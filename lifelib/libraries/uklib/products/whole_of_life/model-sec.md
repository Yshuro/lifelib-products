# In-Force Implementation Notes

**Status:** Draft, 2026-11-23. `WOL_UK_SEC` is [`WOL_UK_S`](model.md) taught to project
from a valuation date. Besides policies issued at that date, it takes policies already in
force there, in any month of their policy year, on full cover or paid-up, and policies to
be written in the ten years after it, as lifelib's `basiclife/BasicTerm_SE` extends
`basiclife/BasicTerm_S`. The product is the one [`product-spec.md`](product-spec.md)
specifies and [`technical-notes.md`](technical-notes.md) models; this page says what
running in force changes. The suffix adds lifelib's letters to `S`: `E` for in force, as in
`BasicTerm_SE`, and `C` for the compiled form, as in `basiclife/BasicTerm_SC`, which the
model's next step adds (UKLIB-SEC-PLAN.md U2). Until then it runs in modelx alone.

> **This is a mechanics demonstration, not a pricing or reserving result.** The model is
> `WOL_UK_S` on another time axis, and it reads `WOL_UK_S`'s assumption tables in place,
> every assumption unchanged: the contractual mechanics are sourced, and every rate is a
> **[std]** standardization, the two mortality bases proxies shaped like the tables the
> notes name, whose current editions are restricted to the CMI's Authorised Users
> [REG-R22] [R7]. Replace them with licensed tables and company experience before drawing
> any conclusion from the numbers.

## Run it

```bash
python products/whole_of_life/run_sec.py            # point 1: the anchor cell, issued at t = 0
python products/whole_of_life/run_sec.py 10         # point 10: the paid-up point in force 200 months
python products/whole_of_life/run_sec.py --block    # every model point, summed row by row
```

The first prints the twelve rows `run.py` prints for `WOL_UK_S`'s point 1, with the policy
counts behind them. Three lines to the same thing for point 10:

```python
import modelx as mx
model = mx.read_model("products/whole_of_life/WOL_UK_SEC")
model.Projection[10].result_cf()
```

`Projection` takes a `point_id`, as `WOL_UK_S`'s does; it will take `idx`, a point's
position in the table, once the model compiles, and the runner takes its key from the
model either way. `result_cf()` has `WOL_UK_S`'s columns — `pols_if`, `pols_pu`,
`premiums`, `claims_death`, `claims_death_pu`, `claims_lapse`, `expenses`, `commissions`
and `net_cf` — with one row per month from the valuation date, `t = 0 … proj_len() − 1`.
`result_pols()` sets out the counts behind it on the same rows, on both strands:
`pols_if`, `pols_new_biz`, `pols_pu`, then the month's deaths on full cover and paid-up,
its lapses and conversions to paid-up in processing order, the survivors at the limiting
age, and `WOL_UK_S`'s other five columns, the premiums paid, the cover, the benefit per
death and the annual mortality and lapse rates.

`--block` projects every point and releases its ItemSpace once its frame is read, so the
run holds the cells of one point at a time. Deleting it, `del model.Projection[10]`, is not
enough: an ItemSpace sits in reference cycles, which only Python's cyclic collector frees,
so the runner collects after each release. It freezes everything alive (`gc.freeze()`)
once the model and its table are read, and again once it has asked every point for its
frame, so that each collection scans only what the block has made since. It keeps the
block's sum as it goes, compensated as pandas sums a `groupby`, so that the block is, bit
for bit, the frames concatenated and summed by `t`. Its projection years carry the counts
of their first month, on full cover and paid-up, and the flows of all twelve.

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
  date to the limiting age.
- **`duration_mth(t)`, the policy clock**, counts the months the policy has been in force
  at time `t`: `duration_mth(t) = duration_mth_init() + t`, with `duration_mth_init()` read
  from the model point. The contract runs on it: `duration(t) = duration_mth(t) // 12`,
  `policy_year(t) = duration(t) + 1`, the lapse table's key, and
  `age(t) = age_at_entry() + duration(t)`, the mortality table's, age last birthday, as in
  `WOL_UK_S`. Whole of life has no maturity, so cover runs to the limiting age, policy month
  `limit_mth() = 12 × (omega_age − age_at_entry())`, `WOL_UK_S`'s frame from issue.
  `BasicTerm_SE` reaches the same numbers by adding one a month, a recursion as long as the
  frame; the closed form needs no such chain of calls.

Point 10 is the pro-rata paid-up point in force 200 months. At `t = 0` it is in policy year
17 at attained age 86, with 0.180202 policies on full cover and 0.057170 paid-up, and its
frame has 400 rows, `t = 0 … 399`; `WOL_UK_S` projects the same months as its rows 200 to
599. Point 14 is the RPI point to be issued 13 months after the valuation date:
`duration_mth(0) = −13`, it is on the books from `t_entry() = 13`, rows 0 to 12 are zeros,
and its frame has 613 rows.

| Read on the policy clock | Read on the valuation clock |
|---|---|
| the mortality table at the attained age; the lapse table by policy year; the over-50s moratorium and the underwritten suicide window, each the first twelve policy months; the escalation on each policy anniversary; premium cessation, and with it the end of lapses; the payments made that the pro-rata paid-up value counts; the first year's commission; the crossover; the limiting age | expense inflation, `inflation_factor(t) = 1.03^(t // 12)`; mortality improvement, `mort_improve_factor(t) = (1 − r)^(t // 12)` |

Expense inflation and mortality improvement run on `t`, stepping on each anniversary of
the valuation date, for every point alike (USLIB-SEC-PLAN.md D7; UKLIB-SEC-PLAN.md §9
item 4). The maintenance charge is then in valuation-date pounds, and the mortality tables
state their basis at the valuation date, improved from there: `WOL_UK_S` improves from
issue, which on a point in force would improve a table stated today by the years the
policy has already run. Improvement ships at 0, where the two clocks agree. The RPI is a
flat Reference, the rate assumed from the valuation date on. The acquisition expense,
£150 or £300 per policy issued, is charged in the issue month and not inflated, as in
`basiclife/BasicTerm_SE`.

