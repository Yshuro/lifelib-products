"""In-force tests for IP_UK_SEC: the splice, future business, counts, regeneration.

``IP_UK_SEC`` is ``IP_UK_S`` taught to run in force at a valuation date
(UKLIB-SEC-PLAN.md, milestone M7, after USLIB-SEC-PLAN.md's Phase 1).  It runs on two
clocks: ``t`` counts months from the valuation date, the same month for every model point,
and ``duration_mth(t)`` counts the months the policy has been in force,
``duration_mth_init() + t``; and on the claim duration ``z``, a cohort index the
termination rates read.  A model point may be a policy already in force at the valuation
date, in any month of its policy year, one issued at it, or one to be issued after it, as
in ``basiclife/BasicTerm_SE``.  A policy in force opens with its count, the lives in health
and in claim together, and with three columns of state beside it and a vector of claim
cohorts, each measured at the valuation instant, before month 0's events, recoveries
already returned to health: the healthy share of the count, the share in claim at each
claim duration, read from a sparse companion, ``inforce_cohorts_sec.csv``, and the benefit
and premium entering month 0.

The worked example is not restated here.  On a point issued at the valuation date the two
clocks coincide and the model is ``IP_UK_S``, and ``test_model_conventions_uk.py`` asserts
that cell by cell on the twins of S's four new-business points (T1), so every golden of
``test_income_protection_uk.py`` on them holds on this model with no number copied.  The
twins of S's three claims in payment, the claims-in-payment worked example among them, are
on policy clocks of whole years since issue, ``duration_mth = 12n``, and are splice cases,
which this module compares with S cell by cell.  The conventions also hold the SEC family's
other rules: every frame opens at ``t = 0``, ``pols_if`` is the ``BEF_DECR`` count,
``BEF_DECR`` is ``BEF_NB`` plus the month's new business, new business enters once, and
nothing happens before issue.  This module holds the rest of the plan's tests (its §5) and
the product's own facts:

* T2, the splice: an S point restated in force at month ``d``, opened with the state S
  carries into ``d``, its claim cohorts among it, continues S's projection from ``d`` on,
  in every cell of S's, the cohort vector included, and in its reports.  The months
  straddle the product's events: the anniversaries, the lapse table's last year, the
  inception table's pivot ages, the claim-duration years, the first month and the last two.
  Every assumption that ships idle is on, under four sets of References: the escalation
  lapse shock at an RPI of 5%, beside the cycle overlay, the active-life mortality factor,
  the amount-payable ratio and the claim severity, each moved off its neutral 1 and off
  each other; the escalation cap at 12%; the RPI's floor at -2%; and the recovery rate's
  bound at an overlay of 0.35.  Three variants of S's points, in a copy of S's table, add
  an active cell on the exit basis, the youngest entry ages below the inception table's
  first pivot, and the oldest entry age to the latest expiry, past its last.  The twins of
  S's two claims on the exit basis are splice cases, on their policy clocks; the claim on
  the active-lives basis, whose recovered lives S lapses at first-year rates, is spliced
  under a flat lapse table by a test of its own.
* T3, future new business: a point issued ``k`` months after the valuation date is S's
  projection ``k`` months on, with zeros before issue and no table read there.
* D11's R1 and R2, and D3's and D5's chains: on the splice's grid no cell is called at a
  negative month, none on the books reads a month before them, and none reads beyond
  ``t + 1``; on the committed points no recursion runs backward over the frame; the policy
  clock is a closed form; and each chain, called cold, runs one cell a month back to
  ``t_entry()``, at the contract's longest cover, on each shape.
* T4, the count algebra: the counts roll forward through new business, the transitions
  between the states and the exits, ``result_pols`` holds S's counts with the new business
  beside them, multiplying ``policy_count`` by 2.5 with every assumption that ships idle
  switched on multiplies every flow and every counted cell, the cohort vector's every
  element among them, by 2.5 and moves no per-policy value, a point restated a month on
  continues its own flows, and the roll-forward and the population identity, whose
  tolerances scale with the policies on the books, close on ten million policies.
* T5, validation: each malformed row of the table and of the companion is refused as it is
  read, naming its point or its line, by its label on an extract labelled otherwise; each
  assumption table, malformed or holding a value that is not a number in its range, is
  refused before a value of it is read, naming its lines; the future horizon is a
  Reference that bounds future business; a point past its policy end date, one the
  contract does not issue and one that reads a Reference off its domain are refused by the
  frame, each domain at both its edges, NaN and the infinities included; a value past the
  floats is refused in the cell where it first is; the edges of the interface are
  accepted, the shares' tolerance pinned from both sides; and so is every state
  ``IP_UK_S`` reaches, on each set of inputs on which those states differ.
* T6, regeneration: the committed ``model_point_table_sec.csv`` and
  ``inforce_cohorts_sec.csv`` are what the generator makes of ``IP_UK_S`` and its table as
  they stand.
* Then the product's own facts: the two clocks on the shipped points; the twins of S's
  claims on their policy clocks, and the claim on the active-lives basis under a flat
  lapse table, S's restarted clock recorded where the table is not flat; the committed rows
  continuing their S points, those read under an RPI of their own continuing S under it;
  each history column read rather than recomputed (UKLIB-SEC-PLAN.md K14), the healthy
  share, the claim cohorts, the benefit and the premium; an anniversary at the valuation
  date as the projection's first event; the cumulative counts restarting on the books; the
  present value and the annuity factor on the valuation clock; expense inflation on it; the
  escalation's floor, cap and lapse shock; the caps on mortality and inception and the
  lapse rate's bound; a NaN that reaches a bound and a check whose residual is NaN; the
  values outside cover; the block; an in-force extract; the runner; the cells' defaulted
  parameters; the static check the C step will make; the docstrings; the shared input
  tables; and what the default grid reaches.
* C2, the fingerprint: every committed point computes what the model computed when its E
  step ended, frozen at the end of this module before its C step changed anything
  (USLIB-SEC-PLAN.md §5.4).

SEC month ``t`` is S month ``t + source_mth`` throughout, the direction in which
``uk_sec_support`` takes its ``t_offset``: ``d`` for a point restated at S month ``d``,
``-k`` for one issued ``k`` months on, and 0 for the twin of an S claim in payment, which S
opens at the valuation date.

**The core grid and the full one** (UKLIB-SEC-PLAN.md U6).  T2 and T3 over every S point
at every month, under every set, run by default on a core, chosen so that between them they
reach every branch, every opening-state column, every kind of valuation month and both
sides of every ``min`` and ``max`` the full grid reaches, which
``test_the_core_grid_reaches_every_branch`` asserts.  The other cases, and the rules
test's scan of their rows, carry the ``sec_full`` marker and are skipped, with the reason
shown, unless ``UKLIB_SEC_FULL=1`` is set.  So do the slower tests' other cases
(``GRIDS``): over the committed points, the default run takes five among which every flow
and counted cell is nonzero (``CORE_POINTS``), and the full grid the rest; the cold
chains run on one shape by default and on the other three with the full grid; and so on,
each test's docstring saying which.  They are never dropped: one leg of the CI matrix sets
it, and ``UKLIB_SEC_FULL=1 python -m pytest -m sec_full
lifelib/libraries/uklib/tests/test_income_protection_uk_sec.py`` runs them alone.  Each
splice row is released once it has been read (``_release``), as ``run_sec.py --block``
releases its points.

Every test keeps four rules.  Each model is read under a name of its own and closed:
``conftest.income_protection`` reads S under its default name, and reading a model under a
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

SEC, TWIN = "IP_UK_SEC", "IP_UK_S"
TABLE, COHORTS = "model_point_table_sec.csv", "inforce_cohorts_sec.csv"
SPEC = SEC_SPECS[SEC]

# S's seven points: the active-lives anchor cell, a 35-year-old man, occupation class 1, a
# 26-week deferred period, £2,000 a month to 65 with RPI escalation (1); the
# claims-in-payment worked example, the same cell level and in claim from duration 0, on
# the exit basis (2); the level-cover anchor cell (3); a 42-year-old woman, class 3, 13
# weeks, £1,500 a month to 60 with RPI escalation (4); a claim at duration 30 months at 50,
# to 65, on the exit basis (5); a 55-year-old man, class 2, 52 weeks, £3,000 a month to 65
# with RPI escalation (6); and the worked example's claim on the active-lives basis, its
# recovered lives back in health (7).
S_POINTS = (1, 2, 3, 4, 5, 6, 7)
NEW_BUSINESS = (1, 3, 4, 6)
IN_CLAIM = (2, 5, 7)

# T2's months (UKLIB-SEC-PLAN.md §6.3).  On the new-business points: the second month; 11 to
# 13 about the first anniversary, where the benefit and the premium first escalate and the
# lapse table moves to its second year; 59 to 61 about the lapse table's last year, policy
# year 6; on the anchor cell the inception table's pivot ages, 40 at 60, 45 at 120, 50 at
# 180, 55 at 240, 60 at 300 and its last pivot, 64, at 348, past which it extrapolates;
# on the female cell 45 at 36, 50 at 96 and 55 at 156; on the older male cell its last
# pivot at 108; and the last two months of each frame.  On the claims on the exit basis the
# claim-duration years the termination table changes at: the claim from duration 0 at 11
# to 13, 23 to 25 and 47 to 49, about the starts of its years 2, 3 and 5, the last row; and
# the claim from duration 30 at 5 and 6 and 17 and 18, about the starts of its years 4 and
# 5; and the first and last months of each.
SPLICE_MTHS = {
    1: (1, 11, 12, 13, 59, 60, 61, 120, 180, 240, 300, 348, 358, 359),
    2: (1, 11, 12, 13, 23, 24, 25, 47, 48, 49, 358, 359),
    3: (1, 11, 12, 13, 59, 60, 61, 358, 359),
    4: (1, 11, 12, 13, 36, 59, 60, 61, 96, 156, 214, 215),
    5: (1, 5, 6, 17, 18, 178, 179),
    6: (1, 11, 12, 13, 59, 60, 61, 108, 118, 119),
}

# T3's months: issued one month on, which puts the policy anniversaries a month off the
# valuation years; twelve, which puts them back on; and the horizon, 120, the latest the
# table admits.  Each variant is issued 13 months on, more than a year after the valuation
# date and off its anniversaries (USLIB-SEC-PLAN.md §7.1, *Record — M14*, *Splice grid*).
FUTURE_MTHS = (1, 12, 120)

# Three more S points, in the splice's copy of S's table and never in the committed one,
# each one of S's points changed so as to reach what S's own points cannot:
#
# 8, S point 1 on the exit basis: an active cell whose recovered lives leave the model,
#   S's exit basis on lives that started healthy;
# 9, S point 3 at 22, to 55, occupation class 4 and a 4-week deferred period: the youngest
#   attained ages, below the inception table's first pivot, 30, from which it
#   extrapolates, a class and a deferred period no S point holds, and the expiry age 55;
# 10, S point 4 as a man of 59, occupation class 2 and an 8-week deferred period, to 70:
#   the latest entry age the product issues at, the latest expiry, attained ages past the
#   inception table's last pivot, 64, and the mortality table read to 69.
#
# Each variant is (the S point it changes, the columns it changes); the policy_id keeps
# the generated ids apart.
VARIANTS = {
    8: (1, {"policy_id": "IP-900008", "recovery_basis": "exit"}),
    9: (3, {"policy_id": "IP-900009", "occ_class": 4, "deferred_weeks": 4, "entry_age": 22,
            "expiry_age": 55}),
    10: (4, {"policy_id": "IP-900010", "sex": "M", "occ_class": 2, "deferred_weeks": 8,
             "entry_age": 59, "expiry_age": 70}),
}
VARIANT_MTHS = {8: (12, 60, 120), 9: (1, 12, 95, 96, 395), 10: (1, 11, 12, 13, 60, 131)}
LATE_FUTURES = tuple((p, 13) for p in VARIANTS)


def _s_table():
    """S's committed table, indexed by point_id."""
    return pd.read_csv(model_path(TWIN).parent / "model_point_table.csv",
                       index_col="point_id")


def _s_table_with_variants(points=None):
    """S's committed table with the :data:`VARIANTS` appended, under their own point_ids;
    or, given ``points``, those of them alone."""
    table = _s_table()
    rows = []
    for point_id, (base, changes) in VARIANTS.items():
        row = table.loc[[base]].assign(**changes)
        row.index = pd.Index([point_id], name="point_id")
        rows.append(row)
    table = pd.concat([table, *rows])
    return table if points is None else table.loc[list(points)]


# The months from issue to the policy end date of each S point and variant, 12 times the
# years from its entry age to its expiry age; S's frames, but on its claims, which S opens
# at the valuation date with the clock restarted.
COVER = {p: 12 * (int(row["expiry_age"]) - int(row["entry_age"]))
         for p, row in _s_table_with_variants().iterrows()}

# The committed rows the generator reads from S under References of their own (the spec's
# derived_refs), by (S policy, month), with those References.
UNDER_REFS = {(_s_table().at[p, "policy_id"], d): refs
              for (p, d), refs in SPEC.derived_refs.items()}

# The sets of References T2 and T3 run under, each set in S and SEC alike before either
# evaluates anything.  Every set holds the valuation clock's one input at 0: expense
# inflation, which S runs from its frame's start and SEC from the valuation date, so at the
# shipped 3% the expenses of a point opened at d differ by the inflation of the policy years
# before d, by design, and at 0 both factors are 1; the clock is asserted on its own, at
# the shipped rate.  Discounting is no cash flow, and its clock has a test of its own.
# Every assumption that ships idle is on in the main set: the escalation lapse shock, which
# the shipped RPI of 3% leaves at 1, at an RPI of 5%, where premiums grow 7.5% a year, past
# the threshold of 5%; and the four factors that ship at a neutral 1, each moved off it and
# off each other, so that a formula that read one for another would part from S: the cycle
# overlay on inception and recovery at 1.25, the active-life mortality factor at 1.1, the
# amount-payable ratio at 0.9 and the claim severity at 0.95.  The RPI is a flat Reference,
# the same on either clock.  Three more sets each reach a bound the main one does not: the
# escalation cap at an RPI of 12%, the RPI's floor at -2%, and the recovery rate's bound at
# an overlay of 0.35, under which the first claim-duration year's recovery rate, 0.4 /
# 0.35, binds at 1.
MAIN = {"inflation_rate": 0.0, "rpi_rate": 0.05, "cycle_factor": 1.25,
        "mort_active_factor": 1.1, "ap_ratio": 0.9, "claim_severity": 0.95}
SPLICE_SETS = {
    "main": MAIN,
    "rpi_cap": {**MAIN, "rpi_rate": 0.12},
    "rpi_floor": {**MAIN, "rpi_rate": -0.02},
    "recovery": {**MAIN, "cycle_factor": 0.35},
}

# The cases of the three sets beyond the main one, each with the points it holds: the RPI
# points about their first anniversary and later, under the cap and the floor, and under the
# recovery bound the anchor cell, whose claims of the first year all recover in the month,
# on the active-lives basis and on the exit basis.
SET_MTHS = {
    "rpi_cap": {1: (11, 12, 13, 60), 4: (12, 13), 6: (12, 61)},
    "rpi_floor": {1: (12, 13), 4: (12,), 6: (60,)},
    "recovery": {1: (12, 60), 8: (60,)},
}
SET_FUTURES = {"rpi_cap": ((1, 1), (4, 13)), "rpi_floor": ((1, 1),), "recovery": ()}

# T2's cases, as (set, row_kind, S point, source_mth): each S point restated in force at
# each of its months, each variant at its own, and the other sets' cases; the twins of S's
# two claims on the exit basis, which S opens in force at the valuation date.  T3's cases,
# as (set, S point, k).
SPLICES = (tuple(("main", "derived", p, d) for p, mths in SPLICE_MTHS.items() for d in mths)
           + tuple(("main", "derived", p, d) for p, mths in VARIANT_MTHS.items()
                   for d in mths)
           + tuple((rates, "derived", p, d) for rates, points in SET_MTHS.items()
                   for p, mths in points.items() for d in mths))
IN_FORCE_TWINS = (("main", "twin", 2, 0), ("main", "twin", 5, 0))
FUTURES = (tuple(("main", p, k) for p in NEW_BUSINESS for k in FUTURE_MTHS)
           + tuple(("main", p, k) for p, k in LATE_FUTURES)
           + tuple((rates, p, k) for rates, cases in SET_FUTURES.items() for p, k in cases))

# The default run's cases (the module docstring), each with what it is there for.  The rest
# of SPLICES, IN_FORCE_TWINS and FUTURES run with UKLIB_SEC_FULL=1.
CORE_SPLICES = {
    ("main", "derived", 1, 12): "the anchor cell on its first anniversary, escalating at 0",
    ("main", "derived", 1, 13): "the anchor cell a month past its first anniversary",
    ("main", "derived", 1, 60): "the anchor cell in the lapse table's last year, at a pivot",
    ("main", "derived", 1, 348): "the anchor cell at its last pivot, cohorts 348 long",
    ("main", "derived", 1, 359): "the anchor cell in its last month",
    ("main", "derived", 2, 12): "the claim from duration 0 in its second claim year",
    ("main", "derived", 2, 48): "the claim from duration 0 in the termination's last row",
    ("main", "derived", 3, 1): "the level cell a month after issue, one cohort",
    ("main", "derived", 3, 61): "the level cell past the lapse table's last year",
    ("main", "derived", 4, 11): "the female cell in the month before its anniversary",
    ("main", "derived", 4, 215): "the female cell in its last month",
    ("main", "derived", 5, 6): "the claim from duration 30 in its fourth claim year",
    ("main", "derived", 5, 18): "the claim from duration 30 in its fifth",
    ("main", "derived", 6, 108): "the older male cell at its last pivot",
    ("main", "derived", 6, 118): "the older male cell in its last two months",
    ("main", "derived", 8, 60): "an active cell on the exit basis, its recoveries leaving",
    ("main", "derived", 9, 95): "the youngest cell below the first pivot, then at it",
    ("main", "derived", 10, 60): "the oldest cell past the last pivot",
    ("main", "twin", 2, 0): "the claims-in-payment worked example on its policy clock",
    ("main", "twin", 5, 0): "the claim from duration 30 on its policy clock",
    ("rpi_cap", "derived", 1, 12): "the escalation cap at the valuation anniversary",
    ("rpi_cap", "derived", 4, 13): "the escalation cap a month past an anniversary",
    ("rpi_floor", "derived", 1, 12): "the RPI's floor at the valuation anniversary",
    ("recovery", "derived", 1, 12): "the recovery rate's bound, on the active-lives basis",
    ("recovery", "derived", 8, 60): "the recovery rate's bound, on the exit basis",
}
CORE_FUTURES = {
    ("main", 1, 1): "issued a month off the valuation anniversaries",
    ("main", 3, 12): "the level cell a year on",
    ("main", 4, 120): "the female cell at the horizon",
    ("main", 8, 13): "the exit basis, more than a year on",
    ("rpi_cap", 4, 13): "the escalation cap, more than a year on",
}

SEC_FULL = os.environ.get("UKLIB_SEC_FULL") == "1"
FULL_ONLY = (pytest.mark.sec_full,
             pytest.mark.skipif(not SEC_FULL, reason="the full splice grid runs with "
                                "UKLIB_SEC_FULL=1 (UKLIB-SEC-PLAN.md U6)"))

# The tests that run over every committed point run the core's by default and the rest on
# the full grid (GRIDS): the anchor cell's twin, the anchor cell in force at 60, the claim
# on the exit basis at 24, the claim on the active-lives basis at 12 and the female cell
# issued 13 months on, by label, among which every flow and every counted cell is nonzero.
CORE_POINTS = (1, 9, 11, 13, 17)
GRIDS = [pytest.param("core", id="core"), pytest.param("full", id="full", marks=FULL_ONLY)]


def _on_grid(grid, label):
    """Whether committed point ``label`` is one the ``grid`` case of a test runs on."""
    return (label in CORE_POINTS) == (grid == "core")


# The cells T2 and T3 skip beyond T1's: the spec's exempt, proj_len, and the three
# cumulative counts.  proj_len counts from the valuation date on SEC and from issue on S,
# so it differs by d, or by -k, by design; frame_mismatches asserts what it must get right,
# that both frames end at the same instant.  The cumulative counts restart at t_entry() on
# SEC, on the count on the books, where S counts from its frame's start: the splice
# compares their increments instead (_cumulative_faults).
CUMULATIVE = ("pols_dead_cum", "pols_lapse_cum", "pols_exit_cum")
SPLICE_EXEMPT = TWIN_EXEMPT_DEFAULT | SPEC.exempt | {"proj_len", *CUMULATIVE}
FUTURE_EXEMPT = SPLICE_EXEMPT

# What else differs on a row of an S claim, which S opens with its policy clock restarted
# at the valuation date and the SEC twin n whole years after issue: the issue age, n years
# less; the policy clock, 12n months on, and so the policy year, which the lapse rates
# read, the healthy lives on the exit basis being none, so that no lapse is weighted by
# them; and the cohort vector and its rates, as long as the cover from issue, 12n longer
# than S's.  _clock_faults holds the clock to S's plus 12n and the attained age to S's,
# and _cohort_faults the cohorts and their rates to S's, the rest zeros; result_states is
# compared frame by frame, without its lapse_rate column.  The claim on the active-lives
# basis has a test of its own.
IN_CLAIM_CELLS = frozenset({"age_at_entry", "duration", "duration_mth", "policy_year",
                            "lapse_rate_base", "lapse_rate", "lapse_rate_mth",
                            "sick_cohorts", "claim_rate_vectors", "max_dur",
                            "result_states"})

# The result_cf columns that expense inflation moves, and the cells they are made of: on
# the committed points, at the shipped 3%, the only places an in-force row's flows depart
# from S.
INFLATED = ("expenses", "net_cf")
INFLATION_CELLS = frozenset({"inflation_factor", "expenses", "net_cf", "result_cf"})

# The discount factor and the two values it makes, which discount to each model's own
# start, S's frame's and the valuation date here (D7): on a row S does not open at the
# valuation date they differ by design, and the present value test holds them.  No report
# shows them, so a comparison meets them only where S has evaluated them.
DISCOUNT_CELLS = frozenset({"disc_factor", "pv_benefits", "annuity_dis"})

# The S cells whose exact value is 0 and whose computed value is rounding about it, the
# roll-forward's residual and the population identity's: a comparison with S holds them at
# the harness's absolute floor of 1e-9, and every other cell at none (_compare).
RESIDUALS = frozenset({"check_pols_roll_fwd_resid", "check_states_resid"})

# The reads keyed by an attained age or a policy year, and the monthly rates, none of which
# may be evaluated before issue (R1, D4).  The annual rates, inception_rate, mort_rate and
# lapse_rate, are columns of result_states, as in IP_UK_S, so the report evaluates them in
# every month of the frame, and before issue each is 0.0 without a read (OUTSIDE_COVER):
# the reads under them are what T3 holds.
KEYED_READS = ("age", "duration", "policy_year", "lapse_rate_base", "mort_rate_mth",
               "lapse_rate_mth", "inception_rate_mth")

# The cells that scale with the counts.  Every other cell is a per-policy amount, a share,
# a rate, a factor, a clock or a flag, and must not move when the counts do.
COUNTED = frozenset({
    "policy_count", "pols_if_init", "pols_if", "pols_if_at", "pols_new_biz", "pols_active",
    "pols_sick", "sick_cohorts", "pols_sick_dur", "pols_sick_surv", "pols_recovery",
    "pols_death_sick", "pols_exit", "pols_death_active", "pols_lapse", "pols_inception",
    "pols_maturity", "pols_dead_cum", "pols_lapse_cum", "pols_exit_cum", "premiums",
    "claims", "expenses", "net_cf", "pv_benefits", "check_pols_roll_fwd_resid",
    "check_states_resid", "result_cf", "result_states", "result_pols"})

# result_pols' columns, in its order: the count in force, the new business within it, the
# healthy and the sick counts, then the month's movements in the notes' processing order,
# out of H the deaths, the lapses and the inceptions, out of S the recoveries and the deaths,
# the recoveries leaving the model and the expiry; then the amounts per policy, which no
# count moves.
RESULT_POLS = ["pols_if", "pols_new_biz", "pols_active", "pols_sick", "pols_death_active",
               "pols_lapse", "pols_inception", "pols_recovery", "pols_death_sick",
               "pols_exit", "pols_maturity", "benefit_pp", "premium_pp"]
COUNTS_POLS = RESULT_POLS[:11]
PER_POLICY_POLS = RESULT_POLS[11:]

# S's two timings and BEF_NB, the one running in force adds; and the kinds.
TIMINGS = ("BEF_NB", "BEF_DECR", "AFT_DECR")
KINDS = ("BENEFIT", "DEATH", "LAPSE")

# What each cell holds outside cover, before issue and from the month cover has ended, as
# its docstring says: no count, so no cash flow; no benefit or premium; no rate read at a
# policy year or an age the policy does not have.  The type is part of the value: a count
# is a float in every branch, because the C step types a cell by the values it returns
# (USLIB-SEC-PLAN.md F3).  The guard test also calls pols_if_at at each timing and claims
# at each kind, all 0.0, and the cohort vector, all zeros.
OUTSIDE_COVER = {
    "is_active": False, "benefit_pp": 0.0, "premium_pp": 0.0, "amount_payable_pp": 0.0,
    "inception_rate": 0.0, "mort_rate": 0.0, "lapse_rate_base": 0.0, "lapse_rate": 0.0,
    "pols_active": 0.0, "pols_sick": 0.0, "pols_if": 0.0, "pols_new_biz": 0.0,
    "pols_sick_surv": 0.0, "pols_recovery": 0.0, "pols_death_sick": 0.0, "pols_exit": 0.0,
    "pols_death_active": 0.0, "pols_lapse": 0.0, "pols_inception": 0.0,
    "pols_maturity": 0.0, "pols_dead_cum": 0.0, "pols_lapse_cum": 0.0,
    "pols_exit_cum": 0.0, "premiums": 0.0, "expenses": 0.0, "net_cf": 0.0,
    "check_pols_roll_fwd_resid": 0.0, "check_states_resid": 0.0}

