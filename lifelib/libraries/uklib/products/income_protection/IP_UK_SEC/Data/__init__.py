# modelx: pseudo-python
# This file is part of a modelx model.
# It can be imported as a Python module, but functions defined herein
# are model formulas and may not be executable as standard Python.

"""Input data shared by every by-policy projection.

The six input CSVs are read here, **once per model**, and referenced from
:mod:`~.IP_UK_SEC.Projection` as ``data``. :mod:`~.IP_UK_SEC.Projection` is parameterized
by ``idx``, the position of a model point in the table, so each ``Projection[i]`` is a
separate ItemSpace with its own cells cache; if the readers lived there, every model point
would re-read every file. Holding them in an unparameterized Space reads each file once no
matter how many policies are projected.

Inputs are **external files**: plain CSVs in the model folder's parent directory,
``products/income_protection/``, rather than data stored inside the model. The model
folder therefore holds nothing but formulas — no ``_data/``, no IOSpec, no embedded
values — so a diff of the model shows logic changes only. This follows
``annuallife.TradLife_A``; contrast ``basiclife.BasicTerm_S``, which keeps its inputs
*inside* the model through modelx's IOSpec machinery.

The consequence worth knowing: **the model is not portable on its own.** Copying the
``IP_UK_SEC`` folder without its parent's CSVs produces a model that reads and then
fails on first evaluation.

**Four of the tables are IP_UK_S's.** The inception, termination, mortality and lapse
tables are the files :mod:`~.IP_UK_S` reads, read here in place: one copy of each table
serves both models, so an edit to one reaches both. The model point table,
``model_point_table_sec.csv``, and the claim cohorts, ``inforce_cohorts_sec.csv``, are
this model's own; the first sits beside :mod:`~.IP_UK_S`'s ``model_point_table.csv``,
which this model never opens.

:func:`input_dir` resolves the directory from ``_model.path.parent`` at run time, so
the model works wherever the repository is checked out. Each table has a filename
Reference and a reader Cells:

======================  ==========================  ==============================
Reference               Cells                       File
======================  ==========================  ==============================
model_point_file        model_point_table()         model_point_table_sec.csv
inforce_cohorts_file    inforce_cohorts()           inforce_cohorts_sec.csv
inception_file          inception_table()           inception_table.csv
termination_file        termination_table()         termination_table.csv
mort_table_file         mort_table()                mort_table.csv
lapse_table_file        lapse_table()               lapse_table.csv
======================  ==========================  ==============================

The two experience bases are separate files because they are separate CMI publications
and are parameterized differently. Inception rates are keyed by **sex, occupation class,
deferred period and age**, exactly as the IP11 Series names its tables; termination
rates are keyed by **claim duration** alone here, which is a deliberate simplification —
IP11 terminations are two-dimensional in age and duration, with claimant mortality
duration-dependent to five years and age-only beyond, and a licensee should restore the
age dimension by adding it as an index level. The projection's cohort shift assumes the
termination rates depend on the claim duration alone, so restoring the age dimension
touches the cohort recursion as well as the lookups.

**The model point table is checked as it is read.** Five of its columns are the in-force
interface: ``policy_count`` and ``duration_mth``, as in ``basiclife.BasicTerm_SE``, and
the opening state of a point in force, the healthy share of its count,
``pols_active_init``, and the monthly benefit and premium entering month 0,
``benefit_pp_init`` and ``premium_pp_init``. :func:`model_point_table` refuses a table
that lacks one, repeats a ``point_id``, holds a count, a duration or a state no policy can
have, or a policy to be issued more than ``future_horizon_mth`` months after the valuation
date, 120 as shipped: future new business is written over a stated horizon, so that no
frame runs longer than cover from issue plus that horizon. Set to 0, the Reference refuses
future new business altogether. It refuses, too, what :mod:`~.IP_UK_S` projects without a
word or meets only when a projection reaches it: a code that names no sex, occupation
class, deferred period, escalation, status or recovery basis, a premium basis the model
does not price, which :mod:`~.IP_UK_S` checks in a cell nothing calls, an age or an amount
that is not a number in its range, and a history the contract cannot have given. The checks
run in turn, and the first that fails raises, naming the missing column or every point that
fails it. Whether a point is still in cover at the valuation date, and whether the contract
issues it, are rules of the product, and ``Projection.proj_len`` checks them, against its
own References.

**The claim cohorts are checked as they are read.** :func:`inforce_cohorts` refuses a
row for a point the table lacks, for a point not yet in force, which is issued healthy,
at a claim duration that is not whole or not between 1 and the point's months in force,
twice for one point and duration, or with a share that is not a share of the count, and a
point in force whose healthy share and cohort shares do not sum to 1.

**Each assumption table is checked before a value of it is read.** Its keys are read by
their value, so an age written ``35.0`` is age 35, and a key that is not whole, text among
them, is refused, naming the file, the column and its lines; so are keys that repeat or
leave a gap the projection would read, naming the keys. A value that is blank, text,
infinite or outside its range is refused, naming the file, the column and its lines,
whether or not a point reads it: ``Projection.mort_rate`` and ``Projection.inception_rate``
cap the annual rate with ``min``, which keeps its first argument unless a later one
compares smaller, and no comparison with NaN holds, so each cap is written with its bound
second and a NaN would stay NaN; but an infinity is a number, which the cap reads as 1,
certain death or certain claim. The check of the inception table is in its reader,
:func:`inception_table`, which the projection reads whole; that of each other table is in
the cell the projection takes its extent from, which it asks before it reads the table:
:func:`mort_age_first` and :func:`mort_age_last` for the mortality table,
:func:`termination_last_year` for the termination table and :func:`lapse_last_year` for the
lapse table. Each refusal names the table's lines, the header line 1: each check reads the
file as it stands, where :mod:`~.IP_UK_S`'s readers sort the tables or index them, and with
the order would lose the lines. A key that is not whole, or is ``2**53`` or more in size,
which int64 would hold inexactly, is refused before the keys are cast, and the gaps between
a table's keys are found in one pass over them, so that a key far from the rest costs no
more than the rows.

**The vectors.** The readers return what the files hold, and no
:mod:`~.IP_UK_SEC.Projection` cell but ``model_point``, a reporting cell, reads them. The
others read the arrays below instead, one element at a time, a model point's attribute
being the element at its position, ``data.benefit_mth()[idx]``. That is what lets the
model compile to C, as ``basiclife.BasicTerm_SC`` does: each array is a numpy vector or
table of int64 or float64, which compiles to a typed memoryview, never one of bools,
objects or text, and each extent of a table is an int.

Text the projection needs is decoded here, into the number it selects, for every point at
once, as :mod:`~.IP_UK_S` reads each value: the sex, the occupation class and the deferred
period into the point's row of the inception table, its schedule, and the sex into its
row of the mortality table; the escalation into a 0/1 flag, RPI 1; and the recovery basis
into its code, return_to_h 0 and exit 1, ``Projection``'s ``RETURN_TO_H`` and ``EXIT``. And
each table keyed by more than a number becomes an integer-indexed array: the inception
table, by its forty schedules and the attained age, holding :mod:`~.IP_UK_S`'s
interpolation, extrapolation and floor at 0 at every age the contract admits; the
mortality table by sex and attained age, padded from age 0; the termination table's two
rates by claim duration year and the lapse table by policy year, each padded at year 0;
and the claim cohorts by point and claim duration:

==============================  =======  ================  =================================
Cells                           dtype    Shape             From
==============================  =======  ================  =================================
point_id()                      int64    [point]           the table's index
entry_age()                     int64    [point]           ``entry_age``
expiry_age()                    int64    [point]           ``expiry_age``
occ_class()                     int64    [point]           ``occ_class``
deferred_weeks()                int64    [point]           ``deferred_weeks``
inception_schedule()            int64    [point]           ``sex``, ``occ_class`` and
                                                           ``deferred_weeks``, decoded:
                                                           20 x sex + 5 x (class - 1) +
                                                           deferred period
mort_schedule()                 int64    [point]           ``sex``, decoded: M 0, F 1
escalation_rpi()                int64    [point]           ``escalation``, decoded: RPI 1,
                                                           none 0
recovery_code()                 int64    [point]           ``recovery_basis``, decoded:
                                                           return_to_h 0, exit 1
benefit_mth()                   float64  [point]           ``benefit_mth``
earnings_annual()               float64  [point]           ``earnings_annual``
premium_mth()                   float64  [point]           ``premium_mth``
policy_count()                  float64  [point]           ``policy_count``
duration_mth()                  int64    [point]           ``duration_mth``
pols_active_init()              float64  [point]           ``pols_active_init``
benefit_pp_init()               float64  [point]           ``benefit_pp_init``
premium_pp_init()               float64  [point]           ``premium_pp_init``
rate_age_first()                int      scalar            ``rate_age_min``, checked
rate_age_last()                 int      scalar            ``rate_age_max``
inception_array()               float64  [schedule, age]   *inception_table.csv*
mort_age_first()                int      scalar            *mort_table.csv*, checked
mort_age_last()                 int      scalar            *mort_table.csv*
mort_table_array()              float64  [sex, age]        *mort_table.csv*
termination_last_year()         int      scalar            *termination_table.csv*, checked
recovery_rate_array()           float64  [year]            *termination_table.csv*
mort_rate_sick_array()          float64  [year]            *termination_table.csv*
lapse_last_year()               int      scalar            *lapse_table.csv*, checked
lapse_rate_array()              float64  [year]            *lapse_table.csv*
cohort_z_last()                 int      scalar            *inforce_cohorts_sec.csv*
cohort_z_max()                  int64    [point]           *inforce_cohorts_sec.csv*
cohort_share()                  float64  [point, z]        *inforce_cohorts_sec.csv*
==============================  =======  ================  =================================

**An array is read by element, never whole,** in this Space as in
:mod:`~.IP_UK_SEC.Projection`. The compiler types an array cell as a memoryview only once
it has seen that every use of it, in either Space, is an element read: one ``len()``,
slice, loop over it or numpy call on it anywhere, and the cell compiles as a Python object.
So an array derived here reads the table's column, never another cell's array, and a width
comes from a table.

**What cannot be held is refused** when the table is first read, naming every point or
line at fault, beside the checks above: a ``point_id`` that is not a whole number below
``2**53`` in size, when :func:`point_id` is first read, as a refusal reads it; an
``entry_age``, an ``expiry_age`` or a ``duration_mth`` that is not below ``2**53`` in size,
by :func:`model_point_table` itself; and a key of an assumption table or of the claim
cohorts ``2**53`` or more in size, by the table's check, each of which numpy would
otherwise cast to int64 inexactly, or to the least int64, without a word. A fraction of a
year of age truncates, as :mod:`~.IP_UK_S`'s ``int`` truncates it.

**Three References are floats, though each is a whole number:** ``future_horizon_mth``,
``rate_age_min`` and ``rate_age_max``, as ``Projection``'s four contract ages are. A
compiled model holds an int Reference as a C integer, which truncates a fraction set on
it as it is set, so that 12.5 would read as 12 compiled where modelx refuses it; held as
a float, the fraction is the fraction in either engine, and the check that it is whole
refuses it in both, printing it as a float.
"""

