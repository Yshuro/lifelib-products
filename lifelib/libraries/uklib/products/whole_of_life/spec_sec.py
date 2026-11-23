# mx2cy's spec for WOL_UK_SEC: the length of each C-array cache in Projection, by the
# cells' parameters (USLIB-SEC-PLAN.md F4, section 6.1 step 6; UKLIB-SEC-PLAN.md 6.4).  A
# compiled cache raises IndexError for an argument outside [0, size), so each size covers
# the largest argument any cell is called with on a point the contract allows, in its
# frame and in the month after it, t = proj_len(), which the roll-forward reads and C4's
# full sweep evaluates every monthly cell at; plus one because the index starts at 0.  No
# size has headroom past that: each is held to its derivation by a test.  mx2cy keys a
# size by a cell's parameter names, so every cell taking t alone shares one.  The contract
# is three References and one of Data's.  Projection.proj_len refuses a point issued below
# issue_age_min, 18, the youngest age the mortality table rates; and an omega_age, the
# limiting age every frame ends at, above omega_age_max, 121, the shipped table's last age
# plus one, the most the table admits; and Data refuses a point issued more than
# future_horizon_mth, 120 months, after the valuation date.  So no point a report projects
# outruns these sizes, and a change to omega_age_max, issue_age_min or the horizon needs
# them recomputed here and the model rebuilt.  The ages bound no cache: an age indexes
# Data's mortality table, not a cache.
#
# t, months from the valuation date.  The longest frame is the longest cover, a policy
# issued at issue_age_min, 18, to omega_age_max, 121: 12 * (121 - 18) = 1,236 months from
# issue, issued future_horizon_mth, 120 months, after the valuation date: 1,356 months,
# t = 0 .. 1,355, and 1,356 in the month after it; and the roll-forward's residual there,
# check_pols_roll_fwd_resid(1356), reads the counts in force at 1,357, pols_all(1357):
# 1,358, which is 12 * (omega_age_max - issue_age_min) + future_horizon_mth + 2.  A longer
# future_horizon_mth, a higher omega_age_max or a lower issue_age_min needs t raised to
# 12 * (omega_age_max - issue_age_min) + the horizon + 2.
# timing, beside t in pols_if_at: BEF_NB = 0 to AFT_DECR = 3, the codes, 4.
# kind, beside t in benefit_pp and claims: benefit_pp's DEATH = 0 to PAID_UP = 3 and
# claims' DEATH = 0 to ALL = 3, DEATH one code in both families, the codes, 4 each.  Every
# 2-D cache of a model shares one inner width, the widest, here 4 of each family: Cython's
# unpickle code converts the 2-D caches with one function, and two widths are refused by
# gcc 14 and would write past the narrower array (USLIB-SEC-PLAN.md 7.2, Record -- M15).
# So a code from 4 raises IndexError, compiled alone, and every code inside the width is
# one its cell takes.
# y, a policy year, alone in pols_if_py, pols_pu_py, pu_benefit_py and prem_cum_pp_py,
# the openings of the year the four chains are blocked by: read in the first month of
# policy year y, in cover and after t_entry(), so y runs from 2 to the policy year of the
# last month of the longest cover, 12 * (121 - 18) - 1 = 1,235, policy year 1235 // 12 + 1
# = 103: 104, which is omega_age_max - issue_age_min + 1.  A higher omega_age_max or a
# lower issue_age_min needs y raised to omega_age_max - issue_age_min + 1; the horizon
# moves no policy year.
{"spaces": {"Projection": {"cells_param_size": {
    "t": 1358, ("t", "timing"): (1358, 4), ("t", "kind"): (1358, 4), "y": 104}}}}
