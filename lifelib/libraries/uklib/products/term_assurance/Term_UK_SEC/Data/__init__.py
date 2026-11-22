# modelx: pseudo-python
# This file is part of a modelx model.
# It can be imported as a Python module, but functions defined herein
# are model formulas and may not be executable as standard Python.

"""Input data shared by every by-policy projection.

The five input CSVs are read here, **once per model**, and referenced from
:mod:`~.Term_UK_SEC.Projection` as ``data``. :mod:`~.Term_UK_SEC.Projection` is
parameterized by ``idx``, the position of a model point in the table, so each
``Projection[i]`` is a separate ItemSpace with its own cells cache; if the readers lived
there, every model point would re-read every file. Holding them in an unparameterized
Space reads each file once no matter how many policies are projected.

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
business altogether. A longer horizon projects in modelx, but the compiled model's caches
are sized for the shipped 120 months (``spec_sec.py``): it needs ``t`` there raised to
12 x 50 + the horizon + 2 and a rebuild, or a frame longer than 720 months raises
``IndexError`` compiled, naming nothing, at the first month past the caches. It refuses,
too, what :mod:`~.Term_UK_S` projects without a word or meets only when a projection
reaches it: a flag that is not True or False, a code that names no shape, sex, smoker
status, premium mode or mortality basis, an age, a term or an amount that is not a number
in its range, a joint point with no second life, and indexation off the level shape. The
checks run in turn, and the first that fails raises, naming the missing column or every
point that fails it.

**The waiver pipeline is checked as it is read.** :func:`wop_pipeline` refuses a
companion row for a point the table lacks, for a point without the waiver rider, at a lag
that predates issue, twice for one point and lag, or with a deferred share that is not a
share of the policies in force. How many lags a point holds is a rule of the product,
since it is ``Projection.wop_defer_mths``, so ``Projection.proj_len`` checks it, from
:func:`wop_pipeline_count` and :func:`wop_pipeline_last`. Whether a point is still in
cover at the valuation date, and whether the contract issues it, are rules of the product
too, and ``Projection.proj_len`` checks them, against its own References, the contract the
compiled model's caches are sized from as they are from the horizon.

**Each assumption table is checked before a value of it is read.** Its keys are read by
their value, so an age written ``35.0`` is age 35, and a key that is not whole, text among
them, is refused, naming the file, the column and its lines; so are keys that repeat or
leave a gap the projection would read, naming the keys. A value that is blank, text,
infinite or outside its range is refused, naming the file, the column and its lines,
whether or not a point reads it: ``Projection.mort_rate_life`` caps the annual rate with
``min``, which keeps its first argument unless a later one compares smaller, and no
comparison with NaN holds, so the cap is written with its bound second and a NaN would
stay NaN; but an infinity is a number, which the cap reads as 1, certain death. The check
of each table is in the cell its array and its extent are sized from, which a projection
asks before it reads the table: :func:`mort_age_first` and :func:`mort_age_last` for the
mortality table, :func:`select_last_duration` for the select factors and
:func:`lapse_last_year` for the lapse table. A read beyond a table's extent is refused by
the one ``Projection`` cell that reads the table, naming the point, where
:mod:`~.Term_UK_S`'s lookup raised ``KeyError``.

To swap in a licensed mortality basis — the CMI "16" Series assured lives tables
TMNL16/TFNL16, which are subscriber-restricted and cannot be redistributed here —
replace ``mort_table.csv`` and ``select_factor_table.csv`` with same-schema files, or
point ``mort_table_file`` and ``select_factor_file`` at different names, then clear the
cache. No formula changes. Replacing a file changes :mod:`~.Term_UK_S` too, which reads
the same one. A compiled model clears no cache, so there the name is set on a package
just imported, before anything is read.

**The vectors.** The readers return what the files hold, and no
:mod:`~.Term_UK_SEC.Projection` cell but ``model_point``, a reporting cell, reads them.
The others read the arrays below instead, one element at a time, a model point's
attribute being the element at its position, ``data.age_at_entry()[idx]``. That is what
lets the model compile to C, as ``basiclife.BasicTerm_SC`` does: each array is a numpy
vector or table of int64 or float64, which compiles to a typed memoryview, never one of
bools, objects or text, and each extent of a table, or width of the pipeline, is an int.

Text the projection needs is decoded here, into the number it selects, for every point
at once, as :mod:`~.Term_UK_S` reads each value: the shape into a flag for each of the
three, the premium mode into the months between premiums, the mortality basis into a
flag, each life's sex and smoker status into its row of the mortality table, and each
True or False column into a 0/1 flag. The second life's age and row are read on a joint
point alone, and are 0 elsewhere: :func:`joint_first_death` is the flag beside them, so no
NaN reaches a formula. And each table keyed by more than a number becomes an
integer-indexed array. The mortality table, keyed by sex, smoker status and age, is
tabled by its row, the four sex and smoker groups numbered, and padded from age 0, so that
the index is the attained age; the select factors and the lapse table are vectors by
duration and by policy year; and the waiver pipeline, keyed by point and lag, is tabled by
point and lag:

==============================  =======  ================  =================================
Cells                           dtype    Shape             From
==============================  =======  ================  =================================
point_id()                      int64    [point]           the table's index
age_at_entry()                  int64    [point]           ``age_at_entry``
joint_first_death()             int64    [point]           ``joint_first_death``, 0/1
joint_age()                     int64    [point]           ``joint_age``, 0 off a joint point
mort_group()                    int64    [point]           ``sex`` and ``smoker``, decoded
joint_mort_group()              int64    [point]           ``joint_sex`` and
                                                           ``joint_smoker``, decoded, 0 off
                                                           a joint point
policy_term()                   int64    [point]           ``policy_term``
sum_assured()                   float64  [point]           ``sum_assured``
fib_income()                    float64  [point]           ``fib_income``
sched_rate()                    float64  [point]           ``sched_rate``
indexation()                    int64    [point]           ``indexation``, 0/1
wop()                           int64    [point]           ``wop``, 0/1
premium_mth()                   float64  [point]           ``premium_mth``
prem_cycle()                    int64    [point]           ``premium_mode``, decoded
is_level()                      int64    [point]           ``shape``, 1 where ``level``
is_decreasing()                 int64    [point]           ``shape``, 1 where ``decreasing``
is_fib()                        int64    [point]           ``shape``, 1 where ``fib``
is_select_basis()               int64    [point]           ``mort_basis``, 1 where ``select``
policy_count()                  float64  [point]           ``policy_count``
fib_commute_rate()              float64  [point]           ``fib_commute_rate``
duration_mth()                  int64    [point]           ``duration_mth``
lapse_cum_init()                float64  [point]           ``lapse_cum_init``
fib_cum_init()                  float64  [point]           ``fib_cum_init``
fib_streams_init()              float64  [point]           ``fib_streams_init``
idx_factor_init()               float64  [point]           ``idx_factor_init``
idx_prem_factor_init()          float64  [point]           ``idx_prem_factor_init``
wop_waived_frac_init()          float64  [point]           ``wop_waived_frac_init``
comm_init_pp_init()             float64  [point]           ``comm_init_pp_init``
wop_pipeline_count()            int64    [point]           *wop_pipeline_sec.csv*
wop_pipeline_last()             int64    [point]           *wop_pipeline_sec.csv*
wop_pipeline_max()              int      scalar            *wop_pipeline_sec.csv*, checked
wop_deferred_init()             float64  [point, lag]      *wop_pipeline_sec.csv*
mort_age_first()                int      scalar            *mort_table.csv*, checked
mort_age_last()                 int      scalar            *mort_table.csv*
mort_table_array()              float64  [group, age]      *mort_table.csv*
select_last_duration()          int      scalar            *select_factor_table.csv*,
                                                           checked
select_factor_array()           float64  [duration]        *select_factor_table.csv*
lapse_last_year()               int      scalar            *lapse_table.csv*, checked
lapse_table_array()             float64  [policy year]     *lapse_table.csv*
==============================  =======  ================  =================================

**An array is read by element, never whole,** in this Space as in
:mod:`~.Term_UK_SEC.Projection`. The compiler types an array cell as a memoryview only
once it has seen that every use of it, in either Space, is an element read: one
``len()``, slice, loop over it or numpy call on it anywhere, and the cell compiles as a
Python object. So an array derived here reads the table's column, never another cell's
array, and a width comes from a table or a count cell.

**What cannot be held is refused** when the table is first read, naming every point at
fault, beside the checks above: a ``point_id`` that is not a whole number below ``2**53``
in size, when :func:`point_id` is first read, as a refusal reads it; and an
``age_at_entry``, a ``policy_term`` or, on a joint point, a ``joint_age`` that is not
below ``2**53`` in size, by :func:`model_point_table` itself, which numpy would otherwise
cast to the least int64 without a word. A fraction of a year truncates, as
:mod:`~.Term_UK_S`'s ``int`` truncates it.
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
        :mod:`~.Term_UK_S` reads with ``int``, below ``2**53`` in size, which numpy would
        otherwise cast to the least int64 without a word; ``sum_assured``,
        ``fib_income``, ``premium_mth`` and ``sched_rate`` numbers, zero or more; and
        ``fib_commute_rate``, a share of the claims, from 0 to 1;
    11. a joint first-death point has a second life: ``joint_age`` a finite number below
        ``2**53`` in size, ``joint_sex`` M or F and ``joint_smoker`` N or S;
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
        if kind == "finite":
            bad = table.index[~(v.abs() < 2.0 ** 53)].tolist()
            if bad:
                raise ValueError(f"{name}: {column} must be below 2**53 in size; it is "
                                 f"not at point_id {bad}")
    joint = table["joint_first_death"].map(lambda v: str(v).lower() == "true")
    ages = pd.to_numeric(table["joint_age"], errors="coerce")        # noqa: F821
    bad = table.index[joint & ~((ages > -float("inf")) & (ages < float("inf")))].tolist()
    if bad:
        raise ValueError(f"{name}: joint_age must be a finite number on a joint "
                         f"first-death point; it is not at point_id {bad}")
    bad = table.index[joint & ~(ages.abs() < 2.0 ** 53)].tolist()
    if bad:
        raise ValueError(f"{name}: joint_age must be below 2**53 in size on a joint "
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
    """The number of lags *wop_pipeline_sec.csv* holds for each point: int64 [point].

    Element ``i`` is the count of the table's point at position ``i``, 0 where the file
    holds none, read from :func:`wop_pipeline`, which checks the file first.
    ``Projection.proj_len`` asks it, with :func:`wop_pipeline_last`, whether a point in
    force with the waiver holds exactly the lags it reads.  At stage ``E`` it was a Series
    by ``point_id``; it is a vector here, read at the point's position, as every vector
    is.
    """
    held = wop_pipeline().groupby(level="point_id").size()
    held = held.reindex(model_point_table().index, fill_value=0)
    return held.to_numpy(dtype="int64")


def wop_pipeline_last():
    """The last lag *wop_pipeline_sec.csv* holds for each point: int64 [point].

    Element ``i`` is the last lag of the table's point at position ``i``, 0 where the file
    holds none, read from :func:`wop_pipeline`, which checks the file first and refuses a
    lag below 1 or held twice.  So a point whose last lag equals its count holds lags 1 to
    that count, one each, which is what ``Projection.proj_len`` asks.
    """
    lags = wop_pipeline().reset_index().groupby("point_id")["lag"].max()
    lags = lags.reindex(model_point_table().index, fill_value=0)
    return lags.to_numpy(dtype="int64")


def wop_pipeline_max():
    """The most lags any one point holds in *wop_pipeline_sec.csv*, 0 if none: an int.

    Read from :func:`wop_pipeline`, which checks the file first: the pipeline's check,
    which :func:`wop_deferred_init` asks first, and one less than its width, so that a lag
    is its own column.  It counts rows, not lags: a point ``Projection.proj_len``
    projects holds lags 1 to its count, so its every lag is a column, and a row at a lag
    past the widest count belongs to a point holding a gap, which ``proj_len`` refuses
    before any of its lags is read.  So the width is bounded by the file's length, not by
    the largest lag a row may name.  6 on the shipped pipeline,
    ``Projection.wop_defer_mths``, which ``Data`` cannot read.
    """
    held = wop_pipeline().groupby(level="point_id").size()
    return int(held.max()) if len(held) else 0


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
    table, and :func:`mort_table_array` is sized from the two, so a table it cannot read
    is refused before any value of it is.  The rules, each over the whole table, the first
    that fails raising ``ValueError`` and naming the lines, the header line 1:

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
    duration past it, where ``select_period`` runs beyond the table; :func:`select_factor_array`
    is sized from it.  The rules, the first that fails raising ``ValueError`` and naming
    the lines, the header line 1: each duration is a whole number, read by its value; the
    durations run from 0, one row a duration, without a gap or a repeat, since the factor
    is read at every completed policy year up to ``select_period``, every fault named in
    one message, a duration below 0 and a repeated one each with its lines, and each span
    the table lacks; and each ``factor`` is a number, zero or more, a multiple of a
    mortality rate the cap reads.
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
    later policy year at it, :mod:`~.Term_UK_S`'s ``tbl.index.max()``, and
    :func:`lapse_table_array` is sized from it.  The rules, the first that fails raising
    ``ValueError`` and naming the lines, the header line 1: each policy year is a whole
    number, read by its value; the years run from 1, one row a year, without a gap or a
    repeat, since each policy year from the first is read, every fault named in one
    message, a year below 1 and a repeated one each with its lines, and each span the
    table lacks; and each ``lapse_rate`` is a number from 0 to 1, a probability, which the
    lapse rate's ``min`` reads.
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


def point_id():
    """The ``point_id`` of every model point, in table order: int64 [point].

    ``Projection`` is indexed by position, ``idx``, so this is how a projection names its
    point: ``Projection.point_id()`` is the element at ``idx``, and every refusal quotes
    it.  Read by value, so that a label written ``3.0`` is 3, and refused when it is first
    read, naming every label at fault, where one is not a whole number, text and a blank
    among them, or is ``2**53`` or more in size: the labels are the table's keys, which
    the pipeline's ``point_id`` names.  A projection that names no point reads no label,
    and runs.
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


