"""In-force tests for PA_UK_SEC: the splice, future business, counts, regeneration.

``PA_UK_SEC`` is ``PA_UK_S`` taught to run in force at a valuation date
(UKLIB-SEC-PLAN.md, milestone M11, after USLIB-SEC-PLAN.md's Phase 1), on the payout
chassis of uslib's ``SPIA_US_SEC``.  It runs on two clocks: ``t`` counts months from the
valuation date, the same month for every model point, and ``duration_mth(t)`` counts the
months from the annuity's start date, ``duration_mth_init() + t``.  A model point may be an
annuity already in payment at the valuation date, in any month of its policy year, one
starting at it, or one to start after it, as in ``basiclife/BasicTerm_SE``.  A contract in
payment opens with its state beside its count, each per contract and measured at the
valuation instant: each covered life's survival, ``lives_if_init_1`` and
``lives_if_init_2``; the payments made to date on every stream, ``cum_annuity_all_init``;
and on RPI-linked escalation the history no flat ``rpi_rate`` re-derives, the income of the
policy year under way before any month-0 anniversary, ``annual_income_init``, the ratchet's
peak over the latest index, ``rpi_peak_init``, and where value protection is on the first
death the annuitant's as-if-alive instalments to date, ``cum_annuity_pp_init``.  The count
on the books is never decremented: mortality decrements each life's survival, and
``pols_if`` is ``PA_UK_S``'s closing obligation measure on that count, so the registry marks
the model ``closing_pols_if``.

The worked example is not restated here.  On a point starting at the valuation date the two
clocks coincide and the model is ``PA_UK_S``, and ``test_model_conventions_uk.py`` asserts
that cell by cell on the twins of S's ten points (T1), so every golden of
``test_pension_annuity_uk.py`` holds on this model with no number copied.  The conventions
also hold the SEC family's other rules: every frame opens at ``t = 0``, ``BEF_DECR`` is
``BEF_NB`` plus the month's new business, new business enters once, and nothing happens
before the start.  This module holds the rest of the plan's tests (its §5) and the
product's own facts:

* T2, the splice: an S point restated in payment at month ``d``, opened with the state S
  carries into ``d``, continues S's projection from ``d`` on, in every cell of S's.  The
  months straddle the product's events: quarterly payments in arrears, the anniversaries,
  the scenario death, the guarantee's end, value protection running out on the first and
  the last death, the mortality cap, the older life past the limiting age and the frame's
  last month.  Twelve variants of S's points, in a copy of S's table, add advance timing
  with value protection, semi-annual and annual payments, the dependant dying first, both
  lives dead with and without a guarantee, a guarantee past the age stop, a rated joint
  life, the proportionate payment on the table basis and the RPI bases without
  first-death value protection; and the RPI points are spliced under RPIs of 8% and -2%,
  where the LPI cap and floor bind and the ratchet freezes.
* T3, future new business: a point starting ``k`` months after the valuation date is S's
  projection ``k`` months on, with zeros before it and no rate evaluated there.
* D11's R1 and R2, and D3's and D5's chains: on the splice's grid no cell is called at a
  negative month, none on the books reads a month before them, none reads beyond
  ``t + 1``, and on an RPI-linked row none asks a year, an anniversary or a policy month
  closed before the valuation date; on the committed points no recursion runs backward
  over the frame; the policy clock is a closed form; and each chain, called cold, runs one
  cell a month back to ``t_entry()``, at each shape's longest cover.
* T4, the count algebra: the count is never decremented, ``BEF_NB`` a closed form;
  multiplying ``policy_count`` by 2.5 multiplies every flow and every counted cell by 2.5
  and moves no per-contract value, each flow nonzero on some point; and a point restated a
  month on, with the state it carries there, continues its own flows.
* T5, validation: each malformed row of the table is refused as it is read, naming its
  point, on the committed labels and on an extract's; each text value no decode knows
  raises ``PA_UK_S``'s message; the mortality table is refused before a value of it is
  read; the future horizon is a Reference; a point at or past its stop, one owing nothing,
  one the contract does not issue and one read under a Reference outside its domain are
  refused by the frame, each domain at both its edges; the edges of the interface are
  accepted; and so is every state ``PA_UK_S`` reaches, on each set of inputs on which those
  states differ, but a contract owing nothing, which is set aside and shown refused.
* T6, regeneration: the committed ``model_point_table_sec.csv`` is what the generator makes
  of ``PA_UK_S`` and its table as they stand.
* Then the product's own facts: the two clocks; the committed rows continuing their S
  points, and the two read from S under an RPI of their own; each history column read
  rather than recomputed (UKLIB-SEC-PLAN.md K14), the ratchet's catch-up among them, with
  goldens of its own; the income measured before month 0's anniversary; the RPI, inflation
  and improvement each on its clock; no premium and no acquisition; the cap on mortality
  and a NaN that reaches it; the checks failing a NaN residual; the values outside the
  frame; the block; an in-force extract; the runner; the docstrings; the shared input
  table; and what the default grid reaches.
* C2, the fingerprint: every committed point computes what the model computed when its E
  step ended, frozen at the end of this module before its C step changed anything
  (USLIB-SEC-PLAN.md §5.4).

SEC month ``t`` is S month ``t + source_mth`` throughout, the direction in which
``uk_sec_support`` takes its ``t_offset``: ``d`` for a point restated at S month ``d``,
``-k`` for one starting ``k`` months on.

**The core grid and the full one** (UKLIB-SEC-PLAN.md U6).  T2 and T3 over every S point at
every month, about 400 cases, run by default on a core, chosen so that between them they
reach every branch, every opening-state column, every kind of valuation month and both
sides of every ``min`` and ``max`` the full grid reaches, which
``test_the_core_grid_reaches_every_branch`` asserts.  The other cases, and the rules test's
scan of their rows, carry the ``sec_full`` marker and are skipped, with the reason shown,
unless ``UKLIB_SEC_FULL=1`` is set.  They are never dropped: one leg of the CI matrix sets
it, and ``UKLIB_SEC_FULL=1 python -m pytest -m sec_full
lifelib/libraries/uklib/tests/test_pension_annuity_uk_sec.py`` runs them alone.  Each
splice row is released once it has been read (``_release``), as ``run_sec.py --block``
releases its points.

Every test keeps four rules.  Each model is read under a name of its own and closed:
``conftest.pension_annuity`` reads S under its default name, and reading a model under a
name in use renames the open one.  No test writes inside the library tree: every changed
input goes through ``uk_sec_support.temp_inputs`` into a temporary directory, because a CSV
added beside the models, even briefly, would fail a concurrent
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
import gc
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

SEC, TWIN = "PA_UK_SEC", "PA_UK_S"
TABLE = "model_point_table_sec.csv"
SPEC = SEC_SPECS[SEC]

# S's ten points, every one starting at the valuation date: the worked example, a joint
# life with a dependant at 50%, quarterly in arrears, fixed 3%, value protection of 50% on
# the first death, on the scenario basis, the annuitant dying in policy month 16 (1); the
# same on the table basis (2); a 120-month guarantee without overlap (3) and with it (4);
# a single life, level, monthly in advance, on the table (5); the RPI catch-up (6) and LPI
# (7) on the table; a single life rated 1.35, level, monthly in arrears (8); the
# proportionate final payment (9); and value protection on the last death (10).
S_POINTS = tuple(range(1, 11))

# Twelve more S points, in the splice's copy of S's table and never in the committed one,
# each one of S's points changed so as to reach what S's own points cannot:
#
# 11, S point 2 in advance: value protection measured after an advance instalment;
# 12, S point 2 paying twice a year, in arrears;
# 13, S point 5 paying once a year, in advance;
# 14, S point 1 with the dependant dying first, in policy month 10, and the annuitant in 40;
# 15, S point 3 with the dependant dying in 30 too: both lives dead inside its guarantee,
#   which pays on to policy month 120, after which nothing is owed;
# 16, S point 1 with the dependant dying in 30: both lives dead without a guarantee, after
#   which nothing is owed;
# 17, S point 5 bought at 90 with a 360-month guarantee: the guarantee past the age stop;
# 18, S point 2 rated, the annuitant at 1.3 and the dependant at 1.5;
# 19, S point 2 with the proportionate final payment, on the table basis, where it is paid
#   in every month a life can die;
# 20, S point 10 in advance: last-survivor value protection measured after an advance
#   instalment;
# 21, S point 6 without value protection: RPI-linked, so the annuitant's payments to date
#   are read nowhere;
# 22, S point 7 with value protection on the last death: RPI-linked, the annuitant's
#   payments to date read nowhere either.
#
# Each variant is (the S point it changes, the columns it changes); the policy_id keeps the
# generated ids apart.
VARIANTS = {
    11: (2, {"policy_id": "PA-900011", "timing": "advance"}),
    12: (2, {"policy_id": "PA-900012", "frequency": 2}),
    13: (5, {"policy_id": "PA-900013", "frequency": 1}),
    14: (1, {"policy_id": "PA-900014", "death_mth_1": 40.0, "death_mth_2": 10.0}),
    15: (3, {"policy_id": "PA-900015", "death_mth_2": 30.0}),
    16: (1, {"policy_id": "PA-900016", "death_mth_2": 30.0}),
    17: (5, {"policy_id": "PA-900017", "annuitant_age": 90, "guarantee_months": 360}),
    18: (2, {"policy_id": "PA-900018", "rating_multiplier": 1.3, "dependant_rating": 1.5}),
    19: (2, {"policy_id": "PA-900019", "proportion": True}),
    20: (10, {"policy_id": "PA-900020", "timing": "advance"}),
    21: (6, {"policy_id": "PA-900021", "vp_pct": 0.0}),
    22: (7, {"policy_id": "PA-900022", "vp_basis": "last_survivor"}),
}

# Each point's frame from its start, in months: the age stop on its youngest life, or the
# guarantee if longer.
FRAME = {**{p: 636 for p in (1, 2, 3, 4, 6, 7, 9, 10)}, 5: 600, 8: 600,
         **{p: 636 for p in (11, 12, 14, 15, 16, 18, 19, 20, 21, 22)}, 13: 600, 17: 360}

# The first S month from which a point owes nothing, every covered life dead and no
# guarantee left, so that proj_len() refuses it restated there or later: S point 8, whose
# rated life the cap kills in policy month 576, and variants 14, 15 and 16 once both their
# lives have died (measured at M11).  The splice leaves those months out, and the
# every-state test sets them aside and shows them refused.
OWES_NOTHING_FROM = {8: 577, 14: 41, 15: 120, 16: 31}

# T2's months (UKLIB-SEC-PLAN.md §6.7): 1, 2 and 3, about the first quarterly payment in
# arrears; 11 to 13 and 23 to 25, about the first two anniversaries; 15 to 17, about the
# scenario death in policy month 16, value protection and the proportionate payment in it
# and the dependant's first instalment after it; 101 and 102, where first-death value
# protection runs out; 119 to 122, about the guarantee's end; 170 and 171, where
# last-survivor value protection runs out; 575 and 576, where point 8's mortality cap first
# binds; 599 and 600, where the older life reaches the limiting age; and 635, the joint
# frames' last month.  A month at or past a point's frame, or from the one it owes nothing
# (OWES_NOTHING_FROM), is left out.  Each variant's months straddle its own events: the
# advance balance's last month, 99, and run-out, 100; the first semi-annual payments; the
# annual instalment's anniversary; each death; the age stop at 300 inside the guarantee;
# the rated annuitant's cap from 576; and the advance last-survivor balance's run-out at
# 166.
SPLICE_MTHS = (1, 2, 3, 11, 12, 13, 15, 16, 17, 23, 24, 25, 101, 102, 119, 120, 121, 122,
               170, 171, 575, 576, 599, 600, 635)
VARIANT_MTHS = {11: (2, 3, 99, 100), 12: (1, 5, 6, 101), 13: (1, 12, 13, 599),
                14: (9, 10, 11, 39, 40), 15: (16, 29, 30, 31, 119),
                16: (16, 17, 29, 30), 17: (1, 299, 300, 359), 18: (1, 24, 575, 576),
                19: (1, 2, 24), 20: (1, 2, 16, 17, 165, 166), 21: (12, 24), 22: (12, 24)}


def _owes(s_point, month):
    """Whether S point ``s_point`` restated at ``month`` owes something: inside its frame,
    before the month it owes nothing from."""
    return month < min(FRAME[s_point], OWES_NOTHING_FROM.get(s_point, FRAME[s_point]))

# The splice's three sets of References, each set in both models before either evaluates
# anything.  Expense inflation is the one input PA reads on the valuation clock (D7): S
# inflates from the start and SEC from the valuation date, so at the shipped 3% the expenses
# of a point opened at d differ by 1.03^(d // 12), by design, and at 0 both factors are 1.
# The clock itself is asserted on its own, at the shipped rate.  Improvement is dated by the
# calendar on the policy clock in both, and so is left at its shipped scale (D7, precised at
# M11).  rpi_rate is a flat Reference, the RPI on either clock, so the RPI sets run S and
# SEC at one rate: 8%, past the LPI's 5% cap, and -2%, below its floor, where the catch-up's
# index falls and the ratchet freezes the income.  Nothing else ships at 0 to switch on.
SPLICE_SETS = {
    "shipped": {"inflation_rate": 0.0},
    "rpi_high": {"inflation_rate": 0.0, "rpi_rate": 0.08},
    "rpi_low": {"inflation_rate": 0.0, "rpi_rate": -0.02},
}

# The RPI points, spliced under each RPI set at its anniversaries, the month before and
# after each, and the sixth: S's two RPI points and the variants that move their value
# protection.
RPI_POINTS = (6, 7, 21, 22)
RPI_MTHS = (11, 12, 13, 23, 24, 25, 60, 61)

# T2's cases, as (set, row_kind, S point, source_mth): each S point restated in payment at
# each of its months inside its frame, then each variant at its own, then the RPI points
# under the RPI sets.  PA_UK_S has no point in payment, so no twin is a splice case.  T3's
# cases, as (set, S point, k).
SPLICES = (tuple(("shipped", "derived", p, d) for p in S_POINTS for d in SPLICE_MTHS
                 if _owes(p, d))
           + tuple(("shipped", "derived", p, d) for p, mths in VARIANT_MTHS.items()
                   for d in mths if _owes(p, d))
           + tuple((rates, "derived", p, d) for rates in ("rpi_high", "rpi_low")
                   for p in RPI_POINTS for d in RPI_MTHS))
IN_FORCE_TWINS = ()
FUTURES = (tuple(("shipped", p, k) for p in S_POINTS for k in (1, 12))
           + tuple(("shipped", p, 1) for p in VARIANTS)
           + (("shipped", 6, 13), ("shipped", 1, 25))
           + tuple((rates, p, k) for rates in ("rpi_high", "rpi_low") for p in (6, 7)
                   for k in (1, 13)))

# The default run's cases (the module docstring), each with what it is there for.  The rest
# of SPLICES and FUTURES run with UKLIB_SEC_FULL=1.
CORE_SPLICES = {
    ("shipped", "derived", 1, 1): "the worked example in its second month",
    ("shipped", "derived", 1, 2): "the worked example in its first payment month",
    ("shipped", "derived", 1, 12): "the worked example on its first anniversary",
    ("shipped", "derived", 1, 16): "the worked example in the month of the death",
    ("shipped", "derived", 1, 17): "the dependant's first instalment",
    ("shipped", "derived", 9, 16): "value protection and the proportionate payment",
    ("shipped", "derived", 3, 119): "the guarantee's last month, without overlap",
    ("shipped", "derived", 3, 120): "the guarantee ended, the dependant's income starting",
    ("shipped", "derived", 4, 119): "the guarantee's last month, the dependant paid beside "
                                    "it",
    ("shipped", "derived", 2, 13): "the table basis after its first anniversary",
    ("shipped", "derived", 2, 101): "first-death value protection's last balance",
    ("shipped", "derived", 2, 102): "first-death value protection run out",
    ("shipped", "derived", 10, 171): "last-survivor value protection run out",
    ("shipped", "derived", 8, 575): "the month before the rated life's cap binds",
    ("shipped", "derived", 8, 576): "the rated life's cap binding",
    ("shipped", "derived", 2, 600): "the older life past the limiting age",
    ("shipped", "derived", 2, 635): "the joint frame's last month",
    ("shipped", "derived", 5, 120): "the single life, monthly in advance",
    ("shipped", "derived", 6, 25): "the RPI catch-up after an anniversary",
    ("shipped", "derived", 7, 23): "the LPI before an anniversary",
    ("shipped", "derived", 11, 3): "advance value protection, the instalment netted",
    ("shipped", "derived", 12, 5): "semi-annual payments in arrears",
    ("shipped", "derived", 13, 12): "an annual instalment in advance",
    ("shipped", "derived", 14, 11): "the dependant dead first",
    ("shipped", "derived", 14, 40): "the annuitant dying after the dependant",
    ("shipped", "derived", 15, 31): "both lives dead inside the guarantee",
    ("shipped", "derived", 16, 30): "both lives dying without a guarantee",
    ("shipped", "derived", 17, 300): "the guarantee past the age stop",
    ("shipped", "derived", 18, 24): "a rated joint life",
    ("shipped", "derived", 19, 2): "the proportionate payment on the table basis",
    ("shipped", "derived", 20, 16): "last-survivor value protection in advance",
    ("shipped", "derived", 21, 24): "the RPI catch-up without value protection",
    ("shipped", "derived", 22, 12): "the LPI with last-survivor value protection",
    ("rpi_high", "derived", 7, 24): "the LPI cap binding, its history capped",
    ("rpi_high", "derived", 6, 13): "the catch-up's index rising past its peak",
    ("rpi_low", "derived", 6, 24): "the ratchet frozen, its peak above the index",
    ("rpi_low", "derived", 7, 25): "the LPI floor binding",
    ("rpi_low", "derived", 21, 61): "the ratchet frozen, no value protection",
}
CORE_FUTURES = {
    ("shipped", 1, 1): "starting a month off the valuation anniversaries",
    ("shipped", 1, 12): "starting on them, a year on, the block's",
    ("shipped", 5, 1): "the single life in advance",
    ("shipped", 6, 13): "the RPI catch-up, more than a year on",
    ("shipped", 1, 25): "the worked example, more than two years on",
    ("shipped", 17, 1): "the guarantee past the age stop",
    ("rpi_low", 7, 13): "the LPI floor, more than a year on",
}

SEC_FULL = os.environ.get("UKLIB_SEC_FULL") == "1"
FULL_ONLY = (pytest.mark.sec_full,
             pytest.mark.skipif(not SEC_FULL, reason="the full splice grid runs with "
                                "UKLIB_SEC_FULL=1 (UKLIB-SEC-PLAN.md U6)"))

# The cells T2 skips beyond T1's.  proj_len counts from the valuation date on SEC and from
# the start on S, so it differs by d by design; the comparison asserts what it must get
# right, that both frames end at the same instant.  payment_surv_mth returns a time point,
# which on SEC's clock is S's less d, as SPIA's does: payment_factor_life and
# dependant_factor, which read it, are compared, so a wrong survival point still fails.
# annual_income_init is S's first year's income and SEC's income of the year under way at
# the valuation date, the two the same only where that year is the first; the splice
# compares the column with S's income of that year (_compare).  rpi_index and rpi_peak are
# measured relative to the latest index at the valuation date on SEC, and from outset on S,
# so they differ by S's index there; the splice compares them so scaled (_compare).
SPLICE_EXEMPT = (TWIN_EXEMPT_DEFAULT | SPEC.exempt
                 | {"proj_len", "payment_surv_mth", "annual_income_init", "rpi_index",
                    "rpi_peak"})

# T3's: a point starting later measures its index from outset and its income from the
# first year, as S's does, so only the frame and the survival point, a time point on the
# valuation clock, S's plus k, are exempt beyond T1's.
FUTURE_EXEMPT = TWIN_EXEMPT_DEFAULT | SPEC.exempt | {"proj_len", "payment_surv_mth"}

# The result_cf columns that expense inflation moves, and the cells they are made of: on the
# committed points, at the shipped 3%, the only places an in-force row departs from S.
INFLATED = ("expenses", "liability_cf", "net_cf")
INFLATION_CELLS = frozenset({"inflation_factor", "expenses", "liability_cf", "net_cf",
                             "result_cf"})

# The cells whose exact value is 0 and whose computed value is rounding about it, held at
# the harness's absolute floor of 1e-9, as the template's residuals are (§5.2, T2): every
# other cell at none (_compare).
RESIDUALS = frozenset({"check_lives_roll_fwd_resid", "check_payment_factor_resid"})
FLOOR = 1e-9

# The reports, which the comparison reads as frames rather than as cells.
REPORTS = ("result_cf", "result_pols")

# The cells that scale with policy_count.  Every other cell is a per-contract amount, a
# probability, a factor, a clock or a flag, and must not move when the count does.
COUNTED = frozenset({
    "policy_count", "pols_if_init", "pols_if", "pols_if_at", "pols_new_biz",
    "annuity_payments", "claims", "expenses", "liability_cf", "net_cf",
    "result_cf", "result_pols"})

# result_pols' columns, in its order: the closing obligation measure and the new business,
# then PA_UK_S's other columns in its order.
RESULT_POLS = ["pols_if", "pols_new_biz", "lives_if_1", "lives_if_2", "certain_floor",
               "payment_factor", "dependant_factor", "annuity_pp", "cum_annuity_all",
               "vp_balance"]
COUNTED_POLS = ("pols_if", "pols_new_biz")

# The flows of result_cf, each nonzero on some committed point (T4).
FLOWS = ("annuity_payments", "claims_vp", "claims_prop", "expenses", "liability_cf",
         "net_cf")

# The timings and the kinds.
TIMINGS = ("BEF_NB", "BEF_DECR")
KINDS = ("VP", "PROP")

# What each cell holds outside the frame, before the start and from the stop rule on, as
# its docstring says: no count, so no cash flow; no instalment, floor or factor; no rate
# read at a policy year or an age the contract does not have.  The type is part of the
# value: a count is a float in every branch and a flag a bool, because the C step types a
# cell by the values it returns (USLIB-SEC-PLAN.md F3).  The guard test also calls
# pols_if_at at each timing, claims at each kind and each (t, life) cell for both lives,
# all 0.0.
OUTSIDE_COVER = {
    "is_active": False, "is_payment_mth": False, "annuity_pp": 0.0,
    "next_payment_mth": -1, "mths_since_payment": 0, "lives_death_last": 0.0,
    "certain_floor": 0.0, "payment_factor_life": 0.0, "payment_factor": 0.0,
    "overlap_gate": 0.0, "dependant_factor": 0.0, "annuity_payments": 0.0,
    "pols_if": 0.0, "pols_new_biz": 0.0, "expenses": 0.0, "liability_cf": 0.0,
    "net_cf": 0.0, "check_payment_factor_resid": 0.0}
PER_LIFE_OUTSIDE = ("lives_death", "mort_rate", "mort_rate_base", "improve_rate",
                    "improve_factor")

# The time points before the contract is on the books, which hold 0.0 there: survival, the
# expected payments to date, the value-protection balance and the residual.
BEFORE_ENTRY = ("lives_if_last", "cum_annuity_all", "vp_balance",
                "check_lives_roll_fwd_resid")

# The cells a month outside the frame may not reach: the clocks of the contract, keyed by a
# policy year, an attained age or a calendar year.
IN_COVER_ONLY = ("duration", "policy_year", "calendar_year", "age")

# The opening state, in the table's order, and the cells running in force adds to
# PA_UK_S's, each of which the symbol map must name.
STATE = ("lives_if_init_1", "lives_if_init_2", "cum_annuity_all_init",
         "annual_income_init", "rpi_peak_init", "cum_annuity_pp_init")
NEW_CELLS = ("policy_count", "duration_mth_init", "t_entry", "stop_mth", "is_active",
             "pols_if_at", "pols_new_biz", "lives_if_init", "cum_annuity_all_init",
             "rpi_peak_init", "cum_annuity_pp_init", "annual_income_first",
             "policy_year_init", "is_payment_pm", "annuity_pp_pm", "cum_annuity_all",
             "mort_rate_base_at", "is_arrears", "is_scenario", "is_first_death",
             "is_level", "is_fixed", "is_lpi5", "is_rpi_catchup")

INFLATION = 0.03        # the shipped inflation_rate, which the inflation test reads

# The recursion limit, as mx.set_recursion takes it, under which the committed points are
# first swept (R2, F7).  A report evaluates each column in ascending t, so a forward
# recursion, through t - 1, finds the month before already cached; the committed points'
# sweep passes under a limit of 7, and fails under 6 (measured at M11).  A backward
# recursion over the frame, through t + 1, opens a chain as long as the frame, and the
# shortest committed frame longer than a month is 25.
CALL_DEPTH = 40

# The reads beyond t + 1 the model makes, as (reader, cell read): none.  PA_UK_S's one,
# the proportionate payment's scan to the next payment month, is a closed form on the
# policy month here (UKLIB-SEC-PLAN.md §6.7).
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
    is the twin's.  The two ``derived_refs`` rows, read from S under an RPI of their own,
    are the only rows of their point and month, and are found the same way.
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


def _s_table():
    """S's committed table, indexed by point_id."""
    return pd.read_csv(model_path(TWIN).parent / "model_point_table.csv",
                       index_col="point_id")


def _s_table_with_variants(points=None):
    """S's committed table with the :data:`VARIANTS` appended, under their own point_ids;
    only ``points`` of it, where given."""
    table = _s_table()
    rows = []
    for point_id, (base, changes) in VARIANTS.items():
        row = table.loc[[base]].assign(**changes)
        row.index = pd.Index([point_id], name="point_id")
        rows.append(row)
    table = pd.concat([table, *rows])
    return table if points is None else table.loc[list(points)]


def _sec_inputs(tmp_path, table, edits=None):
    """A copy of the product directory whose SEC table is ``table``, other inputs changed
    by ``edits``, as :func:`uk_sec_support.temp_inputs` takes them; its SEC folder."""
    return temp_inputs(tmp_path, model_path(SEC), model_points=table,
                       model_point_file=TABLE, edits=edits)


def _read_edited(tmp_path, edit, edits=None):
    """PA_UK_SEC read from a copy whose SEC table is ``edit(_committed())``."""
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

    :func:`uk_sec_support.sweep` reaches ``PA_UK_S``'s ``next_payment_mth`` and
    ``mths_since_payment`` only where a point takes the proportionate payment, and
    ``lives_death`` of the dependant, ``duration_mth`` and ``payment_surv_mth`` nowhere; a
    cell S never evaluates is compared nowhere.  They are evaluated here over the frame, so
    the splice and the future comparison see them too.
    """
    sweep(proj)
    lives = (1, 2) if proj.is_joint() else (1,)
    for t in range(proj.proj_len()):
        proj.next_payment_mth(t)
        proj.mths_since_payment(t)
        proj.duration_mth(t)
        proj.payment_surv_mth(t)
        for life in lives:
            proj.lives_death(t, life)


def _rpi_linked(s_proj):
    """Whether S point ``s_proj`` escalates with the RPI."""
    return s_proj.escalation_type() in ("lpi5", "rpi_catchup")


def _before_valuation(s_proj, month):
    """An ``arg_map`` that skips each S key before the valuation date that SEC does not
    carry as S keys it (USLIB-SEC-PLAN.md §5.2, T2, precised at M7).

    ``cum_annuity_pp``'s keys before S's month ``month``: the ``"ALL"`` payments to date
    are SEC's opening state, one total, and on RPI-linked escalation so are the annuitant's.
    And on RPI-linked escalation ``annual_income``'s years before the one under way at the
    valuation instant: history SEC carries in its opening state.  On level and fixed
    escalation the annuitant's schedule and its income are the contract's, which SEC
    re-derives at every key, so those keys are compared.
    """
    linked = _rpi_linked(s_proj)
    first_year = max(month - 1, 0) // 12 + 1

    def mapped(name, args):
        if name == "cum_annuity_pp" and args[0] < month and (
                args[1] == "ALL" or linked):
            return None
        if name == "annual_income" and linked and args[0] < first_year:
            return None
        return args
    return mapped


def _index_faults(s_proj, sec_proj, month):
    """Where SEC's relative index and peak depart from S's, scaled by S's index at ``a0``.

    SEC measures ``rpi_index`` and ``rpi_peak`` relative to the latest index at the
    valuation instant, the one of the anniversary ``a0`` that opened the year under way,
    where S measures them from outset.  So at every anniversary ``a >= a0`` S cached, SEC's
    is S's over S's index at ``a0``, to 1e-12 relative.
    """
    if s_proj.escalation_type() != "rpi_catchup":
        return []
    a0 = max(month - 1, 0) // 12
    scale = s_proj.rpi_index(a0)
    found = []
    for name in ("rpi_index", "rpi_peak"):
        for a in sorted(s_proj.cells[name].keys()):
            if a < a0:
                continue
            want = s_proj.cells[name](a) / scale
            got = sec_proj.cells[name](a)
            if not math.isclose(got, want, rel_tol=1e-12, abs_tol=0.0):
                found.append(f"{name}({a}): SEC {got!r}, S's over its index at {a0}, "
                             f"{want!r}")
    return found


def _compare(s_proj, sec_proj, month, exempt, columns=None):
    """Where SEC's row departs from S's point from S month ``month`` on.

    First the frames, ``result_cf`` (over ``columns``, or every column both hold) and
    ``result_pols``, on every column both hold, SEC row ``t`` against S row ``t + month``,
    frames ending together; then every cell of S's but ``exempt``, :data:`REPORTS` and
    :data:`RESIDUALS`, at every argument S cached inside its frame from ``month`` on,
    moved onto SEC's clock, but the keys before the valuation date SEC carries as opening
    state (:func:`_before_valuation`).  Both to 1e-9 relative with no absolute floor
    (USLIB-SEC-PLAN.md §5.2, T2, precised at M11): a floor of 1e-9 passes an error of 1% in
    any value below 1e-7, and survival late in a long frame, and where the cap binds, falls
    below 1e-9.  Then the cells of :data:`RESIDUALS` at the floor of 1e-9: their exact value
    is 0.  Then, on a row in payment, the opening income against S's income of the year
    under way, and the relative index and peak against S's (:func:`_index_faults`).
    Returns the mismatch lines, empty when the row is S's.
    """
    end = sec_proj.proj_len()
    s_end = s_proj.proj_len() - month
    if s_end != end:
        return [f"the frames end apart: S's at t = {s_end - 1} on SEC's clock, SEC's at "
                f"t = {end - 1}"]
    found = []
    for report in REPORTS:
        keep = columns if report == "result_cf" else None
        found += [f"{report}: {line}" for line in frame_mismatches(
            s_proj.cells[report](), sec_proj.cells[report](), t_offset=month,
            columns=keep, atol=0.0)]
    others = exempt | set(REPORTS)
    history = _before_valuation(s_proj, month)
    found += twin_mismatches(s_proj, sec_proj, t_offset=month, exempt=others | RESIDUALS,
                             arg_map=history, atol=0.0, codes=codes(sec_proj))
    found += twin_mismatches(s_proj, sec_proj, t_offset=month,
                             exempt=others | (set(s_proj.cells) - RESIDUALS),
                             arg_map=history, codes=codes(sec_proj))
    if month > 0:
        year = max(month - 1, 0) // 12 + 1
        want = s_proj.annual_income(year)
        if not math.isclose(sec_proj.annual_income_init(), want, rel_tol=1e-12,
                            abs_tol=0.0):
            found.append(f"annual_income_init(): SEC {sec_proj.annual_income_init()!r}, S's "
                         f"annual_income({year}) {want!r}")
        found += _index_faults(s_proj, sec_proj, month)
    return found


def _continues_s(s_proj, sec_proj, month):
    """Where a committed row departs from S's point ``s_proj`` from S month ``month`` on.

    The splice's comparison (:func:`_compare`), on the committed model at the shipped
    assumptions.  The shipped 3% expense inflation runs from the start in S and from the
    valuation date here (D7), so :data:`INFLATED`'s columns, and :data:`INFLATION_CELLS`,
    differ by design and are left out; the inflation test holds them.  Every other column
    and cell must agree, to 1e-9 relative, with no absolute floor but on the residuals.
    """
    keep = [c for c in s_proj.result_cf().columns if c not in INFLATED]
    return _compare(s_proj, sec_proj, month, SPLICE_EXEMPT | INFLATION_CELLS, keep)


def _case_id(rates, kind, s_point, month):
    """A case's id: ``point2-d12``, ``point2-k3`` if it starts later, and the set where it
    is not the shipped RPI's, ``rpi_low-point6-d24``."""
    if kind == "future":
        where = f"point{s_point}-k{-month}"
    else:
        where = f"point{s_point}-" + (f"d{month}" if kind == "derived" else f"{kind}{month}")
    return where if rates == "shipped" else f"{rates}-{where}"


