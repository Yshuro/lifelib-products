# mx2cy's spec for Term_UK_SEC: the length of each C-array cache in Projection, by the
# cells' parameters (USLIB-SEC-PLAN.md F4, section 6.1 step 6; UKLIB-SEC-PLAN.md 6.1).  A
# compiled cache raises IndexError for an argument outside [0, size), so each size covers
# the largest argument any cell is called with on a point the contract allows, in its
# frame and in the month after it, t = proj_len(), which the roll-forward reads and C4's
# full sweep evaluates every monthly cell at; plus one because the index starts at 0.  No
# size has headroom past that: each is held to its derivation by a test.  mx2cy keys a
# size by a cell's parameter names, so every cell taking t alone shares one, and
# benefit_sched and wop_deferred_init share k's.  The contract is six References.
# Projection.proj_len refuses a term above policy_term_max, 50 years, or above
# policy_term_max_fib, 40, on the family income benefit; a life issued below
# issue_age_min, 18; and cover past expiry_age_max, 90, or expiry_age_max_fib, 70, on the
# family income benefit; and Data refuses a point issued more than future_horizon_mth,
# 120 months, after the valuation date.  So no point a report projects outruns these
# sizes, and a change to a term's maximum or to the horizon needs them recomputed here
# and the model rebuilt.  The ages bound no cache: an age indexes Data's mortality table,
# not a cache.
#
# t, months from the valuation date.  The longest frame is the longest term,
# policy_term_max, 50 years, issued future_horizon_mth, 120 months, after the valuation
# date: 12 * 50 + 120 = 720 months, t = 0 .. 719, and 720 in the month after it; and the
# roll-forward's residual there, check_pols_roll_fwd_resid(720), reads the count carried
# into 721, pols_if_at(721, BEF_NB): 722, which is 12 * policy_term_max +
# future_horizon_mth + 2.  A longer future_horizon_mth needs t raised to
# 12 * policy_term_max + the horizon + 2.
# timing, beside t in pols_if_at: BEF_NB = 0 to AFT_DECR = 3, the codes, 4.
# kind, beside t in claims: DEATH = 0 to ALL = 3, the codes, 4.
# life, beside t in age, mort_rate_base and mort_rate_life: 1 or 2, the lives of a joint
# first death, 3; widened to 4, since every 2-D cache of a model shares one inner width,
# the widest, the codes' 4: Cython's unpickle code converts the 2-D caches with one
# function, and two widths are refused by gcc 14 and would write past the narrower array
# (USLIB-SEC-PLAN.md 7.2, Record -- M15).
# life, alone in age_at_entry and mort_group: 1 or 2, 3, widened to the same 4, so that a
# life of 3, which no cell asks for, inside the caches above, is inside these too, and is
# refused by the formula, ValueError("invalid life"), in both engines, as a life of 0 is;
# one past 3 raises IndexError compiled.
# k, a policy month, beside nothing: benefit_sched reads duration_mth(t) in cover alone,
# 0 .. 12 * policy_term_max - 1 = 599 on the decreasing shape's longest term, and
# wop_deferred_init reads a lag from 1 to min(wop_defer_mths, duration_mth_init()),
# below the months of cover: 600, which is 12 * policy_term_max.
# m, the months left to the end of the term, at which fib_commute_pp reads
# annuity_certain_factor in cover: term_mths() - duration_mth(t), 1 .. 480 on the family
# income benefit's longest term, policy_term_max_fib, 40 years, 480 at its issue month:
# 481, which is 12 * policy_term_max_fib + 1.
{"spaces": {"Projection": {"cells_param_size": {
    "t": 722, ("t", "timing"): (722, 4), ("t", "kind"): (722, 4),
    ("t", "life"): (722, 4), "life": 4, "k": 600, "m": 481}}}}