# The cells a month outside cover may not reach: the clocks of the contract and the
# monthly rates, each keyed by a policy year or an attained age.  The reads that guard
# themselves are held by their values in OUTSIDE_COVER instead.
IN_COVER_ONLY = ("age", "duration", "policy_year", "mort_rate_mth", "lapse_rate_mth",
                 "inception_rate_mth")

# The opening state, in the table's order, and the cells running in force adds to
# IP_UK_S's, each of which the symbol map must name.
STATE = ("pols_active_init", "benefit_pp_init", "premium_pp_init")
NEW_CELLS = ("policy_count", "duration_mth_init", "duration_init", "t_entry", "is_active",
             "expiry_mth", "pols_new_biz", "pols_sick_dur_init", "result_pols", *STATE)

INFLATION = 0.03        # the shipped inflation_rate, which the inflation test reads

# The recursion limit, as mx.set_recursion takes it, under which the committed points are
# first swept (R2, F7).  A report evaluates each column in ascending t, so a forward
# recursion, through t - 1, finds the month before already cached: the committed points'
# sweep passes under a limit far below it (measured at M7).  A backward recursion over the
# frame, through t + 1, opens a chain as long as the frame, and the committed frames run to
# 360 months.
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


def _committed_cohorts():
    """The committed claim cohorts as the file holds them, unvalidated, a plain table."""
    return pd.read_csv(model_path(SEC).parent / COHORTS)


def _sec_inputs(tmp_path, table, cohorts=None, edits=None):
    """A copy of the product directory whose SEC table is ``table``, and whose claim
    cohorts are ``cohorts`` (the committed ones where ``None``), other inputs changed by
    ``edits``, as :func:`uk_sec_support.temp_inputs` takes them; its SEC folder."""
    edits = dict(edits or {})
    if cohorts is not None:
        edits[COHORTS] = cohorts
    return temp_inputs(tmp_path, model_path(SEC), model_points=table,
                       model_point_file=TABLE, edits=edits)


def _read_edited(tmp_path, edit, cohorts_edit=None, edits=None):
    """IP_UK_SEC read from a copy whose SEC table is ``edit(_committed())`` and whose
    claim cohorts are ``cohorts_edit(_committed_cohorts())``."""
    cohorts = None if cohorts_edit is None else cohorts_edit(_committed_cohorts())
    folder = _sec_inputs(tmp_path, edit(_committed()), cohorts, edits)
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

    :func:`uk_sec_support.sweep` reaches ``IP_UK_S``'s ``pols_if_at`` at none of its
    timings, since S's roll-forward reads ``pols_if(t + 1)``; nor ``duration_mth``, which no
    S formula reads; nor the survival step of each claim duration, which no report reads,
    nor ``premium_basis``, which no formula calls.  A cell S never evaluates is compared
    nowhere, so they are evaluated here, over the frame and the cohort vector, and the
    splice and the future comparison see them too.  The present value and the annuity
    factor discount from each model's own start, and a test of their own compares them.
    """
    sweep(proj)
    for t in range(proj.proj_len()):
        for timing in ("BEF_DECR", "AFT_DECR"):
            proj.pols_if_at(t, timing)
        proj.duration_mth(t)
    for z in range(1, proj.max_dur() + 1):
        proj.claim_surv_step(z)
    proj.premium_basis()


def _years_in_force(s_proj, sec_proj, month):
    """n: the whole years by which the SEC row's policy clock runs ahead of S's, 0 on a
    row of S's new business and ``n`` on a row of one of S's claims (the spec's
    ``_ip_twin_years``)."""
    gap = sec_proj.duration_mth_init() - s_proj.duration_mth(month)
    assert gap % 12 == 0, gap
    return gap // 12


def _cumulative_faults(s_proj, sec_proj, month):
    """Where SEC's cumulative counts depart from S's increments since S's month ``month``.

    Each restarts at ``t_entry()`` on SEC, on the count on the books, where S's counts from
    its frame's start, so at every month of SEC's frame SEC's count is S's at
    ``month + t`` less S's at ``month``, to 1e-9 relative with no absolute floor: 0.0 in
    both at ``t = 0``.  On a row issued later, before issue, SEC's is 0.0.
    """
    found = []
    entry = sec_proj.t_entry()
    for name in CUMULATIVE:
        base = s_proj.cells[name](month) if month > 0 else 0.0
        for t in range(sec_proj.proj_len()):
            got = sec_proj.cells[name](t)
            want = 0.0 if t < entry else s_proj.cells[name](month + t) - base
            if not abs(got - want) <= 1e-9 * max(abs(got), abs(want)):
                found.append(f"{name}({t}): SEC {got!r}, S's increment since its month "
                             f"{month} {want!r}")
    return found


def _clock_faults(s_proj, sec_proj, month):
    """Where a row of one of S's claims departs from S's clocks shifted by its years.

    SEC's policy clock runs ``12n`` months ahead of S's restarted one, at every month of
    the frame, and its issue age ``n`` years behind, so its attained age is S's, which the
    cell comparison holds, ``age`` being compared there; the cohort vector is ``12n``
    longer, the cover from issue and a cohort of headroom.
    """
    n = _years_in_force(s_proj, sec_proj, month)
    found = []
    if not n > 0:
        found.append(f"the row's clock is S's, n = {n}")
    if sec_proj.age_at_entry() != s_proj.age_at_entry() - n:
        found.append(f"issue age {sec_proj.age_at_entry()}, S's {s_proj.age_at_entry()} "
                     f"less {n}")
    for t in range(sec_proj.proj_len()):
        if sec_proj.duration_mth(t) != s_proj.duration_mth(month + t) + 12 * n:
            found.append(f"duration_mth({t}) {sec_proj.duration_mth(t)}, S's "
                         f"{s_proj.duration_mth(month + t)} plus {12 * n}")
            break
    if sec_proj.max_dur() != sec_proj.expiry_mth() + 1:
        found.append(f"max_dur() {sec_proj.max_dur()}, not expiry_mth() + 1")
    return found


def _cohort_faults(s_proj, sec_proj, month):
    """Where a row's cohort vector, and the rates it is aged by, depart from S's.

    At every month of the frame SEC's ``sick_cohorts(t)`` holds S's ``sick_cohorts(month +
    t)`` element by element, to 1e-9 relative with no absolute floor, and zeros, exactly,
    past S's length; and SEC's three rate vectors hold S's, element by element, the rates
    of each claim duration S's vector reaches.
    """
    found = []
    for t in range(sec_proj.proj_len()):
        mine, theirs = sec_proj.sick_cohorts(t), s_proj.sick_cohorts(month + t)
        if len(mine) < len(theirs):
            found.append(f"sick_cohorts({t}) is {len(mine)} long, S's {len(theirs)}")
            break
        bad = [z for z, (a, b) in enumerate(zip(theirs, mine), start=1)
               if not abs(a - b) <= 1e-9 * max(abs(a), abs(b))]
        bad += [z for z in range(len(theirs) + 1, len(mine) + 1) if mine[z - 1] != 0.0]
        if bad:
            found.append(f"sick_cohorts({t}) departs from S's at z = {bad[:5]}")
            break
    for mine, theirs in zip(sec_proj.claim_rate_vectors(), s_proj.claim_rate_vectors()):
        if list(mine[:len(theirs)]) != list(theirs):
            found.append("claim_rate_vectors() departs from S's")
            break
    return found


def _compare(s_proj, sec_proj, month, exempt, columns=None):
    """Where SEC's row departs from S's point from S month ``month`` on, in two passes.

    First the frames, ``result_cf`` (over ``columns``, or every column both hold) and
    ``result_states``, SEC row ``t`` against S row ``t + month``, frames ending together;
    then every cell of S's but ``exempt`` and :data:`RESIDUALS`, at every argument S cached
    inside its frame from ``month`` on, moved onto SEC's clock, S's timing and kind strings
    mapped onto SEC's codes (``uk_sec_support.codes``).  Both to 1e-9 relative with no
    absolute floor (USLIB-SEC-PLAN.md §5.2, T2, precised at M11): a floor of 1e-9 passes an
    error of 1% in any value below 1e-7.  Then the cells of :data:`RESIDUALS` alone, at the
    floor of 1e-9: their exact value is 0, and the computed one moves by an ulp of what it
    closes when an opening state comes back from the CSV one ulp off.  Then the cumulative
    counts, by their increments (:func:`_cumulative_faults`).  On a row of one of S's
    claims, whose policy clock S restarts, the cells of :data:`IN_CLAIM_CELLS` are left to
    :func:`_clock_faults` and :func:`_cohort_faults`, and the lapse rate to neither report
    column: such a row on the exit basis holds no healthy life to lapse.  On a row S does
    not open at the valuation date, ``month`` not 0, :data:`DISCOUNT_CELLS` are left out.
    Returns the mismatch lines, empty when the row is S's.
    """
    in_claim = s_proj.status() == "in_claim"
    if in_claim:
        exempt = exempt | IN_CLAIM_CELLS
    if month != 0:
        exempt = exempt | DISCOUNT_CELLS
    states = [c for c in s_proj.result_states().columns
              if not (in_claim and c == "lapse_rate")]
    found = []
    for report, keep in (("result_cf", columns), ("result_states", states)):
        found += [f"{report}: {line}" for line in frame_mismatches(
            s_proj.cells[report](), sec_proj.cells[report](), t_offset=month,
            columns=keep, atol=0.0)]
    found += twin_mismatches(s_proj, sec_proj, t_offset=month, exempt=exempt | RESIDUALS,
                             atol=0.0, codes=codes(sec_proj))
    found += twin_mismatches(s_proj, sec_proj, t_offset=month,
                             exempt=exempt | (set(s_proj.cells) - RESIDUALS),
                             codes=codes(sec_proj))
    found += _cumulative_faults(s_proj, sec_proj, month)
    if in_claim:
        found += _clock_faults(s_proj, sec_proj, month)
        found += _cohort_faults(s_proj, sec_proj, month)
    return found


def _continues_s(s_proj, sec_proj, month):
    """Where a committed row departs from S's point ``s_proj`` from S month ``month`` on.

    The splice's comparison (:func:`_compare`), on the committed model at the shipped
    assumptions: frame by frame, ``result_cf`` and ``result_states``, then cell by cell
    over every cell of S's but :data:`SPLICE_EXEMPT`.  The shipped 3% expense inflation
    runs from S's frame's start and from the valuation date here (D7), so on a row valued
    after that start :data:`INFLATED`'s two columns, and :data:`INFLATION_CELLS`, differ by
    design and are left out; the inflation test holds them.  On the twin of one of S's
    claims, which S opens at the valuation date, the two clocks of inflation are one.
    Every other column and cell must agree, to 1e-9 relative, with no absolute floor but on
    the residuals.
    """
    if month == 0:
        return _compare(s_proj, sec_proj, month, SPLICE_EXEMPT)
    keep = [c for c in s_proj.result_cf().columns if c not in INFLATED]
    return _compare(s_proj, sec_proj, month, SPLICE_EXEMPT | INFLATION_CELLS, keep)


def _case_id(rates, kind, s_point, month):
    """A case's id: ``main-point2-d12``, or ``main-point2-k3`` if issued later."""
    if kind == "future":
        return f"{rates}-point{s_point}-k{-month}"
    return f"{rates}-point{s_point}-" + (f"d{month}" if kind == "derived" else
                                         f"{kind}{month}")


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
    """IP_UK_SEC read in place, as committed, and swept once, cold; what it met.

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
    """IP_UK_SEC read in place, as committed, with every point swept (sec_read)."""
    return sec_read[0]


@pytest.fixture(scope="module")
def s_model():
    """IP_UK_S read in place, as committed, with every point swept.

    T6 regenerates the SEC inputs from it, which would otherwise project every S point
    again (USLIB-SEC-PLAN.md §4, *Carried into Phase 1*), and the in-force tests read S's
    months off it.
    """
    model = mx.read_model(model_path(TWIN), name=_name("s"))
    for key in point_keys(model):
        _sweep_s(projection(model, key))
    yield model
    model.close()


def _set_points(rates):
    """The S points a splice set's S model holds: every point and variant in the main
    set, and the points of its cases in the others."""
    if rates == "main":
        return None
    return sorted({*SET_MTHS[rates], *(p for p, _ in SET_FUTURES[rates])})


class _Splices:
    """The splice's models, a pair for each of :data:`SPLICE_SETS`, each made when first
    asked for (:meth:`pair`) and closed at the module's end.

    For a set, S is read from a copy of the product directory whose table has the variants
    appended, only the set's points outside the main set, and the set's References are set
    on it.  SEC runs on the same assumption tables, and on a model point table and claim
    cohorts of its own, built by the generator from the registered spec with its rows
    replaced by the set's cases this run selects, the core or the full grid
    (:func:`_selected`), out of this S model, so each row opens with the state of the very
    run it is compared with, its cohorts among it; the set's References are set on it too.
    No input table moves with ``d``: IP's one valuation-clock input is the
    ``inflation_rate`` Reference.  An S point is swept (:func:`_sweep_s`) when a case first
    compares a row with it (:meth:`s_point`), and stays swept, the points of a set holding
    some tens of megabytes; each SEC row is projected by the case that compares it and
    released once compared (:func:`_settle`).
    """

    def __init__(self, root):
        self.root, self.pairs, self.swept = root, {}, {}

    def pair(self, rates):
        if rates not in self.pairs:
            refs = SPLICE_SETS[rates]
            s = mx.read_model(temp_inputs(self.root / rates / "s", model_path(TWIN),
                                          model_points=_s_table_with_variants(
                                              _set_points(rates))),
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
            sec = mx.read_model(_sec_inputs(self.root / rates / "sec", table,
                                            companions[COHORTS]),
                                name=_name(f"sec_{rates}"))
            for ref, value in refs.items():
                setattr(sec.Projection, ref, value)
            self.pairs[rates], self.swept[rates] = (s, sec), set()
        return self.pairs[rates]

    def s_point(self, rates, s_point):
        """S point ``s_point`` of set ``rates``, swept, as a comparison needs it: the S
        space must be swept before a row is compared with it, since the comparison reads
        what S cached (:func:`uk_sec_support.twin_mismatches`)."""
        s = self.pair(rates)[0]
        proj = _point(s, s_point)
        if s_point not in self.swept[rates]:
            _sweep_s(proj)
            self.swept[rates].add(s_point)
        return proj

    def close(self):
        for s, sec in self.pairs.values():
            sec.close()
            s.close()


@pytest.fixture(scope="module")
def spliced(tmp_path_factory):
    """The splice's models, by set, each pair made when first asked for (:class:`_Splices`)."""
    splices = _Splices(tmp_path_factory.mktemp("spliced"))
    yield splices
    splices.close()


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


def _pivots(x):
    """The pivot ages of row ``x``'s inception schedule, sorted."""
    sub = x.data.inception_table().loc[(x.sex(), x.occ_class(), x.deferred_weeks())]
    return sorted(int(a) for a in sub.index)


def _held(x, t):
    """The claim durations at which row ``x`` holds lives in claim at the start of month
    ``t``."""
    return [z for z, held in enumerate(x.sick_cohorts(t), start=1) if held > 0.0]


# What test_the_core_grid_reaches_every_branch asks of the core's rows in the model's own
# values, which no column of the table shows: each holds of some core row, or of a core row
# in some month of its frame.  At the valuation date, every opening-state column in use, a
# share or an amount apart from its issue value, and each kind of valuation month: in the
# first policy year, on an anniversary whose escalation is month 0's, every life in claim,
# lives in health and in claim, and a claim in the termination table's last year.  Later in
# the frame, every branch and both sides of each min and max the full grid reaches: an
# inception, a recovery back to health and one leaving the model, a death in each state, a
# lapse, an escalation, the escalation lapse shock and the RPI's floor and cap, the lapse
# table inside and past its last year, the termination table inside and past its last
# year, the inception rate interpolated between pivots and extrapolated beyond each end,
# the recovery rate's bound binding and not, an active cell on the exit basis and the
# policy end date's last month.  Three bounds bind elsewhere, each in a test of its own:
# the caps on mortality and inception and the lapse rate's bound.  Two are idle on every
# input the model accepts: the inception rate's floor at 0, since the shipped schedules,
# one shape scaled, extrapolate to 0 only below age 13.3, under the youngest issue age; and
# the in-claim mortality's cap, since Data holds the termination table's rates to 0 to 1.
AT_VALUATION = {
    "lives in health and in claim": lambda x: 0.0 < x.pols_active_init() < 1.0,
    "every life in claim": lambda x: (
        x.duration_mth_init() > 0 and x.pols_active_init() == 0.0),
    "a claim in the termination table's last year": lambda x: (
        x.duration_mth_init() > 0 and any(
            x.claim_dur_year(z) >= x.data.termination_last_year()
            and x.pols_sick_dur_init(z) > 0.0 for z in range(1, x.duration_mth_init() + 1))),
    "benefit_pp_init above the benefit at issue": lambda x: (
        x.benefit_pp_init() > x.benefit_mth()),
    "premium_pp_init above the premium at issue": lambda x: (
        x.premium_pp_init() > x.premium_mth()),
    "valued in the first policy year": lambda x: 0 < x.duration_mth_init() < 12,
    "an escalation at t = 0 on an anniversary valuation": lambda x: (
        0 < x.duration_mth_init() and x.duration_mth_init() % 12 == 0
        and x.benefit_pp(0) > x.benefit_pp_init()),
    "a claim on a policy clock of whole years": lambda x: (
        x.status() == "in_claim" and x.duration_mth_init() % 12 == 0),
}
IN_FRAME = {
    "an inception": lambda x, t: x.pols_inception(t) > 0.0,
    "a recovery back to health": lambda x, t: (
        x.recovery_basis() == "return_to_h" and x.pols_recovery(t) > 0.0),
    "a recovery leaving the model": lambda x, t: x.pols_exit(t) > 0.0,
    "a death in claim": lambda x, t: x.pols_death_sick(t) > 0.0,
    "a death in health": lambda x, t: x.pols_death_active(t) > 0.0,
    "a lapse": lambda x, t: x.pols_lapse(t) > 0.0,
    "an escalation": lambda x, t: (
        _active(x, t) and x.esc_rate() > 0.0 and x.duration(t) > x.duration_init()),
    "the escalation lapse shock": lambda x, t: (
        _active(x, t) and x.esc_lapse_factor(t) > 1.0),
    "the RPI's floor binding": lambda x, t: (
        _active(x, t) and x.escalation() == "RPI" and x.rpi_rate < 0.0),
    "the escalation cap binding": lambda x, t: (
        _active(x, t) and x.escalation() == "RPI" and x.rpi_rate > x.esc_cap),
    "inside the lapse table": lambda x, t: (
        _active(x, t) and x.policy_year(t) < x.data.lapse_last_year()),
    "past the lapse table's last year": lambda x, t: (
        _active(x, t) and x.policy_year(t) > x.data.lapse_last_year()),
    "a claim inside the termination table": lambda x, t: (
        _active(x, t) and any(x.claim_dur_year(z) < x.data.termination_last_year()
                              for z in _held(x, t))),
    "a claim past the termination table's last year": lambda x, t: (
        _active(x, t) and any(x.claim_dur_year(z) > x.data.termination_last_year()
                              for z in _held(x, t))),
    "the inception rate between pivots": lambda x, t: (
        _active(x, t) and _pivots(x)[0] < x.age(t) < _pivots(x)[-1]),
    "the inception rate below the first pivot": lambda x, t: (
        _active(x, t) and x.age(t) < _pivots(x)[0]),
    "the inception rate past the last pivot": lambda x, t: (
        _active(x, t) and x.age(t) > _pivots(x)[-1]),
    "the recovery rate's bound binding": lambda x, t: (
        _active(x, t) and any(x.rec_rate(z) == 1.0 for z in _held(x, t))),
    "a recovery rate below its bound": lambda x, t: (
        _active(x, t) and any(0.0 < x.rec_rate(z) < 1.0 for z in _held(x, t))),
    "an active cell on the exit basis": lambda x, t: (
        x.recovery_basis() == "exit" and x.pols_active(t) > 0.0),
    "the policy end date's last month": lambda x, t: x.pols_maturity(t) > 0.0,
}


def _branches(x):
    """The names in :data:`AT_VALUATION` and :data:`IN_FRAME` that hold of row ``x``."""
    reached = {what for what, holds in AT_VALUATION.items() if holds(x)}
    frame = range(x.t_entry(), x.proj_len())
    return reached | {what for what, holds in IN_FRAME.items()
                      if any(holds(x, t) for t in frame)}


def _settle(records, case, model, key):
    """Record what the rules and the core grid's reach need of a row, and release it.

    ``case`` is the row's (set, row_kind, S point, source_mth) and ``key`` its registry key
    in ``model``, the splice's SEC model.  A T2 or T3 case calls this once it has compared
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
    nowhere else, because on a point issued at ``t = 0`` the two clocks coincide and the
    opening state is the issue value.  For the same reason it is the test that catches a
    policy month passed as ``t`` (R1a), as an anniversary, a lapse table's year or an
    escalation read on ``t`` would be.  The frame comparisons read SEC row ``t`` against S
    row ``t + d`` in every column of ``result_cf`` and ``result_states``, and fail frames
    that end apart.  The cell comparison then evaluates every cell of S's but
    :data:`SPLICE_EXEMPT`, at every argument S cached inside its own frame from month ``d``
    on, moved onto SEC's clock: the healthy count, the cohort vector element by element,
    the transitions out of each state, the benefit, the premium and the rates, among them.
    Each compares to 1e-9 relative with no absolute floor, but the residuals, which keep the
    floor of 1e-9, and the cumulative counts, which restart on the books and are compared
    by their increments (:func:`_compare`).  An S cell this model lacked would fail it.

    A row of one of S's claims, which S opens with its policy clock restarted at the
    valuation date, is on its policy clock of whole years here, and is compared with S's
    clock shifted by them, its cohorts with S's padded with zeros.  The twins of those
    claims, issued ``n`` years before the valuation date, are compared at offset 0.  The
    row is then recorded for the rules test and released (:func:`_settle`).
    """
    s, sec = spliced.pair(rates)
    key = _row_key(sec, kind, s_point, month)
    s_proj, sec_proj = spliced.s_point(rates, s_point), projection(sec, key)
    try:
        assert _compare(s_proj, sec_proj, month, SPLICE_EXEMPT) == []
    finally:
        _settle(splice_records, (rates, kind, s_point, month), sec, key)


# ---------------------------------------------------------------------------
# T3 -- future new business


@pytest.mark.parametrize(
    "rates, s_point, k",
    [_case(case, CORE_FUTURES, _case_id(case[0], "future", case[1], -case[2]))
     for case in FUTURES])
def test_future_new_business_is_the_s_projection_k_months_on(spliced, splice_records,
                                                             rates, s_point, k):
    """Issued k months after the valuation date, the point is S's projection k months on.

    SEC rows ``k ..`` are S rows ``0 ..``, ending together at the policy end date, in
    ``result_cf`` and ``result_states``, and every cell of S's but :data:`FUTURE_EXEMPT`
    agrees at every argument S cached inside its own frame, moved ``k`` later, the cohort
    vector among them, all zeros until claims incept.  Each compares as the splice compares,
    with no absolute floor but on the residuals (:func:`_compare`).  An S cell this model
    lacked would fail it.  Before issue every column of ``result_cf``, ``result_states`` and
    ``result_pols`` is an exact zero, and the policies arrive in month ``k`` as new
    business, all healthy.

    The last assertions are R1 and D4's base rule made testable.  After the reports, no read
    keyed by an attained age or a policy year, and no monthly rate, has been evaluated at a
    month before issue (:data:`KEYED_READS`); the annual rates, columns of
    ``result_states``, are 0.0 there without a read.  A count recursion based at ``t == 0``
    rather than at ``t_entry()``, or a transition that evaluates its rate before asking
    whether the month is in cover, still gives the right numbers.  This is the only test
    that sees the first, and the guard test sees the second too.

    The pre-issue rows are asserted present before they are asserted zero, in every report:
    a frame that opened at issue would have none, its zeros would hold of nothing, and the
    comparisons with S, which start at issue, would not see it.  The row is then recorded
    for the rules test and released (:func:`_settle`).
    """
    s, sec = spliced.pair(rates)
    key = _row_key(sec, "future", s_point, -k)
    s_proj, sec_proj = spliced.s_point(rates, s_point), projection(sec, key)
    try:
        assert _compare(s_proj, sec_proj, -k, FUTURE_EXEMPT) == []
        for report in ("result_cf", "result_states", "result_pols"):
            frame = sec_proj.cells[report]()
            assert list(frame.index[:k]) == list(range(k)), report
            assert (frame.loc[:k - 1] == 0.0).all().all(), report
        assert sec_proj.pols_new_biz(k) == sec_proj.policy_count() == 1.0
        assert sec_proj.pols_active(k) == 1.0 and sec_proj.pols_sick(k) == 0.0
        early = {name: sorted(args[0] for args in _cached_args(sec_proj.cells[name])
                              if args[0] < k)
                 for name in KEYED_READS}
        assert not any(early.values()), f"read before issue: {early}"
    finally:
        _settle(splice_records, (rates, "future", s_point, -k), sec, key)


