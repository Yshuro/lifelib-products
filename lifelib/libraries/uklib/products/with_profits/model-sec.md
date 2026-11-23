# In-Force Implementation Notes

**Status:** Draft, 2026-11-23. `WP_UK_SEC` is [`WP_UK_S`](model.md) taught to project from
a valuation date. Besides policies issued at that date, it takes policies already in force
there, in any month of their policy year, and policies to be written in the ten years after
it, as lifelib's `basiclife/BasicTerm_SE` extends `basiclife/BasicTerm_S`. The product is
the one [`product-spec.md`](product-spec.md) specifies and
[`technical-notes.md`](technical-notes.md) models; this page says what running in force
changes. The suffix adds lifelib's letters to `S`: `E` for in force, as in `BasicTerm_SE`,
and `C` for the compiled form, as in `basiclife/BasicTerm_SC`, which the model's next step
adds (UKLIB-SEC-PLAN.md U2). Until then it runs in modelx alone.

> **This is a mechanics demonstration, not a pricing or reserving result.** The model is
> `WP_UK_S` on another time axis, and it reads `WP_UK_S`'s assumption tables in place,
> every assumption unchanged: the with-profits mechanics are sourced, and every rate is a
> **[std]** standardization. Bonus declarations, MVR scales and lapse experience are not
> published, and the mortality table is an ONS-shaped proxy, not a CMI table. A
> deterministic run understates the cost of guarantees, which is convex in the fund
> return. Replace the assumptions with licensed tables and company experience, and the
> run with a market-consistent stochastic one, before drawing any conclusion from the
> numbers.

## Run it

```bash
python products/with_profits/run_sec.py            # point 1: the worked example's bond, in force 60 months
python products/with_profits/run_sec.py 7          # point 7: the down-market bond issued at t = 0
python products/with_profits/run_sec.py --block    # every model point, summed row by row
```

The first prints the first twelve rows of point 1's cash flows, which `WP_UK_S` projects as
its rows 60 to 71, with the policy counts behind them. Three lines to the same thing for
point 7:

```python
import modelx as mx
model = mx.read_model("products/with_profits/WP_UK_SEC")
model.Projection[7].result_cf()
```

`Projection` takes a `point_id`, as `WP_UK_S`'s does; it will take `idx`, a point's
position in the table, once the model compiles, and the runner takes its key from the
model either way. `result_cf()` has `WP_UK_S`'s columns — `pols_if`, `asset_share`,
`premiums`, `claims_death`, `claims_surrender`, `claims_maturity`, `withdrawals`,
`expenses`, `shareholder_transfers`, `smoothing_cost` and `net_cf` — and `result_payout()`
`WP_UK_S`'s payout machinery, each with one row per month from the valuation date,
`t = 0 … proj_len() − 1`. `result_pols()` sets out the counts behind them on the same
rows: `pols_if`, `pols_new_biz`, then the month's deaths and surrenders in processing
order, and the survivors of the frame's last month.

`--block` projects every point and releases its ItemSpace once its frame is read, so the
run holds the cells of one point at a time. Deleting it, `del model.Projection[7]`, is not
enough: an ItemSpace sits in reference cycles, which only Python's cyclic collector frees,
so the runner collects after each release. It freezes everything alive (`gc.freeze()`)
once the model and its table are read, and again once it has asked every point for its
frame, so that each collection scans only what the block has made since. It keeps the
block's sum as it goes, compensated as pandas sums a `groupby`, so that the block is, bit
for bit, the frames concatenated and summed by `t`. It leaves out `asset_share`, an amount
per policy, which no sum of the points makes a block's. Its projection years carry the
count of their first month and the flows of all twelve.

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
  date to the end of the projection: the endowment's maturity, the bond's limiting age, or
  the month a withdrawal election exhausts the bond's units, whichever comes first.
- **`duration_mth(t)`, the policy clock**, counts the months the policy has been in force
  at time `t`: `duration_mth(t) = duration_mth_init() + t`, with `duration_mth_init()` read
  from the model point. The contract runs on it: `duration(t) = duration_mth(t) // 12`,
  `policy_year(t) = duration(t) + 1`, the lapse table's key and the guarantee dates',
  `age(t) = age_at_entry() + duration(t)`, the mortality table's, age nearest birthday, as
  in `WP_UK_S`; the declaration in the twelfth month of each policy year; the
  guarantee-imminent window; the single premium in the issue month; and the end of cover,
  `cover_end_mth()`, `12 × policy_term()` on the endowment and `12 × (omega_age −
  age_at_entry())` on the bond, `WP_UK_S`'s frame from issue but for the exhaustion.
  `BasicTerm_SE` reaches the same numbers by adding one a month, a recursion as long as
  the frame; the closed form needs no such chain of calls.

Point 1 is the worked example's bond, in force 60 months. At `t = 0` it is in its sixth
policy year at attained age 60, and its frame has 720 rows, `t = 0 … 719`; `WP_UK_S`
projects the same months as its rows 60 to 779, opening its frame late, on an
anniversary, `proj_start() = 12 × duration_inforce()`. Point 19 is the down-market bond to
be issued 13 months after the valuation date: `duration_mth(0) = −13`, it is on the books
from `t_entry() = 13`, rows 0 to 12 are zeros, and its frame has 280 rows, its units running
out at policy month 267.

| Read on the policy clock | Read on the valuation clock |
|---|---|
| the mortality table at the attained age; the lapse table by policy year; the declaration, in the twelfth month of each policy year; the guarantee dates and the twelve months before each; the single premium, in the issue month; the endowment's maturity and the bond's limiting age; the bonus rule's remaining term | expense inflation, `inflation_factor(t) = 1.03^(t // 12)` |

