"""Tests of ``tools/check_sec_harness.py``, which holds uklib's SEC harness to uslib's.

``uk_sec_support.py`` is uslib's ``sec_support.py`` under uklib's own name, and the check
is what keeps the copy a copy (UKLIB-SEC-PLAN.md U3, K10): it compares the two files
statement by statement outside their product specs, uklib's three spellings read as
uslib's, and holds each file's product specs, which it does not compare, to what they may
hold.  A check that passed everything would leave both suites green on drifted copies, so
each kind of finding is shown here on a small pair of synthetic files written to
``tmp_path``, shaped as the real two are, shared code around a block of product specs:

* the pair as written agrees, and a change to code in either copy fails, as does a
  function that only one copy holds;
* a file whose markers are missing, doubled or out of order is refused, exit 2;
* prose is each library's own: a changed docstring, a constant's documentation or a
  comment passes, and so does a uslib spelling in uklib's prose, and a change to the code
  of one copy's product specs;
* uslib's spellings in uklib's code fail, outside the product specs and inside them;
* each rule of the product specs, in either file: a statement there that is not a
  definition, an assignment to plain names or an assignment's documentation fails, with
  its line; so does a name bound there, by any means, that either file binds outside
  them, and a ``global`` declaration there of such a name; and what the rules allow
  passes, a comprehension's loop variable and a function's local among it, which bind no
  name of the module;
* ``DIVERGENCES``: an entry whose name no longer differs fails, and so does one with no
  reason, and one with its reason is reported as allowed.

One more test runs the check on the repository's two files, as CI's ``test`` job does.
The tool is the source repository's, outside the library, so it is loaded by its path,
under a module name of its own, and every test skips, with the reason, where it is absent,
as from a ``lifelib.create()`` copy.
"""
import importlib.util

import pytest

from uk_registry import LIB

TOOL = LIB.parents[2] / "tools" / "check_sec_harness.py"

BEGIN = "# >>> product specs: this library's own.\n"
END = "# <<< product specs\n"

# The synthetic harness in uslib's spelling: shared code, the product specs, and shared
# code again, each kind of statement the check compares among it.
TOP = '''\
"""The synthetic harness: the module's docstring, which is prose."""
import re

from us_registry import MODELS, model_path

TWIN_EXEMPT_DEFAULT = frozenset({"model_point"})
"""The cells T1 leaves out: a constant's documentation, which is prose."""


def twin_mismatches(s_proj, sec_proj, limit=20):
    """T1's comparison: a function's docstring, which is prose."""
    # A comment, which is prose.
    return [s_proj, sec_proj, limit, MODELS]


class SecSpec:
    """A product's spec."""
    twin: str = ""
    """The S model: an attribute's documentation, which is prose."""


'''

US_SPECS = BEGIN + '''
def _wl_state(row):
    """WholeLife's opening state."""
    return row["av_pp"]


SEC_SPECS = {"WholeLife_US_SEC": SecSpec()}
"""uslib's specs."""

''' + END

UK_SPECS = BEGIN + '''
def _term_state(row):
    """Term's opening state."""
    return row["sum_assured"]


SEC_SPECS: dict = {"Term_UK_SEC": SecSpec()}

''' + END

BOTTOM = '''

CYTHON_SHARD = "USLIB_CYTHON_SHARD"


def cython_shard(name):
    """The shard of a test module."""
    found = re.fullmatch(r"test_(\\w+)_us_sec\\.py", name)
    return found and found.group(1)
'''


def as_uklib(text):
    """uslib's ``text`` with uklib's three spellings, as U3 substituted them."""
    for us, uk in (("us_registry", "uk_registry"), ("USLIB_", "UKLIB_"),
                   ("_us_sec", "_uk_sec")):
        text = text.replace(us, uk)
    return text


FILES = {"uslib": TOP + US_SPECS + BOTTOM,
         "uklib": as_uklib(TOP) + UK_SPECS + as_uklib(BOTTOM)}


