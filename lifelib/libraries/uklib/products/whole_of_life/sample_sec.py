"""mx2cy's sample run for WOL_UK_SEC: the calls that type every cell.

mx2cy compiles the model's export, and it types each cell from the values this run passes
it and gets back: a cell it never calls compiles as a Python object, with a dict cache,
and the typing guard fails on it (USLIB-SEC-PLAN.md F3, C3).  So the run calls every
``Projection`` cell at least once, on every point of the committed table.  The two
reports and the two checks reach all but these: ``model_point`` and the five label
accessors, ``cell``, ``escalation``, ``mort_basis``, ``sex`` and ``smoker``, which only a
reader asks for; ``point_id``, which only a refusal names; ``crossover_mth``, which no
projection cell reads; and the two refusal cells, ``prem_cum_pp_refusal`` and
``pu_benefit_refusal``, which only the error paths of ``prem_cum_pp`` and ``pu_benefit``
call, where a total has left the floats, and which return the total elsewhere.  And codes
of cells the reports reach: the count at ``AFT_DECR``, the end of the month, which no
cell reads, and on the underwritten cell the moratorium's and the accidental benefit's
kinds, which only the over-50s blend reads.  Those are called here too, every timing and
every kind, the claims total among them, in every month of the frame and the month after
it, as are the two refusal cells.  Every code inside the one inner width, 4, is one its
cell takes, so no call here raises: a raise is not traced.

The run takes the committed points alone, at the shipped References, and they leave
branches untaken: the crossover stress, a lapse rate at its bound, the cap on mortality
with improvement on, the RPI's floor and caps, an odd cessation, an issue age of 80; and a
power or a total past the largest float, which the refusals reach.  That is enough to type
every cell, because every branch of a cell returns the one type its other branches
return, a count or an amount a float in every branch, ``0.0``, ``0`` or ``False`` outside
cover.  What the compiled model computes on those branches is not traced but tested: the
compile tests run it there and compare it with modelx, C4 on the splice grid, at the
contract's extremes and where each cap binds, and the refusal test on the overflows.

The five label accessors return text alone.  Each refuses any value but its column's
codes, ``invalid cell``, ``invalid escalation``, ``invalid sex`` or ``invalid smoker``, as
``WOL_UK_S``'s ``cell`` and ``escalation`` do, and ``mort_basis`` reads ``cell``, so a
label that is not text, a blank or a number, raises in modelx as compiled, and none need
be traced on one: each compiles to ``str``, which the typing guard admits of a label that
refuses its column blank and as a number.
"""
import sys

# The export does not raise the recursion limit as modelx does (F7).  The deepest call the
# contract allows, a cold claims(t, DEATH_PU) in the last month of the longest cover, the
# paid-up point issued at 18 to the contract's largest omega_age, omega_age_max, 121, now
# or 120 months on, with the stress and improvement on, needs a limit of 492 in the
# export, the paid-up count 490 and net_cf 466, and the reports and checks below, which run
# in ascending t, need 128 from a script's top level (measured at M6).  The four chains are
# blocked by policy year, so a cold call runs one cell a month within its year and two cells
# a year before it.  So the build itself needs 128, and the rest is margin for an edit
# that calls a cell cold.  The limit is four times the first, rounded up to the thousand,
# 2,000, which a test holds to this comment.
sys.setrecursionlimit(2_000)

from WOL_UK_SEC_nomx import mx_model  # noqa: E402

projection = mx_model.Projection
codes = (projection.BEF_NB, projection.BEF_DECR, projection.BEF_LAPSE,
         projection.AFT_DECR)
benefits = (projection.DEATH, projection.NON_ACC, projection.ACC, projection.PAID_UP)
kinds = (projection.DEATH, projection.DEATH_PU, projection.LAPSE, projection.ALL)
for idx in range(len(mx_model.Data.model_point_table())):
    p = projection[idx]
    p.result_cf()
    p.result_pols()
    p.check_pols_roll_fwd()
    p.check_truncation()
    p.model_point(), p.point_id(), p.crossover_mth()
    p.cell(), p.escalation(), p.mort_basis(), p.sex(), p.smoker()
    for t in range(p.proj_len() + 1):
        for code in codes:
            p.pols_if_at(t, code)
        for code in benefits:
            p.benefit_pp(t, code)
        for code in kinds:
            p.claims(t, code)
        p.prem_cum_pp_refusal(t)
        p.pu_benefit_refusal(t)
