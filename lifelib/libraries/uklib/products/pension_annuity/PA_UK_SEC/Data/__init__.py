# modelx: pseudo-python
# This file is part of a modelx model.
# It can be imported as a Python module, but functions defined herein
# are model formulas and may not be executable as standard Python.

"""Input data shared by every by-contract projection.

The two input CSVs are read here, **once per model**, and referenced from
:mod:`~.PA_UK_SEC.Projection` as ``data``. :mod:`~.PA_UK_SEC.Projection` is parameterized
by ``idx``, the position of a model point in the table, so each ``Projection[i]`` is a
separate ItemSpace with its own cells cache; if the readers lived there, every model point
would re-read every file. Holding them in an unparameterized Space reads each file once no
matter how many contracts are projected.

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
without a word, in every column every point's projection reads, and in a column only some
points' read, on those points: a flag that is not True or False, which :mod:`~.PA_UK_S`
reads through ``bool`` so that a blank is True; an age, a guarantee, a frequency or a month
of death that is not a whole number, which :mod:`~.PA_UK_S` truncates with ``int``; a month
of death below 0, which :mod:`~.PA_UK_S` reads as a life that never dies; and an amount, a
percentage or a rate that is not a number in its range. The checks run in turn, and the
first that fails raises, naming the missing column or every point that fails it. Whether a
contract is short of its stop rule, issued at an age the contract allows, and still owes a
payment at the valuation date, are rules of the product, and ``Projection.proj_len`` checks
them, against its own References. A text column :mod:`~.PA_UK_S` validates as it reads it,
``timing``, ``escalation_type``, ``vp_basis`` and ``mort_basis``, is refused by
``Projection``'s decode of it, with :mod:`~.PA_UK_S`'s message.

**A column only some points' projections read is refused by point.** Seven columns are
read by a projection on some points and never on others, and a value no projection can
use is refused by the ``Projection`` accessor of a point whose projection reads it, naming
that point, never here, and never for another point's value (USLIB-SEC-PLAN.md R7,
precised at M23): the sexes, the ratings and the start year, which the table basis reads
and the scenario basis never does; the purchase price, which value protection alone reads;
and the overlap, which a contract with a dependant alone reads. So a contract on the
scenario basis whose rating is blank projects, as :mod:`~.PA_UK_S` projects it, and one on
the table basis whose rating is blank is refused, by its own projection.

**The mortality table is checked before a value of it is read.** Its keys are read by
their value, so an age written ``65.0`` is age 65, and a key that is not whole, text among
them, or is ``2**53`` or more in size, which int64 would hold inexactly, is refused; so are
keys that repeat or leave a gap the projection would read, found from the keys the table
holds, so that a key far from the rest is refused as a gap at once. A rate
that is blank, text, infinite or outside 0 to 1 is refused, whether or not a point reads
it: ``Projection.mort_rate`` caps the annual rate with ``min``, which keeps its first
argument unless a later one compares smaller, and no comparison with NaN holds, so the cap
is written with its bound second and a NaN would stay NaN; but an infinity is a number,
which the cap reads as 1, certain death. The check is :func:`mort_sexes`, which every array,
extent and schedule of the table asks before it reads the table, and each refusal names
the table's lines, the header line 1: the check reads the file as it stands,
:func:`mort_table_rows`, where :mod:`~.PA_UK_S`'s reader, :func:`mort_table`, sorts it, and
with the order would lose the lines. A read beyond the table's ages is refused by the one
``Projection`` cell that reads it, naming the point, where :mod:`~.PA_UK_S`'s lookup raised
``KeyError``.

There are only two files because this product has almost nothing to parameterize: no
lapse table, no charge scale, no bonus rates, no surrender-value schedule. Everything
else is either a contractual rule in the formulas or a single Reference on
``Projection``.

Substituting a licensed basis means replacing ``mort_table.csv`` with a same-schema
file — the SAPS S3/S4 pensioner tables or the PMA16/PFA16 insured-annuitant family,
both restricted to CMI Authorised Users — and setting ``Projection.annuitant_adj`` to 1
so the population-proxy adjustment stops being applied on top of an annuitant table.
No formula changes. Replacing the file changes :mod:`~.PA_UK_S` too, which reads the same
one. A compiled model clears no cache, so there a file's name is set on a package just
imported, before anything is read.

**The vectors.** The readers return what the files hold, and no
:mod:`~.PA_UK_SEC.Projection` cell but ``model_point``, a reporting cell, reads them. The
others read the arrays below instead, one element at a time, a model point's attribute
being the element at its position, ``data.annual_income()[idx]``. That is what lets the
model compile to C, as ``basiclife.BasicTerm_SC`` does: each array is a numpy vector or
table of int64 or float64, which compiles to a typed memoryview, never one of bools,
objects or text, and each check of a table is an int. Each model point column a projection
reads is one vector of the column's own name, read element by element, each value by its
own value whatever type pandas gives the column (USLIB-SEC-PLAN.md R6): ``float()`` of an
amount or a rate, ``int()`` of the ``float()`` of an age, a month count or a year, so that
``2026.0`` written as text is 2026, and a flag True where ``str()`` of its value, lowered,
is ``true``. A column that holds one value pandas cannot read as a number or a flag,
which a point that never reads the column may hold, is read as text throughout, and
there ``bool("False")`` is True and ``int("2026.0")`` refuses, so no element is read
through either. Where a point's value can be one its projection cannot use, a 0/1 vector
beside it, ``<column>_ok``, says whether it is usable. The text the projection branches on is decoded into 0/1 flags, each with a
``has_*`` flag that says the value is one :mod:`~.PA_UK_S` names. The mortality table,
keyed by sex and age, is tabled by schedule, one per sex, and age, padded from age 0, each
point carrying the schedule of each life's sex:

==================================  =======  ================  ===========================
Cells                               dtype    Shape             From
==================================  =======  ================  ===========================
point_id()                          int64    [point]           the table's index
policy_count()                      float64  [point]           ``policy_count``
duration_mth()                      int64    [point]           ``duration_mth``
annuitant_age()                     int64    [point]           ``annuitant_age``
dependant_age()                     int64    [point]           ``dependant_age``, 0 where
                                                               blank
is_joint()                          int64    [point]           ``dependant_present``, 1 on
                                                               True
overlap(), overlap_ok()             int64    [point]           ``overlap``, 1 on True
proportion()                        int64    [point]           ``proportion``, 1 on True
purchase_price()                    float64  [point]           ``purchase_price``
purchase_price_ok()                 int64    [point]           ``purchase_price``, its
                                                               flag
rating_multiplier()                 float64  [point]           ``rating_multiplier``
rating_multiplier_ok()              int64    [point]           ``rating_multiplier``, its
                                                               flag
dependant_rating()                  float64  [point]           ``dependant_rating``
dependant_rating_ok()               int64    [point]           ``dependant_rating``, its
                                                               flag
dependant_pct()                     float64  [point]           ``dependant_pct``
annual_income()                     float64  [point]           ``annual_income``
frequency()                         int64    [point]           ``frequency``
guarantee_months()                  int64    [point]           ``guarantee_months``
vp_pct()                            float64  [point]           ``vp_pct``
start_year(), start_year_ok()       int64    [point]           ``start_year``
escalation_rate()                   float64  [point]           ``escalation_rate``
escalation_rate_ok()                int64    [point]           ``escalation_rate``, its
                                                               flag
has_timing()                        int64    [point]           ``timing``, 1 on arrears or
                                                               advance
is_arrears()                        int64    [point]           the same, 1 on arrears
has_escalation_type()               int64    [point]           ``escalation_type``, 1 on
                                                               one of four
is_level()                          int64    [point]           the same, 1 on level
is_fixed()                          int64    [point]           the same, 1 on fixed
is_lpi5()                           int64    [point]           the same, 1 on lpi5
is_rpi_catchup()                    int64    [point]           the same, 1 on rpi_catchup
has_vp_basis()                      int64    [point]           ``vp_basis``, 1 on
                                                               first_death or
                                                               last_survivor
is_first_death()                    int64    [point]           the same, 1 on first_death
has_mort_basis()                    int64    [point]           ``mort_basis``, 1 on table
                                                               or scenario
is_scenario()                       int64    [point]           the same, 1 on scenario
death_mth_1(), death_mth_1_ok()     int64    [point]           ``death_mth_1``, -1 where
                                                               blank
death_mth_2(), death_mth_2_ok()     int64    [point]           ``death_mth_2``, -1 where
                                                               blank
lives_if_init_1()                   float64  [point]           ``lives_if_init_1``
lives_if_init_2()                   float64  [point]           ``lives_if_init_2``
cum_annuity_all_init()              float64  [point]           ``cum_annuity_all_init``
annual_income_init()                float64  [point]           ``annual_income_init``
rpi_peak_init()                     float64  [point]           ``rpi_peak_init``
rpi_peak_init_ok()                  int64    [point]           ``rpi_peak_init``, its flag
cum_annuity_pp_init()               float64  [point]           ``cum_annuity_pp_init``
cum_annuity_pp_init_ok()            int64    [point]           ``cum_annuity_pp_init``, its
                                                               flag
mort_sexes()                        int      scalar            *mort_table.csv*, checked
mort_table_array()                  float64  [schedule, age]   *mort_table.csv*
mort_age_first(), mort_age_last()   int64    [schedule]        *mort_table.csv*
mort_schedule_1()                   int64    [point]           ``annuitant_sex``, joined;
                                                               0 where not
mort_schedule_2()                   int64    [point]           ``dependant_sex``, joined;
                                                               0 where not
==================================  =======  ================  ===========================

The table is numbered by its sexes, in sorted order, from schedule 1, F 1 and M 2:
:func:`mort_sexes`, the table's one check, an int, gives the count. Schedule 0 is a row of
padding whose first age is 1 and whose last is 0, so that no age lies between them: a life
whose sex the table lacks, a blank among them, has schedule 0, and ``Projection``'s reader
of it, ``mort_schedule``, refuses it, naming the point and the column, where the table
basis first reads it. A point on the scenario basis, or a single-life point's second life,
never reads it. Each schedule's first and last ages are its own sex's, 50 and 115 as
shipped.

**An array is read by element, never whole,** in this Space as in
:mod:`~.PA_UK_SEC.Projection`. The compiler types an array cell as a memoryview only once
it has seen that every use of it, in either Space, is an element read: one ``len()``,
slice, loop over it or numpy call on it anywhere, and the cell compiles as a Python
object. So an array derived here reads the table's column, and a width comes from a table
or a check's int, never from another cell's array. The table's check is one int cell that
its array, its extents and its schedules read first, so that a projection, which reads an
extent first, meets the same refusal as a reader of the array.

**What a point's projection cannot use is refused where it reads it,** by the point's own
``Projection`` cell, naming the point, never here: no point is refused for another's
value, nor for a column its projection never reads (above). Where a vector cannot hold a
value, the vector holds 0 or NaN there and its ``_ok`` flag 0, and the
:mod:`~.PA_UK_SEC.Projection` accessor that reads the element raises:

* text in a column of numbers, which :mod:`~.PA_UK_S`'s ``float()`` or ``int()`` refuses in
  the same cell, on every point, whether or not its projection reads the column;
* an int of ``2**53`` or more in size, which an int64 cannot be trusted to hold, in the
  start year and the two months of death, and a start year ``float()`` cannot read;
* on a point whose projection reads it, a value outside the range ``model_point_table``
  would hold it to on every point: a purchase price that is not a finite number, 0 or more,
  where value protection is elected; a rating that is not a finite number, 1 or more, the
  dependant's on a contract with a dependant, on the table basis; a start year that is not
  a whole number, on the table basis; and an overlap that is not True or False, on a
  contract with a dependant.

Elsewhere a blank stays NaN, as :mod:`~.PA_UK_S` reads it, and a fraction in an int column
truncates, as :mod:`~.PA_UK_S`'s ``int()`` does. A text value of ``timing``,
``escalation_type``, ``vp_basis`` or ``mort_basis`` that is none of :mod:`~.PA_UK_S`'s
values sets no ``has_*`` flag, and the decode that reads the flag raises
:mod:`~.PA_UK_S`'s message there, as at stage ``E``; the values are compared exactly, case
and whitespace included, as :mod:`~.PA_UK_S` compares them. :func:`point_id` refuses a
label that is not a whole number below ``2**53``, naming every label at fault, when a
label is first read: the labels are the table's keys.

**An int64 holds what it is read from.** A float past int64 casts to the least int64
without a word, so a number read into an int64 vector is usable only below ``2**53`` in
size, where the int64 holds :mod:`~.PA_UK_S`'s reading of it exactly. The columns every
reading point's projection reads, ``duration_mth``, the ages, the frequency and the
guarantee, are held below it by :func:`model_point_table`; the start year and the months of
death are held by their ``_ok`` flags.
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
    6. ``dependant_present`` and ``proportion`` are True or False.  pandas reads a column of
       them as booleans, but one blank or one other text leaves the whole column text or
       mixed, and :mod:`~.PA_UK_S`'s ``bool`` reads a blank, NaN, as True;
    7. ``annuitant_age`` is a whole number below ``2**53``, which :mod:`~.PA_UK_S` truncates
       with ``int``;
    8. the contract's: ``annual_income`` an amount, a finite number, 0 or more;
       ``frequency`` 12, 4, 2 or 1, read by its value, which :mod:`~.PA_UK_S` truncates
       with ``int`` before it checks it; ``guarantee_months`` a whole number of months, 0
       or more, below ``2**53``; and ``vp_pct`` a number from 0 to 1, a share of the
       purchase price;
    9. on a contract with a dependant, the dependant's: ``dependant_age`` a whole number
       below ``2**53``, and ``dependant_pct`` a number from 0 to 1, a share of the income.
       A single-life contract's are never read, and are left;
    10. on fixed escalation, ``escalation_rate`` a finite number, 0 or more: the notes'
        menu is non-decreasing, which the dependant's base relies on;
    11. on the scenario basis, each covered life's month of death, ``death_mth_1`` and
        ``death_mth_2``, is blank, the life surviving the projection, or a whole number of
        months, 0 or more, below ``2**53``, read by value, so that ``16.0`` is 16.  The
        table is returned with the two columns as the numbers they were checked as, which
        is what :func:`death_mth_1` and :func:`death_mth_2` read;
    12. ``lives_if_init_1`` and ``lives_if_init_2`` are probabilities, 0 to 1, and
        ``lives_if_init_2`` is 0 on a single-life contract, which covers no second life;
    13. ``cum_annuity_all_init`` is a finite number, 0 or more; on RPI-linked escalation
        ``annual_income_init`` too; on ``rpi_catchup`` ``rpi_peak_init`` is a finite
        number, 1 or more, the peak being at least the latest index; and on RPI-linked
        escalation with value protection on the first death ``cum_annuity_pp_init`` is a
        finite number, 0 or more;
    14. on RPI-linked escalation ``annual_income_init`` is ``annual_income`` or more, to
        half a cent: the LPI's floor and the ratchet never let the income fall below the
        first year's, so a lower one is no history the contract can have, as a negative
        fixed escalation is none.  Half a cent, since an extract may carry the opening
        income to the cent, which takes it up to half a cent from its exact value, while
        the first year's income is the contract's own (USLIB-SEC-PLAN.md D6): 5,399.995
        against 5,400 is read, and 5,399.99 refused;
    15. a contract not yet in payment, ``duration_mth`` 0 or less, holds its values at the
        start date: each covered life alive, nothing paid, the first year's income,
        ``annual_income``, and a peak of 1;
    16. a contract in its first policy year, ``duration_mth`` 1 to 12, has passed no
        anniversary before month 0: on RPI-linked escalation its income of the year under
        way is the first year's, and on ``rpi_catchup`` its peak is 1.  Beyond the first
        year the history is the contract's own, and no rule holds one column to another
        but 14;
    17. on the scenario basis, each covered life's opening status is its death month's:
        1 while the life survives to the valuation date, ``death_mth`` blank or
        ``duration_mth`` or later, and 0 once it has died.  So the scenario's step
        function, which ``lives_if`` follows after the valuation date, agrees with the
        opening value at it.

    The seven columns only some points' projections read, ``annuitant_sex``,
    ``rating_multiplier``, ``purchase_price``, ``start_year``, ``overlap``,
    ``dependant_sex`` and ``dependant_rating``, are not checked here: each is refused by
    point, by the ``Projection`` accessor of a point whose projection reads it (the Space
    docstring).  The column keywords of the ``DataFrame.assign`` that returns the table
    are passed as ``**{...}``, since a keyword named as a cell of this Space,
    ``death_mth_1``, would be rewritten by the export.
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
    for column in ("dependant_present", "proportion"):
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
            ("annual_income", "amount", everyone, ""),
            ("frequency", "frequency", everyone, ""),
            ("guarantee_months", "months", everyone, ""),
            ("vp_pct", "share", everyone, ""),
            ("dependant_age", "whole", joint, " on a contract with a dependant"),
            ("dependant_pct", "share", joint, " on a contract with a dependant"),
            ("escalation_rate", "amount", escalation == "fixed",
             " on fixed escalation")):
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
    # Amounts of money are compared to a cent, so that an extract may carry each to the
    # cent (USLIB-SEC-PLAN.md D6): an opening income so carried is within half a cent of
    # its exact value, and the first year's income, the contract's own, adds nothing.
    income = pd.to_numeric(table["annual_income"], errors="coerce")  # noqa: F821
    bad = table.index[linked & ~(values["annual_income_init"] >= income - 0.005)].tolist()
    if bad:
        raise ValueError(f"{name}: annual_income_init must be annual_income or more, to "
                         f"half a cent, on RPI-linked escalation, whose income never falls "
                         f"below the first year's; it is not at point_id {bad}")
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
    return table.assign(**{"death_mth_1": deaths[1], "death_mth_2": deaths[2]})


def mort_table():
    """The base annual mortality rates by sex and age, from *mort_table.csv*.

    A **[std]** proxy shaped like the ONS UK national life tables, which are period
    tables of *population* mortality and the only freely redistributable UK source.  It
    is **not** an annuitant table: the proper bases are the SAPS S3/S4 pensioner tables
    and the PMA16/PFA16 insured-annuitant family, both restricted to CMI Authorised
    Users.  ``Projection.annuitant_adj`` carries the population-to-annuitant adjustment
    that stands in for the difference, and it is a shape-level placeholder rather than a
    calibration.  :mod:`~.PA_UK_S`'s reader, indexed and sorted as it is, from the one read
    of the file, :func:`mort_table_rows`, for a reader of the table: the projection reads
    :func:`mort_table_array`, which :func:`mort_sexes` checks first.
    """
    return mort_table_rows().set_index(["sex", "age"]).sort_index()


def mort_table_rows():
    """*mort_table.csv* as the file holds it: one row a line, in the file's order.

    The one read of the file.  :func:`mort_sexes` checks it here, so that each refusal
    names the lines at fault, the header line 1, which the sort of :func:`mort_table` would
    lose.
    """
    return pd.read_csv(input_dir() / mort_table_file)                # noqa: F821


def mort_sexes():
    """*mort_table.csv*'s check, an int: the number of its sexes, each a schedule.

    :func:`mort_table_array`, :func:`mort_age_first`, :func:`mort_age_last` and the two
    schedule vectors ask it first, so a table the projection cannot read is refused before
    any value of it is, wherever the projection first reads it.  The check reads the file
    as it stands, :func:`mort_table_rows`, not :func:`mort_table`, which sorts it, so that
    each refusal names the lines at fault, the header line 1.  The rules, each over the
    whole table, the first that fails raising ``ValueError``:

    1. each age is a whole number, read by its value, so ``65.0`` is 65, and below
       ``2**53`` in size, which int64 holds exactly, the check made before the ages are
       cast, where numpy would cast a larger float to the least int64 without a word;
    2. each sex is M or F, the codes the model point table holds;
    3. each sex runs over the table's ages from the first to the last, one row an age,
       none below 0: the projection reads a rate at each attained age a life reaches.
       Every fault is named in one message: an age below 0 and an age a sex repeats each
       with its lines, and each span of ages a sex lacks, found in one pass over the ages
       each sex holds, so that a key far from the rest costs no more than the rows;
    4. each ``mort_rate`` is a number from 0 to 1, a probability, read by the cap.

    So the table holds both sexes, F and M, over one span of ages, and each schedule's
    extents are the table's: the first age, 50 as shipped, and the last, 115.
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
    return int(tbl["sex"].nunique())


