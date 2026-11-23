# modelx: pseudo-python
# This file is part of a modelx model.
# It can be imported as a Python module, but functions defined herein
# are model formulas and may not be executable as standard Python.

"""Input data shared by every by-policy projection.

The three input CSVs are read here, **once per model**, and referenced from
:mod:`~.ULB_UK_SEC.Projection` as ``data``. :mod:`~.ULB_UK_SEC.Projection` is parameterized
by ``idx``, the position of a model point in the table, so each ``Projection[i]`` is a
separate ItemSpace with its own cells cache; if the readers lived there, every model point
would re-read every file. Holding them in an unparameterized Space reads each file once no
matter how many policies are projected.

Inputs are **external files**: plain CSVs in the model folder's parent directory,
``products/unit_linked_bond/``, rather than data stored inside the model. The model
folder therefore holds nothing but formulas — no ``_data/``, no IOSpec, no embedded
values — so a diff of the model shows logic changes only. This follows
``annuallife.TradLife_A``; contrast ``basiclife.BasicTerm_S``, which keeps its inputs
*inside* the model through modelx's IOSpec machinery.

The consequence worth knowing: **the model is not portable on its own.** Copying the
``ULB_UK_SEC`` folder without its parent's CSVs produces a model that reads and then
fails on first evaluation.

**Two of the tables are ULB_UK_S's.** The mortality and surrender tables are the files
:mod:`~.ULB_UK_S` reads, read here in place by :mod:`~.ULB_UK_S`'s own readers: one copy of
each table serves both models, so an edit to one reaches both. The model point table,
``model_point_table_sec.csv``, is this model's own, and sits beside :mod:`~.ULB_UK_S`'s
``model_point_table.csv``, which this model never opens.

:func:`input_dir` resolves the directory from ``_model.path.parent`` at run time, so
the model works wherever the repository is checked out. Each table has a filename
Reference and a reader Cells:

======================  ==========================  ==============================
Reference               Cells                       File
======================  ==========================  ==============================
model_point_file        model_point_table()         model_point_table_sec.csv
mort_table_file         mort_table()                mort_table.csv
surr_table_file         surr_table()                surr_table.csv
======================  ==========================  ==============================

**The model point table is checked as it is read.** Five of its columns are the in-force
interface: ``policy_count`` and ``duration_mth``, as in ``basiclife.BasicTerm_SE``, and the
opening state of a bond in force, ``av_pp_init``, ``wd_cum_pp_init`` and
``allowance_cum_pp_init``.
:func:`model_point_table` refuses a table that lacks one, repeats a ``point_id``, holds a
count, a duration or a state no bond can have, or a bond to be issued more than
``future_horizon_mth`` months after the valuation date, 120 as shipped: future new
business is written over a stated horizon, so that no frame runs longer than cover from
issue plus that horizon. Set to 0, the Reference refuses future new business altogether.
It refuses, too, what :mod:`~.ULB_UK_S` projects without a word or meets only when a
projection reaches it: a flag that is not True or False, a code that names no sex or
withdrawal pattern, a joint bond, which :mod:`~.ULB_UK_S`'s guard on ``lives`` would refuse
but which no formula of it calls, an age, a premium, a charge or a rate that is not a
number in its range, an issue age ``2**53`` or more in size, and a number of segments that
is not a whole number, 1 or more. The
checks run in turn, and the first that fails raises, naming the missing column or every
point that fails it. Whether a bond is still in cover at the valuation date, whether the
contract issues it, and whether its fund is exhausted there, are rules of the product,
and ``Projection.proj_len`` checks them, against its own References.

**Each assumption table is checked before a value of it is read.** Its keys are read by
their value, so an age written ``35.0`` is age 35, and a key that is not whole, text among
them, or is ``2**53`` or more in size, which int64 would hold inexactly, is refused; so are
keys that repeat or leave a gap the projection would read. A
value that is blank, text, infinite or outside its range is refused, whether or not a
point reads it: ``Projection.mort_rate`` caps the annual rate with ``min``, which keeps
its first argument unless a later one compares smaller, and no comparison with NaN
holds, so the cap is written with its bound second and a NaN would stay NaN; but an
infinity is a number, which the cap reads as 1, certain death. The check of each table is
in the cell the projection takes the table's extent from, which it asks before it reads
the table: :func:`mort_age_first` and :func:`mort_age_last` for the mortality table, and
:func:`surr_last_year` for the surrender table. Each refusal names the table's lines, the
header line 1: the check reads the file as it stands, where :mod:`~.ULB_UK_S`'s reader,
:func:`mort_table`, sorts the mortality table, and with the order would lose the lines. A
read beyond the
mortality table's ages is refused by the one ``Projection`` cell that reads it, naming the
point, where :mod:`~.ULB_UK_S`'s lookup raised ``KeyError``.

To swap in a licensed mortality basis, replace ``mort_table.csv`` with a same-schema file,
or point ``mort_table_file`` at a different name, then clear the cache. No formula
changes. Replacing a file changes :mod:`~.ULB_UK_S` too, which reads the same one. A
compiled model clears no cache, so there the name is set on a package just imported,
before anything is read.

**The vectors.** The readers return what the files hold, and no
:mod:`~.ULB_UK_SEC.Projection` cell but ``model_point``, a reporting cell, reads them.
The others read the arrays below instead, one element at a time, a model point's
attribute being the element at its position, ``data.premium()[idx]``. That is what lets
the model compile to C, as ``basiclife.BasicTerm_SC`` does: each array is a numpy vector
or table of int64 or float64, which compiles to a typed memoryview, never one of bools,
objects or text, and each extent of a table is an int.

Text the projection needs is decoded here, into the number it selects, for every point at
once, as :mod:`~.ULB_UK_S` reads each value: the sex into the mortality table's row, its
schedule, M 0 and F 1; the withdrawal pattern into its code, none 0, allowance_5pct 1 and
custom 2, ``Projection``'s References ``NONE``, ``ALLOWANCE_5PCT`` and ``CUSTOM``, which
stays a code because the anchor pattern's rate is ``Projection.wd_allowance_rate``, a
Reference this Space cannot read; and the rider's True or False into a 0/1 flag. And each
table keyed by more than a number becomes an integer-indexed array. The mortality table,
keyed by sex and age, is tabled by its schedule and padded from age 0, so that the index
is the attained age; the surrender table is a vector by policy year, padded at year 0:

==============================  =======  ================  =================================
Cells                           dtype    Shape             From
==============================  =======  ================  =================================
point_id()                      int64    [point]           the table's index
age_at_entry()                  int64    [point]           ``age_at_entry``
mort_schedule()                 int64    [point]           ``sex``, decoded: M 0, F 1
premium()                       float64  [point]           ``premium``
n_segments()                    int64    [point]           ``n_segments``
db_uplift()                     float64  [point]           ``db_uplift``
amc_rate()                      float64  [point]           ``amc_rate``
further_costs_rate()            float64  [point]           ``further_costs_rate``
tax_provision_rate()            float64  [point]           ``tax_provision_rate``
wd_pattern_code()               int64    [point]           ``wd_pattern``, decoded: none 0,
                                                           allowance_5pct 1, custom 2
wd_rate_custom()                float64  [point]           ``wd_rate_custom``
oac_rate()                      float64  [point]           ``oac_rate``
gmdb_flag()                     int64    [point]           ``gmdb_flag``, 0/1
policy_count()                  float64  [point]           ``policy_count``
duration_mth()                  int64    [point]           ``duration_mth``
av_pp_init()                    float64  [point]           ``av_pp_init``
wd_cum_pp_init()                float64  [point]           ``wd_cum_pp_init``
allowance_cum_pp_init()         float64  [point]           ``allowance_cum_pp_init``
mort_age_first()                int      scalar            *mort_table.csv*, checked
mort_age_last()                 int      scalar            *mort_table.csv*
mort_table_array()              float64  [schedule, age]   *mort_table.csv*
surr_last_year()                int      scalar            *surr_table.csv*, checked
surr_table_array()              float64  [policy year]     *surr_table.csv*
==============================  =======  ================  =================================

**An array is read by element, never whole,** in this Space as in
:mod:`~.ULB_UK_SEC.Projection`. The compiler types an array cell as a memoryview only
once it has seen that every use of it, in either Space, is an element read: one
``len()``, slice, loop over it or numpy call on it anywhere, and the cell compiles as a
Python object. So an array derived here reads the table's column, never another cell's
array, and a width comes from a table.

**What cannot be held is refused** when the table is first read, naming every point or
line at fault, beside the checks above: a ``point_id`` that is not a whole number below
``2**53`` in size, when :func:`point_id` is first read, as a refusal reads it; an
``age_at_entry`` that is not below ``2**53`` in size, by :func:`model_point_table`
itself; and a mortality age or a surrender policy year ``2**53`` or more in size, by the
table's check, each of which numpy would otherwise cast to int64 inexactly, or to the
least int64, without a word. A fraction of a year of age truncates, as
:mod:`~.ULB_UK_S`'s ``int`` truncates it.

Note what is **not** an input file. The charge rates — the annual management charge, the
fund-borne further costs, the tax provision rate, the death-benefit uplift — are model
point columns rather than a rate table, because they are per-policy contractual and
discretionary parameters rather than experience assumptions, and because per-fund charge
rate cards are not published anyway. The fund return is a single Reference on
``Projection``, because the base run is deterministic.
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
    ``basiclife.BasicTerm_SE``, and the three of a bond's opening state, ``av_pp_init``,
    ``wd_cum_pp_init`` and ``allowance_cum_pp_init``. The rest are :mod:`~.ULB_UK_S`'s, but ``pols_if_init``, which
    ``policy_count`` replaces, ``uf_init``, which is ``av_pp_init`` renamed, and
    ``row_kind``, ``source_policy_id`` and ``source_mth``, which record where the generator
    took each shipped row from and which no formula reads.

    The checks run over the whole table at once, and the first that fails raises
    ``ValueError``, naming the missing column or every point it fails on:

    1. the five in-force columns are present;
    2. no ``point_id`` appears twice;
    3. ``policy_count`` is a number, zero or more;
    4. ``duration_mth`` is a whole number of months, below ``2**53`` in size, which numpy
       would otherwise cast to the least int64 without a word: positive for a bond in
       force, 0 for one issued at the valuation date, negative for one issued later;
    5. no bond is issued more than ``future_horizon_mth`` months after the valuation
       date, so ``duration_mth`` is ``-future_horizon_mth`` or more. At 0 the model takes
       no future new business, and the message says so; a negative horizon is itself
       refused;
    6. the opening state is a number in its range: ``av_pp_init``, the unit fund per
       policy, above 0, a bond with no units having nothing to project;
       ``wd_cum_pp_init``, an amount withdrawn, 0 or more; and ``allowance_cum_pp_init``,
       an allowance accrued, 0 or more;
    7. a bond not yet in force, ``duration_mth`` 0 or less, has withdrawn nothing and
       accrued no allowance: ``wd_cum_pp_init`` and ``allowance_cum_pp_init`` are 0. Its
       ``av_pp_init`` keeps :mod:`~.ULB_UK_S`'s meaning, the
       fund at outset, its premium as shipped, as an S column that is a value at issue does
       (USLIB-SEC-PLAN.md D6, precised at M7), so this rule leaves it;
    8. ``gmdb_flag`` is True or False. pandas reads a column of them as booleans, but one
       blank or one other text leaves the whole column text or mixed, and
       ``bool("False")`` is True;
    9. ``sex`` is M or F, ``lives`` single and ``wd_pattern`` none, allowance_5pct or
       custom;
    10. ``age_at_entry`` is a finite number, which :mod:`~.ULB_UK_S` reads with ``int``,
        below ``2**53`` in size, which numpy would otherwise cast to the least int64
        without a word; ``premium`` and ``wd_rate_custom`` numbers, zero or more;
        ``db_uplift`` a number,
        1 or more, the death benefit being at least the bid value of units; ``amc_rate``,
        ``further_costs_rate``, ``tax_provision_rate`` and ``oac_rate``, annual rates on the
        fund or shares of its return, from 0 to 1; and ``n_segments`` a whole number, 1 or
        more, which the fund per segment divides by.
    """
    name = model_point_file                                          # noqa: F821
    table = pd.read_csv(input_dir() / name, index_col="point_id")    # noqa: F821
    for column in ("policy_count", "duration_mth", "av_pp_init", "wd_cum_pp_init",
                   "allowance_cum_pp_init"):
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
        raise ValueError(f"future_horizon_mth must be 0 months or more, not "
                         f"{int(horizon)}")
    bad = table.index[months < -horizon].tolist()
    if bad and horizon == 0:
        raise ValueError(f"{name}: duration_mth must be 0 or more: this model takes no "
                         f"future new business; it is not at point_id {bad}")
    if bad:
        raise ValueError(f"{name}: duration_mth must be -{int(horizon)} or more, a bond "
                         f"issued at most {int(horizon)} months after the valuation date; "
                         f"it is not at point_id {bad}")
    fund = pd.to_numeric(table["av_pp_init"], errors="coerce")       # noqa: F821
    bad = table.index[~((fund > 0) & (fund < float("inf")))].tolist()
    if bad:
        raise ValueError(f"{name}: av_pp_init must be a number above 0, the unit fund; "
                         f"it is not at point_id {bad}")
    drawn = pd.to_numeric(table["wd_cum_pp_init"], errors="coerce")  # noqa: F821
    bad = table.index[~((drawn >= 0) & (drawn < float("inf")))].tolist()
    if bad:
        raise ValueError(f"{name}: wd_cum_pp_init must be a number, zero or more; it is "
                         f"not at point_id {bad}")
    allowed = pd.to_numeric(table["allowance_cum_pp_init"], errors="coerce")  # noqa: F821
    bad = table.index[~((allowed >= 0) & (allowed < float("inf")))].tolist()
    if bad:
        raise ValueError(f"{name}: allowance_cum_pp_init must be a number, zero or more; "
                         f"it is not at point_id {bad}")
    for column, held in (("wd_cum_pp_init", drawn), ("allowance_cum_pp_init", allowed)):
        bad = table.index[(months <= 0) & (held != 0)].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be 0 on a bond not yet in force, "
                             f"duration_mth 0 or less; it is not at point_id {bad}")
    flag = table["gmdb_flag"]
    bad = table.index[~flag.map(lambda v: str(v).lower() in ("true", "false"))].tolist()
    if bad:
        raise ValueError(f"{name}: gmdb_flag must be True or False; it is not at "
                         f"point_id {bad}")
    for column, codes in (("sex", ("M", "F")), ("lives", ("single",)),
                          ("wd_pattern", ("none", "allowance_5pct", "custom"))):
        bad = table.index[~table[column].isin(codes)].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be {' or '.join(codes)}; it is not "
                             f"at point_id {bad}")
    rules = {"finite": ("a finite number",
                        lambda v: (v > -float("inf")) & (v < float("inf"))),
             "amount": ("a number, zero or more",
                        lambda v: (v >= 0) & (v < float("inf"))),
             "uplift": ("a number, 1 or more",
                        lambda v: (v >= 1) & (v < float("inf"))),
             "share": ("a number from 0 to 1", lambda v: (v >= 0) & (v <= 1)),
             "segments": ("a whole number, 1 or more",
                          lambda v: (v >= 1) & (v % 1 == 0) & (v < 2.0 ** 53))}
    for column, kind in (("age_at_entry", "finite"), ("premium", "amount"),
                         ("n_segments", "segments"), ("db_uplift", "uplift"),
                         ("amc_rate", "share"), ("further_costs_rate", "share"),
                         ("tax_provision_rate", "share"), ("wd_rate_custom", "amount"),
                         ("oac_rate", "share")):
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
    return table


