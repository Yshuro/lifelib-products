# modelx: pseudo-python
# This file is part of a modelx model.
# It can be imported as a Python module, but functions defined herein
# are model formulas and may not be executable as standard Python.

"""The by-policy projection of the :mod:`~.WP_UK_SEC` model; holds all formulas.

The Space is parameterized by ``idx``, the position of a model point in the table and in
every :mod:`~.WP_UK_SEC.Data` vector, as ``basiclife.BasicTerm_SC`` is: ``Projection[0]``
is an ItemSpace projecting the table's first row, model point 1, the twin of
:mod:`~.WP_UK_S`'s worked-example bond, in force at the valuation date five years after
issue, and :func:`point_id` is its label::

    >>> Projection[0].result_cf()          # one row per month from the valuation date
    >>> Projection[0].result_pols()        # the counts behind it
    >>> Projection[0].point_id()           # 1, the row's point_id
    >>> Projection.idx = 6                 # or switch the default, before it computes

Compiled, no cache is ever cleared: set ``idx``, like every Reference, on a model just
imported, before anything is computed, or project through ``Projection[i]``. modelx
recomputes what a Reference reaches when it is set; a compiled ItemSpace takes the
References when it is made and keeps every value it has computed until it is deleted,
and the base ``Projection`` and ``Data`` keep theirs for good.

Any ``idx`` makes an ItemSpace, and none is refused here. ``Projection[-1]`` reads every
vector at its last element, as numpy and a compiled memoryview both do, so it is the
table's last point, under that point's own :func:`point_id`; an ``idx`` past the last
row raises ``IndexError`` at its first read of a vector, which modelx reports inside its
``FormulaError``.

This is :mod:`~.WP_UK_S` taught to run in force at a valuation date, as lifelib's
``basiclife.BasicTerm_SE`` extends ``basiclife.BasicTerm_S``, and then made to compile, as
``basiclife.BasicTerm_SC`` is made from ``basiclife.BasicTerm_S``. A formula of
:mod:`~.WP_UK_S` is rewritten where it depends on where the projection starts, where it
must answer for a month outside cover, where it read a policy month as ``t``, or where a
chain of its cells ran more than one cell a month; every other formula is
:mod:`~.WP_UK_S`'s own, the cap on mortality, ``min(q, 1.0)``, among them.
``products/with_profits/model-sec.md`` lists the rewritten cells with the reason for each.
Making it compile changed how each cell reads its inputs and spells its codes, and how its
eight chains reach back in time, and no number: every model point attribute a projection
cell uses is read as a number from a ``Data`` vector, every table as an array indexed by
integers, the guarantee dates as a flag by policy year, every timing and kind is an int
code (*Codes*, below), and the chassis and the sex are decoded into the numbers a formula
branches on and reads by.

.. rubric:: A monthly grid with an annual discretion cycle

This is the one thing to hold on to about this model. The notes' rationale for an annual
grid was that **bonus declarations are annual** — they are the governing act of
discretion, and a declaration permanently hardens the guarantee. That is a fact about
the product, not about the grid, and it survives the move to monthly steps intact: the
declaration still fires once a policy year, in its twelfth month,
:func:`is_declaration_month`. Everything continuous runs monthly around it — the fund
return, the charges, the mortality charge, the decrements, the smoothed payout, the
final bonus and the market value reduction — and everything discretionary stays where
the contract puts it.

So :func:`unit_price` and :func:`guar_benefit_pp` are **step functions** of the policy
year, flat for eleven months and stepping in the twelfth; :func:`cost_of_bonus_pp` and
:func:`shareholder_transfer_pp` are nil in eleven months out of twelve;
:func:`bonus_rate` is the **annual** rate declared for the policy year the month falls
in, and the ±1% gradual-change discipline is applied once a year to it rather than
twelve times. :func:`check_declaration_is_annual` asserts all of that, because the way
this conversion goes wrong quietly is by compounding an annual bonus rate monthly: the
model still runs, the roll-forwards still close, and the guarantee is an order of
magnitude too large a decade later.

The annual rates the assumptions are quoted in — the fund return, the annual management
charge, the guarantee charge, mortality, surrender, expense inflation and the ±10%
smoothing cap — are converted with the effective ``(1 + r)^(1/12)`` and
``1 - (1 - r)^(1/12)`` forms **[std]**, so twelve months compound back to the annual
figure exactly and the basis does not move with the grid.

Two things the monthly grid genuinely says better than the annual one, and both are
about the **guarantee date**. First, a guarantee date is a date: an exit in that month
is MVR-free and an exit in the other eleven months of the same policy year is not, which
:func:`mvr_applied_pp` can now express. Second, the anti-selective encashment that
follows from it is a dated exercise rather than a year-long elevation of the surrender
rate, which is :func:`guarantee_exercise`. That second change moves an assumption's
shape and not merely its frequency, and its docstring says so.

.. rubric:: Input data

Inputs are **external files**: plain CSVs living in the model folder's parent
directory, ``products/with_profits/``, read at run time rather than stored inside the
model. The model folder therefore holds nothing but formulas — no ``_data/``, no
IOSpec, no embedded values — so a diff of the model shows logic changes only, and an
input can be edited or swapped without rewriting the model. This follows
``annuallife.TradLife_A``; contrast ``basiclife.BasicTerm_S``, which keeps its inputs
*inside* the model through modelx's IOSpec machinery.

The consequence worth knowing: **the model is not portable on its own.** Copying the
``WP_UK_SEC`` folder without its parent's CSVs produces a model that reads and then fails
on first evaluation.

The two assumption tables are the files :mod:`~.WP_UK_S` reads, read in place; the model
point table is this model's own. Each table has a filename Reference and a reader Cells,
both on :mod:`~.WP_UK_SEC.Data`, reached here through the ``data`` Reference:

======================  ==============================  ==========================
Reference               Cells                           File
======================  ==============================  ==========================
model_point_file        data.model_point_table()        model_point_table_sec.csv
mort_table_file         data.mort_table()               mort_table.csv
lapse_table_file        data.lapse_table()              lapse_table.csv
======================  ==============================  ==========================

.. rubric:: Two clocks

``t`` counts months from the **valuation date**, 0-based, the clock
``basiclife.BasicTerm_SE`` runs on: ``t = 0`` is the valuation month for every model
point, however old the policy, month ``t`` runs from time ``t`` to time ``t + 1``, and the
frame is ``t = 0 .. proj_len() - 1``, where :func:`proj_len` counts the months from the
valuation date to the end of the projection: the endowment's maturity, the bond's
limiting age, or the month a withdrawal election exhausts the bond's units, whichever
comes first. Row ``t`` is the same month for every point, so the frames of a block line
up and sum row by row.

``duration_mth(t)`` counts **policy months**, the months the policy has been in force at
time ``t``: ``duration_mth(t) = duration_mth_init() + t``, where
:func:`duration_mth_init` is read from the model point — positive for a policy in force at
the valuation date, 0 for one issued at it, ``-k`` for one issued ``k`` months later, at
most ten years later. Everything contractual reads it: the completed policy years
``duration(t) = duration_mth(t) // 12``, the contractual 1-based label
``policy_year(t) = duration(t) + 1``, the lapse table's key and the guarantee dates', the
attained age ``age(t) = age_at_entry() + duration(t)``, the mortality table's, the
declaration in the twelfth month of each policy year, the guarantee-imminent window, the
single premium in the issue month, and the end of cover, :func:`cover_end_mth`. The
worked example's bond, model point 1, is in its sixth policy year at attained age 60 at
``t = 0``, where :mod:`~.WP_UK_S` opens it at its own ``t = 60``.

One input reads the valuation clock instead: expense inflation,
``inflation_factor(t) = (1 + inflation_rate) ** (t // 12)``, stepping on each anniversary
of the valuation date, so that the maintenance charge is in valuation-date pounds for every
point alike (USLIB-SEC-PLAN.md D7; UKLIB-SEC-PLAN.md §9 item 4). :mod:`~.WP_UK_S` inflates
from issue, so its in-force points carry five and twenty years of it at their first
projected month. The fund return and the bonus rate are levels of the model point, the
same on either clock. WP has no acquisition expense and no commission.

On a point issued at ``t = 0`` the two clocks coincide and this model computes what
:mod:`~.WP_UK_S` computes: every cell the two share agrees at every argument
:mod:`~.WP_UK_S` evaluates in its sweep, but for those whose meaning changed —
``pols_if_init``, now the count already in force at the valuation date, ``model_point``, a
row of another table, and :func:`fund_exhaust_mth`, whose "never" is no longer 0 (*The
frame ends where the units do*, below). ``tests/test_model_conventions_uk.py`` asserts it
cell by cell.

.. rubric:: Counts

``pols_if(t)`` is the count that weights row ``t``: ``pols_if_at(t, BEF_DECR)``, the
count carried in from ``t - 1`` (``BEF_NB``) plus the month's new business,
:func:`pols_new_biz`, before the month's decrements. A point in force at the valuation
date opens with :func:`pols_if_init`, its ``policy_count``; one issued at or after the
valuation date opens with none, and takes its ``policy_count`` as new business in its
issue month. The recursion's base is :func:`t_entry`, the first month on the books, and
nothing is counted outside the frame: before issue every count, and so every cash flow, is
zero, and the survivors of the frame's last month leave as :func:`pols_maturity`, paid on
the endowment's maturity and on the bond's forced encashment, and paid nothing at the
bond's limiting age. :mod:`~.WP_UK_S`'s three timings are kept, ``BEF_DECR``,
``BEF_SURR`` and ``AFT_DECR``, and ``BEF_NB`` is the one running in force adds.

.. rubric:: The opening state

A policy in force carries, beside its count, the state :mod:`~.WP_UK_S` carries into the
month it is valued at, each per policy, so that the count is the one weight on every
flow, and each measured at the valuation instant, the start of month 0, before any
month-0 event, which is :mod:`~.WP_UK_S`'s close of the month before:

* :func:`asset_share_init`, the asset share, the retrospective accumulation, floored at
  0, as :mod:`~.WP_UK_S` floors it;
* on the bond, :func:`units_init` and :func:`unit_price_init`, the units held and the
  price the declarations have raised the seed price to; the face value is their product;
* on the endowment, :func:`attaching_bonus_init`, the reversionary bonuses already
  attaching, so that the guarantee is the sum assured plus it;
* :func:`smoothed_payout_init`, the payout the smoothing cap works from, which is 0 where
  the asset share has floored at 0, the corridor holding the payout to it;
* :func:`bonus_rate_init`, the rate of the policy year under way;
* the two cumulants :mod:`~.WP_UK_S` restarts at 0 where its frame opens:
  :func:`guar_charge_cum_pp_init`, the guarantee charges taken since issue, which the
  charge's lifetime cap of 2% of the asset share is measured against, and
  :func:`smoothing_account_init`, the estate's smoothing and guarantee cost on the exits
  since issue, per policy in force.

Each is history, read from the model point, never recomputed from a Reference, which is
an assumption from the valuation date on: a fund return, a charge or a smoothing rule
changed at the valuation date reaches back over no month already run. A policy not yet in
force carries none of them; its seed price and its first year's bonus rate are issue
values. No balance is needed at a second instant: a declaration costs the month's own
opening values, and no annual quantity reads the balance entering the policy year.

.. rubric:: Codes

What :mod:`~.WP_UK_S` spells as text, a timing, a kind or a chassis, is here an int
Reference named as the text it replaces, so that every cell takes and returns C numbers.
A call site reads as it did, less the quotes: ``pols_if_at(t, BEF_DECR)``,
``asset_share_at(t, AFT_MC)``, ``claims(t, DEATH)``.

==============  =====  ==========================================================
Reference       Value  Meaning
==============  =====  ==========================================================
BEF_NB          0      :func:`pols_if_at`: the count carried in from month t - 1
BEF_DECR        1      :func:`pols_if_at`: that count plus month t's new business
BEF_SURR        2      :func:`pols_if_at`: after the month's deaths, before its
                       surrenders
AFT_DECR        3      :func:`pols_if_at`: the end of the month
BEF_PREM        4      :func:`asset_share_at`: the balance the month opens with
BEF_RETURN      5      :func:`asset_share_at`: after the premium and the withdrawal
AFT_RETURN      6      :func:`asset_share_at`: after the month's fund return
AFT_CHARGE      7      :func:`asset_share_at`: after the two charges
AFT_ST          8      :func:`asset_share_at`: after the shareholder transfer
AFT_MC          9      :func:`asset_share_at`: after the mortality charge and the
                       estate distribution, before the floor at 0
DEATH           0      :func:`claim_pp`, :func:`smoothing_cost_pp` and
                       :func:`claims`: a death
SURRENDER       1      the same three: a surrender, a guarantee date's among them
GUARANTEE       2      :func:`claim_pp` and :func:`smoothing_cost_pp`: an exit on a
                       guarantee date, which no flow pays apart
MATURITY        3      the same three: the maturity, or the forced encashment
ALL             4      :func:`claims`: the total of the deaths, the surrenders and
                       the maturities
UWP_BOND        0      :func:`chassis_code`: the unitised bond
CWP_ENDOWMENT   1      :func:`chassis_code`: the conventional endowment
==============  =====  ==========================================================

A code a cell takes indexes that cell's cache, a C array of ten codes a month, the model's
one inner width, for :func:`pols_if_at`, :func:`asset_share_at`, :func:`claim_pp`,
:func:`smoothing_cost_pp` and :func:`claims`, so codes are numbered densely from 0: the
count's four timings in the order of their instants within the month, ``BEF_NB`` before
``BEF_DECR``, as in every SEC model, and then the asset share's six, in its order, one
numbering for the two families of timings; and the kinds in :func:`result_cf`'s order,
then ``ALL``, :mod:`~.WP_UK_S`'s ``kind=None``. A code a cell does not take raises,
``invalid timing`` or ``invalid kind``: the other family's timings, a payout's ``ALL`` and
the claims' ``GUARANTEE``, which they pay inside the surrenders, among them. The chassis's
codes index no cache: :func:`chassis_code` is ``Data``'s decode of the point's column,
compared as :mod:`~.WP_UK_S` compares the text, and is the chassis's row of the lapse table.
They are References, not cells, so the symbol map below does not list them.

.. rubric:: Reporting cells

:func:`model_point`, the label accessors :func:`chassis`, :func:`sex` and
:func:`tax_basis`, the reports :func:`result_cf`, :func:`result_payout` and
:func:`result_pols`, and the seven checks return Python values, a table row, text,
DataFrames and verdicts, for a reader and for the comparison with :mod:`~.WP_UK_S`. No
cell but these calls a label accessor or a report: every other reads the number ``Data``
decoded from the same column instead, the point's chassis code and mortality schedule.
So the labels and the reports stay Python when the model compiles, each check compiles to
a ``bint``, a verdict over cells that compile, and every other cell returns a C ``bint``,
``long long`` or ``double``. Each label refuses any value but its column's codes, as
:mod:`~.WP_UK_S`'s ``chassis`` and ``tax_basis`` do and its ``sex`` does not, so each
returns text or raises, in either engine.

.. rubric:: Each chain one cell a month within its policy year

Eight chains carry the state forward, coupled: the count, the asset share, the smoothed
payout, which reads the asset share and feeds the withdrawal's share of it back, the
endowment's guarantee, the bond's units and unit price, and the two cumulants, the
guarantee charges taken and the smoothing account. :mod:`~.WP_UK_S` runs the asset share
through seven cells a month, its :func:`asset_share_at` timings, the payout through three
and the guarantee through two, so that a cold read of the asset share in a late month ran
thousands of cells deep. Here each chain's month is written in the cell that carries it,
reading that chain's own month before first and the month's other cells after,
:func:`asset_share`, :func:`smoothed_payout`, :func:`guar_benefit_pp` and
``pols_if_at(t, BEF_NB)``, in :mod:`~.WP_UK_S`'s order and its floats;
:func:`asset_share_at` reads it, a step at a time, as :mod:`~.WP_UK_S`'s does.

And each chain is blocked by policy year (UKLIB-SEC-PLAN.md K12), as ``ULB_UK_SEC``'s fund
and ``WOL_UK_SEC``'s counts are. In the first month of a policy year after :func:`t_entry`
a chain reads the year's opening, :func:`pols_if_py`, :func:`asset_share_py`,
:func:`smoothed_payout_py`, :func:`guar_benefit_pp_py`, :func:`units_py`,
:func:`unit_price_py`, :func:`guar_charge_cum_pp_py` or :func:`smoothing_account_py`, each
of which walks the months of the year before in ascending order, asking the monthly cell
of each, so that each finds the month before cached, and returns the value the year's last
month closes on, bit for bit. So a chain of calls from month ``t`` back to :func:`t_entry`
is one cell a month within its policy year and two cells a year before it (USLIB-SEC-PLAN.md
D5), 215 at the contract's longest cover, where one cell a month ran 1,236, which a
compiled model runs on the C stack: one cell a month, a cold call there needed 292 KiB of
it, and blocked 64 (``products/with_profits/model-sec.md``, *What a compiled run needs*).
The bonus rule's own chain, each year's rate declared from the year before's, runs one
cell a year. No cell a chain recurses through formats a message: where the asset share,
the unit price, the units, the guarantee or a cumulant leaves the floats, its cell calls a
refusal cell of its own, :func:`asset_share_refusal`, :func:`unit_price_refusal`,
:func:`units_refusal`, :func:`guar_benefit_refusal`, :func:`guar_charge_cum_refusal` or
:func:`smoothing_account_refusal`, which computes the value again from the same cells and
names what made it, since a compiled cell's frame holds the code of every message it
could format, run or not.

.. rubric:: The frame ends where the units do

A level withdrawal election runs a bond's units down, and against a fund whose growth is
only the declared bonus it eventually cancels the last of them. :func:`fund_exhaust_mth`
finds the month: one loop in that cell, over the units' own months from :func:`t_entry`,
ascending, so that each month's units are read once the month before's are known, the far
read R2 admits, as uslib's ``DIA_US_SEC`` reads its survival to its payout date and
``ULB_UK_SEC`` its fund to exhaustion. It returns a policy month, and its "never" is a
month past cover, where :mod:`~.WP_UK_S`'s was 0, which on the valuation clock is a real
month. :func:`proj_len` ends the frame the month before, where the survivors are encashed,
paid ``FV + FB`` (:func:`is_forced_encashment`). The search reads the units chain, so
nothing the units read may read the frame: :func:`is_active`, which every chain reads, is
the policy-clock end of cover alone, :func:`cover_end_mth`, and in the months after an
exhaustion and before that end a bond is in cover and holds no count, its frame having
ended.

.. rubric:: Naming

Cells names follow lifelib's ``basiclife.BasicTerm_S`` wherever that model has an
analogue — ``pols_*`` for policy counts, plural nouns for cash flows, ``*_rate`` for
rates, ``*_pp`` for per-policy amounts, ``claims(t, kind)`` and ``claim_pp(t, kind)``
with a ``kind`` code (*Codes*, above). What running in force adds is named as
``basiclife.BasicTerm_SE`` names it: ``duration_mth`` read from the model point,
``policy_count``, ``pols_new_biz``, ``pols_if_at``'s ``BEF_NB`` timing, ``is_active`` and
``result_pols``. ``duration_mth_init``, the policy months completed at the valuation date,
takes ``UL_US_S``'s name; ``t_entry`` is this model's own, and each opening-state cell is
the cell it opens with ``_init`` added. The technical notes use compact symbols instead.
The mapping is:

=========================  ==============================  ==========================
Notes symbol               Cells                           Meaning
=========================  ==============================  ==========================
chassis                    chassis()                       UWP_bond or CWP_endowment
(chassis, coded)           chassis_code()                  The chassis's code
(none)                     point_id()                      The point's label
(none)                     mort_schedule()                 Its row of the mortality table
(none)                     lapse_last_year()               Its chassis's last lapse year
t                          (the cells argument)            Months from the valuation
(none)                     duration_mth(t)                 Policy months at time t
(none)                     duration_mth_init()             Policy months at t = 0
(none)                     t_entry()                       First month on the books
(none)                     is_active(t)                    Whether month t is in cover
(none)                     cover_end_mth()                 Policy month cover ends
t // 12 + 1                policy_year(t)                  Contractual policy year label
(none)                     duration(t)                     Completed policy years
(none)                     is_declaration_month(t)         The twelfth month of a policy year
(none)                     declaration_month(t)            That month, for the year holding t
x                          age_at_entry()                  Entry age (ANB)
x + duration(t)            age(t)                          Attained age (ANB)
n                          policy_term()                   Endowment term in years
(none)                     proj_len()                      Months to the frame's end
(none)                     fund_exhaust_mth()              Policy month the units run out
(none)                     is_forced_encashment()          Whether the run ends there
P(t)                       premium_pp(t)                   Premium received at BOM
W(t)                       wd_pp(t)                        Partial withdrawal at BOM
W_AS(t)                    wd_as_pp(t)                     Asset-share reduction for it
r                          fund_return()                   Earned fund return, annual
r_m                        fund_return_mth()               The same, monthly
c_amc                      amc_rate                        Annual management charge
(monthly)                  amc_rate_mth()                  The same, monthly
c_g                        guar_charge_rate(t)             Guarantee/smoothing charge, annual
(monthly)                  guar_charge_rate_mth(t)         The same, monthly
CumGC(t)                   guar_charge_cum_pp(t)           Cumulative guarantee charge
(CumGC at t = 0)           guar_charge_cum_pp_init()       Charges taken before t = 0
(CumGC entering year y)    guar_charge_cum_pp_py(y)        Its year's opening
AS(t)                      asset_share(t)                  Asset share at the end of month t
(the steps)                asset_share_at(t, timing)       The asset share inside month t
AS(t-1)                    asset_share_at(t, BEF_PREM)     The balance month t opens with
(AS entering year y)       asset_share_py(y)               Its year's opening
(AS at t = 0)              asset_share_init()              Asset share at the valuation
M(t)                       misc_surplus_pp(t)              Estate distributions; 0 in base
Q(t)                       unit_price(t)                   With-profits unit price
(Q at t = 0)               unit_price_init()               Unit price at the valuation
(Q entering year y)        unit_price_py(y)                Its year's opening
U(t)                       units(t)                        Units held
(U at t = 0)               units_init()                    Units held at the valuation
(U entering year y)        units_py(y)                     Its year's opening
FV(t), G(t)                guar_benefit_pp(t)              Guaranteed benefit
(FV, G entering year y)    guar_benefit_pp_py(y)           Its year's opening
FV(t-1), G(t-1)            guar_benefit_open(t)            The guarantee month t opens with
G - SA                     attaching_bonus_init()          Reversionary bonus at t = 0
(pre-MVR value)            policy_value_pp(t)              Guaranteed benefit + final bonus
(opening value)            policy_value_open(t)            The pre-MVR value at its open
b, b_rev                   bonus_rate(t)                   Declared annual bonus rate
(b at t = 0)               bonus_rate_init()               The rate of the year under way
b_supp                     bonus_supportable(t)            Rate the guarantee-fill implies
theta, kappa               guar_fill_target, bonus_speed   Bonus-rule parameters
CB(t)                      cost_of_bonus_pp(t)             Cost of the declared bonus
ST(t)                      shareholder_transfer_pp(t)      CB/9, the 90:10 transfer
MC(t)                      mort_charge_pp(t)               Mortality charge to the AS
DB_g(t)                    death_guar_pp(t)                Guaranteed death benefit
q(x+t)                     mort_rate(t)                    Annual mortality rate
q_m(t)                     mort_rate_mth(t)                Monthly mortality rate
w(t)                       surr_rate(t)                    Annual ordinary surrender rate
w_m(t)                     surr_rate_mth(t)                Monthly rate, exercise included
(table)                    surr_rate_base(t)               Table annual surrender rate
(spike)                    guarantee_exercise(t)           MVR-free encashment on the date
sigma                      smooth_cap                      Year-on-year smoothing cap
(monthly floor)            smooth_cap_dn_mth()             Its twelfth roots, down
(monthly ceiling)          smooth_cap_up_mth()             and up
S(t)                       smoothed_payout(t)              Smoothed target payout
S(t-1)                     smoothed_payout_open(t)         The payout month t opens with
(S at t = 0)               smoothed_payout_init()          The payout at the valuation
(S entering year y)        smoothed_payout_py(y)           Its year's opening
(cap step)                 smoothed_payout_capped(t)       After the cap, before the corridor
FB(t), TB(t)               final_bonus_pp(t)               Final or terminal bonus
MVR(t)                     mvr_pp(t)                       Market value reduction, unapplied
(applied)                  mvr_applied_pp(t)               Zero where the exit is MVR-free
(guarantee dates)          is_guarantee_date(t)            MVR-free anniversary month
(guarantee years)          is_guarantee_year(y)            Whether year y closes on one
g_db                       death_benefit_factor            Bond death uplift, 1.01
i_sv, v_sv                 surr_disc_rate                  Endowment surrender discount
(none)                     policy_count()                  Policies the point stands for
l(t)                       pols_if(t)                      In force at the start of month t
(l at t = 0)               pols_if_init()                  Count in force at t = 0
(l entering year y)        pols_if_py(y)                   Its year's opening
(none)                     pols_new_biz(t)                 Policies issued in month t
(none)                     pols_if_at(t, timing)           BEF_NB / BEF_DECR / BEF_SURR / AFT_DECR
(none)                     pols_death(t)                   Deaths in month t
(none)                     pols_surr(t)                    Surrenders at the end of month t
(none)                     pols_maturity(t)                Maturities, or the truncation
(payouts)                  claim_pp(t, kind)               Payout per claim by kind
SM(t)                      smoothing_account(t)            Cumulative smoothing cost
(SM at t = 0)              smoothing_account_init()        The same before t = 0, per policy
(SM entering year y)       smoothing_account_py(y)         Its year's opening
(cash flows)               premiums, claims, withdrawals   Probability-weighted flows
E(t)                       expenses(t)                     Maintenance expense
(none)                     inflation_factor(t)             Expense inflation factor
ST x l                     shareholder_transfers(t)        Transfer outgo
(none)                     net_cf(t)                       Net cash flow, income positive
(none)                     result_pols()                   The counts, month by month
=========================  ==============================  ==========================

Six names needed care in :mod:`~.WP_UK_S`, and keep their reasons here.

``G`` is the guaranteed benefit on the endowment chassis and ``FV`` the unit face value
on the bond chassis, but every rule that consumes them — the bonus cost, the mortality
charge sum at risk, the final bonus, the MVR — treats them identically. They are
therefore **one cells**, :func:`guar_benefit_pp`, and the chassis decides how it rolls
forward. Keeping two names would have duplicated five rules to no purpose.

``MVR`` is computed whether or not it applies: :func:`mvr_pp` is the *scale* and
:func:`mvr_applied_pp` is what an exit actually bears, which is zero on death and on a
guarantee date. Both are needed, because the behavioural deterrent keys off the scale
being positive while the payout keys off what is applied.

``FB`` and ``TB`` are the same quantity — the non-guaranteed top-up from the smoothed
payout to the guaranteed benefit — under two names, one per chassis. They are
:func:`final_bonus_pp` here.

``q(t)`` and ``w(t)`` are the **annual** mortality and surrender rates, as the tables
quote them, with :func:`mort_rate_mth` and :func:`surr_rate_mth` carrying the monthly
conversions. That is the library-wide split — a bare ``*_rate`` is annual everywhere and
only ``*_rate_mth`` is monthly — and it is what keeps the assumption basis stated in the
units it was set in. The same goes for ``fund_return`` against
:func:`fund_return_mth` and ``amc_rate`` against :func:`amc_rate_mth`.

``guarantee_spike``, the annual grid's 2.5x multiplier on a guarantee-date *year*, is
:func:`guarantee_exercise` here: a one-off encashment rate in the guarantee-date
*month*. The rename is not cosmetic — it is a multiplier on a rate becoming a rate of
its own, because the monthly grid can put the exercise in the month the MVR-free window
is actually open.

There is **no** ``av_pp_at`` in this model, and that is a product statement rather than
an omission. The asset share is a *shadow* retrospective accumulation that the
policyholder never owns and is never paid; the guaranteed benefit is not a fund either.
Naming either of them the library's account value would assert something false about
the contract.

.. rubric:: The asset share is a state variable, not a cash flow

::

    AS(t) = [AS(t-1) + P(t) - W_AS(t)] (1 + r_m) (1 - c_amc_m - c_g_m) - ST(t) - MC(t) + M(t)

Every item in it is a recorded deduction from or addition to a retrospective
accumulation, and none of them is a policy cash flow. The policy's actual flows are
premiums, claims, withdrawals, expenses and the shareholder transfer; the asset share
reaches them only through the bonus, smoothing and MVR rules, and the difference between
what is paid and what the asset share says is absorbed by the estate. That difference is
tracked in :func:`smoothing_account`, which the base model accumulates without recycling.

:func:`asset_share_at` exposes the recursion one step at a time — ``BEF_RETURN``,
``AFT_RETURN``, ``AFT_CHARGE``, ``AFT_ST``, ``AFT_MC`` — because the order is
contractual discipline rather than arithmetic convenience: the shareholder transfer is
charged to asset shares *after* the charges and *before* the mortality charge, and the
mortality charge's sum at risk is measured on the balance after the transfer.
:func:`asset_share` writes the same steps inline, in the same order and floats.

.. rubric:: The bonus hardens, and that is what makes guarantees expensive

A declared regular bonus increases the guaranteed benefit permanently. The unit price
therefore never falls — ``b >= 0`` is a contractual floor, not a modelling choice —
and every declaration converts non-guaranteed final bonus into guaranteed benefit
without changing the target payout. That is the whole tension the discretion manages,
and it is why ``guar_fill_target`` and ``bonus_speed`` are genuine modelling
choices with no public calibration rather than parameters someone measured.

The base projection holds the model point's snapshot rate level, as the notes specify.
:func:`bonus_supportable` and the smoothed setting rule are implemented and switched off
behind ``bonus_rule_on``, so the revision module is available for scenario work
without disturbing the reproduction of the worked example. With it on, the year under way
at the valuation date keeps :func:`bonus_rate_init`, as :mod:`~.WP_UK_S` keeps its first
projected year's, and each later year's rate is set at its declaration.

.. rubric:: Smoothing: the cap, then the corridor

::

    S_raw = AS(t)
    S_cap = clamp(S_raw, (1-sigma)^(1/12) S(t-1), (1+sigma)^(1/12) S(t-1))
    S(t)  = clamp(S_cap, 0.80 AS(t), 1.20 AS(t))

The cap is applied **first** and the target corridor **second**, and the order matters:
the cap is what stops a market shock reaching payouts in one step, and the corridor is
what stops the cap holding a payout indefinitely away from the asset share. In the
notes' down scenario the cap binds in every month and the corridor then does not, which
is exactly the pattern the two rules are designed to produce.

The cap is the notes' **year-on-year** ±10% discipline, taken to its twelfth root so
that twelve capped months move the payout by exactly ±10% over the policy year. That is
the conversion that keeps the rule's meaning: a flat ±10% per month would be twelve
times as loose, and a ±10% applied only at anniversaries would leave the eleven
intervening payouts unsmoothed. The notes' down scenario reaches the same closing payout
on this grid as on an annual one for exactly that reason.

The corridor implements the 80-120% target range at model-point level. The regulatory
test is a *portfolio* property — a proportion of policies within the range — and a
single-policy model cannot express it, so the deterministic corridor is a **[std]**
reading of it.

Two things the cap cannot say. It is skipped where there is no previous payout to work
from: in a new-business cell's issue month, where the opening payout ``S`` is nil and the
cap would clamp the payout to nil with it, and in any month that opens on a nil payout,
as a policy in force whose asset share has floored at nil does. And on a
**premium-paying** policy it is only loosely meaningful: a firm's ±10% discipline is a
*like-for-like* comparison between successive maturity cohorts — this year's payout on a
25-year endowment against last year's — not a comparison of one policy's own payout
across its own durations. A regular-premium asset share grows far faster than 10% a year
in early durations because premiums, not investment return, dominate it, so the cap's
upper bound binds and the corridor floor is what actually sets the payout: exactly 80% of
the asset share for most of the first dozen policy years on the endowment cell shipped
here — its issue month is the one month where the cap is skipped, so the payout there is
the asset share itself. Later the corridor floor stops binding and the capped path alone
carries the payout up towards the asset share at maturity. The single-premium bond
the worked example uses has no such problem, which is why the notes can state the cap
plainly.

.. rubric:: Final bonus and MVR are never simultaneous

``FB > 0`` requires ``S > FV`` and ``MVR > 0`` requires ``S < FV``, so the two cannot
both be positive. :func:`check_fb_mvr_exclusive` asserts it, because an implementation
that computed them independently could produce both and would then pay a final bonus and
deduct a market value reduction on the same exit.

The MVR also carries a **contractual bound**: it may not exceed the excess of the unit
value over the underlying asset value, which is ``max(0, FV - AS)``.
:func:`check_mvr_bound` asserts that too. In the notes' down scenario the bound is
2,704.05 and the MVR actually applied is 1,328.04 — comfortably inside it, which is the
point of checking rather than assuming.

The MVR is **unitised only**. It is an adjustment to a *unit* value, and the notes
define it for the unitised chassis alone; a conventional endowment has no units to
reduce. Applying the same arithmetic there would be arithmetically harmless — it happens
to collapse the surrender payout onto the asset share — but it would report a £19,575
"market value reduction" in policy year 1 of a 25-year endowment, which is not a thing
that exists. :func:`mvr_pp` returns zero on that chassis and :func:`claim_pp` sets the
surrender value on a surrender basis instead.

.. rubric:: What a deterministic run cannot do

This is a deterministic single-scenario projection, and it **materially understates the
cost of guarantees**, because guarantee cost is convex in the fund return: the average
of the cost over scenarios exceeds the cost at the average scenario. The ``c_g`` charge
in the asset share recursion is a *charging* proxy — a deduction firms make — and not a
valuation of anything. What this model produces is exactly the per-scenario cash flow
vector a market-consistent stochastic valuation consumes; the stochastic layer is out of
scope and is the reason the notes list a deterministic base run as the central model
risk.

.. rubric:: Behaviour, where the anti-selection lives

Three behavioural adjustments sit on the base surrender rate, all **[std]** and all
rationalized from the incentive structure rather than measured:

- an **MVR deterrent** of 0.6 on the annual rate while an MVR would be applied — an
  active MVR penalizes exit;
- a **guarantee-imminent suppression** of 0.8 on the annual rate in the twelve months
  before a guarantee date, policyholders waiting for the MVR-free window; and
- a **guarantee-date encashment** of 7.5% of the survivors of the guarantee-date
  **month**, applied **only when the guarantee is in the money** (``GB > AS``), because
  MVR-free encashment is worth exercising precisely then and worth nothing otherwise.

The third is the one that matters. Anti-selective exit when guarantees are in the money
is the dominant behavioural risk on with-profits business, and dynamic assumptions of
this kind are a regulatory expectation for the best estimate rather than an optional
refinement. It is also the one place where this grid changes an assumption's shape
rather than its frequency: on an annual grid it could only be a multiplier on the whole
guarantee-date year's surrender rate, which spreads MVR-free exits across eleven months
in which the window is shut. :func:`guarantee_exercise` puts it in the month the option
is open, at a rate chosen so that the guarantee-date year still sheds roughly what the
annual grid's 2.5x spike shed.

The MVR deterrent applies on the bond chassis only, because there is no MVR on the other
one. That falls out of :func:`mvr_applied_pp` rather than being coded as a special case.

.. rubric:: A withdrawal election is not unconditional

The MVR-free allowance is 5% of the original premium a year, and the withdrawing cell
takes the whole of it — a twelfth each month. Against a fund whose growth is only the
declared bonus, that exhausts the fund. :func:`wd_pp` therefore caps the withdrawal at
the unit fund it comes out of, and :func:`proj_len` stops the projection the month
before exhaustion, where
:func:`is_forced_encashment` marks the ending as a real contractual event and the
survivors are paid ``FV + FB`` rather than nothing. :func:`check_fund_nonneg` asserts the
result, because the failure mode here is silent: an uncapped election turns the unit
holding negative and every number downstream of it stays plausible enough to read past.

.. rubric:: What is out of scope, and why

The **smoothed-fund (PruFund-style) chassis** is not implemented. Its mechanics are
daily and quarterly — a 5% daily and 10% quarterly smoothing limit with a 2.5% gap
trigger — and a monthly grid still smooths away the limits that define the design: a
daily limit needs a daily step, and a trigger that fires and unwinds between two monthly
points is invisible to this projection. Moving from an annual grid to a monthly one
narrows that gap without closing it, so the exclusion stands rather than being quietly
relaxed. Implementing it here would produce something that ran and meant nothing, so
:func:`chassis` accepts the two chassis this grid can carry and says so.

Also out of scope, per the notes: paid-up conversion on the endowment chassis, the
guaranteed annuity option module on legacy pension cells (long interest-rate
optionality that needs the stochastic layer to mean anything), estate reattributions and
special bonuses, and the fund-level excess of actual expenses over capped charges, which
a single-policy model cannot see.

.. rubric:: The contract's bounds

What running in force adds is the contract's own bounds, which :func:`proj_len` holds a
point to: an issue age of ``issue_age_min``, 18, or more, the youngest the mortality table
rates, though the bond admits issue from 3 months; the bond's cover from issue to
``omega_age`` and the endowment's to a maturity no later than it, so that every attained
age in cover is one the table rates, ``omega_age`` being at most ``omega_age_max``, 121,
the shipped table's last age plus one; and a policy still in cover at the valuation date.
``Data`` bounds future new business by ``future_horizon_mth``, 120 months. Those bounds
are the contract the compiled model's caches are sized from (``spec_sec.py``): a cover of
at most 1,236 months from issue at 18 to 121, starting at most 120 months after the
valuation date. So each of the three is held to the value the caches are sized from too:
:func:`proj_len` refuses an ``issue_age_min`` below 18 and an ``omega_age_max`` above 121,
and ``Data`` a horizon above 120, so that no value of a Reference admits a frame the
compiled model would read past its caches, raising ``IndexError`` where modelx projects.
And :func:`proj_len` holds every Reference a formula reads through a bound, a power or a
product to its domain, NaN and the infinities outside each, its docstring naming each
domain and its reason.
"""