def _case(case, core, case_id):
    """One parametrized case: run by default if it is in ``core``, else on the full grid."""
    return pytest.param(*case, id=case_id, marks=() if case in core else FULL_ONLY)


def _selected(cases, core):
    """The cases this run makes rows for: the core, or every one under UKLIB_SEC_FULL."""
    return [case for case in cases if SEC_FULL or case in core]


# Every row the splice compares, as (set, row_kind, S point, source_mth), T3's included,
# and the default run's among them.
GRID = (*SPLICES, *IN_FORCE_TWINS, *((r, "future", p, -k) for r, p, k in FUTURES))
CORE_GRID = frozenset({*CORE_SPLICES, *((r, "future", p, -k) for r, p, k in CORE_FUTURES)})


# ---------------------------------------------------------------------------
# Fixtures


@pytest.fixture(scope="module")
def sec_read():
    """PA_UK_SEC read in place, as committed, and swept once, cold; what it met.

    The model is first asked for ``duration_mth(500)`` on the twin of S point 1, and the
    keys that call leaves in ``duration_mth`` are kept.  Then every committed point is
    swept (:func:`uk_sec_support.sweep`: ``result_cf``, the other report and the checks),
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
    """PA_UK_SEC read in place, as committed, with every point swept (sec_read)."""
    return sec_read[0]


@pytest.fixture(scope="module")
def s_model():
    """PA_UK_S read in place, as committed, with every point swept.

    T6 regenerates the SEC inputs from it, which would otherwise project every S point
    again (USLIB-SEC-PLAN.md §4, *Carried into Phase 1*), and the in-force tests read S's
    months off it.
    """
    model = mx.read_model(model_path(TWIN), name=_name("s"))
    for key in point_keys(model):
        _sweep_s(projection(model, key))
    yield model
    model.close()


# How many S points of a splice set are kept swept at once (_Splices.s_point).  A swept S
# point on the table basis holds about 140 MB, most of it modelx's record of what
# PA_UK_S's survival check reads, a product over every month before each time point, so
# that the shipped set's 22 points swept together held 1.8 GB (measured at M11).  T2 and
# T3 run their cases point by point, so two are enough.
SWEPT = 2


class _Splices:
    """The splice's models, a pair for each of :data:`SPLICE_SETS`, each made when first
    asked for (:meth:`pair`) and closed at the module's end.

    For a set, S is read from a copy of the product directory whose table has the variants
    appended, only the RPI points under the RPI sets, and the set's References are set on
    it.  SEC runs on the same mortality table, and on a model point table of its own, built
    by the generator from the registered spec with its rows replaced by the set's cases this
    run selects, the core or the full grid (:func:`_selected`), out of this S model, so each
    row opens with the state of the very run it is compared with; the set's References are
    set on it too.  No input table moves with ``d``: PA's one valuation-clock input is the
    ``inflation_rate`` Reference.  An S point is swept (:func:`_sweep_s`) when a case first
    compares a row with it (:meth:`s_point`), and the :data:`SWEPT` most recently compared
    stay swept; each SEC row is projected by the case that compares it and released once
    compared (:func:`_settle`).
    """

    def __init__(self, root):
        self.root, self.pairs, self.swept = root, {}, {}

    def pair(self, rates):
        if rates not in self.pairs:
            refs = SPLICE_SETS[rates]
            points = None if rates == "shipped" else RPI_POINTS
            s = mx.read_model(temp_inputs(self.root / rates / "s", model_path(TWIN),
                                          model_points=_s_table_with_variants(points)),
                              name=_name(f"s_{rates}"))
            for ref, value in refs.items():
                setattr(s.Projection, ref, value)
            derived = [(p, d) for r, kind, p, d in _selected(SPLICES + IN_FORCE_TWINS,
                                                             CORE_SPLICES)
                       if r == rates and kind == "derived"]
            futures = [(p, k) for r, p, k in _selected(FUTURES, CORE_FUTURES) if r == rates]
            spec = dataclasses.replace(SPEC, derived=tuple(derived), future=tuple(futures),
                                       derived_refs={})
            table, companions = build_sec_table(spec, s)
            assert companions == {}
            sec = mx.read_model(_sec_inputs(self.root / rates / "sec", table),
                                name=_name(f"sec_{rates}"))
            for ref, value in refs.items():
                setattr(sec.Projection, ref, value)
            self.pairs[rates], self.swept[rates] = (s, sec), []
        return self.pairs[rates]

    def s_point(self, rates, s_point):
        """S point ``s_point`` of set ``rates``, swept, as a comparison needs it.

        The S space must be swept before a row is compared with it, since the comparison
        reads what S cached (:func:`uk_sec_support.twin_mismatches`).  The :data:`SWEPT`
        points most recently asked for stay swept, and an older one is released, and its
        memory collected, before another is swept: a released point, asked for again, is
        swept afresh.
        """
        s = self.pair(rates)[0]
        key, swept = _key(s, s_point), self.swept[rates]
        if key in swept:
            swept.remove(key)
        else:
            while len(swept) >= SWEPT:
                _release(s, swept.pop(0))
                gc.collect()
            _sweep_s(projection(s, key))
        swept.append(key)
        return projection(s, key)

    def close(self):
        for s, sec in self.pairs.values():
            sec.close()
            s.close()


@pytest.fixture(scope="module")
def spliced(tmp_path_factory):
    """The splice's models, by set (:class:`_Splices`)."""
    splices = _Splices(tmp_path_factory.mktemp("spliced"))
    yield splices
    splices.close()


@pytest.fixture(scope="module")
def splice_records():
    """What each splice row was found to do, by case (:func:`_settle`)."""
    return {}


# ---------------------------------------------------------------------------
# The splice's records
#
# Each T2 and T3 case scans its row first, on an ItemSpace made for it, and records what
# the rules test and the core grid's reach need of the row; then it compares the row with
# S, and releases it (_settle).  The scan comes first because the comparison evaluates SEC
# cells at S's cached keys, at months and years before the valuation date among them
# (SPIA's *Record — M11*, carried).  Each of the two tests reads the records, and computes
# any case no earlier test has recorded, which keeps it whole when run alone.


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
    month, such as ``proj_len()`` or the payments to date on the policy clock, as far as
    the dependency graph goes, each with the call keyed by no month that reads it: so a read
    that looks ahead through a cell taking no ``t`` is the reader's (USLIB-SEC-PLAN.md §5.2,
    T2, precised at M12; ``DIA_US_SEC``'s form).  ``reach`` holds what each call keyed by
    no month reads, so that each is walked once a row, and the walk is a loop, not a
    recursion.
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


def _closed_reads(proj):
    """The keys before the valuation date an RPI-linked row has asked of the cells keyed on
    the policy clock (USLIB-SEC-PLAN.md §5.2, T2, precised at M7).

    On RPI-linked escalation the income, the index and the payments before the valuation
    instant are history, held in the opening state, so no cell may ask ``annual_income`` a
    year before the one under way, ``rpi_index`` or ``rpi_peak`` an anniversary before
    the one that opened it, or ``cum_annuity_pp``, ``annuity_pp_pm`` or ``is_payment_pm`` a
    policy month before the valuation date's.  On level and fixed escalation the schedule
    is the contract's, which one loop at the valuation date's key sums, R2's admitted read.
    """
    if not (proj.is_lpi5() or proj.is_rpi_catchup()):
        return []
    d = max(proj.duration_mth_init(), 0)
    y0 = proj.policy_year_init()
    bounds = {"annual_income": y0, "rpi_index": y0 - 1, "rpi_peak": y0 - 1,
              "cum_annuity_pp": d, "annuity_pp_pm": d, "is_payment_pm": d}
    return [f"{name}{args}" for name, low in bounds.items()
            for args in _cached_args(proj.cells[name])
            if args[0] < low and not (name == "cum_annuity_pp" and args[0] <= 0)]


def _rule_breaches(proj):
    """R1 and R2's look-ahead on one row, once it has run whole.

    The row's reports and checks are run (:func:`uk_sec_support.sweep`), and then every
    monthly cell at every month of the frame and the month after it, as the C step's sweep
    runs them (:func:`uk_sec_support.full_sweep`): no report of a row need read every state,
    and a base at ``t == 0`` would hide in a cell the reports leave unread
    (USLIB-SEC-PLAN.md §5.2, T2, precised at M4).  ``{"negative": [...], "early": [...],
    "ahead": [...], "closed": [...], "raised": [...]}``: every cached call with a negative
    argument; every call keyed by a month before ``t_entry()`` that a call keyed by a month
    at or after it reads; every call keyed by a month beyond ``t + 1`` that a call keyed by
    ``t`` reads, but :data:`LOOK_AHEAD`'s; every key before the valuation date an RPI-linked
    row asked (:func:`_closed_reads`); and every call the full sweep found raising.  A call
    reads its precedents, as modelx's dependency graph records them, and, through a
    precedent keyed by no month, whatever that precedent reads in turn
    (:func:`_months_read`).
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
    return {"negative": negative, "early": early, "ahead": ahead,
            "closed": _closed_reads(proj), "raised": raised}


def _vp_paid(x, t):
    """The month's value-protection payment per contract in force, before the count."""
    return x.claims(t, _code(x, "VP"))


# What test_the_core_grid_reaches_every_branch asks of the core's rows in the model's own
# values, which no column of the table shows: each holds of some core row, or of a core row
# in some month of its frame.  At the valuation date, each opening-state column in use: a
# life dead in the opening state, each; survival a probability strictly between 0 and 1;
# payments carried in; and on RPI-linked escalation an income past the first year's, a peak
# above the index and the annuitant's payments carried in.  Later in the frame, every branch
# and both sides of each min and max the full grid reaches: the guarantee's floor binding
# and lifted, the overlap gate shut and open, the dependant paid, value protection paid and
# run out, the proportionate payment paid and past the frame, the LPI's cap, floor and
# between, the ratchet frozen and rising, the mortality cap, an age past the limiting age,
# the improvement flat, tapering and spent, the obligation measure's cap binding and not,
# its dependant's leg dropped, and the frame's two ends.
AT_VALUATION = {
    "the annuitant dead in the opening state": lambda x: (
        x.duration_mth_init() > 0 and x.lives_if_init(1) == 0.0),
    "the dependant dead in the opening state": lambda x: (
        x.duration_mth_init() > 0 and x.is_joint() and x.lives_if_init(2) == 0.0),
    "survival a probability in the opening state": lambda x: (
        0.0 < x.lives_if_init(1) < 1.0),
    "payments carried in": lambda x: x.cum_annuity_all_init() > 0.0,
    "an RPI-linked income past the first year's": lambda x: (
        (x.is_lpi5() or x.is_rpi_catchup()) and x.duration_mth_init() > 12
        and x.annual_income_init() != x.annual_income_first()),
    "a peak above the index": lambda x: x.is_rpi_catchup() and x.rpi_peak_init() > 1.0,
    "the annuitant's payments carried in": lambda x: (
        (x.is_lpi5() or x.is_rpi_catchup()) and x.vp_pct() > 0.0 and x.is_first_death()
        and x.cum_annuity_pp_init() > 0.0),
    "valued on an anniversary": lambda x: (
        x.duration_mth_init() > 0 and x.duration_mth_init() % 12 == 0),
    "valued inside the guarantee": lambda x: (
        0 < x.duration_mth_init() < x.guarantee_mths()),
    "valued past the guarantee": lambda x: (
        0 < x.guarantee_mths() <= x.duration_mth_init()),
}
IN_FRAME = {
    "the guarantee's floor paying past survival": lambda x, t: (
        x.certain_floor(t) == 1.0 and x.payment_factor_life(t) < 1.0
        and x.annuity_pp(t) > 0.0),
    "the floor lifted": lambda x, t: (
        x.is_active(t) and x.guarantee_mths() > 0 and x.certain_floor(t) == 0.0),
    "the overlap gate shut": lambda x, t: (
        x.is_joint() and x.is_active(t) and x.overlap_gate(t) == 0.0
        and x.lives_if(x.payment_surv_mth(t), 2) > 0.0
        and x.lives_if(x.payment_surv_mth(t), 1) < 1.0),
    "the overlap gate open with overlap": lambda x, t: (
        x.overlap() and x.certain_floor(t) == 1.0 and x.dependant_factor(t) > 0.0
        and x.annuity_pp(t) > 0.0),
    "the dependant paid": lambda x, t: (
        x.dependant_factor(t) > 0.0 and x.annuity_pp(t) > 0.0),
    "value protection paid on the first death": lambda x, t: (
        x.vp_pct() > 0.0 and x.is_first_death() and _vp_paid(x, t) > 0.0),
    "value protection paid on the last death": lambda x, t: (
        x.vp_pct() > 0.0 and not x.is_first_death() and _vp_paid(x, t) > 0.0),
    "value protection run out": lambda x, t: (
        x.vp_pct() > 0.0 and x.is_active(t) and x.vp_balance(t) == 0.0),
    "value protection netting an advance instalment": lambda x, t: (
        x.vp_pct() > 0.0 and not x.is_arrears() and x.is_payment_mth(t)
        and _vp_paid(x, t) > 0.0),
    "the proportionate payment": lambda x, t: (
        x.proportion() and x.claims(t, _code(x, "PROP")) > 0.0),
    "a payment month": lambda x, t: x.is_payment_mth(t),
    "a month between payments": lambda x, t: (
        x.is_active(t) and not x.is_payment_mth(t)),
    "the LPI cap binding": lambda x, t: (
        x.is_lpi5() and x.is_active(t) and x.rpi_rate > x.esc_lpi_cap),
    "the LPI floor binding": lambda x, t: (
        x.is_lpi5() and x.is_active(t) and x.rpi_rate < 0.0),
    "the LPI between its bounds": lambda x, t: (
        x.is_lpi5() and x.is_active(t) and 0.0 <= x.rpi_rate <= x.esc_lpi_cap),
    "the ratchet frozen": lambda x, t: (
        x.is_rpi_catchup() and x.is_active(t) and x.duration(t) >= x.policy_year_init()
        and x.rpi_index(x.duration(t)) < x.rpi_peak(x.duration(t) - 1)),
    "the ratchet rising": lambda x, t: (
        x.is_rpi_catchup() and x.is_active(t) and x.duration(t) >= x.policy_year_init()
        and x.rpi_index(x.duration(t)) > x.rpi_peak(x.duration(t) - 1)),
    "the mortality cap binding": lambda x, t: (
        x.is_active(t) and not x.is_scenario() and x.mort_rate(t, 1) == 1.0
        and x.age(t, 1) < x.omega_age),
    "an age past the limiting age": lambda x, t: (
        x.is_active(t) and not x.is_scenario() and x.age(t, 1) >= x.omega_age),
    "the improvement flat": lambda x, t: (
        x.is_active(t) and not x.is_scenario()
        and x.improve_rate(t, 1) == x.improve_rate_base),
    "the improvement tapering": lambda x, t: (
        x.is_active(t) and not x.is_scenario()
        and 0.0 < x.improve_rate(t, 1) < x.improve_rate_base),
    "the improvement spent": lambda x, t: (
        x.is_active(t) and not x.is_scenario() and x.improve_rate(t, 1) == 0.0),
    "the obligation's cap binding": lambda x, t: (
        x.dependant_pct() > 0.0 and x.certain_floor(t) == 1.0
        and x.lives_if(t + 1, 1) < 1.0 and x.lives_if(t + 1, 2) > 0.0),
    "the obligation's dependant leg dropped": lambda x, t: (
        x.is_active(t) and x.dependant_pct() == 0.0),
    "the frame ending at the age stop": lambda x, t: (
        t == x.proj_len() - 1 and x.stop_mth() == x.horizon_mths()),
    "the frame ending at the guarantee": lambda x, t: (
        t == x.proj_len() - 1 and x.stop_mth() > x.horizon_mths()),
}


def _branches(x):
    """The names in :data:`AT_VALUATION` and :data:`IN_FRAME` that hold of row ``x``."""
    reached = {what for what, holds in AT_VALUATION.items() if holds(x)}
    frame = range(x.t_entry(), x.proj_len())
    return reached | {what for what, holds in IN_FRAME.items()
                      if any(holds(x, t) for t in frame)}


def _scan(records, case, proj):
    """Record what the rules and the core grid's reach need of a row, on an ItemSpace that
    has computed nothing else yet.

    The record is :func:`_rule_breaches`'s, with the row's :func:`_branches`, and a row that
    raises is recorded as raising, which the rules test reports.
    """
    try:
        record = _rule_breaches(proj)
        record["branches"] = _branches(proj)
        record["failed"] = None
    except Exception as err:                    # recorded, and reported by the rules test
        record = {"negative": [], "early": [], "ahead": [], "closed": [], "raised": [],
                  "branches": set(), "failed": _raised(err)}
    records[case] = record
    return record


def _settle(records, case, model, key):
    """Scan a row afresh if no case has, and release it (:func:`_scan`)."""
    try:
        if case not in records:
            if key in model.Projection.itemspaces:
                _release(model, key)
            _scan(records, case, projection(model, key))
    finally:
        _release(model, key)
    return records[case]


def _record_of(spliced, records, case):
    """The record of ``case``, from the case that compared its row or, failing it, now."""
    if case not in records:
        sec = spliced.pair(case[0])[1]
        _settle(records, case, sec, _row_key(sec, *case[1:]))
    return records[case]


# ---------------------------------------------------------------------------
# T2 -- the splice


@pytest.mark.parametrize(
    "rates, kind, s_point, month",
    [_case(case, CORE_SPLICES, _case_id(*case)) for case in SPLICES + IN_FORCE_TWINS])
def test_an_in_force_point_continues_its_s_projection(spliced, splice_records, rates, kind,
                                                      s_point, month):
    """Opened with S's state at month d, the point is S from d on, in every cell of S's.

    This is the test that says the opening state is complete: a state column the SEC row
    did not carry, or carried from the wrong instant, would make SEC part from S here, and
    nowhere else, because on a point starting at ``t = 0`` the two clocks coincide and the
    opening state is the start date's.  For the same reason it is the test that catches a
    policy month passed as ``t`` (R1a), a scenario death read on the wrong clock, and a
    look-back that stops at the wrong month.  The frame comparisons read SEC row ``t``
    against S row ``t + d`` in every column of ``result_cf`` and every column of
    ``result_pols`` both hold, and fail frames that end apart.  The cell comparison then
    evaluates every cell of S's but :data:`SPLICE_EXEMPT`, at every argument S cached inside
    its own frame from month ``d`` on, moved onto SEC's clock: survival, the payments to
    date on both clocks, the value-protection balance, the floors and factors, the income
    and the residuals among them, but the keys before the valuation date that SEC carries as
    opening state (:func:`_compare`).  Each compares to 1e-9 relative with no absolute floor
    but the residuals.  The opening income is held to S's of the year under way, and the
    relative index and peak to S's.  An S cell this model lacked would fail it.

    The row is first scanned for the rules test, on an ItemSpace made for it, then
    compared, then released (:func:`_scan`, :func:`_settle`).
    """
    sec = spliced.pair(rates)[1]
    key = _row_key(sec, kind, s_point, month)
    if key in sec.Projection.itemspaces:
        _release(sec, key)
    case = (rates, kind, s_point, month)
    try:
        _scan(splice_records, case, projection(sec, key))
        s_proj = spliced.s_point(rates, s_point)
        sec_proj = projection(sec, key)
        assert _compare(s_proj, sec_proj, month, SPLICE_EXEMPT) == []
    finally:
        _settle(splice_records, case, sec, key)


# ---------------------------------------------------------------------------
# T3 -- future new business


@pytest.mark.parametrize(
    "rates, s_point, k",
    [_case(case, CORE_FUTURES, _case_id(case[0], "future", case[1], -case[2]))
     for case in FUTURES])
def test_future_new_business_is_the_s_projection_k_months_on(spliced, splice_records,
                                                             rates, s_point, k):
    """Starting k months after the valuation date, the point is S's projection k months on.

    SEC rows ``k ..`` are S rows ``0 ..``, ending together at the stop rule, in
    ``result_cf`` and ``result_pols``, and every cell of S's but :data:`FUTURE_EXEMPT`
    agrees at every argument S cached inside its own frame, moved ``k`` later: the policy
    clock's keys, the payments to date, the income and the index, need no move.  Each
    compares as the splice compares, with no absolute floor but on the residuals
    (:func:`_compare`).  Before the start every column of ``result_cf`` and
    ``result_pols`` is an exact zero, and the contracts arrive in month ``k`` as new
    business.

    The last assertions are R1 and D4's base rule made testable.  After the reports, no
    mortality rate, no read keyed by a policy year, an age or a calendar year has been
    evaluated at a month before the start.  A survival recursion based at ``t == 0``
    rather than at ``t_entry()``, or a rate evaluated before the month is asked whether it
    is in the frame, still gives the right numbers.

    The pre-start rows are asserted present before they are asserted zero, in every
    report: a frame that opened at the start would have none, its zeros would hold of
    nothing, and the comparisons with S, which start at the start, would not see it.  The
    row is first scanned for the rules test, then compared, then released.
    """
    sec = spliced.pair(rates)[1]
    key = _row_key(sec, "future", s_point, -k)
    if key in sec.Projection.itemspaces:
        _release(sec, key)
    case = (rates, "future", s_point, -k)
    try:
        _scan(splice_records, case, projection(sec, key))
        _release(sec, key)
        s_proj = spliced.s_point(rates, s_point)
        sec_proj = projection(sec, key)
        frames = {name: sec_proj.cells[name]() for name in REPORTS}
        assert _compare(s_proj, sec_proj, -k, FUTURE_EXEMPT) == []
        for report, frame in frames.items():
            assert list(frame.index[:k]) == list(range(k)), report
            assert (frame.loc[:k - 1] == 0.0).all().all(), report
        assert sec_proj.pols_new_biz(k) == sec_proj.policy_count() == 1.0
        early = {}
        for name in ("mort_rate", "mort_rate_base", "improve_rate", "improve_factor",
                     "age", "calendar_year", "duration", "policy_year"):
            months = sorted(args[0] for args in _cached_args(sec_proj.cells[name])
                            if args[0] < k)
            if months:
                early[name] = months
        assert not early, f"rates evaluated before the start: {early}"
    finally:
        _settle(splice_records, case, sec, key)


# ---------------------------------------------------------------------------
# D11's R1 and R2, and D3's closed-form clock


@pytest.mark.parametrize("grid", [pytest.param("core", id="core"),
                                  pytest.param("full", id="full", marks=FULL_ONLY)])
def test_no_cell_is_called_before_the_valuation_date_or_reads_far_ahead(spliced,
                                                                        splice_records,
                                                                        grid):
    """R1, its look-back and R2's look-ahead, on the rows T2 and T3 compare: core or rest.

    Each is a rule of how the model computes, not of what, so no number shows a breach,
    and on a point starting at ``t = 0`` the two clocks coincide and hide it from T1 too.
    The splice's rows are points in payment at every month T2 names, the variants and the
    RPI sets among them, and points starting later, and on each the reports, the checks and
    the full sweep are run first (:func:`_rule_breaches`):

    * R1: no cell holds a negative argument.  modelx evaluates one without complaint, and a
      compiled cache raises ``IndexError`` below 0 (USLIB-SEC-PLAN.md F4).  A policy month
      turned into ``t`` by subtracting ``duration_mth_init()`` (R1a) goes negative on a
      point in payment past it.
    * R1's look-back stops at ``t_entry()``: no cell evaluated at a month from
      ``t_entry()`` on read a month before it, directly or through a cell keyed by no
      month.  On a point starting later a recursion based at ``t == 0`` reads the pre-start
      zeros, so no number need show it and no argument goes negative.
    * R2's look-ahead: no cell evaluated at month ``t`` read a cell keyed by a month beyond
      ``t + 1``, as modelx's dependency graph records each cached call's precedents and
      through every precedent keyed by no month (:data:`LOOK_AHEAD` admits none).
    * On an RPI-linked row no cell asked a year, an anniversary or a policy month before
      the valuation date of the cells keyed on the policy clock (:func:`_closed_reads`):
      that history is the opening state's.
    * And no call of the full sweep raised.

    Each row was scanned by the T2 or T3 case that compared it, before the comparison
    (:func:`_scan`), and a row no case has scanned is scanned here.  The core case covers
    the core's rows, the full case every other row of the full grid, with
    ``UKLIB_SEC_FULL=1``.  The new-business twins in the splice's tables are no case's, and
    are left out: on them the clocks coincide, and T1 compares them with S cell by cell.
    """
    cases = [case for case in GRID if (case in CORE_GRID) == (grid == "core")]
    negative, early, ahead, closed, raised, failed = [], [], [], [], [], []
    for case in cases:
        record, where = _record_of(spliced, splice_records, case), _case_id(*case)
        negative += [f"{where}: {call}" for call in record["negative"]]
        early += [f"{where}: {read}" for read in record["early"]]
        ahead += [f"{where}: {read}" for read in record["ahead"]]
        closed += [f"{where}: {read}" for read in record["closed"]]
        raised += [f"{where}: {call}" for call in record["raised"]]
        if record["failed"]:
            failed.append(f"{where}: {record['failed']}")
    assert cases, f"the {grid} grid has no rows"
    assert not failed, f"rows that raised: {failed[:10]}"
    assert not raised, f"calls the full sweep found raising: {raised[:10]}"
    assert not negative, f"called before the valuation date: {negative[:10]}"
    assert not early, f"read before the start from the books: {early[:10]}"
    assert not ahead, f"read beyond t + 1: {ahead[:10]}"
    assert not closed, f"asked history the opening state holds: {closed[:10]}"


