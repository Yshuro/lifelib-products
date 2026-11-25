"""The library an SEC model belongs to, read from the country tag in its name.

An SEC model's name carries its library's country tag: uslib's are ``<Name>_US_SEC``
(USLIB-SEC-PLAN.md D1) and uklib's ``<Name>_UK_SEC`` (UKLIB-SEC-PLAN.md U1).  Each library
keeps its SEC harness and its model registry in its own ``tests/``, under names of its
own: ``sec_support`` and ``us_registry`` in uslib, ``uk_sec_support`` and ``uk_registry``
in uklib.  lifelib copies one library at a time, so each must carry both, and two modules
of one name, imported in one process, would collide in ``sys.modules``
(UKLIB-SEC-PLAN.md U3).

``tools/gen_sec_points.py`` and ``tools/gen_sec_fingerprint.py`` serve both libraries
(UKLIB-SEC-PLAN.md U4).  Each hands the model's name to :func:`library`, which reads the
tag, puts that library's ``tests/`` on ``sys.path`` and imports its harness and its registry
from there.  :data:`TAGS` is the choice between libraries, written once; a library that
gains SEC models gains a line.  A name carrying none of its tags, or more than one, raises
:class:`UnknownTag`, and the tools report it as they report a model their library does not
register: they print why and exit 2.
"""
import dataclasses
import importlib
import pathlib
import sys
import types

LIBRARIES = pathlib.Path(__file__).resolve().parents[1] / "lifelib" / "libraries"

# The country tag in an SEC model's name -> its library, and the harness and the registry
# modules in that library's tests/.
TAGS = {
    "_US_": ("uslib", "sec_support", "us_registry"),
    "_UK_": ("uklib", "uk_sec_support", "uk_registry"),
}


class UnknownTag(LookupError):
    """A model name that carries no tag of :data:`TAGS`, or more than one."""


@dataclasses.dataclass(frozen=True)
class Library:
    """One library's SEC modules, imported: the library's folder name, its ``tests/``, its
    harness and its registry."""
    name: str
    tests: pathlib.Path
    harness: types.ModuleType
    registry: types.ModuleType


def library(model):
    """The library of the model named ``model``, its harness and its registry imported.

    The library is the one whose tag the name carries: ``Term_US_SEC`` is uslib's and
    ``Term_UK_SEC`` uklib's.  Its ``tests/`` goes first on ``sys.path``, where the harness
    finds the registry it imports.  Whether the library knows the model is the caller's
    question, which the harness's ``SEC_SPECS`` or the registry's ``MODELS`` answers.
    Raises :class:`UnknownTag`, before anything is imported, when the name carries no tag
    of :data:`TAGS` or more than one.
    """
    tags = [tag for tag in TAGS if tag in model]
    known = " or ".join(f"{tag} for {lib}" for tag, (lib, _, _) in TAGS.items())
    if not tags:
        raise UnknownTag(f"{model!r} names no library: an SEC model's name carries its "
                         f"library's country tag, {known}")
    if len(tags) > 1:
        names = " and ".join(TAGS[tag][0] for tag in tags)
        raise UnknownTag(f"{model!r} names {len(tags)} libraries, {names}: an SEC model's "
                         f"name carries one country tag, {known}")
    name, harness, registry = TAGS[tags[0]]
    tests = LIBRARIES / name / "tests"
    sys.path.insert(0, str(tests))
    return Library(name, tests, importlib.import_module(harness),
                   importlib.import_module(registry))
