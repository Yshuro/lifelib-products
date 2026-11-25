"""mx2cy's sample run for Term_UK_SEC: the calls that type every cell.

mx2cy compiles the model's export, and it types each cell from the values this run passes
it and gets back: a cell it never calls compiles as a Python object, with a dict cache,
and the typing guard fails on it (USLIB-SEC-PLAN.md F3, C3).  So the run calls every
``Projection`` cell at least once, on every point of the committed table.  The two reports
and the two checks reach all but these: ``model_point`` and the five label accessors,
which only a reader asks for; ``point_id``, which only a refusal names; and the count at
``AFT_DECR``, the end of the month, which ``Term_UK_S``'s count chain read and this
model's carries at ``BEF_NB`` instead.  Those are called here too, the count in every month
of the frame and the month after it.  Every other timing and every kind are reached by the
reports and the checks.  A code a cell refuses is not called, since a raise is not traced.

The run takes the committed points alone, at the shipped References, and they leave
branches untaken: an annual payer, a family income benefit commuted in part, an indexed
waiver point, the decreasing shape at a schedule rate of 0 and a joint life who smokes,
which the splice grid's variants take; the clawback window open, which its References
open; the cap on mortality, which the cap's points reach; a commutation discount of 0, and
one whose monthly rate rounds to 0, 1e-17, at which the committed points run; and a power
past the largest float, which the refusals reach.  That is enough to type every cell,
because every branch of a cell returns the one type its other branches return, a count a
float in every branch, ``0.0`` or ``False`` outside cover.  What the compiled model
computes on those branches is not traced but tested: the compile tests run it there and
compare it with modelx, C4 on the splice grid, where the cap binds and at the two
discounts, and the refusal test on the overflows.

The label accessors are typed from more than the committed points.  ``shape()``,
``premium_mode()`` and ``mort_basis()`` validate their column, as ``Term_UK_S``'s do, so
each returns text or raises, and compiles to ``str``.  But ``sex(life)`` and
``smoker(life)`` return each life's column as read, and ``Data`` checks the second life's
on a joint point alone, so a single-life point's ``joint_sex`` and ``joint_smoker`` may be
a blank, which the committed table holds, or a number, which pandas reads as an int and no
projection reads.  An accessor traced on text alone would compile to ``str`` and raise
``TypeError`` on a number.  So the run also calls ``sex(1)``, ``sex(2)``, ``smoker(1)``
and ``smoker(2)`` on a copy of the table's first point, a single life, with its second
life's columns blank, written to a temporary directory and read by a second instance of
the export, whose ``Data`` reads it by an absolute ``model_point_file``; ``Data`` refuses
a ``sex`` other than M or F, and a ``smoker`` other than N or S, on every point, so each
first life's is text.  mx2cy then types ``sex`` and ``smoker`` as Python objects, the
reporting cells they are, and the compiled model returns what modelx returns.  Nothing is
written beside the export, and no other cell is called there but ``model_point``,
``model_point_table`` and ``input_dir``, which are typed already: the waiver pipeline
names points the copy lacks, and no call reads it.
"""
import pathlib
import sys
import tempfile

# The export does not raise the recursion limit as modelx does (F7).  The deepest call the
# contract allows, a cold net_cf in the last month of the longest cover, the waiver point
# on the select basis issued at 18 on a 50-year term, now or 120 months on, needs a limit
# of 1,246 in the export, and the reports and checks below, which run in ascending t, need
# 128 from a script's top level (measured at M2).  So the build itself needs 128, and the
# rest is margin for an edit that calls a cell cold.  The limit is four times the first,
# rounded up to the thousand, 5,000, which a test holds to this comment.
sys.setrecursionlimit(5_000)

import pandas as pd  # noqa: E402

from Term_UK_SEC_nomx import mx_model  # noqa: E402
from Term_UK_SEC_nomx._mx_model import _c_Term_UK_SEC  # noqa: E402

projection = mx_model.Projection
for idx in range(len(mx_model.Data.model_point_table())):
    p = projection[idx]
    p.result_cf()
    p.result_pols()
    p.check_pols_roll_fwd()
    p.check_fib_ledger()
    p.model_point(), p.shape(), p.premium_mode(), p.mort_basis(), p.point_id()
    p.sex(1), p.sex(2), p.smoker(1), p.smoker(2)
    for t in range(p.proj_len() + 1):
        p.pols_if_at(t, projection.AFT_DECR)

data = mx_model.Data
blank = pd.read_csv(data.input_dir() / data.model_point_file).iloc[[0]]
blank = blank.assign(joint_first_death=False, joint_sex=None, joint_smoker=None)
with tempfile.TemporaryDirectory() as folder:
    path = pathlib.Path(folder) / "blank_second_life.csv"
    blank.to_csv(path, index=False)
    second = _c_Term_UK_SEC()
    second.Data.model_point_file = str(path)
    p = second.Projection[0]
    (p.sex(1), p.sex(2), p.smoker(1), p.smoker(2))
    del p, second