def age_at_entry():
    """The issue age (ANB) of the first life of every model point: int64 [point].

    Read as :mod:`~.Term_UK_S` reads it, ``int`` of the number, which truncates a
    fraction; :func:`model_point_table` has refused one that is not a finite number below
    ``2**53`` in size.
    """
    ages = pd.to_numeric(model_point_table()["age_at_entry"])        # noqa: F821
    return ages.to_numpy(dtype="int64")


def joint_first_death():
    """Whether each model point covers two lives on a first-death basis: int64 [point],
    1 where it does, 0 where it does not.

    :mod:`~.Term_UK_S` reads the column with ``bool``.  :func:`model_point_table` has
    refused a value whose text is not True or False, in either case, so pandas reads the
    column as booleans, and each is decoded by its text, element by element, which is
    ``bool`` of each wherever the table reads.  An int, not a bool: a numpy bool array
    compiles as a Python object, not a memoryview.
    """
    flags = model_point_table()["joint_first_death"].tolist()
    out = np.zeros(len(flags), dtype="int64")                        # noqa: F821
    for i in range(len(flags)):
        out[i] = 1 if str(flags[i]).lower() == "true" else 0
    return out


def joint_age():
    """The issue age (ANB) of the second life of every joint model point: int64 [point].

    ``int`` of the ``joint_age`` column, as :mod:`~.Term_UK_S` reads it, on a joint
    first-death point, where :func:`model_point_table` has refused a value that is not a
    finite number below ``2**53`` in size; 0 on any other point, whose column no formula
    reads and the table may hold blank, as the shipped single-life points do.
    :func:`joint_first_death` is the flag beside it, which ``Projection.age_at_entry``
    asks first, so that no NaN reaches a formula.
    """
    table = model_point_table()
    flags = table["joint_first_death"].tolist()
    ages = pd.to_numeric(table["joint_age"], errors="coerce").tolist()  # noqa: F821
    out = np.zeros(len(ages), dtype="int64")                         # noqa: F821
    for i in range(len(ages)):
        if str(flags[i]).lower() == "true":
            out[i] = int(ages[i])
    return out


