# modelx: pseudo-python
# This file is part of a modelx model.
# It can be imported as a Python module, but functions defined herein
# are model formulas and may not be executable as standard Python.

"""Input data shared by every by-policy projection.

The six input CSVs are read here, **once per model**, and referenced from
:mod:`~.IP_UK_SEC.Projection` as ``data``. :mod:`~.IP_UK_SEC.Projection` is parameterized
by ``point_id``, so each ``Projection[N]`` is a separate ItemSpace with its own cells
cache; if the readers lived there, every model point would re-read every file. Holding
them in an unparameterized Space reads each file once no matter how many policies are
projected.

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
the order would lose the lines.
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
    ``source_policy_id`` and ``source_mth``, which record where the generator took each
    shipped row from and which no formula reads.  :mod:`~.IP_UK_S`'s ``status`` is kept as
    a label, which no formula reads either, so an extract may leave it out.

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
                         f"below 2**53, not {horizon}")
    horizon = int(horizon)
    bad = table.index[months < -horizon].tolist()
    if bad and horizon == 0:
        raise ValueError(f"{name}: duration_mth must be 0 or more: this model takes no "
                         f"future new business; it is not at point_id {bad}")
    if bad:
        raise ValueError(f"{name}: duration_mth must be -{horizon} or more, a policy "
                         f"issued at most {horizon} months after the valuation date; it "
                         f"is not at point_id {bad}")
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
    held = sorted(set(keys[keys >= 1]))
    spans = []
    for y in sorted(set(range(1, max(held, default=1) + 1)) - set(held)):
        if spans and spans[-1][1] == y - 1:
            spans[-1][1] = y
        else:
            spans.append([y, y])
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
        spans = []
        for a in sorted(set(range(first, last + 1)) - set(run)):
            if spans and spans[-1][1] == a - 1:
                spans[-1][1] = a
            else:
                spans.append([a, a])
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
    held = sorted(set(keys[keys >= 1]))
    spans = []
    for y in sorted(set(range(1, max(held, default=1) + 1)) - set(held)):
        if spans and spans[-1][1] == y - 1:
            spans[-1][1] = y
        else:
            spans.append([y, y])
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


# ---------------------------------------------------------------------------
# References

model_point_file = "model_point_table_sec.csv"

inforce_cohorts_file = "inforce_cohorts_sec.csv"

inception_file = "inception_table.csv"

termination_file = "termination_table.csv"

mort_table_file = "mort_table.csv"

lapse_table_file = "lapse_table.csv"

future_horizon_mth = 120

pd = ("Module", "pandas")
