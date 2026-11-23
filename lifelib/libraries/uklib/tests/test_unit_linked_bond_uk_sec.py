"""In-force tests for ULB_UK_SEC: the splice, future business, counts, regeneration.

``ULB_UK_SEC`` is ``ULB_UK_S`` taught to run in force at a valuation date
(UKLIB-SEC-PLAN.md, milestone M9, after USLIB-SEC-PLAN.md's Phase 1).  It runs on two
clocks: ``t`` counts months from the valuation date, the same month for every model point,
and ``duration_mth(t)`` counts the months the bond has been in force,
``duration_mth_init() + t``.  A model point may be a bond already in force at the valuation
date, in any month of its policy year, one issued at it, or one to be issued after it, as
in ``basiclife/BasicTerm_SE``.  A bond in force opens with two columns of state beside its
count, each per policy and measured at the valuation instant: the unit fund,
``av_pp_init``, and the withdrawals and adviser charges since issue, ``wd_cum_pp_init``,
which open the guaranteed minimum death benefit.  Its frame ends at the limiting age or at
the first month its fund opens at or below ``depletion_threshold``, half a pence, where
``ULB_UK_S``'s ends at the first that opens on exactly 0 or less: a recorded departure,
whose effect on each S point ``test_the_depletion_threshold_moves_point_3_alone`` states.

The worked example is not restated here.  On a point issued at the valuation date the two
clocks coincide and the model is ``ULB_UK_S``, and ``test_model_conventions_uk.py``
asserts that cell by cell on the twins of S's six new-business points (T1), so every
golden of ``test_unit_linked_bond_uk.py`` on them holds on this model with no number
copied; on S's point 3, whose fund S closes on a rounding of 3.4e-15 and projects a month
more, over the months both frames run alike.  The conventions also hold the SEC family's
other rules: every frame opens at ``t = 0``, ``pols_if`` is the ``BEF_DECR`` count,
``BEF_DECR`` is ``BEF_NB`` plus the month's new business, new business enters once, and
nothing happens before issue.  This module holds the rest of the plan's tests (its §5)
and the product's own facts:

* T2, the splice: an S point restated in force at month ``d``, opened with the state S
  carries into ``d``, continues S's projection from ``d`` on, in every cell of S's.  The
  months straddle the product's events: the surrender bands' edges, policy year 21, where
  the allowance-exhaustion step starts, the allowance stops accruing and the GMDB of the
  anchor's pattern has run out, and each frame's last month.  Every switch that ships off
  is on, and three variants of S's points, in a copy of S's table, add the GMDB in the
  money, a custom withdrawal above the 7.5% cap, and the rider beside an adviser charge.
* T3, future new business: a point issued ``k`` months after the valuation date is S's
  projection ``k`` months on, with zeros before issue and no rate evaluated there.
* D11's R1 and R2, and D3's and D5's chains: on the splice's grid no cell is called at a
  negative month, none on the books reads a month before them, and none reads beyond
  ``t + 1`` but the exhaustion search R2 admits; on the committed points no recursion runs
  backward over the frame; the policy clock is a closed form; and each chain, called cold,
  runs one cell a month back to ``t_entry()``, at each shape's longest cover.
* T4, the count algebra: the count rolls forward through new business and decrements,
  multiplying ``policy_count`` by 2.5 with every switch that ships off switched on
  multiplies every flow and every counted cell by 2.5 and moves no per-policy value, and
  the roll-forward, whose tolerance scales with the count, closes on a million policies.
* T5, validation: each malformed row of the table is refused as it is read, naming its
  point; each assumption table, malformed or holding a value that is not a number in its
  range, is refused before a value of it is read, and a read beyond the mortality table is
  refused naming the point; the future horizon is a Reference that bounds future business;
  a point past its cover, one the contract does not issue, one read under a Reference
  outside its domain and one whose fund is exhausted at the valuation date are refused by
  the frame, each bound just inside it, and a surrender rate outside 0 to 1 in the month it
  leaves; the edges of the interface and of each bound are accepted; and so is every state
  ``ULB_UK_S`` reaches, on each set of inputs on which those states differ, but the
  exhausted fund it runs on past the threshold, which is set aside and shown refused.
* T6, regeneration: the committed ``model_point_table_sec.csv`` is what the generator makes
  of ``ULB_UK_S`` and its table as they stand.
* Then the product's own facts: the two clocks on the shipped points; the committed rows
  continuing their S points; each history column read rather than recomputed, the unit
  fund and the withdrawals since issue, which open the GMDB (UKLIB-SEC-PLAN.md K14); the
  depletion threshold, its effect on each S point, and its rules at the Reference's value,
  part of it and just past it; the fund chain written inline; expense inflation on the
  valuation clock; acquisition on new business alone; the cap on mortality and a NaN that
  reaches it; the values outside cover; the block; an in-force extract; the runner; the
  cells' defaulted parameters; the docstrings; the shared input tables; and what the
  default grid reaches.

SEC month ``t`` is S month ``t + source_mth`` throughout, the direction in which
``uk_sec_support`` takes its ``t_offset``: ``d`` for a point restated at S month ``d``,
``-k`` for one issued ``k`` months on.

**The core grid and the full one** (UKLIB-SEC-PLAN.md U6).  T2 and T3 over every S point
at every month, about 130 cases, run by default on a core, chosen so that between them they
reach every branch, every opening-state column, every kind of valuation month and both
sides of every ``min`` and ``max`` the full grid reaches, which
``test_the_core_grid_reaches_every_branch`` asserts.  The other cases, and the rules
test's scan of their rows, carry the ``sec_full`` marker and are skipped, with the reason
shown, unless ``UKLIB_SEC_FULL=1`` is set.  They are never dropped: one leg of the CI
matrix sets it, and ``UKLIB_SEC_FULL=1 python -m pytest -m sec_full
lifelib/libraries/uklib/tests/test_unit_linked_bond_uk_sec.py`` runs them alone.  Each
splice row is released once it has been read (``_release``), as ``run_sec.py --block``
releases its points.

Every test keeps four rules.  Each model is read under a name of its own and closed:
``conftest.unit_linked_bond`` reads S under its default name, and reading a model under a
name in use renames the open one.  No test writes inside the library tree: every changed
input goes through ``uk_sec_support.temp_inputs`` into a temporary directory, because a
CSV added beside the models, even briefly, would fail a concurrent
``test_every_csv_beside_the_model_is_actually_read``.  No test indexes ``Projection`` by
hand: the keys come from ``uk_registry.point_keys`` and the ItemSpaces from
``uk_registry.projection``, and a generated row is found by what it is, its kind, its S
policy and its month (``_row``), so neither a renumbered table nor the C step's positions
can point a test at the wrong row.  And a timing or a kind is passed through ``_code``,
which gives the model's int Reference of its name where the model has one, as at stage
``"EC"`` it will, and the string at stage ``"E"``; every comparison with S passes
``uk_sec_support.codes``, ``{}`` at stage ``"E"``.
"""
import ast
import dataclasses
import inspect
import io
import itertools
import math
import os
import re
import shutil
import subprocess
import sys

import modelx as mx
import numpy as np
import pandas as pd
import pytest

from uk_registry import model_path, point_keys, projection
from uk_sec_support import (
    GENERATED_COLUMNS, SEC_SPECS, TWIN_EXEMPT_DEFAULT, build_sec_table, check_generated,
    codes, frame_mismatches, full_sweep, sweep, temp_inputs, twin_mismatches)

SEC, TWIN = "ULB_UK_SEC", "ULB_UK_S"
TABLE = "model_point_table_sec.csv"
SPEC = SEC_SPECS[SEC]

# S's six new-business points: the anchor cell, a 5% withdrawal (1); the accumulation cell,
# no withdrawals (2); the anchor with a 0.5% adviser charge (3); the anchor with the GMDB
# rider (4); the anchor at a 101% death uplift (5); and a female 55, a larger premium and a
# 3% custom withdrawal (6).
S_POINTS = (1, 2, 3, 4, 5, 6)

# The depletion threshold as shipped (Projection.depletion_threshold), half a pence.
THRESHOLD = 0.005

# T2's months (UKLIB-SEC-PLAN.md §6.6): the second month; 11, 12, 23, 24, 59, 60, 119 and 120,
# either side of the surrender bands' edges, policy years 1 to 2, 2 to 3, 5 to 6 and 10 to
# 11, the first of which is also the first anniversary; 37 and 125, mid-band; 239, 240 and
# 241, either side of policy year 21, where the allowance-exhaustion step starts, the
# allowance stops accruing, the first excess gain of the anchor's pattern appears and the
# GMDB point's guarantee reaches 0; and each frame's last month, 322, 352, 659 and 779.  A
# month at or past a point's frame is left out.  T3's: issued one month on, which puts the
# policy anniversaries a month off the valuation years, and twelve, which puts them back on;
# and later, more than a year after the valuation date (USLIB-SEC-PLAN.md §7.1, *Record —
# M14*, *Splice grid*).
SPLICE_MTHS = (1, 11, 12, 23, 24, 37, 59, 60, 119, 120, 125, 239, 240, 241, 322, 352, 659,
               779)
FUTURE_MTHS = (1, 12)
LATE_FUTURES = ((4, 13), (6, 25))

# Three more S points, in the splice's copy of S's table and never in the committed one,
# each one of S's points changed so as to reach what S's own points cannot:
#
# 7, S point 4, the GMDB point, at an AMC of 4%: its fund falls faster than its guarantee,
#   which is in the money from month 5, so the rider charges and the guarantee pays on
#   death, where S's own GMDB point is in the money only in its issue month, on the death
#   strain;
# 8, S point 6, the custom pattern, at 9% a year: above the 7.5% product cap, which then
#   binds every month the fund can pay;
# 9, S point 3, the adviser charge, with the GMDB rider beside it: both of the charges that
#   leave the fund on a rounding where the withdrawal cap closes it.
#
# Each variant is (the S point it changes, the columns it changes); the policy_id keeps
# the generated ids apart.
VARIANTS = {
    7: (4, {"policy_id": "ULB-900007", "amc_rate": 0.04}),
    8: (6, {"policy_id": "ULB-900008", "wd_rate_custom": 0.09}),
    9: (3, {"policy_id": "ULB-900009", "gmdb_flag": True}),
}
VARIANT_MTHS = {7: (1, 5, 6, 60, 120, 232), 8: (1, 12, 120, 200), 9: (12, 66, 322)}

# Each point's frame from issue, in months, as this model ends it and as ULB_UK_S does.  Its
# fund runs out at 353 on the anchor's pattern, at 323 under the adviser charge, where S
# runs one month more on a rounding of 3.4e-15, at 233 on the GMDB in the money and at 201
# on the custom 9%, and never on the accumulation cell or the custom 3%, whose frames run
# to the limiting age.  test_the_depletion_threshold_moves_point_3_alone holds both.
FRAME = {1: 353, 2: 660, 3: 323, 4: 353, 5: 353, 6: 780, 7: 233, 8: 201, 9: 323}
S_FRAME = {**FRAME, 3: 324, 9: 324}


def _s_table():
    """S's committed table, indexed by point_id."""
    return pd.read_csv(model_path(TWIN).parent / "model_point_table.csv",
                       index_col="point_id")


def _s_table_with_variants():
    """S's committed table with the :data:`VARIANTS` appended, under their own point_ids."""
    table = _s_table()
    rows = []
    for point_id, (base, changes) in VARIANTS.items():
        row = table.loc[[base]].assign(**changes)
        row.index = pd.Index([point_id], name="point_id")
        rows.append(row)
    return pd.concat([table, *rows])


# T2's cases, as (row_kind, S point, source_mth): each S point restated in force at each of
# its months inside its frame, then each variant at its own.  ULB_UK_S has no point in force,
# so no twin is a splice case.  T3's cases, as (S point, k).
SPLICES = (tuple(("derived", p, d) for p in S_POINTS for d in SPLICE_MTHS if d < FRAME[p])
           + tuple(("derived", p, d) for p, mths in VARIANT_MTHS.items() for d in mths))
IN_FORCE_TWINS = ()
FUTURES = (tuple((p, k) for p in S_POINTS for k in FUTURE_MTHS)
           + tuple((p, 1) for p in VARIANTS) + LATE_FUTURES)

# The default run's cases (the module docstring), each with what it is there for.  The
# rest of SPLICES and FUTURES run with UKLIB_SEC_FULL=1.
CORE_SPLICES = {
    ("derived", 1, 1): "the anchor cell in its second month",
    ("derived", 1, 11): "the anchor cell the month before its first anniversary",
    ("derived", 1, 12): "the anchor cell on its first anniversary: the 3% band",
    ("derived", 1, 59): "the last month of the 5% band",
    ("derived", 1, 60): "the first month of the 8% band",
    ("derived", 1, 120): "the first month of the ultimate 10% band",
    ("derived", 1, 239): "the last month of policy year 20",
    ("derived", 1, 240): "policy year 21: the step, the allowance spent",
    ("derived", 1, 241): "policy year 21 under way, an excess gain carried in",
    ("derived", 1, 352): "the last month before the fund is exhausted",
    ("derived", 2, 125): "the accumulation cell mid-band",
    ("derived", 2, 659): "the accumulation cell at the limiting age",
    ("derived", 3, 37): "the adviser charge mid-band, in its fourth year",
    ("derived", 3, 322): "the adviser charge's last month: S runs on past it",
    ("derived", 4, 23): "the GMDB in the month before its second anniversary",
    ("derived", 4, 24): "the GMDB on its second anniversary: the 5% band",
    ("derived", 4, 239): "the GMDB in the last month of its guarantee",
    ("derived", 4, 240): "the GMDB's guarantee run out",
    ("derived", 5, 119): "the 101% uplift in the last month of the 8% band",
    ("derived", 6, 12): "the custom 3%, female, on her first anniversary",
    ("derived", 6, 779): "the custom 3% at the limiting age",
    ("derived", 7, 1): "the GMDB out of the money, its fund falling faster",
    ("derived", 7, 6): "the GMDB in the money: the rider charges",
    ("derived", 7, 232): "the GMDB in the money in its last month",
    ("derived", 8, 1): "the 7.5% cap binding",
    ("derived", 8, 200): "the 7.5% cap's last month, the fund exhausted",
    ("derived", 9, 66): "the rider beside the adviser charge",
    ("derived", 9, 322): "the rider and the adviser charge's last month",
}
CORE_FUTURES = {
    (1, 1): "issued a month off the valuation anniversaries",
    (1, 12): "issued on them, a year on",
    (3, 1): "the adviser charge, whose S frame runs on",
    (4, 13): "the GMDB, more than a year on",
    (6, 25): "the custom 3%, female, more than two years on",
    (7, 1): "the GMDB in the money",
    (8, 1): "the 7.5% cap binding",
}

SEC_FULL = os.environ.get("UKLIB_SEC_FULL") == "1"
FULL_ONLY = (pytest.mark.sec_full,
             pytest.mark.skipif(not SEC_FULL, reason="the full splice grid runs with "
                                "UKLIB_SEC_FULL=1 (UKLIB-SEC-PLAN.md U6)"))

# What the splice sets in both models, S and SEC alike, before either evaluates anything.
# Expense inflation is the one input ULB reads on the valuation clock (D7): S inflates from
# issue and SEC from the valuation date, so at the shipped 2.5% the expenses of a point
# opened at d differ by 1.025^(d // 12), by design, and at 0 both factors are 1.  The clock
# itself is then asserted on its own, at the shipped rate.  The fund return is a flat
# Reference, the same on both clocks, so no input moves with d.  The rest switch on what
# ships off, each of which hides some of the state from any comparison:
#   return_shock, at -0.75, a trailing return 75 points below the fund's, which takes the
#     performance multiplier past its cap of 2, so that the surrender rate is twice the
#     table's;
#   surr_rate_cap, lowered to 0.25, which the ultimate 10% at that multiple and the
#     allowance-exhaustion step's 1.5 then pass from policy year 21, so that the surrender
#     cap binds there and not before.
# The identity does not depend on the values, only on both models having the same ones.
SPLICED_REFS = {"inflation_rate": 0.0, "return_shock": -0.75, "surr_rate_cap": 0.25}

# The splice's switches, for T4, at the shipped inflation.
SWITCHED_ON = {ref: value for ref, value in SPLICED_REFS.items() if ref != "inflation_rate"}

# The cells T2 and T3 skip beyond T1's, which already drop S's av_init_pp, the accessor of
# the column this model renames (the spec's exempt).  proj_len counts from the valuation
# date on SEC and from issue on S, so it differs by d, or by -k, by design; the comparison
# asserts what it must get right, that both frames end at the same instant.
SPLICE_EXEMPT = TWIN_EXEMPT_DEFAULT | SPEC.exempt | {"proj_len"}
FUTURE_EXEMPT = SPLICE_EXEMPT

# The result_cf columns that expense inflation moves, and the cells they are made of: on
# the committed points, at the shipped 2.5%, the only places an in-force row departs from S.
INFLATED = ("expenses", "net_cf")
INFLATION_CELLS = frozenset({"inflation_factor", "expenses", "net_cf", "result_cf"})

# The cells whose exact value is 0 and whose computed value is rounding about it: the three
# residuals, and the excess gain where the withdrawals equal the allowance in exact
# arithmetic, at each policy year's end on the anchor's pattern, where S's value is a
# rounding of 1e-11.  A comparison with S holds them at the harness's absolute floor of
# 1e-9, and every other cell at none (_compare).  result_uf carries the excess gain, and is
# held with them.
RESIDUALS = frozenset({"check_av_roll_fwd_resid", "check_pols_roll_fwd_resid",
                       "check_unit_funding_resid", "excess_gain_pp", "result_uf"})
FLOOR = 1e-9

# The reports, which the comparison reads as frames rather than as cells.
REPORTS = ("result_cf", "result_uf")

# The decrement rates, the allowance step and the policy clock's year and age, none of
# which a report may evaluate before issue (R1, D4): a count asks whether the month is in
# cover before it reads a rate.  allowance_cum_pp is not among them: result_uf reads it at
# every month of the frame, and it guards itself, holding 0 before issue.
DECREMENT_RATES = ("mort_rate", "mort_rate_mth", "surr_rate_base", "surr_rate",
                   "surr_rate_mth", "allow_factor", "age", "duration", "policy_year")

# The cells that scale with policy_count.  Every other cell is a per-policy amount, a rate,
# a ratio, a clock or a flag, and must not move when the count does.
COUNTED = frozenset({
    "policy_count", "pols_if_init", "pols_if", "pols_if_at", "pols_new_biz",
    "pols_death", "pols_surr", "pols_maturity", "claims", "withdrawals", "unit_releases",
    "amc_charges", "gmdb_charges", "further_costs", "tax_provisions", "death_strain",
    "expenses", "net_cf", "check_pols_roll_fwd_resid", "check_unit_funding_resid",
    "result_cf", "result_pols"})

# result_pols' columns, in its order: the count, the new business within it, then the
# month's deaths and surrenders in processing order and the frame's last survivors.
RESULT_POLS = ["pols_if", "pols_new_biz", "pols_death", "pols_surr", "pols_maturity"]
OUTFLOWS = RESULT_POLS[2:]

# result_cf's per-policy column: the unit fund, which no count moves.
PER_POLICY_COLUMNS = ("av_pp",)

# S's three timings and BEF_NB, the one running in force adds; the fund's four; and the
# kinds.
TIMINGS = ("BEF_NB", "BEF_DECR", "BEF_SURR", "AFT_DECR")
FUND_TIMINGS = ("BEF_GROWTH", "AFT_GROWTH", "AFT_CHARGE", "AFT_WD")
KINDS = ("DEATH", "SURRENDER")

# What each cell holds outside cover, before issue and from the limiting age, as its
# docstring says: no count, so no cash flow; no fund, no charge and no withdrawal; no rate
# read at a policy year or an age the bond does not have.  The type is part of the value.
# A count is a float in every branch and a flag a bool, because the C step types a cell by
# the values it returns (USLIB-SEC-PLAN.md F3).  The guard test also calls pols_if_at at
# each timing, av_pp_at at each of the fund's and claims at each kind, all 0.0.
OUTSIDE_COVER = {
    "is_active": False, "av_pp": 0.0, "av_per_segment_pp": 0.0, "fund_growth_pp": 0.0,
    "tax_provision_pp": 0.0, "amc_pp": 0.0, "further_costs_pp": 0.0, "wd_cap_pp": 0.0,
    "wd_pp": 0.0, "adviser_charge_pp": 0.0, "gmdb_guarantee_pp": 0.0,
    "gmdb_charge_pp": 0.0, "death_strain_pp": 0.0, "wd_cum_pp": 0.0,
    "allowance_cum_pp": 0.0, "excess_gain_pp": 0.0, "mort_rate": 0.0,
    "surr_rate_base": 0.0, "allow_factor": 0.0, "surr_rate": 0.0,
    "pols_if": 0.0, "pols_new_biz": 0.0, "pols_death": 0.0, "pols_surr": 0.0,
    "pols_maturity": 0.0, "withdrawals": 0.0, "unit_releases": 0.0, "amc_charges": 0.0,
    "gmdb_charges": 0.0, "further_costs": 0.0, "tax_provisions": 0.0, "death_strain": 0.0,
    "expenses": 0.0, "net_cf": 0.0}

# The counts and the cash flows: what a month after an exhausted fund holds, the frame
# having ended there while the bond is still short of the limiting age, and so in cover.
FRAME_CELLS = ("pols_if", "pols_new_biz", "pols_death", "pols_surr", "pols_maturity",
               "withdrawals", "unit_releases", "amc_charges", "gmdb_charges",
               "further_costs", "tax_provisions", "death_strain", "expenses", "net_cf")

# The cells a month outside cover may not reach: the clocks of the contract and the
# monthly rates, each keyed by a policy year or an attained age.  The reads that guard
# themselves are held by their values in OUTSIDE_COVER instead.
IN_COVER_ONLY = ("age", "duration", "policy_year", "mort_rate_mth", "surr_rate_mth")

# The opening state, in the table's order, and the cells running in force adds to
# ULB_UK_S's, each of which the symbol map must name.
STATE = ("av_pp_init", "wd_cum_pp_init")
NEW_CELLS = ("policy_count", "duration_mth_init", "t_entry", "is_active", "pols_new_biz",
             *STATE, "result_pols")

INFLATION = 0.025       # the shipped inflation_rate, which the inflation test reads

