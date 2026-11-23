"""In-force tests for WOL_UK_SEC: the splice, future business, counts, regeneration.

``WOL_UK_SEC`` is ``WOL_UK_S`` taught to run in force at a valuation date
(UKLIB-SEC-PLAN.md, milestone M5, after USLIB-SEC-PLAN.md's Phase 1).  It runs on two
clocks: ``t`` counts months from the valuation date, the same month for every model point,
and ``duration_mth(t)`` counts the months the policy has been in force,
``duration_mth_init() + t``.  A model point may be a policy already in force at the
valuation date, in any month of its policy year, one issued at it, or one to be issued
after it, as in ``basiclife/BasicTerm_SE``.  A policy in force opens with two counts, the
full-cover ``policy_count`` and the paid-up ``pols_pu_init``, the library's first
two-strand count, and with four columns of state beside them, each measured at the
valuation instant: the paid-up cover per paid-up policy, the premiums paid, and the cover
and premium of the policy year under way.

The worked example is not restated here.  On a point issued at the valuation date the two
clocks coincide and the model is ``WOL_UK_S``, and ``test_model_conventions_uk.py``
asserts that cell by cell on the twins of S's seven new-business points (T1), so every
golden of ``test_whole_of_life_uk.py`` on them holds on this model with no number
copied.  The conventions also hold the SEC family's other rules: every frame opens at
``t = 0``, ``pols_if`` is the ``BEF_DECR`` count, ``BEF_DECR`` is ``BEF_NB`` plus the
month's new business, new business enters once, and nothing happens before issue.  This
module holds the rest of the plan's tests (its §5) and the product's own facts:

* T2, the splice: an S point restated in force at month ``d``, opened with the state S
  carries into ``d``, continues S's projection from ``d`` on, in every cell of S's and in
  ``result_pols``.  The months straddle the product's events: the moratorium and the
  suicide window, the first anniversary, the first paid-up conversion, the crossover,
  premium cessation, the mortality cap and the limiting age.  The crossover stress that
  ships at 0 is on, at 0.5, and four variants of S's points, in a copy of S's table, add
  the RPI increases with the paid-up value, the double accidental benefit with the
  paid-up value, an over-50s policy issued at 80, and an underwritten female smoker.  A
  stress that lapses every policy is spliced by a test of its own, and the RPI's floor and
  caps are held to ``WOL_UK_S``'s by another.
* T3, future new business: a point issued ``k`` months after the valuation date is S's
  projection ``k`` months on, with zeros before issue and no table read there.
* D11's R1 and R2, and D3's and D5's chains: on the splice's grid no cell is called at a
  negative month, none on the books reads a month before them, and none reads beyond
  ``t + 1``; on the committed points no recursion runs backward over the frame; the policy
  clock is a closed form; and each chain, called cold, runs one cell a month back to
  ``t_entry()``, at the contract's longest cover, on each shape.
* T4, the count algebra: the counts roll forward on both strands through new business,
  deaths, lapses and conversions, ``result_pols`` is S's report with the new business, the
  paid-up deaths and the truncation residual beside it, multiplying ``policy_count`` and
  ``pols_pu_init`` by 2.5 with every assumption that ships at zero switched on multiplies
  every flow and every counted cell by 2.5 and moves no per-policy value, a point restated
  a month on continues its own flows, and the roll-forward, whose tolerance scales with the
  policies on the books, closes on ten million policies.
* T5, validation: each malformed row of the table is refused as it is read, naming its
  point, by its label on an extract labelled otherwise; each assumption table, malformed or
  holding a value that is not a number in its range, is refused before a value of it is
  read, naming its lines; the future horizon is a Reference that bounds future business; a
  point past the limiting age, one the contract does not issue and one that reads a
  Reference off its domain are refused by the frame, each domain at both its edges; a
  cover, a premium or premiums paid past the floats in the cell where they first are; the
  edges of the interface are accepted; and so is every state ``WOL_UK_S`` reaches, on each
  set of inputs on which those states differ.
* T6, regeneration: the committed ``model_point_table_sec.csv`` is what the generator makes
  of ``WOL_UK_S`` and its table as they stand.
* Then the product's own facts: the two clocks on the shipped points; each twin S's in every
  cell with improvement, the RPI, the take-up and the stress on, where T1 holds them at
  their shipped values and T2 holds improvement at 0; the committed rows continuing their S
  points, those read under References of their own continuing S under them; each history
  column read rather than recomputed (UKLIB-SEC-PLAN.md K14), the cover and the premium
  on the RPI and the fixed increases, the premiums paid, and the paid-up count and cover;
  expense inflation and mortality improvement on the valuation clock, and where
  improvement carries survivors past the truncation check; the crossover a policy month
  carried from the opening state; the moratorium, the suicide window and commission on
  the policy clock; acquisition on new business; a stress that lapses every policy, and
  the RPI's floor and caps; the cap on mortality, a NaN that reaches a bound and a check
  whose residual is NaN; the values outside cover; the block; an
  in-force extract; the runner; the cells' defaulted parameters; the docstrings; the
  shared input tables; and what the default grid reaches.
* C2, the fingerprint: every committed point computes what the model computed when its E
  step ended, frozen at the end of this module before its C step changed anything
  (USLIB-SEC-PLAN.md §5.4).

SEC month ``t`` is S month ``t + source_mth`` throughout, the direction in which
``uk_sec_support`` takes its ``t_offset``: ``d`` for a point restated at S month ``d``,
``-k`` for one issued ``k`` months on.  ``WOL_UK_S`` has no point in force, so there is no
in-force twin.

**The core grid and the full one** (UKLIB-SEC-PLAN.md U6).  T2 and T3 over every S point
at every month, about 170 cases, run by default on a core, chosen so that between them they
reach every branch, every opening-state column, every kind of valuation month and both
sides of every ``min`` and ``max`` the full grid reaches, which
``test_the_core_grid_reaches_every_branch`` asserts.  The other cases, and the rules
test's scan of their rows, carry the ``sec_full`` marker and are skipped, with the reason
shown, unless ``UKLIB_SEC_FULL=1`` is set.  They are never dropped: one leg of the CI
matrix sets it, and ``UKLIB_SEC_FULL=1 python -m pytest -m sec_full
lifelib/libraries/uklib/tests/test_whole_of_life_uk_sec.py`` runs them alone.  Each
splice row is released once it has been read (``_release``), as ``run_sec.py --block``
releases its points.

Every test keeps four rules.  Each model is read under a name of its own and closed:
``conftest.whole_of_life`` reads S under its default name, and reading a model under a
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
import errno
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
    codes, fingerprint_mismatches, frame_mismatches, full_sweep, sweep, temp_inputs,
    twin_mismatches)

SEC, TWIN = "WOL_UK_SEC", "WOL_UK_S"
TABLE = "model_point_table_sec.csv"
SPEC = SEC_SPECS[SEC]

# S's seven points, all new business: the over-50s anchor cell, a 70-year-old woman paying
# £30 a month for £5,000 (1); with the double accidental benefit (2); with the pro-rata
# paid-up value (3); with RPI increases (4); the underwritten cell, a 40-year-old man
# paying £101.25 a month for life for £150,000 (5); with fixed increases of 5% and 10% (6);
# and an over-50s male smoker at 65 (7).
S_POINTS = (1, 2, 3, 4, 5, 6, 7)

# T2's months (UKLIB-SEC-PLAN.md §6.4).  On the over-50s points at 70: the second month; 6,
# inside the moratorium; 11, 12 and 13 about the first anniversary, where the moratorium
# ends, the lapse table moves to its second year and commission stops; 60, the lapse
# table's last year; 118 to 121 about the first conversion to paid-up, at the end of policy
# month 119, the 120th payment, half of 240; 165 to 167 about the crossover at 166, and 185
# and 186 about the RPI point's at 185; 239 to 241 about premium cessation at 240; 479 to
# 481 about the mortality cap, which binds from attained age 110, policy month 480; and
# 599, the last month before the limiting age.  On the underwritten points at 40: 11 to 13
# about the suicide window's end and the first anniversary; 642 and 643 about the
# increasing point's crossover; 887 to 889 about the cap at 888, attained age 114; and 959,
# the last month.  On the male smoker at 65: 222 and 223 about its crossover; 299 to 301
# about its cessation at 300; 431 to 433 about its cap at 432, attained age 101; and 659.
_O50 = (1, 6, 11, 12, 13, 60, 118, 119, 120, 121, 165, 166, 167, 239, 240, 241, 479, 480,
        481, 599)
_UW = (11, 12, 13, 642, 643, 887, 888, 889, 959)
SPLICE_MTHS = {1: _O50, 2: _O50, 3: _O50, 4: (*_O50, 185, 186), 5: _UW, 6: _UW,
               7: (222, 223, 299, 300, 301, 431, 432, 433, 659)}

# T3's months: issued one month on, which puts the policy anniversaries a month off the
# valuation years; twelve, which puts them back on; and the horizon, 120, the latest the
# table admits.  Each variant is issued 13 months on, more than a year after the valuation
# date and off its anniversaries (USLIB-SEC-PLAN.md §7.1, *Record — M14*, *Splice grid*).
FUTURE_MTHS = (1, 12, 120)

# Five more S points, in the splice's copy of S's table and never in the committed one,
# each one of S's points changed so as to reach what S's own points cannot:
#
# 8, S point 4 with the pro-rata paid-up value: conversions at a cover that RPI has
#   raised, so that each paid-up cash sum is a share of an indexed cover;
# 9, S point 2 with the pro-rata paid-up value: the double accidental benefit, the
#   moratorium and the paid-up strand together;
# 10, S point 1 issued at 80, its premiums ceasing at 90, after 120 months: the latest
#   entry age of the over-50s cell, a cessation of its own, total premiums below the cash
#   sum, so no crossover, and the cap from policy month 360;
# 11, S point 6 as a female smoker: the underwritten cell's other mortality rows, the
#   assured female smoker's, which no S point reads, capped from policy month 852;
# 12, S point 3 with its premiums ceasing after 239 months, an odd number: the first
#   conversion at the end of policy month 119, when 120 of 239 payments, more than half,
#   have been made, so that the paid-up strand is in force from 120, half of 239 rounded
#   up, where half rounded down would be 119; with a cessation a multiple of 12 the two
#   agree.
#
# Each variant is (the S point it changes, the columns it changes); the policy_id keeps
# the generated ids apart.
VARIANTS = {
    8: (4, {"policy_id": "WOL-900008", "variant_paid_up": True}),
    9: (2, {"policy_id": "WOL-900009", "variant_paid_up": True}),
    10: (1, {"policy_id": "WOL-900010", "entry_age": 80, "cessation_months": 120}),
    11: (6, {"policy_id": "WOL-900011", "sex": "F", "smoker": "S"}),
    12: (3, {"policy_id": "WOL-900012", "cessation_months": 239}),
}
VARIANT_MTHS = {8: (118, 119, 120, 121, 185, 186, 200, 239, 240, 241),
                9: (11, 12, 13, 119, 120, 200),
                10: (1, 11, 12, 13, 119, 120, 121, 359, 360, 361, 479),
                11: (12, 642, 643, 851, 852, 853, 959),
                12: (119, 120, 121, 238, 239, 240)}
LATE_FUTURES = tuple((p, 13) for p in VARIANTS)


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


# The months from issue to the limiting age of each S point and variant, 12 times the
# years from its entry age to 120.
COVER = {p: 12 * (120 - int(x)) for p, x in _s_table_with_variants()["entry_age"].items()}

# The committed rows the generator reads from S under References of their own (the spec's
# derived_refs), by (S policy, month), with those References.
UNDER_REFS = {(_s_table().at[p, "policy_id"], d): refs
              for (p, d), refs in SPEC.derived_refs.items()}

# T2's cases, as (row_kind, S point, source_mth): each S point restated in force at each
# of its months, and each variant at its own.  WOL_UK_S has no point in force, so no twin
# is a splice case.  T3's cases, as (S point, k).
SPLICES = (tuple(("derived", p, d) for p in S_POINTS for d in SPLICE_MTHS[p]
                 if d < COVER[p])
           + tuple(("derived", p, d) for p, mths in VARIANT_MTHS.items() for d in mths))
IN_FORCE_TWINS = ()
FUTURES = tuple((p, k) for p in S_POINTS for k in FUTURE_MTHS) + LATE_FUTURES

# The default run's cases (the module docstring), each with what it is there for.  The
# rest of SPLICES and FUTURES run with UKLIB_SEC_FULL=1.
CORE_SPLICES = {
    ("derived", 1, 6): "the anchor cell inside its moratorium, in its first policy year",
    ("derived", 1, 11): "the anchor cell in the moratorium's last month",
    ("derived", 1, 12): "the anchor cell on its first anniversary, the moratorium over",
    ("derived", 1, 166): "the anchor cell in its crossover month, stressed from t = 0",
    ("derived", 1, 240): "the anchor cell as its premiums cease",
    ("derived", 1, 480): "the anchor cell in its first capped month",
    ("derived", 1, 599): "the anchor cell in the last month before the limiting age",
    ("derived", 2, 13): "the double accidental benefit past the moratorium",
    ("derived", 3, 119): "the paid-up point in the month of its first conversions",
    ("derived", 3, 120): "the paid-up point with its first conversions in force",
    ("derived", 3, 167): "the paid-up point past its crossover, the stress converting",
    ("derived", 3, 241): "the paid-up point after cessation, its strand running off",
    ("derived", 4, 12): "the RPI point on its first anniversary, its first increase",
    ("derived", 4, 186): "the RPI point past its crossover",
    ("derived", 4, 239): "the RPI point in its last premium month",
    ("derived", 4, 241): "the RPI point after its premiums ceased, its crossover history",
    ("derived", 5, 12): "underwritten on its first anniversary, the suicide window over",
    ("derived", 5, 888): "underwritten in its first capped month",
    ("derived", 6, 11): "underwritten increasing, inside the suicide window",
    ("derived", 6, 643): "underwritten increasing past its crossover",
    ("derived", 6, 959): "underwritten increasing in its last month",
    ("derived", 7, 223): "the male smoker past its crossover",
    ("derived", 7, 300): "the male smoker as its premiums cease",
    ("derived", 7, 432): "the male smoker in its first capped month",
    ("derived", 8, 120): "RPI and paid-up together, the first conversions in force",
    ("derived", 8, 186): "RPI and paid-up past the crossover",
    ("derived", 9, 12): "the double accidental benefit with paid-up, the moratorium over",
    ("derived", 9, 200): "the double accidental benefit with paid-up, the strand in force",
    ("derived", 10, 120): "issued at 80, its premiums ceasing",
    ("derived", 10, 360): "issued at 80, its first capped month",
    ("derived", 11, 12): "an underwritten female smoker on its first anniversary",
    ("derived", 11, 852): "an underwritten female smoker in its first capped month",
    ("derived", 12, 120): "an odd cessation, its strand in force from half of 239 up",
}
CORE_FUTURES = {
    (1, 1): "issued a month off the valuation anniversaries",
    (1, 12): "issued on them, a year on",
    (3, 120): "the paid-up point at the horizon",
    (4, 1): "the RPI increases a month off the valuation anniversaries",
    (6, 12): "underwritten increasing, a year on",
    (7, 1): "the male smoker",
    (8, 13): "RPI and paid-up, more than a year on",
    (10, 13): "issued at 80, more than a year on",
    (11, 13): "an underwritten female smoker, more than a year on",
}

SEC_FULL = os.environ.get("UKLIB_SEC_FULL") == "1"
FULL_ONLY = (pytest.mark.sec_full,
             pytest.mark.skipif(not SEC_FULL, reason="the full splice grid runs with "
                                "UKLIB_SEC_FULL=1 (UKLIB-SEC-PLAN.md U6)"))

# What the splice sets in both models, S and SEC alike, before either evaluates anything.
# Two inputs run on the valuation clock (D7): expense inflation, which S runs from issue
# and SEC from the valuation date, so at the shipped 3% the expenses of a point opened at d
# differ by the inflation of the policy years before d, by design, and at 0 both factors
# are 1; and mortality improvement, which S runs from issue too, and which ships at 0,
# where the splice keeps it (UKLIB-SEC-PLAN.md §6.4, §9 item 4): on it SEC's mortality at d
# is S's at d with none of the improvement since issue, by design.  Each clock is then
# asserted on its own, with its rate on.  There is no scenario table, so no input table
# moves with d.  The one other assumption that ships at zero, the crossover stress on the
# lapse rate, is on, at 0.5, so that past the crossover the premiums paid, which the
# opening state carries, move the lapses, the conversions and so every count: without it
# no number past the moratorium reads them.  The identity does not depend on the value,
# only on both models having the same one; a stress that lapses every policy, the lapse
# rate's bound at 1, has a test of its own.
SPLICED_REFS = {"inflation_rate": 0.0, "mort_improvement": 0.0, "lapse_crossover_beta": 0.5}

# The improvement the module switches on where it compares the model with itself or a twin
# with S: a rate at which check_truncation holds on every committed point, 0.2% a year
# (UKLIB-SEC-PLAN.md §6.4).  The truncation test records where it gives way.
IMPROVEMENT = 0.002

# Every assumption that ships at zero, switched on, for T4, at the shipped inflation: the
# stress, as the splice sets it, and improvement, which T4 can hold since it compares the
# model with itself.
SWITCHED_ON = {"lapse_crossover_beta": 0.5, "mort_improvement": IMPROVEMENT}

# The cells T2 and T3 skip beyond T1's, which already drop result_pols as a whole (the
# spec's exempt).  proj_len counts from the valuation date on SEC and from issue on S, so it
# differs by d, or by -k, by design; frame_mismatches asserts what it must get right, that
# both frames end at the same instant.  Both tests compare result_pols column by column
# instead.
SPLICE_EXEMPT = TWIN_EXEMPT_DEFAULT | SPEC.exempt | {"proj_len"}
FUTURE_EXEMPT = SPLICE_EXEMPT

# The result_cf columns that expense inflation moves, and the cells they are made of: on
# the committed points, at the shipped 3% and the shipped improvement of 0, the only places
# an in-force row departs from S.
INFLATED = ("expenses", "net_cf")
INFLATION_CELLS = frozenset({"inflation_factor", "expenses", "net_cf", "result_cf"})

# The S cell whose exact value is 0 and whose computed value is rounding about it, the
# roll-forward's residual: a comparison with S holds it at the harness's absolute floor of
# 1e-9, and every other cell at none (_compare).
RESIDUALS = frozenset({"check_pols_roll_fwd_resid"})

# The reads keyed by an attained age or a policy year, and the monthly rates, none of which
# may be evaluated before issue (R1, D4).  The annual rates, mort_rate and lapse_rate, are
# columns of result_pols, as in WOL_UK_S, so the report evaluates them in every month of
# the frame, and before issue each is 0.0 without a read (OUTSIDE_COVER): the reads under
# them are what T3 holds.
KEYED_READS = ("age", "duration", "policy_year", "lapse_rate_base", "mort_rate_mth",
               "lapse_rate_mth")

# The cells that scale with the counts.  Every other cell is a per-policy amount, a rate,
# a factor, a clock or a flag, and must not move when the counts do.
COUNTED = frozenset({
    "policy_count", "pols_if_init", "pols_pu_init", "pols_if", "pols_if_at", "pols_new_biz",
    "pols_pu", "pu_benefit", "pols_all", "pols_death", "pols_death_pu", "pols_exit",
    "pols_convert", "pols_lapse", "pols_maturity", "premiums", "claims", "expenses",
    "commissions", "net_cf", "check_pols_roll_fwd_resid", "result_cf", "result_pols"})

# result_pols' columns, in its order: the full-cover count, the new business within it,
# the paid-up count, the month's deaths on each strand, its lapses and conversions in
# processing order, and the truncation residual; then S's other columns, the premiums paid,
# the cover, the benefit per death and the rates, which no count moves.
RESULT_POLS = ["pols_if", "pols_new_biz", "pols_pu", "pols_death", "pols_death_pu",
               "pols_lapse", "pols_convert", "pols_maturity", "prem_cum_pp", "cover_pp",
               "benefit_death_pp", "mort_rate", "lapse_rate"]
COUNTS_POLS = RESULT_POLS[:8]
PER_POLICY_POLS = RESULT_POLS[8:]

# S's three timings and BEF_NB, the one running in force adds; and the kinds.
TIMINGS = ("BEF_NB", "BEF_DECR", "BEF_LAPSE", "AFT_DECR")
KINDS = ("DEATH", "DEATH_PU", "LAPSE")
BENEFITS = ("NON_ACC", "ACC", "DEATH", "PAID_UP")

# What each cell holds outside cover, before issue and from the month cover has ended, as
# its docstring says: no count, so no cash flow; no cover, premium or premiums paid; no
# rate read at a policy year or an age the policy does not have; no window open.  The type
# is part of the value.  A count is a float in every branch, a flag a bool and the payments
# made an int, because the C step types a cell by the values it returns (USLIB-SEC-PLAN.md
# F3).  The guard test also calls pols_if_at at each timing, claims at each kind and
# benefit_pp at each benefit, all 0.0.
OUTSIDE_COVER = {
    "is_active": False, "in_moratorium": False, "payments_made": 0, "pu_eligible": False,
    "cover_pp": 0.0, "premium_pp": 0.0, "prem_cum_pp": 0.0, "mort_rate": 0.0,
    "lapse_rate_base": 0.0, "lapse_rate": 0.0, "pols_if": 0.0, "pols_pu": 0.0,
    "pu_benefit": 0.0, "pols_all": 0.0, "pols_new_biz": 0.0, "pols_death": 0.0,
    "pols_death_pu": 0.0, "pols_exit": 0.0, "pols_convert": 0.0, "pols_lapse": 0.0,
    "pols_maturity": 0.0, "premiums": 0.0, "claims": 0.0, "expenses": 0.0,
    "commissions": 0.0, "net_cf": 0.0, "check_pols_roll_fwd_resid": 0.0}

# The cells a month outside cover may not reach: the clocks of the contract and the
# monthly rates, each keyed by a policy year or an attained age.  The reads that guard
# themselves are held by their values in OUTSIDE_COVER instead.
IN_COVER_ONLY = ("age", "duration", "policy_year", "mort_rate_mth", "lapse_rate_mth")

# The opening state, in the table's order, and the cells running in force adds to
# WOL_UK_S's, each of which the symbol map must name.
STATE = ("pols_pu_init", "pu_benefit_pp_init", "prem_cum_pp_init", "cover_pp_init",
         "premium_pp_init", "crossover_mth_init")
NEW_CELLS = ("policy_count", "duration_mth_init", "t_entry", "is_active", "limit_mth",
             "pols_new_biz", *STATE)

INFLATION = 0.03        # the shipped inflation_rate, which the inflation test reads

# The recursion limit, as mx.set_recursion takes it, under which the committed points are
# first swept (R2, F7).  A report evaluates each column in ascending t, so a forward
# recursion, through t - 1, finds the month before already cached: the committed points'
# sweep passes under a limit of 12 (measured at M5).  A backward recursion over the frame,
# through t + 1, opens a chain as long as the frame, and the shortest committed frame is
# 360.
CALL_DEPTH = 40

# The reads beyond t + 1 the model makes, as (reader, cell read): none.  The rules test
# admits no other.
LOOK_AHEAD = frozenset()


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
                       model_point_file=TABLE, edits=dict(edits or {}))


def _read_edited(tmp_path, edit, edits=None):
    """WOL_UK_SEC read from a copy whose SEC table is ``edit(_committed())``."""
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
    """Evaluate on an S point what the splice compares: the sweep, and cells more.

    :func:`uk_sec_support.sweep` reaches ``WOL_UK_S``'s ``pols_if_at`` at none of its
    timings, since S's ``pols_if`` is a recursion of its own and its exits read
    ``"BEF_LAPSE"`` alone; nor ``duration_mth``, which no S formula reads, nor the
    crossover, which no report reads; nor, on a point that does not reach them, the
    benefit of each kind, the payments made, the moratorium and the paid-up eligibility.
    A cell S never evaluates is compared nowhere, so they are evaluated here, over the
    frame, and the splice and the future comparison see them too.
    """
    sweep(proj)
    for t in range(proj.proj_len()):
        for timing in ("BEF_DECR", "BEF_LAPSE", "AFT_DECR"):
            proj.pols_if_at(t, timing)
        for kind in BENEFITS:
            proj.benefit_pp(t, kind)
        proj.duration_mth(t)
        proj.payments_made(t)
        proj.in_moratorium(t)
        proj.pu_eligible(t)
    proj.crossover_mth()
    proj.payments_expected()


def _compare(s_proj, sec_proj, month, exempt, columns=None):
    """Where SEC's row departs from S's point from S month ``month`` on, in two passes.

    First the frames, ``result_cf`` (over ``columns``, or every column both hold) and
    ``result_pols``, SEC row ``t`` against S row ``t + month``, frames ending together;
    then every cell of S's but ``exempt`` and :data:`RESIDUALS`, at every argument S cached
    inside its frame from ``month`` on, moved onto SEC's clock, S's timing and kind strings
    mapped onto SEC's codes (``uk_sec_support.codes``).  Both to 1e-9 relative with no
    absolute floor (USLIB-SEC-PLAN.md §5.2, T2, precised at M11): a floor of 1e-9 passes an
    error of 1% in any value below 1e-7.  Then the cells of :data:`RESIDUALS` alone, at the
    floor of 1e-9: their exact value is 0, and the computed one moves by an ulp of what it
    closes when an opening state comes back from the CSV one ulp off.  Returns the mismatch
    lines, empty when the row is S's.
    """
    found = []
    for report, keep in (("result_cf", columns), ("result_pols", None)):
        found += [f"{report}: {line}" for line in frame_mismatches(
            s_proj.cells[report](), sec_proj.cells[report](), t_offset=month,
            columns=keep, atol=0.0)]
    found += twin_mismatches(s_proj, sec_proj, t_offset=month, exempt=exempt | RESIDUALS,
                             atol=0.0, codes=codes(sec_proj))
    return found + twin_mismatches(s_proj, sec_proj, t_offset=month,
                                   exempt=exempt | (set(s_proj.cells) - RESIDUALS),
                                   codes=codes(sec_proj))


def _continues_s(s_proj, sec_proj, month):
    """Where a committed row departs from S's point ``s_proj`` from S month ``month`` on.

    The splice's comparison (:func:`_compare`), on the committed model at the shipped
    assumptions: frame by frame, ``result_cf`` and ``result_pols``, then cell by cell over
    every cell of S's but :data:`SPLICE_EXEMPT`.  The shipped 3% expense inflation runs
    from issue in S and from the valuation date here (D7), so :data:`INFLATED`'s two
    columns, and :data:`INFLATION_CELLS`, differ by design and are left out; the inflation
    test holds them.  Improvement ships at 0, where the two clocks agree.  Every other
    column and cell must agree, to 1e-9 relative, with no absolute floor but on the
    residual.
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
    """WOL_UK_SEC read in place, as committed, and swept once, cold; what it met.

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
    """WOL_UK_SEC read in place, as committed, with every point swept (sec_read)."""
    return sec_read[0]


@pytest.fixture(scope="module")
def s_model():
    """WOL_UK_S read in place, as committed, with every point swept.

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
    selects, the core or the full grid (:func:`_selected`), out of this S model, so each
    row opens with the state of the very run it is compared with.  No input table moves
    with ``d``: WOL's two valuation-clock inputs are the ``inflation_rate`` and
    ``mort_improvement`` References.  Every S point is then swept (:func:`_sweep_s`), and
    stays swept; each SEC row is projected by the case that compares it and released once
    compared (:func:`_settle`).
    """
    root = tmp_path_factory.mktemp("spliced")
    s_folder = temp_inputs(root / "s", model_path(TWIN),
                           model_points=_s_table_with_variants())
    s = mx.read_model(s_folder, name=_name("s_spliced"))
    for ref, value in SPLICED_REFS.items():
        setattr(s.Projection, ref, value)
    derived = [(p, d) for kind, p, d in _selected(SPLICES + IN_FORCE_TWINS, CORE_SPLICES)
               if kind == "derived"]
    spec = dataclasses.replace(SPEC, derived=tuple(derived), derived_refs={},
                               future=tuple(_selected(FUTURES, CORE_FUTURES)))
    table, companions = build_sec_table(spec, s)
    assert companions == {}
    sec = mx.read_model(_sec_inputs(root / "sec", table), name=_name("sec_spliced"))
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


def _rule_breaches(proj):
    """R1 and R2's look-ahead on one row, once it has run whole.

    The row's reports and checks are run (:func:`uk_sec_support.sweep`), and then every
    monthly cell at every month of the frame and the month after it, as the C step's sweep
    runs them (:func:`uk_sec_support.full_sweep`): no report of a row need read every
    state, and a base at ``t == 0`` would hide in a cell the reports leave unread
    (USLIB-SEC-PLAN.md §5.2, T2, precised at M4).  ``{"negative": [...], "early": [...],
    "ahead": [...], "raised": [...]}``: every cached call with a negative argument; every
    precedent keyed by a month before ``t_entry()`` of a call keyed by a month at or after
    it; every precedent keyed by a month beyond ``t + 1`` of a call keyed by ``t``, but
    :data:`LOOK_AHEAD`'s, which is empty; and every call the full sweep found raising.  A
    precedent is a call's as modelx's dependency graph records it.
    """
    sweep(proj)
    raised = [f"{name}{args}: {text}" for (name, args), text in full_sweep(proj).items()]
    entry = proj.t_entry()
    negative, early, ahead = [], [], []
    for name, cells in proj.cells.items():
        t_pos = cells.parameters.index("t") if "t" in cells.parameters else None
        for args in _cached_args(cells):
            if any(_month(a) and a < 0 for a in args):
                negative.append(f"{name}{args}")
            if t_pos is None:
                continue
            t = args[t_pos]
            for node in cells.preds(*args):
                params = getattr(node.obj, "parameters", None) or ()
                u = node.args[params.index("t")] if "t" in params else None
                if not _month(u):
                    continue
                if u < entry <= t:
                    early.append(f"{name}{args} -> {node.obj.name}{node.args}")
                if u <= t + 1 or (name, node.obj.name) in LOOK_AHEAD:
                    continue
                ahead.append(f"{name}{args} -> {node.obj.name}{node.args}")
    return {"negative": negative, "early": early, "ahead": ahead, "raised": raised}


def _active(x, t):
    return x.is_active(t)


# What test_the_core_grid_reaches_every_branch asks of the core's rows in the model's own
# values, which no column of the table shows: each holds of some core row, or of a core row
# in some month of its frame.  At the valuation date, every opening-state column in use, a
# count or an amount apart from its issue value, and each kind of valuation month the
# contract's windows make: inside the moratorium, inside the suicide window, after
# cessation and past the crossover.  Later in the frame, every branch and both sides of
# each min and max the full grid reaches: the moratorium and its end, the suicide window,
# an increase, cessation, commission, a conversion, a terminating lapse, a paid-up death,
# the crossover stress and the premiums paid below the cover, the lapse table inside and
# past its last year, the cap on mortality binding and not, the double accidental benefit,
# the payments made capped at cessation, and the limiting age's last month.
AT_VALUATION = {
    "pols_pu_init above 0": lambda x: x.pols_pu_init() > 0.0,
    "pu_benefit_pp_init above 0": lambda x: x.pu_benefit_pp_init() > 0.0,
    "prem_cum_pp_init above 0": lambda x: x.prem_cum_pp_init() > 0.0,
    "cover_pp_init above the sum assured": lambda x: x.cover_pp_init() > x.sum_assured(),
    "premium_pp_init above the premium at issue": lambda x: (
        x.premium_pp_init() > x.premium_mth()),
    "valued inside the moratorium": lambda x: (
        0 < x.duration_mth_init() < x.moratorium_mths()),
    "valued inside the suicide window": lambda x: (
        x.cell() == "UW" and 0 < x.duration_mth_init() < x.suicide_mths),
    "valued once premiums have ceased": lambda x: (
        0 < x.cessation_mths() <= x.duration_mth_init()),
    "valued past the crossover": lambda x: 0 <= x.crossover_mth() < x.duration_mth_init(),
    "crossover_mth_init 0 or more": lambda x: x.crossover_mth_init() >= 0,
    "an escalating point valued once premiums have ceased": lambda x: (
        x.escalation() != "level" and 0 < x.cessation_mths() <= x.duration_mth_init()),
}
IN_FRAME = {
    "the moratorium": lambda x, t: x.in_moratorium(t),
    "the moratorium's end": lambda x, t: (
        _active(x, t) and x.cell() == "O50" and x.duration_mth(t) == x.moratorium_mths()),
    "the suicide window": lambda x, t: (
        _active(x, t) and x.cell() == "UW" and x.duration_mth(t) < x.suicide_mths),
    "an increase": lambda x, t: (
        _active(x, t) and x.esc_cover_step() > 0.0
        and x.duration(t) > x.duration(x.t_entry())),
    "premiums ceasing": lambda x, t: (
        x.cessation_mths() > 0 and x.duration_mth(t) == x.cessation_mths()),
    "commission": lambda x, t: x.commissions(t) > 0.0,
    "a conversion to paid-up": lambda x, t: x.pols_convert(t) > 0.0,
    "a lapse that terminates": lambda x, t: x.pols_lapse(t) > 0.0,
    "a paid-up death": lambda x, t: x.pols_death_pu(t) > 0.0,
    "the crossover stress": lambda x, t: (
        _active(x, t) and x.lapse_rate(t) > x.lapse_rate_base(t)),
    "premiums paid below the cover": lambda x, t: (
        _active(x, t) and x.prem_cum_pp(t) <= x.cover_pp(t)),
    "inside the lapse table": lambda x, t: (
        _active(x, t) and x.policy_year(t) <= x.data.lapse_last_year(x.cell())),
    "past the lapse table's last year": lambda x, t: (
        _active(x, t) and x.policy_year(t) > x.data.lapse_last_year(x.cell())),
    "the mortality cap binding": lambda x, t: x.mort_rate(t) == 1.0,
    "a mortality rate below the cap": lambda x, t: 0.0 < x.mort_rate(t) < 1.0,
    "the double accidental benefit": lambda x, t: (
        _active(x, t) and x.adb_multiplier() > 1.0 and not x.in_moratorium(t)),
    "the payments made capped at cessation": lambda x, t: (
        _active(x, t) and 0 < x.cessation_mths() == x.payments_made(t)
        and x.duration_mth(t) + 1 > x.cessation_mths()),
    "the limiting age's last month": lambda x, t: x.duration_mth(t) == x.limit_mth() - 1,
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
    policy month passed as ``t`` (R1a), as a moratorium, a cessation or a payment count
    read on ``t`` would be.  The frame comparisons read SEC row ``t`` against S row
    ``t + d`` in every column of ``result_cf`` and every column of ``result_pols`` both
    reports hold, and fail frames that end apart.  The cell comparison then evaluates every
    cell of S's but :data:`SPLICE_EXEMPT`, at every argument S cached inside its own frame
    from month ``d`` on, moved onto SEC's clock: the counts on both strands, the paid-up
    cover, the premiums paid, the cover and premium, the benefits, the payments made, the
    rates and the crossover, a policy month, among them.  Each compares to 1e-9 relative
    with no absolute floor, but the roll-forward's residual, which keeps the floor of 1e-9
    (:func:`_compare`).  An S cell this model lacked would fail it.

    The rows past the first conversion are the ones that see the paid-up strand carried in
    at the wrong instant, and the rows past the crossover the premiums paid, which the
    stress reads in every month.  The row is then recorded for the rules test and released
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

    SEC rows ``k ..`` are S rows ``0 ..``, ending together at the limiting age, in
    ``result_cf`` and in every column of ``result_pols`` S's has, and every cell of S's but
    :data:`FUTURE_EXEMPT` agrees at every argument S cached inside its own frame, moved
    ``k`` later.  Each compares as the splice compares, with no absolute floor but on the
    residual (:func:`_compare`).  An S cell this model lacked would fail it.  Before issue
    every column of ``result_cf`` and ``result_pols`` is an exact zero, and the policies
    arrive in month ``k`` as new business.

    The last assertions are R1 and D4's base rule made testable.  After the reports, no read
    keyed by an attained age or a policy year, and no monthly rate, has been evaluated at a
    month before issue (:data:`KEYED_READS`); the annual rates, columns of ``result_pols``,
    are 0.0 there without a read.  A count recursion based at ``t == 0`` rather than at
    ``t_entry()``, or a decrement count that evaluates its rate before asking whether the
    month is in cover, still gives the right numbers.  This is the only test that sees the
    first, and the guard test sees the second too.

    The pre-issue rows are asserted present before they are asserted zero, in both reports:
    a frame that opened at issue would have none, its zeros would hold of nothing, and the
    comparisons with S, which start at issue, would not see it.  The row is then recorded
    for the rules test and released (:func:`_settle`).
    """
    s, sec = spliced
    key = _row_key(sec, "future", s_point, -k)
    s_proj, sec_proj = _point(s, s_point), projection(sec, key)
    try:
        df, pols = sec_proj.result_cf(), sec_proj.result_pols()
        assert _compare(s_proj, sec_proj, -k, FUTURE_EXEMPT) == []
        for report, frame in (("result_cf", df), ("result_pols", pols)):
            assert list(frame.index[:k]) == list(range(k)), report
            assert (frame.loc[:k - 1] == 0.0).all().all(), report
        assert sec_proj.pols_new_biz(k) == sec_proj.policy_count() == 1.0
        early = {name: sorted(args[0] for args in _cached_args(sec_proj.cells[name])
                              if args[0] < k)
                 for name in KEYED_READS}
        assert not any(early.values()), f"read before issue: {early}"
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
    first (:func:`_rule_breaches`), :func:`crossover_mth` among the cells it calls:

    * R1: no cell holds a negative argument.  modelx evaluates one without complaint, and
      a compiled cache raises ``IndexError`` below 0 (USLIB-SEC-PLAN.md F4).  A policy
      month turned into ``t`` by subtracting ``duration_mth_init()`` (R1a) goes negative
      on a point in force past it, as the crossover's search over the policy months would.
    * R1's look-back stops at ``t_entry()``: no cell evaluated at a month from
      ``t_entry()`` on read a month before it.  On a point issued later a recursion based
      at ``t == 0`` reads the pre-issue zeros, so no number shows it and no argument goes
      negative.  The increases counted from ``t_entry()`` read it, the month of entry, and
      no month before.
    * R2's look-ahead: no cell evaluated at month ``t`` read a cell keyed by a month beyond
      ``t + 1``, as modelx's dependency graph records each cached call's precedents; this
      model admits none (:data:`LOOK_AHEAD`).
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
# Data's first reads of its tables.  WOL runs four chains, the full-cover count, the
# paid-up count, the paid-up cover and the premiums paid, each one cell a month; the cover,
# the premium and the improvement are closed forms.  Measured at M5, at the contract's
# longest cover, issued now and 120 months on, with the stress and improvement on: a cold
# net_cf in the last month runs 9 or 10 cells beyond its chain on every shape, the full
# count's head 6, the premiums paid 4, and on the paid-up shape the paid-up cover 10 and
# the paid-up count 11.  Term's 16 (USLIB-SEC-PLAN.md D5).  Any chain of two cells a month
# runs a frame's length beyond.
CHAIN_OVERHEAD = 16

