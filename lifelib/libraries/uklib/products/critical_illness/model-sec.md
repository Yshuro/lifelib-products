# In-Force Implementation Notes

**Status:** Draft, 2026-11-22. `CI_UK_SEC` is [`CI_UK_S`](model.md) taught to project from
a valuation date. Besides policies issued at that date, it takes policies already in force
there, in any month of their policy year, and policies to be written in the ten years after
it, as lifelib's `basiclife/BasicTerm_SE` extends `basiclife/BasicTerm_S`. The product is
the one [`product-spec.md`](product-spec.md) specifies and
[`technical-notes.md`](technical-notes.md) models; this page says what running in force
changes. The suffix adds lifelib's letters to `S`: `E` for in force, as in `BasicTerm_SE`,
and `C` for the compiled form, as in `basiclife/BasicTerm_SC`, which the model's next step
adds (UKLIB-SEC-PLAN.md U2). Until then it runs in modelx alone.

> **This is a mechanics demonstration, not a pricing or reserving result.** The model is
> `CI_UK_S` on another time axis, and it reads `CI_UK_S`'s assumption tables in place,
> every assumption unchanged: the benefit structure is sourced, and every rate is a
> **[std]** standardization, the diagnosis and mortality bases proxies shaped like the
> subscriber-restricted CMI tables [R8]. Replace them with company data and licensed tables
> before drawing any conclusion from the numbers.

## Run it

```bash
python products/critical_illness/run_sec.py            # point 1: the anchor cell, issued at t = 0
python products/critical_illness/run_sec.py 9          # point 9: the reviewable point on its first review
python products/critical_illness/run_sec.py --block    # every model point, summed row by row
```

The first prints the twelve rows `run.py` prints for `CI_UK_S`'s point 1, with the policy
counts behind them. Three lines to the same thing for point 9:

```python
import modelx as mx
model = mx.read_model("products/critical_illness/CI_UK_SEC")
model.Projection[9].result_cf()
```

`Projection` takes a `point_id`, as `CI_UK_S`'s does; it will take `idx`, a point's
position in the table, once the model compiles, and the runner takes its key from the
model either way. `result_cf()` has `CI_UK_S`'s columns — `pols_if`, `premiums`,
`claims_main`, `claims_ap`, `claims_child`, `claims_lapse`, `claim_expenses`, `expenses`
and `net_cf` — with one row per month from the valuation date, `t = 0 … proj_len() − 1`.
`result_pols()` sets out the counts behind it on the same rows: `pols_if`, `pols_new_biz`,
then the month's main claims and lapses in processing order, the expiries of the last
covered month, and `CI_UK_S`'s other six columns, the end-of-month count and the first
life's diagnosis and mortality rates, the policy's annual and monthly claim rates and the
annual lapse rate.

`--block` projects every point and releases its ItemSpace once its frame is read, so the
run holds the cells of one point at a time. Deleting it, `del model.Projection[9]`, is not
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
  from the model point. The contract runs on it: `duration(t) = duration_mth(t) // 12`,
  `policy_year(t) = duration(t) + 1`, the lapse table's key, and
  `age(t, life) = age_at_entry(life) + duration(t)`, the pivot table's, as in `CI_UK_S`.
  `BasicTerm_SE` reaches the same numbers by adding one a month, a recursion as long as the
  frame; the closed form needs no such chain of calls.

Point 9 is the reviewable point in force 60 months, valued on its first review. At `t = 0`
it is in policy year 6 at attained age 45, and its frame has 240 rows, `t = 0 … 239`;
`CI_UK_S` projects the same months as its rows 60 to 299. Point 13 is the indexed point to
be issued 13 months after the valuation date: `duration_mth(0) = −13`, it is on the books
from `t_entry() = 13`, rows 0 to 12 are zeros, and its frame has 313 rows.

| Read on the policy clock | Read on the valuation clock |
|---|---|
| the diagnosis and mortality pivot rates at the attained age; the lapse table by policy year; the RPI increase on each anniversary; the premium reviews every 60 policy months from the fifth anniversary, and the shock lapse in the twelve policy months after each; the end of cover | expense inflation, `inflation_factor(t) = 1.03^(t // 12)`; the morbidity trend, `ci_trend_factor(t) = (1 + τ)^(t // 12)` |

Expense inflation and the morbidity trend run on `t`, stepping on each anniversary of the
valuation date, for every point alike (USLIB-SEC-PLAN.md D7; UKLIB-SEC-PLAN.md §9 item 4).
The maintenance charge is then in valuation-date pounds, and the diagnosis table states its
basis at the valuation date, trended from there: `CI_UK_S` trends it from issue, which on a
point in force would trend a basis stated today by the years the policy has already run.
The trend ships at 0, where the two clocks agree. The initial expense, £200 per policy
issued, is charged in the issue month and not inflated, as in `basiclife/BasicTerm_SE`.