def mort_table():
    """The base annual mortality rates by sex and age, from *mort_table.csv*.

    A **[std]** proxy shaped like the ONS UK national life tables, the only fully
    redistributable UK mortality source; the CMI's current assured-lives tables are
    restricted to Authorised Users.  ``Projection.mort_be_factor`` carries the crude
    allowance for population mortality being heavier than insured-lives experience.

    Mortality is nearly irrelevant on this product - the net amount at risk is a tenth
    of a percent of the unit fund - unless the guaranteed minimum death benefit rider is
    enabled, which is why a proxy of this quality is tolerable here and would not be
    elsewhere.  Sorted on read, because ``Projection.mort_rate`` indexes into it.
    :mod:`~.ULB_UK_S`'s reader, indexed and sorted as it is, from the one read of the file,
    :func:`mort_table_rows`; :func:`mort_age_first` checks the table.
    """
    return mort_table_rows().set_index(["sex", "age"]).sort_index()


def mort_table_rows():
    """*mort_table.csv* as the file holds it: one row a line, in the file's order.

    The one read of the file.  :func:`mort_age_first` checks it here, so that each refusal
    names the lines at fault, the header line 1, which the sort of :func:`mort_table`, the
    reader the projection indexes into, would lose.
    """
    return pd.read_csv(input_dir() / mort_table_file)                # noqa: F821