# ---------------------------------------------------------------------------
# The claim on the active-lives basis, under a flat lapse table
#
# IP_UK_S's point 7 is the worked example's claim on the return_to_h basis: its recovered
# lives return to health and lapse there.  S restarts the policy clock at the valuation
# date, so it lapses them at the first policy year's rate, 10%, where the twin, issued a
# year before, lapses them at the second's, 8%, and so on down the table: S's restarted
# clock is a defect of S (UKLIB-SEC-PLAN.md §6.3, model-sec.md).  So the twin and its rows
# are compared with S under a lapse table that is flat, every year at 10%, the shipped
# first year's rate, on which the two clocks lapse alike.  The first year's rate being the
# shipped one, S's states up to any month are what the shipped table gives them, so the
# committed row of point 7 at month 12 continues S there too.
FLAT_LAPSE = {"lapse_table.csv": lambda t: t.assign(lapse_rate=0.10)}
POINT7_MTHS = {"core": (1, 12), "full": (13, 24, 60, 359)}


@pytest.mark.parametrize("grid", GRIDS)
def test_the_claim_on_the_active_lives_basis_continues_s_under_a_flat_lapse_table(
        tmp_path, grid):
    """S's point 7, its twin and its rows, are S's under a flat lapse table (§6.3).

    Under :data:`FLAT_LAPSE`, in S and SEC alike, with the main set's References
    (:data:`MAIN`), the twin of S's point 7, issued a year before the valuation date at
    34, and the point restated in force at a month after its claim's first recoveries
    have returned to health and started claiming again, are S's from their months on, in
    every cell, as the splice compares them (:func:`_compare`): the healthy lives, each
    cohort, the recoveries back to health and every flow.  The default run compares the
    twin and the rows at months 1 and 12, and the full grid the rows at 13, 24, 60 and 359.

    And at the shipped lapse table the twin parts from S, as S's restarted clock makes it:
    its recovered lives lapse at the second policy year's 8% where S's lapse at the first's
    10%, so that 60 months on 0.8002 of the policy is in force where S holds 0.7791.  That
    is S's defect, which model-sec.md records, and no departure of this model's.
    """
    s = mx.read_model(temp_inputs(tmp_path / "s", model_path(TWIN), edits=FLAT_LAPSE),
                      name=_name("flat_s"))
    sec = None
    try:
        for ref, value in MAIN.items():
            setattr(s.Projection, ref, value)
        months = POINT7_MTHS[grid]
        spec = dataclasses.replace(SPEC, derived=tuple((7, d) for d in months), future=(),
                                   derived_refs={})
        table, companions = build_sec_table(spec, s)
        sec = mx.read_model(_sec_inputs(tmp_path / "sec", table, companions[COHORTS],
                                        edits=FLAT_LAPSE), name=_name("flat"))
        for ref, value in MAIN.items():
            setattr(sec.Projection, ref, value)
        s_proj = _point(s, 7)
        _sweep_s(s_proj)
        cases = ((("twin", 7, 0),) if grid == "core" else ()) + tuple(
            ("derived", 7, d) for d in months)
        found = []
        for case in cases:
            found += [f"{case}: {line}" for line in _compare(
                s_proj, _row(sec, *case), case[2], SPLICE_EXEMPT)]
        assert not found, found[:20]
        if grid == "full":
            return
        back = _row(sec, "derived", 7, 12)
        assert 0.0 < back.pols_active_init() < 1.0 and back.pols_recovery(0) > 0.0
        assert back.pols_inception(0) > 0.0
    finally:
        if sec is not None:
            sec.close()
        s.close()
    shipped_s = mx.read_model(model_path(TWIN), name=_name("defect_s"))
    shipped = mx.read_model(model_path(SEC), name=_name("defect"))
    try:
        twin, s7 = _row(shipped, "twin", 7, 0), _point(shipped_s, 7)
        assert (twin.lapse_rate(0), s7.lapse_rate(0)) == (0.08, 0.1)
        assert round(twin.pols_if(60), 4) == 0.8002 and round(s7.pols_if(60), 4) == 0.7791
        assert twin.pols_if(1) == s7.pols_if(1) and twin.pols_if(2) != s7.pols_if(2)
    finally:
        shipped.close()
        shipped_s.close()


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
    The splice's rows are points in force at every month T2 names, the variants and the
    twins of S's claims among them, and points issued later, under every set, and on each
    the reports, the checks and the full sweep are run first (:func:`_rule_breaches`):

    * R1: no cell holds a negative argument.  modelx evaluates one without complaint, and
      a compiled cache raises ``IndexError`` below 0 (USLIB-SEC-PLAN.md F4).  A policy
      month turned into ``t`` by subtracting ``duration_mth_init()`` (R1a) goes negative
      on a point in force past it.
    * R1's look-back stops at ``t_entry()``: no cell evaluated at a month from
      ``t_entry()`` on read a month before it.  On a point issued later a recursion based
      at ``t == 0`` reads the pre-issue zeros, so no number shows it and no argument goes
      negative.
    * R2's look-ahead: no cell evaluated at month ``t`` read a cell keyed by a month beyond
      ``t + 1``, as modelx's dependency graph records each cached call's precedents; this
      model admits none (:data:`LOOK_AHEAD`).
    * And no call of the full sweep raised.

    Each row was scanned by the T2 or T3 case that compared it (:func:`_settle`), and a row
    no case has scanned is scanned here.  The core case covers the core's rows, the full
    case every other row of the full grid, with ``UKLIB_SEC_FULL=1``.  The new-business
    twins in the splice's tables are no case's, and are left out: on them the clocks
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
# Data's first reads of its tables.  IP runs its chains one cell a month: the healthy count,
# pols_active, which reads itself at t - 1 and the recoveries of t - 1; the cohort vector,
# sick_cohorts, which reads itself at t - 1 and the inceptions of t - 1; and the three
# cumulative counts, each reading itself at t - 1.  Measured at M7, at the contract's
# longest cover, issued now and 120 months on, with the escalation lapse shock on: a cold
# net_cf in the last month runs 8 or 9 cells beyond its chain on every shape, 631 or 632
# levels deep from issue at 18 to expiry at 70, since the chains stop at t_entry(); the
# healthy count's head 5 or 6, the cohort vector's and the cumulative counts' 6, the
# population identity's residual 7 and the roll-forward's 8.  Term's 16 (USLIB-SEC-PLAN.md
# D5).  Any chain of two cells a month runs a frame's length beyond.
CHAIN_OVERHEAD = 16

# The contract's longest cover (held by proj_len()): issued at issue_age_min, 18, to
# expiry_age_max, 70, 624 months, the same on every shape.
YOUNGEST, OLDEST_EXPIRY = 18, 70

# The chains of the model and the cells that head them, called cold in the last month of
# the frame, each on a read of its own: (cell, the timing it takes, or None).
CHAIN_HEADS = (("net_cf", None), ("pols_active", None), ("sick_cohorts", None),
               ("pols_dead_cum", None), ("check_states_resid", None),
               ("check_pols_roll_fwd_resid", None), ("pols_if_at", "BEF_NB"))

# The shapes the chains run at their longest cover on, by the S point whose twin each is,
# with the recovery basis each runs on: the anchor cell, healthy at issue, on the
# active-lives basis and on the exit basis, issued now and 120 months on; and the claim
# from duration 0 on each basis, in force a year at the valuation date, the cohort in
# payment its one row.  The anchor cell on the active-lives basis runs by default, and the
# other three with the full grid.
CHAIN_SHAPES = {"active": (1, "return_to_h"), "active_exit": (1, "exit"),
                "claim_exit": (2, "exit"), "claim": (7, "return_to_h")}


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


def _longest_cover(tmp_path, shape):
    """A copy whose table holds the twin of :data:`CHAIN_SHAPES`'s ``shape`` at the
    contract's longest cover, and each row's frame and ``t_entry()``.

    The twin issued at 18 and expiring at 70, 624 months of cover.  On a healthy shape,
    issued at the valuation date and 120 months after it, the shipped
    ``future_horizon_mth``: frames of 624 and 744 months, whose chains stop at
    ``t_entry()``.  On a claim, in force a year at the valuation date, its cohort in
    payment carried over: a frame of 612 months.  The shipped tables serve every age from
    18 to 69.
    """
    s_point, basis = CHAIN_SHAPES[shape]
    committed = _committed()
    label = _label(committed, "twin", s_point, 0)
    top = committed.index.max()
    row = committed.loc[[label]].assign(recovery_basis=basis, expiry_age=OLDEST_EXPIRY,
                                        entry_age=YOUNGEST)
    cover = 12 * (OLDEST_EXPIRY - YOUNGEST)
    if committed.at[label, "duration_mth"] > 0:
        rows = row.set_axis([top + 1]).rename_axis("point_id")
        held = _committed_cohorts()
        held = pd.concat([held, held[held["point_id"] == label].assign(point_id=top + 1)],
                         ignore_index=True)
        d = int(committed.at[label, "duration_mth"])
        return _sec_inputs(tmp_path, pd.concat([committed, rows]), held), [
            (top + 1, cover - d, 0)]
    rows = pd.concat([row.set_axis([top + 1]),
                      row.assign(duration_mth=-120).set_axis([top + 2])])
    rows = rows.rename_axis("point_id")
    return _sec_inputs(tmp_path, pd.concat([committed, rows])), [
        (top + 1, cover, 0), (top + 2, cover + 120, 120)]


# modelx warns as its stack trace starts and stops, which is all the test does with it.
@pytest.mark.filterwarnings("ignore:call stack trace:UserWarning")
@pytest.mark.parametrize("shape", [pytest.param(s, id=s,
                                                marks=() if s == "active" else FULL_ONLY)
                                   for s in CHAIN_SHAPES])
def test_every_chain_runs_one_cell_a_month_from_a_cold_start(tmp_path, shape):
    """Called cold, each chain runs one cell a month back to ``t_entry()``, no more.

    No number shows how deep a chain runs, and a compiled model runs it on the C stack, so
    a chain of two cells a month, which gives the same numbers, needs twice the stack on
    every platform (F7); ``IP_UK_S``'s chains each run one cell a month, but reach back to
    its frame's start.  On a model just read, nothing is cached, so modelx's stack trace
    counts how deep a call runs, against one cell a month back to ``t_entry()`` and
    :data:`CHAIN_OVERHEAD` more, with modelx's recursion limit where the module leaves it:
    each head of :data:`CHAIN_HEADS` in the last month of the frame, each on a read of its
    own, at an RPI of 5%, so that the escalation lapse shock reads the RPI in every month.
    On each shape at the contract's longest cover, 624 months from issue age 18 to expiry
    age 70, issued now and 120 months on, or in claim a year at the valuation date
    (:func:`_longest_cover`), each row's frame asserted first, as M1's carried rule asks,
    that every chain runs at its own shape's longest cover.  The anchor cell on the
    active-lives basis, which runs every chain, runs by default, and the others on the full
    grid.
    """
    folder, frames = _longest_cover(tmp_path, shape)
    found = []
    for label, months, entry in frames:
        for cell, timing in CHAIN_HEADS:
            fresh = mx.read_model(folder, name=_name("cold"))
            try:
                fresh.Projection.rpi_rate = 0.05
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


def test_the_counts_roll_forward_through_the_states(sec_model):
    """The count leaves month t by its exits, and the transitions move lives between the
    states.

    On every committed point and at every ``t`` of its frame, to 1e-12: the count in force
    weighting month ``t``, ``pols_if(t)``, less the count it carries into ``t + 1``,
    ``pols_if_at(t + 1, BEF_NB)``, is the deaths in health and in claim, the lapses, the
    recoveries that leave the model and the expiry, which in the last month takes every
    survivor; and the notes' end-of-month count, ``pols_if_at(t, AFT_DECR)``, is exactly the
    count carried into the next month before its new business, 0 in the last.  Within the
    frame the healthy count falls by its deaths, its lapses and its inceptions and rises by
    the recoveries that return to health, and the sick count falls by its recoveries and its
    deaths and rises by the inceptions, so that an inception or a returning recovery moves
    a life between the states and out of neither.

    ``result_pols()`` sets the same movement out row by row, in :data:`RESULT_POLS`'s
    columns, indexed by ``t`` over the frame: ``pols_if`` at ``t + 1`` is ``pols_if`` less
    its exits at ``t``, plus the new business of ``t + 1``, row 0 opening from
    ``pols_if_init()`` within the shares' tolerance, 1e-10 of the count, which ``Data``
    holds the opening shares to.
    """
    table = sec_model.Data.model_point_table()
    for key, point_id in zip(point_keys(sec_model), table.index):
        p = projection(sec_model, key)
        bef_nb, aft = (_code(p, c) for c in ("BEF_NB", "AFT_DECR"))
        last = p.proj_len() - 1
        back = p.recovery_basis() == "return_to_h"
        for t in range(p.proj_len()):
            carried = p.pols_if_at(t + 1, bef_nb)
            assert p.pols_if_at(t, aft) == (0.0 if t == last else carried), (point_id, t)
            out = (p.pols_death_active(t) + p.pols_death_sick(t) + p.pols_lapse(t)
                   + p.pols_exit(t) + p.pols_maturity(t))
            assert p.pols_if(t) - carried == pytest.approx(out, abs=1e-12), (point_id, t)
            if t == last:
                continue
            healthy = (p.pols_death_active(t) + p.pols_lapse(t) + p.pols_inception(t)
                       - (p.pols_recovery(t) if back else 0.0))
            entering = p.pols_active(t + 1) - p.pols_new_biz(t + 1)
            assert p.pols_active(t) - entering == pytest.approx(healthy, abs=1e-12), (
                point_id, t)
            sick = p.pols_recovery(t) + p.pols_death_sick(t) - p.pols_inception(t)
            assert p.pols_sick(t) - p.pols_sick(t + 1) == pytest.approx(sick, abs=1e-12), (
                point_id, t)
        pols = p.result_pols()
        assert list(pols.columns) == RESULT_POLS, point_id
        assert pols.index.name == "t" and list(pols.index) == list(range(p.proj_len()))
        out = pols[["pols_death_active", "pols_death_sick", "pols_lapse", "pols_exit"]]
        carried = (pols["pols_if"] - out.sum(axis=1)).shift(1)
        expected = carried.fillna(p.pols_if_init()) + pols["pols_new_biz"]
        gap = (pols["pols_if"] - expected).abs()
        assert gap.iloc[0] <= 1e-10 * max(p.policy_count(), 1.0), point_id
        assert (gap.iloc[1:] <= 1e-12).all(), point_id


def test_result_pols_holds_s_counts_with_the_new_business_beside_it(sec_model, s_model):
    """``result_pols()`` is S's counts and amounts, column by column, the new business
    beside them (D5).

    ``IP_UK_S`` has no ``result_pols``: its counts are cells, some in ``result_states``,
    which T1 compares at every month.  So the report is compared here with S's cells, on
    the twins S projects from the valuation date, its new business and its two claims on
    the exit basis, each at offset 0: every column but ``pols_new_biz`` is S's cell of its
    name, the benefit and the premium included, to 1e-9 relative with no absolute floor,
    and ``pols_new_biz`` holds the count in the issue month and 0 in every other.  The
    counts and amounts carry no inflation, so the shipped assumptions serve.  The claim on
    the active-lives basis, which S lapses on its restarted clock, has a test of its own.
    """
    table = sec_model.Data.model_point_table()
    twins = table.index[table["row_kind"] == "twin"].tolist()
    assert twins == sorted(s_model.Data.model_point_table().index)
    for point_id in (1, 2, 3, 4, 5, 6):
        p, s = _point(sec_model, point_id), _point(s_model, point_id)
        pols = p.result_pols()
        assert list(pols.columns)[:2] == ["pols_if", "pols_new_biz"]
        assert len(pols) == s.proj_len(), point_id
        for column in RESULT_POLS:
            if column == "pols_new_biz":
                continue
            theirs = [s.cells[column](t) for t in pols.index]
            bad = [t for t, (a, b) in enumerate(zip(theirs, pols[column]))
                   if not abs(a - b) <= 1e-9 * max(abs(a), abs(b))]
            assert not bad, (point_id, column, bad[:5])
        issue = -int(table.at[point_id, "duration_mth"])
        assert list(pols["pols_new_biz"]) == [
            p.policy_count() if t == issue else 0.0 for t in pols.index], point_id


# What T4 multiplies the counts by: not a whole number, because a count of policies need
# not be one, so that a flow which read the count as whole policies would not follow it.
COUNT_FACTOR = 2.5

# Every assumption that ships idle or neutral switched on, for T4, at the shipped inflation:
# the main splice set's (MAIN), but its inflation of 0.
SWITCHED_ON = {ref: value for ref, value in MAIN.items() if ref != "inflation_rate"}


def _pairs(want, got):
    """The values a counted cell holds, as pairs: its two numbers, or a cohort vector's
    elements, which must be as many."""
    if isinstance(want, tuple):
        assert isinstance(got, tuple) and len(got) == len(want)
        return list(zip(want, got))
    return [(want, got)]


@pytest.mark.parametrize("grid", GRIDS)
def test_scaling_the_counts_scales_every_flow_and_no_per_policy_value(tmp_path, grid):
    """The count is the weight: 2.5 times it, 2.5 times every flow, the same per policy.

    The committed table, and a copy with every ``policy_count`` multiplied by
    :data:`COUNT_FACTOR`, are each read with :data:`SWITCHED_ON` set before either computes
    anything: every assumption that ships idle or neutral, on, so that the escalation lapse
    shock moves the lapses, the cycle overlay the inceptions and the recoveries, and the
    amount payable and the severity the benefit.  The shares and the amounts of the opening
    state are per policy, and stay.  On every point ``result_cf``, the counts of
    ``result_pols`` and every column of ``result_states`` but its rates are 2.5 times the
    committed table's, element by element, to 1e-12 relative: a scaled count is a computed
    float, which may come back from the CSV within two ulps (``uk_sec_support``'s module
    docstring).  ``result_pols``'s per-policy columns are the committed table's exactly.
    So is every other cell of :data:`COUNTED`, at every argument the sweep of the committed
    table's point cached, the present value among them: the counts at each timing, the
    cohort vector element by element, the transitions out of each state and the claims of
    each kind, which no report shows, and the two residuals, roundings about 0 on that many
    policies, to their floor of 1e-9.  And every cell outside :data:`COUNTED` (the shares,
    the benefit, the premium, the rates, both clocks, the flags) agrees bit for bit at
    every argument that sweep cached, but the annuity factor, the present value over the
    count, a ratio of two scaled floats, which agrees to 1e-12.  So a flow that dropped the
    count, or read it as whole policies, which a table of counts of 1 hides from every
    comparison with S and a count doubled hides here, fails (USLIB-SEC-PLAN.md §5.2, T4,
    precised at M11).  Each counted cell but the residuals is nonzero on some point; the
    death and lapse claims are zero on every point by design, the product paying no death
    benefit and no surrender value.

    The default run takes :data:`CORE_POINTS`, among which every counted cell is nonzero,
    and the full grid the other committed points.
    """
    table = _committed()
    base = mx.read_model(_sec_inputs(tmp_path / "base", table), name=_name("counted"))
    scaled = mx.read_model(_sec_inputs(tmp_path / "scaled", table.assign(
        policy_count=COUNT_FACTOR * table["policy_count"])), name=_name("scaled"))
    reports = ("result_cf", "result_states", "result_pols")
    counted = sorted(COUNTED - set(reports))
    per_policy = {"result_pols": PER_POLICY_POLS,
                  "result_states": ["inception_rate", "mort_rate", "lapse_rate"],
                  "result_cf": []}
    nonzero = set()
    try:
        for model in (base, scaled):
            for ref, value in SWITCHED_ON.items():
                setattr(model.Projection, ref, value)
        for key, scaled_key, label in zip(point_keys(base), point_keys(scaled), table.index):
            if not _on_grid(grid, label):
                continue
            one, many = projection(base, key), projection(scaled, scaled_key)
            sweep(one)
            one.pv_benefits()
            one.annuity_dis()
            for report in reports:
                b, d = one.cells[report](), many.cells[report]()
                assert d.index.equals(b.index) and list(d.columns) == list(b.columns)
                flows = [c for c in b.columns if c not in per_policy[report]]
                want = COUNT_FACTOR * b[flows]
                bad = ((d[flows] - want).abs() > 1e-12 * want.abs()).any()
                assert not bad.any(), (key, report, list(bad[bad].index))
                fixed = per_policy[report]
                assert d[fixed].equals(b[fixed]), (key, report)
            for name in counted:
                floor = 1e-9 if name in RESIDUALS else 0.0
                for args in _cached_args(one.cells[name]):
                    for one_value, got in _pairs(one.cells[name](*args),
                                                 many.cells[name](*args)):
                        want = COUNT_FACTOR * one_value
                        assert abs(got - want) <= floor + 1e-12 * abs(want), (
                            key, name, args, got, want)
                        if want != 0.0 and name not in RESIDUALS:
                            nonzero.add(name)
            assert twin_mismatches(one, many, exempt=TWIN_EXEMPT_DEFAULT | COUNTED
                                   | {"annuity_dis"}, rtol=0.0, atol=0.0) == []
            assert many.annuity_dis() == pytest.approx(one.annuity_dis(), rel=1e-12, abs=0)
            _release(base, key)
            _release(scaled, scaled_key)
    finally:
        scaled.close()
        base.close()
    if grid == "core":
        want = set(counted) - RESIDUALS - {"pols_sick_dur"}
        assert want <= nonzero, f"0 on every core point: {sorted(want - nonzero)}"


def _restated_a_month_on(p, label):
    """Point ``p``'s row as this model carries it into month 1, under ``label``: its count,
    healthy share and cohorts at the start of month 1, before its events, and the benefit
    and premium of month 0, entering month 1.  ``(the table's row, the cohorts' rows)``."""
    count = p.pols_if_at(1, _code(p, "BEF_NB"))
    cohorts = pd.DataFrame(
        [{"point_id": label, "z": z, "pols_sick_dur_init": held / count}
         for z, held in enumerate(p.sick_cohorts(1), start=1) if held != 0.0],
        columns=["point_id", "z", "pols_sick_dur_init"])
    return {"duration_mth": p.duration_mth(1), "policy_count": count,
            "pols_active_init": p.pols_active(1) / count,
            "benefit_pp_init": p.benefit_pp(0), "premium_pp_init": p.premium_pp(0)}, cohorts


