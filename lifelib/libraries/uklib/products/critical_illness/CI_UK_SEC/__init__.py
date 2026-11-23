# modelx: pseudo-python
# This file is part of a modelx model.
# It can be imported as a Python module, but functions defined herein
# are model formulas and may not be executable as standard Python.

"""In-force reference liability cash flow model for UK critical illness cover.

:mod:`~.CI_UK_SEC` projects the policy :mod:`~.CI_UK_S` projects — UK critical illness
cover: an **accelerated** life-or-CI contract paying the sum assured on the first of
death, terminal illness or diagnosis of a listed condition, with non-terminating
**additional-payment** and **children's-cover** benefits alongside it, a **standalone**
variant on which death pays nothing, a 5-yearly **reviewable** premium variant and an
optional RPI indexation option — from a **valuation date** rather than from issue. A model
point may be a policy already in force at that date, in any month of its policy year, one
issued at it, or one to be issued in the ten years after it, as in lifelib's
``basiclife/BasicTerm_SE``, which extends ``basiclife/BasicTerm_S`` the same way. Its
formulas are the executable counterpart of ``products/critical_illness/technical-notes.md``,
and ``products/critical_illness/model-sec.md`` explains what running in force changes.

The product sits on the term assurance chassis specified in ``products/term_assurance/``
and implemented as :mod:`.Term_UK_S`, and its notes state only the CI-specific deltas, as
this model runs in force on :mod:`.Term_UK_SEC`'s chassis. Two of those deltas change the
model rather than a parameter, and both are the notes' own first-listed pitfalls:

* the insured event is *death or first CI diagnosis, whichever first*, so the two rates
  cannot simply be added — the combined decrement nets out an overlap factor ``k``; and
* the additional-payment and children's benefits are **non-depleting and
  non-terminating**: they neither reduce the sum assured nor decrement the in-force.

**Spaces.** The model contains two:

:mod:`~.CI_UK_SEC.Data`
    Reads the two assumption CSVs it shares with :mod:`~.CI_UK_S` and its own model point
    table, and holds their filename References. It takes no parameters, so each file is
    read **once per model**. It checks each table before a value of it is read.

:mod:`~.CI_UK_SEC.Projection`
    The by-policy projection, parameterized by ``point_id``: ``Projection[1]`` is an
    ItemSpace projecting model point 1. It reaches the input tables through its ``data``
    Reference, which resolves to the single :mod:`~.CI_UK_SEC.Data` Space.

The split matters for more than tidiness. Because ``Projection`` is parameterized,
every ``Projection[N]`` is a separate ItemSpace with its own cells cache; readers
placed there would re-read every file for every policy. In ``Data`` they are evaluated
once, however many policies are projected.

Input data is **external**: CSVs in the model folder's parent directory, read at run
time rather than stored inside the model. The model folder itself holds no data, so
the model and its inputs must travel together.

**Projection basis.** Monthly steps on two clocks. ``t`` counts months from the
valuation date, 0-based, as ``basiclife/BasicTerm_SE`` counts them: ``t = 0`` is the
valuation month for every model point, however old the policy, and the frame runs
``t = 0, 1, ..., proj_len() - 1``, where ``proj_len()`` counts the months from the
valuation date to the end of the term. ``duration_mth(t)`` counts the months the policy
has been in force, ``duration_mth_init() + t`` from the model point's ``duration_mth`` at
``t = 0``, and the contract runs on it: the completed policy years are
``duration(t) = duration_mth(t) // 12``, the contractual 1-based label is
``policy_year(t) = duration(t) + 1``, the lapse table's key, and the attained age is
``age_at_entry(life) + duration(t)``, the pivot table's. The RPI increase falls on each
policy anniversary, the premium reviews every 60 policy months from the fifth anniversary,
and the shock lapse in the twelve policy months after a review. Expense inflation and the
morbidity trend run on ``t``, stepping on each anniversary of the valuation date, so the
maintenance charge is in valuation-date pounds and the diagnosis basis is trended from
the date it is stated at; the initial expense is charged per policy issued, in the issue
month, uninflated, as in ``basiclife/BasicTerm_SE``. On a point issued at ``t = 0`` the
two clocks coincide, and the model computes what :mod:`~.CI_UK_S` computes, except that
``pols_if_init()`` is the count already in force at the valuation date, 0 for such a
point, whose policies enter as new business at ``t = 0``.

Premiums and maintenance expense fall at the beginning of the month; claims and
decrements at the end; lapses act on non-claiming survivors, claim before lapse. Cover
expires at the end of the last month with no maturity or surrender value.

**In force.** A point in force carries, beside its count, the facts of its contract that
:mod:`~.CI_UK_S` would recompute from flat References, each measured at the valuation
instant: the RPI indexation factors already given, on the cover and on the premium; the
premium factor the reviews already made have given; the select latch, the anti-selection
factor on the diagnosis rate once a review has shocked lapses; and the premium change the
last review made, which sets the shock lapse while its window is still running. Each is
history, which no Reference changed at the valuation date reaches back to.
``result_pols()`` sets out the counts: in force, new business and each decrement, month by
month.

**What is sourced and what is not.** The benefit structure is sourced: the accelerated
design, the additional-payment benefit at ``min(25% of SA, £25,000)``, children's cover
at ``min(50% of SA, £25,000)``, both non-depleting, the 14-day survival period, the
absence of any surrender value, the 5-yearly review cycle of the reviewable variant, and
the product's limits on terms and ages. Every rate is a standardization. The CMI's
accelerated-CI diagnosis tables (AC04, the "16" Series) are restricted to subscribers, so
the diagnosis and mortality rates shipped here are **[std]** proxies shaped like those
tables and no more, and the £55 monthly premium is a placeholder — no UK insurer publishes
CI rate cards. **This model is a mechanics demonstration, not a pricing or reserving
result.** Profitability conclusions drawn from it are meaningless; replace the basis with
licensed tables and company data first.

**Model points.** ``model_point_table_sec.csv`` is generated from :mod:`~.CI_UK_S` and
its model point table, and the tests regenerate it and compare, so no row is typed by
hand. Points 1 to 7 are the twins of :mod:`~.CI_UK_S`'s seven, issued at the valuation
date: the anchor cell, the standalone variant, the reviewable variant, an indexed policy,
one without children's cover, a female smoker on a shorter term, and a joint first-event
policy. Points 8 to 12 are S points restated in force, each opened with the state S
carries into its month: the indexed point on its third anniversary, the reviewable point
on its first review, inside the review's shock window and mid-year after it, and the
anchor cell in its last covered month. Point 13 is the indexed point issued 13 months
after the valuation date.

**Verification.** On the seven twins every cell this model shares with :mod:`~.CI_UK_S`
agrees with it at every argument the S model evaluates in its sweep, ``pols_if_init`` and
``model_point`` excepted, so the worked example ``tests/test_critical_illness_uk.py``
asserts — money to the penny, in-force to six decimals — holds here too, with no number
restated. ``tests/test_critical_illness_uk_sec.py`` splices: an S point restated in force
at month ``d`` continues the S projection from ``d`` on, cell by cell, at months about the
first anniversary, the first and second reviews and the shock window's end, and the end of
the term, with the premium reviews raising premiums past the shock threshold, and on
variants of S's points that reach what S's own cannot. A point issued ``k`` months late is
the S projection ``k`` months on.

Example:

    >>> import modelx as mx
    >>> model = mx.read_model("products/critical_illness/CI_UK_SEC")
    >>> model.Projection[9].result_cf()      # the reviewable point on its first review
    >>> model.Projection[9].result_pols()
"""

from modelx.serialize.jsonvalues import *

_name = "CI_UK_SEC"

_allow_none = False

_spaces = [
    "Data",
    "Projection"
]
