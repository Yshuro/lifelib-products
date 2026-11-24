"""mx2cy's sample run for PA_UK_SEC: the calls that type every cell.

mx2cy compiles the model's export, and it types each cell from the values this run passes
it and gets back: a cell it never calls compiles as a Python object, with a dict cache,
and the typing guard fails on it (USLIB-SEC-PLAN.md F3, C3).  So the run calls every
``Projection`` cell at least once, on every point of the committed table.  The two reports
and the four checks reach every cell but these: ``model_point`` and the five label
accessors, which only a reader asks for; ``point_id``, which only a refusal names; the
dependant's ``lives_death``, which the last-death density replaces in every flow;
``is_payment_mth``, which value protection asks in advance alone and no committed point
with value protection pays in advance; ``next_payment_mth`` and ``mths_since_payment``,
which only the proportionate payment reads; ``cum_annuity_pp`` at ``ALL``, through
``cum_annuity_pp_all``, which no cell reads, its total being ``cum_annuity_all``'s; and
the three refusals moved off the chains, ``annual_income_refusal``,
``cum_annuity_all_refusal`` and ``cum_annuity_pp_refusal``, which only their cells' error
paths call, where a value has left the floats, and which return the value elsewhere.
Those are called here too: the monthly ones in every month of the frame and the month
after it, the payments to date at every key a projection reads, from the valuation date's
key to the stop rule's, and the income's refusal in every year from the one under way at
the valuation date to the frame's last.  Every timing of ``pols_if_at`` and every kind of
``claims`` are reached by the reports, and ``cum_annuity_pp``'s ``ANNUITANT`` by value
protection on the first death.  A code a cell refuses is not called, since a raise is not
traced.

The run takes the committed points alone, at the shipped References, and they leave
branches untaken: semi-annual and annual payments, a dependant older than the annuitant,
value protection paid in advance, the LPI's cap and floor binding, a ratchet whose peak
the index passes, and a power, an income or a total past the largest float.  That is
enough to type every cell, because every branch of a cell returns the one type its other
branches return, a probability or an amount a float in every branch, ``0.0`` or
``False`` outside the frame.  What the compiled model computes on those branches is not
traced but tested: the compile tests run it there and compare it with modelx, C4 on the
splice grid, at the contract's extremes and where the cap binds, and the refusal test on
the overflows.

The labels are typed from the committed points too.  ``payment_timing()``,
``escalation_type()``, ``vp_basis()`` and ``mort_basis()`` validate their column, as
``PA_UK_S``'s do, so each returns text or raises, and compiles to ``str``.  But
``sex(life)`` returns its column as read, and the committed table holds three single-life
points, whose ``dependant_sex`` is blank: ``sex(2)`` returns NaN there, a float beside the
text of every other call, and mx2cy types ``sex`` as a Python object, the reporting cell it
is, so that the compiled model returns what modelx returns on a blank or a number, which
``Data`` holds where no projection reads the sex.
"""
import sys

# The export does not raise the recursion limit as modelx does (F7).  The deepest call the
# contract allows, a cold cum_annuity_all or claims total in the last month of the longest
# cover, the table basis under a guarantee of 1,392 months from 50 at the largest limiting
# age, omega_age_max, 116, now or 120 months on, needs a limit of 521 in the export, its
# net_cf 500 to 507, and the reports and checks below, which run in ascending t, need 128
# from a script's top level (measured at M12).
# The three chains are blocked by policy year, so a cold call runs one cell a month within
# its year and two cells a year before it.  So the build itself needs 128, and the rest is
# margin for an edit that calls a cell cold.  The limit is four times the first, rounded up
# to the thousand, 3,000, which a test holds to this comment.
sys.setrecursionlimit(3_000)

from PA_UK_SEC_nomx import mx_model  # noqa: E402

projection = mx_model.Projection
for idx in range(len(mx_model.Data.model_point_table())):
    p = projection[idx]
    p.result_cf()
    p.result_pols()
    p.check_lives_roll_fwd()
    p.check_payment_factor()
    p.check_guarantee_xor()
    p.check_vp_bound()
    p.model_point(), p.point_id(), p.sex(1), p.sex(2)
    p.payment_timing(), p.escalation_type(), p.vp_basis(), p.mort_basis()
    end = p.proj_len()
    for t in range(end + 1):
        p.is_payment_mth(t)
        p.next_payment_mth(t)
        p.mths_since_payment(t)
        p.lives_death(t, 1)
        p.lives_death(t, 2)
        p.cum_annuity_all_refusal(t)
    for k in range(max(p.duration_mth_init(), 0), p.duration_mth(end) + 1):
        p.cum_annuity_pp(k, projection.ALL)
        p.cum_annuity_pp_refusal(k)
    for y in range(p.policy_year_init(), p.policy_year(end - 1) + 1):
        p.annual_income_refusal(y)