Because row `t` is the same month for every point, the frames of a block line up and sum
row by row, which is what `run_sec.py --block` prints:

```python
import pandas as pd
frames = [model.Projection[p].result_cf() for p in model.Data.model_point_table().index]
block = pd.concat(frames).groupby(level="t").sum()
```

On a point issued at `t = 0` the two clocks coincide, and the model computes what
`CI_UK_S` computes: every cell the two models share agrees, but two whose meaning changed,
`pols_if_init()`, now the count already in force at the valuation date, 0 for new
business, and `model_point()`, a row of another table. `CI_UK_S` charges the initial
expense on the count in force at `t = 0`, which on such a point is the count issued, so the
two agree at any count.

## The in-force interface

The model point table is `model_point_table_sec.csv`. It carries `CI_UK_S`'s columns, one
of them restated as the in-force interface under `basiclife/BasicTerm_SE`'s name, a policy
clock column, and six columns of opening state. Each state column is a factor, a rate or a flag,
so that `policy_count` is the one weight on every flow, and each is measured at the
valuation instant, the start of month 0, before any month-0 event (USLIB-SEC-PLAN.md D6). A
review or an anniversary that falls at the valuation date, the start of month 0, is
already made at that instant: the premium due in month 0 is the reviewed one, and the cover
of the year an anniversary opens is the indexed one. Each is history: what the contract has
given or charged, never re-derived from a Reference, which is an assumption from the
valuation date on, so that a Reference changed there reaches back over no review or
anniversary already made (UKLIB-SEC-PLAN.md K14, §9 item 5):

| Column | Unit | Measured at | Meaning |
|---|---|---|---|
| `policy_count` | policies, not necessarily whole | for a point in force, the start of month 0, before any month-0 event; for any other, its issue month | the policies in force at the valuation date, for a point already in force; the policies issued, for one issued at or after it |
| `duration_mth` | whole months | the valuation date | the policy's age in months: positive in force, 0 for a policy issued at the valuation date, `−k` for one to be issued `k` months later, with `k` at most 120 as shipped |
| `idx_factor_init` | a factor, 1 or more | the policy year under way at the valuation date; on an anniversary, the one it opens | the RPI cover increases already given, on the sum assured at issue |
| `idx_prem_factor_init` | a factor, 1 or more | as `idx_factor_init` | the RPI premium increases already given, on the premium at issue |
| `review_prem_factor_init` | a factor, 0 or more | the review period under way at the valuation date; on a review month, the one it opens | the premium changes the reviews already made have given, on the premium at issue |
| `ci_sel_latched_init` | 0 or 1 | the start of month 0 | the select latch: 1 once a review at or before the valuation date has raised premiums past the shock threshold of its day, and 0 before |
| `ci_sel_factor_init` | a multiple of the diagnosis rate, above 0 | the start of month 0 | the factor the latch closed at, `1 + η` at the loading of its day, read only while the latch is closed: 1 on an open latch, and 1 or below 1 on one closed at a loading of 0 or less |
| `review_prem_shock_init` | a premium change, −1 or more | the review that opened the review period under way, at or before the valuation date | the change that review made, which sets the shock lapse of its twelve-month window; read only while that window is still running, and 0 before the first review |

`CI_UK_S` holds none of them. It recomputes the premium at month `t` as
`P × idx_p(t) × (1 + ρ)^reviews`, one `review_prem_shock` for every review since issue;
the latch as closed once any review's `ρ` passes the threshold; the shock lapse in every
window from that one `ρ`; and the index factors from one flat `rpi_rate`. On a point in
force those are facts of the contract: a `review_prem_shock` set at the valuation date
would reprice premiums long collected, open or close the latch at reviews long past, and
lapse a window already closed. Here a review after the valuation date applies
`review_prem_shock`, and one at or before it is the history the columns carry:

- `review_prem_factor(t)` opens at `review_prem_factor_init` and takes `1 + ρ` for each
  review after `t_entry()`, `reviews_passed(t) − reviews_passed(t_entry())`;
- `ci_sel_factor(t)` stays at `ci_sel_factor_init` where `ci_sel_latched_init` is 1, a
  latch already closed, whatever the factor, 1 among them, and otherwise closes at
  `1 + sel_lapse_ci_loading` at the first review after `t_entry()` whose `ρ` passes the
  threshold. The latch is a flag of its own because a latch closed at a loading of 0
  holds a factor of 1, which read as open would close again at today's loading;
- `review_prem_change(t)`, the change the review under way in month `t` made, is
  `review_prem_shock_init` for a review at or before the valuation date and
  `review_prem_shock` after it; `review_shock_active(t)` asks it inside a window alone, and
  the shock lapse reads it there.

