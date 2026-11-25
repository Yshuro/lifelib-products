"""Tests of uklib's ``conftest.py`` hooks, run on probes in a pytest of their own.

``conftest.py`` holds uslib's two hooks read for uklib (UKLIB-SEC-PLAN.md U7, §3 item 5).
``pytest_collection_modifyitems``, under ``UKLIB_CYTHON_SHARD``, deselects uklib's compile
tests outside the shard, refuses a name that is no shard, and under
``UKLIB_REQUIRE_CYTHON=1`` refuses a shard that keeps none of them.
``pytest_runtest_makereport`` reports a ``cython`` test that skips as failed under
``UKLIB_REQUIRE_CYTHON=1``, and a ``docutils`` test under ``UKLIB_REQUIRE_DOCUTILS=1``.  The
``cython_uk`` and ``sec_uk`` jobs rely on both, since without them a leg that compiled
nothing, or parsed no docstring, is green.  And CI's ``test`` job collects every library in
one process, where every collection hook is handed every library's items: so the hook
must count uklib's compile tests alone, by the directory they lie in, and both hooks must
read uklib's variables, not uslib's.  No suite run shows a hook failing at that, so each
fault the review found, C1, the directory filter of ``_ours`` removed, and C2, ``REQUIRED``
pointed at the ``USLIB_*`` variables, passed every test there was.

So the hooks run here on probes.  ``conftest.py`` is copied into ``uk/``, a folder of
``tmp_path``, beside a probe module: a compile test and a docstring test that skip, and a
plain test.  A second folder, ``elsewhere/``, outside the copy's, stands for another
library: a compile test that passes and one that skips.  Each run is ``python -m pytest``
over both folders in a subprocess, with uklib's ``tests/`` on ``PYTHONPATH`` for
``uk_registry`` and ``uk_sec_support``, and of uklib's and uslib's variables those of the
run alone:

* the ``toolchain`` shard under ``UKLIB_REQUIRE_CYTHON=1``, ``-m cython`` and ``-k``
  deselecting the uklib probe, is a usage error, though the other library's compile tests
  are kept: counted as uklib's, as without the filter, they would pass the run (C1);
* a shard that is no shard is a usage error that lists the shards;
* under ``UKLIB_REQUIRE_CYTHON=1`` and ``UKLIB_REQUIRE_DOCUTILS=1``, with the ``toolchain``
  shard keeping the compile probe, the two probes that skip are failed, saying why, and
  the plain one passes; the other library's skip is still a skip, since pytest hands the
  report hook the tests below its ``conftest.py`` alone;
* under uslib's two variables alone, every probe that skips is skipped (C2).

Four runs, about a second each.
"""
import os
import re
import shutil
import subprocess
import sys

import pytest

from uk_registry import LIB
from uk_sec_support import cython_shards

CONFTEST = LIB / "tests" / "conftest.py"

PROBE_UK = '''\
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

PROBE_ELSEWHERE = '''\
import pytest


@pytest.mark.cython
def test_compile_probe_elsewhere():
    pass


@pytest.mark.cython
def test_compile_probe_elsewhere_skips():
    pytest.skip("another library's compile test, which uklib's variables do not govern")