Expense inflation runs on `t`, stepping on each anniversary of the valuation date, for
every point alike (USLIB-SEC-PLAN.md D7; UKLIB-SEC-PLAN.md §9 item 4). The maintenance
charge is then in valuation-date pounds: `WP_UK_S` inflates from issue, so its bonds in
force carry five years of it in their first projected month and its endowment in force
twenty. The fund return and the bonus rate are levels of the model point, the same on
either clock, so nothing is re-based. WP has no acquisition expense and no commission.

Because row `t` is the same month for every point, the frames of a block line up and sum
row by row, which is what `run_sec.py --block` prints:

```python
import pandas as pd
frames = [model.Projection[p].result_cf() for p in model.Data.model_point_table().index]
block = pd.concat(frames).groupby(level="t").sum()
```

On a point issued at `t = 0` the two clocks coincide, and the model computes what
`WP_UK_S` computes: every cell the two models share agrees, but three whose meaning
changed, `pols_if_init()`, now the count already in force at the valuation date, 0 for new
business, `model_point()`, a row of another table, and `fund_exhaust_mth()`, whose
"never" is no longer 0 (*Where the units run out*, below).

## The in-force interface

The model point table is `model_point_table_sec.csv`. It carries `WP_UK_S`'s columns, one
of them restated as the in-force interface under `basiclife/BasicTerm_SE`'s name, a policy
clock column, three renamed to D6's vocabulary and two columns of state `WP_UK_S` lacks.
The count is the only weight on the flows, and every state column is per policy. Each is
measured at the valuation instant, the start of month 0, before any month-0 event, which
is `WP_UK_S`'s close of the month before (USLIB-SEC-PLAN.md D6). A declaration falls at the
end of a policy year's twelfth month, so on a point valued on an anniversary the
declaration that closed the year before is in the columns, and the first declaration the
projection makes is the one that closes the year under way. Each state column is history:
what the contract has accumulated, declared, charged or paid, never re-derived from a
Reference, which is an assumption from the valuation date on, so that a Reference changed
there reaches back over no month already run (UKLIB-SEC-PLAN.md K14, §9 item 5):

| Column | Unit | Measured at | Meaning |
|---|---|---|---|
| `policy_count` | policies, not necessarily whole | for a point in force, the start of month 0, before any month-0 event; for any other, its issue month | the policies in force at the valuation date, for a point already in force; the policies issued, for one issued at or after it |
| `duration_mth` | whole months | the valuation date | the policy's age in months: positive in force, 0 for a policy issued at the valuation date, `−k` for one to be issued `k` months later, with `k` at most 120 as shipped |
| `asset_share_init` | pounds per policy | the start of month 0 | the asset share, the retrospective accumulation, floored at 0 as `WP_UK_S` floors it: `WP_UK_S`'s `asset_share` of month −1 |
| `units_init` | units per policy | the start of month 0 | on the bond, the units held, which the premium bought and the withdrawals have cancelled; 0 on the endowment |
| `unit_price_init` | pounds per unit | the start of month 0 | on the bond, the with-profits unit price the declarations have raised the seed price to; on a policy not yet in force, the seed price its premium buys units at, an issue value |
| `attaching_bonus_init` | pounds per policy | the start of month 0 | on the endowment, the reversionary bonuses already added to the sum assured; 0 on the bond |
| `smoothed_payout_init` | pounds per policy | the start of month 0 | the smoothed payout the year-on-year cap works from; 0 where the asset share has floored at 0 |
| `bonus_rate_init` | a rate a year | the policy year under way | the declared bonus rate of the policy year under way: of every year with the bonus rule off, and of the year under way with it on; on a policy not yet in force, its first year's |
| `guar_charge_cum_pp_init` | pounds per policy | the end of month −1 | the guarantee charges taken since issue, which the charge's lifetime cap of 2% of the asset share is measured against |
| `smoothing_account_init` | pounds per policy in force | the end of month −1 | the estate's smoothing and guarantee cost on the exits since issue, over the policies in force: of either sign |

`WP_UK_S` carries the first five in its own columns on its in-force rows, and holds no
column for the last two. It restarts both cumulants at 0 where its frame opens, so a bond
it reopens in force charges on where its own projection from issue has stopped: the
down-market bond issued at the valuation date, point 7, stops charging at month 88, and
reopened at 60 without its charges it would charge again, its asset share parting from
`WP_UK_S`'s from issue. Its twins of `WP_UK_S`'s own in-force rows carry 0 in both, which is
what `WP_UK_S` assumes there. Here:

- `asset_share(t)` opens at `asset_share_init()` at `t_entry()`, `units(t)` at
  `units_init()`, `unit_price(t)` at `unit_price_init()`, the endowment's guarantee at
  `sum_assured() + attaching_bonus_init()` and `smoothed_payout(t)` at
  `smoothed_payout_init()`, each the balance the month opens with;
- `guar_charge_cum_pp(t)` opens at `guar_charge_cum_pp_init()`, which the cap's test reads
  in month 0;
- `smoothing_account(t)` opens at `smoothing_account_init() × pols_if_init()`;
- `bonus_rate(t)` is `bonus_rate_init()` in every policy year with the rule off, and with
  it on in the year under way at the valuation date, as `WP_UK_S`'s first projected year
  takes its column; each later year's rate is then declared by the rule, from the year
  before's.

No balance is needed at a second instant: a declaration costs the month's own opening
values, and no annual quantity reads the balance entering the policy year, so there is no
`_prev_anniv_init` column and no `_ytd_init`.

