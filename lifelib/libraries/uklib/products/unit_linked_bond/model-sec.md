# In-Force Implementation Notes

**Status:** Draft, 2026-11-23. `ULB_UK_SEC` is [`ULB_UK_S`](model.md) taught to project
from a valuation date. Besides bonds issued at that date, it takes bonds already in force
there, in any month of their policy year, and bonds to be written in the ten years after
it, as lifelib's `basiclife/BasicTerm_SE` extends `basiclife/BasicTerm_S`. The product is
the one [`product-spec.md`](product-spec.md) specifies and
[`technical-notes.md`](technical-notes.md) models; this page says what running in force
changes. The suffix adds lifelib's letters to `S`: `E` for in force, as in
`BasicTerm_SE`, and `C` for the compiled form, as in `basiclife/BasicTerm_SC`, which the
model's next step adds (UKLIB-SEC-PLAN.md U2). Until then it runs in modelx alone.

> **This is a mechanics demonstration, not a pricing or reserving result.** The model is
> `ULB_UK_S` on another time axis, and it reads `ULB_UK_S`'s assumption tables in place,
> every assumption unchanged: the contractual mechanics are sourced, and every rate is a
> **[std]** standardization, the mortality basis a placeholder for the CMI's assured-lives
> tables, which are restricted to Authorised Users [R8] [REG-R30]. Replace them with
> company data and licensed tables before drawing any conclusion from the numbers.

## Run it

```bash
python products/unit_linked_bond/run_sec.py            # point 1: the anchor cell, issued at t = 0
python products/unit_linked_bond/run_sec.py 7          # point 7: the anchor cell in force 30 months
python products/unit_linked_bond/run_sec.py --block    # every model point, summed row by row
```

The first prints the anchor cell's first twelve rows of cash flows, with the policy
counts behind them. Three lines to the same thing for point 7:

```python
import modelx as mx
model = mx.read_model("products/unit_linked_bond/ULB_UK_SEC")
model.Projection[7].result_cf()
```

`Projection` takes a `point_id`, as `ULB_UK_S`'s does; it will take `idx`, a point's
position in the table, once the model compiles, and the runner takes its key from the
model either way. `result_cf()` has `ULB_UK_S`'s columns — `pols_if`, `av_pp`,
`amc_charges`, `gmdb_charges`, `further_costs`, `tax_provisions`, `withdrawals`,
`claims_death`, `claims_surrender`, `unit_releases`, `death_strain`, `expenses` and
`net_cf` — with one row per month from the valuation date, `t = 0 … proj_len() − 1`, and
`result_uf()` the unit fund recursion on the same rows, per policy, column for column as
`ULB_UK_S`'s. `result_pols()` sets out the counts behind them: `pols_if`, `pols_new_biz`,
then the month's deaths and surrenders in processing order, and the survivors of the
frame's last month.

`--block` projects every point and releases its ItemSpace once its frame is read, so the
run holds the cells of one point at a time. Deleting it, `del model.Projection[7]`, is not
enough: an ItemSpace sits in reference cycles, which only Python's cyclic collector frees,
so the runner collects after each release. It freezes everything alive (`gc.freeze()`)
once the model and its table are read, and again once it has asked every point for its
frame, so that each collection scans only what the block has made since. It keeps the
block's sum as it goes, compensated as pandas sums a `groupby`, so that the block is, bit
for bit, the frames concatenated and summed by `t`. The block leaves out `av_pp`, the unit
fund per policy, which summed over the points is no amount of anything; every other
column is a flow of the month or the count that weights it.

The runner is uslib Term's, so it already takes `--cython`, which runs the compiled model
in place of modelx, building it first with the repository's `tools/build_sec_cy.py`, and
`--build DIR`, which runs a build made elsewhere. The model compiles from its next step
on, which brings the build's `sample_sec.py` and `spec_sec.py`; until then a build stops,
saying why. A `lifelib.create()` copy carries no `tools/`, and there `--cython` stops
before building, saying so.

## Two clocks

The model runs on two clocks, and each formula reads the one its quantity belongs to.

- **`t`, the valuation clock**, counts months from the valuation date. `t = 0` is the
  valuation month for every model point, however old the bond, and the frame runs
  `t = 0 … proj_len() − 1`, where `proj_len()` is the number of months from the valuation
  date to the end of the frame: the limiting age, or the month the fund runs out.