Because row `t` is the same month for every point, the frames of a block line up and sum
row by row, which is what `run_sec.py --block` prints:

```python
import pandas as pd
frames = [model.Projection[p].result_cf() for p in model.Data.model_point_table().index]
block = pd.concat(frames).groupby(level="t").sum()
```

On a point issued at `t = 0` the two clocks coincide, and the model computes what
`WOL_UK_S` computes: every cell the two models share agrees, but two whose meaning changed,
`pols_if_init()`, now the count already in force at the valuation date, 0 for new
business, and `model_point()`, a row of another table. `WOL_UK_S` charges the acquisition
expense on the count in force at `t = 0`, which on such a point is the count issued, so
the two agree at any count.

## The in-force interface

The model point table is `model_point_table_sec.csv`. It carries `WOL_UK_S`'s columns, one
of them restated as the in-force interface under `basiclife/BasicTerm_SE`'s name, a policy
clock column, a second count and five columns of opening state. The two counts are the
only weights on the flows, and every state column is per policy. Each is measured at the
valuation instant, the start of month 0, before any month-0 event (USLIB-SEC-PLAN.md D6).
An anniversary that falls at the valuation date is month 0's event, the projection's
first: the cover and premium columns hold the policy year it closes, and its increase is
made at `t = 0` at today's References, as a fixing at month 0 reads the assumptions of the
valuation date (D6, as precised at uslib's M7). Each state column is history: what the contract has given, charged or converted, never re-derived from a
Reference, which is an assumption from the valuation date on, so that a Reference changed
there reaches back over no increase, premium or conversion already made
(UKLIB-SEC-PLAN.md K14, §9 item 5):

| Column | Unit | Measured at | Meaning |
|---|---|---|---|
| `policy_count` | policies on full cover, not necessarily whole | for a point in force, the start of month 0, before any month-0 event; for any other, its issue month | the policies on full cover in force at the valuation date, for a point already in force, 0 if it is paid-up entirely; the policies issued, for one issued at or after it |
| `duration_mth` | whole months | the valuation date | the policy's age in months: positive in force, 0 for a policy issued at the valuation date, `−k` for one to be issued `k` months later, with `k` at most 120 as shipped |
| `pols_pu_init` | paid-up policies, 0 or more | the start of month 0 | the policies already converted to paid-up by the pro-rata paid-up value, the second strand's count |
| `pu_benefit_pp_init` | pounds per paid-up policy | the start of month 0 | the paid-up cash sum each carries on average: each policy's `SA × N_paid / N_expected` at the month it converted, averaged over the strand |
| `prem_cum_pp_init` | pounds per policy on full cover | the end of month −1, before month 0's premium | the premiums paid since issue, which the moratorium and suicide refunds pay back and the crossover stress compares with the cover |
| `cover_pp_init` | pounds | the start of month 0, before its events: the policy year of month −1, which on an anniversary is the year it closes | the cash sum in force, after every increase the RPI or the fixed step has already given |
| `premium_pp_init` | pounds a month | as `cover_pp_init` | the premium of that policy year, after every increase already given; once premiums have ceased, the last premium paid |
| `crossover_mth_init` | a policy month, or −1 | the valuation date | the policy month the premiums paid first exceeded the cover, if that was before the valuation date, and −1 if it was not: a crossover in month 0 or later is the projection's |

`WOL_UK_S` holds none of them. It rebuilds the cover and the premium from issue at one
flat `rpi_rate`, or at `esc_fixed_cover`, `esc_fixed_prem` and `esc_take_up`; the
premiums paid by summing that schedule; the paid-up strand by converting every would-be
lapse since its halfway point at today's lapse table and crossover stress; and the
crossover by searching that schedule from issue. On a point in force those are facts of
the contract: an RPI set at the valuation date would reprice increases long given and move
a crossover already past, a take-up would reach back over increases already taken up or
declined, and a stress would convert lapses long past. Here an increase after the
valuation date steps at today's References, and one at or before it is the history the
columns carry:

- `cover_pp(t)` and `premium_pp(t)` open at `cover_pp_init()` and `premium_pp_init()` and
  take `1 + step` for each anniversary since the columns' year, `duration(t) −
  duration_init()`, `duration_init()` being the policy years of month −1, so that an
  anniversary at the valuation date steps them at `t = 0`;
- `prem_cum_pp(t)` opens at `prem_cum_pp_init()` plus month `t_entry()`'s premium and adds
  each month's after;
- `pols_pu(t)` and `pu_benefit(t)` open at `pols_pu_init()` and at
  `pols_pu_init() × pu_benefit_pp_init()`, and take in each month's conversions;
- `crossover_mth()` reports `crossover_mth_init()` where the crossover fell before the
  valuation date, and otherwise searches forward from it, the premiums paid accumulating
  from `prem_cum_pp_init()` and the premium and cover stepping from the columns.

The fixed variant carries its cover and premium columns as the RPI one does: its increases
are a fixed 5% and 10%, but at the take-up of their day. And the paid-up strand needs no
history of when its policies converted: paid-up policies neither lapse nor escalate, so the
count and the summed cover roll forward on the same survival factor, and the average is all
the strand needs.

On a point issued at the valuation date each history column holds its issue value, and the
model is `WOL_UK_S`. A model that dropped the columns and recomputed them from the
References would pass the splice, since `WOL_UK_S` and the splice recompute them alike, so
the tests write each off its References' path and project through it.

The crossover is reported, and no cell of the projection reads it: the crossover stress
compares the premiums paid with the cover month by month. Carried back from the columns at
today's increases, as the model first did, it was wrong wherever the history ran
otherwise: the RPI point restated after a crossover at 166 under an RPI of 0 reported 166,
150 and 137, and one at 201 under 8% reported 220. As a column it is the history's.

Nothing else is history `WOL_UK_S` rebuilds from a Reference: commission is paid in the
first policy year alone, on the premiums of that year still to come, with no clawback; the
acquisition expense falls at issue; the moratorium and the suicide window read the
premiums paid; and inflation and improvement run from the valuation date.

| `WOL_UK_S` | `WOL_UK_SEC` | Why |
|---|---|---|
| `pols_if_init` (1.0) | `policy_count` | The full-cover count, under BasicTerm_SE's name. `pols_if_init()` now means the count in force at the valuation date, 0 for a point issued at or after it |
| — | `duration_mth` | The policy clock, in months, any month of a policy year; every `WOL_UK_S` point is new business |
| — | `pols_pu_init`, `pu_benefit_pp_init` | The paid-up strand in force; `WOL_UK_S` builds it from issue at today's lapse table and stress |
| — | `prem_cum_pp_init`, `cover_pp_init`, `premium_pp_init`, `crossover_mth_init` | `WOL_UK_S` rebuilds each from issue at its References: the premiums from the schedule, the increases from `rpi_rate` or the fixed step and the take-up, and the crossover by searching both |

The columns carried over are read as `WOL_UK_S` reads them. For a policy in force, the
facts they record are still those at issue:

| Column | Unit | Measured at |
|---|---|---|
| `point_id`, `policy_id` | labels | — |
| `cell`, `sex`, `smoker`, `escalation` | codes, as in `WOL_UK_S`'s table | issue |
| `entry_age` | years, age last birthday | issue, not the valuation date: `age(0)` is the attained age there |
| `sum_assured`, `premium_mth` | pounds, the amounts at issue | issue: on an escalating point the month's cover and premium step from `cover_pp_init` and `premium_pp_init` |
| `cessation_months`, `moratorium_months` | whole policy months | issue: counts on the policy clock, 0 for premiums for life or no moratorium |
| `variant_adb_2x`, `variant_paid_up` | True or False | issue |

Three more columns, `row_kind`, `source_policy_id` and `source_mth`, record where the
generator took each shipped row from (below). No formula reads them, and an in-force
extract need not carry them: without them the model projects the same numbers, and
`run_sec.py` runs.

`Data.model_point_table()` checks the table as it reads it, over all rows at once. The
first check that fails raises `ValueError`, naming the missing column or every point that
fails it: the eight in-force columns are present; no `point_id` appears twice;
`policy_count` is a number, zero or more; `duration_mth` is a whole number of months,
below `2**53`, and −120 or more, future new business being written over a horizon,
`Data.future_horizon_mth`, 120 months as shipped, itself a whole number of months below
`2**53`, which set to 0 refuses future new business altogether; each state column is a
number, zero or more, and the crossover a whole number of months, −1 or more; each flag is
True or False; each code is one `WOL_UK_S` knows, the smoker status `NS` or `S`, not term
assurance's `N`; the entry age is a finite number, the amounts zero or more and the month
counts whole, 0 or more; and a pro-rata paid-up point has a premium cessation date, which
its paid-up value is measured to. Then the history: a point not yet in force holds the
issue values, no paid-up policy, no paid-up cover, no premium paid and no crossover, the
sum assured and the premium at issue; a point in force 12 months or fewer holds the issue
cover and premium, its columns its first policy year's, the first anniversary's increase
being the projection's; a level point holds them always, and an escalating one those or more, each increase floored at 0; the paid-up strand
is empty without the variant, and before the earliest policy month a converted policy can
be in force at, half of `cessation_months` rounded up; and the paid-up cover per policy is
0 where no paid-up policy is in force. The amounts are held to the contract, to the cent,
within half a cent of each bound, so that an extract rounded to the cent reads:

- the premiums paid are the premiums due so far, `min(duration_mth, cessation_months)`, or
  `duration_mth` for life, times the premium at issue on a level point, and on an
  escalating one between that and the same count times `premium_pp_init`, the latest
  premium, each increase being floored at 0;
- where paid-up policies are in force, the paid-up cover per policy lies between the sum
  assured times the payments a conversion needs, half of `cessation_months` rounded up,
  and `cover_pp_init` times the payments made, each over `cessation_months`;
- a crossover before the valuation date fell in a premium-paying month before it; there
  was one where the premiums paid exceed the cover; and on a level point it is the month
  the contract puts it in, `P × t* ≤ SA < P × (t* + 1)`.

Each holds of every state `WOL_UK_S` reaches, as shipped, under the splice's stress,
under one that lapses every policy, under an RPI of 8% and under a take-up of a half,
which a test asserts. `WOL_UK_S` meets most of these only when a projection reaches them, and some
never: a blank flag reads as True, and one stray word in a flag column turns every `False`
in it to text that reads as True.

A point at or past the limiting age at the valuation date, `duration_mth ≥ limit_mth()`,
reads, but `proj_len()` refuses it, naming the point: the limiting age is the product's
rule, keyed on the policy clock, not the table's. So does a point the contract does not
write ([`product-spec.md`](product-spec.md)): one issued below 18,
`Projection.issue_age_min`, the youngest age the mortality table rates and the product
issues at, or at or past the limiting age, `omega_age`, which itself must lie above
`issue_age_min` and at most a year past the mortality table's last age. Each is a
lower-case Reference, the contract a compiled model's caches will be sized from: a frame
of at most 1,236 months, from 18 to the largest `omega_age` it accepts, 121, and the
horizon, and attained ages from 18 to 120 on the mortality table. A whole limiting age
written as a float, `120.0`, is read as the `int` it is, so that the frame is a whole
number of months, as it will be compiled. On every point `proj_len()` also refuses a Reference off its domain
(below). The References are the projection's, which `Data` cannot read. A loop over the
block meets such a row only when it reaches it, after projecting the points before it, so
`run_sec.py --block` asks every point for its frame before it projects any, and stops
before it prints anything.

The assumption tables are checked before a value of them is read, each by the cell the
projection takes its extent from, reading the file as it stands, so that a fault is named
by its line. The mortality table is checked by `Data.mort_age_first`: each age a whole
number, each basis `population` or `assured`, sex `M` or `F` and smoker `NS` or `S`, each
of the eight groups running from the table's first age to its last, one row an age, none
below 0, and each rate from 0 to 1. The lapse table is checked by `Data.lapse_last_year`:
policy years from 1 without a gap or a repeat in each cell, each cell `O50` or `UW`, each
rate from 0 to 1. A key is read by its value, so an age written `70.0` is 70. Each refusal
names the file, the column and its lines. An attained age outside the mortality table,
which only a lowered `issue_age_min` admits, is refused by `mort_rate`, naming the point
and the age, where `WOL_UK_S`'s lookup raised `KeyError`.

## The model points

No row of `model_point_table_sec.csv` is typed by hand. Every one is generated from
`WOL_UK_S` and its table by `tests/uk_sec_support.py`, from the `WOL_UK_SEC` entry in its
`SEC_SPECS`, and the tests regenerate it and compare, so an edit to a `WOL_UK_S` row reaches
it or fails the suite. In the source repository, `python tools/gen_sec_points.py WOL_UK_SEC`
writes it.

| Point | Kind | From | At the valuation date |
|---|---|---|---|
| 1 to 7 | twin | S points 1 to 7 | issued at `t = 0`: `WOL_UK_S`'s worked example and its variants, the over-50s anchor cell, with the double accidental benefit, with the pro-rata paid-up value and with RPI increases, the underwritten cell, with fixed increases, and an over-50s male smoker |
| 8 | derived | S point 1 at S month 6 | the anchor cell inside its moratorium, £180 of premiums paid |
| 9 | derived | S point 1 at S month 166 | the anchor cell in its crossover month, £4,980 paid |
| 10 | derived | S point 3 at S month 200 | the paid-up point with its strand in force, each paid-up policy carrying £3,294.64 |
| 11 | derived | S point 4 at S month 186 | the RPI point past its crossover, its cover £7,789.84 and premium £58.06 |
| 12 | derived | S point 6 at S month 12 | the underwritten increasing point on its first anniversary, its columns the first year's and its first increase at `t = 0` |
| 13 | derived | S point 7 at S month 300 | the male smoker as its premiums cease |
| 14 | future | S point 4, 13 months on | to be issued at `t = 13` |
| 15 | derived | S point 4 at S month 120, `WOL_UK_S` run under an RPI of 5% | the RPI point with a cover of `5,000 × 1.05^9` and a premium of `30 × 1.075^9`, its tenth anniversary's increase at `t = 0` |
| 16 | derived | S point 6 at S month 120, `WOL_UK_S` run under a take-up of 0.5 | the underwritten increasing point with increases of 2.5% on the cover and 5% on the premium |
| 17 | derived | S point 3 at S month 180, `WOL_UK_S` run under a crossover stress of 100 | the paid-up point paid-up entirely: `policy_count` 0, and 0.285193 paid-up policies |

A derived row's `policy_count` is the count `WOL_UK_S` carries into that month on full
cover, its `pols_if(d)`, and its state what S carries there, so the row continues the S
projection from there: point 10 opens with 0.180202 policies on full cover, 0.057170
paid-up and £6,000 of premiums paid. At the shipped References the escalating rows'
history is what today's References rebuild, and no shipped point is paid-up entirely, so
three rows are read from `WOL_UK_S` run under References of their own, which the spec's
`derived_refs` records: points 15 to 17. Points 15 and 16 are valued on their tenth
anniversary, so at the shipped References they make its increase at `t = 0` at today's
References and part from `WOL_UK_S` under theirs there, their counts S's throughout; point
17, with no full cover for its stress to lapse, projects `WOL_UK_S` under its stress
throughout, but in the lapse rates themselves, which weight no policy. A test asserts each.
A derived row's `policy_id` is the S row's with the month appended, `WOL-000003-M200`, and a future row's carries the months to issue,
`WOL-000004-F13`. Row `t` of a generated point is month `t + source_mth` of its S point.

## Counts and timings

`pols_if_init()` is the full-cover count in force at the valuation date: `policy_count` for
a point already in force, 0 for any other. `pols_new_biz(t)` is `policy_count` in the issue
month, the month with `duration_mth(t) = 0`, and 0 in every other; every policy issued
starts on full cover. `pols_if_at(t, timing)` keeps `WOL_UK_S`'s three timings and adds
`basiclife/BasicTerm_SE`'s `"BEF_NB"`:

- `"BEF_NB"`, the count carried in from month `t − 1`, before month `t`'s new business:
  `pols_if_init()` at `t_entry()`, the first month on the books, and the survivors of
  month `t − 1`'s deaths and would-be lapses after it;
- `"BEF_DECR"`, that count plus `pols_new_biz(t)`, before month `t`'s decrements, which
  `pols_if(t)` returns;
- `"BEF_LAPSE"`, after the month's deaths, before its lapses;
- `"AFT_DECR"`, the end of the month, after its deaths and lapses, which is `"BEF_NB"`
  at `t + 1` exactly, and 0 from the last month before the limiting age on.

Any other timing raises. The survivors carried into month `t` are those of month `t − 1`'s
`"BEF_DECR"` count, which `"BEF_NB"` forms itself, as its own value at `t − 1` plus that
month's new business, exactly the sum `"BEF_DECR"` returns. So the chain of calls from
month `t` back to `t_entry()` is one cell a month, as `WOL_UK_S`'s own `pols_if`
recursion is from issue.

The paid-up strand runs beside it. `pols_pu(t)` opens at `pols_pu_init()` at `t_entry()`
and rolls forward on mortality alone, taking in each month's conversions; `pu_benefit(t)`,
the strand's summed cover, opens at `pols_pu_init() × pu_benefit_pp_init()` and takes in
each conversion at its own paid-up value, `benefit_pp(t, "PAID_UP")`. Each is one cell a
month, and so are the premiums paid, `prem_cum_pp(t)`, from `prem_cum_pp_init()`: the
model's four chains. The cover, the premium and the improvement are closed forms on their
clocks. On a model just read, a cold `net_cf` in the last month runs 9 or 10 cells deeper
than one a month, and the paid-up chains 10 or 11, at the contract's longest cover, 1,224
months from issue age 18, issued now and 120 months on, on the anchor, paid-up, RPI and
underwritten increasing shapes alike.

`pols_all(t) = pols_if(t) + pols_pu(t)` carries the maintenance expense, a paid-up policy
costing money to administer though it pays no premium, and the roll-forward, which closes
as

```
pols_all(t) − (pols_if_at(t + 1, "BEF_NB") + pols_pu(t + 1))
    = pols_death(t) + pols_death_pu(t) + pols_lapse(t) + pols_maturity(t)
```

at every `t` of every frame, and `pols_all(t + 1)` adds `pols_new_biz(t + 1)` to the counts
on the left. Conversions move policies between the strands and out of neither: the
full-cover count loses its deaths, its terminating lapses and its conversions, and the
paid-up count loses its deaths and gains the conversions. `pols_maturity(t)`, the survivors
in the last month before the limiting age, policy month `limit_mth() − 1`, is the
truncation residual, which pays nothing; `check_truncation()` asserts it is negligible.
Both checks scale their tolerance with the policies on the books, `policy_count() +
pols_pu_init()`, on both strands.

Cover is `is_active(t)`, `0 ≤ duration_mth(t) < limit_mth()`, and outside it, before issue
and from the limiting age on, every count on both strands is zero, and so every cash flow.
No count evaluates a rate there, and no table is read at a policy year or an attained age
the policy does not have: `mort_rate`, `lapse_rate_base`, `lapse_rate`, the cover, the
premium, the premiums paid, the benefits, the payments made, the moratorium and the paid-up
eligibility are zero or false outside cover, before any table or rate is read.

## Departures from WOL_UK_S

Each formula that tested `t` against a contractual event now tests the policy clock, and
each recursion opens at `t_entry()` from the opening state. Where `WOL_UK_S`'s test would
have stayed correct on the valuation clock, it moved anyway, so that cover has one
definition. Thirteen cells are new — `policy_count`, `duration_mth_init`, `duration_init`,
`t_entry`, `is_active`, `limit_mth`, `pols_new_biz` and the six accessors of the opening
state — and none of `WOL_UK_S`'s 61 is gone. One Reference is new, `issue_age_min`.

| Cells | `WOL_UK_S` | `WOL_UK_SEC` | Why |
|---|---|---|---|
| `duration_mth`, `duration` | `t`, `t // 12` | `duration_mth_init() + t`, `duration_mth(t) // 12` | The policy clock, opened from the model point |
| `proj_len`; `limit_mth`, new | `12 × (omega_age − entry_age)`, from issue | `limit_mth() − duration_mth_init()`, from the valuation date, `limit_mth()` reading `omega_age` as an `int`; raises at or past the limiting age, outside the contract's bounds and on a Reference off its domain | The frame starts at the valuation date; a whole float, `120.0`, makes the frame 120 does |
| `pols_if`, `pols_if_at`, `pols_if_init` | `pols_if` a recursion of its own, one cell a month, from the column's 1.0 at `t = 0`, which the timings read | `pols_if` is `"BEF_DECR"`, the `"BEF_NB"` chain plus the month's new business, one cell a month from `t_entry()`; `pols_if_init()` is 0 unless in force | Policies in force at the valuation date open the count; new business joins it in its issue month |
| `pols_pu`, `pu_benefit` | from 0 at `t = 0` | from `pols_pu_init()` and `pols_pu_init() × pu_benefit_pp_init()` at `t_entry()` | The paid-up strand in force is history |
| `cover_pp`, `premium_pp`; `duration_init`, new | `SA` and `P` times `(1 + step)^(t // 12)` | `cover_pp_init()` and `premium_pp_init()` times `(1 + step)` for each anniversary since the columns' year, an anniversary at the valuation date the first; a value past the floats refused in its month | The increases already given are history, and one at month 0 is the projection's, at today's References |
| `benefit_pp`, `pu_benefit`, `premiums`, `claims`, `expenses`, `commissions`, `net_cf` | unchecked | a value past the floats refused in its month, naming the point and what makes it | An expense of 1.7e308 inflated at 100% a year, each in its domain, made `WOL_UK_S`'s expenses infinite at `t = 48` with every check passing |
| `prem_cum_pp` | the schedule summed from `t = 0` | from `prem_cum_pp_init()` at `t_entry()`; past the floats refused | The premiums already paid are history |
| `premium_pp`, `lapse_rate`, `in_moratorium`, `payments_made`, `benefit_pp` | cessation, the moratorium, the suicide window and the payments made on `t` | each on `duration_mth(t)` | A contractual event falls on a policy month |
| `crossover_mth`; `crossover_mth_init`, new | a search over `t` to cessation, reading `prem_cum_pp(t)` and `cover_pp(t)` | `crossover_mth_init()` where it fell before the valuation date; else one loop forward from the valuation date on the contractual schedule, from the opening state; `proj_len()` asked first | A crossover already past is history; a policy month passed as `t` would be negative before the valuation date; and the frame's refusals hold here too |
| `mort_improve_factor` | `(1 − r)^(y − 1)`, from issue | `(1 − r)^(t // 12)`, from the valuation date | Improvement on a basis stated at the valuation date |
| `inflation_factor` | `1.03^(y − 1)`, from issue | `1.03^(t // 12)`, from the valuation date | Unit costs in valuation-date pounds |
| `expenses` | the acquisition expense on `pols_if(t)` at `t = 0` | on `pols_new_biz(t)` | A point in force bears none, one issued later bears it in its issue month, per policy issued and not inflated, as in `basiclife/BasicTerm_SE` |
| `commissions` | in policy year 1, `t < 12` | in policy year 1 on the policy clock | A point valued in its first year pays the rest of that year's commission |
| `mort_rate`, `lapse_rate_base`, `lapse_rate`, `benefit_pp`, `claims`, `payments_made`, `pu_eligible`, the counts | the rates and benefits unguarded, the two strands zero outside `0 ≤ t < proj_len()`: no `WOL_UK_S` frame has a month outside cover | zero outside cover, before any table or rate is read; an age past the table refused by name; the lapse table's extent from `Data` | Before issue `WOL_UK_S` reads the mortality table at ages the policy never has, or raises `KeyError` below its first, and raises `KeyError` on the lapse table, which has no policy year 0 |
| `pols_maturity`, `"AFT_DECR"` | at `t = proj_len() − 1` | at `duration_mth(t) = limit_mth() − 1` | One definition of cover, on the policy clock |
| `check_pols_roll_fwd_resid` | `pols_all(t + 1)` | `pols_all(t + 1) − pols_new_biz(t + 1)` | The next month's new business is no part of month `t`'s movement |
| `check_pols_roll_fwd`, `check_truncation` | `1e-10` and `1e-9` times `max(pols_if_init(), 1)` | times `max(policy_count() + pols_pu_init(), 1)` | `pols_if_init` is 0 on new business here, and the paid-up strand rounds too |
| `result_cf` | `range(proj_len())`, from issue | `range(proj_len())`, from the valuation date | Row 0 is the valuation month |
| `result_pols` | `WOL_UK_S`'s ten columns | `pols_new_biz`, `pols_death_pu` and `pols_maturity` added; the rates 0 outside cover | The counts behind `result_cf()` on both strands, after `basiclife/BasicTerm_SE`'s `result_pols()` |

Of the cash flows, the change of clock moves the maintenance expense alone at the shipped
assumptions, and `net_cf` with it, improvement shipping at 0. Point 12 carries that expense
in valuation-date pounds, so its `expenses(t)` is `WOL_UK_S`'s `expenses(12 + t)` divided
by `1.03`. Its `pols_if`, `premiums`, the claims columns and `commissions` are `WOL_UK_S`'s
from month 12 on. Point 14 is `WOL_UK_S`'s point 4 thirteen months on in those columns too;
its maintenance expense is `1.03^(t // 12 − (t − 13) // 12)` above S's at each `t`, and its
acquisition expense £150 exactly.

**The caps, as `WOL_UK_S` has them since UKLIB-SEC-PLAN.md's M0.** `mort_rate` caps the
annual mortality rate at 1, written `min(q, 1.0)`, the product first and the bound second,
so that a NaN stays NaN where `min(1.0, q)` would read it as certain death; wherever `q` is
a number the two are the same float. The shipped tables reach 1 in the tail, so the cap
binds on `WOL_UK_S`'s own points: on the anchor cell from attained age 110, policy month
480, where the population rate times the loading of 1.2 passes 1; on the male smoker from
101, policy month 432; and on the underwritten cell from 114, policy month 888. The RPI
steps take their floor and caps the same way, `min(max(rpi, 0.0), cap)`. The lapse rate's
bound keeps `WOL_UK_S`'s order, `min(1.0, w)`: it is no cap on a mortality rate, and the
stress and the table that feed it are held to domains no NaN is in.

**Improvement and the limiting age.** Improvement lowers every mortality rate, and the cap
with it, and carries survivors to the limiting age, which `check_truncation()` measures. At
0.2% a year it holds on every committed point, the largest residual 4.1e-12 of a policy;
at 0.4% it gives way on three underwritten points, and at 1% the underwritten twins hold
7.1e-6 of a policy at age 120. The tests switch improvement on at 0.2%, and record where it
gives way.

**Domains `WOL_UK_S` leaves unchecked.** `WOL_UK_S` raises a Reference to a power, bounds
a rate or an increase with it, or reads it as a share, a loading, a factor or an amount, and
checks none. Off its domain it projects a negative rate, benefit or expense with every
check passing, as an accidental share of 2, a mortality loading of −1 or an expense of −50
would. And a NaN fails every comparison it meets: a NaN cover cap is lost through the
`min` it bounds, written with the bound second; a NaN stress is switched off by its
comparison with 0; a NaN suicide window closes; and a NaN limiting age refuses nothing and
sizes no frame. An RPI of +∞ reads as the 10% cap, and one of −∞ as no increase. Here
`proj_len()` refuses each Reference off its domain, naming the point, the Reference, the
domain and the value, on every point, as a model-wide assumption:

| Reference | Domain | Off it |
|---|---|---|
| `issue_age_min`, `omega_age` | a whole number below `2**53`; the first 0 or more, the second above the first and at most a year past the mortality table's last age | a NaN bound refuses nothing and an infinite one bounds nothing, where the compiled caches will be sized from them; past the table the frame reads an age it lacks |
| `mort_loading_o50`, `mort_loading_uw` | a finite number, 0 or more | a negative rate, or certain death at an infinity, through the cap |
| `mort_improvement` | a finite number, 1 or less | the factor `(1 − r)^n` changes sign each year |
| `acc_share`, `suicide_share` | a number from 0 to 1 | the shares blend two benefits, and outside them make a negative one or one past the cover |
| `suicide_mths` | a whole number of months below `2**53`, 0 or more | the window compares a policy month with it, and a NaN closes it |
| `rpi_rate` | a finite number | an infinity reads as the cap or as no increase, through the floor at 0 and the cap |
| `esc_rpi_cover_cap`, `esc_rpi_prem_cap`, `esc_rpi_prem_mult` | a finite number, 0 or more | an increase is a cut; a NaN cap is lost through `min` |
| `esc_fixed_cover`, `esc_fixed_prem` | a finite number, 0 or more | the source defines increases only |
| `esc_take_up` | a number from 0 to 1 | the share of each increase taken up: below 0 an increase is a cut, and past 1 more than the contract gives |
| `lapse_crossover_beta` | a finite number, 0 or more | a negative stress lowers lapses past the crossover, and an infinity reads as a certain lapse through the rate's `min` |
| `inflation_rate` | a finite number, −1 or more | the inflation factor changes sign each year |
| `expense_acq_o50`, `expense_acq_uw`, `expense_maint_o50`, `expense_maint_uw`, `comm_init_rate` | a finite number, 0 or more | an expense is income |

Each domain is a comparison no NaN passes, a finite one bounded by the largest float, and
a whole number one of which `x == x // 1` holds below `2**53`, which an infinity fails, and
each Reference is printed as the compiled model will type it, the three integers through
`int()` once whole and every other through `float()`. `Data.future_horizon_mth` is held to
a whole number of months, 0 or more, by `Data` itself, as it reads the table.

**Values past the floats, refused in their cell.** From an opening state and References
each in its domain, an increase can take the cover or the premium past the largest float,
a premium the premiums paid, a multiple or a share of the cover a benefit or the paid-up
cover, a count an amount, an inflation rate an expense, a commission rate a commission,
and the flows' sum the net cash flow, where `WOL_UK_S` would pay an infinite claim, charge
an infinite expense or compare an infinite total, every report infinite and its checks
NaN or passing. Here `cover_pp`, `premium_pp`, `prem_cum_pp`, `benefit_pp`, `pu_benefit`,
`premiums`, `claims`, `expenses`, `commissions` and `net_cf` each raise `ValueError` in
the month its value first leaves the floats, naming the point, the month and what makes
it.

A power is different. modelx runs a formula as Python does, and Python's float `**` raises
`OverflowError`, with the platform's own message, "Numerical result out of range" on
Linux, where its result would pass the largest float, before the cell can look at it. So
the cover's and the premium's step to the policy years since the valuation date, the
inflation and improvement factors and the crossover's search, each raised from a step in
its domain but large enough, `1e200`, are refused by Python's error, which names neither
the point nor the Reference, and a test holds that. The compiled model's `pow` returns an
infinity there instead, so its C step takes uslib's M22 form for these five powers,
Python's own float power where the compiled one gives an infinity, so that both engines
raise the same error.

## Tests

- **The twin identity**, in `tests/test_model_conventions_uk.py`: on points 1 to 7, every
  cell of `WOL_UK_S`'s agrees at every argument `WOL_UK_S` evaluates in its own sweep, to
  1e-9 relative with no absolute floor, but for `pols_if_init` and `model_point`, and
  `result_pols`, which the spec names with its reason; a cell this model lacked would fail
  it. So `WOL_UK_S`'s worked example, which `tests/test_whole_of_life_uk.py` asserts to the
  penny and the in-force to five decimals, holds here with no number restated. The same
  suite holds the model to the conventions every `_SEC` model meets: every frame starts at
  `t = 0`, `pols_if` is the `"BEF_DECR"` count, new business enters once at its
  `policy_count`, nothing happens before issue, and the in-force columns are present. And
  `tests/test_whole_of_life_uk_sec.py` compares each twin with S in every cell again, with
  improvement at 0.2%, the RPI at 6%, the take-up at 0.8 and the crossover stress on in
  both models, which T1, at the shipped References, and the splice, at no improvement,
  cannot: a cell that dropped improvement fails there alone.
- **The splice**, in `tests/test_whole_of_life_uk_sec.py`: each `WOL_UK_S` point restated
  in force at months about its events — on the over-50s points 1, 6, 11 to 13 (the
  moratorium's end and the first anniversary), 60 (the lapse table's last year), 118 to 121
  (the first conversion to paid-up), 165 to 167 (the crossover), 239 to 241 (premium
  cessation), 479 to 481 (the cap) and 599, with 185 and 186 on the RPI point; on the
  underwritten points 11 to 13 (the suicide window's end), 642 and 643, 887 to 889 and 959;
  on the male smoker 222 and 223, 299 to 301, 431 to 433 and 659 — continues the S
  projection in every cell the two share but `proj_len`, and in both reports, to 1e-9
  relative with no absolute floor, the residual at 1e-9. The crossover stress, which ships
  at 0, is on in both models at 0.5, so that past the crossover the premiums paid move the
  lapses, the conversions and so every count; inflation and improvement, the inputs on the
  valuation clock, are 0 in both. A stress of 100, which takes the lapse rate to its bound
  and leaves the paid-up point paid-up entirely, is spliced on the anchor and paid-up points
  the same way. Five variants of S's points, in a copy of S's table that is never committed,
  reach what S's own cannot: the RPI point with the pro-rata paid-up value, the double
  accidental benefit with it, the anchor cell issued at 80 with its premiums ceasing at 90
  and no crossover, the underwritten increasing point as a female smoker, and the paid-up
  point with an odd cessation, 239 months, its strand in force from 120. A core of 24 of
  the 149 splice cases and 5 of the 26 future ones runs by default, the RPI point after
  its premiums ceased among them, and the full grid with `UKLIB_SEC_FULL=1`; a test
  asserts the core reaches every branch, opening-state column, kind of valuation month and
  side of every `min` and `max` the full grid reaches. The slower tests over every
  committed point, every shape or every cap run a part of it by default, six points among
  which every flow is nonzero, and the rest with the full grid.
- **Future new business**: issued 1, 12 and 120 months after the valuation date, each S
  point is the S projection moved on, with zeros before issue and no table read there, and
  so is each variant issued 13 months on, more than a year after the valuation date and
  off its anniversaries.
- **How it computes**: on every row of the splice's grid, after its reports, its checks
  and every monthly cell at every month, no cell has been called at a negative month, none
  on the books read a month before `t_entry()`, none read a month later than `t + 1`, and
  none raised. On a fresh read of the committed model, `duration_mth(500)` evaluates
  `duration_mth` once, the policy clock being a closed form, and every point's reports and
  checks run under modelx's recursion limit lowered to 40, which a recursion backward over
  the frame would exceed; they pass at 12. And each chain, called cold in the last month at
  the contract's longest cover on four shapes, runs one cell a month back to `t_entry()`
  and at most 16 more.
- **Counts**: the roll-forward closes on both strands; `result_pols()` is S's report with
  `pols_new_biz`, the paid-up deaths and the truncation residual beside it; multiplying
  `policy_count` and `pols_pu_init` by 2.5 together, with the stress and improvement on,
  multiplies every flow and counted cell, each nonzero on some point, and moves no
  per-policy value, bit for bit; a point restated a month on, opened with what the model
  carries into its month 1, continues its own flows, its commission among them, which is
  what sees a paid-up flow weighted by the full-cover count; the roll-forward, its
  tolerance scaled by the policies on both strands, closes on ten million policies, the
  point paid-up entirely among them; and so does the truncation check, on that point with
  ten million paid-up policies at a loading under which survivors reach the limiting age.
- **Validation and regeneration**: each malformed row of the table, 89 cases, is refused
  naming its point, and naming its label on an extract labelled otherwise than by position,
  among them each bound of the premiums paid, the paid-up cover and the crossover a cent or
  a month outside, the first year's history a month after issue, and a paid-up strand at
  half an odd cessation rounded down; the horizon is a Reference, whole and below `2**53`;
  a point past the limiting age is refused by `proj_len()`, and `run_sec.py --block`
  refuses it before printing anything; so is a point outside the contract's bounds, 4
  cases, each bound just inside it and each moved past a committed point; each of 22
  References off its domain, the value next outside each edge, NaN and both infinities,
  150 cases, where each edge is accepted, and a whole limiting age written `120.0`
  projects as 120 does, cell for cell; a value past the floats, 10 cases, from the cover to
  the net cash flow, each in its own cell, and each of the five powers raising
  `OverflowError`; each assumption table a reader cannot read, 24 cases, refused naming its
  lines, and an age past the mortality table refused by name; keys written as floats read
  as `WOL_UK_S` reads them; the edges of the interface are accepted, a point paid-up
  entirely, a zero count, the horizon, the first month a paid-up policy can be in force,
  an escalated point at its issue values, a point after cessation, each bound of the
  contract and each bound of the history at its edge among them; every state `WOL_UK_S`
  reaches, as shipped, under the splice's stress, under a stress that lapses every policy,
  under an RPI of 8% and under a take-up of a half, is accepted in force; and the
  committed table is what `WOL_UK_S` generates.
- **The product's own facts**: the two clocks on the shipped points; the committed rows, in
  force and issued later, continuing their S points at the shipped assumptions but for
  inflation, and the rows read under References of their own holding `WOL_UK_S`'s history
  under them, its counts throughout, and with those References set in both, `WOL_UK_S`
  throughout; each history column read, not recomputed, the cover and the premium on an
  RPI history no flat rate gives and on the fixed increases at a take-up of their day, the
  premiums paid, which move the stressed lapses and the crossover, and which the
  moratorium refunds as read, to the cent, the paid-up count and cover, and the crossover,
  on the RPI point restated after crossings under an RPI of 0 and of 8%; and the instant
  the columns are measured at, before month 0's events, so that point 12, valued on its
  first anniversary, makes its first increase at `t = 0` at a take-up of a half set at the
  valuation date, a cover of 153,750 and a premium of 106.31, where columns read after
  that step would hold 157,500 and 111.38 (UKLIB-SEC-PLAN.md K14); expense inflation and mortality improvement on the
  valuation clock, which only these tests see, and where improvement gives way to the
  truncation check; the crossover a policy month, `WOL_UK_S`'s on every row it reaches; the
  moratorium, the suicide window and commission on the policy clock; the acquisition
  expense on new business alone; the RPI's floor and caps; every guarded cell's value
  outside cover; the block; an extract without the generator's three columns, labelled
  otherwise, projecting the same numbers; `run_sec.py`'s numbers, for a point and for the
  block, and its sum, and its `--cython` stopping where no repository is above it; no
  cell's parameter defaulted but the `claims` total's; the docstrings, read through
  docutils as the docs build reads them where docutils is installed; and the shared input
  tables.
- **The caps**: on the anchor cell, the male smoker and the underwritten point, under the
  splice's References, `WOL_UK_S`'s mortality rate reaches the float 1.0 in its first
  capped month and stays there, as does the monthly rate; every policy in force at its start
  dies in it, and none is in force after it; the reports hold finite floats; and every cell
  the two models share agrees, issued now and 12 months on, and restated in force the month
  before the cap, to 1e-9 relative with no absolute floor. A row restated five months into
  the capped year does the same from its first month. And a NaN sent to the cap, through
  either loading or improvement, or to the RPI's floor and caps, stays NaN in the cell,
  where the frame refuses the Reference; and each check is False where its residual's
  formula is replaced by one returning NaN, the only way left to give it one.

```bash
python -m pytest tests/test_whole_of_life_uk_sec.py -q
UKLIB_SEC_FULL=1 python -m pytest tests/test_whole_of_life_uk_sec.py -q   # the full grid
python -m pytest tests/test_model_conventions_uk.py -q -k WOL_UK_SEC
```

<!-- BEGIN generated citation links -- regenerate with tools/gen_citation_links.py -->
[R7]: #uklib-whole_of_life-r7
[REG-R22]: #uklib-reg-r22
[std]: #uklib-std
<!-- END generated citation links -->
