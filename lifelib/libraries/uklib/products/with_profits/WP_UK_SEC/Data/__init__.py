# modelx: pseudo-python
# This file is part of a modelx model.
# It can be imported as a Python module, but functions defined herein
# are model formulas and may not be executable as standard Python.

"""Input data shared by every by-policy projection.

The three input CSVs are read here, **once per model**, and referenced from
:mod:`~.WP_UK_SEC.Projection` as ``data``. :mod:`~.WP_UK_SEC.Projection` is parameterized by
``idx``, the position of a model point in the table, so each ``Projection[i]`` is a
separate ItemSpace with its own cells cache; if the readers lived there, every model point
would re-read every file. Holding them in an unparameterized Space reads each file once no
matter how many policies are projected.

Inputs are **external files**: plain CSVs in the model folder's parent directory,
``products/with_profits/``, rather than data stored inside the model. The model folder
therefore holds nothing but formulas — no ``_data/``, no IOSpec, no embedded values —
so a diff of the model shows logic changes only. This follows ``annuallife.TradLife_A``;
contrast ``basiclife.BasicTerm_S``, which keeps its inputs *inside* the model through
modelx's IOSpec machinery.

The consequence worth knowing: **the model is not portable on its own.** Copying the
``WP_UK_SEC`` folder without its parent's CSVs produces a model that reads and then fails
on first evaluation.

**Two of the tables are WP_UK_S's.** The mortality and lapse tables are the files
:mod:`~.WP_UK_S` reads, read here in place by :mod:`~.WP_UK_S`'s own readers: one copy of
each table serves both models, so an edit to one reaches both. The model point table,
``model_point_table_sec.csv``, is this model's own, and sits beside :mod:`~.WP_UK_S`'s
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

Note how little is in a file. The discretionary scale that actually drives this product
— the bonus rates, the smoothing cap, the target corridor, the guarantee-fill target,
the charge levels — lives in model point columns and ``Projection`` References rather
than in a rate table, and that is not an oversight: **none of it is published**. Firms'
principles and practices documents describe the discretion and withhold the numbers, so
every one of those values is a standardization, and putting them where a reader trips
over them is better than filing them in a table that looks like data.

**The model point table is checked as it is read.** Ten of its columns are the in-force
interface: ``policy_count`` and ``duration_mth``, as in ``basiclife.BasicTerm_SE``, and the
opening state of a point in force, each per policy and measured at the start of month 0,
before any month-0 event: the asset share, the units and the unit price, the attaching
bonus, the smoothed payout, the bonus rate of the policy year under way, and the two
cumulants :mod:`~.WP_UK_S` restarts at 0, the guarantee charges taken and the smoothing
account. :func:`model_point_table` refuses a table that lacks one, repeats a
``point_id``, holds a count, a duration or a state no policy can have, or a policy to be
issued more than ``future_horizon_mth`` months after the valuation date, 120 as shipped:
future new business is written over a stated horizon, so that no frame runs longer than
cover from issue plus that horizon. Set to 0, the Reference refuses future new business
altogether. It refuses, too, what :mod:`~.WP_UK_S` projects without a word or meets only
when a projection reaches it: a code that names no chassis, sex or tax basis, guarantee
dates that are no anniversaries or that a conventional endowment carries, an age, an
amount, a rate or a term that is not a number in its range, a fund return at which the
monthly return has no real value, and a history the contract cannot have given. The checks
run in turn, and the first that fails raises, naming the missing column or every point
that fails it. Whether a point is still in cover at the valuation date, and whether the
contract issues it, are rules of the product, and ``Projection.proj_len`` checks them,
against its own References.

**Each assumption table is checked before a value of it is read.** Its keys are read by
their value, so an age written ``70.0`` is age 70, and a key that is not whole, text among
them, or is ``2**53`` or more in size, which int64 would hold inexactly, is refused; so are
keys that repeat or leave a gap the projection would read, each gap found from the keys a
group holds, so that a key far from the rest costs no more than the rows. A value that is
blank, text, infinite or outside its range is refused, whether or not a point reads it:
``Projection.mort_rate`` caps the annual rate with ``min``, which keeps its first argument
unless a later one compares smaller, and no comparison with NaN holds, so the cap is
written with its bound second and a NaN would stay NaN; but an infinity is a number, which
the cap reads as 1, certain death, and ``Projection.surr_rate`` bounds the surrender rate
with :mod:`~.WP_UK_S`'s ``min(1.0, ...)``, its bound first, which reads a NaN as certain
surrender. The check of each table is in the cell the projection takes the table's extent
from, which it asks before it reads the table: :func:`mort_age_first` and
:func:`mort_age_last` for the mortality table, and :func:`lapse_last_year` for the lapse
table. Each refusal names the table's lines, the header line 1: the check reads the file as
it stands, :func:`mort_table_rows` and :func:`lapse_table_rows`, where :mod:`~.WP_UK_S`'s
readers, :func:`mort_table` and :func:`lapse_table`, sort the tables, and with the order
would lose the lines. A read beyond the mortality table's ages is refused by the one
``Projection`` cell that reads it, naming the point, where :mod:`~.WP_UK_S`'s lookup
raised ``KeyError``.

**The vectors.** The readers return what the files hold, and no
:mod:`~.WP_UK_SEC.Projection` cell but ``model_point``, a reporting cell, reads them. The
others read the arrays below instead, one element at a time, a model point's attribute
being the element at its position, ``data.sum_assured()[idx]``. That is what lets the
model compile to C, as ``basiclife.BasicTerm_SC`` does: each array is a numpy vector or
table of int64 or float64, which compiles to a typed memoryview, never one of bools,
objects or text, and each extent of a table is an int.

Text the projection needs is decoded here, into the number it selects, for every point at
once, as :mod:`~.WP_UK_S` reads each value: the chassis into its code, UWP_bond 0 and
CWP_endowment 1, ``Projection``'s References ``UWP_BOND`` and ``CWP_ENDOWMENT``, which is
the chassis's row of the lapse table, and stays a code because the rules it selects are
``Projection``'s; the sex into the point's row of the mortality table, M 0 and F 1, its
schedule; and the guarantee dates, the text of one policy anniversary or a ``;``-separated
list of them, into a flag by point and policy year, 1 where the anniversary closing that
policy year is a guarantee date. The tax basis is no number a formula reads: the fund
return is supplied on it, and ``Projection.tax_basis`` reports it. And each table keyed by
more than a number becomes an integer-indexed array. The mortality table, keyed by sex and
age, is tabled by its two schedules, M before F, and padded from age 0, so that the index
is the attained age; the lapse table, keyed by chassis and policy year, is tabled by the
chassis's code and padded at year 0, beside each chassis's last year:

==============================  =======  ================  =================================
Cells                           dtype    Shape             From
==============================  =======  ================  =================================
point_id()                      int64    [point]           the table's index
chassis_code()                  int64    [point]           ``chassis``, decoded: UWP_bond 0,
                                                           CWP_endowment 1
mort_schedule()                 int64    [point]           ``sex``, decoded: M 0, F 1
age_at_entry()                  int64    [point]           ``age_at_entry``
premium_single()                float64  [point]           ``premium_single``
premium_regular()               float64  [point]           ``premium_regular``
sum_assured()                   float64  [point]           ``sum_assured``
policy_term()                   int64    [point]           ``policy_term``
units_init()                    float64  [point]           ``units_init``
unit_price_init()               float64  [point]           ``unit_price_init``
attaching_bonus_init()          float64  [point]           ``attaching_bonus_init``
asset_share_init()              float64  [point]           ``asset_share_init``
smoothed_payout_init()          float64  [point]           ``smoothed_payout_init``
wd_rate()                       float64  [point]           ``wd_rate``
fund_return()                   float64  [point]           ``fund_return``
bonus_rate_init()               float64  [point]           ``bonus_rate_init``
policy_count()                  float64  [point]           ``policy_count``
duration_mth()                  int64    [point]           ``duration_mth``
guar_charge_cum_pp_init()       float64  [point]           ``guar_charge_cum_pp_init``
smoothing_account_init()        float64  [point]           ``smoothing_account_init``
guarantee_year_last()           int      scalar            *mort_table.csv*'s last age
                                                           plus 2
guarantee_flags()               int64    [point, year]     ``guarantee_dates``, decoded: 1
                                                           at each date's policy year
mort_age_first()                int      scalar            *mort_table.csv*, checked
mort_age_last()                 int      scalar            *mort_table.csv*
mort_table_array()              float64  [schedule, age]   *mort_table.csv*
lapse_last_year()               int64    [chassis]         *lapse_table.csv*, checked
lapse_table_array()             float64  [chassis, year]   *lapse_table.csv*
==============================  =======  ================  =================================

**An array is read by element, never whole,** in this Space as in
:mod:`~.WP_UK_SEC.Projection`. The compiler types an array cell as a memoryview only once
it has seen that every use of it, in either Space, is an element read: one ``len()``,
slice, loop over it or numpy call on it anywhere, and the cell compiles as a Python object.
So an array derived here reads the table's column, never another cell's array, and a width
comes from a table or an extent's cell.

**What cannot be held is refused** when the table is first read, naming every point or
line at fault, beside the checks above: a ``point_id`` that is not a whole number below
``2**53`` in size, when :func:`point_id` is first read, as a refusal reads it; and a
mortality age or a lapse policy year ``2**53`` or more in size, by the table's check, each
of which numpy would otherwise cast to int64 inexactly, or to the least int64, without a
word. :func:`model_point_table` already holds every other whole number a vector carries,
the ages, the terms, the durations and the guarantee years, below ``2**53``. A guarantee
year past :func:`guarantee_year_last` is no year a frame reads, and is not tabled: no
cover runs past the largest limiting age the mortality table admits, a year past its last
age, and the last month of the longest cover reads the date a year after its own.
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

    Indexed by ``point_id``. Ten columns are the in-force interface: ``policy_count`` and
    ``duration_mth``, the completed policy months at the valuation date, as in
    ``basiclife.BasicTerm_SE``, and the eight of a point's opening state, each per policy.
    The rest are :mod:`~.WP_UK_S`'s, but ``pols_if_init``, which ``policy_count`` replaces,
    ``duration_inforce``, the completed years ``duration_mth`` replaces, the three columns
    renamed to D6's vocabulary, ``units``, ``attaching_bonus`` and ``bonus_rate``, now
    ``units_init``, ``attaching_bonus_init`` and ``bonus_rate_init``, and ``row_kind``,
    ``source_policy_id``, ``source_mth`` and ``source_refs``, which record where the
    generator took each shipped row from, and under what References, and which no formula
    reads.

    The checks run over the whole table at once, and the first that fails raises
    ``ValueError``, naming the missing column or every point it fails on:

    1. the ten in-force columns are present;
    2. no ``point_id`` appears twice;
    3. ``policy_count`` is a number, zero or more;
    4. ``duration_mth`` is a whole number of months, below ``2**53`` in size, which numpy
       would otherwise cast to the least int64 without a word: positive for a policy in
       force, 0 for one issued at the valuation date, negative for one issued later;
    5. no policy is issued more than ``future_horizon_mth`` months after the valuation
       date, so ``duration_mth`` is ``-future_horizon_mth`` or more. At 0 the model takes
       no future new business, and the message says so; a horizon that is not a whole
       number of months, 0 or more, below ``2**53``, is itself refused, since a NaN one
       fails every comparison and so would admit every policy, and an infinite one bounds
       nothing.  A longer horizon than the shipped 120 is read as set: a frame longer
       than the compiled model's caches hold, 1,356 months, is refused by point, by
       ``Projection.proj_len``, and every shorter one projects whose cover is no longer
       than the caches are sized for, 1,236 months;
    6. ``chassis`` is UWP_bond or CWP_endowment, ``sex`` M or F and ``tax_basis`` life_net
       or pension_gross, the codes the formulas branch on and the tables are keyed by,
       which :mod:`~.WP_UK_S` refuses only once a projection reaches them;
    7. ``age_at_entry`` and ``policy_term`` are whole numbers, 0 or more, below ``2**53``,
       which :mod:`~.WP_UK_S` reads with ``int``, truncating a fraction; ``premium_single``,
       ``premium_regular`` and ``sum_assured`` are numbers, zero or more; ``wd_rate``, the
       share of the original premium withdrawn a year, is a number from 0 to 1; and
       ``fund_return`` is a finite number above -1, since at -1 or below the monthly
       return, ``(1 + r)^(1/12) - 1``, has no real value;
    8. ``guarantee_dates`` is blank or a ``;``-separated list of policy anniversaries, each
       a whole number of years, 1 or more, below ``2**53``, the form
       :func:`guarantee_flags` decodes; and it is blank on a conventional endowment,
       which has no guarantee dates, though ``Projection.guarantee_exercise`` and
       ``Projection.guarantee_imminent`` would read any it held;
    9. a conventional endowment has a term, ``policy_term`` 1 or more, which its maturity is
       read from, and no units; a bond, whole of life, has no term, ``policy_term`` 0, and
       no attaching bonus;
    10. the opening state is a number in its range: ``asset_share_init``, ``units_init``,
        ``attaching_bonus_init``, ``smoothed_payout_init`` and ``guar_charge_cum_pp_init``
        amounts, zero or more; ``unit_price_init`` a finite number above 0, a price;
        ``bonus_rate_init`` a finite number, zero or more, the declared bonus being floored
        at 0 by the contract; and ``smoothing_account_init`` a finite number of either
        sign, the estate's cumulative cost, which is negative where payouts have fallen
        short of the asset shares;
    11. a policy not yet in force, ``duration_mth`` 0 or less, holds no opening state: no
        asset share, units, attaching bonus, payout, guarantee charges or smoothing
        account, all 0. Its ``unit_price_init`` and ``bonus_rate_init`` are issue values,
        the seed price its premium buys units at and the rate of its first policy year,
        and are exempt;
    12. a bond in force holds units, ``units_init`` above 0: a bond whose units are spent
        is encashed, and has nothing to project;
    13. a policy in force with an asset share above a cent has a payout above 0: the
        smoothing cap holds a payout above 0 once it is, and the cap is skipped only from a
        payout of 0, which :mod:`~.WP_UK_S` holds only where the asset share is 0, the
        corridor's.  It compares to the cent, a rule tying two amounts of money: an extract
        carrying an asset share of £0.006 and its payout of £0.0048 to the cent reads 0.01
        beside 0.00, which is read;
    14. a conventional endowment in force 11 months or fewer has no attaching bonus, to the
        cent: the first declaration falls at the end of policy month 11, and before it no
        reversionary bonus has been added.

    Rules 13 and 14 hold the amounts to the cent, rule 14 within half a cent of 0, so that
    an extract rounded to the cent reads. Each rule of the history holds of every state
    :mod:`~.WP_UK_S` reaches, under any References: the relations it states are the
    contract's.
    """
    name = model_point_file                                          # noqa: F821
    table = pd.read_csv(input_dir() / name, index_col="point_id")    # noqa: F821
    amounts = ("asset_share_init", "units_init", "attaching_bonus_init",
               "smoothed_payout_init", "guar_charge_cum_pp_init")
    state_columns = (*amounts, "unit_price_init", "bonus_rate_init",
                     "smoothing_account_init")
    for column in ("policy_count", "duration_mth", "asset_share_init", "units_init",
                   "unit_price_init", "attaching_bonus_init", "smoothed_payout_init",
                   "bonus_rate_init", "guar_charge_cum_pp_init", "smoothing_account_init"):
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
    horizon = int(horizon)
    bad = table.index[months < -horizon].tolist()
    if bad and horizon == 0:
        raise ValueError(f"{name}: duration_mth must be 0 or more: this model takes no "
                         f"future new business; it is not at point_id {bad}")
    if bad:
        raise ValueError(f"{name}: duration_mth must be -{horizon} or more, a policy "
                         f"issued at most {horizon} months after the valuation date; it "
                         f"is not at point_id {bad}")
    for column, codes in (("chassis", ("UWP_bond", "CWP_endowment")),
                          ("sex", ("M", "F")),
                          ("tax_basis", ("life_net", "pension_gross"))):
        bad = table.index[~table[column].isin(codes)].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be {' or '.join(codes)}; it is not "
                             f"at point_id {bad}")
    rules = {"whole": ("a whole number, 0 or more, below 2**53",
                       lambda v: (v >= 0) & (v % 1 == 0) & (v < 2.0 ** 53)),
             "amount": ("a number, zero or more",
                        lambda v: (v >= 0) & (v < float("inf"))),
             "share": ("a number from 0 to 1",
                       lambda v: (v >= 0) & (v <= 1)),
             "return": ("a finite number above -1",
                        lambda v: (v > -1) & (v < float("inf")))}
    numbers = {}
    for column, kind in (("age_at_entry", "whole"), ("policy_term", "whole"),
                         ("premium_single", "amount"), ("premium_regular", "amount"),
                         ("sum_assured", "amount"), ("wd_rate", "share"),
                         ("fund_return", "return")):
        rule, holds = rules[kind]
        v = pd.to_numeric(table[column], errors="coerce")            # noqa: F821
        bad = table.index[~holds(v)].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be {rule}; it is not at point_id "
                             f"{bad}")
        numbers[column] = v

    dates = table["guarantee_dates"]
    bad = []
    for point, v in dates.items():
        if pd.isna(v):                                               # noqa: F821
            continue
        for s in str(v).split(";"):
            if not s.strip():
                continue
            y = pd.to_numeric(s.strip(), errors="coerce")            # noqa: F821
            if not (y >= 1 and y % 1 == 0 and y < 2.0 ** 53):
                bad.append(point)
                break
    if bad:
        raise ValueError(f"{name}: guarantee_dates must be blank or policy anniversaries "
                         f"separated by ';', each a whole number of years, 1 or more, below "
                         f"2**53; they are not at point_id {bad}")
    bond = table["chassis"] == "UWP_bond"
    bad = table.index[~bond & dates.notna()].tolist()
    if bad:
        raise ValueError(f"{name}: guarantee_dates must be blank on a conventional "
                         f"endowment, which has no guarantee dates; it is not at point_id "
                         f"{bad}")
    term = numbers["policy_term"]
    bad = table.index[~bond & (term < 1)].tolist()
    if bad:
        raise ValueError(f"{name}: policy_term must be 1 or more on a conventional "
                         f"endowment, the years to its maturity; it is not at point_id "
                         f"{bad}")
    bad = table.index[bond & (term != 0)].tolist()
    if bad:
        raise ValueError(f"{name}: policy_term must be 0 on a bond, which is whole of life "
                         f"and has no term; it is not at point_id {bad}")
    state = {}
    for column in amounts:
        v = pd.to_numeric(table[column], errors="coerce")            # noqa: F821
        bad = table.index[~((v >= 0) & (v < float("inf")))].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be a number, zero or more; it is not "
                             f"at point_id {bad}")
        state[column] = v
    v = pd.to_numeric(table["unit_price_init"], errors="coerce")     # noqa: F821
    bad = table.index[~((v > 0) & (v < float("inf")))].tolist()
    if bad:
        raise ValueError(f"{name}: unit_price_init must be a finite number above 0, a "
                         f"price; it is not at point_id {bad}")
    state["unit_price_init"] = v
    v = pd.to_numeric(table["bonus_rate_init"], errors="coerce")     # noqa: F821
    bad = table.index[~((v >= 0) & (v < float("inf")))].tolist()
    if bad:
        raise ValueError(f"{name}: bonus_rate_init must be a finite number, zero or more, "
                         f"a declared bonus being floored at 0; it is not at point_id "
                         f"{bad}")
    state["bonus_rate_init"] = v
    v = pd.to_numeric(table["smoothing_account_init"], errors="coerce")  # noqa: F821
    bad = table.index[~((v > -float("inf")) & (v < float("inf")))].tolist()
    if bad:
        raise ValueError(f"{name}: smoothing_account_init must be a finite number; it is "
                         f"not at point_id {bad}")
    state["smoothing_account_init"] = v
    bad = table.index[~bond & (state["units_init"] != 0)].tolist()
    if bad:
        raise ValueError(f"{name}: units_init must be 0 on a conventional endowment, which "
                         f"holds no units; it is not at point_id {bad}")
    bad = table.index[bond & (state["attaching_bonus_init"] != 0)].tolist()
    if bad:
        raise ValueError(f"{name}: attaching_bonus_init must be 0 on a bond, whose bonus "
                         f"is in its unit price; it is not at point_id {bad}")
    for column in (*amounts, "smoothing_account_init"):
        bad = table.index[(months <= 0) & (state[column] != 0)].tolist()
        if bad:
            raise ValueError(f"{name}: {column} must be 0 on a policy not yet in force, "
                             f"duration_mth 0 or less; it is not at point_id {bad}")
    bad = table.index[bond & (months > 0) & ~(state["units_init"] > 0)].tolist()
    if bad:
        raise ValueError(f"{name}: units_init must be above 0 on a bond in force, whose "
                         f"units are spent only when it is encashed; it is not at point_id "
                         f"{bad}")
    cent = 0.005
    bad = table.index[(months > 0) & (state["asset_share_init"] > 2 * cent)
                      & ~(state["smoothed_payout_init"] > 0)].tolist()
    if bad:
        raise ValueError(f"{name}: smoothed_payout_init must be above 0 on a policy in force "
                         f"with an asset share above a cent, which holds the payout above 0; "
                         f"it is not at point_id {bad}")
    bad = table.index[~bond & (months > 0) & (months <= 11)
                      & (state["attaching_bonus_init"] > cent)].tolist()
    if bad:
        raise ValueError(f"{name}: attaching_bonus_init must be 0, to the cent, on a "
                         f"conventional endowment in force 11 months or fewer, before its "
                         f"first declaration at the end of policy month 11; it is not at "
                         f"point_id {bad}")
    return table


