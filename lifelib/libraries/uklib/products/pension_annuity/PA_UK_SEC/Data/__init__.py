# modelx: pseudo-python
# This file is part of a modelx model.
# It can be imported as a Python module, but functions defined herein
# are model formulas and may not be executable as standard Python.

"""Input data shared by every by-contract projection.

The two input CSVs are read here, **once per model**, and referenced from
:mod:`~.PA_UK_SEC.Projection` as ``data``. :mod:`~.PA_UK_SEC.Projection` is parameterized
by ``point_id``, so each ``Projection[N]`` is a separate ItemSpace with its own cells
cache; if the readers lived there, every model point would re-read every file. Holding
them in an unparameterized Space reads each file once no matter how many contracts are
projected.

Inputs are **external files**: plain CSVs in the model folder's parent directory,
``products/pension_annuity/``, rather than data stored inside the model. The model
folder therefore holds nothing but formulas — no ``_data/``, no IOSpec, no embedded
values — so a diff of the model shows logic changes only. This follows
``annuallife.TradLife_A``; contrast ``basiclife.BasicTerm_S``, which keeps its inputs
*inside* the model through modelx's IOSpec machinery.

The consequence worth knowing: **the model is not portable on its own.** Copying the
``PA_UK_SEC`` folder without its parent's CSVs produces a model that reads and then fails
on first evaluation.

**The mortality table is PA_UK_S's.** It is the file :mod:`~.PA_UK_S` reads, read here in
place: one copy serves both models, so an edit to it reaches both. The model point table,
``model_point_table_sec.csv``, is this model's own, and sits beside :mod:`~.PA_UK_S`'s
``model_point_table.csv``, which this model never opens.

:func:`input_dir` resolves the directory from ``_model.path.parent`` at run time, so
the model works wherever the repository is checked out. Each table has a filename
Reference and a reader Cells:

======================  ==========================  ==============================
Reference               Cells                       File
======================  ==========================  ==============================
model_point_file        model_point_table()         model_point_table_sec.csv
mort_table_file         mort_table()                mort_table.csv
======================  ==========================  ==============================

**The model point table is checked as it is read.** Eight of its columns are the in-force
interface: ``policy_count`` and ``duration_mth``, as in ``basiclife.BasicTerm_SE``, and the
six of a contract's opening state, each covered life's survival, the payments made to
date, and on RPI-linked escalation the income of the year under way, the ratchet's peak
and the annuitant's payments to date. :func:`model_point_table` refuses a table that lacks
one, repeats a ``point_id``, holds a count, a duration or a state no contract can have, or
an annuity to start more than ``future_horizon_mth`` months after the valuation date, 120
as shipped: future new business is written over a stated horizon, so that no frame runs
longer than the stop rule from the start date plus that horizon. Set to 0, the Reference
refuses future new business altogether. It refuses, too, what :mod:`~.PA_UK_S` projects
without a word: a flag that is not True or False, which :mod:`~.PA_UK_S` reads through
``bool`` so that a blank is True; an age, a guarantee, a frequency, a start year or a
month of death that is not a whole number, which :mod:`~.PA_UK_S` truncates with ``int``;
a month of death below 0, which :mod:`~.PA_UK_S` reads as a life that never dies; a code
that names no sex; and an amount, a rating, a percentage or a rate that is not a number in
its range. The checks run in turn, and the first that fails raises, naming the missing
column or every point that fails it. Whether a contract is short of its stop rule, issued
at an age the contract allows, and still owes a payment at the valuation date, are rules of
the product, and ``Projection.proj_len`` checks them, against its own References. A text
column :mod:`~.PA_UK_S` validates as it reads it, ``timing``, ``escalation_type``,
``vp_basis`` and ``mort_basis``, is refused by ``Projection``'s decode of it, with
:mod:`~.PA_UK_S`'s message.

**The mortality table is checked before a value of it is read.** Its keys are read by
their value, so an age written ``65.0`` is age 65, and a key that is not whole, text among
them, is refused; so are keys that repeat or leave a gap the projection would read. A rate
that is blank, text, infinite or outside 0 to 1 is refused, whether or not a point reads
it: ``Projection.mort_rate`` caps the annual rate with ``min``, which keeps its first
argument unless a later one compares smaller, and no comparison with NaN holds, so the cap
is written with its bound second and a NaN would stay NaN; but an infinity is a number,
which the cap reads as 1, certain death. The check is in the cell the projection takes the
table's extent from, which it asks before it reads the table, :func:`mort_age_first`, and
each refusal names the table's lines, the header line 1: the check reads the file as it
stands, where :mod:`~.PA_UK_S`'s reader, :func:`mort_table`, sorts it, and with the order
would lose the lines. A read beyond the table's ages is refused by the one ``Projection``
cell that reads it, naming the point, where :mod:`~.PA_UK_S`'s lookup raised ``KeyError``.

There are only two files because this product has almost nothing to parameterize: no
lapse table, no charge scale, no bonus rates, no surrender-value schedule. Everything
else is either a contractual rule in the formulas or a single Reference on
``Projection``.

Substituting a licensed basis means replacing ``mort_table.csv`` with a same-schema
file — the SAPS S3/S4 pensioner tables or the PMA16/PFA16 insured-annuitant family,
both restricted to CMI Authorised Users — and setting ``Projection.annuitant_adj`` to 1
so the population-proxy adjustment stops being applied on top of an annuitant table.
No formula changes. Replacing the file changes :mod:`~.PA_UK_S` too, which reads the same
one.
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

    Indexed by ``point_id``.  Eight columns are the in-force interface: ``policy_count``,
    the contracts the point stands for, and ``duration_mth``, the months elapsed from the
    annuity start date at the valuation date, as in ``basiclife.BasicTerm_SE``; then the
    opening state, per contract, as it stands at the start of month 0, before any month-0
    event:

    * ``lives_if_init_1`` and ``lives_if_init_2``: each covered life's probability of
      being alive at the valuation date, 1 or 0 on a real record, where a joint contract
      may carry one life already dead, and 0 for the second life of a single-life
      contract;
    * ``cum_annuity_all_init``: the instalments paid before the valuation date on every
      stream, per contract;
    * ``annual_income_init``, read on RPI-linked escalation, ``lpi5`` or ``rpi_catchup``:
      the annualized income of the policy year under way, before any month-0 anniversary;
    * ``rpi_peak_init``, read on ``rpi_catchup``: the ratchet's running peak of the
      reference index over the latest index;
    * ``cum_annuity_pp_init``, read on RPI-linked escalation with value protection on the
      first death: the annuitant's as-if-alive instalments before the valuation date.

    The last three are blank on a point that does not read them.  The rest are
    :mod:`~.PA_UK_S`'s, ``pols_if_init`` renamed ``policy_count``, except ``row_kind``,
    ``source_policy_id`` and ``source_mth``, which record where the generator took each
    shipped row from and which no formula reads.

    The checks run over the whole table at once, and the first that fails raises
    ``ValueError``, naming the missing column or every point it fails on:

    1. the eight in-force columns are present;
    2. no ``point_id`` appears twice;
    3. ``policy_count`` is a number, zero or more;
    4. ``duration_mth`` is a whole number of months, below ``2**53`` in size, which numpy
       would otherwise cast to the least int64 without a word: positive for a contract in
       payment, 0 for one starting at the valuation date, negative for one starting later;
    5. ``future_horizon_mth`` is a whole number of months, 0 or more, and no annuity starts
       more than that many months after the valuation date, so ``duration_mth`` is
       ``-future_horizon_mth`` or more.  At 0 the model takes no future new business, and
       the message says so;
    6. ``dependant_present``, ``overlap`` and ``proportion`` are True or False.  pandas
       reads a column of them as booleans, but one blank or one other text leaves the whole
       column text or mixed, and :mod:`~.PA_UK_S`'s ``bool`` reads a blank, NaN, as True;
    7. the annuitant's columns: ``annuitant_age`` a whole number below ``2**53``, which
       :mod:`~.PA_UK_S` truncates with ``int``; ``annuitant_sex`` M or F, the table's key;
       ``rating_multiplier`` a finite number, 1 or more, the notes' ``theta >= 1``;
    8. the contract's: ``purchase_price`` and ``annual_income`` amounts, finite numbers, 0
       or more; ``frequency`` 12, 4, 2 or 1, read by its value, which :mod:`~.PA_UK_S`
       truncates with ``int`` before it checks it; ``guarantee_months`` a whole number of
       months, 0 or more, below ``2**53``; ``vp_pct`` a number from 0 to 1, a share of the
       purchase price; and ``start_year`` a whole number below ``2**53``, a calendar year;
    9. on a contract with a dependant, the dependant's: ``dependant_age`` a whole number
       below ``2**53``, ``dependant_sex`` M or F, ``dependant_rating`` a finite number, 1
       or more, and ``dependant_pct`` a number from 0 to 1, a share of the income.  A
       single-life contract's are never read, and are left;
    10. on fixed escalation, ``escalation_rate`` a finite number, 0 or more: the notes'
        menu is non-decreasing, which the dependant's base relies on;
    11. on the scenario basis, each covered life's month of death, ``death_mth_1`` and
        ``death_mth_2``, is blank, the life surviving the projection, or a whole number of
        months, 0 or more, below ``2**53``, read by value, so that ``16.0`` is 16.  The
        table is returned with the two columns as the numbers they were checked as, which
        is what ``Projection.death_mth`` reads;
    12. ``lives_if_init_1`` and ``lives_if_init_2`` are probabilities, 0 to 1, and
        ``lives_if_init_2`` is 0 on a single-life contract, which covers no second life;
    13. ``cum_annuity_all_init`` is a finite number, 0 or more; on RPI-linked escalation
        ``annual_income_init`` too; on ``rpi_catchup`` ``rpi_peak_init`` is a finite
        number, 1 or more, the peak being at least the latest index; and on RPI-linked
        escalation with value protection on the first death ``cum_annuity_pp_init`` is a
        finite number, 0 or more;
    14. a contract not yet in payment, ``duration_mth`` 0 or less, holds its values at the
        start date: each covered life alive, nothing paid, the first year's income,
        ``annual_income``, and a peak of 1;
    15. a contract in its first policy year, ``duration_mth`` 1 to 12, has passed no
        anniversary before month 0: on RPI-linked escalation its income of the year under
        way is the first year's, and on ``rpi_catchup`` its peak is 1.  Beyond the first
        year the history is the contract's own, and no rule holds one column to another;
    16. on the scenario basis, each covered life's opening status is its death month's:
        1 while the life survives to the valuation date, ``death_mth`` blank or
        ``duration_mth`` or later, and 0 once it has died.  So the scenario's step
        function, which ``lives_if`` follows after the valuation date, agrees with the
        opening value at it.
    """
    name = model_point_file                                          # noqa: F821
    table = pd.read_csv(input_dir() / name, index_col="point_id")    # noqa: F821
    state = ("lives_if_init_1", "lives_if_init_2", "cum_annuity_all_init",
             "annual_income_init", "rpi_peak_init", "cum_annuity_pp_init")
    for column in ("policy_count", "duration_mth", *state):
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
        raise ValueError(f"future_horizon_mth must be a whole number of months, 0 or "
                         f"more, not {float(horizon)}")
    bad = table.index[months < -horizon].tolist()
    if bad and horizon == 0:
        raise ValueError(f"{name}: duration_mth must be 0 or more: this model takes no "
                         f"future new business; it is not at point_id {bad}")
    if bad:
        raise ValueError(f"{name}: duration_mth must be -{int(horizon)} or more, an "
                         f"annuity starting at most {int(horizon)} months after the "
                         f"valuation date; it is not at point_id {bad}")
    for column in ("dependant_present", "overlap", "proportion"):
        flag = table[column]
        bad = table.index[~flag.map(lambda v: str(v).lower() in ("true", "false"))].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be True or False; it is not at "
                             f"point_id {bad}")
    joint = table["dependant_present"].map(lambda v: str(v).lower() == "true")
    rules = {"whole": ("a whole number below 2**53",
                       lambda v: (v % 1 == 0) & (v.abs() < 2.0 ** 53)),
             "months": ("a whole number of months, 0 or more, below 2**53",
                        lambda v: (v >= 0) & (v % 1 == 0) & (v < 2.0 ** 53)),
             "amount": ("a finite number, 0 or more",
                        lambda v: (v >= 0) & (v < float("inf"))),
             "rating": ("a finite number, 1 or more",
                        lambda v: (v >= 1) & (v < float("inf"))),
             "share": ("a number from 0 to 1", lambda v: (v >= 0) & (v <= 1)),
             "frequency": ("12, 4, 2 or 1", lambda v: v.isin([12, 4, 2, 1]))}
    everyone = pd.Series(True, index=table.index)                    # noqa: F821
    escalation = table["escalation_type"]
    for column, kind, where, on in (
            ("annuitant_age", "whole", everyone, ""),
            ("annuitant_sex", None, everyone, ""),
            ("rating_multiplier", "rating", everyone, ""),
            ("purchase_price", "amount", everyone, ""),
            ("annual_income", "amount", everyone, ""),
            ("frequency", "frequency", everyone, ""),
            ("guarantee_months", "months", everyone, ""),
            ("vp_pct", "share", everyone, ""),
            ("start_year", "whole", everyone, ""),
            ("dependant_age", "whole", joint, " on a contract with a dependant"),
            ("dependant_sex", None, joint, " on a contract with a dependant"),
            ("dependant_rating", "rating", joint, " on a contract with a dependant"),
            ("dependant_pct", "share", joint, " on a contract with a dependant"),
            ("escalation_rate", "amount", escalation == "fixed",
             " on fixed escalation")):
        if kind is None:
            rule, holds = "M or F", table[column].isin(["M", "F"])
        else:
            rule, test = rules[kind]
            holds = test(pd.to_numeric(table[column], errors="coerce"))  # noqa: F821
        bad = table.index[where & ~holds].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be {rule}{on}; it is not at "
                             f"point_id {bad}")
    scenario = table["mort_basis"] == "scenario"
    deaths = {}
    for life, covered in ((1, everyone), (2, joint)):
        column = f"death_mth_{life}"
        death = pd.to_numeric(table[column], errors="coerce")        # noqa: F821
        whole = (death >= 0) & (death % 1 == 0) & (death < 2.0 ** 53)
        bad = table.index[scenario & covered & ~(table[column].isna() | whole)].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be blank or a whole number of "
                             f"months, 0 or more, a policy month, on the scenario basis; "
                             f"it is not at point_id {bad}")
        deaths[life] = death
    values = {c: pd.to_numeric(table[c], errors="coerce") for c in state}  # noqa: F821
    for column in ("lives_if_init_1", "lives_if_init_2"):
        v = values[column]
        bad = table.index[~((v >= 0) & (v <= 1))].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be a probability, 0 to 1; it is "
                             f"not at point_id {bad}")
    bad = table.index[~joint & (values["lives_if_init_2"] != 0)].tolist()
    if bad:
        raise ValueError(f"{name}: lives_if_init_2 must be 0 on a single-life contract, "
                         f"which covers no second life; it is not at point_id {bad}")
    linked = escalation.isin(["lpi5", "rpi_catchup"])
    catchup = escalation == "rpi_catchup"
    first_death = (pd.to_numeric(table["vp_pct"], errors="coerce") > 0) & (  # noqa: F821
        table["vp_basis"] == "first_death")
    for column, kind, where, on in (
            ("cum_annuity_all_init", "amount", everyone, ""),
            ("annual_income_init", "amount", linked,
             " on RPI-linked escalation, lpi5 or rpi_catchup"),
            ("rpi_peak_init", "rating", catchup, " on rpi_catchup escalation"),
            ("cum_annuity_pp_init", "amount", linked & first_death,
             " on RPI-linked escalation with value protection on the first death")):
        rule, test = rules[kind]
        bad = table.index[where & ~test(values[column])].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be {rule}{on}; it is not at "
                             f"point_id {bad}")
    income = pd.to_numeric(table["annual_income"], errors="coerce")  # noqa: F821
    issued = months <= 0
    for column, want, where in (
            ("lives_if_init_1", 1.0, everyone),
            ("lives_if_init_2", joint.astype(float), everyone),
            ("cum_annuity_all_init", 0.0, everyone),
            ("annual_income_init", income, linked),
            ("rpi_peak_init", 1.0, catchup),
            ("cum_annuity_pp_init", 0.0, linked & first_death)):
        bad = table.index[issued & where & (values[column] != want)].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must hold its value at the start date on "
                             f"a contract not yet in payment, duration_mth 0 or less: each "
                             f"covered life alive, nothing paid, the first year's income "
                             f"and a peak of 1; it does not at point_id {bad}")
    first_year = (months > 0) & (months <= 12)
    for column, want, where in (("annual_income_init", income, linked),
                                ("rpi_peak_init", 1.0, catchup)):
        bad = table.index[first_year & where & (values[column] != want)].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must hold its first year's value on a "
                             f"contract in its first policy year, duration_mth 1 to 12, "
                             f"before which no anniversary has passed: the first year's "
                             f"income and a peak of 1; it does not at point_id {bad}")
    for life, covered in ((1, everyone), (2, joint)):
        death = deaths[life]
        alive = death.isna() | (death >= months)
        want = alive.astype(float).where(covered, 0.0)
        column = f"lives_if_init_{life}"
        bad = table.index[scenario & (values[column] != want)].tolist()
        if bad:
            raise ValueError(f"{name}: on the scenario basis {column} must be 1 while "
                             f"the life survives to the valuation date, death_mth_{life} "
                             f"blank or duration_mth or later, and 0 once it has died; "
                             f"it is not at point_id {bad}")
    return table.assign(death_mth_1=deaths[1], death_mth_2=deaths[2])