def mort_table_array():
    """*mort_table.csv*'s rates, float64 by schedule and attained age, ``[s, x]``.

    Schedule ``s`` is the ``s``-th of the table's sexes in sorted order, from 1, F 1 and
    M 2; row 0, and every age below a sex's first, is NaN padding, which
    ``Projection.mort_rate_base_at`` never reads, since it checks the age against
    :func:`mort_age_first` and :func:`mort_age_last` first.
    """
    n = mort_sexes()
    rows = mort_table_rows()
    rows = rows.assign(age=pd.to_numeric(rows["age"]).astype("int64"))  # noqa: F821
    out = np.full((n + 1, int(rows["age"].max()) + 1), np.nan)       # noqa: F821
    s = 0
    for _, part in rows.groupby("sex", sort=True):
        s += 1
        out[s, part["age"].to_numpy()] = pd.to_numeric(              # noqa: F821
            part["mort_rate"]).to_numpy(dtype="float64")
    return out


def mort_age_first():
    """Each mortality schedule's first age, int64 by schedule: 1 on schedule 0."""
    out = np.ones(mort_sexes() + 1, dtype="int64")                  # noqa: F821
    rows = mort_table_rows()
    rows = rows.assign(age=pd.to_numeric(rows["age"]).astype("int64"))  # noqa: F821
    s = 0
    for _, part in rows.groupby("sex", sort=True):
        s += 1
        out[s] = int(part["age"].min())
    return out


