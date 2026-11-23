# modelx: pseudo-python
# This file is part of a modelx model.
# It can be imported as a Python module, but functions defined herein
# are model formulas and may not be executable as standard Python.

"""Input data shared by every by-policy projection.

The three input CSVs are read here, **once per model**, and referenced from
:mod:`~.CI_UK_SEC.Projection` as ``data``. :mod:`~.CI_UK_SEC.Projection` is
parameterized by ``idx``, the position of a model point in the table, so each
``Projection[i]`` is a separate ItemSpace with its own cells cache; if the readers lived
there, every model point would re-read every file. Holding them in an unparameterized
Space reads each file once no matter how many policies are projected.

Inputs are **external files**: plain CSVs in the model folder's parent directory,
``products/critical_illness/``, rather than data stored inside the model. The model
folder therefore holds nothing but formulas — no ``_data/``, no IOSpec, no embedded
values — so a diff of the model shows logic changes only. This follows
``annuallife.TradLife_A``; contrast ``basiclife.BasicTerm_S``, which keeps its inputs
*inside* the model through modelx's IOSpec machinery.

The consequence worth knowing: **the model is not portable on its own.** Copying the
``CI_UK_SEC`` folder without its parent's CSVs produces a model that reads and then
fails on first evaluation.

**Two of the tables are CI_UK_S's.** The pivot rates and the lapse table are the files
:mod:`~.CI_UK_S` reads, read here in place: one copy of each table serves both models, so
an edit to one reaches both. The model point table, ``model_point_table_sec.csv``, is this
model's own; it sits beside :mod:`~.CI_UK_S`'s ``model_point_table.csv``, which this model
never opens.

:func:`input_dir` resolves the directory from ``_model.path.parent`` at run time, so
the model works wherever the repository is checked out. Each table has a filename
Reference and a reader Cells:

======================  ==========================  ==============================
Reference               Cells                       File
======================  ==========================  ==============================
model_point_file        model_point_table()         model_point_table_sec.csv
ci_rate_file            ci_rate_table()             ci_rate_table.csv
lapse_table_file        lapse_table()               lapse_table.csv
======================  ==========================  ==============================

``ci_rate_table.csv`` holds **pivot ages only** — 40, 45, 50, 55, 60, 65 — because that
is the form the technical notes give the basis in, together with the rule that
intermediate ages are interpolated log-linearly. The interpolation is :mod:`~.CI_UK_S`'s
``pivot_interp``, which this model makes once, here, for every age the contract admits
(:func:`i_ci_array`, below), rather than baking it into a pre-expanded file, so that
swapping in a licensed AC04 or "16" Series basis still means replacing a 24-row table,
not a generated one.

**The model point table is checked as it is read.** Eight of its columns are the
in-force interface: ``policy_count`` and ``duration_mth``, as in
``basiclife.BasicTerm_SE``, and the opening state of a point in force,
``idx_factor_init``, ``idx_prem_factor_init``, ``review_prem_factor_init``,
``ci_sel_latched_init``, ``ci_sel_factor_init`` and ``review_prem_shock_init``.
:func:`model_point_table` refuses a table that lacks one, repeats a ``point_id``, holds a
count, a duration or a state no policy can have, or a policy to be issued more than
``future_horizon_mth`` months after the valuation date, 120 as shipped: future new
business is written over a stated horizon, so that no frame runs longer than cover from
issue plus that horizon. Set to 0, the Reference refuses future new business altogether.
A longer horizon projects in modelx, but the compiled model's caches are sized for the
shipped 120 months (``spec_sec.py``): it needs ``t`` there raised to 12 x 50 + the horizon
+ 2 and a rebuild, or a frame longer than 720 months raises ``IndexError`` compiled,
naming nothing, at the first month past the caches. It refuses, too, what
:mod:`~.CI_UK_S` projects without a word or meets only when a projection reaches it: a
flag that is not True or False, a code that names no contract type, life basis, sex,
smoker status, cover basis, premium guarantee or premium mode, an age, a term or an amount
that is not a number in its range, a joint point with no second life or on the standalone
contract, an indexation history before the first anniversary, an open latch with a
factor, and a history of indexation or reviews on a point without the option or the
reviews. The checks run in turn, and the first that fails raises, naming the missing
column or every point that fails it. Whether a point is still in cover at the valuation
date, whether the contract issues it, and whether a reviewable point has had the reviews
its history says, are rules of the product, and ``Projection.proj_len`` checks them,
against its own References, the contract the compiled model's caches are sized from as
they are from the horizon.

**Each assumption table is checked before a value of it is read.** Its keys are read by
their value, so an age written ``40.0`` is age 40, and a key that is not whole, text among
them, is refused, naming the file, the column and its lines; so are keys that repeat or
leave a gap the projection would read, naming the keys. A value that is blank, text,
infinite or outside its range is refused, naming the file, the column and its lines,
whether or not a point reads it: ``Projection.ci_rate`` and ``claim_rate_life`` cap the
annual rates with ``min``, which keeps its first argument unless a later one compares
smaller, and no comparison with NaN holds, so each cap is written with its bound second
and a NaN would stay NaN; but an infinity is a number, which the cap reads as 1, a
certain claim. The pivot table is checked by its reader, :func:`ci_rate_table`, before it
indexes and sorts the table, so that a fault is named by its line of the file; the lapse
table by :func:`lapse_last_year`, the cell the projection takes the table's extent from,
which it asks before it reads the table. And a pivot table whose interpolation is not a
finite number at an age the contract admits, past the largest float, is refused as
:func:`i_ci_array` and :func:`q_d_array` build it, naming the file, the column, the group
and the age, though no point may reach that age. A read beyond a table's extent is refused
by the one ``Projection`` cell that reads the table, naming the point.

**The vectors.** The readers return what the files hold, and no
:mod:`~.CI_UK_SEC.Projection` cell but ``model_point``, a reporting cell, reads them.
The others read the arrays below instead, one element at a time, a model point's
attribute being the element at its position, ``data.age_at_entry()[idx]``. That is what
lets the model compile to C, as ``basiclife.BasicTerm_SC`` does: each array is a numpy
vector or table of int64 or float64, which compiles to a typed memoryview, never one of
bools, objects or text, and each extent of a table is an int.

Text the projection needs is decoded here, into the number it selects, for every point
at once, as :mod:`~.CI_UK_S` reads each value: the contract type, the life basis and the
premium guarantee into a flag each, each life's sex and smoker status into its row of the
pivot arrays, and each True or False column into a 0/1 flag. The second life's age and
row are read on a joint point alone, and are 0 elsewhere: :func:`is_joint` is the flag
beside them, so no NaN reaches a formula. ``cover_basis`` and ``premium_mode`` are checked
but not decoded, since no projection cell reads them: the cover is level on every point
``model_point_table`` admits, and the premium is carried monthly in either mode. And each
table keyed by more than a number becomes an integer-indexed array. The pivot rates,
keyed by sex, smoker status and pivot age, are interpolated by :mod:`~.CI_UK_S`'s rule at
every attained age the contract admits, ``rate_age_min`` to ``rate_age_max``, 18 to 74,
and tabled by the row of the sex and smoker group, the four numbered, and padded from age
0, so that the index is the attained age; and the lapse table is a vector by policy year:

==============================  =======  ================  =================================
Cells                           dtype    Shape             From
==============================  =======  ================  =================================
point_id()                      int64    [point]           the table's index
age_at_entry()                  int64    [point]           ``age_at_entry``
is_joint()                      int64    [point]           ``life_basis``, 1 where
                                                           ``joint_first_event``
joint_age()                     int64    [point]           ``joint_age``; 0 if not joint
rate_group()                    int64    [point]           ``sex`` and ``smoker``, decoded
joint_rate_group()              int64    [point]           ``joint_sex`` and
                                                           ``joint_smoker``, decoded, 0 off
                                                           a joint point
policy_term()                   int64    [point]           ``policy_term``
sum_assured()                   float64  [point]           ``sum_assured``
premium_mth()                   float64  [point]           ``premium_mth``
is_accelerated()                int64    [point]           ``contract_type``, 1 where
                                                           ``accelerated``
is_reviewable()                 int64    [point]           ``premium_guarantee``, 1 where
                                                           ``reviewable``
children_cover()                int64    [point]           ``children_cover``, 0/1
indexation()                    int64    [point]           ``indexation``, 0/1
policy_count()                  float64  [point]           ``policy_count``
duration_mth()                  int64    [point]           ``duration_mth``
idx_factor_init()               float64  [point]           ``idx_factor_init``
idx_prem_factor_init()          float64  [point]           ``idx_prem_factor_init``
review_prem_factor_init()       float64  [point]           ``review_prem_factor_init``
ci_sel_latched_init()           int64    [point]           ``ci_sel_latched_init``, 0/1
ci_sel_factor_init()            float64  [point]           ``ci_sel_factor_init``
review_prem_shock_init()        float64  [point]           ``review_prem_shock_init``
rate_age_first()                int      scalar            ``rate_age_min``, checked
rate_age_last()                 int      scalar            ``rate_age_max``
i_ci_array()                    float64  [group, age]      *ci_rate_table.csv*, ``i_ci``
q_d_array()                     float64  [group, age]      *ci_rate_table.csv*, ``q_d``
lapse_last_year()               int      scalar            *lapse_table.csv*, checked
lapse_table_array()             float64  [policy year]     *lapse_table.csv*
==============================  =======  ================  =================================

**An array is read by element, never whole,** in this Space as in
:mod:`~.CI_UK_SEC.Projection`. The compiler types an array cell as a memoryview only
once it has seen that every use of it, in either Space, is an element read: one
``len()``, slice, loop over it or numpy call on it anywhere, and the cell compiles as a
Python object. So an array derived here reads the table's column, never another cell's
array, and a width comes from a table, a Reference or a count cell.

**What cannot be held is refused** when the table is first read, naming every point at
fault, beside the checks above: a ``point_id`` that is not a whole number below ``2**53``
in size, when :func:`point_id` is first read, as a refusal reads it; and an
``age_at_entry``, a ``policy_term`` or, on a joint point, a ``joint_age`` that is not
below ``2**53`` in size, by :func:`model_point_table` itself, which numpy would otherwise
cast to the least int64 without a word. A fraction of a year truncates, as
:mod:`~.CI_UK_S`'s ``int`` truncates it.
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

    Indexed by ``point_id``. Eight columns are the in-force interface: ``policy_count``
    and ``duration_mth``, the completed policy months at the valuation date, as in
    ``basiclife.BasicTerm_SE``, and the six of a point's opening state. The rest are
    :mod:`~.CI_UK_S`'s, but ``pols_if_init``, which ``policy_count`` replaces, and
    ``row_kind``, ``source_policy_id`` and ``source_mth``, which record where the generator
    took each shipped row from and which no formula reads.

    The checks run over the whole table at once, and the first that fails raises
    ``ValueError``, naming the missing column or every point it fails on:

    1. the eight in-force columns are present;
    2. no ``point_id`` appears twice;
    3. ``policy_count`` is a number, zero or more;
    4. ``duration_mth`` is a whole number of months, below ``2**53`` in size, which numpy
       would otherwise cast to the least int64 without a word: positive for a policy in
       force, 0 for one issued at the valuation date, negative for one issued later;
    5. no policy is issued more than ``future_horizon_mth`` months after the valuation
       date, so ``duration_mth`` is ``-future_horizon_mth`` or more. At 0 the model takes
       no future new business, and the message says so; a horizon that is not a whole
       number of months, 0 or more, is itself refused, since a NaN one fails every
       comparison and so would admit every policy, and an infinite one bounds nothing;
    6. the opening state is a number in its range: the two indexation factors 1 or more,
       the RPI increase being floored at 0; ``review_prem_factor_init``, a factor on a
       premium, 0 or more; ``ci_sel_latched_init``, the latch, 0 or 1;
       ``ci_sel_factor_init``, a multiple of a diagnosis rate, 0 or more, the factor of a
       latch closed at a loading of -1 being 0; and
       ``review_prem_shock_init``, a premium change, -1 or more, since no review takes a
       premium below 0;
    7. a policy not yet in force, ``duration_mth`` 0 or less, holds the issue values: 1
       for the four factors, and 0 for the latch and the review's change;
    8. a policy in force fewer than 12 months, before its first anniversary, holds
       indexation factors of 1, no increase having been given;
    9. an open latch, ``ci_sel_latched_init`` 0, holds a factor of 1: the factor is read
       only once the latch has closed;
    10. each of ``children_cover`` and ``indexation`` is True or False. pandas reads a
        column of them as booleans, but one blank or one other text leaves the whole
        column text or mixed, and ``bool("False")`` is True;
    11. ``contract_type`` is accelerated or standalone, ``life_basis`` single or
        joint_first_event, ``sex`` M or F, ``smoker`` NS or S, ``cover_basis`` level,
        ``premium_guarantee`` guaranteed or reviewable and ``premium_mode`` monthly or
        annual;
    12. ``age_at_entry`` and ``policy_term`` are finite numbers, which :mod:`~.CI_UK_S`
        reads with ``int``, below ``2**53`` in size, which numpy would otherwise cast to
        the least int64 without a word; and ``sum_assured`` and ``premium_mth`` numbers,
        zero or more;
    13. a joint first-event point has a second life: ``joint_age`` a finite number below
        ``2**53`` in size, ``joint_sex`` M or F and ``joint_smoker`` NS or S;
    14. no joint first-event point is on the standalone contract, which
        :mod:`~.CI_UK_S` scopes out;
    15. the indexation factors are 1 without indexation, and on a guaranteed point the
        review factor 1, the latch open and the review's change 0.
    """
    name = model_point_file                                          # noqa: F821
    table = pd.read_csv(input_dir() / name, index_col="point_id")    # noqa: F821
    for column in ("policy_count", "duration_mth", "idx_factor_init",
                   "idx_prem_factor_init", "review_prem_factor_init", "ci_sel_latched_init",
                   "ci_sel_factor_init", "review_prem_shock_init"):
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
    if not (horizon >= 0 and horizon % 1 == 0):
        raise ValueError(f"future_horizon_mth must be a whole number of months, 0 or more, "
                         f"not {int(horizon) if horizon % 1 == 0 else horizon}")
    bad = table.index[months < -horizon].tolist()
    if bad and horizon == 0:
        raise ValueError(f"{name}: duration_mth must be 0 or more: this model takes no "
                         f"future new business; it is not at point_id {bad}")
    if bad:
        raise ValueError(f"{name}: duration_mth must be -{int(horizon)} or more, a policy "
                         f"issued at most {int(horizon)} months after the valuation date; "
                         f"it is not at point_id {bad}")
    state = {}
    for column, holds, rule in (
            ("idx_factor_init", lambda v: v >= 1.0, "a number, 1 or more"),
            ("idx_prem_factor_init", lambda v: v >= 1.0, "a number, 1 or more"),
            ("review_prem_factor_init", lambda v: v >= 0.0, "a number, zero or more"),
            ("ci_sel_latched_init", lambda v: (v == 0) | (v == 1), "0 or 1"),
            ("ci_sel_factor_init", lambda v: v >= 0.0, "a number, zero or more"),
            ("review_prem_shock_init", lambda v: v >= -1.0, "a number, -1 or more")):
        v = pd.to_numeric(table[column], errors="coerce")            # noqa: F821
        bad = table.index[~(holds(v) & (v < float("inf")))].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be {rule}; it is not at point_id "
                             f"{bad}")
        state[column] = v
    issue = {"idx_factor_init": 1, "idx_prem_factor_init": 1, "review_prem_factor_init": 1,
             "ci_sel_latched_init": 0, "ci_sel_factor_init": 1, "review_prem_shock_init": 0}
    for column, value in issue.items():
        bad = table.index[(months <= 0) & (state[column] != value)].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be {value} on a policy not yet in "
                             f"force, duration_mth 0 or less; it is not at point_id {bad}")
    for column in ("idx_factor_init", "idx_prem_factor_init"):
        bad = table.index[(months > 0) & (months < 12) & (state[column] != 1)].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be 1 on a policy in force fewer than "
                             f"12 months, before its first anniversary; it is not at "
                             f"point_id {bad}")
    open_latch = state["ci_sel_latched_init"] == 0
    bad = table.index[open_latch & (state["ci_sel_factor_init"] != 1)].tolist()
    if bad:
        raise ValueError(f"{name}: ci_sel_factor_init must be 1 on an open latch, "
                         f"ci_sel_latched_init 0; it is not at point_id {bad}")
    for column in ("children_cover", "indexation"):
        flag = table[column]
        bad = table.index[~flag.map(lambda v: str(v).lower() in ("true", "false"))].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be True or False; it is not at "
                             f"point_id {bad}")
    for column, codes in (("contract_type", ("accelerated", "standalone")),
                          ("life_basis", ("single", "joint_first_event")),
                          ("sex", ("M", "F")), ("smoker", ("NS", "S")),
                          ("cover_basis", ("level",)),
                          ("premium_guarantee", ("guaranteed", "reviewable")),
                          ("premium_mode", ("monthly", "annual"))):
        bad = table.index[~table[column].isin(codes)].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be {' or '.join(codes)}; it is not "
                             f"at point_id {bad}")
    rules = {"finite": ("a finite number",
                        lambda v: (v > -float("inf")) & (v < float("inf"))),
             "amount": ("a number, zero or more",
                        lambda v: (v >= 0) & (v < float("inf")))}
    for column, kind in (("age_at_entry", "finite"), ("policy_term", "finite"),
                         ("sum_assured", "amount"), ("premium_mth", "amount")):
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
    joint = table["life_basis"] == "joint_first_event"
    ages = pd.to_numeric(table["joint_age"], errors="coerce")        # noqa: F821
    bad = table.index[joint & ~((ages > -float("inf")) & (ages < float("inf")))].tolist()
    if bad:
        raise ValueError(f"{name}: joint_age must be a finite number on a joint "
                         f"first-event point; it is not at point_id {bad}")
    bad = table.index[joint & ~(ages.abs() < 2.0 ** 53)].tolist()
    if bad:
        raise ValueError(f"{name}: joint_age must be below 2**53 in size on a joint "
                         f"first-event point; it is not at point_id {bad}")
    for column, codes in (("joint_sex", ("M", "F")), ("joint_smoker", ("NS", "S"))):
        bad = table.index[joint & ~table[column].isin(codes)].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be {' or '.join(codes)} on a joint "
                             f"first-event point; it is not at point_id {bad}")
    bad = table.index[joint & (table["contract_type"] == "standalone")].tolist()
    if bad:
        raise ValueError(f"{name}: a joint first-event point must be accelerated, the "
                         f"standalone joint first event being out of scope; it is not at "
                         f"point_id {bad}")
    indexed = table["indexation"].map(lambda v: str(v).lower() == "true")
    guaranteed = table["premium_guarantee"] == "guaranteed"
    for column, value, flag, what in (
            ("idx_factor_init", 1, ~indexed, "without indexation"),
            ("idx_prem_factor_init", 1, ~indexed, "without indexation"),
            ("review_prem_factor_init", 1, guaranteed, "on a guaranteed point"),
            ("ci_sel_latched_init", 0, guaranteed, "on a guaranteed point"),
            ("review_prem_shock_init", 0, guaranteed, "on a guaranteed point")):
        bad = table.index[flag & (state[column] != value)].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be {value} {what}; it is not at "
                             f"point_id {bad}")
    return table


