# modelx: pseudo-python
# This file is part of a modelx model.
# It can be imported as a Python module, but functions defined herein
# are model formulas and may not be executable as standard Python.

"""The by-contract projection of the :mod:`~.PA_UK_SEC` model.

The Space is parameterized by ``idx``, the position of a model point in the table and in
every :mod:`~.PA_UK_SEC.Data` vector, as ``basiclife.BasicTerm_SC`` is: ``Projection[10]``
is an ItemSpace projecting the table's eleventh row, model point 11, the worked example in
payment 17 months at the valuation date, its annuitant dead since policy month 16, and
:func:`point_id` is its label::

    >>> Projection[10].result_cf()         # one row per month from the valuation date
    >>> Projection[10].result_pols()       # the counts and survival behind it
    >>> Projection[10].point_id()          # 11, the row's point_id
    >>> Projection.idx = 1                 # or switch the default, before it computes

Switch the default, or set any Reference, before the model computes anything. Compiled, no
cache is ever cleared: set ``idx``, like every Reference, on a model just imported, before
anything is computed, or project through ``Projection[i]``. modelx recomputes what a
Reference reaches when it is set; a compiled ItemSpace takes the References when it is
made and keeps every value it has computed until it is deleted, and the base
``Projection`` and ``Data`` keep theirs for good. And it holds each Reference as a C
variable of its shipped value's type: a float set on an int Reference, ``omega_age``,
``issue_age_min``, ``mort_table_year``, ``improve_flat_age`` or ``improve_taper_age``,
truncates toward zero, and an int set on a float Reference reads as a float
(``products/pension_annuity/model-sec.md``).

Any ``idx`` makes an ItemSpace, and none is refused here. ``Projection[-1]`` reads every
vector at its last element, as numpy and a compiled memoryview both do, so it is the
table's last point, under that point's own :func:`point_id`; an ``idx`` past the last
row raises ``IndexError`` at its first read of a vector, which modelx reports inside its
``FormulaError``.

This is :mod:`~.PA_UK_S` taught to run in force at a valuation date, as lifelib's
``basiclife.BasicTerm_SE`` extends ``basiclife.BasicTerm_S``, on the payout chassis of
``SPIA_US_SEC``, and then made to compile, as ``basiclife.BasicTerm_SC`` is made from
``basiclife.BasicTerm_S``. A formula of :mod:`~.PA_UK_S` is rewritten where it depends on
where the projection starts, where it must answer for a month outside the frame, where it
passed a policy month as ``t`` or read history that a Reference cannot give, or where it
branched on text; every other formula is :mod:`~.PA_UK_S`'s own, the cap on mortality,
``min(q, 1.0)``, among them. ``products/pension_annuity/model-sec.md`` lists the rewritten
cells with the reason for each. Making it compile changed how each cell reads its inputs
and spells its codes, and how three chains reach back in time, and no number: every model
point attribute a projection cell uses is read as a number from a ``Data`` vector, each
text column it branches on as ``Data``'s decoded flags, the mortality table as an array by
sex and age, every timing and kind as an int code (*Codes*, below), :mod:`~.PA_UK_S`'s
``claims(t, kind=None)`` total as ``claims(t, ALL)``, and survival and the two payments to
date blocked by policy year (*Chains blocked by policy year*, below).

.. rubric:: Input data

Inputs are **external files**: plain CSVs living in the model folder's parent
directory, ``products/pension_annuity/``, read at run time rather than stored inside
the model. The model folder therefore holds nothing but formulas — no ``_data/``, no
IOSpec, no embedded values — so a diff of the model shows logic changes only, and an
input can be edited or swapped without rewriting the model. This follows
``annuallife.TradLife_A``; contrast ``basiclife.BasicTerm_S``, which keeps its inputs
*inside* the model through modelx's IOSpec machinery.

The consequence worth knowing: **the model is not portable on its own.** Copying the
``PA_UK_SEC`` folder without its parent's CSVs produces a model that reads and then fails
on first evaluation.

The mortality table is the file :mod:`~.PA_UK_S` reads, read in place; the model point
table is this model's own. Each table has a filename Reference and a reader Cells, both on
:mod:`~.PA_UK_SEC.Data`, reached here through the ``data`` Reference:

======================  ==============================  ==========================
Reference               Cells                           File
======================  ==============================  ==========================
model_point_file        data.model_point_table()        model_point_table_sec.csv
mort_table_file         data.mort_table()               mort_table.csv
======================  ==============================  ==========================

.. rubric:: Two clocks

``t`` counts months from the **valuation date**, 0-based, the clock
``basiclife.BasicTerm_SE`` runs on: ``t = 0`` is the valuation month for every model
point, however long the annuity has been in payment, month ``t`` runs from time ``t`` to
time ``t + 1``, and the frame is ``t = 0 .. proj_len() - 1``, where :func:`proj_len`
counts the months from the valuation date to the stop rule. Row ``t`` is the same month
for every point, so the frames of a block line up and sum row by row. Five cells are
indexed by a **time point** on this clock rather than by a month: ``lives_if(t, life)``
and ``lives_if_last(t)``, survival *at* time ``t``; ``cum_annuity_all(t)``, the expected
payments made by time ``t``; ``vp_balance(t)``, the value-protection balance there; and
``check_lives_roll_fwd_resid(t)``. Time ``t`` is the start of month ``t``, so month ``t``
opens at time ``t`` and closes at time ``t + 1``, which is why the death density of month
``t`` is ``l(t) - l(t + 1)`` and the arrears survival point is ``t + 1``, as in
:mod:`~.PA_UK_S`.

``duration_mth(t)`` counts **policy months**, the months elapsed from the annuity start
date at the start of month ``t``: ``duration_mth(t) = duration_mth_init() + t``, where
:func:`duration_mth_init` is read from the model point — positive for an annuity already
in payment at the valuation date, 0 for one starting at it, ``-k`` for one starting ``k``
months later, at most ten years later. Everything contractual reads it: the completed
policy years ``duration(t) = duration_mth(t) // 12``, the 1-based
``policy_year(t) = duration(t) + 1``, the attained ages ``age(t, life)``, the calendar
year, and through them the payment months, the escalation anniversaries, the guarantee
period, the overlap gate and the mortality table. A cell keyed directly by this clock
takes ``k``, never ``t``: :func:`is_payment_pm` and :func:`annuity_pp_pm` are keyed by the
policy month ``k``, and the annuitant's payments to date, ``cum_annuity_pp(k,
ANNUITANT)``, by the time point ``k`` months after the start date, so that the notes'
``G(16) = 6,790.50`` reads unchanged. The policy year is keyed ``y`` and an escalation
anniversary ``a``, as in :mod:`~.PA_UK_S`, both counted from the start date.

The **stop rule** ends every frame where it ends :mod:`~.PA_UK_S`'s: :func:`stop_mth` is
:mod:`~.PA_UK_S`'s frame length from the start date, the age stop on the youngest covered
life or the end of the guarantee if that is later, and :func:`is_active` is
``0 <= duration_mth(t) < stop_mth()``. A contract's own end, the last death or the last
guaranteed instalment, is a probability or a floor reaching zero inside the frame, which
runs on with zeros, as :mod:`~.PA_UK_S`'s does.

Two inputs, and their clocks. Expense inflation reads the **valuation** clock,
``inflation_factor(t) = (1 + inflation_rate) ** (t // 12)``, :mod:`~.PA_UK_S`'s annual
steps moved onto ``t``, so that the maintenance charge is in valuation-date pounds for
every point alike. Mortality improvement stays on the **policy** clock, because it is
already calendar-dated: its exponent is ``calendar_year(t) - mort_table_year``, and
``calendar_year(t) = start_year() + duration(t)`` is the calendar year the contract
reaches whatever the valuation date, so a contract in payment reads the improvement of
its own calendar years and nothing is re-based. The RPI assumption, ``rpi_rate``, is one
flat rate, the same on either clock: the RPI from the valuation date on. The increases a
contract has already been given, and the ratchet's state, are history, carried in its
opening state (below), not rebuilt from today's rate.

On a point whose start date is the valuation date the two clocks coincide and this model
computes what :mod:`~.PA_UK_S` computes: every cell the two share agrees at every
argument :mod:`~.PA_UK_S` evaluates in its sweep, but for three whose meaning changed,
``pols_if_init``, now the count already in payment at the valuation date,
``model_point``, a row of another table, and ``result_pols``, which gains the month's new
business. That is how the worked example carries over, and
``tests/test_model_conventions_uk.py`` asserts it cell by cell.

.. rubric:: Counts

The count on the books is the number of contracts the point stands for,
:func:`policy_count`, from the start date to the stop rule. Mortality decrements each
life's survival, :func:`lives_if`, never the count: the two lives are independent, so their
two probabilities are the whole survival state, and every cash flow is the count times a
per-contract amount weighted by survival, as :mod:`~.PA_UK_S` weights every flow by its
constant ``pols_if_init``. So ``pols_if_at(t, BEF_NB)`` is :func:`pols_if_init`, the count
already in payment, at :func:`t_entry`, the first month on the books, the whole count after
it, and 0 outside the frame; and ``pols_if_at(t, BEF_DECR)`` adds :func:`pols_new_biz`,
the annuities starting in month ``t``. The ``BEF_DECR`` count weights every cash flow of
row ``t``. A contract in payment at the valuation date opens with its ``policy_count``; one
starting at or after it opens with none, and takes its ``policy_count`` as new business in
the month of its start date, ``duration_mth(t) = 0``. New business brings no premium and
no acquisition cost: the purchase price is a pricing input, as in :mod:`~.PA_UK_S`.

:func:`pols_if` keeps :mod:`~.PA_UK_S`'s definition, the notes' obligation measure
``IF(t)``, on that count: the contracts with a payment obligation still open at the end of
month ``t``, which carries the maintenance expense. It is a closing measure, not the count
before decrements: on the twins of :mod:`~.PA_UK_S`'s points 2, 6 and 7, ``pols_if(0)`` is
0.99999965 against a count of 1.0, as in :mod:`~.PA_UK_S`, and the registry marks the model
``closing_pols_if`` for that reason. There is no lapse decrement, and no ``pols_lapse``.

.. rubric:: The opening state

A contract in payment at the valuation date carries what its count and its policy clock
do not say, each per contract and measured at the valuation instant, the start of month 0,
before any month-0 event:

``lives_if_init_1``, ``lives_if_init_2``
    each covered life's probability of being alive at the valuation date,
    :func:`lives_if_init`. On a real record it is 1 or 0, and a joint contract may carry
    one life already dead; on a point restated from :mod:`~.PA_UK_S` at its month ``d`` it
    is :mod:`~.PA_UK_S`'s ``lives_if(d, life)``, a probability. Life 2 is 0 on a
    single-life contract.
``cum_annuity_all_init``
    the payments made to date on every stream, :func:`cum_annuity_all_init`: what was paid
    on a record, an expectation on a restated point, which last-survivor value protection
    nets against and :func:`result_pols` publishes. It is path-dependent.
``annual_income_init``
    on RPI-linked escalation only (``lpi5``, ``rpi_catchup``): the annualized income of
    the policy year under way, taken before any month-0 anniversary, so that an
    anniversary falling in month 0 escalates at the valuation date's ``rpi_rate``. The
    increases already given are history, which no flat rate re-derives.
``rpi_peak_init``
    on ``rpi_catchup`` only: the ratchet's running peak of the reference index, relative
    to the latest index, the one of the anniversary that opened the year under way, so 1
    while the index has never fallen and above 1 while it is below its peak.
``cum_annuity_pp_init``
    on RPI-linked escalation with value protection on the first death only: the
    as-if-alive annuitant instalments to date, which the first-death balance nets against.

On level and fixed escalation the income of the year under way and the annuitant's
payments to date are deterministic schedules of the contract, and are re-derived from it,
each by one loop at the valuation date's key, bit for bit with :mod:`~.PA_UK_S`
(:func:`annual_income_init`, :func:`cum_annuity_pp`). At the start date each covered life
is 1, the payments 0, the income the first year's and the peak 1, so a point starting at
or after the valuation date carries those values. :mod:`~.PA_UK_S`'s scenario death
months stay policy months, and ``Data`` checks each life's opening status against them.
Nothing else carries a path: the guarantee months left, the months since a payment and
the next payment month follow from ``duration_mth``.

.. rubric:: Naming

Cells names follow lifelib's ``basiclife.BasicTerm_S`` and ``savings.CashValue_SE``
wherever those models have an analogue, and follow ``SPIA_US_SEC`` — the library's U.S.
payout chassis — wherever the two products share machinery, so that the same concept has
the same name on both sides of the Atlantic. What running in force adds is named as
``basiclife.BasicTerm_SE`` names it: ``duration_mth`` read from the model point,
``policy_count``, ``pols_new_biz``, ``pols_if_at`` with its ``BEF_NB`` and
``BEF_DECR`` timings, ``is_active`` and ``result_pols``. ``duration_mth_init``, the
policy months completed at the valuation date, takes ``UL_US_S``'s name, and each
opening-state column is ``<cell>_init``, the cell it opens with ``_init`` added.
``t_entry`` and ``stop_mth`` are the SEC family's own. A cell keyed by policy month carries
``_pm``, a table reader keyed by attained age ``_at``, a chain's opening of a policy year
``_py``, as ``ULB_UK_SEC``'s, and a refusal moved off a chain ``_refusal``. The ``is_*``
decodes turn the model point's text columns into the flags the projection branches on,
each reading and validating its column as :mod:`~.PA_UK_S`'s label accessor does, so that
no other projection cell compares text and none calls a label accessor
(``payment_timing``, ``escalation_type``, ``vp_basis``, ``mort_basis``, ``sex``), which is
left to reporting.
The technical notes use compact actuarial symbols instead. The mapping is:

=========================  ==============================  ==========================
Notes symbol               Cells                           Meaning
=========================  ==============================  ==========================
t                          (the cells argument)            Month from the valuation date
k                          (the cells argument)            Policy month or time point
a                          (the cells argument)            Anniversary count, from start
y = duration + 1           policy_year(t)                  Policy year containing month t
(none)                     duration(t)                     Completed policy years, y - 1
(none)                     duration_mth(t)                 Policy months at month t
(none)                     duration_mth_init()             Policy months at t = 0
(none)                     t_entry()                       First month on the books
(stopping rule)            stop_mth()                      Policy month the frame stops
(none)                     is_active(t)                    Month t is in the frame
(none)                     policy_year_init()              Policy year under way at t = 0
P                          purchase_price()                Purchase price
x_a, x_d                   age_at_entry(life)              Entry ages (ALB), life 1 or 2
(none)                     age(t, life)                    Attained age (ALB)
(none)                     sex(life)                       Sex of each covered life
(none)                     mort_schedule(life)             Its row of the table, by sex
theta_a, theta_d           rating_factor(life)             Enhanced/impaired multiplier
delta                      dependant_pct()                 Dependant's percentage
(dependant_present)        is_joint()                      Contract covers a dependant
overlap                    overlap()                       Dependant runs during guarantee
A(1)                       annual_income_first()           Starting annualized income
A(y0)                      annual_income_init()            Income of the year under way
A(y)                       annual_income(y)                Annualized income in year y
(none)                     annual_income_refusal(y)        Its refusal past the floats
g                          escalation_rate()               Fixed escalation rate
escalation_type            escalation_type()               level / fixed / rpi_catchup / lpi5
(none)                     is_level()                      escalation_type decoded: level
(none)                     is_fixed()                      escalation_type decoded: fixed
(none)                     is_lpi5()                       escalation_type decoded: lpi5
(none)                     is_rpi_catchup()                escalation_type decoded: rpi_catchup
I(a)                       rpi_index(a)                    RPI level at anniversary a, relative
peak(a)                    rpi_peak(a)                     Running peak of I through a
peak(a0)                   rpi_peak_init()                 The peak at t = 0, relative
m                          payment_freq()                  Payments per year
timing                     payment_timing()                arrears or advance
(none)                     is_arrears()                    timing decoded: arrears or not
T                          is_payment_mth(t)               Month t is a payment date
(T by policy month)        is_payment_pm(k)                Policy month k is a payment date
s(t)                       payment_surv_mth(t)             Time point survival is measured at
inst(t)                    annuity_pp(t)                   Scheduled instalment
(inst by policy month)     annuity_pp_pm(k)                The same, in policy month k
n                          guarantee_mths()                Guarantee period in months
C(t)                       certain_floor(t)                Floor 1{duration_mth(t) < n}
l_a(t), l_d(t)             lives_if(t, life)               Survival probability to time t
(l at a year's start)      lives_if_py(y, life)            Survival opening policy year y
(l at t_entry)             lives_if_init(life)             Survival at t = 0, or 1 later
d_a(t), d_d(t)             lives_death(t, life)            Death density of month t
d_last(t)                  lives_death_last(t)             Last-death density of month t
(none)                     lives_if_last(t)                At least one covered life alive
max(C, l_a)                payment_factor(t)               Annuitant payment factor
(none)                     payment_factor_life(t)          l_a alone, before the floor
w(t)                       overlap_gate(t)                 Dependant-stream availability
delta(1-l_a)l_d w          dependant_factor(t)             Dependant payment factor
G(k)                       cum_annuity_pp(k, kind)         Instalments to policy time k
(G at a year's start)      cum_annuity_pp_py(y)            G opening policy year y
(G at t = 0)               cum_annuity_pp_init()           Annuitant's paid at t = 0
(G, kind ALL)              cum_annuity_pp_all(k)           G_all read at policy time k
G_all(t)                   cum_annuity_all(t)              Paid on every stream to time t
(G_all at a year's start)  cum_annuity_all_py(y)           G_all opening policy year y
(G_all at t = 0)           cum_annuity_all_init()          The same at t = 0
v                          vp_pct()                        Value-protection percentage
vp_basis                   vp_basis()                      first_death or last_survivor
(none)                     is_first_death()                vp_basis decoded: first death
VPbal(t)                   vp_balance(t)                   Value-protection balance at t
h(t)                       mths_since_payment(t)           Complete months since payment
proportion                 proportion()                    Proportionate final payment
(none)                     next_payment_mth(t)             The next payment's policy month
q_x (table)                mort_rate_base(t, life)         Base-table annual rate
(q_x by age)               mort_rate_base_at(x, life)      The table rate at attained age x
alpha                      annuitant_adj                   Population-to-annuitant factor
f(x)                       improve_rate(t, life)           Improvement rate at the age
(1-f)^(c-c0)               improve_factor(t, life)         Cumulative improvement factor
q_rated                    mort_rate(t, life)              Annual rate after all factors
q_m                        mort_rate_mth(t, life)          Monthly rate 1-(1-q)^(1/12)
(none)                     mort_basis()                    table or scenario run **[std]**
(none)                     is_scenario()                   mort_basis decoded: scenario
(none)                     death_mth(life)                 Scenario policy month of death
omega                      omega_age                       Limiting age, 115
(none)                     issue_age_min                   Youngest issue age, 0
(stopping rule)            horizon_mths()                  Policy months to the age stop
(none)                     proj_len()                      Months from t = 0 to the stop
(none)                     start_year()                    Calendar year of the start date
(none)                     calendar_year(t)                Calendar year containing month t
IF(t)                      pols_if(t)                      Any payment obligation open
(none)                     policy_count()                  Contracts the point stands for
(none)                     point_id()                      The point's label, idx's row
(none)                     pols_if_init()                  Contracts in payment at t = 0
(none)                     pols_if_at(t, timing)           Contracts on the books at time t
(none)                     pols_new_biz(t)                 Annuities starting in month t
E[ANN(t)]                  annuity_payments(t)             Expected annuity outgo
E[VP(t)]                   claims(t, VP)                   Value-protection lump sum
E[PROP(t)]                 claims(t, PROP)                 Proportionate final payment
(none)                     claims(t, ALL)                  The two kinds' total
E[EXP(t)]                  expenses(t)                     Maintenance expense
c_e, pi                    expense_maint, inflation_rate   Expense level and inflation
(none)                     inflation_factor(t)             Expense inflation, valuation clock
(none)                     cum_annuity_all_refusal(t)      G_all's refusal past the floats
(none)                     cum_annuity_pp_refusal(k)       G's refusal past the floats
CF(t)                      liability_cf(t)                 Total gross liability outgo
(none)                     net_cf(t)                       -liability_cf(t), insurer sign
=========================  ==============================  ==========================

Five names needed care in :mod:`~.PA_UK_S`, and keep their reasons here.

``G`` is used for two different accumulations in the notes: the *state variable* table
defines it as cumulative gross instalments **scheduled**, which is what the worked
example's G column prints, while the value-protection section says it accumulates
instalments "while the annuitant is alive" on the first-death basis and "the dependant's
instalments too" on the last-survivor one. Those are different objects whenever the
dependant's stream is running, and here they run on different clocks:
:func:`cum_annuity_pp` with ``kind = ANNUITANT`` is the deterministic as-if-alive
annuitant schedule, keyed by the policy time point ``k`` as the contract fixes it, and
:func:`cum_annuity_all` is the expected payments on every stream, keyed by the time point
``t`` on the valuation clock, as the survival that weights it is; ``cum_annuity_pp(k,
ALL)`` reads it at the policy time point ``k``, so that the notes' printed column keeps
its name.

``l`` and ``L`` differ in the notes only by case, as in ``SPIA_US_S``: survival
probability against the payment factor. They become :func:`lives_if` and
:func:`payment_factor_life`, with :func:`payment_factor` the certain-floored version.

``w(t)`` is the overlap gate, not a lapse rate — there is no lapse on this product at
all. It is spelled :func:`overlap_gate` so that nothing in the model reads as a
decrement that is not one.

``pols_if`` is not a policy count in the usual sense. It is the notes' ``IF(t)``, the
contracts with *any* payment obligation remaining — guarantee certain, annuitant alive, or
dependant stream in payment — and it exists to carry the maintenance expense. The name is
kept because it is what the rest of the library calls the expense weight.

``A(1)`` and the income of the year under way: :mod:`~.PA_UK_S`'s ``annual_income_init()``
returns the first year's income, which here is :func:`annual_income_first`, so that the
name ``annual_income_init`` is free for the opening state it means in the SEC family.

.. rubric:: Two mortality bases: table and scenario

The notes' worked example is not a probability-weighted run. It is a **scenario**: "the
annuitant dies in month 16; the dependant survives throughout", evaluated at
``l_a = 0`` from time 17 and ``l_d = 1`` throughout. The rest of the notes projects on
an expected basis. Both readings are shipped, and which one applies is a model point
column — the same device ``SPIA_US_S`` uses for the same reason:

``mort_basis = "table"``
    ``lives_if`` runs the generational recursion off the shipped mortality table and
    improvement scale, forward from the opening state.

``mort_basis = "scenario"`` **[std]**
    ``lives_if(t, life)`` is the deterministic step function
    ``1{duration_mth(t) <= death_mth(life)}`` on the policy clock — the life is alive up
    to the start of its month of death and dead from the end of it — with a blank
    ``death_mth`` meaning the life survives the whole projection. Restated in payment
    after the death, a point carries the life's 0 in its opening state.

The scenario switch is a **[std]** modelling device, not a product feature; it exists
because the notes' verification anchor is a scenario and retuning assumptions to force a
probability-weighted run onto it would be dishonest.

.. rubric:: The guarantee is a floor, not a second stream

``payment_factor(t) = max(certain_floor(t), payment_factor_life(t))`` is the notes'
first-listed pitfall written as one line. During the guarantee period the full
instalment is payable regardless of survival, escalating as if the annuitant were alive;
an additive construction would pay ``1 + l_a`` and silently double the guarantee. The
guarantee covers policy months ``0 .. n - 1``, so the months of it left at the valuation
date follow from ``duration_mth``.

The guarantee and value protection **never coexist** in the representative design — the
contract offers one or the other, and :func:`check_guarantee_xor` asserts no model point
carries both. An engine supporting the combinable variant would have to net guarantee
payments off the value-protection balance or the death benefit is paid twice.

.. rubric:: The overlap gate

``overlap = False`` is the representative default and means the dependant's stream
starts only at the **end of the guarantee period**, not at the annuitant's death.
Applying the dependant's percentage from the death date silently converts every
without-overlap policy into the more expensive with-overlap form, which is the notes'
second-listed pitfall. The gate reads the guarantee's end on the policy clock.

.. rubric:: Escalation, and the one path-dependent option

Four bases. ``level`` and ``fixed`` are self-explanatory; ``lpi5`` is RPI floored at
zero and capped at 5%; ``rpi_catchup`` is a **ratchet**: income is indexed to the
*running peak* of the RPI reference index, so a fall in the index freezes income rather
than reducing it, and later rises only bite once the index passes its previous peak.
:func:`rpi_peak` carries that state across anniversaries, from the opening state's.

The increases given before the valuation date are history. :mod:`~.PA_UK_S` rebuilds
them from today's flat ``rpi_rate``, so a contract restated in payment would have them
rewritten by any change of the assumption; here the RPI-linked income of the year under
way and the ratchet's peak are read from the model point, and ``rpi_rate`` is the RPI from
the valuation date on. The index is measured relative to the latest one, at the
anniversary that opened the year under way, ``rpi_index(a) = (1 + rpi_rate)^(a - a0)``,
and the peak relative to it is ``rpi_peak_init``. Under :mod:`~.PA_UK_S`'s deterministic
path the index is monotone and the ratchet never binds; with a peak above the index carried
in, a rising index first freezes income until it passes the peak and then catches up, the
branch a flat rate never reaches. The six-month reference lag of the source contract is
not modelled, as in :mod:`~.PA_UK_S`.

Escalation applies on the **anniversary**, not on payment dates: the year-2 rate does
not reach the ``t = 11`` arrears instalment, which accrued in year 1.

.. rubric:: Value protection, and where the balance is measured

``VP(t) = d(t) x max(0, v P - G)``, the death benefit measured against instalments
**already paid**. Two timing rules matter and both are the notes' pitfalls:

- on **arrears** timing the balance is the one at the *start* of the death month,
  because the instalment due at the end of it is never paid;
- on **advance** timing an instalment paid at the *start* of the death month **has**
  been paid, so in an advance payment month the balance is the one at its end —
  netting it, or the lump sum is overstated by one instalment.

On the ``first_death`` basis the death that triggers it is the annuitant's and the
balance nets the annuitant's schedule alone, at the policy time point; on
``last_survivor`` it is the last death, and the balance nets both streams' expected
payments, at the valuation time point. :func:`vp_balance` is keyed by the time point
``t`` on the valuation clock, and reads each at its own clock.

.. rubric:: There is no policyholder behaviour to model

No lapse decrement, no dynamic behaviour formulas, no surrender value at any time, no
alteration of options and no premium flexibility. That is a cited product feature and
the reason the liability is matching-adjustment eligible, and it is why this model has no
``lapse_rate`` of any kind.

.. rubric:: Sign convention

The notes define ``CF(t)`` as total gross liability **outgo**, which is
:func:`liability_cf`. :func:`net_cf` is its negative, the library-wide income-positive
convention, so a ``result_cf()["net_cf"]`` column can be summed or compared across every
model in the library. There is no premium income in the projection at all: the purchase
price is a pricing input paid at outset, before the first projected month, not a projected
cash flow.

.. rubric:: Chains blocked by policy year

Three cells recurse month by month: survival, :func:`lives_if`, on the table basis; the
payments to date on every stream, :func:`cum_annuity_all`; and the annuitant's,
``cum_annuity_pp(k, ANNUITANT)``. Called cold in the last month of the longest cover, at the
shipped limiting age, 115, one cell a month ran 1,380 cells back to :func:`t_entry` or the
valuation date's key, and at the contract's largest, ``omega_age_max``, 116, it would run
1,392; and a compiled model runs such a chain on the C stack, which the interpreter's
recursion limit does not count: it needed 244 to 276 KiB of it, compiled with gcc, past the
256 KiB the C step allows itself (UKLIB-SEC-PLAN.md K12). So each is blocked by policy year,
in ``ULB_UK_SEC``'s form: within a policy year it runs one cell a month, as before, and at
the time point or key that opens a year it reads the year's opening, :func:`lives_if_py`,
:func:`cum_annuity_all_py` or :func:`cum_annuity_pp_py`, which walks the year before in
ascending order, asking the monthly cell of each of its months, so that each finds the month
before cached, and returns the year's last month's step, the cell's own float, so no number
moves. A cold read then runs one cell a month back to its year's first time point and two
cells a year before that: at the shipped limiting age 239 cells and at most 12 more,
and 52 to 76 KiB of C stack, and at 116, 241 and at most 12 more. And no
cell such a chain recurses through formats a message: a compiled cell's C frame holds the
code of every message it formats, whether its branch runs or not, so a refusal that names
values sits in a cell of its own, which the chain's cell calls on its error path alone,
:func:`annual_income_refusal`, :func:`cum_annuity_all_refusal` and
:func:`cum_annuity_pp_refusal`, and ``cum_annuity_pp(k, ALL)``'s refusal of a key before the
valuation date's sits in :func:`cum_annuity_pp_all`.

.. rubric:: Codes

What :mod:`~.PA_UK_S` spells as text, a timing or a kind, is here an int Reference named as
the text it replaces, so that every cell takes and returns C numbers. A call site reads as
it did, less the quotes: ``pols_if_at(t, BEF_DECR)``, ``claims(t, VP)``,
``cum_annuity_pp(k, ANNUITANT)``.

=============  =====  ===============================================================
Reference      Value  Meaning
=============  =====  ===============================================================
BEF_NB         0      :func:`pols_if_at`: the count carried in from month t - 1
BEF_DECR       1      :func:`pols_if_at`: that count plus month t's new business
VP             0      :func:`claims`: the value-protection lump sum
PROP           1      :func:`claims`: the proportionate final payment
ANNUITANT      2      :func:`cum_annuity_pp`: the annuitant's as-if-alive instalments
ALL            3      :func:`claims`: the two kinds' total; :func:`cum_annuity_pp`: the
                      payments on every stream
=============  =====  ===============================================================

The timings are numbered by instant, ``BEF_NB`` 0 and ``BEF_DECR`` 1, as in every SEC
model. The kinds of the two cells that take one are numbered as one family, the claims'
two and the annuitant's stream, so that a kind of one cell is refused by the other's, as
``ULB_UK_SEC`` numbers its two families of timing; ``ALL``, the total, comes last, and
names the total of either cell, which :mod:`~.PA_UK_S` spells ``claims(t)`` and
``cum_annuity_pp(k, "ALL")``. A code a cell takes indexes that cell's cache, a C array four
codes wide, since every 2-D cache of the model has one inner width (``spec_sec.py``), so
codes are numbered densely from 0, and any other code a cell is given raises, as
:mod:`~.PA_UK_S`'s text does. They are References, not cells, so the symbol map does not
list them. Every other Reference is named in lower case, ``issue_age_min`` and
``omega_age`` among them, the contract's bounds that :func:`proj_len` checks and that the
compiled model's caches are sized from, with ``Data.future_horizon_mth``.

.. rubric:: Reporting cells

:func:`model_point`, the label accessors :func:`payment_timing`, :func:`escalation_type`,
:func:`vp_basis`, :func:`mort_basis` and :func:`sex`, the reports :func:`result_cf` and
:func:`result_pols`, and the four checks are written for a reader and for the comparison
with :mod:`~.PA_UK_S`, which has every one of them: a table row, text, DataFrames and four
verdicts. No other cell calls them: each reads the number ``Data`` decoded from the same
column instead, the decodes' flags and the schedules the sexes select. So the row, the
text and the frames stay Python when the model compiles. Each label returns its point's
column: ``escalation_type``, ``vp_basis`` and ``mort_basis`` the column of their own name,
``payment_timing`` the ``timing`` column and ``sex(life)`` the ``annuitant_sex`` or
``dependant_sex`` column by life, as the registry declares them. The first four validate
their column, as :mod:`~.PA_UK_S`'s do, so each returns text or raises; ``sex`` returns
its column as read, text or not, a single-life contract's blank second life as NaN, where
:mod:`~.PA_UK_S` refuses the second life of a single life, and the compiled accessor
returns the same. Every other cell returns a C ``bint``, ``long long`` or ``double``, and so
do the four checks, which may stay Python but compile to a ``bint``, their verdict, as
their per-month residuals, ``*_resid``, compile to a ``double``.

.. rubric:: The contract's bounds

What running in force adds is the contract's own bounds, which :func:`proj_len` holds a
point to: every covered life issued at ``issue_age_min``, 0, or more, the youngest age
:mod:`~.PA_UK_S` projects; on the table basis a limiting age of at most
``omega_age_max``, 116, the shipped table's last age plus one; a guarantee of at most
``12 x (omega_age - issue_age_min)`` months, the longest frame from the start date; a
contract still owing a payment at the valuation date, short of the stop rule. ``Data``
bounds future new business by ``future_horizon_mth``, 120 months. And :func:`proj_len`
holds every Reference a formula reads through a bound or a power to its domain, NaN and
the infinities outside each, its docstring naming each domain and its reason. Those
bounds are the contract the compiled model's caches are sized from (``spec_sec.py``): a
frame of at most ``12 x (omega_age_max - issue_age_min)`` months, 1,392, from the start
date, starting at most 120 months after the valuation date, so that every frame the table
basis projects fits them, at any limiting age the table and the bound admit. The
scenario basis reads no mortality table, and :func:`proj_len` holds its limiting age to
no bound, as the in-force step held it to none: there a limiting age above
``omega_age_max`` projects in modelx, and in the compiled model a frame longer than 1,392
months from the start date, a life issued younger than ``omega_age - omega_age_max``,
raises a bare ``IndexError`` at its first policy month past 1,393, where the caches end.
Raising ``omega_age_max`` or the horizon needs the caches derived again and the model
rebuilt; :func:`proj_len` refuses an ``issue_age_min`` below 0.
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

    Row ``idx`` of the table, for a reader who wants every column at once: a reporting
    cell (the Space docstring's *Reporting cells*), which only the label accessors read.
    Every projection cell reads its own ``Data`` vector instead.
    """
    return data.model_point_table().iloc[idx]                        # noqa: F821