- **`duration_mth(t)`, the policy clock**, counts the months the bond has been in force at
  time `t`: `duration_mth(t) = duration_mth_init() + t`, with `duration_mth_init()` read
  from the model point. The contract runs on it: `duration(t) = duration_mth(t) // 12`,
  `policy_year(t) = duration(t) + 1`, the key of the surrender table, of the 5% allowance
  and of the allowance-exhaustion step, and `age(t) = age_at_entry() + duration(t)`, age
  last birthday, the mortality table's, as in `ULB_UK_S`. `BasicTerm_SE` reaches the same
  numbers by adding one a month, a recursion as long as the frame; the closed form needs
  no such chain of calls.

Point 7 is the anchor cell in force 30 months. At `t = 0` it is in policy year 3 at
attained age 67, with a fund of 94,328.86 a policy, and its frame has 323 rows,
`t = 0 … 322`; S projects the same months as its rows 30 to 352. Point 11 is the GMDB
point to be issued 13 months after the valuation date: `duration_mth(0) = −13`, it is on
the books from `t_entry() = 13`, rows 0 to 12 are zeros, and its frame has 366 rows.

| Read on the policy clock | Read on the valuation clock |
|---|---|
| the mortality table at the attained age; the surrender table by policy year, its last year for every later one; the allowance-exhaustion step from policy year 21; the 5% allowance, accrued by policy year for twenty years; the limiting age, the end of cover | expense inflation, `inflation_factor(t) = 1.025^(t // 12)` |

Expense inflation alone runs on `t`, stepping on each anniversary of the valuation date, so
the maintenance charge is in valuation-date pounds, for every point alike. Acquisition,
£300 per bond issued, is charged in the issue month and not inflated, as in
`basiclife/BasicTerm_SE`. The fund return, the return shock and every other Reference is a
flat rate, the same on either clock, and the rolling withdrawal cap is a twelfth of the
annual one each month, so no input reads a month before the valuation date.

Because row `t` is the same month for every point, the frames of a block line up and sum
row by row, which is what `run_sec.py --block` prints:

```python
import pandas as pd
frames = [model.Projection[p].result_cf() for p in model.Data.model_point_table().index]
block = pd.concat(frames).groupby(level="t").sum()
```

On a point issued at `t = 0` the two clocks coincide, and the model computes what
`ULB_UK_S` computes: every cell the two models share agrees, but two whose meaning
changed, `pols_if_init()`, now the count already in force at the valuation date, 0 for new
business, and `model_point()`, a row of another table; on S's point 3, whose fund the
depletion threshold ends a month before `ULB_UK_S` does (*Where the fund runs out*), over
the months both frames run alike. `ULB_UK_S` charges acquisition on the count in force at
`t = 0`, which on such a point is the count issued, so the two agree at any count.

## The in-force interface

The model point table is `model_point_table_sec.csv`. It carries `ULB_UK_S`'s columns, its
count restated as the in-force interface under `basiclife/BasicTerm_SE`'s names, its fund
at outset under the name of the cell that reads it, and one column of opening state more.
Each state column is per policy in force, so that `policy_count` is the one weight on
every flow, and each is measured at the valuation instant, the start of month 0, before
any month-0 event (USLIB-SEC-PLAN.md D6). Each is history: what the bond has earned, borne
and paid out since issue, never re-derived from a Reference, which is an assumption from
the valuation date on, so that a Reference changed there reaches back over no month
already run (UKLIB-SEC-PLAN.md K14, §9 item 5):

| Column | Unit | Measured at | Meaning |
|---|---|---|---|
| `policy_count` | bonds, not necessarily whole | for a point in force, the start of month 0, before any month-0 event; for any other, its issue month | the bonds in force at the valuation date, for a point already in force; the bonds issued, for one issued at or after it |
| `duration_mth` | whole months | the valuation date | the bond's age in months: positive in force, 0 for a bond issued at the valuation date, `−k` for one to be issued `k` months later, with `k` at most 120 as shipped |
| `av_pp_init` | pounds per bond, above 0 | for a point in force, the start of month 0, before the month's growth, charges and cancellations; for any other, its issue month | the unit fund, the bid value of units the frame opens with: `av_pp(0)` in force, the fund at outset otherwise, the premium on every shipped point |
| `wd_cum_pp_init` | pounds per bond, 0 or more | the end of month −1, after its cancellations: the start of month 0 | the withdrawals and adviser charges cancelled since issue, the total the 5% allowance is measured against and the guaranteed minimum death benefit is net of; 0 on a point not yet in force |