# The recursion limit, as mx.set_recursion takes it, under which the committed points are
# first swept (R2, F7).  A report asks for the frame first, which searches the fund in
# ascending t, and evaluates each column in ascending t, so a forward recursion, through
# t - 1, finds the month before already cached: the committed points' sweep runs 16 cells
# deep at most, and passes under a limit of 16 (measured at M9).  A backward recursion over
# the frame, through t + 1, opens a chain as long as the frame, and the shortest committed
# frame longer than a month is 113.
CALL_DEPTH = 40

# The reads beyond t + 1 the model makes, as (reader, cell read): fund_exhaust_mth's search
# of the unit fund, the loop R2 admits, which every count reads through proj_len() (the
# rules test follows calls keyed by no month), at months up to the frame's end, the first
# month whose fund is exhausted.  The rules test admits no other.
LOOK_AHEAD = frozenset({("fund_exhaust_mth", "av_pp")})


# ---------------------------------------------------------------------------
# Helpers


_names = itertools.count(1)


def _name(tag):
    """A model name that no other read in this session uses."""
    return f"{SEC}_{tag}_{next(_names)}"


def _key(model, point_id):
    """The registry's key for the row labelled ``point_id`` (``uk_registry.point_keys``)."""
    return dict(zip(model.Data.model_point_table().index, point_keys(model)))[point_id]


def _point(model, point_id):
    """The ItemSpace of the row labelled ``point_id``, through the registry's keys."""
    return projection(model, _key(model, point_id))


def _label(table, kind, s_point, month):
    """The ``point_id`` of the one ``kind`` row generated from S point ``s_point``.

    ``month`` is the row's ``source_mth``: 0 for a twin, ``d`` for a derived row, ``-k``
    for a future one.  The twins keep S's ``point_id`` and ``policy_id``, so the S policy
    is the twin's.
    """
    policy = table.at[s_point, "policy_id"]
    hit = table.index[(table["row_kind"] == kind) & (table["source_policy_id"] == policy)
                      & (table["source_mth"] == month)].tolist()
    assert len(hit) == 1, f"{kind} rows of S point {s_point} at month {month}: {hit}"
    return hit[0]


def _row_key(model, kind, s_point, month):
    """The registry's key for that row of ``model``'s table (:func:`_label`)."""
    return _key(model, _label(model.Data.model_point_table(), kind, s_point, month))


def _row(model, kind, s_point, month):
    """The ItemSpace of that row of ``model``'s table (:func:`_label`)."""
    return projection(model, _row_key(model, kind, s_point, month))


def _release(model, key):
    """Drop the ItemSpace at ``key``, the registry's key, and every value it has cached.

    Each splice row is needed once, so each is released when read, as ``run_sec.py
    --block`` releases its points (USLIB-SEC-PLAN.md F5).  Asked for again, the ItemSpace
    is made afresh and recomputes.
    """
    del model.Projection[key]


def _code(proj, label):
    """The argument that selects timing or kind ``label``: the model's int Reference of
    that name where it has one, as at stage ``"EC"``, else the string, as at ``"E"``."""
    value = proj.refs.get(label) if label in proj.refs else None
    return value if isinstance(value, int) and not isinstance(value, bool) else label


def _committed():
    """The committed SEC table as the file holds it, unvalidated, indexed by point_id."""
    return pd.read_csv(model_path(SEC).parent / TABLE, index_col="point_id")


def _sec_inputs(tmp_path, table, edits=None):
    """A copy of the product directory whose SEC table is ``table``, other inputs changed
    by ``edits``, as :func:`uk_sec_support.temp_inputs` takes them; its SEC folder."""
    return temp_inputs(tmp_path, model_path(SEC), model_points=table,
                       model_point_file=TABLE, edits=edits)


def _read_edited(tmp_path, edit, edits=None):
    """ULB_UK_SEC read from a copy whose SEC table is ``edit(_committed())``."""
    folder = _sec_inputs(tmp_path, edit(_committed()), edits)
    return mx.read_model(folder, name=_name("edited"))


def _set(column, points, value):
    """An edit of the table that writes ``value`` into ``column`` at ``points`` alone.

    The column is made ``object`` first, so a text or a number of another type can go in
    beside the numbers it holds: the file then carries what an extract with a bad cell
    would.
    """
    def edit(table):
        cells = table[column].astype(object)
        return table.assign(**{column: cells.where(~table.index.isin(points), value)})
    return edit


def _then(*edits):
    """One edit made of ``edits``, applied in turn."""
    def edit(table):
        for each in edits:
            table = each(table)
        return table
    return edit


def _refused(call, message):
    """``call()`` raises ``ValueError`` with ``message``, inside modelx's wrapper.

    modelx re-raises an error inside a formula as ``FormulaError``, with the original type
    and message in its text, so the text is asserted rather than a modelx class.
    """
    with pytest.raises(Exception) as excinfo:
        call()
    text = str(excinfo.value)
    assert "ValueError" in text and message in text, text


def _raised(err):
    """The line that names an error: modelx's ``FormulaError`` puts it second."""
    lines = [line for line in str(err).splitlines() if line.strip()]
    if type(err).__name__ == "FormulaError" and len(lines) > 1:
        return lines[1]
    return f"{type(err).__name__}: {lines[0] if lines else ''}"


def _sweep_s(proj):
    """Evaluate on an S point what the splice compares: the sweep, and the cells it misses.

    :func:`uk_sec_support.sweep` reaches ``ULB_UK_S``'s ``pols_if_at(t, "BEF_DECR")`` and
    ``av_pp_at(t, "BEF_GROWTH")`` nowhere, nor ``duration_mth``, ``av_per_segment_pp`` or
    ``lives``, which no formula of S reads; a cell S never evaluates is compared nowhere.
    They are evaluated here over the frame, so the splice and the future comparison see
    them too.
    """
    sweep(proj)
    proj.lives()
    for t in range(proj.proj_len()):
        proj.pols_if_at(t, "BEF_DECR")
        proj.av_pp_at(t, "BEF_GROWTH")
        proj.duration_mth(t)
        proj.av_per_segment_pp(t)


def _from(last):
    """An ``arg_map`` that skips every S key at month ``last`` or later, the ``t`` of a
    cell's arguments; keys without a ``t`` pass."""
    def mapped(name, args, last=last):
        return None if args and _month(args[0]) and args[0] >= last else args
    return mapped


def _only(month, skip=()):
    """An ``arg_map`` that keeps the S keys at ``month`` alone, but those of ``skip``,
    ``(name, args)`` pairs."""
    def mapped(name, args, month=month):
        if not (args and _month(args[0]) and args[0] == month):
            return None
        return None if (name, args) in skip else args
    return mapped


def _departure(s_proj, sec_proj, month):
    """What the depletion threshold changes where S runs on past the SEC frame (§6.6).

    The SEC frame ends at the first month whose fund opens at or below
    ``depletion_threshold``, and S's at the first that opens on 0 or less.  So where S
    projects months past the SEC frame, the first of them opens on a fund above 0 and at or
    below the threshold, a rounding the withdrawal cap closed the month before on; the SEC
    frame's survivors leave in its last month, where S's carry on; and nothing else in that
    month moves.  The mismatch lines, empty when the row is so.
    """
    end = sec_proj.proj_len()
    last = end - 1
    found = []
    opened = s_proj.av_pp(month + end)
    if not 0.0 < opened <= sec_proj.depletion_threshold:
        found.append(f"S's run-on month {month + end} opens on {opened!r}, which is not "
                     f"above 0 and at or below depletion_threshold, "
                     f"{sec_proj.depletion_threshold}")
    if sec_proj.fund_exhaust_mth() != sec_proj.duration_mth(end):
        found.append(f"fund_exhaust_mth() is {sec_proj.fund_exhaust_mth()}, not the policy "
                     f"month of t = {end}, {sec_proj.duration_mth(end)}")
    survivors = s_proj.pols_if_at(month + last, "AFT_DECR")
    left = sec_proj.pols_maturity(last)
    if not math.isclose(left, survivors, rel_tol=1e-9, abs_tol=0.0):
        found.append(f"pols_maturity({last}) is {left!r}, not S's survivors "
                     f"pols_if_at({month + last}, 'AFT_DECR'), {survivors!r}")
    aft = sec_proj.pols_if_at(last, _code(sec_proj, "AFT_DECR"))
    if aft != 0.0 or s_proj.pols_maturity(month + last) != 0.0:
        found.append(f"in the SEC frame's last month the count carries {aft!r} on, and S "
                     f"matures {s_proj.pols_maturity(month + last)!r}: both must be 0")
    return found


def _compare(s_proj, sec_proj, month, exempt, columns=None):
    """Where SEC's row departs from S's point from S month ``month`` on.

    First the frames, ``result_cf`` (over ``columns``, or every column both hold) and
    ``result_uf``, SEC row ``t`` against S row ``t + month``, frames ending together; then
    every cell of S's but ``exempt``, :data:`REPORTS` and :data:`RESIDUALS`, at every
    argument S cached inside its frame from ``month`` on, moved onto SEC's clock.  Both to
    1e-9 relative with no absolute floor (USLIB-SEC-PLAN.md §5.2, T2, precised at M11): a
    floor of 1e-9 passes an error of 1% in any value below 1e-7, and the counts late in a
    long frame, under the splice's switches, fall below 1e-12.  Then the cells of
    :data:`RESIDUALS`, and ``result_uf``, which shows the excess gain, at the floor of
    1e-9: their exact value is 0, and the computed one moves by an ulp of what it closes
    when an opening state comes back from the CSV one ulp off; every other value
    ``result_uf`` shows is a cell held at no floor.

    Two departures are by design, and taken as such.  Where the frame ends because the fund
    is exhausted, its last month closes the fund on a subtraction whose exact value is 0,
    and whose computed value, 0 or a rounding of either sign floored at 0, turns on the
    fund's last bit, which a fund read back from the CSV may hold otherwise: that month is
    compared at the floor (VA's ``_residue_months``, USLIB-SEC-PLAN.md §7.7, *Record —
    M9*).  And where S's frame runs past SEC's, on a rounding at or below
    ``depletion_threshold``, the months the two run alike are compared so, S's months past
    the SEC frame are not, the count's exit in the SEC frame's last month is held to S's
    survivors, and the rest of the departure is :func:`_departure`'s.  Returns the
    mismatch lines, empty when the row is S's.
    """
    end = sec_proj.proj_len()
    s_end = s_proj.proj_len() - month
    if s_end < end:
        return [f"the SEC frame runs past S's: S's ends at t = {s_end - 1} on SEC's clock, "
                f"SEC's at t = {end - 1}"]
    cut = s_end > end
    last = end - 1
    exhausted = sec_proj.fund_exhaust_mth() <= sec_proj.horizon_mths()
    found = _departure(s_proj, sec_proj, month) if cut else []
    for report in REPORTS:
        keep = columns if report == "result_cf" else None
        floor = FLOOR if report in RESIDUALS else 0.0
        s_df = s_proj.cells[report]().loc[: month + last]
        sec_df = sec_proj.cells[report]()
        if exhausted:
            if last > 0 and len(s_df.loc[month: month + last - 1]):
                found += [f"{report}: {line}" for line in frame_mismatches(
                    s_df.loc[: month + last - 1], sec_df.loc[: last - 1], t_offset=month,
                    columns=keep, atol=floor)]
            found += [f"{report}, its last month: {line}" for line in frame_mismatches(
                s_df.loc[month + last:], sec_df.loc[last:], t_offset=month, columns=keep,
                atol=FLOOR)]
        else:
            found += [f"{report}: {line}" for line in frame_mismatches(
                s_df, sec_df, t_offset=month, columns=keep, atol=floor)]
    others = exempt | set(REPORTS) | ({"fund_exhaust_mth"} if cut else set())
    head = _from(month + last) if exhausted else None
    found += twin_mismatches(s_proj, sec_proj, t_offset=month, exempt=others | RESIDUALS,
                             arg_map=head, atol=0.0, codes=codes(sec_proj))
    found += twin_mismatches(s_proj, sec_proj, t_offset=month,
                             exempt=others | (set(s_proj.cells) - RESIDUALS),
                             arg_map=head, codes=codes(sec_proj))
    if exhausted:
        exits = {("pols_if_at", (month + last, "AFT_DECR")),
                 ("pols_maturity", (month + last,))} if cut else set()
        found += [f"its last month: {line}" for line in twin_mismatches(
            s_proj, sec_proj, t_offset=month, exempt=others,
            arg_map=_only(month + last, exits), codes=codes(sec_proj))]
    return found


def _continues_s(s_proj, sec_proj, month):
    """Where a committed row departs from S's point ``s_proj`` from S month ``month`` on.

    The splice's comparison (:func:`_compare`), on the committed model at the shipped
    assumptions.  The shipped 2.5% expense inflation runs from issue in S and from the
    valuation date here (D7), so :data:`INFLATED`'s two columns, and
    :data:`INFLATION_CELLS`, differ by design and are left out; the inflation test holds
    them.  Every other column and cell must agree, to 1e-9 relative, with no absolute floor
    but on the residuals and in an exhausted frame's last month.
    """
    keep = [c for c in s_proj.result_cf().columns if c not in INFLATED]
    return _compare(s_proj, sec_proj, month, SPLICE_EXEMPT | INFLATION_CELLS, keep)


def _case_id(kind, s_point, month):
    """A case's id: ``point2-d12``, or ``point2-k3`` if issued later."""
    if kind == "future":
        return f"point{s_point}-k{-month}"
    return f"point{s_point}-" + (f"d{month}" if kind == "derived" else f"{kind}{month}")


def _case(case, core, case_id):
    """One parametrized case: run by default if it is in ``core``, else on the full grid."""
    return pytest.param(*case, id=case_id, marks=() if case in core else FULL_ONLY)


def _selected(cases, core):
    """The cases this run makes rows for: the core, or every one under UKLIB_SEC_FULL."""
    return [case for case in cases if SEC_FULL or case in core]


# Every row the splice compares, as (row_kind, S point, source_mth), T3's included, and the
# default run's among them.
GRID = (*SPLICES, *IN_FORCE_TWINS, *(("future", p, -k) for p, k in FUTURES))
CORE_GRID = frozenset({*CORE_SPLICES, *(("future", p, -k) for p, k in CORE_FUTURES)})


# ---------------------------------------------------------------------------
# Fixtures


@pytest.fixture(scope="module")
def sec_read():
    """ULB_UK_SEC read in place, as committed, and swept once, cold; what it met.

    The model is first asked for ``duration_mth(500)`` on the twin of S point 1, and the
    keys that call leaves in ``duration_mth`` are kept.  Then every committed point is
    swept (:func:`uk_sec_support.sweep`: ``result_cf``, the other reports and the checks),
    in table order and each column in ascending ``t``, under a recursion limit lowered to
    :data:`CALL_DEPTH`, and whatever that raises is kept, point by point, rather than
    raised.  So the record says what a cold model does, which the clock and depth test
    asserts (D3, R2), and every test on the committed model reads a model already swept:
    the sweep is paid once, not once for each.  Returns ``(model, record)``.
    """
    model = mx.read_model(model_path(SEC), name=_name("sec"))
    first = _row(model, "twin", 1, 0)
    record = {"duration_mth(500)": first.duration_mth(500),
              "keys": list(first.cells["duration_mth"].keys()), "deep": []}
    labels = model.Data.model_point_table().index
    limit = mx.get_recursion()
    mx.set_recursion(CALL_DEPTH)
    try:
        for key, point_id in zip(point_keys(model), labels):
            try:
                sweep(projection(model, key))
            except Exception as err:            # kept, so every point is swept
                record["deep"].append(f"point {point_id}: the sweep raised {_raised(err)}")
    finally:
        mx.set_recursion(limit)
    yield model, record
    model.close()


@pytest.fixture(scope="module")
def sec_model(sec_read):
    """ULB_UK_SEC read in place, as committed, with every point swept (sec_read)."""
    return sec_read[0]


@pytest.fixture(scope="module")
def s_model():
    """ULB_UK_S read in place, as committed, with every point swept.

    T6 regenerates the SEC inputs from it, which would otherwise project every S point
    again (USLIB-SEC-PLAN.md §4, *Carried into Phase 1*), and the in-force tests read S's
    months off it.
    """
    model = mx.read_model(model_path(TWIN), name=_name("s"))
    for key in point_keys(model):
        _sweep_s(projection(model, key))
    yield model
    model.close()


@pytest.fixture(scope="module")
def spliced(tmp_path_factory):
    """S and SEC on the splice's inputs, with :data:`SPLICED_REFS` set in both.

    S is read from a copy of the product directory whose table has the variants appended.
    SEC runs on the same assumption tables, and on a model point table of its own, built by
    the generator from the registered spec with its rows replaced by the cases this run
    selects, the core or the full grid (:func:`_selected`), out of this S model, so each row
    opens with the state of the very run it is compared with.  No input table moves with
    ``d``: ULB's one valuation-clock input is the ``inflation_rate`` Reference.  Every S
    point is then swept (:func:`_sweep_s`), and stays swept; each SEC row is projected by
    the case that compares it and released once compared (:func:`_settle`).
    """
    root = tmp_path_factory.mktemp("spliced")
    s_folder = temp_inputs(root / "s", model_path(TWIN),
                           model_points=_s_table_with_variants())
    s = mx.read_model(s_folder, name=_name("s_spliced"))
    for ref, value in SPLICED_REFS.items():
        setattr(s.Projection, ref, value)
    derived = [(p, d) for kind, p, d in _selected(SPLICES + IN_FORCE_TWINS, CORE_SPLICES)
               if kind == "derived"]
    spec = dataclasses.replace(SPEC, derived=tuple(derived),
                               future=tuple(_selected(FUTURES, CORE_FUTURES)))
    table, companions = build_sec_table(spec, s)
    assert companions == {}
    sec_folder = _sec_inputs(root / "sec", table)
    sec = mx.read_model(sec_folder, name=_name("sec_spliced"))
    for ref, value in SPLICED_REFS.items():
        setattr(sec.Projection, ref, value)
    for key in point_keys(s):
        _sweep_s(projection(s, key))
    yield s, sec
    sec.close()
    s.close()


@pytest.fixture(scope="module")
def splice_records():
    """What each splice row was found to do once compared, by case (:func:`_settle`)."""
    return {}


# ---------------------------------------------------------------------------
# The splice's records
#
# Each T2 and T3 case compares its row with S, then records what the rules test and the
# core grid's reach need of the row, and releases it (_settle).  So each of the two tests
# reads the records, and computes any case no earlier test has recorded, which keeps it
# whole when run alone.


def _cached_args(cells):
    """The argument tuple of every key ``cells`` has cached (uk_sec_support._args)."""
    n = len(cells.parameters)
    return [() if n == 0 else (key,) if n == 1 else tuple(key)
            for key in list(cells.keys())]


def _month(x):
    return isinstance(x, int) and not isinstance(x, bool)


def _month_of(node):
    """The month a precedent ``node`` is keyed by, its ``t``, or None if it takes none."""
    params = getattr(node.obj, "parameters", None) or ()
    u = node.args[params.index("t")] if "t" in params else None
    return u if _month(u) else None


def _months_read(node, reach):
    """The calls keyed by a month that precedent ``node`` reads, as ``(reader, cell, month,
    text)``.

    ``node`` itself if it is keyed by ``t``, its reader ``None``.  Otherwise every
    month-keyed call its own precedents read, followed through every call keyed by no
    month, such as ``proj_len()`` and the ``fund_exhaust_mth()`` it reads, as far as the
    dependency graph goes, each with the call keyed by no month that reads it: so a read
    that looks ahead through a cell taking no ``t`` is the reader's, and the reader names
    the loop that makes it (USLIB-SEC-PLAN.md §5.2, T2, precised at M12; ``DIA_US_SEC``'s
    form).  ``reach`` holds what each call keyed by no month reads, so that each is walked
    once a row, and the walk is a loop, not a recursion.
    """
    month = _month_of(node)
    if month is not None:
        return {(None, node.obj.name, month, f"{node.obj.name}{node.args}")}
    top = (id(node.obj), node.args)
    stack, seen = [(node, False)], set()
    while stack:
        here, done = stack.pop()
        key = (id(here.obj), here.args)
        if key in reach:
            continue
        if done:
            found = set()
            for pred in here.preds:
                month = _month_of(pred)
                if month is not None:
                    found.add((here.obj.name, pred.obj.name, month,
                               f"{here.obj.name}{here.args} -> {pred.obj.name}{pred.args}"))
                elif "t" not in (getattr(pred.obj, "parameters", None) or ()):
                    found |= reach[(id(pred.obj), pred.args)]
            reach[key] = found
            continue
        if key in seen:
            continue
        seen.add(key)
        stack.append((here, True))
        for pred in here.preds:
            if _month_of(pred) is None and (id(pred.obj), pred.args) not in reach:
                if "t" not in (getattr(pred.obj, "parameters", None) or ()):
                    stack.append((pred, False))
    return reach[top]


def _rule_breaches(proj):
    """R1 and R2's look-ahead on one row, once it has run whole.

    The row's reports and checks are run (:func:`uk_sec_support.sweep`), and then every
    monthly cell at every month of the frame and the month after it, as the C step's sweep
    runs them (:func:`uk_sec_support.full_sweep`): no report of a row need read every
    state, and a base at ``t == 0`` would hide in a cell the reports leave unread
    (USLIB-SEC-PLAN.md §5.2, T2, precised at M4).  ``{"negative": [...], "early": [...],
    "ahead": [...], "raised": [...]}``: every cached call with a negative argument; every
    call keyed by a month before ``t_entry()`` that a call keyed by a month at or after it
    reads; every call keyed by a month beyond ``t + 1`` that a call keyed by ``t`` reads, but
    :data:`LOOK_AHEAD`'s, at months up to ``proj_len()``; and every call the full sweep found
    raising.  A call reads its precedents, as modelx's dependency graph records them, and,
    through a precedent keyed by no month, whatever that precedent reads in turn
    (:func:`_months_read`): every count reads the frame, ``proj_len()``, which reads
    ``fund_exhaust_mth()``, whose search reads the fund to the frame's end.
    """
    sweep(proj)
    raised = [f"{name}{args}: {text}" for (name, args), text in full_sweep(proj).items()]
    entry, end = proj.t_entry(), proj.proj_len()
    negative, early, ahead = [], [], []
    reach = {}
    for name, cells in proj.cells.items():
        t_pos = cells.parameters.index("t") if "t" in cells.parameters else None
        for args in _cached_args(cells):
            if any(_month(a) and a < 0 for a in args):
                negative.append(f"{name}{args}")
            if t_pos is None:
                continue
            t = args[t_pos]
            for node in cells.preds(*args):
                if _month_of(node) is None and "t" in (
                        getattr(node.obj, "parameters", None) or ()):
                    continue
                for reader, cell, u, text in sorted(_months_read(node, reach),
                                                    key=lambda r: (r[2], r[3])):
                    if u < entry <= t:
                        early.append(f"{name}{args} -> {text}")
                    if u <= t + 1 or ((reader, cell) in LOOK_AHEAD and u <= end):
                        continue
                    ahead.append(f"{name}{args} -> {text}")
    return {"negative": negative, "early": early, "ahead": ahead, "raised": raised}