def mort_group():
    """The mortality table's row for the first life of every model point: int64 [point].

    The point's ``sex`` and ``smoker`` status, the key :mod:`~.Term_UK_S` reads
    *mort_table.csv* by, numbered as :func:`mort_table_array` tables the four groups: M N
    0, M S 1, F N 2 and F S 3.  :func:`model_point_table` has refused a code the table
    cannot hold, so every point has one of the four, and the four are each a whole run of
    the table's ages, which :func:`mort_age_first` checks.
    """
    table = model_point_table()
    sexes, smokers = table["sex"].tolist(), table["smoker"].tolist()
    out = np.zeros(len(sexes), dtype="int64")                        # noqa: F821
    for i in range(len(sexes)):
        out[i] = 2 * ("M", "F").index(sexes[i]) + ("N", "S").index(smokers[i])
    return out


def joint_mort_group():
    """The mortality table's row for the second life of every joint model point: int64
    [point].

    The point's ``joint_sex`` and ``joint_smoker``, numbered as :func:`mort_group`
    numbers the first life's, on a joint first-death point, where
    :func:`model_point_table` has refused a code the table cannot hold; 0 on any other
    point, whose columns no formula reads and the table may hold blank.
    :func:`joint_first_death` is the flag beside it, which ``Projection.mort_group`` asks
    first.
    """
    table = model_point_table()
    flags = table["joint_first_death"].tolist()
    sexes = table["joint_sex"].tolist()
    smokers = table["joint_smoker"].tolist()
    out = np.zeros(len(sexes), dtype="int64")                        # noqa: F821
    for i in range(len(sexes)):
        if str(flags[i]).lower() == "true":
            out[i] = 2 * ("M", "F").index(sexes[i]) + ("N", "S").index(smokers[i])
    return out