`ULB_UK_S` re-derives both from References where its frame opens, which a Reference
changed at the valuation date would rewrite back to issue. Its fund is the premium grown
at `fund_return` and charged at the bond's rates from issue, so a market that has fallen
since issue, which no flat return set at the valuation date gives, is in the column and
not in S: a test projects point 7 on 60% of the fund S carries there, and its fund runs out
years earlier. And its withdrawals since issue are its pattern run from issue, so a
withdrawal taken once, or a pattern changed since, is in the column and not in S: the
guarantee opens from it, `max(0, P − wd_cum_pp_init)`, so a test opens point 9, whose
pattern has drawn its whole premium, at half of it withdrawn, and the guarantee is in the
money from its first month.

Nothing else of the contract is rebuilt from the References of the day. The allowance
accrued is a closed form on the policy year from issue, `P × min(y, 20) × 5%`, and the
excess gain the withdrawals since issue less it. The allowance-exhaustion step reads the
policy year. The withdrawal cap is a twelfth of `7.5% × max(UF′, P)` each month, which
reads no withdrawal of the twelve months before. The trailing return that drives the
performance multiplier is `fund_return + return_shock`, two flat References; a projection
that drew it from a path of returns would carry the last twelve months' as state.

| `ULB_UK_S` | `ULB_UK_SEC` | Why |
|---|---|---|
| `pols_if_init` (1.0) | `policy_count` | The count, under BasicTerm_SE's name. `pols_if_init()` now means the count in force at the valuation date, 0 for a point issued at or after it |
| — | `duration_mth` | The policy clock, in months, any month of a policy year |
| `uf_init` | `av_pp_init` | The fund the frame opens with, under the name of the cell that reads it; S's accessor, `av_init_pp`, is gone |
| — | `wd_cum_pp_init` | `ULB_UK_S` restarts the withdrawals since issue at 0 where its frame opens, and so the guarantee at the premium |

The columns carried over are read as `ULB_UK_S` reads them. For a bond in force, the
facts they record are still those at issue, or the elections that run from the valuation
date on:

| Column | Unit | Measured at |
|---|---|---|
| `point_id`, `policy_id` | labels | — |
| `age_at_entry` | years, age last birthday | issue, not the valuation date: `age(0)` is the attained age there |
| `sex`, `lives` | codes, as in `ULB_UK_S`'s table | issue |
| `premium` | pounds | issue: the single premium, which the withdrawal cap's floor, the allowance, the guarantee and the scheduled withdrawal are measured on |
| `n_segments` | a whole number, 1 or more | the segments held; reported only, in `av_per_segment_pp` |
| `db_uplift` | a factor, 1 or more | issue |
| `amc_rate`, `further_costs_rate`, `tax_provision_rate`, `oac_rate` | rates a year | the rates charged from the valuation date on |
| `wd_pattern`, `wd_rate_custom` | a code, a rate a year | the election from the valuation date on |
| `gmdb_flag` | True or False | issue |

Three more columns, `row_kind`, `source_policy_id` and `source_mth`, record where the
generator took each shipped row from (below). No formula reads them, and an in-force
extract need not carry them: without them the model projects the same numbers, and
`run_sec.py` runs.

`Data.model_point_table()` checks the table as it reads it, over all rows at once. The
first check that fails raises `ValueError`, naming the missing column or every point that
fails it: the four in-force columns are present; no `point_id` appears twice;
`policy_count` is a number, zero or more; `duration_mth` is a whole number of months,
below `2**53`, and −120 or more, future new business being written over a horizon,
`Data.future_horizon_mth`, 120 months as shipped, which set to 0 refuses future new
business altogether; `av_pp_init` is a number above 0, and `wd_cum_pp_init` a number,
zero or more, and 0 on a point not yet in force; the flag is True or False; each code is
one `ULB_UK_S` knows; the issue age is a finite number, the premium and the custom rate
amounts zero or more, the uplift 1 or more, the four charge rates from 0 to 1, and the
segments a whole number, 1 or more. `ULB_UK_S` meets most of these only when a projection
reaches them, and some never: a blank fund or charge rate reads as NaN, which every flow
then carries, and a blank flag reads as True.

A bond whose cover had ended by the valuation date, `duration_mth ≥ horizon_mths()`, the
limiting age, reads, but `proj_len()` refuses it, naming the point: the end of cover is
the product's rule, not the table's. So does a bond the contract does not issue
([`product-spec.md`](product-spec.md)): one issued below 18, `Projection.issue_age_min`,
the youngest age the mortality table rates, though the product admits issue from 3
months, or at or past `omega_age`. Each bound is a lower-case Reference, the contract a
compiled model's caches will be sized from: a frame of at most 1,224 months and the
horizon, and ages from 18 to `omega_age` on the mortality table. So does a point read
under a Reference outside its domain, each named: `fund_return` or `inflation_rate` below
−1, under which S's monthly rate has no real value or the inflation factor changes sign
each year; `mort_be_factor`, `wd_allowance_rate` or `allowance_years` below 0, under which
a mortality rate, a withdrawal or the allowance accrued is negative; and a
`depletion_threshold` that is not a finite number, zero or more. And so does a bond whose
opening fund is at or below the threshold (*Where the fund runs out*). A loop over the
block meets such a row only when it reaches it, after projecting the points before it,
so `run_sec.py --block` asks every point for its frame before it projects any, and stops
before it prints anything.

