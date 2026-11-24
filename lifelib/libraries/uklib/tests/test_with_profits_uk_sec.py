"""In-force tests for WP_UK_SEC: the splice, future business, counts, regeneration.

``WP_UK_SEC`` is ``WP_UK_S`` taught to run in force at a valuation date (UKLIB-SEC-PLAN.md,
milestone M13, after USLIB-SEC-PLAN.md's Phase 1).  It runs on two clocks: ``t`` counts
months from the valuation date, the same month for every model point, and
``duration_mth(t)`` counts the months the policy has been in force,
``duration_mth_init() + t``.  A model point may be a policy already in force at the
valuation date, in any month of its policy year, one issued at it, or one to be issued
after it, as in ``basiclife/BasicTerm_SE``.  A policy in force opens with its count and
eight columns of state beside it, each per policy and measured at the valuation instant,
before month 0's events, ``WP_UK_S``'s close of the month before: the asset share, the
units and the unit price, the endowment's attaching bonus, the smoothed payout, the bonus
rate of the year under way, and the two cumulants ``WP_UK_S`` restarts at 0 where its frame
opens, the guarantee charges taken and the smoothing account.

The worked example is not restated here.  On a point issued at the valuation date the two
clocks coincide and the model is ``WP_UK_S``, and ``test_model_conventions_uk.py`` asserts
that cell by cell on the twins of S's two new-business points, the endowment and the bond
S's point 7 issues at the valuation date (T1).  The conventions also hold the SEC family's
other rules: every frame opens at ``t = 0``, ``pols_if`` is the ``BEF_DECR`` count,
``BEF_DECR`` is ``BEF_NB`` plus the month's new business, new business enters once, and
nothing happens before issue.  This module holds the rest of the plan's tests (its §5) and
the product's own facts:

* T2, the splice: an S point restated in force at month ``d``, opened with the state S
  carries into ``d``, continues S's projection from ``d`` on, in every cell of S's and in
  the three reports.  The months straddle the product's events: the declarations, the
  guarantee window, the smoothing cap, the corridor, the market value reduction turning
  on, the guarantee charge's cap, the asset share's floor, exhaustion and the one-row
  frames.  S's own in-force points are spliced as twins at 60 and 240.  It runs on two sets
  of References: the main one, with the estate distribution that ships at 0 on, and a
  second with the bonus rule on, on fewer rows.  Variants of S's points, in a copy of S's
  table, add a female life, a -40% crash, the pension tax basis on a bond, and three bonds
  issued at the valuation date for the charge's cap.
* T3, future new business: a point issued ``k`` months after the valuation date is S's
  projection ``k`` months on, with zeros before issue and no table read there.
* D11's R1 and R2, and D3's and D5's chains: on the splice's grid no cell is called at a
  negative month, none on the books reads a month before them, and none reads beyond
  ``t + 1`` but the bonus rate's declaration read, inside the frame; the exhaustion search
  reads the units to the month they run out and no further; on the committed points no
  recursion runs backward over the frame; the policy clock is a closed form; each chain,
  called cold, runs one cell a month back to ``t_entry()`` at the contract's longest cover,
  on each shape; and each chain written inline is its step-by-step cells, bit for bit.
* T4, the count algebra: the count rolls forward through new business, deaths,
  surrenders and maturities, ``result_pols`` holds it, multiplying ``policy_count`` by 2.5
  with every switch that ships off on multiplies every flow and counted cell by 2.5 and
  moves no per-policy value, a point restated a month on continues its own flows, and the
  roll-forward, whose tolerance scales with the count, closes on ten million policies.
* T5, validation: each malformed row of the table is refused as it is read, naming its
  point, by its label on an extract labelled otherwise; each assumption table, malformed or
  holding a value that is not a number in its range, is refused before a value of it is
  read; the future horizon is a Reference that bounds future business; a point past its
  cover, one the contract does not issue, a bond spent in its first month and one that
  reads a Reference off its domain are refused by the frame, each domain at both its edges
  and each accepted edge projecting its reports; a value past the floats in the cell where
  it first is; the edges of the interface are accepted; and so is every state ``WP_UK_S``
  reaches.
* T6, regeneration: the committed ``model_point_table_sec.csv`` is what the generator makes
  of ``WP_UK_S`` and its table as they stand.
* Then the product's own facts: the two clocks on the shipped points; the committed rows
  continuing their S points, those read under References of their own continuing S under
  them; each history column read rather than recomputed (UKLIB-SEC-PLAN.md K14), both
  cumulants among them; the single premium, the declaration and the guarantee window on the
  policy clock; the bonus rate's read bounded by the frame, the recorded departure; the
  exhaustion's new "never"; expense inflation on the valuation clock; the cap on mortality,
  a NaN that reaches a bound and a check whose residual is NaN; the values outside cover;
  the block; an in-force extract; the runner; the cells' defaulted parameters; the
  docstrings; the shared input tables; the parameters a formula could confuse, apart on
  some core row; and what the default grid reaches.

SEC month ``t`` is S month ``t + source_mth`` throughout, the direction in which
``uk_sec_support`` takes its ``t_offset``: ``d`` for a point restated at S month ``d``,
``-k`` for one issued ``k`` months on.

**The core grid and the full one** (UKLIB-SEC-PLAN.md U6).  T2 and T3 over every S point and
variant at every month run by default on a core, chosen so that between them they reach
every branch, every opening-state column, every kind of valuation month and both sides of
every ``min`` and ``max`` the full grid reaches, which
``test_the_core_grid_reaches_every_branch`` asserts.  The other cases, and the rules
test's scan of their rows, carry the ``sec_full`` marker and are skipped, with the reason
shown, unless ``UKLIB_SEC_FULL=1`` is set.  So do the slower tests' other cases
(``GRIDS``), each test's docstring saying which.  They are never dropped: one leg of the CI
matrix sets it, and ``UKLIB_SEC_FULL=1 python -m pytest -m sec_full
lifelib/libraries/uklib/tests/test_with_profits_uk_sec.py`` runs them alone.  Each splice
row is released once it has been read (``_release``), as ``run_sec.py --block`` releases
its points.

Every test keeps four rules.  Each model is read under a name of its own and closed:
``conftest.with_profits`` reads S under its default name, and reading a model under a name
in use renames the open one.  No test writes inside the library tree: every changed input
goes through ``uk_sec_support.temp_inputs`` into a temporary directory, because a CSV added
beside the models, even briefly, would fail a concurrent
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
    SEC_SPECS, TWIN_EXEMPT_DEFAULT, build_sec_table, check_generated, codes,
    fingerprint_mismatches, frame_mismatches, full_sweep, sweep, temp_inputs,
    twin_mismatches)

SEC, TWIN = "WP_UK_SEC", "WP_UK_S"
TABLE = "model_point_table_sec.csv"
SPEC = SEC_SPECS[SEC]

# S's seven points: the worked example's bond in force 60 months at +7% (1) and -15% (2),
# on a 5% return (3), and with the 5% withdrawal election (4); the endowment issued at the
# valuation date (5) and in force 240 months on a gross pension basis (6); and the down
# scenario's bond issued at the valuation date with the withdrawal election (7), the bond
# variant the spec adds to S's table.
S_POINTS = (1, 2, 3, 4, 5, 6, 7)

# Six more S points, in the splice's copy of S's table and never in the committed one, each
# one of S's points changed so as to reach what S's own points cannot:
#
# 8, S point 1 as a woman: the mortality table's female rows, which no S point reads;
# 9, S point 2 at -40%, the crash the S module uses: the corridor's ceiling binding a
#   month after the cap's floor, the charge cap from 115 and the asset share floored from
#   154;
# 10, S point 3 on the pension tax basis: a bond on the other basis, which no S bond holds;
# 11, S point 7 at 5% without withdrawals: a bond issued at the valuation date whose charge
#   cap binds from 442, the cap a +5% bond reopened late without its charges misses;
# 12, S point 7 at 5% with them: its cap from 197, and its units exhausted at 303;
# 13, S point 7 without withdrawals: the -15% bond issued at the valuation date, its charges
#   stopping from 101, which a bond reopened at 60 without them would charge on past;
# 14, S point 2 at a 6% bonus: under the rule, its first declaration in S's rule, at 83, cut
#   by the change cap, 1.5%, to 4.5%, above the floor;
# 15, S point 1 at a 12% return and a 20% bonus: its guarantee outruns its asset share,
#   whose rise outruns the smoothed payout, so that the MVR is held to its contractual
#   bound, the guarantee less the asset share, from 71;
# 16, S point 7 at 5% with a 6% withdrawal: under the rule its units run out at policy
#   month 287, so its frame ends the month before a declaration, the bonus rate's frame
#   bound at its edge.
#
# Each variant is (the S point it changes, the columns it changes); the policy_id keeps the
# generated ids apart.  11 to 13 are new business, so their twins are cases too: an issue
# month no S bond but point 7 takes.
VARIANTS = {
    8: (1, {"policy_id": "WP-900008", "sex": "F"}),
    9: (2, {"policy_id": "WP-900009", "fund_return": -0.40}),
    10: (3, {"policy_id": "WP-900010", "tax_basis": "pension_gross"}),
    11: (7, {"policy_id": "WP-900011", "wd_rate": 0.0, "fund_return": 0.05,
             "bonus_rate": 0.02}),
    12: (7, {"policy_id": "WP-900012", "fund_return": 0.05, "bonus_rate": 0.02}),
    13: (7, {"policy_id": "WP-900013", "wd_rate": 0.0}),
    14: (2, {"policy_id": "WP-900014", "bonus_rate": 0.06}),
    15: (1, {"policy_id": "WP-900015", "fund_return": 0.12, "bonus_rate": 0.20}),
    16: (7, {"policy_id": "WP-900016", "fund_return": 0.05, "bonus_rate": 0.02,
             "wd_rate": 0.06}),
}

# T2's months under the main set of References (UKLIB-SEC-PLAN.md §6.5), S months, each
# after the point's own entry and inside its frame.  The declarations at the end of each
# policy year's twelfth month, 71, 119, and on the endowment 11 and 287, the month after
# each and mid-year; on the down scenario the smoothing cap's floor from 61, the market
# value reduction from 68, the corridor's ceiling from 92, the guarantee window, 106, 107
# and 118 to 120, the encashment at 119, the corridor again at 131, 144, 154 and 155, the
# charge's cap from 160 and the asset share's floor from 242; the 5% bond's cap from 504,
# where it flickers monthly; the withdrawing bond's cap from 284 and its exhaustion at
# 403, its last month 402; on the endowment the cap's ceiling at 289 and 290 and maturity
# at 299; the bond variant's cap from 88, and past it at 100, its floor from 196 and its
# last month, 266; and the limiting age's last month, 779.  The events are S's under
# SPLICED_REFS, whose estate
# distribution moves the charge's cap and the floor a few months from where S ships them.
SPLICE_MTHS = {
    1: (61, 65, 71, 72, 119, 120, 125, 778, 779),
    2: (61, 64, 65, 67, 68, 71, 72, 92, 93, 106, 107, 118, 119, 120, 125, 131, 144, 154,
        155, 159, 160, 161, 241, 242, 243, 600, 779),
    3: (71, 72, 503, 504, 505, 779),
    4: (65, 71, 119, 283, 284, 285, 396, 401, 402),
    5: (1, 11, 12, 13, 65, 125, 287, 288, 289, 290, 299),
    6: (241, 287, 288, 289, 290, 299),
    7: (1, 11, 12, 87, 88, 89, 100, 106, 107, 119, 120, 195, 196, 197, 266),
}
VARIANT_MTHS = {8: (65, 119, 779), 9: (61, 65, 66, 71, 92, 115, 116, 119, 153, 154),
                10: (71, 119), 11: (1, 441, 442, 443), 12: (1, 196, 197, 198, 302),
                13: (1, 100, 101, 102, 600), 15: (71, 85)}

# The second set's months, with the bonus rule on: each declaration the rule sets, the
# first in S's frame at 83 on the bonds in force and at 11 and 23 on the bonds issued at the
# valuation date, the month after it and mid-year; the endowment's; and the withdrawing
# variant's frame, whose units run out at policy month 400 under the rule, in its 34th
# policy year, the partial year whose rate the frame bounds: restated before that year, at
# 395, and inside it, at 397, where its rate is the row's own.
RULE_MTHS = {1: (61, 83, 84, 125), 2: (83, 84, 119), 5: (11, 12, 13, 150, 299),
             7: (1, 23, 24, 100), 12: (1, 302, 395, 397), 14: (83, 95), 16: (275, 280)}

# The third set's months, a deterrent of 25, under which the surrender rate is held to its
# bound, 1, wherever the market value reduction applies: the down scenario the month before
# it turns on, 67.
BOUND_MTHS = {2: (67,)}

# T3's months: issued one month on, which puts the policy anniversaries a month off the
# valuation years; twelve, which puts them back on; and the horizon, 120, the latest the
# table admits.  Each new-business variant is issued 13 months on, more than a year after
# the valuation date and off its anniversaries (USLIB-SEC-PLAN.md §7.1, *Record — M14*,
# *Splice grid*).  The endowment is closed to new business, and is issued later all the
# same, as a projection's mechanics.
FUTURE_MTHS = (1, 12, 120)
LATE_FUTURES = ((11, 13), (12, 13), (13, 13))


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


# The month each S point and variant enters S's frame: 60 on the bonds in force, 240 on the
# endowment in force, 0 on new business.
ENTRY = {p: 12 * int(y) for p, y in _s_table_with_variants()["duration_inforce"].items()}

# The committed rows the generator reads from S under References of their own (the spec's
# derived_refs), by (S policy, month), with those References.
UNDER_REFS = {(_s_table().at[p, "policy_id"], d): refs
              for (p, d), refs in SPEC.derived_refs.items()}

# T2's cases, as (row_kind, S point, source_mth, set): each S point and variant restated in
# force at each of its months, and the twins of S's points in force, at their own months,
# and of the new business, at 0, on each set.  T3's cases, as (S point, k, set).
SPLICES = (tuple(("derived", p, d, "main") for p in S_POINTS for d in SPLICE_MTHS[p])
           + tuple(("derived", p, d, "main") for p, mths in VARIANT_MTHS.items()
                   for d in mths)
           + tuple(("derived", p, d, "rule") for p, mths in RULE_MTHS.items()
                   for d in mths)
           + tuple(("derived", p, d, "bound") for p, mths in BOUND_MTHS.items()
                   for d in mths))
IN_FORCE_TWINS = (tuple(("twin", p, ENTRY[p], "main") for p in (*S_POINTS, *VARIANTS))
                  + tuple(("twin", p, ENTRY[p], "rule") for p in (1, 5, 6, 7, 12)))
FUTURES = (tuple((p, k, "main") for p in (5, 7) for k in FUTURE_MTHS)
           + tuple((p, k, "main") for p, k in LATE_FUTURES)
           + ((7, 13, "rule"), (12, 13, "rule")))

# The default run's cases (the module docstring), each with what it is there for.  The
# rest of SPLICES, IN_FORCE_TWINS and FUTURES run with UKLIB_SEC_FULL=1.
CORE_SPLICES = {
    ("twin", 1, 60, "main"): "S's worked example in force, an anniversary valuation",
    ("twin", 4, 60, "main"): "S's withdrawing bond in force, to its exhaustion",
    ("twin", 6, 240, "main"): "S's endowment in force, to maturity",
    ("twin", 7, 0, "main"): "the bond variant issued at the valuation date",
    ("derived", 1, 71, "main"): "a declaration at the end of month 0",
    ("derived", 1, 779, "main"): "the limiting age's last month, a one-row frame",
    ("derived", 2, 65, "main"): "mid-year, the smoothing cap's floor binding",
    ("derived", 2, 68, "main"): "the market value reduction turning on",
    ("derived", 2, 92, "main"): "the corridor's ceiling binding",
    ("derived", 2, 107, "main"): "inside the guarantee-imminent window",
    ("derived", 2, 119, "main"): "the guarantee date in month 0, the encashment",
    ("derived", 2, 242, "main"): "the asset share floored at 0, the payout with it",
    ("derived", 3, 504, "main"): "the 5% bond as its charge cap binds",
    ("derived", 4, 402, "main"): "the withdrawing bond's last month, a forced encashment",
    ("derived", 5, 1, "main"): "the endowment in its second month",
    ("derived", 5, 11, "main"): "the endowment's first declaration in month 0",
    ("derived", 5, 290, "main"): "the endowment's payout at the cap's ceiling",
    ("derived", 5, 299, "main"): "the endowment's maturity, a one-row frame",
    ("derived", 7, 100, "main"): "the bond variant past its charge cap",
    ("derived", 7, 266, "main"): "the bond variant's last month, floored and exhausted",
    ("derived", 8, 119, "main"): "a woman on her guarantee date",
    ("derived", 9, 92, "main"): "the -40% crash, the corridor's ceiling binding",
    ("derived", 10, 71, "main"): "a bond on the pension tax basis",
    ("derived", 11, 443, "main"): "the +5% bond issued at t = 0, past its charge cap",
    ("derived", 13, 102, "main"): "the -15% bond issued at t = 0, past its charge cap",
    ("twin", 1, 60, "rule"): "S's worked example in force: its first declaration, D6's",
    ("derived", 1, 83, "rule"): "the rule's declaration as month 0's own event",
    ("derived", 1, 84, "rule"): "the rule's year under way, from S's declared rate",
    ("derived", 2, 84, "rule"): "the down scenario under the rule, its rate floored",
    ("derived", 5, 150, "rule"): "the endowment under the rule, mid-term",
    ("derived", 12, 302, "rule"): "the withdrawing bond under the rule, to its cut year",
    ("derived", 14, 83, "rule"): "a 6% rate the rule cuts by its cap, above the floor",
    ("derived", 16, 280, "rule"): "a frame ending the month before a declaration",
    ("derived", 15, 71, "main"): "a 20% bonus on a 12% return: the MVR at its bound",
    ("derived", 2, 67, "bound"): "a deterrent of 25: the surrender rate at its bound",
}
CORE_FUTURES = {
    (7, 1, "main"): "the bond variant a month off the valuation anniversaries",
    (12, 13, "rule"): "the withdrawing bond more than a year on, under the rule",
}

SEC_FULL = os.environ.get("UKLIB_SEC_FULL") == "1"
FULL_ONLY = (pytest.mark.sec_full,
             pytest.mark.skipif(not SEC_FULL, reason="the full splice grid runs with "
                                "UKLIB_SEC_FULL=1 (UKLIB-SEC-PLAN.md U6)"))

# The tests that run over every committed point run the core's by default and the rest on
# the full grid (GRIDS): the in-force twins of S's withdrawing bond and its endowment, the
# bond issued at the valuation date, the down scenario on its guarantee date and with its
# asset share floored, the withdrawing bond's last month, the endowment at its first
# declaration, the bond variant past its cap, the future row and the rows under the
# doubled charge and under the rule, by label, among which every flow and every counted
# cell is nonzero.
CORE_POINTS = (4, 6, 7, 11, 12, 14, 15, 18, 19, 20, 22)
GRIDS = [pytest.param("core", id="core"), pytest.param("full", id="full", marks=FULL_ONLY)]


def _on_grid(grid, label):
    """Whether committed point ``label`` is one the ``grid`` case of a test runs on."""
    return (label in CORE_POINTS) == (grid == "core")


# What the main splice sets in both models, S and SEC alike, before either evaluates
# anything.  One input runs on the valuation clock (D7): expense inflation, which S runs
# from issue and SEC from the valuation date, so at the shipped 3% the expenses of a point
# opened at d differ by the inflation of the policy years before d, by design, and at 0 both
# factors are 1; its clock is then asserted on its own, with its rate on.  The fund return
# and the bonus rate are levels of the model point, no path, so no input table moves with
# d.  The one assumption that ships at zero, the estate distribution, is on, at a hundredth
# of a percent of the asset share a month, so that the opening asset share feeds it in
# every month.  And two References a formula could confuse with another that ships equal
# are set apart from it: the MVR deterrent, which ships at the 0.6 of mortality's
# best-estimate factor, at 0.65, and the guarantee-imminent factor, which ships at the 0.8
# of the corridor's floor, at 0.75.  The identity does not depend on the values, only on
# both models having the same ones.  The bonus rule ships off, and the second set switches
# it on (RULE_REFS).
SPLICED_REFS = {"inflation_rate": 0.0, "misc_surplus_rate": 0.0001,
                "mvr_deterrent_factor": 0.65, "guarantee_imminent_factor": 0.75}

# The second set: the main one with the bonus rule on, its guarantee-fill target and its
# annual change cap set apart from the corridor's floor and the annual management charge
# they ship equal to.
RULE_REFS = {**SPLICED_REFS, "bonus_rule_on": True, "guar_fill_target": 0.85,
             "bonus_change_cap": 0.015}
# The third set: the main one with the MVR deterrent at 25, which takes the surrender rate
# to its bound, 1, wherever the market value reduction applies (UKLIB-SEC-PLAN.md §6.5;
# ULB_UK_SEC's T2 variant for its own bound).
BOUND_REFS = {**SPLICED_REFS, "mvr_deterrent_factor": 25.0}
REF_SETS = {"main": SPLICED_REFS, "rule": RULE_REFS, "bound": BOUND_REFS}

# Every switch that ships off, on, for T4, at the shipped inflation: the second set's.
SWITCHED_ON = {ref: value for ref, value in RULE_REFS.items() if ref != "inflation_rate"}

# The accessors of S's columns that open its frame: on a row restated at d, S's value is
# the column at S's own opening, 60 or 240 or issue, and SEC's the state at d, by design;
# the cells they open are compared.  And declaration_month, which S returns as a policy month
# and SEC as a valuation month, the same number only where the clocks coincide; a test of
# its own holds its form.
OPENING = frozenset({"asset_share_init", "units_init", "unit_price_init",
                     "smoothed_payout_init", "bonus_rate_init"})

# The reports, which the comparison reads as frames rather than as cells.
REPORTS = ("result_cf", "result_payout", "result_pols")

# The cells T2 and T3 skip beyond T1's (the spec's exempt): proj_len counts from the
# valuation date on SEC and from issue on S, so it differs by d, or by -k, by design;
# frame_mismatches asserts what it must get right, that both frames end at the same
# instant.  OPENING's, for their reason.  And the reports, compared as frames.
SPLICE_EXEMPT = (TWIN_EXEMPT_DEFAULT | SPEC.exempt | OPENING
                 | {"proj_len", "declaration_month", *REPORTS})
FUTURE_EXEMPT = SPLICE_EXEMPT

# The result_cf columns that expense inflation moves, and the cells they are made of: on
# the committed points, at the shipped 3%, the only places an in-force row departs from S.
INFLATED = ("expenses", "net_cf")
INFLATION_CELLS = frozenset({"inflation_factor", "expenses", "net_cf"})

# The S cells whose exact value is 0 and whose computed value is rounding about it, the
# roll-forwards' residuals: a comparison with S holds them at the harness's absolute floor
# of 1e-9, and every other cell at none (_compare).
RESIDUALS = frozenset({"check_pols_roll_fwd_resid", "check_asset_share_roll_fwd_resid"})
FLOOR = 1e-9

# The S cells whose value is the difference of two amounts equal in many months: the
# smoothing cost of an exit, the claim less the asset share it releases.  Where the payout
# is the asset share, the computed value is rounding about 0 at the asset share's last
# bit, 2.9e-11 on the 5% bond at 487, and an opening state read back from the CSV one ulp
# off moves it, so a comparison holds it to the residuals' floor (_compare).
DIFFERENCES = frozenset({"smoothing_cost_pp"})
FLOORED = RESIDUALS | DIFFERENCES

# The reads keyed by an attained age or a policy year, and the monthly rates, none of which
# may be evaluated before issue (R1, D4).
KEYED_READS = ("age", "duration", "policy_year", "mort_rate", "surr_rate_base",
               "mort_rate_mth", "surr_rate_mth")

# The cells that scale with the count.  Every other cell is a per-policy amount, a rate, a
# factor, a clock or a flag, and must not move when the count does.
COUNTED = frozenset({
    "policy_count", "pols_if_init", "pols_if", "pols_if_at", "pols_new_biz", "pols_death",
    "pols_surr", "pols_maturity", "premiums", "withdrawals", "claims", "expenses",
    "shareholder_transfers", "smoothing_cost", "smoothing_account",
    "smoothing_account_refusal", "net_cf", "check_pols_roll_fwd_resid", "result_cf",
    "result_payout", "result_pols"})

# result_pols' columns, in its order: the count, the new business within it, the month's
# deaths and surrenders in processing order, and the survivors of the frame's last month.
RESULT_POLS = ["pols_if", "pols_new_biz", "pols_death", "pols_surr", "pols_maturity"]

# result_payout's columns: each a per-policy amount or a rate, but the smoothing account,
# which sums the exits of the count.
PAYOUT_COUNTED = ("smoothing_account",)

# S's three timings and BEF_NB, the one running in force adds; the asset share's six; and
# the kinds.
TIMINGS = ("BEF_NB", "BEF_DECR", "BEF_SURR", "AFT_DECR")
AS_TIMINGS = ("BEF_PREM", "BEF_RETURN", "AFT_RETURN", "AFT_CHARGE", "AFT_ST", "AFT_MC")
KINDS = ("DEATH", "SURRENDER", "MATURITY")
CLAIM_KINDS = ("DEATH", "SURRENDER", "GUARANTEE", "MATURITY")

# What each cell holds outside cover, before issue and from the month cover has ended, as
# its docstring says: no count, so no cash flow; no balance, price or rate read at a policy
# year or an age the policy does not have; no declaration, guarantee date or window.  The
# type is part of the value.  A count is a float in every branch and a flag a bool, because
# the C step types a cell by the values it returns (USLIB-SEC-PLAN.md F3).  The guard test
# also calls pols_if_at at each timing and asset_share_at at each, all 0.0.
OUTSIDE_COVER = {
    "is_active": False, "is_declaration_month": False, "is_guarantee_date": False,
    "premium_pp": 0.0, "wd_pp": 0.0, "wd_as_pp": 0.0, "guar_charge_rate": 0.0,
    "guar_charge_rate_mth": 0.0, "guar_charge_pp": 0.0, "guar_charge_cum_pp": 0.0,
    "misc_surplus_pp": 0.0, "asset_share": 0.0, "unit_price": 0.0, "units": 0.0,
    "guar_benefit_pp": 0.0, "guar_benefit_open": 0.0, "bonus_rate": 0.0,
    "cost_of_bonus_pp": 0.0, "shareholder_transfer_pp": 0.0, "mort_rate": 0.0,
    "mort_rate_mth": 0.0, "mort_charge_pp": 0.0, "smoothed_payout": 0.0,
    "smoothed_payout_open": 0.0, "final_bonus_pp": 0.0, "mvr_pp": 0.0,
    "mvr_applied_pp": 0.0, "surr_rate_base": 0.0, "surr_rate": 0.0, "surr_rate_mth": 0.0,
    "pols_if": 0.0, "pols_new_biz": 0.0, "pols_death": 0.0, "pols_surr": 0.0,
    "pols_maturity": 0.0, "premiums": 0.0, "withdrawals": 0.0, "claims": 0.0,
    "expenses": 0.0, "shareholder_transfers": 0.0, "smoothing_cost": 0.0,
    "smoothing_account": 0.0, "net_cf": 0.0, "check_pols_roll_fwd_resid": 0.0}

# The cells a month outside cover may not reach: the clocks of the contract, each keyed
# by a policy year or an attained age.  The reads that guard themselves are held by their
# values in OUTSIDE_COVER instead.
IN_COVER_ONLY = ("age", "policy_year", "duration")

# The opening state, in the table's order, and the cells running in force adds to
# WP_UK_S's, each of which the symbol map must name.
STATE = ("units_init", "unit_price_init", "attaching_bonus_init", "asset_share_init",
         "smoothed_payout_init", "bonus_rate_init", "guar_charge_cum_pp_init",
         "smoothing_account_init")
NEW_CELLS = ("policy_count", "duration_mth_init", "t_entry", "is_active", "cover_end_mth",
             "pols_new_biz", "result_pols", "attaching_bonus_init", "guar_charge_cum_pp_init",
             "smoothing_account_init")

INFLATION = 0.03        # the shipped inflation_rate, which the inflation test reads

# The edges of the floats the domains and the past-the-floats cases read.
BIG = 1.7976931348623157e308
WHOLE = 2.0 ** 53
BELOW_0 = math.nextafter(0.0, -1.0)
ABOVE_0 = math.nextafter(0.0, 1.0)
ABOVE_1 = math.nextafter(1.0, 2.0)
BELOW_1 = math.nextafter(1.0, 0.0)

# The recursion limit, as mx.set_recursion takes it, under which the committed points are
# first swept (R2, F7).  A report evaluates each column in ascending t, so a forward
# recursion, through t - 1, finds the month before already cached.  A backward recursion
# over the frame, through t + 1, opens a chain as long as the frame, and the shortest
# committed frame of more than a row is 167.
CALL_DEPTH = 60

# The reads beyond t + 1 the model makes, as (reader, cell read): the bonus rate's read of
# the rate of the declaration closing its policy year, up to 11 months ahead, R2's
# anniversary read, with the bonus rule on.  The rules test admits it, and asserts each
# such read lies inside the frame.  The exhaustion search reads the units of the month
# they run out, from a cell that takes no month, which a test of its own holds.
LOOK_AHEAD = frozenset({("bonus_rate", "bonus_rate")})


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

    ``month`` is the row's ``source_mth``: S's entry month for a twin, ``d`` for a derived
    row, ``-k`` for a future one.  The twins keep S's ``point_id`` and ``policy_id``, so the
    S policy is the twin's.
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
    --block`` releases its points (USLIB-SEC-PLAN.md F5).  Asked for again, the ItemSpace is
    made afresh and recomputes.
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
    """WP_UK_SEC read from a copy whose SEC table is ``edit(_committed())``."""
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

    :func:`uk_sec_support.sweep` reaches ``WP_UK_S``'s ``pols_if_at`` at two of its
    timings, ``asset_share_at`` at the timings the recursion reads, and ``claim_pp`` and
    ``smoothing_cost_pp`` at the kinds the flows read; nor ``duration_mth``, which no S
    formula reads, nor ``policy_value_pp``, ``is_guarantee_date``, ``guarantee_imminent`` or
    ``death_guar_pp`` where no flow asks.  A cell S never evaluates is compared nowhere, so
    they are evaluated here, over the frame, and the splice and the future comparison see
    them too.
    """
    sweep(proj)
    for t in range(proj.proj_start(), proj.proj_len()):
        for timing in ("BEF_DECR", "BEF_SURR", "AFT_DECR"):
            proj.pols_if_at(t, timing)
        for timing in AS_TIMINGS:
            proj.asset_share_at(t, timing)
        for kind in CLAIM_KINDS:
            proj.claim_pp(t, kind)
            proj.smoothing_cost_pp(t, kind)
        proj.duration_mth(t)
        proj.policy_value_pp(t)
        proj.policy_value_open(t)
        proj.is_guarantee_date(t)
        proj.guarantee_imminent(t)
        proj.death_guar_pp(t)
        proj.guar_benefit_open(t)
        proj.smoothed_payout_capped(t)


