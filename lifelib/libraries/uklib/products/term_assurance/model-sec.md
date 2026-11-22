# In-Force Implementation Notes

**Status:** Draft, 2026-11-22. `Term_UK_SEC` is [`Term_UK_S`](model.md) taught to project
from a valuation date. Besides policies issued at that date, it takes policies already in
force there, in any month of their policy year, and policies to be written in the ten
years after it, as lifelib's `basiclife/BasicTerm_SE` extends `basiclife/BasicTerm_S`. The
product is the one [`product-spec.md`](product-spec.md) specifies and
[`technical-notes.md`](technical-notes.md) models; this page says what running in force
changes. The suffix adds lifelib's letters to `S`: `E` for in force, as in
`BasicTerm_SE`, and `C` for the compiled form, as in `basiclife/BasicTerm_SC`, which the
model's next step adds (UKLIB-SEC-PLAN.md U2). Until then it runs in modelx alone.

> **This is a mechanics demonstration, not a pricing or reserving result.** The model is
> `Term_UK_S` on another time axis, and it reads `Term_UK_S`'s assumption tables in place,
> every assumption unchanged: the contractual mechanics are sourced, and every
> quantitative assumption is a **[std]** standardization, the mortality basis a proxy for
> the subscriber-restricted CMI "16" Series tables [R11]. Replace them with company data
> and licensed tables before drawing any conclusion from the numbers.

## Run it

```bash
python products/term_assurance/run_sec.py            # point 1: the anchor cell, issued at t = 0
python products/term_assurance/run_sec.py 8          # point 8: the anchor cell in force 5 years
python products/term_assurance/run_sec.py --block    # every model point, summed row by row
```

The first prints the twelve rows `run.py` prints for `Term_UK_S`'s point 1, with the
policy counts behind them. Three lines to the same thing for point 8:

```python
import modelx as mx
model = mx.read_model("products/term_assurance/Term_UK_SEC")
model.Projection[8].result_cf()
```

`Projection` takes a `point_id`, as `Term_UK_S`'s does; it will take `idx`, a point's
position in the table, once the model compiles, and the runner takes its key from the
model either way. `result_cf()` has `Term_UK_S`'s columns — `pols_if`, `premiums`,
`claims_death`, `claims_fib`, `claims_lapse`, `claim_expenses`, `expenses`, `commissions`
and `net_cf` — with one row per month from the valuation date, `t = 0 … proj_len() − 1`.
`result_pols()` sets out the counts behind it on the same rows: `pols_if`,
`pols_new_biz`, then the month's deaths and lapses in processing order, the expiries of the
last covered month, and `Term_UK_S`'s other four columns, the policies paying premium, the
deaths since issue, `fib_cum`, and the two monthly rates.

`--block` projects every point and releases its ItemSpace once its frame is read, so the
run holds the cells of one point at a time. Deleting it, `del model.Projection[8]`, is not
enough: an ItemSpace sits in reference cycles, which only Python's cyclic collector frees,
so the runner collects after each release. It freezes everything alive (`gc.freeze()`)
once the model and its table are read, and again once it has asked every point for its
frame, so that each collection scans only what the block has made since. It keeps the
block's sum as it goes, compensated as pandas sums a `groupby`, so that the block is, bit
for bit, the frames concatenated and summed by `t`.

The runner is uslib Term's, so it already takes `--cython`, which runs the compiled model
in place of modelx, building it first with the repository's `tools/build_sec_cy.py`, and
`--build DIR`, which runs a build made elsewhere. The model compiles from its next step
on, which brings the build's `sample_sec.py` and `spec_sec.py`; until then a build stops,
saying why. A `lifelib.create()` copy carries no `tools/`, and there `--cython` stops
before building, saying so.

## Two clocks

The model runs on two clocks, and each formula reads the one its quantity belongs to.

- **`t`, the valuation clock**, counts months from the valuation date. `t = 0` is the
  valuation month for every model point, however old the policy, and the frame runs
  `t = 0 … proj_len() − 1`, where `proj_len()` is the number of months from the valuation
  date to the end of the term.
- **`duration_mth(t)`, the policy clock**, counts the months the policy has been in force
  at time `t`: `duration_mth(t) = duration_mth_init() + t`, with `duration_mth_init()` read
  from the model point. It is the technical notes' month index `k`, and the contract runs
  on it: `duration(t) = duration_mth(t) // 12`, the select duration,
  `policy_year(t) = duration(t) + 1`, the lapse table's key, and
  `age(t, life) = age_at_entry(life) + duration(t)`, the mortality table's, as in
  `Term_UK_S`. `BasicTerm_SE` reaches the same numbers by adding one a month, a recursion
  as long as the frame; the closed form needs no such chain of calls.

