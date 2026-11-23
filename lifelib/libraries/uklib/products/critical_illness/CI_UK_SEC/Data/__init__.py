# modelx: pseudo-python
# This file is part of a modelx model.
# It can be imported as a Python module, but functions defined herein
# are model formulas and may not be executable as standard Python.

"""Input data shared by every by-policy projection.

The three input CSVs are read here, **once per model**, and referenced from
:mod:`~.CI_UK_SEC.Projection` as ``data``. :mod:`~.CI_UK_SEC.Projection` is
parameterized by ``point_id``, so each ``Projection[N]`` is a separate ItemSpace with its
own cells cache; if the readers lived there, every model point would re-read every file.
Holding them in an unparameterized Space reads each file once no matter how many policies
are projected.

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
intermediate ages are interpolated log-linearly. The interpolation therefore lives in
``Projection.pivot_interp`` rather than being baked into a pre-expanded file, and
swapping in a licensed AC04 or "16" Series basis means replacing a 24-row table, not a
generated one.

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
It refuses, too, what :mod:`~.CI_UK_S` projects without a word or meets only when a
projection reaches it: a flag that is not True or False, a code that names no contract
type, life basis, sex, smoker status, cover basis, premium guarantee or premium mode, an
age, a term or an amount that is not a number in its range, a joint point with no second
life or on the standalone contract, an indexation history before the first anniversary,
an open latch with a factor, and a history of indexation or reviews on a point without
the option or the reviews. The checks run in turn, and the first that fails raises,
naming the missing column or every point that fails it. Whether a point is still in cover
at the valuation date, whether the contract issues it, and whether a reviewable point has
had the reviews its history says, are rules of the product, and ``Projection.proj_len``
checks them, against its own References.

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
which it asks before it reads the table.
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
       no future new business, and the message says so; a negative horizon is itself
       refused;
    6. the opening state is a number in its range: the two indexation factors 1 or more,
       the RPI increase being floored at 0; ``review_prem_factor_init``, a factor on a
       premium, 0 or more; ``ci_sel_latched_init``, the latch, 0 or 1;
       ``ci_sel_factor_init``, a multiple of a diagnosis rate, above 0; and
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
        reads with ``int``; and ``sum_assured`` and ``premium_mth`` numbers, zero or more;
    13. a joint first-event point has a second life: ``joint_age`` a finite number,
        ``joint_sex`` M or F and ``joint_smoker`` NS or S;
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
    for column, holds, rule in (
            ("idx_factor_init", lambda v: v >= 1.0, "a number, 1 or more"),
            ("idx_prem_factor_init", lambda v: v >= 1.0, "a number, 1 or more"),
            ("review_prem_factor_init", lambda v: v >= 0.0, "a number, zero or more"),
            ("ci_sel_latched_init", lambda v: (v == 0) | (v == 1), "0 or 1"),
            ("ci_sel_factor_init", lambda v: v > 0.0, "a number above 0"),
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
    joint = table["life_basis"] == "joint_first_event"
    ages = pd.to_numeric(table["joint_age"], errors="coerce")        # noqa: F821
    bad = table.index[joint & ~((ages > -float("inf")) & (ages < float("inf")))].tolist()
    if bad:
        raise ValueError(f"{name}: joint_age must be a finite number on a joint "
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
    it: ``Projection.pivot_interp`` slices the frame by (sex, smoker), and pandas warns
    about indexing past the lexsort depth of an unsorted MultiIndex.  Here the file is
    checked first, as read, so that each fault is named by its line, the header line 1,
    and the first rule that fails raises ``ValueError``:

    1. each age is a whole number, read by its value, so ``40.0`` is 40;
    2. each sex is M or F, and each smoker status NS or S, the codes the model point table
       holds;
    3. each of the four groups, M and F by NS and S, holds two pivot ages or more, one row
       an age: ``Projection.pivot_interp`` interpolates between the two pivots about an
       age and extrapolates from the two at an end. Every fault is named in one message:
       an age a group repeats with its lines, and a group with fewer than two;
    4. each ``i_ci`` and ``q_d`` is a number above 0 and at most 1, a probability:
       ``Projection.pivot_interp`` raises the ratio of two of them to a power, which has no
       real value below 0 and divides by zero at 0.

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
    later policy year at it, :mod:`~.CI_UK_S`'s ``tbl.index.max()``.  The rules, the
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

ci_rate_file = "ci_rate_table.csv"

lapse_table_file = "lapse_table.csv"

future_horizon_mth = 120

pd = ("Module", "pandas")
