# modelx: pseudo-python
# This file is part of a modelx model.
# It can be imported as a Python module, but functions defined herein
# are model formulas and may not be executable as standard Python.

"""Input data shared by every by-policy projection.

The five input CSVs are read here, **once per model**, and referenced from
:mod:`~.Term_UK_SEC.Projection` as ``data``. :mod:`~.Term_UK_SEC.Projection` is
parameterized by ``point_id``, so each ``Projection[N]`` is a separate ItemSpace with
its own cells cache; if the readers lived there, every model point would re-read every
file. Holding them in an unparameterized Space reads each file once no matter how many
policies are projected.

Inputs are **external files**: plain CSVs in the model folder's parent directory,
``products/term_assurance/``, rather than data stored inside the model. The model
folder therefore holds nothing but formulas — no ``_data/``, no IOSpec, no embedded
values — so a diff of the model shows logic changes only. This follows
``annuallife.TradLife_A``; contrast ``basiclife.BasicTerm_S``, which keeps its inputs
*inside* the model through modelx's IOSpec machinery.

The consequence worth knowing: **the model is not portable on its own.** Copying the
``Term_UK_SEC`` folder without its parent's CSVs produces a model that reads and then
fails on first evaluation.

**Three of the tables are Term_UK_S's.** The mortality table, the select factors and the
lapse table are the files :mod:`~.Term_UK_S` reads, read here in place by
:mod:`~.Term_UK_S`'s own readers: one copy of each table serves both models, so an edit
to one reaches both. The model point table, ``model_point_table_sec.csv``, and the
waiver pipeline, ``wop_pipeline_sec.csv``, are this model's own; the first sits beside
:mod:`~.Term_UK_S`'s ``model_point_table.csv``, which this model never opens.

:func:`input_dir` resolves the directory from ``_model.path.parent`` at run time, so
the model works wherever the repository is checked out. Each table has a filename
Reference and a reader Cells:

======================  ==========================  ==============================
Reference               Cells                       File
======================  ==========================  ==============================
model_point_file        model_point_table()         model_point_table_sec.csv
wop_pipeline_file       wop_pipeline()              wop_pipeline_sec.csv
mort_table_file         mort_table()                mort_table.csv
select_factor_file      select_factor_table()       select_factor_table.csv
lapse_table_file        lapse_table()               lapse_table.csv
======================  ==========================  ==============================

**The model point table is checked as it is read.** Nine of its columns are the
in-force interface: ``policy_count`` and ``duration_mth``, as in
``basiclife.BasicTerm_SE``, and the opening state of a point in force, ``lapse_cum_init``,
``fib_cum_init``, ``fib_streams_init``, ``idx_factor_init``, ``idx_prem_factor_init``,
``wop_waived_frac_init`` and ``comm_init_pp_init``. :func:`model_point_table` refuses a
table that lacks one,
repeats a ``point_id``, holds a count, a duration or a state no policy can have, or a
policy to be issued more than ``future_horizon_mth`` months after the valuation date, 120
as shipped: future new business is written over a stated horizon, so that no frame runs
longer than cover from issue plus that horizon. Set to 0, the Reference refuses future new
business altogether. It refuses, too, what :mod:`~.Term_UK_S` projects without a word or
meets only when a projection reaches it: a flag that is not True or False, a code that
names no shape, sex, smoker status, premium mode or mortality basis, an age, a term or an
amount that is not a number in its range, a joint point with no second life, and
indexation off the level shape. The checks run in turn, and the first that fails raises,
naming the missing column or every point that fails it.

**The waiver pipeline is checked as it is read.** :func:`wop_pipeline` refuses a
companion row for a point the table lacks, for a point without the waiver rider, at a lag
that predates issue, twice for one point and lag, or with a deferred share that is not a
share of the policies in force. How many lags a point holds is a rule of the product,
since it is ``Projection.wop_defer_mths``, so ``Projection.proj_len`` checks it, from
:func:`wop_pipeline_count` and :func:`wop_pipeline_last`. Whether a point is still in
cover at the valuation date, and whether the contract issues it, are rules of the product
too, and ``Projection.proj_len`` checks them, against its own References.

**Each assumption table is checked before a value of it is read.** Its keys are read by
their value, so an age written ``35.0`` is age 35, and a key that is not whole, text among
them, is refused, naming the file, the column and its lines; so are keys that repeat or
leave a gap the projection would read, naming the keys. A value that is blank, text,
infinite or outside its range is refused, naming the file, the column and its lines,
whether or not a point reads it: ``Projection.mort_rate_life`` caps the annual rate with
``min``, which keeps its first argument unless a later one compares smaller, and no
comparison with NaN holds, so the cap is written with its bound second and a NaN would
stay NaN; but an infinity is a number, which the cap reads as 1, certain death. The check
of each table is in the cell the projection takes the table's extent from, which it asks
before it reads the table: :func:`mort_age_first` and :func:`mort_age_last` for the
mortality table, :func:`select_last_duration` for the select factors and
:func:`lapse_last_year` for the lapse table. A read beyond a table's extent is refused by
the one ``Projection`` cell that reads the table, naming the point, where
:mod:`~.Term_UK_S`'s lookup raised ``KeyError``.

To swap in a licensed mortality basis — the CMI "16" Series assured lives tables
TMNL16/TFNL16, which are subscriber-restricted and cannot be redistributed here —
replace ``mort_table.csv`` and ``select_factor_table.csv`` with same-schema files, or
point ``mort_table_file`` and ``select_factor_file`` at different names, then clear the
cache. No formula changes. Replacing a file changes :mod:`~.Term_UK_S` too, which reads
the same one.
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

    Indexed by ``point_id``. Nine columns are the in-force interface: ``policy_count``
    and ``duration_mth``, the completed policy months at the valuation date, as in
    ``basiclife.BasicTerm_SE``, and the seven of a point's opening state. The rest are
    :mod:`~.Term_UK_S`'s, but ``pols_if_init`` and ``duration_inforce``, which the first
    two replace, and ``row_kind``, ``source_policy_id`` and ``source_mth``, which record
    where the generator took each shipped row from and which no formula reads.

    The checks run over the whole table at once, and the first that fails raises
    ``ValueError``, naming the missing column or every point it fails on:

    1. the nine in-force columns are present;
    2. no ``point_id`` appears twice;
    3. ``policy_count`` is a number, zero or more;
    4. ``duration_mth`` is a whole number of months, below ``2**53`` in size, which numpy
       would otherwise cast to the least int64 without a word: positive for a policy in
       force, 0 for one issued at the valuation date, negative for one issued later;
    5. no policy is issued more than ``future_horizon_mth`` months after the valuation
       date, so ``duration_mth`` is ``-future_horizon_mth`` or more. At 0 the model takes
       no future new business, and the message says so; a negative horizon is itself
       refused;
    6. the opening state is a number in its range: ``lapse_cum_init``, a share of the
       issued cohort, from 0 to below 1, since a point with a policy in force has not
       lapsed whole; ``fib_cum_init`` and ``fib_streams_init``, deaths and streams per
       policy in force, 0 or more; the two indexation factors 1 or more, the RPI increase
       being floored at 0; ``wop_waived_frac_init``, a share of the policies in force,
       from 0 to 1; and ``comm_init_pp_init``, an amount, 0 or more;
    7. a policy not yet in force, ``duration_mth`` 0 or less, holds the issue values: 0
       for the lapse ratio, the deaths, the streams, the waived share and the commission,
       an event of the issue month, and 1 for the factors;
    8. each of ``joint_first_death``, ``indexation`` and ``wop`` is True or False. pandas
       reads a column of them as booleans, but one blank or one other text leaves the
       whole column text or mixed, and ``bool("False")`` is True;
    9. ``shape`` is level, decreasing or fib, ``sex`` M or F, ``smoker`` N or S,
       ``premium_mode`` monthly or annual and ``mort_basis`` applied or select;
    10. ``age_at_entry`` and ``policy_term`` are finite numbers, which
        :mod:`~.Term_UK_S` reads with ``int``; ``sum_assured``, ``fib_income``,
        ``premium_mth`` and ``sched_rate`` numbers, zero or more; and
        ``fib_commute_rate``, a share of the claims, from 0 to 1;
    11. a joint first-death point has a second life: ``joint_age`` a finite number,
        ``joint_sex`` M or F and ``joint_smoker`` N or S;
    12. indexation is elected on the level shape only;
    13. the factors are 1 without indexation, the waived share 0 without the waiver, and
        the streams in payment 0 off the family income benefit;
    14. the streams in payment are no more than the deaths since issue,
        ``fib_streams_init`` at most ``fib_cum_init``: a commuted claim stops a stream, and
        nothing starts one but a death.
    """
    name = model_point_file                                          # noqa: F821
    table = pd.read_csv(input_dir() / name, index_col="point_id")    # noqa: F821
    for column in ("policy_count", "duration_mth", "lapse_cum_init", "fib_cum_init",
                   "fib_streams_init", "idx_factor_init", "idx_prem_factor_init",
                   "wop_waived_frac_init", "comm_init_pp_init"):
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
    if horizon < 0:
        raise ValueError(f"future_horizon_mth must be 0 months or more, not {horizon}")
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
            ("lapse_cum_init", 0.0, 1.0,
             "a number, 0 or more and below 1, the share of the issued cohort lapsed"),
            ("fib_cum_init", 0.0, float("inf"), "a number, zero or more"),
            ("fib_streams_init", 0.0, float("inf"), "a number, zero or more"),
            ("idx_factor_init", 1.0, float("inf"), "a number, 1 or more"),
            ("idx_prem_factor_init", 1.0, float("inf"), "a number, 1 or more"),
            ("wop_waived_frac_init", 0.0, 1.0, "a number from 0 to 1"),
            ("comm_init_pp_init", 0.0, float("inf"), "a number, zero or more")):
        v = pd.to_numeric(table[column], errors="coerce")            # noqa: F821
        above = (v < high) if column == "lapse_cum_init" else (v <= high)
        bad = table.index[~((v >= low) & above & (v < float("inf")))].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be {rule}; it is not at point_id "
                             f"{bad}")
        state[column] = v
    issue = {"lapse_cum_init": 0, "fib_cum_init": 0, "fib_streams_init": 0,
             "idx_factor_init": 1, "idx_prem_factor_init": 1, "wop_waived_frac_init": 0,
             "comm_init_pp_init": 0}
    for column, value in issue.items():
        bad = table.index[(months <= 0) & (state[column] != value)].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be {value} on a policy not yet in "
                             f"force, duration_mth 0 or less; it is not at point_id {bad}")
    for column in ("joint_first_death", "indexation", "wop"):
        flag = table[column]
        bad = table.index[~flag.map(lambda v: str(v).lower() in ("true", "false"))].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be True or False; it is not at "
                             f"point_id {bad}")
    for column, codes in (("shape", ("level", "decreasing", "fib")), ("sex", ("M", "F")),
                          ("smoker", ("N", "S")), ("premium_mode", ("monthly", "annual")),
                          ("mort_basis", ("applied", "select"))):
        bad = table.index[~table[column].isin(codes)].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be {' or '.join(codes)}; it is not "
                             f"at point_id {bad}")
    rules = {"finite": ("a finite number",
                        lambda v: (v > -float("inf")) & (v < float("inf"))),
             "amount": ("a number, zero or more",
                        lambda v: (v >= 0) & (v < float("inf"))),
             "share": ("a number from 0 to 1", lambda v: (v >= 0) & (v <= 1))}
    for column, kind in (("age_at_entry", "finite"), ("policy_term", "finite"),
                         ("sum_assured", "amount"), ("fib_income", "amount"),
                         ("premium_mth", "amount"), ("sched_rate", "amount"),
                         ("fib_commute_rate", "share")):
        rule, holds = rules[kind]
        v = pd.to_numeric(table[column], errors="coerce")            # noqa: F821
        bad = table.index[~holds(v)].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be {rule}; it is not at point_id "
                             f"{bad}")
    joint = table["joint_first_death"].map(lambda v: str(v).lower() == "true")
    ages = pd.to_numeric(table["joint_age"], errors="coerce")        # noqa: F821
    bad = table.index[joint & ~((ages > -float("inf")) & (ages < float("inf")))].tolist()
    if bad:
        raise ValueError(f"{name}: joint_age must be a finite number on a joint "
                         f"first-death point; it is not at point_id {bad}")
    for column, codes in (("joint_sex", ("M", "F")), ("joint_smoker", ("N", "S"))):
        bad = table.index[joint & ~table[column].isin(codes)].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be {' or '.join(codes)} on a joint "
                             f"first-death point; it is not at point_id {bad}")
    indexed = table["indexation"].map(lambda v: str(v).lower() == "true")
    bad = table.index[indexed & (table["shape"] != "level")].tolist()
    if bad:
        raise ValueError(f"{name}: indexation is modelled on the level shape only; it is "
                         f"elected at point_id {bad}")
    waived = table["wop"].map(lambda v: str(v).lower() == "true")
    fib = table["shape"] == "fib"
    for column, value, flag, what in (
            ("idx_factor_init", 1, indexed, "indexation is elected"),
            ("idx_prem_factor_init", 1, indexed, "indexation is elected"),
            ("wop_waived_frac_init", 0, waived, "the waiver of premium rider is in force"),
            ("fib_streams_init", 0, fib, "the shape is fib")):
        bad = table.index[~flag & (state[column] != value)].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be {value} unless {what}; it is "
                             f"not at point_id {bad}")
    bad = table.index[state["fib_streams_init"] > state["fib_cum_init"]].tolist()
    if bad:
        raise ValueError(f"{name}: fib_streams_init must be at most fib_cum_init, the "
                         f"streams in payment no more than the deaths since issue; it is "
                         f"not at point_id {bad}")
    return table


