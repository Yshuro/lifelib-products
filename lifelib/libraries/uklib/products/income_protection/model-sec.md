# In-Force Implementation Notes

**Status:** Draft, 2026-11-23. `IP_UK_SEC` is [`IP_UK_S`](model.md) taught to project from
a valuation date. Besides policies issued at that date, it takes policies already in force
there, in any month of their policy year, with lives in health and lives in claim at any
claim duration, and policies to be written in the ten years after it, as lifelib's
`basiclife/BasicTerm_SE` extends `basiclife/BasicTerm_S`. The product is the one
[`product-spec.md`](product-spec.md) specifies and [`technical-notes.md`](technical-notes.md)
models; this page says what running in force changes. The suffix adds lifelib's letters to
`S`: `E` for in force, as in `BasicTerm_SE`, and `C` for the compiled form, as in
`basiclife/BasicTerm_SC`, which the model's next step adds (UKLIB-SEC-PLAN.md U2). Until
then it runs in modelx alone.

> **This is a mechanics demonstration, not a pricing or reserving result.** The model is
> `IP_UK_S` on another time axis, and it reads `IP_UK_S`'s assumption tables in place,
> every assumption unchanged: the contractual mechanics are sourced, and every rate is a
> **[std]** standardization, the inception and termination bases proxies shaped like the
> CMI IP11 Series, whose values are restricted to the CMI's Authorised Users, the
> mortality a proxy shaped like the ONS national life tables, and the lapse table a
> placeholder no public study anchors. Replace them with licensed tables and company
> experience before drawing any conclusion from the numbers.

## Run it

```bash
python products/income_protection/run_sec.py            # point 1: the anchor cell, issued at t = 0
python products/income_protection/run_sec.py 9          # point 9: the anchor cell in force 60 months
python products/income_protection/run_sec.py --block    # every model point, summed row by row
```

The first prints the twelve rows `run.py` prints for `IP_UK_S`'s point 1, with the policy
counts behind them. Three lines to the same thing for point 9:

```python
import modelx as mx
model = mx.read_model("products/income_protection/IP_UK_SEC")
model.Projection[9].result_cf()
```

`Projection` takes a `point_id`, as `IP_UK_S`'s does; it will take `idx`, a point's
position in the table, once the model compiles, and the runner takes its key from the
model either way. `result_cf()` has `IP_UK_S`'s columns — `pols_if`, `pols_active`,
`pols_sick`, `premiums`, `claims_benefit`, `claims_death`, `claims_lapse`, `expenses` and
`net_cf` — with one row per month from the valuation date, `t = 0 … proj_len() − 1`, and
`result_states()` `IP_UK_S`'s ten columns of the states, their transitions and the annual
rates. `result_pols()`, new, sets out the counts behind them on the same rows: `pols_if`,
`pols_new_biz`, the healthy and the sick counts, then the month's movements in the
notes' processing order, out of health the deaths, the lapses and the inceptions, out of
claim the recoveries and the deaths, the recoveries that leave the model and the expiry;
then the benefit and the premium per policy.

`--block` projects every point and releases its ItemSpace once its frame is read, so the
run holds the cells of one point at a time. Deleting it, `del model.Projection[9]`, is not
enough: an ItemSpace sits in reference cycles, which only Python's cyclic collector frees,
so the runner collects after each release. It freezes everything alive (`gc.freeze()`)
once the model and its table are read, and again once it has asked every point for its
frame, so that each collection scans only what the block has made since. It keeps the
block's sum as it goes, compensated as pandas sums a `groupby`, so that the block is, bit
for bit, the frames concatenated and summed by `t`. Its projection years carry the counts
of their first month, in force, healthy and in claim, and the flows of all twelve.

The runner is uslib Term's, so it already takes `--cython`, which runs the compiled model
in place of modelx, building it first with the repository's `tools/build_sec_cy.py`, and
`--build DIR`, which runs a build made elsewhere. The model compiles from its next step
on, which brings the build's `sample_sec.py` and `spec_sec.py`; until then a build stops,
saying why. A `lifelib.create()` copy carries no `tools/`, and there `--cython` stops
before building, saying so.

## Two clocks

The model runs on two clocks, and each formula reads the one its quantity belongs to; the
claim clock, `z`, is a third, which only the termination rates read.

- **`t`, the valuation clock**, counts months from the valuation date. `t = 0` is the
  valuation month for every model point, however old the policy, and the frame runs
  `t = 0 … proj_len() − 1`, where `proj_len()` is the number of months from the valuation
  date to the policy end date.
- **`duration_mth(t)`, the policy clock**, counts the months the policy has been in force
  at time `t`: `duration_mth(t) = duration_mth_init() + t`, with `duration_mth_init()` read
  from the model point. The contract runs on it: `duration(t) = duration_mth(t) // 12`,
  `policy_year(t) = duration(t) + 1`, the lapse table's key and the escalation's, and
  `age(t) = age_at_entry() + duration(t)`, the inception and mortality tables', as in
  `IP_UK_S`. Cover ends at the policy end date, policy month
  `expiry_mth() = 12 × (expiry_age − entry_age)`, `IP_UK_S`'s frame from issue.
  `BasicTerm_SE` reaches the same numbers by adding one a month, a recursion as long as the
  frame; the closed form needs no such chain of calls.