def mort_age_last():
    """Each mortality schedule's last age, int64 by schedule: 0 on schedule 0, so that no
    age lies between its extents."""
    out = np.zeros(mort_sexes() + 1, dtype="int64")                 # noqa: F821
    rows = mort_table_rows()
    rows = rows.assign(age=pd.to_numeric(rows["age"]).astype("int64"))  # noqa: F821
    s = 0
    for _, part in rows.groupby("sex", sort=True):
        s += 1
        out[s] = int(part["age"].max())
    return out


def mort_schedule_1():
    """The mortality schedule of each point's ``annuitant_sex``, int64 by point.

    The sex's number in :func:`mort_table_array`, matched as :mod:`~.PA_UK_S`'s ``.loc``
    matches it, and 0 where the table lacks it, a blank among them: a point on the
    scenario basis never reads the table, and one on the table basis is refused where
    ``Projection.mort_schedule`` first reads schedule 0.
    """
    mort_sexes()
    keys = sorted(mort_table_rows()["sex"].unique())
    number = {}
    for i in range(len(keys)):
        number[keys[i]] = i + 1
    sexes = model_point_table()["annuitant_sex"].tolist()
    out = np.zeros(len(sexes), dtype="int64")                        # noqa: F821
    for i in range(len(sexes)):
        out[i] = number.get(sexes[i], 0)
    return out


