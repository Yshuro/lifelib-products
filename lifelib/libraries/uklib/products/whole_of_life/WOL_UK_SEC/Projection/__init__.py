# modelx: pseudo-python
# This file is part of a modelx model.
# It can be imported as a Python module, but functions defined herein
# are model formulas and may not be executable as standard Python.

"""The by-policy projection of the :mod:`~.WOL_UK_SEC` model; holds all formulas.

The Space is parameterized by ``idx``, the position of a model point in the table and in
every :mod:`~.WOL_UK_SEC.Data` vector, as ``basiclife.BasicTerm_SC`` is: ``Projection[9]``
is an ItemSpace projecting the table's tenth row, model point 10, :mod:`~.WOL_UK_S`'s
pro-rata paid-up point in force 200 months, and :func:`point_id` is its label::

    >>> Projection[9].result_cf()          # one row per month from the valuation date
    >>> Projection[9].result_pols()        # the counts behind it, both strands
    >>> Projection[9].point_id()           # 10, the row's point_id
    >>> Projection.idx = 1                 # or switch the default, before it computes

Compiled, no cache is ever cleared: set ``idx``, like every Reference, on a model just
imported, before anything is computed, or project through ``Projection[i]``. modelx
recomputes what a Reference reaches when it is set; a compiled ItemSpace takes the
References when it is made and keeps every value it has computed until it is deleted,
and the base ``Projection`` and ``Data`` keep theirs for good.

Any ``idx`` makes an ItemSpace, and none is refused here. ``Projection[-1]`` reads every
vector at its last element, as numpy and a compiled memoryview both do, so it is the
table's last point, under that point's own :func:`point_id`; an ``idx`` past the last
row raises ``IndexError`` at its first read of a vector, which modelx reports inside its
``FormulaError``.

This is :mod:`~.WOL_UK_S` taught to run in force at a valuation date, as lifelib's
``basiclife.BasicTerm_SE`` extends ``basiclife.BasicTerm_S``, and then made to compile, as
``basiclife.BasicTerm_SC`` is made from ``basiclife.BasicTerm_S``. A formula of
:mod:`~.WOL_UK_S` is rewritten where it depends on where the projection starts, where it
must answer for a month outside cover, or where it read a policy month as ``t``; every
other formula is :mod:`~.WOL_UK_S`'s own, the cap on mortality, ``min(q, 1.0)``, among
them. ``products/whole_of_life/model-sec.md`` lists the rewritten cells with the reason
for each. Making it compile changed how each cell reads its inputs and spells its codes,
and how its four chains reach back in time, and no number: every model point attribute a
projection cell uses is read as a number from a ``Data`` vector, every table as an array
indexed by integers, every timing and kind is an int code (*Codes*, below), and every text
column is decoded into the number a formula branches on.

.. rubric:: Input data

Inputs are **external files**: plain CSVs living in the model folder's parent
directory, ``products/whole_of_life/``, read at run time rather than stored inside the
model. The model folder therefore holds nothing but formulas — no ``_data/``, no
IOSpec, no embedded values — so a diff of the model shows logic changes only, and an
input can be edited or swapped without rewriting the model. This follows
``annuallife.TradLife_A``; contrast ``basiclife.BasicTerm_S``, which keeps its inputs
*inside* the model through modelx's IOSpec machinery.

The consequence worth knowing: **the model is not portable on its own.** Copying the
``WOL_UK_SEC`` folder without its parent's CSVs produces a model that reads and then
fails on first evaluation.

The two assumption tables are the files :mod:`~.WOL_UK_S` reads, read in place; the model
point table is this model's own. Each table has a filename Reference and a reader Cells,
both on :mod:`~.WOL_UK_SEC.Data`, reached here through the ``data`` Reference:

======================  ==============================  ==========================
Reference               Cells                           File
======================  ==============================  ==========================
model_point_file        data.model_point_table()        model_point_table_sec.csv
mort_table_file         data.mort_table()               mort_table.csv
lapse_table_file        data.lapse_table()              lapse_table.csv
======================  ==============================  ==========================

No cell here but :func:`model_point`, a reporting cell, reads the readers' DataFrames, and
the label accessors read through it. Every other reads :mod:`~.WOL_UK_SEC.Data`'s vectors
and arrays, one element at a time: a model point's attribute at its position,
``data.sum_assured()[idx]``, decoded already into the number the formula needs; the
mortality table at the point's schedule and attained age,
``data.mort_table_array()[mort_schedule(), x]``; and the lapse table at the point's cell
and policy year. ``Data``'s docstring lists them.

.. rubric:: Two clocks

``t`` counts months from the **valuation date**, 0-based, the clock
``basiclife.BasicTerm_SE`` runs on: ``t = 0`` is the valuation month for every model
point, however old the policy, month ``t`` runs from time ``t`` to time ``t + 1``, and the
frame is ``t = 0 .. proj_len() - 1``, where :func:`proj_len` counts the months from the
valuation date to the limiting age. Row ``t`` is the same month for every point, so the
frames of a block line up and sum row by row.

``duration_mth(t)`` counts **policy months**, the months the policy has been in force at
time ``t``: ``duration_mth(t) = duration_mth_init() + t``, where
:func:`duration_mth_init` is read from the model point — positive for a policy in force at
the valuation date, 0 for one issued at it, ``-k`` for one issued ``k`` months later, at
most ten years later. Everything contractual reads it: the completed policy years
``duration(t) = duration_mth(t) // 12``, the contractual 1-based label
``policy_year(t) = duration(t) + 1``, the lapse table's key, the attained age
``age(t) = age_at_entry() + duration(t)``, the mortality table's, and through them the
over-50s moratorium and the underwritten suicide window, the escalation steps on each
policy anniversary, premium cessation, the payments made that the pro-rata paid-up value
counts, the first year's commission and the limiting age, :func:`limit_mth`. Model point
10, the pro-rata paid-up point valued 200 months after issue, is in policy year 17 at
attained age 86 at ``t = 0``, carries policies on both strands, and has 400 months to the
limiting age.

Two inputs read the valuation clock instead, both from the valuation date on, for every
point alike: expense inflation, ``inflation_factor(t) = (1 + inflation_rate) ** (t //
12)``, so that the maintenance charge is in valuation-date pounds, and mortality
improvement, ``mort_improve_factor(t) = (1 - mort_improvement) ** (t // 12)``, which
improves the tables from the date they are stated at, as uslib's ``ULSG_US_SEC`` improves
its own (USLIB-SEC-PLAN.md D7; UKLIB-SEC-PLAN.md §9 item 4). The acquisition expense is
charged per policy issued, in the issue month, uninflated, as in
``basiclife.BasicTerm_SE``. RPI is a flat Reference, the rate assumed from the valuation
date on.

On a point issued at ``t = 0`` the two clocks coincide and this model computes what
:mod:`~.WOL_UK_S` computes: every cell the two share agrees at every argument
:mod:`~.WOL_UK_S` evaluates in its sweep, but for those whose meaning changed —
``pols_if_init``, now the count already in force at the valuation date, and
``model_point``, a row of another table. ``tests/test_model_conventions_uk.py`` asserts it
cell by cell.

.. rubric:: Counts

``pols_if(t)`` is the count on full cover that weights row ``t``: ``pols_if_at(t,
BEF_DECR)``, the count carried in from ``t - 1`` (``BEF_NB``) plus the month's new
business, :func:`pols_new_biz`, before the month's decrements. A point in force at the
valuation date opens with :func:`pols_if_init`, its ``policy_count``; one issued at or
after the valuation date opens with none, and takes its ``policy_count`` as new business
in its issue month. The recursion's base is :func:`t_entry`, the first month on the books,
and nothing is counted outside cover (:func:`is_active`): before issue every count, and so
every cash flow, is zero. :mod:`~.WOL_UK_S`'s three timings are kept, ``BEF_DECR``,
``BEF_LAPSE`` and ``AFT_DECR``, and ``BEF_NB`` is the one running in force adds.

Each of the model's four chains, the full-cover count, the paid-up count, the paid-up
cover and the premiums paid, runs one cell a month within a policy year, and in a year's
first month after :func:`t_entry` reads the year's opening, the cell of its name with
``_py`` added: :func:`pols_if_py`, :func:`pols_pu_py`, :func:`pu_benefit_py` and
:func:`prem_cum_pp_py`. Each opening walks the year before in ascending order, asking the
monthly cell of each of its months, so that each finds the month before cached, and
returns the value carried out of the year's last month, the month's own float, so no
number moves. A cold read then runs one cell a month back to its year's first month and
two cells a year before that, where one cell a month would run the contract's longest
cover, 1,236 months, on a compiled model's C stack (UKLIB-SEC-PLAN.md K12).

The pro-rata paid-up variant runs a second strand beside the first, :func:`pols_pu`, the
policies made paid-up, and :func:`pu_benefit`, their summed cover. A point in force opens
it with :func:`pols_pu_init` policies, each with :func:`pu_benefit_pp_init` of cover; any
other point opens it empty. :func:`pols_all`, the two strands together, carries the
maintenance expense and the roll-forward. A point may be paid-up entirely, its
``policy_count`` 0 and its paid-up strand alone in force.

.. rubric:: The opening state

A point in force carries, beside its two counts, the facts of its contract that
:mod:`~.WOL_UK_S` carries into the month it is valued at, each per policy, so that the
counts are the only weights on the flows, and each measured at the valuation instant, the
start of month 0, before any month-0 event:

* :func:`pols_pu_init` and :func:`pu_benefit_pp_init`, the paid-up strand: its policies,
  and the paid-up cash sum each carries on average;
* :func:`prem_cum_pp_init`, the premiums paid per policy on full cover to the end of
  month -1, which the moratorium refund, the suicide refund, the crossover stress on the
  lapse rate and :func:`crossover_mth` read;
* :func:`crossover_mth_init`, the policy month the premiums paid first exceeded the cover,
  if that was before the valuation date, and ``-1`` if it was not, which
  :func:`crossover_mth` reports rather than searching the months before the valuation
  date again;
* :func:`cover_pp_init` and :func:`premium_pp_init`, the cash sum in force and the monthly
  premium before month 0's events, after every increase already given: on the
  escalating variants the history :mod:`~.WOL_UK_S` rebuilds from issue at today's
  ``rpi_rate``, ``esc_fixed_cover`` and ``esc_take_up``. On a point valued on an
  anniversary they are the year it closes: the anniversary's increase is the
  projection's first event, at today's References. Once premiums have ceased,
  :func:`premium_pp_init` is the last premium paid.

Each is history, read from the model point, never recomputed from a Reference, which is
an assumption from the valuation date on: an RPI, a take-up or a lapse stress changed at
the valuation date reaches back over no increase, no premium, no conversion and no
crossover already made. The increases after the valuation date step on each policy
anniversary at today's References.

.. rubric:: Codes

What :mod:`~.WOL_UK_S` spells as text, a timing, a kind, a cell or an escalation, is here
an int Reference named as the text it replaces, so that every cell takes and returns C
numbers. A call site reads as it did, less the quotes: ``pols_if_at(t, BEF_DECR)``,
``benefit_pp(t, DEATH)``, ``claims(t, DEATH_PU)``.

==============  =====  ==========================================================
Reference       Value  Meaning
==============  =====  ==========================================================
BEF_NB          0      :func:`pols_if_at`: the count carried in from month t - 1
BEF_DECR        1      :func:`pols_if_at`: that count plus month t's new business
BEF_LAPSE       2      :func:`pols_if_at`: after the month's deaths, before its
                       lapses
AFT_DECR        3      :func:`pols_if_at`: the end of the month, after its
                       decrements
DEATH           0      :func:`benefit_pp`: the expected benefit per death on full
                       cover; :func:`claims`: the full-cover strand's death outgo
NON_ACC         1      :func:`benefit_pp`: the non-accidental death benefit
ACC             2      :func:`benefit_pp`: the accidental death benefit
PAID_UP         3      :func:`benefit_pp`: the paid-up payout on conversion
DEATH_PU        1      :func:`claims`: the paid-up strand's death outgo
LAPSE           2      :func:`claims`: the lapse outgo, nothing
ALL             3      :func:`claims`: the three kinds' total
O50             0      :func:`cell_code`: over-50s guaranteed acceptance
UW              1      :func:`cell_code`: underwritten
LEVEL           0      :func:`escalation_code`: no increase
FIXED_5PCT      1      :func:`escalation_code`: the fixed increases
RPI             2      :func:`escalation_code`: the RPI increases
==============  =====  ==========================================================

A code a cell takes indexes that cell's cache, a C array of four codes a month, the
model's one inner width, for :func:`pols_if_at`, :func:`benefit_pp` and :func:`claims`,
so codes are numbered densely from 0: the timings in the order of their instants within
the month, ``BEF_NB`` before ``BEF_DECR``, as in every SEC model; and the kinds of each
family in their own order, ``claims``' in :func:`result_cf`'s, then ``ALL``,
:mod:`~.WOL_UK_S`'s ``kind=None``. :mod:`~.WOL_UK_S` spells ``DEATH`` in both families, the
benefit per death and the outgo it pays, so ``DEATH`` is one Reference, 0 in both, as
uslib's ``ULSG_US_SEC`` names ``GRACE`` a kind and a status: ``benefit_pp``'s kinds put it
first, before the two it blends on the over-50s cell, ``NON_ACC`` and ``ACC`` in
:mod:`~.WOL_UK_S`'s order, and the paid-up payout, so that each family fits the width of
four. A code a cell does not take raises, ``invalid timing`` or ``invalid kind``. The
cells' and the escalations' codes index no cache: each is ``Data``'s decode of a point's
column, :func:`cell_code` and :func:`escalation_code`, compared as :mod:`~.WOL_UK_S`
compares the text. They are References, not cells, so the symbol map below does not list
them.

.. rubric:: Reporting cells

:func:`model_point`, the label accessors :func:`cell`, :func:`escalation`,
:func:`mort_basis`, :func:`sex` and :func:`smoker`, and the reports :func:`result_cf` and
:func:`result_pols` return Python values, a table row, text and DataFrames, for a reader
and for the comparison with :mod:`~.WOL_UK_S`, which has every one of them. No cell but
these calls a label accessor or a report: every other reads the number ``Data`` decoded
from the same column instead, the point's cell, escalation and mortality schedule. So
they stay Python when the model compiles, and every other cell returns a C ``bint``,
``long long`` or ``double``. Each label refuses any value but its column's codes, as
:mod:`~.WOL_UK_S`'s ``cell`` and ``escalation`` do and its ``sex`` and ``smoker`` do not, and
:func:`mort_basis` reads :func:`cell`, so each returns text or raises, in either engine.
The two checks, :func:`check_pols_roll_fwd` and :func:`check_truncation`, are reporting
cells too, which no cell calls, and each compiles to a ``bint``, a verdict over cells that
compile.

.. rubric:: Naming

Cells names follow lifelib's ``basiclife.BasicTerm_S`` and ``savings.CashValue_SE``
wherever those models have an analogue — ``pols_*`` for policy counts, plural nouns for
cash flows, ``*_rate`` for annual rates and ``*_rate_mth`` for monthly ones, ``*_pp``
for per-policy amounts, ``claims(t, kind)`` and ``benefit_pp(t, kind)`` with a ``kind``
code named in capitals. What running in force adds is named as
``basiclife.BasicTerm_SE`` names it: ``duration_mth`` read from the model point,
``policy_count``, ``pols_new_biz``, ``pols_if_at``'s ``BEF_NB`` timing, ``is_active``
and ``result_pols``. ``duration_mth_init``, the policy months completed at the valuation
date, takes ``UL_US_S``'s name; ``t_entry`` and ``limit_mth`` are this model's own, and each
opening-state cell is the cell it opens with ``_init`` added, ``pu_benefit_pp_init`` the
per-policy form of :func:`pu_benefit`'s. What compiling adds is named as
``basiclife.BasicTerm_SC`` names it: ``idx``, ``point_id`` and the ``Data`` vectors under
their columns' names; a decoded text column is the number it selects, ``mort_schedule``
the mortality table's row of the point's basis, sex and smoker status, and ``cell_code``
and ``escalation_code`` the codes of the cell and the escalation. A chain blocked by policy
year opens each year at its cell with ``_py`` added, of the year ``y``, and a refusal moved
off a chain into a cell of its own is that cell's, the quantity it refuses with
``_refusal`` added. The technical notes use compact actuarial symbols instead. The mapping
is:

=========================  ==============================  ===============================
Notes symbol               Cells                           Meaning
=========================  ==============================  ===============================
(none)                     point_id()                      The model point's label
cell                       cell()                          O50 or UW
(cell decoded)             cell_code()                     The cell as its code
entry_age                  age_at_entry()                  Entry age (ALB)
a(t)                       age(t)                          Attained age (ALB) in month t
y                          policy_year(t)                  Policy year containing month t
(none)                     duration(t)                     Completed policy years, y - 1
(none)                     duration_mth(t)                 Policy months at month t
(none)                     duration_mth_init()             Policy months at t = 0
(none)                     duration_init()                 Policy years the columns hold
(none)                     t_entry()                       First month on the books
(none)                     is_active(t)                    Whether month t is in cover
omega                      omega_age                       Limiting age, 120
(none)                     limit_mth()                     Policy month of the limiting age
(none)                     proj_len()                      Months to the limiting age
(none)                     policy_count()                  Policies the point stands for
SA                         sum_assured()                   Sum assured at outset
SA(t)                      cover_pp(t)                     Sum assured in force in month t
(SA at t = 0)              cover_pp_init()                 Cover before month 0
P                          premium_mth()                   Monthly premium at outset
P(t)                       premium_pp(t)                   Monthly premium due in month t
(P at t = 0)               premium_pp_init()               Premium before month 0
T_cess                     cessation_mths()                Premium-paying policy months
CumPrem(t)                 prem_cum_pp(t)                  Premiums paid, end of month t
(none)                     prem_cum_pp_refusal(t)          Premiums paid past the floats
(CumPrem at a year)        prem_cum_pp_py(y)               Premiums paid entering year y
(CumPrem at t = 0)         prem_cum_pp_init()              Premiums paid to month -1
(escalation)               esc_cover_step()                Annual cover increase
(escalation)               esc_prem_step()                 Annual premium increase
(escalation)               escalation_code()               The escalation as its code
(moratorium)               moratorium_mths()               O50 moratorium, 12 months
in_moratorium(t)           in_moratorium(t)                Whether month t is inside it
DB_na(t)                   benefit_pp(t, NON_ACC)          Non-accidental death benefit
DB_ac(t)                   benefit_pp(t, ACC)              Accidental death benefit
(blended)                  benefit_pp(t, DEATH)            Expected benefit per death
PU                         benefit_pp(t, PAID_UP)          Paid-up payout on conversion
k_adb                      adb_multiplier()                Accidental multiplier, 1 or 2
delta_acc                  acc_share                       Accidental share of deaths, 3%
delta_su                   suicide_share                   Suicide share of year-1 deaths
N_paid(t)                  payments_made(t)                Payments made by end of month t
N_expected                 payments_expected()             Payments expected to cessation
paid_up                    pu_eligible(t)                  Pro-rata paid-up qualifies
t*                         crossover_mth()                 Policy month CumPrem passes SA
(t* before t = 0)          crossover_mth_init()            The crossover, if before t = 0
(basis)                    mort_basis()                    population or assured
(basis, sex, smoker)       mort_schedule()                 The point's mortality row
(loading)                  mort_loading()                  Anti-selection loading
q(y)                       mort_rate(t)                    Annual mortality rate applied
q_m(y)                     mort_rate_mth(t)                Monthly mortality rate
(improvement)              mort_improve_factor(t)          Improvement, valuation clock
w(y)                       lapse_rate(t)                   Annual lapse rate in month t
(table)                    lapse_rate_base(t)              Table lapse rate before beta
(table)                    lapse_last_year()               The cell's last lapse year
beta                       lapse_crossover_beta            Crossover lapse stress dial
w_m(y)                     lapse_rate_mth(t)               Monthly lapse rate
l(t)                       pols_if(t)                      Full cover, start of month t
(l(0))                     pols_if_init()                  Full cover in force at t = 0
(none)                     pols_new_biz(t)                 Policies issued in month t
(none)                     pols_if_at(t, timing)           The within-month counts
(l at a policy year)       pols_if_py(y)                   Full cover carried into year y
(none)                     pols_pu(t)                      Paid-up policies in force
(paid-up at a year)        pols_pu_py(y)                   Paid-up carried into year y
(none)                     pols_pu_init()                  Paid-up policies at t = 0
(none)                     pu_benefit(t)                   Paid-up cover in force
(none)                     pu_benefit_refusal(t)           Paid-up cover past the floats
(paid-up cover at a year)  pu_benefit_py(y)                Paid-up cover into year y
(none)                     pu_benefit_pp_init()            Paid-up cover per policy, t = 0
(none)                     pols_all(t)                     pols_if + pols_pu
(none)                     pols_death(t)                   Deaths on full cover
(none)                     pols_death_pu(t)                Deaths on paid-up cover
(none)                     pols_exit(t)                    Would-be lapses
(none)                     pols_convert(t)                 Would-be lapses made paid-up
(none)                     pols_lapse(t)                   Lapses that actually terminate
(none)                     pols_maturity(t)                Survivors at the limiting age
E[premium](t)              premiums(t)                     Premium income
E[death outgo](t)          claims(t, kind)                 Death outgo by kind
E[expenses](t)             expenses(t)                     Acquisition + maintenance
(commission)               commissions(t)                  Initial commission
(none)                     inflation_factor(t)             Inflation, valuation clock
CF(t)                      net_cf(t)                       Net cash flow, income positive
(none)                     result_pols()                   The counts, month by month
=========================  ==============================  ===============================

Three names needed care in :mod:`~.WOL_UK_S`, and keep their reasons here.

The notes' ``l(t)`` is a single in-force probability, but the pro-rata paid-up variant
splits the population in two: policies still on **full cover**, and policies made
**paid-up** at a reduced payout. :func:`pols_if` is the first strand — the notes' ``l``,
and what the worked example prints — :func:`pols_pu` the second, and :func:`pols_all`
their sum, which is what the maintenance expense is carried on. On every model point
without the pro-rata paid-up variant the second strand is empty and the three coincide.

``SA`` is a constant in the notes and a function of ``t`` here, because the escalating
variants move it. :func:`sum_assured` is the outset value the model point carries,
:func:`cover_pp_init` the amount in force at the valuation date, and :func:`cover_pp` the
amount in force in month ``t``.

``pols_maturity`` is borrowed from the term models and means something different here.
Whole of life has no maturity: the cells is the population still alive when the
projection is truncated at the limiting age, so it is a **truncation artefact** rather
than a benefit, and it pays nothing. It exists so the roll-forward closes in the last
month; :func:`check_truncation` asserts it is negligible, which is the real statement —
if it were not, the limiting age would be too low.

.. rubric:: Two cells, two bases, and why they must not be swapped

``cell = "UW"`` is underwritten guaranteed whole of life: full underwriting, level
premiums for life, the sum assured paid once on death or earlier terminal illness.
``cell = "O50"`` is over-50s guaranteed acceptance: no underwriting at all, a fixed cash
sum, a twelve-month moratorium, and premiums ceasing at the anniversary on or after the
90th birthday while cover continues.

They share this engine and **not** their mortality basis. Full underwriting restores
select experience, so the UW cell takes an assured-lives shape. Guaranteed acceptance
removes underwriting, so the O50 pool cannot be better than the population and
self-selects worse; it takes a population shape with an anti-selection loading of 120%
**[std]**. The CMI analyses non-underwritten whole of life separately from underwritten
business for exactly this reason. Feeding either cell the other's basis produces
plausible-looking but wrong margins, and the FCA's price differential between the two
designs — £71.73 against £8.10 per £1,000 of cover — is the scale of that error. The
basis is therefore derived from :func:`cell` rather than being a free parameter.

.. rubric:: The moratorium is a discontinuity, not a curve

During the O50 cell's first twelve policy months a **non-accidental** death returns the
premiums paid — not the cash sum, not an annualized premium — while an **accidental**
death pays the full cash sum from day one. From policy month 12 the full cash sum becomes
payable for any death, and expected death outgo jumps about elevenfold on the anchor cell
between its policy months 11 and 12. That step is the signature of the product and must
not be smoothed: an annual-grid implementation has to split policy year 1 explicitly, and
the notes list smoothing it as a pitfall. On a point valued inside the moratorium the
refund reads the premiums already paid, :func:`prem_cum_pp_init`, and the step falls in
the frame at ``t = 12 - duration_mth_init()``.

Note where the year-one outgo actually comes from. In the issue month the blended
benefit is ``0.97 x £30 + 0.03 x £5,000 = £179.10``: five sixths of it is the small
accidental tail paying the full cash sum, not the premium refund. An implementation that
dropped the accidental split would understate year-one claims by about that much.

The accidental-multiplier variant doubles the accidental benefit, but **only on and after
the first anniversary** [S7] — inside the moratorium the accidental benefit is already
the full cash sum, and doubling it there, or applying the multiplier to all deaths,
overstates outgo. :func:`adb_multiplier` is applied in one place, in
``benefit_pp(t, ACC)``, past the moratorium only.

.. rubric:: Lapse pays nothing, which is the whole economics

There is no surrender value at any duration on either cell, so a lapse produces no cash
flow at all: its entire effect is through :func:`pols_if`. Every lapse therefore
extinguishes a liability for nothing, the best estimate falls monotonically as assumed
lapses rise, and the FCA records that without the continuing-payer cross-subsidy
insurers would need to rely on lapses to remain profitable. Two consequences are wired
into the model rather than left as prose:

- **No lapse after premiums cease.** There are no premiums to stop paying once the O50
  cell reaches cessation, so :func:`lapse_rate` is zero from there. Applying a lapse
  decrement past cessation silently destroys liability, and the notes list it as a
  pitfall.
- **The pro-rata paid-up variant is a different product.** Once half the expected payments
  have been made, a would-be lapse converts to a **paid-up** policy at
  ``SA x N_paid / N_expected`` instead of forfeiting everything. That converts lapse
  profit into a retained pro-rata liability and collapses most of the lapse sensitivity,
  which is why it is a variant rather than an adjustment. It is carried as a second
  population strand: :func:`pols_pu` counts the policies and :func:`pu_benefit` carries
  their aggregate cover, which is enough because paid-up policies neither lapse nor
  escalate — so the two roll forward on the same survival factor and no per-conversion
  cohort dimension is needed. For the same reason a point in force needs no history of
  when its paid-up policies converted: the count and the average cover are the strand.

.. rubric:: The crossover

On the O50 cell cumulative premiums eventually exceed the cash sum. :func:`crossover_mth`
finds the policy month: on the anchor cell ``floor(5000/30) = 166``, the month in which
the 167th monthly premium is paid — thirteen years and eleven months of premiums, which
is the FCA's stylised example exactly. It is searched rather than closed-form so that an
escalating variant still resolves, and it is reported rather than acted on — the notes'
crossover-aware lapse module, which raises lapse past the tipping point, is a pure stress
dial and is off in the base run (``lapse_crossover_beta`` is 0); switched on, it compares
the premiums paid with the cover month by month, from the opening state. Total premiums
are capped at ``P x T_cess``, so on level premiums a crossover exists only where the cash
sum is below that cap.

.. rubric:: The contract's bounds

:mod:`~.WOL_UK_S` projects any entry age its tables reach, to any limiting age. What
running in force adds is a check of the bounds a frame is sized from: an issue age of
``issue_age_min``, 18, or more, the youngest age the mortality table rates and the
product issues, and a limiting age, ``omega_age``, above it and no more than a year past
the table's last age, and at most ``omega_age_max``, 121, the shipped table's last age
plus one and the largest limiting age the compiled model's caches are sized for
(``spec_sec.py``), so that every limiting age the shipped table admits projects and a
longer table bounds no frame. :func:`proj_len` holds each point to them, and to premiums
ceasing no later than the limiting age, so that :func:`crossover_mth`'s search over the
premium-paying months runs no longer than the contract's longest cover; and it holds every
assumption to its domain too, which :mod:`~.WOL_UK_S` checks nowhere: each Reference it
raises to a power, bounds a rate with, reads through a ``min`` or a ``max``, or reads as a
share, a loading or an amount, so that no projection runs on a negative rate, benefit or
expense, or a NaN a comparison loses.

.. rubric:: Sign convention

The notes' cash flow table is income positive, which is the library-wide sign of
:func:`net_cf`, so there is no outgo-positive ``liability_cf`` companion. The notes'
worked-example table prints premium income and death outgo as separate positive columns
and omits expenses entirely "for clarity"; :func:`result_cf` carries all of them, so
``net_cf`` will not equal any column of that table.
"""