# The contract's longest cover (held by proj_len()): issued at issue_age_min, 18, to the
# limiting age, omega_age, 120, 1,224 months, the same on every shape.
YOUNGEST = 18

# The chains of the model and the cells that head them, called cold in the last month of
# the frame, each on a read of its own: (cell, the timing it takes, or None).  The count,
# the premiums paid and net_cf over them, the deepest call a projection makes, on every
# shape; and on the paid-up shape its two chains.
CHAIN_HEADS = (("net_cf", None), ("pols_if_at", "BEF_NB"), ("prem_cum_pp", None))
PAID_UP_HEADS = (("pols_pu", None), ("pu_benefit", None))

# The shapes the chains run at their longest cover on, by the S point whose twin each is,
# with their heads: the anchor cell, level; the paid-up point, its strand's two chains
# among them; the RPI point, its increases in every year; and the underwritten increasing
# point, paying for life.
CHAIN_SHAPES = ((1, CHAIN_HEADS), (3, CHAIN_HEADS + PAID_UP_HEADS), (4, CHAIN_HEADS),
                (6, CHAIN_HEADS))


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
    """A copy whose table holds each of :data:`CHAIN_SHAPES` at the longest cover, issued
    now and 120 months on, and each row's frame, ``t_entry()`` and heads.

    Each S point's twin, issued at 18, 1,224 months from the limiting age, issued at the
    valuation date and 120 months after it, the shipped ``future_horizon_mth``: frames of
    1,224 and 1,344 months, whose chains stop at ``t_entry()``.  The shipped tables serve
    every age from 18.
    """
    committed = _committed()
    labels = [_label(committed, "twin", p, 0) for p, _ in CHAIN_SHAPES]
    heads = [h for _, h in CHAIN_SHAPES]
    top = committed.index.max()
    rows = committed.loc[labels + labels].assign(entry_age=YOUNGEST)
    later = list(range(top + 1, top + 1 + len(labels)))
    rows = rows.set_axis(labels + later).rename_axis("point_id")
    rows = _set("duration_mth", later, -120)(rows)
    cover = 12 * (120 - YOUNGEST)
    frames = ([(label, cover, 0, h) for label, h in zip(labels, heads)]
              + [(label, cover + 120, 120, h) for label, h in zip(later, heads)])
    return _sec_inputs(tmp_path, rows), frames