def wop_pipeline():
    """The waiver pipeline of each point in force, from *wop_pipeline_sec.csv*, checked.

    Indexed by ``point_id`` and ``lag``, both read by value as ints.  One row per month of
    the deferred period not yet waived, for each point in force with the waiver rider:
    ``lag`` ``k`` is the policy month ``k`` months before the valuation date, and
    ``wop_deferred_init`` the share of the policies in force whose life became
    incapacitated in it, from the premium-paying lives, and is still in the deferred
    period at the valuation instant, the start of month 0, after the recoveries of the
    ``k - 1`` months since; ``Projection.wop_waived_frac`` takes it in once the deferred
    period has run, less the recoveries of the months still to run.  ``point_id`` is the
    only key to a point, and nothing else in the file names one.  A point not yet in
    force, or without the rider, holds no row; a point in force with it holds one for each
    of its last ``min(wop_defer_mths, duration_mth)`` months, which
    ``Projection.proj_len`` checks, since the deferred period is
    ``Projection.wop_defer_mths``.

    The checks run over the whole file at once, by 7 rules in turn, and the first that
    fails raises ``ValueError``, naming the missing column or the lines, the header line 1:

    1. the three columns are present;
    2. each of ``point_id`` and ``lag`` is a whole number, below ``2**53`` in size;
    3. each ``point_id`` is a point of :func:`model_point_table`;
    4. no ``point_id`` and ``lag`` appear together twice;
    5. ``lag`` is from 1 to its point's ``duration_mth``: no incapacity predates issue,
       and a point not yet in force holds none;
    6. its point has the waiver rider in force;
    7. ``wop_deferred_init`` is a number from 0 to 1, a share of the policies in force.
    """
    name = wop_pipeline_file                                         # noqa: F821
    points = model_point_file                                        # noqa: F821
    table = pd.read_csv(input_dir() / name)                          # noqa: F821
    for column in ("point_id", "lag", "wop_deferred_init"):
        if column not in table.columns:
            raise ValueError(f"{name} has no {column} column")
    keys = {}
    for column in ("point_id", "lag"):
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
    pairs = pd.MultiIndex.from_arrays([keys["point_id"], keys["lag"]])  # noqa: F821
    faults = []
    for p, k in sorted(set(pairs[pairs.duplicated()])):
        lines = (table.index[(keys["point_id"] == p) & (keys["lag"] == k)] + 2).tolist()
        faults.append(f"point_id {p} lag {k} is on line {lines}")
    if faults:
        raise ValueError(f"{name}: each point_id and lag must have one row; "
                         + "; ".join(faults))
    months = pd.to_numeric(model_points["duration_mth"], errors="coerce")  # noqa: F821
    life = months.reindex(keys["point_id"].to_numpy()).to_numpy()
    bad = (table.index[~((keys["lag"] >= 1) & (keys["lag"] <= life))] + 2).tolist()
    if bad:
        raise ValueError(f"{name}: lag must be from 1 to its point's duration_mth, the "
                         f"months since issue at the valuation date; it is not on line "
                         f"{bad}")
    wop = model_points["wop"].map(lambda v: str(v).lower() == "true")
    covered = wop.reindex(keys["point_id"].to_numpy()).to_numpy()
    bad = (table.index[~covered] + 2).tolist()
    if bad:
        raise ValueError(f"{name}: a row's point must have the waiver of premium rider in "
                         f"force; it does not on line {bad}")
    v = pd.to_numeric(table["wop_deferred_init"], errors="coerce")   # noqa: F821
    bad = (table.index[~((v >= 0) & (v <= 1))] + 2).tolist()
    if bad:
        raise ValueError(f"{name}: wop_deferred_init must be a number from 0 to 1; it is "
                         f"not on line {bad}")
    out = table.assign(point_id=keys["point_id"], lag=keys["lag"], wop_deferred_init=v)
    return out.set_index(["point_id", "lag"]).sort_index()


