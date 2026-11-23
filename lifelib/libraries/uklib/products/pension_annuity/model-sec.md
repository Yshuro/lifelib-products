# In-Force Implementation Notes

**Status:** Draft, 2026-11-23. `PA_UK_SEC` is [`PA_UK_S`](model.md) taught to project
from a valuation date. Besides annuities starting at that date, it takes annuities already
in payment there, in any month of their policy year, and annuities to start in the ten
years after it, as lifelib's `basiclife/BasicTerm_SE` extends `basiclife/BasicTerm_S`. It
stands on the payout chassis of uslib's `SPIA_US_SEC`. The product is the one
[`product-spec.md`](product-spec.md) specifies and
[`technical-notes.md`](technical-notes.md) models; this page says what running in force
changes. The suffix adds lifelib's letters to `S`: `E` for in force, as in
`BasicTerm_SE`, and `C` for the compiled form, as in `basiclife/BasicTerm_SC`, which the
model's next step adds (UKLIB-SEC-PLAN.md U2). Until then it runs in modelx alone.

> **This is a mechanics demonstration, not a pricing or reserving result.** The model is
> `PA_UK_S` on another time axis, and it reads `PA_UK_S`'s mortality table in place, every
> assumption unchanged: the contractual mechanics are sourced, and every rate is a
> **[std]** standardization, the mortality basis an ONS-shaped population proxy standing in
> for the annuitant tables, which are restricted to CMI Authorised Users [R10] [R11]
> [REG-R22] [REG-R27]. Replace them with company data and licensed tables before drawing
> any conclusion from the numbers.

## Run it

```bash
python products/pension_annuity/run_sec.py            # point 1: the worked example, starting at t = 0
python products/pension_annuity/run_sec.py 11         # point 11: the worked example in payment 17 months
python products/pension_annuity/run_sec.py --block    # every model point, summed row by row
```

The first prints the worked example's first twelve rows of cash flows, with the counts and
survival behind them. Three lines to the same thing for point 11:

```python
import modelx as mx
model = mx.read_model("products/pension_annuity/PA_UK_SEC")
model.Projection[11].result_cf()
```

`Projection` takes a `point_id`, as `PA_UK_S`'s does; it will take `idx`, a point's
position in the table, once the model compiles, and the runner takes its key from the
model either way. `result_cf()` has `PA_UK_S`'s columns — `pols_if`, `annuity_payments`,
`claims_vp`, `claims_prop`, `expenses`, `liability_cf` and `net_cf` — with one row per
month from the valuation date, `t = 0 … proj_len() − 1`. `result_pols()` sets out the
counts first, `pols_if`, the closing obligation measure, and `pols_new_biz`, the annuities
starting in the month, then `PA_UK_S`'s other columns in its order: each life's survival,
the guarantee's floor, the two payment factors, the instalment, the payments to date and
the value-protection balance.

`--block` projects every point and releases its ItemSpace once its frame is read, so the
run holds the cells of one point at a time. Deleting it, `del model.Projection[11]`, is
not enough: an ItemSpace sits in reference cycles, which only Python's cyclic collector
frees, so the runner collects after each release. It freezes everything alive
(`gc.freeze()`) once the model and its table are read, and again once it has asked every
point for its frame, so that each collection scans only what the block has made since. It
keeps the block's sum as it goes, compensated as pandas sums a `groupby`, so that the block
is, bit for bit, the frames concatenated and summed by `t`. Every column is summed: each is
a flow of the month or `pols_if`, the contracts with an obligation open at its end.

The runner is uslib Term's, so it already takes `--cython`, which runs the compiled model
in place of modelx, building it first with the repository's `tools/build_sec_cy.py`, and
`--build DIR`, which runs a build made elsewhere. The model compiles from its next step
on, which brings the build's `sample_sec.py` and `spec_sec.py`; until then a build stops,
saying why. A `lifelib.create()` copy carries no `tools/`, and there `--cython` stops
before building, saying so.

## Two clocks

The model runs on two clocks, and each formula reads the one its quantity belongs to.

- **`t`, the valuation clock**, counts months from the valuation date. `t = 0` is the
  valuation month for every model point, however long the annuity has been in payment, and
  the frame runs `t = 0 … proj_len() − 1`, where `proj_len()` is the number of months from
  the valuation date to the stop rule.
- **`duration_mth(t)`, the policy clock**, counts the months from the annuity start date
  at time `t`: `duration_mth(t) = duration_mth_init() + t`, with `duration_mth_init()` read
  from the model point. The contract runs on it: `duration(t) = duration_mth(t) // 12`,
  `policy_year(t) = duration(t) + 1`, the year the income escalates by, `age(t, life) =
  age_at_entry(life) + duration(t)`, age last birthday, the mortality table's, and the
  calendar year, `start_year() + duration(t)`, which dates the improvement. The stop rule
  is a policy month, `stop_mth()`: `PA_UK_S`'s frame length, the age stop on the youngest
  covered life or the guarantee's end if later. `BasicTerm_SE` reaches the same clock by
  adding one a month, a recursion as long as the frame; the closed form needs no such chain
  of calls.

Point 11 is the worked example in payment 17 months. At `t = 0` it is in policy year 2 at
attained age 66, its annuitant dead since policy month 16 on the scenario basis and its
dependant paid half the income, £695.25 in month 0; its frame has 619 rows, `t = 0 … 618`,
and `PA_UK_S` projects the same months as its rows 17 to 635. Point 20 is the RPI catch-up
point to start 13 months after the valuation date: `duration_mth(0) = −13`, it is on the
books from `t_entry() = 13`, rows 0 to 12 are zeros, and its frame has 649 rows.