from modelx.serialize.jsonvalues import *

_formula = lambda idx: None

_bases = []

_allow_none = None

_spaces = []

# ---------------------------------------------------------------------------
# Cells

def model_point():
    """The selected model point, its row of ``model_point_table_sec.csv``, as a Series.

    Row ``idx`` of this model's own table, which carries the in-force interface beside
    :mod:`~.WOL_UK_S`'s columns, for a reader who wants every column at once: a reporting
    cell (the Space docstring), which no projection cell reads. Each attribute a formula
    reads has an accessor below, which reads its own ``Data`` vector instead.
    """
    return data.model_point_table().iloc[idx]                        # noqa: F821


def point_id():
    """The label of the selected model point, its ``point_id``, from ``Data.point_id``.

    ``Projection`` is indexed by position, ``idx``, as ``basiclife.BasicTerm_SC`` is; the
    label is what a reader finds in the table, so every refusal names it.
    """
    return int(data.point_id()[idx])                                 # noqa: F821


def cell():
    """``O50`` (over-50s guaranteed acceptance) or ``UW`` (underwritten guaranteed).

    The two cells share this engine and not their mortality basis, their lapse table,
    their expense levels or their benefit rules.  See the Space docstring.

    A reporting cell (the Space docstring), :mod:`~.WOL_UK_S`'s, which returns the column
    as read, refusing any other value: no projection cell reads it, and each branches on
    ``Data``'s decode of the same column instead, :func:`cell_code`.
    """
    v = model_point()["cell"]
    if v not in ("O50", "UW"):
        raise ValueError("invalid cell")
    return v