def wop_pipeline_count():
    """The number of lags *wop_pipeline_sec.csv* holds for each point, by ``point_id``.

    0 where the file holds none, read from :func:`wop_pipeline`, which checks the file
    first.  ``Projection.proj_len`` asks it, with :func:`wop_pipeline_last`, whether a
    point in force with the waiver holds exactly the lags it reads.
    """
    held = wop_pipeline().groupby(level="point_id").size()
    return held.reindex(model_point_table().index, fill_value=0)


def wop_pipeline_last():
    """The last lag *wop_pipeline_sec.csv* holds for each point, by ``point_id``.

    0 where the file holds none, read from :func:`wop_pipeline`, which checks the file
    first.
    """
    lags = wop_pipeline().reset_index().groupby("point_id")["lag"].max()
    return lags.reindex(model_point_table().index, fill_value=0)


def mort_table():
    """The mortality rates by sex, smoker status and age, from *mort_table.csv*.

    Read as the applied best-estimate rate on the ``applied`` mortality basis and as
    the ultimate rate on the ``select`` basis; see ``Projection.mort_basis``.
    :mod:`~.Term_UK_S`'s reader, unchanged; :func:`mort_age_first` checks the table.
    """
    return pd.read_csv(                                              # noqa: F821
        input_dir() / mort_table_file,                               # noqa: F821
        index_col=["sex", "smoker", "age"])