# modelx warns as its stack trace starts and stops, which is all the test does with it.
@pytest.mark.filterwarnings("ignore:call stack trace:UserWarning")
def test_every_chain_runs_one_cell_a_month_from_a_cold_start(tmp_path):
    """Called cold, each chain runs one cell a month back to ``t_entry()``, no more.

    No number shows how deep a chain runs, and a compiled model runs it on the C stack, so
    a chain of two cells a month, which gives the same numbers, needs twice the stack on
    every platform (F7); ``WOL_UK_S``'s chains each run one cell a month, but its count
    reaches back to issue.  On a model just read, nothing is cached, so modelx's stack
    trace counts how deep a call runs, against one cell a month back to ``t_entry()`` and
    :data:`CHAIN_OVERHEAD` more, with modelx's recursion limit where the module leaves it:
    each head of :data:`CHAIN_SHAPES` in the last month of the frame, each on a read of its
    own, with :data:`SWITCHED_ON` set, so that the stress reads the premiums paid in every
    month and improvement moves the rates.  On each shape at the contract's longest cover,
    1,224 months from issue age 18, issued now and 120 months on (:func:`_longest_cover`),
    each row's frame asserted first, as §7.5's *Record — M5* and M14's carried rule ask,
    and M1's that every chain runs at its own shape's longest cover.
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
                assert p.proj_len() == months and p.t_entry() == entry, label
                last = p.proj_len() - 1
                args = (last,) if timing is None else (last, _code(p, timing))
                depth, chain = _cold_depth(p, cell, args), last - p.t_entry()
                if not chain <= depth <= chain + CHAIN_OVERHEAD:
                    found.append(f"point {label}: {cell}{args} cold runs {depth} cells "
                                 f"deep, where one cell a month back to t_entry() "
                                 f"{p.t_entry()} is {chain} and {CHAIN_OVERHEAD} more are "
                                 f"allowed")
            finally:
                fresh.close()
    assert not found, found


# ---------------------------------------------------------------------------
# T4 -- the count algebra
#
# BEF_DECR == BEF_NB + pols_new_biz, at every t of every point, is a convention
# (test_new_business_joins_the_count_before_decrements), and is not repeated here.


def test_the_counts_roll_forward_on_both_strands(sec_model):
    """Each strand's count leaves month t by its own outflows, and conversions move
    policies between them.

    On every committed point and at every ``t`` of its frame but the last, to 1e-12: the
    full-cover count weighting month ``t``, ``pols_if_at(t, BEF_DECR)``, less the count it
    carries into ``t + 1``, ``pols_if_at(t + 1, BEF_NB)``, is its deaths, its terminating
    lapses and its conversions to paid-up; the paid-up count, ``pols_pu(t)``, less
    ``pols_pu(t + 1)``, is its deaths less the conversions it takes in.  In every month the
    two together, ``pols_all``, less what they carry into ``t + 1`` before its new business,
    is the deaths on both strands, the terminating lapses and the truncation residual,
    which in the last month before the limiting age takes every survivor, a conversion of
    that month among them.  And the notes' end-of-month count, ``pols_if_at(t,
    AFT_DECR)``, is exactly the count carried into the next month before its new business.

    ``result_pols()`` sets the same movement out row by row, in :data:`RESULT_POLS`'s
    columns, indexed by ``t`` over the frame: ``pols_if`` at ``t + 1`` is ``pols_if`` less
    its outflows at ``t``, plus the new business of ``t + 1``, and ``pols_pu`` at ``t + 1``
    is ``pols_pu`` less its deaths plus the conversions, row 0 opening from
    ``pols_if_init()`` and ``pols_pu_init()``.
    """
    table = sec_model.Data.model_point_table()
    for key, point_id in zip(point_keys(sec_model), table.index):
        p = projection(sec_model, key)
        bef_nb, bef_decr, aft = (_code(p, c) for c in ("BEF_NB", "BEF_DECR", "AFT_DECR"))
        last = p.proj_len() - 1
        for t in range(p.proj_len()):
            carried = p.pols_if_at(t + 1, bef_nb)
            assert p.pols_if_at(t, aft) == carried, (point_id, t)
            out = (p.pols_death(t) + p.pols_death_pu(t) + p.pols_lapse(t)
                   + p.pols_maturity(t))
            moved = p.pols_all(t) - (carried + p.pols_pu(t + 1))
            assert moved == pytest.approx(out, abs=1e-12), (point_id, t)
            if t == last:
                continue
            full = p.pols_death(t) + p.pols_lapse(t) + p.pols_convert(t)
            assert p.pols_if_at(t, bef_decr) - carried == pytest.approx(full, abs=1e-12), (
                point_id, t)
            paid_up = p.pols_death_pu(t) - p.pols_convert(t)
            assert p.pols_pu(t) - p.pols_pu(t + 1) == pytest.approx(paid_up, abs=1e-12), (
                point_id, t)
        pols = p.result_pols()
        assert list(pols.columns) == RESULT_POLS, point_id
        assert pols.index.name == "t" and list(pols.index) == list(range(p.proj_len()))
        full = (pols["pols_if"] - pols[["pols_death", "pols_lapse", "pols_convert"]]
                .sum(axis=1)).shift(1)
        expected = full.fillna(p.pols_if_init()) + pols["pols_new_biz"]
        assert ((pols["pols_if"] - expected).abs() <= 1e-12).all(), point_id
        paid_up = (pols["pols_pu"] - pols["pols_death_pu"] + pols["pols_convert"]).shift(1)
        expected = paid_up.fillna(p.pols_pu_init())
        assert ((pols["pols_pu"] - expected).abs() <= 1e-12).all(), point_id


def test_result_pols_is_s_report_with_the_new_business_beside_it(sec_model, s_model):
    """``result_pols()`` is S's, column for column, with three columns added (D5).

    T1 skips the report as a whole, because its frame has columns S's lacks (the spec's
    exempt), so it is compared here, on every twin, each issued at the valuation date, at
    offset 0.  The SEC report is S's columns in S's order with ``pols_new_biz`` second, the
    paid-up deaths after the full-cover ones and the truncation residual after the
    conversions; every column S's report has agrees, to 1e-9, frames ending together, and
    ``pols_new_biz`` holds the count in the issue month and 0 in every other.  The counts
    and rates carry no inflation, so the shipped assumptions serve.
    """
    table = sec_model.Data.model_point_table()
    twins = table.index[table["row_kind"] == "twin"].tolist()
    assert twins == sorted(s_model.Data.model_point_table().index)
    for point_id in twins:
        p = _point(sec_model, point_id)
        mine, theirs = p.result_pols(), _point(s_model, point_id).result_pols()
        assert [c for c in mine.columns if c in theirs.columns] == list(theirs.columns)
        assert [c for c in mine.columns if c not in theirs.columns] == [
            "pols_new_biz", "pols_death_pu", "pols_maturity"], point_id
        assert list(mine.columns)[:2] == ["pols_if", "pols_new_biz"]
        month = int(table.at[point_id, "source_mth"])
        assert frame_mismatches(theirs, mine, t_offset=month) == [], point_id
        issue = -int(table.at[point_id, "duration_mth"])
        assert list(mine["pols_new_biz"]) == [
            p.policy_count() if t == issue else 0.0 for t in mine.index], point_id


# What T4 multiplies the counts by: not a whole number, because a count of policies need
# not be one, so that a flow which read the count as whole policies would not follow it.
COUNT_FACTOR = 2.5


def test_scaling_the_counts_scales_every_flow_and_no_per_policy_value(tmp_path):
    """The counts are the weights: 2.5 times both, 2.5 times every flow, the same per policy.

    The committed table, and a copy with every ``policy_count`` and every ``pols_pu_init``
    multiplied by :data:`COUNT_FACTOR` together, are each read with :data:`SWITCHED_ON` set
    before either computes anything: every assumption that ships at zero, on, so that every
    flow is nonzero on some point, the stress moves the lapses and the conversions past the
    crossover, and improvement moves the rates.  On every point ``result_cf`` and the counts
    of ``result_pols`` are 2.5 times the committed table's, element by element, to 1e-12
    relative: a scaled count is a computed float, which may come back from the CSV within
    two ulps (``uk_sec_support``'s module docstring).  ``result_pols``'s per-policy columns
    are the committed table's exactly.  So is every other cell of :data:`COUNTED`, at every
    argument the sweep of the committed table's point cached: the counts at each timing and
    the claims of each kind, which no report shows, among them, and the roll-forward's
    residual, a rounding about 0 on that many policies, to the residual's floor of 1e-9.
    And every cell outside :data:`COUNTED` (the premiums paid, the cover, the premium, the
    benefits, the payments made, the rates, both clocks, the flags) agrees bit for bit at
    every argument that sweep cached.  So a flow that dropped a count, or read it as whole
    policies, which a table of counts of 1 hides from every comparison with S and a count
    doubled hides here, fails (USLIB-SEC-PLAN.md §5.2, T4, precised at M11).  Each counted
    cell but the residual is nonzero on some point, the paid-up ones on the committed
    paid-up rows.  A paid-up flow weighted by the full-cover count scales with both counts
    alike, so this test cannot see it: the month-on restatement, which moves one count and
    not the other, does.
    """
    table = _committed()
    base = mx.read_model(_sec_inputs(tmp_path / "base", table), name=_name("counted"))
    scaled = mx.read_model(_sec_inputs(tmp_path / "scaled", table.assign(
        policy_count=COUNT_FACTOR * table["policy_count"],
        pols_pu_init=COUNT_FACTOR * table["pols_pu_init"])), name=_name("scaled"))
    reports = ("result_cf", "result_pols")
    counted = sorted(COUNTED - set(reports))
    nonzero = set()
    try:
        for model in (base, scaled):
            for ref, value in SWITCHED_ON.items():
                setattr(model.Projection, ref, value)
        for key, scaled_key in zip(point_keys(base), point_keys(scaled)):
            one, many = projection(base, key), projection(scaled, scaled_key)
            sweep(one)
            for report in reports:
                b, d = one.cells[report](), many.cells[report]()
                assert d.index.equals(b.index) and list(d.columns) == list(b.columns)
                flows = [c for c in b.columns if c not in PER_POLICY_POLS]
                want = COUNT_FACTOR * b[flows]
                bad = ((d[flows] - want).abs() > 1e-12 * want.abs()).any()
                assert not bad.any(), (key, report, list(bad[bad].index))
                fixed = [c for c in b.columns if c in PER_POLICY_POLS]
                assert d[fixed].equals(b[fixed]), (key, report)
            for name in counted:
                floor = 1e-9 if name in RESIDUALS else 0.0
                for args in _cached_args(one.cells[name]):
                    want = COUNT_FACTOR * one.cells[name](*args)
                    got = many.cells[name](*args)
                    assert abs(got - want) <= floor + 1e-12 * abs(want), (
                        key, name, args, got, want)
                    if want != 0.0 and name not in RESIDUALS:
                        nonzero.add(name)
            assert twin_mismatches(one, many, exempt=TWIN_EXEMPT_DEFAULT | COUNTED,
                                   rtol=0.0, atol=0.0) == []
            _release(base, key)
            _release(scaled, scaled_key)
    finally:
        scaled.close()
        base.close()
    want = set(counted) - RESIDUALS
    assert want <= nonzero, f"0 on every point: {sorted(want - nonzero)}"


def test_a_point_restated_a_month_on_continues_its_own_flows(tmp_path):
    """The counts a point carries into a month are the counts that weight its flows (T4).

    Scaling every count alike, as the test above does, cannot see a flow weighted by the
    count a point opened with, ``policy_count()`` or ``pols_pu_init()``, rather than the
    count in force in its month: both move by the same factor.  So each point in force on
    the committed table is restated a month on, opened with what this model carries into
    its month 1: the full-cover count, ``pols_if_at(1, "BEF_NB")``; the paid-up count,
    ``pols_pu(1)``, and its cover per paid-up policy, ``pu_benefit(1) / pols_pu(1)``; the
    premiums paid, ``prem_cum_pp(0)``; the cover, ``cover_pp(1)``; and the premium,
    ``premium_pp(1)``, or once the premiums have ceased by month 1 the last one paid; and
    the crossover, if it fell in month 0 or before.  The
    restatement must continue the point's own frames, its row ``t`` the point's row
    ``t + 1``, in ``result_cf`` and ``result_pols``, every flow among them, to 1e-9
    relative, floored at 1e-9 for what a state read back from the CSV an ulp off moves
    about 0.  The point valued in its first policy year continues its commission.  Both
    models run at an inflation rate of 0, set on each as it is read (K7): the restatement
    moves the valuation date a month on, and expense inflation, on the valuation clock,
    would step a month apart by design (D7), as improvement would, which ships at 0.  The
    restatement also shows the opening state complete on this model's own states, as the
    splice shows it on S's.
    """
    table = _committed()
    model = mx.read_model(_sec_inputs(tmp_path / "base", table), name=_name("month_on"))
    model.Projection.inflation_rate = 0.0
    rows, pairs = [], []
    try:
        top = table.index.max()
        for label in table.index[table["duration_mth"] > 0]:
            p = _point(model, label)
            if p.proj_len() < 2:
                continue
            cessation, d = p.cessation_mths(), p.duration_mth_init()
            crossover = p.crossover_mth()
            premium = (p.premium_pp(1) if cessation <= 0 or d + 1 < cessation
                       else p.premium_pp(0) if d + 1 == cessation else p.premium_pp_init())
            paid_up = p.pols_pu(1)
            top += 1
            row = table.loc[[label]].assign(
                duration_mth=p.duration_mth(1),
                policy_count=p.pols_if_at(1, _code(p, "BEF_NB")),
                pols_pu_init=paid_up,
                pu_benefit_pp_init=p.pu_benefit(1) / paid_up if paid_up > 0 else 0.0,
                prem_cum_pp_init=p.prem_cum_pp(0), cover_pp_init=p.cover_pp(1),
                premium_pp_init=premium,
                crossover_mth_init=crossover if 0 <= crossover <= d else -1)
            row.index = pd.Index([top], name="point_id")
            rows.append(row)
            pairs.append((label, top))
        frames = {label: {report: _point(model, label).cells[report]()
                          for report in ("result_cf", "result_pols")}
                  for label, _ in pairs}
    finally:
        model.close()
    first_year = [label for label, _ in pairs
                  if (frames[label]["result_cf"]["commissions"] > 0.0).any()]
    assert first_year, "no restated point pays commission"
    restated = mx.read_model(_sec_inputs(tmp_path / "on", pd.concat([table, *rows])),
                             name=_name("month_on"))
    restated.Projection.inflation_rate = 0.0
    found = []
    try:
        for label, moved in pairs:
            p = _point(restated, moved)
            for report, frame in frames[label].items():
                found += [f"point {label} restated as {moved}, {report}: {line}"
                          for line in frame_mismatches(frame, p.cells[report](),
                                                       t_offset=1)]
    finally:
        restated.close()
    assert not found, found[:20]


def test_the_roll_forward_closes_on_ten_million_policies(tmp_path):
    """``check_pols_roll_fwd`` scales its tolerance with the policies on the books, and
    closes at 1e7.

    A residual is rounding on that many policies, so the check holds it to 1e-10 times
    ``max(policy_count() + pols_pu_init(), 1)``, where its tolerance unscaled would be
    1e-10: at the counts the other tests use, one policy or less, the two are one.
    ``WOL_UK_S`` scales by ``pols_if_init()``, which here is 0 on a point issued at the
    valuation date, the count entering as new business, and which leaves out the paid-up
    strand, whose policies the residual rounds on too.  So every committed point is
    projected from a copy where each counts ten million policies on each strand it holds:
    the check closes on each, and the largest residual on every point exceeds the unscaled
    1e-10, so the scaling is what closes it (USLIB-SEC-PLAN.md §5.2, T4, precised at M10).
    The point paid-up entirely, whose ``policy_count`` is 0, closes on its paid-up count
    alone, which a tolerance scaled by the full-cover count would leave at 1e-10.  At a
    million policies the largest residuals are about 1e-10, and the paid-up point's
    5.7e-11, which an unscaled tolerance would pass.
    """
    table = _committed()
    table = table.assign(policy_count=1e7 * (table["policy_count"] > 0),
                         pols_pu_init=1e7 * (table["pols_pu_init"] > 0))
    model = mx.read_model(_sec_inputs(tmp_path, table), name=_name("ten_million"))
    least, paid_up_only = math.inf, 0.0
    try:
        for key, point_id in zip(point_keys(model), table.index):
            p = projection(model, key)
            assert p.check_pols_roll_fwd() and p.check_truncation(), point_id
            largest = max(abs(p.check_pols_roll_fwd_resid(t)) for t in range(p.proj_len()))
            least = min(least, largest)
            if p.policy_count() == 0.0 and p.pols_pu_init() > 0.0:
                paid_up_only = max(paid_up_only, largest)
            _release(model, key)
    finally:
        model.close()
    assert least > 1e-10, least
    assert paid_up_only > 1e-10, paid_up_only


# ---------------------------------------------------------------------------
# T5 -- validation
#
# Each malformed table is the committed one with one fault.  The checks run over the whole
# table as it is read, in Data, and the message names the file it read and the column or
# every point at fault.  A blank cell reads as NaN, and so does a text cell once the checks
# coerce the column to numbers, so each is refused as a count, a duration or a state that
# is not a number.  The repeated point_id holds another policy under the same label, as a
# bad extract would, so that the check must look at the labels and not at whole rows.  The
# point_ids are the committed table's: 1 to 7 the twins of S's points; 8, the anchor cell
# at 6, inside its moratorium; 9, the anchor cell at 166; 10, the paid-up point at 200; 11,
# the RPI point at 186; 12, the underwritten increasing point at 12; 13, the male smoker at
# 300; 14, the RPI point issued 13 months on; 15, the RPI point at 120 under an RPI of 5%;
# 16, the underwritten increasing point at 120 under a take-up of a half; 17, the paid-up
# point at 180 paid-up entirely.  A {file} in a message is the table's filename: every case
# is read by one model, from a file of its own (the malformed fixture).


def _drop(column):
    return lambda table: table.drop(columns=column)


_NOT_YET = "on a policy not yet in force, duration_mth 0 or less; it is not at point_id"
_FIRST_YEAR = ("on a policy in force fewer than 12 months, before its first anniversary; "
               "it is not at point_id")
_EARLIEST = ("before the first policy month a converted policy can be in force at, half "
             "of cessation_months, rounded up; it is not at point_id")
_CROSS_WHOLE = ("{file}: crossover_mth_init must be a whole number of months, -1 or more, "
                "below 2**53; it is not at point_id ")
_CROSS_MONTH = ("{file}: crossover_mth_init must be -1, or a premium-paying policy month "
                "before the valuation date, below duration_mth and cessation_months; it is "
                "not at point_id ")
_CROSS_LEVEL = ("{file}: crossover_mth_init must be the month the contract puts the "
                "crossover in on a level point, the whole number of premiums the sum assured "
                "holds, to the cent; it is not at point_id ")
_PAID_LEVEL = ("{file}: prem_cum_pp_init must be premium_mth times the premiums due, "
               "min(duration_mth, cessation_months), to the cent, on a level point; it is "
               "not at point_id [8]")
_PAID_ESCALATING = ("{file}: prem_cum_pp_init must lie between premium_mth and "
                    "premium_pp_init times the premiums due, min(duration_mth, "
                    "cessation_months), to the cent, on an escalating point; it is not at "
                    "point_id [11]")
_PU_COVER = ("{file}: pu_benefit_pp_init must lie between sum_assured times the payments a "
             "conversion needs, half of cessation_months rounded up, and cover_pp_init times "
             "the payments made, min(duration_mth, cessation_months), each over "
             "cessation_months, to the cent, where paid-up policies are in force; it is not "
             "at point_id [10]")

MALFORMED = [
    ("a negative count", _set("policy_count", [8], -0.1),
     "{file}: policy_count must be a number, zero or more; it is not at point_id [8]"),
    ("a blank count", _set("policy_count", [9], float("nan")),
     "{file}: policy_count must be a number, zero or more; it is not at point_id [9]"),
    ("two bad counts", _set("policy_count", [8, 10], -1.0),
     "{file}: policy_count must be a number, zero or more; it is not at point_id [8, 10]"),
    ("a text count", _set("policy_count", [11], "abc"),
     "{file}: policy_count must be a number, zero or more; it is not at point_id [11]"),
    ("an infinite count", _set("policy_count", [11], float("inf")),
     "{file}: policy_count must be a number, zero or more; it is not at point_id [11]"),
    ("a fractional duration", _set("duration_mth", [9], 166.5),
     "{file}: duration_mth must be a whole number of months; it is not at point_id [9]"),
    ("a blank duration", _set("duration_mth", [14], float("nan")),
     "{file}: duration_mth must be a whole number of months; it is not at point_id [14]"),
    ("a text duration", _set("duration_mth", [11], "x4"),
     "{file}: duration_mth must be a whole number of months; it is not at point_id [11]"),
    # numpy casts a float past int64 to the least int64, a policy issued 2**63 months on,
    # without a word: the table refuses it first.
    ("a duration past int64", _set("duration_mth", [8], 1e19),
     "{file}: duration_mth must be below 2**53 months; it is not at point_id [8]"),
    ("durations of 2**53 months at two points", _set("duration_mth", [8, 10], 2.0 ** 53),
     "{file}: duration_mth must be below 2**53 months; it is not at point_id [8, 10]"),
    ("issued beyond the horizon", _set("duration_mth", [14], -121),
     "{file}: duration_mth must be -120 or more, a policy issued at most 120 months after "
     "the valuation date; it is not at point_id [14]"),
    *[(f"no {column} column", _drop(column), f"{{file}} has no {column} column")
      for column in ("policy_count", "duration_mth", *STATE)],
    ("a repeated point_id",
     lambda t: pd.concat([t, t.loc[[8]].assign(policy_id="WOL-900099")]),
     "{file}: point_id [8] appears more than once"),
    ("a negative paid-up count", _set("pols_pu_init", [10], -0.01),
     "{file}: pols_pu_init must be a number, zero or more; it is not at point_id [10]"),
    ("a blank paid-up count", _set("pols_pu_init", [17], float("nan")),
     "{file}: pols_pu_init must be a number, zero or more; it is not at point_id [17]"),
    ("an infinite paid-up count", _set("pols_pu_init", [10], float("inf")),
     "{file}: pols_pu_init must be a number, zero or more; it is not at point_id [10]"),
    ("a negative paid-up cover", _set("pu_benefit_pp_init", [10], -1.0),
     "{file}: pu_benefit_pp_init must be a number, zero or more; it is not at point_id "
     "[10]"),
    ("a text paid-up cover", _set("pu_benefit_pp_init", [17], "x"),
     "{file}: pu_benefit_pp_init must be a number, zero or more; it is not at point_id "
     "[17]"),
    ("negative premiums paid", _set("prem_cum_pp_init", [9], -30.0),
     "{file}: prem_cum_pp_init must be a number, zero or more; it is not at point_id [9]"),
    ("blank premiums paid", _set("prem_cum_pp_init", [13], float("nan")),
     "{file}: prem_cum_pp_init must be a number, zero or more; it is not at point_id [13]"),
    ("an infinite cover", _set("cover_pp_init", [11], float("inf")),
     "{file}: cover_pp_init must be a number, zero or more; it is not at point_id [11]"),
    ("a blank cover", _set("cover_pp_init", [12], float("nan")),
     "{file}: cover_pp_init must be a number, zero or more; it is not at point_id [12]"),
    ("a negative premium", _set("premium_pp_init", [15], -1.0),
     "{file}: premium_pp_init must be a number, zero or more; it is not at point_id [15]"),
    ("a text premium", _set("premium_pp_init", [16], "high"),
     "{file}: premium_pp_init must be a number, zero or more; it is not at point_id [16]"),
    ("a blank flag", _set("variant_paid_up", [3], float("nan")),
     "{file}: variant_paid_up must be True or False; it is not at point_id [3]"),
    ("a flag written yes", _set("variant_adb_2x", [2], "yes"),
     "{file}: variant_adb_2x must be True or False; it is not at point_id [2]"),
    ("a flag written 1", _set("variant_adb_2x", [1], 1),
     "{file}: variant_adb_2x must be True or False; it is not at point_id [1]"),
    ("an unknown cell", _set("cell", [1], "O60"),
     "{file}: cell must be O50 or UW; it is not at point_id [1]"),
    ("an unknown escalation", _set("escalation", [4], "indexed"),
     "{file}: escalation must be level or fixed_5pct or rpi; it is not at point_id [4]"),
    ("an unknown sex", _set("sex", [2], "X"),
     "{file}: sex must be M or F; it is not at point_id [2]"),
    ("term assurance's smoker code", _set("smoker", [3], "N"),
     "{file}: smoker must be NS or S; it is not at point_id [3]"),
    ("a blank entry age", _set("entry_age", [1], float("nan")),
     "{file}: entry_age must be a finite number; it is not at point_id [1]"),
    ("an infinite entry age", _set("entry_age", [5], float("inf")),
     "{file}: entry_age must be a finite number; it is not at point_id [5]"),
    ("a text entry age", _set("entry_age", [7], "x65"),
     "{file}: entry_age must be a finite number; it is not at point_id [7]"),
    ("a negative sum assured", _set("sum_assured", [1], -1.0),
     "{file}: sum_assured must be a number, zero or more; it is not at point_id [1]"),
    ("a text premium at issue", _set("premium_mth", [2], "30 pounds"),
     "{file}: premium_mth must be a number, zero or more; it is not at point_id [2]"),
    ("an infinite premium at issue", _set("premium_mth", [6], float("inf")),
     "{file}: premium_mth must be a number, zero or more; it is not at point_id [6]"),
    ("a fractional cessation", _set("cessation_months", [1], 240.5),
     "{file}: cessation_months must be a whole number of months, 0 or more, below 2**53; "
     "it is not at point_id [1]"),
    ("a negative cessation", _set("cessation_months", [5], -12),
     "{file}: cessation_months must be a whole number of months, 0 or more, below 2**53; "
     "it is not at point_id [5]"),
    ("a blank moratorium", _set("moratorium_months", [7], float("nan")),
     "{file}: moratorium_months must be a whole number of months, 0 or more, below 2**53; "
     "it is not at point_id [7]"),
    ("a moratorium of 2**53 months", _set("moratorium_months", [2], 2.0 ** 53),
     "{file}: moratorium_months must be a whole number of months, 0 or more, below 2**53; "
     "it is not at point_id [2]"),
    ("the paid-up value without a cessation date", _set("cessation_months", [3], 0),
     "{file}: a pro-rata paid-up point must have a premium cessation date, "
     "cessation_months above 0, which the paid-up value is measured to; it is not at "
     "point_id [3]"),
    ("a paid-up count on new business", _set("pols_pu_init", [3], 0.1),
     f"{{file}}: pols_pu_init must be 0 {_NOT_YET} [3]"),
    ("a paid-up cover on future business", _set("pu_benefit_pp_init", [14], 2500.0),
     f"{{file}}: pu_benefit_pp_init must be 0 {_NOT_YET} [14]"),
    ("premiums paid on new business", _set("prem_cum_pp_init", [1], 30.0),
     f"{{file}}: prem_cum_pp_init must be 0 {_NOT_YET} [1]"),
    ("a cover on new business", _set("cover_pp_init", [4], 5150.0),
     f"{{file}}: cover_pp_init must be the sum assured {_NOT_YET} [4]"),
    ("a premium on future business", _set("premium_pp_init", [14], 31.35),
     f"{{file}}: premium_pp_init must be the premium at issue {_NOT_YET} [14]"),
    # No anniversary has passed in a policy's first twelve months: the RPI point at 186,
    # moved back into its first policy year with its increases, and the anchor cell inside
    # its moratorium given an increase.
    ("a cover in the first policy year", _set("duration_mth", [11], 11),
     f"{{file}}: cover_pp_init must be the sum assured {_FIRST_YEAR} [11]"),
    ("a premium in the first policy year", _set("premium_pp_init", [8], 31.0),
     f"{{file}}: premium_pp_init must be the premium at issue {_FIRST_YEAR} [8]"),
    ("a level cover moved", _set("cover_pp_init", [9], 5100.0),
     "{file}: cover_pp_init must be the sum assured on a level point, which never "
     "escalates; it is not at point_id [9]"),
    ("a level premium moved", _set("premium_pp_init", [13], 46.0),
     "{file}: premium_pp_init must be the premium at issue on a level point, which never "
     "escalates; it is not at point_id [13]"),
    ("an escalated cover below the sum assured", _set("cover_pp_init", [11], 4999.0),
     "{file}: cover_pp_init must be the sum assured or more on an escalating point, each "
     "increase being floored at 0; it is not at point_id [11]"),
    ("an escalated premium below the premium at issue", _set("premium_pp_init", [12], 100.0),
     "{file}: premium_pp_init must be the premium at issue or more on an escalating point, "
     "each increase being floored at 0; it is not at point_id [12]"),
    ("a paid-up count without the variant", _set("pols_pu_init", [9], 0.1),
     "{file}: pols_pu_init must be 0 on a point without the pro-rata paid-up variant; it "
     "is not at point_id [9]"),
    ("a paid-up cover without the variant", _set("pu_benefit_pp_init", [13], 5000.0),
     "{file}: pu_benefit_pp_init must be 0 on a point without the pro-rata paid-up "
     "variant; it is not at point_id [13]"),
    # The first conversion is at the end of policy month 119, when the 120th of 240
    # payments has been made, so a paid-up policy is first in force at 120: the paid-up
    # point moved to 119 with its strand, and with its count gone but its cover left.
    ("a paid-up count before the first conversion", _set("duration_mth", [10], 119),
     f"{{file}}: pols_pu_init must be 0 {_EARLIEST} [10]"),
    ("a paid-up cover before the first conversion",
     _then(_set("duration_mth", [10], 119), _set("pols_pu_init", [10], 0.0)),
     f"{{file}}: pu_benefit_pp_init must be 0 {_EARLIEST} [10]"),
    ("a paid-up cover on no paid-up policy", _set("pols_pu_init", [10], 0.0),
     "{file}: pu_benefit_pp_init must be 0 where no paid-up policy is in force, "
     "pols_pu_init 0; it is not at point_id [10]"),
    # The first year's history at its first month: an increase a month after issue.
    ("a cover a month after issue",
     _then(_set("duration_mth", [14], 1), _set("cover_pp_init", [14], 5150.0)),
     f"{{file}}: cover_pp_init must be the sum assured {_FIRST_YEAR} [14]"),
    # The earliest paid-up month on an odd cessation: 239 months, half of which rounded up
    # is 120, so a strand at 119 is one no conversion can have made, where half rounded
    # down would admit it.
    ("a paid-up count at half an odd cessation rounded down",
     _then(_set("cessation_months", [10], 239), _set("duration_mth", [10], 119)),
     f"{{file}}: pols_pu_init must be 0 {_EARLIEST} [10]"),
    ("a crossover not whole", _set("crossover_mth_init", [10], 166.5), _CROSS_WHOLE + "[10]"),
    ("a crossover below -1", _set("crossover_mth_init", [11], -2), _CROSS_WHOLE + "[11]"),
    ("a blank crossover", _set("crossover_mth_init", [13], float("nan")),
     _CROSS_WHOLE + "[13]"),
    ("a crossover on new business", _set("crossover_mth_init", [1], 166),
     "{file}: crossover_mth_init must be -1 on a policy not yet in force, duration_mth 0 "
     "or less; it is not at point_id [1]"),
    ("a crossover in the valuation month", _set("crossover_mth_init", [9], 166),
     _CROSS_MONTH + "[9]"),
    ("a crossover after cessation",
     _then(_set("duration_mth", [13], 310), _set("crossover_mth_init", [13], 305)),
     _CROSS_MONTH + "[13]"),
    ("premiums paid past the cover with no crossover",
     _set("crossover_mth_init", [10], -1),
     "{file}: crossover_mth_init must not be -1 where the premiums paid exceed the cover, "
     "prem_cum_pp_init above cover_pp_init, to the cent: they crossed it before the "
     "valuation date; it is not at point_id [10]"),
    ("a level crossover a month early", _set("crossover_mth_init", [10], 165),
     _CROSS_LEVEL + "[10]"),
    ("a level crossover a month late", _set("crossover_mth_init", [10], 167),
     _CROSS_LEVEL + "[10]"),
    # The premiums paid: the review's refund of 1,000,030 on a 5,000 policy, and each
    # bound a cent outside.
    ("a million paid on a level point", _set("prem_cum_pp_init", [8], 1e6), _PAID_LEVEL),
    ("a cent short of the level premiums", _set("prem_cum_pp_init", [8], 179.99),
     _PAID_LEVEL),
    ("a cent past the level premiums", _set("prem_cum_pp_init", [8], 180.01), _PAID_LEVEL),
    ("a cent short of the premiums at issue", _set("prem_cum_pp_init", [11], 5579.99),
     _PAID_ESCALATING),
    ("a cent past the latest premium", lambda t: _set(
        "prem_cum_pp_init", [11], t.at[11, "premium_pp_init"] * 186 + 0.01)(t),
     _PAID_ESCALATING),
    # The paid-up cover: the review's 0 and 1e7 beside paid-up policies, and each bound a
    # cent outside, 5,000 x 120 / 240 and 5,000 x 200 / 240.
    ("no paid-up cover beside paid-up policies", _set("pu_benefit_pp_init", [10], 0.0),
     _PU_COVER),
    ("a paid-up cover of 1e7", _set("pu_benefit_pp_init", [10], 1e7), _PU_COVER),
    ("a cent short of the paid-up cover", _set("pu_benefit_pp_init", [10], 2499.99),
     _PU_COVER),
    ("a cent past the paid-up cover",
     _set("pu_benefit_pp_init", [10], 5000.0 * 200 / 240 + 0.01), _PU_COVER),
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


def _relabelled(message, relabel):
    """``message`` with every ``point_id [...]`` list it holds relabelled by ``relabel``."""
    def labels(match):
        return "point_id [" + ", ".join(str(relabel[int(p)]) for p in
                                        match.group(1).split(", ")) + "]"
    return re.sub(r"point_id \[(\d+(?:, \d+)*)\]", labels, message)


@pytest.fixture(scope="module")
def malformed_extract(tmp_path_factory):
    """:data:`MALFORMED`'s tables as an extract labels its rows, each a file of its own.

    Each case's table is the committed one with its fault, made by its own labels, and
    then relabelled :data:`EXTRACT_LABELS`, in order, so that no label is its position
    plus one.  One model reads them all, as :func:`malformed` reads its files.  Returns
    ``(model, {case: filename}, {committed label: extract label})``.
    """
    root = tmp_path_factory.mktemp("malformed_extract")
    relabel = dict(zip(_committed().index, EXTRACT_LABELS))
    files = {}
    for number, (case, edit, _) in enumerate(MALFORMED):
        files[case] = f"extract_{number:02d}_sec.csv"
        table = edit(_committed()).rename(index=relabel)
        temp_inputs(root, model_path(SEC), model_points=table, model_point_file=files[case])
    model = mx.read_model(root / SEC, name=_name("malformed_extract"))
    yield model, files, relabel
    model.close()


@pytest.mark.parametrize("case, edit, message", MALFORMED, ids=[c[0] for c in MALFORMED])
def test_a_malformed_row_of_an_extract_is_refused_naming_its_label(malformed_extract, case,
                                                                    edit, message):
    """Each refusal names the extract's labels, never the rows' positions (T5).

    The committed labels are their positions plus one, so a check that named a row by its
    place in the table, ``idx + 1``, would pass every case of :data:`MALFORMED`.  On the
    extract each label is another, and each case's message names the extract's.
    """
    model, files, relabel = malformed_extract
    model.Data.model_point_file = files[case]
    _refused(model.Data.model_point_table,
             _relabelled(message, relabel).format(file=files[case]))


def test_the_future_horizon_is_a_reference_that_bounds_future_business(tmp_path):
    """``Data.future_horizon_mth`` refuses a policy issued later than it, and 0 refuses all.

    The committed table's one future point is issued 13 months on.  It reads at the shipped
    120 months and at 13, the shortest horizon that admits it, and is refused at 12, by
    name.  At 0 the model takes no future new business, D4's fallback for a product that
    cannot support it, and the message says so.  A horizon that is not a whole number of
    months, 0 or more, below ``2**53``, is itself refused, a NaN and an infinity among
    them: either would admit every policy.  A whole number written as a float, ``13.0``,
    reads as 13 does, and ``2**53 - 1``, the largest whole number the compiled model holds
    exactly, reads; ``2**53`` does not.  Setting the Reference clears the table, so each
    value is read afresh.
    """
    future = _label(_committed(), "future", 4, -13)
    later = (f"{TABLE}: duration_mth must be -12 or more, a policy issued at most 12 months "
             f"after the valuation date; it is not at point_id [{future}]")
    no_future = (f"{TABLE}: duration_mth must be 0 or more: this model takes no future new "
                 f"business; it is not at point_id [{future}]")
    model = mx.read_model(_sec_inputs(tmp_path, _committed()), name=_name("horizon"))
    try:
        assert model.Data.future_horizon_mth == 120
        off = ("future_horizon_mth must be a whole number of months, 0 or more, below "
               "2**53, not {}")
        for horizon, refusal in ((13, None), (12, later), (0, no_future), (13.0, None),
                                 *((h, off.format(h)) for h in (
                                     -1, 12.5, math.nan, math.inf, -math.inf, WHOLE)),
                                 (WHOLE - 1, None), (120, None)):
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


def _moved_on(label, months):
    """An edit that moves the anchor cell's row ``label`` on to policy month ``months``,
    past its cessation at 240, with the history the move gives it: 240 premiums of 30
    paid, and its crossover at 166, so that ``Data`` reads it."""
    return _then(_set("duration_mth", [label], months),
                 _set("prem_cum_pp_init", [label], 30.0 * 240),
                 _set("crossover_mth_init", [label], 166))


def test_a_point_past_the_limiting_age_is_refused_by_proj_len(tmp_path):
    """A point at or past the limiting age has no frame, and ``proj_len()`` refuses it.

    The anchor cell at its crossover month is moved on to ``duration_mth`` 600, the policy
    month it reaches ``omega_age``, 120, from entry at 70, on the policy clock.  That is a
    rule of the product, not of the table: it needs the limiting age, a Reference, and the
    entry age the point's own columns give, read where the frame is defined, so the table
    reads, and the point is refused on its first projection, rather than projecting
    nothing.  A loop over the block would meet the point only when it reached it, after
    projecting the points before it, so ``run_sec.py --block``, run beside the table, asks
    every point for its frame first: it fails naming the point, and prints nothing before.
    And one month earlier, 599, the last month before the limiting age, projects one month.
    """
    moved = _label(_committed(), "derived", 1, 166)
    model = _read_edited(tmp_path, _moved_on(moved, 600))
    message = (f"point_id {moved}: duration_mth 600 is at or past the limiting age, policy "
               f"month 600, omega_age 120")
    try:
        assert len(model.Data.model_point_table()) == len(_committed())
        _refused(_point(model, moved).result_cf, message)
    finally:
        model.close()
    model = _read_edited(tmp_path / "last", _moved_on(moved, 599))
    try:
        assert len(_point(model, moved).result_cf()) == 1
    finally:
        model.close()
    runner = tmp_path / "run_sec.py"
    shutil.copy(model_path(SEC).parent / "run_sec.py", runner)
    done = _run_sec(runner, "--block", check=False)
    assert done.returncode != 0 and done.stdout == b""
    assert message in done.stderr.decode(errors="replace")


# What the contract does not issue, refused by proj_len() as a point past the limiting age
# is, as (case, the table's edit, the References set, the point, the message, and the
# frame the point projects at the shipped References, or None).  Data reads an entry age as
# WOL_UK_S does, so each reads.  The product issues from 18, the mortality table's first
# age, and the frame runs to omega_age, 120; the compiled caches will be sized from both.
# Each bound is refused just inside it here, and accepted at it in the edges test.  And
# each bound, moved past a committed twin, refuses it, which at the shipped bound projects
# its frame: the Reference is what refuses it.  Point 1 is the anchor cell, issued at 70;
# point 5 the underwritten one, at 40.
NOT_ISSUED = [
    ("an issue age of 17", _set("entry_age", [5], 17), {}, 5,
     "point_id 5: the issue age, 17, is below issue_age_min, 18", None),
    ("an issue age below a bound raised to 41", None, {"issue_age_min": 41}, 5,
     "point_id 5: the issue age, 40, is below issue_age_min, 41", 960),
    ("an issue age of 120", _set("entry_age", [1], 120), {}, 1,
     "point_id 1: the issue age, 120, is at or past omega_age, 120: the policy has no cover",
     None),
    ("an issue age at a limiting age lowered to 70", None, {"omega_age": 70}, 1,
     "point_id 1: the issue age, 70, is at or past omega_age, 70: the policy has no cover",
     600),
]


@pytest.mark.parametrize("case, edit, refs, point, message, frame", NOT_ISSUED,
                         ids=[c[0] for c in NOT_ISSUED])
def test_a_point_the_contract_does_not_issue_is_refused_by_proj_len(tmp_path, case, edit,
                                                                    refs, point, message,
                                                                    frame):
    """``proj_len()`` refuses a point outside the contract's bounds, naming it (§6.4).

    ``WOL_UK_S`` projects any entry age from any age its tables reach, and so would modelx
    here, but the contract does not write it, and the compiled model's caches will be sized
    from the contract: a frame of at most 102 years and the horizon, attained ages from 18
    to 119.  So the frame refuses such a point, naming it, as it refuses a point past the
    limiting age, and every report with it (:data:`NOT_ISSUED`): each bound just inside it,
    and each bound moved past a committed twin, which projects at the shipped bound, on a
    model read afresh.  A bound off by one, or a refusal lost, lets a point through.  The
    table reads either way.  Every Reference is set on a model just read, before its
    projection computes anything (K7).
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


# Each Reference proj_len() holds to a domain, as (case, the References set, the message
# where refused, or None where the twin of S point 1 projects).  NaN and the infinities are
# outside every domain.  WOL_UK_S reads the mortality loadings and improvement inside the
# cap's min, which reads an infinity as certain death; the RPI through a max and a min,
# max(rpi, 0.0) then the cover cap, which read an infinity as no increase or the cap; each
# cap as a bound written second, which a NaN cap is lost through; the stress through a
# comparison with 0, which a NaN switches off, and through the lapse rate's min, its bound
# first, which reads an infinity as a certain lapse; and the shares, the take-up, the
# expenses and commission as weights, which below 0 or past 1 make a negative benefit,
# expense or rate.  Each is refused at the nearest value outside each edge of its domain,
# and accepted at the edge itself: the largest finite float an edge of each domain
# unbounded above, -1 inflation's and 1 improvement's.  issue_age_min, suicide_mths and
# omega_age are whole numbers below 2**53, which the compiled model holds as long long,
# printed through int() once whole: each is refused at a fraction and at exactly 2**53, and
# its largest whole number accepted, or refused by a later rule.
BIG = 1.7976931348623157e308
WHOLE = 2.0 ** 53
BELOW_0 = math.nextafter(0.0, -1.0)
ABOVE_1 = math.nextafter(1.0, 2.0)


def _domain(ref, rule, accepted, refused, printed=float):
    """The DOMAINS cases of ``ref`` alone: each of ``accepted`` projects, each of
    ``refused`` is refused by the domain's ``rule``, and NaN and the infinities by it
    too."""
    message = f"point_id 1: {ref} must be {rule}, not {{}}"
    cases = [(f"{ref}={value!r}", {ref: value}, None) for value in accepted]
    cases += [(f"{ref}={value!r}", {ref: value}, message.format(printed(value)))
              for value in refused]
    return cases + [(f"{ref}={value!r}", {ref: value}, message.format(float(value)))
                    for value in (math.nan, math.inf, -math.inf)]


def _whole_domain(ref, accepted, below=True):
    """The DOMAINS cases of an integer Reference: a whole number below 2**53, and 0 or
    more where ``below``, printed through int() once whole."""
    whole = f"point_id 1: {ref} must be a whole number below 2**53, not {{}}"
    cases = [(f"{ref}={value!r}", {ref: value}, None) for value in accepted]
    if below:
        cases.append((f"{ref}=-1", {ref: -1}, f"point_id 1: {ref} must be 0 or more, not -1"))
    return cases + [(f"{ref}={value!r}", {ref: value}, whole.format(float(value)))
                    for value in (0.5, 120.5, WHOLE, 1e300, math.nan, math.inf, -math.inf)]


_FINITE_0 = ("a finite number, 0 or more", (0.0, BIG), (BELOW_0,))
_SHARE = ("a number from 0 to 1", (0.0, 1.0), (BELOW_0, ABOVE_1))
OMEGA = ("point_id 1: omega_age must be above issue_age_min, 18, and at most 121, a year "
         "past mort_table.csv's last age, not {}")
DOMAINS = [
    *_domain("mort_loading_o50", *_FINITE_0),
    *_domain("mort_loading_uw", *_FINITE_0),
    *_domain("mort_improvement", "a finite number, 1 or less", (-BIG, 1.0), (ABOVE_1,)),
    *_domain("acc_share", *_SHARE),
    *_domain("suicide_share", *_SHARE),
    *_whole_domain("suicide_mths", (0, WHOLE - 1)),
    *_domain("rpi_rate", "a finite number", (-BIG, BIG), ()),
    *_domain("esc_rpi_cover_cap", *_FINITE_0),
    *_domain("esc_rpi_prem_mult", *_FINITE_0),
    *_domain("esc_rpi_prem_cap", *_FINITE_0),
    *_domain("esc_fixed_cover", *_FINITE_0),
    *_domain("esc_fixed_prem", *_FINITE_0),
    *_domain("esc_take_up", *_SHARE),
    *_domain("lapse_crossover_beta", *_FINITE_0),
    *_domain("inflation_rate", "a finite number, -1 or more", (-1.0, BIG),
             (math.nextafter(-1.0, -2.0),)),
    *_domain("expense_acq_o50", *_FINITE_0),
    *_domain("expense_acq_uw", *_FINITE_0),
    *_domain("expense_maint_o50", *_FINITE_0),
    *_domain("expense_maint_uw", *_FINITE_0),
    *_domain("comm_init_rate", *_FINITE_0),
    *_whole_domain("issue_age_min", (0,)),
    ("issue_age_min=2**53-1", {"issue_age_min": WHOLE - 1},
     f"point_id 1: the issue age, 70, is below issue_age_min, {int(WHOLE - 1)}"),
    *_whole_domain("omega_age", (120, 121, 120.0), below=False),
    ("omega_age=122", {"omega_age": 122}, OMEGA.format(122)),
    ("omega_age=18", {"omega_age": 18}, OMEGA.format(18)),
    ("omega_age=19", {"omega_age": 19},
     "point_id 1: the issue age, 70, is at or past omega_age, 19: the policy has no cover"),
    ("omega_age=2**53-1", {"omega_age": WHOLE - 1}, OMEGA.format(int(WHOLE - 1))),
]


@pytest.mark.parametrize("case, refs, message", DOMAINS, ids=[c[0] for c in DOMAINS])
def test_each_reference_is_held_to_its_domain_at_both_edges(case, refs, message):
    """``proj_len()`` holds each Reference to its domain, NaN and the infinities outside it.

    ``WOL_UK_S`` checks none of them, and off its domain each projects a negative rate,
    benefit or expense, a factor that changes sign each year, or a NaN that a comparison
    loses, every check passing: a NaN cover cap is lost through its ``min``, a NaN stress
    switches itself off, a NaN suicide window closes, and a NaN limiting age switches off
    every comparison with it, the limiting age sizing every frame.  The frame refuses each
    such Reference, by name, before it projects anything, and every report with it, at the
    nearest value outside each edge of its domain, and accepts the edge itself
    (:data:`DOMAINS`): the integer References at a fraction and at exactly ``2**53``, and
    ``omega_age`` past the mortality table's last age.  Each Reference is refused on every
    point, whether or not the point's cell reads it, as a model-wide assumption.  Each case
    sets its References on a model just read (K7).
    """
    model = mx.read_model(model_path(SEC), name=_name("domain"))
    try:
        for ref, value in refs.items():
            setattr(model.Projection, ref, value)
        p = _row(model, "twin", 1, 0)
        if message is None:
            assert p.proj_len() > 0
        else:
            _refused(p.result_cf, message)
    finally:
        model.close()


# A value that leaves the floats, from an opening state and References each in its domain,
# as (case, the table's edit, the References set, the point, the call, a report that reads
# it, the start of the message).  The RPI row at 186 opened on a cover or a premium near
# the largest float, which its next anniversary's increase takes past it at t = 6, and on
# premiums paid at it, which month 0's premium, opened at 1e306, takes past it at t = 0: a
# premium of a few pounds would round back to the largest float.  Then the review's
# expenses, an expense of 1.7e308 inflated at 100% a year, past the floats at t = 48; a
# commission rate of 1e308; a commission and an expense each just inside the floats, whose
# sum, the net cash flow, is not; a count of 1e307 paying 30 a month; a count of 1e300
# with a cover of 1e300, whose claims leave the floats; a paid-up count and cover of 1e300
# and 6e299, whose summed paid-up cover does; and the double accidental benefit on a cover
# of 1e308, from the first anniversary.  Each is refused in the cell where it first is,
# naming the point, the month and what makes it.
NET = 1.7e308
PAST_THE_FLOATS = [
    ("a cover", _set("cover_pp_init", [11], 1.79e308), {}, 11, ("cover_pp", 6),
     "result_cf",
     "point_id 11: the cover cover_pp(6) is inf, not a finite number, from cover_pp_init "
     "1.79e+308 and an annual increase of 0.03"),
    ("a premium", _set("premium_pp_init", [11], 1.79e308), {}, 11, ("premium_pp", 6),
     "result_cf",
     "point_id 11: the premium premium_pp(6) is inf, not a finite number, from "
     "premium_pp_init 1.79e+308 and an annual increase of 0.045"),
    ("premiums paid",
     _then(_set("prem_cum_pp_init", [11], BIG), _set("premium_pp_init", [11], 1e306)), {},
     11, ("prem_cum_pp", 0), "result_pols",
     "point_id 11: the premiums paid prem_cum_pp(0) are inf, not a finite number, from "
     "prem_cum_pp_init 1.7976931348623157e+308"),
    ("the expenses", None, {"expense_maint_o50": NET, "inflation_rate": 1.0}, 1,
     ("expenses", 48), "result_cf",
     "point_id 1: the expenses expenses(48) are inf, not a finite number, from "
     "expense_acq_o50 150.0, expense_maint_o50 1.7e+308 and inflation_rate 1.0, on "
     "pols_all(48) "),
    ("the commission", None, {"comm_init_rate": 1e308}, 1, ("commissions", 0), "result_cf",
     "point_id 1: the commission commissions(0) is inf, not a finite number, from "
     "comm_init_rate 1e+308 on premiums(0) 30.0"),
    ("the net cash flow", None, {"comm_init_rate": NET / 30, "expense_acq_o50": NET}, 1,
     ("net_cf", 0), "result_cf",
     "point_id 1: the net cash flow net_cf(0) is -inf, not a finite number, from premiums "
     "30.0, claims "),
    ("the premiums", _set("policy_count", [1], 1e307), {}, 1, ("premiums", 0), "result_cf",
     "point_id 1: the premiums premiums(0) are inf, not a finite number, from premium_pp(0) "
     "30.0 on pols_if(0) 1e+307 policies"),
    ("the claims",
     _then(_set("policy_count", [1], 1e300), _set("sum_assured", [1], 1e300),
           _set("cover_pp_init", [1], 1e300)), {}, 1, ("claims", 0, "DEATH"), "result_cf",
     "point_id 1: the claims claims(0, DEATH) are inf, not a finite number, from "
     "pols_death(0) "),
    ("the paid-up cover",
     _then(_set("sum_assured", [10], 1e300), _set("cover_pp_init", [10], 1e300),
           _set("pols_pu_init", [10], 1e300), _set("pu_benefit_pp_init", [10], 6e299),
           _set("crossover_mth_init", [10], -1)), {}, 10, ("pu_benefit", 0), "result_cf",
     "point_id 10: the paid-up cover pu_benefit(0) is inf, not a finite number, from "
     "pols_pu_init 1e+300 paid-up policies at pu_benefit_pp_init 6e+299"),
    ("a benefit",
     _then(_set("sum_assured", [2], 1e308), _set("cover_pp_init", [2], 1e308)), {}, 2,
     ("benefit_pp", 12, "ACC"), "result_cf",
     "point_id 2: the benefit benefit_pp(12, ACC) is inf, not a finite number, from the "
     "cover cover_pp(12) 1e+308"),
]


@pytest.mark.parametrize("case, edit, refs, point, call, report, message", PAST_THE_FLOATS,
                         ids=[c[0] for c in PAST_THE_FLOATS])
def test_a_value_past_the_floats_is_refused_where_it_first_is(tmp_path, case, edit, refs,
                                                              point, call, report, message):
    """A value past the largest float is refused in the cell where it first is.

    ``Data`` and ``proj_len()`` hold each opening amount, count and Reference to a finite
    number, so a value near the largest float reads; an increase, a premium, a count, an
    inflation rate or a sum then takes a value the projection computes past the floats,
    where ``WOL_UK_S`` would pay an infinite claim, charge an infinite expense or compare
    an infinite total, every report infinite and its checks NaN or passing.  The cell where
    the value first leaves the floats refuses it, naming the point, the month and what makes
    it (:data:`PAST_THE_FLOATS`), and so does a report that reads it first: ``result_cf``,
    or ``result_pols`` for the premiums paid, which no cash flow reads on that point at the
    shipped References (USLIB-SEC-PLAN.md §7.1, *Record — M1*; UKLIB-SEC-PLAN.md §6.6,
    *Carried into M10 and after*).  The month before projects.  Each Reference is set on a
    model just read (K7).
    """
    model = _read_edited(tmp_path, edit or (lambda t: t))
    try:
        for ref, value in refs.items():
            setattr(model.Projection, ref, value)
        p = _point(model, point)
        name, t, *rest = call
        if t > 0:
            p.cells[name](t - 1, *rest)
        _refused(lambda: p.cells[name](t, *rest), message)
        _refused(p.cells[report], message)
    finally:
        model.close()


# A step to the policy years that overflows the floats, from a Reference in its domain, as
# (case, the References set, the S point whose twin is read, the call): each of the five
# powers the projection raises, the cover's and the premium's steps, the inflation and
# improvement factors and the crossover's search.  A step of 1e200 squares past the floats
# at the second anniversary, t = 24.
OVERFLOWING_POWERS = [
    ("the cover's step", {"esc_fixed_cover": 1e200}, 6, ("cover_pp", 24)),
    ("the premium's step", {"esc_fixed_prem": 1e200}, 6, ("premium_pp", 24)),
    ("the inflation factor", {"inflation_rate": 1e200}, 1, ("inflation_factor", 24)),
    ("the improvement factor", {"mort_improvement": -1e200}, 1, ("mort_improve_factor", 24)),
    ("the crossover's search", {"esc_fixed_cover": 1e200}, 6, ("crossover_mth",)),
]


@pytest.mark.parametrize("case, refs, s_point, call", OVERFLOWING_POWERS,
                         ids=[c[0] for c in OVERFLOWING_POWERS])
def test_an_overflowing_power_raises_python_s_overflow_error(case, refs, s_point, call):
    """A power that leaves the floats raises ``OverflowError``, as Python raises it.

    The cells check what they compute, but a ``**`` whose result passes the largest float
    raises before the cell can look at it: modelx runs the formula as Python does, and
    Python's float power raises ``OverflowError`` with the platform's own message,
    ``os.strerror(errno.ERANGE)``, "Numerical result out of range" on Linux, rather than
    return an infinity.  So a step to the policy years at a Reference in its domain but large
    enough, 1e200, is refused, not projected, though the refusal names neither the point nor
    the Reference (:data:`OVERFLOWING_POWERS`).  The compiled model's ``pow`` returns an
    infinity there, so its C step takes uslib's M22 form, Python's own float power where
    the compiled one gives an infinity, so that both engines raise this error.  Each
    Reference is set on a model just read (K7).
    """
    model = mx.read_model(model_path(SEC), name=_name("power"))
    try:
        for ref, value in refs.items():
            setattr(model.Projection, ref, value)
        p = _row(model, "twin", s_point, 0)
        name, *args = call
        with pytest.raises(Exception) as excinfo:
            p.cells[name](*args)
        text = str(excinfo.value)
        assert "OverflowError" in text and os.strerror(errno.ERANGE) in text, text
    finally:
        model.close()


def test_a_whole_limit_written_as_a_float_projects_as_the_int_does():
    """``omega_age = 120.0`` projects what 120 projects, cell for cell (§6.4).

    ``proj_len()`` holds ``omega_age``, ``issue_age_min`` and ``suicide_mths`` to whole
    numbers, which ``120.0``, ``18.0`` and ``12.0`` are, and reads ``omega_age`` as the
    ``int`` it is: a float limit would make ``proj_len()`` the float 600.0, on which every
    report's ``range`` raises ``TypeError``, where the compiled model, typing the Reference
    ``long long``, would project.  So with the three set as floats, on a model just read,
    the twins of S's anchor and underwritten points, the paid-up point in force and the RPI
    point issued later are what the shipped model makes of them in every cell, bit for bit,
    each integer cell an ``int`` in both.
    """
    floats = mx.read_model(model_path(SEC), name=_name("floats"))
    ints = mx.read_model(model_path(SEC), name=_name("ints"))
    try:
        floats.Projection.omega_age = 120.0
        floats.Projection.issue_age_min = 18.0
        floats.Projection.suicide_mths = 12.0
        for case in (("twin", 1, 0), ("twin", 5, 0), ("derived", 3, 200), ("future", 4, -13)):
            mine, theirs = _row(floats, *case), _row(ints, *case)
            sweep(theirs)
            assert twin_mismatches(theirs, mine, exempt=frozenset(), rtol=0.0,
                                   atol=0.0) == [], case
            for name in ("proj_len", "limit_mth", "t_entry", "duration_mth_init"):
                assert type(mine.cells[name]()) is int, (case, name)
    finally:
        ints.close()
        floats.close()


def test_the_edges_of_the_in_force_interface_are_accepted(sec_model, tmp_path):
    """A zero count, whole numbers in any type, the horizon and each bound's edge are read.

    A count of 0 is a point that projects zeros, and a point paid-up entirely, its full
    cover count 0 and its paid-up strand in force, projects the strand alone: the committed
    row read under a stress of its own.  ``166.0`` is a whole number of months, read back as
    the int the policy clock counts in; a policy issued 120 months after the valuation date,
    the shipped ``future_horizon_mth``, is the last one the table admits, with a frame of
    720 months.  The paid-up point valued at 120, the first policy month a converted policy
    can be in force at, holds its strand.  An escalated cover and premium at the issue
    values, an RPI of 0 since issue, are read; and so is a level point valued after its
    premiums ceased, its premium the last one paid.  And each bound of the contract at its
    edge projects: issue at 18, 1,224 months to the limiting age, and issue at 119, 12
    months.  Then the history's bounds, each at its edge (``Data``'s rules 16 and 17): the
    premiums paid on an escalating point at the premium at issue and at the latest premium
    times the premiums due; on a level point a third of a cent past the premiums due, an
    extract rounded to the cent; the paid-up cover at the sum assured's share at the first
    conversion and at today's cover's share of the payments made; and an odd cessation, 239
    months, at its first paid-up month, 120, where the two shares meet.  The extra rows are
    copies of committed rows under labels of their own, 21 to 29.
    """
    committed = _committed()
    crossover = _label(committed, "derived", 1, 166)
    future = _label(committed, "future", 4, -13)
    paid_up = _label(committed, "derived", 3, 200)
    rpi = _label(committed, "derived", 4, 186)
    entire = _label(committed, "derived", 3, 180)
    ceased = _label(committed, "derived", 7, 300)
    latest = committed.at[rpi, "premium_pp_init"] * 186
    copies = {21: (paid_up, {"duration_mth": 120, "prem_cum_pp_init": 3600.0,
                             "pu_benefit_pp_init": 2500.0, "crossover_mth_init": -1}),
              22: (rpi, {"cover_pp_init": 5000.0, "premium_pp_init": 30.0,
                         "prem_cum_pp_init": 5580.0, "crossover_mth_init": 166}),
              23: (crossover, {"entry_age": 119, "duration_mth": 0, "prem_cum_pp_init": 0.0}),
              24: (rpi, {"prem_cum_pp_init": 5580.0}),
              25: (rpi, {"prem_cum_pp_init": latest}),
              26: (paid_up, {"pu_benefit_pp_init": 2500.0}),
              27: (paid_up, {"pu_benefit_pp_init": 5000.0 * 200 / 240}),
              28: (paid_up, {"cessation_months": 239, "duration_mth": 120,
                             "prem_cum_pp_init": 3600.0,
                             "pu_benefit_pp_init": 5000.0 * 120 / 239,
                             "crossover_mth_init": -1}),
              29: (_label(committed, "derived", 1, 6), {"prem_cum_pp_init": 180.004})}

    def edit(table):
        extra = []
        for label, (source, changes) in copies.items():
            row = table.loc[[source]].assign(policy_id=f"WOL-9000{label}", **changes)
            row.index = pd.Index([label], name="point_id")
            extra.append(row)
        table = pd.concat([table, *extra])
        table = _set("policy_count", [crossover], 0.0)(table)
        table = table.assign(duration_mth=table["duration_mth"].astype(float))
        table = _set("duration_mth", [future], -120.0)(table)
        table = _set("entry_age", [5], 18)(table)
        return table

    model = _read_edited(tmp_path, edit)
    try:
        read = model.Data.model_point_table()
        assert read["duration_mth"].dtype == float
        df = _point(model, crossover).result_cf()
        assert len(df) == 434 and (df == 0.0).all().all()
        p = _point(model, entire)
        assert (p.policy_count(), p.duration_mth(0)) == (0.0, 180)
        assert type(p.duration_mth(0)) is int
        pols = p.result_cf()
        assert (pols["pols_if"] == 0.0).all() and (pols["premiums"] == 0.0).all()
        assert pols["pols_pu"].iloc[0] == p.pols_pu_init() > 0.0
        assert (pols["claims_death_pu"] > 0.0).any() and p.check_pols_roll_fwd()
        late = _point(model, future)
        assert (late.t_entry(), late.proj_len(), late.pols_new_biz(120)) == (120, 720, 1.0)
        first = _point(model, 21)
        assert first.pols_pu(0) == first.pols_pu_init() > 0.0
        assert len(first.result_cf()) == first.proj_len() == 480
        flat = _point(model, 22)
        assert flat.cover_pp(0) == 5000.0 and flat.premium_pp(0) == 30.0
        assert flat.cover_pp(6) == pytest.approx(5150.0, rel=1e-12)
        last = _point(model, 23)
        assert len(last.result_cf()) == last.proj_len() == 12
        old = _point(model, ceased)
        assert old.premium_pp_init() == 45.0 and old.premium_pp(0) == 0.0
        assert len(old.result_cf()) == 360
        young = _point(model, 5)
        assert len(young.result_cf()) == young.proj_len() == 1224
        assert young.check_pols_roll_fwd() and young.check_truncation()
        for label in (24, 25):
            edge = _point(model, label)
            assert edge.prem_cum_pp(0) == edge.prem_cum_pp_init() + edge.premium_pp(0)
        assert _point(model, 25).prem_cum_pp_init() == latest
        for label in (26, 27, 28):
            edge = _point(model, label)
            assert edge.pu_benefit(0) == edge.pols_pu_init() * edge.pu_benefit_pp_init()
            assert edge.pols_pu(0) > 0.0 and edge.proj_len() > 0
        odd = _point(model, 28)
        assert (odd.cessation_mths(), odd.duration_mth(0)) == (239, 120)
        refund = _point(model, 29)
        assert refund.benefit_pp(0, _code(refund, "NON_ACC")) == 180.004 + 30.0
    finally:
        model.close()


def _every_state_months(start, end, cessation):
    """The S months a point whose S frame runs from ``start`` to ``end`` is restated at.

    By default the edges of its windows (USLIB-SEC-PLAN.md §5.2, T5): every month of the
    first policy year and the first anniversary, through which the moratorium, the suicide
    window and ``Data``'s first-year rule end, each anniversary and the month before it,
    which takes in the first conversion at half the payments and cessation, each month of
    the year the crossover falls in on any S point, and the last month of the frame.  With
    ``UKLIB_SEC_FULL=1``, every month.  Each after ``start``, the twin's month.
    """
    if SEC_FULL:
        return list(range(start + 1, end))
    months = {*range(1, 14), end - 1, *(m for a in range(12, end, 12) for m in (a - 1, a)),
              *range(160, 192), *range(636, 648), *range(216, 228)}
    if cessation > 0:
        months |= {cessation // 2 - 1, cessation // 2, -(-cessation // 2)}
    return sorted(m for m in months if start < m < end)


def _states(s):
    """Each ``(S point, month)`` of :func:`_every_state_months` on every point of ``s``."""
    table = s.Data.model_point_table()
    return [(point_id, d) for key, point_id in zip(point_keys(s), table.index)
            for d in _every_state_months(0, projection(s, key).proj_len(),
                                         int(table.at[point_id, "cessation_months"]))]


def _restated(root, s, states):
    """The twins of ``s``'s points and a row in force at each of ``states``, ``(S point,
    month)``, built by the generator out of ``s`` into a copy of the product directory:
    ``(folder, table)``."""
    spec = dataclasses.replace(SPEC, derived=tuple(states), future=(), derived_refs={})
    table, _ = build_sec_table(spec, s)
    return _sec_inputs(root, table), table


def _states_apart(a, b):
    """The state columns, the counts among them, in which two tables of :func:`_restated`
    differ on the states, ``(S policy, month)``, they share, of which there must be some."""
    both = a.index.intersection(b.index)
    assert len(both), "the two tables share no state"
    return {c for c in ("policy_count", *STATE) if (a.loc[both, c] != b.loc[both, c]).any()}


def _refused_in_force(folder, refs):
    """What ``Data`` and ``proj_len()`` refuse of the table in ``folder``, read with
    ``refs`` set first: ``Data``'s refusal, or each row's ``proj_len()``'s, each by the line
    that names it.  Each row is released once asked (:func:`_release`)."""
    model = mx.read_model(folder, name=_name("every"))
    try:
        for ref, value in refs.items():
            setattr(model.Projection, ref, value)
        try:
            model.Data.model_point_table()
        except Exception as err:                # reported, with the rows' states
            return [f"Data: {_raised(err)}"]
        refused = []
        for key in point_keys(model):
            try:
                projection(model, key).proj_len()
            except Exception as err:            # reported, so every row is asked
                refused.append(_raised(err))
            _release(model, key)
        return refused
    finally:
        model.close()


# The stress that lapses every policy past its crossover, as the committed row paid-up
# entirely is read under: S reaches a full-cover count of 0 with paid-up policies in force
# under it, and under no other set of inputs.
LAPSE_ALL = {**SPLICED_REFS, "lapse_crossover_beta": 100.0}

# The other inputs that move the states S reaches, each moving the cover, the premium, the
# premiums paid and the crossover of an escalating point: an RPI of 8%, under which the
# RPI point's premiums rise faster and it crosses at 201, and a take-up of a half, under
# which both escalating points take half their increases.
RPI_SET = {"rpi_rate": 0.08}
TAKE_UP_SET = {"esc_take_up": 0.5}
ESCALATED = {"cover_pp_init", "premium_pp_init", "prem_cum_pp_init", "crossover_mth_init"}


def test_every_state_s_reaches_is_accepted_in_force(s_model, spliced, tmp_path):
    """Every state ``WOL_UK_S`` reaches is a valid opening state (T5).

    ``Data``'s rules and ``proj_len()``'s hold an opening state to what a policy in force
    can be, so they must accept each state the S model reaches: a rule exercised only on
    the rows the other tests choose could refuse a state S reaches elsewhere (D6).  So each
    point of S is restated in force by the generator at the edges of its windows, or with
    ``UKLIB_SEC_FULL=1`` at every month of its frame (:func:`_every_state_months`), into
    one table beside the twins: ``Data`` reads it, and no row's ``proj_len()`` refuses it
    (USLIB-SEC-PLAN.md §5.2, T5, precised at M10).  The splice's stress moves three of the
    states S reaches: the full-cover count, the paid-up count and the paid-up cover per
    policy, through the stressed lapses and conversions past the crossover.  It leaves
    alone the premiums paid, the cover, the premium and the crossover, which per policy no
    decrement moves.  A stress that lapses every policy moves the counts to a full-cover
    count of 0 with paid-up policies in force, which no other set reaches.  The RPI and the
    take-up move the other four on an escalating point: its cover, its premium, its
    premiums paid and its crossover.  Expense inflation and improvement move no state, each
    at 0 or on the valuation clock.  So the test runs on each set of inputs on which those
    states differ (precised at M9), and asserts which states each moves:

    * S as shipped, its seven points under its own References, as T1 and the committed rows
      read it (``s_model``);
    * the splice's, its points and five variants under :data:`SPLICED_REFS`, the stress
      on (``spliced``), an odd cessation among them;
    * the stress that lapses every policy, :data:`LAPSE_ALL`, on S's points, whose paid-up
      point is paid-up entirely from policy month 167;
    * an RPI of 8%, :data:`RPI_SET`, on S's points, the RPI point crossing at 201;
    * a take-up of a half, :data:`TAKE_UP_SET`, on S's points, both escalating points
      taking half their increases.

    ``WOL_UK_SEC`` refuses no state ``WOL_UK_S`` reaches, so none is set aside.
    """
    extra = {"lapse_all": LAPSE_ALL, "rpi": RPI_SET, "take_up": TAKE_UP_SET}
    read = {tag: mx.read_model(model_path(TWIN), name=_name(tag)) for tag in extra}
    try:
        for tag, refs in extra.items():
            for ref, value in refs.items():
                setattr(read[tag].Projection, ref, value)
        sets = {"shipped": (s_model, {}), "spliced": (spliced[0], SPLICED_REFS),
                **{tag: (read[tag], refs) for tag, refs in extra.items()}}
        found, states = {}, {}
        for tag, (s, refs) in sets.items():
            reached = _states(s)
            folder, rows = _restated(tmp_path / tag, s, reached)
            assert len(rows) == len(s.Data.model_point_table()) + len(reached)
            states[tag] = rows.set_index(["source_policy_id", "source_mth"])
            refused = _refused_in_force(folder, refs)
            if refused:
                found[tag] = f"{len(refused)} refused, first: {refused[:5]}"
    finally:
        for model in read.values():
            model.close()
    assert not found, found
    shipped, every = states["shipped"], states["lapse_all"]
    apart = _states_apart(shipped, states["spliced"])
    assert apart == {"policy_count", "pols_pu_init", "pu_benefit_pp_init"}, apart
    entire = every[(every["policy_count"] == 0.0) & (every["pols_pu_init"] > 0.0)]
    assert len(entire), "no state paid-up entirely"
    for tag in ("rpi", "take_up"):
        apart = _states_apart(shipped, states[tag])
        assert apart == ESCALATED, (tag, apart)


# ---------------------------------------------------------------------------
# The assumption tables
#
# Data checks each table before a value of it is read, in the cell the projection takes
# its extent from, reading the file as it stands (UKLIB-SEC-PLAN.md §4; USLIB-SEC-PLAN.md
# §7.1, *Precised at M3*, item 9).  Each case is the shipped tables with one fault, read
# from a copy, refused by its Data cell alone, naming the file, the column and its lines,
# the header line 1, and through a projection of the anchor cell, which reads both tables.
# The lines are the shipped files': mort_table.csv holds each basis, sex and smoker group at
# ages 18 to 120, 103 lines a group, assured F NS on lines 2 to 104, then assured F S,
# assured M NS, assured M S, population F NS from line 414, population F S, population M NS
# and population M S on lines 723 to 825; lapse_table.csv O50's policy years 1 to 6 on
# lines 2 to 7 and UW's on lines 8 to 13.


def _written(column, value, where):
    """An edit of a table that writes ``value`` into ``column`` on the rows ``where``
    picks."""
    def edit(table):
        cells = table[column].astype(object)
        cells[where(table)] = value
        return table.assign(**{column: cells})
    return edit


def _rate_at(basis, sex, smoker, age):
    return lambda t: ((t["basis"] == basis) & (t["sex"] == sex) & (t["smoker"] == smoker)
                      & (t["age"] == age))


def _group(basis, sex, smoker):
    return lambda t: (t["basis"] == basis) & (t["sex"] == sex) & (t["smoker"] == smoker)


def _year(cell, year):
    return lambda t: (t["cell"] == cell) & (t["policy_year"] == year)


def _dropped(where):
    return lambda table: table[~where(table)].reset_index(drop=True)


def _repeated(where):
    return lambda table: pd.concat([table, table[where(table)]], ignore_index=True)


MORT = "mort_table.csv"
LAPSE = "lapse_table.csv"
RATE = f"{MORT}: mort_rate must be a number from 0 to 1; it is not on line "
AGES = (f"{MORT}: the ages of each basis, sex and smoker status must run from 18 to 120, "
        f"the table's first and last, one row an age, none below 0; ")
LAPSE_RATE = f"{LAPSE}: lapse_rate must be a number from 0 to 1; it is not on line "
YEARS = (f"{LAPSE}: the policy years of each cell must run from 1, one row a year, without a "
         f"gap or a repeat; ")

# A table a reader cannot read, or whose value is not a number in its range, as (case, the
# file, its edit, the Data cell that refuses it, its message).  A value no point reads is
# refused too: the assured female smoker's rates, which no committed point reaches.
UNREADABLE = [
    ("a blank rate", MORT, _written("mort_rate", float("nan"),
                                    _rate_at("population", "F", "NS", 70)),
     "mort_age_first", RATE + "[466]"),
    ("a text rate", MORT, _written("mort_rate", "low", _rate_at("assured", "F", "S", 50)),
     "mort_age_first", RATE + "[137]"),
    ("an infinite rate", MORT, _written("mort_rate", float("inf"),
                                        _rate_at("assured", "M", "NS", 40)),
     "mort_age_first", RATE + "[230]"),
    ("a negative rate", MORT, _written("mort_rate", -0.001,
                                       _rate_at("population", "M", "S", 65)),
     "mort_age_first", RATE + "[770]"),
    ("a rate past 1", MORT, _written("mort_rate", 1.5, _rate_at("assured", "F", "NS", 100)),
     "mort_age_first", RATE + "[84]"),
    ("two lines at fault", MORT, _then(
        _written("mort_rate", float("nan"), _rate_at("assured", "F", "NS", 18)),
        _written("mort_rate", float("nan"), _rate_at("population", "M", "S", 120))),
     "mort_age_first", RATE + "[2, 825]"),
    ("an age not whole", MORT, _written("age", 45.5, _rate_at("assured", "M", "S", 45)),
     "mort_age_first", f"{MORT}: age must be a whole number; it is not on line [338]"),
    ("an age written as text", MORT, _written("age", "x", _rate_at("population", "F", "S", 18)),
     "mort_age_first", f"{MORT}: age must be a whole number; it is not on line [517]"),
    ("an unknown basis", MORT, _written("basis", "select", _rate_at("assured", "F", "NS", 20)),
     "mort_age_first", f"{MORT}: basis must be population or assured, sex M or F, and "
                       f"smoker NS or S; they are not on line [4]"),
    ("term assurance's smoker code", MORT,
     _written("smoker", "N", _rate_at("population", "M", "NS", 30)),
     "mort_age_first", f"{MORT}: basis must be population or assured, sex M or F, and "
                       f"smoker NS or S; they are not on line [632]"),
    ("an age twice", MORT, _repeated(_rate_at("assured", "M", "NS", 60)), "mort_age_first",
     AGES + "basis assured, sex M, smoker NS, age 60 repeats on lines [250, 826]"),
    ("a group missing", MORT, _dropped(_group("population", "M", "S")), "mort_age_first",
     AGES + "no line holds basis population, sex M, smoker S, ages 18 to 120"),
    ("a gap in a group", MORT, _dropped(_rate_at("assured", "F", "S", 80)), "mort_age_first",
     AGES + "no line holds basis assured, sex F, smoker S, age 80"),
    ("an age below 0", MORT, _written("age", -1, _rate_at("assured", "F", "NS", 18)),
     "mort_age_first", AGES + "age -1, below 0, is on lines [2]; no line holds basis "
                              "assured, sex F, smoker NS, age 18"),
    ("a blank lapse rate", LAPSE, _written("lapse_rate", float("nan"), _year("O50", 3)),
     "lapse_last_year", LAPSE_RATE + "[4]"),
    ("a lapse rate past 1", LAPSE, _written("lapse_rate", 1.5, _year("UW", 6)),
     "lapse_last_year", LAPSE_RATE + "[13]"),
    ("a negative lapse rate", LAPSE, _written("lapse_rate", -0.1, _year("O50", 1)),
     "lapse_last_year", LAPSE_RATE + "[2]"),
    ("a text lapse rate", LAPSE, _written("lapse_rate", "high", _year("UW", 2)),
     "lapse_last_year", LAPSE_RATE + "[9]"),
    ("a policy year not whole", LAPSE, _written("policy_year", 2.5, _year("O50", 2)),
     "lapse_last_year", f"{LAPSE}: policy_year must be a whole number; it is not on line [3]"),
    ("an unknown cell", LAPSE, _written("cell", "O60", _year("UW", 1)),
     "lapse_last_year", f"{LAPSE}: cell must be O50 or UW; it is not on line [8]"),
    ("a policy year missing", LAPSE, _dropped(_year("O50", 3)), "lapse_last_year",
     YEARS + "no line holds cell O50, policy_year 3"),
    ("a policy year twice", LAPSE, _repeated(_year("UW", 4)), "lapse_last_year",
     YEARS + "cell UW, policy_year 4 repeats on lines [11, 14]"),
    ("no policy year 1", LAPSE, _dropped(_year("O50", 1)), "lapse_last_year",
     YEARS + "no line holds cell O50, policy_year 1"),
    ("a cell missing", LAPSE, _dropped(lambda t: t["cell"] == "UW"), "lapse_last_year",
     YEARS + "no line holds cell UW, policy_year 1"),
]


@pytest.mark.parametrize("case, file, edit, cell, message", UNREADABLE,
                         ids=[c[0] for c in UNREADABLE])
def test_a_table_a_reader_cannot_read_is_refused_naming_its_lines(tmp_path, case, file, edit,
                                                                  cell, message):
    """``Data`` refuses an assumption table before a value of it is read (§4, T5).

    ``WOL_UK_S`` reads a blank rate as NaN, which its cap would keep and every flow carry;
    an infinite one, which the cap reads as certain death; a negative one, a lapse rate
    past 1 whose monthly rate has no real value, and a key that is not whole as one ``int``
    truncates; and a gap in a group or a cell's year as a ``KeyError``, only where a
    projection reaches it.  Here the cell the projection asks first refuses each, naming the
    file, the column and its lines (:data:`UNREADABLE`), and so does a projection of the
    anchor cell, which reads both tables: ``Data.mort_age_first`` the mortality table and
    ``Data.lapse_last_year`` the lapse table, whichever cell it is asked for.
    """
    model = _read_edited(tmp_path, lambda t: t, edits={file: edit})
    try:
        call = model.Data.cells[cell]
        _refused((lambda: call("O50")) if cell == "lapse_last_year" else call, message)
        _refused(_point(model, 1).result_cf, message)
    finally:
        model.close()


def test_a_read_beyond_the_mortality_table_is_refused_naming_its_point(tmp_path):
    """An attained age the mortality table lacks is refused by the cell that reads it.

    ``proj_len()`` holds the limiting age to a year past the table's last age, and the
    issue age to ``issue_age_min``, the table's first, so no frame the shipped References
    admit reads past the table.  With ``issue_age_min`` lowered to 10, a point issued at 15
    is admitted by the frame and reads an age the table, from 18, lacks: ``mort_rate``
    refuses it, naming the point and the age, where ``WOL_UK_S``'s lookup raised
    ``KeyError``, and so does every report.  The bound is a Reference, so it is what admits
    the point.
    """
    model = _read_edited(tmp_path, _set("entry_age", [5], 15))
    try:
        model.Projection.issue_age_min = 10
        p = _point(model, 5)
        assert p.proj_len() == 12 * (120 - 15)
        message = "point_id 5: mort_table.csv has no rate at attained age 15"
        _refused(lambda: p.mort_rate(0), message)
        _refused(p.result_cf, message)
        assert p.mort_rate_mth(36) > 0.0
    finally:
        model.close()


# The rows the float keys are read on, by what they are: the anchor cell, the underwritten
# cell and the male smoker, issued at the valuation date; the paid-up point and the RPI
# point in force; and the RPI point issued 13 months on.
FLOAT_KEYED = (("twin", 1, 0), ("twin", 5, 0), ("twin", 7, 0), ("derived", 3, 200),
               ("derived", 4, 186), ("future", 4, -13))


def test_a_key_written_as_a_float_reads_as_wol_uk_s_reads_it(sec_model, tmp_path):
    """A key written ``70.0`` is the key 70, in every table and in every extent.

    ``WOL_UK_S``'s lookups match a float key to the int the projection asks, so a table
    written by a tool that writes every number with a decimal point reads the same.  Each
    assumption table's keys and the model point table's ``duration_mth`` are written as
    floats, and a point of each cell, sex and smoker status, issued at the valuation date,
    in force on both strands and to be issued later, projects what the committed tables
    project, exactly (:data:`FLOAT_KEYED`): between them they read both tables over every
    age from 40 to 119 and every policy year.
    """
    def as_float(column):
        return lambda table: table.assign(**{column: table[column].astype(float)})

    edits = {MORT: as_float("age"), LAPSE: as_float("policy_year")}
    model = _read_edited(tmp_path, as_float("duration_mth"), edits=edits)
    committed = _committed()
    points = [_label(committed, *case) for case in FLOAT_KEYED]
    try:
        for point_id in points:
            for report in ("result_cf", "result_pols"):
                assert frame_mismatches(_point(sec_model, point_id).cells[report](),
                                        _point(model, point_id).cells[report](),
                                        rtol=0, atol=0) == [], (point_id, report)
    finally:
        model.close()


# ---------------------------------------------------------------------------
# T6 -- regeneration


def test_the_committed_sec_inputs_are_what_s_generates():
    """``model_point_table_sec.csv`` is what WOL_UK_S and its table generate today.

    Every row and column, the text cells and the five opening-state columns included: an
    edit to an S row the table copies or derives from, or to an S formula a row's state is
    read from, fails here until ``python tools/gen_sec_points.py WOL_UK_SEC`` regenerates
    it, in the same commit.  Text and integers compare exactly, and a float by its value, to
    1e-12, because the text the writer picks for a computed float depends on the platform's
    parser (§5).  The generator reads S itself: the rows of the spec's ``derived_refs`` are
    read with References set on S, which drops what an S model given to it had cached.
    """
    assert check_generated(SEC) == []


# ---------------------------------------------------------------------------
# The product's own facts


def test_the_two_clocks_on_the_shipped_points(sec_model):
    """``t`` counts from the valuation date; ``duration_mth(t)`` from issue (D3, D4).

    On a twin of S's new business the two coincide, and its policies enter as new business
    at ``t = 0``.  The paid-up point valued 200 months after issue is in policy year 17 at
    attained age 86 at ``t = 0``, has 400 months to the limiting age, and is on the books
    from ``t = 0`` on both strands with no new business; its premiums cease at ``t = 40``,
    policy month 240.  The RPI point valued at 186 steps its increases at ``t = 6``, policy
    month 192.  The point issued 13 months on has nothing in force and nothing to do before
    ``t = 13``, and a frame of 613 months; its increase steps at ``t = 25``.  A timing the
    model does not know is refused rather than answered with another count.
    """
    twin = _row(sec_model, "twin", 1, 0)
    assert [twin.duration_mth(t) for t in (0, 1, 599)] == [0, 1, 599]
    assert (twin.t_entry(), twin.pols_if_init(), twin.pols_new_biz(0), twin.pols_if(0)) == (
        0, 0.0, 1.0, 1.0)
    assert (twin.limit_mth(), twin.proj_len()) == (600, 600)
    old = _row(sec_model, "derived", 3, 200)
    assert (old.duration_mth(0), old.duration(0), old.policy_year(0), old.age(0)) == (
        200, 16, 17, 86)
    assert (old.proj_len(), old.t_entry(), old.pols_new_biz(0)) == (400, 0, 0.0)
    assert old.is_active(399) and not old.is_active(400)
    assert old.pols_if(0) == old.pols_if_init() == old.policy_count()
    assert old.pols_pu(0) == old.pols_pu_init() > 0.0
    assert old.premium_pp(39) == 30.0 and old.premium_pp(40) == 0.0
    idx = _row(sec_model, "derived", 4, 186)
    assert idx.cover_pp(5) == idx.cover_pp_init() == pytest.approx(5000 * 1.03 ** 15,
                                                                   rel=1e-12)
    assert idx.cover_pp(6) == pytest.approx(idx.cover_pp_init() * 1.03, rel=1e-12)
    fut = _row(sec_model, "future", 4, -13)
    assert (fut.duration_mth(0), fut.t_entry(), fut.proj_len()) == (-13, 13, 613)
    assert not fut.is_active(12) and fut.is_active(13)
    assert (fut.pols_if_init(), fut.pols_new_biz(13), fut.pols_if(13)) == (0.0, 1.0, 1.0)
    assert fut.cover_pp(24) == 5000.0
    assert fut.cover_pp(25) == pytest.approx(5150.0, rel=1e-12)
    _refused(lambda: old.pols_if_at(0, "BEF_NOTHING"), "invalid timing")


def test_the_committed_rows_continue_their_s_points(sec_model, s_model):
    """Each committed row in force, or issued later, is its S point from its month on.

    T6 compares a float to 1e-12, which pins a small count only to that much of itself, so
    each committed row is compared with its S point frame by frame and cell by cell, at the
    shipped assumptions (USLIB-SEC-PLAN.md §7.1, *Precised at M3*, item 11): the six
    derived rows from their months, and the row issued 13 months on from S's issue month,
    all to 1e-9 relative with no absolute floor but on the residual, every cell but those
    expense inflation moves (:func:`_continues_s`), which the inflation test holds.  The
    rows read from S under References of their own are S's under them, which the test after
    this one compares.
    """
    table = sec_model.Data.model_point_table()
    found = []
    for point_id in table.index:
        kind, month = table.at[point_id, "row_kind"], int(table.at[point_id, "source_mth"])
        if kind == "twin" and month == 0:
            continue
        policy = table.at[point_id, "source_policy_id"]
        if (policy, month) in UNDER_REFS:
            continue
        s_point = int(s_model.Data.model_point_table().index[
            s_model.Data.model_point_table()["policy_id"] == policy][0])
        found += [f"point {point_id}: {line}" for line in _continues_s(
            _point(s_model, s_point), _point(sec_model, point_id), month)]
    assert not found, found[:20]


def _window_sweep(proj, months):
    """Evaluate on an S point every cell keyed by a month at each of ``months``, alone.

    Each cell with a ``t`` parameter is called at each of ``months`` with every timing of
    S's and every kind the cell takes, and no report and no check is called: so what S
    caches from the first of ``months`` on is those months and the months their
    recursions and look-aheads read, and a comparison that reads S's cache,
    :func:`uk_sec_support.twin_mismatches`, compares those months alone.
    """
    domains = {"timing": ("BEF_DECR", "BEF_LAPSE", "AFT_DECR")}
    kinds = {"benefit_pp": BENEFITS, "claims": (*KINDS, None)}
    for name, cells in proj.cells.items():
        params = list(cells.parameters)
        if "t" not in params:
            continue
        options = [months if param == "t" else kinds[name] if param == "kind"
                   else domains[param] for param in params]
        for args in itertools.product(*options):
            cells(*args)


# Where each committed row read under References of its own parts from S under them at the
# shipped References: the RPI and the take-up step the cover and the premium at the next
# policy anniversary, at the shipped values from then on, so those rows are S's to their
# next anniversary, in every cell but the steps themselves, and S's in their counts
# throughout, since neither moves a decrement; the stress lapses nothing on a point with no
# full cover, so the row paid-up entirely is S's throughout, but in the lapse rates
# themselves, which multiply no policy.
UNDER_REFS_UNTIL = {("WOL-000004", 120): 12, ("WOL-000006", 120): 12,
                    ("WOL-000003", 180): None}
UNDER_REFS_STEPS = frozenset({"esc_cover_step", "esc_prem_step"})
UNDER_REFS_RATES = frozenset({"lapse_rate", "lapse_rate_mth"})


def test_the_committed_rows_under_references_of_their_own_are_s_under_them(sec_model):
    """Each row read from S under References of its own is S's under them, as far as they
    reach, and today's References' after (§6.4, K14).

    At S's References each history is what today's References rebuild, so the spec reads
    three rows from S under References of their own, which its ``derived_refs`` records
    (:data:`UNDER_REFS`): the RPI point at 120 under an RPI of 5%, its cover and premium
    1.05 and 1.075 to the tenth power; the underwritten increasing point at 120 under a
    take-up of a half, its increases 2.5% and 5% a year; and the paid-up point at 180 under
    a stress of 100, paid-up entirely.  At the shipped References the committed model
    projects each from that history: the first two S's under their References to the next
    policy anniversary, at ``t = 12``, in every cell S evaluates in those months and both
    reports' rows, to 1e-9 relative with no absolute floor but on the residual, but those
    expense inflation moves (:func:`_continues_s`), and from that anniversary at today's
    increases, where S's continue at its own; the third S's under its stress over the whole
    frame, but in the lapse rates, which on a point with no full cover multiply nothing.
    The history is history.  And with each row's References set in both models the row is
    S's in every month of its frame.  Each Reference is set on a model just read (K7).
    """
    assert set(UNDER_REFS) == set(UNDER_REFS_UNTIL), UNDER_REFS
    for (policy, d), refs in UNDER_REFS.items():
        s_point = int(policy.rsplit("-", 1)[1])
        row = _row(sec_model, "derived", s_point, d)
        until = UNDER_REFS_UNTIL[(policy, d)]
        s = mx.read_model(model_path(TWIN), name=_name("under"))
        try:
            for ref, value in refs.items():
                setattr(s.Projection, ref, value)
            sp = _point(s, s_point)
            end = sp.proj_len() if until is None else d + until
            _window_sweep(sp, range(d, end))
            exempt = SPLICE_EXEMPT | INFLATION_CELLS | UNDER_REFS_STEPS
            if until is None:
                exempt = exempt | UNDER_REFS_RATES
            found = twin_mismatches(sp, row, t_offset=d, exempt=exempt | RESIDUALS,
                                    atol=0.0, codes=codes(row))
            others = exempt | (set(sp.cells) - RESIDUALS)
            found += twin_mismatches(sp, row, t_offset=d, exempt=others, codes=codes(row))
            keep = [c for c in sp.result_cf().columns if c not in INFLATED]
            pols = [c for c in sp.result_pols().columns if c not in UNDER_REFS_RATES]
            for report, columns in (("result_cf", keep), ("result_pols", pols)):
                found += [f"{report}: {line}" for line in frame_mismatches(
                    sp.cells[report]().loc[d:end - 1], row.cells[report]().loc[:end - d - 1],
                    t_offset=d, columns=columns, atol=0.0)]
            assert not found, (policy, d, found[:20])
            counts = ["pols_if", "pols_pu", "pols_death", "pols_lapse", "pols_convert"]
            assert frame_mismatches(sp.result_pols(), row.result_pols(), t_offset=d,
                                    columns=counts, atol=0.0) == [], (policy, d)
            if until is not None:
                step = row.cover_pp(until) / row.cover_pp(until - 1)
                assert step == pytest.approx(1.0 + row.esc_cover_step(), rel=1e-12)
                assert sp.cover_pp(d + until) / sp.cover_pp(d + until - 1) != step
        finally:
            s.close()
        sec = mx.read_model(model_path(SEC), name=_name("under_sec"))
        s = mx.read_model(model_path(TWIN), name=_name("under_s"))
        try:
            for model in (sec, s):
                for ref, value in refs.items():
                    setattr(model.Projection, ref, value)
            sp = _point(s, s_point)
            _sweep_s(sp)
            assert _continues_s(sp, _row(sec, "derived", s_point, d), d) == [], (policy, d)
        finally:
            sec.close()
            s.close()


def _rpi_history(path, months, premium=30.0, cover=5000.0, cessation=240):
    """The cover, the premium and the premiums paid entering policy month ``months`` of
    a policy whose RPI at each anniversary ``y`` was ``path[y - 1]``, as the contract
    gives them: the cover up by the RPI floored at 0 and capped at 10%, the premium by 1.5
    times it capped at 15%, at each anniversary, and a premium paid at the start of each
    month to cessation.  ``(cover, premium, premiums paid)``, the premium the last one paid
    once premiums have ceased."""
    paid = 0.0
    for m in range(months):
        if m and m % 12 == 0:
            r = path[m // 12 - 1]
            cover *= 1.0 + min(max(r, 0.0), 0.10)
            premium *= 1.0 + min(max(1.5 * r, 0.0), 0.15)
        if m < cessation:
            paid += premium
    if months % 12 == 0 and months:
        r = path[months // 12 - 1]
        cover *= 1.0 + min(max(r, 0.0), 0.10)
        if months < cessation:
            premium *= 1.0 + min(max(1.5 * r, 0.0), 0.15)
    return cover, premium, paid


# An RPI that held at 0 for ten years and then rose to 12% a year, past the caps: a
# history no flat rpi_rate gives, which leaves the RPI point at its policy month 186 with a
# cover of 5,000 x 1.1^5, a premium of 30 x 1.15^5, and premiums paid of 30 x 132 for the
# first eleven years and the capped increases after.
RPI_PATH = (0.0,) * 10 + (0.12,) * 10


def test_the_cover_history_is_read_from_the_model_point(sec_model, tmp_path):
    """The cash sum's increases already given are the point's, not recomputed (K14).

    ``WOL_UK_S`` rebuilds the RPI variant's cover from issue at today's flat ``rpi_rate``,
    so a model that dropped the column and did the same would pass the splice, since S and
    the splice rebuild it alike.  So the RPI point at 186 is projected with the cover of
    :data:`RPI_PATH`, which no flat rate gives: its cash sum is that through the policy year
    under way, and times 1.03 for each anniversary after, at today's RPI; the claims on a
    death pay it, beyond the moratorium.  The committed row's own cover, at today's 3% since
    issue, is 5,000 x 1.03^15, and projects as that.
    """
    row = _label(_committed(), "derived", 4, 186)
    cover, premium, paid = _rpi_history(RPI_PATH, 186)
    assert cover == pytest.approx(5000.0 * 1.1 ** 5, rel=1e-12)
    model = _read_edited(tmp_path, _then(_set("cover_pp_init", [row], cover)))
    try:
        p = _point(model, row)
        death = _code(p, "DEATH")
        for t, years in ((0, 0), (5, 0), (6, 1), (30, 3), (413, 34)):
            assert p.cover_pp(t) == pytest.approx(cover * 1.03 ** years, rel=1e-12), t
            assert p.benefit_pp(t, death) == p.cover_pp(t), t
        q = _point(sec_model, row)
        assert q.cover_pp(0) == pytest.approx(5000.0 * 1.03 ** 15, rel=1e-12)
        assert p.cover_pp(0) != pytest.approx(q.cover_pp(0), rel=1e-6)
    finally:
        model.close()


def test_the_premium_history_is_read_from_the_model_point(sec_model, tmp_path):
    """The premium's increases already given are the point's, not recomputed (K14).

    ``WOL_UK_S`` rebuilds the RPI variant's premium from issue at today's flat ``rpi_rate``
    as it does the cover.  So the RPI point at 186 is projected with the premium of
    :data:`RPI_PATH`, 30 x 1.15^5: its premium is that through the policy year under way,
    times 1.045 for each anniversary after, at 1.5 times today's RPI, to cessation at policy
    month 240, ``t = 54``, and nothing from then on; the premiums paid add it month by month.
    """
    row = _label(_committed(), "derived", 4, 186)
    _, premium, _ = _rpi_history(RPI_PATH, 186)
    assert premium == pytest.approx(30.0 * 1.15 ** 5, rel=1e-12)
    model = _read_edited(tmp_path, _set("premium_pp_init", [row], premium))
    try:
        p = _point(model, row)
        for t, years in ((0, 0), (5, 0), (6, 1), (53, 4)):
            assert p.premium_pp(t) == pytest.approx(premium * 1.045 ** years, rel=1e-12), t
        assert p.premium_pp(54) == 0.0 and p.premium_pp(100) == 0.0
        assert p.prem_cum_pp(1) == p.prem_cum_pp(0) + p.premium_pp(1)
        assert _point(sec_model, row).premium_pp(0) == pytest.approx(30.0 * 1.045 ** 15,
                                                                      rel=1e-12)
    finally:
        model.close()


def test_the_premiums_paid_are_read_from_the_model_point(sec_model, tmp_path):
    """The premiums already paid are the point's, not rebuilt from the schedule (K14).

    ``WOL_UK_S`` sums the premiums from issue at today's RPI, so a model that rebuilt them
    from the schedule would pass the splice.  The stress on the lapse rate compares them
    with the cover in every month, so the RPI point at 186 is projected under a stress of
    0.5 with the whole history of :data:`RPI_PATH`, which never crossed: its premiums paid,
    6,389.30, below its cover of 8,052.55, cross it at ``t`` = 37, policy month 223, where
    the stressed lapse starts, and the crossover, a policy month, is found there, searched
    forward from the columns.  At today's 3% since issue the row's premiums paid exceed its
    cover from month 0, and stress it there.  And the moratorium refunds of the anchor cell
    valued at 6 pay the premiums it carries in plus the month's: the 180 it holds, and
    180.004, which ``Data`` reads, an extract rounded to the cent, where a refund rebuilt
    from the premium schedule would pay 180.
    """
    row = _label(_committed(), "derived", 4, 186)
    cover, premium, paid = _rpi_history(RPI_PATH, 186)
    model = _read_edited(tmp_path, _then(_set("cover_pp_init", [row], cover),
                                         _set("premium_pp_init", [row], premium),
                                         _set("prem_cum_pp_init", [row], paid),
                                         _set("crossover_mth_init", [row], -1)))
    try:
        model.Projection.lapse_crossover_beta = 0.5
        p = _point(model, row)
        assert p.prem_cum_pp(0) == pytest.approx(paid + premium, rel=1e-15)
        crossing = next(t for t in range(p.proj_len()) if p.prem_cum_pp(t) > p.cover_pp(t))
        for t in range(crossing):
            assert p.lapse_rate(t) == p.lapse_rate_base(t), t
        assert p.lapse_rate(crossing) == pytest.approx(1.5 * p.lapse_rate_base(crossing),
                                                       rel=1e-12)
        assert (crossing, p.crossover_mth()) == (37, 223)
        assert (round(paid, 2), round(cover, 2)) == (6389.30, 8052.55)
        shipped = _point(sec_model, row)
        assert shipped.prem_cum_pp(0) > shipped.cover_pp(0) and crossing > 0
    finally:
        model.close()
    anchor = _row(sec_model, "derived", 1, 6)
    non_acc = _code(anchor, "NON_ACC")
    assert anchor.prem_cum_pp_init() == 180.0
    assert [anchor.benefit_pp(t, non_acc) for t in (0, 5, 6)] == [210.0, 360.0, 5000.0]
    label = anchor.point_id
    model = _read_edited(tmp_path / "cent", _set("prem_cum_pp_init", [label], 180.004))
    try:
        p = _point(model, label)
        assert [p.benefit_pp(t, _code(p, "NON_ACC")) for t in (0, 5)] == [
            180.004 + 30.0, 180.004 + 30.0 + 150.0]
    finally:
        model.close()


def test_the_fixed_increases_taken_up_are_read_from_the_model_point(sec_model):
    """The underwritten variant's increases taken up are the point's (K14).

    ``WOL_UK_S`` rebuilds the fixed increases from issue at today's ``esc_take_up``, so a
    take-up changed at the valuation date would reach back over every increase already
    given, though they are history, a fact of the contract, as the RPI's are.  The cover and
    premium columns carry them on the fixed variant as on the RPI one: the committed row of
    the underwritten increasing point at 120, read from S under a take-up of a half, holds a
    cover of 150,000 x 1.025^10 and a premium of 101.25 x 1.05^10, and at today's take-up of
    1 its cover steps by 5% and its premium by 10% at each anniversary after, from those.
    With the take-up raised to 1 at the valuation date in ``WOL_UK_S`` the whole history
    would be 1.05^10 and 1.1^10.
    """
    row = _row(sec_model, "derived", 6, 120)
    assert row.cover_pp_init() == pytest.approx(150000.0 * 1.025 ** 10, rel=1e-12)
    assert row.premium_pp_init() == pytest.approx(101.25 * 1.05 ** 10, rel=1e-12)
    for t, years in ((0, 0), (11, 0), (12, 1), (60, 5)):
        assert row.cover_pp(t) == pytest.approx(row.cover_pp_init() * 1.05 ** years,
                                                rel=1e-12), t
        assert row.premium_pp(t) == pytest.approx(row.premium_pp_init() * 1.1 ** years,
                                                  rel=1e-12), t
    assert row.cover_pp(0) != pytest.approx(150000.0 * 1.05 ** 10, rel=1e-6)


def test_the_paid_up_strand_is_read_from_the_model_point(sec_model, spliced, tmp_path):
    """The paid-up policies and their cover are the point's, not rebuilt (K14).

    ``WOL_UK_S`` builds the paid-up strand from issue, its conversions at today's lapse
    table and stress and its cash sums at today's cover, so a stress or an RPI set at the
    valuation date would convert lapses long past or reprice a paid-up value already fixed.
    So the paid-up point at 200 is projected at the shipped References, with no stress, from
    the strand ``WOL_UK_S`` reaches at policy month 200 under the splice's stress of 0.5,
    more policies converted past the crossover, at the cash sums of their months: its
    paid-up count and its paid-up cover are the columns', which today's References, the
    committed row's, do not give; each paid-up death pays the cover per paid-up policy;
    and the strand runs off from them on mortality alone, taking in the month's
    conversions.
    """
    stressed = _point(spliced[0], 3)
    count = stressed.pols_pu(200)
    cover = stressed.pu_benefit(200) / count
    label = _label(_committed(), "derived", 3, 200)
    shipped = _point(sec_model, label)
    assert count != pytest.approx(shipped.pols_pu_init(), rel=1e-6)
    assert cover != pytest.approx(shipped.pu_benefit_pp_init(), rel=1e-9)
    model = _read_edited(tmp_path, _then(_set("pols_pu_init", [label], count),
                                         _set("pu_benefit_pp_init", [label], cover)))
    try:
        p = _point(model, label)
        pu_kind = _code(p, "DEATH_PU")
        assert p.pols_pu(0) == count and p.pu_benefit(0) == count * cover
        assert p.claims(0, pu_kind) == p.pu_benefit(0) * p.mort_rate_mth(0)
        assert p.pols_death_pu(0) == count * p.mort_rate_mth(0)
        assert p.pols_pu(1) == count * (1.0 - p.mort_rate_mth(0)) + p.pols_convert(0)
        assert p.pols_if(0) == shipped.pols_if(0)
    finally:
        model.close()


# Histories of the crossover no flat rate at today's 3% rebuilds, as (WOL_UK_S's RPI, its
# crossover there, the months S point 4 is restated at): at an RPI of 0 the RPI point is a
# level point and crosses at 166; at 8% its premiums rise faster and it crosses at 201.
CROSSOVER_HISTORIES = ((0.0, 166, (167, 186, 200)), (0.08, 201, (202, 230, 239)))


@pytest.mark.parametrize("rpi, month, restated", CROSSOVER_HISTORIES,
                         ids=[f"rpi {rpi:.0%}" for rpi, _, _ in CROSSOVER_HISTORIES])
def test_the_crossover_is_read_from_the_model_point(tmp_path, rpi, month, restated):
    """A crossover before the valuation date is the point's, not searched for again (K14).

    ``WOL_UK_S`` searches for the crossover from issue at today's ``rpi_rate``, so a model
    that carried the opening state back at today's increases would report the month today's
    RPI puts it in, where the RPI of its day put it elsewhere: the review found the RPI
    point restated after a crossover at 166 under an RPI of 0 reported at 166, 150 and 137,
    and one at 201 under 8% at 220.  So S point 4 is restated by the generator out of
    ``WOL_UK_S`` run under each of :data:`CROSSOVER_HISTORIES`, after its crossover, and
    projected at the shipped RPI of 3%: each row's ``crossover_mth_init`` is S's month, and
    ``crossover_mth()`` reports it.  Restated in the crossover month itself, the crossover
    is the projection's, ``crossover_mth_init`` -1, and the search forward from the opening
    state finds it there, in month 0.
    """
    s = mx.read_model(model_path(TWIN), name=_name("crossover_s"))
    try:
        s.Projection.rpi_rate = rpi
        assert _point(s, 4).crossover_mth() == month
        spec = dataclasses.replace(SPEC, derived=tuple((4, d) for d in (month, *restated)),
                                   future=(), derived_refs={})
        table, _ = build_sec_table(spec, s)
    finally:
        s.close()
    model = mx.read_model(_sec_inputs(tmp_path, table), name=_name("crossover"))
    try:
        assert model.Projection.rpi_rate == 0.03
        for d in restated:
            row = _row(model, "derived", 4, d)
            assert (row.crossover_mth_init(), row.crossover_mth()) == (month, month), d
        at = _row(model, "derived", 4, month)
        assert (at.crossover_mth_init(), at.crossover_mth()) == (-1, month)
    finally:
        model.close()


def test_the_truncation_check_scales_with_the_paid_up_policies(tmp_path):
    """``check_truncation`` closes on the paid-up strand's policies too (§7.1, T4).

    The survivors at the limiting age are rounding on every policy on the books, so the
    check holds them to 1e-9 times ``max(policy_count() + pols_pu_init(), 1)``.  At the
    shipped loading the over-50s cap takes every life before the limiting age and the
    survivors are exactly 0, which any tolerance passes; at a loading of 0.8 the cap no
    longer binds there and the paid-up point paid-up entirely keeps 3.0e-11 of a policy at
    age 120 for each it holds.  So that point is projected with ten million paid-up
    policies and no full cover: its survivors, 3.0e-4 of a policy, exceed 1e-9, which a
    tolerance scaled by ``policy_count()`` alone, 0, would hold them to, and the check
    closes on the paid-up count.  The loading is set on a model just read (K7).
    """
    label = _label(_committed(), "derived", 3, 180)
    model = _read_edited(tmp_path, _set("pols_pu_init", [label], 1e7))
    try:
        model.Projection.mort_loading_o50 = 0.8
        p = _point(model, label)
        survivors = p.pols_maturity(p.proj_len() - 1)
        assert p.policy_count() == 0.0 and p.pols_pu_init() == 1e7
        assert 1e-9 < survivors < 1e-9 * 1e7, survivors
        assert p.check_truncation() is True
    finally:
        model.close()


def test_expense_inflation_runs_on_the_valuation_clock(sec_model, s_model):
    """Maintenance is in valuation-date pounds, for every point alike (D7).

    At the shipped 3%, the factor at ``t`` is ``1.03^(t // 12)`` on every point, whatever
    its duration, stepping on the valuation date's anniversaries.  So the underwritten
    increasing point valued on its first anniversary, in force 12 months, pays S's
    month-``12 + t`` expenses deflated by ``1.03``, the inflation S had already applied
    since issue, and the point issued 13 months on pays S's maintenance a year of inflation
    earlier than S's issue month would: its factor at ``t`` is ``1.03^(t // 12)``, where S's
    at ``t - 13`` is ``1.03^((t - 13) // 12)``.  The acquisition expense is not inflated on
    either.  This is the only test that sees inflation run on the policy clock: the splice
    sets the rate to 0, and on a point issued at ``t = 0`` the clocks agree.
    """
    assert sec_model.Projection.inflation_rate == INFLATION
    p, s = _row(sec_model, "derived", 6, 12), _point(s_model, 6)
    fut = _row(sec_model, "future", 4, -13)
    for t in (0, 11, 12, 30):
        assert p.inflation_factor(t) == fut.inflation_factor(t) == (1 + INFLATION) ** (t // 12)
    for t in range(p.proj_len()):
        assert p.expenses(t) == pytest.approx(s.expenses(12 + t) / (1 + INFLATION),
                                              rel=1e-12), t
    s4 = _point(s_model, 4)
    acq = s4.expense_acq_pp()
    for t in range(13, fut.proj_len()):
        issued = acq if t == 13 else 0.0
        if fut.pols_all(t) == 0.0:
            continue
        maint = (fut.expenses(t) - issued) / fut.pols_all(t)
        want = (s4.expenses(t - 13) - issued) / s4.pols_all(t - 13)
        assert maint == pytest.approx(
            want * (1 + INFLATION) ** (t // 12 - (t - 13) // 12), rel=1e-12), t


def test_mortality_improvement_runs_on_the_valuation_clock(tmp_path):
    """Improvement steps on the valuation date's anniversaries, for every point (D7).

    With improvement at 1% a year, the factor at ``t`` is ``0.99^(t // 12)`` on every point,
    whatever its duration: 1 through the first valuation year, whether the policy is new, in
    force 186 or 12 months, or to be issued 13 months on.  The mortality rate it multiplies
    is the table's at the point's attained age times the loading, capped, the table stated
    at the valuation date.  So the RPI point valued at 186 dies at S's table rate at month
    ``186 + t`` times ``0.99^(t // 12)``, where ``WOL_UK_S`` would improve it from issue,
    ``0.99^((186 + t) // 12)``.  This is the only test that sees improvement run on the
    policy clock: the splice keeps it at 0, where the clocks agree.  The References are set
    on a model just read (K7).
    """
    model = mx.read_model(_sec_inputs(tmp_path, _committed()), name=_name("improve"))
    try:
        model.Projection.mort_improvement = 0.01
        rows = [_row(model, *case) for case in (("twin", 1, 0), ("derived", 4, 186),
                                                 ("derived", 6, 12), ("future", 4, -13))]
        for t in (0, 11, 12, 30, 200):
            assert {p.mort_improve_factor(t) for p in rows} == {0.99 ** (t // 12)}, t
        p = rows[1]
        table = p.data.mort_table()
        for t in (0, 5, 6, 18, 290):
            q = float(table.loc[("population", "F", "NS", p.age(t)), "mort_rate"])
            assert p.mort_rate(t) == min(q * 1.2 * 0.99 ** (t // 12), 1.0), t
            assert p.mort_rate(t) != pytest.approx(
                min(q * 1.2 * 0.99 ** ((186 + t) // 12), 1.0), rel=1e-9), t
        assert rows[3].mort_rate(13) == min(
            float(table.loc[("population", "F", "NS", 70), "mort_rate"]) * 1.2 * 0.99, 1.0)
    finally:
        model.close()


def test_improvement_carries_survivors_past_the_truncation_check():
    """Where improvement gives way to the truncation check, recorded (§6.4).

    The shipped tables reach 1 well before the limiting age, so ``check_truncation()``
    holds on every point at no improvement.  Improvement lowers every rate, and the cap
    with it, and carries survivors to the limiting age.  At :data:`IMPROVEMENT`, 0.2%, the
    rate the module switches improvement on at, the check holds on every committed point,
    the largest residual 4.1e-12 of a policy; at 0.4% it first gives way, on the
    underwritten twins and the underwritten row valued at 12, each past the check's 1e-9;
    at 1% the underwritten twins hold 7.1e-6 of a policy at age 120; and at 2% the check
    gives way on every twin but the male smoker's, whose rates are the heaviest.  The
    underwritten twins hold the same count, as the escalation moves no decrement.  The two
    larger rates are read on the twins alone.  Each improvement is set on a model just read
    (K7).
    """
    found, worst = {}, {}
    for rate in (IMPROVEMENT, 0.004, 0.01, 0.02):
        model = mx.read_model(model_path(SEC), name=_name("truncation"))
        try:
            model.Projection.mort_improvement = rate
            table = model.Data.model_point_table()
            gives_way, largest = {}, 0.0
            for key, point_id in zip(point_keys(model), table.index):
                if rate > 0.004 and point_id not in S_POINTS:
                    continue
                p = projection(model, key)
                survivors = p.pols_maturity(p.proj_len() - 1)
                largest = max(largest, survivors)
                if not p.check_truncation():
                    gives_way[point_id] = survivors
            found[rate], worst[rate] = gives_way, largest
        finally:
            model.close()
    assert found[IMPROVEMENT] == {} and 1e-12 < worst[IMPROVEMENT] < 1e-11
    assert set(found[0.004]) == {5, 6, 12}
    assert found[0.01][5] == found[0.01][6] == pytest.approx(7.1e-6, rel=0.01)
    assert set(found[0.02]) == set(S_POINTS) - {7}


def test_every_twin_is_s_with_improvement_rpi_take_up_and_the_stress_on():
    """On new business, each twin is S's in every cell with every rate dial moved, in both.

    T1 compares the twins at the shipped References, where improvement and the stress are
    0 and the RPI and the take-up at their shipped values, and the splice holds improvement
    at 0 by design (D7), so a cell that dropped improvement, or read the RPI or the take-up
    from another clock, would pass both.  On a point issued at ``t = 0`` the two clocks
    coincide, and improvement, which runs on the valuation clock here and from issue in
    ``WOL_UK_S``, is the same factor in every month.  So with improvement at
    :data:`IMPROVEMENT`, the RPI at 6%, the take-up at 0.8 and the stress at the splice's
    0.5 set in both models, each twin of S's seven points is S's in every cell S evaluates
    in its sweep and in both reports, to 1e-9 relative with no absolute floor but on the
    residual (:func:`_compare`).  The References are set on models just read (K7).
    """
    refs = {"mort_improvement": IMPROVEMENT, "rpi_rate": 0.06, "esc_take_up": 0.8,
            "lapse_crossover_beta": SPLICED_REFS["lapse_crossover_beta"]}
    sec = mx.read_model(model_path(SEC), name=_name("dials"))
    s = mx.read_model(model_path(TWIN), name=_name("dials_s"))
    try:
        for model in (sec, s):
            for ref, value in refs.items():
                setattr(model.Projection, ref, value)
        found = []
        for point in S_POINTS:
            s_proj, twin = _point(s, point), _row(sec, "twin", point, 0)
            _sweep_s(s_proj)
            found += [f"point {point}: {line}" for line in _compare(
                s_proj, twin, 0, TWIN_EXEMPT_DEFAULT | SPEC.exempt)]
        assert not found, found[:20]
        twin = _row(sec, "twin", 4, 0)
        assert twin.mort_improve_factor(12) == 1.0 - IMPROVEMENT
        assert twin.esc_cover_step() == pytest.approx(0.06 * 0.8, rel=1e-15)
        assert _row(sec, "twin", 1, 0).lapse_rate(166) == pytest.approx(
            1.5 * _point(s, 1).lapse_rate_base(166), rel=1e-15)
    finally:
        sec.close()
        s.close()


def test_the_crossover_is_a_policy_month_carried_from_the_opening_state(sec_model,
                                                                        s_model):
    """The crossover is ``WOL_UK_S``'s policy month on every committed point S reaches.

    ``WOL_UK_S`` searches the policy months it projects, which in force start at the
    valuation date, where look-back stops, and passes each as ``t`` (R1a).  Here a crossover
    before the valuation date is the point's ``crossover_mth_init``, and the search runs
    forward from the valuation date over the policy months on the contractual schedule, the
    premiums paid and the cover carried from the opening state.  So on every committed row
    S reaches at the shipped References, the twins, the rows in force and the row issued
    later, it is S's policy month: 166 on the level over-50s points, valued before it, at it
    or after it, 185 on the RPI point valued after it, 642 on the underwritten increasing
    one, 222 on the male smoker valued after cessation, and none on the level underwritten
    point.  On no point is it a month of the frame.  The test of the column itself, on
    histories today's References do not rebuild, follows the paid-up strand's.
    """
    table = sec_model.Data.model_point_table()
    s_table = s_model.Data.model_point_table()
    seen = {}
    for point_id in table.index:
        policy, month = table.at[point_id, "source_policy_id"], int(
            table.at[point_id, "source_mth"])
        if (policy, month) in UNDER_REFS:
            continue
        s_point = int(s_table.index[s_table["policy_id"] == policy][0])
        mine = _point(sec_model, point_id).crossover_mth()
        assert mine == _point(s_model, s_point).crossover_mth(), point_id
        seen[point_id] = mine
    assert seen[_label(table, "derived", 1, 166)] == 166
    assert seen[_label(table, "derived", 3, 200)] == 166
    assert seen[_label(table, "derived", 4, 186)] == 185
    assert seen[_label(table, "derived", 7, 300)] == 222
    assert seen[_label(table, "derived", 6, 12)] == 642
    assert seen[5] == -1


def test_the_moratorium_the_suicide_window_and_commission_run_on_the_policy_clock(
        sec_model, tmp_path):
    """The year-one rules count policy months, wherever they fall in the frame.

    The anchor cell valued 6 months after issue is inside its moratorium for six more
    months: a non-accidental death refunds the premiums paid through ``t = 5`` and pays the
    cash sum from ``t = 6``, its policy month 12, where ``WOL_UK_S`` would read the
    moratorium on ``t``; its accidental benefit doubles there on the double-benefit variant;
    and commission, 25% of each premium of policy year 1, continues through ``t = 5`` and
    stops at ``t = 6``.  The underwritten point valued on its first anniversary is past its
    suicide window, and one valued at 6 months inside it for six months more.  A point
    valued later pays no commission at all.
    """
    anchor = _row(sec_model, "derived", 1, 6)
    non_acc, death = _code(anchor, "NON_ACC"), _code(anchor, "DEATH")
    assert [anchor.in_moratorium(t) for t in (0, 5, 6)] == [True, True, False]
    assert anchor.benefit_pp(5, non_acc) == pytest.approx(360.0, rel=1e-15)
    assert anchor.benefit_pp(6, non_acc) == 5000.0
    assert [anchor.commissions(t) > 0.0 for t in (0, 5, 6, 7)] == [True, True, False, False]
    assert anchor.commissions(0) == pytest.approx(0.25 * anchor.premiums(0), rel=1e-15)
    uw = _row(sec_model, "derived", 6, 12)
    assert uw.benefit_pp(0, death) == uw.cover_pp(0)
    assert all(uw.commissions(t) == 0.0 for t in range(uw.proj_len()))
    assert all(_row(sec_model, "derived", 1, 166).commissions(t) == 0.0
               for t in range(434))
    model = _read_edited(tmp_path, _then(
        _set("duration_mth", [uw.point_id], 6), _set("cover_pp_init", [uw.point_id], 150000.0),
        _set("premium_pp_init", [uw.point_id], 101.25),
        _set("prem_cum_pp_init", [uw.point_id], 607.5),
        _set("variant_adb_2x", [anchor.point_id], True)))
    try:
        p = _point(model, uw.point_id)
        for t in (0, 5):
            assert p.benefit_pp(t, death) == pytest.approx(
                0.99 * p.cover_pp(t) + 0.01 * p.prem_cum_pp(t), rel=1e-15), t
        assert p.benefit_pp(6, death) == p.cover_pp(6)
        q = _point(model, anchor.point_id)
        acc = _code(q, "ACC")
        assert [q.benefit_pp(t, acc) for t in (5, 6)] == [5000.0, 10000.0]
    finally:
        model.close()


def test_acquisition_is_charged_on_new_business_only(sec_model):
    """The acquisition expense per policy issued, in the issue month alone.

    On every committed point, what ``expenses(t)`` holds beyond its maintenance part is
    the cell's acquisition expense times ``policy_count()`` in the issue month,
    ``t = -duration_mth``, and 0 in every other month, to 1e-9: the twins of S's new business
    bear it at ``t = 0``, the point issued 13 months on at ``t = 13``, and the points
    already in force never, though on the valuation clock their row 0 is ``t = 0``, as S's
    restated rows did not.  ``WOL_UK_S`` charges it at ``t = 0`` on the count in force there,
    which on a point issued at the valuation date is the issued count, so the twins agree
    with S at any count.
    """
    table = sec_model.Data.model_point_table()
    for key, point_id in zip(point_keys(sec_model), table.index):
        p = projection(sec_model, key)
        ts = range(p.proj_len())
        issue = -table.at[point_id, "duration_mth"]
        acq = [p.expenses(t) - p.expense_maint_pp() / 12 * p.inflation_factor(t)
               * p.pols_all(t) for t in ts]
        assert acq == pytest.approx([p.expense_acq_pp() * p.policy_count() if t == issue
                                     else 0.0 for t in ts], abs=1e-9), point_id
        assert (issue in ts) == (sum(acq) > 0.0), point_id


# A stress that lapses every policy past the crossover, as (the S points restated, their
# months): at a stress of 100 the lapse rate's bound at 1 binds, min(1.0, w), its bound
# first as in WOL_UK_S, and every would-be lapse leaves at the crossover, the paid-up
# point's converting.
LAPSE_ALL_CASES = ((1, (165, 166, 167, 200)), (3, (165, 166, 167, 200)))


def test_a_stress_that_lapses_every_policy_continues_the_s_projection(tmp_path):
    """T2 with the lapse rate's bound binding, which the splice's stress does not reach.

    The splice's stress of 0.5 takes no lapse rate past 1, so the bound side of the lapse
    rate's ``min`` is compared with S nowhere there.  So S's anchor and paid-up points are
    restated by the generator about their crossover under :data:`LAPSE_ALL`, a stress of
    100 set in S and SEC alike with the splice's inflation and improvement of 0, and each
    row is S's from its month on in every cell (:func:`_compare`): the lapse rates, the
    lapses and the conversions among them.  Then what the bound reaches: the lapse rate is 1
    from the crossover, every policy on full cover leaves in it, the paid-up point's
    converting, and the rows after it are paid-up entirely or empty, the states the
    every-state test reads.
    """
    s = mx.read_model(model_path(TWIN), name=_name("lapse_all_s"))
    sec = None
    try:
        for ref, value in LAPSE_ALL.items():
            setattr(s.Projection, ref, value)
        spec = dataclasses.replace(SPEC, derived=tuple((p, d) for p, mths in LAPSE_ALL_CASES
                                                       for d in mths),
                                   future=(), derived_refs={})
        table, _ = build_sec_table(spec, s)
        sec = mx.read_model(_sec_inputs(tmp_path, table), name=_name("lapse_all"))
        for ref, value in LAPSE_ALL.items():
            setattr(sec.Projection, ref, value)
        found = []
        for p, mths in LAPSE_ALL_CASES:
            s_proj = _point(s, p)
            _sweep_s(s_proj)
            for d in mths:
                found += [f"point {p} at {d}: {line}" for line in _compare(
                    s_proj, _row(sec, "derived", p, d), d, SPLICE_EXEMPT)]
        assert not found, found[:20]
        on = _row(sec, "derived", 3, 166)
        assert on.lapse_rate(0) == 1.0 and on.lapse_rate_mth(0) == 1.0
        assert on.pols_if(1) == 0.0 and on.pols_convert(0) == on.pols_exit(0) > 0.0
        after = _row(sec, "derived", 3, 200)
        assert after.policy_count() == 0.0 and after.pols_pu_init() > 0.0
        gone = _row(sec, "derived", 1, 200)
        assert gone.policy_count() == 0.0 and gone.pols_pu_init() == 0.0
    finally:
        if sec is not None:
            sec.close()
        s.close()


@pytest.mark.parametrize("rpi, steps", [(-0.02, (0.0, 0.0)), (0.25, (0.10, 0.15))],
                         ids=["an RPI below 0", "an RPI past both caps"])
def test_the_rpi_increases_are_floored_at_0_and_capped(rpi, steps):
    """The RPI's floor and caps, which the splice's 3% sits between, as in ``WOL_UK_S``.

    The cover's increase is the RPI floored at 0 and capped at 10%, and the premium's 1.5
    times it, floored at 0 and capped at 15%: ``max`` and then ``min``, each bound written
    second.  With the RPI at -2% neither the twin of the RPI point nor its row in force at
    186 increases at its next anniversary, and at 25% each cover rises 10% and each premium
    15%; the twin's steps, cover and premium are ``WOL_UK_S``'s at the same RPI, read on a
    model of each just read with the RPI set (K7).  T1 compares them at the shipped 3% and
    the twins test at 6%; the NaN test holds the bounds' order.
    """
    model = mx.read_model(model_path(SEC), name=_name("rpi"))
    s = mx.read_model(model_path(TWIN), name=_name("rpi_s"))
    try:
        for each in (model, s):
            each.Projection.rpi_rate = rpi
        twin, row, s_proj = _row(model, "twin", 4, 0), _row(model, "derived", 4, 186), _point(s, 4)
        for proj in (twin, s_proj):
            assert (proj.esc_cover_step(), proj.esc_prem_step()) == steps
            assert proj.cover_pp(12) == pytest.approx(5000.0 * (1 + steps[0]), rel=1e-15)
            assert proj.premium_pp(12) == pytest.approx(30.0 * (1 + steps[1]), rel=1e-15)
        assert twin_mismatches(s_proj, twin, rtol=0.0, atol=0.0, codes=codes(twin)) == []
        assert row.cover_pp(6) == pytest.approx(row.cover_pp_init() * (1 + steps[0]),
                                                rel=1e-15)
        assert row.premium_pp(6) == pytest.approx(row.premium_pp_init() * (1 + steps[1]),
                                                  rel=1e-15)
    finally:
        s.close()
        model.close()


# ---------------------------------------------------------------------------
# The cap on mortality
#
# mort_rate caps the annual rate at 1, the bound second, as WOL_UK_S's does since M0.  The
# shipped tables reach 1 in the tail, loaded or not, so the cap binds on S's own points: on
# the over-50s anchor cell from attained age 110, policy month 480, where the population
# rate times the loading of 1.2 passes 1; on the male smoker from 101, policy month 432; and
# on the underwritten cell from 114, policy month 888, where the assured rate reaches 1.
# S points 1, 7 and 5, each as (its first capped month, the attained age then).
CAPPED_POINTS = {1: (480, 110), 7: (432, 101), 5: (888, 114)}


def test_an_annual_mortality_past_1_is_capped_in_both_models(s_model, tmp_path):
    """Where the annual mortality rate passes 1, both models' rate is 1.

    On each of :data:`CAPPED_POINTS`, at the shipped tables, ``WOL_UK_S``'s rate reaches 1
    in its first capped month and stays there to the end of the frame, and the uncapped
    product passes 1 there or later: the capped rate and the monthly rate,
    ``1 - (1 - q)^(1/12)``, are 1.0 in every one of those months, the float, not the int 1,
    which compares equal to it, and S's are floats below 1 in every month before.  So every
    policy in force at the start of the first capped month dies in it, on both strands, none
    is in force after it, and every report holds finite floats alone.

    Four rows of each point, built from S by the generator under :data:`SPLICED_REFS`:
    issued at the valuation date and 12 months after it, and restated in force in the month
    before the cap, opened with S's count and state there, each compared with S in every
    cell, the capped months included, as T1, T3 and the splice compare them, to 1e-9
    relative with no absolute floor, but for the residual, rounding around 0, which keeps
    the floor of 1e-9 (USLIB-SEC-PLAN.md §5.1, step 6); and restated five months into the
    capped year, opened with S's state there and one policy, since S's count there is 0.  On
    each, the capped rates are 1.0 from its first capped month, every policy in force there
    dies in it, and the count is 0.0 after it.
    """
    s = mx.read_model(model_path(TWIN), name=_name("capped_s"))
    sec = None
    try:
        for ref, value in SPLICED_REFS.items():
            setattr(s.Projection, ref, value)
        derived, future = [], []
        for s_point, (cap, age) in CAPPED_POINTS.items():
            sp = _point(s, s_point)
            end = sp.proj_len()
            first = next(t for t in range(end) if sp.mort_rate(t) == 1.0)
            assert (first, sp.age(first)) == (cap, age), s_point
            after = range(cap, end)
            for name in ("mort_rate", "mort_rate_mth"):
                assert all(type(sp.cells[name](t)) is float and sp.cells[name](t) < 1.0
                           for t in range(cap)), name
                assert [(type(sp.cells[name](t)), sp.cells[name](t)) for t in after] == [
                    (float, 1.0)] * len(after), name
            _sweep_s(sp)
            assert sp.pols_if(cap) > 0.0 and sp.pols_death(cap) == sp.pols_if(cap)
            assert [sp.pols_all(t) for t in range(cap + 1, end)] == [0.0] * (len(after) - 1)
            derived += [(s_point, cap - 1), (s_point, cap + 5)]
            future.append((s_point, 12))
        rows, _ = build_sec_table(dataclasses.replace(SPEC, derived=tuple(derived),
                                                      future=tuple(future),
                                                      derived_refs={}), s)
        emptied = (rows["row_kind"] == "derived") & (rows["policy_count"] == 0.0)
        assert emptied.sum() == len(CAPPED_POINTS)
        rows.loc[emptied, "policy_count"] = 1.0
        sec = mx.read_model(_sec_inputs(tmp_path / "sec", rows), name=_name("capped"))
        for ref, value in SPLICED_REFS.items():
            setattr(sec.Projection, ref, value)
        for s_point, (cap, _) in CAPPED_POINTS.items():
            sp = _point(s, s_point)
            cases = ((("twin", s_point, 0), cap, TWIN_EXEMPT_DEFAULT | SPEC.exempt),
                     (("future", s_point, -12), cap + 12, FUTURE_EXEMPT),
                     (("derived", s_point, cap - 1), 1, SPLICE_EXEMPT),
                     (("derived", s_point, cap + 5), 0, None))
            for case, first, exempt in cases:
                p = _row(sec, *case)
                if exempt is not None:
                    assert twin_mismatches(sp, p, t_offset=case[2],
                                           exempt=exempt | RESIDUALS, atol=0.0,
                                           codes=codes(p)) == [], case
                    others = exempt | (set(sp.cells) - RESIDUALS)
                    assert twin_mismatches(sp, p, t_offset=case[2], exempt=others,
                                           codes=codes(p)) == [], case
                capped, later = range(first, p.proj_len()), range(first + 1, p.proj_len())
                for name in ("mort_rate", "mort_rate_mth"):
                    assert [(type(p.cells[name](t)), p.cells[name](t)) for t in capped] == [
                        (float, 1.0)] * len(capped), (case, name)
                assert p.pols_if(first) > 0.0 and p.pols_death(first) == p.pols_if(first)
                assert [p.pols_all(t) for t in later] == [0.0] * len(later), case
                for report in ("result_cf", "result_pols"):
                    frame = p.cells[report]()
                    assert (frame.dtypes == "float64").all(), (case, report)
                    assert np.isfinite(frame.to_numpy()).all(), (case, report)
    finally:
        if sec is not None:
            sec.close()
        s.close()


# A NaN sent to each bound written with its bound second, as (the bound, the Reference that
# feeds it, set to NaN on a model read for the test before it computes anything, the S
# point whose twin reads it, and the calls that must give the float NaN).  The cap reads
# each cell's loading on its own cell's points, and improvement from the second valuation
# year, where its power first reads it; the RPI's floor and cover cap, max(rpi, 0.0) and
# min(..., 0.1), read rpi_rate, and the premium step's, max(1.5 x rpi, 0.0) and
# min(..., 0.15), esc_rpi_prem_mult, on the RPI point.  A bound written first would turn
# each NaN into the bound: a blank input read as certain death, or an increase of 10%.  This
# form runs compiled unchanged, since a compiled ItemSpace takes the References when it is
# made (USLIB-SEC-PLAN.md §5.1, step 6, precised at M12).
NAN_BOUNDS = [
    ("the mortality cap on the over-50s cell, min(q, 1.0)", "mort_loading_o50", 1,
     [("mort_rate", (0,)), ("mort_rate_mth", (0,)), ("pols_death", (0,))]),
    ("the mortality cap on the underwritten cell", "mort_loading_uw", 5,
     [("mort_rate", (0,)), ("mort_rate_mth", (300,)), ("pols_death", (0,))]),
    ("the mortality cap, through improvement", "mort_improvement", 1,
     [("mort_improve_factor", (12,)), ("mort_rate", (12,)), ("mort_rate_mth", (12,))]),
    ("the RPI's floor and cover cap", "rpi_rate", 4,
     [("esc_cover_step", ()), ("esc_prem_step", ())]),
    ("the RPI premium step's floor and cap", "esc_rpi_prem_mult", 4,
     [("esc_prem_step", ())]),
]


@pytest.mark.parametrize("bound, ref, s_point, calls", NAN_BOUNDS,
                         ids=[c[0] for c in NAN_BOUNDS])
def test_a_nan_that_reaches_a_bound_stays_nan(bound, ref, s_point, calls):
    """A NaN that reaches a bound written second stays NaN, and is not read as the bound.

    ``min`` keeps its first argument unless a later one compares smaller, and ``max`` unless
    a later one compares larger, in modelx and compiled alike, and no comparison with NaN
    holds, so with its bound first each would turn a NaN into the bound.  Each is written
    with its bound second, as ``WOL_UK_S`` writes it (:data:`NAN_BOUNDS`): the Reference
    that feeds it is set to NaN on a model read for the test, and every call must give the
    float NaN.  The cells are called on their own, without the frame: ``proj_len()`` refuses
    each of these References at NaN before a report reaches a bound (the domain test).  The
    lapse rate's bound keeps ``WOL_UK_S``'s order, the bound first, and is no cap on a
    mortality rate (USLIB-SEC-PLAN.md §5.1, step 6); ``Data`` and ``proj_len()`` hold what it
    reads to domains no NaN is in.
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


def test_no_check_passes_a_residual_that_is_not_a_number():
    """No check passes a residual that is NaN (§7.1).

    A check is ``abs(resid) <= tolerance`` over the frame, and no comparison with NaN
    holds, so a NaN residual would fail it, as ``WOL_UK_S``'s does (USLIB-SEC-PLAN.md §7.1,
    *Precised at M3*, item 11); and the frame comes first.  With ``mort_loading_o50`` NaN,
    set on a model read for the test before it computes anything, the mortality rates, the
    counts on both strands and so the roll-forward's residual and the truncation residual
    are NaN on the paid-up twin, and each check, asking ``proj_len()`` for the frame, is
    refused the Reference, by name, before it compares one.  So no check passes; and on the
    shipped References each is the bool True.
    """
    for loading, closes in ((float("nan"), False), (1.2, True)):
        model = mx.read_model(model_path(SEC), name=_name("nan_check"))
        try:
            model.Projection.mort_loading_o50 = loading
            p = _row(model, "twin", 3, 0)
            assert math.isnan(p.check_pols_roll_fwd_resid(0)) != closes
            assert math.isnan(p.pols_maturity(599)) != closes
            if closes:
                assert p.check_pols_roll_fwd() is True and p.check_truncation() is True
            else:
                refusal = "point_id 3: mort_loading_o50 must be a finite number, 0 or more, not nan"
                _refused(p.check_pols_roll_fwd, refusal)
                _refused(p.check_truncation, refusal)
        finally:
            model.close()


@pytest.mark.parametrize("check, resid", [
    ("check_pols_roll_fwd", "check_pols_roll_fwd_resid"),
    ("check_truncation", "pols_maturity")])
def test_a_check_fails_a_residual_that_is_not_a_number(sec_model, check, resid):
    """Each check returns False where its residual is NaN (§7.1, item 11).

    A check is ``abs(resid) <= tolerance`` over the frame, or the truncation residual
    ``<= tolerance`` in its last month, which no NaN passes, as ``WOL_UK_S``'s are; but no
    input the frame accepts gives a NaN residual any more, so the residual's formula is
    replaced, on a model read for the test, by one that returns NaN in every month: the
    roll-forward's, and the truncation residual, ``pols_maturity``.  Then the check is the
    bool False on every committed point, where with its own formula it is True.  A check
    that asked whether any residual was past its tolerance would pass NaN.
    """
    model = mx.read_model(model_path(SEC), name=_name("nan_resid"))
    try:
        model.Projection.cells[resid].formula = lambda t: float("nan")
        for key in point_keys(model):
            p, shipped = projection(model, key), projection(sec_model, key)
            assert math.isnan(p.cells[resid](0)), key
            assert shipped.cells[check]() is True and p.cells[check]() is False, key
    finally:
        model.close()


def _outside_cover_faults(p, where):
    """Where ``p``, an ItemSpace that has evaluated nothing, departs from OUTSIDE_COVER.

    Every cell of :data:`OUTSIDE_COVER`, ``pols_if_at`` at each timing, ``claims`` at each
    kind and ``benefit_pp`` at each benefit, in every month before issue and at
    ``t = proj_len()``, the first month after cover, which the count's look-ahead reads,
    against :data:`OUTSIDE_COVER`; then whether any of :data:`IN_COVER_ONLY` was evaluated
    on the way, which only a fresh ItemSpace can say.  A cell that raises is reported as a
    fault too, so the scan goes on.
    """
    faults = []
    for t in [*range(p.t_entry()), p.proj_len()]:
        calls = [(name, (t,), want) for name, want in OUTSIDE_COVER.items()]
        calls += [("pols_if_at", (t, _code(p, timing)), 0.0) for timing in TIMINGS]
        calls += [("claims", (t, _code(p, kind)), 0.0) for kind in KINDS]
        calls += [("benefit_pp", (t, _code(p, kind)), 0.0) for kind in BENEFITS]
        for name, args, want in calls:
            try:
                got = p.cells[name](*args)
            except Exception as err:        # reported, so the scan goes on
                faults.append(f"{where}: {name}{args} raised {_raised(err)}")
                continue
            if got != want or type(got) is not type(want):
                faults.append(f"{where}: {name}{args} = {got!r}, not {want!r}")
    read = {name: sorted(p.cells[name].keys()) for name in IN_COVER_ONLY
            if len(p.cells[name].keys())}
    if read:
        faults.append(f"{where}: evaluated outside cover: {read}")
    return faults


def test_every_guarded_cell_holds_its_outside_cover_value(spliced):
    """Outside cover each cell holds :data:`OUTSIDE_COVER`'s value, and reads no rate.

    On every committed point, in every month before issue and in the first month after
    cover, ``t = proj_len()``, which the count's look-ahead reads, on a model that evaluates
    nothing else.  So afterwards none of :data:`IN_COVER_ONLY` may hold a value at all:
    ``is_active``'s docstring promises that outside cover no count evaluates a rate, and no
    table is read at a policy year or an attained age the policy does not have.

    The committed table's one point issued after the valuation date is the RPI point, which
    has no paid-up value and is on the over-50s cell, so on it a cell tied to the paid-up
    strand or to the underwritten cell would hold zero before issue, guarded or not.  So
    the same scan runs on the splice's future rows, the core's or, with
    ``UKLIB_SEC_FULL=1``, all of them: the paid-up point, the underwritten one and the
    variants among them.  Each row is made afresh first and released after.

    Several of these guards change no number the frame shows: once the counts are zero
    outside cover, every cash flow is too, and an unguarded value multiplies a zero count.
    They are held here because they are what the docstrings promise a caller, and because
    the C step needs them: a table read at a policy year or an age the policy does not have
    would wrap round in a compiled model rather than fail (USLIB-SEC-PLAN.md F4, R1).
    """
    faults = []
    model = mx.read_model(model_path(SEC), name=_name("cover"))
    try:
        table = model.Data.model_point_table()
        for key, point_id in zip(point_keys(model), table.index):
            faults += _outside_cover_faults(projection(model, key), f"point {point_id}")
    finally:
        model.close()
    sec = spliced[1]
    futures = _selected(FUTURES, CORE_FUTURES)
    for s_point, k in futures:
        key = _row_key(sec, "future", s_point, -k)
        if key in sec.Projection.itemspaces:
            _release(sec, key)
        try:
            faults += _outside_cover_faults(projection(sec, key),
                                            _case_id("future", s_point, -k))
        finally:
            _release(sec, key)
    assert futures and not faults, (
        f"{len(faults)} faults outside cover, first:\n  " + "\n  ".join(faults[:20]))


def test_the_points_sum_row_by_row_into_a_block(spliced):
    """Row ``t`` is the same month on every point, so a block is its frames summed (D3).

    S point 1's twin, the point restated at month 12 and the point issued 12 months on,
    summed as ``run_sec.py --block`` sums them, are indexed 0..611 and equal S's frame added
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
    assert list(block.index) == list(range(612))
    assert frame_mismatches(expected, block) == []


# The labels an extract carries in the test below and in the malformed extract's: the
# committed points' in reverse, from 100 plus their number down to 101, so that a label is
# neither a position plus one nor in the order of the rows.
EXTRACT_LABELS = tuple(range(100 + len(_committed()), 100, -1))


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
    in ``result_cf`` and ``result_pols``, to 1e-12, and ``run_sec.py``, run beside that
    extract, prints the point without saying where it came from.  On every shipped row
    ``source_mth`` equals ``duration_mth``, so a formula that read the one for the other
    would pass every test that leaves ``duration_mth`` as generated.  And a refusal names
    the extract's label.
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
            for report in ("result_cf", "result_pols"):
                assert frame_mismatches(base.cells[report](), mine.cells[report](),
                                        rtol=1e-12, atol=1e-12) == [], (key, report)
            _release(model, key)
    finally:
        model.close()
    runner = folder.parent / "run_sec.py"
    shutil.copy(model_path(SEC).parent / "run_sec.py", runner)
    label = extract.index[extract["policy_id"] == "WOL-000003-M200"][0]
    out = _run_sec(runner, str(label))
    row = _row(sec_model, "derived", 3, 200)
    assert out.splitlines()[:2] == [
        f"model point {label}: WOL-000003-M200 - O50 cell, F70 smoker NS, level cover "
        f"5,000, premium 30.00 a month to policy month 240, pro-rata paid-up value",
        f"at the valuation date: in force 200 months: policy year 17, attained age 86, "
        f"{row.pols_if(0):.6f} on full cover, {row.pols_pu(0):.6f} paid-up"]
    last = extract.index[extract["policy_id"] == "WOL-000001-M166"][0]
    moved = _moved_on(last, 601)(extract)
    model = mx.read_model(_sec_inputs(tmp_path / "moved", moved), name=_name("moved"))
    try:
        _refused(_point(model, last).result_cf,
                 f"point_id {last}: duration_mth 601 is at or past the limiting age, policy "
                 f"month 600, omega_age 120")
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
            f"{p.age(0)}, {p.pols_if(0):.6f} on full cover, {p.pols_pu(0):.6f} paid-up")


def test_run_sec_prints_a_point_and_the_block(sec_model):
    """The runner prints one point, saying where it came from, and the block (D8).

    Each mode in an interpreter of its own, as a user runs it, with exit code 0 and ASCII
    output, so that it prints on a Windows console under any code page.  The numbers are
    the model's.  The anchor cell, the runner's default, with its lines at the valuation
    date, each asserted whole, so that a longer number cannot pass for the one asserted,
    and its first twelve rows of cash flows and counts.  Point 6, the underwritten
    increasing point, whose line says it pays for life; point 10, restated in force at S's
    month 200 with its paid-up strand; and point 14, to be issued 13 months on: each with
    the two lines that say where its row came from and where it stands, which only the
    committed table's generator columns can say.  And the block: a line for each committed
    point, in table order, its first twelve rows, which must be the committed points'
    frames summed row by row, as this test sums them, and those frames summed into
    projection years, each year's counts, on full cover and paid-up, the ones in force in
    its first month.  Nothing else runs the runner on the committed table.
    """
    runner = model_path(SEC).parent / "run_sec.py"
    out = _run_sec(runner)
    assert out.splitlines()[:3] == [
        "model point 1: WOL-000001 (S's WOL-000001) - O50 cell, F70 smoker NS, level cover "
        "5,000, premium 30.00 a month to policy month 240",
        "at the valuation date: issued at the valuation date, t = 0",
        "proj_len = 600 months from the valuation date (t = 0..599); the limiting age is "
        "policy month 600"]
    anchor = _row(sec_model, "twin", 1, 0)
    assert anchor.result_cf().head(12).round(2).to_string() in out
    assert anchor.result_pols().head(12).round(6).to_string() in out
    row = _row(sec_model, "derived", 3, 200)
    for point_id, lines in (
            ("6", ["model point 6: WOL-000006 (S's WOL-000006) - UW cell, M40 smoker NS, "
                   "fixed_5pct cover 150,000, premium 101.25 a month for life",
                   "at the valuation date: issued at the valuation date, t = 0"]),
            ("10", ["model point 10: WOL-000003-M200 (S's WOL-000003 at its month 200) - "
                    "O50 cell, F70 smoker NS, level cover 5,000, premium 30.00 a month to "
                    "policy month 240, pro-rata paid-up value",
                    f"at the valuation date: in force 200 months: policy year 17, attained "
                    f"age 86, {row.pols_if(0):.6f} on full cover, {row.pols_pu(0):.6f} "
                    f"paid-up"]),
            ("14", ["model point 14: WOL-000004-F13 (S's WOL-000004, issued 13 months on) - "
                    "O50 cell, F70 smoker NS, rpi cover 5,000, premium 30.00 a month to "
                    "policy month 240",
                    "at the valuation date: to be issued at t = 13, 13 months after the "
                    "valuation date"])):
        assert _run_sec(runner, point_id).splitlines()[:2] == lines, point_id
    out = _run_sec(runner, "--block")
    table = sec_model.Data.model_point_table()
    points = [projection(sec_model, key) for key in point_keys(sec_model)]
    assert out.splitlines()[:len(points) + 1] == [
        "model points, t = 0 the valuation date for each:",
        *("  {:>2}  {:<15} {}; proj_len {}".format(
            point_id, table.at[point_id, "policy_id"], _standing(p), p.proj_len())
          for point_id, p in zip(table.index, points))]
    block = pd.concat([p.result_cf() for p in points]).groupby(level="t").sum()
    assert block.head(12).round(2).to_string() in out
    years = pd.Index(block.index // 12 + 1, name="proj_year")
    annual = block.drop(columns=["pols_if", "pols_pu"]).groupby(years).sum()
    annual.insert(0, "pols_pu", [block.at[12 * (y - 1), "pols_pu"] for y in annual.index])
    annual.insert(0, "pols_if", [block.at[12 * (y - 1), "pols_if"] for y in annual.index])
    assert annual.head(12).round(2).to_string() in out


# run_sec.py run as though it sat at /m/products/whole_of_life, a copy too shallow to have
# a repository above it: the source compiled under that name, so that its own __file__ is
# it.
SHALLOW_RUN = """\
import sys
source = open(sys.argv[1], encoding="utf-8").read()
where = "/m/products/whole_of_life/run_sec.py"
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
    columns = list(frames[0].columns)
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

    ``WOL_UK_S`` defaults no other parameter, and running in force adds none: a compiled
    model declares a defaulted parameter in its ``.pxd`` as ``long long life=*``, which the
    C step's typing guard would read as a parameter of that name.  ``claims``'
    ``kind=None`` is R12's total, which the C step settles.
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
    outside the parentheses of the column, ``age`` of ``age(t)``.
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


# What only WOL_UK_S's docstrings may say: a reference into its Spaces, which the SEC pages
# would link to the wrong model; its clock, t counting policy months from issue, t = 0 the
# issue month, the policy year t // 12 + 1, and its anniversaries at t = 12, 24; and its
# frame of 12 x (omega_age - entry_age) months from t = 0.
STALE = re.compile(r"~\.WOL_UK_S\.|``t = 0`` is the issue month"
                   r"|``t`` counts \*\*policy months|t // 12 \+ 1|``t = 12, 24"
                   r"|``proj_len\(\) = 12 x|indexed by policy month ``t``")


def test_the_docstrings_describe_the_valuation_clock(sec_model, s_model):
    """The docstrings say what this model is, and none says what only WOL_UK_S is.

    Whitespace is collapsed first, as ``test_model_conventions_uk`` collapses it, so that a
    phrase split across a line break still matches.  The model docstring names the
    valuation date, BasicTerm_SE, the policy clock, the SEC table and the product.  The
    symbol map in the Projection docstring maps every cell running in force adds, which are
    exactly the cells ``WOL_UK_S`` lacks, and names nothing the model lacks: every name in
    it is a cell or a Reference.  No row of a simple table in any docstring puts text between
    two of its columns (:func:`_table_overruns`), which would drop the table from the
    rendered page.  And no docstring says what :data:`STALE` matches.
    """
    flat = {where: re.sub(r"\s+", " ", doc) for where, doc in _docs(sec_model)}
    for phrase in ("valuation date", "BasicTerm_SE", "duration_mth", TABLE,
                   "whole of life"):
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
    assert not stale, f"docstrings that describe WOL_UK_S: {stale}"


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
    reaches both models, and the two can never drift apart.
    """
    assert sec_model.Data.input_dir() == s_model.Data.input_dir()
    files = {r: v for r, v in s_model.Data.refs.items() if r.endswith("_file")}
    assert {r: v for r, v in sec_model.Data.refs.items() if r.endswith("_file")} == {
        **files, "model_point_file": TABLE}


# The policy month of each S point's and variant's crossover and first capped month, read
# off S at the shipped References: the static properties of the grid read them.
CROSSOVER = {1: 166, 2: 166, 3: 166, 4: 185, 5: -1, 6: 642, 7: 222, 8: 185, 9: 166,
             10: -1, 11: 642, 12: 166}
CAP = {1: 480, 2: 480, 3: 480, 4: 480, 5: 888, 6: 888, 7: 432, 8: 480, 9: 480, 10: 360,
       11: 852, 12: 480}


def test_the_core_grid_reaches_every_branch(spliced, splice_records):
    """What the default run's T2 and T3 cases reach, which the full grid only multiplies.

    The default run thins the splice to a core (the module docstring), and this test is
    what keeps the thinning from costing a branch.  First, statically, over S's table with
    the variants, each property below holds of some core case: both cells, every
    escalation, both sexes and smoker statuses on each cell, the paid-up value, the double
    accidental benefit, the paid-up value with RPI increases and with the double benefit,
    an entry age of its own; and each kind of valuation month: the first policy year, on an
    anniversary, in the month before one, mid-year, inside the moratorium and at its last
    month, at the crossover and past it, at cessation and past it, the first conversion, the
    cap and the last month before the limiting age.  And of some core future case: issued
    off the valuation anniversaries and on them, more than a year on, at the horizon, on
    each cell, with the paid-up value and with RPI increases.

    Then, on the splice's model, of some core row, each of :data:`AT_VALUATION` and
    :data:`IN_FRAME`, what no column of the table shows: every opening-state column in use,
    and each kind of valuation month the windows make; and every branch and both sides of
    every ``min`` and ``max`` the full grid reaches: the moratorium, the suicide window, an
    increase, cessation, commission, conversions, terminating lapses, paid-up deaths, the
    stress and the premiums paid either side of the cover, the lapse table inside and past
    its last year, the cap binding and not, the double benefit, the payments capped and the
    limiting age's last month.

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

    def o50(p):
        return at(p, "cell") == "O50"

    def cessation(p):
        return int(at(p, "cessation_months"))

    splices = {
        **{f"the {c} cell": (lambda k, p, d, c=c: at(p, "cell") == c) for c in ("O50", "UW")},
        **{f"{e} escalation": (lambda k, p, d, e=e: at(p, "escalation") == e)
           for e in ("level", "fixed_5pct", "rpi")},
        **{f"sex {x}, smoker {y} on the {c} cell": (
            lambda k, p, d, x=x, y=y, c=c: (at(p, "sex"), at(p, "smoker"), at(p, "cell"))
            == (x, y, c)) for x, y, c in (("F", "NS", "O50"), ("M", "S", "O50"),
                                          ("M", "NS", "UW"), ("F", "S", "UW"))},
        "the paid-up value": lambda k, p, d: flag(p, "variant_paid_up"),
        "the double accidental benefit": lambda k, p, d: flag(p, "variant_adb_2x"),
        "the paid-up value with RPI increases": lambda k, p, d: (
            flag(p, "variant_paid_up") and at(p, "escalation") == "rpi"),
        "the paid-up value with the double benefit": lambda k, p, d: (
            flag(p, "variant_paid_up") and flag(p, "variant_adb_2x")),
        "an entry age of 80": lambda k, p, d: int(at(p, "entry_age")) == 80,
        "an odd cessation": lambda k, p, d: cessation(p) % 2 == 1,
        "an escalating point past cessation": lambda k, p, d: (
            at(p, "escalation") != "level" and 0 < cessation(p) < d),
        "in the first policy year": lambda k, p, d: d < 12,
        "on an anniversary": lambda k, p, d: d % 12 == 0,
        "in the month before an anniversary": lambda k, p, d: d % 12 == 11,
        "mid-year": lambda k, p, d: d % 12 not in (0, 11),
        "inside the moratorium": lambda k, p, d: o50(p) and d < 12,
        "in the moratorium's last month": lambda k, p, d: o50(p) and d == 11,
        "at the crossover": lambda k, p, d: d == CROSSOVER[p],
        "past the crossover": lambda k, p, d: 0 <= CROSSOVER[p] < d,
        "at cessation": lambda k, p, d: d == cessation(p) > 0,
        "past cessation": lambda k, p, d: 0 < cessation(p) < d,
        "the first conversion": lambda k, p, d: (
            flag(p, "variant_paid_up") and d == cessation(p) // 2 - 1),
        "at the cap": lambda k, p, d: d == CAP[p],
        "in the last month before the limiting age": lambda k, p, d: d == COVER[p] - 1,
    }
    futures = {
        "issued off the anniversaries": lambda p, k: k % 12 != 0,
        "issued on them": lambda p, k: k % 12 == 0,
        "issued more than a year on": lambda p, k: k > 12,
        "issued at the horizon": lambda p, k: k == 120,
        "the over-50s cell": lambda p, k: at(p, "cell") == "O50",
        "the underwritten cell": lambda p, k: at(p, "cell") == "UW",
        "the paid-up value": lambda p, k: flag(p, "variant_paid_up"),
        "RPI increases": lambda p, k: at(p, "escalation") == "rpi",
        "fixed increases": lambda p, k: at(p, "escalation") == "fixed_5pct",
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


# ---------------------------------------------------------------------------
# C2 -- the Phase 1 fingerprint


def test_the_phase_1_fingerprint_is_reproduced(sec_model):
    """Every committed point computes what the model computed when its E step ended (C2).

    The C step changes how the model is represented and no number it computes
    (UKLIB-SEC-PLAN.md U2, after USLIB-SEC-PLAN.md D2), so before it changed anything the
    model as M5 committed it was frozen below (USLIB-SEC-PLAN.md §5.4): for each point,
    each column of ``result_cf()`` and ``result_pols()``, its sum, its largest absolute
    value and its values at five fixed months, the frame's first and last and the three
    quartiles between.  Every later version must reproduce it, to 1e-12 relative, floored
    at 1e-12 of the column's own magnitude (``uk_sec_support.fingerprint_mismatches``),
    with the same points, frames and columns exactly.  ``python
    tools/gen_sec_fingerprint.py WOL_UK_SEC --check`` runs the same comparison from the
    command line.
    """
    assert fingerprint_mismatches(FINGERPRINT, sec_model) == []


# WOL_UK_SEC's fingerprint, frozen from the model as M5 committed it and committed alone,
# before its C step changed anything.  Each point is keyed by its point_id; each column
# holds (its sum over the frame, its largest absolute value, (its values at the months)).
# The block is written by tools/gen_sec_fingerprint.py, and is never edited by hand: a
# refreeze goes through the tool's --force, in a commit of its own that says why.
# BEGIN generated fingerprint: WOL_UK_SEC -- tools/gen_sec_fingerprint.py
FINGERPRINT = {
    1: {"rows": 600, "months": (0, 149, 299, 449, 599),
        "result_cf": {
            "pols_if": (114.72542869134317, 1.0, (
                1.0, 0.32338578013476976, 0.03343488549823728, 5.265637242601398e-06, 0.0)),
            "pols_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "premiums": (3296.8393833512946, 30.0, (
                30.0, 9.701573404043092, 0.0, 0.0, 0.0)),
            "claims_death": (2742.7905913148893, 11.286308984382895, (
                0.3622016939630002, 10.517455501513004, 3.715375696228344,
                0.003464980967042672, 0.0)),
            "claims_death_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_lapse": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (509.1278461695021, 152.5, (
                152.5, 1.1526769916959823, 0.16991559547748794, 3.929780193114011e-05,
                0.0)),
            "commissions": (85.70735294691069, 7.5, (
                7.5, 0.0, 0.0, 0.0, 0.0)),
            "net_cf": (-40.786407080007365, 130.36220169396302, (
                -130.36220169396302, -1.9685590891658937, -3.885291291705832,
                -0.003504278768973812, 0.0)),
        },
        "result_pols": {
            "pols_if": (114.72542869134317, 1.0, (
                1.0, 0.32338578013476976, 0.03343488549823728, 5.265637242601398e-06, 0.0)),
            "pols_new_biz": (1.0, 1.0, (
                1.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_death": (0.5701155297708609, 0.002257261796876579, (
                0.002022343349877165, 0.0021034911003026007, 0.0007430751392456689,
                6.929961934085344e-07, 0.0)),
            "pols_death_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_lapse": (0.4298844702291391, 0.006910379149139073, (
                0.006910379149139073, 0.001091091745431058, 0.0, 0.0, 0.0)),
            "pols_convert": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_maturity": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "prem_cum_pp": (3459600.0, 7200.0, (
                30.0, 4500.0, 7200.0, 7200.0, 7200.0)),
            "cover_pp": (3000000.0, 5000.0, (
                5000.0, 5000.0, 5000.0, 5000.0, 5000.0)),
            "benefit_death_pp": (2944069.8, 5000.0, (
                179.1, 5000.0, 5000.0, 5000.0, 5000.0)),
            "mort_rate": (247.46665603728002, 1.0, (
                0.024, 0.07532228099999999, 0.2363935842, 0.81609476604, 1.0)),
            "lapse_rate": (10.32, 0.08, (
                0.08, 0.04, 0.0, 0.0, 0.0)),
        },
    },
    2: {"rows": 600, "months": (0, 149, 299, 449, 599),
        "result_cf": {
            "pols_if": (114.72542869134317, 1.0, (
                1.0, 0.32338578013476976, 0.03343488549823728, 5.265637242601398e-06, 0.0)),
            "pols_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "premiums": (3296.8393833512946, 30.0, (
                30.0, 9.701573404043092, 0.0, 0.0, 0.0)),
            "claims_death": (2824.841326875163, 11.624898253914383, (
                0.3622016939630002, 10.832979166558394, 3.8268369671151947,
                0.0035689303960539523, 0.0)),
            "claims_death_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_lapse": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (509.1278461695021, 152.5, (
                152.5, 1.1526769916959823, 0.16991559547748794, 3.929780193114011e-05,
                0.0)),
            "commissions": (85.70735294691069, 7.5, (
                7.5, 0.0, 0.0, 0.0, 0.0)),
            "net_cf": (-122.83714264028123, 130.36220169396302, (
                -130.36220169396302, -2.284082754211284, -3.9967525625926825,
                -0.0036082281979850925, 0.0)),
        },
        "result_pols": {
            "pols_if": (114.72542869134317, 1.0, (
                1.0, 0.32338578013476976, 0.03343488549823728, 5.265637242601398e-06, 0.0)),
            "pols_new_biz": (1.0, 1.0, (
                1.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_death": (0.5701155297708609, 0.002257261796876579, (
                0.002022343349877165, 0.0021034911003026007, 0.0007430751392456689,
                6.929961934085344e-07, 0.0)),
            "pols_death_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_lapse": (0.4298844702291391, 0.006910379149139073, (
                0.006910379149139073, 0.001091091745431058, 0.0, 0.0, 0.0)),
            "pols_convert": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_maturity": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "prem_cum_pp": (3459600.0, 7200.0, (
                30.0, 4500.0, 7200.0, 7200.0, 7200.0)),
            "cover_pp": (3000000.0, 5000.0, (
                5000.0, 5000.0, 5000.0, 5000.0, 5000.0)),
            "benefit_death_pp": (3032269.8, 5150.0, (
                179.1, 5150.0, 5150.0, 5150.0, 5150.0)),
            "mort_rate": (247.46665603728002, 1.0, (
                0.024, 0.07532228099999999, 0.2363935842, 0.81609476604, 1.0)),
            "lapse_rate": (10.32, 0.08, (
                0.08, 0.04, 0.0, 0.0, 0.0)),
        },
    },
    3: {"rows": 600, "months": (0, 149, 299, 449, 599),
        "result_cf": {
            "pols_if": (114.72542869134317, 1.0, (
                1.0, 0.32338578013476976, 0.03343488549823728, 5.265637242601398e-06, 0.0)),
            "pols_pu": (7.722306625015724, 0.05732805609862964, (
                0.0, 0.03474597957753035, 0.0170271665376639, 2.681596808860805e-06, 0.0)),
            "premiums": (3296.8393833512946, 30.0, (
                30.0, 9.701573404043092, 0.0, 0.0, 0.0)),
            "claims_death": (2742.7905913148893, 11.286308984382895, (
                0.3622016939630002, 10.517455501513004, 3.715375696228344,
                0.003464980967042672, 0.0)),
            "claims_death_pu": (344.601138660018, 2.671127347993102, (
                0.0, 0.6320942172298808, 1.3864514174568086, 0.0012930126495939481, 0.0)),
            "claims_lapse": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (541.974134943921, 152.5, (
                152.5, 1.2765256383379795, 0.2564474049461954, 5.931073776371327e-05, 0.0)),
            "commissions": (85.70735294691069, 7.5, (
                7.5, 0.0, 0.0, 0.0, 0.0)),
            "net_cf": (-418.2338345144443, 130.36220169396302, (
                -130.36220169396302, -2.7245019530377714, -5.358274518631348,
                -0.004817304354400333, 0.0)),
        },
        "result_pols": {
            "pols_if": (114.72542869134317, 1.0, (
                1.0, 0.32338578013476976, 0.03343488549823728, 5.265637242601398e-06, 0.0)),
            "pols_new_biz": (1.0, 1.0, (
                1.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_pu": (7.722306625015724, 0.05732805609862964, (
                0.0, 0.03474597957753035, 0.0170271665376639, 2.681596808860805e-06, 0.0)),
            "pols_death": (0.5701155297708609, 0.002257261796876579, (
                0.002022343349877165, 0.0021034911003026007, 0.0007430751392456689,
                6.929961934085344e-07, 0.0)),
            "pols_death_pu": (0.09946495445807699, 0.0007290632593001773, (
                0.0, 0.0002260082641301418, 0.00037842104010198704, 3.5291766127795995e-07,
                0.0)),
            "pols_lapse": (0.33041951577106216, 0.006910379149139073, (
                0.006910379149139073, 0.0, 0.0, 0.0, 0.0)),
            "pols_convert": (0.09946495445807695, 0.0014384879451534512, (
                0.0, 0.001091091745431058, 0.0, 0.0, 0.0)),
            "pols_maturity": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "prem_cum_pp": (3459600.0, 7200.0, (
                30.0, 4500.0, 7200.0, 7200.0, 7200.0)),
            "cover_pp": (3000000.0, 5000.0, (
                5000.0, 5000.0, 5000.0, 5000.0, 5000.0)),
            "benefit_death_pp": (2944069.8, 5000.0, (
                179.1, 5000.0, 5000.0, 5000.0, 5000.0)),
            "mort_rate": (247.46665603728002, 1.0, (
                0.024, 0.07532228099999999, 0.2363935842, 0.81609476604, 1.0)),
            "lapse_rate": (10.32, 0.08, (
                0.08, 0.04, 0.0, 0.0, 0.0)),
        },
    },
    4: {"rows": 600, "months": (0, 149, 299, 449, 599),
        "result_cf": {
            "pols_if": (114.72542869134317, 1.0, (
                1.0, 0.32338578013476976, 0.03343488549823728, 5.265637242601398e-06, 0.0)),
            "pols_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "premiums": (4476.866602558695, 30.0, (
                30.0, 16.452718204551218, 0.0, 0.0, 0.0)),
            "claims_death": (4019.710590529493, 15.934062393626284, (
                0.3622016939630002, 14.995376683202407, 7.552593818579198,
                0.010343753621033163, 0.0)),
            "claims_death_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_lapse": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (509.1278461695021, 152.5, (
                152.5, 1.1526769916959823, 0.16991559547748794, 3.929780193114011e-05,
                0.0)),
            "commissions": (85.70735294691069, 7.5, (
                7.5, 0.0, 0.0, 0.0, 0.0)),
            "net_cf": (-137.6791870872106, 130.36220169396302, (
                -130.36220169396302, 0.30466452965282853, -7.722509414056686,
                -0.010383051422964303, 0.0)),
        },
        "result_pols": {
            "pols_if": (114.72542869134317, 1.0, (
                1.0, 0.32338578013476976, 0.03343488549823728, 5.265637242601398e-06, 0.0)),
            "pols_new_biz": (1.0, 1.0, (
                1.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_death": (0.5701155297708609, 0.002257261796876579, (
                0.002022343349877165, 0.0021034911003026007, 0.0007430751392456689,
                6.929961934085344e-07, 0.0)),
            "pols_death_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_lapse": (0.4298844702291391, 0.006910379149139073, (
                0.006910379149139073, 0.001091091745431058, 0.0, 0.0, 0.0)),
            "pols_convert": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_maturity": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "prem_cum_pp": (5230802.107143078, 11293.712198699246, (
                30.0, 5872.310120041152, 11293.712198699246, 11293.712198699246,
                11293.712198699246)),
            "cover_pp": (6767812.037414186, 21281.097178189782, (
                5000.0, 7128.804434230897, 10163.97053230202, 14926.133389213763,
                21281.097178189782)),
            "benefit_death_pp": (6711881.837414185, 21281.097178189782, (
                179.1, 7128.804434230896, 10163.970532302019, 14926.133389213763,
                21281.097178189782)),
            "mort_rate": (247.46665603728002, 1.0, (
                0.024, 0.07532228099999999, 0.2363935842, 0.81609476604, 1.0)),
            "lapse_rate": (10.32, 0.08, (
                0.08, 0.04, 0.0, 0.0, 0.0)),
        },
    },
    5: {"rows": 960, "months": (0, 239, 479, 719, 959),
        "result_cf": {
            "pols_if": (308.58218922392905, 1.0, (
                1.0, 0.5728814419221651, 0.2700455819277968, 0.014630523250624694, 0.0)),
            "pols_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "premiums": (31243.946658922818, 101.25, (
                101.25, 58.00424599461921, 27.342115170189427, 1.4813404791257503, 0.0)),
            "claims_death": (57996.165313486155, 161.45180244556863, (
                11.142172830996692, 39.51631272158369, 127.17144792767878,
                51.777039859802365, 0.0)),
            "claims_death_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_lapse": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (2749.8560487432596, 304.1666666666667, (
                304.1666666666667, 4.1856294837752275, 3.5635068519856654,
                0.34869432118605953, 0.0)),
            "commissions": (295.1830886463622, 25.3125, (
                25.3125, 0.0, 0.0, 0.0, 0.0)),
            "net_cf": (-29797.257791952958, 239.37133949766337, (
                -239.37133949766337, 14.302303789260296, -103.39283960947502,
                -50.644393701862676, 0.0)),
        },
        "result_pols": {
            "pols_if": (308.58218922392905, 1.0, (
                1.0, 0.5728814419221651, 0.2700455819277968, 0.014630523250624694, 0.0)),
            "pols_new_biz": (1.0, 1.0, (
                1.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_death": (0.3866498138438875, 0.0010763453496371242, (
                7.503095530070336e-05, 0.0002634420848105579, 0.0008478096528511919,
                0.00034518026573201576, 0.0)),
            "pols_death_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_lapse": (0.6133501861561121, 0.0051426269466570505, (
                0.0051426269466570505, 0.0009632251039910364, 0.00045282902784638354,
                2.4029983315367736e-05, 0.0)),
            "pols_convert": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_maturity": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "prem_cum_pp": (46704600.0, 97200.0, (
                101.25, 24300.0, 48600.0, 72900.0, 97200.0)),
            "cover_pp": (144000000.0, 150000.0, (
                150000.0, 150000.0, 150000.0, 150000.0, 150000.0)),
            "benefit_death_pp": (143982078.975, 150000.0, (
                148501.0125, 150000.0, 150000.0, 150000.0, 150000.0)),
            "mort_rate": (196.7690000964, 1.0, (
                0.0009, 0.0055043181, 0.0370303, 0.2491213414, 1.0)),
            "lapse_rate": (20.4, 0.06, (
                0.06, 0.02, 0.02, 0.02, 0.02)),
        },
    },
    6: {"rows": 960, "months": (0, 239, 479, 719, 959),
        "result_cf": {
            "pols_if": (308.58218922392905, 1.0, (
                1.0, 0.5728814419221651, 0.2700455819277968, 0.014630523250624694, 0.0)),
            "pols_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "premiums": (503632.0380498866, 1399.4122141697894, (
                101.25, 354.7486927177009, 1124.9852529655527, 410.0372525484368, 0.0)),
            "claims_death": (486045.1197572478, 1827.8101935618524, (
                11.142172830996692, 99.85575415233079, 852.6529123003878, 921.0980500844421,
                0.0)),
            "claims_death_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_lapse": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (2749.8560487432596, 304.1666666666667, (
                304.1666666666667, 4.1856294837752275, 3.5635068519856654,
                0.34869432118605953, 0.0)),
            "commissions": (295.1830886463622, 25.3125, (
                25.3125, 0.0, 0.0, 0.0, 0.0)),
            "net_cf": (14541.879155249087, 760.1188542795003, (
                -239.37133949766337, 250.7073090815949, 268.76883381317924,
                -511.40949185719137, 0.0)),
        },
        "result_pols": {
            "pols_if": (308.58218922392905, 1.0, (
                1.0, 0.5728814419221651, 0.2700455819277968, 0.014630523250624694, 0.0)),
            "pols_new_biz": (1.0, 1.0, (
                1.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_death": (0.3866498138438875, 0.0010763453496371242, (
                7.503095530070336e-05, 0.0002634420848105579, 0.0008478096528511919,
                0.00034518026573201576, 0.0)),
            "pols_death_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_lapse": (0.6133501861561121, 0.0051426269466570505, (
                0.0051426269466570505, 0.0009632251039910364, 0.00045282902784638354,
                2.4029983315367736e-05, 0.0)),
            "pols_convert": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_maturity": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "prem_cum_pp": (3135138944.8125124, 24875912.607213527, (
                101.25, 69589.12438430607, 537749.9551533383, 3687301.9204282453,
                24875912.607213527)),
            "cover_pp": (1748211878.4063323, 7080205.8666918, (
                150000.0, 379042.529306346, 1005712.6731606653, 2668455.127731856,
                7080205.8666918)),
            "benefit_death_pp": (1748193957.3813324, 7080205.8666918, (
                148501.0125, 379042.529306346, 1005712.6731606653, 2668455.127731856,
                7080205.8666918)),
            "mort_rate": (196.7690000964, 1.0, (
                0.0009, 0.0055043181, 0.0370303, 0.2491213414, 1.0)),
            "lapse_rate": (20.4, 0.06, (
                0.06, 0.02, 0.02, 0.02, 0.02)),
        },
    },
    7: {"rows": 660, "months": (0, 164, 329, 494, 659),
        "result_cf": {
            "pols_if": (98.78170848228129, 1.0, (
                1.0, 0.20455288798561502, 0.002167274414410266, 0.0, 0.0)),
            "pols_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "premiums": (4437.558965477801, 45.0, (
                45.0, 9.204879959352676, 0.0, 0.0, 0.0)),
            "claims_death": (5780.4632888393735, 29.36945527351167, (
                1.0061256623035115, 21.55134726383172, 1.063458608812075, 0.0, 0.0)),
            "claims_death_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_lapse": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (448.4886255712781, 152.5, (
                152.5, 0.750982030476893, 0.012035357071957567, 0.0, 0.0)),
            "commissions": (127.93387212352953, 11.25, (
                11.25, 0.0, 0.0, 0.0, 0.0)),
            "net_cf": (-1919.3268210563792, 119.7561256623035, (
                -119.7561256623035, -13.097449334955936, -1.0754939658840326, 0.0, 0.0)),
        },
        "result_pols": {
            "pols_if": (98.78170848228129, 1.0, (
                1.0, 0.20455288798561502, 0.002167274414410266, 0.0, 0.0)),
            "pols_new_biz": (1.0, 1.0, (
                1.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_death": (0.6094141934830261, 0.002936945527351167, (
                0.002927762730404515, 0.002155134726383172, 0.00010634586088120749, 0.0,
                0.0)),
            "pols_death_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_lapse": (0.3905858065169741, 0.006904109678909223, (
                0.006904109678909223, 0.0006873535374097411, 0.0, 0.0, 0.0)),
            "pols_convert": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_maturity": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "prem_cum_pp": (6891750.0, 13500.0, (
                45.0, 7425.0, 13500.0, 13500.0, 13500.0)),
            "cover_pp": (6600000.0, 10000.0, (
                10000.0, 10000.0, 10000.0, 10000.0, 10000.0)),
            "benefit_death_pp": (6487004.7, 10000.0, (
                343.65, 10000.0, 10000.0, 10000.0, 10000.0)),
            "mort_rate": (352.10017090992, 1.0, (
                0.03457289928, 0.11935502495999999, 0.45325050864, 1.0, 1.0)),
            "lapse_rate": (12.719999999999999, 0.08, (
                0.08, 0.04, 0.0, 0.0, 0.0)),
        },
    },
    8: {"rows": 594, "months": (0, 148, 296, 444, 593),
        "result_cf": {
            "pols_if": (108.85783431166041, 0.9475864076695066, (
                0.9475864076695066, 0.3077253423036933, 0.03109145420377051,
                4.572641049192864e-06, 0.0)),
            "pols_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "premiums": (3120.8115519608123, 28.4275922300852, (
                28.4275922300852, 9.231760269110799, 0.0, 0.0, 0.0)),
            "claims_death": (2739.811102637476, 11.286308984382895, (
                0.6778112512534888, 10.008132061397868, 3.8527782412534606,
                0.0030089642477429367, 0.0)),
            "claims_death_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_lapse": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (339.5092134322118, 2.3689660191737665, (
                2.3689660191737665, 1.0968568923698947, 0.1580063121667706,
                3.412592512062353e-05, 0.0)),
            "commissions": (41.700395099290155, 7.1068980575213, (
                7.1068980575213, 0.0, 0.0, 0.0, 0.0)),
            "net_cf": (-0.20915920816506173, 18.273916902136648, (
                18.273916902136648, -1.8732286846569637, -4.0107845534202315,
                -0.0030430901728635603, 0.0)),
        },
        "result_pols": {
            "pols_if": (108.85783431166041, 0.9475864076695066, (
                0.9475864076695066, 0.3077253423036933, 0.03109145420377051,
                4.572641049192864e-06, 0.0)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_death": (0.5582492392973328, 0.002257261796876579, (
                0.0019163450699844187, 0.0020016264122795736, 0.0007705556482506921,
                6.017928495485873e-07, 0.0)),
            "pols_death_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_lapse": (0.3893371683721738, 0.006548181353566956, (
                0.006548181353566956, 0.0010382540033379987, 0.0, 0.0, 0.0)),
            "pols_convert": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_maturity": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "prem_cum_pp": (3458970.0, 7200.0, (
                210.0, 4650.0, 7200.0, 7200.0, 7200.0)),
            "cover_pp": (2970000.0, 5000.0, (
                5000.0, 5000.0, 5000.0, 5000.0, 5000.0)),
            "benefit_death_pp": (2942558.7, 5000.0, (
                353.7, 5000.0, 5000.0, 5000.0, 5000.0)),
            "mort_rate": (247.32265603728, 1.0, (
                0.024, 0.07532228099999999, 0.26003294268, 0.81609476604, 1.0)),
            "lapse_rate": (9.84, 0.08, (
                0.08, 0.04, 0.0, 0.0, 0.0)),
        },
    },
    9: {"rows": 434, "months": (0, 108, 216, 324, 433),
        "result_cf": {
            "pols_if": (18.015819242028112, 0.27130934818144503, (
                0.27130934818144503, 0.05654313507900997, 0.0016654512969787995, 0.0, 0.0)),
            "pols_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "premiums": (395.55109987184323, 8.139280445443351, (
                8.139280445443351, 0.0, 0.0, 0.0, 0.0)),
            "claims_death": (1134.84656953584, 10.534292367451181, (
                9.742065844452595, 5.075020360965567, 0.4176135699604161, 0.0, 0.0)),
            "claims_death_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_lapse": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (50.857325198769864, 0.6782733704536126, (
                0.6782733704536126, 0.18443991595181725, 0.007088298374653967, 0.0, 0.0)),
            "commissions": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "net_cf": (-790.1527948627665, 7.451380813889131, (
                -2.281058769462857, -5.259460276917384, -0.42470186833507007, 0.0, 0.0)),
        },
        "result_pols": {
            "pols_if": (18.015819242028112, 0.27130934818144503, (
                0.27130934818144503, 0.05654313507900997, 0.0016654512969787995, 0.0, 0.0)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_death": (0.22696931390716799, 0.0021068584734902362, (
                0.0019484131688905192, 0.0010150040721931134, 8.352271399208322e-05, 0.0,
                0.0)),
            "pols_death_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_lapse": (0.04434003427427714, 0.0009147640650128105, (
                0.0009147640650128105, 0.0, 0.0, 0.0, 0.0)),
            "pols_convert": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_maturity": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "prem_cum_pp": (3043770.0, 7200.0, (
                5010.0, 7200.0, 7200.0, 7200.0, 7200.0)),
            "cover_pp": (2170000.0, 5000.0, (
                5000.0, 5000.0, 5000.0, 5000.0, 5000.0)),
            "benefit_death_pp": (2170000.0, 5000.0, (
                5000.0, 5000.0, 5000.0, 5000.0, 5000.0)),
            "mort_rate": (239.57556984936, 1.0, (
                0.08285450916, 0.19536659856, 0.46066421987999995, 1.0, 1.0)),
            "lapse_rate": (2.96, 0.04, (
                0.04, 0.0, 0.0, 0.0, 0.0)),
        },
    },
    10: {"rows": 400, "months": (0, 99, 199, 299, 399),
        "result_cf": {
            "pols_if": (10.346690223563272, 0.18020175881063383, (
                0.18020175881063383, 0.03343488549823728, 0.0006045439654619611, 0.0, 0.0)),
            "pols_pu": (4.661759492952453, 0.05732805609862964, (
                0.057169538009509614, 0.0170271665376639, 0.00030787217081402124, 0.0,
                0.0)),
            "premiums": (165.47722931789804, 5.406052764319015, (
                5.406052764319015, 0.0, 0.0, 0.0, 0.0)),
            "claims_death": (808.4239246949178, 9.163270837802965, (
                8.730827346033395, 3.715375696228344, 0.19849970829825014, 0.0, 0.0)),
            "claims_death_pu": (272.64141565070156, 2.671127347993102, (
                1.8251514680133294, 1.3864514174568086, 0.074073317057613, 0.0, 0.0)),
            "claims_lapse": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (41.76254963938744, 0.5934282420503586, (
                0.5934282420503586, 0.15980954441126166, 0.0036604001225492657, 0.0, 0.0)),
            "commissions": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "net_cf": (-957.3506606671089, 10.234335809638676, (
                -5.743354291778068, -5.261636658096415, -0.2762334254784124, 0.0, 0.0)),
        },
        "result_pols": {
            "pols_if": (10.346690223563272, 0.18020175881063383, (
                0.18020175881063383, 0.03343488549823728, 0.0006045439654619611, 0.0, 0.0)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_pu": (4.661759492952453, 0.05732805609862964, (
                0.057169538009509614, 0.0170271665376639, 0.00030787217081402124, 0.0,
                0.0)),
            "pols_death": (0.16168478493898353, 0.0018326541675605932, (
                0.0017461654692066792, 0.0007430751392456689, 3.969994165965003e-05, 0.0,
                0.0)),
            "pols_death_pu": (0.07568651188116, 0.0007290632593001773, (
                0.000553976131096527, 0.00037842104010198704, 2.0217730914916414e-05, 0.0,
                0.0)),
            "pols_lapse": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_convert": (0.01851697387165037, 0.0006060446886318847, (
                0.0006060446886318847, 0.0, 0.0, 0.0, 0.0)),
            "pols_maturity": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "prem_cum_pp": (2856600.0, 7200.0, (
                6030.0, 7200.0, 7200.0, 7200.0, 7200.0)),
            "cover_pp": (2000000.0, 5000.0, (
                5000.0, 5000.0, 5000.0, 5000.0, 5000.0)),
            "benefit_death_pp": (2000000.0, 5000.0, (
                5000.0, 5000.0, 5000.0, 5000.0, 5000.0)),
            "mort_rate": (236.23089902447998, 1.0, (
                0.11027935164000001, 0.2363935842, 0.55740370608, 1.0, 1.0)),
            "lapse_rate": (1.6, 0.04, (
                0.04, 0.0, 0.0, 0.0, 0.0)),
        },
    },
    11: {"rows": 414, "months": (0, 103, 206, 309, 413),
        "result_cf": {
            "pols_if": (13.130544205870645, 0.21538403111628068, (
                0.21538403111628068, 0.04186089727076868, 0.0009380613326661115, 0.0, 0.0)),
            "pols_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "premiums": (525.6334139256243, 12.504868018246096, (
                12.504868018246096, 0.0, 0.0, 0.0, 0.0)),
            "claims_death": (1730.9208986171625, 15.563277464552115, (
                14.705844670080682, 9.455942476131838, 0.6907498563377353, 0.0, 0.0)),
            "claims_death_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_lapse": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (36.67748811721925, 0.5384600777907017, (
                0.5384600777907017, 0.1325703306066257, 0.0038761811315571656, 0.0, 0.0)),
            "commissions": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "net_cf": (-1241.9649728087575, 13.204697714115694, (
                -2.739436729625287, -9.588512806738464, -0.6946260374692925, 0.0, 0.0)),
        },
        "result_pols": {
            "pols_if": (13.130544205870645, 0.21538403111628068, (
                0.21538403111628068, 0.04186089727076868, 0.0009380613326661115, 0.0, 0.0)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_death": (0.18750061294798873, 0.0019397039963636633, (
                0.0018878244196103248, 0.0009303394225790007, 5.364875010814619e-05, 0.0,
                0.0)),
            "pols_death_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_lapse": (0.02788341816829203, 0.0007250444757089917, (
                0.0007250444757089917, 0.0, 0.0, 0.0, 0.0)),
            "pols_convert": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_maturity": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "prem_cum_pp": (4580785.422967019, 11293.712198699246, (
                7888.668857778385, 11293.712198699246, 11293.712198699246,
                11293.712198699246, 11293.712198699246)),
            "cover_pp": (5605138.1817146335, 21281.097178189782, (
                7789.837083003826, 10163.970532302019, 12875.413778425564,
                16799.49462879525, 21281.097178189782)),
            "benefit_death_pp": (5605138.181714633, 21281.097178189782, (
                7789.837083003826, 10163.970532302019, 12875.413778425562,
                16799.49462879525, 21281.097178189782)),
            "mort_rate": (237.71465757407998, 1.0, (
                0.10025395608, 0.2363935842, 0.50673064188, 1.0, 1.0)),
            "lapse_rate": (2.16, 0.04, (
                0.04, 0.0, 0.0, 0.0, 0.0)),
        },
    },
    12: {"rows": 948, "months": (0, 236, 473, 710, 947),
        "result_cf": {
            "pols_if": (296.9206351045666, 0.9391540000000004, (
                0.9391540000000004, 0.5617281575281621, 0.26191431207585203,
                0.013474623012090353, 0.0)),
            "pols_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "premiums": (502451.30569530115, 1399.4122141697896, (
                104.59827675000005, 382.62639781967977, 1200.222237204407, 415.405999826036,
                0.0)),
            "claims_death": (485915.17988846486, 1827.8101935618524, (
                12.208672963559183, 113.11667034715332, 956.8367358331229,
                994.2448036293056, 0.0)),
            "claims_death_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_lapse": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (2331.32644651707, 4.21727583614519, (
                3.9131416666666685, 4.104140518372834, 3.4562070560552987,
                0.32114535098656055, 0.0)),
            "commissions": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "net_cf": (14204.79936031923, 760.0926553106705, (
                88.4764621197742, 265.4055869541536, 239.92929431522884, -579.1599491542561,
                0.0)),
        },
        "result_pols": {
            "pols_if": (296.9206351045666, 0.9391540000000004, (
                0.9391540000000004, 0.5617281575281621, 0.26191431207585203,
                0.013474623012090353, 0.0)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_death": (0.38577483629802095, 0.0010763453496371242, (
                7.751538389561386e-05, 0.0002842165559430285, 0.0009060968466092433,
                0.00035484944196350064, 0.0)),
            "pols_death_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_lapse": (0.5533791637019793, 0.004005460563398711, (
                0.004005460563398711, 0.0009444287440871752, 0.0004390530254517186,
                2.2069329404618374e-05, 0.0)),
            "pols_convert": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_maturity": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "prem_cum_pp": (3135131047.312513, 24875912.607213527, (
                1326.375, 75719.55871312901, 565244.9529110052, 3779788.2184389513,
                24875912.607213527)),
            "cover_pp": (1746411878.406332, 7080205.8666918, (
                157500.0, 397994.65577166335, 1055998.3068186985, 2801877.884118449,
                7080205.8666918)),
            "benefit_death_pp": (1746411878.406332, 7080205.8666918, (
                157500.0, 397994.65577166335, 1055998.3068186985, 2801877.884118449,
                7080205.8666918)),
            "mort_rate": (196.7582000964, 1.0, (
                0.00099, 0.00605475, 0.04073333, 0.2740334756, 1.0)),
            "lapse_rate": (19.68, 0.05, (
                0.05, 0.02, 0.02, 0.02, 0.02)),
        },
    },
    13: {"rows": 360, "months": (0, 89, 179, 269, 359),
        "result_cf": {
            "pols_if": (0.16928702721902053, 0.007579814271932304, (
                0.007579814271932304, 2.66879672345351e-05, 0.0, 0.0, 0.0)),
            "pols_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "premiums": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_death": (75.79814271932307, 2.9073855572538516, (
                2.9073855572538516, 0.02758451816315208, 0.0, 0.0, 0.0)),
            "claims_death_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_lapse": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (0.43759912339065327, 0.018949535679830758, (
                0.018949535679830758, 8.205708355767492e-05, 0.0, 0.0, 0.0)),
            "commissions": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "net_cf": (-76.23574184271372, 2.9263350929336824, (
                -2.9263350929336824, -0.027666575246709756, 0.0, 0.0, 0.0)),
        },
        "result_pols": {
            "pols_if": (0.16928702721902053, 0.007579814271932304, (
                0.007579814271932304, 2.66879672345351e-05, 0.0, 0.0, 0.0)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_death": (0.0075798142719323055, 0.00029073855572538516, (
                0.00029073855572538516, 2.758451816315208e-06, 0.0, 0.0, 0.0)),
            "pols_death_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_lapse": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_convert": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_maturity": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "prem_cum_pp": (4860000.0, 13500.0, (
                13500.0, 13500.0, 13500.0, 13500.0, 13500.0)),
            "cover_pp": (3600000.0, 10000.0, (
                10000.0, 10000.0, 10000.0, 10000.0, 10000.0)),
            "benefit_death_pp": (3600000.0, 10000.0, (
                10000.0, 10000.0, 10000.0, 10000.0, 10000.0)),
            "mort_rate": (311.29845516048, 1.0, (
                0.37458719712, 0.7299644766, 1.0, 1.0, 1.0)),
            "lapse_rate": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
        },
    },
    14: {"rows": 613, "months": (0, 153, 306, 459, 612),
        "result_cf": {
            "pols_if": (114.72542869134317, 1.0, (
                0.0, 0.3527415575057059, 0.03826176992717273, 8.04085840041836e-06, 0.0)),
            "pols_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "premiums": (4476.866602558695, 30.0, (
                0.0, 17.173431328407993, 0.0, 0.0, 0.0)),
            "claims_death": (4019.7105905294925, 15.934062393626284, (
                0.0, 14.388461707963344, 8.64293694246685, 0.015795364238659997, 0.0)),
            "claims_death_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_lapse": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (520.779713765115, 152.575, (
                0.0, 1.2573127896420944, 0.20027912355755415, 6.18097463999386e-05, 0.0)),
            "commissions": (85.7073529469107, 7.5, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "net_cf": (-149.3310546828236, 130.437201693963, (
                0.0, 1.5276568308025544, -8.843216066024404, -0.015857173985059935, 0.0)),
        },
        "result_pols": {
            "pols_if": (114.72542869134317, 1.0, (
                0.0, 0.3527415575057059, 0.03826176992717273, 8.04085840041836e-06, 0.0)),
            "pols_new_biz": (1.0, 1.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_death": (0.5701155297708609, 0.002257261796876579, (
                0.0, 0.002078906175071857, 0.0008503504526108979, 1.0582355005667024e-06,
                0.0)),
            "pols_death_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_lapse": (0.42988447022913906, 0.006910379149139073, (
                0.0, 0.0011908690187923125, 0.0, 0.0, 0.0)),
            "pols_convert": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_maturity": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "prem_cum_pp": (5230802.107143078, 11293.712198699246, (
                0.0, 5420.994688028956, 11293.712198699246, 11293.712198699246,
                11293.712198699246)),
            "cover_pp": (6767812.037414186, 21281.097178189782, (
                0.0, 6921.169353622229, 10163.97053230202, 14926.133389213763,
                21281.097178189782)),
            "benefit_death_pp": (6711881.837414185, 21281.097178189782, (
                0.0, 6921.169353622229, 10163.970532302019, 14926.133389213763,
                21281.097178189782)),
            "mort_rate": (247.46665603728, 1.0, (
                0.0, 0.06847480092, 0.2363935842, 0.81609476604, 1.0)),
            "lapse_rate": (10.32, 0.08, (
                0.0, 0.04, 0.0, 0.0, 0.0)),
        },
    },
    15: {"rows": 480, "months": (0, 119, 239, 359, 479),
        "result_cf": {
            "pols_if": (33.921439348243936, 0.422137899377621, (
                0.422137899377621, 0.09992331667213186, 0.004988714607953328,
                3.619333640475052e-09, 0.0)),
            "pols_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "premiums": (2103.1937298891007, 26.101186026095633, (
                26.101186026095633, 9.181620790703636, 0.0, 0.0, 0.0)),
            "claims_death": (3287.462007426172, 19.312889562653634, (
                18.365102007192196, 13.954060684981311, 2.788956054473979,
                2.1242886866084678e-05, 0.0)),
            "claims_death_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_lapse": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (98.28471802324961, 1.0553447484440523, (
                1.0553447484440523, 0.3259431600826884, 0.0218693531553008,
                2.1322992029707165e-08, 0.0)),
            "commissions": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "net_cf": (-1282.552995560321, 15.999784557041515, (
                6.680739270459385, -5.0983830543603625, -2.8108254076292796,
                -2.1264209858114385e-05, 0.0)),
        },
        "result_pols": {
            "pols_if": (33.921439348243936, 0.422137899377621, (
                0.422137899377621, 0.09992331667213186, 0.004988714607953328,
                3.619333640475052e-09, 0.0)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_death": (0.3241114328646976, 0.0022549159049686574, (
                0.0022549159049686574, 0.0013131144786530464, 0.00019528613344444893,
                1.1068047764681482e-09, 0.0)),
            "pols_death_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_lapse": (0.09802646651292349, 0.0014259449491933493, (
                0.0014259449491933493, 0.00033488549260507104, 0.0, 0.0, 0.0)),
            "pols_convert": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_maturity": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "prem_cum_pp": (6238923.153898815, 14210.450947218373, (
                5154.782445255555, 14210.450947218373, 14210.450947218373,
                14210.450947218373, 14210.450947218373)),
            "cover_pp": (7369242.409909606, 25793.766173457516, (
                8144.47313388721, 10626.690141513762, 14281.382939395055, 19192.98445193872,
                25793.766173457516)),
            "benefit_death_pp": (7369242.409909606, 25793.766173457516, (
                8144.47313388721, 10626.690141513762, 14281.382939395055, 19192.98445193872,
                25793.766173457516)),
            "mort_rate": (242.87667775248, 1.0, (
                0.06224981904, 0.14678181708, 0.38071423128, 0.9874746669599999, 1.0)),
            "lapse_rate": (4.8, 0.04, (
                0.04, 0.04, 0.0, 0.0, 0.0)),
        },
    },
    16: {"rows": 840, "months": (0, 209, 419, 629, 839),
        "result_cf": {
            "pols_if": (209.1490200413217, 0.7262110548597567, (
                0.7262110548597567, 0.462231094695573, 0.18949350013487623,
                0.005823471311495339, 0.0)),
            "pols_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "premiums": (306435.47635600885, 878.8440145364343, (
                119.77078012320288, 385.3211322539418, 798.4240967966142,
                136.42362684373424, 0.0)),
            "claims_death": (380194.8412106468, 1436.4045040359515, (
                27.15476107333572, 201.10874767194173, 976.9482426485572,
                466.69890463019044, 0.0)),
            "claims_death_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_lapse": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (1472.0488716999487, 3.2321907657301328, (
                3.025879395248986, 3.183323210124824, 2.1569929020104124,
                0.11285125243335618, 0.0)),
            "commissions": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "net_cf": (-75231.4137263379, 740.4837756162977, (
                89.59013965461817, 181.02906137187526, -180.6811387539534,
                -330.38812903888953, 0.0)),
        },
        "result_pols": {
            "pols_if": (209.1490200413217, 0.7262110548597567, (
                0.7262110548597567, 0.462231094695573, 0.18949350013487623,
                0.005823471311495339, 0.0)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_death": (0.37502343125645743, 0.0010763453496371242, (
                0.00014142170633155908, 0.00045696502811289644, 0.000968513045026669,
                0.0001922486580392382, 0.0)),
            "pols_death_pu": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_lapse": (0.3511876236032983, 0.0012213526261793885, (
                0.0012213526261793885, 0.0007767699132679163, 0.00031712590303851476,
                9.472519249329562e-06, 0.0)),
            "pols_convert": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_maturity": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "prem_cum_pp": (1970895968.798654, 15625428.149215387, (
                15447.065011653041, 100526.11218900754, 551668.356546492,
                2947231.7176651736, 15625428.149215387)),
            "cover_pp": (1356059250.6824284, 5564056.723307534, (
                192012.6816294535, 440096.58354480553, 1008709.4310863473,
                2427579.5180579964, 5564056.723307534)),
            "benefit_death_pp": (1356059250.6824284, 5564056.723307534, (
                192012.6816294535, 440096.58354480553, 1008709.4310863473,
                2427579.5180579964, 5564056.723307534)),
            "mort_rate": (196.59687591120002, 1.0, (
                0.0023343682, 0.0117989948, 0.0596376685, 0.3315805055, 1.0)),
            "lapse_rate": (16.799999999999997, 0.02, (
                0.02, 0.02, 0.02, 0.02, 0.02)),
        },
    },
    17: {"rows": 420, "months": (0, 104, 209, 314, 419),
        "result_cf": {
            "pols_if": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_pu": (20.255037425937065, 0.28519318513354724, (
                0.28519318513354724, 0.07004224820069264, 0.0016893719029589947, 0.0, 0.0)),
            "premiums": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_death": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_death_pu": (970.6153814850065, 8.50736895265714, (
                8.50736895265714, 4.758155634831591, 0.3288226057070529, 0.0, 0.0)),
            "claims_lapse": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (57.11232651496061, 0.7129829628338681, (
                0.7129829628338681, 0.2218185611344076, 0.006980685874580494, 0.0, 0.0)),
            "commissions": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "net_cf": (-1027.7277079999672, 9.220351915491008, (
                -9.220351915491008, -4.979974195965998, -0.3358032915816334, 0.0, 0.0)),
        },
        "result_pols": {
            "pols_if": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_pu": (20.255037425937065, 0.28519318513354724, (
                0.28519318513354724, 0.07004224820069264, 0.0016893719029589947, 0.0, 0.0)),
            "pols_death": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_death_pu": (0.28519318513354724, 0.0024996962700122014, (
                0.0024996962700122014, 0.001398075475357299, 9.661702055661835e-05, 0.0,
                0.0)),
            "pols_lapse": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_convert": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_maturity": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "prem_cum_pp": (2970900.0, 7200.0, (
                5430.0, 7200.0, 7200.0, 7200.0, 7200.0)),
            "cover_pp": (2100000.0, 5000.0, (
                5000.0, 5000.0, 5000.0, 5000.0, 5000.0)),
            "benefit_death_pp": (2100000.0, 5000.0, (
                5000.0, 5000.0, 5000.0, 5000.0, 5000.0)),
            "mort_rate": (238.31618131056, 1.0, (
                0.10025395608, 0.21490325844, 0.50673064188, 1.0, 1.0)),
            "lapse_rate": (2.4000000000000004, 0.04, (
                0.04, 0.0, 0.0, 0.0, 0.0)),
        },
    },
}
# END generated fingerprint: WOL_UK_SEC