def test_a_point_restated_a_month_on_continues_its_own_flows(tmp_path):
    """The counts a point carries into a month are the counts that weight its flows (T4).

    Scaling the count, as the test above does, cannot see a flow weighted by the count a
    point opened with, ``policy_count()``, rather than the count in force in its month, nor
    one weighted by the healthy or the sick count of the valuation date: each moves by the
    same factor.  So each point in force on the committed table is restated a month on,
    opened with what this model carries into its month 1: the count,
    ``pols_if_at(1, "BEF_NB")``, the healthy share and the cohorts at the start of month 1,
    over that count, and the benefit and premium of month 0, entering month 1.  The
    restatement must continue the point's own frames, its row ``t`` the point's row
    ``t + 1``, in ``result_cf``, ``result_states`` and ``result_pols``, every flow among
    them, to 1e-9 relative, floored at 1e-9 for what a state read back from the CSV an ulp
    off moves about 0.  The point valued on its first anniversary takes no step at its
    restated month 0, and the one valued a month before an anniversary steps there.  Both
    models run at an inflation rate of 0, set on each as it is read (K7): the restatement
    moves the valuation date a month on, and expense inflation, on the valuation clock,
    would step a month apart by design (D7).  The restatement also shows the opening state
    complete on this model's own states, as the splice shows it on S's.
    """
    table = _committed()
    model = mx.read_model(_sec_inputs(tmp_path / "base", table), name=_name("month_on"))
    model.Projection.inflation_rate = 0.0
    rows, held, pairs = [], [_committed_cohorts()], []
    try:
        top = table.index.max()
        for label in table.index[table["duration_mth"] > 0]:
            p = _point(model, label)
            if p.proj_len() < 2:
                continue
            top += 1
            state, cohorts = _restated_a_month_on(p, top)
            row = table.loc[[label]].assign(**state)
            row.index = pd.Index([top], name="point_id")
            rows.append(row)
            held.append(cohorts)
            pairs.append((label, top))
        frames = {label: {report: _point(model, label).cells[report]()
                          for report in ("result_cf", "result_states", "result_pols")}
                  for label, _ in pairs}
    finally:
        model.close()
    assert len(pairs) >= 10, pairs
    restated = mx.read_model(_sec_inputs(tmp_path / "on", pd.concat([table, *rows]),
                                         pd.concat(held, ignore_index=True)),
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


@pytest.mark.parametrize("grid", GRIDS)
def test_the_checks_close_on_ten_million_policies(tmp_path, grid):
    """``check_pols_roll_fwd`` and ``check_states`` scale their tolerance with the
    policies on the books, and close at 1e7.

    A residual is rounding on that many policies, so each check holds it to 1e-10 times
    ``max(policy_count(), 1)``, where its tolerance unscaled would be 1e-10: at the counts
    the other tests use, one policy or less, the two are one.  ``IP_UK_S`` scales by
    ``pols_if_init()``, which here is 0 on a point issued at the valuation date, the count
    entering as new business.  So every committed point is projected from a copy where
    each counts ten million policies: both checks close on each, and the largest residual
    of each check exceeds the unscaled 1e-10 on some point, so the scaling is what closes
    it (USLIB-SEC-PLAN.md §5.2, T4, precised at M10).

    The default run takes :data:`CORE_POINTS`, the point issued later among them, and the
    full grid the other committed points.
    """
    table = _committed().assign(policy_count=1e7)
    model = mx.read_model(_sec_inputs(tmp_path, table), name=_name("ten_million"))
    largest = {"check_pols_roll_fwd_resid": 0.0, "check_states_resid": 0.0}
    try:
        for key, point_id in zip(point_keys(model), table.index):
            if not _on_grid(grid, point_id):
                continue
            p = projection(model, key)
            assert p.check_pols_roll_fwd() and p.check_states(), point_id
            for resid in largest:
                largest[resid] = max(largest[resid], max(
                    abs(p.cells[resid](t)) for t in range(p.proj_len())))
            _release(model, key)
    finally:
        model.close()
    assert all(value > 1e-10 for value in largest.values()), largest


# ---------------------------------------------------------------------------
# T5 -- validation
#
# Each malformed table is the committed one with one fault.  The checks run over the whole
# table as it is read, in Data, and the message names the file it read and the column or
# every point at fault.  A blank cell reads as NaN, and so does a text cell once the checks
# coerce the column to numbers, so each is refused as a count, a duration or a state that
# is not a number.  The repeated point_id holds another policy under the same label, as a
# bad extract would, so that the check must look at the labels and not at whole rows.  The
# point_ids are the committed table's: 1 to 7 the twins of S's points, 2, 5 and 7 in claim
# on their policy clocks of 12, 36 and 12 months; 8, the anchor cell on its first
# anniversary; 9, at 60; 10, at 359; 11, the claim from duration 0 at 24; 12, the claim
# from duration 30 at 6; 13, the claim on the active-lives basis at 12; 14, the female cell
# at 13; 15, the older male cell at 118; 16, the level cell at 30; 17, the female cell issued
# 13 months on; 18, the anchor cell at 40 under an RPI of 5%; 19, the female cell at 30
# under 12%.  A {file} in a message is the table's filename: every case is read by one
# model, from a file of its own (the malformed fixture).


def _drop(column):
    return lambda table: table.drop(columns=column)


_NOT_YET = "on a policy not yet in force, duration_mth 0 or less; it is not at point_id"
_FIRST_YEAR = ("on a policy in force 12 months or fewer, whose amounts are its first policy "
               "year's, the first anniversary's increase being the projection's; it is not "
               "at point_id")
_LEVEL = "on a point without escalation, which never escalates; it is not at point_id"
_RPI = ("or more, to half a cent, on a point with RPI escalation, each increase being "
        "floored at 0; it is not at point_id")
_SHARE_RULE = "must be a number from 0 to 1, a share of the count; it is not at point_id"

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
    ("a blank duration", _set("duration_mth", [17], float("nan")),
     "{file}: duration_mth must be a whole number of months; it is not at point_id [17]"),
    ("a text duration", _set("duration_mth", [11], "x36"),
     "{file}: duration_mth must be a whole number of months; it is not at point_id [11]"),
    # numpy casts a float past int64 to the least int64, a policy issued 2**63 months on,
    # without a word: the table refuses it first.
    ("a duration past int64", _set("duration_mth", [8], 1e19),
     "{file}: duration_mth must be below 2**53 months; it is not at point_id [8]"),
    ("durations of 2**53 months at two points", _set("duration_mth", [8, 10], 2.0 ** 53),
     "{file}: duration_mth must be below 2**53 months; it is not at point_id [8, 10]"),
    ("issued beyond the horizon", _set("duration_mth", [17], -121),
     "{file}: duration_mth must be -120 or more, a policy issued at most 120 months after "
     "the valuation date; it is not at point_id [17]"),
    *[(f"no {column} column", _drop(column), f"{{file}} has no {column} column")
      for column in ("policy_count", "duration_mth", *STATE)],
    ("a repeated point_id",
     lambda t: pd.concat([t, t.loc[[8]].assign(policy_id="IP-900099")]),
     "{file}: point_id [8] appears more than once"),
    ("a negative healthy share", _set("pols_active_init", [9], -0.01),
     f"{{file}}: pols_active_init {_SHARE_RULE} [9]"),
    ("a healthy share past 1", _set("pols_active_init", [9], 1.01),
     f"{{file}}: pols_active_init {_SHARE_RULE} [9]"),
    ("a blank healthy share", _set("pols_active_init", [13], float("nan")),
     f"{{file}}: pols_active_init {_SHARE_RULE} [13]"),
    ("a text healthy share", _set("pols_active_init", [16], "most"),
     f"{{file}}: pols_active_init {_SHARE_RULE} [16]"),
    ("an infinite healthy share", _set("pols_active_init", [9], float("inf")),
     f"{{file}}: pols_active_init {_SHARE_RULE} [9]"),
    ("a negative benefit", _set("benefit_pp_init", [9], -1.0),
     "{file}: benefit_pp_init must be a number, zero or more; it is not at point_id [9]"),
    ("a blank benefit", _set("benefit_pp_init", [14], float("nan")),
     "{file}: benefit_pp_init must be a number, zero or more; it is not at point_id [14]"),
    ("a text benefit", _set("benefit_pp_init", [18], "high"),
     "{file}: benefit_pp_init must be a number, zero or more; it is not at point_id [18]"),
    ("an infinite benefit", _set("benefit_pp_init", [10], float("inf")),
     "{file}: benefit_pp_init must be a number, zero or more; it is not at point_id [10]"),
    ("a negative premium", _set("premium_pp_init", [14], -1.0),
     "{file}: premium_pp_init must be a number, zero or more; it is not at point_id [14]"),
    ("a blank premium", _set("premium_pp_init", [9], float("nan")),
     "{file}: premium_pp_init must be a number, zero or more; it is not at point_id [9]"),
    ("an infinite premium", _set("premium_pp_init", [19], float("inf")),
     "{file}: premium_pp_init must be a number, zero or more; it is not at point_id [19]"),
    ("an unknown sex", _set("sex", [1], "X"),
     "{file}: sex must be M or F; it is not at point_id [1]"),
    ("an unknown escalation", _set("escalation", [4], "LPI"),
     "{file}: escalation must be RPI or none; it is not at point_id [4]"),
    # IP_UK_S checks the premium basis in a cell no formula calls, so it projects a
    # reviewable premium as guaranteed.
    ("a reviewable premium", _set("premium_basis", [3], "reviewable"),
     "{file}: premium_basis must be guaranteed; it is not at point_id [3]"),
    ("an unknown status", _set("status", [2], "claim"),
     "{file}: status must be active or in_claim; it is not at point_id [2]"),
    ("an unknown recovery basis", _set("recovery_basis", [7], "return"),
     "{file}: recovery_basis must be return_to_h or exit; it is not at point_id [7]"),
    ("an occupation class of 5", _set("occ_class", [1], 5),
     "{file}: occ_class must be a whole number from 1 to 4; it is not at point_id [1]"),
    ("an occupation class of 0", _set("occ_class", [6], 0),
     "{file}: occ_class must be a whole number from 1 to 4; it is not at point_id [6]"),
    ("an occupation class not whole", _set("occ_class", [4], 2.5),
     "{file}: occ_class must be a whole number from 1 to 4; it is not at point_id [4]"),
    ("an occupation class written as text", _set("occ_class", [3], "OC1"),
     "{file}: occ_class must be a whole number from 1 to 4; it is not at point_id [3]"),
    ("a blank occupation class", _set("occ_class", [5], float("nan")),
     "{file}: occ_class must be a whole number from 1 to 4; it is not at point_id [5]"),
    ("a deferred period off the menu", _set("deferred_weeks", [1], 6),
     "{file}: deferred_weeks must be 4, 8, 13, 26 or 52; it is not at point_id [1]"),
    ("a blank deferred period", _set("deferred_weeks", [4], float("nan")),
     "{file}: deferred_weeks must be 4, 8, 13, 26 or 52; it is not at point_id [4]"),
    ("a deferred period written as text", _set("deferred_weeks", [6], "26w"),
     "{file}: deferred_weeks must be 4, 8, 13, 26 or 52; it is not at point_id [6]"),
    ("a blank entry age", _set("entry_age", [1], float("nan")),
     "{file}: entry_age must be a finite number; it is not at point_id [1]"),
    ("an infinite entry age", _set("entry_age", [5], float("inf")),
     "{file}: entry_age must be a finite number; it is not at point_id [5]"),
    ("a text entry age", _set("entry_age", [7], "x34"),
     "{file}: entry_age must be a finite number; it is not at point_id [7]"),
    ("an entry age of 2**53", _set("entry_age", [3], 2.0 ** 53),
     "{file}: entry_age must be below 2**53 in size; it is not at point_id [3]"),
    ("a blank expiry age", _set("expiry_age", [6], float("nan")),
     "{file}: expiry_age must be a finite number; it is not at point_id [6]"),
    ("a text expiry age", _set("expiry_age", [2], "65y"),
     "{file}: expiry_age must be a finite number; it is not at point_id [2]"),
    ("a negative benefit at issue", _set("benefit_mth", [1], -1.0),
     "{file}: benefit_mth must be a number, zero or more; it is not at point_id [1]"),
    ("text earnings", _set("earnings_annual", [4], "40k"),
     "{file}: earnings_annual must be a number, zero or more; it is not at point_id [4]"),
    ("an infinite premium at issue", _set("premium_mth", [6], float("inf")),
     "{file}: premium_mth must be a number, zero or more; it is not at point_id [6]"),
    ("lives in claim on new business", _set("pols_active_init", [1], 0.9),
     "{file}: pols_active_init must be 1 on a policy not yet in force, duration_mth 0 or "
     "less, which is issued healthy; it is not at point_id [1]"),
    ("lives in claim on future business", _set("pols_active_init", [17], 0.0),
     "{file}: pols_active_init must be 1 on a policy not yet in force, duration_mth 0 or "
     "less, which is issued healthy; it is not at point_id [17]"),
    ("a benefit on new business", _set("benefit_pp_init", [3], 2100.0),
     f"{{file}}: benefit_pp_init must be the benefit at issue {_NOT_YET} [3]"),
    ("a premium on future business", _set("premium_pp_init", [17], 60.0),
     f"{{file}}: premium_pp_init must be the premium at issue {_NOT_YET} [17]"),
    # No anniversary has passed in a policy's first twelve months: the female cell at 13,
    # moved back to its first anniversary with its first increase, and the anchor cell on
    # its first anniversary given the increase that anniversary makes, read after month
    # 0's step, where the columns are measured before it.
    ("a benefit in the first policy year", _set("duration_mth", [14], 12),
     f"{{file}}: benefit_pp_init must be the benefit at issue {_FIRST_YEAR} [14]"),
    ("a benefit on the first anniversary", _set("benefit_pp_init", [8], 2060.0),
     f"{{file}}: benefit_pp_init must be the benefit at issue {_FIRST_YEAR} [8]"),
    ("a premium on the first anniversary", _set("premium_pp_init", [8], 36.575),
     f"{{file}}: premium_pp_init must be the premium at issue {_FIRST_YEAR} [8]"),
    # The first year's history at its first month: an increase a month after issue.
    ("a premium a month after issue",
     _then(_set("duration_mth", [8], 1), _set("premium_pp_init", [8], 36.575)),
     f"{{file}}: premium_pp_init must be the premium at issue {_FIRST_YEAR} [8]"),
    ("a level benefit moved", _set("benefit_pp_init", [16], 2001.0),
     f"{{file}}: benefit_pp_init must be the benefit at issue {_LEVEL} [16]"),
    ("a level premium moved", _set("premium_pp_init", [16], 35.5),
     f"{{file}}: premium_pp_init must be the premium at issue {_LEVEL} [16]"),
    ("a level claim's benefit moved", _set("benefit_pp_init", [11], 2060.0),
     f"{{file}}: benefit_pp_init must be the benefit at issue {_LEVEL} [11]"),
    # An escalated amount a cent below the amount at issue, which half a cent's slack, for
    # an extract rounded to the cent, does not admit.
    ("an escalated benefit a cent below the benefit at issue",
     _set("benefit_pp_init", [9], 1999.99),
     f"{{file}}: benefit_pp_init must be the benefit at issue {_RPI} [9]"),
    ("an escalated premium a cent below the premium at issue",
     _set("premium_pp_init", [9], 34.99),
     f"{{file}}: premium_pp_init must be the premium at issue {_RPI} [9]"),
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
    """``message`` with every point it names relabelled by ``relabel``, a label it does not
    hold left as it is: each ``point_id [...]`` list, and each ``point_id p z``, the
    companion's key."""
    def one(p):
        return str(relabel.get(int(p), int(p)))

    def labels(match):
        return "point_id [" + ", ".join(one(p) for p in match.group(1).split(", ")) + "]"
    message = re.sub(r"point_id \[(\d+(?:, \d+)*)\]", labels, message)
    return re.sub(r"point_id (\d+) z ", lambda m: f"point_id {one(m.group(1))} z ", message)


# The labels an extract carries in the tests below: the committed points' in reverse, from
# 100 plus their number down to 101, so that a label is neither a position plus one nor in
# the order of the rows.
EXTRACT_LABELS = tuple(range(100 + len(_committed()), 100, -1))


def _relabel_map():
    """``{committed label: extract label}``."""
    return dict(zip(_committed().index, EXTRACT_LABELS))


@pytest.fixture(scope="module")
def malformed_extract(tmp_path_factory):
    """:data:`MALFORMED`'s tables as an extract labels its rows, each a file of its own.

    Each case's table is the committed one with its fault, made by its own labels, and
    then relabelled :data:`EXTRACT_LABELS`, in order, so that no label is its position
    plus one.  One model reads them all, as :func:`malformed` reads its files.  Returns
    ``(model, {case: filename}, {committed label: extract label})``.
    """
    root = tmp_path_factory.mktemp("malformed_extract")
    relabel = _relabel_map()
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


def _cell(row, column, value):
    """An edit that writes ``value`` into ``column`` on row ``row``, line ``row + 2``."""
    def edit(table):
        cells = table[column].astype(object)
        cells.iloc[row] = value
        return table.assign(**{column: cells})
    return edit


def _extra(**row):
    """An edit that appends a row of its own, on the line after the last."""
    return lambda table: pd.concat([table, pd.DataFrame([row])], ignore_index=True)


def _without(point):
    """An edit that drops every row of ``point``."""
    return lambda table: table[table["point_id"] != point].reset_index(drop=True)


def _sum_off(point, by):
    """An edit that moves ``point``'s largest cohort share by ``by``, so that its shares
    and its healthy share sum to ``1 + by``, within the float of it."""
    def edit(table):
        table = table.copy()
        mine = table.index[table["point_id"] == point]
        at = table.loc[mine, "pols_sick_dur_init"].idxmax()
        table.loc[at, "pols_sick_dur_init"] = table.at[at, "pols_sick_dur_init"] + by
        return table
    return edit


def _past_one(points):
    """What ``Data.inforce_cohorts()`` says of ``points``, whose shares do not sum to 1."""
    return (f"{{file}}: a point's pols_active_init and its pols_sick_dur_init must sum to "
            f"1 within 1e-10, shares of one count; they do not at point_id {points}")


_Z_RANGE = ("{file}: z must be from 1 to its point's duration_mth, the months since issue "
            "at the valuation date; it is not on line ")
_IN_FORCE = ("{file}: a row's point must be in force, duration_mth above 0: a point not yet "
             "in force is issued healthy; it is not on line ")
_COHORT_SHARE = ("{file}: pols_sick_dur_init must be a number from 0 to 1, a share of the "
                 "count; it is not on line ")

# The claim cohorts with one fault each, as (case, the edit of the committed file, the
# message), {file} in a message the companion's filename.  The committed file holds, by
# line, the header line 1: the twins of S's claims, point 2's cohort z 1 on line 2, point
# 5's z 31 on line 3 and point 7's z 1 on line 4; point 8's cohorts z 1 to 12 on lines 5 to
# 16; point 9's z 1 to 60 on lines 17 to 76; point 10's, 359 of them, on lines 77 to 435;
# point 11's z 25 on line 436; point 12's z 37 on line 437; point 13's z 1 to 11 and 13 on
# lines 438 to 449; then points 14, 15, 16, 18 and 19, to line 680.
MALFORMED_COHORTS = [
    *[(f"no {column} column", (lambda t, c=column: t.drop(columns=c)),
       f"{{file}} has no {column} column")
      for column in ("point_id", "z", "pols_sick_dur_init")],
    ("a fractional point_id", _cell(0, "point_id", 2.5),
     "{file}: point_id must be a whole number; it is not on line [2]"),
    ("a text z", _cell(1, "z", "thirty-one"),
     "{file}: z must be a whole number; it is not on line [3]"),
    ("a blank z", _cell(7, "z", float("nan")),
     "{file}: z must be a whole number; it is not on line [9]"),
    ("a z past int64", _cell(2, "z", 1e19),
     "{file}: z must be below 2**53 in size; it is not on line [4]"),
    ("a point the table lacks", _extra(point_id=99, z=1, pols_sick_dur_init=0.0),
     f"{{file}}: point_id [99] on line [681] is no point of {TABLE}"),
    ("a z twice", _extra(point_id=9, z=5, pols_sick_dur_init=0.0),
     "{file}: each point_id and z must have one row; point_id 9 z 5 is on line [21, 681]"),
    ("a claim on new business", _extra(point_id=1, z=1, pols_sick_dur_init=0.0),
     _IN_FORCE + "[681]"),
    ("a claim on future business", _extra(point_id=17, z=1, pols_sick_dur_init=0.0),
     _IN_FORCE + "[681]"),
    ("a z of 0", _cell(0, "z", 0), _Z_RANGE + "[2]"),
    ("a claim older than its policy", _cell(0, "z", 13), _Z_RANGE + "[2]"),
    ("a claim duration past the policy's at a later point",
     _extra(point_id=12, z=43, pols_sick_dur_init=0.0), _Z_RANGE + "[681]"),
    ("a negative cohort share", _cell(4, "pols_sick_dur_init", -0.01),
     _COHORT_SHARE + "[6]"),
    ("a cohort share past 1", _cell(8, "pols_sick_dur_init", 1.5),
     _COHORT_SHARE + "[10]"),
    ("a blank cohort share", _cell(9, "pols_sick_dur_init", float("nan")),
     _COHORT_SHARE + "[11]"),
    ("an infinite cohort share", _cell(3, "pols_sick_dur_init", float("inf")),
     _COHORT_SHARE + "[5]"),
    # The shares' tolerance, 1e-10, pinned from outside on each side; the edges test
    # accepts each side just inside it.
    ("shares past 1 by 1.1e-10", _sum_off(13, 1.1e-10), _past_one([13])),
    ("shares short of 1 by 1.1e-10", _sum_off(9, -1.1e-10), _past_one([9])),
    ("a claim's cohort lost", _without(11), _past_one([11])),
    ("one of several cohorts lost",
     lambda t: t.drop(index=t.index[(t["point_id"] == 13) & (t["z"] == 13)]).reset_index(
         drop=True), _past_one([13])),
    ("two points' shares off", _then(_sum_off(13, 1e-3), _sum_off(18, 1e-6)),
     _past_one([13, 18])),
]


@pytest.fixture(scope="module")
def malformed_cohorts(tmp_path_factory):
    """One model, and beside it every companion of :data:`MALFORMED_COHORTS`, each a file
    of its own, read as the committed table's claim cohorts in turn; and the same as an
    extract labels its rows, table and companion relabelled alike
    (:data:`EXTRACT_LABELS`).  Returns ``{"committed": (model, files), "extract": (model,
    files, relabel)}``.
    """
    root = tmp_path_factory.mktemp("malformed_cohorts")
    relabel = _relabel_map()
    out = {}
    for tag in ("committed", "extract"):
        files = {}
        for number, (case, edit, _) in enumerate(MALFORMED_COHORTS):
            files[case] = f"{tag}_cohorts_{number:02d}_sec.csv"
            frame = edit(_committed_cohorts())
            if tag == "extract" and "point_id" in frame:
                frame = frame.assign(point_id=frame["point_id"].map(
                    lambda p: relabel.get(p, p)))
            temp_inputs(root / tag, model_path(SEC), model_points=frame,
                        model_point_file=files[case])
        # Last, since each copy writes the committed CSVs over the folder's.
        table = _committed() if tag == "committed" else _committed().rename(index=relabel)
        temp_inputs(root / tag, model_path(SEC), model_points=table, model_point_file=TABLE)
        model = mx.read_model(root / tag / SEC, name=_name(f"cohorts_{tag}"))
        out[tag] = (model, files)
    out["extract"] = (*out["extract"], relabel)
    yield out
    for tag in ("committed", "extract"):
        out[tag][0].close()


@pytest.mark.parametrize("case, edit, message", MALFORMED_COHORTS,
                         ids=[c[0] for c in MALFORMED_COHORTS])
def test_malformed_claim_cohorts_are_refused_naming_their_lines(malformed_cohorts, case,
                                                                 edit, message):
    """``Data.inforce_cohorts()`` refuses the companion, naming the fault and its lines or
    its points, and so does a projection of a point in force that reads it (D6, D8, T5);
    and on an extract labelled otherwise, table and companion alike, each refusal names the
    extract's labels.

    The checks are :func:`IP_UK_SEC.Data.inforce_cohorts`'s eight rules: the columns; keys
    whole and below ``2**53``; a point of the table; one row a point and duration; a point
    in force, since a point not yet in force is issued healthy; a duration from 1 to the
    point's months in force; a share from 0 to 1; and the healthy share and the cohort
    shares summing to 1 within 1e-10, on every point in force, a point holding no row
    among them, which is all healthy.  ``IP_UK_S`` has no companion: it seeds one cohort
    from its ``claim_duration_months``.
    """
    model, files = malformed_cohorts["committed"]
    model.Data.inforce_cohorts_file = files[case]
    _refused(model.Data.inforce_cohorts, message.format(file=files[case]))
    _refused(_point(model, 9).result_cf, message.format(file=files[case]))
    model, files, relabel = malformed_cohorts["extract"]
    model.Data.inforce_cohorts_file = files[case]
    _refused(model.Data.inforce_cohorts,
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


def test_a_point_past_its_policy_end_date_is_refused_by_proj_len(tmp_path):
    """A point at or past its policy end date has no frame, and ``proj_len()`` refuses it.

    The anchor cell valued at 60 is moved on to ``duration_mth`` 360, the policy month
    cover ends at, from entry at 35 to expiry at 65, on the policy clock.  That is a rule of
    the product, not of the table: it needs the expiry age and the entry age the point's
    own columns give, read where the frame is defined, so the table and its cohorts read,
    and the point is refused on its first projection, rather than projecting nothing.  A
    loop over the block would meet the point only when it reached it, after projecting the
    points before it, so ``run_sec.py --block``, run beside the table, asks every point for
    its frame first: it fails naming the point, and prints nothing before.  And one month
    earlier, 359, the last covered month, projects one month.
    """
    moved = _label(_committed(), "derived", 1, 60)
    model = _read_edited(tmp_path, _set("duration_mth", [moved], 360))
    message = (f"point_id {moved}: duration_mth 360 is at or past the policy end date, "
               f"policy month 360, expiry age 65")
    try:
        assert len(model.Data.model_point_table()) == len(_committed())
        assert len(model.Data.inforce_cohorts()) == len(_committed_cohorts())
        _refused(_point(model, moved).result_cf, message)
    finally:
        model.close()
    model = _read_edited(tmp_path / "last", _set("duration_mth", [moved], 359))
    try:
        assert len(_point(model, moved).result_cf()) == 1
    finally:
        model.close()
    runner = tmp_path / "run_sec.py"
    shutil.copy(model_path(SEC).parent / "run_sec.py", runner)
    done = _run_sec(runner, "--block", check=False)
    assert done.returncode != 0 and done.stdout == b""
    assert message in done.stderr.decode(errors="replace")


# What the contract does not issue, refused by proj_len() as a point past its policy end date
# is, as (case, the table's edit, the References set, the point, the message, and the frame
# the point projects at the shipped References, or None).  Data reads an entry and an expiry
# age as IP_UK_S does, so each reads.  The product issues from 18 to 59 and expires from 50
# to 70; the compiled caches will be sized from the youngest issue and the latest expiry.
# Each bound is refused just past it here, and accepted at it in the edges test.  And each
# bound, moved past a committed twin, refuses it, which at the shipped bound projects its
# frame: the Reference is what refuses it.  Point 1 is the anchor cell, issued at 35 to 65;
# point 4 the female cell at 42 to 60; point 6 the older male cell at 55 to 65.
NOT_ISSUED = [
    ("an issue age of 17", _set("entry_age", [3], 17), {}, 3,
     "point_id 3: the issue age, 17, is below issue_age_min, 18", None),
    ("an issue age of 60", _set("entry_age", [6], 60), {}, 6,
     "point_id 6: the issue age, 60, is above issue_age_max, 59", None),
    ("an issue age below a bound raised to 36", None, {"issue_age_min": 36}, 1,
     "point_id 1: the issue age, 35, is below issue_age_min, 36", 360),
    ("an issue age above a bound lowered to 54", None, {"issue_age_max": 54}, 6,
     "point_id 6: the issue age, 55, is above issue_age_max, 54", 120),
    ("an expiry age of 49", _set("expiry_age", [4], 49), {}, 4,
     "point_id 4: the expiry age, 49, is below expiry_age_min, 50", None),
    ("an expiry age of 71", _set("expiry_age", [1], 71), {}, 1,
     "point_id 1: the expiry age, 71, is above expiry_age_max, 70", None),
    ("an expiry age below a bound raised to 61", None, {"expiry_age_min": 61}, 4,
     "point_id 4: the expiry age, 60, is below expiry_age_min, 61", 216),
    ("an expiry age above a bound lowered to 64", None, {"expiry_age_max": 64}, 1,
     "point_id 1: the expiry age, 65, is above expiry_age_max, 64", 360),
    ("an issue age at the expiry age", _then(_set("entry_age", [6], 55),
                                             _set("expiry_age", [6], 55)), {}, 6,
     "point_id 6: the issue age, 55, is at or past the expiry age, 55: the policy has no "
     "cover", None),
]


@pytest.mark.parametrize("case, edit, refs, point, message, frame", NOT_ISSUED,
                         ids=[c[0] for c in NOT_ISSUED])
def test_a_point_the_contract_does_not_issue_is_refused_by_proj_len(tmp_path, case, edit,
                                                                    refs, point, message,
                                                                    frame):
    """``proj_len()`` refuses a point outside the contract's bounds, naming it (§6.3).

    ``IP_UK_S`` projects any entry age to any expiry age its tables reach, and so would
    modelx here, but the contract does not write it, and the compiled model's caches will be
    sized from the contract: a frame of at most 52 years and the horizon, claim durations
    to 625 months, attained ages from 18 to 69.  So the frame refuses such a point, naming
    it, as it refuses a point past its policy end date, and every report with it
    (:data:`NOT_ISSUED`): each bound just past it, and each bound moved past a committed
    twin, which projects at the shipped bound, on a model read afresh.  A bound off by one,
    or a refusal lost, lets a point through.  The table reads either way.  Every Reference
    is set on a model just read, before its projection computes anything (K7).
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


# Each Reference proj_len() holds to a domain, as (case, the References set, the point,
# the message where refused, and where an accepted edge takes a value past the floats, the
# refusal its report meets there).  NaN and the infinities are outside every domain.
# IP_UK_S reads the cycle overlay inside the inception cap's min and the recovery bound's
# min, which a NaN is lost through and a 0 divides by; the mortality factor inside the
# mortality cap's min, which reads an infinity as certain death; the RPI through a max and
# a min, max(rpi, 0.0) then the escalation cap, which read an infinity as no increase or as
# the cap; the cap as a bound written second, which a NaN cap is lost through; the lapse
# shock's threshold through a bound-first max, which a NaN is lost through; the shares and
# the expenses as weights, which below 0 or past 1 make a negative benefit, expense or rate;
# and the discount rate through a negative power, which at -1 divides by zero.  Each is
# refused at the nearest value outside each edge of its domain, and accepted at the edge
# itself, where its reports project in finite floats over the whole frame, but where the
# edge takes a value past the floats, which is refused where it first is.  The four age
# bounds are whole numbers below 2**53, which the compiled model holds as long long,
# printed through int() once whole: each is refused at a fraction and at exactly 2**53.
BIG = 1.7976931348623157e308
WHOLE = 2.0 ** 53
BELOW_0 = math.nextafter(0.0, -1.0)
ABOVE_0 = math.nextafter(0.0, 1.0)
ABOVE_1 = math.nextafter(1.0, 2.0)
BELOW_MINUS_1 = math.nextafter(-1.0, -2.0)
ABOVE_MINUS_1 = math.nextafter(-1.0, 0.0)


def _domain(ref, rule, point, accepted, refused, reports=None):
    """The DOMAINS cases of ``ref`` on ``point``: each of ``accepted`` projects, or meets
    the report refusal ``reports`` gives it, and each of ``refused`` is refused by the
    domain's ``rule``, and NaN and the infinities by it too."""
    message = f"point_id {point}: {ref} must be {rule}, not {{}}"
    reports = reports or {}
    cases = [(f"{ref}={value!r} on {point}", {ref: value}, point, None, reports.get(value))
             for value in accepted]
    return cases + [(f"{ref}={value!r} on {point}", {ref: value}, point,
                     message.format(float(value)), None)
                    for value in (*refused, math.nan, math.inf, -math.inf)]


def _whole_domain(ref, point, accepted, below=True):
    """The DOMAINS cases of an integer Reference: a whole number below 2**53, and 0 or more
    where ``below``, printed through int() once whole; each of ``accepted`` projects."""
    whole = f"point_id {point}: {ref} must be a whole number below 2**53, not {{}}"
    cases = [(f"{ref}={value!r} on {point}", {ref: value}, point, None, None)
             for value in accepted]
    if below:
        cases.append((f"{ref}=-1 on {point}", {ref: -1}, point,
                      f"point_id {point}: {ref} must be 0 or more, not -1", None))
    return cases + [(f"{ref}={value!r} on {point}", {ref: value}, point,
                     whole.format(float(value)), None)
                    for value in (0.5, 50.5, WHOLE, 1e300, math.nan, math.inf, -math.inf)]


_FINITE_0 = ("a finite number, 0 or more", (0.0, BIG), (BELOW_0,))
_SHARE = ("a number from 0 to 1", (0.0, 1.0), (BELOW_0, ABOVE_1))
_EXPIRY_MAX = ("point_id 1: expiry_age_max must be expiry_age_min, 50, or more, and at most "
               "76, a year past mort_table.csv's last age, not {}")
DOMAINS = [
    *_domain("cycle_factor", "a finite number above 0", 1, (ABOVE_0, BIG), (0.0,)),
    *_domain("mort_active_factor", *_FINITE_0[:1], 1, *_FINITE_0[1:]),
    *_domain("ap_ratio", *_SHARE[:1], 2, *_SHARE[1:]),
    *_domain("claim_severity", *_SHARE[:1], 2, *_SHARE[1:]),
    *_domain("rpi_rate", "a finite number", 1, (-BIG, BIG), ()),
    *_domain("esc_cap", *_FINITE_0[:1], 1, *_FINITE_0[1:]),
    *_domain("esc_prem_mult", *_FINITE_0[:1], 1, *_FINITE_0[1:],
             {BIG: "point_id 1: the premium premium_pp(12) is inf, not a finite number, "
                   "from premium_pp_init 35.0"}),
    *_domain("esc_lapse_slope", *_FINITE_0[:1], 1, *_FINITE_0[1:]),
    *_domain("esc_lapse_threshold", *_FINITE_0[:1], 1, *_FINITE_0[1:]),
    *_domain("ben_band1_rate", *_SHARE[:1], 6, *_SHARE[1:]),
    *_domain("ben_band2_rate", *_SHARE[:1], 6, *_SHARE[1:]),
    *_domain("ben_breakpoint", *_FINITE_0[:1], 6, *_FINITE_0[1:]),
    *_domain("ben_cap_mth", *_FINITE_0[:1], 6, *_FINITE_0[1:]),
    *_domain("ben_guarantee_mth", *_FINITE_0[:1], 6, *_FINITE_0[1:]),
    *_domain("ben_tolerance", "a number above 0 and at most 1", 6, (ABOVE_0, 1.0),
             (0.0, ABOVE_1)),
    *_domain("expense_maint", *_FINITE_0[:1], 1, *_FINITE_0[1:]),
    *_domain("expense_claim", *_FINITE_0[:1], 2, *_FINITE_0[1:]),
    *_domain("inflation_rate", "a finite number, -1 or more", 1, (-1.0, BIG),
             (BELOW_MINUS_1,),
             {BIG: "point_id 1: the expenses expenses(12) are inf, not a finite number, "
                   "from expense_maint 60.0, expense_claim 300.0 and inflation_rate "
                   f"{BIG}"}),
    *_domain("disc_rate", "a finite number above -1", 2, (ABOVE_MINUS_1, BIG), (-1.0,)),
    *_whole_domain("issue_age_min", 1, (0, 18, 18.0, 35)),
    ("issue_age_min=2**53-1 on 1", {"issue_age_min": WHOLE - 1}, 1,
     f"point_id 1: issue_age_max must be issue_age_min, {int(WHOLE - 1)}, or more, not 59",
     None),
    *_whole_domain("issue_age_max", 1, (35, 59, 59.0, int(WHOLE - 1)), below=False),
    ("issue_age_max=17 on 1", {"issue_age_max": 17}, 1,
     "point_id 1: issue_age_max must be issue_age_min, 18, or more, not 17", None),
    *_whole_domain("expiry_age_min", 1, (0, 50, 50.0, 65), below=False),
    *_whole_domain("expiry_age_max", 1, (65, 70, 70.0, 76), below=False),
    ("expiry_age_max=77 on 1", {"expiry_age_max": 77}, 1, _EXPIRY_MAX.format(77), None),
    ("expiry_age_max=49 on 1", {"expiry_age_max": 49}, 1, _EXPIRY_MAX.format(49), None),
]


@pytest.mark.parametrize("case, refs, point, message, report", DOMAINS,
                         ids=[c[0] for c in DOMAINS])
def test_each_reference_is_held_to_its_domain_at_both_edges(case, refs, point, message,
                                                            report):
    """``proj_len()`` holds each Reference to its domain, NaN and the infinities outside it.

    ``IP_UK_S`` checks none of them, and off its domain each projects a negative rate,
    benefit or expense, a factor that changes sign each year, or a NaN that a comparison
    loses, every check passing: a NaN escalation cap is lost through its ``min``, a NaN
    lapse threshold through the shock's ``max``, a NaN cycle overlay through the recovery
    rate's bound, and a NaN age bound switches off every comparison with it.  The frame
    refuses each such Reference, by name, before it projects anything, and every report with
    it, at the nearest value outside each edge of its domain (:data:`DOMAINS`), on a point
    that reads it.  Each Reference is refused on every point, whether or not the point reads
    it, as a model-wide assumption.  And the frame accepts each edge, whose reports then
    project, in finite floats over the whole frame, but where the edge takes a value past
    the floats, which is refused where it first is, naming the References.  A whole float,
    ``70.0``, reads as the whole number.  Each case sets its References on a model just read
    (K7).
    """
    model = mx.read_model(model_path(SEC), name=_name("domain"))
    try:
        for ref, value in refs.items():
            setattr(model.Projection, ref, value)
        p = _row(model, "twin", point, 0)
        if message is not None:
            _refused(p.result_cf, message)
        elif report is not None:
            assert p.proj_len() > 0
            _refused(p.result_cf, report)
        else:
            for name in ("result_cf", "result_states", "result_pols"):
                frame = p.cells[name]()
                assert list(frame.index) == list(range(p.proj_len())), (case, name)
                assert np.isfinite(frame.to_numpy(dtype=float)).all(), (case, name)
            assert p.check_pols_roll_fwd() and p.check_states(), case
    finally:
        model.close()


# A value past the floats from an opening state and References each in its domain, as
# (case, the table's edit, the References set, the point, the call, a report that reads it,
# the start of the message).  The anchor cell at 60, opened on a benefit near the largest
# float, which month 0's escalation, its sixth anniversary's, takes past it; the female
# cell at 13 on a premium near it, which its second anniversary, at t = 11, takes past it;
# a count of 1e307 paying 35 a month; the claim at 24 paying 1e300 a month on a count of
# 1e300; the claims-in-payment twin paying 1.75e308 a month beside a claim expense of the
# largest float, each finite and their sum, the net cash flow, not; the same twin's present
# value at 1e308 a month; the lapse shock under an escalation of 1e300 and a slope of 1e10;
# and the powers: the inflation factor and the benefit's and premium's steps under rates of
# 1e200, which square past the floats at the second anniversary, and the discount factor at
# a rate a hair above -1.  Each is refused in the cell where it first is, naming the point,
# the month and what makes it.
PAST_THE_FLOATS = [
    ("a benefit", _set("benefit_pp_init", [9], 1.79e308), {}, 9, ("benefit_pp", 0),
     "result_cf",
     "point_id 9: the benefit benefit_pp(0) is inf, not a finite number, from "
     "benefit_pp_init 1.79e+308 and an annual increase of 0.03"),
    ("a premium", _set("premium_pp_init", [14], 1.79e308), {}, 14, ("premium_pp", 11),
     "result_cf",
     "point_id 14: the premium premium_pp(11) is inf, not a finite number, from "
     "premium_pp_init 1.79e+308 and an annual increase of 0.045"),
    ("the premiums", _set("policy_count", [1], 1e307), {}, 1, ("premiums", 0), "result_cf",
     "point_id 1: the premiums premiums(0) are inf, not a finite number, from "
     "premium_pp(0) 35.0 on pols_active(0) 1e+307 healthy lives"),
    ("the claims",
     _then(_set("policy_count", [11], 1e300), _set("benefit_mth", [11], 1e300),
           _set("benefit_pp_init", [11], 1e300)), {}, 11, ("claims", 0, "BENEFIT"),
     "result_cf",
     "point_id 11: the claims claims(0, BENEFIT) are inf, not a finite number, from "
     "amount_payable_pp(0) 1e+300 on pols_sick_surv(0) "),
    ("the net cash flow",
     _then(_set("benefit_mth", [2], 1.75e308), _set("benefit_pp_init", [2], 1.75e308)),
     {"expense_claim": BIG}, 2, ("net_cf", 0), "result_cf",
     "point_id 2: the net cash flow net_cf(0) is -inf, not a finite number, from premiums "
     "0.0, claims "),
    ("the present value",
     _then(_set("benefit_mth", [2], 1e308), _set("benefit_pp_init", [2], 1e308)), {}, 2,
     ("pv_benefits",), "pv_benefits",
     "point_id 2: the present value pv_benefits() is inf, not a finite number, at "
     "disc_rate 0.03"),
    ("the lapse shock", None,
     {"rpi_rate": 1e300, "esc_cap": 1e300, "esc_lapse_slope": 1e10}, 1,
     ("esc_lapse_factor", 12), "result_cf",
     "point_id 1: the lapse shock esc_lapse_factor(12) is inf, not a finite number, from "
     "esc_lapse_slope 10000000000.0, esc_prem_mult 1.5 and an escalation rate of 1e+300"),
    ("the inflation factor", None, {"inflation_rate": 1e200}, 1, ("inflation_factor", 24),
     "result_cf",
     "point_id 1: the inflation factor inflation_factor(24) is past the largest float, "
     "under inflation_rate 1e+200"),
    ("the benefit's step", None, {"rpi_rate": 1e200, "esc_cap": 1e200}, 1,
     ("benefit_pp", 24), "result_pols",
     "point_id 1: the benefit benefit_pp(24) is past the largest float, from "
     "benefit_pp_init 2000.0 and an annual increase of 1e+200"),
    ("the premium's step", None, {"rpi_rate": 1e200, "esc_cap": 1e200}, 1,
     ("premium_pp", 24), "result_cf",
     "point_id 1: the premium premium_pp(24) is past the largest float, from "
     "premium_pp_init 35.0 and an annual increase of 1.5e+200"),
    ("the discount factor", None, {"disc_rate": ABOVE_MINUS_1}, 2, ("disc_factor", 231),
     "pv_benefits",
     "point_id 2: the discount factor disc_factor(231) is past the largest float, under "
     "disc_rate -0.9999999999999999"),
]


@pytest.mark.parametrize("case, edit, refs, point, call, report, message", PAST_THE_FLOATS,
                         ids=[c[0] for c in PAST_THE_FLOATS])
def test_a_value_past_the_floats_is_refused_where_it_first_is(tmp_path, case, edit, refs,
                                                              point, call, report, message):
    """A value past the largest float is refused in the cell where it first is.

    ``Data`` and ``proj_len()`` hold each opening amount, count and Reference to a finite
    number, so a value near the largest float reads; an escalation, a premium, a count, a
    rate or a sum then takes a value the projection computes past the floats, where
    ``IP_UK_S`` would pay an infinite benefit, charge an infinite expense or discount by an
    infinite factor, every report infinite and its checks NaN or passing, or where a power
    raises Python's ``OverflowError``, naming nothing.  The cell where the value first
    leaves the floats refuses it, naming the point, the month and what makes it
    (:data:`PAST_THE_FLOATS`), and so does a report that reads it first: ``result_cf``, or
    ``result_pols`` for the benefit's step, which no cash flow reads before the premium's,
    or ``pv_benefits`` for the discount factor, which no report reads
    (USLIB-SEC-PLAN.md §7.1, *Record — M1*; UKLIB-SEC-PLAN.md §6.6, *Carried into M10 and
    after*; §6.7, *Record — M11*).  The month before projects.  Each Reference is set on a
    model just read (K7).
    """
    model = _read_edited(tmp_path, edit or (lambda t: t))
    try:
        for ref, value in refs.items():
            setattr(model.Projection, ref, value)
        p = _point(model, point)
        name, *args = call
        if args and args[0] > 0:
            p.cells[name](args[0] - 1, *args[1:])
        _refused(lambda: p.cells[name](*args), message)
        _refused(p.cells[report], message)
    finally:
        model.close()


@pytest.mark.parametrize("grid", GRIDS)
def test_a_whole_bound_written_as_a_float_projects_as_the_int_does(grid):
    """The four age bounds written as floats project what the ints project, cell for cell.

    ``proj_len()`` holds ``issue_age_min``, ``issue_age_max``, ``expiry_age_min`` and
    ``expiry_age_max`` to whole numbers, which ``18.0``, ``59.0``, ``50.0`` and ``70.0`` are,
    and compares each with an ``int`` age, which a compiled model typing the Reference
    ``long long`` would too.  So with the four set as floats, on a model just read, the
    twins of S's anchor cell and of its claims-in-payment cell, the anchor cell in force at
    60 and the female cell issued later are what the shipped model makes of them in every
    cell, bit for bit, each integer cell an ``int`` in both.

    The twin of the anchor cell and the anchor cell in force run by default, and the claim's
    twin and the point issued later with the full grid.
    """
    floats = mx.read_model(model_path(SEC), name=_name("floats"))
    ints = mx.read_model(model_path(SEC), name=_name("ints"))
    try:
        for ref, value in (("issue_age_min", 18.0), ("issue_age_max", 59.0),
                           ("expiry_age_min", 50.0), ("expiry_age_max", 70.0)):
            setattr(floats.Projection, ref, value)
        cases = ((("twin", 1, 0), ("derived", 1, 60)) if grid == "core"
                 else (("twin", 2, 0), ("future", 4, -13)))
        for case in cases:
            mine, theirs = _row(floats, *case), _row(ints, *case)
            sweep(theirs)
            assert twin_mismatches(theirs, mine, exempt=frozenset(), rtol=0.0,
                                   atol=0.0) == [], case
            for name in ("proj_len", "expiry_mth", "t_entry", "duration_mth_init",
                         "max_dur"):
                assert type(mine.cells[name]()) is int, (case, name)
    finally:
        ints.close()
        floats.close()


def test_the_edges_of_the_in_force_interface_are_accepted(tmp_path):
    """A zero count, whole numbers in any type, the horizon and each bound's edge are read.

    A count of 0 is a point that projects zeros.  ``60.0`` is a whole number of months,
    read back as the int the policy clock counts in; a policy issued 120 months after the
    valuation date, the shipped ``future_horizon_mth``, is the last one the table admits,
    with a frame of 336 months.  And each bound of the contract at its edge projects: issue
    at 18 to expiry at 70, 624 months, and issue at 59 to expiry at 60, 12 months, the
    oldest issue and the shortest cover, and expiry at 50, the earliest.  Then the
    history's bounds, each at its edge: an escalated benefit and premium half a cent below
    those at issue, an extract rounded to the cent, which ``Data``'s rule 12 admits; and
    the first-year rule's edge, the female cell a month past its first anniversary, its
    first increase in the columns.  And the claim cohorts' edges: shares summing to 1
    within 9e-11 either side, inside the tolerance of 1e-10 the malformed cases refuse
    1.1e-10 past; a claim as old as its policy, ``z = duration_mth``; and a point in force
    all healthy, holding no row in the companion.  The extra rows are copies of committed
    rows under labels of their own, 41 to 49.
    """
    committed = _committed()
    claim = _label(committed, "derived", 2, 24)
    anchor = _label(committed, "derived", 1, 60)
    female = _label(committed, "derived", 4, 13)
    future = _label(committed, "future", 4, -13)
    copies = {41: (1, {"entry_age": 18, "expiry_age": 70}),
              42: (6, {"entry_age": 59, "expiry_age": 60}),
              43: (3, {"entry_age": 18, "expiry_age": 50}),
              44: (anchor, {"benefit_pp_init": 1999.995, "premium_pp_init": 34.995}),
              46: (anchor, {}),
              47: (anchor, {}),
              48: (claim, {}),
              49: (anchor, {"pols_active_init": 1.0})}

    def edit(table):
        extra = []
        for label, (source, changes) in copies.items():
            row = table.loc[[source]].assign(policy_id=f"IP-9000{label}", **changes)
            row.index = pd.Index([label], name="point_id")
            extra.append(row)
        table = pd.concat([table, *extra])
        table = _set("policy_count", [1], 0.0)(table)
        table = table.assign(duration_mth=table["duration_mth"].astype(float))
        table = _set("duration_mth", [future], -120.0)(table)
        return table

    def cohorts(table):
        def copy_of(source, label):
            return table[table["point_id"] == source].assign(point_id=label)
        held = [table, copy_of(anchor, 44)]
        for label, by in ((46, 9e-11), (47, -9e-11)):
            rows = copy_of(anchor, label).reset_index(drop=True)
            at = rows["pols_sick_dur_init"].idxmax()
            rows.loc[at, "pols_sick_dur_init"] = rows.at[at, "pols_sick_dur_init"] + by
            held.append(rows)
        held.append(copy_of(claim, 48).assign(z=36))
        return pd.concat(held, ignore_index=True)

    model = _read_edited(tmp_path, edit, cohorts)
    try:
        read = model.Data.model_point_table()
        assert read["duration_mth"].dtype == float
        assert len(model.Data.inforce_cohorts()) == len(cohorts(_committed_cohorts()))
        zero = _point(model, 1)
        df = zero.result_cf()
        assert len(df) == 360 and (df == 0.0).all().all()
        assert type(zero.duration_mth(0)) is int
        late = _point(model, future)
        assert (late.t_entry(), late.proj_len(), late.pols_new_biz(120)) == (120, 336, 1.0)
        for label, months in ((41, 624), (42, 12), (43, 384)):
            edge = _point(model, label)
            assert len(edge.result_cf()) == edge.proj_len() == months, label
            assert edge.check_pols_roll_fwd() and edge.check_states(), label
        half = _point(model, 44)
        assert half.benefit_pp(0) == pytest.approx(1999.995 * 1.03, rel=1e-15)
        first = _point(model, female)
        assert (first.duration_mth_init(), first.duration_init()) == (13, 1)
        assert first.benefit_pp(0) == first.benefit_pp_init() == 1545.0
        for label in (46, 47):
            p = _point(model, label)
            assert p.check_states() and p.proj_len() == 300, label
        old = _point(model, 48)
        assert old.pols_sick_dur_init(36) > 0.0 and old.pols_sick_dur_init(25) == 0.0
        assert old.sick_cohorts(0)[35] == old.pols_if_init() * old.pols_sick_dur_init(36)
        healthy = _point(model, 49)
        assert healthy.pols_active(0) == healthy.policy_count()
        assert healthy.pols_sick(0) == 0.0 and healthy.check_states()
    finally:
        model.close()


def _every_state_months(start, end):
    """The S months a point whose S frame runs from ``start`` to ``end`` is restated at.

    By default the edges of its windows (USLIB-SEC-PLAN.md §5.2, T5): every month of the
    first policy year and the first anniversary, through which ``Data``'s first-year rule
    ends and the first claims start, each anniversary and the month before it, which on
    S's clock are the escalation's steps, the lapse table's years and, on a claim, its
    claim-duration years, and the last month of the frame.  With ``UKLIB_SEC_FULL=1``,
    every month.  Each after ``start``, the twin's month.
    """
    if SEC_FULL:
        return list(range(start + 1, end))
    months = {*range(1, 14), end - 1, *(m for a in range(12, end, 12) for m in (a - 1, a))}
    return sorted(m for m in months if start < m < end)


def _states(s):
    """Each ``(S point, month)`` of :func:`_every_state_months` on every point of ``s``."""
    table = s.Data.model_point_table()
    return [(point_id, d) for key, point_id in zip(point_keys(s), table.index)
            for d in _every_state_months(0, projection(s, key).proj_len())]


def _restated(root, s, states):
    """The twins of ``s``'s points and a row in force at each of ``states``, ``(S point,
    month)``, with their claim cohorts, built by the generator out of ``s`` into a copy of
    the product directory: ``(folder, table, cohorts)``."""
    spec = dataclasses.replace(SPEC, derived=tuple(states), future=(), derived_refs={})
    table, companions = build_sec_table(spec, s)
    return _sec_inputs(root, table, companions[COHORTS]), table, companions[COHORTS]


def _refused_in_force(folder, refs):
    """What ``Data`` and ``proj_len()`` refuse of the table and cohorts in ``folder``, read
    with ``refs`` set first: ``Data``'s refusal, or each row's ``proj_len()``'s, each by
    the line that names it.  Each row is released once asked (:func:`_release`)."""
    model = mx.read_model(folder, name=_name("every"))
    try:
        for ref, value in refs.items():
            setattr(model.Projection, ref, value)
        try:
            model.Data.model_point_table()
            model.Data.inforce_cohorts()
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


def test_every_state_s_reaches_is_accepted_in_force(s_model, tmp_path):
    """Every state ``IP_UK_S`` reaches is a valid opening state (T5).

    ``Data``'s rules and ``proj_len()``'s hold an opening state to what a policy in force
    can be, so they must accept each state the S model reaches: a rule exercised only on
    the rows the other tests choose could refuse a state S reaches elsewhere (D6).  So each
    point of S is restated in force by the generator at the edges of its windows, or with
    ``UKLIB_SEC_FULL=1`` at every month of its frame (:func:`_every_state_months`), into
    one table beside the twins, with its claim cohorts: ``Data`` reads both, and no row's
    ``proj_len()`` refuses it (USLIB-SEC-PLAN.md §5.2, T5, precised at M10).  The test runs
    on each set of inputs on which the states S reaches differ (precised at M9), and
    asserts which states each moves:

    * S as shipped, its seven points under its own References, as T1 and the committed rows
      read it (``s_model``);
    * the main splice set's, :data:`MAIN`, which moves the count, the healthy share, the
      cohorts, the benefit and the premium, every column of the state: the escalation lapse
      shock and the overlays move the first three, and the RPI the last two;
    * the escalation cap's, an RPI of 12%, which moves them all again, the escalation at
      10% a year;
    * the RPI floor's, an RPI of -2%, under which an escalating point's benefit and premium
      stay those at issue past its first year, the edge of ``Data``'s rule 12, which the
      shipped set reaches only in a first policy year or on a level point;
    * the recovery bound's, an overlay of 0.35, under which every claim of a first claim
      year recovers in its month, which moves the count, the healthy share and the cohorts
      and leaves the benefit and the premium the main set's, at its RPI of 5%.

    Expense inflation moves no state, being on the valuation clock and no count.
    ``IP_UK_SEC`` refuses no state ``IP_UK_S`` reaches, so none is set aside.
    """
    extra = {tag: SPLICE_SETS[tag] for tag in ("main", "rpi_cap", "rpi_floor", "recovery")}
    read = {tag: mx.read_model(model_path(TWIN), name=_name(tag)) for tag in extra}
    try:
        for tag, refs in extra.items():
            for ref, value in refs.items():
                setattr(read[tag].Projection, ref, value)
        sets = {"shipped": (s_model, {}), **{tag: (read[tag], refs)
                                             for tag, refs in extra.items()}}
        found, states, held = {}, {}, {}
        for tag, (s, refs) in sets.items():
            reached = _states(s)
            folder, rows, cohorts = _restated(tmp_path / tag, s, reached)
            assert len(rows) == len(s.Data.model_point_table()) + len(reached)
            states[tag] = rows.set_index(["source_policy_id", "source_mth"])
            held[tag] = cohorts.assign(
                policy=cohorts["point_id"].map(rows.set_index("point_id")[
                    "source_policy_id"]),
                month=cohorts["point_id"].map(rows.set_index("point_id")["source_mth"]))
            refused = _refused_in_force(folder, refs)
            if refused:
                found[tag] = f"{len(refused)} refused, first: {refused[:5]}"
    finally:
        for model in read.values():
            model.close()
    assert not found, found
    shipped = states["shipped"]
    columns = ("policy_count", *STATE)
    for tag, moved in (("main", set(columns)), ("rpi_cap", set(columns)),
                       ("rpi_floor", set(columns)),
                       ("recovery", {"policy_count", "pols_active_init"})):
        both = shipped.index.intersection(states[tag].index)
        assert len(both), tag
        apart = {c for c in columns
                 if (shipped.loc[both, c] != states[tag].loc[both, c]).any()}
        if tag == "recovery":
            apart -= {c for c in STATE[1:]
                      if (states["main"].loc[both, c] == states[tag].loc[both, c]).all()}
        assert apart == moved, (tag, apart)
        keys = ["policy", "month", "z"]
        a = held["shipped"].set_index(keys)["pols_sick_dur_init"]
        b = held[tag].set_index(keys)["pols_sick_dur_init"]
        assert not a.reindex(b.index).equals(b), tag


# ---------------------------------------------------------------------------
# The assumption tables
#
# Data checks each table before a value of it is read, in the cell the projection takes the
# table's extent from, or in the reader where it takes none (UKLIB-SEC-PLAN.md §4;
# USLIB-SEC-PLAN.md §7.1, *Precised at M3*, item 9).  Each case is the shipped table with
# one fault, read from a copy, refused by that cell alone, naming the file, the column and
# the lines at fault, the header line 1, and through a projection of the anchor cell in
# force at 60, which reads every table.  The lines are the shipped file's (_line): the
# mortality table holds the male ages 16 to 75 on lines 2 to 61 and the female on lines 62
# to 121; the lapse table the policy years 1 to 6 on lines 2 to 7; the termination table the
# claim duration years 1 to 5 on lines 2 to 6; and the inception table its forty schedules,
# eight pivot ages each, on lines 2 to 321.

MORT, LAPSE, TERM, INCEPTION = ("mort_table.csv", "lapse_table.csv",
                                "termination_table.csv", "inception_table.csv")

# The Data cell that checks each table, the first a projection asks of it.
CHECKED_BY = {MORT: "mort_age_first", LAPSE: "lapse_last_year",
              TERM: "termination_last_year", INCEPTION: "inception_table"}


def _line(file, **keys):
    """The line of the shipped ``file`` whose columns hold ``keys``, the header line 1."""
    rows = pd.read_csv(model_path(TWIN).parent / file)
    hit = rows.index[_where(**keys)(rows)].tolist()
    assert len(hit) == 1, (file, keys, hit)
    return hit[0] + 2


def _where(**keys):
    """The rows of a table whose columns hold ``keys``, as a boolean array."""
    return lambda table: np.logical_and.reduce(
        [(table[c] == v).to_numpy() for c, v in keys.items()])


def _written(column, value, where):
    """An edit of a table that writes ``value`` into ``column`` on the rows ``where``
    picks."""
    def edit(table):
        cells = table[column].astype(object)
        cells[where(table)] = value
        return table.assign(**{column: cells})
    return edit


def _dropped(where):
    return lambda table: table[~where(table)].reset_index(drop=True)


def _repeated(where):
    return lambda table: pd.concat([table, table[where(table)]], ignore_index=True)


def _rate_rule(file, column, *lines):
    return f"{file}: {column} must be a number from 0 to 1; it is not on line {list(lines)}"


def _whole_rule(file, column, *lines):
    return (f"{file}: {column} must be a whole number below 2**53 in size; it is not on "
            f"line {list(lines)}")


def _ages_apart(*faults):
    """The message of a mortality table whose sexes do not run one row an age."""
    return (f"{MORT}: the ages of each sex must run from 16 to 75, the table's first and "
            f"last, one row an age, none below 0; " + "; ".join(faults))


def _years_apart(file, years, *faults):
    """The message of a lapse or termination table whose years do not run one row a
    year."""
    return (f"{file}: the {years} must run from 1, one row a year, without a gap or a "
            f"repeat; " + "; ".join(faults))


def _schedules_apart(*faults):
    """The message of an inception table whose schedules do not hold two pivots each."""
    return (f"{INCEPTION}: each sex, occupation class and deferred period must hold two "
            f"pivot ages or more, one row an age; " + "; ".join(faults))


def _mort(sex, age):
    return _where(sex=sex, age=age)


def _pivot(sex, occ, weeks, age):
    return _where(sex=sex, occ_class=occ, deferred_weeks=weeks, age=age)


def _pivot_line(sex, occ, weeks, age):
    return _line(INCEPTION, sex=sex, occ_class=occ, deferred_weeks=weeks, age=age)


NAN, INF = float("nan"), float("inf")
_CODES = (f"{INCEPTION}: sex must be M or F, occ_class 1 to 4, and deferred_weeks 4, 8, 13, "
          f"26 or 52; they are not on line ")

# A table the reader cannot read, or whose value is not a number in its range, as (case,
# the file, its edit, the message).  A value no point reads is refused too: the male
# mortality at 75, which no frame reaches, and the female inception schedule of class 4
# and 52 weeks, which no point holds.
UNREADABLE = [
    ("a blank mortality rate", MORT, _written("mort_rate", NAN, _mort("M", 40)),
     _rate_rule(MORT, "mort_rate", _line(MORT, sex="M", age=40))),
    ("a text mortality rate", MORT, _written("mort_rate", "low", _mort("F", 40)),
     _rate_rule(MORT, "mort_rate", _line(MORT, sex="F", age=40))),
    ("an infinite mortality rate no point reads", MORT,
     _written("mort_rate", INF, _mort("M", 75)),
     _rate_rule(MORT, "mort_rate", _line(MORT, sex="M", age=75))),
    ("a negative mortality rate", MORT, _written("mort_rate", -0.001, _mort("F", 16)),
     _rate_rule(MORT, "mort_rate", _line(MORT, sex="F", age=16))),
    ("a mortality rate past 1", MORT, _written("mort_rate", 1.5, _mort("M", 60)),
     _rate_rule(MORT, "mort_rate", _line(MORT, sex="M", age=60))),
    ("two mortality rows at fault", MORT,
     _then(_written("mort_rate", NAN, _mort("M", 16)),
           _written("mort_rate", NAN, _mort("F", 75))),
     _rate_rule(MORT, "mort_rate", _line(MORT, sex="M", age=16),
                _line(MORT, sex="F", age=75))),
    ("an age not whole", MORT, _written("age", 65.5, _mort("M", 65)),
     _whole_rule(MORT, "age", _line(MORT, sex="M", age=65))),
    ("an age past 2**53", MORT, _written("age", 1e19, _mort("F", 50)),
     _whole_rule(MORT, "age", _line(MORT, sex="F", age=50))),
    ("an age written as text", MORT, _written("age", "x", _mort("F", 17)),
     _whole_rule(MORT, "age", _line(MORT, sex="F", age=17))),
    ("an unknown sex", MORT, _written("sex", "X", _mort("F", 18)),
     f"{MORT}: sex must be M or F; it is not on line [{_line(MORT, sex='F', age=18)}]"),
    ("an age missing", MORT, _dropped(_mort("M", 40)),
     _ages_apart("no line holds sex M, age 40")),
    ("an age twice", MORT, _repeated(_mort("F", 30)),
     _ages_apart(f"sex F, age 30 repeats on lines [{_line(MORT, sex='F', age=30)}, 122]")),
    ("an age below 0", MORT, _written("age", -1, _mort("M", 16)),
     _ages_apart(f"age -1, below 0, is on lines [{_line(MORT, sex='M', age=16)}]",
                 "no line holds sex M, age 16")),
    ("a sex missing", MORT, _dropped(lambda t: (t["sex"] == "F").to_numpy()),
     _ages_apart("no line holds sex F, ages 16 to 75")),
    ("a sex shorter", MORT, _dropped(_mort("F", 75)),
     _ages_apart("no line holds sex F, age 75")),
    ("a blank lapse rate", LAPSE, _written("lapse_rate", NAN, _where(policy_year=2)),
     _rate_rule(LAPSE, "lapse_rate", 3)),
    ("a lapse rate past 1", LAPSE, _written("lapse_rate", 1.2, _where(policy_year=6)),
     _rate_rule(LAPSE, "lapse_rate", 7)),
    ("an infinite lapse rate", LAPSE, _written("lapse_rate", INF, _where(policy_year=1)),
     _rate_rule(LAPSE, "lapse_rate", 2)),
    ("a text lapse rate", LAPSE, _written("lapse_rate", "six", _where(policy_year=4)),
     _rate_rule(LAPSE, "lapse_rate", 5)),
    ("a policy year not whole", LAPSE, _written("policy_year", 3.5, _where(policy_year=3)),
     _whole_rule(LAPSE, "policy_year", 4)),
    ("a policy year missing", LAPSE, _dropped(_where(policy_year=4)),
     _years_apart(LAPSE, "policy years", "no line holds policy_year 4")),
    ("a policy year twice", LAPSE, _repeated(_where(policy_year=2)),
     _years_apart(LAPSE, "policy years", "policy_year 2 repeats on lines [3, 8]")),
    ("a policy year of 0", LAPSE, _written("policy_year", 0, _where(policy_year=1)),
     _years_apart(LAPSE, "policy years", "policy_year 0, below 1, is on lines [2]",
                  "no line holds policy_year 1")),
    ("a blank recovery rate", TERM,
     _written("recovery_rate", NAN, _where(claim_duration_year=1)),
     _rate_rule(TERM, "recovery_rate", 2)),
    ("a recovery rate past 1", TERM,
     _written("recovery_rate", 1.4, _where(claim_duration_year=2)),
     _rate_rule(TERM, "recovery_rate", 3)),
    ("a negative in-claim mortality", TERM,
     _written("mort_rate_sick", -0.01, _where(claim_duration_year=3)),
     _rate_rule(TERM, "mort_rate_sick", 4)),
    ("an infinite in-claim mortality", TERM,
     _written("mort_rate_sick", INF, _where(claim_duration_year=5)),
     _rate_rule(TERM, "mort_rate_sick", 6)),
    ("a claim duration year written as text", TERM,
     _written("claim_duration_year", "4+", _where(claim_duration_year=4)),
     _whole_rule(TERM, "claim_duration_year", 5)),
    ("two claim duration years missing", TERM,
     _dropped(lambda t: t["claim_duration_year"].isin([2, 3]).to_numpy()),
     _years_apart(TERM, "claim duration years", "no line holds claim duration years 2 to 3")),
    ("a claim duration year twice", TERM, _repeated(_where(claim_duration_year=5)),
     _years_apart(TERM, "claim duration years",
                  "claim_duration_year 5 repeats on lines [6, 7]")),
    ("a blank inception rate", INCEPTION,
     _written("inception_rate", NAN, _pivot("M", 1, 26, 40)),
     _rate_rule(INCEPTION, "inception_rate", _pivot_line("M", 1, 26, 40))),
    ("an inception rate past 1", INCEPTION,
     _written("inception_rate", 1.2, _pivot("F", 3, 13, 45)),
     _rate_rule(INCEPTION, "inception_rate", _pivot_line("F", 3, 13, 45))),
    ("a text inception rate", INCEPTION,
     _written("inception_rate", "high", _pivot("M", 2, 52, 60)),
     _rate_rule(INCEPTION, "inception_rate", _pivot_line("M", 2, 52, 60))),
    ("an infinite inception rate no point reads", INCEPTION,
     _written("inception_rate", INF, _pivot("F", 4, 52, 64)),
     _rate_rule(INCEPTION, "inception_rate", _pivot_line("F", 4, 52, 64))),
    ("an occupation class of 5", INCEPTION, _written("occ_class", 5, _pivot("M", 4, 8, 30)),
     _CODES + f"[{_pivot_line('M', 4, 8, 30)}]"),
    ("a deferred period off the menu", INCEPTION,
     _written("deferred_weeks", 6, _pivot("F", 1, 4, 35)),
     _CODES + f"[{_pivot_line('F', 1, 4, 35)}]"),
    ("an unknown sex in the inception table", INCEPTION,
     _written("sex", "X", _pivot("M", 3, 26, 50)),
     _CODES + f"[{_pivot_line('M', 3, 26, 50)}]"),
    ("a pivot age not whole", INCEPTION, _written("age", 37.5, _pivot("M", 1, 26, 35)),
     _whole_rule(INCEPTION, "age", _pivot_line("M", 1, 26, 35))),
    ("an occupation class written as text", INCEPTION,
     _written("occ_class", "OC2", _pivot("F", 2, 8, 40)),
     _whole_rule(INCEPTION, "occ_class", _pivot_line("F", 2, 8, 40))),
    ("a schedule of one pivot", INCEPTION,
     _dropped(lambda t: (_where(sex="M", occ_class=1, deferred_weeks=4)(t)
                         & (t["age"] != 30).to_numpy())),
     _schedules_apart("sex M, occ_class 1, deferred_weeks 4 holds 1 pivot age")),
    ("a schedule missing", INCEPTION,
     _dropped(_where(sex="F", occ_class=4, deferred_weeks=52)),
     _schedules_apart("sex F, occ_class 4, deferred_weeks 52 holds 0 pivot ages")),
    ("a pivot age twice", INCEPTION, _repeated(_pivot("M", 1, 26, 40)),
     _schedules_apart(f"sex M, occ_class 1, deferred_weeks 26, age 40 repeats on lines "
                      f"[{_pivot_line('M', 1, 26, 40)}, 322]")),
]


@pytest.mark.parametrize("case, file, edit, message", UNREADABLE,
                         ids=[c[0] for c in UNREADABLE])
def test_a_table_a_reader_cannot_read_is_refused_naming_its_lines(tmp_path, case, file,
                                                                  edit, message):
    """``Data`` refuses each assumption table before a value of it is read (T5).

    ``IP_UK_S`` reads a blank rate as NaN, which its caps keep and every flow carries; an
    infinite one, which a cap reads as certain death or a certain claim; a key that is not
    whole, gapped or repeated, as a ``KeyError`` only where a projection reaches it, or as a
    wrong row; and an inception schedule of one pivot as an interpolation it cannot make.
    Here the cell that checks the table (:data:`CHECKED_BY`), the first a projection asks
    of it, refuses each, naming the file, the column and the lines at fault
    (:data:`UNREADABLE`), and so does a projection of the anchor cell in force at 60, which
    reads all four tables.
    """
    model = _read_edited(tmp_path, lambda t: t, edits={file: edit})
    try:
        _refused(model.Data.cells[CHECKED_BY[file]], message)
        _refused(_row(model, "derived", 1, 60).result_cf, message)
    finally:
        model.close()


def test_a_read_beyond_the_mortality_table_is_refused_naming_its_point(tmp_path):
    """A read past the mortality table's ages is refused, naming the point, and the
    contract keeps every frame inside it.

    ``IP_UK_S``'s lookup raises ``KeyError`` beyond the table, naming no point.  The table
    rates ages 16 to 75, and the contract issues from 18, ``issue_age_min``, and expires by
    70, ``expiry_age_max``, which ``proj_len()`` holds to a year past the table's last age,
    so no frame the contract writes reads past it.  With ``issue_age_min`` lowered to 0, a
    policy issued at 15 is refused by the one cell that reads the table, naming the point
    and the age.  And with the table cut to ages 16 to 68, the shipped ``expiry_age_max`` of
    70 is itself refused, naming the table's last age, since a cover to 70 reads 69; at 69
    the anchor cell projects.  Each Reference is set on a model just read (K7).
    """
    model = _read_edited(tmp_path / "young", _set("entry_age", [3], 15))
    try:
        model.Projection.issue_age_min = 0
        _refused(_point(model, 3).result_cf,
                 "point_id 3: mort_table.csv has no rate at attained age 15")
    finally:
        model.close()
    model = _read_edited(tmp_path / "short", lambda t: t,
                         edits={MORT: _dropped(lambda t: (t["age"] > 68).to_numpy())})
    try:
        _refused(_point(model, 1).result_cf,
                 "point_id 1: expiry_age_max must be expiry_age_min, 50, or more, and at "
                 "most 69, a year past mort_table.csv's last age, not 70")
    finally:
        model.close()
    model = _read_edited(tmp_path / "shorter", lambda t: t,
                         edits={MORT: _dropped(lambda t: (t["age"] > 68).to_numpy())})
    try:
        model.Projection.expiry_age_max = 69
        assert len(_point(model, 1).result_cf()) == 360
    finally:
        model.close()


@pytest.mark.parametrize("grid", GRIDS)
def test_a_key_written_as_a_float_reads_as_ip_uk_s_reads_it(sec_model, tmp_path, grid):
    """A key written ``65.0`` is the key 65, in every table and in its extents.

    ``IP_UK_S``'s lookups match a float key to the int the projection asks, so a table
    written by a tool that writes every number with a decimal point reads the same.  The
    four assumption tables' keys, the model point table's ``duration_mth``, ages,
    occupation class and deferred period, and the claim cohorts' ``point_id`` and ``z`` are
    written as floats, and every committed point projects what the committed tables
    project, exactly.  The default run takes :data:`CORE_POINTS`, and the full grid the
    other committed points.
    """
    def as_float(*columns):
        return lambda table: table.assign(**{c: table[c].astype(float) for c in columns})

    model = _read_edited(tmp_path, as_float("duration_mth", "entry_age", "expiry_age",
                                            "occ_class", "deferred_weeks"),
                         as_float("point_id", "z"),
                         edits={MORT: as_float("age"), LAPSE: as_float("policy_year"),
                                TERM: as_float("claim_duration_year"),
                                INCEPTION: as_float("occ_class", "deferred_weeks", "age")})
    try:
        for point_id in _committed().index:
            if not _on_grid(grid, point_id):
                continue
            for report in ("result_cf", "result_states", "result_pols"):
                assert frame_mismatches(_point(sec_model, point_id).cells[report](),
                                        _point(model, point_id).cells[report](),
                                        rtol=0, atol=0) == [], (point_id, report)
    finally:
        model.close()


# ---------------------------------------------------------------------------
# T6 -- regeneration


def test_the_committed_sec_inputs_are_what_s_generates(s_model):
    """``model_point_table_sec.csv`` and ``inforce_cohorts_sec.csv`` are what IP_UK_S and
    its table generate today.

    Every row and column of both, the text cells, the opening state and the claim cohorts
    among them: an edit to an S row the table copies or derives from, or to an S formula a
    row's state is read from, fails here until ``python tools/gen_sec_points.py
    IP_UK_SEC`` regenerates them, in the same commit.  Text and integers compare exactly,
    and a float by its value, to 1e-12, because the text the writer picks for a computed
    float depends on the platform's parser (``uk_sec_support``'s module docstring).
    """
    assert check_generated(SEC, s_model=s_model) == []


# ---------------------------------------------------------------------------
# The product's own facts


def test_the_two_clocks_on_the_shipped_points(sec_model):
    """``t`` counts from the valuation date; ``duration_mth(t)`` from issue (D3, D4).

    On the twin of S's anchor cell the two coincide, and its policy enters as new business
    at ``t = 0``.  The anchor cell in force 60 months, its fifth anniversary falling at the
    valuation date, is in policy year 6 at attained age 40 at ``t = 0``, its count on the
    books and none new, steps into policy year 7 at ``t = 12``, and has 300 months of its
    frame left, to the same policy end date as from issue, policy month 360.  The twin of
    S's claims-in-payment worked example is in force 12 months, issued at 34 so that it is
    35 at the valuation date, as S's point is, every life in claim at claim duration 1, to
    the policy end date 372 months from issue.  The female cell issued 13 months on has
    nothing on the books and nothing to do before ``t = 13``, and a frame of 229 months.
    The anchor cell in its last month has a one-month frame, at whose end the policies in
    force reach the policy end date.  A timing or a kind the model does not know is refused
    rather than answered with another count.
    """
    twin = _row(sec_model, "twin", 1, 0)
    assert [twin.duration_mth(t) for t in (0, 1, 359)] == [0, 1, 359]
    assert (twin.t_entry(), twin.pols_if_init(), twin.pols_new_biz(0)) == (0, 0.0, 1.0)
    assert (twin.expiry_mth(), twin.proj_len(), twin.max_dur()) == (360, 360, 361)
    old = _row(sec_model, "derived", 1, 60)
    assert (old.duration_mth(0), old.duration_init(), old.duration(0), old.policy_year(0),
            old.age(0)) == (60, 4, 5, 6, 40)
    assert (old.policy_year(11), old.policy_year(12)) == (6, 7)
    assert (old.proj_len(), old.expiry_mth(), old.t_entry(), old.pols_new_biz(0)) == (
        300, 360, 0, 0.0)
    assert old.pols_if_at(0, _code(old, "BEF_DECR")) == old.pols_if_init() == (
        old.policy_count())
    claim = _row(sec_model, "twin", 2, 0)
    assert (claim.duration_mth(0), claim.age_at_entry(), claim.age(0),
            claim.policy_year(0)) == (12, 34, 35, 2)
    assert (claim.pols_active(0), claim.pols_sick(0), claim.pols_sick_dur(0, 1)) == (
        0.0, 1.0, 1.0)
    assert (claim.proj_len(), claim.expiry_mth()) == (360, 372)
    fut = _row(sec_model, "future", 4, -13)
    assert (fut.duration_mth(0), fut.t_entry(), fut.proj_len()) == (-13, 13, 229)
    assert not fut.is_active(12) and fut.is_active(13)
    assert (fut.pols_if_init(), fut.pols_new_biz(13), fut.pols_active(13)) == (0.0, 1.0, 1.0)
    last = _row(sec_model, "derived", 1, 359)
    assert (last.proj_len(), last.age(0), last.policy_year(0)) == (1, 64, 30)
    assert last.pols_maturity(0) > 0.0
    _refused(lambda: old.pols_if_at(0, "BEF_NOTHING"), "invalid timing")
    _refused(lambda: old.claims(0, "NOTHING"), "invalid kind")


DISC = 0.03             # the shipped disc_rate, which the present value test reads


def test_the_present_value_and_the_annuity_factor_run_on_the_valuation_clock(sec_model,
                                                                            s_model):
    """``pv_benefits`` discounts to the valuation date, and ``annuity_dis`` is per policy
    of the amount payable there (D7).

    On the twin of S's claims-in-payment worked example, which S opens at the valuation
    date, both are S's: the notes' ``a_dis(35, 0)``, 49.783 per £1 a month, on £2,000 a
    month a value of 99,566.90.  On a row restated in force at S month ``d``, they are S's
    claims from ``d`` on, discounted to ``d``, which S does not compute: the claim from
    duration 0 at 24, the claim from duration 30 at 6, and the anchor cell at 60, its value
    one of future claims; the factor is that value over the amount payable at the valuation
    date times the count, per policy on the books.  On the female cell issued 13 months on
    the value is S's discounted 13 months more, nothing being paid before issue.  And the
    discount factor runs on ``t``, ``1.03^-((t + 1) / 12)``, on every point.
    """
    assert sec_model.Projection.disc_rate == DISC
    twin, s2 = _row(sec_model, "twin", 2, 0), _point(s_model, 2)
    assert twin.pv_benefits() == pytest.approx(s2.pv_benefits(), rel=1e-12)
    assert twin.annuity_dis() == pytest.approx(s2.annuity_dis(), rel=1e-12)
    assert (round(twin.annuity_dis(), 3), round(twin.pv_benefits(), 2)) == (49.783, 99566.9)
    for s_point, month in ((2, 24), (5, 6), (1, 60)):
        p, s = _row(sec_model, "derived", s_point, month), _point(s_model, s_point)
        want = sum(s.claims(month + t, "BENEFIT") * (1.0 + DISC) ** (-(t + 1) / 12.0)
                   for t in range(p.proj_len()))
        assert p.pv_benefits() == pytest.approx(want, rel=1e-12), (s_point, month)
        assert p.annuity_dis() == pytest.approx(
            want / (p.amount_payable_pp(0) * p.policy_count()), rel=1e-12), (s_point, month)
    fut, s4 = _row(sec_model, "future", 4, -13), _point(s_model, 4)
    assert fut.pv_benefits() == pytest.approx(
        s4.pv_benefits() * (1.0 + DISC) ** (-13 / 12.0), rel=1e-12)
    for p in (twin, fut, _row(sec_model, "derived", 1, 60)):
        assert [p.disc_factor(t) for t in (0, 11, 12)] == [
            (1.0 + DISC) ** (-(t + 1) / 12.0) for t in (0, 11, 12)]


@pytest.mark.parametrize("grid", GRIDS)
def test_the_committed_rows_continue_their_s_points(sec_model, s_model, tmp_path, grid):
    """Each committed row in force, or issued later, is its S point from its month on.

    T6 compares a float to 1e-12, which pins a small count only to that much of itself, so
    each committed row is compared with its S point frame by frame and cell by cell, at the
    shipped assumptions (USLIB-SEC-PLAN.md §7.1, *Precised at M3*, item 11): the derived
    rows from their months, and the row issued 13 months on from S's start, all to 1e-9
    relative with no absolute floor but on the residuals, every cell but those expense
    inflation moves (:func:`_continues_s`), which the inflation test holds.  The twins are
    T1's and T2's.  The row of S's claim on the active-lives basis at its month 12 is
    compared under :data:`FLAT_LAPSE`, read by S and SEC alike, on which S's restarted
    clock lapses as the policy's does: its state at month 12 is the shipped table's, whose
    first year's rate the flat one is.  The two rows read from S under an RPI of their own
    continue S under that RPI, which the shipped one replaces from the valuation date, and
    their own test holds them.  The default run takes the rows among :data:`CORE_POINTS`,
    and the full grid the rest.
    """
    table = sec_model.Data.model_point_table()
    s_table = s_model.Data.model_point_table()
    found, flat = [], None
    try:
        for point_id in table.index:
            kind, month = table.at[point_id, "row_kind"], int(table.at[point_id,
                                                                       "source_mth"])
            policy = table.at[point_id, "source_policy_id"]
            s_point = int(s_table.index[s_table["policy_id"] == policy][0])
            if (kind == "twin" or (s_point, month) in SPEC.derived_refs
                    or not _on_grid(grid, point_id)):
                continue
            if s_point == 7:
                if flat is None:
                    flat = (mx.read_model(temp_inputs(tmp_path / "s", model_path(TWIN),
                                                      edits=FLAT_LAPSE),
                                          name=_name("flat_s")),
                            mx.read_model(_sec_inputs(tmp_path / "sec", _committed(),
                                                      edits=FLAT_LAPSE),
                                          name=_name("flat_sec")))
                s_proj, sec_proj = _point(flat[0], 7), _point(flat[1], point_id)
                _sweep_s(s_proj)
            else:
                s_proj, sec_proj = _point(s_model, s_point), _point(sec_model, point_id)
            found += [f"point {point_id}: {line}"
                      for line in _continues_s(s_proj, sec_proj, month)]
    finally:
        for model in flat or ():
            model.close()
    assert not found, found[:20]


def test_the_rows_read_under_an_rpi_of_their_own_continue_s_under_it(sec_model):
    """The two committed rows S reaches only under an RPI of its own are S's under it (C2).

    At ``IP_UK_S``'s flat 3% no state holds a lapse shocked by escalation, nor an increase
    capped, so the spec restates the anchor cell at its month 40 from S run under an RPI of
    5%, and the female cell at its month 30 from S under 12% (the spec's ``derived_refs``),
    and C2 freezes both.  Three things are held of each:

    * the row is S's state under that RPI: S read under it holds, at the row's month, the
      row's count, its healthy share and its claim cohorts, and the month before, its
      benefit and premium;
    * set on this model too, that RPI gives the row S's path: it continues S's projection
      from its month on in every cell, over the whole of both frames, as the splice
      compares them (:func:`_continues_s`);
    * at today's References, which take over from the valuation date, the benefit and the
      premium are S's under that RPI until the row's next anniversary, and from it step at
      today's 3% and 4.5%.
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
            count = sp.pols_if(month)
            assert row.policy_count() == pytest.approx(count, rel=1e-12)
            assert row.pols_active_init() == pytest.approx(sp.pols_active(month) / count,
                                                           rel=1e-12)
            held = sp.sick_cohorts(month)
            assert [row.pols_sick_dur_init(z) for z in range(1, len(held) + 1)] == (
                pytest.approx([h / count for h in held], rel=1e-12, abs=0.0))
            assert row.benefit_pp_init() == pytest.approx(sp.benefit_pp(month - 1),
                                                          rel=1e-12)
            assert row.premium_pp_init() == pytest.approx(sp.premium_pp(month - 1),
                                                          rel=1e-12)
            _sweep_s(sp)
            assert _continues_s(sp, _point(sec, label), month) == []
            anniversary = 12 - month % 12
            for t in range(anniversary):
                assert row.benefit_pp(t) == pytest.approx(sp.benefit_pp(month + t),
                                                          rel=1e-12), t
                assert row.premium_pp(t) == pytest.approx(sp.premium_pp(month + t),
                                                          rel=1e-12), t
            assert row.benefit_pp(anniversary) == pytest.approx(
                row.benefit_pp_init() * 1.03, rel=1e-12)
            assert row.premium_pp(anniversary) == pytest.approx(
                row.premium_pp_init() * 1.045, rel=1e-12)
        finally:
            sec.close()
            s.close()


def test_the_healthy_share_is_read_from_the_model_point(sec_model, tmp_path):
    """The healthy share of the count is the point's, not rebuilt (K14).

    ``IP_UK_S`` opens an active cell all healthy and a claim all in claim, so a model that
    read the shares from ``status`` would pass every comparison with S's twins.  So the
    claim on the active-lives basis at its month 12, 0.3913 of it healthy, its recoveries
    back in health, is opened with half its count healthy and its cohorts scaled to the
    other half: it opens its healthy lives and its lives in claim at the shares the row
    holds, and its premiums, paid by the healthy lives alone, follow them.
    """
    row = _label(_committed(), "derived", 7, 12)
    share = _committed().at[row, "pols_active_init"]
    scale = 0.5 / (1.0 - share)

    def cohorts(frame):
        mine = frame["point_id"] == row
        return frame.assign(pols_sick_dur_init=frame["pols_sick_dur_init"].where(
            ~mine, frame["pols_sick_dur_init"] * scale))

    model = _read_edited(tmp_path, _set("pols_active_init", [row], 0.5), cohorts)
    try:
        p, q = _point(model, row), _point(sec_model, row)
        count = p.policy_count()
        assert (p.pols_active(0), q.pols_active(0)) == (count * 0.5, count * share)
        assert p.pols_sick(0) == pytest.approx(count * 0.5, rel=1e-12)
        assert p.premiums(0) == p.premium_pp(0) * (count * 0.5)
        assert q.premiums(0) == q.premium_pp(0) * (count * share)
        for z in range(1, 14):
            assert p.pols_sick_dur(0, z) == pytest.approx(q.pols_sick_dur(0, z) * scale,
                                                          rel=1e-12, abs=0.0), z
    finally:
        model.close()


def test_the_claim_cohorts_are_read_from_the_model_point(sec_model, tmp_path):
    """The lives in claim at each claim duration are the point's, not rebuilt (K14).

    ``IP_UK_S`` seeds a claim in one cohort, ``claim_duration_months``, and builds the rest
    from the inceptions since issue, so a model that rebuilt them from the history would
    pass the splice.  So the anchor cell at 60 is opened with its lives in claim at
    duration 5 moved to duration 17, a claim year on: the cohort vector opens with them
    there, and they recover at the second claim year's rate, 0.25 a year, where at
    duration 5 the first year's 0.40 would apply; every other cohort is the committed
    row's.
    """
    row = _label(_committed(), "derived", 1, 60)

    def moved(frame):
        frame = frame.copy()
        mine = frame["point_id"] == row
        five = frame.index[mine & (frame["z"] == 5)][0]
        later = frame.index[mine & (frame["z"] == 17)][0]
        frame.loc[later, "pols_sick_dur_init"] += frame.at[five, "pols_sick_dur_init"]
        return frame.drop(index=five).reset_index(drop=True)

    model = _read_edited(tmp_path, lambda t: t, moved)
    try:
        p, q = _point(model, row), _point(sec_model, row)
        lives = q.pols_sick_dur(0, 5)
        assert lives > 0.0 and p.pols_sick_dur(0, 5) == 0.0
        assert p.pols_sick_dur(0, 17) == pytest.approx(q.pols_sick_dur(0, 17) + lives,
                                                       rel=1e-12)
        assert [p.pols_sick_dur(0, z) for z in range(1, 61) if z not in (5, 17)] == (
            pytest.approx([q.pols_sick_dur(0, z) for z in range(1, 61)
                           if z not in (5, 17)], rel=1e-12, abs=0.0))
        assert (p.rec_rate(5), p.rec_rate(17)) == (0.4, 0.25)
        assert p.pols_recovery(0) - q.pols_recovery(0) == pytest.approx(
            lives * (p.rec_rate_mth(17) - p.rec_rate_mth(5)), rel=1e-9)
    finally:
        model.close()


def test_the_benefit_is_read_from_the_model_point(sec_model, tmp_path):
    """The benefit entering month 0 is the point's, not rebuilt from issue (K14).

    ``IP_UK_S`` rebuilds an RPI cell's benefit from issue at today's flat ``rpi_rate``, so
    a model that did the same would pass the splice.  So the anchor cell at 60 is opened
    with a benefit of 2,400 a month, which no flat RPI gives beside its premium: it pays
    that times 1.03 from ``t = 0``, month 0's anniversary step at today's RPI, through
    policy year 6, and times 1.03 again from ``t = 12``; its claims pay it on the lives in
    claim.  The committed row's own benefit, 2,000 x 1.03^4, projects as that.
    """
    row = _label(_committed(), "derived", 1, 60)
    model = _read_edited(tmp_path, _set("benefit_pp_init", [row], 2400.0))
    try:
        p, q = _point(model, row), _point(sec_model, row)
        for t, years in ((0, 1), (11, 1), (12, 2), (299, 25)):
            assert p.benefit_pp(t) == pytest.approx(2400.0 * 1.03 ** years, rel=1e-12), t
        assert p.claims(0, _code(p, "BENEFIT")) == pytest.approx(
            p.benefit_pp(0) * p.pols_sick_surv(0), rel=1e-15)
        assert q.benefit_pp_init() == pytest.approx(2000.0 * 1.03 ** 4, rel=1e-12)
        assert q.benefit_pp(0) == pytest.approx(2000.0 * 1.03 ** 5, rel=1e-12)
        assert p.premium_pp(0) == q.premium_pp(0)
    finally:
        model.close()


def test_the_premium_is_read_from_the_model_point(sec_model, tmp_path):
    """The premium entering month 0 is the point's, not rebuilt from issue (K14).

    ``IP_UK_S`` rebuilds an RPI cell's premium from issue at 1.5 times today's flat
    ``rpi_rate``, as it does the benefit.  So the anchor cell at 60 is opened with a premium
    of 45 a month: it charges that times 1.045 from ``t = 0`` through policy year 6, and
    times 1.045 again from ``t = 12``, on its healthy lives.  The committed row's own,
    35 x 1.045^4, projects as that.
    """
    row = _label(_committed(), "derived", 1, 60)
    model = _read_edited(tmp_path, _set("premium_pp_init", [row], 45.0))
    try:
        p, q = _point(model, row), _point(sec_model, row)
        for t, years in ((0, 1), (11, 1), (12, 2), (299, 25)):
            assert p.premium_pp(t) == pytest.approx(45.0 * 1.045 ** years, rel=1e-12), t
        assert p.premiums(0) == p.premium_pp(0) * p.pols_active(0)
        assert q.premium_pp_init() == pytest.approx(35.0 * 1.045 ** 4, rel=1e-12)
        assert p.benefit_pp(0) == q.benefit_pp(0)
    finally:
        model.close()


def test_an_anniversary_at_the_valuation_date_is_the_projection_s_first_event(sec_model):
    """The columns are measured before month 0's events, and the anniversary's increase is
    the projection's, at today's References (D6, as precised at uslib's M7; K14).

    The anchor cell valued on its first anniversary, ``d = 12``, holds the first year's
    benefit and premium, 2,000 and 35, which ``IP_UK_S`` gives in policy month 11, and its
    first escalation is made at ``t = 0``: 3% on the benefit and 4.5% on the premium, at
    today's RPI, so that it pays 2,060 and charges 36.575 through policy year 2, steps again
    at ``t = 12``, and lapses at policy year 2's rate from ``t = 0``.  With the RPI set to
    5% on a model just read (K7), the step at ``t = 0`` is 5% and 7.5%, which shocks its
    lapses from month 0 by 1.05; read after month 0's step, as the instant first was, the
    columns would hold 2,060 and 36.575, at the 3% the history does not have.
    """
    shipped = _row(sec_model, "derived", 1, 12)
    assert (shipped.duration_mth_init(), shipped.duration_init()) == (12, 0)
    assert (shipped.benefit_pp_init(), shipped.premium_pp_init()) == (2000.0, 35.0)
    for t in (0, 11):
        assert shipped.benefit_pp(t) == pytest.approx(2060.0, rel=1e-15), t
        assert shipped.premium_pp(t) == pytest.approx(36.575, rel=1e-15), t
    assert shipped.benefit_pp(12) == pytest.approx(2000.0 * 1.03 ** 2, rel=1e-15)
    assert (shipped.policy_year(0), shipped.lapse_rate(0)) == (2, 0.08)
    model = mx.read_model(model_path(SEC), name=_name("instant"))
    try:
        model.Projection.rpi_rate = 0.05
        row = _row(model, "derived", 1, 12)
        assert row.benefit_pp(0) == pytest.approx(2100.0, rel=1e-15)
        assert row.premium_pp(0) == pytest.approx(37.625, rel=1e-15)
        assert row.esc_lapse_factor(0) == pytest.approx(1.05, rel=1e-15)
        assert row.lapse_rate(0) == pytest.approx(0.084, rel=1e-15)
    finally:
        model.close()


def test_the_cumulative_counts_restart_on_the_books(sec_model, s_model):
    """The cumulative deaths, lapses and exits count from ``t_entry()`` (D5).

    On the anchor cell in force at 60 each is 0.0 at ``t = 0``, where ``IP_UK_S``'s at month
    60 counts the five years before, and adds each month's own from there:
    ``pols_dead_cum(t + 1)`` is ``pols_dead_cum(t)`` plus the deaths of month ``t`` in both
    states, and so S's at ``61 + t`` less S's at 60, as the splice holds its increments.  On
    the twin of the claim on the exit basis, the exits are its recoveries, from its month 0.
    """
    p, s = _row(sec_model, "derived", 1, 60), _point(s_model, 1)
    assert (p.pols_dead_cum(0), p.pols_lapse_cum(0), p.pols_exit_cum(0)) == (0.0, 0.0, 0.0)
    assert s.pols_dead_cum(60) > 0.0 and s.pols_lapse_cum(60) > 0.0
    for t in (0, 1, 11, 12, 298):
        assert p.pols_dead_cum(t + 1) == (
            p.pols_dead_cum(t) + p.pols_death_active(t) + p.pols_death_sick(t)), t
        assert p.pols_lapse_cum(t + 1) == p.pols_lapse_cum(t) + p.pols_lapse(t), t
        assert p.pols_dead_cum(t + 1) == pytest.approx(
            s.pols_dead_cum(61 + t) - s.pols_dead_cum(60), rel=1e-9), t
    claim = _row(sec_model, "twin", 2, 0)
    assert claim.pols_exit_cum(1) == claim.pols_exit(0) > 0.0


def test_expense_inflation_runs_on_the_valuation_clock(sec_model, s_model):
    """The expense loads are in valuation-date pounds, for every point alike (D7).

    At the shipped 3%, the factor at ``t`` is ``1.03^(t // 12)`` on every point, whatever
    its duration, stepping on the valuation date's anniversaries.  So the anchor cell in
    force 60 months pays S's month-``60 + t`` expenses with S's factor taken out and this
    model's put in: at ``t = 0`` S's less 1.03^5, the inflation S has applied since issue.
    And the female cell issued 13 months on pays S's expenses with a year more of inflation
    from its ``t = 24``: its factor at ``t`` is ``1.03^(t // 12)``, where S's at ``t - 13`` is
    ``1.03^((t - 13) // 12)``.  This is the only test that sees inflation run on the
    valuation clock: the splice sets the rate to 0, and on a point issued at ``t = 0``, and
    on the twins of S's claims, which S opens at the valuation date, the clocks agree.
    """
    assert sec_model.Projection.inflation_rate == INFLATION
    p, s = _row(sec_model, "derived", 1, 60), _point(s_model, 1)
    fut, s4 = _row(sec_model, "future", 4, -13), _point(s_model, 4)
    for t in (0, 11, 12, 30):
        assert p.inflation_factor(t) == fut.inflation_factor(t) == (
            (1 + INFLATION) ** (t // 12)), t
    for t in range(p.proj_len()):
        assert p.expenses(t) == pytest.approx(
            s.expenses(60 + t) / s.inflation_factor(60 + t) * p.inflation_factor(t),
            rel=1e-12), t
    assert p.expenses(0) == pytest.approx(s.expenses(60) / (1 + INFLATION) ** 5, rel=1e-12)
    for t in range(13, fut.proj_len()):
        assert fut.expenses(t) == pytest.approx(
            s4.expenses(t - 13) * (1 + INFLATION) ** (t // 12 - (t - 13) // 12),
            rel=1e-12), t


@pytest.mark.parametrize("rpi, esc, shock", [(-0.02, 0.0, 1.0), (0.05, 0.05, 1.05),
                                              (0.12, 0.10, 1.2)])
def test_the_rpi_increases_are_floored_at_0_and_capped(rpi, esc, shock):
    """An RPI point's increases are the RPI floored at 0 and capped at 10%, and premiums
    growing past 5% a year shock its lapses (K14).

    On the anchor cell in force at 60 the benefit steps at ``t = 0`` and each anniversary
    after by ``max(rpi, 0)`` capped at ``esc_cap``, 10%, and the premium by 1.5 times that;
    from policy year 2 its lapses are shocked by ``1 + 2 max(0, 1.5 j - 0.05)``.  At an RPI
    of -2% the floor holds the amounts and leaves the lapses unshocked; at 5% the premium
    grows 7.5% a year and the lapses are shocked by 1.05; at 12% the cap holds the increase
    to 10%, the premium's to 15%, and the shock to 1.2.  The level cell at 30 never moves.
    The RPI is set on a model just read (K7).
    """
    model = mx.read_model(model_path(SEC), name=_name("rpi"))
    try:
        model.Projection.rpi_rate = rpi
        p = _row(model, "derived", 1, 60)
        assert p.esc_rate() == esc
        for t, years in ((0, 1), (11, 1), (12, 2), (299, 25)):
            assert p.benefit_pp(t) == pytest.approx(
                p.benefit_pp_init() * (1 + esc) ** years, rel=1e-12), t
            assert p.premium_pp(t) == pytest.approx(
                p.premium_pp_init() * (1 + 1.5 * esc) ** years, rel=1e-12), t
            assert p.esc_lapse_factor(t) == pytest.approx(shock, rel=1e-12), t
        level = _row(model, "derived", 3, 30)
        assert (level.esc_rate(), level.benefit_pp(299), level.premium_pp(299)) == (
            0.0, 2000.0, 35.0)
    finally:
        model.close()


# ---------------------------------------------------------------------------
# The caps
#
# The mortality and inception caps are written with their bound second, min(q, 1.0), as
# IP_UK_S writes them since M0, and the lapse rate's bound first, min(1.0, w), S's; each
# binds only under References the product does not ship.  Active-life mortality times 100
# passes 1 at attained age 61, on S points 1 and 3 from month 312 and on point 6 from
# month 72; inception under a cycle factor of 50 at age 54 on the female cell, from month
# 144; and the lapse rate at an RPI of 12% under a shock slope of 300 from the first
# anniversary on every RPI point.  Each as (the bound, the References, the annual rate
# capped, the S point, its first capped month, and a committed row of that point).
CAPS = [
    ("the mortality cap", {"mort_active_factor": 100.0}, "mort_rate", 6, 72,
     ("derived", 6, 118)),
    ("the inception cap", {"cycle_factor": 50.0}, "inception_rate", 4, 144,
     ("derived", 4, 13)),
    ("the lapse rate's bound", {"rpi_rate": 0.12, "esc_lapse_slope": 300.0}, "lapse_rate",
     1, 12, ("derived", 1, 12)),
]


@pytest.mark.parametrize("bound, refs, cell, s_point, first, row", CAPS,
                         ids=[c[0] for c in CAPS])
def test_a_rate_past_1_is_capped_in_both_models(bound, refs, cell, s_point, first, row):
    """Where an annual rate passes 1, both models' rate is the float 1.0, and every
    healthy life leaves health in the month.

    On S's point, its twin and a committed row of the point, read with :data:`CAPS`'
    References set on S and SEC alike before either computes anything (K7): the annual rate
    and the monthly rate are 1.0 from the first capped month to the end of the frame, the
    float, not the int 1, which compares equal to it, and floats below 1 before.  So in each
    capped month no healthy life is left at its end: deaths, lapses and inceptions take
    them all, by death under the mortality cap, by lapse under the lapse bound, and by a
    claim under the inception cap.  Every report holds finite floats.  On the committed row
    the first capped month is on its own clock.
    """
    s = mx.read_model(model_path(TWIN), name=_name("cap_s"))
    sec = mx.read_model(model_path(SEC), name=_name("cap"))
    try:
        for model in (s, sec):
            for ref, value in refs.items():
                setattr(model.Projection, ref, value)
        cases = ((_point(s, s_point), first), (_row(sec, "twin", s_point, 0), first),
                 (_row(sec, *row), max(first - row[2], 0)))
        for p, start in cases:
            n = p.proj_len()
            assert 0 <= start < n, (bound, start, n)
            for name in (cell, f"{cell}_mth"):
                rates = [p.cells[name](t) for t in range(n)]
                assert all(type(r) is float and r < 1.0 for r in rates[:start]), (bound, name)
                assert [(type(r), r) for r in rates[start:]] == [(float, 1.0)] * (
                    n - start), (bound, name)
            for t in range(start, n):
                left = (p.pols_active(t) - p.pols_death_active(t) - p.pols_lapse(t)
                        - p.pols_inception(t))
                assert left == pytest.approx(0.0, abs=1e-12), (bound, t)
            for report in ("result_cf", "result_states"):
                frame = p.cells[report]()
                assert np.isfinite(frame.to_numpy(dtype=float)).all(), (bound, report)
    finally:
        sec.close()
        s.close()


# A NaN sent to a bound written with its bound second, as (the bound, the References set to
# NaN on a model read for the test before it computes anything, a replacement of
# Data.termination_table's formula or None, the S point whose twin reads it, and the calls
# that must give the float NaN).  The mortality cap reads mort_active_factor, the inception
# cap cycle_factor, and the in-claim mortality's cap the termination table, whose reader is
# replaced by one that reads NaN for every in-claim mortality, which Data's check of the
# file does not see.  A bound written first would turn the NaN into the bound: a blank input
# read as certain death or a certain claim.  proj_len() refuses a Reference that is not a
# number and Data a rate that is not, so no report projects one; the calls here read no
# frame.
def _nan_sick_mortality():
    """``Data.termination_table`` as a formula reading NaN for every in-claim mortality:
    run in the Data Space, where ``termination_table_rows`` is its cell."""
    return termination_table_rows().set_index("claim_duration_year").assign(  # noqa: F821
        mort_rate_sick=float("nan"))


NAN_BOUNDS = [
    ("the mortality cap, min(q, 1.0)", {"mort_active_factor": NAN}, None, 6,
     [("mort_rate", (0,)), ("mort_rate", (100,)), ("mort_rate_mth", (72,))]),
    ("the inception cap, min(i, 1.0)", {"cycle_factor": NAN}, None, 4,
     [("inception_rate", (0,)), ("inception_rate", (150,)), ("inception_rate_mth", (144,))]),
    ("the in-claim mortality's cap, min(q, 1.0)", {}, _nan_sick_mortality, 2,
     [("mort_rate_sick", (1,)), ("mort_rate_sick", (60,)), ("mort_rate_sick_mth", (13,))]),
]


@pytest.mark.parametrize("bound, refs, table, s_point, calls", NAN_BOUNDS,
                         ids=[c[0] for c in NAN_BOUNDS])
def test_a_nan_that_reaches_a_bound_stays_nan(bound, refs, table, s_point, calls):
    """A NaN that reaches a cap written with its bound second stays NaN, and is not read as
    the bound.

    ``min`` keeps its first argument unless a later one compares smaller, in modelx and
    compiled alike, and no comparison with NaN holds, so with its bound first a cap would
    turn a NaN into 1: certain death, or a certain claim.  The three caps are written with
    the bound second, as ``IP_UK_S`` writes them (:data:`NAN_BOUNDS`): what feeds each is
    made NaN on a model read for the test, and every call must give the float NaN.  The
    cells are called on their own, without the frame: ``proj_len()`` refuses each Reference
    at NaN before a report reaches its cap (the domain test), and ``Data`` each rate.  The
    lapse rate's bound and the recovery rate's keep ``IP_UK_S``'s order, the bound first,
    and the domains and ``Data`` keep a NaN from each.
    """
    model = mx.read_model(model_path(SEC), name=_name("nan"))
    try:
        for ref, value in refs.items():
            setattr(model.Projection, ref, value)
        if table is not None:
            model.Data.cells["termination_table"].formula = table
        p = _row(model, "twin", s_point, 0)
        lost = [f"{name}{args} = {value!r}" for name, args in calls
                for value in [p.cells[name](*args)]
                if not (type(value) is float and math.isnan(value))]
        assert not lost, f"{bound} loses a NaN: {lost}"
    finally:
        model.close()


@pytest.mark.parametrize("check, resid", [
    ("check_pols_roll_fwd", "check_pols_roll_fwd_resid"),
    ("check_states", "check_states_resid")])
def test_a_check_fails_a_residual_that_is_not_a_number(check, resid):
    """Each check returns False where its residual is NaN (§7.1, item 11).

    A check is ``abs(resid) <= tolerance`` over the frame, which no NaN passes, as
    ``IP_UK_S``'s is; but no input the frame accepts gives a NaN residual, so the residual's
    formula is replaced, on a model read for the test, by one that returns NaN in every
    month.  Then the check is the bool False on every committed point, where with its own
    formula it is True, as it is first shown on the twin of the anchor cell and on the
    anchor cell in force at 60, each released once read.  A check that asked whether any
    residual was past its tolerance would pass NaN.
    """
    model = mx.read_model(model_path(SEC), name=_name("nan_resid"))
    try:
        table = model.Data.model_point_table()
        for kind, s_point, month in (("twin", 1, 0), ("derived", 1, 60)):
            key = _row_key(model, kind, s_point, month)
            assert projection(model, key).cells[check]() is True, (kind, s_point, month)
            _release(model, key)
        model.Projection.cells[resid].formula = lambda t: float("nan")
        for key, point_id in zip(point_keys(model), table.index):
            p = projection(model, key)
            assert math.isnan(p.cells[resid](0)), point_id
            assert p.cells[check]() is False, point_id
            _release(model, key)
    finally:
        model.close()


def _outside_cover_faults(p, where, months):
    """Where ``p``, an ItemSpace that has evaluated nothing, departs from OUTSIDE_COVER.

    Every cell of :data:`OUTSIDE_COVER`, ``pols_if_at`` at each timing, ``claims`` at each
    kind, the cohort vector, all zeros, and the cohorts at the first and last claim
    durations, at each of ``months``, every one outside the frame.  Then whether any of
    :data:`IN_COVER_ONLY` was evaluated on the way, which only a fresh ItemSpace can say.  A
    cell that raises is reported as a fault too, so the scan goes on.
    """
    faults = []
    n = p.max_dur()
    for t in months:
        calls = [(name, (t,), want) for name, want in OUTSIDE_COVER.items()]
        calls += [("pols_if_at", (t, _code(p, timing)), 0.0) for timing in TIMINGS]
        calls += [("claims", (t, _code(p, kind)), 0.0) for kind in KINDS]
        calls += [("sick_cohorts", (t,), (0.0,) * n)]
        calls += [("pols_sick_dur", (t, z), 0.0) for z in (1, n)]
        for name, args, want in calls:
            try:
                got = p.cells[name](*args)
            except Exception as err:        # reported, so the scan goes on
                faults.append(f"{where}: {name}{args} raised {_raised(err)}")
                continue
            if got != want or type(got) is not type(want):
                shown = got if name != "sick_cohorts" else "a nonzero vector"
                faults.append(f"{where}: {name}{args} = {shown!r}, not {want!r}"[:200])
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

    On every committed point, in every month before issue and in the first month after the
    frame, ``t = proj_len()``, on a model that evaluates nothing else.  So afterwards none of
    :data:`IN_COVER_ONLY` may hold a value outside the frame at all: ``is_active``'s
    docstring promises that outside cover no count evaluates a rate, and no table is read
    at a policy year or an attained age the policy does not have.

    The committed table's one point issued after the valuation date is the female cell, so
    the same scan runs on the splice's future rows, the core's or, with
    ``UKLIB_SEC_FULL=1``, all of them: the anchor cell, the level cell, an active cell on
    the exit basis and the cap's set among them.  Each row is made afresh first and released
    after.

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
            faults += _outside_cover_faults(p, _case_id(rates, "future", s_point, -k),
                                            [*range(k), p.proj_len()])
        finally:
            _release(sec, key)
    assert futures and not faults, (
        f"{len(faults)} faults outside the frame, first:\n  " + "\n  ".join(faults[:20]))


def test_the_points_sum_row_by_row_into_a_block(spliced):
    """Row ``t`` is the same month on every point, so a block is its frames summed (D3).

    The twin of S's anchor cell, the anchor cell restated at month 12 and the anchor cell
    issued a month on, of the main splice set, summed as ``run_sec.py --block`` sums them,
    are indexed 0..360 and equal S's frame added to itself moved 12 months earlier and a
    month later.  A model whose frames sat on the policy clock would fail it.
    """
    s, sec = spliced.pair("main")
    keys = [_row_key(sec, "twin", 1, 0), _row_key(sec, "derived", 1, 12),
            _row_key(sec, "future", 1, -1)]
    try:
        frames = [projection(sec, key).result_cf() for key in keys]
    finally:
        for key in keys:
            _release(sec, key)
    block = pd.concat(frames).groupby(level="t").sum()
    sdf = _point(s, 1).result_cf()
    expected = pd.concat([sdf, sdf.set_axis(sdf.index - 12).loc[0:],
                          sdf.set_axis(sdf.index + 1)]).groupby(level=0).sum()
    assert list(block.index) == list(range(361))
    assert frame_mismatches(expected, block) == []


def _extract():
    """The committed table as an administration extract would hold it: without the
    generator's columns, and labelled :data:`EXTRACT_LABELS`."""
    extract = _committed().drop(columns=list(GENERATED_COLUMNS))
    extract.index = pd.Index(EXTRACT_LABELS, name="point_id")
    return extract


def _extract_cohorts():
    """The committed claim cohorts under the extract's labels (:func:`_extract`)."""
    cohorts = _committed_cohorts()
    return cohorts.assign(point_id=cohorts["point_id"].map(_relabel_map()))


def _standing(p):
    """What ``run_sec.py`` says of point ``p`` at the valuation date, stated here."""
    d = p.duration_mth_init()
    if d < 0:
        return f"to be issued at t = {-d}, {-d} months after the valuation date"
    if d == 0:
        return "issued at the valuation date, t = 0"
    return (f"in force {d} months: policy year {p.policy_year(0)}, attained age {p.age(0)}, "
            f"{p.pols_if(0):.6f} in force, {p.pols_active(0):.6f} healthy, "
            f"{p.pols_sick(0):.6f} in claim")


def _product(p):
    """What ``run_sec.py`` says of point ``p``'s product, stated here."""
    return (f"{p.sex()}{p.age_at_entry()} occupation class {p.occ_class()}, "
            f"{p.deferred_weeks()}-week deferred period, benefit {p.benefit_mth():,.2f} a "
            f"month to age {p.expiry_age()}, premium {p.premium_mth():,.2f} a month, "
            f"escalation {p.escalation()}, recoveries {p.recovery_basis()}")


@pytest.mark.parametrize("grid", GRIDS)
def test_an_in_force_extract_needs_none_of_the_generator_columns(sec_model, tmp_path, grid):
    """The model reads the in-force interface and S's columns, never where a row came from,
    and names each point by its label, wherever the row stands.

    ``row_kind``, ``source_policy_id`` and ``source_mth`` record how the generator made each
    shipped row, and an administration extract carries none of them.  Read without them,
    and with every label changed, in the table and its claim cohorts alike, every point
    projects what the committed table projects, in ``result_cf``, ``result_states`` and
    ``result_pols``, to 1e-12, and ``run_sec.py``, run beside that extract, prints the point
    without saying where it came from.  On every shipped row in force at the valuation date
    but the twins of S's claims ``source_mth`` equals ``duration_mth``, so a formula that
    read the one for the other would pass every test that leaves ``duration_mth`` as
    generated.  And a refusal names the extract's label.

    The default run compares :data:`CORE_POINTS` and runs the runner and the moved row, and
    the full grid compares the other committed points.
    """
    extract = _extract()
    folder = _sec_inputs(tmp_path / "extract", extract, _extract_cohorts())
    model = mx.read_model(folder, name=_name("extract"))
    try:
        table = model.Data.model_point_table()
        assert not set(GENERATED_COLUMNS) & set(table.columns)
        assert list(table.index) == list(EXTRACT_LABELS)
        for key, base_key, label in zip(point_keys(model), point_keys(sec_model),
                                        _committed().index):
            if not _on_grid(grid, label):
                continue
            mine, base = projection(model, key), projection(sec_model, base_key)
            for report in ("result_cf", "result_states", "result_pols"):
                assert frame_mismatches(base.cells[report](), mine.cells[report](),
                                        rtol=1e-12, atol=1e-12) == [], (key, report)
            _release(model, key)
    finally:
        model.close()
    if grid == "full":
        return
    runner = folder.parent / "run_sec.py"
    shutil.copy(model_path(SEC).parent / "run_sec.py", runner)
    label = extract.index[extract["policy_id"] == "IP-000001-M60"][0]
    out = _run_sec(runner, str(label))
    row = _row(sec_model, "derived", 1, 60)
    assert out.splitlines()[:2] == [
        f"model point {label}: IP-000001-M60 - {_product(row)}",
        f"at the valuation date: {_standing(row)}"]
    last = extract.index[extract["policy_id"] == "IP-000001-M359"][0]
    moved = _set("duration_mth", [last], 360)(extract)
    model = mx.read_model(_sec_inputs(tmp_path / "moved", moved, _extract_cohorts()),
                          name=_name("moved"))
    try:
        _refused(_point(model, last).result_cf,
                 f"point_id {last}: duration_mth 360 is at or past the policy end date, "
                 f"policy month 360, expiry age 65")
    finally:
        model.close()


def test_run_sec_prints_a_point_and_the_block(sec_model):
    """The runner prints one point, saying where it came from, and the block (D8).

    Each mode in an interpreter of its own, as a user runs it, with exit code 0 and ASCII
    output, so that it prints on a Windows console under any code page.  The numbers are
    the model's.  The anchor cell, the runner's default, with its lines at the valuation
    date, each asserted whole, so that a longer number cannot pass for the one asserted,
    and its first twelve rows of cash flows and counts.  Point 9, the anchor cell in force
    60 months; point 11, the claims-in-payment worked example restated at its month 24;
    and point 17, the female cell to be issued 13 months on: each with the lines that say
    where its row came from and where it stands, which only the committed table's generator
    columns can say.  And the block: a line for each committed point, in table order, its
    first twelve rows, which must be the committed points' frames summed row by row, as
    this test sums them, and those frames summed into projection years, each year's counts,
    in force, healthy and in claim, the ones of its first month.  Nothing else runs the
    runner on the committed table.
    """
    runner = model_path(SEC).parent / "run_sec.py"
    out = _run_sec(runner)
    anchor = _row(sec_model, "twin", 1, 0)
    assert out.splitlines()[:3] == [
        f"model point 1: IP-000001 (S's IP-000001) - {_product(anchor)}",
        "at the valuation date: issued at the valuation date, t = 0",
        "proj_len = 360 months from the valuation date (t = 0..359); the policy end date "
        "is policy month 360"]
    assert _product(anchor) == (
        "M35 occupation class 1, 26-week deferred period, benefit 2,000.00 a month to age "
        "65, premium 35.00 a month, escalation RPI, recoveries return_to_h")
    assert anchor.result_cf().head(12).round(2).to_string() in out
    assert anchor.result_pols().head(12).round(6).to_string() in out
    for point_id, case, origin, frame in (
            (9, ("derived", 1, 60), "S's IP-000001 at its month 60",
             "proj_len = 300 months from the valuation date (t = 0..299); the policy end "
             "date is policy month 360"),
            (11, ("derived", 2, 24), "S's IP-000002 at its month 24",
             "proj_len = 336 months from the valuation date (t = 0..335); the policy end "
             "date is policy month 372"),
            (17, ("future", 4, -13), "S's IP-000004, issued 13 months on",
             "proj_len = 229 months from the valuation date (t = 0..228); the policy end "
             "date is policy month 216")):
        p = _row(sec_model, *case)
        policy = sec_model.Data.model_point_table().at[point_id, "policy_id"]
        assert _run_sec(runner, str(point_id)).splitlines()[:3] == [
            f"model point {point_id}: {policy} ({origin}) - {_product(p)}",
            f"at the valuation date: {_standing(p)}", frame], point_id
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
    counts = ["pols_if", "pols_active", "pols_sick"]
    annual = block.drop(columns=counts).groupby(years).sum()
    for column in reversed(counts):
        annual.insert(0, column, block[column].groupby(years).first())
    assert annual.head(12).round(2).to_string() in out


# run_sec.py run as though it sat at /m/products/income_protection, a copy too shallow to
# have a repository above it: the source compiled under that name, so that its own
# __file__ is it.
SHALLOW_RUN = """\
import sys
source = open(sys.argv[1], encoding="utf-8").read()
where = "/m/products/income_protection/run_sec.py"
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
    hold a repository above the product at all.  Each must exit nonzero having printed
    nothing, and say why.  Neither needs modelx-cython, since neither gets as far as
    building.
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
    adds one: ``IP_UK_S``'s one, ``claims``' ``kind=None``, is R12's total, which the C step
    settles, as it did ``Term_UK_SEC``'s.
    """
    assert _defaulted(TWIN) == ["claims"]
    assert _defaulted(SEC) == ["claims"]


# The texts a computed cell may hold at stage "E", beside a column's name read off the
# model point: the kinds and the timings, which the C step makes int References, as it did
# Term's, CI's and ULB's (R9).
CODES = frozenset({*TIMINGS, *KINDS})

# The cells the static check leaves to the C step, each an item of UKLIB-SEC-PLAN.md §6.3's
# C list or a cell that stays Python, every one of them IP_UK_S's as it ships but the
# companion's reader and result_pols:
#
# * the reports and the checks, which stay Python;
# * the six decodes, which read int columns once the text columns are decoded, and the five
#   cells that compare a decoded column with its text, esc_rate, esc_lapse_factor,
#   pols_active, pols_exit and pols_maturity, which then compare ints;
# * the five readers of the assumption tables, by sex, class, deferred period and age, by
#   claim duration year and by policy year, and the reader of the claim cohorts,
#   pols_sick_dur_init, keyed (point_id, z): array reads;
# * the claim cohorts, the tuples IP_UK_S carries them in: sick_cohorts, one a month, and
#   claim_rate_vectors, its rates by claim duration, and the three sums over them,
#   pols_sick_surv, pols_recovery and pols_death_sick, which the C step restructures into
#   pols_sick_dur(t, z), based at t_entry() on a [point, z] array of the companion (M8);
# * the claims total, left to right on int kinds (R12), and the present value, a sum over
#   the frame.
STATIC_EXEMPT = {
    "result_cf", "result_states", "result_pols", "check_pols_roll_fwd", "check_states",
    "occ_class", "deferred_weeks", "escalation", "premium_basis", "status",
    "recovery_basis", "esc_rate", "esc_lapse_factor", "pols_active", "pols_exit",
    "pols_maturity", "inception_rate", "mort_rate", "rec_rate", "mort_rate_sick",
    "lapse_rate_base", "pols_sick_dur_init", "sick_cohorts", "claim_rate_vectors",
    "pols_sick_surv", "pols_recovery", "pols_death_sick", "claims", "pv_benefits"}


def test_no_computed_cell_builds_a_python_object(sec_model):
    """No computed cell builds a tuple, a text or a generator but to raise (§6.3, *C*).

    The C step's static check refuses a Python object in a computed cell, and turns
    ``IP_UK_S``'s own into the C forms UKLIB-SEC-PLAN.md §6.3 lists (:data:`STATIC_EXEMPT`).
    So that the C step restructures nothing beyond that list, no other ``Projection`` cell
    holds a tuple, a list, a set, a dict, a comprehension, a generator or an f-string, or a
    text other than a kind or a timing (:data:`CODES`) or the name of a column it reads off
    ``model_point()``, but inside a ``raise`` statement, read from the source as the build
    reads it.  ``try`` is allowed: a power that leaves the floats raises Python's
    ``OverflowError``, which the cell names.  Every cell of the Space is read, and every
    exemption is a cell of it.
    """
    source = (model_path(SEC) / "Projection" / "__init__.py").read_text(encoding="utf-8")
    built = (ast.Tuple, ast.List, ast.Set, ast.Dict, ast.GeneratorExp, ast.ListComp,
             ast.SetComp, ast.DictComp, ast.JoinedStr, ast.Lambda)
    found, read = [], set()
    for node in ast.parse(source).body:
        if not isinstance(node, ast.FunctionDef):
            continue
        read.add(node.name)
        if node.name in STATIC_EXEMPT:
            continue
        raises = {id(n) for r in ast.walk(node) if isinstance(r, ast.Raise)
                  for n in ast.walk(r)}
        columns = {id(n) for s in ast.walk(node)
                   if isinstance(s, ast.Subscript) and isinstance(s.value, ast.Call)
                   and getattr(s.value.func, "id", None) == "model_point"
                   for n in ast.walk(s.slice)}
        body = node.body[1:] if ast.get_docstring(node) is not None else node.body
        for inner in (n for statement in body for n in ast.walk(statement)):
            if id(inner) in raises:
                continue
            if isinstance(inner, built):
                found.append(f"{node.name}: {type(inner).__name__} at line {inner.lineno}")
            elif (isinstance(inner, ast.Constant) and isinstance(inner.value, str)
                  and inner.value not in CODES and id(inner) not in columns):
                found.append(f"{node.name}: the text {inner.value!r} at line "
                             f"{inner.lineno}")
    assert read == set(sec_model.Projection.cells)
    assert STATIC_EXEMPT <= read
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
    outside the parentheses and quotes of the column, ``claims`` of ``claims(t, "BENEFIT")``;
    a cell of two names, ``expense_maint, inflation_rate``, maps both.
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


# What only IP_UK_S's docstrings may say: a reference into its Spaces, which the SEC pages
# would link to the wrong model, and its clock, t counting policy months.
STALE = re.compile(r"~\.IP_UK_S\.|``t`` counts \*\*policy months\*\*")


def test_the_docstrings_describe_the_valuation_clock(sec_model, s_model):
    """The docstrings say what this model is, and none says what only IP_UK_S is.

    Whitespace is collapsed first, as ``test_model_conventions_uk`` collapses it, so that a
    phrase split across a line break still matches.  The model docstring names the valuation
    date, BasicTerm_SE, the policy clock, the SEC table, its companion and the product.  The
    symbol map in the Projection docstring maps every cell running in force adds, which are
    exactly the cells ``IP_UK_S`` lacks, and names nothing the model lacks: every name in it
    is a cell or a Reference.  No row of a simple table in any docstring puts text between
    two of its columns (:func:`_table_overruns`), which would drop the table from the
    rendered page.  And no docstring says what :data:`STALE` matches.
    """
    flat = {where: re.sub(r"\s+", " ", doc) for where, doc in _docs(sec_model)}
    for phrase in ("valuation date", "BasicTerm_SE", "duration_mth", TABLE, COHORTS,
                   "income protection"):
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
    assert not stale, f"docstrings that describe IP_UK_S: {stale}"


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


def test_the_sec_model_reads_the_s_tables_in_place(sec_model, s_model):
    """One copy of each assumption table serves both models (D1).

    The two ``input_dir()`` s are one directory, and SEC's filename References are S's with
    ``model_point_file`` changed, to ``model_point_table_sec.csv``, and the claim cohorts'
    added: an edit to a table reaches both models, and the two can never drift apart.  And
    every Reference of S's is the SEC model's at S's value, but the four it adds, the
    contract's issue and expiry ages, so that no assumption moves between the two; ``Data``
    adds the future horizon.
    """
    assert sec_model.Data.input_dir() == s_model.Data.input_dir()
    files = {r: v for r, v in s_model.Data.refs.items() if r.endswith("_file")}
    assert {r: v for r, v in sec_model.Data.refs.items() if r.endswith("_file")} == {
        **files, "model_point_file": TABLE, "inforce_cohorts_file": COHORTS}
    assert sec_model.Data.future_horizon_mth == 120
    plain = (bool, int, float, str)
    s_refs = {r: v for r, v in s_model.Projection.refs.items()
              if isinstance(v, plain) and r != "point_id"}
    sec_refs = {r: v for r, v in sec_model.Projection.refs.items()
                if isinstance(v, plain) and r != "point_id"}
    assert sec_refs == {**s_refs, "issue_age_min": 18, "issue_age_max": 59,
                        "expiry_age_min": 50, "expiry_age_max": 70}


# The inception table's pivot ages, which every schedule shares.
PIVOTS = (30, 35, 40, 45, 50, 55, 60, 64)


def test_the_core_grid_reaches_every_branch(spliced, splice_records):
    """What the default run's T2 and T3 cases reach, which the full grid only multiplies.

    The default run thins the splice to a core (the module docstring), and this test is what
    keeps the thinning from costing a branch.  First, statically, over S's table with the
    variants, each property below holds of some core case: each escalation, status and
    recovery basis, each sex, each variant and each set of References; and each kind of
    valuation month: the second month, on an anniversary, the month before and after one,
    about the lapse table's last year, at an inception pivot, on a claim's anniversary,
    and the last month of a frame.  And of some core future case: issued off the valuation
    anniversaries and on them, more than a year on, each escalation, a variant and a set
    other than the main one.

    Then, on the splice's models, of some core row, each of :data:`AT_VALUATION` and
    :data:`IN_FRAME`, what no column of the table shows: every opening-state column in use,
    the month-0 events, and every branch and both sides of every ``min`` and ``max`` the
    full grid reaches.

    Each core row's branches were recorded by the T2 or T3 case that compared it
    (:func:`_settle`), and a row no case has recorded is evaluated here.  With
    ``UKLIB_SEC_FULL=1`` it asks the same of the full grid's rows, which must reach nothing
    the core does not.
    """
    assert set(CORE_SPLICES) <= set(SPLICES + IN_FORCE_TWINS)
    assert set(CORE_FUTURES) <= set(FUTURES)
    s_table = _s_table_with_variants()

    def at(p, column):
        return s_table.at[p, column]

    splices = {
        **{f"{e} escalation": (lambda r, k, p, d, e=e: at(p, "escalation") == e)
           for e in ("RPI", "none")},
        **{f"the {s} status": (lambda r, k, p, d, s=s: at(p, "status") == s)
           for s in ("active", "in_claim")},
        **{f"the {b} basis": (lambda r, k, p, d, b=b: at(p, "recovery_basis") == b)
           for b in ("return_to_h", "exit")},
        **{f"sex {x}": (lambda r, k, p, d, x=x: at(p, "sex") == x) for x in ("M", "F")},
        **{f"variant {v}": (lambda r, k, p, d, v=v: p == v) for v in VARIANTS},
        **{f"the {s} set": (lambda r, k, p, d, s=s: r == s) for s in SPLICE_SETS},
        "a twin in claim": lambda r, k, p, d: k == "twin",
        "in the second month": lambda r, k, p, d: d == 1,
        "on an anniversary": lambda r, k, p, d: d > 0 and d % 12 == 0,
        "in the month before an anniversary": lambda r, k, p, d: d % 12 == 11,
        "in the month after an anniversary": lambda r, k, p, d: d % 12 == 1 and d > 12,
        "about the lapse table's last year": lambda r, k, p, d: (
            at(p, "status") == "active" and 59 <= d <= 61),
        "at an inception pivot": lambda r, k, p, d: (
            at(p, "status") == "active" and d % 12 == 0
            and at(p, "entry_age") + d // 12 in PIVOTS),
        "on a claim's anniversary": lambda r, k, p, d: (
            at(p, "status") == "in_claim" and d > 0
            and (at(p, "claim_duration_months") + d) % 12 == 0),
        "the last month of a frame": lambda r, k, p, d: d == COVER[p] - 1,
    }
    futures = {
        "issued off the anniversaries": lambda r, p, k: k % 12 != 0,
        "issued on them": lambda r, p, k: k % 12 == 0,
        "issued more than a year on": lambda r, p, k: k > 12,
        **{f"{e} escalation": (lambda r, p, k, e=e: at(p, "escalation") == e)
           for e in ("RPI", "none")},
        "a variant": lambda r, p, k: p in VARIANTS,
        "a set other than the main one": lambda r, p, k: r != "main",
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
    model as M7 committed it was frozen below (USLIB-SEC-PLAN.md §5.4): for each point,
    each column of ``result_cf()`` and ``result_pols()``, its sum, its largest absolute value
    and its values at five fixed months, the frame's first and last and the three quartiles
    between.  Every later version must reproduce it, to 1e-12 relative, floored at 1e-12 of
    the column's own magnitude (``uk_sec_support.fingerprint_mismatches``), with the same
    points, frames and columns exactly.  ``python tools/gen_sec_fingerprint.py IP_UK_SEC
    --check`` runs the same comparison from the command line.  Until the freeze, which is
    committed alone, the block is empty and the test skips.
    """
    if not FINGERPRINT:
        pytest.skip("the Phase 1 fingerprint is frozen in a commit of its own")
    assert fingerprint_mismatches(FINGERPRINT, sec_model) == []


# IP_UK_SEC's fingerprint, frozen from the model as M7 committed it and committed alone,
# before its C step changed anything.  Each point is keyed by its point_id; each column
# holds (its sum over the frame, its largest absolute value, (its values at the months)).
# The block is written by tools/gen_sec_fingerprint.py, and is never edited by hand: a
# refreeze goes through the tool's --force, in a commit of its own that says why.
# BEGIN generated fingerprint: IP_UK_SEC -- tools/gen_sec_fingerprint.py
FINGERPRINT = {}
# END generated fingerprint: IP_UK_SEC
