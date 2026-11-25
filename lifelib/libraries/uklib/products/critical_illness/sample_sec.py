"""mx2cy's sample run for CI_UK_SEC: the calls that type every cell.

mx2cy compiles the model's export, and it types each cell from the values this run passes
it and gets back: a cell it never calls compiles as a Python object, with a dict cache,
and the typing guard fails on it (USLIB-SEC-PLAN.md F3, C3).  So the run calls every
``Projection`` cell at least once, on every point of the committed table.  The two reports
and the two checks reach all but these: ``model_point`` and the seven label accessors,
which only a reader asks for, and ``point_id``, which only a refusal names.  Those are
called here too.  Every timing and every kind a cell takes are reached by the reports and
the checks, the claims total, ``ALL``, through ``net_cf``.  A code a cell refuses is not
called, since a raise is not traced.

The run takes the committed points alone, at the shipped References, and they leave
branches untaken: a review that changes the premium in the frame, its shock window and
the latch it closes, which the review change of 0 shipped leaves at their issue values on
every point but 14, read under a change of its own; the standalone contract reviewable,
the joint point reviewable, a male smoker, cover below the ancillary caps and ages past
the last pivot, which the splice grid's variants take; the caps on the claim rates, which
the cap's points reach; and a power past the largest float, which the refusals reach.
That is enough to type every cell, because every branch of a cell returns the one type
its other branches return, a count a float in every branch, ``0.0``, ``0`` or ``False``
outside cover.  What the compiled model computes on those branches is not traced but
tested: the compile tests run it there and compare it with modelx, C4 on the splice grid
and where the caps bind, and the refusal test on the overflows.

The label accessors are typed from more than the committed points.  ``contract_type()``,
``life_basis()``, ``cover_basis()``, ``premium_guarantee()`` and ``premium_mode()``
validate their column, as ``CI_UK_S``'s first four do, so each returns text or raises, and
compiles to ``str``.  But ``sex(life)`` and ``smoker(life)`` return each life's column as
read, and ``Data`` checks the second life's on a joint point alone, so a single-life
point's ``joint_sex`` and ``joint_smoker`` may be a blank, which the committed table
holds, or a number, which pandas reads as an int and no projection reads.  An accessor
traced on text alone would compile to ``str`` and raise ``TypeError`` on a number.  So the
run also calls ``sex(1)``, ``sex(2)``, ``smoker(1)`` and ``smoker(2)`` on a copy of the
table's first point, a single life, with its second life's columns blank, written to a
temporary directory and read by a second instance of the export, whose ``Data`` reads it
by an absolute ``model_point_file``; ``Data`` refuses a ``sex`` other than M or F, and a
``smoker`` other than NS or S, on every point, so each first life's is text.  mx2cy then
types ``sex`` and ``smoker`` as Python objects, the reporting cells they are, and the
compiled model returns what modelx returns.  Nothing is written beside the export, and no
other cell is called there but ``model_point``, ``model_point_table`` and ``input_dir``,
which are typed already.
"""
import pathlib
import sys
import tempfile

# The export does not raise the recursion limit as modelx does (F7).  The deepest call the
# contract allows, a cold net_cf in the last month of the longest cover, a 50-year term
# from 18, now or 120 months on, on the reviewable, the standalone and the joint shape
# alike, with the review change and the trend on, needs a limit of 1,242 in the export,
# and the reports and checks below, which run in ascending t, need 128 from a script's top
# level (measured at M4).  So the build itself needs 128, and the rest is margin for an
# edit that calls a cell cold.  The limit is four times the first, rounded up to the
# thousand, 5,000, which a test holds to this comment.
sys.setrecursionlimit(5_000)

import pandas as pd  # noqa: E402

from CI_UK_SEC_nomx import mx_model  # noqa: E402
from CI_UK_SEC_nomx._mx_model import _c_CI_UK_SEC  # noqa: E402

projection = mx_model.Projection
for idx in range(len(mx_model.Data.model_point_table())):
    p = projection[idx]
    p.result_cf()
    p.result_pols()
    p.check_pols_roll_fwd()
    p.check_claim_split()
    p.model_point(), p.contract_type(), p.life_basis(), p.cover_basis()
    p.premium_guarantee(), p.premium_mode(), p.point_id()
    p.sex(1), p.sex(2), p.smoker(1), p.smoker(2)

data = mx_model.Data
blank = pd.read_csv(data.input_dir() / data.model_point_file).iloc[[0]]
blank = blank.assign(life_basis="single", joint_sex=None, joint_smoker=None)
with tempfile.TemporaryDirectory() as folder:
    path = pathlib.Path(folder) / "blank_second_life.csv"
    blank.to_csv(path, index=False)
    second = _c_CI_UK_SEC()
    second.Data.model_point_file = str(path)
    p = second.Projection[0]
    (p.sex(1), p.sex(2), p.smoker(1), p.smoker(2))
    del p, second