from modelx.serialize.jsonvalues import *

_formula = None

_bases = []

_allow_none = None

_spaces = []

# ---------------------------------------------------------------------------
# Cells

def input_dir():
    """The directory holding the input CSVs: the model folder's parent.

    Inputs are *external* files, not data stored inside the model, so the model
    folder is pure formulas.  The path is resolved at run time from where the model
    was read, following ``annuallife.TradLife_A``.
    """
    return _model.path.parent                                        # noqa: F821


def model_point_table():
    """The model point table, read from *model_point_table_sec.csv* and checked.

    Indexed by ``point_id``. Five columns are the in-force interface: ``policy_count``
    and ``duration_mth``, the completed policy months at the valuation date, as in
    ``basiclife.BasicTerm_SE``, and the three of a point's opening state. The rest are
    :mod:`~.IP_UK_S`'s, but ``pols_if_init``, which ``policy_count`` replaces,
    ``claim_duration_months``, which the claim cohorts replace, and ``row_kind``,
    ``source_policy_id``, ``source_mth`` and ``source_refs``, which record where the
    generator took each shipped row from, and under what References, and which no formula
    reads.  :mod:`~.IP_UK_S`'s ``status`` is kept as a label, which no formula reads
    either, so an extract may leave it out.

    The checks run over the whole table at once, and the first that fails raises
    ``ValueError``, naming the missing column or every point it fails on:

    1. the five in-force columns are present, and the eleven of :mod:`~.IP_UK_S`'s the
       projection reads: ``entry_age``, ``sex``, ``occ_class``, ``benefit_mth``,
       ``earnings_annual``, ``deferred_weeks``, ``expiry_age``, ``escalation``,
       ``premium_mth``, ``premium_basis`` and ``recovery_basis``;
    2. no ``point_id`` appears twice;
    3. ``policy_count`` is a number, zero or more: the policies in force, healthy and in
       claim, or the policies issued;
    4. ``duration_mth`` is a whole number of months, below ``2**53`` in size, which numpy
       would otherwise cast to the least int64 without a word: positive for a policy in
       force, 0 for one issued at the valuation date, negative for one issued later;
    5. no policy is issued more than ``future_horizon_mth`` months after the valuation
       date, so ``duration_mth`` is ``-future_horizon_mth`` or more. At 0 the model takes
       no future new business, and the message says so; a horizon that is not a whole
       number of months, 0 or more, below ``2**53``, is itself refused, since a NaN one
       fails every comparison and so would admit every policy, and an infinite one bounds
       nothing;
    6. the opening state is a number in its range: ``pols_active_init``, a share of the
       count, from 0 to 1; ``benefit_pp_init`` and ``premium_pp_init``, amounts, 0 or
       more;
    7. ``sex`` is M or F, ``escalation`` RPI or none and ``recovery_basis`` return_to_h
       or exit, the codes the formulas branch on and the tables are keyed by; ``status``,
       where the table has it, active or in_claim; and ``premium_basis`` is guaranteed,
       the one basis the model prices, which :mod:`~.IP_UK_S` checks in a cell no formula
       calls;
    8. ``occ_class`` is a whole number from 1 to 4, a CMI occupation class, and
       ``deferred_weeks`` one of the deferred periods 4, 8, 13, 26 and 52, which key the
       inception table;
    9. ``entry_age`` and ``expiry_age`` are finite numbers, which :mod:`~.IP_UK_S` reads
       with ``int``, below ``2**53`` in size; and ``benefit_mth``, ``earnings_annual`` and
       ``premium_mth`` numbers, zero or more;
    10. a policy not yet in force, ``duration_mth`` 0 or less, holds the issue values:
        the whole count healthy, ``pols_active_init`` 1, since new business is issued
        healthy, and the benefit and the premium at issue as its benefit and premium;
    11. a policy in force 12 months or fewer holds the benefit and the premium at issue:
        the columns are measured before month 0's events, so on the first anniversary
        they are still the first year's, the increase it makes the projection's;
    12. without escalation the benefit and the premium are those at issue, which never
        move; with RPI escalation they are those or more, to half a cent, each increase
        being floored at 0.

    Rule 12's bound on an escalating point holds each amount to the cent, within half a
    cent of its bound, so that an extract rounded to the cent reads: its history is
    computed and rounded by the extract's own system.  The equalities compare exactly:
    there the opening amount is no history but the contract's own first year's, and an
    extract writes the same number in both columns.  Each rule of the history holds of
    every state :mod:`~.IP_UK_S` reaches, under any References: the relations it states
    are the contract's.  The history's upper bounds, an increase at most the cap and the
    premium's increases ``esc_prem_mult`` times the benefit's, read References, which
    this Space cannot see, so ``Projection.proj_len`` holds them.  Rule 12 refuses one
    state :mod:`~.IP_UK_S` cannot reach either: a point whose escalation option has lapsed
    after increases refused, its benefit above its benefit at issue and its escalation
    none.  The model has no representation of a lapsed option, which would project the
    increases already given and no more.
    """
    name = model_point_file                                          # noqa: F821
    table = pd.read_csv(input_dir() / name, index_col="point_id")    # noqa: F821
    state_columns = ("pols_active_init", "benefit_pp_init", "premium_pp_init")
    read_columns = ("entry_age", "sex", "occ_class", "benefit_mth", "earnings_annual",
                    "deferred_weeks", "expiry_age", "escalation", "premium_mth",
                    "premium_basis", "recovery_basis")
    for column in ("policy_count", "duration_mth", *state_columns, *read_columns):
        if column not in table.columns:
            raise ValueError(f"{name} has no {column} column")
    repeated = table.index[table.index.duplicated()].unique().tolist()
    if repeated:
        raise ValueError(f"{name}: point_id {repeated} appears more than once")
    count = pd.to_numeric(table["policy_count"], errors="coerce")    # noqa: F821
    bad = table.index[~((count >= 0) & (count < float("inf")))].tolist()
    if bad:
        raise ValueError(f"{name}: policy_count must be a number, zero or more; it is "
                         f"not at point_id {bad}")
    months = pd.to_numeric(table["duration_mth"], errors="coerce")   # noqa: F821
    bad = table.index[~(months % 1 == 0)].tolist()
    if bad:
        raise ValueError(f"{name}: duration_mth must be a whole number of months; it "
                         f"is not at point_id {bad}")
    bad = table.index[~(months.abs() < 2.0 ** 53)].tolist()
    if bad:
        raise ValueError(f"{name}: duration_mth must be below 2**53 months; it is not at "
                         f"point_id {bad}")
    horizon = future_horizon_mth                                     # noqa: F821
    if not (horizon >= 0 and horizon < 2.0 ** 53 and horizon % 1 == 0):
        raise ValueError(f"future_horizon_mth must be a whole number of months, 0 or more, "
                         f"below 2**53, not {float(horizon)}")
    # The horizon is printed through int(), never assigned it: compiled, a local takes one
    # C type, a double here, which would print 120.0 where modelx prints 120.
    bad = table.index[months < -horizon].tolist()
    if bad and horizon == 0:
        raise ValueError(f"{name}: duration_mth must be 0 or more: this model takes no "
                         f"future new business; it is not at point_id {bad}")
    if bad:
        raise ValueError(f"{name}: duration_mth must be -{int(horizon)} or more, a policy "
                         f"issued at most {int(horizon)} months after the valuation date; "
                         f"it is not at point_id {bad}")
    state = {}
    for column, low, high, rule in (
            ("pols_active_init", 0.0, 1.0, "a number from 0 to 1, a share of the count"),
            ("benefit_pp_init", 0.0, float("inf"), "a number, zero or more"),
            ("premium_pp_init", 0.0, float("inf"), "a number, zero or more")):
        v = pd.to_numeric(table[column], errors="coerce")            # noqa: F821
        bad = table.index[~((v >= low) & (v <= high) & (v < float("inf")))].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be {rule}; it is not at point_id "
                             f"{bad}")
        state[column] = v
    for column, codes in (("sex", ("M", "F")), ("escalation", ("RPI", "none")),
                          ("premium_basis", ("guaranteed",)),
                          ("status", ("active", "in_claim")),
                          ("recovery_basis", ("return_to_h", "exit"))):
        if column not in table.columns:                 # status, the one label, only
            continue
        bad = table.index[~table[column].isin(codes)].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be {' or '.join(codes)}; it is not "
                             f"at point_id {bad}")
    occ = pd.to_numeric(table["occ_class"], errors="coerce")         # noqa: F821
    bad = table.index[~occ.isin([1, 2, 3, 4])].tolist()
    if bad:
        raise ValueError(f"{name}: occ_class must be a whole number from 1 to 4; it is "
                         f"not at point_id {bad}")
    deferred = pd.to_numeric(table["deferred_weeks"], errors="coerce")  # noqa: F821
    bad = table.index[~deferred.isin([4, 8, 13, 26, 52])].tolist()
    if bad:
        raise ValueError(f"{name}: deferred_weeks must be 4, 8, 13, 26 or 52; it is not "
                         f"at point_id {bad}")
    numbers = {}
    for column, finite in (("entry_age", True), ("expiry_age", True),
                           ("benefit_mth", False), ("earnings_annual", False),
                           ("premium_mth", False)):
        v = pd.to_numeric(table[column], errors="coerce")            # noqa: F821
        if finite:
            bad = table.index[~((v > -float("inf")) & (v < float("inf")))].tolist()
            if bad:
                raise ValueError(f"{name}: {column} must be a finite number; it is not at "
                                 f"point_id {bad}")
            bad = table.index[~(v.abs() < 2.0 ** 53)].tolist()
            if bad:
                raise ValueError(f"{name}: {column} must be below 2**53 in size; it is "
                                 f"not at point_id {bad}")
        else:
            bad = table.index[~((v >= 0) & (v < float("inf")))].tolist()
            if bad:
                raise ValueError(f"{name}: {column} must be a number, zero or more; it is "
                                 f"not at point_id {bad}")
        numbers[column] = v
    issue = {"benefit_pp_init": numbers["benefit_mth"],
             "premium_pp_init": numbers["premium_mth"]}
    at_issue = {"benefit_pp_init": "the benefit at issue",
                "premium_pp_init": "the premium at issue"}
    bad = table.index[(months <= 0) & (state["pols_active_init"] != 1)].tolist()
    if bad:
        raise ValueError(f"{name}: pols_active_init must be 1 on a policy not yet in force, "
                         f"duration_mth 0 or less, which is issued healthy; it is not at "
                         f"point_id {bad}")
    for column in ("benefit_pp_init", "premium_pp_init"):
        bad = table.index[(months <= 0) & (state[column] != issue[column])].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be {at_issue[column]} on a policy not "
                             f"yet in force, duration_mth 0 or less; it is not at point_id "
                             f"{bad}")
    for column in ("benefit_pp_init", "premium_pp_init"):
        bad = table.index[(months > 0) & (months <= 12)
                          & (state[column] != issue[column])].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be {at_issue[column]} on a policy in "
                             f"force 12 months or fewer, whose amounts are its first "
                             f"policy year's, the first anniversary's increase being the "
                             f"projection's; it is not at point_id {bad}")
    cent = 0.005
    level = table["escalation"] == "none"
    for column in ("benefit_pp_init", "premium_pp_init"):
        bad = table.index[level & (state[column] != issue[column])].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be {at_issue[column]} on a point "
                             f"without escalation, which never escalates; it is not at "
                             f"point_id {bad}")
        bad = table.index[~level & ~(state[column] >= issue[column] - cent)].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be {at_issue[column]} or more, to half "
                             f"a cent, on a point with RPI escalation, each increase being "
                             f"floored at 0; it is not at point_id {bad}")
    return table