@pytest.fixture(scope="module")
def check():
    """The tool as a module, loaded by its path under a name of its own."""
    if not TOOL.is_file():
        pytest.skip("tools/check_sec_harness.py is the source repository's, and it is "
                    "absent, as from a lifelib.create() copy")
    spec = importlib.util.spec_from_file_location("check_sec_harness_uk", TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _pair(tmp_path, lib=None, old=None, new=None):
    """The synthetic pair written to ``tmp_path``, ``(uslib's, uklib's)``, with ``old``
    replaced by ``new`` in ``lib``'s file where one is given."""
    texts = dict(FILES)
    if lib is not None:
        assert texts[lib].count(old) == 1, old
        texts[lib] = texts[lib].replace(old, new)
    paths = tmp_path / "sec_support.py", tmp_path / "uk_sec_support.py"
    for path, lib in zip(paths, ("uslib", "uklib")):
        path.write_text(texts[lib], encoding="utf-8")
    return paths


def _run(check, capsys, paths):
    """The check's command line on ``paths``: ``(exit code, its report)``."""
    code = check.main([str(path) for path in paths])
    return code, capsys.readouterr().out


def _line(text, start, after=None):
    """The number of the line of ``text`` that is ``start``, the first after the line
    ``after`` where one is given."""
    lines = text.splitlines()
    return lines.index(start, 0 if after is None else lines.index(after)) + 1


def test_the_synthetic_pair_agrees(check, capsys, tmp_path):
    """The pair every test below edits passes as written: seven statements compared, and
    set aside as product specs three of uslib's, a documentation string among them, and
    two of uklib's."""
    code, out = _run(check, capsys, _pair(tmp_path))
    assert code == 0, out
    assert "agree outside their product specs: 7 statements compared, and 3 and 2 set " \
           "aside" in out, out


@pytest.mark.parametrize("lib", ["uslib", "uklib"])
def test_a_changed_code_line_in_either_copy_fails(check, capsys, tmp_path, lib):
    """The finding names the function and shows the line, from uslib's side of the diff
    to uklib's: removed where uklib's copy changed it, added where uslib's did."""
    code, out = _run(check, capsys, _pair(
        tmp_path, lib, "return [s_proj, sec_proj, limit, MODELS]",
        "return [s_proj, sec_proj, MODELS]"))
    assert code == 1, out
    assert "differs: function twin_mismatches" in out, out
    side = "-" if lib == "uklib" else "+"
    assert f"{side}    return [s_proj, sec_proj, limit, MODELS]" in out, out


@pytest.mark.parametrize("lib", ["uslib", "uklib"])
def test_a_function_in_one_copy_alone_fails(check, capsys, tmp_path, lib):
    code, out = _run(check, capsys, _pair(
        tmp_path, lib, "    return found and found.group(1)\n",
        "    return found and found.group(1)\n\n\ndef helper():\n    return 1\n"))
    assert code == 1, out
    assert f"only in {lib}: function helper" in out, out


# Each marker fault: what replaces what, and what the refusal says.
MARKER_FAULTS = {
    "begin missing": (BEGIN, "", "no line begins '# >>> product specs'"),
    "end missing": (END, "", "no line begins '# <<< product specs'"),
    "begin doubled": (BEGIN, BEGIN + "\n" + BEGIN, "2 lines begin '# >>> product specs'"),
    "end doubled": (END, END + "\n" + END, "2 lines begin '# <<< product specs'"),
    "out of order": (BEGIN, END, None),
}


@pytest.mark.parametrize("lib", ["uslib", "uklib"])
@pytest.mark.parametrize("fault", sorted(MARKER_FAULTS))
def test_a_missing_doubled_or_misordered_marker_is_refused(check, capsys, tmp_path, lib,
                                                           fault):
    """A file without each marker once, in order, is not compared: exit 2.  Out of
    order is the end marker before the begin marker, the begin moved past the end."""
    old, new, said = MARKER_FAULTS[fault]
    if fault == "out of order":
        text = FILES[lib].replace(BEGIN, "").replace(END, END + "\n" + BEGIN)
        old, new = FILES[lib], text
        said = "'# <<< product specs' at line"
    code, out = _run(check, capsys, _pair(tmp_path, lib, old, new))
    assert code == 2, out
    assert out.startswith("check_sec_harness: refused: ") and said in out, out


# Prose, and the product specs' code, are each library's own: an edit to uklib's copy, as
# (what, its replacement).
OWN = {
    "module docstring": (
        '"""The synthetic harness: the module\'s docstring, which is prose."""',
        '"""uklib\'s own words for it, which name us_registry and USLIB_ freely."""'),
    "function docstring": (
        '"""T1\'s comparison: a function\'s docstring, which is prose."""',
        '"""Said otherwise, as us_registry says it."""'),
    "constant documentation": (
        '"""The cells T1 leaves out: a constant\'s documentation, which is prose."""',
        '"""Said otherwise."""'),
    "attribute documentation": (
        '"""The S model: an attribute\'s documentation, which is prose."""',
        '"""Said otherwise."""'),
    "comment": ("# A comment, which is prose.", "# Another, naming test_x_us_sec.py."),
    "product specs' docstring": ('"""Term\'s opening state."""',
                                 '"""As uslib\'s USLIB_ extractors have it."""'),
    "product specs' comment": (END, "# A comment naming us_registry.\n" + END),
    "product specs' code": ('return row["sum_assured"]', 'return row["sum_assured_init"]'),
}


@pytest.mark.parametrize("edit", sorted(OWN))
def test_a_changed_docstring_comment_or_product_spec_passes(check, capsys, tmp_path,
                                                             edit):
    """Prose is not compared, and holds uslib's spellings freely; a product spec's code is
    the library's own."""
    code, out = _run(check, capsys, _pair(tmp_path, "uklib", *OWN[edit]))
    assert code == 0, out


# A uslib spelling in uklib's code: what replaces what, and the statement the finding
# names, by its first line and how the report gives it, ``{line}`` its number.
SPELLINGS = {
    "import outside": ("from uk_registry import MODELS, model_path",
                       "from us_registry import MODELS, model_path",
                       "from us_registry import MODELS, model_path",
                       "from us_registry import (line {line})"),
    "constant outside": ('CYTHON_SHARD = "UKLIB_CYTHON_SHARD"',
                         'CYTHON_SHARD = "USLIB_CYTHON_SHARD"',
                         'CYTHON_SHARD = "USLIB_CYTHON_SHARD"',
                         "assignment CYTHON_SHARD (line {line})"),
    "regex outside": ('"test_(\\w+)_uk_sec\\.py"', '"test_(\\w+)_us_sec\\.py"',
                      "def cython_shard(name):", "function cython_shard (line {line})"),
    "function in the specs": ('return row["sum_assured"]',
                              'return row["sum_assured"] or "test_term_us_sec.py"',
                              "def _term_state(row):",
                              "uklib's product specs, line {line}:"),
    "assignment in the specs": ('{"Term_UK_SEC": SecSpec()}',
                                '{"Term_UK_SEC": SecSpec(), "USLIB_SHARD": None}',
                                'SEC_SPECS: dict = {"Term_UK_SEC": SecSpec(), '
                                '"USLIB_SHARD": None}',
                                "uklib's product specs, line {line}:"),
}


@pytest.mark.parametrize("case", sorted(SPELLINGS))
def test_a_uslib_spelling_in_uklib_s_code_fails(check, capsys, tmp_path, case):
    """Read as uslib's, uklib's ``from us_registry import`` compares equal to uslib's own
    import, so the check refuses a uslib spelling in uklib's code by itself: outside the
    product specs, and inside them, which are not compared at all."""
    old, new, start, where = SPELLINGS[case]
    paths = _pair(tmp_path, "uklib", old, new)
    where = where.format(line=_line(paths[1].read_text(encoding="utf-8"), start))
    code, out = _run(check, capsys, paths)
    assert code == 1, out
    found = [line for line in out.splitlines() if "uklib spells uslib's" in line]
    assert len(found) == 1 and where in found[0], out


# Statements the product specs may not hold, each added at their end: the statement, the
# text of the line the finding names, and what the finding says.
REFUSED = {
    "import": ("import json", "import json", "an import"),
    "import from": ("from os import path", "from os import path", "an import"),
    "expression": ('print("specs")', 'print("specs")', "an expression statement"),
    "stray string": ('def _f():\n    return 0\n\n\n"""Documents no assignment."""',
                     '"""Documents no assignment."""',
                     "a string documenting no assignment"),
    "if": ("if SEC_SPECS:\n    _X = 1", "if SEC_SPECS:", "a control-flow statement"),
    "for": ("for _key in SEC_SPECS:\n    pass", "for _key in SEC_SPECS:",
            "a control-flow statement"),
    "try": ("try:\n    _X = 1\nexcept ImportError:\n    _X = 0", "try:",
            "a control-flow statement"),
    "with": ("with open(__file__) as _handle:\n    pass", "with open(__file__) as _handle:",
             "a control-flow statement"),
    "augmented": ("_COUNT = 0\n_COUNT += 1", "_COUNT += 1", "an augmented assignment"),
    "attribute": ('SecSpec.twin = "x"', 'SecSpec.twin = "x"',
                  "an assignment to an attribute"),
    "subscript": ('MODELS["Toy"] = ("toy", {})', 'MODELS["Toy"] = ("toy", {})',
                  "an assignment to a subscript"),
    "tuple": ("_A, _B = 1, 2", "_A, _B = 1, 2", "an assignment to a tuple"),
    "del": ("del SEC_SPECS", "del SEC_SPECS", "a statement of kind Delete"),
    "rebinds by assignment": (
        'TWIN_EXEMPT_DEFAULT = TWIN_EXEMPT_DEFAULT | {"result_cf"}',
        'TWIN_EXEMPT_DEFAULT = TWIN_EXEMPT_DEFAULT | {"result_cf"}',
        "'TWIN_EXEMPT_DEFAULT' is bound here, and bound outside the product specs"),
    "rebinds by definition": (
        "def twin_mismatches(s_proj, sec_proj, **kw):\n    return []",
        "def twin_mismatches(s_proj, sec_proj, **kw):",
        "'twin_mismatches' is bound here, and bound outside the product specs"),
    "rebinds by a decorated definition": (
        "@staticmethod\ndef twin_mismatches(s_proj, sec_proj):\n    return []",
        "@staticmethod", "'twin_mismatches' is bound here"),
    "rebinds by class": ("class SecSpec:\n    pass", "class SecSpec:",
                         "'SecSpec' is bound here"),
    "rebinds by annotation": ("MODELS: dict = {}", "MODELS: dict = {}",
                              "'MODELS' is bound here"),
    "rebinds by chained assignment": ("_X = model_path = None", "_X = model_path = None",
                                      "'model_path' is bound here"),
    "rebinds an import": ("from os import path as model_path",
                          "from os import path as model_path",
                          "'model_path' is bound here"),
    "rebinds by walrus": ("_X = (twin_mismatches := None)",
                          "_X = (twin_mismatches := None)",
                          "'twin_mismatches' is bound here"),
    "rebinds by walrus in a default": ("def _f(x=(MODELS := {})):\n    return x",
                                       "def _f(x=(MODELS := {})):",
                                       "'MODELS' is bound here"),
    "rebinds by walrus in a comprehension": (
        '_KEYS = [(model_path := key) for key in "ab"]',
        '_KEYS = [(model_path := key) for key in "ab"]', "'model_path' is bound here"),
    "declares global in a function": (
        "def _hook():\n    global TWIN_EXEMPT_DEFAULT\n"
        "    TWIN_EXEMPT_DEFAULT = frozenset()",
        "def _hook():", "'TWIN_EXEMPT_DEFAULT' is declared global here"),
    "declares global in a method": (
        "class _Cache:\n    def reset(self):\n        global MODELS\n        MODELS = {}",
        "class _Cache:", "'MODELS' is declared global here"),
    "declares global in a nested function": (
        "def _outer():\n    def _inner():\n        global twin_mismatches\n"
        "        twin_mismatches = None\n    return _inner",
        "def _outer():", "'twin_mismatches' is declared global here"),
}


def _with_specs(tmp_path, lib, statement):
    """The pair with ``statement`` added at the end of ``lib``'s product specs."""
    return _pair(tmp_path, lib, "\n" + END, "\n" + statement + "\n\n" + END)


@pytest.mark.parametrize("lib", ["uslib", "uklib"])
@pytest.mark.parametrize("case", sorted(REFUSED))
def test_the_product_specs_hold_no_other_statement_and_no_shared_name(
        check, capsys, tmp_path, lib, case):
    """Each statement the product specs may not hold fails the check, in either file,
    with its line: a statement that is not a definition, an assignment to plain names, or
    the string that documents an assignment; a name the product specs bind, in whatever
    way, that the harness binds outside them; and a ``global`` declaration of one."""
    statement, line, said = REFUSED[case]
    paths = _with_specs(tmp_path, lib, statement)
    number = _line(paths[lib == "uklib"].read_text(encoding="utf-8"), line,
                   after=BEGIN.rstrip("\n"))
    code, out = _run(check, capsys, paths)
    assert code == 1, out
    found = [text for text in out.splitlines()
             if text.startswith(f"{lib}'s product specs, line {number}: ") and said in text]
    assert found, out


@pytest.mark.parametrize("lib, other", [("uslib", "uklib"), ("uklib", "uslib")])
def test_a_name_bound_outside_the_specs_in_the_other_file_alone_is_refused(
        check, capsys, tmp_path, lib, other):
    """The names held are those either file binds outside its product specs: a helper of
    one file's shared code alone, defined among the other's product specs, fails there
    too, besides being only in the one."""
    paths = dict(zip(("uslib", "uklib"), _pair(
        tmp_path, other, "    return found and found.group(1)\n",
        "    return found and found.group(1)\n\n\ndef helper():\n    return 1\n")))
    text = paths[lib].read_text(encoding="utf-8").replace(
        "\n" + END, "\ndef helper():\n    return 2\n\n" + END)
    paths[lib].write_text(text, encoding="utf-8")
    shared = _line(paths[other].read_text(encoding="utf-8"), "def helper():")
    code, out = _run(check, capsys, paths.values())
    assert code == 1, out
    assert (f"{lib}'s product specs, line {_line(text, 'def helper():')}: 'helper' is "
            f"bound here, and bound outside the product specs ({other} line {shared})"
            ) in out, out


# What the product specs may hold: definitions, decorated or not, assignments to plain
# names of their own, chained or annotated, and the string documenting one; a global
# declaration of a name of their own; and names that bind nothing in the module, a
# comprehension's loop variable, a lambda's assignment expression, a function's local,
# named as the harness's names are.
ALLOWED = '''\
def _keep(function):
    return function


@_keep
def _decorated(row):
    """A decorated extractor."""
    return row


class _Extractor:
    """An extractor as a class."""
    column = "sum_assured"
    """Its column."""

    def __call__(self, row):
        return row[self.column]


_A = _B = 1
_C: int = 2
"""Two names, documented."""

_CACHE = {}


def _reset():
    global _CACHE
    _CACHE = {}


_NAMES = [model_path for model_path in ("a", "b")]
_PICK = lambda row: (MODELS := row)                         # noqa: E731


def _local():
    TWIN_EXEMPT_DEFAULT = frozenset()
    return TWIN_EXEMPT_DEFAULT
'''


@pytest.mark.parametrize("lib", ["uslib", "uklib"])
def test_the_product_specs_may_hold_definitions_and_names_of_their_own(
        check, capsys, tmp_path, lib):
    code, out = _run(check, capsys, _with_specs(tmp_path, lib, ALLOWED))
    assert code == 0, out


def test_a_stale_divergence_fails(check, capsys, tmp_path, monkeypatch):
    """An entry for a name that no longer differs is itself a finding, so that
    ``DIVERGENCES`` stays the record of what differs and why."""
    monkeypatch.setattr(check, "DIVERGENCES", {"twin_mismatches": "uklib's T1 needs it"})
    code, out = _run(check, capsys, _pair(tmp_path))
    assert code == 1, out
    assert ("DIVERGENCES['twin_mismatches'] is stale: twin_mismatches no longer differs; "
            "take its entry out") in out, out


def _differing(tmp_path):
    return _pair(tmp_path, "uklib", "return [s_proj, sec_proj, limit, MODELS]",
                 "return [s_proj, sec_proj, MODELS]")


@pytest.mark.parametrize("reason", ["", "   "])
def test_a_divergence_without_a_reason_fails(check, capsys, tmp_path, monkeypatch, reason):
    monkeypatch.setattr(check, "DIVERGENCES", {"twin_mismatches": reason})
    code, out = _run(check, capsys, _differing(tmp_path))
    assert code == 1, out
    assert "DIVERGENCES['twin_mismatches'] gives no reason" in out, out


def test_a_divergence_with_its_reason_is_reported_as_allowed(check, capsys, tmp_path,
                                                             monkeypatch):
    monkeypatch.setattr(check, "DIVERGENCES",
                        {"twin_mismatches": "uklib's T1 drops the limit"})
    code, out = _run(check, capsys, _differing(tmp_path))
    assert code == 0, out
    assert "allowed: twin_mismatches: uklib's T1 drops the limit" in out, out


def test_the_repository_s_two_harnesses_agree_and_keep_to_the_rules(check, capsys):
    """The check CI's ``test`` job runs, on the repository's two files: they agree
    outside their product specs, and the product specs of each keep to their rules."""
    for path in (check.USLIB, check.UKLIB):
        if not path.is_file():
            pytest.skip(f"{path.name} is absent: the check reads both libraries' harnesses")
    code, out = _run(check, capsys, [])
    assert code == 0, out
    assert "agree outside their product specs" in out, out