def policy_term():
    """The term in years of every model point: int64 [point].

    Read as :mod:`~.Term_UK_S` reads it, ``int`` of the number, which truncates a
    fraction; :func:`model_point_table` has refused one that is not a finite number below
    ``2**53`` in size.  ``Projection.proj_len`` refuses a term above the contract's.
    """
    terms = pd.to_numeric(model_point_table()["policy_term"])        # noqa: F821
    return terms.to_numpy(dtype="int64")


def sum_assured():
    """The initial sum assured of every model point: float64 [point]."""
    return pd.to_numeric(model_point_table()["sum_assured"]).to_numpy(  # noqa: F821
        dtype="float64")


def fib_income():
    """The family income benefit per month of every model point: float64 [point]."""
    return pd.to_numeric(model_point_table()["fib_income"]).to_numpy(  # noqa: F821
        dtype="float64")


def sched_rate():
    """The decreasing schedule's rate a year of every model point: float64 [point]."""
    return pd.to_numeric(model_point_table()["sched_rate"]).to_numpy(  # noqa: F821
        dtype="float64")


def indexation():
    """Whether each model point elects the RPI indexation option: int64 [point], 1 or 0.

    Decoded as :func:`joint_first_death` decodes its column.
    """
    flags = model_point_table()["indexation"].tolist()
    out = np.zeros(len(flags), dtype="int64")                        # noqa: F821
    for i in range(len(flags)):
        out[i] = 1 if str(flags[i]).lower() == "true" else 0
    return out


