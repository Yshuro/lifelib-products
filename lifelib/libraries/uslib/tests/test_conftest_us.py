"""Tests of uslib's ``conftest.py`` hooks, run on probes in a pytest of their own.

``pytest_collection_modifyitems``, under ``USLIB_CYTHON_SHARD``, deselects uslib's compile
tests outside the shard, refuses a name that is no shard, and under
``USLIB_REQUIRE_CYTHON=1`` refuses a shard that keeps none of them.
``pytest_runtest_makereport`` reports a ``cython`` test that skips as failed under
``USLIB_REQUIRE_CYTHON=1``, and a ``docutils`` test under ``USLIB_REQUIRE_DOCUTILS=1``.  The
``cython`` and ``sec`` jobs rely on both, since without them a leg that compiled nothing,
or parsed no docstring, is green.  And CI's ``test`` job collects every library in one
process, where every collection hook is handed every library's items: so the hook must
deselect and count uslib's compile tests alone, by the directory they lie in, and both
hooks must read uslib's variables, not uklib's.  No suite run shows a hook failing at
that: with the directory filter removed, or ``REQUIRED`` pointed at the ``UKLIB_*``
variables, every test uslib had passed, as the same two faults passed uklib's until
``test_conftest_uk.py`` ran its hooks on probes.

So uslib's hooks run here on probes, as uklib's run there.  ``conftest.py`` is copied into
``us/``, a folder of ``tmp_path``, beside two probe modules.  ``test_probe_us.py`` holds a
compile test and a docstring test that skip, and a plain test; tied to no model, its
compile test is the ``toolchain`` shard's.  ``test_<shard>_us_sec.py``, named as the
product module of :data:`SHARD`, the first model's shard, holds a compile test of that
shard that passes.  A second folder, ``elsewhere/``, outside the copy's, stands for another
library: a compile test that passes and one that skips, which ``sec_support.cython_shard``
would give the ``toolchain`` shard.  Each run is ``python -m pytest`` over both folders in
a subprocess, with uslib's ``tests/`` on ``PYTHONPATH`` for ``us_registry`` and
``sec_support``, and of uslib's and uklib's variables those of the run alone:

* the ``toolchain`` shard under ``USLIB_REQUIRE_CYTHON=1``, ``-m cython`` and ``-k``
  deselecting ``test_probe_us.py``, keeps no compile test of uslib's, and is a usage
  error, though the other library's compile tests are kept;
* the model's shard under ``USLIB_REQUIRE_CYTHON=1`` keeps the model's compile probe, drops
  the toolchain's, and keeps the other library's compile tests;
* a shard that is no shard is a usage error that lists the shards;
* under ``USLIB_REQUIRE_CYTHON=1`` and ``USLIB_REQUIRE_DOCUTILS=1``, with the ``toolchain``
  shard keeping the toolchain's compile probe, the two probes that skip are failed, saying
  why, and the plain one passes; the other library's skip is still a skip, since pytest
  hands the report hook the tests below its ``conftest.py`` alone;
* under uklib's three variables alone, its shard among them, every probe runs, and every
  skip is a skip.

uklib's hook reads the directory filter from one helper, ``_ours``; uslib's writes it
twice, where the hook deselects and where it counts what the shard kept, so the first two
runs hold one each.  Without the filter in the count, or in both places, the first run
exits 0 on the other library's compile tests.  Without it where the hook deselects alone,
the first run is still refused, the other library's compile tests being the ``toolchain``
shard's, and the second run drops them from the model's shard.  Five runs, about a second
each.
"""
import os
import re
import shutil
import subprocess
import sys

import pytest

from sec_support import cython_shards
from us_registry import LIB

CONFTEST = LIB / "tests" / "conftest.py"

# The shard of the registry's first model at stage "EC", term_life, or None while there is
# none and the toolchain's is the one shard.
SHARD = next((shard for shard, model in cython_shards().items() if model is not None), None)

PROBE_US = '''\
import pytest


@pytest.mark.cython
def test_compile_probe():
    pytest.skip("the probe finds no compiler")


@pytest.mark.docutils
def test_docstring_probe():
    pytest.skip("the probe finds no docutils")


def test_plain_probe():
    pass
'''

PROBE_SHARD = '''\
import pytest


@pytest.mark.cython
def test_compile_probe_of_the_shard():
    pass
'''

PROBE_ELSEWHERE = '''\
import pytest


@pytest.mark.cython
def test_compile_probe_elsewhere():
    pass


@pytest.mark.cython
def test_compile_probe_elsewhere_skips():
    pytest.skip("another library's compile test, which uslib's variables do not govern")
'''


@pytest.fixture(scope="module")
def probes(tmp_path_factory):
    """The runs' folder: uslib's ``conftest.py`` copied into ``us/`` beside its probes, and
    ``elsewhere/``, another library's, under a ``pytest.ini`` that makes it the root."""
    root = tmp_path_factory.mktemp("conftest_probes")
    (root / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")
    probes = [("us", "test_probe_us.py", PROBE_US),
              ("elsewhere", "test_probe_elsewhere.py", PROBE_ELSEWHERE)]
    if SHARD is not None:
        probes.append(("us", f"test_{SHARD}_us_sec.py", PROBE_SHARD))
    for folder, probe, text in probes:
        (root / folder).mkdir(exist_ok=True)
        (root / folder / probe).write_text(text, encoding="utf-8")
    shutil.copyfile(CONFTEST, root / "us" / "conftest.py")
    return root


def _run(root, variables, *args):
    """``python -m pytest -v`` over both folders, in a subprocess, under ``variables`` and
    no other of uslib's and uklib's, nor options from ``PYTEST_ADDOPTS``: ``(exit code,
    output)``."""
    env = {key: value for key, value in os.environ.items()
           if not key.startswith(("USLIB_", "UKLIB_")) and key != "PYTEST_ADDOPTS"}
    env.update(variables)
    env["PYTHONPATH"] = os.pathsep.join(
        [str(LIB / "tests")] + ([env["PYTHONPATH"]] if env.get("PYTHONPATH") else []))
    done = subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "-v", "us", "elsewhere",
         *args], cwd=root, env=env, capture_output=True, text=True, timeout=300)
    return done.returncode, done.stdout + done.stderr