def _excess(x, t):
    """The withdrawals since issue less the allowance accrued in month ``t``, the excess
    gain's max's argument."""
    return x.wd_cum_pp(t) - x.allowance_cum_pp(t)


def _scheduled(x):
    """The month's scheduled withdrawal, before either cap."""
    return x.wd_rate() * x.premium() / 12.0


# What test_the_core_grid_reaches_every_branch asks of the core's rows in the model's own
# values, which no column of the table shows: each holds of some core row, or of a core row
# in some month of its frame.  At the valuation date, both opening-state columns in use, the
# withdrawals since issue past the premium, so that the GMDB opens at 0, and short of it,
# the GMDB in the money and out of it, and an excess gain carried in.  Later in the frame,
# every branch and both sides of each min and max the full grid reaches: the withdrawal's
# three bounds, the cap's two bases, the GMDB in and out of the money on its charge and on
# its death benefit, the fund closed on 0 and on a rounding, the excess gain, the
# surrender table's last year, the surrender cap, the allowance step, the allowance's
# twenty years, and the frame's two ends.
AT_VALUATION = {
    "a fund carried in": lambda x: x.duration_mth_init() > 0 and x.av_pp_init() > 0.0,
    "withdrawals carried in": lambda x: x.wd_cum_pp_init() > 0.0,
    "the GMDB opened from what is left of it": lambda x: (
        x.gmdb_flag() and x.duration_mth_init() > 0 and x.gmdb_guarantee_pp(0) > 0.0),
    "the GMDB opened at 0, all drawn": lambda x: (
        x.gmdb_flag() and x.duration_mth_init() > 0 and x.gmdb_guarantee_pp(0) == 0.0),
    "an excess gain carried in": lambda x: (
        x.duration_mth_init() > 0 and x.wd_cum_pp_init() > x.allowance_cum_pp(0)),
    "the GMDB in the money at t = 0": lambda x: (
        x.gmdb_flag() and x.gmdb_charge_pp(x.t_entry()) > 0.0),
}
IN_FRAME = {
    "the scheduled withdrawal paid": lambda x, t: (
        x.wd_pp(t) > 0.0 and x.wd_pp(t) == _scheduled(x)),
    "the 7.5% cap binding": lambda x, t: (
        x.wd_pp(t) < _scheduled(x) and x.wd_pp(t) == max(
            0.0, x.wd_cap_pp(t) / 12.0 - x.adviser_charge_pp(t))
        and x.wd_pp(t) < x.av_pp_at(t, "AFT_CHARGE") - x.adviser_charge_pp(t)
        - x.gmdb_charge_pp(t)),
    "the fund drawn to nothing": lambda x, t: (
        _scheduled(x) > 0.0 and x.wd_pp(t) < _scheduled(x)
        and x.av_pp_at(t, "AFT_WD") <= x.depletion_threshold),
    "the cap on the fund": lambda x, t: x.av_pp_at(t, "AFT_CHARGE") > x.premium(),
    "the cap on the premium": lambda x, t: (
        x.is_active(t) and x.av_pp_at(t, "AFT_CHARGE") < x.premium()),
    "the GMDB charge in the money": lambda x, t: x.gmdb_charge_pp(t) > 0.0,
    "the GMDB charge out of the money": lambda x, t: (
        x.gmdb_flag() and x.is_active(t) and x.gmdb_guarantee_pp(t) > 0.0
        and x.gmdb_charge_pp(t) == 0.0),
    "the GMDB paying on death": lambda x, t: (
        x.gmdb_flag() and x.gmdb_guarantee_pp(t) > x.db_uplift() * x.av_pp_at(t, "AFT_WD")
        and x.pols_death(t) > 0.0),
    "the fund closed on 0": lambda x, t: (
        t == x.proj_len() - 1 and x.av_pp_at(t, "AFT_WD") == 0.0
        and x.fund_exhaust_mth() <= x.horizon_mths()),
    "the fund closed on a rounding": lambda x, t: (
        t == x.proj_len() - 1 and 0.0 < x.av_pp_at(t, "AFT_WD") <= x.depletion_threshold),
    "an excess gain": lambda x, t: _excess(x, t) > 0.0,
    "no excess gain": lambda x, t: x.is_active(t) and _excess(x, t) < 0.0,
    "inside the surrender table": lambda x, t: (
        x.is_active(t) and x.policy_year(t) <= x.data.surr_last_year()),
    "past the surrender table's last year": lambda x, t: (
        x.is_active(t) and x.policy_year(t) > x.data.surr_last_year()),
    "the surrender cap binding": lambda x, t: (
        x.is_active(t) and x.surr_rate(t) == x.surr_rate_cap
        < x.surr_rate_base(t) * x.perf_factor(t) * x.allow_factor(t)),
    "the surrender cap not binding": lambda x, t: (
        x.is_active(t) and x.surr_rate(t) < x.surr_rate_cap),
    "the allowance-exhaustion step": lambda x, t: (
        x.is_active(t) and x.allow_factor(t) == x.allow_step),
    "before the step": lambda x, t: x.is_active(t) and x.allow_factor(t) == 1.0,
    "the allowance accruing": lambda x, t: (
        x.is_active(t) and x.policy_year(t) < x.allowance_years),
    "the allowance spent": lambda x, t: (
        x.is_active(t) and x.policy_year(t) > x.allowance_years),
    "the frame ending at exhaustion": lambda x, t: (
        x.pols_maturity(t) > 0.0 and x.fund_exhaust_mth() <= x.horizon_mths()),
    "the frame ending at the limiting age": lambda x, t: (
        x.pols_maturity(t) > 0.0 and x.fund_exhaust_mth() > x.horizon_mths()),
}


def _branches(x):
    """The names in :data:`AT_VALUATION` and :data:`IN_FRAME` that hold of row ``x``."""
    reached = {what for what, holds in AT_VALUATION.items() if holds(x)}
    frame = range(x.t_entry(), x.proj_len())
    return reached | {what for what, holds in IN_FRAME.items()
                      if any(holds(x, t) for t in frame)}


def _settle(records, case, model, key):
    """Record what the rules and the core grid's reach need of a row, and release it.

    ``case`` is the row's (row_kind, S point, source_mth) and ``key`` its registry key in
    ``model``, the splice's SEC model.  A T2 or T3 case calls this once it has compared
    the row, whatever the comparison found, so the row is released either way.  The record
    is :func:`_rule_breaches`'s, with the row's :func:`_branches`, and a row that raises is
    recorded as raising, which the rules test reports.
    """
    try:
        proj = projection(model, key)
        record = _rule_breaches(proj)
        record["branches"] = _branches(proj)
        record["failed"] = None
    except Exception as err:                    # recorded, and reported by the rules test
        record = {"negative": [], "early": [], "ahead": [], "raised": [],
                  "branches": set(), "failed": _raised(err)}
    finally:
        _release(model, key)
    records[case] = record
    return record


def _record_of(spliced, records, case):
    """The record of ``case``, from the case that compared its row or, failing it, now."""
    if case not in records:
        sec = spliced[1]
        _settle(records, case, sec, _row_key(sec, *case))
    return records[case]


# ---------------------------------------------------------------------------
# T2 -- the splice


@pytest.mark.parametrize(
    "kind, s_point, month",
    [_case(case, CORE_SPLICES, _case_id(*case)) for case in SPLICES + IN_FORCE_TWINS])
def test_an_in_force_point_continues_its_s_projection(spliced, splice_records, kind,
                                                      s_point, month):
    """Opened with S's state at month d, the point is S from d on, in every cell of S's.

    This is the test that says the opening state is complete: a state column the SEC row
    did not carry, or carried from the wrong instant, would make SEC part from S here, and
    nowhere else, because on a point issued at ``t = 0`` the two clocks coincide and the
    opening state is the issue value.  For the same reason it is the test that catches a
    policy month passed as ``t`` (R1a) and a look-back that stops at the wrong month.  The
    frame comparisons read SEC row ``t`` against S row ``t + d`` in every column of
    ``result_cf`` and ``result_uf``, and fail frames that end apart.  The cell comparison
    then evaluates every cell of S's but :data:`SPLICE_EXEMPT`, at every argument S cached
    inside its own frame from month ``d`` on, moved onto SEC's clock: the counts, the fund
    at each of its timings, the withdrawals since issue, the GMDB, the allowance and the
    excess gain among them.  Each compares to 1e-9 relative with no absolute floor, but the
    residuals and an exhausted frame's last month, which keep the floor of 1e-9, and on the
    adviser charge's rows S's month past the SEC frame, which the depletion threshold drops
    (:func:`_compare`).  An S cell this model lacked would fail it.

    The months about policy year 21 are the ones that see the withdrawals since issue read
    at the wrong instant: the GMDB of the anchor's pattern runs out there, and the excess
    gain first appears.  The row is then recorded for the rules test and released
    (:func:`_settle`).
    """
    s, sec = spliced
    key = _row_key(sec, kind, s_point, month)
    s_proj, sec_proj = _point(s, s_point), projection(sec, key)
    try:
        assert _compare(s_proj, sec_proj, month, SPLICE_EXEMPT) == []
    finally:
        _settle(splice_records, (kind, s_point, month), sec, key)


# ---------------------------------------------------------------------------
# T3 -- future new business


@pytest.mark.parametrize(
    "s_point, k",
    [_case(case, CORE_FUTURES, _case_id("future", case[0], -case[1]))
     for case in FUTURES])
def test_future_new_business_is_the_s_projection_k_months_on(spliced, splice_records,
                                                             s_point, k):
    """Issued k months after the valuation date, the point is S's projection k months on.

    SEC rows ``k ..`` are S rows ``0 ..``, ending together where the fund is exhausted or
    at the limiting age, in ``result_cf`` and ``result_uf``, and every cell of S's but
    :data:`FUTURE_EXEMPT` agrees at every argument S cached inside its own frame, moved
    ``k`` later.  Each compares as the splice compares, with no absolute floor but on the
    residuals and in an exhausted frame's last month (:func:`_compare`).  An S cell this
    model lacked would fail it.  Before issue every column of ``result_cf``, ``result_uf``
    and ``result_pols`` is an exact zero, and the policies arrive in month ``k`` as new
    business.

    The last assertions are R1 and D4's base rule made testable.  After the reports, no
    decrement rate or read keyed by a policy year or an age has been evaluated at a month
    before issue.  A count recursion based at ``t == 0`` rather than at ``t_entry()``, or a
    decrement count that evaluates its rate before asking whether the month is in cover,
    still gives the right numbers.  And the frame is searched from issue: searched from
    ``t = 0``, the empty fund before issue would end it there.

    The pre-issue rows are asserted present before they are asserted zero, in every report:
    a frame that opened at issue would have none, its zeros would hold of nothing, and the
    comparisons with S, which start at issue, would not see it.  The row is then recorded
    for the rules test and released (:func:`_settle`).
    """
    s, sec = spliced
    key = _row_key(sec, "future", s_point, -k)
    s_proj, sec_proj = _point(s, s_point), projection(sec, key)
    try:
        frames = {name: sec_proj.cells[name]() for name in (*REPORTS, "result_pols")}
        assert _compare(s_proj, sec_proj, -k, FUTURE_EXEMPT) == []
        for report, frame in frames.items():
            assert list(frame.index[:k]) == list(range(k)), report
            assert (frame.loc[:k - 1] == 0.0).all().all(), report
        assert sec_proj.pols_new_biz(k) == sec_proj.policy_count() == 1.0
        early = {name: sorted(args[0] for args in _cached_args(sec_proj.cells[name])
                              if args[0] < k)
                 for name in DECREMENT_RATES}
        assert not any(early.values()), f"rates evaluated before issue: {early}"
    finally:
        _settle(splice_records, ("future", s_point, -k), sec, key)


# ---------------------------------------------------------------------------
# D11's R1 and R2, and D3's closed-form clock


@pytest.mark.parametrize("grid", [pytest.param("core", id="core"),
                                  pytest.param("full", id="full", marks=FULL_ONLY)])
def test_no_cell_is_called_before_the_valuation_date_or_reads_far_ahead(spliced,
                                                                        splice_records,
                                                                        grid):
    """R1, its look-back and R2's look-ahead, on the rows T2 and T3 compare: core or rest.

    Each is a rule of how the model computes, not of what, so no number shows a breach,
    and on a point issued at ``t = 0`` the two clocks coincide and hide it from T1 too.
    The splice's rows are points in force at every month T2 names, the variants among them,
    and points issued later, and on each the reports, the checks and the full sweep are run
    first (:func:`_rule_breaches`):

    * R1: no cell holds a negative argument.  modelx evaluates one without complaint, and
      a compiled cache raises ``IndexError`` below 0 (USLIB-SEC-PLAN.md F4).  A policy
      month turned into ``t`` by subtracting ``duration_mth_init()`` (R1a) goes negative
      on a point in force past it.
    * R1's look-back stops at ``t_entry()``: no cell evaluated at a month from
      ``t_entry()`` on read a month before it, directly or through a cell keyed by no
      month.  On a point issued later a recursion based at ``t == 0``, or the exhaustion
      search started there, reads the pre-issue zeros, so no number need show it and no
      argument goes negative.
    * R2's look-ahead: no cell evaluated at month ``t`` read a cell keyed by a month beyond
      ``t + 1``, as modelx's dependency graph records each cached call's precedents and
      through every precedent keyed by no month, but the loop R2 admits: the exhaustion
      search, ``fund_exhaust_mth()``, which reads the fund to the frame's end and which
      every count reads through ``proj_len()`` (:data:`LOOK_AHEAD`), at months up to
      ``proj_len()``, the first whose fund is exhausted.
    * And no call of the full sweep raised.

    Each row was scanned by the T2 or T3 case that compared it (:func:`_settle`), and a row
    no case has scanned is scanned here.  The core case covers the core's rows, the full
    case every other row of the full grid, with ``UKLIB_SEC_FULL=1``.  The new-business
    twins in the splice's table are no case's, and are left out: on them the clocks
    coincide, and T1 compares them with S cell by cell.  The closed-form clock and the
    recursion depth are asserted on the committed model, in the tests after this one.
    """
    cases = [case for case in GRID if (case in CORE_GRID) == (grid == "core")]
    negative, early, ahead, raised, failed = [], [], [], [], []
    for case in cases:
        record, where = _record_of(spliced, splice_records, case), _case_id(*case)
        negative += [f"{where}: {call}" for call in record["negative"]]
        early += [f"{where}: {read}" for read in record["early"]]
        ahead += [f"{where}: {read}" for read in record["ahead"]]
        raised += [f"{where}: {call}" for call in record["raised"]]
        if record["failed"]:
            failed.append(f"{where}: {record['failed']}")
    assert cases, f"the {grid} grid has no rows"
    assert not failed, f"rows that raised: {failed[:10]}"
    assert not raised, f"calls the full sweep found raising: {raised[:10]}"
    assert not negative, f"called before the valuation date: {negative[:10]}"
    assert not early, f"read before issue from the books: {early[:10]}"
    assert not ahead, f"read beyond t + 1: {ahead[:10]}"


def test_the_exhaustion_search_is_the_one_far_read_and_stays_in_the_frame(sec_model):
    """The exhaustion search, R2's admitted loop, reads the fund from issue to the frame's
    end, and nothing else reads ahead.

    :data:`LOOK_AHEAD` admits one reader and one cell, and the rules test above holds every
    other read to ``t + 1``; this holds what the admitted one reads, on every committed
    point: of the cells keyed by a month, ``fund_exhaust_mth()`` has read ``av_pp`` alone,
    as modelx's dependency graph records it, and at exactly the months from ``t_entry()``
    to the frame's end, ``proj_len()`` itself where the fund is exhausted there, and the
    frame's last month where the frame ends at the limiting age.  A search from ``t = 0``
    reads the months before a later issue, and one past the frame reads months no report
    reads (§6.6).
    """
    table = sec_model.Data.model_point_table()
    for key, point_id in zip(point_keys(sec_model), table.index):
        p = projection(sec_model, key)
        monthly = [pred for pred in p.cells["fund_exhaust_mth"].preds()
                   if _month_of(pred) is not None]
        assert {pred.obj.name for pred in monthly} == {"av_pp"}, point_id
        read = sorted(pred.args[0] for pred in monthly)
        exhausted = p.fund_exhaust_mth() <= p.horizon_mths()
        end = p.proj_len() if exhausted else p.proj_len() - 1
        assert read == list(range(p.t_entry(), end + 1)), (point_id, read[:3], read[-3:])


def test_the_policy_clock_is_a_closed_form_and_no_recursion_runs_backward(sec_read):
    """D3 and R2's recursions, on the committed model as it was first swept, cold.

    Both need a model on which nothing had been evaluated yet, which is what the fixture
    held when it made the record asserted here:

    * D3: the policy clock is the closed form.  Called first, ``duration_mth(500)``
      evaluates ``duration_mth`` once, where ``BasicTerm_SE``'s recursion would evaluate
      it at all 501 months from 0.
    * R2's recursions run forward: under modelx's recursion limit lowered to
      :data:`CALL_DEPTH`, every committed point is swept, each column in ascending ``t``.
      A forward recursion, through ``t - 1``, finds the month before already cached and
      stays shallow, which is why D3 is asserted on its own.  A backward recursion over the
      frame, through ``t + 1``, keeps every step within the look-ahead but opens a chain as
      long as the frame, which a compiled model would run on the C stack (F7), and fails
      here.
    """
    record = sec_read[1]
    assert record["duration_mth(500)"] == 500
    assert record["keys"] == [500]
    assert not record["deep"], f"under a recursion limit of {CALL_DEPTH}: {record['deep']}"


# How deep a cold call may run beyond its chain, one cell a month from its month back to
# t_entry() (D5): the cells above the chain and those below it, the first month's rates and
# Data's first reads of its tables.  Each chain head called cold alone, before anything else
# on a read of its own, runs at most 10 cells beyond its chain: the fund 5 or 6, the count
# 4, the withdrawals since issue 7, the excess gain 8, the GMDB's guarantee 7, net_cf 9 or
# 10, the deepest call a projection makes, on every shape at its longest cover (measured at
# M9).  Term's 16, as for uslib's Term (USLIB-SEC-PLAN.md D5).  Any chain of two cells a
# month runs a frame's length beyond; ULB_UK_S's fund runs four, about 5,400 levels at the
# longest cover (UKLIB-SEC-PLAN.md §6.6).
CHAIN_OVERHEAD = 16

# The contract's longest cover (product-spec.md, held by proj_len()): a bond issued at
# issue_age_min, 18, the youngest the mortality table rates, whose fund lasts to the
# limiting age, omega_age 120: 1,224 months from issue.
YOUNGEST = 18

# Each shape and the chains it runs, called cold in the last month of the frame at its own
# longest cover, each on a read of its own: (the S point whose twin it is, its frame from
# issue at YOUNGEST, the chain heads, each a (cell, the timing it takes, or None)).  The
# accumulation cell, no withdrawals, runs to the limiting age; the custom 3% withdraws to
# policy month 1,176, where its fund runs out at that age; the GMDB point withdraws 5% to
# month 353, its guarantee reading the withdrawals' chain; the adviser charge to 323.  Each
# is issued now and future_horizon_mth, 120 months, on.
CHAIN_HEADS = (("net_cf", None), ("av_pp", None), ("av_pp_at", "AFT_WD"),
               ("pols_if_at", "BEF_NB"), ("wd_cum_pp", None), ("excess_gain_pp", None),
               ("check_pols_roll_fwd_resid", None))
SHAPES = ((2, 1224, CHAIN_HEADS), (6, 1176, CHAIN_HEADS),
          (4, 353, CHAIN_HEADS + (("gmdb_guarantee_pp", None), ("claims", "DEATH"))),
          (3, 323, CHAIN_HEADS))


def _cold_depth(proj, cell, args):
    """How many cells deep ``cell(*args)`` runs on ``proj``, by modelx's stack trace."""
    mx.start_stacktrace(maxlen=None)
    try:
        proj.cells[cell](*args)
        trace = mx.get_stacktrace(summarize=False)
    finally:
        mx.stop_stacktrace()
    level = deepest = 0
    for event, *_ in trace:
        level += 1 if event == "ENTER" else -1
        deepest = max(deepest, level)
    return deepest


def _longest_cover(tmp_path):
    """A copy whose table holds each of :data:`SHAPES` at its longest cover: the twin of
    its S point issued at :data:`YOUNGEST`, now and 120 months on, the shipped
    ``future_horizon_mth``.  ``(folder, [(label, frame, t_entry, heads)])``."""
    committed = _committed()
    rows, frames = [], []
    top = committed.index.max()
    for s_point, months, heads in SHAPES:
        twin = _label(committed, "twin", s_point, 0)
        for k in (0, 120):
            top += 1
            row = committed.loc[[twin]].assign(age_at_entry=YOUNGEST, duration_mth=-k)
            row.index = pd.Index([top], name="point_id")
            rows.append(row)
            frames.append((top, months + k, k, heads))
    return _sec_inputs(tmp_path, pd.concat(rows)), frames