def ci_rate_table():
    """The CI diagnosis and mortality pivot rates, from *ci_rate_table.csv*, checked.

    Annual rates at the pivot ages 40, 45, 50, 55, 60 and 65 by sex and smoker status.
    ``i_ci`` is the first-diagnosis rate for a listed condition including total and
    permanent disability; ``q_d`` is best-estimate mortality.  Both are **[std]**
    proxies - the CMI accelerated-CI tables are subscriber-restricted - and the file's
    ``provenance`` column says which cells came from the notes and which from a
    sex/smoker factor.

    :mod:`~.CI_UK_S`'s reader, indexed by sex, smoker and age and sorted, as it returns
    it: :func:`i_ci_array` and :func:`q_d_array` slice the frame by (sex, smoker), as
    :mod:`~.CI_UK_S`'s ``pivot_interp`` does, and pandas warns about indexing past the
    lexsort depth of an unsorted MultiIndex.  Here the file is checked first, as read, so
    that each fault is named by its line, the header line 1, and the first rule that fails
    raises ``ValueError``:

    1. each age is a whole number, read by its value, so ``40.0`` is 40;
    2. each sex is M or F, and each smoker status NS or S, the codes the model point table
       holds;
    3. each of the four groups, M and F by NS and S, holds two pivot ages or more, one row
       an age: the interpolation reads the two pivots about an age and extrapolates from
       the two at an end. Every fault is named in one message: an age a group repeats with
       its lines, and a group with fewer than two;
    4. each ``i_ci`` and ``q_d`` is a number above 0 and at most 1, a probability: the
       interpolation raises the ratio of two of them to a power, which has no real value
       below 0 and divides by zero at 0.

    The pivot ages need not run without a gap, nor be the same in each group: each
    interpolation reads its own group's two pivots about an age.
    """
    name = ci_rate_file                                              # noqa: F821
    tbl = pd.read_csv(input_dir() / name)                            # noqa: F821
    lines = tbl.index + 2
    ages = pd.to_numeric(tbl["age"], errors="coerce")                # noqa: F821
    bad = lines[(~(ages % 1 == 0)).to_numpy()].tolist()
    if bad:
        raise ValueError(f"{name}: age must be a whole number; it is not on line {bad}")
    bad = lines[(~(tbl["sex"].isin(["M", "F"])
                   & tbl["smoker"].isin(["NS", "S"]))).to_numpy()].tolist()
    if bad:
        raise ValueError(f"{name}: sex must be M or F, and smoker NS or S; they are not "
                         f"on line {bad}")
    ages = ages.astype("int64")
    faults = []
    for s in ("M", "F"):
        for k in ("NS", "S"):
            group = ((tbl["sex"] == s) & (tbl["smoker"] == k)).to_numpy()
            run = ages[group]
            for a in sorted(set(run[run.duplicated()])):
                faults.append(f"sex {s}, smoker {k}, age {a} repeats on lines "
                              f"{lines[group & (ages == a).to_numpy()].tolist()}")
            held = len(set(run))
            if held < 2:
                faults.append(f"sex {s}, smoker {k} holds {held} pivot "
                              + ("age" if held == 1 else "ages"))
    if faults:
        raise ValueError(f"{name}: each sex and smoker status must hold two pivot ages or "
                         f"more, one row an age; " + "; ".join(faults))
    for column in ("i_ci", "q_d"):
        rates = pd.to_numeric(tbl[column], errors="coerce")          # noqa: F821
        bad = lines[(~((rates > 0) & (rates <= 1))).to_numpy()].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be a number above 0 and at most 1; "
                             f"it is not on line {bad}")
    return tbl.set_index(["sex", "smoker", "age"]).sort_index()