- **`z`, the claim clock**, counts the months a claim has run: the lives in claim at the
  start of month `t` are held by claim duration, cohort `z = 1` the claims that incepted at
  the end of month `t − 1`, not yet paid. `claim_dur_year(z)` keys the termination table.
  It is `IP_UK_S`'s, unchanged.

Point 9 is the anchor cell in force 60 months, its fifth anniversary falling at the
valuation date. At `t = 0` it is in policy year 6 at attained age 40, 0.683305 of its
policy in force, 0.680544 healthy and 0.002761 in claim, and its frame has 300 rows,
`t = 0 … 299`; `IP_UK_S` projects the same months as its rows 60 to 359. Point 17 is the
female cell to be issued 13 months after the valuation date: `duration_mth(0) = −13`, it is
on the books from `t_entry() = 13`, rows 0 to 12 are zeros, and its frame has 229 rows.

| Read on the policy clock | Read on the valuation clock |
|---|---|
| the inception and mortality tables at the attained age; the lapse table by policy year; the escalation of the benefit and premium on each policy anniversary, and the lapse shock from policy year 2; the policy end date | expense inflation, `inflation_factor(t) = 1.03^(t // 12)`; discounting, `disc_factor(t) = 1.03^(−(t + 1) / 12)` |

Expense inflation runs on `t`, stepping on each anniversary of the valuation date, for
every point alike (USLIB-SEC-PLAN.md D7): the maintenance and claim-management loads are
then in valuation-date pounds. `IP_UK_S` inflates from issue, `1.03^(y − 1)`, which on a
point in force would inflate a load stated today by the years the policy has already run;
on its `in_claim` cells, which it opens at the valuation date, the two are one.
Discounting was already on `t`, to the start of `IP_UK_S`'s frame, the valuation date on
every point here. The RPI is a flat Reference, the rate assumed from the valuation date on,
and `cycle_factor` a scenario overlay on inception and recovery from it. Neither model
charges an acquisition expense or a commission.

Because row `t` is the same month for every point, the frames of a block line up and sum
row by row, which is what `run_sec.py --block` prints:

```python
import pandas as pd
frames = [model.Projection[p].result_cf() for p in model.Data.model_point_table().index]
block = pd.concat(frames).groupby(level="t").sum()
```

On a point issued at `t = 0` the two clocks coincide, and the model computes what
`IP_UK_S` computes: every cell the two models share agrees, but two whose meaning changed,
`pols_if_init()`, now the count already in force at the valuation date, 0 for new
business, and `model_point()`, a row of another table.

## The in-force interface