def point_id():
    """The label of the selected model point, its ``point_id``, from ``Data.point_id``.

    ``Projection`` is indexed by position, ``idx``, as ``basiclife.BasicTerm_SC`` is; the
    label is what a reader finds in the table, so every refusal names it.
    """
    return int(data.point_id()[idx])                                 # noqa: F821


def purchase_price():
    """P: the amount applied to the annuity after any lump sum and adviser charges.

    A pricing input paid at outset, before the first projected month, not a projected
    cash flow: the projection carries no premium income, for a contract starting after the
    valuation date as for one already in payment.  It enters the projection only through
    value protection, where the guarantee is measured against it.

    Read from ``Data.purchase_price``.  Refused here, naming the point, where it is not a
    number, which :mod:`~.PA_UK_S`'s ``float()`` refuses, and where value protection is
    elected, the one reader, where it is not a finite number, 0 or more, which the
    balance's ``max(0, v P - G)`` would read as a number (``Data``'s
    ``purchase_price_ok``).  A contract without value protection never reads it, and a
    blank there is NaN, as in :mod:`~.PA_UK_S`.
    """
    if data.purchase_price_ok()[idx] == 0:                           # noqa: F821
        raise ValueError(f"point_id {point_id()}: purchase_price must be a number, and a "
                         f"finite one, 0 or more, where value protection is elected, which "
                         f"reads it; it is not")
    return float(data.purchase_price()[idx])                         # noqa: F821