def wop():
    """Whether each model point has the waiver of premium rider in force: int64 [point],
    1 or 0.

    Decoded as :func:`joint_first_death` decodes its column.
    """
    flags = model_point_table()["wop"].tolist()
    out = np.zeros(len(flags), dtype="int64")                        # noqa: F821
    for i in range(len(flags)):
        out[i] = 1 if str(flags[i]).lower() == "true" else 0
    return out


def premium_mth():
    """The guaranteed monthly premium at issue of every model point: float64 [point]."""
    return pd.to_numeric(model_point_table()["premium_mth"]).to_numpy(  # noqa: F821
        dtype="float64")


def prem_cycle():
    """Months between premiums, decoded from ``premium_mode``: int64 [point].

    ``monthly`` 1 and ``annual`` 12, the arithmetic of the mode, which
    ``Projection.premium_pp`` branches on where :mod:`~.Term_UK_S` compares the text with
    ``"annual"``.  :func:`model_point_table` has refused any other mode, naming the point.
    """
    modes = model_point_table()["premium_mode"].tolist()
    out = np.zeros(len(modes), dtype="int64")                        # noqa: F821
    for i in range(len(modes)):
        out[i] = 12 if modes[i] == "annual" else 1
    return out


def is_level():
    """1 where a model point's ``shape`` is ``level``, else 0: int64 [point].

    :mod:`~.Term_UK_S`'s comparison, made element by element, exactly.
    :func:`model_point_table` has refused a shape other than the three, so on every point
    exactly one of :func:`is_level`, :func:`is_decreasing` and :func:`is_fib` is 1.
    """
    shapes = model_point_table()["shape"].tolist()
    out = np.zeros(len(shapes), dtype="int64")                       # noqa: F821
    for i in range(len(shapes)):
        out[i] = 1 if shapes[i] == "level" else 0
    return out