def test_the_policy_clock_is_a_closed_form_and_no_recursion_runs_backward(sec_read):
    """D3 and R2's recursions, on the committed model as it was first swept, cold.

    Both need a model on which nothing had been evaluated yet, which is what the fixture
    held when it made the record asserted here:

    * D3: the policy clock is the closed form.  Called first, ``duration_mth(500)``
      evaluates ``duration_mth`` once, where ``BasicTerm_SE``'s recursion would evaluate it
      at all 501 months from 0.
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


# modelx warns as its stack trace starts and stops, which the test uses to count a depth.
@pytest.mark.filterwarnings("ignore:call stack trace:UserWarning")
def test_the_schedules_are_based_at_the_valuation_dates_key(sec_model, s_model):
    """The payments to date and the income are based at static keys, read in one loop.

    ``cum_annuity_pp`` on the policy clock is based at ``max(duration_mth_init(), 0)``,
    and ``annual_income`` at ``policy_year_init()``, the year under way before any
    month-0 anniversary, keys that read no clock (USLIB-SEC-PLAN.md R2, precised at M12).
    On level and fixed escalation one loop there sums, or compounds, the contract's
    schedule in ``PA_UK_S``'s order, so every key is S's to the last bit, before the base
    and after it, on the table basis's joint point restated at 101 and at 635.  And a
    contract valued late reads its balance without recursing back to its start: on the one
    at 635, a one-row frame, every cell its reports evaluate, called cold, runs within
    :data:`LATE_DEPTH` cells of the report, where ``PA_UK_S``'s ``G(636)`` runs a chain of
    636.  On RPI-linked escalation the base is the opening state, the history: the
    catch-up point's annuitant payments to date at 60 open at 27,000, five years of a
    frozen 5,400.
    """
    table = sec_model.Data.model_point_table()
    for month in (101, 635):
        label = _label(table, "derived", 2, month)
        p, s = _point(sec_model, label), _point(s_model, 2)
        for k in range(1, month + 2):
            assert p.cum_annuity_pp(k, "ANNUITANT") == s.cum_annuity_pp(k, "ANNUITANT"), (
                label, k)
        for y in range(1, p.policy_year(0) + 1):
            assert p.annual_income(y) == s.annual_income(y), (label, y)
    fresh = mx.read_model(model_path(SEC), name=_name("late"))
    try:
        late = _point(fresh, _label(table, "derived", 2, 635))
        mx.start_stacktrace(maxlen=None)
        try:
            late.result_cf()
            late.result_pols()
            trace = mx.get_stacktrace(summarize=False)
        finally:
            mx.stop_stacktrace()
        level = deepest = 0
        for event, *_ in trace:
            level += 1 if event == "ENTER" else -1
            deepest = max(deepest, level)
        assert deepest <= LATE_DEPTH, deepest
    finally:
        fresh.close()
    frozen = _point(sec_model, _label(table, "derived", 6, 60))
    assert frozen.cum_annuity_pp(60, "ANNUITANT") == frozen.cum_annuity_pp_init() == 27000.0


# How deep the reports of a contract valued in its last month run, called cold: 8 cells,
# the report, the frame's checks, the count, the policy month and the model point read
# through Data (measured at M11).
LATE_DEPTH = 8

# How deep a cold call may run beyond its chain, one cell a month from its month back to
# t_entry() (D5): the cells above the chain and those below it, the first month's rates and
# Data's first reads of its tables.  Each chain head called cold alone, before anything else
# on a read of its own, runs at most 12 cells beyond its chain on every shape at its
# longest cover: the survival check 2, value protection's balance 4 and its claim 5 to 8,
# survival 6, the payments to date 3 to 9, the obligation measure 8 and net_cf 7 to 12
# (measured at M11).  Term's 16, as for uslib's Term and SPIA (USLIB-SEC-PLAN.md D5).  Any
# chain of two cells a month runs a frame's length beyond.
CHAIN_OVERHEAD = 16

# The contract's longest cover, held by proj_len() and the mortality table: every covered
# life issued at the youngest age the basis projects, issue_age_min, 0, on the scenario
# basis, which reads no mortality, and the table's first age, 50, on the table basis,
# which reads it from the issue age on; so frames of 12 x 115 = 1,380 months and 12 x 65 =
# 780 from the start, the age stop on the youngest life.  Each issued now and
# future_horizon_mth, 120 months, on.
YOUNGEST = {"scenario": 0, "table": 50}
LONGEST = 1380

# Each shape and the chains it runs, called cold in the last month of the frame at its own
# longest cover, each on a read of its own: (the S point whose twin it is, its basis, the
# chain heads, each a (cell, its arguments beyond the month)).  On the scenario basis
# survival is a step function, so the chains are the payments to date: the worked example
# reads the annuitant's, on the policy clock, through first-death value protection, and
# the last-survivor point the expected payments on both streams, on the valuation clock.
# On the table basis survival recurses too, and the obligation measure, the reports and
# the survival check read it: the worked example's table twin, the RPI catch-up and the
# LPI, whose income recurses by the year and whose payments to date are the annuitant's;
# and the rated single life, which the cap kills before its frame ends.
SCENARIO_HEADS = (("net_cf", ()), ("vp_balance", ()), ("claims", ("VP",)),
                  ("cum_annuity_all", ()))
TABLE_HEADS = (("net_cf", ()), ("pols_if", ()), ("vp_balance", ()),
               ("cum_annuity_all", ()), ("check_lives_roll_fwd_resid", ()),
               ("claims", ("VP",)), ("lives_if", (1,)), ("lives_if", (2,)))
SINGLE_HEADS = (("net_cf", ()), ("pols_if", ()), ("cum_annuity_all", ()),
                ("check_lives_roll_fwd_resid", ()), ("lives_if", (1,)))
SHAPES = ((1, "scenario", SCENARIO_HEADS), (10, "scenario", SCENARIO_HEADS),
          (2, "table", TABLE_HEADS), (6, "table", TABLE_HEADS), (7, "table", TABLE_HEADS),
          (8, "table", SINGLE_HEADS))


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
    its S point with every covered life issued at :data:`YOUNGEST` on its basis, now and
    120 months on, the shipped ``future_horizon_mth``.  ``(folder, [(label, frame,
    t_entry, heads)])``."""
    committed = _committed()
    rows, frames = [], []
    top = committed.index.max()
    for s_point, basis, heads in SHAPES:
        twin = _label(committed, "twin", s_point, 0)
        age = YOUNGEST[basis]
        assert committed.at[twin, "mort_basis"] == basis, s_point
        for k in (0, 120):
            top += 1
            row = committed.loc[[twin]].assign(annuitant_age=age, duration_mth=-k)
            if str(row["dependant_present"].iloc[0]) == "True":
                row = row.assign(dependant_age=age)
            row.index = pd.Index([top], name="point_id")
            rows.append(row)
            frames.append((top, 12 * (115 - age) + k, k, heads))
    return _sec_inputs(tmp_path, pd.concat(rows)), frames


# modelx warns as its stack trace starts and stops, which is all the test does with it.
@pytest.mark.filterwarnings("ignore:call stack trace:UserWarning")
def test_every_chain_runs_one_cell_a_month_from_a_cold_start(tmp_path):
    """Called cold, each chain runs one cell a month back to ``t_entry()``, no more (D5).

    No number shows how deep a chain runs, and a compiled model runs it on the C stack, so
    a chain of two cells a month, which gives the same numbers, needs twice the stack on
    every platform (F7); ``PA_UK_S``'s payments to date recurse from the start, however old
    the contract.  On a model just read, nothing is cached, so modelx's stack trace counts
    how deep a call runs, against one cell a month back to ``t_entry()`` and
    :data:`CHAIN_OVERHEAD` more, with modelx's recursion limit where the module leaves it:
    each chain head of each of :data:`SHAPES`, in the last month of the frame, each on a
    read of its own and called first.  At each shape's longest cover, every life issued at
    the youngest age its basis projects, now and 120 months on (:func:`_longest_cover`);
    each row's frame is asserted after.  The deepest, ``net_cf`` through the scenario
    basis's payments to date at 1,380 months, 1,379 months back to ``t_entry()``, runs
    1,387 cells, measured at M11: the longest chain the C step's stack must carry
    (UKLIB-SEC-PLAN.md §6.7, *Risk*, which put it at about 1,510).
    """
    folder, frames = _longest_cover(tmp_path)
    found, deepest = [], 0
    for label, months, entry, heads in frames:
        for cell, extra in heads:
            fresh = mx.read_model(folder, name=_name("cold"))
            try:
                p = _point(fresh, label)
                last = months - 1
                args = (last, *(_code(p, a) if isinstance(a, str) else a for a in extra))
                depth, chain = _cold_depth(p, cell, args), last - entry
                deepest = max(deepest, depth)
                assert (p.proj_len(), p.t_entry()) == (months, entry), label
                if not chain <= depth <= chain + CHAIN_OVERHEAD:
                    found.append(f"point {label}: {cell}{args} cold runs {depth} cells "
                                 f"deep, where one cell a month back to t_entry() "
                                 f"{entry} is {chain} and {CHAIN_OVERHEAD} more are "
                                 f"allowed")
            finally:
                fresh.close()
    assert not found, found
    assert LONGEST - 1 <= deepest <= LONGEST - 1 + CHAIN_OVERHEAD, deepest


# ---------------------------------------------------------------------------
# T4 -- the count algebra
#
# BEF_DECR == BEF_NB + pols_new_biz, at every t of every point, is a convention
# (test_new_business_joins_the_count_before_decrements), and is not repeated here.


def test_the_count_is_never_decremented(sec_model):
    """The count on the books is ``policy_count`` from the start to the stop rule (D5).

    Mortality decrements each life's survival, never the count, so on every committed point
    ``pols_if_at(t, BEF_NB)`` is ``pols_if_init()`` at ``t_entry()``, ``policy_count()`` at
    every later month of the frame and 0 outside it: a closed form, which no recursion
    reaches, so that ``BEF_NB`` at the frame's last month evaluates nothing at the month
    before.  And ``pols_if``, the closing obligation measure, is the count times
    ``min(1, max(C, l_a(t+1)) + 1{delta > 0} (1 - l_a(t+1)) l_d(t+1))``, ``PA_UK_S``'s, at
    every month: below the count wherever a life may have died, 0.99999965 at ``t = 0`` on
    the twins of S's points 2, 6 and 7.
    """
    table = sec_model.Data.model_point_table()
    bef_nb = _code(_point(sec_model, 1), "BEF_NB")
    for key, point_id in zip(point_keys(sec_model), table.index):
        p = projection(sec_model, key)
        for t in range(p.proj_len() + 1):
            want = (0.0 if not p.is_active(t) else p.pols_if_init() if t == p.t_entry()
                    else p.policy_count())
            assert p.pols_if_at(t, bef_nb) == want, (point_id, t)
            if not p.is_active(t):
                continue
            la, ld = p.lives_if(t + 1, 1), p.lives_if(t + 1, 2)
            obligation = max(p.certain_floor(t), la)
            if p.dependant_pct() > 0.0:
                obligation += (1.0 - la) * ld
            assert p.pols_if(t) == (p.pols_if_at(t, _code(p, "BEF_DECR"))
                                    * min(1.0, obligation)), (point_id, t)
    fresh = mx.read_model(model_path(SEC), name=_name("closed_form"))
    try:
        p = _point(fresh, 1)
        last = p.proj_len() - 1
        p.pols_if_at(last, bef_nb)
        assert list(p.cells["pols_if_at"].keys()) == [(last, bef_nb)]
    finally:
        fresh.close()
    for point_id in (2, 6, 7):
        assert _point(sec_model, point_id).pols_if(0) == pytest.approx(0.99999965, abs=1e-8)


def test_result_pols_is_s_report_with_the_new_business_beside_it(sec_model, s_model):
    """``result_pols()`` is S's report, column for column, with ``pols_new_biz`` second (D5).

    ``pols_if`` comes first and ``pols_new_biz`` second, then ``PA_UK_S``'s other columns in
    its order (:data:`RESULT_POLS`).  On every twin, all starting at the valuation date, each
    column S holds is S's, to 1e-9 relative at no absolute floor, and ``pols_new_biz`` holds
    the count at ``t = 0`` and 0 in every other month.
    """
    table = sec_model.Data.model_point_table()
    twins = table.index[table["row_kind"] == "twin"].tolist()
    assert twins == sorted(s_model.Data.model_point_table().index)
    for point_id in twins:
        p, s = _point(sec_model, point_id), _point(s_model, point_id)
        pols, s_pols = p.result_pols(), s.result_pols()
        assert list(pols.columns) == RESULT_POLS, point_id
        assert set(s_pols.columns) == set(RESULT_POLS) - {"pols_new_biz"}
        assert frame_mismatches(s_pols, pols, atol=0.0) == [], point_id
        assert list(pols["pols_new_biz"]) == [
            p.policy_count() if t == 0 else 0.0 for t in pols.index], point_id


# What T4 multiplies policy_count by: not a whole number, because a count of contracts need
# not be one, so that a flow which read the count as whole contracts would not follow it.
COUNT_FACTOR = 2.5


def test_scaling_the_count_scales_every_flow_and_no_per_contract_value(sec_model, tmp_path):
    """``policy_count`` is a weight: 2.5 times the count, 2.5 times every flow, the same per
    contract.

    The committed model, swept as the module reads it (``sec_model``), and a copy of its
    table with every count multiplied by :data:`COUNT_FACTOR`, read at the shipped
    References, are compared point by point.  On every point every
    column of ``result_cf`` and the counted columns of ``result_pols`` are 2.5 times the
    committed table's, element by element, to 1e-12 relative: a scaled count is a computed
    float, which may come back from the CSV within two ulps.  ``result_pols``' other
    columns, per contract, are the committed table's exactly.  So is every other cell of
    :data:`COUNTED`, at every argument the sweep of the committed table's point cached: the
    count at each timing and the claims of each kind, which no report shows by kind, among
    them.  And every cell outside :data:`COUNTED` (survival, the payments to date, the
    balance, the floors and factors, the income, both clocks, the flags) agrees bit for bit
    at every argument that sweep cached.  So a flow that dropped the count, or read it as
    whole contracts, which a table of counts of 1 hides from every comparison with S and a
    count doubled hides here, fails.  Each flow of :data:`FLOWS` is nonzero on some point
    (USLIB-SEC-PLAN.md §5.2, T4), the proportionate payment on point 9's twin and on
    point 12.
    """
    table = _committed()
    scaled = mx.read_model(_sec_inputs(tmp_path / "scaled", table.assign(
        policy_count=COUNT_FACTOR * table["policy_count"])), name=_name("scaled"))
    counted = sorted(COUNTED - {"result_cf", "result_pols"})
    nonzero = set()
    try:
        for key, scaled_key in zip(point_keys(sec_model), point_keys(scaled)):
            one, many = projection(sec_model, key), projection(scaled, scaled_key)
            sweep(one)
            for report in REPORTS:
                b, d = one.cells[report](), many.cells[report]()
                assert d.index.equals(b.index) and list(d.columns) == list(b.columns)
                flows = [c for c in b.columns
                         if report == "result_cf" or c in COUNTED_POLS]
                fixed = [c for c in b.columns if c not in flows]
                want = COUNT_FACTOR * b[flows]
                bad = ((d[flows] - want).abs() > 1e-12 * want.abs()).any()
                assert not bad.any(), (key, report, list(bad[bad].index))
                assert d[fixed].equals(b[fixed]), (key, report)
                if report == "result_cf":
                    nonzero |= {c for c in FLOWS if (b[c] != 0.0).any()}
            for name in counted:
                for args in _cached_args(one.cells[name]):
                    want = COUNT_FACTOR * one.cells[name](*args)
                    got = many.cells[name](*args)
                    assert abs(got - want) <= 1e-12 * abs(want), (key, name, args, got, want)
            assert twin_mismatches(one, many, exempt=TWIN_EXEMPT_DEFAULT | COUNTED,
                                   rtol=0.0, atol=0.0) == []
            _release(scaled, scaled_key)
    finally:
        scaled.close()
    assert set(FLOWS) <= nonzero, f"0 on every point: {sorted(set(FLOWS) - nonzero)}"


def _month_on(p):
    """The state point ``p`` carries into its month 1, as the table's opening columns write
    it: what this model would read restated a month on."""
    d = p.duration_mth(1)
    linked = p.is_lpi5() or p.is_rpi_catchup()
    year = max(d - 1, 0) // 12 + 1
    state = {"duration_mth": d, "lives_if_init_1": p.lives_if(1, 1),
             "lives_if_init_2": p.lives_if(1, 2),
             "cum_annuity_all_init": p.cum_annuity_all(1)}
    if linked:
        state["annual_income_init"] = p.annual_income(year)
    if p.is_rpi_catchup():
        state["rpi_peak_init"] = p.rpi_peak(year - 1) / p.rpi_index(year - 1)
    if linked and p.vp_pct() > 0.0 and p.is_first_death():
        state["cum_annuity_pp_init"] = p.cum_annuity_pp(d, "ANNUITANT")
    return state


def test_a_point_restated_a_month_on_continues_its_own_flows(tmp_path):
    """The state a point carries into a month is the state its flows are made of (T4).

    Each point in payment on the committed table is restated a month on, opened with what
    this model carries into its month 1 (:func:`_month_on`): its count, unchanged, since the
    count is never decremented; each life's survival at time 1; the payments to date there;
    and on RPI-linked escalation the income of the policy year under way before any month-1
    anniversary, the ratchet's peak over the latest index and the annuitant's payments to
    date.  The restatement must continue the point's own frames, its row ``t`` the point's
    row ``t + 1``, in ``result_cf`` and ``result_pols``, every flow among them, to 1e-9
    relative, floored at 1e-9 for what a state read back from the CSV an ulp off moves about
    0.  A point whose frame ends in its first month has no month 1, and is left out.  Both
    models run at an inflation rate of 0, set on each as it is read (K7): the restatement
    moves the valuation date a month on, and expense inflation, on the valuation clock,
    would step a month apart by design (D7).  The restatement shows the opening state
    complete on this model's own states, the RPI history read under an RPI of its own
    among them, which S's at the shipped rate do not reach, as the splice shows it on S's;
    and the rated life at 575, restated on its anniversary at 576, crosses the month-0
    rule again.  Ten points: the joint point at 635 is the one with a one-month frame.
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
            top += 1
            row = table.loc[[label]].assign(**_month_on(p))
            row.index = pd.Index([top], name="point_id")
            rows.append(row)
            pairs.append((label, top))
        frames = {label: {report: _point(model, label).cells[report]()
                          for report in REPORTS}
                  for label, _ in pairs}
    finally:
        model.close()
    assert len(pairs) == 10
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


# ---------------------------------------------------------------------------
# T5 -- validation
#
# Each malformed table is the committed one with one fault.  The checks run over the whole
# table as it is read, in Data, and the message names the file it read and the column or
# every point at fault.  A blank cell reads as NaN, and so does a text cell once the checks
# coerce the column to numbers, so each is refused as a count, a duration or a state that
# is not a number.  The repeated point_id holds another contract under the same label, as a
# bad extract would, so that the check must look at the labels and not at whole rows.  The
# point_ids are the committed table's: 1 to 10 the twins of S's points; 11, the worked
# example at 17, the annuitant dead; 12, the proportionate payment's point at 16; 13, the
# guarantee's point at 120; 14, the LPI point at 24; 15, the catch-up point at 30; 16, the
# table basis's joint point at 101; 17, last-survivor value protection at 170; 18, the
# rated single life at 575; 19, the table basis's joint point at 635; 20, the catch-up point
# starting 13 months on; 21, the catch-up point at 60 under an RPI of -2%; 22, the LPI
# point at 42 under 8%.  A {file} in a message is the table's filename: every case is read
# by one model, from a file of its own (the malformed fixture).


def _drop(column):
    return lambda table: table.drop(columns=column)


def _rule(column, rule, points, on=""):
    """The message of one column's rule."""
    return f"{{file}}: {column} must be {rule}{on}; it is not at point_id {points}"


JOINT = " on a contract with a dependant"
LINKED = " on RPI-linked escalation, lpi5 or rpi_catchup"
CATCHUP = " on rpi_catchup escalation"
PAID = " on RPI-linked escalation with value protection on the first death"
START = ("{file}: {column} must hold its value at the start date on a contract not yet in "
         "payment, duration_mth 0 or less: each covered life alive, nothing paid, the first "
         "year's income and a peak of 1; it does not at point_id {points}")
FIRST_YEAR = ("{file}: {column} must hold its first year's value on a contract in its "
              "first policy year, duration_mth 1 to 12, before which no anniversary has "
              "passed: the first year's income and a peak of 1; it does not at point_id "
              "{points}")
STATUS = ("{file}: on the scenario basis lives_if_init_{life} must be 1 while the life "
          "survives to the valuation date, death_mth_{life} blank or duration_mth or "
          "later, and 0 once it has died; it is not at point_id {points}")
DEATH = ("{file}: death_mth_{life} must be blank or a whole number of months, 0 or more, a "
         "policy month, on the scenario basis; it is not at point_id {points}")


def _start(column, points):
    return START.replace("{column}", column).replace("{points}", str(points))


def _first_year(column, points):
    return FIRST_YEAR.replace("{column}", column).replace("{points}", str(points))


def _status(life, points):
    return STATUS.replace("{life}", str(life)).replace("{points}", str(points))


def _death(life, points):
    return DEATH.replace("{life}", str(life)).replace("{points}", str(points))