On a point issued at the valuation date each history column holds its issue value, and the
model is `CI_UK_S`. A model that dropped the columns and recomputed them from the
References would pass the splice, since `CI_UK_S` and the splice recompute them alike, so
the tests write each off its References' path and project through it.

Nothing else on this product is history `CI_UK_S` rebuilds from a Reference: there is no
commission to claw back, the initial expense falls at issue alone, the additional-payment
and children's benefits read today's indexed cover through the contract's shares and caps,
and the trend and the inflation run from the valuation date. The contractual claim-count
caps, one claim per additional-payment condition and two children's claims, are ignored by
`CI_UK_S`'s frequency loadings, and a point in force carries no count of the claims it has
used either.

| `CI_UK_S` | `CI_UK_SEC` | Why |
|---|---|---|
| `pols_if_init` (1.0) | `policy_count` | The count, under BasicTerm_SE's name. `pols_if_init()` now means the count in force at the valuation date, 0 for a point issued at or after it |
| — | `duration_mth` | The policy clock, in months, any month of a policy year; every `CI_UK_S` point is new business |
| — | the six state columns | `CI_UK_S` recomputes each from its References, from issue: the index factors from `rpi_rate`, the review factor, the latch and the window's change from `review_prem_shock` |

The columns carried over are read as `CI_UK_S` reads them. For a policy in force, the
facts they record are still those at issue:

| Column | Unit | Measured at |
|---|---|---|
| `point_id`, `policy_id` | labels | — |
| `age_at_entry`, `joint_age` | years, age nearest birthday | issue, not the valuation date: `age(0, life)` is the attained age there |
| `contract_type`, `life_basis`, `sex`, `smoker`, `joint_sex`, `joint_smoker`, `cover_basis`, `premium_guarantee` | codes, as in `CI_UK_S`'s table | issue |
| `policy_term` | whole years | issue |
| `sum_assured`, `premium_mth` | pounds, the amounts at issue | issue: on an indexed or reviewed point the month's cover and premium are these times the factors |
| `children_cover`, `indexation` | True or False | issue |
| `premium_mode` | monthly or annual | inert, as in `CI_UK_S`: the premium is carried monthly either way |

Three more columns, `row_kind`, `source_policy_id` and `source_mth`, record where the
generator took each shipped row from (below). No formula reads them, and an in-force
extract need not carry them: without them the model projects the same numbers, and
`run_sec.py` runs.

`Data.model_point_table()` checks the table as it reads it, over all rows at once. The
first check that fails raises `ValueError`, naming the missing column or every point that
fails it: the eight in-force columns are present; no `point_id` appears twice;
`policy_count` is a number, zero or more; `duration_mth` is a whole number of months,
below `2**53`, and −120 or more, future new business being written over a horizon,
`Data.future_horizon_mth`, 120 months as shipped, which set to 0 refuses future new
business altogether; each state column is a number in its range, the latch 0 or 1 and its
factor above 0; a point not yet in force holds the issue values, 1 for the factors and 0
for the latch and the change; a point in force fewer than 12 months, before its first
anniversary, holds index factors of 1; an open latch holds a factor of 1; each flag is
True or False;
each code is one `CI_UK_S` knows, the smoker status `NS` or `S`, not term assurance's `N`;
the ages and the term are finite numbers, and the amounts zero or more; a joint point has a
second life, and is not on the standalone contract, which `CI_UK_S` scopes out; and the
index factors are 1 without indexation, and on a guaranteed point the review factor 1,
the latch open and the change 0. `CI_UK_S` meets most of these only when a projection reaches
them, and some never: a blank flag reads as True, and one stray word in a flag column turns
every `False` in it to text that reads as True.

A point whose cover had ended by the valuation date, `duration_mth ≥ 12 × policy_term`,
reads, but `proj_len()` refuses it, naming the point: the end of cover is the product's
rule, not the table's. So does a point the contract does not write
([`product-spec.md`](product-spec.md)): a term below 5 years, `Projection.policy_term_min`,
or above 50, `policy_term_max`; a life issued below 18, `issue_age_min`, or above 64,
`issue_age_max`; or a life whose cover runs past the 75th birthday, `expiry_age_max`, the
issue age plus the term. Each is a lower-case Reference, the contract a compiled model's
caches will be sized from: a frame of at most 600 months and the horizon, and attained ages
from 18 to 74 on the pivot table. On every point `proj_len()` also refuses a Reference
off its domain (below), and on a reviewable point a review history the point cannot have
had: a review factor other than 1, a closed latch or a change other than 0 while it has
been in force fewer months than `review_period_mths`, since no review is made before the
fifth anniversary; and between its first review and its second a review factor other
than `1 + review_prem_shock_init`, the one change made. What depends on an assumption of
its day is left alone: a latch left open after a change past today's threshold, the
threshold of its day perhaps higher, and the factor of two reviews or more. The
References are the projection's, which `Data` cannot read. A loop over
the block meets such a row only when it reaches it, after projecting the points before it,
so `run_sec.py --block` asks every point for its frame before it projects any, and stops
before it prints anything.