def surr_table():
    """The base annual full-surrender rates by policy year, from *surr_table.csv*.

    Low early, rising as the advised five-to-ten-year holding period completes, then
    settling at a high ultimate level.  A **[std]** drafting construction: no public UK
    bond persistency study was fetched.  On a product whose every margin line is
    proportional to the unit fund *and* to persistency, this is the first assumption to
    sensitivity-test.  The ``policy_year`` key is the contractual 1-based label, read at
    ``Projection.policy_year(t)`` on the policy clock.  :mod:`~.ULB_UK_S`'s reader,
    unchanged; :func:`surr_last_year` checks the table.
    """
    return pd.read_csv(                                              # noqa: F821
        input_dir() / surr_table_file, index_col="policy_year")      # noqa: F821


def mort_age_first():
    """The first attained age *mort_table.csv* gives a rate for, the table checked first.

    ``Projection.mort_rate`` asks it, and :func:`mort_age_last`, before it reads the
    table, so a table it cannot read is refused before any value of it is.  The check
    reads the file as it stands, :func:`mort_table_rows`, not :func:`mort_table`, which
    sorts it, so that each refusal names the lines at fault, the header line 1.  The
    rules, each over the whole table, the first that fails raising ``ValueError``:

    1. each age is a whole number, read by its value, so ``35.0`` is 35, and below
       ``2**53`` in size, which int64 holds exactly, the check made before the ages are
       cast;
    2. each sex is M or F, the codes the model point table holds;
    3. each sex runs over the table's ages from the first to the last, one row an age,
       none below 0: the projection reads a rate at each attained age a bond reaches.
       Every fault is named in one message: an age below 0 and an age a sex repeats each
       with its lines, and each span of ages a sex lacks, found from the ages each sex
       holds, so that a key far from the rest costs no more than the rows;
    4. each ``mort_rate`` is a number from 0 to 1, a probability, read by the cap.
    """
    name = mort_table_file                                           # noqa: F821
    tbl = mort_table_rows()
    lines = tbl.index + 2
    ages = pd.to_numeric(tbl["age"], errors="coerce")                # noqa: F821
    bad = lines[(~(ages % 1 == 0)).to_numpy()].tolist()
    if bad:
        raise ValueError(f"{name}: age must be a whole number; it is not on line {bad}")
    bad = lines[(~(ages.abs() < 2.0 ** 53)).to_numpy()].tolist()
    if bad:
        raise ValueError(f"{name}: age must be below 2**53 in size; it is not on line "
                         f"{bad}")
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
        for a in [*(int(a) for a in sorted(set(run))), last + 1]:
            if a > before + 1:
                spans.append([before + 1, a - 1])
            before = a
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
    ages = pd.to_numeric(mort_table().reset_index()["age"], errors="coerce")  # noqa: F821
    return int(ages.max())