| Read on the policy clock | Read on the valuation clock |
|---|---|
| the payment months and the months since a payment; the policy year and its escalation, the RPI's anniversaries among them; the guarantee's end; the scenario's months of death; the attained age, the mortality table and the limiting age; the calendar year the improvement counts from; the annuitant's payments to date, which first-death value protection nets | survival and the expected payments to date on every stream, from the opening state; the value-protection balance; expense inflation, `inflation_factor(t) = 1.03^(t // 12)` |

Expense inflation alone of `PA_UK_S`'s inputs runs on `t`, stepping on each anniversary of
the valuation date, so the maintenance charge is in valuation-date pounds, for every point
alike (USLIB-SEC-PLAN.md D7). Improvement is dated by the calendar and stays on the policy
clock: a contract in payment reads the calendar years it reaches, whatever the valuation
date. `rpi_rate` is one flat rate, the assumed RPI from the valuation date on, the same on
either clock, so no index path is introduced (UKLIB-SEC-PLAN.md §9 item 4); the increases
given before the valuation date are opening state (*The RPI and the income's history*).

Because row `t` is the same month for every point, the frames of a block line up and sum
row by row, which is what `run_sec.py --block` prints:

```python
import pandas as pd
frames = [model.Projection[p].result_cf() for p in model.Data.model_point_table().index]
block = pd.concat(frames).groupby(level="t").sum()
```

On a point starting at `t = 0` the two clocks coincide, and the model computes what
`PA_UK_S` computes: every cell the two models share agrees, but `pols_if_init()`, now the
count already in payment at the valuation date, 0 for new business, and `model_point()`,
a row of another table. `annual_income_init()` agrees too: it is now the income of the
year under way at the valuation date, which on such a point is the first year's, the
value `PA_UK_S`'s cell of that name returns, and which this model also gives as
`annual_income_first()`.

## The in-force interface

The model point table is `model_point_table_sec.csv`. It carries `PA_UK_S`'s columns, its
count restated as the in-force interface under `basiclife/BasicTerm_SE`'s names, and six
columns of opening state. Each state column is per contract, so that `policy_count` is the
one weight on every flow, and each is measured at the valuation instant, the start of month
0, before any month-0 event (USLIB-SEC-PLAN.md D6). Each is history: what the contract has
survived, paid and been given since its start, never re-derived from a Reference, which is
an assumption from the valuation date on, so that a Reference changed there reaches back
over no month already run (UKLIB-SEC-PLAN.md K14, §9 item 5):

| Column | Unit | Measured at | Meaning |
|---|---|---|---|
| `policy_count` | contracts, not necessarily whole | for a point in payment, the start of month 0; for any other, its start month | the contracts in payment at the valuation date, for a point already in payment; the annuities starting, for one starting at or after it |
| `duration_mth` | whole months | the valuation date | the months from the annuity start date: positive in payment, 0 for an annuity starting at the valuation date, `−k` for one to start `k` months later, with `k` at most 120 as shipped |
| `lives_if_init_1`, `lives_if_init_2` | probabilities | the start of month 0, before any month-0 death | each covered life's probability of being alive, the annuitant's and the dependant's: 1 or 0 on a record, `PA_UK_S`'s `lives_if(d, life)` on a restated point; the dependant's 0 on a single life |
| `cum_annuity_all_init` | pounds per contract, 0 or more | the start of month 0 | the instalments paid on every stream before the valuation date, the annuitant's, the guaranteed and the dependant's: what was paid on a record, the expectation on a restated point; last-survivor value protection nets it |
| `annual_income_init` | pounds a year, `annual_income` or more, to half a cent | the start of month 0, before any month-0 anniversary | read on RPI-linked escalation, `lpi5` and `rpi_catchup`: the annuitant's income of the policy year under way, before the dependant's percentage, the scale the dependant is paid `δ` times of after the annuitant's death; the increases the RPI has given since the start, never below the first year's; on a point valued on an anniversary the year the anniversary closes, month 0 escalating it at the valuation date's RPI |
| `rpi_peak_init` | a factor, 1 or more | the anniversary that opened the policy year under way | read on `rpi_catchup`: the ratchet's running peak of the reference index over the latest index, above 1 while the index stands below a past peak |
| `cum_annuity_pp_init` | pounds per contract, 0 or more | the start of month 0 | read on RPI-linked escalation with value protection on the first death: the annuitant's as-if-alive instalments before the valuation date, which the first-death balance nets |

The last three are blank on a point that does not read them. Every state column holds its
value at the start date on a point not yet in payment, each covered life alive, nothing
paid, the first year's income and a peak of 1; and in the first policy year, before any
anniversary, the income and the peak hold the first year's. On level and fixed escalation
the income and the annuitant's schedule are the contract's, re-derived at the valuation
date's key by one loop in `PA_UK_S`'s order, bit for bit (*The RPI and the income's
history*).

`PA_UK_S` rebuilds all six from References where its frame opens, which a Reference
changed at the valuation date would rewrite back to the start. Its survival is the
mortality basis run from the start, so an `annuitant_adj` changed at the valuation date
moves the survival and the payments of every month already run: here a test changes it and
the opening state stays the column. Its income on RPI-linked escalation is the flat
`rpi_rate` compounded from the start, so an increase capped at 5% under an RPI of 8%, or an
income the ratchet froze through a fall, which no flat rate set at the valuation date
gives, is in the column and not in S. A test writes each column off any path S makes and
projects it through.

| `PA_UK_S` | `PA_UK_SEC` | Why |
|---|---|---|
| `pols_if_init` (1.0) | `policy_count` | The count, under BasicTerm_SE's name. `pols_if_init()` now means the count in payment at the valuation date, 0 for a point starting at or after it |
| — | `duration_mth` | The policy clock, in months, any month of a policy year |
| — | `lives_if_init_1`, `lives_if_init_2` | `PA_UK_S` opens each life's survival at 1, at the start |
| — | `cum_annuity_all_init` | `PA_UK_S` opens the payments to date at 0 |
| — | `annual_income_init`, `rpi_peak_init`, `cum_annuity_pp_init` | `PA_UK_S` rebuilds the RPI's history from the flat rate of the day |

The columns carried over are read as `PA_UK_S` reads them. For a contract in payment, the
facts they record are those at the start date:

| Column | Unit | Measured at |
|---|---|---|
| `point_id`, `policy_id` | labels | — |
| `annuitant_age`, `dependant_age` | years, age last birthday | the start date, not the valuation date: `age(0, life)` is the attained age there |
| `annuitant_sex`, `dependant_sex` | M or F | the start date |
| `rating_multiplier`, `dependant_rating` | factors, 1 or more | the start date |
| `dependant_present`, `overlap`, `proportion` | True or False | the start date |
| `purchase_price`, `annual_income` | pounds; pounds a year | the start date: the price value protection is measured on, and the first year's income |
| `frequency`, `timing` | 12, 4, 2 or 1 a year; arrears or advance | the start date |
| `escalation_type`, `escalation_rate` | a code; a rate a year | the start date |
| `guarantee_months` | whole months from the start date | the start date: the guarantee covers policy months 0 to `n − 1`, so the months of it left follow from `duration_mth` |
| `vp_pct`, `vp_basis` | a share of the price; a code | the start date |
| `mort_basis` | table or scenario | the basis from the valuation date on |
| `death_mth_1`, `death_mth_2` | policy months, or blank | the scenario's months of death, counted from the start date, so the same month whatever the valuation date |
| `start_year` | a calendar year | the year the annuity started, or will start |

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
business altogether; the three flags are True or False; the ages and the start year whole
numbers below `2**53`, each sex M or F, each rating a finite number 1 or more, the price
and the income finite and 0 or more, the frequency 12, 4, 2 or 1, the guarantee a whole
number of months, 0 or more, the value protection and the dependant's share from 0 to 1,
the fixed escalation finite and 0 or more; on the scenario basis each month of death blank
or a whole number, 0 or more; each survival a probability, the second 0 on a single life;
each state column in its domain where it is read; the start date's values on a point not
yet in payment, and the first year's in the first policy year; and on the scenario basis
each life's opening status its month of death's, alive while the death falls at the
valuation month or later; and on RPI-linked escalation the income of the year under way
is the first year's or more, to half a cent, the LPI's floor and the ratchet never letting
it fall: half a cent, so that an extract may carry it to the cent (USLIB-SEC-PLAN.md D6),
5,399.995 against a first year's 5,400 read and 5,399.99 refused.
`PA_UK_S` meets most of these only when a projection reaches them, and some never: `bool`
reads a blank flag as True, `int()` truncates an age, a frequency, a guarantee, a start
year and a month of death, and a negative month of death reads as a life that never dies
(UKLIB-SEC-PLAN.md §6.7, *S defects found*). Each window a rule reads, the start date's to
120 months on and the first policy year's, is held at both its ends. A column some points
never read, such as a scenario point's rating or start year, is still held on every
point, as `PA_UK_S`'s reader holds it; refusing it only where it is read is carried into
M12, the C step, as SPIA's C step reworked its refusals by point (USLIB-SEC-PLAN.md §7.9,
*Record — M23*, *Refusal by point*).

