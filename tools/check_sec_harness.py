"""Hold uklib's copy of the SEC harness to uslib's, everywhere outside the product specs.

uklib's SEC tests lean on ``lifelib/libraries/uklib/tests/uk_sec_support.py``, which is
uslib's ``lifelib/libraries/uslib/tests/sec_support.py`` under a name of uklib's own.  It is
a copy, and not one module both import, for the reason UKLIB-SEC-PLAN.md U3 gives:

    *Why a copy:* the name must be the library's own. ``conftest.py`` taught this already
    (MERGE.md §9): with both suites in one process, two modules named ``sec_support``
    collide in ``sys.modules``, and the second library's tests would import the first's
    harness and its registry. A module both libraries imported would also have to ship in
    both, which is a copy again.

A copy drifts, and nothing else would notice.  U3 again:

    *Why the check:* uslib's harness has changed in at least 14 commits since its M13,
    most of them a product's step adding a check every later product meets. A fix to one
    copy that never reaches the other would be found by nothing, since each library's
    suite passes on its own copy.

So, as U3 has it, this check "parses the two files, undoes the three substitutions, and
fails on any function, class or constant the two share whose source differs, listing it",
and it fails too on one that only one file holds.  U3 runs it as a step of CI's ``test``
job.  What it cannot settle on its own is the risk the plan names K10:

    **K10 — Two harnesses drift.** U3's check fails CI on any shared function that
    differs. What it cannot stop is a fix one library needs and the other does not; such a
    divergence is listed in the tool with its reason, and reviewed like code.

That list is :data:`DIVERGENCES`, below.

**What is compared.**  Each file holds its own library's product specs, the ``SecSpec`` of
each SEC model and the opening-state extractors it names, between two marker comments: a
line beginning ``# >>> product specs`` and a line beginning ``# <<< product specs``.  That
region is set aside.  A file is refused unless it holds each marker once, in that order,
each a comment at the start of a line and between two top-level statements, not inside
one.  Every other top-level statement is compared: functions, classes, assignments,
imports, and module-level strings.  uklib's text is read with its three spellings,
``uk_registry``, ``UKLIB_`` and ``_uk_sec``, turned back into uslib's, ``us_registry``,
``USLIB_`` and ``_us_sec``.  Both files are parsed with ``ast`` and each statement compared
as ``ast.unparse`` writes it, so layout and comments do not count; and neither does prose,
which is each library's own: docstrings, the module's, a function's or a class's, are
taken out, and so is a constant's documentation, a string standing alone after an
assignment, at module level or in a class body.  Any other module-level string is
compared, as the string after the statement it follows.

A statement is known by the name it binds: a function or a class by its name, an
assignment by its target, ``import x`` and ``from x import`` by the module.  The check
reports each name that only one file has, and each name whose code differs, with a short
unified diff of the two normalized sources.  And because uklib's spellings are read as
uslib's, a uklib statement still spelt as uslib's would compare equal: ``from us_registry
import ...``, the import of uslib's registry U3 exists to prevent.  So the code of uklib's
copy, its prose aside, may hold none of uslib's three spellings, and each that does is
reported too.  The statements' order is not compared.

**A deliberate divergence** is entered in :data:`DIVERGENCES` as ``{name: reason}``, and is
then reported as allowed, with its reason.  An entry whose name no longer differs is
itself an error, so that the dict stays the record of what differs and why.

Usage::

    python tools/check_sec_harness.py
    python tools/check_sec_harness.py <uslib sec_support.py> <uklib uk_sec_support.py>

With no argument it reads the repository's two files, and given two paths it reads those,
as a test of the check reads edited copies.  It exits 0 when the two agree, 1 when they
differ, and 2 when they cannot be compared: a malformed command line, or a file that is
missing, does not parse, or lacks its markers.  It needs the standard library alone.
"""
import argparse
import ast
import copy
import dataclasses
import difflib
import io
import pathlib
import sys
import tokenize

REPO = pathlib.Path(__file__).resolve().parents[1]
USLIB = REPO / "lifelib" / "libraries" / "uslib" / "tests" / "sec_support.py"
UKLIB = REPO / "lifelib" / "libraries" / "uklib" / "tests" / "uk_sec_support.py"

BEGIN = "# >>> product specs"
END = "# <<< product specs"

# The spellings U3 changed in uklib's copy, (uslib's, uklib's): the registry module, the
# environment variables' prefix, and the SEC test modules' suffix in the shard regex.
SUBSTITUTIONS = (("us_registry", "uk_registry"), ("USLIB_", "UKLIB_"),
                 ("_us_sec", "_uk_sec"))

# The deliberate differences, name to reason: a top-level name, as the report gives it,
# whose code one library needs otherwise than the other (K10).  Each entry is reviewed like
# code, and one whose name no longer differs is an error.
DIVERGENCES = {}

DIFF_LINES = 40         # the most lines of diff shown for one name

DEFINITIONS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
ASSIGNMENTS = (ast.Assign, ast.AnnAssign, ast.AugAssign)


class Refused(Exception):
    """A file the check cannot compare: unreadable, unparsable, or without its markers."""


