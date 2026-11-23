# modelx: pseudo-python
# This file is part of a modelx model.
# It can be imported as a Python module, but functions defined herein
# are model formulas and may not be executable as standard Python.

"""The by-policy projection of the :mod:`~.IP_UK_SEC` model; holds all formulas.

The Space is parameterized by ``point_id``, so ``Projection[1]`` is an ItemSpace
projecting model point 1, the twin of :mod:`~.IP_UK_S`'s active-lives anchor cell, issued
at the valuation date::

    >>> Projection[1].result_cf()          # one row per month from the valuation date
    >>> Projection[1].result_pols()        # the counts behind it, healthy and in claim
    >>> Projection.point_id = 2            # the twin of the claims-in-payment cell

This is :mod:`~.IP_UK_S` taught to run in force at a valuation date, as lifelib's
``basiclife.BasicTerm_SE`` extends ``basiclife.BasicTerm_S``. A formula of
:mod:`~.IP_UK_S` is rewritten where it depends on where the projection starts, where it
must answer for a month outside cover, or where it read a policy month as ``t``; every
other formula is :mod:`~.IP_UK_S`'s own, the caps on mortality and inception,
``min(q, 1.0)``, among them. ``products/income_protection/model-sec.md`` lists the
rewritten cells with the reason for each.

.. rubric:: Input data

Inputs are **external files**: plain CSVs living in the model folder's parent
directory, ``products/income_protection/``, read at run time rather than stored inside
the model. The model folder therefore holds nothing but formulas — no ``_data/``, no
IOSpec, no embedded values — so a diff of the model shows logic changes only, and an
input can be edited or swapped without rewriting the model. This follows
``annuallife.TradLife_A``; contrast ``basiclife.BasicTerm_S``, which keeps its inputs
*inside* the model through modelx's IOSpec machinery.

The consequence worth knowing: **the model is not portable on its own.** Copying the
``IP_UK_SEC`` folder without its parent's CSVs produces a model that reads and then fails
on first evaluation.

The four assumption tables are the files :mod:`~.IP_UK_S` reads, read in place; the model
point table and the claim cohorts are this model's own. Each table has a filename
Reference and a reader Cells, both on :mod:`~.IP_UK_SEC.Data`, reached here through the
``data`` Reference:

======================  ==============================  ==========================
Reference               Cells                           File
======================  ==============================  ==========================
model_point_file        data.model_point_table()        model_point_table_sec.csv
inforce_cohorts_file    data.inforce_cohorts()          inforce_cohorts_sec.csv
inception_file          data.inception_table()          inception_table.csv
termination_file        data.termination_table()        termination_table.csv
mort_table_file         data.mort_table()               mort_table.csv
lapse_table_file        data.lapse_table()              lapse_table.csv
======================  ==============================  ==========================

.. rubric:: Two clocks

``t`` counts months from the **valuation date**, 0-based, the clock
``basiclife.BasicTerm_SE`` runs on: ``t = 0`` is the valuation month for every model
point, however old the policy, month ``t`` runs from time ``t`` to time ``t + 1``, and the
frame is ``t = 0 .. proj_len() - 1``, where :func:`proj_len` counts the months from the
valuation date to the policy end date. Row ``t`` is the same month for every point, so
the frames of a block line up and sum row by row. Premiums fall at the start of month
``t``, and transitions and the benefit at its end.

``duration_mth(t)`` counts **policy months**, the months the policy has been in force at
time ``t``: ``duration_mth(t) = duration_mth_init() + t``, where
:func:`duration_mth_init` is read from the model point — positive for a policy in force
at the valuation date, 0 for one issued at it, ``-k`` for one issued ``k`` months later,
at most ten years later. Everything contractual reads it: the completed policy years
``duration(t) = duration_mth(t) // 12``, the contractual 1-based label
``policy_year(t) = duration(t) + 1``, the lapse table's key and the escalation's
anniversaries, the attained age ``age(t) = age_at_entry() + duration(t)``, the inception
and mortality tables' key, and the policy end date, :func:`expiry_mth`. Model point 9, the
anchor cell valued 60 months after issue, is in policy year 6 at attained age 40 at
``t = 0``, with 300 months to the policy end date.

The claim duration ``z`` is a third clock, a separate 1-based cohort index on which only
the termination rates are read, and is not a time index: cohort ``z`` at the start of month
``t`` holds the claims that incepted at the end of month ``t - z``.

Two inputs read the valuation clock instead, for every point alike: expense inflation,
``inflation_factor(t) = (1 + inflation_rate) ** (t // 12)``, so that the expense loads are
in valuation-date pounds, and the discount factor, ``disc_factor(t)``, to the end of month
``t`` from the valuation date, as :mod:`~.IP_UK_S` already discounts. RPI is a flat
Reference, the rate assumed from the valuation date on, and ``cycle_factor`` a flat
scenario overlay on the rates, from the valuation date on.

On a point issued at ``t = 0`` the two clocks coincide and this model computes what
:mod:`~.IP_UK_S` computes: every cell the two share agrees at every argument
:mod:`~.IP_UK_S` evaluates in its sweep, but for those whose meaning changed —
``pols_if_init``, now the count already in force at the valuation date, and
``model_point``, a row of another table. ``tests/test_model_conventions_uk.py`` asserts it
cell by cell.

.. rubric:: Counts

``pols_if(t)`` is the count that weights row ``t``, the healthy lives and those in claim
together, :func:`pols_active` plus :func:`pols_sick`: ``pols_if_at(t, "BEF_DECR")``, the
count carried in from ``t - 1`` (``"BEF_NB"``) plus the month's new business,
:func:`pols_new_biz`, before the month's transitions. New business enters healthy, in its
issue month, and only on an empty book, so ``"BEF_NB"`` is ``pols_if(t)`` less
:func:`pols_new_biz` exactly. A point in force at the valuation date opens with
:func:`pols_if_init`, its ``policy_count``, split between the states by its opening state;
one issued at or after the valuation date opens with none, and takes its ``policy_count``
into state H as new business in its issue month. Each recursion's base is :func:`t_entry`,
the first month on the books, and nothing is counted outside cover (:func:`is_active`):
before issue every count, and so every cash flow, is zero. :mod:`~.IP_UK_S`'s two timings
are kept, ``"BEF_DECR"`` and ``"AFT_DECR"``, and ``"BEF_NB"`` is the one running in force
adds.

.. rubric:: The opening state

A point in force carries, beside its count, the facts of its contract that
:mod:`~.IP_UK_S` carries into the month it is valued at, each measured at the valuation
instant, the start of month 0, before any month-0 event, recoveries of month -1 already
returned to health:

* :func:`pols_active_init`, the healthy share of the count, the lives in state H;
* the claim cohorts, :func:`pols_sick_dur_init`, the share of the count in claim payment at
  each claim duration ``z``, cohort 1 holding the claims that incepted at the end of month
  -1, which are paid from the end of month 0. A point's vector is as long as its months in
  force, and it is read from a sparse companion, ``inforce_cohorts_sec.csv``, keyed
  ``(point_id, z)``: a claim duration it holds no row for holds no lives;
* :func:`benefit_pp_init` and :func:`premium_pp_init`, the monthly benefit and premium
  entering month 0, after every escalation already given, :mod:`~.IP_UK_S`'s
  ``benefit_pp`` and ``premium_pp`` of month -1. On a point valued on an anniversary they
  are the year it closes: the anniversary's escalation is the projection's first event,
  at today's References. The benefit escalates on policy anniversaries for the lives in
  health and in claim alike, so no cohort carries an amount of its own.

Each is history, read from the model point and the companion, never recomputed from a
Reference, which is an assumption from the valuation date on: an RPI, a cycle overlay or a
termination basis changed at the valuation date reaches back over no escalation, no
inception and no recovery already made. The shares are count-free, so ``policy_count`` is
the one weight on the flows; with the cohorts they sum to 1, which ``Data`` checks.

.. rubric:: Naming

Cells names follow lifelib's ``basiclife.BasicTerm_S`` and ``savings.CashValue_SE``
wherever those models have an analogue — ``pols_*`` for population counts, plural nouns
for cash flows, ``*_rate`` for annual rates and ``*_rate_mth`` for monthly ones,
``*_pp`` for per-policy amounts, ``claims(t, kind)`` with an uppercase ``kind`` string.
What running in force adds is named as ``basiclife.BasicTerm_SE`` names it:
``duration_mth`` read from the model point, ``policy_count``, ``pols_new_biz``,
``pols_if_at``'s ``"BEF_NB"`` timing, ``is_active`` and ``result_pols``.
``duration_mth_init``, the policy months completed at the valuation date, takes
``UL_US_S``'s name; ``t_entry`` and ``expiry_mth`` are this model's own, and each
opening-state cell is the cell it opens with ``_init`` added. The technical notes use
compact actuarial symbols instead. The mapping is:

=========================  ==============================  ==========================
Notes symbol               Cells                           Meaning
=========================  ==============================  ==========================
entry_age                  age_at_entry()                  Entry age (ANB), at issue
a                          age(t)                          Attained age (ANB) in month t
y                          policy_year(t)                  Policy year containing month t
(none)                     duration(t)                     Completed policy years
(none)                     duration_mth(t)                 Policy months at month t
(none)                     duration_mth_init()             Policy months at t = 0
(none)                     duration_init()                 Policy years the amounts hold
(none)                     t_entry()                       First month on the books
(none)                     is_active(t)                    Whether month t is in cover
expiry_age                 expiry_age()                    Age all cover ceases
(none)                     expiry_mth()                    Policy month cover ends
(none)                     proj_len()                      Months to the policy end date
(none)                     policy_count()                  Policies the point stands for
d                          deferred_weeks()                Deferred period in weeks
occ_class                  occ_class()                     CMI occupation class OC1-OC4
status                     status()                        S's label: active or in_claim
z                          (the duration argument)         Claim duration in months
(none)                     claim_dur_year(z)               Duration year containing z
(none)                     max_dur()                       Longest claim duration tracked
B(1)                       benefit_mth()                   Monthly benefit at issue
B(y)                       benefit_pp(t)                   Escalated monthly benefit
(B at t = 0)               benefit_pp_init()               Benefit before month 0
P(1)                       premium_mth()                   Monthly premium at issue
P(y)                       premium_pp(t)                   Escalated monthly premium
(P at t = 0)               premium_pp_init()               Premium before month 0
AP(y)                      amount_payable_pp(t)            Amount payable per month
(max benefit formula)      benefit_max_pp()                Contractual maximum benefit
k                          claim_severity                  Severity factor, 1.0
AP/B                       ap_ratio                        Offset/guarantee effect, 1.0
j                          esc_rate()                      Escalation rate
M_esc(y)                   esc_lapse_factor(t)             Premium-shock lapse multiplier
iota_a(a)                  inception_rate(t)               Annual claim inception rate
iota_m(a)                  inception_rate_mth(t)           The same, monthly
M_cycle                    cycle_factor                    Economic-cycle overlay, 1.0
q_H_a(a)                   mort_rate(t)                    Active-life annual mortality
q_H_m(a)                   mort_rate_mth(t)                The same, monthly
w_a(y)                     lapse_rate(t)                   Annual lapse rate in month t
(table)                    lapse_rate_base(t)              Table lapse rate before shock
w_m(y)                     lapse_rate_mth(t)               Monthly lapse rate
rho_a(z)                   rec_rate(z)                     Annual recovery rate
rho_m(z)                   rec_rate_mth(z)                 Monthly recovery rate
q_S_a(z)                   mort_rate_sick(z)               Annual in-claim mortality
q_S_m(z)                   mort_rate_sick_mth(z)           Monthly in-claim mortality
s_S(z)                     claim_surv_step(z)              Monthly in-claim survival
(the three vectors)        claim_rate_vectors()            rho_m, q_S_m and s_S as tuples
l_H(t)                     pols_active(t)                  In state H at start of month t
(l_H(0) / l(0))            pols_active_init()              Healthy share at t = 0
l_S(t, z)                  pols_sick_dur(t, z)             In claim at duration z
(l_S(0, z) / l(0))         pols_sick_dur_init(z)           Share in claim at z, t = 0
l_S(t)                     pols_sick(t)                    Total in claim payment
(the whole vector)         sick_cohorts(t)                 l_S(t, .) as a tuple
(none)                     pols_if(t)                      H + S: policies in force
(none)                     pols_if_init()                  In force at t = 0
(none)                     pols_new_biz(t)                 Policies issued in month t
(none)                     pols_if_at(t, timing)           BEF_NB / BEF_DECR / AFT_DECR
n(t)                       pols_inception(t)               New claim inceptions
rec(t)                     pols_recovery(t)                Recoveries out of S
dth_S(t)                   pols_death_sick(t)              Deaths in claim
dth_H(t)                   pols_death_active(t)            Deaths in state H
lps(t)                     pols_lapse(t)                   Lapses out of H
(none)                     pols_exit(t)                    Recoveries leaving the model
(none)                     pols_maturity(t)                In force at the policy end date
(none)                     pols_sick_surv(t)               In claim at the end of month t
(none)                     pols_dead_cum(t)                Deaths since t_entry()
(none)                     pols_lapse_cum(t)               Lapses since t_entry()
(none)                     pols_exit_cum(t)                Exits since t_entry()
PREM(t)                    premiums(t)                     Premium income
BEN(t)                     claims(t, "BENEFIT")            Income benefit outgo
0                          claims(t, "DEATH")              Death benefit; always zero
0                          claims(t, "LAPSE")              Surrender outgo; always zero
EXP(t)                     expenses(t)                     Maintenance + claim management
e_m(y), ec_m(y)            expense_maint, expense_claim    Expense levels p.a.
(none)                     inflation_factor(t)             Inflation, valuation clock
CF(t)                      net_cf(t)                       Net cash flow, income positive
v(t)                       disc_factor(t)                  Discount factor to end of t
(none)                     pv_benefits()                   PV of benefit outgo
a_dis(a0, z0)              annuity_dis()                   Disabled-life annuity factor
(none)                     result_pols()                   The counts, month by month
=========================  ==============================  ==========================

Three names needed care in :mod:`~.IP_UK_S`, and keep their reasons here.

The notes use ``q_H`` and ``q_S`` for the two mortality rates. :func:`mort_rate` is the
**active-life** one, because that is what ``mort_rate`` means in every other model in
this library — the rate applying to the population the projection starts with — and the
in-claim rate is :func:`mort_rate_sick`, keyed by claim duration rather than by month.
Reading a claimant mortality rate out of ``mort_rate`` is the kind of mistake the naming
is there to prevent.

``BEN(t)`` is an income stream, not a lump sum, but it is reached as
``claims(t, "BENEFIT")`` so that the library's one benefit-outgo cells covers it. The
other two kinds are zero and say so: this composite carries **no death benefit** — the
£5,000-£10,000 death benefits two sampled insurers offer are out of scope — and **no
surrender value** at any time.

``z`` is the claim duration in months and ``t`` the month from the valuation date. They
are different clocks and the model never mixes them: rates out of state S take ``z``,
rates out of state H take ``t``. ``z`` is 1-based by construction - cohort 1 is a claim
that has just started paying - and the 0-based time index ``t`` does not change that.

.. rubric:: Three states, and why the model needs all of them

Healthy and active (H), sick and in claim payment (S), dead (D), with lapse as a further
exit from H and **recovery flowing back from S to H**. That is the structure of the
CMI's own graduations, and it is why income protection has two experience bases rather
than one: claim *inception* rates out of H, and claim *termination* rates out of S, the
latter split into recovery and death.

The deferred period is embedded **in the inception basis**, not modelled as a fourth
state. ``iota`` is a claim *payment* inception rate specific to the policy's deferred
period — exactly the quantity the CMI publishes per deferred period — so a sickness
spell that recovers inside the deferred period never leaves H, and a life sick but not
yet in payment stays in H and keeps paying premiums, which is what the contract's
waiver-from-payment-start convention says. No separate "sick, not yet in payment" state
is needed and the lag between onset and payment is absorbed into the calibration of
``iota``. Dual deferred periods and sick-pay-linked deferreds would need spell-level
modelling and are out of scope.

.. rubric:: The in-claim population is two-dimensional

Termination rates depend on how long the claim has already run: 40% a year at duration
one falling to 5% from duration five in the shipped **[std]** basis. So the model tracks
``l_S(t, z)`` cohort by cohort, and a point in force opens with its own cohorts, the
vector :func:`pols_sick_dur_init` reads. Collapsing that to a single bucket with a
duration-independent termination rate materially misstates claim run-off, and is the
notes' first-listed pitfall — the duration gradient *is* the defining feature of income
protection terminations.

:func:`sick_cohorts` holds the whole vector for one month and is the model's only
vector-valued cells, with :func:`claim_rate_vectors`, the rates it is aged by. Both return
tuples, as :mod:`~.IP_UK_S`'s do: modelx hands every caller the cached object itself, so a
list would let one caller's assignment rewrite the cache that later months are built
from. :func:`pols_sick_dur` reads an element out of the vector, so that the notes'
two-dimensional object is still addressable by name, and :func:`pols_sick`,
:func:`pols_sick_surv`, :func:`pols_recovery` and :func:`pols_death_sick` sum over it. A
compiled cell holds no tuple, so the C step restructures these cells into a
two-parameter recursion, ``pols_sick_dur(t, z)``, whose base reads the cohorts as an
array (``products/income_protection/model-sec.md``); every other cell is written as it
will compile.

The shipped termination basis suppresses the **age** dimension **[std]**. IP11 is
two-dimensional in age and duration, with claimant mortality duration-dependent to five
years and age-only beyond, and it also has a "run-in" of *increasing* recovery rates
over the first weeks of claim for the shorter deferred periods, which annual duration-year
granularity smooths away. Restoring the age dimension changes ``termination_table.csv``,
the two lookups, and the cohort recursion, which ages each cohort by its claim duration
alone.

.. rubric:: Where recoveries go

The model point's ``recovery_basis`` column says which of the notes' two calculations a
point runs:

``recovery_basis = "return_to_h"``
    The notes' processing order step 5: recovered lives re-enter H, resume paying
    premiums and are again exposed to inception. This is the **active-lives** basis.

``recovery_basis = "exit"``
    Recovered lives leave the model. This is the **disabled-life annuity** the notes'
    claims-in-payment section values — the expected present value of the benefit until
    recovery, death or expiry.

Keeping it a column rather than deriving it from the opening state matters, because the
choice is a valuation question and not a property of the point: a claims-in-payment
reserve is the disabled-life annuity, but a full contract-boundary best estimate for the
same policy would carry the post-recovery active phase as well, and recovered lives can
and do claim again.

:mod:`~.IP_UK_S`'s ``status`` column, ``active`` or ``in_claim``, said where its whole
population started; here it is a label of the row's kind in :mod:`~.IP_UK_S` that no
formula reads, the opening state saying where each life is. :mod:`~.IP_UK_S` restarts the
policy clock at the valuation date on an ``in_claim`` row, so the twin of one is issued
``n`` whole years before the valuation date, the least that holds its claim,
``duration_mth = 12n``, at its entry age less ``n``: its age, its claim and its counts are
:mod:`~.IP_UK_S`'s, and only its policy clock differs.

One limitation the notes name and this model inherits: contractually a same-cause
recurrence within 52 weeks restarts payment with **no new deferred period**, and
returning recovered lives to the standard inception basis ignores that. It understates
re-inception at short horizons. The refinement is a post-recovery flag carrying a loaded
inception rate for twelve months, and it is not implemented.

.. rubric:: Premiums come from H alone

Premiums are waived from the start of benefit payment, so :func:`premiums` is carried on
:func:`pols_active` and never on :func:`pols_if`. Projecting premium income from lives in
claim is the notes' second-listed pitfall and overstates income by the whole in-claim
population. Note the asymmetry it creates with escalation: the benefit escalates in
claim and the premium that would have paid for it does not, which is why the escalation
option is inflation-sensitive on exactly the claims that are longest.

.. rubric:: Benefit in arrears, and the month a claim starts

A claim incepting at the end of month ``t`` seeds cohort ``z = 1`` and receives its first
payment at the end of month ``t + 1``. So the benefit is paid on
:func:`pols_sick_surv` — the cohorts that were already in payment at the start of the
month and survived it — and not on :func:`pols_sick` plus new inceptions. Paying the new
inceptions would hand over a full month's benefit at the instant payment starts and
break the equivalence with the inception-annuity decomposition of the same projection.

The contractual daily pro-rating of partial claim months is replaced by whole-month
payment **[std]**: a life recovering mid-month receives nothing for that month here and
a pro-rated amount in reality.

.. rubric:: Expiry truncates everything

All cover and any claim in payment terminate at the policy end date with no value, the
end of policy month ``expiry_mth() - 1``, the frame's last row. :func:`pols_maturity` is
that termination, non-zero only in the last month, and it is what makes the in-force
roll-forward close. An untruncated disabled-life annuity materially overstates the
liability for claims incepting near expiry.

.. rubric:: Amount payable is not the same thing as the chosen benefit

Offsets against other income, the minimum benefit guarantee and proportionate benefits
on a partial return to work all move the amount actually paid away from the benefit the
policyholder chose. The base run sets ``AP = B`` through ``ap_ratio`` and the
severity factor ``claim_severity`` to 1 **[std]**, which **overstates** outgo
wherever the maximum-benefit formula bites and understates nothing, since ``AP <= B``
always. A portfolio calibration sets one or both below 1 from claims experience.
:func:`benefit_max_pp` implements the contractual two-band maximum so that
:func:`check_benefit_max` can assert every model point is inside it.

.. rubric:: Discounting, which the rest of the library does not do

Every other model in this library projects **undiscounted** gross liability cash flows
and leaves discounting to the layer that consumes them. This one carries
:func:`disc_factor`, :func:`pv_benefits` and :func:`annuity_dis` as well, because the
notes' worked example is a present value and because the disabled-life annuity is the
object a claims-in-payment reserve is quoted as. They are a **companion**, not part of
the cash flow projection: no line of :func:`result_cf` is discounted, and
``disc_rate`` is the worked example's flat 3% **[std]**, not a valuation basis. Here they
discount to the valuation date. A Solvency UK best estimate discounts these same cash
flows on the PRA risk-free term structure, and the claims-in-payment element is
matching-adjustment eligible where it is organised and managed separately.

.. rubric:: The contract's bounds

:mod:`~.IP_UK_S` projects any entry age its tables reach, to any expiry age. What running
in force adds is a check of the bounds a frame is sized from, the product's: an issue age
from ``issue_age_min``, 18, to ``issue_age_max``, 59, and an expiry age from
``expiry_age_min``, 50, to ``expiry_age_max``, 70. :func:`proj_len` holds each point to
them, and holds every assumption to its domain too, which :mod:`~.IP_UK_S` checks nowhere:
each Reference it raises to a power, bounds a rate with, reads through a ``min`` or a
``max``, or reads as a share, a factor or an amount, so that no projection runs on a
negative rate, benefit or expense, or a NaN a comparison loses.
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
    :mod:`~.IP_UK_S`'s columns. Each attribute a formula reads has an accessor below.
    """
    return data.model_point_table().loc[point_id]                    # noqa: F821