def inforce_cohorts():
    """The claim cohorts of each point in force, from *inforce_cohorts_sec.csv*, checked.

    Indexed by ``point_id`` and ``z``, both read by value as ints.  One row per claim
    duration in which a point in force holds lives in claim payment at the valuation
    instant, the start of month 0, recoveries already returned to health:
    ``pols_sick_dur_init`` is the share of the point's count, ``policy_count``, in claim
    at claim duration ``z`` months, cohort 1 being the claims that incepted at the end of
    month -1 and are not yet paid, :mod:`~.IP_UK_S`'s ``sick_cohorts`` at the valuation
    instant over its ``pols_if``.  ``point_id`` is the only key to a point, and nothing
    else in the file names one.  The file is sparse: a claim duration a point holds no
    row for holds no lives, so a point all healthy holds no row at all, and a claims
    extract one row per claim duration in payment.  ``Projection.pols_sick_dur_init``
    reads it, at every claim duration the cohort vector carries.

    The checks run over the whole file at once, by 8 rules in turn, and the first that
    fails raises ``ValueError``, naming the missing column or the lines, the header line 1,
    or for the last the points:

    1. the three columns are present;
    2. each of ``point_id`` and ``z`` is a whole number, below ``2**53`` in size;
    3. each ``point_id`` is a point of :func:`model_point_table`;
    4. no ``point_id`` and ``z`` appear together twice;
    5. its point is in force, ``duration_mth`` above 0: a point not yet in force is issued
       healthy, and holds no claim;
    6. ``z`` is from 1 to its point's ``duration_mth``: a claim incepts at the end of a
       month the policy is in force, so none is older than the policy;
    7. ``pols_sick_dur_init`` is a number from 0 to 1, a share of the count;
    8. each point in force holds a healthy share, ``pols_active_init``, and cohort shares
       that sum to 1 within 1e-10, the tolerance ``Projection.check_states`` holds the
       population identity to: they are the shares of one count, which the projection
       opens at, the healthy lives and those in claim.  A point holding no row is all
       healthy, its healthy share 1.  They are summed from the healthy share, then the
       point's cohorts in ``z`` order.
    """
    name = inforce_cohorts_file                                      # noqa: F821
    points = model_point_file                                        # noqa: F821
    table = pd.read_csv(input_dir() / name)                          # noqa: F821
    for column in ("point_id", "z", "pols_sick_dur_init"):
        if column not in table.columns:
            raise ValueError(f"{name} has no {column} column")
    keys = {}
    for column in ("point_id", "z"):
        v = pd.to_numeric(table[column], errors="coerce")            # noqa: F821
        bad = (table.index[~(v % 1 == 0)] + 2).tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be a whole number; it is not on "
                             f"line {bad}")
        bad = (table.index[~(v.abs() < 2.0 ** 53)] + 2).tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be below 2**53 in size; it is not "
                             f"on line {bad}")
        keys[column] = v.astype("int64")
    model_points = model_point_table()
    known = keys["point_id"].isin(model_points.index)
    bad = (table.index[~known] + 2).tolist()
    if bad:
        ids = sorted(set(keys["point_id"][~known].tolist()))
        raise ValueError(f"{name}: point_id {ids} on line {bad} is no point of {points}")
    pairs = pd.MultiIndex.from_arrays([keys["point_id"], keys["z"]])  # noqa: F821
    faults = []
    for p, z in sorted(set(pairs[pairs.duplicated()])):
        lines = (table.index[(keys["point_id"] == p) & (keys["z"] == z)] + 2).tolist()
        faults.append(f"point_id {p} z {z} is on line {lines}")
    if faults:
        raise ValueError(f"{name}: each point_id and z must have one row; "
                         + "; ".join(faults))
    months = pd.to_numeric(model_points["duration_mth"], errors="coerce")  # noqa: F821
    life = months.reindex(keys["point_id"].to_numpy()).to_numpy()
    bad = (table.index[~(life > 0)] + 2).tolist()
    if bad:
        raise ValueError(f"{name}: a row's point must be in force, duration_mth above 0: a "
                         f"point not yet in force is issued healthy; it is not on line "
                         f"{bad}")
    bad = (table.index[~((keys["z"] >= 1) & (keys["z"] <= life))] + 2).tolist()
    if bad:
        raise ValueError(f"{name}: z must be from 1 to its point's duration_mth, the "
                         f"months since issue at the valuation date; it is not on line "
                         f"{bad}")
    v = pd.to_numeric(table["pols_sick_dur_init"], errors="coerce")  # noqa: F821
    bad = (table.index[~((v >= 0) & (v <= 1))] + 2).tolist()
    if bad:
        raise ValueError(f"{name}: pols_sick_dur_init must be a number from 0 to 1, a "
                         f"share of the count; it is not on line {bad}")
    out = table.assign(point_id=keys["point_id"], z=keys["z"], pols_sick_dur_init=v)
    out = out.set_index(["point_id", "z"]).sort_index()
    healthy = pd.to_numeric(model_points["pols_active_init"],          # noqa: F821
                            errors="coerce")
    held = {p: float(share) for p, share in healthy[months > 0].items()}
    for (p, _), share in out["pols_sick_dur_init"].items():
        held[p] = held[p] + float(share)
    bad = [p for p, total in held.items() if not abs(total - 1.0) <= 1e-10]
    if bad:
        raise ValueError(f"{name}: a point's pols_active_init and its pols_sick_dur_init "
                         f"must sum to 1 within 1e-10, shares of one count; they do not at "
                         f"point_id {bad}")
    return out


