"""The S models' caps on annual mortality and morbidity, sent a NaN and taken past 1.

UKLIB-SEC-PLAN.md §9 item 6 puts the bound of every cap on an annual mortality or
morbidity rate of uklib's seven ``_S`` models second, ``min(q, 1.0)``, as
USLIB-SEC-PLAN.md §5.1 step 6 writes it for the ``_SEC`` models and its §8.2 item 4 did
for uslib's: death, critical illness diagnosis and claim, and income protection
inception.  ``min`` keeps its first argument unless a later one compares smaller, and no
comparison with NaN holds, so with its bound first a cap reads a NaN, a missing factor,
as 1, certain death or a certain claim with every flow finite; and bounded by the int
``1`` it returns an int where the product passes it.  The same item caps the rates S
left uncapped, none of which reaches 1 on a shipped point: ``IP_UK_S``'s active and sick
mortality and its inception rate, and ``CI_UK_S``'s diagnosis rate ``ci_rate``, each
life's claim rate ``claim_rate_life`` and the standalone paid rate ``claim_rate_paid``.
Past 1 the monthly rate ``1 - (1 - q)^(1/12)`` of an uncapped rate is complex in modelx,
and ``CI_UK_S``'s joint decrement ``1 - (1 - q_1)(1 - q_2)`` falls below 1 where both
lives' rates pass it.  No shipped point sends a cap a NaN, and where a shipped product
reaches 1, in ``WOL_UK_S`` and ``PA_UK_S``, either order gives the float 1.0, so the
products' own test modules cannot see how a cap is written, nor whether an added one is
there.

So each case reads its model fresh and, before the model computes anything, feeds the
product a NaN and then a value that takes it past 1, and every rate it reads, annual and
monthly, must be the float NaN, then the float 1.0.  A case feeds a Reference on
``Projection``, a factor, a loading or a rating, or a column of a copy of an input
table, written to ``tmp_path`` and read through the ``Data`` filename Reference:
``PA_UK_S``'s ratings are model point columns, and ``IP_UK_S``'s sick mortality is the
termination table's rate with no factor at all.  So that a factor left outside a cap
fails the test, :data:`BACKGROUND` moves off 1 the factors that the shipped References
hold at 1, ``Term_UK_S``'s selective-lapse loading, ``CI_UK_S``'s trend and review
selection and ``WOL_UK_S``'s improvement, and every factor of a product is fed by its
case or differs from 1 at one of its reads.  So that a cap on one branch of a product
fails the test, the reads take each branch: ``Term_UK_S``'s applied and select bases, in
the select period and after it, and its joint lives; ``CI_UK_S``'s single and joint
lives, its accelerated and standalone contracts and its reviewable point after a review;
``IP_UK_S``'s active lives and its lives in claim; ``WOL_UK_S``'s O50 and UW cells; and
``PA_UK_S``'s dependant and its annuitant past the limiting age, where no table is read.
:data:`PREMISES` holds the reads to those branches and factors, so that a change to a
shipped point or Reference that would leave a cap unseen fails here.

A NaN in a table rate does not always reach a cap: ``IP_UK_S`` floors its interpolated
inception rate at 0 before the economic-cycle factor, ``max(0.0, r)``, which reads a NaN
as 0, so its case feeds the factor.  Floors, and the lapse, surrender and recovery
bounds, keep S's order, as uslib's fix kept them: where a value can equal its bound as an
int, or be -0.0 against 0.0, the order is visible.  ``CI_UK_S``'s ``claim_rate`` caps, on
the single life and on the joint decrement, cannot bind once each life's rate is capped,
so only their order is held here: a NaN reaches them.
"""
import csv
import math

import modelx as mx
import pytest

from uk_registry import model_path, projection