# modelx warns as its stack trace starts and stops, which is all the test does with it.
@pytest.mark.filterwarnings("ignore:call stack trace:UserWarning")
def test_every_chain_runs_one_cell_a_month_from_a_cold_start(tmp_path):
    """Called cold, each chain runs one cell a month back to ``t_entry()``, no more (D5).

    No number shows how deep a chain runs, and a compiled model runs it on the C stack, so
    a chain of two cells a month, which gives the same numbers, needs twice the stack on
    every platform (F7); ``ULB_UK_S``'s fund chain runs four cells a month, through
    ``av_pp_at`` at three timings, and its count three.  On a model just read, nothing is
    cached, so modelx's stack trace counts how deep a call runs, against one cell a month
    back to ``t_entry()`` and :data:`CHAIN_OVERHEAD` more, with modelx's recursion limit
    where the module leaves it: each chain head of each of :data:`SHAPES`, in the last month
    of the frame, each on a read of its own and called first, since ``proj_len()`` searches
    the fund in ascending ``t`` and would leave it cached, with :data:`SWITCHED_ON` set.  At
    each shape's longest cover, issued at 18, the youngest the table rates, now and 120
    months on (:func:`_longest_cover`); each row's frame is asserted after.
    """
    folder, frames = _longest_cover(tmp_path)
    found = []
    for label, months, entry, heads in frames:
        for cell, timing in heads:
            fresh = mx.read_model(folder, name=_name("cold"))
            try:
                for ref, value in SWITCHED_ON.items():
                    setattr(fresh.Projection, ref, value)
                p = _point(fresh, label)
                last = months - 1
                args = (last,) if timing is None else (last, _code(p, timing))
                depth, chain = _cold_depth(p, cell, args), last - entry
                assert (p.proj_len(), p.t_entry()) == (months, entry), label
                if not chain <= depth <= chain + CHAIN_OVERHEAD:
                    found.append(f"point {label}: {cell}{args} cold runs {depth} cells "
                                 f"deep, where one cell a month back to t_entry() "
                                 f"{entry} is {chain} and {CHAIN_OVERHEAD} more are "
                                 f"allowed")
            finally:
                fresh.close()
    assert not found, found


def test_the_fund_chain_is_written_inline_and_av_pp_at_reads_it(sec_model):
    """``av_pp`` writes the month before's steps inline, and ``av_pp_at`` reads it (§6.6).

    The fund's chain of calls is one cell a month, the depth test above shows, because
    ``av_pp(t)`` reads ``av_pp(t - 1)`` and computes the month before's growth, tax
    provision, charges and cancellations itself, where ``ULB_UK_S`` reads
    ``av_pp_at(t - 1, "AFT_WD")`` through three timings.  So the two forms must give one
    fund: on every committed point, in every month whose next is in cover, ``av_pp_at(t,
    "AFT_WD")``, computed from that month's own fund, is ``av_pp(t + 1)`` bit for bit, and
    ``"BEF_GROWTH"`` is ``av_pp(t)``.  And ``av_pp``'s precedents in a month after
    ``t_entry()`` are ``av_pp`` of the month before and none of the fund's timings, as
    modelx's dependency graph records them.
    """
    table = sec_model.Data.model_point_table()
    for key, point_id in zip(point_keys(sec_model), table.index):
        p = projection(sec_model, key)
        for t in range(p.t_entry(), p.proj_len()):
            if p.is_active(t + 1):
                assert p.av_pp_at(t, "AFT_WD") == p.av_pp(t + 1), (point_id, t)
            assert p.av_pp_at(t, "BEF_GROWTH") == p.av_pp(t), (point_id, t)
        if p.proj_len() > p.t_entry() + 1:
            t = p.t_entry() + 1
            reads = {(n.obj.name, n.args) for n in p.cells["av_pp"].preds(t)}
            assert ("av_pp", (t - 1,)) in reads, (point_id, reads)
            assert not any(name == "av_pp_at" for name, _ in reads), (point_id, reads)


# ---------------------------------------------------------------------------
# T4 -- the count algebra
#
# BEF_DECR == BEF_NB + pols_new_biz, at every t of every point, is a convention
# (test_new_business_joins_the_count_before_decrements), and is not repeated here.


def test_the_count_rolls_forward_through_new_business_and_decrements(sec_model):
    """The count leaves month t by its deaths, surrenders and last survivors alone.

    On every committed point and at every ``t`` of its frame, the count weighting month
    ``t``, ``pols_if_at(t, BEF_DECR)``, less the count carried into ``t + 1``,
    ``pols_if_at(t + 1, BEF_NB)``, is the three outflows of month ``t``, to 1e-12.  The
    step from the last row to ``t = proj_len()`` is what catches a frame that runs a month
    too long: the survivors would then leave a month late, and the count would carry over.
    And the notes' end-of-month count, ``pols_if_at(t, AFT_DECR)``, is exactly the count
    carried into the next month before its new business, in every month: the two are one
    product in one order.

    ``result_pols()`` sets the same movement out row by row, in :data:`RESULT_POLS`'s
    columns, indexed by ``t`` over the frame: ``pols_if`` at ``t + 1`` is ``pols_if`` less
    the outflows at ``t``, plus the new business of ``t + 1``, and row 0 opens from
    ``pols_if_init()``.
    """
    table = sec_model.Data.model_point_table()
    for key, point_id in zip(point_keys(sec_model), table.index):
        p = projection(sec_model, key)
        bef_nb, bef_decr, aft = (_code(p, c) for c in ("BEF_NB", "BEF_DECR", "AFT_DECR"))
        for t in range(p.proj_len()):
            out = p.pols_death(t) + p.pols_surr(t) + p.pols_maturity(t)
            moved = p.pols_if_at(t, bef_decr) - p.pols_if_at(t + 1, bef_nb)
            assert moved == pytest.approx(out, abs=1e-12), (point_id, t)
            assert p.pols_if_at(t, aft) == p.pols_if_at(t + 1, bef_nb), (point_id, t)
        pols = p.result_pols()
        assert list(pols.columns) == RESULT_POLS, point_id
        assert pols.index.name == "t" and list(pols.index) == list(range(p.proj_len()))
        carried = (pols["pols_if"] - pols[OUTFLOWS].sum(axis=1)).shift(1)
        expected = carried.fillna(p.pols_if_init()) + pols["pols_new_biz"]
        assert ((pols["pols_if"] - expected).abs() <= 1e-12).all(), point_id


def test_result_pols_holds_s_counts_with_the_new_business_beside_them(sec_model, s_model):
    """``result_pols()`` is S's counts, column for column, with ``pols_new_biz`` second (D5).

    ``ULB_UK_S`` has no such report, so each of its columns is held to the S cell of its
    name on every twin, all issued at the valuation date, at offset 0: the count, the
    deaths, the surrenders and the last survivors, to 1e-9 relative at no absolute floor,
    the frames ending together but on S's point 3, which the depletion threshold ends a
    month early, compared over the months before its last.  ``pols_new_biz`` holds the
    count in the issue month and 0 in every other.
    """
    table = sec_model.Data.model_point_table()
    twins = table.index[table["row_kind"] == "twin"].tolist()
    assert twins == sorted(s_model.Data.model_point_table().index)
    for point_id in twins:
        p, s = _point(sec_model, point_id), _point(s_model, point_id)
        pols = p.result_pols()
        assert list(pols.columns) == RESULT_POLS, point_id
        frame = range(p.proj_len() - (1 if p.proj_len() < s.proj_len() else 0))
        for column in ("pols_if", "pols_death", "pols_surr", "pols_maturity"):
            want = [s.cells[column](t) for t in frame]
            assert pols[column].loc[frame.start:frame.stop - 1].tolist() == pytest.approx(
                want, rel=1e-9, abs=0.0), (point_id, column)
        assert list(pols["pols_new_biz"]) == [
            p.policy_count() if t == 0 else 0.0 for t in pols.index], point_id


# What T4 multiplies policy_count by: not a whole number, because a count of policies need
# not be one, so that a flow which read the count as whole policies would not follow it.
COUNT_FACTOR = 2.5


def test_scaling_the_count_scales_every_flow_and_no_per_policy_value(tmp_path):
    """``policy_count`` is a weight: 2.5 times the count, 2.5 times every flow, the same per
    policy.

    The committed table, and a copy with every count multiplied by :data:`COUNT_FACTOR`,
    are each read with :data:`SWITCHED_ON` set before either computes anything: the
    switches that ship off, at the splice's values, so that the surrender rate moves with
    the shock and binds its cap.  On every point ``result_cf``'s flows and the counts of
    ``result_pols`` are 2.5 times the committed table's, element by element, to 1e-12
    relative: a scaled count is a computed float, which may come back from the CSV within
    two ulps (``uk_sec_support``'s module docstring).  ``result_cf``'s ``av_pp`` and every
    column of ``result_uf``, per policy, are the committed table's exactly.  So is every
    other cell of :data:`COUNTED`, at every argument the sweep of the committed table's
    point cached: the count at each timing and the claims of each kind, which no report
    shows, among them, and the two count-weighted residuals, a rounding about 0 on that many
    policies, to the residuals' floor of 1e-9.  And every cell outside :data:`COUNTED` (the
    fund at each timing, the withdrawals since issue, the GMDB, the charges, the rates, both
    clocks, the flags) agrees bit for bit at every argument that sweep cached.  So a flow
    that dropped the count, or read it as whole policies, which a table of counts of 1 hides
    from every comparison with S and a count doubled hides here, fails.  Each counted cell
    but the residuals is nonzero on some point.
    """
    table = _committed()
    base = mx.read_model(_sec_inputs(tmp_path / "base", table), name=_name("counted"))
    scaled = mx.read_model(_sec_inputs(tmp_path / "scaled", table.assign(
        policy_count=COUNT_FACTOR * table["policy_count"])), name=_name("scaled"))
    counted = sorted(COUNTED - {"result_cf", "result_pols"})
    residuals = {"check_pols_roll_fwd_resid", "check_unit_funding_resid"}
    nonzero = set()
    try:
        for model in (base, scaled):
            for ref, value in SWITCHED_ON.items():
                setattr(model.Projection, ref, value)
        for key, scaled_key in zip(point_keys(base), point_keys(scaled)):
            one, many = projection(base, key), projection(scaled, scaled_key)
            sweep(one)
            for report in ("result_cf", "result_pols", "result_uf"):
                b, d = one.cells[report](), many.cells[report]()
                assert d.index.equals(b.index) and list(d.columns) == list(b.columns)
                fixed = [c for c in b.columns
                         if report == "result_uf" or c in PER_POLICY_COLUMNS]
                flows = [c for c in b.columns if c not in fixed]
                want = COUNT_FACTOR * b[flows]
                bad = ((d[flows] - want).abs() > 1e-12 * want.abs()).any()
                assert not bad.any(), (key, report, list(bad[bad].index))
                assert d[fixed].equals(b[fixed]), (key, report)
            for name in counted:
                floor = 1e-9 if name in residuals else 0.0
                for args in _cached_args(one.cells[name]):
                    want = COUNT_FACTOR * one.cells[name](*args)
                    got = many.cells[name](*args)
                    assert abs(got - want) <= floor + 1e-12 * abs(want), (
                        key, name, args, got, want)
                    if want != 0.0 and name not in residuals:
                        nonzero.add(name)
            assert twin_mismatches(one, many, exempt=TWIN_EXEMPT_DEFAULT | COUNTED,
                                   rtol=0.0, atol=0.0) == []
            _release(base, key)
            _release(scaled, scaled_key)
    finally:
        scaled.close()
        base.close()
    want = set(counted) - residuals - {"gmdb_charges"}
    assert want <= nonzero, f"0 on every point: {sorted(want - nonzero)}"


def test_the_roll_forward_closes_on_a_million_policies(tmp_path):
    """``check_pols_roll_fwd`` scales its tolerance with the count, and closes at 1e6.

    A residual is rounding on that many policies, so the check holds it to 1e-10 times
    ``max(policy_count(), 1)``, where its tolerance unscaled would be 1e-10: at the counts
    the other tests use, one policy or less, the two are one.  ``ULB_UK_S`` scales by
    ``pols_if_init()``, which here is 0 on a point issued at the valuation date, the count
    entering as new business.  So every committed point is projected from a copy where each
    counts a million policies: the check closes on each, and on some point the largest
    residual exceeds the unscaled 1e-10, so the scaling is what closes it (USLIB-SEC-PLAN.md
    §5.2, T4, precised at M10).  The fund's and the unit funding's checks are per policy and
    scale with nothing.
    """
    table = _committed()
    model = mx.read_model(_sec_inputs(tmp_path, table.assign(policy_count=1e6)),
                          name=_name("million"))
    worst = 0.0
    try:
        for key, point_id in zip(point_keys(model), table.index):
            p = projection(model, key)
            assert p.policy_count() == 1e6
            assert p.check_pols_roll_fwd() and p.check_av_roll_fwd(), point_id
            worst = max(worst, max(abs(p.check_pols_roll_fwd_resid(t))
                                   for t in range(p.proj_len())))
            _release(model, key)
    finally:
        model.close()
    assert worst > 1e-10, worst


# ---------------------------------------------------------------------------
# T5 -- validation
#
# Each malformed table is the committed one with one fault.  The checks run over the whole
# table as it is read, in Data, and the message names the file it read and the column or
# every point at fault.  A blank cell reads as NaN, and so does a text cell once the checks
# coerce the column to numbers, so each is refused as a count, a duration or a state that
# is not a number.  The repeated point_id holds another policy under the same label, as a
# bad extract would, so that the check must look at the labels and not at whole rows.  The
# point_ids are the committed table's: 1 to 6 the twins of S's points; 7, the anchor cell at
# 30; 8, the adviser charge at 66; 9, the GMDB point at 240; 10, the anchor cell in its last
# month, 352; 11, the GMDB point issued 13 months on.  A {file} in a message is the table's
# filename: every case is read by one model, from a file of its own (the malformed fixture).


def _drop(column):
    return lambda table: table.drop(columns=column)


MALFORMED = [
    ("a negative count", _set("policy_count", [7], -0.1),
     "{file}: policy_count must be a number, zero or more; it is not at point_id [7]"),
    ("a blank count", _set("policy_count", [8], float("nan")),
     "{file}: policy_count must be a number, zero or more; it is not at point_id [8]"),
    ("two bad counts", _set("policy_count", [7, 9], -1.0),
     "{file}: policy_count must be a number, zero or more; it is not at point_id [7, 9]"),
    ("a text count", _set("policy_count", [10], "abc"),
     "{file}: policy_count must be a number, zero or more; it is not at point_id [10]"),
    ("an infinite count", _set("policy_count", [10], float("inf")),
     "{file}: policy_count must be a number, zero or more; it is not at point_id [10]"),
    ("a fractional duration", _set("duration_mth", [8], 66.5),
     "{file}: duration_mth must be a whole number of months; it is not at point_id [8]"),
    ("a blank duration", _set("duration_mth", [11], float("nan")),
     "{file}: duration_mth must be a whole number of months; it is not at point_id [11]"),
    ("a text duration", _set("duration_mth", [10], "x4"),
     "{file}: duration_mth must be a whole number of months; it is not at point_id [10]"),
    # numpy casts a float past int64 to the least int64, a bond issued 2**63 months on,
    # without a word: the table refuses it first.
    ("a duration past int64", _set("duration_mth", [7], 1e19),
     "{file}: duration_mth must be below 2**53 months; it is not at point_id [7]"),
    ("durations of 2**53 months at two points", _set("duration_mth", [7, 9], 2.0 ** 53),
     "{file}: duration_mth must be below 2**53 months; it is not at point_id [7, 9]"),
    ("issued beyond the horizon", _set("duration_mth", [11], -121),
     "{file}: duration_mth must be -120 or more, a bond issued at most 120 months after "
     "the valuation date; it is not at point_id [11]"),
    *[(f"no {column} column", _drop(column), f"{{file}} has no {column} column")
      for column in ("policy_count", "duration_mth", *STATE)],
    ("a repeated point_id",
     lambda t: pd.concat([t, t.loc[[7]].assign(policy_id="ULB-900099")]),
     "{file}: point_id [7] appears more than once"),
    ("a negative fund", _set("av_pp_init", [7], -1.0),
     "{file}: av_pp_init must be a number above 0, the unit fund; it is not at point_id "
     "[7]"),
    ("a fund of 0 in force", _set("av_pp_init", [8], 0.0),
     "{file}: av_pp_init must be a number above 0, the unit fund; it is not at point_id "
     "[8]"),
    ("a fund of 0 at outset", _set("av_pp_init", [1], 0.0),
     "{file}: av_pp_init must be a number above 0, the unit fund; it is not at point_id "
     "[1]"),
    ("a blank fund", _set("av_pp_init", [9], float("nan")),
     "{file}: av_pp_init must be a number above 0, the unit fund; it is not at point_id "
     "[9]"),
    ("a text fund", _set("av_pp_init", [10], "x"),
     "{file}: av_pp_init must be a number above 0, the unit fund; it is not at point_id "
     "[10]"),
    ("an infinite fund", _set("av_pp_init", [7], float("inf")),
     "{file}: av_pp_init must be a number above 0, the unit fund; it is not at point_id "
     "[7]"),
    ("negative withdrawals", _set("wd_cum_pp_init", [7], -1.0),
     "{file}: wd_cum_pp_init must be a number, zero or more; it is not at point_id [7]"),
    ("blank withdrawals", _set("wd_cum_pp_init", [8], float("nan")),
     "{file}: wd_cum_pp_init must be a number, zero or more; it is not at point_id [8]"),
    ("text withdrawals", _set("wd_cum_pp_init", [9], "x"),
     "{file}: wd_cum_pp_init must be a number, zero or more; it is not at point_id [9]"),
    ("infinite withdrawals", _set("wd_cum_pp_init", [10], float("inf")),
     "{file}: wd_cum_pp_init must be a number, zero or more; it is not at point_id [10]"),
    ("withdrawals on new business", _set("wd_cum_pp_init", [1], 100.0),
     "{file}: wd_cum_pp_init must be 0 on a bond not yet in force, duration_mth 0 or "
     "less; it is not at point_id [1]"),
    ("withdrawals on future business", _set("wd_cum_pp_init", [11], 1.0),
     "{file}: wd_cum_pp_init must be 0 on a bond not yet in force, duration_mth 0 or "
     "less; it is not at point_id [11]"),
    ("a blank flag", _set("gmdb_flag", [3], float("nan")),
     "{file}: gmdb_flag must be True or False; it is not at point_id [3]"),
    ("a flag written yes", _set("gmdb_flag", [2], "yes"),
     "{file}: gmdb_flag must be True or False; it is not at point_id [2]"),
    ("a flag written 1", _set("gmdb_flag", [1], 1),
     "{file}: gmdb_flag must be True or False; it is not at point_id [1]"),
    ("an unknown sex", _set("sex", [2], "X"),
     "{file}: sex must be M or F; it is not at point_id [2]"),
    ("a joint bond", _set("lives", [1], "joint"),
     "{file}: lives must be single; it is not at point_id [1]"),
    ("an unknown withdrawal pattern", _set("wd_pattern", [4], "monthly"),
     "{file}: wd_pattern must be none or allowance_5pct or custom; it is not at point_id "
     "[4]"),
    ("a blank issue age", _set("age_at_entry", [1], float("nan")),
     "{file}: age_at_entry must be a finite number; it is not at point_id [1]"),
    ("an infinite issue age", _set("age_at_entry", [2], float("inf")),
     "{file}: age_at_entry must be a finite number; it is not at point_id [2]"),
    ("a text issue age", _set("age_at_entry", [3], "x65"),
     "{file}: age_at_entry must be a finite number; it is not at point_id [3]"),
    ("a negative premium", _set("premium", [1], -1.0),
     "{file}: premium must be a number, zero or more; it is not at point_id [1]"),
    ("a blank premium", _set("premium", [2], float("nan")),
     "{file}: premium must be a number, zero or more; it is not at point_id [2]"),
    ("no segments", _set("n_segments", [1], 0),
     "{file}: n_segments must be a whole number, 1 or more; it is not at point_id [1]"),
    ("half a segment", _set("n_segments", [2], 2.5),
     "{file}: n_segments must be a whole number, 1 or more; it is not at point_id [2]"),
    ("a blank count of segments", _set("n_segments", [3], float("nan")),
     "{file}: n_segments must be a whole number, 1 or more; it is not at point_id [3]"),
    ("an uplift below 1", _set("db_uplift", [5], 0.999),
     "{file}: db_uplift must be a number, 1 or more; it is not at point_id [5]"),
    ("a blank uplift", _set("db_uplift", [1], float("nan")),
     "{file}: db_uplift must be a number, 1 or more; it is not at point_id [1]"),
    ("an AMC past 1", _set("amc_rate", [1], 1.5),
     "{file}: amc_rate must be a number from 0 to 1; it is not at point_id [1]"),
    ("a negative AMC", _set("amc_rate", [2], -0.01),
     "{file}: amc_rate must be a number from 0 to 1; it is not at point_id [2]"),
    ("blank further costs", _set("further_costs_rate", [3], float("nan")),
     "{file}: further_costs_rate must be a number from 0 to 1; it is not at point_id [3]"),
    ("a tax provision past 1", _set("tax_provision_rate", [4], 1.2),
     "{file}: tax_provision_rate must be a number from 0 to 1; it is not at point_id [4]"),
    ("a negative custom withdrawal", _set("wd_rate_custom", [6], -0.01),
     "{file}: wd_rate_custom must be a number, zero or more; it is not at point_id [6]"),
    ("a blank custom withdrawal", _set("wd_rate_custom", [6], float("nan")),
     "{file}: wd_rate_custom must be a number, zero or more; it is not at point_id [6]"),
    ("a negative adviser charge", _set("oac_rate", [3], -0.001),
     "{file}: oac_rate must be a number from 0 to 1; it is not at point_id [3]"),
]


@pytest.fixture(scope="module")
def malformed(tmp_path_factory):
    """One model, and beside it every table of :data:`MALFORMED`, each a file of its own.

    Reading the model costs more than every check it makes, so the cases share one read:
    each case points ``Data.model_point_file`` at its own file, which clears the table, and
    reads it afresh.  Returns ``(model, {case: filename})``.
    """
    root = tmp_path_factory.mktemp("malformed")
    files = {}
    for number, (case, edit, _) in enumerate(MALFORMED):
        files[case] = f"malformed_{number:02d}_sec.csv"
        temp_inputs(root, model_path(SEC), model_points=edit(_committed()),
                    model_point_file=files[case])
    model = mx.read_model(root / SEC, name=_name("malformed"))
    yield model, files
    model.close()


@pytest.mark.parametrize("case, edit, message", MALFORMED, ids=[c[0] for c in MALFORMED])
def test_a_malformed_in_force_row_is_refused_naming_its_point(malformed, case, edit,
                                                               message):
    """``Data.model_point_table()`` refuses the table, naming the fault (D6, T5)."""
    model, files = malformed
    model.Data.model_point_file = files[case]
    _refused(model.Data.model_point_table, message.format(file=files[case]))


