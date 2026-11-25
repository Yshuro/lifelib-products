# modelx: pseudo-python
# This file is part of a modelx model.
# It can be imported as a Python module, but functions defined herein
# are model formulas and may not be executable as standard Python.

"""Input data shared by every by-policy projection.

The three input CSVs are read here, **once per model**, and referenced from
:mod:`~.WOL_UK_SEC.Projection` as ``data``. :mod:`~.WOL_UK_SEC.Projection` is parameterized
by ``idx``, the position of a model point in the table, so each ``Projection[i]`` is a
separate ItemSpace with its own cells cache; if the readers lived there, every model point
would re-read every file. Holding them in an unparameterized Space reads each file once no
matter how many policies are projected.

Inputs are **external files**: plain CSVs in the model folder's parent directory,
``products/whole_of_life/``, rather than data stored inside the model. The model folder
therefore holds nothing but formulas — no ``_data/``, no IOSpec, no embedded values —
so a diff of the model shows logic changes only. This follows ``annuallife.TradLife_A``;
contrast ``basiclife.BasicTerm_S``, which keeps its inputs *inside* the model through
modelx's IOSpec machinery.

The consequence worth knowing: **the model is not portable on its own.** Copying the
``WOL_UK_SEC`` folder without its parent's CSVs produces a model that reads and then
fails on first evaluation.

**Two of the tables are WOL_UK_S's.** The mortality and lapse tables are the files
:mod:`~.WOL_UK_S` reads, read here in place by :mod:`~.WOL_UK_S`'s own readers: one copy of
each table serves both models, so an edit to one reaches both. The model point table,
``model_point_table_sec.csv``, is this model's own, and sits beside :mod:`~.WOL_UK_S`'s
``model_point_table.csv``, which this model never opens.

:func:`input_dir` resolves the directory from ``_model.path.parent`` at run time, so
the model works wherever the repository is checked out. Each table has a filename
Reference and a reader Cells:

======================  ==========================  ==============================
Reference               Cells                       File
======================  ==========================  ==============================
model_point_file        model_point_table()         model_point_table_sec.csv
mort_table_file         mort_table()                mort_table.csv
lapse_table_file        lapse_table()               lapse_table.csv
======================  ==========================  ==============================

Both the mortality and the lapse table are keyed by the **cell** as well as by the usual
rating factors, because the two cells of this product do not share a basis and must not
be given each other's. The underwritten cell restores select experience through full
underwriting and takes an assured-lives shape; the guaranteed-acceptance cell cannot be
better than the population and self-selects worse, so it takes a population shape with an
anti-selection loading. The FCA's price differential between the two designs — £71.73
against £8.10 per £1,000 of cover — is the scale of the error a basis mix-up produces.

**The model point table is checked as it is read.** Eight of its columns are the in-force
interface: ``policy_count`` and ``duration_mth``, as in ``basiclife.BasicTerm_SE``, and
the opening state of a point in force, the paid-up strand's ``pols_pu_init`` and
``pu_benefit_pp_init``, the premiums paid, ``prem_cum_pp_init``, the cover and premium
before month 0's events, ``cover_pp_init`` and ``premium_pp_init``, and the crossover, if
it fell before the valuation date, ``crossover_mth_init``.
:func:`model_point_table` refuses a table that lacks one, repeats a ``point_id``, holds a
count, a duration or a state no policy can have, or a policy to be issued more than
``future_horizon_mth`` months after the valuation date, 120 as shipped: future new
business is written over a stated horizon, so that no frame runs longer than cover from
issue plus that horizon. Set to 0, the Reference refuses future new business altogether.
It refuses, too, what :mod:`~.WOL_UK_S` projects without a word or meets only when a
projection reaches it: a flag that is not True or False, a code that names no cell,
escalation, sex or smoker status, an age, an amount or a month count that is not a number
in its range, the pro-rata paid-up variant without a premium cessation date, and a history
the contract cannot have given. The checks run in turn, and the first that fails raises,
naming the missing column or every point that fails it. Whether a point is still short of
the limiting age at the valuation date, and whether the contract issues it, are rules of
the product, and ``Projection.proj_len`` checks them, against its own References.

**Each assumption table is checked before a value of it is read.** Its keys are read by
their value, so an age written ``70.0`` is age 70, and a key that is not whole, text among
them, or is ``2**53`` or more in size, which int64 would hold inexactly, is refused; so are
keys that repeat or leave a gap the projection would read. A
value that is blank, text, infinite or outside its range is refused, whether or not a
point reads it: ``Projection.mort_rate`` caps the annual rate with ``min``, which keeps
its first argument unless a later one compares smaller, and no comparison with NaN
holds, so the cap is written with its bound second and a NaN would stay NaN; but an
infinity is a number, which the cap reads as 1, certain death. The check of each table is
in the cell the projection takes the table's extent from, which it asks before it reads
the table: :func:`mort_age_first` and :func:`mort_age_last` for the mortality table, and
:func:`lapse_last_year` for the lapse table. Each refusal names the table's lines, the
header line 1: the check reads the file as it stands, :func:`mort_table_rows` and
:func:`lapse_table_rows`, where :mod:`~.WOL_UK_S`'s readers, :func:`mort_table` and
:func:`lapse_table`, sort the tables, and with the order would lose the lines. A read
beyond the mortality table's ages is refused by the one ``Projection`` cell that reads it,
naming the point, where :mod:`~.WOL_UK_S`'s lookup raised ``KeyError``.

**The vectors.** The readers return what the files hold, and no
:mod:`~.WOL_UK_SEC.Projection` cell but ``model_point``, a reporting cell, reads them.
The others read the arrays below instead, one element at a time, a model point's
attribute being the element at its position, ``data.sum_assured()[idx]``. That is what
lets the model compile to C, as ``basiclife.BasicTerm_SC`` does: each array is a numpy
vector or table of int64 or float64, which compiles to a typed memoryview, never one of
bools, objects or text, and each extent of a table is an int.

Text the projection needs is decoded here, into the number it selects, for every point at
once, as :mod:`~.WOL_UK_S` reads each value: the cell into its code, O50 0 and UW 1,
``Projection``'s References ``O50`` and ``UW``, which is the cell's row of the lapse table,
and stays a code because the loadings, the expenses and the benefit rules it selects are
``Projection``'s References and rules, which this Space cannot read; the escalation into
its code, level 0, fixed_5pct 1 and rpi 2, ``Projection``'s ``LEVEL``, ``FIXED_5PCT`` and
``RPI``, a code for the same reason, the steps it selects being ``Projection``'s
References; the basis the cell takes, the sex and the smoker status into the point's row
of the mortality table, its schedule; and each variant's True or False into a 0/1 flag.
And each table keyed by more than a number becomes an integer-indexed array. The
mortality table, keyed by basis, sex, smoker status and age, is tabled by its eight
schedules, numbered as :func:`mort_age_first` runs over them, population before assured,
M before F and NS before S, and padded from age 0, so that the index is the attained age;
the lapse table, keyed by cell and policy year, is tabled by the cell's code and padded at
year 0, beside each cell's last year:

==============================  =======  ================  =================================
Cells                           dtype    Shape             From
==============================  =======  ================  =================================
point_id()                      int64    [point]           the table's index
entry_age()                     int64    [point]           ``entry_age``
cell_code()                     int64    [point]           ``cell``, decoded: O50 0, UW 1
escalation_code()               int64    [point]           ``escalation``, decoded: level 0,
                                                           fixed_5pct 1, rpi 2
mort_schedule()                 int64    [point]           ``cell``, ``sex`` and ``smoker``,
                                                           decoded: 4 x basis + 2 x sex +
                                                           smoker
sum_assured()                   float64  [point]           ``sum_assured``
premium_mth()                   float64  [point]           ``premium_mth``
cessation_months()              int64    [point]           ``cessation_months``
moratorium_months()             int64    [point]           ``moratorium_months``
variant_adb_2x()                int64    [point]           ``variant_adb_2x``, 0/1
variant_paid_up()               int64    [point]           ``variant_paid_up``, 0/1
policy_count()                  float64  [point]           ``policy_count``
duration_mth()                  int64    [point]           ``duration_mth``
pols_pu_init()                  float64  [point]           ``pols_pu_init``
pu_benefit_pp_init()            float64  [point]           ``pu_benefit_pp_init``
prem_cum_pp_init()              float64  [point]           ``prem_cum_pp_init``
cover_pp_init()                 float64  [point]           ``cover_pp_init``
premium_pp_init()               float64  [point]           ``premium_pp_init``
crossover_mth_init()            int64    [point]           ``crossover_mth_init``
mort_age_first()                int      scalar            *mort_table.csv*, checked
mort_age_last()                 int      scalar            *mort_table.csv*
mort_table_array()              float64  [schedule, age]   *mort_table.csv*
lapse_last_year()               int64    [cell]            *lapse_table.csv*, checked
lapse_table_array()             float64  [cell, year]      *lapse_table.csv*
==============================  =======  ================  =================================

**An array is read by element, never whole,** in this Space as in
:mod:`~.WOL_UK_SEC.Projection`. The compiler types an array cell as a memoryview only
once it has seen that every use of it, in either Space, is an element read: one
``len()``, slice, loop over it or numpy call on it anywhere, and the cell compiles as a
Python object. So an array derived here reads the table's column, never another cell's
array, and a width comes from a table.

**What cannot be held is refused** when the table is first read, naming every point or
line at fault, beside the checks above: a ``point_id`` that is not a whole number below
``2**53`` in size, when :func:`point_id` is first read, as a refusal reads it; an
``entry_age`` that is not below ``2**53`` in size, by :func:`model_point_table` itself;
and a mortality age or a lapse policy year ``2**53`` or more in size, by the table's
check, each of which numpy would otherwise cast to int64 inexactly, or to the least
int64, without a word. A fraction of a year of age truncates, as :mod:`~.WOL_UK_S`'s
``int`` truncates it.
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
    :mod:`~.WOL_UK_S`'s, but ``pols_if_init``, which ``policy_count`` replaces, and
    ``row_kind``, ``source_policy_id``, ``source_mth`` and ``source_refs``, which record
    where the generator took each shipped row from, and under what References, and which
    no formula reads.

    The checks run over the whole table at once, and the first that fails raises
    ``ValueError``, naming the missing column or every point it fails on:

    1. the eight in-force columns are present;
    2. no ``point_id`` appears twice;
    3. ``policy_count`` is a number, zero or more: the policies on full cover;
    4. ``duration_mth`` is a whole number of months, below ``2**53`` in size, which numpy
       would otherwise cast to the least int64 without a word: positive for a policy in
       force, 0 for one issued at the valuation date, negative for one issued later;
    5. no policy is issued more than ``future_horizon_mth`` months after the valuation
       date, so ``duration_mth`` is ``-future_horizon_mth`` or more. At 0 the model takes
       no future new business, and the message says so; a horizon that is not a whole
       number of months, 0 or more, below ``2**53``, is itself refused, since a NaN one
       fails every comparison and so would admit every policy, and an infinite one bounds
       nothing;
    6. the opening state is a number, zero or more: ``pols_pu_init``, a count;
       ``pu_benefit_pp_init``, ``prem_cum_pp_init``, ``cover_pp_init`` and
       ``premium_pp_init``, amounts per policy; and ``crossover_mth_init`` a whole number
       of months, -1 or more, below ``2**53``;
    7. each of ``variant_adb_2x`` and ``variant_paid_up`` is True or False. pandas reads a
       column of them as booleans, but one blank or one other text leaves the whole
       column text or mixed, and ``bool("False")`` is True;
    8. ``cell`` is O50 or UW, ``escalation`` level, fixed_5pct or rpi, ``sex`` M or F and
       ``smoker`` NS or S, the codes the formulas branch on and the tables are keyed by;
    9. ``entry_age`` is a finite number, which :mod:`~.WOL_UK_S` reads with ``int``, below
       ``2**53`` in size, which numpy would otherwise cast to the least int64 without a
       word; ``sum_assured`` and ``premium_mth`` numbers, zero or more; and
       ``cessation_months`` and ``moratorium_months`` whole numbers of months, 0 or more,
       below ``2**53``;
    10. a point with the pro-rata paid-up variant has a premium cessation date,
        ``cessation_months`` above 0, which the paid-up value is measured to, and which
        :mod:`~.WOL_UK_S` asks for only when a projection reaches it;
    11. a policy not yet in force, ``duration_mth`` 0 or less, holds the issue values: no
        paid-up policy, no paid-up cover and no premium paid, the sum assured and the
        premium at issue as its cover and premium, and no crossover, ``-1``;
    12. a policy in force 12 months or fewer holds the sum assured and the premium at
        issue: the columns are measured before month 0's events, so on the first
        anniversary they are still the first year's, the increase it makes the
        projection's;
    13. on a level point the cover and the premium are the sum assured and the premium at
        issue, which never move; on an escalating one they are those or more, each
        increase being floored at 0;
    14. the paid-up strand, ``pols_pu_init`` and ``pu_benefit_pp_init``, is 0 on a point
        without the pro-rata paid-up variant, and before the earliest policy month a
        converted policy can be in force at, half of ``cessation_months``, rounded up:
        a would-be lapse converts once half the expected payments have been made, and a
        policy converted at the end of a month is paid-up from the start of the next;
    15. ``pu_benefit_pp_init``, an amount per paid-up policy, is 0 where no paid-up policy
        is in force;
    16. the premiums paid, ``prem_cum_pp_init``, are the premiums due so far,
        ``min(duration_mth, cessation_months)`` or ``duration_mth`` where premiums are
        payable for life, times the premium at issue on a level point, and on an
        escalating one between that and the same count times ``premium_pp_init``, the
        latest premium, each increase being floored at 0;
    17. where paid-up policies are in force, the paid-up cover per policy lies between the
        sum assured times the payments a conversion needs, half of ``cessation_months``
        rounded up, and ``cover_pp_init`` times the payments made, each over
        ``cessation_months``: each policy converted at ``SA(t) x N_paid / N_expected``,
        on a cover at least the sum assured and at most today's, having made at least half
        its payments and no more than have fallen due;
    18. a crossover before the valuation date, ``crossover_mth_init`` 0 or more, fell in a
        premium-paying policy month before it, below ``duration_mth`` and below
        ``cessation_months`` where premiums cease; there was one, ``crossover_mth_init``
        not -1, where the premiums paid exceed the cover; and on a level point it is the
        month the contract puts it in, the whole number of premiums the sum assured holds,
        ``P x t* <= SA < P x (t* + 1)``.

    Rules 16 to 18 hold each amount to the cent, within half a cent of its bound, so that
    an extract rounded to the cent reads.  Each rule of the history holds of every state
    :mod:`~.WOL_UK_S` reaches, under any References: the relations it states are the
    contract's.
    """
    name = model_point_file                                          # noqa: F821
    table = pd.read_csv(input_dir() / name, index_col="point_id")    # noqa: F821
    state_columns = ("pols_pu_init", "pu_benefit_pp_init", "prem_cum_pp_init",
                     "cover_pp_init", "premium_pp_init")
    for column in ("policy_count", "duration_mth", *state_columns, "crossover_mth_init"):
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
    for column in state_columns:
        v = pd.to_numeric(table[column], errors="coerce")            # noqa: F821
        bad = table.index[~((v >= 0) & (v < float("inf")))].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be a number, zero or more; it is not "
                             f"at point_id {bad}")
        state[column] = v
    crossover = pd.to_numeric(table["crossover_mth_init"], errors="coerce")  # noqa: F821
    bad = table.index[~((crossover >= -1) & (crossover % 1 == 0)
                        & (crossover < 2.0 ** 53))].tolist()
    if bad:
        raise ValueError(f"{name}: crossover_mth_init must be a whole number of months, -1 "
                         f"or more, below 2**53; it is not at point_id {bad}")
    flags = {}
    for column in ("variant_adb_2x", "variant_paid_up"):
        flag = table[column]
        bad = table.index[~flag.map(lambda v: str(v).lower() in ("true", "false"))].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be True or False; it is not at "
                             f"point_id {bad}")
        flags[column] = flag.map(lambda v: str(v).lower() == "true")
    for column, codes in (("cell", ("O50", "UW")),
                          ("escalation", ("level", "fixed_5pct", "rpi")),
                          ("sex", ("M", "F")), ("smoker", ("NS", "S"))):
        bad = table.index[~table[column].isin(codes)].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be {' or '.join(codes)}; it is not "
                             f"at point_id {bad}")
    rules = {"finite": ("a finite number",
                        lambda v: (v > -float("inf")) & (v < float("inf"))),
             "amount": ("a number, zero or more",
                        lambda v: (v >= 0) & (v < float("inf"))),
             "months": ("a whole number of months, 0 or more, below 2**53",
                        lambda v: (v >= 0) & (v % 1 == 0) & (v < 2.0 ** 53))}
    numbers = {}
    for column, kind in (("entry_age", "finite"), ("sum_assured", "amount"),
                         ("premium_mth", "amount"), ("cessation_months", "months"),
                         ("moratorium_months", "months")):
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
        numbers[column] = v
    paid_up = flags["variant_paid_up"]
    cessation = numbers["cessation_months"]
    bad = table.index[paid_up & (cessation <= 0)].tolist()
    if bad:
        raise ValueError(f"{name}: a pro-rata paid-up point must have a premium cessation "
                         f"date, cessation_months above 0, which the paid-up value is "
                         f"measured to; it is not at point_id {bad}")
    issue = {"pols_pu_init": 0.0, "pu_benefit_pp_init": 0.0, "prem_cum_pp_init": 0.0,
             "cover_pp_init": numbers["sum_assured"],
             "premium_pp_init": numbers["premium_mth"]}
    at_issue = {"cover_pp_init": "the sum assured", "premium_pp_init": "the premium at issue"}
    for column in state_columns:
        bad = table.index[(months <= 0) & (state[column] != issue[column])].tolist()
        if bad:
            what = at_issue.get(column, "0")
            raise ValueError(f"{name}: {column} must be {what} on a policy not yet in "
                             f"force, duration_mth 0 or less; it is not at point_id {bad}")
    bad = table.index[(months <= 0) & (crossover != -1)].tolist()
    if bad:
        raise ValueError(f"{name}: crossover_mth_init must be -1 on a policy not yet in "
                         f"force, duration_mth 0 or less; it is not at point_id {bad}")
    for column in ("cover_pp_init", "premium_pp_init"):
        bad = table.index[(months > 0) & (months <= 12)
                          & (state[column] != issue[column])].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be {at_issue[column]} on a policy in "
                             f"force 12 months or fewer, whose columns are its first "
                             f"policy year's, the first anniversary's increase being the "
                             f"projection's; it is not at point_id {bad}")
    level = table["escalation"] == "level"
    for column in ("cover_pp_init", "premium_pp_init"):
        bad = table.index[level & (state[column] != issue[column])].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be {at_issue[column]} on a level "
                             f"point, which never escalates; it is not at point_id {bad}")
        bad = table.index[~level & ~(state[column] >= issue[column])].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be {at_issue[column]} or more on an "
                             f"escalating point, each increase being floored at 0; it is "
                             f"not at point_id {bad}")
    for column in ("pols_pu_init", "pu_benefit_pp_init"):
        bad = table.index[~paid_up & (state[column] != 0)].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be 0 on a point without the pro-rata "
                             f"paid-up variant; it is not at point_id {bad}")
        bad = table.index[(months < -(-cessation // 2)) & (state[column] != 0)].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be 0 before the first policy month a "
                             f"converted policy can be in force at, half of "
                             f"cessation_months, rounded up; it is not at point_id {bad}")
    bad = table.index[(state["pols_pu_init"] == 0)
                      & (state["pu_benefit_pp_init"] != 0)].tolist()
    if bad:
        raise ValueError(f"{name}: pu_benefit_pp_init must be 0 where no paid-up policy is "
                         f"in force, pols_pu_init 0; it is not at point_id {bad}")
    cent = 0.005
    in_force = months > 0
    due = months.where((cessation <= 0) | (months <= cessation), cessation)
    premium, sa = numbers["premium_mth"], numbers["sum_assured"]
    paid = state["prem_cum_pp_init"]
    low = premium * due
    bad = table.index[in_force & level & ~((paid >= low - cent)
                                           & (paid <= low + cent))].tolist()
    if bad:
        raise ValueError(f"{name}: prem_cum_pp_init must be premium_mth times the premiums "
                         f"due, min(duration_mth, cessation_months), to the cent, on a "
                         f"level point; it is not at point_id {bad}")
    high = state["premium_pp_init"] * due
    bad = table.index[in_force & ~level & ~((paid >= low - cent)
                                            & (paid <= high + cent))].tolist()
    if bad:
        raise ValueError(f"{name}: prem_cum_pp_init must lie between premium_mth and "
                         f"premium_pp_init times the premiums due, min(duration_mth, "
                         f"cessation_months), to the cent, on an escalating point; it is not "
                         f"at point_id {bad}")
    cover_pu = state["pu_benefit_pp_init"]
    pu_low = sa * (-(-cessation // 2)) / cessation
    pu_high = state["cover_pp_init"] * due / cessation
    bad = table.index[(state["pols_pu_init"] > 0)
                      & ~((cover_pu >= pu_low - cent) & (cover_pu <= pu_high + cent))].tolist()
    if bad:
        raise ValueError(f"{name}: pu_benefit_pp_init must lie between sum_assured times "
                         f"the payments a conversion needs, half of cessation_months rounded "
                         f"up, and cover_pp_init times the payments made, min(duration_mth, "
                         f"cessation_months), each over cessation_months, to the cent, where "
                         f"paid-up policies are in force; it is not at point_id {bad}")
    last = cessation.where(cessation > 0, months)
    bad = table.index[in_force & (crossover >= 0)
                      & ~((crossover < months) & (crossover < last))].tolist()
    if bad:
        raise ValueError(f"{name}: crossover_mth_init must be -1, or a premium-paying policy "
                         f"month before the valuation date, below duration_mth and "
                         f"cessation_months; it is not at point_id {bad}")
    bad = table.index[in_force & (crossover == -1)
                      & (paid > state["cover_pp_init"] + cent)].tolist()
    if bad:
        raise ValueError(f"{name}: crossover_mth_init must not be -1 where the premiums paid "
                         f"exceed the cover, prem_cum_pp_init above cover_pp_init, to the "
                         f"cent: they crossed it before the valuation date; it is not at "
                         f"point_id {bad}")
    bad = table.index[in_force & level & (crossover >= 0)
                      & ~((premium * crossover <= sa + cent)
                          & (premium * (crossover + 1) > sa - cent))].tolist()
    if bad:
        raise ValueError(f"{name}: crossover_mth_init must be the month the contract puts the "
                         f"crossover in on a level point, the whole number of premiums the sum "
                         f"assured holds, to the cent; it is not at point_id {bad}")
    return table


def mort_table():
    """The annual mortality rates, read from *mort_table.csv*.

    Keyed by basis (``population`` or ``assured``), sex, smoker status and age last
    birthday, and capped at 1.  Both bases are **[std]** proxies: the ``population``
    rates are shaped like the ONS national life tables and anchored so that the O50
    cell's loaded rate is the notes' walk-through basis exactly, and the ``assured``
    rates are shaped like the "00" Series permanent assurance tables.  Neither is a
    published table, and the file's ``provenance`` column says which cells are anchors
    and which come from a sex or smoker factor.  Sorted on read, because
    ``Projection.mort_rate`` indexes into it.  :mod:`~.WOL_UK_S`'s reader, indexed and
    sorted as it is, from the one read of the file, :func:`mort_table_rows`;
    :func:`mort_age_first` checks the table.
    """
    return mort_table_rows().set_index(["basis", "sex", "smoker", "age"]).sort_index()


def mort_table_rows():
    """*mort_table.csv* as the file holds it: one row a line, in the file's order.

    The one read of the file.  :func:`mort_age_first` checks it here, so that each refusal
    names the lines at fault, the header line 1, which the sort of :func:`mort_table`, the
    reader the projection indexes into, would lose.
    """
    return pd.read_csv(input_dir() / mort_table_file)                # noqa: F821


def lapse_table():
    """The annual lapse rates by cell and policy year, from *lapse_table.csv*.

    ``policy_year`` is the contractual 1-based label (1 for the first policy year), not
    the projection's 0-based month index; ``Projection.lapse_rate_base`` reads it at
    ``policy_year(t)`` on the policy clock, so the file's keys are left as written.
    The two cells carry different tables: the guaranteed-acceptance one lapses faster
    early, on affordability attrition.  Both are **[std]** drafting constructions - no
    public UK whole of life lapse study was retrieved - and on a product with no
    surrender value they are the single largest lever on the liability.
    :mod:`~.WOL_UK_S`'s reader, indexed and sorted as it is, from the one read of the file,
    :func:`lapse_table_rows`; :func:`lapse_last_year` checks the table.
    """
    return lapse_table_rows().set_index(["cell", "policy_year"]).sort_index()


def lapse_table_rows():
    """*lapse_table.csv* as the file holds it: one row a line, in the file's order.

    The one read of the file.  :func:`lapse_last_year` checks it here, so that each
    refusal names the lines at fault, the header line 1, which the sort of
    :func:`lapse_table` would lose.
    """
    return pd.read_csv(input_dir() / lapse_table_file)               # noqa: F821


def mort_age_first():
    """The first attained age *mort_table.csv* gives a rate for, the table checked first.

    ``Projection.mort_rate`` asks it, and :func:`mort_age_last`, before it reads the
    table, so a table it cannot read is refused before any value of it is.  The check
    reads the file as it stands, :func:`mort_table_rows`, not :func:`mort_table`, which
    sorts it, so that each refusal names the lines at fault, the header line 1.  The
    rules, each over the whole table, the first that fails raising ``ValueError``:

    1. each age is a whole number, read by its value, so ``70.0`` is 70, and below
       ``2**53`` in size, which int64 holds exactly, the check made before the ages are
       cast;
    2. each basis is population or assured, each sex M or F and each smoker status NS or
       S, the codes the model point table and the cell give;
    3. each of the eight groups, the two bases by M and F by NS and S, runs over the
       table's ages from the first to the last, one row an age, none below 0: the
       projection reads a rate at each attained age a policy reaches. Every fault is named
       in one message: an age below 0 and an age a group repeats each with its lines, and
       each span of ages a group lacks, found from the ages each group holds, so that a key
       far from the rest costs no more than the rows;
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
    bad = lines[(~(tbl["basis"].isin(["population", "assured"])
                   & tbl["sex"].isin(["M", "F"])
                   & tbl["smoker"].isin(["NS", "S"]))).to_numpy()].tolist()
    if bad:
        raise ValueError(f"{name}: basis must be population or assured, sex M or F, and "
                         f"smoker NS or S; they are not on line {bad}")
    ages = ages.astype("int64")
    faults = []
    for a in sorted(set(ages[ages < 0])):
        faults.append(f"age {a}, below 0, is on lines "
                      f"{lines[(ages == a).to_numpy()].tolist()}")
    kept = ages[ages >= 0]
    if kept.empty:
        raise ValueError(f"{name}: no line holds an age of 0 or more")
    first, last = int(kept.min()), int(kept.max())
    for b in ("population", "assured"):
        for s in ("M", "F"):
            for k in ("NS", "S"):
                group = ((tbl["basis"] == b) & (tbl["sex"] == s) & (tbl["smoker"] == k)
                         & (ages >= 0)).to_numpy()
                run = ages[group]
                for a in sorted(set(run[run.duplicated()])):
                    faults.append(f"basis {b}, sex {s}, smoker {k}, age {a} repeats on "
                                  f"lines {lines[group & (ages == a).to_numpy()].tolist()}")
                spans, before = [], first - 1
                for a in [*(int(a) for a in sorted(set(run))), last + 1]:
                    if a > before + 1:
                        spans.append([before + 1, a - 1])
                    before = a
                for low, high in spans:
                    faults.append(f"no line holds basis {b}, sex {s}, smoker {k}, "
                                  + (f"ages {low} to {high}" if high > low
                                     else f"age {low}"))
    if faults:
        raise ValueError(f"{name}: the ages of each basis, sex and smoker status must run "
                         f"from {first} to {last}, the table's first and last, one row an "
                         f"age, none below 0; " + "; ".join(faults))
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


def lapse_last_year():
    """The last policy year *lapse_table.csv* gives each cell's rate for, the table checked
    first: int64 [cell].

    Element ``c`` is the last policy year of the cell whose code is ``c``, O50 0 and UW 1,
    as :func:`cell_code` numbers each point's.  ``Projection.lapse_rate_base`` asks it
    before it reads the table, and reads every later policy year at the cell's own last,
    :mod:`~.WOL_UK_S`'s ``tbl.index.max()`` on the cell's own rows; and
    :func:`lapse_table_array` is sized from the table it checks.  The check reads the file
    as it stands, :func:`lapse_table_rows`, so that each refusal names the lines at fault,
    the header line 1, and runs over the whole table.  The rules, the first that fails
    raising ``ValueError``:

    1. each policy year is a whole number, read by its value, and below ``2**53`` in size,
       which int64 holds exactly, the check made before the years are cast;
    2. each cell is O50 or UW, the codes the model point table holds;
    3. each cell's years run from 1, one row a year, without a gap or a repeat, since each
       policy year from the first is read: every fault named in one message, a year below
       1 and a repeated one each with its lines, and each span a cell lacks, a cell with
       no line lacking its first year, found from the years each cell holds, so that a
       key far from the rest costs no more than the rows;
    4. each ``lapse_rate`` is a number from 0 to 1, a probability, which the lapse rate's
       ``min`` reads.
    """
    name = lapse_table_file                                          # noqa: F821
    tbl = lapse_table_rows()
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
    bad = lines[(~tbl["cell"].isin(["O50", "UW"])).to_numpy()].tolist()
    if bad:
        raise ValueError(f"{name}: cell must be O50 or UW; it is not on line {bad}")
    keys = years.astype("int64")
    faults = []
    held = {}
    for c in ("O50", "UW"):
        mine = (tbl["cell"] == c).to_numpy()
        run = keys[mine]
        for y in sorted(set(run[run < 1])):
            faults.append(f"cell {c}, policy_year {y}, below 1, is on lines "
                          f"{lines[mine & (keys == y).to_numpy()].tolist()}")
        for y in sorted(set(run[run.duplicated() & (run >= 1)])):
            faults.append(f"cell {c}, policy_year {y} repeats on lines "
                          f"{lines[mine & (keys == y).to_numpy()].tolist()}")
        held[c] = [int(y) for y in sorted(set(run[run >= 1]))]
        spans, before = [], 0
        for y in held[c]:
            if y > before + 1:
                spans.append([before + 1, y - 1])
            before = y
        if not held[c]:
            spans.append([1, 1])
        for low, high in spans:
            faults.append(f"no line holds cell {c}, "
                          + (f"policy years {low} to {high}" if high > low
                             else f"policy_year {low}"))
    if faults:
        raise ValueError(f"{name}: the policy years of each cell must run from 1, one row "
                         f"a year, without a gap or a repeat; " + "; ".join(faults))
    rates = pd.to_numeric(tbl["lapse_rate"], errors="coerce")        # noqa: F821
    bad = lines[(~((rates >= 0) & (rates <= 1))).to_numpy()].tolist()
    if bad:
        raise ValueError(f"{name}: lapse_rate must be a number from 0 to 1; it is not on "
                         f"line {bad}")
    out = np.zeros(2, dtype="int64")                                 # noqa: F821
    for i, c in enumerate(("O50", "UW")):
        out[i] = held[c][-1]
    return out


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
    """The entry age (ALB) of every model point: int64 [point].

    Read as :mod:`~.WOL_UK_S` reads it, ``int`` of the number, which truncates a fraction;
    :func:`model_point_table` has refused one that is not a finite number below ``2**53``
    in size.
    """
    ages = pd.to_numeric(model_point_table()["entry_age"])           # noqa: F821
    return ages.to_numpy(dtype="int64")


def cell_code():
    """The cell of every model point, as its code: int64 [point].

    O50 0 and UW 1, ``Projection``'s References ``O50`` and ``UW``, and each cell's row of
    :func:`lapse_table_array` and :func:`lapse_last_year`.  A code, not the quantities it
    selects, because the loadings, the expenses and the benefit rules it selects are
    ``Projection``'s References and rules, which this Space cannot read.
    :func:`model_point_table` has refused any other cell, naming the point.
    """
    cells = model_point_table()["cell"].tolist()
    out = np.zeros(len(cells), dtype="int64")                        # noqa: F821
    for i in range(len(cells)):
        out[i] = ("O50", "UW").index(cells[i])
    return out


def escalation_code():
    """The escalation of every model point, as its code: int64 [point].

    level 0, fixed_5pct 1 and rpi 2, ``Projection``'s References ``LEVEL``, ``FIXED_5PCT``
    and ``RPI``, in the order :mod:`~.WOL_UK_S`'s ``esc_cover_step`` compares the text.  A
    code, not the steps it selects, because those are ``Projection``'s References, which
    this Space cannot read.  :func:`model_point_table` has refused any other escalation.
    """
    codes = model_point_table()["escalation"].tolist()
    out = np.zeros(len(codes), dtype="int64")                        # noqa: F821
    for i in range(len(codes)):
        out[i] = ("level", "fixed_5pct", "rpi").index(codes[i])
    return out


def mort_schedule():
    """The mortality table's row for every model point: int64 [point].

    The point's basis, sex and smoker status, the keys :mod:`~.WOL_UK_S` reads
    *mort_table.csv* by beside the age, numbered as :func:`mort_table_array` tables them:
    ``4 x basis + 2 x sex + smoker``, the basis population 0 and assured 1, the sex M 0 and
    F 1, the smoker status NS 0 and S 1, so 0 to 7 in the order :func:`mort_age_first`
    checks the groups.  The basis is the cell's, as ``Projection.mort_basis`` derives it,
    population for O50 and assured for UW.  :func:`model_point_table` has refused any other
    cell, sex or smoker status, so every point has one of the eight, and each is a whole
    run of the table's ages, which :func:`mort_age_first` checks.
    """
    table = model_point_table()
    cells, sexes, smokers = (table[c].tolist() for c in ("cell", "sex", "smoker"))
    out = np.zeros(len(cells), dtype="int64")                        # noqa: F821
    for i in range(len(cells)):
        out[i] = (4 * ("O50", "UW").index(cells[i]) + 2 * ("M", "F").index(sexes[i])
                  + ("NS", "S").index(smokers[i]))
    return out


def sum_assured():
    """The sum assured at outset of every model point: float64 [point]."""
    return pd.to_numeric(model_point_table()["sum_assured"]).to_numpy(  # noqa: F821
        dtype="float64")


def premium_mth():
    """The monthly premium at outset of every model point: float64 [point]."""
    return pd.to_numeric(model_point_table()["premium_mth"]).to_numpy(  # noqa: F821
        dtype="float64")


def cessation_months():
    """The premium-paying policy months of every model point, 0 for life: int64 [point].

    :func:`model_point_table` has refused one that is not a whole number, 0 or more, below
    ``2**53``.
    """
    months = pd.to_numeric(model_point_table()["cessation_months"])  # noqa: F821
    return months.to_numpy(dtype="int64")


def moratorium_months():
    """The moratorium in policy months of every model point: int64 [point].

    :func:`model_point_table` has refused one that is not a whole number, 0 or more, below
    ``2**53``.
    """
    months = pd.to_numeric(model_point_table()["moratorium_months"])  # noqa: F821
    return months.to_numpy(dtype="int64")


def variant_adb_2x():
    """Whether each model point carries the double accidental benefit: int64 [point], 1
    or 0.

    :mod:`~.WOL_UK_S` reads the column with ``bool``.  :func:`model_point_table` has refused
    a value whose text is not True or False, in either case, so pandas reads the column as
    booleans, and each is decoded by its text, element by element, which is ``bool`` of
    each wherever the table reads.  An int, not a bool: a numpy bool array compiles as a
    Python object, not a memoryview.
    """
    flags = model_point_table()["variant_adb_2x"].tolist()
    out = np.zeros(len(flags), dtype="int64")                        # noqa: F821
    for i in range(len(flags)):
        out[i] = 1 if str(flags[i]).lower() == "true" else 0
    return out


def variant_paid_up():
    """Whether each model point carries the pro-rata paid-up value: int64 [point], 1 or 0.

    Decoded as :func:`variant_adb_2x` is.
    """
    flags = model_point_table()["variant_paid_up"].tolist()
    out = np.zeros(len(flags), dtype="int64")                        # noqa: F821
    for i in range(len(flags)):
        out[i] = 1 if str(flags[i]).lower() == "true" else 0
    return out


def policy_count():
    """The ``policy_count`` of every model point, on full cover: float64 [point].

    :func:`model_point_table` has checked it: a number, zero or more.
    """
    return pd.to_numeric(model_point_table()["policy_count"]).to_numpy(  # noqa: F821
        dtype="float64")


def duration_mth():
    """The ``duration_mth`` of every model point, in whole months: int64 [point].

    :func:`model_point_table` has checked that each is whole and below ``2**53`` in size,
    so a duration written as ``200.0`` is the int 200.
    """
    months = pd.to_numeric(model_point_table()["duration_mth"])      # noqa: F821
    return months.to_numpy(dtype="int64")


def pols_pu_init():
    """The paid-up policies in force at the valuation date, of every model point: float64
    [point]."""
    return pd.to_numeric(model_point_table()["pols_pu_init"]).to_numpy(  # noqa: F821
        dtype="float64")


def pu_benefit_pp_init():
    """The paid-up cover per paid-up policy at the valuation date, of every model point:
    float64 [point]."""
    return pd.to_numeric(                                            # noqa: F821
        model_point_table()["pu_benefit_pp_init"]).to_numpy(dtype="float64")


def prem_cum_pp_init():
    """The premiums paid per policy to the end of month -1, of every model point: float64
    [point]."""
    return pd.to_numeric(                                            # noqa: F821
        model_point_table()["prem_cum_pp_init"]).to_numpy(dtype="float64")


def cover_pp_init():
    """The cover before month 0's events, of every model point: float64 [point]."""
    return pd.to_numeric(model_point_table()["cover_pp_init"]).to_numpy(  # noqa: F821
        dtype="float64")


def premium_pp_init():
    """The monthly premium before month 0's events, of every model point: float64
    [point]."""
    return pd.to_numeric(                                            # noqa: F821
        model_point_table()["premium_pp_init"]).to_numpy(dtype="float64")


def crossover_mth_init():
    """The policy month of a crossover before the valuation date, or -1, of every model
    point: int64 [point].

    :func:`model_point_table` has checked that each is whole, -1 or more and below
    ``2**53``.
    """
    months = pd.to_numeric(model_point_table()["crossover_mth_init"])  # noqa: F821
    return months.to_numpy(dtype="int64")


def mort_table_array():
    """The annual mortality rates by schedule and attained age, from *mort_table.csv*:
    float64 [schedule, age].

    Row ``s`` is a basis, a sex and a smoker status, ``4 x basis + 2 x sex + smoker``, as
    :func:`mort_schedule` numbers each point's, and column ``a`` the attained age ``a``:
    padded from age 0, as ``basiclife.BasicTerm_SC``'s ``mort_table_array`` pads its table,
    so that the index **is** the age, and :func:`mort_age_last` plus one wide.  The ages
    below the table's first, 0 to 17 as shipped, hold NaN, which no formula reads:
    ``Projection.mort_rate`` refuses an age outside the table, naming the point.  Asks
    :func:`mort_age_first` first, which checks the table: each schedule runs over every age
    from the first to the last, one row an age, so no cell between them is padding, and
    each rate is a number from 0 to 1.  Read from the one read of the file,
    :func:`mort_table_rows`, which :mod:`~.WOL_UK_S`'s reader sorts.
    """
    mort_age_first()
    last = mort_age_last()
    tbl = mort_table_rows()
    ages = pd.to_numeric(tbl["age"]).to_numpy(dtype="int64")         # noqa: F821
    rates = pd.to_numeric(tbl["mort_rate"]).to_numpy(dtype="float64")  # noqa: F821
    bases, sexes, smokers = (tbl[c].tolist() for c in ("basis", "sex", "smoker"))
    out = np.full((8, last + 1), np.nan)                             # noqa: F821
    for i in range(len(ages)):
        row = (4 * ("population", "assured").index(bases[i])
               + 2 * ("M", "F").index(sexes[i]) + ("NS", "S").index(smokers[i]))
        out[row, ages[i]] = rates[i]
    return out


def lapse_table_array():
    """The annual lapse rate by cell and policy year, from *lapse_table.csv*: float64
    [cell, policy year].

    Row ``c`` is the cell whose code is ``c``, O50 0 and UW 1, as :func:`cell_code`
    numbers each point's, and element ``[c, y]`` the rate of its policy year ``y``, from 1
    to the cell's last, :func:`lapse_last_year`, which checks the table first: each cell's
    years run from 1 without a gap.  As wide as the table's last year plus one.  Year 0, no
    policy year, and any year past a cell's last, where the other cell's runs further, hold
    NaN, which no formula reads: ``Projection.lapse_rate_base`` reads a policy year of
    cover, 1 or more, at most the cell's last, which it reads every later year at, as
    :mod:`~.WOL_UK_S` does.  It asks :func:`lapse_last_year` first, by one element, which
    runs the table's check, and takes its width from the table, never from that cell's
    array (R13).
    """
    lapse_last_year()[0]
    tbl = lapse_table_rows()
    years = pd.to_numeric(tbl["policy_year"]).to_numpy(dtype="int64")  # noqa: F821
    rates = pd.to_numeric(tbl["lapse_rate"]).to_numpy(dtype="float64")  # noqa: F821
    cells = tbl["cell"].tolist()
    out = np.full((2, int(years.max()) + 1), np.nan)                 # noqa: F821
    for i in range(len(cells)):
        out[("O50", "UW").index(cells[i]), years[i]] = rates[i]
    return out


# ---------------------------------------------------------------------------
# References

model_point_file = "model_point_table_sec.csv"

mort_table_file = "mort_table.csv"

lapse_table_file = "lapse_table.csv"

future_horizon_mth = 120

pd = ("Module", "pandas")

np = ("Module", "numpy")