def select_factor_table():
    """The select-duration factors, read from *select_factor_table.csv*.

    :mod:`~.Term_UK_S`'s reader, unchanged; :func:`select_last_duration` checks the table.
    """
    return pd.read_csv(                                              # noqa: F821
        input_dir() / select_factor_file, index_col="duration")      # noqa: F821


def lapse_table():
    """The lapse rates by policy year, read from *lapse_table.csv*.

    The ``policy_year`` key is the contractual 1-based label (1, 2, ..., 6+), not the
    projection's 0-based month index ``t``; ``Projection.lapse_rate_base`` reads the row
    ``policy_year(t)`` on the policy clock, and the rate it returns is the **annual** one
    the table is quoted in.  :mod:`~.Term_UK_S`'s reader, unchanged;
    :func:`lapse_last_year` checks the table.
    """
    return pd.read_csv(                                              # noqa: F821
        input_dir() / lapse_table_file, index_col="policy_year")     # noqa: F821


def mort_age_first():
    """The first attained age *mort_table.csv* gives a rate for, the table checked first.

    ``Projection.mort_rate_base`` asks it, and :func:`mort_age_last`, before it reads the
    table, so a table it cannot read is refused before any value of it is.  The rules,
    each over the whole table, the first that fails raising ``ValueError`` and naming the
    lines, the header line 1:

    1. each age is a whole number, read by its value, so ``35.0`` is 35;
    2. each sex is M or F, and each smoker status N or S, the codes the model point table
       holds;
    3. each of the four groups, M and F by N and S, runs over the table's ages from the
       first to the last, one row an age, none below 0: the projection reads a rate at
       each attained age a policy reaches, of either life. Every fault is named in one
       message: an age below 0 and an age a group repeats each with its lines, and each
       span of ages a group lacks;
    4. each ``mort_rate`` is a number from 0 to 1, a probability, read by the cap.
    """
    name = mort_table_file                                           # noqa: F821
    tbl = mort_table().reset_index()
    lines = tbl.index + 2
    ages = pd.to_numeric(tbl["age"], errors="coerce")                # noqa: F821
    bad = lines[(~(ages % 1 == 0)).to_numpy()].tolist()
    if bad:
        raise ValueError(f"{name}: age must be a whole number; it is not on line {bad}")
    bad = lines[(~(tbl["sex"].isin(["M", "F"])
                   & tbl["smoker"].isin(["N", "S"]))).to_numpy()].tolist()
    if bad:
        raise ValueError(f"{name}: sex must be M or F, and smoker N or S; they are not on "
                         f"line {bad}")
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
        for k in ("N", "S"):
            group = ((tbl["sex"] == s) & (tbl["smoker"] == k) & (ages >= 0)).to_numpy()
            run = ages[group]
            for a in sorted(set(run[run.duplicated()])):
                faults.append(f"sex {s}, smoker {k}, age {a} repeats on lines "
                              f"{lines[group & (ages == a).to_numpy()].tolist()}")
            spans = []
            for a in sorted(set(range(first, last + 1)) - set(run)):
                if spans and spans[-1][1] == a - 1:
                    spans[-1][1] = a
                else:
                    spans.append([a, a])
            for low, high in spans:
                faults.append(f"no line holds sex {s}, smoker {k}, "
                              + (f"ages {low} to {high}" if high > low else f"age {low}"))
    if faults:
        raise ValueError(f"{name}: the ages of each sex and smoker status must run from "
                         f"{first} to {last}, the table's first and last, one row an age, "
                         f"none below 0; " + "; ".join(faults))
    rates = pd.to_numeric(tbl["mort_rate"], errors="coerce")         # noqa: F821
    bad = (tbl.index[~((rates >= 0) & (rates <= 1))] + 2).tolist()
    if bad:
        raise ValueError(f"{name}: mort_rate must be a number from 0 to 1; it is not on "
                         f"line {bad}")
    return first