def test_the_future_horizon_is_a_reference_that_bounds_future_business(tmp_path):
    """``Data.future_horizon_mth`` refuses a bond issued later than it, and 0 refuses all.

    The committed table's one future point is issued 13 months on.  It reads at the shipped
    120 months and at 13, the shortest horizon that admits it, and is refused at 12, by
    name.  At 0 the model takes no future new business, D4's fallback for a product that
    cannot support it, and the message says so.  A negative horizon is itself refused.
    Setting the Reference clears the table, so each value is read afresh.
    """
    future = _label(_committed(), "future", 4, -13)
    later = (f"{TABLE}: duration_mth must be -12 or more, a bond issued at most 12 months "
             f"after the valuation date; it is not at point_id [{future}]")
    no_future = (f"{TABLE}: duration_mth must be 0 or more: this model takes no future new "
                 f"business; it is not at point_id [{future}]")
    model = mx.read_model(_sec_inputs(tmp_path, _committed()), name=_name("horizon"))
    try:
        assert model.Data.future_horizon_mth == 120
        negative = "future_horizon_mth must be 0 months or more, not -1"
        for horizon, refusal in ((13, None), (12, later), (0, no_future), (-1, negative),
                                 (120, None)):
            model.Data.future_horizon_mth = horizon
            if refusal is None:
                assert len(model.Data.model_point_table()) == len(_committed()), horizon
            else:
                _refused(model.Data.model_point_table, refusal)
    finally:
        model.close()


def _run_sec(script, *args, check=True):
    """Run ``script``, a ``run_sec.py``, with ``args``; its output, checked ASCII.

    With ``check=False`` the finished process is returned instead, whatever its exit code,
    for a test that expects the runner to fail.
    """
    done = subprocess.run([sys.executable, str(script), *args], capture_output=True,
                          timeout=300)
    if not check:
        return done
    assert done.returncode == 0, done.stderr.decode(errors="replace")
    assert done.stdout.isascii(), "run_sec.py printed a non-ASCII character"
    # Windows ends each printed line with "\r\n"; read them as "\n", as a frame's
    # to_string() writes them.
    return done.stdout.decode("ascii").replace("\r\n", "\n")


def test_a_point_past_its_cover_is_refused_by_proj_len(tmp_path):
    """A bond at the limiting age has no frame, and ``proj_len()`` refuses it by name.

    The anchor cell in its last month before exhaustion is moved on to ``duration_mth``
    660, the month it reaches ``omega_age``, 120, at issue age 65.  That is a rule of the
    product, not of the table: it needs the limiting age, a Reference, read where the frame
    is defined, so the table reads, and the point is refused on its first projection,
    rather than projecting nothing.  A loop over the block would meet the point only when it
    reached it, after projecting the points before it, so ``run_sec.py --block``, run beside
    the table, asks every point for its frame first: it fails naming the point, and prints
    nothing before.  And one month earlier, 659, the last month of cover, projects one
    month, its fund carried in.
    """
    moved = _label(_committed(), "derived", 1, 352)
    model = _read_edited(tmp_path, _set("duration_mth", [moved], 660))
    message = (f"point_id {moved}: duration_mth 660 is at or past the end of cover, policy "
               f"month 660, the limiting age 120")
    try:
        assert len(model.Data.model_point_table()) == len(_committed())
        _refused(_point(model, moved).result_cf, message)
    finally:
        model.close()
    runner = tmp_path / "run_sec.py"
    shutil.copy(model_path(SEC).parent / "run_sec.py", runner)
    done = _run_sec(runner, "--block", check=False)
    assert done.returncode != 0 and done.stdout == b""
    assert message in done.stderr.decode(errors="replace")
    model = _read_edited(tmp_path / "last", _set("duration_mth", [moved], 659))
    try:
        df = _point(model, moved).result_cf()
        assert len(df) == 1 and df["av_pp"].iloc[0] == _committed().at[moved, "av_pp_init"]
    finally:
        model.close()


# What the contract does not issue, or the model cannot project, refused by proj_len() as
# a point past its cover is, as (case, the table's edit, the References set, the point, the
# message, and the frame the point projects at the shipped References, or None).  Data
# reads an issue age as ULB_UK_S does, so each reads.  The mortality table rates ages from
# 18, so a bond issued younger is refused, though the product admits issue from 3 months;
# one issued at or past omega_age has no cover.  Each bound is refused just inside it here,
# and accepted at it in the edges test, and each, moved past a committed twin, refuses it,
# which at the shipped bound projects its frame: the Reference is what refuses it.  Point 1
# is the anchor cell, issued at 65 with a 5% withdrawal, whose fund lasts 353 months; point
# 7 the anchor cell in force 30 months.  And each Reference S raises to a power, or reads as
# a multiple of a rate or an amount, that is outside its domain.
NOT_ISSUED = [
    ("an issue age of 17", _set("age_at_entry", [1], 17), {}, 1,
     "point_id 1: the issue age, 17, is below issue_age_min, 18", None),
    ("an issue age below a bound raised to 66", None, {"issue_age_min": 66}, 1,
     "point_id 1: the issue age, 65, is below issue_age_min, 66", 353),
    ("an issue age of 120", _set("age_at_entry", [1], 120), {}, 1,
     "point_id 1: the issue age, 120, is at or past omega_age, 120: the bond has no cover",
     None),
    ("an issue age at a limiting age lowered to 65", None, {"omega_age": 65}, 1,
     "point_id 1: the issue age, 65, is at or past omega_age, 65: the bond has no cover",
     353),
    ("a fund_return below -1", None, {"fund_return": -1.01}, 1,
     "point_id 1: fund_return must be a number, -1 or more, not -1.01", 353),
    ("a fund_return of NaN", None, {"fund_return": math.nan}, 7,
     "point_id 7: fund_return must be a number, -1 or more, not nan", 323),
    ("an inflation_rate below -1", None, {"inflation_rate": -1.5}, 1,
     "point_id 1: inflation_rate must be a number, -1 or more, not -1.5", 353),
    ("a negative mort_be_factor", None, {"mort_be_factor": -0.1}, 1,
     "point_id 1: mort_be_factor must be a number, zero or more, not -0.1", 353),
    ("a mort_be_factor of NaN", None, {"mort_be_factor": math.nan}, 1,
     "point_id 1: mort_be_factor must be a number, zero or more, not nan", 353),
    ("a negative wd_allowance_rate", None, {"wd_allowance_rate": -0.01}, 1,
     "point_id 1: wd_allowance_rate must be a number, zero or more, not -0.01", 353),
    ("a negative allowance_years", None, {"allowance_years": -1}, 1,
     "point_id 1: allowance_years must be a number, zero or more, not -1.0", 353),
    ("a negative depletion_threshold", None, {"depletion_threshold": -0.001}, 1,
     "point_id 1: depletion_threshold must be a number, zero or more, not -0.001", 353),
    ("a depletion_threshold of NaN", None, {"depletion_threshold": math.nan}, 1,
     "point_id 1: depletion_threshold must be a number, zero or more, not nan", 353),
    ("an infinite depletion_threshold", None, {"depletion_threshold": math.inf}, 1,
     "point_id 1: depletion_threshold must be a number, zero or more, not inf", 353),
]


@pytest.mark.parametrize("case, edit, refs, point, message, frame", NOT_ISSUED,
                         ids=[c[0] for c in NOT_ISSUED])
def test_a_point_the_contract_does_not_issue_is_refused_by_proj_len(tmp_path, case, edit,
                                                                    refs, point, message,
                                                                    frame):
    """``proj_len()`` refuses a point outside the contract's bounds or a Reference's
    domain, naming both (§6.6).

    ``ULB_UK_S`` projects a bond from any age its table holds, and so would modelx here, but
    the mortality table rates no age below 18 and the compiled model's caches will be sized
    from the contract: a frame of at most ``omega_age - issue_age_min`` years and the
    horizon.  And under a ``fund_return`` below -1 S's monthly rate has no real value, and
    under a negative factor, rate or count of years a mortality rate, a withdrawal or the
    allowance accrued is negative, every check passing.  So the frame refuses such a point,
    naming it, as it refuses a point past its cover, and every report with it
    (:data:`NOT_ISSUED`): each bound just inside it, and each bound moved past a committed
    point, which projects at the shipped bound, on a model read afresh.  The table reads
    either way.  Every Reference is set on a model just read, before its projection computes
    anything (K7).
    """
    model = _read_edited(tmp_path, edit or (lambda t: t))
    try:
        for ref, value in refs.items():
            setattr(model.Projection, ref, value)
        assert len(model.Data.model_point_table()) == len(_committed())
        _refused(_point(model, point).result_cf, message)
    finally:
        model.close()
    if frame is not None:
        shipped = mx.read_model(model_path(SEC), name=_name("bound"))
        try:
            assert len(_point(shipped, point).result_cf()) == frame
        finally:
            shipped.close()


def _exhausted(point, value):
    """The message ``proj_len()`` gives a bond in force at ``point`` whose fund is
    ``value``, at or below the shipped threshold."""
    return (f"point_id {point}: av_pp_init is {value}, at or below depletion_threshold, "
            f"{THRESHOLD}: a bond in force whose fund is exhausted at the valuation date has "
            f"nothing to project")


# The depletion threshold's rules on a bond's opening fund, as (case, the table's edit, the
# References set, the point, the message where refused or None, and the frame where it
# projects).  The threshold is half a pence, a Reference, so each rule is stated on it,
# never on a stand-in such as a fund above 0, and tested where the two part: a fund of
# exactly the threshold is exhausted, so is part of it and so is a rounding above 0, and the
# least fund past it is not, and projects; with the threshold moved off its shipped value,
# a fund the shipped one projects is refused (USLIB-SEC-PLAN.md §7.7, *Record — M9*).  A
# bond not yet in force holds its fund at outset, which at or below the threshold has
# nothing to project either.  Point 7 is the anchor cell in force 30 months; 11, the GMDB
# point issued 13 months on.  A fund past the threshold that the next month's withdrawal
# draws to nothing projects that month alone.
PAST_THE_THRESHOLD = math.nextafter(THRESHOLD, 1.0)
EXHAUSTED = [
    ("a fund of exactly the threshold", _set("av_pp_init", [7], THRESHOLD), {}, 7,
     _exhausted(7, THRESHOLD), None),
    ("a fund of part of the threshold", _set("av_pp_init", [7], 0.003), {}, 7,
     _exhausted(7, 0.003), None),
    ("a fund of a rounding above 0", _set("av_pp_init", [7], 3.4e-15), {}, 7,
     _exhausted(7, 3.4e-15), None),
    ("a fund just past the threshold", _set("av_pp_init", [7], PAST_THE_THRESHOLD), {}, 7,
     None, 1),
    ("a fund of 0.006", _set("av_pp_init", [7], 0.006), {}, 7, None, 1),
    ("a fund of 0.006 under a threshold raised to 0.01", _set("av_pp_init", [7], 0.006),
     {"depletion_threshold": 0.01}, 7,
     "point_id 7: av_pp_init is 0.006, at or below depletion_threshold, 0.01: a bond in "
     "force whose fund is exhausted at the valuation date has nothing to project", None),
    ("a fund at outset of the threshold", _set("av_pp_init", [11], THRESHOLD), {}, 11,
     f"point_id 11: av_pp_init, the fund at outset, is {THRESHOLD}, at or below "
     f"depletion_threshold, {THRESHOLD}: the bond holds nothing to project from its issue "
     f"month", None),
]


@pytest.mark.parametrize("case, edit, refs, point, message, frame", EXHAUSTED,
                         ids=[c[0] for c in EXHAUSTED])
def test_a_fund_at_or_below_the_threshold_is_exhausted(tmp_path, case, edit, refs, point,
                                                       message, frame):
    """``proj_len()`` refuses a bond whose fund is at or below ``depletion_threshold``.

    ``Data`` reads the table, since the rule is the product's: the threshold is a Reference
    of the projection, which ``Data`` cannot see, so the frame refuses the point, naming it,
    as it refuses a point past its cover (:data:`EXHAUSTED`).  A bond in force whose fund is
    exhausted has nothing left to project, and ``ULB_UK_S`` would project a month on a fund
    above 0 that the threshold reads as exhausted.  The least fund past the threshold
    projects, and is drawn to nothing in its first month.  Every Reference is set on a model
    just read (K7).
    """
    model = _read_edited(tmp_path, edit)
    try:
        for ref, value in refs.items():
            setattr(model.Projection, ref, value)
        model.Data.model_point_table()
        p = _point(model, point)
        if message is not None:
            _refused(p.result_cf, message)
        else:
            assert len(p.result_cf()) == frame
            assert p.av_pp(0) == p.av_pp_init() > p.depletion_threshold
            assert p.av_pp_at(0, "AFT_WD") <= p.depletion_threshold
    finally:
        model.close()


# A surrender rate S lets leave 0 to 1, as (case, the References set, the month it first
# leaves, on the anchor cell's twin).  The table's rates are probabilities, which Data holds
# to 0 to 1, but the multipliers and the cap are References: a cap raised past 1, with the
# performance multiplier past it, takes the rate past 1 at the ultimate band, where S's
# monthly rate is complex; a negative multiple takes it below 0 from the first month.
SURRENDER_OUT = [
    ("past 1", {"surr_rate_cap": 2.0, "perf_factor_cap": 20.0, "return_shock": -5.0}, 120,
     "point_id 1: the surrender rate surr_rate(120) is 1.1, outside 0 to 1, under "
     "surr_rate_cap 2.0, perf_factor_cap 20.0, perf_factor_slope 2.0, return_shock -5.0 and "
     "allow_step 1.5"),
    ("below 0", {"perf_factor_cap": -1.0}, 0,
     "point_id 1: the surrender rate surr_rate(0) is -0.02, outside 0 to 1, under "
     "surr_rate_cap 0.35, perf_factor_cap -1.0, perf_factor_slope 2.0, return_shock 0.0 and "
     "allow_step 1.5"),
]


@pytest.mark.parametrize("case, refs, month, message", SURRENDER_OUT,
                         ids=[c[0] for c in SURRENDER_OUT])
def test_a_surrender_rate_outside_0_to_1_is_refused_in_its_month(case, refs, month,
                                                                 message):
    """A surrender rate S lets leave 0 to 1 is refused in its cell, naming the References.

    ``ULB_UK_S``'s rate is ``min(cap, table x multiplier x step)``, the bound S's own,
    which keeps S's order: under References that take it past 1, its monthly rate,
    ``1 - (1 - w)^(1/12)``, is complex, and below 0 its surrenders add policies, every check
    passing.  ``surr_rate`` refuses the rate in the month it first leaves 0 to 1, naming the
    point, the month, the rate and the References that make it (:data:`SURRENDER_OUT`), and
    so does every report that reads it; in the months before it, the rate projects.  The
    References are set on a model just read (K7).
    """
    model = mx.read_model(model_path(SEC), name=_name("surr"))
    try:
        for ref, value in refs.items():
            setattr(model.Projection, ref, value)
        p = _row(model, "twin", 1, 0)
        if month > 0:
            assert 0.0 <= p.surr_rate(month - 1) <= 1.0
        _refused(lambda: p.surr_rate(month), message)
        _refused(p.result_cf, message)
    finally:
        model.close()


def test_the_edges_of_the_in_force_interface_are_accepted(sec_model, tmp_path):
    """A zero count, whole numbers in any type, the horizon and each bound's edge are read.

    A count of 0 is a point that projects zeros; ``30.0`` is a whole number of months, read
    back as the int the policy clock counts in; a bond issued 120 months after the valuation
    date, the shipped ``future_horizon_mth``, is the last one the table admits, with a frame
    of 473 months, 353 from its issue after 120 before it.  A row valued in its first month,
    1, holds a fund and a withdrawal, the state a bond in force holds where one not yet in
    force holds none.  And each bound of the contract at its edge projects: issue at 18,
    the youngest the table rates, and at 119, a year short of the limiting age.
    """
    committed = _committed()
    last = _label(committed, "derived", 1, 352)
    future = _label(committed, "future", 4, -13)
    first = _label(committed, "derived", 1, 30)

    def edit(table):
        table = _set("policy_count", [last], 0.0)(table)
        table = _set("duration_mth", [first], 1)(table)
        table = table.assign(duration_mth=table["duration_mth"].astype(float))
        table = _set("duration_mth", [future], -120.0)(table)
        table = _set("age_at_entry", [1], 18)(table)
        return _set("age_at_entry", [2], 119)(table)

    model = _read_edited(tmp_path, edit)
    try:
        read = model.Data.model_point_table()
        assert read["duration_mth"].dtype == float
        df = _point(model, last).result_cf()
        assert len(df) == 1 and (df.drop(columns="av_pp") == 0.0).all().all()
        p = _point(model, _label(committed, "derived", 3, 66))
        assert p.duration_mth(0) == 66 and type(p.duration_mth(0)) is int
        assert frame_mismatches(
            _point(sec_model, _label(committed, "derived", 3, 66)).result_cf(),
            p.result_cf(), rtol=0, atol=0) == []
        late = _point(model, future)
        assert (late.t_entry(), late.proj_len(), late.pols_new_biz(120)) == (120, 473, 1.0)
        one = _point(model, first)
        assert (one.duration_mth_init(), one.av_pp_init() > 0.0,
                one.wd_cum_pp_init() > 0.0) == (1, True, True)
        assert len(_point(model, 1).result_cf()) == 353
        assert len(_point(model, 2).result_cf()) == 12
        for point in (1, 2):
            assert _point(model, point).check_pols_roll_fwd(), point
    finally:
        model.close()


# proj_len()'s refusal of a bond in force whose fund is exhausted, at any fund: the fund the
# generator computed, written to the CSV, may read back an ulp or two off it.
EXHAUSTED_REFUSAL = re.compile(
    r"ValueError: point_id \d+: av_pp_init is \S+, at or below depletion_threshold, "
    + re.escape(f"{THRESHOLD}: a bond in force whose fund is exhausted at the valuation date "
                "has nothing to project"))


def _every_state_months(end):
    """The S months a point whose S frame runs to ``end`` is restated at.

    By default the edges of its windows (USLIB-SEC-PLAN.md §5.2, T5): every month of the
    first policy year and the first anniversary, each anniversary and the month before it,
    through which the surrender bands, the allowance and the step turn, and the last two
    months of the frame, about the fund's exhaustion.  With ``UKLIB_SEC_FULL=1``, every
    month.  Each after 0, the twin's month.
    """
    if SEC_FULL:
        return list(range(1, end))
    months = {*range(1, 14), end - 2, end - 1,
              *(m for a in range(12, end, 12) for m in (a - 1, a))}
    return sorted(m for m in months if 0 < m < end)


def _states(s):
    """Each ``(S point, month)`` of :func:`_every_state_months` on every point of ``s``."""
    labels = s.Data.model_point_table().index
    return [(point_id, d) for key, point_id in zip(point_keys(s), labels)
            for d in _every_state_months(projection(s, key).proj_len())]


def _restated(root, s, states):
    """The twins of ``s``'s points and a row in force at each of ``states``, ``(S point,
    month)``, built by the generator out of ``s`` into a copy of the product directory:
    ``(folder, table)``."""
    spec = dataclasses.replace(SPEC, derived=tuple(states), future=())
    table, _ = build_sec_table(spec, s)
    return _sec_inputs(root, table), table


def _refused_in_force(folder, refs):
    """What ``Data`` and ``proj_len()`` refuse of the table in ``folder``, read with
    ``refs`` set first: ``Data``'s refusal, or each row's ``proj_len()``'s, by its label,
    each by the line that names it.  Each row is released once asked (:func:`_release`)."""
    model = mx.read_model(folder, name=_name("every"))
    try:
        for ref, value in refs.items():
            setattr(model.Projection, ref, value)
        try:
            table = model.Data.model_point_table()
        except Exception as err:                # reported, with the rows' states
            return {"Data": _raised(err)}
        refused = {}
        for key, label in zip(point_keys(model), table.index):
            try:
                projection(model, key).proj_len()
            except Exception as err:            # reported, so every row is asked
                refused[label] = _raised(err)
            _release(model, key)
        return refused
    finally:
        model.close()


def test_every_state_s_reaches_is_accepted_in_force(s_model, spliced, tmp_path):
    """Every state ``ULB_UK_S`` reaches is a valid opening state, but an exhausted fund (T5).

    ``Data``'s rules and ``proj_len()``'s hold an opening state to what a bond in force can
    be, so they must accept each state the S model reaches: a rule exercised only on the
    rows the other tests choose could refuse a state S reaches elsewhere (D6).  So each point
    of S is restated in force by the generator at the edges of its windows, or with
    ``UKLIB_SEC_FULL=1`` at every month of its frame (:func:`_every_state_months`), into one
    table beside the twins: ``Data`` reads it, and no row's ``proj_len()`` refuses it
    (USLIB-SEC-PLAN.md §5.2, T5, precised at M10), but the states the product refuses by
    name, set aside and shown refused: a fund that opens above 0 and at or below
    ``depletion_threshold``, the rounding ``ULB_UK_S`` runs on past the threshold, which it
    reaches on its point 3 at month 323 and on the splice's variant 9 at the same month.

    The splice's switches move one of the states S reaches, the count, through the
    surrender rate: the fund and the withdrawals since issue are per policy and read no
    count, so its variants are what move them, the GMDB charged, the 7.5% cap binding and
    the rider beside the adviser charge.  So the test runs on each set of inputs on which
    those states differ (precised at M9), and asserts which states each moves:

    * S as shipped, its six points under its own References, the switches off, as T1 and the
      committed rows read it (``s_model``);
    * the splice's, its points and three variants under :data:`SPLICED_REFS`, the switches
      on (``spliced``).

    The cap's References, a ``mort_be_factor`` that caps mortality at 1, move only the
    count, to 0 once the cap binds, which ``Data`` reads as it reads every count, so that set
    is not run: the cap's test reads its rows in force.
    """
    sets = {"shipped": (s_model, {}), "spliced": (spliced[0], SPLICED_REFS)}
    found, states, set_aside = {}, {}, {}
    for tag, (s, refs) in sets.items():
        reached = _states(s)
        folder, rows = _restated(tmp_path / tag, s, reached)
        assert len(rows) == len(s.Data.model_point_table()) + len(reached)
        states[tag] = rows.set_index(["source_policy_id", "source_mth"])
        refused = _refused_in_force(folder, refs)
        exhausted = rows.index[(rows["duration_mth"] > 0)
                               & (rows["av_pp_init"] <= THRESHOLD)].tolist()
        set_aside[tag] = sorted((rows.at[label, "source_policy_id"],
                                 int(rows.at[label, "source_mth"])) for label in exhausted)
        for label in exhausted:
            point = int(rows.at[label, "point_id"])
            if not EXHAUSTED_REFUSAL.fullmatch(refused.pop(point, "")):
                found.setdefault(tag, []).append(f"{point} not refused as exhausted")
        if refused:
            found.setdefault(tag, []).append(
                f"{len(refused)} refused, first: {list(refused.items())[:5]}")
    assert not found, found
    assert set_aside["shipped"] == [("ULB-000003", 323)], set_aside
    assert set_aside["spliced"] == [("ULB-000003", 323), ("ULB-900009", 323)], set_aside
    shipped, splice = states["shipped"], states["spliced"]
    both = shipped.index.intersection(splice.index)
    apart = {c for c in ("policy_count", *STATE)
             if (shipped.loc[both, c] != splice.loc[both, c]).any()}
    assert apart == {"policy_count"}, apart


