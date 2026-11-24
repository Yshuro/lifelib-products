"""mx2cy's sample run for IP_UK_SEC: the calls that type every cell.

mx2cy compiles the model's export, and it types each cell from the values this run passes
it and gets back: a cell it never calls compiles as a Python object, with a dict cache,
and the typing guard fails on it (USLIB-SEC-PLAN.md F3, C3).  So the run calls every
``Projection`` cell at least once, on every point of the committed table.  The three
reports and the three checks reach all but these: ``model_point`` and the five label
accessors, ``escalation``, ``premium_basis``, ``recovery_basis``, ``sex`` and ``status``,
which only a reader asks for; ``point_id``, which only a refusal names; ``occ_class`` and
``deferred_weeks``, which the inception rate reads through its schedule instead; and the
present value, its discount factor and the annuity factor, ``pv_benefits``,
``disc_factor`` and ``annuity_dis``, a companion no report reads.  And codes and keys of
cells the reports reach: the count at ``BEF_DECR`` and ``AFT_DECR``, which no cell reads,
and the cohorts outside the claim durations that can hold lives, ``pols_sick_dur`` at
claim duration 0 and past :func:`claim_dur_live`, which no sum reads.  Those are called here
too, every timing and every kind, the claims total among them, in every month of the frame
and the month after it, and every claim duration of the vector, 0 to ``max_dur()``, in
each of those months.  Every code inside the one inner width, 4, is one its cell takes but
the timing 3, which is refused, and is not called: a raise is not traced.

The run takes the committed points alone, at the shipped References, and they leave
branches untaken: a lapse rate at its bound, the caps on mortality and inception, the RPI's
floor and cap, the inception floor; and a power or a total past the largest float, which
the refusals reach.  That is enough to type every cell, because every branch of a cell
returns the one type its other branches return, a count or an amount a float in every
branch, ``0.0``, ``0`` or ``False`` outside cover.  What the compiled model computes on
those branches is not traced but tested: the compile tests run it there and compare it
with modelx, C4 on the splice grid, at the contract's extremes and where each cap binds,
and the refusal test on the overflows.

The five label accessors return text alone.  Each refuses any value but its column's
codes, ``invalid escalation``, ``invalid premium_basis``, ``invalid recovery_basis``,
``invalid sex`` and ``invalid status``, as ``IP_UK_S``'s ``escalation``, ``premium_basis``,
``recovery_basis`` and ``status`` do, so a label that is not text, a blank or a number,
raises in modelx as compiled, and none need be traced on one: each compiles to ``str``,
which the typing guard admits of a label that refuses its column blank and as a number.
"""
import sys

# The export does not raise the recursion limit as modelx does (F7).  The deepest call the
# contract allows, a cold claims(t, BENEFIT) in the last month of the longest cover, the
# anchor cell issued at 18 to expire at 70, now or 120 months on, at an RPI of 5%, needs
# a limit of 1,282 in the export, net_cf 1,279 and the oldest cohort the month can hold
# 1,278, and the reports and checks below, which run in ascending t, need 36 from a
# script's top level (measured at M8).  The chains run one cell a month, the cohorts' down
# their diagonal, and a cell is two Python frames in the export.  So the build itself needs
# 36, and the rest is margin for an edit that calls a cell cold.  The limit is four times
# the first, rounded up to the thousand, 6,000, which a test holds to this comment.
sys.setrecursionlimit(6_000)

from IP_UK_SEC_nomx import mx_model  # noqa: E402

projection = mx_model.Projection
timings = (projection.BEF_NB, projection.BEF_DECR, projection.AFT_DECR)
kinds = (projection.BENEFIT, projection.DEATH, projection.LAPSE, projection.ALL)
for idx in range(len(mx_model.Data.model_point_table())):
    p = projection[idx]
    p.result_cf()
    p.result_states()
    p.result_pols()
    p.check_pols_roll_fwd()
    p.check_states()
    p.check_benefit_max()
    p.model_point(), p.point_id(), p.occ_class(), p.deferred_weeks()
    p.escalation(), p.premium_basis(), p.recovery_basis(), p.sex(), p.status()
    p.pv_benefits(), p.annuity_dis()
    for t in range(p.proj_len() + 1):
        for code in timings:
            p.pols_if_at(t, code)
        for code in kinds:
            p.claims(t, code)
        p.disc_factor(t)
        for z in range(p.max_dur() + 1):
            p.pols_sick_dur(t, z)