def inception_table():
    """The claim inception rates, read from *inception_table.csv*, checked.

    Annual rates per life in state H, keyed by sex, occupation class, deferred period
    and pivot age - the IP11 Series parameterization.  A **[std]** proxy: the IP11
    values are restricted to CMI Authorised Users, and the file's ``provenance`` column
    marks which cells are the notes' own pivots and which come from a factor.  Sorted
    on read, because ``Projection.inception_rate`` slices it.

    :mod:`~.IP_UK_S`'s reader, indexed by sex, occupation class, deferred period and age
    and sorted, as it returns it.  Here the file is checked first, as read, so that each
    fault is named by its line, the header line 1, and the first rule that fails raises
    ``ValueError``:

    1. each occupation class, deferred period and age is a whole number below ``2**53``
       in size, read by its value, so ``35.0`` is 35, which numpy would otherwise cast to
       an int it is not;
    2. each sex is M or F, each occupation class 1 to 4 and each deferred period 4, 8, 13,
       26 or 52, the codes the model point table holds;
    3. each of the forty schedules, M and F by the four classes by the five deferred
       periods, holds two pivot ages or more, one row an age: ``Projection.inception_rate``
       interpolates between the two pivots about an age and extrapolates from the two at
       an end.  Every fault is named in one message: an age a schedule repeats with its
       lines, and a schedule with fewer than two;
    4. each ``inception_rate`` is a number from 0 to 1, a probability, which the cap's
       ``min`` reads.

    The pivot ages need not run without a gap, nor be the same in each schedule: each
    interpolation reads its own schedule's two pivots about an age.
    """
    name = inception_file                                            # noqa: F821
    tbl = pd.read_csv(input_dir() / name)                            # noqa: F821
    lines = tbl.index + 2
    keys = {}
    for column in ("occ_class", "deferred_weeks", "age"):
        v = pd.to_numeric(tbl[column], errors="coerce")              # noqa: F821
        bad = lines[(~((v % 1 == 0) & (v.abs() < 2.0 ** 53))).to_numpy()].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be a whole number below 2**53 in "
                             f"size; it is not on line {bad}")
        keys[column] = v.astype("int64")
    bad = lines[(~(tbl["sex"].isin(["M", "F"])
                   & keys["occ_class"].isin([1, 2, 3, 4])
                   & keys["deferred_weeks"].isin([4, 8, 13, 26, 52]))).to_numpy()].tolist()
    if bad:
        raise ValueError(f"{name}: sex must be M or F, occ_class 1 to 4, and deferred_weeks "
                         f"4, 8, 13, 26 or 52; they are not on line {bad}")
    ages = keys["age"]
    faults = []
    for s in ("M", "F"):
        for c in (1, 2, 3, 4):
            for w in (4, 8, 13, 26, 52):
                group = ((tbl["sex"] == s) & (keys["occ_class"] == c)
                         & (keys["deferred_weeks"] == w)).to_numpy()
                run = ages[group]
                for a in sorted(set(run[run.duplicated()])):
                    faults.append(f"sex {s}, occ_class {c}, deferred_weeks {w}, age {a} "
                                  f"repeats on lines "
                                  f"{lines[group & (ages == a).to_numpy()].tolist()}")
                held = len(set(run))
                if held < 2:
                    faults.append(f"sex {s}, occ_class {c}, deferred_weeks {w} holds {held} "
                                  + ("pivot age" if held == 1 else "pivot ages"))
    if faults:
        raise ValueError(f"{name}: each sex, occupation class and deferred period must hold "
                         f"two pivot ages or more, one row an age; " + "; ".join(faults))
    rates = pd.to_numeric(tbl["inception_rate"], errors="coerce")    # noqa: F821
    bad = lines[(~((rates >= 0) & (rates <= 1))).to_numpy()].tolist()
    if bad:
        raise ValueError(f"{name}: inception_rate must be a number from 0 to 1; it is not "
                         f"on line {bad}")
    return tbl.set_index(["sex", "occ_class", "deferred_weeks", "age"]).sort_index()