On a point issued at the valuation date each history column holds its issue value, and the
model is `WP_UK_S`. A model that dropped a column and rebuilt it from the References would
pass the splice wherever `WP_UK_S` and the splice rebuild it alike, so the tests write each
off its References' path and project through it.

| `WP_UK_S` | `WP_UK_SEC` | Why |
|---|---|---|
| `pols_if_init` (1.0) | `policy_count` | The count, under BasicTerm_SE's name. `pols_if_init()` now means the count in force at the valuation date, 0 for a point issued at or after it |
| `duration_inforce` (years) | `duration_mth` (months) | The policy clock, in months, any month of a policy year |
| `units`, `attaching_bonus`, `bonus_rate` | `units_init`, `attaching_bonus_init`, `bonus_rate_init` | D6's vocabulary: each is the value the projection opens with |
| — | `guar_charge_cum_pp_init`, `smoothing_account_init` | The cumulants `WP_UK_S` restarts at 0 where its frame opens |

The columns carried over are read as `WP_UK_S` reads them. For a policy in force, the
facts they record are still those at issue:

| Column | Unit | Measured at |
|---|---|---|
| `point_id`, `policy_id` | labels | — |
| `chassis`, `sex`, `tax_basis` | codes, as in `WP_UK_S`'s table | issue |
| `age_at_entry` | whole years, age nearest birthday | issue, not the valuation date: `age(0)` is the attained age there |
| `premium_single`, `premium_regular`, `sum_assured` | pounds, the amounts at issue | issue |
| `policy_term` | whole years | issue: 0 on the whole-of-life bond |
| `guarantee_dates` | policy anniversaries, `;`-separated | issue: blank on the endowment |
| `wd_rate`, `fund_return` | rates a year | the withdrawal election and the scenario's level |
| `asset_share_init`, `unit_price_init`, `smoothed_payout_init` | as above | `WP_UK_S`'s columns of these names, measured at the valuation instant |

Three more columns, `row_kind`, `source_policy_id` and `source_mth`, record where the
generator took each shipped row from (below). No formula reads them, and an in-force
extract need not carry them: without them the model projects the same numbers, and
`run_sec.py` runs.

`Data.model_point_table()` checks the table as it reads it, over all rows at once. The
first check that fails raises `ValueError`, naming the missing column or every point that
fails it: the ten in-force columns are present; no `point_id` appears twice;
`policy_count` is a number, zero or more; `duration_mth` is a whole number of months,
below `2**53`, and −120 or more, future new business being written over a horizon,
`Data.future_horizon_mth`, 120 months as shipped, itself a whole number of months below
`2**53`, which set to 0 refuses future new business altogether; each code is one
`WP_UK_S` knows, the chassis `UWP_bond` or `CWP_endowment`, the sex `M` or `F` and the tax
basis `life_net` or `pension_gross`; the age and the term are whole numbers, the amounts
zero or more, the withdrawal rate from 0 to 1 and the fund return a finite number above
−1, where the monthly return has a real value; the guarantee dates are blank or whole
anniversaries, 1 or more, and blank on the endowment, which has none; the endowment has a
term of a year or more and no units, the bond no term and no attaching bonus. Then the
opening state: the asset share, the units, the attaching bonus, the payout and the
guarantee charges are amounts, zero or more; the unit price a finite number above 0; the
bonus rate a finite number, zero or more, a declared bonus being floored at 0 by the
contract; and the smoothing account a finite number of either sign. A point not yet in
force holds no opening state, its seed price and its first year's bonus rate excepted,
which are issue values; a bond in force holds units, a bond whose units are spent being
encashed; and an endowment in force 11 months or fewer has no attaching bonus, to the
cent, its first declaration falling at the end of policy month 11. Each holds of every
state `WP_UK_S` reaches, as shipped and under the splice's References, which a test
asserts. `WP_UK_S` meets most of these only when a projection reaches them, and some
never: a guarantee date on the endowment would gate an exercise and the imminent window
there, and a fraction of a year in the age would be truncated by `int()`.

A point at or past the end of cover at the valuation date, `duration_mth ≥
cover_end_mth()`, reads, but `proj_len()` refuses it, naming the point: the end of cover is
the product's rule, keyed on the policy clock, not the table's. So does a point the
contract does not write ([`product-spec.md`](product-spec.md)): one issued below 18,
`Projection.issue_age_min`, the youngest age the mortality table rates, though the bond
admits issue from 3 months; a bond issued at or past the limiting age, `omega_age`; and an
endowment maturing past it, `age_at_entry() + policy_term() > omega_age`, whose last
attained ages the table may not rate, where `WP_UK_S` bounds no term and reads them at
`omega_age`. `omega_age` itself must lie above `issue_age_min` and at most a year past the
mortality table's last age. Each is a lower-case Reference, the contract a compiled
model's caches will be sized from: a frame of at most 1,224 months from issue age 18, on
either chassis, and the horizon, and attained ages from 18 to 119 on the mortality table.
A whole limiting age written as a float, `120.0`, is read as the `int` it is, so that the
frame is a whole number of months, as it will be compiled. And `proj_len()` refuses a bond
whose units run out in its first month on the books, which would leave no month to
project. On every point `proj_len()` also refuses a Reference off its domain (below). A
loop over the block meets such a row only when it reaches it, so `run_sec.py --block` asks
every point for its frame before it projects any, and stops before it prints anything.

