# modelx: pseudo-python
# This file is part of a modelx model.
# It can be imported as a Python module, but functions defined herein
# are model formulas and may not be executable as standard Python.

"""The by-policy projection of the :mod:`~.ULB_UK_SEC` model; holds all formulas.

The Space is parameterized by ``point_id``, so ``Projection[1]`` is an ItemSpace
projecting model point 1, the twin of :mod:`~.ULB_UK_S`'s anchor cell, issued at the
valuation date::

    >>> Projection[1].result_cf()          # one row per month from the valuation date
    >>> Projection[1].result_pols()        # the counts behind it
    >>> Projection.point_id = 7            # or switch the default

This is :mod:`~.ULB_UK_S` taught to run in force at a valuation date, as lifelib's
``basiclife.BasicTerm_SE`` extends ``basiclife.BasicTerm_S``. A formula of
:mod:`~.ULB_UK_S` is rewritten where it depends on where the projection starts, where it
must answer for a month outside cover, or where it read a policy month as ``t``; every
other formula is :mod:`~.ULB_UK_S`'s own, the cap on mortality, ``min(q, 1.0)``, among
them. ``products/unit_linked_bond/model-sec.md`` lists the rewritten cells with the reason
for each.

.. rubric:: Input data

Inputs are **external files**: plain CSVs living in the model folder's parent
directory, ``products/unit_linked_bond/``, read at run time rather than stored inside
the model. The model folder therefore holds nothing but formulas — no ``_data/``, no
IOSpec, no embedded values — so a diff of the model shows logic changes only, and an
input can be edited or swapped without rewriting the model. This follows
``annuallife.TradLife_A``; contrast ``basiclife.BasicTerm_S``, which keeps its inputs
*inside* the model through modelx's IOSpec machinery.

The consequence worth knowing: **the model is not portable on its own.** Copying the
``ULB_UK_SEC`` folder without its parent's CSVs produces a model that reads and then
fails on first evaluation.

The two assumption tables are the files :mod:`~.ULB_UK_S` reads, read in place; the model
point table is this model's own. Each table has a filename Reference and a reader Cells,
both on :mod:`~.ULB_UK_SEC.Data`, reached here through the ``data`` Reference:

======================  ==============================  ==========================
Reference               Cells                           File
======================  ==============================  ==========================
model_point_file        data.model_point_table()        model_point_table_sec.csv
mort_table_file         data.mort_table()               mort_table.csv
surr_table_file         data.surr_table()               surr_table.csv
======================  ==============================  ==========================

.. rubric:: Two clocks

``t`` counts months from the **valuation date**, 0-based, the clock
``basiclife.BasicTerm_SE`` runs on: ``t = 0`` is the valuation month for every model
point, however old the bond, month ``t`` runs from time ``t`` to time ``t + 1``, and the
frame is ``t = 0 .. proj_len() - 1``, where :func:`proj_len` counts the months from the
valuation date to the end of the bond's projection: the limiting age, or the month its
fund is exhausted, whichever comes first. Row ``t`` is the same month for every point, so
the frames of a block line up and sum row by row.

``duration_mth(t)`` counts **policy months**, the months the bond has been in force at
time ``t``: ``duration_mth(t) = duration_mth_init() + t``, where
:func:`duration_mth_init` is read from the model point — positive for a bond in force at
the valuation date, 0 for one issued at it, ``-k`` for one issued ``k`` months later, at
most ten years later. Everything contractual reads it: the completed policy years
``duration(t) = duration_mth(t) // 12``, the 1-based ``policy_year(t) = duration(t) + 1``,
which is the insurance year of the tax allowance, the attained age
``age(t) = age_at_entry() + duration(t)``, and through them the mortality and surrender
tables, the surrender bands, the allowance-exhaustion step from policy year 21 and the
twenty years of 5% allowance. The limiting age and the fund's exhaustion are policy
months too, :func:`horizon_mths` and :func:`fund_exhaust_mth`.

One input reads the valuation clock instead: expense inflation,
``inflation_factor(t) = (1 + inflation_rate) ** (t // 12)``, stepping on each
anniversary of the valuation date, so that the maintenance charge is in valuation-date
pounds for every point alike. Acquisition is charged per policy issued, in the issue
month, and not inflated, as in ``basiclife.BasicTerm_SE``. The fund return and the return
shock are flat References, the same on either clock.

On a point issued at ``t = 0`` the two clocks coincide and this model computes what
:mod:`~.ULB_UK_S` computes: every cell the two share agrees at every argument
:mod:`~.ULB_UK_S` evaluates in its sweep, but for those whose meaning changed —
``pols_if_init``, now the count already in force at the valuation date, and
``model_point``, a row of another table — and :mod:`~.ULB_UK_S`'s ``av_init_pp``, which
:func:`av_pp_init` replaces. The one exception by design is where the fund runs out
(*The fund runs out, and the frame ends there*, below).
``tests/test_model_conventions_uk.py`` asserts it cell by cell.

.. rubric:: Counts

``pols_if(t)`` is the count that weights row ``t``: ``pols_if_at(t, "BEF_DECR")``, the
count carried in from ``t - 1`` (``"BEF_NB"``) plus the month's new business,
:func:`pols_new_biz`, before the month's decrements. A point in force at the valuation
date opens with :func:`pols_if_init`, its ``policy_count``; one issued at or after the
valuation date opens with none, and takes its ``policy_count`` as new business in its
issue month. The recursion's base is :func:`t_entry`, the first month on the books, and
nothing is counted outside the frame: before issue every count, and so every cash flow,
is zero, and the survivors of the frame's last month leave as :func:`pols_maturity`.
:mod:`~.ULB_UK_S`'s three timings are kept, ``"BEF_DECR"``, ``"BEF_SURR"`` and
``"AFT_DECR"``, and ``"BEF_NB"`` is the one running in force adds.

.. rubric:: The opening state

A bond in force carries, beside its count, what :mod:`~.ULB_UK_S` carries into the month
a point is valued at, each per policy, so that the count is the one weight on every flow,
and each measured at the valuation instant, the start of month 0, before any month-0
event:

* :func:`av_pp_init`, the unit fund, the bid value of units: :mod:`~.ULB_UK_S`'s
  ``uf_init`` renamed, holding ``av_pp`` of the month it opens, so the fund at outset on a
  bond not yet in force, its premium as shipped;
* :func:`wd_cum_pp_init`, the withdrawals and adviser charges cancelled since issue,
  which carry on the allowance-relevant total and open the guaranteed minimum death
  benefit, ``max(0, P - wd_cum_pp_init)``;
* :func:`allowance_cum_pp_init`, the 5% allowance accrued since issue, through the policy
  year of the month before the valuation date, which the excess gain is measured against:
  on an anniversary the year that begins in month 0 accrues in month 0, at the References
  of the valuation date, as every month-0 event does.

Each is history, read from the model point, never recomputed from a Reference, which is
an assumption from the valuation date on: a fund return, a withdrawal rate or an
allowance rate changed at the valuation date reaches back over no month already run.
Later policy years accrue the allowance at the References of the day,
``wd_allowance_rate`` a year for ``allowance_years`` from issue. The excess gain is the
withdrawals since issue less that allowance, and the allowance-exhaustion step a closed
form on the policy year; the premium, the charges, the withdrawal pattern and the rider
are columns.

.. rubric:: Naming

Cells names follow lifelib's ``savings.CashValue_SE`` and ``basiclife.BasicTerm_S``
wherever those models have an analogue, and the account-value vocabulary the U.S. models
in this library settled on — ``av_pp_at(t, timing)`` for the fund read at a point inside
the month, ``check_av_roll_fwd`` for its identity. What running in force adds is named as
``basiclife.BasicTerm_SE`` names it: ``duration_mth`` read from the model point,
``policy_count``, ``pols_new_biz``, ``pols_if_at``'s ``"BEF_NB"`` timing, ``is_active``
and ``result_pols``. ``duration_mth_init``, the policy months completed at the valuation
date, takes ``UL_US_S``'s name; ``t_entry`` is this model's own, and each opening-state
cell is the cell it opens with ``_init`` added. The technical notes use compact symbols
instead. The mapping is:

=========================  ==============================  ==========================
Notes symbol               Cells                           Meaning
=========================  ==============================  ==========================
t                          (the cells argument)            Months from the valuation
(none)                     duration_mth(t)                 Policy months at time t
(none)                     duration_mth_init()             Policy months at t = 0
(none)                     t_entry()                       First month on the books
(none)                     is_active(t)                    Whether month t is in cover
y = duration + 1           policy_year(t)                  Policy year containing month t
a                          age(t)                          Attained age (ALB)
(none)                     duration(t)                     Completed policy years
(none)                     horizon_mths()                  Policy month of omega_age
(none)                     fund_exhaust_mth()              Policy month the fund is out
(frame)                    proj_len()                      Months to the frame's end
P                          premium()                       Single premium
UF(t)                      av_pp(t)                        Unit fund at time t (start of month t)
UF at t = 0                av_pp_init()                    Unit fund at the valuation
UF_g(t), UF'(t), UF(t+1)   av_pp_at(t, timing)             The fund inside month t
(per segment)              av_per_segment_pp(t)            The fund divided by the segments
g                          fund_return                     Annual gross fund return
g_m                        fund_return_mth()               Its monthly equivalent
G$(t)                      fund_growth_pp(t)               Gross return credited in month t
t_pf                       tax_provision_rate()            Tax provision rate
TX(t)                      tax_provision_pp(t)             Tax provision deducted
c, c_m                     amc_rate(), amc_rate_mth()      Annual management charge
AMC$(t)                    amc_pp(t)                       AMC collected in month t
f, f_m                     further_costs_rate()            Fund-borne further costs
FC$(t)                     further_costs_pp(t)             Further costs borne in month t
u                          db_uplift()                     Death-benefit uplift, 1.001
W(t)                       wd_pp(t)                        Withdrawal cancelled at EOM
(cap)                      wd_cap_pp(t)                    Rolling 12-month withdrawal cap
(pattern)                  wd_pattern()                    none / allowance_5pct / custom
AC(t)                      adviser_charge_pp(t)            Ongoing adviser charge
GC(t)                      gmdb_charge_pp(t)               GMDB rider charge
G(t)                       gmdb_guarantee_pp(t)            GMDB guaranteed amount
gmdb_flag                  gmdb_flag()                     Rider elected
DS(t)                      death_strain_pp(t)              Non-unit cost per death
q_a, q_m(t)                mort_rate(t), mort_rate_mth(t)  Mortality rates
w_base(y)                  surr_rate_base(t)               Table surrender rate
M_perf(t)                  perf_factor(t)                  Performance lapse multiplier
M_allow(y)                 allow_factor(t)                 Allowance-exhaustion step
w_ann(y,t), w_m(t)         surr_rate(t), surr_rate_mth(t)  Surrender rates applied
(none)                     policy_count()                  Policies the point stands for
l(t)                       pols_if(t)                      Count weighting month t
(l at t = 0)               pols_if_init()                  Count in force at t = 0
(none)                     pols_new_biz(t)                 Policies issued in month t
l(t+1) (AFT_DECR)          pols_if_at(t, timing)           The within-month counts
(none)                     pols_death(t)                   Deaths in month t
(none)                     pols_surr(t)                    Surrenders at the end of month t
(none)                     pols_maturity(t)                In force when the frame ends
CumWD(n)                   wd_cum_pp(t)                    Cumulative withdrawals + charges
(CumWD at t = 0)           wd_cum_pp_init()                Withdrawn since issue, t = 0
CumAllow(n)                allowance_cum_pp(t)             Cumulative 5% allowable element
(CumAllow at t = 0)        allowance_cum_pp_init()         Allowance accrued, t = 0
ExcessGain(n)              excess_gain_pp(t)               Excess-event gain, policyholder side
E(t)                       expenses(t)                     Acquisition + maintenance
(none)                     inflation_factor(t)             Expense inflation factor
(unit cancellations)       claims(t, kind)                 Gross benefit outgo by kind
(none)                     unit_releases(t)                Units cancelled to fund benefits
(none)                     withdrawals(t)                  Withdrawal outgo
AMC$ x l                   amc_charges(t)                  AMC margin collected
FC$ x l                    further_costs(t)                Further costs, a pass-through
TX x l                     tax_provisions(t)               Tax provision, a pass-through
NUCF(t)                    net_cf(t)                       Non-unit cash flow, income positive
(none)                     result_pols()                   The counts, month by month
=========================  ==============================  ==========================

Four names needed care in :mod:`~.ULB_UK_S`, and keep their reasons here.

``UF`` is the unit fund, and the library calls a policyholder-owned fund
:func:`av_pp_at`. The house name wins, because one concept must not carry two names
across the library — but the docstrings and the ``result_cf`` columns keep the unit
vocabulary the product is actually discussed in, and ``av_pp(t)`` is documented
everywhere as the notes' ``UF(t)``, the fund at time ``t``.

``G`` is used twice in the notes: ``G$(t)`` is the gross fund return credited in the
month and ``G(t)`` the GMDB guaranteed amount. They become :func:`fund_growth_pp` and
:func:`gmdb_guarantee_pp`; nothing here is called ``G``.

``net_cf`` on this product is the **non-unit** cash flow, not a gross liability total.
That is not a departure from the library convention but the consequence of the product:
every benefit is funded by cancelling the policyholder's own units, so a gross
presentation adds the same money to both sides. The gross flows are still published —
``claims_death``, ``claims_surrender``, ``withdrawals`` and ``unit_releases`` are
``result_cf`` columns — and :func:`check_unit_funding` asserts that they net exactly
against the fund.

``pols_maturity`` is borrowed from the term models and, as in ``WOL_UK_S``, means
something different: a bond has no maturity date, so this is the population still in
force when the frame ends. It pays nothing and exists only so the roll-forward closes in
the last month.

.. rubric:: The unit fund recursion, and the order the charges come in

Per policy, within month ``t`` (from time ``t`` to time ``t + 1``)::

    UF_g(t) = UF(t) x (1 + g_m(1 - t_pf))            growth, net of the tax provision
    UF'(t)  = UF_g(t) x (1 - c_m - f_m)              AMC and further costs
    UF(t+1) = UF'(t) - W(t) - AC(t) - GC(t)          unit cancellations at end of month

The **order matters and is a listed pitfall**. The annual management charge accrues
daily through the unit price, so it is levied on the post-growth, pre-cancellation fund.
Charging it on ``UF(t)`` instead, or after the withdrawal, moves the margin by about
half a month's growth or withdrawal — small in one month and systematic over decades.
:func:`av_pp_at` exposes all three points so the ordering is inspectable rather than
buried in one expression. :func:`av_pp` writes the same three steps of the month before
inline, in the same order, so that the fund's chain of calls from month ``t`` back to
:func:`t_entry` is one cell a month, where :mod:`~.ULB_UK_S`'s runs through
:func:`av_pp_at` at three timings, four cells a month: a compiled model runs that chain
on the C stack.

.. rubric:: What is margin and what is a pass-through

Only two of the four amounts that leave the unit fund are insurer income:

============================  ==============  ===================================
Amount                        Insurer income  Why
============================  ==============  ===================================
AMC                           **yes**         the charge for managing the contract
GMDB rider charge             **yes**         the price of the guarantee
Further costs                 no              fund-borne expenses, paid on to the fund
Tax provision                 no              collected in-price, paid on as tax
Adviser charges               no              post-RDR pass-throughs facilitated by
                                              cancelling units
============================  ==============  ===================================

Booking the pass-throughs as margin is the notes' second-listed pitfall and would
overstate the year-one non-unit result by more than the AMC itself — the tax provision
alone is about 97% of the AMC on the anchor cell, and the further costs another 10%.
:func:`further_costs` and :func:`tax_provisions` are therefore published as their own
``result_cf`` columns and are **not** in :func:`net_cf`, so the exclusion is visible.

.. rubric:: The death strain is the uplift, not the death benefit

The sum assured is ``u x UF``, of which ``UF`` is funded by cancelling the policyholder's
own units. The non-unit cost per death is therefore only

    DS(t) = (u - 1) UF(t+1) + max(0, G(t) - u UF(t+1)) 1{gmdb}

— a tenth of a percent of the end-of-month fund on the composite, plus any in-the-money
guarantee.
The uplift is a **parameter and never a literal**: 100.1% against 101% is a tenfold
difference in death strain, which the notes list as a pitfall and model point 5
exercises.

.. rubric:: The 5% allowance is policyholder tax machinery, not a product feature

:func:`allowance_cum_pp` and :func:`excess_gain_pp` track the cumulative 5% tax-deferred
allowance and the excess-event gain it produces when exceeded. **Neither generates an
insurer cash flow.** The allowance never caps what can be withdrawn — the *product* cap
is the rolling 7.5% of :func:`wd_cap_pp` — and treating it as a product feature is a
listed pitfall. It is carried because it drives behaviour: the allowance-exhaustion step
in :func:`allow_factor` raises surrender from policy year 21, once twenty years of
allowance have been drawn.

.. rubric:: The fund runs out, and the frame ends there

A 5% withdrawal against a 5% gross return is not sustainable once the tax provision and
the charges are taken: the fund drifts down and, on the deterministic base run, reaches
zero inside the annuitant's lifetime. :func:`wd_pp` caps the withdrawal at what the fund
can pay, so the fund never goes negative, and :func:`proj_len` ends the frame at
:func:`fund_exhaust_mth` — a bond with no units has no liability, no margin and nothing
left to project. That is a product fact worth seeing rather than an artefact to hide:
the anchor cell's fund is exhausted around policy year 30, and every margin the insurer
was counting on stops there.

Where the withdrawal cap binds, the month closes the fund on a subtraction that is 0 in
exact arithmetic, which in floating point leaves 0 or a rounding of either sign, floored
at 0; with an adviser or rider charge beside the withdrawal it is a rounding as often as
not. :mod:`~.ULB_UK_S` ends its frame at the first month the fund opens on 0 or less, so a
rounding above 0 runs it on, a month or several, charging expenses against a fund of
1e-15, and whether it does turns on the fund's last bit. This model ends it at the first
month the fund opens at or below ``depletion_threshold``, half a pence **[std]**, which
the rounding never reaches and a fund in use is never near, as ``VA_US_SEC`` tests its
depletion: a recorded departure from :mod:`~.ULB_UK_S`'s exact test of 0. Its effect on
each of :mod:`~.ULB_UK_S`'s six points:

* points 1, 4 and 5, on which nothing but the withdrawal is cancelled, close their funds
  on 0 exactly at the end of policy month 352, and their frames, 353 months, are S's;
* points 2 and 6 never exhaust their funds, and run to the limiting age, 660 and 780
  months, as in S;
* point 3, whose adviser charge leaves a rounding of 3.4e-15 at the end of month 322, is
  projected for 323 months where :mod:`~.ULB_UK_S` projects 324: its survivors, 0.0194
  policies, mature in month 322 rather than carry on, and its net cash flow differs by
  S's month 323 alone, £0.18 of maintenance against an AMC of 6e-20.

A bond in force whose fund is at or below the threshold at the valuation date has nothing
to project, and :func:`proj_len` refuses it.

.. rubric:: Behaviour is the whole valuation

Every margin line is proportional to the unit fund **and** to persistency, and a
surrender costs nothing at the point of exit — the surrender value is the bid value of
units, cancelled — while truncating the entire future AMC stream. Two dynamic overlays
sit on the base table, both **[std]** and both inert in the deterministic base run:

- :func:`perf_factor`, ``min(2, 1 + 2 max(0, g_ref - R_12m))``, raising surrender after
  poor performance. The base run has ``R_12m = g_ref`` by construction, so it is 1;
  ``return_shock`` moves the trailing return without disturbing the fund path, which
  is what makes the multiplier testable in isolation.
- :func:`allow_factor`, a step to 1.5 from policy year 21, when the tax allowance is
  spent.

There is no interest-sensitive dynamic lapse and no paid-up state: the product is single
premium, so there is no premium obligation to stop.

.. rubric:: The contract's bounds

What running in force adds is the contract's own bounds, which :func:`proj_len` holds a
point to: an issue age of ``issue_age_min``, 18, or more, the youngest the mortality table
rates, though the product admits issue from 3 months; cover from issue below
``omega_age``; and a bond still inside it at the valuation date. ``Data`` bounds future
new business by ``future_horizon_mth``, 120 months. And :func:`proj_len` holds every
Reference a formula reads through a bound, a power or a product to its domain, NaN and
the infinities outside each, its docstring naming each domain and its reason.
"""