def mort_table():
    """The base annual mortality rates by sex and age, from *mort_table.csv*.

    A **[std]** proxy shaped like the ONS national life tables, which are the only
    freely redistributable UK mortality source; CMI tables issued after March 2013 are
    restricted to Authorised Users, so no current insured rate can be reproduced here.
    ``Projection.mort_be_factor`` carries the allowance for population mortality being
    heavier than insured experience.  Sorted on read, because ``Projection.mort_rate``
    indexes into it.  :mod:`~.WP_UK_S`'s reader, indexed and sorted as it is, from the one
    read of the file, :func:`mort_table_rows`; :func:`mort_age_first` checks the table.
    """
    return mort_table_rows().set_index(["sex", "age"]).sort_index()


def mort_table_rows():
    """*mort_table.csv* as the file holds it: one row a line, in the file's order.

    The one read of the file.  :func:`mort_age_first` checks it here, so that each refusal
    names the lines at fault, the header line 1, which the sort of :func:`mort_table`, the
    reader the projection indexes into, would lose.
    """
    return pd.read_csv(input_dir() / mort_table_file)                # noqa: F821


def lapse_table():
    """The base annual surrender rates by chassis and policy year, from *lapse_table.csv*.

    The ``policy_year`` key is the **contractual 1-based label**, not the projection's
    month: ``Projection.surr_rate_base(t)`` reads row ``policy_year(t)``, on the policy
    clock, and takes the chassis's last row beyond it, :func:`lapse_last_year`.

    Flat on the bond chassis and duration-declining on the endowment.  Both are **[std]**
    drafting constructions - no public UK with-profits lapse experience was retrieved -
    and the dynamic multipliers layered on them in ``Projection.surr_rate`` matter more
    than the levels do, because anti-selective exit when guarantees are in the money is
    the dominant behavioural risk on this product.  :mod:`~.WP_UK_S`'s reader, indexed and
    sorted as it is, from the one read of the file, :func:`lapse_table_rows`;
    :func:`lapse_last_year` checks the table.
    """
    return lapse_table_rows().set_index(["chassis", "policy_year"]).sort_index()


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
    2. each sex is M or F, the codes the model point table gives;
    3. each sex runs over the table's ages from the first to the last, one row an age,
       none below 0: the projection reads a rate at each attained age a policy reaches.
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
    ages = pd.to_numeric(mort_table_rows()["age"], errors="coerce")  # noqa: F821
    return int(ages.max())


