# modelx: pseudo-python
# This file is part of a modelx model.
# It can be imported as a Python module, but functions defined herein
# are model formulas and may not be executable as standard Python.

"""The by-policy projection of the :mod:`~.Term_UK_SEC` model; holds all formulas.

The Space is parameterized by ``idx``, the position of a model point in the table and in
every :mod:`~.Term_UK_SEC.Data` vector, as ``basiclife.BasicTerm_SC`` is: ``Projection[7]``
is an ItemSpace projecting the table's eighth row, model point 8, the twin of
:mod:`~.Term_UK_S`'s anchor cell in force five years, and :func:`point_id` is its label::

    >>> Projection[7].result_cf()          # one row per month from the valuation date
    >>> Projection[7].result_pols()        # the counts behind it
    >>> Projection[7].point_id()           # 8, the row's point_id
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

This is :mod:`~.Term_UK_S` taught to run in force at a valuation date, as lifelib's
``basiclife.BasicTerm_SE`` extends ``basiclife.BasicTerm_S``, and then made to compile, as
``basiclife.BasicTerm_SC`` is made from ``basiclife.BasicTerm_S``. A formula of
:mod:`~.Term_UK_S` is rewritten where it depends on where the projection starts, where it
must answer for a month outside cover, or where it read a policy month as ``t``; every
other formula is :mod:`~.Term_UK_S`'s own, the cap on mortality,
``min(q, 1.0)``, among them. ``products/term_assurance/model-sec.md`` lists the rewritten
cells with the reason for each. Making it compile changed how each cell reads its inputs
and spells its codes, and no number: every model point attribute a projection cell uses
is read as a number from a ``Data`` vector, every table as an array indexed by integers,
every timing and kind is an int code (*Codes*, below), and every text column is decoded
into the number a formula branches on.

.. rubric:: Input data

Inputs are **external files**: plain CSVs living in the model folder's parent
directory, ``products/term_assurance/``, read at run time rather than stored inside
the model. The model folder therefore holds nothing but formulas — no ``_data/``, no
IOSpec, no embedded values — so a diff of the model shows logic changes only, and an
input can be edited or swapped without rewriting the model. This follows
``annuallife.TradLife_A``; contrast ``basiclife.BasicTerm_S``, which keeps its inputs
*inside* the model through modelx's IOSpec machinery.

The consequence worth knowing: **the model is not portable on its own.** Copying the
``Term_UK_SEC`` folder without its parent's CSVs produces a model that reads and then
fails on first evaluation.

:func:`~.Term_UK_SEC.Data.input_dir` resolves the directory from ``_model.path.parent``
at run time, so the model works wherever the repository is checked out. The three
assumption tables are the files :mod:`~.Term_UK_S` reads, read in place; the model point
table and the waiver pipeline are this model's own. Each table has a filename Reference
and a reader Cells, both on :mod:`~.Term_UK_SEC.Data`, reached here through the ``data``
Reference:

======================  ==============================  ==========================
Reference               Cells                           File
======================  ==============================  ==========================
model_point_file        data.model_point_table()        model_point_table_sec.csv
wop_pipeline_file       data.wop_pipeline()             wop_pipeline_sec.csv
mort_table_file         data.mort_table()               mort_table.csv
select_factor_file      data.select_factor_table()      select_factor_table.csv
lapse_table_file        data.lapse_table()              lapse_table.csv
======================  ==============================  ==========================

No cell here but :func:`model_point`, a reporting cell, reads the readers' DataFrames,
and the label accessors read through it. Every other reads :mod:`~.Term_UK_SEC.Data`'s
vectors and arrays, one element at a time: a model point's attribute at its position,
``data.age_at_entry()[idx]``, decoded already into the number the formula needs; the
mortality table at a life's row and attained age,
``data.mort_table_array()[mort_group(life), age(t, life)]``; the select factors at the
select duration and the lapse table at the policy year; and the waiver pipeline at the
point and the lag, ``data.wop_deferred_init()[idx, k]``. ``Data``'s docstring lists them.

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
most ten years later. It is the technical notes' month index ``k``. Everything contractual
reads it: the completed policy years ``duration(t) = duration_mth(t) // 12``, which are the
select duration, the contractual 1-based label ``policy_year(t) = duration(t) + 1``, the
attained age ``age(t, life) = age_at_entry(life) + duration(t)``, and through them the
mortality and lapse tables, the decreasing schedule, the indexation anniversaries, the
annual premium, the renewal commission from the second policy year and the clawback
window. Model point 8, :mod:`~.Term_UK_S`'s point in force five years, is in policy year 6
at attained age 40 at ``t = 0`` and has 240 months of cover left.

One input reads the valuation clock instead: expense inflation,
``inflation_factor(t) = (1 + inflation_rate) ** (t // 12)``, stepping on each
anniversary of the valuation date, so that the maintenance charge is in valuation-date
pounds for every point alike. Acquisition and the initial commission are charged per
policy issued, in the issue month, and not inflated, as in ``basiclife.BasicTerm_SE``.

On a point issued at ``t = 0`` the two clocks coincide and this model computes what
:mod:`~.Term_UK_S` computes: every cell the two share agrees at every argument
:mod:`~.Term_UK_S` evaluates in its sweep, but for those whose meaning changed —
``pols_if_init``, now the count already in force at the valuation date, and
``model_point``, a row of another table — and S's two cells this model does not have,
``proj_start`` and ``duration_inforce``, which ``duration_mth`` replaces.
``tests/test_model_conventions_uk.py`` asserts it cell by cell.

.. rubric:: Counts

``pols_if(t)`` is the count that weights row ``t``: ``pols_if_at(t, BEF_DECR)``, the
count carried in from ``t - 1`` (``BEF_NB``) plus the month's new business,
:func:`pols_new_biz`, before the month's decrements. A point in force at the valuation
date opens with :func:`pols_if_init`, its ``policy_count``; one issued at or after the
valuation date opens with none, and takes its ``policy_count`` as new business in its
issue month. The recursion's base is :func:`t_entry`, the first month on the books, and
nothing is counted outside cover (:func:`is_active`): before issue every count, and so
every cash flow, is zero. :mod:`~.Term_UK_S`'s three timings are kept, ``BEF_DECR``,
``BEF_LAPSE`` and ``AFT_DECR``, and ``BEF_NB`` is the one running in force adds.

.. rubric:: The opening state

A point in force carries, beside its count, what :mod:`~.Term_UK_S` carries into the
month a point is valued at, each per policy in force or as a ratio, so that the count is
the one weight on every flow, and each measured at the valuation instant, the start of
month 0, before any month-0 event:

* :func:`lapse_cum_init`, the selective-lapse ratio, the share of the issued cohort that
  has lapsed;
* :func:`fib_cum_init`, the deaths since issue per policy in force;
* :func:`fib_streams_init`, on the family income benefit, the streams in payment per
  policy in force: the deaths whose streams were not commuted, at the take-up of the
  month each fell in;
* :func:`idx_factor_init` and :func:`idx_prem_factor_init`, the indexation factors of the
  policy year under way, the RPI increases already given;
* :func:`wop_waived_frac_init`, the share of the policies in force whose premiums are
  waived; and, in the companion ``wop_pipeline_sec.csv``, :func:`wop_deferred_init`, the
  share of the policies in force still inside the deferred period, by the month their
  incapacity began, after the recoveries already made;
* :func:`comm_init_pp_init`, the initial commission paid at issue, per policy, which the
  clawback recovers.

Each is history, read from the model point, never recomputed from a Reference, which is
an assumption from the valuation date on. From :func:`lapse_cum_init` and
:func:`fib_cum_init`, :func:`cohort_frac` rebuilds the share of the issued cohort in
force, which turns a month's lapse rate into the lapse ratio's increment without dividing
by the count; and from :func:`wop_waived_frac_init` and :func:`wop_deferred_init`,
:func:`wop_active_frac` opens at what they leave, the share whose life is active, on which
the incidence falls.

.. rubric:: Codes

What :mod:`~.Term_UK_S` spells as text, a timing or a kind, is here an int Reference
named as the text it replaces, so that every cell takes and returns C numbers. A call
site reads as it did, less the quotes: ``pols_if_at(t, BEF_DECR)``, ``claims(t, FIB)``.

=============  =====  ===========================================================
Reference      Value  Meaning
=============  =====  ===========================================================
BEF_NB         0      :func:`pols_if_at`: the count carried in from month t - 1
BEF_DECR       1      :func:`pols_if_at`: that count plus month t's new business
BEF_LAPSE      2      :func:`pols_if_at`: after the month's deaths, before its lapses
AFT_DECR       3      :func:`pols_if_at`: the end of the month, after its decrements
DEATH          0      :func:`claims`: the lump sum on death and terminal illness
FIB            1      :func:`claims`: the family income benefit instalments
LAPSE          2      :func:`claims`: the lapse benefit, nil by product design
ALL            3      :func:`claims`: the three kinds' total
=============  =====  ===========================================================

A code a cell takes indexes that cell's cache, a C array of four timings a month for
:func:`pols_if_at` and four kinds a month for :func:`claims`, so codes are numbered
densely from 0. Timings are numbered in the order of their instants within the month,
``BEF_NB`` before ``BEF_DECR``, as in every SEC model, then :mod:`~.Term_UK_S`'s two
others in its processing order; kinds in :func:`result_cf`'s order, the order
:mod:`~.Term_UK_S` adds them in its total, and then ``ALL``, which is
:mod:`~.Term_UK_S`'s ``kind=None``. A code a cell does not take raises, ``invalid
timing`` or ``invalid kind``. They are References, not cells, so the symbol map below
does not list them.

.. rubric:: Reporting cells

:func:`model_point`, the label accessors :func:`shape`, :func:`sex`, :func:`smoker`,
:func:`premium_mode` and :func:`mort_basis`, and the reports :func:`result_cf` and
:func:`result_pols` return Python values, a table row, text and DataFrames, for a reader
and for the comparison with :mod:`~.Term_UK_S`, which has every one of them but
:func:`result_pols`. No cell but these calls a label accessor or a report: every other
reads the number ``Data`` decoded from the same column instead, the shape's flags, the
mode's cycle, the basis's flag and each life's row of the mortality table. So they stay
Python when the model compiles, and every other cell returns a C ``bint``, ``long long``
or ``double``. The two checks, :func:`check_pols_roll_fwd` and :func:`check_fib_ledger`,
are reporting cells too, which no cell calls, and each compiles to a ``bint``, a verdict
over residual cells that compile.

.. rubric:: Naming

Cells names follow lifelib's ``basiclife.BasicTerm_S`` wherever that model has an
analogue — ``pols_*`` for policy counts, plural nouns for cash flows, ``*_rate`` for
annual rates and ``*_rate_mth`` for monthly ones, ``*_pp`` for per-policy amounts,
``claims(t, kind)`` with a ``kind`` code, ``pols_if_at(t, timing)`` for the
within-month in-force reads. What running in force adds is named as
``basiclife.BasicTerm_SE`` names it: ``duration_mth`` read from the model point,
``policy_count``, ``pols_new_biz``, ``pols_if_at``'s ``BEF_NB`` timing, ``is_active``
and ``result_pols``. ``duration_mth_init``, the policy months completed at the valuation
date, takes ``UL_US_S``'s name; ``t_entry`` and ``cohort_frac`` are this model's own, and
each opening-state cell is the cell it opens with ``_init`` added. What compiling adds is
named as ``basiclife.BasicTerm_SC`` names it: ``idx``, ``point_id`` and the ``Data``
vectors under their columns' names; a decoded text column is the number it selects,
``prem_cycle`` the months between premiums, ``is_level``, ``is_decreasing``, ``is_fib``
and ``is_select_basis`` its flags, and ``mort_group(life)`` a life's row of the mortality
table. The technical notes use compact actuarial symbols instead. The mapping is:

=========================  ==============================  ==========================
Notes symbol               Cells                           Meaning
=========================  ==============================  ==========================
(none)                     point_id()                      The model point's label
shape                      shape()                         level / decreasing / fib
(shape decoded)            is_level(), is_decreasing()     The level and decreasing
                                                           shapes' flags
(shape decoded)            is_fib()                        The FIB shape's flag
x                          age_at_entry(life)              Issue age (ANB), life 1 or 2
x + duration(t)            age(t, life)                    Attained age in month t
(none)                     sex(life), smoker(life)         Rating factors of each life
(rating decoded)           mort_group(life)                The life's mortality row
n                          policy_term()                   Term in years
N = 12n                    term_mths()                     Policy month cover ends at
(frame)                    proj_len()                      Months to the end of cover
(none)                     policy_count()                  Policies the point stands for
(none)                     duration_mth_init()             Policy months at t = 0
k, duration_mth(t)         duration_mth(t)                 Policy months at month t
(none)                     t_entry()                       First month on the books
(none)                     is_active(t)                    Whether month t is in cover
(none)                     duration(t)                     Completed policy years
(none)                     policy_year(t)                  Contractual policy year
SA0                        sum_assured()                   Initial sum assured
I                          fib_income()                    FIB income per month
j                          sched_rate()                    Decreasing schedule rate
j_m                        sched_rate_mth()                (1+j)^(1/12) - 1
B(k)                       benefit_sched(k)                Benefit after k months
DB(t)                      benefit_pp(t)                   Death/TI benefit per policy
idx(t)                     idx_factor(t)                   Cover indexation factor
(idx at t = 0)             idx_factor_init()               Cover factor given to date
idx_p(t)                   idx_prem_factor(t)              Premium indexation factor
(idx_p at t = 0)           idx_prem_factor_init()          Premium factor to date
(RPI scenario)             rpi_rate                        Flat RPI assumption, 3%
P_m                        premium_mth_pp()                Monthly premium at issue
P_m x idx_p(t)             premium_pp(t)                   Premium due in month t
(mode)                     premium_mode()                  monthly or annual
(mode decoded)             prem_cycle()                    Months between premiums
(table)                    mort_rate_base(t, life)         Table rate before factors
(select)                   select_factor(t)                Select-duration factor
(proxy scaling)            mort_scale                      "00" to "16" Series factor
(none)                     mort_rate_life(t, life)         Per-life annual rate
q(t), q_joint              mort_rate(t)                    Annual policy decrement
q_m(t)                     mort_rate_mth(t)                Monthly policy decrement
(none)                     mort_basis()                    applied or select run
(basis decoded)            is_select_basis()               Whether the run is select
lambda                     sel_lapse_lambda                Selective-lapse loading
w_ref                      sel_lapse_ref                   Selective-lapse threshold
w_cum(t)                   lapse_cum(t)                    Cumulative lapse ratio
(w_cum at t = 0)           lapse_cum_init()                Lapse ratio at t = 0
l(t) per policy issued     cohort_frac(t)                  Share of cohort in force
(none)                     sel_lapse_factor(t)             Loading on persisters
(table)                    lapse_rate_base(t)              Table annual lapse rate
M_reb(t)                   rebroke_factor(t)               Rebroking multiplier
w(t)                       lapse_rate(t)                   Annual lapse rate
w_m(t)                     lapse_rate_mth(t)               Monthly lapse rate
l(t)                       pols_if(t)                      Count weighting month t
(l(0))                     pols_if_init()                  Count in force at t = 0
(none)                     pols_new_biz(t)                 Policies issued in month t
l(t)(1-q_m), l(t+1)        pols_if_at(t, timing)           The within-month counts
D(t)                       pols_death(t)                   Death/TI claims
(none)                     pols_lapse(t)                   Lapses at end of month t
(none)                     pols_maturity(t)                Expiries at end of term
(none)                     pols_payer(t)                   Policies paying premium
inc(t)                     wop_inc_rate                    WOP annual incidence
(recovery)                 wop_rec_rate                    WOP annual recovery
(deferred period)          wop_defer_mths                  26 weeks, as 6 months
act(t)                     wop_active_frac(t)              Share active, can fall ill
u(t)                       wop_waived_frac(t)              Share with premium waived
(u at t = 0)               wop_waived_frac_init()          Share waived at t = 0
(deferred, lag k)          wop_deferred_init(k)            In deferral at t=0, lag k
FIBcum(t)                  fib_cum(t)                      Deaths since issue
(FIBcum at t = 0)          fib_cum_init()                  Deaths to date per policy
(1-c) FIBcum(t)            fib_streams(t)                  FIB streams in payment
(streams at t = 0)         fib_streams_init()              Streams per policy, t = 0
a(m)                       annuity_certain_factor(m)       m-month annuity-certain
r_c                        fib_commute_disc_rate           FIB commutation rate, 3%
CV(k)                      fib_commute_pp(t)               Commuted value of a stream
(take-up)                  fib_commute_rate()              Share of FIB commuted
P_m x idx_p x l            premiums(t)                     Premium income
DB(t) x D(t), Claims_fib   claims(t, kind)                 Benefit outgo by kind
ec x D(t)                  claim_expenses(t)               Claim expense outgo
E0, e(t)                   expenses(t)                     Acquisition + maintenance
(none)                     inflation_factor(t)             Expense inflation factor
c0                         comm_init_pp()                  Initial commission
(c0 paid at issue)         comm_init_pp_init()             c0 paid, in force at t = 0
c_r                        comm_renewal_rate               Renewal commission rate
(clawback)                 comm_clawback(t)                Commission recovered
c0, c_r x premiums         commissions(t)                  Commission outgo, net
CF(t)                      net_cf(t)                       Net cash flow, income +
(none)                     result_pols()                   The counts, month by month
=========================  ==============================  ==========================

Five names needed care in :mod:`~.Term_UK_S`, and keep their reasons here.

The notes use ``q(t)`` both for the per-life table rate and for the decrement actually
applied to the policy, which on a joint first-death policy is
``1 - (1-q_1)(1-q_2)``. :func:`mort_rate_life` is the per-life rate and
:func:`mort_rate` the policy decrement, so the joint combination has somewhere to live
and the single-life case collapses to the same number.

``q(t)`` and ``w(t)`` are **annual** rates in the notes and stay annual here, with
:func:`mort_rate_mth` and :func:`lapse_rate_mth` carrying the monthly conversions
``1 - (1 - q)^(1/12)`` and ``1 - (1 - w)^(1/12)``. That is the library-wide split — a
bare ``*_rate`` is the annual rate everywhere, and only ``*_rate_mth`` is monthly — and
it is what lets the assumption tables stay in the annual units they are quoted in.

``w(t)`` is the lapse rate and ``w_cum(t)`` the cumulative lapse ratio that drives the
selective-lapsation loading on *mortality*. Spelling them ``lapse_rate`` and
``lapse_cum`` keeps the second from reading as a running total of the first, which it
is not: it is a share of the issued cohort, and the loading it feeds moves claims, not
lapses.

``E0`` and ``e(t)`` are the acquisition and maintenance expenses; both are inside
:func:`expenses`, which is the library-wide name, with the claim expense ``ec x D(t)``
kept out of it under :func:`claim_expenses` because the notes' worked-example table
prints the two as separate columns.

``pols_maturity`` has no symbol in the notes at all. The notes give the roll-forward as
``l(t+1) = l(t)(1-q_m)(1-w_m)`` and, separately, terminate everything at the end of the
term. Those do not reconcile in the last covered month, ``duration_mth(t) = N - 1``: its
survivors neither die nor lapse — their cover simply runs out — so without a term for
that the roll-forward appears to lose lives with no cause. :func:`pols_maturity` names
it, zero in every month but that one, so that

    pols_if(t) - pols_if_at(t + 1, BEF_NB) = pols_death(t) + pols_lapse(t)
                                              + pols_maturity(t)

holds for every ``t``, and ``pols_if(t + 1)`` adds ``pols_new_biz(t + 1)`` to the count on
the left; :func:`check_pols_roll_fwd` asserts it. It is bookkeeping determined by the
notes' own rules, not an added assumption, and the name follows
``BasicTerm_S.pols_maturity``. It is *not* a maturity **benefit**: the amount paid is nil.

.. rubric:: The monthly grid, and what it removes

As in :mod:`~.Term_UK_S`: the decreasing benefit is the exact balance
:func:`benefit_sched` of the policy month the claim falls in, the premium is the
contractual monthly premium ``P_m``, collected in the months it is due and stopping the
month the policy leaves, and family income benefit instalments are counted one by one. A
policy paying annually is charged ``12 P_m`` in the first month of each policy year,
``duration_mth(t) % 12 == 0``, and nothing in the other eleven; and the waiver of premium
rider's 26-week deferred period is carried as ``wop_defer_mths = 6`` months. The
assumption tables stay in the annual units they are quoted in and are converted with
``1 - (1 - r)^(1/12)`` **[std]**, stepped by policy year.

.. rubric:: No tail states

A UK term policy expires at the end of its term, policy month ``N - 1``: there is no jump
to ART rates, no post-level-term shock lapse, no mortality deterioration factor and no
conversion option, so none of those cells exist here, as in :mod:`~.Term_UK_S`. What
running in force adds is the contract's own bounds, which :func:`proj_len` holds a point
to: a term of at most ``policy_term_max``, 50 years, or ``policy_term_max_fib``, 40, on
the family income benefit; an issue age of ``issue_age_min``, 18, or more; and expiry by
attained age ``expiry_age_max``, 90, or ``expiry_age_max_fib``, 70.

.. rubric:: Terminal illness is not an extra benefit

Terminal illness is a 100% **acceleration** of the death benefit under a two-limb
12-month definition, not an additional cover: one decrement, one payment. So
``mort_rate`` is the combined death-and-terminal-illness rate and there is no ``ti_rate``
anywhere in the model, as in :mod:`~.Term_UK_S`.

.. rubric:: The family income benefit ledger

A death in policy month ``k`` on the ``fib`` shape triggers ``N - k`` monthly instalments
of ``I``, in arrears, ending at the end of the term: an **annuity-certain**, decremented by
neither mortality nor lapse, unless the claim is commuted to a lump sum, as the take-up
``c`` of :func:`fib_commute_rate` is. :func:`fib_streams` is the ledger, the expected
streams in payment at the start of month ``t``: on a point in force it opens from
:func:`fib_streams_init`, the streams in payment per policy in force, history, and adds
the share of each month's deaths not commuted, so that
``claims(t, FIB) = I x [(1 - c) D(t) + streams(t)]`` pays the streams that began before
the valuation date as well as after it, and a take-up changed at the valuation date
commutes none already in payment. :func:`fib_cum`, :mod:`~.Term_UK_S`'s ``FIBcum``, counts
the deaths since issue alongside. :func:`check_fib_ledger` rebuilds the month's
instalment count from the opening streams and the death vector, with no reference to the
recursion, and asserts the two agree in every projected month.

.. rubric:: Two mortality bases: applied and select

As in :mod:`~.Term_UK_S`, which applies is a model point column: ``mort_basis =
"applied"`` reads ``mort_table.csv`` as the annual rate actually applied, and
``"select"`` reads it as an ultimate basis, multiplied by :func:`select_factor`, read at
the select duration :func:`duration` on the policy clock, and by ``mort_scale``. The
shipped table is a **[std]** construction throughout, not a published table, and no
conclusion about UK mortality should be drawn from it.

.. rubric:: Modules that are off in the base run

Four of the notes' optional constructions are implemented and switched off, as in
:mod:`~.Term_UK_S`: selective lapsation (``sel_lapse_lambda = 0``), rebroking
(``premium_market_ratio = 1``), commission clawback (``clawback_mths = 0``; 48 for the
notes' four-year rule, the months in force read on the policy clock) and the waiver of
premium, on model point 7 alone. Each carries its state in force, so a point valued at
any month continues as it would have from issue.

.. rubric:: Sign convention

The notes' ``CF(t)`` is already **income positive** — "+ = inflow" — which is the
library-wide sign of :func:`net_cf`, so there is no ``liability_cf`` companion.

.. rubric:: Lapse pays nothing

There is no surrender value and no paid-up value at any duration, so a lapse is a pure
decrement: it moves ``pols_if`` and pays nothing. ``claims(t, LAPSE)`` exists and
returns zero, and ``result_cf()`` carries the zero column, as in :mod:`~.Term_UK_S`.
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
    :mod:`~.Term_UK_S`'s columns, for a reader who wants every column at once: a reporting
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


def shape():
    """The benefit shape: ``level``, ``decreasing`` or ``fib`` [S1][S2][S6][S8].

    A reporting cell (the Space docstring), :mod:`~.Term_UK_S`'s, which returns the column
    as read, refusing any other value: no projection cell reads it here, and each branches
    on ``Data``'s decode of the same column instead, :func:`is_level`,
    :func:`is_decreasing` and :func:`is_fib`.
    """
    v = model_point()["shape"]
    if v not in ("level", "decreasing", "fib"):
        raise ValueError("invalid shape")
    return v


def is_level():
    """Whether the benefit shape is ``level``, from ``Data.is_level``.

    ``Data`` decodes the ``shape`` column as :mod:`~.Term_UK_S`'s ``shape() == "level"``
    compares it, and refuses a shape other than the three, so exactly one of
    :func:`is_level`, :func:`is_decreasing` and :func:`is_fib` is True.
    """
    return bool(data.is_level()[idx])                                # noqa: F821


def is_decreasing():
    """Whether the benefit shape is ``decreasing``, from ``Data.is_decreasing``."""
    return bool(data.is_decreasing()[idx])                           # noqa: F821


def is_fib():
    """Whether the benefit shape is ``fib``, the family income benefit, from
    ``Data.is_fib``."""
    return bool(data.is_fib()[idx])                                  # noqa: F821


def is_joint():
    """True when the policy covers two lives on a first-death basis.

    The policy pays once and ends; separation and replacement options create *new*
    policies and are out of scope **[std scope]**.  From ``Data.joint_first_death``, which
    decodes the column as :mod:`~.Term_UK_S`'s ``bool`` reads it.
    """
    return bool(data.joint_first_death()[idx])                       # noqa: F821


def age_at_entry(life):
    """x: the issue age (ANB) of the first (``life = 1``) or second life.

    Age nearest birthday at entry, plus a curtate policy year **[std]**: the fetched
    product documents state no age basis, and the UK assured lives tables are select
    tables indexed that way. The age at issue, not at the valuation date:
    ``age(0, life)`` is the attained age then.

    ``life`` has no default, here or in the other seven cells that take it, :func:`sex`,
    :func:`smoker`, :func:`mort_group`, :func:`age`, :func:`mort_rate_base` and
    :func:`mort_rate_life`, where :mod:`~.Term_UK_S` defaults it to 1: every call passes
    1 or 2, so that a compiled model declares each a plain parameter. modelx keys
    :mod:`~.Term_UK_S`'s calls by the arguments bound, ``age(t)`` as ``(t, 1)``, so the
    two models' cells pair as before. Read from ``Data.age_at_entry`` and, on a joint
    point, ``Data.joint_age``, ``int`` of each as :mod:`~.Term_UK_S` reads it.
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
    :mod:`~.Term_UK_S` refuses as ``invalid life``: no projection cell reads it here, and
    :func:`mort_rate_base` reads each life's row of the mortality table,
    :func:`mort_group`, instead.
    """
    if life == 1:
        return model_point()["sex"]
    if life == 2:
        return model_point()["joint_sex"]
    raise ValueError("invalid life")


def smoker(life):
    """The smoker status (N / S) of the first or second life, as the table spells it.

    A reporting cell, as :func:`sex` is: the ``smoker`` or ``joint_smoker`` column as
    read, a single-life point's blank second life as NaN.
    """
    if life == 1:
        return model_point()["smoker"]
    if life == 2:
        return model_point()["joint_smoker"]
    raise ValueError("invalid life")


def mort_group(life):
    """The row of ``Data.mort_table_array`` of the first (``life = 1``) or second life.

    The life's sex and smoker status, the key :mod:`~.Term_UK_S` reads *mort_table.csv*
    by, decoded in ``Data`` into the row they select: M N 0, M S 1, F N 2 and F S 3, from
    ``Data.mort_group`` and, on a joint point, ``Data.joint_mort_group``. Like
    :func:`age_at_entry`, it refuses a second life on a single-life point.
    """
    if life == 1:
        return int(data.mort_group()[idx])                           # noqa: F821
    if life == 2 and is_joint():
        return int(data.joint_mort_group()[idx])                     # noqa: F821
    raise ValueError("invalid life")


def policy_term():
    """n: the term in years; 1-50 level, 5-50 decreasing, 5-40 FIB [S1][S6][S8].

    :func:`proj_len` refuses a term above ``policy_term_max``, 50 years, or
    ``policy_term_max_fib``, 40, on the family income benefit. From ``Data.policy_term``.
    """
    return int(data.policy_term()[idx])                              # noqa: F821


def sum_assured():
    """SA0: the initial sum assured of the level and decreasing shapes [S1][S6].

    The sum assured at issue: on an indexed point in force, the cover of the year under
    way is this times :func:`idx_factor_init`. From ``Data.sum_assured``.
    """
    return float(data.sum_assured()[idx])                            # noqa: F821


def fib_income():
    """I: the family income benefit, per month, on the ``fib`` shape [S2][S6][S8].

    From ``Data.fib_income``.
    """
    return float(data.fib_income()[idx])                             # noqa: F821


def sched_rate():
    """j: the decreasing shape's schedule rate p.a. **[std]**, 6% on the shipped points.

    Contractual, not experience: the client selects it at outset and the benefit
    amortizes at it whatever happens to interest rates [S1][S6][S8].  The risk it
    carries is therefore specification error - mis-implementing the amortization or the
    monthly convention - rather than assumption error.  From ``Data.sched_rate``.
    """
    return float(data.sched_rate()[idx])                             # noqa: F821


def indexation():
    """Whether the RPI indexation option is elected [S1][S2][S6][S7].

    Restricted to the level shape **[std scope]**: no fetched insurer offers indexed
    decreasing cover, and the notes do not combine indexation with the FIB schedule
    either.  From ``Data.indexation``; ``Data`` refuses the option off the level shape
    when it reads the table, and this refuses it again, as :mod:`~.Term_UK_S` does.
    """
    v = bool(data.indexation()[idx])                                 # noqa: F821
    if v and not is_level():
        raise ValueError("indexation is modelled on the level shape only")
    return v


def wop():
    """Whether the waiver of premium rider is in force [S1]; false in the base run.

    From ``Data.wop``.
    """
    return bool(data.wop()[idx])                                     # noqa: F821


def premium_mth_pp():
    """P_m: the guaranteed monthly premium per policy at issue **[std]**.

    A pure modelling value.  No UK insurer publishes premium rate tables - pricing is
    quote-driven and only the £5/month minimum is public [S5] - so any reference
    premium basis is constructed rather than observed.  It is guaranteed level for the
    full term [S2][S6][S9], which is what puts every month of premium inside the
    Solvency UK contract boundary [R3].  On an indexed point in force, the premium of the
    year under way is this times :func:`idx_prem_factor_init`.  From ``Data.premium_mth``.
    """
    return float(data.premium_mth()[idx])                            # noqa: F821


def premium_mode():
    """Monthly or annual premium collection.

    A monthly payer is charged ``P_m`` in every month; an annual payer is charged
    ``12 P_m`` in the first month of each policy year, ``duration_mth(t) % 12 == 0`` on
    the policy clock, and nothing in the other eleven, so a point valued mid-year pays its
    next premium on its next anniversary.  The amount collected over a policy year is the
    same and only its timing differs.  No premium discount for annual collection is
    modelled **[std]**; UK protection pricing is quote-driven and no published scale
    exists.

    A reporting cell (the Space docstring), :mod:`~.Term_UK_S`'s, which returns the column
    as read, refusing any other value: :func:`premium_pp` branches on ``Data``'s decode of
    the same column instead, :func:`prem_cycle`.
    """
    v = model_point()["premium_mode"]
    if v not in ("monthly", "annual"):
        raise ValueError("invalid premium_mode")
    return v


def prem_cycle():
    """Months between premiums: ``monthly`` 1 and ``annual`` 12, from ``Data.prem_cycle``.

    The arithmetic of the mode rather than an assumption, so ``Data`` decodes it from the
    ``premium_mode`` column, refusing any other mode, and :func:`premium_pp` charges an
    annual payer where it is 12, as :mod:`~.Term_UK_S` charges one where the mode is
    ``"annual"``.
    """
    return int(data.prem_cycle()[idx])                               # noqa: F821


def mort_basis():
    """Whether the mortality table is read as the *applied* rate or as an *ultimate* one.

    *applied* **[std]** takes ``mort_table.csv`` as the annual rate actually applied,
    which is how the notes quote their illustrative worked-example vector; *select*
    multiplies it by :func:`select_factor` and by ``mort_scale``, the notes' proxy for
    the unavailable subscriber tables.  See the Space docstring for why both are
    shipped.

    A reporting cell (the Space docstring), :mod:`~.Term_UK_S`'s, which returns the column
    as read, refusing any other value: :func:`mort_rate_life` branches on ``Data``'s decode
    of the same column instead, :func:`is_select_basis`.
    """
    v = model_point()["mort_basis"]
    if v not in ("applied", "select"):
        raise ValueError("invalid mort_basis")
    return v


def is_select_basis():
    """Whether the mortality table is read as an ultimate basis, from
    ``Data.is_select_basis``.

    ``Data`` decodes the ``mort_basis`` column as :mod:`~.Term_UK_S`'s ``mort_basis() ==
    "select"`` compares it, and refuses a basis other than ``applied`` and ``select``.
    """
    return bool(data.is_select_basis()[idx])                         # noqa: F821


def policy_count():
    """The number of policies the model point stands for, its ``policy_count`` column.

    A point in force at the valuation date counts the policies in force then, before any
    month-0 event; any other point counts the policies it issues. Either way the count
    enters the projection once: as :func:`pols_if_init` for the first, as
    :func:`pols_new_biz` in the issue month for the second. It is the one weight on every
    flow: every opening-state column is per policy in force, or a ratio. Read from
    ``Data.policy_count``.
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

    The policy's age in months at ``t = 0``: 60 for model point 8, issued five years
    before the valuation date, 0 for one issued at it, and -13 for one to be issued 13
    months after it, which ``Data`` admits up to ``future_horizon_mth`` months ahead. It
    is read as ``basiclife.BasicTerm_SE`` reads it, and is the one fact the policy clock
    takes from the model point. It replaces :mod:`~.Term_UK_S`'s ``duration_inforce``
    column, a count of whole years, twelve months to each of which S opened its frame
    late, on an anniversary only; a point may be valued in any month of its policy year.
    Its element of ``Data.duration_mth``.
    """
    return int(data.duration_mth()[idx])                             # noqa: F821


def lapse_cum_init():
    """w_cum at the valuation date: the share of the issued cohort that has lapsed.

    :func:`lapse_cum`'s value entering month 0, a ratio to the policies issued, so the
    count does not move it. 0 on a point not yet in force, which ``Data`` requires, and
    on :mod:`~.Term_UK_S`'s point 8, which S opens with nothing lapsed. With
    :func:`fib_cum_init` it gives :func:`cohort_frac` its opening value. From
    ``Data.lapse_cum_init``.
    """
    return float(data.lapse_cum_init()[idx])                         # noqa: F821


def fib_cum_init():
    """FIBcum at the valuation date, per policy in force: the deaths since issue.

    :func:`fib_cum`'s value entering month 0 divided by the count in force then, which
    :func:`fib_cum` scales by :func:`pols_if_init`. On every shape, as
    :mod:`~.Term_UK_S`'s ``fib_cum`` counts them, the deaths since issue, which with
    :func:`lapse_cum_init` give :func:`cohort_frac` its opening value. Which of those
    deaths' streams are still in payment is :func:`fib_streams_init`, a column of its own.
    0 on a point not yet in force, which ``Data`` requires. From ``Data.fib_cum_init``.
    """
    return float(data.fib_cum_init()[idx])                           # noqa: F821


def fib_streams_init():
    """The family income benefit streams in payment at the valuation date, per policy.

    :func:`fib_streams`'s value entering month 0 divided by the count in force then: the
    deaths since issue whose instalments were not commuted, each at the take-up of the
    month it fell in. History, read from the model point: :mod:`~.Term_UK_S` re-derives
    it as ``(1 - fib_commute_rate()) x FIBcum``, so a take-up set at the valuation date
    would reach back over every claim already admitted, commuting streams long in payment.
    At a take-up that never changed it is that, ``(1 - c) x`` :func:`fib_cum_init`, and
    it is never more than :func:`fib_cum_init`, which ``Data`` requires. 0 on a point not
    yet in force, and on the level and decreasing shapes, which pay no instalments. From
    ``Data.fib_streams_init``.
    """
    return float(data.fib_streams_init()[idx])                       # noqa: F821


def idx_factor_init():
    """idx at the valuation date: the cover factor of the policy year under way.

    The RPI increases the policy has already been given, as one factor on
    :func:`sum_assured`, the sum assured at issue: on a valuation on an anniversary, the
    factor of the policy year it opens. History, read from the model point, not
    recomputed from ``rpi_rate``, which is the assumed rate from the valuation date on.
    1 on a point not yet in force or without the option, which ``Data`` requires. From
    ``Data.idx_factor_init``.
    """
    return float(data.idx_factor_init()[idx])                        # noqa: F821


def idx_prem_factor_init():
    """idx_p at the valuation date: the premium factor of the policy year under way.

    :func:`idx_factor_init`'s counterpart on the premium, :func:`premium_mth_pp` the
    premium at issue.  History, as the cover factor is.  1 on a point not yet in force or
    without the option, which ``Data`` requires.  From ``Data.idx_prem_factor_init``.
    """
    return float(data.idx_prem_factor_init()[idx])                   # noqa: F821


def wop_waived_frac_init():
    """u at the valuation date: the share of the policies in force whose premium is waived.

    :func:`wop_waived_frac`'s value entering month 0, the lives who have completed the
    deferred period and not recovered. 0 on a point not yet in force or without the
    rider, which ``Data`` requires, and on a point in force no longer than the deferred
    period, whose first incapacity has not yet run its course, which :func:`proj_len`
    requires. The lives still inside the deferred period are the pipeline,
    :func:`wop_deferred_init`. From ``Data.wop_waived_frac_init``.
    """
    return float(data.wop_waived_frac_init()[idx])                   # noqa: F821


def wop_deferred_init(k):
    """The share in the deferred period at ``t = 0``, incapacitated ``k`` months before.

    The policies in force whose life became incapacitated in the policy month ``k`` months
    before the valuation date, from the lives active then, ``inc_m act``, and has not
    recovered by the start of month 0: the incidence of that month after the
    ``k - 1`` months of recovery it has already been through, at the rates of those
    months. :func:`wop_waived_frac` takes the cohort in at ``t = wop_defer_mths + 1 - k``,
    once the deferred period has run, less the recoveries of its remaining ``t`` months,
    at ``wop_rec_rate``, the assumption from the valuation date on. ``k`` runs from 1 to
    ``min(wop_defer_mths, duration_mth_init())``: a cohort ``wop_defer_mths + 1`` months
    back or more has entered the waived share, :func:`wop_waived_frac_init`, already, and
    none predates issue. History, read from the companion ``wop_pipeline_sec.csv``, keyed
    ``(point_id, lag)``, not recomputed from ``wop_inc_rate`` or ``wop_rec_rate``: held
    as the incidence instead, the months of the deferred period already run would be run
    again at today's recovery rate.

    ``Data.wop_deferred_init`` at this point and lag ``k``, after :func:`proj_len`, which
    refuses a point whose pipeline does not hold exactly the lags it reads, naming it.
    Then a lag below 1 or past the point's last, ``Data.wop_pipeline_last``, is refused,
    naming the point and the lag, where stage ``E``'s ``.loc`` raised pandas'
    ``KeyError``, so that no read meets ``Data``'s padding.
    """
    proj_len()
    if k < 1 or k > data.wop_pipeline_last()[idx]:                   # noqa: F821
        raise ValueError(f"point_id {point_id()}: wop_pipeline_sec.csv holds no lag {k}")
    return float(data.wop_deferred_init()[idx, k])                   # noqa: F821


def comm_init_pp_init():
    """c0 paid at issue, per policy, on a point in force at the valuation date.

    The initial commission the policy paid when it was written, which the clawback
    recovers on a lapse inside its window: history, read from the model point, where
    :mod:`~.Term_UK_S` re-derives it from ``comm_init_rate`` and the premium, so that a
    rate changed at the valuation date would change what was paid years before.
    :func:`comm_init_pp` returns it on a point in force; a point issued at or after the
    valuation date pays the rate, and holds 0 here, which ``Data`` requires, the
    commission being an event of the issue month.  From ``Data.comm_init_pp_init``.
    """
    return float(data.comm_init_pp_init()[idx])                      # noqa: F821


def fib_commute_rate():
    """The proportion of FIB claims commuted to a lump sum **[std]**; 0 in the base run.

    The insurer may replace the remaining instalments with a lump sum determined
    "fairly and reasonably" [S6][S8]; no insurer publishes the basis, so both the
    take-up and the discount rate ``fib_commute_disc_rate`` are standardizations.  From
    ``Data.fib_commute_rate``.
    """
    return float(data.fib_commute_rate()[idx])                       # noqa: F821


def proj_len():
    """The number of months from the valuation date to the end of cover.

    ``term_mths() - duration_mth_init()``: 300 for the anchor cell issued at ``t = 0``,
    240 for model point 8, in force 60 months, and the term's months plus ``k`` for a
    point issued ``k`` months after the valuation date. The frame is
    ``t = 0, 1, ..., proj_len() - 1``; ``proj_len()`` is its exclusive end and the row
    count of :func:`result_cf`. Cover ceases at the end of the term with no maturity
    value, no renewal and no conversion [S1][S2][S6][S8][R8].

    Eight kinds of point raise here, naming the point, rather than project nothing or a
    frame the contract does not have, each checked in this order:

    * one whose cover ended at or before the valuation date, which an in-force extract
      should not carry;
    * one whose term is above ``policy_term_max``, 50 years, or on the family income
      benefit ``policy_term_max_fib``, 40;
    * one with a life issued below ``issue_age_min``, 18;
    * one with a life whose cover runs past attained age ``expiry_age_max``, 90, or on the
      family income benefit ``expiry_age_max_fib``, 70: the issue age plus the term;
    * one of the family income benefit while ``fib_commute_disc_rate``, the annual rate
      the commuted value discounts at, is not a finite number above -1: at -1 the
      discount's power ``(1 + r_c)^(-m/12)`` divides by zero, below it has no real
      value, which :mod:`~.Term_UK_S` projects as a complex number, and an infinite rate
      gives a factor of 0, and NaN one of NaN, without a word;
    * one with the waiver rider in force while ``wop_inc_rate`` or ``wop_rec_rate``, an
      annual rate, is outside 0 to 1 or not a number: each is one Reference, with no
      factor and no cap, and past 1 its monthly rate, ``1 - (1 - r)^(1/12)``, has no real
      value, which :mod:`~.Term_UK_S` projects as a complex number;
    * one with the waiver rider in force under a negative ``wop_defer_mths``, or in force
      no longer than ``wop_defer_mths`` with a waived share other than 0, a state
      :mod:`~.Term_UK_S` cannot reach, since no incapacity has yet run the deferred period;
    * one with the waiver rider in force whose pipeline in ``wop_pipeline_sec.csv`` does
      not hold exactly one lag for each of its last ``min(wop_defer_mths,
      duration_mth_init())`` months, lags 1 to that.

    The last two rules read ``wop_defer_mths``, a Reference of this Space, which ``Data``
    cannot see, so they are checked here.

    These are the product's limits (``product-spec.md``), and rules of the product, read
    from this Space's References, where ``Data`` checks the tables. They are the contract
    the compiled model's caches are sized from (``spec_sec.py``): a frame of at most
    ``policy_term_max``, 50 years, and ``Data.future_horizon_mth``, 120 months, so 720
    months; a schedule of at most 600 policy months; an annuity-certain of at most 480
    months, ``policy_term_max_fib``'s 40 years; and two lives. Every report reads this
    cell first, so no point outside them is projected, in modelx as compiled. Raising
    ``policy_term_max``, ``policy_term_max_fib`` or the horizon needs the spec's sizes
    raised and the model rebuilt, or a report runs past the caches in the compiled model
    alone, raising ``IndexError`` where modelx projects. A point without the rider reads
    neither waiver rate, and one of another shape no discount rate, and each projects
    whatever they are.
    """
    n = term_mths() - duration_mth_init()
    if n <= 0:
        raise ValueError(
            f"point_id {point_id()}: duration_mth {duration_mth_init()} "
            f"is at or past the end of cover, policy month {term_mths()}")
    fib = is_fib()
    longest = policy_term_max_fib if fib else policy_term_max        # noqa: F821
    if policy_term() > longest:
        raise ValueError(
            f"point_id {point_id()}: the term, {policy_term()} years, is above "
            f"{'policy_term_max_fib' if fib else 'policy_term_max'}, {int(longest)}")
    oldest = expiry_age_max_fib if fib else expiry_age_max           # noqa: F821
    for life in range(1, 3 if is_joint() else 2):
        if age_at_entry(life) < issue_age_min:                       # noqa: F821
            raise ValueError(
                f"point_id {point_id()}: life {life}'s issue age, "
                f"{age_at_entry(life)}, is below issue_age_min, "
                f"{int(issue_age_min)}")                             # noqa: F821
        if age_at_entry(life) + policy_term() > oldest:
            raise ValueError(
                f"point_id {point_id()}: life {life}'s cover runs to attained age "
                f"{age_at_entry(life) + policy_term()}, issue age "
                f"{age_at_entry(life)} and a {policy_term()}-year term, past "
                f"{'expiry_age_max_fib' if fib else 'expiry_age_max'}, {int(oldest)}")
    if fib and not (fib_commute_disc_rate > -1.0                     # noqa: F821
                    and fib_commute_disc_rate <= 1.7976931348623157e308):  # noqa: F821
        raise ValueError(
            f"point_id {point_id()}: fib_commute_disc_rate must be a finite number "
            f"above -1, not {float(fib_commute_disc_rate)}")         # noqa: F821
    if wop():
        if not (wop_inc_rate >= 0.0 and wop_inc_rate <= 1.0):        # noqa: F821
            raise ValueError(
                f"point_id {point_id()}: wop_inc_rate must be a number from 0 to 1, "
                f"not {float(wop_inc_rate)}")                        # noqa: F821
        if not (wop_rec_rate >= 0.0 and wop_rec_rate <= 1.0):        # noqa: F821
            raise ValueError(
                f"point_id {point_id()}: wop_rec_rate must be a number from 0 to 1, "
                f"not {float(wop_rec_rate)}")                        # noqa: F821
        if wop_defer_mths < 0:                                       # noqa: F821
            raise ValueError(f"point_id {point_id()}: wop_defer_mths must be "
                             f"0 months or more, not {int(wop_defer_mths)}")  # noqa: F821
        if (duration_mth_init() > 0 and duration_mth_init() <= wop_defer_mths  # noqa: F821
                and wop_waived_frac_init() != 0.0):
            raise ValueError(
                f"point_id {point_id()}: wop_waived_frac_init is "
                f"{wop_waived_frac_init()}, where a waiver point in force "
                f"{duration_mth_init()} months, no longer than wop_defer_mths, "
                f"{int(wop_defer_mths)}, has waived no premium yet: 0")  # noqa: F821
        lags = min(wop_defer_mths, max(duration_mth_init(), 0))      # noqa: F821
        held = data.wop_pipeline_count()[idx]                        # noqa: F821
        last = data.wop_pipeline_last()[idx]                         # noqa: F821
        if held != lags or last != lags:
            raise ValueError(
                f"point_id {point_id()}: wop_pipeline_sec.csv holds {held} lags, "
                f"its last {last}, where a waiver point in force "
                f"{max(duration_mth_init(), 0)} months holds one for each of its "
                f"last {int(lags)}, min(wop_defer_mths, duration_mth), lags 1 to "
                f"{int(lags)}")
    return n


def term_mths():
    """N = 12n: the term in months, the policy month cover ends at, on the policy clock.

    The horizon of the benefit schedules, and :mod:`~.Term_UK_S`'s frame from issue: the
    last covered month is ``duration_mth(t) = N - 1``, and :func:`is_active` is false
    from ``duration_mth(t) = N`` on. :func:`proj_len` counts from the valuation date
    instead.
    """
    return 12 * policy_term()


def t_entry():
    """The first month the policy is on the books: ``max(0, -duration_mth_init())``.

    0 for a point in force at the valuation date or issued at it, ``k`` for one issued
    ``k`` months later. It is the base of every recursion: the count, the lapse ratio and
    the cohort's share in force, the active and waived shares and the ledger open there,
    from the opening state, and none reads a month before it.
    """
    return max(0, -duration_mth_init())


def is_active(t):
    """Whether month t is inside cover: issued, and not yet expired.

    ``0 <= duration_mth(t) < term_mths()``. False before issue and from the month cover
    has ended, ``t = proj_len()``. Outside cover every count is zero, and so every cash
    flow; no count cell evaluates a rate there, and no table is read at a policy year, a
    select duration or an attained age the policy does not have.
    """
    return 0 <= duration_mth(t) < term_mths()


def duration(t):
    """Completed policy years at the start of month t: ``duration_mth(t) // 12``.

    0 throughout the first policy year, and negative before issue. The select duration,
    which is what the UK assured lives tables are indexed by alongside attained age,
    and the count of anniversaries the indexation factors step on.
    """
    return duration_mth(t) // 12


def duration_mth(t):
    """Completed policy months at the start of month t, the **policy** clock.

    ``duration_mth_init() + t``: ``t`` counts months from the valuation date and
    ``duration_mth(t)`` months from issue, and the two move together. The notes'
    benefit-schedule index ``k``. A closed form, where ``basiclife.BasicTerm_SE`` adds one
    a month by recursion: the same numbers, without a call chain as long as the frame.
    Negative before issue.
    """
    return duration_mth_init() + t


def policy_year(t):
    """The contractual policy year containing month t: the 1-based label ``duration(t) + 1``.

    Used only where a 1-based schedule is looked up - the lapse table's
    ``policy_year`` key.  Never the index of anything in the projection.  It is 0 or less
    before issue, where nothing reads a table by it.
    """
    return duration(t) + 1


def age(t, life):
    """The attained age (ANB) of ``life`` in month t: ``x + duration(t)``.

    Advances on the policy anniversary rather than monthly, which is what an
    age-nearest-birthday basis means and how the mortality table is entered.
    """
    return age_at_entry(life) + duration(t)


def select_factor(t):
    """The select-duration factor applying in month t **[std]**; 0 outside cover.

    A 5-year select period, the structure of TMNL16/TFNL16 [R12], with the factor
    grading from 0.55 at duration 0 to 1.00 at and beyond ``select_period``.  Stepped by
    completed policy year, like the table it multiplies, read at
    ``min(duration(t), select_period)`` on the policy clock.  Read only on the *select*
    mortality basis; the *applied* basis takes the table as it stands.  The values are a
    standardization - the real tables are subscriber-only [R11] - and a licensed basis
    drops in by replacing the CSV.

    It is the one cell that reads ``Data.select_factor_array``, indexed by the duration,
    and it reads it only in cover: before issue ``duration(t)`` is negative, where
    :mod:`~.Term_UK_S`'s lookup raised ``KeyError``. A duration outside the table's, 0 to
    ``Data.select_last_duration``, where ``select_period`` runs beyond it or below 0,
    raises ``ValueError``, naming the point, rather than reading the array at another
    duration or wrapping round to its end.  The duration is read as an ``int``, as the
    compiled model holds ``select_period``, so a period written as a float, 3.0, reads
    the array at 3, as :mod:`~.Term_UK_S`'s lookup did, where numpy refuses a float index.
    """
    if not is_active(t):
        return 0.0
    d = min(duration(t), select_period)                              # noqa: F821
    if d < 0 or d > data.select_last_duration():                     # noqa: F821
        raise ValueError(f"point_id {point_id()}: select_factor_table.csv has no factor "
                         f"at duration {int(d)}")
    return float(data.select_factor_array()[int(d)])                 # noqa: F821


def mort_rate_base(t, life):
    """The annual mortality table rate for ``life`` at its attained age in month t.

    Includes terminal illness, which is an acceleration of the death benefit rather
    than a separate cover [S1][S6][S8]; the 16-Series tables the shipped table proxies
    are graduated on that basis [R10].

    Zero outside cover, where ``age(t, life)`` is not an age the policy reaches in force.
    Inside it, this is the one cell that reads ``Data.mort_table_array``, at the life's
    row, :func:`mort_group`, and its attained age, the array's index. An age outside the
    table's, ``Data.mort_age_first`` to ``Data.mort_age_last``, raises ``ValueError``,
    naming the point and the age, where :mod:`~.Term_UK_S`'s lookup raised ``KeyError``,
    rather than reading the array's padding.
    """
    if not is_active(t):
        return 0.0
    a = age(t, life)
    if a < data.mort_age_first() or a > data.mort_age_last():        # noqa: F821
        raise ValueError(f"point_id {point_id()}: mort_table.csv has no rate at "
                         f"attained age {a}")
    return float(data.mort_table_array()[mort_group(life), a])       # noqa: F821


def mort_rate_life(t, life):
    """The annual mortality (incl. TI) rate applied to ``life`` in month t.

    The table rate, then on the *select* basis the select factor and the **[std]** 75%
    proxy scaling, then the selective-lapsation loading.  Capped at 1, the bound second,
    ``min(q, 1.0)``, so that a missing input, a NaN, stays NaN, where ``min(1.0, q)``
    would read it as 1: :mod:`~.Term_UK_S`'s cap, and no departure.  ``Data`` refuses a
    blank, text or infinite value wherever the product reads one, so that none reaches
    it.  Past 1 the monthly rate, ``1 - (1 - q)^(1/12)``, has no real value; at 1 it is 1,
    and every policy in force at the start of the month dies in it.
    """
    q = mort_rate_base(t, life)
    if is_select_basis():
        q = q * select_factor(t) * mort_scale                        # noqa: F821
    return min(q * sel_lapse_factor(t), 1.0)


def mort_rate(t):
    """q(t): the **annual** mortality (incl. TI) decrement of the *policy* in month t.

    The single life's rate on a single-life policy.  On a joint first-death policy it
    is the joint decrement ``1 - (1 - q_1)(1 - q_2)`` **[std]** on one policy, which
    pays once and ends [S1][S6]; modelling the two lives as separate policies would pay
    twice.  :func:`mort_rate_mth` is what the projection actually decrements by.
    """
    q1 = mort_rate_life(t, 1)
    if not is_joint():
        return q1
    q2 = mort_rate_life(t, 2)
    return 1.0 - (1.0 - q1) * (1.0 - q2)


def mort_rate_mth(t):
    """q_m(t) = 1 - (1 - q(t))^(1/12): the monthly death and TI decrement **[std]**.

    The notes' own monthly-grid conversion, so the twelve months of a policy year
    compound back to that year's annual rate exactly.  The nominal alternative ``q/12``
    does not: twelve months of it leave ``(1 - q/12)^12 > 1 - q``, so it **understates**
    the decrement, by more the larger the rate.  The effective monthly rate is therefore
    always a little above ``q/12``.
    """
    return 1.0 - (1.0 - mort_rate(t)) ** (1.0 / 12.0)


def lapse_cum(t):
    """w_cum(t): the cumulative lapse ratio of the issued cohort at the start of month t.

    A share of the policies issued, not a running total of :func:`lapse_rate`, and it
    drives a loading on **mortality** rather than on lapse.  At :func:`t_entry` it is
    :func:`lapse_cum_init`, the ratio already reached at the valuation date, 0 on a point
    issued at or after it; each month after adds that month's lapses as a share of the
    issued cohort, :func:`cohort_frac` times the month's lapse probability, which
    :mod:`~.Term_UK_S` writes as ``pols_lapse(t - 1) / pols_if_init()``, the same number
    on a point that counts one policy issued.  Written count-free, it is the same whatever
    the count, and needs none of the policies issued, which a point in force does not
    carry.  0 outside cover.
    """
    if not is_active(t):
        return 0.0
    if t == t_entry():
        return lapse_cum_init()
    return (lapse_cum(t - 1) + cohort_frac(t - 1) * (1.0 - mort_rate_mth(t - 1))
            * lapse_rate_mth(t - 1))


def cohort_frac(t):
    """The share of the issued cohort in force at the start of month t: l(t) per policy
    issued.

    The notes' in-force probability ``l(t)``, ``l(0) = 1``, counted per policy issued: what
    :func:`lapse_cum` weights a month's lapse probability by.  1 at issue.  A point in
    force carries no count of the policies issued, so at :func:`t_entry` it is rebuilt
    from the opening state: every policy issued is still in force, has died or has lapsed,
    since none expires before the end of cover, so the policies issued are those in force
    and the deaths since issue, ``1 + fib_cum_init()`` per policy in force, over the share
    that has not lapsed, ``1 - lapse_cum_init()``, and this is the inverse of that ratio.
    Then the notes' roll-forward, ``l(t+1) = l(t)(1 - q_m)(1 - w_m)``, one cell a month.
    It holds no count, so the count moves none of it.  0 outside cover.
    """
    if not is_active(t):
        return 0.0
    if t == t_entry():
        return (1.0 - lapse_cum_init()) / (1.0 + fib_cum_init())
    return (cohort_frac(t - 1) * (1.0 - mort_rate_mth(t - 1))
            * (1.0 - lapse_rate_mth(t - 1)))


def sel_lapse_factor(t):
    """The selective-lapsation loading on mortality in month t **[std]**.

    ``1 + lambda max(0, w_cum(t) - w_ref)``.  Lapsers are healthier than persisters, so
    a block that has already shed a large proportion of its lives carries impaired
    mortality on the remainder - guaranteed premiums plus healthy-life rebroking make
    this a structural feature of UK term rather than an incidental one.  Off in the base
    run (``sel_lapse_lambda = 0``), where it returns 1 in every month.  On a point in
    force the ratio carries on from :func:`lapse_cum_init`, so the loading is what it
    would have been from issue.
    """
    return 1.0 + sel_lapse_lambda * max(                             # noqa: F821
        0.0, lapse_cum(t) - sel_lapse_ref)                           # noqa: F821


def lapse_rate_base(t):
    """The table **annual** lapse rate in month t **[std]**, before any rebroking.

    10 / 8 / 7 / 5 / 6 / 4 percent, anchored to the FCA's 5% average in-force lapse
    rate for pure protection and to the spike pattern just after the two- and four-year
    commission clawback periods end [R9].  A full duration curve is not public and the
    levels are standardized calibrations.  The table is keyed by the contractual
    1-based policy year, read at :func:`policy_year` ``(t)`` on the policy clock; policy
    years beyond the table take its last row, ``Data.lapse_last_year``.

    Zero outside cover, where the month has no policy year: before issue
    :func:`policy_year` is 0 or less, where :mod:`~.Term_UK_S`'s lookup raised
    ``KeyError``.  Inside it, this is the one cell that reads ``Data.lapse_table_array``,
    indexed by the policy year, which is 1 or more in cover and at most the table's last,
    since every later year is read at it: so both ends of the table hold the key, and no
    read meets the array's padding at index 0.
    """
    if not is_active(t):
        return 0.0
    y = min(policy_year(t), data.lapse_last_year())                  # noqa: F821
    return float(data.lapse_table_array()[y])                        # noqa: F821


def rebroke_factor(t):
    """M_reb(t): the rebroking multiplier on the lapse rate **[std]**; 1 in the base run.

    ``min(rebroke_cap, max(1, P_inforce / P_market))``.  Premiums are guaranteed, so
    there is no premium-shock lapse to model; the economic driver is rebroking when
    market premiums for the attained age fall below the in-force premium.
    ``premium_market_ratio`` is a flat scalar, so the multiplier is level in ``t`` -
    a market premium path would be another input table.
    """
    return min(rebroke_cap, max(1.0, premium_market_ratio))          # noqa: F821


def lapse_rate(t):
    """w(t): the **annual** lapse rate applying in month t.

    The table rate times the rebroking multiplier, capped at 1, in
    :mod:`~.Term_UK_S`'s order.  A lapse pays nothing: there is no surrender or paid-up
    value at any duration [S1][S6][S8][R8].
    """
    return min(1.0, lapse_rate_base(t) * rebroke_factor(t))


def lapse_rate_mth(t):
    """w_m(t) = 1 - (1 - w(t))^(1/12): the monthly lapse rate **[std]**.

    The notes' monthly-grid conversion, so twelve months of a policy year compound back
    to that year's table rate exactly.  As with :func:`mort_rate_mth`, a nominal ``w/12``
    would understate the decrement; the gap is wider here because the lapse rates are an
    order of magnitude larger than the mortality ones.
    """
    return 1.0 - (1.0 - lapse_rate(t)) ** (1.0 / 12.0)


def pols_if(t):
    """l(t): the number of policies in force at time t, the count that weights row t.

    ``pols_if_at(t, BEF_DECR)``: the count carried in from month t - 1, plus month t's
    new business, before month t's decrements. On a point issued at ``t = 0`` that is
    exactly :mod:`~.Term_UK_S`'s ``pols_if``, the count at the start of the month, which
    follows the notes' monthly recursion ``l(t+1) = l(t)(1 - q_m(t))(1 - w_m(t))``. It is
    ``basiclife.BasicTerm_SE``'s ``BEF_DECR`` count, not its ``pols_if``. Zero outside
    cover: before issue, and from ``t = proj_len()`` on, when the term has ended.
    """
    return pols_if_at(t, BEF_DECR)                                   # noqa: F821


def pols_if_at(t, timing):
    """The number of policies in force at a point inside month t.

    ``BEF_NB``
        The count carried in from month t - 1, before month t's new business: the
        survivors of month t - 1's deaths and lapses, out of month t - 1's
        ``BEF_DECR`` count. At :func:`t_entry`, the first month on the books, it is
        :func:`pols_if_init`, the count in force at the valuation date (0 for a point
        issued at or after it), and the recursion reads no earlier month. Zero outside
        cover, so the survivors of the last covered month leave as
        :func:`pols_maturity`.

    ``BEF_DECR``
        ``BEF_NB`` plus :func:`pols_new_biz`: l(t), the count that weights month t,
        which :func:`pols_if` returns.

    ``BEF_LAPSE``
        after deaths, before lapses - the notes' processing order is
        **death before lapse** **[std order]**, so this is the population
        lapses are taken from.

    ``AFT_DECR``
        l(t+1), the end-of-month state: what is left once the month's deaths and lapses
        are taken, and zero from the last covered month on, because the cover expires
        at its end. It is ``BEF_NB`` at t + 1 exactly, one product in one order.

    These are int References, 0 to 3, named as :mod:`~.Term_UK_S`'s strings (the Space
    docstring's *Codes*). ``BEF_NB`` is the one timing running in force adds, as
    ``basiclife.BasicTerm_SE`` names it; the other three are :mod:`~.Term_UK_S`'s, and any
    other raises. ``BEF_NB`` forms month t - 1's ``BEF_DECR`` count itself, as
    ``BEF_NB`` plus :func:`pols_new_biz` at t - 1, the same sum in the same order, rather
    than calling for it. So the chain of calls from month t back to :func:`t_entry` is one
    cell a month,
    where :mod:`~.Term_UK_S`'s ``pols_if`` chain runs three: a compiled model runs that
    chain on the C stack.
    """
    if timing == BEF_NB:                                             # noqa: F821
        if not is_active(t):
            return 0.0
        if t == t_entry():
            return pols_if_init()
        return ((pols_if_at(t - 1, BEF_NB) + pols_new_biz(t - 1))       # noqa: F821
                * (1.0 - mort_rate_mth(t - 1)) * (1.0 - lapse_rate_mth(t - 1)))
    if timing == BEF_DECR:                                           # noqa: F821
        return pols_if_at(t, BEF_NB) + pols_new_biz(t)                 # noqa: F821
    if timing == BEF_LAPSE:                                          # noqa: F821
        if not is_active(t):
            return 0.0
        return pols_if(t) * (1.0 - mort_rate_mth(t))
    if timing == AFT_DECR:                                           # noqa: F821
        if not is_active(t) or duration_mth(t) >= term_mths() - 1:
            return 0.0
        return pols_if_at(t, BEF_LAPSE) * (1.0 - lapse_rate_mth(t))    # noqa: F821
    raise ValueError("invalid timing")


def pols_new_biz(t):
    """The number of policies issued in month t: ``policy_count()`` in the issue month.

    The issue month is the one with ``duration_mth(t) == 0``: ``t = 0`` for a point
    issued at the valuation date, ``t = k`` for one issued ``k`` months later. A point
    already in force at the valuation date has none.
    """
    return policy_count() if duration_mth(t) == 0 else 0.0


def pols_death(t):
    """D(t) = l(t) q_m(t): expected death and terminal illness claims in month t.

    One decrement covering both: terminal illness accelerates the death benefit rather
    than adding to it [S1][S6][S8].  Zero outside cover, before any rate is read.
    """
    return pols_if(t) * mort_rate_mth(t) if is_active(t) else 0.0


def pols_lapse(t):
    """Lapses at the end of month t, taken from the survivors of mortality.

    Pays nothing - there is no surrender value [S6][R8] - so this moves
    :func:`pols_if` and nothing else.  Zero outside cover, before any rate is read.
    """
    if not is_active(t):
        return 0.0
    return pols_if_at(t, BEF_LAPSE) * lapse_rate_mth(t)                # noqa: F821


def pols_maturity(t):
    """Policies whose cover expires at the end of the term; zero in every other month.

    Non-zero only in the last covered month, ``duration_mth(t) = term_mths() - 1``, which
    is the frame's last row, ``t = proj_len() - 1``.  Not a decrement and not a benefit -
    the contract simply runs out, with no maturity value [S1][S2][S6][S8][R8] - but
    needed for the in-force roll-forward to close; see the Space docstring and
    :func:`check_pols_roll_fwd`.
    """
    if duration_mth(t) != term_mths() - 1:
        return 0.0
    return pols_if_at(t, BEF_LAPSE) * (1.0 - lapse_rate_mth(t))        # noqa: F821


def wop_active_frac(t):
    """act(t): the share of in-force policies active at the start of month t.

    The waiver of premium rider puts the life of each policy in force in one of three
    states **[std]**, as in :mod:`~.Term_UK_S`:

    * *active*: paying premium, and able to fall incapacitated, at ``inc_m`` a month;
    * *deferred*: incapacitated, and still paying, inside the ``wop_defer_mths`` months
      of the deferred period [S1] since the incapacity began;
    * *waived*: incapacitated past the deferred period, its premium waived, the share
      :func:`wop_waived_frac`.

    A deferred life and a waived one recover to active alike, at ``rec_m`` a month, and a
    deferred life that has not recovered by the end of the deferred period enters waiver.
    So the active share follows a two-state chain of its own, incidence out and recovery
    in, :mod:`~.Term_UK_S`'s::

        act(t+1) = act(t)(1 - inc_m) + (1 - act(t)) rec_m

    At :func:`t_entry` it is what the opening state leaves, all of it measured at the
    valuation instant: ``1 - wop_waived_frac_init() - wop_deferred_init(k)``, summed over
    the point's lags from its last down to 1, the order :func:`wop_waived_frac` takes them
    in.  So it is 1 on a point issued at or after the valuation date, which holds neither,
    and ``Data`` refuses an opening state whose waived share and pipeline sum past 1, so
    it is 0 or more; and the chain, at rates from 0 to 1, keeps it from 0 to 1.
    :func:`wop_waived_frac` reads it at the month its entrants fell incapacitated, from
    the valuation date on, since only an active life can.  1 unless the rider is in force,
    and 0 outside cover.
    """
    if not is_active(t):
        return 0.0
    if not wop():
        return 1.0
    if t == t_entry():
        held = wop_waived_frac_init()
        lags = min(wop_defer_mths, max(duration_mth_init(), 0))      # noqa: F821
        for k in range(lags, 0, -1):
            held = held + wop_deferred_init(k)
        return 1.0 - held
    a = wop_active_frac(t - 1)
    return a * (1.0 - wop_inc_rate_mth()) + (1.0 - a) * wop_rec_rate_mth()


def wop_waived_frac(t):
    """u(t): the share of in-force policies with premiums waived at the start of month t.

    The waived state of the three :func:`wop_active_frac` sets out, at monthly rates
    **[std]**, with the 26-week deferred period [S1] carried explicitly as
    ``wop_defer_mths`` months between incidence and the first waived premium::

        u(t+1) = u(t)(1 - rec_m) + inc_m act(t - defer) (1 - rec_m)^defer

    The entrants of month ``t + 1`` are the lives who became incapacitated ``defer``
    months earlier, in month ``src = t - defer``, and have not recovered since.  At
    :func:`t_entry` the share is :func:`wop_waived_frac_init`, 0 on a point issued at or
    after the valuation date.  An incidence month after the valuation date reads the
    active share then, :func:`wop_active_frac`, as :mod:`~.Term_UK_S` reads it; one before
    it, in the first ``wop_defer_mths`` months of the frame, is the pipeline's,
    :func:`wop_deferred_init` at lag ``-src``, the lives still in the deferred period at
    the valuation date, which the months of the deferred period after it, ``t`` of them,
    carry in at ``wop_rec_rate``; and one before issue has none, as :mod:`~.Term_UK_S`
    assumes before its frame.  The incidence falls on the active share alone: a life
    already in its deferred period cannot fall incapacitated again.

    The share computes ``u(t - 1)`` first and reads the active share after it, at a month
    that chain has reached already, so each read runs one cell deep and a cold call runs
    no deeper than the waived share's own chain, as before the active share was added:
    compiled, each chain runs on the C stack (``model-sec.md``, *What a compiled run
    needs*).

    The three shares partition the in-force, so at rates from 0 to 1, which
    :func:`proj_len` holds the rates to, and from an opening state ``Data`` holds to 1 or
    less, the share stays from 0 to 1; only rounding takes it past 1, by a few units in the
    last place, at an incidence near 1 with no recovery, as in :mod:`~.Term_UK_S`.

    Both rates are placeholders: no public UK incidence basis for the waiver work-tasks
    definitions appears in the fetched sources.  Mortality and lapse are assumed
    independent of the waiver state **[std]** - which is what lets the waived population
    be carried as a share of the in-force rather than as its own decrement.  Zero
    unless the rider is in force, and outside cover.
    """
    if not wop() or not is_active(t):
        return 0.0
    if t == t_entry():
        return wop_waived_frac_init()
    prev = wop_waived_frac(t - 1)
    src = t - 1 - wop_defer_mths                                     # noqa: F821
    if src >= t_entry():
        entrants = (wop_inc_rate_mth() * wop_active_frac(src)
                    * (1.0 - wop_rec_rate_mth()) ** wop_defer_mths)  # noqa: F821
    elif duration_mth_init() + src >= 0:
        entrants = wop_deferred_init(-src) * (1.0 - wop_rec_rate_mth()) ** t
    else:
        entrants = 0.0
    return prev * (1.0 - wop_rec_rate_mth()) + entrants


def wop_inc_rate_mth():
    """inc_m: the monthly waiver incidence rate, ``1 - (1 - inc)^(1/12)`` **[std]**.

    :mod:`~.Term_UK_S`'s formula, uncapped: on a waiver point :func:`proj_len` refuses a
    ``wop_inc_rate`` outside 0 to 1: below 0 this is negative, and past 1 it has no
    real value.
    """
    return 1.0 - (1.0 - wop_inc_rate) ** (1.0 / 12.0)                # noqa: F821


def wop_rec_rate_mth():
    """rec_m: the monthly waiver recovery rate, ``1 - (1 - rec)^(1/12)`` **[std]**.

    :mod:`~.Term_UK_S`'s formula, uncapped: on a waiver point :func:`proj_len` refuses a
    ``wop_rec_rate`` outside 0 to 1: below 0 this is negative, and past 1 it has no
    real value.
    """
    return 1.0 - (1.0 - wop_rec_rate) ** (1.0 / 12.0)                # noqa: F821


def pols_payer(t):
    """The number of in-force policies actually paying premium in month t.

    ``l(t)`` less the waived share.  Equal to :func:`pols_if` unless the waiver of
    premium rider is in force.  Zero outside cover.
    """
    if not is_active(t):
        return 0.0
    return pols_if(t) * (1.0 - wop_waived_frac(t))


def idx_increase():
    """The cover increase offered at each anniversary under the indexation option.

    ``min(max(RPI, 0), 10%)`` [S1][S2][S6][S7], times ``idx_accept_rate``.  The
    notes' base run is deterministic and always accepts, which is what the shipped
    ``idx_accept_rate = 1`` means; their 80% take-up **[std]** would be a mixture of
    paths, and scaling the increase instead is a deterministic approximation to it.
    ``rpi_rate`` is the RPI assumed from the valuation date on; the increases already
    given are the opening state, :func:`idx_factor_init`.

    One consequence worth stating: with acceptance certain, the rule removing the option
    after three consecutive declines [S1][S6] (two at one insurer [S8]) is never
    reached, so it is not implemented.
    """
    return min(max(rpi_rate, 0.0), idx_cover_cap) * idx_accept_rate  # noqa: F821


def idx_factor(t):
    """idx(t): the cumulative **cover** indexation factor in month t.

    Steps on the policy anniversary and is level through the policy year, because the
    increase is offered at an anniversary and not monthly: :func:`idx_factor_init` in
    the policy year under way at :func:`t_entry`, 1 at issue, then one factor of
    ``1 + idx_increase()`` per anniversary passed since, ``duration(t) -
    duration(t_entry())``.  The increases before the valuation date are history, carried
    in, and those after it are projected at ``rpi_rate``.  1 whenever the option is not
    elected, and 0 outside cover, where there is no cover to index.

    The exponent is a whole number of years, 0 or more, so the power is real whatever the
    base.  It passes the largest float only where the References put the increase above
    about 2 million a year, which the shipped cap, 10%, does not.  Python's float power
    raises ``OverflowError`` past the largest float, where C's ``pow`` gives an infinity,
    so where the power is infinite from a finite base the cell calls Python's own, which
    raises the platform's message in the compiled model as in modelx (USLIB-SEC-PLAN.md,
    *Record -- M22*); modelx never reaches the call, its own power raising first.
    """
    if not is_active(t):
        return 0.0
    if not indexation():
        return 1.0
    base = 1.0 + idx_increase()
    n = duration(t) - duration(t_entry())
    factor = base ** n
    if factor - factor != 0.0 and base - base == 0.0:
        raise float.__pow__(base, n)
    return idx_factor_init() * factor


def idx_prem_factor(t):
    """idx_p(t): the cumulative **premium** indexation factor in month t.

    The premium rises by ``min(1.5 x increase, 15%)`` for a cover increase of
    ``increase`` [S1][S2][S6], on the same anniversary step as the cover factor, from
    :func:`idx_prem_factor_init`.  The 1.5 multiplier is what makes an accepted increase
    premium-margin-accretive if mortality is proportional to cover - and what reverses
    the sign of that conclusion if acceptance is selective, impaired lives accepting
    while healthy ones decline **[std]** concern.  No public take-up data exists.  1
    whenever the option is not elected, and 0 outside cover.

    The exponent is a whole number of years, as :func:`idx_factor`'s is, and the power
    passes the largest float only where the References put the step above about 2 million
    a year, which the shipped cap, 15%, does not; there the cell raises Python's
    ``OverflowError`` in both engines, as :func:`idx_factor` does.
    """
    if not is_active(t):
        return 0.0
    if not indexation():
        return 1.0
    step = 1.0 + min(idx_prem_mult * idx_increase(), idx_prem_cap)   # noqa: F821
    n = duration(t) - duration(t_entry())
    factor = step ** n
    if factor - factor != 0.0 and step - step == 0.0:
        raise float.__pow__(step, n)
    return idx_prem_factor_init() * factor


def premium_pp(t):
    """P_m idx_p(t): the gross premium per policy due in month t.

    The contractual monthly premium on a ``monthly`` payer, and ``12 P_m`` in the first
    month of each policy year, ``duration_mth(t) % 12 == 0``, and nil in the rest on an
    ``annual`` one - the timing difference the annual grid could not see.  Indexed if the
    option is elected, and loaded by ``wop_prem_loading`` where the waiver rider is in
    force - a **[std]** placeholder, since the rider's extra premium is not published
    either.  Zero outside cover.
    """
    if not is_active(t):
        return 0.0
    if prem_cycle() == 12:
        p = 12.0 * premium_mth_pp() if duration_mth(t) % 12 == 0 else 0.0
    else:
        p = premium_mth_pp()
    p = p * idx_prem_factor(t)
    return p * (1.0 + wop_prem_loading) if wop() else p              # noqa: F821


def premiums(t):
    """Premium income at the start of month t, an inflow.

    Carried on :func:`pols_payer`, never on the FIB ledger: premiums stop at death
    while family income benefit instalments continue.  Collected only from the policies
    still in force at the start of the month.
    """
    return premium_pp(t) * pols_payer(t)


def sched_rate_mth():
    """j_m = (1+j)^(1/12) - 1: the decreasing schedule's monthly rate **[std]**.

    The effective convention, not a nominal ``j/12``.  The two give slightly different
    schedules, so the convention has to be stated; ``benefit_sched(60) = £134,588`` on
    the anchor cell is the notes' validation anchor for an implementation.
    """
    return (1.0 + sched_rate()) ** (1.0 / 12.0) - 1.0


def benefit_sched(k):
    """B(k): the decreasing shape's benefit after k policy months [S1][S6][S8].

    ``SA0 [(1+j_m)^N - (1+j_m)^k] / [(1+j_m)^N - 1]``, a mortgage-style amortization
    from ``B(0) = SA0`` to ``B(N) = 0``.  A zero schedule rate degenerates to straight
    line, which the closed form cannot express.  Keyed by the policy month, not by
    ``t``: :func:`benefit_pp` reads it at ``duration_mth(t)``, in cover only.

    ``Data`` refuses a schedule rate below 0, or not a finite number, so ``1 + j_m`` is 1
    or more, and the divisor is above 0 wherever ``j_m`` is.  ``(1 + j_m)^N`` passes the
    largest float on a 50-year term from a rate of about 1.5 million a year; there the
    cell raises Python's ``OverflowError`` in both engines, as :func:`idx_factor` does.
    """
    n_m = term_mths()
    jm = sched_rate_mth()
    if jm == 0.0:
        return sum_assured() * (n_m - k) / n_m
    grown = (1.0 + jm) ** n_m
    if grown - grown != 0.0 and jm - jm == 0.0:
        raise float.__pow__(1.0 + jm, n_m)
    return sum_assured() * (grown - (1.0 + jm) ** k) / (grown - 1.0)


def annuity_certain_factor(m):
    """a(m): the m-month annuity-certain factor at the FIB commutation rate **[std]**.

    ``[1 - (1+r_c)^(-m/12)] / [(1+r_c)^(1/12) - 1]``, instalments in arrears.  Used
    only by the commutation module, at the months left to the end of the term.

    :func:`proj_len` refuses, on a family income benefit point, a rate that is not a
    finite number above -1, so the base ``1 + r_c`` is above 0.  The divisor, the monthly
    rate, is tested for 0, as :func:`benefit_sched` tests :func:`sched_rate_mth`, and
    there the factor is ``m``, the closed form's limit: at a rate of 0, as in
    :mod:`~.Term_UK_S`, and at one whose monthly rate rounds to 0, such as 1e-17, where
    ``1 + r_c`` is 1 and :mod:`~.Term_UK_S`, which tests the annual rate, divides by zero.
    Within about 2e-8 of -1, ``(1 + r_c)^(-m/12)`` passes the largest float at the
    longest commutation; there the cell raises Python's ``OverflowError`` in both
    engines, as :func:`idx_factor` does.
    """
    if m <= 0:
        return 0.0
    base = 1.0 + fib_commute_disc_rate                               # noqa: F821
    j_m = base ** (1.0 / 12.0) - 1.0
    if j_m == 0.0:
        return float(m)
    v = base ** (-m / 12.0)
    if v - v != 0.0 and base - base == 0.0:
        raise float.__pow__(base, -m / 12.0)
    return (1.0 - v) / j_m


def fib_commute_pp(t):
    """CV: the commuted value of one FIB stream arising from a death in month t **[std]**.

    ``I a(N - k)`` at the exact death month on the policy clock, ``k = duration_mth(t)``,
    so it falls to zero as the term runs out.  :mod:`~.Term_UK_S` reads ``N - t``, the
    same month only on a point issued at ``t = 0``.  Zero on the level and decreasing
    shapes, and outside cover.
    """
    if not is_active(t) or not is_fib():
        return 0.0
    return fib_income() * annuity_certain_factor(term_mths() - duration_mth(t))


def benefit_pp(t):
    """DB(t): the death and terminal illness benefit per policy in month t.

    Level: ``SA0 idx(t)``.  Decreasing: the exact schedule balance ``B(k)`` at the policy
    month ``k = duration_mth(t)``, the outstanding amount through the month the claim
    falls in.  FIB: the commuted value of the instalment stream, which is what a
    commuted claim pays; an uncommuted FIB claim has no lump sum at all and goes through
    ``claims(t, FIB)`` instead.  Zero outside cover, before any schedule is read: before
    issue ``B(k)`` at a negative month would exceed the sum assured without a word.  The
    shape is read from its flags, :func:`is_level` and :func:`is_decreasing`, in
    :mod:`~.Term_UK_S`'s order, the family income benefit the shape that is neither.
    """
    if not is_active(t):
        return 0.0
    if is_level():
        return sum_assured() * idx_factor(t)
    if is_decreasing():
        return benefit_sched(duration_mth(t))
    return fib_commute_pp(t)


def fib_cum(t):
    """FIBcum(t): the expected deaths since issue, at the start of month t.

    ``sum of D(s) for s < t`` since issue: at :func:`t_entry` the deaths before the
    valuation date, ``fib_cum_init() x pols_if_init()``, 0 on a point issued at or after
    it, and each month after adds that month's deaths.  **Not decremented** by mortality
    or lapse.  On every shape it counts the deaths since issue, as :mod:`~.Term_UK_S`'s
    does, and :func:`cohort_frac` opens from it; :mod:`~.Term_UK_S` pays the family
    income benefit on ``(1 - c)`` of it, which this model pays on :func:`fib_streams`
    instead, the streams in payment.  0 outside cover.
    """
    if not is_active(t):
        return 0.0
    if t == t_entry():
        return fib_cum_init() * pols_if_init()
    return fib_cum(t - 1) + pols_death(t - 1)


def fib_streams(t):
    """The expected family income benefit streams in payment at the start of month t.

    At :func:`t_entry` the streams of the deaths before the valuation date that were not
    commuted, ``fib_streams_init() x pols_if_init()``, history, 0 on a point issued at or
    after it; each month after adds the share of that month's deaths not commuted at
    today's take-up, ``(1 - c) D(t - 1)``.  **Not decremented** by mortality or lapse:
    once a claim is admitted the instalments are an annuity-certain to the end of the
    term whatever happens to any life [S6][S8].  Only *new* claims carry ``l(t)``.
    :mod:`~.Term_UK_S` holds no such cell: it pays ``(1 - c) x FIBcum(t)``, the same
    number at a take-up that never changes, and on new business the same floats where
    ``1 - c`` scales exactly, at the shipped take-ups of 0 and 1 and at 0.5.  0 outside
    cover, and on the level and decreasing shapes, which pay no instalments.
    """
    if not is_active(t) or not is_fib():
        return 0.0
    if t == t_entry():
        return fib_streams_init() * pols_if_init()
    return fib_streams(t - 1) + (1.0 - fib_commute_rate()) * pols_death(t - 1)


def claims(t, kind):
    """Benefit outgo in month t, by kind, and the three kinds' total.

    ``DEATH``
        the lump sum paid at the end of the month of death: ``DB(t) D(t)`` on
        the level and decreasing shapes, and on the ``fib`` shape only the
        commuted proportion of the streams.

    ``FIB``
        the family income benefit instalments falling in month t,
        ``I [(1 - c) D(t) + streams(t)]`` - one instalment for every stream in payment,
        :func:`fib_streams`, those that began before the valuation date included, and for
        the month's new claims not commuted, since the instalments are in arrears from
        the month of death.  :mod:`~.Term_UK_S`'s ``(1 - c) I [D(t) + FIBcum(t)]`` at a
        take-up that never changes; at one changed at the valuation date, the streams
        already in payment stay in payment.  Zero on the other two shapes.

    ``LAPSE``
        zero, always.  There is no surrender or paid-up value at any duration
        [S1][S6][S8][R8]; the kind exists so that the zero is stated rather
        than left to inference.  See the Space docstring.

    ``ALL``
        the three kinds' total, :mod:`~.Term_UK_S`'s ``claims(t)``, whose ``kind=None``
        sums the three with Python's ``sum``, which compiles to no C.  It is written left
        to right from ``0.0``, ``0.0 + DEATH + FIB + LAPSE``, which is ``sum``'s float
        wherever at most two kinds are non-zero in a month: ``sum`` carries the rounding
        error of each addition, Neumaier's way, and adds it back once at the end, and the
        error of a single addition, added back, rounds to the sum it came from.  Here the
        lapse kind is 0.0 in every month, so at most two kinds are ever non-zero, the
        lump sum and the instalments of a family income benefit commuted in part; and
        ``0.0 +`` the first kind is ``sum``'s start, the int 0, which turns a negative
        zero to ``0.0``.  So the total is :mod:`~.Term_UK_S`'s float in every month.  A
        product whose three kinds can be non-zero together writes Neumaier's loop out
        instead, as :func:`check_fib_ledger_resid` does.

    These are int References, 0 to 3, named as :mod:`~.Term_UK_S`'s strings (the Space
    docstring's *Codes*), and any other raises.
    """
    if kind == DEATH:                                                # noqa: F821
        if is_fib():
            return fib_commute_rate() * benefit_pp(t) * pols_death(t)
        return benefit_pp(t) * pols_death(t)
    if kind == FIB:                                                  # noqa: F821
        if not is_fib():
            return 0.0
        return fib_income() * ((1.0 - fib_commute_rate()) * pols_death(t)
                               + fib_streams(t))
    if kind == LAPSE:                                                # noqa: F821
        return 0.0
    if kind == ALL:                                                  # noqa: F821
        return 0.0 + claims(t, DEATH) + claims(t, FIB) + claims(t, LAPSE)  # noqa: F821
    raise ValueError("invalid kind")


def claim_expenses(t):
    """ec D(t): the claim handling expense on the month's death and TI claims **[std]**.

    £250 per claim, uninflated.  Kept out of :func:`expenses` because the notes' worked
    example prints the two as separate columns.
    """
    return expense_claim * pols_death(t)                             # noqa: F821


def inflation_factor(t):
    """The expense inflation factor in month t, ``(1 + pi)^(t // 12)`` **[std]**.

    On the **valuation** clock: ``t`` counts months from the valuation date, so the
    maintenance charge it inflates is in valuation-date pounds, whatever the policy's
    age, and every point of a block inflates alike, stepping on each anniversary of the
    valuation date.  :mod:`~.Term_UK_S` inflates from issue, ``(1 + pi)^duration(t)``,
    the notes' ``e(t) = 30 x 1.03^t`` with ``t`` the policy year; on a point issued at
    ``t = 0`` the two are the same.  Acquisition is not inflated (see :func:`expenses`).

    The exponent is a whole number of years, so the power is real whatever the base.  It
    passes the largest float within the longest frame only where ``inflation_rate`` is
    above about 140,000 a year in size; there the cell raises Python's ``OverflowError``
    in both engines, as :func:`idx_factor` does.
    """
    base = 1.0 + inflation_rate                                      # noqa: F821
    n = t // 12
    factor = base ** n
    if factor - factor != 0.0 and base - base == 0.0:
        raise float.__pow__(base, n)
    return factor


def expenses(t):
    """E0 and e(t): acquisition and inflating maintenance expense in month t **[std]**.

    £150 per policy issued, ``expense_acq * pols_new_biz(t)``: in the issue month, never
    for a point already in force at the valuation date, and not inflated, as in
    ``basiclife.BasicTerm_SE``.  :mod:`~.Term_UK_S` charges it on the count at ``t = 0``,
    which on a point issued then is the count issued.  Then £30 per policy per year - a
    twelfth of it each month - inflating at 3% on the valuation clock, both at the start
    of the month.  Premiums as low as £5/month against a £30 annual maintenance expense
    make this assumption solvency-relevant on small-sum-assured blocks, which is why the
    notes rate expense inflation a first-order lever despite its size.
    """
    return (expense_acq * pols_new_biz(t)                            # noqa: F821
            + expense_maint / 12.0 * inflation_factor(t) * pols_if(t))  # noqa: F821


def comm_init_pp():
    """c0: initial commission per policy issued **[std]**.

    On a point issued at or after the valuation date, 150% of the annualized premium of
    the first policy year, ``12 P_m``, paid upfront at issue, with the waiver's loading
    where the rider is in force: the issue premium's, :mod:`~.Term_UK_S` multiplying by
    ``idx_prem_factor(0)``, which is 1 at issue.  On a point in force at the valuation
    date, the commission it paid when it was written, :func:`comm_init_pp_init`: history,
    which ``comm_init_rate``, the rate on new business from the valuation date on, does
    not reach back to.  Roughly 96% of protection commission is paid upfront [R9], which
    with the acquisition expense is what produces the deep first-month new business
    strain in the worked example.
    """
    if duration_mth_init() > 0:
        return comm_init_pp_init()
    p = 12.0 * premium_mth_pp()
    if wop():
        p = p * (1.0 + wop_prem_loading)                             # noqa: F821
    return comm_init_rate * p                                        # noqa: F821


def comm_clawback(t):
    """Initial commission recovered on lapses inside the clawback window **[std]**.

    ``c0 (clawback_mths - m)/clawback_mths`` per lapsed policy, ``m = duration_mth(t) + 1``
    the months in force at the end of month t on the policy clock, linear in months in
    force, ``c0`` the commission the policy paid, :func:`comm_init_pp`.  Off in the base
    run (``clawback_mths`` is 0); set it to 48 for the notes' four-year rule.  Clawback
    periods of two to four years are evidenced [R9]; the linear formula is a
    standardization.  Inside the window it reverses the sign of the early-lapse
    sensitivity, which is the point of carrying it.  Zero outside cover.
    """
    if clawback_mths <= 0 or not is_active(t):                       # noqa: F821
        return 0.0
    mths = duration_mth(t) + 1
    if mths >= clawback_mths:                                        # noqa: F821
        return 0.0
    return (comm_init_pp() * (clawback_mths - mths)                  # noqa: F821
            / clawback_mths * pols_lapse(t))                         # noqa: F821


def commissions(t):
    """Commission outgo in month t **[std]**, net of any clawback recovered.

    The initial commission on the policies issued in the month,
    ``comm_init_pp() * pols_new_biz(t)``, then 2.5% of premium income from the second
    policy year (``duration_mth(t) >= 12``), on the policy clock.  Both are levels chosen
    for the reference implementation; only the upfront *pattern* is evidenced [R9].
    """
    init = comm_init_pp() * pols_new_biz(t)
    renew = comm_renewal_rate * premiums(t) if duration_mth(t) >= 12 else 0.0  # noqa: F821
    return init + renew - comm_clawback(t)


def net_cf(t):
    """CF(t): the net cash flow of month t, **income positive**.

    Premiums less death and terminal illness claims, claim expense, maintenance and
    acquisition expense and commission.  The notes' own sign - they write ``+ = inflow``
    - which is also the library-wide convention, so unlike the whole life and payout
    annuity models there is no outgo-positive ``liability_cf`` companion to publish.
    """
    return (premiums(t) - claims(t, ALL) - claim_expenses(t)          # noqa: F821
            - expenses(t) - commissions(t))


def check_pols_roll_fwd_resid(t):
    """The in-force roll-forward residual in month t; zero everywhere.

    ``pols_if(t) - pols_if_at(t + 1, BEF_NB) - deaths - lapses - expiries``, where the
    count carried into the next month is taken before its new business, which is no part
    of month t's movement.  Expiries are non-zero only in the last covered month, where
    the survivors neither die nor lapse: their cover runs out.  Without that term the
    last month appears to lose lives with no cause.
    """
    return (pols_if(t) - pols_if_at(t + 1, BEF_NB)                    # noqa: F821
            - pols_death(t) - pols_lapse(t) - pols_maturity(t))


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


def check_fib_ledger_resid(t):
    """The family income benefit ledger residual in month t; zero everywhere.

    :func:`claims` ``(t, FIB)`` less an independent rebuild of the same figure: one
    instalment for every stream in payment at the valuation date,
    ``fib_streams_init() x pols_if_init()``, and for the share not commuted of every death
    in month t or any earlier month on the books, summed straight off the death vector
    with no reference to the :func:`fib_streams` recursion.  A ledger that was decremented
    by mortality or lapse - the notes' pitfall - one that paid only the month-of-death
    instalment, or one that lost the streams already in payment would show up here.  Zero
    by definition on the level and decreasing shapes, which have no ledger.

    The deaths are summed from :func:`t_entry` in an explicit loop that compensates as
    Python's ``sum()`` of floats does from Python 3.12, Neumaier's improvement of Kahan's
    summation, the error of each addition carried and added back at the end where it is
    a finite number other than zero, ``abs(c) <= 1.7976931348623157e308``, the largest
    double: so the sum is stage ``E``'s ``sum()`` of a generator, bit for bit, and
    compiled it is C on doubles, added in the order written, since nothing in the build
    lets the compiler reassociate and no multiply and add is fused into one rounding
    (``-ffp-contract=off``).  A month before :func:`t_entry` sums no death, ``0.0``, as
    ``sum()`` of none is the int 0.
    """
    if not is_fib():
        return 0.0
    deaths = 0.0
    c = 0.0
    for s in range(t_entry(), t + 1):
        x = pols_death(s)
        u = deaths + x
        if abs(deaths) >= abs(x):
            c = c + ((deaths - u) + x)
        else:
            c = c + ((x - u) + deaths)
        deaths = u
    if c != 0.0 and abs(c) <= 1.7976931348623157e308:
        deaths = deaths + c
    built = fib_streams_init() * pols_if_init() + (1.0 - fib_commute_rate()) * deaths
    return claims(t, FIB) - fib_income() * built                     # noqa: F821


def check_fib_ledger():
    """True when the family income benefit ledger closes in every month of the frame.

    No argument, one bool over all t, the library-wide shape of a ``check_*`` cells;
    :func:`check_fib_ledger_resid` gives the signed residual of the month that failed.
    The tolerance scales with ``policy_count()``, as the roll-forward's does.
    """
    return all(abs(check_fib_ledger_resid(t)) <= 1e-10 * max(policy_count(), 1.0)
               for t in range(proj_len()))


def result_cf():
    """Result table of cashflows, one row per month ``t = 0 .. proj_len() - 1``.

    Row 0 is the valuation month for every model point, so the frames of a block line up
    and sum row by row.  A point issued after the valuation date has zeros until its issue
    month.  ``pols_if`` is the count that weights every cash flow on the same row.  The
    columns are :mod:`~.Term_UK_S`'s: ``net_cf`` carries the notes' own income-positive
    sign, and ``claims_lapse`` is a column of zeros by product design - there is no
    surrender value - and is published rather than dropped; see the Space docstring.
    """
    ts = list(range(proj_len()))
    return pd.DataFrame(                                             # noqa: F821
        {
            "pols_if": [pols_if(t) for t in ts],
            "premiums": [premiums(t) for t in ts],
            "claims_death": [claims(t, DEATH) for t in ts],            # noqa: F821
            "claims_fib": [claims(t, FIB) for t in ts],                # noqa: F821
            "claims_lapse": [claims(t, LAPSE) for t in ts],            # noqa: F821
            "claim_expenses": [claim_expenses(t) for t in ts],
            "expenses": [expenses(t) for t in ts],
            "commissions": [commissions(t) for t in ts],
            "net_cf": [net_cf(t) for t in ts],
        },
        index=pd.Index(ts, name="t"),                                # noqa: F821
    )


def result_pols():
    """Result table of policy counts and decrement rates, one row per month t.

    The same rows as :func:`result_cf`, ``t = 0 .. proj_len() - 1``.  First the counts
    :func:`result_cf` weights its rows by, and how they move, as
    ``basiclife.BasicTerm_SE``'s ``result_pols`` sets them out: ``pols_if``, the count of
    month t; ``pols_new_biz``, the part of it issued in month t; then month t's deaths and
    lapses in processing order, and the expiries of the last covered month.  Row by row,
    ``pols_if`` at ``t + 1`` is ``pols_if`` less the three outflows of month t, plus the
    new business of month ``t + 1``.  Then :mod:`~.Term_UK_S`'s other four columns: the
    policies paying premium, ``fib_cum``, the deaths since issue, and the **monthly**
    decrements the projection actually applies, which are 0 outside cover, where the model
    reads no rate.
    """
    ts = list(range(proj_len()))
    return pd.DataFrame(                                             # noqa: F821
        {
            "pols_if": [pols_if(t) for t in ts],
            "pols_new_biz": [pols_new_biz(t) for t in ts],
            "pols_death": [pols_death(t) for t in ts],
            "pols_lapse": [pols_lapse(t) for t in ts],
            "pols_maturity": [pols_maturity(t) for t in ts],
            "pols_payer": [pols_payer(t) for t in ts],
            "fib_cum": [fib_cum(t) for t in ts],
            "mort_rate_mth": [mort_rate_mth(t) if is_active(t) else 0.0 for t in ts],
            "lapse_rate_mth": [lapse_rate_mth(t) if is_active(t) else 0.0 for t in ts],
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

FIB = 1

LAPSE = 2

ALL = 3

issue_age_min = 18

policy_term_max = 50

policy_term_max_fib = 40

expiry_age_max = 90

expiry_age_max_fib = 70

select_period = 5

mort_scale = 0.75

sel_lapse_lambda = 0.0

sel_lapse_ref = 0.2

premium_market_ratio = 1.0

rebroke_cap = 2.0

rpi_rate = 0.03

idx_cover_cap = 0.1

idx_prem_mult = 1.5

idx_prem_cap = 0.15

idx_accept_rate = 1.0

expense_acq = 150.0

expense_maint = 30.0

expense_claim = 250.0

inflation_rate = 0.03

comm_init_rate = 1.5

comm_renewal_rate = 0.025

clawback_mths = 0

fib_commute_disc_rate = 0.03

wop_inc_rate = 0.004

wop_rec_rate = 0.35

wop_defer_mths = 6

wop_prem_loading = 0.05

pd = ("Module", "pandas")