The assumption tables are checked before a value of them is read, each by the cell the
projection takes its extent from, reading the file as it stands, so that a fault is named
by its line. The mortality table is checked by `Data.mort_age_first`: each age a whole
number, each sex `M` or `F`, each running from the table's first age to its last, one row
an age, none below 0, and each rate from 0 to 1. The lapse table is checked by
`Data.lapse_last_year`: policy years from 1 without a gap or a repeat on each chassis, each
chassis `UWP_bond` or `CWP_endowment`, each rate from 0 to 1. A key is read by its value,
so an age written `70.0` is 70. Each refusal names the file, the column and its lines. An
attained age outside the mortality table, which only a lowered `issue_age_min` admits, is
refused by `mort_rate`, naming the point and the age, where `WP_UK_S`'s lookup raised
`KeyError`.

## The model points

No row of `model_point_table_sec.csv` is typed by hand. Every one is generated from
`WP_UK_S` and its table by `tests/uk_sec_support.py`, from the `WP_UK_SEC` entry in its
`SEC_SPECS`, and the tests regenerate it and compare, so an edit to a `WP_UK_S` row reaches
it or fails the suite. In the source repository, `python tools/gen_sec_points.py WP_UK_SEC`
writes it.

| Point | Kind | From | At the valuation date |
|---|---|---|---|
| 1 to 4, 6 | twin | S points 1 to 4 and 6 | in force, as `WP_UK_S` opens them: the worked example's bond at +7% and −15%, on a 5% return, with the 5% withdrawal election, all in force 60 months; and the endowment, in force 240 months on a gross pension basis |
| 5, 7 | twin | S points 5 and 7 | issued at `t = 0`: the endowment, and the down scenario's bond with the withdrawal election, the one bond `WP_UK_S` issues at the valuation date |
| 8 | derived | S point 1 at S month 71 | the bond in its sixth year's last month, the declaration at the end of month 0 |
| 9 | derived | S point 2 at S month 68 | the down scenario as its market value reduction turns on, the smoothing cap's floor binding |
| 10 | derived | S point 2 at S month 92 | the down scenario as the corridor's ceiling binds |
| 11 | derived | S point 2 at S month 119 | the down scenario on its guarantee date, the MVR-free encashment in month 0 |
| 12 | derived | S point 2 at S month 242 | the down scenario with its asset share floored at 0, and its payout 0 with it |
| 13 | derived | S point 3 at S month 487 | the 5% bond in a month its charge cap binds |
| 14 | derived | S point 4 at S month 402 | the withdrawing bond in its last month, 99.10 units left: a one-row frame, ended by forced encashment |
| 15 | derived | S point 5 at S month 11 | the endowment at its first declaration, no bonus yet attaching |
| 16 | derived | S point 5 at S month 299 | the endowment's last month: a one-row frame, maturing |
| 17 | derived | S point 1 at S month 779 | the bond in its last month before the limiting age: a one-row frame, paying nothing |
| 18 | derived | S point 7 at S month 100 | the down-market bond past its charge cap, its charges stopped at 88 |
| 19 | future | S point 7, 13 months on | to be issued at `t = 13` |
| 20 | derived | S point 7 at S month 60, `WP_UK_S` run under a guarantee charge of 0.2% | its charges taken at twice today's rate, 147.88, where today's would have taken 74.05 |
| 21 | derived | S point 3 at S month 300, under a guarantee charge of 0.2% | the 5% bond past its charge cap from 207, where today's rate caps it from 487 |
| 22 | derived | S point 1 at S month 150, under the bonus rule | a unit price of 1.486230 and a year's rate of 5.69%, where rates held level give 1.268242 and 2% |
| 23 | derived | S point 5 at S month 150, under the bonus rule | the endowment with 2,091.61 of bonus attaching and a year's rate of 0.60% |
| 24 | derived | S point 1 at S month 156, under a smoothing cap of 5% | the payout held to 43,584.94 below an asset share of 46,540.48, its smoothing account below 0 |

A derived row's `policy_count` is the count `WP_UK_S` carries into that month, its
`pols_if(d)`, and its state what S carries there, so the row continues the S projection from
there. At the shipped References no state carries a cumulant or a history that today's
References would not rebuild, so five rows are read from `WP_UK_S` run under References of
their own, which the spec's `derived_refs` records: points 20 to 24. At the shipped
References the committed model projects each from that history at today's, and a test
asserts that each continues `WP_UK_S` under its own References with them set in both. A
derived row's `policy_id` is the S row's with the month appended, `WP-000002-M119`, and a
future row's carries the months to issue, `WP-000007-F13`. Row `t` of a generated point is
month `t + source_mth` of its S point.

## Counts and timings

`pols_if_init()` is the count in force at the valuation date: `policy_count` for a point
already in force, 0 for any other. `pols_new_biz(t)` is `policy_count` in the issue month,
the month with `duration_mth(t) = 0`, and 0 in every other. `pols_if_at(t, timing)` keeps
`WP_UK_S`'s three timings and adds `basiclife/BasicTerm_SE`'s `"BEF_NB"`:

- `"BEF_NB"`, the count carried in from month `t − 1`, before month `t`'s new business:
  `pols_if_init()` at `t_entry()`, the first month on the books, and the survivors of
  month `t − 1`'s deaths and surrenders after it, and 0 outside the frame;
- `"BEF_DECR"`, that count plus `pols_new_biz(t)`, before month `t`'s decrements, which
  `pols_if(t)` returns;
- `"BEF_SURR"`, after the month's deaths, before its surrenders;
- `"AFT_DECR"`, the end of the month, which is `"BEF_NB"` at `t + 1` exactly, and 0 in
  the frame's last month, where the survivors leave as `pols_maturity(t)`.

