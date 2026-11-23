# modelx: pseudo-python
# This file is part of a modelx model.
# It can be imported as a Python module, but functions defined herein
# are model formulas and may not be executable as standard Python.

"""In-force reference liability cash flow model for UK pension annuities.

:mod:`~.PA_UK_SEC` projects the contract :mod:`~.PA_UK_S` projects — a UK pension annuity
in payment: instalments to the annuitant and to a dependant, guarantee-period payments,
value-protection lump sums and maintenance expense — from a **valuation date** rather than
from the annuity's start. A model point may be an annuity already in payment at that date,
in any month of its policy year, one starting at it, or one to start in the ten years
after it, as in lifelib's ``basiclife/BasicTerm_SE``, which extends
``basiclife/BasicTerm_S`` the same way, on the payout chassis of the library's
``SPIA_US_SEC``. Its formulas are the executable counterpart of
``products/pension_annuity/technical-notes.md``, and
``products/pension_annuity/model-sec.md`` explains what running in force changes.

**Mortality is the model**, as it is :mod:`~.PA_UK_S`'s. After outset the contract has no
premiums, no surrender value, no account value and no policyholder options at all. The
only decrements are deaths; the only stochastic drivers are longevity and, on the indexed
options, inflation. That is not an omission — it is the design property that makes the
liability eligible for the Solvency UK matching adjustment, whose conditions effectively
require this shape.

**Spaces.** The model contains two:

:mod:`~.PA_UK_SEC.Data`
    Reads the mortality table it shares with :mod:`~.PA_UK_S` and its own model point
    table, and holds their filename References. It takes no parameters, so each file is
    read **once per model**. It checks each table as it reads it.

:mod:`~.PA_UK_SEC.Projection`
    The by-contract projection, parameterized by ``point_id``: ``Projection[1]`` is an
    ItemSpace projecting model point 1. It reaches the input tables through its ``data``
    Reference, which resolves to the single :mod:`~.PA_UK_SEC.Data` Space.

The split matters for more than tidiness. Because ``Projection`` is parameterized,
every ``Projection[N]`` is a separate ItemSpace with its own cells cache; readers
placed there would re-read every file for every contract. In ``Data`` they are evaluated
once, however many contracts are projected.

Input data is **external**: CSVs in the model folder's parent directory, read at run
time rather than stored inside the model. The model folder itself holds no data, so
the model and its inputs must travel together.

**Projection basis.** Monthly steps on two clocks. ``t`` counts months from the
valuation date, 0-based, as ``basiclife/BasicTerm_SE`` counts them: ``t = 0`` is the
valuation month for every model point, however long the annuity has been in payment, and
the frame runs ``t = 0, 1, ..., proj_len() - 1``, where ``proj_len()`` counts the months
from the valuation date to the stop rule. ``duration_mth(t)`` counts the months from the
annuity start date, ``duration_mth_init() + t`` from the model point's ``duration_mth`` at
``t = 0``, and the contract runs on it: the policy year, ``policy_year(t) = duration(t) +
1``, whose anniversaries escalate the income; the attained ages, age last birthday, and
the calendar years, which date the mortality improvement; the payment months; the
guarantee; the overlap gate. Expense inflation alone runs on ``t``, stepping on each
anniversary of the valuation date, so the maintenance charge is in valuation-date pounds.
Survival, the expected payments to date and the value-protection balance are time points
on the valuation clock; the annuitant's scheduled payments to date are time points on the
policy clock. The projection stops one month before the youngest covered life would reach
the limiting age, 115, or at the end of the guarantee if that is later, as from the start.

On a point starting at the valuation date the two clocks coincide, and the model computes
what :mod:`~.PA_UK_S` computes, except that ``pols_if_init()`` is the count already in
payment at the valuation date, 0 for such a point, whose contracts enter as new business at
``t = 0``. The count on the books is never decremented: mortality decrements each life's
survival, and ``pols_if`` is :mod:`~.PA_UK_S`'s closing obligation measure on that count.

**In force.** A contract in payment carries, beside its count, the state
:mod:`~.PA_UK_S` carries into the month it is valued at, each per contract and measured at
the valuation instant: each covered life's survival; the payments made to date on every
stream; and on RPI-linked escalation the income of the policy year under way, the
ratchet's peak over the latest index, and the annuitant's payments to date where value
protection is on the first death. Each is history, which no assumption changed at the
valuation date reaches back to: ``rpi_rate`` is the RPI from the valuation date on.
``result_pols()`` sets out the counts and the survival behind them, month by month.

**What is sourced and what is not.** The contractual mechanics are sourced: the
instalment formula, the four escalation bases and the RPI catch-up ratchet, the
dependant's percentage and the overlap rule, the guarantee period as an annuity-certain
floor, value protection and its exclusivity with the guarantee, the ``v + delta <= 1``
bound, and the absence of any surrender value. Every rate is a standardization. The SAPS
and PMA16/PFA16 annuitant tables are restricted to CMI Authorised Users and the CMI
projections model software with them, so the mortality basis shipped here is a **[std]**
proxy, and no insurer publishes an annuity rate card, so the starting income is a model
point input. **This model is a mechanics demonstration, not a pricing or reserving
result.** Replace the basis with licensed tables before drawing any conclusion from the
output.

**Model points.** ``model_point_table_sec.csv`` is generated from :mod:`~.PA_UK_S` and its
model point table, and the tests regenerate it and compare, so no row is typed by hand.
Points 1 to 10 are the twins of :mod:`~.PA_UK_S`'s ten points, starting at the valuation
date. Points 11 to 19 are S points restated in payment, each opened with the state S
carries into its month: the worked example the month after the annuitant's death; the
proportionate payment's point in the month of the death; the guarantee's point at its end;
the LPI point on its second anniversary; the RPI catch-up point mid-year; the first-death
value protection in its last month with a balance; the last-survivor value protection
likewise; the rated single life the month before its mortality cap binds; and the table
basis's joint point in its last month. Point 20 is the RPI catch-up point starting 13
months after the valuation date. Points 21 and 22 are restated from S run under an RPI of
its own: the catch-up point under an RPI of -2%, its income frozen and its peak above the
index, and the LPI point under 8%, its increases capped at 5%; histories no state S reaches
at its shipped RPI holds.

**Verification.** On the ten twins every cell this model shares with :mod:`~.PA_UK_S`
agrees with it at every argument the S model evaluates in its sweep, ``pols_if_init`` and
``model_point`` excepted, so the worked example ``tests/test_pension_annuity_uk.py``
asserts to the penny holds here too, with no number restated.
``tests/test_pension_annuity_uk_sec.py`` splices: an S point restated in payment at month
``d`` continues the S projection from ``d`` on, cell by cell, at months about the payment
dates, the anniversaries, the scenario death, the guarantee's end, value protection running
out and the mortality cap, under RPI rates that bind the LPI cap and floor and freeze the
ratchet, and on variants of S's points that reach what S's own cannot. A point starting
``k`` months late is the S projection ``k`` months on.

Example:

    >>> import modelx as mx
    >>> model = mx.read_model("products/pension_annuity/PA_UK_SEC")
    >>> model.Projection[11].result_cf()     # the worked example in payment 17 months
    >>> model.Projection[11].result_pols()
"""

from modelx.serialize.jsonvalues import *

_name = "PA_UK_SEC"

_allow_none = False

_spaces = [
    "Data",
    "Projection"
]
