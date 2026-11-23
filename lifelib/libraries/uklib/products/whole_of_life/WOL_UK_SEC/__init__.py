# modelx: pseudo-python
# This file is part of a modelx model.
# It can be imported as a Python module, but functions defined herein
# are model formulas and may not be executable as standard Python.

"""In-force reference liability cash flow model for UK whole of life assurance.

:mod:`~.WOL_UK_SEC` projects the policies :mod:`~.WOL_UK_S` projects — UK guaranteed whole
of life assurance, in the two cells ``products/whole_of_life/technical-notes.md`` specifies
— from a **valuation date** rather than from issue. A model point may be a policy already
in force at that date, in any month of its policy year, on full cover or paid-up, one
issued at it, or one to be issued in the ten years after it, as in lifelib's
``basiclife/BasicTerm_SE``, which extends ``basiclife/BasicTerm_S`` the same way. Its
formulas are the executable counterpart of those notes, and
``products/whole_of_life/model-sec.md`` explains what running in force changes.

The two cells share one engine:

**RefWOL-UW** — underwritten guaranteed whole of life. Full underwriting, guaranteed
level premiums payable for life, the sum assured paid once on death or earlier terminal
illness, suicide inside twelve months refunding premiums instead.

**RefWOL-O50** — over-50s guaranteed acceptance. No underwriting at all, a fixed cash
sum, a **twelve-month moratorium** during which non-accidental death returns the
premiums paid rather than the cash sum, premiums ceasing at the anniversary on or after
the 90th birthday while cover continues, and a **crossover** past which cumulative
premiums exceed the cash sum.

**Neither cell has an account value, a unit fund or a surrender value.** Both are pure
decrement protection models: premiums in, death benefits and expenses out, weighted by
survivorship, and **every lapse extinguishes a liability for nothing**. One plan's
*pro-rata paid-up value* variant [S9] converts late lapses into paid-up liabilities
instead, so a policy in force may be paid-up, which is why this model carries two counts.

**Spaces.** The model contains two:

:mod:`~.WOL_UK_SEC.Data`
    Reads the two assumption CSVs it shares with :mod:`~.WOL_UK_S` and its own model
    point table, and holds their filename References. It takes no parameters, so each
    file is read **once per model**. It checks each table before a value of it is read.

:mod:`~.WOL_UK_SEC.Projection`
    The by-policy projection, parameterized by ``point_id``: ``Projection[1]`` is an
    ItemSpace projecting model point 1. It reaches the input tables through its ``data``
    Reference, which resolves to the single :mod:`~.WOL_UK_SEC.Data` Space.

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
valuation date to the limiting age. Whole of life has no maturity, so the frame is
truncated at ``omega_age``, policy month ``limit_mth() = 12 x (omega_age - entry age)``.
``duration_mth(t)`` counts the months the policy has been in force,
``duration_mth_init() + t`` from the model point's ``duration_mth`` at ``t = 0``, and the
contract runs on it: the completed policy years are ``duration(t) = duration_mth(t) //
12``, the contractual 1-based label is ``policy_year(t) = duration(t) + 1``, the lapse
table's key, and the attained age is the entry age plus ``duration(t)``, the mortality
table's, **age last birthday**, as the underwritten cell's specimen defines it. The
moratorium and the suicide window are the first twelve policy months, the premiums cease
at policy month ``cessation_months``, the cover and premium escalate on each policy
anniversary, the paid-up value counts the payments made, and the crossover is a policy
month. Expense inflation and mortality improvement run on ``t``, stepping on each
anniversary of the valuation date, so the maintenance charge is in valuation-date pounds
and the mortality basis is improved from the date it is stated at; the acquisition
expense is charged per policy issued, in the issue month, uninflated, as in
``basiclife/BasicTerm_SE``. On a point issued at ``t = 0`` the two clocks coincide, and
the model computes what :mod:`~.WOL_UK_S` computes, except that ``pols_if_init()`` is the
count already in force at the valuation date, 0 for such a point, whose policies enter
as new business at ``t = 0``.

Premiums and expenses fall at the beginning of the month; deaths at the end, against the
beginning-of-month in-force; lapses at the end after deaths, the pro-rata paid-up
variant's converting rather than terminating once half the premiums are paid.

**In force.** A point in force opens with two counts, ``policy_count`` on full cover and
``pols_pu_init`` paid-up, and with the facts of its contract that :mod:`~.WOL_UK_S` would
recompute from flat References, each measured at the valuation instant: the paid-up cover
per paid-up policy; the premiums paid since issue, which the moratorium refunds and the
crossover compares with the cover; and the cover and the premium of the policy year under
way, after every increase the RPI or the fixed step has already given. Each is history,
which no Reference changed at the valuation date reaches back to. ``result_pols()`` sets
out the counts on both strands: in force, new business and each decrement, month by month.

**What is sourced and what is not.** The contractual mechanics are sourced: the
moratorium and its return-of-premiums benefit, accidental death paying the full cash sum
from day one, premium cessation at 90 with cover continuing, the absence of any
surrender value, the suicide clause, the escalation ratios and the pro-rata paid-up value
formula. Every rate is a standardization. The CMI's current tables are restricted to
Authorised Users, so the two mortality bases shipped here are **[std]** proxies shaped
like the tables the notes name, and no insurer publishes premium rate tables, so the
premium is a model point input. **This model is a mechanics demonstration, not a pricing
or reserving result.** Replace the basis with licensed tables and company experience
first.

**Model points.** ``model_point_table_sec.csv`` is generated from :mod:`~.WOL_UK_S` and
its model point table, and the tests regenerate it and compare, so no row is typed by
hand. Points 1 to 7 are the twins of :mod:`~.WOL_UK_S`'s seven, issued at the valuation
date: the over-50s anchor cell, with the double accidental benefit, with the pro-rata
paid-up value and with RPI increases, the underwritten cell, with fixed increases, and an
over-50s male smoker. Points 8 to 13 are S points restated in force, each opened with the
state S carries into its month: the anchor cell inside its moratorium and in its
crossover month, the paid-up point with its strand in force, the RPI point past its
crossover, the underwritten increasing point on its first anniversary, and the male
smoker after its premiums have ceased. Point 14 is the RPI point issued 13 months after
the valuation date. Points 15 to 17 are read from S under References of their own, so
that their history is one today's References do not rebuild: the RPI point under an RPI
of 5%, the underwritten increasing point under a take-up of a half, and the paid-up point
under a crossover stress that leaves it paid-up entirely.

**Verification.** On the seven twins every cell this model shares with :mod:`~.WOL_UK_S`
agrees with it at every argument the S model evaluates in its sweep, ``pols_if_init`` and
``model_point`` excepted, so the worked example ``tests/test_whole_of_life_uk.py`` asserts
— money to the penny, in-force to five decimals — holds here too, with no number
restated. ``tests/test_whole_of_life_uk_sec.py`` splices: an S point restated in force at
month ``d`` continues the S projection from ``d`` on, cell by cell, at months about the
moratorium's end, the first conversion to paid-up, the crossover, premium cessation, the
cap on mortality and the limiting age, with the crossover stress on, and on variants of
S's points that reach what S's own cannot. A point issued ``k`` months late is the S
projection ``k`` months on.

Example:

    >>> import modelx as mx
    >>> model = mx.read_model("products/whole_of_life/WOL_UK_SEC")
    >>> model.Projection[10].result_cf()     # the paid-up point in force 200 months
    >>> model.Projection[10].result_pols()
"""

from modelx.serialize.jsonvalues import *

_name = "WOL_UK_SEC"

_allow_none = False

_spaces = [
    "Data",
    "Projection"
]

