# modelx: pseudo-python
# This file is part of a modelx model.
# It can be imported as a Python module, but functions defined herein
# are model formulas and may not be executable as standard Python.

"""The by-policy projection of the :mod:`~.CI_UK_SEC` model; holds all formulas.

The Space is parameterized by ``idx``, the position of a model point in the table and in
every :mod:`~.CI_UK_SEC.Data` vector, as ``basiclife.BasicTerm_SC`` is: ``Projection[8]``
is an ItemSpace projecting the table's ninth row, model point 9, the reviewable point
valued on its first review, and :func:`point_id` is its label::

    >>> Projection[8].result_cf()          # one row per month from the valuation date
    >>> Projection[8].result_pols()        # the counts behind it
    >>> Projection[8].point_id()           # 9, the row's point_id
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

This is :mod:`~.CI_UK_S` taught to run in force at a valuation date, as lifelib's
``basiclife.BasicTerm_SE`` extends ``basiclife.BasicTerm_S``, and then made to compile, as
``basiclife.BasicTerm_SC`` is made from ``basiclife.BasicTerm_S``. A formula of
:mod:`~.CI_UK_S` is rewritten where it depends on where the projection starts, where it
must answer for a month outside cover, or where it read a policy month as ``t``; every
other formula is :mod:`~.CI_UK_S`'s own, its caps on the diagnosis rate, on each life's
claim rate, on the policy's and on the standalone paid rate, each ``min(q, 1.0)``, among
them. ``products/critical_illness/model-sec.md`` lists the rewritten cells with the reason
for each. Making it compile changed how each cell reads its inputs and spells its codes,
and no number: every model point attribute a projection cell uses is read as a number from
a ``Data`` vector, every table as an array indexed by integers, the pivot interpolation
made once in ``Data`` at every attained age the contract admits, every timing and kind is
an int code (*Codes*, below), and every text column is decoded into the number a formula
branches on.

.. rubric:: Input data

Inputs are **external files**: plain CSVs living in the model folder's parent
directory, ``products/critical_illness/``, read at run time rather than stored inside
the model. The model folder therefore holds nothing but formulas — no ``_data/``, no
IOSpec, no embedded values — so a diff of the model shows logic changes only, and an
input can be edited or swapped without rewriting the model. This follows
``annuallife.TradLife_A``; contrast ``basiclife.BasicTerm_S``, which keeps its inputs
*inside* the model through modelx's IOSpec machinery.

The consequence worth knowing: **the model is not portable on its own.** Copying the
``CI_UK_SEC`` folder without its parent's CSVs produces a model that reads and then
fails on first evaluation.

:func:`~.CI_UK_SEC.Data.input_dir` resolves the directory from ``_model.path.parent``
at run time, so the model works wherever the repository is checked out. The two
assumption tables are the files :mod:`~.CI_UK_S` reads, read in place; the model point
table is this model's own. Each table has a filename Reference and a reader Cells, both
on :mod:`~.CI_UK_SEC.Data`, reached here through the ``data`` Reference:

======================  ==============================  ==========================
Reference               Cells                           File
======================  ==============================  ==========================
model_point_file        data.model_point_table()        model_point_table_sec.csv
ci_rate_file            data.ci_rate_table()            ci_rate_table.csv
lapse_table_file        data.lapse_table()              lapse_table.csv
======================  ==============================  ==========================

No cell here but :func:`model_point`, a reporting cell, reads the readers' DataFrames,
and the label accessors read through it. Every other reads :mod:`~.CI_UK_SEC.Data`'s
vectors and arrays, one element at a time: a model point's attribute at its position,
``data.age_at_entry()[idx]``, decoded already into the number the formula needs; the pivot
rates at a life's row and attained age,
``data.i_ci_array()[rate_group(life), age(t, life)]``, interpolated in ``Data`` by
:mod:`~.CI_UK_S`'s own rule; and the lapse table at the policy year. ``Data``'s docstring
lists them.

.. rubric:: Two clocks

``t`` counts months from the **valuation date**, 0-based, the clock
``basiclife.BasicTerm_SE`` runs on: ``t = 0`` is the valuation month for every model
point, however old the policy, month ``t`` runs from time ``t`` to time ``t + 1``, and the
frame is ``t = 0 .. proj_len() - 1``, where :func:`proj_len` counts the months from the
valuation date to the end of the term. Row ``t`` is the same month for every point, so the
frames of a block line up and sum row by row.

``duration_mth(t)`` counts **policy months**, the months the policy has been in force at
time ``t``: ``duration_mth(t) = duration_mth_init() + t``, where
:func:`duration_mth_init` is read from the model point — positive for a policy in force at
the valuation date, 0 for one issued at it, ``-k`` for one issued ``k`` months later, at
most ten years later. Everything contractual reads it: the completed policy years
``duration(t) = duration_mth(t) // 12``, the contractual 1-based label
``policy_year(t) = duration(t) + 1``, the attained age
``age(t, life) = age_at_entry(life) + duration(t)``, and through them the pivot rates, the
lapse table, the indexation anniversaries, the five-yearly premium reviews and the
twelve-month shock window after each, and the end of cover. Model point 9, the reviewable
point valued on its first review, is in policy year 6 at attained age 45 at ``t = 0`` and
has 240 months of cover left.

Two inputs read the valuation clock instead, both from the valuation date on, for every
point alike: expense inflation, ``inflation_factor(t) = (1 + inflation_rate) ** (t //
12)``, so that the maintenance charge is in valuation-date pounds, and the morbidity
trend, ``ci_trend_factor(t) = (1 + ci_trend) ** (t // 12)``, a calendar trend on the
diagnosis basis, which the table states at the valuation date. The initial expense is
charged per policy issued, in the issue month, and not inflated, as in
``basiclife.BasicTerm_SE``.

On a point issued at ``t = 0`` the two clocks coincide and this model computes what
:mod:`~.CI_UK_S` computes: every cell the two share agrees at every argument
:mod:`~.CI_UK_S` evaluates in its sweep, but for those whose meaning changed —
``pols_if_init``, now the count already in force at the valuation date, and
``model_point``, a row of another table. ``tests/test_model_conventions_uk.py`` asserts it
cell by cell.

.. rubric:: Counts

``pols_if(t)`` is the count that weights row ``t``: ``pols_if_at(t, BEF_DECR)``, the
count carried in from ``t - 1`` (``BEF_NB``) plus the month's new business,
:func:`pols_new_biz`, before the month's decrements. A point in force at the valuation
date opens with :func:`pols_if_init`, its ``policy_count``; one issued at or after the
valuation date opens with none, and takes its ``policy_count`` as new business in its
issue month. The recursion's base is :func:`t_entry`, the first month on the books, and
nothing is counted outside cover (:func:`is_active`): before issue every count, and so
every cash flow, is zero. :mod:`~.CI_UK_S`'s three timings are kept, ``BEF_DECR``,
``BEF_LAPSE`` and ``AFT_DECR``, and ``BEF_NB`` is the one running in force adds.

.. rubric:: The opening state

A point in force carries, beside its count, the facts of its contract that
:mod:`~.CI_UK_S` would recompute from flat References, each a factor or a rate, so that the
count is the one weight on every flow, and each measured at the valuation instant, the
start of month 0, before any month-0 event:

* :func:`idx_factor_init` and :func:`idx_prem_factor_init`, the indexation factors
  entering month 0, the RPI increases given before it: on an anniversary, those of the
  policy year it closes;
* :func:`review_prem_factor_init`, the premium factor the reviews made before month 0 have
  given: on a review month, that of the review period it closes;
* :func:`ci_sel_latched_init`, the select latch, 1 once a review before month 0 has
  shocked lapses and 0 before, and :func:`ci_sel_factor_init`, the anti-selection factor
  on the diagnosis rate it closed at, read only while it is closed: a latch closed at a
  loading of 0 holds a factor of 1, and stays closed;
* :func:`review_prem_shock_init`, the premium change the last review before month 0
  made, which sets the shock lapse of its twelve-month window, read only while that
  window is still running.

Each is read from the model point, never recomputed from a Reference, which is an
assumption from the valuation date on: ``review_prem_shock`` is the premium change at
each review from the valuation instant on, and ``rpi_rate`` the RPI from it. An event
that falls at the valuation date itself is month 0's, the projection's first, made at the
References of the valuation date, as on a point issued then (USLIB-SEC-PLAN.md D6,
precised at its M7): on a point valued on its anniversary, that anniversary's RPI increase
is made at ``rpi_rate``; on one valued in a review month, that review is made at
``review_prem_shock``, opens its window at that change, and closes the select latch at
``1 + sel_lapse_ci_loading`` if the change passes ``review_lapse_threshold``, each of the
valuation date; and the columns hold the state before it.

.. rubric:: Codes

What :mod:`~.CI_UK_S` spells as text, a timing or a kind, is here an int Reference
named as the text it replaces, so that every cell takes and returns C numbers. A call
site reads as it did, less the quotes: ``pols_if_at(t, BEF_DECR)``, ``claims(t, AP)``.

=============  =====  ===========================================================
Reference      Value  Meaning
=============  =====  ===========================================================
BEF_NB         0      :func:`pols_if_at`: the count carried in from month t - 1
BEF_DECR       1      :func:`pols_if_at`: that count plus month t's new business
BEF_LAPSE      2      :func:`pols_if_at`: after the month's main claims, before its
                      lapses
AFT_DECR       3      :func:`pols_if_at`: the end of the month, after its decrements
MAIN           0      :func:`benefit_pp`, :func:`claims`: the main, terminating benefit
AP             1      :func:`benefit_pp`, :func:`claims`: the additional payment
CHILD          2      :func:`benefit_pp`, :func:`claims`: children's cover
LAPSE          3      :func:`claims`: the lapse benefit, nil by product design
ALL            4      :func:`claims`: the four kinds' total
=============  =====  ===========================================================

A code a cell takes indexes that cell's cache, a C array of four timings a month for
:func:`pols_if_at` and five kinds a month for :func:`benefit_pp` and :func:`claims`, so
codes are numbered densely from 0. Timings are numbered in the order of their instants
within the month, ``BEF_NB`` before ``BEF_DECR``, as in every SEC model, then
:mod:`~.CI_UK_S`'s two others in its processing order; kinds in :func:`result_cf`'s
order, the order :mod:`~.CI_UK_S` adds them in its total, and then ``ALL``, which is
:mod:`~.CI_UK_S`'s ``kind=None``. :func:`benefit_pp` takes the three benefits alone,
``MAIN`` to ``CHILD``. A code a cell does not take raises, ``invalid timing`` or
``invalid kind``. They are References, not cells, so the symbol map below does not list
them.

.. rubric:: Reporting cells

:func:`model_point`, the label accessors :func:`contract_type`, :func:`life_basis`,
:func:`cover_basis`, :func:`premium_guarantee`, :func:`premium_mode`, :func:`sex` and
:func:`smoker`, and the reports :func:`result_cf` and :func:`result_pols` return Python
values, a table row, text and DataFrames, for a reader and for the comparison with
:mod:`~.CI_UK_S`, which has every one of them but :func:`result_pols`. No cell but these
calls a label accessor or a report: every other reads the number ``Data`` decoded from the
same column instead, the contract's, the life basis's and the guarantee's flags and each
life's row of the pivot rates. So they stay Python when the model compiles, and every
other cell returns a C ``bint``, ``long long`` or ``double``. The two checks,
:func:`check_pols_roll_fwd` and :func:`check_claim_split`, are reporting cells too, which
no cell calls, and each compiles to a ``bint``, a verdict over residual cells that
compile.

.. rubric:: Naming

Cells names follow lifelib's ``basiclife.BasicTerm_S`` and ``savings.CashValue_SE``
wherever those models have an analogue — ``pols_*`` for policy counts, plural nouns for
cash flows, ``*_rate`` for annual rates and ``*_rate_mth`` for monthly ones, ``*_pp``
for per-policy amounts, ``claims(t, kind)`` and ``benefit_pp(t, kind)`` with a
``kind`` code, ``pols_if_at(t, timing)`` for the within-month in-force reads. What
running in force adds is named as ``basiclife.BasicTerm_SE`` names it: ``duration_mth``
read from the model point, ``policy_count``, ``pols_new_biz``, ``pols_if_at``'s
``BEF_NB`` timing, ``is_active`` and ``result_pols``.
``duration_mth_init``, the policy months completed at the valuation date, takes
``UL_US_S``'s name; ``t_entry``, ``expiry_mth``, ``review_prem_factor`` and
``review_prem_change`` are this model's own, and each opening-state cell is the cell it
opens with ``_init`` added, ``review_prem_shock_init`` the Reference's and
``ci_sel_latched_init`` the latch's. What compiling adds is named as
``basiclife.BasicTerm_SC`` names it: ``idx``, ``point_id`` and the ``Data`` vectors under
their columns' names; a decoded text column is the number it selects, ``is_accelerated``,
``is_joint`` and ``is_reviewable`` its flags, and ``rate_group(life)`` a life's row of the
pivot rates. The technical notes use compact actuarial symbols instead. The mapping is:

===================  ===============================  ================================
Notes symbol         Cells                            Meaning
===================  ===============================  ================================
(none)               point_id()                       The model point's label
contract_type        contract_type()                  accelerated or standalone
(type decoded)       is_accelerated()                 The accelerated contract's flag
(basis decoded)      is_joint()                       The joint first event's flag
issue_age            age_at_entry(life)               Issue age (ANB), life 1 or 2
a                    age(t, life)                     Attained age (ANB) in month t
y                    policy_year(t)                   Policy year containing month t
(none)               duration(t)                      Completed policy years, y - 1
k                    duration_mth(t)                  Policy months at month t
(none)               duration_mth_init()              Policy months at t = 0
(none)               t_entry()                        First month on the books
(none)               is_active(t)                     Whether month t is in cover
n                    policy_term()                    Term in years
12n                  expiry_mth()                     Policy month cover ends at
(frame)              proj_len()                       Months to the end of cover
(none)               policy_count()                   Policies the point stands for
SA                   sum_assured()                    Sum assured at outset
SA(t)                benefit_pp(t, MAIN)              Sum assured in month t, indexed
B_AP                 benefit_pp(t, AP)                Additional-payment benefit
B_ch                 benefit_pp(t, CHILD)             Children's-cover benefit
P                    premium_mth_pp()                 Monthly premium at outset
(guarantee decoded)  is_reviewable()                  The reviewable premium's flag
P(t)                 premium_pp(t)                    Monthly premium in month t
(rating decoded)     rate_group(life)                 The life's row of the rates
i_ci(a)              ci_rate_base(t, life)            Table CI diagnosis rate
(1 + tau)^(t//12)    ci_trend_factor(t)               CI trend, valuation clock
eta                  sel_lapse_ci_loading             Anti-selection loading on i_ci
(none)               ci_sel_factor(t)                 Anti-selection factor applied
(latch at t = 0)     ci_sel_latched_init()            Whether the latch had closed
(factor at t = 0)    ci_sel_factor_init()             The factor it closed at
i_ci x trend x sel   ci_rate(t, life)                 CI diagnosis rate applied
q_d(a)               mort_rate(t, life)               Best-estimate mortality rate
k                    overlap_k                        Death/CI overlap factor, 0.10
(per life)           claim_rate_life(t, life)         q_d(1-k) + i_ci, one life
q_claim(a)           claim_rate(t)                    Combined claim decrement
q_pay(a)             claim_rate_paid(t)               The part that pays a benefit
delta                survival_slip                    Standalone slippage, 0.03
q_m(t)               claim_rate_mth(t)                Monthly combined decrement
q_pay_m(t)           claim_rate_paid_mth(t)           Monthly paying decrement
q_exit_m(t)          claim_rate_exit_mth(t)           Monthly non-paying decrement
a(x)                 ap_rate(t)                       Additional-payment frequency
a_m(t)               ap_rate_mth(t)                   The same, monthly
lambda_ch            child_freq                       Children's claim frequency p.a.
lambda_m             child_rate_mth()                 The same, monthly
w(y)                 lapse_rate(t)                    Annual lapse rate in month t
(table)              lapse_rate_base(t)               Table lapse rate before shock
w_shock              lapse_rate(t)                    Post-review shock lapse, too
w_m(t)               lapse_rate_mth(t)                Monthly lapse rate
rho_review           review_prem_shock                Premium change at a review
(rho at t = 0)       review_prem_shock_init()         Change at the last review so far
(none)               review_prem_change(t)            Change at the review under way
(none)               reviews_passed(t)                Reviews already applied
(none)               review_shock_active(t)           In the post-review window
(1 + rho)^reviews    review_prem_factor(t)            Premium factor from reviews
(factor at t = 0)    review_prem_factor_init()        Review factor to date
l(t)                 pols_if(t)                       In force at the start of month t
(l(0))               pols_if_init()                   Count in force at t = 0
(none)               pols_new_biz(t)                  Policies issued in month t
l(t+1)               pols_if_at(t, AFT_DECR)          In force at the end of month t
(none)               pols_if_at(t, timing)            The within-month counts
(none)               pols_claim(t)                    Main-benefit claims in month t
(none)               pols_lapse(t)                    Lapses at the end of month t
(none)               pols_maturity(t)                 Expiries at the end of the term
idx(t)               idx_factor(t)                    Cover indexation factor
(idx at t = 0)       idx_factor_init()                Cover factor given to date
idx_p(t)             idx_prem_factor(t)               Premium indexation factor
(idx_p at t = 0)     idx_prem_factor_init()           Premium factor to date
P x l                premiums(t)                      Premium income
SA x q_m x l         claims(t, MAIN)                  Main-benefit outgo
B_AP x a_m x l       claims(t, AP)                    Additional-payment outgo
B_ch x lambda_m x l  claims(t, CHILD)                 Children's-cover outgo
0                    claims(t, LAPSE)                 Surrender outgo; always zero
(sum)                claims(t, ALL)                   The four kinds' total
E_cl x q_m x l       claim_expenses(t)                Claim handling expense
E0, E_m(y)           expenses(t)                      Initial + maintenance expense
(none)               inflation_factor(t)              Expense inflation factor
CF(t)                net_cf(t)                        Net cash flow, income positive
(none)               result_pols()                    The counts, month by month
===================  ===============================  ================================

Three names needed care in :mod:`~.CI_UK_S`, and keep their reasons here.

The notes write ``a(x)`` for the additional-payment frequency and ``a`` for the attained
age in the same table. :func:`ap_rate` and :func:`age` separate them; nothing in the
model is called ``a``.

``q_d`` is the best-estimate mortality rate and is spelled :func:`mort_rate`, the
library-wide name, even though on this product mortality never acts as a decrement on
its own: it enters only through :func:`claim_rate`, net of the overlap. Keeping the
name makes the input visible where a reader looks for it.

``SA`` is a constant in the notes and a function of ``t`` here, because the indexation
option moves it. ``benefit_pp(t, MAIN)`` is that quantity; :func:`sum_assured` is the
outset value the model point carries. The additional-payment and children's benefits
are derived from the *indexed* sum assured **[std]** — the notes state their caps
against ``SA`` without saying which ``SA``, and applying the cap to a frozen outset
value would make the benefit shrink in real terms while the main benefit did not.

.. rubric:: The combined decrement, and why the rates cannot be added

The insured event is *death or first CI diagnosis, whichever comes first*. Adding
``q_d`` and ``i_ci`` double-counts lives that are both diagnosed and die in the same
period: once the CI claim has been paid the subsequent death of that life is not a
second claim, and a death inside the survival period converts the CI claim into a death
claim of the same amount rather than adding one. So

    q_claim(a) = i_ci(a) x trend x sel + q_d(a)(1 - k)          **[std]**

where ``k`` is the proportion of deaths preceded by a claimable diagnosis. ``k = 0.10``
flat is a standardization: the cause-of-claim splits that would calibrate it live in
CMI working papers whose datasets are subscriber-restricted. ``k = 0`` maximally
double-counts and ``k = 0.25`` may understate, so the notes rate it the third-largest
lever on the liability and it is a Reference rather than a literal.

On the **accelerated** contract nothing further is needed: however the overlap
resolves, ``SA`` is paid once. The 14-day survival period is cash-flow-neutral there
and is not modelled, which is the notes' second pitfall — applying the survival-period
slippage ``delta`` to the accelerated main benefit is wrong, because a death inside the
period still pays ``SA`` as a death claim.

On the **standalone** contract death pays nothing, and the decrement splits::

    q_pay(a)  = i_ci(a) x trend x sel x (1 - delta)
    q_exit(a) = q_d(a)(1 - k) + i_ci(a) x trend x sel x delta

with the same total, so the in-force run-off is identical and only the *paid* part
generates outgo. Note where ``k`` goes: onto the non-paying death exit, never onto the
paid decrement. Applying it to ``q_pay`` instead is the mirror-image pitfall and
understates claims.

One divergence from the notes' literal text, kept from :mod:`~.CI_UK_S`. The notes
convert annual rates to monthly with ``1 - (1 - q)^(1/12)`` and prescribe ``q_pay_m`` for
the standalone main benefit, but converting ``q_pay`` and ``q_exit`` independently leaves
their sum slightly below the ``q_m`` the same notes use for the in-force run-off — the two
conventions are inconsistent at second order. :func:`claim_rate_paid_mth` follows the
notes literally and :func:`claim_rate_exit_mth` is defined as the **residual**
``q_m - q_pay_m``, so the split is exact by construction and the run-off is the notes'.
:func:`check_claim_split` bounds the artefact: it asserts the residual really is the
independently converted ``q_exit`` to within ``claim_split_tol``, which on the
shipped points it is by four decimal places or better.

.. rubric:: The non-terminating benefits

The additional-payment and children's-cover benefits are the notes' third and fourth
pitfalls, and they are one mistake in two directions. Both are **non-depleting** —
they do not reduce the sum assured — and **non-terminating** — they do not decrement
the in-force. Only the main benefit ends the policy. Modelling them as accelerations
of the sum assured is a different product; terminating the policy on one is the same
error with the opposite sign.

They are carried as frequency loadings on the in-force, ``a_m`` and ``lambda_m``, and
appear in the roll-forward nowhere at all: :func:`pols_if_at` never sees them. Note the
monthly conversion is ``rate / 12`` and not ``1 - (1 - rate)^(1/12)``, which is correct
and deliberate: these are claim *frequencies* — expected events per year, repeatable —
not probabilities of a terminating event, so there is no survival transform to apply.

The treatment deliberately ignores the contractual claim-count caps — one per
additional-payment condition, two children's claims, and the per-child cross-policy
limit — because at the **[std]** frequencies shipped here the probability of reaching a
cap is second order. Respecting them exactly would need claim-count state variables,
which no point in force carries either.

.. rubric:: The rate basis is interpolated, not tabulated

``ci_rate_table.csv`` holds six pivot ages and the notes' rule is to interpolate
log-linearly between them, which :mod:`~.CI_UK_S`'s ``pivot_interp`` does: geometric in
the rate, linear in age. Outside the pivot range it continues the nearest end segment's
gradient, which is the same expression with the exponent out of [0, 1] — an
extrapolation, and flagged as one, because a 25-year policy issued at 40 stays inside
the pivots but a longer or younger one does not. ``Data`` makes the interpolation once,
by :mod:`~.CI_UK_S`'s own formula, element by element, for each sex and smoker group at
every attained age the contract admits, 18 to 74: ``Data.i_ci_array`` and
``Data.q_d_array``, tabled by the group's row and the age. Two cells read them, each at
the life's row, :func:`rate_group`, and its attained age, in cover alone:
:func:`ci_rate_base` and :func:`mort_rate`, which are 0 outside cover before they read
them, and refuse an age outside the arrays, naming the point.

Both rate sets are **[std]** placeholders shaped like the tables the notes name — AC04
and the "16" Series for diagnosis, a scaled population table for mortality — and must
not be presented as CMI or ONS values. The sex and smoker cells are the male
non-smoker pivots times flat factors, which is cruder still: real accelerated-CI
experience is not a flat female factor, since breast cancer makes female incidence
exceed male at the younger ages. The file's ``provenance`` column marks which cells came
from the notes and which from a factor.

.. rubric:: The reviewable variant

``premium_guarantee = reviewable`` turns on a 5-yearly review from the fifth
anniversary, policy month 60, on the policy clock. Premiums are constant between reviews
and multiplied by ``1 + rho_review`` at each one; the snapshot is ``rho_review = 0``, so
the variant runs identically to the guaranteed one until the Reference is moved. On a
point in force, the reviews made before month 0 are history,
:func:`review_prem_factor_init`, and ``rho_review`` applies to each review from the
valuation instant on, one in the valuation month among them. Two behavioural responses
hang off the same switch, both **[std]**:

- a **review shock lapse** in the twelve months after a review that raises premiums by
  more than 5%, ``min(0.30, w(y) + 2.0 max(0, rho - 0.05))``, where ``rho`` is the change
  that review made, :func:`review_prem_change`: on a point valued inside the window of a
  review before the valuation date, :func:`review_prem_shock_init`; and
- **selective lapsation** from the first such shock onward, loading the diagnosis rate
  by ``1 + eta`` on the lives that remain, because the healthier ones leave first: on a
  point in force whose latch closed before the valuation date,
  :func:`ci_sel_latched_init`, at :func:`ci_sel_factor_init`.

The economics are the point of the variant rather than the cash flows: guaranteed
premiums mean morbidity deterioration and definition drift fall entirely on the
insurer, and the reviewable design transfers that to policyholders at the cost of these
two responses.

.. rubric:: The contract's bounds

:mod:`~.CI_UK_S` projects any term from any age its tables reach. What running in force
adds is the contract's own bounds (``product-spec.md``), which :func:`proj_len` holds a
point to: a term of ``policy_term_min``, 5 years, to ``policy_term_max``, 50; an issue age
of each life from ``issue_age_min``, 18, to ``issue_age_max``, 64; and cover ending by the
75th birthday, ``expiry_age_max``: the issue age plus the term.  It holds the bounds and
the assumptions to their domains too, which :mod:`~.CI_UK_S` checks nowhere: each
Reference it raises to a power, divides by, bounds a rate or a benefit with, or reads as
a share, a loading, a frequency or an amount, on every point that reads it, so that no
projection runs on a negative rate, benefit or expense, a complex lapse or a NaN that a
comparison loses.

.. rubric:: What this product does not have

No account value, no asset share, no surrender or paid-up value, no bonus, no market
value reduction, and no commission line — the notes fold acquisition cost into the £200
initial expense rather than carrying commission separately as the term assurance
chassis does. There is likewise no interest-sensitive dynamic lapse: with no cash value
and no credited rate there is nothing to arbitrage, so the machinery the accumulation
products in this library carry is deliberately absent. ``claims(t, LAPSE)`` exists and
returns zero so that the absence of a surrender value is stated rather than inferred.

.. rubric:: Sign convention

The notes' ``Net CF`` is income positive, which is the library-wide sign of
:func:`net_cf`, so there is no outgo-positive ``liability_cf`` companion here. One
caveat for a reader checking the worked example by eye: the notes' **Net CF column
excludes the initial expense** — at the anchor cell's issue month it shows 31.88, with
the £200 initial expense noted separately as taking the month to -168.12.
:func:`net_cf` is the total, so on the twin issued at the valuation date ``net_cf(0)`` is
-168.12 and the notes' column is ``net_cf(0) + 200``.
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
    :mod:`~.CI_UK_S`'s columns, for a reader who wants every column at once: a reporting
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


def contract_type():
    """``accelerated`` (death or CI, whichever first) or ``standalone`` (CI only).

    On the standalone variant death pays nothing and simply terminates the policy
    [S4][S11]; a premium-refund-on-death feature exists in some designs and is excluded
    **[std]**.

    A reporting cell (the Space docstring), :mod:`~.CI_UK_S`'s, which returns the column
    as read, refusing any other value: no projection cell reads it here, and each branches
    on ``Data``'s decode of the same column instead, :func:`is_accelerated`.
    """
    v = model_point()["contract_type"]
    if v not in ("accelerated", "standalone"):
        raise ValueError("invalid contract_type")
    return v


def is_accelerated():
    """Whether the contract is ``accelerated``, from ``Data.is_accelerated``.

    ``Data`` decodes the ``contract_type`` column as :mod:`~.CI_UK_S`'s ``contract_type()
    == "accelerated"`` compares it, and refuses a type other than the two, so False is the
    standalone contract.
    """
    return bool(data.is_accelerated()[idx])                          # noqa: F821


def life_basis():
    """``single`` or ``joint_first_event``.

    The joint variant is a two-life survivorship product the notes place outside the
    base model **[std scope]**.  It is not combined with the standalone contract: the
    notes write the standalone decrement split for one life only, and there is no
    published basis for splitting a joint first-event decrement into paying and
    non-paying parts, so the combination raises rather than inventing one.

    A reporting cell (the Space docstring), :mod:`~.CI_UK_S`'s, which returns the column
    as read, refusing any other value and the combination: no projection cell reads it
    here, and each branches on ``Data``'s decode of the same column instead,
    :func:`is_joint`.  ``Data`` refuses the combination too, when it reads the table.
    """
    v = model_point()["life_basis"]
    if v not in ("single", "joint_first_event"):
        raise ValueError("invalid life_basis")
    if v == "joint_first_event" and contract_type() == "standalone":
        raise ValueError("standalone joint first event is out of scope")
    return v


def is_joint():
    """True when the policy covers two lives on a first-event basis, from ``Data.is_joint``.

    ``Data`` decodes the ``life_basis`` column as :mod:`~.CI_UK_S`'s ``life_basis() ==
    "joint_first_event"`` compares it, and refuses a basis other than the two.
    """
    return bool(data.is_joint()[idx])                                # noqa: F821


def age_at_entry(life):
    """The issue age (ANB) of the first (``life = 1``) or second life.

    Age nearest birthday, attained age advancing on policy anniversaries **[std]**.
    Any consistent basis works, but it must be the same one for the diagnosis rates,
    the mortality rates and the attained-age indexing - a mismatch there is one of the
    notes' listed pitfalls.  The age at issue, not at the valuation date: ``age(0, life)``
    is the attained age then.

    ``life`` has no default, here or in the seven other cells that take it, :func:`sex`,
    :func:`smoker`, :func:`age`, :func:`ci_rate_base`, :func:`mort_rate`, :func:`ci_rate`
    and :func:`claim_rate_life`, where :mod:`~.CI_UK_S` defaults it to 1: every call passes
    1 or 2, so that a compiled model declares each a plain parameter.  modelx keys
    :mod:`~.CI_UK_S`'s calls by the arguments bound, ``age(t)`` as ``(t, 1)``, so the two
    models' cells pair as before.  Read from ``Data.age_at_entry`` and, on a joint point,
    ``Data.joint_age``, ``int`` of each as :mod:`~.CI_UK_S` reads it.
    """
    if life == 1:
        return int(data.age_at_entry()[idx])                         # noqa: F821
    if life == 2 and is_joint():
        return int(data.joint_age()[idx])                            # noqa: F821
    raise ValueError("invalid life")


def sex(life):
    """The sex (M / F) of the first or second life, as the table spells it.

    A reporting cell (the Space docstring), which returns the ``sex`` or ``joint_sex``
    column as read, a single-life point's blank second life as NaN, which
    :mod:`~.CI_UK_S` refuses as ``invalid life``: no projection cell reads it here, and
    :func:`ci_rate_base` and :func:`mort_rate` read each life's row of the pivot rates,
    :func:`rate_group`, instead.
    """
    if life == 1:
        return model_point()["sex"]
    if life == 2:
        return model_point()["joint_sex"]
    raise ValueError("invalid life")


def smoker(life):
    """The smoker status (NS / S) of the first or second life, as the table spells it.

    A reporting cell, as :func:`sex` is: the ``smoker`` or ``joint_smoker`` column as
    read, a single-life point's blank second life as NaN.
    """
    if life == 1:
        return model_point()["smoker"]
    if life == 2:
        return model_point()["joint_smoker"]
    raise ValueError("invalid life")


def rate_group(life):
    """The row of ``Data.i_ci_array`` and ``Data.q_d_array`` of the first (``life = 1``) or
    second life.

    The life's sex and smoker status, the key :mod:`~.CI_UK_S`'s ``pivot_interp`` reads
    *ci_rate_table.csv* by, decoded in ``Data`` into the row they select: M NS 0, M S 1,
    F NS 2 and F S 3, from ``Data.rate_group`` and, on a joint point,
    ``Data.joint_rate_group``.  Like :func:`age_at_entry`, it refuses a second life on a
    single-life point.
    """
    if life == 1:
        return int(data.rate_group()[idx])                           # noqa: F821
    if life == 2 and is_joint():
        return int(data.joint_rate_group()[idx])                     # noqa: F821
    raise ValueError("invalid life")


def sum_assured():
    """SA: the sum assured at outset **[std]**, £100,000 on the anchor cell.

    :func:`benefit_pp` ``(t, MAIN)`` is the amount actually at risk in month t, which
    differs from this once the indexation option is elected: on an indexed point in force,
    the cover of the year under way is this times :func:`idx_factor_init`.  From
    ``Data.sum_assured``.
    """
    return float(data.sum_assured()[idx])                            # noqa: F821


def policy_term():
    """n: the term in years, 5-50 [S2][S5]; the policy also ends by the 75th birthday.

    :func:`proj_len` refuses a term below ``policy_term_min``, 5 years, or above
    ``policy_term_max``, 50, and a life whose cover runs past ``expiry_age_max``, 75.
    From ``Data.policy_term``.
    """
    return int(data.policy_term()[idx])                              # noqa: F821


def cover_basis():
    """The cover shape.  Level only: decreasing and FIB shapes are out of scope here.

    Both exist on the term assurance chassis this product sits on and are implemented
    in ``Term_UK_S``; these notes scope them out **[std scope]**.

    A reporting cell (the Space docstring), :mod:`~.CI_UK_S`'s, which returns the column
    as read, refusing any other value: no projection cell reads it, the cover being level
    on every point ``Data`` admits.
    """
    v = model_point()["cover_basis"]
    if v != "level":
        raise ValueError("invalid cover_basis")
    return v


def premium_guarantee():
    """``guaranteed`` [S1] or ``reviewable``, which turns on the 5-yearly review cycle.

    A reporting cell (the Space docstring), :mod:`~.CI_UK_S`'s, which returns the column
    as read, refusing any other value: no projection cell reads it here, and each branches
    on ``Data``'s decode of the same column instead, :func:`is_reviewable`.
    """
    v = model_point()["premium_guarantee"]
    if v not in ("guaranteed", "reviewable"):
        raise ValueError("invalid premium_guarantee")
    return v


def is_reviewable():
    """Whether the premium is ``reviewable``, from ``Data.is_reviewable``.

    ``Data`` decodes the ``premium_guarantee`` column as :mod:`~.CI_UK_S`'s
    ``premium_guarantee() == "reviewable"`` compares it, and refuses a guarantee other than
    the two, so False is the guaranteed premium, which no review changes.
    """
    return bool(data.is_reviewable()[idx])                           # noqa: F821


def premium_mth_pp():
    """P: the monthly premium per policy at outset **[std]**, £55.00 on the anchor cell.

    A placeholder, not a market rate: no UK insurer publishes CI rate cards, so any
    reference premium is constructed.  Profitability conclusions drawn from the worked
    example are meaningless.  On a point in force, the premium of the month is this times
    the indexation factor and the review factor, each from its history at the valuation
    date (:func:`premium_pp`).  From ``Data.premium_mth``.
    """
    return float(data.premium_mth()[idx])                            # noqa: F821


def premium_mode():
    """Monthly or annual premium payment.

    Inert: the grid is monthly and the notes carry the premium as a monthly amount
    either way.  Carried because the model point attribute table names it.

    A reporting cell (the Space docstring), which returns the column as read, refusing
    any other value, as ``Term_UK_SEC``'s does: no projection cell reads it.
    :mod:`~.CI_UK_S`'s returns the column unchecked, and ``Data`` has refused any other
    mode since the in-force step, so it returns the same text on every point ``Data``
    admits.
    """
    v = model_point()["premium_mode"]
    if v not in ("monthly", "annual"):
        raise ValueError("invalid premium_mode")
    return v


def children_cover():
    """Whether children's cover is active; automatic on the composite product [S1].

    From ``Data.children_cover``, which decodes the column as :mod:`~.CI_UK_S`'s ``bool``
    reads it.
    """
    return bool(data.children_cover()[idx])                          # noqa: F821


def indexation():
    """Whether the increasing-cover option is elected; false in the base run **[std]**.

    Declining an increase three years running removes the option [S1][S4]; the base
    model assumes full take-up while the option is active, so that rule is never
    reached and is not implemented.  From ``Data.indexation``, decoded as
    :func:`children_cover`'s column is.
    """
    return bool(data.indexation()[idx])                              # noqa: F821


def policy_count():
    """The number of policies the model point stands for, its ``policy_count`` column.

    A point in force at the valuation date counts the policies in force then, before any
    month-0 event; any other point counts the policies it issues. Either way the count
    enters the projection once: as :func:`pols_if_init` for the first, as
    :func:`pols_new_biz` in the issue month for the second. It is the one weight on every
    flow: every opening-state column is a factor or a rate.  From ``Data.policy_count``.
    """
    return float(data.policy_count()[idx])                           # noqa: F821


def pols_if_init():
    """Policies in force at the valuation date, before any month-0 event.

    ``policy_count()`` for a point already in force at ``t = 0``
    (``duration_mth_init() > 0``), and 0 for one issued at or after it, whose policies
    enter through :func:`pols_new_biz` in the issue month instead, as in
    ``basiclife.BasicTerm_SE``. So on a point issued at ``t = 0`` this is 0, and
    ``pols_if(0)`` is the issued count.
    """
    return policy_count() if duration_mth_init() > 0 else 0.0


def duration_mth_init():
    """Completed policy months at the valuation date, the ``duration_mth`` column.

    The policy's age in months at ``t = 0``: 60 for model point 9, valued on its first
    review, 0 for one issued at the valuation date, and -13 for one to be issued 13 months
    after it, which ``Data`` admits up to ``future_horizon_mth`` months ahead. It is read
    as ``basiclife.BasicTerm_SE`` reads it, and is the one fact the policy clock takes from
    the model point; a point may be valued in any month of its policy year.  Its element of
    ``Data.duration_mth``.
    """
    return int(data.duration_mth()[idx])                             # noqa: F821


def idx_factor_init():
    """idx at the valuation instant: the cover factor entering month 0.

    The RPI increases the policy was given before month 0, as one factor on
    :func:`sum_assured`, the sum assured at issue: mid-year, the factor of the policy year
    under way; on a valuation on an anniversary, the factor of the policy year it closes,
    the anniversary's own increase being month 0's event, which :func:`idx_factor` makes
    at ``rpi_rate``, the References of the valuation date (USLIB-SEC-PLAN.md D6, precised
    at its M7). History, read from the model point, not recomputed from ``rpi_rate``,
    which is the assumed rate from the valuation instant on. 1 on a point not yet in
    force, on one in force 12 months or fewer, whose first anniversary is month 0's or
    later, and on one without the option, which ``Data`` requires.  From
    ``Data.idx_factor_init``.
    """
    return float(data.idx_factor_init()[idx])                        # noqa: F821


def idx_prem_factor_init():
    """idx_p at the valuation instant: the premium factor entering month 0.

    :func:`idx_factor_init`'s counterpart on the premium, :func:`premium_mth_pp` the
    premium at issue, measured at the same instant: on an anniversary, the factor of the
    policy year it closes.  History, as the cover factor is.  1 on a point not yet in
    force, on one in force 12 months or fewer, and on one without the option, which
    ``Data`` requires.  From ``Data.idx_prem_factor_init``.
    """
    return float(data.idx_prem_factor_init()[idx])                   # noqa: F821


def review_prem_factor_init():
    """The premium factor the reviews made before month 0 have given.

    The premium changes the reviews before the valuation instant have made, as one factor
    on the premium at issue: mid-period, the factor of the review period under way; on a
    valuation in a review month, the factor of the period that review closes, the review
    being month 0's event, which :func:`review_prem_factor` makes at today's
    ``review_prem_shock`` (USLIB-SEC-PLAN.md D6, precised at its M7).  History, read from
    the model point: :mod:`~.CI_UK_S` re-derives it as ``(1 + rho)`` to the power of the
    reviews passed, so a ``review_prem_shock`` set at the valuation date would reach back
    over every review already made, repricing premiums long collected.  At a change that
    never moved, it is that.  1 on a point not yet in force, on a guaranteed point, which
    ``Data`` requires, and on a reviewable point in force no longer than the review
    period, which has made no review before month 0, which :func:`proj_len` requires.
    From ``Data.review_prem_factor_init``.
    """
    return float(data.review_prem_factor_init()[idx])                # noqa: F821


def ci_sel_latched_init():
    """The select latch entering month 0: 1 once it has closed, and 0 before.

    Whether a review before month 0 raised premiums past the shock threshold of its day,
    so that the lives remaining carry an anti-selection factor,
    :func:`ci_sel_factor_init`, from then on.  On a valuation in a review month it is the
    latch before that review, which is month 0's event: if it closes the latch, it does so
    at ``t = 0``, at the References of the valuation date (USLIB-SEC-PLAN.md D6, precised
    at its M7).  A flag of its own, not read off the factor: a latch closed at a loading
    of 0 holds a factor of 1, and stays closed, where read as open it would close again at
    the next shock review, at today's ``sel_lapse_ci_loading``.  History, read from the
    model point: :mod:`~.CI_UK_S` re-derives the latch from ``review_prem_shock``, so a
    change set at the valuation date would open or close it at reviews long past.  0 on a
    point not yet in force and on a guaranteed point, which ``Data`` requires, and on a
    reviewable point in force no longer than the review period, which :func:`proj_len`
    requires.  From ``Data.ci_sel_latched_init``.
    """
    return int(data.ci_sel_latched_init()[idx])                      # noqa: F821


def ci_sel_factor_init():
    """The anti-selection factor the select latch closed at, read only once it has.

    :func:`ci_sel_factor`'s value in month 0 on a point whose latch had closed before
    month 0, :func:`ci_sel_latched_init` 1: ``1 + eta``, at the loading of its day, which
    :func:`ci_sel_factor` carries unchanged, whatever it is, 1 among them.  History, read
    from the model point, as the latch is.  A number, 0 or more, as ``Data`` requires: 0
    for a latch closed at a loading of -1, which :func:`proj_len` admits; and 1 on an
    open latch, on a point not yet in force, on a guaranteed point, and on a reviewable
    point in force no longer than the review period.  While the latch is open a review
    from month 0 on, a review at the valuation date among them, closes it at
    ``1 + sel_lapse_ci_loading``.  From ``Data.ci_sel_factor_init``.
    """
    return float(data.ci_sel_factor_init()[idx])                     # noqa: F821


def review_prem_shock_init():
    """rho entering month 0: the premium change the last review before it made.

    The change at the last review before month 0, which opened the review period under
    way or, on a valuation in a review month, the one that month's review closes, the
    ``review_prem_shock`` of its day: on a point valued inside that review's twelve-month
    window it sets the window's shock lapse, through :func:`review_prem_change`, which
    reads it nowhere else.  On a valuation in a review month it is read nowhere: from
    ``t = 0`` the review under way is that month's own, month 0's event, which opens its
    own window at today's change (USLIB-SEC-PLAN.md D6, precised at its M7), the window of
    the review before it having closed.  History, read from the model point, where
    :mod:`~.CI_UK_S` reads today's ``review_prem_shock`` at every review.  0 on a point not
    yet in force, on a guaranteed point, which ``Data`` requires, and on a reviewable
    point in force no longer than the review period, which :func:`proj_len` requires.
    From ``Data.review_prem_shock_init``.
    """
    return float(data.review_prem_shock_init()[idx])                 # noqa: F821


def proj_len():
    """The number of months from the valuation date to the end of cover.

    ``expiry_mth() - duration_mth_init()``: 300 for the anchor cell issued at ``t = 0``,
    240 for model point 9, in force 60 months, and the term's months plus ``k`` for a
    point issued ``k`` months after the valuation date.  The frame is
    ``t = 0, 1, ..., proj_len() - 1``; ``proj_len()`` is its exclusive end and the row count
    of :func:`result_cf`.  The policy expires at the end of the last month with no maturity
    and no surrender value [S1][S4][S5], so there is nothing after it.

    These raise here, naming the point, rather than project nothing, a frame the contract
    does not have or numbers no policy can have, each checked in this order:

    * a point whose cover ended at or before the valuation date, which an in-force extract
      should not carry;
    * any point while a bound of the contract, ``policy_term_min``, ``policy_term_max``,
      ``issue_age_min``, ``issue_age_max`` or ``expiry_age_max``, is not a whole number, 0
      or more: a NaN bound fails every comparison, and so refuses nothing, and an infinite
      one bounds nothing;
    * one whose term is below ``policy_term_min``, 5 years, or above ``policy_term_max``,
      50;
    * one with a life issued below ``issue_age_min``, 18, or above ``issue_age_max``, 64;
    * one with a life whose cover runs past the 75th birthday, ``expiry_age_max``: the
      issue age plus the term;
    * any point while a Reference every point reads is off its domain, which the message
      names: ``ci_trend``, ``inflation_rate`` and ``sel_lapse_ci_loading`` a finite number,
      -1 or more, since the factors they make, ``1 + tau`` and the rest, below 0 make a
      negative diagnosis rate or expense; ``overlap_k`` and ``survival_slip`` a number from
      0 to 1, the shares of the deaths and of the diagnoses that do not pay, which off it
      make a negative claim, paid or exit rate; ``ap_freq_factor`` and ``child_freq`` a
      number from 0 to 12, so that no month's additional payments or children's claims
      number more than one per policy in force, at any rate the model accepts, or fewer
      than none (:func:`ap_rate` and :func:`child_rate_mth` derive the bound);
      ``rpi_rate`` a finite number, since the floor at 0 and the cap read an infinity as
      no increase or as the cap; ``idx_cover_cap``, ``idx_prem_cap`` and ``idx_prem_mult``
      a finite number, 0 or more, below which an increase is a cut, and ``ap_cap`` and
      ``child_cap`` too, below which a benefit is negative; each cap is a bound written
      second, so a NaN one would be lost, ``min`` keeping its first argument; ``ap_share``
      and ``child_share`` a number from 0 to 1, a share of the indexed cover; the expenses
      ``expense_acq``, ``expense_maint`` and ``expense_claim`` a finite number, 0 or more;
      and ``claim_split_tol`` a finite number, 0 or more, since at an infinity
      :func:`check_claim_split` passes anything;
    * a reviewable point while a review Reference is off its domain: ``review_period_mths``
      a whole number of months, 1 or more, which the reviews divide the policy months by;
      ``review_lapse_cap`` a number from 0 to 1, since the shock lapse is at most the cap,
      and past 1 its monthly rate, ``1 - (1 - w)^(1/12)``, has no real value, which
      :mod:`~.CI_UK_S` projects as a complex number, and below 0 the window lapses a
      negative share; ``review_prem_shock`` a finite number, -1 or more, below which a
      review takes the premium below 0; ``review_lapse_threshold`` a finite number, since
      a NaN fails every comparison and so closes the latch at a review that changed nothing;
      and ``review_lapse_slope`` a finite number, 0 or more, since below 0 the window lapses
      fewer the more the premium rises, and a NaN reads as the cap through
      :func:`lapse_rate`'s ``min``, its bound first as in :mod:`~.CI_UK_S`;
    * a reviewable point in force for ``review_period_mths`` months or fewer with a review
      history, a review factor other than 1, a closed latch or a last change other than
      0, a state :mod:`~.CI_UK_S` cannot reach, since no review has been made before month
      0: on a point valued in its first review's month, that review is month 0's event,
      the projection's, not history (USLIB-SEC-PLAN.md D6, precised at its M7);
    * and a reviewable point in force for more than ``review_period_mths`` months and no
      more than twice that, one review made before month 0, whose review factor is not
      ``1 + review_prem_shock_init()``, to 1e-12 of it, as an extract may spell the two:
      the one review made has made that change and no other.

    What depends on an assumption of its day is not refused: a latch left open after a
    change past today's ``review_lapse_threshold`` is a history some point can have, the
    threshold having been higher then; and two reviews or more give a factor any changes
    can make.

    A domain is a comparison no NaN passes, a finite number one that ``x - x == 0.0`` holds
    of, which an infinity fails too, an infinity less itself being NaN, and a whole number
    one that ``x % 1 == 0`` holds of, which an infinity fails, its remainder being NaN.
    All but the first read this Space's References, which ``Data`` cannot see, so they are
    checked here.  The bounds are the product's limits (``product-spec.md``), the contract
    the compiled model's caches are sized from (``spec_sec.py``): a frame of at most
    ``policy_term_max``, 50 years, and ``Data.future_horizon_mth``, 120 months, so 720
    months; and attained ages from ``issue_age_min``, 18, to ``expiry_age_max`` less one,
    74, the ages ``Data`` interpolates the pivot rates at.  Every report reads this cell
    first, so no point outside them is projected, in modelx as compiled.  Raising
    ``policy_term_max`` or the horizon needs the spec's ``t`` raised and the model rebuilt,
    or a report runs past the caches in the compiled model alone, raising ``IndexError``
    where modelx projects; and raising ``expiry_age_max`` or lowering ``issue_age_min``
    needs ``Data.rate_age_max`` or ``rate_age_min`` moved with it, or the cell that reads
    the rates refuses the age.  A guaranteed point reads no review Reference, and projects
    whatever they are.

    A message prints each Reference as the compiled model holds it: a rate through
    ``float``, and a term, an age or a count of months through ``int``, a whole number as
    an int where a domain is refused.  So a Reference set as an int or as a float gives one
    message in both engines.
    """
    n = expiry_mth() - duration_mth_init()
    if n <= 0:
        raise ValueError(
            f"point_id {point_id()}: duration_mth {duration_mth_init()} "
            f"is at or past the end of cover, policy month {expiry_mth()}")
    if not (policy_term_min >= 0 and policy_term_min % 1 == 0):      # noqa: F821
        raise ValueError(
            f"point_id {point_id()}: policy_term_min must be a whole number, 0 or more, "
            f"not {int(policy_term_min) if policy_term_min % 1 == 0 else policy_term_min}")
    if not (policy_term_max >= 0 and policy_term_max % 1 == 0):      # noqa: F821
        raise ValueError(
            f"point_id {point_id()}: policy_term_max must be a whole number, 0 or more, "
            f"not {int(policy_term_max) if policy_term_max % 1 == 0 else policy_term_max}")
    if not (issue_age_min >= 0 and issue_age_min % 1 == 0):          # noqa: F821
        raise ValueError(
            f"point_id {point_id()}: issue_age_min must be a whole number, 0 or more, "
            f"not {int(issue_age_min) if issue_age_min % 1 == 0 else issue_age_min}")
    if not (issue_age_max >= 0 and issue_age_max % 1 == 0):          # noqa: F821
        raise ValueError(
            f"point_id {point_id()}: issue_age_max must be a whole number, 0 or more, "
            f"not {int(issue_age_max) if issue_age_max % 1 == 0 else issue_age_max}")
    if not (expiry_age_max >= 0 and expiry_age_max % 1 == 0):        # noqa: F821
        raise ValueError(
            f"point_id {point_id()}: expiry_age_max must be a whole number, 0 or more, "
            f"not {int(expiry_age_max) if expiry_age_max % 1 == 0 else expiry_age_max}")
    if policy_term() < policy_term_min:                              # noqa: F821
        raise ValueError(
            f"point_id {point_id()}: the term, {policy_term()} years, is below "
            f"policy_term_min, {int(policy_term_min)}")              # noqa: F821
    if policy_term() > policy_term_max:                              # noqa: F821
        raise ValueError(
            f"point_id {point_id()}: the term, {policy_term()} years, is above "
            f"policy_term_max, {int(policy_term_max)}")              # noqa: F821
    for life in range(1, 3 if is_joint() else 2):
        if age_at_entry(life) < issue_age_min:                       # noqa: F821
            raise ValueError(
                f"point_id {point_id()}: life {life}'s issue age, "
                f"{age_at_entry(life)}, is below issue_age_min, "
                f"{int(issue_age_min)}")                             # noqa: F821
        if age_at_entry(life) > issue_age_max:                       # noqa: F821
            raise ValueError(
                f"point_id {point_id()}: life {life}'s issue age, "
                f"{age_at_entry(life)}, is above issue_age_max, "
                f"{int(issue_age_max)}")                             # noqa: F821
        if age_at_entry(life) + policy_term() > expiry_age_max:      # noqa: F821
            raise ValueError(
                f"point_id {point_id()}: life {life}'s cover runs to attained age "
                f"{age_at_entry(life) + policy_term()}, issue age "
                f"{age_at_entry(life)} and a {policy_term()}-year term, past "
                f"expiry_age_max, {int(expiry_age_max)}")            # noqa: F821
    if not (ci_trend >= -1.0 and ci_trend - ci_trend == 0.0):        # noqa: F821
        raise ValueError(
            f"point_id {point_id()}: ci_trend must be a finite number, -1 or "
            f"more, not {float(ci_trend)}")                          # noqa: F821
    if not (inflation_rate >= -1.0                                   # noqa: F821
            and inflation_rate - inflation_rate == 0.0):             # noqa: F821
        raise ValueError(
            f"point_id {point_id()}: inflation_rate must be a finite number, "
            f"-1 or more, not {float(inflation_rate)}")              # noqa: F821
    if not (sel_lapse_ci_loading >= -1.0                             # noqa: F821
            and sel_lapse_ci_loading - sel_lapse_ci_loading == 0.0):  # noqa: F821
        raise ValueError(
            f"point_id {point_id()}: sel_lapse_ci_loading must be a finite "
            f"number, -1 or more, not {float(sel_lapse_ci_loading)}")  # noqa: F821
    if not (overlap_k >= 0.0 and overlap_k <= 1.0):                  # noqa: F821
        raise ValueError(
            f"point_id {point_id()}: overlap_k must be a number from 0 to 1, "
            f"not {float(overlap_k)}")                               # noqa: F821
    if not (survival_slip >= 0.0 and survival_slip <= 1.0):          # noqa: F821
        raise ValueError(
            f"point_id {point_id()}: survival_slip must be a number from 0 to "
            f"1, not {float(survival_slip)}")                        # noqa: F821
    if not (ap_freq_factor >= 0.0 and ap_freq_factor <= 12.0):       # noqa: F821
        raise ValueError(
            f"point_id {point_id()}: ap_freq_factor must be a number from 0 to "
            f"12, not {float(ap_freq_factor)}")                      # noqa: F821
    if not (child_freq >= 0.0 and child_freq <= 12.0):               # noqa: F821
        raise ValueError(
            f"point_id {point_id()}: child_freq must be a number from 0 to 12, "
            f"not {float(child_freq)}")                              # noqa: F821
    if not rpi_rate - rpi_rate == 0.0:                               # noqa: F821
        raise ValueError(
            f"point_id {point_id()}: rpi_rate must be a finite number, not "
            f"{float(rpi_rate)}")                                    # noqa: F821
    if not (idx_cover_cap >= 0.0 and idx_cover_cap - idx_cover_cap == 0.0):  # noqa: F821
        raise ValueError(
            f"point_id {point_id()}: idx_cover_cap must be a finite number, 0 "
            f"or more, not {float(idx_cover_cap)}")                  # noqa: F821
    if not (idx_prem_mult >= 0.0 and idx_prem_mult - idx_prem_mult == 0.0):  # noqa: F821
        raise ValueError(
            f"point_id {point_id()}: idx_prem_mult must be a finite number, 0 "
            f"or more, not {float(idx_prem_mult)}")                  # noqa: F821
    if not (idx_prem_cap >= 0.0 and idx_prem_cap - idx_prem_cap == 0.0):  # noqa: F821
        raise ValueError(
            f"point_id {point_id()}: idx_prem_cap must be a finite number, "
            f"0 or more, not {float(idx_prem_cap)}")                 # noqa: F821
    if not (ap_share >= 0.0 and ap_share <= 1.0):                    # noqa: F821
        raise ValueError(
            f"point_id {point_id()}: ap_share must be a number from 0 to 1, "
            f"not {float(ap_share)}")                                # noqa: F821
    if not (ap_cap >= 0.0 and ap_cap - ap_cap == 0.0):               # noqa: F821
        raise ValueError(
            f"point_id {point_id()}: ap_cap must be a finite number, 0 or "
            f"more, not {float(ap_cap)}")                            # noqa: F821
    if not (child_share >= 0.0 and child_share <= 1.0):              # noqa: F821
        raise ValueError(
            f"point_id {point_id()}: child_share must be a number from 0 to 1, "
            f"not {float(child_share)}")                             # noqa: F821
    if not (child_cap >= 0.0 and child_cap - child_cap == 0.0):      # noqa: F821
        raise ValueError(
            f"point_id {point_id()}: child_cap must be a finite number, 0 or "
            f"more, not {float(child_cap)}")                         # noqa: F821
    if not (expense_acq >= 0.0 and expense_acq - expense_acq == 0.0):  # noqa: F821
        raise ValueError(
            f"point_id {point_id()}: expense_acq must be a finite number, 0 or "
            f"more, not {float(expense_acq)}")                       # noqa: F821
    if not (expense_maint >= 0.0 and expense_maint - expense_maint == 0.0):  # noqa: F821
        raise ValueError(
            f"point_id {point_id()}: expense_maint must be a finite number, 0 "
            f"or more, not {float(expense_maint)}")                  # noqa: F821
    if not (expense_claim >= 0.0 and expense_claim - expense_claim == 0.0):  # noqa: F821
        raise ValueError(
            f"point_id {point_id()}: expense_claim must be a finite number, 0 "
            f"or more, not {float(expense_claim)}")                  # noqa: F821
    if not (claim_split_tol >= 0.0                                   # noqa: F821
            and claim_split_tol - claim_split_tol == 0.0):           # noqa: F821
        raise ValueError(
            f"point_id {point_id()}: claim_split_tol must be a finite "
            f"number, 0 or more, not {float(claim_split_tol)}")      # noqa: F821
    if is_reviewable():
        if not (review_period_mths >= 1 and review_period_mths % 1 == 0):  # noqa: F821
            raise ValueError(
                f"point_id {point_id()}: review_period_mths must be a whole number of "
                f"months, 1 or more, not {int(review_period_mths)}"
                if review_period_mths % 1 == 0 else                  # noqa: F821
                f"point_id {point_id()}: review_period_mths must be a whole number of "
                f"months, 1 or more, not {review_period_mths}")      # noqa: F821
        if not (review_lapse_cap >= 0.0 and review_lapse_cap <= 1.0):  # noqa: F821
            raise ValueError(
                f"point_id {point_id()}: review_lapse_cap must be a number "
                f"from 0 to 1, not {float(review_lapse_cap)}")       # noqa: F821
        if not (review_prem_shock >= -1.0                            # noqa: F821
                and review_prem_shock - review_prem_shock == 0.0):   # noqa: F821
            raise ValueError(
                f"point_id {point_id()}: review_prem_shock must be a finite "
                f"number, -1 or more, not {float(review_prem_shock)}")  # noqa: F821
        if not review_lapse_threshold - review_lapse_threshold == 0.0:  # noqa: F821
            raise ValueError(
                f"point_id {point_id()}: review_lapse_threshold must be a "
                f"finite number, not {float(review_lapse_threshold)}")  # noqa: F821
        if not (review_lapse_slope >= 0.0                            # noqa: F821
                and review_lapse_slope - review_lapse_slope == 0.0):  # noqa: F821
            raise ValueError(
                f"point_id {point_id()}: review_lapse_slope must be a finite "
                f"number, 0 or more, not {float(review_lapse_slope)}")  # noqa: F821
        d = duration_mth_init()
        if 0 < d <= review_period_mths:                              # noqa: F821
            if review_prem_factor_init() != 1.0:
                raise ValueError(
                    f"point_id {point_id()}: review_prem_factor_init is "
                    f"{review_prem_factor_init()}, where a reviewable point in force {d} "
                    f"months, no more than review_period_mths, "
                    f"{int(review_period_mths)}, has had no review before "  # noqa: F821
                    "month 0: 1")
            if ci_sel_latched_init() != 0:
                raise ValueError(
                    f"point_id {point_id()}: ci_sel_latched_init is "
                    f"{ci_sel_latched_init()}, where a reviewable point in force {d} "
                    f"months, no more than review_period_mths, "
                    f"{int(review_period_mths)}, has had no review before "  # noqa: F821
                    "month 0: 0")
            if review_prem_shock_init() != 0.0:
                raise ValueError(
                    f"point_id {point_id()}: review_prem_shock_init is "
                    f"{review_prem_shock_init()}, where a reviewable point in force {d} "
                    f"months, no more than review_period_mths, "
                    f"{int(review_period_mths)}, has had no review before "  # noqa: F821
                    "month 0: 0")
        if review_period_mths < d <= 2 * review_period_mths:         # noqa: F821
            once = 1.0 + review_prem_shock_init()
            if not abs(review_prem_factor_init() - once) <= 1e-12 * abs(once):
                raise ValueError(
                    f"point_id {point_id()}: review_prem_factor_init is "
                    f"{review_prem_factor_init()}, where a reviewable point in force {d} "
                    f"months, review_period_mths {int(review_period_mths)}, "  # noqa: F821
                    f"has had one review before month 0, whose change, "
                    f"review_prem_shock_init, is {review_prem_shock_init()}: {once}")
    return n


def expiry_mth():
    """12n: the policy month cover expires at, on the policy clock.

    :mod:`~.CI_UK_S`'s frame from issue, its ``proj_len()``: the last covered month is
    ``duration_mth(t) = 12n - 1``, and :func:`is_active` is false from
    ``duration_mth(t) = 12n`` on.  :func:`proj_len` counts from the valuation date instead.
    """
    return 12 * policy_term()


def t_entry():
    """The first month the policy is on the books: ``max(0, -duration_mth_init())``.

    0 for a point in force at the valuation date or issued at it, ``k`` for one issued
    ``k`` months later.  It is the base of the count's recursion, which opens there from
    the opening state, and reads no month before it.  The reviews and anniversaries the
    projection makes are counted from the valuation instant instead, on the policy clock,
    one that falls at the valuation date the first of them.
    """
    return max(0, -duration_mth_init())


def is_active(t):
    """Whether month t is inside cover: issued, and not yet expired.

    ``0 <= duration_mth(t) < expiry_mth()``.  False before issue and from the month cover
    has ended, ``t = proj_len()``.  Outside cover every count is zero, and so every cash
    flow; no count cell evaluates a rate there, and no table is read at a policy year or
    an attained age the policy does not have.
    """
    return 0 <= duration_mth(t) < expiry_mth()


def duration(t):
    """Completed policy years at the start of month t: ``duration_mth(t) // 12``.

    0 throughout the first policy year, and negative before issue: the count of
    anniversaries the indexation factors step on.
    """
    return duration_mth(t) // 12


def duration_mth(t):
    """Completed policy months at the start of month t, the **policy** clock.

    ``duration_mth_init() + t``: ``t`` counts months from the valuation date and
    ``duration_mth(t)`` months from issue, and the two move together.  A closed form,
    where ``basiclife.BasicTerm_SE`` adds one a month by recursion: the same numbers,
    without a call chain as long as the frame.  Negative before issue.  The reviews and
    their shock window read it.
    """
    return duration_mth_init() + t


def policy_year(t):
    """y: the 1-based policy year containing month t, ``duration(t) + 1``.

    1 through the first twelve policy months.  Used only where a 1-based schedule is
    looked up, the lapse table's ``policy_year`` key; 0 or less before issue, where
    nothing reads a table by it.
    """
    return duration(t) + 1


def age(t, life):
    """a: the attained age (ANB) of ``life`` in the policy year containing month t."""
    return age_at_entry(life) + duration(t)


def ci_rate_base(t, life):
    """i_ci(a): the table CI diagnosis rate for ``life`` in the year containing month t.

    First diagnosis of a listed condition, total and permanent disability included.  A
    **[std]** proxy shaped like an insured-lives accelerated-CI diagnosis-rate table -
    the AC04 and "16" Series values are subscriber-restricted - and not to be presented
    as a CMI rate.  The basis at the valuation date: :func:`ci_trend_factor` trends it
    from there.  Zero outside cover, where ``age(t, life)`` is not an age the policy reaches
    in force, before the rates are read.

    Inside it, this is the one cell that reads ``Data.i_ci_array``, :mod:`~.CI_UK_S`'s
    ``pivot_interp(age, sex, smoker, "i_ci")`` at every attained age the contract admits,
    made once in ``Data`` by S's own formula: at the life's row, :func:`rate_group`, and its
    attained age, the array's index.  An age outside the array's, ``Data.rate_age_first``
    to ``Data.rate_age_last``, 18 to 74, raises ``ValueError``, naming the point, the
    file, as ``Data.ci_rate_file`` names it, and the age, rather than reading the array's
    padding below the first or past its end.
    """
    if not is_active(t):
        return 0.0
    a = age(t, life)
    if a < data.rate_age_first() or a > data.rate_age_last():        # noqa: F821
        raise ValueError(
            f"point_id {point_id()}: {data.ci_rate_file} is interpolated at "  # noqa: F821
            f"attained ages {data.rate_age_first()} to "                       # noqa: F821
            f"{data.rate_age_last()}, Data's rate_age_min to rate_age_max, "   # noqa: F821
            f"not at {a}")
    return float(data.i_ci_array()[rate_group(life), a])             # noqa: F821


def mort_rate(t, life):
    """q_d(a): the best-estimate annual mortality rate for ``life`` **[std]**.

    Never a decrement on its own: on this product mortality enters only through
    :func:`claim_rate`, net of the overlap factor.  A **[std]** proxy shaped like a
    scaled population table, not an ONS value.  Zero outside cover, before the rates are
    read.

    Inside it, this is the one cell that reads ``Data.q_d_array``, :mod:`~.CI_UK_S`'s
    ``pivot_interp(age, sex, smoker, "q_d")`` at every attained age the contract admits, at
    the life's row and attained age, and an age outside the array's raises ``ValueError``,
    naming the point and the age, as :func:`ci_rate_base` does.
    """
    if not is_active(t):
        return 0.0
    a = age(t, life)
    if a < data.rate_age_first() or a > data.rate_age_last():        # noqa: F821
        raise ValueError(
            f"point_id {point_id()}: {data.ci_rate_file} is interpolated at "  # noqa: F821
            f"attained ages {data.rate_age_first()} to "                       # noqa: F821
            f"{data.rate_age_last()}, Data's rate_age_min to rate_age_max, "   # noqa: F821
            f"not at {a}")
    return float(data.q_d_array()[rate_group(life), a])              # noqa: F821


def ci_trend_factor(t):
    """(1 + tau)^(t // 12): the CI trend factor in month t **[std]**, valuation clock.

    Zero trend in the base run.  It is the notes' *first*-listed sensitivity anyway:
    diagnosis rates move with medical practice, and the covered event itself moves when
    the ABI revises its model definitions - the 2021/22 review broadened Alzheimer's to
    all dementia, tightened cancer staging and excluded myocardial injury from heart
    attack.  Those are **step** changes that no trend parameter anticipates, so the
    basis must be re-mapped at each definition generation rather than trended through
    one.

    A calendar trend: ``t`` counts months from the valuation date, the date the diagnosis
    table states its basis at, so the factor is 1 through the first valuation year and
    steps on each anniversary of the valuation date, for every point alike, whatever its
    age (USLIB-SEC-PLAN.md D7).  :mod:`~.CI_UK_S` trends from issue,
    ``(1 + tau)^(y - 1)``; on a point issued at ``t = 0`` the two are the same.  The
    exponent is a whole number of years, 0 or more, in every month of the frame, and
    :func:`proj_len` holds ``ci_trend`` to a finite number, -1 or more, so the factor is
    a number, 0 or more.

    It passes the largest float within the longest frame only where ``ci_trend`` is above
    about 140,000 a year.  Python's float power raises ``OverflowError`` past the largest
    float, where C's ``pow`` gives an infinity, so where the power is infinite from a
    finite base the cell calls Python's own, which raises the platform's message in the
    compiled model as in modelx (USLIB-SEC-PLAN.md, *Record -- M22*); modelx never reaches
    the call, its own power raising first.
    """
    base = 1.0 + ci_trend                                            # noqa: F821
    n = t // 12
    factor = base ** n
    if factor - factor != 0.0 and base - base == 0.0:
        raise float.__pow__(base, n)
    return factor


def ci_sel_factor(t):
    """1 + eta once a review shock has occurred; 1 otherwise **[std]**.

    Healthier lives lapse first when premiums rise, so the lives remaining after a
    review shock carry loaded diagnosis rates.  Reachable only on the reviewable
    variant, and only once a review has actually raised premiums past the shock
    threshold; ``sel_lapse_ci_loading`` is 0.10 in the notes and the magnitude is a
    placeholder.

    On a point in force, a latch closed before the valuation date is history,
    :func:`ci_sel_latched_init` 1, and the factor stays at :func:`ci_sel_factor_init`,
    whatever it is: 1 for a latch closed at a loading of 0, or below 1.  Otherwise the
    latch closes at the first review from month 0 on, ``reviews_passed(t)`` past the
    reviews made before month 0, ``(duration_mth_init() - 1) // review_period_mths``, that
    raises the premium by ``review_prem_shock``, past ``review_lapse_threshold``: a review
    that falls at the valuation date closes it at ``t = 0``, at the References of the
    valuation date (USLIB-SEC-PLAN.md D6, precised at its M7).  On a point issued at or
    after the valuation date that is :mod:`~.CI_UK_S`'s latch.  Zero outside cover, where
    there is no rate to load.
    """
    if not is_active(t):
        return 0.0
    if not is_reviewable():
        return 1.0
    if ci_sel_latched_init() == 1:
        return ci_sel_factor_init()
    made = max(duration_mth_init() - 1, 0) // review_period_mths       # noqa: F821
    if reviews_passed(t) <= made:
        return 1.0
    if review_prem_shock <= review_lapse_threshold:                  # noqa: F821
        return 1.0
    return 1.0 + sel_lapse_ci_loading                                # noqa: F821


def ci_rate(t, life):
    """The CI diagnosis rate applied to ``life`` in month t: table x trend x selection.

    Capped at 1, the bound second, ``min(q, 1.0)``, so that a missing input, a NaN, stays
    NaN, where ``min(1.0, q)`` would read it as 1: :mod:`~.CI_UK_S`'s cap, and no
    departure.
    """
    return min(ci_rate_base(t, life) * ci_trend_factor(t) * ci_sel_factor(t), 1.0)


def claim_rate_life(t, life):
    """The combined annual claim decrement for one life: ``i_ci + q_d (1 - k)``.

    The overlap term is what stops the two rates being added.  See the Space docstring
    for why, and for the bounds on ``k``, which :func:`proj_len` holds to 0 to 1: past 1
    the overlap takes more than every death off the rate, below 0 adds more.  Capped at 1,
    the bound second, as :func:`ci_rate` is: the joint decrement in :func:`claim_rate` is a
    probability only when each life's rate is, and two lives past 1 would make it less
    than certain.
    """
    return min(ci_rate(t, life)
               + mort_rate(t, life) * (1.0 - overlap_k), 1.0)        # noqa: F821


def claim_rate(t):
    """q_claim(a): the combined annual claim decrement applied to the policy.

    One life's rate on a single-life policy; on a joint first-event policy the joint
    decrement ``1 - (1 - q_1)(1 - q_2)`` **[std]** on one policy, which pays once and
    ends.  Capped at 1, the bound second, ``min(q, 1.0)``, so that a missing input, a
    NaN, stays NaN, where ``min(1.0, q)`` would read it as 1.
    """
    q1 = claim_rate_life(t, 1)
    if not is_joint():
        return min(q1, 1.0)
    q2 = claim_rate_life(t, 2)
    return min(1.0 - (1.0 - q1) * (1.0 - q2), 1.0)


def claim_rate_paid(t):
    """q_pay(a): the part of the claim decrement that pays the main benefit.

    The whole of it on the **accelerated** contract, where death and CI both pay ``SA``
    and the 14-day survival period is cash-flow-neutral.  On the **standalone**
    contract only diagnoses that survive the period pay, ``i_ci(1 - delta)``; deaths pay
    nothing and neither do diagnoses followed by death inside the period.  The overlap
    factor ``k`` belongs to the non-paying exit and never appears here - applying it to
    the paid decrement understates claims, which is the mirror image of the
    double-counting pitfall.  The standalone rate is capped at 1, the bound second, as
    :func:`claim_rate` is, and ``delta``, the share of the diagnoses that do not pay, is
    held to 0 to 1 by :func:`proj_len`, off which the paid or the exit rate is negative.
    The contract is read from its flag, :func:`is_accelerated`.
    """
    if is_accelerated():
        return claim_rate(t)
    return min(ci_rate(t, 1) * (1.0 - survival_slip), 1.0)           # noqa: F821


def claim_rate_mth(t):
    """q_m(t) = 1 - (1 - q_claim)^(1/12): the monthly combined decrement **[std]**.

    This is what runs the in-force off, on both contract types: the standalone variant
    terminates on death as well, it simply pays nothing for it.
    """
    return 1.0 - (1.0 - claim_rate(t)) ** (1.0 / 12.0)


def claim_rate_paid_mth(t):
    """q_pay_m(t) = 1 - (1 - q_pay)^(1/12): the monthly paying decrement.

    Equal to :func:`claim_rate_mth` on the accelerated contract, where every claim pays.
    """
    return 1.0 - (1.0 - claim_rate_paid(t)) ** (1.0 / 12.0)


def claim_rate_exit_mth(t):
    """q_exit_m(t): the monthly decrement that terminates the policy without paying.

    Defined as the **residual** ``q_m - q_pay_m`` rather than by converting ``q_exit``
    independently, so that the paying and non-paying parts sum exactly to the decrement
    that runs the in-force off.  Converting both annual parts independently would leave
    their sum slightly below ``q_m``: the notes' additive annual split and their
    ``1 - (1 - q)^(1/12)`` conversion are inconsistent at second order.
    :func:`check_claim_split` bounds the difference rather than hiding it.  Zero on the
    accelerated contract.
    """
    return claim_rate_mth(t) - claim_rate_paid_mth(t)


def ap_rate(t):
    """a(x) = 0.15 i_ci(a): the annual additional-payment claim frequency **[std]**.

    A **frequency**, not a probability: additional-payment conditions are payable more
    than once across the schedule, subject to one claim per condition, and they never
    terminate the policy.  So it has no cap of its own, but it takes :func:`ci_rate`'s,
    which caps ``i_ci`` at 1: the frequency is at most ``ap_freq_factor``, and a NaN
    diagnosis rate reaches it as NaN.

    That bounds ``ap_freq_factor``.  The month's additional payments per policy in force
    are :func:`ap_rate_mth`, ``ap_freq_factor x ci_rate(t, 1) / 12``, and the diagnosis
    rate is at most 1 at any rate the model accepts, so they are at most
    ``ap_freq_factor / 12``: one claim a month per policy in force or fewer while the
    factor is at most 12, and none fewer than none while it is 0 or more.
    :func:`proj_len` refuses it outside 0 to 12.
    """
    return ap_freq_factor * ci_rate(t, 1)                            # noqa: F821


def ap_rate_mth(t):
    """a_m(t) = a(x)/12: the monthly additional-payment frequency **[std]**.

    Divided by twelve rather than transformed by ``1 - (1 - a)^(1/12)``, because a
    frequency of repeatable events has no survival transform to apply.  The notes use
    the same approximation and say so.
    """
    return ap_rate(t) / 12.0


def child_rate_mth():
    """lambda_m = lambda_ch/12: the monthly children's-cover claim frequency **[std]**.

    Flat in age and duration, and zero if children's cover is not active.  Like the
    additional-payment frequency it is per-year events divided by twelve, not a
    probability conversion.  It is the month's children's claims per policy in force, so
    ``child_freq``, the claims a year, is at most 12 for it to be one or fewer, and 0 or
    more for it to be none fewer than none: :func:`proj_len` refuses it outside 0 to 12.
    """
    if not children_cover():
        return 0.0
    return child_freq / 12.0                                         # noqa: F821


def reviews_passed(t):
    """The number of premium reviews already applied at month t, on the policy clock.

    Reviews fall every ``review_period_mths`` policy months from the fifth anniversary
    [S3][S4], which is the start of policy month 60, so the first bites there - the month
    that opens the sixth policy year: ``duration_mth(t) // review_period_mths``.  On a
    point in force those before month 0, the first
    ``(duration_mth_init() - 1) // review_period_mths``, were made before the valuation
    instant, and their premium changes are history; the later ones apply
    ``review_prem_shock``, a review that falls at the valuation date the first of them
    (USLIB-SEC-PLAN.md D6, precised at its M7).  :mod:`~.CI_UK_S` divides ``t``, the same
    month only on a point issued at ``t = 0``.  Always zero on guaranteed-premium
    business, where the premium cannot be changed at all, and outside cover.  An int in
    every month: the period is read as the int it is, :func:`proj_len` having held it to
    a whole number, so that a period written ``60.0`` counts reviews as 60 does, and not
    as floats.
    """
    if not is_active(t):
        return 0
    if not is_reviewable():
        return 0
    return duration_mth(t) // int(review_period_mths)                # noqa: F821


def review_prem_change(t):
    """The premium change the review under way in month t made: its rho.

    The review under way is the last at or before month t.  Made before month 0, on a
    point in force, it is history, :func:`review_prem_shock_init`; made from month 0 on,
    a review that falls at the valuation date among them, ``review_prem_shock``, the change
    assumed at each review from the valuation instant on (USLIB-SEC-PLAN.md D6, precised at
    its M7).  :func:`review_shock_active` and :func:`lapse_rate` read it only inside the
    review's twelve-month window, so the opening column is read only while a review before
    the valuation date is still inside its window: on a point valued on a review month,
    never, that review opening its own window at today's change.  0 before the first
    review, and outside cover.
    """
    if not is_active(t) or reviews_passed(t) < 1:
        return 0.0
    made = max(duration_mth_init() - 1, 0) // review_period_mths       # noqa: F821
    if reviews_passed(t) == made:
        return review_prem_shock_init()
    return review_prem_shock                                         # noqa: F821


def review_shock_active(t):
    """Whether month t falls in the twelve months after a premium-raising review.

    The window a review shock lapse applies in: the policy months from a review,
    ``duration_mth(t) % review_period_mths`` below 12, after a review whose premium change,
    :func:`review_prem_change`, is above ``review_lapse_threshold``.  A review that raises
    premiums by less than the threshold produces no shock at all.  The window is asked
    first, so a change is read inside a window alone; and the change is compared as
    :mod:`~.CI_UK_S` compares it, so a NaN change is read as a shock there too.  False
    outside cover.  The period is read as an int, as :func:`reviews_passed` reads it.
    """
    if not is_active(t) or reviews_passed(t) < 1:
        return False
    if duration_mth(t) % int(review_period_mths) >= 12:              # noqa: F821
        return False
    if review_prem_change(t) <= review_lapse_threshold:              # noqa: F821
        return False
    return True


def idx_increase():
    """The cover increase offered at each anniversary under the indexation option.

    ``min(max(RPI, 0), 10%)`` [S1][S4] on a flat 3% RPI scenario **[std]**: ``rpi_rate``
    is the RPI assumed from the valuation instant on, an anniversary at the valuation
    date's increase among them; the increases given before month 0 are the opening state,
    :func:`idx_factor_init`.
    """
    return min(max(rpi_rate, 0.0), idx_cover_cap)                    # noqa: F821


def idx_factor(t):
    """idx(t): the cumulative **cover** indexation factor in month t.

    Steps on the policy anniversary and is level through the policy year:
    :func:`idx_factor_init`, the factor entering month 0, 1 at issue, then one factor of
    ``1 + idx_increase()`` for each anniversary from month 0 on, month 0's own among them:
    ``duration(t)`` less the anniversaries passed before month 0,
    ``(duration_mth_init() - 1) // 12`` on a point in force and none on one issued at or
    after the valuation date.  The increases before the valuation instant are history,
    carried in, and those from it on are projected at ``rpi_rate``, an anniversary that
    falls at the valuation date the first of them, as on a point issued then
    (USLIB-SEC-PLAN.md D6, precised at its M7).  1 throughout if the option is not
    elected, and 0 outside cover, where there is no cover to index.

    The exponent is a whole number of years, 0 or more, so the power is real whatever the
    base.  It passes the largest float only where the References put the increase above
    about 2 million a year, which the shipped cap, 10%, does not; there the cell raises
    Python's ``OverflowError`` in both engines, as :func:`ci_trend_factor` does.
    """
    if not is_active(t):
        return 0.0
    if not indexation():
        return 1.0
    base = 1.0 + idx_increase()
    n = duration(t) - max(duration_mth_init() - 1, 0) // 12
    factor = base ** n
    if factor - factor != 0.0 and base - base == 0.0:
        raise float.__pow__(base, n)
    return idx_factor_init() * factor


def idx_prem_factor(t):
    """idx_p(t): the cumulative **premium** indexation factor in month t.

    The premium rises by ``min(1.5 x increase, 15%)`` for a cover increase of
    ``increase`` [S1][S4] - the same x1.5 factor the term assurance chassis carries - on
    the same anniversary steps as the cover factor, from :func:`idx_prem_factor_init`,
    month 0's own among them.  1 if the option is not elected, and 0 outside cover.

    The exponent is a whole number of years, as :func:`idx_factor`'s is, and the power
    passes the largest float only where the References put the step above about 2 million
    a year, which the shipped cap, 15%, does not; there the cell raises Python's
    ``OverflowError`` in both engines, as :func:`ci_trend_factor` does.
    """
    if not is_active(t):
        return 0.0
    if not indexation():
        return 1.0
    step = min(idx_prem_mult * idx_increase(), idx_prem_cap)         # noqa: F821
    base = 1.0 + step
    n = duration(t) - max(duration_mth_init() - 1, 0) // 12
    factor = base ** n
    if factor - factor != 0.0 and base - base == 0.0:
        raise float.__pow__(base, n)
    return idx_prem_factor_init() * factor


def review_prem_factor(t):
    """The premium factor the reviews have given by month t.

    :func:`review_prem_factor_init`, the factor entering month 0, 1 at issue, then one
    factor of ``1 + review_prem_shock`` for each review from month 0 on, month 0's own
    among them: ``reviews_passed(t)`` less the reviews made before month 0,
    ``(duration_mth_init() - 1) // review_period_mths`` on a point in force and none on
    one issued at or after the valuation date.  The changes made before the valuation
    instant are history; those from it on are projected at ``review_prem_shock``, a review
    that falls at the valuation date the first of them, as on a point issued then
    (USLIB-SEC-PLAN.md D6, precised at its M7).  :mod:`~.CI_UK_S` has no such cell: it
    multiplies the premium by ``(1 + review_prem_shock)`` to the power of every review
    passed since issue, the same number on a point issued at ``t = 0``.  1 on a guaranteed
    point, and 0 outside cover.

    The exponent is a whole number of reviews, 0 or more, so the power is real whatever
    the base, which :func:`proj_len` holds to 0 or more.  The reviews before month 0 divide
    by the period as the model holds it, as :func:`ci_sel_factor` and
    :func:`review_prem_change` count them too: compiled, a C integer, where ``int`` would
    make the count a Python object; in modelx, a period written ``60.0`` counts them as the
    float ``1.0``, which moves no value.  It passes the largest float only where
    ``review_prem_shock`` is far outside the product: above about 1.8e34 at the shipped
    60-month period, nine reviews in the longest cover, and above about 2.3 at a period of
    one month, 600; there the cell raises Python's ``OverflowError`` in both engines, as
    :func:`ci_trend_factor` does.
    """
    if not is_active(t):
        return 0.0
    if not is_reviewable():
        return 1.0
    base = 1.0 + review_prem_shock                                   # noqa: F821
    made = max(duration_mth_init() - 1, 0) // review_period_mths       # noqa: F821
    n = reviews_passed(t) - made
    factor = base ** n
    if factor - factor != 0.0 and base - base == 0.0:
        raise float.__pow__(base, n)
    return review_prem_factor_init() * factor


def premium_pp(t):
    """P(t): the monthly premium per policy in month t.

    The outset premium, indexed if the option is elected, and multiplied by the reviews'
    factor, :func:`review_prem_factor`.  On guaranteed-premium business - the base run - it
    is level for the whole term but for indexation, which is what puts every month of
    premium inside the Solvency UK contract boundary.  Zero outside cover.
    """
    if not is_active(t):
        return 0.0
    p = premium_mth_pp() * idx_prem_factor(t)
    return p * review_prem_factor(t)


def premiums(t):
    """Premium income at the beginning of month t, an inflow.

    Carried on the policies in force at the start of the month, :func:`pols_if`.
    """
    return premium_pp(t) * pols_if(t)


def lapse_rate_base(t):
    """The table annual lapse rate in month t **[std]**, before any review shock.

    10 / 8 / 6 / 6 / 6 / 4 percent by policy year.  Protection lapse is duration-skewed
    - buyer's remorse, remortgaging, distribution churn - and levels off later; UK CI
    lapse studies are proprietary, so the levels are calibrations to be replaced with
    the user's own experience.  The table is keyed by the contractual 1-based policy
    year, read at :func:`policy_year` ``(t)`` on the policy clock; policy years beyond the
    table take its last row, ``Data.lapse_last_year``.

    Zero outside cover, where the month has no policy year: before issue
    :func:`policy_year` is 0 or less, where :mod:`~.CI_UK_S`'s lookup raised ``KeyError``.
    Inside it, this is the one cell that reads ``Data.lapse_table_array``, indexed by the
    policy year, which is 1 or more in cover and at most the table's last, since every
    later year is read at it: so both ends of the table hold the key, and no read meets the
    array's padding at index 0.
    """
    if not is_active(t):
        return 0.0
    y = min(policy_year(t), data.lapse_last_year())                  # noqa: F821
    return float(data.lapse_table_array()[y])                        # noqa: F821


def lapse_rate(t):
    """w(y): the **annual** lapse rate applying in month t, review shock included.

    ``min(0.30, w(y) + 2.0 max(0, rho - 0.05))`` in the twelve months after a review that
    raises premiums by more than 5% **[std]**, ``rho`` the change that review made,
    :func:`review_prem_change`, and the table rate otherwise; the bounds in
    :mod:`~.CI_UK_S`'s order.  Review-driven shocks are the dominant behavioural risk on
    reviewable business, where one insurer's review changes are subject to no stated
    limit at all; the slope and the cap are placeholders.  :func:`proj_len` holds the
    slope to a finite number, 0 or more, the threshold to a finite number and the cap to 0
    to 1 on a reviewable point, so that ``min`` here, its bound first, never meets a NaN
    from them.

    There is no interest-sensitive dynamic lapse anywhere in this model.  With no cash
    value and no credited rate there is nothing to arbitrage, so the machinery the
    accumulation products in this library carry is deliberately absent.
    """
    w = lapse_rate_base(t)
    if not review_shock_active(t):
        return w
    shock = w + review_lapse_slope * max(                            # noqa: F821
        0.0, review_prem_change(t) - review_lapse_threshold)         # noqa: F821
    return min(review_lapse_cap, shock)                              # noqa: F821


def lapse_rate_mth(t):
    """w_m(t) = 1 - (1 - w(y))^(1/12): the monthly lapse rate **[std]**."""
    return 1.0 - (1.0 - lapse_rate(t)) ** (1.0 / 12.0)


def pols_if(t):
    """l(t): the number of policies in force at time t, the count that weights row t.

    ``pols_if_at(t, BEF_DECR)``: the count carried in from month t - 1, plus month t's
    new business, before month t's decrements.  On a point issued at ``t = 0`` that is
    exactly :mod:`~.CI_UK_S`'s ``pols_if``, the notes' ``l(t)``, which follows the notes'
    recursion ``l(t + 1) = l(t)(1 - q_m(t))(1 - w_m(t))``.  It is
    ``basiclife.BasicTerm_SE``'s ``BEF_DECR`` count, not its ``pols_if``.  Zero outside
    cover: before issue, and from ``t = proj_len()`` on, when the term has ended.
    """
    return pols_if_at(t, BEF_DECR)                                   # noqa: F821


def pols_if_at(t, timing):
    """The number of policies in force at a point inside month t.

    ``BEF_NB``
        The count carried in from month t - 1, before month t's new business: the
        survivors of month t - 1's claims and lapses, out of month t - 1's
        ``BEF_DECR`` count.  At :func:`t_entry`, the first month on the books, it is
        :func:`pols_if_init`, the count in force at the valuation date (0 for a point
        issued at or after it), and the recursion reads no earlier month.  Zero outside
        cover, so the survivors of the last covered month leave as
        :func:`pols_maturity`.

    ``BEF_DECR``
        ``BEF_NB`` plus :func:`pols_new_biz`: l(t), the count that weights month t,
        which :func:`pols_if` returns.

    ``BEF_LAPSE``
        after main-benefit claims, before lapses - the notes' processing order is
        **claim before lapse** **[std order]**, so this is the population lapses are
        taken from.

    ``AFT_DECR``
        the notes' ``l(t + 1)``, the end-of-month state, and zero from the last covered
        month on, because the cover expires at its end.  It is ``BEF_NB`` at t + 1
        exactly, one product in one order.

    The additional-payment and children's-cover claims appear at none of these points.
    They are non-terminating: only the main benefit ends the policy.  These are int
    References, 0 to 3, named as :mod:`~.CI_UK_S`'s strings (the Space docstring's
    *Codes*).  ``BEF_NB`` is the one timing running in force adds, as
    ``basiclife.BasicTerm_SE`` names it; the other three are :mod:`~.CI_UK_S`'s, and any
    other raises.  ``BEF_NB`` forms month t - 1's ``BEF_DECR`` count itself, as ``BEF_NB``
    plus :func:`pols_new_biz` at t - 1, the same sum in the same order, rather than calling
    for it.  So the chain of calls from
    month t back to :func:`t_entry` is one cell a month, where :mod:`~.CI_UK_S`'s
    ``pols_if`` chain runs three: a compiled model runs that chain on the C stack.
    """
    if timing == BEF_NB:                                             # noqa: F821
        if not is_active(t):
            return 0.0
        if t == t_entry():
            return pols_if_init()
        return ((pols_if_at(t - 1, BEF_NB) + pols_new_biz(t - 1))       # noqa: F821
                * (1.0 - claim_rate_mth(t - 1)) * (1.0 - lapse_rate_mth(t - 1)))
    if timing == BEF_DECR:                                           # noqa: F821
        return pols_if_at(t, BEF_NB) + pols_new_biz(t)                 # noqa: F821
    if timing == BEF_LAPSE:                                          # noqa: F821
        if not is_active(t):
            return 0.0
        return pols_if(t) * (1.0 - claim_rate_mth(t))
    if timing == AFT_DECR:                                           # noqa: F821
        if not is_active(t) or duration_mth(t) >= expiry_mth() - 1:
            return 0.0
        return pols_if_at(t, BEF_LAPSE) * (1.0 - lapse_rate_mth(t))    # noqa: F821
    raise ValueError("invalid timing")


def pols_new_biz(t):
    """The number of policies issued in month t: ``policy_count()`` in the issue month.

    The issue month is the one with ``duration_mth(t) == 0``: ``t = 0`` for a point
    issued at the valuation date, ``t = k`` for one issued ``k`` months later.  A point
    already in force at the valuation date has none.
    """
    return policy_count() if duration_mth(t) == 0 else 0.0


def pols_claim(t):
    """Main-benefit claims in month t: death, terminal illness or CI diagnosis.

    The whole combined decrement, including the standalone contract's non-paying
    deaths - they terminate the policy just the same.  What is *paid* on them is
    :func:`claims` ``(t, MAIN)``.  Zero outside cover, before any rate is read.
    """
    return pols_if(t) * claim_rate_mth(t) if is_active(t) else 0.0


def pols_lapse(t):
    """Lapses at the end of month t, taken from the non-claiming survivors.

    Pays nothing: there is no surrender or paid-up value [S1][S4][S5].  The 60-day
    grace period is not modelled separately - the lapse rates are assumed already to
    reflect grace-period cures **[std]**.  Zero outside cover, before any rate is read.
    """
    if not is_active(t):
        return 0.0
    return pols_if_at(t, BEF_LAPSE) * lapse_rate_mth(t)                # noqa: F821


def pols_maturity(t):
    """Policies whose cover expires at the end of the term; zero in every other month.

    Non-zero only in the last covered month, ``duration_mth(t) = expiry_mth() - 1``,
    which is the frame's last row, ``t = proj_len() - 1``.  Not a decrement and not a
    benefit - the contract runs out, with no maturity value - but needed for the in-force
    roll-forward to close; see :func:`check_pols_roll_fwd`.
    """
    if duration_mth(t) != expiry_mth() - 1:
        return 0.0
    return pols_if_at(t, BEF_LAPSE) * (1.0 - lapse_rate_mth(t))        # noqa: F821


def benefit_pp(t, kind):
    """The benefit amount per policy in month t, by kind.

    ``MAIN``
        SA(t), the sum assured, indexed if the option is elected: on a point in force, the
        sum assured at issue times the factor given to date, :func:`idx_factor_init`, and
        each increase after.

    ``AP``
        the additional-payment benefit ``min(25% of SA(t), £25,000)``
        [S1][S4][S11] - £25,000 at the anchor cell, and **non-depleting**: it
        does not reduce the main benefit.

    ``CHILD``
        children's cover ``min(50% of SA(t), £25,000)`` [S1], also
        non-depleting, and zero if the cover is not active.  The £4,000 child
        funeral benefit is excluded as de minimis **[std]**.

    Both caps are struck against the **indexed** sum assured **[std]**: the notes state
    them against ``SA`` without saying which, and holding them to a frozen outset value
    would let the ancillary benefits shrink in real terms while the main one did not.
    In practice the cash cap binds at the anchor cell either way.  Each is written with
    its bound second, as :mod:`~.CI_UK_S` writes it, so a NaN share stays NaN.  Zero
    outside cover.

    These are int References, 0 to 2, named as :mod:`~.CI_UK_S`'s strings (the Space
    docstring's *Codes*), the codes of :func:`claims`' first three kinds, and any other
    raises, ``LAPSE`` and ``ALL`` among them.
    """
    if kind == MAIN:                                                 # noqa: F821
        return sum_assured() * idx_factor(t) if is_active(t) else 0.0
    if kind == AP:                                                   # noqa: F821
        if not is_active(t):
            return 0.0
        return min(ap_share * benefit_pp(t, MAIN), ap_cap)           # noqa: F821
    if kind == CHILD:                                                # noqa: F821
        if not children_cover() or not is_active(t):
            return 0.0
        return min(child_share * benefit_pp(t, MAIN), child_cap)     # noqa: F821
    raise ValueError("invalid kind")


def claims(t, kind):
    """Benefit outgo in month t, by kind, and the four kinds' total.

    ``MAIN``
        ``SA(t) x q_pay_m(t) x l``, the terminating benefit.  On the
        accelerated contract every claim pays; on the standalone one only
        diagnoses surviving the 14-day period do.

    ``AP``
        ``B_AP x a_m(t) x l``, non-terminating and non-depleting.

    ``CHILD``
        ``B_ch x lambda_m x l``, likewise.

    ``LAPSE``
        zero, always.  There is no surrender or paid-up value [S1][S4][S5];
        the kind exists so that the zero is stated rather than inferred.

    ``ALL``
        the four kinds' total, :mod:`~.CI_UK_S`'s ``claims(t)``, whose ``kind=None``
        sums the four with Python's ``sum``, which compiles to no C.  ``sum`` of floats
        is compensated since Python 3.12: it carries the rounding error of each
        addition, Neumaier's way, and adds it back once at the end, where it is finite
        and not 0.  The main claim, the additional payment and the children's claim are
        non-zero together in most months of cover, and there a total written left to
        right, ``0.0 + MAIN + AP + CHILD + LAPSE``, differs from ``sum``'s in the last
        bit.  So each addition is written as ``sum`` makes it, in explicit statements,
        with no tuple and no loop, which would not compile to C: ``0.0 +`` the first
        kind is ``sum``'s start, the int 0, which turns a negative zero to ``0.0``; each
        later kind is added with its rounding error carried, the larger of the two in
        size first; and the final test, ``abs(c) <= 1.7976931348623157e308``, the
        largest double, is ``sum``'s test that the carried error is finite, false for an
        infinity or a NaN, without a subtraction a compiler might fold.  So the total is
        :mod:`~.CI_UK_S`'s float in every month, and each step is one IEEE operation in
        both engines, since nothing in the build lets the compiler reassociate or fuse a
        multiply and an add (``-ffp-contract=off``).

    Each kind is zero outside cover, before any rate is read.  These are int References,
    0 to 4, named as :mod:`~.CI_UK_S`'s strings (the Space docstring's *Codes*), and any
    other raises.
    """
    if kind == MAIN:                                                 # noqa: F821
        if not is_active(t):
            return 0.0
        return benefit_pp(t, MAIN) * claim_rate_paid_mth(t) * pols_if(t)  # noqa: F821
    if kind == AP:                                                   # noqa: F821
        if not is_active(t):
            return 0.0
        return benefit_pp(t, AP) * ap_rate_mth(t) * pols_if(t)       # noqa: F821
    if kind == CHILD:                                                # noqa: F821
        if not is_active(t):
            return 0.0
        return benefit_pp(t, CHILD) * child_rate_mth() * pols_if(t)  # noqa: F821
    if kind == LAPSE:                                                # noqa: F821
        return 0.0
    if kind == ALL:                                                  # noqa: F821
        f = 0.0 + claims(t, MAIN)                                    # noqa: F821
        c = 0.0
        x = claims(t, AP)                                            # noqa: F821
        s = f + x
        if abs(f) >= abs(x):
            c = c + ((f - s) + x)
        else:
            c = c + ((x - s) + f)
        f = s
        x = claims(t, CHILD)                                         # noqa: F821
        s = f + x
        if abs(f) >= abs(x):
            c = c + ((f - s) + x)
        else:
            c = c + ((x - s) + f)
        f = s
        x = claims(t, LAPSE)                                         # noqa: F821
        s = f + x
        if abs(f) >= abs(x):
            c = c + ((f - s) + x)
        else:
            c = c + ((x - s) + f)
        f = s
        if c != 0.0 and abs(c) <= 1.7976931348623157e308:
            f = f + c
        return f
    raise ValueError("invalid kind")


def claim_expenses(t):
    """E_cl x q_m(t) x l: the claim handling expense in month t **[std]**.

    £250 per main claim, uninflated, carried on the **whole** combined decrement rather
    than on the paying part: a notified death on a standalone contract costs the
    insurer to assess even though it pays nothing.  That is the notes' own formula.
    Kept out of :func:`expenses` because the notes' worked example prints the two as
    separate columns.  Zero outside cover, before any rate is read.
    """
    if not is_active(t):
        return 0.0
    return expense_claim * claim_rate_mth(t) * pols_if(t)            # noqa: F821


def inflation_factor(t):
    """The expense inflation factor in month t, ``(1 + pi)^(t // 12)`` **[std]**.

    On the **valuation** clock: ``t`` counts months from the valuation date, so the
    maintenance charge it inflates is in valuation-date pounds, whatever the policy's
    age, and every point of a block inflates alike, stepping on each anniversary of the
    valuation date.  :mod:`~.CI_UK_S` inflates from issue, ``(1 + pi)^(y - 1)``, as the
    notes write it; on a point issued at ``t = 0`` the two are the same.  The initial
    expense is not inflated (see :func:`expenses`).  :func:`proj_len` holds
    ``inflation_rate`` to a finite number, -1 or more, so the factor is a number, 0 or more.

    The exponent is a whole number of years, so the power is real whatever the base.  It
    passes the largest float within the longest frame only where ``inflation_rate`` is
    above about 140,000 a year; there the cell raises Python's ``OverflowError`` in both
    engines, as :func:`ci_trend_factor` does.
    """
    base = 1.0 + inflation_rate                                      # noqa: F821
    n = t // 12
    factor = base ** n
    if factor - factor != 0.0 and base - base == 0.0:
        raise float.__pow__(base, n)
    return factor


def expenses(t):
    """E0 and E_m(y): the initial and maintenance expense in month t **[std]**.

    £200 per policy issued, ``expense_acq * pols_new_biz(t)``: in the issue month, never
    for a point already in force at the valuation date, and not inflated, as in
    ``basiclife.BasicTerm_SE``.  :mod:`~.CI_UK_S` charges it on the count at ``t = 0``,
    which on a point issued then is the count issued.  Then £30 per policy per year - a
    twelfth of it each month - inflating at 3% on the valuation clock, both at the
    beginning of the month.  There is **no commission line** on this product: the notes
    fold acquisition cost into the initial expense rather than carrying commission
    separately as the term assurance chassis does.
    """
    return (expense_acq * pols_new_biz(t)                            # noqa: F821
            + expense_maint / 12.0 * inflation_factor(t) * pols_if(t))  # noqa: F821


def net_cf(t):
    """CF(t): the net cash flow of month t, **income positive**.

    Premiums less main, additional-payment and children's claims, claim expense and
    expenses.  The notes' own sign, and the library-wide one, so there is no
    outgo-positive ``liability_cf`` companion.

    One caveat for a reader checking the worked example by eye: the notes' *Net CF*
    column **excludes the initial expense**, showing 31.88 in the anchor cell's issue
    month and noting the £200 separately as taking the month to -168.12.  This cells is
    the total, so on the twin issued at the valuation date ``net_cf(0)`` is -168.12 and the
    notes' column is ``net_cf(0) + 200``.  The claims are the four kinds' total,
    ``claims(t, ALL)``.
    """
    return premiums(t) - claims(t, ALL) - claim_expenses(t) - expenses(t)  # noqa: F821


def check_pols_roll_fwd_resid(t):
    """The in-force roll-forward residual in month t; zero everywhere.

    ``pols_if(t) - pols_if_at(t + 1, BEF_NB) - main claims - lapses - expiries``, where
    the count carried into the next month is taken before its new business, which is no
    part of month t's movement.  The additional-payment and children's-cover claims are
    absent by design: they are non-terminating, and their appearance here would be the
    notes' fourth pitfall.  Expiries are non-zero only in the last covered month, where
    the survivors neither claim nor lapse - their cover runs out.
    """
    return (pols_if(t) - pols_if_at(t + 1, BEF_NB)                    # noqa: F821
            - pols_claim(t) - pols_lapse(t) - pols_maturity(t))


def check_pols_roll_fwd():
    """True when the in-force roll-forward closes in every month of the frame.

    The library-wide form of a roll-forward check: no argument, one bool over all t, so
    one test can call it across every model.  :func:`check_pols_roll_fwd_resid` gives
    the signed residual of the month that failed.  The tolerance scales with
    ``policy_count()``, since the residual accumulates rounding on that many policies,
    in force at the valuation date or issued after it.
    """
    return all(abs(check_pols_roll_fwd_resid(t)) <= 1e-10 * max(policy_count(), 1.0)
               for t in range(proj_len()))


def check_claim_split_resid(t):
    """How far the residual exit rate is from an independently converted ``q_exit``.

    :func:`claim_rate_exit_mth` is defined as ``q_m - q_pay_m`` so that the split is
    exact; the notes' own construction would instead convert the annual ``q_exit``
    directly.  The two differ because the notes add the annual parts but convert them
    geometrically, which cannot both hold.  This residual is that inconsistency, made
    visible: it is zero on the accelerated contract and of order 1e-5 on the standalone
    one at the shipped rates, growing with the level of the rates.  Zero outside cover,
    before any rate is read.

    ``q_exit``, ``q_d (1 - k) + i_ci delta``, is the one annual rate :mod:`~.CI_UK_S`
    leaves uncapped, since it is never a decrement: an extrapolated mortality rate can
    take it past 1, where its monthly conversion has no real value and
    :mod:`~.CI_UK_S`'s residual is a complex number.  It raises ``ValueError`` there,
    naming the point, the month, the rate and the References it is made of, in the month
    it first passes 1, rather than compare a number that is not one.  The contract is read
    from its flag, :func:`is_accelerated`.
    """
    if not is_active(t) or is_accelerated():
        return 0.0
    q_exit = (mort_rate(t, 1) * (1.0 - overlap_k)                    # noqa: F821
              + ci_rate(t, 1) * survival_slip)                       # noqa: F821
    if q_exit > 1.0:
        raise ValueError(
            f"point_id {point_id()}: the annual exit rate q_exit({t}), q_d (1 - "
            f"overlap_k) + i_ci survival_slip, is {q_exit}, past 1, at q_d "
            f"{mort_rate(t, 1)} and i_ci {ci_rate(t, 1)} under overlap_k "
            f"{float(overlap_k)} and survival_slip {float(survival_slip)}: "  # noqa: F821
            f"its monthly rate has no real value")
    return claim_rate_exit_mth(t) - (1.0 - (1.0 - q_exit) ** (1.0 / 12.0))


def check_claim_split():
    """True when the paying/non-paying split stays inside ``claim_split_tol``.

    No argument, one bool over all t, the library-wide shape of a ``check_*`` cells.
    Unlike a roll-forward check this one is not an identity that must hold exactly - it
    bounds a known second-order artefact of the notes' two conventions - so its
    tolerance is a Reference rather than a machine epsilon, and moving that Reference is
    how a user states how much of the artefact they will accept.
    """
    return all(abs(check_claim_split_resid(t)) <= claim_split_tol    # noqa: F821
               for t in range(proj_len()))


def result_cf():
    """Result table of cashflows, one row per month ``t = 0 .. proj_len() - 1``.

    Row 0 is the valuation month for every model point, so the frames of a block line up
    and sum row by row.  A point issued after the valuation date has zeros until its issue
    month.  ``pols_if`` is the count that weights every cash flow on the same row.  The
    columns are :mod:`~.CI_UK_S`'s: ``net_cf`` carries the notes' own income-positive
    sign and **includes** the initial expense, unlike the notes' own Net CF column, and
    ``claims_lapse`` is a column of zeros by product design - there is no surrender value
    - and is published rather than dropped.
    """
    ts = list(range(proj_len()))
    return pd.DataFrame(                                             # noqa: F821
        {
            "pols_if": [pols_if(t) for t in ts],
            "premiums": [premiums(t) for t in ts],
            "claims_main": [claims(t, MAIN) for t in ts],              # noqa: F821
            "claims_ap": [claims(t, AP) for t in ts],                  # noqa: F821
            "claims_child": [claims(t, CHILD) for t in ts],            # noqa: F821
            "claims_lapse": [claims(t, LAPSE) for t in ts],            # noqa: F821
            "claim_expenses": [claim_expenses(t) for t in ts],
            "expenses": [expenses(t) for t in ts],
            "net_cf": [net_cf(t) for t in ts],
        },
        index=pd.Index(ts, name="t"),                                # noqa: F821
    )


def result_pols():
    """Result table of policy counts and decrement rates, one row per month t.

    The same rows as :func:`result_cf`, ``t = 0 .. proj_len() - 1``.  First the counts
    :func:`result_cf` weights its rows by, and how they move, as
    ``basiclife.BasicTerm_SE``'s ``result_pols`` sets them out: ``pols_if``, the count of
    month t; ``pols_new_biz``, the part of it issued in month t; then month t's main
    claims and lapses in processing order, and the expiries of the last covered month.
    Row by row, ``pols_if`` at ``t + 1`` is ``pols_if`` less the three outflows of month t,
    plus the new business of month ``t + 1``.  Then :mod:`~.CI_UK_S`'s other six columns:
    the end-of-month count, ``pols_if_aft_decr``, and the first life's diagnosis and
    mortality rates, the policy's annual and monthly claim rates and the annual lapse rate,
    which are 0 outside cover, where the model reads no rate.
    """
    ts = list(range(proj_len()))
    return pd.DataFrame(                                             # noqa: F821
        {
            "pols_if": [pols_if(t) for t in ts],
            "pols_new_biz": [pols_new_biz(t) for t in ts],
            "pols_claim": [pols_claim(t) for t in ts],
            "pols_lapse": [pols_lapse(t) for t in ts],
            "pols_maturity": [pols_maturity(t) for t in ts],
            "pols_if_aft_decr": [pols_if_at(t, AFT_DECR) for t in ts],  # noqa: F821
            "ci_rate": [ci_rate(t, 1) if is_active(t) else 0.0 for t in ts],
            "mort_rate": [mort_rate(t, 1) if is_active(t) else 0.0 for t in ts],
            "claim_rate": [claim_rate(t) if is_active(t) else 0.0 for t in ts],
            "claim_rate_mth": [claim_rate_mth(t) if is_active(t) else 0.0 for t in ts],
            "lapse_rate": [lapse_rate(t) if is_active(t) else 0.0 for t in ts],
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

MAIN = 0

AP = 1

CHILD = 2

LAPSE = 3

ALL = 4

issue_age_min = 18

issue_age_max = 64

policy_term_min = 5

policy_term_max = 50

expiry_age_max = 75

overlap_k = 0.1

survival_slip = 0.03

ci_trend = 0.0

ap_freq_factor = 0.15

ap_share = 0.25

ap_cap = 25000.0

child_freq = 0.0004

child_share = 0.5

child_cap = 25000.0

expense_acq = 200.0

expense_maint = 30.0

expense_claim = 250.0

inflation_rate = 0.03

rpi_rate = 0.03

idx_cover_cap = 0.1

idx_prem_mult = 1.5

idx_prem_cap = 0.15

review_period_mths = 60

review_prem_shock = 0.0

review_lapse_slope = 2.0

review_lapse_threshold = 0.05

review_lapse_cap = 0.3

sel_lapse_ci_loading = 0.1

claim_split_tol = 0.0001

pd = ("Module", "pandas")