The assumption tables are checked before a value of them is read. The pivot table is
checked by its reader, `Data.ci_rate_table`, as it reads the file and before it indexes
and sorts it, so that a fault is named by its line: each age a whole number, each sex `M`
or `F` and smoker `NS` or `S`, each of the four groups holding two pivot ages or more, one
row an age, and each `i_ci` and `q_d` a number above 0 and at most 1, since
`pivot_interp` raises the ratio of two rates to a power. The pivot ages need not run
without a gap, nor be the same in each group. The lapse table is checked by
`Data.lapse_last_year`, the cell the projection takes its extent from: policy years from 1
without a gap, each rate from 0 to 1. A key is read by its value, so an age written `40.0`
is 40. Each refusal names the file, the column and its lines.

## The model points

No row of `model_point_table_sec.csv` is typed by hand. Every one is generated from
`CI_UK_S` and its table by `tests/uk_sec_support.py`, from the `CI_UK_SEC` entry in its
`SEC_SPECS`, and the tests regenerate it and compare, so an edit to a `CI_UK_S` row reaches
it or fails the suite. In the source repository, `python tools/gen_sec_points.py CI_UK_SEC`
writes it.

| Point | Kind | From | At the valuation date |
|---|---|---|---|
| 1 to 7 | twin | S points 1 to 7 | issued at `t = 0`: `CI_UK_S`'s worked example and its contracts, guarantees, lives and options |
| 8 | derived | S point 4 at S month 36 | the indexed point on its third anniversary, its factors those of policy year 4 |
| 9 | derived | S point 3 at S month 60 | the reviewable point on its first review, its history that review's |
| 10 | derived | S point 3 at S month 66 | the reviewable point inside the window its first review opened |
| 11 | derived | S point 3 at S month 78 | the reviewable point mid-year after the window closed |
| 12 | derived | S point 1 at S month 299 | in its last covered month: a one-row frame |
| 13 | future | S point 4, 13 months on | to be issued at `t = 13` |

A derived row's `policy_count` is the count `CI_UK_S` carries into that month, its
`pols_if(d)`, and its state what S carries there, so the row continues the S projection
from there: point 8 opens with 0.772371 policies and cover and premium factors of `1.03^3`
and `1.045^3`. At the shipped review change of 0 the reviewable rows' history is the issue
values, which the tests move off. A derived row's `policy_id` is the S row's with the month
appended, `CI-000003-M60`, and a future row's carries the months to issue, `CI-000004-F13`.
Row `t` of a generated point is month `t + source_mth` of its S point.

## Counts and timings

`pols_if_init()` is the count in force at the valuation date: `policy_count` for a point
already in force, 0 for any other. `pols_new_biz(t)` is `policy_count` in the issue month,
the month with `duration_mth(t) = 0`, and 0 in every other. `pols_if_at(t, timing)` keeps
`CI_UK_S`'s three timings and adds `basiclife/BasicTerm_SE`'s `"BEF_NB"`:

- `"BEF_NB"`, the count carried in from month `t − 1`, before month `t`'s new business:
  `pols_if_init()` at `t_entry()`, the first month on the books, and the survivors of
  month `t − 1` after it;
- `"BEF_DECR"`, that count plus `pols_new_biz(t)`, before month `t`'s decrements, which
  `pols_if(t)` returns;
- `"BEF_LAPSE"`, after the month's main claims, before its lapses;
- `"AFT_DECR"`, the end of the month, after its claims and lapses, which is `"BEF_NB"`
  at `t + 1` exactly, and 0 from the last covered month on.

Any other timing raises. The survivors carried into month `t` are those of month `t − 1`'s
`"BEF_DECR"` count, which `"BEF_NB"` forms itself, as its own value at `t − 1` plus that
month's new business, exactly the sum `"BEF_DECR"` returns. So the chain of calls from
month `t` back to `t_entry()` is one cell a month, where `CI_UK_S`'s `pols_if` chain runs
three. It is the model's one chain: the reviews, the latch and the factors are closed forms
on the policy clock. On a model just read, a cold `net_cf` in the last month runs 11 cells
deeper than one a month, on every committed point and at the contract's longest cover, a
50-year term from issue age 18, issued now and 120 months on, on the reviewable, the
standalone and the joint shapes alike.

The roll-forward closes as

```
pols_if(t) − pols_if_at(t + 1, "BEF_NB")
    = pols_claim(t) + pols_lapse(t) + pols_maturity(t)
```

at every `t` of every frame, and `pols_if(t + 1)` adds `pols_new_biz(t + 1)` to the count
on the left. The additional-payment and children's claims decrement nothing. Joint first
event is still one policy decremented by `1 − (1 − q1)(1 − q2)`.