def mort_schedule_2():
    """The mortality schedule of each point's ``dependant_sex``, int64 by point, as
    :func:`mort_schedule_1`: 0 on a single-life point's blank, which nothing reads."""
    mort_sexes()
    keys = sorted(mort_table_rows()["sex"].unique())
    number = {}
    for i in range(len(keys)):
        number[keys[i]] = i + 1
    sexes = model_point_table()["dependant_sex"].tolist()
    out = np.zeros(len(sexes), dtype="int64")                        # noqa: F821
    for i in range(len(sexes)):
        out[i] = number.get(sexes[i], 0)
    return out


def point_id():
    """The model points' labels, int64 by position: the table's ``point_id`` index.

    The label ``Projection.point_id`` reports for a position, and the one every refusal
    names.  Read by value, so that a label written ``3.0`` is 3, and refused when a label
    is first read, naming every label at fault, where one is not a whole number, text and
    a blank among them, or is ``2**53`` or more in size: the labels are the table's keys,
    as in the family's other compiled models.  A projection that names no point reads no
    label, and runs.
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


def policy_count():
    """The ``policy_count`` column, float64 by point, as :func:`model_point_table` checked
    it."""
    return pd.to_numeric(model_point_table()["policy_count"]).to_numpy(  # noqa: F821
        dtype="float64")


def duration_mth():
    """The ``duration_mth`` column, int64 by point: ``int()`` of each value, which
    :func:`model_point_table` has held to a whole number below ``2**53``, read by value, so
    that ``12.0`` is 12."""
    values = model_point_table()["duration_mth"].tolist()
    out = np.zeros(len(values), dtype="int64")                       # noqa: F821
    for i in range(len(values)):
        out[i] = int(float(values[i]))
    return out


def annuitant_age():
    """The ``annuitant_age`` column, int64 by point: ``int()`` of each value, which
    :func:`model_point_table` has held to a whole number below ``2**53``."""
    values = model_point_table()["annuitant_age"].tolist()
    out = np.zeros(len(values), dtype="int64")                       # noqa: F821
    for i in range(len(values)):
        out[i] = int(float(values[i]))
    return out


def dependant_age():
    """The ``dependant_age`` column, int64 by point: ``int()`` of each value on a contract
    with a dependant, which :func:`model_point_table` has held to a whole number below
    ``2**53``, and 0 on a single-life contract, which ``Projection.age_at_entry`` never
    reads there."""
    table = model_point_table()
    values = table["dependant_age"].tolist()
    joint = table["dependant_present"].tolist()
    out = np.zeros(len(values), dtype="int64")                       # noqa: F821
    for i in range(len(values)):
        if str(joint[i]).lower() == "true":
            out[i] = int(float(values[i]))
    return out


def is_joint():
    """The ``dependant_present`` column, int64 by point: 1 where the value is True, read by
    its value, ``str()`` of it lowered being ``true``, on values :func:`model_point_table`
    has held to True or False, as :mod:`~.PA_UK_S`'s ``bool()`` reads a True or a False.
    ``bool()`` itself would read the text ``False`` as True, and pandas leaves a column as
    text where one value is neither, ``tRUE`` among them, which the check reads as True."""
    values = model_point_table()["dependant_present"].tolist()
    out = np.zeros(len(values), dtype="int64")                       # noqa: F821
    for i in range(len(values)):
        out[i] = 1 if str(values[i]).lower() == "true" else 0
    return out


def overlap():
    """The ``overlap`` column, int64 by point: 1 where the value is True, read by its
    value as :func:`is_joint` reads its column.  A single-life contract may hold any text
    there, which it never reads, and then pandas reads the whole column as text, where
    ``bool()`` would read every joint contract's ``False`` as True."""
    values = model_point_table()["overlap"].tolist()
    out = np.zeros(len(values), dtype="int64")                       # noqa: F821
    for i in range(len(values)):
        out[i] = 1 if str(values[i]).lower() == "true" else 0
    return out