A contract at or past its stop rule, `duration_mth ≥ stop_mth()`, reads, but `proj_len()`
refuses it, naming the point: the stop is the product's rule, not the table's. So does a
contract owing nothing after the valuation date: in payment, its guarantee over and every
covered life dead, its last payment made before the valuation date, which an in-force
extract should not carry, as `SPIA_US_SEC` refuses it. The rule reads the lives and the
guarantee: a joint contract whose dependant is alive at a share of 0 projects, owing
zeros, which is no wrong number. So does a point the contract does
not issue: a life issued below `Projection.issue_age_min`, 0, since `PA_UK_S` projects any
age on the scenario basis, a negative one among them; and a guarantee longer than
`12 × (omega_age − issue_age_min)` months, 1,380, the longest frame from the start date.
Each bound is a lower-case Reference, the contract a compiled model's caches will be sized
from: a frame of at most 1,380 months from the start and the horizon. So does a point read
under a Reference outside its domain, each named, NaN and the infinities outside every one,
since `PA_UK_S` reads several of them through a `min` or a `max` whose bound comes first,
which keeps the bound where a NaN meets it, or through a power. Each is held on the points
that read it:

| Reference | Read on | Domain | Outside it |
|---|---|---|---|
| `issue_age_min` | every point | a whole number of years below `2**53`, 0 or more | a NaN switches the bound off, every comparison with it failing; past `2**53` the compiled model's `long long` cannot hold it |
| `omega_age` | every point | a whole number of years below `2**53`, above `issue_age_min`; on the table basis at most a year past the table's last age, `Data.mort_age_last() + 1`, 116 | it sizes every frame; the table is read at attained ages to `omega_age − 1` |
| `expense_maint` | every point | finite, 0 or more | an expense |
| `inflation_rate` | every point | finite, −1 or more | the inflation factor changes sign each year |
| `annuitant_adj` | the table basis | finite, 0 or more | a mortality rate is negative; an infinity reads through the cap as certain death |
| `improve_rate_base` | the table basis | finite, below 1 | the improvement factor raises `1 − f` to a power, which at or below 0 has no real value or changes sign |
| `improve_flat_age`, `improve_taper_age` | the table basis | finite | the ages the scale is flat to and tapers to 0 at |
| `mort_table_year` | the table basis | a whole number below `2**53` | the calendar year the improvement counts from |
| `esc_fixed_cap` | fixed escalation | finite, 0 or more | a NaN switches the cap off, every comparison with it failing |
| `rpi_rate` | `lpi5` and `rpi_catchup` | finite, above −1 | the index, `(1 + r)^a`, is a price level, above 0; the LPI floor, `max(0, r)`, its bound first, reads a NaN as no increase |
| `esc_lpi_cap` | `lpi5` | finite, 0 or more | the cap, `min(cap, …)`, its bound first, which an infinity switches off |