def lapse_last_year():
    """The last policy year *lapse_table.csv* gives each chassis's rate for, the table
    checked first: int64 [chassis].

    Element ``c`` is the last policy year of the chassis whose code is ``c``, UWP_bond 0
    and CWP_endowment 1, as :func:`chassis_code` numbers each point's.
    ``Projection.surr_rate_base`` asks it before it reads the table, and reads every later
    policy year at the chassis's own last, :mod:`~.WP_UK_S`'s ``tbl.index.max()`` on the
    chassis's own rows; and :func:`lapse_table_array` is sized from the table it checks.
    The check reads the file as it stands, :func:`lapse_table_rows`, so that each refusal
    names the lines at fault, the header line 1, and runs over the whole table.  The
    rules, the first that fails raising ``ValueError``:

    1. each policy year is a whole number, read by its value, and below ``2**53`` in size,
       which int64 holds exactly, the check made before the years are cast;
    2. each chassis is UWP_bond or CWP_endowment, the codes the model point table holds;
    3. each chassis's years run from 1, one row a year, without a gap or a repeat, since
       each policy year from the first is read: every fault named in one message, a year
       below 1 and a repeated one each with its lines, and each span a chassis lacks, a
       chassis with no line lacking its first year, found from the years each chassis
       holds, so that a key far from the rest costs no more than the rows;
    4. each ``lapse_rate`` is a number from 0 to 1, a probability, which the surrender
       rate's ``min`` reads.
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
    bad = lines[(~tbl["chassis"].isin(["UWP_bond", "CWP_endowment"])).to_numpy()].tolist()
    if bad:
        raise ValueError(f"{name}: chassis must be UWP_bond or CWP_endowment; it is not on "
                         f"line {bad}")
    keys = years.astype("int64")
    faults = []
    held = {}
    for c in ("UWP_bond", "CWP_endowment"):
        mine = (tbl["chassis"] == c).to_numpy()
        run = keys[mine]
        for y in sorted(set(run[run < 1])):
            faults.append(f"chassis {c}, policy_year {y}, below 1, is on lines "
                          f"{lines[mine & (keys == y).to_numpy()].tolist()}")
        for y in sorted(set(run[run.duplicated() & (run >= 1)])):
            faults.append(f"chassis {c}, policy_year {y} repeats on lines "
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
            faults.append(f"no line holds chassis {c}, "
                          + (f"policy years {low} to {high}" if high > low
                             else f"policy_year {low}"))
    if faults:
        raise ValueError(f"{name}: the policy years of each chassis must run from 1, one "
                         f"row a year, without a gap or a repeat; " + "; ".join(faults))
    rates = pd.to_numeric(tbl["lapse_rate"], errors="coerce")        # noqa: F821
    bad = lines[(~((rates >= 0) & (rates <= 1))).to_numpy()].tolist()
    if bad:
        raise ValueError(f"{name}: lapse_rate must be a number from 0 to 1; it is not on "
                         f"line {bad}")
    out = np.zeros(2, dtype="int64")                                 # noqa: F821
    for i, c in enumerate(("UWP_bond", "CWP_endowment")):
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


def chassis_code():
    """The chassis of every model point, as its code: int64 [point].

    UWP_bond 0 and CWP_endowment 1, ``Projection``'s References ``UWP_BOND`` and
    ``CWP_ENDOWMENT``, and each chassis's row of :func:`lapse_table_array` and
    :func:`lapse_last_year`.  A code, not the quantities it selects, because the rules it
    selects, the bond's units and price, its market value reduction and its guarantee
    dates, the endowment's term and its surrender basis, are ``Projection``'s formulas and
    References, which this Space cannot read.  :func:`model_point_table` has refused any
    other chassis, naming the point.
    """
    codes = model_point_table()["chassis"].tolist()
    out = np.zeros(len(codes), dtype="int64")                        # noqa: F821
    for i in range(len(codes)):
        out[i] = ("UWP_bond", "CWP_endowment").index(codes[i])
    return out


def mort_schedule():
    """The mortality table's row for every model point: int64 [point].

    The point's sex, the key :mod:`~.WP_UK_S` reads *mort_table.csv* by beside the age,
    numbered as :func:`mort_table_array` tables it: M 0 and F 1, in the order
    :func:`mort_age_first` checks the sexes.  :func:`model_point_table` has refused any
    other sex, so every point has one of the two, and each is a whole run of the table's
    ages, which :func:`mort_age_first` checks.
    """
    sexes = model_point_table()["sex"].tolist()
    out = np.zeros(len(sexes), dtype="int64")                        # noqa: F821
    for i in range(len(sexes)):
        out[i] = ("M", "F").index(sexes[i])
    return out


def age_at_entry():
    """The entry age (ANB) of every model point: int64 [point].

    :func:`model_point_table` has refused one that is not a whole number, 0 or more,
    below ``2**53``.
    """
    ages = pd.to_numeric(model_point_table()["age_at_entry"])        # noqa: F821
    return ages.to_numpy(dtype="int64")


def premium_single():
    """The single premium of every model point, paid in its issue month: float64
    [point]."""
    return pd.to_numeric(model_point_table()["premium_single"]).to_numpy(  # noqa: F821
        dtype="float64")


def premium_regular():
    """The regular annual premium of every model point: float64 [point]."""
    return pd.to_numeric(model_point_table()["premium_regular"]).to_numpy(  # noqa: F821
        dtype="float64")


def sum_assured():
    """The basic sum assured of every model point: float64 [point]."""
    return pd.to_numeric(model_point_table()["sum_assured"]).to_numpy(  # noqa: F821
        dtype="float64")


def policy_term():
    """The endowment term in years of every model point, 0 on the bond: int64 [point].

    :func:`model_point_table` has refused one that is not a whole number, 0 or more,
    below ``2**53``.
    """
    terms = pd.to_numeric(model_point_table()["policy_term"])        # noqa: F821
    return terms.to_numpy(dtype="int64")


def units_init():
    """The units held entering month 0, of every model point: float64 [point]."""
    return pd.to_numeric(model_point_table()["units_init"]).to_numpy(  # noqa: F821
        dtype="float64")


def unit_price_init():
    """The unit price month 0 opens with, or the seed price, of every model point:
    float64 [point]."""
    return pd.to_numeric(                                            # noqa: F821
        model_point_table()["unit_price_init"]).to_numpy(dtype="float64")


def attaching_bonus_init():
    """The reversionary bonuses attaching at the valuation date, of every model point:
    float64 [point]."""
    return pd.to_numeric(                                            # noqa: F821
        model_point_table()["attaching_bonus_init"]).to_numpy(dtype="float64")


def asset_share_init():
    """The asset share month 0 opens with, of every model point: float64 [point]."""
    return pd.to_numeric(                                            # noqa: F821
        model_point_table()["asset_share_init"]).to_numpy(dtype="float64")


def smoothed_payout_init():
    """The smoothed payout month 0 opens with, of every model point: float64 [point]."""
    return pd.to_numeric(                                            # noqa: F821
        model_point_table()["smoothed_payout_init"]).to_numpy(dtype="float64")


def wd_rate():
    """The withdrawal taken a year, a share of the original premium, of every model point:
    float64 [point]."""
    return pd.to_numeric(model_point_table()["wd_rate"]).to_numpy(  # noqa: F821
        dtype="float64")


def fund_return():
    """The earned fund return, annual, of every model point: float64 [point]."""
    return pd.to_numeric(model_point_table()["fund_return"]).to_numpy(  # noqa: F821
        dtype="float64")


def bonus_rate_init():
    """The bonus rate declared at the last declaration before the valuation date, or the
    rate a new policy's first declaration starts from, of every model point: float64
    [point]."""
    return pd.to_numeric(                                            # noqa: F821
        model_point_table()["bonus_rate_init"]).to_numpy(dtype="float64")


def policy_count():
    """The ``policy_count`` of every model point: float64 [point].

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