def age_at_entry():
    """The entry age (ANB) of the selected model point, the age at issue.

    The age the policy was issued at, not the age at the valuation date: ``age(0)`` is
    the attained age then.  :mod:`~.IP_UK_S` reads an ``in_claim`` cell's ``entry_age`` as
    the attained age at the valuation date and restarts its policy clock there
    **[std]**, the notes giving no anniversary offset for an in-force claim; here every
    point is on its policy clock from issue, and the twin of such a cell is issued ``n``
    whole years before the valuation date at its entry age less ``n``.
    """
    return int(model_point()["entry_age"])


def sex():
    """The sex (M / F) of the selected model point.

    Not a smoker split: the IP11 rate structure is sex, deferred period and occupation
    class, and any smoker differentiation sits in insurer pricing, which is not public.
    """
    return model_point()["sex"]


def occ_class():
    """The CMI occupation class, OC1 to OC4 [R1]; 1 is the lightest."""
    v = int(model_point()["occ_class"])
    if v not in (1, 2, 3, 4):
        raise ValueError("invalid occ_class")
    return v


def deferred_weeks():
    """d: the deferred period in weeks, from the 4/8/13/26/52 menu [S6].

    It is not a state in this model: the inception basis is deferred-period-specific, so
    the deferred period enters through :func:`inception_rate` and nowhere else.  See the
    Space docstring.
    """
    v = int(model_point()["deferred_weeks"])
    if v not in (4, 8, 13, 26, 52):
        raise ValueError("invalid deferred_weeks")
    return v