Point 8 is the anchor cell in force 60 months, `Term_UK_S`'s own point 8. At `t = 0` it is
in policy year 6 at attained age 40, and its frame has 240 rows, `t = 0 … 239`; S projects
the same months as its rows 60 to 299. Point 14 is the waiver point to be issued 13 months
after the valuation date: `duration_mth(0) = −13`, it is on the books from
`t_entry() = 13`, rows 0 to 12 are zeros, and its frame has 253 rows.

| Read on the policy clock | Read on the valuation clock |
|---|---|
| the mortality table at the attained age and the select factor at the select duration; the lapse table by policy year; the decreasing schedule `B(k)` and the family income benefit's commuted value `I a(N − k)` at the policy month; an annual premium on the policy anniversary; the RPI increase on each anniversary; renewal commission from the second policy year; the clawback window from issue; the end of cover | expense inflation, `inflation_factor(t) = 1.03^(t // 12)` |

Expense inflation alone runs on `t`, stepping on each anniversary of the valuation date, so
the maintenance charge is in valuation-date pounds, for every point alike. Acquisition, £150
per policy issued, and the initial commission, 150% of the issue premium's year, are
charged in the issue month and not inflated, as in `basiclife/BasicTerm_SE`.

Because row `t` is the same month for every point, the frames of a block line up and sum
row by row, which is what `run_sec.py --block` prints:

```python
import pandas as pd
frames = [model.Projection[p].result_cf() for p in model.Data.model_point_table().index]
block = pd.concat(frames).groupby(level="t").sum()
```

On a point issued at `t = 0` the two clocks coincide, and the model computes what
`Term_UK_S` computes: every cell the two models share agrees, but two whose meaning
changed, `pols_if_init()`, now the count already in force at the valuation date, 0 for new
business, and `model_point()`, a row of another table. `Term_UK_S` charges acquisition and
the initial commission on the count in force at `t = 0`, which on such a point is the count
issued, so the two agree at any count.

## The in-force interface

The model point table is `model_point_table_sec.csv`. It carries `Term_UK_S`'s columns, two
of them restated as the in-force interface under `basiclife/BasicTerm_SE`'s names, and
seven columns of opening state. Each state column is per policy in force, or a ratio, so
that `policy_count` is the one weight on every flow, and each is measured at the valuation
instant, the start of month 0, before any month-0 event (USLIB-SEC-PLAN.md D6). Each is
history: what the policy has had or paid, never re-derived from a Reference, which is an
assumption from the valuation date on, so that a Reference changed there reaches back over
no month already run (UKLIB-SEC-PLAN.md K14, §9 item 5):

| Column | Unit | Measured at | Meaning |
|---|---|---|---|
| `policy_count` | policies, not necessarily whole | for a point in force, the start of month 0, before any month-0 event; for any other, its issue month | the policies in force at the valuation date, for a point already in force; the policies issued, for one issued at or after it |
| `duration_mth` | whole months | the valuation date | the policy's age in months: positive in force, 0 for a policy issued at the valuation date, `−k` for one to be issued `k` months later, with `k` at most 120 as shipped |
| `lapse_cum_init` | a share of the policies issued, 0 to below 1 | the start of month 0 | the selective-lapse ratio `w_cum`: the share of the issued cohort that has lapsed |
| `fib_cum_init` | deaths per policy in force, 0 or more | the start of month 0 | the deaths since issue, for each policy still in force, on every shape, which `cohort_frac` opens from |
| `fib_streams_init` | streams per policy in force, 0 to `fib_cum_init` | the start of month 0 | on the family income benefit, the streams in payment: the deaths since issue whose instalments were not commuted, at the take-up of the month each fell in; 0 on the other shapes |
| `idx_factor_init` | a factor, 1 or more | the policy year under way at the valuation date; on an anniversary, the one it opens | the RPI cover increases already given, on the sum assured at issue |
| `idx_prem_factor_init` | a factor, 1 or more | as `idx_factor_init` | the RPI premium increases already given, on the premium at issue |
| `wop_waived_frac_init` | a share of the policies in force, 0 to 1 | the start of month 0 | the policies whose premium the waiver of premium rider waives; 0 while the policy has been in force no longer than the deferred period |
| `comm_init_pp_init` | pounds per policy, 0 or more | issue | the initial commission the policy paid when it was written, which the clawback recovers; 0 on a point issued at or after the valuation date, which pays `comm_init_rate` in its issue month |

`Term_UK_S` re-derives two of them from References, which a Reference changed at the
valuation date would rewrite back to issue. It pays the family income benefit on
`(1 − c)` of every death since issue at the take-up `c` of the day, so a take-up of 0.5 set
at the valuation date of the point in force at 66 would commute half the streams long in
payment, and pay 49.6% low at `t = 0`; here the streams in payment are a column, and each
later death adds its `(1 − c)` share, `fib_streams(t)`, so that the payment is
`I [(1 − c) D(t) + streams(t)]`, `Term_UK_S`'s number at a take-up that never changes, bit
for bit on its new business. And it rebuilds the commission paid at issue from
`comm_init_rate`, which the clawback recovers; here a point in force reads it.