def guar_charge_cum_pp_init():
    """The guarantee charges taken per policy before the valuation date, of every model
    point: float64 [point]."""
    return pd.to_numeric(                                            # noqa: F821
        model_point_table()["guar_charge_cum_pp_init"]).to_numpy(dtype="float64")


def smoothing_account_init():
    """The estate's smoothing cost since issue per policy in force, of every model point:
    float64 [point]."""
    return pd.to_numeric(                                            # noqa: F821
        model_point_table()["smoothing_account_init"]).to_numpy(dtype="float64")


def guarantee_year_last():
    """The last policy year :func:`guarantee_flags` holds: :func:`mort_age_last` plus 2.

    The year after the last a cover can reach.  ``Projection.proj_len`` admits a limiting
    age, ``omega_age``, of at most a year past the mortality table's last age, and an
    issue age of ``issue_age_min``, 0 or more, so no cover runs past policy year
    ``mort_age_last() + 1``; and the guarantee-imminent window of a cover's last month, the
    twelfth of its last policy year, reads the date a year on.  A later guarantee date is
    one no frame reads, and is not tabled.  122 as shipped.  The array is read by value,
    not cached, so it may run past the policy years ``Projection``'s caches hold, to 104,
    the year a cover of 1,236 months, the longest ``Projection.proj_len`` admits, reads
    last.
    """
    return mort_age_last() + 2


