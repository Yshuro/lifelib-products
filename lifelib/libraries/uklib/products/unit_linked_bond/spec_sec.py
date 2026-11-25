# mx2cy's spec for ULB_UK_SEC: the length of each C-array cache in Projection, by the
# cells' parameters (USLIB-SEC-PLAN.md F4, section 6.1 step 6; UKLIB-SEC-PLAN.md 6.6).  A
# compiled cache raises IndexError for an argument outside [0, size), so each size covers
# the largest argument any cell is called with on a point the contract allows, in its
# frame and in the month after it, t = proj_len(), which the roll-forward reads and C4's
# full sweep evaluates every monthly cell at; plus one because the index starts at 0.  No
# size has headroom past that: each is held to its derivation by a test.  mx2cy keys a
# size by a cell's parameter names, so every cell taking t alone shares one.  The contract
# is three References and one of Data's.  Projection.proj_len refuses a bond issued below
# issue_age_min, 18, the youngest age the mortality table rates; and an omega_age, the
# limiting age every frame ends at, above omega_age_max, 121, the shipped table's last age
# plus one, the most the table admits; and Data refuses a bond issued more than
# future_horizon_mth, 120 months, after the valuation date.  So no point a report projects
# outruns these sizes, and a change to omega_age_max, issue_age_min or the horizon needs
# them recomputed here and the model rebuilt.  The fund's exhaustion only shortens a frame.
# The ages bound no cache: an age indexes Data's mortality table, not a cache.
#
# t, months from the valuation date.  The longest frame is the longest cover, a bond issued
# at issue_age_min, 18, whose fund lasts to omega_age_max, 121: 12 * (121 - 18) = 1,236
# months from issue, issued future_horizon_mth, 120 months, after the valuation date:
# 1,356 months, t = 0 .. 1,355, and 1,356 in the month after it; and the roll-forward's
# residual there, check_pols_roll_fwd_resid(1356), reads the count carried into 1,357,
# pols_if_at(1357, BEF_NB): 1,358, which is 12 * (omega_age_max - issue_age_min) +
# future_horizon_mth + 2.  A longer future_horizon_mth, a higher omega_age_max or a lower
# issue_age_min needs t raised to 12 * (omega_age_max - issue_age_min) + the horizon + 2.
# timing, beside t in pols_if_at and av_pp_at: BEF_NB = 0 to AFT_WD = 7, one numbering for
# the count's four timings and the fund's four, the codes, 8.
# kind, beside t in claims: DEATH = 0 to ALL = 2, the codes, 3; widened to 8, since every
# 2-D cache of a model shares one inner width, the widest, the timings' 8: Cython's
# unpickle code converts the 2-D caches with one function, and two widths are refused by
# gcc 14 and would write past the narrower array (USLIB-SEC-PLAN.md 7.2, Record -- M15).
# So a kind 3 to 7 is inside the cache, where the cell refuses it as modelx does,
# ValueError("invalid kind"), and a code from 8 raises IndexError, compiled alone.
# y, a policy year, alone in av_pp_py, wd_cum_pp_py and pols_if_py, the openings of the
# year the fund, the withdrawals since issue and the count are blocked by: read in the
# first month of policy year y, in cover and after t_entry(), so y runs from 2 to the
# policy year of the last month of the longest cover, 12 * (121 - 18) - 1 = 1,235, policy
# year 1235 // 12 + 1 = 103: 104, which is omega_age_max - issue_age_min + 1.  A higher
# omega_age_max or a lower issue_age_min needs y raised to omega_age_max - issue_age_min
# + 1; the horizon moves no policy year.
{"spaces": {"Projection": {"cells_param_size": {
    "t": 1358, ("t", "timing"): (1358, 8), ("t", "kind"): (1358, 8), "y": 104}}}}