`surr_rate` keeps `ULB_UK_S`'s `min(surr_rate_cap, w_base × M_perf × M_allow)`, and refuses
a rate outside 0 to 1, or NaN, in the month it first leaves, naming the point, the month,
the rate and the References that make it: the table's rates are probabilities, which
`Data` holds to 0 to 1, but the multipliers and the cap are References, and past 1 S's
monthly rate is a complex number, below 0 its surrenders add policies.

The assumption tables are checked before a value of them is read, each in the cell the
projection takes its extent from: `Data.mort_age_first` and `mort_age_last` for the
mortality table, whose two sexes must run over the same ages, one row an age, without a
gap or a repeat, each rate a number from 0 to 1; and `Data.surr_last_year` for the
surrender table, policy years from 1 without a gap, each rate from 0 to 1. A key is read
by its value, so an age written `35.0` is 35. Each refusal names the file and the column;
the surrender table's names its lines, and the mortality table's its keys, sex and age,
because `ULB_UK_S`'s reader sorts the table as it reads it. A read at an attained age
outside the mortality table is refused by the one cell that reads it, naming the point,
where `ULB_UK_S`'s lookup raised `KeyError`; the surrender table takes its last year for
every later one, as `ULB_UK_S` does, so no read is beyond it.

## The model points

No row of `model_point_table_sec.csv` is typed by hand. Every one is generated from
`ULB_UK_S` and its table by `tests/uk_sec_support.py`, from the `ULB_UK_SEC` entry in its
`SEC_SPECS`, and the tests regenerate it and compare, so an edit to a `ULB_UK_S` row
reaches it or fails the suite. In the source repository,
`python tools/gen_sec_points.py ULB_UK_SEC` writes it.

| Point | Kind | From | At the valuation date |
|---|---|---|---|
| 1 to 6 | twin | S points 1 to 6 | issued at `t = 0`: `ULB_UK_S`'s anchor cell and its variants, the accumulation cell, the adviser charge, the GMDB, the 101% uplift and the custom 3% |
| 7 | derived | S point 1 at S month 30 | the anchor cell mid-way through policy year 3, 12,500.00 withdrawn |
| 8 | derived | S point 3 at S month 66 | the adviser charge mid-way through policy year 6, its withdrawals and charges since issue 498.69 past the allowance |
| 9 | derived | S point 4 at S month 240 | the GMDB point in policy year 21, its whole premium withdrawn and its guarantee 0, the step on and the allowance spent |
| 10 | derived | S point 1 at S month 352 | in the last month before its fund is exhausted: a one-row frame |
| 11 | future | S point 4, 13 months on | to be issued at `t = 13` |

A derived row's `policy_count` is the count `ULB_UK_S` carries into that month, its
`pols_if(d)`, and its state what S carries there, so the row continues the S projection
from there: point 7 opens with 0.901766 bonds, a fund of 94,328.86 a bond and 12,500.00
withdrawn since issue, and point 9 with 0.107986 bonds, a fund of 41,262.73 and the whole
premium withdrawn. Its `policy_id` is the S row's with the month appended,
`ULB-000001-M30`, and a future row's carries the months to issue, `ULB-000004-F13`. Row `t`
of a generated point is month `t + source_mth` of its S point.

No committed row holds the guarantee in the money, because no state `ULB_UK_S` reaches at
its shipped References does after the issue month: its GMDB point's fund grows faster than
its 5% withdrawals erode the guarantee, and in its issue month the guarantee exceeds the
uplifted fund after the month's withdrawal by £82.88, on the death benefit alone; the
rider charge, on the fund before the withdrawal, is 0 throughout. So the tests reach it
otherwise: the splice adds the GMDB point at a 4% AMC, in the money from its sixth month,
and a test writes point 9's withdrawals since issue at half its premium.

## Counts and timings

