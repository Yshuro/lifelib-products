# modelx: pseudo-python
# This file is part of a modelx model.
# It can be imported as a Python module, but functions defined herein
# are model formulas and may not be executable as standard Python.

"""In-force reference liability cash flow model for a UK unit-linked investment bond.

:mod:`~.ULB_UK_SEC` projects the bond :mod:`~.ULB_UK_S` projects — a modern clean-charge
onshore unit-linked bond: a single premium, a death benefit of 100.1% of the bid value of
units, no surrender penalty, the 5% a year tax-deferred withdrawal pattern the product is
sold on, an optional ongoing adviser charge and an optional return-of-premium guaranteed
minimum death benefit — from a **valuation date** rather than from issue. A model point
may be a bond already in force at that date, in any month of its policy year, one issued
at it, or one to be issued in the ten years after it, as in lifelib's
``basiclife/BasicTerm_SE``, which extends ``basiclife/BasicTerm_S`` the same way. Its
formulas are the executable counterpart of ``products/unit_linked_bond/technical-notes.md``,
and ``products/unit_linked_bond/model-sec.md`` explains what running in force changes.

**The decomposition is the model**, as it is :mod:`~.ULB_UK_S`'s: *the unit fund*, the bid
value of units, which grows with the fund, bears the tax provision and the fund-based
charges, and is drawn down by withdrawals and adviser charges; and *the non-unit cash
flow*, what accrues to the insurer: the annual management charge and any rider charge,
less expenses and the **death strain**, which is only the uplift over the unit fund,
because the rest of every benefit is funded by cancelling the policyholder's own units.

**Spaces.** The model contains two:

:mod:`~.ULB_UK_SEC.Data`
    Reads the two assumption CSVs it shares with :mod:`~.ULB_UK_S` and its own model point
    table, and holds their filename References. It takes no parameters, so each file is
    read **once per model**. It checks each table before a value of it is read, and hands
    the projection what the files hold as numpy vectors and arrays of numbers, one element
    per model point or per key.

:mod:`~.ULB_UK_SEC.Projection`
    The by-policy projection, parameterized by ``idx``, the position of a model point in
    the ``Data`` vectors, as ``basiclife.BasicTerm_SC`` is: ``Projection[0]`` is an
    ItemSpace projecting the table's first row, model point 1, and its ``point_id()`` is
    that label. It reaches the inputs through its ``data`` Reference, which resolves to
    the single :mod:`~.ULB_UK_SEC.Data` Space.

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
branches on; the fund, the withdrawals since issue and the count are carried a policy
year at a time, so that a cold call at the longest cover runs on a small C stack; and
every cell but the three reports, ``model_point`` and three label accessors returns a C
``bint``, ``long long`` or ``double``, the three checks among them, cached as a single
value or in a C array sized from the contract. modelx reads and runs the same formulas,
and computes the same numbers. ``products/unit_linked_bond/model-sec.md`` says how to
compile and run it, and what the compiled model does not do as modelx does: it clears no
cache when a Reference is set, so every Reference is set on a model just imported.

**Projection basis.** Monthly steps on two clocks. ``t`` counts months from the
valuation date, 0-based, as ``basiclife/BasicTerm_SE`` counts them: ``t = 0`` is the
valuation month for every model point, however old the bond, and the frame runs
``t = 0, 1, ..., proj_len() - 1``, where ``proj_len()`` counts the months from the
valuation date to the end of the frame. ``duration_mth(t)`` counts the months the bond has
been in force, ``duration_mth_init() + t`` from the model point's ``duration_mth`` at
``t = 0``, and the contract runs on it: the completed policy years are
``duration(t) = duration_mth(t) // 12``, the contractual 1-based label is
``policy_year(t) = duration(t) + 1``, the key of the surrender table, of the 5% allowance
and of the allowance-exhaustion step, and the attained age, age last birthday, is
``age_at_entry() + duration(t)``, the mortality table's. Expense inflation alone runs on
``t``, stepping on each anniversary of the valuation date, so the maintenance charge is in
valuation-date pounds; acquisition is charged per bond issued, in the issue month,
uninflated, as in ``basiclife/BasicTerm_SE``. Fund growth, the tax provision and the
fund-based charges accrue over the month; withdrawals, adviser charges and any rider
charge are unit cancellations at the end of it; death and surrender follow, deaths before
surrenders.

The frame ends at the limiting age or, sooner, at the first month the unit fund opens at
or below ``depletion_threshold``, half a pence, which on the deterministic base run it
does, because a 5% withdrawal against a 5% gross return net of tax and charges cannot be
sustained. :mod:`~.ULB_UK_S` tests the fund against 0, and so runs a month on where the
withdrawal cap closes a fund on a rounding above 0, as it does on its adviser-charge point;
that is the one departure on a point issued at ``t = 0``. Otherwise, there the two clocks
coincide, and the model computes what :mod:`~.ULB_UK_S` computes, except that
``pols_if_init()`` is the count already in force at the valuation date, 0 for such a
point, whose policies enter as new business at ``t = 0``.

**In force.** A point in force carries, beside its count, the state :mod:`~.ULB_UK_S`
carries into the month it is valued at, each per policy and measured at the valuation
instant: the unit fund; the withdrawals and adviser charges since issue, which the
allowance is measured against and the guaranteed minimum death benefit is net of; and the
5% allowance accrued since issue, through the policy year of the month before. Each is
history, which no Reference changed at the valuation date reaches back to.
``result_pols()`` sets out the counts: in force, new business and each decrement, month by
month.

**What is sourced and what is not.** The contractual mechanics are sourced: the 100.1%
death uplift, the surrender value as the bid value of units with no penalty, the 7.5%
rolling withdrawal cap, charges accruing daily through the unit price, segmentation into
100 identical policies, and the liability cap to fund assets. Every rate is a
standardization. Per-fund charge rate cards are not published, the CMI's assured-lives
tables are restricted to Authorised Users, and no public UK bond persistency study was
retrieved, so the charge levels, the mortality basis and the whole surrender table are
placeholders. **This model is a mechanics demonstration, not a pricing or reserving
result.**

**Model points.** ``model_point_table_sec.csv`` is generated from :mod:`~.ULB_UK_S` and its
model point table, and the tests regenerate it and compare, so no row is typed by hand.
Points 1 to 6 are the twins of :mod:`~.ULB_UK_S`'s six points, issued at the valuation
date. Points 7 to 10 are S points restated in force, each opened with the state S carries
into its month: the anchor cell 30 months in, the adviser charge at 66, the GMDB point on
its twentieth anniversary, its whole premium withdrawn, and the anchor cell in its last
month before its fund is exhausted. Point 11 is the GMDB point issued 13 months after the
valuation date. Point 12 is the GMDB point restated at its month 66 from S run under a fund
return of 0, a fund that has earned nothing since issue, its guarantee in the money and
the rider charging, which no state S reaches at its shipped return holds.

**Verification.** On the six twins every cell this model shares with :mod:`~.ULB_UK_S`
agrees with it at every argument the S model evaluates in its sweep, ``pols_if_init`` and
``model_point`` excepted, over the months both frames run alike, so the worked example
``tests/test_unit_linked_bond_uk.py`` asserts to the penny holds here too, with no number
restated. ``tests/test_unit_linked_bond_uk_sec.py`` splices: an S point restated in force
at month ``d`` continues the S projection from ``d`` on, cell by cell, at months about the
surrender bands' edges, policy year 21 and the end of the frame, with every switch that
ships off switched on, and on variants of S's points that reach what S's own cannot. A
point issued ``k`` months late is the S projection ``k`` months on.

Example:

    >>> import modelx as mx
    >>> model = mx.read_model("products/unit_linked_bond/ULB_UK_SEC")
    >>> model.Projection[6].result_cf()      # the seventh row: the anchor cell in force
    >>> model.Projection[6].result_pols()    # 30 months, model point 7
"""

from modelx.serialize.jsonvalues import *

_name = "ULB_UK_SEC"

_allow_none = False

_spaces = [
    "Data",
    "Projection"
]