from modelx.serialize.jsonvalues import *

_formula = lambda idx: None

_bases = []

_allow_none = None

_spaces = []

# ---------------------------------------------------------------------------
# Cells

def model_point():
    """The selected model point as a Series, row ``idx`` of *model_point_table_sec.csv*.

    For a reader who wants every column at once: a reporting cell (the Space docstring),
    which no projection cell reads, but the three label accessors.  ``Data`` checks the
    table as it reads it, and each attribute a formula reads has an accessor below, which
    reads its own ``Data`` vector instead.
    """
    return data.model_point_table().iloc[idx]                        # noqa: F821


def point_id():
    """The label of the selected model point, its ``point_id``, from ``Data.point_id``.

    ``Projection`` is indexed by position, ``idx``, as ``basiclife.BasicTerm_SC`` is; the
    label is what a reader finds in the table, so every refusal names it.
    """
    return int(data.point_id()[idx])                                 # noqa: F821


def chassis():
    """``UWP_bond`` (unitised) or ``CWP_endowment`` (conventional).

    The smoothed-fund chassis of the notes is **not implemented**: its smoothing limits
    are a 5% *daily* and a 10% quarterly movement with a 2.5% gap trigger, and a monthly
    grid can express none of them - a daily limit needs a daily step, and a trigger that
    fires between two monthly points is invisible to this projection.  See the Space
    docstring.  ``Data`` refuses any other code as it reads the table.

    A reporting cell (the Space docstring), :mod:`~.WP_UK_S`'s, which returns the column
    as read, refusing any other value: no projection cell reads it, and each branches on
    ``Data``'s decode of the same column instead, :func:`chassis_code`.
    """
    v = model_point()["chassis"]
    if v not in ("UWP_bond", "CWP_endowment"):
        raise ValueError(
            "invalid chassis; SF_smoothed is out of scope on a monthly grid")
    return v


def chassis_code():
    """The chassis as its code, from ``Data.chassis_code``: ``UWP_BOND`` or
    ``CWP_ENDOWMENT``.

    The int References of the names (the Space docstring's *Codes*), UWP_BOND 0 and
    CWP_ENDOWMENT 1, which :func:`is_unitised` compares as :mod:`~.WP_UK_S` compares the
    text, and the point's row of the lapse table.  A code, not the quantities it selects,
    because the rules of a chassis are this Space's formulas and References, which
    ``Data`` cannot read.  ``Data`` refuses any other chassis.
    """
    return int(data.chassis_code()[idx])                             # noqa: F821


def is_unitised():
    """True on the unitised bond chassis, where the guaranteed benefit is a unit value.

    The chassis is :func:`chassis_code`, compared as :mod:`~.WP_UK_S` compares the text.
    """
    return chassis_code() == UWP_BOND                                # noqa: F821


def age_at_entry():
    """x: the entry age of the model point, age nearest birthday **[std]**.

    ``Data`` holds it to a whole number of years, which :mod:`~.WP_UK_S`'s ``int`` would
    otherwise truncate, and :func:`proj_len` to ``issue_age_min`` or more.  From
    ``Data.age_at_entry``.
    """
    return int(data.age_at_entry()[idx])                             # noqa: F821


def sex():
    """The sex (M / F) of the model point, as the table spells it.

    A reporting cell (the Space docstring), which returns the ``sex`` column as read: no
    projection cell reads it here, and :func:`mort_rate` reads the point's row of the
    mortality table, :func:`mort_schedule`, instead.  It refuses any value but M and F, as
    :mod:`~.WP_UK_S`'s :func:`chassis` and :func:`tax_basis` refuse theirs, so that it
    returns text or raises, in either engine.  ``Data`` refuses any other sex as the table
    is read, so the refusal here is met only past ``Data``'s checks; :mod:`~.WP_UK_S`'s
    returns the column as read.
    """
    v = model_point()["sex"]
    if v not in ("M", "F"):
        raise ValueError("invalid sex")
    return v


def mort_schedule():
    """The row of ``Data.mort_table_array`` of the selected model point: M 0 and F 1.

    The point's sex, the key :mod:`~.WP_UK_S` reads *mort_table.csv* by beside the age,
    decoded in ``Data`` into the row it selects, ``Data.mort_schedule``.
    """
    return int(data.mort_schedule()[idx])                            # noqa: F821


def premium_single_pp():
    """The single premium of the bond chassis, paid in the issue month.

    A contract fact, on a policy in force as on one not yet issued: :func:`premium_pp`
    receives it in the issue month alone, ``duration_mth(t) == 0``, which a policy in force
    at the valuation date has passed, and the withdrawal election is a share of it.  From
    ``Data.premium_single``.
    """
    return float(data.premium_single()[idx])                         # noqa: F821


def premium_regular_pp():
    """The regular annual premium of the endowment chassis, from ``Data.premium_regular``."""
    return float(data.premium_regular()[idx])                        # noqa: F821


def sum_assured():
    """The basic sum assured of the endowment chassis; the guarantee floor at outset.

    From ``Data.sum_assured``.
    """
    return float(data.sum_assured()[idx])                            # noqa: F821