def termination_table():
    """The claim termination rates, read from *termination_table.csv*.

    Annual recovery and in-claim mortality rates by claim duration year.  IP11 splits
    terminations into recovery and death exactly this way, but is two-dimensional in
    age and duration; the age dimension is suppressed here **[std]**.
    :mod:`~.IP_UK_S`'s reader, indexed as it is, from the one read of the file,
    :func:`termination_table_rows`; :func:`termination_last_year` checks the table.
    """
    return termination_table_rows().set_index("claim_duration_year")


def termination_table_rows():
    """*termination_table.csv* as the file holds it: one row a line, in the file's order.

    The one read of the file.  :func:`termination_last_year` checks it here, so that each
    refusal names the lines at fault, the header line 1, and so that what it checks is the
    file, whatever :func:`termination_table`, the reader the projection indexes into,
    makes of it.
    """
    return pd.read_csv(input_dir() / termination_file)               # noqa: F821


def termination_last_year():
    """The last claim duration year *termination_table.csv* gives rates for, checked first.

    ``Projection.rec_rate`` and ``Projection.mort_rate_sick`` ask it before they read the
    table, and read every later duration year at it, :mod:`~.IP_UK_S`'s
    ``tbl.index.max()``: the shipped table's "5+" row.  The rules, the first that fails
    raising ``ValueError`` and naming the lines, the header line 1: each claim duration
    year is a whole number below ``2**53`` in size, read by its value; the years run from
    1, one row a year,
    without a gap or a repeat, since each duration year from the first is read, every
    fault named in one message, a year below 1 and a repeated one each with its lines, and
    each span the table lacks; and each ``recovery_rate`` and ``mort_rate_sick`` is a
    number from 0 to 1, a probability, which the recovery rate's ``min`` and the in-claim
    mortality's cap read.
    """
    name = termination_file                                          # noqa: F821
    tbl = termination_table_rows()
    lines = tbl.index + 2
    years = pd.to_numeric(tbl["claim_duration_year"], errors="coerce")  # noqa: F821
    bad = lines[(~((years % 1 == 0) & (years.abs() < 2.0 ** 53))).to_numpy()].tolist()
    if bad:
        raise ValueError(f"{name}: claim_duration_year must be a whole number below 2**53 "
                         f"in size; it is not on line {bad}")
    keys = years.astype("int64")
    faults = []
    for y in sorted(set(keys[keys < 1])):
        faults.append(f"claim_duration_year {y}, below 1, is on lines "
                      f"{lines[(keys == y).to_numpy()].tolist()}")
    for y in sorted(set(keys[keys.duplicated() & (keys >= 1)])):
        faults.append(f"claim_duration_year {y} repeats on lines "
                      f"{lines[(keys == y).to_numpy()].tolist()}")
    held = [int(y) for y in sorted(set(keys[keys >= 1]))]
    spans, before = [], 0
    for y in held:
        if y > before + 1:
            spans.append([before + 1, y - 1])
        before = y
    if not held:
        spans.append([1, 1])
    for low, high in spans:
        faults.append("no line holds " + (f"claim duration years {low} to {high}"
                                          if high > low else f"claim_duration_year {low}"))
    if faults:
        raise ValueError(f"{name}: the claim duration years must run from 1, one row a "
                         f"year, without a gap or a repeat; " + "; ".join(faults))
    for column in ("recovery_rate", "mort_rate_sick"):
        rates = pd.to_numeric(tbl[column], errors="coerce")          # noqa: F821
        bad = lines[(~((rates >= 0) & (rates <= 1))).to_numpy()].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be a number from 0 to 1; it is not on "
                             f"line {bad}")
    return int(held[-1])


def mort_table():
    """The active-life mortality rates by sex and age, from *mort_table.csv*.

    A **[std]** proxy shaped like the ONS UK national life tables, which are the only
    freely redistributable UK mortality source; population mortality is heavier than
    insured experience, and active-life mortality is a minor decrement in income
    protection anyway, so the shipped rates are a placeholder to be replaced with
    portfolio experience.  :mod:`~.IP_UK_S`'s reader, indexed and sorted as it is, from
    the one read of the file, :func:`mort_table_rows`; :func:`mort_age_first` checks the
    table.
    """
    return mort_table_rows().set_index(["sex", "age"]).sort_index()


def mort_table_rows():
    """*mort_table.csv* as the file holds it: one row a line, in the file's order.

    The one read of the file.  :func:`mort_age_first` checks it here, so that each refusal
    names the lines at fault, the header line 1, which the sort of :func:`mort_table`, the
    reader the projection indexes into, would lose.
    """
    return pd.read_csv(input_dir() / mort_table_file)                # noqa: F821


def mort_age_first():
    """The first attained age *mort_table.csv* gives a rate for, the table checked first.

    ``Projection.mort_rate`` asks it, and :func:`mort_age_last`, before it reads the
    table, so a table it cannot read is refused before any value of it is.  The check
    reads the file as it stands, :func:`mort_table_rows`, not :func:`mort_table`, which
    sorts it, so that each refusal names the lines at fault, the header line 1.  The
    rules, each over the whole table, the first that fails raising ``ValueError``:

    1. each age is a whole number below ``2**53`` in size, read by its value, so ``35.0``
       is 35;
    2. each sex is M or F, the codes the model point table holds;
    3. each sex runs over the table's ages from the first to the last, one row an age,
       none below 0: the projection reads a rate at each attained age a policy reaches.
       Every fault is named in one message: an age below 0 and an age a sex repeats each
       with its lines, and each span of ages a sex lacks;
    4. each ``mort_rate`` is a number from 0 to 1, a probability, read by the cap.
    """
    name = mort_table_file                                           # noqa: F821
    tbl = mort_table_rows()
    lines = tbl.index + 2
    ages = pd.to_numeric(tbl["age"], errors="coerce")                # noqa: F821
    bad = lines[(~((ages % 1 == 0) & (ages.abs() < 2.0 ** 53))).to_numpy()].tolist()
    if bad:
        raise ValueError(f"{name}: age must be a whole number below 2**53 in size; it is "
                         f"not on line {bad}")
    bad = lines[(~tbl["sex"].isin(["M", "F"])).to_numpy()].tolist()
    if bad:
        raise ValueError(f"{name}: sex must be M or F; it is not on line {bad}")
    ages = ages.astype("int64")
    faults = []
    for a in sorted(set(ages[ages < 0])):
        faults.append(f"age {a}, below 0, is on lines "
                      f"{lines[(ages == a).to_numpy()].tolist()}")
    kept = ages[ages >= 0]
    if kept.empty:
        raise ValueError(f"{name}: no line holds an age of 0 or more")
    first, last = int(kept.min()), int(kept.max())
    for s in ("M", "F"):
        group = ((tbl["sex"] == s) & (ages >= 0)).to_numpy()
        run = ages[group]
        for a in sorted(set(run[run.duplicated()])):
            faults.append(f"sex {s}, age {a} repeats on lines "
                          f"{lines[group & (ages == a).to_numpy()].tolist()}")
        spans, before = [], first - 1
        for a in [int(a) for a in sorted(set(run))]:
            if a > before + 1:
                spans.append([before + 1, a - 1])
            before = a
        if before < last:
            spans.append([before + 1, last])
        for low, high in spans:
            faults.append(f"no line holds sex {s}, "
                          + (f"ages {low} to {high}" if high > low else f"age {low}"))
    if faults:
        raise ValueError(f"{name}: the ages of each sex must run from {first} to {last}, "
                         f"the table's first and last, one row an age, none below 0; "
                         + "; ".join(faults))
    rates = pd.to_numeric(tbl["mort_rate"], errors="coerce")         # noqa: F821
    bad = lines[(~((rates >= 0) & (rates <= 1))).to_numpy()].tolist()
    if bad:
        raise ValueError(f"{name}: mort_rate must be a number from 0 to 1; it is not on "
                         f"line {bad}")
    return first


