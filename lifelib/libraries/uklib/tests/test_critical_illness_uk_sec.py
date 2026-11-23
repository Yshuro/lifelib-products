"""In-force tests for CI_UK_SEC: the splice, future business, counts, regeneration.

``CI_UK_SEC`` is ``CI_UK_S`` taught to run in force at a valuation date
(UKLIB-SEC-PLAN.md, milestone M3, after USLIB-SEC-PLAN.md's Phase 1).  It runs on two
clocks: ``t`` counts months from the valuation date, the same month for every model point,
and ``duration_mth(t)`` counts the months the policy has been in force,
``duration_mth_init() + t``.  A model point may be a policy already in force at the
valuation date, in any month of its policy year, one issued at it, or one to be issued
after it, as in ``basiclife/BasicTerm_SE``.  A policy in force opens with six columns of
state beside its count, each measured at the valuation instant: the two indexation
factors, the premium factor the reviews have given, the select latch and the factor it
closed at, and the premium change of the last review, which sets the shock lapse while
its window runs.

The worked example is not restated here.  On a point issued at the valuation date the two
clocks coincide and the model is ``CI_UK_S``, and ``test_model_conventions_uk.py``
asserts that cell by cell on the twins of S's seven new-business points (T1), so every
golden of ``test_critical_illness_uk.py`` on them holds on this model with no number
copied.  The conventions also hold the SEC family's other rules: every frame opens at
``t = 0``, ``pols_if`` is the ``BEF_DECR`` count, ``BEF_DECR`` is ``BEF_NB`` plus the
month's new business, new business enters once, and nothing happens before issue.  This
module holds the rest of the plan's tests (its §5) and the product's own facts:

* T2, the splice: an S point restated in force at month ``d``, opened with the state S
  carries into ``d``, continues S's projection from ``d`` on, in every cell of S's and in
  ``result_pols``.  The months straddle the product's events: the first anniversary, the
  first and second reviews, the review shock window's end, the last covered month.  The
  review premium change that ships at 0 is on, at 12%, past the shock threshold and apart
  from the select loading, so that the reviews move premiums, open their windows and close
  the select latch, and four variants of S's points, in a copy of S's table, add a
  reviewable indexed male smoker, a reviewable standalone contract, a policy issued at 50
  whose pivots run past the table's last and whose ancillary benefits fall below their caps,
  and a reviewable joint point whose second life is a male smoker.  The changes it does not
  reach, one whose shock lapse takes the cap, the threshold itself and the float above it,
  are spliced on the reviewable point by a test of their own.
* T3, future new business: a point issued ``k`` months after the valuation date is S's
  projection ``k`` months on, with zeros before issue and no rate evaluated there.
* D11's R1 and R2, and D3's and D5's chains: on the splice's grid no cell is called at a
  negative month, none on the books reads a month before them, and none reads beyond
  ``t + 1``; on the committed points no recursion runs backward over the frame; the policy
  clock is a closed form; and the count's chain, called cold, runs one cell a month back to
  ``t_entry()``, at the contract's longest cover, on each contract shape.
* T4, the count algebra: the count rolls forward through new business and decrements,
  ``result_pols`` is S's report with the new business beside it, multiplying
  ``policy_count`` by 2.5 with every assumption that ships at zero switched on multiplies
  every flow and every counted cell by 2.5 and moves no per-policy value, and the
  roll-forward, whose tolerance scales with the count, closes on a million policies.
* T5, validation: each malformed row of the table is refused as it is read, naming its
  point, by its label on an extract labelled otherwise; each assumption table, malformed or
  holding a value that is not a number in its range, is refused before a value of it is
  read, naming its lines; the future horizon is a Reference that bounds future business; a
  point past its cover, one the contract does not issue, one that reads a Reference off its
  domain, and one with a review history before its first review, are refused by the frame,
  each bound just inside it, and an exit rate past 1 in the month it passes; the edges of
  the interface and of each bound are accepted; and so is every state ``CI_UK_S`` reaches,
  on each set of inputs on which those states differ.
* T6, regeneration: the committed ``model_point_table_sec.csv`` is what the generator makes
  of ``CI_UK_S`` and its table as they stand.
* Then the product's own facts: the two clocks on the shipped points; each twin S's in every
  cell with the trend and the review change on, where T1 holds both at 0 and T2 the trend;
  the committed rows continuing their S points, the one read under a review change of its
  own continuing S under it to its next review; each history column read rather than
  recomputed, the indexation factors, the review factor, the select latch, read from its own
  flag, and the last review's change, and a review change set at the valuation date reaching
  back over no review already made (UKLIB-SEC-PLAN.md K14); expense inflation and the
  morbidity trend on the valuation clock; the initial expense on new business; the reviews
  and their window on the policy clock; the caps on the claim rates, a second life's among
  them, a NaN that reaches a bound and a check whose residual is NaN; a whole review period
  written as a float; the values outside cover; the block; an in-force extract; the runner;
  the cells' defaulted parameters; the docstrings; the shared input tables; and what the
  default grid reaches.
* C2, the fingerprint: every committed point computes what the model computed when its E
  step ended, frozen at the end of this module before its C step changed anything
  (USLIB-SEC-PLAN.md §5.4).

SEC month ``t`` is S month ``t + source_mth`` throughout, the direction in which
``uk_sec_support`` takes its ``t_offset``: ``d`` for a point restated at S month ``d``,
``-k`` for one issued ``k`` months on.  ``CI_UK_S`` has no point in force, so there is no
in-force twin.

**The core grid and the full one** (UKLIB-SEC-PLAN.md U6).  T2 and T3 over every S point
at every month, about 140 cases, run by default on a core, chosen so that between them they
reach every branch, every opening-state column, every kind of valuation month and both
sides of every ``min`` and ``max`` the full grid reaches, which
``test_the_core_grid_reaches_every_branch`` asserts.  The other cases, and the rules
test's scan of their rows, carry the ``sec_full`` marker and are skipped, with the reason
shown, unless ``UKLIB_SEC_FULL=1`` is set.  They are never dropped: one leg of the CI
matrix sets it, and ``UKLIB_SEC_FULL=1 python -m pytest -m sec_full
lifelib/libraries/uklib/tests/test_critical_illness_uk_sec.py`` runs them alone.  Each
splice row is released once it has been read (``_release``), as ``run_sec.py --block``
releases its points.

Every test keeps four rules.  Each model is read under a name of its own and closed:
``conftest.critical_illness`` reads S under its default name, and reading a model under a
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
    codes, fingerprint_mismatches, frame_mismatches, full_sweep, sweep, temp_inputs,
    twin_mismatches)

SEC, TWIN = "CI_UK_SEC", "CI_UK_S"
TABLE = "model_point_table_sec.csv"
SPEC = SEC_SPECS[SEC]

# S's seven points, all new business: the anchor cell, accelerated (1); the standalone
# variant (2); the reviewable variant (3); an indexed policy (4); one without children's
# cover (5); a female smoker on a 20-year term (6); and a joint first-event policy (7).
S_POINTS = (1, 2, 3, 4, 5, 6, 7)

# T2's months (UKLIB-SEC-PLAN.md §6.2): the second month; 11, 12 and 13 about the first
# anniversary, where the index steps and the lapse rate moves to its second year; 59, 60
# and 61 about the first review, the start of policy month 60, where the pivot age reaches
# 45 on the anchor cell and the lapse table its ultimate year 6; 71 and 72, the review's
# twelve-month shock window's last month and the first after it; 119, 120 and 121 about the
# second review; 239, the female smoker's last month; and 299, the last month of a 25-year
# term.  A month at or past a point's cover is left out.  T3's: issued one month on, which
# puts the policy anniversaries and reviews a month off the valuation years, and twelve,
# which puts them back on; and later, more than a year after the valuation date
# (USLIB-SEC-PLAN.md §7.1, *Record — M14*, *Splice grid*).
SPLICE_MTHS = (1, 11, 12, 13, 59, 60, 61, 71, 72, 119, 120, 121, 239, 299)
FUTURE_MTHS = (1, 12)
LATE_FUTURES = ((3, 13), (4, 25))

# Four more S points, in the splice's copy of S's table and never in the committed one,
# each one of S's points changed so as to reach what S's own points cannot:
#
# 8, S point 3, the reviewable point, indexed and a smoker: both premium factors in force
#   together, and the male smoker's rates, which no S point reads;
# 9, S point 2, the standalone contract, reviewable: the select latch on the paid rate;
# 10, S point 1 issued at 50, its cover reduced to 40,000: attained ages from 65, where the
#   pivot interpolation extrapolates past the table's last pivot, and the additional
#   payment and children's cover on the share side of their caps, where S's points take the
#   cap;
# 11, S point 7, the joint point, reviewable, with a male smoker as its second life: the
#   latch on two lives.
#
# Each variant is (the S point it changes, the columns it changes); the policy_id keeps
# the generated ids apart.
VARIANTS = {
    8: (3, {"policy_id": "CI-900008", "indexation": True, "smoker": "S"}),
    9: (2, {"policy_id": "CI-900009", "premium_guarantee": "reviewable"}),
    10: (1, {"policy_id": "CI-900010", "age_at_entry": 50, "sum_assured": 40000.0}),
    11: (7, {"policy_id": "CI-900011", "premium_guarantee": "reviewable",
             "joint_sex": "M", "joint_smoker": "S"}),
}
VARIANT_MTHS = {8: (1, 12, 59, 60, 61, 71, 72, 120), 9: (59, 60, 72, 120),
                10: (12, 179, 180, 299), 11: (60, 66, 120)}


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


# The months of cover from issue of each S point and variant, 12 times its term.
COVER = {p: 12 * int(n) for p, n in _s_table_with_variants()["policy_term"].items()}

# The committed rows the generator reads from S under References of their own (the spec's
# derived_refs), by (S policy, month), with those References.
UNDER_REFS = {(_s_table().at[p, "policy_id"], d): refs
              for (p, d), refs in SPEC.derived_refs.items()}

# T2's cases, as (row_kind, S point, source_mth): each S point restated in force at each
# of its months, and each variant at its own.  CI_UK_S has no point in force, so no twin is
# a splice case.  T3's cases, as (S point, k).
SPLICES = (tuple(("derived", p, d) for p in S_POINTS for d in SPLICE_MTHS if d < COVER[p])
           + tuple(("derived", p, d) for p, mths in VARIANT_MTHS.items() for d in mths))
IN_FORCE_TWINS = ()
FUTURES = (tuple((p, k) for p in S_POINTS for k in FUTURE_MTHS)
           + tuple((p, 1) for p in VARIANTS) + LATE_FUTURES)

# The default run's cases (the module docstring), each with what it is there for.  The
# rest of SPLICES and FUTURES run with UKLIB_SEC_FULL=1.
CORE_SPLICES = {
    ("derived", 1, 1): "the anchor cell in its second month",
    ("derived", 1, 11): "the anchor cell in the month before its first anniversary",
    ("derived", 1, 12): "the anchor cell on its first anniversary",
    ("derived", 1, 299): "the anchor cell in its last covered month",
    ("derived", 2, 13): "the standalone split after its first anniversary",
    ("derived", 2, 120): "the standalone contract on a later anniversary",
    ("derived", 3, 1): "reviewable in its second month, before any review",
    ("derived", 3, 59): "reviewable in the month before its first review",
    ("derived", 3, 60): "reviewable on its first review: its history at t = 0",
    ("derived", 3, 61): "reviewable inside the first review's window",
    ("derived", 3, 71): "reviewable in the first window's last month",
    ("derived", 3, 72): "reviewable past the first window",
    ("derived", 3, 119): "reviewable in the month before its second review",
    ("derived", 3, 121): "reviewable inside the second review's window",
    ("derived", 4, 12): "indexed on its first anniversary: the step at t = 0",
    ("derived", 4, 13): "indexed mid-year: the factors of the year under way",
    ("derived", 4, 60): "indexed on its fifth anniversary",
    ("derived", 5, 60): "without children's cover",
    ("derived", 6, 61): "the female smoker mid-year",
    ("derived", 6, 239): "the female smoker in its last covered month",
    ("derived", 7, 12): "joint first event on an anniversary",
    ("derived", 7, 120): "joint first event later",
    ("derived", 8, 60): "reviewable and indexed on its review, a male smoker",
    ("derived", 8, 72): "reviewable and indexed past its window",
    ("derived", 9, 60): "standalone and reviewable on its review: the latch on the paid rate",
    ("derived", 9, 120): "standalone and reviewable on its second review",
    ("derived", 10, 179): "issued at 50, the month before the last pivot",
    ("derived", 10, 180): "issued at 50, at the last pivot and past it, below the caps",
    ("derived", 11, 66): "joint and reviewable in its window, a male smoker second",
}
CORE_FUTURES = {
    (1, 1): "issued a month off the valuation anniversaries",
    (1, 12): "issued on them, a year on",
    (3, 13): "reviewable, more than a year on: its reviews a month off",
    (4, 25): "indexed, more than two years on",
    (7, 12): "joint first event",
    (9, 1): "standalone and reviewable",
    (10, 1): "issued at 50, below the caps",
}

SEC_FULL = os.environ.get("UKLIB_SEC_FULL") == "1"
FULL_ONLY = (pytest.mark.sec_full,
             pytest.mark.skipif(not SEC_FULL, reason="the full splice grid runs with "
                                "UKLIB_SEC_FULL=1 (UKLIB-SEC-PLAN.md U6)"))

# What the splice sets in both models, S and SEC alike, before either evaluates anything.
# Two inputs run on the valuation clock (D7): expense inflation, which S runs from issue
# and SEC from the valuation date, so at the shipped 3% the expenses of a point opened at d
# differ by 1.03^(d // 12), by design, and at 0 both factors are 1; and the morbidity
# trend, which S runs from issue too, and which ships at 0, where the splice keeps it
# (UKLIB-SEC-PLAN.md §6.2, §9 item 4): on it SEC's diagnosis rate at d is S's at d with
# none of the trend since issue, by design.  Each clock is then asserted on its own, with
# its rate on.  There is no scenario table, so no input table moves with d.  The one other
# assumption that ships at zero, the premium change at a review, is on, at 12%, past the
# shock threshold of 5%, without which the reviews move no premium, open no shock window
# and close no select latch, and so the review history, the latch and the last review's
# change reach no number.  And 12%, not 10%, the shipped select loading, so that a latch
# closed at 1 + rho, or a review factor read from the latch, departs from S.  The
# identity does not depend on the value, only on both models having the same one; the
# changes the splice's does not reach, past the lapse cap and at the threshold, have a
# test of their own.
SPLICED_REFS = {"inflation_rate": 0.0, "ci_trend": 0.0, "review_prem_shock": 0.12}

# Every assumption that ships at zero, switched on, for T4, at the shipped inflation: the
# review change, as the splice sets it, and the morbidity trend, at 2% a year, which T4 can
# hold since it compares the model with itself.
SWITCHED_ON = {"review_prem_shock": 0.12, "ci_trend": 0.02}

# The cells T2 and T3 skip beyond T1's, which already drop result_pols as a whole (the
# spec's exempt).  proj_len counts from the valuation date on SEC and from issue on S, so it
# differs by d, or by -k, by design; frame_mismatches asserts what it must get right, that
# both frames end at the same instant.  Both tests compare result_pols column by column
# instead.
SPLICE_EXEMPT = TWIN_EXEMPT_DEFAULT | SPEC.exempt | {"proj_len"}
FUTURE_EXEMPT = SPLICE_EXEMPT

# The result_cf columns that expense inflation moves, and the cells they are made of: on
# the committed points, at the shipped 3% and the shipped trend of 0, the only places an
# in-force row departs from S.
INFLATED = ("expenses", "net_cf")
INFLATION_CELLS = frozenset({"inflation_factor", "expenses", "net_cf", "result_cf"})

# The S cell whose exact value is 0 and whose computed value is rounding about it, the
# roll-forward's residual: a comparison with S holds it at the harness's absolute floor of
# 1e-9, and every other cell at none (_compare).  The claim split's residual is no rounding:
# it is the notes' second-order artefact, of order 1e-5 on the standalone contract, made of
# rates no count moves, and it compares with no floor.
RESIDUALS = frozenset({"check_pols_roll_fwd_resid"})

# The decrement rates and the reads keyed by an attained age or a policy year, none of
# which may be evaluated before issue (R1, D4).
DECREMENT_RATES = ("ci_rate_base", "mort_rate", "ci_rate", "claim_rate_life", "claim_rate",
                   "claim_rate_paid", "claim_rate_mth", "claim_rate_paid_mth",
                   "claim_rate_exit_mth", "ap_rate", "ap_rate_mth", "lapse_rate_base",
                   "lapse_rate", "lapse_rate_mth")

# The cells that scale with policy_count.  Every other cell is a per-policy amount, a rate,
# a factor, a clock or a flag, and must not move when the count does.
COUNTED = frozenset({
    "policy_count", "pols_if_init", "pols_if", "pols_if_at", "pols_new_biz", "pols_claim",
    "pols_lapse", "pols_maturity", "premiums", "claims", "claim_expenses", "expenses",
    "net_cf", "check_pols_roll_fwd_resid", "result_cf", "result_pols"})

# result_pols' columns, in its order: the count, the new business within it, the month's
# claims and lapses in processing order, the expiries of the last covered month, then S's
# other six: the end-of-month count, and the rates, which no count moves.
RESULT_POLS = ["pols_if", "pols_new_biz", "pols_claim", "pols_lapse", "pols_maturity",
               "pols_if_aft_decr", "ci_rate", "mort_rate", "claim_rate", "claim_rate_mth",
               "lapse_rate"]
OUTFLOWS = RESULT_POLS[2:5]
RATES = RESULT_POLS[6:]

# S's three timings and BEF_NB, the one running in force adds; and the kinds.
TIMINGS = ("BEF_NB", "BEF_DECR", "BEF_LAPSE", "AFT_DECR")
KINDS = ("MAIN", "AP", "CHILD", "LAPSE")
BENEFITS = ("MAIN", "AP", "CHILD")

# What each cell holds outside cover, before issue and from the month cover has ended, as
# its docstring says: no count, so no cash flow; no factor and no review; no rate read at a
# policy year or an age the policy does not have.  The type is part of the value.  A count
# is a float in every branch, a flag a bool and the reviews passed an int, because the C
# step types a cell by the values it returns (USLIB-SEC-PLAN.md F3).  The guard test also
# calls pols_if_at at each timing, claims at each kind, benefit_pp at each benefit, and
# ci_rate_base and mort_rate at each life the point has, all 0.0: they take their life with
# no default, so they are called with one, as every caller calls them.
OUTSIDE_COVER = {
    "is_active": False, "reviews_passed": 0, "review_shock_active": False,
    "review_prem_change": 0.0, "ci_sel_factor": 0.0, "review_prem_factor": 0.0,
    "idx_factor": 0.0, "idx_prem_factor": 0.0, "premium_pp": 0.0, "lapse_rate_base": 0.0,
    "pols_if": 0.0, "pols_new_biz": 0.0, "pols_claim": 0.0, "pols_lapse": 0.0,
    "pols_maturity": 0.0, "premiums": 0.0, "claims": 0.0, "claim_expenses": 0.0,
    "expenses": 0.0, "net_cf": 0.0, "check_claim_split_resid": 0.0}

# The cells a month outside cover may not reach: the clocks of the contract, the pivot
# interpolation and the rates, each keyed by a policy year or an attained age.  The reads
# that guard themselves are held by their values in OUTSIDE_COVER instead.
IN_COVER_ONLY = ("age", "duration", "policy_year", "pivot_interp", "ci_rate",
                 "claim_rate_life", "claim_rate", "claim_rate_paid", "claim_rate_mth",
                 "claim_rate_paid_mth", "claim_rate_exit_mth", "ap_rate", "ap_rate_mth",
                 "lapse_rate", "lapse_rate_mth")

# The opening state, in the table's order, and the cells running in force adds to
# CI_UK_S's, each of which the symbol map must name.
STATE = ("idx_factor_init", "idx_prem_factor_init", "review_prem_factor_init",
         "ci_sel_latched_init", "ci_sel_factor_init", "review_prem_shock_init")
NEW_CELLS = ("policy_count", "duration_mth_init", "t_entry", "is_active", "expiry_mth",
             "pols_new_biz", *STATE, "review_prem_factor", "review_prem_change")

INFLATION = 0.03        # the shipped inflation_rate, which the inflation test reads
TREND = 0.02            # the morbidity trend the trend test switches on

# The recursion limit, as mx.set_recursion takes it, under which the committed points are
# first swept (R2, F7).  A report evaluates each column in ascending t, so a forward
# recursion, through t - 1, finds the month before already cached: the committed points'
# sweep passes under a limit of 10 and fails under 9 (measured at M3), as Term's does.  A
# backward recursion over the frame, through t + 1, opens a chain as long as the frame,
# and the shortest committed frame longer than a month is 222.
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
    """CI_UK_SEC read from a copy whose SEC table is ``edit(_committed())``."""
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
    """Evaluate on an S point what the splice compares: the sweep, and four cells more.

    :func:`uk_sec_support.sweep` reaches ``CI_UK_S``'s ``pols_if_at(t, "BEF_DECR")``
    nowhere, since S's ``pols_if`` is a recursion of its own, nor ``duration_mth``, which
    no S formula reads, nor ``cover_basis`` and ``premium_mode``, which no report reads; a
    cell S never evaluates is compared nowhere.  They are evaluated here, over the frame,
    so the splice and the future comparison see them too.
    """
    sweep(proj)
    for t in range(proj.proj_len()):
        proj.pols_if_at(t, "BEF_DECR")
        proj.duration_mth(t)
    proj.cover_basis()
    proj.premium_mode()


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
    test holds them.  The morbidity trend ships at 0, where the two clocks agree.  Every
    other column and cell must agree, to 1e-9 relative, with no absolute floor but on the
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
    """CI_UK_SEC read in place, as committed, and swept once, cold; what it met.

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
    """CI_UK_SEC read in place, as committed, with every point swept (sec_read)."""
    return sec_read[0]


@pytest.fixture(scope="module")
def s_model():
    """CI_UK_S read in place, as committed, with every point swept.

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
    with ``d``: CI's two valuation-clock inputs are the ``inflation_rate`` and ``ci_trend``
    References.  Every S point is then swept (:func:`_sweep_s`), and stays swept; each SEC
    row is projected by the case that compares it and released once compared
    (:func:`_settle`).
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


def _pivot_side(x, t, life):
    """Which branch of ``pivot_interp`` life ``life``'s attained age takes in month ``t``:
    ``"below"`` at or below the first pivot, ``"above"`` at or above the last, else
    ``"between"``, for the life's own group of the table."""
    ages = sorted(int(a) for a in x.data.ci_rate_table().loc[
        (x.sex(life), x.smoker(life))].index)
    a = x.age(t, life)
    return "below" if a <= ages[0] else "above" if a >= ages[-1] else "between"


def _lives(x):
    return (1, 2) if x.is_joint() else (1,)


def _historic_window(x, t):
    """Month ``t`` is in the shock window of a review made at or before the valuation
    date."""
    return (x.review_shock_active(t) and x.duration_mth_init() > 0
            and x.reviews_passed(t) == x.reviews_passed(x.t_entry()))