`pols_if_init()` is the count in force at the valuation date: `policy_count` for a point
already in force, 0 for any other. `pols_new_biz(t)` is `policy_count` in the issue month,
the month with `duration_mth(t) = 0`, and 0 in every other. `pols_if_at(t, timing)` keeps
`ULB_UK_S`'s three timings and adds `basiclife/BasicTerm_SE`'s `"BEF_NB"`:

- `"BEF_NB"`, the count carried in from month `t − 1`, before month `t`'s new business:
  `pols_if_init()` at `t_entry()`, the first month on the books, and the survivors of
  month `t − 1` after it;
- `"BEF_DECR"`, that count plus `pols_new_biz(t)`, before month `t`'s decrements, which
  `pols_if(t)` returns;
- `"BEF_SURR"`, after the month's deaths, before its surrenders;
- `"AFT_DECR"`, the end of the month, after its deaths and surrenders, which is `"BEF_NB"`
  at `t + 1` exactly, and 0 in the frame's last month.

Any other timing raises. The survivors carried into month `t` are those of month `t − 1`'s
`"BEF_DECR"` count, which `"BEF_NB"` forms itself, as its own value at `t − 1` plus that
month's new business, exactly the sum `"BEF_DECR"` returns. So the chain of calls from
month `t` back to `t_entry()` is one cell a month, where `ULB_UK_S`'s `pols_if` chain runs
three. The unit fund's is one cell a month too, where `ULB_UK_S`'s runs four (*Departures*).
On a model just read, a cold `net_cf` in the frame's last month runs at most 10 cells
deeper than one a month, at each shape's longest cover, issued at 18 now and 120 months
on: 1,224 months on the accumulation cell, whose cold `net_cf` runs 1,232 deep, where
`ULB_UK_S`'s fund alone would run about 4,900; each other chain, the withdrawals since
issue, the excess gain and the guarantee, is one cell a month too.

The roll-forward closes as

```
pols_if(t) − pols_if_at(t + 1, "BEF_NB")
    = pols_death(t) + pols_surr(t) + pols_maturity(t)
```

at every `t` of every frame, and `pols_if(t + 1)` adds `pols_new_biz(t + 1)` to the count
on the left. `pols_maturity` holds the survivors of the frame's last month: those still
holding a bond whose fund has just been drawn to nothing, or the population at the
limiting age. It pays nothing.

Cover is `is_active(t)`, `0 ≤ duration_mth(t) < horizon_mths()`, issued and short of the
limiting age, and outside it, before issue and from the limiting age on, the unit fund and
every count are zero, and so every cash flow. No count evaluates a decrement rate there,
and no table is read at a policy year or an attained age the bond does not have:
`mort_rate`, `surr_rate_base`, `allow_factor`, the allowance, the guarantee, the
withdrawal and its cap are zero outside cover, before any table or rate is read. Cover
reads the limiting age alone, not `proj_len()`: the frame also ends where the fund runs
out, which `fund_exhaust_mth()` finds by projecting the fund, and the fund reads cover. So
in the months after the fund is exhausted and before the limiting age a bond is in cover
and holds no units, and there the counts are zero because the frame has ended.

## Where the fund runs out

`ULB_UK_S` ends its frame at the first month whose fund opens on 0 or less. The withdrawal
cap draws a fund to nothing on a subtraction whose exact value is 0: the month's fund
after charges, less the adviser and rider charges and the withdrawal, which the cap sets
to what those leave. Where nothing but the withdrawal is cancelled, as on S's points 1, 4
and 5, the float is 0 exactly. Where an adviser charge or a rider charge is cancelled
beside it, the float is a rounding of either sign, floored at 0, and which it is turns on
the fund's last bit. S's point 3, its adviser charge beside its withdrawal, closes its
fund on 3.39e-15 at the end of policy month 322, so S projects month 323 on that: 0.0194
bonds, a maintenance charge of £0.18 against an AMC of 6e-20, and its survivors maturing
a month later. A fund read back from a CSV an ulp off, or the same model compiled with
another order of operations, closes it on 0 instead, and ends a month sooner.

So this model ends the frame at the first month whose fund opens at or below
`depletion_threshold`, half a pence, uslib `VA_US_SEC`'s value (UKLIB-SEC-PLAN.md §9 item
10; USLIB-SEC-PLAN.md §7.7, *Record — M9*): far above any rounding of a fund in pounds and
far below any fund worth projecting. `fund_exhaust_mth()` searches the fund from
`t_entry()`, ascending, the one loop that reads beyond `t + 1`, which R2 admits; from 0 it
would find a bond issued later exhausted before its issue. `proj_len()` refuses a bond in
force whose fund opens at or below the threshold, which has nothing to project, and one
not yet in force whose fund at outset does.