def cell_code():
    """The cell as its code, from ``Data.cell_code``: ``O50`` or ``UW``.

    The int References of the names (the Space docstring's *Codes*), O50 0 and UW 1, which
    the formulas compare as :mod:`~.WOL_UK_S` compares the text, and the point's row of the
    lapse table.  A code, not the quantities it selects, because the loadings, the expenses
    and the benefit rules of a cell are this Space's References and rules, which ``Data``
    cannot read.  ``Data`` refuses any other cell.
    """
    return int(data.cell_code()[idx])                                # noqa: F821


def age_at_entry():
    """The entry age of the selected model point, **age last birthday**.

    ALB rather than the age nearest birthday every other model in this library uses:
    the underwritten cell's specimen defines entry age x as "before the (x+1)th
    birthday", which is ALB, and the over-50s documents price on "age at outset" without
    stating a basis **[std]**.  All age lookups here are on that one basis.  The age at
    issue, not at the valuation date: ``age(0)`` is the attained age then.  From
    ``Data.entry_age``, ``int`` of the column as :mod:`~.WOL_UK_S` reads it.
    """
    return int(data.entry_age()[idx])                                # noqa: F821


def sex():
    """The sex (M / F) of the selected model point, as the table spells it.

    Carried for the basis lookup.  The over-50s documents state age and smoker status as
    the rate factors and do not rate by sex, so on that cell this drives the shipped
    **[std]** proxy table and nothing contractual.

    A reporting cell (the Space docstring), which returns the ``sex`` column as read: no
    projection cell reads it here, and :func:`mort_rate` reads the point's row of the
    mortality table, :func:`mort_schedule`, instead.  It refuses any value but M and F, as
    :mod:`~.WOL_UK_S`'s :func:`cell` and :func:`escalation` refuse theirs, so that it
    returns text or raises, in either engine.  ``Data`` refuses any other sex as the table
    is read, so the refusal here is met only past ``Data``'s checks; :mod:`~.WOL_UK_S`'s
    returns the column as read.
    """
    v = model_point()["sex"]
    if v not in ("M", "F"):
        raise ValueError("invalid sex")
    return v


def smoker():
    """The smoker status (NS / S), as the table spells it.

    The underwritten specimen distinguishes three smoking states; they are collapsed to
    two here **[std]**.

    A reporting cell, which refuses any value but NS and S, as :func:`sex` refuses its own,
    where :mod:`~.WOL_UK_S`'s returns the column as read: :func:`mort_rate` reads the
    point's row of the mortality table, :func:`mort_schedule`, instead.
    """
    v = model_point()["smoker"]
    if v not in ("NS", "S"):
        raise ValueError("invalid smoker")
    return v


def mort_schedule():
    """The row of ``Data.mort_table_array`` of the selected model point, 0 to 7.

    The point's basis, sex and smoker status, the keys :mod:`~.WOL_UK_S` reads
    *mort_table.csv* by beside the age, decoded in ``Data`` into the row they select,
    ``Data.mort_schedule``: ``4 x basis + 2 x sex + smoker``, the basis the cell's,
    population 0 for O50 and assured 1 for UW, as :func:`mort_basis` derives it, the sex M
    0 and F 1, and the smoker status NS 0 and S 1.
    """
    return int(data.mort_schedule()[idx])                            # noqa: F821


def sum_assured():
    """SA: the sum assured or cash sum at outset.

    :func:`cover_pp` is the amount in force in a given month, which differs from this on
    the escalating variants; on a point in force, :func:`cover_pp_init` is the amount in
    force at the valuation date, after every increase already given.  From
    ``Data.sum_assured``.
    """
    return float(data.sum_assured()[idx])                            # noqa: F821


def premium_mth():
    """P: the monthly premium at outset, guaranteed never to increase.

    A model point input, not a rate-table lookup: no insurer publishes whole of life
    premium rate tables, so any shipped scale would be a **[std]** snapshot calibrated
    to the handful of public quote anchors.  On a point in force, :func:`premium_pp_init`
    is the premium before month 0's events.  From ``Data.premium_mth``.
    """
    return float(data.premium_mth()[idx])                            # noqa: F821


def escalation():
    """``level``, ``fixed_5pct`` (the UW increasing-cover variant) or ``rpi``.

    The underwritten variant raises cover 5% and premium 10% a year - two percent of
    premium for each one percent of cover - and the over-50s RPI variant raises the cash
    sum by RPI capped at 10% and the premium by 1.5 x RPI capped at 15%.

    A reporting cell (the Space docstring), :mod:`~.WOL_UK_S`'s, which returns the column
    as read, refusing any other value: :func:`esc_cover_step` and :func:`esc_prem_step`
    branch on ``Data``'s decode of the same column instead, :func:`escalation_code`.
    """
    v = model_point()["escalation"]
    if v not in ("level", "fixed_5pct", "rpi"):
        raise ValueError("invalid escalation")
    return v


def escalation_code():
    """The escalation as its code, from ``Data.escalation_code``.

    ``LEVEL``, ``FIXED_5PCT`` or ``RPI``, the int References of the names (the Space
    docstring's *Codes*): :func:`esc_cover_step` and :func:`esc_prem_step` branch on it
    where :mod:`~.WOL_UK_S` compares the text.  A code, not the steps it selects, because
    those are this Space's References, which ``Data`` cannot read.  ``Data`` refuses any
    other escalation.
    """
    return int(data.escalation_code()[idx])                          # noqa: F821


def cessation_mths():
    """T_cess: the number of premium-paying policy months; 0 means premiums for life.

    An elapsed count on the policy clock, not a month of the frame: premiums are due in
    policy months ``duration_mth(t) < T_cess`` and policy month ``T_cess`` is the first
    premium-free month.  The over-50s cells cease at the anniversary on or after the 90th
    birthday **[std]** and cover continues; the underwritten cell has no cessation at all.
    From ``Data.cessation_months``.
    """
    return int(data.cessation_months()[idx])                         # noqa: F821


def moratorium_mths():
    """The over-50s moratorium in policy months, 12; zero on the underwritten cell.

    A count of months on the policy clock: the moratorium covers policy months
    ``duration_mth(t) < moratorium_mths()``.  The underwritten cell has a suicide clause
    over the same window instead, which is a different rule with a different
    denominator - see :func:`benefit_pp`.  From ``Data.moratorium_months``.
    """
    return int(data.moratorium_months()[idx])                        # noqa: F821


def adb_multiplier():
    """k_adb: the accidental death multiplier past the moratorium, 1 or 2.

    The 2 is one insurer's variant and applies to **accidental** death **on and after
    the first anniversary** only.  Inside the moratorium the accidental benefit is
    already the full cash sum, so doubling it there - or applying the multiplier to all
    deaths - overstates outgo.  From ``Data.variant_adb_2x``, which decodes the column as
    :mod:`~.WOL_UK_S`'s ``bool`` reads it.
    """
    return 2.0 if bool(data.variant_adb_2x()[idx]) else 1.0          # noqa: F821


def pu_variant():
    """Whether the pro-rata paid-up variant applies.

    Once half the expected payments have been made, a would-be lapse converts to a
    paid-up policy instead of forfeiting everything.  Requires a premium cessation date,
    since ``N_expected`` is measured to it; the underwritten cell has none, so the
    combination raises rather than dividing by zero, and ``Data`` refuses it as the table
    is read.  From ``Data.variant_paid_up``, which decodes the column as
    :mod:`~.WOL_UK_S`'s ``bool`` reads it.
    """
    v = bool(data.variant_paid_up()[idx])                            # noqa: F821
    if v and cessation_mths() <= 0:
        raise ValueError("the pro-rata paid-up value needs a premium cessation date")
    return v


def policy_count():
    """The number of policies the model point stands for, its ``policy_count`` column.

    A point in force at the valuation date counts the policies on full cover then, before
    any month-0 event; any other point counts the policies it issues. Either way the count
    enters the projection once: as :func:`pols_if_init` for the first, as
    :func:`pols_new_biz` in the issue month for the second. With :func:`pols_pu_init`, the
    paid-up policies, it is the only weight on the flows: every other opening-state column
    is per policy. A point may be paid-up entirely, its count 0.
    """
    return float(data.policy_count()[idx])                           # noqa: F821


def pols_if_init():
    """Full-cover policies in force at the valuation date, before any month-0 event.

    ``policy_count()`` for a point already in force at ``t = 0``
    (``duration_mth_init() > 0``), and 0 for one issued at or after it, whose policies
    enter through :func:`pols_new_biz` in the issue month instead, as in
    ``basiclife.BasicTerm_SE``. So on a point issued at ``t = 0`` this is 0, and
    ``pols_if(0)`` is the issued count.
    """
    return policy_count() if duration_mth_init() > 0 else 0.0


def duration_mth_init():
    """Completed policy months at the valuation date, the ``duration_mth`` column.

    The policy's age in months at ``t = 0``: 200 for model point 10, the paid-up point
    valued 200 months after issue, 0 for one issued at the valuation date, and -13 for one
    to be issued 13 months after it, which ``Data`` admits up to ``future_horizon_mth``
    months ahead. It is read as ``basiclife.BasicTerm_SE`` reads it, and is the one fact the
    policy clock takes from the model point; a point may be valued in any month of its
    policy year.
    """
    return int(data.duration_mth()[idx])                             # noqa: F821


def pols_pu_init():
    """Paid-up policies in force at the valuation date, before any month-0 event.

    The second strand's count, the policies already converted to paid-up by the
    pro-rata paid-up value, beside the full-cover count :func:`policy_count`.  History,
    read from the model point: :mod:`~.WOL_UK_S` would rebuild it from issue at today's
    lapse table and stress, so a stress set at the valuation date would convert lapses
    long past.  0 on a point not yet in force, on a point without the variant, and before
    the first policy month a conversion can have reached, which ``Data`` requires.
    """
    return float(data.pols_pu_init()[idx])                           # noqa: F821


def pu_benefit_pp_init():
    """The paid-up cash sum per paid-up policy at the valuation date.

    :func:`pu_benefit` at the valuation instant over :func:`pols_pu_init`: each policy's
    pro-rata paid-up value, ``SA(t) x N_paid / N_expected`` at the month it converted,
    averaged over the strand, which is all the strand needs, since paid-up policies
    neither lapse nor escalate (the Space docstring).  Per policy, so that the counts are
    the only weights.  History, read from the model point.  0 where no paid-up policy is
    in force, which ``Data`` requires.
    """
    return float(data.pu_benefit_pp_init()[idx])                     # noqa: F821


def prem_cum_pp_init():
    """CumPrem at the valuation date: the premiums paid per policy to the end of month -1.

    :func:`prem_cum_pp`'s value entering month 0, before month 0's premium: every premium
    a policy on full cover has paid since issue.  The moratorium and suicide refunds pay
    it back, the crossover stress compares it with the cover, and :func:`crossover_mth`
    reads it.  History, read from the model point, not rebuilt from the premium schedule
    at today's RPI.  0 on a point not yet in force, which ``Data`` requires.
    """
    return float(data.prem_cum_pp_init()[idx])                       # noqa: F821


def cover_pp_init():
    """SA at the valuation date: the cash sum in force before month 0's events.

    The sum assured at issue after every increase already given, measured at the start of
    month 0, before any month-0 event: the cover of policy month ``duration_mth_init() -
    1``'s year.  On a point valued on an anniversary that is the year the anniversary
    closes, and the anniversary's increase is the projection's first event, made at
    today's References (USLIB-SEC-PLAN.md D6, as precised at uslib's M7: a fixing at month
    0 itself reads the assumptions of the valuation date).  On the level cells it is the
    sum assured at issue; on the escalating ones it is history, the increases the RPI or
    the fixed step gave at the take-up of their day, which :mod:`~.WOL_UK_S` rebuilds from
    issue at today's ``rpi_rate``, ``esc_fixed_cover`` and ``esc_take_up``.
    :func:`cover_pp` steps it on each anniversary from month 0 on at today's References.
    The sum assured on a point not yet in force, which ``Data`` requires.
    """
    return float(data.cover_pp_init()[idx])                          # noqa: F821


def premium_pp_init():
    """P at the valuation date: the monthly premium before month 0's events.

    The premium at issue after every increase already given, :func:`cover_pp_init`'s
    counterpart, measured at the same instant: the premium of policy month
    ``duration_mth_init() - 1``'s year, so that on a point valued on an anniversary the
    anniversary's increase is the projection's, as the cover's is; once premiums have
    ceased, the last premium paid.  History, as the cover is.  The premium at issue on a
    point not yet in force, which ``Data`` requires.
    """
    return float(data.premium_pp_init()[idx])                        # noqa: F821


def crossover_mth_init():
    """t* before the valuation date: the policy month of the crossover, or ``-1``.

    The first policy month, before the valuation date, in which the premiums paid exceeded
    the cover in force, ``-1`` where none did, and ``-1`` on a point not yet in force: a
    crossover in month 0 or later is the projection's.  History, read from the model
    point: :mod:`~.WOL_UK_S` searches the months before the valuation date again, from
    issue at today's ``rpi_rate`` and ``esc_take_up``, which on an escalating point would
    move a crossover already past.  :func:`crossover_mth` reports it.
    """
    return int(data.crossover_mth_init()[idx])                       # noqa: F821


def t_entry():
    """The first month the policy is on the books: ``max(0, -duration_mth_init())``.

    0 for a point in force at the valuation date or issued at it, ``k`` for one issued
    ``k`` months later.  It is the base of every recursion: the counts on both strands,
    the paid-up cover and the premiums paid open there, from the opening state, and none
    reads a month before it.
    """
    return max(0, -duration_mth_init())


def is_active(t):
    """Whether month t is inside cover: issued, and short of the limiting age.

    ``0 <= duration_mth(t) < limit_mth()``.  False before issue and from the month the
    policy reaches ``omega_age``, ``t = proj_len()``.  Outside cover every count is zero,
    and so every cash flow; no count cell evaluates a rate there, and no table is read at
    a policy year or an attained age the policy does not have.
    """
    return 0 <= duration_mth(t) < limit_mth()


def limit_mth():
    """The policy month of the limiting age: ``12 x (omega_age - entry_age)``.

    :mod:`~.WOL_UK_S`'s frame from issue, its ``proj_len()``, on the policy clock: the last
    projected month is ``duration_mth(t) = limit_mth() - 1``, the last month of age
    ``omega_age - 1``, and :func:`is_active` is false from ``duration_mth(t) = limit_mth()``
    on.  Whole of life has no maturity date, so this is a limiting age rather than a
    contractual one.  :func:`proj_len` counts from the valuation date instead.

    ``omega_age`` is read as an ``int``, which :func:`proj_len` holds it to be first: a
    whole number written as a float, ``120.0``, makes the frame ``120`` makes, in whole
    months, as a compiled model typing the Reference ``long long`` would.
    """
    return 12 * (int(omega_age) - age_at_entry())                    # noqa: F821


