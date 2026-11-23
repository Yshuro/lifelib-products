"""mx2cy's sample run for ULB_UK_SEC: the calls that type every cell.

mx2cy compiles the model's export, and it types each cell from the values this run passes
it and gets back: a cell it never calls compiles as a Python object, with a dict cache,
and the typing guard fails on it (USLIB-SEC-PLAN.md F3, C3).  So the run calls every
``Projection`` cell at least once, on every point of the committed table.  The three
reports and the three checks reach all but these: ``model_point`` and the three label
accessors, ``sex``, ``lives`` and ``wd_pattern``, which only a reader asks for;
``point_id``, which only a refusal names; ``av_pp_grown_refusal``, which only
``av_pp_at``'s error path calls, where the fund has left the floats, and which returns the
fund grown elsewhere; and ``av_per_segment_pp``, with ``n_segments``, which only it
reads, the fund per segment no report prints.  And two codes of cells the reports reach:
the count at ``AFT_DECR``, the end of the month, which ``ULB_UK_S``'s count chain read in
every month and this model's reads only where a policy year's opening ends, carrying the
count at ``BEF_NB`` instead, and the fund at ``BEF_GROWTH``, the start of the month,
which is ``av_pp``.  Those are called here too, in every month of the frame and the month
after it, as are the fund grown's refusal and the fund per segment.  Every other timing
and every kind are reached by the reports and the checks.  A code a cell refuses is not
called, since a raise is not traced.

The run takes the committed points alone, at the shipped References, and they leave
branches untaken: the custom pattern above the 7.5% cap, the cap binding net of an adviser
charge, the rider beside an adviser charge, the surrender cap and the performance
multiplier binding, which the splice grid's variants and References take; the cap on
mortality, which the cap's points reach; and a power past the largest float, which the
refusals reach.  That is enough to type every cell, because every branch of a cell returns
the one type its other branches return, a count or an amount a float in every branch,
``0.0`` or ``False`` outside cover.  What the compiled model computes on those branches is
not traced but tested: the compile tests run it there and compare it with modelx, C4 on
the splice grid, at the contract's extremes and where the cap binds, and the refusal test
on the overflow.

The three label accessors return text alone.  Each refuses any value but its column's
codes, ``invalid sex``, ``invalid lives`` or ``invalid wd_pattern``, as ``ULB_UK_S``'s
``lives`` and ``wd_pattern`` do, so a label that is not text, a blank or a number, raises
in modelx as compiled, and none need be traced on one: each compiles to ``str``, which the
typing guard admits of a label that refuses its column blank and as a number.
"""
import sys

# The export does not raise the recursion limit as modelx does (F7).  The deepest call the
# contract allows, a cold check_unit_funding_resid in the last month of the longest cover,
# the GMDB point with no withdrawals, issued at 18 and its rider charged to the limiting
# age, 120, now or 120 months on, needs a limit of 473 in the export, its net_cf 469, and
# the reports and checks below, which run in ascending t, need 128 from a script's top
# level (measured at M10).  The chains are blocked by policy year, so a cold call runs one
# cell a month within its year and two cells a year before it.  So the build itself needs
# 128, and the rest is margin for an edit that calls a cell cold.  The limit is four times
# the first, rounded up to the thousand, 2,000, which a test holds to this comment.
sys.setrecursionlimit(2_000)

from ULB_UK_SEC_nomx import mx_model  # noqa: E402

projection = mx_model.Projection
for idx in range(len(mx_model.Data.model_point_table())):
    p = projection[idx]
    p.result_cf()
    p.result_uf()
    p.result_pols()
    p.check_av_roll_fwd()
    p.check_pols_roll_fwd()
    p.check_unit_funding()
    p.model_point(), p.point_id(), p.sex(), p.lives(), p.wd_pattern()
    for t in range(p.proj_len() + 1):
        p.pols_if_at(t, projection.AFT_DECR)
        p.av_pp_at(t, projection.BEF_GROWTH)
        p.av_pp_grown_refusal(t)
        p.av_per_segment_pp(t)