def mort_age_last():
    """The last attained age *mort_table.csv* gives a rate for, read once
    :func:`mort_age_first` has checked the table."""
    mort_age_first()
    ages = pd.to_numeric(mort_table_rows()["age"], errors="coerce")  # noqa: F821
    return int(ages.max())


def lapse_table():
    """The lapse rates by policy year, read from *lapse_table.csv*.

    ``policy_year`` is the contractual 1-based label (1 for the first policy year), not
    the projection's 0-based month index; ``Projection.lapse_rate_base`` reads it at
    ``policy_year(t)`` on the policy clock.  :mod:`~.IP_UK_S`'s reader, indexed as it is,
    from the one read of the file, :func:`lapse_table_rows`; :func:`lapse_last_year`
    checks the table.
    """
    return lapse_table_rows().set_index("policy_year")


def lapse_table_rows():
    """*lapse_table.csv* as the file holds it: one row a line, in the file's order.

    The one read of the file.  :func:`lapse_last_year` checks it here, so that each
    refusal names the lines at fault, the header line 1.
    """
    return pd.read_csv(input_dir() / lapse_table_file)               # noqa: F821


def lapse_last_year():
    """The last policy year *lapse_table.csv* gives a rate for, the table checked first.

    ``Projection.lapse_rate_base`` asks it before it reads the table, and reads every
    later policy year at it, :mod:`~.IP_UK_S`'s ``tbl.index.max()``.  The rules, the
    first that fails raising ``ValueError`` and naming the lines, the header line 1: each
    policy year is a whole number below ``2**53`` in size, read by its value; the years run
    from 1, one row a year, without a gap or a repeat, since each policy year from the
    first is read, every
    fault named in one message, a year below 1 and a repeated one each with its lines, and
    each span the table lacks; and each ``lapse_rate`` is a number from 0 to 1, a
    probability, which the lapse rate's ``min`` reads.
    """
    name = lapse_table_file                                          # noqa: F821
    tbl = lapse_table_rows()
    lines = tbl.index + 2
    years = pd.to_numeric(tbl["policy_year"], errors="coerce")       # noqa: F821
    bad = lines[(~((years % 1 == 0) & (years.abs() < 2.0 ** 53))).to_numpy()].tolist()
    if bad:
        raise ValueError(f"{name}: policy_year must be a whole number below 2**53 in size; "
                         f"it is not on line {bad}")
    keys = years.astype("int64")
    faults = []
    for y in sorted(set(keys[keys < 1])):
        faults.append(f"policy_year {y}, below 1, is on lines "
                      f"{lines[(keys == y).to_numpy()].tolist()}")
    for y in sorted(set(keys[keys.duplicated() & (keys >= 1)])):
        faults.append(f"policy_year {y} repeats on lines "
                      f"{lines[(keys == y).to_numpy()].tolist()}")
    held = [int(y) for y in sorted(set(keys[keys >= 1]))]
    spans, before = [], 0
    for y in held:
        if y > before + 1:
            spans.append([before + 1, y - 1])
        before = y
    if not held:
        spans.append([1, 1])
    for low, high in spans:
        faults.append("no line holds " + (f"policy years {low} to {high}" if high > low
                                          else f"policy_year {low}"))
    if faults:
        raise ValueError(f"{name}: the policy years must run from 1, one row a year, "
                         f"without a gap or a repeat; " + "; ".join(faults))
    rates = pd.to_numeric(tbl["lapse_rate"], errors="coerce")        # noqa: F821
    bad = lines[(~((rates >= 0) & (rates <= 1))).to_numpy()].tolist()
    if bad:
        raise ValueError(f"{name}: lapse_rate must be a number from 0 to 1; it is not on "
                         f"line {bad}")
    return int(held[-1])


def point_id():
    """The ``point_id`` of every model point, in table order: int64 [point].

    ``Projection`` is indexed by position, ``idx``, so this is how a projection names its
    point: ``Projection.point_id()`` is the element at ``idx``, and every refusal quotes
    it.  Read by value, so that a label written ``3.0`` is 3, and refused when it is first
    read, naming every label at fault, where one is not a whole number, text and a blank
    among them, or is ``2**53`` or more in size.  A projection that names no point reads
    no label, and runs.
    """
    table = model_point_table()
    labels = pd.to_numeric(pd.Series(table.index), errors="coerce")  # noqa: F821
    bad = table.index[~(labels % 1 == 0).to_numpy()].tolist()
    if bad:
        raise ValueError(f"{model_point_file}: point_id must be a whole "  # noqa: F821
                         f"number; {bad} is not")
    bad = table.index[~(labels.abs() < 2.0 ** 53).to_numpy()].tolist()
    if bad:
        raise ValueError(f"{model_point_file}: point_id must be below 2**53 "  # noqa: F821
                         f"in size; {bad} is not")
    return labels.to_numpy(dtype="int64")


def entry_age():
    """The entry age (ANB) of every model point: int64 [point].

    Read as :mod:`~.IP_UK_S` reads it, ``int`` of the number, which truncates a fraction;
    :func:`model_point_table` has refused one that is not a finite number below ``2**53``
    in size.
    """
    ages = pd.to_numeric(model_point_table()["entry_age"])           # noqa: F821
    return ages.to_numpy(dtype="int64")


def expiry_age():
    """The expiry age of every model point: int64 [point].

    Read as :mod:`~.IP_UK_S` reads it, ``int`` of the number, as :func:`entry_age` is;
    :func:`model_point_table` has refused one that is not a finite number below ``2**53``
    in size.
    """
    ages = pd.to_numeric(model_point_table()["expiry_age"])          # noqa: F821
    return ages.to_numpy(dtype="int64")


def occ_class():
    """The CMI occupation class of every model point, 1 to 4: int64 [point].

    :func:`model_point_table` has refused any value that is not 1, 2, 3 or 4, so each is
    whole, read by its value.
    """
    classes = pd.to_numeric(model_point_table()["occ_class"])        # noqa: F821
    return classes.to_numpy(dtype="int64")


def deferred_weeks():
    """The deferred period in weeks of every model point, 4, 8, 13, 26 or 52: int64
    [point].

    :func:`model_point_table` has refused any other value, so each is whole, read by its
    value.
    """
    weeks = pd.to_numeric(model_point_table()["deferred_weeks"])     # noqa: F821
    return weeks.to_numpy(dtype="int64")


def inception_schedule():
    """The inception table's row for every model point: int64 [point].

    The point's sex, occupation class and deferred period, the keys :mod:`~.IP_UK_S` reads
    *inception_table.csv* by beside the age, numbered as :func:`inception_array` tables
    them: ``20 x sex + 5 x (occ_class - 1) + deferred``, the sex M 0 and F 1, and the
    deferred periods 4, 8, 13, 26 and 52 weeks 0 to 4, so 0 to 39, in the order
    :func:`inception_table` checks the schedules.  :func:`model_point_table` has refused
    any other sex, class or period, so every point has one of the forty, each of which
    :func:`inception_table` holds to two pivot ages or more.
    """
    table = model_point_table()
    sexes = table["sex"].tolist()
    classes = pd.to_numeric(table["occ_class"]).tolist()             # noqa: F821
    weeks = pd.to_numeric(table["deferred_weeks"]).tolist()          # noqa: F821
    out = np.zeros(len(sexes), dtype="int64")                        # noqa: F821
    for i in range(len(sexes)):
        out[i] = (20 * ("M", "F").index(sexes[i]) + 5 * (int(classes[i]) - 1)
                  + (4, 8, 13, 26, 52).index(int(weeks[i])))
    return out