def _departure(s_proj, month):
    """Where SEC's bonus rate departs from S's by design on a row: ``(S month, rate)``, or
    ``None``.

    With the bonus rule on, each month reads the rate declared at the end of its policy
    year.  Where a forced encashment ends the frame mid-year, no declaration falls in the
    frame in the year it ends in, and S reads the rate past its frame, where this model
    reads the rate declared before the year (``bonus_rate``'s docstring, the recorded
    departure).  So the months of that year, S months from its first, ``12 x ((L - 1) //
    12)``, to the frame's last, ``L - 1``, S's policy months, are the departure, unless the
    year is the one under way at the row's valuation date, S month ``month``, whose rate is
    the row's column and S's own; returned with the rate this model reads there, S's of
    the year before, declared the month before the year.  It changes ``bonus_rate`` in
    those months, and the ``bonus_rate`` column of ``result_payout``, and no other cell: no
    declaration falls in them.
    """
    if not (s_proj.bonus_rule_on and s_proj.is_forced_encashment()):
        return None
    end = s_proj.proj_len()
    first = 12 * ((end - 1) // 12)
    if end % 12 == 0:
        return None
    return first, s_proj.bonus_rate(first - 1)


def _carried_cut(s_proj, month):
    """The S month of a row's first declaration in the frame, where S makes it from its
    carried column rather than by its rule; or ``None``.

    Under the rule every declaration in this model's frame is the rule's, at today's
    References (D6), but ``WP_UK_S``'s first frame year keeps its column: so a twin of S's
    points, in force or new, and a row valued inside S's first frame year, part from S at
    their first declaration in the frame, the departure ``model-sec.md`` records.  The
    comparison runs to the month before it, S month ``cut``, but on the ``bonus_rate``,
    which every month of the year reads from that declaration.
    """
    if not s_proj.bonus_rule_on:
        return None
    first = 11 if month < 0 else 12 * (month // 12) + 11
    if first <= s_proj.proj_start() + 11 and first < s_proj.proj_len():
        return first
    return None


def _s_result_pols(s_proj):
    """S's counts as ``result_pols`` sets them out, from S's own cells.

    ``WP_UK_S`` has no ``result_pols``: its frame's rows are S months from
    ``proj_start()``, each holding S's ``pols_if``, ``pols_death``, ``pols_surr`` and
    ``pols_maturity``, and the new business is the count S opens a frame from issue with,
    ``pols_if_init()``, in its month 0.
    """
    ts = list(range(s_proj.proj_start(), s_proj.proj_len()))
    new = s_proj.pols_if_init() if s_proj.proj_start() == 0 else 0.0
    return pd.DataFrame(
        {"pols_if": [s_proj.pols_if(t) for t in ts],
         "pols_new_biz": [new if t == 0 else 0.0 for t in ts],
         "pols_death": [s_proj.pols_death(t) for t in ts],
         "pols_surr": [s_proj.pols_surr(t) for t in ts],
         "pols_maturity": [s_proj.pols_maturity(t) for t in ts]},
        index=pd.Index(ts, name="t"))


def _compare(s_proj, sec_proj, month, exempt, columns=None):
    """Where SEC's row departs from S's point from S month ``month`` on, in three passes.

    First the frames, ``result_cf`` (over ``columns``, or every column both hold),
    ``result_payout`` and ``result_pols``, SEC row ``t`` against S row ``t + month``, frames
    ending together; then every cell of S's but ``exempt`` and :data:`RESIDUALS`, at every
    argument S cached inside its frame from ``month`` on, moved onto SEC's clock, S's
    timing and kind strings mapped onto SEC's codes (``uk_sec_support.codes``).  Both to
    1e-9 relative with no absolute floor (USLIB-SEC-PLAN.md §5.2, T2, precised at M11): a
    floor of 1e-9 passes an error of 1% in any value below 1e-7.  Then the cells of
    :data:`RESIDUALS` and :data:`DIFFERENCES` alone, at the floor of 1e-9: a residual's
    exact value is 0, and a difference's is in many months, and the computed one moves by
    an ulp of what it closes when an opening state comes back from the CSV one ulp off.  The
    bonus rate's recorded departure in a cut year (:func:`_departure`) is compared over the
    months before it, and held to its own rate in its months; a row whose first declaration
    S makes from its carried column (:func:`_carried_cut`) is compared to the month before
    that declaration.  Returns the mismatch lines, empty when the row is S's.
    """
    found = []
    cut = _carried_cut(s_proj, month)
    gone = None if cut is not None else _departure(s_proj, month)

    def arg_map(name, args):
        if cut is not None and (name == "bonus_rate"
                                or (args and _month(args[0]) and args[0] >= cut)):
            return None
        if gone is not None and name == "bonus_rate" and args[0] >= gone[0]:
            return None
        return args

    for report, keep in (("result_cf", columns), ("result_payout", None),
                         ("result_pols", None)):
        sec_df = sec_proj.cells[report]()
        s_df = (_s_result_pols(s_proj) if report == "result_pols"
                else s_proj.cells[report]())
        if cut is not None:
            if cut <= month:
                continue                    # month 0's declaration: nothing before it
            names = [c for c in (s_df.columns if keep is None else keep)
                     if c in sec_df.columns and c != "bonus_rate"]
            found += [f"{report} before the first declaration: {line}"
                      for line in frame_mismatches(
                          s_df[s_df.index < cut], sec_df[sec_df.index < cut - month],
                          t_offset=month, columns=names, atol=0.0)]
            continue
        if report == "result_payout" and gone is not None:
            found += [f"{report}: {line}" for line in frame_mismatches(
                s_df, sec_df, t_offset=month,
                columns=[c for c in s_df.columns if c != "bonus_rate"], atol=0.0)]
            start = gone[0] - month
            if start > 0:
                found += [f"{report} before the departure: {line}"
                          for line in frame_mismatches(
                              s_df[s_df.index < gone[0]], sec_df[sec_df.index < start],
                              t_offset=month, columns=["bonus_rate"], atol=0.0)]
            held = sec_df.loc[sec_df.index >= start, "bonus_rate"]
            if not (held == gone[1]).all():
                found.append(f"the departure's months hold {sorted(set(held))}, not the "
                             f"rate declared before them, {gone[1]}")
            continue
        found += [f"{report}: {line}" for line in frame_mismatches(
            s_df, sec_df, t_offset=month, columns=keep, atol=0.0)]
    found += twin_mismatches(s_proj, sec_proj, t_offset=month, exempt=exempt | FLOORED,
                             arg_map=arg_map, atol=0.0, codes=codes(sec_proj))
    return found + twin_mismatches(s_proj, sec_proj, t_offset=month,
                                   exempt=exempt | (set(s_proj.cells) - FLOORED),
                                   arg_map=arg_map, atol=FLOOR, codes=codes(sec_proj))


def _continues_s(s_proj, sec_proj, month):
    """Where a committed row departs from S's point ``s_proj`` from S month ``month`` on.

    The splice's comparison (:func:`_compare`), on the committed model at the shipped
    assumptions: frame by frame, then cell by cell over every cell of S's but
    :data:`SPLICE_EXEMPT`.  The shipped 3% expense inflation runs from issue in S and from
    the valuation date here (D7), so :data:`INFLATED`'s two columns, and
    :data:`INFLATION_CELLS`, differ by design and are left out; the inflation test holds
    them.  Every other column and cell must agree, to 1e-9 relative, with no absolute floor
    but on the residuals.
    """
    keep = [c for c in s_proj.result_cf().columns if c not in INFLATED]
    return _compare(s_proj, sec_proj, month, SPLICE_EXEMPT | INFLATION_CELLS, keep)


def _case_id(kind, s_point, month, refs="main"):
    """A case's id: ``point2-d119``, ``point2-twin60-rule``, or ``point7-k13`` if issued
    later."""
    tail = "" if refs == "main" else f"-{refs}"
    if kind == "future":
        return f"point{s_point}-k{-month}{tail}"
    return f"point{s_point}-" + (f"d{month}" if kind == "derived" else f"{kind}{month}") + tail


def _case(case, core, case_id):
    """One parametrized case: run by default if it is in ``core``, else on the full grid."""
    return pytest.param(*case, id=case_id, marks=() if case in core else FULL_ONLY)


def _selected(cases, core):
    """The cases this run makes rows for: the core, or every one under UKLIB_SEC_FULL."""
    return [case for case in cases if SEC_FULL or case in core]


# Every row the splice compares, as (row_kind, S point, source_mth, set), T3's included,
# and the default run's among them.
GRID = (*SPLICES, *IN_FORCE_TWINS, *(("future", p, -k, refs) for p, k, refs in FUTURES))
CORE_GRID = frozenset({*CORE_SPLICES, *(("future", p, -k, refs)
                                        for p, k, refs in CORE_FUTURES)})


# ---------------------------------------------------------------------------
# Fixtures


@pytest.fixture(scope="module")
def sec_read():
    """WP_UK_SEC read in place, as committed, and swept once, cold; what it met.

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
    first = _row(model, "twin", 1, 60)
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
    """WP_UK_SEC read in place, as committed, with every point swept (sec_read)."""
    return sec_read[0]


@pytest.fixture(scope="module")
def s_model():
    """WP_UK_S read in place, as committed, with every point swept.

    T6 regenerates the SEC inputs from it, which would otherwise project every S point
    again (USLIB-SEC-PLAN.md §4, *Carried into Phase 1*), and the in-force tests read S's
    months off it.
    """
    model = mx.read_model(model_path(TWIN), name=_name("s"))
    for key in point_keys(model):
        _sweep_s(projection(model, key))
    yield model
    model.close()


def _spliced_pair(root, refs, set_name):
    """S and SEC on one set of the splice's inputs, ``refs`` set in both: see
    :func:`spliced`."""
    s_folder = temp_inputs(root / "s", model_path(TWIN), model_points=_s_table_with_variants())
    s = mx.read_model(s_folder, name=_name(f"s_{set_name}"))
    for ref, value in refs.items():
        setattr(s.Projection, ref, value)
    chosen = [case for case in _selected(SPLICES + IN_FORCE_TWINS, CORE_SPLICES)
              if case[3] == set_name]
    derived = [(p, d) for kind, p, d, _ in chosen if kind == "derived"]
    futures = [(p, k) for p, k, refs_name in _selected(FUTURES, CORE_FUTURES)
               if refs_name == set_name]
    spec = dataclasses.replace(SPEC, derived=tuple(derived), derived_refs={},
                               future=tuple(futures))
    table, companions = build_sec_table(spec, s)
    assert companions == {}
    sec = mx.read_model(_sec_inputs(root / "sec", table), name=_name(f"sec_{set_name}"))
    for ref, value in refs.items():
        setattr(sec.Projection, ref, value)
    compared = {p for _, p, _, _ in chosen} | {p for p, _ in futures}
    for key, point_id in zip(point_keys(s), s.Data.model_point_table().index):
        if point_id in compared:
            _sweep_s(projection(s, key))
    return s, sec


@pytest.fixture(scope="module")
def spliced(tmp_path_factory):
    """S and SEC on each set of the splice's inputs, ``{set: (s, sec)}``.

    For each set, :data:`SPLICED_REFS` and :data:`RULE_REFS`, S is read from a copy of the
    product directory whose table has the variants appended, with the set's References set.
    SEC runs on the same assumption tables, and on a model point table of its own, built by
    the generator from the registered spec with its rows replaced by the set's cases this
    run selects, the core or the full grid (:func:`_selected`), out of this S model, so each
    row opens with the state of the very run it is compared with.  No input table moves
    with ``d``: WP's one valuation-clock input is the ``inflation_rate`` Reference.  Every S
    point a selected case compares is then swept (:func:`_sweep_s`), and stays swept; each
    SEC row is projected by the case that compares it and released once compared
    (:func:`_settle`).
    """
    root = tmp_path_factory.mktemp("spliced")
    pairs = {name: _spliced_pair(root / name, refs, name) for name, refs in REF_SETS.items()}
    yield pairs
    for s, sec in pairs.values():
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
    "ahead": [...], "outside": [...], "raised": [...]}``: every cached call with a negative
    argument; every precedent keyed by a month before ``t_entry()`` of a call keyed by a
    month at or after it; every precedent keyed by a month beyond ``t + 1`` of a call keyed
    by ``t``, but :data:`LOOK_AHEAD`'s; every read :data:`LOOK_AHEAD` admits that lies past
    the frame, from a month inside it; and every call the full sweep found raising.  A
    precedent is a call's as modelx's dependency graph records it.
    """
    sweep(proj)
    raised = [f"{name}{args}: {text}" for (name, args), text in full_sweep(proj).items()]
    entry, end = proj.t_entry(), proj.proj_len()
    negative, early, ahead, outside = [], [], [], []
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
                if u <= t + 1:
                    continue
                if (name, node.obj.name) in LOOK_AHEAD:
                    if t < end <= u:
                        outside.append(f"{name}{args} -> {node.obj.name}{node.args}")
                    continue
                ahead.append(f"{name}{args} -> {node.obj.name}{node.args}")
    return {"negative": negative, "early": early, "ahead": ahead, "outside": outside,
            "raised": raised}


def _active(x, t):
    return x.is_active(t)


def _first_year(x):
    """The months of the policy year under way at the valuation date, on the books."""
    d = x.duration_mth_init()
    return range(x.t_entry(), x.t_entry() + 12 - max(d, 0) % 12)


# What test_the_core_grid_reaches_every_branch asks of the core's rows in the model's own
# values, which no column of the table shows: each holds of some core row, or of a core row
# in some month of its frame.  At the valuation date, every opening-state column in use, a
# count or an amount apart from its issue value, and each kind of valuation month: an
# anniversary, mid-year, a declaration month and a guarantee date, inside the
# guarantee-imminent window, and with the asset share floored.  Later in the frame, every
# branch and both sides of each min and max the full grid reaches: a declaration on each
# chassis and the cost of each, the smoothing cap's floor and ceiling and the cap skipped,
# the corridor's floor and ceiling, the asset share's floor, the market value reduction
# applied and waived on a guarantee date, the guarantee exercised, the imminent window,
# the charge's cap binding and released, a forced encashment and a maturity paid, the
# limiting age paying nothing, the lapse table inside and past its last year, and with the
# rule on a declaration set by it, its rise and its cut held to the cap and its rate floored
# at 0, a withdrawal capped at the unit fund, which it is in every withdrawing bond's issue
# month, its fund 0, the surrender rate at its bound, under a deterrent of 25, and the MVR
# held to its contractual bound.  Each at-valuation kind is keyed by the set its row runs
# under: the main set must reach every one, and the rule set its declarations' months.
AT_VALUATION = {
    "asset_share_init above 0": lambda x: x.asset_share_init() > 0.0,
    "asset_share_init 0 in force": lambda x: (
        x.duration_mth_init() > 0 and x.asset_share_init() == 0.0),
    "units_init above 0": lambda x: x.units_init() > 0.0,
    "unit_price_init above the seed": lambda x: x.unit_price_init() > 1.0,
    "attaching_bonus_init above 0": lambda x: x.attaching_bonus_init() > 0.0,
    "smoothed_payout_init above 0": lambda x: x.smoothed_payout_init() > 0.0,
    "guar_charge_cum_pp_init above 0": lambda x: x.guar_charge_cum_pp_init() > 0.0,
    "smoothing_account_init above 0": lambda x: x.smoothing_account_init() > 0.0,
    "smoothing_account_init below 0": lambda x: x.smoothing_account_init() < 0.0,
    "valued on an anniversary": lambda x: (
        x.duration_mth_init() > 0 and x.duration_mth_init() % 12 == 0),
    "valued mid-year": lambda x: x.duration_mth_init() % 12 not in (0, 11),
    "valued in a declaration month": lambda x: (
        x.duration_mth_init() > 0 and x.is_declaration_month(0)),
    "valued on a guarantee date": lambda x: (
        x.duration_mth_init() > 0 and x.is_guarantee_date(0)),
    "valued inside the guarantee-imminent window": lambda x: (
        x.duration_mth_init() > 0 and x.guarantee_imminent(0) != 1.0),
    "valued past the charge's cap": lambda x: (
        x.duration_mth_init() > 0 and x.guar_charge_rate(0) == 0.0),
    "an endowment in force": lambda x: (
        not x.is_unitised() and x.duration_mth_init() > 0),
    "a bond issued at or after the valuation date": lambda x: (
        x.is_unitised() and x.duration_mth_init() <= 0),
}
IN_FRAME = {
    "a declaration on the bond": lambda x, t: (
        x.is_unitised() and x.is_declaration_month(t) and x.cost_of_bonus_pp(t) > 0.0),
    "a declaration on the endowment": lambda x, t: (
        not x.is_unitised() and x.is_declaration_month(t) and x.cost_of_bonus_pp(t) > 0.0),
    "the smoothing cap skipped": lambda x, t: (
        _active(x, t) and x.smoothed_payout_open(t) <= 0.0),
    "the smoothing cap's floor": lambda x, t: (
        _active(x, t) and x.smoothed_payout_open(t) > 0.0
        and x.smoothed_payout_capped(t) == x.smooth_cap_dn_mth()
        * x.smoothed_payout_open(t) and x.asset_share(t) < x.smoothed_payout_capped(t)),
    "the smoothing cap's ceiling": lambda x, t: (
        _active(x, t) and x.smoothed_payout_open(t) > 0.0
        and x.smoothed_payout_capped(t) == x.smooth_cap_up_mth()
        * x.smoothed_payout_open(t) and x.asset_share(t) > x.smoothed_payout_capped(t)),
    "the corridor's floor": lambda x, t: (
        x.asset_share(t) > 0.0
        and x.smoothed_payout(t) == x.corridor_lo * x.asset_share(t)
        and x.smoothed_payout_capped(t) < x.smoothed_payout(t)),
    "the corridor's ceiling": lambda x, t: (
        x.asset_share(t) > 0.0
        and x.smoothed_payout(t) == x.corridor_hi * x.asset_share(t)
        and x.smoothed_payout_capped(t) > x.smoothed_payout(t)),
    "the asset share's floor": lambda x, t: (
        _active(x, t) and x.asset_share_at(t, "AFT_MC") < 0.0),
    "a market value reduction applied": lambda x, t: x.mvr_applied_pp(t) > 0.0,
    "a market value reduction waived on a guarantee date": lambda x, t: (
        x.is_guarantee_date(t) and x.mvr_pp(t) > 0.0),
    "the guarantee exercised": lambda x, t: x.guarantee_exercise(t) > 0.0,
    "the guarantee date out of the money": lambda x, t: (
        x.is_guarantee_date(t) and x.guarantee_exercise(t) == 0.0),
    "the guarantee-imminent window": lambda x, t: (
        _active(x, t) and x.guarantee_imminent(t) != 1.0),
    "the charge's cap binding": lambda x, t: (
        _active(x, t) and x.guar_charge_rate(t) == 0.0),
    "the charge's cap released": lambda x, t: (
        _active(x, t) and t > x.t_entry() and x.guar_charge_rate(t) > 0.0
        and x.guar_charge_rate(t - 1) == 0.0),
    "a forced encashment paid": lambda x, t: (
        x.is_unitised() and x.claim_pp(t, "MATURITY") > 0.0),
    "a maturity paid": lambda x, t: (
        not x.is_unitised() and x.claim_pp(t, "MATURITY") > 0.0),
    "the limiting age paying nothing": lambda x, t: (
        x.is_unitised() and not x.is_forced_encashment() and t == x.proj_len() - 1),
    "inside the lapse table": lambda x, t: (
        _active(x, t) and x.policy_year(t) <= x.data.lapse_last_year(x.chassis())),
    "past the lapse table's last year": lambda x, t: (
        _active(x, t) and x.policy_year(t) > x.data.lapse_last_year(x.chassis())),
    "a rate set by the rule": lambda x, t: (
        _active(x, t) and x.bonus_rule_on and x.is_declaration_month(t)),
    "a rule's rise held to its cap": lambda x, t: (
        _declared(x, t) and _rule_step(x, t)[1] == x.bonus_change_cap),
    "a rule's cut held to its cap, above the floor": lambda x, t: (
        _declared(x, t) and _rule_step(x, t)[1] == -x.bonus_change_cap
        and sum(_rule_step(x, t)) > 0.0),
    "a rule's rate floored at 0": lambda x, t: (
        _declared(x, t) and sum(_rule_step(x, t)) < 0.0),
    "a withdrawal capped at the unit fund": lambda x, t: (
        _active(x, t) and x.is_unitised() and x.wd_rate() > 0.0
        and x.wd_pp(t) < x.wd_rate() * x.premium_single_pp() / 12.0),
    "the surrender rate's bound": lambda x, t: _active(x, t) and x.surr_rate(t) == 1.0,
    "the MVR at its contractual bound": lambda x, t: (
        x.mvr_pp(t) > 0.0 and x.guar_benefit_pp(t) - x.asset_share(t)
        < x.guar_benefit_pp(t) - x.smoothed_payout(t)),
}

# The at-valuation kinds the rule set's core must reach as well as the main set's: the
# months the rule declares in, so that a core row holds a declaration as month 0's own
# event under the rule, and the months either side of one (the M13 review).
RULE_AT_VALUATION = ("valued on an anniversary", "valued mid-year",
                     "valued in a declaration month")
REACHED = frozenset({*(f"{what} [main]" for what in AT_VALUATION),
                     *(f"{what} [rule]" for what in RULE_AT_VALUATION), *IN_FRAME})


def _prev_rate(x, t):
    """The rate the declaration at the end of month ``t`` starts from: the one before it, or
    in the frame's first the rate declared before the valuation date."""
    return x.bonus_rate(t - 12) if t - 12 >= x.t_entry() else x.bonus_rate_init()


def _rule_step(x, t):
    """``(the rate the declaration at the end of month t starts from, its step clamped)``."""
    prev = _prev_rate(x, t)
    step = x.bonus_speed * (x.bonus_supportable(t) - prev)
    return prev, max(-x.bonus_change_cap, min(x.bonus_change_cap, step))


def _declared(x, t):
    """Whether month ``t`` carries a declaration the rule makes."""
    return _active(x, t) and x.bonus_rule_on and x.is_declaration_month(t)


def _branches(x, refs):
    """The names in :data:`AT_VALUATION`, keyed by ``refs``, the set the row runs under, and
    in :data:`IN_FRAME` that hold of row ``x``."""
    reached = {f"{what} [{refs}]" for what, holds in AT_VALUATION.items() if holds(x)}
    frame = range(x.t_entry(), x.proj_len())
    return reached | {what for what, holds in IN_FRAME.items()
                      if any(holds(x, t) for t in frame)}


def _settle(records, case, model, key):
    """Record what the rules and the core grid's reach need of a row, and release it.

    ``case`` is the row's (row_kind, S point, source_mth, set) and ``key`` its registry key
    in ``model``, the splice's SEC model.  A T2 or T3 case calls this once it has compared
    the row, whatever the comparison found, so the row is released either way.  The record
    is :func:`_rule_breaches`'s, with the row's :func:`_branches`, and a row that raises is
    recorded as raising, which the rules test reports.
    """
    try:
        proj = projection(model, key)
        record = _rule_breaches(proj)
        record["branches"] = _branches(proj, case[3])
        record["failed"] = None
    except Exception as err:                    # recorded, and reported by the rules test
        record = {"negative": [], "early": [], "ahead": [], "outside": [], "raised": [],
                  "branches": set(), "failed": _raised(err)}
    finally:
        _release(model, key)
    records[case] = record
    return record


def _record_of(spliced, records, case):
    """The record of ``case``, from the case that compared its row or, failing it, now."""
    if case not in records:
        sec = spliced[case[3]][1]
        _settle(records, case, sec, _row_key(sec, *case[:3]))
    return records[case]


# ---------------------------------------------------------------------------
# T2 -- the splice


@pytest.mark.parametrize(
    "kind, s_point, month, refs",
    [_case(case, CORE_SPLICES, _case_id(*case)) for case in SPLICES + IN_FORCE_TWINS])
def test_an_in_force_point_continues_its_s_projection(spliced, splice_records, kind,
                                                      s_point, month, refs):
    """Opened with S's state at month d, the point is S from d on, in every cell of S's.

    This is the test that says the opening state is complete: a state column the SEC row
    did not carry, or carried from the wrong instant, would make SEC part from S here, and
    nowhere else, because on a point issued at ``t = 0`` the two clocks coincide and the
    opening state is the issue value.  For the same reason it is the test that catches a
    policy month passed as ``t`` (R1a), as a declaration, a guarantee date or a single
    premium read on ``t`` would be.  The frame comparisons read SEC row ``t`` against S row
    ``t + d`` in every column of the three reports both hold, and fail frames that end
    apart.  The cell comparison then evaluates every cell of S's but :data:`SPLICE_EXEMPT`,
    at every argument S cached inside its own frame from month ``d`` on, moved onto SEC's
    clock: the count, the asset share at each step, the units, the price, the guarantee,
    the payout, the bonus rate, the cumulants and the claims of each kind among them.  Each
    compares to 1e-9 relative with no absolute floor, but the roll-forwards' residuals,
    which keep the floor of 1e-9 (:func:`_compare`).  An S cell this model lacked would fail
    it.

    The rows past a cap the cumulants carry are the ones that see a cumulant dropped: the
    -15% and +5% bonds issued at the valuation date, restated past their caps at 102 and
    443, charge on without their charges where S has stopped.  The twins of S's points in
    force are spliced at their own months, and the twins of the new business at 0, on each
    set.  The row is then recorded for the rules test and released (:func:`_settle`).
    """
    s, sec = spliced[refs]
    key = _row_key(sec, kind, s_point, month)
    s_proj, sec_proj = _point(s, s_point), projection(sec, key)
    try:
        assert _compare(s_proj, sec_proj, month, SPLICE_EXEMPT) == []
    finally:
        _settle(splice_records, (kind, s_point, month, refs), sec, key)


# ---------------------------------------------------------------------------
# T3 -- future new business


@pytest.mark.parametrize(
    "s_point, k, refs",
    [_case(case, CORE_FUTURES, _case_id("future", case[0], -case[1], case[2]))
     for case in FUTURES])
def test_future_new_business_is_the_s_projection_k_months_on(spliced, splice_records,
                                                             s_point, k, refs):
    """Issued k months after the valuation date, the point is S's projection k months on.

    SEC rows ``k ..`` are S rows ``0 ..``, ending together at the end of the frame, in the
    three reports, and every cell of S's but :data:`FUTURE_EXEMPT` agrees at every argument
    S cached inside its own frame, moved ``k`` later.  Each compares as the splice compares,
    with no absolute floor but on the residuals (:func:`_compare`).  Before issue every
    column of ``result_cf`` and ``result_pols`` is an exact zero, and the policies arrive in
    month ``k`` as new business, paying the single premium there and nowhere else.

    The last assertions are R1 and D4's base rule made testable.  After the reports, no read
    keyed by an attained age or a policy year, and no rate, has been evaluated at a month
    before issue (:data:`KEYED_READS`).  A chain based at ``t == 0`` rather than at
    ``t_entry()``, or a rate evaluated before the month is asked whether it is in cover,
    still gives the right numbers.  This is the only test that sees the first, and the guard
    test sees the second too.  The row is then recorded for the rules test and released
    (:func:`_settle`).
    """
    s, sec = spliced[refs]
    key = _row_key(sec, "future", s_point, -k)
    s_proj, sec_proj = _point(s, s_point), projection(sec, key)
    try:
        df, pols = sec_proj.result_cf(), sec_proj.result_pols()
        assert _compare(s_proj, sec_proj, -k, FUTURE_EXEMPT) == []
        for report, frame in (("result_cf", df), ("result_pols", pols)):
            assert list(frame.index[:k]) == list(range(k)), report
            assert (frame.loc[:k - 1] == 0.0).all().all(), report
        assert sec_proj.pols_new_biz(k) == sec_proj.policy_count() == 1.0
        assert [t for t in range(sec_proj.proj_len())
                if sec_proj.premium_pp(t) > sec_proj.premium_regular_pp() / 12.0] == (
            [k] if sec_proj.premium_single_pp() > 0.0 else [])
        early = {name: sorted(args[0] for args in _cached_args(sec_proj.cells[name])
                              if args[0] < k)
                 for name in KEYED_READS}
        assert not any(early.values()), f"read before issue: {early}"
    finally:
        _settle(splice_records, ("future", s_point, -k, refs), sec, key)


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
    and points issued later, on both sets, and on each the reports, the checks and the full
    sweep are run first (:func:`_rule_breaches`):

    * R1: no cell holds a negative argument.  modelx evaluates one without complaint, and
      a compiled cache raises ``IndexError`` below 0 (USLIB-SEC-PLAN.md F4).  A policy
      month turned into ``t`` by subtracting ``duration_mth_init()`` (R1a) goes negative
      on a point in force past it.
    * R1's look-back stops at ``t_entry()``: no cell evaluated at a month from
      ``t_entry()`` on read a month before it.  On a point issued later a chain based at
      ``t == 0`` reads the pre-issue zeros, so no number shows it and no argument goes
      negative.
    * R2's look-ahead: no cell evaluated at month ``t`` read a cell keyed by a month beyond
      ``t + 1``, as modelx's dependency graph records each cached call's precedents, but the
      bonus rate's read of its year's declaration (:data:`LOOK_AHEAD`), which reads no
      month past the frame from a month inside it.
    * And no call of the full sweep raised.

    Each row was scanned by the T2 or T3 case that compared it (:func:`_settle`), and a row
    no case has scanned is scanned here.  The core case covers the core's rows, the full
    case every other row of the full grid, with ``UKLIB_SEC_FULL=1``.  The closed-form
    clock and the recursion depth are asserted on the committed model, in the tests after
    this one, and the exhaustion search's reads by a test of its own.
    """
    cases = [case for case in GRID if (case in CORE_GRID) == (grid == "core")]
    negative, early, ahead, outside, raised, failed = [], [], [], [], [], []
    for case in cases:
        record, where = _record_of(spliced, splice_records, case), _case_id(*case)
        negative += [f"{where}: {call}" for call in record["negative"]]
        early += [f"{where}: {read}" for read in record["early"]]
        ahead += [f"{where}: {read}" for read in record["ahead"]]
        outside += [f"{where}: {read}" for read in record["outside"]]
        raised += [f"{where}: {call}" for call in record["raised"]]
        if record["failed"]:
            failed.append(f"{where}: {record['failed']}")
    assert cases, f"the {grid} grid has no rows"
    assert not failed, f"rows that raised: {failed[:10]}"
    assert not raised, f"calls the full sweep found raising: {raised[:10]}"
    assert not negative, f"called before the valuation date: {negative[:10]}"
    assert not early, f"read before issue from the books: {early[:10]}"
    assert not ahead, f"read beyond t + 1: {ahead[:10]}"
    assert not outside, f"the declaration's read past the frame: {outside[:10]}"


def test_the_exhaustion_search_reads_the_units_to_their_exhaustion_and_no_further(
        sec_model):
    """``fund_exhaust_mth()`` reads the units month by month, from ``t_entry()`` to the month
    they run out.

    The search is R2's far read, one loop in one cell, from the first month on the books,
    ascending.  On each committed bond whose units run out the cell reads ``units`` at every
    month from ``t_entry()`` to ``proj_len()``, the month the withdrawal takes the last of
    them, which is the first month the frame does not project, and at no month after it;
    on the bond issued 13 months on it reads none before its issue month, where a search
    from 0 would find a bond with no units and read it as exhausted.  It returns the policy
    month of that read, and the frame ends the month before.  On the bonds that take no
    withdrawal, and on the endowment, it reads no units at all, and returns a month past
    cover.  Its precedents are read off modelx's dependency graph.
    """
    table = sec_model.Data.model_point_table()
    exhausting = 0
    for key, label in zip(point_keys(sec_model), table.index):
        p = projection(sec_model, key)
        exhaust = p.fund_exhaust_mth()
        reads = sorted(node.args[0] for node in p.cells["fund_exhaust_mth"].preds()
                       if node.obj.name == "units")
        if not (p.is_unitised() and p.wd_rate() > 0.0):
            assert reads == [] and exhaust == p.cover_end_mth() + 1, label
            continue
        assert exhaust < p.cover_end_mth(), label
        assert reads == list(range(p.t_entry(), p.proj_len() + 1)), label
        assert exhaust == p.duration_mth(p.proj_len()), label
        assert p.units(p.proj_len()) <= 1e-9 < p.units(p.proj_len() - 1), label
        exhausting += 1
    assert exhausting >= 4


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
      stays shallow.  A backward recursion over the frame, through ``t + 1``, keeps every
      step within the look-ahead but opens a chain as long as the frame, which a compiled
      model would run on the C stack (F7), and fails here.
    """
    record = sec_read[1]
    assert record["duration_mth(500)"] == 560
    assert record["keys"] == [500]
    assert not record["deep"], f"under a recursion limit of {CALL_DEPTH}: {record['deep']}"


# How deep a cold call may run beyond its chain, one cell a month from its month back to
# t_entry() (D5): the cells above the chain and those below it, the first month's rates and
# Data's first reads of its tables.  WP runs its four chains, the count, the asset share,
# the payout and the endowment's guarantee, one cell a month, and the units, the price and
# the two cumulants, which were one already.  Measured at M13, at the contract's longest
# cover, 1,224 months from issue age 18, issued now and 120 months on alike, with the bonus
# rule and the estate distribution on: a cold net_cf in the last month runs 16 cells beyond
# its chain on the bond, 14 on the endowment and 9 on the withdrawing bond, whose
# exhaustion search has run its chains first; the count 12, 6 and 5; the asset share 6; the
# payout 7; the guarantee 11, 10 on the endowment; the units, the price and the guarantee
# charges 10, the declaration's read of the asset share opening beneath them under the
# rule; the smoothing account 12, 8 on the withdrawing bond; and the roll-forward's
# residual 7.  Term's 16 (USLIB-SEC-PLAN.md D5), met exactly by the bond's net_cf.  Any
# chain of two cells a month runs a frame's length beyond.
CHAIN_OVERHEAD = 16

# The bonus rule's own chain, the rate declared each year from the year before's, runs one
# cell a policy year, its declaration's read of the asset share and the payout opening
# beneath its first: measured at M13, 30 cells beyond one a year at the longest cover, on
# each shape.
RULE_OVERHEAD = 40

# The contract's longest cover (held by proj_len()): issued at issue_age_min, 18, to the
# limiting age, omega_age, 120, 1,224 months, on the bond; and an endowment maturing at it,
# 102 years.
YOUNGEST = 18
LONGEST = 12 * (120 - YOUNGEST)

# The chains of the model and the cells that head them, called cold in the last month of
# the frame, each on a read of its own: (cell, the timing it takes, or None).
CHAIN_HEADS = (("net_cf", None), ("pols_if_at", "BEF_NB"), ("asset_share", None),
               ("smoothed_payout", None), ("guar_benefit_pp", None), ("units", None),
               ("unit_price", None), ("guar_charge_cum_pp", None),
               ("smoothing_account", None), ("check_asset_share_roll_fwd_resid", None))

# The shapes the chains run at their longest cover on: the anchor bond issued at 18, the
# endowment issued at 18 for 102 years, and the bond with a 1% withdrawal at 7%, whose
# units never run out, so that the exhaustion search runs over the whole cover.  Each is a
# committed twin made new business at 18: (the twin's S point, the columns changed).
SHAPES = {
    "bond": (1, {}),
    "endowment": (5, {"policy_term": 102}),
    "withdrawing bond": (7, {"fund_return": 0.07, "wd_rate": 0.01}),
}


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


def _new_business(row):
    """``row``, a committed twin's, as new business: no opening state, the seed price."""
    return row.assign(duration_mth=0, units_init=0.0, unit_price_init=1.0,
                      attaching_bonus_init=0.0, asset_share_init=0.0,
                      smoothed_payout_init=0.0, guar_charge_cum_pp_init=0.0,
                      smoothing_account_init=0.0)


def _longest_cover(tmp_path, shape):
    """A copy whose table holds the shape at the longest cover, issued now and 120 months
    on, and each row's label, frame and ``t_entry()``."""
    committed = _committed()
    s_point, changes = SHAPES[shape]
    label = _label(committed, "twin", s_point, 0 if s_point in (5, 7) else 60)
    row = _new_business(committed.loc[[label]]).assign(age_at_entry=YOUNGEST, **changes)
    later = row.assign(duration_mth=-120)
    top = committed.index.max()
    rows = pd.concat([row, later]).set_axis([top + 1, top + 2]).rename_axis("point_id")
    return _sec_inputs(tmp_path, rows), [(top + 1, LONGEST, 0), (top + 2, LONGEST + 120, 120)]


# modelx warns as its stack trace starts and stops, which is all the test does with it.
@pytest.mark.filterwarnings("ignore:call stack trace:UserWarning")
@pytest.mark.parametrize("shape", [pytest.param(s, id=s.replace(" ", "_"),
                                                marks=() if s != "withdrawing bond"
                                                else FULL_ONLY)
                                   for s in SHAPES])
def test_every_chain_runs_one_cell_a_month_from_a_cold_start(tmp_path, shape):
    """Called cold, each chain runs one cell a month back to ``t_entry()``, no more.

    No number shows how deep a chain runs, and a compiled model runs it on the C stack, so
    a chain of several cells a month, which gives the same numbers, needs that many times
    the stack on every platform (F7).  ``WP_UK_S``'s asset share runs seven cells a month: a
    cold read of ``asset_share(779)`` on the worked example's bond runs 5,042 deep.  On a
    model just read, nothing is cached, so modelx's stack trace counts how deep a call
    runs, against one cell a month back to ``t_entry()`` and :data:`CHAIN_OVERHEAD` more:
    each head of :data:`CHAIN_HEADS` in the last month of the frame, each on a read of its
    own, with :data:`SWITCHED_ON` set, so that the bonus rule declares from the asset share
    and the estate distribution reads it.  On each shape at the contract's longest cover,
    1,224 months from issue age 18, issued now and, with the full grid, 120 months on
    (:func:`_longest_cover`), each row's frame asserted first.  The bonus rule's own chain,
    one cell a year, is held to a year a cell and :data:`RULE_OVERHEAD` more.  The bond and
    the endowment run by default, its guarantee's chain among them, and the withdrawing bond
    with the full grid.
    """
    folder, frames = _longest_cover(tmp_path, shape)
    frames = frames if SEC_FULL else frames[:1]
    found = []
    framed = mx.read_model(folder, name=_name("framed"))
    try:
        for ref, value in SWITCHED_ON.items():
            setattr(framed.Projection, ref, value)
        for label, months, entry in frames:
            p = _point(framed, label)
            assert p.proj_len() == months and p.t_entry() == entry, label
    finally:
        framed.close()
    for label, months, entry in frames:
        for cell, timing in (*CHAIN_HEADS, ("bonus_rate", None)):
            fresh = mx.read_model(folder, name=_name("cold"))
            try:
                for ref, value in SWITCHED_ON.items():
                    setattr(fresh.Projection, ref, value)
                p = _point(fresh, label)
                last = months - 1
                args = (last,) if timing is None else (last, _code(p, timing))
                depth = _cold_depth(p, cell, args)
                if cell == "bonus_rate":
                    chain, allowed = (last - entry) // 12 + 1, RULE_OVERHEAD
                else:
                    chain, allowed = last - entry, CHAIN_OVERHEAD
                if not (cell == "units" and shape == "endowment") and not (
                        chain <= depth <= chain + allowed):
                    found.append(f"{shape} {label}: {cell}{args} cold runs {depth} cells "
                                 f"deep, where its chain back to t_entry() {entry} is "
                                 f"{chain} and {allowed} more are allowed")
            finally:
                fresh.close()
    assert not found, found


def test_each_chain_written_inline_is_its_steps_bit_for_bit(sec_model):
    """The chains written inline are the cells that expose their steps, to the last bit.

    ``asset_share(t)`` writes the month's premium and withdrawal, return, charges,
    shareholder transfer, mortality charge and estate distribution inline, for its chain;
    ``asset_share_at(t, "AFT_MC")`` builds the same balance a step at a time, as
    ``WP_UK_S``'s does, each step a cell.  ``smoothed_payout(t)`` writes the cap and the
    corridor inline; ``smoothed_payout_capped(t)`` is the cap as a cell.  And the endowment's
    ``guar_benefit_pp(t)`` writes the declaration on the guarantee the month before, which
    ``guar_benefit_open(t)`` reads.  On every committed point and month the inline cell is
    the step-by-step one, floored or clamped as it floors or clamps, compared with ``==``,
    so a step reordered, a float rounded otherwise or a floor dropped fails.
    """
    for key, label in zip(point_keys(sec_model), sec_model.Data.model_point_table().index):
        p = projection(sec_model, key)
        for t in range(p.t_entry(), p.proj_len()):
            assert p.asset_share(t) == max(0.0, p.asset_share_at(t, "AFT_MC")), (label, t)
            capped, as_t = p.smoothed_payout_capped(t), p.asset_share(t)
            assert p.smoothed_payout(t) == max(p.corridor_lo * as_t,
                                               min(p.corridor_hi * as_t, capped)), (label, t)
            if not p.is_unitised():
                g = p.guar_benefit_open(t)
                want = g * (1.0 + p.bonus_rate(t)) if p.is_declaration_month(t) else g
                assert p.guar_benefit_pp(t) == want, (label, t)
            if t > p.t_entry():
                assert p.asset_share_at(t, "BEF_PREM") == p.asset_share(t - 1)
                assert p.smoothed_payout_open(t) == p.smoothed_payout(t - 1)


# ---------------------------------------------------------------------------
# T4 -- the count algebra
#
# BEF_DECR == BEF_NB + pols_new_biz, at every t of every point, is a convention
# (test_new_business_joins_the_count_before_decrements), and is not repeated here.


def test_the_count_rolls_forward_and_result_pols_holds_it(sec_model, s_model):
    """The count leaves month t by its decrements, and ``result_pols`` sets it out (D5).

    On every committed point and at every ``t`` of its frame, to 1e-12: the count weighting
    month ``t``, ``pols_if_at(t, BEF_DECR)``, less the count it carries into ``t + 1``,
    ``pols_if_at(t + 1, BEF_NB)``, is its deaths, its surrenders and, in the frame's last
    month, the survivors paid or truncated there, ``pols_maturity``; the count before
    surrenders is the count less its deaths; and the notes' end-of-month count,
    ``pols_if_at(t, AFT_DECR)``, is exactly the count carried into the next month, 0 from
    the last.  The new business is ``policy_count()`` in the issue month alone.

    ``result_pols()`` sets the same movement out row by row, in :data:`RESULT_POLS`'s
    columns, indexed by ``t`` over the frame: ``pols_if`` at ``t + 1`` is ``pols_if`` less
    its decrements at ``t``, plus the new business of ``t + 1``, row 0 opening from
    ``pols_if_init()``.  ``WP_UK_S`` has no ``result_pols``, so on each twin the report is
    compared with S's own counts (:func:`_s_result_pols`), to 1e-9, frames ending together:
    the counts carry no inflation, so the shipped assumptions serve.
    """
    table = sec_model.Data.model_point_table()
    for key, point_id in zip(point_keys(sec_model), table.index):
        p = projection(sec_model, key)
        bef_nb, bef_decr, bef_surr, aft = (_code(p, c) for c in TIMINGS)
        last, issue = p.proj_len() - 1, -p.duration_mth_init()
        for t in range(p.proj_len()):
            carried = p.pols_if_at(t + 1, bef_nb)
            assert p.pols_if_at(t, aft) == carried, (point_id, t)
            out = p.pols_death(t) + p.pols_surr(t) + p.pols_maturity(t)
            assert p.pols_if_at(t, bef_decr) - carried == pytest.approx(out, abs=1e-12), (
                point_id, t)
            assert p.pols_if_at(t, bef_surr) == pytest.approx(
                p.pols_if(t) - p.pols_death(t), abs=1e-12), (point_id, t)
            assert p.pols_new_biz(t) == (p.policy_count() if t == issue else 0.0)
            assert (p.pols_maturity(t) == 0.0) == (t != last) or p.pols_if(t) == 0.0
        assert p.pols_if_at(last + 1, bef_nb) == 0.0, point_id
        pols = p.result_pols()
        assert list(pols.columns) == RESULT_POLS, point_id
        assert pols.index.name == "t" and list(pols.index) == list(range(p.proj_len()))
        moved = (pols["pols_if"] - pols[["pols_death", "pols_surr", "pols_maturity"]]
                 .sum(axis=1)).shift(1)
        expected = moved.fillna(p.pols_if_init()) + pols["pols_new_biz"]
        assert ((pols["pols_if"] - expected).abs() <= 1e-12).all(), point_id
        if table.at[point_id, "row_kind"] == "twin":
            s = _point(s_model, point_id)
            assert frame_mismatches(_s_result_pols(s), pols,
                                    t_offset=int(table.at[point_id, "source_mth"])) == []


# What T4 multiplies the counts by: not a whole number, because a count of policies need
# not be one, so that a flow which read the count as whole policies would not follow it.
COUNT_FACTOR = 2.5

# The per-policy columns of each report, which the count must not move: the rest are
# counts or flows, which it scales.
PER_POLICY = {"result_cf": ("asset_share",), "result_pols": (),
              "result_payout": tuple(c for c in (
                  "asset_share", "guar_benefit_pp", "smoothed_payout", "final_bonus_pp",
                  "mvr_pp", "mvr_applied_pp", "claim_death", "claim_surrender",
                  "claim_guarantee", "bonus_rate", "cost_of_bonus_pp",
                  "shareholder_transfer_pp", "mort_charge_pp"))}

# The counted cells no sweep evaluates: a refusal's cell, called on the error path alone.
NEVER_SWEPT = frozenset({"smoothing_account_refusal"})


@pytest.mark.parametrize("grid", GRIDS)
def test_scaling_the_counts_scales_every_flow_and_no_per_policy_value(tmp_path, grid):
    """The count is the weight: 2.5 times it, 2.5 times every flow, the same per policy.

    The committed table, and a copy with every ``policy_count`` multiplied by
    :data:`COUNT_FACTOR`, are each read with :data:`SWITCHED_ON` set before either computes
    anything: every switch that ships off, on, so that every flow is nonzero on some point,
    the bonus rule declares from the asset share and the estate distribution reads it.  On
    every point each report's counts and flows are 2.5 times the committed table's, element
    by element, to 1e-12 relative: a scaled count is a computed float, which may come back
    from the CSV within two ulps (``uk_sec_support``'s module docstring); and its per-policy
    columns (:data:`PER_POLICY`) are the committed table's exactly.  So is every other cell
    of :data:`COUNTED`, at every argument the sweep of the committed table's point cached:
    the counts at each timing and the claims of each kind, which no report shows, among
    them, and the roll-forward's residual, a rounding about 0, to its floor of 1e-9.  And
    every cell outside :data:`COUNTED` (the asset share, the units, the price, the
    guarantee, the payout, the rates, both clocks, the flags) agrees bit for bit at every
    argument that sweep cached.  So a flow that dropped the count, or read it as whole
    policies, which a table of counts of 1 hides from every comparison with S, fails
    (USLIB-SEC-PLAN.md §5.2, T4, precised at M11).  The smoothing account opens from its
    per-policy column times the count, and scales with it.  Each counted cell is nonzero on
    some point but the residual and :data:`NEVER_SWEPT`.

    The default run takes :data:`CORE_POINTS`, among which every counted cell is nonzero,
    and the full grid the other committed points.
    """
    table = _committed()
    base = mx.read_model(_sec_inputs(tmp_path / "base", table), name=_name("counted"))
    scaled = mx.read_model(_sec_inputs(tmp_path / "scaled", table.assign(
        policy_count=COUNT_FACTOR * table["policy_count"])), name=_name("scaled"))
    counted = sorted(COUNTED - set(PER_POLICY))
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
            for report, fixed in PER_POLICY.items():
                b, d = one.cells[report](), many.cells[report]()
                assert d.index.equals(b.index) and list(d.columns) == list(b.columns)
                flows = [c for c in b.columns if c not in fixed]
                want = COUNT_FACTOR * b[flows]
                bad = ((d[flows] - want).abs() > 1e-12 * want.abs()).any()
                assert not bad.any(), (label, report, list(bad[bad].index))
                assert d[list(fixed)].equals(b[list(fixed)]), (label, report)
            for name in counted:
                floor = FLOOR if name in RESIDUALS else 0.0
                for args in _cached_args(one.cells[name]):
                    want = COUNT_FACTOR * one.cells[name](*args)
                    got = many.cells[name](*args)
                    assert abs(got - want) <= floor + 1e-12 * abs(want), (
                        label, name, args, got, want)
                    if want != 0.0 and name not in RESIDUALS:
                        nonzero.add(name)
            assert twin_mismatches(one, many, exempt=TWIN_EXEMPT_DEFAULT | COUNTED
                                   | set(PER_POLICY), rtol=0.0, atol=0.0) == [], label
            _release(base, key)
            _release(scaled, scaled_key)
    finally:
        scaled.close()
        base.close()
    if grid == "core":
        want = set(counted) - RESIDUALS - NEVER_SWEPT
        assert want <= nonzero, f"0 on every core point: {sorted(want - nonzero)}"


def _month_on(p):
    """The columns that restate ``p``, a point in force, a month on: what this model
    carries into its month 1, at month 1's ``BEF_NB`` instant (D6)."""
    count = p.pols_if_at(1, _code(p, "BEF_NB"))
    return dict(
        duration_mth=p.duration_mth(1), policy_count=count,
        asset_share_init=p.asset_share(0), units_init=p.units(0),
        unit_price_init=p.unit_price(0),
        attaching_bonus_init=(0.0 if p.is_unitised()
                              else p.guar_benefit_pp(0) - p.sum_assured()),
        smoothed_payout_init=p.smoothed_payout(0),
        bonus_rate_init=p.bonus_rate(0) if p.is_declaration_month(0) else p.bonus_rate_init(),
        guar_charge_cum_pp_init=p.guar_charge_cum_pp(0),
        smoothing_account_init=p.smoothing_account(0) / count)


@pytest.mark.parametrize("grid", GRIDS)
def test_a_point_restated_a_month_on_continues_its_own_flows(tmp_path, grid):
    """The state a point carries into a month is the state its month opens with (T4, D6).

    Each point in force on the committed table, its frame longer than a month, is restated
    a month on, opened with what this model carries into its month 1 (:func:`_month_on`):
    its count, ``pols_if_at(1, "BEF_NB")``; its asset share, units, unit price, guarantee
    less the sum assured on the endowment, smoothed payout and two cumulants at the close
    of month 0, the smoothing account per policy in force at month 1; and the rate declared
    at the last declaration before month 1, month 0's own where month 0 declares, and the
    point's opening rate otherwise (D6).  The restatement must continue the point's own
    frames, its row ``t`` the point's row ``t + 1``, in ``result_cf``, ``result_payout``
    and ``result_pols``, every flow among them, to 1e-9 relative, floored at 1e-9 for what a
    state read back from the CSV an ulp off moves about 0.  Scaling every count alike
    cannot see a flow weighted by the count a point opened with rather than the one in force
    in its month, and the splice sees only S's states: this sees both, on this model's own.
    It runs with the bonus rule on, so that the rate of the year under way is a state, and
    the estate distribution on, so that every month reads the opening asset share, at an
    inflation rate of 0, set on each model as it is read (K7): the restatement moves the
    valuation date a month on, and expense inflation, on the valuation clock, would step a
    month apart by design (D7).  The rows of a declaration in month 0, at 71 and 11, carry
    the declaration in their state.

    The default run restates the points in force among :data:`CORE_POINTS` and the twins
    in force at 60, and the full grid the others.
    """
    table = _committed()
    refs = {**SWITCHED_ON, "inflation_rate": 0.0}
    model = mx.read_model(_sec_inputs(tmp_path / "base", table), name=_name("month_on"))
    rows, pairs, frames = [], [], {}
    try:
        for ref, value in refs.items():
            setattr(model.Projection, ref, value)
        top = table.index.max()
        for label in table.index[table["duration_mth"] > 0]:
            core = label in CORE_POINTS or table.at[label, "duration_mth"] == 60
            if core != (grid == "core"):
                continue
            p = _point(model, label)
            if p.proj_len() < 2:
                continue
            top += 1
            row = table.loc[[label]].assign(**_month_on(p))
            row.index = pd.Index([top], name="point_id")
            rows.append(row)
            pairs.append((label, top))
            frames[label] = {report: p.cells[report]() for report in REPORTS}
            _release(model, _key(model, label))
    finally:
        model.close()
    if grid == "core":
        assert {table.at[label, "duration_mth"] % 12 for label, _ in pairs} >= {0, 11}
    restated = mx.read_model(_sec_inputs(tmp_path / "on", pd.concat([table, *rows])),
                             name=_name("month_on"))
    found = []
    try:
        for ref, value in refs.items():
            setattr(restated.Projection, ref, value)
        for label, moved in pairs:
            p = _point(restated, moved)
            for report, frame in frames[label].items():
                found += [f"point {label} restated as {moved}, {report}: {line}"
                          for line in frame_mismatches(frame, p.cells[report](),
                                                       t_offset=1)]
            _release(restated, _key(restated, moved))
    finally:
        restated.close()
    assert not found, found[:20]


@pytest.mark.parametrize("grid", GRIDS)
def test_the_roll_forward_closes_on_ten_million_policies(tmp_path, grid):
    """``check_pols_roll_fwd`` scales its tolerance with the policies, and closes at 1e7.

    A residual is rounding on that many policies, so the check holds it to 1e-10 times
    ``max(policy_count(), 1)``, where ``WP_UK_S``'s holds it to 1e-10 unscaled: at the
    counts the other tests use, one policy or less, the two are one.  ``WP_UK_S`` cannot
    scale by ``pols_if_init()``, which here is 0 on a point issued at or after the valuation
    date, its count entering as new business.  So every committed point is projected from a
    copy where each counts ten million policies: the check closes on each, and the largest
    residual over the points exceeds the unscaled 1e-10, so the scaling is what closes it
    (USLIB-SEC-PLAN.md §5.2, T4, precised at M10).

    The default run takes :data:`CORE_POINTS`, and the full grid the other points.
    """
    table = _committed()
    model = mx.read_model(_sec_inputs(tmp_path, table.assign(policy_count=1e7)),
                          name=_name("ten_million"))
    largest = 0.0
    try:
        for key, point_id in zip(point_keys(model), table.index):
            if not _on_grid(grid, point_id):
                continue
            p = projection(model, key)
            assert p.check_pols_roll_fwd() is True, point_id
            resid = max(abs(p.check_pols_roll_fwd_resid(t)) for t in range(p.proj_len()))
            assert resid <= 1e-10 * 1e7, point_id
            largest = max(largest, resid)
            _release(model, key)
    finally:
        model.close()
    assert largest > 1e-10, largest


# ---------------------------------------------------------------------------
# T5 -- validation
#
# Each malformed table is the committed one with one fault.  The checks run over the whole
# table as it is read, in Data, and the message names the file it read and the column or
# every point at fault.  A blank cell reads as NaN, and so does a text cell once the checks
# coerce the column to numbers, so each is refused as a count, a duration or a state that
# is not a number.  The repeated point_id holds another policy under the same label, as a
# bad extract would, so that the check must look at the labels and not at whole rows.  The
# point_ids are the committed table's: 1 to 7 the twins of S's points, 1 to 4 bonds in
# force at 60, 5 the endowment issued at the valuation date, 6 the endowment in force at
# 240 and 7 the bond variant issued at it; then S point 1 at 71 (8), point 2 at 68, 92, 119
# and 242 (9 to 12), point 3 at 487 (13), point 4 at 402 (14), the endowment at 11 and 299
# (15, 16), point 1 at 779 (17), the bond variant at 100 (18), its future row 13 months on
# (19), and the rows under References of their own, the bond variant at 60 (20), point 3
# at 300 (21), point 1 at 150 (22), the endowment at 150 (23) and point 1 at 156 (24).  A
# {file} in a message is the table's filename: every case is read by one model, from a
# file of its own (the malformed fixture).


def _drop(column):
    return lambda table: table.drop(columns=column)


_COUNT = "{file}: policy_count must be a number, zero or more; it is not at point_id "
_WHOLE_MONTHS = "{file}: duration_mth must be a whole number of months; it is not at point_id "
_BELOW_2_53 = "{file}: duration_mth must be below 2**53 months; it is not at point_id "
_WHOLE = "must be a whole number, 0 or more, below 2**53; it is not at point_id "
_AMOUNT = "must be a number, zero or more; it is not at point_id "
_DATES = ("{file}: guarantee_dates must be blank or policy anniversaries separated by ';', "
          "each a whole number of years, 1 or more, below 2**53; they are not at point_id ")
_NOT_YET = "must be 0 on a policy not yet in force, duration_mth 0 or less; it is not at point_id "
_PRICE = "{file}: unit_price_init must be a finite number above 0, a price; it is not at point_id "
_RATE = ("{file}: bonus_rate_init must be a finite number, zero or more, a declared bonus being "
         "floored at 0; it is not at point_id ")
_ACCOUNT = "{file}: smoothing_account_init must be a finite number; it is not at point_id "

MALFORMED = [
    ("a negative count", _set("policy_count", [8], -0.1), _COUNT + "[8]"),
    ("a blank count", _set("policy_count", [9], float("nan")), _COUNT + "[9]"),
    ("two bad counts", _set("policy_count", [8, 10], -1.0), _COUNT + "[8, 10]"),
    ("a text count", _set("policy_count", [11], "abc"), _COUNT + "[11]"),
    ("an infinite count", _set("policy_count", [11], float("inf")), _COUNT + "[11]"),
    ("a fractional duration", _set("duration_mth", [9], 68.5), _WHOLE_MONTHS + "[9]"),
    ("a blank duration", _set("duration_mth", [19], float("nan")), _WHOLE_MONTHS + "[19]"),
    ("a text duration", _set("duration_mth", [11], "x4"), _WHOLE_MONTHS + "[11]"),
    # numpy casts a float past int64 to the least int64, a policy issued 2**63 months on,
    # without a word: the table refuses it first.
    ("a duration past int64", _set("duration_mth", [8], 1e19), _BELOW_2_53 + "[8]"),
    ("durations of 2**53 months at two points", _set("duration_mth", [8, 10], 2.0 ** 53),
     _BELOW_2_53 + "[8, 10]"),
    ("issued beyond the horizon", _set("duration_mth", [19], -121),
     "{file}: duration_mth must be -120 or more, a policy issued at most 120 months after "
     "the valuation date; it is not at point_id [19]"),
    *[(f"no {column} column", _drop(column), f"{{file}} has no {column} column")
      for column in ("policy_count", "duration_mth", *STATE)],
    ("a point_id twice", lambda table: table.rename(index={9: 8}),
     "{file}: point_id [8] appears more than once"),
    ("an unknown chassis", _set("chassis", [8], "UWP_fund"),
     "{file}: chassis must be UWP_bond or CWP_endowment; it is not at point_id [8]"),
    ("an unknown sex", _set("sex", [9], "X"),
     "{file}: sex must be M or F; it is not at point_id [9]"),
    ("an unknown tax basis", _set("tax_basis", [10], "pension_net"),
     "{file}: tax_basis must be life_net or pension_gross; it is not at point_id [10]"),
    ("a fractional issue age", _set("age_at_entry", [8], 55.5),
     "{file}: age_at_entry " + _WHOLE + "[8]"),
    ("a negative issue age", _set("age_at_entry", [9], -1),
     "{file}: age_at_entry " + _WHOLE + "[9]"),
    ("an issue age of 2**53", _set("age_at_entry", [9], 2.0 ** 53),
     "{file}: age_at_entry " + _WHOLE + "[9]"),
    ("a fractional term", _set("policy_term", [6], 25.5),
     "{file}: policy_term " + _WHOLE + "[6]"),
    ("a negative single premium", _set("premium_single", [1], -1.0),
     "{file}: premium_single " + _AMOUNT + "[1]"),
    ("a blank regular premium", _set("premium_regular", [6], float("nan")),
     "{file}: premium_regular " + _AMOUNT + "[6]"),
    ("an infinite sum assured", _set("sum_assured", [6], float("inf")),
     "{file}: sum_assured " + _AMOUNT + "[6]"),
    ("a withdrawal past 1", _set("wd_rate", [4], ABOVE_1),
     "{file}: wd_rate must be a number from 0 to 1; it is not at point_id [4]"),
    ("a negative withdrawal", _set("wd_rate", [14], -0.01),
     "{file}: wd_rate must be a number from 0 to 1; it is not at point_id [14]"),
    ("a return of -1", _set("fund_return", [2], -1.0),
     "{file}: fund_return must be a finite number above -1; it is not at point_id [2]"),
    ("an infinite return", _set("fund_return", [3], float("inf")),
     "{file}: fund_return must be a finite number above -1; it is not at point_id [3]"),
    ("a guarantee date of 0", _set("guarantee_dates", [1], "0"), _DATES + "[1]"),
    ("a guarantee date not whole", _set("guarantee_dates", [2], "10;12.5"), _DATES + "[2]"),
    ("a guarantee date in text", _set("guarantee_dates", [3], "10;x"), _DATES + "[3]"),
    ("guarantee dates on an endowment", _set("guarantee_dates", [6], "10"),
     "{file}: guarantee_dates must be blank on a conventional endowment, which has no "
     "guarantee dates; it is not at point_id [6]"),
    ("an endowment with no term", _set("policy_term", [6], 0),
     "{file}: policy_term must be 1 or more on a conventional endowment, the years to its "
     "maturity; it is not at point_id [6]"),
    ("a bond with a term", _set("policy_term", [8], 10),
     "{file}: policy_term must be 0 on a bond, which is whole of life and has no term; it "
     "is not at point_id [8]"),
    ("a negative asset share", _set("asset_share_init", [8], -0.01),
     "{file}: asset_share_init " + _AMOUNT + "[8]"),
    ("blank units", _set("units_init", [9], float("nan")),
     "{file}: units_init " + _AMOUNT + "[9]"),
    ("a negative attaching bonus", _set("attaching_bonus_init", [16], -1.0),
     "{file}: attaching_bonus_init " + _AMOUNT + "[16]"),
    ("an infinite payout", _set("smoothed_payout_init", [10], float("inf")),
     "{file}: smoothed_payout_init " + _AMOUNT + "[10]"),
    ("negative charges taken", _set("guar_charge_cum_pp_init", [11], -0.01),
     "{file}: guar_charge_cum_pp_init " + _AMOUNT + "[11]"),
    ("a unit price of 0", _set("unit_price_init", [12], 0.0), _PRICE + "[12]"),
    ("an infinite unit price", _set("unit_price_init", [13], float("inf")), _PRICE + "[13]"),
    ("a text unit price", _set("unit_price_init", [7], "par"), _PRICE + "[7]"),
    ("a negative bonus rate", _set("bonus_rate_init", [14], -0.01), _RATE + "[14]"),
    ("a blank bonus rate", _set("bonus_rate_init", [19], float("nan")), _RATE + "[19]"),
    ("an infinite smoothing account", _set("smoothing_account_init", [17], float("inf")),
     _ACCOUNT + "[17]"),
    ("a smoothing account of -inf", _set("smoothing_account_init", [24], -math.inf),
     _ACCOUNT + "[24]"),
    ("a text smoothing account", _set("smoothing_account_init", [18], "x"),
     _ACCOUNT + "[18]"),
    ("units on an endowment", _set("units_init", [16], 1.0),
     "{file}: units_init must be 0 on a conventional endowment, which holds no units; it is "
     "not at point_id [16]"),
    ("an attaching bonus on a bond", _set("attaching_bonus_init", [8], 1.0),
     "{file}: attaching_bonus_init must be 0 on a bond, whose bonus is in its unit price; it "
     "is not at point_id [8]"),
    ("an asset share before issue", _set("asset_share_init", [19], 1.0),
     "{file}: asset_share_init " + _NOT_YET + "[19]"),
    ("units before issue", _set("units_init", [19], 1.0),
     "{file}: units_init " + _NOT_YET + "[19]"),
    ("an attaching bonus at issue", _set("attaching_bonus_init", [5], 1.0),
     "{file}: attaching_bonus_init " + _NOT_YET + "[5]"),
    ("a payout at issue", _set("smoothed_payout_init", [7], 1.0),
     "{file}: smoothed_payout_init " + _NOT_YET + "[7]"),
    ("charges taken before issue", _set("guar_charge_cum_pp_init", [19], 1.0),
     "{file}: guar_charge_cum_pp_init " + _NOT_YET + "[19]"),
    ("a smoothing account at issue", _set("smoothing_account_init", [5], -1.0),
     "{file}: smoothing_account_init " + _NOT_YET + "[5]"),
    ("a payout of 0 beside an asset share", _set("smoothed_payout_init", [8], 0.0),
     "{file}: smoothed_payout_init must be above 0 on a policy in force with an asset share, "
     "which holds the payout above 0; it is not at point_id [8]"),
    ("a bond in force without units", _set("units_init", [14], 0.0),
     "{file}: units_init must be above 0 on a bond in force, whose units are spent only "
     "when it is encashed; it is not at point_id [14]"),
    # Rule 14 holds the endowment's attaching bonus to 0, to the cent, before its first
    # declaration: a cent past 0 is refused, and half a cent read (the edges test).
    ("an attaching bonus a cent past 0 at 11", _set("attaching_bonus_init", [15], 0.01),
     "{file}: attaching_bonus_init must be 0, to the cent, on a conventional endowment in "
     "force 11 months or fewer, before its first declaration at the end of policy month "
     "11; it is not at point_id [15]"),
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


# An extract's labels: none is its position plus one, as every committed label is.
EXTRACT_LABELS = tuple(range(100 + len(_committed()), 100, -1))


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

    The committed table's one future point is the bond variant issued 13 months on.  It
    reads at the shipped 120 months and at 13, the shortest horizon that admits it, and is
    refused at 12, by name.  At 0 the model takes no future new business, D4's fallback for
    a product that cannot support it, and the message says so.  A horizon that is not a
    whole number of months, 0 or more, below ``2**53``, is itself refused, a NaN and an
    infinity among them: either would admit every policy.  A whole number written as a
    float, ``13.0``, reads as 13 does, and ``2**53 - 1``, the largest whole number the
    compiled model holds exactly, reads; ``2**53`` does not.  Setting the Reference clears
    the table, so each value is read afresh.
    """
    future = _label(_committed(), "future", 7, -13)
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
                          timeout=600)
    if not check:
        return done
    assert done.returncode == 0, done.stderr.decode(errors="replace")
    assert done.stdout.isascii(), "run_sec.py printed a non-ASCII character"
    # Windows ends each printed line with "\r\n"; read them as "\n", as a frame's
    # to_string() writes them.
    return done.stdout.decode("ascii").replace("\r\n", "\n")


# A point at the end of its cover, as (case, the S point and month of the committed row,
# the policy month it is moved to, the end of cover): the worked example's bond at the
# limiting age, 780 months from issue at 55, and the endowment at its maturity, 300 months.
PAST_COVER = [("the bond at the limiting age", (1, 779), 780),
              ("the endowment at maturity", (5, 299), 300)]


@pytest.mark.parametrize("case, row, end", PAST_COVER, ids=[c[0] for c in PAST_COVER])
def test_a_point_past_its_cover_is_refused_by_proj_len(tmp_path, case, row, end):
    """A point at or past the end of its cover has no frame, and ``proj_len()`` refuses it.

    The committed row in the last month of its cover is moved on a month, to the policy
    month cover ends, the bond's limiting age, ``omega_age``, 120, from issue at 55, or the
    endowment's maturity, on the policy clock.  That is a rule of the product, not of the
    table: it needs the limiting age, a Reference, or the term, and the entry age the
    point's own columns give, read where the frame is defined, so the table reads, and the
    point is refused on its first projection, rather than projecting nothing.  A loop over
    the block would meet the point only when it reached it, after projecting the points
    before it, so ``run_sec.py --block``, run beside the table, asks every point for its
    frame first: it fails naming the point, and prints nothing before.  The month before,
    the committed row, projects one month.
    """
    moved = _label(_committed(), "derived", *row)
    model = _read_edited(tmp_path, _set("duration_mth", [moved], end))
    message = (f"point_id {moved}: duration_mth {end} is at or past the end of cover, policy "
               f"month {end}")
    try:
        assert len(model.Data.model_point_table()) == len(_committed())
        _refused(_point(model, moved).result_cf, message)
    finally:
        model.close()
    shipped = mx.read_model(model_path(SEC), name=_name("last"))
    try:
        assert len(_point(shipped, moved).result_cf()) == 1
    finally:
        shipped.close()
    runner = tmp_path / "run_sec.py"
    shutil.copy(model_path(SEC).parent / "run_sec.py", runner)
    done = _run_sec(runner, "--block", check=False)
    assert done.returncode != 0 and done.stdout == b""
    assert message in done.stderr.decode(errors="replace")


# What the contract does not issue, refused by proj_len() as a point past cover is, as
# (case, the table's edit, the References set, the point, the message, and the frame the
# point projects at the shipped References, or None).  Data reads an issue age as WP_UK_S
# does, so each reads.  The product issues from 18, the mortality table's first age, and
# cover runs to omega_age, 120, on the bond, and to an endowment's maturity at most then;
# the compiled caches will be sized from both.  Each bound is refused just inside it here,
# and accepted at it in the edges test.  And each bound, moved past a committed twin,
# refuses it, which at the shipped bound projects its frame: the Reference is what refuses
# it.  Point 1 is the worked example's bond, issued at 55; point 5 the endowment, issued at
# 35 for 25 years.
NOT_ISSUED = [
    ("an issue age of 17", _set("age_at_entry", [5], 17), {}, 5,
     "point_id 5: the issue age, 17, is below issue_age_min, 18", None),
    ("an issue age below a bound raised to 36", None, {"issue_age_min": 36}, 5,
     "point_id 5: the issue age, 35, is below issue_age_min, 36", 300),
    ("a bond issued at 120", _set("age_at_entry", [7], 120), {}, 7,
     "point_id 7: the issue age, 120, is at or past omega_age, 120: the bond has no cover",
     None),
    ("a bond issued at a limiting age lowered to 55", None, {"omega_age": 55}, 7,
     "point_id 7: the issue age, 55, is at or past omega_age, 55: the bond has no cover",
     267),
    ("an endowment maturing at 121", _set("age_at_entry", [5], 96), {}, 5,
     "point_id 5: the endowment matures at age 121, past omega_age, 120, whose attained "
     "ages mort_table.csv may not rate", None),
    ("an endowment maturing past a limiting age lowered to 59", None, {"omega_age": 59}, 5,
     "point_id 5: the endowment matures at age 60, past omega_age, 59, whose attained ages "
     "mort_table.csv may not rate", 300),
]


@pytest.mark.parametrize("case, edit, refs, point, message, frame", NOT_ISSUED,
                         ids=[c[0] for c in NOT_ISSUED])
def test_a_point_the_contract_does_not_issue_is_refused_by_proj_len(tmp_path, case, edit,
                                                                    refs, point, message,
                                                                    frame):
    """``proj_len()`` refuses a point outside the contract's bounds, naming it (§6.5).

    ``WP_UK_S`` projects any issue age its tables reach, and an endowment maturing past the
    limiting age at the limiting age's rate, and so would modelx here, but the contract
    does not write either, and the compiled model's caches will be sized from the contract:
    a frame of at most 102 years and the horizon, attained ages from 18 to 119.  So the frame
    refuses such a point, naming it, as it refuses a point past its cover, and every report
    with it (:data:`NOT_ISSUED`): each bound just inside it, and each bound moved past a
    committed twin, which projects at the shipped bound, on a model read afresh.  A bound
    off by one, or a refusal lost, lets a point through.  The table reads either way.  Every
    Reference is set on a model just read, before its projection computes anything (K7).
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


# A bond whose units run out in its first month on the books, as (case, the table's edit,
# the point, the policy month): the withdrawing bond in its last month, 402, opened with a
# unit, which month 0's withdrawal, capped at the unit fund, takes; and the bond variant
# issued 13 months on and the one issued at the valuation date, each with no premium, so
# that its withdrawal election finds no units in its issue month.  WP_UK_S's search returns
# 0 there, its "never", and projects the bond to the limiting age.
SPENT = [
    ("a bond in force spent in month 0", _set("units_init", [14], 1.0), 14, 402),
    ("a bond issued later with no premium", _set("premium_single", [19], 0.0), 19, 0),
    ("a bond issued now with no premium", _set("premium_single", [7], 0.0), 7, 0),
]


@pytest.mark.parametrize("case, edit, point, month", SPENT, ids=[c[0] for c in SPENT])
def test_a_bond_spent_in_its_first_month_is_refused_by_proj_len(tmp_path, case, edit, point,
                                                                month):
    """A bond whose units run out in its first month on the books has no frame (§6.5).

    The frame ends the month before the units run out, so a bond spent in its first month,
    month 0 in force or its issue month, would end before it began: ``proj_len()`` refuses
    it, naming the point and the policy month, and every report with it.  On new business
    the withdrawal is capped at the unit fund the month opens with, 0, so a bond with a
    premium is never spent in its issue month; with none it is, and ``WP_UK_S``'s search,
    whose "never" is that month, would project it to the limiting age.
    """
    model = _read_edited(tmp_path, edit)
    try:
        p = _point(model, point)
        assert p.fund_exhaust_mth() == month
        _refused(p.result_cf, f"point_id {point}: the bond's units run out in its first "
                              f"month on the books, policy month {month}, so its frame "
                              f"would end before it began")
    finally:
        model.close()


# Each Reference proj_len() holds to a domain, as (case, the References set, the S point
# whose twin is read, the message where refused, and where the frame accepts a value the
# reports refuse, the start of their message).  The point is the bond variant issued at the
# valuation date, whose 267 months read every bond Reference, its market value reduction and
# its guarantee date among them, or for the rule and the discount the endowment.  NaN and
# the infinities are outside every domain.  WP_UK_S reads mort_be_factor inside the cap's
# min, which reads an infinity as certain death; amc_rate, guar_charge_rate_base and
# smooth_cap through twelfth roots with no real value past 1, and the two charges together
# as one factor on the balance; corridor_lo and corridor_hi, the guarantee-imminent and
# MVR-deterrent factors and guarantee_exercise_rate through a max and a min, the surrender
# rate's bound first, which reads a NaN as certain surrender; the estate distribution and
# the death uplift before a floor, which reads a NaN as an exhausted share; bonus_change_cap
# through a clamp a NaN is lost through; and the limits in comparisons a NaN switches off,
# omega_age sizing every bond's frame.  Each is refused at the nearest value outside each
# edge of its domain, and accepted at the edge itself, whose reports then project, in finite
# floats over the whole frame (M11's template), or are refused where a value first leaves
# the floats, or where the contract refuses it, a bond that buys no units being spent in its
# issue month: the largest finite float an edge of each domain unbounded above.  The
# horizon's largest whole number grows the worked example's +7% past the floats, and decays
# the down scenario's below the smallest, each refused, the latter by the frame, whose
# exhaustion search declares on that withdrawing bond: a horizon of 4,500 underflows there,
# where 4,000 does not.  issue_age_min, omega_age and bonus_horizon are whole numbers below
# 2**53, which the compiled model holds as long long, printed through int() once whole: each
# is refused at a fraction and at exactly 2**53, and its largest whole number accepted, or
# refused by a later rule.  The rule's References are read with the rule on, on the
# endowment, point 5, where its every term is read.
RULE = {"bonus_rule_on": True}


def _domain(ref, rule, accepted, refused, printed=float, point=7, also=None):
    """The DOMAINS cases of ``ref``: each of ``accepted`` projects, or its reports refuse
    as ``accepted`` maps it; each of ``refused`` is refused by the domain's ``rule``, and NaN
    and the infinities by it too.  ``also`` are References set beside it."""
    also = also or {}
    message = f"point_id {point}: {ref} must be {rule}, not {{}}"
    if not isinstance(accepted, dict):
        accepted = dict.fromkeys(accepted)
    cases = [(f"{ref}={value!r}", {**also, ref: value}, point, None, report)
             for value, report in accepted.items()]
    cases += [(f"{ref}={value!r}", {**also, ref: value}, point,
               message.format(printed(value)), None) for value in refused]
    return cases + [(f"{ref}={value!r}", {**also, ref: value}, point,
                     message.format(float(value)), None)
                    for value in (math.nan, math.inf, -math.inf)]


def _whole_domain(ref, accepted, least=0, point=7, also=None):
    """The DOMAINS cases of an integer Reference: a whole number below 2**53, and
    ``least`` or more, printed through int() once whole."""
    also = also or {}
    whole = f"point_id {point}: {ref} must be a whole number below 2**53, not {{}}"
    cases = [(f"{ref}={value!r}", {**also, ref: value}, point, None, None)
             for value in accepted]
    if least is not None:
        cases.append((f"{ref}={least - 1}", {**also, ref: least - 1}, point,
                      f"point_id {point}: {ref} must be {least} or more, not {least - 1}", None))
    return cases + [(f"{ref}={value!r}", {**also, ref: value}, point,
                     whole.format(float(value)), None)
                    for value in (0.5, 120.5, WHOLE, 1e300, math.nan, math.inf, -math.inf)]


_FINITE_0 = ("a finite number, 0 or more", (0.0, BIG), (BELOW_0,))
_SHARE = ("a number from 0 to 1", (0.0, 1.0), (BELOW_0, ABOVE_1))
_ASSET_SHARE = "point_id {}: the asset share of month {} before its floor"
OMEGA = ("point_id 7: omega_age must be above issue_age_min, 18, and at most 121, a year "
         "past mort_table.csv's last age, not {}")
CHARGED = ("point_id 7: amc_rate and guar_charge_rate_base must together charge at most the "
           "whole asset share in a month, their monthly rates summing to 1 or less, not ")
DOMAINS = [
    *_domain("mort_be_factor", *_FINITE_0),
    *_domain("amc_rate", "a number from 0 to 1", (0.0,), (BELOW_0, ABOVE_1)),
    *_domain("guar_charge_rate_base", "a number from 0 to 1", (0.0,), (BELOW_0, ABOVE_1)),
    ("amc_rate=1 with no guarantee charge", {"amc_rate": 1.0, "guar_charge_rate_base": 0.0},
     7, None, None),
    ("guar_charge_rate_base=1 with no management charge",
     {"amc_rate": 0.0, "guar_charge_rate_base": 1.0}, 7, None, None),
    ("amc_rate=1 with a guarantee charge", {"amc_rate": 1.0}, 7,
     CHARGED + "1.0000833715521975, under amc_rate 1.0 and guar_charge_rate_base 0.001", None),
    ("both charges at 1", {"amc_rate": 1.0, "guar_charge_rate_base": 1.0}, 7,
     CHARGED + "2.0, under amc_rate 1.0 and guar_charge_rate_base 1.0", None),
    *_domain("guar_charge_cap", *_SHARE),
    *_domain("misc_surplus_rate", "a finite number, 0 or more",
             {0.0: None, BIG: "point_id 7: the estate distribution misc_surplus_pp(1) is "
                              "inf, not a finite number"}, (BELOW_0,)),
    *_domain("prem_alloc_rate", "a number from 0 to 1", (1.0,), (BELOW_0, ABOVE_1)),
    ("prem_alloc_rate=0.0", {"prem_alloc_rate": 0.0}, 7,
     "point_id 7: the bond's units run out in its first month on the books, policy month 0, "
     "so its frame would end before it began", None),
    *_domain("death_benefit_factor", "a finite number, 0 or more",
             {0.0: None, BIG: "point_id 7: the guaranteed death benefit death_guar_pp(0) is "
                              "inf, not a finite number"}, (BELOW_0,)),
    *_domain("shareholder_transfer_divisor", "a finite number above 0",
             {ABOVE_0: "point_id 7: the shareholder transfer shareholder_transfer_pp(11) is "
                       "inf, not a finite number", BIG: None}, (0.0,)),
    *_domain("surr_disc_rate", "a finite number above -1",
             {math.nextafter(-1.0, 0.0): (
                 "point_id 5: the endowment's discount on its bonus cost, "
                 "(1 + surr_disc_rate)^24 in cost_of_bonus_pp(11), is 0.0, below the "
                 "smallest float"), BIG: (
                 "point_id 5: the endowment's discount on its bonus cost, "
                 "(1 + surr_disc_rate)^24 in cost_of_bonus_pp(11), is past the largest "
                 "float")}, (-1.0,), point=5),
    *_domain("smooth_cap", *_SHARE),
    *_domain("corridor_lo", *_SHARE),
    *_domain("corridor_hi", "a finite number, 1 or more", (1.0, BIG), (BELOW_1,)),
    ("bonus_rule_on=True", {"bonus_rule_on": True}, 7, None, None),
    ("bonus_rule_on=1", {"bonus_rule_on": 1}, 7, None, None),
    *[(f"bonus_rule_on={value!r}", {"bonus_rule_on": value}, 7,
       f"point_id 7: bonus_rule_on must be True or False, not {value!r}", None)
      for value in (2, 0.5, math.nan, None, "yes")],
    *_domain("guar_fill_target", "a finite number, 0 or more",
             {0.0: None, BIG: "point_id 5: the supportable bonus rate bonus_supportable(11) "
                              "is inf, not a finite number"}, (BELOW_0,), point=5, also=RULE),
    *_domain("bonus_speed", *_SHARE, point=5, also=RULE),
    *_domain("bonus_change_cap", *_FINITE_0, point=5, also=RULE),
    *_whole_domain("bonus_horizon", (1, 10.0), least=1, also=RULE),
    ("bonus_horizon=2**53-1", {**RULE, "bonus_horizon": WHOLE - 1}, 7,
     "point_id 7: the bonus rule's growth factor (1 + r_e)^m in bonus_supportable(11) is "
     "0.0, below the smallest float", None),
    ("bonus_horizon=4500", {**RULE, "bonus_horizon": 4500}, 7,
     "point_id 7: the bonus rule's growth factor (1 + r_e)^m in bonus_supportable(11) is "
     "0.0, below the smallest float", None),
    ("bonus_horizon=4000", {**RULE, "bonus_horizon": 4000}, 7, None, None),
    ("bonus_horizon=2**53-1 at +7%", {**RULE, "bonus_horizon": WHOLE - 1}, 1, None,
     "point_id 1: the bonus rule's growth factor (1 + r_e)^m in bonus_supportable(11) is "
     "past the largest float"),
    *_domain("mvr_deterrent_factor", *_FINITE_0),
    *_domain("guarantee_exercise_rate", *_SHARE),
    *_domain("guarantee_imminent_factor", *_FINITE_0),
    *_domain("expense_maint", *_FINITE_0),
    *_domain("inflation_rate", "a finite number, -1 or more",
             {-1.0: None, BIG: "point_id 7: the expenses expenses(12) are inf, not a finite "
                               "number, from expense_maint 30.0 and inflation_rate "
                               "1.7976931348623157e+308"},
             (math.nextafter(-1.0, -2.0),)),
    *_whole_domain("issue_age_min", (0, 18.0)),
    ("issue_age_min=2**53-1", {"issue_age_min": WHOLE - 1}, 7,
     f"point_id 7: the issue age, 55, is below issue_age_min, {int(WHOLE - 1)}", None),
    *_whole_domain("omega_age", (120, 121, 120.0), least=None),
    ("omega_age=122", {"omega_age": 122}, 7, OMEGA.format(122), None),
    ("omega_age=18", {"omega_age": 18}, 7, OMEGA.format(18), None),
    ("omega_age=55", {"omega_age": 55}, 7,
     "point_id 7: the issue age, 55, is at or past omega_age, 55: the bond has no cover",
     None),
    ("omega_age=2**53-1", {"omega_age": WHOLE - 1}, 7, OMEGA.format(int(WHOLE - 1)), None),
]


@pytest.mark.parametrize("case, refs, point, message, report", DOMAINS,
                         ids=[c[0] for c in DOMAINS])
def test_each_reference_is_held_to_its_domain_at_both_edges(case, refs, point, message,
                                                            report):
    """``proj_len()`` holds each Reference to its domain, NaN and the infinities outside it.

    ``WP_UK_S`` checks none of them, and off its domain each projects a negative rate,
    charge or expense, a twelfth root with no real value, a factor that changes sign each
    year, or a NaN that a comparison loses, every check passing: a NaN smoothing cap is lost
    through the cap's ``max`` and ``min``, a NaN deterrent reads as certain surrender, a NaN
    estate distribution as an exhausted share, and a NaN limiting age switches off every
    comparison with it, the limiting age sizing every bond's frame.  The frame refuses each
    such Reference, by name, before it projects anything, and every report with it, at the
    nearest value outside each edge of its domain, and on each combination a formula reads,
    the two charges' monthly rates summed, and accepts the edge itself (:data:`DOMAINS`):
    the integer References at a fraction and at exactly ``2**53``, and ``omega_age`` past
    the mortality table's last age.  Each edge accepted projects its reports, in finite
    floats over the whole frame, but where the edge makes a value past the floats, which is
    refused where it first is, naming the point (M11's template).  A whole float, ``120.0``,
    reads as the whole number.  Each case sets its References on a model just read (K7).
    """
    model = mx.read_model(model_path(SEC), name=_name("domain"))
    try:
        for ref, value in refs.items():
            setattr(model.Projection, ref, value)
        p = _row(model, "twin", point, ENTRY[point])
        if message is not None:
            _refused(p.result_cf, message)
        elif report is not None:
            assert p.proj_len() > 0
            _refused(lambda: [p.cells[name]() for name in REPORTS], report)
        else:
            for name in REPORTS:
                frame = p.cells[name]()
                assert list(frame.index) == list(range(p.proj_len())), (case, name)
                assert np.isfinite(frame.to_numpy(dtype=float)).all(), (case, name)
    finally:
        model.close()


# A value that leaves the floats, from an opening state and References each in its domain,
# as (case, the table's edit, the References set, the point, the call, the report that
# reads it first, the start of the message).  An opening premium near the largest float on
# the bond issued at the valuation date, with a regular premium beside it; a unit price of
# 1e305 opening the bond variant at 60, whose withdrawal reads the guarantee it opens with,
# and the down scenario at 68, whose guarantee is the units at that price; an opening asset
# share of 1.79e308 grown by a month's return; the smallest price above 0 buying units with
# a premium; a price near the largest float raised by a declaration in month 0; an
# endowment's bonus cost discounted at a rate a hair above -1, the discount near the
# smallest float; the charges taken grown past the floats by a charge of the whole asset
# share, under a cap of all of it; an opening smoothing account of 1e308 on two policies;
# and each flow on a count that takes it past the floats, the transfers through a divisor
# near 0, and the net cash flow summing an expense and a transfer each just inside them.
# Then the three powers: the inflation factor at the second anniversary under 1e200, the
# bonus rule's growth to a horizon of 20 years at a return of 1e20, and the endowment's
# discount at a rate of 1e200.  Each is refused in the cell where it first is, naming the
# point, the month and what makes it, and so is the report that reads it first; but the
# withdrawals' report reads first the guarantee date's surrenders on that count, past the
# floats too, which it names instead (the report given with its own message).
NET = 1.7e308
PAST_THE_FLOATS = [
    ("a premium", _then(_set("premium_single", [7], BIG), _set("premium_regular", [7], BIG)),
     {}, 7, ("premium_pp", 0), "result_cf",
     "point_id 7: the premium premium_pp(0) is inf, not a finite number, from the single "
     "premium 1.7976931348623157e+308 and the regular premium's twelfth "),
    ("an opening guarantee", _set("unit_price_init", [20], 1e305), {}, 20,
     ("guar_benefit_open", 0), "result_cf",
     "point_id 20: the guarantee the books open with, guar_benefit_open(0), is inf, not a "
     "finite number, from "),
    ("an asset share", _set("asset_share_init", [13], BIG), {}, 13, ("asset_share", 0),
     "result_cf",
     "point_id 13: the asset share of month 0 before its floor, asset_share_at(0, 'AFT_MC'), "
     "is inf, not a finite number, from the opening asset share 1.7976931348623157e+308"),
    ("the units", _set("unit_price_init", [7], ABOVE_0), {}, 7, ("units", 0), "result_cf",
     "point_id 7: the units held units(0) are inf, not a finite number, from the opening "
     "units 0.0 at the price 5e-324 and the premium 25000.0"),
    ("a unit price", _set("unit_price_init", [8], 1.79e308), {}, 8, ("unit_price", 0),
     "result_cf",
     "point_id 8: the unit price unit_price(0) is inf, not a finite number, from the opening "
     "price 1.79e+308 and the bonus rate 0.02"),
    ("a guarantee", _set("unit_price_init", [9], 1e305), {}, 9, ("guar_benefit_pp", 0),
     "result_cf",
     "point_id 9: the guaranteed benefit guar_benefit_pp(0) is inf, not a finite number, from "
     "25000.0 units at the price 1e+305"),
    ("a cost of bonus", None, {"surr_disc_rate": -1.0 + 1e-13}, 5, ("cost_of_bonus_pp", 11),
     "result_cf",
     "point_id 5: the cost of bonus cost_of_bonus_pp(11) is inf, not a finite number, from "
     "the bonus rate 0.015"),
    ("the charges taken",
     _then(_set("asset_share_init", [13], 1.7e308),
           _set("guar_charge_cum_pp_init", [13], 1.69e308)),
     {"guar_charge_cap": 1.0, "guar_charge_rate_base": 1.0, "amc_rate": 0.0}, 13,
     ("guar_charge_cum_pp", 0), "result_cf",
     "point_id 13: the cumulative guarantee charge guar_charge_cum_pp(0) is inf, not a finite "
     "number, from the charges carried in, 1.69e+308, and the month's charge, "),
    ("the smoothing account",
     _then(_set("smoothing_account_init", [24], 1e308), _set("policy_count", [24], 2.0)), {},
     24, ("smoothing_account", 0), "result_payout",
     "point_id 24: the smoothing account smoothing_account(0) is inf, not a finite number, "
     "from the account carried in, inf, and the month's cost, "),
    ("the premiums", _set("policy_count", [7], 1e307), {}, 7, ("premiums", 0), "result_cf",
     "point_id 7: the premiums premiums(0) are inf, not a finite number, from premium_pp(0) "
     "25000.0 on pols_if(0) 1e+307 policies"),
    ("the withdrawals", _set("policy_count", [18], 1.75e306), {}, 18, ("withdrawals", 0),
     ("result_cf", "point_id 18: the claims claims(19, SURRENDER) are inf, not a finite "
                   "number"),
     "point_id 18: the withdrawals withdrawals(0) are inf, not a finite number, from wd_pp(0) "
     "104.16666666666667 on pols_if(0) 1.75e+306 policies"),
    ("the claims", _set("policy_count", [1], 1e308), {}, 1, ("claims", 0, "DEATH"),
     "result_cf",
     "point_id 1: the claims claims(0, DEATH) are inf, not a finite number, from "
     "claim_pp(0, DEATH) "),
    ("the expenses", None, {"expense_maint": NET, "inflation_rate": 1.0}, 1, ("expenses", 48),
     "result_cf",
     "point_id 1: the expenses expenses(48) are inf, not a finite number, from expense_maint "
     "1.7e+308 and inflation_rate 1.0"),
    ("the shareholder transfers", _set("policy_count", [8], 1e10),
     {"shareholder_transfer_divisor": 1e-300}, 8, ("shareholder_transfers", 0), "result_cf",
     "point_id 8: the shareholder transfers shareholder_transfers(0) are inf, not a finite "
     "number, from the transfer on the declaration "),
    ("the net cash flow", _set("policy_count", [8], 11.0),
     {"expense_maint": BIG, "shareholder_transfer_divisor": 3.75e-305}, 8, ("net_cf", 0),
     "result_cf",
     "point_id 8: the net cash flow net_cf(0) is -inf, not a finite number, from premiums "
     "0.0, claims "),
    ("the inflation factor", None, {"inflation_rate": 1e200}, 1, ("inflation_factor", 24),
     "result_cf",
     "point_id 1: the inflation factor inflation_factor(24) is past the largest float, under "
     "inflation_rate 1e+200"),
    ("the bonus rule's growth", _set("fund_return", [1], 1e20),
     {"bonus_rule_on": True, "bonus_horizon": 20}, 1, ("bonus_rate", 11), "result_cf",
     "point_id 1: the bonus rule's growth factor (1 + r_e)^m in bonus_supportable(11) is past "
     "the largest float, under fund_return 1e+20, amc_rate 0.01"),
    ("the endowment's discount", None, {"surr_disc_rate": 1e200}, 5,
     ("cost_of_bonus_pp", 11), "result_cf",
     "point_id 5: the endowment's discount on its bonus cost, (1 + surr_disc_rate)^24 in "
     "cost_of_bonus_pp(11), is past the largest float, under surr_disc_rate 1e+200"),
]

# The cells whose month before is in the same policy year's read, so not a month apart.
SAME_YEAR = frozenset({"bonus_rate"})


@pytest.mark.parametrize("case, edit, refs, point, call, report, message", PAST_THE_FLOATS,
                         ids=[c[0] for c in PAST_THE_FLOATS])
def test_a_value_past_the_floats_is_refused_where_it_first_is(tmp_path, case, edit, refs,
                                                              point, call, report, message):
    """A value past the largest float is refused in the cell where it first is.

    ``Data`` and ``proj_len()`` hold each opening amount, count and Reference to a finite
    number, so a value near the largest float reads; a return, a price, a declaration, a
    count, a sum or a power then takes a value the projection computes past the floats,
    where ``WP_UK_S`` would carry an infinite asset share, price or flow, or a NaN, every
    report infinite and its checks NaN or passing, and where Python's power raises
    ``OverflowError``, naming nothing, and C's gives an infinity.  The cell where the value
    first leaves the floats refuses it, naming the point, the month and what makes it
    (:data:`PAST_THE_FLOATS`), and so does the report that reads it first (UKLIB-SEC-PLAN.md
    §6.6, *Carried into M10 and after*; *Record — M11*).  The month before projects, but in
    a cell whose months read one declaration (:data:`SAME_YEAR`).  Each Reference is set on
    a model just read (K7).
    """
    model = _read_edited(tmp_path, edit or (lambda t: t))
    try:
        for ref, value in refs.items():
            setattr(model.Projection, ref, value)
        p = _point(model, point)
        name, t, *rest = call
        if t > p.t_entry() and name not in SAME_YEAR:
            p.cells[name](t - 1, *rest)
        _refused(lambda: p.cells[name](t, *rest), message)
        report, first = report if isinstance(report, tuple) else (report, message)
        _refused(p.cells[report], first)
    finally:
        model.close()


@pytest.mark.parametrize("grid", GRIDS)
def test_a_whole_limit_written_as_a_float_projects_as_the_int_does(grid):
    """``omega_age = 120.0`` projects what 120 projects, cell for cell (§6.5).

    ``proj_len()`` holds ``omega_age``, ``issue_age_min`` and ``bonus_horizon`` to whole
    numbers, which ``120.0``, ``18.0`` and ``10.0`` are, and reads ``omega_age`` and
    ``bonus_horizon`` as the ``int`` each is: a float limit would make ``proj_len()`` the
    float 720.0, on which every report's ``range`` raises ``TypeError``, where the compiled
    model, typing the Reference ``long long``, would project.  So with the three set as
    floats, and the bonus rule on in both models so that its horizon is read, on a model
    just read, rows of each kind are what the model makes of them under the ints in every
    cell, bit for bit, each integer cell an ``int`` in both.

    The twin of the worked example's bond and the endowment issued at the valuation date
    run by default, and the withdrawing bond in its last month and the future row with the
    full grid.
    """
    floats = mx.read_model(model_path(SEC), name=_name("floats"))
    ints = mx.read_model(model_path(SEC), name=_name("ints"))
    try:
        for model in (floats, ints):
            model.Projection.bonus_rule_on = True
        floats.Projection.omega_age = 120.0
        floats.Projection.issue_age_min = 18.0
        floats.Projection.bonus_horizon = 10.0
        cases = ((("twin", 1, 60), ("twin", 5, 0)) if grid == "core"
                 else (("derived", 4, 402), ("future", 7, -13)))
        for case in cases:
            mine, theirs = _row(floats, *case), _row(ints, *case)
            sweep(theirs)
            assert twin_mismatches(theirs, mine, exempt=frozenset(), rtol=0.0,
                                   atol=0.0) == [], case
            for name in ("proj_len", "cover_end_mth", "fund_exhaust_mth", "t_entry",
                         "duration_mth_init"):
                assert type(mine.cells[name]()) is int, (case, name)
    finally:
        ints.close()
        floats.close()


# The extra rows of the edges test, each a committed row under a label of its own with the
# columns changed, and the frame it projects, as {label: ((row_kind, S point, month), the
# columns changed, proj_len)}: the endowment at 11 holding half a cent of attaching bonus,
# rule 13's edge; the declaration row's duration written 71.0; the bond variant issued 120
# months on, the horizon; a bond issued at 18 and at 119, the youngest issue age and the
# last year before the limiting age, and an endowment issued at 18 maturing at it, 102
# years on, the contract's longest cover; a count of 0; the whole original premium
# withdrawn a year, the share's edge, which exhausts the units in the 14th month; a return
# a hair above -1, the return's edge; a bond with no guarantee date; a smoothing account of
# minus the largest float; a bonus rate of 0; and the smallest price above 0.
EDGES = {
    25: (("derived", 5, 11), {"attaching_bonus_init": 0.005}, 289),
    26: (("derived", 1, 71), {"duration_mth": 71.0}, 709),
    27: (("future", 7, -13), {"duration_mth": -120}, 387),
    28: (("twin", 7, 0), {"age_at_entry": 18, "wd_rate": 0.0}, LONGEST),
    29: (("twin", 5, 0), {"age_at_entry": 18, "policy_term": 102}, LONGEST),
    30: (("twin", 7, 0), {"age_at_entry": 119, "wd_rate": 0.0}, 12),
    31: (("twin", 1, 60), {"policy_count": 0.0}, 720),
    32: (("twin", 1, 60), {"wd_rate": 1.0}, 13),
    33: (("twin", 2, 60), {"fund_return": math.nextafter(-1.0, 0.0)}, 720),
    34: (("twin", 1, 60), {"guarantee_dates": float("nan")}, 720),
    35: (("derived", 1, 71), {"smoothing_account_init": -BIG}, 709),
    36: (("derived", 1, 71), {"bonus_rate_init": 0.0}, 709),
    37: (("twin", 1, 60), {"unit_price_init": ABOVE_0}, 720),
}


def test_the_edges_of_the_in_force_interface_are_accepted(sec_model, tmp_path):
    """Each edge of the in-force interface is read, and projects its reports (T5).

    An asset share and a payout of 0 in force, the down scenario's at 242 with its asset
    share floored, and a smoothing account below 0, which the endowment's payouts short of
    their asset shares leave, are committed rows, and read.  Then :data:`EDGES`, each a
    committed row under a label of its own with columns changed, in one table: ``Data``
    reads it, and each row projects the frame given, its three reports in finite floats
    over the whole of it.  ``71.0`` is a whole number of months, read back as the ``int``
    the policy clock counts in, and the row projects what the committed row does, bit for
    bit; a count of 0 projects zeros; and the whole withdrawal exhausts the bond in its 14th
    month, a forced encashment.
    """
    committed = _committed()
    assert committed.at[_label(committed, "derived", 2, 242), "asset_share_init"] == 0.0
    assert committed.at[_label(committed, "derived", 2, 242), "smoothed_payout_init"] == 0.0
    assert (committed["smoothing_account_init"] < 0.0).sum() >= 3
    rows = []
    for label, (case, changes, _) in EDGES.items():
        row = committed.loc[[_label(committed, *case)]].assign(**changes)
        rows.append(row.set_axis(pd.Index([label], name="point_id")))
    model = mx.read_model(_sec_inputs(tmp_path, pd.concat([committed, *rows])),
                          name=_name("edges"))
    try:
        assert len(model.Data.model_point_table()) == len(committed) + len(EDGES)
        for label, (case, changes, frame) in EDGES.items():
            p = _point(model, label)
            assert p.proj_len() == frame, (label, p.proj_len())
            for name in REPORTS:
                df = p.cells[name]()
                assert list(df.index) == list(range(frame)), (label, name)
                assert np.isfinite(df.to_numpy(dtype=float)).all(), (label, name)
        whole = _point(model, 26)
        assert type(whole.duration_mth_init()) is int and whole.duration_mth_init() == 71
        shipped = _row(sec_model, "derived", 1, 71)
        for name in REPORTS:
            assert frame_mismatches(shipped.cells[name](), whole.cells[name](), rtol=0.0,
                                    atol=0.0) == [], name
        none = _point(model, 31).result_cf()
        assert (none.drop(columns="asset_share") == 0.0).all().all()
        spent = _point(model, 32)
        assert spent.is_forced_encashment() and spent.fund_exhaust_mth() == 73
    finally:
        model.close()


# The S months a point is restated at by the every-state test, by default: the edges of its
# windows, every month of the first policy year and the first anniversary, the declaration
# and the anniversary of every fifth policy year, the guarantee window from its imminence
# to the guarantee date, policy months 106 to 120, and the last month of the frame; with
# UKLIB_SEC_FULL=1, every month.
def _every_state_months(start, end):
    if SEC_FULL:
        return list(range(start + 1, end))
    months = {*range(1, 14), end - 1, *range(106, 121),
              *(m for a in range(60, end, 60) for m in (a - 1, a))}
    return sorted(m for m in months if start < m < end)


def _states(s):
    """Each ``(S point, month)`` of :func:`_every_state_months` on every point of ``s``."""
    table = s.Data.model_point_table()
    found = []
    for key, point_id in zip(point_keys(s), table.index):
        p = projection(s, key)
        found += [(point_id, d) for d in _every_state_months(p.proj_start(), p.proj_len())]
    return found


def _restated(root, s, states):
    """The twins of ``s``'s points and a row in force at each of ``states``, ``(S point,
    month)``, built by the generator out of ``s`` into a copy of the product directory:
    ``(folder, table)``."""
    spec = dataclasses.replace(SPEC, derived=tuple(states), future=(), derived_refs={})
    table, _ = build_sec_table(spec, s)
    return _sec_inputs(root, table), table


def _states_apart(a, b):
    """The state columns, the count among them, in which two tables of :func:`_restated`
    differ on the states, ``(S policy, month)``, they share, of which there must be some."""
    both = a.index.intersection(b.index)
    assert len(both), "the two tables share no state"
    return {c for c in ("policy_count", *STATE)
            if (a.loc[both, c] - b.loc[both, c]).abs().max() > 1e-9 * max(
                1.0, a.loc[both, c].abs().max())}


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


# The other inputs that move the states S reaches, beside the splice's two sets: the
# guarantee charge doubled and the smoothing cap halved, under which the committed rows'
# own References read the cumulants and the payout.
CHARGE_SET = {"guar_charge_rate_base": 0.002}
SMOOTH_SET = {"smooth_cap": 0.05}


def test_every_state_s_reaches_is_accepted_in_force(s_model, tmp_path):
    """Every state ``WP_UK_S`` reaches is a valid opening state (T5).

    ``Data``'s rules and ``proj_len()``'s hold an opening state to what a policy in force
    can be, so they must accept each state the S model reaches: a rule exercised only on
    the rows the other tests choose could refuse a state S reaches elsewhere (D6).  So each
    point of S is restated in force by the generator at the edges of its windows, or with
    ``UKLIB_SEC_FULL=1`` at every month of its frame (:func:`_every_state_months`), into
    one table beside the twins: ``Data`` reads it, and no row's ``proj_len()`` refuses it
    (USLIB-SEC-PLAN.md §5.2, T5, precised at M10).  It runs on each set of inputs on which
    the states differ (precised at M9):

    * S as shipped, its seven points under its own References (``s_model``);
    * with ``UKLIB_SEC_FULL=1``, the others: the splice's main set, its points and variants
      under :data:`SPLICED_REFS`, the estate distribution on, a woman, the crash and the
      pension basis among them; its second set, under :data:`RULE_REFS`, the bonus rule on;
      the guarantee charge doubled, :data:`CHARGE_SET`, and the smoothing cap halved,
      :data:`SMOOTH_SET`, on S's points, the committed rows' own References.  The default
      run takes S as shipped alone, at the cost of the other sets' states, which the full
      grid's leg asks (the M13 review; UKLIB-SEC-PLAN.md U6, as VA and IUL do).

    Each set but the first is read into an S model of its own, which is closed once its
    states are asked, so that one set's projections are held at a time.

    Between them the sets move every state column and the count away from S's shipped
    states, and the rule moves the unit price, the attaching bonus, the bonus rate and the
    withdrawing bond's units, which no other set moves.  ``WP_UK_SEC`` refuses no state
    ``WP_UK_S`` reaches, so none is set aside.
    """
    variants = temp_inputs(tmp_path / "variants", model_path(TWIN),
                           model_points=_s_table_with_variants())
    sets = {"shipped": (None, {})}
    if SEC_FULL:
        sets.update(main=(variants, SPLICED_REFS), rule=(variants, RULE_REFS),
                    charge=(model_path(TWIN), CHARGE_SET),
                    smooth=(model_path(TWIN), SMOOTH_SET))
    found, states = {}, {}
    for tag, (folder, refs) in sets.items():
        s = s_model if folder is None else mx.read_model(folder, name=_name(tag))
        try:
            for ref, value in refs.items():
                setattr(s.Projection, ref, value)
            reached = _states(s)
            restated, rows = _restated(tmp_path / tag, s, reached)
            assert len(rows) == len(s.Data.model_point_table()) + len(reached)
        finally:
            if folder is not None:
                s.close()
        states[tag] = rows.set_index(["source_policy_id", "source_mth"])
        refused = _refused_in_force(restated, refs)
        if refused:
            found[tag] = f"{len(refused)} refused, first: {refused[:5]}"
    assert not found, found
    if not SEC_FULL:
        return
    apart = {tag: _states_apart(states["shipped"], states[tag]) for tag in sets
             if tag != "shipped"}
    assert set().union(*apart.values()) == {"policy_count", *STATE}, apart
    moved_by_rule = apart["rule"] - set().union(
        *(cols for tag, cols in apart.items() if tag != "rule"))
    assert moved_by_rule >= {"unit_price_init", "attaching_bonus_init", "bonus_rate_init",
                             "units_init"}, apart


# ---------------------------------------------------------------------------
# The assumption tables
#
# Data checks each table before a value of it is read, in the cell the projection takes
# its extent from, reading the file as it stands (UKLIB-SEC-PLAN.md §4; USLIB-SEC-PLAN.md
# §7.1, *Precised at M3*, item 9).  Each case is the shipped tables with one fault, read
# from a copy, refused by its Data cell alone, naming the file, the column and its lines,
# the header line 1, and through a projection of the worked example's bond, which reads
# both tables.  The lines are the shipped files': mort_table.csv holds the men at ages 18 to
# 120 on lines 2 to 104 and the women on lines 105 to 207; lapse_table.csv the bond's one
# policy year on line 2 and the endowment's years 1 to 4 on lines 3 to 6.
MORT, LAPSE = "mort_table.csv", "lapse_table.csv"


def _written(column, value, where):
    """An edit of a table that writes ``value`` into ``column`` on the rows ``where``
    picks."""
    def edit(table):
        cells = table[column].astype(object)
        cells[where(table)] = value
        return table.assign(**{column: cells})
    return edit


def _dropped(where):
    return lambda table: table[~where(table)]


def _repeated(where):
    return lambda table: pd.concat([table, table[where(table)]], ignore_index=True)


def _rate_at(sex, age):
    return lambda t: (t["sex"] == sex) & (t["age"] == age)


def _year(chassis, year):
    return lambda t: (t["chassis"] == chassis) & (t["policy_year"] == year)


MORT_RATE = f"{MORT}: mort_rate must be a number from 0 to 1; it is not on line "
LAPSE_RATE = f"{LAPSE}: lapse_rate must be a number from 0 to 1; it is not on line "
AGES = (f"{MORT}: the ages of each sex must run from 18 to 120, the table's first and last, "
        f"one row an age, none below 0; ")
YEARS = (f"{LAPSE}: the policy years of each chassis must run from 1, one row a year, "
         f"without a gap or a repeat; ")
UNREADABLE = [
    ("a blank mortality rate", MORT, _written("mort_rate", float("nan"), _rate_at("M", 60)),
     "mort_age_first", MORT_RATE + "[44]"),
    ("a mortality rate past 1", MORT, _written("mort_rate", ABOVE_1, _rate_at("F", 80)),
     "mort_age_first", MORT_RATE + "[167]"),
    ("a negative mortality rate", MORT, _written("mort_rate", -0.001, _rate_at("M", 18)),
     "mort_age_first", MORT_RATE + "[2]"),
    ("a text mortality rate", MORT, _written("mort_rate", "high", _rate_at("F", 30)),
     "mort_age_first", MORT_RATE + "[117]"),
    ("an age not whole", MORT, _written("age", 50.5, _rate_at("M", 50)), "mort_age_first",
     f"{MORT}: age must be a whole number; it is not on line [34]"),
    ("an unknown sex", MORT, _written("sex", "X", _rate_at("M", 70)), "mort_age_first",
     f"{MORT}: sex must be M or F; it is not on line [54]"),
    ("an age twice", MORT, _repeated(_rate_at("M", 60)), "mort_age_first",
     AGES + "sex M, age 60 repeats on lines [44, 208]"),
    ("a sex missing", MORT, _dropped(lambda t: t["sex"] == "F"), "mort_age_first",
     AGES + "no line holds sex F, ages 18 to 120"),
    ("a gap in a sex", MORT, _dropped(_rate_at("F", 80)), "mort_age_first",
     AGES + "no line holds sex F, age 80"),
    ("an age below 0", MORT, _written("age", -1, _rate_at("M", 18)), "mort_age_first",
     AGES + "age -1, below 0, is on lines [2]; no line holds sex M, age 18"),
    ("a blank lapse rate", LAPSE, _written("lapse_rate", float("nan"),
                                           _year("CWP_endowment", 2)),
     "lapse_last_year", LAPSE_RATE + "[4]"),
    ("a lapse rate past 1", LAPSE, _written("lapse_rate", 1.5, _year("UWP_bond", 1)),
     "lapse_last_year", LAPSE_RATE + "[2]"),
    ("a negative lapse rate", LAPSE, _written("lapse_rate", -0.1, _year("CWP_endowment", 4)),
     "lapse_last_year", LAPSE_RATE + "[6]"),
    ("a text lapse rate", LAPSE, _written("lapse_rate", "high", _year("CWP_endowment", 1)),
     "lapse_last_year", LAPSE_RATE + "[3]"),
    ("a policy year not whole", LAPSE, _written("policy_year", 2.5,
                                                _year("CWP_endowment", 2)),
     "lapse_last_year", f"{LAPSE}: policy_year must be a whole number; it is not on line [4]"),
    ("an unknown chassis", LAPSE, _written("chassis", "UWP_fund", _year("CWP_endowment", 3)),
     "lapse_last_year",
     f"{LAPSE}: chassis must be UWP_bond or CWP_endowment; it is not on line [5]"),
    ("a policy year missing", LAPSE, _dropped(_year("CWP_endowment", 3)), "lapse_last_year",
     YEARS + "no line holds chassis CWP_endowment, policy_year 3"),
    ("a policy year twice", LAPSE, _repeated(_year("CWP_endowment", 2)), "lapse_last_year",
     YEARS + "chassis CWP_endowment, policy_year 2 repeats on lines [4, 7]"),
    ("no policy year 1", LAPSE, _dropped(_year("UWP_bond", 1)), "lapse_last_year",
     YEARS + "no line holds chassis UWP_bond, policy_year 1"),
    ("a chassis missing", LAPSE, _dropped(lambda t: t["chassis"] == "CWP_endowment"),
     "lapse_last_year", YEARS + "no line holds chassis CWP_endowment, policy_year 1"),
]


@pytest.mark.parametrize("case, file, edit, cell, message", UNREADABLE,
                         ids=[c[0] for c in UNREADABLE])
def test_a_table_a_reader_cannot_read_is_refused_naming_its_lines(tmp_path, case, file, edit,
                                                                  cell, message):
    """``Data`` refuses an assumption table before a value of it is read (§4, T5).

    ``WP_UK_S`` reads a blank rate as NaN, which its cap would keep and every flow carry; a
    rate past 1, whose monthly rate has no real value; a negative one, and a key that is not
    whole as one ``int`` truncates; and a gap in a sex or a chassis's years as a
    ``KeyError``, only where a projection reaches it.  Here the cell the projection asks
    first refuses each, naming the file, the column and its lines (:data:`UNREADABLE`), and
    so does a projection of the worked example's bond, which reads both tables:
    ``Data.mort_age_first`` the mortality table and ``Data.lapse_last_year`` the lapse
    table, whichever chassis asks.
    """
    model = _read_edited(tmp_path, lambda t: t, edits={file: edit})
    try:
        call = model.Data.cells[cell]
        _refused((lambda: call("UWP_bond")) if cell == "lapse_last_year" else call, message)
        _refused(_point(model, 1).result_cf, message)
    finally:
        model.close()


def test_a_read_beyond_the_mortality_table_is_refused_naming_its_point(tmp_path):
    """An attained age the mortality table lacks is refused by the cell that reads it.

    ``proj_len()`` holds the limiting age to a year past the table's last age, and the
    issue age to ``issue_age_min``, the table's first, so no frame the shipped References
    admit reads past the table.  With ``issue_age_min`` lowered to 10, the bond issued at
    the valuation date at 15 is admitted by the frame and reads an age the table, from 18,
    lacks: ``mort_rate`` refuses it, naming the point and the age, where ``WP_UK_S``'s
    lookup raised ``KeyError``, and so does every report.  The bound is a Reference, so it
    is what admits the point.
    """
    model = _read_edited(tmp_path, _then(_set("age_at_entry", [7], 15), _set("wd_rate", [7],
                                                                             0.0)))
    try:
        model.Projection.issue_age_min = 10
        p = _point(model, 7)
        assert p.proj_len() == 12 * (120 - 15)
        message = "point_id 7: mort_table.csv has no rate at attained age 15"
        _refused(lambda: p.mort_rate(0), message)
        _refused(p.result_cf, message)
        assert p.mort_rate_mth(36) > 0.0
    finally:
        model.close()


# The rows the float keys are read on, by what they are: the worked example's bond in force,
# the endowment issued at the valuation date and in force, the withdrawing bond in its last
# month and the bond variant issued 13 months on.
FLOAT_KEYED = (("twin", 1, 60), ("twin", 5, 0), ("twin", 6, 240), ("derived", 4, 402),
               ("future", 7, -13))


def test_a_key_written_as_a_float_reads_as_wp_uk_s_reads_it(sec_model, tmp_path):
    """A key written ``70.0`` is the key 70, in every table and in every extent.

    ``WP_UK_S``'s lookups match a float key to the int the projection asks, so a table
    written by a tool that writes every number with a decimal point reads the same.  Each
    assumption table's keys and the model point table's ``duration_mth``, ``age_at_entry``
    and ``policy_term`` are written as floats, and a point of each chassis, issued at the
    valuation date, in force and to be issued later, projects what the committed tables
    project, exactly (:data:`FLOAT_KEYED`): between them they read both tables over the
    ages from 35 to 119 and each chassis's policy years.
    """
    def as_float(*columns):
        return lambda table: table.assign(**{c: table[c].astype(float) for c in columns})

    edits = {MORT: as_float("age"), LAPSE: as_float("policy_year")}
    model = _read_edited(tmp_path, as_float("duration_mth", "age_at_entry", "policy_term"),
                         edits=edits)
    committed = _committed()
    try:
        for case in FLOAT_KEYED:
            point_id = _label(committed, *case)
            for report in REPORTS:
                assert frame_mismatches(_point(sec_model, point_id).cells[report](),
                                        _point(model, point_id).cells[report](),
                                        rtol=0, atol=0) == [], (point_id, report)
    finally:
        model.close()


# ---------------------------------------------------------------------------
# T6 -- regeneration


def test_the_committed_sec_inputs_are_what_s_generates():
    """``model_point_table_sec.csv`` is what WP_UK_S and its table generate today.

    Every row and column, the text cells and the eight opening-state columns included: an
    edit to an S row the table copies or derives from, or to an S formula a row's state is
    read from, fails here until ``python tools/gen_sec_points.py WP_UK_SEC`` regenerates
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

    On the twin of the bond variant issued at the valuation date the two coincide, and its
    policies enter as new business at ``t = 0``, paying the single premium there.  The
    worked example's bond valued 60 months after issue is in policy year 6 at attained age
    60 at ``t = 0``, has 720 months to the limiting age, declares at ``t = 11`` and 23,
    policy months 71 and 83, and meets its guarantee date at ``t = 59``, the end of its
    tenth policy year.  The row at 71 declares in month 0, its price stepping by its rate
    there.  The bond variant issued 13 months on has nothing in force and nothing to do
    before ``t = 13``, where it pays its single premium; its frame of 280 months ends where
    its units run out, at its policy month 267; it declares first at ``t = 24`` and its
    guarantee window opens at ``t = 120``, policy month 107, a year before its guarantee
    date at ``t = 132``.  The twins of S's points in force carry 0 in both cumulants, which
    S restarts where its frame opens, so that they reproduce S.  A timing the model does not
    know is refused rather than answered with another count.
    """
    twin = _row(sec_model, "twin", 7, 0)
    assert [twin.duration_mth(t) for t in (0, 1, 266)] == [0, 1, 266]
    assert (twin.t_entry(), twin.pols_if_init(), twin.pols_new_biz(0), twin.pols_if(0)) == (
        0, 0.0, 1.0, 1.0)
    assert twin.premium_pp(0) == 25000.0 and twin.premium_pp(1) == 0.0
    assert (twin.proj_len(), twin.fund_exhaust_mth()) == (267, 267)
    old = _row(sec_model, "twin", 1, 60)
    assert (old.duration_mth(0), old.duration(0), old.policy_year(0), old.age(0)) == (
        60, 5, 6, 60)
    assert (old.proj_len(), old.t_entry(), old.pols_new_biz(0), old.premium_pp(0)) == (
        720, 0, 0.0, 0.0)
    assert old.is_active(719) and not old.is_active(720)
    assert [t for t in range(30) if old.is_declaration_month(t)] == [11, 23]
    assert [t for t in range(720) if old.is_guarantee_date(t)] == [59]
    assert old.pols_if(0) == old.pols_if_init() == old.policy_count()
    for label in _committed().index[(_committed()["row_kind"] == "twin")
                                    & (_committed()["duration_mth"] > 0)]:
        p = _point(sec_model, label)
        assert (p.guar_charge_cum_pp_init(), p.smoothing_account_init()) == (0.0, 0.0)
    declared = _row(sec_model, "derived", 1, 71)
    assert declared.is_declaration_month(0) and declared.declaration_month(0) == 0
    assert declared.unit_price(0) == declared.unit_price_init() * 1.02
    fut = _row(sec_model, "future", 7, -13)
    assert (fut.duration_mth(0), fut.t_entry(), fut.proj_len()) == (-13, 13, 280)
    assert not fut.is_active(12) and fut.is_active(13)
    assert (fut.pols_if_init(), fut.pols_new_biz(13), fut.pols_if(13)) == (0.0, 1.0, 1.0)
    assert [t for t in range(280) if fut.premium_pp(t) > 0.0] == [13]
    assert [t for t in range(60) if fut.is_declaration_month(t)] == [24, 36, 48]
    assert [t for t in range(280) if fut.is_guarantee_date(t)] == [132]
    assert [t for t in range(140) if fut.guarantee_imminent(t) != 1.0] == list(range(120, 132))
    _refused(lambda: old.pols_if_at(0, "BEF_NOTHING"), "invalid timing")


def test_the_rebased_reads_run_on_the_policy_clock(sec_model):
    """Every read §6.5 rebases is on the policy clock, on every committed point and month.

    ``WP_UK_S`` reads its clock off ``t``, which on the valuation clock is a month since the
    valuation date: its single premium at ``t == 0``, which every bond in force would pay
    again in month 0; its declarations at ``(t + 1) % 12 == 0``, which would put a bond
    valued mid-year's declarations in the wrong months; its declaration month as the policy
    month ``12 x duration(t) + 11``, which the bonus rate passes back as ``t``; and its
    guarantee window at ``12 g - 1 - t``.  On every committed point, at every month of its
    frame: the single premium falls in the issue month alone, ``duration_mth(t) == 0``; a
    declaration falls where ``(duration_mth(t) + 1) % 12 == 0`` and in no other month, and
    the price or the guarantee moves there and nowhere else; ``declaration_month(t)`` is the
    valuation month of the declaration closing ``t``'s policy year, from ``t`` to 11 months
    on; the guarantee date is the declaration of a guarantee year; and the window shuts
    the year before each guarantee date, on the policy clock.  So a policy month passed as
    ``t`` fails here, on every point not issued at the valuation date (R1a).
    """
    for key, label in zip(point_keys(sec_model), sec_model.Data.model_point_table().index):
        p = projection(sec_model, key)
        years = p.guarantee_years()
        for t in range(p.t_entry(), p.proj_len()):
            m = p.duration_mth(t)
            single = p.premium_single_pp() if m == 0 else 0.0
            assert p.premium_pp(t) == p.premium_regular_pp() / 12.0 + single, (label, t)
            assert p.is_declaration_month(t) == ((m + 1) % 12 == 0), (label, t)
            assert p.declaration_month(t) == t + 11 - m % 12, (label, t)
            assert p.duration(p.declaration_month(t)) == p.duration(t), (label, t)
            assert p.is_guarantee_date(t) == (
                p.is_declaration_month(t) and p.policy_year(t) in years), (label, t)
            assert (p.guarantee_imminent(t) != 1.0) == any(
                0 < 12 * g - 1 - m <= 12 for g in years), (label, t)
        assert p.check_declaration_is_annual() is True, label


def test_the_committed_rows_continue_their_s_points(sec_model, s_model):
    """Each committed row in force, or issued later, is its S point from its month on.

    T6 compares a float to 1e-12, which pins a small count only to that much of itself, so
    each committed row is compared with its S point frame by frame and cell by cell, at the
    shipped assumptions (USLIB-SEC-PLAN.md §7.1, *Precised at M3*, item 11): the twins in
    force from S's own months, the derived rows from theirs, and the row issued 13 months
    on from S's issue month, all to 1e-9 relative with no absolute floor but on the
    residuals, every cell but those expense inflation moves (:func:`_continues_s`), which
    the inflation test holds.  The rows read from S under References of their own are S's
    under them, which the test after this one compares.
    """
    table = sec_model.Data.model_point_table()
    s_table = s_model.Data.model_point_table()
    found = []
    for point_id in table.index:
        kind, month = table.at[point_id, "row_kind"], int(table.at[point_id, "source_mth"])
        if kind == "twin" and month == 0:
            continue
        policy = table.at[point_id, "source_policy_id"]
        if (policy, month) in UNDER_REFS:
            continue
        s_point = int(s_table.index[s_table["policy_id"] == policy][0])
        found += [f"point {point_id}: {line}" for line in _continues_s(
            _point(s_model, s_point), _point(sec_model, point_id), month)]
    assert not found, found[:20]


def test_the_committed_rows_under_references_of_their_own_are_s_under_them(sec_model):
    """Each row read from S under References of its own opens with S's state under them,
    and with those References set in both models is S's through its whole frame (K14).

    At S's References each history is what today's References rebuild, so the spec reads
    five rows from S under References of their own (``derived_refs``): the bond variant at
    60 and the 5% bond at 300 under a guarantee charge doubled, the worked example's bond and
    the endowment at 150 under the bonus rule, and the worked example's bond at 156 under a
    smoothing cap of 5%.  Each row's eight state columns are S's under them at its month,
    as the spec's extractors read them, to 1e-12 relative; and with the row's References
    set in both models the row is S's in every month of its frame, in every cell S
    evaluates and the three reports, to 1e-9 relative with no absolute floor but on the
    residuals, but those expense inflation moves (:func:`_continues_s`).  At the shipped
    References the committed model projects each from that history: the K14 test after
    this one holds what each column moves.  Each Reference is set on a model just read (K7).
    """
    assert len(UNDER_REFS) == 5, UNDER_REFS
    for (policy, d), refs in UNDER_REFS.items():
        s_point = int(policy.rsplit("-", 1)[1])
        row = _row(sec_model, "derived", s_point, d)
        sec = mx.read_model(model_path(SEC), name=_name("under_sec"))
        s = mx.read_model(model_path(TWIN), name=_name("under_s"))
        try:
            for model in (sec, s):
                for ref, value in refs.items():
                    setattr(model.Projection, ref, value)
            sp = _point(s, s_point)
            for column, extract in SPEC.state.items():
                want, got = extract(sp, d), row.cells[column]()
                assert got == pytest.approx(want, rel=1e-12, abs=1e-12), (policy, d, column)
            sweep(sp)
            assert _continues_s(sp, _row(sec, "derived", s_point, d), d) == [], (policy, d)
        finally:
            sec.close()
            s.close()


# Each history column (UKLIB-SEC-PLAN.md K14), as (column, the References S reaches its
# history under, the S point and month it is read at, and what month 0 opens with on that
# row, read off the projection, which must be the column).  Each state departs from what
# today's References reach at the same month: the asset share and the charges taken under a
# guarantee charge doubled, on the 5% bond at 300 and the bond variant at 60, the cases
# §6.5 names where a bond reopened without its cumulants parts from S; the withdrawing
# bond's units, the price, the endowment's attaching bonus and the rate under the bonus
# rule; and the payout and the smoothing account under a smoothing cap of 5%.
HISTORIES = [
    ("asset_share_init", CHARGE_SET, (3, 300),
     lambda p: p.asset_share_at(0, "BEF_PREM")),
    ("units_init", RULE, (4, 150), lambda p: p.guar_benefit_open(0) / p.unit_price_init()),
    ("unit_price_init", RULE, (1, 150), lambda p: p.guar_benefit_open(0) / p.units_init()),
    ("attaching_bonus_init", RULE, (5, 150),
     lambda p: p.guar_benefit_open(0) - p.sum_assured()),
    ("smoothed_payout_init", SMOOTH_SET, (1, 156), lambda p: p.smoothed_payout_open(0)),
    ("bonus_rate_init", RULE, (1, 150), lambda p: p.bonus_rate(0)),
    ("guar_charge_cum_pp_init", CHARGE_SET, (7, 60),
     lambda p: p.guar_charge_cum_pp(0) - p.guar_charge_pp(0)),
    ("smoothing_account_init", SMOOTH_SET, (1, 156),
     lambda p: (p.smoothing_account(0) - p.smoothing_cost(0)) / p.pols_if_init()),
]


@pytest.mark.parametrize("column, refs, source, opened", HISTORIES,
                         ids=[c[0] for c in HISTORIES])
def test_each_history_column_is_read_from_the_model_point(s_model, tmp_path, column, refs,
                                                          source, opened):
    """Each history column is the point's own, read, never rebuilt (K14, D6).

    A model that rebuilt a history from today's References, or dropped it, would pass every
    comparison with S at today's References, since S rebuilds it alike.  So each column is
    read on a state S reaches under References of its own (:data:`HISTORIES`), which
    departs from what today's References reach at the same month by more than 1e-6 of
    itself: the committed row read under them (``derived_refs``), or for the units, which no
    committed row departs in, the row built by the generator out of S under the bonus rule,
    beside a copy holding today's value of that column alone.  At today's References month
    0 opens with the column, to the float's rounding (the history's ``opened``), and the
    two rows' reports part; and with the References set in both models the row is S's
    under them through its whole frame, in every cell and the three reports
    (:func:`_continues_s`), which for a committed row the test before this one asserts.
    And the rate declared before the valuation date is where today's rule starts from (D6):
    with the rule on at today's References, the first declaration in the frame is the
    rule's step from the column, and from today's value another.  For the
    cumulants, what they move: the charges taken stop the charge at the cap where today's
    history, or none, would charge on, and the smoothing account runs the column's distance
    from today's in every month, per policy times the count.  Each Reference is set on a
    model just read (K7).
    """
    s_point, d = source
    committed = UNDER_REFS.get((_s_table().at[s_point, "policy_id"], d)) == refs
    s = None if committed else mx.read_model(model_path(TWIN), name=_name("history_s"))
    sec = today = None
    try:
        theirs = SPEC.state[column](_point(s_model, s_point), d)
        if committed:
            table = _committed()
        else:
            for ref, value in refs.items():
                setattr(s.Projection, ref, value)
            spec = dataclasses.replace(SPEC, derived=((s_point, d),), future=(),
                                       derived_refs={})
            table = build_sec_table(spec, s)[0].set_index("point_id")
        label = _label(table, "derived", s_point, d)
        mine = table.at[label, column]
        assert abs(mine - theirs) > 1e-6 * max(abs(mine), abs(theirs)), (column, mine, theirs)
        twin = table.loc[[label]].assign(**{column: theirs})
        twin.index = pd.Index([table.index.max() + 1], name="point_id")
        folder = _sec_inputs(tmp_path, pd.concat([table, twin]))
        today = mx.read_model(folder, name=_name("history_today"))
        p, q = _point(today, label), _point(today, twin.index[0])
        assert opened(p) == pytest.approx(mine, rel=1e-12, abs=1e-12), (column, opened(p))
        assert opened(q) == pytest.approx(theirs, rel=1e-12, abs=1e-12), column
        assert any(frame_mismatches(q.cells[name](), p.cells[name](), rtol=1e-9, atol=0.0)
                   for name in REPORTS), f"{column} moves no report"
        if column == "guar_charge_cum_pp_init":
            first = [next(t for t in range(x.proj_len()) if x.guar_charge_rate(t) == 0.0)
                     for x in (p, q)]
            assert first[0] < first[1], first
        if column == "smoothing_account_init":
            gap = (mine - theirs) * p.pols_if_init()
            assert all(p.smoothing_account(t) - q.smoothing_account(t)
                       == pytest.approx(gap, rel=1e-9) for t in range(p.proj_len()))
        if column == "bonus_rate_init":
            sec = mx.read_model(folder, name=_name("history_rule"))
            for ref, value in RULE_REFS.items():
                setattr(sec.Projection, ref, value)
            declared = [_rule_from(_point(sec, row), rate)
                        for row, rate in ((label, mine), (twin.index[0], theirs))]
            assert declared[0][0] == declared[0][1], declared
            assert declared[1][0] == declared[1][1], declared
            assert declared[0][0] != declared[1][0], declared
            sec.close()
            sec = None
        if committed:
            return
        sec = mx.read_model(folder, name=_name("history_sec"))
        for ref, value in refs.items():
            setattr(sec.Projection, ref, value)
        sp = _point(s, s_point)
        sweep(sp)
        assert _continues_s(sp, _point(sec, label), d) == [], column
    finally:
        for model in (sec, today, s):
            if model is not None:
                model.close()


def _rule_from(p, prev):
    """``(the rate p declares first in its frame, the rule's step from prev at it)``."""
    d = p.declaration_month(0)
    step = p.bonus_speed * (p.bonus_supportable(d) - prev)
    step = max(-p.bonus_change_cap, min(p.bonus_change_cap, step))
    return p.bonus_rate(d), max(0.0, prev + step)


# Rows on which D6's declarations are asserted under the rule, at today's References: the
# worked example's bond valued in a declaration month, 71, its declaration month 0's own
# event, and the down scenario valued mid-year, 68, its year-end declaration at t = 3.
DECLARED = ((("derived", 1, 71), 0), (("derived", 2, 68), 3))


def test_each_declaration_in_the_frame_is_made_at_today_s_references():
    """A declaration at or after the valuation date is the projection's own event (D6).

    With the bonus rule on, set on the committed model just read, every declaration in the
    frame is the rule's at today's References, from this model's own asset share and
    guarantee, and the first starts from ``bonus_rate_init()``, the rate declared before
    the valuation date.  On the row valued in a declaration month (:data:`DECLARED`) that
    declaration is month 0's own event: its rule reads the opening state, the asset share
    the month opens with being ``asset_share_init()`` and the guarantee the units at the
    opening price, and the price steps by it at ``t = 0``.  On the row valued mid-year the
    year-end declaration, at ``t = 3``, is the rule's from the opening rate, and every month
    of the year reads it.  Each differs from the rate the row opens with.
    """
    model = mx.read_model(model_path(SEC), name=_name("declared"))
    try:
        for ref, value in RULE_REFS.items():
            setattr(model.Projection, ref, value)
        for case, d0 in DECLARED:
            p = _row(model, *case)
            assert p.declaration_month(0) == d0 and p.is_declaration_month(d0), case
            init = p.bonus_rate_init()
            got, want = _rule_from(p, init)
            assert got == want != init, (case, got, want, init)
            assert [p.bonus_rate(t) for t in range(d0 + 1)] == [got] * (d0 + 1), case
            opened = p.unit_price_init() if d0 == 0 else p.unit_price(d0 - 1)
            assert p.unit_price(d0) == opened * (1.0 + got), case
        p = _row(model, *DECLARED[0][0])
        assert p.asset_share_at(0, "BEF_PREM") == p.asset_share_init()
        assert p.guar_benefit_open(0) == p.units_init() * p.unit_price_init()
    finally:
        model.close()


def test_under_the_rule_a_first_declaration_s_carries_departs_by_d6(spliced):
    """Where S's first frame year keeps its column, this model declares by the rule (D6).

    ``WP_UK_S``'s first projected year keeps its column under the rule; this model makes
    every declaration in its frame by the rule at today's References.  So under the rule
    set the twin of S's worked example in force at 60 parts from S at its first
    declaration, policy month 71, ``t = 11``: S keeps the 2% it carries, and this model
    declares the rule's step from it.  Before it the row is S's in every cell and report
    but the bonus rate, which every month of the year reads from that declaration (T2,
    :func:`_carried_cut`); the price steps apart there.  The departure ``model-sec.md``
    records.  At the shipped References the rule is off, and the committed twins are S's.
    """
    s, sec = spliced["rule"]
    sp = _point(s, 1)
    assert _carried_cut(sp, 60) == 71
    key = _row_key(sec, "twin", 1, 60)
    p = projection(sec, key)
    try:
        assert sp.bonus_rate(71) == sp.bonus_rate_init() == p.bonus_rate_init() == 0.02
        got, want = _rule_from(p, p.bonus_rate_init())
        assert got == want != 0.02, (got, want)
        assert p.unit_price(10) == sp.unit_price(70)
        assert p.unit_price(11) == sp.unit_price(70) * (1.0 + got) != sp.unit_price(71)
    finally:
        _release(sec, key)


def test_the_bonus_rate_read_is_bounded_by_the_frame(spliced):
    """With the bonus rule on, a frame ending mid-year reads no declaration past it.

    Each month's rate is the one declared at the end of its policy year, the anniversary
    read R2 admits up to 11 months ahead.  Where a forced encashment ends the frame
    mid-year, the year's declaration falls past the frame: ``WP_UK_S`` reads it there, from
    an asset share and a payout it projects past its own last month, which a compiled
    cache sized to the frame does not hold.  This model reads the rate declared before the
    year instead, the recorded departure (``bonus_rate``'s docstring; UKLIB-SEC-PLAN.md
    §6.5): on the withdrawing variant under the rule, restated at its month 302, whose units
    run out at policy month 400, the months of its 34th policy year, from policy month 396
    to the frame's last, hold the rate declared at 395, where S's own read the declaration
    of policy month 407, past its frame, which differs.  And at the bound's edge: the
    variant withdrawing 6%, whose units run out at policy month 287, restated at 280, ends
    its frame the month before its year's declaration, 287, which it does not read.  No
    other cell moves (T2, :func:`_departure`), and no read of the rate lies past the frame.
    """
    s, sec = spliced["rule"]
    for s_point, month, end, first, after in ((12, 302, 400, 396, 407),
                                               (16, 280, 287, 276, 287)):
        sp = _point(s, s_point)
        gone = _departure(sp, month)
        assert gone is not None and sp.proj_len() == end, (s_point, gone, sp.proj_len())
        assert gone[0] == first and sp.declaration_month(first) == after >= end, s_point
        key = _row_key(sec, "derived", s_point, month)
        p = projection(sec, key)
        try:
            assert p.proj_len() == end - month
            months = range(max(first - month, 0), p.proj_len())
            assert [p.bonus_rate(t) for t in months] == [gone[1]] * len(months), s_point
            assert all(sp.bonus_rate(t + month) != gone[1] for t in months), s_point
            if s_point == 16:
                assert p.declaration_month(0) == p.proj_len()
            p.result_payout()
            assert max(p.cells["bonus_rate"].keys()) < p.proj_len(), s_point
        finally:
            _release(sec, key)


def test_the_exhaustion_search_s_never_is_a_month_past_cover(sec_model, s_model):
    """Where the units never run out, ``fund_exhaust_mth()`` is a month past cover.

    ``WP_UK_S``'s search returns 0 for "never", safe there because its month 0 is a bond's
    issue month, which the single premium funds.  On the valuation clock a policy month of 0
    is a real month, and month 0 may be any month of a bond's life, including the one its
    last units are withdrawn in; so this model's "never" is ``cover_end_mth() + 1``, which no
    month of cover reaches.  On every twin, where S's search finds no month this model's
    returns that, and where S's finds one, the bond variant's 267, this model's is the same
    month; and on every committed point the frame ends at the earlier of cover's end and the
    month the units run out.
    """
    table = sec_model.Data.model_point_table()
    for key, label in zip(point_keys(sec_model), table.index):
        p = projection(sec_model, key)
        exhaust, end = p.fund_exhaust_mth(), p.cover_end_mth()
        assert p.proj_len() == min(end, exhaust) - p.duration_mth_init(), label
        assert p.is_forced_encashment() == (exhaust < end), label
        if table.at[label, "row_kind"] == "twin":
            theirs = _point(s_model, label).fund_exhaust_mth()
            assert exhaust == (end + 1 if theirs == 0 else theirs), (label, theirs)
    assert _row(sec_model, "twin", 7, 0).fund_exhaust_mth() == 267


def test_expense_inflation_runs_on_the_valuation_clock(sec_model, s_model):
    """Expense inflation steps on the valuation date's anniversaries, for every point (D7).

    ``WP_UK_S`` inflates the maintenance expense from issue, ``(1 + pi)^duration(t)``, which
    on a policy in force would inflate today's expense by the years the policy has already
    run.  Here the factor is ``(1 + pi)^(t // 12)`` on every committed point, the same for a
    point issued at the valuation date as for one in force 240 months, so the block's
    expenses are in valuation-date pounds; and the expense is the twelfth of
    ``expense_maint`` times it, per policy in force.  On the in-force twins S's expense in
    month ``t + d`` is this model's in month ``t`` times the inflation of the policy years
    before the valuation date, ``1.03^(d // 12)``, and on the twins issued at the valuation
    date the two are the same, bit for bit.
    """
    for key, label in zip(point_keys(sec_model), sec_model.Data.model_point_table().index):
        p = projection(sec_model, key)
        for t in range(p.proj_len()):
            assert p.inflation_factor(t) == (1.0 + INFLATION) ** (t // 12), (label, t)
            assert p.expenses(t) == (p.expense_maint / 12.0 * p.inflation_factor(t)
                                     * p.pols_if(t)), (label, t)
    for s_point, d in ((1, 60), (6, 240)):
        p, sp = _row(sec_model, "twin", s_point, d), _point(s_model, s_point)
        for t in range(0, p.proj_len(), 7):
            assert sp.inflation_factor(t + d) == (1.0 + INFLATION) ** ((t + d) // 12)
            assert sp.expenses(t + d) == pytest.approx(
                p.expenses(t) * (1.0 + INFLATION) ** ((t + d) // 12)
                / (1.0 + INFLATION) ** (t // 12), rel=1e-12), (s_point, t)
    for s_point in (5, 7):
        p, sp = _row(sec_model, "twin", s_point, 0), _point(s_model, s_point)
        assert [p.expenses(t) for t in range(p.proj_len())] == [
            sp.expenses(t) for t in range(sp.proj_len())]


# ---------------------------------------------------------------------------
# The cap on mortality
#
# mort_rate caps the annual rate at 1, the bound second, as WP_UK_S's does: min(q, 1.0).  At
# the shipped mort_be_factor of 0.6 no attained age reaches the cap, so it is held at a
# factor of 2, under which the men's rate passes 1 from attained age 106: on the worked
# example's bond, issued at 55, from policy month 612.
CAP_FACTOR = 2.0
CAP_MONTH, CAP_AGE = 612, 106


def test_an_annual_mortality_past_1_is_capped_in_both_models(tmp_path):
    """Where the annual mortality rate passes 1, both models' rate is 1.

    Under a ``mort_be_factor`` of 2, set with :data:`SPLICED_REFS` in both models, the
    worked example's bond's rate reaches 1 at attained age 106, policy month 612, and stays
    there to the end of the frame, where its uncapped rate passes 1: the capped rate and the
    monthly rate, ``1 - (1 - q)^(1/12)``, are 1.0 in every one of those months, the float,
    not the int 1, which compares equal to it, and S's are floats below 1 in every month
    before.  So every policy in force at the start of the first capped month dies in it,
    none is in force after it, and every report holds finite floats alone.

    Three rows built from S by the generator under the factor: the twin in force at 60,
    restated in force in the month before the cap, opened with S's count and state there,
    each compared with S in every cell, the capped months included, as T2 compares them, to
    1e-9 relative with no absolute floor but for the residuals; and restated five months
    into the capped year, opened with S's state there and one policy, since S's count there
    is 0.  On each, the capped rates are 1.0 from its first capped month, every policy in
    force there dies in it, and the count is 0.0 after it.  This is T2's binding mortality
    cap (UKLIB-SEC-PLAN.md §6.5).
    """
    refs = {**SPLICED_REFS, "mort_be_factor": CAP_FACTOR}
    s = mx.read_model(model_path(TWIN), name=_name("capped_s"))
    sec = None
    try:
        for ref, value in refs.items():
            setattr(s.Projection, ref, value)
        sp = _point(s, 1)
        end = sp.proj_len()
        first = next(t for t in range(sp.proj_start(), end) if sp.mort_rate(t) == 1.0)
        assert (first, sp.age(first)) == (CAP_MONTH, CAP_AGE)
        after = range(CAP_MONTH, end)
        for name in ("mort_rate", "mort_rate_mth"):
            assert all(type(sp.cells[name](t)) is float and sp.cells[name](t) < 1.0
                       for t in range(sp.proj_start(), CAP_MONTH)), name
            assert [(type(sp.cells[name](t)), sp.cells[name](t)) for t in after] == [
                (float, 1.0)] * len(after), name
        _sweep_s(sp)
        assert sp.pols_if(CAP_MONTH) > 0.0
        assert sp.pols_death(CAP_MONTH) == sp.pols_if(CAP_MONTH)
        assert [sp.pols_if(t) for t in range(CAP_MONTH + 1, end)] == [0.0] * (len(after) - 1)
        spec = dataclasses.replace(SPEC, derived=((1, CAP_MONTH - 1), (1, CAP_MONTH + 5)),
                                   future=(), derived_refs={})
        rows, _ = build_sec_table(spec, s)
        emptied = (rows["row_kind"] == "derived") & (rows["policy_count"] == 0.0)
        assert emptied.sum() == 1
        rows.loc[emptied, "policy_count"] = 1.0
        sec = mx.read_model(_sec_inputs(tmp_path, rows), name=_name("capped"))
        for ref, value in refs.items():
            setattr(sec.Projection, ref, value)
        cases = ((("twin", 1, 60), CAP_MONTH - 60, SPLICE_EXEMPT),
                 (("derived", 1, CAP_MONTH - 1), 1, SPLICE_EXEMPT),
                 (("derived", 1, CAP_MONTH + 5), 0, None))
        for case, first, exempt in cases:
            p = _row(sec, *case)
            if exempt is not None:
                assert _continues_s(sp, p, case[2]) == [], case
            capped = range(first, p.proj_len())
            later = range(first + 1, p.proj_len())
            for name in ("mort_rate", "mort_rate_mth"):
                assert [(type(p.cells[name](t)), p.cells[name](t)) for t in capped] == [
                    (float, 1.0)] * len(capped), (case, name)
            assert p.pols_if(first) > 0.0 and p.pols_death(first) == p.pols_if(first)
            assert [p.pols_if(t) for t in later] == [0.0] * len(later), case
            for name in REPORTS:
                frame = p.cells[name]()
                assert (frame.dtypes == "float64").all(), (case, name)
                assert np.isfinite(frame.to_numpy()).all(), (case, name)
    finally:
        if sec is not None:
            sec.close()
        s.close()


def test_a_nan_that_reaches_the_mortality_cap_stays_nan():
    """A NaN that reaches the cap ``min(q, 1.0)`` stays NaN, and is not read as death.

    ``min`` keeps its first argument unless a later one compares smaller, in modelx and
    compiled alike, and no comparison with NaN holds, so with its bound first,
    ``min(1.0, q)``, the cap would turn a NaN into certain death.  It is written with its
    bound second, as ``WP_UK_S`` writes it: ``mort_be_factor`` is set to NaN on a model
    read for the test, and the rate, the monthly rate and the mortality charge, which no
    floor reads before it, must give the float NaN; the asset share, whose floor would read
    a NaN as an exhausted share, refuses it.  The cells are called on their own, without the
    frame: ``proj_len()`` refuses the Reference at NaN before a report reaches the cap (the
    domain test).  The surrender rate's bound keeps ``WP_UK_S``'s order, the bound first,
    and is no cap on a mortality rate; ``Data`` and ``proj_len()`` hold what it reads to
    domains no NaN is in.
    """
    model = mx.read_model(model_path(SEC), name=_name("nan"))
    try:
        model.Projection.mort_be_factor = float("nan")
        p = _row(model, "twin", 1, 60)
        lost = [f"{name}(0) = {value!r}" for name in ("mort_rate", "mort_rate_mth",
                                                      "mort_charge_pp")
                for value in [p.cells[name](0)]
                if not (type(value) is float and math.isnan(value))]
        assert not lost, f"the cap loses a NaN mort_be_factor: {lost}"
        _refused(lambda: p.asset_share(0), "point_id 1: the asset share of month 0 before "
                                           "its floor, asset_share_at(0, 'AFT_MC'), is nan")
    finally:
        model.close()


def test_no_check_passes_a_residual_that_is_not_a_number():
    """No check passes a residual that is NaN (§7.1).

    A check is ``abs(resid) <= tolerance`` over the frame, and no comparison with NaN
    holds, so a NaN residual would fail it, as ``WP_UK_S``'s does (USLIB-SEC-PLAN.md §7.1,
    *Precised at M3*, item 11); and the frame comes first.  With ``mort_be_factor`` NaN, set
    on a model read for the test before it computes anything, the mortality rates and so
    the roll-forward's residual are NaN, and each check, asking ``proj_len()`` for the frame,
    is refused the Reference, by name, before it compares one.  So no check passes; and on
    the shipped References each is the bool True.
    """
    for factor, closes in ((float("nan"), False), (0.6, True)):
        model = mx.read_model(model_path(SEC), name=_name("nan_check"))
        try:
            model.Projection.mort_be_factor = factor
            p = _row(model, "twin", 7, 0)
            assert math.isnan(p.mort_rate_mth(5)) != closes
            for check in ("check_pols_roll_fwd", "check_asset_share_roll_fwd"):
                if closes:
                    assert p.cells[check]() is True, check
                else:
                    _refused(p.cells[check], "point_id 7: mort_be_factor must be a finite "
                                             "number, 0 or more, not nan")
        finally:
            model.close()


@pytest.mark.parametrize("check, resid", [
    ("check_pols_roll_fwd", "check_pols_roll_fwd_resid"),
    ("check_asset_share_roll_fwd", "check_asset_share_roll_fwd_resid")])
def test_a_check_fails_a_residual_that_is_not_a_number(sec_model, check, resid):
    """Each check returns False where its residual is NaN (§7.1, item 11).

    A check is ``abs(resid) <= tolerance`` over the frame, which no NaN passes, as
    ``WP_UK_S``'s are; but no input the frame accepts gives a NaN residual any more, so the
    residual's formula is replaced, on a model read for the test, by one that returns NaN
    in every month.  Then the check is the bool False on every committed point, where with
    its own formula it is True.  A check that asked whether any residual was past its
    tolerance would pass NaN.
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

    Every cell of :data:`OUTSIDE_COVER`, ``pols_if_at`` and ``asset_share_at`` at each
    timing, and ``claim_pp``, ``smoothing_cost_pp`` and ``claims`` at each kind, in every
    month before issue and in the first month past cover, ``cover_end_mth()`` on the
    valuation clock, against :data:`OUTSIDE_COVER`; then whether any of
    :data:`IN_COVER_ONLY` was evaluated on the way at a month outside cover, which only a
    fresh ItemSpace can say: the frame's exhaustion search projects the months in cover,
    where they are read.  A cell that raises is reported as a fault too, so the scan goes
    on.
    """
    faults = []
    outside = [*range(p.t_entry()), p.cover_end_mth() - p.duration_mth_init()]
    for t in outside:
        calls = [(name, (t,), want) for name, want in OUTSIDE_COVER.items()]
        calls += [("pols_if_at", (t, _code(p, timing)), 0.0) for timing in TIMINGS]
        calls += [("asset_share_at", (t, _code(p, timing)), 0.0) for timing in AS_TIMINGS]
        calls += [(name, (t, _code(p, kind)), 0.0) for kind in CLAIM_KINDS
                  for name in ("claim_pp", "smoothing_cost_pp")]
        calls += [("claims", (t, _code(p, kind)), 0.0) for kind in KINDS]
        for name, args, want in calls:
            try:
                got = p.cells[name](*args)
            except Exception as err:        # reported, so the scan goes on
                faults.append(f"{where}: {name}{args} raised {_raised(err)}")
                continue
            if got != want or type(got) is not type(want):
                faults.append(f"{where}: {name}{args} = {got!r}, not {want!r}")
    read = {name: sorted(t for t in p.cells[name].keys() if not 0 <= p.duration_mth(t) <
                         p.cover_end_mth()) for name in IN_COVER_ONLY}
    read = {name: months for name, months in read.items() if months}
    if read:
        faults.append(f"{where}: evaluated outside cover: {read}")
    return faults


def test_every_guarded_cell_holds_its_outside_cover_value(spliced):
    """Outside cover each cell holds :data:`OUTSIDE_COVER`'s value, and reads no rate.

    On every committed point, in every month before issue and in the first month past
    cover, on a model that evaluates nothing else.  So afterwards none of
    :data:`IN_COVER_ONLY` may hold a value at all: ``is_active``'s docstring promises that
    outside cover every balance, count, flow and charge is 0, every flag False, and no
    table is read at a policy year or an attained age the policy does not have.

    The committed table's one point issued after the valuation date is the bond variant,
    so the same scan runs on the splice's future rows, the core's or, with
    ``UKLIB_SEC_FULL=1``, all of them: the endowment and the variants among them.  Each
    row is made afresh first and released after.

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
    futures = _selected(FUTURES, CORE_FUTURES)
    for s_point, k, refs in futures:
        sec = spliced[refs][1]
        key = _row_key(sec, "future", s_point, -k)
        if key in sec.Projection.itemspaces:
            _release(sec, key)
        try:
            faults += _outside_cover_faults(projection(sec, key),
                                            _case_id("future", s_point, -k, refs))
        finally:
            _release(sec, key)
    assert futures and not faults, (
        f"{len(faults)} faults outside cover, first:\n  " + "\n  ".join(faults[:20]))


def test_the_points_sum_row_by_row_into_a_block(spliced):
    """Row ``t`` is the same month on every point, so a block is its frames summed (D3).

    The bond variant's twin, issued at the valuation date, the variant restated at its
    month 266, its last, and the variant issued a month on, summed as ``run_sec.py --block``
    sums them, are indexed 0..267 and equal S's frame added to itself moved 266 months
    earlier and a month later.  A model whose frames sat on the policy clock would fail it.
    """
    s, sec = spliced["main"]
    cases = (("derived", 7, 266, "main"), ("future", 7, -1, "main"))
    keys = [_row_key(sec, *case[:3]) for case in cases if SEC_FULL or case in CORE_GRID]
    assert len(keys) == 2, "the block's rows are the core's"
    twin = _row_key(sec, "twin", 7, 0)
    try:
        frames = [projection(sec, key).result_cf() for key in (twin, *keys)]
    finally:
        for key in (twin, *keys):
            _release(sec, key)
    block = pd.concat(frames).groupby(level="t").sum()
    sdf = _point(s, 7).result_cf()
    expected = pd.concat([sdf, sdf.set_axis(sdf.index - 266).loc[0:],
                          sdf.set_axis(sdf.index + 1)]).groupby(level=0).sum()
    assert list(block.index) == list(range(268))
    assert frame_mismatches(expected, block) == []


# The generator's columns, which an extract carries none of.
GENERATED_COLUMNS = ("row_kind", "source_policy_id", "source_mth")


def _extract():
    """The committed table as an administration extract would hold it: without the
    generator's columns, and labelled :data:`EXTRACT_LABELS`."""
    extract = _committed().drop(columns=list(GENERATED_COLUMNS))
    extract.index = pd.Index(EXTRACT_LABELS, name="point_id")
    return extract


@pytest.mark.parametrize("grid", GRIDS)
def test_an_in_force_extract_needs_none_of_the_generator_columns(sec_model, tmp_path, grid):
    """The model reads the in-force interface and S's columns, never where a row came from,
    and names each point by its label, wherever the row stands.

    ``row_kind``, ``source_policy_id`` and ``source_mth`` record how the generator made each
    shipped row, and an administration extract carries none of them.  Read without them,
    and with every label changed, every point projects what the committed table projects,
    in the three reports, to 1e-12, and ``run_sec.py``, run beside that extract, prints the
    point without saying where it came from.  On every shipped row ``source_mth`` equals
    ``duration_mth``, so a formula that read the one for the other would pass every test
    that leaves ``duration_mth`` as generated.  And a refusal names the extract's label.

    The default run compares :data:`CORE_POINTS` and runs the runner and the moved row, and
    the full grid compares the other committed points.
    """
    extract = _extract()
    folder = _sec_inputs(tmp_path / "extract", extract)
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
            for report in REPORTS:
                assert frame_mismatches(base.cells[report](), mine.cells[report](),
                                        rtol=1e-12, atol=1e-12) == [], (key, report)
            _release(model, key)
    finally:
        model.close()
    if grid == "full":
        return
    runner = folder.parent / "run_sec.py"
    shutil.copy(model_path(SEC).parent / "run_sec.py", runner)
    committed = _committed()
    label = EXTRACT_LABELS[list(committed.index).index(_label(committed, "derived", 4, 402))]
    out = _run_sec(runner, str(label))
    row = _row(sec_model, "derived", 4, 402)
    assert out.splitlines()[:3] == [
        f"model point {label}: WP-000004-M402 - UWP_bond M55, single premium 25,000, "
        f"withdrawals 5.0% a year, fund return +5.0% (life_net), bonus 2.00%",
        f"at the valuation date: in force 402 months: policy year 34, attained age 88, "
        f"{row.pols_if(0):.6f} in force, asset share {row.asset_share_init():,.2f}",
        "proj_len = 1 months from the valuation date (t = 0..0); its units run out at "
        "policy month 403, a forced encashment"]
    last = EXTRACT_LABELS[list(committed.index).index(_label(committed, "derived", 1, 779))]
    moved = _set("duration_mth", [last], 780)(extract)
    model = mx.read_model(_sec_inputs(tmp_path / "moved", moved), name=_name("moved"))
    try:
        _refused(_point(model, last).result_cf,
                 f"point_id {last}: duration_mth 780 is at or past the end of cover, policy "
                 f"month 780")
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
            f"{p.age(0)}, {p.pols_if(0):.6f} in force, asset share "
            f"{p.asset_share_init():,.2f}")


def test_run_sec_prints_a_point_and_the_block(sec_model):
    """The runner prints one point, saying where it came from, and the block (D8).

    Each mode in an interpreter of its own, as a user runs it, with exit code 0 and ASCII
    output, so that it prints on a Windows console under any code page.  The numbers are
    the model's.  The worked example's bond, the runner's default, with its lines at the
    valuation date, each asserted whole, so that a longer number cannot pass for the one
    asserted, and its first twelve rows of cash flows and counts.  The endowment in force
    at 240, restated in force at S's month 299 at its maturity, and the bond variant to be
    issued 13 months on: each with the two lines that say where its row came from and where
    it stands, which only the committed table's generator columns can say.  And the block:
    a line for each committed point, in table order, its first twelve rows, which must be
    the committed points' frames summed row by row, as this test sums them, and those
    frames summed into projection years, each year's count the one in force in its first
    month.  Nothing else runs the runner on the committed table.
    """
    runner = model_path(SEC).parent / "run_sec.py"
    out = _run_sec(runner)
    first = _row(sec_model, "twin", 1, 60)
    assert out.splitlines()[:3] == [
        "model point 1: WP-000001 (S's WP-000001) - UWP_bond M55, single premium 25,000, "
        "withdrawals 0.0% a year, fund return +7.0% (life_net), bonus 2.00%",
        f"at the valuation date: in force 60 months: policy year 6, attained age 60, "
        f"{first.pols_if(0):.6f} in force, asset share 30,000.00",
        "proj_len = 720 months from the valuation date (t = 0..719); cover ends at policy "
        "month 780"]
    assert first.result_cf().head(12).round(2).to_string() in out
    assert first.result_pols().head(12).round(6).to_string() in out
    matured = _row(sec_model, "derived", 5, 299)
    for point_id, lines in (
            ("6", ["model point 6: WP-000006 (S's WP-000006) - CWP_endowment M35, premium "
                   "720 a year for 25 years, sum assured 20,000, fund return +5.0% "
                   "(pension_gross), bonus 1.50%",
                   "at the valuation date: in force 240 months: policy year 21, attained "
                   f"age 55, {_row(sec_model, 'twin', 6, 240).pols_if(0):.6f} in force, "
                   "asset share 24,000.00"]),
            ("16", ["model point 16: WP-000005-M299 (S's WP-000005 at its month 299) - "
                    "CWP_endowment M35, premium 720 a year for 25 years, sum assured 20,000, "
                    "fund return +5.0% (life_net), bonus 1.50%",
                    f"at the valuation date: in force 299 months: policy year 25, attained "
                    f"age 59, {matured.pols_if(0):.6f} in force, asset share "
                    f"{matured.asset_share_init():,.2f}"]),
            ("19", ["model point 19: WP-000007-F13 (S's WP-000007, issued 13 months on) - "
                    "UWP_bond M55, single premium 25,000, withdrawals 5.0% a year, fund "
                    "return -15.0% (life_net), bonus 1.00%",
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
    frames = [p.result_cf().drop(columns="asset_share") for p in points]
    block = pd.concat(frames).groupby(level="t").sum()
    assert block.head(12).round(2).to_string() in out
    years = pd.Index(block.index // 12 + 1, name="proj_year")
    annual = block.drop(columns=["pols_if"]).groupby(years).sum()
    annual.insert(0, "pols_if", block["pols_if"].groupby(years).first())
    assert annual.head(12).round(2).to_string() in out


# run_sec.py run as though it sat at /m/products/with_profits, a copy too shallow to have a
# repository above it: the source compiled under that name, so that its own __file__ is it.
SHALLOW_RUN = """\
import sys
source = open(sys.argv[1], encoding="utf-8").read()
where = "/m/products/with_profits/run_sec.py"
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
    frames = [projection(sec_model, key).result_cf().drop(columns="asset_share")
              for key in point_keys(sec_model)]
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

    ``WP_UK_S`` defaults no other parameter, and running in force adds none: a compiled
    model declares a defaulted parameter in its ``.pxd`` as ``long long life=*``, which the
    C step's typing guard would read as a parameter of that name.  ``claims``'
    ``kind=None`` is R12's total, which the C step settles, with the compensated total of
    three kinds UKLIB-SEC-PLAN.md §6.5's C list names.
    """
    assert _defaulted(TWIN) == ["claims"]
    assert _defaulted(SEC) == ["claims"]


# The texts a computed cell may hold at stage "E", beside a column's name read off the
# model point: the timings and the kinds, and the chassis codes, which the C step makes int
# References, as it did Term's, CI's and ULB's (R9; §6.5's C list, "the codes").
CODES = frozenset({*TIMINGS, *AS_TIMINGS, *CLAIM_KINDS, "UWP_bond", "CWP_endowment"})

# The cells the static check leaves to the C step, each an item of UKLIB-SEC-PLAN.md §6.5's
# C list or a cell that stays Python: the reports and the five checks that build a
# generator; the two label accessors that test a code against a tuple, which the codes
# replace; the guarantee dates' tuple and the two cells that read it, which become a flag
# array; the two readers of the assumption tables, which become arrays; and the claims
# total, the compensated total of three kinds.  Each is needed: the test takes each away
# in turn and the scan finds its cell.
STATIC_EXEMPT = frozenset({
    "result_cf", "result_payout", "result_pols", "check_pols_roll_fwd",
    "check_asset_share_roll_fwd", "check_fb_mvr_exclusive", "check_mvr_bound",
    "check_fund_nonneg", "chassis", "tax_basis", "guarantee_years", "is_guarantee_date",
    "guarantee_imminent", "mort_rate", "surr_rate_base", "claims"})


def _static_findings(exempt):
    """What the C step's static check finds in the Projection source, ``exempt`` aside.

    A tuple, a list, a set, a dict, a comprehension, a generator, an f-string or a lambda,
    a text other than a code (:data:`CODES`) or a column read off ``model_point()``, each
    outside a ``raise``; and a call of a cell that returns a tuple, whose membership test or
    loop no node of the caller shows, as M7's check now flags.  ``(cells read, findings)``,
    each finding led by its cell's name.
    """
    source = (model_path(SEC) / "Projection" / "__init__.py").read_text(encoding="utf-8")
    built = (ast.Tuple, ast.List, ast.Set, ast.Dict, ast.GeneratorExp, ast.ListComp,
             ast.SetComp, ast.DictComp, ast.JoinedStr, ast.Lambda)
    cells = [node for node in ast.parse(source).body if isinstance(node, ast.FunctionDef)]
    tuples = {node.name for node in cells for r in ast.walk(node)
              if isinstance(r, ast.Return) and (
                  isinstance(r.value, ast.Tuple)
                  or (isinstance(r.value, ast.Call)
                      and getattr(r.value.func, "id", None) == "tuple"))}
    found = []
    for node in cells:
        if node.name in exempt:
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
            elif (isinstance(inner, ast.Call) and getattr(inner.func, "id", None) in tuples
                  and node.name not in tuples):
                found.append(f"{node.name}: a call of {inner.func.id}, a tuple, at line "
                             f"{inner.lineno}")
    return {node.name for node in cells}, found


def test_no_computed_cell_builds_a_python_object(sec_model):
    """No computed cell builds a tuple, a text or a generator but to raise (§6.5, *C*).

    The C step's static check refuses a Python object in a computed cell, and turns
    ``WP_UK_S``'s own into the C forms UKLIB-SEC-PLAN.md §6.5 lists (:data:`STATIC_EXEMPT`).
    So that the C step restructures nothing beyond that list, no other ``Projection`` cell
    holds a tuple, a list, a set, a dict, a comprehension, a generator or an f-string, or a
    text other than a timing, a kind or a chassis (:data:`CODES`) or the name of a column it
    reads off ``model_point()``, but inside a ``raise`` statement, nor calls a cell that
    returns a tuple, ``policy_year(t) in guarantee_years()`` among them, read from the
    source as the build reads it (:func:`_static_findings`; *Record — M11*, and M7's
    check).  ``try`` is allowed: a power that leaves the floats raises Python's
    ``OverflowError``, which the cell names.  Every cell of the Space is read, and every
    exemption is a cell of it and needed: with any one exemption taken away, the scan finds
    that cell, so that no exemption is inert, as one was under pandas 3 at M7, where a text
    column reads as ``str``.
    """
    read, found = _static_findings(STATIC_EXEMPT)
    assert read == set(sec_model.Projection.cells)
    assert STATIC_EXEMPT <= read
    assert not found, found
    inert = [name for name in sorted(STATIC_EXEMPT)
             if not any(f.startswith(f"{name}: ")
                        for f in _static_findings(STATIC_EXEMPT - {name})[1])]
    assert not inert, f"exemptions the scan needs none of: {inert}"


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
    outside the parentheses and quotes of the column, ``claims`` of ``claims(t, kind)``.
    """
    lines = doc.splitlines()
    head = next(i for i, line in enumerate(lines) if line.startswith("Notes symbol"))
    start, end = [m.span() for m in re.finditer("=+", lines[head + 1])][1]
    names = set()
    for line in lines[head + 2:]:
        if line.startswith("="):
            break
        bare = re.sub(r"\([^)]*\)|\"[^\"]*\"", "", line[start:end])
        names.update(re.findall(r"[a-z_][a-z0-9_]*", bare))
    return names


_RULE_LINE = re.compile(r"^\s*=+(?:\s+=+)+\s*$")


def _table_overruns(doc):
    """The rows of the RST simple tables in ``doc`` that put text between two columns.

    A simple table's rule lines, runs of ``=`` apart, give its columns' spans, and a row
    whose text runs into the gap between two spans is what docutils rejects as a
    malformed table, dropping the whole table from the page.  Only the last column may run
    past its rule.  Each table runs from a rule line to the blank line that ends it.
    """
    lines, found, i = doc.splitlines(), [], 0
    while i < len(lines):
        if not _RULE_LINE.match(lines[i]):
            i += 1
            continue
        spans = [m.span() for m in re.finditer("=+", lines[i])]
        gaps = set()
        for (_, end), (start, _) in zip(spans, spans[1:]):
            gaps.update(range(end, start))
        i += 1
        while i < len(lines) and lines[i].strip():
            taken = {j for j, ch in enumerate(lines[i]) if ch != " "}
            if not _RULE_LINE.match(lines[i]) and taken & gaps:
                found.append(lines[i].strip())
            i += 1
    return found


# What only WP_UK_S's docstrings may say: a reference into its Spaces, which the SEC pages
# would link to the wrong model; its clock, t counting policy months from issue and t = 0
# the issue month; its frame opening at proj_start(); and its exhaustion's "never", 0.
STALE = re.compile(r"~\.WP_UK_S\.|``t = 0`` is the issue month"
                   r"|``t`` counts \*\*policy months|proj_start\(\)``? is"
                   r"|0 if the units never|``range\(proj_start\(\)")


def test_the_docstrings_describe_the_valuation_clock(sec_model, s_model):
    """The docstrings say what this model is, and none says what only WP_UK_S is.

    Whitespace is collapsed first, as ``test_model_conventions_uk`` collapses it, so that a
    phrase split across a line break still matches.  The model docstring names the
    valuation date, BasicTerm_SE, the policy clock, the SEC table and the product.  The
    symbol map in the Projection docstring maps every cell running in force adds, which are
    exactly the cells ``WP_UK_S`` lacks but the refusals, and names nothing the model lacks:
    every name in it is a cell or a Reference.  No row of a simple table in any docstring
    puts text between two of its columns (:func:`_table_overruns`), which would drop the
    table from the rendered page.  And no docstring says what :data:`STALE` matches.
    """
    flat = {where: re.sub(r"\s+", " ", doc) for where, doc in _docs(sec_model)}
    for phrase in ("valuation date", "BasicTerm_SE", "duration_mth", TABLE, "with-profits"):
        assert phrase in flat["model"], phrase
    added = set(sec_model.Projection.cells) - set(s_model.Projection.cells)
    assert set(NEW_CELLS) == {c for c in added if not c.endswith("_refusal")}, added
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
    assert not stale, f"docstrings that describe WP_UK_S: {stale}"


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


# Parameters a formula could confuse, each pair equal somewhere a point or the shipped
# References hold them (*Record — M11*, the template): the withdrawal election and the fund
# return, both 5% on S's withdrawing bond; the bonus rate and the management charge, both
# 1% on the down scenario, and the bonus rate and the charge's cap, both 2% on the worked
# example; the single premium and the units, 25,000 on every bond in force at 60; the asset
# share and the payout, equal while the corridor holds; and the References that ship equal,
# the MVR deterrent and mortality's factor, the guarantee-imminent factor and the
# corridor's floor, the rule's guarantee-fill target and the corridor's floor, and the
# rule's change cap and the management charge.  Each pair as (what, how a row's value of
# each is read).
CONFUSABLE = [
    ("wd_rate and fund_return", lambda p: (p.wd_rate(), p.fund_return())),
    ("bonus_rate_init and amc_rate", lambda p: (p.bonus_rate_init(), p.amc_rate)),
    ("bonus_rate_init and guar_charge_cap", lambda p: (p.bonus_rate_init(),
                                                       p.guar_charge_cap)),
    ("premium_single and units_init", lambda p: (p.premium_single_pp(), p.units_init())),
    ("asset_share_init and smoothed_payout_init",
     lambda p: (p.asset_share_init(), p.smoothed_payout_init())),
    ("mvr_deterrent_factor and mort_be_factor",
     lambda p: (p.mvr_deterrent_factor, p.mort_be_factor)),
    ("guarantee_imminent_factor and corridor_lo",
     lambda p: (p.guarantee_imminent_factor, p.corridor_lo)),
    ("guar_fill_target and corridor_lo", lambda p: (p.guar_fill_target, p.corridor_lo)),
    ("bonus_change_cap and amc_rate", lambda p: (p.bonus_change_cap, p.amc_rate)),
]


def test_parameters_a_formula_could_confuse_differ_on_some_core_row(sec_model, spliced):
    """Each pair of :data:`CONFUSABLE` is equal somewhere and apart on some core T2 row.

    A formula that read one parameter of a pair for the other would pass every comparison
    with S on a row where the two are equal, so each pair that the shipped points or
    References hold equal somewhere must be apart on some row the default run compares
    with S (*Record — M11*): a core T2 or T3 row on the set it runs on, read through the
    projection as the formulas read it.  The rows' own columns are read on the splice's
    model, and nothing is projected.
    """
    rows = []
    for kind, s_point, month, refs in sorted(CORE_GRID):
        sec = spliced[refs][1]
        rows.append(projection(sec, _row_key(sec, kind, s_point, month)))
    shipped = [projection(sec_model, key) for key in point_keys(sec_model)]
    for what, read in CONFUSABLE:
        assert any(len(set(read(p))) == 1 for p in shipped), f"{what} never ship equal"
        assert any(len(set(read(p))) == 2 for p in rows), f"{what} on no core row apart"


def test_the_core_grid_reaches_every_branch(spliced, splice_records):
    """What the default run's T2 and T3 cases reach, which the full grid only multiplies.

    The default run thins the splice to a core (the module docstring), and this test is
    what keeps the thinning from costing a branch.  First, statically, over S's table with
    the variants, each property below holds of some core case: both chassis, both sexes,
    both tax bases, each fund return, a withdrawal election, each set of References, a bond
    and the endowment issued at the valuation date; and each kind of valuation month: the
    first policy year, on an anniversary, in a declaration month, mid-year, on a guarantee
    date, inside the guarantee window, in the last month of a frame.  And of some core
    future case: issued off the valuation anniversaries, more than a year on, a withdrawing
    bond, and under the bonus rule.

    Then, on the splice's model, of some core row, each of :data:`AT_VALUATION` and
    :data:`IN_FRAME`, what no column of the table shows: every opening-state column in use,
    and each kind of valuation month; and every branch and both sides of every ``min`` and
    ``max`` the full grid reaches: a declaration on each chassis, the smoothing cap's floor
    and ceiling and the cap skipped, the corridor's floor and ceiling, the asset share's
    floor, the market value reduction applied and waived, the guarantee exercised and out
    of the money, the imminent window, the charge's cap binding and released, a forced
    encashment and a maturity paid, the limiting age paying nothing, the lapse table inside
    and past its last year, and under the rule a declaration set by it, held to its cap and
    floored at 0.

    Each core row's branches were recorded by the T2 or T3 case that compared it
    (:func:`_settle`), and a row no case has recorded is evaluated here.  With
    ``UKLIB_SEC_FULL=1`` it asks the same of the full grid's rows, which must reach nothing
    the core does not.
    """
    assert set(CORE_SPLICES) <= set(SPLICES + IN_FORCE_TWINS), "a core case off the grid"
    assert set(CORE_FUTURES) <= set(FUTURES), "a core future off the grid"
    s_table = _s_table_with_variants()

    def at(p, column):
        return s_table.at[p, column]

    splices = {
        **{f"the {c} chassis": (lambda k, p, d, r, c=c: at(p, "chassis") == c)
           for c in ("UWP_bond", "CWP_endowment")},
        **{f"sex {x}": (lambda k, p, d, r, x=x: at(p, "sex") == x) for x in ("M", "F")},
        **{f"the {b} basis on a bond": (
            lambda k, p, d, r, b=b: at(p, "tax_basis") == b and at(p, "chassis") == "UWP_bond")
           for b in ("life_net", "pension_gross")},
        **{f"a return of {f:+.0%}": (lambda k, p, d, r, f=f: at(p, "fund_return") == f)
           for f in (0.07, -0.15, 0.05, -0.40)},
        "a withdrawal election": lambda k, p, d, r: at(p, "wd_rate") > 0.0,
        **{f"the {r} set": (lambda k, p, d, r_, r=r: r_ == r) for r in REF_SETS},
        "a bond issued at the valuation date": lambda k, p, d, r: (
            at(p, "chassis") == "UWP_bond" and int(at(p, "duration_inforce")) == 0),
        "the endowment issued at the valuation date": lambda k, p, d, r: (
            at(p, "chassis") == "CWP_endowment" and int(at(p, "duration_inforce")) == 0),
        "in the first policy year": lambda k, p, d, r: d < 12,
        "on an anniversary": lambda k, p, d, r: d % 12 == 0,
        "in a declaration month": lambda k, p, d, r: d % 12 == 11,
        "mid-year": lambda k, p, d, r: d % 12 not in (0, 11),
        "on a guarantee date": lambda k, p, d, r: d == 119 and at(p, "chassis") == "UWP_bond",
        "inside the guarantee window": lambda k, p, d, r: (
            at(p, "chassis") == "UWP_bond" and 107 <= d < 119),
    }
    futures = {
        "issued off the anniversaries": lambda p, k, r: k % 12 != 0,
        "issued more than a year on": lambda p, k, r: k > 12,
        "a withdrawing bond": lambda p, k, r: at(p, "wd_rate") > 0.0,
        "under the bonus rule": lambda p, k, r: r == "rule",
    }
    missing = [what for what, holds in splices.items()
               if not any(holds(*case) for case in CORE_SPLICES)]
    missing += [what for what, holds in futures.items()
                if not any(holds(*case) for case in CORE_FUTURES)]
    assert not missing, f"no core case reaches: {missing}"
    reached = set()
    for case in sorted(CORE_GRID):
        reached |= _record_of(spliced, splice_records, case)["branches"]
    missing = sorted(REACHED - reached)
    assert not missing, f"no core row reaches: {missing}"
    if SEC_FULL:
        beyond = set()
        for case in GRID:
            if case not in CORE_GRID:
                beyond |= _record_of(spliced, splice_records, case)["branches"]
        beyond &= REACHED
        assert beyond <= reached, f"the full grid alone reaches: {sorted(beyond - reached)}"


# ---------------------------------------------------------------------------
# C2 -- the Phase 1 fingerprint


def test_the_phase_1_fingerprint_is_reproduced(sec_model):
    """Every committed point computes what the model computed when its E step ended (C2).

    The C step changes how the model is represented and no number it computes
    (UKLIB-SEC-PLAN.md U2, after USLIB-SEC-PLAN.md D2), so before it changed anything the
    model as M13 committed it was frozen below (USLIB-SEC-PLAN.md §5.4): for each point,
    each column of ``result_cf()`` and ``result_pols()``, its sum, its largest absolute value
    and its values at five fixed months, the frame's first and last and the three quartiles
    between.  Every later version must reproduce it, to 1e-12 relative, floored at 1e-12 of
    the column's own magnitude (``uk_sec_support.fingerprint_mismatches``), with the same
    points, frames and columns exactly.  ``python tools/gen_sec_fingerprint.py WP_UK_SEC
    --check`` runs the same comparison from the command line.  Until the freeze, which is
    committed alone, the block is empty and the test skips.
    """
    if not FINGERPRINT:
        pytest.skip("the Phase 1 fingerprint is frozen in a commit of its own")
    assert fingerprint_mismatches(FINGERPRINT, sec_model) == []


# WP_UK_SEC's fingerprint, frozen from the model as M13 committed it and committed alone,
# before its C step changed anything; refrozen once, alone, when M13's review set the bonus
# rate's opening state at the last declaration before the valuation date (D6), which moved
# rows 22 and 23, read from S under the bonus rule.  Each point is keyed by its point_id;
# each column holds (its sum over the frame, its largest absolute value, (its values at
# the months)).
# The block is written by tools/gen_sec_fingerprint.py, and is never edited by hand: a
# refreeze goes through the tool's --force, in a commit of its own that says why.
# BEGIN generated fingerprint: WP_UK_SEC -- tools/gen_sec_fingerprint.py
FINGERPRINT = {
    1: {"rows": 720, "months": (0, 179, 359, 539, 719),
        "result_cf": {
            "pols_if": (169.4171172083074, 1.0, (
                1.0, 0.4038313635650291, 0.10213456329837323, 0.0037186395448912794,
                3.625294576735273e-08)),
            "asset_share": (176374586.1835235, 853080.58288399, (
                30141.85174676119, 68535.89428818191, 158065.41525132974,
                366604.94925883715, 853080.58288399)),
            "premiums": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_death": (34538.47415109776, 110.53392118951682, (
                12.542347857716836, 41.84061362285522, 97.58298290906751, 35.81559557012655,
                0.0022963149171459202)),
            "claims_surrender": (45816.29366312256, 128.54316812413578, (
                126.7772979023175, 117.8742908392414, 68.44695812155966, 5.663535809191134,
                0.00012221462670911797)),
            "claims_maturity": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "withdrawals": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (602.2619035819566, 2.5, (
                2.5, 1.5270779277567301, 0.6017169721006952, 0.03413201902806098,
                5.184173976061588e-07)),
            "shareholder_transfers": (5823.422917167304, 59.99685426412443, (
                1.109545750913014, 40.78972977789695, 23.664367379099772, 4.275842400543021,
                0.003078653470465503)),
            "smoothing_cost": (336.9305005939452, 1.779247197762372, (
                -1.779247197762372, 0.41426350121639083, 0.9661681476145356,
                0.35460985712996695, -0.028508154562619903)),
            "net_cf": (-86780.45263496958, 203.36192406909973, (
                -142.92919151094736, -202.0317121677503, -190.29602538182763,
                -45.78910579888876, -0.005497701431718148)),
        },
        "result_pols": {
            "pols_if": (169.4171172083074, 1.0, (
                1.0, 0.4038313635650291, 0.10213456329837323, 0.0037186395448912794,
                3.625294576735273e-08)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_death": (0.2867621007050729, 0.0007302774405201529, (
                0.00041762458917626866, 0.0006044475023182451, 0.0006112457592815527,
                9.672806050405982e-05, 2.665139931096325e-09)),
            "pols_surr": (0.7132378658503838, 0.00426353747555846, (
                0.00426353747555846, 0.0017198913367001505, 0.0004330293126597397,
                1.5448607065019356e-05, 1.4326269893044545e-10)),
            "pols_maturity": (3.3444543137325954e-08, 3.3444543137325954e-08, (
                0.0, 0.0, 0.0, 0.0, 3.3444543137325954e-08)),
        },
    },
    2: {"rows": 720, "months": (0, 179, 359, 539, 719),
        "result_cf": {
            "pols_if": (201.52322290891985, 1.0, (
                1.0, 0.4996363890338725, 0.17272240898342225, 0.008595714222110085,
                1.145415671750053e-07)),
            "asset_share": (1768943.7845160055, 29569.19661755969, (
                29569.19661755969, 98.35404368239527, 0.0, 0.0, 0.0)),
            "premiums": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_death": (14833.405383912319, 42.30563733625083, (
                12.472311825577485, 24.20446726331924, 38.84144169773767, 9.753814764251421,
                0.0004264661656424322)),
            "claims_surrender": (6481.4303901316725, 1898.0846006015577, (
                126.0693779011222, 0.14926682251876794, 0.0, 0.0, 0.0)),
            "claims_maturity": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "withdrawals": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (755.4104321084428, 2.5, (
                2.5, 1.8893621705408672, 1.0175791778129444, 0.07889688630668652,
                1.6379452735692369e-06)),
            "shareholder_transfers": (573.2387004204923, 29.278237534487335, (
                1.0231832389936963, 17.61374600389099, 7.069146169120992,
                0.40843302426551836, 6.318625408324828e-06)),
            "smoothing_cost": (15603.807610624901, 1104.6344725924396, (
                0.1234882358968066, 24.155791316463333, 38.84144169773767,
                9.753814764251421, 0.0004264661656424322)),
            "net_cf": (-22643.48490657293, 1941.4871720521248, (
                -142.06487296569338, -43.85684226026987, -46.9281670446716,
                -10.241144674823627, -0.0004344227363243263)),
        },
        "result_pols": {
            "pols_if": (201.52322290891985, 1.0, (
                1.0, 0.4996363890338725, 0.17272240898342225, 0.008595714222110085,
                1.145415671750053e-07)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_death": (0.41843711609978784, 0.0011381946289203192, (
                0.00041762458917626866, 0.0007478467366990415, 0.0010336935569556834,
                0.00022358896454326296, 8.420537917317777e-09)),
            "pols_surr": (0.5815627780482049, 0.06542861872080553, (
                0.00426353747555846, 0.0012647067076094554, 0.00043523924005326565,
                2.1223744529061893e-05, 2.6902196811862335e-10)),
            "pols_maturity": (1.058520072895689e-07, 1.058520072895689e-07, (
                0.0, 0.0, 0.0, 0.0, 1.058520072895689e-07)),
        },
    },
    3: {"rows": 720, "months": (0, 179, 359, 539, 719),
        "result_cf": {
            "pols_if": (169.4171172083074, 1.0, (
                1.0, 0.4038313635650291, 0.10213456329837323, 0.0037186395448912794,
                3.625294576735273e-08)),
            "asset_share": (78103968.40327853, 269400.362367108, (
                30094.494733263495, 51459.78245760187, 88780.3610286598, 154259.84586906506,
                269400.362367108)),
            "premiums": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_death": (20470.131300646026, 59.804931656201774, (
                12.542347857716836, 31.41578434610107, 54.80928537811607,
                15.070468261615567, 0.0007251695598283631)),
            "claims_surrender": (33984.68405689491, 127.71479683555354, (
                126.7772979023175, 88.50523403730384, 38.44449871392409, 2.3830997447416356,
                3.85950230055519e-05)),
            "claims_maturity": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "withdrawals": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (602.2619035819566, 2.5, (
                2.5, 1.5270779277567301, 0.6017169721006952, 0.03413201902806098,
                5.184173976061588e-07)),
            "shareholder_transfers": (2961.12497779776, 59.70373308512943, (
                1.109545750913014, 36.37965533931487, 15.625183492118106, 1.629157281334553,
                0.0007275282060349471)),
            "smoothing_cost": (199.63440549267875, 1.5575613426778345, (
                -1.5575613426778345, 0.3110473697633776, 0.5426661918625382,
                0.14921255704569922, -0.009002792143766022)),
            "net_cf": (-58018.202238920654, 200.42835873639177, (
                -142.92919151094736, -157.82775165047653, -109.48068455625896,
                -19.116857306719815, -0.0014918112062664683)),
        },
        "result_pols": {
            "pols_if": (169.4171172083074, 1.0, (
                1.0, 0.4038313635650291, 0.10213456329837323, 0.0037186395448912794,
                3.625294576735273e-08)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_death": (0.2867621007050729, 0.0007302774405201529, (
                0.00041762458917626866, 0.0006044475023182451, 0.0006112457592815527,
                9.672806050405982e-05, 2.665139931096325e-09)),
            "pols_surr": (0.7132378658503838, 0.00426353747555846, (
                0.00426353747555846, 0.0017198913367001505, 0.0004330293126597397,
                1.5448607065019356e-05, 1.4326269893044545e-10)),
            "pols_maturity": (3.3444543137325954e-08, 3.3444543137325954e-08, (
                0.0, 0.0, 0.0, 0.0, 3.3444543137325954e-08)),
        },
    },
    4: {"rows": 343, "months": (0, 85, 171, 256, 342),
        "result_cf": {
            "pols_if": (160.62110991928793, 1.0, (
                1.0, 0.6699706399595071, 0.42291707921182636, 0.2467634982975917,
                0.12124010292555126)),
            "asset_share": (9123444.275571682, 29988.22886203022, (
                29988.22886203022, 28582.8319036891, 26827.016739466948, 24749.429672624752,
                22244.875422131485)),
            "premiums": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_death": (5407.080135521979, 18.179968299045637, (
                12.542347857716836, 15.27762687403602, 17.151713756007375,
                17.556584067882007, 14.844204783538334)),
            "claims_surrender": (18761.47798387899, 127.19004042750915, (
                126.7772979023175, 81.61487786795823, 48.32018272702059, 25.975250045377216,
                11.440752606450287)),
            "claims_maturity": (2670.833000679888, 2670.833000679888, (
                0.0, 0.0, 0.0, 0.0, 2670.833000679888)),
            "withdrawals": (16731.365616592495, 104.16666666666667, (
                104.16666666666667, 69.78860832911533, 44.05386241789858, 25.7045310726658,
                12.629177388078258)),
            "expenses": (543.7517163492223, 2.5, (
                2.5, 2.0599484517204325, 1.59925007120386, 1.147631990947639,
                0.6934714672315075)),
            "shareholder_transfers": (1771.3448394441057, 298.50042893117296, (
                1.1637258674029978, 2.4684307741973885, 3.0265562105242187,
                3.1745083580304034, 298.50042893117296)),
            "smoothing_cost": (52.3280763032691, 1.0601135774846462, (
                -1.0601135774846462, 0.15126363241619922, 0.16981894807928033,
                0.17382756502853425, 0.14697232458948772)),
            "net_cf": (-45885.85329246668, 3008.941035856359, (
                -247.15003829410404, -171.2094922970274, -114.15156518265462,
                -73.55850553490308, -3008.941035856359)),
        },
        "result_pols": {
            "pols_if": (160.62110991928793, 1.0, (
                1.0, 0.6699706399595071, 0.42291707921182636, 0.2467634982975917,
                0.12124010292555126)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_death": (0.20386121912283656, 0.0007302774405201529, (
                0.00041762458917626866, 0.0005292114963481805, 0.000633014657307942,
                0.0007023497806933496, 0.0006607019450568166)),
            "pols_surr": (0.676073689479858, 0.00426353747555846, (
                0.00426353747555846, 0.0028553810953009327, 0.0018011761500090191,
                0.001049529237197265, 0.0005143095831891175)),
            "pols_maturity": (0.12006509139730534, 0.12006509139730534, (
                0.0, 0.0, 0.0, 0.0, 0.12006509139730534)),
        },
    },
    5: {"rows": 300, "months": (0, 74, 149, 224, 299),
        "result_cf": {
            "pols_if": (219.45588410772675, 1.0, (
                1.0, 0.8264302140841789, 0.7231094375512656, 0.6291983814305998,
                0.5421463661838041)),
            "asset_share": (3633592.409251401, 28339.994028334775, (
                59.32946196259077, 4898.715439514098, 11024.844002764356,
                18700.505634424462, 28339.994028334775)),
            "premiums": (13167.353046463606, 60.0, (
                60.0, 49.58581284505074, 43.386566253075934, 37.75190288583599,
                32.528781971028245)),
            "claims_death": (790.5590946952217, 6.046186882174327, (
                0.8621220165849763, 1.3431683226776394, 2.215837025304588,
                3.6360020957261927, 5.999055210680071)),
            "claims_surrender": (3492.4162720004906, 25.835297545617635, (
                0.2530481597819001, 5.447646344045867, 10.726884624870571,
                16.966174702978318, 25.835297545617635)),
            "claims_maturity": (15700.041761930715, 15700.041761930715, (
                0.0, 0.0, 0.0, 0.0, 15700.041761930715)),
            "withdrawals": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (772.8758428611177, 2.818478348155215, (
                2.5, 2.4670022376204175, 2.5774528824248355, 2.677920316565223,
                2.7551798450434024)),
            "shareholder_transfers": (455.851914102742, 25.833325164561504, (
                0.0, 0.0, 0.0, 0.0, 25.833325164561504)),
            "smoothing_cost": (110.21440068679111, 367.45133455460837, (
                0.8595645548154718, -0.3196184718216617, -1.4875003175284685,
                -1.786600719860656, 367.45133455460837)),
            "net_cf": (-8044.3918391266825, 15727.93583772559, (
                56.384829823633126, 40.32799594070681, 27.86639172047594,
                14.471805770566254, -15727.93583772559)),
        },
        "result_pols": {
            "pols_if": (219.45588410772675, 1.0, (
                1.0, 0.8264302140841789, 0.7231094375512656, 0.6291983814305998,
                0.5421463661838041)),
            "pols_new_biz": (1.0, 1.0, (
                1.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_death": (0.031241627767410764, 0.00021147866348074503, (
                4.310610082924882e-05, 6.141920513710805e-05, 9.266491084674341e-05,
                0.00013906100659879408, 0.0002067291918918717)),
            "pols_surr": (0.4277303549650776, 0.004265134916299351, (
                0.004265134916299351, 0.0013900701141221568, 0.0012162172796028822,
                0.0010581674510826507, 0.0009116197244003331)),
            "pols_maturity": (0.5410280172675118, 0.5410280172675118, (
                0.0, 0.0, 0.0, 0.0, 0.5410280172675118)),
        },
    },
    6: {"rows": 60, "months": (0, 14, 29, 44, 59),
        "result_cf": {
            "pols_if": (56.62892433542358, 1.0, (
                1.0, 0.973038456716396, 0.9445202582486653, 0.9163626302194888,
                0.8885319300776782)),
            "asset_share": (1698712.2151229507, 32710.961238423326, (
                24135.052081366084, 26035.67709702561, 28173.320472061856,
                30413.275329274045, 32710.961238423326)),
            "premiums": (3397.735460125414, 60.0, (
                60.0, 58.38230740298376, 56.67121549491991, 54.98175781316933,
                53.31191580466069)),
            "claims_death": (525.1358718657921, 11.08285372497666, (
                7.13022906530113, 7.7121216827806425, 8.459699587128988, 9.703369325563761,
                11.08285372497666)),
            "claims_surrender": (2691.8322718006575, 48.87238210468561, (
                42.50839643803349, 42.6025496256827, 44.74804032939161, 46.86429909062299,
                48.87238210468561)),
            "claims_maturity": (29004.778288042733, 29004.778288042733, (
                0.0, 0.0, 0.0, 0.0, 29004.778288042733)),
            "withdrawals": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (150.11203730150248, 2.5575650981705538, (
                2.5, 2.50557402604472, 2.5051038549400224, 2.5033354695796284,
                2.500126288171827)),
            "shareholder_transfers": (581.1263152864415, 410.7270169124913, (
                0.0, 0.0, 0.09658396327932264, 0.4721270446238948, 410.7270169124913)),
            "smoothing_cost": (13.381685244373683, 2.653448479894922, (
                2.653448479894922, 0.35810809969251767, 0.0, 0.0, 0.0)),
            "net_cf": (-29555.24932417171, 29424.648751268396, (
                7.861374496665377, 5.562062068475704, 0.8617877601799735,
                -4.561373117220948, -29424.648751268396)),
        },
        "result_pols": {
            "pols_if": (56.62892433542358, 1.0, (
                1.0, 0.973038456716396, 0.9445202582486653, 0.9163626302194888,
                0.8885319300776782)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_death": (0.018073427721947363, 0.0003465955999216059, (
                0.0002650642775204881, 0.00028245908703208904, 0.00030027343051444965,
                0.0003190504547934653, 0.0003388116186557792)),
            "pols_surr": (0.09522752125864065, 0.0016816966768391456, (
                0.0016816966768391456, 0.001636314257044989, 0.0015883126156097259,
                0.0015409158856860823, 0.0014940674396103828)),
            "pols_maturity": (0.886699051019412, 0.886699051019412, (
                0.0, 0.0, 0.0, 0.0, 0.886699051019412)),
        },
    },
    7: {"rows": 267, "months": (0, 66, 133, 199, 266),
        "result_cf": {
            "pols_if": (176.81806443734877, 1.0, (
                1.0, 0.827564674470349, 0.625441879030398, 0.49835313021911354,
                0.3803043087036435)),
            "asset_share": (1199274.6289545007, 24640.835756407596, (
                24640.835756407596, 6737.234607094408, 1338.188286663984, 0.0, 0.0)),
            "premiums": (25000.0, 25000.0, (
                25000.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_death": (1354.0810251266332, 7.052668553253777, (
                6.692873007392325, 6.7075220325920535, 6.01119787686019, 3.9030004283098085,
                0.03002770881997718)),
            "claims_surrender": (3929.288337167024, 811.5831805442349, (
                62.44915909803726, 16.953904912495254, 2.5442421171407967, 0.0, 0.0)),
            "claims_maturity": (15.021465621918319, 15.021465621918319, (
                0.0, 0.0, 0.0, 0.0, 15.021465621918319)),
            "withdrawals": (18314.381712223832, 103.87505823536169, (
                0.0, 86.20465359066135, 65.15019573233313, 51.91178439782433,
                39.61503215662953)),
            "expenses": (584.03253707868, 2.5, (
                2.5, 2.3984356797999866, 2.1643945828085465, 1.999276192519121,
                1.8217559557787364)),
            "shareholder_transfers": (232.68760226987862, 25.812004963477875, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "smoothing_cost": (2123.721536521738, 706.6687026405285, (
                0.16146768011913523, 7.204708055059273, 5.831707535131686,
                3.9030004283098085, 15.051493330738296)),
            "net_cf": (570.5073205120334, 24928.35796789457, (
                24928.35796789457, -112.26451621554865, -75.87003030914266,
                -57.814061018653256, -56.48828144314656)),
        },
        "result_pols": {
            "pols_if": (176.81806443734877, 1.0, (
                1.0, 0.827564674470349, 0.625441879030398, 0.49835313021911354,
                0.3803043087036435)),
            "pols_new_biz": (1.0, 1.0, (
                1.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_death": (0.12381762946594721, 0.0007560989662605337, (
                0.0002650642775204881, 0.000345611357192472, 0.0004510058118128248,
                0.0005670184462445236, 0.0007493088725334534)),
            "pols_surr": (0.49758956107914054, 0.05588617346461286, (
                0.002534376663007382, 0.002097040539284291, 0.0015843822468133556,
                0.0012619119926369662, 0.00096219037619664)),
            "pols_maturity": (0.3785928094549134, 0.3785928094549134, (
                0.0, 0.0, 0.0, 0.0, 0.3785928094549134)),
        },
    },
    8: {"rows": 709, "months": (0, 177, 354, 531, 708),
        "result_cf": {
            "pols_if": (158.67099906140896, 0.9496956793875818, (
                0.9496956793875818, 0.382946994320866, 0.0957424126107081,
                0.0033718785480403237, 3.625294576735273e-08)),
            "asset_share": (176035074.82568115, 853080.58288399, (
                31685.856551934517, 71508.2510754261, 162603.1313460383, 371829.9325730049,
                853080.58288399)),
            "premiums": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_death": (34399.05523710524, 110.53392118951682, (
                12.692797434046508, 45.36604930830424, 103.37367591103212,
                36.631152449478115, 0.0022963149171459202)),
            "claims_surrender": (44407.05566454699, 128.29803317245984, (
                128.29803317245984, 116.60934932518293, 65.96599525160369,
                5.193012412183797, 0.00012221462670911797)),
            "claims_maturity": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "withdrawals": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (560.0471631497766, 2.3742391984689544, (
                2.3742391984689544, 1.448104221934727, 0.5640581675512807,
                0.030949227902482213, 5.184173976061588e-07)),
            "shareholder_transfers": (5805.781204708521, 59.99685426412443, (
                59.99685426412443, 8.623667012632144, 12.951363938739732, 3.77313724022814,
                0.003078653470465503)),
            "smoothing_cost": (340.55617442752043, 1.0943952593021684, (
                0.1256712617232329, 0.44916880503271606, 1.0235017416933845,
                0.3626846777176006, -0.028508154562619903)),
            "net_cf": (-85171.93926951053, 203.36192406909973, (
                -203.36192406909973, -172.04716986805406, -182.8550932689268,
                -45.62825132979253, -0.005497701431718148)),
        },
        "result_pols": {
            "pols_if": (158.67099906140896, 0.9496956793875818, (
                0.9496956793875818, 0.382946994320866, 0.0957424126107081,
                0.0033718785480403237, 3.625294576735273e-08)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_death": (0.2822742575287348, 0.0007302774405201529, (
                0.0003966162679467162, 0.0006281356322907926, 0.0006294477438538727,
                9.754047373429136e-05, 2.665139931096325e-09)),
            "pols_surr": (0.6674213884143035, 0.004049063119444907, (
                0.004049063119444907, 0.0016307118069799344, 0.0004056871150360592,
                1.3966095672419282e-05, 1.4326269893044545e-10)),
            "pols_maturity": (3.3444543137325954e-08, 3.3444543137325954e-08, (
                0.0, 0.0, 0.0, 0.0, 3.3444543137325954e-08)),
        },
    },
    9: {"rows": 712, "months": (0, 177, 355, 533, 711),
        "result_cf": {
            "pols_if": (193.65307545689353, 0.963158564303706, (
                0.963158564303706, 0.4873317156907075, 0.16662431897291646,
                0.008088772132651474, 1.145415671750053e-07)),
            "asset_share": (1543945.6624436222, 26336.59611973368, (
                26336.59611973368, 0.0, 0.0, 0.0, 0.0)),
            "premiums": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_death": (14738.177158807302, 42.30563733625083, (
                11.213628672344552, 25.87154512898954, 41.1620725420769, 10.207506784339799,
                0.0004264661656424322)),
            "claims_surrender": (5518.869217390825, 1898.0846006015577, (
                67.27244374870833, 0.0, 0.0, 0.0, 0.0)),
            "claims_maturity": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "withdrawals": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (721.4793571713095, 2.4078964107592653, (
                2.4078964107592653, 1.8428323643744422, 0.9816528063846985,
                0.0742438520895634, 1.6379452735692369e-06)),
            "shareholder_transfers": (568.7999987530537, 29.278237534487335, (
                0.0, 0.0, 0.0, 0.0, 6.318625408324828e-06)),
            "smoothing_cost": (15582.544172443002, 1104.6344725924398, (
                3.6144799728173873, 25.87154512898954, 41.1620725420769, 10.207506784339799,
                0.0004264661656424322)),
            "net_cf": (-21547.325732122492, 1941.4871720521248, (
                -80.89396883181215, -27.71437749336398, -42.1437253484616,
                -10.281750636429361, -0.0004344227363243263)),
        },
        "result_pols": {
            "pols_if": (193.65307545689353, 0.963158564303706, (
                0.963158564303706, 0.4873317156907075, 0.16662431897291646,
                0.008088772132651474, 1.145415671750053e-07)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_death": (0.41515034900337866, 0.0011381946289203192, (
                0.00040223869972893996, 0.000799354531855272, 0.0010954528801685962,
                0.0002339890522468853, 8.420537917317777e-09)),
            "pols_surr": (0.5480081094483199, 0.06542861872080553, (
                0.002440634088684865, 0.0012333831877424392, 0.0004196237225383792,
                1.991225695996752e-05, 2.6902196811862335e-10)),
            "pols_maturity": (1.058520072895689e-07, 1.058520072895689e-07, (
                0.0, 0.0, 0.0, 0.0, 1.058520072895689e-07)),
        },
    },
    10: {"rows": 688, "months": (0, 171, 343, 515, 687),
        "result_cf": {
            "pols_if": (171.31320729291434, 0.8961698603101973, (
                0.8961698603101973, 0.4512281215841987, 0.14903264413831854,
                0.006680024219897696, 1.145415671750053e-07)),
            "asset_share": (1007423.5965837496, 18498.994909893423, (
                18498.994909893423, 0.0, 0.0, 0.0, 0.0)),
            "premiums": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_death": (14445.034079677229, 42.30563733625083, (
                12.767582647212881, 26.780943566751475, 40.8616620629698, 8.429758117293956,
                0.0004264661656424322)),
            "claims_surrender": (4104.056636075628, 1898.0846006015577, (
                50.40671332305741, 0.0, 0.0, 0.0, 0.0)),
            "claims_maturity": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "withdrawals": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (626.6443833628603, 2.240424650775493, (
                2.240424650775493, 1.7063075506848304, 0.8524397777809044,
                0.05779383096623267, 1.5439205142513306e-06)),
            "shareholder_transfers": (510.99378104453467, 27.782516372204807, (
                0.0, 16.226937896365975, 0.0, 0.0, 6.318625408324828e-06)),
            "smoothing_cost": (15373.950448772217, 1104.6344725924396, (
                12.863469996399001, 26.780943566751475, 40.8616620629698, 8.429758117293956,
                0.0004264661656424322)),
            "net_cf": (-19686.728880160255, 1941.3532248468628, (
                -65.41472062104579, -44.71418901380228, -41.7141018407507,
                -8.487551948260188, -0.00043432871156500835)),
        },
        "result_pols": {
            "pols_if": (171.31320729291434, 0.8961698603101973, (
                0.8961698603101973, 0.4512281215841987, 0.14903264413831854,
                0.006680024219897696, 1.145415671750053e-07)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_death": (0.40476797701454104, 0.0011381946289203192, (
                0.00044895582589454136, 0.0008111481861268627, 0.0010766910966351672,
                0.00019323730605423018, 8.420537917317777e-09)),
            "pols_surr": (0.4914017774436486, 0.06542861872080553, (
                0.002270696037297476, 0.0011418289240612983, 0.00037507553366720553,
                1.6444320174192843e-05, 2.6902196811862335e-10)),
            "pols_maturity": (1.058520072895689e-07, 1.058520072895689e-07, (
                0.0, 0.0, 0.0, 0.0, 1.058520072895689e-07)),
        },
    },
    11: {"rows": 661, "months": (0, 165, 330, 495, 660),
        "result_cf": {
            "pols_if": (148.03174014557936, 0.8292813643338744, (
                0.8292813643338744, 0.40989745668252614, 0.12947723079120413,
                0.0053071238831693, 1.145415671750053e-07)),
            "asset_share": (594115.2506437511, 12256.78634055271, (
                12256.78634055271, 0.0, 0.0, 0.0, 0.0)),
            "premiums": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_death": (14067.727000443356, 42.30563733625083, (
                14.603313364926773, 29.520069697760913, 39.41500132934523,
                7.537619632574057, 0.0004264661656424322)),
            "claims_surrender": (3102.220712716094, 1898.0846006015577, (
                1898.0846006015577, 0.0, 0.0, 0.0, 0.0)),
            "claims_maturity": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "withdrawals": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (530.8568146793378, 2.073203410834686, (
                2.073203410834686, 1.5048705854908553, 0.7190158730704292,
                0.044578499584826826, 1.4552931607609865e-06)),
            "shareholder_transfers": (456.17012234668215, 26.465849381823666, (
                26.465849381823666, 0.0, 0.0, 0.0, 6.318625408324828e-06)),
            "smoothing_cost": (15029.19781366322, 1104.6344725924396, (
                1104.6344725924396, 29.520069697760913, 39.41500132934523,
                7.537619632574057, 0.0004264661656424322)),
            "net_cf": (-18156.974650185468, 1941.226966759143, (
                -1941.226966759143, -31.02494028325177, -40.13401720241566,
                -7.582198132158884, -0.00043424008421151804)),
        },
        "result_pols": {
            "pols_if": (148.03174014557936, 0.8292813643338744, (
                0.8292813643338744, 0.40989745668252614, 0.12947723079120413,
                0.0053071238831693, 1.145415671750053e-07)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_death": (0.3916789122775514, 0.0011381946289203192, (
                0.000498404800892447, 0.0008852589613848704, 0.0010282891794969572,
                0.00017107584956513317, 8.420537917317777e-09)),
            "pols_surr": (0.43760234620431554, 0.06542861872080553, (
                0.06542861872080553, 0.0010368658048752765, 0.00032562431138154793,
                1.302013144818689e-05, 2.6902196811862335e-10)),
            "pols_maturity": (1.058520072895689e-07, 1.058520072895689e-07, (
                0.0, 0.0, 0.0, 0.0, 1.058520072895689e-07)),
        },
    },
    12: {"rows": 538, "months": (0, 134, 268, 402, 537),
        "result_cf": {
            "pols_if": (70.87109605804426, 0.4934811579670024, (
                0.4934811579670024, 0.24187055787622683, 0.059498572456221414,
                0.0016419539142302243, 1.145415671750053e-07)),
            "asset_share": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "premiums": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_death": (11692.326706492577, 42.30563733625083, (
                26.19800771750338, 39.49385522414838, 30.77555992493588, 2.97623146606729,
                0.0004264661656424322)),
            "claims_surrender": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_maturity": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "withdrawals": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (229.9178154784163, 1.233702894917506, (
                1.233702894917506, 0.8370135463582264, 0.2850135437642902,
                0.010887530566172103, 1.0513347430223995e-06)),
            "shareholder_transfers": (222.80313103464377, 16.922008966651656, (
                0.0, 0.0, 0.0, 0.0, 6.318625408324828e-06)),
            "smoothing_cost": (11692.326706492577, 42.30563733625083, (
                26.19800771750338, 39.49385522414838, 30.77555992493588, 2.97623146606729,
                0.0004264661656424322)),
            "net_cf": (-12145.047653005638, 47.96117515853352, (
                -27.431710612420886, -40.33086877050661, -31.06057346870017,
                -2.987118996633462, -0.0004338361257937794)),
        },
        "result_pols": {
            "pols_if": (70.87109605804426, 0.4934811579670024, (
                0.4934811579670024, 0.24187055787622683, 0.059498572456221414,
                0.0016419539142302243, 1.145415671750053e-07)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_death": (0.3146169475487363, 0.0011381946289203192, (
                0.000809441264143918, 0.0010937334457137241, 0.0007639286792323562,
                6.621836352427482e-05, 8.420537917317777e-09)),
            "pols_surr": (0.17886410456625895, 0.001248946752504123, (
                0.001248946752504123, 0.0006103809550165718, 0.00014889517729104777,
                3.994566223590307e-06, 2.6902196811862335e-10)),
            "pols_maturity": (1.058520072895689e-07, 1.058520072895689e-07, (
                0.0, 0.0, 0.0, 0.0, 1.058520072895689e-07)),
        },
    },
    13: {"rows": 293, "months": (0, 73, 146, 219, 292),
        "result_cf": {
            "pols_if": (2.194633684578459, 0.04347590166475625, (
                0.04347590166475625, 0.010891089179282913, 0.0010684394881920515,
                1.3051479791480757e-05, 3.625294576735273e-08)),
            "asset_share": (51981330.30952366, 269400.36236710794, (
                109318.78747037724, 136873.02447561987, 171479.52605424912,
                214957.5755324661, 269400.36236710794)),
            "premiums": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_death": (4475.041273395681, 52.67544456795697, (
                50.77568524035188, 28.74494704007431, 6.662724478704199,
                0.20831023030836077, 0.000725169559828363)),
            "claims_surrender": (1145.6923570016836, 20.05749050575102, (
                20.05749050575102, 6.236902549441265, 0.7533352288019349,
                0.011086701064708077, 3.859502300555189e-05)),
            "claims_maturity": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "withdrawals": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (6.001726952172051, 0.10868975416189061, (
                0.10868975416189061, 0.03251132511556226, 0.003808348080565443,
                5.554817673780334e-05, 1.842369362442582e-07)),
            "shareholder_transfers": (352.94688789662047, 8.680188033269674, (
                3.8685309746948686, 2.104263785556417, 0.4832604589207778,
                0.015291339558952113, 0.000727528206034947)),
            "smoothing_cost": (44.29832936851095, 0.5215390551282857, (
                0.5027295568351661, 0.2846034360403422, 0.06596756909608074,
                0.0020624775278055723, -0.00900279214376602)),
            "net_cf": (-5979.6822452461565, 76.29070605916863, (
                -74.81039647495966, -37.11862470018756, -7.903128514507476,
                -0.23474381910875877, -0.001491477025805106)),
        },
        "result_pols": {
            "pols_if": (2.194633684578459, 0.04347590166475625, (
                0.04347590166475625, 0.010891089179282913, 0.0010684394881920515,
                1.3051479791480757e-05, 3.625294576735273e-08)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_death": (0.03426119085621411, 0.0004701194813270156, (
                0.0004598748014575215, 0.0002079324520888584, 3.846964743488487e-05,
                9.594812012075593e-07, 2.665139931096325e-09)),
            "pols_surr": (0.009214677363999009, 0.00018347706711608117, (
                0.00018347706711608117, 4.5567068992124126e-05, 4.39314970210269e-06,
                5.1576228645329115e-08, 1.4326269893044545e-10)),
            "pols_maturity": (3.3444543137325954e-08, 3.3444543137325954e-08, (
                0.0, 0.0, 0.0, 0.0, 3.3444543137325954e-08)),
        },
    },
    14: {"rows": 1, "months": (0,),
        "result_cf": {
            "pols_if": (0.12124010292555126, 0.12124010292555126, (
                0.12124010292555126,)),
            "asset_share": (22244.875422131485, 22244.875422131485, (
                22244.875422131485,)),
            "premiums": (0.0, 0.0, (
                0.0,)),
            "claims_death": (14.844204783538334, 14.844204783538334, (
                14.844204783538334,)),
            "claims_surrender": (11.440752606450287, 11.440752606450287, (
                11.440752606450287,)),
            "claims_maturity": (2670.833000679888, 2670.833000679888, (
                2670.833000679888,)),
            "withdrawals": (12.629177388078258, 12.629177388078258, (
                12.629177388078258,)),
            "expenses": (0.30310025731387813, 0.30310025731387813, (
                0.30310025731387813,)),
            "shareholder_transfers": (298.50042893117296, 298.50042893117296, (
                298.50042893117296,)),
            "smoothing_cost": (0.14697232458948772, 0.14697232458948772, (
                0.14697232458948772,)),
            "net_cf": (-3008.5506646464414, 3008.5506646464414, (
                -3008.5506646464414,)),
        },
        "result_pols": {
            "pols_if": (0.12124010292555126, 0.12124010292555126, (
                0.12124010292555126,)),
            "pols_new_biz": (0.0, 0.0, (
                0.0,)),
            "pols_death": (0.0006607019450568166, 0.0006607019450568166, (
                0.0006607019450568166,)),
            "pols_surr": (0.0005143095831891175, 0.0005143095831891175, (
                0.0005143095831891175,)),
            "pols_maturity": (0.12006509139730534, 0.12006509139730534, (
                0.12006509139730534,)),
        },
    },
    15: {"rows": 289, "months": (0, 72, 144, 216, 288),
        "result_cf": {
            "pols_if": (208.68980103843228, 0.9536171193270517, (
                0.9536171193270517, 0.813458210013106, 0.7152915963778248,
                0.625613525923461, 0.5421463661838041)),
            "asset_share": (3629634.6863595597, 28339.994028334775, (
                711.573273690413, 5558.66663972799, 11564.165008255764, 19019.579193403868,
                28339.994028334775)),
            "premiums": (12521.388062305936, 57.2170271596231, (
                57.2170271596231, 48.80749260078636, 42.91749578266949, 37.53681155540766,
                32.528781971028245)),
            "claims_death": (781.2774174488002, 6.046186882174327, (
                0.8344663286736566, 1.3419166556407778, 2.224758886619155,
                3.6695152767134176, 5.999055210680071)),
            "claims_surrender": (3479.244414199263, 25.835297545617635, (
                2.315348809940276, 6.084520843030568, 11.15094975335672, 17.27629610260413,
                25.835297545617635)),
            "claims_maturity": (15700.041761930715, 15700.041761930715, (
                0.0, 0.0, 0.0, 0.0, 15700.041761930715)),
            "withdrawals": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (726.0885708992129, 2.7551798450434024, (
                2.3840427983176293, 2.428279109491297, 2.549586952013167, 2.66266287522742,
                2.7551798450434024)),
            "shareholder_transfers": (455.851914102742, 25.833325164561504, (
                12.400883885055329, 14.635586745483398, 17.805505319315085,
                21.546344513656308, 25.833325164561504)),
            "smoothing_cost": (104.32819019866194, 367.45133455460837, (
                0.22637868592855137, -0.5152635410334949, -1.596777904172529,
                -1.6952336389534113, 367.45133455460837)),
            "net_cf": (-8621.116016274798, 15727.93583772559, (
                39.28228533763621, 24.317189247140316, 9.186694871365361, -7.61800721279362,
                -15727.93583772559)),
        },
        "result_pols": {
            "pols_if": (208.68980103843228, 0.9536171193270517, (
                0.9536171193270517, 0.813458210013106, 0.7152915963778248,
                0.625613525923461, 0.5421463661838041)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_death": (0.03077754390508969, 0.00021147866348074503, (
                4.110671569820969e-05, 6.045514287812647e-05, 9.166307140484077e-05,
                0.00013826870701563163, 0.0002067291918918717)),
            "pols_surr": (0.38181155815445034, 0.004067305672422613, (
                0.004067305672422613, 0.0013682509757700434, 0.0012030682415312343,
                0.001052138545849513, 0.0009116197244003331)),
            "pols_maturity": (0.5410280172675118, 0.5410280172675118, (
                0.0, 0.0, 0.0, 0.0, 0.5410280172675118)),
        },
    },
    16: {"rows": 1, "months": (0,),
        "result_cf": {
            "pols_if": (0.5421463661838041, 0.5421463661838041, (
                0.5421463661838041,)),
            "asset_share": (28339.994028334775, 28339.994028334775, (
                28339.994028334775,)),
            "premiums": (32.528781971028245, 32.528781971028245, (
                32.528781971028245,)),
            "claims_death": (5.999055210680071, 5.999055210680071, (
                5.999055210680071,)),
            "claims_surrender": (25.835297545617635, 25.835297545617635, (
                25.835297545617635,)),
            "claims_maturity": (15700.041761930715, 15700.041761930715, (
                15700.041761930715,)),
            "withdrawals": (0.0, 0.0, (
                0.0,)),
            "expenses": (1.3553659154595101, 1.3553659154595101, (
                1.3553659154595101,)),
            "shareholder_transfers": (25.833325164561504, 25.833325164561504, (
                25.833325164561504,)),
            "smoothing_cost": (367.45133455460837, 367.45133455460837, (
                367.45133455460837,)),
            "net_cf": (-15726.536023796005, 15726.536023796005, (
                -15726.536023796005,)),
        },
        "result_pols": {
            "pols_if": (0.5421463661838041, 0.5421463661838041, (
                0.5421463661838041,)),
            "pols_new_biz": (0.0, 0.0, (
                0.0,)),
            "pols_death": (0.0002067291918918717, 0.0002067291918918717, (
                0.0002067291918918717,)),
            "pols_surr": (0.0009116197244003331, 0.0009116197244003331, (
                0.0009116197244003331,)),
            "pols_maturity": (0.5410280172675118, 0.5410280172675118, (
                0.5410280172675118,)),
        },
    },
    17: {"rows": 1, "months": (0,),
        "result_cf": {
            "pols_if": (3.625294576735273e-08, 3.625294576735273e-08, (
                3.625294576735273e-08,)),
            "asset_share": (853080.58288399, 853080.58288399, (
                853080.58288399,)),
            "premiums": (0.0, 0.0, (
                0.0,)),
            "claims_death": (0.0022963149171459202, 0.0022963149171459202, (
                0.0022963149171459202,)),
            "claims_surrender": (0.00012221462670911797, 0.00012221462670911797, (
                0.00012221462670911797,)),
            "claims_maturity": (0.0, 0.0, (
                0.0,)),
            "withdrawals": (0.0, 0.0, (
                0.0,)),
            "expenses": (9.063236441838182e-08, 9.063236441838182e-08, (
                9.063236441838182e-08,)),
            "shareholder_transfers": (0.003078653470465503, 0.003078653470465503, (
                0.003078653470465503,)),
            "smoothing_cost": (-0.028508154562619903, 0.028508154562619903, (
                -0.028508154562619903,)),
            "net_cf": (-0.0054972736466849595, 0.0054972736466849595, (
                -0.0054972736466849595,)),
        },
        "result_pols": {
            "pols_if": (3.625294576735273e-08, 3.625294576735273e-08, (
                3.625294576735273e-08,)),
            "pols_new_biz": (0.0, 0.0, (
                0.0,)),
            "pols_death": (2.665139931096325e-09, 2.665139931096325e-09, (
                2.665139931096325e-09,)),
            "pols_surr": (1.4326269893044545e-10, 1.4326269893044545e-10, (
                1.4326269893044545e-10,)),
            "pols_maturity": (3.3444543137325954e-08, 3.3444543137325954e-08, (
                3.3444543137325954e-08,)),
        },
    },
    18: {"rows": 167, "months": (0, 41, 83, 124, 166),
        "result_cf": {
            "pols_if": (89.75438761041644, 0.7469373079710191, (
                0.7469373079710191, 0.6093430388420875, 0.5280767516172314,
                0.4531650055469536, 0.3803043087036435)),
            "asset_share": (104772.51463218611, 3174.45925499511, (
                3174.45925499511, 1055.1981639950159, 122.6254307875541, 0.0, 0.0)),
            "premiums": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_death": (688.344710851558, 6.870532020715113, (
                6.707101500516318, 5.486644204787155, 4.656130673302279, 2.70528979330252,
                0.030027708819978894)),
            "claims_surrender": (1007.5655292128696, 811.583180544235, (
                7.209133718284143, 1.95456508522824, 0.1967858561762404, 0.0, 0.0)),
            "claims_maturity": (15.021465621919177, 15.021465621919177, (
                0.0, 0.0, 0.0, 0.0, 15.021465621919177)),
            "withdrawals": (9349.415376085048, 77.8059695803145, (
                77.8059695803145, 63.47323321271745, 55.00799496012828, 47.20468807780767,
                39.61503215662953)),
            "expenses": (267.5266969207925, 1.8673432699275478, (
                1.8673432699275478, 1.6646139770119943, 1.5763781450303238,
                1.5225396837503025, 1.3962242467554797)),
            "shareholder_transfers": (75.38897178958699, 12.652040154537953, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "smoothing_cost": (1391.5352948073523, 706.6687026405286, (
                6.6075699729238355, 5.348754201035283, 4.621679191353547, 2.70528979330252,
                15.051493330739156)),
            "net_cf": (-11403.262750481772, 904.8343482868709, (
                -93.58954806904251, -72.57905647974485, -61.437289634637125,
                -51.43251755486049, -56.06274973412417)),
        },
        "result_pols": {
            "pols_if": (89.75438761041644, 0.7469373079710191, (
                0.7469373079710191, 0.6093430388420875, 0.5280767516172314,
                0.4531650055469536, 0.3803043087036435)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_death": (0.09138336826370519, 0.0007560989662605337, (
                0.00040985053184284045, 0.0004393969465740117, 0.0005484109145457757,
                0.0006189973441556425, 0.0007493088725334534)),
            "pols_surr": (0.27696113025240193, 0.05588617346461286, (
                0.0018924833961722108, 0.0015436003333473324, 0.0013373099888579112,
                0.0011472261307918293, 0.00096219037619664)),
            "pols_maturity": (0.3785928094549134, 0.3785928094549134, (
                0.0, 0.0, 0.0, 0.0, 0.3785928094549134)),
        },
    },
    19: {"rows": 280, "months": (0, 69, 139, 209, 279),
        "result_cf": {
            "pols_if": (176.81806443734877, 1.0, (
                0.0, 0.8522686211246088, 0.6396357057558408, 0.5038804417143988,
                0.3803043087036435)),
            "asset_share": (1199274.6289545004, 24640.835756407596, (
                0.0, 8289.073986085017, 1641.51754128338, 0.0, 0.0)),
            "premiums": (25000.0, 25000.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_death": (1354.0810251266334, 7.052668553253777, (
                0.0, 6.584282154169498, 5.865987254250775, 4.127239336267641,
                0.03002770881997718)),
            "claims_surrender": (3929.2883371670246, 811.5831805442349, (
                0.0, 21.48248008865471, 3.191977122334086, 0.0, 0.0)),
            "claims_maturity": (15.021465621918319, 15.021465621918319, (
                0.0, 0.0, 0.0, 0.0, 15.021465621918319)),
            "withdrawals": (18314.381712223832, 103.87505823536169, (
                0.0, 88.77798136714675, 66.62871934956675, 52.48754601191655,
                39.61503215662953)),
            "expenses": (603.0165171378162, 2.575, (
                0.0, 2.4700322920229207, 2.213513522079926, 2.082093987589221,
                1.8764086344520987)),
            "shareholder_transfers": (232.68760226987862, 25.812004963477875, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "smoothing_cost": (2123.721536521738, 706.6687026405285, (
                0.0, 7.4708804786375325, 5.706774365982206, 4.127239336267641,
                15.051493330738296)),
            "net_cf": (551.523340452899, 24928.28296789457, (
                0.0, -119.31477590199388, -77.90019724823154, -58.69687933577341,
                -56.542934121819926)),
        },
        "result_pols": {
            "pols_if": (176.81806443734877, 1.0, (
                0.0, 0.8522686211246088, 0.6396357057558408, 0.5038804417143988,
                0.3803043087036435)),
            "pols_new_biz": (1.0, 1.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_death": (0.12381762946594721, 0.0007560989662605337, (
                0.0, 0.0003249838315067795, 0.0004210793110281634, 0.0005733073353593331,
                0.0007493088725334534)),
            "pols_surr": (0.4975895610791405, 0.05588617346461286, (
                0.0, 0.0021597185367868642, 0.0016204401527130585, 0.0012759080533416996,
                0.00096219037619664)),
            "pols_maturity": (0.3785928094549134, 0.3785928094549134, (
                0.0, 0.0, 0.0, 0.0, 0.3785928094549134)),
        },
    },
    20: {"rows": 207, "months": (0, 51, 103, 154, 206),
        "result_cf": {
            "pols_if": (121.56474856351588, 0.8423731906178802, (
                0.8423731906178802, 0.7233703890711242, 0.5661353151886602,
                0.47109924637740774, 0.3803043087036435)),
            "asset_share": (310863.90256773337, 7581.623646555877, (
                7581.623646555877, 2421.185264822468, 456.535326787749, 0.0, 0.0)),
            "premiums": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_death": (957.8349772286516, 7.052668553253777, (
                7.049618102535108, 6.679408780046974, 5.097818731558662, 3.153626912747302,
                0.03002770881997718)),
            "claims_surrender": (1510.4503059101553, 811.5831805442349, (
                19.420163720321295, 4.247797388659016, 0.7855723976731147, 0.0, 0.0)),
            "claims_maturity": (15.021465621918319, 15.021465621918319, (
                0.0, 0.0, 0.0, 0.0, 15.021465621918319)),
            "withdrawals": (12662.994642032907, 87.7472073560292, (
                87.7472073560292, 75.35108219490877, 58.972428665485445, 49.07283816431331,
                39.61503215662953)),
            "expenses": (377.5256413680194, 2.1059329765447004, (
                2.1059329765447004, 2.0353993644816955, 1.7929081982448574,
                1.679187198269049, 1.5714626904589062)),
            "shareholder_transfers": (121.96641885535044, 17.03227133822366, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "smoothing_cost": (1669.7946375249444, 707.066870727297, (
                7.6191290208517835, 6.3347612094172945, 5.005100926611342,
                3.153626912747302, 15.051493330738296)),
            "net_cf": (-15645.793451017002, 905.0034788018194, (
                -116.32292215543029, -88.31368772809645, -66.64872799296208,
                -53.90565227532966, -56.237988177826736)),
        },
        "result_pols": {
            "pols_if": (121.56474856351588, 0.8423731906178802, (
                0.8423731906178802, 0.7233703890711242, 0.5661353151886602,
                0.47109924637740774, 0.3803043087036435)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_death": (0.10621604101726997, 0.0007560989662605337, (
                0.00035179575766489487, 0.0004347514489561509, 0.0004898778358872041,
                0.0005872812393119208, 0.0007493088725334534)),
            "pols_surr": (0.35756434014569793, 0.05588617346461286, (
                0.0021345651698612233, 0.0014620240791343995, 0.0014339386818841943,
                0.0011927707050169059, 0.00096219037619664)),
            "pols_maturity": (0.3785928094549134, 0.3785928094549134, (
                0.0, 0.0, 0.0, 0.0, 0.3785928094549134)),
        },
    },
    21: {"rows": 480, "months": (0, 119, 239, 359, 479),
        "result_cf": {
            "pols_if": (28.6500921718857, 0.27572723369715557, (
                0.27572723369715557, 0.10213456329837323, 0.017403362825692808,
                0.0003137605684771608, 3.625294576735273e-08)),
            "asset_share": (67075486.01632072, 267624.7803558709, (
                61237.77383401564, 88086.91016781736, 127372.08695461274,
                184489.86938433343, 267624.7803558709)),
            "premiums": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_death": (14278.086479081943, 59.357067092496074, (
                44.26723548380635, 54.38117779117639, 34.99066465929942, 2.649778190070447,
                0.000720390063564088)),
            "claims_surrender": (9690.346473770398, 71.83263033977693, (
                71.83263033977693, 38.14421416429019, 9.307174755554009,
                0.23571048789047186, 3.834064833444973e-05)),
            "claims_maturity": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "withdrawals": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (87.14580290765875, 0.689318084242889, (
                0.689318084242889, 0.33315609833456994, 0.07629225514687338,
                0.0018484933320479287, 2.870351436029068e-07)),
            "shareholder_transfers": (1390.8976537507592, 27.481017498576293, (
                4.243894240841087, 15.544721997940997, 4.857616077510558, 0.240545439563992,
                0.0007203759751061843)),
            "smoothing_cost": (141.35824227368627, 0.5876937335890685, (
                0.43828946023570464, 0.5384275028829392, 0.3464422243495,
                0.026235427624459913, -0.008943455936342534)),
            "net_cf": (-25446.476409510757, 139.42212136793006, (
                -121.03307814866726, -108.40327005174214, -49.23174774751086,
                -3.1278826108569584, -0.001479393722148325)),
        },
        "result_pols": {
            "pols_if": (28.6500921718857, 0.27572723369715557, (
                0.27572723369715557, 0.10213456329837323, 0.017403362825692808,
                0.0003137605684771608, 3.625294576735273e-08)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_death": (0.1541830640513052, 0.0007302774405201529, (
                0.0007157174939501974, 0.0006112457592815527, 0.0002719922650501511,
                1.4220524797383665e-05, 2.665139931096325e-09)),
            "pols_surr": (0.12154413620130745, 0.0011730117841069554, (
                0.0011730117841069554, 0.0004330293126597397, 7.307075653765876e-05,
                1.277633772938689e-06, 1.4326269893044545e-10)),
            "pols_maturity": (3.3444543137325954e-08, 3.3444543137325954e-08, (
                0.0, 0.0, 0.0, 0.0, 3.3444543137325954e-08)),
        },
    },
    22: {"rows": 630, "months": (0, 157, 314, 471, 629),
        "result_cf": {
            "pols_if": (95.82133253134698, 0.6532178000042325, (
                0.6532178000042325, 0.2627747414618228, 0.060094329289545265,
                0.0017260190109812433, 4.5117876966103824e-08)),
            "asset_share": (103411577.03625713, 411827.1191117323, (
                44828.85279539066, 87849.61869237697, 171564.63318496157,
                333549.28197779326, 0.0)),
            "premiums": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_death": (29537.859275599396, 97.30366173013704, (
                23.362026296483148, 60.521103907520875, 90.94773012390164,
                18.74374808543255, 0.0023042255844270268)),
            "claims_surrender": (32264.677243578328, 124.80268949203594, (
                124.80268949203594, 98.20785141043015, 43.59161891569407, 2.376440422127904,
                0.0)),
            "claims_maturity": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "withdrawals": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (321.1510635240652, 1.633044500010581, (
                1.633044500010581, 0.9647339172005137, 0.32399726443684373,
                0.013665871950314774, 5.24595244012782e-07)),
            "shareholder_transfers": (4137.743415812702, 151.13264760249294, (
                2.8134388408281126, 2.366538457619104, 1.3883769438737437,
                0.10714651847189918, 0.00018473687967170144)),
            "smoothing_cost": (302.98147197777183, 0.9634025913874924, (
                0.23130719105428732, 0.5992188505695165, 0.9004725754841791,
                0.18558166421220293, 0.0023042255844270268)),
            "net_cf": (-66261.4309985145, 299.87932214147816, (
                -152.61119912935777, -162.06022769277064, -136.2517232479063,
                -21.24100089798267, -0.002489487059342741)),
        },
        "result_pols": {
            "pols_if": (95.82133253134698, 0.6532178000042325, (
                0.6532178000042325, 0.2627747414618228, 0.060094329289545265,
                0.0017260190109812433, 4.5117876966103824e-08)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_death": (0.2455787211843951, 0.0007302774405201529, (
                0.0005159783858624011, 0.0006820961314218089, 0.0005248590917414703,
                5.5638454117421535e-05, 3.3168464786367896e-09)),
            "pols_surr": (0.407639037124774, 0.0027839813358968724, (
                0.0027839813358968724, 0.0011179086815883016, 0.00025408277980403177,
                7.1247055548634656e-06, 1.0596764439419843e-10)),
            "pols_maturity": (4.1695062843072834e-08, 4.1695062843072834e-08, (
                0.0, 0.0, 0.0, 0.0, 4.1695062843072834e-08)),
        },
    },
    23: {"rows": 150, "months": (0, 37, 74, 111, 149),
        "result_cf": {
            "pols_if": (94.46124186628127, 0.721800555360816, (
                0.721800555360816, 0.6745068393906527, 0.6291983814305998,
                0.5855618581059508, 0.5421463661838041)),
            "asset_share": (2917538.3597850446, 29047.50825167064, (
                11253.97220649939, 14915.588082474042, 19033.753216575158,
                23680.521589141368, 29047.50825167064)),
            "premiums": (5667.674511976877, 43.30803332164896, (
                43.30803332164896, 40.470410363439164, 37.75190288583599, 35.13371148635705,
                32.528781971028245)),
            "claims_death": (521.9541407684952, 6.004967907340347, (
                2.0434120910603233, 2.554439533530583, 3.18784680839438, 3.96938026330924,
                6.004967907340347)),
            "claims_surrender": (2666.671564804548, 26.48028146690439, (
                10.930000375155704, 13.720909259295299, 17.170726627382468,
                21.43735554293309, 26.48028146690439)),
            "claims_maturity": (15715.515795963054, 15715.515795963054, (
                0.0, 0.0, 0.0, 0.0, 15715.515795963054)),
            "withdrawals": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (279.1125151843157, 1.952482875990099, (
                1.80450138840204, 1.8426295877170744, 1.8782394307988437,
                1.9100635248246751, 1.932427709626635)),
            "shareholder_transfers": (418.49475073433734, 316.82891799110024, (
                0.0, 0.0, 0.0, 0.0, 316.82891799110024)),
            "smoothing_cost": (-287.06437476477197, 2.477622897523966, (
                -1.730048700402398, -2.3383530577429448, -2.4291775715926653,
                -1.9369915969433973, 0.0)),
            "net_cf": (-13934.074255477875, 16034.233609067, (
                28.530119467030897, 22.35243198289621, 15.515090019260297,
                7.816912155290044, -16034.233609067)),
        },
        "result_pols": {
            "pols_if": (94.46124186628127, 0.721800555360816, (
                0.721800555360816, 0.6745068393906527, 0.6291983814305998,
                0.5855618581059508, 0.5421463661838041)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_death": (0.021912122879724705, 0.00021147866348074503, (
                9.249718042422586e-05, 0.00011351045314700465, 0.00013906100659879408,
                0.0001699801962602467, 0.0002067291918918717)),
            "pols_surr": (0.15886041521357985, 0.001214015835320285, (
                0.001214015835320285, 0.001134425715889475, 0.0010581674510826507,
                0.00098471258786002, 0.0009116197244003331)),
            "pols_maturity": (0.5410280172675118, 0.5410280172675118, (
                0.0, 0.0, 0.0, 0.0, 0.5410280172675118)),
        },
    },
    24: {"rows": 624, "months": (0, 155, 311, 467, 623),
        "result_cf": {
            "pols_if": (91.95079018351181, 0.6336664272907219, (
                0.6336664272907219, 0.255648365055038, 0.05778766270402682,
                0.0016027749458801008, 3.625294576735273e-08)),
            "asset_share": (172748584.91998482, 853080.58288399, (
                46760.54478803456, 95654.09982820188, 197732.94968756658, 410239.6701781786,
                853080.58288399)),
            "premiums": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "claims_death": (32818.122737446276, 110.53392118951682, (
                24.32962497834793, 64.1106162381628, 100.79634403569351, 21.407258490503043,
                0.0022963149171459202)),
            "claims_surrender": (33787.46948354499, 124.99852895853245, (
                118.63751279830822, 104.03256825865974, 48.31209983265328,
                2.7141356238835836, 0.00012221462670911797)),
            "claims_maturity": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "withdrawals": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "expenses": (306.97222546050006, 1.5841660682268046, (
                1.5841660682268046, 0.911233599204117, 0.3024863319399836,
                0.012320464807074572, 4.0924348089930086e-07)),
            "shareholder_transfers": (5087.534210533127, 48.13839653897991, (
                4.184521240420621, 33.7728641542107, 18.766071152464868, 2.4477103025925677,
                0.003078653470465503)),
            "smoothing_cost": (232.44088288797477, 8.946799489834458, (
                -8.946799489834458, 0.6347585766154694, 0.9979836043137978,
                0.21195305436141584, -0.028508154562619903)),
            "net_cf": (-72000.09865698489, 202.82728225023735, (
                -148.7358250853036, -202.82728225023735, -168.17700135275163,
                -26.58142488178627, -0.005497592257801441)),
        },
        "result_pols": {
            "pols_if": (91.95079018351181, 0.6336664272907219, (
                0.6336664272907219, 0.255648365055038, 0.05778766270402682,
                0.0016027749458801008, 3.625294576735273e-08)),
            "pols_new_biz": (0.0, 0.0, (
                0.0, 0.0, 0.0, 0.0, 0.0)),
            "pols_death": (0.24250130724427826, 0.0007302774405201529, (
                0.0005483126202295124, 0.0006635978779325946, 0.0005047128492700325,
                5.166566516333223e-05, 2.665139931096325e-09)),
            "pols_surr": (0.3911650866018999, 0.0027004505829178447, (
                0.0027004505829178447, 0.001087591315432437, 0.0002443300416495589,
                6.6159755410898185e-06, 1.4326269893044545e-10)),
            "pols_maturity": (3.3444543137325954e-08, 3.3444543137325954e-08, (
                0.0, 0.0, 0.0, 0.0, 3.3444543137325954e-08)),
        },
    },
}
# END generated fingerprint: WP_UK_SEC