def age_at_entry(life):
    """x: the entry age of the annuitant (``life = 1``) or dependant (``life = 2``).

    **Age last birthday**, chosen to index the shipped single-year-of-age proxy table
    **[std]**.  The age at the start date, not at the valuation date: ``age(0, life)`` is
    the attained age there.  Read from ``Data.annuitant_age`` and ``Data.dependant_age``,
    which ``Data`` holds to whole numbers below ``2**53``, the dependant's on a contract
    with a dependant, the one that reads it.
    """
    if life == 1:
        return int(data.annuitant_age()[idx])                        # noqa: F821
    if life == 2 and is_joint():
        return int(data.dependant_age()[idx])                        # noqa: F821
    raise ValueError("invalid life")


def sex(life):
    """The sex (M / F) of the annuitant (life = 1) or dependant (life = 2); a label.

    A label accessor, which no projection cell calls: it returns the ``annuitant_sex`` or
    ``dependant_sex`` column as read, a single-life contract's blank second life as NaN,
    where :mod:`~.PA_UK_S` refuses the second life of a single-life contract, as
    ``Term_UK_SEC``'s and ``SPIA_US_SEC``'s labels do.  The mortality table's reader joins
    on the sex through :func:`mort_schedule` instead.
    """
    if life == 1:
        return model_point()["annuitant_sex"]
    if life == 2:
        return model_point()["dependant_sex"]
    raise ValueError("invalid life")


def mort_schedule(life):
    """The number of ``life``'s sex in the mortality table: its row of
    ``Data.mort_table_array``.

    ``Data.mort_schedule_1`` for the annuitant (life = 1) and ``Data.mort_schedule_2`` for
    the dependant (life = 2) of a contract with one; any other life raises, as
    :func:`age_at_entry` does.  The table basis alone reads it, through
    :func:`mort_rate_base_at` and :func:`proj_len`, and a sex the table lacks, schedule 0,
    a blank among them, is refused here, naming the point and the column, where
    :mod:`~.PA_UK_S`'s lookup raised ``KeyError``: on the scenario basis, which reads no
    mortality, the same sex projects (``Data``, *refused by point*).  A cell of its own, so
    that the reader indexes the table by a cell's value, never by a ``Data`` array's.
    """
    if life == 1:
        if data.mort_schedule_1()[idx] == 0:                         # noqa: F821
            raise ValueError(f"point_id {point_id()}: annuitant_sex must be M or F, a sex "
                             f"mort_table.csv rates, on the table basis, which reads it; "
                             f"it is not")
        return int(data.mort_schedule_1()[idx])                      # noqa: F821
    if life == 2 and is_joint():
        if data.mort_schedule_2()[idx] == 0:                         # noqa: F821
            raise ValueError(f"point_id {point_id()}: dependant_sex must be M or F, a sex "
                             f"mort_table.csv rates, on the table basis, which reads it; "
                             f"it is not")
        return int(data.mort_schedule_2()[idx])                      # noqa: F821
    raise ValueError("invalid life")


def rating_factor(life):
    """theta: the enhanced or impaired mortality multiplier **[std]**; 1.0 standard.

    ``q_rated = min(theta x q, 1)``, the simplest overlay that reprices longevity
    without touching contract mechanics.  Insurers' real rating structures - postcode
    and condition-specific factors - are not public, and a rated-age offset is the
    equivalent form.  Whole-market enhanced quoting is mandated at the point of sale, so
    lives remaining on standard terms are healthier on average; the model carries that
    through this multiplier rather than through any behavioural dynamic.

    Read from ``Data.rating_multiplier`` and ``Data.dependant_rating``.  Refused here,
    naming the point, where it is not a number, and on the table basis, the one reader,
    where it is not a finite number, 1 or more, the notes' ``theta >= 1``: the cap puts
    its bound second, so a missing rating would stay missing, and an infinite one read as
    certain death (``Data``'s ``rating_multiplier_ok`` and ``dependant_rating_ok``).  The
    scenario basis never reads it.
    """
    if life == 1:
        if data.rating_multiplier_ok()[idx] == 0:                    # noqa: F821
            raise ValueError(f"point_id {point_id()}: rating_multiplier must be a number, "
                             f"and a finite one, 1 or more, on the table basis, which "
                             f"reads it; it is not")
        return float(data.rating_multiplier()[idx])                  # noqa: F821
    if life == 2 and is_joint():
        if data.dependant_rating_ok()[idx] == 0:                     # noqa: F821
            raise ValueError(f"point_id {point_id()}: dependant_rating must be a number, "
                             f"and a finite one, 1 or more, on the table basis, which "
                             f"reads it; it is not")
        return float(data.dependant_rating()[idx])                   # noqa: F821
    raise ValueError("invalid life")


def is_joint():
    """True when the contract carries a dependant's income: ``Data.is_joint``.

    ``Data`` holds ``dependant_present`` to True or False, where :mod:`~.PA_UK_S` reads a
    blank as True through ``bool(nan)``.
    """
    return bool(data.is_joint()[idx])                                # noqa: F821


def dependant_pct():
    """delta: the dependant's percentage of the income; zero on a single-life contract.

    Asks first whether the contract covers a dependant, so that a single-life contract's
    ``dependant_pct`` is never read, where :mod:`~.PA_UK_S` reads it first and discards it:
    ``Data`` holds it to a number from 0 to 1 where it is read.
    """
    if not is_joint():
        return 0.0
    return float(data.dependant_pct()[idx])                          # noqa: F821


def overlap():
    """Whether the dependant's stream runs *during* the remaining guarantee period.

    ``False`` is the representative default and means the stream starts at the end of
    the guarantee, not at the annuitant's death.  See :func:`overlap_gate`.  Read from
    ``Data.overlap``, and refused here, naming the point, where it is not True or False on
    a contract with a dependant, the one reader (``Data``'s ``overlap_ok``).
    """
    if data.overlap_ok()[idx] == 0:                                  # noqa: F821
        raise ValueError(f"point_id {point_id()}: overlap must be True or False on a "
                         f"contract with a dependant, which reads it; it is not")
    return bool(data.overlap()[idx])                                 # noqa: F821


def annual_income_first():
    """A(1): the starting annualized income, the ``annual_income`` column.

    :mod:`~.PA_UK_S`'s ``annual_income_init()``, renamed, so that D6's name is free for the
    income of the year under way at the valuation date, :func:`annual_income_init`.  A
    pricing input taken from a quote: no insurer publishes an annuity rate card, so the
    model does not derive income from the purchase price and nothing in the projection
    consumes ``P`` except value protection.  Read from ``Data.annual_income``.
    """
    return float(data.annual_income()[idx])                          # noqa: F821


def policy_year_init():
    """y0: the policy year under way at the valuation instant, before any month-0 event.

    ``(duration_mth_init() - 1) // 12 + 1`` on a contract in payment at the valuation
    date, the policy year of the month before it, and 1 on one starting at or after it.
    On a contract valued on an anniversary, ``duration_mth_init()`` a multiple of 12, it is
    the year the anniversary closes, not the one it opens: the anniversary's escalation is
    a month-0 event, and applies at the valuation date's References.  The key at which
    :func:`annual_income` takes its opening value, and through ``a0 = y0 - 1`` the
    anniversary :func:`rpi_index` and :func:`rpi_peak` measure from.  Static: it reads no
    clock.
    """
    d = duration_mth_init()
    if d > 0:
        return (d - 1) // 12 + 1
    return 1


def annual_income_init():
    """A(y0): the annualized income of the policy year under way at the valuation instant.

    The **annuitant's** income, before the dependant's percentage, as every year's
    :func:`annual_income` is: on a contract whose annuitant has died it is still the
    annuitant's scale, the dependant being paid ``delta`` times it.  The year is
    :func:`policy_year_init`, before any month-0 anniversary.  By basis:

    * RPI-linked, ``lpi5`` or ``rpi_catchup``: the ``annual_income_init`` column, history,
      from ``Data.annual_income_init``.  The increases given before the valuation date are
      facts of the contract, which no flat ``rpi_rate`` re-derives: an RPI past the LPI
      cap, or a fall the ratchet froze income through, is in it.  At the start date, and
      so on every point not yet in payment, and in the first policy year, it is the first
      year's income, :func:`annual_income_first`, as ``Data`` checks.
    * ``fixed``: the contract's schedule, ``A(1) (1 + g)^(y0 - 1)``, compounded year by
      year in one loop in :mod:`~.PA_UK_S`'s order, bit for bit with its recursion.  An
      income that leaves the floats on the way is refused in the year it first does, as
      :func:`annual_income` refuses it.
    * ``level``: ``A(1)``.

    On a point starting at the valuation date it is ``A(1)`` on every basis,
    :mod:`~.PA_UK_S`'s ``annual_income_init()``.
    """
    if is_lpi5() or is_rpi_catchup():
        return float(data.annual_income_init()[idx])                 # noqa: F821
    income = annual_income_first()
    if is_fixed():
        for y in range(2, policy_year_init() + 1):
            income *= 1.0 + escalation_rate()
            if not income <= 1.7976931348623157e308:
                raise ValueError(
                    f"point_id {point_id()}: the income annual_income({y}) is {income}, "
                    f"not a finite number, under escalation_rate {escalation_rate()}")
    return income


def payment_freq():
    """m: payments per year, in {12, 4, 2, 1}.

    Read from ``Data.frequency``, which ``Data`` holds to a whole number, read by its value,
    which :mod:`~.PA_UK_S` truncates with ``int``.  The four values are compared one by
    one, where :mod:`~.PA_UK_S` builds a tuple of them, which a compiled cell cannot hold,
    and the element is compared, never held in a local, so the compiled cell keeps no
    Python object.
    """
    if (data.frequency()[idx] == 12 or data.frequency()[idx] == 4    # noqa: F821
            or data.frequency()[idx] == 2 or data.frequency()[idx] == 1):  # noqa: F821
        return int(data.frequency()[idx])                            # noqa: F821
    raise ValueError(f"point_id {point_id()}: invalid frequency")


def payment_timing():
    """Whether instalments fall in *arrears* or in *advance*; a label, for reporting.

    Arrears instalments require survival at the end of the payment month; advance
    instalments at the start of it.  Using end-of-period survival for advance payments
    understates the liability by roughly one period's mortality per payment, which is
    material at high ages.  A label accessor, which no projection cell calls: it returns
    the ``timing`` column, compared exactly, or raises.  The projection branches on
    :func:`is_arrears`.
    """
    v = model_point()["timing"]
    if v not in ("arrears", "advance"):
        raise ValueError("invalid timing")
    return v


def is_arrears():
    """Whether instalments fall in arrears, at the end of the month, rather than in advance.

    A decode of the model point's ``timing`` column, ``Data.is_arrears``, validated by
    ``Data.has_timing`` as :func:`payment_timing` validates it, so that the payment months,
    the survival point, the value-protection balance and the proportion rule branch on a
    flag and no projection cell calls the label accessor, which is left to reporting.  A
    value the accessor refuses is refused here in :mod:`~.PA_UK_S`'s words, naming the
    point, as every refusal of a value the model point holds does.
    """
    if data.has_timing()[idx] == 0:                                  # noqa: F821
        raise ValueError(f"point_id {point_id()}: invalid timing")
    return bool(data.is_arrears()[idx])                              # noqa: F821


def proportion():
    """Whether a proportionate final payment is made for the accrued part-period.

    Arrears only.  Without it - the representative default - nothing is paid for the
    final partial period, which is the more common contractual design.  Read from
    ``Data.proportion``, which ``Data`` holds to True or False.
    """
    v = bool(data.proportion()[idx])                                 # noqa: F821
    if v and not is_arrears():
        raise ValueError(f"point_id {point_id()}: proportion applies to arrears payments "
                         f"only")
    return v


def escalation_type():
    """``level``, ``fixed``, ``rpi_catchup`` or ``lpi5``; a label, for reporting.

    ``lpi5`` is RPI floored at zero and capped at 5%; ``rpi_catchup`` is a ratchet on
    the running peak of the RPI reference index.  See the Space docstring.  A label
    accessor, which no projection cell calls: it returns the column, compared exactly, or
    raises.  The projection branches on the four decodes below.
    """
    v = model_point()["escalation_type"]
    if v not in ("level", "fixed", "rpi_catchup", "lpi5"):
        raise ValueError("invalid escalation_type")
    return v


def is_level():
    """Whether the income is level.

    One of four decodes of the model point's ``escalation_type`` column, as are the three
    below it, so that no projection cell compares text or calls :func:`escalation_type`,
    the label accessor, which is left to reporting.  Each reads ``Data``'s flag for its
    value, and ``Data.has_escalation_type``, which says whether the column holds one of the
    four values :func:`escalation_type` accepts, compared as it compares them, so an
    invalid basis raises :mod:`~.PA_UK_S`'s ``invalid escalation_type``, naming the point,
    wherever the projection first meets it.
    """
    if data.has_escalation_type()[idx] == 0:                         # noqa: F821
        raise ValueError(f"point_id {point_id()}: invalid escalation_type")
    return bool(data.is_level()[idx])                                # noqa: F821


def is_fixed():
    """Whether the income escalates at the fixed rate ``g`` each anniversary.

    A decode of the ``escalation_type`` column, validated as :func:`escalation_type`
    validates it.
    """
    if data.has_escalation_type()[idx] == 0:                         # noqa: F821
        raise ValueError(f"point_id {point_id()}: invalid escalation_type")
    return bool(data.is_fixed()[idx])                                # noqa: F821


def is_lpi5():
    """Whether the income escalates at the RPI, floored at 0 and capped at ``esc_lpi_cap``.

    A decode of the ``escalation_type`` column, validated as :func:`escalation_type`
    validates it.
    """
    if data.has_escalation_type()[idx] == 0:                         # noqa: F821
        raise ValueError(f"point_id {point_id()}: invalid escalation_type")
    return bool(data.is_lpi5()[idx])                                 # noqa: F821


def is_rpi_catchup():
    """Whether the income is indexed to the running peak of the RPI reference index.

    A decode of the ``escalation_type`` column, validated as :func:`escalation_type`
    validates it.
    """
    if data.has_escalation_type()[idx] == 0:                         # noqa: F821
        raise ValueError(f"point_id {point_id()}: invalid escalation_type")
    return bool(data.is_rpi_catchup()[idx])                          # noqa: F821


def escalation_rate():
    """g: the fixed escalation rate, at most ``esc_fixed_cap``; read on ``fixed`` only.

    Read from ``Data.escalation_rate``, which ``Data`` holds to a finite number, 0 or
    more, on a ``fixed`` point: the notes' menu is non-decreasing, which the dependant's
    base relies on.  Text is refused here, naming the point, which :mod:`~.PA_UK_S`'s
    ``float()`` refuses, and elsewhere a blank is NaN (``Data``'s ``escalation_rate_ok``).
    """
    if data.escalation_rate_ok()[idx] == 0:                          # noqa: F821
        raise ValueError(f"point_id {point_id()}: escalation_rate must be a number; it "
                         f"is not")
    v = float(data.escalation_rate()[idx])                           # noqa: F821
    if v > esc_fixed_cap:                                            # noqa: F821
        raise ValueError(f"point_id {point_id()}: fixed escalation exceeds the "
                         f"contractual cap")
    return v