#: S model -> the References set on ``Projection`` when the model is read, before any
#: feed, so that the factors the shipped References hold at 1 differ from 1 at the reads.
BACKGROUND = {
    # The selective-lapse loading 1 + lambda max(0, w_cum - w_ref): a reference ratio
    # below 0 applies it from the frame's first month, 1.25 at t = 0.
    "Term_UK_S": {"sel_lapse_lambda": 0.25, "sel_lapse_ref": -1.0},
    # The trend (1 + tau)^(y - 1), 1.01^5 at t = 60, and the review selection, 1.10 on
    # the reviewable point once a review has raised its premium past the 5% threshold.
    "CI_UK_S": {"ci_trend": 0.01, "review_prem_shock": 0.10},
    # The improvement (1 - f)^(y - 1), 0.99 from the first anniversary.
    "WOL_UK_S": {"mort_improvement": 0.01},
}

#: Term's reads: point 1 on the applied basis, point 6 joint, and point 7 on the select
#: basis in its select period (t = 0) and after it (t = 72).
_TERM_APPLIED = (
    (1, "mort_rate_life", (0, 1)), (1, "mort_rate", (0,)), (1, "mort_rate_mth", (0,)),
    (6, "mort_rate_life", (0, 1)), (6, "mort_rate_life", (0, 2)),
    (6, "mort_rate", (0,)), (6, "mort_rate_mth", (0,)))
_TERM_SELECT = tuple(
    (7, cell, args) for t in (0, 72)
    for cell, args in (("mort_rate_life", (t, 1)), ("mort_rate", (t,)),
                       ("mort_rate_mth", (t,))))

#: CI's reads, at t = 60: the claim rates of point 1 (accelerated), point 2 (standalone,
#: whose paid rate is its own), point 3 (reviewable, after its first review) and point 7
#: (joint).  ``_CI_CLAIM`` is what the mortality term reaches; ``_CI_DIAGNOSIS`` adds the
#: diagnosis rate, which the trend reaches as well.
_CI_PAID = (("claim_rate_paid", (60,)), ("claim_rate_paid_mth", (60,)))
_CI_JOINT = (("claim_rate_life", (60, 1)), ("claim_rate_life", (60, 2)),
             ("claim_rate", (60,)), ("claim_rate_mth", (60,)))
_CI_SINGLE = (("claim_rate_life", (60, 1)), ("claim_rate", (60,)),
              ("claim_rate_mth", (60,)))
_CI_CLAIM = tuple(
    (point, cell, args) for point, reads in (
        (1, _CI_SINGLE + _CI_PAID), (2, _CI_SINGLE), (3, _CI_SINGLE + _CI_PAID),
        (7, _CI_JOINT + _CI_PAID))
    for cell, args in reads)
_CI_DIAGNOSIS = (
    (1, "ci_rate", (60, 1)), (2, "ci_rate", (60, 1)), (3, "ci_rate", (60, 1)),
    (7, "ci_rate", (60, 1)), (7, "ci_rate", (60, 2))) + _CI_CLAIM

#: PA's reads at t = 0, on point 8, single and rated 1.35, and point 2, joint; and past
#: the limiting age, where ``mort_rate_base`` is 1.0 and reads no table: point 2's
#: annuitant at t = 600, age 115, inside the frame its younger dependant extends.
_PA_ANNUITANT = ((8, "mort_rate", (0, 1)), (8, "mort_rate_mth", (0, 1)),
                 (2, "mort_rate", (0, 1)), (2, "mort_rate_mth", (0, 1)))
_PA_DEPENDANT = ((2, "mort_rate", (0, 2)), (2, "mort_rate_mth", (0, 2)))
_PA_PAST_OMEGA = ((2, "mort_rate", (600, 1)), (2, "mort_rate_mth", (600, 1)))