The model point table is `model_point_table_sec.csv`. It carries `IP_UK_S`'s columns, one
of them restated as the in-force interface under `basiclife/BasicTerm_SE`'s name, a policy
clock column and three columns of opening state, and beside it a companion,
`inforce_cohorts_sec.csv`, which holds the lives in claim by claim duration. The count is
the only weight on the flows, and every state is per policy, a share of the count or an
amount. Each is measured at the valuation instant, the start of month 0, before any
month-0 event, recoveries of month −1 already returned to health (USLIB-SEC-PLAN.md D6;
UKLIB-SEC-PLAN.md §6.3). An anniversary that falls at the valuation date is month 0's
event, the projection's first: the benefit and premium columns hold the policy year it
closes, and its increase is made at `t = 0` at today's References, as a fixing at month 0
reads the assumptions of the valuation date (D6, as precised at uslib's M7). Each state is
history, what the contract has given and what the lives have done, never re-derived from
a Reference, which is an assumption from the valuation date on (UKLIB-SEC-PLAN.md K14):

| Column | Unit | Meaning |
|---|---|---|
| `policy_count` | policies, not necessarily whole | the policies in force at the valuation date, healthy and in claim together, for a point already in force; the policies issued, for one issued at or after it |
| `duration_mth` | whole months | the policy's age in months: positive in force, 0 for a policy issued at the valuation date, `−k` for one to be issued `k` months later, with `k` at most `Data.future_horizon_mth`, 120 as shipped |
| `pols_active_init` | a share of the count, 0 to 1 | the lives in health, those sick but still inside the deferred period among them, and the recoveries of month −1 back in health; 1 on a point not yet in force, which is issued healthy |
| `benefit_pp_init` | pounds a month | the benefit entering month 0, `IP_UK_S`'s `benefit_pp(d − 1)`: the policy year of month −1, after every increase the RPI has given; the benefit at issue on a point not yet in force, and in its first policy year |
| `premium_pp_init` | pounds a month | the premium entering month 0, as `benefit_pp_init` |

| `inforce_cohorts_sec.csv` | | |
|---|---|---|
| `point_id`, `z` | whole numbers, the key | a point in force and a claim duration at which it holds lives in claim, 1 to its `duration_mth` |
| `pols_sick_dur_init` | a share of the count, 0 to 1 | the lives in claim at claim duration `z`, `IP_UK_S`'s `sick_cohorts(d)` element `z − 1` over its `pols_if(d)` |

The companion is sparse: a claim duration a point holds no row for holds no lives, so a
point all healthy holds no row, and a claims extract one row per claim in payment. The
anchor cell at its month 359 holds 359 cohorts, one for each month's inceptions still in
claim; under the contract's bounds a cohort vector runs to 624. The rejected shapes were
624 columns, and one model point per state, exact since the model is linear but a
projection per cohort.

`IP_UK_S` holds none of the state. Its `status` column says whether a point is in health
or in claim, and an `in_claim` point puts its whole count into cohort
`claim_duration_months + 1`, with its policy clock restarted at the valuation date and its
`entry_age` the attained age there: a healthy policy months after issue cannot be
represented, and it rebuilds the benefit and premium from issue at today's flat
`rpi_rate`. Here:

- `pols_active(t)` opens at `t_entry()` at `policy_count × pols_active_init` plus the
  month's new business, which enters healthy, and `sick_cohorts(t)` at `policy_count ×
  pols_sick_dur_init(z)` for each `z`; from there each runs `IP_UK_S`'s recursion, one cell
  a month;
- `benefit_pp(t)` and `premium_pp(t)` open at `benefit_pp_init()` and `premium_pp_init()`
  and take `1 + j` and `1 + 1.5 j` for each anniversary since the columns' year,
  `duration(t) − duration_init()`, `duration_init()` being the policy years of month −1, so
  that an anniversary at the valuation date steps them at `t = 0`. The benefit escalates
  for everyone in health and in claim alike, so no cohort carries an amount of its own.

`status` stays, a label no formula reads, which an extract may leave out, and
`claim_duration_months` is gone, the companion its successor. On a point issued at the
valuation date each state holds its
issue value, and the model is `IP_UK_S`. A model that dropped the columns and recomputed
them from the References and the status would pass the splice, since `IP_UK_S` and the
splice recompute them alike, so the tests write each off that path and project through
it.

### What `Data` refuses

`Data.model_point_table()` checks the table as it reads it, the first rule that fails
raising `ValueError` and naming the missing column or every point it fails on, by its
`point_id`: the five in-force columns present, and the eleven of `IP_UK_S`'s the projection
reads, `status`, a label, not among them; no `point_id` twice; a count that is a number, 0
or more; a `duration_mth` that is a whole number below `2**53` and no further from the
valuation date than the horizon, itself a whole number 0 or more below `2**53`; a healthy
share from 0 to 1 and amounts 0 or more; the codes `IP_UK_S` branches on, `status`'s where
the table has it, and a `premium_basis` of `guaranteed`, the one the model prices, which
`IP_UK_S` checks in a cell no formula calls; an occupation class from 1 to 4 and a
deferred period of 4, 8, 13, 26 or 52 weeks; finite ages below `2**53`; and the history
from below: a policy not yet in force all healthy and at its issue amounts, a policy in
force 12 months or fewer at its issue amounts, a level policy at them always, and an
escalating policy at them or above, to half a cent, each increase floored at 0. The
history's upper bounds read References, so `proj_len()` holds them. Rule 12 refuses one
state `IP_UK_S` cannot reach either: a policy whose escalation option has lapsed after
increases refused, its benefit above its benefit at issue and its escalation `none`. The
model cannot represent a lapsed option, which would keep the increases already given and
take no more, so such a policy is not one it projects.

`Data.inforce_cohorts()` checks the companion by eight rules, naming the lines, the header
line 1: the three columns; keys whole and below `2**53`; a point of the table; one row a
point and duration; a point in force, `duration_mth` above 0, since a point not yet in
force is issued healthy; a duration from 1 to the point's `duration_mth`, since a claim
incepts at the end of a month the policy is in force; a share from 0 to 1; and on every
point in force the healthy share and the cohort shares summing to 1 within 1e-10, the
tolerance `check_states` holds the population identity to.

Each assumption table is checked before a value of it is read, in the cell the projection
first asks of it: `Data.inception_table()` itself, and `Data.termination_last_year()`,
`Data.mort_age_first()` and `Data.lapse_last_year()`, which give the extents
`IP_UK_S`'s lookups took from the table. Each key is a whole number below `2**53`; the
termination and lapse years run from 1 without a gap or a repeat, each sex of the
mortality table over the table's ages, and each of the forty inception schedules holds two
pivot ages or more; and every rate is a number from 0 to 1. A fault is named by its lines.

### What `proj_len()` refuses

Whether a point is still in cover and whether the contract issues it are rules of the
product, not of the table, so the frame applies them, naming the point: a point at or past
its policy end date at the valuation date; an issue age outside `issue_age_min` to
`issue_age_max`, 18 to 59, or an expiry age outside `expiry_age_min` to `expiry_age_max`,
50 to 70, the bounds the compiled caches will be sized from; and an issue age at or past
the expiry age. So is an escalation history the contract cannot have, after the
anniversaries before the valuation date: a benefit above the benefit at issue increased by
`esc_cap` at each, a premium above the premium at issue increased by `esc_prem_mult` times
`esc_cap` at each, or a premium outside the range its benefit's increases allow, each
increase `j` of the benefit's raising the premium by `esc_prem_mult × j`, least when the
benefit's increases fell at the cap, one part-way and the rest none, most when they were
equal. Each holds to half a cent, the benefit's own half cent carried into the premium's
range, for an extract rounded to the cent; a level point, at its amounts at issue, meets
them, and so does every state `IP_UK_S` reaches. And each Reference off its domain, NaN
and both infinities outside every one:

| Reference | Domain | Off it |
|---|---|---|
| `cycle_factor` | a finite number above 0 | 0 divides the recovery rate by zero; below 0.4 `IP_UK_S`'s in-claim survival is silently 0 |
| `mort_active_factor`, `esc_cap`, `esc_prem_mult`, `esc_lapse_slope`, `esc_lapse_threshold`, `ben_breakpoint`, `ben_cap_mth`, `ben_guarantee_mth`, `expense_maint`, `expense_claim` | a finite number, 0 or more | a negative rate, step or load; a NaN threshold is lost through the shock's `max`, a NaN cap through the escalation's `min` |
| `ap_ratio`, `claim_severity`, `ben_band1_rate`, `ben_band2_rate` | a number from 0 to 1 | a benefit paid above its amount, or of the wrong sign |
| `ben_tolerance` | a number above 0, at most 1 | a maximum-benefit check that passes or fails every point |
| `rpi_rate` | a finite number | the escalation reads an infinity as no increase or as the cap |
| `inflation_rate` | a finite number, −1 or more | a factor that changes sign each year |
| `disc_rate` | a finite number above −1 | −1 divides by zero |
| `issue_age_min`, `issue_age_max`, `expiry_age_min`, `expiry_age_max` | a whole number below `2**53`; the minimum issue age 0 or more, each maximum its minimum or more, and the latest expiry at most a year past the mortality table's last age | a NaN bound refuses nothing and an infinite one bounds nothing, where the compiled caches will be sized from them; past the table the frame reads an age it lacks |

At each edge of its domain a Reference projects its reports in finite floats, but where
the edge takes a value past the floats: an escalation, a load, a count or a rate each in
its domain can, and the cell where such a value first is refuses it, naming the point,
the month and what makes it, where `IP_UK_S` would carry an infinity into every report and
pass its checks. A power that would pass the largest float, the benefit's and premium's
steps, the inflation factor and the discount factor, is refused by name where Python's
power raises `OverflowError`, naming neither.

## The model points

No row of `model_point_table_sec.csv` or `inforce_cohorts_sec.csv` is typed by hand. Every
one is generated from `IP_UK_S` and its table by `tests/uk_sec_support.py`, from the
`IP_UK_SEC` entry in its `SEC_SPECS`, and the tests regenerate them and compare, so an edit
to an `IP_UK_S` row reaches them or fails the suite. In the source repository,
`python tools/gen_sec_points.py IP_UK_SEC` writes them.

| Point | Kind | From | At the valuation date |
|---|---|---|---|
| 1, 3, 4, 6 | twin | S points 1, 3, 4, 6 | issued at `t = 0`: the active-lives anchor cell, its level-cover variant, the female cell and the older male cell |
| 2, 5, 7 | twin | S points 2, 5, 7 | in claim, on policy clocks of whole years since issue: the claims-in-payment worked example, issued at 34 and in force 12 months, its claim at duration 1; the claim at duration 30, issued at 47 and in force 36 months; and the worked example's claim on the active-lives basis, as point 2 |
| 8 | derived | S point 1 at S month 12 | the anchor cell on its first anniversary, at its first year's amounts, its first escalation at `t = 0` |
| 9 | derived | S point 1 at S month 60 | the anchor cell in policy year 6, the lapse table's last, at attained age 40, an inception pivot |
| 10 | derived | S point 1 at S month 359 | the anchor cell in its last month, 359 cohorts in claim |
| 11 | derived | S point 2 at S month 24 | the claims-in-payment cell at claim duration 25, in claim year 3 |
| 12 | derived | S point 5 at S month 6 | the claim at claim duration 37, in claim year 4 |
| 13 | derived | S point 7 at S month 12 | the claim on the active-lives basis, 0.391343 of its count recovered and healthy, some of it claiming again |
| 14 | derived | S point 4 at S month 13 | the female cell a month past its first anniversary, at £1,545 and £60.61 |
| 15 | derived | S point 6 at S month 118 | the older male cell in its last two months |
| 16 | derived | S point 3 at S month 30 | the level cell mid-year |
| 17 | future | S point 4, 13 months on | to be issued at `t = 13` |
| 18 | derived | S point 1 at S month 40, `IP_UK_S` run under an RPI of 5% | the anchor cell at `2,000 × 1.05^3` and `35 × 1.075^3`, its lapses shocked by 1.05 since policy year 2 |
| 19 | derived | S point 4 at S month 30, `IP_UK_S` run under an RPI of 12% | the female cell at the cap's `1,500 × 1.1^2` and `58 × 1.15^2` |

A derived row's `policy_count` is the count `IP_UK_S` carries into that month, its
`pols_if(d)`, and its state and cohorts what S carries there, so the row continues the S
projection from there. Where S carries no policy into the month, as on a claim on the exit
basis whose every life has recovered, which the recovery bound's splice set reaches, the
generator writes a point of no policies, all healthy, its share 1 and no cohort, which
projects nothing, as S does; no committed row is one. At the shipped 3% no state holds a
lapse shocked by escalation, nor
an increase capped, so two rows are read from `IP_UK_S` run under an RPI of their own,
which the spec's `derived_refs` records, their cohorts read under it too: points 18 and
19. At the shipped References they step at today's 3% from their next anniversary, and a
test asserts each. A derived row's `policy_id` is the S row's with the month appended,
`IP-000001-M60`, and a future row's carries the months to issue, `IP-000004-F13`. Row `t`
of a generated point is month `t + source_mth` of its S point.

**The in-claim twins.** `IP_UK_S` opens its three `in_claim` points in claim at the
valuation date with their policy clock restarted there, so they have no policy clock to
copy (UKLIB-SEC-PLAN.md D8): S's row records no issue date. Each twin is given one, issued
`n` whole years before, the least whole number of years that holds the claim,
`n = ⌈(z0 + 1) / 12⌉` for a claim at duration `z0`, with `duration_mth = 12n` and issue
age `entry_age − n`: its anniversaries are then S's, a year apart, its attained ages S's,
and its claim cohort S's. That clock is the generator's choice, not the policy's: a claim
at duration 0 after a 26-week deferral fits a policy anywhere from 7 to 11 months old.
Points 2 and 5 then match S in every count, cash flow and check, since their healthy state
is empty and only the clock cells differ. On point 7 the recovered lives return to health
and lapse there, and the twin's clock runs a year ahead of S's restarted one: in each year
S lapses them at a policy year's rate, 10% in its first, where the twin lapses them at the
next year's, 8% in its second, so that 60 months on 0.8002 of the twin is in force against
`IP_UK_S`'s 0.7791. Neither is the policy's own clock, which S's row does not record; the
difference is the clock each model gives the claim, S's restarted one recorded below. So
the tests compare point 7 and its rows under a flat lapse table, on which the two clocks
lapse alike, and under which the twin equals S in every cell. An `in_claim` point with RPI
escalation has no twin: valued on an anniversary, it would escalate at `t = 0`, where
`IP_UK_S` takes no step, and the generator refuses it, naming the point. No shipped point
is one.

## Counts and timings

`pols_if_init()` is the count in force at the valuation date: `policy_count` for a point
already in force, 0 for any other. `pols_new_biz(t)` is `policy_count` in the issue month,
the month with `duration_mth(t) = 0`, and 0 in every other; every policy issued starts in
health. `pols_if(t)` is `pols_active(t) + pols_sick(t)`, the count weighting month `t`,
healthy and in claim, D5's row weight with no exception. `pols_if_at(t, timing)` keeps
`IP_UK_S`'s two timings and adds `basiclife/BasicTerm_SE`'s `"BEF_NB"`:

- `"BEF_NB"`, the count carried in from month `t − 1`, before month `t`'s new business:
  `pols_if(t)` less `pols_new_biz(t)`, exactly, since new business arrives only on an
  empty book;
- `"BEF_DECR"`, the count before month `t`'s decrements, `pols_if(t)`;
- `"AFT_DECR"`, the count after them: `"BEF_NB"` at `t + 1`, which counts none of that
  month's new business, and 0 in the last covered month and outside cover.

Any other timing raises. The roll-forward check reads the same `"BEF_NB"`, so it never
counts the next month's new business. The three cumulative counts, of deaths, lapses and
recoveries leaving the model, which only the population identity reads, restart at
`t_entry()`, the identity restated on the count on the books; `IP_UK_S`'s count from its
frame's start, and the splice compares their increments. Both checks scale their
tolerance with `policy_count()`, the policies on the books, which `IP_UK_S`'s
`pols_if_init()` is not here on a point issued at or after the valuation date.

`pv_benefits()` discounts the benefit outgo to the valuation date, and `annuity_dis()` is
it over the amount payable at `t_entry()` times `policy_count()`, per policy on the books;
`IP_UK_S` divides by `amount_payable_pp(0)` alone, the same number on its points, each of
one policy. On a point in claim on the exit basis the factor is the notes' `a_dis(a0, z0)`:
49.783 per £1 a month on the worked example's twin, as in `IP_UK_S`.

The caps are `IP_UK_S`'s since M0: active-life mortality, in-claim mortality and inception
`min(q, 1.0)`, the bound second, so that a NaN stays NaN; recovery and lapse
`min(1.0, w)`, the bound first, `IP_UK_S`'s order, which no NaN reaches, `Data` and
`proj_len()` holding every rate and Reference they read to a number. At the shipped
References none binds. The tests bind four: mortality at a factor of 100, inception at an
overlay of 50, the lapse rate at an RPI of 12% under a shock slope of 300 and the recovery
rate at an overlay of 0.35, which every splice under it crosses. The in-claim mortality's
cap no test binds, and none can: `Data` holds the termination table's rates to 0 to 1 and
no factor multiplies them, so the cap meets only a rate of 1 at most; a test holds its
order, a NaN rate staying NaN through it. The inception rate's floor at 0 binds on no
shipped schedule, each, one shape scaled, extrapolating to 0 only below age 13.3, under
the youngest issue age; but `Data` accepts a schedule that falls below 0 above it, and a
test splices one, a copy of the inception table whose schedule for variant 9, issued at
22, reads 0 until 30, where `IP_UK_S` and this model floor it alike.

## Departures from IP_UK_S

Each formula that tested `t` against a contractual event now tests the policy clock, and
each recursion opens at `t_entry()` from the opening state. Twelve cells are new —
`policy_count`, `duration_mth_init`, `duration_init`, `t_entry`, `is_active`,
`expiry_mth`, `pols_new_biz`, `result_pols` and the four accessors of the opening state,
`pols_active_init`, `pols_sick_dur_init`, `benefit_pp_init` and `premium_pp_init` — and
one of `IP_UK_S`'s 73 is gone, `claim_duration_months`, which the claim cohorts replace.
Four References are new, the contract's bounds `issue_age_min`, `issue_age_max`,
`expiry_age_min` and `expiry_age_max`, and in `Data` the future horizon; `Data` gains the
companion's reader and the four tables' checks, three of the readers reading their file
once through a `*_rows` cell that the check and the indexed reader share.

| Cells | `IP_UK_S` | `IP_UK_SEC` | Why |
|---|---|---|---|
| `duration_mth`, `duration` | `t`, `t // 12` | `duration_mth_init() + t`, `duration_mth(t) // 12` | The policy clock, opened from the model point |
| `proj_len`; `expiry_mth`, new | `12 × (expiry_age − entry_age)`, from issue | `expiry_mth() − duration_mth_init()`, from the valuation date; raises at or past the policy end date, outside the contract's bounds, on an escalation history past them and on a Reference off its domain | The frame starts at the valuation date |
| `pols_active`, `sick_cohorts` | from `pols_if_init()` on an `active` cell, into cohort `claim_duration_months + 1` on an `in_claim` one | from `policy_count` split by the healthy share and the companion's cohort shares at `t_entry()`, new business healthy | Lives in health and in claim at once, at every claim duration, are history |
| `max_dur` | `proj_len() + claim_duration_months() + 1` | `expiry_mth() + 1`, the cover from issue and a cohort of headroom | A claim is no older than its policy; on a future row the horizon would size `z` |
| `pols_if`, `pols_if_at`, `pols_if_init` | `pols_if_at(t + 1)` read for the roll-forward; `pols_if_init()` the column | `"BEF_NB"` added, `pols_if(t) − pols_new_biz(t)`; the roll-forward and `"AFT_DECR"` read it at `t + 1`; `pols_if_init()` 0 unless in force | Next month's new business is not this month's survivors |
| `benefit_pp`, `premium_pp`; `duration_init`, new | the amounts at issue times `(1 + j)^(t // 12)` | `benefit_pp_init()` and `premium_pp_init()` times the step for each anniversary since the columns' year, an anniversary at the valuation date the first; a value past the floats refused in its month | The increases already given are history, and one at month 0 is the projection's, at today's References |
| `premiums`, `claims`, `expenses`, `net_cf`, `pv_benefits`, `esc_lapse_factor` | unchecked | a value past the floats refused in its month, naming the point and what makes it | An infinite flow would pass every check |
| `inflation_factor` | `1.03^(y − 1)`, from issue | `1.03^(t // 12)`, from the valuation date; past the floats refused | Unit costs in valuation-date pounds |
| `disc_factor` | `1.03^(−(t + 1) / 12)` | the same, on the valuation clock; past the floats refused | Values at the valuation date |
| `annuity_dis` | `pv_benefits() / amount_payable_pp(0)` | over `amount_payable_pp(t_entry()) × policy_count()`, refused where that is 0 | Per policy on the books, at the month the point is first on them |
| `pols_dead_cum`, `pols_lapse_cum`, `pols_exit_cum` | from the frame's start | from `t_entry()` | The identity restated on the count on the books |
| `check_pols_roll_fwd`, `check_states`, `check_states_resid` | tolerance `1e-10 × max(pols_if_init(), 1)`; the identity on `pols_if_init()` | tolerance on `policy_count()`; the identity on `policy_count()` in cover and 0 outside it | `pols_if_init()` is 0 on new business |
| `inception_rate`, `mort_rate`, `lapse_rate_base`, `lapse_rate` | evaluated before issue by `result_states()`, the lapse lookup raising there | 0.0 outside cover, without a read | No table read at a policy year or an age the policy does not have |
| `result_pols`, new | — | the counts and amounts behind the reports, row by row | D5's report |
| `status`, `premium_basis` | branched on; checked by a cell no formula calls | a label no formula reads, which an extract may leave out; refused by `Data` unless `guaranteed` | The shares are read, not decided by status; a reviewable premium is not priced |

Every cell outside cover holds 0, False or a vector of zeros, as its docstring says, and
reads no rate: no count evaluates a rate before issue or from the policy end date. The
generator, not the model, departs once more: a month at which `IP_UK_S` carries no policy
is written as a point of no policies, all healthy, where S's shares are 0 over 0.

**Defects of `IP_UK_S`** found in this work, which `IP_UK_SEC` does not share or, for the
first, compares around:

- an `in_claim` cell's policy clock restarts at the valuation date, its row recording no
  issue date, so point 7's recovered lives lapse at first-year rates in the year after
  it, whatever the policy's age: 0.7791 in force at month 60, against 0.8002 on its twin,
  whose clock, the least whole year that holds the claim, runs a year ahead;
- `premium_basis()` has no caller, so its check never runs, and a point set to
  `reviewable` projects as guaranteed;
- `annuity_dis()` divides by the amount payable alone, so on a point of more than one
  policy the factor is not per policy;
- a blank, text or infinite rate in any assumption table is read as NaN or infinity, which
  the caps keep and every flow carries, and a gapped or repeated key raises `KeyError`
  only where a projection reaches it, or reads a wrong row;
- the docstrings say restoring the age dimension to the termination basis touches only
  the lookups, but the cohort shift assumes the rates depend on `z` alone; and
  `claim_rate_vectors` recomputes the in-claim survival beside `claim_surv_step`, which
  only the tests read.

## Tests

- **The twin identity**, in `tests/test_model_conventions_uk.py`: on points 1, 3, 4 and 6,
  every cell of `IP_UK_S`'s agrees at every argument `IP_UK_S` evaluates in its own sweep,
  to 1e-9 relative with no absolute floor, but for `pols_if_init`, `model_point` and
  `claim_duration_months`, which the spec names with their reasons. So `IP_UK_S`'s worked
  example, which `tests/test_income_protection_uk.py` asserts, holds here with no number
  restated. The same suite holds the model to the conventions every `_SEC` model meets:
  every frame starts at `t = 0`, `pols_if` is the `"BEF_DECR"` count, new business enters
  once at its `policy_count`, nothing happens before issue, and the in-force columns are
  present.
- **The splice**, in `tests/test_income_protection_uk_sec.py`: each `IP_UK_S` point
  restated in force at months about its events — the anniversaries, 11 to 13; the lapse
  table's last year, 59 to 61; the inception table's pivot ages; the claim-duration years
  of the two claims on the exit basis; the first month and the last two — and the twins of
  S's claims on their policy clocks, continue the S projection in both reports and in every
  cell the two share, the cohort vector element by element among them, to 1e-9 relative
  with no absolute floor, the residuals at 1e-9. Four kinds of cell are compared otherwise:
  `proj_len`, which counts from the valuation date, by the frames ending together; the
  cumulative counts, which restart on the books, by their increments; away from month 0
  the discount factor, the present value and the annuity factor, which discount to each
  model's own start, by a test of their own; and on a row of one of S's claims the clock
  and cohort cells, by checks that its policy clock is S's plus `12n`, its issue age S's
  less `n`, and its cohort vector S's, with zeros past S's length. Every assumption that ships
  idle is on: the escalation lapse shock at an RPI of 5%, beside the cycle overlay at 1.25,
  the active-life mortality factor at 1.1, the amount-payable ratio at 0.9 and the claim
  severity at 0.95; and three more sets reach the escalation cap at 12%, the RPI's floor at
  −2% and the recovery rate's bound at an overlay of 0.35. Expense inflation, the one input
  on the valuation clock, is 0 in both. Three variants of S's points, in a copy of S's
  table that is never committed, reach an active cell on the exit basis, the youngest
  attained ages below the inception table's first pivot, and the oldest entry to the latest
  expiry, past its last. A core of 25 of the 95 splice cases and 5 of the 18 future ones
  runs by default, and the full grid with `UKLIB_SEC_FULL=1`; a test asserts the core
  reaches every branch, opening-state column, month-0 event and side of every `min` and
  `max` the full grid reaches. Point 7 and its rows are spliced under a flat lapse table,
  and their difference at the shipped table asserted, the twin's clock a year ahead of
  S's restarted one; and the inception rate's floor is spliced on a copy of the inception
  table with a schedule below 0, which no shipped schedule reaches.
- **Future new business**: issued 1, 12 and 120 months after the valuation date, each S
  point is the S projection moved on, with zeros before issue and no table read there, and
  so is each variant issued 13 months on.
- **How it computes**: on every row of the splice's grid, after its reports, its checks
  and every monthly cell at every month, no cell has been called at a negative month, none
  on the books read a month before `t_entry()`, none read a month later than `t + 1`, and
  none raised. On a fresh read of the committed model, `duration_mth(500)` evaluates
  `duration_mth` once, and every point's reports and checks run under modelx's recursion
  limit lowered to 40. And each chain, called cold in the last month at the contract's
  longest cover, 624 months, on four shapes, runs one cell a month back to `t_entry()` and
  at most 16 more: measured, a cold `net_cf` runs 8 or 9 more, 631 to 632 deep, and the
  other heads 5 to 8.
- **Counts**: the counts roll forward through the states; `result_pols()` is S's counts and
  amounts with `pols_new_biz` beside them; multiplying `policy_count` by 2.5, with every
  idle assumption on, multiplies every flow and counted cell, each cohort element among
  them, each nonzero on some point, and moves no per-policy value, bit for bit, but the
  annuity factor, the present value over the count, a ratio of two scaled sums, which
  agrees to 1e-12; a point restated a month on continues its own flows; and both checks
  close on ten million policies.
- **Validation and regeneration**: each malformed row of the table, 75 cases, a missing
  column among them, and of the companion, 23, is refused naming its point or its lines,
  and naming its label on an extract labelled otherwise, table and companion alike; the
  horizon is a Reference; a point past its policy end date is refused by `proj_len()`,
  and `run_sec.py --block` refuses it before printing anything; so is a point outside the
  contract's bounds, 9 cases; so is an escalation history past them, each bound a cent
  outside and accepted half a cent inside, beside two histories the contract cannot have
  and the committed history under a contract it was not written under, 11 cases; each of
  23 References off its domain, the value next outside each edge, NaN and both
  infinities, where each edge is accepted; a value past the floats, 11 cases, where it
  first is; each assumption table with one fault, 42 cases, before a value of it is read;
  the edges of the interface, the shares' tolerance pinned from both sides and an
  escalated amount half a cent below its issue value among them; and every state `IP_UK_S`
  reaches, under the shipped References and four sets more, at the edges of each frame's
  windows, or at every month with the full grid. The committed CSVs are what the generator
  makes of `IP_UK_S` today.
- **The product's own facts**: the two clocks; the present value and the annuity factor
  on the valuation clock; the committed rows continuing their S points, the two read
  under an RPI of their own continuing S under it; each history column read rather than
  rebuilt, the healthy share, the claim cohorts, the benefit and the premium; an
  anniversary at the valuation date as the projection's first event; the cumulative counts
  restarting on the books; expense inflation on the valuation clock; the RPI's floor, cap
  and lapse shock; the caps on mortality and inception and the lapse rate's bound, in both
  models; a NaN that reaches a cap; a check whose residual is NaN; the values outside
  cover; the block; an in-force extract, without the generator's columns or `status`; the
  runner; the static check the C step will make; the docstrings; and the shared tables.
  The K14 tests open the anchor cell in force at 60 with histories the contract can have:
  the benefit and premium `IP_UK_S` gives it under an RPI of 5%, valued under today's 3%.
- **The fingerprint (C2)**: every committed point's `result_cf()` and `result_pols()`,
  frozen when this step ended, in a commit of its own, which every later version must
  reproduce to 1e-12.

The default run takes three to five minutes, by the machine's load: about 190 seconds
alone, at a peak of 1.4 GB, and 291 seconds measured at a load of 4 to 5.

## Carried into the C step (M8)

The cohort vector and its rates are tuples here, `IP_UK_S`'s: `sick_cohorts(t)`, one a
month, and `claim_rate_vectors()`, with five cells reading them: `pols_sick`, their sum,
`pols_sick_dur`, an element, and `pols_sick_surv`, `pols_recovery` and `pols_death_sick`,
the month's flows out of them. The C step restructures them into `pols_sick_dur(t, z)`,
based at `t_entry()` on a `[point, z]` array of the companion, with the sums in `z` order
(UKLIB-SEC-PLAN.md §6.3, *C — the restructure*). The static check in
`tests/test_income_protection_uk_sec.py` names every cell the C step must change, flagging
besides a Python object or a text each cell that calls a tuple cell or reads a text
column, and nothing this step wrote adds to `IP_UK_S`'s but the companion's reader and
`result_pols`: the seven decodes, `sex`, which returns a text, among them, and the five
cells that compare a decoded column with its text; the readers of the four tables and of
the companion; the tuples and the five cells that read them; the claims total and the
present value. The inception table's array read must keep the rate's floor at 0, which the
floor's splice holds, and the history's bounds in `proj_len()` are loops and powers, no
Python object. The caches will be sized from the contract: `t` 0..745, a policy issued at
18 to expire at 70, 624 months, issued 120 months on, and the roll-forward's `t + 1`; and
`z` 0..625, `max_dur()`, which does not grow with the horizon.