Each check is a comparison written out, a finite bound the largest float and a whole one
`2**53`, so that the compiled model runs it in C; the three integer References are printed
through `int()` once they are whole, the others through `float()`, and a whole float,
`omega_age = 115.0`, is read as the whole number it is. Every accepted edge projects
through its reports. A value a formula computes past the floats from References and
columns each in its domain is refused in the cell where it first is, naming what made it,
where Python's power would raise `OverflowError`, naming nothing, and a product or C's power
would carry an infinity on: the income, in `annual_income` and in the valuation date's
loop in `annual_income_init`, under an escalation, an RPI or a history near the largest
float; the payments to date, in `cum_annuity_pp` and `cum_annuity_all`, where the
value-protection balance, `max(0, vP − G)`, its bound first, would read an infinity as no
balance; the three powers, the inflation factor under an `inflation_rate` of 1e200, the
catch-up's index under an `rpi_rate` of 1e200 and the improvement factor under an
`improve_rate_base` of −1e200, or of 0.999999 with `mort_table_year` 2100; and the
maintenance, in `expenses`, where the largest `expense_maint` inflates past them. A loop
over the block meets a refused row only when
it reaches it, after projecting the points before it, so `run_sec.py --block` asks every
point for its frame before it projects any, and stops before it prints anything.

The mortality table is checked before a value of it is read, in the cell the projection
takes its extent from, `Data.mort_age_first`, and through it `mort_age_last`: each age a
whole number, each sex M or F, each sex running over the table's ages, 50 to 115, one row
an age, without a gap or a repeat, and each rate a number from 0 to 1. A key is read by its
value, so an age written `65.0` is 65. Each refusal names the file, the column and the lines
at fault: the check reads the file as it stands, one read that `PA_UK_S`'s reader then
sorts. A read below the table's first age, a life issued younger than 50 on the table
basis, is refused by the one cell that reads it, `mort_rate_base_at`, naming the point and
the age, where `PA_UK_S`'s lookup raised `KeyError`; on the scenario basis, which reads no
mortality, the same age projects. No frame reads past the table's last age.

## The model points

No row of `model_point_table_sec.csv` is typed by hand. Every one is generated from
`PA_UK_S` and its table by `tests/uk_sec_support.py`, from the `PA_UK_SEC` entry in its
`SEC_SPECS`, and the tests regenerate it and compare, so an edit to a `PA_UK_S` row
reaches it or fails the suite. In the source repository,
`python tools/gen_sec_points.py PA_UK_SEC` writes it.

| Point | Kind | From | At the valuation date |
|---|---|---|---|
| 1 to 10 | twin | S points 1 to 10 | starting at `t = 0`: `PA_UK_S`'s worked example, its table basis, the guarantee without and with overlap, the single life in advance, the RPI catch-up, the LPI, the rated single life, the proportionate payment and last-survivor value protection |
| 11 | derived | S point 1 at S month 17 | the worked example in policy year 2, its annuitant dead in policy month 16, its dependant paid, 6,790.50 paid to date |
| 12 | derived | S point 9 at S month 16 | the proportionate payment's point in the month of its scenario death, value protection and the proportionate payment paid in month 0 |
| 13 | derived | S point 3 at S month 120 | the guarantee ended at the valuation date, the annuitant dead and the dependant's income starting |
| 14 | derived | S point 7 at S month 24 | the LPI on its second anniversary, opening with the income of the year it closes, 5,562.00, and escalating it in month 0 |
| 15 | derived | S point 6 at S month 30 | the RPI catch-up mid-way through policy year 3, an income of 5,728.86 and a peak of 1 |
| 16 | derived | S point 2 at S month 101 | the table basis in the last month of first-death value protection's balance, its survival 0.890787 and 0.944548 |
| 17 | derived | S point 10 at S month 170 | the last month of last-survivor value protection's balance, 471.67 left |
| 18 | derived | S point 8 at S month 575 | the rated life the month before the cap kills it, its survival 8.6e-10 |
| 19 | derived | S point 2 at S month 635 | the joint frame's last month, the annuitant past the limiting age: a one-row frame |
| 20 | future | S point 6, 13 months on | to start at `t = 13` |
| 21 | derived | S point 6 at S month 60, S run under an `rpi_rate` of −2% | the catch-up frozen: an income of 5,400, a peak of 1.0841658 over the index, and 27,000 of the annuitant's instalments to date |
| 22 | derived | S point 7 at S month 42, S run under an `rpi_rate` of 8% | the LPI capped at 5% each year: an income of 6,251.18 and 20,149.09 of the annuitant's instalments to date |
| 23 | derived | S point 7 at S month 54, S run under an `rpi_rate` of −2% | the LPI held at its floor: an income of 5,400 and 24,300 of the annuitant's instalments to date |

A derived row's `policy_count` is the count `PA_UK_S` weights every flow by, 1, which no
decrement moves, and its state what S carries into that month, so the row continues the S
projection from there. Its `policy_id` is the S row's with the month appended,
`PA-000001-M17`, and a future row's carries the months to the start, `PA-000006-F13`. Row
`t` of a generated point is month `t + source_mth` of its S point.