Cover is `is_active(t)`, `0 ≤ duration_mth(t) < expiry_mth()`, `CI_UK_S`'s own frame from
issue on the policy clock, `expiry_mth()` its `12 × policy_term()`, and outside it, before
issue and from the end of the term on, every count is zero, and so every cash flow. No
count evaluates a rate there, and no table is read at a policy year or an attained age the
policy does not have: `ci_rate_base`, `mort_rate`, `lapse_rate_base`, the benefits, the
premium, the factors, the reviews and the latch are zero outside cover, before any table or
rate is read.

## Departures from CI_UK_S

Each formula that tested `t` against a contractual event now tests the policy clock, and
each recursion opens at `t_entry()` from the opening state. Where `CI_UK_S`'s test would
have stayed correct on the valuation clock, it moved anyway, so that cover has one
definition. Fourteen cells are new — `policy_count`, `duration_mth_init`, `t_entry`,
`is_active`, `expiry_mth`, `pols_new_biz`, the six accessors of the opening state,
`review_prem_factor` and `review_prem_change` — and none of `CI_UK_S`'s 63 is gone.

| Cells | `CI_UK_S` | `CI_UK_SEC` | Why |
|---|---|---|---|
| `duration_mth`, `duration` | `t`, `t // 12` | `duration_mth_init() + t`, `duration_mth(t) // 12` | The policy clock, opened from the model point |
| `proj_len` | `12 × policy_term()`, from issue | `expiry_mth() − duration_mth_init()`, from the valuation date; raises past cover, outside the contract's bounds, on a Reference off its domain, and on a review history before the first review | The frame starts at the valuation date |
| `age_at_entry`, `sex`, `smoker`, `age`, `ci_rate_base`, `mort_rate`, `ci_rate`, `claim_rate_life` | `life=1`, a default | `life`, no default; every call passes 1 or 2, positionally | A compiled model declares a defaulted parameter as `long long life=*`, which the C step's typing guard would read as a parameter of that name; modelx keys `CI_UK_S`'s `age(t)` as `(t, 1)`, so the twin identity pairs the cells as before |
| `pols_if`, `pols_if_at`, `pols_if_init` | a recursion through `"AFT_DECR"`, three cells a month, from the column's 1.0 at `t = 0` | `"BEF_DECR"`, one cell a month from `t_entry()`; `pols_if_init()` is 0 unless in force | Policies in force at the valuation date open the count; new business joins it in its issue month |
| `pols_maturity`, `"AFT_DECR"` | at `t = proj_len() − 1` | at `duration_mth(t) = expiry_mth() − 1` | One definition of cover, on the policy clock |
| `reviews_passed`, `review_shock_active` | `t // review_period_mths`; the window `t % review_period_mths < 12`, after a review whose `review_prem_shock` passes the threshold | `duration_mth(t) // review_period_mths`; the window on `duration_mth(t)`, asked first, after a review whose own change, `review_prem_change(t)`, passes it | A review falls on a policy month, and a review made before the valuation date made its own change |
| `premium_pp`; `review_prem_factor`, new | `P × idx_p(t) × (1 + ρ)^reviews_passed(t)` | `P × idx_p(t) × review_prem_factor(t)`, the factor opening at `review_prem_factor_init()` and taking `1 + ρ` for each review after `t_entry()` | The reviews already made are history |
| `ci_sel_factor` | `1 + η` once `reviews_passed(t) ≥ 1` while `ρ` passes the threshold | `ci_sel_factor_init()` while `ci_sel_latched_init()` is 1; else `1 + η` once a review after `t_entry()` has a `ρ` past the threshold | The latch closed before the valuation date is history, at the loading of its day, which may have been 0 |
| `lapse_rate`; `review_prem_change`, new | the shock `w + 2 max(0, ρ − 0.05)` | the shock from `review_prem_change(t)`, `review_prem_shock_init()` in the window of a review at or before the valuation date | A window open at the valuation date lapses at the change its review made |
| `idx_factor`, `idx_prem_factor` | a step per anniversary since issue, from 1 | `idx_factor_init()` and `idx_prem_factor_init()`, then a step per anniversary since `t_entry()`'s | The increases already given are history |
| `ci_trend_factor` | `(1 + τ)^(y − 1)`, from issue | `(1 + τ)^(t // 12)`, from the valuation date | A calendar trend on a basis stated at the valuation date |
| `inflation_factor` | `1.03^(y − 1)`, from issue | `1.03^(t // 12)`, from the valuation date | Unit costs in valuation-date pounds |
| `expenses` | the initial expense on `pols_if(t)` at `t = 0` | on `pols_new_biz(t)` | A point in force bears none, one issued later bears it in its issue month, per policy issued and not inflated, as in `basiclife/BasicTerm_SE` |
| `ci_rate_base`, `mort_rate`, `lapse_rate_base`, `benefit_pp`, `claims`, `claim_expenses`, the counts | unguarded: no `CI_UK_S` frame has a month outside cover | zero outside cover, before any table or rate is read; the lapse table's extent from `Data` | Before issue `CI_UK_S` extrapolates the pivots to ages the policy never reaches, and raises `KeyError` on the lapse table |
| `check_pols_roll_fwd_resid` | `pols_if(t + 1)` | `pols_if_at(t + 1, "BEF_NB")` | The next month's new business is no part of month `t`'s movement |
| `check_claim_split_resid` | any `q_exit` | zero outside cover; `q_exit` past 1 refused in the month it passes | Past 1 the independent conversion has no real value |
| `check_pols_roll_fwd` | `1e-10 × max(pols_if_init(), 1)` | `1e-10 × max(policy_count(), 1)` | `pols_if_init` is 0 on new business here; `check_claim_split` keeps `CI_UK_S`'s tolerance, `claim_split_tol`, a Reference, unscaled in both models, since the artefact it bounds is a rate no count moves |
| `result_cf` | `range(proj_len())`, from issue | `range(proj_len())`, from the valuation date | Row 0 is the valuation month |
| `result_pols` | — | `pols_new_biz` added, the rates 0 outside cover | The counts behind `result_cf()`, after `basiclife/BasicTerm_SE`'s `result_pols()` |