The waiver's deferred period is a vector whose length is a Reference,
`Projection.wop_defer_mths`, six months as shipped, so it goes in a companion,
`wop_pipeline_sec.csv`, keyed by `point_id` and `lag`, as uslib's indexed UL keys its
segment ladder by slot:

| Column | Unit | Measured at | Meaning |
|---|---|---|---|
| `point_id` | a label of the model point table | — | the point the row belongs to, and the only column that names one |
| `lag` | whole months, 1 to `min(wop_defer_mths, duration_mth)` | — | the policy month `lag` months before the valuation date in which the lives became incapacitated |
| `wop_deferred_init` | a share of the policies in force, 0 to 1 | the start of month 0, after the recoveries of the `lag − 1` months since | the lives still in the deferred period from that month: its incidence, `inc_m (1 − u)` of the premium-paying lives, less those who have recovered since |

That is what `Term_UK_S`'s `wop_waived_frac(t)` carries into a month a later month reads:
the waived share itself, `u(t − 1)`, and the incidence of the month `wop_defer_mths + 1`
months back, whose lives enter waiver once the deferred period has run, those who have not
recovered. At the valuation date the waived share is `wop_waived_frac_init`, and the
cohorts of the six months before it are still in the deferred period: in the frame's
first six months, the entrants of month `t` are the share at lag `7 − t`, carried through
the `t` months of its deferred period still to run at the recovery rate, `(1 − rec_m)^t`.
UKLIB-SEC-PLAN.md §6.1 names the pipeline's state "the incidence of the deferral months not
yet waived"; it is precised here as the share still in the deferred period at the valuation
instant. Held as the incidence, the `lag − 1` months of each deferred period already run
would be run again at the recovery rate of the day, so that a rate changed at the
valuation date would reach back over them; held so, only the months still to run take it.
Income protection's claim cohorts take the same form.

A cohort seven months back or more has entered the waived share already; one before issue
there is none of. A point in force with the rider holds one row for each of its last
`min(6, duration_mth)` months, and none otherwise; `Data` refuses a row for a point the
table lacks, without the rider, at a lag before issue, twice, or with a share that is not
one, and `proj_len()` a point that does not hold exactly its lags, by their count and by
its last, naming it, since the deferred period is the product's Reference. The pipeline
and the waived share are history, read from the extract: a model that recomputed them from
`wop_inc_rate` would pass the splice, which recomputes them alike, so a test writes them
off the rate's path and projects through them, and another changes the recovery rate at
the valuation date (UKLIB-SEC-PLAN.md K14).

`lapse_cum_init` is the selective-lapse ratio as `Term_UK_S` defines it, a share of the
policies issued, so the count does not move it. Its increments are a share of the issued
cohort too, which a point in force does not count; `Term_UK_S` divides each month's lapses
by the count its frame opened with, which on a point it restates in force is the count in
force, not the cohort issued, and its deaths under the loading part from the projection
from issue by up to 10% (UKLIB-SEC-PLAN.md G2). Here `cohort_frac(t)`, the share of the
issued cohort in force, rebuilds the cohort from the opening state: every policy issued is
still in force, has died or has lapsed, since none expires before the end of cover, so the
policies issued are those in force with the deaths since issue, `1 + fib_cum_init` per
policy in force, over the share that has not lapsed, `1 − lapse_cum_init`. The ratio then
grows by `cohort_frac(t) (1 − q_m) w_m` a month, with no count in it, which is
`Term_UK_S`'s `pols_lapse(t) / pols_if_init()` on a point that counts one policy issued.

| `Term_UK_S` | `Term_UK_SEC` | Why |
|---|---|---|
| `pols_if_init` (1.0) | `policy_count` | The count, under BasicTerm_SE's name. `pols_if_init()` now means the count in force at the valuation date, 0 for a point issued at or after it |
| `duration_inforce` (whole years) | `duration_mth` | The policy clock, in months, any month of a policy year; the S column is dropped |
| — | the seven state columns and the pipeline | `Term_UK_S` restarts each where its frame opens: the lapse ratio at 0, the ledger and its streams at 0, the waiver with none waived and none in the deferred period, and the factors at 1; and re-derives the commission paid at issue from today's rate |

The columns carried over are read as `Term_UK_S` reads them. For a policy in force, the
facts they record are still those at issue:

| Column | Unit | Measured at |
|---|---|---|
| `point_id`, `policy_id` | labels | — |
| `age_at_entry`, `joint_age` | years, age nearest birthday | issue, not the valuation date: `age(0, life)` is the attained age there |
| `shape`, `sex`, `smoker`, `joint_sex`, `joint_smoker`, `mort_basis` | codes, as in `Term_UK_S`'s table | issue |
| `policy_term` | whole years | issue |
| `sum_assured`, `fib_income`, `premium_mth` | pounds, the amounts at issue | issue: on an indexed point the year's cover and premium are these times the factors |
| `sched_rate` | a rate a year | issue: the decreasing schedule runs from issue on the policy clock |
| `joint_first_death`, `indexation`, `wop` | True or False | issue |
| `premium_mode` | monthly or annual | the mode billed over the frame; an annual premium falls on the policy anniversary |
| `fib_commute_rate` | a share | an assumption, not a fact about the policy |