def guarantee_mths():
    """n: the guarantee period in months, 0 or 12-360, counted from the start date.

    Instalments are certain for policy months ``0 .. n - 1``, escalating as if the
    annuitant were alive.  Mutually exclusive with value protection in the representative
    design.  Read from ``Data.guarantee_months``, which ``Data`` holds to a whole number of
    months, 0 or more, which :mod:`~.PA_UK_S` truncates with ``int``, and :func:`proj_len`
    to the longest frame.
    """
    return int(data.guarantee_months()[idx])                         # noqa: F821


def vp_pct():
    """v: the value-protection percentage of the purchase price; 0 if not elected.

    Read from ``Data.vp_pct``, which ``Data`` holds to a number from 0 to 1, where
    :mod:`~.PA_UK_S` reads any.
    """
    return float(data.vp_pct()[idx])                                 # noqa: F821


def vp_basis():
    """Whether value protection pays on the ``first_death`` or the ``last_survivor``.

    A label, for reporting; the projection branches on :func:`is_first_death`.  On the
    first-death basis the trigger is the annuitant's death and the balance nets the
    annuitant's instalments; on the last-survivor basis it is the last death, and the
    balance nets both streams.  It returns the column, compared exactly, or raises.
    """
    v = model_point()["vp_basis"]
    if v not in ("first_death", "last_survivor"):
        raise ValueError("invalid vp_basis")
    return v


def is_first_death():
    """Whether value protection pays on the annuitant's death, not on the last death.

    A decode of the model point's ``vp_basis`` column, ``Data.is_first_death``, validated
    by ``Data.has_vp_basis`` as :func:`vp_basis` validates it.  Read only where value
    protection is elected.
    """
    if data.has_vp_basis()[idx] == 0:                                # noqa: F821
        raise ValueError(f"point_id {point_id()}: invalid vp_basis")
    return bool(data.is_first_death()[idx])                          # noqa: F821


def mort_basis():
    """Whether the run is probability-weighted (*table*) or deterministic (*scenario*).

    A label, for reporting; the projection branches on :func:`is_scenario`.  *table* runs
    the generational recursion off the shipped table and improvement scale; *scenario*
    **[std]** replaces it with the step function ``1{duration_mth(t) <= death_mth(life)}``.
    See the Space docstring.  It returns the column, compared exactly, or raises.
    """
    v = model_point()["mort_basis"]
    if v not in ("table", "scenario"):
        raise ValueError("invalid mort_basis")
    return v


def is_scenario():
    """Whether the run is the deterministic scenario, not the probability-weighted table.

    A decode of the model point's ``mort_basis`` column, ``Data.is_scenario``, validated
    by ``Data.has_mort_basis`` as :func:`mort_basis` validates it, so that :func:`lives_if`
    and its check branch on a flag.
    """
    if data.has_mort_basis()[idx] == 0:                              # noqa: F821
        raise ValueError(f"point_id {point_id()}: invalid mort_basis")
    return bool(data.is_scenario()[idx])                             # noqa: F821


def death_mth(life):
    """The scenario month of death of ``life``, a **policy month**; -1 if it survives.

    Read only on the scenario basis.  A blank cell in the model point table means the life
    never dies in the scenario and is returned as -1, because month 0 is a projectable
    month of death like any other.  The month counts from the start date, on the clock
    :func:`duration_mth` counts, whatever the valuation date: a death "in month 16" is
    decremented at the end of policy month 16, so ``lives_if(t, life)`` is 1 while
    ``duration_mth(t) <= 16`` and 0 from the next time point on.  Read from
    ``Data.death_mth_1`` and ``Data.death_mth_2``, which hold the blank as -1 already, and
    which ``Data`` holds on the scenario basis to blank or a whole number, 0 or more, where
    :mod:`~.PA_UK_S` truncates a fraction and reads a negative month as a life that never
    dies; a month of ``2**53`` or more in size is refused here, naming the point.  Any
    other life raises, where stage ``E`` read the dependant's column for any life but 1.
    """
    if life == 1:
        if data.death_mth_1_ok()[idx] == 0:                          # noqa: F821
            raise ValueError(f"point_id {point_id()}: death_mth_1 must be blank or below "
                             f"2**53 months in size; it is not")
        return int(data.death_mth_1()[idx])                          # noqa: F821
    if life == 2:
        if data.death_mth_2_ok()[idx] == 0:                          # noqa: F821
            raise ValueError(f"point_id {point_id()}: death_mth_2 must be blank or below "
                             f"2**53 months in size; it is not")
        return int(data.death_mth_2()[idx])                          # noqa: F821
    raise ValueError("invalid life")


def start_year():
    """The calendar year of the annuity start date; the improvement-scale anchor.

    The improvement exponent is ``calendar_year(t) - mort_table_year``, so this is what
    makes the mortality basis generational rather than period.  For a contract in payment
    at the valuation date it is the year the annuity started, before that date; for one
    starting after it, the year it will start.  The model carries no calendar valuation
    date: each point's calendar years follow from its own start year, which is why
    improvement needs nothing re-based on the valuation clock.  Read from
    ``Data.start_year``, by value, and refused here, naming the point, where it is not a
    number below ``2**53`` in size, and on the table basis, the one reader, where it is
    not a whole number, which :mod:`~.PA_UK_S` truncates (``Data``'s ``start_year_ok``).
    """
    if data.start_year_ok()[idx] == 0:                               # noqa: F821
        raise ValueError(f"point_id {point_id()}: start_year must be a number, below 2**53 "
                         f"in size, and a whole one on the table basis, which reads it; it "
                         f"is not")
    return int(data.start_year()[idx])                               # noqa: F821


def policy_count():
    """The number of contracts the model point stands for, its ``policy_count`` column.

    A point in payment at the valuation date counts the contracts in payment then, before
    any month-0 event; any other point counts the annuities it starts.  Either way the
    count enters the projection once: as :func:`pols_if_init` for the first, as
    :func:`pols_new_biz` in the month the annuity starts for the second.  It is
    :mod:`~.PA_UK_S`'s ``pols_if_init`` column, renamed, and like it a constant on the
    books: mortality decrements each life's survival, :func:`lives_if`, never the count.
    Read from ``Data.policy_count``.
    """
    return float(data.policy_count()[idx])                           # noqa: F821


def pols_if_init():
    """Contracts in payment at the valuation date, before any month-0 event.

    ``policy_count()`` for a point already in payment at ``t = 0``
    (``duration_mth_init() > 0``), and 0 for one starting at or after it, whose contracts
    enter through :func:`pols_new_biz` in the month the annuity starts instead, as in
    ``basiclife.BasicTerm_SE``.  So on a point starting at ``t = 0`` this is 0, where
    :mod:`~.PA_UK_S`'s is the count itself; on either model the count that weights row 0 is
    the same, here ``pols_if_at(0, BEF_DECR)``.
    """
    return policy_count() if duration_mth_init() > 0 else 0.0


def duration_mth_init():
    """Months from the start date to the valuation date, the ``duration_mth`` column.

    The contract's age in months at ``t = 0``: 17 for an annuity that started 17 months
    before the valuation date, 0 for one starting at it, and -13 for one to start 13 months
    after it, which ``Data`` admits up to ``future_horizon_mth`` months ahead.  It is read
    as ``basiclife.BasicTerm_SE`` reads it, by value, and is the one fact the policy clock
    takes from the model point, from ``Data.duration_mth``.
    """
    return int(data.duration_mth()[idx])                             # noqa: F821


def lives_if_init(life):
    """l_i at the valuation date: the probability that ``life`` is alive then.

    The ``lives_if_init_1`` (annuitant, life = 1) or ``lives_if_init_2`` (dependant,
    life = 2) column, as the contract stands at the start of month 0, before any month-0
    death: the opening value of :func:`lives_if` at :func:`t_entry`.  On a real record it
    is 1 or 0, so a joint contract may carry one life already dead; on a point restated
    from :mod:`~.PA_UK_S` at its month ``d`` it is :mod:`~.PA_UK_S`'s ``lives_if(d, life)``,
    a probability.  The lives are independent, as in :mod:`~.PA_UK_S`, so the two per-life
    probabilities are the whole survival state.  A contract not yet in payment carries its
    values at the start date, 1 for each covered life, and ``lives_if_init_2`` is 0 on a
    single-life contract; ``Data`` checks both, and on the scenario basis that each status
    is its death month's.  Read from ``Data.lives_if_init_1`` and ``Data.lives_if_init_2``.
    """
    if life == 1:
        return float(data.lives_if_init_1()[idx])                    # noqa: F821
    if life == 2:
        return float(data.lives_if_init_2()[idx])                    # noqa: F821
    raise ValueError("invalid life")


def cum_annuity_all_init():
    """G_all at the valuation date: the payments made by then on every stream, per contract.

    The ``cum_annuity_all_init`` column: every instalment paid before the valuation
    instant, the annuitant's, the guaranteed ones and the dependant's, the opening value of
    :func:`cum_annuity_all` at :func:`t_entry`.  What was paid, on a real record; on a point
    restated from :mod:`~.PA_UK_S` at its month ``d``, its expectation,
    ``cum_annuity_pp(d, "ALL")`` there.  Path-dependent, so no schedule re-derives it.
    Last-survivor value protection nets against it, and :func:`result_pols` publishes it.
    0 on a contract not yet in payment, which ``Data`` requires.  Read from
    ``Data.cum_annuity_all_init``.
    """
    return float(data.cum_annuity_all_init()[idx])                   # noqa: F821


def rpi_peak_init():
    """peak(a0) / I(a0): the ratchet's state at the valuation date, relative to the index.

    The ``rpi_peak_init`` column, read on ``rpi_catchup`` only: the running peak of the RPI
    reference index through the anniversary that opened the policy year under way,
    ``a0 = policy_year_init() - 1``, over the index there.  1 while the index has never
    fallen below a past peak, and above 1 while it is below one, as after a fall the
    ratchet froze income through.  History, which :mod:`~.PA_UK_S` rebuilds from today's
    flat ``rpi_rate``, under which a monotone index never leaves the ratio at anything but
    1.  1 at the start date, and so on a point not yet in payment, and in the first policy
    year, as ``Data`` checks.  Read from ``Data.rpi_peak_init``; text is refused here,
    naming the point, and elsewhere than on ``rpi_catchup`` a blank is NaN.
    """
    if data.rpi_peak_init_ok()[idx] == 0:                            # noqa: F821
        raise ValueError(f"point_id {point_id()}: rpi_peak_init must be a number; it is "
                         f"not")
    return float(data.rpi_peak_init()[idx])                          # noqa: F821


def cum_annuity_pp_init():
    """G at the valuation date: the annuitant's as-if-alive instalments to date, per contract.

    The ``cum_annuity_pp_init`` column, read on RPI-linked escalation with value protection
    on the first death: the scheduled annuitant instalments of every policy month before the
    valuation date, whether or not the annuitant lived to them, which the first-death
    balance nets against.  On RPI-linked escalation the instalments followed the RPI of
    their day, which no flat ``rpi_rate`` re-derives; on level and fixed escalation
    :func:`cum_annuity_pp` sums the schedule instead.  0 on a contract not yet in payment,
    which ``Data`` requires.  Read from ``Data.cum_annuity_pp_init``; text is refused here,
    naming the point, and elsewhere than where it is read a blank is NaN.
    """
    if data.cum_annuity_pp_init_ok()[idx] == 0:                      # noqa: F821
        raise ValueError(f"point_id {point_id()}: cum_annuity_pp_init must be a number; "
                         f"it is not")
    return float(data.cum_annuity_pp_init()[idx])                    # noqa: F821


def duration(t):
    """Completed policy years at the start of month t: ``duration_mth(t) // 12``.

    0 throughout the first policy year from the start date, and negative before it.
    """
    return duration_mth(t) // 12


def duration_mth(t):
    """Months elapsed from the start date at the start of month t, the **policy** clock.

    ``duration_mth_init() + t``: ``t`` counts months from the valuation date and
    ``duration_mth(t)`` months from the start date, and the two move together.  A closed
    form, where ``basiclife.BasicTerm_SE`` adds one a month by recursion: the same numbers,
    without a call chain as long as the frame.  Negative before the start date.
    """
    return duration_mth_init() + t


def t_entry():
    """The first month the contract is on the books: ``max(0, -duration_mth_init())``.

    0 for a contract in payment at the valuation date or starting at it, ``k`` for one
    starting ``k`` months later.  It is the base of every recursion on the valuation
    clock: :func:`lives_if` and :func:`cum_annuity_all` open there, from the opening
    state, and read no month before it, and :func:`pols_if_at` counts the contracts from
    there.
    """
    return max(0, -duration_mth_init())


def stop_mth():
    """The policy month at which the projection stops: the stop rule, on the policy clock.

    ``max(horizon_mths(), guarantee_mths())``, :mod:`~.PA_UK_S`'s frame length counted from
    the start date: the notes' age stop on the youngest covered life, or the end of the
    guarantee if that is later.  The last projected month is policy month
    ``stop_mth() - 1``; :func:`proj_len` counts the months to the stop from the valuation
    date instead.  636 on the worked configuration's 65/62 pair.
    """
    return max(horizon_mths(), guarantee_mths())


def is_active(t):
    """Whether month t is inside the frame: started, and not yet at the stop rule.

    ``0 <= duration_mth(t) < stop_mth()``.  False before the start date and from the stop
    rule on.  Outside it every count is zero, and so every cash flow; no cell reads a rate,
    a policy year or an attained age there that the contract does not have.  A contract's
    own end inside the frame - its last death, or its last guaranteed instalment - is a
    probability or a floor reaching zero, not the end of the frame, which runs on with zeros
    as :mod:`~.PA_UK_S`'s does.
    """
    return 0 <= duration_mth(t) < stop_mth()


def policy_year(t):
    """y = duration(t) + 1: the policy year containing month t, on the policy clock.

    The contract's own 1-based label, *derived* from the policy clock, never used to index
    the frame: 1 for policy months 0..11, whatever ``t`` they fall at.  It is 0 or less
    before the start date, where no cell reads a schedule by it.
    """
    return duration(t) + 1


def age(t, life):
    """The attained age (ALB) of ``life`` in the policy year containing month t.

    ``age_at_entry(life) + duration(t)``, on the policy clock: the age changes on each
    anniversary of the start date, whatever the valuation date.
    """
    return age_at_entry(life) + duration(t)


def calendar_year(t):
    """The calendar year of the policy year containing month t, on the policy clock.

    ``start_year() + duration(t)``: calendar-dated from the start year, so a contract in
    payment at the valuation date reads its own calendar years whatever that date, and
    nothing in the improvement it dates is re-based onto the valuation clock.  On a point
    restated from :mod:`~.PA_UK_S` at its month ``d``, month ``t`` here is
    :mod:`~.PA_UK_S`'s month ``d + t``, and so the same calendar year.
    """
    return start_year() + duration(t)


def horizon_mths():
    """Policy months from the start date before some covered life reaches the limiting age.

    ``12 x (omega_age - min x_i)``: the notes stop once ``t // 12 + x_i >= omega`` for
    every covered life, and stopping on the annuitant's age alone would truncate a
    younger dependant's tail.  Counted from the start date, so the last month it admits is
    policy month ``horizon_mths() - 1``.  The notes' other stop test, ``IF(t) < 1e-6``, is
    not implemented, because a stopping rule that depends on the projection it bounds is
    harder to reason about than one that does not.  The younger of the two ages is found by
    one comparison, where :mod:`~.PA_UK_S` takes the ``min`` of a list, which a compiled
    cell cannot hold.  ``omega_age`` is read through ``int()``, which :func:`proj_len` has
    held to a whole number, so that a whole float, ``115.0``, gives the int frame every
    report counts its months in, as ``Term_UK_SEC`` reads one.
    """
    youngest = age_at_entry(1)
    if is_joint() and age_at_entry(2) < youngest:
        youngest = age_at_entry(2)
    return 12 * (int(omega_age) - youngest)                          # noqa: F821