Its effect on each of S's points, which a test holds:

| S point | `ULB_UK_S`'s frame | `ULB_UK_SEC`'s | Why |
|---|---|---|---|
| 1, 4, 5 | 353 | 353 | the fund closes on 0 exactly at the end of policy month 352 |
| 2, 6 | 660, 780 | 660, 780 | the fund never runs out, and the frame runs to the limiting age |
| 3 | 324 | 323 | the fund closes on 3.39e-15, at or below the threshold |

On point 3 every cell agrees with `ULB_UK_S`'s in each of the 322 months before the SEC
frame's last; in its last, every cell but where its survivors go, which leave here as
`pols_maturity(322)` and in S carry on into month 323; and the frame's net cash flow moves
by S's month 323 alone, −£0.18. The twin identity, in `tests/test_model_conventions_uk.py`,
holds the months before the last on point 3 and leaves the frame's end to that test
(`TWIN_FRAME_ENDS`).

## Departures from ULB_UK_S

Each formula that tested `t` against a contractual event now tests the policy clock, each
read at a month passed as `t` is a read at the policy month or year, and each recursion
opens at `t_entry()` from the opening state. Where `ULB_UK_S`'s test would have stayed
correct on the valuation clock, it moved anyway, so that cover has one definition. Eight
cells are new, and one of `ULB_UK_S`'s, `av_init_pp`, is gone, `av_pp_init` replacing it;
the twin identity names it as dropped, and a cell of `ULB_UK_S`'s that this model lacked
without saying so would fail it.

| Cells | `ULB_UK_S` | `ULB_UK_SEC` | Why |
|---|---|---|---|
| `duration_mth`, `duration` | `t`, `t // 12` | `duration_mth_init() + t`, `duration_mth(t) // 12` | The policy clock, opened from the model point |
| `t_entry`, `is_active`, new | — | `max(0, −duration_mth_init())`; `0 ≤ duration_mth(t) < horizon_mths()` | The first month on the books, and cover, read from the limiting age alone |
| `fund_exhaust_mth` | the first `t` from 0 whose fund is 0 or less | the first month from `t_entry()` whose fund is at or below `depletion_threshold`, as a policy month | *Where the fund runs out* |
| `proj_len` | `min(horizon_mths(), fund_exhaust_mth())`, from issue | the same less `duration_mth_init()`, from the valuation date; raises past cover, outside the contract's bounds, under a Reference outside its domain, and on an opening fund at or below the threshold | The frame starts at the valuation date |
| `av_pp`, `av_pp_at` | `av_pp(t) = av_pp_at(t − 1, "AFT_WD")`, four cells a month, from `uf_init` at 0 | `av_pp_init()` at `t_entry()`, then month `t − 1`'s growth, tax provision, charges and cancellations inline, in `av_pp_at`'s order and floats, one cell a month; `av_pp_at` reads `av_pp`; 0 outside cover | One cell a month (D5); the same float as S's in every month |
| `wd_cum_pp`, `gmdb_guarantee_pp` | 0 before `t = 0` | `wd_cum_pp_init()` before `t_entry()` | The withdrawals since issue are history, and the guarantee opens from them |
| `pols_if`, `pols_if_at`, `pols_if_init` | a recursion through `"AFT_DECR"`, three cells a month, from the column's 1.0 at 0 | `"BEF_DECR"`, one cell a month from `t_entry()` through `"BEF_NB"`; `pols_if_init()` is 0 unless in force | Bonds in force at the valuation date open the count; new business joins it in its issue month |
| `pols_death`, `pols_surr`, `"BEF_SURR"` | unguarded | zero outside cover and the frame, before a rate is read | No count evaluates a rate outside cover |
| `mort_rate`, `surr_rate_base`, `allow_factor`, `allowance_cum_pp`, `wd_cap_pp`, `wd_pp`, `gmdb_charge_pp` | unguarded: no `ULB_UK_S` frame has a month outside cover | zero outside cover, before any table or rate is read; the tables' extents from `Data`, a read past the mortality table refused by name | Before issue S's tables raise `KeyError`, and its allowance is negative |
| `surr_rate` | `min(cap, w_base × M_perf × M_allow)` | the same, and a rate outside 0 to 1, or NaN, refused in its month | Past 1 S's monthly rate is complex; below 0 its surrenders add policies |
| `inflation_factor` | `1.025^duration(t)`, from issue | `1.025^(t // 12)`, from the valuation date | Unit costs in valuation-date pounds (D7) |
| `expenses` | acquisition on `pols_if(t)` at `t = 0` | on `pols_new_biz(t)` | A bond in force bears no acquisition, one issued later bears it in its issue month, per bond issued and not inflated, as in `basiclife/BasicTerm_SE` |
| `check_pols_roll_fwd_resid` | `pols_if(t + 1)` | `pols_if_at(t + 1, "BEF_NB")` | The next month's new business is no part of month `t`'s movement |
| `check_pols_roll_fwd` | tolerance on `pols_if_init()` | tolerance on `policy_count()` | S's `pols_if_init` is 0 on new business here |
| `result_pols`, new | — | `pols_if`, `pols_new_biz`, `pols_death`, `pols_surr`, `pols_maturity` | The counts behind `result_cf()`, after `basiclife/BasicTerm_SE`'s `result_pols()` |
| `policy_count`, `duration_mth_init`, `av_pp_init`, `wd_cum_pp_init`, `pols_new_biz`, new | — | the interface's columns, and the new business of each month | *The in-force interface*; *Counts and timings* |