Three more columns, `row_kind`, `source_policy_id` and `source_mth`, record where the
generator took each shipped row from (below). No formula reads them, and an in-force
extract need not carry them: without them the model projects the same numbers, and
`run_sec.py` runs.

`Data.model_point_table()` checks the table as it reads it, over all rows at once. The
first check that fails raises `ValueError`, naming the missing column or every point that
fails it: the seven in-force columns are present; no `point_id` appears twice;
`policy_count` is a number, zero or more; `duration_mth` is a whole number of months,
below `2**53`, and −120 or more, future new business being written over a horizon,
`Data.future_horizon_mth`, 120 months as shipped, which set to 0 refuses future new
business altogether; each state column is a number in its range; a point not yet in force
holds the issue values, 0 for the ratio, the deaths, the streams, the waived share and the
commission, and 1 for the factors; each flag is True or False; each code is one
`Term_UK_S` knows; the ages and the term are finite numbers, the amounts and the schedule
rate zero or more, and the commutation share from 0 to 1; a joint point has a second life;
indexation is elected on the level shape alone; the factors are 1 without indexation, the
waived share 0 without the waiver, and the streams 0 off the family income benefit; and
the streams in payment are no more than the deaths since issue. `Term_UK_S` meets most
of these only when a projection reaches them, and some never: a blank flag reads as
True, and one stray word in a flag column turns every `False` in it to text that reads as
True.

A point whose cover had ended by the valuation date, `duration_mth ≥ 12 × policy_term`,
reads, but `proj_len()` refuses it, naming the point: the end of cover is the product's
rule, not the table's. So does a point the contract does not write
([`product-spec.md`](product-spec.md)): a term above 50 years, `Projection.policy_term_max`,
or 40 on the family income benefit, `policy_term_max_fib`; a life issued below 18,
`issue_age_min`; or a life whose cover runs past attained age 90, `expiry_age_max`, or 70
on the family income benefit, `expiry_age_max_fib`. Each is a lower-case Reference, the
contract a compiled model's caches will be sized from: a frame of at most 600 months and
the horizon, ages from 18 to 89 on the mortality table, a schedule of 600 months and an
annuity-certain of 480. None is `expiry_age`, the U.S. tail's name, which `Term_UK_S`'s
tests hold absent. A loop over the block meets such a row only when it reaches it, after
projecting the points before it, so `run_sec.py --block` asks every point for its frame
before it projects any, and stops before it prints anything.

The assumption tables are checked before a value of them is read, each in the cell the
projection takes its extent from: `Data.mort_age_first` and `mort_age_last` for the
mortality table, whose four groups, M and F by N and S, must run over the same ages
without a gap or a repeat, each rate a number from 0 to 1; `Data.select_last_duration` for
the select factors, durations from 0 without a gap, each factor a number, zero or more;
and `Data.lapse_last_year` for the lapse table, policy years from 1 without a gap, each
rate from 0 to 1. A key is read by its value, so an age written `35.0` is 35. Each refusal
names the file, the column and its lines. A read past a table, an attained age outside the
mortality table or a select duration past the select table, is refused by the one cell
that reads the table, naming the point, where `Term_UK_S`'s lookup raised `KeyError`.

## The model points

No row of `model_point_table_sec.csv` or of `wop_pipeline_sec.csv` is typed by hand. Every
one is generated from `Term_UK_S` and its table by `tests/uk_sec_support.py`, from the
`Term_UK_SEC` entry in its `SEC_SPECS`, and the tests regenerate both and compare, so an
edit to a `Term_UK_S` row reaches them or fails the suite. In the source repository,
`python tools/gen_sec_points.py Term_UK_SEC` writes them.

| Point | Kind | From | At the valuation date |
|---|---|---|---|
| 1 to 7 | twin | S points 1 to 7 | issued at `t = 0`: `Term_UK_S`'s worked example and its shapes, bases and options |
| 8 | twin | S point 8, in force at S month 60 | in force five years, opened where `Term_UK_S` opens it: nothing lapsed, no ledger, no waiver, no index step |
| 9 | derived | S point 5 at S month 60 | the indexed point on its fifth anniversary, its factors those of policy year 6 |
| 10 | derived | S point 3 at S month 66 | the family income benefit mid-year, its streams in payment |
| 11 | derived | S point 7 at S month 66 | the waiver point after its select period, a share waived and six months of deferred lives in the pipeline |
| 12 | derived | S point 7 at S month 4 | the waiver point inside its deferred period, four months of deferred lives and none waived |
| 13 | derived | S point 1 at S month 299 | in its last covered month: a one-row frame |
| 14 | future | S point 7, 13 months on | to be issued at `t = 13` |