def benefit_mth():
    """B(1): the chosen monthly benefit in policy year 1 **[std]**, £2,000 on the base cell.

    ``B(y)`` is indexed by the contractual policy year ``y = policy_year(t)``, which is
    1-based; this is its value at issue, which :func:`check_benefit_max` holds to the
    contractual maximum.  On a point in force, :func:`benefit_pp_init` is the benefit
    before month 0's events, after every escalation already given.
    """
    return float(model_point()["benefit_mth"])


def earnings_annual():
    """The annual earnings on the underwriting record, which cap the benefit."""
    return float(model_point()["earnings_annual"])


def expiry_age():
    """The age at which all cover and any claim in payment cease, 50-70 [S1][S3][S5]."""
    return int(model_point()["expiry_age"])


def escalation():
    """``RPI`` or ``none``: whether the escalation option is elected [S1][S2]."""
    v = model_point()["escalation"]
    if v not in ("RPI", "none"):
        raise ValueError("invalid escalation")
    return v


def premium_mth():
    """P(1): the monthly premium in policy year 1 **[std]**, a placeholder.

    UK income protection premium rates are not public, so any reference premium is
    constructed.  It is guaranteed level apart from the escalation uplift
    [S1][S3][S5][S7].  Its value at issue; ``P(y)`` is indexed by the 1-based
    contractual policy year.  On a point in force, :func:`premium_pp_init` is the premium
    before month 0's events.
    """
    return float(model_point()["premium_mth"])


def premium_basis():
    """``guaranteed``.  Reviewable and age-costed premiums are out of scope.

    A reviewable variation exists - fixed for five years, then reviewed with no
    contractual cap - but the review formulas are insurer-discretionary and undisclosed,
    so any reviewable model would need a **[std]** review rule that no source supports.
    No formula calls this cell, as none in :mod:`~.IP_UK_S` does, so ``Data`` refuses any
    other basis as the table is read, where :mod:`~.IP_UK_S` projects one.
    """
    v = model_point()["premium_basis"]
    if v != "guaranteed":
        raise ValueError("invalid premium_basis")
    return v


def status():
    """``active`` or ``in_claim``: the kind of row the point is in :mod:`~.IP_UK_S`.

    A label, which no formula reads.  :mod:`~.IP_UK_S` started an ``active`` cell's whole
    population in H and an ``in_claim`` cell's in S at a stated claim duration; here the
    opening state says where each life is, the healthy share :func:`pols_active_init`
    and the claim cohorts :func:`pols_sick_dur_init`, and the row keeps :mod:`~.IP_UK_S`'s
    label for what it was.  ``Data`` refuses any other code.
    """
    v = model_point()["status"]
    if v not in ("active", "in_claim"):
        raise ValueError("invalid status")
    return v


def recovery_basis():
    """Where recovered lives go: back to H, or out of the model.

    ``return_to_h``
        the notes' processing order step 5 - recovered lives re-enter H,
        resume paying premiums and are again exposed to inception.  The
        **active-lives** basis.

    ``exit``
        recovered lives leave the model, which is the **disabled-life
        annuity** the claims-in-payment valuation uses, and the basis the
        notes' worked example is computed on.

    A column rather than something derived from the opening state, because it is a
    valuation question: a claims-in-payment reserve is the disabled-life annuity, but a
    full contract-boundary best estimate for the same policy carries the post-recovery
    active phase too.  See the Space docstring.
    """
    v = model_point()["recovery_basis"]
    if v not in ("return_to_h", "exit"):
        raise ValueError("invalid recovery_basis")
    return v


def policy_count():
    """The number of policies the model point stands for, its ``policy_count`` column.

    A point in force at the valuation date counts the policies in force then, in health
    and in claim together, before any month-0 event; any other point counts the policies
    it issues. Either way the count enters the projection once: as :func:`pols_if_init`
    for the first, split between the states by its opening state, and as
    :func:`pols_new_biz` in the issue month for the second. It is the only weight on the
    flows: every opening-state column is a share of it or an amount per policy.
    """
    return float(model_point()["policy_count"])


def pols_if_init():
    """Policies in force at the valuation date, before any month-0 event.

    ``policy_count()`` for a point already in force at ``t = 0``
    (``duration_mth_init() > 0``), in health and in claim together, and 0 for one issued
    at or after it, whose policies enter through :func:`pols_new_biz` in the issue month
    instead, as in ``basiclife.BasicTerm_SE``. So on a point issued at ``t = 0`` this is
    0, and ``pols_if(0)`` is the issued count.
    """
    return policy_count() if duration_mth_init() > 0 else 0.0


def duration_mth_init():
    """Completed policy months at the valuation date, the ``duration_mth`` column.

    The policy's age in months at ``t = 0``: 60 for model point 9, the anchor cell valued
    60 months after issue, 0 for one issued at the valuation date, and -13 for one to be
    issued 13 months after it, which ``Data`` admits up to ``future_horizon_mth`` months
    ahead.  It is read as ``basiclife.BasicTerm_SE`` reads it, and is the one fact the
    policy clock takes from the model point; a point may be valued in any month of its
    policy year.
    """
    return int(model_point()["duration_mth"])


def pols_active_init():
    """l_H at the valuation date, as a share: the healthy share of the count.

    The lives in state H at the start of month 0, before any month-0 event, the
    recoveries of month -1 already returned to health, over the policies in force,
    :mod:`~.IP_UK_S`'s ``pols_active`` over its ``pols_if`` in the month it is valued at.
    A share, count-free, so that :func:`policy_count` is the one weight; with the claim
    cohorts, :func:`pols_sick_dur_init`, it sums to 1, which ``Data`` checks.  History,
    read from the model point: :mod:`~.IP_UK_S` would rebuild it from issue at today's
    inception, recovery, mortality and lapse rates.  1 on a point not yet in force, which
    is issued healthy, as ``Data`` requires.
    """
    return float(model_point()["pols_active_init"])


def pols_sick_dur_init(z):
    """l_S at the valuation date at claim duration z months, as a share of the count.

    The lives in claim payment at the start of month 0 whose claim has run ``z`` months,
    over the policies in force: cohort 1 holds the claims that incepted at the end of
    month -1, not yet paid, and cohort ``z`` those that incepted at the end of month
    ``-z``, after the recoveries and deaths of the ``z - 1`` months of payment since, at
    the rates of those months.  :mod:`~.IP_UK_S`'s ``sick_cohorts`` over its ``pols_if``
    in the month it is valued at.  History, read from the companion
    ``inforce_cohorts_sec.csv``, keyed ``(point_id, z)``, never recomputed from today's
    inception or termination rates, which would run the elapsed part of each claim again
    at rates set at the valuation date.  The companion is sparse: a claim duration it
    holds no row for holds no lives, and this returns 0.0 there, as on a point not yet in
    force, which ``Data`` holds to no row.

    One float of one read of ``Data.inforce_cohorts``, after :func:`proj_len`, which
    refuses a point outside its bounds before any of its state is read.
    """
    proj_len()
    return float(data.inforce_cohorts()["pols_sick_dur_init"].get(  # noqa: F821
        (point_id, z), 0.0))                                         # noqa: F821


def benefit_pp_init():
    """B at the valuation date: the monthly benefit entering month 0.

    The benefit at issue after every escalation already given, measured at the start of
    month 0, before any month-0 event: :mod:`~.IP_UK_S`'s ``benefit_pp`` of policy month
    ``duration_mth_init() - 1``.  On a point valued on an anniversary that is the year the
    anniversary closes, and the anniversary's escalation is the projection's first event,
    made at today's References (USLIB-SEC-PLAN.md D6, as precised at uslib's M7).  The
    benefit escalates on policy anniversaries for the lives in health and in claim alike,
    so this one amount serves every cohort.  On a point without escalation it is the
    benefit at issue; with RPI escalation it is history, the increases the RPI of their day
    gave, which :mod:`~.IP_UK_S` rebuilds from issue at today's ``rpi_rate``.
    :func:`benefit_pp` steps it on each anniversary from month 0 on at today's References.
    The benefit at issue on a point not yet in force, which ``Data`` requires.
    """
    return float(model_point()["benefit_pp_init"])


def premium_pp_init():
    """P at the valuation date: the monthly premium entering month 0.

    The premium at issue after every escalation uplift already given, :func:`benefit_pp_init`'s
    counterpart, measured at the same instant: :mod:`~.IP_UK_S`'s ``premium_pp`` of policy
    month ``duration_mth_init() - 1``, so that on a point valued on an anniversary the
    anniversary's uplift is the projection's, as the benefit's is.  It is the premium a
    healthy life pays; a life in claim pays none.  History, as the benefit is.  The
    premium at issue on a point not yet in force, which ``Data`` requires.
    """
    return float(model_point()["premium_pp_init"])


def t_entry():
    """The first month the policy is on the books: ``max(0, -duration_mth_init())``.

    0 for a point in force at the valuation date or issued at it, ``k`` for one issued
    ``k`` months later.  It is the base of every recursion: the healthy lives, the claim
    cohorts and the cumulative counts open there, from the opening state, and none reads a
    month before it.
    """
    return max(0, -duration_mth_init())


def is_active(t):
    """Whether month t is inside cover: issued, and short of the policy end date.

    ``0 <= duration_mth(t) < expiry_mth()``.  False before issue and from the month the
    policy reaches its expiry age, ``t = proj_len()``.  Outside cover every count is zero,
    and so every cash flow; no count cell evaluates a rate there, and no table is read at
    a policy year or an attained age the policy does not have.
    """
    return 0 <= duration_mth(t) < expiry_mth()


def expiry_mth():
    """The policy month cover ends: ``12 x (expiry_age - entry_age)``.

    :mod:`~.IP_UK_S`'s frame from issue, its ``proj_len()``, on the policy clock: the last
    covered month is ``duration_mth(t) = expiry_mth() - 1``, at whose end all cover and any
    claim in payment terminate without value, and :func:`is_active` is false from
    ``duration_mth(t) = expiry_mth()`` on.  Named for the event that ends cover, the policy
    end date.  :func:`proj_len` counts from the valuation date instead.
    """
    return 12 * (expiry_age() - age_at_entry())