from modelx.serialize.jsonvalues import *

_formula = lambda point_id: None

_bases = []

_allow_none = None

_spaces = []

# ---------------------------------------------------------------------------
# Cells

def model_point():
    """The selected model point, its row of ``model_point_table_sec.csv``, as a Series.

    A row of this model's own table, which carries the in-force interface beside
    :mod:`~.ULB_UK_S`'s columns. Each attribute a formula reads has an accessor below.
    """
    return data.model_point_table().loc[point_id]                    # noqa: F821


def age_at_entry():
    """The issue age of the selected model point, **age last birthday**.

    ALB is chosen to index directly into the single-year-of-age table used as the
    **[std]** mortality proxy.  The anchor documents quote contractual age limits next
    birthday; the difference is immaterial to a product whose death strain is a tenth of
    a percent of the fund.  The age at issue, not at the valuation date: ``age(0)`` is
    the attained age there.
    """
    return int(model_point()["age_at_entry"])


def sex():
    """The sex (M / F) of the selected model point."""
    return model_point()["sex"]


def lives():
    """``single``.  Joint last-death bonds are out of scope in this composite.

    :mod:`~.ULB_UK_S`'s guard, which no formula calls, so that a joint row would project
    as single: ``Data`` refuses any other value as the table is read.
    """
    v = model_point()["lives"]
    if v != "single":
        raise ValueError("invalid lives")
    return v