Any other timing raises. The survivors of the frame's last month are paid `G + TB` on the
endowment's maturity and `FV + FB` on the bond's forced encashment, and nothing at the
bond's limiting age. The roll-forward closes as

```
pols_if(t) − pols_if(t + 1) + pols_new_biz(t + 1)
    = pols_death(t) + pols_surr(t) + pols_maturity(t)
```

at every `t` of every frame, and its check scales its tolerance with `policy_count()`,
where `WP_UK_S` scales with `pols_if_init()`, which here is 0 on new business.

Cover is `is_active(t)`, `0 ≤ duration_mth(t) < cover_end_mth()`, and outside it, before
issue and from the end of cover on, every count is zero, and so every cash flow; so is
every balance, every rate read at a policy year or an age, and every flag false. Between a
bond's exhaustion and its limiting age it is in cover, holding no count, its frame having
ended.

## Each chain one cell a month

Four chains carry the state forward, coupled: the count; the asset share; the smoothed
payout, which reads the asset share and feeds the withdrawal's share of it back through
`wd_as_pp` and `policy_value_open`; and the endowment's guarantee. `WP_UK_S` runs the
asset share through seven cells a month, its `asset_share_at` timings, the payout through
three and the guarantee through two: a cold read of `asset_share(779)` on the worked
example's bond runs 5,042 cells deep. Here each is written in the cell that carries it,
reading that chain's own month before first and the month's other cells after:
`asset_share(t)` writes the month's premium and withdrawal, return, charges, shareholder
transfer, mortality charge and estate distribution inline, in `asset_share_at`'s order and
its floats, `smoothed_payout(t)` the cap and the corridor, the endowment's
`guar_benefit_pp(t)` the declaration, and `pols_if_at(t, "BEF_NB")` the month before's
deaths and surrenders, so that each chain from month `t` back to `t_entry()` is one cell a
month, whichever chain a call meets first (USLIB-SEC-PLAN.md D5). `asset_share_at` and
`smoothed_payout_capped` read them, a step at a time, as `WP_UK_S`'s do, and a test holds
each inline cell to them, bit for bit. The units, the unit price and the two cumulants were
one cell a month already.

Called cold on a model just read, at the contract's longest cover, 1,224 months from issue
age 18 on the bond and on an endowment maturing at 120, each chain runs one cell a month
back to `t_entry()` and at most 16 more, measured with the bonus rule and the estate
distribution on, on a point issued now and one issued 120 months on alike: a cold `net_cf`
in the last month runs 16 beyond its chain on the bond, 14 on the endowment and 9 on a bond
withdrawing 1% a year, whose exhaustion search runs its chains first; the count 12, 6 and
5; the asset share 6; the payout 7; the guarantee 11, 10 on the endowment; the units, the
unit price and the guarantee charges 10, the declaration's read of the asset share opening
beneath them; the smoothing account 12, 8 on the withdrawing bond; and the roll-forward's
residual 7. The rule's own chain, `bonus_rate` through each year's declaration, is one cell
a year and 30 more.

## Where the units run out

A level withdrawal election runs a bond's units down, and against a fund whose growth is
only the declared bonus it cancels the last of them. `fund_exhaust_mth()` finds the month,
as a policy month: the first whose closing units are at or below `1e-9`, `WP_UK_S`'s test,
the month the withdrawal, capped at the unit fund, takes the last of it. The frame ends
the month before, and its survivors are paid `FV + FB` there, a forced encashment. The
search is one loop over the units' own months, from `t_entry()` to the end of cover,
ascending, so that each month's units are read once the month before's are known: the far
read R2 admits, as uslib's `DIA_US_SEC` reads its survival to its payout date and
`ULB_UK_SEC` its fund to exhaustion. It starts at `t_entry()`, because a bond issued later
holds no units before its issue month, which a search from 0 would read as exhausted at
once, and it reads the units of the month they run out, the month after the frame's last.

`WP_UK_S`'s "never" was 0, safe there because its month 0 is a bond's issue month, which
the single premium funds. On the valuation clock month 0 is any month of a bond's life,
the one its last units are withdrawn in among them, and a policy month of 0 is the issue
month, so here "never" is a month past cover, `cover_end_mth() + 1`. A bond whose units
run out in its first month on the books has no month to project, and `proj_len()` refuses
it. The search reads the units' chain, and through the bonus rule the asset share's, so
nothing they read may read the frame: `is_active(t)` reads the end of cover alone.

## Departures from WP_UK_S

Each formula that tested `t` against a contractual event now tests the policy clock, and
each recursion opens at `t_entry()` from the opening state. Where `WP_UK_S`'s test would
have stayed correct on the valuation clock, it moved anyway, so that cover has one
definition. Fifteen cells are new — `policy_count`, `duration_mth_init`, `t_entry`,
`is_active`, `cover_end_mth`, `pols_new_biz`, `result_pols`, the accessors of the three
columns renamed and of the two cumulants, and the refusal cells of five chains — and three
of `WP_UK_S`'s are gone, `proj_start` and `duration_inforce`, which the valuation clock
replaces, and `attaching_bonus`, renamed. One Reference is new, `issue_age_min`.