def proj_len():
    """The number of months from the valuation date to the limiting age.

    ``limit_mth() - duration_mth_init()``: 600 for the anchor cell issued at ``t = 0``, 400
    for model point 10, in force 200 months, and the frame from issue plus ``k`` for a
    point issued ``k`` months after the valuation date.  The frame is
    ``t = 0, 1, ..., proj_len() - 1``; ``proj_len()`` is its exclusive end and the row count
    of :func:`result_cf`.  Whole of life has no maturity date, so the horizon is a
    **limiting age** rather than a contractual one.  The shipped mortality tables reach 1
    well before ``omega_age``, so the population is exhausted inside the projection rather
    than truncated by it; :func:`check_truncation` asserts that, because a limiting age set
    too low would silently drop liability off the end.

    These raise here, naming the point, rather than project nothing, a frame the contract
    does not have, or numbers no policy can have, each checked in this order:

    * ``issue_age_min`` that is not a whole number below ``2**53``, or is below 0: an age,
      which a NaN would switch off, every comparison with it failing;
    * a point issued below ``issue_age_min``, 18, the youngest age the mortality table
      rates and the product issues at;
    * ``omega_age`` that is not a whole number below ``2**53``, or is not above
      ``issue_age_min`` and at most a year past the mortality table's last age,
      ``Data.mort_age_last() + 1``, since the projection reads attained ages to
      ``omega_age - 1``: the limiting age sizes every frame, and a NaN, an infinity or a
      fraction of a year would leave the frame's months no whole number;
    * ``omega_age_max`` that is not a whole number below ``2**53``, and ``omega_age``
      above it: the largest limiting age the compiled model's caches are sized for
      (``spec_sec.py``), 121, the shipped table's last age plus one, so that every
      limiting age the shipped table admits projects, and a longer table, which would
      admit a later one, bounds no frame;
    * a point issued at or past ``omega_age``, which has no cover from issue;
    * a point at or past the limiting age at the valuation date, ``duration_mth`` at or
      past :func:`limit_mth`, keyed on the policy clock, which an in-force extract should
      not carry;
    * a point whose premiums cease past the limiting age, ``cessation_months`` above
      :func:`limit_mth`: no premium is payable after cover ends, and :func:`crossover_mth`
      searches the premium-paying months, so that no point the frame accepts runs that
      search past the contract's longest cover, 1,236 months, where a cessation of
      ``2**52`` months would run it about ``4.5e15`` times.  Premiums ceasing at the
      limiting age itself, ``cessation_months`` equal to :func:`limit_mth`, are payable to
      the end of cover, and read;
    * any point while a Reference is off its domain, which the message names. NaN and the
      infinities are outside every one:

      - ``mort_loading_o50`` and ``mort_loading_uw``, finite, 0 or more: factors on a
        probability, read inside the mortality cap's ``min``, where an infinity reads as
        certain death and below 0 a rate is negative;
      - ``mort_improvement``, finite, 1 or less: the factor it makes, ``(1 - r)`` to the
        years since the valuation date, is below 0 past 1, and changes sign each year;
      - ``acc_share`` and ``suicide_share``, from 0 to 1: the shares of the deaths that are
        accidental, or suicides refunded, which blend two benefits;
      - ``suicide_mths``, a whole number of months below ``2**53``, 0 or more: the window
        compares a policy month with it, and a NaN would close it;
      - ``rpi_rate``, finite: the floor at 0 and the cover cap read an infinity as no
        increase or as the cap;
      - ``esc_rpi_cover_cap``, ``esc_rpi_prem_cap`` and ``esc_rpi_prem_mult``, finite, 0 or
        more: each cap is a bound written second, which a NaN cap would be lost through,
        ``min`` keeping its first argument, and below 0 an increase is a cut;
      - ``esc_fixed_cover`` and ``esc_fixed_prem``, finite, 0 or more: the fixed increases,
        each raised to the policy years, which the source defines as increases only;
      - ``esc_take_up``, from 0 to 1, the share of each increase taken up;
      - ``lapse_crossover_beta``, finite, 0 or more: the stress dial, a NaN of which is
        switched off by its comparison with 0, and an infinity read as a certain lapse
        through the lapse rate's ``min``, its bound first as in :mod:`~.WOL_UK_S`;
      - ``inflation_rate``, finite, -1 or more: below -1 the inflation factor changes sign
        each year;
      - the expenses, ``expense_acq_o50``, ``expense_acq_uw``, ``expense_maint_o50`` and
        ``expense_maint_uw``, and ``comm_init_rate``, finite, 0 or more: below 0 an
        income.

    The rules read this Space's References, which ``Data`` cannot see, so they are checked
    here.  They are the contract the compiled model's caches are sized from
    (``spec_sec.py``): a frame of at most ``omega_age_max - issue_age_min`` years and the
    future horizon, ``Data.future_horizon_mth``, so 1,356 months, and attained ages from 18
    to ``omega_age - 1`` on the mortality table.  Every report reads this cell first, and so
    does every check, so no point outside them is projected, in modelx as compiled.
    Raising ``omega_age_max`` or the horizon, or lowering ``issue_age_min``, needs the
    spec's sizes raised and the model rebuilt, or a report runs past the caches in the
    compiled model alone, raising ``IndexError`` where modelx projects.  Each check is a
    comparison written out, a finite bound the largest float, 1.7976931348623157e308, and
    a whole one ``2**53``, so that a compiled cell runs it in C, and each Reference is
    printed as the compiled model types it: ``issue_age_min``, ``omega_age``,
    ``omega_age_max`` and ``suicide_mths`` through ``int()`` once they are whole numbers,
    and every other through ``float()``; ``omega_age`` is then read as the ``int`` it is.
    A value a formula computes past the floats, from References and an opening state each
    in its domain, is refused in the cell where it first is, naming the point: the cover,
    the premium, the premiums paid, a benefit, the paid-up cover, the premiums, the claims,
    the expenses, the commission and the net cash flow.  A power that overflows is not:
    modelx, as Python, raises ``OverflowError``, with the platform's own message, from the
    ``**`` itself, before the cell can look at the result - the cover's and the premium's
    step to the policy years since the valuation date, the inflation and improvement
    factors, and the crossover's search, each at a step in its domain but large enough,
    ``1e200``.  Compiled, each of those cells calls Python's own float power where its C
    ``pow`` gives an infinity from a finite base, uslib's M22 form, so that both engines
    raise the same error, with the platform's message.
    """
    if not (issue_age_min > -9007199254740992.0                       # noqa: F821
            and issue_age_min < 9007199254740992.0                    # noqa: F821
            and issue_age_min == issue_age_min // 1):                 # noqa: F821
        raise ValueError(f"point_id {point_id()}: issue_age_min must be a whole number "  # noqa: F821
                         f"below 2**53, not {float(issue_age_min)}")  # noqa: F821
    if issue_age_min < 0:                                            # noqa: F821
        raise ValueError(f"point_id {point_id()}: issue_age_min must be 0 or more, "  # noqa: F821
                         f"not {int(issue_age_min)}")                # noqa: F821
    x = age_at_entry()
    if x < issue_age_min:                                            # noqa: F821
        raise ValueError(f"point_id {point_id()}: the issue age, {x}, is below "  # noqa: F821
                         f"issue_age_min, {int(issue_age_min)}")     # noqa: F821
    if not (omega_age > -9007199254740992.0                           # noqa: F821
            and omega_age < 9007199254740992.0                        # noqa: F821
            and omega_age == omega_age // 1):                         # noqa: F821
        raise ValueError(f"point_id {point_id()}: omega_age must be a whole number "  # noqa: F821
                         f"below 2**53, not {float(omega_age)}")     # noqa: F821
    if not (omega_age > issue_age_min                                # noqa: F821
            and omega_age <= data.mort_age_last() + 1):               # noqa: F821
        raise ValueError(
            f"point_id {point_id()}: omega_age must be above issue_age_min, "  # noqa: F821
            f"{int(issue_age_min)}, and at most {data.mort_age_last() + 1}, a year past "  # noqa: F821
            f"mort_table.csv's last age, not {int(omega_age)}")      # noqa: F821
    if not (omega_age_max > -9007199254740992.0                       # noqa: F821
            and omega_age_max < 9007199254740992.0                    # noqa: F821
            and omega_age_max == omega_age_max // 1):                 # noqa: F821
        raise ValueError(f"point_id {point_id()}: omega_age_max must be a whole number "
                         f"below 2**53, not {float(omega_age_max)}")  # noqa: F821
    if omega_age > omega_age_max:                                    # noqa: F821
        raise ValueError(f"point_id {point_id()}: omega_age, {int(omega_age)}, is above "  # noqa: F821
                         f"omega_age_max, {int(omega_age_max)}")     # noqa: F821
    if limit_mth() <= 0:
        raise ValueError(f"point_id {point_id()}: the issue age, {x}, is at or past "  # noqa: F821
                         f"omega_age, {int(omega_age)}: the policy has no cover")  # noqa: F821
    d = duration_mth_init()
    if d >= limit_mth():
        raise ValueError(
            f"point_id {point_id()}: duration_mth {d} is at or past the limiting age, "  # noqa: F821
            f"policy month {limit_mth()}, omega_age {int(omega_age)}")  # noqa: F821
    if cessation_mths() > limit_mth():
        raise ValueError(
            f"point_id {point_id()}: cessation_months {cessation_mths()} is past the "
            f"limiting age, policy month {limit_mth()}, omega_age {int(omega_age)}")  # noqa: F821
    if not (mort_loading_o50 >= 0.0                                  # noqa: F821
            and mort_loading_o50 <= 1.7976931348623157e308):          # noqa: F821
        raise ValueError(f"point_id {point_id()}: mort_loading_o50 must be a finite "  # noqa: F821
                         f"number, 0 or more, not {float(mort_loading_o50)}")  # noqa: F821
    if not (mort_loading_uw >= 0.0                                   # noqa: F821
            and mort_loading_uw <= 1.7976931348623157e308):           # noqa: F821
        raise ValueError(f"point_id {point_id()}: mort_loading_uw must be a finite "  # noqa: F821
                         f"number, 0 or more, not {float(mort_loading_uw)}")  # noqa: F821
    if not (mort_improvement >= -1.7976931348623157e308               # noqa: F821
            and mort_improvement <= 1.0):                             # noqa: F821
        raise ValueError(f"point_id {point_id()}: mort_improvement must be a finite "  # noqa: F821
                         f"number, 1 or less, not {float(mort_improvement)}")  # noqa: F821
    if not (acc_share >= 0.0 and acc_share <= 1.0):                  # noqa: F821
        raise ValueError(f"point_id {point_id()}: acc_share must be a number from 0 to 1, "  # noqa: F821
                         f"not {float(acc_share)}")                  # noqa: F821
    if not (suicide_share >= 0.0 and suicide_share <= 1.0):          # noqa: F821
        raise ValueError(f"point_id {point_id()}: suicide_share must be a number from 0 "  # noqa: F821
                         f"to 1, not {float(suicide_share)}")        # noqa: F821
    if not (suicide_mths > -9007199254740992.0                        # noqa: F821
            and suicide_mths < 9007199254740992.0                     # noqa: F821
            and suicide_mths == suicide_mths // 1):                   # noqa: F821
        raise ValueError(f"point_id {point_id()}: suicide_mths must be a whole number "  # noqa: F821
                         f"below 2**53, not {float(suicide_mths)}")  # noqa: F821
    if suicide_mths < 0:                                             # noqa: F821
        raise ValueError(f"point_id {point_id()}: suicide_mths must be 0 or more, not "  # noqa: F821
                         f"{int(suicide_mths)}")                     # noqa: F821
    if not (rpi_rate >= -1.7976931348623157e308                       # noqa: F821
            and rpi_rate <= 1.7976931348623157e308):                  # noqa: F821
        raise ValueError(f"point_id {point_id()}: rpi_rate must be a finite number, "  # noqa: F821
                         f"not {float(rpi_rate)}")                   # noqa: F821
    if not (esc_rpi_cover_cap >= 0.0                                 # noqa: F821
            and esc_rpi_cover_cap <= 1.7976931348623157e308):         # noqa: F821
        raise ValueError(f"point_id {point_id()}: esc_rpi_cover_cap must be a finite "  # noqa: F821
                         f"number, 0 or more, not {float(esc_rpi_cover_cap)}")  # noqa: F821
    if not (esc_rpi_prem_mult >= 0.0                                 # noqa: F821
            and esc_rpi_prem_mult <= 1.7976931348623157e308):         # noqa: F821
        raise ValueError(f"point_id {point_id()}: esc_rpi_prem_mult must be a finite "  # noqa: F821
                         f"number, 0 or more, not {float(esc_rpi_prem_mult)}")  # noqa: F821
    if not (esc_rpi_prem_cap >= 0.0                                  # noqa: F821
            and esc_rpi_prem_cap <= 1.7976931348623157e308):          # noqa: F821
        raise ValueError(f"point_id {point_id()}: esc_rpi_prem_cap must be a finite "  # noqa: F821
                         f"number, 0 or more, not {float(esc_rpi_prem_cap)}")  # noqa: F821
    if not (esc_fixed_cover >= 0.0                                   # noqa: F821
            and esc_fixed_cover <= 1.7976931348623157e308):           # noqa: F821
        raise ValueError(f"point_id {point_id()}: esc_fixed_cover must be a finite "  # noqa: F821
                         f"number, 0 or more, not {float(esc_fixed_cover)}")  # noqa: F821
    if not (esc_fixed_prem >= 0.0                                    # noqa: F821
            and esc_fixed_prem <= 1.7976931348623157e308):            # noqa: F821
        raise ValueError(f"point_id {point_id()}: esc_fixed_prem must be a finite "  # noqa: F821
                         f"number, 0 or more, not {float(esc_fixed_prem)}")  # noqa: F821
    if not (esc_take_up >= 0.0 and esc_take_up <= 1.0):              # noqa: F821
        raise ValueError(f"point_id {point_id()}: esc_take_up must be a number from 0 to "  # noqa: F821
                         f"1, not {float(esc_take_up)}")             # noqa: F821
    if not (lapse_crossover_beta >= 0.0                              # noqa: F821
            and lapse_crossover_beta <= 1.7976931348623157e308):      # noqa: F821
        raise ValueError(f"point_id {point_id()}: lapse_crossover_beta must be a finite "  # noqa: F821
                         f"number, 0 or more, not {float(lapse_crossover_beta)}")  # noqa: F821
    if not (inflation_rate >= -1.0                                   # noqa: F821
            and inflation_rate <= 1.7976931348623157e308):            # noqa: F821
        raise ValueError(f"point_id {point_id()}: inflation_rate must be a finite "  # noqa: F821
                         f"number, -1 or more, not {float(inflation_rate)}")  # noqa: F821
    if not (expense_acq_o50 >= 0.0                                   # noqa: F821
            and expense_acq_o50 <= 1.7976931348623157e308):           # noqa: F821
        raise ValueError(f"point_id {point_id()}: expense_acq_o50 must be a finite "  # noqa: F821
                         f"number, 0 or more, not {float(expense_acq_o50)}")  # noqa: F821
    if not (expense_acq_uw >= 0.0                                    # noqa: F821
            and expense_acq_uw <= 1.7976931348623157e308):            # noqa: F821
        raise ValueError(f"point_id {point_id()}: expense_acq_uw must be a finite "  # noqa: F821
                         f"number, 0 or more, not {float(expense_acq_uw)}")  # noqa: F821
    if not (expense_maint_o50 >= 0.0                                 # noqa: F821
            and expense_maint_o50 <= 1.7976931348623157e308):         # noqa: F821
        raise ValueError(f"point_id {point_id()}: expense_maint_o50 must be a finite "  # noqa: F821
                         f"number, 0 or more, not {float(expense_maint_o50)}")  # noqa: F821
    if not (expense_maint_uw >= 0.0                                  # noqa: F821
            and expense_maint_uw <= 1.7976931348623157e308):          # noqa: F821
        raise ValueError(f"point_id {point_id()}: expense_maint_uw must be a finite "  # noqa: F821
                         f"number, 0 or more, not {float(expense_maint_uw)}")  # noqa: F821
    if not (comm_init_rate >= 0.0                                    # noqa: F821
            and comm_init_rate <= 1.7976931348623157e308):            # noqa: F821
        raise ValueError(f"point_id {point_id()}: comm_init_rate must be a finite "  # noqa: F821
                         f"number, 0 or more, not {float(comm_init_rate)}")  # noqa: F821
    return limit_mth() - d


def duration_init():
    """The completed policy years the opening cover and premium hold.

    Those of policy month ``duration_mth_init() - 1``, the month before the valuation date,
    on a point in force, since :func:`cover_pp_init` and :func:`premium_pp_init` are
    measured before month 0's events, and 0 on a point not yet in force, whose columns are
    the issue values: ``(max(duration_mth_init(), 1) - 1) // 12``.  The cover and the
    premium step once for each anniversary from there to month t,
    ``duration(t) - duration_init()``, so that an anniversary at the valuation date steps
    them at ``t = 0``, at today's References.
    """
    return (max(duration_mth_init(), 1) - 1) // 12


def duration(t):
    """Completed policy years at the start of month t: ``duration_mth(t) // 12``.

    0 throughout the first policy year, and negative before issue: the count of
    anniversaries the escalation steps on.
    """
    return duration_mth(t) // 12


def duration_mth(t):
    """Completed policy months at the start of month t, the **policy** clock.

    ``duration_mth_init() + t``: ``t`` counts months from the valuation date and
    ``duration_mth(t)`` months from issue, and the two move together.  A closed form,
    where ``basiclife.BasicTerm_SE`` adds one a month by recursion: the same numbers,
    without a call chain as long as the frame.  Negative before issue.  The moratorium,
    the suicide window, premium cessation and the payments made read it.
    """
    return duration_mth_init() + t


def policy_year(t):
    """y: the 1-based policy year containing month t, ``duration(t) + 1``.

    A contractual label, derived from the policy clock and never indexed by: the lapse
    table is keyed by it, and the first year's commission reads it.  0 or less before
    issue, where nothing reads a table by it.
    """
    return duration(t) + 1


def age(t):
    """a(t): the attained age (ALB) in month t, ``age_at_entry() + duration(t)``."""
    return age_at_entry() + duration(t)


def mort_basis():
    """The mortality basis the cell takes: ``population`` for O50, ``assured`` for UW.

    Derived from :func:`cell` rather than left as a free parameter, because feeding
    either cell the other's basis produces plausible-looking but wrong margins.  See the
    Space docstring.

    A reporting cell (the Space docstring), :mod:`~.WOL_UK_S`'s, which returns the point's
    ``cell`` column through the map O50 to population and UW to assured, the registry's
    ``"reporting_columns"``, and refuses what :func:`cell` refuses: :func:`mort_rate` reads
    the point's row of the mortality table, :func:`mort_schedule`, which ``Data`` decodes
    from the same basis, instead.
    """
    return "population" if cell() == "O50" else "assured"


def mort_loading():
    """The anti-selection loading on the table rate: 120% for O50, 100% for UW **[std]**.

    Guaranteed acceptance removes underwriting, so the pool cannot be better than the
    population and self-selects worse.  No insurer discloses its guaranteed-acceptance
    pricing basis, so the loading is a placeholder to be calibrated - and a deliberately
    modest one, since population mortality is already heavier than insured experience.
    """
    return mort_loading_o50 if cell_code() == O50 else mort_loading_uw  # noqa: F821


def mort_improve_factor(t):
    """The mortality improvement factor in month t, on the valuation clock; 1 in the base run.

    ``(1 - improvement)^(t // 12)``: 1 through the first year from the valuation date, and
    stepping on each anniversary of it, for every point alike, whatever its age
    (USLIB-SEC-PLAN.md D7, as ``ULSG_US_SEC``'s improvement runs).  The tables state
    mortality at the valuation date, and improvement runs from there: :mod:`~.WOL_UK_S`
    improves from issue, ``(1 - improvement)^(y - 1)``, which on a point in force would
    improve a table stated today by the years the policy has already run.  On a point
    issued at ``t = 0`` the two are the same.  The market-standard expression is a CMI
    projections model with a chosen long-term rate, but that model is subscriber-restricted,
    so a flat annual improvement is the **[std]** sensitivity proxy.  Improvements lengthen
    exactly the part of the liability that is pure outgo - past the crossover and past
    premium cessation - so this is not a second-order dial on this product.
    :func:`proj_len` holds ``mort_improvement`` to a finite number, 1 or less, so the factor
    is a number, 0 or more.

    The exponent is a whole number of years, 0 or more, so the power is real whatever the
    base.  Within the longest frame and the month after it, 113 years from the valuation
    date, it passes the largest float only where the base is above about 534, an
    improvement below about -533 a year, a deterioration no product reaches.  Python's
    float power raises ``OverflowError`` past the largest float,
    where C's ``pow`` gives an infinity, so where the power is infinite from a finite base
    the cell calls Python's own, which raises the platform's message in the compiled model
    as in modelx (USLIB-SEC-PLAN.md, *Record -- M22*); modelx never reaches the call, its
    own power raising first.
    """
    base = 1.0 - mort_improvement                                    # noqa: F821
    n = t // 12
    factor = base ** n
    if factor - factor != 0.0 and base - base == 0.0:
        raise float.__pow__(base, n)
    return factor


def mort_rate(t):
    """q(y): the annual mortality rate applied in the policy year containing month t.

    The cell's table rate at the attained age, times the anti-selection loading and the
    improvement factor, capped at 1, the bound second, ``min(q, 1.0)``, so that a missing
    input, a NaN, stays NaN, where ``min(1.0, q)`` would read it as 1: :mod:`~.WOL_UK_S`'s
    cap, and no departure.  Both shipped bases are **[std]** proxies shaped like the tables
    the notes name and are not published tables.

    Zero outside cover, where ``age(t)`` is not an age the policy reaches.  Inside it, this
    is the one cell that reads ``Data.mort_table_array``, at the point's row,
    :func:`mort_schedule`, and the attained age, the array's index, as :mod:`~.WOL_UK_S`
    reads its table at the basis, sex, smoker status and age.  An age outside the table's,
    ``Data.mort_age_first`` to ``Data.mort_age_last``, raises ``ValueError``, naming the
    point and the age, where :mod:`~.WOL_UK_S`'s lookup raised ``KeyError``, rather than
    reading the array's padding or wrapping round to its end.
    """
    if not is_active(t):
        return 0.0
    x = age(t)
    if x < data.mort_age_first() or x > data.mort_age_last():        # noqa: F821
        raise ValueError(f"point_id {point_id()}: mort_table.csv has no rate at "
                         f"attained age {x}")
    q = float(data.mort_table_array()[mort_schedule(), x])           # noqa: F821
    return min(q * mort_loading() * mort_improve_factor(t), 1.0)


def mort_rate_mth(t):
    """q_m(y) = 1 - (1 - q)^(1/12): the monthly mortality rate **[std]**."""
    return 1.0 - (1.0 - mort_rate(t)) ** (1.0 / 12.0)


def esc_cover_step():
    """The annual increase in the sum assured under the escalation variant.

    5% on the underwritten increasing-cover variant, and RPI floored at 0 and capped at
    10% on the over-50s RPI variant.  Scaled by ``esc_take_up``, which is 1 in the
    base run: holders may decline an increase, with three declines removing the option,
    but a deterministic run cannot represent a take-up probability, so full take-up is
    assumed and the decline rule is not implemented.  The increase from the valuation
    date on: those already given are history, :func:`cover_pp_init`.  The escalation is
    :func:`escalation_code`, compared as :mod:`~.WOL_UK_S` compares the text.
    """
    e = escalation_code()
    if e == LEVEL:                                                   # noqa: F821
        return 0.0
    if e == FIXED_5PCT:                                              # noqa: F821
        return esc_fixed_cover * esc_take_up                         # noqa: F821
    return min(max(rpi_rate, 0.0), esc_rpi_cover_cap) * esc_take_up  # noqa: F821


def esc_prem_step():
    """The annual increase in the premium under the escalation variant.

    10% on the underwritten variant - two percent of premium for each one percent of
    cover - and ``1.5 x RPI`` capped at 15% on the over-50s RPI variant.  Floored at 0:
    the source defines an increase only, with no decrease **[std]**.  The increase from
    the valuation date on: those already given are history, :func:`premium_pp_init`.  The
    escalation is :func:`escalation_code`, as in :func:`esc_cover_step`.
    """
    e = escalation_code()
    if e == LEVEL:                                                   # noqa: F821
        return 0.0
    if e == FIXED_5PCT:                                              # noqa: F821
        return esc_fixed_prem * esc_take_up                          # noqa: F821
    return min(max(esc_rpi_prem_mult * rpi_rate, 0.0),               # noqa: F821
               esc_rpi_prem_cap) * esc_take_up                       # noqa: F821


def cover_pp(t):
    """SA(t): the sum assured or cash sum in force in month t.

    :func:`cover_pp_init`, the cover before month 0's events, the sum assured at issue on
    a point not yet in force, times ``(1 + step)`` for each policy anniversary since,
    ``duration(t) - duration_init()``, so it steps at policy anniversaries on the policy
    clock.  The increases before the valuation date are history, carried in, and those
    from it on are projected at today's step, an anniversary at the valuation date's
    among them.  On the RPI
    variant the cash sum **continues to index after premiums cease at 90**, which is why
    this carries no cessation test - the premium step, being applied to a zero premium,
    stops of its own accord.  Zero outside cover.

    A cover that leaves the floats, from an opening cover or a step each in its domain,
    raises ``ValueError`` in the month it first does, naming the point, the month and what
    makes it, rather than pay an infinite claim.  The step's power is computed first, as
    :mod:`~.WOL_UK_S` computes it, and where it is infinite from a finite base the cell
    calls Python's own float power, which raises ``OverflowError`` with the platform's
    message in the compiled model as in modelx, where C's ``pow`` gives an infinity
    (USLIB-SEC-PLAN.md, *Record -- M22*); modelx never reaches the call, its own power
    raising first.  The exponent is a whole number of years, 0 or more, so the power is
    real; within the longest cover, 102 anniversaries, only a step of the order of a
    thousand a year, a cover multiplied a thousandfold each year, passes the floats.
    """
    if not is_active(t):
        return 0.0
    base = 1.0 + esc_cover_step()
    n = duration(t) - duration_init()
    step = base ** n
    if step - step != 0.0 and base - base == 0.0:
        raise float.__pow__(base, n)
    cover = cover_pp_init() * step
    if not cover - cover == 0.0:
        raise ValueError(
            f"point_id {point_id()}: the cover cover_pp({t}) is {cover}, not a finite "  # noqa: F821
            f"number, from cover_pp_init {cover_pp_init()} and an annual increase of "
            f"{esc_cover_step()}")
    return cover


def premium_pp(t):
    """P(t): the monthly premium due at the beginning of month t.

    Due in policy months ``duration_mth(t) < cessation_mths()`` - the T_cess premiums of
    the premium-paying period - and zero from policy month ``cessation_mths()`` on.  Then
    :func:`premium_pp_init`, the premium before month 0's events, the premium at issue on a
    point not yet in force, times ``(1 + step)`` for each policy anniversary since,
    ``duration(t) - duration_init()``, as the cover steps.  Zero too on a paid-up policy, which is carried as a separate
    population strand rather than as a premium of zero, so it does not appear here, and
    zero outside cover.

    A premium that leaves the floats raises ``ValueError`` in the month it first does, as
    :func:`cover_pp` does, and a step's power past the largest float ``OverflowError``, in
    M22's form, as the cover's does.
    """
    if not is_active(t):
        return 0.0
    if cessation_mths() > 0 and duration_mth(t) >= cessation_mths():
        return 0.0
    base = 1.0 + esc_prem_step()
    n = duration(t) - duration_init()
    step = base ** n
    if step - step != 0.0 and base - base == 0.0:
        raise float.__pow__(base, n)
    p = premium_pp_init() * step
    if not p - p == 0.0:
        raise ValueError(
            f"point_id {point_id()}: the premium premium_pp({t}) is {p}, not a finite "  # noqa: F821
            f"number, from premium_pp_init {premium_pp_init()} and an annual increase of "
            f"{esc_prem_step()}")
    return p


def prem_cum_pp(t):
    """CumPrem(t): cumulative premiums paid per policy to the end of month t.

    The premium falls at the beginning of the month and death at the end, so a death in
    month t has had the month-t premium paid on it - which is why the moratorium refund
    in the issue month is one month's premium and not nothing.  This is the **refund
    base**: a year-one non-accidental claim pays cumulative premiums paid, not the cash sum
    and not an annualized premium.

    At :func:`t_entry` it is :func:`prem_cum_pp_init`, the premiums paid before the
    valuation date, 0 on a point not yet in force, plus the month's premium; each later
    month adds its own, so the chain reads no month before :func:`t_entry`.  Zero outside
    cover.  A total that leaves the floats is refused in the month it first does, by
    :func:`prem_cum_pp_refusal`, which this cell calls on that error path alone: it is on
    a chain, which a compiled run recurses through on the C stack, so it formats no
    message itself.

    In the first month of a policy year after :func:`t_entry` the total carried in is the
    year's opening, :func:`prem_cum_pp_py`, which is ``prem_cum_pp(t - 1)``, bit for bit:
    the running sum blocked by policy year, as :func:`pols_if_at`'s count is, so that a
    cold read runs one cell a month within its year and two cells a year before it.
    """
    if not is_active(t):
        return 0.0
    if t == t_entry():
        paid = prem_cum_pp_init() + premium_pp(t)
    elif duration_mth(t) % 12 == 0:
        paid = prem_cum_pp_py(policy_year(t)) + premium_pp(t)
    else:
        paid = prem_cum_pp(t - 1) + premium_pp(t)
    if not paid - paid == 0.0:
        return prem_cum_pp_refusal(t)
    return paid


def prem_cum_pp_py(y):
    """CumPrem entering policy year y: the premiums paid per policy to the end of policy
    year y - 1.

    The running sum blocked by policy year, as :func:`pols_if_py` blocks the count: it
    walks the months of policy year ``y - 1`` on the books in ascending order, asking
    :func:`prem_cum_pp` of each, so that each finds the month before cached, and returns
    the year's last month's, :func:`prem_cum_pp`'s own value.  :func:`prem_cum_pp` reads it
    in the first month of policy year ``y``, in cover and after :func:`t_entry`, so ``y``
    runs from 2 to 103 at the contract's longest cover, as :func:`pols_if_py`'s does; no
    other cell reads it but :func:`prem_cum_pp_refusal`, on its error path.
    """
    d = duration_mth_init()
    first = max(t_entry(), 12 * (y - 2) - d)
    last = 12 * (y - 1) - 1 - d
    for s in range(first, last):
        prem_cum_pp(s)
    return prem_cum_pp(last)


def prem_cum_pp_refusal(t):
    """The refusal of premiums paid past the floats in month t, :func:`prem_cum_pp`'s, in a
    cell of its own.

    A compiled cell's C frame holds the code that formats each of its messages, whether a
    run reaches it or not, and a chain holds a frame of each cell it recurses through at
    each level.  :func:`prem_cum_pp` is a chain, so it calls this cell only where the total
    it adds has left the floats, and the message is formatted in this cell's frame, which
    no chain holds on a run that does not raise.  It takes the month alone, the one value
    of the message that is not a cell's, since a float parameter would give the compiled
    cell a dictionary for a cache: it adds the total as :func:`prem_cum_pp` does, from the
    same cells, the same float, and refuses it where it is not a finite number, naming the
    point, the month and the opening total, :func:`prem_cum_pp_init`, in
    :func:`prem_cum_pp`'s words.  Where it is finite, it returns it, as the sample asks for
    it in every month, to type the cell; 0 outside cover.
    """
    if not is_active(t):
        return 0.0
    if t == t_entry():
        paid = prem_cum_pp_init() + premium_pp(t)
    elif duration_mth(t) % 12 == 0:
        paid = prem_cum_pp_py(policy_year(t)) + premium_pp(t)
    else:
        paid = prem_cum_pp(t - 1) + premium_pp(t)
    if not paid - paid == 0.0:
        raise ValueError(
            f"point_id {point_id()}: the premiums paid prem_cum_pp({t}) are {paid}, not a "
            f"finite number, from prem_cum_pp_init {prem_cum_pp_init()}")
    return paid


def in_moratorium(t):
    """Whether month t falls inside the over-50s moratorium, on the policy clock.

    ``duration_mth(t) < moratorium_mths()``: the first twelve policy months, wherever they
    fall in the frame.  Always False on the UW cell, whose moratorium is 0 months, and
    False outside cover.
    """
    if not is_active(t):
        return False
    return duration_mth(t) < moratorium_mths()


def payments_made(t):
    """N_paid(t): the number of monthly payments made by the end of month t.

    ``min(duration_mth(t) + 1, T_cess)``: the premium of each policy month is paid at its
    start, so ``duration_mth(t) + 1`` payments have been made by the end of month t until
    cessation caps the count, on the policy clock, with no payment holiday modelled.  0
    outside cover.
    """
    if not is_active(t):
        return 0
    if cessation_mths() <= 0:
        return duration_mth(t) + 1
    return min(duration_mth(t) + 1, cessation_mths())


def payments_expected():
    """N_expected: the payments expected over the premium-paying period.

    The pro-rata paid-up denominator, so it is the cessation month; zero where premiums
    are payable for life, in which case the variant does not apply.
    """
    return cessation_mths()


def pu_eligible(t):
    """Whether a would-be lapse in month t converts to paid-up instead of terminating.

    The pro-rata paid-up rule: at least half the expected payments must have been made
    [S9].  Before that halfway point a lapse is a total loss and the base lapse rate
    applies; after it, forfeiture is strictly dominated, so **all** would-be lapses are
    assumed to convert **[std]**.  False outside cover.
    """
    if not is_active(t) or not pu_variant():
        return False
    return payments_made(t) >= payments_expected() / 2.0


def crossover_mth():
    """t*: the first policy month in which cumulative premiums exceed the cover in force.

    ``t* = floor(SA/P)`` under level premiums, the month in which the
    ``floor(SA/P) + 1``-th premium is paid: policy month 166 on the anchor cell, the
    167th monthly premium, thirteen years and eleven months of premiums, which is the
    FCA's stylised example exactly - but searched rather than closed-form so that an
    escalating variant still resolves.  Returns ``-1`` where the crossover never happens,
    which is the case whenever the cash sum exceeds the total premiums payable to
    cessation; ``0`` is a real month, so it cannot be the sentinel.  A policy month, as in
    :mod:`~.WOL_UK_S`, on every point: the crossover is a fact of the contract, which can
    fall before the valuation date.

    Before the valuation date it is history, :func:`crossover_mth_init`, read from the
    model point and never searched for again: a crossover already past on an escalating
    point fell where the increases of its day put it, which today's References need not
    reproduce.  Otherwise the search runs over the policy months from the valuation date,
    or from issue on a point not yet in force, to cessation, or to the limiting age where
    premiums are payable for life, on the contractual schedule: in each policy year the
    premium and the cover of the year, carried from the opening state and stepped on each
    anniversary at today's References, the premiums paid accumulating from
    :func:`prem_cum_pp_init`.  On a point not yet in force that is :mod:`~.WOL_UK_S`'s own
    search, from the premium and the sum assured at issue.  It asks :func:`proj_len` for
    the frame first, as a report does, so that a Reference off its domain is refused here
    too.  No cell of the projection reads it: the crossover stress on the lapse rate
    compares the premiums paid and the cover month by month instead.

    The search is one loop, with no tuple, text or generator, so that it compiles to a C
    loop, and runs at most 1,236 months a point, the contract's longest cover:
    :func:`proj_len` refuses a cessation past the limiting age.  Each step's power is computed as
    :mod:`~.WOL_UK_S` computes it, the premium's and then the cover's, and where one is
    infinite from a finite base the cell calls Python's own float power, which raises
    ``OverflowError`` with the platform's message in the compiled model as in modelx, where
    C's ``pow`` gives an infinity (USLIB-SEC-PLAN.md, *Record -- M22*); modelx never
    reaches the call, its own power raising first.
    """
    end = duration_mth_init() + proj_len()
    last = cessation_mths() if cessation_mths() > 0 else end
    d = duration_mth_init()
    if d > 0 and crossover_mth_init() >= 0:
        return crossover_mth_init()
    c = esc_cover_step()
    g = esc_prem_step()
    prem_base = 1.0 + g
    cover_base = 1.0 + c
    if d <= 0:
        paid = 0.0
        for m in range(last):
            n = m // 12
            grown = prem_base ** n
            if grown - grown != 0.0 and prem_base - prem_base == 0.0:
                raise float.__pow__(prem_base, n)
            paid = paid + premium_mth() * grown
            stepped = cover_base ** n
            if stepped - stepped != 0.0 and cover_base - cover_base == 0.0:
                raise float.__pow__(cover_base, n)
            if paid > sum_assured() * stepped:
                return m
        return -1
    paid = prem_cum_pp_init()
    for m in range(d, last):
        n = m // 12 - duration_init()
        grown = prem_base ** n
        if grown - grown != 0.0 and prem_base - prem_base == 0.0:
            raise float.__pow__(prem_base, n)
        paid = paid + premium_pp_init() * grown
        stepped = cover_base ** n
        if stepped - stepped != 0.0 and cover_base - cover_base == 0.0:
            raise float.__pow__(cover_base, n)
        if paid > cover_pp_init() * stepped:
            return m
    return -1


def lapse_rate_base(t):
    """The table annual lapse rate in month t **[std]**, before the crossover stress.

    Read from the cell's own rows of the lapse table, which are keyed by the contractual
    1-based policy year, :func:`policy_year` ``(t)`` on the policy clock; policy years
    beyond the cell's last row take that row, ``Data.lapse_last_year``, as
    :mod:`~.WOL_UK_S`'s ``tbl.index.max()`` does.  Both tables are drafting constructions -
    no public UK whole of life lapse study was retrieved - and on a product with no
    surrender value they are the single largest lever on the liability.

    Zero outside cover, where the month has no policy year: before issue
    :func:`policy_year` is 0 or less, where :mod:`~.WOL_UK_S`'s lookup raised ``KeyError``.
    Inside it, this is the one cell that reads ``Data.lapse_table_array``, at the point's
    cell, :func:`cell_code`, and the policy year, which is 1 or more in cover and at most
    the cell's last, :func:`lapse_last_year`, since every later year is read at it: so
    both ends of the cell's rows hold the key, and no read meets the array's padding.
    """
    if not is_active(t):
        return 0.0
    y = min(policy_year(t), lapse_last_year())
    return float(data.lapse_table_array()[cell_code(), y])           # noqa: F821


def lapse_last_year():
    """The last policy year the lapse table gives the point's cell a rate for.

    ``Data.lapse_last_year`` at the point's cell, :func:`cell_code`: the extent of the
    cell's own rows, which :func:`lapse_rate_base` reads every later policy year at, as
    :mod:`~.WOL_UK_S`'s ``tbl.index.max()`` does on the cell's rows, and which ``Data``
    asks the table's check of before it is read.
    """
    return int(data.lapse_last_year()[cell_code()])                  # noqa: F821


def lapse_rate(t):
    """w(y): the annual lapse rate applying at the end of month t.

    **Zero once premiums have ceased**, from policy month ``cessation_mths()`` on: there is
    nothing left to stop paying, and applying a lapse decrement there silently destroys
    liability - the notes list it as a pitfall.  Otherwise the table rate, optionally
    stressed by ``1 + beta`` past the crossover, which is off in the base run: in a month
    whose premiums paid, :func:`prem_cum_pp`, from the opening state, exceed the cover in
    force.  The bound is :mod:`~.WOL_UK_S`'s, ``min(1.0, w)``, its bound first: a lapse
    rate's bound is no cap on mortality, and :func:`proj_len` holds the stress to a finite
    number, 0 or more, and ``Data`` the table's rates to 0 to 1, so no NaN reaches it.
    Zero outside cover.
    """
    if not is_active(t):
        return 0.0
    if cessation_mths() > 0 and duration_mth(t) >= cessation_mths():
        return 0.0
    w = lapse_rate_base(t)
    if lapse_crossover_beta > 0.0 and prem_cum_pp(t) > cover_pp(t):  # noqa: F821
        w = w * (1.0 + lapse_crossover_beta)                         # noqa: F821
    return min(1.0, w)


def lapse_rate_mth(t):
    """w_m(y) = 1 - (1 - w)^(1/12): the monthly lapse rate **[std]**."""
    return 1.0 - (1.0 - lapse_rate(t)) ** (1.0 / 12.0)


def pols_if(t):
    """l(t): full-cover policies in force at the **start** of month t, the row's weight.

    ``pols_if_at(t, BEF_DECR)``: the count carried in from month t - 1, plus month t's
    new business, before month t's decrements.  On a point issued at ``t = 0`` that is
    exactly :mod:`~.WOL_UK_S`'s ``pols_if``, the notes' in-force probability ``l(t)``, the
    column their worked-example table prints.  It is ``basiclife.BasicTerm_SE``'s
    ``BEF_DECR`` count, not its ``pols_if``.  Paid-up policies are **not** counted here:
    they are a separate strand, :func:`pols_pu`, because their benefit is a reduced
    amount.  Zero outside cover: before issue, and from ``t = proj_len()`` on.
    """
    return pols_if_at(t, BEF_DECR)                                   # noqa: F821


def pols_pu(t):
    """Paid-up policies in force at the start of month t.

    Zero without the pro-rata paid-up variant.  At :func:`t_entry` it is
    :func:`pols_pu_init`, the paid-up policies in force at the valuation date, 0 on a
    point not yet in force, whose policies all start on full cover.  Paid-up policies pay
    no premium, carry no lapse decrement and do not escalate, so they roll forward on
    mortality alone and take conversions in from the full-cover strand: one cell a month
    within a policy year, reading no month before :func:`t_entry`.  Zero outside cover.

    In the first month of a policy year after :func:`t_entry` the strand carried in is the
    year's opening, :func:`pols_pu_py`, the same sum in the same order, bit for bit: the
    recursion blocked by policy year, as :func:`pols_if_at`'s count is.
    """
    if not is_active(t) or not pu_variant():
        return 0.0
    if t == t_entry():
        return pols_pu_init()
    if duration_mth(t) % 12 == 0:
        return pols_pu_py(policy_year(t))
    return pols_pu(t - 1) * (1.0 - mort_rate_mth(t - 1)) + pols_convert(t - 1)


def pols_pu_py(y):
    """The paid-up policies carried into policy year y: the strand policy year y - 1
    closes on.

    The paid-up count's recursion blocked by policy year, as :func:`pols_if_py` blocks the
    full-cover count's: it walks the months of policy year ``y - 1`` on the books in
    ascending order, asking :func:`pols_pu` of each, so that each finds the month before
    cached, and returns the year's last month's survivors and conversions, the sum
    :func:`pols_pu` forms at the next month, in the same order, bit for bit.
    :func:`pols_pu` reads it in the first month of policy year ``y``, in cover and after
    :func:`t_entry`, so ``y`` runs from 2 to 103 at the contract's longest cover, as
    :func:`pols_if_py`'s does; no other cell reads it.
    """
    d = duration_mth_init()
    first = max(t_entry(), 12 * (y - 2) - d)
    last = 12 * (y - 1) - 1 - d
    for s in range(first, last):
        pols_pu(s)
    return pols_pu(last) * (1.0 - mort_rate_mth(last)) + pols_convert(last)


def pu_benefit(t):
    """The aggregate paid-up cover in force at the start of month t.

    Carrying the aggregate benefit alongside the count is what removes the need for a
    per-conversion cohort dimension: the paid-up payout depends on when the policy
    converted, but every paid-up policy thereafter rolls forward on the same survival
    factor, so the sum of their payouts satisfies the same recursion as the count.
    Death outgo on the strand is then ``pu_benefit(t) x q_m(t)``.  At :func:`t_entry` it
    is :func:`pols_pu_init` times :func:`pu_benefit_pp_init`, 0 on a point not yet in
    force.  Zero outside cover.  A summed cover that leaves the floats is refused in the
    month it first does, naming the point, by :func:`pu_benefit_refusal`, which this cell
    calls on that error path alone: it is on a chain, so it formats no message itself.

    In the first month of a policy year after :func:`t_entry` the cover carried in is the
    year's opening, :func:`pu_benefit_py`, the same sum in the same order, bit for bit:
    the recursion blocked by policy year, as :func:`pols_pu`'s is.
    """
    if not is_active(t) or not pu_variant():
        return 0.0
    if t == t_entry():
        v = pols_pu_init() * pu_benefit_pp_init()
    elif duration_mth(t) % 12 == 0:
        v = pu_benefit_py(policy_year(t))
    else:
        v = (pu_benefit(t - 1) * (1.0 - mort_rate_mth(t - 1))
             + pols_convert(t - 1) * benefit_pp(t - 1, PAID_UP))      # noqa: F821
    if not v - v == 0.0:
        return pu_benefit_refusal(t)
    return v


def pu_benefit_py(y):
    """The paid-up cover carried into policy year y: the summed cover policy year y - 1
    closes on.

    The paid-up cover's recursion blocked by policy year, as :func:`pols_pu_py` blocks
    the count's: it walks the months of policy year ``y - 1`` on the books in ascending
    order, asking :func:`pu_benefit` of each, so that each finds the month before cached,
    and returns the year's last month's surviving cover and the cover its conversions
    bring, the sum :func:`pu_benefit` forms at the next month, in the same order, bit for
    bit.  :func:`pu_benefit` reads it in the first month of policy year ``y``, in cover and
    after :func:`t_entry`, so ``y`` runs from 2 to 103 at the contract's longest cover; no
    other cell reads it but :func:`pu_benefit_refusal`, on its error path.
    """
    d = duration_mth_init()
    first = max(t_entry(), 12 * (y - 2) - d)
    last = 12 * (y - 1) - 1 - d
    for s in range(first, last):
        pu_benefit(s)
    return (pu_benefit(last) * (1.0 - mort_rate_mth(last))
            + pols_convert(last) * benefit_pp(last, PAID_UP))         # noqa: F821


def pu_benefit_refusal(t):
    """The refusal of a paid-up cover past the floats in month t, :func:`pu_benefit`'s, in
    a cell of its own.

    :func:`pu_benefit` is a chain, which a compiled run recurses through on the C stack,
    so it calls this cell only where the summed cover has left the floats, as
    :func:`prem_cum_pp` calls :func:`prem_cum_pp_refusal`.  It takes the month alone, sums
    the cover as :func:`pu_benefit` does, from the same cells, the same float, and refuses
    it where it is not a finite number, naming the point, the month and the opening strand,
    in :func:`pu_benefit`'s words; where it is finite, it returns it, as the sample asks for
    it in every month, to type the cell.  0 outside cover and without the variant.
    """
    if not is_active(t) or not pu_variant():
        return 0.0
    if t == t_entry():
        v = pols_pu_init() * pu_benefit_pp_init()
    elif duration_mth(t) % 12 == 0:
        v = pu_benefit_py(policy_year(t))
    else:
        v = (pu_benefit(t - 1) * (1.0 - mort_rate_mth(t - 1))
             + pols_convert(t - 1) * benefit_pp(t - 1, PAID_UP))      # noqa: F821
    if not v - v == 0.0:
        raise ValueError(
            f"point_id {point_id()}: the paid-up cover pu_benefit({t}) is {v}, not a "
            f"finite number, from pols_pu_init {pols_pu_init()} paid-up policies at "
            f"pu_benefit_pp_init {pu_benefit_pp_init()} and the conversions since")
    return v


def pols_all(t):
    """All policies in force at the start of month t: full cover plus paid-up.

    The weight on the maintenance expense, and the count the roll-forward closes on.
    """
    return pols_if(t) + pols_pu(t)


def pols_if_at(t, timing):
    """The number of full-cover policies in force at a point inside month t.

    ``BEF_NB``
        The count carried in from month t - 1, before month t's new business: the
        survivors of month t - 1's deaths and would-be lapses, out of month t - 1's
        ``BEF_DECR`` count.  At :func:`t_entry`, the first month on the books, it is
        :func:`pols_if_init`, the count in force at the valuation date (0 for a point
        issued at or after it), and the recursion reads no earlier month.  Zero outside
        cover, so the survivors of the last month leave as :func:`pols_maturity`.

    ``BEF_DECR``
        ``BEF_NB`` plus :func:`pols_new_biz`: l(t), the count that weights month t,
        which :func:`pols_if` returns.

    ``BEF_LAPSE``
        after deaths, before lapses - the notes' processing order is
        **death before lapse** **[std]**.

    ``AFT_DECR``
        the end-of-month count, the notes' ``l(t+1)``: ``BEF_NB`` at t + 1 exactly, one
        product in one order, and zero from the last month before the limiting age on,
        where the survivors are :func:`pols_maturity`.

    These are int References, 0 to 3, named as :mod:`~.WOL_UK_S`'s strings (the Space
    docstring's *Codes*).  ``BEF_NB`` is the one timing running in force adds, as
    ``basiclife.BasicTerm_SE`` names it; the other three are :mod:`~.WOL_UK_S`'s, and any
    other raises.  ``BEF_NB`` forms month t - 1's ``BEF_DECR`` count itself, as ``BEF_NB``
    plus :func:`pols_new_biz` at t - 1, the same sum in the same order, rather than calling
    for it, so the chain of calls within a policy year is one cell a month.  In the first
    month of a policy year after :func:`t_entry` the count carried in is the year's
    opening, :func:`pols_if_py`, the same product in the same order, bit for bit: the
    recursion blocked by policy year (UKLIB-SEC-PLAN.md K12), so that a cold read runs one
    cell a month back to its year's first month and two cells a year from there, where
    one cell a month back to :func:`t_entry` would run the contract's longest cover, 1,236
    months, on the compiled model's C stack.
    """
    if timing == BEF_NB:                                             # noqa: F821
        if not is_active(t):
            return 0.0
        if t == t_entry():
            return pols_if_init()
        if duration_mth(t) % 12 == 0:
            return pols_if_py(policy_year(t))
        return ((pols_if_at(t - 1, BEF_NB) + pols_new_biz(t - 1))      # noqa: F821
                * (1.0 - mort_rate_mth(t - 1)) * (1.0 - lapse_rate_mth(t - 1)))
    if timing == BEF_DECR:                                           # noqa: F821
        return pols_if_at(t, BEF_NB) + pols_new_biz(t)                 # noqa: F821
    if timing == BEF_LAPSE:                                          # noqa: F821
        if not is_active(t):
            return 0.0
        return pols_if(t) * (1.0 - mort_rate_mth(t))
    if timing == AFT_DECR:                                           # noqa: F821
        if not is_active(t) or duration_mth(t) >= limit_mth() - 1:
            return 0.0
        return pols_if_at(t + 1, BEF_NB)                             # noqa: F821
    raise ValueError("invalid timing")


def pols_if_py(y):
    """The full-cover count carried into policy year y: the survivors of policy year y - 1.

    The count's recursion blocked by policy year, as uslib's and ``ULB_UK_SEC``'s chains
    are (UKLIB-SEC-PLAN.md K12, §6.6, *Record -- M10*): it walks the months of policy year
    ``y - 1`` on the books in ascending order, from the later of :func:`t_entry` and the
    year's first month, asking the count carried into each, ``pols_if_at(s, BEF_NB)``, so
    that each finds the month before cached, and returns the count carried out of the
    year's last month, ``BEF_NB`` plus :func:`pols_new_biz` there, less its deaths and
    would-be lapses: the product ``pols_if_at(t, BEF_NB)`` forms at the next month, in the
    same order, bit for bit.  ``pols_if_at(t, BEF_NB)`` reads it in the first month of
    policy year ``y``, in cover and after :func:`t_entry`, so ``y`` runs from 2 to the
    policy year of the limiting age's last month, 103 at the contract's longest cover,
    issue at ``issue_age_min``, 18, to ``omega_age_max``, 121 (``spec_sec.py``); no other
    cell reads it.
    """
    d = duration_mth_init()
    first = max(t_entry(), 12 * (y - 2) - d)
    last = 12 * (y - 1) - 1 - d
    for s in range(first, last):
        pols_if_at(s, BEF_NB)                                        # noqa: F821
    return ((pols_if_at(last, BEF_NB) + pols_new_biz(last))           # noqa: F821
            * (1.0 - mort_rate_mth(last)) * (1.0 - lapse_rate_mth(last)))


def pols_new_biz(t):
    """The number of policies issued in month t: ``policy_count()`` in the issue month.

    The issue month is the one with ``duration_mth(t) == 0``: ``t = 0`` for a point
    issued at the valuation date, ``t = k`` for one issued ``k`` months later.  A point
    already in force at the valuation date has none.  Every policy issued starts on full
    cover.
    """
    return policy_count() if duration_mth(t) == 0 else 0.0


def pols_death(t):
    """Deaths on full cover at the end of month t, against the start-of-month in-force.

    Zero outside cover, before any rate is read.
    """
    if not is_active(t):
        return 0.0
    return pols_if(t) * mort_rate_mth(t)


def pols_death_pu(t):
    """Deaths on paid-up cover at the end of month t; zero without the pro-rata paid-up value.

    Zero outside cover, before any rate is read.
    """
    if not is_active(t):
        return 0.0
    return pols_pu(t) * mort_rate_mth(t)


def pols_exit(t):
    """Would-be lapses at the end of month t, taken from the survivors of mortality.

    What happens to them depends on :func:`pu_eligible`: they either terminate for
    nothing or convert to paid-up.  Zero outside cover, before any rate is read.
    """
    if not is_active(t):
        return 0.0
    return pols_if_at(t, BEF_LAPSE) * lapse_rate_mth(t)              # noqa: F821


def pols_convert(t):
    """Would-be lapses converted to paid-up at the end of month t.

    All of them once the pro-rata paid-up halfway point is passed **[std]**, none before
    it, and none at all without the variant.  A state change, not a cash flow.  Zero
    outside cover.
    """
    if not is_active(t):
        return 0.0
    return pols_exit(t) if pu_eligible(t) else 0.0


def pols_lapse(t):
    """Lapses that actually terminate the policy at the end of month t.

    **Pays nothing.** There is no surrender value at any duration on either cell, so
    this moves :func:`pols_if` and produces no cash flow whatever - which is the
    arithmetic meaning of a lapse-supported product.  Zero outside cover.
    """
    if not is_active(t):
        return 0.0
    return pols_exit(t) - pols_convert(t)


def pols_maturity(t):
    """Policies still in force when the projection is truncated at the limiting age.

    Not a maturity - whole of life has none - and not a benefit: it pays nothing.  It is
    the truncation residual, non-zero only in the last month before the limiting age,
    ``duration_mth(t) = limit_mth() - 1``, on the policy clock, the frame's last row
    ``t = proj_len() - 1``, and it exists so that the roll-forward closes there.
    :func:`check_truncation` asserts it is negligible, which is the substantive statement:
    a limiting age set too low would drop liability off the end of the projection instead.
    """
    if duration_mth(t) != limit_mth() - 1:
        return 0.0
    return (pols_all(t) - pols_death(t) - pols_death_pu(t) - pols_lapse(t))


def benefit_pp(t, kind):
    """The benefit amount per policy in month t, by kind.

    ``NON_ACC``
        the non-accidental death benefit.  On the O50 cell it is
        ``CumPrem(t)`` inside the moratorium and the cash sum after it; on
        the UW cell it is the sum assured, with the suicide refund handled
        under ``DEATH``.

    ``ACC``
        the accidental death benefit: the full cash sum from day one, and
        ``k_adb`` times it past the moratorium.  On the UW cell there is no
        accidental split, so this is the sum assured.

    ``DEATH``
        the expected benefit per death on the full-cover strand, blending the
        two above by the accidental share on O50, and the sum assured with
        the suicide refund by the suicide share inside the first twelve
        policy months (``duration_mth(t) < suicide_mths``) on UW.  This is what
        :func:`claims` multiplies by.

    ``PAID_UP``
        the pro-rata paid-up payout for a policy converting in month t,
        ``SA(t) x N_paid / N_expected``.  Zero without the variant.

    These are int References, named as :mod:`~.WOL_UK_S`'s strings, ``DEATH`` 0, the one
    code it shares with :func:`claims`, then ``NON_ACC`` 1, ``ACC`` 2 and ``PAID_UP`` 3 (the
    Space docstring's *Codes*), and any other raises.  The cell is :func:`cell_code`,
    compared as :mod:`~.WOL_UK_S` compares the text.

    The moratorium and the suicide window are policy months, wherever they fall in the
    frame, and their refunds read the premiums paid from the opening state.  Each kind is
    zero outside cover.  A benefit the cover and premiums paid make that leaves the
    floats, a multiple, a blend or a share of them, raises ``ValueError`` in the month it
    first does, naming the point and the kind by its code.
    """
    if kind == NON_ACC:                                              # noqa: F821
        if not is_active(t):
            return 0.0
        if cell_code() == O50 and in_moratorium(t):                  # noqa: F821
            return prem_cum_pp(t)
        return cover_pp(t)
    if kind == ACC:                                                  # noqa: F821
        if not is_active(t):
            return 0.0
        if cell_code() != O50 or in_moratorium(t):                   # noqa: F821
            return cover_pp(t)
        v = adb_multiplier() * cover_pp(t)
    elif kind == DEATH:                                              # noqa: F821
        if not is_active(t):
            return 0.0
        if cell_code() == O50:                                       # noqa: F821
            v = ((1.0 - acc_share) * benefit_pp(t, NON_ACC)          # noqa: F821
                 + acc_share * benefit_pp(t, ACC))                   # noqa: F821
        elif duration_mth(t) < suicide_mths:                         # noqa: F821
            v = ((1.0 - suicide_share) * cover_pp(t)                 # noqa: F821
                 + suicide_share * prem_cum_pp(t))                   # noqa: F821
        else:
            return cover_pp(t)
    elif kind == PAID_UP:                                            # noqa: F821
        if not is_active(t) or not pu_variant():
            return 0.0
        v = cover_pp(t) * payments_made(t) / payments_expected()
    else:
        raise ValueError("invalid kind")
    if not v - v == 0.0:
        raise ValueError(
            f"point_id {point_id()}: the benefit benefit_pp({t}, {kind}) is {v}, not a "  # noqa: F821
            f"finite number, from the cover cover_pp({t}) {cover_pp(t)}")
    return v


def premiums(t):
    """E[premium](t): premium income at the beginning of month t, an inflow.

    Carried on the full-cover strand only: paid-up policies pay nothing, and neither do
    over-50s policies past cessation, where :func:`premium_pp` is already zero.  Income
    that leaves the floats raises ``ValueError`` in the month it first does, naming the
    point.
    """
    v = premium_pp(t) * pols_if(t)
    if not v - v == 0.0:
        raise ValueError(
            f"point_id {point_id()}: the premiums premiums({t}) are {v}, not a finite "  # noqa: F821
            f"number, from premium_pp({t}) {premium_pp(t)} on pols_if({t}) {pols_if(t)} "
            f"policies")
    return v


def claims(t, kind):
    """Death outgo in month t, by kind, and the three kinds' total.

    ``DEATH``
        outgo on the full-cover strand, ``deaths x benefit_pp(t, DEATH)``.

    ``DEATH_PU``
        outgo on the paid-up strand, ``pu_benefit(t) x q_m(t)`` - the
        aggregate paid-up cover times the monthly mortality rate, which is
        why the strand carries a benefit total as well as a count.

    ``LAPSE``
        zero, always.  There is no surrender value at any time on either
        cell; the kind exists so the zero is stated rather than inferred.

    ``ALL``
        the three kinds' total, :mod:`~.WOL_UK_S`'s ``claims(t)``, whose ``kind=None``
        sums the three with Python's ``sum``, which compiles to no C.  It is written left to
        right from ``0.0``, ``0.0 + DEATH + DEATH_PU + LAPSE``, which is ``sum``'s float
        wherever at most two kinds are non-zero in a month, and here at most two are, the
        lapse kind being 0 by the product's design: ``sum`` carries the rounding error of
        each addition, Neumaier's way, and adds it back once at the end, and the error of a
        single addition, added back, rounds to the sum it came from; and ``0.0 +`` the first
        kind is ``sum``'s start, the int 0, which turns a negative zero to ``0.0``.  So the
        total is :mod:`~.WOL_UK_S`'s float in every month, and a test holds it so by its
        bits.

    These are int References, ``DEATH`` 0, the one code this family shares with
    :func:`benefit_pp`'s, ``DEATH_PU`` 1, ``LAPSE`` 2 and ``ALL`` 3, named as
    :mod:`~.WOL_UK_S`'s strings (the Space docstring's *Codes*), and any other raises.  The
    total is asked for first, as :mod:`~.WOL_UK_S` asks whether ``kind`` is ``None``, and
    reads its kinds in :mod:`~.WOL_UK_S`'s order.

    Each kind is zero outside cover, before any rate is read.  Outgo that leaves the
    floats, of a kind or in total, raises ``ValueError`` in the month it first does, naming
    the point and the kind by its code.
    """
    if kind == ALL:                                                  # noqa: F821
        v = 0.0 + claims(t, DEATH) + claims(t, DEATH_PU) + claims(t, LAPSE)  # noqa: F821
    elif kind == DEATH:                                              # noqa: F821
        if not is_active(t):
            return 0.0
        v = pols_death(t) * benefit_pp(t, DEATH)                     # noqa: F821
    elif kind == DEATH_PU:                                           # noqa: F821
        if not is_active(t):
            return 0.0
        v = pu_benefit(t) * mort_rate_mth(t)
    elif kind == LAPSE:                                              # noqa: F821
        return 0.0
    else:
        raise ValueError("invalid kind")
    if not v - v == 0.0:
        raise ValueError(
            f"point_id {point_id()}: the claims claims({t}, {kind}) are {v}, not a finite "
            f"number, from pols_death({t}) {pols_death(t)} deaths on full cover at "
            f"benefit_pp({t}, DEATH) {benefit_pp(t, DEATH)}, and pu_benefit({t}) "  # noqa: F821
            f"{pu_benefit(t)} of paid-up cover")
    return v


def expense_acq_pp():
    """The acquisition expense per policy at issue **[std]**: £150 on O50, £300 on UW.

    The cell is :func:`cell_code`, compared as :mod:`~.WOL_UK_S` compares the text.
    """
    return expense_acq_o50 if cell_code() == O50 else expense_acq_uw  # noqa: F821


def expense_maint_pp():
    """The annual maintenance expense per policy **[std]**: £30 on O50, £50 on UW.

    Premiums are level and small - £30 a month on the anchor cell - while this inflates,
    so the expense margin erodes mechanically over a twenty-year-plus horizon.  A
    per-policy expense error compounds accordingly.  The cell is :func:`cell_code`.
    """
    return expense_maint_o50 if cell_code() == O50 else expense_maint_uw  # noqa: F821


def inflation_factor(t):
    """The expense inflation factor in month t, ``(1 + pi)^(t // 12)`` **[std]**.

    On the **valuation** clock: ``t`` counts months from the valuation date, so the
    maintenance charge it inflates is in valuation-date pounds, whatever the policy's
    age, and every point of a block inflates alike, stepping on each anniversary of the
    valuation date.  :mod:`~.WOL_UK_S` inflates from issue, ``(1 + pi)^(y - 1)``, as the
    notes write it; on a point issued at ``t = 0`` the two are the same.  The acquisition
    expense is not inflated (see :func:`expenses`).  :func:`proj_len` holds
    ``inflation_rate`` to a finite number, -1 or more, so the factor is a number, 0 or
    more.

    The exponent is a whole number of years, 0 or more, so the power is real whatever the
    base.  Within the longest frame and the month after it, 113 years from the valuation
    date, it passes the largest float only where ``inflation_rate`` is above about 533 a
    year, which no product reaches.  Python's
    float power raises ``OverflowError`` past the largest float, where C's ``pow`` gives an
    infinity, so where the power is infinite from a finite base the cell calls Python's
    own, which raises the platform's message in the compiled model as in modelx
    (USLIB-SEC-PLAN.md, *Record -- M22*); modelx never reaches the call, its own power
    raising first.
    """
    base = 1.0 + inflation_rate                                      # noqa: F821
    n = t // 12
    factor = base ** n
    if factor - factor != 0.0 and base - base == 0.0:
        raise float.__pow__(base, n)
    return factor


def expenses(t):
    """Acquisition and maintenance expense in month t **[std]**.

    The acquisition charge falls once per policy issued, ``expense_acq_pp() *
    pols_new_biz(t)``: in the issue month, never for a point already in force at the
    valuation date, and not inflated, as in ``basiclife.BasicTerm_SE``.
    :mod:`~.WOL_UK_S` charges it on the count at ``t = 0``, which on a point issued then is
    the count issued.  Maintenance is carried on :func:`pols_all`, so a paid-up policy still
    costs money to administer even though it pays no premium - which is part of why the
    pro-rata paid-up variant is expensive.  Expenses that leave the floats raise
    ``ValueError`` in the month they first do, naming the point and the References that
    make them: an expense and an inflation rate each in its domain can, as an expense of
    1.7e308 inflated at 100% a year does at ``t = 48``.
    """
    acq = expense_acq_pp() * pols_new_biz(t)
    v = acq + expense_maint_pp() / 12.0 * inflation_factor(t) * pols_all(t)
    if not v - v == 0.0:
        raise ValueError(
            f"point_id {point_id()}: the expenses expenses({t}) are {v}, not a finite "
            f"number, from expense_acq_{'o50' if cell_code() == O50 else 'uw'} "  # noqa: F821
            f"{expense_acq_pp()}, expense_maint_{'o50' if cell_code() == O50 else 'uw'} "  # noqa: F821
            f"{expense_maint_pp()} and inflation_rate {float(inflation_rate)}, on "  # noqa: F821
            f"pols_all({t}) {pols_all(t)} policies")
    return v


def commissions(t):
    """Initial commission in month t **[std]**: a share of the first year's premiums.

    Policy year 1 on the policy clock, ``duration_mth(t) < 12``, so commission continues
    on a point valued in its first policy year, on the premiums it pays in the months of
    that year left after the valuation date, and is never paid again on a point valued
    later.  The existence of commission is sourced - an intermediary is "paid by
    commission as a percentage of total annual premium" - and the level is a
    standardization.  Zero outside cover.  A commission that leaves the floats raises
    ``ValueError`` in the month it first does, naming the point and ``comm_init_rate``.
    """
    if not is_active(t) or policy_year(t) > 1:
        return 0.0
    v = comm_init_rate * premiums(t)                                 # noqa: F821
    if not v - v == 0.0:
        raise ValueError(
            f"point_id {point_id()}: the commission commissions({t}) is {v}, not a finite "  # noqa: F821
            f"number, from comm_init_rate {float(comm_init_rate)} on premiums({t}) "  # noqa: F821
            f"{premiums(t)}")
    return v


def net_cf(t):
    """CF(t): the net cash flow of month t, **income positive**.

    Premiums less death outgo, expenses and commission.  The notes' own sign and the
    library-wide one, so there is no outgo-positive ``liability_cf`` companion.

    Note that the notes' worked-example table prints premium income and death outgo as
    separate positive columns and omits expenses "for clarity", so ``net_cf`` will not
    equal any column of that table.  Lapse contributes nothing at all: it moves
    :func:`pols_if` and pays no cash.  Each flow is a finite number, its cell refusing one
    that is not, but their sum can leave the floats, which raises ``ValueError`` here,
    naming the point and the flows.  The death outgo is the claims total,
    ``claims(t, ALL)``, :mod:`~.WOL_UK_S`'s ``claims(t)``.
    """
    v = premiums(t) - claims(t, ALL) - expenses(t) - commissions(t)  # noqa: F821
    if not v - v == 0.0:
        raise ValueError(
            f"point_id {point_id()}: the net cash flow net_cf({t}) is {v}, not a finite "
            f"number, from premiums {premiums(t)}, claims {claims(t, ALL)}, expenses "  # noqa: F821
            f"{expenses(t)} and commissions {commissions(t)}")
    return v


def check_pols_roll_fwd_resid(t):
    """The in-force roll-forward residual in month t; zero everywhere.

    ``pols_all(t) - pols_all(t+1)``, plus the new business of month t + 1, which is no
    part of month t's movement, less deaths from both strands, lapses that actually
    terminate, and the truncation residual in the last month.  Conversions to paid-up
    are absent because they move policies *between* strands rather than out of the
    population - which is the point of running the check on the total.
    """
    return (pols_all(t) - pols_all(t + 1) + pols_new_biz(t + 1)
            - pols_death(t) - pols_death_pu(t) - pols_lapse(t)
            - pols_maturity(t))


def check_pols_roll_fwd():
    """True when the in-force roll-forward closes in every month of the frame.

    The library-wide form of a roll-forward check: no argument, one bool over all t, so
    one test can call it across every model.  :func:`check_pols_roll_fwd_resid` gives
    the signed residual of the month that failed.  The tolerance scales with the
    policies on the books, ``policy_count() + pols_pu_init()``, on both strands, in force
    at the valuation date or issued after it, since the residual accumulates rounding on
    that many policies.

    Written as a loop, the frame first, that returns False at the first month whose
    residual is not within the tolerance, a NaN among them, where :mod:`~.WOL_UK_S` writes
    ``all()`` over a generator: the same verdict at the same month, which compiles to C
    rather than to a Python closure inside the cell.
    """
    end = proj_len()
    tol = 1e-10 * max(policy_count() + pols_pu_init(), 1.0)
    for t in range(end):
        if not abs(check_pols_roll_fwd_resid(t)) <= tol:
            return False
    return True


def check_truncation():
    """True when the population left at the limiting age is negligible.

    Whole of life has no maturity date, so the projection ends at a limiting age rather
    than at a contractual one, and anything still in force there is liability dropped
    off the end.  The shipped mortality tables reach 1 well before ``omega_age``, so the
    residual should be vanishing; if it is not, the limiting age is too low and the
    model is understating the tail rather than merely rounding it.  The tolerance scales
    with the policies on the books, ``policy_count() + pols_pu_init()``.  Mortality
    improvement can carry survivors to the limiting age: at 1% a year the underwritten
    points hold about 7e-6 of a policy there, and the check gives way.
    """
    return pols_maturity(proj_len() - 1) <= 1e-9 * max(policy_count() + pols_pu_init(),
                                                       1.0)


def result_cf():
    """Result table of cashflows, one row per month ``t = 0 .. proj_len() - 1``.

    Row 0 is the valuation month for every model point, so the frames of a block line up
    and sum row by row.  A point issued after the valuation date has zeros until its issue
    month.  ``pols_if`` is the full-cover count at the start of the month, which is the
    weight on premium income and on full-cover death outgo; ``pols_pu`` is the paid-up
    strand, empty on every model point without the pro-rata paid-up variant.  The columns
    are :mod:`~.WOL_UK_S`'s.  ``claims_lapse`` is a column of zeros by product design -
    there is no surrender value - and is published rather than dropped.
    """
    ts = list(range(proj_len()))
    return pd.DataFrame(                                             # noqa: F821
        {
            "pols_if": [pols_if(t) for t in ts],
            "pols_pu": [pols_pu(t) for t in ts],
            "premiums": [premiums(t) for t in ts],
            "claims_death": [claims(t, DEATH) for t in ts],            # noqa: F821
            "claims_death_pu": [claims(t, DEATH_PU) for t in ts],      # noqa: F821
            "claims_lapse": [claims(t, LAPSE) for t in ts],            # noqa: F821
            "expenses": [expenses(t) for t in ts],
            "commissions": [commissions(t) for t in ts],
            "net_cf": [net_cf(t) for t in ts],
        },
        index=pd.Index(ts, name="t"),                                # noqa: F821
    )


def result_pols():
    """Result table of policy counts, benefits and rates, one row per month t.

    The same rows as :func:`result_cf`, ``t = 0 .. proj_len() - 1``.  First the counts
    :func:`result_cf` weights its rows by, and how they move, as
    ``basiclife.BasicTerm_SE``'s ``result_pols`` sets them out, on both strands:
    ``pols_if``, the full-cover count of month t; ``pols_new_biz``, the part of it issued
    in month t; ``pols_pu``, the paid-up strand; then month t's deaths on each strand, and
    its would-be lapses, terminating or converted to paid-up, in processing order, and the
    truncation residual of the last month.  Row by row, ``pols_if`` at ``t + 1`` is
    ``pols_if`` less its deaths, lapses and conversions of month t, plus the new business
    of month ``t + 1``, and ``pols_pu`` at ``t + 1`` is ``pols_pu`` less its deaths plus the
    conversions.  Then :mod:`~.WOL_UK_S`'s other five columns: the premiums paid, the
    cover, the benefit per death and the annual mortality and lapse rates, which are 0
    outside cover, where the model reads no rate.
    """
    ts = list(range(proj_len()))
    return pd.DataFrame(                                             # noqa: F821
        {
            "pols_if": [pols_if(t) for t in ts],
            "pols_new_biz": [pols_new_biz(t) for t in ts],
            "pols_pu": [pols_pu(t) for t in ts],
            "pols_death": [pols_death(t) for t in ts],
            "pols_death_pu": [pols_death_pu(t) for t in ts],
            "pols_lapse": [pols_lapse(t) for t in ts],
            "pols_convert": [pols_convert(t) for t in ts],
            "pols_maturity": [pols_maturity(t) for t in ts],
            "prem_cum_pp": [prem_cum_pp(t) for t in ts],
            "cover_pp": [cover_pp(t) for t in ts],
            "benefit_death_pp": [benefit_pp(t, DEATH) for t in ts],    # noqa: F821
            "mort_rate": [mort_rate(t) for t in ts],
            "lapse_rate": [lapse_rate(t) for t in ts],
        },
        index=pd.Index(ts, name="t"),                                # noqa: F821
    )


# ---------------------------------------------------------------------------
# References

data = ("Interface", ("..", "Data"), "auto")

idx = 0

BEF_NB = 0

BEF_DECR = 1

BEF_LAPSE = 2

AFT_DECR = 3

DEATH = 0

NON_ACC = 1

ACC = 2

PAID_UP = 3

DEATH_PU = 1

LAPSE = 2

ALL = 3

O50 = 0

UW = 1

LEVEL = 0

FIXED_5PCT = 1

RPI = 2

issue_age_min = 18

omega_age = 120

omega_age_max = 121

mort_loading_o50 = 1.2

mort_loading_uw = 1.0

mort_improvement = 0.0

acc_share = 0.03

suicide_share = 0.01

suicide_mths = 12

rpi_rate = 0.03

esc_fixed_cover = 0.05

esc_fixed_prem = 0.1

esc_rpi_cover_cap = 0.1

esc_rpi_prem_mult = 1.5

esc_rpi_prem_cap = 0.15

esc_take_up = 1.0

lapse_crossover_beta = 0.0

expense_acq_o50 = 150.0

expense_acq_uw = 300.0

expense_maint_o50 = 30.0

expense_maint_uw = 50.0

inflation_rate = 0.03

comm_init_rate = 0.25

pd = ("Module", "pandas")
