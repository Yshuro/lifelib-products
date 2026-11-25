"""Write, or check, the generated input files of one uslib or uklib SEC model.

Each SEC model, uslib's ``<Name>_US_SEC`` or uklib's ``<Name>_UK_SEC``, reads its own model
point table, ``model_point_table_sec.csv``, and some read ``*_sec.csv`` companions beside
it: in uslib, DIA's premium schedule, FIA's and RILA's scenarios re-based to each row, and
VA's two re-based scenarios (USLIB-SEC-PLAN.md D8).  None of those rows is typed by hand.
Every one is generated from the S model and its inputs as they stand: a twin from its S
row, a derived in-force row from S's own state at a chosen month, a future row from an S
new-business row.  The T6 test regenerates them and compares, so the committed files cannot
drift from S.  When S changes, a reworded ``provenance`` cell or a renamed lookup key, T6
fails until the files are regenerated, in the same commit.

This is a thin command line over ``write_generated`` and ``check_generated`` in the
harness of the model's library: ``lifelib/libraries/uslib/tests/sec_support.py`` for a
``_US_`` model, ``lifelib/libraries/uklib/tests/uk_sec_support.py`` for a ``_UK_`` one
(UKLIB-SEC-PLAN.md U3).  The logic lives there, beside the per-product specs in the
harness's ``SEC_SPECS``, because ``lifelib.create()`` copies a library's ``tests/`` but not
this repository's ``tools/``, and T6 must be able to regenerate inside such a copy.  So the
tool reads the library from the country tag in the model's name, ``_US_`` or ``_UK_``, puts
that library's ``tests/`` folder on ``sys.path`` and imports the harness from there
(``tools/sec_libraries.py``, UKLIB-SEC-PLAN.md U4).

Writing is deterministic.  A rerun with no S change touches no file, and a file is
rewritten only when a cell would change.  A float compares by its value, not its
spelling, so a rerun on another platform, whose pandas may spell some computed floats
otherwise, touches nothing either.

**Before committing what this writes, search it.**  The generator copies every text cell
from S or composes it from S's own keys and a month, and adds no name of its own.  It cannot
vouch for S, though, and T6 keeps the files in step with S without looking for names.  So
``CLAUDE.md``'s rule applies to every file written here as to any other input file: before
committing, search each one, case-insensitively, for every publisher and product the
product's ``sources.md`` cites (USLIB-SEC-PLAN.md §5.1, step 10).  Case-insensitively,
because a name lowercased into a lookup key slips past a case-sensitive search.  The tool
prints the files it wrote and the ``sources.md`` to search them against.

Usage::

    python tools/gen_sec_points.py Term_US_SEC
    python tools/gen_sec_points.py Term_US_SEC --check
    python tools/gen_sec_points.py Term_US_SEC --product-dir /tmp/term_copy

``--check`` writes nothing, prints the drift cell by cell, and exits 1 if there is any.
``--product-dir`` reads the S model and its inputs from a copy of the product directory, and
writes there, instead of the product directory in the registry.  A name that carries
neither tag, a model its library's harness has no spec for, or a malformed command line,
exits 2.
"""
import pathlib
import sys

import sec_libraries  # tools/sec_libraries.py, beside this script

USAGE = "usage: python tools/gen_sec_points.py <SEC model> [--check] [--product-dir DIR]"


def parse(argv):
    """``(name, check, product_dir)`` from the command line, or ``None`` if malformed."""
    names, check, product_dir = [], False, None
    args = iter(argv)
    for arg in args:
        if arg == "--check":
            check = True
        elif arg == "--product-dir":
            product_dir = next(args, None)
            if product_dir is None:
                return None
        elif arg.startswith("--product-dir="):
            product_dir = arg.partition("=")[2]
        elif arg.startswith("-"):
            return None
        else:
            names.append(arg)
    if len(names) != 1:
        return None
    return names[0], check, pathlib.Path(product_dir) if product_dir else None


def main(argv):
    parsed = parse(argv)
    if parsed is None:
        print(USAGE)
        return 2
    name, check, product_dir = parsed
    try:
        harness = sec_libraries.library(name).harness
    except sec_libraries.UnknownTag as err:
        print(err)
        return 2
    if name not in harness.SEC_SPECS:
        known = ", ".join(sorted(harness.SEC_SPECS)) or "none yet"
        print(f"no SecSpec is registered for {name!r} in {harness.__file__} "
              f"(registered: {known})")
        return 2

    if check:
        drift = harness.check_generated(name, product_dir)
        for line in drift:
            print(line)
        print(f"{name}: {len(drift)} differences from what S now generates" if drift
              else f"{name}: the generated files are current")
        return 1 if drift else 0

    written = harness.write_generated(name, product_dir)
    for path, changed in written.items():
        print(f"{'wrote    ' if changed else 'unchanged'} {path}")
    if any(written.values()):
        sources = next(iter(written)).parent / "sources.md"
        print(f"\nBefore committing, search the files written above, case-insensitively, "
              f"for every\npublisher and product {sources} cites (CLAUDE.md).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