#: Each case: the S model; what it feeds, a ``Projection`` Reference by name or
#: ``(Data filename Reference, column)``; the value that takes the product past 1; and
#: the reads, ``(point, cell, arguments)``, each of which the feed reaches and caps.
CASES = [
    ("Term_UK_S", "sel_lapse_lambda", 1e6, _TERM_APPLIED + _TERM_SELECT),
    ("Term_UK_S", "mort_scale", 1e6, _TERM_SELECT),
    ("CI_UK_S", "ci_trend", 1e6, _CI_DIAGNOSIS),
    ("CI_UK_S", "sel_lapse_ci_loading", 1e6,
     tuple(r for r in _CI_DIAGNOSIS if r[0] == 3)),
    ("CI_UK_S", "overlap_k", -1e6, _CI_CLAIM),
    ("CI_UK_S", "survival_slip", -1e6,
     tuple((2, cell, args) for cell, args in _CI_PAID)),
    ("IP_UK_S", "mort_active_factor", 1e6,
     ((1, "mort_rate", (0,)), (1, "mort_rate_mth", (0,)))),
    ("IP_UK_S", "cycle_factor", 1e6,
     ((1, "inception_rate", (0,)), (1, "inception_rate_mth", (0,)))),
    ("IP_UK_S", ("termination_file", "mort_rate_sick"), 2.0,
     tuple((2, cell, (z,)) for z in (1, 61)
           for cell in ("mort_rate_sick", "mort_rate_sick_mth"))),
    ("WOL_UK_S", "mort_loading_o50", 1e6,
     ((1, "mort_rate", (12,)), (1, "mort_rate_mth", (12,)))),
    ("WOL_UK_S", "mort_loading_uw", 1e6,
     ((5, "mort_rate", (12,)), (5, "mort_rate_mth", (12,)))),
    ("WOL_UK_S", "mort_improvement", -1e6,
     ((1, "mort_rate", (12,)), (1, "mort_rate_mth", (12,)),
      (5, "mort_rate", (12,)), (5, "mort_rate_mth", (12,)))),
    ("ULB_UK_S", "mort_be_factor", 1e6,
     ((1, "mort_rate", (0,)), (1, "mort_rate_mth", (0,)))),
    ("WP_UK_S", "mort_be_factor", 1e6,
     ((1, "mort_rate", (0,)), (1, "mort_rate_mth", (0,)))),
    ("PA_UK_S", "annuitant_adj", 1e6, _PA_ANNUITANT + _PA_DEPENDANT),
    ("PA_UK_S", "improve_rate_base", -1e6, _PA_ANNUITANT + _PA_DEPENDANT),
    ("PA_UK_S", ("model_point_file", "rating_multiplier"), 1e6,
     _PA_ANNUITANT + _PA_PAST_OMEGA),
    ("PA_UK_S", ("model_point_file", "dependant_rating"), 1e6, _PA_DEPENDANT),
]

#: S model -> what its reads rely on, each ``(point, cell, arguments, value)``: the
#: branch a read takes, or, where ``value`` is ``None``, a factor that a case reading it
#: does not feed and that must differ from 1 there.
PREMISES = {
    "Term_UK_S": (
        (1, "mort_basis", (), "applied"), (6, "is_joint", (), True),
        (7, "mort_basis", (), "select"), (7, "select_factor", (0,), None),
        (7, "select_factor", (72,), 1.0), (1, "sel_lapse_factor", (0,), None),
        (6, "sel_lapse_factor", (0,), None), (7, "sel_lapse_factor", (0,), None),
        (7, "sel_lapse_factor", (72,), None)),
    "CI_UK_S": (
        (1, "contract_type", (), "accelerated"), (1, "is_joint", (), False),
        (2, "contract_type", (), "standalone"),
        (3, "contract_type", (), "accelerated"),
        (3, "premium_guarantee", (), "reviewable"), (7, "is_joint", (), True),
        (7, "contract_type", (), "accelerated"), (3, "ci_trend_factor", (60,), None),
        (3, "ci_sel_factor", (60,), None)),
    "IP_UK_S": ((1, "status", (), "active"), (2, "status", (), "in_claim")),
    "WOL_UK_S": (
        (1, "cell", (), "O50"), (5, "cell", (), "UW"), (1, "mort_loading", (), None),
        (1, "mort_improve_factor", (12,), None),
        (5, "mort_improve_factor", (12,), None)),
    "PA_UK_S": (
        (8, "mort_basis", (), "table"), (8, "is_joint", (), False),
        (2, "mort_basis", (), "table"), (2, "is_joint", (), True),
        (8, "rating_factor", (1,), None), (8, "improve_factor", (0, 1), None),
        (2, "improve_factor", (0, 1), None), (2, "improve_factor", (0, 2), None),
        (2, "age", (600, 1), 115), (2, "proj_len", (), 636)),
}