A derived row's `policy_count` is the count `Term_UK_S` carries into that month, its
`pols_if(d)`, and its state what S carries there, so the row continues the S projection
from there: point 9 opens with 0.685393 policies, 31.2% of the cohort lapsed, and cover
and premium factors of `1.03^5` and `1.045^5`. Its `policy_id` is the S row's with the
month appended, `TA-000005-M60`, and a future row's carries the months to issue,
`TA-000007-F13`. Row `t` of a generated point is month `t + source_mth` of its S point.
The pipeline holds point 11's six lags and point 12's four.

## Counts and timings

`pols_if_init()` is the count in force at the valuation date: `policy_count` for a point
already in force, 0 for any other. `pols_new_biz(t)` is `policy_count` in the issue month,
the month with `duration_mth(t) = 0`, and 0 in every other. `pols_if_at(t, timing)` keeps
`Term_UK_S`'s three timings and adds `basiclife/BasicTerm_SE`'s `"BEF_NB"`:

- `"BEF_NB"`, the count carried in from month `t − 1`, before month `t`'s new business:
  `pols_if_init()` at `t_entry()`, the first month on the books, and the survivors of
  month `t − 1` after it;
- `"BEF_DECR"`, that count plus `pols_new_biz(t)`, before month `t`'s decrements, which
  `pols_if(t)` returns;
- `"BEF_LAPSE"`, after the month's deaths, before its lapses;
- `"AFT_DECR"`, the end of the month, after its deaths and lapses, which is `"BEF_NB"`
  at `t + 1` exactly, and 0 from the last covered month on.

Any other timing raises. The survivors carried into month `t` are those of month `t − 1`'s
`"BEF_DECR"` count, which `"BEF_NB"` forms itself, as its own value at `t − 1` plus that
month's new business, exactly the sum `"BEF_DECR"` returns. So the chain of calls from
month `t` back to `t_entry()` is one cell a month, where `Term_UK_S`'s `pols_if` chain
runs three. On a model just read, a cold `net_cf` in the last month runs 11 cells deeper
than one a month, on every committed point and at the contract's longest cover, a 50-year
term from issue age 18, issued now and 120 months on; each other chain, the lapse ratio,
the cohort's share, the waived share and the deaths since issue, is one cell a month too.

The roll-forward closes as

```
pols_if(t) − pols_if_at(t + 1, "BEF_NB")
    = pols_death(t) + pols_lapse(t) + pols_maturity(t)
```

at every `t` of every frame, and `pols_if(t + 1)` adds `pols_new_biz(t + 1)` to the count
on the left. Joint first death is still one policy decremented by `1 − (1 − q1)(1 − q2)`,
and the policies paying premium are `pols_if(t) (1 − u(t))`.

Cover is `is_active(t)`, `0 ≤ duration_mth(t) < term_mths()`, `Term_UK_S`'s own frame from
issue on the policy clock, and outside it, before issue and from the end of the term on,
every count is zero, and so every cash flow. No count evaluates a decrement rate there,
and no table is read at a select duration, a policy year or an attained age the policy
does not have: `select_factor`, `mort_rate_base`, `lapse_rate_base`, the benefit, the
commuted value, the premium and the factors are zero outside cover, before any table or
rate is read.

## Departures from Term_UK_S

Each formula that tested `t` against a contractual event now tests the policy clock, each
read of a contractual schedule at a month passed as `t` is a read at the policy month or
year, and each recursion opens at `t_entry()` from the opening state. Where `Term_UK_S`'s
test would have stayed correct on the valuation clock, it moved anyway, so that cover has
one definition. Fifteen cells are new, and two of `Term_UK_S`'s, `proj_start` and
`duration_inforce`, are gone, `duration_mth` replacing both; the twin identity names them
as dropped, and a cell of `Term_UK_S`'s that this model lacked without saying so would
fail it.