def guarantee_flags():
    """Whether each policy anniversary of every model point is a guarantee date: int64
    [point, policy year], 1 or 0.

    Element ``[i, y]`` is 1 where point ``i``'s ``guarantee_dates`` name policy year
    ``y``, whose anniversary, the end of its twelfth month, is then a date an exit is
    MVR-free, and 0 elsewhere: year 0, no policy year, every year a point names no date
    at, and every policy year of a conventional endowment, which carries none.  As wide
    as :func:`guarantee_year_last` plus one, every year a frame can read, and a date
    named past it is not tabled, no frame reading it.  Each value is read as
    :mod:`~.WP_UK_S`'s ``guarantee_years`` reads it, and as :func:`model_point_table`'s
    eighth rule checks it, ``str()`` of it split at each ``;``, each part stripped and
    read by its value, a blank part skipped: so ``10``, ``10.0``, `` 10`` and ``10;`` name
    year 10.  :func:`model_point_table` has refused a value whose parts are not whole
    numbers, 1 or more, below ``2**53``, and a date on an endowment.
    """
    dates = model_point_table()["guarantee_dates"].tolist()
    last = guarantee_year_last()
    out = np.zeros((len(dates), last + 1), dtype="int64")            # noqa: F821
    for i in range(len(dates)):
        if pd.isna(dates[i]):                                        # noqa: F821
            continue
        for s in str(dates[i]).split(";"):
            if not s.strip():
                continue
            y = int(pd.to_numeric(s.strip()))                        # noqa: F821
            if y <= last:
                out[i, y] = 1
    return out