| Cells | `WP_UK_S` | `WP_UK_SEC` | Why |
|---|---|---|---|
| `duration_mth`, `duration`, `age`, `policy_year` | `t`, `t // 12` | `duration_mth_init() + t`, `duration_mth(t) // 12` | The policy clock, opened from the model point |
| `proj_len`; `cover_end_mth`, new | `12 × policy_term()`, or `min(12 × (omega_age − x), fund_exhaust_mth())`, from issue | `min(cover_end_mth(), fund_exhaust_mth()) − duration_mth_init()`, from the valuation date; raises past cover, outside the contract's bounds, on a Reference off its domain and on units spent in the first month | The frame starts at the valuation date |
| `fund_exhaust_mth` | the first `t` from `proj_start()` whose units are at or below 1e-9, 0 if none | the same as a policy month, from `t_entry()`; `cover_end_mth() + 1` if none | 0 is a real month on either clock |
| `is_forced_encashment` | `fund_exhaust_mth() > 0` and the frame ends there | `fund_exhaust_mth()` inside cover | The new "never" |
| `is_declaration_month`, `declaration_month` | `(t + 1) % 12 == 0`; the policy month `12 × duration(t) + 11` | `(duration_mth(t) + 1) % 12 == 0`; the valuation month `t + 11 − duration_mth(t) % 12`, `WholeLife_US_SEC`'s `anniv_mth` | A declaration falls in a policy year's twelfth month, and `bonus_rate` passed the policy month back as `t` |
| `guarantee_imminent` | `0 < 12g − 1 − t ≤ 12` | `0 < 12g − 1 − duration_mth(t) ≤ 12` | A guarantee date is a policy anniversary |
| `premium_pp` | the single premium at `t == 0` | at `duration_mth(t) == 0` | On the valuation clock every bond in force would pay its single premium again |
| `asset_share`, `asset_share_at` | seven cells a month from `asset_share_init()` at `proj_start()` | inline, one cell a month, from `asset_share_init()` at `t_entry()`; a balance past the floats refused before its floor | D5's one cell a month; the floor would read `−inf` or NaN as an exhausted share |
| `smoothed_payout`, `smoothed_payout_open` | three cells a month from the column at `proj_start()` | inline, one cell a month, from the column at `t_entry()` | D5 |
| `guar_benefit_pp`, `guar_benefit_open` | the endowment's guarantee two cells a month | inline, one cell a month; a guarantee past the floats refused | D5 |
| `units`, `unit_price` | from the columns at `proj_start()` | from the columns at `t_entry()`; past the floats refused | The opening state |
| `guar_charge_cum_pp`, `guar_charge_rate` | from 0 at `proj_start()` | from `guar_charge_cum_pp_init()` at `t_entry()` | A cumulant `WP_UK_S` restarts at 0 |
| `smoothing_account` | from 0 at `proj_start()` | from `smoothing_account_init() × pols_if_init()`; 0 outside the frame | A cumulant `WP_UK_S` restarts at 0 |
| `bonus_rate` | the column, or with the rule on the rule from S's second projected year, each month reading its year's declaration, past the frame where a forced encashment ends it mid-year | the column, or with the rule on the rule from the second year on the books, each month reading its year's declaration where the frame reaches it, and the year before's rate where it does not | R2's read bounded by the frame; it changes the `bonus_rate` column of `result_payout` in such a year alone |
| `pols_if`, `pols_if_at`, `pols_if_init` | `pols_if` a recursion of its own, three cells a month, from the column's 1.0 at `proj_start()` | `pols_if` is `"BEF_DECR"`, the `"BEF_NB"` chain plus the month's new business, one cell a month from `t_entry()`; `pols_if_init()` is 0 unless in force | Policies in force at the valuation date open the count; new business joins it in its issue month |
| `inflation_factor` | `1.03^duration(t)`, from issue | `1.03^(t // 12)`, from the valuation date | Unit costs in valuation-date pounds |
| `mort_rate`, `surr_rate_base`, `surr_rate`, `premium_pp`, `wd_pp`, the balances, the counts | no `WP_UK_S` frame has a month before issue | zero outside cover, before any table or rate is read; an age past the table refused by name; the lapse table's extent from `Data` | Before issue `WP_UK_S` reads the tables at ages and policy years the policy never has |
| `cost_of_bonus_pp`, the flows, `net_cf` | unchecked | a value past the floats refused in its month | From inputs each in its domain, a bonus rate past every amount of money made the cost, and so the asset share, infinite with every check passing |
| `inflation_factor`, `bonus_supportable`, `cost_of_bonus_pp`'s discount | Python's `OverflowError`, naming nothing | a power past the floats refused, naming the point and the References | `PA_UK_SEC`'s form (*Record — M11*) |
| `check_pols_roll_fwd_resid`, `check_pols_roll_fwd` | `pols_if(t + 1)`; tolerance `1e-10 × max(pols_if_init(), 1)` | adds `pols_new_biz(t + 1)`; tolerance `1e-10 × max(policy_count(), 1)` | The next month's new business is no part of month `t`'s movement, and `pols_if_init` is 0 on new business here |
| `check_declaration_is_annual` | the months of S's frame | the months on the books, from `t_entry()` | Before issue a policy holds no price to move |
| `result_cf`, `result_payout` | `range(proj_start(), proj_len())` | `range(proj_len())`, from the valuation date | Row 0 is the valuation month |
| `result_pols`, new | — | the counts behind `result_cf()` | After `basiclife/BasicTerm_SE`'s `result_pols()` |

Of the cash flows, the change of clock moves the maintenance expense alone at the shipped
assumptions, and `net_cf` with it. The twins of `WP_UK_S`'s bonds in force carry that
expense in valuation-date pounds, so their `expenses(t)` is `WP_UK_S`'s `expenses(60 + t)`
divided by `1.03^5`; every other column is `WP_UK_S`'s from month 60 on. The endowment in
force divides by `1.03^20`.