Of the cash flows, the change of clock moves the maintenance expense alone at the shipped
assumptions, and `net_cf` with it, the trend shipping at 0. Point 9 carries that expense in
valuation-date pounds, so its `expenses(t)` is `CI_UK_S`'s `expenses(60 + t)` divided by
`1.03^5`. Its `pols_if`, `premiums`, the four claims columns and `claim_expenses` are
`CI_UK_S`'s from month 60 on. Point 13 is `CI_UK_S`'s point 4 thirteen months on in those
columns too; its maintenance expense is `1.03^(t // 12 − (t − 13) // 12)` above S's at each
`t`, and its initial expense £200 exactly.

**The caps, as `CI_UK_S` has them since UKLIB-SEC-PLAN.md's M0.** `ci_rate` caps each
life's diagnosis rate, `claim_rate_life` each life's claim rate, `claim_rate` the policy's
and `claim_rate_paid` the standalone paid rate, each at 1, written `min(q, 1.0)`, the
product first and the bound second, so that a NaN stays NaN where `min(1.0, q)` would read
it as a certain claim; wherever `q` is a number the two are the same float. No shipped rate
comes near a cap, the largest claim rate being 0.0404, the joint point's in its last month,
and `Data` refuses a pivot rate past 1; the product passes 1 through the latch's loading, or the pivots' extrapolation, which a
test shows. The additional-payment and children's benefits take their caps the same way,
`min(share × SA(t), cap)`. The lapse rate's bounds keep `CI_UK_S`'s order,
`min(0.30, w + 2.0 max(0, ρ − 0.05))`: they are no cap on a claim rate.

**Domains `CI_UK_S` leaves unchecked.** `CI_UK_S` raises a Reference to a power, divides
by it, bounds a rate with it or reads it as a share, a loading or a frequency, and checks
none. Off its domain it projects a negative premium, rate or claim with every check
passing, as a trend of −3, an overlap of 3 or a review change of −150% would, or a
complex lapse rate; and a NaN fails every comparison it meets, so that a NaN threshold
closes the latch at a review that changed nothing, and a NaN slope reads as the cap through
the lapse rate's `min`. Here `proj_len()` refuses each Reference off its domain, naming the
point, the Reference, the domain and the value, on every point that reads it:

| Reference | Read on | Domain | Off it |
|---|---|---|---|
| `ci_trend` (τ), `inflation_rate` | every point | a finite number, −1 or more | the factors `(1 + τ)^n` and `(1 + i)^n` are negative, and so the diagnosis rate or the expense they multiply |
| `sel_lapse_ci_loading` (η) | every point | a finite number, −1 or more | a closed latch's factor, `1 + η`, is negative, and so the diagnosis rate |
| `overlap_k` (k), `survival_slip` (δ) | every point | a number from 0 to 1 | the shares of the deaths and of the diagnoses that do not pay make a negative claim, paid or exit rate |
| `ap_freq_factor`, `child_freq` | every point | a number from 0 to 12 | a month's additional payments, `ap_freq_factor × i_ci / 12` with `i_ci` capped at 1, or children's claims, `child_freq / 12`, number more than one per policy in force, or fewer than none |
| `review_period_mths` | a reviewable point | a whole number of months, 1 or more | the reviews divide the policy months by it: at 0 by zero, below it counting reviews backward, off a whole number in parts |
| `review_lapse_cap` | a reviewable point | a number from 0 to 1 | the shock lapse is at most the cap: past 1 its monthly rate, `1 − (1 − w)^(1/12)`, has no real value, which `CI_UK_S` projects as a complex number, and below 0 the window lapses a negative share |
| `review_prem_shock` (ρ) | a reviewable point | a finite number, −1 or more | a review takes the premium below 0 |
| `review_lapse_threshold` | a reviewable point | a finite number | the latch and the window compare a change with it, and a NaN closes the latch at every review |
| `review_lapse_slope` | a reviewable point | a finite number, 0 or more | the window lapses fewer the more the premium rises; at NaN, at the cap |