def mort_table_array():
    """The annual mortality rates by sex and attained age, from *mort_table.csv*: float64
    [schedule, age].

    Row ``s`` is the sex, M 0 and F 1, as :func:`mort_schedule` numbers each point's, and
    column ``a`` the attained age ``a``: padded from age 0, as ``basiclife.BasicTerm_SC``'s
    ``mort_table_array`` pads its table, so that the index **is** the age, and
    :func:`mort_age_last` plus one wide.  The ages below the table's first, 0 to 17 as
    shipped, hold NaN, which no formula reads: ``Projection.mort_rate`` refuses an age
    outside the table, naming the point.  Asks :func:`mort_age_first` first, which checks
    the table: each sex runs over every age from the first to the last, one row an age, so
    no cell between them is padding, and each rate is a number from 0 to 1.  Read from the
    one read of the file, :func:`mort_table_rows`, which :mod:`~.WP_UK_S`'s reader sorts.
    """
    mort_age_first()
    last = mort_age_last()
    tbl = mort_table_rows()
    ages = pd.to_numeric(tbl["age"]).to_numpy(dtype="int64")         # noqa: F821
    rates = pd.to_numeric(tbl["mort_rate"]).to_numpy(dtype="float64")  # noqa: F821
    sexes = tbl["sex"].tolist()
    out = np.full((2, last + 1), np.nan)                             # noqa: F821
    for i in range(len(ages)):
        out[("M", "F").index(sexes[i]), ages[i]] = rates[i]
    return out