| Cells | `Term_UK_S` | `Term_UK_SEC` | Why |
|---|---|---|---|
| `duration_mth`, `duration` | `t`, `t // 12` | `duration_mth_init() + t`, `duration_mth(t) // 12` | The policy clock, opened from the model point |
| `proj_len` | `term_mths()`, from issue | `term_mths() − duration_mth_init()`, from the valuation date; raises past cover, outside the contract's bounds, on a short pipeline and, on a waiver point, on a waiver rate outside 0 to 1 or a share waived before the deferred period has run | The frame starts at the valuation date |
| `age_at_entry`, `sex`, `smoker`, `age`, `mort_rate_base`, `mort_rate_life` | `life=1`, a default | `life`, no default; every call passes 1 or 2, positionally | A compiled model declares a defaulted parameter as `long long life=*`, which the C step's typing guard would read as a parameter of that name; modelx keys `Term_UK_S`'s `age(t)` as `(t, 1)`, so the twin identity pairs the cells as before |
| `pols_if`, `pols_if_at`, `pols_if_init` | a recursion through `"AFT_DECR"`, three cells a month, from the column's 1.0 at `proj_start()` | `"BEF_DECR"`, one cell a month from `t_entry()`; `pols_if_init()` is 0 unless in force | Policies in force at the valuation date open the count; new business joins it in its issue month |
| `pols_maturity`, `"AFT_DECR"` | at `t = proj_len() − 1` | at `duration_mth(t) = term_mths() − 1` | One definition of cover, on the policy clock |
| `lapse_cum` | 0 at `proj_start()`, then lapses over the count S opened with | `lapse_cum_init()` at `t_entry()`, then `cohort_frac(t − 1)` times the month's lapse probability | The ratio carried in, and a share of the cohort issued, which no count moves |
| `fib_cum` | 0 at `proj_start()` | `fib_cum_init() × pols_if_init()` at `t_entry()` | The deaths since issue at the valuation date |
| `claims(t, "FIB")`; `fib_streams`, new | `(1 − c) I [D(t) + FIBcum(t)]` | `I [(1 − c) D(t) + fib_streams(t)]`, the streams opening at `fib_streams_init() × pols_if_init()` | The streams in payment are history, which a take-up changed at the valuation date does not commute; S's number at a take-up that never changes |
| `wop_waived_frac` | 0 at `proj_start()`, no entrants from before it | `wop_waived_frac_init()` at `t_entry()`; entrants from before it, `wop_deferred_init(lag) (1 − rec_m)^t`, from after issue; a share outside 0 to 1 refused | The waived share and the deferred period carried in, at the valuation instant; past an incidence of about 0.855 S's share passes 1 |
| `idx_factor`, `idx_prem_factor` | a step per anniversary since `proj_start()`'s, from 1 | `idx_factor_init()` and `idx_prem_factor_init()`, then a step per anniversary since `t_entry()`'s | The increases already given are history |
| `premium_pp` | an annual premium where `t % 12 == 0` | where `duration_mth(t) % 12 == 0` | An anniversary is a policy month |
| `fib_commute_pp` | `I a(N − t)` | `I a(N − duration_mth(t))` | The months left to the end of the term |
| `benefit_pp`, `select_factor`, `mort_rate_base`, `lapse_rate_base`, the counts | unguarded: no `Term_UK_S` frame has a month outside cover | zero outside cover, before any table or rate is read; the tables' extents from `Data`, a read past them refused by name | Before issue S raises `KeyError` on the tables, and `B(k)` at a negative month exceeds the sum assured without a word |
| `inflation_factor` | `1.03^duration(t)`, from issue | `1.03^(t // 12)`, from the valuation date | Unit costs in valuation-date pounds |
| `expenses`, `commissions` | acquisition and the initial commission on `pols_if(t)` at `t = 0`; renewal from `t ≥ 12` | on `pols_new_biz(t)`; renewal from `duration_mth(t) ≥ 12` | A point in force bears no acquisition, one issued later bears it in its issue month, per policy issued and not inflated, as in `basiclife/BasicTerm_SE` |
| `comm_init_pp` | `comm_init_rate × 12 P_m × idx_prem_factor(0)` | on new business `comm_init_rate × 12 P_m`; in force, `comm_init_pp_init()` | The issue premium, S's month 0 not being the issue month on a point in force; and what a policy in force paid is history, which a rate changed at the valuation date does not move |
| `comm_clawback` | `t + 1` months in force | `duration_mth(t) + 1` | The window runs from issue |
| `check_pols_roll_fwd_resid` | `pols_if(t + 1)` | `pols_if_at(t + 1, "BEF_NB")` | The next month's new business is no part of month `t`'s movement |
| `check_fib_ledger_resid` | `(1 − c)` of the deaths summed from `proj_start()` | the opening streams, then `(1 − c)` of the deaths summed from `t_entry()` | The rebuild starts from the streams in payment at the valuation date |
| `check_pols_roll_fwd`, `check_fib_ledger` | `range(proj_start(), proj_len())`, tolerance on `pols_if_init()` | `range(proj_len())`, tolerance on `policy_count()` | The frame from the valuation date; S's `pols_if_init` is 0 on new business here |
| `result_cf` | `range(proj_start(), proj_len())` | `range(proj_len())` | Row 0 is the valuation month |
| `result_pols` | — | `pols_new_biz` added, the rates 0 outside cover | The counts behind `result_cf()`, after `basiclife/BasicTerm_SE`'s `result_pols()` |

Of the cash flows, the change of clock moves the maintenance expense alone, and `net_cf`
with it. Point 8 carries that expense in valuation-date pounds, so its `expenses(t)` is
`Term_UK_S`'s `expenses(60 + t)` divided by `1.03^5`. Its `pols_if`, `premiums`, the three
claims columns, `claim_expenses` and `commissions` are `Term_UK_S`'s from month 60 on.
Point 14 is `Term_UK_S`'s point 7 thirteen months on in those columns too; its maintenance
expense is `1.03^(t // 12 − (t − 13) // 12)` above S's at each `t`, and its acquisition
£150 exactly.