def proj_len():
    """The number of months from the valuation date to the stop rule.

    ``stop_mth() - duration_mth_init()``: 636 for the worked configuration starting at
    ``t = 0``, 619 for it in payment 17 months, and 649 for a joint contract starting 13
    months after the valuation date.  The exclusive end of the frame: :func:`result_cf`
    runs over ``range(proj_len())``, so the last projected month is ``proj_len() - 1``,
    which is policy month ``stop_mth() - 1`` on every point.

    These raise here, naming the point, rather than project nothing, a frame the contract
    does not have, or one that no value of a Reference defines, each checked in this order:

    * ``issue_age_min`` that is not a whole number, 0 or more, below ``2**53``: an age,
      which a NaN would switch off, every comparison with it failing, and which the
      compiled model holds as a ``long long``;
    * a covered life issued below ``issue_age_min``, 0, the youngest age
      :mod:`~.PA_UK_S` projects: it projects any age on the scenario basis, so no
      product-spec age bounds a contract here;
    * ``omega_age`` that is not a whole number below ``2**53``, or not above
      ``issue_age_min``: the limiting age sizes every frame, and a NaN, an infinity or a
      fraction of a year would leave the frame's months no whole number;
    * ``omega_age_max`` that is not a whole number below ``2**53``;
    * on the table basis, a covered life of a sex the mortality table lacks
      (:func:`mort_schedule`), and ``omega_age`` more than a year past the last age the
      table rates that sex at, ``Data.mort_age_last`` of its schedule, plus 1, since the
      table is read at attained ages to ``omega_age - 1``; and then an ``omega_age`` above
      ``omega_age_max``, the contract's largest limiting age, 116, the shipped table's last
      age plus one, so that every limiting age the shipped table admits projects, and a
      longer table's runs no frame past the caches (UKLIB-SEC-PLAN.md §6.6, *Record --
      M10*).  The scenario basis reads no table, and the in-force step projected it at any
      limiting age, so the bound is not asked there (the Space docstring);
    * a guarantee longer than ``12 x (omega_age - issue_age_min)`` months, the longest
      frame from the start date that the youngest life allows, which the compiled
      model's caches are sized from;
    * a point at or past the stop rule, which an in-force extract should not carry;
    * a contract that owes nothing after the valuation date: in payment, its guarantee
      over, and every covered life dead, so that no instalment, no dependant's income and
      no value-protection lump sum is left to pay.  Its last payment was made before the
      valuation date;
    * one read under a Reference outside its domain, each named.  NaN and the infinities
      are outside every one: :mod:`~.PA_UK_S` reads several of them through a ``min`` or a
      ``max`` whose bound comes first, which keeps the bound where a NaN meets it, so that
      the NaN is lost rather than carried, or through a power.  On every point:

      - ``expense_maint``, a finite number, 0 or more: an expense;
      - ``inflation_rate``, a finite number, -1 or more: below -1 the inflation factor,
        ``(1 + pi)^(t // 12)``, changes sign each year;

      on the table basis, which reads the mortality References:

      - ``annuitant_adj``, a finite number, 0 or more: below 0 a mortality rate is
        negative, and an infinity reads through the cap as certain death;
      - ``improve_rate_base``, a finite number below 1: the improvement factor raises
        ``1 - f`` to a power, which at or below 0 has no real value or changes sign;
      - ``improve_flat_age`` and ``improve_taper_age``, finite numbers, the ages the
        scale is flat to and tapers to 0 at;
      - ``mort_table_year``, a whole number below ``2**53``, a calendar year the
        improvement counts from;

      on ``fixed`` escalation:

      - ``esc_fixed_cap``, a finite number, 0 or more: the cap a NaN would switch off,
        every comparison with it failing;

      on RPI-linked escalation, ``lpi5`` and ``rpi_catchup``:

      - ``rpi_rate``, a finite number above -1: the index, ``(1 + rpi_rate)^a``, is a
        price level, above 0, and the LPI floor, ``max(0, rpi_rate)``, its bound first,
        would read a NaN as no increase;

      and on ``lpi5``:

      - ``esc_lpi_cap``, a finite number, 0 or more: the cap, ``min(cap, ...)``, its
        bound first, which an infinity would switch off.

    The rules read this Space's References, which ``Data`` cannot see, so they are checked
    here.  They are the contract a compiled model's caches are sized from: a frame of at
    most ``omega_age_max - issue_age_min`` years and the future horizon (``spec_sec.py``).
    Every report reads this cell first, so no point outside them is projected.  Each check
    is a comparison written out, a finite bound the largest float, 1.7976931348623157e308,
    and a whole one ``2**53``, so that a compiled cell runs it in C, and each Reference is
    printed as the compiled model types it: ``issue_age_min``, ``omega_age``,
    ``omega_age_max`` and ``mort_table_year`` through ``int()`` once they are whole numbers,
    and every other through ``float()``; the two improvement ages ship as floats, 90.0 and
    110.0, so that the compiled model holds a fraction as modelx reads it.  A value a
    formula computes past the floats, from References and columns each in its domain, is
    refused in the cell where it first is: the income, in :func:`annual_income` and
    :func:`annual_income_init`; the payments to date, in :func:`cum_annuity_pp` and
    :func:`cum_annuity_all`; the three powers, :func:`inflation_factor`, :func:`rpi_index`
    and :func:`improve_factor`; and the maintenance, in :func:`expenses`.  On the scenario
    basis an ``omega_age`` above ``omega_age_max`` is not refused, as the in-force step
    refused none, and in the compiled model a frame longer than the caches raises a bare
    ``IndexError`` where modelx projects (the Space docstring).  ``omega_age_max`` or
    ``Data.future_horizon_mth`` raised needs the caches derived again and the model rebuilt;
    ``issue_age_min`` cannot go below 0, the first rule above.
    """
    if not (issue_age_min > -9007199254740992.0                       # noqa: F821
            and issue_age_min < 9007199254740992.0                    # noqa: F821
            and issue_age_min == issue_age_min // 1):                 # noqa: F821
        raise ValueError(f"point_id {point_id()}: issue_age_min must be a whole number "
                         f"below 2**53, not {float(issue_age_min)}")  # noqa: F821
    if issue_age_min < 0:                                            # noqa: F821
        raise ValueError(f"point_id {point_id()}: issue_age_min must be 0 or more, "
                         f"not {int(issue_age_min)}")                # noqa: F821
    for life in range(1, 3 if is_joint() else 2):
        if age_at_entry(life) < issue_age_min:                       # noqa: F821
            raise ValueError(
                f"point_id {point_id()}: life {life}'s issue age, {age_at_entry(life)}, "
                f"is below issue_age_min, {int(issue_age_min)}")     # noqa: F821
    if not (omega_age > -9007199254740992.0                           # noqa: F821
            and omega_age < 9007199254740992.0                        # noqa: F821
            and omega_age == omega_age // 1):                         # noqa: F821
        raise ValueError(f"point_id {point_id()}: omega_age must be a whole number "
                         f"below 2**53, not {float(omega_age)}")     # noqa: F821
    if not omega_age > issue_age_min:                                # noqa: F821
        raise ValueError(f"point_id {point_id()}: omega_age must be above issue_age_min, "
                         f"{int(issue_age_min)}, not {int(omega_age)}")  # noqa: F821
    if not (omega_age_max > -9007199254740992.0                       # noqa: F821
            and omega_age_max < 9007199254740992.0                    # noqa: F821
            and omega_age_max == omega_age_max // 1):                 # noqa: F821
        raise ValueError(f"point_id {point_id()}: omega_age_max must be a whole number "
                         f"below 2**53, not {float(omega_age_max)}")  # noqa: F821
    if not is_scenario():
        for life in range(1, 3 if is_joint() else 2):
            last = data.mort_age_last()[mort_schedule(life)]         # noqa: F821
            if omega_age > last + 1:                                 # noqa: F821
                raise ValueError(
                    f"point_id {point_id()}: omega_age must be at most {int(last) + 1}, a "
                    f"year past mort_table.csv's last age, on the table basis, not "
                    f"{int(omega_age)}")                             # noqa: F821
        if omega_age > omega_age_max:                                # noqa: F821
            raise ValueError(f"point_id {point_id()}: omega_age, {int(omega_age)}, is "
                             f"above omega_age_max, {int(omega_age_max)}, on the table "
                             f"basis")                               # noqa: F821
    longest = 12 * (omega_age - issue_age_min)                       # noqa: F821
    if guarantee_mths() > longest:
        raise ValueError(
            f"point_id {point_id()}: the guarantee, {guarantee_mths()} months, is longer "
            f"than {int(longest)} months, 12 x (omega_age - issue_age_min), the longest "
            f"frame from the start date")
    d = duration_mth_init()
    n = stop_mth() - d
    if n <= 0:
        raise ValueError(
            f"point_id {point_id()}: duration_mth {d} is at or past the end of the "
            f"projection, policy month {stop_mth()}")
    if (d > 0 and d >= guarantee_mths() and not lives_if_init(1) > 0.0
            and not (is_joint() and lives_if_init(2) > 0.0)):
        if guarantee_mths() > 0:
            raise ValueError(
                f"point_id {point_id()}: duration_mth {d}: no payment is owed after the "
                f"valuation date: every covered life has died, and the guarantee ended "
                f"at policy month {guarantee_mths()}")
        raise ValueError(
            f"point_id {point_id()}: duration_mth {d}: no payment is owed after the "
            f"valuation date: every covered life has died, and the contract has no "
            f"guarantee")
    if not (expense_maint >= 0.0                                     # noqa: F821
            and expense_maint <= 1.7976931348623157e308):             # noqa: F821
        raise ValueError(f"point_id {point_id()}: expense_maint must be a finite number, "
                         f"0 or more, not {float(expense_maint)}")   # noqa: F821
    if not (inflation_rate >= -1.0                                   # noqa: F821
            and inflation_rate <= 1.7976931348623157e308):            # noqa: F821
        raise ValueError(f"point_id {point_id()}: inflation_rate must be a finite number, "
                         f"-1 or more, not {float(inflation_rate)}")  # noqa: F821
    if not is_scenario():
        if not (annuitant_adj >= 0.0                                 # noqa: F821
                and annuitant_adj <= 1.7976931348623157e308):         # noqa: F821
            raise ValueError(f"point_id {point_id()}: annuitant_adj must be a finite "
                             f"number, 0 or more, not {float(annuitant_adj)}")  # noqa: F821
        if not (improve_rate_base >= -1.7976931348623157e308          # noqa: F821
                and improve_rate_base < 1.0):                         # noqa: F821
            raise ValueError(f"point_id {point_id()}: improve_rate_base must be a finite "
                             f"number below 1, not {float(improve_rate_base)}")  # noqa: F821
        if not (improve_flat_age >= -1.7976931348623157e308           # noqa: F821
                and improve_flat_age <= 1.7976931348623157e308):      # noqa: F821
            raise ValueError(f"point_id {point_id()}: improve_flat_age must be a finite "
                             f"number, not {float(improve_flat_age)}")  # noqa: F821
        if not (improve_taper_age >= -1.7976931348623157e308          # noqa: F821
                and improve_taper_age <= 1.7976931348623157e308):     # noqa: F821
            raise ValueError(f"point_id {point_id()}: improve_taper_age must be a finite "
                             f"number, not {float(improve_taper_age)}")  # noqa: F821
        if not (mort_table_year > -9007199254740992.0                 # noqa: F821
                and mort_table_year < 9007199254740992.0              # noqa: F821
                and mort_table_year == mort_table_year // 1):         # noqa: F821
            raise ValueError(f"point_id {point_id()}: mort_table_year must be a whole "
                             f"number below 2**53, not {float(mort_table_year)}")  # noqa: F821
    if is_fixed():
        if not (esc_fixed_cap >= 0.0                                 # noqa: F821
                and esc_fixed_cap <= 1.7976931348623157e308):         # noqa: F821
            raise ValueError(f"point_id {point_id()}: esc_fixed_cap must be a finite "
                             f"number, 0 or more, not {float(esc_fixed_cap)}")  # noqa: F821
    if is_lpi5() or is_rpi_catchup():
        if not (rpi_rate > -1.0 and rpi_rate <= 1.7976931348623157e308):  # noqa: F821
            raise ValueError(f"point_id {point_id()}: rpi_rate must be a finite number "
                             f"above -1, not {float(rpi_rate)}")     # noqa: F821
    if is_lpi5():
        if not (esc_lpi_cap >= 0.0                                   # noqa: F821
                and esc_lpi_cap <= 1.7976931348623157e308):           # noqa: F821
            raise ValueError(f"point_id {point_id()}: esc_lpi_cap must be a finite "
                             f"number, 0 or more, not {float(esc_lpi_cap)}")  # noqa: F821
    return n


def is_payment_pm(k):
    """Whether policy month k is a payment month: the schedule, on the policy clock.

    ``k`` counts months from the start date.  Arrears: the instalment falls at the *end*
    of the month, so ``k = 2, 5, 8, ...`` at m = 4.  Advance: the j-th instalment
    (j = 1, 2, ...) falls one full payment period earlier, at the start of policy month
    ``12(j-1)/m``, so ``k = 0, 3, 6, ...``  At m = 12 every month is a payment month on
    either convention.  The one definition of the payment months: :func:`is_payment_mth`
    asks it at the policy month of month t, and :func:`annuity_pp_pm` at any policy month,
    so that the payments to date read the schedule without passing a policy month as
    ``t``.  False before the start date.
    """
    if k < 0:
        return False
    step = 12 // payment_freq()
    if is_arrears():
        return (k + 1) % step == 0
    return k % step == 0


def is_payment_mth(t):
    """Whether month t is a payment date: ``is_payment_pm(duration_mth(t))``, in the frame.

    The schedule is the contract's, on the policy clock (:func:`is_payment_pm`): a contract
    in payment 17 months that pays quarterly in arrears pays in policy months 17, 20, ...,
    so at ``t = 0, 3, ...``.  False outside the frame.
    """
    return is_active(t) and is_payment_pm(duration_mth(t))


def payment_surv_mth(t):
    """s(t): the **time point** at which survival is measured for month t's instalment.

    A time point on the valuation clock, where :func:`lives_if` is indexed.  Arrears: the
    end of month t, which is time ``t + 1``.  Advance: the start of month t, which is time
    ``t``, because an advance instalment falls at the *start* of the month; for the first
    instalment of a contract starting at the valuation date that is time 0, where
    ``lives_if`` is 1.  Using end-of-period survival for advance payments understates the
    liability by about one period's mortality per payment.
    """
    return t + 1 if is_arrears() else t


def rpi_index(a):
    """I(a): the RPI reference level at anniversary a, relative to the latest index.

    ``(1 + rpi_rate)^(a - a0)``, ``a0 = policy_year_init() - 1`` the anniversary that
    opened the policy year under way at the valuation date, so 1 there.  ``a`` is an
    **anniversary count** from the start date - one step per policy year, 0 at outset -
    not the month-scale time point the state cells take.  ``rpi_rate`` is the RPI from the
    valuation date on, a flat **[std]** rate; the index before ``a0`` is history this model
    does not need, its ratchet's state being carried in :func:`rpi_peak_init`, and no cell
    reads it.  On a point starting at the valuation date ``a0`` is 0, and this is
    :mod:`~.PA_UK_S`'s ``(1 + rpi_rate)^a``, bit for bit.  A deterministic path cannot value
    the zero floor, the catch-up ratchet or the LPI cap - all of them inflation options -
    and values them at intrinsic only; a market-consistent value needs stochastic
    inflation.  :func:`proj_len` holds ``rpi_rate`` above -1, where the level stays above 0.

    A level past the largest float, which only an ``rpi_rate`` past every rate of inflation
    makes, is refused at the anniversary it first is, naming the point and the Reference.
    Python's float power raises ``OverflowError`` there, naming neither, where C's ``pow``
    gives an infinity; so where the power is infinite from a finite base the cell calls
    Python's own, uslib's M22 form (USLIB-SEC-PLAN.md, *Record -- M22*), which raises the
    same ``OverflowError`` in the compiled model as in modelx, and the one ``except``
    around both turns it into the refusal, in either engine.  modelx never reaches the
    call, its own power raising first.
    """
    base = 1.0 + rpi_rate                                            # noqa: F821
    n = a - (policy_year_init() - 1)
    try:
        index = base ** n
        if index - index != 0.0 and base - base == 0.0:
            raise float.__pow__(base, n)
    except OverflowError:
        raise ValueError(
            f"point_id {point_id()}: the index rpi_index({a}) is past the largest float, "
            f"under rpi_rate {float(rpi_rate)}") from None            # noqa: F821
    if not index <= 1.7976931348623157e308:
        raise ValueError(
            f"point_id {point_id()}: the index rpi_index({a}) is past the largest float, "
            f"under rpi_rate {float(rpi_rate)}")                      # noqa: F821
    return index


def rpi_peak(a):
    """The running maximum of the RPI reference index through anniversary a, relative.

    Indexed by the same **anniversary count** as :func:`rpi_index`, and relative to the
    same latest index.  The catch-up ratchet's state, and it is **path-dependent**: it must
    persist across anniversaries.  Its base is the opening state, :func:`rpi_peak_init`, at
    ``a0 = policy_year_init() - 1``, where :mod:`~.PA_UK_S`'s is ``I(0)`` at outset, and it
    runs forward from there; on a point starting at the valuation date the two are one,
    and this is :mod:`~.PA_UK_S`'s, bit for bit.  Resetting it each year turns the catch-up
    into a plain zero floor and overstates indexed income after a deflation-recovery path.
    """
    if a <= policy_year_init() - 1:
        return rpi_peak_init()
    return max(rpi_peak(a - 1), rpi_index(a))


def annual_income(y):
    """A(y): the annualized income in policy year y, on the annuitant's scale.

    Escalation applies at the start of the month containing the policy anniversary, so
    the first increase reaches policy month 12 and not the month-11 arrears instalment,
    which accrued in year 1.  By basis::

        level:        A(y) = A(1)
        fixed:        A(y) = A(y-1)(1 + g)
        lpi5:         A(y) = A(y-1)(1 + min(esc_lpi_cap, max(0, RPI)))
        rpi_catchup:  A(y) = A(y0) x peak(y-1) / peak(y0-1)

    based at ``y0 = policy_year_init()``, the year under way at the valuation instant, on
    :func:`annual_income_init`: RPI-linked, the income history gave, read from the model
    point; fixed, the schedule compounded by one loop; so a contract valued late in life
    reads its income without recursing back to the start date, and a year after ``y0``
    escalates at the valuation date's References.  The catch-up form is the closed version
    of the ratchet pseudocode, measured from the peak carried in.  On a point starting at
    the valuation date ``y0`` is 1 and every year is :mod:`~.PA_UK_S`'s, bit for bit; a
    year before ``y0`` is history, which no cell reads.  An income that is not a finite
    number, which only a rate or a peak past every amount of money makes, is refused in
    the year it first is, naming the References, where the payments to date would carry it
    on: by :func:`annual_income_refusal`, since the cell recurses by the year, and a
    compiled chain holds a C frame of each cell it recurses through, with the code of every
    message it formats, whether its branch runs or not.
    """
    if y <= 1:
        return annual_income_first()
    if is_level():
        return annual_income_first()
    if y == policy_year_init():
        return annual_income_init()
    if is_fixed():
        income = annual_income(y - 1) * (1.0 + escalation_rate())
    elif is_lpi5():
        step = min(esc_lpi_cap, max(0.0, rpi_rate))                  # noqa: F821
        income = annual_income(y - 1) * (1.0 + step)
    else:
        income = annual_income_init() * rpi_peak(y - 1) / rpi_peak_init()
    if not income <= 1.7976931348623157e308:
        return annual_income_refusal(y)
    return income


def annual_income_refusal(y):
    """The refusal of an income past the floats in policy year y, :func:`annual_income`'s,
    in a cell of its own.

    :func:`annual_income` recurses by the year, and a compiled chain holds a frame of each
    cell it recurses through at each level, with the code of every message the cell
    formats, so it calls this cell only where the income it computes is not a finite
    number, and the message is formatted in this cell's frame, which no chain holds on a
    run that does not raise.  It takes the year alone, as the cell does: it computes the
    income as :func:`annual_income` does, from the same cells, the same float, and refuses
    it where it is not a finite number, naming the References of its basis, in
    :func:`annual_income`'s words at stage ``E``.  Where it is finite, it returns it, as
    the sample asks for it in every year, to type the cell; so it answers a year
    :func:`annual_income` answers without computing, the first, a level income's and
    ``y0``'s, as :func:`annual_income` does.
    """
    if y <= 1:
        return annual_income_first()
    if is_level():
        return annual_income_first()
    if y == policy_year_init():
        return annual_income_init()
    if is_fixed():
        income = annual_income(y - 1) * (1.0 + escalation_rate())
        if not income <= 1.7976931348623157e308:
            raise ValueError(
                f"point_id {point_id()}: the income annual_income({y}) is {income}, not "
                f"a finite number, under escalation_rate {escalation_rate()}")
        return income
    if is_lpi5():
        step = min(esc_lpi_cap, max(0.0, rpi_rate))                  # noqa: F821
        income = annual_income(y - 1) * (1.0 + step)
        if not income <= 1.7976931348623157e308:
            raise ValueError(
                f"point_id {point_id()}: the income annual_income({y}) is {income}, not "
                f"a finite number, under rpi_rate {float(rpi_rate)} and esc_lpi_cap "  # noqa
                f"{float(esc_lpi_cap)}")                              # noqa: F821
        return income
    income = annual_income_init() * rpi_peak(y - 1) / rpi_peak_init()
    if not income <= 1.7976931348623157e308:
        raise ValueError(
            f"point_id {point_id()}: the income annual_income({y}) is {income}, not a "
            f"finite number, under rpi_rate {float(rpi_rate)}, annual_income_init "  # noqa
            f"{annual_income_init()} and rpi_peak_init {rpi_peak_init()}")
    return income


def annuity_pp_pm(k):
    """The scheduled instalment per contract in policy month k: ``A(y)/m`` or 0.

    ``y = k // 12 + 1`` the policy year containing policy month ``k``.  Keyed by policy
    month, on the policy clock, so that :func:`cum_annuity_pp` reads the schedule at
    policy months before month t without passing a policy month as ``t``;
    :func:`annuity_pp` is this at the policy month of month t.  0 outside payment months
    and before the start date.
    """
    if not is_payment_pm(k):
        return 0.0
    return annual_income(k // 12 + 1) / payment_freq()


def annuity_pp(t):
    """inst(t) = A(y(t))/m: the scheduled instalment per contract in month t.

    ``annuity_pp_pm(duration_mth(t))`` inside the frame, and 0 outside it and outside
    payment months.  This is the *annuitant's* instalment; the dependant's is ``delta``
    times it, on the same escalated income, which is what the contractual "percentage of
    the higher of income at death and at guarantee end" reduces to under a non-decreasing
    escalation path.
    """
    if not is_active(t):
        return 0.0
    return annuity_pp_pm(duration_mth(t))


def next_payment_mth(t):
    """The **policy month** of the next scheduled payment at or after month t; -1 if none.

    A closed form on the policy clock, where :mod:`~.PA_UK_S` scans month by month: from
    policy month ``k = duration_mth(t)``, the next arrears payment falls at
    ``k + (step - 1 - k % step)`` and the next advance one at ``k + (step - k % step) %
    step``, ``step = 12 / m``.  -1 where that falls at or past the stop rule, as
    :mod:`~.PA_UK_S`'s scan stops at the end of its frame, and outside the frame.  The
    sentinel is -1 rather than 0 because month 0 is a payment month like any other.  A
    policy month, as :mod:`~.PA_UK_S`'s is, never a month of the frame: on arrears it falls
    in the policy year of month t, so the proportion rule's instalment is ``A(y(t))/m``.
    """
    if not is_active(t):
        return -1
    k = duration_mth(t)
    step = 12 // payment_freq()
    if is_arrears():
        nxt = k + (step - 1 - k % step)
    else:
        nxt = k + (step - k % step) % step
    if nxt >= stop_mth():
        return -1
    return nxt


def mths_since_payment(t):
    """h(t): complete months elapsed since the last payment date, measured at time t.

    On the policy clock: time t is the start of month t, policy time ``k =
    duration_mth(t)``, and the last payment date at or before it is ``(k // step) x step``,
    ``step = 12/m``, so a death in month t accrues from there.  The accrual base of the
    proportionate final payment: on the worked configuration a death in policy month 16
    with quarterly arrears payments at months 2, 5, ... gives h = 1, one complete month
    since the month-14 instalment, whatever ``t`` policy month 16 falls at.  0 outside the
    frame.
    """
    if not is_active(t):
        return 0
    k = duration_mth(t)
    step = 12 // payment_freq()
    if k <= 0:
        return 0
    last = (k // step) * step
    return max(0, k - last)


def mort_rate_base_at(x, life):
    """The base-table annual mortality rate at attained age ``x``, for ``life``'s sex.

    The one cell that reads ``mort_table.csv``, keyed by age and life, so that the monthly
    cells call it rather than join the table themselves.  The sex is the join key:
    :func:`mort_schedule` gives ``life``'s row of ``Data.mort_table_array``, refusing a sex
    the table lacks, and the age is its column, and the label accessor itself is left to
    reporting.  Called only below the limiting age, where :func:`mort_rate_base` returns 1
    without calling here, and only inside the frame, which :func:`mort_rate_base` asks
    first.  The age is checked against the schedule's first and last ages,
    ``Data.mort_age_first`` and ``Data.mort_age_last``, the sex's own, before the array is
    read, so an age outside them raises ``ValueError``, naming the point and the age, where
    :mod:`~.PA_UK_S`'s lookup raised ``KeyError``: an annuitant issued younger than the table
    rates, on the table basis.  The padding is never read.
    """
    s = mort_schedule(life)
    if x < data.mort_age_first()[s] or x > data.mort_age_last()[s]:  # noqa: F821
        raise ValueError(f"point_id {point_id()}: mort_table.csv has no rate at "
                         f"attained age {x}")
    return float(data.mort_table_array()[s, x])                      # noqa: F821


def mort_rate_base(t, life):
    """The base-table annual mortality rate for ``life`` in the year containing month t.

    Population mortality, times the **[std]** annuitant adjustment that stands in for
    the difference between a population table and the licensed annuitant tables.  Rates
    at and above the limiting age are 1, and the table is read below it, at the attained
    age :func:`age` gives, through :func:`mort_rate_base_at`, the one reader of the table,
    which this cell asks only inside the frame.  Zero outside the frame, where the contract
    has no attained age to look up.
    """
    if not is_active(t):
        return 0.0
    x = age(t, life)
    if x >= omega_age:                                               # noqa: F821
        return 1.0
    return mort_rate_base_at(x, life) * annuitant_adj                # noqa: F821


def improve_rate(t, life):
    """f(x): the annual mortality improvement rate at ``life``'s attained age **[std]**.

    A flat rate to age 90, tapering linearly to zero at 110 and zero above it.  This
    stands in for the CMI Mortality Projections Model, whose software is restricted, and
    it **materially understates** the age-period-cohort structure of the real model - it
    exists only so the reference implementation is runnable without CMI access.  The
    choice of long-term improvement rate is the single most sensitive judgment in UK
    annuity valuation, and the CMI model carries no default recommendation for it.  Zero
    outside the frame, where the contract has no attained age.
    """
    if not is_active(t):
        return 0.0
    x = age(t, life)
    if x <= improve_flat_age:                                        # noqa: F821
        return improve_rate_base                                     # noqa: F821
    if x >= improve_taper_age:                                       # noqa: F821
        return 0.0
    span = improve_taper_age - improve_flat_age                      # noqa: F821
    return improve_rate_base * (improve_taper_age - x) / span        # noqa: F821


def improve_factor(t, life):
    """(1 - f(x))^(c - c0): the cumulative improvement factor for ``life`` in month t.

    ``c`` is the calendar year containing month t, on the policy clock
    (:func:`calendar_year`), and ``c0`` the base table's data mid-year, so the basis is
    **generational**: each attained age in each future calendar year carries its own
    improved rate, and a contract in payment reads the calendar years it reaches, whatever
    the valuation date.  Zero outside the frame, before the calendar year is read.

    A factor past the largest float, which a negative rate far below any improvement makes,
    or a rate near 1 with ``mort_table_year`` years after the contract's, is refused in the
    month it first is, naming the point and the References.  Python's float power raises
    ``OverflowError`` there, naming neither, where C's ``pow`` gives an infinity; so where
    the power is infinite from a finite base the cell calls Python's own, uslib's M22 form,
    and the one ``except`` around both turns it into the refusal, in either engine, as
    :func:`rpi_index` does.
    """
    if not is_active(t):
        return 0.0
    k = calendar_year(t) - mort_table_year                           # noqa: F821
    rate = improve_rate(t, life)
    base = 1.0 - rate
    try:
        factor = base ** k
        if factor - factor != 0.0 and base - base == 0.0:
            raise float.__pow__(base, k)
    except OverflowError:
        raise ValueError(
            f"point_id {point_id()}: the improvement factor improve_factor({t}, {life}) is "
            f"past the largest float, (1 - {rate}) to the power {int(k)}, under "
            f"improve_rate_base {float(improve_rate_base)} and mort_table_year "  # noqa: F821
            f"{int(mort_table_year)}") from None                      # noqa: F821
    if not factor <= 1.7976931348623157e308:
        raise ValueError(
            f"point_id {point_id()}: the improvement factor improve_factor({t}, {life}) is "
            f"past the largest float, (1 - {rate}) to the power {int(k)}, under "
            f"improve_rate_base {float(improve_rate_base)} and mort_table_year "  # noqa: F821
            f"{int(mort_table_year)}")                                # noqa: F821
    return factor


def mort_rate(t, life):
    """q_rated: the annual mortality rate applied to ``life`` in the year containing t.

    The notes' construction, in order::

        q_base  = ONS-shaped table rate x alpha
        q_imp   = q_base x (1 - f(x))^(c - c0)
        q_rated = min(theta x q_imp, 1)

    Every one of the three factors is a standardization: the table is a population
    proxy, the improvement scale a stand-in for a restricted model, and the rating
    multiplier the simplest form of an unpublished structure.  The liability is a
    life-contingent stream with no offsetting decrements, so the level of this rate is
    the single largest lever on it.  The cap puts its float bound second,
    ``min(q, 1.0)``, as :mod:`~.PA_UK_S` does, so that a missing input, a NaN, stays NaN,
    where ``min(1.0, q)`` would read it as 1.  Compiled, the cap is a comparison of two
    doubles that keeps the product unless the bound is smaller.  Zero outside the frame.
    """
    if not is_active(t):
        return 0.0
    q = mort_rate_base(t, life) * improve_factor(t, life)
    return min(rating_factor(life) * q, 1.0)


def mort_rate_mth(t, life):
    """q_m = 1 - (1 - q_rated)^(1/12): the monthly mortality rate **[std]**."""
    return 1.0 - (1.0 - mort_rate(t, life)) ** (1.0 / 12.0)


def lives_if(t, life):
    """l(t): the probability that ``life`` is alive **at time t**.

    Indexed by a **time point** on the valuation clock, not by a month: time ``t`` is the
    start of month ``t``, so month t opens at time ``t`` and closes at time ``t + 1``, and
    time 0 is the valuation date.  The argument is named ``t``, as the valuation clock's;
    :mod:`~.PA_UK_S` names its own ``k``, the same reading on its one clock.

    At :func:`t_entry`, the first time point on the books, it is the opening state,
    :func:`lives_if_init`: the life's status at the valuation date for a contract in
    payment, and 1, its value at the start date, for one starting at or after it.  Before
    that it is 0: the contract is not yet on the books.  After it, on the *table* basis,
    ``l(t) = l(t-1)(1 - q_m(t-1))``: the rate of month ``t - 1``, the month that has just
    closed, deaths being decremented at end of month.  On the *scenario* basis **[std]**
    the survival path is the step function ``1{duration_mth(t) <= death_mth}`` on the
    policy clock, with ``death_mth = -1`` meaning the life survives the whole projection -
    which is what the notes' worked example specifies; ``Data`` holds the opening status
    to the same step, so the two agree at :func:`t_entry`.  The annuitant dying in policy
    month 16 reads ``lives_if(17, 1) = 0`` on a point starting at the valuation date, as in
    the notes, and ``lives_if(0, 1) = 0`` on a point in payment 17 months.  Returns 0 for
    life = 2 on a single-life contract.

    On the table basis, at a time point that opens a policy year after :func:`t_entry`,
    survival is the year's opening, :func:`lives_if_py`, which is ``l(t-1)(1 - q_m(t-1))``,
    the same product in the same order, bit for bit: the recursion blocked by policy year
    (UKLIB-SEC-PLAN.md K12), so that a cold read runs one cell a month back to its year's
    first time point and two cells a year from there, where one cell a month back to
    :func:`t_entry` would run the contract's longest cover, 1,392 months at its largest
    limiting age, on the compiled model's C stack.
    """
    if life == 2 and not is_joint():
        return 0.0
    if t < t_entry():
        return 0.0
    if t == t_entry():
        return lives_if_init(life)
    if is_scenario():
        d = death_mth(life)
        return 0.0 if (d >= 0 and duration_mth(t) > d) else 1.0
    if duration_mth(t) % 12 == 0:
        return lives_if_py(policy_year(t), life)
    return lives_if(t - 1, life) * (1.0 - mort_rate_mth(t - 1, life))


def lives_if_py(y, life):
    """l at the start of policy year y: the survival policy year y - 1 closes on.

    The survival recursion blocked by policy year, as K12 of UKLIB-SEC-PLAN.md blocks a
    long chain whose margin on the stack is gone, in ``ULB_UK_SEC``'s form: it walks the
    time points of policy year ``y - 1`` on the books in ascending order, from the later of
    :func:`t_entry` and the year's first, asking :func:`lives_if` of each, so that each
    finds the time point before cached and none runs a chain, and returns survival across
    the year's last month, ``l(last)(1 - q_m(last))``, the inline step of :func:`lives_if`,
    bit for bit.  So the values are :func:`lives_if`'s own, and the chain of a cold read is
    one cell a month within its year and two cells a year before it: :func:`lives_if` of
    the year's first time point on the books, and the opening of the year before that.

    :func:`lives_if` reads it on the table basis at a time point that opens policy year
    ``y``, after :func:`t_entry` and up to the frame's closing time point, ``t =
    proj_len()``, so ``y`` runs from 2 to the policy year of that point, 117 at the
    contract's longest cover, 1,392 months from issue at ``issue_age_min``, 0, to its
    largest limiting age, ``omega_age_max``, 116 (``spec_sec.py``); no other cell reads
    it.
    """
    d = duration_mth_init()
    first = max(t_entry(), 12 * (y - 2) - d)
    last = 12 * (y - 1) - 1 - d
    for s in range(first, last):
        lives_if(s, life)
    return lives_if(last, life) * (1.0 - mort_rate_mth(last, life))


def lives_death(t, life):
    """d(t) = l(t) - l(t+1): the death density of ``life`` in month t.

    Month t runs from time t to time ``t + 1``, and :func:`lives_if` is indexed by time,
    so the density is the fall in survival across it.  Zero outside the frame.
    """
    if not is_active(t):
        return 0.0
    return lives_if(t, life) - lives_if(t + 1, life)


def lives_if_last(t):
    """The probability that at least one covered life is alive at time t.

    ``l_a + l_d - l_a l_d`` under **joint-life independence [std]**, which ignores
    broken-heart dependence and common lifestyle factors and so modestly overstates the
    expected dependant stream.  On a single-life contract this is ``l_a``.  A time-point
    cells on the valuation clock, like :func:`lives_if`, and 0 before the contract is on
    the books.
    """
    la = lives_if(t, 1)
    if not is_joint():
        return la
    ld = lives_if(t, 2)
    return la + ld - la * ld


def lives_death_last(t):
    """d_last(t): the last-death density in month t, the last-survivor VP trigger.

    Zero outside the frame.
    """
    if not is_active(t):
        return 0.0
    return lives_if_last(t) - lives_if_last(t + 1)


def certain_floor(t):
    """C(t) = 1{duration_mth(t) < n}: the annuity-certain floor indicator of the guarantee.

    ``n`` is a **count** of guaranteed months from the start date, so the guarantee
    covers policy months ``0 ... n - 1``: a 10-year guarantee is ``duration_mth(t) < 120``,
    and the floor is gone from policy month 120, whatever ``t`` it falls at.  The months of
    it left at the valuation date are therefore no opening state: they follow from
    ``duration_mth``.  Zero outside the frame.
    """
    if not is_active(t):
        return 0.0
    return 1.0 if duration_mth(t) < guarantee_mths() else 0.0


def payment_factor_life(t):
    """l_a measured at the payment point: the annuitant's survival factor alone.

    Survival is measured at :func:`payment_surv_mth`, the payment point - the end of the
    payment month (time ``t + 1``) on arrears and the start of it (time ``t``) on
    advance.  Zero outside the frame.
    """
    if not is_active(t):
        return 0.0
    return lives_if(payment_surv_mth(t), 1)


def payment_factor(t):
    """max(C(t), l_a): the annuitant stream's payment factor.

    The ``max`` makes the guarantee period an annuity-**certain floor** rather than an
    additional stream: during the guarantee the full instalment is payable regardless of
    survival, escalating as if the annuitant were alive, and the ``max`` prevents paying
    ``1 + l_a``.  An additive construction silently doubles the guarantee, which is the
    notes' first-listed pitfall.
    """
    return max(certain_floor(t), payment_factor_life(t))


def overlap_gate(t):
    """w(t) = 1{overlap or duration_mth(t) >= n}: the dependant's stream available in t.

    1 with overlap, or once the guarantee period has run, on the policy clock; 0 inside the
    guarantee without overlap.  **Not** a decrement of any kind - there is no lapse on this
    product - which is why it is not called a rate.  Applying the dependant's percentage
    from the death date on a without-overlap contract silently converts it into the more
    expensive with-overlap form.  Zero outside the frame.
    """
    if not is_active(t):
        return 0.0
    if overlap() or duration_mth(t) >= guarantee_mths():
        return 1.0
    return 0.0


def dependant_factor(t):
    """delta (1 - l_a) l_d w(t): the dependant stream's payment factor.

    The dependant is paid when the annuitant is dead and the dependant alive, gated by
    the overlap rule, both survivals measured at the payment point.  Zero on a
    single-life contract and outside the frame.
    """
    if not is_joint() or not is_active(t):
        return 0.0
    s = payment_surv_mth(t)
    return (dependant_pct() * (1.0 - lives_if(s, 1)) * lives_if(s, 2)
            * overlap_gate(t))


def cum_annuity_all(t):
    """G_all(t): the expected instalments paid per contract on every stream by time t.

    Indexed by a **time point** on the valuation clock, as the survival that weights it
    is: the annuitant's instalments with their guarantee floor and the dependant's, of
    every month that has closed by time ``t``.  At :func:`t_entry` it is the opening state,
    :func:`cum_annuity_all_init`, the payments made before the valuation date, path-
    dependent, and 0 on a contract starting at or after it; then ``G_all(t) = G_all(t-1) +
    inst(t-1) [max(C, l_a) + delta (1 - l_a) l_d w](t-1)``, :mod:`~.PA_UK_S`'s ``"ALL"``
    recursion in its order, one cell a month.  0 before the contract is on the books.
    This is the column the notes' worked-example table prints, and the balance the
    last-survivor basis nets against.  A total past the floats, which only an income near
    the largest float makes, is refused where it first is, naming the month, by
    :func:`cum_annuity_all_refusal`, since a compiled chain holds a frame of each cell it
    recurses through, with the code of every message it formats.
    """
    if t < t_entry():
        return 0.0
    if t == t_entry():
        return cum_annuity_all_init()
    if duration_mth(t) % 12 == 0:
        total = cum_annuity_all_py(policy_year(t))
    else:
        paid = annuity_pp(t - 1) * (payment_factor(t - 1) + dependant_factor(t - 1))
        total = cum_annuity_all(t - 1) + paid
    if not total <= 1.7976931348623157e308:
        return cum_annuity_all_refusal(t)
    return total


def cum_annuity_all_py(y):
    """G_all at the start of policy year y: the payments to date policy year y - 1 closes
    on.

    The payments to date blocked by policy year, as :func:`lives_if_py` blocks survival:
    it walks the time points of policy year ``y - 1`` on the books in ascending order,
    asking :func:`cum_annuity_all` of each, so that each finds the time point before
    cached, and returns the total across the year's last month, ``G_all(last) +
    inst(last) [max(C, l_a) + delta (1 - l_a) l_d w](last)``, the inline step of
    :func:`cum_annuity_all`, bit for bit; :func:`cum_annuity_all` refuses it where it is not
    a finite number.  :func:`cum_annuity_all` reads it at a time point that opens policy
    year ``y`` after :func:`t_entry`, so ``y`` runs from 2 to 117 at the contract's longest
    cover, as :func:`lives_if_py`'s does; no other cell reads it.
    """
    d = duration_mth_init()
    first = max(t_entry(), 12 * (y - 2) - d)
    last = 12 * (y - 1) - 1 - d
    for s in range(first, last):
        cum_annuity_all(s)
    paid = annuity_pp(last) * (payment_factor(last) + dependant_factor(last))
    return cum_annuity_all(last) + paid


def cum_annuity_all_refusal(t):
    """The refusal of the payments to date on every stream past the floats at time t,
    :func:`cum_annuity_all`'s, in a cell of its own.

    :func:`cum_annuity_all` recurses month by month, so it formats no message itself: it
    calls this cell only where the total it computes is not a finite number, and the
    message is formatted in this cell's frame, which no chain holds on a run that does not
    raise.  It takes the time point alone, computes the total as :func:`cum_annuity_all`
    does, from the same cells, the same float, and refuses it, naming the point and the
    time, in :func:`cum_annuity_all`'s words at stage ``E``.  Where it is finite, it
    returns it, as the sample asks for it at every time point, to type the cell.
    """
    if t <= t_entry():
        return cum_annuity_all(t)
    paid = annuity_pp(t - 1) * (payment_factor(t - 1) + dependant_factor(t - 1))
    total = cum_annuity_all(t - 1) + paid
    if not total <= 1.7976931348623157e308:
        raise ValueError(
            f"point_id {point_id()}: the payments to date cum_annuity_all({t}) are "
            f"{total}, not a finite number")
    return total


def cum_annuity_pp(k, kind):
    """G(k): cumulative instalments per contract up to time point k, by ``kind``.

    Indexed by a **time point** on the **policy** clock: ``k`` months after the start
    date, ``G(0) = 0``, and ``G(k)`` sums the instalments of policy months ``0 ... k - 1``,
    so the instalment of policy month ``m`` enters at ``G(m + 1)`` whether it falls at the
    month's start or at its end.  That index does not move with the valuation date, which
    is why the notes' ``G(16) = 6,790.50`` reads unchanged on a point in payment 17
    months as on its twin.  ``kind`` is an int code (the Space docstring's *Codes*):

    ``ANNUITANT``
        the **deterministic as-if-alive** annuitant schedule, which the first-death
        value-protection balance nets against.  ``G(k) = G(k-1) + inst(k-1)``,
        :mod:`~.PA_UK_S`'s recursion, based where the valuation date falls, at the policy
        time point ``max(duration_mth_init(), 0)``, a static key: on level and fixed
        escalation one loop there sums the schedule before it, the same additions in the
        same order as the recursion, so ``G`` is :mod:`~.PA_UK_S`'s to the last bit; on
        RPI-linked escalation the instalments before it followed the RPI of their day,
        which no flat rate re-derives, so the base is the opening state,
        :func:`cum_annuity_pp_init`.  Later keys recurse back to the base, and a contract
        valued late in life reads its balance without recursing back to the start date.
        A total past the floats, which only an income near the largest float makes, is
        refused where it first is, by :func:`cum_annuity_pp_refusal`, since the cell
        recurses month by month and a compiled chain holds a frame of each cell it recurses
        through, with the code of every message it formats.

    ``ALL``
        the same plus the expected dependant instalments and the guaranteed ones, weighted
        by survival: :func:`cum_annuity_pp_all`, which reads :func:`cum_annuity_all`, on
        the valuation clock, at the time point ``k - duration_mth_init()`` there, and
        refuses a key before the valuation date's.

    Any other kind raises, as :mod:`~.PA_UK_S`'s does.
    """
    if k <= 0:
        return 0.0
    if kind == ANNUITANT:                                            # noqa: F821
        if k == max(duration_mth_init(), 0):
            if is_lpi5() or is_rpi_catchup():
                return cum_annuity_pp_init()
            total = 0.0
            for j in range(k):
                total += annuity_pp_pm(j)
        elif k % 12 == 0:
            total = cum_annuity_pp_py(k // 12 + 1)
        else:
            total = cum_annuity_pp(k - 1, kind) + annuity_pp_pm(k - 1)
        if not total <= 1.7976931348623157e308:
            return cum_annuity_pp_refusal(k)
        return total
    if kind == ALL:                                                  # noqa: F821
        return cum_annuity_pp_all(k)
    raise ValueError("invalid kind")


def cum_annuity_pp_py(y):
    """G at policy time ``12 (y - 1)``, the start of policy year y: the annuitant's
    as-if-alive instalments policy year y - 1 closes on.

    ``cum_annuity_pp(k, ANNUITANT)`` blocked by policy year, as :func:`lives_if_py` blocks
    survival: it walks the keys of policy year ``y - 1`` in ascending order, asking
    :func:`cum_annuity_pp` of each, so that each finds the key before cached, and returns
    the total across the year's last policy month, ``G(last) + inst(last)``, the inline
    step of :func:`cum_annuity_pp`, bit for bit; :func:`cum_annuity_pp` refuses it where it
    is not a finite number.  The walk starts at the year's first key, or where the
    valuation date's key, the static base ``max(duration_mth_init(), 0)``, falls inside
    the year, at the base, below which the payments to date are the loop's or the opening
    state's.  :func:`cum_annuity_pp` reads it at a key that opens a policy year, other than
    the base, so ``y`` runs from 2 to 117, the policy year of the stop rule's key, 1,392 at
    the contract's longest cover; no other cell reads it.
    """
    base = max(duration_mth_init(), 0)
    first = 12 * (y - 2)
    if first < base < 12 * (y - 1):
        first = base
    last = 12 * (y - 1) - 1
    for j in range(first, last):
        cum_annuity_pp(j, ANNUITANT)                                 # noqa: F821
    return cum_annuity_pp(last, ANNUITANT) + annuity_pp_pm(last)     # noqa: F821


def cum_annuity_pp_refusal(k):
    """The refusal of the annuitant's payments to date past the floats at policy time k,
    ``cum_annuity_pp(k, ANNUITANT)``'s, in a cell of its own.

    As :func:`cum_annuity_all_refusal` is :func:`cum_annuity_all`'s: it computes the total
    as :func:`cum_annuity_pp` does at ``ANNUITANT``, from the same cells, the same float,
    and refuses it where it is not a finite number, naming the point and the key, in
    :func:`cum_annuity_pp`'s words at stage ``E``; where it is finite, it returns it, as the
    sample asks for it at every key, to type the cell.
    """
    if k <= 0:
        return 0.0
    if k == max(duration_mth_init(), 0):
        if is_lpi5() or is_rpi_catchup():
            return cum_annuity_pp_init()
        total = 0.0
        for j in range(k):
            total += annuity_pp_pm(j)
    else:
        total = cum_annuity_pp(k - 1, ANNUITANT) + annuity_pp_pm(k - 1)  # noqa: F821
    if not total <= 1.7976931348623157e308:
        raise ValueError(
            f"point_id {point_id()}: the payments to date cum_annuity_pp({k}, "
            f"'ANNUITANT') are {total}, not a finite number")
    return total


def cum_annuity_pp_all(k):
    """``cum_annuity_pp(k, ALL)``: the expected payments on every stream by policy time k.

    :func:`cum_annuity_all`, which runs on the valuation clock, read at the time point
    ``k - duration_mth_init()`` there, so that the notes' printed column keeps its name on
    the policy clock.  The payments before the valuation date are the opening state's,
    held as one total, so a key before the valuation date's, which no cell asks, raises,
    naming the point and the key.  A cell of its own, apart from :func:`cum_annuity_pp`,
    which recurses month by month and so formats no message.
    """
    if k < duration_mth_init():
        raise ValueError(
            f"point_id {point_id()}: cum_annuity_pp({k}, 'ALL') is before the "
            f"valuation date, policy time {duration_mth_init()}, where the payments "
            f"to date are cum_annuity_all_init, one total")
    return cum_annuity_all(k - duration_mth_init())


def vp_balance(t):
    """VPbal(t) = max(0, v P - G): the value-protection balance at time t.

    Indexed by a **time point** on the valuation clock.  Nets the payments the elected
    basis applies to: on ``first_death`` the annuitant's as-if-alive schedule,
    ``cum_annuity_pp(duration_mth(t), ANNUITANT)``, read at the policy time point of time
    ``t``; on ``last_survivor`` the expected payments on both streams,
    :func:`cum_annuity_all` at ``t``.  Zero when value protection is not elected, and
    before the contract is on the books.
    """
    if vp_pct() <= 0.0 or t < t_entry():
        return 0.0
    if is_first_death():
        paid = cum_annuity_pp(duration_mth(t), ANNUITANT)            # noqa: F821
    else:
        paid = cum_annuity_all(t)
    return max(0.0, vp_pct() * purchase_price() - paid)


def annuity_payments(t):
    """E[ANN(t)]: expected annuity outgo in month t.

    ``inst(t) x [max(C(t), l_a) + delta (1 - l_a) l_d w(t)]``, on the contracts on the
    books, ``pols_if_at(t, BEF_DECR)``: the annuitant stream with its guarantee floor,
    plus the dependant's stream.
    """
    return (pols_if_at(t, BEF_DECR) * annuity_pp(t)                  # noqa: F821
            * (payment_factor(t) + dependant_factor(t)))


def claims(t, kind):
    """Expected lump-sum outgo in month t, by ``kind``, an int code; ``ALL`` the total.

    ``VP``
        the value-protection lump sum, ``d(t) x VPbal``.  The trigger is the
        annuitant's death on the ``first_death`` basis and the last death on
        ``last_survivor``.  The balance is measured at time ``t`` - the start of
        the death month - on arrears timing, because the instalment due at the
        end of that month is never paid; in an **advance** payment month it is
        measured at time ``t + 1``, because an instalment paid at the start of
        the death month has been paid and netting it is what keeps the lump sum
        from being overstated by one instalment.

    ``PROP``
        the proportionate final payment on an arrears contract that elects it:
        ``d_a(t) x (h(t) + 0.5)/(12/m) x inst(next(t))``, a **[std]** half-month
        accrual for the part-period between the last payment date and the death.
        On arrears the next payment falls in the policy year of month t, so
        ``inst(next(t))`` is ``A(policy_year(t))/m``, read in closed form, where
        :mod:`~.PA_UK_S` reads it at the month its scan finds; zero where the next
        payment falls past the stop rule.  Zero on the representative default,
        where nothing is paid for the final partial period.

    ``ALL``
        the total, which :mod:`~.PA_UK_S` spells ``claims(t)``, its ``kind`` defaulted
        to ``None``, with Python's ``sum``: here ``0.0 + claims(t, VP) + claims(t,
        PROP)``, written left to right, which is ``sum``'s float wherever at most two
        kinds are non-zero in a month, and there are only two (USLIB-SEC-PLAN.md R12).
        The twin identity reaches :mod:`~.PA_UK_S`'s ``(t, None)`` through the spec's
        ``twin_arg_map``.

    Each on the contracts on the books, ``pols_if_at(t, BEF_DECR)``, and zero outside
    the frame.  Any other kind raises, as :mod:`~.PA_UK_S`'s does.
    """
    if kind == ALL:                                                  # noqa: F821
        return 0.0 + claims(t, VP) + claims(t, PROP)                 # noqa: F821
    if kind == VP:                                                   # noqa: F821
        if not is_active(t) or vp_pct() <= 0.0:
            return 0.0
        density = lives_death(t, 1) if is_first_death() else lives_death_last(t)
        measured_at = t + 1 if (not is_arrears() and is_payment_mth(t)) else t
        return pols_if_at(t, BEF_DECR) * density * vp_balance(measured_at)  # noqa: F821
    if kind == PROP:                                                 # noqa: F821
        if not is_active(t) or not proportion():
            return 0.0
        if next_payment_mth(t) < 0:
            return 0.0
        accrual = (mths_since_payment(t) + 0.5) / (12.0 / payment_freq())
        instalment = annual_income(policy_year(t)) / payment_freq()
        return (pols_if_at(t, BEF_DECR) * lives_death(t, 1) * accrual  # noqa: F821
                * instalment)
    raise ValueError("invalid kind")


def pols_if(t):
    """IF(t): contracts with a payment obligation still open in month t.

    ``pols_if_at(t, BEF_DECR) x min(1, max(C(t), l_a(t+1)) + 1{delta>0}(1 - l_a(t+1))
    l_d(t+1))`` **[std]** - guarantee certain, annuitant alive, or dependant stream in
    payment, survival taken at the *end* of month t (time ``t + 1``), on the contracts on
    the books.  This is the weight the maintenance expense is carried on, which is why it
    keeps the library's name for the expense weight even though it is a closing measure
    rather than the count that weights row t: on the twins of :mod:`~.PA_UK_S`'s points 2,
    6 and 7, ``pols_if(0)`` is 0.99999965 against a count of 1.0, as in :mod:`~.PA_UK_S`,
    and the registry marks the model ``closing_pols_if`` for that reason.  The dependant's
    leg is dropped where there is no dependant's pension, ``delta`` 0.  Zero outside the
    frame.
    """
    if not is_active(t):
        return 0.0
    la = lives_if(t + 1, 1)
    obligation = max(certain_floor(t), la)
    if dependant_pct() > 0.0:
        obligation += (1.0 - la) * lives_if(t + 1, 2)
    return pols_if_at(t, BEF_DECR) * min(1.0, obligation)            # noqa: F821


def pols_if_at(t, timing):
    """Contracts on the books at time t, at the instant ``timing`` names.

    ``BEF_NB``
        The contracts carried in from month t - 1, before month t's annuities start: at
        :func:`t_entry`, the first month on the books, :func:`pols_if_init`, the count in
        payment at the valuation date (0 for a point starting at or after it), and the
        whole ``policy_count()`` after it.  Zero outside the frame, so the contracts leave
        the books at the stop rule, at the end of the last projected month.
    ``BEF_DECR``
        ``BEF_NB`` plus :func:`pols_new_biz`: the count that weights every cash flow
        of month t.

    These are ``basiclife.BasicTerm_SE``'s names, int codes (the Space docstring's
    *Codes*), compared by ``==`` alone, and any other timing raises, a string among them in
    modelx.  The count is not decremented: mortality decrements each life's survival,
    :func:`lives_if`, and every cash flow is this count times a per-contract amount
    weighted by survival, as :mod:`~.PA_UK_S` weights its flows by the constant
    ``pols_if_init``.  A count weighted by survival could not carry the two lives'
    independent probabilities.  So ``BEF_NB`` is a closed form, the same float that the
    recursion ``BEF_NB(t-1) + pols_new_biz(t-1)`` gives, with no chain of calls back to
    :func:`t_entry`.  :func:`pols_if` is not ``BEF_DECR``: it is the notes' closing
    obligation measure on this count.
    """
    if timing == BEF_NB:                                             # noqa: F821
        if not is_active(t):
            return 0.0
        if t == t_entry():
            return pols_if_init()
        return policy_count()
    elif timing == BEF_DECR:                                         # noqa: F821
        return pols_if_at(t, BEF_NB) + pols_new_biz(t)               # noqa: F821
    else:
        raise ValueError("invalid timing")


def pols_new_biz(t):
    """Annuities starting in month t: ``policy_count()`` in the month of the start date.

    The month with ``duration_mth(t) == 0``: ``t = 0`` for a point whose start date is the
    valuation date, ``t = k`` for one starting ``k`` months later.  A contract already in
    payment at the valuation date has none.  New business in ``basiclife.BasicTerm_SE``'s
    sense, a contract entering the books, with no premium and no acquisition cost: the
    purchase price is a pricing input, as in :mod:`~.PA_UK_S`.
    """
    return policy_count() if duration_mth(t) == 0 else 0.0


def inflation_factor(t):
    """The expense inflation factor in month t: ``(1 + pi)^(t // 12)`` **[std]**.

    On the **valuation** clock: :mod:`~.PA_UK_S`'s annual steps, ``(1 + pi)^(y - 1)``,
    moved onto ``t``, so that the maintenance charge it inflates is in valuation-date
    pounds, whatever the contract's age, and every point of a block inflates alike,
    stepping on each anniversary of the valuation date.  On a point starting at ``t = 0``
    the two are the same.

    The exponent is a whole number of years, 0 or more, so the power is real whatever the
    base, and :func:`proj_len` holds the base to 0 or more.  A factor past the largest
    float, which only an ``inflation_rate`` past every rate of inflation makes, is refused
    in the month it first is, naming the point and the Reference.  Python's float power
    raises ``OverflowError`` there, naming neither, where C's ``pow`` gives an infinity; so
    where the power is infinite from a finite base the cell calls Python's own, uslib's M22
    form, and the one ``except`` around both turns it into the refusal, in either engine,
    as :func:`rpi_index` does.
    """
    base = 1.0 + inflation_rate                                      # noqa: F821
    n = t // 12
    try:
        factor = base ** n
        if factor - factor != 0.0 and base - base == 0.0:
            raise float.__pow__(base, n)
    except OverflowError:
        raise ValueError(
            f"point_id {point_id()}: the inflation factor inflation_factor({t}) is past the "
            f"largest float, under inflation_rate {float(inflation_rate)}") from None  # noqa
    if not factor <= 1.7976931348623157e308:
        raise ValueError(
            f"point_id {point_id()}: the inflation factor inflation_factor({t}) is past the "
            f"largest float, under inflation_rate {float(inflation_rate)}")  # noqa: F821
    return factor


def expenses(t):
    """E[EXP(t)]: maintenance expense in month t **[std]**.

    ``(c_e / 12)(1 + pi)^(t // 12) IF(t)``: a round placeholder for in-payment
    administration, paid monthly while any payment obligation remains, inflating on the
    valuation clock (:func:`inflation_factor`).  No insurer publishes expense assumptions -
    charges are priced into the annuity rate - and acquisition cost is out of scope, the
    premium being single and the cost priced in, so an annuity starting after the
    valuation date brings none either.  Second-order against the instalments, but the
    in-payment term is thirty years or more, so the inflation assumption compounds.  An
    expense past the largest float, which only an ``expense_maint`` and an inflation
    factor near it make, is refused in the month it first is, naming the References,
    where ``liability_cf`` and ``net_cf`` would carry an infinity on.
    """
    cost = expense_maint / 12.0 * inflation_factor(t) * pols_if(t)   # noqa: F821
    if not cost <= 1.7976931348623157e308:
        raise ValueError(
            f"point_id {point_id()}: the expense expenses({t}) is {cost}, not a finite "
            f"number, under expense_maint {float(expense_maint)} and inflation_rate "  # noqa
            f"{float(inflation_rate)}")                               # noqa: F821
    return cost


def liability_cf(t):
    """CF(t): total gross liability outgo in month t, the notes' cash flow definition.

    ``E[ANN] + E[PROP] + E[VP] + E[EXP]``.  **Outgo positive**, the notes' own sign.
    There is no premium income in the projection - the purchase price is a pricing input
    paid at outset, before the first projected month - and no surrender outgo, because
    the contract has no surrender value at any time.
    """
    return annuity_payments(t) + claims(t, ALL) + expenses(t)        # noqa: F821


def net_cf(t):
    """Net cash flow to the insurer in month t: income less outgo, so ``-liability_cf``.

    **Income positive**, the sign convention every model in this library carries, kept
    even though this product has no projected income so that every model's ``net_cf``
    can be compared or summed across the library.  :func:`liability_cf` carries the
    opposite, outgo-positive sign of the technical notes; both are published as columns
    of :func:`result_cf` rather than one being made to stand for the other.
    """
    return -liability_cf(t)


def check_lives_roll_fwd_resid(t):
    """Residual between :func:`lives_if` and an independently rebuilt survival path.

    Indexed by a **time point** on the valuation clock, like :func:`lives_if` itself:
    time 0 is the valuation date and the residual is checked over ``t = 0 ...
    proj_len()``, the opening and closing time of every projected month.  It is zero
    before the contract is on the books, where both sides are 0.

    Deliberately **not** the telescoping identity ``l(t) - d(t) - l(t+1)``:
    :func:`lives_death` is *defined* as that difference, so the identity is identically
    zero whatever :func:`lives_if` returns and constrains nothing.  Each life's survival to
    time t is rebuilt here from the opening state and the assumptions instead, with no
    reference to the recursion - on the *table* basis as :func:`lives_if_init` times the
    running product ``prod (1 - q_m(s))`` over the months ``s = t_entry() ... t - 1`` that
    have closed since the contract came on the books, which a misindexed or mis-based
    recursion breaks; on the *scenario* basis as the step function on the policy clock -
    and the residual is the sum of the per-life differences.
    """
    res = 0.0
    entry = t_entry()
    scenario = is_scenario()
    for i in range(1, 3):
        if i == 2 and not is_joint():
            continue
        if t < entry:
            built = 0.0
        elif scenario:
            d = death_mth(i)
            built = 0.0 if (d >= 0 and duration_mth(t) > d) else 1.0
        else:
            built = lives_if_init(i)
            for s in range(entry, t):
                built *= 1.0 - mort_rate_mth(s, i)
        res += built - lives_if(t, i)
    return res


def check_lives_roll_fwd():
    """Whether the survival recursion closes at **every** projected time point.

    Takes no argument and returns a ``bool``, the library-wide shape of a ``check_*``
    cells, so one test can call the same check across every model.  :func:`lives_if` is
    a time-point cells, so the sweep runs over ``t = 0 ... proj_len()``: the valuation date
    through the close of the last projected month.  The signed residual of a failing time
    point stays available as :func:`check_lives_roll_fwd_resid`.
    """
    return all(abs(check_lives_roll_fwd_resid(k)) < 1e-10
               for k in range(proj_len() + 1))


def check_payment_factor_resid(t):
    """``payment_factor(t) - max(C(t), l_a)``: the guarantee double-count guard.

    Zero by construction.  It is asserted anyway because an additive floor - ``C + l_a``
    instead of ``max(C, l_a)`` - is the notes' first-listed pitfall and would show up
    here as ``min(C, l_a)``.
    """
    return payment_factor(t) - max(certain_floor(t), payment_factor_life(t))


def check_payment_factor():
    """Whether the guarantee stays a floor rather than a second stream, at every month."""
    return all(abs(check_payment_factor_resid(t)) < 1e-10
               for t in range(proj_len()))


def check_guarantee_xor():
    """Whether the contract carries at most one of a guarantee period and value protection.

    The representative design offers one or the other, never both.  An engine supporting
    the combinable variant would have to net guarantee payments off the value-protection
    balance, or the death benefit is paid twice - so the exclusivity is asserted rather
    than assumed.
    """
    return not (guarantee_mths() > 0 and vp_pct() > 0.0)


def check_vp_bound():
    """Whether ``v + delta <= 1`` on the first-death value-protection basis.

    A contractual bound, and the worked configuration sits exactly on it.  It does not
    apply on the last-survivor basis, where the two benefits cannot both be triggered by
    the same death.
    """
    if vp_pct() <= 0.0 or not is_first_death():
        return True
    return vp_pct() + dependant_pct() <= 1.0 + 1e-12


def result_cf():
    """Result table of cashflows, one row per month ``t = 0 ... proj_len() - 1``.

    Row 0 is the valuation month for every model point, so the frames of a block line up
    and sum row by row; a point starting after the valuation date has zeros until the month
    its annuity starts.  The columns are :mod:`~.PA_UK_S`'s.  ``pols_if`` is the contracts
    with any payment obligation remaining, which is the expense weight rather than the
    count on the books.  Both signs of the net flow are published: ``net_cf`` is
    income-positive, the library-wide convention, and ``liability_cf`` is the technical
    notes' outgo-positive ``CF(t)``.
    """
    ts = list(range(proj_len()))
    return pd.DataFrame(                                             # noqa: F821
        {
            "pols_if": [pols_if(t) for t in ts],
            "annuity_payments": [annuity_payments(t) for t in ts],
            "claims_vp": [claims(t, VP) for t in ts],                # noqa: F821
            "claims_prop": [claims(t, PROP) for t in ts],            # noqa: F821
            "expenses": [expenses(t) for t in ts],
            "liability_cf": [liability_cf(t) for t in ts],
            "net_cf": [net_cf(t) for t in ts],
        },
        index=pd.Index(ts, name="t"),                                # noqa: F821
    )


def result_pols():
    """Result table of the counts, survival probabilities and payment factors, by month t.

    One row per projected month, ``t = 0 ... proj_len() - 1``: ``pols_if``, the closing
    obligation measure, and ``pols_new_biz``, the annuities starting in the month, as
    ``basiclife.BasicTerm_SE``'s ``result_pols`` sets its counts out first; then
    :mod:`~.PA_UK_S`'s other columns in :mod:`~.PA_UK_S`'s order.  The state columns are
    read at the **end** of month t, i.e. at time ``t + 1``: ``lives_if_1``,
    ``lives_if_2``, ``cum_annuity_all`` and ``vp_balance`` are the closing values of the
    month whose flows the same row of :func:`result_cf` carries, and every column is 0 in
    the months before a point's annuity starts.  The count on the books that weights the
    cash flows is not a column: it is the table's ``policy_count``, from the start date to
    the stop rule.
    """
    ts = list(range(proj_len()))
    return pd.DataFrame(                                             # noqa: F821
        {
            "pols_if": [pols_if(t) for t in ts],
            "pols_new_biz": [pols_new_biz(t) for t in ts],
            "lives_if_1": [lives_if(t + 1, 1) if is_active(t) else 0.0 for t in ts],
            "lives_if_2": [lives_if(t + 1, 2) if is_active(t) else 0.0 for t in ts],
            "certain_floor": [certain_floor(t) for t in ts],
            "payment_factor": [payment_factor(t) for t in ts],
            "dependant_factor": [dependant_factor(t) for t in ts],
            "annuity_pp": [annuity_pp(t) for t in ts],
            "cum_annuity_all": [cum_annuity_all(t + 1) if is_active(t) else 0.0
                                for t in ts],
            "vp_balance": [vp_balance(t + 1) if is_active(t) else 0.0 for t in ts],
        },
        index=pd.Index(ts, name="t"),                                # noqa: F821
    )


# ---------------------------------------------------------------------------
# References

data = ("Interface", ("..", "Data"), "auto")

idx = 0

BEF_NB = 0

BEF_DECR = 1

VP = 0

PROP = 1

ANNUITANT = 2

ALL = 3

issue_age_min = 0

omega_age = 115

omega_age_max = 116

mort_table_year = 2023

annuitant_adj = 0.8

improve_rate_base = 0.0125

improve_flat_age = 90.0

improve_taper_age = 110.0

rpi_rate = 0.03

esc_fixed_cap = 0.1

esc_lpi_cap = 0.05

expense_maint = 30.0

inflation_rate = 0.03

pd = ("Module", "pandas")