**The caps, as `WP_UK_S` has them since UKLIB-SEC-PLAN.md's M0.** `mort_rate` caps the
annual mortality rate at 1, written `min(q, 1.0)`, the product first and the bound second,
so that a NaN stays NaN where `min(1.0, q)` would read it as certain death; wherever `q` is
a number the two are the same float. The table reaches 1 at male age 113 and female 118,
so at the shipped factor of 0.6 the cap never binds, and its test takes a factor above 1.
The surrender rates keep `WP_UK_S`'s order, `min(1.0, w)`: they are no cap on a mortality
rate, and the multipliers that feed them are held to domains no NaN is in.

**Domains `WP_UK_S` leaves unchecked.** `WP_UK_S` raises a Reference to a power, bounds a
rate or a balance with it, or reads it as a share, a factor or an amount, and checks none.
Off its domain it projects a negative rate or charge, or a NaN that a `min` or a `max`
loses: a NaN smoothing cap or corridor is lost through the clamps, which then read the
corridor's ceiling; a NaN deterrent or exercise rate reads as certain surrender through
`min(1.0, ...)`; a NaN estate distribution is lost in the asset share's floor; and a NaN
charge cap switches the cap off. Here `proj_len()` refuses each Reference off its domain,
naming the point, the Reference, the domain and the value, on every point, as a model-wide
assumption:

| Reference | Domain | Off it |
|---|---|---|
| `issue_age_min`, `omega_age` | a whole number below `2**53`; the first 0 or more, the second above the first and at most a year past the mortality table's last age | a NaN bound refuses nothing and an infinite one bounds nothing, where the compiled caches will be sized from them |
| `mort_be_factor`, `misc_surplus_rate`, `death_benefit_factor`, `mvr_deterrent_factor`, `guarantee_imminent_factor`, `guar_fill_target`, `bonus_change_cap`, `expense_maint` | a finite number, 0 or more | a negative rate, charge, uplift or expense; a NaN lost in a `min` or a `max` |
| `amc_rate`, `guar_charge_rate_base`, `guar_charge_cap`, `prem_alloc_rate`, `smooth_cap`, `corridor_lo`, `bonus_speed`, `guarantee_exercise_rate` | a number from 0 to 1 | past 1 a monthly rate `1 − (1 − c)^(1/12)` has no real value, or a share is more than the whole |
| `amc_rate` and `guar_charge_rate_base` together | their monthly rates summing to 1 or less | the charges' factor on the balance, `1 − c_amc_m − c_g_m`, turns negative |
| `corridor_hi` | a finite number, 1 or more | the corridor must include 100% of the asset share |
| `shareholder_transfer_divisor` | a finite number above 0 | the cost of bonus is divided by it |
| `surr_disc_rate` | a finite number above −1 | the endowment's bonus cost is discounted at `(1 + i)^years` |
| `bonus_rule_on` | True or False | the switch |
| `bonus_horizon` | a whole number of years, 1 or more, below `2**53` | the rule divides by it |
| `inflation_rate` | a finite number, −1 or more | the inflation factor changes sign each year |

Each domain is a comparison no NaN passes, a finite one bounded by the largest float, and
a whole number one of which `x == x // 1` holds below `2**53`, which an infinity fails, and
each Reference is printed as the compiled model will type it, the three integers through
`int()` once whole and every other through `float()`. `Data.future_horizon_mth` is held to
a whole number of months, 0 or more, by `Data` itself, as it reads the table.

**Values past the floats, refused in their cell.** From an opening state and References
each in its domain, a return can take the asset share past the largest float, a bonus
rate the unit price, the guarantee or the cost of bonus, a premium at a tiny price the
units, a long run the two cumulants, a count any flow, and the flows' sum the net cash
flow, where `WP_UK_S` would floor an infinite or NaN asset share at 0 and read it as
exhausted, every check passing. Here each value is refused with `ValueError` in the cell
and the month where it first leaves the floats, naming the point, the month and what
makes it: the premium, the guarantee the books open with, the asset share and the parts
of its month a Reference multiplies, the withdrawal's share of it, the estate
distribution and the shareholder transfer, the units, the unit price, the guarantee, the
death uplift and the death claim, the cost of bonus, the two cumulants, each flow, the
claims of each kind and their total, and the net cash flow. Each chain's refusal is
formatted in a cell of its own, `asset_share_refusal`, `units_refusal`,
`unit_price_refusal`, `guar_benefit_refusal`, `guar_charge_cum_refusal` and
`smoothing_account_refusal`, which the chain calls only on its error path, so that no
frame a chain holds formats a message (UKLIB-SEC-PLAN.md §6.6, *Record — M10*); each
returns its chain's value, under its chain's guards, wherever it is called.

A power is refused the same way. modelx runs a formula as Python does, and Python's float
`**` raises `OverflowError`, naming neither the point nor the Reference, where its result
would pass the largest float, and C's `pow` gives an infinity there. So the inflation
factor, the bonus rule's growth to its horizon and the endowment's discount on its bonus
cost each catch the one and test for the other, and raise `ValueError` naming the point
and the References, `PA_UK_SEC`'s form (*Record — M11*); the discount is refused below the
smallest float too, since the cost divides by it. The C step keeps the test and drops the
`try` for uslib's M22 form.

## Tests

- **The twin identity**, in `tests/test_model_conventions_uk.py`: on points 5 and 7, the
  endowment and the bond issued at the valuation date, every cell of `WP_UK_S`'s agrees at
  every argument `WP_UK_S` evaluates in its own sweep, to 1e-9 relative with no absolute
  floor, but for `pols_if_init` and `model_point`, and the four cells the spec names with
  its reasons; a cell this model lacked would fail it. So `WP_UK_S`'s goldens on its new
  business hold here with no number restated. The same suite holds the model to the
  conventions every `_SEC` model meets: every frame starts at `t = 0`, `pols_if` is the
  `"BEF_DECR"` count, new business enters once at its `policy_count`, nothing happens
  before issue, and the in-force columns are present.