`mort_rate_life` caps the annual rate at 1, written `min(q, 1.0)`, the product first and
the bound second, as `Term_UK_S` writes it, so that a NaN stays NaN where `min(1.0, q)`
would read it as certain death; wherever `q` is a number the two are the same float. No
shipped rate comes near it, the largest being 0.0077, and `Data` refuses a table rate past
1; the product can pass 1 through the selective-lapse loading, which a test shows. The
lapse rate's bound keeps `Term_UK_S`'s order, `min(1.0, …)`: it is no cap on mortality.

The waiver's incidence and recovery, `wop_inc_rate` and `wop_rec_rate`, are each one
Reference, with no factor and no annual-rate cell, so no cap reaches them, in `Term_UK_S`
or here, and this model keeps `Term_UK_S`'s formulas, `1 − (1 − r)^(1/12)`. Past 1 that
has no real value, and `Term_UK_S` projects a complex number; below 0 it is negative. So on
a waiver point `proj_len()` refuses either rate outside 0 to 1, or NaN, naming the point
and the Reference, where it refuses a negative deferred period; 0 and 1 are accepted, and
a point without the rider reads neither.

**A defect of the specification, kept in both models.** The waiver recursion,
`u(t + 1) = u(t)(1 − rec_m) + inc_m (1 − u(t − 6)) (1 − rec_m)^6`, takes each month's
incidence from `1 − u(t − 6)`, which counts the lives already in their deferred period
among those who can fall ill. A three-state rebuild, healthy, deferred and waived, takes
it from the healthy alone. On point 7 and the rows derived from it the entrants run up to
0.184% high, the waived share up to 0.182% (1.38e-5 absolute, at month 239), and the
premiums £0.07 (0.0011%) low over the frame. This model keeps `Term_UK_S`'s formula, as
uslib's `SPIA_US_SEC` keeps `SPIA_US_S`'s installment refund trim, so that the twin
identity and the splice hold; the fix belongs to the S model and its technical notes, and
is not part of this step. The over-count grows with the incidence: at the shipped
recovery rate and deferred period the share passes 1 from an annual incidence of about
0.8552, where the premium turns negative and both checks still pass, and at an incidence
of 1 it reaches 7.9e12. So `wop_waived_frac` refuses a share outside 0 to 1, naming the
point, the month and the share, in the month it first leaves: at 0.855 every waiver point
projects, at 0.856 the waiver point refuses at month 19, S's month and S's share, and at 1
at month 8. The refusal sits in the cell, where the share is computed month by month, and
not in `proj_len()`: the frame cannot know the share without running the recursion,
which reads the pipeline, which asks the frame first.

A waived share is also refused on a point in force no longer than the deferred period, a
state `Term_UK_S` cannot reach: its first incapacity has not yet run the six months. The
deferred period is a Reference of the projection, which `Data` cannot read, so the rule
is `proj_len()`'s, beside the pipeline's length, which reads it too.

## Tests

- **The twin identity**, in `tests/test_model_conventions_uk.py`: on points 1 to 7, every
  cell of `Term_UK_S`'s agrees at every argument `Term_UK_S` evaluates in its own sweep,
  to 1e-9 relative with no absolute floor, but for `pols_if_init` and `model_point`, and
  `proj_start`, `duration_inforce` and `result_pols`, which the spec names with its
  reasons; a cell this model lacked would fail it. So `Term_UK_S`'s worked example, which
  `tests/test_term_assurance_uk.py` asserts to the penny and the in-force to six decimals,
  holds here with no number restated. The same suite holds the model to the conventions
  every `_SEC` model meets: every frame starts at `t = 0`, `pols_if` is the `"BEF_DECR"`
  count, new business enters once at its `policy_count`, nothing happens before issue,
  and the in-force columns are present.
- **The splice**, in `tests/test_term_assurance_uk_sec.py`: each `Term_UK_S` point
  restated in force at months 1, 6 and 7 (the waiver's first entrants), 11, 12 and 13 (the
  first anniversary), 22, 23 and 30 (the selective-lapse ratio's crossing), 47 and 48 (the
  clawback window's end), 59 and 60 (the select period's end), 66, 120, 239 and 299,
  continues the S projection in every cell the two share but `proj_len`, and in both
  reports, to 1e-9 relative with no absolute floor; so does S's own point 8, in force at
  60, and restated at 66, 120 and 299. Every switch that ships off is on in both models:
  the selective-lapse loading at 0.25, rebroking at a market ratio of 1.25 and the
  four-year clawback; inflation, the one input on the valuation clock, is 0 in both. Five
  variants of S's points, in a copy of S's table that is never committed, reach what S's
  own cannot: an annual payer on the indexed point and a male smoker, the family income
  benefit commuted in half, the waiver point indexed, the decreasing shape at a schedule
  rate of 0, and a joint point whose second life is a male smoker. A core of 34 of the
  139 splice cases and 8 of the 21 future ones runs by default, and the full grid with
  `UKLIB_SEC_FULL=1`; a test asserts the core reaches every branch, opening-state
  column, kind of valuation month and side of every `min` and `max` the full grid
  reaches.
