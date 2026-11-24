# modelx: pseudo-python
# This file is part of a modelx model.
# It can be imported as a Python module, but functions defined herein
# are model formulas and may not be executable as standard Python.

"""In-force reference liability cash flow model for UK with-profits business.

:mod:`~.WP_UK_SEC` projects the policies :mod:`~.WP_UK_S` projects — a **unitised
with-profits bond** and a **conventional with-profits endowment**, through the machinery
that makes with-profits what it is: a retrospective asset share, an annually declared bonus
that hardens into a guarantee, a smoothed payout inside a target corridor, a market value
reduction on non-guaranteed exits, and a 90:10 shareholder transfer — from a **valuation
date** rather than from issue. A model point may be a policy already in force at that date,
in any month of its policy year, one issued at it, or one to be issued in the ten years
after it, as in lifelib's ``basiclife/BasicTerm_SE``, which extends ``basiclife/BasicTerm_S``
the same way. Its formulas are the executable counterpart of
``products/with_profits/technical-notes.md``, and ``products/with_profits/model-sec.md``
explains what running in force changes.

**The asset share is a state variable, not a cash flow**, as it is in :mod:`~.WP_UK_S`.
The policy's cash flows are premiums, claims, withdrawals, expenses and shareholder
transfers; the asset share is a *shadow* retrospective accumulation that nobody owns and
nobody is paid, and it drives claim amounts only through the bonus, smoothing and MVR
rules. The difference between what is paid and what the asset share says is absorbed by
the estate. On the valuation clock that makes the asset share history: a policy in force
opens with the asset share its own past built, which no Reference set today reaches back
to.

**Spaces.** The model contains two:

:mod:`~.WP_UK_SEC.Data`
    Reads the two assumption CSVs it shares with :mod:`~.WP_UK_S` and its own model point
    table, and holds their filename References. It takes no parameters, so each file is
    read **once per model**. It checks each table before a value of it is read, and hands
    the projection what the files hold as numpy vectors and arrays of numbers, one element
    per model point or per key.

:mod:`~.WP_UK_SEC.Projection`
    The by-policy projection, parameterized by ``idx``, the position of a model point in
    the ``Data`` vectors, as ``basiclife.BasicTerm_SC`` is: ``Projection[0]`` is an
    ItemSpace projecting the table's first row, model point 1, and its ``point_id()`` is
    that label. It reaches the inputs through its ``data`` Reference, which resolves to
    the single :mod:`~.WP_UK_SEC.Data` Space.

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
number from a ``Data`` vector at ``idx``, and every table as an array indexed by integers,
the guarantee dates as a flag by point and policy year; a timing or a kind is an int code,
and the claims total a code of its own, compensated as Python's ``sum`` is; the chassis
and the sex are decoded into the numbers a formula branches on and reads by; the eight
chains, the count, the asset share, the payout, the guarantee, the units, the unit price
and the two cumulants, are carried a policy year at a time, so that a cold call at the
longest cover runs on a small C stack; and every cell but the three reports,
``model_point`` and the three label accessors returns a C ``bint``, ``long long`` or
``double``, the seven checks among them, cached as a single value or in a C array sized
from the contract. modelx reads and runs the same formulas, and computes the same numbers.
``products/with_profits/model-sec.md`` says how to compile and run it, and what the
compiled model does not do as modelx does: it clears no cache when a Reference is set, so
every Reference is set on a model just imported.

**Projection basis.** Monthly steps on two clocks, with the bonus declaration left on its
annual cycle. ``t`` counts months from the valuation date, 0-based, as
``basiclife/BasicTerm_SE`` counts them: ``t = 0`` is the valuation month for every model
point, however old the policy, and the frame runs ``t = 0, 1, ..., proj_len() - 1``,
where ``proj_len()`` counts the months from the valuation date to the end of the frame:
the endowment's maturity, the bond's limiting age, or the month a withdrawal election
exhausts the bond's units, whichever comes first. ``duration_mth(t)`` counts the months
the policy has been in force, ``duration_mth_init() + t`` from the model point's
``duration_mth`` at ``t = 0``, and the contract runs on it: the completed policy years are
``duration(t) = duration_mth(t) // 12``, the contractual 1-based label is
``policy_year(t) = duration(t) + 1``, the key of the lapse table and of the guarantee
dates, the attained age, age nearest birthday, is ``age_at_entry() + duration(t)``, the
single premium falls in the issue month, ``duration_mth(t) == 0``, and a declaration falls
in the twelfth month of each policy year, ``(duration_mth(t) + 1) % 12 == 0``. Expense
inflation alone runs on ``t``, stepping on each anniversary of the valuation date, so the
maintenance expense is in valuation-date pounds. Premiums and partial withdrawals fall at
the start of the month; the fund return accrues over it; charges, the shareholder transfer
and the mortality charge fall at the end, in that order; claims and decrements follow,
deaths before surrenders. On a point issued at ``t = 0`` the two clocks coincide and the
model computes what :mod:`~.WP_UK_S` computes, except that ``pols_if_init()`` is the count
already in force at the valuation date, 0 for such a point, whose policies enter as new
business at ``t = 0``.

**The declaration stays annual, and that is the point.** The bonus declaration is the
governing act of discretion on this product, it happens once a policy year, and it
permanently hardens the guarantee. So it fires in the twelfth month of each policy year,
on the policy clock, and nowhere else: the unit price and the guaranteed benefit are step
functions, and the cost of bonus and the shareholder transfer are nil in the other eleven
months. Everything continuous runs monthly around it, annual assumptions converted with
the effective ``(1 + r)^(1/12)`` and ``1 - (1 - r)^(1/12)`` forms. What the monthly grid
buys is the **guarantee date**: an exit in a guarantee-date month is MVR-free and an exit
in the other eleven months of the same policy year is not.

**In force.** A point in force carries, beside its count, ``policy_count``, the state
:mod:`~.WP_UK_S` carries into the month it is valued at, each per policy and measured at
the valuation instant, before month 0's events: the asset share, the units and the unit
price, the endowment's attaching bonus, the smoothed payout, the bonus rate of the policy
year under way, and the two cumulants :mod:`~.WP_UK_S` restarts at 0 where its frame
opens, the guarantee charges taken, which cap the charge at 2% of the asset share, and the
smoothing account. Each is history. A declaration or a guarantee date at the end of month 0
is the projection's first event. With the bonus rule on, a frame a forced encashment ends
mid-year reads the rate declared before its last policy year, where :mod:`~.WP_UK_S` reads
the year's declaration past its frame: the one departure from it, recorded in
``bonus_rate``. ``result_pols()`` sets out the counts: in force, new business and each
decrement, month by month.

**What is deterministic, and what that costs.** This is a deterministic single-scenario
projection, and the notes are emphatic that a deterministic base run **materially
understates the cost of guarantees**, because guarantee cost is convex in the fund
return. The model produces the per-scenario cash flows a market-consistent stochastic
valuation consumes; the stochastic layer is out of scope.

**What is sourced and what is not.** The mechanics are sourced: the asset share item
list and its regulatory codification, bonus hardening, the unit-price floor, the
guarantee-date and death MVR exemptions, the MVR's contractual bound, the target
corridor, the smoothing cap, the lifetime guarantee-charge cap and the 90:10 split.
Every *rate* is a standardization: bonus declarations are not published in the
principles and practices documents, no MVR scale is public, the CMI's tables are
restricted to Authorised Users, and no UK with-profits lapse experience was retrieved.
**This model is a mechanics demonstration, not a pricing or reserving result.**

**Model points.** ``model_point_table_sec.csv`` is generated from :mod:`~.WP_UK_S` and its
model point table, and the tests regenerate it and compare, so no row is typed by hand.
Points 1 to 7 are the twins of :mod:`~.WP_UK_S`'s seven points: its four bonds and its
endowment in force, at 60 and 240 months, and the endowment and the down scenario's bond
issued at the valuation date. Points 8 to 18 are S points restated in force, each opened
with the state S carries into its month: the worked example's bond in a declaration month,
71, and in its last month before the limiting age, 779; the down scenario as its market
value reduction turns on, 68, as its corridor's ceiling binds, 92, on its guarantee date,
119, and with its asset share floored at 0, 242; the 5% bond as its charge cap binds, 487;
the withdrawing bond in its last month, 402; the endowment at its first declaration, 11,
and at maturity, 299; and the bond variant past its charge cap, 100. Point 19 is the bond
variant issued 13 months after the valuation date. Points 20 to 24 are S points restated
from S run under References of their own, histories no state S reaches at its shipped
References holds: the bond variant at 60 and the 5% bond at 300 under a guarantee charge
doubled, the worked example's bond and the endowment at 150 under the bonus rule, and the
worked example's bond at 156 under a smoothing cap of 5%.

**Verification.** On the twins of :mod:`~.WP_UK_S`'s new business every cell this model
shares with it agrees with it at every argument the S model evaluates in its sweep, so the
worked example ``tests/test_with_profits_uk.py`` asserts to the penny holds here too, with
no number restated. ``tests/test_with_profits_uk_sec.py`` splices: an S point restated in
force at month ``d`` continues the S projection from ``d`` on, cell by cell, at months
about the declarations, the guarantee window, the smoothing cap, the corridor, the market
value reduction, the charge cap, the asset share's floor and the frame's end, with the
estate distribution and the bonus rule switched on, and on variants of S's points that
reach what S's own cannot. A point issued ``k`` months late is the S projection ``k``
months on.

Example:

    >>> import modelx as mx
    >>> model = mx.read_model("products/with_profits/WP_UK_SEC")
    >>> model.Projection[10].result_cf()      # the eleventh row, model point 11: the
    >>> model.Projection[10].result_payout()  # down scenario on its guarantee date
"""

from modelx.serialize.jsonvalues import *

_name = "WP_UK_SEC"

_allow_none = False

_spaces = [
    "Data",
    "Projection"
]