def overlap_ok():
    """1 where the point's projection may read its ``overlap``: 0 on a contract with a
    dependant, the one reader, where the value is not True or False, which
    :mod:`~.PA_UK_S`'s ``bool`` would read as True were it blank."""
    table = model_point_table()
    values = table["overlap"].tolist()
    joint = table["dependant_present"].tolist()
    out = np.zeros(len(values), dtype="int64")                       # noqa: F821
    for i in range(len(values)):
        if (str(values[i]).lower() in ("true", "false")
                or not str(joint[i]).lower() == "true"):
            out[i] = 1
    return out


def proportion():
    """The ``proportion`` column, int64 by point: 1 where the value is True, read by its
    value as :func:`is_joint` reads its column, on values :func:`model_point_table` has
    held to True or False."""
    values = model_point_table()["proportion"].tolist()
    out = np.zeros(len(values), dtype="int64")                       # noqa: F821
    for i in range(len(values)):
        out[i] = 1 if str(values[i]).lower() == "true" else 0
    return out


def purchase_price():
    """The ``purchase_price`` column, float64 by point: ``float()`` of each value, NaN on
    text."""
    values = model_point_table()["purchase_price"].tolist()
    out = np.full(len(values), np.nan)                               # noqa: F821
    for i in range(len(values)):
        try:
            out[i] = float(values[i])
        except (TypeError, ValueError):
            pass
    return out