def attaching_bonus_init():
    """G - SA at the valuation date: the reversionary bonuses attaching (endowment).

    :mod:`~.WP_UK_S`'s ``attaching_bonus`` column, renamed to D6's vocabulary: the bonuses
    every declaration before the valuation date has added to the sum assured, measured
    before any month-0 event, so the guarantee month 0 opens with is ``sum_assured() +
    attaching_bonus_init()``.  On a policy valued on an anniversary it includes the
    declaration of the twelfth month just ended.  History, read from the model point:
    the rates declared at the declarations of their day, which no ``bonus_rate`` set at
    the valuation date reaches back to.  0 on a bond, whose bonus is in its unit price,
    on a policy not yet in force, and on an endowment in force 11 months or fewer, before
    its first declaration, which ``Data`` requires.  From ``Data.attaching_bonus_init``.
    """
    return float(data.attaching_bonus_init()[idx])                   # noqa: F821


def policy_term():
    """n: the endowment term in years; 0 on the whole-of-life bond chassis.

    From ``Data.policy_term``.
    """
    return int(data.policy_term()[idx])                              # noqa: F821


def units_init():
    """U at the valuation date: the units held entering month 0 (bond chassis).

    :mod:`~.WP_UK_S`'s ``units`` column, renamed to D6's vocabulary: on a bond in force the
    units its premiums bought less those its withdrawals cancelled, before any month-0
    event, so :mod:`~.WP_UK_S`'s ``units`` of the month before.  Above 0 on a bond in force,
    which ``Data`` requires, a bond whose units are spent being encashed; 0 on a policy
    not yet in force, whose premium buys its units in its issue month, and on the
    endowment, which holds none.  From ``Data.units_init``.
    """
    return float(data.units_init()[idx])                             # noqa: F821


def unit_price_init():
    """Q at the valuation date: the with-profits unit price month 0 opens with (bond).

    On the anchor cell in force at duration 5 it is ``1.02^5 = 1.104081`` - five
    declarations at 2% on a unit seeded at £1.0000.  History on a bond in force: the
    declarations of its day raised it, which no ``bonus_rate`` set at the valuation date
    reaches back to.  On a policy not yet in force it is the **seed price** its premium
    buys units at, an issue value, which ``Data``'s check that such a policy holds no
    opening state exempts.  A finite number above 0, which ``Data`` requires.  From
    ``Data.unit_price_init``.
    """
    return float(data.unit_price_init()[idx])                        # noqa: F821


def asset_share_init():
    """AS at the valuation date: the asset share month 0 opens with.

    A retrospective accumulation, and the model point's most important number: it is
    what the payout machinery is measured against, and nobody is ever paid it.  On a
    policy in force, :mod:`~.WP_UK_S`'s close of the month before, floored at 0 as
    :mod:`~.WP_UK_S` floors it; 0 is a state the down scenario reaches, and ``Data``
    accepts it.  0 on a policy not yet in force, which ``Data`` requires.  From
    ``Data.asset_share_init``.
    """
    return float(data.asset_share_init()[idx])                       # noqa: F821


def smoothed_payout_init():
    """S at the valuation date: the smoothed payout month 0 opens with.

    The benchmark the year-on-year cap works from.  On the anchor cell it is £29,500
    against an asset share of £30,000 - the payout is already a little below the asset
    share, which is what the smoothing cap does after a good year.  0 legitimately where
    the asset share has floored at 0, the corridor holding the payout to the asset share,
    and then the cap is skipped in month 0 as in a new-business cell's issue month.  0 on a
    policy not yet in force, which ``Data`` requires.  From ``Data.smoothed_payout_init``.
    """
    return float(data.smoothed_payout_init()[idx])                   # noqa: F821


def is_guarantee_year(y):
    """Whether the anniversary closing policy year y is a guarantee date, an exit there
    MVR-free.

    The one cell that reads ``Data.guarantee_flags``, the point's ``guarantee_dates``
    decoded by policy year, where :mod:`~.WP_UK_S` parses the column into a tuple of years,
    ``guarantee_years``, and tests a year's membership of it: 1 at each year the column
    names, so that ``is_guarantee_year(y)`` is ``y in guarantee_years()``.  False below
    year 1, which no column names, and past ``Data.guarantee_year_last``, a year no cover
    reaches, which the array does not hold, so that no read meets either end of it.
    :func:`is_guarantee_date` reads it at the policy year of a declaration month, and
    :func:`guarantee_imminent` at the year whose date is the next a month's window waits
    for, so ``y`` runs from 1 to the year after the longest cover's last, 104 at the
    contract's longest, issue at ``issue_age_min``, 18, to ``omega_age_max``, 121
    (``spec_sec.py``).  Never True on the endowment chassis, which ``Data`` holds to no
    guarantee dates.
    """
    if y < 1 or y > data.guarantee_year_last():                      # noqa: F821
        return False
    return bool(data.guarantee_flags()[idx, y] == 1)                 # noqa: F821


def wd_rate():
    """The partial withdrawal taken each year, as a fraction of the original premium.

    Zero in the base run; the MVR-free allowance is 5% a year, and a withdrawing cell
    takes the whole of it.  ``Data`` holds it from 0 to 1.  From ``Data.wd_rate``.
    """
    return float(data.wd_rate()[idx])                                # noqa: F821


def tax_basis():
    """``life_net`` or ``pension_gross``.

    The fund return is quoted net of life-fund tax on a ``life_net`` cell and gross on a
    pension one; asset shares are accumulated on the basis that applies to the policy.
    The distinction is carried on the model point and is applied by supplying the return
    already on the right basis, rather than by grossing up inside the model.

    A reporting cell (the Space docstring), :mod:`~.WP_UK_S`'s, which returns the column
    as read, refusing any other value: no projection cell reads the basis, the return
    being supplied on it.
    """
    v = model_point()["tax_basis"]
    if v not in ("life_net", "pension_gross"):
        raise ValueError("invalid tax_basis")
    return v


def fund_return():
    """r: the earned fund return, on the model point's tax basis **[std]**.

    A **scenario level** rather than a best estimate: the notes' worked example is a
    one-year, two-scenario comparison, and the shipped scenario cells hold their own
    return for the whole projection, so the first projected year reproduces the notes
    exactly and the remainder shows what that scenario implies if sustained.  A level, so
    the same on the valuation clock as on the policy clock, and nothing is re-based.

    Asset shares, final bonuses and MVR incidence all key off this one number, and a
    deterministic run understates guarantee cost because the cost is convex in it.
    ``Data`` holds it to a finite number above -1, where the monthly return has a real
    value.

    Read the down cell's tail for what it is.  A single year at -15% is a market shock;
    sixty consecutive years at -15% is not a scenario anyone would value against, and the
    cell duly exhausts its asset share and leaves the guarantee entirely estate-funded.
    That end of the projection is a demonstration of the machinery under stress, not a
    result.  From ``Data.fund_return``.
    """
    return float(data.fund_return()[idx])                            # noqa: F821


def bonus_rate_init():
    """The bonus rate declared at the last declaration before the valuation date.

    :mod:`~.WP_UK_S`'s ``bonus_rate`` column, renamed to D6's vocabulary: 2.00% on the bond
    chassis and 1.50% compound on the endowment, both **[std]**: declarations are not
    published in firms' principles and practices documents.  It is the rate of every
    policy year in the base run.  With ``bonus_rule_on`` it is the state before the
    valuation date (D6): the rate declared at the end of policy month
    ``12 x duration(0) - 1``, from which the rule sets the first declaration in the frame,
    the one closing the policy year under way, at today's References.  On a policy not yet
    in force, the rate its first declaration starts from, an issue value.  A finite number,
    zero or more, the declared bonus being floored at 0, which ``Data`` requires.  From
    ``Data.bonus_rate_init``.
    """
    return float(data.bonus_rate_init()[idx])                        # noqa: F821


def guar_charge_cum_pp_init():
    """CumGC at the valuation date: the guarantee charges taken per policy since issue.

    :func:`guar_charge_cum_pp`'s value entering month 0, the charges of every month to the
    end of month -1, which the charge's lifetime cap of 2% of the asset share is measured
    against in month 0.  :mod:`~.WP_UK_S` restarts it at 0 where its frame opens, so a bond
    it reopens in force charges on where its own projection from issue has stopped: the
    down scenario's bond issued at the valuation date stops charging at month 88, and
    reopened at month 60 without its charges it would charge again.  History, read from
    the model point, never rebuilt from today's charge and cap.  0 on a policy not yet in
    force, which ``Data`` requires.  From ``Data.guar_charge_cum_pp_init``.
    """
    return float(data.guar_charge_cum_pp_init()[idx])                # noqa: F821


def smoothing_account_init():
    """SM at the valuation date: the estate's smoothing cost since issue, per policy.

    :func:`smoothing_account`'s value entering month 0 over the policies then in force:
    the excess of every payout over the asset share it released, on the exits of every
    month to the end of month -1, carried per policy in force so that the count is the one
    weight, and :func:`smoothing_account` opens at it times :func:`pols_if_init`.
    :mod:`~.WP_UK_S` restarts the account at 0 where its frame opens.  Of either sign: it is
    negative where payouts have fallen short of the asset shares.  History, read from the
    model point.  0 on a policy not yet in force, which ``Data`` requires.  From
    ``Data.smoothing_account_init``.
    """
    return float(data.smoothing_account_init()[idx])                 # noqa: F821


def policy_count():
    """The number of policies the model point stands for, its ``policy_count`` column.

    A point in force at the valuation date counts the policies in force then, before any
    month-0 event; any other point counts the policies it issues. Either way the count
    enters the projection once: as :func:`pols_if_init` for the first, as
    :func:`pols_new_biz` in the issue month for the second. It is the one weight on every
    flow: every opening-state column is per policy.  From ``Data.policy_count``.
    """
    return float(data.policy_count()[idx])                           # noqa: F821


def pols_if_init():
    """Policies in force at the valuation date, before any month-0 event.

    ``policy_count()`` for a point already in force at ``t = 0``
    (``duration_mth_init() > 0``), and 0 for one issued at or after it, whose policies
    enter through :func:`pols_new_biz` in the issue month instead, as in
    ``basiclife.BasicTerm_SE``. So on a point issued at ``t = 0`` this is 0, and
    ``pols_if(0)`` is the issued count.
    """
    return policy_count() if duration_mth_init() > 0 else 0.0


def duration_mth_init():
    """Completed policy months at the valuation date, the ``duration_mth`` column.

    The policy's age in months at ``t = 0``: 60 for the worked example's bond, in force
    five years, 0 for one issued at the valuation date, and -13 for one to be issued 13
    months after it, which ``Data`` admits up to ``future_horizon_mth`` months ahead. It is
    read as ``basiclife.BasicTerm_SE`` reads it, and is the one fact the policy clock takes
    from the model point; a point may be valued in any month of its policy year, where
    :mod:`~.WP_UK_S` opens a frame on an anniversary only.  From ``Data.duration_mth``.
    """
    return int(data.duration_mth()[idx])                             # noqa: F821


def t_entry():
    """The first month the policy is on the books: ``max(0, -duration_mth_init())``.

    0 for a point in force at the valuation date or issued at it, ``k`` for one issued
    ``k`` months later.  It is the base of every recursion: the count, the asset share,
    the units, the unit price, the guarantee, the smoothed payout and the two cumulants
    open there, from the opening state, and none reads a month before it.
    :func:`fund_exhaust_mth` searches the units from it.
    """
    return max(0, -duration_mth_init())


def is_active(t):
    """Whether month t is inside cover: issued, and short of the end of cover.

    ``0 <= duration_mth(t) < cover_end_mth()``.  False before issue and from the month the
    endowment matures or the bond reaches ``omega_age``.  Outside cover every balance,
    count, flow and charge is 0, every flag False, and no table is read at a policy year
    or an attained age the policy does not have.

    It reads the end of cover alone, on the policy clock, not :func:`proj_len`: the frame
    also ends where a withdrawal election exhausts the bond's units, which
    :func:`fund_exhaust_mth` finds by projecting the units, and the units, through every
    chain they read, read this.  So in the months after an exhaustion and before the
    limiting age a bond is in cover; there the counts are 0, because the frame has ended.
    """
    return 0 <= duration_mth(t) < cover_end_mth()


def cover_end_mth():
    """The policy month cover ends: the endowment's maturity or the bond's limiting age.

    ``12 x policy_term()`` on the endowment, which matures at the end of policy month
    ``12n - 1``, and ``12 x (omega_age - age_at_entry())`` on the whole-of-life bond, whose
    cover runs to the limiting age.  :mod:`~.WP_UK_S`'s frame from issue but for the
    exhaustion, on the policy clock: :func:`is_active` is false from ``duration_mth(t) =
    cover_end_mth()`` on.  ``omega_age`` is read as an ``int``, which :func:`proj_len` holds
    it to be first: a whole number written as a float, ``120.0``, makes the frame ``120``
    makes, in whole months.
    """
    if not is_unitised():
        return 12 * policy_term()
    return 12 * (int(omega_age) - age_at_entry())                    # noqa: F821


def fund_exhaust_mth():
    """The policy month in which a bond's withdrawals cancel its last unit.

    The first month on the books whose closing units, :func:`units`, are at or below
    ``1e-9``, :mod:`~.WP_UK_S`'s test, as a policy month, ``duration_mth(t)``: the month the
    withdrawal election, capped at the unit fund, takes the last of it.  That month is not
    projected: the bond is encashed at the end of the month before, which is the frame's
    last (:func:`proj_len`, :func:`is_forced_encashment`).  On the endowment, and on a
    bond taking no withdrawals, the units never run out, and so on a bond whose withdrawals
    the declared bonus outruns.

    The search is one loop in this cell, over the units' own months from :func:`t_entry`
    to the end of cover, ascending, so that it reads each month's units once those of the
    month before are known: the far read R2 admits, as ``DIA_US_SEC``'s survival to its
    payout date is and ``ULB_UK_SEC``'s fund to its exhaustion, and the only one this model
    makes but the bonus rate's, the policy month being formed from
    :func:`duration_mth_init` rather than read.  It reads the units of the month of
    exhaustion, one past the frame's last, as :mod:`~.WP_UK_S`'s search does.  It starts at
    :func:`t_entry`, not at 0, because a bond issued later holds no units before its issue
    month, which a search from 0 would read as exhausted at once.

    "Never" is ``cover_end_mth() + 1``, a month past cover.  :mod:`~.WP_UK_S`'s was 0, safe
    there because its month 0 is a bond's issue month, which the single premium funds; on
    the valuation clock month 0 is any month of a bond's life, including the one its last
    units are withdrawn in, and a policy month of 0 is a real month too.
    """
    if not is_unitised() or wd_rate() <= 0.0:
        return cover_end_mth() + 1
    for t in range(t_entry(), cover_end_mth() - duration_mth_init()):
        if units(t) <= 1e-9:
            return duration_mth_init() + t
    return cover_end_mth() + 1