def mort_age_last():
    """The last attained age *mort_table.csv* gives a rate for, read once
    :func:`mort_age_first` has checked the table."""
    mort_age_first()
    ages = pd.to_numeric(mort_table().reset_index()["age"], errors="coerce")  # noqa: F821
    return int(ages.max())


def select_last_duration():
    """The last select duration *select_factor_table.csv* gives a factor for, checked.

    ``Projection.select_factor`` asks it before it reads the table, and refuses a
    duration past it, where ``select_period`` runs beyond the table.  The rules, the first
    that fails raising ``ValueError`` and naming the lines, the header line 1: each
    duration is a whole number, read by its value; the durations run from 0, one row a
    duration, without a gap or a repeat, since the factor is read at every completed
    policy year up to ``select_period``, every fault named in one message, a duration
    below 0 and a repeated one each with its lines, and each span the table lacks; and
    each ``factor`` is a number, zero or more, a multiple of a mortality rate the cap
    reads.
    """
    name = select_factor_file                                        # noqa: F821
    tbl = select_factor_table().reset_index()
    lines = tbl.index + 2
    durations = pd.to_numeric(tbl["duration"], errors="coerce")      # noqa: F821
    bad = lines[(~(durations % 1 == 0)).to_numpy()].tolist()
    if bad:
        raise ValueError(f"{name}: duration must be a whole number; it is not on line "
                         f"{bad}")
    keys = durations.astype("int64")
    faults = []
    for d in sorted(set(keys[keys < 0])):
        faults.append(f"duration {d}, below 0, is on lines "
                      f"{lines[(keys == d).to_numpy()].tolist()}")
    for d in sorted(set(keys[keys.duplicated() & (keys >= 0)])):
        faults.append(f"duration {d} repeats on lines "
                      f"{lines[(keys == d).to_numpy()].tolist()}")
    held = sorted(set(keys[keys >= 0]))
    spans = []
    for d in sorted(set(range(0, max(held, default=0) + 1)) - set(held)):
        if spans and spans[-1][1] == d - 1:
            spans[-1][1] = d
        else:
            spans.append([d, d])
    for low, high in spans:
        faults.append("no line holds " + (f"durations {low} to {high}" if high > low
                                          else f"duration {low}"))
    if faults:
        raise ValueError(f"{name}: the durations must run from 0, one row a duration, "
                         f"without a gap or a repeat; " + "; ".join(faults))
    factors = pd.to_numeric(tbl["factor"], errors="coerce")          # noqa: F821
    bad = (tbl.index[~((factors >= 0) & (factors < float("inf")))] + 2).tolist()
    if bad:
        raise ValueError(f"{name}: factor must be a number, zero or more; it is not on "
                         f"line {bad}")
    return int(held[-1])