def lapse_table():
    """The lapse rates by policy year, read from *lapse_table.csv*.

    The ``policy_year`` key is the contractual 1-based label (1, 2, ..., 6+), not the
    projection's 0-based month index ``t``; ``Projection.lapse_rate_base`` reads the row
    ``policy_year(t)`` on the policy clock, and the rate it returns is the **annual** one
    the table is quoted in.  :mod:`~.CI_UK_S`'s reader, unchanged;
    :func:`lapse_last_year` checks the table.
    """
    return pd.read_csv(                                              # noqa: F821
        input_dir() / lapse_table_file, index_col="policy_year")     # noqa: F821


def lapse_last_year():
    """The last policy year *lapse_table.csv* gives a rate for, the table checked first.

    ``Projection.lapse_rate_base`` asks it before it reads the table, and reads every
    later policy year at it, :mod:`~.CI_UK_S`'s ``tbl.index.max()``, and
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


def age_at_entry():
    """The issue age (ANB) of the first life of every model point: int64 [point].

    Read as :mod:`~.CI_UK_S` reads it, ``int`` of the number, which truncates a
    fraction; :func:`model_point_table` has refused one that is not a finite number below
    ``2**53`` in size.
    """
    ages = pd.to_numeric(model_point_table()["age_at_entry"])        # noqa: F821
    return ages.to_numpy(dtype="int64")


def is_joint():
    """1 where a model point covers two lives on a first-event basis, else 0: int64
    [point].

    The ``life_basis`` column decoded as :mod:`~.CI_UK_S`'s ``is_joint`` compares it,
    ``life_basis() == "joint_first_event"``, element by element, exactly;
    :func:`model_point_table` has refused a basis other than ``single`` and
    ``joint_first_event``, and a joint point on the standalone contract.  An int, not a
    bool: a numpy bool array compiles as a Python object, not a memoryview.
    """
    bases = model_point_table()["life_basis"].tolist()
    out = np.zeros(len(bases), dtype="int64")                        # noqa: F821
    for i in range(len(bases)):
        out[i] = 1 if bases[i] == "joint_first_event" else 0
    return out


def joint_age():
    """The issue age (ANB) of the second life of every joint model point: int64 [point].

    ``int`` of the ``joint_age`` column, as :mod:`~.CI_UK_S` reads it, on a joint
    first-event point, where :func:`model_point_table` has refused a value that is not a
    finite number below ``2**53`` in size; 0 on any other point, whose column no formula
    reads and the table may hold blank, as the shipped single-life points do.
    :func:`is_joint` is the flag beside it, which ``Projection.age_at_entry`` asks first,
    so that no NaN reaches a formula.
    """
    table = model_point_table()
    bases = table["life_basis"].tolist()
    ages = pd.to_numeric(table["joint_age"], errors="coerce").tolist()  # noqa: F821
    out = np.zeros(len(ages), dtype="int64")                         # noqa: F821
    for i in range(len(ages)):
        if bases[i] == "joint_first_event":
            out[i] = int(ages[i])
    return out


def rate_group():
    """The pivot arrays' row for the first life of every model point: int64 [point].

    The point's ``sex`` and ``smoker`` status, the key :mod:`~.CI_UK_S`'s ``pivot_interp``
    reads *ci_rate_table.csv* by, numbered as :func:`i_ci_array` and :func:`q_d_array`
    table the four groups: M NS 0, M S 1, F NS 2 and F S 3.  :func:`model_point_table` has
    refused a code the table cannot hold, so every point has one of the four, and
    :func:`ci_rate_table` holds two pivot ages or more in each.
    """
    table = model_point_table()
    sexes, smokers = table["sex"].tolist(), table["smoker"].tolist()
    out = np.zeros(len(sexes), dtype="int64")                        # noqa: F821
    for i in range(len(sexes)):
        out[i] = 2 * ("M", "F").index(sexes[i]) + ("NS", "S").index(smokers[i])
    return out


def joint_rate_group():
    """The pivot arrays' row for the second life of every joint model point: int64
    [point].

    The point's ``joint_sex`` and ``joint_smoker``, numbered as :func:`rate_group`
    numbers the first life's, on a joint first-event point, where
    :func:`model_point_table` has refused a code the table cannot hold; 0 on any other
    point, whose columns no formula reads and the table may hold blank.  :func:`is_joint`
    is the flag beside it, which ``Projection.rate_group`` asks first.
    """
    table = model_point_table()
    bases = table["life_basis"].tolist()
    sexes = table["joint_sex"].tolist()
    smokers = table["joint_smoker"].tolist()
    out = np.zeros(len(sexes), dtype="int64")                        # noqa: F821
    for i in range(len(sexes)):
        if bases[i] == "joint_first_event":
            out[i] = 2 * ("M", "F").index(sexes[i]) + ("NS", "S").index(smokers[i])
    return out


def policy_term():
    """The term in years of every model point: int64 [point].

    Read as :mod:`~.CI_UK_S` reads it, ``int`` of the number, which truncates a
    fraction; :func:`model_point_table` has refused one that is not a finite number below
    ``2**53`` in size.  ``Projection.proj_len`` refuses a term outside the contract's.
    """
    terms = pd.to_numeric(model_point_table()["policy_term"])        # noqa: F821
    return terms.to_numpy(dtype="int64")


def sum_assured():
    """The sum assured at outset of every model point: float64 [point]."""
    return pd.to_numeric(model_point_table()["sum_assured"]).to_numpy(  # noqa: F821
        dtype="float64")


def premium_mth():
    """The monthly premium at outset of every model point: float64 [point]."""
    return pd.to_numeric(model_point_table()["premium_mth"]).to_numpy(  # noqa: F821
        dtype="float64")


def is_accelerated():
    """1 where a model point's ``contract_type`` is ``accelerated``, else 0: int64 [point].

    :mod:`~.CI_UK_S`'s comparison, ``contract_type() == "accelerated"``, made element by
    element, exactly; :func:`model_point_table` has refused a type other than
    ``accelerated`` and ``standalone``, so 0 is the standalone contract.
    """
    types = model_point_table()["contract_type"].tolist()
    out = np.zeros(len(types), dtype="int64")                        # noqa: F821
    for i in range(len(types)):
        out[i] = 1 if types[i] == "accelerated" else 0
    return out


def is_reviewable():
    """1 where a model point's ``premium_guarantee`` is ``reviewable``, else 0: int64
    [point].

    :mod:`~.CI_UK_S`'s comparison, ``premium_guarantee() == "reviewable"``, made element
    by element, exactly; :func:`model_point_table` has refused a guarantee other than
    ``guaranteed`` and ``reviewable``, so 0 is the guaranteed premium.
    """
    guarantees = model_point_table()["premium_guarantee"].tolist()
    out = np.zeros(len(guarantees), dtype="int64")                   # noqa: F821
    for i in range(len(guarantees)):
        out[i] = 1 if guarantees[i] == "reviewable" else 0
    return out


def children_cover():
    """Whether each model point's children's cover is active: int64 [point], 1 or 0.

    :mod:`~.CI_UK_S` reads the column with ``bool``.  :func:`model_point_table` has
    refused a value whose text is not True or False, in either case, so pandas reads the
    column as booleans, and each is decoded by its text, element by element, which is
    ``bool`` of each wherever the table reads.  An int, not a bool: a numpy bool array
    compiles as a Python object, not a memoryview.
    """
    flags = model_point_table()["children_cover"].tolist()
    out = np.zeros(len(flags), dtype="int64")                        # noqa: F821
    for i in range(len(flags)):
        out[i] = 1 if str(flags[i]).lower() == "true" else 0
    return out


def indexation():
    """Whether each model point elects the increasing-cover option: int64 [point], 1 or 0.

    Decoded as :func:`children_cover` decodes its column.
    """
    flags = model_point_table()["indexation"].tolist()
    out = np.zeros(len(flags), dtype="int64")                        # noqa: F821
    for i in range(len(flags)):
        out[i] = 1 if str(flags[i]).lower() == "true" else 0
    return out


def policy_count():
    """The ``policy_count`` of every model point: float64 [point].

    :func:`model_point_table` has checked it: a number, zero or more.
    """
    return pd.to_numeric(model_point_table()["policy_count"]).to_numpy(  # noqa: F821
        dtype="float64")


def duration_mth():
    """The ``duration_mth`` of every model point, in whole months: int64 [point].

    :func:`model_point_table` has checked that each is whole and below ``2**53`` in size,
    so a duration written as ``12.0`` is the int 12.
    """
    months = pd.to_numeric(model_point_table()["duration_mth"])      # noqa: F821
    return months.to_numpy(dtype="int64")


def idx_factor_init():
    """The cover indexation factor already given at the valuation date: float64 [point]."""
    return pd.to_numeric(model_point_table()["idx_factor_init"]).to_numpy(  # noqa: F821
        dtype="float64")


def idx_prem_factor_init():
    """The premium indexation factor already given at the valuation date: float64
    [point]."""
    return pd.to_numeric(                                            # noqa: F821
        model_point_table()["idx_prem_factor_init"]).to_numpy(dtype="float64")


def review_prem_factor_init():
    """The premium factor the reviews have given by the valuation date: float64 [point]."""
    return pd.to_numeric(                                            # noqa: F821
        model_point_table()["review_prem_factor_init"]).to_numpy(dtype="float64")


def ci_sel_latched_init():
    """The select latch at the valuation date, 1 closed and 0 open: int64 [point].

    :func:`model_point_table` has checked that each is 0 or 1, so a latch written as
    ``1.0`` is the int 1.
    """
    return pd.to_numeric(                                            # noqa: F821
        model_point_table()["ci_sel_latched_init"]).to_numpy(dtype="int64")


def ci_sel_factor_init():
    """The anti-selection factor the select latch closed at: float64 [point]."""
    return pd.to_numeric(                                            # noqa: F821
        model_point_table()["ci_sel_factor_init"]).to_numpy(dtype="float64")


def review_prem_shock_init():
    """The premium change the last review before the valuation date made: float64
    [point]."""
    return pd.to_numeric(                                            # noqa: F821
        model_point_table()["review_prem_shock_init"]).to_numpy(dtype="float64")


def rate_age_first():
    """The first attained age the pivot arrays hold a rate at, ``rate_age_min``, checked.

    ``Projection.ci_rate_base`` and ``Projection.mort_rate`` ask it, and
    :func:`rate_age_last`, before they read the arrays, and :func:`i_ci_array` and
    :func:`q_d_array` are built from the two, so that a table or an extent this cannot
    read is refused before any rate is.  It asks :func:`ci_rate_table` first, which
    checks the pivot table, and then refuses ``rate_age_min`` and ``rate_age_max`` unless
    each is a whole number, ``rate_age_min`` 0 or more and ``rate_age_max`` no less: they
    are the extent of an array indexed by the attained age.

    The two are the attained ages the contract admits, ``Projection.issue_age_min``, 18,
    to ``Projection.expiry_age_max`` less one, 74, which this Space cannot read, and so
    holds as References of its own; a test holds the two to the contract.  A contract
    whose bounds are moved past them needs them moved too: an age outside them is refused
    by the cell that reads it, naming the point and the age.
    """
    ci_rate_table()
    low, high = rate_age_min, rate_age_max                           # noqa: F821
    if not (low >= 0 and low % 1 == 0 and high % 1 == 0 and high >= low):
        raise ValueError(
            f"rate_age_min and rate_age_max must be whole numbers, 0 <= rate_age_min <= "
            f"rate_age_max; they are {int(low) if low % 1 == 0 else low} and "
            f"{int(high) if high % 1 == 0 else high}")
    return int(low)


def rate_age_last():
    """The last attained age the pivot arrays hold a rate at, ``rate_age_max``, read once
    :func:`rate_age_first` has checked the table and the two."""
    rate_age_first()
    return int(rate_age_max)                                         # noqa: F821


def i_ci_array():
    """The diagnosis rate by row and attained age, interpolated from *ci_rate_table.csv*:
    float64 [group, age].

    Row ``g`` is a sex and smoker group, M NS 0, M S 1, F NS 2 and F S 3, as
    :func:`rate_group` and :func:`joint_rate_group` number each life's, and column ``x``
    the attained age ``x``: padded from age 0, as ``basiclife.BasicTerm_SC``'s
    ``mort_table_array`` pads its table, so that the index **is** the age, and
    :func:`rate_age_last` plus one wide.  Each age from :func:`rate_age_first` to
    :func:`rate_age_last` holds :mod:`~.CI_UK_S`'s ``pivot_interp(x, sex, smoker,
    "i_ci")``, built here by its own formula, element by element, on Python floats, so
    that each element is the float its call returns: log-linear between the group's two
    pivot ages about ``x``, ``r0 (r1/r0)^((x - x0)/(x1 - x0))``, and extrapolated from the
    two at the nearer end outside them, the same expression with the exponent outside 0 to
    1.  The ages below the first hold NaN, which no formula reads:
    ``Projection.ci_rate_base`` refuses an age outside the two, naming the point.  Asks the
    two first, which check the pivot table, so each pivot is a number above 0 and at most
    1, and the ratio's power is real.

    It may still not be finite: two pivots far apart extrapolate past the largest float at
    an age a point may never reach, where the power overflows, and a pivot below about
    5.6e-309 can make the ratio itself infinite.  :mod:`~.CI_UK_S` raises ``OverflowError``
    only when a point reaches such an age, naming nothing, and reads an infinite rate, which
    its cap takes for a certain claim; here every age the contract admits is built, so the
    table is refused, ``ValueError`` naming the file, the column, the group and the first
    age whose rate is not finite, as an infinite rate in the file is refused.
    """
    first, last = rate_age_first(), rate_age_last()
    tbl = ci_rate_table()
    out = np.full((4, last + 1), np.nan)                             # noqa: F821
    for g in range(4):
        sex, smoker = ("M", "M", "F", "F")[g], ("NS", "S", "NS", "S")[g]
        sub = tbl.loc[(sex, smoker)]
        ages = sorted(int(a) for a in sub.index)
        for x in range(first, last + 1):
            if x <= ages[0]:
                lo, hi = ages[0], ages[1]
            elif x >= ages[-1]:
                lo, hi = ages[-2], ages[-1]
            else:
                lo = max(a for a in ages if a <= x)
                hi = min(a for a in ages if a > x)
            r_lo = float(sub.loc[lo, "i_ci"])
            r_hi = float(sub.loc[hi, "i_ci"])
            try:
                rate = r_lo * (r_hi / r_lo) ** ((x - lo) / (hi - lo))
            except OverflowError:
                rate = float("inf")
            if not rate - rate == 0.0:                               # inf, or NaN
                raise ValueError(
                    f"{ci_rate_file}: i_ci for sex {sex}, smoker {smoker} is "  # noqa: F821
                    f"not a finite number at attained age {x}, an age the contract "
                    f"admits, interpolated log-linearly from its pivot ages {lo} and {hi}")
            out[g, x] = rate
    return out


def q_d_array():
    """The mortality rate by row and attained age, interpolated from *ci_rate_table.csv*:
    float64 [group, age].

    :func:`i_ci_array`'s table of the ``q_d`` column: :mod:`~.CI_UK_S`'s
    ``pivot_interp(x, sex, smoker, "q_d")`` at each age the contract admits, by the same
    formula, element by element, and NaN below the first, which
    ``Projection.mort_rate`` never reads.  A rate that is not a finite number refuses the
    table, as :func:`i_ci_array`'s does.
    """
    first, last = rate_age_first(), rate_age_last()
    tbl = ci_rate_table()
    out = np.full((4, last + 1), np.nan)                             # noqa: F821
    for g in range(4):
        sex, smoker = ("M", "M", "F", "F")[g], ("NS", "S", "NS", "S")[g]
        sub = tbl.loc[(sex, smoker)]
        ages = sorted(int(a) for a in sub.index)
        for x in range(first, last + 1):
            if x <= ages[0]:
                lo, hi = ages[0], ages[1]
            elif x >= ages[-1]:
                lo, hi = ages[-2], ages[-1]
            else:
                lo = max(a for a in ages if a <= x)
                hi = min(a for a in ages if a > x)
            r_lo = float(sub.loc[lo, "q_d"])
            r_hi = float(sub.loc[hi, "q_d"])
            try:
                rate = r_lo * (r_hi / r_lo) ** ((x - lo) / (hi - lo))
            except OverflowError:
                rate = float("inf")
            if not rate - rate == 0.0:                               # inf, or NaN
                raise ValueError(
                    f"{ci_rate_file}: q_d for sex {sex}, smoker {smoker} is "  # noqa: F821
                    f"not a finite number at attained age {x}, an age the contract "
                    f"admits, interpolated log-linearly from its pivot ages {lo} and {hi}")
            out[g, x] = rate
    return out


def lapse_table_array():
    """The annual lapse rate by policy year, from *lapse_table.csv*: float64 [policy
    year].

    Element ``y`` is the rate of policy year ``y``, from 1 to :func:`lapse_last_year`,
    which checks the table first: the years run from 1 without a gap.  Element 0, no
    policy year, holds NaN, which no formula reads: ``Projection.lapse_rate_base`` reads
    a policy year of cover, 1 or more, at most the last, which it reads every later year
    at, as :mod:`~.CI_UK_S` does.
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

ci_rate_file = "ci_rate_table.csv"

lapse_table_file = "lapse_table.csv"

future_horizon_mth = 120

rate_age_min = 18

rate_age_max = 74

pd = ("Module", "pandas")

np = ("Module", "numpy")