# ---------------------------------------------------------------------------
# The assumption tables
#
# Data checks each table before a value of it is read, in the cell the projection takes the
# table's extent from (UKLIB-SEC-PLAN.md §4; USLIB-SEC-PLAN.md §7.1, *Precised at M3*,
# item 9).  Each case is the shipped tables with one fault, read from a copy, refused by its
# Data cell alone, naming the file, the column and the rows at fault, and through a
# projection of the anchor cell, which reads both tables.  The surrender table's refusals
# name its lines, the header line 1: policy years 1 to 11 on lines 2 to 12.  The mortality
# table's name its keys, sex and age: ULB_UK_S's reader sorts the table as it reads it, so
# its lines are lost with the order.


def _written(column, value, where):
    """An edit of a table that writes ``value`` into ``column`` on the rows ``where``
    picks."""
    def edit(table):
        cells = table[column].astype(object)
        cells[where(table)] = value
        return table.assign(**{column: cells})
    return edit


def _mort(sex, age):
    return lambda t: (t["sex"] == sex) & (t["age"] == age)


def _key_is(column, value):
    return lambda t: t[column] == value


def _dropped(where):
    return lambda table: table[~where(table)].reset_index(drop=True)


def _repeated(where):
    return lambda table: pd.concat([table, table[where(table)]], ignore_index=True)


MORT, SURR = "mort_table.csv", "surr_table.csv"
RATE = f"{MORT}: mort_rate must be a number from 0 to 1; it is not at (sex, age) "
SURR_RATE = f"{SURR}: surr_rate must be a number from 0 to 1; it is not on line "


def _ages_apart(*faults):
    """The message of a mortality table whose sexes do not run one row an age, naming
    ``faults``: each repeat with how often it appears, each span a sex lacks."""
    return (f"{MORT}: the ages of each sex must run from 18 to 120, the table's first and "
            f"last, one row an age, none below 0; " + "; ".join(faults))


YEARS = (f"{SURR}: the policy years must run from 1, one row a year, without a gap or a "
         f"repeat; ")


# A table a reader cannot read, or whose value is not a number in its range, as (case, the
# file, its edit, the Data cell that refuses it, its message).  A value no point reads is
# refused too: the female rate at 18, which no point reaches, and the male at 120, which no
# frame does.
UNREADABLE = [
    ("a blank mortality rate", MORT, _written("mort_rate", float("nan"), _mort("M", 70)),
     "mort_age_first", RATE + "[('M', 70)]"),
    ("a text mortality rate", MORT, _written("mort_rate", "low", _mort("M", 66)),
     "mort_age_first", RATE + "[('M', 66)]"),
    ("an infinite mortality rate", MORT, _written("mort_rate", float("inf"),
                                                  _mort("M", 120)),
     "mort_age_first", RATE + "[('M', 120)]"),
    ("a negative mortality rate", MORT, _written("mort_rate", -0.001, _mort("F", 18)),
     "mort_age_first", RATE + "[('F', 18)]"),
    ("a mortality rate past 1", MORT, _written("mort_rate", 1.5, _mort("M", 80)),
     "mort_age_first", RATE + "[('M', 80)]"),
    ("two rows at fault", MORT, _then(_written("mort_rate", float("nan"), _mort("M", 18)),
                                      _written("mort_rate", float("nan"), _mort("F", 90))),
     "mort_age_first", RATE + "[('F', 90), ('M', 18)]"),
    ("an age not whole", MORT, _written("age", 65.5, _mort("M", 65)),
     "mort_age_first",
     f"{MORT}: age must be a whole number; it is not at (sex, age) [('M', 65.5)]"),
    ("an age written as text", MORT, _written("age", "x", _mort("F", 18)),
     "mort_age_first",
     f"{MORT}: age must be a whole number; it is not at (sex, age) [('F', 'x')]"),
    ("an unknown sex", MORT, _written("sex", "X", _mort("F", 18)),
     "mort_age_first", f"{MORT}: sex must be M or F; it is not at (sex, age) [('X', 18)]"),
    ("an age missing", MORT, _dropped(_mort("M", 70)), "mort_age_first",
     _ages_apart("no row holds sex M, age 70")),
    ("an age twice", MORT, _repeated(_mort("F", 40)), "mort_age_first",
     _ages_apart("sex F, age 40 appears 2 times")),
    ("a sex missing", MORT, _dropped(lambda t: t["sex"] == "F"), "mort_age_first",
     _ages_apart("no row holds sex F, ages 18 to 120")),
    ("a sex shorter", MORT, _dropped(_mort("F", 120)), "mort_age_first",
     _ages_apart("no row holds sex F, age 120")),
    ("a blank surrender rate", SURR, _written("surr_rate", float("nan"),
                                              _key_is("policy_year", 3)),
     "surr_last_year", SURR_RATE + "[4]"),
    ("a surrender rate past 1", SURR, _written("surr_rate", 1.5, _key_is("policy_year", 11)),
     "surr_last_year", SURR_RATE + "[12]"),
    ("a negative surrender rate", SURR, _written("surr_rate", -0.1,
                                                 _key_is("policy_year", 1)),
     "surr_last_year", SURR_RATE + "[2]"),
    ("a text surrender rate", SURR, _written("surr_rate", "high", _key_is("policy_year", 2)),
     "surr_last_year", SURR_RATE + "[3]"),
    ("a policy year not whole", SURR, _written("policy_year", 2.5,
                                               _key_is("policy_year", 2)),
     "surr_last_year",
     f"{SURR}: policy_year must be a whole number; it is not on line [3]"),
    ("a policy year missing", SURR, _dropped(_key_is("policy_year", 3)), "surr_last_year",
     YEARS + "no line holds policy_year 3"),
    ("a policy year twice", SURR, _repeated(_key_is("policy_year", 4)), "surr_last_year",
     YEARS + "policy_year 4 repeats on lines [5, 13]"),
    ("no policy year 1", SURR, _dropped(_key_is("policy_year", 1)), "surr_last_year",
     YEARS + "no line holds policy_year 1"),
]


@pytest.mark.parametrize("case, file, edit, cell, message", UNREADABLE,
                         ids=[c[0] for c in UNREADABLE])
def test_a_table_a_reader_cannot_read_is_refused_naming_its_rows(tmp_path, case, file, edit,
                                                                 cell, message):
    """``Data`` refuses an assumption table before a value of it is read (§4, T5).

    ``ULB_UK_S`` reads a blank rate as NaN, which its cap would keep and every flow carry;
    an infinite one, which the cap reads as certain death; a key that is not whole, gapped
    or repeated, as a ``KeyError`` only where a projection reaches it, or as a wrong row.
    Here the extent cell the projection asks first refuses each, naming the file, the
    column and the rows at fault (:data:`UNREADABLE`), and so does a projection of the
    anchor cell, which reads both tables.
    """
    model = _read_edited(tmp_path, lambda t: t, edits={file: edit})
    try:
        _refused(model.Data.cells[cell], message)
        _refused(_point(model, 1).result_cf, message)
    finally:
        model.close()


def test_a_read_beyond_the_mortality_table_is_refused_naming_its_point(tmp_path):
    """A read past the mortality table's ages is refused by the one cell that reads it.

    ``ULB_UK_S``'s lookup raises ``KeyError`` beyond the table, naming no point.  Here the
    mortality rate's read at an attained age outside the table, above or below it, raises
    ``ValueError`` naming the point and the age: a table cut to ages 20 to 100, so that the
    anchor cell, issued at 65, is refused where it reaches 101, and the custom point, issued
    at 55, the same.  And under a limiting age raised to 122, past the table's last age, a
    point is refused where its age reaches 121.  The surrender table takes its last year for
    every later one, as ``ULB_UK_S`` does, so no read is beyond it.
    """
    cut = {MORT: _dropped(lambda t: (t["age"] > 100) | (t["age"] < 20))}
    model = _read_edited(tmp_path, lambda t: t, edits=cut)
    try:
        _refused(_point(model, 2).result_cf,
                 "point_id 2: mort_table.csv has no rate at attained age 101")
        _refused(_point(model, 6).result_cf,
                 "point_id 6: mort_table.csv has no rate at attained age 101")
    finally:
        model.close()
    model = _read_edited(tmp_path / "omega", lambda t: t)
    try:
        model.Projection.omega_age = 122
        _refused(_point(model, 2).result_cf,
                 "point_id 2: mort_table.csv has no rate at attained age 121")
        assert len(_point(model, 1).result_cf()) == 353
    finally:
        model.close()


def test_a_key_written_as_a_float_reads_as_ulb_uk_s_reads_it(sec_model, tmp_path):
    """A key written ``35.0`` is the key 35, in every table and in every extent.

    ``ULB_UK_S``'s lookups match a float key to the int the projection asks, so a table
    written by a tool that writes every number with a decimal point reads the same.  Each
    assumption table's keys and the model point table's ``duration_mth`` are written as
    floats, and every committed point projects what the committed tables project, exactly.
    """
    def as_float(column):
        return lambda table: table.assign(**{column: table[column].astype(float)})

    edits = {MORT: as_float("age"), SURR: as_float("policy_year")}
    model = _read_edited(tmp_path, as_float("duration_mth"), edits=edits)
    try:
        for point_id in _committed().index:
            for report in ("result_cf", "result_uf", "result_pols"):
                assert frame_mismatches(_point(sec_model, point_id).cells[report](),
                                        _point(model, point_id).cells[report](),
                                        rtol=0, atol=0) == [], (point_id, report)
    finally:
        model.close()


# ---------------------------------------------------------------------------
# T6 -- regeneration


def test_the_committed_sec_inputs_are_what_s_generates(s_model):
    """``model_point_table_sec.csv`` is what ULB_UK_S and its table generate today.

    Every row and column, the text cells and the two opening-state columns included: an
    edit to an S row the table copies or derives from, or to an S formula a row's state is
    read from, fails here until ``python tools/gen_sec_points.py ULB_UK_SEC`` regenerates
    it, in the same commit.  Text and integers compare exactly, and a float by its value, to
    1e-12, because the text the writer picks for a computed float depends on the platform's
    parser (§5).
    """
    assert check_generated(SEC, s_model=s_model) == []


# ---------------------------------------------------------------------------
# The product's own facts


def test_the_two_clocks_on_the_shipped_points(sec_model):
    """``t`` counts from the valuation date; ``duration_mth(t)`` from issue (D3, D4).

    On a twin of S's new business the two coincide, and its policies enter as new business
    at ``t = 0``.  The anchor cell in force 30 months is in policy year 3 at attained age 67
    at ``t = 0``, steps into policy year 4 at ``t = 6``, and has 323 months of its frame
    left, its fund exhausted at policy month 353 as from issue.  The GMDB point at 240 is in
    policy year 21, past the allowance's twenty years, its guarantee run out.  The point
    issued 13 months on has nothing in force and nothing to do before ``t = 13``, and a
    frame of 366 months.  The anchor cell in its last month before exhaustion has a one-month
    frame, in which its survivors leave.  A timing the model does not know is refused rather
    than answered with another count.
    """
    twin = _row(sec_model, "twin", 1, 0)
    assert [twin.duration_mth(t) for t in (0, 1, 352)] == [0, 1, 352]
    assert (twin.t_entry(), twin.pols_if_init(), twin.pols_new_biz(0), twin.pols_if(0)) == (
        0, 0.0, 1.0, 1.0)
    assert (twin.horizon_mths(), twin.fund_exhaust_mth(), twin.proj_len()) == (660, 353, 353)
    old = _row(sec_model, "derived", 1, 30)
    assert (old.duration_mth(0), old.duration(0), old.policy_year(0), old.age(0)) == (
        30, 2, 3, 67)
    assert (old.policy_year(5), old.policy_year(6)) == (3, 4)
    assert (old.proj_len(), old.fund_exhaust_mth(), old.t_entry(), old.pols_new_biz(0)) == (
        323, 353, 0, 0.0)
    assert old.pols_if(0) == old.pols_if_init() == old.policy_count()
    gmdb = _row(sec_model, "derived", 4, 240)
    assert (gmdb.policy_year(0), gmdb.allow_factor(0), gmdb.gmdb_guarantee_pp(0)) == (
        21, 1.5, 0.0)
    fut = _row(sec_model, "future", 4, -13)
    assert (fut.duration_mth(0), fut.t_entry(), fut.proj_len()) == (-13, 13, 366)
    assert not fut.is_active(12) and fut.is_active(13)
    assert (fut.pols_if_init(), fut.pols_new_biz(13), fut.pols_if(13)) == (0.0, 1.0, 1.0)
    assert (fut.av_pp(12), fut.av_pp(13), fut.gmdb_guarantee_pp(13)) == (
        0.0, 100000.0, 100000.0)
    last = _row(sec_model, "derived", 1, 352)
    assert (last.proj_len(), last.age(0), last.policy_year(0)) == (1, 94, 30)
    assert last.pols_maturity(0) > 0.0 and last.pols_if_at(1, _code(last, "BEF_NB")) == 0.0
    _refused(lambda: old.pols_if_at(0, "BEF_NOTHING"), "invalid timing")
    _refused(lambda: old.av_pp_at(0, "AFT_NOTHING"), "invalid timing")


def test_the_committed_rows_continue_their_s_points(sec_model, s_model):
    """Each committed row in force, or issued later, is its S point from its month on.

    T6 compares a float to 1e-12, which pins a small count only to that much of itself, so
    each committed row is compared with its S point frame by frame and cell by cell, at the
    shipped assumptions (USLIB-SEC-PLAN.md §7.1, *Precised at M3*, item 11): the four
    derived rows from their months, and the row issued 13 months on from S's issue month,
    all to 1e-9 relative with no absolute floor but on the residuals and in an exhausted
    frame's last month, every cell but those expense inflation moves (:func:`_continues_s`),
    which the inflation test holds.  The adviser charge's row at 66 ends a month before S's
    point does, where the depletion threshold drops S's month on a rounding.
    """
    table = sec_model.Data.model_point_table()
    found = []
    for point_id in table.index:
        kind, month = table.at[point_id, "row_kind"], int(table.at[point_id, "source_mth"])
        if kind == "twin":
            continue
        policy = table.at[point_id, "source_policy_id"]
        s_point = int(s_model.Data.model_point_table().index[
            s_model.Data.model_point_table()["policy_id"] == policy][0])
        found += [f"point {point_id}: {line}" for line in _continues_s(
            _point(s_model, s_point), _point(sec_model, point_id), month)]
    assert not found, found[:20]


def test_the_depletion_threshold_moves_point_3_alone(sec_model, s_model):
    """The threshold's effect on each S point: one month of point 3's, on 3.4e-15 (§6.6).

    ``ULB_UK_S`` ends a frame at the first month whose fund opens on 0 or less; this model
    at the first that opens at or below ``depletion_threshold``, half a pence.  Where the
    withdrawal cap draws a fund to nothing, the month closes it on a subtraction whose
    exact value is 0: on 0 exactly where nothing is cancelled beside the withdrawal, as on
    S's points 1, 4 and 5, but on a rounding of either sign where an adviser or a rider
    charge is, floored at 0.  S's point 3, its adviser charge beside its withdrawal, closes
    its fund on 3.4e-15 at the end of month 322, which S projects a month more: 0.019
    policies, a maintenance charge of about 18 pence against an AMC of 6e-20, and its
    survivors maturing a month later.  Points 2 and 6 never exhaust their funds, and run to
    the limiting age.

    So on every twin the frames, as ``FRAME`` and ``S_FRAME`` hold them, end together but
    on point 3, which ends a month early; there every cell agrees with S's in every month
    before its last, every cell of its last month but where its survivors go, which leave
    here and carry on in S, S's month 323 opens on a fund above 0 and at or below the
    threshold, and the departure moves the frame's net cash flow by S's last month alone.
    """
    table = sec_model.Data.model_point_table()
    twins = table.index[table["row_kind"] == "twin"].tolist()
    frames = {}
    for point_id in twins:
        p, s = _point(sec_model, point_id), _point(s_model, point_id)
        frames[point_id] = (p.proj_len(), s.proj_len())
        if p.proj_len() == s.proj_len():
            continue
        assert _compare(s, p, 0, TWIN_EXEMPT_DEFAULT | SPEC.exempt | {"proj_len"}) == []
        last = p.proj_len()
        assert s.av_pp(last) == 3.3861802251067274e-15, point_id
        moved = s.result_cf()["net_cf"].sum() - p.result_cf()["net_cf"].sum()
        assert moved == pytest.approx(s.net_cf(last), rel=1e-9, abs=0.0)
        assert -0.2 < s.net_cf(last) < -0.15
    assert frames == {p: (FRAME[p], S_FRAME[p]) for p in twins}, frames
    assert [p for p, (mine, theirs) in frames.items() if mine != theirs] == [3]


def test_a_fund_that_reaches_the_threshold_exactly_is_exhausted_there(tmp_path):
    """The search for the fund's exhaustion reads the threshold as exhausted, at or below.

    The anchor cell's fund opens month 352 on 326.68, the last month before the withdrawal
    cap draws it to 0.  With ``depletion_threshold`` set to exactly that fund, the search
    finds it exhausted at month 352, and the frame is 352 months; set to the float below it,
    the frame is the shipped 353.  A test of ``<`` where ``<=`` is meant moves the first by a
    month, which no shipped fund, a rounding of 1e-15 or a fund of hundreds, shows.
    """
    shipped = mx.read_model(model_path(SEC), name=_name("exact"))
    try:
        fund = _row(shipped, "twin", 1, 0).av_pp(352)
    finally:
        shipped.close()
    for threshold, frame in ((fund, 352), (math.nextafter(fund, 0.0), 353)):
        model = mx.read_model(model_path(SEC), name=_name("exact"))
        try:
            model.Projection.depletion_threshold = threshold
            p = _row(model, "twin", 1, 0)
            assert (p.fund_exhaust_mth(), p.proj_len()) == (frame, frame), threshold
            assert p.check_pols_roll_fwd() and p.pols_maturity(frame - 1) > 0.0
        finally:
            model.close()


def test_the_unit_fund_is_read_from_the_model_point(sec_model, tmp_path):
    """The fund a bond in force holds is the point's, not recomputed (UKLIB-SEC-PLAN.md K14).

    ``ULB_UK_S`` rebuilds the fund from the premium at its References, so a model that
    dropped ``av_pp_init`` and did the same would pass the splice, since S and the splice
    recompute it alike.  So the anchor cell in force 30 months is projected with a fund no
    fund return gives, 60% of what S carries there, as though the market had fallen a third
    since issue: the fund at ``t = 0`` is the column; each month after is the month before
    grown, charged and drawn down at the References, ``av_pp(t + 1) = max(0, UF'(t) - W(t))``
    from it; the AMC is levied on it; the withdrawals since issue and the allowance are the
    committed row's in every month but the last, where the smaller fund can no longer pay
    the withdrawal: the fund pays them, and does not set them; and the fund is exhausted,
    and the frame ends, years before the committed row's.  The fund is rounded to pence,
    so that the CSV holds it exactly.
    """
    row = _label(_committed(), "derived", 1, 30)
    fund = round(0.6 * _committed().at[row, "av_pp_init"], 2)
    model = _read_edited(tmp_path, _set("av_pp_init", [row], fund))
    try:
        p, base = _point(model, row), _point(sec_model, row)
        assert p.av_pp(0) == fund
        for t in (0, 1, 11, 100):
            grown = p.av_pp(t) * (1 + p.fund_return_mth() * (1 - p.tax_provision_rate()))
            charged = grown * (1 - p.amc_rate_mth() - p.further_costs_rate_mth())
            assert p.av_pp(t + 1) == pytest.approx(max(0.0, charged - p.wd_pp(t)),
                                                   rel=1e-12), t
            assert p.amc_pp(t) == pytest.approx(p.amc_rate_mth() * grown, rel=1e-12), t
        last = p.proj_len() - 1
        for t in range(last):
            assert p.wd_cum_pp(t) == base.wd_cum_pp(t), t
            assert p.allowance_cum_pp(t) == base.allowance_cum_pp(t), t
        assert p.wd_pp(last) < base.wd_pp(last) and p.av_pp_at(last, "AFT_WD") == 0.0
        assert p.proj_len() < base.proj_len() - 100
        assert p.fund_exhaust_mth() == p.proj_len() + 30
    finally:
        model.close()


def test_the_withdrawals_since_issue_are_read_from_the_model_point(sec_model, tmp_path):
    """What a bond has withdrawn since issue is the point's, not its pattern's (K14; D6).

    ``ULB_UK_S`` rebuilds the withdrawals from the premium and its pattern, so a model that
    dropped ``wd_cum_pp_init`` and did the same would pass the splice, which rebuilds them
    alike; and the GMDB opens from them, ``max(0, P - wd_cum_pp_init)``.  So the GMDB point
    at 240, whose pattern has drawn the whole premium and whose guarantee is 0, is projected
    as though it had withdrawn only half of it, history no pattern of its gives: its
    guarantee opens at 50,000, above its fund's 41,263 uplifted, so the rider charges in the
    first month, the death benefit is the guarantee, and the guarantee runs down from 50,000
    by each later withdrawal.  And the adviser-charge point at 66, written with 10,000 more
    withdrawn, as though one withdrawal had been taken beside its pattern, carries 10,000
    more withdrawn in every month of its frame, and an excess gain of what that leaves above
    the allowance, which the committed row has none of in some months, while its fund and
    its frame are the committed row's: the withdrawals since issue move the tax machinery,
    not the units.
    """
    gmdb = _label(_committed(), "derived", 4, 240)
    adviser = _label(_committed(), "derived", 3, 66)
    more = _committed().at[adviser, "wd_cum_pp_init"] + 10000.0
    model = _read_edited(tmp_path, _then(_set("wd_cum_pp_init", [gmdb], 50000.0),
                                         _set("wd_cum_pp_init", [adviser], more)))
    try:
        g, base = _point(model, gmdb), _point(sec_model, gmdb)
        assert (base.gmdb_guarantee_pp(0), g.gmdb_guarantee_pp(0)) == (0.0, 50000.0)
        assert g.gmdb_guarantee_pp(0) > g.db_uplift() * g.av_pp_at(0, "AFT_CHARGE")
        assert g.gmdb_charge_pp(0) > 0.0 and base.gmdb_charge_pp(0) == 0.0
        assert g.claims(0, _code(g, "DEATH")) == pytest.approx(
            50000.0 * g.pols_death(0), rel=1e-12)
        assert g.gmdb_guarantee_pp(1) == pytest.approx(
            50000.0 - g.wd_pp(0) - g.adviser_charge_pp(0), rel=1e-12)
        a, abase = _point(model, adviser), _point(sec_model, adviser)
        assert a.proj_len() == abase.proj_len()
        gained = []
        for t in range(a.proj_len()):
            assert a.av_pp(t) == abase.av_pp(t), t
            assert a.wd_cum_pp(t) == pytest.approx(abase.wd_cum_pp(t) + 10000.0,
                                                   rel=1e-12), t
            assert a.excess_gain_pp(t) == pytest.approx(max(
                0.0, abase.wd_cum_pp(t) + 10000.0 - abase.allowance_cum_pp(t)),
                rel=1e-12, abs=1e-9), t
            if abase.excess_gain_pp(t) == 0.0 < a.excess_gain_pp(t):
                gained.append(t)
        assert gained, "the 10,000 moves no month's excess gain off 0"
    finally:
        model.close()