def _outcomes(output):
    """Each probe's outcome in a run's ``-v`` output, by its name."""
    return {found.group(1): found.group(2) for found in re.finditer(
        r"::(test_\w+) (PASSED|FAILED|SKIPPED|ERROR)", output)}


def test_a_shard_counts_uslib_s_compile_tests_alone(probes):
    """The ``toolchain`` shard, under ``USLIB_REQUIRE_CYTHON=1``, with ``-k`` deselecting
    uslib's toolchain probe, keeps no compile test of uslib's, the model's probe being its
    shard's, and is a usage error: the other library's compile tests, which the run keeps,
    are not uslib's.  Counted as uslib's, without the directory filter where the hook
    counts, the run would pass on theirs, exit 0."""
    code, output = _run(probes, {"USLIB_REQUIRE_CYTHON": "1",
                                 "USLIB_CYTHON_SHARD": "toolchain"},
                        "-m", "cython", "-k", "not probe_us")
    assert code == pytest.ExitCode.USAGE_ERROR, output
    assert ("USLIB_REQUIRE_CYTHON=1, and USLIB_CYTHON_SHARD='toolchain' selects no compile "
            "test") in output, output


def test_a_model_s_shard_deselects_uslib_s_compile_tests_alone(probes):
    """A model's shard, under ``USLIB_REQUIRE_CYTHON=1``, keeps uslib's compile test of
    that shard and deselects the toolchain's, and leaves the other library's compile tests
    to run: ``sec_support.cython_shard`` gives them the ``toolchain`` shard, so without the
    directory filter where the hook deselects, they would be dropped from the run as
    uslib's."""
    if SHARD is None:
        pytest.skip("no uslib model is at stage 'EC', and the toolchain's is the one shard")
    code, output = _run(probes, {"USLIB_REQUIRE_CYTHON": "1", "USLIB_CYTHON_SHARD": SHARD})
    assert code == pytest.ExitCode.OK, output
    assert _outcomes(output) == {
        "test_compile_probe_of_the_shard": "PASSED", "test_docstring_probe": "SKIPPED",
        "test_plain_probe": "PASSED", "test_compile_probe_elsewhere": "PASSED",
        "test_compile_probe_elsewhere_skips": "SKIPPED"}, output


def test_a_name_that_is_no_uslib_shard_is_a_usage_error_that_lists_the_shards(probes):
    code, output = _run(probes, {"USLIB_CYTHON_SHARD": "nonesuch"})
    assert code == pytest.ExitCode.USAGE_ERROR, output
    assert (f"USLIB_CYTHON_SHARD='nonesuch' is no shard; the shards are "
            f"{', '.join(cython_shards())}") in output, output


def test_uslib_s_variables_fail_a_skip_of_uslib_s_tests_alone(probes):
    """Under ``USLIB_REQUIRE_CYTHON=1`` and ``USLIB_REQUIRE_DOCUTILS=1``, each uslib probe
    that skips is failed, saying which variable forbids it and why it skipped; the other
    library's compile test that skips is skipped.  The ``toolchain`` shard keeps uslib's
    toolchain probe, so the collection hook lets the run go on, and deselects the model's
    probe, its shard's."""
    code, output = _run(probes, {"USLIB_REQUIRE_CYTHON": "1", "USLIB_REQUIRE_DOCUTILS": "1",
                                 "USLIB_CYTHON_SHARD": "toolchain"})
    assert code == pytest.ExitCode.TESTS_FAILED, output
    assert _outcomes(output) == {
        "test_compile_probe": "FAILED", "test_docstring_probe": "FAILED",
        "test_plain_probe": "PASSED", "test_compile_probe_elsewhere": "PASSED",
        "test_compile_probe_elsewhere_skips": "SKIPPED"}, output
    for variable, reason in (("USLIB_REQUIRE_CYTHON", "the probe finds no compiler"),
                             ("USLIB_REQUIRE_DOCUTILS", "the probe finds no docutils")):
        assert re.search(rf"{variable}=1 forbids a skip, and it skipped: .*{reason}",
                         output), output


def test_uklib_s_variables_govern_no_test_of_uslib_s(probes):
    """Under ``UKLIB_REQUIRE_CYTHON=1``, ``UKLIB_REQUIRE_DOCUTILS=1`` and
    ``UKLIB_CYTHON_SHARD`` alone, uklib's variables, every probe runs, and every probe that
    skips is skipped: uslib's hooks read uslib's."""
    code, output = _run(probes, {"UKLIB_REQUIRE_CYTHON": "1",
                                 "UKLIB_REQUIRE_DOCUTILS": "1",
                                 "UKLIB_CYTHON_SHARD": "toolchain"})
    assert code == pytest.ExitCode.OK, output
    want = {"test_compile_probe": "SKIPPED", "test_docstring_probe": "SKIPPED",
            "test_plain_probe": "PASSED", "test_compile_probe_elsewhere": "PASSED",
            "test_compile_probe_elsewhere_skips": "SKIPPED"}
    if SHARD is not None:
        want["test_compile_probe_of_the_shard"] = "PASSED"
    assert _outcomes(output) == want, output