def purchase_price_ok():
    """1 where the point's projection may read its ``purchase_price``.

    0 on text, which ``float()`` refuses, and where value protection is elected, ``vp_pct``
    above 0, the one reader, on a price that is not a finite number, 0 or more, which the
    balance ``max(0, v P - G)`` would read as a number.  A blank stays NaN on a contract
    without value protection, which never reads it.
    """
    table = model_point_table()
    values = table["purchase_price"].tolist()
    shares = pd.to_numeric(table["vp_pct"], errors="coerce").tolist()  # noqa: F821
    out = np.zeros(len(values), dtype="int64")                       # noqa: F821
    for i in range(len(values)):
        try:
            v = float(values[i])
        except (TypeError, ValueError):
            continue
        if not shares[i] > 0.0 or (v >= 0.0 and v < float("inf")):
            out[i] = 1
    return out


def rating_multiplier():
    """The ``rating_multiplier`` column, float64 by point: ``float()`` of each value, NaN
    on text."""
    values = model_point_table()["rating_multiplier"].tolist()
    out = np.full(len(values), np.nan)                               # noqa: F821
    for i in range(len(values)):
        try:
            out[i] = float(values[i])
        except (TypeError, ValueError):
            pass
    return out


def rating_multiplier_ok():
    """1 where the point's projection may read its ``rating_multiplier``.

    0 on text, and on the table basis, the one reader, on a rating that is not a finite
    number, 1 or more, the notes' ``theta >= 1``: the mortality cap puts its bound second,
    so a missing rating would stay missing there, and an infinite one read as certain
    death.  The scenario basis never reads it.
    """
    table = model_point_table()
    values = table["rating_multiplier"].tolist()
    basis = table["mort_basis"].tolist()
    out = np.zeros(len(values), dtype="int64")                       # noqa: F821
    for i in range(len(values)):
        try:
            v = float(values[i])
        except (TypeError, ValueError):
            continue
        if not basis[i] == "table" or (v >= 1.0 and v < float("inf")):
            out[i] = 1
    return out


def dependant_rating():
    """The ``dependant_rating`` column, float64 by point: ``float()`` of each value, NaN on
    text."""
    values = model_point_table()["dependant_rating"].tolist()
    out = np.full(len(values), np.nan)                               # noqa: F821
    for i in range(len(values)):
        try:
            out[i] = float(values[i])
        except (TypeError, ValueError):
            pass
    return out


def dependant_rating_ok():
    """1 where the point's projection may read its ``dependant_rating``: as
    :func:`rating_multiplier_ok`, on a contract with a dependant on the table basis, the
    one reader.  A single-life contract never reads it."""
    table = model_point_table()
    values = table["dependant_rating"].tolist()
    basis = table["mort_basis"].tolist()
    joint = table["dependant_present"].tolist()
    out = np.zeros(len(values), dtype="int64")                       # noqa: F821
    for i in range(len(values)):
        try:
            v = float(values[i])
        except (TypeError, ValueError):
            continue
        if (not (basis[i] == "table" and str(joint[i]).lower() == "true")
                or (v >= 1.0 and v < float("inf"))):
            out[i] = 1
    return out


def dependant_pct():
    """The ``dependant_pct`` column, float64 by point: ``float()`` of each value, which
    :func:`model_point_table` has held to a number from 0 to 1 on a contract with a
    dependant; NaN on a single-life contract's text, which ``Projection.dependant_pct``
    never reads there."""
    values = model_point_table()["dependant_pct"].tolist()
    out = np.full(len(values), np.nan)                               # noqa: F821
    for i in range(len(values)):
        try:
            out[i] = float(values[i])
        except (TypeError, ValueError):
            pass
    return out


def annual_income():
    """The ``annual_income`` column, A(1), float64 by point, as :func:`model_point_table`
    checked it."""
    return pd.to_numeric(model_point_table()["annual_income"]).to_numpy(  # noqa: F821
        dtype="float64")


def frequency():
    """The ``frequency`` column, int64 by point: ``int()`` of each value, which
    :func:`model_point_table` has held to 12, 4, 2 or 1."""
    values = model_point_table()["frequency"].tolist()
    out = np.zeros(len(values), dtype="int64")                       # noqa: F821
    for i in range(len(values)):
        out[i] = int(float(values[i]))
    return out