def test_expense_inflation_runs_on_the_valuation_clock(sec_model, s_model):
    """Maintenance is in valuation-date pounds, for every point alike (D7).

    At the shipped 2.5%, the factor at ``t`` is ``1.025^(t // 12)`` on every point, whatever
    its duration, stepping on the valuation date's anniversaries.  So the anchor cell in
    force 30 months pays S's month-``30 + t`` maintenance with S's factor taken out and this
    model's put in: at ``t = 0`` S's less ``1.025^2``, the inflation S had applied since
    issue, and from ``t = 6``, where S's policy anniversary falls, a further 1.025 less until
    the valuation date's own.  And the point issued 13 months on pays S's maintenance with
    a year or two more of inflation: its factor at ``t`` is ``1.025^(t // 12)``, where S's at
    ``t - 13`` is ``1.025^((t - 13) // 12)``.  Acquisition is not inflated on either.  This is the only
    test that sees inflation run on the policy clock: the splice sets the rate to 0, and on
    a point issued at ``t = 0`` the clocks agree.
    """
    assert sec_model.Projection.inflation_rate == INFLATION
    p, s = _row(sec_model, "derived", 1, 30), _point(s_model, 1)
    fut = _row(sec_model, "future", 4, -13)
    for t in (0, 11, 12, 30):
        assert p.inflation_factor(t) == fut.inflation_factor(t) == (1 + INFLATION) ** (t // 12)
    for t in range(p.proj_len()):
        assert p.expenses(t) == pytest.approx(
            s.expenses(30 + t) / s.inflation_factor(30 + t) * p.inflation_factor(t)
            * p.pols_if(t) / s.pols_if(30 + t), rel=1e-12), t
    assert p.expenses(0) == pytest.approx(s.expenses(30) / (1 + INFLATION) ** 2, rel=1e-12)
    s4 = _point(s_model, 4)
    acq = s4.expense_acq
    for t in range(13, fut.proj_len()):
        issued = acq if t == 13 else 0.0
        maint = (fut.expenses(t) - issued) / fut.pols_if(t)
        want = (s4.expenses(t - 13) - issued) / s4.pols_if(t - 13)
        assert maint == pytest.approx(
            want * (1 + INFLATION) ** (t // 12 - (t - 13) // 12), rel=1e-12), t


def test_acquisition_is_charged_on_new_business_only(sec_model):
    """£300 per policy issued, in the issue month alone, uninflated.

    On every committed point, what ``expenses(t)`` holds beyond its maintenance part is
    ``300 * policy_count()`` in the issue month, ``t = -duration_mth``, and 0 in every other
    month, to 1e-9: the twins of S's new business bear it at ``t = 0``, the point issued 13
    months on at ``t = 13``, and the points already in force never, though on the valuation
    clock their row 0 is ``t = 0``.  ``ULB_UK_S`` charges it at ``t = 0`` on the count in
    force there, which on a point issued at the valuation date is the issued count, so the
    twins agree with S at any count.
    """
    table = sec_model.Data.model_point_table()
    for key, point_id in zip(point_keys(sec_model), table.index):
        p = projection(sec_model, key)
        ts = range(p.proj_len())
        issue = -table.at[point_id, "duration_mth"]
        acq = [p.expenses(t) - p.expense_maint / 12 * p.inflation_factor(t) * p.pols_if(t)
               for t in ts]
        assert acq == pytest.approx([p.expense_acq * p.policy_count() if t == issue
                                     else 0.0 for t in ts], abs=1e-9), point_id
        assert (issue in ts) == (sum(acq) > 0.0), point_id


def test_the_surrender_bands_and_the_step_run_on_the_policy_clock(sec_model):
    """The surrender table, the step and the allowance read the policy year, not ``t``.

    ``ULB_UK_S`` reads them at ``t // 12 + 1``, which is the policy year only on a point
    issued at ``t = 0``.  The anchor cell in force 30 months surrenders at the 5% band, the
    policy years 3 to 5, from ``t = 0`` and at the 8% band from ``t = 30``, policy month 60;
    its allowance accrues to policy year 20, ``t = 210``, and stays there, and the step to
    1.5 starts at ``t = 210``, policy month 240.  The point issued 13 months on reads its
    first band at its issue month, ``t = 13``.
    """
    p = _row(sec_model, "derived", 1, 30)
    assert [p.surr_rate_base(t) for t in (0, 29, 30, 89, 90)] == [0.05, 0.05, 0.08, 0.08,
                                                                 0.10]
    assert (p.allow_factor(209), p.allow_factor(210)) == (1.0, 1.5)
    assert p.allowance_cum_pp(209) == p.allowance_cum_pp(210) == pytest.approx(
        100000.0, rel=1e-12)
    assert p.allowance_cum_pp(0) == pytest.approx(15000.0, rel=1e-12)
    fut = _row(sec_model, "future", 4, -13)
    assert (fut.surr_rate_base(12), fut.surr_rate_base(13), fut.surr_rate_base(25)) == (
        0.0, 0.02, 0.03)


# ---------------------------------------------------------------------------
# The cap on mortality
#
# mort_rate caps the annual rate at 1, the bound second, as ULB_UK_S's does since M0.  At
# the shipped mort_be_factor of 0.8 the rate stays at or below 0.8 to the end of every
# frame, the table's 1.0 from age 114 times the factor, so neither the committed points nor
# the splice grid come near the cap, and Data refuses a table rate past 1.  So the cap
# binds through the factor: at 1.25, the accumulation cell's male rates pass 1 from
# attained age 111, policy month 552, where they stay to the limiting age.  S point 2
# alone, in a copy of S's table, under SPLICED_REFS and the factor.
CAPPED_REFS = {**SPLICED_REFS, "mort_be_factor": 1.25}
CAPPED_POINT = 2
CAPPED_MTH = 12 * (111 - 65)     # the first month at attained age 111, where it passes 1


def _capped_s(tmp_path):
    """ULB_UK_S on :data:`CAPPED_POINT` alone, under :data:`CAPPED_REFS`, read from a copy
    of S's inputs; the caller closes it."""
    s = mx.read_model(temp_inputs(tmp_path, model_path(TWIN),
                                  model_points=_s_table().loc[[CAPPED_POINT]]),
                      name=_name("capped_s"))
    for ref, value in CAPPED_REFS.items():
        setattr(s.Projection, ref, value)
    return s


def test_an_annual_mortality_past_1_is_capped_in_both_models(tmp_path):
    """Where the annual mortality product passes 1, both models' rate is 1.

    On :data:`CAPPED_POINT`, under :data:`CAPPED_REFS`, ``ULB_UK_S``'s product of the table
    rate and ``mort_be_factor`` passes 1 in month :data:`CAPPED_MTH` and stays past it to
    the end of the frame.  Both models cap it: ``mort_rate`` and the monthly rate,
    ``1 - (1 - q)^(1/12)``, are 1.0 in every one of those months, the float, not the int 1,
    which compares equal to it, and S's are floats below 1 in every month before.  So every
    policy in force at the start of the first capped month dies in it, none is in force
    after it, and every report holds finite floats alone.

    Four rows of the point, built from S by the generator: issued at the valuation date
    and 12 months after it, and restated in force in the month before the cap, opened with
    S's count and state there, each compared with S in every cell, the capped months
    included, as T1, T3 and the splice compare them, to 1e-9 relative with no absolute
    floor, but for the residuals, which keep the floor of 1e-9 (:func:`_compare`,
    USLIB-SEC-PLAN.md §5.1, step 6); and restated five months into the capped year, opened
    with S's state there and one policy, since S's count there is 0.  On each, the rate is
    1.0 from its first capped month, every policy in force there dies in it, and the count
    is 0.0 after it.
    """
    s = _capped_s(tmp_path / "s")
    sec = None
    try:
        sp = _point(s, CAPPED_POINT)
        end = sp.proj_len()
        product = [sp.data.mort_table().loc[(sp.sex(), sp.age(t)), "mort_rate"]
                   * sp.mort_be_factor for t in range(end)]
        cap = next(t for t in range(end) if product[t] > 1)
        assert (cap, sp.age(cap)) == (CAPPED_MTH, 111)
        after = range(cap, end)
        assert all(product[t] > 1 for t in after)
        for rate in (sp.mort_rate, sp.mort_rate_mth):
            assert all(type(rate(t)) is float and rate(t) < 1.0 for t in range(cap))
            assert [(type(rate(t)), rate(t)) for t in after] == [(float, 1.0)] * len(after)
        _sweep_s(sp)
        assert sp.pols_if(cap) > 0.0 and sp.pols_death(cap) == sp.pols_if(cap)
        assert [sp.pols_if(t) for t in range(cap + 1, end)] == [0.0] * (len(after) - 1)
        spec = dataclasses.replace(
            SPEC, derived=((CAPPED_POINT, cap - 1), (CAPPED_POINT, cap + 5)),
            future=((CAPPED_POINT, 12),))
        rows, _ = build_sec_table(spec, s)
        rows.loc[rows["source_mth"] == cap + 5, "policy_count"] = 1.0
        sec = mx.read_model(_sec_inputs(tmp_path / "sec", rows), name=_name("capped"))
        for ref, value in CAPPED_REFS.items():
            setattr(sec.Projection, ref, value)
        # Each row with the month its rate is first capped, on its own clock, and the
        # exemptions of its comparison with S: none for the row S's count does not open.
        cases = ((("twin", CAPPED_POINT, 0), cap, TWIN_EXEMPT_DEFAULT | SPEC.exempt),
                 (("future", CAPPED_POINT, -12), cap + 12, FUTURE_EXEMPT),
                 (("derived", CAPPED_POINT, cap - 1), 1, SPLICE_EXEMPT),
                 (("derived", CAPPED_POINT, cap + 5), 0, None))
        for case, first, exempt in cases:
            p = _row(sec, *case)
            if exempt is not None:
                assert _compare(sp, p, case[2], exempt | {"proj_len"}) == [], case
            capped, later = range(first, p.proj_len()), range(first + 1, p.proj_len())
            for rate in (p.mort_rate, p.mort_rate_mth):
                assert [(type(rate(t)), rate(t)) for t in capped] == (
                    [(float, 1.0)] * len(capped)), case
            assert p.pols_if(first) > 0.0 and p.pols_death(first) == p.pols_if(first), case
            assert [p.pols_if(t) for t in later] == [0.0] * len(later), case
            for report in ("result_cf", "result_uf", "result_pols"):
                frame = p.cells[report]()
                assert (frame.dtypes == "float64").all(), (case, report)
                assert np.isfinite(frame.to_numpy()).all(), (case, report)
    finally:
        if sec is not None:
            sec.close()
        s.close()


# A NaN sent to the bound written with its bound second, as (the bound, the Reference that
# feeds it, set to NaN on a model read for the test before it computes anything, the S
# point whose twin reads it, and the calls that must give the float NaN).  The cap reads
# mort_be_factor on every point, and the GMDB's charge reads the capped rate.  A bound
# written first would turn the NaN into the bound: a blank input read as certain death.
# proj_len() refuses a mort_be_factor that is not a number, so no report projects it; the
# calls here read no frame.  This form runs compiled unchanged, since a compiled ItemSpace
# takes the References when it is made (USLIB-SEC-PLAN.md §5.1, step 6, precised at M12).
NAN_BOUNDS = [
    ("the mortality cap, min(q, 1.0)", "mort_be_factor", 4,
     [("mort_rate", (0,)), ("mort_rate", (300,)), ("mort_rate_mth", (100,)),
      ("gmdb_charge_pp", (0,))]),
]


@pytest.mark.parametrize("bound, ref, s_point, calls", NAN_BOUNDS,
                         ids=[c[0] for c in NAN_BOUNDS])
def test_a_nan_that_reaches_a_bound_stays_nan(bound, ref, s_point, calls):
    """A NaN that reaches the bound written second stays NaN, and is not read as the bound.

    ``min`` keeps its first argument unless a later one compares smaller, in modelx and
    compiled alike, and no comparison with NaN holds, so with its bound first the cap would
    turn a NaN into 1.  It is written with its bound second, as ``ULB_UK_S`` writes it
    (:data:`NAN_BOUNDS`): the Reference that feeds it is set to NaN on a model read for the
    test, and every call must give the float NaN.  Every other ``min`` and ``max`` keeps
    ``ULB_UK_S``'s order, and ``Data`` refuses a blank the projection reads.
    """
    model = mx.read_model(model_path(SEC), name=_name("nan"))
    try:
        setattr(model.Projection, ref, float("nan"))
        p = _row(model, "twin", s_point, 0)
        lost = [f"{name}{args} = {value!r}" for name, args in calls
                for value in [p.cells[name](*args)]
                if not (type(value) is float and math.isnan(value))]
        assert not lost, f"{bound} loses a NaN {ref}: {lost}"
    finally:
        model.close()


def _outside_cover_faults(p, where, months):
    """Where ``p``, an ItemSpace that has evaluated nothing, departs from OUTSIDE_COVER.

    Every cell of :data:`OUTSIDE_COVER`, ``pols_if_at`` at each timing, ``av_pp_at`` at each
    of the fund's and ``claims`` at each kind, at each of ``months``, every one outside
    cover, against :data:`OUTSIDE_COVER`; then whether any of :data:`IN_COVER_ONLY` was
    evaluated on the way, which only a fresh ItemSpace can say.  A cell that raises is
    reported as a fault too, so the scan goes on.
    """
    faults = []
    for t in months:
        calls = [(name, (t,), want) for name, want in OUTSIDE_COVER.items()]
        calls += [("pols_if_at", (t, _code(p, timing)), 0.0) for timing in TIMINGS]
        calls += [("av_pp_at", (t, timing), 0.0) for timing in FUND_TIMINGS]
        calls += [("claims", (t, _code(p, kind)), 0.0) for kind in KINDS]
        for name, args, want in calls:
            try:
                got = p.cells[name](*args)
            except Exception as err:        # reported, so the scan goes on
                faults.append(f"{where}: {name}{args} raised {_raised(err)}")
                continue
            if got != want or type(got) is not type(want):
                faults.append(f"{where}: {name}{args} = {got!r}, not {want!r}")
    read = {name: sorted(p.cells[name].keys()) for name in IN_COVER_ONLY
            if any(not p.is_active(key) for key in p.cells[name].keys())}
    if read:
        faults.append(f"{where}: evaluated outside cover: {read}")
    return faults


def _after_the_frame_faults(p, where):
    """Where ``p`` departs from what the month after its frame holds, ``t = proj_len()``.

    At the limiting age the month is outside cover, and :func:`_outside_cover_faults`
    holds it.  After a fund exhausted short of it the bond is in cover and holds no units:
    every count and every flow of :data:`FRAME_CELLS` is 0.0, the frame having ended, and
    the fund at or below ``depletion_threshold``.
    """
    t = p.proj_len()
    if not p.is_active(t):
        return _outside_cover_faults(p, where, [t])
    faults = []
    calls = [(name, (t,)) for name in FRAME_CELLS]
    calls += [("pols_if_at", (t, _code(p, timing))) for timing in TIMINGS]
    calls += [("claims", (t, _code(p, kind))) for kind in KINDS]
    for name, args in calls:
        got = p.cells[name](*args)
        if got != 0.0 or type(got) is not float:
            faults.append(f"{where}: {name}{args} = {got!r}, not 0.0")
    if not 0.0 <= p.av_pp(t) <= p.depletion_threshold:
        faults.append(f"{where}: av_pp({t}) = {p.av_pp(t)!r}, not an exhausted fund")
    return faults


def test_every_guarded_cell_holds_its_outside_cover_value(spliced):
    """Outside cover each cell holds :data:`OUTSIDE_COVER`'s value, and reads no rate.

    On every committed point, in every month before issue, on a model that evaluates nothing
    else.  So afterwards none of :data:`IN_COVER_ONLY` may hold a value outside cover at all:
    ``is_active``'s docstring promises that outside cover no count evaluates a rate, and no
    table is read at a policy year or an attained age the bond does not have.  And in the
    first month after the frame, ``t = proj_len()``, which the count's look-ahead reads: at
    the limiting age the same, and after a fund exhausted short of it, where the bond is in
    cover, no count and no flow, and a fund at or below the threshold
    (:func:`_after_the_frame_faults`).

    The committed table's one point issued after the valuation date is the GMDB point, on
    the anchor's pattern, so on it a cell tied to another pattern would hold zero before
    issue, guarded or not.  So the same scan runs on the splice's future rows, the core's
    or, with ``UKLIB_SEC_FULL=1``, all of them: the accumulation cell, the adviser charge,
    the custom pattern, the GMDB in the money and the cap binding among them.  Each row is
    made afresh first and released after.

    Several of these guards change no number the frame shows: once the counts are zero
    outside cover, every cash flow is too, and an unguarded value multiplies a zero count.
    They are held here because they are what the docstrings promise a caller, and because
    the C step needs them: a table read at a policy year or an age the bond does not have
    would wrap round in a compiled model rather than fail (USLIB-SEC-PLAN.md F4, R1).
    """
    faults = []
    model = mx.read_model(model_path(SEC), name=_name("cover"))
    try:
        table = model.Data.model_point_table()
        for key, point_id in zip(point_keys(model), table.index):
            p = projection(model, key)
            faults += _outside_cover_faults(p, f"point {point_id}", range(p.t_entry()))
            faults += _after_the_frame_faults(p, f"point {point_id}")
    finally:
        model.close()
    sec = spliced[1]
    futures = _selected(FUTURES, CORE_FUTURES)
    for s_point, k in futures:
        key = _row_key(sec, "future", s_point, -k)
        if key in sec.Projection.itemspaces:
            _release(sec, key)
        try:
            p = projection(sec, key)
            faults += _outside_cover_faults(p, _case_id("future", s_point, -k), range(k))
            faults += _after_the_frame_faults(p, _case_id("future", s_point, -k))
        finally:
            _release(sec, key)
    assert futures and not faults, (
        f"{len(faults)} faults outside cover, first:\n  " + "\n  ".join(faults[:20]))


def test_the_points_sum_row_by_row_into_a_block(spliced):
    """Row ``t`` is the same month on every point, so a block is its frames summed (D3).

    S point 1's twin, the point restated at month 12 and the point issued 12 months on,
    summed as ``run_sec.py --block`` sums them, are indexed 0..364 and equal S's frame added
    to itself moved 12 months earlier and 12 months later.  A model whose frames sat on the
    policy clock would fail it.
    """
    s, sec = spliced
    cases = (("derived", 1, 12), ("future", 1, -12))
    keys = [_row_key(sec, *case) for case in cases if SEC_FULL or case in CORE_GRID]
    assert len(keys) == 2, "the block's rows are the core's"
    twin = _row_key(sec, "twin", 1, 0)
    try:
        frames = [projection(sec, key).result_cf() for key in (twin, *keys)]
    finally:
        for key in (twin, *keys):
            _release(sec, key)
    block = pd.concat(frames).groupby(level="t").sum()
    sdf = _point(s, 1).result_cf()
    expected = pd.concat([sdf, sdf.set_axis(sdf.index - 12).loc[0:],
                          sdf.set_axis(sdf.index + 12)]).groupby(level=0).sum()
    assert list(block.index) == list(range(365))
    assert frame_mismatches(expected, block) == []


# The labels an extract carries in the test below: the committed points' in reverse, from
# 111 down, so that a label is neither a position plus one nor in the order of the rows.
EXTRACT_LABELS = tuple(range(111, 100, -1))


def _extract():
    """The committed table as an administration extract would hold it: without the
    generator's columns, and labelled :data:`EXTRACT_LABELS`."""
    extract = _committed().drop(columns=list(GENERATED_COLUMNS))
    extract.index = pd.Index(EXTRACT_LABELS, name="point_id")
    return extract


def test_an_in_force_extract_needs_none_of_the_generator_columns(sec_model, tmp_path):
    """The model reads the in-force interface and S's columns, never where a row came from,
    and names each point by its label, wherever the row stands.

    ``row_kind``, ``source_policy_id`` and ``source_mth`` record how the generator made each
    shipped row, and an administration extract carries none of them.  Read without them,
    and with every label changed, every point projects what the committed table projects,
    in ``result_cf``, ``result_uf`` and ``result_pols``, to 1e-12, and ``run_sec.py``, run
    beside that extract, prints the point without saying where it came from.  On every
    shipped row ``source_mth`` equals ``duration_mth``, so a formula that read the one for the
    other would pass every test that leaves ``duration_mth`` as generated.  And a refusal
    names the extract's label.
    """
    extract = _extract()
    folder = _sec_inputs(tmp_path / "extract", extract)
    model = mx.read_model(folder, name=_name("extract"))
    try:
        table = model.Data.model_point_table()
        assert not set(GENERATED_COLUMNS) & set(table.columns)
        assert list(table.index) == list(EXTRACT_LABELS)
        for key, base_key in zip(point_keys(model), point_keys(sec_model)):
            mine, base = projection(model, key), projection(sec_model, base_key)
            for report in ("result_cf", "result_uf", "result_pols"):
                assert frame_mismatches(base.cells[report](), mine.cells[report](),
                                        rtol=1e-12, atol=1e-12) == [], (key, report)
            _release(model, key)
    finally:
        model.close()
    runner = folder.parent / "run_sec.py"
    shutil.copy(model_path(SEC).parent / "run_sec.py", runner)
    label = extract.index[extract["policy_id"] == "ULB-000003-M66"][0]
    out = _run_sec(runner, str(label))
    p = _row(sec_model, "derived", 3, 66)
    assert out.splitlines()[:2] == [
        f"model point {label}: ULB-000003-M66 - M65, premium 100,000 in 100 segments, AMC "
        f"1.00%, uplift 1.001, allowance_5pct withdrawals at 5.0% a year, adviser charge "
        f"0.50%",
        f"at the valuation date: in force 66 months: policy year 6, attained age 70, "
        f"{p.pols_if(0):.6f} in force, fund {p.av_pp_init():,.2f} a policy, "
        f"{p.wd_cum_pp_init():,.2f} withdrawn since issue"]
    last = extract.index[extract["policy_id"] == "ULB-000001-M352"][0]
    moved = _set("duration_mth", [last], 661)(extract)
    model = mx.read_model(_sec_inputs(tmp_path / "moved", moved), name=_name("moved"))
    try:
        _refused(_point(model, last).result_cf,
                 f"point_id {last}: duration_mth 661 is at or past the end of cover, "
                 f"policy month 660, the limiting age 120")
    finally:
        model.close()


def _standing(p):
    """What ``run_sec.py`` says of point ``p`` at the valuation date, stated here."""
    d = p.duration_mth_init()
    if d < 0:
        return f"to be issued at t = {-d}, {-d} months after the valuation date"
    if d == 0:
        return "issued at the valuation date, t = 0"
    return (f"in force {d} months: policy year {p.policy_year(0)}, attained age "
            f"{p.age(0)}, {p.pols_if(0):.6f} in force, fund {p.av_pp_init():,.2f} a "
            f"policy, {p.wd_cum_pp_init():,.2f} withdrawn since issue")


def test_run_sec_prints_a_point_and_the_block(sec_model):
    """The runner prints one point, saying where it came from, and the block (D8).

    Each mode in an interpreter of its own, as a user runs it, with exit code 0 and ASCII
    output, so that it prints on a Windows console under any code page.  The numbers are
    the model's.  The anchor cell, the runner's default, with its lines at the valuation
    date, each asserted whole, so that a longer number cannot pass for the one asserted,
    and its first twelve rows of cash flows and counts.  Point 4, the GMDB; point 8, the
    adviser charge restated in force at S's month 66, whose frame ends where its fund is
    exhausted; and point 11, to be issued 13 months on: each with the lines that say where
    its row came from and where it stands, which only the committed table's generator
    columns can say.  And the block: a line for each of the 11 points, in table order, its
    first twelve rows, which must be the committed points' frames summed row by row, as
    this test sums them, but the fund per policy, which summed is no amount, and those
    frames summed into projection years, each year's count the one in force in its first
    month.  Nothing else runs the runner on the committed table.
    """
    runner = model_path(SEC).parent / "run_sec.py"
    out = _run_sec(runner)
    assert out.splitlines()[:3] == [
        "model point 1: ULB-000001 (S's ULB-000001) - M65, premium 100,000 in 100 segments, "
        "AMC 1.00%, uplift 1.001, allowance_5pct withdrawals at 5.0% a year",
        "at the valuation date: issued at the valuation date, t = 0",
        "proj_len = 353 months from the valuation date (t = 0..352); the frame ends at "
        "policy month 353, the fund exhausted there"]
    anchor = _row(sec_model, "twin", 1, 0)
    assert anchor.result_cf().head(12).round(2).to_string() in out
    assert anchor.result_pols().head(12).round(6).to_string() in out
    adviser = _row(sec_model, "derived", 3, 66)
    for point_id, lines in (
            ("4", ["model point 4: ULB-000004 (S's ULB-000004) - M65, premium 100,000 in "
                   "100 segments, AMC 1.00%, uplift 1.001, allowance_5pct withdrawals at "
                   "5.0% a year, GMDB",
                   "at the valuation date: issued at the valuation date, t = 0",
                   "proj_len = 353 months from the valuation date (t = 0..352); the frame "
                   "ends at policy month 353, the fund exhausted there"]),
            ("8", ["model point 8: ULB-000003-M66 (S's ULB-000003 at its month 66) - M65, "
                   "premium 100,000 in 100 segments, AMC 1.00%, uplift 1.001, "
                   "allowance_5pct withdrawals at 5.0% a year, adviser charge 0.50%",
                   f"at the valuation date: {_standing(adviser)}",
                   "proj_len = 257 months from the valuation date (t = 0..256); the frame "
                   "ends at policy month 323, the fund exhausted there"]),
            ("11", ["model point 11: ULB-000004-F13 (S's ULB-000004, issued 13 months on) "
                    "- M65, premium 100,000 in 100 segments, AMC 1.00%, uplift 1.001, "
                    "allowance_5pct withdrawals at 5.0% a year, GMDB",
                    "at the valuation date: to be issued at t = 13, 13 months after the "
                    "valuation date",
                    "proj_len = 366 months from the valuation date (t = 0..365); the frame "
                    "ends at policy month 353, the fund exhausted there"])):
        assert _run_sec(runner, point_id).splitlines()[:3] == lines, point_id
    shown = _run_sec(runner, "2").splitlines()[2]
    assert shown == ("proj_len = 660 months from the valuation date (t = 0..659); the frame "
                     "ends at policy month 660, the limiting age")
    out = _run_sec(runner, "--block")
    table = sec_model.Data.model_point_table()
    points = [projection(sec_model, key) for key in point_keys(sec_model)]
    assert out.splitlines()[:len(points) + 1] == [
        "model points, t = 0 the valuation date for each:",
        *("  {:>2}  {:<15} {}; proj_len {}".format(
            point_id, table.at[point_id, "policy_id"], _standing(p), p.proj_len())
          for point_id, p in zip(table.index, points))]
    block = pd.concat([p.result_cf() for p in points]).groupby(level="t").sum()
    block = block.drop(columns="av_pp")
    assert block.head(12).round(2).to_string() in out
    years = pd.Index(block.index // 12 + 1, name="proj_year")
    annual = block.drop(columns="pols_if").groupby(years).sum()
    annual.insert(0, "pols_if", [block.at[12 * (y - 1), "pols_if"] for y in annual.index])
    assert annual.head(12).round(2).to_string() in out


# run_sec.py run as though it sat at /m/products/unit_linked_bond, a copy too shallow to
# have a repository above it: the source compiled under that name, so that its own __file__
# is it.
SHALLOW_RUN = """\
import sys
source = open(sys.argv[1], encoding="utf-8").read()
where = "/m/products/unit_linked_bond/run_sec.py"
sys.argv = [where, "--cython"]
exec(compile(source, where, "exec"), {"__name__": "__main__", "__file__": where})
"""


def test_run_sec_says_a_copy_without_the_repository_cannot_build(tmp_path):
    """``run_sec.py --cython`` outside the repository stops, saying it cannot build.

    The runner is uslib Term's as it stands, ``--cython`` and ``_tool()`` included
    (USLIB-SEC-PLAN.md §7.1, *Record — M14*, *Carried into Phase 1*), so that the C step
    changes nothing in it.  ``--cython`` builds with the repository's
    ``tools/build_sec_cy.py``, which a ``lifelib.create()`` copy does not carry, wherever
    the copy is: beside a copy of the model and its inputs, and at a path too shallow to
    hold a repository above the product at all, where uslib's runner once raised
    ``IndexError`` looking for the tool.  Each must exit nonzero having printed nothing, and
    say why.  Neither needs modelx-cython, since neither gets as far as building.
    """
    runner = model_path(SEC).parent / "run_sec.py"
    copy = _sec_inputs(tmp_path / "copy", _committed()).parent / "run_sec.py"
    shutil.copy(runner, copy)
    shallow = tmp_path / "shallow.py"
    shallow.write_text(SHALLOW_RUN, encoding="utf-8")
    for args in ((copy, "1", "--cython"), (shallow, runner)):
        done = _run_sec(*args, check=False)
        stderr = done.stderr.decode(errors="replace")
        assert done.returncode != 0 and done.stdout == b"", stderr
        assert "a lifelib.create() copy carries no tools/, so it cannot build" in stderr, (
            stderr)


def test_the_runner_sums_the_block_as_groupby_does(sec_model):
    """``run_sec.py``'s running sum of the block is pandas' ``groupby`` sum, bit for bit.

    A block run keeps one point's frame at a time, so it sums the frames as it goes,
    compensated, with ``add``, so that the block is the frames concatenated and summed by
    ``t``, as a runner that kept every point would, to the last bit.  The printed block, to
    two decimals, cannot show a last bit, so ``add`` itself is read from the runner, which
    runs the model when imported, and run here on the committed points' frames.  A plain
    running sum differs from ``groupby``'s on them, so the comparison can fail.
    """
    tree = ast.parse((model_path(SEC).parent / "run_sec.py").read_text(encoding="utf-8"))
    found = [node for node in tree.body
             if isinstance(node, ast.FunctionDef) and node.name == "add"]
    assert len(found) == 1
    space = {}
    exec(compile(ast.Module(found, []), "run_sec.py", "exec"), space)
    frames = [projection(sec_model, key).result_cf() for key in point_keys(sec_model)]
    columns = [c for c in frames[0].columns if c != "av_pp"]
    rows = max(len(frame) for frame in frames)
    total, compensation = np.zeros((rows, len(columns))), np.zeros((rows, len(columns)))
    plain = np.zeros((rows, len(columns)))
    for frame in frames:
        space["add"](total, compensation, frame[columns].to_numpy())
        plain[:len(frame)] += frame[columns].to_numpy()
    want = pd.concat(frames).groupby(level="t").sum()[columns].to_numpy()
    assert np.array_equal(total, want)
    assert not np.array_equal(plain, want)


def _defaulted(model_name):
    """The cells of ``model_name``'s Projection with a parameter that has a default, sorted,
    read from its source, as the C step's build reads it."""
    source = (model_path(model_name) / "Projection" / "__init__.py").read_text(
        encoding="utf-8")
    return sorted(node.name for node in ast.parse(source).body
                  if isinstance(node, ast.FunctionDef)
                  and (node.args.defaults or any(node.args.kw_defaults)))


def test_no_cell_takes_a_default_but_the_claims_total():
    """No cell has a defaulted parameter but ``claims(t, kind=None)``, the total (R12).

    A compiled model declares a defaulted parameter in its ``.pxd`` as ``long long x=*``,
    which the C step's typing guard would read as a parameter of that name, so no cell
    here adds one: ``ULB_UK_S``'s one, ``claims``' ``kind=None``, is R12's total, which the
    C step settles, as it did ``Term_UK_SEC``'s.
    """
    assert _defaulted(TWIN) == ["claims"]
    assert _defaulted(SEC) == ["claims"]


def _docs(model):
    """``(where, docstring)`` for the model, each Space and each cells, blanks as ``""``."""
    yield "model", model.doc or ""
    for space in model.spaces.values():
        yield space.name, space.doc or ""
        for cells in space.cells.values():
            yield f"{space.name}.{cells.name}", cells.doc or ""


def _mapped_cells(doc):
    """The names in the Cells column of the symbol map in ``doc``, the Projection docstring.

    The map is an RST simple table whose header row starts ``Notes symbol``.  The runs of
    ``=`` in the border under the header give the column spans.  A name is an identifier
    outside the parentheses of the column, ``av_pp_at`` of ``av_pp_at(t, timing)``; a cell
    of two names, ``amc_rate(), amc_rate_mth()``, maps both.
    """
    lines = doc.splitlines()
    head = next(i for i, line in enumerate(lines) if line.startswith("Notes symbol"))
    start, end = [m.span() for m in re.finditer("=+", lines[head + 1])][1]
    names = set()
    for line in lines[head + 2:]:
        if line.startswith("="):
            break
        bare = re.sub(r"\([^)]*\)", "", line[start:end])
        names.update(re.findall(r"[a-z_][a-z0-9_]*", bare))
    return names


_RULE = re.compile(r"^\s*=+(?:\s+=+)+\s*$")


def _table_overruns(doc):
    """The rows of the RST simple tables in ``doc`` that put text between two columns.

    A simple table's rule lines, runs of ``=`` apart, give its columns' spans, and a row
    whose text runs into the gap between two spans is what docutils rejects as a
    malformed table, dropping the whole table from the page.  Only the last column may run
    past its rule.  Each table runs from a rule line to the blank line that ends it.
    """
    lines, found, i = doc.splitlines(), [], 0
    while i < len(lines):
        if not _RULE.match(lines[i]):
            i += 1
            continue
        spans = [m.span() for m in re.finditer("=+", lines[i])]
        gaps = set()
        for (_, end), (start, _) in zip(spans, spans[1:]):
            gaps.update(range(end, start))
        i += 1
        while i < len(lines) and lines[i].strip():
            taken = {j for j, ch in enumerate(lines[i]) if ch != " "}
            if not _RULE.match(lines[i]) and taken & gaps:
                found.append(lines[i].strip())
            i += 1
    return found


# What only ULB_UK_S's docstrings may say: a reference into its Spaces, which the SEC pages
# would link to the wrong model; its clock, t counting policy months from issue; and a call
# of the cell this model renamed.
STALE = re.compile(r"~\.ULB_UK_S\.|``t`` counts \*\*policy months\*\* from issue"
                   r"|\bav_init_pp\(\)")


def test_the_docstrings_describe_the_valuation_clock(sec_model, s_model):
    """The docstrings say what this model is, and none says what only ULB_UK_S is.

    Whitespace is collapsed first, as ``test_model_conventions_uk`` collapses it, so that a
    phrase split across a line break still matches.  The model docstring names the
    valuation date, BasicTerm_SE, the policy clock, the SEC table, the threshold and the
    product.  The symbol map in the Projection docstring maps every cell running in force
    adds, which are exactly the cells ``ULB_UK_S`` lacks, and names nothing the model lacks:
    every name in it is a cell or a Reference.  No row of a simple table in any docstring
    puts text between two of its columns (:func:`_table_overruns`), which would drop the
    table from the rendered page.  And no docstring says what :data:`STALE` matches.
    """
    flat = {where: re.sub(r"\s+", " ", doc) for where, doc in _docs(sec_model)}
    for phrase in ("valuation date", "BasicTerm_SE", "duration_mth", TABLE,
                   "depletion_threshold", "unit-linked"):
        assert phrase in flat["model"], phrase
    assert set(NEW_CELLS) == set(sec_model.Projection.cells) - set(s_model.Projection.cells)
    mapped = _mapped_cells(sec_model.Projection.doc)
    missing = [cells for cells in NEW_CELLS if cells not in mapped]
    assert not missing, f"the symbol map does not map {missing}"
    known = set(sec_model.Projection.cells) | set(sec_model.Projection.refs)
    unknown = sorted(mapped - known)
    assert not unknown, f"the symbol map names what the model lacks: {unknown}"
    overruns = {where: rows for where, rows in ((where, _table_overruns(doc))
                                                for where, doc in _docs(sec_model)) if rows}
    assert not overruns, f"table rows that run into a column gap: {overruns}"
    stale = sorted(where for where, doc in flat.items() if STALE.search(doc))
    assert not stale, f"docstrings that describe ULB_UK_S: {stale}"


@pytest.mark.docutils
def test_the_docstrings_parse_as_rst(sec_model):
    """Every docstring of the model parses as reStructuredText, without a warning.

    The docs build reads each docstring through docutils, which reports a malformed table, a
    bad indentation or an unclosed inline markup and drops what it cannot read; a raw-text
    test sees none of it.  Each docstring, dedented as autodoc dedents it and its Sphinx
    roles read as plain interpreted text, which docutils alone does not know, is parsed
    here, and any warning or error is a fault.  docutils comes with the docs build, not with
    the models' requirements, so the test is skipped where it is absent; the column check
    in the test above runs everywhere.
    """
    core = pytest.importorskip("docutils.core")
    faults = []
    for where, doc in _docs(sec_model):
        stream = io.StringIO()
        core.publish_doctree(re.sub(r":[a-z]+:`", "`", inspect.cleandoc(doc)),
                             settings_overrides={"report_level": 2, "halt_level": 5,
                                                 "warning_stream": stream})
        faults += [f"{where}: {line}" for line in stream.getvalue().splitlines()
                   if re.search(r"\((WARNING|ERROR|SEVERE)/", line)]
    assert not faults, f"{len(faults)} docutils messages, first:\n  " + "\n  ".join(
        faults[:10])


def test_the_sec_model_reads_the_s_tables_in_place(sec_model, s_model):
    """One copy of each assumption table serves both models (D1).

    The two ``input_dir()`` s are one directory, and SEC's filename References are S's with
    ``model_point_file`` changed, to ``model_point_table_sec.csv``: an edit to a table
    reaches both models, and the two can never drift apart.  And every Reference of S's is
    the SEC model's at S's value, but those it adds, the threshold and the youngest issue
    age, so that no assumption moves between the two (USLIB-SEC-PLAN.md §7.7, *Record —
    M9*, *References held to S's*).
    """
    assert sec_model.Data.input_dir() == s_model.Data.input_dir()
    files = {r: v for r, v in s_model.Data.refs.items() if r.endswith("_file")}
    assert {r: v for r, v in sec_model.Data.refs.items() if r.endswith("_file")} == {
        **files, "model_point_file": TABLE}
    plain = (bool, int, float, str)
    s_refs = {r: v for r, v in s_model.Projection.refs.items()
              if isinstance(v, plain) and r != "point_id"}
    sec_refs = {r: v for r, v in sec_model.Projection.refs.items()
                if isinstance(v, plain) and r != "point_id"}
    assert sec_refs == {**s_refs, "depletion_threshold": THRESHOLD, "issue_age_min": 18}


def test_the_core_grid_reaches_every_branch(spliced, splice_records):
    """What the default run's T2 and T3 cases reach, which the full grid only multiplies.

    The default run thins the splice to a core (the module docstring), and this test is
    what keeps the thinning from costing a branch.  First, statically, over S's table with
    the variants, each property below holds of some core case: every withdrawal pattern,
    both sexes, the adviser charge, the GMDB rider, the 101% uplift and each variant; and
    each kind of valuation month: the first months, on an anniversary, in the month before
    one, mid-year, either side of each surrender band's edge, about policy year 21, and the
    last month of a frame, at exhaustion and at the limiting age.  And of some core future
    case: issued off the valuation anniversaries and on them, more than a year on, each
    pattern, the adviser charge, the GMDB and the variants.

    Then, on the splice's model, of some core row, each of :data:`AT_VALUATION` and
    :data:`IN_FRAME`, what no column of the table shows: both opening-state columns in use,
    and the GMDB opened from what is left of its guarantee and at 0; and every branch and
    both sides of every ``min`` and ``max`` the full grid reaches: the withdrawal's three
    bounds, the cap's two bases, the GMDB in and out of the money, the fund closed on 0 and
    on a rounding, the excess gain, the surrender table's last year, the surrender cap, the
    allowance step and its twenty years, and the frame's two ends.

    Each core row's branches were recorded by the T2 or T3 case that compared it
    (:func:`_settle`), and a row no case has recorded is evaluated here.  With
    ``UKLIB_SEC_FULL=1`` it asks the same of the full grid's rows, which must reach nothing
    the core does not.
    """
    s_table = _s_table_with_variants()

    def at(p, column):
        return s_table.at[p, column]

    def flag(p, column):
        return str(at(p, column)).lower() == "true"

    splices = {
        **{f"the {w} pattern": (lambda k, p, d, w=w: at(p, "wd_pattern") == w)
           for w in ("none", "allowance_5pct", "custom")},
        **{f"sex {x}": (lambda k, p, d, x=x: at(p, "sex") == x) for x in ("M", "F")},
        "an adviser charge": lambda k, p, d: at(p, "oac_rate") > 0.0,
        "the GMDB": lambda k, p, d: flag(p, "gmdb_flag"),
        "a 101% uplift": lambda k, p, d: at(p, "db_uplift") > 1.001,
        **{f"variant {v}": (lambda k, p, d, v=v: p == v) for v in VARIANTS},
        "in the second month": lambda k, p, d: d == 1,
        "on an anniversary": lambda k, p, d: k == "derived" and d % 12 == 0,
        "in the month before an anniversary": lambda k, p, d: d % 12 == 11,
        "mid-year": lambda k, p, d: d % 12 not in (0, 11),
        "either side of a band's edge": lambda k, p, d: d in (11, 12, 23, 24, 59, 60, 119,
                                                              120),
        "about policy year 21": lambda k, p, d: d in (239, 240, 241),
        "the last month before exhaustion": lambda k, p, d: (
            d == FRAME[p] - 1 and FRAME[p] < 12 * (120 - at(p, "age_at_entry"))),
        "the last month before the limiting age": lambda k, p, d: (
            d == FRAME[p] - 1 and FRAME[p] == 12 * (120 - at(p, "age_at_entry"))),
        "a frame S runs on past": lambda k, p, d: S_FRAME[p] > FRAME[p],
    }
    futures = {
        "issued off the anniversaries": lambda p, k: k % 12 != 0,
        "issued on them": lambda p, k: k % 12 == 0,
        "issued more than a year on": lambda p, k: k > 12,
        **{f"the {w} pattern": (lambda p, k, w=w: at(p, "wd_pattern") == w)
           for w in ("allowance_5pct", "custom")},
        "an adviser charge": lambda p, k: at(p, "oac_rate") > 0.0,
        "the GMDB": lambda p, k: flag(p, "gmdb_flag"),
        "a variant": lambda p, k: p in VARIANTS,
        "a frame S runs on past": lambda p, k: S_FRAME[p] > FRAME[p],
    }
    missing = [what for what, holds in splices.items()
               if not any(holds(*case) for case in CORE_SPLICES)]
    missing += [what for what, holds in futures.items()
                if not any(holds(*case) for case in CORE_FUTURES)]
    assert not missing, f"no core case reaches: {missing}"

    reached = set()
    for case in sorted(CORE_GRID):
        reached |= _record_of(spliced, splice_records, case)["branches"]
    missing = [what for what in (*AT_VALUATION, *IN_FRAME) if what not in reached]
    assert not missing, f"no core row reaches: {missing}"
    if SEC_FULL:
        beyond = set()
        for case in GRID:
            if case not in CORE_GRID:
                beyond |= _record_of(spliced, splice_records, case)["branches"]
        assert beyond <= reached, f"the full grid alone reaches: {sorted(beyond - reached)}"