def mort_schedule():
    """The mortality table's row for every model point: int64 [point], M 0 and F 1.

    The point's sex, the key :mod:`~.IP_UK_S` reads *mort_table.csv* by beside the age,
    numbered as :func:`mort_table_array` tables it.  :func:`model_point_table` has refused
    any other sex.
    """
    sexes = model_point_table()["sex"].tolist()
    out = np.zeros(len(sexes), dtype="int64")                        # noqa: F821
    for i in range(len(sexes)):
        out[i] = ("M", "F").index(sexes[i])
    return out


def escalation_rpi():
    """Whether each model point elects RPI escalation: int64 [point], 1 or 0.

    :mod:`~.IP_UK_S` compares the ``escalation`` column's text with ``"RPI"``.
    :func:`model_point_table` has refused any value whose text is not exactly RPI or none,
    a blank, a number, ``True`` and the codes with a space or in another case among them,
    so each is decoded by its text, element by element: 1 where it is RPI, 0 where it is
    none, the decode's one rule.  An int, not a bool: a numpy bool array compiles as a
    Python object, not a memoryview.
    """
    codes = model_point_table()["escalation"].tolist()
    out = np.zeros(len(codes), dtype="int64")                        # noqa: F821
    for i in range(len(codes)):
        out[i] = ("none", "RPI").index(codes[i])
    return out


def recovery_code():
    """The recovery basis of every model point, as its code: int64 [point].

    return_to_h 0 and exit 1, ``Projection``'s References ``RETURN_TO_H`` and ``EXIT``,
    which :mod:`~.IP_UK_S`'s ``pols_active``, ``pols_exit`` and ``pols_maturity`` compare
    the text by.  :func:`model_point_table` has refused any other basis.
    """
    codes = model_point_table()["recovery_basis"].tolist()
    out = np.zeros(len(codes), dtype="int64")                        # noqa: F821
    for i in range(len(codes)):
        out[i] = ("return_to_h", "exit").index(codes[i])
    return out


def benefit_mth():
    """The monthly benefit at issue of every model point: float64 [point]."""
    return pd.to_numeric(model_point_table()["benefit_mth"]).to_numpy(  # noqa: F821
        dtype="float64")


def earnings_annual():
    """The annual earnings on the underwriting record of every model point: float64
    [point]."""
    return pd.to_numeric(                                            # noqa: F821
        model_point_table()["earnings_annual"]).to_numpy(dtype="float64")


def premium_mth():
    """The monthly premium at issue of every model point: float64 [point]."""
    return pd.to_numeric(model_point_table()["premium_mth"]).to_numpy(  # noqa: F821
        dtype="float64")


def policy_count():
    """The ``policy_count`` of every model point, healthy and in claim: float64 [point].

    :func:`model_point_table` has checked it: a number, zero or more.
    """
    return pd.to_numeric(model_point_table()["policy_count"]).to_numpy(  # noqa: F821
        dtype="float64")


def duration_mth():
    """The ``duration_mth`` of every model point, in whole months: int64 [point].

    :func:`model_point_table` has checked that each is whole and below ``2**53`` in size,
    so a duration written as ``60.0`` is the int 60.
    """
    months = pd.to_numeric(model_point_table()["duration_mth"])      # noqa: F821
    return months.to_numpy(dtype="int64")


def pols_active_init():
    """The healthy share of the count at the valuation date, of every model point: float64
    [point]."""
    return pd.to_numeric(                                            # noqa: F821
        model_point_table()["pols_active_init"]).to_numpy(dtype="float64")


def benefit_pp_init():
    """The monthly benefit entering month 0, of every model point: float64 [point]."""
    return pd.to_numeric(                                            # noqa: F821
        model_point_table()["benefit_pp_init"]).to_numpy(dtype="float64")


def premium_pp_init():
    """The monthly premium entering month 0, of every model point: float64 [point]."""
    return pd.to_numeric(                                            # noqa: F821
        model_point_table()["premium_pp_init"]).to_numpy(dtype="float64")


def rate_age_first():
    """The first attained age the inception array holds a rate at, ``rate_age_min``,
    checked.

    ``Projection.inception_rate`` asks it, and :func:`rate_age_last`, before it reads the
    array, and :func:`inception_array` is built from the two, so that a table or an extent
    this cannot read is refused before any rate is.  It asks :func:`inception_table` first,
    which checks the pivot table, and then refuses ``rate_age_min`` and ``rate_age_max``
    unless each is a whole number, ``rate_age_min`` 0 or more and ``rate_age_max`` no less:
    they are the extent of an array indexed by the attained age.

    The two are the attained ages the contract admits, ``Projection.issue_age_min``, 18, to
    ``Projection.expiry_age_max`` less one, 69, which this Space cannot read, and so holds as
    References of its own; a test holds the two to the contract.  A contract whose bounds
    are moved past them needs them moved too: an age outside them is refused by the cell
    that reads it, naming the point and the age, where :mod:`~.IP_UK_S` extrapolated.
    """
    inception_table()
    low, high = rate_age_min, rate_age_max                           # noqa: F821
    if not (low >= 0 and low % 1 == 0 and high % 1 == 0 and high >= low):
        raise ValueError(
            f"rate_age_min and rate_age_max must be whole numbers, 0 <= rate_age_min <= "
            f"rate_age_max; they are {float(low)} and {float(high)}")
    return int(low)


def rate_age_last():
    """The last attained age the inception array holds a rate at, ``rate_age_max``, read
    once :func:`rate_age_first` has checked the table and the two."""
    rate_age_first()
    return int(rate_age_max)                                         # noqa: F821


def inception_array():
    """The annual inception rate by schedule and attained age, from *inception_table.csv*:
    float64 [schedule, age].

    Row ``s`` is a sex, an occupation class and a deferred period, ``20 x sex + 5 x
    (occ_class - 1) + deferred``, as :func:`inception_schedule` numbers each point's, the
    sex M 0 and F 1 and the deferred periods 4, 8, 13, 26 and 52 weeks 0 to 4; column
    ``x`` the attained age ``x``: padded from age 0, as ``basiclife.BasicTerm_SC``'s
    ``mort_table_array`` pads its table, so that the index **is** the age, and
    :func:`rate_age_last` plus one wide, 70 as shipped.  Each age from
    :func:`rate_age_first` to :func:`rate_age_last` holds :mod:`~.IP_UK_S`'s inception
    rate before the overlay and the cap, ``max(0.0, r)``, built here by its own formula,
    element by element, on Python floats, so that each element is the float its cell
    computes: linear between the schedule's two pivot ages about ``x``,
    ``r_lo + (r_hi - r_lo) (x - lo) / (hi - lo)``, extrapolated from the two at the nearer
    end outside them, and floored at 0, since linear extrapolation below the first pivot
    can go negative.  ``Projection.inception_rate`` multiplies it by the overlay and caps
    it, as :mod:`~.IP_UK_S` does.  The ages below the first hold NaN, which no formula
    reads: ``Projection.inception_rate`` refuses an age outside the two, naming the point.
    Asks the two first, which check the pivot table, so each schedule holds two pivot
    ages or more, one row an age, and each rate is a number from 0 to 1, which keeps every
    element finite.
    """
    first, last = rate_age_first(), rate_age_last()
    tbl = inception_table()
    out = np.full((40, last + 1), np.nan)                            # noqa: F821
    for s, sex in enumerate(("M", "F")):
        for c in (1, 2, 3, 4):
            for w, weeks in enumerate((4, 8, 13, 26, 52)):
                sub = tbl.loc[(sex, c, weeks)]
                ages = sorted(int(a) for a in sub.index)
                for x in range(first, last + 1):
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
                    out[20 * s + 5 * (c - 1) + w, x] = max(0.0, r)
    return out