def guarantee_months():
    """The ``guarantee_months`` column, int64 by point: ``int()`` of each value, which
    :func:`model_point_table` has held to a whole number of months, 0 or more, below
    ``2**53``."""
    values = model_point_table()["guarantee_months"].tolist()
    out = np.zeros(len(values), dtype="int64")                       # noqa: F821
    for i in range(len(values)):
        out[i] = int(float(values[i]))
    return out


def vp_pct():
    """The ``vp_pct`` column, float64 by point, as :func:`model_point_table` checked it."""
    return pd.to_numeric(model_point_table()["vp_pct"]).to_numpy(    # noqa: F821
        dtype="float64")


def start_year():
    """The ``start_year`` column, int64 by point: ``int()`` of the ``float()`` of each value,
    read by its value, so that ``2026.0`` is 2026 whether pandas reads the column as numbers
    or as text, and 0 where :func:`start_year_ok` is 0 for want of a number below ``2**53``
    in size."""
    values = model_point_table()["start_year"].tolist()
    out = np.zeros(len(values), dtype="int64")                       # noqa: F821
    for i in range(len(values)):
        try:
            v = float(values[i])
        except (TypeError, ValueError):
            continue
        if abs(v) < 2.0 ** 53:
            out[i] = int(v)
    return out


def start_year_ok():
    """1 where the point's projection may read its ``start_year``.

    0 where ``float()`` cannot read it as a number below ``2**53`` in size, text, a blank
    and an infinity among them; and on the table basis, the one reader, where it is not a
    whole number, which :mod:`~.PA_UK_S` truncates.  Read by value, as :func:`start_year`
    reads it, so that a year written ``2026.0`` reads on every point when another point,
    which never reads its year, holds text there and pandas reads the column as text.  The
    scenario basis never reads it, and there a fraction truncates, as ``int()`` does.
    """
    table = model_point_table()
    values = table["start_year"].tolist()
    basis = table["mort_basis"].tolist()
    out = np.zeros(len(values), dtype="int64")                       # noqa: F821
    for i in range(len(values)):
        try:
            v = float(values[i])
        except (TypeError, ValueError):
            continue
        if abs(v) < 2.0 ** 53 and (not basis[i] == "table" or v % 1 == 0):
            out[i] = 1
    return out


def escalation_rate():
    """The ``escalation_rate`` column, g, float64 by point: ``float()`` of each value, NaN
    on text."""
    values = model_point_table()["escalation_rate"].tolist()
    out = np.full(len(values), np.nan)                               # noqa: F821
    for i in range(len(values)):
        try:
            out[i] = float(values[i])
        except (TypeError, ValueError):
            pass
    return out


def escalation_rate_ok():
    """1 where ``float()`` reads the point's ``escalation_rate``: 0 on text alone.

    :func:`model_point_table` holds the rate on fixed escalation, the one reader; elsewhere
    a blank stays NaN, as :mod:`~.PA_UK_S` reads it, and only a direct call reads it.
    """
    values = model_point_table()["escalation_rate"].tolist()
    out = np.zeros(len(values), dtype="int64")                       # noqa: F821
    for i in range(len(values)):
        try:
            float(values[i])
        except (TypeError, ValueError):
            continue
        out[i] = 1
    return out


def has_timing():
    """1 where the point's ``timing`` is ``arrears`` or ``advance``, compared exactly."""
    return model_point_table()["timing"].isin(["arrears", "advance"]).to_numpy(
        dtype="int64")


def is_arrears():
    """1 where the point's ``timing`` is ``arrears``."""
    return (model_point_table()["timing"] == "arrears").to_numpy(dtype="int64")


def has_escalation_type():
    """1 where the point's ``escalation_type`` is one of :mod:`~.PA_UK_S`'s four, compared
    exactly."""
    return model_point_table()["escalation_type"].isin(
        ["level", "fixed", "rpi_catchup", "lpi5"]).to_numpy(dtype="int64")


def is_level():
    """1 where the point's ``escalation_type`` is ``level``."""
    return (model_point_table()["escalation_type"] == "level").to_numpy(dtype="int64")


def is_fixed():
    """1 where the point's ``escalation_type`` is ``fixed``."""
    return (model_point_table()["escalation_type"] == "fixed").to_numpy(dtype="int64")


def is_lpi5():
    """1 where the point's ``escalation_type`` is ``lpi5``."""
    return (model_point_table()["escalation_type"] == "lpi5").to_numpy(dtype="int64")


def is_rpi_catchup():
    """1 where the point's ``escalation_type`` is ``rpi_catchup``."""
    return (model_point_table()["escalation_type"] == "rpi_catchup").to_numpy(
        dtype="int64")


def has_vp_basis():
    """1 where the point's ``vp_basis`` is ``first_death`` or ``last_survivor``."""
    return model_point_table()["vp_basis"].isin(
        ["first_death", "last_survivor"]).to_numpy(dtype="int64")


def is_first_death():
    """1 where the point's ``vp_basis`` is ``first_death``."""
    return (model_point_table()["vp_basis"] == "first_death").to_numpy(dtype="int64")


def has_mort_basis():
    """1 where the point's ``mort_basis`` is ``table`` or ``scenario``."""
    return model_point_table()["mort_basis"].isin(["table", "scenario"]).to_numpy(
        dtype="int64")


def is_scenario():
    """1 where the point's ``mort_basis`` is ``scenario``."""
    return (model_point_table()["mort_basis"] == "scenario").to_numpy(dtype="int64")