def mort_table():
    """The base annual mortality rates by sex and age, from *mort_table.csv*.

    A **[std]** proxy shaped like the ONS UK national life tables, which are period
    tables of *population* mortality and the only freely redistributable UK source.  It
    is **not** an annuitant table: the proper bases are the SAPS S3/S4 pensioner tables
    and the PMA16/PFA16 insured-annuitant family, both restricted to CMI Authorised
    Users.  ``Projection.annuitant_adj`` carries the population-to-annuitant adjustment
    that stands in for the difference, and it is a shape-level placeholder rather than a
    calibration.  Sorted on read, because ``Projection.mort_rate_base_at`` indexes into
    it.  :mod:`~.PA_UK_S`'s reader, indexed and sorted as it is, from the one read of the
    file, :func:`mort_table_rows`; :func:`mort_age_first` checks the table.
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

    ``Projection.mort_rate_base_at`` asks it, and :func:`mort_age_last`, before it reads
    the table, so a table it cannot read is refused before any value of it is; so does
    ``Projection.proj_len`` on the table basis, through :func:`mort_age_last`.  The check
    reads the file as it stands, :func:`mort_table_rows`, not :func:`mort_table`, which
    sorts it, so that each refusal names the lines at fault, the header line 1.  The rules,
    each over the whole table, the first that fails raising ``ValueError``:

    1. each age is a whole number, read by its value, so ``65.0`` is 65;
    2. each sex is M or F, the codes the model point table holds;
    3. each sex runs over the table's ages from the first to the last, one row an age,
       none below 0: the projection reads a rate at each attained age a life reaches.
       Every fault is named in one message: an age below 0 and an age a sex repeats each
       with its lines, and each span of ages a sex lacks;
    4. each ``mort_rate`` is a number from 0 to 1, a probability, read by the cap.
    """
    name = mort_table_file                                           # noqa: F821
    tbl = mort_table_rows()
    lines = tbl.index + 2
    ages = pd.to_numeric(tbl["age"], errors="coerce")                # noqa: F821
    bad = lines[(~(ages % 1 == 0)).to_numpy()].tolist()
    if bad:
        raise ValueError(f"{name}: age must be a whole number; it is not on line {bad}")
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
    ages = pd.to_numeric(mort_table().reset_index()["age"], errors="coerce")  # noqa: F821
    return int(ages.max())


# ---------------------------------------------------------------------------
# References

model_point_file = "model_point_table_sec.csv"

mort_table_file = "mort_table.csv"

future_horizon_mth = 120

pd = ("Module", "pandas")