Of the cash flows, the change of clock moves the maintenance expense alone, and `net_cf`
with it. Point 7 carries that expense in valuation-date pounds, so its `expenses(t)` is
`ULB_UK_S`'s `expenses(30 + t)` with S's factor, `1.025^((30 + t) // 12)`, taken out and
`1.025^(t // 12)` put in: 1.025² less at `t = 0`. Its `pols_if`, its fund, its charges, its
withdrawals, both claims columns, `unit_releases` and `death_strain` are `ULB_UK_S`'s from
month 30 on. Point 11 is `ULB_UK_S`'s point 4 thirteen months on in those columns too; its
maintenance expense is `1.025^(t // 12 − (t − 13) // 12)` above S's at each `t`, and its
acquisition £300 exactly.

`mort_rate` caps the annual rate at 1, written `min(q, 1.0)`, the product first and the
bound second, as `ULB_UK_S` writes it, so that a NaN stays NaN where `min(1.0, q)` would
read it as certain death; wherever `q` is a number the two are the same float. At the
shipped `mort_be_factor` of 0.8 the rate stays at or below 0.8 to the end of every frame,
and `Data` refuses a table rate past 1; the product passes 1 through the factor, from
attained age 111 at 1.25, which a test shows. The surrender rate's bound keeps
`ULB_UK_S`'s order, `min(cap, …)`: it is no cap on mortality.

## Tests

- **The twin identity**, in `tests/test_model_conventions_uk.py`: on points 1 to 6, every
  cell of `ULB_UK_S`'s agrees at every argument `ULB_UK_S` evaluates in its own sweep, to
  1e-9 relative with no absolute floor, but for `pols_if_init` and `model_point`, and
  `av_init_pp`, which the spec names with its reason; a cell this model lacked would fail
  it. On point 3 it holds every month but the SEC frame's last, which the threshold's
  test holds. So `ULB_UK_S`'s worked example, which `tests/test_unit_linked_bond_uk.py`
  asserts to the penny, holds here with no number restated. The same suite holds the
  model to the conventions every `_SEC` model meets: every frame starts at `t = 0`,
  `pols_if` is the `"BEF_DECR"` count, new business enters once at its `policy_count`,
  nothing happens before issue, and the in-force columns are present.
- **The splice**, in `tests/test_unit_linked_bond_uk_sec.py`: each `ULB_UK_S` point
  restated in force at months 1, 11, 12, 23, 24, 37, 59, 60, 119, 120 and 125, about the
  surrender bands' edges, 239, 240 and 241, about policy year 21, where the step starts,
  the allowance stops accruing and the GMDB of the anchor's pattern runs out, and 322, 352,
  659 and 779, each frame's last month, continues the S projection in every cell the two
  share but `proj_len`, and in both reports, to 1e-9 relative with no absolute floor, but
  the residuals and an exhausted frame's last month, which closes a fund on a subtraction
  whose exact value is 0, at a floor of 1e-9. Every switch that ships off is on in both
  models: a return shock of −0.75, which takes the performance multiplier to its cap of 2,
  and a surrender cap of 0.25, which binds from policy year 21; inflation, the one input on
  the valuation clock, is 0 in both. Three variants of S's points, in a copy of S's table
  that is never committed, reach what S's own cannot: the GMDB point at a 4% AMC, in the
  money; the custom pattern at 9%, above the 7.5% cap; and the adviser charge with the
  GMDB beside it. A core of 28 of the 111 splice cases and 7 of the 17 future ones runs by
  default, and the full grid with `UKLIB_SEC_FULL=1`; a test asserts the core reaches every
  branch, opening-state column, kind of valuation month and side of every `min` and `max`
  the full grid reaches.