def death_mth_1():
    """The annuitant's scenario month of death, int64 by point: -1 where blank.

    The ``death_mth_1`` column as :func:`model_point_table` returns it, the numbers it
    checked, a whole number of policy months, 0 or more, or blank on the scenario basis,
    the blank being :mod:`~.PA_UK_S`'s survivor, which ``Projection.death_mth`` reads as
    -1; elsewhere text is blank there too, and a fraction truncates; 0 where
    :func:`death_mth_1_ok` is 0.
    """
    values = model_point_table()["death_mth_1"].tolist()
    out = np.zeros(len(values), dtype="int64")                       # noqa: F821
    for i in range(len(values)):
        v = values[i]
        if not v == v:
            out[i] = -1
        elif abs(v) < 2 ** 53:
            out[i] = int(v)
    return out


def death_mth_1_ok():
    """1 where :func:`death_mth_1` holds the point's month: blank, or below ``2**53``."""
    values = model_point_table()["death_mth_1"].tolist()
    out = np.zeros(len(values), dtype="int64")                       # noqa: F821
    for i in range(len(values)):
        v = values[i]
        if not v == v or abs(v) < 2 ** 53:
            out[i] = 1
    return out


def death_mth_2():
    """The dependant's scenario month of death, int64 by point: -1 where blank, as
    :func:`death_mth_1`."""
    values = model_point_table()["death_mth_2"].tolist()
    out = np.zeros(len(values), dtype="int64")                       # noqa: F821
    for i in range(len(values)):
        v = values[i]
        if not v == v:
            out[i] = -1
        elif abs(v) < 2 ** 53:
            out[i] = int(v)
    return out


def death_mth_2_ok():
    """1 where :func:`death_mth_2` holds the point's month: blank, or below ``2**53``."""
    values = model_point_table()["death_mth_2"].tolist()
    out = np.zeros(len(values), dtype="int64")                       # noqa: F821
    for i in range(len(values)):
        v = values[i]
        if not v == v or abs(v) < 2 ** 53:
            out[i] = 1
    return out


def lives_if_init_1():
    """The ``lives_if_init_1`` column, float64 by point: checked by
    :func:`model_point_table`."""
    return pd.to_numeric(model_point_table()["lives_if_init_1"]).to_numpy(  # noqa: F821
        dtype="float64")


def lives_if_init_2():
    """The ``lives_if_init_2`` column, float64 by point: checked by
    :func:`model_point_table`."""
    return pd.to_numeric(model_point_table()["lives_if_init_2"]).to_numpy(  # noqa: F821
        dtype="float64")


def cum_annuity_all_init():
    """The ``cum_annuity_all_init`` column, float64 by point: checked by
    :func:`model_point_table`."""
    return pd.to_numeric(model_point_table()["cum_annuity_all_init"]).to_numpy(  # noqa
        dtype="float64")


def annual_income_init():
    """The ``annual_income_init`` column, float64 by point: checked by
    :func:`model_point_table` on RPI-linked escalation, the one reader, and NaN elsewhere
    on text, which ``Projection.annual_income_init`` never reads there."""
    values = model_point_table()["annual_income_init"].tolist()
    out = np.full(len(values), np.nan)                               # noqa: F821
    for i in range(len(values)):
        try:
            out[i] = float(values[i])
        except (TypeError, ValueError):
            pass
    return out


def rpi_peak_init():
    """The ``rpi_peak_init`` column, float64 by point: ``float()`` of each value, NaN on
    text."""
    values = model_point_table()["rpi_peak_init"].tolist()
    out = np.full(len(values), np.nan)                               # noqa: F821
    for i in range(len(values)):
        try:
            out[i] = float(values[i])
        except (TypeError, ValueError):
            pass
    return out


def rpi_peak_init_ok():
    """1 where ``float()`` reads the point's ``rpi_peak_init``: 0 on text alone.

    :func:`model_point_table` holds the peak on ``rpi_catchup``, the one reader; elsewhere
    a blank stays NaN, and only a direct call reads it.
    """
    values = model_point_table()["rpi_peak_init"].tolist()
    out = np.zeros(len(values), dtype="int64")                       # noqa: F821
    for i in range(len(values)):
        try:
            float(values[i])
        except (TypeError, ValueError):
            continue
        out[i] = 1
    return out


def cum_annuity_pp_init():
    """The ``cum_annuity_pp_init`` column, float64 by point: ``float()`` of each value, NaN
    on text."""
    values = model_point_table()["cum_annuity_pp_init"].tolist()
    out = np.full(len(values), np.nan)                               # noqa: F821
    for i in range(len(values)):
        try:
            out[i] = float(values[i])
        except (TypeError, ValueError):
            pass
    return out


def cum_annuity_pp_init_ok():
    """1 where ``float()`` reads the point's ``cum_annuity_pp_init``: 0 on text alone.

    :func:`model_point_table` holds it on RPI-linked escalation with value protection on
    the first death, the one reader; elsewhere a blank stays NaN, and only a direct call
    reads it.
    """
    values = model_point_table()["cum_annuity_pp_init"].tolist()
    out = np.zeros(len(values), dtype="int64")                       # noqa: F821
    for i in range(len(values)):
        try:
            float(values[i])
        except (TypeError, ValueError):
            continue
        out[i] = 1
    return out


# ---------------------------------------------------------------------------
# References

model_point_file = "model_point_table_sec.csv"

mort_table_file = "mort_table.csv"

future_horizon_mth = 120

pd = ("Module", "pandas")

np = ("Module", "numpy")