def is_decreasing():
    """1 where a model point's ``shape`` is ``decreasing``, else 0: int64 [point]."""
    shapes = model_point_table()["shape"].tolist()
    out = np.zeros(len(shapes), dtype="int64")                       # noqa: F821
    for i in range(len(shapes)):
        out[i] = 1 if shapes[i] == "decreasing" else 0
    return out


def is_fib():
    """1 where a model point's ``shape`` is ``fib``, the family income benefit, else 0:
    int64 [point]."""
    shapes = model_point_table()["shape"].tolist()
    out = np.zeros(len(shapes), dtype="int64")                       # noqa: F821
    for i in range(len(shapes)):
        out[i] = 1 if shapes[i] == "fib" else 0
    return out


def is_select_basis():
    """1 where a model point's ``mort_basis`` is ``select``, else 0: int64 [point].

    :mod:`~.Term_UK_S`'s comparison, made element by element, exactly;
    :func:`model_point_table` has refused a basis other than ``applied`` and ``select``.
    """
    bases = model_point_table()["mort_basis"].tolist()
    out = np.zeros(len(bases), dtype="int64")                        # noqa: F821
    for i in range(len(bases)):
        out[i] = 1 if bases[i] == "select" else 0
    return out


def policy_count():
    """The ``policy_count`` of every model point: float64 [point].

    :func:`model_point_table` has checked it: a number, zero or more.
    """
    return pd.to_numeric(model_point_table()["policy_count"]).to_numpy(  # noqa: F821
        dtype="float64")


def fib_commute_rate():
    """The share of each model point's family income benefit claims commuted: float64
    [point]."""
    return pd.to_numeric(model_point_table()["fib_commute_rate"]).to_numpy(  # noqa: F821
        dtype="float64")


def duration_mth():
    """The ``duration_mth`` of every model point, in whole months: int64 [point].

    :func:`model_point_table` has checked that each is whole and below ``2**53`` in size,
    so a duration written as ``12.0`` is the int 12.
    """
    months = pd.to_numeric(model_point_table()["duration_mth"])      # noqa: F821
    return months.to_numpy(dtype="int64")


def lapse_cum_init():
    """The selective-lapse ratio at the valuation date of every model point: float64
    [point]."""
    return pd.to_numeric(model_point_table()["lapse_cum_init"]).to_numpy(  # noqa: F821
        dtype="float64")


def fib_cum_init():
    """The deaths since issue per policy in force at the valuation date: float64 [point]."""
    return pd.to_numeric(model_point_table()["fib_cum_init"]).to_numpy(  # noqa: F821
        dtype="float64")


def fib_streams_init():
    """The family income benefit streams in payment per policy in force at the valuation
    date: float64 [point]."""
    return pd.to_numeric(model_point_table()["fib_streams_init"]).to_numpy(  # noqa: F821
        dtype="float64")


def idx_factor_init():
    """The cover indexation factor already given at the valuation date: float64 [point]."""
    return pd.to_numeric(model_point_table()["idx_factor_init"]).to_numpy(  # noqa: F821
        dtype="float64")


def idx_prem_factor_init():
    """The premium indexation factor already given at the valuation date: float64
    [point]."""
    return pd.to_numeric(                                            # noqa: F821
        model_point_table()["idx_prem_factor_init"]).to_numpy(dtype="float64")


def wop_waived_frac_init():
    """The share of the policies in force whose premium is waived at the valuation date:
    float64 [point]."""
    return pd.to_numeric(                                            # noqa: F821
        model_point_table()["wop_waived_frac_init"]).to_numpy(dtype="float64")


def comm_init_pp_init():
    """The initial commission each policy in force paid at issue: float64 [point]."""
    return pd.to_numeric(model_point_table()["comm_init_pp_init"]).to_numpy(  # noqa: F821
        dtype="float64")


