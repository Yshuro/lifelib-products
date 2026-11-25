# mx2cy's spec for CI_UK_SEC: the length of each C-array cache in Projection, by the cells'
# parameters (USLIB-SEC-PLAN.md F4, section 6.1 step 6; UKLIB-SEC-PLAN.md 6.2).  A compiled
# cache raises IndexError for an argument outside [0, size), so each size covers the
# largest argument any cell is called with on a point the contract allows, in its frame
# and in the month after it, t = proj_len(), which the roll-forward reads and C4's full
# sweep evaluates every monthly cell at; plus one because the index starts at 0.  No size
# has headroom past that: each is held to its derivation by a test.  mx2cy keys a size by
# a cell's parameter names, so every cell taking t alone shares one.  The contract is two
# References: Projection.proj_len refuses a term above policy_term_max, 50 years, and Data
# refuses a point issued more than future_horizon_mth, 120 months, after the valuation
# date.  So no point a report projects outruns these sizes, and a change to either needs
# them recomputed here and the model rebuilt.  The ages bound no cache: an age indexes
# Data's pivot arrays, which Data.rate_age_min and rate_age_max size, not a cache.
#
# t, months from the valuation date.  The longest frame is the longest term,
# policy_term_max, 50 years, issued future_horizon_mth, 120 months, after the valuation
# date: 12 * 50 + 120 = 720 months, t = 0 .. 719, and 720 in the month after it; and the
# roll-forward's residual there, check_pols_roll_fwd_resid(720), reads the count carried
# into 721, pols_if_at(721, BEF_NB): 722, which is 12 * policy_term_max +
# future_horizon_mth + 2.  A longer future_horizon_mth needs t raised to
# 12 * policy_term_max + the horizon + 2.
# timing, beside t in pols_if_at: BEF_NB = 0 to AFT_DECR = 3, the codes, 4.
# kind, beside t in benefit_pp and claims: MAIN = 0 to ALL = 4, the codes, 5; benefit_pp
# takes MAIN to CHILD alone, and refuses LAPSE and ALL by its formula, ValueError("invalid
# kind"), in both engines.
# life, beside t in age, ci_rate_base, mort_rate, ci_rate and claim_rate_life: 1 or 2, the
# lives of a joint first event, 3; widened to 5, since every 2-D cache of a model shares
# one inner width, the widest, the kinds' 5: Cython's unpickle code converts the 2-D caches
# with one function, and two widths are refused by gcc 14 and would write past the
# narrower array (USLIB-SEC-PLAN.md 7.2, Record -- M15).
# life, alone in age_at_entry, rate_group, sex and smoker: 1 or 2, 3, widened to the same
# 5, so that a life of 3 or 4, which no cell asks for, inside the caches above, is inside
# these too, and is refused by the formula, ValueError("invalid life"), in both engines, as
# a life of 0 is; one past 4 raises IndexError compiled.
{"spaces": {"Projection": {"cells_param_size": {
    "t": 722, ("t", "timing"): (722, 5), ("t", "kind"): (722, 5),
    ("t", "life"): (722, 5), "life": 5}}}}