def premium():
    """P: the single premium, net of any set-up adviser charge.

    Top-ups are excluded from the base projection: a top-up is a new model point with
    its own premium, allowance clock and segments **[std]**.  The premium paid at issue,
    on a bond in force as on new business: the GMDB guarantees it, less what has been
    drawn, and the 5% allowance accrues on it.
    """
    return float(model_point()["premium"])


def n_segments():
    """The number of identical segments the bond is written in; 100 **[std]**.

    Per-segment values are bond values divided by this.  Modelling at bond level is
    exact only while all segments stay identical - a segment surrender breaks the
    symmetry - and the composite keeps bond-level modelling and notes the approximation.
    """
    return int(model_point()["n_segments"])


def db_uplift():
    """u: the death benefit as a multiple of the bid value of units; 1.001.

    A **parameter and never a literal**: 100.1% against 101% is a tenfold difference in
    death strain, which is the whole non-unit cost of mortality on this product.  Model
    point 5 is the anchor cell at 101% and exists to make that visible.
    """
    return float(model_point()["db_uplift"])


def amc_rate():
    """c: the annual management charge, 1.00% **[std]**.

    A snapshot of a discretionary element: per-fund charge rate cards are not published,
    and the insurer's provisions allow the charge to be increased.  It is the insurer's
    only material income line, so its level sets the whole result.
    """
    return float(model_point()["amc_rate"])


def further_costs_rate():
    """f: the fund-borne further costs, 0.10% **[std]**.

    Reduces the unit fund and is **not** insurer income - it is paid on as a fund
    expense.  Booking it as margin is a listed pitfall.
    """
    return float(model_point()["further_costs_rate"])


def tax_provision_rate():
    """t_pf: the life-fund tax provision taken in-price, 20% of gross return **[std]**.

    Collected through the unit price and paid on as corporation tax, so it is neutral to
    the insurer's margin in this model.  The real I-E position has timing differences -
    income as received, realised gains at the next charge date, an annual deemed
    disposal, settlement on full surrender - and base differences including expense
    relief and the minimum profits test, all of which create insurer-side tax strain or
    float that this proxy does not capture.
    """
    return float(model_point()["tax_provision_rate"])


def wd_pattern():
    """``none``, ``allowance_5pct`` or ``custom``: the regular withdrawal pattern.

    ``allowance_5pct`` is the anchor: 5% of premium a year, taken monthly.  That is the
    pattern every fetched key features document leads with, it sits inside the 7.5%
    product cap, and adviser charges consume the same tax allowance - so rational
    take-up gravitates to 5% inclusive of charges.  ``Data`` refuses any other value.
    """
    v = model_point()["wd_pattern"]
    if v not in ("none", "allowance_5pct", "custom"):
        raise ValueError("invalid wd_pattern")
    return v


def wd_rate():
    """The annual regular withdrawal as a fraction of the premium.

    Zero on ``none``, 5% on ``allowance_5pct``, and the model point's own rate on
    ``custom``.  The election from the valuation date on: what was withdrawn before it is
    :func:`wd_cum_pp_init`.  ``allowance_5pct`` reads ``wd_allowance_rate``, the one
    Reference that is also the statutory allowance rate (:func:`allowance_cum_pp`), as
    :mod:`~.ULB_UK_S` reads it: the pattern is "withdraw what the allowance allows", so a
    rate changed at the valuation date moves that pattern's withdrawals from then on, and
    the allowance from the next policy year, together.
    """
    p = wd_pattern()
    if p == "none":
        return 0.0
    if p == "allowance_5pct":
        return wd_allowance_rate                                     # noqa: F821
    return float(model_point()["wd_rate_custom"])


def oac_rate():
    """The ongoing adviser charge as an annual rate on the unit value; 0 in the base run.

    Post-RDR adviser charges are **pass-throughs** facilitated by cancelling units: they
    reduce the fund and consume the policyholder's tax allowance, and they add nothing to
    the insurer's non-unit cash flow.  Treating them as income is a listed pitfall.
    """
    return float(model_point()["oac_rate"])


def gmdb_flag():
    """Whether the return-of-premium death benefit rider is elected; false in the base.

    With it, the death strain stops being negligible and becomes market-contingent, and
    the rider's charge scale is unpublished - so the **[std]** cost-of-insurance form
    used here is a guess.  Enable it only with its own sensitivity set.
    """
    return bool(model_point()["gmdb_flag"])


