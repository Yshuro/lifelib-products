"""The model registry, and the locator that resolves it against this library.

Models are located relative to **this library directory**, so the suite runs from a clean
clone with no installation step, and keeps running from a copy made by
``lifelib.create()`` — where it tests *that copy's* models, which is the whole point of
shipping the tests inside the library.

That is why the path here is relative and not :data:`lifelib._dirs.TEMPLATES`: the
canonical locator resolves to the *installed* library, so a copy would silently test
lifelib's pristine models instead of the user's edited ones, and pass while proving
nothing.

:data:`MODELS` is the registry ``test_model_conventions_uk.py`` is parametrized over, so
registering a model here subjects it to the whole house style: it then either conforms or
fails.  The metadata records the projection basis — every model in this library runs on a
monthly grid, the frequency these products are written in — and records that none of them
discount.  :data:`ANNUAL` is kept alongside :data:`MONTHLY` because the grid is a property
of the model rather than of the library, and a later annual-step model would register with
it.  ``discounted: False`` is a property of the library, not an omission: every
``technical-notes.md`` specifies *gross liability cash flows* and leaves discounting and
reserves to a separate layer that consumes them.

**The SEC keys.**  UKLIB-SEC-PLAN.md puts a ``_SEC`` model beside each ``_S`` one, as
USLIB-SEC-PLAN.md did for uslib, and the metadata keys that describe one are uslib's, with
the meanings ``us_registry`` gives them (UKLIB-SEC-PLAN.md U5).  ``"twin"`` names the S
model an SEC model is derived from; its presence is what makes an entry SEC
(:func:`is_sec`).  ``"stage"`` is ``"E"`` while an SEC model runs in force at ``t = 0`` but
does not yet compile, and ``"EC"`` once it does; the name does not change with it.
``"param"`` names the ``Projection`` parameter: ``"point_id"``, the default, or ``"idx"``,
the position of a model point in the ``Data`` vectors, which a compiled model takes as
``basiclife/BasicTerm_SC`` does.  ``"closing_pols_if"`` marks ``PA_UK_SEC`` alone, whose
``pols_if`` is a closing count, as ``SPIA_US_SEC``'s is, not the count that weights row
``t`` (UKLIB-SEC-PLAN.md §6.7).  At stage ``"EC"``, ``"reporting"`` names the model's label
accessors, the S cells that return a model point's text, which no other cell calls and
which stay Python when the model compiles; ``"reporting_columns"`` says what a label
returns where that is not its point's column of the label's own name; ``"python_calls"``
maps a ``Projection`` cell to the Python builtins its formula may still call; and
``"engine"`` names S's cells kept for a reader and for the twin identity that no compiled
cell calls.  ``us_registry``'s docstring gives each in full.  Read them through
:func:`meta`, which hands out a copy.

**Why :func:`point_keys` exists.**  An ``idx``-parameterized ``Projection`` is indexed by
position, not by table label.  The tables number their points from 1, so a test that
indexes such a model by label is off by one -- ``Projection[1]`` is the second point, and the
first is never projected -- and then fails at the last label, which lies past the end of
every vector, far from the line that caused it.  So no test indexes ``Projection`` by hand:
:func:`point_keys` gives the keys in table order, for whichever parameter the model takes,
and :func:`projection` turns a key into its ItemSpace.

**Why this is not in `conftest.py`.**  Two libraries now ship in-library suites, and
``conftest.py`` is a name pytest fixes.  Collecting both in one run puts two files called
``conftest`` on ``sys.path``, one wins ``sys.modules``, and every ``from conftest import
LIB`` in *either* suite silently resolves to the other library — a green run against the
wrong models, or the ``FileNotFoundError`` that revealed it.  The registry therefore lives
under a library-unique module name and ``conftest.py`` re-exports it for its fixtures.
"""
import operator
import pathlib

LIB = pathlib.Path(__file__).resolve().parents[1]

ANNUAL = {"grid": "annual", "discounted": False}
MONTHLY = {"grid": "monthly", "discounted": False}

# The age basis is a property of the product, not of the grid: most of the library rates
# on age nearest birthday, but whole of life prices on "age last birthday" for both cells,
# the unit-linked bond's mortality charge is quoted ALB, and the pension annuity's
# generational table is entered ALB.  It is recorded per model rather than folded into the
# grid constants, where a single value would be false for three of the seven.
ANB, ALB = "ANB", "ALB"