@dataclasses.dataclass(frozen=True)
class Statement:
    """One top-level statement: what it is, its first line, and its normalized source."""
    kind: str
    line: int
    source: str


def shown(path):
    """``path`` relative to the repository where it lies inside it, as a report gives it."""
    path = pathlib.Path(path).resolve()
    try:
        return path.relative_to(REPO).as_posix()
    except ValueError:
        return str(path)


def read(path):
    """The text of ``path``, or :class:`Refused`."""
    try:
        return pathlib.Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as err:
        raise Refused(f"{shown(path)}: cannot be read: {err}") from None


def as_uslib(text):
    """uklib's ``text`` with its three spellings turned back into uslib's."""
    for us, uk in SUBSTITUTIONS:
        text = text.replace(uk, us)
    return text


def marker_lines(text, path):
    """The lines of the two markers, ``(begin, end)``, each the one comment of its kind.

    Read with ``tokenize``, so a marker is a comment at the start of a line, and text that
    only looks like one, inside a string, is not one.
    """
    found = {BEGIN: [], END: []}
    try:
        for token in tokenize.generate_tokens(io.StringIO(text).readline):
            if token.type == tokenize.COMMENT and token.start[1] == 0:
                for marker, lines in found.items():
                    if token.string.startswith(marker):
                        lines.append(token.start[0])
    except (tokenize.TokenError, SyntaxError) as err:
        raise Refused(f"{shown(path)}: does not tokenize: {err}") from None
    for marker, lines in found.items():
        if not lines:
            raise Refused(f"{shown(path)}: no line begins {marker!r}; the product specs "
                          f"lie between {BEGIN!r} and {END!r}, and a file without both "
                          f"markers is not compared")
        if len(lines) > 1:
            raise Refused(f"{shown(path)}: {len(lines)} lines begin {marker!r}, at lines "
                          f"{', '.join(map(str, lines))}; a file holds one")
    (begin,), (end,) = found[BEGIN], found[END]
    if end < begin:
        raise Refused(f"{shown(path)}: {END!r} at line {end} comes before {BEGIN!r} at "
                      f"line {begin}")
    return begin, end


def _is_string(node):
    """Whether ``node`` is a string standing alone as a statement."""
    return (isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str))


def _without_prose(body, documented):
    """``body`` without its docstring, and where ``documented`` without the string that
    documents each assignment, standing alone after it."""
    return [node for i, node in enumerate(body)
            if not (_is_string(node) and (
                i == 0 or (documented and isinstance(body[i - 1], ASSIGNMENTS))))]


def normalized(node):
    """``node``'s source as ``ast.unparse`` writes it, without its prose.

    The docstring of every function and class within it is taken out, and in a class body
    the documentation string after an attribute; a body left empty holds ``pass``.
    """
    node = copy.deepcopy(node)
    for inner in list(ast.walk(node)):
        if isinstance(inner, DEFINITIONS):
            inner.body = (_without_prose(inner.body, isinstance(inner, ast.ClassDef))
                          or [ast.Pass()])
    return ast.unparse(node)


def _kind(node):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return "function"
    if isinstance(node, ast.ClassDef):
        return "class"
    if isinstance(node, ASSIGNMENTS):
        return "assignment"
    if isinstance(node, (ast.Import, ast.ImportFrom)):
        return "import"
    if _is_string(node):
        return "string"
    return f"{type(node).__name__} statement"


def _name(node, previous):
    """The name a statement is known by: what it binds, or, for a statement that binds
    nothing, its kind and the name of the statement before it."""
    if isinstance(node, DEFINITIONS):
        return node.name
    if isinstance(node, ast.Assign):
        return " = ".join(ast.unparse(target) for target in node.targets)
    if isinstance(node, (ast.AnnAssign, ast.AugAssign)):
        return ast.unparse(node.target)
    if isinstance(node, ast.Import):
        return "import " + ", ".join(alias.name for alias in node.names)
    if isinstance(node, ast.ImportFrom):
        return f"from {'.' * node.level}{node.module or ''} import"
    return f"the {_kind(node)} after {previous or 'the module docstring'}"


def statements(text, path):
    """``(compared, aside)``: the top-level statements outside the product specs,
    ``{name: Statement}`` in file order, and how many lie inside them.

    The module's docstring is prose, and so is a string standing alone after an
    assignment, its documentation; neither is a statement here.  A name bound twice is
    known the second time as ``name (2)``.
    """
    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError as err:
        raise Refused(f"{shown(path)}: does not parse: {err}") from None
    begin, end = marker_lines(text, path)
    compared, aside, previous = {}, 0, None
    for index, node in enumerate(tree.body):
        first = min([node.lineno] + [d.lineno for d in getattr(node, "decorator_list", [])])
        last = node.end_lineno
        if begin < first and last < end:
            aside += 1
            continue
        for marker, line in ((BEGIN, begin), (END, end)):
            if first <= line <= last:
                raise Refused(f"{shown(path)}: {marker!r} at line {line} lies inside the "
                              f"statement of lines {first} to {last}")
        if _is_string(node) and (index == 0 or isinstance(tree.body[index - 1],
                                                          ASSIGNMENTS)):
            continue
        name = _name(node, previous)
        key, count = name, 1
        while key in compared:
            count += 1
            key = f"{name} ({count})"
        compared[key] = Statement(_kind(node), first, normalized(node))
        previous = key
    return compared, aside