def surr_last_year():
    """The last policy year *surr_table.csv* gives a rate for, the table checked first.

    ``Projection.surr_rate_base`` asks it before it reads the table, and reads every
    later policy year at it, :mod:`~.ULB_UK_S`'s ``tbl.index.max()``.  The rules, the
    first that fails raising ``ValueError`` and naming the lines, the header line 1: each
    policy year is a whole number, read by its value, below ``2**53`` in size, which int64
    holds exactly, the check made before the years are cast; the years run from 1, one row a
    year, without a gap or a repeat, since each policy year from the first is read, every
    fault named in one message, a year below 1 and a repeated one each with its lines, and
    each span the table lacks; and each ``surr_rate`` is a number from 0 to 1, a
    probability, which the surrender rate's ``min`` reads.
    """
    name = surr_table_file                                           # noqa: F821
    tbl = surr_table().reset_index()
    lines = tbl.index + 2
    years = pd.to_numeric(tbl["policy_year"], errors="coerce")       # noqa: F821
    bad = lines[(~(years % 1 == 0)).to_numpy()].tolist()
    if bad:
        raise ValueError(f"{name}: policy_year must be a whole number; it is not on line "
                         f"{bad}")
    bad = lines[(~(years.abs() < 2.0 ** 53)).to_numpy()].tolist()
    if bad:
        raise ValueError(f"{name}: policy_year must be below 2**53 in size; it is not on "
                         f"line {bad}")
    keys = years.astype("int64")
    faults = []
    for y in sorted(set(keys[keys < 1])):
        faults.append(f"policy_year {y}, below 1, is on lines "
                      f"{lines[(keys == y).to_numpy()].tolist()}")
    for y in sorted(set(keys[keys.duplicated() & (keys >= 1)])):
        faults.append(f"policy_year {y} repeats on lines "
                      f"{lines[(keys == y).to_numpy()].tolist()}")
    held = sorted(set(keys[keys >= 1]))
    spans, before = [], 0
    for y in (int(y) for y in held):
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
    rates = pd.to_numeric(tbl["surr_rate"], errors="coerce")         # noqa: F821
    bad = (tbl.index[~((rates >= 0) & (rates <= 1))] + 2).tolist()
    if bad:
        raise ValueError(f"{name}: surr_rate must be a number from 0 to 1; it is not on "
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
    """The issue age (ALB) of every model point: int64 [point].

    Read as :mod:`~.ULB_UK_S` reads it, ``int`` of the number, which truncates a
    fraction; :func:`model_point_table` has refused one that is not a finite number below
    ``2**53`` in size.
    """
    ages = pd.to_numeric(model_point_table()["age_at_entry"])        # noqa: F821
    return ages.to_numpy(dtype="int64")


def mort_schedule():
    """The mortality table's row for every model point, its sex decoded: int64 [point].

    The point's ``sex``, the key :mod:`~.ULB_UK_S` reads *mort_table.csv* by beside the
    age, numbered as :func:`mort_table_array` tables the two: M 0 and F 1.
    :func:`model_point_table` has refused any other code, so every point has one of the
    two, and each is a whole run of the table's ages, which :func:`mort_age_first` checks.
    """
    sexes = model_point_table()["sex"].tolist()
    out = np.zeros(len(sexes), dtype="int64")                        # noqa: F821
    for i in range(len(sexes)):
        out[i] = ("M", "F").index(sexes[i])
    return out


def premium():
    """The single premium of every model point: float64 [point]."""
    return pd.to_numeric(model_point_table()["premium"]).to_numpy(   # noqa: F821
        dtype="float64")


def n_segments():
    """The segments each model point's bond is written in: int64 [point].

    :func:`model_point_table` has refused one that is not a whole number, 1 or more,
    below ``2**53``.
    """
    segments = pd.to_numeric(model_point_table()["n_segments"])      # noqa: F821
    return segments.to_numpy(dtype="int64")


def db_uplift():
    """The death-benefit uplift of every model point: float64 [point]."""
    return pd.to_numeric(model_point_table()["db_uplift"]).to_numpy(  # noqa: F821
        dtype="float64")


def amc_rate():
    """The annual management charge of every model point: float64 [point]."""
    return pd.to_numeric(model_point_table()["amc_rate"]).to_numpy(  # noqa: F821
        dtype="float64")


def further_costs_rate():
    """The fund-borne further costs of every model point: float64 [point]."""
    return pd.to_numeric(                                            # noqa: F821
        model_point_table()["further_costs_rate"]).to_numpy(dtype="float64")


def tax_provision_rate():
    """The tax provision rate of every model point: float64 [point]."""
    return pd.to_numeric(                                            # noqa: F821
        model_point_table()["tax_provision_rate"]).to_numpy(dtype="float64")


def wd_pattern_code():
    """The withdrawal pattern of every model point, as its code: int64 [point].

    none 0, allowance_5pct 1 and custom 2, the ``Projection`` References ``NONE``,
    ``ALLOWANCE_5PCT`` and ``CUSTOM``, in the order :mod:`~.ULB_UK_S`'s ``wd_rate``
    compares the text.  A code, not the rate it selects, because the anchor pattern's rate
    is ``Projection.wd_allowance_rate``, a Reference this Space cannot read.
    :func:`model_point_table` has refused any other pattern, naming the point.
    """
    patterns = model_point_table()["wd_pattern"].tolist()
    out = np.zeros(len(patterns), dtype="int64")                     # noqa: F821
    for i in range(len(patterns)):
        out[i] = ("none", "allowance_5pct", "custom").index(patterns[i])
    return out


def wd_rate_custom():
    """The custom withdrawal rate of every model point: float64 [point]."""
    return pd.to_numeric(model_point_table()["wd_rate_custom"]).to_numpy(  # noqa: F821
        dtype="float64")


def oac_rate():
    """The ongoing adviser charge of every model point: float64 [point]."""
    return pd.to_numeric(model_point_table()["oac_rate"]).to_numpy(  # noqa: F821
        dtype="float64")


def gmdb_flag():
    """Whether each model point elects the GMDB rider: int64 [point], 1 or 0.

    :mod:`~.ULB_UK_S` reads the column with ``bool``.  :func:`model_point_table` has
    refused a value whose text is not True or False, in either case, so pandas reads the
    column as booleans, and each is decoded by its text, element by element, which is
    ``bool`` of each wherever the table reads.  An int, not a bool: a numpy bool array
    compiles as a Python object, not a memoryview.
    """
    flags = model_point_table()["gmdb_flag"].tolist()
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
    so a duration written as ``30.0`` is the int 30.
    """
    months = pd.to_numeric(model_point_table()["duration_mth"])      # noqa: F821
    return months.to_numpy(dtype="int64")


def av_pp_init():
    """The unit fund per policy the frame opens with, of every model point: float64
    [point]."""
    return pd.to_numeric(model_point_table()["av_pp_init"]).to_numpy(  # noqa: F821
        dtype="float64")


def wd_cum_pp_init():
    """The withdrawals and adviser charges since issue per policy, of every model point:
    float64 [point]."""
    return pd.to_numeric(model_point_table()["wd_cum_pp_init"]).to_numpy(  # noqa: F821
        dtype="float64")


def allowance_cum_pp_init():
    """The 5% allowance accrued since issue per policy, of every model point: float64
    [point]."""
    return pd.to_numeric(                                            # noqa: F821
        model_point_table()["allowance_cum_pp_init"]).to_numpy(dtype="float64")


def mort_table_array():
    """The mortality rates by schedule and attained age, from *mort_table.csv*: float64
    [schedule, age].

    Row ``s`` is a sex, M 0 and F 1, as :func:`mort_schedule` numbers each point's, and
    column ``a`` the attained age ``a``: padded from age 0, as ``basiclife.BasicTerm_SC``'s
    ``mort_table_array`` pads its table, so that the index **is** the age, and
    :func:`mort_age_last` plus one wide.  The ages below the table's first, 0 to 17 as
    shipped, hold NaN, which no formula reads: ``Projection.mort_rate`` refuses an age
    outside the table, naming the point.  Asks :func:`mort_age_first` first, which checks
    the table: each sex runs over every age from the first to the last, one row an age, so
    no cell between them is padding, and each rate is a number from 0 to 1.  Read from the
    one read of the file, :func:`mort_table_rows`, which :mod:`~.ULB_UK_S`'s reader sorts.
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


def surr_table_array():
    """The annual surrender rate by policy year, from *surr_table.csv*: float64 [policy
    year].

    Element ``y`` is the rate of policy year ``y``, from 1 to :func:`surr_last_year`, which
    checks the table first: the years run from 1 without a gap.  Element 0, no policy year,
    holds NaN, which no formula reads: ``Projection.surr_rate_base`` reads a policy year of
    cover, 1 or more, at most the last, which it reads every later year at, as
    :mod:`~.ULB_UK_S` does.
    """
    last = surr_last_year()
    tbl = surr_table().reset_index()
    years = pd.to_numeric(tbl["policy_year"]).to_numpy(dtype="int64")  # noqa: F821
    rates = pd.to_numeric(tbl["surr_rate"]).to_numpy(dtype="float64")  # noqa: F821
    out = np.full(last + 1, np.nan)                                  # noqa: F821
    out[years] = rates
    return out


# ---------------------------------------------------------------------------
# References

model_point_file = "model_point_table_sec.csv"

mort_table_file = "mort_table.csv"

surr_table_file = "surr_table.csv"

future_horizon_mth = 120

pd = ("Module", "pandas")

np = ("Module", "numpy")