def lapse_last_year():
    """The last policy year *lapse_table.csv* gives a rate for, the table checked first.

    ``Projection.lapse_rate_base`` asks it before it reads the table, and reads every
    later policy year at it, :mod:`~.Term_UK_S`'s ``tbl.index.max()``.  The rules, the
    first that fails raising ``ValueError`` and naming the lines, the header line 1: each
    policy year is a whole number, read by its value; the years run from 1, one row a
    year, without a gap or a repeat, since each policy year from the first is read, every
    fault named in one message, a year below 1 and a repeated one each with its lines, and
    each span the table lacks; and each ``lapse_rate`` is a number from 0 to 1, a
    probability, which the lapse rate's ``min`` reads.
    """
    name = lapse_table_file                                          # noqa: F821
    tbl = lapse_table().reset_index()
    lines = tbl.index + 2
    years = pd.to_numeric(tbl["policy_year"], errors="coerce")       # noqa: F821
    bad = lines[(~(years % 1 == 0)).to_numpy()].tolist()
    if bad:
        raise ValueError(f"{name}: policy_year must be a whole number; it is not on line "
                         f"{bad}")
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
    bad = (tbl.index[~((rates >= 0) & (rates <= 1))] + 2).tolist()
    if bad:
        raise ValueError(f"{name}: lapse_rate must be a number from 0 to 1; it is not on "
                         f"line {bad}")
    return int(held[-1])


# ---------------------------------------------------------------------------
# References

model_point_file = "model_point_table_sec.csv"

wop_pipeline_file = "wop_pipeline_sec.csv"

mort_table_file = "mort_table.csv"

select_factor_file = "select_factor_table.csv"

lapse_table_file = "lapse_table.csv"

future_horizon_mth = 120

pd = ("Module", "pandas")