def lapse_table_array():
    """The annual surrender rate by chassis and policy year, from *lapse_table.csv*:
    float64 [chassis, policy year].

    Row ``c`` is the chassis whose code is ``c``, UWP_bond 0 and CWP_endowment 1, as
    :func:`chassis_code` numbers each point's, and element ``[c, y]`` the rate of its
    policy year ``y``, from 1 to the chassis's last, :func:`lapse_last_year`, which checks
    the table first: each chassis's years run from 1 without a gap.  As wide as the
    table's last year plus one.  Year 0, no policy year, and any year past a chassis's
    last, where the other chassis's runs further, hold NaN, which no formula reads:
    ``Projection.surr_rate_base`` reads a policy year of cover, 1 or more, at most the
    chassis's last, which it reads every later year at, as :mod:`~.WP_UK_S` does.  It asks
    :func:`lapse_last_year` first, by one element, which runs the table's check, and takes
    its width from the table, never from that cell's array (R13).
    """
    lapse_last_year()[0]
    tbl = lapse_table_rows()
    years = pd.to_numeric(tbl["policy_year"]).to_numpy(dtype="int64")  # noqa: F821
    rates = pd.to_numeric(tbl["lapse_rate"]).to_numpy(dtype="float64")  # noqa: F821
    chassis = tbl["chassis"].tolist()
    out = np.full((2, int(years.max()) + 1), np.nan)                 # noqa: F821
    for i in range(len(chassis)):
        out[("UWP_bond", "CWP_endowment").index(chassis[i]), years[i]] = rates[i]
    return out


# ---------------------------------------------------------------------------
# References

model_point_file = "model_point_table_sec.csv"

mort_table_file = "mort_table.csv"

lapse_table_file = "lapse_table.csv"

future_horizon_mth = 120

pd = ("Module", "pandas")

np = ("Module", "numpy")