- **Future new business**: issued 1 and 12 months after the valuation date, each S point is
  the S projection moved on, with zeros before issue and no rate evaluated there, and so is
  each variant issued a month on, the waiver point 13 months on and the indexed point 25.
- **How it computes**: on every row of the splice's grid, after its reports, its checks
  and every monthly cell at every month, no cell has been called at a negative month, none
  on the books read a month before `t_entry()`, none read a month later than `t + 1`, and
  none raised. On a fresh read of the committed model, `duration_mth(500)` evaluates
  `duration_mth` once, the policy clock being a closed form, and every point's reports and
  checks run under modelx's recursion limit lowered to 40, which a recursion backward over
  the frame would exceed. And each chain, called cold in the last month at the contract's
  longest cover, runs one cell a month back to `t_entry()` and at most 16 more.
- **Counts**: the roll-forward closes; `result_pols()` is S's report with `pols_new_biz`
  beside it; multiplying `policy_count` by 2.5, with every switch that ships off on,
  multiplies every flow and counted cell and moves no per-policy value, bit for bit, the
  lapse ratio and the cohort's share among them; and both checks, their tolerances scaled
  by the count, close on a million policies.
- **Validation and regeneration**: each malformed row of the table, 71 cases, and of the
  pipeline, 17, is refused naming its point or its line; the horizon is a Reference; a
  point past its cover, outside the contract's bounds or with a pipeline not exactly its
  lags, 8 cases, among them none at all and a gap, is refused by `proj_len()`, each bound
  just inside it and each moved past a committed point, and `run_sec.py --block` refuses
  such a point before printing anything; so is a share waived before the deferred period
  has run, at its last month among them; a waiver point under a waiver rate a float
  outside 0 to 1, or NaN, is refused by the frame, and under an incidence of 0.856 or 1 by
  the waived share in the month it passes 1, S's month and S's share, where at 0, at
  0.855 and at a recovery of 1 the twin of S's waiver point is S's in every cell; each
  assumption table a reader cannot read, 28 cases, is refused naming its lines, a repeated
  key with each of its lines, and a read beyond a table naming the point; keys written as
  floats read as `Term_UK_S` reads them; the edges of the interface and of each bound are
  accepted; every state `Term_UK_S` reaches, as shipped, under the splice's switches and
  where the cap binds, is accepted in force; and the committed table and pipeline are what
  `Term_UK_S` generates.
- **The product's own facts**: the two clocks on the shipped points; the committed rows,
  in force and issued later, continuing their S points at the shipped assumptions but for
  inflation; the lapse ratio carried on from the issued cohort, and the deaths it loads;
  each history column read, not recomputed, the index factors, the streams in payment, the
  commission paid at issue, the waived share and the pipeline's deferred lives, each
  written off its References' path and projected through, and the take-up, the commission
  rate and the recovery rate each changed at the valuation date reaching back over no
  month already run (UKLIB-SEC-PLAN.md K14); expense inflation on the valuation clock at
  the shipped 3%, which only this test sees; acquisition and the initial commission on new
  business alone; renewal commission and the clawback on the policy clock; an annual
  premium on the anniversary of a point valued mid-year; every guarded cell's value outside
  cover; the block; an extract without the generator's three columns, labelled otherwise,
  projecting the same numbers; `run_sec.py`'s numbers, for a point, the joint life among
  them, and for the block, and its sum, and its `--cython` stopping where no repository is
  above it; no cell's parameter defaulted but the `claims` total's; the docstrings, read
  through docutils as the docs build reads them where docutils is installed; and the
  shared input tables.
- **The cap**: on the anchor cell with its male non-smoker rates from age 50 at 0.96, in a
  copy of the table, under the splice's References, the product of the rate and the
  selective-lapse loading passes 1 from attained age 50, policy month 180. In both models
  `mort_rate_life`, `mort_rate` and `mort_rate_mth` are the float 1.0 there; every policy
  in force at the start of that month dies in it, and none is in force after it; the
  reports hold finite floats; and every cell the two models share agrees, issued now and
  12 months on, and restated in force the month before the cap, to 1e-9 relative with no
  absolute floor. And a NaN sent to the cap, through `mort_scale` or the loading's
  multiple, or to the RPI's floor and caps, stays NaN.

```bash
python -m pytest tests/test_term_assurance_uk_sec.py -q
UKLIB_SEC_FULL=1 python -m pytest tests/test_term_assurance_uk_sec.py -q   # the full grid
python -m pytest tests/test_model_conventions_uk.py -q -k Term_UK_SEC
```

<!-- BEGIN generated citation links -- regenerate with tools/gen_citation_links.py -->
[R11]: #uklib-term_assurance-r11
[std]: #uklib-std
<!-- END generated citation links -->