def wop_deferred_init():
    """The share in the deferred period at the valuation instant, by point and lag:
    float64 [point, lag].

    Row ``i`` is the table's point at position ``i`` and column ``k`` its lag ``k`` of
    *wop_pipeline_sec.csv*, the column ``wop_deferred_init``, so that the lag is the
    index: :func:`wop_pipeline_max` plus one wide, 7 on the shipped pipeline.  NaN in
    column 0, which is no lag, and wherever the point holds no row, padding that
    ``Projection.wop_deferred_init`` never reads: it asks ``Projection.proj_len`` first,
    which refuses a point whose lags are not 1 to its count, one each, and then refuses a
    lag below 1 or past the point's last.  A row at a lag past the width belongs to such a
    point and is left out.  The width is the file's, not ``Projection.wop_defer_mths``,
    which ``Data`` cannot read, so a model run at another deferred period reads a
    pipeline written for it.  Asks :func:`wop_pipeline_max` first, which checks the file.
    """
    n = wop_pipeline_max()
    table = model_point_table()
    pipeline = wop_pipeline().reset_index()
    rows = table.index.get_indexer(pipeline["point_id"])
    lags = pipeline["lag"].to_numpy(dtype="int64")
    held = lags <= n
    out = np.full((len(table), n + 1), np.nan)                       # noqa: F821
    out[rows[held], lags[held]] = pipeline["wop_deferred_init"].to_numpy(
        dtype="float64")[held]
    return out


def mort_table_array():
    """The mortality rates by row and attained age, from *mort_table.csv*: float64
    [group, age].

    Row ``g`` is a sex and smoker group, M N 0, M S 1, F N 2 and F S 3, as
    :func:`mort_group` and :func:`joint_mort_group` number each life's, and column ``a``
    the attained age ``a``: padded from age 0, as ``basiclife.BasicTerm_SC``'s
    ``mort_table_array`` pads its table, so that the index **is** the age, and
    :func:`mort_age_last` plus one wide.  The ages below the table's first, 0 to 17 as
    shipped, hold NaN, which no formula reads: ``Projection.mort_rate_base`` refuses an
    age outside the table, naming the point.  Asks :func:`mort_age_first` first, which
    checks the table: each group runs over every age from the first to the last, one row
    an age, so no cell between them is padding, and each rate is a number from 0 to 1.
    """
    mort_age_first()
    last = mort_age_last()
    tbl = mort_table().reset_index()
    ages = pd.to_numeric(tbl["age"]).to_numpy(dtype="int64")         # noqa: F821
    rates = pd.to_numeric(tbl["mort_rate"]).to_numpy(dtype="float64")  # noqa: F821
    sexes, smokers = tbl["sex"].tolist(), tbl["smoker"].tolist()
    out = np.full((4, last + 1), np.nan)                             # noqa: F821
    for i in range(len(sexes)):
        g = 2 * ("M", "F").index(sexes[i]) + ("N", "S").index(smokers[i])
        out[g, ages[i]] = rates[i]
    return out


def select_factor_array():
    """The select factor by completed policy year, from *select_factor_table.csv*:
    float64 [duration].

    Element ``d`` is the factor at select duration ``d``, from 0 to
    :func:`select_last_duration`, which checks the table first: the durations run from 0
    without a gap, so no element is padding.  ``Projection.select_factor`` refuses a
    duration outside it, naming the point.
    """
    last = select_last_duration()
    tbl = select_factor_table().reset_index()
    durations = pd.to_numeric(tbl["duration"]).to_numpy(dtype="int64")  # noqa: F821
    factors = pd.to_numeric(tbl["factor"]).to_numpy(dtype="float64")  # noqa: F821
    out = np.full(last + 1, np.nan)                                  # noqa: F821
    out[durations] = factors
    return out


def lapse_table_array():
    """The annual lapse rate by policy year, from *lapse_table.csv*: float64 [policy
    year].

    Element ``y`` is the rate of policy year ``y``, from 1 to :func:`lapse_last_year`,
    which checks the table first: the years run from 1 without a gap.  Element 0, no
    policy year, holds NaN, which no formula reads: ``Projection.lapse_rate_base`` reads
    a policy year of cover, 1 or more, at most the last, which it reads every later year
    at, as :mod:`~.Term_UK_S` does.
    """
    last = lapse_last_year()
    tbl = lapse_table().reset_index()
    years = pd.to_numeric(tbl["policy_year"]).to_numpy(dtype="int64")  # noqa: F821
    rates = pd.to_numeric(tbl["lapse_rate"]).to_numpy(dtype="float64")  # noqa: F821
    out = np.full(last + 1, np.nan)                                  # noqa: F821
    out[years] = rates
    return out


# ---------------------------------------------------------------------------
# References

model_point_file = "model_point_table_sec.csv"

wop_pipeline_file = "wop_pipeline_sec.csv"

mort_table_file = "mort_table.csv"

select_factor_file = "select_factor_table.csv"

lapse_table_file = "lapse_table.csv"

future_horizon_mth = 120

pd = ("Module", "pandas")

np = ("Module", "numpy")
