"""mx2cy's sample run for WP_UK_SEC: the calls that type every cell.

mx2cy compiles the model's export, and it types each cell from the values this run passes
it and gets back: a cell it never calls compiles as a Python object, with a dict cache,
and the typing guard fails on it (USLIB-SEC-PLAN.md F3, C3).  So the run calls every
``Projection`` cell at least once, on every point of the committed table, twice: at the
shipped References, the bonus rule off, and again with the rule on, each point's
ItemSpace made afresh, as an ItemSpace takes the References when it is made.  The three
reports and the seven checks reach all but these: ``model_point`` and the three label
accessors, ``chassis``, ``sex`` and ``tax_basis``, which only a reader asks for;
``point_id``, which only a refusal names; ``bonus_supportable`` and
``declaration_month``, which only the rule reads, and which the second pass reaches;
``policy_value_pp`` and ``smoothed_payout_capped``, which no cell reads, the payout
writing the cap inline; ``unit_price`` on the endowment, which no cell reads there; and the
six refusal cells, ``guar_charge_cum_refusal``, ``asset_share_refusal``,
``unit_price_refusal``, ``units_refusal``, ``guar_benefit_refusal`` and
``smoothing_account_refusal``, which only their chains' error paths call, where a value has
left the floats, and which return the value elsewhere.  And
codes of cells the reports reach: the count at ``AFT_DECR``, the end of the month, which no
cell reads; the asset share at ``AFT_MC``, which only its refusal reads; and
``smoothing_cost_pp`` at ``GUARANTEE``, which no flow reads.  Those are called here too,
every timing of ``pols_if_at`` and ``asset_share_at``, every kind of ``claim_pp`` and
``smoothing_cost_pp``, and every kind of ``claims`` and its total, in every month of the
frame and the month after it, as are the cells above.  Each call is of a code its cell
takes, so no call here raises: a raise is not traced.

The run takes the committed points alone, and they reach every branch that fixes a type:
both chassis, the rule off and on, the smoothing cap's floor and ceiling and the corridor's,
the market value reduction applied and waived on a guarantee date, the guarantee charge's
cap, the asset share floored at 0, the forced encashment, the endowment's maturity and the
limiting age's last month.  They leave branches untaken: the female life, the pension tax
basis on a bond, a binding mortality cap, the surrender rate at its bound, a power or a
value past the largest float, which the refusals reach.  That is enough to type every
cell, because every branch of a cell returns the one type its other branches return, a
count, an amount or a rate a float in every branch, ``0.0`` or ``False`` outside cover.
What the compiled model computes on those branches is not traced but tested: the compile
tests run it there and compare it with modelx, C4 on the splice grid, at the contract's
extremes and where each cap and bound binds, and the refusal test on the overflows.

The three label accessors return text alone.  Each refuses any value but its column's
codes, ``invalid chassis; ...``, ``invalid sex`` or ``invalid tax_basis``, as
``WP_UK_S``'s ``chassis`` and ``tax_basis`` do, so a label that is not text, a blank or a
number, raises in modelx as compiled, and none need be traced on one: each compiles to
``str``, which the typing guard admits of a label that refuses its column blank and as a
number.
"""
import sys

# The export does not raise the recursion limit as modelx does (F7).  The deepest call the
# contract allows, a cold net_cf in the last month of the longest cover, the endowment
# issued at 18 for 103 years to 121, the longest cover proj_len admits, now or 120 months
# on, with the bonus rule and the estate's distribution on, needs a limit of 490 in the
# export, the guarantee's and the unit price's 489, and the reports and checks below,
# which run in ascending t, need 128 from a script's top level (measured at M14).
# The eight chains are blocked by policy year, so a cold call runs one cell a month within
# its year and two cells a year before it.  So the build itself needs 128, and the rest is
# margin for an edit that calls a cell cold.  The limit is four times the first, rounded
# up to the thousand, 2,000, which a test holds to this comment.
sys.setrecursionlimit(2_000)

from WP_UK_SEC_nomx import mx_model  # noqa: E402

projection = mx_model.Projection
timings = (projection.BEF_NB, projection.BEF_DECR, projection.BEF_SURR,
           projection.AFT_DECR)
as_timings = (projection.BEF_PREM, projection.BEF_RETURN, projection.AFT_RETURN,
              projection.AFT_CHARGE, projection.AFT_ST, projection.AFT_MC)
kinds = (projection.DEATH, projection.SURRENDER, projection.GUARANTEE,
         projection.MATURITY)
claim_kinds = (projection.DEATH, projection.SURRENDER, projection.MATURITY,
               projection.ALL)
for rule in (False, True):
    projection.bonus_rule_on = rule
    for idx in range(len(mx_model.Data.model_point_table())):
        p = projection[idx]
        p.result_cf()
        p.result_payout()
        p.result_pols()
        p.check_pols_roll_fwd()
        p.check_asset_share_roll_fwd()
        p.check_fb_mvr_exclusive()
        p.check_mvr_bound()
        p.check_fund_nonneg()
        p.check_payout_corridor()
        p.check_declaration_is_annual()
        p.model_point(), p.point_id(), p.chassis(), p.sex(), p.tax_basis()
        for t in range(p.proj_len() + 1):
            for code in timings:
                p.pols_if_at(t, code)
            for code in as_timings:
                p.asset_share_at(t, code)
            for code in kinds:
                p.claim_pp(t, code)
                p.smoothing_cost_pp(t, code)
            for code in claim_kinds:
                p.claims(t, code)
            p.policy_value_pp(t)
            p.smoothed_payout_capped(t)
            p.unit_price(t)
            p.bonus_supportable(t)
            p.declaration_month(t)
            p.guar_charge_cum_refusal(t)
            p.asset_share_refusal(t)
            p.unit_price_refusal(t)
            p.units_refusal(t)
            p.guar_benefit_refusal(t)
            p.smoothing_account_refusal(t)
        del projection[idx]