def _diff(name, us, uk):
    """A short unified diff of two normalized sources, indented under its report line."""
    lines = list(difflib.unified_diff(us.splitlines(), uk.splitlines(), f"uslib {name}",
                                      f"uklib {name}", n=2, lineterm=""))
    if len(lines) > DIFF_LINES:
        lines = lines[:DIFF_LINES] + [f"(and {len(lines) - DIFF_LINES} more lines)"]
    return [f"    {line}" for line in lines]


def _label(name, statement):
    """How a report names a statement: ``function sweep``, ``assignment C_CALLS``, and an
    import, or a statement that binds nothing, by its name alone."""
    if statement.kind in ("function", "class", "assignment"):
        return f"{statement.kind} {name}"
    return name


def compare(us_path, uk_path, divergences=None):
    """The check: ``(findings, allowed, counts)``.

    ``findings`` holds one entry per finding, each a list of report lines, a diff's
    beneath its first, and is empty when the two files agree outside their product
    specs; ``allowed`` lists each divergence of ``divergences``, by default
    :data:`DIVERGENCES`, with its reason; ``counts`` are the statements compared, and
    those set aside in each file.  Raises :class:`Refused` for a file it cannot compare.
    """
    divergences = DIVERGENCES if divergences is None else divergences
    us, us_aside = statements(read(us_path), us_path)
    uk_text = read(uk_path)
    spelt, uk_aside = statements(uk_text, uk_path)
    uk, _ = statements(as_uslib(uk_text), uk_path)

    differing = {}
    for name, statement in us.items():
        if name not in uk:
            differing[name] = [f"only in uslib: {_label(name, statement)} (line "
                               f"{statement.line})"]
        elif statement.source != uk[name].source:
            differing[name] = ([f"differs: {_label(name, statement)} (uslib line "
                                f"{statement.line}, uklib line {uk[name].line})"]
                               + _diff(name, statement.source, uk[name].source))
    for name, statement in uk.items():
        if name not in us:
            differing[name] = [f"only in uklib: {_label(name, statement)} (line "
                               f"{statement.line})"]

    findings, allowed = [], []
    for name, statement in spelt.items():
        for us_spelling, uk_spelling in SUBSTITUTIONS:
            if us_spelling in statement.source:
                findings.append([f"uklib spells uslib's {us_spelling!r} for its own "
                                 f"{uk_spelling!r}: {_label(name, statement)} (line "
                                 f"{statement.line})"])
    for name, lines in differing.items():
        if name in divergences:
            allowed.append(f"allowed: {name}: {divergences[name]}")
        else:
            findings.append(lines)
    for name, reason in divergences.items():
        if name not in differing:
            findings.append([f"DIVERGENCES[{name!r}] is stale: {name} no longer differs; "
                             f"take its entry out"])
        elif not str(reason).strip():
            findings.append([f"DIVERGENCES[{name!r}] gives no reason"])
    counts = {"compared": len(set(us) & set(uk)), "uslib aside": us_aside,
              "uklib aside": uk_aside}
    return findings, allowed, counts


def main(argv):
    parser = argparse.ArgumentParser(
        prog="python tools/check_sec_harness.py",
        description="Hold uklib's SEC harness to uslib's outside the product specs "
                    "(UKLIB-SEC-PLAN.md U3, K10).")
    parser.add_argument("uslib", nargs="?", type=pathlib.Path,
                        help=f"uslib's harness, by default {shown(USLIB)}")
    parser.add_argument("uklib", nargs="?", type=pathlib.Path,
                        help=f"uklib's harness, by default {shown(UKLIB)}")
    args = parser.parse_args(argv)
    if (args.uslib is None) != (args.uklib is None):
        parser.error("give both files, uslib's and uklib's, or neither")
    us_path, uk_path = args.uslib or USLIB, args.uklib or UKLIB
    try:
        findings, allowed, counts = compare(us_path, uk_path)
    except Refused as err:
        print(f"check_sec_harness: refused: {err}")
        return 2
    for line in allowed:
        print(line)
    if findings:
        print(f"{shown(us_path)} and {shown(uk_path)}, uklib's spellings read as "
              f"uslib's, outside their product specs:")
        for lines in findings:
            print("\n".join(lines))
        count = f"{len(findings)} finding{'' if len(findings) == 1 else 's'}"
        print(f"check_sec_harness: {count}.  Bring the two copies together, or enter a "
              f"deliberate divergence in DIVERGENCES with its reason.")
        return 1
    print(f"check_sec_harness: {shown(us_path)} and {shown(uk_path)} agree outside their "
          f"product specs: {counts['compared']} statements compared, "
          f"{counts['uslib aside']} and {counts['uklib aside']} set aside as each "
          f"library's own")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
