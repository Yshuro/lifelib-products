# mx2cy's spec for WP_UK_SEC: the length of each C-array cache in Projection, by the
# cells' parameters (USLIB-SEC-PLAN.md F4, section 6.1 step 6; UKLIB-SEC-PLAN.md 6.5).  A
# compiled cache raises IndexError for an argument outside [0, size), so each size covers
# the largest argument any cell is called with on a point the contract allows, in its
# frame and in the month after it, t = proj_len(), which the roll-forward reads and C4's
# full sweep evaluates every monthly cell at; plus one because the index starts at 0.  No
# size has headroom past that: each is held to its derivation by a test.  mx2cy keys a
# size by a cell's parameter names, so every cell taking t alone shares one.  The contract
# is three References and one of Data's.  Projection.proj_len refuses a point issued below
# issue_age_min, 18, the youngest age the mortality table rates; an omega_age, the
# limiting age every bond's cover ends at, above omega_age_max, 121, the shipped table's
# last age plus one, the most the table admits; and an endowment maturing past omega_age;
# and Data refuses a point issued more than future_horizon_mth, 120 months, after the
# valuation date.  And each of the three is held to the value these sizes are derived
# from: proj_len refuses an issue_age_min below 18 and an omega_age_max above 121, and
# Data a future_horizon_mth above 120, so that no value of a Reference admits a frame the
# compiled model would read past its caches, raising IndexError where modelx projects
# (UKLIB-SEC-PLAN.md 6.5, Record -- M14).  So no point a report projects outruns these
# sizes, and a bound moved is moved in the model's check, here and in the spec test
# together, and the model rebuilt.  The units' exhaustion only shortens a frame, and its
# search reads the units in the months of cover alone.  The ages bound no cache: an age
# indexes Data's mortality table, not a cache.
#
# t, months from the valuation date.  The longest frame is the longest cover, a bond issued
# at issue_age_min, 18, whose units last to omega_age_max, 121, or an endowment maturing
# there: 12 * (121 - 18) = 1,236 months from issue, issued future_horizon_mth, 120 months,
# after the valuation date: 1,356 months, t = 0 .. 1,355, and 1,356 in the month after it;
# and the roll-forward's residual there, check_pols_roll_fwd_resid(1356), reads the count
# carried into 1,357, pols_if(1357): 1,358, which is 12 * (omega_age_max - issue_age_min) +
# future_horizon_mth + 2.  A longer future_horizon_mth, a higher omega_age_max or a lower
# issue_age_min needs t raised to 12 * (omega_age_max - issue_age_min) + the horizon + 2.
# timing, beside t in pols_if_at and asset_share_at: BEF_NB = 0 to AFT_DECR = 3, the
# count's, and BEF_PREM = 4 to AFT_MC = 9, the asset share's, one numbering for the two
# families, the count's first: 10.
# kind, beside t in claim_pp, smoothing_cost_pp and claims: DEATH = 0 to MATURITY = 3 and
# ALL = 4, the claims total, the codes, 5; widened to 10, since every 2-D cache of a model
# shares one inner width, the widest, the timings' 10: Cython's unpickle code converts the
# 2-D caches with one function, and two widths are refused by gcc 14 and would write past
# the narrower array (USLIB-SEC-PLAN.md 7.2, Record -- M15).  So a kind 5 to 9 is inside the
# cache, where the cell refuses it as modelx does, ValueError("invalid kind"), as each
# cell refuses a code of the other family's or a kind it does not take, and a code from 10
# raises IndexError, compiled alone.
# y, a policy year, in the openings of the year the eight chains are blocked by,
# pols_if_py, asset_share_py, smoothed_payout_py, guar_benefit_pp_py, units_py,
# unit_price_py, guar_charge_cum_pp_py and smoothing_account_py, and in
# is_guarantee_year, the one reader of the guarantee dates.  An opening is read in the
# first month of policy year y, in cover and after t_entry(), so y runs from 2 to the
# policy year of the last month of the longest cover, 12 * (121 - 18) - 1 = 1,235, policy
# year 1235 // 12 + 1 = 103.  The guarantee-imminent window of that last month, the
# twelfth of policy year 103, waits for the date that closes policy year 104, which
# is_guarantee_year is asked of in that month and in the month after it, the frame's
# end: 105, which is omega_age_max - issue_age_min + 2.  A higher omega_age_max or a lower
# issue_age_min needs y raised to omega_age_max - issue_age_min + 2; the horizon moves no
# policy year.
{"spaces": {"Projection": {"cells_param_size": {
    "t": 1358, ("t", "timing"): (1358, 10), ("t", "kind"): (1358, 10), "y": 105}}}}