'''


@pytest.fixture(scope="module")
def probes(tmp_path_factory):
    """The runs' folder: uklib's ``conftest.py`` copied into ``uk/`` beside its probe, and
    ``elsewhere/``, another library's, under a ``pytest.ini`` that makes it the root."""
    root = tmp_path_factory.mktemp("conftest_probes")
    (root / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")
    for folder, probe, text in (("uk", "test_probe_uk.py", PROBE_UK),
                                ("elsewhere", "test_probe_elsewhere.py", PROBE_ELSEWHERE)):
        (root / folder).mkdir()
        (root / folder / probe).write_text(text, encoding="utf-8")
    shutil.copyfile(CONFTEST, root / "uk" / "conftest.py")
    return root


def _run(root, variables, *args):
    """``python -m pytest -v`` over both folders, in a subprocess, under ``variables`` and
    no other of uklib's and uslib's, nor options from ``PYTEST_ADDOPTS``: ``(exit code,
    output)``."""
    env = {key: value for key, value in os.environ.items()
           if not key.startswith(("UKLIB_", "USLIB_")) and key != "PYTEST_ADDOPTS"}
    env.update(variables)
    env["PYTHONPATH"] = os.pathsep.join(
        [str(LIB / "tests")] + ([env["PYTHONPATH"]] if env.get("PYTHONPATH") else []))
    done = subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "-v", "uk", "elsewhere",
         *args], cwd=root, env=env, capture_output=True, text=True, timeout=300)
    return done.returncode, done.stdout + done.stderr


def _outcomes(output):
    """Each probe's outcome in a run's ``-v`` output, by its name."""
    return {found.group(1): found.group(2) for found in re.finditer(
        r"::(test_\w+) (PASSED|FAILED|SKIPPED|ERROR)", output)}


def test_a_shard_counts_uklib_s_compile_tests_alone(probes):
    """The ``toolchain`` shard, under ``UKLIB_REQUIRE_CYTHON=1``, with ``-k`` deselecting
    uklib's compile probe, keeps no compile test of uklib's, and is a usage error: the
    other library's compile tests, which the run keeps, are not uklib's.  With ``_ours``
    counting every library's, it would pass on theirs, exit 0."""
    code, output = _run(probes, {"UKLIB_REQUIRE_CYTHON": "1",
                                 "UKLIB_CYTHON_SHARD": "toolchain"},
                        "-m", "cython", "-k", "not probe_uk")
    assert code == pytest.ExitCode.USAGE_ERROR, output
    assert ("UKLIB_REQUIRE_CYTHON=1, and UKLIB_CYTHON_SHARD='toolchain' selects no compile "
            "test") in output, output


def test_a_shard_that_is_no_shard_is_a_usage_error_that_lists_the_shards(probes):
    code, output = _run(probes, {"UKLIB_CYTHON_SHARD": "nonesuch"})
    assert code == pytest.ExitCode.USAGE_ERROR, output
    assert (f"UKLIB_CYTHON_SHARD='nonesuch' is no shard; the shards are "
            f"{', '.join(cython_shards())}") in output, output


def test_uklib_s_variables_fail_a_skip_of_uklib_s_tests_alone(probes):
    """Under ``UKLIB_REQUIRE_CYTHON=1`` and ``UKLIB_REQUIRE_DOCUTILS=1``, each uklib probe
    that skips is failed, saying which variable forbids it and why it skipped; the other
    library's compile test that skips is skipped.  The ``toolchain`` shard keeps uklib's
    compile probe, so the collection hook lets the run go on."""
    code, output = _run(probes, {"UKLIB_REQUIRE_CYTHON": "1", "UKLIB_REQUIRE_DOCUTILS": "1",
                                 "UKLIB_CYTHON_SHARD": "toolchain"})
    assert code == pytest.ExitCode.TESTS_FAILED, output
    assert _outcomes(output) == {
        "test_compile_probe": "FAILED", "test_docstring_probe": "FAILED",
        "test_plain_probe": "PASSED", "test_compile_probe_elsewhere": "PASSED",
        "test_compile_probe_elsewhere_skips": "SKIPPED"}, output
    for variable, reason in (("UKLIB_REQUIRE_CYTHON", "the probe finds no compiler"),
                             ("UKLIB_REQUIRE_DOCUTILS", "the probe finds no docutils")):
        assert re.search(rf"{variable}=1 forbids a skip, and it skipped: .*{reason}",
                         output), output


def test_uslib_s_variables_fail_no_skip_of_uklib_s(probes):
    """Under ``USLIB_REQUIRE_CYTHON=1`` and ``USLIB_REQUIRE_DOCUTILS=1`` alone, uslib's
    variables, every probe that skips is skipped: uklib's hook reads uklib's."""
    code, output = _run(probes, {"USLIB_REQUIRE_CYTHON": "1",
                                 "USLIB_REQUIRE_DOCUTILS": "1"})
    assert code == pytest.ExitCode.OK, output
    assert _outcomes(output) == {
        "test_compile_probe": "SKIPPED", "test_docstring_probe": "SKIPPED",
        "test_plain_probe": "PASSED", "test_compile_probe_elsewhere": "PASSED",
        "test_compile_probe_elsewhere_skips": "SKIPPED"}, output