def mort_table_array():
    """The active-life annual mortality rates by sex and attained age, from
    *mort_table.csv*: float64 [sex, age].

    Row 0 is M and row 1 F, as :func:`mort_schedule` numbers each point's, and column
    ``a`` the attained age ``a``: padded from age 0, so that the index **is** the age, and
    :func:`mort_age_last` plus one wide.  The ages below the table's first, 0 to 15 as
    shipped, hold NaN, which no formula reads: ``Projection.mort_rate`` refuses an age
    outside the table, naming the point.  Asks :func:`mort_age_first` first, which checks
    the table: each sex runs over every age from the first to the last, one row an age, so
    no cell between them is padding, and each rate is a number from 0 to 1.  Read from the
    one read of the file, :func:`mort_table_rows`, which :mod:`~.IP_UK_S`'s reader sorts.
    """
    mort_age_first()
    last = mort_age_last()
    tbl = mort_table_rows()
    ages = pd.to_numeric(tbl["age"]).to_numpy(dtype="int64")         # noqa: F821
    rates = pd.to_numeric(tbl["mort_rate"]).to_numpy(dtype="float64")  # noqa: F821
    sexes = tbl["sex"].tolist()
    out = np.full((2, last + 1), np.nan)                             # noqa: F821
    for i in range(len(sexes)):
        out[("M", "F").index(sexes[i]), ages[i]] = rates[i]
    return out


def recovery_rate_array():
    """The annual recovery rate by claim duration year, from *termination_table.csv*:
    float64 [year].

    Element ``y`` is the rate of claim duration year ``y``, from 1 to
    :func:`termination_last_year`, which checks the table first: the years run from 1
    without a gap.  Element 0, no claim duration year, holds NaN, which no formula reads:
    ``Projection.rec_rate`` reads a year from 1 to the last, which it reads every later
    year at, as :mod:`~.IP_UK_S` does, and refuses one below 1.  Read from the one read of
    the file, :func:`termination_table_rows`.
    """
    last = termination_last_year()
    tbl = termination_table_rows()
    years = pd.to_numeric(tbl["claim_duration_year"]).to_numpy(dtype="int64")  # noqa: F821
    rates = pd.to_numeric(tbl["recovery_rate"]).to_numpy(dtype="float64")  # noqa: F821
    out = np.full(last + 1, np.nan)                                  # noqa: F821
    for i in range(len(years)):
        out[years[i]] = rates[i]
    return out


def mort_rate_sick_array():
    """The annual in-claim mortality rate by claim duration year, from
    *termination_table.csv*: float64 [year].

    :func:`recovery_rate_array`'s table of the ``mort_rate_sick`` column, padded at year 0
    with NaN, which ``Projection.mort_rate_sick`` never reads.
    """
    last = termination_last_year()
    tbl = termination_table_rows()
    years = pd.to_numeric(tbl["claim_duration_year"]).to_numpy(dtype="int64")  # noqa: F821
    rates = pd.to_numeric(tbl["mort_rate_sick"]).to_numpy(dtype="float64")  # noqa: F821
    out = np.full(last + 1, np.nan)                                  # noqa: F821
    for i in range(len(years)):
        out[years[i]] = rates[i]
    return out


def lapse_rate_array():
    """The annual lapse rate by policy year, from *lapse_table.csv*: float64 [policy
    year].

    Element ``y`` is the rate of policy year ``y``, from 1 to :func:`lapse_last_year`,
    which checks the table first: the years run from 1 without a gap.  Element 0, no
    policy year, holds NaN, which no formula reads: ``Projection.lapse_rate_base`` reads
    a policy year of cover, 1 or more, at most the last, which it reads every later year
    at, as :mod:`~.IP_UK_S` does.  Read from the one read of the file,
    :func:`lapse_table_rows`.
    """
    last = lapse_last_year()
    tbl = lapse_table_rows()
    years = pd.to_numeric(tbl["policy_year"]).to_numpy(dtype="int64")  # noqa: F821
    rates = pd.to_numeric(tbl["lapse_rate"]).to_numpy(dtype="float64")  # noqa: F821
    out = np.full(last + 1, np.nan)                                  # noqa: F821
    for i in range(len(years)):
        out[years[i]] = rates[i]
    return out


def cohort_z_last():
    """The last claim duration :func:`cohort_share` holds, the companion's largest ``z``;
    0 where it holds no row: an int.

    ``Projection.pols_sick_dur_init`` asks it before it reads the array, and reads a
    claim duration past it as no lives, 0.0, as it reads a claim duration a point holds no
    row for.  Asks :func:`inforce_cohorts` first, which checks the companion: each ``z`` is
    whole, from 1 to its point's months in force, and below ``2**53`` in size.
    """
    zs = inforce_cohorts().index.get_level_values("z")
    return int(zs.max()) if len(zs) else 0


def cohort_z_max():
    """The longest claim duration each model point's claim cohorts hold, 0 where it holds
    none: int64 [point].

    The largest ``z`` the companion holds at the point's ``point_id``, the point at
    position ``i`` of :func:`model_point_table`, as :func:`point_id` numbers them: 0 on a
    point not yet in force and on one in force all healthy.  ``Projection.claim_dur_live``
    reads it, the cohorts that can hold lives, which the projection's sums of the cohorts
    run to.  Read from :func:`inforce_cohorts`, which checks the companion.
    """
    table = inforce_cohorts()
    labels = model_point_table().index.tolist()
    position = {}
    for i in range(len(labels)):
        position[labels[i]] = i
    out = np.zeros(len(labels), dtype="int64")                       # noqa: F821
    for p, z in table.index:
        if int(z) > out[position[p]]:
            out[position[p]] = int(z)
    return out


def cohort_share():
    """The claim cohorts of every model point, by claim duration, from
    *inforce_cohorts_sec.csv*: float64 [point, z].

    Element ``[i, z]`` is the share of point ``i``'s count in claim at claim duration
    ``z``, the companion's ``pols_sick_dur_init`` at the point's ``point_id`` and ``z``, the
    point at position ``i`` of :func:`model_point_table`, as :func:`point_id` numbers them,
    and 0.0 where the companion holds no row, which holds no lives, as on every point not
    yet in force.  Column 0, no claim duration, holds NaN, which no formula reads:
    ``Projection.pols_sick_dur_init`` reads a claim duration from 1 to
    :func:`cohort_z_last`, the array's last column, and reads every other as no lives.
    Each row of the companion is placed by its keys, in whatever order the file holds them,
    as the generator joins them.

    As wide as the companion's largest claim duration and one, ``z`` being a key the file
    holds sparsely, a claim in payment at duration 300 holding one row, where uslib's
    ``IUL_US_SEC`` tables its ladder by slot, as wide as the most rows one point holds; the
    companion's check holds each ``z`` to its point's months in force, and
    ``Projection.proj_len`` every point projected to a cover of 624 months, so that every
    claim duration a projection reads is at most 623.
    """
    last = cohort_z_last()
    table = inforce_cohorts()
    labels = model_point_table().index.tolist()
    position = {}
    for i in range(len(labels)):
        position[labels[i]] = i
    out = np.zeros((len(labels), last + 1))                          # noqa: F821
    out[:, 0] = np.nan                                               # noqa: F821
    for (p, z), share in table["pols_sick_dur_init"].items():
        out[position[p], int(z)] = float(share)
    return out


# ---------------------------------------------------------------------------
# References

model_point_file = "model_point_table_sec.csv"

inforce_cohorts_file = "inforce_cohorts_sec.csv"

inception_file = "inception_table.csv"

termination_file = "termination_table.csv"

mort_table_file = "mort_table.csv"

lapse_table_file = "lapse_table.csv"

future_horizon_mth = 120.0

rate_age_min = 18.0

rate_age_max = 69.0

pd = ("Module", "pandas")

np = ("Module", "numpy")