No state `PA_UK_S` reaches at its flat 3% holds a ratchet's peak above the index, nor an
LPI increase capped or floored: a monotone index never leaves the peak above it, and 3% is
inside the cap and above the floor. So points 21, 22 and 23 are read from S run under an
RPI of its own, the spec's `derived_refs`, and C2 freezes all three. Set on the model too,
that RPI gives each row S's path over the whole of both frames; at today's 3%, which takes
over from the valuation date, the income parts from S's at the row's next anniversary, and
survival, the floors and the counts, which read no RPI, stay S's. C2 projects every row at
the shipped References, under which the LPI's step is 3% on every row, so it freezes the
history the cap and the floor made, not the bounds themselves; a test projects the two LPI
rows under their own RPI, where the cap holds the increase at 5% and the floor at 0. A
committed row is one of S's points restated, so a contract term S's table never holds,
value protection apart from the dependant's share or on a single life, a dependant older
than the annuitant, is the splice's alone.

## Counts and timings

`PA_UK_S` weights every flow by a constant count, the contracts it was written for, and
carries mortality in each life's survival, so the count chassis is `SPIA_US_SEC`'s: the
count on the books is never decremented. `pols_if_init()` is the count in payment at the
valuation date: `policy_count` for a point already in payment, 0 for any other.
`pols_new_biz(t)` is `policy_count` in the start month, the month with
`duration_mth(t) = 0`, and 0 in every other. `pols_if_at(t, timing)` takes
`basiclife/BasicTerm_SE`'s two timings:

- `"BEF_NB"`, the contracts carried in from month `t − 1`: `pols_if_init()` at
  `t_entry()`, the first month on the books, `policy_count()` after it, and 0 outside the
  frame, a closed form with no chain of calls back to `t_entry()`;
- `"BEF_DECR"`, that count plus `pols_new_biz(t)`, the count that weights every cash flow
  of month `t`.

Any other timing raises. `pols_if(t)` is not the count: it is `PA_UK_S`'s closing
obligation measure on it, `pols_if_at(t, "BEF_DECR") × min(1, max(C(t), l_a(t + 1)) +
1{δ > 0} (1 − l_a(t + 1)) l_d(t + 1))`, the guarantee certain, the annuitant alive, or the
dependant's pension in payment at the end of the month, the weight the maintenance expense
is carried on. It is 0.99999965 at `t = 0` on the twins of S's points 2, 6 and 7, against a
count of 1, so the registry marks the model `closing_pols_if`, as uslib's does
`SPIA_US_SEC`, and its conventions test reads the measure rather than the count there.

Each life's survival opens at `t_entry()` from the opening state and runs forward one cell
a month, `l(t) = l(t − 1)(1 − q_m(t − 1))` on the table basis and the step function on the
policy clock on the scenario basis; the expected payments to date on every stream,
`cum_annuity_all(t)`, open from `cum_annuity_all_init()` and run forward one cell a month;
and the annuitant's as-if-alive schedule, `cum_annuity_pp(k, "ANNUITANT")`, keyed by the
policy time point, opens at the valuation date's key, `max(duration_mth_init(), 0)`, and
runs forward one cell a month from there. So a contract valued late in life reads its
balance without recursing back to its start date, where `PA_UK_S`'s `G(k)` recurses from
0. On a model just read, a cold call in the frame's last month runs at most 12 cells deeper
than one a month back to `t_entry()`, at each shape's longest cover, 1,380 months from the
start, now, and as deep 120 months on, which the full grid runs: on the scenario basis
every life issued at 0, where `net_cf` runs 1,387 cells deep through the payments to date;
on the table basis every life issued at 50, the table's first age, whose age stop at 780
months a guarantee of 1,380 months, which `proj_len()` accepts, carries to the longest
frame. There `net_cf(1379)` runs 1,391 cells deep through survival, on the worked
example's table twin, the RPI points and the rated life alike: the deepest call a
projection makes, which the C step measures its stack on. Issued later, a chain runs the
same cells over the same policy months, later on the valuation clock: improvement, the
income and the schedules are dated on the policy clock, and inflation, the one cell the
valuation clock dates, is a closed form outside every chain.

Cover is `is_active(t)`, `0 ≤ duration_mth(t) < stop_mth()`, started and short of the stop
rule, and outside it, before the start and from the stop rule on, every count is zero, and
so every cash flow. No cell reads a rate, a policy year or an attained age there that the
contract does not have: the mortality and improvement rates, the instalment, the floors,
the factors and the claims are zero outside cover, before any table or rate is read. A
contract's own end inside the frame, its last death or its last guaranteed instalment, is a
probability or a floor reaching zero, not the end of the frame, which runs on with zeros
as `PA_UK_S`'s does.

## The RPI and the income's history