- **The splice**, in `tests/test_with_profits_uk_sec.py`: each `WP_UK_S` point restated in
  force at months about its events — the declarations at the end of each policy year's
  twelfth month, the month after each and mid-year; on the down scenario the smoothing
  cap's floor from 61, the market value reduction from 68, the corridor's ceiling from 92,
  the guarantee window, 106, 107 and 118 to 120, the charge's cap from 160 and the asset
  share's floor from 242; the 5% bond's cap from 504, where it flickers; the withdrawing
  bond's cap from 284 and its last month, 402; the endowment's cap at 289 and 290 and its
  maturity, 299; the bond variant's cap from 88, its floor from 196 and its last month,
  266; and the limiting age's last month, 779 — continues the S projection in every cell
  the two share but the frame's length, S's accessors of the columns its frame opens with,
  and the declaration month, a valuation month here, and in `result_cf`, `result_payout`
  and `result_pols`, to 1e-9 relative with no absolute floor, the residuals and the smoothing
  cost of an exit, a difference rounding about 0 where the payout is the asset share, at
  1e-9. `WP_UK_S`'s own in-force rows are spliced as twins, at 60 and 240. The splice runs
  on two sets of References: an estate distribution on, which ships off, and the MVR
  deterrent and the guarantee-imminent factor set apart from the factors they ship equal
  to; and the same with the bonus rule on, on fewer rows, its own months about the rule's
  declarations. Inflation, the input on the valuation clock, is 0 in both. Variants of S's
  points, in a copy of S's table that is never committed, reach what S's own cannot: a
  female life, a −40% crash for the corridor's ceiling, the pension tax basis on a bond,
  and three bonds issued at the valuation date, at 5% with and without withdrawals and at
  −15% without, whose charges stop at 442, 197 and 101. The default run takes a core of the
  grid; a test asserts the core reaches every branch, opening-state column, kind of
  valuation month and side of every `min` and `max` the full grid reaches. The binding
  mortality cap is held by a test of its own, under a mortality factor of 2.
- **Future new business**: the bond and the endowment issued 1, 12 and 120 months on, and
  the variants 13 months on, each S's projection moved on, with zeros before issue and no
  table read there.
- **How it computes**: on every row of the splice's grid, after its reports, its checks
  and every monthly cell at every month, no cell has been called at a negative month, none
  on the books read a month before `t_entry()`, none read a month later than `t + 1` but
  the bonus rate's declaration read, inside the frame, and none raised; the exhaustion
  search reads the units to the month they run out and no further. On a fresh read of the
  committed model the policy clock is a closed form, and every point's reports and checks
  run under a lowered recursion limit, which a recursion backward over the frame would
  exceed. And each chain, called cold in the last month at the contract's longest cover on
  each shape, runs one cell a month back to `t_entry()` and at most 16 more.
- **Counts**: the roll-forward closes; `result_pols()` holds the counts; multiplying
  `policy_count` by 2.5, with the rule and the estate distribution on, multiplies every flow
  and counted cell, each nonzero on some point, and moves no per-policy value; a point
  restated a month on, opened with what the model carries into its month 1, continues its
  own flows; and the roll-forward, its tolerance scaled by the count, closes on ten million
  policies.
- **Validation and regeneration**: each malformed row of the table refused naming its
  point, and naming its label on an extract labelled otherwise than by position; the
  horizon a Reference; a point past its cover, one the contract does not issue and a bond
  spent in its first month refused by `proj_len()`; each Reference off its domain, at the
  value next outside each edge, NaN and both infinities, where each edge is accepted and
  projects its reports; each value past the floats refused in its cell, the powers'
  among them; each assumption table a reader cannot read refused naming its lines;
  keys written as floats read as `WP_UK_S` reads them; the edges of the interface accepted;
  every state `WP_UK_S` reaches accepted in force; and the committed table is what `WP_UK_S`
  generates.
- **The product's own facts**: the two clocks on the shipped points; the committed rows
  continuing their S points at the shipped assumptions but for inflation, and the rows read
  under References of their own continuing `WP_UK_S` under them; each history column read,
  not recomputed (UKLIB-SEC-PLAN.md K14): the asset share, the units, the unit price, the
  attaching bonus, the payout, the bonus rate and both cumulants, each on a state whose
  history departs from what today's References give; the single premium paid in the issue
  month alone; the declaration, the guarantee dates and the guarantee-imminent window on the
  policy clock; the bonus rate's read bounded by the frame; the new "never"; expense
  inflation on the valuation clock; the cap on mortality and a NaN that reaches a bound; a
  check whose residual is NaN; the values outside cover; the block; an in-force extract;
  the runner; the docstrings; the shared input tables; each pair of parameters a formula
  could confuse, equal somewhere, apart on some core row; and no computed cell building a
  Python object outside UKLIB-SEC-PLAN.md §6.5's C list.

```bash
python -m pytest tests/test_with_profits_uk_sec.py -q
UKLIB_SEC_FULL=1 python -m pytest tests/test_with_profits_uk_sec.py -q   # the full grid
python -m pytest tests/test_model_conventions_uk.py -q -k WP_UK_SEC
```

<!-- BEGIN generated citation links -- regenerate with tools/gen_citation_links.py -->
[std]: #uklib-std
<!-- END generated citation links -->