Each domain is a comparison no NaN passes, and a finite number one of which `x − x == 0`
holds, which an infinity fails too. A guaranteed point reads no review Reference, and
projects whatever they are. The pivot rates, whose ratio the interpolation raises to a
power, are the table's, which `Data` holds above 0 and at most 1. `rpi_rate` reaches the
index factors only through the floor at 0 and the 10% cap, and the indexation's caps and
multiplier, which the contract fixes, are read as `CI_UK_S` reads them.

**The exit rate past 1, refused in its cell.** `check_claim_split_resid` converts the
notes' annual exit rate, `q_exit = q_d (1 − k) + i_ci δ`, independently, to bound the
standalone split's artefact, and `CI_UK_S` caps no part of it, since it is never a
decrement: past 1, which an extrapolated mortality rate reaches above the last pivot with
rates `Data` accepts, the conversion has no real value and `CI_UK_S`'s residual is a complex
number, whose magnitude its check compares without a word. Here the residual raises in the
month `q_exit` first passes 1, naming the point, the month, the rate, the two rates it is
made of and the References, as `Term_UK_SEC`'s waived share raises in the month it leaves 0
to 1. At rates that high the artefact passes the shipped `claim_split_tol` some months
earlier, where the check returns False, as `CI_UK_S`'s does.

## Tests

- **The twin identity**, in `tests/test_model_conventions_uk.py`: on points 1 to 7, every
  cell of `CI_UK_S`'s agrees at every argument `CI_UK_S` evaluates in its own sweep, to
  1e-9 relative with no absolute floor, but for `pols_if_init` and `model_point`, and
  `result_pols`, which the spec names with its reason; a cell this model lacked would fail
  it. So `CI_UK_S`'s worked example, which `tests/test_critical_illness_uk.py` asserts to
  the penny and the in-force to six decimals, holds here with no number restated. The same
  suite holds the model to the conventions every `_SEC` model meets: every frame starts at
  `t = 0`, `pols_if` is the `"BEF_DECR"` count, new business enters once at its
  `policy_count`, nothing happens before issue, and the in-force columns are present. And
  `tests/test_critical_illness_uk_sec.py` compares each twin with S in every cell again,
  with the trend and the review change on in both models, which T1 and the splice, each
  at a trend of 0, cannot: a cell that dropped the trend fails there alone.