def _feed_id(feed):
    return feed if isinstance(feed, str) else ".".join(feed)


def _read(name):
    """``name`` read for the test, with its :data:`BACKGROUND` set, nothing computed."""
    model = mx.read_model(model_path(name), name=f"{name}_cap")
    try:
        for ref, value in BACKGROUND.get(name, {}).items():
            setattr(model.Projection, ref, value)
    except BaseException:
        model.close()
        raise
    return model


def _copy_with_column(src, dst, column, value):
    """Copy the CSV ``src`` to ``dst`` with every row's ``column`` set to ``value``.

    A NaN is written blank, as a missing input is, and pandas reads it back as NaN.  The
    other cells are copied as text, so every other value is read as the shipped file's.
    """
    with open(src, newline="") as f:
        rows = list(csv.reader(f))
    col = rows[0].index(column)
    for row in rows[1:]:
        row[col] = "" if math.isnan(value) else repr(value)
    with open(dst, "w", newline="") as f:
        csv.writer(f, lineterminator="\n").writerows(rows)


def _rates(tmp_path, name, feed, value, reads):
    """The rates ``reads`` names, on ``name`` read fresh with ``feed`` set to ``value``.

    A Reference is set on ``Projection``; a column is set in a copy of its table, which
    the ``Data`` filename Reference then names by its absolute path, so the shipped file
    is never written.  Either is set before the model computes anything.
    """
    model = _read(name)
    try:
        if isinstance(feed, str):
            setattr(model.Projection, feed, value)
        else:
            file_ref, column = feed
            shipped = getattr(model.Data, file_ref)
            copy = tmp_path / shipped
            _copy_with_column(model_path(name).parent / shipped, copy, column, value)
            setattr(model.Data, file_ref, str(copy))
        return [getattr(projection(model, point), cell)(*args)
                for point, cell, args in reads]
    finally:
        model.close()


CASE_IDS = [f"{name}-{_feed_id(feed)}" for name, feed, _, _ in CASES]


@pytest.mark.parametrize("name, feed, past_1, reads", CASES, ids=CASE_IDS)
def test_a_nan_that_reaches_the_cap_stays_nan(tmp_path, name, feed, past_1, reads):
    """With a NaN fed to the product, each rate is the float NaN, not the cap's 1.0."""
    rates = _rates(tmp_path, name, feed, float("nan"), reads)
    assert [type(r) is float and math.isnan(r) for r in rates] == [True] * len(rates), (
        list(zip(reads, rates)))


@pytest.mark.parametrize("name, feed, past_1, reads", CASES, ids=CASE_IDS)
def test_a_product_past_1_is_capped_at_the_float_1(tmp_path, name, feed, past_1, reads):
    """With the product taken past 1, each rate is the float 1.0, and not the int 1."""
    rates = _rates(tmp_path, name, feed, past_1, reads)
    assert [(type(r), r) for r in rates] == [(float, 1.0)] * len(rates), (
        list(zip(reads, rates)))


@pytest.mark.parametrize("name", sorted(PREMISES))
def test_the_reads_take_each_branch_with_every_unfed_factor_off_1(name):
    """Each premise of the reads holds on the model as :data:`BACKGROUND` sets it."""
    model = _read(name)
    try:
        for point, cell, args, value in PREMISES[name]:
            got = getattr(projection(model, point), cell)(*args)
            if value is None:
                assert got != 1.0, (point, cell, args, got)
            else:
                assert got == value, (point, cell, args, got)
    finally:
        model.close()