def proj_len():
    """The number of months from the valuation date to the policy end date.

    ``expiry_mth() - duration_mth_init()``: 360 for the anchor cell issued at ``t = 0``,
    300 for model point 9, in force 60 months, and the frame from issue plus ``k`` for a
    point issued ``k`` months after the valuation date.  The frame is
    ``t = 0, 1, ..., proj_len() - 1``; ``proj_len()`` is its exclusive end and the row count
    of :func:`result_cf`.  All cover and any claim in payment terminate at the policy end
    date with no value [S1][S3][S5][S7][S10], so there is nothing after it.  This is what
    truncates the disabled-life annuity, and an untruncated one materially overstates the
    liability for claims incepting near expiry.

    These raise here, naming the point, rather than project nothing, a frame the contract
    does not have, or numbers no policy can have, each checked in this order:

    * ``issue_age_min`` and ``issue_age_max`` that are not whole numbers below ``2**53``,
      ``issue_age_min`` below 0 or ``issue_age_max`` below ``issue_age_min``: ages, which a
      NaN would switch off, every comparison with it failing;
    * a point issued below ``issue_age_min``, 18, or above ``issue_age_max``, 59, the
      product's entry ages;
    * ``expiry_age_min`` and ``expiry_age_max`` that are not whole numbers below ``2**53``,
      or ``expiry_age_max`` below ``expiry_age_min`` or past a year beyond the mortality
      table's last age, ``Data.mort_age_last() + 1``, since the projection reads attained
      ages to the expiry age less 1;
    * a point whose expiry age is below ``expiry_age_min``, 50, or above
      ``expiry_age_max``, 70, the product's expiry ages;
    * a point issued at or past its expiry age, which has no cover;
    * a point at or past its policy end date at the valuation date, ``duration_mth`` at or
      past :func:`expiry_mth`, keyed on the policy clock, which an in-force extract should
      not carry;
    * any point while a Reference is off its domain, which the message names.  NaN and the
      infinities are outside every one:

      - ``cycle_factor``, finite and above 0: it multiplies the inception rate inside the
        cap's ``min`` and divides the recovery rate inside its bound's ``min``, which a NaN
        is lost through and a 0 divides by;
      - ``mort_active_factor``, finite, 0 or more: a factor on a probability, read inside
        the mortality cap's ``min``, where an infinity reads as certain death and below 0
        a rate is negative;
      - ``ap_ratio`` and ``claim_severity``, from 0 to 1: the amount payable is at most the
        benefit, ``AP <= B``, and a severity is a share of it;
      - ``rpi_rate``, finite: the floor at 0 and the cap read an infinity as no increase or
        as the cap;
      - ``esc_cap``, ``esc_prem_mult``, ``esc_lapse_slope`` and ``esc_lapse_threshold``,
        finite, 0 or more: the cap is a bound written second, which a NaN cap would be lost
        through, ``min`` keeping its first argument; below 0 an escalation is a cut, the
        premium falls as the benefit rises, or the shock lowers a lapse rate or shocks a
        premium that does not grow; and the threshold is read through
        :mod:`~.IP_UK_S`'s bound-first ``max``, which a NaN is lost through;
      - ``ben_band1_rate`` and ``ben_band2_rate``, from 0 to 1, shares of earnings, and
        ``ben_breakpoint``, ``ben_cap_mth`` and ``ben_guarantee_mth``, finite, 0 or more,
        amounts each read through a ``min`` or a ``max``;
      - ``ben_tolerance``, above 0 and at most 1, the share of the maximum benefit the
        check divides by;
      - ``expense_maint`` and ``expense_claim``, finite, 0 or more: below 0 an income;
      - ``inflation_rate``, finite, -1 or more: below -1 the inflation factor changes sign
        each year;
      - ``disc_rate``, finite and above -1: the discount factor raises ``1 + disc_rate`` to
        a negative power, which at -1 divides by zero.

    The rules read this Space's References, which ``Data`` cannot see, so they are checked
    here.  They are the contract a compiled model's caches are sized from: a frame of at
    most ``expiry_age_max - issue_age_min`` years and the future horizon, claim durations
    to that many months, and attained ages from 18 to ``expiry_age_max - 1`` on the
    mortality table.  Every report reads this cell first, and so does every check, so no
    point outside them is projected.  Each check is a comparison written out, a finite
    bound the largest float, 1.7976931348623157e308, and a whole one ``2**53``, so that a
    compiled cell runs it in C, and each Reference is printed as the compiled model will
    type it: the four ages through ``int()`` once they are whole numbers, and every other
    through ``float()``.  A value a formula computes past the floats, from References and
    an opening state each in its domain, is refused in the cell where it first is, naming
    the point: the benefit, the premium, the lapse shock, the premiums, the claims, the
    expenses, the net cash flow and the present value of the benefit.  A power that
    overflows is not: modelx, as Python, raises ``OverflowError``, with the platform's own
    message, from the ``**`` itself, before the cell can look at the result - the benefit's
    and the premium's step to the policy years since the valuation date, the inflation
    factor and the discount factor, each at a rate in its domain but large enough.  The
    compiled model will take uslib's M22 form there, Python's own float power where the
    compiled ``pow`` gives an infinity, so that both engines raise the same error.
    """
    if not (issue_age_min > -9007199254740992.0                       # noqa: F821
            and issue_age_min < 9007199254740992.0                    # noqa: F821
            and issue_age_min == issue_age_min // 1):                 # noqa: F821
        raise ValueError(f"point_id {point_id}: issue_age_min must be a whole number "  # noqa: F821
                         f"below 2**53, not {float(issue_age_min)}")  # noqa: F821
    if issue_age_min < 0:                                            # noqa: F821
        raise ValueError(f"point_id {point_id}: issue_age_min must be 0 or more, "  # noqa: F821
                         f"not {int(issue_age_min)}")                # noqa: F821
    if not (issue_age_max > -9007199254740992.0                       # noqa: F821
            and issue_age_max < 9007199254740992.0                    # noqa: F821
            and issue_age_max == issue_age_max // 1):                 # noqa: F821
        raise ValueError(f"point_id {point_id}: issue_age_max must be a whole number "  # noqa: F821
                         f"below 2**53, not {float(issue_age_max)}")  # noqa: F821
    if issue_age_max < issue_age_min:                                # noqa: F821
        raise ValueError(f"point_id {point_id}: issue_age_max must be issue_age_min, "  # noqa: F821
                         f"{int(issue_age_min)}, or more, not {int(issue_age_max)}")  # noqa: F821
    x = age_at_entry()
    if x < issue_age_min:                                            # noqa: F821
        raise ValueError(f"point_id {point_id}: the issue age, {x}, is below "  # noqa: F821
                         f"issue_age_min, {int(issue_age_min)}")     # noqa: F821
    if x > issue_age_max:                                            # noqa: F821
        raise ValueError(f"point_id {point_id}: the issue age, {x}, is above "  # noqa: F821
                         f"issue_age_max, {int(issue_age_max)}")     # noqa: F821
    if not (expiry_age_min > -9007199254740992.0                      # noqa: F821
            and expiry_age_min < 9007199254740992.0                   # noqa: F821
            and expiry_age_min == expiry_age_min // 1):               # noqa: F821
        raise ValueError(f"point_id {point_id}: expiry_age_min must be a whole number "  # noqa: F821
                         f"below 2**53, not {float(expiry_age_min)}")  # noqa: F821
    if not (expiry_age_max > -9007199254740992.0                      # noqa: F821
            and expiry_age_max < 9007199254740992.0                   # noqa: F821
            and expiry_age_max == expiry_age_max // 1):               # noqa: F821
        raise ValueError(f"point_id {point_id}: expiry_age_max must be a whole number "  # noqa: F821
                         f"below 2**53, not {float(expiry_age_max)}")  # noqa: F821
    if not (expiry_age_max >= expiry_age_min                         # noqa: F821
            and expiry_age_max <= data.mort_age_last() + 1):          # noqa: F821
        raise ValueError(
            f"point_id {point_id}: expiry_age_max must be expiry_age_min, "  # noqa: F821
            f"{int(expiry_age_min)}, or more, and at most {data.mort_age_last() + 1}, a "  # noqa: F821
            f"year past mort_table.csv's last age, not {int(expiry_age_max)}")  # noqa: F821
    e = expiry_age()
    if e < expiry_age_min:                                           # noqa: F821
        raise ValueError(f"point_id {point_id}: the expiry age, {e}, is below "  # noqa: F821
                         f"expiry_age_min, {int(expiry_age_min)}")   # noqa: F821
    if e > expiry_age_max:                                           # noqa: F821
        raise ValueError(f"point_id {point_id}: the expiry age, {e}, is above "  # noqa: F821
                         f"expiry_age_max, {int(expiry_age_max)}")   # noqa: F821
    if expiry_mth() <= 0:
        raise ValueError(f"point_id {point_id}: the issue age, {x}, is at or past the "  # noqa: F821
                         f"expiry age, {e}: the policy has no cover")
    d = duration_mth_init()
    if d >= expiry_mth():
        raise ValueError(
            f"point_id {point_id}: duration_mth {d} is at or past the policy end date, "  # noqa: F821
            f"policy month {expiry_mth()}, expiry age {e}")
    if not (cycle_factor > 0.0                                       # noqa: F821
            and cycle_factor <= 1.7976931348623157e308):              # noqa: F821
        raise ValueError(f"point_id {point_id}: cycle_factor must be a finite number "  # noqa: F821
                         f"above 0, not {float(cycle_factor)}")      # noqa: F821
    if not (mort_active_factor >= 0.0                                # noqa: F821
            and mort_active_factor <= 1.7976931348623157e308):        # noqa: F821
        raise ValueError(f"point_id {point_id}: mort_active_factor must be a finite "  # noqa: F821
                         f"number, 0 or more, not {float(mort_active_factor)}")  # noqa: F821
    if not (ap_ratio >= 0.0 and ap_ratio <= 1.0):                    # noqa: F821
        raise ValueError(f"point_id {point_id}: ap_ratio must be a number from 0 to 1, "  # noqa: F821
                         f"not {float(ap_ratio)}")                   # noqa: F821
    if not (claim_severity >= 0.0 and claim_severity <= 1.0):        # noqa: F821
        raise ValueError(f"point_id {point_id}: claim_severity must be a number from 0 "  # noqa: F821
                         f"to 1, not {float(claim_severity)}")       # noqa: F821
    if not (rpi_rate >= -1.7976931348623157e308                       # noqa: F821
            and rpi_rate <= 1.7976931348623157e308):                  # noqa: F821
        raise ValueError(f"point_id {point_id}: rpi_rate must be a finite number, "  # noqa: F821
                         f"not {float(rpi_rate)}")                   # noqa: F821
    if not (esc_cap >= 0.0 and esc_cap <= 1.7976931348623157e308):   # noqa: F821
        raise ValueError(f"point_id {point_id}: esc_cap must be a finite number, 0 or "  # noqa: F821
                         f"more, not {float(esc_cap)}")              # noqa: F821
    if not (esc_prem_mult >= 0.0                                     # noqa: F821
            and esc_prem_mult <= 1.7976931348623157e308):             # noqa: F821
        raise ValueError(f"point_id {point_id}: esc_prem_mult must be a finite number, "  # noqa: F821
                         f"0 or more, not {float(esc_prem_mult)}")   # noqa: F821
    if not (esc_lapse_slope >= 0.0                                   # noqa: F821
            and esc_lapse_slope <= 1.7976931348623157e308):           # noqa: F821
        raise ValueError(f"point_id {point_id}: esc_lapse_slope must be a finite "  # noqa: F821
                         f"number, 0 or more, not {float(esc_lapse_slope)}")  # noqa: F821
    if not (esc_lapse_threshold >= 0.0                               # noqa: F821
            and esc_lapse_threshold <= 1.7976931348623157e308):       # noqa: F821
        raise ValueError(f"point_id {point_id}: esc_lapse_threshold must be a finite "  # noqa: F821
                         f"number, 0 or more, not {float(esc_lapse_threshold)}")  # noqa: F821
    if not (ben_band1_rate >= 0.0 and ben_band1_rate <= 1.0):        # noqa: F821
        raise ValueError(f"point_id {point_id}: ben_band1_rate must be a number from 0 "  # noqa: F821
                         f"to 1, not {float(ben_band1_rate)}")       # noqa: F821
    if not (ben_band2_rate >= 0.0 and ben_band2_rate <= 1.0):        # noqa: F821
        raise ValueError(f"point_id {point_id}: ben_band2_rate must be a number from 0 "  # noqa: F821
                         f"to 1, not {float(ben_band2_rate)}")       # noqa: F821
    if not (ben_breakpoint >= 0.0                                    # noqa: F821
            and ben_breakpoint <= 1.7976931348623157e308):            # noqa: F821
        raise ValueError(f"point_id {point_id}: ben_breakpoint must be a finite number, "  # noqa: F821
                         f"0 or more, not {float(ben_breakpoint)}")  # noqa: F821
    if not (ben_cap_mth >= 0.0 and ben_cap_mth <= 1.7976931348623157e308):  # noqa: F821
        raise ValueError(f"point_id {point_id}: ben_cap_mth must be a finite number, 0 "  # noqa: F821
                         f"or more, not {float(ben_cap_mth)}")       # noqa: F821
    if not (ben_guarantee_mth >= 0.0                                 # noqa: F821
            and ben_guarantee_mth <= 1.7976931348623157e308):         # noqa: F821
        raise ValueError(f"point_id {point_id}: ben_guarantee_mth must be a finite "  # noqa: F821
                         f"number, 0 or more, not {float(ben_guarantee_mth)}")  # noqa: F821
    if not (ben_tolerance > 0.0 and ben_tolerance <= 1.0):           # noqa: F821
        raise ValueError(f"point_id {point_id}: ben_tolerance must be a number above 0 "  # noqa: F821
                         f"and at most 1, not {float(ben_tolerance)}")  # noqa: F821
    if not (expense_maint >= 0.0                                     # noqa: F821
            and expense_maint <= 1.7976931348623157e308):             # noqa: F821
        raise ValueError(f"point_id {point_id}: expense_maint must be a finite number, "  # noqa: F821
                         f"0 or more, not {float(expense_maint)}")   # noqa: F821
    if not (expense_claim >= 0.0                                     # noqa: F821
            and expense_claim <= 1.7976931348623157e308):             # noqa: F821
        raise ValueError(f"point_id {point_id}: expense_claim must be a finite number, "  # noqa: F821
                         f"0 or more, not {float(expense_claim)}")   # noqa: F821
    if not (inflation_rate >= -1.0                                   # noqa: F821
            and inflation_rate <= 1.7976931348623157e308):            # noqa: F821
        raise ValueError(f"point_id {point_id}: inflation_rate must be a finite "  # noqa: F821
                         f"number, -1 or more, not {float(inflation_rate)}")  # noqa: F821
    if not (disc_rate > -1.0 and disc_rate <= 1.7976931348623157e308):  # noqa: F821
        raise ValueError(f"point_id {point_id}: disc_rate must be a finite number "  # noqa: F821
                         f"above -1, not {float(disc_rate)}")        # noqa: F821
    return expiry_mth() - d


def duration_init():
    """The completed policy years the opening benefit and premium hold.

    Those of policy month ``duration_mth_init() - 1``, the month before the valuation date,
    on a point in force, since :func:`benefit_pp_init` and :func:`premium_pp_init` are
    measured before month 0's events, and 0 on a point not yet in force, whose columns are
    the issue values: ``(max(duration_mth_init(), 1) - 1) // 12``.  The benefit and the
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
    without a call chain as long as the frame.  Negative before issue.  The policy end
    date, the issue month and the expiry's last month read it.
    """
    return duration_mth_init() + t


def policy_year(t):
    """y: the 1-based contractual policy year containing month t, ``duration(t) + 1``.

    A contractual label, derived from the policy clock and never indexed by: the lapse
    table is keyed by it, and the escalation lapse shock starts in policy year 2.  0 or
    less before issue, where nothing reads a table by it.
    """
    return duration(t) + 1


def age(t):
    """a: the attained age (ANB) in month t, ``age_at_entry() + duration(t)``."""
    return age_at_entry() + duration(t)


def max_dur():
    """The longest claim duration the cohort vector has to carry: ``expiry_mth() + 1``.

    A claim in payment at the start of month t incepted at the end of a covered month
    before it, so its duration is at most ``duration_mth(t)``, and the last covered month
    is ``expiry_mth() - 1``: so no cohort runs past the cover from issue, whenever the
    point is valued or issued.  The final ``+ 1`` is :mod:`~.IP_UK_S`'s cohort of
    headroom, and on a point issued at the valuation date this is :mod:`~.IP_UK_S`'s
    ``proj_len() + z0 + 1`` with ``z0 = 0``.  It does not grow with the future horizon,
    and it bounds the claim durations the companion may hold: ``Data`` holds each to the
    point's months in force.  A length on the claim-duration clock ``z``, which is 1-based
    and separate from ``t``.
    """
    return expiry_mth() + 1


def claim_dur_year(z):
    """The claim duration year containing claim month z: ``(z - 1) // 12 + 1``.

    ``z`` is the 1-based claim-duration cohort index, not the time index ``t``, so the
    ``z - 1`` here is not a first-period idiom.  Duration years beyond the termination
    table take its last row, which is the shipped table's "5+" row.
    """
    return (z - 1) // 12 + 1


def inception_rate(t):
    """iota_a(a): the annual claim payment inception rate out of state H.

    Read from ``inception_table.csv`` at the policy's sex, occupation class and deferred
    period, **linearly** interpolated between pivot ages and linearly extrapolated
    beyond them, then multiplied by the economic-cycle overlay ``cycle_factor``.
    Floored at zero, ``max(0.0, r)``, since linear extrapolation below the first pivot
    can go negative, and the product capped at 1, the bound second, ``min(q, 1.0)``:
    :mod:`~.IP_UK_S`'s floor and cap, and no departure.  The floor comes first, and reads a
    NaN as 0, but ``Data`` refuses a blank table rate, and :func:`proj_len` a NaN
    ``cycle_factor``, which would reach the cap and stay NaN.

    The rate is a *claim payment* inception rate specific to the deferred period, which
    is exactly what the CMI publishes per deferred period - so the deferred period needs
    no state of its own.  The shipped values are **[std]** proxies shaped like IP11 and
    carry no CMI authority; IP11's own inception rates are additionally known to be
    understated through exposure errors, and licensees must apply the CMI's indicative
    adjustments.

    Zero outside cover, where ``age(t)`` is not an age the policy reaches, before any
    table is read: :mod:`~.IP_UK_S`'s ``result_states`` reads it in every month of its
    frame, which here runs from the valuation date, before issue on a point issued later.
    """
    if not is_active(t):
        return 0.0
    sub = data.inception_table().loc[                                # noqa: F821
        (sex(), occ_class(), deferred_weeks())]
    ages = sorted(int(a) for a in sub.index)
    x = age(t)
    if x <= ages[0]:
        lo, hi = ages[0], ages[1]
    elif x >= ages[-1]:
        lo, hi = ages[-2], ages[-1]
    else:
        lo = max(a for a in ages if a <= x)
        hi = min(a for a in ages if a > x)
    r_lo = float(sub.loc[lo, "inception_rate"])
    r_hi = float(sub.loc[hi, "inception_rate"])
    r = r_lo + (r_hi - r_lo) * (x - lo) / (hi - lo)
    return min(max(0.0, r) * cycle_factor, 1.0)                      # noqa: F821


def inception_rate_mth(t):
    """iota_m(a) = 1 - (1 - iota_a)^(1/12): the monthly inception rate **[std]**."""
    return 1.0 - (1.0 - inception_rate(t)) ** (1.0 / 12.0)


def mort_rate(t):
    """q_H_a(a): the **active-life** annual mortality rate.

    A minor decrement in income protection, and a **[std]** proxy shaped like the ONS
    national life tables scaled by ``mort_active_factor``.  Claimant mortality is a
    different rate on a different clock - see :func:`mort_rate_sick`.  Capped at 1, the
    bound second, ``min(q, 1.0)``, so that a missing input, a NaN, stays NaN, where
    ``min(1.0, q)`` would read it as 1: :mod:`~.IP_UK_S`'s cap, and no departure.

    Zero outside cover, where ``age(t)`` is not an age the policy reaches.  Inside it,
    this is the one cell that reads ``Data.mort_table``, at :mod:`~.IP_UK_S`'s key.  An age
    outside the table's, ``Data.mort_age_first`` to ``Data.mort_age_last``, raises
    ``ValueError``, naming the point and the age, where :mod:`~.IP_UK_S`'s lookup raised
    ``KeyError``.
    """
    if not is_active(t):
        return 0.0
    x = age(t)
    if x < data.mort_age_first() or x > data.mort_age_last():        # noqa: F821
        raise ValueError(f"point_id {point_id}: mort_table.csv has no rate at "  # noqa: F821
                         f"attained age {x}")
    q = float(data.mort_table().loc[(sex(), x), "mort_rate"])        # noqa: F821
    return min(q * mort_active_factor, 1.0)                          # noqa: F821


def mort_rate_mth(t):
    """q_H_m(a) = 1 - (1 - q_H_a)^(1/12): the monthly active-life mortality **[std]**."""
    return 1.0 - (1.0 - mort_rate(t)) ** (1.0 / 12.0)


def rec_rate(z):
    """rho_a(z): the annual recovery rate at claim duration z months.

    From the duration year containing z, divided by the economic-cycle overlay - a
    recession is believed to slow recoveries as well as raise inceptions, and the
    overlay is a scenario axis rather than a calibrated assumption, held at 1 in the base
    run.  The declining gradient, 40% in year one to 5% from year five, is the defining
    feature of income protection terminations; the values are **[std]** proxies.
    Duration years beyond the table read its last row, ``Data.termination_last_year``,
    as :mod:`~.IP_UK_S`'s ``tbl.index.max()`` does.  The bound at 1 keeps
    :mod:`~.IP_UK_S`'s order, ``min(1.0, rho)``, the bound first: a recovery rate's bound
    is no cap on a mortality rate, and ``Data`` holds the table's rates to 0 to 1 and
    :func:`proj_len` ``cycle_factor`` to a finite number above 0, so no NaN reaches it.
    Below an overlay of 0.4 the year-one recovery rate binds at 1, and no claim survives
    its first month.
    """
    y = min(claim_dur_year(z), data.termination_last_year())        # noqa: F821
    return min(1.0, float(data.termination_table().loc[y, "recovery_rate"])  # noqa: F821
               / cycle_factor)                                       # noqa: F821


def rec_rate_mth(z):
    """rho_m(z) = 1 - (1 - rho_a)^(1/12): the monthly recovery rate **[std]**."""
    return 1.0 - (1.0 - rec_rate(z)) ** (1.0 / 12.0)


def mort_rate_sick(z):
    """q_S_a(z): the annual mortality of a life in claim at duration z months.

    Flat across durations in the shipped **[std]** proxy.  IP11 makes it
    duration-dependent to five years and age-dependent beyond, so this is the crudest
    part of the shipped basis; it is also the smaller of the two termination causes.
    Capped at 1, the bound second, as :func:`mort_rate` is: :mod:`~.IP_UK_S`'s cap.
    ``Data`` holds the table's rates to 0 to 1, so the cap binds on no table it reads.
    """
    y = min(claim_dur_year(z), data.termination_last_year())        # noqa: F821
    return min(float(data.termination_table().loc[y, "mort_rate_sick"]), 1.0)  # noqa: F821


def mort_rate_sick_mth(z):
    """q_S_m(z) = 1 - (1 - q_S_a)^(1/12): the monthly in-claim mortality **[std]**."""
    return 1.0 - (1.0 - mort_rate_sick(z)) ** (1.0 / 12.0)


def claim_surv_step(z):
    """s_S(z) = (1 - rho_m)(1 - q_S_m): monthly survival in claim at duration z.

    Recovery first, then death among the non-recovered, as independent decrements
    **[std]** - the notes' processing order for exits from state S.
    """
    return (1.0 - rec_rate_mth(z)) * (1.0 - mort_rate_sick_mth(z))


def claim_rate_vectors():
    """The three per-duration rate vectors, ``(rho_m, q_S_m, s_S)``, built once.

    Element ``z - 1`` of each tuple is the value at claim duration ``z``, for
    ``z = 1 ... max_dur()``.  Tuples for the reason :func:`sick_cohorts` gives.
    Purely a performance shape: :func:`pols_recovery`,
    :func:`pols_death_sick` and :func:`pols_sick_surv` each walk the whole cohort vector
    in every projected month, and reading the rates out of a list rather than calling
    :func:`rec_rate_mth` and friends per element turns ``proj_len() x max_dur()``
    cells lookups into ``max_dur()`` of them.  The scalar cells stay, because they are
    what a reader looks up and what a test asserts against; this is built *from* them, so
    there is still one definition of each rate.  :mod:`~.IP_UK_S`'s cell, unchanged; the
    C step restructures it with the cohorts (the Space docstring).
    """
    zs = range(1, max_dur() + 1)
    rec = tuple(rec_rate_mth(z) for z in zs)
    dth = tuple(mort_rate_sick_mth(z) for z in zs)
    return rec, dth, tuple((1.0 - r) * (1.0 - d) for r, d in zip(rec, dth))


def esc_rate():
    """j = min(max(RPI, 0), 10%): the escalation rate [S1][S2].

    Zero when the option is not elected.  A flat 3% RPI snapshot **[std]** - future RPI
    is an economic input, not insurer discretion - so the benefit grows 3% a year and
    the premium 4.5%, the x1.5 multiplier.  The 10% cap is an embedded inflation option
    the insurer has written.  The rate from the valuation date on: the escalations
    already given are history, :func:`benefit_pp_init` and :func:`premium_pp_init`.
    """
    if escalation() != "RPI":
        return 0.0
    return min(max(rpi_rate, 0.0), esc_cap)                          # noqa: F821


def benefit_pp(t):
    """B(y): the escalated monthly benefit in the policy year containing month t.

    :func:`benefit_pp_init`, the benefit before month 0's events, the benefit at issue on
    a point not yet in force, times ``(1 + j)`` for each policy anniversary since,
    ``duration(t) - duration_init()``, so it steps at policy anniversaries on the policy
    clock.  The escalations before the valuation date are history, carried in, and those
    from it on are projected at today's rate, an anniversary at the valuation date's among
    them.  Escalates on policy anniversaries and **continues to escalate in claim**
    [S1][S2], which is what makes the disabled-life annuity inflation-sensitive exactly
    when it is longest, so one amount serves the lives in health and in claim alike.
    Some contracts instead escalate in-claim amounts on *claim* anniversaries with
    index-lag rules; align the convention with the contract being modelled.  Zero outside
    cover.

    A benefit that leaves the floats, from an opening benefit and an escalation each in
    its domain, raises ``ValueError`` in the month it first does, naming the point, the
    month and what makes it, rather than pay an infinite claim: where the step to the
    policy years passes the largest float, at which Python's power raises
    ``OverflowError``, naming neither, and C's gives an infinity, as where the product
    does.
    """
    if not is_active(t):
        return 0.0
    try:
        step = (1.0 + esc_rate()) ** (duration(t) - duration_init())
    except OverflowError:
        raise ValueError(
            f"point_id {point_id}: the benefit benefit_pp({t}) is past the largest float, "  # noqa: F821
            f"from benefit_pp_init {benefit_pp_init()} and an annual increase of "
            f"{esc_rate()}") from None
    b = benefit_pp_init() * step
    if not b - b == 0.0:
        raise ValueError(
            f"point_id {point_id}: the benefit benefit_pp({t}) is {b}, not a finite "  # noqa: F821
            f"number, from benefit_pp_init {benefit_pp_init()} and an annual increase "
            f"of {esc_rate()}")
    return b


def premium_pp(t):
    """P(y): the escalated monthly premium in the policy year containing month t.

    Guaranteed level apart from the escalation uplift of ``1 + 1.5 j`` a year
    [S1][S2][S3][S5][S7]: :func:`premium_pp_init`, the premium before month 0's events, the
    premium at issue on a point not yet in force, times that step for each policy
    anniversary since, ``duration(t) - duration_init()``, as the benefit steps.  The
    premium side compensates for escalation only x1.5 on active lives and not at all on
    lives in claim, where premiums are waived.  Zero outside cover.

    A premium that leaves the floats raises ``ValueError`` in the month it first does, as
    :func:`benefit_pp` does.
    """
    if not is_active(t):
        return 0.0
    rise = esc_prem_mult * esc_rate()                                # noqa: F821
    try:
        factor = (1.0 + rise) ** (duration(t) - duration_init())
    except OverflowError:
        raise ValueError(
            f"point_id {point_id}: the premium premium_pp({t}) is past the largest float, "  # noqa: F821
            f"from premium_pp_init {premium_pp_init()} and an annual increase of "
            f"{rise}") from None
    p = premium_pp_init() * factor
    if not p - p == 0.0:
        raise ValueError(
            f"point_id {point_id}: the premium premium_pp({t}) is {p}, not a finite "  # noqa: F821
            f"number, from premium_pp_init {premium_pp_init()} and an annual increase of "
            f"{rise}")
    return p


def benefit_max_pp():
    """The contractual maximum monthly benefit from the two-band earnings formula.

    65% of earnings to the £60,000 breakpoint and 50% above it, capped at £20,000 a
    month and floored at the £1,500 guarantee [S1][S2][S5][S7].  Nothing in the
    projection consumes it - the base run pays :func:`amount_payable_pp` - but
    :func:`check_benefit_max` asserts every model point's chosen benefit is inside it,
    which is the check the underwriting record exists to support.
    """
    e = earnings_annual()
    gross = (ben_band1_rate * min(e, ben_breakpoint)                 # noqa: F821
             + ben_band2_rate * max(0.0, e - ben_breakpoint))        # noqa: F821
    m = min(gross / 12.0, ben_cap_mth)                               # noqa: F821
    return max(m, ben_guarantee_mth)                                 # noqa: F821


def amount_payable_pp(t):
    """AP(y): the amount actually payable per month of full incapacity.

    ``ap_ratio x B(y)`` with ``ap_ratio`` at 1 **[std]**.  Offsets against other
    income, the minimum benefit guarantee and proportionate benefits on a partial return
    to work all push the amount paid below the chosen benefit, so ``AP <= B`` always and
    the base run **overstates** outgo wherever the maximum-benefit formula bites.  A
    portfolio calibration sets ``ap_ratio`` or ``claim_severity`` below 1 from claims
    experience.  Zero outside cover.
    """
    return ap_ratio * benefit_pp(t)                                  # noqa: F821


def esc_lapse_factor(t):
    """M_esc(y): the premium-shock lapse multiplier **[std]**; 1 in the base run.

    ``1 + 2 max(0, 1.5 j - 0.05)`` once the escalation uplift has started - from policy
    year 2, on the policy clock - and 1 in policy year 1, so a 3% RPI snapshot gives 4.5%
    premium growth and no shock, while the 10% cap would give 15% growth and a multiplier
    of 1.2.  Sampled insurers let policyholders decline escalation increases, with the
    option lapsing after two or three consecutive refusals; declines are a
    portfolio-level phenomenon that a single-cell model cannot represent, so this
    multiplier is the aggregate proxy for them.  The floor at 0 keeps
    :mod:`~.IP_UK_S`'s order, ``max(0.0, x)``, the bound first: :func:`proj_len` holds
    every Reference it reads to a domain no NaN is in.

    A multiplier that leaves the floats, from References each in its domain, raises
    ``ValueError`` where it first does, naming the point and the References, rather than
    read as a certain lapse through the lapse rate's ``min``, or as NaN on a lapse rate of
    0, which that ``min`` would read as 1.
    """
    if escalation() != "RPI" or policy_year(t) < 2:
        return 1.0
    v = 1.0 + esc_lapse_slope * max(                                 # noqa: F821
        0.0, esc_prem_mult * esc_rate() - esc_lapse_threshold)       # noqa: F821
    if not v - v == 0.0:
        raise ValueError(
            f"point_id {point_id}: the lapse shock esc_lapse_factor({t}) is {v}, not a "  # noqa: F821
            f"finite number, from esc_lapse_slope {float(esc_lapse_slope)}, "  # noqa: F821
            f"esc_prem_mult {float(esc_prem_mult)} and an escalation rate of "  # noqa: F821
            f"{esc_rate()}")
    return v


def lapse_rate_base(t):
    """The table annual lapse rate in month t **[std]**, before the escalation shock.

    10 / 8 / 6 / 6 / 6 / 4 percent by policy year.  No public UK income protection lapse
    study was retrieved, so the table has no anchor at all and is a pure placeholder.
    The table is keyed by the contractual 1-based ``policy_year``, reached through
    :func:`policy_year` on the policy clock; policy years beyond the table take its last
    row, ``Data.lapse_last_year``, as :mod:`~.IP_UK_S`'s ``tbl.index.max()`` does.

    Zero outside cover, where the month has no policy year: before issue
    :func:`policy_year` is 0 or less, where :mod:`~.IP_UK_S`'s lookup raised ``KeyError``.
    """
    if not is_active(t):
        return 0.0
    y = min(policy_year(t), data.lapse_last_year())                  # noqa: F821
    return float(data.lapse_table().loc[y, "lapse_rate"])            # noqa: F821


def lapse_rate(t):
    """w_a(y): the **annual** lapse rate out of state H in month t.

    Applied to lives in H only.  Lives in claim never lapse **[std]**: their premiums are
    waived and the benefit in payment is the most valuable thing they own.  The bound is
    :mod:`~.IP_UK_S`'s, ``min(1.0, w)``, its bound first: a lapse rate's bound is no cap on
    mortality, and ``Data`` holds the table's rates to 0 to 1 and the shock to a finite
    number, so no NaN reaches it.  Zero outside cover.
    """
    if not is_active(t):
        return 0.0
    return min(1.0, lapse_rate_base(t) * esc_lapse_factor(t))


def lapse_rate_mth(t):
    """w_m(y) = 1 - (1 - w_a)^(1/12): the monthly lapse rate **[std]**."""
    return 1.0 - (1.0 - lapse_rate(t)) ** (1.0 / 12.0)


def sick_cohorts(t):
    """l_S(t, .): the in-claim population by claim duration, as a tuple.

    Element ``z - 1`` is the population in claim payment at the start of month t with
    claim duration ``z`` months, for ``z = 1 ... max_dur()`` (``z`` is 1-based; the
    ``z - 1`` is tuple position, not a time offset).  The model's only vector-valued
    cells, with :func:`claim_rate_vectors`, and the reason is cost: a two-argument
    recursion would be ``proj_len() x max_dur()`` separate cells - 130,000 on the anchor
    cell - where this is ``proj_len()`` cells with a loop inside.  :func:`pols_sick_dur`
    reads an element out of it, so the notes' two-dimensional object is still addressable
    by name.

    At :func:`t_entry` the vector is the opening state: on a point in force,
    :func:`pols_if_init` times the share of each claim duration, :func:`pols_sick_dur_init`,
    the companion's cohorts; on a point issued at or after the valuation date, all zeros,
    since new business enters healthy.  Thereafter cohort 1 is the previous month's
    inceptions and every other cohort is the previous cohort survived one month, so the
    vector reads no month before :func:`t_entry`.

    The vector is a tuple, never a list.  modelx returns the cached object itself, not
    a copy, so a list would let any caller rewrite the cache in place - and every later
    month is built from it.  A tuple makes that assignment a ``TypeError`` instead.  A
    compiled cell holds no tuple, so the C step restructures this cell, the Space
    docstring says how.

    Outside cover the vector is all zeros: before issue, and from ``t = proj_len()`` on,
    since every claim in payment terminates at the policy end date, the end of the
    frame's last month, without value, so there is no run-off tail for the roll-forward to
    reconcile against.
    """
    n = max_dur()
    if not is_active(t):
        return (0.0,) * n
    if t == t_entry():
        if duration_mth_init() <= 0:
            return (0.0,) * n
        count = pols_if_init()
        return tuple(count * pols_sick_dur_init(z) for z in range(1, n + 1))
    prev = sick_cohorts(t - 1)
    surv = claim_rate_vectors()[2]
    return (pols_inception(t - 1),) + tuple(
        prev[z - 1] * surv[z - 1] for z in range(1, n))


def pols_sick_dur(t, z):
    """l_S(t, z): the population in claim at the start of month t at duration z.

    ``z`` is the 1-based claim-duration cohort index; ``z - 1`` is its list position.
    """
    v = sick_cohorts(t)
    return v[z - 1] if 1 <= z <= len(v) else 0.0


def pols_sick(t):
    """l_S(t): the total population in claim payment at the start of month t."""
    return sum(sick_cohorts(t))


def pols_sick_surv(t):
    """The population still in claim at the **end** of month t, before new inceptions.

    ``sum over z of l_S(t, z) s_S(z)``, which is ``l_S(t + 1) - n(t)``.  This is what
    the benefit is paid on: the benefit is monthly in arrears, so a claim incepting at
    the end of month t is not paid until the end of month ``t + 1``.  Zero outside cover.
    """
    if not is_active(t):
        return 0.0
    v = sick_cohorts(t)
    surv = claim_rate_vectors()[2]
    return sum(a * b for a, b in zip(v, surv) if a != 0.0)


def pols_recovery(t):
    """rec(t): recoveries out of state S at the end of month t.

    ``sum over z of l_S(t, z) rho_m(z)``.  Where they go depends on
    :func:`recovery_basis`.  Zero outside cover.
    """
    if not is_active(t):
        return 0.0
    v = sick_cohorts(t)
    rec = claim_rate_vectors()[0]
    return sum(a * b for a, b in zip(v, rec) if a != 0.0)


def pols_death_sick(t):
    """dth_S(t): deaths in claim at the end of month t.

    ``sum over z of l_S(t, z)(1 - rho_m(z)) q_S_m(z)`` - recovery first, then death
    among the non-recovered.  Zero outside cover.
    """
    if not is_active(t):
        return 0.0
    v = sick_cohorts(t)
    rec, dth, _ = claim_rate_vectors()
    return sum(a * (1.0 - r) * d
               for a, r, d in zip(v, rec, dth) if a != 0.0)


def pols_exit(t):
    """Recoveries that leave the model at the end of month t.

    Equal to :func:`pols_recovery` on the ``exit`` recovery basis and zero on
    ``return_to_h``, where the same lives reappear in :func:`pols_active`.  It exists so
    that the population identity closes on both bases.
    """
    return pols_recovery(t) if recovery_basis() == "exit" else 0.0


def pols_active(t):
    """l_H(t): the population in state H at the start of month t.

    At :func:`t_entry` it is the opening state: :func:`pols_if_init` times the healthy
    share, :func:`pols_active_init`, on a point in force, and on any other point the
    month's new business, :func:`pols_new_biz`, which enters healthy, the book empty
    before it.  Then the notes' state update from the previous month: survivors of
    mortality, lapse and inception, plus that month's recoveries where the recovery basis
    returns them.  One cell a month, reading no month before :func:`t_entry`.  Zero
    outside cover: before issue, and from ``t = proj_len()`` on, once cover has ceased.
    """
    if not is_active(t):
        return 0.0
    if t == t_entry():
        return pols_if_init() * pols_active_init() + pols_new_biz(t)
    prev = pols_active(t - 1)
    stay = (prev * (1.0 - mort_rate_mth(t - 1)) * (1.0 - lapse_rate_mth(t - 1))
            * (1.0 - inception_rate_mth(t - 1)))
    back = 0.0 if recovery_basis() == "exit" else pols_recovery(t - 1)
    return stay + back


def pols_death_active(t):
    """dth_H(t): deaths out of state H at the end of month t.

    The notes' processing order out of H is **death, then lapse, then inception among
    the survivors** **[std]**.  Zero outside cover, before any rate is read.
    """
    if not is_active(t):
        return 0.0
    return pols_active(t) * mort_rate_mth(t)


def pols_lapse(t):
    """lps(t): lapses out of state H at the end of month t.

    Taken from the survivors of mortality.  Pays nothing: the contract has no cash-in
    value at any time [S4][S5][S7].  Lives in claim never lapse.  Zero outside cover,
    before any rate is read.
    """
    if not is_active(t):
        return 0.0
    return pols_active(t) * (1.0 - mort_rate_mth(t)) * lapse_rate_mth(t)


def pols_inception(t):
    """n(t): new claim inceptions at the end of month t, seeding cohort z = 1.

    Taken from the survivors of both mortality and lapse.  Each inception starts a new
    duration cohort, and is not paid until the end of the following month.  Zero outside
    cover, before any rate is read.
    """
    if not is_active(t):
        return 0.0
    return (pols_active(t) * (1.0 - mort_rate_mth(t))
            * (1.0 - lapse_rate_mth(t)) * inception_rate_mth(t))


def pols_new_biz(t):
    """The number of policies issued in month t: ``policy_count()`` in the issue month.

    The issue month is the one with ``duration_mth(t) == 0``: ``t = 0`` for a point
    issued at the valuation date, ``t = k`` for one issued ``k`` months later.  A point
    already in force at the valuation date has none.  Every policy issued starts in state
    H, healthy.
    """
    return policy_count() if duration_mth(t) == 0 else 0.0


def pols_if(t):
    """The number of policies in force at the start of month t: H plus S.

    The row's weight, ``pols_if_at(t, "BEF_DECR")``: the count carried in from month t - 1
    plus month t's new business, before month t's transitions.  The weight on the
    maintenance expense, and the count a reader of ``result_cf()`` reconciles the rest of
    the row against.  Note that it is **not** the weight on premium income, which comes
    from :func:`pols_active` alone because premiums are waived in claim.  Zero outside
    cover.
    """
    return pols_active(t) + pols_sick(t)


def pols_if_at(t, timing):
    """The number of policies in force at a point inside month t.

    ``"BEF_NB"``
        the count carried in from month t - 1, before month t's new business:
        :func:`pols_if` less :func:`pols_new_biz`, exactly, since new business
        enters only in the issue month, on an empty book.  At :func:`t_entry` on
        a point in force it is the opening population, ``pols_if_init()`` split
        between the states.

    ``"BEF_DECR"``
        the start of the month, before any transition; the same number as
        :func:`pols_if`.

    ``"AFT_DECR"``
        the end of the month, once deaths, lapses, recoveries leaving the
        model and - in the last month - the expiry have been taken: ``"BEF_NB"``
        at t + 1, which counts no new business of that month, and zero in the
        last month before the policy end date, ``duration_mth(t) =
        expiry_mth() - 1``, and outside cover.

    ``"BEF_NB"`` is the one timing running in force adds, as ``basiclife.BasicTerm_SE``
    names it; the other two are :mod:`~.IP_UK_S`'s, and any other raises.  The
    intermediate points of the other models have no single-population meaning here,
    because two states are moving at once; :func:`pols_active` and :func:`pols_sick`
    expose them instead.
    """
    if timing == "BEF_NB":
        return pols_if(t) - pols_new_biz(t)
    if timing == "BEF_DECR":
        return pols_if(t)
    if timing == "AFT_DECR":
        if not is_active(t) or duration_mth(t) >= expiry_mth() - 1:
            return 0.0
        return pols_if_at(t + 1, "BEF_NB")
    raise ValueError("invalid timing")


def pols_maturity(t):
    """The population still in force when cover ceases at the policy end date.

    Non-zero only in the last covered month, ``duration_mth(t) = expiry_mth() - 1`` on the
    policy clock, the frame's last row ``t = proj_len() - 1``, at whose end all cover and
    any claim in payment terminate without value [S1][S3][S5][S7][S10].  Not a decrement
    and not a benefit - but without it the last month appears to lose lives with no
    cause, and :func:`check_pols_roll_fwd` would not close.
    """
    if duration_mth(t) != expiry_mth() - 1:
        return 0.0
    stay = (pols_active(t) * (1.0 - mort_rate_mth(t))
            * (1.0 - lapse_rate_mth(t)) * (1.0 - inception_rate_mth(t)))
    back = 0.0 if recovery_basis() == "exit" else pols_recovery(t)
    return stay + back + pols_inception(t) + pols_sick_surv(t)


def pols_dead_cum(t):
    """Cumulative deaths, from both states, from :func:`t_entry` to the start of month t.

    0 at :func:`t_entry`: the count restarts there, on the count on the books, as
    :func:`check_states_resid`, the one cell that reads it, restates the population
    identity.  :mod:`~.IP_UK_S` counts from its frame's start, the issue month on new
    business.  One cell a month.  Zero outside cover.
    """
    if not is_active(t) or t == t_entry():
        return 0.0
    return pols_dead_cum(t - 1) + pols_death_active(t - 1) + pols_death_sick(t - 1)


def pols_lapse_cum(t):
    """Cumulative lapses out of state H from :func:`t_entry` to the start of month t.

    0 at :func:`t_entry`, as :func:`pols_dead_cum` is.  Zero outside cover.
    """
    if not is_active(t) or t == t_entry():
        return 0.0
    return pols_lapse_cum(t - 1) + pols_lapse(t - 1)


def pols_exit_cum(t):
    """Cumulative recoveries that left the model from :func:`t_entry` to the start of month t.

    0 at :func:`t_entry`, as :func:`pols_dead_cum` is, and zero throughout on the
    ``return_to_h`` basis, where recoveries never leave.  Zero outside cover.
    """
    if not is_active(t) or t == t_entry():
        return 0.0
    return pols_exit_cum(t - 1) + pols_exit(t - 1)


def inflation_factor(t):
    """The expense inflation factor in month t, ``(1 + pi)^(t // 12)`` **[std]**.

    On the **valuation** clock: ``t`` counts months from the valuation date, so the
    expense loads it inflates are in valuation-date pounds, whatever the policy's age,
    and every point of a block inflates alike, stepping on each anniversary of the
    valuation date.  :mod:`~.IP_UK_S` inflates from its frame's start,
    ``(1 + pi)^(y - 1)``, as the notes write it; on a point issued at ``t = 0``, and on
    the twin of an ``in_claim`` cell of :mod:`~.IP_UK_S`, which restarts its policy clock
    at the valuation date, the two are the same.  :func:`proj_len` holds
    ``inflation_rate`` to a finite number, -1 or more, so the factor is a number, 0 or
    more.  A factor past the largest float, which only an ``inflation_rate`` past every
    rate of inflation makes, is refused in the month it first is, naming the point and the
    Reference: Python's power raises ``OverflowError`` there, naming neither, and C's gives
    an infinity.
    """
    try:
        factor = (1.0 + inflation_rate) ** (t // 12)                 # noqa: F821
    except OverflowError:
        raise ValueError(
            f"point_id {point_id}: the inflation factor inflation_factor({t}) is past the "  # noqa: F821
            f"largest float, under inflation_rate {float(inflation_rate)}") from None  # noqa: F821
    if not factor <= 1.7976931348623157e308:
        raise ValueError(
            f"point_id {point_id}: the inflation factor inflation_factor({t}) is past the "  # noqa: F821
            f"largest float, under inflation_rate {float(inflation_rate)}")  # noqa: F821
    return factor


def premiums(t):
    """PREM(t): premium income at the beginning of month t, an inflow.

    Carried on :func:`pols_active` and **never** on :func:`pols_if`.  Premiums are
    waived from the start of benefit payment [S5][S7][S10][S11], so projecting income
    from lives in claim overstates it by the whole in-claim population - the notes'
    second-listed pitfall.  Lives sick but still inside the deferred period do pay, and
    they are in H, so they are counted correctly without a state of their own.  Income
    that leaves the floats raises ``ValueError`` in the month it first does, naming the
    point.
    """
    v = premium_pp(t) * pols_active(t)
    if not v - v == 0.0:
        raise ValueError(
            f"point_id {point_id}: the premiums premiums({t}) are {v}, not a finite "  # noqa: F821
            f"number, from premium_pp({t}) {premium_pp(t)} on pols_active({t}) "
            f"{pols_active(t)} healthy lives")
    return v


def claims(t, kind=None):
    """Benefit outgo in month t, by kind; the total when kind is omitted.

    ``"BENEFIT"``
        ``k x AP(y) x`` :func:`pols_sick_surv`, the monthly income benefit,
        paid in arrears at the end of the month to lives in claim throughout
        it.  New inceptions are excluded: a claim incepting at the end of
        month t is not paid until the end of month ``t + 1``.

    ``"DEATH"``
        zero.  This composite carries no death benefit; the £5,000-£10,000
        death benefits two sampled insurers offer are out of scope, and would
        add a ``deaths x DB`` term here.

    ``"LAPSE"``
        zero.  There is no cash-in value at any time [S4][S5][S7].

    The two zero kinds are published rather than omitted so that the product facts are
    stated instead of inferred from a missing column.  The benefit is zero outside cover.
    The total is :mod:`~.IP_UK_S`'s ``sum`` over the three kinds.  Outgo that leaves the
    floats, of a kind or in total, raises ``ValueError`` in the month it first does,
    naming the point.
    """
    if kind is None:
        v = sum(claims(t, k) for k in ("BENEFIT", "DEATH", "LAPSE"))
    elif kind == "BENEFIT":
        if not is_active(t):
            return 0.0
        v = claim_severity * amount_payable_pp(t) * pols_sick_surv(t)  # noqa: F821
    elif kind in ("DEATH", "LAPSE"):
        return 0.0
    else:
        raise ValueError("invalid kind")
    if not v - v == 0.0:
        raise ValueError(
            f"point_id {point_id}: the claims claims({t}, {kind}) are {v}, not a finite "  # noqa: F821
            f"number, from amount_payable_pp({t}) {amount_payable_pp(t)} on "
            f"pols_sick_surv({t}) {pols_sick_surv(t)} lives in claim")
    return v


def expenses(t):
    """EXP(t): maintenance and claim-management expense in month t **[std]**.

    £60 per policy a year on every policy in force, plus £300 a year on every claim in
    payment, both a twelfth at a time and both inflating at 3%, from the valuation date.
    The claim-management load is what makes a long claim expensive to administer as well
    as to pay.  Expenses that leave the floats raise ``ValueError`` in the month they first
    do, naming the point and the References that make them: an expense and an inflation
    rate each in its domain can, as an expense of 1.7e308 inflated at 100% a year does at
    ``t = 12``.
    """
    maint = expense_maint / 12.0 * inflation_factor(t) * pols_if(t)   # noqa: F821
    claim_mgmt = (expense_claim / 12.0 * inflation_factor(t)          # noqa: F821
                  * pols_sick(t))
    v = maint + claim_mgmt
    if not v - v == 0.0:
        raise ValueError(
            f"point_id {point_id}: the expenses expenses({t}) are {v}, not a finite "  # noqa: F821
            f"number, from expense_maint {float(expense_maint)}, expense_claim "  # noqa: F821
            f"{float(expense_claim)} and inflation_rate {float(inflation_rate)}, on "  # noqa: F821
            f"pols_if({t}) {pols_if(t)} policies, pols_sick({t}) {pols_sick(t)} in claim")
    return v


def net_cf(t):
    """CF(t) = PREM(t) - BEN(t) - EXP(t): the net cash flow of month t, income positive.

    The notes' own sign, and the library-wide one, so there is no outgo-positive
    ``liability_cf`` companion.  Death and lapse generate no payment at all on this
    product.  Each flow is a finite number, its cell refusing one that is not, but their
    sum can leave the floats, which raises ``ValueError`` here, naming the point and the
    flows.
    """
    v = premiums(t) - claims(t) - expenses(t)
    if not v - v == 0.0:
        raise ValueError(
            f"point_id {point_id}: the net cash flow net_cf({t}) is {v}, not a finite "  # noqa: F821
            f"number, from premiums {premiums(t)}, claims {claims(t)} and expenses "
            f"{expenses(t)}")
    return v


def disc_factor(t):
    """v(t) = (1 + i)^(-(t + 1)/12): the worked example's flat discount factor **[std]**.

    The discount factor to the **end** of month t, time ``t + 1``, which is when the
    benefit of month t is paid; ``disc_factor(0)`` is one month's discount.  On the
    valuation clock, from the valuation date, as :mod:`~.IP_UK_S` discounts from its
    frame's start.

    A **companion to** the cash flow projection, not part of it: no line of
    :func:`result_cf` is discounted, and every other model in this library projects
    undiscounted gross cash flows and leaves discounting to the layer that consumes them.
    It exists because the notes' worked example is a present value and because the
    disabled-life annuity is the object a claims-in-payment reserve is quoted as.  A
    Solvency UK best estimate discounts these same cash flows on the PRA risk-free term
    structure instead of a flat 3%.  :func:`proj_len` holds ``disc_rate`` to a finite
    number above -1, so the factor is a number above 0; one past the largest float, which
    only a rate within a hair of -1 makes, is refused where it first is, naming the point
    and the Reference, where Python's power raises ``OverflowError``, naming neither.
    """
    try:
        factor = (1.0 + disc_rate) ** (-(t + 1) / 12.0)              # noqa: F821
    except OverflowError:
        raise ValueError(
            f"point_id {point_id}: the discount factor disc_factor({t}) is past the "  # noqa: F821
            f"largest float, under disc_rate {float(disc_rate)}") from None  # noqa: F821
    if not factor <= 1.7976931348623157e308:
        raise ValueError(
            f"point_id {point_id}: the discount factor disc_factor({t}) is past the "  # noqa: F821
            f"largest float, under disc_rate {float(disc_rate)}")    # noqa: F821
    return factor


def pv_benefits():
    """The present value at the valuation date of benefit outgo over the frame, at ``disc_rate``.

    On a point in claim run on the ``exit`` recovery basis this is the claims-in-payment
    liability the notes value.  See :func:`disc_factor` for why discounting appears in
    this model and nowhere else in the library.  A point issued after the valuation date
    pays nothing before issue, so its value is discounted to the valuation date too.  A
    value that leaves the floats, a sum of finite terms, raises ``ValueError``, naming the
    point.
    """
    v = sum(claims(t, "BENEFIT") * disc_factor(t) for t in range(proj_len()))
    if not v - v == 0.0:
        raise ValueError(
            f"point_id {point_id}: the present value pv_benefits() is {v}, not a finite "  # noqa: F821
            f"number, at disc_rate {float(disc_rate)}")              # noqa: F821
    return v


def annuity_dis():
    """a_dis: the disabled-life annuity factor per £1 a month of amount payable, per policy.

    ``pv_benefits() / (AP x policy_count())``, where ``AP`` is
    ``amount_payable_pp(t_entry())``, the amount payable in the month the point is first
    on the books, at the valuation date on a point in force, which on a policy in claim
    run on the ``exit`` basis is the notes' ``a_dis(a0, z0)`` exactly: the expected present
    value of the escalating benefit until recovery, death or expiry, truncated at the
    policy end date.  :mod:`~.IP_UK_S` divides by ``amount_payable_pp(0)``, its frame's
    first month, alone: on its points, each of one policy, the same number.  Here a point
    stands for ``policy_count()`` policies, so the factor is per policy on the books, as
    an amount per policy is, and the count is the one weight on :func:`pv_benefits`.  On a
    point all healthy the same expression is the inception-annuity decomposition of the
    active-lives projection - the value of all *future* claims per unit of benefit - and is
    a different object with the same units.  Where that amount payable or the count is 0,
    a benefit or an ``ap_ratio`` of 0 or a point of no policies, the factor has no value,
    and this raises ``ValueError``, naming the point, rather than divide by zero.
    """
    per = amount_payable_pp(t_entry()) * policy_count()
    if per == 0.0:
        raise ValueError(
            f"point_id {point_id}: the annuity factor annuity_dis() has no value: the "  # noqa: F821
            f"amount payable it is per, amount_payable_pp({t_entry()}) "
            f"{amount_payable_pp(t_entry())} on policy_count {policy_count()} policies, "
            f"is 0")
    return pv_benefits() / per


def check_pols_roll_fwd_resid(t):
    """The in-force roll-forward residual in month t; zero everywhere.

    ``pols_if(t)`` less the count carried into ``t + 1``, ``pols_if_at(t + 1, "BEF_NB")``,
    which counts none of that month's new business, less deaths from both states, lapses,
    recoveries leaving the model and the expiry.  Inceptions and returning recoveries are
    absent because they move lives *between* states rather than out of the policy count -
    which is the point of running the check on ``H + S`` rather than on either state
    alone.
    """
    return (pols_if(t) - pols_if_at(t + 1, "BEF_NB")
            - pols_death_active(t) - pols_death_sick(t) - pols_lapse(t)
            - pols_exit(t) - pols_maturity(t))


def check_pols_roll_fwd():
    """True when the in-force roll-forward closes in every month of the frame.

    The library-wide form of a roll-forward check: no argument, one bool over all t, so
    one test can call it across every model.  :func:`check_pols_roll_fwd_resid` gives
    the signed residual of the month that failed.  The tolerance scales with the policies
    on the books, ``policy_count()``, in force at the valuation date or issued after it,
    since the residual accumulates rounding on that many policies; :mod:`~.IP_UK_S`'s
    ``pols_if_init()`` is 0 here on a point issued at or after the valuation date.
    """
    return all(abs(check_pols_roll_fwd_resid(t)) <= 1e-10 * max(policy_count(), 1.0)
               for t in range(proj_len()))


def check_states_resid(t):
    """The three-state population identity residual at the start of month t; zero.

    ``H + S + cumulative deaths + cumulative lapses + cumulative exits`` must equal the
    population on the books in every month: the cumulative counts run from
    :func:`t_entry`, so the identity is restated on the count on the books from then,
    ``policy_count()``, in force at the valuation date or issued, and 0 outside cover,
    before issue and from the policy end date, where every count is 0.  On a point in
    force the opening healthy share and cohort shares sum to 1 within 1e-10, which
    ``Data`` checks, so the identity holds from month 0.  This is the check that catches a
    leak in the cohort machinery: a mis-indexed duration shift drops population out of S
    with no corresponding exit, and nothing else in the model would notice.
    """
    books = policy_count() if is_active(t) else 0.0
    return (pols_active(t) + pols_sick(t) + pols_dead_cum(t)
            + pols_lapse_cum(t) + pols_exit_cum(t) - books)


def check_states():
    """True when the three-state population identity holds in every month of the frame.

    No argument, one bool over all t, the library-wide shape of a ``check_*`` cells;
    :func:`check_states_resid` gives the signed residual of the month that failed.  The
    tolerance scales with the policies on the books, ``policy_count()``, as the
    roll-forward's does.
    """
    return all(abs(check_states_resid(t)) <= 1e-10 * max(policy_count(), 1.0)
               for t in range(proj_len()))


def check_benefit_max():
    """True when the chosen benefit is inside the contractual maximum.

    ``B(1) <= benefit_max_pp() / tolerance``, the two-band earnings formula with the 90%
    tolerance that stops a small fall in earnings cutting an in-force benefit
    [S1][S2][S5][S7].  Unlike the other two checks this is a **validation of the model
    point** rather than an identity of the projection: a benefit above the maximum is a
    policy that could not have been written, and the underwriting record is on the model
    point precisely so that it can be checked.  It reads the benefit chosen at issue and
    the earnings underwritten then, on a point in force as on new business.
    """
    return benefit_mth() <= benefit_max_pp() / ben_tolerance + 1e-9   # noqa: F821


def result_cf():
    """Result table of cashflows, one row per month ``t = 0 .. proj_len() - 1``.

    Row 0 is the valuation month for every model point, so the frames of a block line up
    and sum row by row.  A point issued after the valuation date has zeros until its issue
    month.  ``pols_if`` is H plus S at the start of the month.  ``pols_active`` is
    published beside it because it, and not ``pols_if``, is the weight on premium income -
    the difference between the two columns is the population whose premiums are waived.
    The columns are :mod:`~.IP_UK_S`'s.  Nothing here is discounted; see
    :func:`disc_factor`.
    """
    ts = list(range(proj_len()))
    return pd.DataFrame(                                             # noqa: F821
        {
            "pols_if": [pols_if(t) for t in ts],
            "pols_active": [pols_active(t) for t in ts],
            "pols_sick": [pols_sick(t) for t in ts],
            "premiums": [premiums(t) for t in ts],
            "claims_benefit": [claims(t, "BENEFIT") for t in ts],
            "claims_death": [claims(t, "DEATH") for t in ts],
            "claims_lapse": [claims(t, "LAPSE") for t in ts],
            "expenses": [expenses(t) for t in ts],
            "net_cf": [net_cf(t) for t in ts],
        },
        index=pd.Index(ts, name="t"),                                # noqa: F821
    )


def result_states():
    """Result table of state movements and rates, one row per month ``t``.

    The same rows as :func:`result_cf`, ``t = 0 .. proj_len() - 1``, and
    :mod:`~.IP_UK_S`'s columns.  The rates are 0 outside cover, where the model reads no
    table: before issue on a point issued after the valuation date.
    """
    ts = list(range(proj_len()))
    return pd.DataFrame(                                             # noqa: F821
        {
            "pols_active": [pols_active(t) for t in ts],
            "pols_sick": [pols_sick(t) for t in ts],
            "pols_inception": [pols_inception(t) for t in ts],
            "pols_recovery": [pols_recovery(t) for t in ts],
            "pols_death_active": [pols_death_active(t) for t in ts],
            "pols_death_sick": [pols_death_sick(t) for t in ts],
            "pols_lapse": [pols_lapse(t) for t in ts],
            "inception_rate": [inception_rate(t) for t in ts],
            "mort_rate": [mort_rate(t) for t in ts],
            "lapse_rate": [lapse_rate(t) for t in ts],
        },
        index=pd.Index(ts, name="t"),                                # noqa: F821
    )


def result_pols():
    """Result table of policy counts and amounts, one row per month t.

    The same rows as :func:`result_cf`, ``t = 0 .. proj_len() - 1``.  First the counts
    :func:`result_cf` weights its rows by, and how they move, as
    ``basiclife.BasicTerm_SE``'s ``result_pols`` sets them out: ``pols_if``, healthy and in
    claim, of month t; ``pols_new_biz``, the part of it issued in month t, all healthy;
    the healthy and the sick counts, ``pols_active`` and ``pols_sick``; then month t's
    movements in the notes' processing order, out of H the deaths, the lapses and the
    inceptions, out of S the recoveries and the deaths in claim, the recoveries that
    leave the model, and the expiry of the last month.  Row by row, ``pols_if`` at
    ``t + 1`` is ``pols_if`` less its deaths in both states, its lapses, its exits and its
    expiry of month t, plus the new business of month ``t + 1``.  Then the amounts per
    policy, the benefit and the premium, which carry the escalation history and no count
    moves.
    """
    ts = list(range(proj_len()))
    return pd.DataFrame(                                             # noqa: F821
        {
            "pols_if": [pols_if(t) for t in ts],
            "pols_new_biz": [pols_new_biz(t) for t in ts],
            "pols_active": [pols_active(t) for t in ts],
            "pols_sick": [pols_sick(t) for t in ts],
            "pols_death_active": [pols_death_active(t) for t in ts],
            "pols_lapse": [pols_lapse(t) for t in ts],
            "pols_inception": [pols_inception(t) for t in ts],
            "pols_recovery": [pols_recovery(t) for t in ts],
            "pols_death_sick": [pols_death_sick(t) for t in ts],
            "pols_exit": [pols_exit(t) for t in ts],
            "pols_maturity": [pols_maturity(t) for t in ts],
            "benefit_pp": [benefit_pp(t) for t in ts],
            "premium_pp": [premium_pp(t) for t in ts],
        },
        index=pd.Index(ts, name="t"),                                # noqa: F821
    )


# ---------------------------------------------------------------------------
# References

data = ("Interface", ("..", "Data"), "auto")

point_id = 1

issue_age_min = 18

issue_age_max = 59

expiry_age_min = 50

expiry_age_max = 70

cycle_factor = 1.0

mort_active_factor = 1.0

ap_ratio = 1.0

claim_severity = 1.0

rpi_rate = 0.03

esc_cap = 0.1

esc_prem_mult = 1.5

esc_lapse_slope = 2.0

esc_lapse_threshold = 0.05

ben_band1_rate = 0.65

ben_band2_rate = 0.5

ben_breakpoint = 60000.0

ben_cap_mth = 20000.0

ben_guarantee_mth = 1500.0

ben_tolerance = 0.9

expense_maint = 60.0

expense_claim = 300.0

inflation_rate = 0.03

disc_rate = 0.03

pd = ("Module", "pandas")