- **The splice**, in `tests/test_critical_illness_uk_sec.py`: each `CI_UK_S` point
  restated in force at months 1, 11, 12 and 13 (the first anniversary), 59, 60 and 61 (the
  first review, pivot age 45 on the anchor cell, lapse year 6), 71 and 72 (the shock
  window's end), 119, 120 and 121 (the second review), 239 and 299, continues the S
  projection in every cell the two share but `proj_len`, and in both reports, to 1e-9
  relative with no absolute floor. The review change, which ships at 0, is on in both
  models at 12%, past the shock threshold and apart from the select loading of 10%, so
  that the reviews move premiums, open their windows and close the latch, and a latch or
  a review factor read from the other's value would show; inflation and the trend, the
  inputs on the valuation clock, are 0 in both. A change of 20%, whose shock lapse takes
  the cap, the threshold itself, where no window opens and no latch closes, and the float
  above it, where both do, are spliced on the reviewable point the same way. Four variants of S's points, in a copy of S's table that is never
  committed, reach what S's own cannot: the reviewable point indexed and a male smoker, the
  standalone contract reviewable, the anchor cell issued at 50 with cover of 40,000, whose
  pivots run past the table's last and whose ancillary benefits fall below their caps, and
  the joint point reviewable with a male smoker as its second life. A core of 29 of the 116
  splice cases and 7 of the 20 future ones runs by default, and the full grid with
  `UKLIB_SEC_FULL=1`; a test asserts the core reaches every branch, opening-state column,
  kind of valuation month and side of every `min` and `max` the full grid reaches.
- **Future new business**: issued 1 and 12 months after the valuation date, each S point is
  the S projection moved on, with zeros before issue and no rate evaluated there, and so is
  each variant issued a month on, the reviewable point 13 months on, its reviews a month off
  the valuation years, and the indexed point 25.
- **How it computes**: on every row of the splice's grid, after its reports, its checks
  and every monthly cell at every month, no cell has been called at a negative month, none
  on the books read a month before `t_entry()`, none read a month later than `t + 1`, and
  none raised. On a fresh read of the committed model, `duration_mth(500)` evaluates
  `duration_mth` once, the policy clock being a closed form, and every point's reports and
  checks run under modelx's recursion limit lowered to 40, which a recursion backward over
  the frame would exceed; they pass at 10. And the count's chain, called cold in the last
  month at the contract's longest cover on three shapes, runs one cell a month back to
  `t_entry()` and at most 16 more.
- **Counts**: the roll-forward closes; `result_pols()` is S's report with `pols_new_biz`
  beside it; multiplying `policy_count` by 2.5, with the review change and the trend on,
  multiplies every flow and counted cell and moves no per-policy value, bit for bit, the
  factors, the reviews and the latch among them; and the roll-forward, its tolerance scaled
  by the count, closes on a million policies.
- **Validation and regeneration**: each malformed row of the table, 74 cases, is refused
  naming its point, and naming its label on an extract labelled otherwise than by
  position; the horizon is a Reference; a point past its cover or outside the
  contract's bounds, 14 cases, is refused by `proj_len()`, each bound just inside it and
  each moved past a committed point, and `run_sec.py --block` refuses such a point before
  printing anything; so is a review history before the first review, 4 cases, a review
  factor between the first review and the second that is not 1 plus that review's
  change, 4 cases, accepted at two reviews, and each of twelve References off its
  domain, the value next outside each edge, NaN and both infinities, on every point that
  reads it, where at the edges the twin that reads it is S's in every cell; an exit rate
  past 1 is refused in the month it passes, where S's residual is complex; each
  assumption table a reader cannot read, 22 cases, is refused naming its lines; keys
  written as floats read as `CI_UK_S` reads them; the edges of the interface and of each
  bound are accepted, a review that cut the premium, to 0 at the edge, and the first
  anniversary among them; every state `CI_UK_S` reaches, as shipped, under the splice's
  review change and where the cap binds, is accepted in force; and the committed table
  is what `CI_UK_S` generates.
- **The product's own facts**: the two clocks on the shipped points; the committed rows,
  in force and issued later, continuing their S points at the shipped assumptions but for
  inflation; each history column read, not recomputed, the index factors, the review
  factor, the latch and the window's change, each written off its References' path, on
  a history a policy can have, and projected through; the latch read from its flag, so
  that one closed at a factor of 1, or below it, stays closed through a later shock
  review; the change read inside its window alone; and a review change set at the
  valuation date reaching back over no review already made (UKLIB-SEC-PLAN.md K14);
  expense inflation and the morbidity trend on the valuation clock, which only these tests
  see; the initial expense on new business alone; the reviews and their window on the
  policy clock; every guarded cell's value outside cover; the block; an extract without the
  generator's three columns, labelled otherwise, projecting the same numbers; `run_sec.py`'s
  numbers, for a point, the joint life among them, and for the block, and its sum, and its
  `--cython` stopping where no repository is above it; no cell's parameter defaulted but
  the `claims` total's; the docstrings, read through docutils as the docs build reads them
  where docutils is installed; and the shared input tables.
- **The caps**: on the reviewable point, the anchor cell and the joint point, its second
  life a male non-smoker issued at 42, with the male non-smoker's diagnosis pivots at 60
  and 65 raised to 0.98 and 1.0, in a copy of the table, under the splice's References:
  on the reviewable point the latch's loading takes the diagnosis rate past 1 from
  attained age 60, policy month 240, and with it the claim rates; on the anchor cell the
  claim rate alone passes 1, from attained age 64, policy month 288; and on the joint
  point the second life's claim rate, from its attained age 64, policy month 264. In both
  models the capped rates and the monthly decrement are the float 1.0 there; every policy
  in force at the start of that month claims in it, and none is in force after it; the
  reports hold finite floats; and every cell the two models share agrees, issued now and 12
  months on, and restated in force the month before the cap, to 1e-9 relative with no
  absolute floor. And a NaN sent to a cap, through the overlap, the trend, the latch's
  loading or the survival slippage, or to the RPI's floor and caps or the ancillary
  benefits' caps, stays NaN in the cell, and no check passes a residual that is NaN: the
  frame refuses the Reference first.

```bash
python -m pytest tests/test_critical_illness_uk_sec.py -q
UKLIB_SEC_FULL=1 python -m pytest tests/test_critical_illness_uk_sec.py -q   # the full grid
python -m pytest tests/test_model_conventions_uk.py -q -k CI_UK_SEC
```

<!-- BEGIN generated citation links -- regenerate with tools/gen_citation_links.py -->
[R8]: #uklib-critical_illness-r8
[std]: #uklib-std
<!-- END generated citation links -->