def proj_len():
    """The number of months from the valuation date to the end of the frame.

    ``min(cover_end_mth(), fund_exhaust_mth()) - duration_mth_init()``: the endowment's
    maturity, the bond's limiting age, or the month a withdrawal election exhausts its
    units, whichever comes first, counted from the valuation date rather than from issue.
    720 for the worked example's bond, in force 60 months of 780; 343 for the withdrawing
    bond, whose units run out at policy month 403; 300 for the endowment issued at the
    valuation date; and the frame from issue plus ``k`` for a policy issued ``k`` months
    after it.  The frame is ``t = 0, 1, ..., proj_len() - 1``; ``proj_len()`` is its
    exclusive end and the row count of :func:`result_cf`.

    These raise here, naming the point, rather than project nothing, a frame the contract
    does not have, or one that no value of a Reference defines, each checked in this order:

    * ``issue_age_min`` that is not a whole number, 18 or more, below ``2**53``: an age,
      which a NaN would switch off, every comparison with it failing, and the youngest
      the compiled model's caches are sized from (``spec_sec.py``), so that a lower one
      would admit frames past them;
    * a policy issued below ``issue_age_min``, 18, the youngest age the mortality table
      rates, though the bond admits issue from 3 months;
    * ``omega_age`` that is not a whole number below ``2**53``, above ``issue_age_min`` and
      at most a year past the mortality table's last age, ``Data.mort_age_last() + 1``,
      since cover reads attained ages to ``omega_age - 1``: the limiting age sizes every
      bond's frame, and a NaN, an infinity or a fraction of a year would leave the frame's
      months no whole number; and ``omega_age`` above ``omega_age_max``, 121, which is
      itself a whole number below ``2**53`` and 121 or less, the largest limiting age the
      caches are sized from, whatever mortality table is read;
    * a bond issued at or past ``omega_age``, which has no cover from issue, and an
      endowment maturing past it, at ``age_at_entry() + policy_term()``, whose last
      attained ages the table would not rate: :mod:`~.WP_UK_S` bounds no term, and reads
      them at ``omega_age``;
    * a policy whose cover had ended by the valuation date, at or past
      :func:`cover_end_mth`, which an in-force extract should not carry;
    * any point while a Reference is off its domain, which the message names. NaN and the
      infinities are outside every one:

      - ``mort_be_factor``, finite, 0 or more: a factor on a probability, read inside the
        mortality cap's ``min``, where an infinity reads as certain death and below 0 a
        rate is negative;
      - ``amc_rate`` and ``guar_charge_rate_base``, from 0 to 1: charges, each taken
        monthly as ``1 - (1 - c)^(1/12)``, which has no real value past 1; and together
        at most the whole asset share a month, ``amc_rate_mth()`` and the guarantee
        charge's monthly rate summing to 1 or less, which the charges' factor on the
        balance, ``1 - c_amc_m - c_g_m``, reads as one;
      - ``guar_charge_cap``, from 0 to 1, the share of the asset share the charges may
        reach, which a NaN would switch off, its comparison failing;
      - ``misc_surplus_rate``, finite, 0 or more: an estate distribution, added to the
        asset share before its floor at 0, which would read a NaN as an exhausted share;
      - ``prem_alloc_rate``, from 0 to 1, the share of a premium that buys units;
      - ``death_benefit_factor``, finite, 0 or more: the bond's uplift, read inside the
        mortality charge's ``max(0, ...)``, which would lose a NaN;
      - ``shareholder_transfer_divisor``, finite, above 0: the cost of bonus is divided by
        it;
      - ``surr_disc_rate``, finite, above -1: the endowment's bonus cost is discounted at
        ``(1 + i)^years``;
      - ``smooth_cap``, from 0 to 1: the cap's twelfth roots, ``(1 - sigma)^(1/12)`` and
        ``(1 + sigma)^(1/12)``, read inside the cap's ``max`` and ``min``, which a NaN would
        be lost through;
      - ``corridor_lo``, from 0 to 1, and ``corridor_hi``, finite, 1 or more: the target
        corridor, which must include 100% of the asset share, read inside the corridor's
        ``max`` and ``min``;
      - ``bonus_rule_on``, True or False, the switch;
      - ``guar_fill_target``, finite, 0 or more, a share of the projected asset share
        raised to ``1/m``; ``bonus_speed``, from 0 to 1, the share of the gap a year's
        declaration closes; ``bonus_change_cap``, finite, 0 or more, the clamp a NaN would
        be lost through; and ``bonus_horizon``, a whole number of years, 1 or more, below
        ``2**53``, the bond's ``m``, which the rule divides by;
      - ``mvr_deterrent_factor`` and ``guarantee_imminent_factor``, finite, 0 or more:
        multipliers of a probability, read inside :func:`surr_rate`'s ``min(1.0, ...)``,
        its bound first as in :mod:`~.WP_UK_S`, which reads a NaN as certain surrender;
      - ``guarantee_exercise_rate``, from 0 to 1, a probability, read the same way;
      - ``expense_maint``, finite, 0 or more: below 0 an income;
      - ``inflation_rate``, finite, -1 or more: below -1 the inflation factor changes sign
        each year;

    * a bond whose units run out in its first month on the books, month 0 for a bond in
      force, its issue month for one not yet in force: the frame would end before it
      began.

    The rules read this Space's References, which ``Data`` cannot see, so they are checked
    here.  They are the contract the compiled model's caches are sized from
    (``spec_sec.py``): a cover of at most ``omega_age_max - issue_age_min`` years, 103, from
    issue at 18 to a limiting age of 121, starting at most ``Data.future_horizon_mth``, 120
    months, after the valuation date, so a frame of at most 1,356 months, and attained ages
    from 18 to ``omega_age - 1`` on the mortality table.  Every report reads this cell
    first, and so does every count, so no point outside them is projected, in modelx as
    compiled; and the three bounds are held to the values the caches are sized from, the
    issue age at 18 or more, the limiting age at 121 or less and the horizon at 120 or less,
    so that no value of a Reference admits a frame the compiled model would read past its
    caches, raising ``IndexError`` where modelx projects.  Each check is a comparison
    written out, a finite bound the largest float, 1.7976931348623157e308, and a whole one
    ``2**53``, so that a compiled cell runs it in C, and each Reference is printed as the
    compiled model types it: ``issue_age_min``, ``omega_age``, ``omega_age_max`` and
    ``bonus_horizon`` through ``int()`` once they are whole numbers, and every other through
    ``float()``; ``omega_age`` is then read as the ``int`` it is.  A value a formula
    computes past the floats, from References and an opening state each in its domain, is
    refused in the cell where it first is, naming the point: the premium, the asset share
    and the parts of its month that a Reference multiplies, the units, the unit price, the
    guarantee, the death uplift, the cost of bonus and its transfer, the two cumulants, each
    flow and the net cash flow.  So is a power past the floats, which Python's ``**`` raises
    as ``OverflowError``, naming neither the point nor the Reference, and C's ``pow`` gives
    as an infinity: the inflation factor, the bonus rule's growth to its horizon and the
    endowment's discount on its bonus cost, which below the smallest float is refused too,
    since the cost divides by it (``PA_UK_SEC``'s form, *Record — M11*).
    """
    if not (issue_age_min > -9007199254740992.0                       # noqa: F821
            and issue_age_min < 9007199254740992.0                    # noqa: F821
            and issue_age_min == issue_age_min // 1):                 # noqa: F821
        raise ValueError(f"point_id {point_id()}: issue_age_min must be a whole number "  # noqa: F821
                         f"below 2**53, not {float(issue_age_min)}")  # noqa: F821
    if issue_age_min < 18:                                           # noqa: F821
        raise ValueError(f"point_id {point_id()}: issue_age_min must be 18 or more, "  # noqa: F821
                         f"not {int(issue_age_min)}")                # noqa: F821
    x = age_at_entry()
    if x < issue_age_min:                                            # noqa: F821
        raise ValueError(f"point_id {point_id()}: the issue age, {x}, is below "  # noqa: F821
                         f"issue_age_min, {int(issue_age_min)}")     # noqa: F821
    if not (omega_age > -9007199254740992.0                           # noqa: F821
            and omega_age < 9007199254740992.0                        # noqa: F821
            and omega_age == omega_age // 1):                         # noqa: F821
        raise ValueError(f"point_id {point_id()}: omega_age must be a whole number "  # noqa: F821
                         f"below 2**53, not {float(omega_age)}")     # noqa: F821
    if not (omega_age > issue_age_min                                # noqa: F821
            and omega_age <= data.mort_age_last() + 1):               # noqa: F821
        raise ValueError(
            f"point_id {point_id()}: omega_age must be above issue_age_min, "  # noqa: F821
            f"{int(issue_age_min)}, and at most {data.mort_age_last() + 1}, a year past "  # noqa: F821
            f"mort_table.csv's last age, not {int(omega_age)}")      # noqa: F821
    if not (omega_age_max > -9007199254740992.0                       # noqa: F821
            and omega_age_max < 9007199254740992.0                    # noqa: F821
            and omega_age_max == omega_age_max // 1):                 # noqa: F821
        raise ValueError(f"point_id {point_id()}: omega_age_max must be a whole number "
                         f"below 2**53, not {float(omega_age_max)}")  # noqa: F821
    if omega_age_max > 121:                                          # noqa: F821
        raise ValueError(f"point_id {point_id()}: omega_age_max must be 121 or less, "
                         f"not {int(omega_age_max)}")                # noqa: F821
    if omega_age > omega_age_max:                                    # noqa: F821
        raise ValueError(f"point_id {point_id()}: omega_age, {int(omega_age)}, is above "  # noqa: F821
                         f"omega_age_max, {int(omega_age_max)}")     # noqa: F821
    if is_unitised():
        if cover_end_mth() <= 0:
            raise ValueError(f"point_id {point_id()}: the issue age, {x}, is at or past "  # noqa: F821
                             f"omega_age, {int(omega_age)}: the bond has no cover")  # noqa: F821
    elif x + policy_term() > omega_age:                              # noqa: F821
        raise ValueError(
            f"point_id {point_id()}: the endowment matures at age {x + policy_term()}, "  # noqa: F821
            f"past omega_age, {int(omega_age)}, whose attained ages mort_table.csv "  # noqa: F821
            f"may not rate")
    d = duration_mth_init()
    if d >= cover_end_mth():
        raise ValueError(
            f"point_id {point_id()}: duration_mth {d} is at or past the end of cover, "  # noqa: F821
            f"policy month {cover_end_mth()}")
    if not (mort_be_factor >= 0.0                                    # noqa: F821
            and mort_be_factor <= 1.7976931348623157e308):            # noqa: F821
        raise ValueError(f"point_id {point_id()}: mort_be_factor must be a finite number, "  # noqa: F821
                         f"0 or more, not {float(mort_be_factor)}")  # noqa: F821
    if not (amc_rate >= 0.0 and amc_rate <= 1.0):                    # noqa: F821
        raise ValueError(f"point_id {point_id()}: amc_rate must be a number from 0 to 1, "  # noqa: F821
                         f"not {float(amc_rate)}")                   # noqa: F821
    if not (guar_charge_rate_base >= 0.0 and guar_charge_rate_base <= 1.0):  # noqa: F821
        raise ValueError(f"point_id {point_id()}: guar_charge_rate_base must be a number "  # noqa: F821
                         f"from 0 to 1, not {float(guar_charge_rate_base)}")  # noqa: F821
    charged = amc_rate_mth() + (1.0 - (1.0 - guar_charge_rate_base) ** (1.0 / 12.0))  # noqa: F821
    if not charged <= 1.0:
        raise ValueError(
            f"point_id {point_id()}: amc_rate and guar_charge_rate_base must together "  # noqa: F821
            f"charge at most the whole asset share in a month, their monthly rates summing "
            f"to 1 or less, not {charged}, under amc_rate {float(amc_rate)} and "  # noqa: F821
            f"guar_charge_rate_base {float(guar_charge_rate_base)}")  # noqa: F821
    if not (guar_charge_cap >= 0.0 and guar_charge_cap <= 1.0):      # noqa: F821
        raise ValueError(f"point_id {point_id()}: guar_charge_cap must be a number from 0 "  # noqa: F821
                         f"to 1, not {float(guar_charge_cap)}")      # noqa: F821
    if not (misc_surplus_rate >= 0.0                                 # noqa: F821
            and misc_surplus_rate <= 1.7976931348623157e308):         # noqa: F821
        raise ValueError(f"point_id {point_id()}: misc_surplus_rate must be a finite "  # noqa: F821
                         f"number, 0 or more, not {float(misc_surplus_rate)}")  # noqa: F821
    if not (prem_alloc_rate >= 0.0 and prem_alloc_rate <= 1.0):      # noqa: F821
        raise ValueError(f"point_id {point_id()}: prem_alloc_rate must be a number from 0 "  # noqa: F821
                         f"to 1, not {float(prem_alloc_rate)}")      # noqa: F821
    if not (death_benefit_factor >= 0.0                              # noqa: F821
            and death_benefit_factor <= 1.7976931348623157e308):      # noqa: F821
        raise ValueError(f"point_id {point_id()}: death_benefit_factor must be a finite "  # noqa: F821
                         f"number, 0 or more, not {float(death_benefit_factor)}")  # noqa: F821
    if not (shareholder_transfer_divisor > 0.0                       # noqa: F821
            and shareholder_transfer_divisor <= 1.7976931348623157e308):  # noqa: F821
        raise ValueError(f"point_id {point_id()}: shareholder_transfer_divisor must be a "  # noqa: F821
                         f"finite number above 0, not "
                         f"{float(shareholder_transfer_divisor)}")    # noqa: F821
    if not (surr_disc_rate > -1.0                                    # noqa: F821
            and surr_disc_rate <= 1.7976931348623157e308):            # noqa: F821
        raise ValueError(f"point_id {point_id()}: surr_disc_rate must be a finite number "  # noqa: F821
                         f"above -1, not {float(surr_disc_rate)}")   # noqa: F821
    if not (smooth_cap >= 0.0 and smooth_cap <= 1.0):                # noqa: F821
        raise ValueError(f"point_id {point_id()}: smooth_cap must be a number from 0 to 1, "  # noqa: F821
                         f"not {float(smooth_cap)}")                 # noqa: F821
    if not (corridor_lo >= 0.0 and corridor_lo <= 1.0):              # noqa: F821
        raise ValueError(f"point_id {point_id()}: corridor_lo must be a number from 0 to 1, "  # noqa: F821
                         f"not {float(corridor_lo)}")                # noqa: F821
    if not (corridor_hi >= 1.0                                       # noqa: F821
            and corridor_hi <= 1.7976931348623157e308):               # noqa: F821
        raise ValueError(f"point_id {point_id()}: corridor_hi must be a finite number, 1 "  # noqa: F821
                         f"or more, not {float(corridor_hi)}")       # noqa: F821
    if not (bonus_rule_on == True or bonus_rule_on == False):        # noqa: F821,E712
        raise ValueError(f"point_id {point_id()}: bonus_rule_on must be True or False, "  # noqa: F821
                         f"not {bonus_rule_on!r}")                   # noqa: F821
    if not (guar_fill_target >= 0.0                                  # noqa: F821
            and guar_fill_target <= 1.7976931348623157e308):          # noqa: F821
        raise ValueError(f"point_id {point_id()}: guar_fill_target must be a finite "  # noqa: F821
                         f"number, 0 or more, not {float(guar_fill_target)}")  # noqa: F821
    if not (bonus_speed >= 0.0 and bonus_speed <= 1.0):              # noqa: F821
        raise ValueError(f"point_id {point_id()}: bonus_speed must be a number from 0 to 1, "  # noqa: F821
                         f"not {float(bonus_speed)}")                # noqa: F821
    if not (bonus_change_cap >= 0.0                                  # noqa: F821
            and bonus_change_cap <= 1.7976931348623157e308):          # noqa: F821
        raise ValueError(f"point_id {point_id()}: bonus_change_cap must be a finite "  # noqa: F821
                         f"number, 0 or more, not {float(bonus_change_cap)}")  # noqa: F821
    if not (bonus_horizon > -9007199254740992.0                       # noqa: F821
            and bonus_horizon < 9007199254740992.0                    # noqa: F821
            and bonus_horizon == bonus_horizon // 1):                 # noqa: F821
        raise ValueError(f"point_id {point_id()}: bonus_horizon must be a whole number "  # noqa: F821
                         f"below 2**53, not {float(bonus_horizon)}")  # noqa: F821
    if bonus_horizon < 1:                                            # noqa: F821
        raise ValueError(f"point_id {point_id()}: bonus_horizon must be 1 or more, not "  # noqa: F821
                         f"{int(bonus_horizon)}")                    # noqa: F821
    if not (mvr_deterrent_factor >= 0.0                              # noqa: F821
            and mvr_deterrent_factor <= 1.7976931348623157e308):      # noqa: F821
        raise ValueError(f"point_id {point_id()}: mvr_deterrent_factor must be a finite "  # noqa: F821
                         f"number, 0 or more, not {float(mvr_deterrent_factor)}")  # noqa: F821
    if not (guarantee_exercise_rate >= 0.0                           # noqa: F821
            and guarantee_exercise_rate <= 1.0):                      # noqa: F821
        raise ValueError(f"point_id {point_id()}: guarantee_exercise_rate must be a number "  # noqa: F821
                         f"from 0 to 1, not {float(guarantee_exercise_rate)}")  # noqa: F821
    if not (guarantee_imminent_factor >= 0.0                         # noqa: F821
            and guarantee_imminent_factor <= 1.7976931348623157e308):  # noqa: F821
        raise ValueError(f"point_id {point_id()}: guarantee_imminent_factor must be a "  # noqa: F821
                         f"finite number, 0 or more, not "
                         f"{float(guarantee_imminent_factor)}")       # noqa: F821
    if not (expense_maint >= 0.0                                     # noqa: F821
            and expense_maint <= 1.7976931348623157e308):             # noqa: F821
        raise ValueError(f"point_id {point_id()}: expense_maint must be a finite number, "  # noqa: F821
                         f"0 or more, not {float(expense_maint)}")   # noqa: F821
    if not (inflation_rate >= -1.0                                   # noqa: F821
            and inflation_rate <= 1.7976931348623157e308):            # noqa: F821
        raise ValueError(f"point_id {point_id()}: inflation_rate must be a finite number, "  # noqa: F821
                         f"-1 or more, not {float(inflation_rate)}")  # noqa: F821
    exhaust = fund_exhaust_mth()
    if exhaust <= max(d, 0):
        raise ValueError(
            f"point_id {point_id()}: the bond's units run out in its first month on the "  # noqa: F821
            f"books, policy month {exhaust}, so its frame would end before it began")
    return min(cover_end_mth(), exhaust) - d


def is_forced_encashment():
    """Whether the bond's projection ends because its units have been exhausted.

    It changes what the survivors at the end of the projection are paid.  A fund-
    exhaustion ending is a **real contractual event** - the last units are cancelled and
    the bond is encashed - so the survivors are paid out.  A limiting-age ending is a
    modelling truncation, and paying anything there would invent a claim.  True where
    :func:`fund_exhaust_mth` finds a month inside cover.
    """
    return is_unitised() and fund_exhaust_mth() < cover_end_mth()


def duration(t):
    """Completed policy years at the start of month t: ``duration_mth(t) // 12``.

    0 throughout the first policy year, and negative before issue, where nothing reads it.
    """
    return duration_mth(t) // 12


def duration_mth(t):
    """Completed policy months at the start of month t, the **policy** clock.

    ``duration_mth_init() + t``: ``t`` counts months from the valuation date and
    ``duration_mth(t)`` months from issue, and the two move together.  A closed form,
    where ``basiclife.BasicTerm_SE`` adds one a month by recursion: the same numbers,
    without a call chain as long as the frame.  Negative before issue.  The declaration
    cycle, the guarantee dates, the single premium and the end of cover read it.
    """
    return duration_mth_init() + t


def age(t):
    """The attained age (ANB) during month t: ``x + duration(t)``.

    Advances on the policy anniversary rather than monthly, which is what an
    age-nearest-birthday basis means and how the mortality table is entered.
    """
    return age_at_entry() + duration(t)


def policy_year(t):
    """The contractual policy year containing month t: the 1-based label ``duration(t) + 1``.

    A contractual label derived from the policy clock, never the index itself: the
    guarantee dates, the declaration cycle and the lapse table are keyed by it.  0 or less
    before issue, where nothing reads a table or a date by it.
    """
    return duration(t) + 1


def is_declaration_month(t):
    """Whether month t ends on a policy anniversary, and so carries a declaration.

    ``(duration_mth(t) + 1) mod 12 = 0``, the twelfth month of a policy year, on the policy
    clock: :mod:`~.WP_UK_S` tests ``(t + 1)``, which on the valuation clock would put a
    bond valued mid-year's declarations in the wrong months.  The bonus declaration is the
    governing discretion cycle and it is **annual**: firms declare once a year, and a
    declaration permanently hardens the guarantee.  So the grid runs monthly and the
    declaration does not - it fires in the twelfth month of each policy year and nowhere
    else, which is what keeps this a change of grid rather than a change of product.
    False outside cover.
    """
    return is_active(t) and (duration_mth(t) + 1) % 12 == 0


def declaration_month(t):
    """The month whose end carries the declaration for the policy year containing t.

    A **valuation** month, ``t + 11 - duration_mth(t) % 12``: ``t`` itself in a
    declaration month, and up to 11 months ahead of it otherwise, as uslib's
    ``WholeLife_US_SEC`` reads its ``anniv_mth``.  :mod:`~.WP_UK_S` returns the **policy**
    month ``12 x duration(t) + 11``, which :func:`bonus_rate` passes back as ``t``, the
    same number only where the two clocks coincide.  Every month of a policy year reads the
    rate declared at that month, so a declared rate is a property of the policy year
    rather than of the month.
    """
    return t + 11 - duration_mth(t) % 12


def is_guarantee_date(t):
    """Whether month t ends on a contractual guarantee date.

    A guarantee date is an anniversary, so it falls at the end of a declaration month
    whose ``policy_year(t)`` is one of the guarantee years.  An exit there is MVR-free
    and pays the full guaranteed benefit plus final bonus, which is the option
    :func:`guarantee_exercise` is exercising.  In the other eleven months of the same
    policy year the window is shut and an exit bears the market value reduction like any
    other - a distinction an annual grid could not draw.  False outside cover.
    """
    return is_declaration_month(t) and is_guarantee_year(policy_year(t))


def premium_pp(t):
    """P(t): the premium received at the start of month t.

    A twelfth of the annual regular premium on the endowment chassis - the model point
    carries the premium per year, the unit a policy document states it in, and it is
    collected monthly by direct debit **[std]** - plus the single premium in the issue
    month, ``duration_mth(t) == 0``, on the policy clock: :mod:`~.WP_UK_S` adds it at
    ``t == 0``, which on the valuation clock is every policy's valuation month, so every
    bond in force would pay its single premium again.  0 outside cover.  A premium past
    the largest float, the single premium and the regular premium's twelfth summed, is
    refused in its issue month, naming both.
    """
    if not is_active(t):
        return 0.0
    p = premium_regular_pp() / 12.0
    if duration_mth(t) == 0:
        p += premium_single_pp()
        if not p - p == 0.0:
            raise ValueError(
                f"point_id {point_id()}: the premium premium_pp({t}) is {p}, not a finite "  # noqa: F821
                f"number, from the single premium {premium_single_pp()} and the regular "
                f"premium's twelfth {premium_regular_pp() / 12.0}")
    return p


def wd_pp(t):
    """W(t): the partial withdrawal paid at the start of month t.

    A twelfth of the annual election, which is taken as a fraction of the **original**
    premium - the form the MVR-free allowance is expressed in - and zero in the base
    run.  Within the allowance it is MVR-free.  Taking the year's allowance in twelve
    instalments rather than one is the ordinary way a bond's withdrawal facility is
    operated, and it is what the monthly grid lets the model say.

    Capped at the unit fund it is cancelled out of, the opening ``FV`` of the period.
    The cap is a physical
    constraint rather than a product rule: a level withdrawal against a fund that is
    being run down eventually exhausts it, and an uncapped election drives the unit
    holding - and with it the guaranteed benefit - negative.  Note what the cap is
    measured against: the *unit* fund, not the pre-MVR policy value, because a partial
    withdrawal cancels units and the final bonus is only paid on full encashment.  The
    residual final bonus reaches the policyholder in the encashment that
    :func:`is_forced_encashment` marks.  0 outside cover.
    """
    if not is_active(t):
        return 0.0
    w = wd_rate() * premium_single_pp() / 12.0
    if w <= 0.0:
        return 0.0
    return min(w, max(0.0, guar_benefit_open(t)))


def wd_as_pp(t):
    """W_AS(t): the asset-share reduction for the month's withdrawal.

    Pro rata to the **pre-MVR policy value** the month opens with, so a withdrawal
    takes the same proportion of the asset share as it takes of what the policy is worth
    - not the same cash amount.  Zero where nothing is withdrawn or the policy value is
    nil.  A product past the largest float is refused in the month it first is.
    """
    w = wd_pp(t)
    if w <= 0.0:
        return 0.0
    pv = policy_value_open(t)
    if pv <= 0.0:
        return 0.0
    v = asset_share_at(t, BEF_PREM) * w / pv
    if not v - v == 0.0:
        raise ValueError(
            f"point_id {point_id()}: the asset share's withdrawal wd_as_pp({t}) is {v}, not a "  # noqa: F821
            f"finite number, from the opening asset share {asset_share_at(t, BEF_PREM)}, "
            f"the withdrawal {w} and the policy value {pv}")
    return v


def guar_charge_rate(t):
    """c_g: the **annual** guarantee and smoothing charge on the asset share **[std]**.

    0.10% a year, and it **stops** once cumulative deductions reach the lifetime cap of
    2% of the asset share.  The cap test is measured on the balance the month opens
    with rather than on its own closing one, which is what keeps the charge from
    depending on the balance it is being deducted from; on this grid it is tested every
    month rather than once a year, so the charge switches off the month the cumulative
    overtakes the threshold instead of at the following anniversary.  The cumulative the
    first month on the books opens with is :func:`guar_charge_cum_pp_init`, the charges
    taken before the valuation date, where :mod:`~.WP_UK_S` opens at 0.

    Note what the cap is a fraction *of*.  The notes set it against the **current** asset
    share, not against a level struck once at first breach, so on a fund that keeps
    growing the threshold grows with it: the charge stops the year the cumulative
    overtakes it and resumes the year after, when the larger asset share has moved the
    threshold back above.  That is the rule as written; a cap frozen at first breach
    would be a different rule and a materially different charge.  0 outside cover.
    """
    if not is_active(t):
        return 0.0
    prev_as = asset_share_at(t, BEF_PREM)
    prev_cum = guar_charge_cum_pp(t - 1) if t > t_entry() else guar_charge_cum_pp_init()
    if prev_as > 0.0 and prev_cum >= guar_charge_cap * prev_as:      # noqa: F821
        return 0.0
    return guar_charge_rate_base                                     # noqa: F821


def guar_charge_rate_mth(t):
    """c_g monthly: ``1 - (1 - c_g)^(1/12)`` **[std]**.

    The effective conversion, so twelve months of the charge compound back to the annual
    rate the notes quote.  Zero in a month the lifetime cap has switched the charge off.
    """
    return 1.0 - (1.0 - guar_charge_rate(t)) ** (1.0 / 12.0)


def amc_rate_mth():
    """c_amc monthly: ``1 - (1 - c_amc)^(1/12)`` **[std]**.

    The same effective conversion as the guarantee charge, and for the same reason: the
    annual management charge is quoted per year and must not be restated in monthly
    units, or the basis moves with the grid.
    """
    return 1.0 - (1.0 - amc_rate) ** (1.0 / 12.0)                    # noqa: F821


def guar_charge_pp(t):
    """The guarantee and smoothing charge actually deducted in month t."""
    return guar_charge_rate_mth(t) * asset_share_at(t, AFT_RETURN)


def guar_charge_cum_pp(t):
    """CumGC(t): cumulative guarantee and smoothing deductions to the end of month t.

    Since issue: :func:`guar_charge_cum_pp_init`, the charges taken before the valuation
    date, at :func:`t_entry`, and the month's charge added in each month after, one cell a
    month.  :mod:`~.WP_UK_S` opens at nil where its frame opens, so on a policy it reopens
    in force the cap's test reads only the charges since, and the charge runs on where
    the policy's own history has stopped it.  0 outside cover.  A cumulative that leaves
    the floats is refused in the month it first does, by
    :func:`guar_charge_cum_refusal`.

    In the first month of a policy year after :func:`t_entry` the cumulative carried in is
    the year's opening, :func:`guar_charge_cum_pp_py`, which is
    ``guar_charge_cum_pp(t - 1)``, bit for bit: the chain blocked by policy year
    (UKLIB-SEC-PLAN.md K12), so that a cold read runs one cell a month within its year and
    two cells a year before it.
    """
    if not is_active(t):
        return 0.0
    if t == t_entry():
        prev = guar_charge_cum_pp_init()
    elif duration_mth(t) % 12 == 0:
        prev = guar_charge_cum_pp_py(policy_year(t))
    else:
        prev = guar_charge_cum_pp(t - 1)
    v = prev + guar_charge_pp(t)
    if not v - v == 0.0:
        return guar_charge_cum_refusal(t)
    return v


def guar_charge_cum_pp_py(y):
    """CumGC entering policy year y: the guarantee charges taken per policy to the end
    of policy year y - 1.

    The recursion blocked by policy year (UKLIB-SEC-PLAN.md K12), as ``ULB_UK_SEC``'s fund
    and ``WOL_UK_SEC``'s counts are (*Record -- M10*, *Record -- M6*): it walks the months
    of policy year ``y - 1`` on the books in ascending order, from the later of
    :func:`t_entry` and the year's first month, asking :func:`guar_charge_cum_pp` of each,
    so that each finds the month before cached and none runs a chain, and returns the year's
    last month's, :func:`guar_charge_cum_pp`'s own value, bit for bit.  So a cold read runs
    one cell a month back to its year's first month and two cells a year before it, where
    one cell a month back to :func:`t_entry` would run the contract's longest cover, 1,236
    months, on the compiled model's C stack.  :func:`guar_charge_cum_pp` and its refusal,
    :func:`guar_charge_cum_refusal` read it in the first month of policy year ``y``, in
    cover and after :func:`t_entry`, so ``y`` runs from 2 to the policy year of the longest
    cover's last month, 103 at the contract's longest, issue at ``issue_age_min``, 18, to
    ``omega_age_max``, 121 (``spec_sec.py``); no other cell reads it.
    """
    d = duration_mth_init()
    first = max(t_entry(), 12 * (y - 2) - d)
    last = 12 * (y - 1) - 1 - d
    for s in range(first, last):
        guar_charge_cum_pp(s)
    return guar_charge_cum_pp(last)


def guar_charge_cum_refusal(t):
    """The refusal of a cumulative guarantee charge past the floats in month t, in a cell
    of its own.

    :func:`guar_charge_cum_pp` is a chain, which holds a frame of each cell it recurses
    through at each level, and the frame of a compiled cell holds the code that formats
    each of its messages, run or not; so the chain calls this cell only on the error path,
    and the message is formatted here (``ULB_UK_SEC``'s form, *Record — M10*).  It takes
    the month alone, recomputes the cumulative from the same cells, the same float, and
    refuses it where it is not a finite number, naming the month, the charges carried in
    and the month's charge; where it is finite it returns it, and outside cover 0, as
    :func:`guar_charge_cum_pp` does.
    """
    if not is_active(t):
        return 0.0
    if t == t_entry():
        prev = guar_charge_cum_pp_init()
    elif duration_mth(t) % 12 == 0:
        prev = guar_charge_cum_pp_py(policy_year(t))
    else:
        prev = guar_charge_cum_pp(t - 1)
    v = prev + guar_charge_pp(t)
    if not v - v == 0.0:
        raise ValueError(
            f"point_id {point_id()}: the cumulative guarantee charge guar_charge_cum_pp({t}) "  # noqa: F821
            f"is {v}, not a finite number, from the charges carried in, {prev}, and the "
            f"month's charge, {guar_charge_pp(t)}")
    return v


def misc_surplus_pp(t):
    """M(t): estate distributions credited to the asset share; zero in the base run.

    Miscellaneous surplus and estate distributions are allocated annually where a firm
    operates them; the base model allocates none, so the rate is a monthly one only in
    the sense that nil is nil at any frequency.  A distribution past the largest float,
    which only a rate past every return makes, is refused in the month it first is.
    """
    v = misc_surplus_rate * asset_share_at(t, BEF_PREM)            # noqa: F821
    if not v - v == 0.0:
        raise ValueError(
            f"point_id {point_id()}: the estate distribution misc_surplus_pp({t}) is {v}, not "  # noqa: F821
            f"a finite number, from misc_surplus_rate {float(misc_surplus_rate)} on the "  # noqa: F821
            f"asset share {asset_share_at(t, BEF_PREM)}")
    return v


def fund_return_mth():
    """r_m = (1 + r)^(1/12) - 1: the monthly earned fund return **[std]**.

    The effective conversion of the scenario's annual return, so twelve months of it
    compound back to the annual figure exactly.  A nominal ``r/12`` would not, and on a
    -15% scenario the gap is not small.  ``Data`` refuses a ``fund_return`` of -1 or less,
    where this has no real value.
    """
    return (1.0 + fund_return()) ** (1.0 / 12.0) - 1.0


def asset_share_at(t, timing):
    """The asset share at a point inside month t.

    ``BEF_PREM``
        the balance the month **opens** with: ``AS(t-1)``, or the
        carried-in :func:`asset_share_init` in the first month on the
        books, :func:`t_entry`.  Everything that needs the opening asset
        share reads it here, so no cells indexes a month before the
        books open.

    ``BEF_RETURN``
        the opening balance plus the start-of-month premium, less the
        withdrawal: ``AS(t-1) + P(t) - W_AS(t)``.

    ``AFT_RETURN``
        after the month's fund return.

    ``AFT_CHARGE``
        after the annual management charge and the guarantee charge, both
        at their monthly equivalents.

    ``AFT_ST``
        after the shareholder transfer, which is charged to asset shares.
        It is nil in eleven months out of twelve, because a transfer
        arises only on a declaration.  **This is the balance the mortality
        charge's sum at risk is measured against.**

    ``AFT_MC``
        after the mortality charge and any estate distribution; the
        closing asset share of the month before its floor at 0, which
        :func:`asset_share` applies.

    The steps are exposed individually because their order is contractual discipline
    rather than arithmetic convenience, and the order survives the change of grid
    unchanged: return, then charges, then the transfer, then the mortality charge on the
    balance the transfer left.  :func:`asset_share` writes the same steps inline, for the
    chain; each timing here reads it at ``t - 1``, a month back, through ``BEF_PREM``.
    0 outside cover, at every timing.
    """
    if timing == BEF_PREM:
        if not is_active(t):
            return 0.0
        if t == t_entry():
            return asset_share_init()
        return asset_share(t - 1)
    if timing == BEF_RETURN:
        return asset_share_at(t, BEF_PREM) + premium_pp(t) - wd_as_pp(t)
    if timing == AFT_RETURN:
        return asset_share_at(t, BEF_RETURN) * (1.0 + fund_return_mth())
    if timing == AFT_CHARGE:
        return (asset_share_at(t, AFT_RETURN)
                * (1.0 - amc_rate_mth() - guar_charge_rate_mth(t)))
    if timing == AFT_ST:
        return asset_share_at(t, AFT_CHARGE) - shareholder_transfer_pp(t)
    if timing == AFT_MC:
        return (asset_share_at(t, AFT_ST) - mort_charge_pp(t)
                + misc_surplus_pp(t))
    raise ValueError("invalid timing")


def asset_share(t):
    """AS(t): the asset share at the end of month t.

    A **shadow retrospective accumulation**: nobody owns it and nobody is paid it.  It
    drives claim amounts only through the bonus, smoothing and MVR machinery, and the
    difference between what is paid and what it says is absorbed by the estate.

    **Floored at zero.**  The charges and the mortality charge are deductions that do not
    stop when the balance runs out, so a sustained adverse scenario - the shipped down
    cell holds its -15% for the whole projection - drives the raw recursion negative.
    A negative asset share would make the payout *target* negative and invert the
    corridor, whose bounds are ``0.80 AS`` and ``1.20 AS``.  What a nil asset share
    actually means is that the fund backing the policy is exhausted and the guarantee is
    being met entirely by the estate, which is what :func:`smoothing_account` then
    records.

    Written here inline, the month's premium and withdrawal, fund return, charges,
    shareholder transfer, mortality charge and estate distribution in
    :func:`asset_share_at`'s order and its floats, on the opening balance, the
    carried-in :func:`asset_share_init` at :func:`t_entry` and the month before's
    ``AS(t-1)`` after it, read first: so the chain of calls from month t back to
    :func:`t_entry` is one cell a month, where :mod:`~.WP_UK_S`'s ``max(0,
    asset_share_at(t, AFT_MC))`` runs through its six timings to ``asset_share(t-1)``,
    seven cells a month, 5,042 deep cold in its last month on the worked example's bond.
    ``asset_share_at(t, AFT_MC)`` floored is this, bit for bit.  0 outside cover.

    A balance whose month leaves the floats is refused there, before its floor, which
    would read ``-inf`` or a NaN as an exhausted share, by :func:`asset_share_refusal`.

    In the first month of a policy year after :func:`t_entry` the balance carried in is the
    year's opening, :func:`asset_share_py`, which is ``asset_share(t - 1)``, bit for bit:
    the chain blocked by policy year (UKLIB-SEC-PLAN.md K12), so that a cold read runs one
    cell a month within its year and two cells a year before it.
    """
    if not is_active(t):
        return 0.0
    if t == t_entry():
        opened = asset_share_init()
    elif duration_mth(t) % 12 == 0:
        opened = asset_share_py(policy_year(t))
    else:
        opened = asset_share(t - 1)
    before = opened + premium_pp(t) - wd_as_pp(t)
    after_return = before * (1.0 + fund_return_mth())
    after_charge = after_return * (1.0 - amc_rate_mth() - guar_charge_rate_mth(t))
    after_st = after_charge - shareholder_transfer_pp(t)
    after_mc = after_st - mort_charge_pp(t) + misc_surplus_pp(t)
    if not after_mc - after_mc == 0.0:
        return asset_share_refusal(t)
    return max(0.0, after_mc)


def asset_share_py(y):
    """AS entering policy year y: the asset share policy year y - 1 closes on.

    The recursion blocked by policy year (UKLIB-SEC-PLAN.md K12), as ``ULB_UK_SEC``'s fund
    and ``WOL_UK_SEC``'s counts are (*Record -- M10*, *Record -- M6*): it walks the months
    of policy year ``y - 1`` on the books in ascending order, from the later of
    :func:`t_entry` and the year's first month, asking :func:`asset_share` of each, so that
    each finds the month before cached and none runs a chain, and returns the year's last
    month's, :func:`asset_share`'s own value, bit for bit.  So a cold read runs one cell a
    month back to its year's first month and two cells a year before it, where one cell a
    month back to :func:`t_entry` would run the contract's longest cover, 1,236 months, on
    the compiled model's C stack.  :func:`asset_share` read it in the first month of policy
    year ``y``, in cover and after :func:`t_entry`, so ``y`` runs from 2 to the policy year
    of the longest cover's last month, 103 at the contract's longest, issue at
    ``issue_age_min``, 18, to ``omega_age_max``, 121 (``spec_sec.py``); no other cell reads
    it.
    """
    d = duration_mth_init()
    first = max(t_entry(), 12 * (y - 2) - d)
    last = 12 * (y - 1) - 1 - d
    for s in range(first, last):
        asset_share(s)
    return asset_share(last)


def asset_share_refusal(t):
    """The refusal of an asset share past the floats in month t, in a cell of its own.

    :func:`asset_share` is a chain, and calls this cell only on the error path, so that
    the message is formatted in this cell's frame and in no frame the chain holds
    (``ULB_UK_SEC``'s form, *Record — M10*).  It takes the month alone, reads the month's
    closing balance before its floor from :func:`asset_share_at`, the same float, and
    refuses it where it is not a finite number, naming the month and what makes it: the
    opening balance, the premium, ``fund_return``, the shareholder transfer and the
    mortality charge, any of which may be the cause.  Where it is finite it returns the
    balance floored, :func:`asset_share`'s value, and outside cover 0, as it does.
    """
    if not is_active(t):
        return 0.0
    v = asset_share_at(t, AFT_MC)
    if not v - v == 0.0:
        raise ValueError(
            f"point_id {point_id()}: the asset share of month {t} before its floor, "  # noqa: F821
            f"asset_share_at({t}, 'AFT_MC'), is {v}, not a finite number, from the "
            f"opening asset share {asset_share_at(t, BEF_PREM)}, the premium "
            f"{premium_pp(t)}, fund_return {fund_return()}, the shareholder transfer "
            f"{shareholder_transfer_pp(t)} and the mortality charge {mort_charge_pp(t)}")
    return max(0.0, v)


def unit_price(t):
    """Q(t): the with-profits unit price at the end of month t.

    ``Q(t) = Q(t-1)(1 + b)`` in a **declaration month** and ``Q(t) = Q(t-1)`` in the
    other eleven: the price is a step function of the policy year, because the
    declaration that moves it is an annual act of discretion.  It **never decreases** -
    the non-negative bonus is a contractual floor, which is what makes a declaration
    irreversible.  The first month on the books opens at :func:`unit_price_init`, the
    price the declarations before the valuation date left, or a new policy's seed price;
    one cell a month after it.  The endowment carries its guarantee as an amount rather
    than a price, and no formula reads this on it.  0 outside cover.  A price that leaves
    the floats is refused in the month it first does, by :func:`unit_price_refusal`.

    In the first month of a policy year after :func:`t_entry` the price carried in is the
    year's opening, :func:`unit_price_py`, which is ``unit_price(t - 1)``, bit for bit: the
    chain blocked by policy year (UKLIB-SEC-PLAN.md K12), so that a cold read runs one
    cell a month within its year and two cells a year before it.
    """
    if not is_active(t):
        return 0.0
    if t == t_entry():
        q = unit_price_init()
    elif duration_mth(t) % 12 == 0:
        q = unit_price_py(policy_year(t))
    else:
        q = unit_price(t - 1)
    v = q * (1.0 + bonus_rate(t)) if is_declaration_month(t) else q
    if not v - v == 0.0:
        return unit_price_refusal(t)
    return v


def unit_price_py(y):
    """Q entering policy year y: the unit price policy year y - 1 closes on.

    The recursion blocked by policy year (UKLIB-SEC-PLAN.md K12), as ``ULB_UK_SEC``'s fund
    and ``WOL_UK_SEC``'s counts are (*Record -- M10*, *Record -- M6*): it walks the months
    of policy year ``y - 1`` on the books in ascending order, from the later of
    :func:`t_entry` and the year's first month, asking :func:`unit_price` of each, so that
    each finds the month before cached and none runs a chain, and returns the year's last
    month's, :func:`unit_price`'s own value, bit for bit.  So a cold read runs one cell a
    month back to its year's first month and two cells a year before it, where one cell a
    month back to :func:`t_entry` would run the contract's longest cover, 1,236 months, on
    the compiled model's C stack.  :func:`unit_price` and its refusal,
    :func:`unit_price_refusal` read it in the first month of policy year ``y``, in cover and
    after :func:`t_entry`, so ``y`` runs from 2 to the policy year of the longest cover's
    last month, 103 at the contract's longest, issue at ``issue_age_min``, 18, to
    ``omega_age_max``, 121 (``spec_sec.py``); no other cell reads it.
    """
    d = duration_mth_init()
    first = max(t_entry(), 12 * (y - 2) - d)
    last = 12 * (y - 1) - 1 - d
    for s in range(first, last):
        unit_price(s)
    return unit_price(last)


def unit_price_refusal(t):
    """The refusal of a unit price past the floats in month t, in a cell of its own.

    :func:`unit_price`'s, on its error path alone (``ULB_UK_SEC``'s form, *Record —
    M10*): it takes the month alone, recomputes the price from the same cells, the same
    float, and refuses it where it is not a finite number, naming the month, the price the
    month opens with and the bonus rate declared; where it is finite it returns it, and
    outside cover 0, as :func:`unit_price` does.
    """
    if not is_active(t):
        return 0.0
    if t == t_entry():
        q = unit_price_init()
    elif duration_mth(t) % 12 == 0:
        q = unit_price_py(policy_year(t))
    else:
        q = unit_price(t - 1)
    v = q * (1.0 + bonus_rate(t)) if is_declaration_month(t) else q
    if not v - v == 0.0:
        raise ValueError(
            f"point_id {point_id()}: the unit price unit_price({t}) is {v}, not a finite "  # noqa: F821
            f"number, from the opening price {q} and the bonus rate {bonus_rate(t)}")
    return v


def units(t):
    """U(t): the units held at the end of month t.

    Bought with the month's premium at the price it opens with and cancelled to fund
    the month's withdrawal.  Constant in the base run, where the bond is single premium
    and nothing is withdrawn after its issue month.  The first month on the books opens
    with :func:`units_init`, the units held before the valuation date, or none on a policy
    not yet in force, whose single premium buys its units in its issue month; one cell a
    month after it.  Nil on the endowment chassis, which carries its guarantee as an
    amount rather than as units at a price, and outside cover.  Units that leave the
    floats are refused in the month they first do, by :func:`units_refusal`.

    In the first month of a policy year after :func:`t_entry` the units carried in is the
    year's opening, :func:`units_py`, which is ``units(t - 1)``, bit for bit: the
    chain blocked by policy year (UKLIB-SEC-PLAN.md K12), so that a cold read runs one
    cell a month within its year and two cells a year before it.
    """
    if not is_unitised() or not is_active(t):
        return 0.0
    if t == t_entry():
        u = units_init()
    elif duration_mth(t) % 12 == 0:
        u = units_py(policy_year(t))
    else:
        u = units(t - 1)
    q = unit_price_init() if t == t_entry() else unit_price(t - 1)
    if q <= 0.0:
        return u
    v = u + prem_alloc_rate * premium_pp(t) / q - wd_pp(t) / q       # noqa: F821
    if not v - v == 0.0:
        return units_refusal(t)
    return v


def units_py(y):
    """U entering policy year y: the units policy year y - 1 closes on.

    The recursion blocked by policy year (UKLIB-SEC-PLAN.md K12), as ``ULB_UK_SEC``'s fund
    and ``WOL_UK_SEC``'s counts are (*Record -- M10*, *Record -- M6*): it walks the months
    of policy year ``y - 1`` on the books in ascending order, from the later of
    :func:`t_entry` and the year's first month, asking :func:`units` of each, so that each
    finds the month before cached and none runs a chain, and returns the year's last
    month's, :func:`units`'s own value, bit for bit.  So a cold read runs one cell a month
    back to its year's first month and two cells a year before it, where one cell a month
    back to :func:`t_entry` would run the contract's longest cover, 1,236 months, on the
    compiled model's C stack.  :func:`units` and its refusal, :func:`units_refusal` read it
    in the first month of policy year ``y``, in cover and after :func:`t_entry`, so ``y``
    runs from 2 to the policy year of the longest cover's last month, 103 at the contract's
    longest, issue at ``issue_age_min``, 18, to ``omega_age_max``, 121 (``spec_sec.py``); no
    other cell reads it.
    """
    d = duration_mth_init()
    first = max(t_entry(), 12 * (y - 2) - d)
    last = 12 * (y - 1) - 1 - d
    for s in range(first, last):
        units(s)
    return units(last)


def units_refusal(t):
    """The refusal of units past the floats in month t, in a cell of its own.

    :func:`units`'s, on its error path alone (``ULB_UK_SEC``'s form, *Record — M10*): it
    takes the month alone, recomputes the units from the same cells, the same float, and
    refuses them where they are not a finite number, naming the month, the units and the
    price the month opens with and its premium; where finite it returns them, and elsewhere
    what :func:`units` returns, under its guards.
    """
    if not is_unitised() or not is_active(t):
        return 0.0
    if t == t_entry():
        u = units_init()
    elif duration_mth(t) % 12 == 0:
        u = units_py(policy_year(t))
    else:
        u = units(t - 1)
    q = unit_price_init() if t == t_entry() else unit_price(t - 1)
    if q <= 0.0:
        return u
    v = u + prem_alloc_rate * premium_pp(t) / q - wd_pp(t) / q       # noqa: F821
    if not v - v == 0.0:
        raise ValueError(
            f"point_id {point_id()}: the units held units({t}) are {v}, not a finite "  # noqa: F821
            f"number, from the opening units {u} at the price {q} and the premium "
            f"{premium_pp(t)}")
    return v


def guar_benefit_pp(t):
    """The guaranteed benefit at the end of month t.

    The unit face value ``U(t) Q(t)`` on the bond chassis, and the sum assured plus
    attaching reversionary bonuses on the endowment, where ``G(t) = G(t-1)(1 + b)`` in a
    declaration month and ``G(t) = G(t-1)`` in the other eleven.  Two contractual forms,
    one cells: every rule that consumes it - the bonus cost, the mortality charge's sum
    at risk, the final bonus, the MVR - treats them identically, so keeping two names
    would duplicate five rules to no purpose.

    The endowment's is written here inline, on the guarantee the month opens with, the
    carried-in ``sum_assured() + attaching_bonus_init()`` at :func:`t_entry` and ``G(t-1)``
    after it, so that its chain is one cell a month, where :mod:`~.WP_UK_S`'s runs through
    :func:`guar_benefit_open`, two.  0 outside cover.  A guarantee that leaves the floats
    is refused in the month it first does, by :func:`guar_benefit_refusal`.

    In the first month of a policy year after :func:`t_entry` the endowment's guarantee
    carried in is the year's opening, :func:`guar_benefit_pp_py`, which is
    ``guar_benefit_pp(t - 1)``, bit for bit: the chain blocked by policy year
    (UKLIB-SEC-PLAN.md K12), so that a cold read runs one cell a month within its year and
    two cells a year before it.
    """
    if not is_active(t):
        return 0.0
    if is_unitised():
        v = units(t) * unit_price(t)
    else:
        if t == t_entry():
            g = sum_assured() + attaching_bonus_init()
        elif duration_mth(t) % 12 == 0:
            g = guar_benefit_pp_py(policy_year(t))
        else:
            g = guar_benefit_pp(t - 1)
        v = g * (1.0 + bonus_rate(t)) if is_declaration_month(t) else g
    if not v - v == 0.0:
        return guar_benefit_refusal(t)
    return v


def guar_benefit_pp_py(y):
    """G entering policy year y, on the endowment: the guarantee policy year y - 1 closes
    on.

    The recursion blocked by policy year (UKLIB-SEC-PLAN.md K12), as ``ULB_UK_SEC``'s fund
    and ``WOL_UK_SEC``'s counts are (*Record -- M10*, *Record -- M6*): it walks the months
    of policy year ``y - 1`` on the books in ascending order, from the later of
    :func:`t_entry` and the year's first month, asking :func:`guar_benefit_pp` of each, so
    that each finds the month before cached and none runs a chain, and returns the year's
    last month's, :func:`guar_benefit_pp`'s own value, bit for bit.  So a cold read runs one
    cell a month back to its year's first month and two cells a year before it, where one
    cell a month back to :func:`t_entry` would run the contract's longest cover, 1,236
    months, on the compiled model's C stack.  :func:`guar_benefit_pp` and its refusal,
    :func:`guar_benefit_refusal` read it in the first month of policy year ``y``, in cover
    and after :func:`t_entry`, so ``y`` runs from 2 to the policy year of the longest
    cover's last month, 103 at the contract's longest, issue at ``issue_age_min``, 18, to
    ``omega_age_max``, 121 (``spec_sec.py``); no other cell reads it.
    """
    d = duration_mth_init()
    first = max(t_entry(), 12 * (y - 2) - d)
    last = 12 * (y - 1) - 1 - d
    for s in range(first, last):
        guar_benefit_pp(s)
    return guar_benefit_pp(last)


def guar_benefit_refusal(t):
    """The refusal of a guaranteed benefit past the floats in month t, in a cell of its
    own.

    :func:`guar_benefit_pp`'s, on its error path alone (``ULB_UK_SEC``'s form, *Record —
    M10*): it takes the month alone, recomputes the guarantee from the same cells, the same
    float, and refuses it where it is not a finite number, naming the month and what makes
    it, the units and the price on the bond and on the endowment the guarantee the month
    opens with and the bonus rate; where finite it returns it, and outside cover 0, as
    :func:`guar_benefit_pp` does.
    """
    if not is_active(t):
        return 0.0
    if is_unitised():
        v = units(t) * unit_price(t)
        if not v - v == 0.0:
            raise ValueError(
                f"point_id {point_id()}: the guaranteed benefit guar_benefit_pp({t}) is {v}, "  # noqa: F821
                f"not a finite number, from {units(t)} units at the price {unit_price(t)}")
        return v
    if t == t_entry():
        g = sum_assured() + attaching_bonus_init()
    elif duration_mth(t) % 12 == 0:
        g = guar_benefit_pp_py(policy_year(t))
    else:
        g = guar_benefit_pp(t - 1)
    v = g * (1.0 + bonus_rate(t)) if is_declaration_month(t) else g
    if not v - v == 0.0:
        raise ValueError(
            f"point_id {point_id()}: the guaranteed benefit guar_benefit_pp({t}) is {v}, "  # noqa: F821
            f"not a finite number, from the opening guarantee {g} and the bonus rate "
            f"{bonus_rate(t)}")
    return v


def guar_benefit_open(t):
    """The guaranteed benefit month t **opens** with: ``FV(t-1)`` or ``G(t-1)``.

    The carried-in guarantee in the first month on the books - the unit face value of
    :func:`units_init` at :func:`unit_price_init` on the bond chassis, the sum assured plus
    :func:`attaching_bonus_init` on the endowment - and the previous month's closing value
    after that.  A declaration is measured against the value its own month opens with,
    and the withdrawal is capped at it.  0 outside cover.  An opening guarantee past the
    largest float, the product or the sum of two opening columns, is refused in the first
    month on the books.
    """
    if not is_active(t):
        return 0.0
    if t > t_entry():
        return guar_benefit_pp(t - 1)
    if is_unitised():
        v = units_init() * unit_price_init()
        if not v - v == 0.0:
            raise ValueError(
                f"point_id {point_id()}: the guarantee the books open with, "  # noqa: F821
                f"guar_benefit_open({t}), is {v}, not a finite number, from {units_init()} "
                f"units at the price {unit_price_init()}")
        return v
    v = sum_assured() + attaching_bonus_init()
    if not v - v == 0.0:
        raise ValueError(
            f"point_id {point_id()}: the guarantee the books open with, guar_benefit_open({t}), "  # noqa: F821
            f"is {v}, not a finite number, from the sum assured {sum_assured()} and the "
            f"attaching bonus {attaching_bonus_init()}")
    return v


def policy_value_pp(t):
    """The pre-MVR policy value at the end of month t: guarantee plus final bonus.

    What an MVR is measured against.
    """
    return guar_benefit_pp(t) + final_bonus_pp(t)


def policy_value_open(t):
    """The pre-MVR policy value month t **opens** with.

    The same guarantee-plus-final-bonus sum as :func:`policy_value_pp`, on the values
    the month opens with, and what a start-of-month withdrawal is taken pro rata to.
    """
    return guar_benefit_open(t) + max(
        0.0, smoothed_payout_open(t) - guar_benefit_open(t))


def bonus_supportable(t):
    """b_supp: the level bonus rate that fills the guarantee to the target **[std]**.

    Project the asset share to the horizon at the expected net return, take
    ``guar_fill_target`` of it, and solve for the level rate that grows the current
    guaranteed benefit to that amount::

        b_supp = [theta AS_proj / GB(t)]^(1/m) - 1

    with ``m`` the remaining endowment term in **years** - the term less the policy year
    the declaration closes, ``policy_term() - policy_year(t)`` - or the bond's
    bonus-setting horizon.  Future premiums are accumulated to the horizon at the same
    net return.  Everything in the rule is annual, because the rate it sets is: the grid
    is monthly but the discretion cycle is not.  Read only at a declaration month, and
    only when ``bonus_rule_on`` is set.

    The growth factor ``(1 + r_e)^m`` is raised once and read twice, the float
    :mod:`~.WP_UK_S` raises twice.  ``bonus_horizon`` is read as it is, an integer, which
    :func:`proj_len` holds it to be, so that ``m`` is a C integer compiled, and printed as
    the ``int`` it is: a whole number written as a float, ``10.0``, raises and divides as
    ``10`` does.  A factor past the largest float, which only a return or a horizon past
    every bond's makes, is refused, naming the point and the References: Python's power
    raises ``OverflowError`` there, naming neither, and C's gives an infinity, so where the
    power is infinite from a finite base the cell calls Python's own, uslib's M22 form
    (USLIB-SEC-PLAN.md, *Record -- M22*), which raises the same ``OverflowError`` in the
    compiled model as in modelx, and the one ``except`` around both turns it into the
    refusal, in either engine, ``PA_UK_SEC``'s form (*Record — M11*, *Record — M12*);
    modelx never reaches the call, its own power raising first.  So is a factor below the
    smallest float, which a horizon long enough makes of a return net of charges below 0,
    and which would read as no asset share at the horizon.  So is a rate past the floats,
    which a projected asset share or a target past them makes.
    """
    m = (bonus_horizon if is_unitised()                              # noqa: F821
         else max(1, policy_term() - policy_year(t)))
    r_e = fund_return() - amc_rate - guar_charge_rate(t)             # noqa: F821
    base = 1.0 + r_e
    try:
        grown = base ** m
        if grown - grown != 0.0 and base - base == 0.0:
            raise float.__pow__(base, m)
    except OverflowError:
        raise ValueError(
            f"point_id {point_id()}: the bonus rule's growth factor (1 + r_e)^m in "  # noqa: F821
            f"bonus_supportable({t}) is past the largest float, under fund_return "
            f"{fund_return()}, amc_rate {float(amc_rate)}, the guarantee charge's rate "  # noqa: F821
            f"{guar_charge_rate(t)} and a horizon of {int(m)} years") from None
    if not abs(grown) <= 1.7976931348623157e308:
        raise ValueError(
            f"point_id {point_id()}: the bonus rule's growth factor (1 + r_e)^m in "  # noqa: F821
            f"bonus_supportable({t}) is past the largest float, under fund_return "
            f"{fund_return()}, amc_rate {float(amc_rate)}, the guarantee charge's rate "  # noqa: F821
            f"{guar_charge_rate(t)} and a horizon of {int(m)} years")
    if grown == 0.0 and 1.0 + r_e != 0.0:
        raise ValueError(
            f"point_id {point_id()}: the bonus rule's growth factor (1 + r_e)^m in "  # noqa: F821
            f"bonus_supportable({t}) is 0.0, below the smallest float, under fund_return "
            f"{fund_return()}, amc_rate {float(amc_rate)}, the guarantee charge's rate "  # noqa: F821
            f"{guar_charge_rate(t)} and a horizon of {int(m)} years")
    proj = asset_share_at(t, BEF_PREM) * grown
    p = premium_regular_pp()
    if p > 0.0:
        if abs(r_e) < 1e-12:
            proj += p * m
        else:
            proj += p * (1.0 + r_e) * (grown - 1.0) / r_e
    gb = guar_benefit_open(t)
    if gb <= 0.0 or proj <= 0.0:
        return 0.0
    v = (guar_fill_target * proj / gb) ** (1.0 / m) - 1.0            # noqa: F821
    if not v - v == 0.0:
        raise ValueError(
            f"point_id {point_id()}: the supportable bonus rate bonus_supportable({t}) is {v}, "  # noqa: F821
            f"not a finite number, from the projected asset share {proj}, guar_fill_target "
            f"{float(guar_fill_target)} and the guarantee the month opens with, {gb}")  # noqa: F821
    return v


def bonus_rate(t):
    """b: the annual regular or reversionary bonus rate for the policy year holding t.

    A declared rate is a property of the **policy year**, not of the month, so every
    month of a year reads the rate set at that year's :func:`declaration_month`.  The
    base projection holds the model point's rate level, :func:`bonus_rate_init`, which is
    what the notes do.  With ``bonus_rule_on`` set, the smoothed setting rule applies once
    a year instead::

        b(y) = max(0, b(y-1) + clamp(kappa (b_supp - b(y-1)), -1%, +1%))

    The floor at zero is contractual - a declared bonus can be nil but never negative -
    and the plus or minus one percent is the gradual-change discipline firms state in
    their principles and practices, which is a discipline **per declaration** and would
    be a different rule applied twelve times a year.

    Every declaration in the frame is the rule's, made at today's References from this
    model's own asset share and guarantee (USLIB-SEC-PLAN.md D6: an annual event at or
    after the valuation date is the projection's), the one closing the policy year under
    way among them, and a declaration at the end of month 0 is month 0's own event.  Each
    starts from the rate declared before it, ``bonus_rate(d - 12)``, a valuation month a
    year back, and the first in the frame from :func:`bonus_rate_init`, the rate declared
    at the last declaration before the valuation date.  :mod:`~.WP_UK_S`'s first
    projected year keeps its column instead, so under the rule its points in force, and a
    point valued inside that year, part from it at their first declaration in the frame,
    by D6 (``model-sec.md``).  A month before its year's declaration reads it ahead, up to
    11 months, the anniversary read R2 admits, bounded by the frame: where the frame ends
    before the year's declaration, as a forced encashment ends it mid-year, no
    declaration is made, and the year reads the rate declared before it, where
    :mod:`~.WP_UK_S` reads past its frame.  The bound changes nothing but the
    ``bonus_rate`` column of ``result_payout`` in such a year's months: no other cell reads
    the rate outside a declaration month.  0 outside cover.
    """
    if not is_active(t):
        return 0.0
    if not bonus_rule_on:                                            # noqa: F821
        return bonus_rate_init()
    d = declaration_month(t)
    if t != d:
        if d >= proj_len():
            return bonus_rate(d - 12) if d - 12 >= t_entry() else bonus_rate_init()
        return bonus_rate(d)
    prev = bonus_rate(d - 12) if d - 12 >= t_entry() else bonus_rate_init()
    step = bonus_speed * (bonus_supportable(d) - prev)               # noqa: F821
    step = max(-bonus_change_cap, min(bonus_change_cap, step))       # noqa: F821
    return max(0.0, prev + step)


def cost_of_bonus_pp(t):
    """CB(t): the cost of the bonus declared at the end of month t **[std]**.

    Zero in every month but a declaration month, because a cost arises only where a
    declaration does.  On the bond chassis it is the face-value uplift the declaration
    delivers, ``b FV`` on the face value the declaration month opened with.  On the
    endowment it is the declared addition to the guarantee discounted to the declaration
    date at the surrender-basis rate, over the ``policy_term() - policy_year(t)`` years
    still to run, since the addition is not payable until maturity; the survivorship
    discount is omitted **[std]**.  A cost that leaves the floats raises ``ValueError``
    here, in the month it first does, naming the point and what makes it; so does a
    discount past the largest float or below the smallest, which only a
    ``surr_disc_rate`` near its domain's edges makes, naming the Reference.
    """
    if not is_declaration_month(t):
        return 0.0
    if is_unitised():
        v = bonus_rate(t) * guar_benefit_open(t)
    else:
        delta = guar_benefit_pp(t) - guar_benefit_open(t)
        years = max(0, policy_term() - policy_year(t))
        base = 1.0 + surr_disc_rate                                  # noqa: F821
        try:
            discount = base ** years
            if discount - discount != 0.0 and base - base == 0.0:
                raise float.__pow__(base, years)
        except OverflowError:
            raise ValueError(
                f"point_id {point_id()}: the endowment's discount on its bonus cost, "  # noqa: F821
                f"(1 + surr_disc_rate)^{years} in cost_of_bonus_pp({t}), is past the "
                f"largest float, under surr_disc_rate {float(surr_disc_rate)}") from None  # noqa: F821
        if not discount <= 1.7976931348623157e308:
            raise ValueError(
                f"point_id {point_id()}: the endowment's discount on its bonus cost, "  # noqa: F821
                f"(1 + surr_disc_rate)^{years} in cost_of_bonus_pp({t}), is past the "
                f"largest float, under surr_disc_rate {float(surr_disc_rate)}")  # noqa: F821
        if not discount > 0.0:
            raise ValueError(
                f"point_id {point_id()}: the endowment's discount on its bonus cost, "  # noqa: F821
                f"(1 + surr_disc_rate)^{years} in cost_of_bonus_pp({t}), is 0.0, below the "
                f"smallest float, under surr_disc_rate {float(surr_disc_rate)}")  # noqa: F821
        v = delta / discount
    if not v - v == 0.0:
        raise ValueError(
            f"point_id {point_id()}: the cost of bonus cost_of_bonus_pp({t}) is {v}, not a "  # noqa: F821
            f"finite number, from the bonus rate {bonus_rate(t)} and the guarantee the "
            f"month opens with, {guar_benefit_open(t)}")
    return v


def shareholder_transfer_pp(t):
    """ST(t) = CB(t)/9: the 90:10 shareholder transfer, charged to the asset share.

    One ninth of the cost of bonus, so that shareholders receive a tenth of each
    distribution and policyholders nine tenths.  It is a real cash outflow from the fund
    and is reported as its own line, not netted into anything.  Like the cost it is
    taken from, it falls in the declaration month and is nil in the other eleven.  A
    transfer past the largest float, which only a divisor near 0 makes, is refused in the
    month it first is.
    """
    v = cost_of_bonus_pp(t) / shareholder_transfer_divisor           # noqa: F821
    if not v - v == 0.0:
        raise ValueError(
            f"point_id {point_id()}: the shareholder transfer shareholder_transfer_pp({t}) is "  # noqa: F821
            f"{v}, not a finite number, from the cost of bonus {cost_of_bonus_pp(t)} over "
            f"shareholder_transfer_divisor {float(shareholder_transfer_divisor)}")  # noqa: F821
    return v


def mort_rate(t):
    """q(x + duration(t)): the **annual** best-estimate mortality rate **[std]**.

    The shipped table rate times ``mort_be_factor``, entered at an attained age that
    advances on the policy anniversary, so the rate is level across a policy year.  Both
    are placeholders: CMI tables issued after March 2013 are subscriber-restricted, so
    the table is an ONS-shaped proxy and the factor a crude allowance for population
    mortality being heavier than insured experience.  :func:`mort_rate_mth` is what the
    projection decrements and charges by.  Capped at 1, the bound second,
    ``min(q, 1.0)``, so that a missing input, a NaN, stays NaN, where ``min(1.0, q)``
    would read it as 1: :mod:`~.WP_UK_S`'s cap, and no departure.

    Zero outside cover, where ``age(t)`` is not an age the policy reaches.  Inside it, this
    is the one cell that reads ``Data.mort_table``, at :mod:`~.WP_UK_S`'s key, its age
    bounded by ``omega_age``, which in cover it never reaches.  An age outside the table's,
    ``Data.mort_age_first`` to ``Data.mort_age_last``, raises ``ValueError``, naming the
    point and the age, where :mod:`~.WP_UK_S`'s lookup raised ``KeyError``.
    """
    if not is_active(t):
        return 0.0
    x = min(age(t), omega_age)                                       # noqa: F821
    if x < data.mort_age_first() or x > data.mort_age_last():        # noqa: F821
        raise ValueError(f"point_id {point_id()}: mort_table.csv has no rate at "
                         f"attained age {x}")
    return min(float(data.mort_table_array()[mort_schedule(), x])    # noqa: F821
               * mort_be_factor, 1.0)                                # noqa: F821


def mort_rate_mth(t):
    """q_m(t) = 1 - (1 - q)^(1/12): the monthly mortality rate **[std]**.

    Twelve months compound back to the table's annual rate exactly, so the in-force at
    each anniversary is what an annual-step roll-forward of the same table would give.
    """
    return 1.0 - (1.0 - mort_rate(t)) ** (1.0 / 12.0)


def death_guar_pp(t):
    """DB_g(t): the **guaranteed** death benefit, the mortality charge's sum-at-risk top.

    ``g_db x FV(t)`` on the bond chassis, where the death benefit carries a 101% uplift,
    and ``G(t)`` on the endowment.  Only the guaranteed element enters the sum at risk
    **[std]**: the final bonus is not guaranteed, so charging for it would charge the
    asset share for a benefit the fund has not promised.  An uplifted guarantee past the
    largest float is refused in the month it first is.
    """
    if not is_unitised():
        return guar_benefit_pp(t)
    v = death_benefit_factor * guar_benefit_pp(t)                    # noqa: F821
    if not v - v == 0.0:
        raise ValueError(
            f"point_id {point_id()}: the guaranteed death benefit death_guar_pp({t}) is {v}, "  # noqa: F821
            f"not a finite number, from death_benefit_factor "
            f"{float(death_benefit_factor)} on the guarantee {guar_benefit_pp(t)}")  # noqa: F821
    return v


def mort_charge_pp(t):
    """MC(t): the mortality charge deducted from the asset share in month t.

    ``q_m x max(0, DB_g(t) - AS_after_ST)``: the **monthly** mortality rate times the
    sum at risk, measured on the balance **after** the shareholder transfer.  Differences
    between charged and actual mortality accrue to the estate, which is why this is a
    charge rather than a claim.  In the eleven months before a declaration the sum at
    risk is measured against the guarantee as it then stands; the declaration month's
    charge is the first to carry the hardened one.  0 outside cover, where no mortality
    rate is read.
    """
    if not is_active(t):
        return 0.0
    return mort_rate_mth(t) * max(0.0, death_guar_pp(t)
                                  - asset_share_at(t, AFT_ST))


def smooth_cap_dn_mth():
    """The monthly floor factor of the smoothing cap: ``(1 - sigma)^(1/12)`` **[std]**.

    The notes' cap is a **year-on-year** discipline: a payout may not move more than
    ``sigma`` from one year to the next.  Twelve of these compound to exactly
    ``1 - sigma``, so the annual discipline survives the change of grid intact while the
    payout itself is recomputed every month.  Converting the cap instead to a flat
    ``sigma`` per month would loosen it twelvefold and stop it being the notes' rule.
    """
    return (1.0 - smooth_cap) ** (1.0 / 12.0)                        # noqa: F821


def smooth_cap_up_mth():
    """The monthly ceiling factor of the smoothing cap: ``(1 + sigma)^(1/12)`` **[std]**."""
    return (1.0 + smooth_cap) ** (1.0 / 12.0)                        # noqa: F821


def smoothed_payout_capped(t):
    """S_cap: the asset share after the month-on-month smoothing cap, before the corridor.

    ``clamp(AS(t), (1 - sigma)^(1/12) S(t-1), (1 + sigma)^(1/12) S(t-1))`` at
    ``sigma = 10%``.  This is what stops a market shock reaching payouts in one step,
    and it is applied **before** the corridor.  Twelve capped months compound to the
    notes' ``+/- 10%`` year-on-year band exactly, so a payout that is capped every month
    of a policy year has moved by exactly ``sigma`` over it - which is what the notes'
    down scenario does.

    The cap is **skipped where there is no previous payout** to compare against - the
    issue month of a new-business cell, where the opening ``S`` is nil and the cap
    would otherwise clamp the payout to nil and leave the corridor to do all the work,
    and any month that opens on a nil payout.  See the Space docstring on what the cap can
    and cannot say about a premium-paying policy.  :func:`smoothed_payout` writes the
    same clamp inline, for the chain.
    """
    prev = smoothed_payout_open(t)
    if prev <= 0.0:
        return asset_share(t)
    lo = smooth_cap_dn_mth() * prev
    hi = smooth_cap_up_mth() * prev
    return max(lo, min(hi, asset_share(t)))


def smoothed_payout(t):
    """S(t): the smoothed target payout at the end of month t.

    The capped value, then clamped into the target corridor of 80% to 120% of the asset
    share.  The corridor is what stops the cap holding a payout indefinitely away from
    the asset share; the order - cap first, corridor second - is what produces the
    pattern the two rules are designed for.

    The regulatory target-range test is a *portfolio* property, a proportion of policies
    within the range, which a single-policy model cannot express; the deterministic
    corridor is a **[std]** reading of it.

    Written here inline, :func:`smoothed_payout_capped`'s clamp and then the corridor, in
    its order and its floats, on the payout the month opens with, the carried-in
    :func:`smoothed_payout_init` at :func:`t_entry` and ``S(t-1)`` after it, read first:
    so the payout's chain from month t back to :func:`t_entry` is one cell a month, where
    :mod:`~.WP_UK_S`'s runs through the cap and the opening payout, three.  0 outside
    cover.
    """
    if not is_active(t):
        return 0.0
    if t == t_entry():
        prev = smoothed_payout_init()
    elif duration_mth(t) % 12 == 0:
        prev = smoothed_payout_py(policy_year(t))
    else:
        prev = smoothed_payout(t - 1)
    as_t = asset_share(t)
    if prev <= 0.0:
        capped = as_t
    else:
        capped = max(smooth_cap_dn_mth() * prev,
                     min(smooth_cap_up_mth() * prev, as_t))
    lo = corridor_lo * as_t                                          # noqa: F821
    hi = corridor_hi * as_t                                          # noqa: F821
    return max(lo, min(hi, capped))


def smoothed_payout_py(y):
    """S entering policy year y: the smoothed payout policy year y - 1 closes on.

    The recursion blocked by policy year (UKLIB-SEC-PLAN.md K12), as ``ULB_UK_SEC``'s fund
    and ``WOL_UK_SEC``'s counts are (*Record -- M10*, *Record -- M6*): it walks the months
    of policy year ``y - 1`` on the books in ascending order, from the later of
    :func:`t_entry` and the year's first month, asking :func:`smoothed_payout` of each, so
    that each finds the month before cached and none runs a chain, and returns the year's
    last month's, :func:`smoothed_payout`'s own value, bit for bit.  So a cold read runs one
    cell a month back to its year's first month and two cells a year before it, where one
    cell a month back to :func:`t_entry` would run the contract's longest cover, 1,236
    months, on the compiled model's C stack.  :func:`smoothed_payout` read it in the first
    month of policy year ``y``, in cover and after :func:`t_entry`, so ``y`` runs from 2 to
    the policy year of the longest cover's last month, 103 at the contract's longest, issue
    at ``issue_age_min``, 18, to ``omega_age_max``, 121 (``spec_sec.py``); no other cell
    reads it.
    """
    d = duration_mth_init()
    first = max(t_entry(), 12 * (y - 2) - d)
    last = 12 * (y - 1) - 1 - d
    for s in range(first, last):
        smoothed_payout(s)
    return smoothed_payout(last)


def smoothed_payout_open(t):
    """S(t-1): the smoothed payout month t **opens** with.

    The carried-in :func:`smoothed_payout_init` in the first month on the books - nil on a
    new-business cell, which is what switches the cap off in its issue month - and the
    previous month's closing payout after that.  0 outside cover.
    """
    if not is_active(t):
        return 0.0
    if t > t_entry():
        return smoothed_payout(t - 1)
    return smoothed_payout_init()


def final_bonus_pp(t):
    """FB(t) or TB(t): the final or terminal bonus, ``max(0, S(t) - GB(t))``.

    The non-guaranteed top-up from the guaranteed benefit to the smoothed payout, and
    the form the discretion keeps a substantial proportion of the payout in - precisely
    because it is the part that has not hardened.
    """
    return max(0.0, smoothed_payout(t) - guar_benefit_pp(t))


def mvr_pp(t):
    """MVR(t): the market value reduction **scale** at the end of month t.

    ``min(max(0, FV - S), max(0, FV - AS))``.  The first argument recovers the shortfall
    of the smoothed payout below the unit face value; the second is the contractual
    bound - the reduction may not exceed the excess of the unit value over the
    underlying asset value.

    This is the scale, not what an exit bears: :func:`mvr_applied_pp` is zero where the
    exit is MVR-free.  Both are needed, because the behavioural deterrent keys off the
    scale being positive while the payout keys off what is applied.

    **Unitised chassis only.**  A market value reduction is a unit-linked-style
    adjustment to a *unit* value, and the notes define it for the unitised chassis
    alone; a conventional endowment has no units to reduce, and its surrender value is
    set on a surrender basis instead - see :func:`claim_pp`.  Returning zero here rather
    than applying the same arithmetic keeps the result table honest: on a conventional
    policy the face value is a maturity guarantee decades away, so ``FV - S`` is a large
    number that means nothing.
    """
    if not is_unitised():
        return 0.0
    gb = guar_benefit_pp(t)
    return min(max(0.0, gb - smoothed_payout(t)),
               max(0.0, gb - asset_share(t)))


def mvr_applied_pp(t):
    """The market value reduction an exit at the end of month t actually bears.

    Zero in a guarantee-date **month**, where the contract promises the full guaranteed
    benefit without reduction, and zero on death.  In the other eleven months of a
    guarantee year the window is shut and the reduction applies in full: the monthly
    grid can say when the option is open, where an annual one could only treat the whole
    year as the date.  The death case is handled in :func:`claim_pp` rather than here,
    because only the surrender payout reads this.  Zero throughout on the endowment
    chassis, which has no units to reduce.
    """
    if is_guarantee_date(t):
        return 0.0
    return mvr_pp(t)


def claim_pp(t, kind):
    """The payout per claim at the end of month t, by kind.

    ``DEATH``
        ``g_db (FV + FB)`` on the bond chassis - the 101% uplift applies to
        the whole payout - and ``G + TB`` on the endowment.  **Never
        MVR'd**: an MVR is not applied on death on either chassis.

    ``SURRENDER``
        ``FV + FB - MVR_applied`` on the bond chassis, the non-guaranteed
        exit.  On the endowment chassis there is no MVR, and the surrender
        value targets the smoothed payout - the asset share under the
        smoothing discipline - capped at the prospective value ``G + TB``,
        which is what the policy would be worth if it ran to maturity.
        Early surrender values are therefore well below the guaranteed
        maturity benefit, as they are on a real conventional policy.

    ``GUARANTEE``
        ``GB + FB``, what a guarantee-date exit pays.  Computed at every
        ``t`` so the two can be compared, but paid only in a month where
        :func:`is_guarantee_date` - in those months it equals the
        surrender payout, because the MVR is not applied.  The endowment
        chassis has no guarantee dates, so this is informational there.

    ``MATURITY``
        ``G + TB`` at the end of the endowment term, the last projected
        month ``proj_len() - 1``.  On the bond chassis, which is whole of
        life, this is zero unless the projection ends in a **forced
        encashment** - the withdrawal election has cancelled the last unit
        - in which case the survivors are paid ``FV + FB``, the residual
        final bonus included.  A limiting-age ending pays nothing, because
        it is a modelling truncation rather than a contractual event.
    """
    base = guar_benefit_pp(t) + final_bonus_pp(t)
    if kind == DEATH:
        if not is_unitised():
            return base
        v = death_benefit_factor * base                              # noqa: F821
        if not v - v == 0.0:
            raise ValueError(
                f"point_id {point_id()}: the death claim claim_pp({t}, DEATH) is {v}, not a "  # noqa: F821
                f"finite number, from death_benefit_factor {float(death_benefit_factor)} on "  # noqa: F821
                f"the guarantee and final bonus {base}")
        return v
    if kind == SURRENDER:
        if not is_unitised():
            return max(0.0, min(smoothed_payout(t), base))
        return base - mvr_applied_pp(t)
    if kind == GUARANTEE:
        return base
    if kind == MATURITY:
        if t != proj_len() - 1:
            return 0.0
        if is_unitised() and not is_forced_encashment():
            return 0.0
        return base
    raise ValueError("invalid kind")


def smoothing_cost_pp(t, kind):
    """The excess of a payout over the asset share, borne by the estate.

    Positive where the smoothing or a guarantee has paid more than the policy earned,
    negative where it has paid less.  Intended broadly neutral over time; the base model
    accumulates the balance in :func:`smoothing_account` without recycling it.
    """
    return claim_pp(t, kind) - asset_share(t)


def surr_rate_base(t):
    """The table **annual** surrender rate applying in month t **[std]**.

    Read from the chassis's own row of the lapse table, whose key is the **contractual
    policy year** - a 1-based label, so month t reads row ``policy_year(t)``, on the
    policy clock; policy years beyond the table take its last row,
    ``Data.lapse_last_year``, which checks the table first.  A drafting construction: no
    public UK with-profits lapse experience was retrieved.  0 outside cover, where no
    policy year is read.
    """
    if not is_active(t):
        return 0.0
    y = min(policy_year(t), lapse_last_year())
    return float(data.lapse_table_array()[chassis_code(), y])        # noqa: F821


def lapse_last_year():
    """The last policy year the lapse table gives the point's chassis a rate for.

    ``Data.lapse_last_year`` at the point's chassis, :func:`chassis_code`: the extent of
    the chassis's own rows, which :func:`surr_rate_base` reads every later policy year at,
    as :mod:`~.WP_UK_S`'s ``tbl.index.max()`` does on the chassis's rows, and which
    ``Data`` asks the table's check of before it is read.
    """
    return int(data.lapse_last_year()[chassis_code()])               # noqa: F821


def mvr_deterrent(t):
    """0.6 while an MVR would be applied, 1 otherwise **[std]**.

    An active market value reduction penalizes exit, and firms may consider exit volumes
    when setting reductions inside the contractual bound.
    """
    return mvr_deterrent_factor if mvr_applied_pp(t) > 0.0 else 1.0  # noqa: F821


def guarantee_exercise(t):
    """The one-off MVR-free encashment taken in a guarantee-date month **[std]**.

    ``guarantee_exercise_rate`` of the survivors of that month, and only **when the
    guarantee is in the money** (``GB > AS``); zero everywhere else.  The gate matters:
    MVR-free encashment is worth exercising precisely when the guaranteed benefit
    exceeds the asset share and worth nothing otherwise, so exercising unconditionally
    would invent anti-selection where there is none.  This is the dominant behavioural
    risk on with-profits business.

    This is where the monthly grid changes the *shape* of an assumption rather than only
    its frequency, and deliberately.  The annual grid could only express the exercise as
    a 2.5x multiplier on the whole guarantee-date **year**'s surrender rate, which
    spreads MVR-free exits across eleven months in which the window is shut.  Here the
    exercise falls in the month the option is actually open, at a rate **[std]** set so
    that a guarantee-date year still sheds about the same proportion of lives as the
    annual grid's spike did.  Neither number is measured: no public UK with-profits
    experience was retrieved, and the whole construction is rationalized from the
    incentive structure.
    """
    if is_guarantee_date(t) and guar_benefit_pp(t) > asset_share(t):
        return guarantee_exercise_rate                               # noqa: F821
    return 0.0


def guarantee_imminent(t):
    """0.8 in the twelve months before a guarantee date **[std]**: policyholders wait.

    The run-up, not the calendar year: any month from which the next guarantee date is
    between one and twelve months away, on the policy clock, ``0 < 12g - 1 -
    duration_mth(t) <= 12`` for a guarantee year ``g``, whose date ends policy month
    ``12g - 1``; :mod:`~.WP_UK_S` measures from ``t``, which on the valuation clock would
    put the window in the wrong months of a policy in force.  On the annual grid this was
    the single period before a guarantee-date period, which is the same window counted in
    years.

    One year meets the test in any month, the window being twelve months long:
    ``g = (duration_mth(t) + 13) // 12``, floor division, the policy year of the month
    itself in its first eleven months and the year after in its twelfth, whose own date
    falls at its end, a month the window does not hold.  So the cell asks
    :func:`is_guarantee_year` of that year alone, where :mod:`~.WP_UK_S` asks ``any()``
    over a generator of its tuple of years, which compiles to no C: the same answer, in
    every month, before issue and past cover among them.  A year below 1 is no guarantee
    date, and is not asked.
    """
    g = (duration_mth(t) + 13) // 12
    if g >= 1 and is_guarantee_year(g):
        return guarantee_imminent_factor                             # noqa: F821
    return 1.0


def surr_rate(t):
    """w(t): the **annual** ordinary surrender rate applying in month t.

    The table rate times the two diffuse behavioural multipliers - the MVR deterrent and
    the guarantee-imminent suppression - capped at 1, :mod:`~.WP_UK_S`'s bound first,
    ``min(1.0, ...)``, whose order a surrender rate keeps (USLIB-SEC-PLAN.md §5.1, step
    6).  The guarantee-date exercise is *not* in here: it is a dated one-off rather than a
    rate per year, and it enters through :func:`surr_rate_mth`.  0 outside cover, where
    no policy year is read.
    """
    if not is_active(t):
        return 0.0
    return min(1.0, surr_rate_base(t) * mvr_deterrent(t)
               * guarantee_imminent(t))


def surr_rate_mth(t):
    """w_m(t): the monthly surrender rate, exercise included.

    ``1 - (1 - w_ord_m)(1 - exercise)`` where ``w_ord_m = 1 - (1 - w(t))^(1/12)``: the
    ordinary monthly rate, and then in a guarantee-date month the MVR-free encashment
    taken by whoever is left after it.  Twelve ordinary months compound back to the
    annual table rate exactly; the exercise is over and above that, and falls in one
    month a decade.
    """
    ordinary = 1.0 - (1.0 - surr_rate(t)) ** (1.0 / 12.0)
    return min(1.0, 1.0 - (1.0 - ordinary) * (1.0 - guarantee_exercise(t)))


def pols_if(t):
    """l(t): the number of policies in force at the **start** of month t, the row's weight.

    ``pols_if_at(t, BEF_DECR)``: the count carried in from month t - 1, plus month t's
    new business, before month t's decrements.  On a point issued at ``t = 0`` that is
    exactly :mod:`~.WP_UK_S`'s ``pols_if``, the notes' ``l(t)``.  It is
    ``basiclife.BasicTerm_SE``'s ``BEF_DECR`` count, not its ``pols_if``.  Zero outside the
    frame: before issue, and from ``t = proj_len()`` on.
    """
    return pols_if_at(t, BEF_DECR)


def pols_if_at(t, timing):
    """The number of policies in force at a point inside month t.

    ``BEF_NB``
        The count carried in from month t - 1, before month t's new
        business: the survivors of month t - 1's deaths and surrenders,
        out of month t - 1's ``BEF_DECR`` count.  At :func:`t_entry`,
        the first month on the books, it is :func:`pols_if_init`, the
        count in force at the valuation date (0 for a point issued at or
        after it), and the recursion reads no earlier month.  Zero outside
        the frame, so the survivors of its last month leave as
        :func:`pols_maturity`.

    ``BEF_DECR``
        ``BEF_NB`` plus :func:`pols_new_biz`: l(t), the count that
        weights month t, which :func:`pols_if` returns.

    ``BEF_SURR``
        after deaths, before surrenders - the processing order is death
        before surrender **[std]**.

    ``AFT_DECR``
        the end-of-month count, ``BEF_NB`` at t + 1 exactly, one product
        in one order, and zero in the last projected month
        ``proj_len() - 1``, where the endowment matures and the bond
        projection is truncated or encashed.

    ``BEF_NB`` is the one timing running in force adds, as ``basiclife.BasicTerm_SE``
    names it; the other three are :mod:`~.WP_UK_S`'s, and any other raises.  ``BEF_NB``
    forms month t - 1's ``BEF_DECR`` count itself, as ``BEF_NB`` plus
    :func:`pols_new_biz` at t - 1, the same sum in the same order, and its deaths and
    surrenders inline, rather than calling for it, so the chain of calls from month t back
    to :func:`t_entry` is one cell a month, where :mod:`~.WP_UK_S`'s ``pols_if`` runs
    through ``AFT_DECR`` and ``BEF_SURR``, three: a compiled model runs that chain on
    the C stack.
    """
    if timing == BEF_NB:
        if not is_active(t) or t >= proj_len():
            return 0.0
        if t == t_entry():
            return pols_if_init()
        if duration_mth(t) % 12 == 0:
            return pols_if_py(policy_year(t))
        return ((pols_if_at(t - 1, BEF_NB) + pols_new_biz(t - 1))       # noqa: F821
                * (1.0 - mort_rate_mth(t - 1)) * (1.0 - surr_rate_mth(t - 1)))
    if timing == BEF_DECR:
        return pols_if_at(t, BEF_NB) + pols_new_biz(t)
    if timing == BEF_SURR:
        if not is_active(t):
            return 0.0
        return pols_if(t) * (1.0 - mort_rate_mth(t))
    if timing == AFT_DECR:
        if not is_active(t) or t >= proj_len() - 1:
            return 0.0
        return pols_if_at(t + 1, BEF_NB)
    raise ValueError("invalid timing")


def pols_if_py(y):
    """The count carried into policy year y: the survivors of policy year y - 1.

    The count's recursion blocked by policy year (UKLIB-SEC-PLAN.md K12), as
    ``ULB_UK_SEC``'s and ``WOL_UK_SEC``'s counts are (*Record -- M10*, *Record -- M6*): it
    walks the months of policy year ``y - 1`` on the books in ascending order, from the
    later of :func:`t_entry` and the year's first month, asking the count carried into each,
    ``pols_if_at(s, BEF_NB)``, so that each finds the month before cached, and returns the
    count carried out of the year's last month, ``BEF_NB`` plus :func:`pols_new_biz` there,
    less its deaths and surrenders: the product ``pols_if_at(t, BEF_NB)`` forms at the next
    month, in the same order, bit for bit.  ``pols_if_at(t, BEF_NB)`` reads it in the first
    month of policy year ``y``, in cover, in the frame and after :func:`t_entry`, so ``y``
    runs from 2 to the policy year of the longest cover's last month, 103 at the contract's
    longest, issue at ``issue_age_min``, 18, to ``omega_age_max``, 121 (``spec_sec.py``); no
    other cell reads it.
    """
    d = duration_mth_init()
    first = max(t_entry(), 12 * (y - 2) - d)
    last = 12 * (y - 1) - 1 - d
    for s in range(first, last):
        pols_if_at(s, BEF_NB)                                        # noqa: F821
    return ((pols_if_at(last, BEF_NB) + pols_new_biz(last))           # noqa: F821
            * (1.0 - mort_rate_mth(last)) * (1.0 - surr_rate_mth(last)))


def pols_new_biz(t):
    """The number of policies issued in month t: ``policy_count()`` in the issue month.

    The issue month is the one with ``duration_mth(t) == 0``: ``t = 0`` for a point
    issued at the valuation date, ``t = k`` for one issued ``k`` months later.  A point
    already in force at the valuation date has none.
    """
    return policy_count() if duration_mth(t) == 0 else 0.0


def pols_death(t):
    """Deaths in month t, against the in force at its start.

    Zero outside cover, before any rate is read.
    """
    if not is_active(t):
        return 0.0
    return pols_if(t) * mort_rate_mth(t)


def pols_surr(t):
    """Surrenders at the end of month t, from the survivors of mortality.

    Carries the guarantee-date encashment as well as the ordinary rate, so the exits of
    a guarantee-date month are visibly larger than its neighbours' - which is the point
    of dating the exercise rather than spreading it.  Zero outside cover, before any rate
    is read.
    """
    if not is_active(t):
        return 0.0
    return pols_if_at(t, BEF_SURR) * surr_rate_mth(t)


def pols_maturity(t):
    """Survivors at the end of the projection: maturities, or the bond's truncation.

    On the endowment chassis these are genuine maturities and are paid.  On the bond
    chassis they are paid where the projection ends in a forced encashment and pay
    nothing where it ends at the limiting age - see :func:`is_forced_encashment`.
    Non-zero in the frame's last month alone, ``t = proj_len() - 1``.
    """
    if t != proj_len() - 1:
        return 0.0
    return pols_if(t) - pols_death(t) - pols_surr(t)


def inflation_factor(t):
    """The expense inflation factor in month t: ``(1 + pi)^(t // 12)`` **[std]**.

    On the **valuation** clock: 1 through the first year from the valuation date, and
    stepping on each anniversary of it, for every point alike, so that the maintenance
    expense is in valuation-date pounds (USLIB-SEC-PLAN.md D7).  :mod:`~.WP_UK_S` inflates
    from issue, ``(1 + pi)^duration(t)``, which on a policy in force would inflate today's
    expense by the years the policy has already run; on a point issued at ``t = 0`` the two
    are the same.  The expense assumption is quoted per year and inflates per year.  A
    factor past the largest float, which only an ``inflation_rate`` past every rate of
    inflation makes, is refused in the month it first is, naming the point and the
    Reference: Python's power raises ``OverflowError`` there, naming neither, and C's gives
    an infinity (``PA_UK_SEC``'s form, *Record — M11*).
    """
    base = 1.0 + inflation_rate                                      # noqa: F821
    n = t // 12
    try:
        factor = base ** n
        if factor - factor != 0.0 and base - base == 0.0:
            raise float.__pow__(base, n)
    except OverflowError:
        raise ValueError(
            f"point_id {point_id()}: the inflation factor inflation_factor({t}) is past the "  # noqa: F821
            f"largest float, under inflation_rate {float(inflation_rate)}") from None  # noqa: F821
    if not factor <= 1.7976931348623157e308:
        raise ValueError(
            f"point_id {point_id()}: the inflation factor inflation_factor({t}) is past the "  # noqa: F821
            f"largest float, under inflation_rate {float(inflation_rate)}")  # noqa: F821
    return factor


def premiums(t):
    """Premium income at the start of month t, an inflow.

    A total past the largest float is refused in the month it first is, naming the
    premium and the count.
    """
    v = premium_pp(t) * pols_if(t)
    if not v - v == 0.0:
        raise ValueError(
            f"point_id {point_id()}: the premiums premiums({t}) are {v}, not a finite number, "  # noqa: F821
            f"from premium_pp({t}) {premium_pp(t)} on pols_if({t}) {pols_if(t)} policies")
    return v


def withdrawals(t):
    """Partial withdrawals paid at the start of month t.

    An owner election rather than a claim, which is why it has its own name and column.
    A total past the largest float is refused in the month it first is.
    """
    v = wd_pp(t) * pols_if(t)
    if not v - v == 0.0:
        raise ValueError(
            f"point_id {point_id()}: the withdrawals withdrawals({t}) are {v}, not a finite "  # noqa: F821
            f"number, from wd_pp({t}) {wd_pp(t)} on pols_if({t}) {pols_if(t)} policies")
    return v


def claims(t, kind):
    """Benefit outgo in month t, by kind; the total when kind is omitted.

    ``DEATH``, ``SURRENDER`` and ``MATURITY`` weight :func:`claim_pp` by the
    corresponding decrement.  ``GUARANTEE`` is not a separate outgo: a guarantee-date
    exit *is* a surrender, paid MVR-free, so it is already inside the surrender line.  A
    claim of a kind, or the total, past the largest float is refused in the month it
    first is, naming what makes it.
    """
    if kind == ALL:                                                  # noqa: F821
        f = 0.0 + claims(t, DEATH)                                   # noqa: F821
        c = 0.0
        x = claims(t, SURRENDER)                                     # noqa: F821
        s = f + x
        if abs(f) >= abs(x):
            c = c + ((f - s) + x)
        else:
            c = c + ((x - s) + f)
        f = s
        x = claims(t, MATURITY)                                      # noqa: F821
        s = f + x
        if abs(f) >= abs(x):
            c = c + ((f - s) + x)
        else:
            c = c + ((x - s) + f)
        f = s
        if c != 0.0 and abs(c) <= 1.7976931348623157e308:
            f = f + c
        if not f - f == 0.0:
            raise ValueError(
                f"point_id {point_id()}: the claims claims({t}, ALL) are {f}, not a finite "
                f"number, from the death, surrender and maturity claims "
                f"{claims(t, DEATH)}, {claims(t, SURRENDER)} and "     # noqa: F821
                f"{claims(t, MATURITY)}")                            # noqa: F821
        return f
    if kind == DEATH:
        n = pols_death(t)
    elif kind == SURRENDER:
        n = pols_surr(t)
    elif kind == MATURITY:
        n = pols_maturity(t)
    else:
        raise ValueError("invalid kind")
    v = claim_pp(t, kind) * n
    if not v - v == 0.0:
        raise ValueError(
            f"point_id {point_id()}: the claims claims({t}, {kind}) are {v}, not a finite "  # noqa: F821
            f"number, from claim_pp({t}, {kind}) {claim_pp(t, kind)} on {n} policies")
    return v


def expenses(t):
    """E(t): the maintenance expense in month t **[std]**.

    £30 a policy a year - a twelfth of it each month - inflating at 3% on each
    anniversary of the valuation date.  Where a fund's actual expenses exceed the capped
    charge taken from asset shares, the excess falls to the estate - a fund-level flow a
    single-policy model cannot see.  An expense past the largest float, which only an
    ``expense_maint`` and an inflation factor near it make, is refused in the month it
    first is, naming the References.
    """
    v = expense_maint / 12.0 * inflation_factor(t) * pols_if(t)      # noqa: F821
    if not v - v == 0.0:
        raise ValueError(
            f"point_id {point_id()}: the expenses expenses({t}) are {v}, not a finite number, "  # noqa: F821
            f"from expense_maint {float(expense_maint)} and inflation_rate "  # noqa: F821
            f"{float(inflation_rate)}, on pols_if({t}) {pols_if(t)} policies")  # noqa: F821
    return v


def shareholder_transfers(t):
    """The 90:10 shareholder transfer paid out of the fund in month t.

    The transfer on the month's declared bonus - nil except in a declaration month -
    weighted by the in force, plus a ninth of the final bonus actually paid on the
    month's claims, which arises whenever a claim does.  The same 90:10 split applied at
    the point the non-guaranteed part is handed over.  A total past the largest float is
    refused in the month it first is.
    """
    on_declaration = shareholder_transfer_pp(t) * pols_if(t)
    exits = pols_death(t) + pols_surr(t) + pols_maturity(t)
    on_final_bonus = (final_bonus_pp(t) * exits
                      / shareholder_transfer_divisor)                # noqa: F821
    v = on_declaration + on_final_bonus
    if not v - v == 0.0:
        raise ValueError(
            f"point_id {point_id()}: the shareholder transfers shareholder_transfers({t}) are "  # noqa: F821
            f"{v}, not a finite number, from the transfer on the declaration "
            f"{on_declaration} and on the final bonus {on_final_bonus}")
    return v


def smoothing_cost(t):
    """The estate's smoothing and guarantee cost on the month's exits.

    Each exiting policy is paid its smoothed payout while the asset share it earned is
    released; the difference falls on the estate.  Positive in a month when guarantees
    or smoothing pay more than the policies earned - which on a guarantee-date month is
    both the largest exit and the deepest shortfall at once.  A total past the largest
    float is refused in the month it first is.
    """
    v = (smoothing_cost_pp(t, DEATH) * pols_death(t)
         + smoothing_cost_pp(t, SURRENDER) * pols_surr(t)
         + smoothing_cost_pp(t, MATURITY) * pols_maturity(t))
    if not v - v == 0.0:
        raise ValueError(
            f"point_id {point_id()}: the smoothing cost smoothing_cost({t}) is {v}, not a "  # noqa: F821
            f"finite number, from the costs per policy on the month's deaths, surrenders "
            f"and maturities, {smoothing_cost_pp(t, DEATH)}, "
            f"{smoothing_cost_pp(t, SURRENDER)} and {smoothing_cost_pp(t, MATURITY)}")
    return v


def smoothing_account(t):
    """SM(t): the cumulative smoothing and guarantee cost borne by the estate.

    Intended broadly neutral over time.  The base model tracks the balance without
    recycling it into credited returns; one insurer operates that recycling, feeding it
    back subject to a maximum annual deduction from asset shares [S5].

    Since issue: at :func:`t_entry` the cost of the exits before the valuation date,
    :func:`smoothing_account_init` per policy times :func:`pols_if_init`, the policies in
    force at it, and each month's cost added after, one cell a month.  :mod:`~.WP_UK_S`
    opens at nil where its frame opens.  A sum over the exits of the count, it is 0
    outside the frame, as the count is: before issue, and from ``t = proj_len()`` on.  It
    asks for the frame before it reads the month before, so that a cold call meets the
    frame's search for the units' exhaustion at its own month, not at the foot of the
    account's chain, where the search's reads of the asset share for the bonus rule would
    run beneath every month of it.  An account that leaves the floats is refused in the
    month it first does, by :func:`smoothing_account_refusal`.

    In the first month of a policy year after :func:`t_entry` the account carried in is the
    year's opening, :func:`smoothing_account_py`, which is ``smoothing_account(t - 1)``, bit
    for bit: the chain blocked by policy year (UKLIB-SEC-PLAN.md K12), so that a cold read
    runs one cell a month within its year and two cells a year before it.
    """
    if not is_active(t) or t >= proj_len():
        return 0.0
    if t == t_entry():
        prev = smoothing_account_init() * pols_if_init()
    elif duration_mth(t) % 12 == 0:
        prev = smoothing_account_py(policy_year(t))
    else:
        prev = smoothing_account(t - 1)
    v = prev + smoothing_cost(t)
    if not v - v == 0.0:
        return smoothing_account_refusal(t)
    return v


def smoothing_account_py(y):
    """SM entering policy year y: the smoothing account policy year y - 1 closes on.

    The recursion blocked by policy year (UKLIB-SEC-PLAN.md K12), as ``ULB_UK_SEC``'s fund
    and ``WOL_UK_SEC``'s counts are (*Record -- M10*, *Record -- M6*): it walks the months
    of policy year ``y - 1`` on the books in ascending order, from the later of
    :func:`t_entry` and the year's first month, asking :func:`smoothing_account` of each, so
    that each finds the month before cached and none runs a chain, and returns the year's
    last month's, :func:`smoothing_account`'s own value, bit for bit.  So a cold read runs
    one cell a month back to its year's first month and two cells a year before it, where
    one cell a month back to :func:`t_entry` would run the contract's longest cover, 1,236
    months, on the compiled model's C stack.  :func:`smoothing_account` and its refusal,
    :func:`smoothing_account_refusal` read it in the first month of policy year ``y``, in
    cover and after :func:`t_entry`, so ``y`` runs from 2 to the policy year of the longest
    cover's last month, 103 at the contract's longest, issue at ``issue_age_min``, 18, to
    ``omega_age_max``, 121 (``spec_sec.py``); no other cell reads it.
    """
    d = duration_mth_init()
    first = max(t_entry(), 12 * (y - 2) - d)
    last = 12 * (y - 1) - 1 - d
    for s in range(first, last):
        smoothing_account(s)
    return smoothing_account(last)


def smoothing_account_refusal(t):
    """The refusal of a smoothing account past the floats in month t, in a cell of its
    own.

    :func:`smoothing_account`'s, on its error path alone (``ULB_UK_SEC``'s form, *Record
    — M10*): it takes the month alone, recomputes the account from the same cells, the
    same float, and refuses it where it is not a finite number, naming the month, the
    account carried in and the month's cost; where finite it returns it, and outside the
    frame 0, as :func:`smoothing_account` does.
    """
    if not is_active(t) or t >= proj_len():
        return 0.0
    if t == t_entry():
        prev = smoothing_account_init() * pols_if_init()
    elif duration_mth(t) % 12 == 0:
        prev = smoothing_account_py(policy_year(t))
    else:
        prev = smoothing_account(t - 1)
    v = prev + smoothing_cost(t)
    if not v - v == 0.0:
        raise ValueError(
            f"point_id {point_id()}: the smoothing account smoothing_account({t}) is {v}, "  # noqa: F821
            f"not a finite number, from the account carried in, {prev}, and the month's "
            f"cost, {smoothing_cost(t)}")
    return v


def net_cf(t):
    """The net cash flow of month t, **income positive**.

    Premiums less claims, withdrawals, expenses and shareholder transfers.  The asset
    share appears nowhere in it: it is a state variable, not a cash flow, and the
    payouts it drives are already in ``claims``.  A net flow that leaves the floats, a
    flow past them among its terms, raises ``ValueError`` here, naming the point and the
    flows.
    """
    v = (premiums(t) - claims(t, ALL) - withdrawals(t)                # noqa: F821
         - expenses(t) - shareholder_transfers(t))
    if not v - v == 0.0:
        raise ValueError(
            f"point_id {point_id()}: the net cash flow net_cf({t}) is {v}, not a finite "  # noqa: F821
            f"number, from premiums {premiums(t)}, claims {claims(t, ALL)}, withdrawals "
            f"{withdrawals(t)}, expenses {expenses(t)} and shareholder transfers "
            f"{shareholder_transfers(t)}")
    return v


def check_pols_roll_fwd_resid(t):
    """The in-force roll-forward residual in month t; zero everywhere.

    ``pols_if(t) - pols_if(t+1)``, plus the new business of month t + 1, which is no part
    of month t's movement, less the month's deaths, surrenders and maturities.
    """
    return (pols_if(t) - pols_if(t + 1) + pols_new_biz(t + 1)
            - pols_death(t) - pols_surr(t) - pols_maturity(t))


def check_pols_roll_fwd():
    """True when the in-force roll-forward closes in every month of the frame.

    The tolerance scales with the policies the point stands for, ``policy_count()``, in
    force at the valuation date or issued after it, since the residual accumulates
    rounding on that many policies.
    """
    end = proj_len()
    tol = 1e-10 * max(policy_count(), 1.0)
    for t in range(end):
        if not abs(check_pols_roll_fwd_resid(t)) <= tol:
            return False
    return True


def check_asset_share_roll_fwd_resid(t):
    """The asset share recursion residual in month t; zero everywhere.

    ``AS(t) - max(0, {[AS(t-1) + P - W_AS](1 + r_m)(1 - c_amc_m - c_g_m) - ST - MC
    + M})``, rebuilt in one expression rather than through :func:`asset_share_at`, so
    that a mis-ordered step - a shareholder transfer taken before the charges, say, or a
    mortality charge measured on the wrong balance - shows up here.  Every rate in it is
    the monthly equivalent, which is the other thing the check pins down: a stray annual
    rate left in the recursion would fail here rather than quietly overcharging the
    asset share twelvefold.  The outer ``max(0, ...)`` is the zero floor
    :func:`asset_share` applies; the check still validates the ordering in every month
    the floor is not binding, which is every month of every cell shipped here except the
    tail of the sustained down scenario.
    """
    built = ((asset_share_at(t, BEF_PREM) + premium_pp(t) - wd_as_pp(t))
             * (1.0 + fund_return_mth())
             * (1.0 - amc_rate_mth() - guar_charge_rate_mth(t))
             - shareholder_transfer_pp(t) - mort_charge_pp(t)
             + misc_surplus_pp(t))
    return asset_share(t) - max(0.0, built)


def check_asset_share_roll_fwd():
    """True when the asset share recursion closes in every month of the frame."""
    end = proj_len()
    for t in range(end):
        if not abs(check_asset_share_roll_fwd_resid(t)) <= 1e-8:
            return False
    return True


def check_fb_mvr_exclusive():
    """True when no month carries both a final bonus and a market value reduction.

    ``FB > 0`` requires ``S > GB`` and ``MVR > 0`` requires ``S < GB``, so the two
    cannot both be positive.  An implementation that computed them independently could
    produce both, and would then pay a final bonus and deduct a reduction on the same
    exit.
    """
    end = proj_len()
    for t in range(end):
        if not min(final_bonus_pp(t), mvr_pp(t)) <= 1e-9:
            return False
    return True


def check_mvr_bound():
    """True when the market value reduction stays inside its contractual bound.

    It may not exceed the excess of the unit value over the underlying asset value,
    ``max(0, GB - AS)``.  The bound is a conduct rule, not a modelling nicety.
    """
    end = proj_len()
    for t in range(end):
        if not mvr_pp(t) <= max(0.0, guar_benefit_pp(t) - asset_share(t)) + 1e-9:
            return False
    return True


def check_fund_nonneg():
    """True when the unit holding and the asset share stay non-negative throughout.

    This is the way a with-profits projection goes wrong quietly.  A level withdrawal
    election runs the unit fund down; uncapped, the unit holding turns negative and the
    guaranteed benefit turns negative with it, and every downstream number - the bonus
    cost, the mortality charge's sum at risk, the smoothed payout - stays plausible
    enough to read past.  :func:`wd_pp` caps the withdrawal at the fund and
    :func:`proj_len` stops at exhaustion; this asserts that they worked.
    """
    end = proj_len()
    for t in range(end):
        if not (units(t) >= -1e-9 and asset_share(t) >= -1e-9):
            return False
    return True


def check_payout_corridor():
    """True when the smoothed payout stays inside the 80-120% target corridor.

    Deterministic at model-point level; the regulatory test is a portfolio property that
    a single-policy model cannot express.
    """
    for t in range(proj_len()):
        as_t = asset_share(t)
        if as_t <= 0.0:
            continue
        ratio = smoothed_payout(t) / as_t
        if ratio < corridor_lo - 1e-9 or ratio > corridor_hi + 1e-9:  # noqa: F821
            return False
    return True


def check_declaration_is_annual():
    """True when the declared bonus moves the guarantee only in declaration months.

    The grid is monthly and the discretion cycle is not: a declaration hardens the
    guarantee once a policy year, at its anniversary, and nothing declares in the other
    eleven months.  The failure this guards against is compounding the *annual* bonus
    rate twelve times a year, which produces a model that still runs, whose roll-forwards
    still close, and whose guarantee is an order of magnitude too large a decade later.

    What is asserted is the quantity a declaration actually moves.  On the bond chassis
    that is the **unit price**, not the face value: a withdrawal cancels units every
    month, so the face value falls between declarations for a reason that has nothing to
    do with discretion.  On the endowment chassis, which holds no units, it is the
    guaranteed benefit itself.  Either way the cost of bonus and the shareholder transfer
    it feeds must be nil outside a declaration month.  The months checked are those of
    the frame on the books, from :func:`t_entry`: before a policy is issued it holds no
    price and no guarantee to move.

    Tolerances are relative to the quantity, since these are money amounts and a price
    rather than probabilities.
    """
    for t in range(t_entry(), proj_len()):
        if is_declaration_month(t):
            continue
        if is_unitised():
            opening = unit_price(t - 1) if t > t_entry() else unit_price_init()
            moved = unit_price(t)
        else:
            opening = guar_benefit_open(t)
            moved = guar_benefit_pp(t)
        if abs(moved - opening) > 1e-9 * max(abs(opening), 1.0):
            return False
        if cost_of_bonus_pp(t) != 0.0 or shareholder_transfer_pp(t) != 0.0:
            return False
    return True


def result_cf():
    """Result table of cashflows, one row per month ``t = 0 .. proj_len() - 1``.

    Row 0 is the valuation month for every model point, so the frames of a block line up
    and sum row by row.  A point issued after the valuation date has zeros until its issue
    month.  The columns are :mod:`~.WP_UK_S`'s.

    ``pols_if`` is the start-of-month count that weights every flow on the row.  The
    asset share is published beside them as ``asset_share`` because it is what the
    payouts are measured against - but it is a state variable, not a cash flow, and it
    is not part of ``net_cf``.
    """
    ts = list(range(proj_len()))
    return pd.DataFrame(                                             # noqa: F821
        {
            "pols_if": [pols_if(t) for t in ts],
            "asset_share": [asset_share(t) for t in ts],
            "premiums": [premiums(t) for t in ts],
            "claims_death": [claims(t, DEATH) for t in ts],
            "claims_surrender": [claims(t, SURRENDER) for t in ts],
            "claims_maturity": [claims(t, MATURITY) for t in ts],
            "withdrawals": [withdrawals(t) for t in ts],
            "expenses": [expenses(t) for t in ts],
            "shareholder_transfers": [shareholder_transfers(t) for t in ts],
            "smoothing_cost": [smoothing_cost(t) for t in ts],
            "net_cf": [net_cf(t) for t in ts],
        },
        index=pd.Index(ts, name="t"),                                # noqa: F821
    )


def result_payout():
    """Result table of the payout machinery, one row per month ``t = 0 .. proj_len() - 1``.

    The asset share against the guaranteed benefit and the smoothed payout, and the
    final bonus and market value reduction the gap between them produces.  Every column
    is an end-of-month value, on the same frame as :func:`result_cf`.  ``bonus_rate`` is
    the **annual** rate declared for the policy year the month falls in, so it repeats
    across twelve rows and steps once a year; ``cost_of_bonus_pp`` and
    ``shareholder_transfer_pp`` beside it are nil in eleven of those twelve.  A point
    issued after the valuation date has zeros until its issue month.
    """
    ts = list(range(proj_len()))
    return pd.DataFrame(                                             # noqa: F821
        {
            "asset_share": [asset_share(t) for t in ts],
            "guar_benefit_pp": [guar_benefit_pp(t) for t in ts],
            "smoothed_payout": [smoothed_payout(t) for t in ts],
            "final_bonus_pp": [final_bonus_pp(t) for t in ts],
            "mvr_pp": [mvr_pp(t) for t in ts],
            "mvr_applied_pp": [mvr_applied_pp(t) for t in ts],
            "claim_death": [claim_pp(t, DEATH) for t in ts],
            "claim_surrender": [claim_pp(t, SURRENDER) for t in ts],
            "claim_guarantee": [claim_pp(t, GUARANTEE) for t in ts],
            "bonus_rate": [bonus_rate(t) for t in ts],
            "cost_of_bonus_pp": [cost_of_bonus_pp(t) for t in ts],
            "shareholder_transfer_pp": [shareholder_transfer_pp(t) for t in ts],
            "mort_charge_pp": [mort_charge_pp(t) for t in ts],
            "smoothing_account": [smoothing_account(t) for t in ts],
        },
        index=pd.Index(ts, name="t"),                                # noqa: F821
    )


def result_pols():
    """Result table of policy counts, one row per month ``t = 0 .. proj_len() - 1``.

    The same rows as :func:`result_cf`: the counts it weights its rows by, and how they
    move, as ``basiclife.BasicTerm_SE``'s ``result_pols`` sets them out.  ``pols_if``, the
    count of month t, and ``pols_new_biz``, the part of it issued in month t; then month
    t's decrements in processing order, deaths and surrenders, the guarantee-date
    encashment among them, and the survivors of the frame's last month, matured, encashed
    or truncated.  Row by row, ``pols_if`` at ``t + 1`` is ``pols_if`` less its deaths,
    surrenders and maturities of month t, plus the new business of month ``t + 1``.
    """
    ts = list(range(proj_len()))
    return pd.DataFrame(                                             # noqa: F821
        {
            "pols_if": [pols_if(t) for t in ts],
            "pols_new_biz": [pols_new_biz(t) for t in ts],
            "pols_death": [pols_death(t) for t in ts],
            "pols_surr": [pols_surr(t) for t in ts],
            "pols_maturity": [pols_maturity(t) for t in ts],
        },
        index=pd.Index(ts, name="t"),                                # noqa: F821
    )


# ---------------------------------------------------------------------------
# References

data = ("Interface", ("..", "Data"), "auto")

idx = 0

BEF_NB = 0

BEF_DECR = 1

BEF_SURR = 2

AFT_DECR = 3

BEF_PREM = 4

BEF_RETURN = 5

AFT_RETURN = 6

AFT_CHARGE = 7

AFT_ST = 8

AFT_MC = 9

DEATH = 0

SURRENDER = 1

GUARANTEE = 2

MATURITY = 3

ALL = 4

UWP_BOND = 0

CWP_ENDOWMENT = 1

issue_age_min = 18

omega_age = 120

omega_age_max = 121

mort_be_factor = 0.6

amc_rate = 0.01

guar_charge_rate_base = 0.001

guar_charge_cap = 0.02

misc_surplus_rate = 0.0

prem_alloc_rate = 1.0

death_benefit_factor = 1.01

shareholder_transfer_divisor = 9.0

surr_disc_rate = 0.04

smooth_cap = 0.1

corridor_lo = 0.8

corridor_hi = 1.2

bonus_rule_on = False

guar_fill_target = 0.8

bonus_speed = 0.5

bonus_change_cap = 0.01

bonus_horizon = 10

mvr_deterrent_factor = 0.6

guarantee_exercise_rate = 0.075

guarantee_imminent_factor = 0.8

expense_maint = 30.0

inflation_rate = 0.03

pd = ("Module", "pandas")