# name -> (path relative to the library root, metadata)
#
# The name is <market short name>_<country>_<grid>: the name the product is actually known
# by (CI, IP, WOL, ULB, WP, PA — the same short names the taxonomy table in the library's
# index uses), then UK, then _A for an annual step or _S for a monthly one.  The grid
# letters follow lifelib, where annuallife/TradLife_A is the annual-step model and
# basiclife/BasicTerm_S and savings/CashValue_SE are the monthly ones.  Every model here
# carries _S: the whole library is on a monthly grid.
#
# This pairing is not derivable from the folder slug — "unit_linked_bond" spelled out is
# unusable in a model name — so it lives here, and test_model_conventions_uk.py asserts
# name, folder and the model's own _name all agree.
#
# An SEC model takes its twin's name with "EC" after the grid letter, and lives in its
# twin's product directory (UKLIB-SEC-PLAN.md U1): E for running in force at t = 0, as
# basiclife/BasicTerm_SE does, C for compiling, as basiclife/BasicTerm_SC does.  The name is
# the family's from the model's first commit, at stage "E" as at "EC", so it never moves
# when the stage does.  Its entry is the twin's metadata plus the SEC keys:
#
#     "Term_UK_SEC": ("products/term_assurance/Term_UK_SEC",
#                     {**MONTHLY, "age_basis": ANB, "twin": "Term_UK_S", "stage": "E"}),
#
# with "param": "idx" and the "reporting" label accessors added at stage "EC", and there
# "python_calls" where a cell keeps a Python builtin and "engine" where it keeps S's cells
# a compiled cell does not call; "closing_pols_if": True on PA_UK_SEC alone.  Each is
# entered directly after its twin, with its INPUT_FILES set below.
MODELS = {
    # Protection
    "Term_UK_S": ("products/term_assurance/Term_UK_S", {**MONTHLY, "age_basis": ANB}),
    "CI_UK_S": ("products/critical_illness/CI_UK_S", {**MONTHLY, "age_basis": ANB}),
    "IP_UK_S": ("products/income_protection/IP_UK_S", {**MONTHLY, "age_basis": ANB}),
    "WOL_UK_S": ("products/whole_of_life/WOL_UK_S", {**MONTHLY, "age_basis": ALB}),
    # Savings
    "ULB_UK_S": ("products/unit_linked_bond/ULB_UK_S", {**MONTHLY, "age_basis": ALB}),
    "WP_UK_S": ("products/with_profits/WP_UK_S", {**MONTHLY, "age_basis": ANB}),
    # Annuity
    "PA_UK_S": ("products/pension_annuity/PA_UK_S", {**MONTHLY, "age_basis": ALB}),
}


# name -> the exact set of input files a full sweep of the shipped model point table reads.
#
# Each product module used to assert its own model's read *count* — ``PA_UK_S`` expects 2,
# ``IP_UK_S`` 5 — inside a copy of the read-once check that built its own instance and
# re-projected every model point to get it.  The counts are kept here as sets instead, and
# ``test_model_conventions_uk.py`` asserts them once against the sweep it already runs.
#
# The set, and not merely "whatever was read was read once", is the assertion: counting only
# the files that happen to be read makes the check self-fulfilling, since a file that stops
# being read drops out of the counter and the check then passes over less coverage rather
# than failing.
INPUT_FILES = {
    "CI_UK_S": {"ci_rate_table.csv", "lapse_table.csv", "model_point_table.csv"},
    "IP_UK_S": {
        "inception_table.csv", "lapse_table.csv", "model_point_table.csv",
        "mort_table.csv", "termination_table.csv"},
    "PA_UK_S": {"model_point_table.csv", "mort_table.csv"},
    "Term_UK_S": {
        "lapse_table.csv", "model_point_table.csv", "mort_table.csv",
        "select_factor_table.csv"},
    "ULB_UK_S": {"model_point_table.csv", "mort_table.csv", "surr_table.csv"},
    "WOL_UK_S": {"lapse_table.csv", "model_point_table.csv", "mort_table.csv"},
    "WP_UK_S": {"lapse_table.csv", "model_point_table.csv", "mort_table.csv"},
}


def model_path(name):
    """Absolute path to a model folder, from its entry in :data:`MODELS`."""
    return LIB / MODELS[name][0]


def meta(name):
    """The metadata registered for ``name``, as a dict of its own.

    A copy, so that a test that sets a key on it sets it for no other entry, and no other
    test.  Keys an entry does not carry are absent rather than defaulted, so a caller states
    its default where it reads one: ``meta(n).get("param", "point_id")``.
    """
    return dict(MODELS[name][1])


def is_sec(name):
    """Whether ``name`` is SEC, i.e. registered with the ``"twin"`` it is derived from."""
    return "twin" in MODELS[name][1]


def _parameter(model):
    """The name of the ``Projection`` parameter, which must be one the helpers here know."""
    parameters = tuple(model.Projection.parameters or ())
    if parameters in (("point_id",), ("idx",)):
        return parameters[0]
    raise ValueError(
        f"{model.name}: Projection is parameterized by {parameters!r}; the registry "
        "helpers know ('point_id',), the table label, and ('idx',), its position")


def point_keys(model):
    """The key of each model point's ``Projection`` ItemSpace, in table order.

    The table labels when ``Projection`` is parameterized by ``point_id``; the positions
    ``0 .. n-1`` when it is parameterized by ``idx``, where position ``i`` is row ``i`` of
    ``model.Data.model_point_table()`` -- the row the ``Data`` vectors hold at ``i``.  Any
    other parameter raises ``ValueError``: a key of an unknown kind is exactly the error
    this helper exists to prevent, so it is not guessed at.
    """
    table = model.Data.model_point_table()
    if _parameter(model) == "idx":
        return list(range(len(table)))
    return list(table.index)


def projection(model, key):
    """The ``Projection`` ItemSpace for ``key``, one of :func:`point_keys`.

    modelx builds an ItemSpace for any argument at all, so a key the table does not have --
    position 0 on a ``point_id`` model, the last label on an ``idx`` one, a label of the
    wrong type -- would otherwise surface later, as whatever error the first lookup inside
    the projection raises.  It raises ``KeyError`` here instead.  What it cannot catch is a
    valid key of the wrong kind, such as label 1 on an ``idx`` model, which is also
    position 1; that is why the keys come from :func:`point_keys` and not from the table.
    A position is passed on as a Python ``int``, whatever integer type it arrived as.
    """
    table = model.Data.model_point_table()
    if _parameter(model) == "idx":
        try:
            position = operator.index(key)
        except TypeError:
            position = None
        if position is None or not 0 <= position < len(table):
            raise KeyError(
                f"{model.name}: {key!r} is not a position 0 .. {len(table) - 1}; an idx "
                "Projection is indexed by position, as point_keys() gives")
        return model.Projection[position]
    if key not in table.index:
        raise KeyError(f"{model.name}: no model point labelled {key!r}")
    return model.Projection[key]