- **Future new business**: issued 1 and 12 months after the valuation date, each S point is
  the S projection moved on, with zeros before issue and no rate evaluated there, and so is
  each variant issued a month on, the GMDB point 13 months on and the custom 3% 25.
- **How it computes**: on every row of the splice's grid, after its reports, its checks
  and every monthly cell at every month, no cell has been called at a negative month, none
  on the books read a month before `t_entry()`, none read a month later than `t + 1` but
  the exhaustion search's reads of the fund to the frame's end, and none raised; the
  search reads the fund alone, from `t_entry()`. On a fresh read of the committed model,
  `duration_mth(500)` evaluates `duration_mth` once, the policy clock being a closed form,
  and every point's reports and checks run under modelx's recursion limit lowered to 40,
  which a recursion backward over the frame would exceed. Each chain, called cold in the
  last month at each shape's longest cover, runs one cell a month back to `t_entry()` and
  at most 16 more; and the inline fund is `av_pp_at`'s, bit for bit.
- **Counts**: the roll-forward closes; `result_pols()` is S's counts with `pols_new_biz`
  beside them; multiplying `policy_count` by 2.5, with every switch that ships off on,
  multiplies every flow and counted cell and moves no per-policy value, the fund at each
  timing, the withdrawals since issue and the guarantee among them; and the check, its
  tolerance scaled by the count, closes on a million bonds.
- **Validation and regeneration**: each malformed row of the table, 51 cases, is refused
  naming its point; the horizon is a Reference; a point past its cover, outside the
  contract's bounds or under a Reference outside its domain, 15 cases, is refused by
  `proj_len()`, each bound just inside it and each moved past a committed point, and
  `run_sec.py --block` refuses such a point before printing anything; so is a fund at or
  below the threshold, at exactly it, part of it and a rounding above 0, where the least
  fund past it projects; a surrender rate outside 0 to 1 is refused in its month; each
  assumption table a reader cannot read, 21 cases, is refused naming its lines or its
  keys, and a read beyond the mortality table naming the point; keys written as floats
  read as `ULB_UK_S` reads them; the edges of the interface and of each bound are
  accepted; every state `ULB_UK_S` reaches, as shipped and under the splice's switches, is
  accepted in force, but the fund S runs on at 3.39e-15, which is refused as exhausted;
  and the committed table is what `ULB_UK_S` generates.
- **The product's own facts**: the two clocks on the shipped points; the committed rows,
  in force and issued later, continuing their S points at the shipped assumptions but for
  inflation; each history column read, not recomputed, the fund written at 60% of S's and
  the withdrawals since issue at half the premium and at 10,000 more, each projected
  through (UKLIB-SEC-PLAN.md K14); the threshold's effect on each S point, and a fund that
  reaches the threshold exactly exhausted there; the surrender bands, the step and the
  allowance on the policy clock; expense inflation on the valuation clock at the shipped
  2.5%, which only this test sees; acquisition on new business alone; every guarded cell's
  value outside cover, and after an exhausted frame; the block; an extract without the
  generator's three columns, labelled otherwise, projecting the same numbers;
  `run_sec.py`'s numbers, for a point and for the block, and its sum, and its `--cython`
  stopping where no repository is above it; no cell's parameter defaulted but the `claims`
  total's; the docstrings, read through docutils as the docs build reads them where
  docutils is installed; and the shared input tables.
- **The cap**: on the accumulation cell under the splice's References and a
  `mort_be_factor` of 1.25, the product of the table rate and the factor passes 1 from
  attained age 111, policy month 552. In both models `mort_rate` and `mort_rate_mth` are
  the float 1.0 there; every bond in force at the start of that month dies in it, and none
  is in force after it; the reports hold finite floats; and every cell the two models
  share agrees, issued now and 12 months on, and restated in force the month before the
  cap, to 1e-9 relative with no absolute floor. And a NaN sent to the cap, through
  `mort_be_factor`, stays NaN.

```bash
python -m pytest tests/test_unit_linked_bond_uk_sec.py -q
UKLIB_SEC_FULL=1 python -m pytest tests/test_unit_linked_bond_uk_sec.py -q   # the full grid
python -m pytest tests/test_model_conventions_uk.py -q -k ULB_UK_SEC
```

<!-- BEGIN generated citation links -- regenerate with tools/gen_citation_links.py -->
[R8]: #uklib-unit_linked_bond-r8
[REG-R30]: #uklib-reg-r30
[std]: #uklib-std
<!-- END generated citation links -->