def policy_count():
    """The number of policies the model point stands for, its ``policy_count`` column.

    A point in force at the valuation date counts the bonds in force then, before any
    month-0 event; any other point counts the bonds it issues. Either way the count
    enters the projection once: as :func:`pols_if_init` for the first, as
    :func:`pols_new_biz` in the issue month for the second. It is the one weight on every
    flow: every opening-state column is per policy.
    """
    return float(model_point()["policy_count"])


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

    The bond's age in months at ``t = 0``: 66 for a bond issued five and a half years
    before the valuation date, 0 for one issued at it, and -13 for one to be issued 13
    months after it, which ``Data`` admits up to ``future_horizon_mth`` months ahead. It
    is read as ``basiclife.BasicTerm_SE`` reads it, and is the one fact the policy clock
    takes from the model point.
    """
    return int(model_point()["duration_mth"])


def av_pp_init():
    """UF at the valuation date: the unit fund per policy entering month 0.

    :mod:`~.ULB_UK_S`'s ``uf_init`` column, renamed: the bid value of units at the start of
    the month the frame opens, before its growth, charges and cancellations, so on a bond
    in force at the valuation date :mod:`~.ULB_UK_S`'s ``av_pp`` of that month. History, read
    from the model point: what the fund has earned and borne since issue, which no
    ``fund_return`` set at the valuation date reaches back to. On a bond not yet in force
    it keeps :mod:`~.ULB_UK_S`'s meaning, the fund at outset, the premium on every shipped
    point. Above 0, which ``Data`` requires; on a bond in force above
    ``depletion_threshold``, which :func:`proj_len` requires, a bond whose fund is
    exhausted having nothing to project.
    """
    return float(model_point()["av_pp_init"])


def wd_cum_pp_init():
    """CumWD at the valuation date: the withdrawals and adviser charges since issue.

    :func:`wd_cum_pp`'s value entering month 0, per policy: every withdrawal and adviser
    charge cancelled at the end of a month before the valuation date, the total the tax
    allowance is measured against. History, read from the model point, not recomputed
    from the withdrawal pattern, which is the election from the valuation date on: a
    withdrawal taken once, or a pattern changed since issue, is in it. It also opens the
    guaranteed minimum death benefit, :func:`gmdb_guarantee_pp`, ``max(0, P -
    wd_cum_pp_init)``. 0 on a bond not yet in force, which ``Data`` requires.
    """
    return float(model_point()["wd_cum_pp_init"])


def allowance_cum_pp_init():
    """CumAllow at the valuation date: the 5% allowance accrued since issue.

    :func:`allowance_cum_pp`'s value entering month 0, per policy: the allowable element
    of every policy year from issue to the one month -1 falls in, each accrued at its
    start.  Measured at the valuation instant, before any month-0 event (USLIB-SEC-PLAN.md
    D6, precised at M7): mid-year that is the year under way, and on an anniversary the
    year before it, the year that begins in month 0 accruing in month 0, at the References
    of the valuation date, as on a bond issued then.  History, read from the model point,
    not rebuilt from ``wd_allowance_rate`` and ``allowance_years``, which are assumptions
    from the valuation date on: an allowance rate changed there accrues every year that
    begins from month 0 on, and moves no year already accrued.  0 on a bond not yet in
    force, which ``Data`` requires.
    """
    return float(model_point()["allowance_cum_pp_init"])


def t_entry():
    """The first month the bond is on the books: ``max(0, -duration_mth_init())``.

    0 for a point in force at the valuation date or issued at it, ``k`` for one issued
    ``k`` months later. It is the base of every recursion: the count, the unit fund and
    the withdrawals since issue open there, from the opening state, and none reads a
    month before it. :func:`fund_exhaust_mth` scans the fund from it.
    """
    return max(0, -duration_mth_init())


def is_active(t):
    """Whether month t is inside cover: issued, and short of the limiting age.

    ``0 <= duration_mth(t) < horizon_mths()``. False before issue and from the month the
    bond reaches ``omega_age``. Outside cover the unit fund is 0, and so is every flow,
    charge and rate read at a policy year or an attained age the bond does not have.

    It reads the limiting age alone, not :func:`proj_len`: the frame also ends where the
    fund runs out, which :func:`fund_exhaust_mth` finds by projecting the fund, and the
    fund reads this. So in the months after the fund is exhausted and before the limiting
    age, a bond is in cover and holds no units; there the counts are 0, because the frame
    has ended.
    """
    return 0 <= duration_mth(t) < horizon_mths()


def duration(t):
    """Completed policy years at the start of month t: ``duration_mth(t) // 12``.

    0 throughout the first policy year, and negative before issue.
    """
    return duration_mth(t) // 12


def duration_mth(t):
    """Completed policy months at the start of month t, the **policy** clock.

    ``duration_mth_init() + t``: ``t`` counts months from the valuation date and
    ``duration_mth(t)`` months from issue, and the two move together. A closed form,
    where ``basiclife.BasicTerm_SE`` adds one a month by recursion: the same numbers,
    without a call chain as long as the frame. Negative before issue.
    """
    return duration_mth_init() + t


def policy_year(t):
    """y = duration(t) + 1: the 1-based policy year containing month t.

    A contractual label derived from the policy clock, never the index itself.  Also
    the **insurance year** the tax allowance is tracked against.  It is 0 or less before
    issue, where nothing reads a table or a band by it.
    """
    return duration(t) + 1


def age(t):
    """a: the attained age (ALB) in the policy year containing month t."""
    return age_at_entry() + duration(t)


def horizon_mths():
    """The mortality horizon in policy months: ``12 x (omega_age - age_at_entry)``.

    The policy month at which the bond reaches the limiting age, on the policy clock, so
    the last month of cover is ``duration_mth(t) = horizon_mths() - 1``. :func:`proj_len`
    counts from the valuation date instead.
    """
    return 12 * (omega_age - age_at_entry())                         # noqa: F821


def fund_exhaust_mth():
    """The policy month at which the unit fund has been drawn to nothing.

    The first month on the books whose opening fund ``av_pp(t)`` is at or below
    ``depletion_threshold``, as a policy month, ``duration_mth(t)``: the fund is
    exhausted at the start of that month, having been cancelled to nothing at the end of
    the month before, so the month is also the number of months the bond carried units
    from issue.  ``horizon_mths() + 1`` if the fund never is, before the limiting age.  A
    5% withdrawal against a 5% gross return is not sustainable once the tax provision and
    the charges are taken, so on the deterministic base run the anchor cell's fund does
    run out - at policy month 353, in policy year 30 - and every margin the insurer was
    counting on stops there.  Searched rather than solved, so that any withdrawal pattern
    and charge basis resolves.

    The search is one loop in this cell, over the months from :func:`t_entry` to the
    limiting age, ascending, so that it reads each month's fund once that of the month
    before is known: the far read R2 admits, as ``DIA_US_SEC``'s survival to its payout
    date is, and the only one it makes, the policy month being formed from
    :func:`duration_mth_init` rather than read.  It starts at :func:`t_entry`, not at 0,
    because a bond issued later holds no fund before its issue month, which a search from
    0 would read as exhausted at once.

    :mod:`~.ULB_UK_S` tests the fund against 0, so that a month the withdrawal cap closes
    on a rounding above 0, rather than on 0, runs the frame on; the threshold ends it
    there (the Space docstring).
    """
    end = horizon_mths() - duration_mth_init()
    for t in range(t_entry(), end):
        if av_pp(t) <= depletion_threshold:                          # noqa: F821
            return duration_mth_init() + t
    return horizon_mths() + 1


def proj_len():
    """The number of months from the valuation date to the end of the frame.

    ``min(horizon_mths(), fund_exhaust_mth()) - duration_mth_init()``: the limiting age
    or the fund's exhaustion, whichever comes first, counted from the valuation date
    rather than from issue.  353 for the anchor cell issued at ``t = 0``, whose fund is
    exhausted at policy month 353; 287 for it valued at month 66; and the frame from
    issue plus ``k`` for a bond issued ``k`` months after the valuation date.  The frame is
    ``t = 0, 1, ..., proj_len() - 1``; ``proj_len()`` is its exclusive end and the row
    count of :func:`result_cf`.  A bond has no maturity date, so the horizon is a limiting
    age - but a bond with no units has no liability, no margin and nothing left to
    project, so the projection also ends when the fund does: the last month is the one
    whose closing fund is exhausted.

    These raise here, naming the point, rather than project nothing, a frame the
    contract does not have, or one that no value of a Reference defines, each checked in
    this order:

    * ``issue_age_min`` that is not a whole number, 0 or more, below ``2**53``: an age,
      which a NaN would switch off, every comparison with it failing, and which the
      compiled model holds as a ``long long``;
    * a bond issued below ``issue_age_min``, 18, the youngest age the mortality table
      rates, though the product admits issue from 3 months;
    * ``omega_age`` that is not a whole number below ``2**53``, above ``issue_age_min`` and
      at most the mortality table's last age, ``Data.mort_age_last()``: the limiting age
      sizes every frame, so the compiled model's caches, and a NaN, an infinity or a
      fraction of a year would leave the frame's months no whole number;
    * one issued at or past ``omega_age``, which has no cover from issue;
    * one whose cover had ended by the valuation date, at or past the limiting age, which
      an in-force extract should not carry;
    * one read under a Reference outside its domain, each named. NaN and the infinities
      are outside every one: :mod:`~.ULB_UK_S` reads several of them through a ``min`` or
      a ``max`` whose bound comes first, which keeps the bound where a NaN meets it, so
      that the NaN is lost rather than carried:

      - ``fund_return`` and ``inflation_rate``, finite, -1 or more: below -1 the monthly
        return, ``(1 + g)^(1/12) - 1``, has no real value, and the inflation factor
        changes sign each year;
      - ``return_shock``, finite, and with ``fund_return`` a trailing year's return,
        ``fund_return + return_shock``, above -1: a return of -100% or less is a fund lost
        whole; a NaN shock would read as no shock, through the shortfall's ``max(0, ...)``;
      - ``mort_be_factor``, finite, 0 or more: below 0 a mortality rate is negative;
      - ``wd_allowance_rate``, finite, 0 or more: below 0 the allowance accrued and the
        anchor pattern's withdrawal are negative;
      - ``allowance_years``, a whole number of years, 0 or more, below ``2**53``: below 0
        the allowance accrued is negative, a NaN would let it accrue without end, and the
        compiled model holds it as a ``long long``;
      - ``depletion_threshold``, finite, 0 or more: below 0 no fund, floored at 0, would
        ever count as exhausted;
      - ``surr_rate_cap`` and ``wd_cap_rate``, from 0 to 1: the cap on a probability, and
        the share of the fund or the premium a year's withdrawals may take; a NaN
        withdrawal cap would pay no withdrawal, through the room's ``max(0, ...)``, and a
        negative one the same;
      - ``perf_factor_cap``, ``perf_factor_slope`` and ``allow_step``, finite, 0 or more:
        multipliers of a probability, below 0 a negative surrender rate; a NaN would be
        lost in the bound-first ``min`` of the multiplier's cap or of :func:`surr_rate`,
        which would then read the surrender cap in every month it reaches;

    * one in force at the valuation date whose fund, :func:`av_pp_init`, is at or below
      ``depletion_threshold``: the fund is exhausted, and the bond has nothing to project;
    * one not yet in force whose fund at outset, :func:`av_pp_init`, is at or below it,
      which holds nothing to project from its issue month.

    The rules read this Space's References, which ``Data`` cannot see, so they are
    checked here.  They are the contract a compiled model's caches are sized from: a
    frame of at most ``omega_age - issue_age_min`` years and the future horizon, and ages
    from 18 to ``omega_age`` on the mortality table.  Every report reads this cell first,
    and so does every count, so no point outside them is projected.  Each check is a
    comparison written out, a finite bound the largest float, 1.7976931348623157e308, and
    a whole one ``2**53``, so that a compiled cell runs it in C, as ``Term_UK_SEC``'s do,
    and each Reference is printed as the compiled model will type it: ``issue_age_min``,
    ``omega_age`` and ``allowance_years`` through ``int()`` once they are whole numbers,
    and every other through ``float()``.  A value a formula computes past the floats,
    from References each in its domain, is refused in the cell where it first is: the
    fund, at ``av_pp_at(t, "AFT_GROWTH")``, and the allowance.
    """
    if not (issue_age_min > -9007199254740992.0                       # noqa: F821
            and issue_age_min < 9007199254740992.0                    # noqa: F821
            and issue_age_min == issue_age_min // 1):                 # noqa: F821
        raise ValueError(f"point_id {point_id}: issue_age_min must be a whole number "  # noqa: F821
                         f"below 2**53, not {float(issue_age_min)}")  # noqa: F821
    if issue_age_min < 0:                                            # noqa: F821
        raise ValueError(f"point_id {point_id}: issue_age_min must be 0 or more, "  # noqa: F821
                         f"not {int(issue_age_min)}")                # noqa: F821
    x = age_at_entry()
    if x < issue_age_min:                                            # noqa: F821
        raise ValueError(f"point_id {point_id}: the issue age, {x}, is below "  # noqa: F821
                         f"issue_age_min, {int(issue_age_min)}")     # noqa: F821
    if not (omega_age > -9007199254740992.0                           # noqa: F821
            and omega_age < 9007199254740992.0                        # noqa: F821
            and omega_age == omega_age // 1):                         # noqa: F821
        raise ValueError(f"point_id {point_id}: omega_age must be a whole number "  # noqa: F821
                         f"below 2**53, not {float(omega_age)}")     # noqa: F821
    if not (omega_age > issue_age_min                                # noqa: F821
            and omega_age <= data.mort_age_last()):                   # noqa: F821
        raise ValueError(
            f"point_id {point_id}: omega_age must be above issue_age_min, "  # noqa: F821
            f"{int(issue_age_min)}, and at most mort_table.csv's last age, "  # noqa: F821
            f"{data.mort_age_last()}, not {int(omega_age)}")         # noqa: F821
    if horizon_mths() <= 0:
        raise ValueError(f"point_id {point_id}: the issue age, {x}, is at or past "  # noqa: F821
                         f"omega_age, {int(omega_age)}: the bond has no cover")  # noqa: F821
    d = duration_mth_init()
    if d >= horizon_mths():
        raise ValueError(
            f"point_id {point_id}: duration_mth {d} is at or past the end of cover, "  # noqa: F821
            f"policy month {horizon_mths()}, the limiting age {int(omega_age)}")  # noqa: F821
    if not (fund_return >= -1.0                                      # noqa: F821
            and fund_return <= 1.7976931348623157e308):               # noqa: F821
        raise ValueError(f"point_id {point_id}: fund_return must be a finite number, "  # noqa: F821
                         f"-1 or more, not {float(fund_return)}")    # noqa: F821
    if not (inflation_rate >= -1.0                                   # noqa: F821
            and inflation_rate <= 1.7976931348623157e308):            # noqa: F821
        raise ValueError(f"point_id {point_id}: inflation_rate must be a finite number, "  # noqa: F821
                         f"-1 or more, not {float(inflation_rate)}")  # noqa: F821
    if not (return_shock >= -1.7976931348623157e308                   # noqa: F821
            and return_shock <= 1.7976931348623157e308):              # noqa: F821
        raise ValueError(f"point_id {point_id}: return_shock must be a finite number, "  # noqa: F821
                         f"not {float(return_shock)}")               # noqa: F821
    if not fund_return + return_shock > -1.0:                        # noqa: F821
        raise ValueError(
            f"point_id {point_id}: fund_return + return_shock, the trailing year's "  # noqa: F821
            f"return, must be above -1, not {float(fund_return + return_shock)}, under "  # noqa: F821
            f"fund_return {float(fund_return)} and return_shock "    # noqa: F821
            f"{float(return_shock)}")                                # noqa: F821
    if not (mort_be_factor >= 0.0                                    # noqa: F821
            and mort_be_factor <= 1.7976931348623157e308):            # noqa: F821
        raise ValueError(f"point_id {point_id}: mort_be_factor must be a finite number, "  # noqa: F821
                         f"0 or more, not {float(mort_be_factor)}")  # noqa: F821
    if not (wd_allowance_rate >= 0.0                                 # noqa: F821
            and wd_allowance_rate <= 1.7976931348623157e308):         # noqa: F821
        raise ValueError(f"point_id {point_id}: wd_allowance_rate must be a finite "  # noqa: F821
                         f"number, 0 or more, not {float(wd_allowance_rate)}")  # noqa: F821
    if not (allowance_years > -9007199254740992.0                     # noqa: F821
            and allowance_years < 9007199254740992.0                  # noqa: F821
            and allowance_years == allowance_years // 1):             # noqa: F821
        raise ValueError(f"point_id {point_id}: allowance_years must be a whole number "  # noqa: F821
                         f"below 2**53, not {float(allowance_years)}")  # noqa: F821
    if allowance_years < 0:                                          # noqa: F821
        raise ValueError(f"point_id {point_id}: allowance_years must be 0 or more, "  # noqa: F821
                         f"not {int(allowance_years)}")              # noqa: F821
    if not (depletion_threshold >= 0.0                               # noqa: F821
            and depletion_threshold <= 1.7976931348623157e308):       # noqa: F821
        raise ValueError(f"point_id {point_id}: depletion_threshold must be a finite "  # noqa: F821
                         f"number, 0 or more, not {float(depletion_threshold)}")  # noqa: F821
    if not (surr_rate_cap >= 0.0 and surr_rate_cap <= 1.0):          # noqa: F821
        raise ValueError(f"point_id {point_id}: surr_rate_cap must be a number from 0 "  # noqa: F821
                         f"to 1, not {float(surr_rate_cap)}")        # noqa: F821
    if not (wd_cap_rate >= 0.0 and wd_cap_rate <= 1.0):              # noqa: F821
        raise ValueError(f"point_id {point_id}: wd_cap_rate must be a number from 0 "  # noqa: F821
                         f"to 1, not {float(wd_cap_rate)}")          # noqa: F821
    if not (perf_factor_cap >= 0.0                                   # noqa: F821
            and perf_factor_cap <= 1.7976931348623157e308):           # noqa: F821
        raise ValueError(f"point_id {point_id}: perf_factor_cap must be a finite "  # noqa: F821
                         f"number, 0 or more, not {float(perf_factor_cap)}")  # noqa: F821
    if not (perf_factor_slope >= 0.0                                 # noqa: F821
            and perf_factor_slope <= 1.7976931348623157e308):         # noqa: F821
        raise ValueError(f"point_id {point_id}: perf_factor_slope must be a finite "  # noqa: F821
                         f"number, 0 or more, not {float(perf_factor_slope)}")  # noqa: F821
    if not (allow_step >= 0.0                                        # noqa: F821
            and allow_step <= 1.7976931348623157e308):                # noqa: F821
        raise ValueError(f"point_id {point_id}: allow_step must be a finite number, "  # noqa: F821
                         f"0 or more, not {float(allow_step)}")      # noqa: F821
    if av_pp_init() <= depletion_threshold:                          # noqa: F821
        if d > 0:
            raise ValueError(
                f"point_id {point_id}: av_pp_init is {av_pp_init()}, at or below "  # noqa: F821
                f"depletion_threshold, {float(depletion_threshold)}: a bond in force whose "  # noqa: F821
                f"fund is exhausted at the valuation date has nothing to project")
        raise ValueError(
            f"point_id {point_id}: av_pp_init, the fund at outset, is {av_pp_init()}, "  # noqa: F821
            f"at or below depletion_threshold, {float(depletion_threshold)}: the bond "  # noqa: F821
            f"holds nothing to project from its issue month")
    return min(horizon_mths(), fund_exhaust_mth()) - d


def fund_return_mth():
    """g_m = (1 + g)^(1/12) - 1: the monthly gross fund return **[std]**.

    Deterministic in the base run.  The insurer's margin is proportional to the unit
    fund, so the liability model inherits full market beta on the margin stream: a 20%
    market fall cuts the margin base by about a fifth and, through
    :func:`perf_factor`, raises surrender at the same time.  A flat Reference, the same on
    the valuation clock as on the policy clock: :func:`proj_len` refuses a ``fund_return``
    below -1, where this has no real value.
    """
    return (1.0 + fund_return) ** (1.0 / 12.0) - 1.0                 # noqa: F821


def amc_rate_mth():
    """c_m = c/12: the monthly annual management charge **[std 1/12 accrual]**."""
    return amc_rate() / 12.0


def further_costs_rate_mth():
    """f_m = f/12: the monthly further costs **[std 1/12 accrual]**."""
    return further_costs_rate() / 12.0


def mort_rate(t):
    """q_a: the annual best-estimate mortality rate at the attained age **[std]**.

    The shipped table rate times ``mort_be_factor``, a crude allowance for
    population mortality being heavier than insured-lives experience.  Nearly irrelevant
    to this product unless the guaranteed minimum death benefit rider is enabled.
    Capped at 1, the bound second, ``min(q, 1.0)``, so that a missing input, a NaN, stays
    NaN, where ``min(1.0, q)`` would read it as 1: :mod:`~.ULB_UK_S`'s cap, and no
    departure.  ``Data`` refuses a table rate that is not a number from 0 to 1, and
    :func:`proj_len` a ``mort_be_factor`` that is not a number, zero or more, so that the
    product is never below 0; above 1 the cap binds, and every policy in force at the
    start of the month dies in it.

    Zero outside cover, where ``age(t)`` is not an age the bond reaches.  Inside it, this
    is the one cell that reads ``Data.mort_table``, at ``min(age(t), omega_age)`` as
    :mod:`~.ULB_UK_S` reads it.  An age outside the table's, ``Data.mort_age_first`` to
    ``Data.mort_age_last``, raises ``ValueError``, naming the point and the age, where
    :mod:`~.ULB_UK_S`'s lookup raised ``KeyError``.
    """
    if not is_active(t):
        return 0.0
    x = min(age(t), omega_age)                                       # noqa: F821
    if x < data.mort_age_first() or x > data.mort_age_last():        # noqa: F821
        raise ValueError(f"point_id {point_id}: mort_table.csv has no rate at "  # noqa: F821
                         f"attained age {x}")
    return min(float(data.mort_table().loc[                          # noqa: F821
        (sex(), x), "mort_rate"]) * mort_be_factor, 1.0)             # noqa: F821


def mort_rate_mth(t):
    """q_m = 1 - (1 - q_a)^(1/12): the monthly mortality rate **[std]**."""
    return 1.0 - (1.0 - mort_rate(t)) ** (1.0 / 12.0)


def surr_rate_base(t):
    """w_base(y): the table annual full-surrender rate in month t **[std]**.

    2 / 3 / 5 / 8 / 10 percent by band, read at :func:`policy_year` ``(t)`` on the policy
    clock.  Policy years beyond the table take its last row, ``Data.surr_last_year``, as
    :mod:`~.ULB_UK_S`'s ``tbl.index.max()`` does.  Zero outside cover, where the month has
    no policy year: before issue :func:`policy_year` is 0 or less, where
    :mod:`~.ULB_UK_S`'s lookup raised ``KeyError``.
    """
    if not is_active(t):
        return 0.0
    y = policy_year(t)
    return float(data.surr_table().loc[                              # noqa: F821
        min(y, data.surr_last_year()), "surr_rate"])                 # noqa: F821


def return_12m(t):
    """R_12m: the trailing twelve-month gross fund return driving the lapse multiplier.

    ``fund_return + return_shock`` **[std]**.  The base run leaves the shock at zero, so
    the trailing return equals the reference and the multiplier is 1.  Keeping the shock
    separate from ``fund_return`` is deliberate: it moves the *behavioural* driver
    without disturbing the fund path, which is what makes the multiplier testable in
    isolation.  A stochastic or scenario projection would replace this with a path.  Two
    flat References, so the window reads no month before the valuation date.
    """
    return fund_return + return_shock                                # noqa: F821


def perf_factor(t):
    """M_perf(t) = min(2, 1 + 2 max(0, g_ref - R_12m)): the performance lapse multiplier.

    Poor recent performance raises surrender **[std]**; 1 in the deterministic base run.
    """
    shortfall = max(0.0, fund_return - return_12m(t))                # noqa: F821
    return min(perf_factor_cap, 1.0 + perf_factor_slope * shortfall)  # noqa: F821


def allow_factor(t):
    """M_allow(y): the allowance-exhaustion step, 1.5 from policy year 21 **[std]**.

    After twenty insurance years the cumulative 5% allowance is fully drawn under the
    anchor withdrawal pattern, and continued withdrawals then generate immediate
    excess-event gains - which pushes policyholders towards full surrender or
    advice-driven restructuring.  Read at the policy year on the policy clock, and 0
    outside cover, where the month has no policy year and no surrender.
    """
    if not is_active(t):
        return 0.0
    return allow_step if policy_year(t) > allowance_years else 1.0   # noqa: F821


def surr_rate(t):
    """w_ann: the annual full-surrender rate applied in month t.

    ``min(cap, w_base x M_perf x M_allow)``, in :mod:`~.ULB_UK_S`'s order: the bound on
    surrender is no cap on mortality.  A surrender costs the insurer nothing at the point
    of exit - the surrender value is the bid value of units, cancelled, with no penalty -
    but truncates the entire future charge stream, which is why persistency rather than
    mortality dominates this product's value.

    The rate is a probability.  ``Data`` holds the table's rates to 0 to 1, and
    :func:`proj_len` holds the cap to 0 to 1 and each multiplier to a finite number, 0 or
    more, so no frame reaches a rate outside 0 to 1: past 1 the monthly rate,
    ``1 - (1 - w)^(1/12)``, has no real value, which :mod:`~.ULB_UK_S` projects as a
    complex number, and below 0 the surrenders add policies.  The cell still refuses one,
    or one that is not a number, for a caller that reads it outside a frame: it raises
    ``ValueError`` in the month the rate first leaves, naming the point, the month, the
    rate and the References that make it.  A rate of exactly 1, the cap at 1 binding,
    surrenders every policy in force after the month's deaths.  0 outside cover.
    """
    w = min(surr_rate_cap,                                           # noqa: F821
            surr_rate_base(t) * perf_factor(t) * allow_factor(t))
    if not (w >= 0.0 and w <= 1.0):
        raise ValueError(
            f"point_id {point_id}: the surrender rate surr_rate({t}) is {w}, outside 0 "  # noqa: F821
            f"to 1, under surr_rate_cap {float(surr_rate_cap)}, perf_factor_cap "  # noqa: F821
            f"{float(perf_factor_cap)}, perf_factor_slope {float(perf_factor_slope)}, "  # noqa: F821
            f"return_shock {float(return_shock)} and allow_step "    # noqa: F821
            f"{float(allow_step)}")                                  # noqa: F821
    return w


def surr_rate_mth(t):
    """w_m = 1 - (1 - w_ann)^(1/12): the monthly surrender rate **[std]**."""
    return 1.0 - (1.0 - surr_rate(t)) ** (1.0 / 12.0)


def av_pp(t):
    """UF(t): the unit fund per policy at time t, the **start** of month t.

    The bid value of units, and the column the notes' worked-example table prints first.
    At :func:`t_entry` the fund the frame opens with, :func:`av_pp_init`: on a bond in
    force the fund at the valuation instant, history; on one not yet in force the fund at
    outset, its premium.  Then the end-of-month value of the previous month,
    ``UF(t) = UF'(t - 1) - W(t - 1) - AC(t - 1) - GC(t - 1)``, floored at zero:
    :func:`wd_pp` caps the withdrawal at what the fund can pay, so the fund is drawn to
    nothing rather than through it.

    Written here inline, the month before's growth, tax provision, charges and
    cancellations in :func:`av_pp_at`'s order and its floats, so that the chain of calls
    from month t back to :func:`t_entry` is one cell a month, the month before's fund read
    first: :mod:`~.ULB_UK_S` reads ``av_pp_at(t - 1, "AFT_WD")``, which runs through three
    timings to ``av_pp(t - 1)``, four cells a month.  ``av_pp_at(t, "AFT_WD")`` is this
    at ``t + 1``, bit for bit, in cover.  0 outside cover: before issue, and from the
    limiting age.
    """
    if not is_active(t):
        return 0.0
    if t == t_entry():
        return av_pp_init()
    uf = av_pp(t - 1)
    growth = fund_return_mth() * uf
    grown = uf + growth - tax_provision_rate() * growth
    charged = grown - amc_rate_mth() * grown - further_costs_rate_mth() * grown
    return max(0.0, charged - wd_pp(t - 1) - adviser_charge_pp(t - 1)
               - gmdb_charge_pp(t - 1))


def av_pp_at(t, timing):
    """The unit fund per policy at a point inside month t.

    ``"BEF_GROWTH"``
        UF(t), the start of the month; the same as :func:`av_pp`.

    ``"AFT_GROWTH"``
        UF_g(t), after the gross return and the tax provision taken in
        price.

    ``"AFT_CHARGE"``
        UF'(t), after the annual management charge and the further costs.
        **This is the base the AMC is levied on**, not ``UF(t)`` and not
        the post-withdrawal fund: the charge accrues daily through the
        unit price, so it sits on the post-growth, pre-cancellation fund.

    ``"AFT_WD"``
        UF(t+1), after the end-of-month unit cancellations - withdrawal,
        adviser charge and rider charge.  Equals ``av_pp(t + 1)`` in cover.

    All four points are exposed so that the charge ordering is inspectable rather than
    buried in one expression; charging on the wrong one moves the margin by about half a
    month's growth or withdrawal, which is small monthly and systematic over decades.
    Each reads :func:`av_pp` of its own month, which carries the chain; ``"AFT_WD"`` is
    computed here rather than read at ``t + 1``, so that the last month of cover, whose
    ``t + 1`` is past it, closes on its own fund.  0 outside cover, at every timing.

    ``"AFT_GROWTH"`` is where a fund that a ``fund_return`` past every amount of money
    grows first leaves the floats, and where it is refused, naming the month and
    ``fund_return``: past it ``inf - inf`` makes a NaN, which the floors of ``"AFT_WD"``
    and :func:`av_pp`, ``max(0, ...)``, would read as a fund drawn to nothing, and the
    threshold as exhaustion.  Every month :func:`av_pp` grows inline reads this timing of
    the month before, through :func:`wd_pp`, so the refusal holds for both.
    """
    if timing == "BEF_GROWTH":
        return av_pp(t)
    if timing == "AFT_GROWTH":
        grown = av_pp(t) + fund_growth_pp(t) - tax_provision_pp(t)
        if not grown <= 1.7976931348623157e308:
            raise ValueError(
                f"point_id {point_id}: the unit fund grown in month {t}, "  # noqa: F821
                f"av_pp_at({t}, 'AFT_GROWTH'), is {grown}, not a finite number, under "
                f"fund_return {float(fund_return)}")                 # noqa: F821
        return grown
    if timing == "AFT_CHARGE":
        return av_pp_at(t, "AFT_GROWTH") - amc_pp(t) - further_costs_pp(t)
    if timing == "AFT_WD":
        return max(0.0, av_pp_at(t, "AFT_CHARGE")
                   - wd_pp(t) - adviser_charge_pp(t) - gmdb_charge_pp(t))
    raise ValueError("invalid timing")


def av_per_segment_pp(t):
    """The unit fund per segment at the start of month t: the bond value over 100.

    Reported only.  A policyholder's tax outcome depends on whether whole segments are
    cashed or a part-surrender is taken across all of them, but the insurer's cash flow
    is identical either way - both cancel the same unit value.  ``Data`` holds the
    segments to a whole number, 1 or more.
    """
    return av_pp(t) / n_segments()


def fund_growth_pp(t):
    """G$(t) = g_m x UF(t): the gross fund return credited in month t; 0 outside cover."""
    return fund_return_mth() * av_pp(t)


def tax_provision_pp(t):
    """TX(t) = t_pf x G$(t): the tax provision taken in the unit price.

    A **pass-through**, not insurer income: it reduces the unit fund and is paid on as
    corporation tax.  On the anchor cell it is about 97% of the AMC, so counting it as
    margin roughly doubles the year-one non-unit result.
    """
    return tax_provision_rate() * fund_growth_pp(t)


def amc_pp(t):
    """AMC$(t) = c_m x UF_g(t): the annual management charge collected in month t.

    Levied on the post-growth, pre-cancellation fund, because it accrues daily through
    the unit price.  The insurer's only material income line on this product.
    """
    return amc_rate_mth() * av_pp_at(t, "AFT_GROWTH")


def further_costs_pp(t):
    """FC$(t) = f_m x UF_g(t): the fund-borne further costs in month t.

    A **pass-through**, not insurer income.
    """
    return further_costs_rate_mth() * av_pp_at(t, "AFT_GROWTH")


def wd_cap_pp(t):
    """The rolling twelve-month withdrawal cap: ``max(7.5% of UF, 7.5% of premium)``.

    The **product** cap, and the only thing that actually limits what can be withdrawn -
    the 5% tax allowance does not.  Measured against the fund after charges and against
    the premium, whichever is larger, and it includes the ongoing adviser charge.  A
    twelfth of it each month, so the window reads no withdrawal before the valuation
    date.  0 outside cover, where nothing can be withdrawn.
    """
    if not is_active(t):
        return 0.0
    return wd_cap_rate * max(                                        # noqa: F821
        av_pp_at(t, "AFT_CHARGE"), premium())


def wd_pp(t):
    """W(t): the regular withdrawal cancelled at the end of month t.

    ``wd_rate x P / 12``, then capped twice: by the product's rolling twelve-month limit
    - a twelfth of it each month, and **net of the ongoing adviser charge**, which counts
    against the same limit - and by what the fund can actually pay after the adviser and
    rider charges.  The second cap is what stops the fund going negative, and it is why
    the fund can close a month at exactly zero rather than through it, or on a rounding of
    either sign about it.  0 outside cover.
    """
    if not is_active(t):
        return 0.0
    scheduled = wd_rate() * premium() / 12.0
    ac = adviser_charge_pp(t)
    gc = gmdb_charge_pp(t)
    room = max(0.0, wd_cap_pp(t) / 12.0 - ac)
    available = max(0.0, av_pp_at(t, "AFT_CHARGE") - ac - gc)
    return min(scheduled, room, available)


def adviser_charge_pp(t):
    """AC(t): the ongoing adviser charge cancelled at the end of month t.

    ``oac_rate/12`` of the fund after charges.  A **pass-through**: it reduces the unit
    fund and consumes the policyholder's tax allowance, and it is not insurer income.
    0 outside cover, where the fund is.
    """
    return oac_rate() / 12.0 * av_pp_at(t, "AFT_CHARGE")


def gmdb_guarantee_pp(t):
    """G(t): the guaranteed minimum death benefit, if the rider is elected.

    ``premium - cumulative withdrawals - adviser charges``: a return-of-premium
    guarantee that erodes as the policyholder draws the fund down.  Zero without the
    rider, and outside cover.

    Measured **before** the current month's cancellations, at ``wd_cum_pp(t - 1)``:
    at :func:`t_entry`, the withdrawals and adviser charges since issue,
    :func:`wd_cum_pp_init`, history, so that a bond in force opens with what is left of
    its guarantee, and one not yet in force with nothing drawn.  That is the only reading
    that resolves: the rider charge is itself a cancellation alongside the withdrawal, so a
    guarantee net of the same month's withdrawal would make the charge depend on a
    withdrawal that depends on the charge.  Taking the start-of-month guarantee breaks the
    loop and matches the contractual sense, in which the amount guaranteed is what is on
    the record when the month begins.
    """
    if not gmdb_flag() or not is_active(t):
        return 0.0
    drawn = wd_cum_pp(t - 1) if t > t_entry() else wd_cum_pp_init()
    return max(0.0, premium() - drawn)


def gmdb_charge_pp(t):
    """GC(t): the rider charge cancelled at the end of month t **[std]**.

    ``q_m x max(0, G(t) - u UF'(t))``, a cost-of-insurance form on the in-the-money part
    of the guarantee.  The real charge scale is unpublished, so this is a guess with the
    right shape and no authority.  Insurer income, unlike the other cancellations.  0
    without the rider, and outside cover, before any rate is read.
    """
    if not gmdb_flag() or not is_active(t):
        return 0.0
    naar = max(0.0, gmdb_guarantee_pp(t)
               - db_uplift() * av_pp_at(t, "AFT_CHARGE"))
    return mort_rate_mth(t) * naar


def death_strain_pp(t):
    """DS(t): the **non-unit** cost per death in month t.

    ``(u - 1) UF(t+1) + max(0, G(t) - u UF(t+1)) 1{gmdb}``, on the end-of-month fund
    after the cancellations.  The sum assured is ``u x UF``, of which ``UF`` is funded by
    cancelling the policyholder's own units, so the insurer's cost is only the uplift - a
    tenth of a percent of the fund on the composite - plus any in-the-money guarantee.
    0 outside cover, where the fund and the guarantee are.
    """
    uf = av_pp_at(t, "AFT_WD")
    strain = (db_uplift() - 1.0) * uf
    if gmdb_flag():
        strain += max(0.0, gmdb_guarantee_pp(t) - db_uplift() * uf)
    return strain


def wd_cum_pp(t):
    """CumWD: cumulative withdrawals and adviser charges to the end of month t.

    The allowance-relevant total: ongoing and ad hoc adviser charges consume the same 5%
    tax allowance as withdrawals do.  At :func:`t_entry` the total entering month 0,
    :func:`wd_cum_pp_init`, history, 0 on a bond not yet in force, and the month's
    cancellations; then the running sum.  **Never restarted**: it counts from issue, as
    the allowance it is measured against does.  0 outside cover.
    """
    if not is_active(t):
        return 0.0
    prior = wd_cum_pp(t - 1) if t > t_entry() else wd_cum_pp_init()
    return prior + wd_pp(t) + adviser_charge_pp(t)


def allowance_cum_pp(t):
    """CumAllow: the cumulative 5% allowable element, ``P x min(y, 20) x 5%`` from issue.

    **Policyholder tax machinery, not a product feature.**  It never caps what can be
    withdrawn - the product cap is :func:`wd_cap_pp` - and it generates no insurer cash
    flow.  It is carried because it drives behaviour through :func:`allow_factor`.

    Each policy year's allowable element accrues at its start, ``wd_allowance_rate`` of
    the premium for each of the first ``allowance_years``.  On a bond in force the years
    to the one month -1 falls in, ``y0 = (d - 1) // 12 + 1`` for ``d`` the policy months
    at the valuation date, are history, :func:`allowance_cum_pp_init`, and each later
    year accrues at the Reference, an anniversary's in month 0 among them:
    ``CumAllow(t) = CumAllow_0 + P x (min(y, n) - min(y0, n)) x r``, ``n`` the years and
    ``r`` the rate.  A bond not yet in force has accrued nothing, ``y0 = 0``, and its
    allowance is :mod:`~.ULB_UK_S`'s closed form from issue, the same float.  An allowance
    that is not a finite number, which only a rate past every amount of money makes, is
    refused in the month it first is, naming the References, where :func:`excess_gain_pp`
    would floor it to no gain.  0 outside cover, where the policy year is 0 or less.
    """
    if not is_active(t):
        return 0.0
    y = policy_year(t)
    y0 = (duration_mth_init() - 1) // 12 + 1 if duration_mth_init() > 0 else 0
    later = min(y, allowance_years) - min(y0, allowance_years)          # noqa: F821
    allowed = allowance_cum_pp_init() + premium() * later * wd_allowance_rate  # noqa: F821
    if not allowed <= 1.7976931348623157e308:
        raise ValueError(
            f"point_id {point_id}: the allowance allowance_cum_pp({t}) is {allowed}, not "  # noqa: F821
            f"a finite number, under wd_allowance_rate {float(wd_allowance_rate)} and "  # noqa: F821
            f"allowance_years {int(allowance_years)}")               # noqa: F821
    return allowed


def excess_gain_pp(t):
    """ExcessGain: the excess-event gain at the insurance-year end, if any.

    ``max(0, CumWD - CumAllow)``, cumulative rather than per-year, so the running total
    is the gain reported to date.  **No insurer cash flow**: chargeable events are
    settled between the policyholder and HMRC, with the insurer issuing certificates.
    """
    return max(0.0, wd_cum_pp(t) - allowance_cum_pp(t))


def pols_if(t):
    """l(t): the number of policies in force at time t, the count that weights row t.

    ``pols_if_at(t, "BEF_DECR")``: the count carried in from month t - 1, plus month t's
    new business, before month t's decrements. On a point issued at ``t = 0`` that is
    exactly :mod:`~.ULB_UK_S`'s ``pols_if``, the notes' ``l(t)``, which follows the
    recursion ``l(t+1) = l(t)(1 - q_m(t))(1 - w_m(t))``, deaths before surrenders
    **[std]**.  It is ``basiclife.BasicTerm_SE``'s ``BEF_DECR`` count, not its ``pols_if``.
    Zero outside the frame, so ``pols_if(proj_len())`` is the count after the last
    projected month: nothing, because :func:`pols_maturity` takes the survivors.
    """
    return pols_if_at(t, "BEF_DECR")


def pols_if_at(t, timing):
    """The number of policies in force at a point inside month t.

    ``"BEF_NB"``
        The count carried in from month t - 1, before month t's new business: the
        survivors of month t - 1's deaths and surrenders, out of month t - 1's
        ``"BEF_DECR"`` count. At :func:`t_entry`, the first month on the books, it is
        :func:`pols_if_init`, the count in force at the valuation date (0 for a point
        issued at or after it), and the recursion reads no earlier month. Zero outside
        the frame, from ``t = proj_len()`` on, so the survivors of the frame's last month
        leave as :func:`pols_maturity`.

    ``"BEF_DECR"``
        ``"BEF_NB"`` plus :func:`pols_new_biz`: l(t), the count that weights month t,
        which :func:`pols_if` returns.

    ``"BEF_SURR"``
        after deaths, before surrenders - the processing order is **death
        before surrender** **[std]**.

    ``"AFT_DECR"``
        the notes' ``l(t+1)``, the end-of-month count, and zero in the frame's last
        month ``t = proj_len() - 1``.  It is ``"BEF_NB"`` at t + 1 exactly, one product in
        one order.

    ``"BEF_NB"`` is the one timing running in force adds, as ``basiclife.BasicTerm_SE``
    names it; the other three are :mod:`~.ULB_UK_S`'s, and any other raises.
    ``"BEF_NB"`` forms month t - 1's ``"BEF_DECR"`` count itself, as ``"BEF_NB"`` plus
    :func:`pols_new_biz` at t - 1, the same sum in the same order, rather than calling for
    it. So the chain of calls from month t back to :func:`t_entry` is one cell a month,
    where :mod:`~.ULB_UK_S`'s ``pols_if`` chain runs three. Each count is zero outside the
    frame before it reads a rate.
    """
    if timing == "BEF_NB":
        if not is_active(t) or t >= proj_len():
            return 0.0
        if t == t_entry():
            return pols_if_init()
        return ((pols_if_at(t - 1, "BEF_NB") + pols_new_biz(t - 1))
                * (1.0 - mort_rate_mth(t - 1)) * (1.0 - surr_rate_mth(t - 1)))
    if timing == "BEF_DECR":
        return pols_if_at(t, "BEF_NB") + pols_new_biz(t)
    if timing == "BEF_SURR":
        if not is_active(t) or t >= proj_len():
            return 0.0
        return pols_if(t) * (1.0 - mort_rate_mth(t))
    if timing == "AFT_DECR":
        if not is_active(t) or t >= proj_len() - 1:
            return 0.0
        return pols_if_at(t, "BEF_SURR") * (1.0 - surr_rate_mth(t))
    raise ValueError("invalid timing")


def pols_new_biz(t):
    """The number of policies issued in month t: ``policy_count()`` in the issue month.

    The issue month is the one with ``duration_mth(t) == 0``: ``t = 0`` for a point
    issued at the valuation date, ``t = k`` for one issued ``k`` months later. A point
    already in force at the valuation date has none.
    """
    return policy_count() if duration_mth(t) == 0 else 0.0


def pols_death(t):
    """Deaths in month t, against the start-of-month count; zero outside the frame,
    before any rate is read."""
    if not is_active(t) or t >= proj_len():
        return 0.0
    return pols_if(t) * mort_rate_mth(t)


def pols_surr(t):
    """Full surrenders at the end of month t, from the survivors of mortality; zero
    outside the frame, before any rate is read."""
    if not is_active(t) or t >= proj_len():
        return 0.0
    return pols_if_at(t, "BEF_SURR") * surr_rate_mth(t)


def pols_maturity(t):
    """Policies still in force when the frame ends; zero in every other month.

    A bond has no maturity date, so this is either the population left at the limiting
    age or - on the base run - the population still holding a bond whose fund has just
    been drawn to nothing.  It pays nothing, and it exists so the roll-forward closes in
    the frame's last month, ``t = proj_len() - 1``.
    """
    if t != proj_len() - 1:
        return 0.0
    return pols_if(t) - pols_death(t) - pols_surr(t)


def claims(t, kind=None):
    """Gross benefit outgo in month t, by kind; the total when kind is omitted.

    ``"DEATH"``
        ``u x UF(t+1)`` per death - the full sum assured on the end-of-month
        fund, of which all but the uplift is funded by cancelling the
        policyholder's own units - or the guaranteed amount where the rider
        is elected and in the money, ``max(u x UF(t+1), G(t))``.

    ``"SURRENDER"``
        ``UF(t+1)`` per surrender: the bid value of units, with no penalty.

    These are **gross** flows.  They are published so the reader can see the whole
    picture, but they are not in :func:`net_cf`, because :func:`unit_releases` cancels
    them against the fund - all except the death strain.  See the Space docstring.
    """
    if kind is None:
        return sum(claims(t, k) for k in ("DEATH", "SURRENDER"))
    uf = av_pp_at(t, "AFT_WD")
    if kind == "DEATH":
        benefit = db_uplift() * uf
        if gmdb_flag():
            benefit = max(benefit, gmdb_guarantee_pp(t))
        return benefit * pols_death(t)
    if kind == "SURRENDER":
        return uf * pols_surr(t)
    raise ValueError("invalid kind")


def withdrawals(t):
    """Withdrawal and adviser-charge outgo in month t, funded by cancelling units.

    An owner election rather than a claim, which is why it has its own name and its own
    ``result_cf`` column.
    """
    return (wd_pp(t) + adviser_charge_pp(t)) * pols_if(t)


def unit_releases(t):
    """The unit fund cancelled to fund the month's death and surrender benefits.

    ``UF(t+1) x (deaths + surrenders)``, on the end-of-month fund.  The gross benefit
    outgo less this is exactly the death strain, which is the only part the insurer funds
    from its own resources.
    """
    return av_pp_at(t, "AFT_WD") * (pols_death(t) + pols_surr(t))


def amc_charges(t):
    """The annual management charge collected in month t; **insurer income**."""
    return amc_pp(t) * pols_if(t)


def gmdb_charges(t):
    """The rider charge collected in month t; **insurer income**, zero in the base run."""
    return gmdb_charge_pp(t) * pols_if(t)


def further_costs(t):
    """The fund-borne further costs in month t; a **pass-through**, not income.

    Published as its own column so that its exclusion from :func:`net_cf` is visible
    rather than merely asserted.
    """
    return further_costs_pp(t) * pols_if(t)


def tax_provisions(t):
    """The tax provision taken in the unit price in month t; a **pass-through**.

    About 97% of the annual management charge on the anchor cell, which is the measure of
    how badly counting it as margin would mislead.
    """
    return tax_provision_pp(t) * pols_if(t)


def death_strain(t):
    """The non-unit cost of the month's deaths: the uplift, plus any in-the-money GMDB."""
    return death_strain_pp(t) * pols_death(t)


def inflation_factor(t):
    """The expense inflation factor in month t, ``(1 + pi)^(t // 12)`` **[std]**.

    On the **valuation** clock: ``t`` counts months from the valuation date, so the
    maintenance charge it inflates is in valuation-date pounds, whatever the bond's age,
    and every point of a block inflates alike, stepping on each anniversary of the
    valuation date.  :mod:`~.ULB_UK_S` inflates from issue, ``(1 + pi)^duration(t)``, the
    notes' ``(1 + pi)^(y - 1)``; on a point issued at ``t = 0`` the two are the same.
    Acquisition is not inflated (see :func:`expenses`).
    """
    return (1.0 + inflation_rate) ** (t // 12)                       # noqa: F821


def expenses(t):
    """Acquisition and maintenance expense in month t **[std]**.

    £300 per policy issued, ``expense_acq * pols_new_biz(t)``: in the issue month, never
    for a bond already in force at the valuation date, and not inflated, as in
    ``basiclife.BasicTerm_SE``.  :mod:`~.ULB_UK_S` charges it on the count at ``t = 0``,
    which on a point issued then is the count issued.  Then £60 per policy a year - a
    twelfth of it each month - inflating at 2.5% on the valuation clock.  The margin is
    proportional to the fund while the expense inflates, so a small-fund cell goes
    margin-negative late in life - which the anchor cell does, as its fund is drawn down.
    """
    return (expense_acq * pols_new_biz(t)                            # noqa: F821
            + expense_maint / 12.0 * inflation_factor(t) * pols_if(t))  # noqa: F821


def net_cf(t):
    """NUCF(t): the **non-unit** cash flow of month t, income positive.

    ``AMC + rider charge - expenses - death strain``.  Not a gross liability total, and
    that is a product fact rather than a departure: every benefit is funded by cancelling
    the policyholder's own units, so a gross presentation would add the same money to
    both sides.  The tax provision, the further costs and the adviser charges are
    excluded because they are pass-throughs - the notes' second-listed pitfall is
    counting them as margin.

    The result is a fund-based margin stream: proportional to the unit fund and to
    persistency, with mortality contributing about a tenth of a percent of the fund times
    the mortality rate.  Behaviour, not mortality, dominates the value.
    """
    return amc_charges(t) + gmdb_charges(t) - expenses(t) - death_strain(t)


def check_av_roll_fwd_resid(t):
    """The unit fund roll-forward residual in month t; zero everywhere.

    ``UF(t+1) - [UF(t) + growth - tax - AMC - further costs - W - AC - GC]``, per policy.
    This is the identity the charge ordering has to satisfy, and it is checked rather
    than assumed because the ordering is the model's most consequential convention.
    Skipped once the fund has been drawn to nothing, where the withdrawal cap breaks the
    equality by design: :mod:`~.ULB_UK_S`'s test of 0, which is the floor's, not the
    exhaustion's.
    """
    uf_end = av_pp_at(t, "AFT_WD")
    if uf_end <= 0.0:
        return 0.0
    built = (av_pp(t) + fund_growth_pp(t) - tax_provision_pp(t)
             - amc_pp(t) - further_costs_pp(t)
             - wd_pp(t) - adviser_charge_pp(t) - gmdb_charge_pp(t))
    return uf_end - built


def check_av_roll_fwd():
    """True when the unit fund roll-forward closes in every projected month.

    The library-wide form of a roll-forward check: no argument, one bool over all t, so
    one test can call the same check across every account-value model in the library.
    """
    return all(abs(check_av_roll_fwd_resid(t)) <= 1e-8
               for t in range(proj_len()))


def check_pols_roll_fwd_resid(t):
    """The in-force roll-forward residual in month t; zero everywhere.

    ``pols_if(t) - pols_if_at(t + 1, "BEF_NB") - deaths - surrenders - the frame's last
    month's survivors``, where the count carried into the next month is taken before its
    new business, which is no part of month t's movement.
    """
    return (pols_if(t) - pols_if_at(t + 1, "BEF_NB")
            - pols_death(t) - pols_surr(t) - pols_maturity(t))


def check_pols_roll_fwd():
    """True when the in-force roll-forward closes in every month of the frame.

    The tolerance scales with ``policy_count()``, since the residual accumulates rounding
    on that many policies, in force at the valuation date or issued after it.
    """
    return all(abs(check_pols_roll_fwd_resid(t)) <= 1e-10 * max(policy_count(), 1.0)
               for t in range(proj_len()))


def check_unit_funding_resid(t):
    """How much of the month's benefit outgo the unit fund does **not** fund.

    ``claims(t) - unit_releases(t) - death_strain(t)``, which is zero: the death benefit
    is the unit fund plus the uplift, the surrender benefit is the unit fund exactly, and
    the uplift is precisely the death strain.  A model that funded benefits twice - once
    from the fund and once from the insurer - would show it here.
    """
    return claims(t) - unit_releases(t) - death_strain(t)


def check_unit_funding():
    """True when every benefit is funded by unit cancellation plus the death strain."""
    return all(abs(check_unit_funding_resid(t)) <= 1e-8
               for t in range(proj_len()))


def result_cf():
    """Result table of cashflows, one row per month ``t = 0 .. proj_len() - 1``.

    Row 0 is the valuation month for every model point, so the frames of a block line up
    and sum row by row.  A point issued after the valuation date has zeros until its issue
    month.  ``av_pp`` is the unit fund at the start of the month, and ``pols_if`` the
    in-force count that weights every flow on the row.  ``net_cf`` is the **non-unit**
    stream - what accrues to the insurer - while ``claims_death``, ``claims_surrender``,
    ``withdrawals`` and ``unit_releases`` show the gross picture they net against.
    ``further_costs`` and ``tax_provisions`` are published precisely because they are
    **not** in ``net_cf``: they leave the unit fund and are paid on.  The columns are
    :mod:`~.ULB_UK_S`'s.
    """
    ts = list(range(proj_len()))
    return pd.DataFrame(                                             # noqa: F821
        {
            "pols_if": [pols_if(t) for t in ts],
            "av_pp": [av_pp(t) for t in ts],
            "amc_charges": [amc_charges(t) for t in ts],
            "gmdb_charges": [gmdb_charges(t) for t in ts],
            "further_costs": [further_costs(t) for t in ts],
            "tax_provisions": [tax_provisions(t) for t in ts],
            "withdrawals": [withdrawals(t) for t in ts],
            "claims_death": [claims(t, "DEATH") for t in ts],
            "claims_surrender": [claims(t, "SURRENDER") for t in ts],
            "unit_releases": [unit_releases(t) for t in ts],
            "death_strain": [death_strain(t) for t in ts],
            "expenses": [expenses(t) for t in ts],
            "net_cf": [net_cf(t) for t in ts],
        },
        index=pd.Index(ts, name="t"),                                # noqa: F821
    )


def result_uf():
    """Result table of the unit fund recursion, one row per month t of the frame.

    The same rows as :func:`result_cf`, ``t = 0 .. proj_len() - 1``, each per policy.
    The notes' worked-example table, column for column: the fund at the start of the
    month (``UF(t)``), the gross return, the tax provision, the charges, the withdrawal,
    and the fund at the end (``UF(t+1)``, as ``av_pp_end``).  A point issued after the
    valuation date has zeros until its issue month.
    """
    ts = list(range(proj_len()))
    return pd.DataFrame(                                             # noqa: F821
        {
            "av_pp": [av_pp(t) for t in ts],
            "fund_growth_pp": [fund_growth_pp(t) for t in ts],
            "tax_provision_pp": [tax_provision_pp(t) for t in ts],
            "amc_pp": [amc_pp(t) for t in ts],
            "further_costs_pp": [further_costs_pp(t) for t in ts],
            "adviser_charge_pp": [adviser_charge_pp(t) for t in ts],
            "gmdb_charge_pp": [gmdb_charge_pp(t) for t in ts],
            "wd_pp": [wd_pp(t) for t in ts],
            "av_pp_end": [av_pp_at(t, "AFT_WD") for t in ts],
            "wd_cum_pp": [wd_cum_pp(t) for t in ts],
            "allowance_cum_pp": [allowance_cum_pp(t) for t in ts],
            "excess_gain_pp": [excess_gain_pp(t) for t in ts],
        },
        index=pd.Index(ts, name="t"),                                # noqa: F821
    )


def result_pols():
    """Result table of policy counts, one row per month t of the frame.

    The same rows as :func:`result_cf`, ``t = 0 .. proj_len() - 1``: the counts
    :func:`result_cf` weights its rows by, and how they move, as
    ``basiclife.BasicTerm_SE``'s ``result_pols`` sets them out: ``pols_if``, the count of
    month t; ``pols_new_biz``, the part of it issued in month t; then month t's deaths
    and surrenders in processing order, and the survivors of the frame's last month.  Row
    by row, ``pols_if`` at ``t + 1`` is ``pols_if`` less the three outflows of month t,
    plus the new business of month ``t + 1``.
    """
    ts = list(range(proj_len()))
    return pd.DataFrame(                                             # noqa: F821
        {
            "pols_if": [pols_if(t) for t in ts],
            "pols_new_biz": [pols_new_biz(t) for t in ts],
            "pols_death": [pols_death(t) for t in ts],
            "pols_surr": [pols_surr(t) for t in ts],
            "pols_maturity": [pols_maturity(t) for t in ts],
        },
        index=pd.Index(ts, name="t"),                                # noqa: F821
    )


# ---------------------------------------------------------------------------
# References

data = ("Interface", ("..", "Data"), "auto")

point_id = 1

issue_age_min = 18

omega_age = 120

depletion_threshold = 0.005

mort_be_factor = 0.8

fund_return = 0.05

return_shock = 0.0

perf_factor_slope = 2.0

perf_factor_cap = 2.0

surr_rate_cap = 0.35

allow_step = 1.5

allowance_years = 20

wd_allowance_rate = 0.05

wd_cap_rate = 0.075

expense_acq = 300.0

expense_maint = 60.0

inflation_rate = 0.025

pd = ("Module", "pandas")
