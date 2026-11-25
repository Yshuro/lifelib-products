# modelx: pseudo-python
# This file is part of a modelx model.
# It can be imported as a Python module, but functions defined herein
# are model formulas and may not be executable as standard Python.

"""In-force reference liability cash flow model for UK individual income protection.

:mod:`~.IP_UK_SEC` projects the policies :mod:`~.IP_UK_S` projects — full-term
guaranteed-premium own-occupation income protection, a monthly income benefit payable in
arrears after a deferred period, escalating in claim, ceasing at recovery, death or the
policy end date, as ``products/income_protection/technical-notes.md`` specifies — from a
**valuation date** rather than from issue. A model point may be a policy already in force
at that date, in any month of its policy year, its lives in health and in claim payment at
any claim duration, one issued at it, or one to be issued in the ten years after it, as in
lifelib's ``basiclife/BasicTerm_SE``, which extends ``basiclife/BasicTerm_S`` the same
way. Its formulas are the executable counterpart of those notes, and
``products/income_protection/model-sec.md`` explains what running in force changes.

**This is the library's one multiple-state model.** It carries a **three-state**
population — healthy and active (H), sick and in claim payment (S), dead (D) — with lapse
as a further exit from H and **recovery flowing back from S to H**, claim *inception*
rates out of H and claim *termination* rates out of S, as the CMI's own graduations
structure it. The in-claim population is **two-dimensional**: termination rates depend
on how long the claim has run, so the model tracks ``l_S(t, z)``, the population in claim
at month ``t`` with claim duration ``z``, cohort by cohort. A policy in force at the
valuation date therefore opens with a vector of claim cohorts, as long as its months in
force, beside its healthy lives.

**Spaces.** The model contains two:

:mod:`~.IP_UK_SEC.Data`
    Reads the four assumption CSVs it shares with :mod:`~.IP_UK_S`, its own model point
    table and its claim cohorts, and holds their filename References. It takes no
    parameters, so each file is read **once per model**. It checks each table before a
    value of it is read, and hands the projection what the files hold as numpy vectors
    and arrays of numbers, one element per model point or per key.

:mod:`~.IP_UK_SEC.Projection`
    The by-policy projection, parameterized by ``idx``, the position of a model point in
    the ``Data`` vectors, as ``basiclife.BasicTerm_SC`` is: ``Projection[0]`` is an
    ItemSpace projecting the table's first row, model point 1, and its ``point_id()`` is
    that label. It reaches the inputs through its ``data`` Reference, which resolves to
    the single :mod:`~.IP_UK_SEC.Data` Space.

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
branches on; the claim cohorts, which :mod:`~.IP_UK_S` carries as a tuple a month, are a
recursion of two parameters, a cohort a cell, whose sums are :mod:`~.IP_UK_S`'s, written
out; and every cell but the three reports, ``model_point`` and the five label accessors
returns a C ``bint``, ``long long`` or ``double``, the three checks among them, cached as
a single value or in a C array sized from the contract. modelx reads and runs the same
formulas, and computes the same numbers. ``products/income_protection/model-sec.md``
says how to compile and run it, and what the compiled model does not do as modelx does:
it clears no cache when a Reference is set, so every Reference is set on a model just
imported.

**Projection basis.** Monthly steps on two clocks, and a third for claims. ``t`` counts
months from the valuation date, 0-based, as ``basiclife/BasicTerm_SE`` counts them:
``t = 0`` is the valuation month for every model point, however old the policy, and the
frame runs ``t = 0, 1, ..., proj_len() - 1``, where ``proj_len()`` counts the months from
the valuation date to the policy end date, policy month
``expiry_mth() = 12 x (expiry_age - entry age)``. ``duration_mth(t)`` counts the months
the policy has been in force, ``duration_mth_init() + t`` from the model point's
``duration_mth`` at ``t = 0``, and the contract runs on it: the completed policy years are
``duration(t) = duration_mth(t) // 12``, the contractual 1-based label is
``policy_year(t) = duration(t) + 1``, the lapse table's key and the escalation's
anniversaries, and the attained age is the entry age plus ``duration(t)``, the inception
and mortality tables'. The claim duration ``z`` is a 1-based cohort index on which the
termination rates are read. Expense inflation and discounting run on ``t``, from the
valuation date, so the expense loads are in valuation-date pounds. On a point issued at
``t = 0`` the two clocks coincide, and the model computes what :mod:`~.IP_UK_S` computes,
except that ``pols_if_init()`` is the count already in force at the valuation date, 0 for
such a point, whose policies enter healthy as new business at ``t = 0``.

Premiums fall at the beginning of the month and are paid by lives in H only — premiums
are waived from the start of benefit payment. Transitions and benefit fall at the end of
the month; a claim incepting at the end of month ``t`` receives its first payment at the
end of month ``t + 1``. All cover and any claim in payment terminate at the policy end
date, the end of the frame's last month, with no value.

**In force.** A point in force opens with its ``policy_count``, the policies in force,
in health and in claim together, and with the facts of its contract that :mod:`~.IP_UK_S`
would recompute from flat References, each measured at the valuation instant, the start of
month 0, before month 0's events, recoveries already returned to health: the healthy share
of the count; the share in claim at each claim duration, the claim cohorts, read from a
companion, ``inforce_cohorts_sec.csv``, keyed by point and claim duration; and the monthly
benefit and premium entering month 0, after every escalation already given, an anniversary
at the valuation date being the projection's first event. Each is history, which no
Reference changed at the valuation date reaches back to. ``result_pols()`` sets out the
counts in each state: in force, new business and each movement, month by month.

**What is sourced and what is not.** The contractual mechanics are sourced: the
deferred period menu, the two-band maximum-benefit formula, escalation capped at 10% with a
x1.5 premium multiplier continuing in claim, waiver of premium from benefit start, linked
claims within 52 weeks, and expiry without value. Every rate is a standardization. The
CMI IP11 Series — claim inception rates by sex, deferred period and occupation class,
and termination rates split by recovery and death — is restricted to CMI Authorised
Users, so the inception, recovery and in-claim mortality rates shipped here are **[std]**
proxies shaped like IP11 and carry no CMI authority, and the premium is a placeholder.
**This model is a mechanics demonstration, not a pricing or reserving result.** Replace
the basis with licensed tables before drawing any conclusion from the output.

**Model points.** ``model_point_table_sec.csv`` and ``inforce_cohorts_sec.csv`` are
generated from :mod:`~.IP_UK_S` and its model point table, and the tests regenerate them
and compare, so no row is typed by hand. Points 1 to 7 are the twins of
:mod:`~.IP_UK_S`'s seven: the active-lives anchor cell, its level-cover variant, an
older female cell on a 13-week deferred period and an older male cell on 52 weeks, issued
at the valuation date; and the three claims in payment, points 2, 5 and 7, the
claims-in-payment worked example among them, each on a policy clock of whole years since
issue, since :mod:`~.IP_UK_S` restarts its policy clock at the valuation date on an
in-claim cell. Points 8 to 16 are S points restated in force, each opened with the state S
carries into its month: the anchor cell on its first anniversary, at policy year 6 and in
its last month; the two claims on the exit basis in later claim-duration years; the claim
on the active-lives basis a year on, its recoveries back in health; the female cell after
its first anniversary; the older male cell in its last months; and the level cell mid-year.
Point 17 is the female cell issued 13 months after the valuation date. Points 18 and 19 are
read from S under References of their own, so that their history is one today's References
do not rebuild: the anchor cell under an RPI of 5%, which shocks its lapses, and the female
cell under 12%, which escalation's 10% cap binds.

**Verification.** On the four twins issued at the valuation date every cell this model
shares with :mod:`~.IP_UK_S` agrees with it at every argument the S model evaluates in its
sweep, ``pols_if_init``, ``model_point`` and the claim duration the cohorts replace
excepted, so the goldens ``tests/test_income_protection_uk.py`` asserts on them hold here
too, with no number restated. ``tests/test_income_protection_uk_sec.py`` splices: an S
point restated in force at month ``d`` continues the S projection from ``d`` on, cell by
cell, its claim cohorts with it, at months about the anniversaries, the ultimate lapse
year, the inception table's pivot ages, the claim-duration bands and the policy end date;
the twins of S's claims in payment continue S from the valuation date, the worked example
among them; and a point issued ``k`` months late is the S projection ``k`` months on.

Example:

    >>> import modelx as mx
    >>> model = mx.read_model("products/income_protection/IP_UK_SEC")
    >>> model.Projection[8].result_cf()      # point 9: the anchor cell in force 60 months
    >>> model.Projection[8].result_pols()
"""

from modelx.serialize.jsonvalues import *

_name = "IP_UK_SEC"

_allow_none = False

_spaces = [
    "Data",
    "Projection"
]

