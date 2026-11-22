# modelx: pseudo-python
# This file is part of a modelx model.
# It can be imported as a Python module, but functions defined herein
# are model formulas and may not be executable as standard Python.

"""In-force reference liability cash flow model for UK guaranteed-premium term assurance.

:mod:`~.Term_UK_SEC` projects the policy :mod:`~.Term_UK_S` projects — UK term assurance
in the three benefit shapes the representative product offers, **level**, **decreasing**
at a client-selected schedule rate and **family income benefit**, with terminal illness
inside the death decrement, an optional RPI indexation option, an optional waiver of
premium and **no tail states of any kind**: cover ceases at the end of the term with no
maturity value, no renewal and no conversion — from a **valuation date** rather than from
issue. A model point may be a policy already in force at that date, in any month of its
policy year, one issued at it, or one to be issued in the ten years after it, as in
lifelib's ``basiclife/BasicTerm_SE``, which extends ``basiclife/BasicTerm_S`` the same
way. Its formulas are the executable counterpart of
``products/term_assurance/technical-notes.md``, and
``products/term_assurance/model-sec.md`` explains what running in force changes.

**Spaces.** The model contains two:

:mod:`~.Term_UK_SEC.Data`
    Reads the three assumption CSVs it shares with :mod:`~.Term_UK_S`, its own model point
    table and its own waiver pipeline, and holds their filename References. It takes no
    parameters, so each file is read **once per model**. It checks each table before a
    value of it is read, and hands the projection what the files hold as numpy vectors
    and arrays of numbers, one element per model point or per key.

:mod:`~.Term_UK_SEC.Projection`
    The by-policy projection, parameterized by ``idx``, the position of a model point in
    the ``Data`` vectors, as ``basiclife.BasicTerm_SC`` is: ``Projection[0]`` is an
    ItemSpace projecting the table's first row, model point 1, and its ``point_id()`` is
    that label. It reaches the inputs through its ``data`` Reference, which resolves to
    the single :mod:`~.Term_UK_SEC.Data` Space.

The split matters for more than tidiness. Because ``Projection`` is parameterized,
every ``Projection[N]`` is a separate ItemSpace with its own cells cache; readers
placed there would re-read every file for every policy. In ``Data`` they are evaluated
once, however many policies are projected.

Input data is **external**: CSVs in the model folder's parent directory, read at run
time rather than stored inside the model. The model folder itself holds no data, so
the model and its inputs must travel together.

**Compiled.** The model compiles under modelx-cython into C-typed code, as
``basiclife/BasicTerm_SC`` does, from the two inputs beside it: ``sample_sec.py``, the run
that types each cell, and ``spec_sec.py``, the length of each cell's cache.
``Projection``'s cells read every model point attribute a projection cell uses as a C
number from a ``Data`` vector at ``idx``, and every table as an array indexed by integers;
a timing or a kind is an int code; a text column is decoded into the number a formula
branches on; and every cell but the two reports, ``model_point`` and five label
accessors returns a C ``bint``, ``long long`` or ``double``, the two checks among them,
cached as a single value or in a C array sized from the contract. modelx reads and runs
the same formulas, and computes the same numbers.
``products/term_assurance/model-sec.md`` says how to compile and run it, and what the
compiled model does not do as modelx does: it clears no cache when a Reference is set, so
every Reference is set on a model just imported.

**Projection basis.** Monthly steps on two clocks. ``t`` counts months from the
valuation date, 0-based, as ``basiclife/BasicTerm_SE`` counts them: ``t = 0`` is the
valuation month for every model point, however old the policy, and the frame runs
``t = 0, 1, ..., proj_len() - 1``, where ``proj_len()`` counts the months from the
valuation date to the end of the term. ``duration_mth(t)`` counts the months the policy
has been in force, ``duration_mth_init() + t`` from the model point's ``duration_mth`` at
``t = 0``, and the contract runs on it: the completed policy years are
``duration(t) = duration_mth(t) // 12``, the select duration, the contractual 1-based
label is ``policy_year(t) = duration(t) + 1``, the lapse table's key, and the attained age
is ``age_at_entry(life) + duration(t)``, the mortality table's. The decreasing schedule
and the family income benefit's annuity-certain read the policy month, an annual premium
and the RPI increase fall on the policy anniversary, renewal commission is paid from the
second policy year and the clawback counts the months since issue. Expense inflation
alone runs on ``t``, stepping on each anniversary of the valuation date, so the
maintenance charge is in valuation-date pounds; acquisition and the initial commission
are charged per policy issued, in the issue month, uninflated, as in
``basiclife/BasicTerm_SE``. On a point issued at ``t = 0`` the two clocks coincide, and the
model computes what :mod:`~.Term_UK_S` computes, except that ``pols_if_init()`` is the
count already in force at the valuation date, 0 for such a point, whose policies enter as
new business at ``t = 0``.

Premiums, maintenance expense and renewal commission fall at the start of the month;
death and terminal illness claims and their claim expense at the end; lapses act on the
survivors of mortality, death before lapse. The assumption tables stay in the annual
units they are quoted in, converted month by month with ``1 - (1 - r)^(1/12)``, the
notes' own convention.

**In force.** A point in force carries, beside its count, the state :mod:`~.Term_UK_S`
carries into the month it is valued at, which S itself restarts where its frame opens,
each measured at the valuation instant: the selective-lapse ratio, as a share of the
cohort issued; the deaths since issue, and the family income benefit streams in payment,
each per policy in force; the RPI indexation factors already given; the share of the
policies whose premium is waived; the initial commission paid at issue, which the
clawback recovers; and, in a companion, ``wop_pipeline_sec.csv``, the share still in the
deferred period from each of its months, after the recoveries already made. Each is
history, which no Reference changed at the valuation date reaches back to.
``result_pols()`` sets out the counts: in force, new business and each decrement, month by
month.

**What is sourced and what is not.** The contractual mechanics are sourced: the
decreasing-shape amortization, the family income benefit as an annuity-certain to the
end of the term, terminal illness as a 100% acceleration rather than an extra benefit,
the absence of any surrender value, the indexation option's cover and premium caps, and
the product's limits on terms and ages. Everything quantitative is a standardization
introduced for the reference implementation. No UK insurer publishes premium rate tables
— pricing is quote-driven, and only the £5/month minimum is public — and the current CMI
"16" Series assured lives tables are subscriber-restricted, so both the premium and the
mortality basis shipped here are constructed. **This model is a mechanics demonstration,
not a pricing or reserving result.** Replace the assumption tables with company data, and
the mortality basis with licensed tables, before drawing any conclusion from the output.

**Model points.** ``model_point_table_sec.csv`` and ``wop_pipeline_sec.csv`` are
generated from :mod:`~.Term_UK_S` and its model point table, and the tests regenerate
them and compare, so no row is typed by hand. Points 1 to 8 are the twins of
:mod:`~.Term_UK_S`'s eight points: 1 to 7 issued at the valuation date, and 8 in force 60
months, which :mod:`~.Term_UK_S` opens at its own month 60. Points 9 to 13 are S points
restated in force, each opened with the state S carries into its month: the indexed point
on its fifth anniversary, the family income benefit mid-year at 66, the waiver point at 66
and four months in, inside its deferred period, and the anchor cell in its last covered
month. Point 14 is the waiver point issued 13 months after the valuation date.

**Verification.** On the seven twins issued at the valuation date every cell this model
shares with :mod:`~.Term_UK_S` agrees with it at every argument the S model evaluates in
its sweep, ``pols_if_init`` and ``model_point`` excepted, so the worked example
``tests/test_term_assurance_uk.py`` asserts — money to the penny, in-force to six decimals
— holds here too, with no number restated. ``tests/test_term_assurance_uk_sec.py``
splices: an S point restated in force at month ``d`` continues the S projection from ``d``
on, cell by cell, at months about the waiver's deferred period, the first anniversary, the
selective-lapse ratio's crossing, the clawback window's and the select period's ends, and
the end of the term, with every switch that ships off switched on, and on variants of S's
points that reach what S's own cannot. A point issued ``k`` months late is the S
projection ``k`` months on.

Example:

    >>> import modelx as mx
    >>> model = mx.read_model("products/term_assurance/Term_UK_SEC")
    >>> model.Projection[7].result_cf()      # the eighth row: the anchor cell in force
    >>> model.Projection[7].result_pols()    # five years, model point 8
"""

from modelx.serialize.jsonvalues import *

_name = "Term_UK_SEC"

_allow_none = False

_spaces = [
    "Data",
    "Projection"
]