`PA_UK_S` reads the RPI as one flat `rpi_rate` from the start: `rpi_catchup` indexes the
income to the running peak of `(1 + r)^a`, and `lpi5` escalates it each anniversary by
`min(5%, max(0, r))`. A flat rate is the same on either clock, so this model keeps it, the
assumed RPI from the valuation date on, and carries what the RPI did before the valuation
date in the opening state (USLIB-SEC-PLAN.md D7, as `SPIA_US_SEC`'s CMT change).

The income of the year under way, `annual_income_init()`, is the year `policy_year_init()`,
`(duration_mth_init() − 1) // 12 + 1` on a contract in payment, the year of the month
before the valuation date: on a contract valued on an anniversary it is the year the
anniversary closes, not the one it opens, because the anniversary's escalation is a month-0
event and applies at the valuation date's RPI, as every month-0 event reads the valuation
date's References (USLIB-SEC-PLAN.md D6, precised at M7). A test restates the LPI point at
its second anniversary under an RPI of 1%: it opens with its second year's income, 5,562.00,
and pays 5,562.00 × 1.01 from month 0. Each year after it escalates at today's References:

```
lpi5:         A(y) = A(y − 1)(1 + min(esc_lpi_cap, max(0, rpi_rate)))
rpi_catchup:  A(y) = A(y₀) × peak(y − 1) / peak(y₀ − 1)
```

with the index and its peak measured relative to the latest index, at the anniversary
`a₀ = y₀ − 1` that opened the year under way: `rpi_index(a) = (1 + rpi_rate)^(a − a₀)`,
and `rpi_peak(a₀) = rpi_peak_init()`, run forward from there. On a point starting at the
valuation date `a₀` is 0, and every index, peak and income is `PA_UK_S`'s, bit for bit.

The ratchet's catch-up branch, an index rising from below its peak, is unreachable in
`PA_UK_S` on a flat rate, so it gets goldens of its own on point 21: its income frozen at
5,400 through its sixth and seventh policy years, the index rising from 1 to 1.0609 under
a peak of 1.0842, and catching up in its eighth by the excess of the index over the peak,
5,442.64, then 5,605.92 and 5,774.10. Written at a peak of 1.2, the income stays frozen to
the eleventh year; at a peak of 1, read from the index, it would escalate at once, to
5,562.00 in the sixth.

On level and fixed escalation the income is the contract's schedule, re-derived at the
valuation date's key, `A(1)(1 + g)^(y₀ − 1)`, compounded in one loop in `PA_UK_S`'s order,
and the annuitant's payments to date are the schedule summed in one loop to the valuation
date's policy month, both bit for bit with `PA_UK_S`'s recursions. The six-month reference
lag of the source contract is not modelled, as in `PA_UK_S`.

## Departures from PA_UK_S

Each formula that tested `t` against a contractual event now tests the policy clock, each
read at a month passed as `t` is a read at the policy month or year, and each recursion
opens at `t_entry()`, or at the valuation date's policy key, from the opening state. Where
`PA_UK_S`'s test would have stayed correct on the valuation clock, it moved anyway, so that
cover has one definition. Twenty-four cells are new, and none of `PA_UK_S`'s is gone.

| Cells | `PA_UK_S` | `PA_UK_SEC` | Why |
|---|---|---|---|
| `duration_mth`, `duration` | `t`, `t // 12` | `duration_mth_init() + t`, `duration_mth(t) // 12` | The policy clock, opened from the model point |
| `t_entry`, `stop_mth`, `is_active`, new | — | `max(0, −duration_mth_init())`; `max(horizon_mths(), guarantee_mths())`; `0 ≤ duration_mth(t) < stop_mth()` | The first month on the books, the stop rule on the policy clock, and cover |
| `proj_len` | `max(horizon_mths(), guarantee_mths())`, from the start | `stop_mth() − duration_mth_init()`, from the valuation date; raises at or past the stop, owing nothing, outside the contract's bounds and under any of twelve References outside its domain | The frame starts at the valuation date |
| `is_payment_mth`, `is_payment_pm`, `annuity_pp`, `annuity_pp_pm` | `(t + 1) % step` and `t % step` on `t` | the schedule keyed by the policy month, read at `duration_mth(t)` | A contract in payment 17 months pays at policy months 17, 20, …, whatever `t` they fall at |
| `mths_since_payment`, `next_payment_mth` | on `t`; a scan month by month to the frame's end | on the policy month; a closed form, returning the policy month or −1 | The proportion rule's one far read, R2's look-ahead, gone |
| `claims(t, "PROP")` | `inst(next(t))` | `A(policy_year(t)) / m` | On arrears the next payment falls in the policy year of month `t` |
| `certain_floor`, `overlap_gate` | `t < n`, `t ≥ n` | `duration_mth(t) < n`, `duration_mth(t) ≥ n` | The guarantee counts from the start date |
| `lives_if`, `check_lives_roll_fwd_resid` | 1 at `k ≤ 0`; the scenario step on `k`; the product from 0 | `lives_if_init(life)` at `t_entry()`, 0 before it; the step on `duration_mth(t)`; the product from `t_entry()` | Survival is history; the scenario's death months are policy months |
| `cum_annuity_pp`, `cum_annuity_all`, new | one recursion from `G(0) = 0` for both kinds | `"ANNUITANT"` on the policy clock, based at `max(duration_mth_init(), 0)` by one loop, or on RPI-linked escalation by `cum_annuity_pp_init()`; `"ALL"` the new `cum_annuity_all(t)`, on the valuation clock from `cum_annuity_all_init()`, raising before the valuation date; each refused past the floats | Both parted by clock; the payments to date are history |
| `vp_balance` | keyed by S's time point | keyed by `t`: first death nets `cum_annuity_pp(duration_mth(t), "ANNUITANT")`, last survivor `cum_annuity_all(t)`; 0 before `t_entry()` | The balance on the valuation clock |
| `annual_income_init`, `annual_income_first`, `policy_year_init`, new | `annual_income_init()`, the first year's income | `annual_income_first()`, the first year's; `annual_income_init()`, the year under way's, `policy_year_init()` | D6's name for the opening income |
| `annual_income` | from `A(1)` at `y ≤ 1` | from `annual_income_init()` at `y₀`; refused past the floats | The income's history is the contract's |
| `rpi_index`, `rpi_peak` | `(1 + r)^a`; the peak from `I(0)` | `(1 + r)^(a − a₀)`; the peak from `rpi_peak_init()` at `a₀`; the index refused past the floats | Relative to the latest index, the peak carried in |
| `inflation_factor`, `expenses` | `1.03^(policy_year(t) − 1)`, from the start | `1.03^(t // 12)`, from the valuation date; each refused past the floats | Unit costs in valuation-date pounds (D7) |
| `horizon_mths`, `payment_freq` | `12 × (omega_age − min x)`; a tuple of the four frequencies | `omega_age` read through `int()`; the four compared one by one | A whole float gives the int frame; no Python object in a computed cell |
| `mort_rate_base_at`, new; `mort_rate_base`, `improve_rate`, `improve_factor`, `mort_rate`, `lives_death`, the floors and factors | unguarded: no `PA_UK_S` frame has a month outside cover | zero outside cover, before any table or rate is read; the table read in one cell, its extents from `Data`, an age outside it refused by name; the improvement factor refused past the floats | Before the start S's lookup raises `KeyError` |
| `pols_if`, `pols_if_at`, `pols_new_biz`, `pols_if_init` | `pols_if_init() × min(1, …)` | `pols_if_at(t, "BEF_DECR") × min(1, …)`, 0 outside the frame | The count enters once, in payment or in its start month |
| `result_pols` | `PA_UK_S`'s columns, `pols_if` last | `pols_if`, `pols_new_biz`, then `PA_UK_S`'s others in its order, 0 before the start | After `basiclife/BasicTerm_SE`'s `result_pols()` |
| `is_arrears`, `is_scenario`, `is_first_death`, `is_level`, `is_fixed`, `is_lpi5`, `is_rpi_catchup`, new | the label accessors, compared as text | decodes of `timing`, `mort_basis`, `vp_basis` and `escalation_type`, each read and validated as its accessor is, raising its message | No projection cell compares text (UKLIB-SEC-PLAN.md §6.7, *C*) |
| `dependant_pct` | reads the column, then discards it on a single life | asks first whether the contract is joint | A single life's share is never read |
| `policy_count`, `duration_mth_init`, `lives_if_init`, `cum_annuity_all_init`, `rpi_peak_init`, `cum_annuity_pp_init`, new | — | the interface's columns | *The in-force interface* |

Of the cash flows, the change of clock moves the maintenance expense alone, and
`liability_cf` and `net_cf` with it. Point 11 carries that expense in valuation-date
pounds, so its `expenses(t)` is `PA_UK_S`'s `expenses(17 + t)` with S's factor,
`1.03^((17 + t) // 12)`, taken out and `1.03^(t // 12)` put in: 1.03 less at `t = 0`. Its
`pols_if`, its instalments, both claims columns and every survival are `PA_UK_S`'s from
month 17 on. Point 20 is `PA_UK_S`'s point 6 thirteen months on in those columns too; its
maintenance expense is `1.03^(t // 12 − (t − 13) // 12)` above S's at each `t`.

`mort_rate` caps the annual rate at 1, written `min(θ × q, 1.0)`, the product first and the
bound second, as `PA_UK_S` writes it, so that a NaN stays NaN where `min(1.0, θ × q)` would
read it as certain death. It binds on S's point 8, rated 1.35, from policy month 576 to the
end of its frame, where the rate is the float 1.0 in both models and every life alive at
the start of the month dies in it; so S's point 8 owes nothing after policy month 576, and
`proj_len()` refuses it restated later.

## Tests

- **The twin identity**, in `tests/test_model_conventions_uk.py`: on points 1 to 10, every
  cell of `PA_UK_S`'s agrees at every argument `PA_UK_S` evaluates in its own sweep, to
  1e-9 relative with no absolute floor, but `pols_if_init`, `model_point` and
  `result_pols`, the harness's two and the one the spec names, with their reasons;
  `annual_income_init` is compared, and is the first year's income on a twin. A cell this
  model lacked would fail it. So `PA_UK_S`'s worked example, which
  `tests/test_pension_annuity_uk.py` asserts to the penny, holds here with no number
  restated. The same suite holds the model to the conventions every `_SEC` model meets:
  every frame starts at `t = 0`, `pols_if` is the closing measure on the `"BEF_DECR"`
  count, new business enters once at its `policy_count`, nothing happens before the
  start, and the in-force columns are present.
- **The splice**, in `tests/test_pension_annuity_uk_sec.py`: each `PA_UK_S` point
  restated in payment at months 1, 2 and 3, about the first quarterly payment in arrears,
  11 to 13 and 23 to 25, about the first two anniversaries, 15 to 17, about the scenario
  death, 101 and 102 and 170 and 171, where first-death and last-survivor value protection
  run out, 119 to 122, about the guarantee's end, 575 and 576, about the cap, 599 and 600,
  where the older life reaches the limiting age, and 635, continues the S projection in
  every cell the two share but `proj_len` and the survival point, a time point on each
  clock, and in both reports, to 1e-9 relative with no absolute floor but the residuals;
  the opening income is held to S's of the year under way, and the relative index and peak
  to S's over its index at the latest anniversary. Inflation, the one input on the
  valuation clock, is 0 in both. Sixteen variants of S's points, in a copy of S's table
  that is never committed, reach what S's own cannot: advance timing with value
  protection on either basis, the last survivor's on the table basis, where a claim is
  paid; semi-annual and annual payments; the dependant dying first; both lives dead with
  and without a guarantee; a guarantee past the age stop; a rated joint life; the
  proportionate payment on the table basis; the RPI points without first-death value
  protection; value protection of 30% beside a dependant's 50%, and on a single life; a
  dependant older than the annuitant; and a dependant's share of 0. The RPI points are
  spliced under RPIs of 8% and −2%, where the LPI's cap and floor bind and the ratchet
  freezes, and the worked example's table twin beside them, its fixed 3% apart from either
  RPI. A core of 44 of the 378 splice cases and 7 of the 46 future ones runs by default,
  and the full grid with `UKLIB_SEC_FULL=1`, the depth test's shapes issued 120 months on
  among it; a test asserts the core reaches every branch, opening-state column, kind of
  valuation month and side of every `min` and `max` the full grid reaches.
- **Future new business**: starting 1 and 12 months after the valuation date, each S point
  is the S projection moved on, with zeros before the start and no rate evaluated there,
  and so is each variant starting a month on, the catch-up point 13 months on and the
  worked example 25, and the RPI points under each RPI.
- **How it computes**: on every row of the splice's grid, after its reports, its checks and
  every monthly cell at every month, no cell has been called at a negative month, none on
  the books read a month before `t_entry()`, none read a month later than `t + 1`, none on
  RPI-linked escalation asked a year, an anniversary or a policy month before the valuation
  date of the cells keyed on the policy clock, none raised, and every check holds, the
  whole survival check among them. On a fresh read of the committed model,
  `duration_mth(500)` evaluates `duration_mth` once, the policy clock being a closed form,
  and every point's reports and checks run under modelx's recursion limit lowered to 40,
  which a recursion backward over the frame would exceed. Each chain, called cold in the
  last month at each shape's longest cover, runs one cell a month back to `t_entry()` and
  at most 16 more, each shape's deepest as measured, 1,391 on the table basis's; the
  schedules at the valuation date's key are S's, bit for bit, and a contract valued in
  its last month runs its reports within 8 cells; and no computed cell outside §6.7's C
  list holds a Python object.
- **Counts**: the count is never decremented, `"BEF_NB"` a closed form, and `pols_if` the
  closing measure on it; `result_pols()` is S's report with `pols_new_biz` beside it;
  multiplying `policy_count` by 2.5 multiplies every flow and counted cell and moves no
  per-contract value, every flow nonzero on some point; and each point in payment, restated
  a month on with the state it carries there, continues its own flows.
- **Validation and regeneration**: each malformed row of the table, 82 cases, is refused
  naming its point, on the committed labels and on an extract's; each text value no
  decode knows raises `PA_UK_S`'s message; the horizon is a Reference; a point at its
  stop, one owing nothing and one the contract does not issue are refused by
  `proj_len()`, each bound just past it and each moved past a committed point, and
  `run_sec.py --block` refuses such a point before printing anything; each of twelve
  References is held to its domain, 105 cases, each edge accepted and its reports
  projected, and the nearest value past it refused, NaN, the infinities, a fraction,
  `2**53` and a whole float too; the income, the payments to date, the three powers and
  the maintenance are refused where they would pass the floats, naming the References;
  each window of `Data`'s is held at both its ends; each mortality table a
  reader cannot read, 13 cases, is refused naming its lines, and a read beyond it naming
  the point; keys written as floats read as `PA_UK_S` reads them; the edges of the
  interface and of each bound are accepted; every state `PA_UK_S` reaches, as shipped,
  with the variants and under each RPI, is accepted in payment, but a contract owing
  nothing, which is refused; and the committed table is what `PA_UK_S` generates.
- **The product's own facts**: the two clocks on the shipped points; the committed rows
  continuing their S points at the shipped assumptions but for inflation, and the three
  read under an RPI of their own continuing S under it, the two LPI rows projected under
  it to the cap's and the floor's goldens; each history column read, not
  recomputed: survival and the payments to date kept under an `annuitant_adj` changed at
  the valuation date and written off S's path, the LPI's capped income and an income no
  flat RPI gives, the ratchet's catch-up with its own goldens, and the annuitant's payments
  to date (UKLIB-SEC-PLAN.md K14); the income measured before month 0's anniversary; the
  RPI one flat rate on either clock; expense inflation on the valuation clock at the
  shipped 3%, which only this test sees; improvement and the payment schedule on the
  policy clock; no premium and no acquisition; every guarded cell's value outside cover;
  the block; an extract without the generator's three columns, labelled otherwise,
  projecting the same numbers; `run_sec.py`'s numbers, for a point and for the block, and
  its sum, and its `--cython` stopping where no repository is above it; no cell's parameter
  defaulted but the `claims` total's, and `cum_annuity_pp`'s total refused before the
  valuation date; the
  docstrings, read through docutils as the docs build reads them where docutils is
  installed; and the shared input table.
- **The cap**: on S's point 8 the rated rate passes 1 from policy month 576 to 599; in
  both models `mort_rate` and `mort_rate_mth` are the float 1.0 there, every life in payment
  at the start of that month dies in it, none is alive after it, and the reports hold
  finite floats, on the twin and restated in payment the month before. A NaN sent to the
  cap, through `annuitant_adj`, stays NaN; and each check fails a residual that is not a
  number.

Memory is the module's other cost. A swept point holds its cached values and modelx's
record of what each read, and `PA_UK_S`'s survival check, which rebuilds survival as a
product over every month before each time point, holds about 110 MB of that record on a
point on the table basis. So the module's sweeps evaluate the check's residual at every
25th time point and the frame's close, the whole check running on each splice row as it
is scanned, released once read; the splice keeps two S points swept at a time. The
default run peaks at 2.9 GB of memory, inside the 7 GB of the smallest CI runner, macOS's,
and takes 284 s on the shared 4-CPU machine, inside the five minutes UKLIB-SEC-PLAN.md U6
budgets (measured at M11). It took 295 s to 330 s, as the machine's load varied, until
the depth test's shapes issued 120 months on, which run as deep as those issued now,
moved to the full grid. The largest part is the core's 44 splice cases, about 110 s, each
scanned whole, and none is cut: the core-reach test's predicates are coarser than the
faults the cases are there for, and the review found that cutting by them would lose
`rpi_high-point2-d24` and `rpi_low-point7-d25`, which catch a fixed escalation
compounded at the RPI and the LPI's floor dropped. Then the 105 domain cases, about 25 s,
each on a model just read, every accepted edge projected, and the cold-depth test, about
18 s, which reads the model afresh for each of its 37 cold calls.

```bash
python -m pytest tests/test_pension_annuity_uk_sec.py -q
UKLIB_SEC_FULL=1 python -m pytest tests/test_pension_annuity_uk_sec.py -q   # the full grid
python -m pytest tests/test_model_conventions_uk.py -q -k PA_UK_SEC
```

<!-- BEGIN generated citation links -- regenerate with tools/gen_citation_links.py -->
[R10]: #uklib-pension_annuity-r10
[R11]: #uklib-pension_annuity-r11
[REG-R22]: #uklib-reg-r22
[REG-R27]: #uklib-reg-r27
[std]: #uklib-std
<!-- END generated citation links -->