# What test_the_core_grid_reaches_every_branch asks of the core's rows in the model's own
# values, which no column of the table shows: each holds of some core row, or of a core row
# in some month of its frame.  At the valuation date, every opening-state column in use, a
# factor apart from 1 and a change apart from 0, and each kind of valuation month the
# reviews make: on a review, inside a window a review before the valuation date opened, and
# before the first review.  Later in the frame, every branch and both sides of each min and
# max the full grid reaches: a review in the frame and its window, a window carried from
# before the valuation date, the latch closed in the frame and carried, the pivot
# interpolation's three branches, the lapse table's last year, an index step, the ancillary
# benefits on either side of their caps, the standalone split, a second life, the expiry.
AT_VALUATION = {
    "idx_factor_init above 1": lambda x: x.idx_factor_init() > 1.0,
    "idx_prem_factor_init above 1": lambda x: x.idx_prem_factor_init() > 1.0,
    "review_prem_factor_init apart from 1": lambda x: x.review_prem_factor_init() != 1.0,
    "ci_sel_latched_init at 1": lambda x: x.ci_sel_latched_init() == 1,
    "ci_sel_factor_init apart from 1": lambda x: x.ci_sel_factor_init() != 1.0,
    "review_prem_shock_init apart from 0": lambda x: x.review_prem_shock_init() != 0.0,
    "valued on a review": lambda x: (
        x.premium_guarantee() == "reviewable" and x.duration_mth_init() > 0
        and x.reviews_passed(0) >= 1 and x.duration_mth_init() % x.review_period_mths == 0),
    "valued inside a window a review before the valuation date opened": lambda x: (
        _historic_window(x, 0)),
    "valued before the first review": lambda x: (
        x.premium_guarantee() == "reviewable"
        and 0 < x.duration_mth_init() < x.review_period_mths),
}
IN_FRAME = {
    "a review in the frame": lambda x, t: (
        x.premium_guarantee() == "reviewable"
        and x.reviews_passed(t) > x.reviews_passed(x.t_entry())),
    "a shock window from a review in the frame": lambda x, t: (
        x.review_shock_active(t) and x.reviews_passed(t) > x.reviews_passed(x.t_entry())),
    "a shock window from a review before the valuation date": _historic_window,
    "a review, past its window": lambda x, t: (
        x.premium_guarantee() == "reviewable" and x.reviews_passed(t) >= 1
        and not x.review_shock_active(t)),
    "the latch closed in the frame": lambda x, t: (
        x.ci_sel_latched_init() == 0 and x.ci_sel_factor(t) > 1.0),
    "the latch carried from the valuation date": lambda x, t: (
        x.ci_sel_latched_init() == 1 and x.ci_sel_factor(t) == x.ci_sel_factor_init()),
    "a pivot age at or below the first": lambda x, t: any(
        _pivot_side(x, t, life) == "below" for life in _lives(x)),
    "a pivot age between two": lambda x, t: any(
        _pivot_side(x, t, life) == "between" for life in _lives(x)),
    "a pivot age at or above the last": lambda x, t: any(
        _pivot_side(x, t, life) == "above" for life in _lives(x)),
    "inside the lapse table": lambda x, t: x.policy_year(t) <= x.data.lapse_last_year(),
    "past the lapse table's last year": lambda x, t: (
        x.policy_year(t) > x.data.lapse_last_year()),
    "an index step in the frame": lambda x, t: (
        x.indexation() and x.duration(t) > x.duration(x.t_entry())),
    "the ancillary benefits below their caps": lambda x, t: (
        x.benefit_pp(t, _code(x, "AP")) < x.ap_cap
        and x.benefit_pp(t, _code(x, "CHILD")) < x.child_cap),
    "the ancillary benefits at their caps": lambda x, t: (
        x.benefit_pp(t, _code(x, "AP")) == x.ap_cap
        and x.benefit_pp(t, _code(x, "CHILD")) == x.child_cap),
    "no children's cover": lambda x, t: (
        not x.children_cover() and x.benefit_pp(t, _code(x, "MAIN")) > 0.0),
    "the standalone split": lambda x, t: (
        x.contract_type() == "standalone" and x.claim_rate_exit_mth(t) > 0.0),
    "a second life": lambda x, t: x.is_joint() and x.claim_rate_life(t, 2) > 0.0,
    "the expiry": lambda x, t: x.pols_maturity(t) > 0.0,
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
    policy month passed as ``t`` (R1a), as a review counted on ``t`` would be, and a review
    made at the valuation date counted twice or not at all.  The frame comparisons read SEC
    row ``t`` against S row ``t + d`` in every column of ``result_cf`` and every column of
    ``result_pols`` both reports hold, and fail frames that end apart.  The cell comparison
    then evaluates every cell of S's but :data:`SPLICE_EXEMPT`, at every argument S cached
    inside its own frame from month ``d`` on, moved onto SEC's clock: the counts, the
    reviews, the shock window, the select latch, the index factors and the pivot rates
    among them.  Each compares to 1e-9 relative with no absolute floor, but the
    roll-forward's residual, which keeps the floor of 1e-9 (:func:`_compare`).  An S cell
    this model lacked would fail it.

    The reviewable rows at 60 to 72 are the ones that see the review history read at the
    wrong instant: on a review month, the review's premium change, its window and its latch
    are history, and each month of the window after it reads the change of its review.  The
    row is then recorded for the rules test and released (:func:`_settle`).
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

    SEC rows ``k ..`` are S rows ``0 ..``, ending together at the end of the term, in
    ``result_cf`` and in every column of ``result_pols`` S's has, and every cell of S's but
    :data:`FUTURE_EXEMPT` agrees at every argument S cached inside its own frame, moved
    ``k`` later.  Each compares as the splice compares, with no absolute floor but on the
    residual (:func:`_compare`).  An S cell this model lacked would fail it.  Before issue
    every column of ``result_cf`` and ``result_pols`` is an exact zero, and the policies
    arrive in month ``k`` as new business.

    The last assertions are R1 and D4's base rule made testable.  After the reports, no
    decrement rate or read keyed by an age or a policy year has been evaluated at a month
    before issue.  A count recursion based at ``t == 0`` rather than at ``t_entry()``, or a
    decrement count that evaluates its rate before asking whether the month is in cover,
    still gives the right numbers.  This is the only test that sees the first, and the
    guard test sees the second too.

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
      on a point in force past it, as a review month would.
    * R1's look-back stops at ``t_entry()``: no cell evaluated at a month from
      ``t_entry()`` on read a month before it.  On a point issued later a recursion based
      at ``t == 0`` reads the pre-issue zeros, so no number shows it and no argument goes
      negative.  The reviews and anniversaries counted from ``t_entry()`` read it, the
      month of entry, and no month before.
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
# Data's first reads of its tables.  The count is CI's one chain: the reviews, the latch
# and the factors are closed forms on the policy clock.  Measured at M3, a cold net_cf in
# the last month runs 11 cells beyond the count's chain on every shape at the contract's
# longest cover, issued now and 120 months on, and on every committed point, 10 on the two
# indexed ones; the count's own head runs 7 beyond, its claims 10.  Term's 16
# (USLIB-SEC-PLAN.md D5).  Any chain of two cells a month runs a frame's length beyond.
CHAIN_OVERHEAD = 16

# The contract's longest cover (product-spec.md, held by proj_len()): a 50-year term,
# policy_term_max, issued at issue_age_min, 18, which expires at 68, inside expiry_age_max,
# 75, and is the same on every contract shape.
LONGEST_TERM, YOUNGEST = 50, 18

# The chain of the model and the cells that head it, called cold in the last month of the
# frame, each on a read of its own: (cell, the timing it takes, or None).  The count, and
# net_cf over it, the deepest call a projection makes.
CHAIN_HEADS = (("net_cf", None), ("pols_if_at", "BEF_NB"))

# The shapes the chain runs at its longest cover on, by the S point whose twin each is:
# the reviewable accelerated point, whose rates read the reviews, the latch and the shock
# window in every month; the standalone contract, whose paid rate is a second decrement;
# and the joint point, whose decrement reads two lives.
CHAIN_SHAPES = (3, 2, 7)


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
    now and 120 months on, and each row's frame and ``t_entry()``.

    Each S point's twin, its lives issued at 18 on a 50-year term, the contract's longest
    cover on every shape, issued at the valuation date and 120 months after it, the shipped
    ``future_horizon_mth``: frames of 600 and 720 months, whose chains stop at
    ``t_entry()``.  The shipped tables serve every age, the pivot table extrapolating below
    its first pivot, 40.
    """
    committed = _committed()
    labels = [_label(committed, "twin", p, 0) for p in CHAIN_SHAPES]
    top = committed.index.max()
    rows = committed.loc[labels + labels].assign(
        age_at_entry=YOUNGEST, policy_term=LONGEST_TERM)
    later = list(range(top + 1, top + 1 + len(labels)))
    rows = rows.set_axis(labels + later).rename_axis("point_id")
    rows = _set("joint_age", [label for label in rows.index
                              if rows.at[label, "life_basis"] == "joint_first_event"],
                float(YOUNGEST))(rows)
    rows = _set("duration_mth", later, -120)(rows)
    frames = [(label, 600, 0) for label in labels] + [(label, 720, 120) for label in later]
    return _sec_inputs(tmp_path, rows), frames


# modelx warns as its stack trace starts and stops, which is all the test does with it.
@pytest.mark.filterwarnings("ignore:call stack trace:UserWarning")
def test_every_chain_runs_one_cell_a_month_from_a_cold_start(tmp_path):
    """Called cold, the count's chain runs one cell a month back to ``t_entry()``, no more.

    No number shows how deep a chain runs, and a compiled model runs it on the C stack, so
    a chain of two cells a month, which gives the same numbers, needs twice the stack on
    every platform (F7); ``CI_UK_S``'s count chain runs three cells a month.  On a model
    just read, nothing is cached, so modelx's stack trace counts how deep a call runs,
    against one cell a month back to ``t_entry()`` and :data:`CHAIN_OVERHEAD` more, with
    modelx's recursion limit where the module leaves it: each of :data:`CHAIN_HEADS` in the
    last month of the frame, each on a read of its own, with :data:`SWITCHED_ON` set, so
    that the reviews shock lapses, close the latch and the trend moves the rates.  On each
    of :data:`CHAIN_SHAPES` at the contract's longest cover, 50 years from issue age 18,
    issued now and 120 months on (:func:`_longest_cover`), each row's frame asserted
    first, as §7.5's *Record — M5* and M14's carried rule ask, and M1's that every chain
    runs at its own shape's longest cover.
    """
    folder, frames = _longest_cover(tmp_path)
    found = []
    for label, months, entry in frames:
        for cell, timing in CHAIN_HEADS:
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


def test_the_count_rolls_forward_through_new_business_and_decrements(sec_model):
    """The count leaves month t by its claims, lapses and expiries alone.

    On every committed point and at every ``t`` of its frame, the count weighting month
    ``t``, ``pols_if_at(t, BEF_DECR)``, less the count carried into ``t + 1``,
    ``pols_if_at(t + 1, BEF_NB)``, is the three outflows of month ``t``, to 1e-12.  The
    step from the last row to ``t = proj_len()`` is what catches cover that runs a month too
    long: the expiries would then leave a month late, and the count would carry over.  And
    the notes' end-of-month count, ``pols_if_at(t, AFT_DECR)``, is exactly the count
    carried into the next month before its new business, in every month: the two are one
    product in one order.  The additional-payment and children's claims decrement nothing.

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
            out = p.pols_claim(t) + p.pols_lapse(t) + p.pols_maturity(t)
            moved = p.pols_if_at(t, bef_decr) - p.pols_if_at(t + 1, bef_nb)
            assert moved == pytest.approx(out, abs=1e-12), (point_id, t)
            assert p.pols_if_at(t, aft) == p.pols_if_at(t + 1, bef_nb), (point_id, t)
        pols = p.result_pols()
        assert list(pols.columns) == RESULT_POLS, point_id
        assert pols.index.name == "t" and list(pols.index) == list(range(p.proj_len()))
        carried = (pols["pols_if"] - pols[OUTFLOWS].sum(axis=1)).shift(1)
        expected = carried.fillna(p.pols_if_init()) + pols["pols_new_biz"]
        assert ((pols["pols_if"] - expected).abs() <= 1e-12).all(), point_id


def test_result_pols_is_s_report_with_the_new_business_beside_it(sec_model, s_model):
    """``result_pols()`` is S's, column for column, with ``pols_new_biz`` second (D5).

    T1 skips the report as a whole, because its frame has a column S's lacks (the spec's
    exempt), so it is compared here, on every twin, each issued at the valuation date, at
    offset 0.  Every column S's report has agrees, to 1e-9, frames ending together, and
    ``pols_new_biz`` holds the count in the issue month and 0 in every other.  The counts
    and rates carry no inflation, so the shipped assumptions serve.
    """
    table = sec_model.Data.model_point_table()
    twins = table.index[table["row_kind"] == "twin"].tolist()
    assert twins == sorted(s_model.Data.model_point_table().index)
    for point_id in twins:
        p = _point(sec_model, point_id)
        mine, theirs = p.result_pols(), _point(s_model, point_id).result_pols()
        assert list(mine.columns) == [theirs.columns[0], "pols_new_biz",
                                      *theirs.columns[1:]], point_id
        month = int(table.at[point_id, "source_mth"])
        assert frame_mismatches(theirs, mine, t_offset=month) == [], point_id
        issue = -int(table.at[point_id, "duration_mth"])
        assert list(mine["pols_new_biz"]) == [
            p.policy_count() if t == issue else 0.0 for t in mine.index], point_id


# What T4 multiplies policy_count by: not a whole number, because a count of policies need
# not be one, so that a flow which read the count as whole policies would not follow it.
COUNT_FACTOR = 2.5


def test_scaling_the_count_scales_every_flow_and_no_per_policy_value(tmp_path):
    """``policy_count`` is a weight: 2.5 times the count, 2.5 times every flow, the same per
    policy.

    The committed table, and a copy with every count multiplied by :data:`COUNT_FACTOR`,
    are each read with :data:`SWITCHED_ON` set before either computes anything: every
    assumption that ships at zero, on, so that every flow is nonzero on some point, the
    reviews shock lapses and close the latch, and the trend moves the diagnosis rates.  On
    every point ``result_cf`` and the counts of ``result_pols`` are 2.5 times the committed
    table's, element by element, to 1e-12 relative: a scaled count is a computed float,
    which may come back from the CSV within two ulps (``uk_sec_support``'s module
    docstring).  ``result_pols``'s rates are the committed table's exactly.  So is every
    other cell of :data:`COUNTED`, at every argument the sweep of the committed table's
    point cached: the count at each timing and the claims of each kind, which no report
    shows, among them, and the roll-forward's residual, a rounding about 0 on that many
    policies, to the residual's floor of 1e-9.  And every cell outside :data:`COUNTED` (the
    premium, the benefits, the factors, the reviews, the latch, the rates, both clocks, the
    flags) agrees bit for bit at every argument that sweep cached.  So a flow that dropped
    the count, or read it as whole policies, which a table of counts of 1 hides from every
    comparison with S and a count doubled hides here, fails (USLIB-SEC-PLAN.md §5.2, T4,
    precised at M11).  Each counted cell but the residual is nonzero on some point.
    """
    table = _committed()
    base = mx.read_model(_sec_inputs(tmp_path / "base", table), name=_name("counted"))
    scaled = mx.read_model(_sec_inputs(tmp_path / "scaled", table.assign(
        policy_count=COUNT_FACTOR * table["policy_count"])), name=_name("scaled"))
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
                flows = [c for c in b.columns if c not in RATES]
                want = COUNT_FACTOR * b[flows]
                bad = ((d[flows] - want).abs() > 1e-12 * want.abs()).any()
                assert not bad.any(), (key, report, list(bad[bad].index))
                rates = [c for c in b.columns if c in RATES]
                assert d[rates].equals(b[rates]), (key, report)
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


def test_the_roll_forward_closes_on_a_million_policies(tmp_path):
    """``check_pols_roll_fwd`` scales its tolerance with the count, and closes at 1e6.

    A residual is rounding on that many policies, so the check holds it to 1e-10 times
    ``max(policy_count(), 1)``, where its tolerance unscaled would be 1e-10: at the counts
    the other tests use, one policy or less, the two are one.  ``CI_UK_S`` scales by
    ``pols_if_init()``, which here is 0 on a point issued at the valuation date, the count
    entering as new business.  So every committed point is projected from a copy where
    each counts a million policies: the check closes on each, and on some point the largest
    residual exceeds the unscaled 1e-10, so the scaling is what closes it
    (USLIB-SEC-PLAN.md §5.2, T4, precised at M10).  ``check_claim_split`` compares rates,
    which no count moves, to ``claim_split_tol``, and closes on each point too.
    """
    table = _committed()
    model = mx.read_model(_sec_inputs(tmp_path, table.assign(policy_count=1e6)),
                          name=_name("million"))
    worst = 0.0
    try:
        for key, point_id in zip(point_keys(model), table.index):
            p = projection(model, key)
            assert p.policy_count() == 1e6
            assert p.check_pols_roll_fwd() and p.check_claim_split(), point_id
            worst = max(worst, *(abs(p.check_pols_roll_fwd_resid(t))
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
# point_ids are the committed table's: 1 to 7 the twins of S's points; 8, the indexed point
# on its third anniversary; 9, 10 and 11, the reviewable point on its first review, inside
# its window and after it; 12, the anchor cell in its last month; 13, the indexed point
# issued 13 months on.  A {file} in a message is the table's filename: every case is read
# by one model, from a file of its own (the malformed fixture).


def _drop(column):
    return lambda table: table.drop(columns=column)


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
    ("a fractional duration", _set("duration_mth", [9], 60.5),
     "{file}: duration_mth must be a whole number of months; it is not at point_id [9]"),
    ("a blank duration", _set("duration_mth", [13], float("nan")),
     "{file}: duration_mth must be a whole number of months; it is not at point_id [13]"),
    ("a text duration", _set("duration_mth", [11], "x4"),
     "{file}: duration_mth must be a whole number of months; it is not at point_id [11]"),
    # numpy casts a float past int64 to the least int64, a policy issued 2**63 months on,
    # without a word: the table refuses it first.
    ("a duration past int64", _set("duration_mth", [8], 1e19),
     "{file}: duration_mth must be below 2**53 months; it is not at point_id [8]"),
    ("durations of 2**53 months at two points", _set("duration_mth", [8, 10], 2.0 ** 53),
     "{file}: duration_mth must be below 2**53 months; it is not at point_id [8, 10]"),
    ("issued beyond the horizon", _set("duration_mth", [13], -121),
     "{file}: duration_mth must be -120 or more, a policy issued at most 120 months after "
     "the valuation date; it is not at point_id [13]"),
    *[(f"no {column} column", _drop(column), f"{{file}} has no {column} column")
      for column in ("policy_count", "duration_mth", *STATE)],
    ("a repeated point_id",
     lambda t: pd.concat([t, t.loc[[8]].assign(policy_id="CI-900099")]),
     "{file}: point_id [8] appears more than once"),
    ("a cover factor below 1", _set("idx_factor_init", [8], 0.99),
     "{file}: idx_factor_init must be a number, 1 or more; it is not at point_id [8]"),
    ("a blank cover factor", _set("idx_factor_init", [8], float("nan")),
     "{file}: idx_factor_init must be a number, 1 or more; it is not at point_id [8]"),
    ("a premium factor below 1", _set("idx_prem_factor_init", [8], 0.5),
     "{file}: idx_prem_factor_init must be a number, 1 or more; it is not at point_id [8]"),
    ("an infinite premium factor", _set("idx_prem_factor_init", [8], float("inf")),
     "{file}: idx_prem_factor_init must be a number, 1 or more; it is not at point_id [8]"),
    ("a negative review factor", _set("review_prem_factor_init", [9], -0.1),
     "{file}: review_prem_factor_init must be a number, zero or more; it is not at "
     "point_id [9]"),
    ("a text review factor", _set("review_prem_factor_init", [10], "x"),
     "{file}: review_prem_factor_init must be a number, zero or more; it is not at "
     "point_id [10]"),
    ("an infinite review factor", _set("review_prem_factor_init", [11], float("inf")),
     "{file}: review_prem_factor_init must be a number, zero or more; it is not at "
     "point_id [11]"),
    ("a negative select factor", _set("ci_sel_factor_init", [10], -1.0),
     "{file}: ci_sel_factor_init must be a number, zero or more; it is not at point_id "
     "[10]"),
    ("a blank select factor", _set("ci_sel_factor_init", [9], float("nan")),
     "{file}: ci_sel_factor_init must be a number, zero or more; it is not at point_id "
     "[9]"),
    ("an infinite select factor", _set("ci_sel_factor_init", [9], float("inf")),
     "{file}: ci_sel_factor_init must be a number, zero or more; it is not at point_id "
     "[9]"),
    ("a latch of 2", _set("ci_sel_latched_init", [10], 2),
     "{file}: ci_sel_latched_init must be 0 or 1; it is not at point_id [10]"),
    ("a latch of a half", _set("ci_sel_latched_init", [8], 0.5),
     "{file}: ci_sel_latched_init must be 0 or 1; it is not at point_id [8]"),
    ("a blank latch", _set("ci_sel_latched_init", [9], float("nan")),
     "{file}: ci_sel_latched_init must be 0 or 1; it is not at point_id [9]"),
    ("a latch written True", _set("ci_sel_latched_init", [11], "True"),
     "{file}: ci_sel_latched_init must be 0 or 1; it is not at point_id [11]"),
    ("a review change below -1", _set("review_prem_shock_init", [10], -1.5),
     "{file}: review_prem_shock_init must be a number, -1 or more; it is not at point_id "
     "[10]"),
    ("a blank review change", _set("review_prem_shock_init", [11], float("nan")),
     "{file}: review_prem_shock_init must be a number, -1 or more; it is not at point_id "
     "[11]"),
    ("an infinite review change", _set("review_prem_shock_init", [9], float("inf")),
     "{file}: review_prem_shock_init must be a number, -1 or more; it is not at point_id "
     "[9]"),
    ("a cover factor on new business", _set("idx_factor_init", [4], 1.03),
     "{file}: idx_factor_init must be 1 on a policy not yet in force, duration_mth 0 or "
     "less; it is not at point_id [4]"),
    ("a premium factor on future business", _set("idx_prem_factor_init", [13], 1.045),
     "{file}: idx_prem_factor_init must be 1 on a policy not yet in force, duration_mth 0 "
     "or less; it is not at point_id [13]"),
    ("a review factor on new business", _set("review_prem_factor_init", [3], 1.1),
     "{file}: review_prem_factor_init must be 1 on a policy not yet in force, duration_mth "
     "0 or less; it is not at point_id [3]"),
    ("a select factor on future business", _set("ci_sel_factor_init", [13], 1.1),
     "{file}: ci_sel_factor_init must be 1 on a policy not yet in force, duration_mth 0 or "
     "less; it is not at point_id [13]"),
    ("a closed latch on future business", _set("ci_sel_latched_init", [13], 1),
     "{file}: ci_sel_latched_init must be 0 on a policy not yet in force, duration_mth 0 "
     "or less; it is not at point_id [13]"),
    # No anniversary has passed in a policy's first twelve months: the indexed point on its
    # third anniversary, moved back into its first policy year with its factors.
    ("a cover factor in the first policy year", _set("duration_mth", [8], 11),
     "{file}: idx_factor_init must be 1 on a policy in force fewer than 12 months, before "
     "its first anniversary; it is not at point_id [8]"),
    ("a premium factor in the first policy year",
     _then(_set("duration_mth", [8], 1), _set("idx_factor_init", [8], 1.0)),
     "{file}: idx_prem_factor_init must be 1 on a policy in force fewer than 12 months, "
     "before its first anniversary; it is not at point_id [8]"),
    # An open latch is read at 1, whatever its factor says, so the factor must say 1.
    ("an open latch with a factor", _set("ci_sel_factor_init", [10], 1.1),
     "{file}: ci_sel_factor_init must be 1 on an open latch, ci_sel_latched_init 0; it is "
     "not at point_id [10]"),
    ("an open latch with a factor below 1", _set("ci_sel_factor_init", [11], 0.95),
     "{file}: ci_sel_factor_init must be 1 on an open latch, ci_sel_latched_init 0; it is "
     "not at point_id [11]"),
    ("a review change on new business", _set("review_prem_shock_init", [3], 0.1),
     "{file}: review_prem_shock_init must be 0 on a policy not yet in force, duration_mth "
     "0 or less; it is not at point_id [3]"),
    ("a blank flag", _set("children_cover", [3], float("nan")),
     "{file}: children_cover must be True or False; it is not at point_id [3]"),
    ("a flag written yes", _set("indexation", [2], "yes"),
     "{file}: indexation must be True or False; it is not at point_id [2]"),
    ("a flag written 1", _set("children_cover", [1], 1),
     "{file}: children_cover must be True or False; it is not at point_id [1]"),
    ("an unknown contract type", _set("contract_type", [1], "term"),
     "{file}: contract_type must be accelerated or standalone; it is not at point_id [1]"),
    ("an unknown life basis", _set("life_basis", [2], "joint"),
     "{file}: life_basis must be single or joint_first_event; it is not at point_id [2]"),
    ("an unknown sex", _set("sex", [2], "X"),
     "{file}: sex must be M or F; it is not at point_id [2]"),
    ("term assurance's smoker code", _set("smoker", [3], "N"),
     "{file}: smoker must be NS or S; it is not at point_id [3]"),
    ("a cover basis out of scope", _set("cover_basis", [1], "decreasing"),
     "{file}: cover_basis must be level; it is not at point_id [1]"),
    ("an unknown premium guarantee", _set("premium_guarantee", [4], "fixed"),
     "{file}: premium_guarantee must be guaranteed or reviewable; it is not at point_id "
     "[4]"),
    ("an unknown premium mode", _set("premium_mode", [5], "weekly"),
     "{file}: premium_mode must be monthly or annual; it is not at point_id [5]"),
    ("a blank issue age", _set("age_at_entry", [1], float("nan")),
     "{file}: age_at_entry must be a finite number; it is not at point_id [1]"),
    ("an infinite issue age", _set("age_at_entry", [2], float("inf")),
     "{file}: age_at_entry must be a finite number; it is not at point_id [2]"),
    ("a text issue age", _set("age_at_entry", [3], "x40"),
     "{file}: age_at_entry must be a finite number; it is not at point_id [3]"),
    ("a blank term", _set("policy_term", [4], float("nan")),
     "{file}: policy_term must be a finite number; it is not at point_id [4]"),
    ("a negative sum assured", _set("sum_assured", [1], -1.0),
     "{file}: sum_assured must be a number, zero or more; it is not at point_id [1]"),
    ("a text premium", _set("premium_mth", [2], "55 pounds"),
     "{file}: premium_mth must be a number, zero or more; it is not at point_id [2]"),
    ("an infinite premium", _set("premium_mth", [6], float("inf")),
     "{file}: premium_mth must be a number, zero or more; it is not at point_id [6]"),
    ("a joint point with no second age", _set("joint_age", [7], float("nan")),
     "{file}: joint_age must be a finite number on a joint first-event point; it is not "
     "at point_id [7]"),
    ("a joint point with an unknown second sex", _set("joint_sex", [7], "X"),
     "{file}: joint_sex must be M or F on a joint first-event point; it is not at "
     "point_id [7]"),
    ("a joint point with term assurance's smoker code", _set("joint_smoker", [7], "N"),
     "{file}: joint_smoker must be NS or S on a joint first-event point; it is not at "
     "point_id [7]"),
    ("a joint point on the standalone contract", _set("contract_type", [7], "standalone"),
     "{file}: a joint first-event point must be accelerated, the standalone joint first "
     "event being out of scope; it is not at point_id [7]"),
    ("a cover factor without indexation", _set("idx_factor_init", [9], 1.2),
     "{file}: idx_factor_init must be 1 without indexation; it is not at point_id [9]"),
    ("a premium factor without indexation", _set("idx_prem_factor_init", [12], 1.2),
     "{file}: idx_prem_factor_init must be 1 without indexation; it is not at point_id "
     "[12]"),
    ("a review factor on a guaranteed point", _set("review_prem_factor_init", [8], 1.1),
     "{file}: review_prem_factor_init must be 1 on a guaranteed point; it is not at "
     "point_id [8]"),
    ("a closed latch on a guaranteed point",
     _then(_set("ci_sel_latched_init", [12], 1), _set("ci_sel_factor_init", [12], 1.1)),
     "{file}: ci_sel_latched_init must be 0 on a guaranteed point; it is not at point_id "
     "[12]"),
    ("a review change on a guaranteed point", _set("review_prem_shock_init", [8], 0.1),
     "{file}: review_prem_shock_init must be 0 on a guaranteed point; it is not at "
     "point_id [8]"),
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
    months, 0 or more, is itself refused, a NaN and an infinity among them: either would
    admit every policy.
    Setting the Reference clears the table, so each value is read afresh.
    """
    future = _label(_committed(), "future", 4, -13)
    later = (f"{TABLE}: duration_mth must be -12 or more, a policy issued at most 12 months "
             f"after the valuation date; it is not at point_id [{future}]")
    no_future = (f"{TABLE}: duration_mth must be 0 or more: this model takes no future new "
                 f"business; it is not at point_id [{future}]")
    model = mx.read_model(_sec_inputs(tmp_path, _committed()), name=_name("horizon"))
    try:
        assert model.Data.future_horizon_mth == 120
        off = "future_horizon_mth must be a whole number of months, 0 or more, not {}"
        for horizon, refusal in ((13, None), (12, later), (0, no_future),
                                 *((h, off.format(h)) for h in (
                                     -1, 12.5, math.nan, math.inf, -math.inf)),
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
    """A point whose cover has ended has no frame, and ``proj_len()`` refuses it by name.

    The anchor cell in its last covered month is moved on to ``duration_mth`` 300, the
    month its 25-year term ends.  That is a rule of the product, not of the table: it needs
    the term the point's own columns give, read where the frame is defined, so the table
    reads, and the point is refused on its first projection, rather than projecting
    nothing.  A loop over the block would meet the point only when it reached it, after
    projecting the points before it, so ``run_sec.py --block``, run beside the table, asks
    every point for its frame first: it fails naming the point, and prints nothing before.
    And one month earlier, 299, the last covered month, is the committed row, which
    projects one month.
    """
    moved = _label(_committed(), "derived", 1, 299)
    model = _read_edited(tmp_path, _set("duration_mth", [moved], 300))
    message = (f"point_id {moved}: duration_mth 300 is at or past the end of cover, policy "
               f"month 300")
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


# What the contract does not issue, refused by proj_len() as a point past its cover is, as
# (case, the table's edit, the References set, the point, the message, and the frame the
# point projects at the shipped References, or None).  Data reads a term and an issue age
# as CI_UK_S does, so each reads.  product-spec.md writes terms of 5 to 50 years, entry ages
# from 18 to 64 and cover ending by the 75th birthday, and the compiled caches will be sized
# from them; each bound is refused just inside it here, and accepted at it in the edges
# test.  And each bound, moved past a committed twin, refuses it, which at the shipped bound
# projects its frame: the Reference is what refuses it.  Point 1 is the anchor cell, issued
# at 40 for 25 years; point 7 joint, its second life 38.
NOT_ISSUED = [
    ("a 51-year term", _set("policy_term", [1], 51), {}, 1,
     "point_id 1: the term, 51 years, is above policy_term_max, 50", None),
    ("a term above a bound lowered to 24", None, {"policy_term_max": 24}, 1,
     "point_id 1: the term, 25 years, is above policy_term_max, 24", 300),
    ("a 4-year term", _set("policy_term", [1], 4), {}, 1,
     "point_id 1: the term, 4 years, is below policy_term_min, 5", None),
    ("a term below a bound raised to 26", None, {"policy_term_min": 26}, 1,
     "point_id 1: the term, 25 years, is below policy_term_min, 26", 300),
    ("an issue age of 17", _set("age_at_entry", [1], 17), {}, 1,
     "point_id 1: life 1's issue age, 17, is below issue_age_min, 18", None),
    ("an issue age below a bound raised to 41", None, {"issue_age_min": 41}, 1,
     "point_id 1: life 1's issue age, 40, is below issue_age_min, 41", 300),
    ("a second life issued at 17", _set("joint_age", [7], 17), {}, 7,
     "point_id 7: life 2's issue age, 17, is below issue_age_min, 18", None),
    ("a second life below a bound raised to 39", None, {"issue_age_min": 39}, 7,
     "point_id 7: life 2's issue age, 38, is below issue_age_min, 39", 300),
    ("an issue age of 65", _then(_set("age_at_entry", [1], 65), _set("policy_term", [1], 5)),
     {}, 1, "point_id 1: life 1's issue age, 65, is above issue_age_max, 64", None),
    ("an issue age above a bound lowered to 39", None, {"issue_age_max": 39}, 1,
     "point_id 1: life 1's issue age, 40, is above issue_age_max, 39", 300),
    ("a second life issued at 65",
     _then(_set("joint_age", [7], 65), _set("policy_term", [7], 5)), {}, 7,
     "point_id 7: life 2's issue age, 65, is above issue_age_max, 64", None),
    ("cover to 76", _set("age_at_entry", [1], 51), {}, 1,
     "point_id 1: life 1's cover runs to attained age 76, issue age 51 and a 25-year "
     "term, past expiry_age_max, 75", None),
    ("cover past a bound lowered to 64", None, {"expiry_age_max": 64}, 1,
     "point_id 1: life 1's cover runs to attained age 65, issue age 40 and a 25-year "
     "term, past expiry_age_max, 64", 300),
    ("a second life covered to 76", _set("joint_age", [7], 51), {}, 7,
     "point_id 7: life 2's cover runs to attained age 76, issue age 51 and a 25-year "
     "term, past expiry_age_max, 75", None),
]


@pytest.mark.parametrize("case, edit, refs, point, message, frame", NOT_ISSUED,
                         ids=[c[0] for c in NOT_ISSUED])
def test_a_point_the_contract_does_not_issue_is_refused_by_proj_len(tmp_path, case, edit,
                                                                    refs, point, message,
                                                                    frame):
    """``proj_len()`` refuses a point outside the contract's bounds, naming it (§6.2).

    ``CI_UK_S`` projects a term of any length from any age its tables reach, and so would
    modelx here, but the contract does not write it, and the compiled model's caches will
    be sized from the contract: a frame of at most 50 years and the horizon, attained ages
    from 18 to 74.  So the frame refuses such a point, naming it, as it refuses a point past
    its cover, and every report with it (:data:`NOT_ISSUED`): each bound just inside it, a
    life of a joint point among them, and each bound moved past a committed twin, which
    projects at the shipped bound, on a model read afresh.  A bound off by one, a life the
    rule forgot, or a refusal lost, lets a point through.  The table reads either way.
    Every Reference is set on a model just read, before its projection computes anything
    (K7).
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


# Each Reference this model raises to a power, divides by, bounds a rate or a benefit with,
# or reads as a share, a loading, a frequency or an amount, as (the domain proj_len() names,
# the S point whose twin reads it, the values at its edges it accepts, the values it
# refuses: next outside each edge, NaN and the infinities).  The five review References are
# read on a reviewable point alone, and refused there; the others on every point.
#   - the contract's bounds, policy_term_min and _max, issue_age_min and _max and
#     expiry_age_max: a NaN bound fails every comparison and so refuses nothing, and an
#     infinite one bounds nothing.  At 0, the edge, a lower bound admits the twin and an
#     upper one refuses it by its own rule, which names the bound;
#   - ci_trend, inflation_rate and sel_lapse_ci_loading: below -1 the factors they make,
#     1 + tau, 1 + i and 1 + eta, are negative, and so are the diagnosis rate and the
#     expenses they multiply;
#   - overlap_k and survival_slip: the shares of the deaths and of the diagnoses that do not
#     pay, which outside 0 to 1 make a negative claim, paid or exit rate;
#   - ap_freq_factor and child_freq: past 12 a month's additional payments or children's
#     claims number more than one per policy in force, below 0 fewer than none (the bound
#     derived in ap_rate's and child_rate_mth's docstrings);
#   - rpi_rate: an infinity reads as the cap or as no increase, through the floor and the
#     cap; idx_cover_cap, idx_prem_cap and idx_prem_mult: below 0 an increase is a cut, and
#     a NaN cap is lost through the min it bounds, its bound second;
#   - ap_share and child_share: shares of the indexed cover; ap_cap and child_cap: below 0
#     a negative benefit, and a NaN one lost through min; the three expenses: below 0 an
#     income; and claim_split_tol: at an infinity the claim split's check passes anything;
#   - review_period_mths: the reviews divide the policy months by it, which at 0 divides by
#     zero, below it counts reviews backward, and off a whole number counts them in parts;
#   - review_lapse_cap: the shock lapse is at most the cap, past 1 its monthly rate,
#     1 - (1 - w)^(1/12), has no real value, which CI_UK_S projects as a complex number,
#     and below 0 the window lapses a negative share;
#   - review_prem_shock: below -1 a review takes the premium below 0;
#   - review_lapse_threshold: the latch and the window compare a change with it, and a NaN
#     fails both comparisons, which closes the latch at every review;
#   - review_lapse_slope: below 0 the window lapses fewer the more the premium rises, and a
#     NaN reads as the cap through the lapse rate's min, its bound first.
# The largest finite float is an edge of each domain that is unbounded above; and the
# floats next outside each edge.
_BIG = sys.float_info.max
_OFF_EDGES = (math.nan, math.inf, -math.inf)
_BELOW_M1, _BELOW_0 = math.nextafter(-1.0, -2.0), math.nextafter(0.0, -1.0)
_ABOVE_1, _ABOVE_12 = math.nextafter(1.0, 2.0), math.nextafter(12.0, 13.0)
_WHOLE = ("a whole number, 0 or more", 1, (0,), (-1, 0.5, *_OFF_EDGES))
_AMOUNT = ("a finite number, 0 or more", 1, (0.0, _BIG), (_BELOW_0, *_OFF_EDGES))
_INDEX = ("a finite number, 0 or more", 4, (0.0, _BIG), (_BELOW_0, *_OFF_EDGES))
_SHARE = ("a number from 0 to 1", 1, (0.0, 1.0), (_BELOW_0, _ABOVE_1, *_OFF_EDGES))
BOUNDS = ("policy_term_min", "policy_term_max", "issue_age_min", "issue_age_max",
          "expiry_age_max")
DOMAINS = {
    **{bound: _WHOLE for bound in BOUNDS},
    "ci_trend": ("a finite number, -1 or more", 1, (-1.0,), (_BELOW_M1, *_OFF_EDGES)),
    "inflation_rate": ("a finite number, -1 or more", 1, (-1.0,), (_BELOW_M1, *_OFF_EDGES)),
    "sel_lapse_ci_loading": ("a finite number, -1 or more", 3, (-1.0,),
                             (_BELOW_M1, *_OFF_EDGES)),
    "overlap_k": ("a number from 0 to 1", 1, (0.0, 1.0), (_BELOW_0, _ABOVE_1, *_OFF_EDGES)),
    "survival_slip": ("a number from 0 to 1", 2, (0.0, 1.0),
                      (_BELOW_0, _ABOVE_1, *_OFF_EDGES)),
    "ap_freq_factor": ("a number from 0 to 12", 1, (0.0, 12.0),
                       (_BELOW_0, _ABOVE_12, *_OFF_EDGES)),
    "child_freq": ("a number from 0 to 12", 1, (0.0, 12.0),
                   (_BELOW_0, _ABOVE_12, *_OFF_EDGES)),
    "rpi_rate": ("a finite number", 4, (-_BIG, _BIG), _OFF_EDGES),
    "idx_cover_cap": _INDEX,
    "idx_prem_mult": _INDEX,
    "idx_prem_cap": _INDEX,
    "ap_share": _SHARE,
    "ap_cap": _AMOUNT,
    "child_share": _SHARE,
    "child_cap": _AMOUNT,
    "expense_acq": _AMOUNT,
    "expense_maint": _AMOUNT,
    "expense_claim": _AMOUNT,
    "claim_split_tol": ("a finite number, 0 or more", 2, (0.0, _BIG),
                        (_BELOW_0, *_OFF_EDGES)),
    "review_period_mths": ("a whole number of months, 1 or more", 3, (1, 61),
                           (0, -60, 60.5, *_OFF_EDGES)),
    "review_lapse_cap": ("a number from 0 to 1", 3, (0.0, 1.0),
                         (_BELOW_0, _ABOVE_1, *_OFF_EDGES)),
    "review_prem_shock": ("a finite number, -1 or more", 3, (-1.0,),
                          (_BELOW_M1, *_OFF_EDGES)),
    "review_lapse_threshold": ("a finite number", 3, (-_BIG, _BIG), _OFF_EDGES),
    "review_lapse_slope": ("a finite number, 0 or more", 3, (0.0, _BIG),
                           (_BELOW_0, *_OFF_EDGES)),
}
REVIEW_REFS = frozenset(ref for ref in DOMAINS if ref.startswith("review_"))
DOMAIN_CASES = [pytest.param(ref, value, refused, id=f"{ref} at {value!r}")
                for ref, (_, _, accepted, off) in DOMAINS.items()
                for values, refused in ((accepted, False), (off, True)) for value in values]

# The premium change the cases review at: past the threshold, so that every review opens a
# window whose lapse reads the cap, and closes the latch.  And the change at which S's
# shock lapse, w + 2 (rho - 0.05), passes 1 in the first review's window, w being 4% there,
# so that a cap past 1 binds nothing and S's monthly lapse rate is complex.
REVIEW_SHOCK = 0.20
REVIEW_SHOCK_PAST_1 = 0.60


@pytest.mark.parametrize("ref, value, refused", DOMAIN_CASES)
def test_a_reference_outside_its_domain_is_refused(ref, value, refused):
    """A Reference off its domain is refused on every point that reads it (T5).

    ``CI_UK_S`` raises each of :data:`DOMAINS`' References to a power, divides by it,
    bounds a rate or a benefit with it, or reads it as a share, a loading, a frequency or
    an amount, and checks none: off its domain it projects a negative premium, rate, benefit
    or expense with every check passing, as a trend of -3, an overlap of 3, a review change
    of -150% or a cover cap of -2 would, or a complex lapse rate; and a NaN fails every
    comparison it meets, so that a NaN threshold closes the latch at every review, adding
    5.3% to the reviewable point's main claims, a NaN slope reads as the cap, a NaN cap is
    lost through its ``min``, and a NaN bound refuses nothing.  This model keeps S's
    formulas, and its frame refuses such a Reference, naming the point, the Reference, its
    domain and its value: the value next outside each edge, NaN and both infinities, on
    every point that reads it, a review Reference on every reviewable point, where a
    guaranteed one, which reads none, projects whatever it is.  At its edges the twin of the
    S point that reads it projects, and is S's in every cell; but a bound of the contract,
    which ``CI_UK_S`` has none of, at 0 admits the twin as a lower bound, and as an upper
    one refuses it by its own rule, naming the bound, and not as off its domain.  The
    review change is :data:`REVIEW_SHOCK`, past the threshold, but where it is the
    Reference the case sets; where the cap passes 1, S reviews at
    :data:`REVIEW_SHOCK_PAST_1`, so that its shock lapse passes 1 and is not capped, and its
    monthly rate is complex in the first review's window.  Each is set in both models as
    each is read, before either computes anything, the form that runs compiled unchanged
    (K7).
    """
    what, s_point, _, _ = DOMAINS[ref]
    refs = {"review_prem_shock": REVIEW_SHOCK, ref: value}
    sec = mx.read_model(model_path(SEC), name=_name("domain"))
    try:
        for name, v in refs.items():
            setattr(sec.Projection, name, v)
        table = sec.Data.model_point_table()
        readers = table.index.tolist()
        if ref in REVIEW_REFS:
            readers = table.index[table["premium_guarantee"] == "reviewable"].tolist()
            assert len(_point(sec, 1).result_cf()) == 300
        assert readers
        if refused:
            for label in readers:
                _refused(_point(sec, label).result_cf,
                         f"point_id {label}: {ref} must be {what}, not {value}")
        elif ref in BOUNDS:
            p = _point(sec, s_point)
            if ref.endswith("_min"):
                assert len(p.result_cf()) == p.proj_len() == 300
            else:
                _refused(p.result_cf, f" {ref}, {value}")
        else:
            s = mx.read_model(model_path(TWIN), name=_name("domain_s"))
            try:
                for name, v in refs.items():
                    setattr(s.Projection, name, v)
                s_proj, p = _point(s, s_point), _point(sec, s_point)
                _sweep_s(s_proj)
                assert len(p.result_cf()) == p.proj_len()
                assert _compare(s_proj, p, 0, TWIN_EXEMPT_DEFAULT | SPEC.exempt) == []
            finally:
                s.close()
    finally:
        sec.close()
    if ref == "review_lapse_cap" and value > 1.0:
        s = mx.read_model(model_path(TWIN), name=_name("domain_past_1"))
        try:
            s.Projection.review_lapse_cap = value
            s.Projection.review_prem_shock = REVIEW_SHOCK_PAST_1
            assert isinstance(_point(s, 3).lapse_rate_mth(60), complex)
        finally:
            s.close()


def _reviewed_too_soon(point, duration, column, value, issue):
    """The message ``proj_len()`` gives a reviewable point in force ``duration`` months,
    before the shipped first review, whose ``column`` holds ``value``."""
    return (f"point_id {point}: {column} is {value}, where a reviewable point in force "
            f"{duration} months, fewer than review_period_mths, 60, has had no review yet: "
            f"{issue}")


# A review history S cannot reach, as (case, the table's edit, the References set, the
# point, the message).  No review is made before the fifth anniversary, so a reviewable
# point in force fewer months than the review period has had none: point 9, the reviewable
# point on its first review, moved back to 59, 1 and 30 months, is refused a review factor,
# a latch and a review change, each in turn; and at 60, its own month, the first review's,
# once the review period is lengthened to 61.  On its own month at the shipped period the
# row carries its first review's history, which the edges test accepts.
REVIEWED_TOO_SOON = [
    ("a review factor before the first review",
     _then(_set("duration_mth", [9], 59), _set("review_prem_factor_init", [9], 1.1)), {}, 9,
     _reviewed_too_soon(9, 59, "review_prem_factor_init", 1.1, 1)),
    ("a latch before the first review",
     _then(_set("duration_mth", [9], 1), _set("ci_sel_latched_init", [9], 1),
           _set("ci_sel_factor_init", [9], 1.1)), {}, 9,
     _reviewed_too_soon(9, 1, "ci_sel_latched_init", 1, 0)),
    ("a review change before the first review",
     _then(_set("duration_mth", [9], 30), _set("review_prem_shock_init", [9], 0.1)), {}, 9,
     _reviewed_too_soon(9, 30, "review_prem_shock_init", 0.1, 0)),
    ("a review factor inside a review period lengthened to 61",
     _set("review_prem_factor_init", [9], 1.1), {"review_period_mths": 61}, 9,
     "point_id 9: review_prem_factor_init is 1.1, where a reviewable point in force 60 "
     "months, fewer than review_period_mths, 61, has had no review yet: 1"),
]


@pytest.mark.parametrize("case, edit, refs, point, message", REVIEWED_TOO_SOON,
                         ids=[c[0] for c in REVIEWED_TOO_SOON])
def test_a_review_history_before_the_first_review_is_refused(tmp_path, case, edit, refs,
                                                             point, message):
    """``proj_len()`` refuses a review history on a reviewable point in force fewer months
    than the review period (§6.2, T5).

    ``Data`` reads the table, since its rule is a product's: the review period is
    ``review_period_mths``, a Reference of the projection, which ``Data`` cannot see, so the
    frame refuses the point, naming it and the column, as it refuses a point past its cover
    (:data:`REVIEWED_TOO_SOON`).  Every Reference is set on a model just read (K7).
    """
    model = _read_edited(tmp_path, edit)
    try:
        for ref, value in refs.items():
            setattr(model.Projection, ref, value)
        model.Data.model_point_table()
        _refused(_point(model, point).result_cf, message)
    finally:
        model.close()


def _one_review(point, duration, factor, change, period=60):
    """The message ``proj_len()`` gives a reviewable point in force ``duration`` months,
    one review made, whose review factor is not 1 plus that review's change."""
    return (f"point_id {point}: review_prem_factor_init is {factor}, where a reviewable "
            f"point in force {duration} months, review_period_mths {period}, has had one "
            f"review, whose change, review_prem_shock_init, is {change}: {1.0 + change}")


def _reviewed(points, factor, change):
    """An edit of the table that gives ``points`` a review factor and a last change."""
    return _then(_set("review_prem_factor_init", points, factor),
                 _set("review_prem_shock_init", points, change))


# A review factor the one review made cannot have given, as (case, the table's edit, the
# References set, the point, the message, or None where the row is accepted).  Between the
# first review and the second the one review made is the one whose change
# review_prem_shock_init holds, so the factor is 1 plus that change: point 9, on its first
# review, point 10 inside its window and point 11 after it, each holding a factor and a
# change that disagree, are refused.  Two reviews give a factor any two changes make, so
# point 11's pair, refused at the shipped period, is accepted once the period is shortened
# to 39 months, when its 78 months hold two.  The rule's edges are pinned: a factor 2e-12
# of itself off 1.1 is refused and one 0.5e-12 off is accepted, the rule reading to 1e-12
# as an extract may spell the two; and a mismatch in month 119, the last before the second
# review, is refused, and one in month 120, the second review's, accepted.  The latch is
# not asked: one left open after a change past today's threshold is a history the
# threshold of its day may have given.
ONE_OFF, ONE_NEAR = 1.1 * (1.0 + 2e-12), 1.1 * (1.0 + 0.5e-12)
ONE_REVIEW_MADE = [
    ("a factor the first review's change did not give",
     _reviewed([9], 1.3, 0.2), {}, 9, _one_review(9, 60, 1.3, 0.2)),
    ("a factor with no change", _set("review_prem_factor_init", [11], 1.1), {}, 11,
     _one_review(11, 78, 1.1, 0.0)),
    ("a change with no factor", _set("review_prem_shock_init", [10], 0.1), {}, 10,
     _one_review(10, 66, 1.0, 0.1)),
    ("two changes' factor at one review", _reviewed([11], 1.21, 0.1), {}, 11,
     _one_review(11, 78, 1.21, 0.1)),
    ("two changes' factor at two reviews", _reviewed([11], 1.21, 0.1),
     {"review_period_mths": 39}, 11, None),
    ("a factor 2e-12 of itself off", _reviewed([11], ONE_OFF, 0.1), {}, 11,
     _one_review(11, 78, ONE_OFF, 0.1)),
    ("a factor 0.5e-12 of itself off", _reviewed([11], ONE_NEAR, 0.1), {}, 11, None),
    ("a mismatch in the month before the second review",
     _then(_set("duration_mth", [11], 119), _reviewed([11], 1.3, 0.0)), {}, 11,
     _one_review(11, 119, 1.3, 0.0)),
    ("a mismatch on the second review",
     _then(_set("duration_mth", [11], 120), _reviewed([11], 1.3, 0.0)), {}, 11, None),
]


@pytest.mark.parametrize("case, edit, refs, point, message", ONE_REVIEW_MADE,
                         ids=[c[0] for c in ONE_REVIEW_MADE])
def test_a_review_factor_one_review_cannot_give_is_refused(tmp_path, case, edit, refs,
                                                           point, message):
    """``proj_len()`` refuses a review factor the one review made did not give (T5).

    A reviewable point between its first review and its second has had one, whose change is
    ``review_prem_shock_init``, so its review factor is ``1 + review_prem_shock_init``: any
    other is a history no policy has, which the frame refuses, naming the point, the factor
    and the change (:data:`ONE_REVIEW_MADE`).  At two reviews or more no such rule holds,
    and the row projects; nor does it at a factor that departs by less than 1e-12 of
    itself.  Every Reference is set on a model just read (K7).
    """
    model = _read_edited(tmp_path, edit)
    try:
        for ref, value in refs.items():
            setattr(model.Projection, ref, value)
        model.Data.model_point_table()
        p = _point(model, point)
        if message is None:
            assert len(p.result_cf()) == p.proj_len()
        else:
            _refused(p.result_cf, message)
    finally:
        model.close()


# The pivot table's male non-smoker mortality raised at its last two pivots, 0.5 at 60 and
# 1.0 at 65, rates Data accepts, which the interpolation extrapolates past 1 above 65.  On
# a standalone point issued at 50, the non-paying exit rate q_exit, q_d (1 - k) + i_ci delta,
# which CI_UK_S leaves uncapped since it is never a decrement, then passes 1.
CI_RATES = "ci_rate_table.csv"
EXIT_TABLE = {CI_RATES: lambda t: t.assign(q_d=t["q_d"].mask(
    (t["sex"] == "M") & (t["smoker"] == "NS") & (t["age"] == 60), 0.5).mask(
    (t["sex"] == "M") & (t["smoker"] == "NS") & (t["age"] == 65), 1.0))}


def test_an_exit_rate_past_1_is_refused_in_the_month_it_passes(tmp_path):
    """The claim split's exit rate past 1 is refused, naming the point and the month (T5).

    ``check_claim_split_resid`` converts the notes' annual exit rate, ``q_exit = q_d (1 -
    k) + i_ci delta``, to a monthly one independently, to bound the split's artefact, and
    ``CI_UK_S`` caps no part of it: past 1 the conversion has no real value, and S's
    residual is a complex number, whose magnitude its check compares without a word.  Here
    the residual raises in the month ``q_exit`` first passes 1, naming the point, the month,
    the rate, the two rates it is made of and the References, on a standalone point issued
    at 50, under :data:`EXIT_TABLE`, where S's is complex in that month and real, and this
    model's S's, in every month before.  At rates this high the split's artefact passes the
    shipped ``claim_split_tol`` some months earlier, where the check returns False as S's
    does, so with the tolerance raised to 1 the check runs on to the month and raises too.
    The accelerated twin of the same point has no split, and projects, its claim rate capped
    at 1.  The tolerance is set on a model just read (K7).
    """
    edit = _then(_set("age_at_entry", [1, 2], 50))
    model = _read_edited(tmp_path / "sec", edit, edits=EXIT_TABLE)
    s = mx.read_model(temp_inputs(tmp_path / "s", model_path(TWIN),
                                  model_points=_s_table().loc[[1, 2]].assign(age_at_entry=50),
                                  edits=EXIT_TABLE), name=_name("exit_s"))
    try:
        model.Projection.claim_split_tol = 1.0
        sp = _point(s, 2)
        resid = [sp.check_claim_split_resid(t) for t in range(sp.proj_len())]
        first = next(t for t, r in enumerate(resid) if isinstance(r, complex))
        assert not any(isinstance(r, complex) for r in resid[:first])
        assert any(abs(r) > sp.claim_split_tol for r in resid[:first])
        p = _point(model, 2)
        q = sp.mort_rate(first) * (1.0 - sp.overlap_k) + sp.ci_rate(first) * sp.survival_slip
        assert q > 1.0
        message = (f"point_id 2: the annual exit rate q_exit({first}), q_d (1 - overlap_k) + "
                   f"i_ci survival_slip, is {q}, past 1, at q_d {sp.mort_rate(first)} and "
                   f"i_ci {sp.ci_rate(first)} under overlap_k 0.1 and survival_slip 0.03: "
                   f"its monthly rate has no real value")
        _refused(lambda: p.check_claim_split_resid(first), message)
        _refused(p.check_claim_split, message)
        assert all(p.check_claim_split_resid(t) == pytest.approx(resid[t], rel=1e-9, abs=0)
                   for t in range(first))
        accelerated = _point(model, 1)
        assert accelerated.check_claim_split() and accelerated.check_pols_roll_fwd()
        assert accelerated.claim_rate(first) == 1.0
    finally:
        model.close()
        s.close()


def test_the_edges_of_the_in_force_interface_are_accepted(sec_model, tmp_path):
    """A zero count, whole numbers in any type, the horizon and each bound's edge are read.

    A count of 0 is a point that projects zeros; ``66.0`` is a whole number of months,
    read back as the int the policy clock counts in; a policy issued 120 months after the
    valuation date, the shipped ``future_horizon_mth``, is the last one the table admits,
    with a frame of 420 months, 300 of cover after 120 before issue.  A reviewable row
    valued in its first month, 1, holds no review history, and one valued on its first
    review, 60, a review factor, a closed latch, its factor and a change, the history a
    policy has once a review is made.  A review may cut the premium: one valued after its
    first review holds a change of -25% and a factor of 0.75, and one at the edge, a change
    of -100%, a factor of 0, and pays no premium from then on.  The indexed point valued in
    its first policy year, at 11 months, holds no increase, and on its first anniversary,
    12, the first.  A latch closed at a loading of -1, the edge ``proj_len()`` admits, has
    a factor of 0, the state ``CI_UK_S`` reaches at that loading under a review change of
    10% at month 72, and the diagnosis rate is 0 from then on.  And each bound of the
    contract at its edge projects: a 50-year term from issue at 18, a 5-year term at 64,
    issue at 18 and 64 of each life of a joint point, and cover to 75, of each life.  The
    extra rows are copies of committed rows under labels of their own, 21 to 25.
    """
    committed = _committed()
    last = _label(committed, "derived", 1, 299)
    future = _label(committed, "future", 4, -13)
    first = _label(committed, "derived", 3, 66)
    review = _label(committed, "derived", 3, 60)
    window = _label(committed, "derived", 3, 78)
    indexed = _label(committed, "derived", 4, 36)
    copies = {21: (window, {"review_prem_factor_init": 0.75,
                            "review_prem_shock_init": -0.25}),
              22: (window, {"review_prem_factor_init": 0.0,
                            "review_prem_shock_init": -1.0}),
              23: (indexed, {"duration_mth": 11, "idx_factor_init": 1.0,
                             "idx_prem_factor_init": 1.0}),
              24: (indexed, {"duration_mth": 12, "idx_factor_init": 1.03,
                             "idx_prem_factor_init": 1.045}),
              25: (window, {"duration_mth": 72, "review_prem_factor_init": 1.1,
                            "review_prem_shock_init": 0.1, "ci_sel_latched_init": 1,
                            "ci_sel_factor_init": 0.0})}

    def edit(table):
        extra = []
        for label, (source, changes) in copies.items():
            row = table.loc[[source]].assign(policy_id=f"CI-9000{label}", **changes)
            row.index = pd.Index([label], name="point_id")
            extra.append(row)
        table = pd.concat([table, *extra])
        table = _set("policy_count", [last], 0.0)(table)
        table = _set("duration_mth", [first], 1)(table)
        table = table.assign(duration_mth=table["duration_mth"].astype(float))
        table = _set("duration_mth", [window], 66.0)(table)
        table = _set("duration_mth", [future], -120.0)(table)
        table = _set("review_prem_factor_init", [review], 1.25)(table)
        table = _set("ci_sel_latched_init", [review], 1)(table)
        table = _set("ci_sel_factor_init", [review], 1.1)(table)
        table = _set("review_prem_shock_init", [review], 0.25)(table)
        table = _set("policy_term", [1], 50)(table)
        table = _set("age_at_entry", [1], 18)(table)
        table = _set("policy_term", [6], 5)(table)
        table = _set("age_at_entry", [6], 64)(table)
        table = _set("age_at_entry", [2], 50)(table)
        table = _set("policy_term", [7], 11)(table)
        table = _set("age_at_entry", [7], 64)(table)
        table = _set("joint_age", [7], 18)(table)
        table = _set("age_at_entry", [5], 18)(table)
        table = _set("policy_term", [5], 50)(table)
        return table

    model = _read_edited(tmp_path, edit)
    try:
        read = model.Data.model_point_table()
        assert read["duration_mth"].dtype == float
        df = _point(model, last).result_cf()
        assert len(df) == 1 and (df == 0.0).all().all()
        p = _point(model, window)
        assert p.duration_mth(0) == 66 and type(p.duration_mth(0)) is int
        late = _point(model, future)
        assert (late.t_entry(), late.proj_len(), late.pols_new_biz(120)) == (120, 420, 1.0)
        one = _point(model, first)
        assert (one.duration_mth_init(), one.proj_len()) == (1, 299)
        assert one.review_prem_factor(0) == 1.0 and one.ci_sel_factor(0) == 1.0
        on = _point(model, review)
        assert len(on.result_cf()) == on.proj_len() == 240
        assert on.premium_pp(0) == pytest.approx(55.0 * 1.25, rel=1e-12)
        assert on.ci_sel_factor(0) == 1.1 and on.review_shock_active(0)
        for label, premium in ((21, 55.0 * 0.75), (22, 0.0)):
            cut = _point(model, label)
            assert len(cut.result_cf()) == cut.proj_len() == 222, label
            assert cut.premium_pp(0) == premium and cut.premium_pp(42) == premium, label
            assert not any(cut.review_shock_active(t) for t in range(cut.proj_len())), label
        young, anniversary = _point(model, 23), _point(model, 24)
        assert len(young.result_cf()) == young.proj_len() == 289
        assert len(anniversary.result_cf()) == anniversary.proj_len() == 288
        assert young.idx_factor(0) == 1.0 and young.idx_factor(1) == pytest.approx(1.03)
        assert anniversary.idx_factor(0) == 1.03 and anniversary.idx_prem_factor(0) == 1.045
        zero = _point(model, 25)
        assert len(zero.result_cf()) == zero.proj_len() == 228
        assert {zero.ci_sel_factor(t) for t in range(228)} == {0.0}
        assert {zero.ci_rate(t, 1) for t in range(228)} == {0.0}
        for point, months in ((1, 600), (6, 60), (2, 300), (7, 132), (5, 600)):
            assert len(_point(model, point).result_cf()) == months, point
            assert _point(model, point).check_pols_roll_fwd(), point
    finally:
        model.close()


def _every_state_months(start, end):
    """The S months a point whose S frame runs from ``start`` to ``end`` is restated at.

    By default the edges of its windows (USLIB-SEC-PLAN.md §5.2, T5): every month of the
    first policy year and the first anniversary, through which ``Data``'s rule for a policy
    not yet in force ends, each anniversary and the month before it, which takes in every
    review and the month before it, each review's shock window's last month and the month
    after it, and the last month of the frame, before expiry.  With ``UKLIB_SEC_FULL=1``,
    every month.  Each after ``start``, the twin's month.
    """
    if SEC_FULL:
        return list(range(start + 1, end))
    months = {*range(1, 14), end - 1, *(m for a in range(12, end, 12) for m in (a - 1, a)),
              *(m for r in range(60, end, 60) for m in (r + 11, r + 12))}
    return sorted(m for m in months if start < m < end)


def _states(s):
    """Each ``(S point, month)`` of :func:`_every_state_months` on every point of ``s``."""
    labels = s.Data.model_point_table().index
    return [(point_id, d) for key, point_id in zip(point_keys(s), labels)
            for d in _every_state_months(0, projection(s, key).proj_len())]


def _restated(root, s, states):
    """The twins of ``s``'s points and a row in force at each of ``states``, ``(S point,
    month)``, built by the generator out of ``s`` into a copy of the product directory:
    ``(folder, table)``."""
    spec = dataclasses.replace(SPEC, derived=tuple(states), future=(), derived_refs={})
    table, _ = build_sec_table(spec, s)
    return _sec_inputs(root, table), table


def _states_apart(a, b):
    """The state columns, the count's among them, in which two tables of :func:`_restated`
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


def test_every_state_s_reaches_is_accepted_in_force(s_model, spliced, tmp_path):
    """Every state ``CI_UK_S`` reaches is a valid opening state (T5).

    ``Data``'s rules and ``proj_len()``'s hold an opening state to what a policy in force
    can be, so they must accept each state the S model reaches: a rule exercised only on
    the rows the other tests choose could refuse a state S reaches elsewhere (D6).  So each
    point of S is restated in force by the generator at the edges of its windows, or with
    ``UKLIB_SEC_FULL=1`` at every month of its frame (:func:`_every_state_months`), into
    one table beside the twins: ``Data`` reads it, and no row's ``proj_len()`` refuses it
    (USLIB-SEC-PLAN.md §5.2, T5, precised at M10).  The splice's review change moves five of
    the states S reaches: the count, through the shock lapse, the review factor, the select
    latch and its factor, and the last review's change.  It leaves alone the indexation
    factors, which the RPI alone moves.  The cap's table moves the count, to 0 once the
    cap binds.  Expense inflation moves no state, and the trend ships at 0 in each.  So
    the test runs on each set of inputs on which those states differ (precised at M9),
    and asserts which states each moves:

    * S as shipped, its seven points under its own References, as T1 and the committed rows
      read it (``s_model``);
    * the splice's, its points and four variants under :data:`SPLICED_REFS`, the review
      change on (``spliced``);
    * the cap's, its points under :data:`SPLICED_REFS` on :data:`CAPPED`'s table, whose
      count falls to exactly 0 once the cap binds, which neither other set reaches.

    ``CI_UK_SEC`` refuses no state ``CI_UK_S`` reaches, so none is set aside.
    """
    capped = _capped_s(tmp_path / "capped")
    try:
        sets = {"shipped": (s_model, {}), "spliced": (spliced[0], SPLICED_REFS),
                "capped": (capped, SPLICED_REFS)}
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
        capped.close()
    assert not found, found
    shipped, splice, cap = states["shipped"], states["spliced"], states["capped"]
    apart = _states_apart(shipped, splice)
    assert apart == {"policy_count", "review_prem_factor_init", "ci_sel_latched_init",
                     "ci_sel_factor_init", "review_prem_shock_init"}, apart
    count = cap["policy_count"]
    assert (count == 0.0).any() and (count > 0.0).any()


# ---------------------------------------------------------------------------
# The assumption tables
#
# Data checks each table before a value of it is read: the pivot table in its reader, as it
# reads the file, so that a fault is named by its line, and the lapse table in the cell the
# projection takes its extent from (UKLIB-SEC-PLAN.md §4; USLIB-SEC-PLAN.md §7.1,
# *Precised at M3*, item 9).  Each case is the shipped tables with one fault, read from a
# copy, refused by its Data cell alone, naming the file, the column and its lines, the
# header line 1, and through a projection of the anchor cell, which reads both tables.  The
# lines are the shipped files': ci_rate_table.csv holds M NS at the pivot ages 40 to 65 on
# lines 2 to 7, then M S, F NS and F S, six lines each; lapse_table.csv policy years 1 to 6
# on lines 2 to 7.


def _written(column, value, where):
    """An edit of a table that writes ``value`` into ``column`` on the rows ``where``
    picks."""
    def edit(table):
        cells = table[column].astype(object)
        cells[where(table)] = value
        return table.assign(**{column: cells})
    return edit


def _pivot(sex, smoker, age):
    return lambda t: (t["sex"] == sex) & (t["smoker"] == smoker) & (t["age"] == age)


def _group(sex, smoker):
    return lambda t: (t["sex"] == sex) & (t["smoker"] == smoker)


def _key_is(column, value):
    return lambda t: t[column] == value


def _dropped(where):
    return lambda table: table[~where(table)].reset_index(drop=True)


def _repeated(where):
    return lambda table: pd.concat([table, table[where(table)]], ignore_index=True)


LAPSE = "lapse_table.csv"
I_CI = f"{CI_RATES}: i_ci must be a number above 0 and at most 1; it is not on line "
Q_D = f"{CI_RATES}: q_d must be a number above 0 and at most 1; it is not on line "
LAPSE_RATE = f"{LAPSE}: lapse_rate must be a number from 0 to 1; it is not on line "
GROUPS = (f"{CI_RATES}: each sex and smoker status must hold two pivot ages or more, one "
          f"row an age; ")
YEARS = (f"{LAPSE}: the policy years must run from 1, one row a year, without a gap or a "
         f"repeat; ")

# A table a reader cannot read, or whose value is not a number in its range, as (case, the
# file, its edit, the Data cell that refuses it, its message).  A value no point reads is
# refused too: the female smoker at 65, which no committed point reaches.
UNREADABLE = [
    ("a blank diagnosis rate", CI_RATES,
     _written("i_ci", float("nan"), _pivot("M", "NS", 50)), "ci_rate_table", I_CI + "[4]"),
    ("a text mortality rate", CI_RATES, _written("q_d", "low", _pivot("F", "S", 65)),
     "ci_rate_table", Q_D + "[25]"),
    ("an infinite diagnosis rate", CI_RATES,
     _written("i_ci", float("inf"), _pivot("M", "S", 40)), "ci_rate_table", I_CI + "[8]"),
    ("a diagnosis rate of 0", CI_RATES, _written("i_ci", 0.0, _pivot("F", "NS", 45)),
     "ci_rate_table", I_CI + "[15]"),
    ("a negative mortality rate", CI_RATES, _written("q_d", -0.001, _pivot("M", "NS", 60)),
     "ci_rate_table", Q_D + "[6]"),
    ("a diagnosis rate past 1", CI_RATES, _written("i_ci", 1.5, _pivot("F", "S", 60)),
     "ci_rate_table", I_CI + "[24]"),
    ("two lines at fault", CI_RATES, _then(
        _written("i_ci", float("nan"), _pivot("M", "NS", 40)),
        _written("i_ci", float("nan"), _pivot("F", "S", 40))),
     "ci_rate_table", I_CI + "[2, 20]"),
    ("an age not whole", CI_RATES, _written("age", 45.5, _pivot("M", "NS", 45)),
     "ci_rate_table", f"{CI_RATES}: age must be a whole number; it is not on line [3]"),
    ("an age written as text", CI_RATES, _written("age", "x", _pivot("F", "NS", 40)),
     "ci_rate_table", f"{CI_RATES}: age must be a whole number; it is not on line [14]"),
    ("an unknown sex", CI_RATES, _written("sex", "X", _pivot("F", "S", 40)),
     "ci_rate_table",
     f"{CI_RATES}: sex must be M or F, and smoker NS or S; they are not on line [20]"),
    ("term assurance's smoker code", CI_RATES, _written("smoker", "N", _pivot("M", "S", 45)),
     "ci_rate_table",
     f"{CI_RATES}: sex must be M or F, and smoker NS or S; they are not on line [9]"),
    ("an age twice", CI_RATES, _repeated(_pivot("F", "S", 40)), "ci_rate_table",
     GROUPS + "sex F, smoker S, age 40 repeats on lines [20, 26]"),
    ("a group missing", CI_RATES, _dropped(_group("M", "S")), "ci_rate_table",
     GROUPS + "sex M, smoker S holds 0 pivot ages"),
    ("a group of one pivot", CI_RATES,
     _dropped(lambda t: _group("F", "NS")(t) & (t["age"] != 50)), "ci_rate_table",
     GROUPS + "sex F, smoker NS holds 1 pivot age"),
    ("a blank lapse rate", LAPSE, _written("lapse_rate", float("nan"),
                                           _key_is("policy_year", 3)),
     "lapse_last_year", LAPSE_RATE + "[4]"),
    ("a lapse rate past 1", LAPSE, _written("lapse_rate", 1.5, _key_is("policy_year", 6)),
     "lapse_last_year", LAPSE_RATE + "[7]"),
    ("a negative lapse rate", LAPSE, _written("lapse_rate", -0.1, _key_is("policy_year", 1)),
     "lapse_last_year", LAPSE_RATE + "[2]"),
    ("a text lapse rate", LAPSE, _written("lapse_rate", "high", _key_is("policy_year", 2)),
     "lapse_last_year", LAPSE_RATE + "[3]"),
    ("a policy year not whole", LAPSE, _written("policy_year", 2.5,
                                                _key_is("policy_year", 2)),
     "lapse_last_year",
     f"{LAPSE}: policy_year must be a whole number; it is not on line [3]"),
    ("a policy year missing", LAPSE, _dropped(_key_is("policy_year", 3)), "lapse_last_year",
     YEARS + "no line holds policy_year 3"),
    ("a policy year twice", LAPSE, _repeated(_key_is("policy_year", 4)), "lapse_last_year",
     YEARS + "policy_year 4 repeats on lines [5, 8]"),
    ("no policy year 1", LAPSE, _dropped(_key_is("policy_year", 1)), "lapse_last_year",
     YEARS + "no line holds policy_year 1"),
]


@pytest.mark.parametrize("case, file, edit, cell, message", UNREADABLE,
                         ids=[c[0] for c in UNREADABLE])
def test_a_table_a_reader_cannot_read_is_refused_naming_its_lines(tmp_path, case, file, edit,
                                                                  cell, message):
    """``Data`` refuses an assumption table before a value of it is read (§4, T5).

    ``CI_UK_S`` reads a blank rate as NaN, which its caps would keep and every flow carry;
    an infinite one, which a cap reads as a certain claim; a rate of 0, at which
    ``pivot_interp``'s ratio divides by zero; a negative one, whose power has no real value;
    a key that is not whole as one ``int`` truncates; and a group short of two pivots as an
    ``IndexError``, only where a projection reaches it.  Here the cell the projection asks
    first refuses each, naming the file, the column and its lines (:data:`UNREADABLE`), and
    so does a projection of the anchor cell, which reads both tables.
    """
    model = _read_edited(tmp_path, lambda t: t, edits={file: edit})
    try:
        _refused(model.Data.cells[cell], message)
        _refused(_point(model, 1).result_cf, message)
    finally:
        model.close()


def test_a_key_written_as_a_float_reads_as_ci_uk_s_reads_it(sec_model, tmp_path):
    """A key written ``40.0`` is the key 40, in every table and in every extent.

    ``CI_UK_S``'s lookups match a float key to the int the projection asks, so a table
    written by a tool that writes every number with a decimal point reads the same.  Each
    assumption table's keys and the model point table's ``duration_mth`` are written as
    floats, and every committed point projects what the committed tables project, exactly.
    """
    def as_float(column):
        return lambda table: table.assign(**{column: table[column].astype(float)})

    edits = {CI_RATES: as_float("age"), LAPSE: as_float("policy_year")}
    model = _read_edited(tmp_path, as_float("duration_mth"), edits=edits)
    try:
        for point_id in _committed().index:
            for report in ("result_cf", "result_pols"):
                assert frame_mismatches(_point(sec_model, point_id).cells[report](),
                                        _point(model, point_id).cells[report](),
                                        rtol=0, atol=0) == [], (point_id, report)
    finally:
        model.close()


# ---------------------------------------------------------------------------
# T6 -- regeneration


def test_the_committed_sec_inputs_are_what_s_generates():
    """``model_point_table_sec.csv`` is what CI_UK_S and its table generate today.

    Every row and column, the text cells and the six opening-state columns included: an
    edit to an S row the table copies or derives from, or to an S formula a row's state is
    read from, fails here until ``python tools/gen_sec_points.py CI_UK_SEC`` regenerates
    it, in the same commit.  Text and integers compare exactly, and a float by its value, to
    1e-12, because the text the writer picks for a computed float depends on the platform's
    parser (§5).  The generator reads S itself: the row of the spec's ``derived_refs`` is
    read with a review change set on S, which drops what an S model given to it had
    cached, and ``s_model``'s sweep is what the tests after this one compare.
    """
    assert check_generated(SEC) == []


# ---------------------------------------------------------------------------
# The product's own facts


def test_the_two_clocks_on_the_shipped_points(sec_model):
    """``t`` counts from the valuation date; ``duration_mth(t)`` from issue (D3, D4).

    On a twin of S's new business the two coincide, and its policies enter as new business
    at ``t = 0``.  The reviewable point valued on its first review, in force 60 months, is in
    policy year 6 at attained age 45 at ``t = 0``, has 240 months of cover left, and is on
    the books from ``t = 0`` with no new business; its next review falls at ``t = 60``,
    policy month 120.  The indexed point valued on its third anniversary steps its factors
    at ``t = 12``.  The point issued 13 months on has nothing in force and nothing to do
    before ``t = 13``, and a frame of 313 months; its index steps at ``t = 25``.  The point
    in its last covered month has a one-month frame, in which its survivors expire.  A
    timing the model does not know is refused rather than answered with another count.
    """
    twin = _row(sec_model, "twin", 1, 0)
    assert [twin.duration_mth(t) for t in (0, 1, 299)] == [0, 1, 299]
    assert (twin.t_entry(), twin.pols_if_init(), twin.pols_new_biz(0), twin.pols_if(0)) == (
        0, 0.0, 1.0, 1.0)
    assert (twin.expiry_mth(), twin.proj_len()) == (300, 300)
    old = _row(sec_model, "derived", 3, 60)
    assert (old.duration_mth(0), old.duration(0), old.policy_year(0), old.age(0, 1)) == (
        60, 5, 6, 45)
    assert (old.proj_len(), old.t_entry(), old.pols_new_biz(0)) == (240, 0, 0.0)
    assert old.is_active(239) and not old.is_active(240)
    assert old.pols_if(0) == old.pols_if_init() == old.policy_count()
    assert (old.reviews_passed(0), old.reviews_passed(59), old.reviews_passed(60)) == (
        1, 1, 2)
    idx = _row(sec_model, "derived", 4, 36)
    assert idx.idx_factor(11) == idx.idx_factor_init() == pytest.approx(1.03 ** 3, rel=1e-12)
    assert idx.idx_factor(12) == pytest.approx(idx.idx_factor_init() * 1.03, rel=1e-12)
    fut = _row(sec_model, "future", 4, -13)
    assert (fut.duration_mth(0), fut.t_entry(), fut.proj_len()) == (-13, 13, 313)
    assert not fut.is_active(12) and fut.is_active(13)
    assert (fut.pols_if_init(), fut.pols_new_biz(13), fut.pols_if(13)) == (0.0, 1.0, 1.0)
    assert fut.idx_factor(24) == 1.0 and fut.idx_factor(25) == pytest.approx(1.03, rel=1e-12)
    last = _row(sec_model, "derived", 1, 299)
    assert (last.proj_len(), last.age(0, 1), last.policy_year(0)) == (1, 64, 25)
    assert last.pols_maturity(0) > 0.0 and last.pols_if_at(1, _code(last, "BEF_NB")) == 0.0
    _refused(lambda: old.pols_if_at(0, "BEF_NOTHING"), "invalid timing")


def test_the_committed_rows_continue_their_s_points(sec_model, s_model):
    """Each committed row in force, or issued later, is its S point from its month on.

    T6 compares a float to 1e-12, which pins a small count only to that much of itself, so
    each committed row is compared with its S point frame by frame and cell by cell, at the
    shipped assumptions (USLIB-SEC-PLAN.md §7.1, *Precised at M3*, item 11): the five
    derived rows from their months, and the row issued 13 months on from S's issue month,
    all to 1e-9 relative with no absolute floor but on the residual, every cell but those
    expense inflation moves (:func:`_continues_s`), which the inflation test holds.  The
    row read from S under a review change of its own is S's under that change, which the
    test after this one compares.
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

    Each cell with a ``t`` parameter is called at each of ``months`` with every life the
    point has, every timing of S's and every kind the cell takes, and no report and no
    check is called: so what S caches from the first of ``months`` on is those months and
    the months their recursions and look-aheads read, and a comparison that reads S's cache,
    :func:`uk_sec_support.twin_mismatches`, compares those months alone.
    """
    domains = {"life": (1, 2) if proj.is_joint() else (1,),
               "timing": ("BEF_DECR", "BEF_LAPSE", "AFT_DECR")}
    kinds = {"benefit_pp": BENEFITS, "claims": (*KINDS, None)}
    for name, cells in proj.cells.items():
        params = list(cells.parameters)
        if "t" not in params:
            continue
        options = [months if param == "t" else kinds[name] if param == "kind"
                   else domains[param] for param in params]
        for args in itertools.product(*options):
            cells(*args)


def test_the_committed_row_with_review_history_is_s_under_its_review_change(sec_model):
    """The row read from S under a review change of its own is S's under that change to its
    next review, and today's References' after it (§6.2, K14).

    At the shipped review change of 0 no S point has a shock month, a closed latch or a
    review factor other than 1, so the spec reads one row from S under a change of 10%,
    which its ``derived_refs`` records (:data:`UNDER_REFS`): the reviewable point at S
    month 124, inside the window its second review opened at policy month 120, its latch
    closed at its first, its review factor 1.1 squared, and its count what S under 10%
    carries in.  At the shipped References the committed model projects S under 10% from
    there to the next review, at ``t = 56``, policy month 180: every cell S evaluates in
    those months, and both reports' rows, to 1e-9 relative with no absolute floor but on
    the residual, but those expense inflation moves (:func:`_continues_s`).  The history
    is history.  From that review on today's change of 0 applies: the premium stays at its
    factor, where S's rises by 10%, and no window opens.  And with 10% set in both models
    the row is S's in every month of its frame.  Each Reference is set on a model just read
    (K7).
    """
    assert UNDER_REFS == {("CI-000003", 124): {"review_prem_shock": 0.10}}
    rho, d = 0.10, 124
    row = _row(sec_model, "derived", 3, d)
    assert (row.ci_sel_latched_init(), row.ci_sel_factor_init()) == (1, 1.1)
    assert row.review_prem_factor_init() == pytest.approx((1 + rho) ** 2, rel=1e-15)
    assert (row.review_prem_shock_init(), row.reviews_passed(0)) == (rho, 2)
    assert row.review_shock_active(7) and not row.review_shock_active(8)
    after = 180 - d
    s = mx.read_model(model_path(TWIN), name=_name("under"))
    try:
        s.Projection.review_prem_shock = rho
        sp = _point(s, 3)
        _window_sweep(sp, range(d, 180))
        assert max(sp.premium_pp.keys()) == 179 and set(range(d, 180)) <= set(
            sp.premium_pp.keys())
        exempt = SPLICE_EXEMPT | INFLATION_CELLS
        found = twin_mismatches(sp, row, t_offset=d, exempt=exempt | RESIDUALS, atol=0.0,
                                codes=codes(row))
        others = exempt | (set(sp.cells) - RESIDUALS)
        found += twin_mismatches(sp, row, t_offset=d, exempt=others, codes=codes(row))
        keep = [c for c in sp.result_cf().columns if c not in INFLATED]
        for report, columns in (("result_cf", keep), ("result_pols", None)):
            found += [f"{report}: {line}" for line in frame_mismatches(
                sp.cells[report]().loc[d:179], row.cells[report]().loc[:after - 1],
                t_offset=d, columns=columns, atol=0.0)]
        assert not found, found[:20]
        assert row.premium_pp(after) == row.premium_pp(after - 1) == pytest.approx(
            55.0 * (1 + rho) ** 2, rel=1e-12)
        assert sp.premium_pp(180) == pytest.approx(sp.premium_pp(179) * (1 + rho),
                                                   rel=1e-12)
        assert sp.review_shock_active(180) and not row.review_shock_active(after)
    finally:
        s.close()
    sec = mx.read_model(model_path(SEC), name=_name("under_sec"))
    s = mx.read_model(model_path(TWIN), name=_name("under_s"))
    try:
        for model in (sec, s):
            model.Projection.review_prem_shock = rho
        sp = _point(s, 3)
        _sweep_s(sp)
        assert _continues_s(sp, _row(sec, "derived", 3, d), d) == []
    finally:
        sec.close()
        s.close()


def test_the_indexation_history_is_read_from_the_model_point(sec_model, tmp_path):
    """The RPI increases already given are the point's, not recomputed (UKLIB-SEC-PLAN.md
    K14).

    ``CI_UK_S`` recomputes the factors from a flat ``rpi_rate``, so a model that dropped
    the two columns and did the same would pass the splice, since S and the splice
    recompute them alike.  So the indexed point on its third anniversary is projected with
    factors no flat rate gives, the increases of an RPI past the 10% cap in two years and
    below 0 in the third: cover 1.21, two increases of 10% and none, and premium 1.3225, two
    of 15%, the premium cap, and none.  Its cover is the sum assured at issue times 1.21
    through the year under way, and times 1.03 for each anniversary after; its premium the
    issue premium times 1.3225, and times 1.045 for each; and the additional payment and
    children's cover take their caps on the indexed cover.
    """
    row = _label(_committed(), "derived", 4, 36)
    model = _read_edited(tmp_path, _then(_set("idx_factor_init", [row], 1.21),
                                         _set("idx_prem_factor_init", [row], 1.3225)))
    try:
        p = _point(model, row)
        main, ap, child = (_code(p, kind) for kind in BENEFITS)
        for t, years in ((0, 0), (11, 0), (12, 1), (30, 2), (263, 21)):
            cover = 100000.0 * 1.21 * 1.03 ** years
            assert p.benefit_pp(t, main) == pytest.approx(cover, rel=1e-12), t
            assert p.premium_pp(t) == pytest.approx(55.0 * 1.3225 * 1.045 ** years,
                                                    rel=1e-12), t
            assert p.benefit_pp(t, ap) == min(0.25 * p.benefit_pp(t, main), 25000.0), t
            assert p.benefit_pp(t, child) == min(0.5 * p.benefit_pp(t, main), 25000.0), t
        q = _point(sec_model, row)
        assert q.premium_pp(0) == pytest.approx(55.0 * 1.045 ** 3, rel=1e-12)
    finally:
        model.close()


def test_the_review_history_is_read_from_the_model_point(sec_model, tmp_path):
    """The premium changes the reviews already made are the point's (UKLIB-SEC-PLAN.md
    K14).

    ``CI_UK_S`` recomputes the premium at each review from one flat ``review_prem_shock``,
    so a model that dropped the column and did the same would pass the splice.  So the
    reviewable point valued on its first review is projected with the history of a first
    review that raised its premium by 30%, a review factor of 1.30 and a change of 30%,
    which no review the shipped ``review_prem_shock`` of 0 makes: its premium is the issue
    premium times 1.30 until its next review, at ``t = 60``, policy month 120, and then
    times ``1 + review_prem_shock`` for each review after, 1 at the shipped 0 and 1.1 under
    10%; the same point valued mid-year after the review carries the factor too.  And the
    twin of the same point, issued at the valuation date, has no history and reviews at
    policy month 60 at the Reference.
    """
    on, after = (_label(_committed(), "derived", 3, d) for d in (60, 78))
    edit = _then(_set("review_prem_factor_init", [on, after], 1.30),
                 _set("review_prem_shock_init", [on, after], 0.30))
    for rho, step in ((0.0, 1.0), (0.10, 1.1)):
        model = _read_edited(tmp_path / f"rho{rho}", edit)
        try:
            model.Projection.review_prem_shock = rho
            p, q = _point(model, on), _point(model, after)
            for t, reviews in ((0, 0), (59, 0), (60, 1), (119, 1), (120, 2), (239, 3)):
                assert p.premium_pp(t) == pytest.approx(55.0 * 1.30 * step ** reviews,
                                                        rel=1e-12), (rho, t)
            assert q.premium_pp(0) == pytest.approx(55.0 * 1.30, rel=1e-12)
            assert q.premium_pp(42) == pytest.approx(55.0 * 1.30 * step, rel=1e-12)
            twin = _row(model, "twin", 3, 0)
            assert twin.premium_pp(59) == 55.0
            assert twin.premium_pp(60) == pytest.approx(55.0 * step, rel=1e-12)
        finally:
            model.close()
    assert _point(sec_model, on).premium_pp(0) == 55.0


def test_the_select_latch_is_read_from_the_model_point(tmp_path):
    """A latch closed before the valuation date is the point's, and stays (K14).

    ``CI_UK_S`` closes the latch at the first review whose ``review_prem_shock`` passes the
    shock threshold, and recomputes it from that one Reference.  So two reviewable rows are
    projected with a latch the References would not give.  Valued inside the first review's
    window, after a review that raised the premium by 20% and closed the latch at a loading
    of 10%, under the shipped change of 0, which closes no latch, the diagnosis rate carries
    10% from ``t = 0`` to the end of the frame, and the reviews after the valuation date
    leave the factor as it is.  Valued after the window, the latch open, under a change of
    20%, which would have closed it at the first review, the rate is the table's until the
    next review, at ``t = 42``, policy month 120, which closes it at
    ``1 + sel_lapse_ci_loading``.
    """
    inside, after = (_label(_committed(), "derived", 3, d) for d in (66, 78))
    model = _read_edited(tmp_path / "latched", _then(
        _reviewed([inside], 1.2, 0.2), _set("ci_sel_latched_init", [inside], 1),
        _set("ci_sel_factor_init", [inside], 1.1)))
    try:
        p = _point(model, inside)
        for t in (0, 5, 53, 54, 233):
            assert p.ci_sel_factor(t) == 1.1, t
            assert p.ci_rate(t, 1) == pytest.approx(1.1 * p.ci_rate_base(t, 1), rel=1e-12)
    finally:
        model.close()
    model = mx.read_model(model_path(SEC), name=_name("unlatched"))
    try:
        model.Projection.review_prem_shock = 0.20
        q = _point(model, after)
        assert (q.ci_sel_latched_init(), q.ci_sel_factor_init()) == (0, 1.0)
        assert [q.ci_sel_factor(t) for t in (0, 41)] == [1.0, 1.0]
        assert [q.ci_sel_factor(t) for t in (42, 221)] == [1.1, 1.1]
        assert q.ci_rate(41, 1) == q.ci_rate_base(41, 1)
    finally:
        model.close()


def test_the_latch_is_read_from_its_flag_and_not_its_factor(tmp_path):
    """A latch closed at a factor of 1, or below, stays closed (K14).

    A latch closes at the loading of its day, which may have been 0, or less, so the factor
    cannot say whether it has closed, and the flag ``ci_sel_latched_init`` does.  The
    reviewable point valued after its first review's window, which raised the premium by
    20%, is projected three times under a change of 20% and today's loading of 10%: with
    its latch closed at a loading of 0, a factor of 1, which the next shock review, at
    ``t = 42``, policy month 120, leaves at 1; closed at a loading of -5%, which it leaves
    at 0.95; and open, which it closes at 1.1.  A latch read off its factor, closed only
    where the factor is not 1, or only where it is above 1, would close the first or the
    second again at today's loading.  The rows are copies of the committed one under labels
    of their own, 21 and 22.
    """
    after = _label(_committed(), "derived", 3, 78)
    history = {"review_prem_factor_init": 1.2, "review_prem_shock_init": 0.2}
    latches = {21: (1, 1.0), 22: (1, 0.95), after: (0, 1.0)}

    def edit(table):
        rows = [table.drop(index=after)]
        for label, (latched, factor) in latches.items():
            row = table.loc[[after]].assign(
                policy_id=f"CI-9000{label}", ci_sel_latched_init=latched,
                ci_sel_factor_init=factor, **history)
            row.index = pd.Index([label], name="point_id")
            rows.append(row)
        return pd.concat(rows)

    model = _read_edited(tmp_path, edit)
    try:
        model.Projection.review_prem_shock = 0.20
        for label, (latched, factor) in latches.items():
            p = _point(model, label)
            assert (p.ci_sel_latched_init(), p.ci_sel_factor_init()) == (latched, factor)
            assert p.review_shock_active(42) and p.reviews_passed(42) == 2, label
            want = [factor] * 2 + ([factor] * 3 if latched else [1.1] * 3)
            assert [p.ci_sel_factor(t) for t in (0, 41, 42, 100, 221)] == want, label
            assert p.ci_rate(42, 1) == pytest.approx(want[2] * p.ci_rate_base(42, 1),
                                                     rel=1e-12), label
            assert len(p.result_cf()) == p.proj_len() == 222, label
    finally:
        model.close()


def test_the_last_review_change_sets_its_window_alone(tmp_path):
    """The change the last review made is read in its window, and nowhere else (K14).

    The shock lapse in the twelve months after a review reads the change that review made.
    A review before the valuation date made the change ``review_prem_shock_init`` carries,
    history, where ``CI_UK_S`` reads today's ``review_prem_shock`` at every review.  So the
    reviewable point valued inside its first review's window is projected with the history
    of a first review that raised the premium by 20%, under the shipped change of 0: the
    window's remaining six months lapse at ``min(0.30, w + 2 (0.20 - 0.05))``, the cap, and
    from ``t = 6``, policy month 72, at the table's rate; the review after the valuation
    date, at ``t = 54``, made no change, and opens no window.  Valued after its second
    review's window, at policy month 138, where two reviews give a factor any changes can,
    the change the second made moves nothing at all: at 50% the frame is, to the bit, the
    one a change of 0 gives.  Those two rows are copies of the committed row after the first
    window, under labels of their own, 21 and 22.
    """
    inside, after = (_label(_committed(), "derived", 3, d) for d in (66, 78))
    late = {21: 0.5, 22: 0.0}

    def edit(table):
        table = _then(_set("review_prem_factor_init", [inside], 1.2),
                      _set("review_prem_shock_init", [inside], 0.20))(table)
        rows = [table]
        for label, change in late.items():
            row = table.loc[[after]].assign(policy_id=f"CI-9000{label}", duration_mth=138,
                                            review_prem_shock_init=change)
            row.index = pd.Index([label], name="point_id")
            rows.append(row)
        return pd.concat(rows)

    model = _read_edited(tmp_path, edit)
    try:
        p = _point(model, inside)
        base = p.lapse_rate_base(0)
        for t in range(6):
            assert p.review_shock_active(t) and p.review_prem_change(t) == 0.20, t
            assert p.lapse_rate(t) == min(0.30, base + 2.0 * (0.20 - 0.05)), t
        for t in (6, 53, 54, 65, 233):
            assert not p.review_shock_active(t), t
            assert p.lapse_rate(t) == p.lapse_rate_base(t), t
        assert p.review_prem_change(54) == 0.0
        q, r = _point(model, 21), _point(model, 22)
        assert (q.reviews_passed(0), q.review_prem_shock_init()) == (2, 0.5)
        assert not any(q.review_shock_active(t) for t in range(q.proj_len()))
        assert frame_mismatches(r.result_cf(), q.result_cf(), rtol=0, atol=0) == []
        assert frame_mismatches(r.result_pols(), q.result_pols(), rtol=0, atol=0) == []
    finally:
        model.close()


def test_a_review_change_set_at_the_valuation_date_reaches_back_over_no_review(sec_model):
    """A ``review_prem_shock`` set at the valuation date applies to the reviews after it
    alone (K14; D6).

    The reviews already made, and their windows and latch, are history.  So with the change
    raised from 0 to 20% at the valuation date, the reviewable point valued on its first
    review keeps that review's premium, makes no shock lapse in its window and closes no
    latch, until its next review at ``t = 60``, policy month 120, where the premium rises by
    20%, the window opens and the latch closes; the rows inside and after the first window
    likewise, each to its own next review; and the twin issued at the valuation date, which
    has made no review, reviews at policy month 60 at the new change.
    """
    model = mx.read_model(model_path(SEC), name=_name("raised"))
    try:
        model.Projection.review_prem_shock = 0.20
        for d, next_review in ((60, 60), (66, 54), (78, 42)):
            p, before = _row(model, "derived", 3, d), _row(sec_model, "derived", 3, d)
            for t in range(next_review):
                assert p.premium_pp(t) == before.premium_pp(t), (d, t)
                assert p.lapse_rate(t) == before.lapse_rate(t), (d, t)
                assert p.ci_sel_factor(t) == 1.0, (d, t)
            assert p.premium_pp(next_review) == pytest.approx(55.0 * 1.2, rel=1e-12)
            assert p.review_shock_active(next_review) and p.ci_sel_factor(next_review) == 1.1
        twin = _row(model, "twin", 3, 0)
        assert twin.premium_pp(59) == 55.0
        assert twin.premium_pp(60) == pytest.approx(66.0, rel=1e-12)
        assert twin.review_shock_active(60) and twin.ci_sel_factor(60) == 1.1
    finally:
        model.close()


def test_expense_inflation_runs_on_the_valuation_clock(sec_model, s_model):
    """Maintenance is in valuation-date pounds, for every point alike (D7).

    At the shipped 3%, the factor at ``t`` is ``1.03^(t // 12)`` on every point, whatever
    its duration, stepping on the valuation date's anniversaries.  So the reviewable point
    valued on its first review, in force 60 months, pays S's month-``60 + t`` expenses
    deflated by ``1.03^5``, the inflation S had already applied since issue, and the point
    issued 13 months on pays S's maintenance a year of inflation earlier than S's issue
    month would: its factor at ``t`` is ``1.03^(t // 12)``, where S's at ``t - 13`` is
    ``1.03^((t - 13) // 12)``.  The initial expense is not inflated on either.  This is the
    only test that sees inflation run on the policy clock: the splice sets the rate to 0,
    and on a point issued at ``t = 0`` the clocks agree.
    """
    assert sec_model.Projection.inflation_rate == INFLATION
    p, s = _row(sec_model, "derived", 3, 60), _point(s_model, 3)
    fut = _row(sec_model, "future", 4, -13)
    for t in (0, 11, 12, 30):
        assert p.inflation_factor(t) == fut.inflation_factor(t) == (1 + INFLATION) ** (t // 12)
    for t in range(p.proj_len()):
        assert p.expenses(t) == pytest.approx(
            s.expenses(60 + t) / (1 + INFLATION) ** 5, rel=1e-12), t
    s4 = _point(s_model, 4)
    acq = s4.expense_acq
    for t in range(13, fut.proj_len()):
        issued = acq if t == 13 else 0.0
        maint = (fut.expenses(t) - issued) / fut.pols_if(t)
        want = (s4.expenses(t - 13) - issued) / s4.pols_if(t - 13)
        assert maint == pytest.approx(
            want * (1 + INFLATION) ** (t // 12 - (t - 13) // 12), rel=1e-12), t


def test_the_ci_trend_runs_on_the_valuation_clock(tmp_path):
    """The morbidity trend steps on the valuation date's anniversaries, for every point (D7).

    With the trend switched on at :data:`TREND`, the factor at ``t`` is ``1.02^(t // 12)``
    on every point, whatever its duration: 1 through the first valuation year, whether the
    policy is new, in force 36 or 60 months, or to be issued 13 months on.  The diagnosis
    rate it multiplies is the table's at the point's attained age, the basis at the
    valuation date, and the mortality rate it leaves alone.  So the indexed point valued on
    its third anniversary diagnoses at S's table rate at month ``36 + t`` times
    ``1.02^(t // 12)``, where ``CI_UK_S`` would trend it from issue,
    ``1.02^((36 + t) // 12)``.  This is the only test that sees the trend run on the policy
    clock: the splice keeps it at 0, where the clocks agree.  The References are set on a
    model just read (K7).
    """
    model = mx.read_model(_sec_inputs(tmp_path, _committed()), name=_name("trend"))
    try:
        model.Projection.ci_trend = TREND
        rows = [_row(model, *case) for case in (("twin", 1, 0), ("derived", 4, 36),
                                                 ("derived", 3, 60), ("future", 4, -13))]
        for t in (0, 11, 12, 30, 200):
            assert {p.ci_trend_factor(t) for p in rows} == {(1 + TREND) ** (t // 12)}, t
        p = rows[1]
        for t in (0, 11, 12, 30, 263):
            factor = (1 + TREND) ** (t // 12)
            assert p.ci_rate(t, 1) == pytest.approx(p.ci_rate_base(t, 1) * factor,
                                                    rel=1e-12), t
            assert p.ci_rate_base(t, 1) == p.pivot_interp(43 + t // 12, "M", "NS", "i_ci")
            assert p.mort_rate(t, 1) == p.pivot_interp(43 + t // 12, "M", "NS", "q_d")
        assert rows[3].ci_rate(13, 1) == rows[3].ci_rate_base(13, 1) * (1 + TREND)
    finally:
        model.close()


def test_every_twin_is_s_with_the_trend_and_the_review_change_on():
    """On new business, each twin is S's in every cell with tau and rho on in both models.

    T1 compares the twins at the shipped References, where the trend and the review change
    are 0, and the splice holds the trend at 0 by design (D7), so a cell that dropped the
    trend, the standalone paid rate among them, would pass both.  On a point issued at
    ``t = 0`` the two clocks coincide, and the trend, which runs on the valuation clock here
    and from issue in ``CI_UK_S``, is the same factor in every month.  So with the trend at
    :data:`TREND` and the review change at the splice's 12% set in both models, each twin of
    S's seven points, its reviews moving premiums, opening windows and closing the latch, is
    S's in every cell S evaluates in its sweep and in both reports, to 1e-9 relative with no
    absolute floor but on the residual (:func:`_compare`).  The References are set on models
    just read (K7).
    """
    refs = {"ci_trend": TREND, "review_prem_shock": SPLICED_REFS["review_prem_shock"]}
    sec = mx.read_model(model_path(SEC), name=_name("tau_rho"))
    s = mx.read_model(model_path(TWIN), name=_name("tau_rho_s"))
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
        twin = _row(sec, "twin", 3, 0)
        assert twin.ci_trend_factor(12) == 1.0 + TREND and twin.ci_sel_factor(60) == 1.1
        assert _row(sec, "twin", 2, 0).claim_rate_paid(12) == pytest.approx(
            _point(s, 2).claim_rate_paid(12), rel=1e-15)
    finally:
        sec.close()
        s.close()


# The review changes the splice's 12% does not reach, as (the change, whether the reviews
# open a shock window and close the latch, whether the window's lapse takes the cap): 20%,
# whose shock lapse, w + 2 (0.20 - 0.05) = 0.34 in the window of every review, policy year 6
# on, passes the cap of 0.30, so that min(review_lapse_cap, shock) takes the cap, before the
# valuation date and after it; the threshold itself, 5%, where neither the window opens nor
# the latch closes, each asking for a change above it, though the premium still rises by
# it; and the float above the threshold, where both do.
REVIEW_EDGES = {
    "past the lapse cap": (0.20, True, True),
    "at the threshold": (0.05, False, False),
    "one float above the threshold": (math.nextafter(0.05, 1.0), True, False),
}
# The reviewable point restated on its first review, inside its window, and on its second.
REVIEW_EDGE_MTHS = (60, 66, 120)


@pytest.mark.parametrize("case", list(REVIEW_EDGES))
def test_a_review_change_at_an_edge_continues_the_s_projection(tmp_path, case):
    """T2 at review changes the splice's does not reach: past the cap, at the threshold.

    The splice's change of 12% shocks the lapse by 0.14, so its window never reaches the
    cap, and is far from the threshold, so neither comparison with it is pinned: a window
    or a latch that asked for a change at the threshold, rather than above it, would pass.
    So S's table is restated by the generator under each change of :data:`REVIEW_EDGES`,
    set in S and SEC alike with the splice's inflation and trend of 0, the reviewable point
    at each of :data:`REVIEW_EDGE_MTHS`, and each row, and the point's twin, is S's from
    its month on in every cell (:func:`_compare`): the windows, the latch and the lapse
    among them.  Then what the change reaches: past the cap, the window's lapse is the
    cap, 0.30, in the window of the review made at the valuation date and of the next; at
    the threshold no window opens, no latch closes, and the premium rises by 5% at each
    review all the same; one float above, every review opens its window and the first
    closes the latch.
    """
    rho, shocks, capped = REVIEW_EDGES[case]
    refs = {**SPLICED_REFS, "review_prem_shock": rho}
    s = mx.read_model(model_path(TWIN), name=_name("edge_s"))
    sec = None
    try:
        for ref, value in refs.items():
            setattr(s.Projection, ref, value)
        spec = dataclasses.replace(SPEC, derived=tuple((3, d) for d in REVIEW_EDGE_MTHS),
                                   future=(), derived_refs={})
        table, _ = build_sec_table(spec, s)
        sec = mx.read_model(_sec_inputs(tmp_path, table), name=_name("edge"))
        for ref, value in refs.items():
            setattr(sec.Projection, ref, value)
        s_proj = _point(s, 3)
        _sweep_s(s_proj)
        found = [f"twin: {line}" for line in _compare(
            s_proj, _row(sec, "twin", 3, 0), 0, TWIN_EXEMPT_DEFAULT | SPEC.exempt)]
        for d in REVIEW_EDGE_MTHS:
            found += [f"d{d}: {line}" for line in _compare(
                s_proj, _row(sec, "derived", 3, d), d, SPLICE_EXEMPT)]
        assert not found, found[:20]
        p = _row(sec, "derived", 3, 60)
        frame = range(p.proj_len())
        assert p.ci_sel_latched_init() == int(shocks)
        assert [p.review_shock_active(t) for t in (0, 11, 12, 60, 71, 72)] == [
            shocks, shocks, False, shocks, shocks, False]
        assert {p.ci_sel_factor(t) for t in frame} == {1.1 if shocks else 1.0}
        assert p.premium_pp(60) == pytest.approx(55.0 * (1.0 + rho) ** 2, rel=1e-12)
        if capped:
            for t in (*range(12), *range(60, 72)):
                assert p.lapse_rate(t) == s_proj.lapse_rate(60 + t) == 0.30, t
        else:
            assert all(p.lapse_rate(t) < 0.30 for t in frame)
    finally:
        if sec is not None:
            sec.close()
        s.close()


def test_the_initial_expense_is_charged_on_new_business_only(sec_model):
    """£200 per policy issued, in the issue month alone.

    On every committed point, what ``expenses(t)`` holds beyond its maintenance part is
    ``200 * policy_count()`` in the issue month, ``t = -duration_mth``, and 0 in every other
    month, to 1e-9: the twins of S's new business bear it at ``t = 0``, the point issued 13
    months on at ``t = 13``, and the points already in force never, though on the valuation
    clock their row 0 is ``t = 0``, as S's restated rows did not.  ``CI_UK_S`` charges it at
    ``t = 0`` on the count in force there, which on a point issued at the valuation date is
    the issued count, so the twins agree with S at any count.
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


def test_the_reviews_and_their_window_run_on_the_policy_clock(sec_model, tmp_path):
    """Reviews fall every 60 policy months, and their windows last 12, on the policy clock.

    ``CI_UK_S`` counts reviews and the window on ``t``, which are the policy's months only on
    a point issued at ``t = 0``.  With the review change at 10%, past the threshold, the
    reviewable point valued inside its first window, at 66, reviews next at ``t = 54``,
    policy month 120, and lapses at the shock rate from there to ``t = 65``, policy month
    131, and at the table's from ``t = 66``; the same point issued 13 months on reviews at
    ``t = 73``, its policy month 60, with its window to ``t = 84``.  The References are set
    on a model just read (K7).
    """
    model = mx.read_model(model_path(SEC), name=_name("reviews"))
    try:
        model.Projection.review_prem_shock = 0.10
        p = _row(model, "derived", 3, 66)
        assert [p.reviews_passed(t) for t in (0, 53, 54)] == [1, 1, 2]
        assert [p.review_shock_active(t) for t in (53, 54, 65, 66)] == [
            False, True, True, False]
        assert p.lapse_rate(54) == pytest.approx(p.lapse_rate_base(54) + 0.10, rel=1e-12)
        assert p.premium_pp(54) == pytest.approx(55.0 * 1.1, rel=1e-12)
    finally:
        model.close()
    table = _committed()
    future = _label(table, "future", 4, -13)
    model = _read_edited(tmp_path, _then(_set("premium_guarantee", [future], "reviewable"),
                                         _set("indexation", [future], False)))
    try:
        model.Projection.review_prem_shock = 0.10
        f = _point(model, future)
        assert [f.reviews_passed(t) for t in (13, 72, 73)] == [0, 0, 1]
        assert [f.review_shock_active(t) for t in (72, 73, 84, 85)] == [
            False, True, True, False]
        assert f.premium_pp(72) == 55.0
        assert f.premium_pp(73) == pytest.approx(55.0 * 1.1, rel=1e-12)
    finally:
        model.close()


# ---------------------------------------------------------------------------
# The caps on the claim rates
#
# ci_rate caps each life's diagnosis rate at 1, claim_rate_life each life's claim rate and
# claim_rate the policy's, the bound second, as CI_UK_S's do since M0.  At the shipped
# tables the claim rate stays at 0.0404 or less to the end of every frame, the joint point's
# last month, so neither the committed points nor the splice grid come near a cap, and Data
# refuses a table rate past 1.  So the caps bind through the product: CAPPED's table writes
# the male non-smoker's diagnosis rate at 0.98 at pivot age 60 and 1.0 at 65, rates Data
# accepts.  On the reviewable point the select latch, closed at its first review under the
# splice's change, loads the rate by 10%, so that the diagnosis rate's product passes 1 from
# attained age 60, policy month 240, where it stays, and the claim rates with it.  On the
# anchor cell, which no review loads, the diagnosis rate stays below 1, and its claim rate,
# the diagnosis rate and 90% of the mortality, passes 1 from attained age 64, policy month
# 288: each life's cap alone.  And on the joint point, its second life made a male
# non-smoker issued at 42 (CAPPED_JOINT), the second life's claim rate passes 1 at its own
# attained age 64, policy month 264, while the first's, at 62, is below 1: the second life's
# cap alone.  S points 3, 1 and 7 in a copy of S's table, under SPLICED_REFS, each as (its
# first capped month, the life whose rate passes 1, that life's attained age then, and the
# rates capped from then on).
CAPPED = {CI_RATES: _then(_written("i_ci", 0.98, _pivot("M", "NS", 60)),
                          _written("i_ci", 1.0, _pivot("M", "NS", 65)))}
CAPPED_JOINT = {"joint_sex": "M", "joint_smoker": "NS", "joint_age": 42}
CAPPED_POINTS = {3: (12 * (60 - 40), 1, 60, ("ci_rate", "claim_rate_life", "claim_rate",
                                             "claim_rate_mth")),
                 1: (12 * (64 - 40), 1, 64, ("claim_rate_life", "claim_rate",
                                             "claim_rate_mth")),
                 7: (12 * (64 - 42), 2, 64, ("claim_rate_life", "claim_rate",
                                             "claim_rate_mth"))}


def _capped_s(tmp_path):
    """CI_UK_S on :data:`CAPPED_POINTS` alone, the joint one's second life
    :data:`CAPPED_JOINT`, on :data:`CAPPED`'s table, under :data:`SPLICED_REFS`, read from
    a copy of S's inputs; the caller closes it."""
    table = _s_table().loc[sorted(CAPPED_POINTS)].astype({"joint_sex": object})
    for column, value in CAPPED_JOINT.items():
        table.loc[7, column] = value
    s = mx.read_model(temp_inputs(tmp_path, model_path(TWIN), model_points=table,
                                  edits=CAPPED), name=_name("capped_s"))
    for ref, value in SPLICED_REFS.items():
        setattr(s.Projection, ref, value)
    return s


def _capped_rate(p, name, t, life):
    """``name``'s rate in month ``t``: a life's rate for ``life``, or the policy's."""
    if name in ("ci_rate", "claim_rate_life"):
        return p.cells[name](t, life)
    return p.cells[name](t)


def test_an_annual_claim_rate_past_1_is_capped_in_both_models(tmp_path):
    """Where an annual claim rate passes 1, both models' rate is 1.

    On each of :data:`CAPPED_POINTS`, on :data:`CAPPED`'s table under :data:`SPLICED_REFS`,
    ``CI_UK_S``'s rate passes 1 in its first capped month and stays past it to the end of
    the frame: on the reviewable point the diagnosis rate's product, loaded by the latch, and
    with it each life's claim rate and the policy's; on the anchor cell each life's claim
    rate and the policy's, the diagnosis rate staying below 1; and on the joint point the
    second life's claim rate and the policy's, the first life's diagnosis rate staying below
    1.  Both models cap each: the capped rates and the monthly decrement,
    ``1 - (1 - q)^(1/12)``, are 1.0 in every one of those months, the float, not the int 1,
    which compares equal to it, and S's are floats below 1 in every month before.  So every
    policy in force at the start of the first capped month claims in it, none is in force
    after it, and every report holds finite floats alone.

    Four rows of each point, built from S by the generator: issued at the valuation date
    and 12 months after it, and restated in force in the month before the cap, opened with
    S's count and state there, each compared with S in every cell, the capped months
    included, as T1, T3 and the splice compare them, to 1e-9 relative with no absolute
    floor, but for the residual, rounding around 0, which keeps the floor of 1e-9
    (USLIB-SEC-PLAN.md §5.1, step 6); and restated five months into the capped year,
    opened with S's state there and one policy, since S's count there is 0.  On each, the
    capped rates are 1.0 from its first capped month, every policy in force there claims in
    it, and the count is 0.0 after it.
    """
    s = _capped_s(tmp_path / "s")
    sec = None
    try:
        derived, future = [], []
        for s_point, (cap, life, age, names) in CAPPED_POINTS.items():
            sp = _point(s, s_point)
            end = sp.proj_len()
            first = next(t for t in range(end) if sp.claim_rate(t) == 1.0)
            assert (first, sp.age(first, life)) == (cap, age), s_point
            after = range(cap, end)
            for name in names:
                assert all(type(_capped_rate(sp, name, t, life)) is float
                           and _capped_rate(sp, name, t, life) < 1.0
                           for t in range(cap)), name
                assert [(type(_capped_rate(sp, name, t, life)),
                         _capped_rate(sp, name, t, life))
                        for t in after] == [(float, 1.0)] * len(after), name
            if "ci_rate" not in names:
                assert all(sp.ci_rate(t, 1) < 1.0 for t in range(end))
            if life == 2:
                assert all(sp.claim_rate_life(t, 1) < 1.0 for t in range(cap + 1))
            _sweep_s(sp)
            assert sp.pols_if(cap) > 0.0 and sp.pols_claim(cap) == sp.pols_if(cap)
            assert [sp.pols_if(t) for t in range(cap + 1, end)] == [0.0] * (len(after) - 1)
            derived += [(s_point, cap - 1), (s_point, cap + 5)]
            future.append((s_point, 12))
        rows, _ = build_sec_table(dataclasses.replace(SPEC, derived=tuple(derived),
                                                      future=tuple(future),
                                                      derived_refs={}), s)
        emptied = (rows["row_kind"] == "derived") & (rows["policy_count"] == 0.0)
        assert emptied.sum() == len(CAPPED_POINTS)
        rows.loc[emptied, "policy_count"] = 1.0
        sec = mx.read_model(_sec_inputs(tmp_path / "sec", rows, edits=CAPPED),
                            name=_name("capped"))
        for ref, value in SPLICED_REFS.items():
            setattr(sec.Projection, ref, value)
        for s_point, (cap, life, _, names) in CAPPED_POINTS.items():
            sp = _point(s, s_point)
            # Each row with the month its rates are first capped, on its own clock, and the
            # exemptions of its comparison with S: none for the row S's count does not open.
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
                for name in names:
                    assert [(type(_capped_rate(p, name, t, life)),
                             _capped_rate(p, name, t, life))
                            for t in capped] == [(float, 1.0)] * len(capped), (case, name)
                assert p.pols_if(first) > 0.0 and p.pols_claim(first) == p.pols_if(first)
                assert [p.pols_if(t) for t in later] == [0.0] * len(later), case
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
# point whose twin reads it, the calls that must give the float NaN, and the References set
# beside it).  Each life's claim rate cap reads overlap_k, and the policy's too, single and
# joint; the diagnosis rate's cap reads the trend from the second valuation year, and the
# latch's loading once a review has closed it; the standalone paid rate's cap reads the
# survival slippage; the RPI's floor and cover cap, max(rpi, 0.0) and min(..., 0.1), read
# rpi_rate, and the premium increase's cap, min(1.5 x increase, 0.15), idx_prem_mult, on the
# indexed point after its first anniversary; and the ancillary benefits' caps,
# min(share x SA, cap), read their shares.  A bound written first would turn each NaN into
# the bound: a blank input read as a certain claim, or as a cover increase of 10%.  This
# form runs compiled unchanged, since a compiled ItemSpace takes the References when it is
# made (USLIB-SEC-PLAN.md §5.1, step 6, precised at M12).
NAN_BOUNDS = [
    ("each life's claim rate cap, min(q, 1.0)", "overlap_k", 1,
     [("claim_rate_life", (0, 1)), ("claim_rate", (0,)), ("claim_rate_mth", (299,)),
      ("pols_if", (1,))], {}),
    ("the joint claim rate's cap", "overlap_k", 7,
     [("claim_rate_life", (0, 2)), ("claim_rate", (0,)), ("pols_if", (1,))], {}),
    ("the diagnosis rate's cap, through the trend", "ci_trend", 1,
     [("ci_rate", (12, 1)), ("claim_rate", (12,)), ("ap_rate", (12,))], {}),
    ("the diagnosis rate's cap, through the latch", "sel_lapse_ci_loading", 3,
     [("ci_sel_factor", (60,)), ("ci_rate", (60, 1)), ("claim_rate", (60,))],
     {"review_prem_shock": 0.10}),
    ("the standalone paid rate's cap", "survival_slip", 2,
     [("claim_rate_paid", (0,)), ("claim_rate_paid_mth", (0,)),
      ("claims", (0, "MAIN"))], {}),
    ("the RPI's floor and cover cap", "rpi_rate", 4,
     [("idx_increase", ()), ("idx_factor", (12,)), ("idx_prem_factor", (12,))], {}),
    ("the premium increase's cap", "idx_prem_mult", 4, [("idx_prem_factor", (12,))], {}),
    ("the additional payment's cap", "ap_share", 1,
     [("benefit_pp", (0, "AP")), ("claims", (0, "AP"))], {}),
    ("the children's cover's cap", "child_share", 1,
     [("benefit_pp", (0, "CHILD")), ("claims", (0, "CHILD"))], {}),
]


@pytest.mark.parametrize("bound, ref, s_point, calls, refs", NAN_BOUNDS,
                         ids=[c[0] for c in NAN_BOUNDS])
def test_a_nan_that_reaches_a_bound_stays_nan(bound, ref, s_point, calls, refs):
    """A NaN that reaches a bound written second stays NaN, and is not read as the bound.

    ``min`` keeps its first argument unless a later one compares smaller, and ``max`` unless
    a later one compares larger, in modelx and compiled alike, and no comparison with NaN
    holds, so with its bound first each would turn a NaN into the bound.  Each is written
    with its bound second, as ``CI_UK_S`` writes it (:data:`NAN_BOUNDS`): the Reference
    that feeds it is set to NaN on a model read for the test, and every call must give the
    float NaN.  The cells are called on their own, without the frame: ``proj_len()`` refuses
    each of these References at NaN before a report reaches a bound (the domain test).
    The lapse rate's bounds keep ``CI_UK_S``'s order, the bound first, and are no cap on a
    claim rate (USLIB-SEC-PLAN.md §5.1, step 6); ``proj_len()`` holds their References to
    domains no NaN is in.
    """
    model = mx.read_model(model_path(SEC), name=_name("nan"))
    try:
        setattr(model.Projection, ref, float("nan"))
        for name, value in refs.items():
            setattr(model.Projection, name, value)
        p = _row(model, "twin", s_point, 0)
        lost = [f"{name}{args} = {value!r}" for name, args in calls
                for value in [p.cells[name](*(_code(p, a) if isinstance(a, str) else a
                                              for a in args))]
                if not (type(value) is float and math.isnan(value))]
        assert not lost, f"{bound} loses a NaN {ref}: {lost}"
    finally:
        model.close()


def test_no_check_passes_a_residual_that_is_not_a_number():
    """No check passes a residual that is NaN (§7.1).

    A check is ``abs(resid) <= tolerance`` over the frame, and no comparison with NaN
    holds, so a NaN residual would fail it, as ``CI_UK_S``'s does (USLIB-SEC-PLAN.md §7.1,
    *Precised at M3*, item 11); and the frame comes first.  With ``overlap_k`` NaN, set on a
    model read for the test before it computes anything, the claim rates, the counts and so
    both residuals are NaN on the standalone twin, and each check, asking ``proj_len()`` for
    the frame, is refused the Reference, by name, before it compares one.  So no check
    passes; and on the shipped References each is the bool True.
    """
    for overlap, closes in ((float("nan"), False), (0.1, True)):
        model = mx.read_model(model_path(SEC), name=_name("nan_check"))
        try:
            model.Projection.overlap_k = overlap
            p = _row(model, "twin", 2, 0)
            assert math.isnan(p.check_pols_roll_fwd_resid(0)) != closes
            assert math.isnan(p.check_claim_split_resid(0)) != closes
            if closes:
                assert p.check_pols_roll_fwd() is True and p.check_claim_split() is True
            else:
                refusal = "point_id 2: overlap_k must be a number from 0 to 1, not nan"
                _refused(p.check_pols_roll_fwd, refusal)
                _refused(p.check_claim_split, refusal)
        finally:
            model.close()


@pytest.mark.parametrize("check, resid", [
    ("check_pols_roll_fwd", "check_pols_roll_fwd_resid"),
    ("check_claim_split", "check_claim_split_resid")])
def test_a_check_fails_a_residual_that_is_not_a_number(sec_model, check, resid):
    """Each check returns False where its residual is NaN (§7.1, item 11).

    A check is ``abs(resid) <= tolerance`` over the frame, which no NaN passes, as
    ``CI_UK_S``'s is; but no input the frame accepts gives a NaN residual any more, so the
    residual's formula is replaced, on a model read for the test, by one that returns NaN in
    every month.  Then the check is the bool False on every committed point, where with its
    own formula it is True.  A check that asked whether any residual was past its tolerance
    would pass NaN.
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


def test_a_whole_review_period_written_as_a_float_is_read_as_the_int():
    """``review_period_mths`` written ``60.0`` projects as 60 does, cell for cell (F3).

    The reviews divide the policy months by the period, and a float period would make
    ``reviews_passed`` a float in cover, ``1.0``, where it is the int 0 outside it, and the
    C step types a cell by the values it returns.  The period is read as the int it is, once
    ``proj_len()`` has held it to a whole number, so on every reviewable point, with the
    review change on so that the reviews move premiums and open windows, every value each
    cell holds after the reports, the checks and every monthly cell at every month is the
    same value, of the same type, under 60.0 as under 60.
    """
    models = []
    try:
        for period in (60, 60.0):
            model = mx.read_model(model_path(SEC), name=_name("period"))
            model.Projection.review_period_mths = period
            model.Projection.review_prem_shock = REVIEW_SHOCK
            models.append(model)
        table = models[0].Data.model_point_table()
        found = []
        for label in table.index[table["premium_guarantee"] == "reviewable"]:
            a, b = _point(models[0], label), _point(models[1], label)
            for p in (a, b):
                sweep(p)
                assert full_sweep(p) == {}, label
            for name, cells in a.cells.items():
                for args in _cached_args(cells):
                    want, have = cells(*args), b.cells[name](*args)
                    if isinstance(want, pd.DataFrame):
                        same = want.equals(have) and list(want.dtypes) == list(have.dtypes)
                    elif isinstance(want, pd.Series):
                        same = want.equals(have) and want.dtype == have.dtype
                    else:
                        same = type(want) is type(have) and want == have
                    if not same:
                        found.append(f"point {label}: {name}{args}: {want!r}, {have!r}")
            last = b.reviews_passed(b.proj_len() - 1)
            assert type(last) is int and last >= 1, label
        assert not found, found[:10]
    finally:
        for model in models:
            model.close()


def _outside_cover_faults(p, where):
    """Where ``p``, an ItemSpace that has evaluated nothing, departs from OUTSIDE_COVER.

    Every cell of :data:`OUTSIDE_COVER`, ``pols_if_at`` at each timing, ``claims`` at each
    kind, ``benefit_pp`` at each benefit and ``ci_rate_base`` and ``mort_rate`` at each life
    the point has, in every month before issue and at ``t = proj_len()``, the first month
    after cover, which the count's look-ahead reads, against :data:`OUTSIDE_COVER`; then
    whether any of :data:`IN_COVER_ONLY` was evaluated on the way, which only a fresh
    ItemSpace can say.  A cell that raises is reported as a fault too, so the scan goes on.
    """
    faults = []
    lives = (1, 2) if p.is_joint() else (1,)
    for t in [*range(p.t_entry()), p.proj_len()]:
        calls = [(name, (t,), want) for name, want in OUTSIDE_COVER.items()]
        calls += [("pols_if_at", (t, _code(p, timing)), 0.0) for timing in TIMINGS]
        calls += [("claims", (t, _code(p, kind)), 0.0) for kind in KINDS]
        calls += [("benefit_pp", (t, _code(p, kind)), 0.0) for kind in BENEFITS]
        calls += [(name, (t, life), 0.0) for name in ("ci_rate_base", "mort_rate")
                  for life in lives]
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

    The committed table's one point issued after the valuation date is the indexed point,
    which is not reviewable and is single, so on it a cell tied to the reviews or to a
    second life would hold zero before issue, guarded or not.  So the same scan runs on the
    splice's future rows, the core's or, with ``UKLIB_SEC_FULL=1``, all of them: the
    reviewable point, the standalone and reviewable one, the joint point and the point issued
    at 50 among them.  Each row is made afresh first and released after.

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
    summed as ``run_sec.py --block`` sums them, are indexed 0..311 and equal S's frame added
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
    assert list(block.index) == list(range(312))
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
    label = extract.index[extract["policy_id"] == "CI-000003-M66"][0]
    out = _run_sec(runner, str(label))
    count = _row(sec_model, "derived", 3, 66).pols_if(0)
    assert out.splitlines()[:2] == [
        f"model point {label}: CI-000003-M66 - M40 smoker NS accelerated, 25-year term, "
        f"cover 100,000, reviewable premium, children's cover",
        f"at the valuation date: in force 66 months: policy year 6, attained age 45, "
        f"{count:.6f} in force"]
    last = extract.index[extract["policy_id"] == "CI-000001-M299"][0]
    moved = _set("duration_mth", [last], 301)(extract)
    model = mx.read_model(_sec_inputs(tmp_path / "moved", moved), name=_name("moved"))
    try:
        _refused(_point(model, last).result_cf,
                 f"point_id {last}: duration_mth 301 is at or past the end of cover, "
                 f"policy month 300")
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
            f"{p.age(0, 1)}, {p.pols_if(0):.6f} in force")


def test_run_sec_prints_a_point_and_the_block(sec_model):
    """The runner prints one point, saying where it came from, and the block (D8).

    Each mode in an interpreter of its own, as a user runs it, with exit code 0 and ASCII
    output, so that it prints on a Windows console under any code page.  The numbers are
    the model's.  The anchor cell, the runner's default, with its lines at the valuation
    date, each asserted whole, so that a longer number cannot pass for the one asserted,
    and its first twelve rows of cash flows and counts.  Point 7, the joint point, whose
    line names its second life through the cells that take one; point 9, restated in force
    at S's month 60; and point 13, to be issued 13 months on: each with the two lines that
    say where its row came from and where it stands, which only the committed table's
    generator columns can say.  And the block: a line for each committed point, in table
    order, its first twelve rows, which must be the committed points' frames summed row by
    row, as this test sums them, and those frames summed into projection years, each
    year's count the one in force in its first month.  Nothing else runs the runner on the
    committed table.
    """
    runner = model_path(SEC).parent / "run_sec.py"
    out = _run_sec(runner)
    assert out.splitlines()[:3] == [
        "model point 1: CI-000001 (S's CI-000001) - M40 smoker NS accelerated, 25-year "
        "term, cover 100,000, guaranteed premium, children's cover",
        "at the valuation date: issued at the valuation date, t = 0",
        "proj_len = 300 months from the valuation date (t = 0..299); cover ends at policy "
        "month 300"]
    anchor = _row(sec_model, "twin", 1, 0)
    assert anchor.result_cf().head(12).round(2).to_string() in out
    assert anchor.result_pols().head(12).round(6).to_string() in out
    count = _row(sec_model, "derived", 3, 60).pols_if(0)
    for point_id, lines in (
            ("7", ["model point 7: CI-000007 (S's CI-000007) - M40 smoker NS accelerated, "
                   "25-year term, cover 100,000, guaranteed premium, children's cover, "
                   "joint with F38 smoker NS",
                   "at the valuation date: issued at the valuation date, t = 0"]),
            ("9", ["model point 9: CI-000003-M60 (S's CI-000003 at its month 60) - M40 "
                   "smoker NS accelerated, 25-year term, cover 100,000, reviewable premium, "
                   "children's cover",
                   f"at the valuation date: in force 60 months: policy year 6, attained "
                   f"age 45, {count:.6f} in force"]),
            ("13", ["model point 13: CI-000004-F13 (S's CI-000004, issued 13 months on) - "
                    "M40 smoker NS accelerated, 25-year term, cover 100,000, guaranteed "
                    "premium, indexed, children's cover",
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
    annual = block.drop(columns="pols_if").groupby(years).sum()
    annual.insert(0, "pols_if", [block.at[12 * (y - 1), "pols_if"] for y in annual.index])
    assert annual.head(12).round(2).to_string() in out


# run_sec.py run as though it sat at /m/products/critical_illness, a copy too shallow to
# have a repository above it: the source compiled under that name, so that its own __file__
# is it.
SHALLOW_RUN = """\
import sys
source = open(sys.argv[1], encoding="utf-8").read()
where = "/m/products/critical_illness/run_sec.py"
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


# The eight cells to which CI_UK_S gives a life defaulted to 1, which here take it with no
# default.
LIFE_CELLS = ("age_at_entry", "sex", "smoker", "age", "ci_rate_base", "mort_rate", "ci_rate",
              "claim_rate_life")


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

    ``CI_UK_S`` gives :data:`LIFE_CELLS` a ``life`` defaulted to 1.  A compiled model
    declares such a parameter in its ``.pxd`` as ``long long life=*``, which the C step's
    typing guard would read as a parameter named ``life=*``, so here none of the eight has a
    default and every caller passes 1 or 2, positionally: a call that left it out would
    raise.  modelx keys ``CI_UK_S``'s ``age(t)`` by the arguments bound, ``(t, 1)``, so the
    twin identity, which ``test_model_conventions_uk`` asserts, pairs the cells as before.
    ``claims``' ``kind=None`` is R12's total, which the C step settles.
    """
    assert _defaulted(TWIN) == sorted((*LIFE_CELLS, "claims"))
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
    outside the parentheses of the column, ``age`` of ``age(t, life)``.
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


# What only CI_UK_S's docstrings may say: a reference into its Spaces, which the SEC pages
# would link to the wrong model; its clock, t counting policy months from issue, t = 0 the
# issue month, and the policy year t // 12 + 1; and its frame of 12 x term months from t = 0.
STALE = re.compile(r"~\.CI_UK_S\.|``t = 0`` is the issue month"
                   r"|``t`` counts \*\*policy months|``t // 12 \+ 1``|y = t//12"
                   r"|``proj_len\(\) = 12 x term``")


def test_the_docstrings_describe_the_valuation_clock(sec_model, s_model):
    """The docstrings say what this model is, and none says what only CI_UK_S is.

    Whitespace is collapsed first, as ``test_model_conventions_uk`` collapses it, so that a
    phrase split across a line break still matches.  The model docstring names the
    valuation date, BasicTerm_SE, the policy clock, the SEC table and the product.  The
    symbol map in the Projection docstring maps every cell running in force adds, which are
    exactly the cells ``CI_UK_S`` lacks, and names nothing the model lacks: every name in it
    is a cell or a Reference.  No row of a simple table in any docstring puts text between
    two of its columns (:func:`_table_overruns`), which would drop the table from the
    rendered page.  And no docstring says what :data:`STALE` matches.
    """
    flat = {where: re.sub(r"\s+", " ", doc) for where, doc in _docs(sec_model)}
    for phrase in ("valuation date", "BasicTerm_SE", "duration_mth", TABLE,
                   "critical illness"):
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
    assert not stale, f"docstrings that describe CI_UK_S: {stale}"


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


def test_the_core_grid_reaches_every_branch(spliced, splice_records):
    """What the default run's T2 and T3 cases reach, which the full grid only multiplies.

    The default run thins the splice to a core (the module docstring), and this test is
    what keeps the thinning from costing a branch.  First, statically, over S's table with
    the variants, each property below holds of some core case: both contract types, both
    premium guarantees, both life bases, the four sex and smoker groups of either life and
    a second life, the indexation option, children's cover on and off, the reviews with the
    indexation and with the standalone contract and a second life, an issue age whose
    pivots run past the table's last and whose cover sits below the ancillary caps; and each
    kind of valuation month: the first months, on an anniversary, in the month before one,
    mid-year, before the first review, on a review, inside its window, in the window's last
    month and after it, and the last covered month.  And of some core future case: issued
    off the valuation anniversaries and on them, more than a year on, reviewable, indexed,
    standalone, a second life and below the caps.

    Then, on the splice's model, of some core row, each of :data:`AT_VALUATION` and
    :data:`IN_FRAME`, what no column of the table shows: every opening-state column in use,
    and each kind of valuation month the reviews make; and every branch and both sides of
    every ``min`` and ``max`` the full grid reaches: the reviews and their windows, each
    before and after the valuation date, the latch closed and carried, the pivot
    interpolation's three branches, the lapse table's last year, an index step, the
    ancillary caps either side, the standalone split, the second life and the expiry.

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

    def reviewable(p):
        return at(p, "premium_guarantee") == "reviewable"

    def joint(p):
        return at(p, "life_basis") == "joint_first_event"

    splices = {
        **{f"the {c} contract": (lambda k, p, d, c=c: at(p, "contract_type") == c)
           for c in ("accelerated", "standalone")},
        **{f"{g} premiums": (lambda k, p, d, g=g: at(p, "premium_guarantee") == g)
           for g in ("guaranteed", "reviewable")},
        **{f"the {b} life basis": (lambda k, p, d, b=b: at(p, "life_basis") == b)
           for b in ("single", "joint_first_event")},
        **{f"sex {x}, smoker {y}, of either life": (lambda k, p, d, x=x, y=y: (
            (at(p, "sex"), at(p, "smoker")) == (x, y)
            or (joint(p) and (at(p, "joint_sex"), at(p, "joint_smoker")) == (x, y))))
           for x in ("M", "F") for y in ("NS", "S")},
        **{f"a second life, sex {x}, smoker {y}": (lambda k, p, d, x=x, y=y: (
            joint(p) and (at(p, "joint_sex"), at(p, "joint_smoker")) == (x, y)))
           for x, y in (("F", "NS"), ("M", "S"))},
        "indexation": lambda k, p, d: flag(p, "indexation"),
        "children's cover on": lambda k, p, d: flag(p, "children_cover"),
        "children's cover off": lambda k, p, d: not flag(p, "children_cover"),
        "reviews with indexation": lambda k, p, d: reviewable(p) and flag(p, "indexation"),
        "reviews on the standalone contract": lambda k, p, d: (
            reviewable(p) and at(p, "contract_type") == "standalone"),
        "reviews on two lives": lambda k, p, d: reviewable(p) and joint(p),
        "pivots past the last": lambda k, p, d: (
            int(at(p, "age_at_entry")) + int(at(p, "policy_term")) > 65),
        "cover below the ancillary caps": lambda k, p, d: at(p, "sum_assured") < 50000,
        "in the second month": lambda k, p, d: d == 1,
        "on an anniversary": lambda k, p, d: d % 12 == 0,
        "in the month before an anniversary": lambda k, p, d: d % 12 == 11,
        "mid-year": lambda k, p, d: d % 12 not in (0, 11),
        "before the first review, reviewable": lambda k, p, d: reviewable(p) and d < 60,
        "on a review": lambda k, p, d: reviewable(p) and d >= 60 and d % 60 == 0,
        "inside a review's window": lambda k, p, d: (
            reviewable(p) and d >= 60 and 0 < d % 60 < 11),
        "in a window's last month": lambda k, p, d: reviewable(p) and d >= 60 and d % 60 == 11,
        "after a review's window": lambda k, p, d: reviewable(p) and d >= 60 and d % 60 >= 12,
        "in the last covered month": lambda k, p, d: d == COVER[p] - 1,
    }
    futures = {
        "issued off the anniversaries": lambda p, k: k % 12 != 0,
        "issued on them": lambda p, k: k % 12 == 0,
        "issued more than a year on": lambda p, k: k > 12,
        "reviewable": lambda p, k: reviewable(p),
        "indexation": lambda p, k: flag(p, "indexation"),
        "the standalone contract": lambda p, k: at(p, "contract_type") == "standalone",
        "a second life": lambda p, k: joint(p),
        "cover below the ancillary caps": lambda p, k: at(p, "sum_assured") < 50000,
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
    model as M3 committed it was frozen below (USLIB-SEC-PLAN.md §5.4): for each point,
    each column of ``result_cf()`` and ``result_pols()``, its sum, its largest absolute
    value and its values at five fixed months, the frame's first and last and the three
    quartiles between.  Every later version must reproduce it, to 1e-12 relative, floored
    at 1e-12 of the column's own magnitude (``uk_sec_support.fingerprint_mismatches``),
    with the same points, frames and columns exactly.  ``python
    tools/gen_sec_fingerprint.py CI_UK_SEC --check`` runs the same comparison from the
    command line.
    """
    assert fingerprint_mismatches(FINGERPRINT, sec_model) == []


# CI_UK_SEC's fingerprint, frozen from the model as M3 committed it and committed alone,
# before its C step changed anything; refrozen once, alone, when M3's review added point
# 14, the row with review history, which left points 1 to 13 as they were.  Each point is
# keyed by its point_id; each column holds (its sum over the frame, its largest absolute
# value, (its values at the months)).  The block is written by
# tools/gen_sec_fingerprint.py, and is never edited by hand: a refreeze goes through the
# tool's --force, in a commit of its own that says why.
# BEGIN generated fingerprint: CI_UK_SEC -- tools/gen_sec_fingerprint.py
FINGERPRINT = {
    1: {"rows": 300, "months": (0, 74, 149, 224, 299),
        "result_cf": {
            "pols_if": (153.57633741710418, 1.0, (
                1.0, 0.6436257064073656, 0.4819178429493733, 0.34988451860438363,
                0.24091005429258047)),
            "premiums": (8446.698557940732, 55.0, (
                55.0, 35.39941385240511, 26.50548136221553, 19.2436485232411,
                13.250052986091926)),
            "claims_main": (9431.877318394943, 51.06765150137514, (
                19.270411067118243, 22.169849326961323, 29.87867827920017,
                39.85190938956583, 48.12186183562568)),
            "claims_ap": (235.35640506943912, 1.2449333047465951, (
                0.46874999999999994, 0.5523920357161402, 0.7535259944137959,
                1.003805510344145, 1.1731204926071708)),
            "claims_child": (127.98028118092019, 0.8333333333333334, (
                0.8333333333333334, 0.5363547553394714, 0.4015982024578111,
                0.2915704321703197, 0.2007583785771504)),
            "claims_lapse": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claim_expenses": (23.579693295987358, 0.12766912875343786, (
                0.04817602766779561, 0.055424623317403304, 0.07469669569800043,
                0.09962977347391458, 0.1203046545890642)),
            "expenses": (717.1807498238388, 202.5, (
                202.5, 1.9213068821020372, 1.7177490278762404, 1.4891374302202778,
                1.2243013463825339)),
            "net_cf": (-2089.2758898243983, 168.12067042811935, (
                -168.12067042811935, 10.164086228968735, -6.320766837430488,
                -23.492404012533395, -37.590293721689676)),
        },
        "result_pols": {
            "pols_if": (153.57633741710418, 1.0, (
                1.0, 0.6436257064073656, 0.4819178429493733, 0.34988451860438363,
                0.24091005429258047)),
            "pols_new_biz": (1.0, 1.0, (
                1.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_claim": (0.09431877318394945, 0.0005106765150137514, (
                0.00019270411067118243, 0.00022169849326961322, 0.00029878678279200173,
                0.00039851909389565835, 0.0004812186183562568)),
            "pols_lapse": (0.6660689002583297, 0.008739926410331863, (
                0.008739926410331863, 0.0021850342392730443, 0.001635603936354174,
                0.0011868730466144933, 0.0008165091165034733)),
            "pols_maturity": (0.23961232655772075, 0.23961232655772075, (
                0.0, 0.0, 0.0, 0.0, 0.23961232655772075)),
            "pols_if_aft_decr": (152.5763374171042, 0.991067369478997, (
                0.991067369478997, 0.641218973674823, 0.47998345223022715,
                0.3482991264638735, 0.0)),
            "ci_rate": (1.8970291755310917, 0.01558251932392911, (
                0.0015, 0.0027464013582652945, 0.005003515054281687, 0.009180679516527256,
                0.01558251932392911)),
            "mort_rate": (1.042696032406785, 0.009028804514474343, (
                0.0009, 0.0015324522979124205, 0.002679011690755323, 0.004891158657635536,
                0.009028804514474343)),
            "claim_rate": (2.8354556046971986, 0.02370844338695602, (
                0.00231, 0.004125608426386473, 0.0074146255759614775, 0.013582722308399239,
                0.02370844338695602)),
            "claim_rate_mth": (0.2377876345820149, 0.0019975032580907826, (
                0.00019270411067118243, 0.00034445251496728613, 0.0006199952692421684,
                0.0011390017926065088, 0.0019975032580907826)),
            "lapse_rate": (13.920000000000002, 0.1, (
                0.1, 0.04, 0.04, 0.04, 0.04)),
        },
    },
    2: {"rows": 300, "months": (0, 74, 149, 224, 299),
        "result_cf": {
            "pols_if": (153.57633741710418, 1.0, (
                1.0, 0.6436257064073656, 0.4819178429493733, 0.34988451860438363,
                0.24091005429258047)),
            "premiums": (8446.698557940732, 55.0, (
                55.0, 35.39941385240511, 26.50548136221553, 19.2436485232411,
                13.250052986091926)),
            "claims_main": (6108.772008158783, 32.42754178729243, (
                12.133093383837057, 14.306016777976945, 19.53469842877457,
                26.07168800698065, 30.55698939895531)),
            "claims_ap": (235.35640506943912, 1.2449333047465951, (
                0.46874999999999994, 0.5523920357161402, 0.7535259944137959,
                1.003805510344145, 1.1731204926071708)),
            "claims_child": (127.98028118092019, 0.8333333333333334, (
                0.8333333333333334, 0.5363547553394714, 0.4015982024578111,
                0.2915704321703197, 0.2007583785771504)),
            "claims_lapse": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claim_expenses": (23.579693295987358, 0.12766912875343786, (
                0.04817602766779561, 0.055424623317403304, 0.07469669569800043,
                0.09962977347391458, 0.1203046545890642)),
            "expenses": (717.1807498238388, 202.5, (
                202.5, 1.9213068821020372, 1.7177490278762404, 1.4891374302202778,
                1.2243013463825339)),
            "net_cf": (1233.8294204117628, 160.9833527448382, (
                -160.9833527448382, 18.027918777953115, 4.023213012995113,
                -9.71218262994821, -20.0254212850193)),
        },
        "result_pols": {
            "pols_if": (153.57633741710418, 1.0, (
                1.0, 0.6436257064073656, 0.4819178429493733, 0.34988451860438363,
                0.24091005429258047)),
            "pols_new_biz": (1.0, 1.0, (
                1.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_claim": (0.09431877318394945, 0.0005106765150137514, (
                0.00019270411067118243, 0.00022169849326961322, 0.00029878678279200173,
                0.00039851909389565835, 0.0004812186183562568)),
            "pols_lapse": (0.6660689002583297, 0.008739926410331863, (
                0.008739926410331863, 0.0021850342392730443, 0.001635603936354174,
                0.0011868730466144933, 0.0008165091165034733)),
            "pols_maturity": (0.23961232655772075, 0.23961232655772075, (
                0.0, 0.0, 0.0, 0.0, 0.23961232655772075)),
            "pols_if_aft_decr": (152.5763374171042, 0.991067369478997, (
                0.991067369478997, 0.641218973674823, 0.47998345223022715,
                0.3482991264638735, 0.0)),
            "ci_rate": (1.8970291755310917, 0.01558251932392911, (
                0.0015, 0.0027464013582652945, 0.005003515054281687, 0.009180679516527256,
                0.01558251932392911)),
            "mort_rate": (1.042696032406785, 0.009028804514474343, (
                0.0009, 0.0015324522979124205, 0.002679011690755323, 0.004891158657635536,
                0.009028804514474343)),
            "claim_rate": (2.8354556046971986, 0.02370844338695602, (
                0.00231, 0.004125608426386473, 0.0074146255759614775, 0.013582722308399239,
                0.02370844338695602)),
            "claim_rate_mth": (0.2377876345820149, 0.0019975032580907826, (
                0.00019270411067118243, 0.00034445251496728613, 0.0006199952692421684,
                0.0011390017926065088, 0.0019975032580907826)),
            "lapse_rate": (13.920000000000002, 0.1, (
                0.1, 0.04, 0.04, 0.04, 0.04)),
        },
    },
    3: {"rows": 300, "months": (0, 74, 149, 224, 299),
        "result_cf": {
            "pols_if": (153.57633741710418, 1.0, (
                1.0, 0.6436257064073656, 0.4819178429493733, 0.34988451860438363,
                0.24091005429258047)),
            "premiums": (8446.698557940732, 55.0, (
                55.0, 35.39941385240511, 26.50548136221553, 19.2436485232411,
                13.250052986091926)),
            "claims_main": (9431.877318394943, 51.06765150137514, (
                19.270411067118243, 22.169849326961323, 29.87867827920017,
                39.85190938956583, 48.12186183562568)),
            "claims_ap": (235.35640506943912, 1.2449333047465951, (
                0.46874999999999994, 0.5523920357161402, 0.7535259944137959,
                1.003805510344145, 1.1731204926071708)),
            "claims_child": (127.98028118092019, 0.8333333333333334, (
                0.8333333333333334, 0.5363547553394714, 0.4015982024578111,
                0.2915704321703197, 0.2007583785771504)),
            "claims_lapse": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claim_expenses": (23.579693295987358, 0.12766912875343786, (
                0.04817602766779561, 0.055424623317403304, 0.07469669569800043,
                0.09962977347391458, 0.1203046545890642)),
            "expenses": (717.1807498238388, 202.5, (
                202.5, 1.9213068821020372, 1.7177490278762404, 1.4891374302202778,
                1.2243013463825339)),
            "net_cf": (-2089.2758898243983, 168.12067042811935, (
                -168.12067042811935, 10.164086228968735, -6.320766837430488,
                -23.492404012533395, -37.590293721689676)),
        },
        "result_pols": {
            "pols_if": (153.57633741710418, 1.0, (
                1.0, 0.6436257064073656, 0.4819178429493733, 0.34988451860438363,
                0.24091005429258047)),
            "pols_new_biz": (1.0, 1.0, (
                1.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_claim": (0.09431877318394945, 0.0005106765150137514, (
                0.00019270411067118243, 0.00022169849326961322, 0.00029878678279200173,
                0.00039851909389565835, 0.0004812186183562568)),
            "pols_lapse": (0.6660689002583297, 0.008739926410331863, (
                0.008739926410331863, 0.0021850342392730443, 0.001635603936354174,
                0.0011868730466144933, 0.0008165091165034733)),
            "pols_maturity": (0.23961232655772075, 0.23961232655772075, (
                0.0, 0.0, 0.0, 0.0, 0.23961232655772075)),
            "pols_if_aft_decr": (152.5763374171042, 0.991067369478997, (
                0.991067369478997, 0.641218973674823, 0.47998345223022715,
                0.3482991264638735, 0.0)),
            "ci_rate": (1.8970291755310917, 0.01558251932392911, (
                0.0015, 0.0027464013582652945, 0.005003515054281687, 0.009180679516527256,
                0.01558251932392911)),
            "mort_rate": (1.042696032406785, 0.009028804514474343, (
                0.0009, 0.0015324522979124205, 0.002679011690755323, 0.004891158657635536,
                0.009028804514474343)),
            "claim_rate": (2.8354556046971986, 0.02370844338695602, (
                0.00231, 0.004125608426386473, 0.0074146255759614775, 0.013582722308399239,
                0.02370844338695602)),
            "claim_rate_mth": (0.2377876345820149, 0.0019975032580907826, (
                0.00019270411067118243, 0.00034445251496728613, 0.0006199952692421684,
                0.0011390017926065088, 0.0019975032580907826)),
            "lapse_rate": (13.920000000000002, 0.1, (
                0.1, 0.04, 0.04, 0.04, 0.04)),
        },
    },
    4: {"rows": 300, "months": (0, 74, 149, 224, 299),
        "result_cf": {
            "pols_if": (153.57633741710418, 1.0, (
                1.0, 0.6436257064073656, 0.4819178429493733, 0.34988451860438363,
                0.24091005429258047)),
            "premiums": (13377.390689385371, 55.0, (
                55.0, 46.09924510296194, 44.95015370875603, 42.49918915092804,
                38.107335689323335)),
            "claims_main": (14709.14623053324, 103.81002100276919, (
                19.270411067118243, 26.471959502560075, 42.59985084114411,
                67.84520809833386, 97.82183713136172)),
            "claims_ap": (235.35640506943912, 1.2449333047465951, (
                0.46874999999999994, 0.5523920357161402, 0.7535259944137959,
                1.003805510344145, 1.1731204926071708)),
            "claims_child": (127.98028118092019, 0.8333333333333334, (
                0.8333333333333334, 0.5363547553394714, 0.4015982024578111,
                0.2915704321703197, 0.2007583785771504)),
            "claims_lapse": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claim_expenses": (23.579693295987358, 0.12766912875343786, (
                0.04817602766779561, 0.055424623317403304, 0.07469669569800043,
                0.09962977347391458, 0.1203046545890642)),
            "expenses": (717.1807498238388, 202.5, (
                202.5, 1.9213068821020372, 1.7177490278762404, 1.4891374302202778,
                1.2243013463825339)),
            "net_cf": (-2435.8526705180566, 168.12067042811935, (
                -168.12067042811935, 16.56180730392681, -0.5972670528339292,
                -28.230162093614478, -62.432986314194295)),
        },
        "result_pols": {
            "pols_if": (153.57633741710418, 1.0, (
                1.0, 0.6436257064073656, 0.4819178429493733, 0.34988451860438363,
                0.24091005429258047)),
            "pols_new_biz": (1.0, 1.0, (
                1.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_claim": (0.09431877318394945, 0.0005106765150137514, (
                0.00019270411067118243, 0.00022169849326961322, 0.00029878678279200173,
                0.00039851909389565835, 0.0004812186183562568)),
            "pols_lapse": (0.6660689002583297, 0.008739926410331863, (
                0.008739926410331863, 0.0021850342392730443, 0.001635603936354174,
                0.0011868730466144933, 0.0008165091165034733)),
            "pols_maturity": (0.23961232655772075, 0.23961232655772075, (
                0.0, 0.0, 0.0, 0.0, 0.23961232655772075)),
            "pols_if_aft_decr": (152.5763374171042, 0.991067369478997, (
                0.991067369478997, 0.641218973674823, 0.47998345223022715,
                0.3482991264638735, 0.0)),
            "ci_rate": (1.8970291755310917, 0.01558251932392911, (
                0.0015, 0.0027464013582652945, 0.005003515054281687, 0.009180679516527256,
                0.01558251932392911)),
            "mort_rate": (1.042696032406785, 0.009028804514474343, (
                0.0009, 0.0015324522979124205, 0.002679011690755323, 0.004891158657635536,
                0.009028804514474343)),
            "claim_rate": (2.8354556046971986, 0.02370844338695602, (
                0.00231, 0.004125608426386473, 0.0074146255759614775, 0.013582722308399239,
                0.02370844338695602)),
            "claim_rate_mth": (0.2377876345820149, 0.0019975032580907826, (
                0.00019270411067118243, 0.00034445251496728613, 0.0006199952692421684,
                0.0011390017926065088, 0.0019975032580907826)),
            "lapse_rate": (13.920000000000002, 0.1, (
                0.1, 0.04, 0.04, 0.04, 0.04)),
        },
    },
    5: {"rows": 300, "months": (0, 74, 149, 224, 299),
        "result_cf": {
            "pols_if": (153.57633741710418, 1.0, (
                1.0, 0.6436257064073656, 0.4819178429493733, 0.34988451860438363,
                0.24091005429258047)),
            "premiums": (8446.698557940732, 55.0, (
                55.0, 35.39941385240511, 26.50548136221553, 19.2436485232411,
                13.250052986091926)),
            "claims_main": (9431.877318394943, 51.06765150137514, (
                19.270411067118243, 22.169849326961323, 29.87867827920017,
                39.85190938956583, 48.12186183562568)),
            "claims_ap": (235.35640506943912, 1.2449333047465951, (
                0.46874999999999994, 0.5523920357161402, 0.7535259944137959,
                1.003805510344145, 1.1731204926071708)),
            "claims_child": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_lapse": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claim_expenses": (23.579693295987358, 0.12766912875343786, (
                0.04817602766779561, 0.055424623317403304, 0.07469669569800043,
                0.09962977347391458, 0.1203046545890642)),
            "expenses": (717.1807498238388, 202.5, (
                202.5, 1.9213068821020372, 1.7177490278762404, 1.4891374302202778,
                1.2243013463825339)),
            "net_cf": (-1961.2956086434776, 167.28733709478604, (
                -167.28733709478604, 10.700440984308209, -5.919168634972676,
                -23.20083358036307, -37.38953534311251)),
        },
        "result_pols": {
            "pols_if": (153.57633741710418, 1.0, (
                1.0, 0.6436257064073656, 0.4819178429493733, 0.34988451860438363,
                0.24091005429258047)),
            "pols_new_biz": (1.0, 1.0, (
                1.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_claim": (0.09431877318394945, 0.0005106765150137514, (
                0.00019270411067118243, 0.00022169849326961322, 0.00029878678279200173,
                0.00039851909389565835, 0.0004812186183562568)),
            "pols_lapse": (0.6660689002583297, 0.008739926410331863, (
                0.008739926410331863, 0.0021850342392730443, 0.001635603936354174,
                0.0011868730466144933, 0.0008165091165034733)),
            "pols_maturity": (0.23961232655772075, 0.23961232655772075, (
                0.0, 0.0, 0.0, 0.0, 0.23961232655772075)),
            "pols_if_aft_decr": (152.5763374171042, 0.991067369478997, (
                0.991067369478997, 0.641218973674823, 0.47998345223022715,
                0.3482991264638735, 0.0)),
            "ci_rate": (1.8970291755310917, 0.01558251932392911, (
                0.0015, 0.0027464013582652945, 0.005003515054281687, 0.009180679516527256,
                0.01558251932392911)),
            "mort_rate": (1.042696032406785, 0.009028804514474343, (
                0.0009, 0.0015324522979124205, 0.002679011690755323, 0.004891158657635536,
                0.009028804514474343)),
            "claim_rate": (2.8354556046971986, 0.02370844338695602, (
                0.00231, 0.004125608426386473, 0.0074146255759614775, 0.013582722308399239,
                0.02370844338695602)),
            "claim_rate_mth": (0.2377876345820149, 0.0019975032580907826, (
                0.00019270411067118243, 0.00034445251496728613, 0.0006199952692421684,
                0.0011390017926065088, 0.0019975032580907826)),
            "lapse_rate": (13.920000000000002, 0.1, (
                0.1, 0.04, 0.04, 0.04, 0.04)),
        },
    },
    6: {"rows": 240, "months": (0, 59, 119, 179, 239),
        "result_cf": {
            "pols_if": (129.1575369356319, 1.0, (
                1.0, 0.6672558305176624, 0.5119830128768998, 0.3782465702996678,
                0.263370414833071)),
            "premiums": (12269.96600888503, 95.0, (
                95.0, 63.389303899177925, 48.63838622330549, 35.93342417846844,
                25.020189409141746)),
            "claims_main": (23463.942479994614, 134.2434877827501, (
                74.20469143535335, 71.89481792786779, 93.52164580711299, 112.48277501503598,
                124.88662494099839)),
            "claims_ap": (411.3691706389516, 2.2918892927325643, (
                1.298828125, 1.2622345042735843, 1.664783096780903, 1.9747877775072775,
                2.132143042729862)),
            "claims_child": (107.63128077969324, 0.8333333333333334, (
                0.8333333333333334, 0.5560465254313853, 0.4266525107307499,
                0.3152054752497232, 0.21947534569422583)),
            "claims_lapse": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claim_expenses": (39.106570799991026, 0.2237391463045835, (
                0.12367448572558892, 0.11982469654644631, 0.15586940967852167,
                0.18747129169172666, 0.208144374901664)),
            "expenses": (608.6218648384566, 202.5, (
                202.5, 1.87750578942874, 1.6700542644447047, 1.4303296892424107,
                1.154554041528043)),
            "net_cf": (-12360.705358166677, 183.96052737941227, (
                -183.96052737941227, -12.321125544370016, -48.80061886544239,
                -80.45714507025868, -103.58075233671043)),
        },
        "result_pols": {
            "pols_if": (129.1575369356319, 1.0, (
                1.0, 0.6672558305176624, 0.5119830128768998, 0.3782465702996678,
                0.263370414833071)),
            "pols_new_biz": (1.0, 1.0, (
                1.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_claim": (0.1564262831999641, 0.000894956585218334, (
                0.0004946979429023557, 0.0004792987861857853, 0.0006234776387140866,
                0.0007498851667669066, 0.000832577499606656)),
            "pols_lapse": (0.5819274719288847, 0.00873728649773978, (
                0.00873728649773978, 0.003429240258653384, 0.001736604185442637,
                0.0012819988251263628, 0.0008915924623132094)),
            "pols_maturity": (0.2616462448711512, 0.2616462448711512, (
                0.0, 0.0, 0.0, 0.0, 0.2616462448711512)),
            "pols_if_aft_decr": (128.1575369356319, 0.9907680155593579, (
                0.9907680155593579, 0.6633472914728231, 0.5096229310527431,
                0.37621468630777455, 0.0)),
            "ci_rate": (2.9683440692406595, 0.025905938376032143, (
                0.00415625, 0.006053375975061717, 0.010405239579657256,
                0.016706882188030875, 0.025905938376032143)),
            "mort_rate": (1.3688540033191021, 0.01264032632026408, (
                0.00196, 0.0028137906842999366, 0.00456724777040235, 0.0075841957921584475,
                0.01264032632026408)),
            "claim_rate": (4.200312672227851, 0.03728223206426982, (
                0.00592025, 0.00858578759093166, 0.014515762573019373, 0.023532658400973478,
                0.03728223206426982)),
            "claim_rate_mth": (0.3537243783232418, 0.0031612415545396733, (
                0.0004946979429023557, 0.0007183133728692059, 0.001217770166261345,
                0.001982529983478254, 0.0031612415545396733)),
            "lapse_rate": (11.520000000000003, 0.1, (
                0.1, 0.06, 0.04, 0.04, 0.04)),
        },
    },
    7: {"rows": 300, "months": (0, 74, 149, 224, 299),
        "result_cf": {
            "pols_if": (148.06938927489063, 1.0, (
                1.0, 0.6351611748490824, 0.46409067258143016, 0.3217782720595449,
                0.20353714362534342)),
            "premiums": (12215.724615178477, 82.5, (
                82.5, 52.4007969250493, 38.28748048796799, 26.546707444912453,
                16.79181434909083)),
            "claims_main": (15113.413721971541, 75.23898879231172, (
                32.91800835207859, 37.51769571248553, 48.86522055652616, 62.99384390411918,
                69.78841423629392)),
            "claims_ap": (220.23120810276254, 1.0685405088499063, (
                0.46874999999999994, 0.5451273479134062, 0.7256514583790309,
                0.9231697472376869, 0.9911317105247652)),
            "claims_child": (123.39115772907553, 0.8333333333333334, (
                0.8333333333333334, 0.529300979040902, 0.38674222715119183,
                0.2681485600496208, 0.16961428635445286)),
            "claims_lapse": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claim_expenses": (37.78353430492886, 0.18809747198077928, (
                0.08229502088019647, 0.09379423928121383, 0.1221630513913154,
                0.15748460976029796, 0.1744710355907348)),
            "expenses": (694.5380247539917, 202.5, (
                202.5, 1.8960391487365116, 1.6542058222918492, 1.3695149218570446,
                1.0343727650184573)),
            "net_cf": (-3973.633031683824, 154.3023867062921, (
                -154.3023867062921, 11.818839497591735, -13.466502627771558,
                -39.16545429811138, -55.3661896846915)),
        },
        "result_pols": {
            "pols_if": (148.06938927489063, 1.0, (
                1.0, 0.6351611748490824, 0.46409067258143016, 0.3217782720595449,
                0.20353714362534342)),
            "pols_new_biz": (1.0, 1.0, (
                1.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_claim": (0.15113413721971541, 0.0007523898879231171, (
                0.00032918008352078587, 0.00037517695712485535, 0.0004886522055652615,
                0.0006299384390411918, 0.0006978841423629392)),
            "pols_lapse": (0.646715456213337, 0.008738733390472549, (
                0.008738733390472549, 0.0021557670187690573, 0.0015744171243220993,
                0.001090636825718955, 0.0006888529160332447)),
            "pols_maturity": (0.20215040656694724, 0.20215040656694724, (
                0.0, 0.0, 0.0, 0.0, 0.20215040656694724)),
            "pols_if_aft_decr": (147.06938927489063, 0.9909320865260066, (
                0.9909320865260066, 0.6326302308731885, 0.4620276032515428,
                0.32005769679478474, 0.0)),
            "ci_rate": (1.8970291755310917, 0.01558251932392911, (
                0.0015, 0.0027464013582652945, 0.005003515054281687, 0.009180679516527256,
                0.01558251932392911)),
            "mort_rate": (1.042696032406785, 0.009028804514474343, (
                0.0009, 0.0015324522979124205, 0.002679011690755323, 0.004891158657635536,
                0.009028804514474343)),
            "claim_rate": (4.837598017895457, 0.04037823227455328, (
                0.003943017114988234, 0.007065176834078812, 0.01256217332772458,
                0.023240841276940594, 0.04037823227455328)),
            "claim_rate_mth": (0.40753131054938363, 0.0034287802704333625, (
                0.00032918008352078587, 0.0005906799281520936, 0.0010529239961820647,
                0.001957678605858826, 0.0034287802704333625)),
            "lapse_rate": (13.920000000000002, 0.1, (
                0.1, 0.04, 0.04, 0.04, 0.04)),
        },
    },
    8: {"rows": 264, "months": (0, 65, 131, 197, 263),
        "result_cf": {
            "pols_if": (122.18597379197513, 0.7723710454023793, (
                0.7723710454023793, 0.5812674408209827, 0.4479130993662145,
                0.33568140501907456, 0.24091005429258047)),
            "premiums": (11576.682173983596, 48.47720201192177, (
                48.47720201192177, 45.464143109741734, 43.65844156303087, 42.60881854534883,
                38.107335689323335)),
            "claims_main": (14023.677716863203, 103.81002100276918, (
                21.790875801980793, 30.547476670015346, 45.431241622358, 73.71420130213613,
                97.8218371313617)),
            "claims_ap": (219.09946726750914, 1.2449333047465951, (
                0.4918996517743304, 0.6020575638681371, 0.7832972574151731,
                1.0541709936778862, 1.1731204926071708)),
            "claims_child": (101.82164482664594, 0.6436425378353161, (
                0.6436425378353161, 0.4843895340174856, 0.3732609161385121,
                0.2797345041825621, 0.2007583785771504)),
            "claims_lapse": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claim_expenses": (21.916762273821465, 0.12766912875343786, (
                0.04985434560045828, 0.06028615042074907, 0.07734116215074627,
                0.10509544745052403, 0.1203046545890642)),
            "expenses": (399.4282098449831, 1.9309276135059483, (
                1.9309276135059483, 1.684620685946187, 1.5048943769026175,
                1.346675280299593, 1.1204091656768194)),
            "net_cf": (-3189.2616270925664, 66.1445824452485, (
                23.570002061224923, 12.08531250547383, -4.511593771934179,
                -33.89105898239786, -62.32909413348857)),
        },
        "result_pols": {
            "pols_if": (122.18597379197513, 0.7723710454023793, (
                0.7723710454023793, 0.5812674408209827, 0.4479130993662145,
                0.33568140501907456, 0.24091005429258047)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_claim": (0.08766704909528586, 0.0005106765150137514, (
                0.00019941738240183315, 0.00024114460168299628, 0.0003093646486029851,
                0.0004203817898020961, 0.0004812186183562568)),
            "pols_lapse": (0.4450916697493724, 0.003971288591276359, (
                0.003971288591276359, 0.001973196211930774, 0.001520086095135191,
                0.001138564270410145, 0.0008165091165034733)),
            "pols_maturity": (0.23961232655772075, 0.23961232655772075, (
                0.0, 0.0, 0.0, 0.0, 0.23961232655772075)),
            "pols_if_aft_decr": (121.41360274657275, 0.7682003394287011, (
                0.7682003394287011, 0.5790531000073689, 0.4460836486224763,
                0.33412245895886233, 0.0)),
            "ci_rate": (1.8370123236680875, 0.01558251932392911, (
                0.002037982774014807, 0.0033144540173399867, 0.005596065904916064,
                0.010049252443928345, 0.01558251932392911)),
            "mort_rate": (1.0072104613829302, 0.009028804514474343, (
                0.0011732047838365091, 0.001836135903305451, 0.0029563140867694495,
                0.005417282708684606, 0.009028804514474343)),
            "claim_rate": (2.743501738912724, 0.02370844338695602, (
                0.0030938670794676652, 0.004966976330314893, 0.008256748583008568,
                0.01492480688174449, 0.02370844338695602)),
            "claim_rate_mth": (0.23011576998474537, 0.0019975032580907826, (
                0.00025818857864867706, 0.0004148599848331491, 0.0006906800650410272,
                0.0012523237317187963, 0.0019975032580907826)),
            "lapse_rate": (11.04, 0.06, (
                0.06, 0.04, 0.04, 0.04, 0.04)),
        },
    },
    9: {"rows": 240, "months": (0, 59, 119, 179, 239),
        "result_cf": {
            "pols_if": (104.75707895764418, 0.6780351474260894, (
                0.6780351474260894, 0.5424326102548538, 0.4260764105699448,
                0.3264356576137959, 0.24091005429258047)),
            "premiums": (5761.639342670429, 37.29193310843492, (
                37.29193310843492, 29.833793564016958, 23.434202581346963,
                17.953961168758774, 13.250052986091926)),
            "claims_main": (8294.388962669887, 51.06765150137514, (
                21.28180187017499, 24.6972055950223, 32.78607527272783, 40.88031209089882,
                48.12186183562568)),
            "claims_ap": (207.42197458322195, 1.2449333047465951, (
                0.5297149589266323, 0.6172083704899902, 0.8333509645151664,
                1.0251357281439986, 1.1731204926071708)),
            "claims_child": (87.29756579803683, 0.5650292895217411, (
                0.5650292895217411, 0.4520271752123782, 0.355063675474954,
                0.2720297146781633, 0.2007583785771504)),
            "claims_lapse": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claim_expenses": (20.735972406674716, 0.12766912875343786, (
                0.053204504675437476, 0.061743013987555745, 0.08196518818181957,
                0.10220078022724705, 0.1203046545890642)),
            "expenses": (334.8323703628872, 1.6950878685652235, (
                1.6950878685652235, 1.526281704182836, 1.3898326869347084,
                1.2344080538323727, 1.0560930961229327)),
            "net_cf": (-3183.0375031502776, 39.71288612725425, (
                13.167094616570889, 2.479327705121896, -12.012085206487514,
                -25.560125199021826, -37.42208547143008)),
        },
        "result_pols": {
            "pols_if": (104.75707895764418, 0.6780351474260894, (
                0.6780351474260894, 0.5424326102548538, 0.4260764105699448,
                0.3264356576137959, 0.24091005429258047)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_claim": (0.08294388962669887, 0.0005106765150137514, (
                0.00021281801870174993, 0.000246972055950223, 0.00032786075272727826,
                0.0004088031209089882, 0.0004812186183562568)),
            "pols_lapse": (0.3554789312416694, 0.0023019206900817104, (
                0.0023019206900817104, 0.0018412912710125445, 0.0014458647245412732,
                0.0011072045421335983, 0.0008165091165034733)),
            "pols_maturity": (0.23961232655772075, 0.23961232655772075, (
                0.0, 0.0, 0.0, 0.0, 0.23961232655772075)),
            "pols_if_aft_decr": (104.07904381021811, 0.6755204087173059, (
                0.6755204087173059, 0.540344346927891, 0.4243026850926762,
                0.32491964995075334, 0.0)),
            "ci_rate": (1.7854701168364868, 0.01558251932392911, (
                0.0025, 0.003641128406052161, 0.006258790724605869, 0.010049252443928345,
                0.01558251932392911)),
            "mort_rate": (0.9777528595136445, 0.009028804514474343, (
                0.0014, 0.002009850488785669, 0.0032623198360016785, 0.005417282708684606,
                0.009028804514474343)),
            "claim_rate": (2.6654476903987674, 0.02370844338695602, (
                0.0037600000000000003, 0.005449993845959263, 0.00919487857700738,
                0.01492480688174449, 0.02370844338695602)),
            "claim_rate_mth": (0.22360152689405322, 0.0019975032580907826, (
                0.00031387461182452725, 0.00045530458766884774, 0.0007694881589166425,
                0.0012523237317187963, 0.0019975032580907826)),
            "lapse_rate": (9.6, 0.04, (
                0.04, 0.04, 0.04, 0.04, 0.04)),
        },
    },
    10: {"rows": 234, "months": (0, 58, 116, 174, 233),
        "result_cf": {
            "pols_if": (100.72640313545782, 0.6630859275352214, (
                0.6630859275352214, 0.5319768466439516, 0.42070334845396085,
                0.32491964995075334, 0.24091005429258047)),
            "premiums": (5539.952172450179, 36.46972601443718, (
                36.46972601443718, 29.25872656541734, 23.138684164967845,
                17.870580747291434, 13.250052986091926)),
            "claims_main": (8167.876281761963, 51.06765150137514, (
                20.812583811142424, 26.58311832579566, 36.06962042531498,
                44.743007897049786, 48.12186183562568)),
            "claims_ap": (204.27300909713887, 1.2449333047465951, (
                0.5180358808868918, 0.6649710583049395, 0.9202885747430394,
                1.1169112967057144, 1.1731204926071708)),
            "claims_child": (83.93866927954818, 0.5525716062793512, (
                0.5525716062793512, 0.4433140388699597, 0.35058612371163406,
                0.2707663749589611, 0.2007583785771504)),
            "claims_lapse": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claim_expenses": (20.419690704404907, 0.12766912875343786, (
                0.05203145952785606, 0.06645779581448914, 0.09017405106328745,
                0.11185751974262446, 0.1203046545890642)),
            "expenses": (320.1104902595401, 1.6577148188380537, (
                1.6577148188380537, 1.4968615690344664, 1.372306118524747,
                1.2286753097975731, 1.0560930961229327)),
            "net_cf": (-3256.665968652413, 39.68024315486221, (
                12.876788437762603, 0.004003777597825886, -15.664291128389847,
                -29.600637650963225, -37.42208547143008)),
        },
        "result_pols": {
            "pols_if": (100.72640313545782, 0.6630859275352214, (
                0.6630859275352214, 0.5319768466439516, 0.42070334845396085,
                0.32491964995075334, 0.24091005429258047)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_claim": (0.08167876281761961, 0.0005106765150137514, (
                0.00020812583811142423, 0.00026583118325795656, 0.0003606962042531498,
                0.00044743007897049786, 0.0004812186183562568)),
            "pols_lapse": (0.34179483815988077, 0.0022511682789449097, (
                0.0022511682789449097, 0.0018057188949549925, 0.001427506008814111,
                0.0011019249202554495, 0.0008165091165034733)),
            "pols_maturity": (0.23961232655772075, 0.23961232655772075, (
                0.0, 0.0, 0.0, 0.0, 0.23961232655772075)),
            "pols_if_aft_decr": (100.06331720792261, 0.6606266334181651, (
                0.6606266334181651, 0.5299052965657387, 0.4189151462408936,
                0.32337029495152736, 0.0)),
            "ci_rate": (1.770470116836487, 0.01558251932392911, (
                0.0025, 0.004, 0.007, 0.011, 0.01558251932392911)),
            "mort_rate": (0.9693528595136445, 0.009028804514474343, (
                0.0014, 0.0022, 0.0036, 0.006, 0.009028804514474343)),
            "claim_rate": (2.6428876903987675, 0.02370844338695602, (
                0.0037600000000000003, 0.00598, 0.010239999999999999, 0.016399999999999998,
                0.02370844338695602)),
            "claim_rate_mth": (0.22171827922310605, 0.0019975032580907826, (
                0.00031387461182452725, 0.0004997044231059844, 0.0008573647097858128,
                0.0013770483842338033, 0.0019975032580907826)),
            "lapse_rate": (9.36, 0.04, (
                0.04, 0.04, 0.04, 0.04, 0.04)),
        },
    },
    11: {"rows": 222, "months": (0, 55, 110, 165, 221),
        "result_cf": {
            "pols_if": (92.92998889277195, 0.6340526384863423, (
                0.6340526384863423, 0.5135914438079662, 0.41008750256023563,
                0.32029371367361686, 0.24091005429258047)),
            "premiums": (5111.149389102457, 34.87289511674883, (
                34.87289511674883, 28.24752940943814, 22.55481264081296, 17.61615425204893,
                13.250052986091926)),
            "claims_main": (7911.380054938415, 51.06765150137514, (
                21.840102594826412, 28.58591863854633, 35.15945526193452, 44.10599408944985,
                48.12186183562568)),
            "claims_ap": (197.88525415865752, 1.2449333047465951, (
                0.5441759461095576, 0.7180181174060103, 0.8970664118505154,
                1.1010096407530578, 1.1731204926071708)),
            "claims_child": (77.4416574106433, 0.5283771987386187, (
                0.5283771987386187, 0.4279928698399718, 0.34173958546686306,
                0.2669114280613474, 0.2007583785771504)),
            "claims_lapse": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claim_expenses": (19.778450137346034, 0.12766912875343786, (
                0.05460025648706602, 0.07146479659636583, 0.0878986381548363,
                0.11026498522362463, 0.1203046545890642)),
            "expenses": (291.8635482066266, 1.5851315962158559, (
                1.5851315962158559, 1.445129236866215, 1.3376779409102557,
                1.1759052918407722, 1.0253331030319734)),
            "net_cf": (-3387.1995757492314, 39.64855094865635, (
                10.320507524371319, -3.000994249816755, -15.26902519750403,
                -29.143931183279726, -37.39132547833912)),
        },
        "result_pols": {
            "pols_if": (92.92998889277195, 0.6340526384863423, (
                0.6340526384863423, 0.5135914438079662, 0.41008750256023563,
                0.32029371367361686, 0.24091005429258047)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_claim": (0.07911380054938415, 0.0005106765150137514, (
                0.00021840102594826408, 0.0002858591863854633, 0.0003515945526193452,
                0.00044105994089449854, 0.0004812186183562568)),
            "pols_lapse": (0.3153265113792372, 0.002152534789710843, (
                0.002152534789710843, 0.001743213072676367, 0.001391484941100656,
                0.0010862366278912821, 0.0008165091165034733)),
            "pols_maturity": (0.23961232655772075, 0.23961232655772075, (
                0.0, 0.0, 0.0, 0.0, 0.23961232655772075)),
            "pols_if_aft_decr": (92.2959362542856, 0.6316817026706831, (
                0.6316817026706831, 0.5115623715489044, 0.40834442306651564,
                0.3187664171048311, 0.0)),
            "ci_rate": (1.7389917086868953, 0.01558251932392911, (
                0.0027464013582652945, 0.004473707658880579, 0.007, 0.011,
                0.01558251932392911)),
            "mort_rate": (0.9517581457261697, 0.009028804514474343, (
                0.0015324522979124205, 0.0024277202721198566, 0.0036, 0.006,
                0.009028804514474343)),
            "claim_rate": (2.5955740398404488, 0.02370844338695602, (
                0.004125608426386473, 0.00665865590378845, 0.010239999999999999,
                0.016399999999999998, 0.02370844338695602)),
            "claim_rate_mth": (0.21776831646235517, 0.0019975032580907826, (
                0.00034445251496728613, 0.0005565886850956714, 0.0008573647097858128,
                0.0013770483842338033, 0.0019975032580907826)),
            "lapse_rate": (8.879999999999999, 0.04, (
                0.04, 0.04, 0.04, 0.04, 0.04)),
        },
    },
    12: {"rows": 1, "months": (0,),
        "result_cf": {
            "pols_if": (0.24091005429258047, 0.24091005429258047, (
                0.24091005429258047,)),
            "premiums": (13.250052986091926, 13.250052986091926, (
                13.250052986091926,)),
            "claims_main": (48.12186183562568, 48.12186183562568, (
                48.12186183562568,)),
            "claims_ap": (1.1731204926071708, 1.1731204926071708, (
                1.1731204926071708,)),
            "claims_child": (0.2007583785771504, 0.2007583785771504, (
                0.2007583785771504,)),
            "claims_lapse": (0.0, 0.0, (
                0.0,)),
            "claim_expenses": (0.1203046545890642, 0.1203046545890642, (
                0.1203046545890642,)),
            "expenses": (0.6022751357314512, 0.6022751357314512, (
                0.6022751357314512,)),
            "net_cf": (-36.9682675110386, 36.9682675110386, (
                -36.9682675110386,)),
        },
        "result_pols": {
            "pols_if": (0.24091005429258047, 0.24091005429258047, (
                0.24091005429258047,)),
            "pols_new_biz": (0.0, 0.0, (
                0.0,)),
            "pols_claim": (0.0004812186183562568, 0.0004812186183562568, (
                0.0004812186183562568,)),
            "pols_lapse": (0.0008165091165034733, 0.0008165091165034733, (
                0.0008165091165034733,)),
            "pols_maturity": (0.23961232655772075, 0.23961232655772075, (
                0.23961232655772075,)),
            "pols_if_aft_decr": (0.0, 0.0, (
                0.0,)),
            "ci_rate": (0.01558251932392911, 0.01558251932392911, (
                0.01558251932392911,)),
            "mort_rate": (0.009028804514474343, 0.009028804514474343, (
                0.009028804514474343,)),
            "claim_rate": (0.02370844338695602, 0.02370844338695602, (
                0.02370844338695602,)),
            "claim_rate_mth": (0.0019975032580907826, 0.0019975032580907826, (
                0.0019975032580907826,)),
            "lapse_rate": (0.04, 0.04, (
                0.04,)),
        },
    },
    13: {"rows": 313, "months": (0, 78, 156, 234, 312),
        "result_cf": {
            "pols_if": (153.5763374171042, 1.0, (
                0.0, 0.6655543767896098, 0.4936576831195254, 0.3546841250080813,
                0.24091005429258047)),
            "premiums": (13377.390689385371, 55.0, (
                0.0, 45.61710135846566, 44.062363102400305, 43.08217973654864,
                38.107335689323335)),
            "claims_main": (14709.14623053324, 103.81002100276919, (
                0.0, 24.217307479901546, 38.03380238584506, 68.77588744518759,
                97.82183713136172)),
            "claims_ap": (235.35640506943912, 1.2449333047465951, (
                0.0, 0.5199643568668827, 0.6901500493240821, 1.0175754004059638,
                1.1731204926071708)),
            "claims_child": (127.98028118092019, 0.8333333333333334, (
                0.0, 0.5546286473246749, 0.41138140259960454, 0.29557010417340107,
                0.2007583785771504)),
            "claims_lapse": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claim_expenses": (23.579693295987358, 0.12766912875343786, (
                0.0, 0.05222515541573848, 0.06869107018371806, 0.10099646354831891,
                0.1203046545890642)),
            "expenses": (733.9927437701299, 202.575, (
                0.0, 1.9867668301764025, 1.8123823764135314, 1.5548519003300647,
                1.29886129837723)),
            "net_cf": (-2452.664664464347, 168.19567042811934, (
                0.0, 18.286208888780415, 3.0459558180343147, -28.662701577096705,
                -62.507546266188996)),
        },
        "result_pols": {
            "pols_if": (153.5763374171042, 1.0, (
                0.0, 0.6655543767896098, 0.4936576831195254, 0.3546841250080813,
                0.24091005429258047)),
            "pols_new_biz": (1.0, 1.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_claim": (0.09431877318394943, 0.0005106765150137514, (
                0.0, 0.00020890062166295393, 0.00027476428073487224, 0.0004039858541932756,
                0.0004812186183562568)),
            "pols_lapse": (0.6660689002583297, 0.008739926410331863, (
                0.0, 0.002259548632725483, 0.001675554639813757, 0.0012031541998865193,
                0.0008165091165034733)),
            "pols_maturity": (0.23961232655772075, 0.23961232655772075, (
                0.0, 0.0, 0.0, 0.0, 0.23961232655772075)),
            "pols_if_aft_decr": (152.57633741710418, 0.991067369478997, (
                0.0, 0.6630859275352214, 0.49170736419897676, 0.35307698495400147, 0.0)),
            "ci_rate": (1.8970291755310917, 0.01558251932392911, (
                0.0, 0.0025, 0.004473707658880579, 0.009180679516527256,
                0.01558251932392911)),
            "mort_rate": (1.0426960324067853, 0.009028804514474343, (
                0.0, 0.0014, 0.0024277202721198566, 0.004891158657635536,
                0.009028804514474343)),
            "claim_rate": (2.8354556046971986, 0.02370844338695602, (
                0.0, 0.0037600000000000003, 0.00665865590378845, 0.013582722308399239,
                0.02370844338695602)),
            "claim_rate_mth": (0.2377876345820149, 0.0019975032580907826, (
                0.0, 0.00031387461182452725, 0.0005565886850956714, 0.0011390017926065088,
                0.0019975032580907826)),
            "lapse_rate": (13.919999999999998, 0.1, (
                0.0, 0.04, 0.04, 0.04, 0.04)),
        },
    },
    14: {"rows": 176, "months": (0, 43, 87, 131, 175),
        "result_cf": {
            "pols_if": (52.88349600004723, 0.4586414252054156, (
                0.4586414252054156, 0.35823659076068426, 0.29591260187455853,
                0.24025115700022567, 0.19046178708271846)),
            "premiums": (3519.396658803144, 30.522586847420413, (
                30.522586847420413, 23.840645115123543, 19.692983654751874,
                15.988714498365022, 12.675231930354917)),
            "claims_main": (5796.4092233516785, 43.12177914799667, (
                24.456031930241696, 26.426464074934575, 32.75002885093304,
                38.74506214232299, 40.574884237840344)),
            "claims_ap": (149.43027727498637, 1.084245472805485, (
                0.6306319596574465, 0.6891209776856743, 0.8531434592360077,
                0.9910877929863954, 1.0202068517047456)),
            "claims_child": (44.069580000039366, 0.3822011876711797, (
                0.3822011876711797, 0.2985304923005702, 0.24659383489546546,
                0.20020929750018807, 0.1587181559022654)),
            "claims_lapse": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claim_expenses": (14.491023058379193, 0.10780444786999167, (
                0.06114007982560424, 0.06606616018733644, 0.0818750721273326,
                0.09686265535580749, 0.10143721059460085)),
            "expenses": (158.42734714307335, 1.1466035630135392, (
                1.1466035630135392, 0.9786369877803756, 0.909837938738485,
                0.807193662622449, 0.7202263552971551)),
            "net_cf": (-2643.430792025012, 31.754791720532612, (
                3.8459781270109494, -4.6181735777649875, -15.148495501178457,
                -24.851701052422815, -29.900240880984192)),
        },
        "result_pols": {
            "pols_if": (52.88349600004723, 0.4586414252054156, (
                0.4586414252054156, 0.35823659076068426, 0.29591260187455853,
                0.24025115700022567, 0.19046178708271846)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_claim": (0.05796409223351677, 0.0004312177914799667, (
                0.000244560319302417, 0.00026426464074934573, 0.0003275002885093304,
                0.00038745062142322994, 0.00040574884237840346)),
            "pols_lapse": (0.21126673514819888, 0.0057253399355282324, (
                0.0057253399355282324, 0.0012156930632435646, 0.0010038227297936742,
                0.0008145899073519542, 0.0006454404166397048)),
            "pols_maturity": (0.18941059782370037, 0.18941059782370037, (
                0.0, 0.0, 0.0, 0.0, 0.18941059782370037)),
            "pols_if_aft_decr": (52.42485457484182, 0.452671524950585, (
                0.452671524950585, 0.35675663305669136, 0.29458127885625557,
                0.2390491164714505, 0.0)),
            "ci_rate": (1.7455253787810592, 0.01714077125632202, (
                0.0044, 0.006155672495407671, 0.009225896606838443, 0.01320068954986754,
                0.01714077125632202)),
            "mort_rate": (0.8674823662732272, 0.009028804514474343, (
                0.0022, 0.0029563140867694495, 0.004416131536907, 0.006645398059489741,
                0.009028804514474343)),
            "claim_rate": (2.526259508426964, 0.02526669531934893, (
                0.00638, 0.008816355173500176, 0.013200414990054744, 0.019181547803408305,
                0.02526669531934893)),
            "claim_rate_mth": (0.21214640985763067, 0.0021303425143343047, (
                0.0005332277152960696, 0.0007376818771868132, 0.0011067466759937528,
                0.0016126899294094388, 0.0021303425143343047)),
            "lapse_rate": (7.839999999999999, 0.14, (
                0.14, 0.04, 0.04, 0.04, 0.04)),
        },
    },
}
# END generated fingerprint: CI_UK_SEC