MALFORMED = [
    *[(f"no {column} column", _drop(column), f"{{file}} has no {column} column")
      for column in ("policy_count", "duration_mth", *STATE)],
    ("a repeated point_id",
     lambda t: pd.concat([t, t.loc[[16]].assign(policy_id="PA-900099")]),
     "{file}: point_id [16] appears more than once"),
    ("a negative count", _set("policy_count", [16], -0.1),
     _rule("policy_count", "a number, zero or more", [16])),
    ("a blank count", _set("policy_count", [11], float("nan")),
     _rule("policy_count", "a number, zero or more", [11])),
    ("two text counts", _set("policy_count", [14, 21], "abc"),
     _rule("policy_count", "a number, zero or more", [14, 21])),
    ("an infinite count", _set("policy_count", [1], float("inf")),
     _rule("policy_count", "a number, zero or more", [1])),
    ("a fractional duration", _set("duration_mth", [16], 101.5),
     "{file}: duration_mth must be a whole number of months; it is not at point_id [16]"),
    ("a blank duration", _set("duration_mth", [20], float("nan")),
     "{file}: duration_mth must be a whole number of months; it is not at point_id [20]"),
    ("a text duration", _set("duration_mth", [13], "x120"),
     "{file}: duration_mth must be a whole number of months; it is not at point_id [13]"),
    ("durations of 2**53 months at two points", _set("duration_mth", [16, 19], 2.0 ** 53),
     "{file}: duration_mth must be below 2**53 months; it is not at point_id [16, 19]"),
    ("starting beyond the horizon", _set("duration_mth", [20], -121),
     "{file}: duration_mth must be -120 or more, an annuity starting at most 120 months "
     "after the valuation date; it is not at point_id [20]"),
    # PA_UK_S reads each flag through bool(), which reads a blank, NaN, as True.
    ("a blank dependant flag", _set("dependant_present", [5], float("nan")),
     _rule("dependant_present", "True or False", [5])),
    ("a blank overlap", _set("overlap", [3], float("nan")),
     _rule("overlap", "True or False", [3])),
    ("a blank proportion", _set("proportion", [2], float("nan")),
     _rule("proportion", "True or False", [2])),
    ("a flag written yes", _set("overlap", [4], "yes"),
     _rule("overlap", "True or False", [4])),
    ("a flag written 1", _set("dependant_present", [1], 1),
     _rule("dependant_present", "True or False", [1])),
    # PA_UK_S truncates each of these with int().
    ("a fractional annuitant age", _set("annuitant_age", [2], 65.5),
     _rule("annuitant_age", "a whole number below 2**53", [2])),
    ("a blank annuitant age", _set("annuitant_age", [3], float("nan")),
     _rule("annuitant_age", "a whole number below 2**53", [3])),
    ("an annuitant age of 2**53", _set("annuitant_age", [4], 2.0 ** 53),
     _rule("annuitant_age", "a whole number below 2**53", [4])),
    ("an unknown annuitant sex", _set("annuitant_sex", [5], "X"),
     _rule("annuitant_sex", "M or F", [5])),
    ("a rating below 1", _set("rating_multiplier", [8], 0.9),
     _rule("rating_multiplier", "a finite number, 1 or more", [8])),
    ("an infinite rating", _set("rating_multiplier", [2], float("inf")),
     _rule("rating_multiplier", "a finite number, 1 or more", [2])),
    ("a blank rating", _set("rating_multiplier", [1], float("nan")),
     _rule("rating_multiplier", "a finite number, 1 or more", [1])),
    ("a negative purchase price", _set("purchase_price", [1], -1.0),
     _rule("purchase_price", "a finite number, 0 or more", [1])),
    ("an infinite purchase price", _set("purchase_price", [6], float("inf")),
     _rule("purchase_price", "a finite number, 0 or more", [6])),
    ("a negative income", _set("annual_income", [7], -1.0),
     _rule("annual_income", "a finite number, 0 or more", [7])),
    ("a blank income", _set("annual_income", [2], float("nan")),
     _rule("annual_income", "a finite number, 0 or more", [2])),
    ("a fractional frequency", _set("frequency", [1], 4.5),
     _rule("frequency", "12, 4, 2 or 1", [1])),
    ("a frequency of 3", _set("frequency", [5], 3),
     _rule("frequency", "12, 4, 2 or 1", [5])),
    ("a fractional guarantee", _set("guarantee_months", [3], 120.5),
     _rule("guarantee_months", "a whole number of months, 0 or more, below 2**53", [3])),
    ("a negative guarantee", _set("guarantee_months", [4], -12),
     _rule("guarantee_months", "a whole number of months, 0 or more, below 2**53", [4])),
    ("value protection past 1", _set("vp_pct", [1], 1.5),
     _rule("vp_pct", "a number from 0 to 1", [1])),
    ("negative value protection", _set("vp_pct", [10], -0.1),
     _rule("vp_pct", "a number from 0 to 1", [10])),
    ("blank value protection", _set("vp_pct", [2], float("nan")),
     _rule("vp_pct", "a number from 0 to 1", [2])),
    ("a fractional start year", _set("start_year", [6], 2026.5),
     _rule("start_year", "a whole number below 2**53", [6])),
    ("a text start year", _set("start_year", [7], "MMXXVI"),
     _rule("start_year", "a whole number below 2**53", [7])),
    ("a fractional dependant age", _set("dependant_age", [2], 62.5),
     _rule("dependant_age", "a whole number below 2**53", [2], JOINT)),
    ("a blank dependant age", _set("dependant_age", [1], float("nan")),
     _rule("dependant_age", "a whole number below 2**53", [1], JOINT)),
    ("an unknown dependant sex", _set("dependant_sex", [6], "W"),
     _rule("dependant_sex", "M or F", [6], JOINT)),
    ("a dependant rating below 1", _set("dependant_rating", [7], 0.5),
     _rule("dependant_rating", "a finite number, 1 or more", [7], JOINT)),
    ("a dependant's share past 1", _set("dependant_pct", [3], 1.2),
     _rule("dependant_pct", "a number from 0 to 1", [3], JOINT)),
    ("a blank dependant's share", _set("dependant_pct", [10], float("nan")),
     _rule("dependant_pct", "a number from 0 to 1", [10], JOINT)),
    ("a negative fixed escalation", _set("escalation_rate", [1], -0.01),
     _rule("escalation_rate", "a finite number, 0 or more", [1], " on fixed escalation")),
    ("a blank fixed escalation", _set("escalation_rate", [9], float("nan")),
     _rule("escalation_rate", "a finite number, 0 or more", [9], " on fixed escalation")),
    # PA_UK_S truncates a fractional month of death, and reads a negative one as a life
    # that never dies.
    ("a fractional death month", _set("death_mth_1", [1], 16.5), _death(1, [1])),
    ("a negative death month", _set("death_mth_1", [9], -1), _death(1, [9])),
    ("a text death month", _set("death_mth_2", [10], "x"), _death(2, [10])),
    ("survival past 1", _set("lives_if_init_1", [16], 1.5),
     "{file}: lives_if_init_1 must be a probability, 0 to 1; it is not at point_id [16]"),
    ("negative survival", _set("lives_if_init_2", [16], -0.1),
     "{file}: lives_if_init_2 must be a probability, 0 to 1; it is not at point_id [16]"),
    ("blank survival", _set("lives_if_init_1", [19], float("nan")),
     "{file}: lives_if_init_1 must be a probability, 0 to 1; it is not at point_id [19]"),
    ("a second life on a single-life contract", _set("lives_if_init_2", [18], 0.5),
     "{file}: lives_if_init_2 must be 0 on a single-life contract, which covers no second "
     "life; it is not at point_id [18]"),
    ("negative payments to date", _set("cum_annuity_all_init", [16], -1.0),
     _rule("cum_annuity_all_init", "a finite number, 0 or more", [16])),
    ("blank payments to date", _set("cum_annuity_all_init", [11], float("nan")),
     _rule("cum_annuity_all_init", "a finite number, 0 or more", [11])),
    ("a blank RPI income", _set("annual_income_init", [14], float("nan")),
     _rule("annual_income_init", "a finite number, 0 or more", [14], LINKED)),
    ("an infinite RPI income", _set("annual_income_init", [15], float("inf")),
     _rule("annual_income_init", "a finite number, 0 or more", [15], LINKED)),
    ("a peak below the index", _set("rpi_peak_init", [15], 0.99),
     _rule("rpi_peak_init", "a finite number, 1 or more", [15], CATCHUP)),
    ("a blank peak", _set("rpi_peak_init", [21], float("nan")),
     _rule("rpi_peak_init", "a finite number, 1 or more", [21], CATCHUP)),
    ("blank annuitant payments", _set("cum_annuity_pp_init", [14], float("nan")),
     _rule("cum_annuity_pp_init", "a finite number, 0 or more", [14], PAID)),
    ("negative annuitant payments", _set("cum_annuity_pp_init", [21], -1.0),
     _rule("cum_annuity_pp_init", "a finite number, 0 or more", [21], PAID)),
    ("survival at the start of a contract not yet in payment",
     _set("lives_if_init_1", [20], 0.99), _start("lives_if_init_1", [20])),
    ("a dead dependant at the start", _set("lives_if_init_2", [1], 0.0),
     _start("lives_if_init_2", [1])),
    ("payments before the start", _set("cum_annuity_all_init", [6], 10.0),
     _start("cum_annuity_all_init", [6])),
    ("an RPI income at the start other than the first year's",
     _set("annual_income_init", [20], 5562.0), _start("annual_income_init", [20])),
    ("a peak at the start other than 1", _set("rpi_peak_init", [6], 1.05),
     _start("rpi_peak_init", [6])),
    ("annuitant payments before the start", _set("cum_annuity_pp_init", [7], 1350.0),
     _start("cum_annuity_pp_init", [7])),
    ("an RPI income in the first year other than the first",
     _then(_set("duration_mth", [15], 12), _set("annual_income_init", [15], 5562.0)),
     _first_year("annual_income_init", [15])),
    ("a peak in the first year other than 1",
     _then(_set("duration_mth", [21], 7), _set("annual_income_init", [21], 5400.0),
           _set("rpi_peak_init", [21], 1.01)),
     _first_year("rpi_peak_init", [21])),
    ("a scenario annuitant alive after the death", _set("lives_if_init_1", [11], 1.0),
     _status(1, [11])),
    ("a scenario annuitant dead before the death", _set("lives_if_init_1", [12], 0.0),
     _status(1, [12])),
    ("a scenario dependant dead with no death", _set("lives_if_init_2", [17], 0.0),
     _status(2, [17])),
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


# The labels an extract carries: the committed points' in reverse, from 122 down, so that
# a label is neither a position plus one nor in the order of the rows.
EXTRACT_LABELS = tuple(range(122, 100, -1))


def _relabelled(message, relabel):
    """``message`` with every ``point_id [...]`` list it holds relabelled by ``relabel``."""
    def labels(match):
        return "point_id [" + ", ".join(str(relabel[int(p)]) for p in
                                        match.group(1).split(", ")) + "]"
    return re.sub(r"point_id \[(\d+(?:, \d+)*)\]", labels, message)


@pytest.fixture(scope="module")
def malformed_extract(tmp_path_factory):
    """:data:`MALFORMED`'s tables as an extract labels its rows, each a file of its own.

    Each case's table is the committed one with its fault, made by its own labels, and then
    relabelled :data:`EXTRACT_LABELS`, in order, so that no label is its position plus one.
    One model reads them all, as :func:`malformed` reads its files.  Returns ``(model,
    {case: filename}, {committed label: extract label})``.
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


# A text value no decode knows, as (case, the table's edit, the point, PA_UK_S's message).
# Data leaves these columns to the decodes, which read and validate each as PA_UK_S's label
# accessor does, so that the refusal is PA_UK_S's own, through a projection of the point.
UNDECODABLE = [
    ("an unknown timing", _set("timing", [1], "monthly"), 1, "invalid timing"),
    ("a timing in capitals", _set("timing", [5], "Advance"), 5, "invalid timing"),
    ("an unknown escalation", _set("escalation_type", [2], "rpi"), 2,
     "invalid escalation_type"),
    ("an escalation with a space", _set("escalation_type", [7], "lpi5 "), 7,
     "invalid escalation_type"),
    ("an unknown value-protection basis", _set("vp_basis", [10], "last"), 10,
     "invalid vp_basis"),
    ("an unknown mortality basis", _set("mort_basis", [2], "stochastic"), 2,
     "invalid mort_basis"),
    ("the proportionate payment in advance",
     _then(_set("timing", [9], "advance")), 9,
     "proportion applies to arrears payments only"),
    ("a fixed escalation past its cap", _set("escalation_rate", [1], 0.11), 1,
     "fixed escalation exceeds the contractual cap"),
]


@pytest.mark.parametrize("case, edit, point, message", UNDECODABLE,
                         ids=[c[0] for c in UNDECODABLE])
def test_a_text_value_no_decode_knows_raises_pa_uk_s_message(tmp_path, case, edit, point,
                                                             message):
    """Each decode reads and validates its column as ``PA_UK_S``'s accessor does (§6.7).

    ``timing``, ``escalation_type``, ``vp_basis`` and ``mort_basis`` are decoded into flags,
    so that no projection cell compares text, and each decode raises ``PA_UK_S``'s own
    message for a value its accessor refuses, through a projection of the point; so do the
    proportion rule and the fixed escalation's cap, which ``PA_UK_S`` checks where it reads
    them.  ``Data`` reads the table, since the checks are the accessors'.
    """
    model = _read_edited(tmp_path, edit)
    try:
        assert len(model.Data.model_point_table()) == len(_committed())
        _refused(_point(model, point).result_cf, message)
    finally:
        model.close()


def test_the_future_horizon_is_a_reference_that_bounds_future_business(tmp_path):
    """``Data.future_horizon_mth`` refuses an annuity starting later than it, and 0 refuses
    all.

    The committed table's one future point starts 13 months on.  It reads at the shipped
    120 months and at 13, the shortest horizon that admits it, and is refused at 12, by
    name.  At 0 the model takes no future new business, D4's fallback for a product that
    cannot support it, and the message says so.  A horizon that is not a whole number of
    months, 0 or more, is itself refused, a NaN and an infinity among them.  Setting the
    Reference clears the table, so each value is read afresh.
    """
    future = _label(_committed(), "future", 6, -13)
    later = (f"{TABLE}: duration_mth must be -12 or more, an annuity starting at most 12 "
             f"months after the valuation date; it is not at point_id [{future}]")
    no_future = (f"{TABLE}: duration_mth must be 0 or more: this model takes no future new "
                 f"business; it is not at point_id [{future}]")
    model = mx.read_model(_sec_inputs(tmp_path, _committed()), name=_name("horizon"))
    try:
        assert model.Data.future_horizon_mth == 120
        cases = [(13, None), (12, later), (0, no_future), (120, None), (13.0, None)]
        cases += [(value, "future_horizon_mth must be a whole number of months, 0 or more, "
                          f"not {float(value)}")
                  for value in (-1, 12.5, math.nan, math.inf)]
        for horizon, refusal in cases:
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


def test_a_point_at_its_stop_is_refused_by_proj_len(tmp_path):
    """A contract at its stop rule has no frame, and ``proj_len()`` refuses it by name.

    The table basis's joint point in its last month, 635, is moved on to ``duration_mth``
    636, the stop rule of its 65/62 pair.  That is a rule of the product, not of the table:
    it needs the limiting age, a Reference, read where the frame is defined, so the table
    reads, and the point is refused on its first projection, rather than projecting
    nothing.  A loop over the block would meet the point only when it reached it, after
    projecting the points before it, so ``run_sec.py --block``, run beside the table, asks
    every point for its frame first: it fails naming the point, and prints nothing before.
    And one month earlier, 635, projects one month, its dependant's survival carried in.
    """
    moved = _label(_committed(), "derived", 2, 635)
    model = _read_edited(tmp_path, _set("duration_mth", [moved], 636))
    message = (f"point_id {moved}: duration_mth 636 is at or past the end of the "
               f"projection, policy month 636")
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
    model = _read_edited(tmp_path / "last", lambda t: t)
    try:
        p = _point(model, moved)
        df = p.result_cf()
        assert len(df) == 1 and p.lives_if(0, 2) == _committed().at[moved, "lives_if_init_2"]
        assert df["annuity_payments"].iloc[0] > 0.0
    finally:
        model.close()


# A contract owing nothing after the valuation date, as (case, the table's edit, the point,
# the message, or None where it is accepted).  Every covered life dead, and no guarantee
# left: no instalment, no dependant's income and no value-protection lump sum to pay.  Point
# 16 is the table basis's joint point at 101, value protection on the first death and no
# guarantee; 13 the guarantee's point at 120, its guarantee ended there, on the scenario
# basis, its annuitant dead in policy month 16, here its dependant written dead in 50.
OWING_NOTHING = [
    ("both lives dead, no guarantee",
     _then(_set("lives_if_init_1", [16], 0.0), _set("lives_if_init_2", [16], 0.0)), 16,
     "point_id 16: duration_mth 101: no payment is owed after the valuation date: every "
     "covered life has died, and the contract has no guarantee"),
    ("both lives dead, the guarantee ended",
     _then(_set("death_mth_2", [13], 50.0), _set("lives_if_init_2", [13], 0.0)), 13,
     "point_id 13: duration_mth 120: no payment is owed after the valuation date: every "
     "covered life has died, and the guarantee ended at policy month 120"),
    ("both lives dead, a month of the guarantee left",
     _then(_set("death_mth_2", [13], 50.0), _set("lives_if_init_2", [13], 0.0),
           _set("duration_mth", [13], 119)), 13, None),
    ("the annuitant dead, the dependant alive",
     _set("lives_if_init_1", [16], 0.0), 16, None),
    ("the dependant alive at a share of 0",
     _then(_set("lives_if_init_1", [16], 0.0), _set("dependant_pct", [16], 0.0)), 16,
     None),
]


@pytest.mark.parametrize("case, edit, point, message", OWING_NOTHING,
                         ids=[c[0] for c in OWING_NOTHING])
def test_a_contract_owing_nothing_is_refused_by_proj_len(tmp_path, case, edit, point,
                                                         message):
    """``proj_len()`` refuses a contract that owes nothing after the valuation date.

    In payment, its guarantee over and every covered life dead, its last payment was made
    before the valuation date, and an in-force extract should not carry it: SPIA's rule,
    worded by whether it had a guarantee (:data:`OWING_NOTHING`).  A month of the guarantee
    left owes its instalments, and a dependant alive owes the dependant's income, or on the
    last-survivor basis the lump sum, and each projects; at a dependant's share of 0 on the
    first-death basis the contract projects zeros, its obligation measure and so its
    maintenance among them, the rule reading the lives and the guarantee alone.
    """
    model = _read_edited(tmp_path, edit)
    try:
        assert len(model.Data.model_point_table()) == len(_committed())
        p = _point(model, point)
        if message is None:
            assert p.proj_len() > 0 and len(p.result_cf()) == p.proj_len()
        else:
            _refused(p.result_cf, message)
    finally:
        model.close()


# What the contract does not issue, or the model cannot project, refused by proj_len(), as
# (case, the table's edit, the References set, the point, the message, and the frame the
# point projects at the shipped References, or None).  Data reads an age as a whole number,
# so each reads.  PA_UK_S projects any age on the scenario basis, so the youngest age the
# contract allows is issue_age_min, 0, and a negative age of either life is refused; and a
# guarantee longer than the longest frame the youngest life allows, 12 x (115 - 0) =
# 1,380 months, which the compiled model's caches are sized from.  Each bound is refused
# just past it here, and accepted at it in the edges test, and each, moved past a committed
# twin, refuses it, which at the shipped bound projects its frame: the issue age raised past
# either life's, and the limiting age lowered to 9, where the longest frame, 108 months, is
# shorter than the guarantee.  Point 1 is the worked example, 65 with a dependant of 62; 3
# its twin with a 120-month guarantee.
NOT_ISSUED = [
    ("an annuitant aged -1", _set("annuitant_age", [1], -1), {}, 1,
     "point_id 1: life 1's issue age, -1, is below issue_age_min, 0", None),
    ("a dependant aged -1", _set("dependant_age", [1], -1), {}, 1,
     "point_id 1: life 2's issue age, -1, is below issue_age_min, 0", None),
    ("an annuitant below a bound raised to 66", None, {"issue_age_min": 66}, 1,
     "point_id 1: life 1's issue age, 65, is below issue_age_min, 66", 636),
    ("a dependant below a bound raised to 63", None, {"issue_age_min": 63}, 1,
     "point_id 1: life 2's issue age, 62, is below issue_age_min, 63", 636),
    ("a guarantee of 1,381 months", _set("guarantee_months", [3], 1381), {}, 3,
     "point_id 3: the guarantee, 1381 months, is longer than 1380 months, 12 x (omega_age "
     "- issue_age_min), the longest frame from the start date", None),
    ("a guarantee past a limiting age lowered to 9", None, {"omega_age": 9}, 3,
     "point_id 3: the guarantee, 120 months, is longer than 108 months, 12 x (omega_age "
     "- issue_age_min), the longest frame from the start date", 636),
]


@pytest.mark.parametrize("case, edit, refs, point, message, frame", NOT_ISSUED,
                         ids=[c[0] for c in NOT_ISSUED])
def test_a_point_the_contract_does_not_issue_is_refused_by_proj_len(tmp_path, case, edit,
                                                                    refs, point, message,
                                                                    frame):
    """``proj_len()`` refuses a point outside the contract's bounds, naming both (§6.7).

    ``PA_UK_S`` projects any age on the scenario basis, a negative one among them, and any
    guarantee, and the compiled model's caches will be sized from the contract: a frame of
    at most ``12 x (omega_age - issue_age_min)`` months from the start and the horizon.  So
    the frame refuses such a point, naming it, as it refuses a point at its stop, and every
    report with it (:data:`NOT_ISSUED`): each bound just past it, and each bound moved past a
    committed point, which projects at the shipped bound, on a model read afresh.  The
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


# Each Reference proj_len() holds to a domain, at both edges of it, as (case, the References
# set, the point, the refusal, or None where proj_len() accepts them; proj_len's docstring
# gives each domain's reason).  NaN and the infinities are outside every domain: PA_UK_S
# reads several of them through a min or a max whose bound comes first, where a NaN is lost,
# and the rest through a power.  A finite domain's upper edge is the largest float, accepted.
# The integer References are whole numbers below 2**53, which the compiled model holds as
# long long, printed through int() once whole: each is refused at a fraction and at exactly
# 2**53.  Each is held on the points that read it: on every point, the expense and the
# inflation, held on point 1; on the table basis the mortality References, on point 2; on
# fixed escalation its cap, on point 1; on RPI-linked escalation rpi_rate, on points 6 and
# 7; on lpi5 its cap, on point 7.  A point that does not read one projects whatever it is,
# point 1 a NaN rpi_rate and a NaN annuitant_adj, point 2 a NaN esc_lpi_cap.
BIG = 1.7976931348623157e308
WHOLE = 2.0 ** 53
BELOW_0 = math.nextafter(0.0, -1.0)
BELOW_MINUS_1 = math.nextafter(-1.0, -2.0)
ABOVE_MINUS_1 = math.nextafter(-1.0, 0.0)
BELOW_1 = math.nextafter(1.0, 0.0)


def _domain(ref, rule, point, accepted, refused):
    """The DOMAINS cases of ``ref`` on ``point``: each of ``accepted`` projects, each of
    ``refused`` is refused by the domain's ``rule``, and NaN and the infinities by it
    too."""
    message = f"point_id {point}: {ref} must be {rule}, not {{}}"
    cases = [(f"{ref}={value!r} on {point}", {ref: value}, point, None)
             for value in accepted]
    return cases + [(f"{ref}={value!r} on {point}", {ref: value}, point,
                     message.format(float(value)))
                    for value in (*refused, math.nan, math.inf, -math.inf)]


def _whole_domain(ref, point, accepted, below=True):
    """The DOMAINS cases of an integer Reference: a whole number below 2**53, and 0 or more
    where ``below``, printed through int() once whole."""
    whole = f"point_id {point}: {ref} must be a whole number below 2**53, not {{}}"
    cases = [(f"{ref}={value!r} on {point}", {ref: value}, point, None)
             for value in accepted]
    if below:
        cases.append((f"{ref}=-1 on {point}", {ref: -1}, point,
                      f"point_id {point}: {ref} must be 0 or more, not -1"))
    return cases + [(f"{ref}={value!r} on {point}", {ref: value}, point,
                     whole.format(float(value)))
                    for value in (0.5, 2023.5, WHOLE, 1e300, math.nan, math.inf,
                                  -math.inf)]


OMEGA_TABLE = ("point_id 2: omega_age must be at most 116, a year past mort_table.csv's "
               "last age, on the table basis, not {}")
DOMAINS = [
    *_domain("expense_maint", "a finite number, 0 or more", 1, (0.0, BIG), (BELOW_0,)),
    *_domain("inflation_rate", "a finite number, -1 or more", 1, (-1.0, BIG),
             (BELOW_MINUS_1,)),
    *_domain("annuitant_adj", "a finite number, 0 or more", 2, (0.0, BIG), (BELOW_0,)),
    *_domain("improve_rate_base", "a finite number below 1", 2, (-BIG, BELOW_1), (1.0,)),
    *_domain("improve_flat_age", "a finite number", 2, (-BIG, BIG), ()),
    *_domain("improve_taper_age", "a finite number", 2, (-BIG, BIG), ()),
    *_whole_domain("mort_table_year", 2, (0, 2023, WHOLE - 1), below=False),
    *_domain("esc_fixed_cap", "a finite number, 0 or more", 1, (0.03, BIG),
             (BELOW_0,)),
    ("esc_fixed_cap=0.0 on 1", {"esc_fixed_cap": 0.0}, 1, None),
    *_domain("rpi_rate", "a finite number above -1", 7, (ABOVE_MINUS_1, BIG), (-1.0,)),
    *_domain("rpi_rate", "a finite number above -1", 6, (ABOVE_MINUS_1, BIG), (-1.0,)),
    *_domain("esc_lpi_cap", "a finite number, 0 or more", 7, (0.0, BIG), (BELOW_0,)),
    *_whole_domain("issue_age_min", 1, (0,)),
    ("issue_age_min=2**53-1 on 1", {"issue_age_min": WHOLE - 1}, 1,
     f"point_id 1: life 1's issue age, 65, is below issue_age_min, {int(WHOLE - 1)}"),
    *_whole_domain("omega_age", 1, (115, 116, 2000), below=False),
    ("omega_age=0 on 1", {"omega_age": 0}, 1,
     "point_id 1: omega_age must be above issue_age_min, 0, not 0"),
    ("omega_age=-5 on 1", {"omega_age": -5}, 1,
     "point_id 1: omega_age must be above issue_age_min, 0, not -5"),
    ("omega_age=116 on 2", {"omega_age": 116}, 2, None),
    ("omega_age=117 on 2", {"omega_age": 117}, 2, OMEGA_TABLE.format(117)),
    ("rpi_rate=nan on 1", {"rpi_rate": math.nan}, 1, None),
    ("annuitant_adj=nan on 1", {"annuitant_adj": math.nan}, 1, None),
    ("esc_lpi_cap=nan on 6", {"esc_lpi_cap": math.nan}, 6, None),
    ("esc_fixed_cap=nan on 7", {"esc_fixed_cap": math.nan}, 7, None),
]


@pytest.mark.parametrize("case, refs, point, message", DOMAINS, ids=[c[0] for c in DOMAINS])
def test_each_reference_is_held_to_its_domain_at_both_edges(case, refs, point, message):
    """``proj_len()`` holds each Reference to its domain, NaN and the infinities outside it.

    ``PA_UK_S`` reads ``rpi_rate`` through the LPI's floor, ``max(0, rpi_rate)``, its bound
    first, so that a NaN reads as no increase, and through the index's power, where a rate
    of -1 or below is no price level; ``esc_lpi_cap`` through the cap, ``min(cap, ...)``,
    its bound first, which an infinity switches off; ``esc_fixed_cap`` in a comparison a
    NaN switches off; the mortality References through the cap ``min(q, 1.0)``, which reads
    an infinity as certain death, and the improvement's power; and the integer References in
    comparisons a NaN switches off, the limiting age sizing every frame.  The frame refuses
    each such Reference, by name, before it projects anything, and every report with it, at
    the nearest value outside each edge of its domain, and accepts the edge itself
    (:data:`DOMAINS`), on the points that read it; a point that does not read it projects
    whatever it is.  Each case sets its References on a model just read (K7).
    """
    model = mx.read_model(model_path(SEC), name=_name("domain"))
    try:
        for ref, value in refs.items():
            setattr(model.Projection, ref, value)
        p = _row(model, "twin", point, 0)
        if message is None:
            assert p.proj_len() > 0
        else:
            _refused(p.result_cf, message)
    finally:
        model.close()


# An income a rate or a history past every amount of money makes, each from References and
# columns inside their domains, as (case, the table's edit, the References set, the S point
# and month of the row, and the year and the reason the refusal names).  The LPI twin under a
# cap and an RPI of 1e300 escalates by that factor a year, past the floats in its third
# year; the fixed twin under an escalation and a cap of 1e300 too.  The table basis's joint
# point at 635 with a first year's income of 1e308 compounds 3% a year at the valuation
# date's key, the one loop, past the floats in its 21st year; and the catch-up point at 30
# carrying an income of 1e308 doubles it under an RPI of 100% at its next anniversary.
INCOMES = [
    ("the LPI past the floats", None, {"esc_lpi_cap": 1e300, "rpi_rate": 1e300}, (7, 0),
     3, "under rpi_rate 1e+300 and esc_lpi_cap 1e+300"),
    ("a fixed escalation past the floats", _set("escalation_rate", [1], 1e300),
     {"esc_fixed_cap": 1e300}, (1, 0), 3, "under escalation_rate 1e+300"),
    ("a fixed income compounded past the floats at the valuation date",
     lambda t: _set("annual_income", [_label(t, "derived", 2, 635)], 1e308)(t), {},
     (2, 635), 21, "under escalation_rate 0.03"),
    ("a catch-up income doubled past the floats",
     lambda t: _set("annual_income_init", [_label(t, "derived", 6, 30)], 1e308)(t),
     {"rpi_rate": 1.0}, (6, 30), 4,
     "under rpi_rate 1.0, annual_income_init 1e+308 and rpi_peak_init 1.0"),
]


@pytest.mark.parametrize("case, edit, refs, row, year, reason", INCOMES,
                         ids=[c[0] for c in INCOMES])
def test_an_income_past_the_floats_is_refused_in_its_year(tmp_path, case, edit, refs, row,
                                                         year, reason):
    """An income that leaves the floats is refused in the year it first does (§6.7).

    Every Reference and column here is inside its domain, and the table reads, but each
    case's income escalates past the largest float (:data:`INCOMES`), where the payments to
    date would carry an infinity on and the value-protection balance, ``max(0, vP - G)``,
    its bound first, would read it as no balance at all.  ``annual_income`` refuses it in
    the year it first is, naming the point, the year and what made it, and so does every
    report that reads it, through the recursion or the valuation date's loop alike.  Every
    Reference is set on a model just read (K7).
    """
    model = _read_edited(tmp_path, edit or (lambda t: t))
    try:
        for ref, value in refs.items():
            setattr(model.Projection, ref, value)
        kind = "twin" if row[1] == 0 else "derived"
        label = _label(model.Data.model_point_table(), kind, *row)
        _refused(_point(model, label).result_cf,
                 f"point_id {label}: the income annual_income({year}) is inf, not a finite "
                 f"number, {reason}")
    finally:
        model.close()


def test_the_payments_to_date_past_the_floats_are_refused(tmp_path):
    """Payments to date that leave the floats are refused where they first do.

    ``Data`` holds each column to a finite number, so the largest float reads, and an
    income of 1e300 does; but the next instalment takes the total past the floats, where
    the value-protection balance, ``max(0, vP - G)``, its bound first, would read it as no
    balance.  ``cum_annuity_all`` refuses it on the last-survivor row at 170, at its first
    instalment, in month 0, closing at time 1; and ``cum_annuity_pp`` the annuitant's on
    the catch-up row at 60 at its first instalment, policy month 62, closing at policy time
    63.  Each names the point and the key.
    """
    big = 1.7976931348623157e308
    last = _label(_committed(), "derived", 10, 170)
    frozen = _label(_committed(), "derived", 6, 60)
    model = _read_edited(tmp_path, _then(_set("cum_annuity_all_init", [last], big),
                                         _set("annual_income", [last], 1e300),
                                         _set("cum_annuity_pp_init", [frozen], big),
                                         _set("annual_income_init", [frozen], 1e300)))
    try:
        _refused(_point(model, last).result_cf,
                 f"point_id {last}: the payments to date cum_annuity_all(1) are inf, not a "
                 f"finite number")
        _refused(_point(model, frozen).result_cf,
                 f"point_id {frozen}: the payments to date cum_annuity_pp(63, 'ANNUITANT') "
                 f"are inf, not a finite number")
    finally:
        model.close()


def test_the_edges_of_the_in_force_interface_are_accepted(sec_model, tmp_path):
    """A zero count, whole numbers in any type, the horizon and each bound's edge are read.

    A count of 0 is a point that projects zeros; ``101.0`` is a whole number of months, read
    back as the int the policy clock counts in; an annuity starting 120 months after the
    valuation date, the shipped ``future_horizon_mth``, is the last one the table admits,
    with a frame of 756 months, 636 from its start after 120 before it.  A row valued in its
    first month, 1, holds each life's survival and a payment to date.  And each bound of the
    contract at its edge projects: issue at 0, the youngest the contract allows, a frame of
    1,380 months on the scenario basis, and a guarantee of exactly 1,380 months, the longest
    frame from the start.
    """
    committed = _committed()
    last = _label(committed, "derived", 2, 635)
    future = _label(committed, "future", 6, -13)
    first = _label(committed, "derived", 2, 101)

    def edit(table):
        table = _set("policy_count", [last], 0.0)(table)
        table = table.assign(duration_mth=table["duration_mth"].astype(float))
        table = _set("duration_mth", [future], -120.0)(table)
        table = _set("duration_mth", [first], 1.0)(table)
        table = _set("annuitant_age", [1], 0)(table)
        table = _set("dependant_age", [1], 0)(table)
        return _set("guarantee_months", [3], 1380)(table)

    model = _read_edited(tmp_path, edit)
    try:
        read = model.Data.model_point_table()
        assert read["duration_mth"].dtype == float
        df = _point(model, last).result_cf()
        assert len(df) == 1 and (df == 0.0).all().all()
        p = _point(model, _label(committed, "derived", 6, 30))
        assert p.duration_mth(0) == 30 and type(p.duration_mth(0)) is int
        assert frame_mismatches(
            _point(sec_model, _label(committed, "derived", 6, 30)).result_cf(),
            p.result_cf(), rtol=0, atol=0) == []
        late = _point(model, future)
        assert (late.t_entry(), late.proj_len(), late.pols_new_biz(120)) == (120, 756, 1.0)
        one = _point(model, first)
        assert one.duration_mth_init() == 1 and one.cum_annuity_all_init() > 0.0
        assert len(_point(model, 1).result_cf()) == 1380
        assert len(_point(model, 3).result_cf()) == 1380
        for point in (1, 3):
            assert _point(model, point).check_lives_roll_fwd(), point
    finally:
        model.close()


# proj_len()'s refusal of a contract owing nothing, which S point 8 reaches once the cap
# has killed its rated life, and variants 14, 15 and 16 once both their lives have died with
# no guarantee left (OWES_NOTHING_FROM).
OWES_NOTHING = re.compile(
    r"ValueError: point_id \d+: duration_mth \d+: no payment is owed after the valuation "
    r"date: every covered life has died, and (the contract has no guarantee|the guarantee "
    r"ended at policy month \d+)")


def _every_state_months(end):
    """The S months a point whose S frame runs to ``end`` is restated at.

    By default the edges of its windows (USLIB-SEC-PLAN.md §5.2, T5): every month of the
    first policy year and the first anniversary, each anniversary and the month before it,
    through which the income escalates, and the last two months of the frame.  With
    ``UKLIB_SEC_FULL=1``, every month.  Each after 0, the twin's month.
    """
    if SEC_FULL:
        return list(range(1, end))
    months = {*range(1, 14), end - 2, end - 1,
              *(m for a in range(12, end, 12) for m in (a - 1, a))}
    return sorted(m for m in months if 0 < m < end)


def _states(s, points=None):
    """Each ``(S point, month)`` of :func:`_every_state_months` on every point of ``s``, or
    of ``points``."""
    labels = s.Data.model_point_table().index
    return [(point_id, d) for key, point_id in zip(point_keys(s), labels)
            if points is None or point_id in points
            for d in _every_state_months(projection(s, key).proj_len())]


def _restated(root, s, states):
    """The twins of ``s``'s points and a row in payment at each of ``states``, ``(S point,
    month)``, built by the generator out of ``s`` into a copy of the product directory:
    ``(folder, table)``."""
    spec = dataclasses.replace(SPEC, derived=tuple(states), future=(), derived_refs={})
    table, _ = build_sec_table(spec, s)
    return _sec_inputs(root, table), table


def _refused_in_force(folder, refs):
    """What ``Data`` and ``proj_len()`` refuse of the table in ``folder``, read with ``refs``
    set first: ``Data``'s refusal, or each row's ``proj_len()``'s, by its label, each by the
    line that names it.  Each row is released once asked (:func:`_release`)."""
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
    """Every state ``PA_UK_S`` reaches is a valid opening state, but a contract owing
    nothing (T5).

    ``Data``'s rules and ``proj_len()``'s hold an opening state to what a contract in
    payment can be, so they must accept each state the S model reaches: a rule exercised
    only on the rows the other tests choose could refuse a state S reaches elsewhere (D6).
    So each point of S is restated in payment by the generator at the edges of its windows,
    or with ``UKLIB_SEC_FULL=1`` at every month of its frame (:func:`_every_state_months`),
    into one table beside the twins: ``Data`` reads it, and no row's ``proj_len()`` refuses
    it (USLIB-SEC-PLAN.md §5.2, T5, precised at M10), but the states the product refuses by
    name, set aside and shown refused: a contract owing nothing, every covered life dead and
    no guarantee left, which S point 8 reaches once the cap has killed its rated life, and
    the splice's variants 14, 15 and 16 once both their lives have died
    (:data:`OWES_NOTHING_FROM`).

    The states S reaches differ with the RPI, which moves the income, the peak and both
    payments to date, and with the variants, which move the lives, the schedule and the
    payments.  So the test runs on each set of inputs on which those states differ
    (precised at M9), and asserts which states each moves:

    * S as shipped, its ten points under its own References, as T1 and the committed rows
      read it (``s_model``);
    * the splice's shipped set, its points and twelve variants;
    * the RPI sets, the RPI points under 8% and under -2%, where the income and both
      payments to date move, and under -2% the peak, and nothing else does.

    Expense inflation moves no state, and the mortality basis's References move the lives
    and the payments alike on every point, so neither is run.
    """
    sets = {"shipped": (s_model, {}, None),
            "spliced": (spliced.pair("shipped")[0], SPLICE_SETS["shipped"], None),
            "rpi_high": (spliced.pair("rpi_high")[0], SPLICE_SETS["rpi_high"], RPI_POINTS),
            "rpi_low": (spliced.pair("rpi_low")[0], SPLICE_SETS["rpi_low"], RPI_POINTS)}
    found, states, set_aside = {}, {}, {}
    for tag, (s, refs, points) in sets.items():
        s_table = s.Data.model_point_table()
        s_point = dict(zip(s_table["policy_id"], s_table.index))
        reached = _states(s, points)
        folder, rows = _restated(tmp_path / tag, s, reached)
        assert len(rows) == len(s_table) + len(reached)
        states[tag] = rows.set_index(["source_policy_id", "source_mth"])
        refused = _refused_in_force(folder, refs)
        if "Data" in refused:
            found[tag] = [refused["Data"]]
            continue
        late = [(int(row.point_id), row.source_policy_id) for row in rows.itertuples()
                if row.source_mth >= OWES_NOTHING_FROM.get(s_point[row.source_policy_id],
                                                           10 ** 9)]
        set_aside[tag] = sorted({policy for _, policy in late})
        for label, _ in late:
            if not OWES_NOTHING.fullmatch(refused.pop(label, "")):
                found.setdefault(tag, []).append(f"{label} not refused as owing nothing")
        if refused:
            found.setdefault(tag, []).append(
                f"{len(refused)} refused, first: {list(refused.items())[:5]}")
    assert not found, found
    assert set_aside == {"shipped": ["PA-000008"],
                         "spliced": ["PA-000008", "PA-900014", "PA-900015", "PA-900016"],
                         "rpi_high": [], "rpi_low": []}, set_aside
    moved = {}
    for tag in ("rpi_high", "rpi_low"):
        shipped, other = states["shipped"], states[tag]
        both = shipped.index.intersection(other.index)
        assert len(both) > 100, tag
        moved[tag] = {c for c in ("policy_count", *STATE)
                      if not shipped.loc[both, c].equals(other.loc[both, c])}
    paid = {"annual_income_init", "cum_annuity_all_init", "cum_annuity_pp_init"}
    assert moved == {"rpi_high": paid, "rpi_low": paid | {"rpi_peak_init"}}, moved


# ---------------------------------------------------------------------------
# The mortality table
#
# Data checks the table before a value of it is read, in the cell the projection takes the
# table's extent from (UKLIB-SEC-PLAN.md §4; USLIB-SEC-PLAN.md §7.1, *Precised at M3*,
# item 9).  Each case is the shipped table with one fault, read from a copy, refused by
# Data.mort_age_first alone, naming the file, the column and the lines at fault, the header
# line 1, and through a projection of the table basis's twin, point 2.  The table holds the
# male ages 50 to 115 on lines 2 to 67 and the female on lines 68 to 133, which its check
# reads as the file stands, where PA_UK_S's reader sorts the table.


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


def _mort_line(sex, age):
    """The line of mort_table.csv that holds ``sex`` at ``age``, as shipped."""
    rows = pd.read_csv(model_path(TWIN).parent / "mort_table.csv")
    return int(rows.index[(rows["sex"] == sex) & (rows["age"] == age)][0]) + 2


def _dropped(where):
    return lambda table: table[~where(table)].reset_index(drop=True)


def _repeated(where):
    return lambda table: pd.concat([table, table[where(table)]], ignore_index=True)


MORT = "mort_table.csv"
RATE = f"{MORT}: mort_rate must be a number from 0 to 1; it is not on line "


def _ages_apart(*faults):
    """The message of a mortality table whose sexes do not run one row an age, naming
    ``faults``."""
    return (f"{MORT}: the ages of each sex must run from 50 to 115, the table's first and "
            f"last, one row an age, none below 0; " + "; ".join(faults))


# A table the reader cannot read, or whose value is not a number in its range, as (case,
# its edit, its message).  A value no point reads is refused too: the male rate at 115,
# which no frame reaches.
UNREADABLE = [
    ("a blank mortality rate", _written("mort_rate", float("nan"), _mort("M", 70)),
     RATE + f"[{_mort_line('M', 70)}]"),
    ("a text mortality rate", _written("mort_rate", "low", _mort("M", 66)),
     RATE + f"[{_mort_line('M', 66)}]"),
    ("an infinite mortality rate", _written("mort_rate", float("inf"), _mort("M", 115)),
     RATE + f"[{_mort_line('M', 115)}]"),
    ("a negative mortality rate", _written("mort_rate", -0.001, _mort("F", 50)),
     RATE + f"[{_mort_line('F', 50)}]"),
    ("a mortality rate past 1", _written("mort_rate", 1.5, _mort("M", 80)),
     RATE + f"[{_mort_line('M', 80)}]"),
    ("two rows at fault", _then(_written("mort_rate", float("nan"), _mort("M", 50)),
                                _written("mort_rate", float("nan"), _mort("F", 90))),
     RATE + f"[{_mort_line('M', 50)}, {_mort_line('F', 90)}]"),
    ("an age not whole", _written("age", 65.5, _mort("M", 65)),
     f"{MORT}: age must be a whole number; it is not on line [{_mort_line('M', 65)}]"),
    ("an age written as text", _written("age", "x", _mort("F", 50)),
     f"{MORT}: age must be a whole number; it is not on line [{_mort_line('F', 50)}]"),
    ("an unknown sex", _written("sex", "X", _mort("F", 51)),
     f"{MORT}: sex must be M or F; it is not on line [{_mort_line('F', 51)}]"),
    ("an age missing", _dropped(_mort("M", 70)),
     _ages_apart("no line holds sex M, age 70")),
    ("an age twice", _repeated(_mort("F", 60)),
     _ages_apart(f"sex F, age 60 repeats on lines [{_mort_line('F', 60)}, 134]")),
    ("a sex missing", _dropped(lambda t: t["sex"] == "F"),
     _ages_apart("no line holds sex F, ages 50 to 115")),
    ("a sex shorter", _dropped(_mort("F", 115)),
     _ages_apart("no line holds sex F, age 115")),
]


@pytest.mark.parametrize("case, edit, message", UNREADABLE, ids=[c[0] for c in UNREADABLE])
def test_a_table_the_reader_cannot_read_is_refused_naming_its_lines(tmp_path, case, edit,
                                                                    message):
    """``Data`` refuses the mortality table before a value of it is read (T5).

    ``PA_UK_S`` reads a blank rate as NaN, which its cap would keep and every flow carry; an
    infinite one, which the cap reads as certain death; a key that is not whole, gapped or
    repeated, as a ``KeyError`` only where a projection reaches it, or as a wrong row.
    Here the extent cell the projection asks first refuses each, naming the file, the
    column and the rows at fault (:data:`UNREADABLE`), and so does a projection of the table
    basis's twin.  A scenario point reads no mortality, and projects.
    """
    model = _read_edited(tmp_path, lambda t: t, edits={MORT: edit})
    try:
        _refused(model.Data.mort_age_first, message)
        _refused(_point(model, 2).result_cf, message)
        assert len(_point(model, 1).result_cf()) == 636
    finally:
        model.close()


def test_a_read_beyond_the_mortality_table_is_refused_naming_its_point(tmp_path):
    """A read past the mortality table's ages is refused, naming the point.

    ``PA_UK_S``'s lookup raises ``KeyError`` beyond the table, naming no point.  Below it,
    an annuitant issued at 49 on the table basis, which the table first rates at 50, is
    refused by the one cell that reads it, naming the point and the age; on the scenario
    basis, which reads no mortality, the same age projects, a frame of 12 x (115 - 49) =
    792 months.  Above it, the table is read at attained ages to ``omega_age - 1``, and
    ``proj_len()`` holds the limiting age to a year past the table's last age on the table
    basis, so no frame reads past it: at 116 the table basis's twin projects what
    ``PA_UK_S`` projects at that limiting age, in every column.
    """
    model = _read_edited(tmp_path, _then(_set("annuitant_age", [2], 49),
                                         _set("annuitant_age", [1], 49)))
    try:
        _refused(_point(model, 2).result_cf,
                 "point_id 2: mort_table.csv has no rate at attained age 49")
        assert len(_point(model, 1).result_cf()) == 792
    finally:
        model.close()
    s = mx.read_model(model_path(TWIN), name=_name("s_omega"))
    sec = mx.read_model(model_path(SEC), name=_name("sec_omega"))
    try:
        for each in (s, sec):
            each.Projection.omega_age = 116
        sp, p = _point(s, 2), _row(sec, "twin", 2, 0)
        assert sp.proj_len() == p.proj_len() == 12 * (116 - 62)
        assert frame_mismatches(sp.result_cf(), p.result_cf(), rtol=0.0, atol=0.0) == []
    finally:
        sec.close()
        s.close()


def test_a_key_written_as_a_float_reads_as_pa_uk_s_reads_it(sec_model, tmp_path):
    """A key written ``65.0`` is the key 65, in the table and in its extents.

    ``PA_UK_S``'s lookups match a float key to the int the projection asks, so a table
    written by a tool that writes every number with a decimal point reads the same.  The
    mortality table's ages and the model point table's ``duration_mth``, ages, frequency,
    guarantee and start year are written as floats, and every committed point projects
    what the committed tables project, exactly.
    """
    def as_float(*columns):
        return lambda table: table.assign(**{c: table[c].astype(float) for c in columns})

    model = _read_edited(tmp_path, as_float("duration_mth", "annuitant_age", "frequency",
                                            "guarantee_months", "start_year"),
                         edits={MORT: as_float("age")})
    try:
        for point_id in _committed().index:
            for report in REPORTS:
                assert frame_mismatches(_point(sec_model, point_id).cells[report](),
                                        _point(model, point_id).cells[report](),
                                        rtol=0, atol=0) == [], (point_id, report)
    finally:
        model.close()


# ---------------------------------------------------------------------------
# T6 -- regeneration


def test_the_committed_sec_inputs_are_what_s_generates(s_model):
    """``model_point_table_sec.csv`` is what PA_UK_S and its table generate today.

    Every row and column, the text cells and the opening-state columns included: an edit to
    an S row the table copies or derives from, or to an S formula a row's state is read
    from, fails here until ``python tools/gen_sec_points.py PA_UK_SEC`` regenerates it, in
    the same commit.  Text and integers compare exactly, and a float by its value, to 1e-12,
    because the text the writer picks for a computed float depends on the platform's parser
    (§5).
    """
    assert check_generated(SEC, s_model=s_model) == []


# ---------------------------------------------------------------------------
# The product's own facts


def test_the_two_clocks_on_the_shipped_points(sec_model):
    """``t`` counts from the valuation date; ``duration_mth(t)`` from the start (D3, D4).

    On a twin of S's points the two coincide, and its contracts enter as new business at
    ``t = 0``.  The worked example in payment 17 months is in policy year 2 at attained age
    66 at ``t = 0``, its annuitant dead since policy month 16 and its dependant paid from
    ``t = 0``, steps into policy year 3 at ``t = 7``, and has 619 months of its frame left,
    to the same stop as from the start.  The point starting 13 months on has nothing on the
    books and nothing to do before ``t = 13``, and a frame of 649 months.  The joint point
    in its last month has a one-month frame.  A timing or a kind the model does not know is
    refused rather than answered with another count.
    """
    twin = _row(sec_model, "twin", 1, 0)
    assert [twin.duration_mth(t) for t in (0, 1, 635)] == [0, 1, 635]
    assert (twin.t_entry(), twin.pols_if_init(), twin.pols_new_biz(0)) == (0, 0.0, 1.0)
    assert (twin.horizon_mths(), twin.stop_mth(), twin.proj_len()) == (636, 636, 636)
    old = _row(sec_model, "derived", 1, 17)
    assert (old.duration_mth(0), old.duration(0), old.policy_year(0), old.age(0, 1)) == (
        17, 1, 2, 66)
    assert (old.policy_year(6), old.policy_year(7)) == (2, 3)
    assert (old.proj_len(), old.stop_mth(), old.t_entry(), old.pols_new_biz(0)) == (
        619, 636, 0, 0.0)
    assert old.lives_if(0, 1) == 0.0 and old.lives_if(0, 2) == 1.0
    assert old.annuity_payments(0) == pytest.approx(695.25, abs=0.005)
    assert old.pols_if_at(0, _code(old, "BEF_DECR")) == old.pols_if_init() == 1.0
    fut = _row(sec_model, "future", 6, -13)
    assert (fut.duration_mth(0), fut.t_entry(), fut.proj_len()) == (-13, 13, 649)
    assert not fut.is_active(12) and fut.is_active(13)
    assert (fut.pols_if_init(), fut.pols_new_biz(13), fut.lives_if(13, 1)) == (
        0.0, 1.0, 1.0)
    assert fut.lives_if(12, 1) == 0.0 and fut.annuity_pp(15) == 1350.0
    last = _row(sec_model, "derived", 2, 635)
    assert (last.proj_len(), last.age(0, 2), last.policy_year(0)) == (1, 114, 53)
    _refused(lambda: old.pols_if_at(0, "BEF_NOTHING"), "invalid timing")
    _refused(lambda: old.claims(0, "NOTHING"), "invalid kind")
    _refused(lambda: old.cum_annuity_pp(20, "NOTHING"), "invalid kind")


def test_the_committed_rows_continue_their_s_points(sec_model, s_model):
    """Each committed row in payment, or starting later, is its S point from its month on.

    T6 compares a float to 1e-12, which pins a small survival only to that much of itself,
    so each committed row is compared with its S point frame by frame and cell by cell, at
    the shipped assumptions (USLIB-SEC-PLAN.md §7.1, *Precised at M3*, item 11): the nine
    derived rows from their months, and the row starting 13 months on from S's start, all
    to 1e-9 relative with no absolute floor but on the residuals, every cell but those
    expense inflation moves (:func:`_continues_s`), which the inflation test holds.  The two
    rows read from S under an RPI of their own continue S under that RPI, which the shipped
    one replaces from the valuation date, and their own test holds them.
    """
    table = sec_model.Data.model_point_table()
    s_table = s_model.Data.model_point_table()
    found = []
    for point_id in table.index:
        kind, month = table.at[point_id, "row_kind"], int(table.at[point_id, "source_mth"])
        policy = table.at[point_id, "source_policy_id"]
        s_point = int(s_table.index[s_table["policy_id"] == policy][0])
        if kind == "twin" or (s_point, month) in SPEC.derived_refs:
            continue
        found += [f"point {point_id}: {line}" for line in _continues_s(
            _point(s_model, s_point), _point(sec_model, point_id), month)]
    assert not found, found[:20]


def test_the_rows_read_under_an_rpi_of_their_own_continue_s_under_it(sec_model):
    """The two committed rows S reaches only under an RPI of its own are S's under it (C2).

    At ``PA_UK_S``'s flat 3% no state holds a ratchet's peak above its index, nor an LPI
    increase capped, so the spec restates the catch-up point at its month 60 from S run
    under an RPI of -2%, and the LPI point at its month 42 from S under 8% (the spec's
    ``derived_refs``), and C2 freezes both.  Three things are held of each:

    * the row is S's state under that RPI: S read under it holds, at the row's month, the
      row's count, survival, payments to date, income, peak and annuitant's payments;
    * set on this model too, that RPI gives the row S's path: it continues S's projection
      from its month on in every cell, over the whole of both frames, as the splice
      compares them (:func:`_continues_s`);
    * at today's References, which take over from the valuation date, the income parts
      from S's at the row's next anniversary, but no RPI moves survival, the guarantee's
      floor or the obligation measure: the committed row holds S's in every month.
    """
    for (s_point, month), refs in SPEC.derived_refs.items():
        label = _label(sec_model.Data.model_point_table(), "derived", s_point, month)
        s = mx.read_model(model_path(TWIN), name=_name("s_refs"))
        sec = mx.read_model(model_path(SEC), name=_name("sec_refs"))
        try:
            for model in (s, sec):
                for ref, value in refs.items():
                    setattr(model.Projection, ref, value)
            sp, row = _point(s, s_point), _point(sec_model, label)
            year = max(month - 1, 0) // 12 + 1
            opening = {"policy_count": sp.pols_if_init(),
                       "lives_if_init": (sp.lives_if(month, 1), sp.lives_if(month, 2)),
                       "cum_annuity_all_init": sp.cum_annuity_pp(month, "ALL"),
                       "annual_income_init": sp.annual_income(year)}
            assert row.policy_count() == opening["policy_count"]
            assert (row.lives_if_init(1), row.lives_if_init(2)) == pytest.approx(
                opening["lives_if_init"], rel=1e-12)
            assert row.cum_annuity_all_init() == pytest.approx(
                opening["cum_annuity_all_init"], rel=1e-12)
            assert row.annual_income_init() == pytest.approx(
                opening["annual_income_init"], rel=1e-12)
            if sp.escalation_type() == "rpi_catchup":
                assert row.rpi_peak_init() == pytest.approx(
                    sp.rpi_peak(year - 1) / sp.rpi_index(year - 1), rel=1e-12)
            assert row.cum_annuity_pp_init() == pytest.approx(
                sp.cum_annuity_pp(month, "ANNUITANT"), rel=1e-12)
            _sweep_s(sp)
            assert _continues_s(sp, _point(sec, label), month) == []
            for t in range(row.proj_len()):
                for cell in ("pols_if", "certain_floor"):
                    assert row.cells[cell](t) == pytest.approx(
                        sp.cells[cell](month + t), rel=1e-9, abs=0.0), (cell, t)
                for life in (1, 2):
                    assert row.lives_if(t, life) == pytest.approx(
                        sp.lives_if(month + t, life), rel=1e-9, abs=0.0), (life, t)
        finally:
            sec.close()
            s.close()


# The ratchet's catch-up branch, which a flat RPI never reaches: the committed catch-up row
# at S month 60, read from S under -2%, its income frozen at 5,400 and its peak 1 / 0.98^4,
# 1.0841657847339398, over the latest index, at the shipped 3% from the valuation date.
# Its fifth anniversary falls in month 0, where the index, 1.03 over the latest, stays below
# the peak, and so does its sixth, at t = 12, 1.03^2 = 1.0609; at its seventh, t = 24,
# 1.03^3 = 1.092727 passes it, and the income catches up by the excess over the peak:
# 5,400 x 1.092727 / 1.0841657847 = 5,442.64; then 5,400 x 1.03^4 / peak = 5,605.92 at its
# eighth, and so on, each anniversary's index over the same peak.  Hand-computed goldens, a
# quarter of each year's income paid in arrears at policy months 62, 65, ... .
CATCH_UP = {5: 5400.0, 6: 5400.0, 7: 5400.0, 8: 5442.64, 9: 5605.92, 10: 5774.10}


def test_the_ratchet_catches_up_from_a_peak_above_the_index(sec_model, tmp_path):
    """Carried in above the index, the ratchet freezes the income, then catches up (§6.7).

    ``PA_UK_S``'s deterministic RPI is monotone, so its catch-up branch, an index rising
    from below its peak, is never reached, and S cannot give it a golden.  The committed
    catch-up row at 60 carries a peak above the index, history S makes only under an RPI
    of -2% (:data:`CATCH_UP`): at the shipped 3% from the valuation date its income is
    frozen at 5,400 through its sixth and seventh policy years, the index rising from 1 to
    1.0609 under a peak of 1.0842, and catches up in its eighth, by the excess of the index
    over the peak, 5,442.64, each to the penny.  The peak runs on from the opening state:
    ``rpi_peak`` is the opening peak at the fourth anniversary, the latest, and at the fifth
    and sixth, and the index itself, 1.03^3, from the seventh.  Read from the index instead,
    a peak of 1 at the valuation date, the income would escalate at once, to 5,562.00 in the
    sixth year; a test writes the peak at 1 and sees that.  And a peak of 1.2 freezes the
    income to the eleventh year, 1.03^6 = 1.194 still short of it, and the twelfth's is
    5,400 x 1.03^7 / 1.2.
    """
    row = _point(sec_model, _label(sec_model.Data.model_point_table(), "derived", 6, 60))
    assert row.rpi_peak_init() == pytest.approx(1.0 / 0.98 ** 4, rel=1e-12)
    assert row.policy_year_init() == 5
    for year, income in CATCH_UP.items():
        assert row.annual_income(year) == pytest.approx(income, abs=0.005), year
    assert row.rpi_peak(4) == row.rpi_peak(5) == row.rpi_peak(6) == row.rpi_peak_init()
    assert row.rpi_peak(7) == row.rpi_index(7) == pytest.approx(1.03 ** 3, rel=1e-12)
    for t, income in ((2, 5400.0), (14, 5400.0), (26, 5442.64), (38, 5605.92)):
        assert row.annuity_pp(t) == pytest.approx(income / 4, abs=0.005), t
    label = _label(_committed(), "derived", 6, 60)
    for peak, frozen_to in ((1.0, None), (1.2, 11)):
        model = _read_edited(tmp_path / f"peak{peak}", _set("rpi_peak_init", [label], peak))
        try:
            p = _point(model, label)
            if frozen_to is None:
                assert p.annual_income(6) == pytest.approx(5400.0 * 1.03, rel=1e-12)
            else:
                for year in range(5, frozen_to + 1):
                    assert p.annual_income(year) == 5400.0, year
                assert p.annual_income(frozen_to + 1) == pytest.approx(
                    5400.0 * 1.03 ** 7 / 1.2, rel=1e-12)
        finally:
            model.close()


def test_the_rpi_linked_income_is_read_from_the_model_point(sec_model, tmp_path):
    """The RPI increases already given are the point's, not today's (UKLIB-SEC-PLAN.md K14).

    ``PA_UK_S`` rebuilds the income of every year from a flat ``rpi_rate``, so a model that
    dropped ``annual_income_init`` and did the same would pass the splice, which runs S and
    this model at one rate.  The committed LPI row at 42, read from S under 8%, carries the
    5% cap's increases: 5,400 x 1.05^3 = 6,251.18 in its fourth year, where the shipped 3%
    rebuilt from the start would give 5,900.66.  Its income is the column through the year
    under way, and 3% more at each anniversary after, the LPI at today's RPI.  And the LPI
    row at 24 written at 6,000.00, an income no flat RPI gives, escalates that by 3% in month
    0, its second anniversary, and pays a quarter of it at each instalment.
    """
    capped = _point(sec_model, _label(sec_model.Data.model_point_table(), "derived", 7, 42))
    assert capped.policy_year_init() == 4
    assert capped.annual_income_init() == pytest.approx(5400.0 * 1.05 ** 3, rel=1e-12)
    assert [capped.annual_income(y) for y in (4, 5, 6)] == pytest.approx(
        [5400.0 * 1.05 ** 3 * 1.03 ** n for n in range(3)], rel=1e-12)
    assert capped.annuity_pp(2) == pytest.approx(5400.0 * 1.05 ** 3 / 4, rel=1e-12)
    label = _label(_committed(), "derived", 7, 24)
    model = _read_edited(tmp_path, _set("annual_income_init", [label], 6000.0))
    try:
        p = _point(model, label)
        assert p.annual_income(2) == 6000.0
        assert p.annual_income(3) == pytest.approx(6000.0 * 1.03, rel=1e-12)
        assert p.annuity_pp(2) == pytest.approx(6000.0 * 1.03 / 4, rel=1e-12)
    finally:
        model.close()


def test_the_income_is_taken_before_month_0s_anniversary(s_model, tmp_path):
    """The RPI-linked income is measured before month 0's own anniversary (D6, M9).

    The opening state is measured at the valuation instant, before any month-0 event, and an
    anniversary's escalation is one: on a row valued on an anniversary the column is the
    income of the year the anniversary closes, and month 0 escalates it at the valuation
    date's RPI, as every month-0 event reads the valuation date's References.  So the LPI
    point restated by the generator at its month 24, its second anniversary, read at an RPI
    of 1%, opens with its second year's income, S's ``annual_income(2)``, 5,562.00, and pays
    5,562.00 x 1.01 from month 0; and its twin, starting at the valuation date, escalates at
    1% at its first anniversary, ``t = 12``.  A column that held month 0's escalation too,
    5,728.86 at S's 3%, would pay that at the new rate's expense; and a model that read the
    column as the year after month 0's anniversary would pay 5,562.00 in month 0.
    """
    spec = dataclasses.replace(SPEC, derived=((7, 24), (6, 24)), future=(),
                               derived_refs={})
    rows, _ = build_sec_table(spec, s_model)
    model = mx.read_model(_sec_inputs(tmp_path, rows), name=_name("anniversary"))
    try:
        model.Projection.rpi_rate = 0.01
        lpi = _row(model, "derived", 7, 24)
        assert lpi.annual_income_init() == _point(s_model, 7).annual_income(2) == 5562.0
        assert lpi.policy_year_init() == 2 and lpi.policy_year(0) == 3
        assert lpi.annual_income(3) == pytest.approx(5562.0 * 1.01, rel=1e-12)
        assert lpi.annuity_pp(2) == pytest.approx(5562.0 * 1.01 / 4, rel=1e-12)
        catchup = _row(model, "derived", 6, 24)
        assert catchup.annual_income_init() == 5562.0 and catchup.rpi_peak_init() == 1.0
        assert catchup.annual_income(3) == pytest.approx(5562.0 * 1.01, rel=1e-12)
        twin = _row(model, "twin", 7, 0)
        assert twin.annual_income(2) == pytest.approx(5400.0 * 1.01, rel=1e-12)
    finally:
        model.close()


def test_the_annuitants_payments_to_date_are_read_from_the_model_point(sec_model,
                                                                       tmp_path):
    """On RPI-linked escalation the annuitant's payments to date are the point's (K14).

    ``PA_UK_S`` rebuilds the as-if-alive annuitant schedule from the start at today's RPI,
    which first-death value protection nets against, so a model that re-derived the column
    would pass the splice.  The committed catch-up row at 60 carries five years of a frozen
    5,400, 27,000.00, where today's 3% would rebuild 28,669.34: its balance at ``t = 0`` is
    50,000 - 27,000 = 23,000.00, and its value protection in the month pays that on the
    annuitant's death.  Written at 30,000.00, a history no RPI gives, the balance is
    20,000.00 at ``t = 0`` and falls by each instalment paid after.
    """
    label = _label(sec_model.Data.model_point_table(), "derived", 6, 60)
    frozen = _point(sec_model, label)
    assert frozen.cum_annuity_pp_init() == 27000.0
    assert frozen.vp_balance(0) == 23000.0
    assert frozen.claims(0, _code(frozen, "VP")) == pytest.approx(
        23000.0 * frozen.lives_death(0, 1), rel=1e-12)
    model = _read_edited(tmp_path, _set("cum_annuity_pp_init", [label], 30000.0))
    try:
        p = _point(model, label)
        assert p.vp_balance(0) == 20000.0
        assert p.vp_balance(3) == 20000.0 - p.annuity_pp(2)
        assert p.vp_balance(6) == 20000.0 - p.annuity_pp(2) - p.annuity_pp(5)
    finally:
        model.close()


def test_the_payments_to_date_and_survival_are_read_from_the_model_point(sec_model,
                                                                         tmp_path):
    """Survival and the payments to date are the point's, not the basis's of the day (K14).

    ``PA_UK_S`` rebuilds each life's survival from the start on the mortality basis it
    holds, and the expected payments to date from that survival, so a basis changed at the
    valuation date would rewrite both back to the start.  Here each is read from the model
    point, history the basis of the day reaches back over no month of: under an
    ``annuitant_adj`` of 0.5 set at the valuation date, the table basis's joint point at
    101 opens with the survival and the payments S carried there at 0.8, and only its later
    months move.  And on a record, the last-survivor row at 170 written as having paid
    45,000.00 to date, its balance opens at 5,000.00, where the scenario's expectation gives
    471.67; and the annuitant written dead on the joint table row, a record's 0, stops the
    annuitant's instalments and starts the dependant's, half of them, from its first
    payment, in month 0.
    """
    joint = _label(_committed(), "derived", 2, 101)
    columns = _committed().loc[joint, ["lives_if_init_1", "lives_if_init_2",
                                       "cum_annuity_all_init"]].tolist()
    model = mx.read_model(model_path(SEC), name=_name("basis"))
    try:
        model.Projection.annuitant_adj = 0.5
        p, base = _point(model, joint), _point(sec_model, joint)
        for each in (p, base):
            assert [each.lives_if(0, 1), each.lives_if(0, 2),
                    each.cum_annuity_all(0)] == columns
        assert p.lives_if(1, 1) > base.lives_if(1, 1)
    finally:
        model.close()
    last = _label(_committed(), "derived", 10, 170)
    model = _read_edited(tmp_path, _then(_set("cum_annuity_all_init", [last], 45000.0),
                                         _set("lives_if_init_1", [joint], 0.0)))
    try:
        p = _point(model, last)
        assert _point(sec_model, last).vp_balance(0) == pytest.approx(471.674763, abs=1e-6)
        assert p.vp_balance(0) == 5000.0
        q = _point(model, joint)
        assert q.payment_factor(0) == 0.0
        assert q.annuity_pp(0) > 0.0
        assert q.annuity_payments(0) == pytest.approx(
            q.annuity_pp(0) * 0.5 * q.lives_if(1, 2), rel=1e-12)
    finally:
        model.close()


def test_the_rpi_is_one_flat_rate_on_either_clock(sec_model, s_model):
    """``rpi_rate`` is the RPI from the valuation date on, the same on both clocks (D7).

    A flat rate is the same on the valuation clock as on the policy clock, so the splice
    runs S and this model at one rate, and no path is introduced (UKLIB-SEC-PLAN.md §9,
    item 4).  On every RPI-linked committed row in payment the relative index is 1 at the
    latest anniversary, ``rpi_index(a0)``, and rises by the shipped 3% an anniversary from
    there; and on each such row read from S at the shipped RPI, the income of the year under
    way and of the four after it is S's, to 1e-12.  The two rows read from S under an RPI of
    their own carry history S's 3% does not make, which their own tests hold.
    """
    table = sec_model.Data.model_point_table()
    linked = 0
    for label in table.index:
        p = _point(sec_model, label)
        if not (p.is_lpi5() or p.is_rpi_catchup()) or p.duration_mth_init() <= 0:
            continue
        linked += 1
        a0 = p.policy_year_init() - 1
        s_point = int(table.at[label, "source_policy_id"][3:])
        if p.is_rpi_catchup():
            assert p.rpi_index(a0) == 1.0, label
            assert p.rpi_index(a0 + 3) == pytest.approx(1.03 ** 3, rel=1e-12), label
        if (s_point, int(table.at[label, "source_mth"])) in SPEC.derived_refs:
            continue
        s = _point(s_model, s_point)
        for year in range(p.policy_year_init(), p.policy_year_init() + 5):
            assert p.annual_income(year) == pytest.approx(s.annual_income(year),
                                                          rel=1e-12), (label, year)
    assert linked == 4


def test_expense_inflation_runs_on_the_valuation_clock(sec_model, s_model):
    """Maintenance is in valuation-date pounds, for every point alike (D7).

    At the shipped 3%, the factor at ``t`` is ``1.03^(t // 12)`` on every point, whatever its
    duration, stepping on the valuation date's anniversaries.  So the worked example in
    payment 17 months pays S's month-``17 + t`` maintenance with S's factor taken out and this
    model's put in: at ``t = 0`` S's less 1.03, the inflation S had applied since the start,
    and from ``t = 7``, where S's policy anniversary falls, a further 1.03 less until the
    valuation date's own.  And the point starting 13 months on pays S's maintenance with a
    year or two more of inflation: its factor at ``t`` is ``1.03^(t // 12)``, where S's at
    ``t - 13`` is ``1.03^((t - 13) // 12)``.  This is the only test that sees inflation run
    on the policy clock: the splice sets the rate to 0, and on a point starting at ``t = 0``
    the clocks agree.
    """
    assert sec_model.Projection.inflation_rate == INFLATION
    p, s = _row(sec_model, "derived", 1, 17), _point(s_model, 1)
    fut, s6 = _row(sec_model, "future", 6, -13), _point(s_model, 6)
    for t in (0, 11, 12, 30):
        assert p.inflation_factor(t) == fut.inflation_factor(t) == (1 + INFLATION) ** (t // 12)
    for t in range(p.proj_len()):
        assert p.expenses(t) == pytest.approx(
            s.expenses(17 + t) / s.inflation_factor(17 + t) * p.inflation_factor(t),
            rel=1e-12), t
    assert p.expenses(0) == pytest.approx(s.expenses(17) / (1 + INFLATION), rel=1e-12)
    for t in range(13, fut.proj_len()):
        assert fut.expenses(t) == pytest.approx(
            s6.expenses(t - 13) * (1 + INFLATION) ** (t // 12 - (t - 13) // 12),
            rel=1e-12), t


def test_improvement_runs_on_the_policy_clock(sec_model, s_model):
    """Mortality improvement is dated by the calendar from the start, on the policy clock.

    Its exponent is ``calendar_year(t) - mort_table_year``, and ``calendar_year(t) =
    start_year() + duration(t)``, the calendar year the contract reaches whatever the
    valuation date (D7, precised at M11; UKLIB-SEC-PLAN.md §9 item 4).  So the table basis's
    joint point at 101 reads, at each ``t``, S's improvement factor and rate of policy month
    ``101 + t``, bit for bit, and its calendar year steps at its own anniversaries, ``t =
    7``, not the valuation date's.  On the valuation clock it would read the factor of
    ``2026 + t // 12``, 8 years of improvement too few at ``t = 0``.
    """
    p, s = _row(sec_model, "derived", 2, 101), _point(s_model, 2)
    assert (p.calendar_year(6), p.calendar_year(7)) == (2034, 2035)
    for t in range(0, p.proj_len(), 7):
        for life in (1, 2):
            assert p.improve_factor(t, life) == s.improve_factor(101 + t, life), (t, life)
            assert p.mort_rate(t, life) == s.mort_rate(101 + t, life), (t, life)


def test_new_business_brings_no_premium_and_no_acquisition(sec_model):
    """An annuity starting in a month brings its count and nothing else (§6.7).

    The purchase price is a pricing input, as in ``PA_UK_S``: no cash flow in the issue
    month but the instalments, any value protection and the maintenance, on every point.
    ``liability_cf`` is the sum of those three, and ``net_cf`` its negative, in every month,
    the issue month of the point starting 13 months on among them, where the expense is the
    maintenance alone.
    """
    table = sec_model.Data.model_point_table()
    for key, point_id in zip(point_keys(sec_model), table.index):
        p = projection(sec_model, key)
        df = p.result_cf()
        total = df["annuity_payments"] + df["claims_vp"] + df["claims_prop"] + df["expenses"]
        assert ((df["liability_cf"] - total).abs() <= 1e-9).all(), point_id
        assert (df["net_cf"] == -df["liability_cf"]).all(), point_id
    fut = _row(sec_model, "future", 6, -13)
    assert fut.expenses(13) == pytest.approx(
        fut.expense_maint / 12.0 * fut.inflation_factor(13) * fut.pols_if(13), rel=1e-12)


def test_the_payment_schedule_runs_on_the_policy_clock(sec_model):
    """The payment months, the months since a payment and the next payment read the policy
    month, not ``t`` (R1a).

    ``PA_UK_S`` reads ``(t + 1) % step``, ``t % step`` and its months since a payment on its
    one clock, which is the policy clock only on a point starting at ``t = 0``.  The worked
    example in payment 17 months pays quarterly in arrears at policy months 17, 20, ..., so
    at ``t = 0, 3, ...``; at ``t = 0`` two months have passed since the last payment date,
    policy time 15, at ``t = 1`` none, the month-17 instalment having fallen at policy time
    18, and its next payment is policy month 20; the proportionate payment's
    point at 16, the month of the death, accrues one month since policy time 15 and pays a
    proportionate quarter of its year's 5,562, ``1.5 / 3 x 1,390.50``, on the annuitant's
    death, with its value protection.  The point starting 13 months on pays at policy months
    2, 5, ..., so at ``t = 15, 18, ...``.
    """
    p = _row(sec_model, "derived", 1, 17)
    assert [t for t in range(9) if p.is_payment_mth(t)] == [0, 3, 6]
    assert (p.mths_since_payment(0), p.mths_since_payment(1), p.next_payment_mth(1)) == (
        2, 0, 20)
    prop = _row(sec_model, "derived", 9, 16)
    assert (prop.mths_since_payment(0), prop.next_payment_mth(0)) == (1, 17)
    assert prop.claims(0, _code(prop, "PROP")) == pytest.approx(695.25, abs=0.005)
    assert prop.claims(0, _code(prop, "VP")) == pytest.approx(43209.50, abs=0.005)
    fut = _row(sec_model, "future", 6, -13)
    assert [t for t in range(13, 22) if fut.is_payment_mth(t)] == [15, 18, 21]


# ---------------------------------------------------------------------------
# The cap on mortality
#
# mort_rate caps the annual rate at 1, the bound second, as PA_UK_S's does since M0.  It
# binds on S point 8, rated 1.35, from policy month 576, attained age 113, where 1.35 times
# the table rate, the adjustment and the improvement passes 1, to the end of its frame.


def test_an_annual_mortality_past_1_is_capped_in_both_models(sec_model, s_model):
    """Where the rated annual mortality passes 1, both models' rate is the float 1.0.

    On S point 8, rated 1.35, the product of the rating and the improved table rate passes 1
    from policy month 576 to the end of its 600-month frame (UKLIB-SEC-PLAN.md §6.7).  Both
    models cap it: ``mort_rate`` and the monthly rate are 1.0 in every one of those months,
    the float, not the int 1, which compares equal to it, and floats below 1 in every month
    before.  So every contract's annuitant alive at the start of the first capped month dies
    in it, and none is alive after it.  On the twin, and on the committed row restated in
    payment the month before, at 575, which T2 and the committed rows' test compare with S
    in every cell: from its ``t = 1``, on its own clock.  Every report holds finite floats.
    """
    s = _point(s_model, 8)
    capped = [t for t in range(s.proj_len())
              if s.rating_factor(1) * s.mort_rate_base(t, 1) * s.improve_factor(t, 1) > 1.0]
    assert capped == list(range(576, 600))
    for case, first in ((("twin", 8, 0), 576), (("derived", 8, 575), 1)):
        p = _row(sec_model, *case)
        for rate in (p.mort_rate, p.mort_rate_mth):
            assert all(type(rate(t, 1)) is float and rate(t, 1) < 1.0
                       for t in range(first)), case
            assert [(type(rate(t, 1)), rate(t, 1)) for t in range(first, p.proj_len())] == (
                [(float, 1.0)] * (p.proj_len() - first)), case
        assert p.lives_if(first, 1) > 0.0 and p.lives_if(first + 1, 1) == 0.0, case
        for report in REPORTS:
            frame = p.cells[report]()
            assert (frame.dtypes == "float64").all(), (case, report)
            assert np.isfinite(frame.to_numpy()).all(), (case, report)
    for t in range(576, 600):
        assert (type(s.mort_rate(t, 1)), s.mort_rate(t, 1)) == (float, 1.0)


# A NaN sent to a bound written with its bound second, as (the bound, the Reference that
# feeds it, set to NaN on a model read for the test before it computes anything, the S
# point whose twin reads it, and the calls that must give the float NaN).  The cap reads
# annuitant_adj on the table basis, through the base rate.  A bound written first would turn
# the NaN into the bound: a blank input read as certain death.  proj_len() refuses an
# annuitant_adj that is not a number, so no report projects it; the calls here read no
# frame.  This form runs compiled unchanged, since a compiled ItemSpace takes the References
# when it is made (USLIB-SEC-PLAN.md §5.1, step 6, precised at M12).
NAN_BOUNDS = [
    ("the mortality cap, min(q, 1.0)", "annuitant_adj", 2,
     [("mort_rate", (0, 1)), ("mort_rate", (300, 2)), ("mort_rate_mth", (100, 1))]),
    ("the mortality cap on the rated life, min(q, 1.0)", "annuitant_adj", 8,
     [("mort_rate", (580, 1)), ("mort_rate_mth", (590, 1))]),
]


@pytest.mark.parametrize("bound, ref, s_point, calls", NAN_BOUNDS,
                         ids=[c[0] for c in NAN_BOUNDS])
def test_a_nan_that_reaches_a_bound_stays_nan(bound, ref, s_point, calls):
    """A NaN that reaches the bound written second stays NaN, and is not read as the bound.

    ``min`` keeps its first argument unless a later one compares smaller, in modelx and
    compiled alike, and no comparison with NaN holds, so with its bound first the cap would
    turn a NaN into 1: certain death, where the rated life's cap binds as on point 8 at
    580.  It is written with its bound second, as ``PA_UK_S`` writes it (:data:`NAN_BOUNDS`):
    the Reference that feeds it is set to NaN on a model read for the test, and every call
    must give the float NaN.  The cells are called on their own, without the frame:
    ``proj_len()`` refuses the Reference at NaN before a report reaches the bound (the domain
    test).  Every other ``min`` and ``max`` keeps ``PA_UK_S``'s order, and the domains and
    ``Data`` keep a NaN from each.
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


@pytest.mark.parametrize("check, resid", [
    ("check_lives_roll_fwd", "check_lives_roll_fwd_resid"),
    ("check_payment_factor", "check_payment_factor_resid")])
def test_a_check_fails_a_residual_that_is_not_a_number(sec_model, check, resid):
    """Each check returns False where its residual is NaN (§7.1, item 11).

    A check is ``abs(resid) < tolerance`` over the frame, which no NaN passes, as
    ``PA_UK_S``'s is; but no input the frame accepts gives a NaN residual, so the residual's
    formula is replaced, on a model read for the test, by one that returns NaN in every
    month.  Then the check is the bool False on every committed point, where with its own
    formula it is True.  A check that asked whether any residual was past its tolerance would
    pass NaN.
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


def _outside_cover_faults(p, where, months):
    """Where ``p``, an ItemSpace that has evaluated nothing, departs from OUTSIDE_COVER.

    Every cell of :data:`OUTSIDE_COVER`, ``pols_if_at`` at each timing, ``claims`` at each
    kind and each of :data:`PER_LIFE_OUTSIDE` for each life the point covers, at each of
    ``months``, every one outside the frame; and before the contract is on the books, each of
    :data:`BEFORE_ENTRY`, and survival of each life, 0.0.  Then whether any of
    :data:`IN_COVER_ONLY` was evaluated on the way, which only a fresh ItemSpace can say.  A
    cell that raises is reported as a fault too, so the scan goes on.
    """
    faults = []
    lives = (1, 2) if p.is_joint() else (1,)
    for t in months:
        calls = [(name, (t,), want) for name, want in OUTSIDE_COVER.items()]
        calls += [("pols_if_at", (t, _code(p, timing)), 0.0) for timing in TIMINGS]
        calls += [("claims", (t, _code(p, kind)), 0.0) for kind in KINDS]
        calls += [(name, (t, life), 0.0) for name in PER_LIFE_OUTSIDE for life in lives]
        if t < p.t_entry():
            calls += [(name, (t,), 0.0) for name in BEFORE_ENTRY]
            calls += [("lives_if", (t, life), 0.0) for life in lives]
        for name, args, want in calls:
            try:
                got = p.cells[name](*args)
            except Exception as err:        # reported, so the scan goes on
                faults.append(f"{where}: {name}{args} raised {_raised(err)}")
                continue
            if got != want or type(got) is not type(want):
                faults.append(f"{where}: {name}{args} = {got!r}, not {want!r}")
    read = {}
    for name in IN_COVER_ONLY:
        months_read = sorted(args[0] for args in _cached_args(p.cells[name])
                             if not p.is_active(args[0]))
        if months_read:
            read[name] = months_read
    if read:
        faults.append(f"{where}: evaluated outside the frame: {read}")
    return faults


def test_every_guarded_cell_holds_its_outside_cover_value(spliced):
    """Outside the frame each cell holds :data:`OUTSIDE_COVER`'s value, and reads no rate.

    On every committed point, in every month before the start and in the first month after
    the frame, ``t = proj_len()``, on a model that evaluates nothing else.  So afterwards
    none of :data:`IN_COVER_ONLY` may hold a value outside the frame at all: ``is_active``'s
    docstring promises that outside the frame no count evaluates a rate, and no table is
    read at a policy year or an attained age the contract does not have.

    The committed table's one point starting after the valuation date is the catch-up point,
    so on it a cell tied to another basis would hold zero before the start, guarded or not.
    So the same scan runs on the splice's future rows, the core's or, with
    ``UKLIB_SEC_FULL=1``, all of them: the worked example, the single life in advance, the
    guarantee past the age stop and the LPI among them.  Each row is made afresh first and
    released after.

    Several of these guards change no number the frame shows: once the counts are zero
    outside the frame, every cash flow is too, and an unguarded value multiplies a zero
    count.  They are held here because they are what the docstrings promise a caller, and
    because the C step needs them: a table read at a policy year or an age the contract
    does not have would wrap round in a compiled model rather than fail (USLIB-SEC-PLAN.md
    F4, R1).
    """
    faults = []
    model = mx.read_model(model_path(SEC), name=_name("cover"))
    try:
        table = model.Data.model_point_table()
        for key, point_id in zip(point_keys(model), table.index):
            p = projection(model, key)
            faults += _outside_cover_faults(p, f"point {point_id}",
                                            [*range(p.t_entry()), p.proj_len()])
    finally:
        model.close()
    futures = _selected(FUTURES, CORE_FUTURES)
    for rates, s_point, k in futures:
        sec = spliced.pair(rates)[1]
        key = _row_key(sec, "future", s_point, -k)
        if key in sec.Projection.itemspaces:
            _release(sec, key)
        try:
            p = projection(sec, key)
            where = _case_id(rates, "future", s_point, -k)
            faults += _outside_cover_faults(p, where, [*range(k), p.proj_len()])
        finally:
            _release(sec, key)
    assert futures and not faults, (
        f"{len(faults)} faults outside the frame, first:\n  " + "\n  ".join(faults[:20]))


def test_the_points_sum_row_by_row_into_a_block(spliced):
    """Row ``t`` is the same month on every point, so a block is its frames summed (D3).

    S point 1's twin, the point restated at month 12 and the point starting 12 months on,
    summed as ``run_sec.py --block`` sums them, are indexed 0..647 and equal S's frame added
    to itself moved 12 months earlier and 12 months later.  A model whose frames sat on the
    policy clock would fail it.
    """
    s, sec = spliced.pair("shipped")
    cases = (("shipped", "derived", 1, 12), ("shipped", "future", 1, -12))
    keys = [_row_key(sec, *case[1:]) for case in cases if SEC_FULL or case in CORE_GRID]
    if len(keys) < 2:
        keys = None
    twin = _row_key(sec, "twin", 1, 0)
    if keys is None:
        pytest.skip("the block's rows are the full grid's")
    try:
        frames = [projection(sec, key).result_cf() for key in (twin, *keys)]
    finally:
        for key in (twin, *keys):
            _release(sec, key)
    block = pd.concat(frames).groupby(level="t").sum()
    sdf = _point(s, 1).result_cf()
    expected = pd.concat([sdf, sdf.set_axis(sdf.index - 12).loc[0:],
                          sdf.set_axis(sdf.index + 12)]).groupby(level=0).sum()
    assert list(block.index) == list(range(648))
    assert frame_mismatches(expected, block) == []


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
    ``source_mth`` equals ``duration_mth``, so a formula that read the one for the other would
    pass every test that leaves ``duration_mth`` as generated.  And a refusal names the
    extract's label.
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
            for report in REPORTS:
                assert frame_mismatches(base.cells[report](), mine.cells[report](),
                                        rtol=1e-12, atol=1e-12) == [], (key, report)
            _release(model, key)
    finally:
        model.close()
    runner = folder.parent / "run_sec.py"
    shutil.copy(model_path(SEC).parent / "run_sec.py", runner)
    label = extract.index[extract["policy_id"] == "PA-000001-M17"][0]
    out = _run_sec(runner, str(label))
    p = _row(sec_model, "derived", 1, 17)
    assert out.splitlines()[:2] == [
        f"model point {label}: PA-000001-M17 - M65 with dependant F62 at 50%, purchase "
        f"price 100,000, income 5,400.00 a year, 4 payments in arrears, fixed escalation, "
        f"value protection 50% on first_death, scenario basis",
        f"at the valuation date: {_standing(p)}"]
    last = extract.index[extract["policy_id"] == "PA-000002-M635"][0]
    moved = _set("duration_mth", [last], 637)(extract)
    model = mx.read_model(_sec_inputs(tmp_path / "moved", moved), name=_name("moved"))
    try:
        _refused(_point(model, last).result_cf,
                 f"point_id {last}: duration_mth 637 is at or past the end of the "
                 f"projection, policy month 636")
    finally:
        model.close()


def _standing(p):
    """What ``run_sec.py`` says of point ``p`` at the valuation date, stated here."""
    d = p.duration_mth_init()
    if d < 0:
        return f"to start at t = {-d}, {-d} months after the valuation date"
    if d == 0:
        return "starting at the valuation date, t = 0"
    alive = f"survival {p.lives_if_init(1):.6g}"
    if p.is_joint():
        alive += f", the dependant's {p.lives_if_init(2):.6g}"
    return (f"in payment {d} months: policy year {p.policy_year(0)}, annuitant aged "
            f"{p.age(0, 1)}, {alive}, income {p.annual_income_init():,.2f} a year, "
            f"{p.cum_annuity_all_init():,.2f} paid to date a contract")


def test_run_sec_prints_a_point_and_the_block(sec_model):
    """The runner prints one point, saying where it came from, and the block (D8).

    Each mode in an interpreter of its own, as a user runs it, with exit code 0 and ASCII
    output, so that it prints on a Windows console under any code page.  The numbers are
    the model's.  The worked example, the runner's default, with its lines at the valuation
    date, each asserted whole, so that a longer number cannot pass for the one asserted,
    and its first twelve rows of cash flows and counts.  Point 11, the worked example in
    payment 17 months; point 13, the guarantee's point at 120, whose frame ends at the age
    stop; and point 20, to start 13 months on: each with the lines that say where its row
    came from and where it stands, which only the committed table's generator columns can
    say.  And the block: a line for each of the 22 points, in table order, its first twelve
    rows, which must be the committed points' frames summed row by row, as this test sums
    them, and those frames summed into projection years, each year's ``pols_if`` the one of
    its first month.  Nothing else runs the runner on the committed table.
    """
    runner = model_path(SEC).parent / "run_sec.py"
    out = _run_sec(runner)
    assert out.splitlines()[:3] == [
        "model point 1: PA-000001 (S's PA-000001) - M65 with dependant F62 at 50%, purchase "
        "price 100,000, income 5,400.00 a year, 4 payments in arrears, fixed escalation, "
        "value protection 50% on first_death, scenario basis",
        "at the valuation date: starting at the valuation date, t = 0",
        "proj_len = 636 months from the valuation date (t = 0..635); the frame ends at "
        "policy month 636, the age stop on the youngest life"]
    anchor = _row(sec_model, "twin", 1, 0)
    assert anchor.result_cf().head(12).round(2).to_string() in out
    assert anchor.result_pols().head(12).round(6).to_string() in out
    for point_id, lines in (
            ("11", ["model point 11: PA-000001-M17 (S's PA-000001 at its month 17) - M65 "
                    "with dependant F62 at 50%, purchase price 100,000, income 5,400.00 a "
                    "year, 4 payments in arrears, fixed escalation, value protection 50% on "
                    "first_death, scenario basis",
                    f"at the valuation date: {_standing(_row(sec_model, 'derived', 1, 17))}",
                    "proj_len = 619 months from the valuation date (t = 0..618); the frame "
                    "ends at policy month 636, the age stop on the youngest life"]),
            ("13", ["model point 13: PA-000003-M120 (S's PA-000003 at its month 120) - M65 "
                    "with dependant F62 at 50%, purchase price 100,000, income 5,400.00 a "
                    "year, 4 payments in arrears, fixed escalation, guarantee 120 months, "
                    "scenario basis",
                    f"at the valuation date: "
                    f"{_standing(_row(sec_model, 'derived', 3, 120))}",
                    "proj_len = 516 months from the valuation date (t = 0..515); the frame "
                    "ends at policy month 636, the age stop on the youngest life"]),
            ("20", ["model point 20: PA-000006-F13 (S's PA-000006, starting 13 months on) "
                    "- M65 with dependant F62 at 50%, purchase price 100,000, income "
                    "5,400.00 a year, 4 payments in arrears, rpi_catchup escalation, value "
                    "protection 50% on first_death, table basis",
                    "at the valuation date: to start at t = 13, 13 months after the "
                    "valuation date",
                    "proj_len = 649 months from the valuation date (t = 0..648); the frame "
                    "ends at policy month 636, the age stop on the youngest life"])):
        assert _run_sec(runner, point_id).splitlines()[:3] == lines, point_id
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


# run_sec.py run as though it sat at /m/products/pension_annuity, a copy too shallow to
# have a repository above it: the source compiled under that name, so that its own __file__
# is it.
SHALLOW_RUN = """\
import sys
source = open(sys.argv[1], encoding="utf-8").read()
where = "/m/products/pension_annuity/run_sec.py"
sys.argv = [where, "--cython"]
exec(compile(source, where, "exec"), {"__name__": "__main__", "__file__": where})
"""


def test_run_sec_says_a_copy_without_the_repository_cannot_build(tmp_path):
    """``run_sec.py --cython`` outside the repository stops, saying it cannot build.

    The runner is uslib Term's as it stands, ``--cython`` and ``_tool()`` included
    (USLIB-SEC-PLAN.md §7.1, *Record — M14*, *Carried into Phase 1*), so that the C step
    changes nothing in it.  ``--cython`` builds with the repository's
    ``tools/build_sec_cy.py``, which a ``lifelib.create()`` copy does not carry, wherever the
    copy is: beside a copy of the model and its inputs, and at a path too shallow to hold a
    repository above the product at all.  Each must exit nonzero having printed nothing, and
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

    A compiled model declares a defaulted parameter in its ``.pxd`` as ``long long x=*``,
    which the C step's typing guard would read as a parameter of that name, so no cell here
    adds one: ``PA_UK_S``'s one, ``claims``' ``kind=None``, is R12's total, which the C step
    settles, as it did ``Term_UK_SEC``'s.
    """
    assert _defaulted(TWIN) == ["claims"]
    assert _defaulted(SEC) == ["claims"]


# The texts a cell keyed by t may hold at stage "E": the kinds and the timings, which the C
# step makes int References, as it did Term's, CI's and ULB's (R9).
CODES = frozenset({"VP", "PROP", "BEF_NB", "BEF_DECR", "ANNUITANT", "ALL"})


def test_no_monthly_cell_builds_a_python_object(sec_model):
    """No cell keyed by ``t`` builds a tuple, a text or a generator but to raise (§6.7, *C*).

    The C step's static check refuses a Python object in a computed cell, and turns
    ``PA_UK_S``'s own into the C forms UKLIB-SEC-PLAN.md §6.7 lists: the claims total's
    generator, ``horizon_mths``'s list, which takes no ``t``, the label accessors' text and
    the text kinds and timings.  So that the C step restructures nothing beyond that list,
    no ``Projection`` cell with a ``t`` parameter but ``claims``, the total, holds a tuple, a
    list, a set, a dict, a comprehension, a generator or an f-string, or a text other than
    a kind or a timing (:data:`CODES`), but inside a ``raise`` statement, read from the
    source as the build reads it.
    """
    source = (model_path(SEC) / "Projection" / "__init__.py").read_text(encoding="utf-8")
    built = (ast.Tuple, ast.List, ast.Set, ast.Dict, ast.GeneratorExp, ast.ListComp,
             ast.SetComp, ast.DictComp, ast.JoinedStr)
    found, monthly = [], []
    for node in ast.parse(source).body:
        if not isinstance(node, ast.FunctionDef) or node.name == "claims":
            continue
        if "t" not in [arg.arg for arg in node.args.args]:
            continue
        monthly.append(node.name)
        raises = {id(n) for r in ast.walk(node) if isinstance(r, ast.Raise)
                  for n in ast.walk(r)}
        body = node.body[1:] if ast.get_docstring(node) is not None else node.body
        for inner in (n for statement in body for n in ast.walk(statement)):
            if id(inner) in raises:
                continue
            if isinstance(inner, built):
                found.append(f"{node.name}: {type(inner).__name__} at line {inner.lineno}")
            elif (isinstance(inner, ast.Constant) and isinstance(inner.value, str)
                  and inner.value not in CODES):
                found.append(f"{node.name}: the text {inner.value!r} at line "
                             f"{inner.lineno}")
    assert set(monthly) == {name for name, cells in sec_model.Projection.cells.items()
                            if "t" in cells.parameters} - {"claims"}
    assert not found, found


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
    outside the parentheses and quotes of the column, ``claims`` of ``claims(t, "VP")``; a
    cell of two names, ``expense_maint, inflation_rate``, maps both.
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
    whose text runs into the gap between two spans is what docutils rejects as a malformed
    table, dropping the whole table from the page.  Only the last column may run past its
    rule.  Each table runs from a rule line to the blank line that ends it.
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


# What only PA_UK_S's docstrings may say: a reference into its Spaces, which the SEC pages
# would link to the wrong model; its clock, t counting months from the annuity start date;
# and the first year's income under the name SEC gives the year under way.
STALE = re.compile(r"~\.PA_UK_S\.|``t`` counts \*\*months from the annuity start date\*\*"
                   r"|A\(1\)\s+annual_income_init\(\)")


def test_the_docstrings_describe_the_valuation_clock(sec_model, s_model):
    """The docstrings say what this model is, and none says what only PA_UK_S is.

    Whitespace is collapsed first, as ``test_model_conventions_uk`` collapses it, so that a
    phrase split across a line break still matches.  The model docstring names the valuation
    date, BasicTerm_SE, the policy clock, the SEC table, the payout chassis and the product.
    The symbol map in the Projection docstring maps every cell running in force adds, which
    are exactly the cells ``PA_UK_S`` lacks, and names nothing the model lacks: every name in
    it is a cell or a Reference.  No row of a simple table in any docstring puts text between
    two of its columns (:func:`_table_overruns`), which would drop the table from the
    rendered page.  And no docstring says what :data:`STALE` matches.
    """
    flat = {where: re.sub(r"\s+", " ", doc) for where, doc in _docs(sec_model)}
    for phrase in ("valuation date", "BasicTerm_SE", "duration_mth", TABLE, "SPIA_US_SEC",
                   "pension annuit"):
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
    assert not stale, f"docstrings that describe PA_UK_S: {stale}"


@pytest.mark.docutils
def test_the_docstrings_parse_as_rst(sec_model):
    """Every docstring of the model parses as reStructuredText, without a warning.

    The docs build reads each docstring through docutils, which reports a malformed table, a
    bad indentation or an unclosed inline markup and drops what it cannot read; a raw-text
    test sees none of it.  Each docstring, dedented as autodoc dedents it and its Sphinx
    roles read as plain interpreted text, which docutils alone does not know, is parsed
    here, and any warning or error is a fault.  docutils comes with the docs build, not with
    the models' requirements, so the test is skipped where it is absent; the column check in
    the test above runs everywhere.
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


def test_the_sec_model_reads_the_s_table_in_place(sec_model, s_model):
    """One copy of the mortality table serves both models (D1).

    The two ``input_dir()`` s are one directory, and SEC's filename References are S's with
    ``model_point_file`` changed, to ``model_point_table_sec.csv``: an edit to the table
    reaches both models, and the two can never drift apart.  And every Reference of S's is
    the SEC model's at S's value, but the one it adds, the youngest issue age, so that no
    assumption moves between the two.
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
    assert sec_refs == {**s_refs, "issue_age_min": 0}


def test_the_core_grid_reaches_every_branch(spliced, splice_records):
    """What the default run's T2 and T3 cases reach, which the full grid only multiplies.

    The default run thins the splice to a core (the module docstring), and this test is what
    keeps the thinning from costing a branch.  First, statically, over S's table with the
    variants, each property below holds of some core case: every escalation basis, timing,
    frequency and mortality basis, each value-protection basis, the guarantee with and
    without overlap, the proportionate payment, a single and a joint life, a rating, each
    variant, and each RPI set; and each kind of valuation month: the first months, a payment
    month and one between, on an anniversary, the month before and after one, about the
    scenario death, about the guarantee's end, about value protection running out, about the
    cap, past the limiting age and the last month of a frame.  And of some core future case:
    starting off the valuation anniversaries and on them, more than a year on, each basis,
    a variant and an RPI set.

    Then, on the splice's models, of some core row, each of :data:`AT_VALUATION` and
    :data:`IN_FRAME`, what no column of the table shows: every opening-state column in use,
    and every branch and both sides of every ``min`` and ``max`` the full grid reaches.

    Each core row's branches were recorded by the T2 or T3 case that compared it
    (:func:`_scan`), and a row no case has recorded is evaluated here.  With
    ``UKLIB_SEC_FULL=1`` it asks the same of the full grid's rows, which must reach nothing
    the core does not.
    """
    assert set(CORE_SPLICES) <= set(SPLICES) and set(CORE_FUTURES) <= set(FUTURES)
    s_table = _s_table_with_variants()

    def at(p, column):
        return s_table.at[p, column]

    def flag(p, column):
        return str(at(p, column)).lower() == "true"

    splices = {
        **{f"{e} escalation": (lambda r, k, p, d, e=e: at(p, "escalation_type") == e)
           for e in ("level", "fixed", "lpi5", "rpi_catchup")},
        **{f"{w} timing": (lambda r, k, p, d, w=w: at(p, "timing") == w)
           for w in ("arrears", "advance")},
        **{f"{m} payments a year": (lambda r, k, p, d, m=m: at(p, "frequency") == m)
           for m in (12, 4, 2, 1)},
        **{f"the {b} basis": (lambda r, k, p, d, b=b: at(p, "mort_basis") == b)
           for b in ("table", "scenario")},
        **{f"value protection on {b}": (
            lambda r, k, p, d, b=b: at(p, "vp_pct") > 0 and at(p, "vp_basis") == b)
           for b in ("first_death", "last_survivor")},
        "a guarantee without overlap": lambda r, k, p, d: (
            at(p, "guarantee_months") > 0 and not flag(p, "overlap")),
        "a guarantee with overlap": lambda r, k, p, d: (
            at(p, "guarantee_months") > 0 and flag(p, "overlap")),
        "the proportionate payment": lambda r, k, p, d: flag(p, "proportion"),
        "a single life": lambda r, k, p, d: not flag(p, "dependant_present"),
        "a rating": lambda r, k, p, d: at(p, "rating_multiplier") > 1.0,
        **{f"variant {v}": (lambda r, k, p, d, v=v: p == v) for v in VARIANTS},
        **{f"the {s} set": (lambda r, k, p, d, s=s: r == s) for s in SPLICE_SETS},
        "in the second month": lambda r, k, p, d: d == 1,
        "on an anniversary": lambda r, k, p, d: d % 12 == 0,
        "in the month before an anniversary": lambda r, k, p, d: d % 12 == 11,
        "in the month after an anniversary": lambda r, k, p, d: d % 12 == 1 and d > 12,
        "about the scenario death": lambda r, k, p, d: (
            at(p, "mort_basis") == "scenario" and 15 <= d <= 17),
        "about the guarantee's end": lambda r, k, p, d: (
            at(p, "guarantee_months") > 0 and 119 <= d <= 122),
        "about value protection running out": lambda r, k, p, d: d in (101, 102, 170, 171),
        "about the cap": lambda r, k, p, d: d in (575, 576),
        "past the limiting age": lambda r, k, p, d: d >= 600,
        "the last month of a frame": lambda r, k, p, d: d == FRAME[p] - 1,
    }
    futures = {
        "starting off the anniversaries": lambda r, p, k: k % 12 != 0,
        "starting on them": lambda r, p, k: k % 12 == 0,
        "starting more than a year on": lambda r, p, k: k > 12,
        **{f"{e} escalation": (lambda r, p, k, e=e: at(p, "escalation_type") == e)
           for e in ("level", "fixed", "lpi5", "rpi_catchup")},
        "a variant": lambda r, p, k: p in VARIANTS,
        "an RPI set": lambda r, p, k: r != "shipped",
    }
    missing = [what for what, holds in splices.items()
               if not any(holds(r, k, p, d) for r, k, p, d in CORE_SPLICES)]
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
    model as M11 committed it was frozen below (USLIB-SEC-PLAN.md §5.4): for each point,
    each column of ``result_cf()`` and ``result_pols()``, its sum, its largest absolute value
    and its values at five fixed months, the frame's first and last and the three quartiles
    between.  Every later version must reproduce it, to 1e-12 relative, floored at 1e-12 of
    the column's own magnitude (``uk_sec_support.fingerprint_mismatches``), with the same
    points, frames and columns exactly.  ``python tools/gen_sec_fingerprint.py PA_UK_SEC
    --check`` runs the same comparison from the command line.  Until the freeze, which is
    committed alone, the block is empty and the test skips.
    """
    if not FINGERPRINT:
        pytest.skip("the Phase 1 fingerprint is frozen in a commit of its own")
    assert fingerprint_mismatches(FINGERPRINT, sec_model) == []


# PA_UK_SEC's fingerprint, frozen from the model as M11 committed it and committed alone,
# before its C step changed anything.  Each point is keyed by its point_id; each column
# holds (its sum over the frame, its largest absolute value, (its values at the months)).
# The block is written by tools/gen_sec_fingerprint.py, and is never edited by hand: a
# refreeze goes through the tool's --force, in a commit of its own that says why.
# BEGIN generated fingerprint: PA_UK_SEC -- tools/gen_sec_fingerprint.py
FINGERPRINT = {
    1: {"rows": 636, "months": (0, 158, 317, 476, 635),
        "result_cf": {
            "pols_if": (636.0, 1.0, (
                1.0, 1.0, 1.0, 1.0, 1.0)),
            "annuity_payments": (344532.3724893371, 3139.347979291292, (
                0.0, 991.2602565798063, 1455.699105592094, 2137.7432132032795,
                3139.347979291292)),
            "claims_vp": (43209.5, 43209.5, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_prop": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (3790.4124721037456, 11.627214738115894, (
                2.5, 3.6713342836289122, 5.3914781688596065, 7.917567456308441,
                11.627214738115894)),
            "liability_cf": (391532.28496144083, 43212.075, (
                2.5, 994.9315908634352, 1461.0905837609535, 2145.660780659588,
                3150.975194029408)),
            "net_cf": (-391532.28496144083, 43212.075, (
                -2.5, -994.9315908634352, -1461.0905837609535, -2145.660780659588,
                -3150.975194029408)),
        },
        "result_pols": {
            "pols_if": (636.0, 1.0, (
                1.0, 1.0, 1.0, 1.0, 1.0)),
            "pols_new_biz": (1.0, 1.0, (
                1.0, 0.0, 0.0, 0.0, 0.0)),
            "lives_if_1": (16.0, 1.0, (
                1.0, 0.0, 0.0, 0.0, 0.0)),
            "lives_if_2": (636.0, 1.0, (
                1.0, 1.0, 1.0, 1.0, 1.0)),
            "certain_floor": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "payment_factor": (16.0, 1.0, (
                1.0, 0.0, 0.0, 0.0, 0.0)),
            "dependant_factor": (310.0, 0.5, (
                0.0, 0.5, 0.5, 0.5, 0.5)),
            "annuity_pp": (682274.2449786742, 6278.695958582584, (
                0.0, 1982.5205131596126, 2911.398211184188, 4275.486426406559,
                6278.695958582584)),
            "cum_annuity_all": (83223198.6694261, 344532.372489337, (
                0.0, 46554.54446722057, 110399.86229012994, 204840.90806671337,
                344532.372489337)),
            "vp_balance": (2613228.2674394264, 50000.0, (
                50000.0, 0.0, 0.0, 0.0, 0.0)),
        },
    },
    2: {"rows": 636, "months": (0, 158, 317, 476, 635),
        "result_cf": {
            "pols_if": (401.3639797203242, 0.9999996527930258, (
                0.9999996527930258, 0.9786592131323972, 0.7969351733402389,
                0.25123977404281717, 0.0007810393830953411)),
            "annuity_payments": (254846.7812328438, 1872.0932658719873, (
                0.0, 1760.74568844968, 1766.8491633953627, 613.1141716348682,
                2.4519544090672767)),
            "claims_vp": (2629.202964676305, 41.92133577406443, (
                41.92133577406443, 0.0, 0.0, 0.0, 0.0)),
            "claims_prop": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (1773.3206084225367, 4.355937739992102, (
                2.4999991319825647, 3.5929851211622643, 4.296658589060244,
                1.9892078586916953, 0.009081312626175096)),
            "liability_cf": (259249.30480594264, 1876.3001596047736, (
                44.421334906046994, 1764.3386735708423, 1771.1458219844228,
                615.1033794935598, 2.461035721693452)),
            "net_cf": (-259249.30480594264, 1876.3001596047736, (
                -44.421334906046994, -1764.3386735708423, -1771.1458219844228,
                -615.1033794935598, -2.461035721693452)),
        },
        "result_pols": {
            "pols_if": (401.3639797203242, 0.9999996527930258, (
                0.9999996527930258, 0.9786592131323972, 0.7969351733402389,
                0.25123977404281717, 0.0007810393830953411)),
            "pols_new_biz": (1.0, 1.0, (
                1.0, 0.0, 0.0, 0.0, 0.0)),
            "lives_if_1": (276.4174277088396, 0.9991615732845187, (
                0.9991615732845187, 0.7976106178854093, 0.41681096183837085,
                0.03556463157901314, 0.0)),
            "lives_if_2": (359.27999007317993, 0.9995858827400101, (
                0.9995858827400101, 0.8945557981123737, 0.6518027374110514,
                0.22362840427235284, 0.0007810393830953411)),
            "certain_floor": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "payment_factor": (276.4174277088396, 0.9991615732845187, (
                0.9991615732845187, 0.7976106178854093, 0.41681096183837085,
                0.03556463157901314, 0.0)),
            "dependant_factor": (62.473276005742306, 0.1962284948587069, (
                0.0004190397542535856, 0.09052429762349393, 0.19006210575093402,
                0.107837571231902, 0.00039051969154767056)),
            "annuity_pp": (682274.2449786742, 6278.695958582584, (
                0.0, 1982.5205131596126, 2911.398211184188, 4275.486426406559,
                6278.695958582584)),
            "cum_annuity_all": (101435853.36923331, 254846.7812328438, (
                0.0, 81887.70612398398, 178200.2726710993, 245403.96321923507,
                254846.7812328438)),
            "vp_balance": (2613228.2674394264, 50000.0, (
                50000.0, 0.0, 0.0, 0.0, 0.0)),
        },
    },
    3: {"rows": 636, "months": (0, 158, 317, 476, 635),
        "result_cf": {
            "pols_if": (636.0, 1.0, (
                1.0, 1.0, 1.0, 1.0, 1.0)),
            "annuity_payments": (372089.5966303081, 3139.347979291292, (
                0.0, 991.2602565798063, 1455.699105592094, 2137.7432132032795,
                3139.347979291292)),
            "claims_vp": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_prop": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (3790.4124721037456, 11.627214738115894, (
                2.5, 3.6713342836289122, 5.3914781688596065, 7.917567456308441,
                11.627214738115894)),
            "liability_cf": (375880.00910241186, 3150.975194029408, (
                2.5, 994.9315908634352, 1461.0905837609535, 2145.660780659588,
                3150.975194029408)),
            "net_cf": (-375880.00910241186, 3150.975194029408, (
                -2.5, -994.9315908634352, -1461.0905837609535, -2145.660780659588,
                -3150.975194029408)),
        },
        "result_pols": {
            "pols_if": (636.0, 1.0, (
                1.0, 1.0, 1.0, 1.0, 1.0)),
            "pols_new_biz": (1.0, 1.0, (
                1.0, 0.0, 0.0, 0.0, 0.0)),
            "lives_if_1": (16.0, 1.0, (
                1.0, 0.0, 0.0, 0.0, 0.0)),
            "lives_if_2": (636.0, 1.0, (
                1.0, 1.0, 1.0, 1.0, 1.0)),
            "certain_floor": (120.0, 1.0, (
                1.0, 0.0, 0.0, 0.0, 0.0)),
            "payment_factor": (120.0, 1.0, (
                1.0, 0.0, 0.0, 0.0, 0.0)),
            "dependant_factor": (258.0, 0.5, (
                0.0, 0.5, 0.5, 0.5, 0.5)),
            "annuity_pp": (682274.2449786742, 6278.695958582584, (
                0.0, 1982.5205131596126, 2911.398211184188, 4275.486426406559,
                6278.695958582584)),
            "cum_annuity_all": (98813808.09033085, 372089.5966303081, (
                0.0, 74111.76860819152, 137957.08643110088, 232398.13220768436,
                372089.5966303081)),
            "vp_balance": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
        },
    },
    4: {"rows": 636, "months": (0, 158, 317, 476, 635),
        "result_cf": {
            "pols_if": (636.0, 1.0, (
                1.0, 1.0, 1.0, 1.0, 1.0)),
            "annuity_payments": (399646.82077127905, 3139.347979291292, (
                0.0, 991.2602565798063, 1455.699105592094, 2137.7432132032795,
                3139.347979291292)),
            "claims_vp": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_prop": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (3790.4124721037456, 11.627214738115894, (
                2.5, 3.6713342836289122, 5.3914781688596065, 7.917567456308441,
                11.627214738115894)),
            "liability_cf": (403437.2332433828, 3150.975194029408, (
                2.5, 994.9315908634352, 1461.0905837609535, 2145.660780659588,
                3150.975194029408)),
            "net_cf": (-403437.2332433828, 3150.975194029408, (
                -2.5, -994.9315908634352, -1461.0905837609535, -2145.660780659588,
                -3150.975194029408)),
        },
        "result_pols": {
            "pols_if": (636.0, 1.0, (
                1.0, 1.0, 1.0, 1.0, 1.0)),
            "pols_new_biz": (1.0, 1.0, (
                1.0, 0.0, 0.0, 0.0, 0.0)),
            "lives_if_1": (16.0, 1.0, (
                1.0, 0.0, 0.0, 0.0, 0.0)),
            "lives_if_2": (636.0, 1.0, (
                1.0, 1.0, 1.0, 1.0, 1.0)),
            "certain_floor": (120.0, 1.0, (
                1.0, 0.0, 0.0, 0.0, 0.0)),
            "payment_factor": (120.0, 1.0, (
                1.0, 0.0, 0.0, 0.0, 0.0)),
            "dependant_factor": (310.0, 0.5, (
                0.0, 0.5, 0.5, 0.5, 0.5)),
            "annuity_pp": (682274.2449786742, 6278.695958582584, (
                0.0, 1982.5205131596126, 2911.398211184188, 4275.486426406559,
                6278.695958582584)),
            "cum_annuity_all": (114404417.51123567, 399646.8207712792, (
                0.0, 101668.99274916259, 165514.3105720719, 259955.3563486554,
                399646.8207712792)),
            "vp_balance": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
        },
    },
    5: {"rows": 600, "months": (0, 149, 299, 449, 599),
        "result_cf": {
            "pols_if": (276.4174277088396, 0.9991615732845187, (
                0.9991615732845187, 0.8137041019416205, 0.4670748754713106,
                0.07405012124087278, 2.2262204334465577e-06)),
            "annuity_payments": (153897.316786483, 554.75, (
                554.75, 452.37852604622356, 260.5739909675787, 42.050408153281644,
                0.0014122545281038566)),
            "claims_vp": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_prop": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (1070.1563008632647, 2.9458657038134453, (
                2.4979039332112967, 2.9003687050366467, 2.3736676353345185,
                0.5526409935643593, 2.3688206692123985e-05)),
            "liability_cf": (154967.47308734627, 557.2479039332113, (
                557.2479039332113, 455.2788947512602, 262.94765860291324,
                42.603049146846004, 0.0014359427347959805)),
            "net_cf": (-154967.47308734627, 557.2479039332113, (
                -557.2479039332113, -455.2788947512602, -262.94765860291324,
                -42.603049146846004, -0.0014359427347959805)),
        },
        "result_pols": {
            "pols_if": (276.4174277088396, 0.9991615732845187, (
                0.9991615732845187, 0.8137041019416205, 0.4670748754713106,
                0.07405012124087278, 2.2262204334465577e-06)),
            "pols_new_biz": (1.0, 1.0, (
                1.0, 0.0, 0.0, 0.0, 0.0)),
            "lives_if_1": (276.4174277088396, 0.9991615732845187, (
                0.9991615732845187, 0.8137041019416205, 0.4670748754713106,
                0.07405012124087278, 2.2262204334465577e-06)),
            "lives_if_2": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "certain_floor": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "payment_factor": (277.4174254826192, 1.0, (
                1.0, 0.8154637693487581, 0.4697142694323186, 0.07580064561204443,
                2.54574948734359e-06)),
            "dependant_factor": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "annuity_pp": (332850.0, 554.75, (
                554.75, 554.75, 554.75, 554.75, 554.75)),
            "cum_annuity_all": (66668377.01000083, 153897.3167864827, (
                554.75, 76507.03035744594, 130951.6704879523, 152598.53369829335,
                153897.3167864827)),
            "vp_balance": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
        },
    },
    6: {"rows": 636, "months": (0, 158, 317, 476, 635),
        "result_cf": {
            "pols_if": (401.3639797203242, 0.9999996527930258, (
                0.9999996527930258, 0.9786592131323972, 0.7969351733402389,
                0.25123977404281717, 0.0007810393830953411)),
            "annuity_payments": (254846.78123284376, 1872.093265871987, (
                0.0, 1760.7456884496798, 1766.8491633953627, 613.1141716348681,
                2.451954409067276)),
            "claims_vp": (2629.202964676305, 41.92133577406443, (
                41.92133577406443, 0.0, 0.0, 0.0, 0.0)),
            "claims_prop": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (1773.3206084225367, 4.355937739992102, (
                2.4999991319825647, 3.5929851211622643, 4.296658589060244,
                1.9892078586916953, 0.009081312626175096)),
            "liability_cf": (259249.30480594258, 1876.3001596047732, (
                44.421334906046994, 1764.338673570842, 1771.1458219844228,
                615.1033794935597, 2.461035721693451)),
            "net_cf": (-259249.30480594258, 1876.3001596047732, (
                -44.421334906046994, -1764.338673570842, -1771.1458219844228,
                -615.1033794935597, -2.461035721693451)),
        },
        "result_pols": {
            "pols_if": (401.3639797203242, 0.9999996527930258, (
                0.9999996527930258, 0.9786592131323972, 0.7969351733402389,
                0.25123977404281717, 0.0007810393830953411)),
            "pols_new_biz": (1.0, 1.0, (
                1.0, 0.0, 0.0, 0.0, 0.0)),
            "lives_if_1": (276.4174277088396, 0.9991615732845187, (
                0.9991615732845187, 0.7976106178854093, 0.41681096183837085,
                0.03556463157901314, 0.0)),
            "lives_if_2": (359.27999007317993, 0.9995858827400101, (
                0.9995858827400101, 0.8945557981123737, 0.6518027374110514,
                0.22362840427235284, 0.0007810393830953411)),
            "certain_floor": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "payment_factor": (276.4174277088396, 0.9991615732845187, (
                0.9991615732845187, 0.7976106178854093, 0.41681096183837085,
                0.03556463157901314, 0.0)),
            "dependant_factor": (62.473276005742306, 0.1962284948587069, (
                0.0004190397542535856, 0.09052429762349393, 0.19006210575093402,
                0.107837571231902, 0.00039051969154767056)),
            "annuity_pp": (682274.2449786742, 6278.6959585825825, (
                0.0, 1982.5205131596124, 2911.398211184188, 4275.486426406558,
                6278.6959585825825)),
            "cum_annuity_all": (101435853.36923331, 254846.78123284376, (
                0.0, 81887.70612398398, 178200.27267109926, 245403.96321923504,
                254846.78123284376)),
            "vp_balance": (2613228.2674394264, 50000.0, (
                50000.0, 0.0, 0.0, 0.0, 0.0)),
        },
    },
    7: {"rows": 636, "months": (0, 158, 317, 476, 635),
        "result_cf": {
            "pols_if": (401.3639797203242, 0.9999996527930258, (
                0.9999996527930258, 0.9786592131323972, 0.7969351733402389,
                0.25123977404281717, 0.0007810393830953411)),
            "annuity_payments": (254846.7812328438, 1872.0932658719873, (
                0.0, 1760.74568844968, 1766.8491633953627, 613.1141716348682,
                2.4519544090672767)),
            "claims_vp": (2629.202964676305, 41.92133577406443, (
                41.92133577406443, 0.0, 0.0, 0.0, 0.0)),
            "claims_prop": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (1773.3206084225367, 4.355937739992102, (
                2.4999991319825647, 3.5929851211622643, 4.296658589060244,
                1.9892078586916953, 0.009081312626175096)),
            "liability_cf": (259249.30480594264, 1876.3001596047736, (
                44.421334906046994, 1764.3386735708423, 1771.1458219844228,
                615.1033794935598, 2.461035721693452)),
            "net_cf": (-259249.30480594264, 1876.3001596047736, (
                -44.421334906046994, -1764.3386735708423, -1771.1458219844228,
                -615.1033794935598, -2.461035721693452)),
        },
        "result_pols": {
            "pols_if": (401.3639797203242, 0.9999996527930258, (
                0.9999996527930258, 0.9786592131323972, 0.7969351733402389,
                0.25123977404281717, 0.0007810393830953411)),
            "pols_new_biz": (1.0, 1.0, (
                1.0, 0.0, 0.0, 0.0, 0.0)),
            "lives_if_1": (276.4174277088396, 0.9991615732845187, (
                0.9991615732845187, 0.7976106178854093, 0.41681096183837085,
                0.03556463157901314, 0.0)),
            "lives_if_2": (359.27999007317993, 0.9995858827400101, (
                0.9995858827400101, 0.8945557981123737, 0.6518027374110514,
                0.22362840427235284, 0.0007810393830953411)),
            "certain_floor": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "payment_factor": (276.4174277088396, 0.9991615732845187, (
                0.9991615732845187, 0.7976106178854093, 0.41681096183837085,
                0.03556463157901314, 0.0)),
            "dependant_factor": (62.473276005742306, 0.1962284948587069, (
                0.0004190397542535856, 0.09052429762349393, 0.19006210575093402,
                0.107837571231902, 0.00039051969154767056)),
            "annuity_pp": (682274.2449786742, 6278.695958582584, (
                0.0, 1982.5205131596126, 2911.398211184188, 4275.486426406559,
                6278.695958582584)),
            "cum_annuity_all": (101435853.36923331, 254846.7812328438, (
                0.0, 81887.70612398398, 178200.2726710993, 245403.96321923507,
                254846.7812328438)),
            "vp_balance": (2613228.2674394264, 50000.0, (
                50000.0, 0.0, 0.0, 0.0, 0.0)),
        },
    },
    8: {"rows": 600, "months": (0, 149, 299, 449, 599),
        "result_cf": {
            "pols_if": (243.54429129936705, 0.9988662863073619, (
                0.9988662863073619, 0.7563952296327764, 0.35519933492572275,
                0.027179186481920845, 0.0)),
            "annuity_payments": (160333.32510541665, 657.5869718190132, (
                657.5869718190132, 497.9601928415778, 233.83956215943417,
                17.892964433931223, 0.0)),
            "claims_vp": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_prop": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (900.9163959547881, 2.746223095907662, (
                2.4971657157684044, 2.6960968335186166, 1.805117786639161,
                0.20284008141973303, 0.0)),
            "liability_cf": (161234.24150137146, 660.0841375347817, (
                660.0841375347817, 500.6562896750964, 235.64467994607332,
                18.095804515350956, 0.0)),
            "net_cf": (-161234.24150137146, 660.0841375347817, (
                -660.0841375347817, -500.6562896750964, -235.64467994607332,
                -18.095804515350956, -0.0)),
        },
        "result_pols": {
            "pols_if": (243.54429129936705, 0.9988662863073619, (
                0.9988662863073619, 0.7563952296327764, 0.35519933492572275,
                0.027179186481920845, 0.0)),
            "pols_new_biz": (1.0, 1.0, (
                1.0, 0.0, 0.0, 0.0, 0.0)),
            "lives_if_1": (243.54429129936705, 0.9988662863073619, (
                0.9988662863073619, 0.7563952296327764, 0.35519933492572275,
                0.027179186481920845, 0.0)),
            "lives_if_2": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "certain_floor": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "payment_factor": (243.54429129936705, 0.9988662863073619, (
                0.9988662863073619, 0.7563952296327764, 0.35519933492572275,
                0.027179186481920845, 0.0)),
            "dependant_factor": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "annuity_pp": (395000.0, 658.3333333333334, (
                658.3333333333334, 658.3333333333334, 658.3333333333334, 658.3333333333334,
                658.3333333333334)),
            "cum_annuity_all": (72087556.50971282, 160333.32510541662, (
                657.5869718190132, 88047.26898219695, 143641.6424749281, 159927.70691758662,
                160333.32510541662)),
            "vp_balance": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
        },
    },
    9: {"rows": 636, "months": (0, 158, 317, 476, 635),
        "result_cf": {
            "pols_if": (636.0, 1.0, (
                1.0, 1.0, 1.0, 1.0, 1.0)),
            "annuity_payments": (344532.3724893371, 3139.347979291292, (
                0.0, 991.2602565798063, 1455.699105592094, 2137.7432132032795,
                3139.347979291292)),
            "claims_vp": (43209.5, 43209.5, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_prop": (695.25, 695.25, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (3790.4124721037456, 11.627214738115894, (
                2.5, 3.6713342836289122, 5.3914781688596065, 7.917567456308441,
                11.627214738115894)),
            "liability_cf": (392227.53496144083, 43907.325, (
                2.5, 994.9315908634352, 1461.0905837609535, 2145.660780659588,
                3150.975194029408)),
            "net_cf": (-392227.53496144083, 43907.325, (
                -2.5, -994.9315908634352, -1461.0905837609535, -2145.660780659588,
                -3150.975194029408)),
        },
        "result_pols": {
            "pols_if": (636.0, 1.0, (
                1.0, 1.0, 1.0, 1.0, 1.0)),
            "pols_new_biz": (1.0, 1.0, (
                1.0, 0.0, 0.0, 0.0, 0.0)),
            "lives_if_1": (16.0, 1.0, (
                1.0, 0.0, 0.0, 0.0, 0.0)),
            "lives_if_2": (636.0, 1.0, (
                1.0, 1.0, 1.0, 1.0, 1.0)),
            "certain_floor": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "payment_factor": (16.0, 1.0, (
                1.0, 0.0, 0.0, 0.0, 0.0)),
            "dependant_factor": (310.0, 0.5, (
                0.0, 0.5, 0.5, 0.5, 0.5)),
            "annuity_pp": (682274.2449786742, 6278.695958582584, (
                0.0, 1982.5205131596126, 2911.398211184188, 4275.486426406559,
                6278.695958582584)),
            "cum_annuity_all": (83223198.6694261, 344532.372489337, (
                0.0, 46554.54446722057, 110399.86229012994, 204840.90806671337,
                344532.372489337)),
            "vp_balance": (2613228.2674394264, 50000.0, (
                50000.0, 0.0, 0.0, 0.0, 0.0)),
        },
    },
    10: {"rows": 636, "months": (0, 158, 317, 476, 635),
        "result_cf": {
            "pols_if": (636.0, 1.0, (
                1.0, 1.0, 1.0, 1.0, 1.0)),
            "annuity_payments": (344532.3724893371, 3139.347979291292, (
                0.0, 991.2602565798063, 1455.699105592094, 2137.7432132032795,
                3139.347979291292)),
            "claims_vp": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_prop": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (3790.4124721037456, 11.627214738115894, (
                2.5, 3.6713342836289122, 5.3914781688596065, 7.917567456308441,
                11.627214738115894)),
            "liability_cf": (348322.7849614409, 3150.975194029408, (
                2.5, 994.9315908634352, 1461.0905837609535, 2145.660780659588,
                3150.975194029408)),
            "net_cf": (-348322.7849614409, 3150.975194029408, (
                -2.5, -994.9315908634352, -1461.0905837609535, -2145.660780659588,
                -3150.975194029408)),
        },
        "result_pols": {
            "pols_if": (636.0, 1.0, (
                1.0, 1.0, 1.0, 1.0, 1.0)),
            "pols_new_biz": (1.0, 1.0, (
                1.0, 0.0, 0.0, 0.0, 0.0)),
            "lives_if_1": (16.0, 1.0, (
                1.0, 0.0, 0.0, 0.0, 0.0)),
            "lives_if_2": (636.0, 1.0, (
                1.0, 1.0, 1.0, 1.0, 1.0)),
            "certain_floor": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "payment_factor": (16.0, 1.0, (
                1.0, 0.0, 0.0, 0.0, 0.0)),
            "dependant_factor": (310.0, 0.5, (
                0.0, 0.5, 0.5, 0.5, 0.5)),
            "annuity_pp": (682274.2449786742, 6278.695958582584, (
                0.0, 1982.5205131596126, 2911.398211184188, 4275.486426406559,
                6278.695958582584)),
            "cum_annuity_all": (83223198.6694261, 344532.372489337, (
                0.0, 46554.54446722057, 110399.86229012994, 204840.90806671337,
                344532.372489337)),
            "vp_balance": (4270862.840938796, 50000.0, (
                50000.0, 3445.4555327794296, 0.0, 0.0, 0.0)),
        },
    },
    11: {"rows": 619, "months": (0, 154, 309, 463, 618),
        "result_cf": {
            "pols_if": (619.0, 1.0, (
                1.0, 1.0, 1.0, 1.0, 1.0)),
            "annuity_payments": (337741.87248933717, 3139.347979291292, (
                695.25, 0.0, 1499.3700787598568, 0.0, 3139.347979291292)),
            "claims_vp": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_prop": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (3594.443105255501, 11.288557998170772, (
                2.5, 3.564402217115448, 5.23444482413554, 7.686958695445089,
                11.288557998170772)),
            "liability_cf": (341336.3155945926, 3150.636537289463, (
                697.75, 3.564402217115448, 1504.6045235839924, 7.686958695445089,
                3150.636537289463)),
            "net_cf": (-341336.3155945926, 3150.636537289463, (
                -697.75, -3.564402217115448, -1504.6045235839924, -7.686958695445089,
                -3150.636537289463)),
        },
        "result_pols": {
            "pols_if": (619.0, 1.0, (
                1.0, 1.0, 1.0, 1.0, 1.0)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "lives_if_1": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "lives_if_2": (619.0, 1.0, (
                1.0, 1.0, 1.0, 1.0, 1.0)),
            "certain_floor": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "payment_factor": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "dependant_factor": (309.5, 0.5, (
                0.5, 0.5, 0.5, 0.5, 0.5)),
            "annuity_pp": (675483.7449786743, 6278.695958582584, (
                1390.5, 0.0, 2998.7401575197136, 0.0, 6278.695958582584)),
            "cum_annuity_all": (83162327.1694261, 344532.372489337, (
                7485.75, 50549.32330123719, 114810.63058007398, 206978.65127991664,
                344532.372489337)),
            "vp_balance": (1824099.7674394264, 41819.0, (
                41819.0, 0.0, 0.0, 0.0, 0.0)),
        },
    },
    12: {"rows": 620, "months": (0, 154, 309, 464, 619),
        "result_cf": {
            "pols_if": (620.0, 1.0, (
                1.0, 1.0, 1.0, 1.0, 1.0)),
            "annuity_payments": (337741.8724893371, 3139.347979291292, (
                0.0, 1020.9980642772006, 0.0, 0.0, 3139.347979291292)),
            "claims_vp": (43209.5, 43209.5, (
                43209.5, 0.0, 0.0, 0.0, 0.0)),
            "claims_prop": (695.25, 695.25, (
                695.25, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (3605.7316632536717, 11.288557998170772, (
                2.5, 3.564402217115448, 5.23444482413554, 7.686958695445089,
                11.288557998170772)),
            "liability_cf": (385252.3541525908, 43907.25, (
                43907.25, 1024.562466494316, 5.23444482413554, 7.686958695445089,
                3150.636537289463)),
            "net_cf": (-385252.3541525908, 43907.25, (
                -43907.25, -1024.562466494316, -5.23444482413554, -7.686958695445089,
                -3150.636537289463)),
        },
        "result_pols": {
            "pols_if": (620.0, 1.0, (
                1.0, 1.0, 1.0, 1.0, 1.0)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "lives_if_1": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "lives_if_2": (620.0, 1.0, (
                1.0, 1.0, 1.0, 1.0, 1.0)),
            "certain_floor": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "payment_factor": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "dependant_factor": (310.0, 0.5, (
                0.5, 0.5, 0.5, 0.5, 0.5)),
            "annuity_pp": (675483.7449786742, 6278.695958582584, (
                0.0, 2041.9961285544011, 0.0, 0.0, 6278.695958582584)),
            "cum_annuity_all": (83169117.66942608, 344532.372489337, (
                6790.5, 50549.32330123719, 113311.26050131413, 206978.65127991664,
                344532.372489337)),
            "vp_balance": (1867309.2674394264, 43209.5, (
                43209.5, 0.0, 0.0, 0.0, 0.0)),
        },
    },
    13: {"rows": 516, "months": (0, 128, 257, 386, 515),
        "result_cf": {
            "pols_if": (516.0, 1.0, (
                1.0, 1.0, 1.0, 1.0, 1.0)),
            "annuity_payments": (310184.64834836614, 3139.347979291292, (
                0.0, 1219.1250834018551, 1687.554233094613, 2335.96972813398,
                3139.347979291292)),
            "claims_vp": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_prop": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (2564.5167703377747, 8.651739733829555, (
                2.5, 3.3597909483603057, 4.650736429273743, 6.437706889212782,
                8.651739733829555)),
            "liability_cf": (312749.16511870397, 3147.9997190251215, (
                2.5, 1222.4848743502155, 1692.2049695238868, 2342.4074350231926,
                3147.9997190251215)),
            "net_cf": (-312749.16511870397, 3147.9997190251215, (
                -2.5, -1222.4848743502155, -1692.2049695238868, -2342.4074350231926,
                -3147.9997190251215)),
        },
        "result_pols": {
            "pols_if": (516.0, 1.0, (
                1.0, 1.0, 1.0, 1.0, 1.0)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "lives_if_1": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "lives_if_2": (516.0, 1.0, (
                1.0, 1.0, 1.0, 1.0, 1.0)),
            "certain_floor": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "payment_factor": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "dependant_factor": (258.0, 0.5, (
                0.5, 0.5, 0.5, 0.5, 0.5)),
            "annuity_pp": (620369.2966967323, 6278.695958582584, (
                0.0, 2438.2501668037103, 3375.108466189226, 4671.93945626796,
                6278.695958582584)),
            "cum_annuity_all": (95311351.5620034, 372089.5966303081, (
                61904.94828194194, 107159.86051142371, 169334.81368644178,
                254751.0742869686, 372089.5966303081)),
            "vp_balance": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
        },
    },
    14: {"rows": 612, "months": (0, 152, 305, 458, 611),
        "result_cf": {
            "pols_if": (377.36575233567964, 0.9997662830741708, (
                0.9997662830741708, 0.9705431692095241, 0.7692040918638099,
                0.22957704947886634, 0.0007810393830953411)),
            "annuity_payments": (243948.6743196447, 1872.0932658719873, (
                0.0, 1770.3609901502903, 1727.108445653783, 569.8530722170404,
                2.4519544090672767)),
            "claims_vp": (1692.8630618425448, 37.50554556494462, (
                37.50554556494462, 0.0, 0.0, 0.0, 0.0)),
            "claims_prop": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (1614.124946808446, 4.105889094157887, (
                2.499415707685427, 3.459406224136681, 4.026356377360398, 1.764749296766199,
                0.008560008130997358)),
            "liability_cf": (247255.6623282957, 1876.0586666946722, (
                40.00496127263005, 1773.820396374427, 1731.1348020311434, 571.6178215138067,
                2.460514417198274)),
            "net_cf": (-247255.6623282957, 1876.0586666946722, (
                -40.00496127263005, -1773.820396374427, -1731.1348020311434,
                -571.6178215138067, -2.460514417198274)),
        },
        "result_pols": {
            "pols_if": (377.36575233567964, 0.9997662830741708, (
                0.9997662830741708, 0.9705431692095241, 0.7692040918638099,
                0.22957704947886634, 0.0007810393830953411)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "lives_if_1": (252.67260331880402, 0.9783036659475713, (
                0.9783036659475713, 0.7634081986646054, 0.3826852716229489,
                0.029226443149435264, 0.0)),
            "lives_if_2": (335.4064433613744, 0.9892278149265049, (
                0.9892278149265049, 0.8754951328650746, 0.6261292700030612,
                0.20638243070754747, 0.0007810393830953411)),
            "certain_floor": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "payment_factor": (252.67260331880402, 0.9783036659475713, (
                0.9783036659475713, 0.7634081986646054, 0.3826852716229489,
                0.029226443149435264, 0.0)),
            "dependant_factor": (62.34657450843784, 0.19622849485870686, (
                0.010731308563299761, 0.10356748527245932, 0.1932594101204305,
                0.10017530316471554, 0.00039051969154767056)),
            "annuity_pp": (671312.2449786743, 6278.695958582584, (
                0.0, 2041.9961285544011, 2998.7401575197136, 4403.751019198756,
                6278.695958582584)),
            "cum_annuity_all": (101311263.7402125, 254846.7812328438, (
                10898.106913199103, 92462.97587600358, 185146.91590377095,
                246558.03682302352, 254846.7812328438)),
            "vp_balance": (1538319.2674394264, 39038.0, (
                39038.0, 0.0, 0.0, 0.0, 0.0)),
        },
    },
    15: {"rows": 606, "months": (0, 151, 302, 453, 605),
        "result_cf": {
            "pols_if": (371.3674906026247, 0.9996256019369548, (
                0.9996256019369548, 0.9679269241207766, 0.7619565922528438,
                0.2259540101204383, 0.0007810393830953411)),
            "annuity_payments": (241120.57005426823, 1872.093265871987, (
                0.0, 0.0, 1703.5071936108125, 0.0, 2.4519544090672762)),
            "claims_vp": (1472.4928143306734, 34.549483381891164, (
                34.549483381891164, 0.0, 0.0, 0.0, 0.0)),
            "claims_prop": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (1575.77996310231, 4.046506948669839, (
                2.499064004842387, 3.4500808743418325, 3.988419740533853,
                1.6863098474427094, 0.008560008130997358)),
            "liability_cf": (244168.8428317012, 1875.9431695833314, (
                37.04854738673355, 3.4500808743418325, 1707.4956133513463,
                1.6863098474427094, 2.4605144171982736)),
            "net_cf": (-244168.8428317012, 1875.9431695833314, (
                -37.04854738673355, -3.4500808743418325, -1707.4956133513463,
                -1.6863098474427094, -2.4605144171982736)),
        },
        "result_pols": {
            "pols_if": (371.3674906026247, 0.9996256019369548, (
                0.9996256019369548, 0.9679269241207766, 0.7619565922528438,
                0.2259540101204383, 0.0007810393830953411)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "lives_if_1": (246.81715953352483, 0.9725589604139413, (
                0.9725589604139413, 0.7534912390671861, 0.37419199290486443,
                0.028221456045297834, 0.0)),
            "lives_if_2": (329.4782593854673, 0.9863562726233098, (
                0.9863562726233098, 0.8698907261638265, 0.6196223042078005,
                0.20347491237093773, 0.0007810393830953411)),
            "certain_floor": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "payment_factor": (246.81715953352483, 0.9725589604139413, (
                0.9725589604139413, 0.7534912390671861, 0.37419199290486443,
                0.028221456045297834, 0.0)),
            "dependant_factor": (62.27516553454993, 0.1962284948587069, (
                0.013533320761506777, 0.1072178425267953, 0.1938822996739897,
                0.09886627703757024, 0.00039051969154767056)),
            "annuity_pp": (668447.8149786742, 6278.695958582583, (
                0.0, 0.0, 2998.7401575197127, 0.0, 6278.695958582583)),
            "cum_annuity_all": (101238801.67720452, 254846.78123284376, (
                13726.211178575504, 94225.89913204522, 186850.42309738172,
                246558.0368230235, 254846.78123284376)),
            "vp_balance": (1311252.3424394268, 36173.57, (
                36173.57, 0.0, 0.0, 0.0, 0.0)),
        },
    },
    16: {"rows": 535, "months": (0, 133, 267, 400, 534),
        "result_cf": {
            "pols_if": (300.5429140613909, 0.9937851467769392, (
                0.9937851467769392, 0.9273331206979856, 0.6604859223003041,
                0.1667120045563878, 0.0007810393830953411)),
            "annuity_payments": (206463.88648203548, 1872.0932658719873, (
                1610.2426629636404, 0.0, 1525.004334156141, 0.0, 2.4519544090672767)),
            "claims_vp": (0.3801586523959143, 0.3801586523959143, (
                0.3801586523959143, 0.0, 0.0, 0.0, 0.0)),
            "claims_prop": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (1162.903807141328, 3.397131353412798, (
                2.484462866942348, 3.2091147877868806, 3.1638983180604257,
                1.1054403108545443, 0.007168872046794359)),
            "liability_cf": (207627.1704478292, 1875.3174996199864, (
                1613.1072844829787, 3.2091147877868806, 1528.1682324742014,
                1.1054403108545443, 2.459123281114071)),
            "net_cf": (-207627.1704478292, 1875.3174996199864, (
                -1613.1072844829787, -3.2091147877868806, -1528.1682324742014,
                -1.1054403108545443, -2.459123281114071)),
        },
        "result_pols": {
            "pols_if": (300.5429140613909, 0.9937851467769392, (
                0.9937851467769392, 0.9273331206979856, 0.6604859223003041,
                0.1667120045563878, 0.0007810393830953411)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "lives_if_1": (180.48852419054907, 0.8893858571190014, (
                0.8893858571190014, 0.6358644501754204, 0.27030162418369735,
                0.01423036345127105, 0.0)),
            "lives_if_2": (260.8288687522316, 0.9438150216492038, (
                0.9438150216492038, 0.8004400302661432, 0.5347199761546864,
                0.15468283405336883, 0.0007810393830953411)),
            "certain_floor": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "payment_factor": (180.48852419054907, 0.8893858571190014, (
                0.8893858571190014, 0.6358644501754204, 0.27030162418369735,
                0.01423036345127105, 0.0)),
            "dependant_factor": (60.027194935420916, 0.1962284948587069, (
                0.0521996448289689, 0.1457343352612826, 0.19509214905830338,
                0.07624082055255837, 0.00039051969154767056)),
            "annuity_pp": (632545.4907190301, 6278.695958582584, (
                1710.139609873282, 0.0, 3276.8043361060445, 0.0, 6278.695958582584)),
            "cum_annuity_all": (99041927.52623053, 254846.7812328438, (
                49993.13741377194, 127058.02684473725, 206289.4610033556, 249428.0855570811,
                254846.7812328438)),
            "vp_balance": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
        },
    },
    17: {"rows": 466, "months": (0, 116, 232, 348, 465),
        "result_cf": {
            "pols_if": (466.0, 1.0, (
                1.0, 1.0, 1.0, 1.0, 1.0)),
            "annuity_payments": (295004.04725237715, 3139.347979291292, (
                1020.9980642772006, 0.0, 0.0, 2406.0488199779993, 3139.347979291292)),
            "claims_vp": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_prop": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (2151.6530651324842, 7.686958695445089, (
                2.5, 3.2619329595731124, 4.383765132692754, 5.891413765023453,
                7.686958695445089)),
            "liability_cf": (297155.70031750965, 3147.034937986737, (
                1023.4980642772006, 3.2619329595731124, 4.383765132692754,
                2411.940233743023, 3147.034937986737)),
            "net_cf": (-297155.70031750965, 3147.034937986737, (
                -1023.4980642772006, -3.2619329595731124, -4.383765132692754,
                -2411.940233743023, -3147.034937986737)),
        },
        "result_pols": {
            "pols_if": (466.0, 1.0, (
                1.0, 1.0, 1.0, 1.0, 1.0)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "lives_if_1": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "lives_if_2": (466.0, 1.0, (
                1.0, 1.0, 1.0, 1.0, 1.0)),
            "certain_floor": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "payment_factor": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "dependant_factor": (233.0, 0.5, (
                0.5, 0.5, 0.5, 0.5, 0.5)),
            "annuity_pp": (590008.0945047543, 6278.695958582584, (
                2041.9961285544011, 0.0, 0.0, 4812.097639955999, 6278.695958582584)),
            "cum_annuity_all": (78994061.51036489, 344532.372489337, (
                50549.32330123719, 95014.54868642578, 155686.07402378996,
                236607.80815037756, 344532.372489337)),
            "vp_balance": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
        },
    },
    18: {"rows": 25, "months": (0, 6, 12, 18, 24),
        "result_cf": {
            "pols_if": (4.479177739724404e-10, 4.479177739724404e-10, (
                4.479177739724404e-10, 0.0, 0.0, 0.0, 0.0)),
            "annuity_payments": (2.948792011985233e-07, 2.948792011985233e-07, (
                2.948792011985233e-07, 0.0, 0.0, 0.0, 0.0)),
            "claims_vp": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_prop": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (1.1197944349311012e-09, 1.1197944349311012e-09, (
                1.1197944349311012e-09, 0.0, 0.0, 0.0, 0.0)),
            "liability_cf": (2.959989956334544e-07, 2.959989956334544e-07, (
                2.959989956334544e-07, 0.0, 0.0, 0.0, 0.0)),
            "net_cf": (-2.959989956334544e-07, 2.959989956334544e-07, (
                -2.959989956334544e-07, -0.0, -0.0, -0.0, -0.0)),
        },
        "result_pols": {
            "pols_if": (4.479177739724404e-10, 4.479177739724404e-10, (
                4.479177739724404e-10, 0.0, 0.0, 0.0, 0.0)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "lives_if_1": (4.479177739724404e-10, 4.479177739724404e-10, (
                4.479177739724404e-10, 0.0, 0.0, 0.0, 0.0)),
            "lives_if_2": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "certain_floor": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "payment_factor": (4.479177739724404e-10, 4.479177739724404e-10, (
                4.479177739724404e-10, 0.0, 0.0, 0.0, 0.0)),
            "dependant_factor": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "annuity_pp": (16458.333333333332, 658.3333333333334, (
                658.3333333333334, 658.3333333333334, 658.3333333333334, 658.3333333333334,
                658.3333333333334)),
            "cum_annuity_all": (4008333.1276354156, 160333.32510541662, (
                160333.32510541662, 160333.32510541662, 160333.32510541662,
                160333.32510541662, 160333.32510541662)),
            "vp_balance": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
        },
    },
    19: {"rows": 1, "months": (0,),
        "result_cf": {
            "pols_if": (0.0007810393830953411, 0.0007810393830953411, (
                0.0007810393830953411,)),
            "annuity_payments": (2.4519544090672767, 2.4519544090672767, (
                2.4519544090672767,)),
            "claims_vp": (0.0, 0.0, (
                0.0,)),
            "claims_prop": (0.0, 0.0, (
                0.0,)),
            "expenses": (0.0019525984577383527, 0.0019525984577383527, (
                0.0019525984577383527,)),
            "liability_cf": (2.453907007525015, 2.453907007525015, (
                2.453907007525015,)),
            "net_cf": (-2.453907007525015, 2.453907007525015, (
                -2.453907007525015,)),
        },
        "result_pols": {
            "pols_if": (0.0007810393830953411, 0.0007810393830953411, (
                0.0007810393830953411,)),
            "pols_new_biz": (0.0, 0.0, (
                0.0,)),
            "lives_if_1": (0.0, 0.0, (
                0.0,)),
            "lives_if_2": (0.0007810393830953411, 0.0007810393830953411, (
                0.0007810393830953411,)),
            "certain_floor": (0.0, 0.0, (
                0.0,)),
            "payment_factor": (0.0, 0.0, (
                0.0,)),
            "dependant_factor": (0.00039051969154767056, 0.00039051969154767056, (
                0.00039051969154767056,)),
            "annuity_pp": (6278.695958582584, 6278.695958582584, (
                6278.695958582584,)),
            "cum_annuity_all": (254846.7812328438, 254846.7812328438, (
                254846.7812328438,)),
            "vp_balance": (0.0, 0.0, (
                0.0,)),
        },
    },
    20: {"rows": 649, "months": (0, 162, 324, 486, 648),
        "result_cf": {
            "pols_if": (401.3639797203242, 0.9999996527930258, (
                0.0, 0.9820012940344517, 0.8101240414937017, 0.26213425372567845,
                0.0007810393830953411)),
            "annuity_payments": (254846.78123284376, 1872.093265871987, (
                0.0, 1728.166399569887, 1758.3944645371303, 643.6721837590176,
                2.451954409067276)),
            "claims_vp": (2629.202964676305, 41.92133577406443, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_prop": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (1830.9922729768807, 4.498799066295056, (
                0.0, 3.6052550173566384, 4.498799066295056, 2.1377296055765953,
                0.009634364565109162)),
            "liability_cf": (259306.9764704969, 1876.4263664167568, (
                0.0, 1731.7716545872438, 1762.8932636034253, 645.8099133645942,
                2.461588773632385)),
            "net_cf": (-259306.9764704969, 1876.4263664167568, (
                -0.0, -1731.7716545872438, -1762.8932636034253, -645.8099133645942,
                -2.461588773632385)),
        },
        "result_pols": {
            "pols_if": (401.3639797203242, 0.9999996527930258, (
                0.0, 0.9820012940344517, 0.8101240414937017, 0.26213425372567845,
                0.0007810393830953411)),
            "pols_new_biz": (1.0, 1.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "lives_if_1": (276.4174277088396, 0.9991615732845187, (
                0.0, 0.8137041019416205, 0.43405223883490035, 0.03896467143218165, 0.0)),
            "lives_if_2": (359.27999007317993, 0.9995858827400101, (
                0.0, 0.903386461252582, 0.664499143674663, 0.23221787551356202,
                0.0007810393830953411)),
            "certain_floor": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "payment_factor": (276.4174277088396, 0.9991615732845187, (
                0.0, 0.8137041019416205, 0.43405223883490035, 0.03896467143218165, 0.0)),
            "dependant_factor": (62.473276005742306, 0.1962284948587069, (
                0.0, 0.08414859604641563, 0.18803590132940068, 0.11158479114674841,
                0.00039051969154767056)),
            "annuity_pp": (682274.2449786741, 6278.6959585825825, (
                0.0, 1924.777197242342, 2826.6002050331917, 4275.486426406558,
                6278.6959585825825)),
            "cum_annuity_all": (101435853.36923328, 254846.78123284376, (
                0.0, 76688.8507383215, 174644.54234790738, 244790.84904760018,
                254846.78123284376)),
            "vp_balance": (2613228.2674394264, 50000.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
        },
    },
    21: {"rows": 576, "months": (0, 143, 287, 431, 575),
        "result_cf": {
            "pols_if": (341.39530530657316, 0.9982726644687168, (
                0.9982726644687168, 0.9541902609342185, 0.7231486040089359,
                0.19909813250408087, 0.0007810393830953411)),
            "annuity_payments": (186078.45896652207, 1534.2032027192527, (
                0.0, 1475.0203851954998, 1334.3994284938626, 397.7560109603246,
                2.0094064627492965)),
            "claims_vp": (768.6874189257287, 26.926226118640038, (
                26.926226118640038, 0.0, 0.0, 0.0, 0.0)),
            "claims_prop": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (1392.365114968722, 3.7574701587476893, (
                2.495681661171792, 3.302056195751356, 3.567990826030178, 1.4005868994718011,
                0.007833620045077459)),
            "liability_cf": (188239.51150041656, 1537.8321062081247, (
                29.42190777981183, 1478.3224413912512, 1337.9674193198928,
                399.1565978597964, 2.0172400827943737)),
            "net_cf": (-188239.51150041656, 1537.8321062081247, (
                -29.42190777981183, -1478.3224413912512, -1337.9674193198928,
                -399.1565978597964, -2.0172400827943737)),
        },
        "result_pols": {
            "pols_if": (341.39530530657316, 0.9982726644687168, (
                0.9982726644687168, 0.9541902609342185, 0.7231486040089359,
                0.19909813250408087, 0.0007810393830953411)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "lives_if_1": (218.0810337613445, 0.9412898611586333, (
                0.9412898611586333, 0.7074738898102813, 0.3312003675891318,
                0.021330794451386068, 0.0)),
            "lives_if_2": (300.1092851975895, 0.9705785820750582, (
                0.9705785820750582, 0.8433994865071313, 0.5860473263224161,
                0.1816419041743972, 0.0007810393830953411)),
            "certain_floor": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "payment_factor": (218.0810337613445, 0.9412898611586333, (
                0.9412898611586333, 0.7074738898102813, 0.3312003675891318,
                0.021330794451386068, 0.0)),
            "dependant_factor": (61.65713577261436, 0.1962284948587069, (
                0.02849140165504173, 0.12335818556196865, 0.19597411820990202,
                0.0888836690263474, 0.00039051969154767056)),
            "annuity_pp": (536022.8454659935, 5145.467709415132, (
                0.0, 1775.3532018303756, 2531.229155506881, 3608.9275255663965,
                5145.467709415132)),
            "cum_annuity_all": (84662600.19064893, 212683.78021733015, (
                26605.321250808007, 92882.42206195297, 163798.7670174127, 207150.6914719923,
                212683.78021733015)),
            "vp_balance": (596824.0824723833, 23000.0, (
                23000.0, 0.0, 0.0, 0.0, 0.0)),
        },
    },
    22: {"rows": 594, "months": (0, 148, 296, 444, 593),
        "result_cf": {
            "pols_if": (359.3739923615178, 0.9992270508833735, (
                0.9992270508833735, 0.9627649585470677, 0.7467965602388613,
                0.215450278842151, 0.0007810393830953411)),
            "annuity_payments": (249386.79353412974, 1983.2785013137402, (
                0.0, 0.0, 1805.7084765417555, 0.0, 2.5975780984605548)),
            "claims_vp": (975.5242306303214, 30.4667179195464, (
                30.4667179195464, 0.0, 0.0, 0.0, 0.0)),
            "claims_prop": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (1500.773026698585, 3.928647522980426, (
                2.498067627208434, 3.4316815528062303, 3.7952091159461485,
                1.607919800370623, 0.008310687505822676)),
            "liability_cf": (251863.0907914586, 1987.0162719072785, (
                32.96478554675483, 3.4316815528062303, 1809.5036856577017,
                1.607919800370623, 2.6058887859663775)),
            "net_cf": (-251863.0907914586, 1987.0162719072785, (
                -32.96478554675483, -3.4316815528062303, -1809.5036856577017,
                -1.607919800370623, -2.6058887859663775)),
        },
        "result_pols": {
            "pols_if": (359.3739923615178, 0.9992270508833735, (
                0.9992270508833735, 0.9627649585470677, 0.7467965602388613,
                0.215450278842151, 0.0007810393830953411)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "lives_if_1": (235.2108467504088, 0.9606302650695717, (
                0.9606302650695717, 0.7351330733479711, 0.35688897070126213,
                0.02540912864397729, 0.0)),
            "lives_if_2": (317.6742815340567, 0.9803669209865787, (
                0.9803669209865787, 0.8594198153631686, 0.6062834748189014,
                0.19499582417979655, 0.0007810393830953411)),
            "certain_floor": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "payment_factor": (235.2108467504088, 0.9606302650695717, (
                0.9606302650695717, 0.7351330733479711, 0.35688897070126213,
                0.02540912864397729, 0.0)),
            "dependant_factor": (62.08157280555451, 0.1962284948587069, (
                0.019298392906900864, 0.11381594259954832, 0.19495379476879957,
                0.09502057509908686, 0.00039051969154767056)),
            "annuity_pp": (701987.3693830438, 6651.593132643529, (
                0.0, 0.0, 3272.1430623515494, 0.0, 6651.593132643529)),
            "cum_annuity_all": (106655349.13359152, 269328.2269246159, (
                19941.43339048627, 104886.36623117932, 200879.1996505286,
                261119.18507579862, 269328.2269246159)),
            "vp_balance": (833236.1332074542, 29850.9125, (
                29850.9125, 0.0, 0.0, 0.0, 0.0)),
        },
    },
}
# END generated fingerprint: PA_UK_SEC
