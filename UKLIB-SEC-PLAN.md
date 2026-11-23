# Plan — `*_UK_SEC`: uklib models that run in force, then compile

**Status:** Accepted, 2026-11-22, with §9's eleven decisions confirmed as recommended;
drafted the same day. Phase 0 (M0) is done, 2026-11-22, its gate met by the Tests
workflow's run 43 (§3, *Record — M0*), and so is Term's in-force step, M1, by run 45
(§6.1, *Record — M1*). Term's compile step, M2, is done too, 2026-11-23, by run 46 (§6.1,
*Record — M2*), critical illness's in-force step, M3, by run 47 (§6.2, *Record — M3*), and
the unit-linked bond's, M9, by run 48 (§6.6, *Record — M9*). Work pauses there; their
compile steps, M4 and M10, are next in their streams (§7). Like USLIB-SEC-PLAN.md, this
document is both the specification and the record: each milestone records what it actually
did, including where the implementation departed from the plan.

Every number in it was measured in this repository, under modelx 0.33.0 and pandas 3.0.5
as USLIB-SEC-PLAN.md's were, or is quoted from USLIB-SEC-PLAN.md, and each is given with
the experiment that produced it.

**Goal.** For each of the seven uklib products, add a model `<Name>_UK_SEC`, derived from
its `<Name>_UK_S`, with the two enhancements USLIB-SEC-PLAN.md made to uslib's twelve, done
in sequence:

1. **E — in force at time 0.** Besides new-business model points, the model projects model
   points already in force at the valuation date `t = 0`, as lifelib's
   `basiclife/BasicTerm_SE` extends `basiclife/BasicTerm_S`.
2. **C — compilable.** The model's exported pure-Python form compiles under modelx-cython
   into C-typed code, as `basiclife/BasicTerm_SC` is derived from `basiclife/BasicTerm_S`:
   `Projection` indexed by `idx`, inputs as numpy vectors read by element, and projection
   logic in C scalars and C arrays.

The `_S` models are not touched, but for the S-side fixes §9 asks about. They remain the
reference: their worked-example goldens pin the SEC models through the twin identity (T1).

---

## 0. How this plan relates to USLIB-SEC-PLAN.md

uslib finished the same two steps on 2026-11-15 (USLIB-SEC-PLAN.md §6.4, Tests run 33).
Its plan is the precedent, and this one **adopts it by reference** rather than restating
it. Everything it settled binds here, in its final form, unless this plan says otherwise:

- its findings F1–F8, decisions D1–D13 and the rules R1–R17 of D11;
- the Phase 1 recipe (§5.1), Term's template (§7.1, *Record — M1*, *Carried into M2 and
  after*, with *Precised at M3*), and the list M14 carried into Phase 1 (§7.1, *Record —
  M14*, *Carried into Phase 1*);
- the Phase 2 recipe (§6.1) and Term's Phase 2 template (§7.1, *Record — M14*, *The Phase 2
  template*);
- the tests T1–T6 (§5.2) and C1–C6 (§6.2), with every precision its records made, those
  of its M13 and M26 among them.

Where USLIB-SEC-PLAN.md names a uslib artefact, read its uklib counterpart:

| uslib | uklib |
|---|---|
| `<Name>_US_S`, `<Name>_US_SEC` | `<Name>_UK_S`, `<Name>_UK_SEC` |
| `tests/us_registry.py` | `tests/uk_registry.py` |
| `tests/sec_support.py` | `tests/uk_sec_support.py` (U3) |
| `tests/test_sec_support.py` | `tests/test_sec_support_uk.py` |
| `tests/test_model_conventions.py` | `tests/test_model_conventions_uk.py` |
| `tests/test_compiled_conventions.py` | `tests/test_compiled_conventions_uk.py` |
| `tests/test_cython_toolchain.py` | `tests/test_cython_toolchain_uk.py` |
| `tests/test_<product>_us_sec.py` | `tests/test_<product>_uk_sec.py` |
| `USLIB_SEC_FULL`, `USLIB_REQUIRE_CYTHON`, `USLIB_CYTHON_SHARD`, `USLIB_REQUIRE_DOCUTILS` | `UKLIB_SEC_FULL`, `UKLIB_REQUIRE_CYTHON`, `UKLIB_CYTHON_SHARD`, `UKLIB_REQUIRE_DOCUTILS` |
| uslib's `index.md`, `README.md` lines | uklib's `index.md`, the README's uklib lines |

The tools stay one set for both libraries (U4): `tools/gen_sec_points.py`,
`gen_sec_fingerprint.py`, `build_sec_cy.py` and `bench_sec_cy.py` learn the library from
the model's country tag.

A milestone this plan names bare, M0 to M15, is uklib's (§7). One of uslib's is always
named as uslib's, as in "uslib's M14".

**What this plan adds** is what uslib's could not know: the shared files uklib needs
(§3), seven per-product notes (§6), the order (§7), and what is new in uklib's products
(§1): a three-state model whose opening state is a vector of claim cohorts, a with-profits
fund that declares once a year, a unit fund whose frame ends where the fund runs out, and
a pension annuity whose escalation ratchets.

**Why adopt the final form from the start.** uslib found its rules while it built its
products, and took each later precision back into the products already landed: its M13
took the precisions of T2–T5 into eleven products before freezing them, and its M26 added
four compiled-model conventions over all twelve. uklib builds each product to the settled form
once, so it needs no retrofit milestone.

---

## 1. Findings that shape this plan

Each product note in §6 comes from a read of its S model, notes and tests; a run of every
shipped point with every check, the caches harvested; cold depths from modelx's stack
trace; and, for Term, WP, WOL, ULB and IP, S points restated in force at chosen months and
compared with S from there. The scratch prototypes were not kept; the measurements are
quoted where they are used.

**G1 — Three time axes, as uslib found (F1).** `Term_UK_S` and `WP_UK_S` open an in-force
frame late, on an anniversary only, `proj_start() = 12 * duration_inforce()`, as
`WholeLife_US_S` and `FIA_US_S` do. `CI_UK_S`, `WOL_UK_S`, `ULB_UK_S` and `PA_UK_S`
project new business only. `IP_UK_S` represents in force only as in claim, and restarts the
policy clock at the valuation date on such a row. So E re-clocks two products, adds
running in force to four, and for IP adds a healthy policy in force, which S cannot
express at all.

**G2 — Where S has in-force rows, they are incomplete.** Each was reopened at its own
state and compared with S from issue:
- `Term_UK_S` restarts four states at its frame's start: the selective-lapse ratio, the
  family income benefit's ledger, the waiver of premium's deferral pipeline and the RPI
  index factors. Indexed premiums come out 4.3 to 36 % low, the uncommuted family income
  benefit 92 to 99 % low.
- `WP_UK_S` restarts two cumulants, the guarantee-charge cumulant and the smoothing
  account. A bond reopened at year 5 keeps charging where S from issue has stopped, its
  asset share up to 49 % off.
- `ULB_UK_S`'s `uf_init` moves the fund and nothing else.
- `IP_UK_S`'s in-claim rows reproduce month 0, but every row's policy clock restarts.

With the states §6 lists carried in, every prototype reproduced S from the restated month:
WP on 62 rows to 3e-12 relative, WOL on 237 to 1.4e-13, ULB on 533 to 6.4e-12, IP in 28
splices to 7.7e-13.

**G3 — Opening states of shapes uslib has not met.**
- A vector whose length the point decides: IP's claim cohorts, up to 624.
- A vector whose length a Reference decides: Term's waiver pipeline, 7 as shipped.
- A second count strand: WOL's paid-up policies and their cover.
- History the contract has already given: RPI increases (Term, CI, WOL, IP, PA) and
  premium reviews (CI). S recomputes these from flat References, and the splice cannot see
  them missing, since S recomputes them the same way.

**G4 — Long chains.** Count chains run three cells a month in Term, CI, WP and ULB. WP's
asset share runs seven: `asset_share(779)` is 5,042 cells deep cold on point 1. ULB's fund
runs four, about 5,400 deep at the longest cover. D5's one-cell-a-month form takes the
counts, and `MYGA_US_SEC.av_pp`'s inline month the balances (F7).

**G5 — Every uklib S model caps with the bound first,** `min(1.0, q)`, which reads a NaN as
certain death, the form uslib's §8.2 item 4 moved its S models off. Some rates are not
capped at all: IP's active and sick mortality, CI's standalone paid rate, and CI's
`ci_rate × trend × sel`. At a factor of 100, IP point 6's counts go complex and both of its
checks still pass.

**G6 — The harness and tools are uslib's, and uklib's tests assume S alone.**
- `sec_support.py` imports `us_registry`.
- `gen_sec_points.py` and `gen_sec_fingerprint.py` hold uslib's tests path, and
  `build_sec_cy.py` and `bench_sec_cy.py` its products path.
- The conventions read `USLIB_*` variables.
- `fix_doc_roles.py` still takes one model folder per product, an item uslib's M1 carried
  and left undone.
- `test_model_conventions_uk.py` is a copy of uslib's from before its M0. It asserts the
  `_S` suffix, the `point_id` parameter, and that every CSV is read by the model beside it.
- Each uklib product module pins the exact set of CSVs beside its model, where uslib's
  check a subset, so an SEC table beside the model fails it.
- uklib has no `CHECK_EXEMPTIONS`: every check holds on every point.

**G7 — No uklib input file names a company or product.** All seven products' CSVs were
searched, case-insensitively, for every publisher, product and document code their
`sources.md` cites. One key does name a product, though: WP's out-of-scope chassis value
`SF_prufund`. It appears in `WP_UK_S`'s refusal message and the technical notes' `chassis`
enum, and `test_with_profits_uk.py` writes it into a temporary model point table beside
the model.

**G8 — The S suites are light.** uklib's S suite ran 560 tests, 9 skipped, in 71 s on the
shared machine (2026-11-22, beside six analysis processes). uslib's twelve SEC modules ran
114 to 912 s each by default at its M13. So each uklib SEC module's cost is its own, and
U6's budget applies to it.

**G9 — S's own defects, met on the way.** Each is refused in the SEC model's `Data` or
`proj_len()` (D6), and S is left as it is (§9, item 6):
- `Data` validates almost nothing: a blank or out-of-range rate, an unknown text code or a
  blank flag projects.
- No model enforces its product's bounds on ages and terms.
- PA reads a blank bool column as True and a negative death month as a life that never
  dies.
- IP's `premium_basis` check has no caller.
- ULB's single-life guard is never called.
- ULB's exhaustion test can be defeated by a rounding residual (§6.6).

---

## 2. Decisions

Each departs from, or adds to, USLIB-SEC-PLAN.md's decision of the same subject.

### U1 — Name, place, derivation (D1, unchanged)

`<Name>_UK_SEC` lives in `products/<product>/` beside `<Name>_UK_S`. Its first commit is
the S folder copied without `__pycache__`, with `_name` changed and nothing else. It reads
the S model's assumption CSVs in place, and its own `model_point_table_sec.csv` and any
`*_sec.csv` companion, every row generated (D8). `tools/gen_scaffolding.py` already pairs
`<Name>_S` with `<Name>_SEC` in any library and refuses an SEC folder without its
`model-sec.md` (uslib M0), so the doc pages need no tool change.

### U2 — Sequence: E then C, product by product (changes D2)

uslib gated every product's C on all twelve E steps and a freeze of all twelve (uslib's
M13), because its rules for C were still being found: Term's C step (uslib's M14) was
brought forward to test them while the other products were written. Those rules are now
settled, and the *Carried into Phase 1* list of uslib's M14 is what a Phase 1 model obeys
so that its C step restructures nothing. So here each product runs its own two steps back to back:

1. **E.** The S copy (commit 1), then the enhancement at `stage: "E"` (commit 2), with its
   test module, `model-sec.md`, `run_sec.py` and generated inputs.
2. **Freeze.** The Phase 1 fingerprint (§5.4's form), written by
   `tools/gen_sec_fingerprint.py` into the module's empty block, committed alone.
3. **C.** The representation change at `stage: "EC"`, `sample_sec.py`, `spec_sec.py`, the
   compile tests, the product's shard in the `cython_uk` job (U7), and C6 in
   `model-sec.md`.

A product lands each step as uslib's did: rebased onto the branch as it stands, the full
uklib suite, doccheck, `gen_sec_points.py --check` and `gen_sec_fingerprint.py --check`
for every registered uklib SEC model run on the rebased tree before it is pushed, and the
CI legs the step adds dispatched green (§7). Term goes first, through both steps, as the
template (§7).

*Why:* the same two reviewable diffs per product, "what running in force needs" and "how
it is made C", with the C step reviewed while its product's E step is fresh, and each
product finished before the next stream's head starts.

*Rejected:* uslib's phase-wide gate. Its purpose, finding the C rules on a real model
before ten products were written against them, is served.

### U3 — The harness is a copy, under a library-unique name

`sec_support.py` is bound to uslib (G6), and lifelib copies one library at a time, so uklib
needs the harness inside its own `tests/`. It gets `uk_sec_support.py`:

- uslib's harness, as it stands at the commit Phase 0 copies, without uslib's product
  specs (lines 1,073–3,103 of 5,381: the `_wl_*`, `_spia_*` … `_iul_*` extractors and its
  `SEC_SPECS`), with three mechanical substitutions, `us_registry` → `uk_registry`,
  `USLIB_` → `UKLIB_` and `_us_sec` → `_uk_sec` (the shard regex and its messages), its
  module docstring's opening paragraph rewritten, and uklib's own `SEC_SPECS` and
  extractors in their place. Outside the product specs, nothing else in the harness's code
  names uslib; its docstrings keep uslib's examples, which are the harness's own record.
- `test_sec_support_uk.py`: uslib's harness tests, re-pointed from `Term_US_S` to
  `Term_UK_S` where they read a real model.
- A repository check, `tools/check_sec_harness.py`, outside the libraries since it reads
  both: it parses the two files, undoes the three substitutions, and fails on any function,
  class or constant the two share whose source differs, listing it. It runs as a step of
  CI's `test` job. A deliberate divergence is listed in the tool with its reason.

*Why a copy:* the name must be the library's own. `conftest.py` taught this already
(MERGE.md §9): with both suites in one process, two modules named `sec_support` collide in
`sys.modules`, and the second library's tests would import the first's harness and its
registry. A module both libraries imported would also have to ship in both, which is a copy
again.

*Why the check:* uslib's harness has changed in at least 14 commits since its M13, most of them
a product's step adding a check every later product meets. A fix to one copy that never
reaches the other would be found by nothing, since each library's suite passes on its
own copy.

*Rejected:* refactoring `sec_support.py` into a registry-agnostic core and per-library
specs. It changes a finished, green module that twelve test modules import, to save a copy
that still has to exist.

### U4 — One set of tools for both libraries

`gen_sec_points.py` and `gen_sec_fingerprint.py` find the library from the model's
country tag, `_US_` or `_UK_`, and import that library's harness and registry: one path
constant each becomes a lookup. `build_sec_cy.py` already takes a product directory; its
command line's bare-name lookup, today `uslib/products/<name>`, accepts `<lib>/<product>`
and a bare name that only one library with SEC models holds (`term_life` is in uslib,
jplib and krlib). `bench_sec_cy.py` takes the same lookup. Each tool's uslib behaviour is
unchanged, and its existing tests and checks still pass.

### U5 — Registry and conventions

`uk_registry.py` gains uslib's `meta`, `is_sec`, `point_keys` and `projection` and the
same SEC keys: `twin`, `stage`, `param`, `reporting`, `reporting_columns`, `python_calls`
and `engine`. Of the count-semantics keys, `closing_pols_if` marks `PA_UK_SEC`, whose
`pols_if` is SPIA's closing measure (§6.7), and the registry test confines it there, as
uslib's confines it to `SPIA_US_SEC`; no other uklib product needs one (D5 holds on IP's
healthy-plus-sick count and on WOL's premium-paying count).
`test_model_conventions_uk.py` takes uslib's M0 generalization and its SEC section, with
`CHECK_EXEMPTIONS` and `EXTRA_POINT_ASSERTIONS` keyed by model name and empty until a
product needs one. `test_compiled_conventions_uk.py` takes uslib's compiled conventions,
the four of uslib's M26 included. uklib's conventions suite is a copy of uslib's from
before uslib's M0 that has diverged in wording (G6), so the port is by section, keeping
uklib's own text where only its wording differs.

### U6 — Tests: uslib's settled forms, a core by default

Every product module holds T1–T6 and, at its C step, C1–C6 with the release, stack,
refusal and Reference tests, in the forms USLIB-SEC-PLAN.md's records settled (§5 below
lists them). Each module runs a **core** of its splice grid by default and the rest under
`sec_full`, which skips unless `UKLIB_SEC_FULL=1`, from its first commit; a test asserts
the core reaches every branch, opening-state column, kind of valuation month and side of
every `min` and `max` the full grid reaches, as uslib's later modules do. The default run
of a module is budgeted at five minutes on the shared machine, the budget uslib's K6
derived from WholeLife's module; a module past it records why, and what a cut would cost.

### U7 — CI: uslib's three jobs, and two more for uklib

- `test`: every library in one process, as upstream runs it, now leaving out
  `test_*_uk_sec.py` beside `test_*_us_sec.py`. uklib's SEC conventions, registry and
  harness tests stay in it, and the harness check (U3) runs as a step of it.
- `sec_uk`: a copy of `sec` over uklib's SEC modules, one to a leg, by default on Windows
  and macOS and over the full grid on Linux, at Python 3.13, the full-grid legs installing
  docutils and setting `UKLIB_REQUIRE_DOCUTILS=1`.
- `cython_uk`: a copy of `cython` over uklib's shards, `toolchain` and one per uklib model
  at stage `"EC"`, each leg setting `UKLIB_REQUIRE_CYTHON=1`, `UKLIB_CYTHON_SHARD` and, on
  Linux, `UKLIB_SEC_FULL=1`, and collecting `lifelib/libraries/uklib/tests` alone.
  `test_compiled_conventions_uk.py` holds this job's `shard` list to uklib's registry, as
  uslib's holds the `cython` job's to its own.

*Why two jobs:* uslib's shard test reads the job named `cython` and requires every shard
in it to be uslib's, and a job's legs take one set of variables. Copies leave uslib's jobs
and tests as they are. The 60- and 90-minute limits stay; K6 measures each step's legs
(§8).

*Rejected:* a library axis on the existing jobs, which would change uslib's shard test and
set both libraries' variables on every leg.

### U8 — Documentation

Each product gets `model-sec.md` (D9), with the H1 *In-Force Implementation Notes* and
Term's sections, and at its C step *The compiled model*. uklib's `index.md` gains the SEC
paragraph, a second model in each row of its models tables, and at the close a compiled
speed table in uslib's form. The convention table both libraries follow is uslib's, which
already has an `_SEC` column; uklib's SEC models follow it, and any convention they settle
otherwise is added there. `README.md`'s status and organization lines and `MERGE.md`'s
model-page note name uklib's SEC models beside uslib's.

---

## 3. Phase 0 — shared infrastructure (M0)

One milestone, before any model, in commits each reviewable on its own:

0. **S-side items**, if §9 items 6 and 9 are confirmed, each in a commit of its own and
   first, so that every SEC copy inherits them: the caps, `test_mortality_caps_uk.py`, the
   product modules' CSV-set tests in uslib's subset form, and WP's chassis key.
1. **Tools** (U4): the library lookup in the four SEC tools, uslib behaviour unchanged;
   `tools/check_sec_harness.py` (U3); `tools/fix_doc_roles.py` taking every model folder
   of a product, uslib M1's item left undone (G6).
2. **Registry** (U5): `uk_registry.py`'s helpers and SEC keys, no SEC model registered.
3. **Harness** (U3): `uk_sec_support.py`, with an empty `SEC_SPECS`, and
   `test_sec_support_uk.py`.
4. **Conventions** (U5): `test_model_conventions_uk.py` generalized, every S model passing
   unchanged and the SEC section inert until M1; `test_compiled_conventions_uk.py`, inert
   until M1's C step; `test_cython_toolchain_uk.py`, which compiles `Term_UK_S` and holds
   it to modelx, so that `cython_uk`'s `toolchain` shard has a test from the start.
5. **Configuration**: uklib's `conftest.py` registers `cython`, `sec_full` and
   `docutils`, its `sec_build` fixture, and the two hooks of uslib's, scoped to uklib's
   directory and reading `UKLIB_*`. `.gitignore` already covers every library's build
   output: `*_nomx/`, `*_nomx_cy/`, compiled modules, and a `setup.py` and `build/` in
   any `lifelib/libraries/*/products/*/`.
6. **CI** (U7): `test`'s second ignore and the harness check's step; `cython_uk` with its
   `toolchain` shard; `sec_uk`, whose module list is empty until M1 and so is added with
   M1's first module.

*Exit:* every S model of both libraries passes unchanged; uslib's suite, its SEC modules,
and `gen_sec_points.py --check` and `gen_sec_fingerprint.py --check` on all twelve uslib
models, are unchanged; the harness check passes; doccheck reports zero; a dispatched run
of the workflow is green, `cython_uk`'s `toolchain` legs on Linux and Windows among it.

### Record — M0, done 2026-11-22

Built as specified, in fifteen commits after the plan's own, `f56bd1e` to `4ce175f`, each
one item of the list above or part of one. Four components were built by agents, each in a
worktree of its own: the caps and their test, the tools, the harness's tests with the
drift check, and the conventions with the configuration. The rest were written directly.
The builders injected faults into their own work.

A second agent then reviewed all fifteen commits against this plan and USLIB-SEC-PLAN.md.
It reran their checks and injected faults of its own, 16 of them. It found no wrong
number, and confirmed the caps' sweep, value for value.
- Five of its seven defects were in checks a later step could pass unseen:
  - the drift check took no notice of what the product specs bind;
  - nothing held the `sec_uk` job to the registry;
  - the `cython_uk` job test read only its shard list;
  - the caps test had lost uslib's coverage guard;
  - the conftest hooks had no test.
- Two were docstrings the code contradicts.
- It also noted, without demonstrating a fault, three registry guards that no test holds.

Six commits more, `9ba6f05` to `084e32f`, fix all eight. Each fix is shown by the fault it
now catches, and the new guards pass on M1's tree too.

**What exists now.**
- *The S-side items* (item 0):
  - The seven product modules' CSV-set tests ask for a subset of the CSVs beside the
    model, as uslib's do (`f56bd1e`).
  - WP's out-of-scope chassis is `SF_smoothed`, in `WP_UK_S`'s refusal, the technical
    notes' enum and the S test (`11597d5`).
  - Every cap on a mortality or morbidity rate puts its bound second, `min(q, 1.0)`
    (`5841933`). These are Term's rate per life, CI's claim rate on one life and on two,
    WOL's, ULB's and WP's mortality, and PA's rated rate.
  - The rates of those kinds S left uncapped are capped the same way. These are IP's
    active and sick mortality and its inception rate, after its floor at 0, and CI's
    diagnosis rate, each life's claim rate and the standalone paid rate. Each life's cap
    is what keeps CI's joint decrement, `1 − (1 − q1)(1 − q2)`, at most 1. Without it, a
    trend of 300% a year takes point 7's claim rate at `t = 60` to −0.54.
  - No shipped number moves. The sweep ran every shipped point of the seven through
    `result_cf()`, every other `result_*` and every `check_*`. Each of the 995,586 values
    the cells cache, and each of the 267 returns of those calls, is what it was, of the
    same type, bit for bit.
  - `test_mortality_caps_uk.py` (`bf2f27e`) is uslib's test on uklib's models: 41 tests in
    2 s. 77 faults were injected one at a time: each of the 13 caps removed, put bound
    first or bounded by the int 1, 26 with a factor left outside, and 12 on one branch
    only. It fails 73. The four it passes are CI's two `claim_rate` caps removed or bounded
    by the int 1. Once each life's rate is capped those two cannot bind, and none of the
    four moves a value.
- *`uk_registry.py`* (`c1cc34a`): uslib's SEC keys, `closing_pols_if` being `PA_UK_SEC`'s
  alone, and `meta`, `is_sec`, `point_keys` and `projection`. No SEC model is registered.
- *`uk_sec_support.py`* (`ae3da4f`), generated by script from uslib's `sec_support.py` as
  it stood:
  - its lines 1–1,072 and 3,104 to the end, leaving out uslib's product specs;
  - three spellings changed: `us_registry`, `USLIB_` and `_us_sec` became `uk_registry`,
    `UKLIB_` and `_uk_sec`;
  - the docstring's opening paragraph rewritten;
  - an empty `SEC_SPECS` between `# >>> product specs` and `# <<< product specs`.

  Term_UK_S compared with a second read of itself gives 0 twin mismatches over the eight
  points.
- *`test_sec_support_uk.py`* (`9dd9bd7`): uslib's harness tests, ported to Term_UK_S.
  - Every expectation of the model was re-derived by running it, such as the 11,721 values
    T1 compares on point 1, and the T6 table's 25 columns and ten rows.
  - Term_UK_S's point 8 is in force at 60 months, which neither of Term_US_S's points is,
    so three refusals that only an in-force S row reaches join the spec cases.
  - Dropped, since their product specs are uslib's: the tests of the `_vul_`, `_spia_` and
    `_dia_twin_args` maps, and the assertion on MYGA_US_SEC's engine cells.
  - 78 tests pass in about 26 s, and 156 with uslib's in one process, in either order. The
    port needed no change to the harness.
- *`tools/check_sec_harness.py`* (`50b5e07`), U3's check.
  - It parses both harnesses with `ast`, and sets aside each one's product specs between
    the markers.
  - It reads uklib's spellings as uslib's, and compares every other top-level statement as
    `ast.unparse` writes it, docstrings left out.
  - It reports a name only one file has, code that differs, and a uslib spelling left in
    uklib's code.
  - `DIVERGENCES` is empty, and a stale entry is an error.
  - On the tree it compares 144 statements, with 77 of uslib's and 1 of uklib's set aside.
    uslib's `sec_support.py` gains the two marker lines, comments only.
- *The tools* (`1cbd9e3`, `0ea0a2d`).
  - `tools/sec_libraries.py` maps a model's country tag, `_US_` or `_UK_`, to its
    library's tests, harness and registry. It refuses a name with neither tag or both.
  - `gen_sec_points.py` and `gen_sec_fingerprint.py` read it. For uslib nothing changes:
    both tools' `--check` exits 0 on all twelve uslib models, with the same output byte for
    byte.
  - `build_sec_cy.py` and `bench_sec_cy.py` also take `<lib>/<product>`. They take a bare
    product name only where exactly one library's product of that name holds an SEC model,
    so `term_life` stays uslib's.
  - `fix_doc_roles.py` takes every model folder of a product, in name order. It had taken
    the first in filesystem order, so it read 12 of uslib's 24 models and never the other
    twelve. Those need no fix.
- *`test_model_conventions_uk.py`* (`d7e0f16`): uslib's M0 generalization and its SEC
  section, inert until M1 registers Term_UK_SEC.
  - The module ran 166 passed and 9 skipped, and runs 166 passed and 17 skipped. The 8 new
    skips are the SEC section's, on an empty parameter set.
  - The section was exercised on a scratch stand-in: Term_UK_S copied as a crude
    Term_UK_SEC at stage E. It passed there, and each of 16 injected faults failed the test
    meant to catch it.
- *uklib's `conftest.py`* (`d861587`): the `cython`, `sec_full` and `docutils` markers, the
  `sec_build` fixture, and uslib's two hooks, reading `UKLIB_*`. The collection hook
  deselects, and counts for an empty shard, this directory's compile tests alone.
- *The compiled conventions* (`618ef03`).
  - `test_compiled_conventions_uk.py` holds C3–C5, the release, the sample's engine cells,
    the runner's block sum and the job test, over the SEC models at stage EC. It is inert
    until M2, and its job test reads `cython_uk`.
  - `test_cython_toolchain_uk.py` compiles Term_UK_S with `build_sec_cy.py`, its caches
    sized for the longest contract `product-spec.md` admits: `t` and `k` 602, `m` 482,
    `life` 3, `(t, life)` (602, 3). It holds every cache of C integers to those sizes, and
    `result_cf()` to modelx on all eight points, exactly with gcc 13.
- *uslib's `conftest.py`* (`4ce175f`): under `USLIB_REQUIRE_CYTHON=1`, the empty-shard
  check counts uslib's compile tests alone. It counted every library's, so collected
  beside uklib's suite, a uslib shard emptied of its own tests passed on uklib's toolchain
  test.
- *The review's fixes*, `9ba6f05` to `084e32f`:
  - *The product specs' rules* (`9ba6f05`). `check_sec_harness.py` now holds each file's
    region to what a product spec is:
    - its statements are definitions, assignments to plain names, and their documentation
      strings;
    - none binds a name that either file binds outside the region, or declares one
      `global`;
    - uklib's holds no uslib spelling.

    The reviewer showed what three lines in uklib's region did, and the check passed them:
    `from us_registry import MODELS, model_path`, a wider `TWIN_EXEMPT_DEFAULT`, and a
    `twin_mismatches` that returns `[]`. Under them T1 compared nothing. Those three lines
    now give six findings. uslib's region, 60 functions and 17 assignments, and uklib's
    keep to the rules unchanged.

    The check has its tests, in `test_check_sec_harness_uk.py`: 89 of them in about 1 s.
    The tool as it was at `4ce175f` fails 57 of them, and each of nine mutants of the new
    rules fails at least one.
  - *The job tests* (`2972026`), beside the shard test:
    - `sec_uk`'s module list must be the registered SEC models' product directories, each
      with its module, no `_uk_sec` module outside the list, and the full grid's two
      variables set. It skips while no model is registered. Each of 13 faults fails it, on
      a scratch copy with toy entries.
    - `cython_uk` must set `UKLIB_REQUIRE_CYTHON: '1'` and run `-m cython` over uklib's
      suite alone.
    - The `test` job must run the harness check.
  - *The caps test's guard* (`c3e3cd4`): every registered S model has a case or is named in
    `NO_CAP`, which is empty.
  - *The hooks' tests* (`b5ba368`), in `test_conftest_uk.py`. They copy the conftest beside
    probe modules and run pytest on it, four runs in about 3 s. The directory filter
    removed, or `REQUIRED` read for uslib's variables, fails them.
  - *Prose* (`dd5d3cd`):
    - IP's inception rate floors before it caps, `max(0.0, r)`, so a blank table rate
      reads as no claim, and only a NaN `cycle_factor` stays NaN.
    - CI's `ap_rate` takes `ci_rate`'s cap.
    - The harness's docstrings name `cython_uk`, `sec_uk` and uklib's modules where the
      substitution had made them name a uslib job or a file in neither library.
  - *The registry's tests* (`084e32f`): `projection`'s `KeyError`, `_parameter`'s refusal,
    and `meta`'s copy.
- *CI* (`f345f2c`).
  - The `test` job gains its second ignore, `*test_*_uk_sec.py`, and a step that runs the
    harness check.
  - `cython_uk` runs the `toolchain` shard on Ubuntu and Windows, Python 3.13, under
    `UKLIB_REQUIRE_CYTHON=1`, with `UKLIB_SEC_FULL=1` on Linux.

**Departures and precisions.**
- Two changes to uslib, which §3 did not list:
  - the marker lines in `sec_support.py`, which U3's check needs;
  - the conftest fix above. It changes no CI run, since CI collects each library's compile
    tests in a job of their own, and uslib's `toolchain` shard still collects 1 of 5,880.
- In `test_compiled_conventions_uk.py`, C3, C4 and the release check are marked `cython`
  only once a uklib model is at stage EC.
  - With none, pytest makes each of them one case, skipped for an empty parameter set.
  - Marked `cython`, that case falls to the `toolchain` shard, where
    `UKLIB_REQUIRE_CYTHON=1` fails the skip. A toolchain leg run here failed so, three
    errors.
  - uslib never had this module without a model at stage EC.
  - The job test skips while the workflow has no `cython_uk` job and no model is at EC,
    and fails a missing job from the first such model on.
- `test_cython_toolchain_uk.py` checks five parameter tuples, not just `t`. It parses the
  `.pxd` itself, because the harness's `pxd_declarations` misreads an integer default
  (*Carried*, below). Cells that return text (`sex`, `smoker`) are left out of its size
  check, since they keep dict caches.
- The conventions leave out uslib's `survival_pols_if`. It marks no uklib model, and set
  on an entry it would switch nothing off.
- Left as S has them, as §9 item 6 says: CI's `ap_rate` and `child_rate_mth`, which the
  model defines as frequencies rather than probabilities; IP's recovery bound; every lapse
  and surrender bound; and PA's `min(1.0, obligation)`, which bounds no rate.
- The agents' worktrees opened at the branch's base, `221b245`, not its head, and each was
  fast-forwarded before work began. Every brief now checks its base first.

**Measured for K6.**
- uklib's suite went from 560 passed and 9 skipped in 71 s to 681 passed and 27 skipped in
  139 s. That was on the shared 4-CPU Linux machine, with modelx-cython and gcc installed.
  - The 121 new passes are the 41 cap tests, the 78 harness tests, the toolchain compile
    (36 s) and the compiled conventions' job test.
  - The 18 new skips are on empty parameter sets: the 8 SEC conventions and 10 compiled
    conventions.
  - The review's fixes take it to 782 passed and 28 skipped in 165 s.
    - The 101 new passes are the check's 89 tests, two job tests, the caps guard, four
      hook tests and five registry tests.
    - The new skip is the `sec_uk` job test, which waits for M1.
- At `4ce175f`, the suite of all six libraries in one process, run here as the `test` job
  runs it, passed 6,863 with 78 skipped in 73 min 18 s. It differs from a CI leg in that the
  compile tests run here.
- In CI, Tests run 43 on `4ce175f` is compared with run 42 on `221b245`, `main` before M0.
  - The `test` job's Ubuntu leg on Python 3.14 went from 6,705 passed and 97 skipped in
    37 min 0 s to 6,825 passed and 116 skipped in 38 min 56 s. That is uklib's 121 new
    passes and 18 new skips, with the toolchain compile skipping in that job, which
    installs no compiler: 120 and 19.
  - The harness check's step takes under a second.
  - `cython_uk`'s `toolchain` legs passed: 1 passed, 707 deselected, in 12.4 s on Ubuntu
    with gcc and in 31.7 s on Windows with MSVC, each leg a minute or less.
  - Run 43's 76 jobs all passed, 1 h 31 min from dispatch to the last. That is the gate's
    dispatched run.
  - The review's six commits came after it. M1's dispatched run is their CI.

**Carried into M1 and after.**
- `sec_uk` comes with M1's first module (item 6).
- The harness's `pxd_declarations` reads an integer parameter's default, which the `.pxd`
  writes `long long life=*`, as a parameter named `life=*`.
  - It is moot while no SEC model gives an integer parameter a default.
  - Term_UK_S gives six cells `life=1`: `age_at_entry`, `sex`, `smoker`, `age`,
    `mort_rate_base` and `mort_rate_life`.
  - Term_UK_SEC drops those defaults at M1, every caller passing `life` positionally (R12),
    so the parser stays as uslib's.
- Term's waiver incidence, `wop_inc_rate_mth`, reads one Reference with no factor and no
  annual-rate cell, and S leaves it uncapped. IP's sick mortality, also without a factor,
  is capped, because §9 item 6 names it. Term_UK_SEC refuses the incidence Reference
  outside [0, 1], by name, rather than capping it (M1).
- The product specs' rules cannot see a call that changes a shared object in place, such as
  `MODELS.update(...)` in an assignment's value. The tool's docstring says so, and such
  code is reviewed as code is (K10).
- The `sec_uk` test does not read the job's docutils install step or its `exclude` list. A
  missing install still fails its legs, under `UKLIB_REQUIRE_DOCUTILS=1`, but a wrong
  `exclude` would pass.
- uslib's own `cython` job test has the blind spots uklib's had, and its conftest hooks have
  no tests. uslib's files are left as they are (U7).

---

## 4. Per product: the recipe

Each product follows USLIB-SEC-PLAN.md's recipes as its records settled them: Phase 1 by
§5.1, the 14 items of Term's template and *Precised at M3*, and the *Carried into Phase 1*
list of uslib's M14; Phase 2 by §6.1 and Term's Phase 2 template, its 13 items. The items that most
often cost a uslib product a fix stage, in uklib's terms:

- **The clocks.** `duration_mth(t) = duration_mth_init() + t`, never a recursion;
  `t_entry() = max(0, -duration_mth_init())`; `is_active(t)` from S's frame from issue,
  named for the event that ends cover; `proj_len()` that frame less
  `duration_mth_init()`, refusing a point outside cover by name.
- **No policy month as `t`** (R1a). Every test of `t` against a contractual event becomes
  a test of `duration_mth(t)` or `policy_year(t)`; every schedule read at a policy month
  passed as `t` becomes a `<cell>_py(y)` cell; acquisition and initial commission are
  charged on `pols_new_biz(t)`, never on `t == 0`.
- **One cell a month** for every chain, its base at `t_entry()` reading the opening state
  for a point in force and the issue values for new business; zeros before issue; a far
  read as a loop in one cell, never a backward recursion (R2).
- **Caps and refusals.** An annual decrement built as a product of factors is capped
  `min(q, 1.0)`, the bound second; `Data` refuses by name a blank, text or infinite value
  wherever a cap, a `min` or a `max` reads it, and a value outside its own range.
- **Valuation-clock inputs** (D7): expense inflation, and any rate path, on `t`; schedules,
  and improvement dated by the calendar from the contract's start, on the policy clock.
- **Compile-neutral writing** (uslib M14's list): no new string, tuple, list, Series or `None`
  return; numbers, bools and int codes for every switch; positional calls; no float
  parameter; `bool(...)` around every comparison that can meet a numpy scalar.

---

## 5. Tests

Each product's `tests/test_<product>_uk_sec.py` holds, in uslib's settled forms:

- **T1**, in the conventions suite: every new-business twin agrees with S in every cell S
  caches, at no absolute floor but on the roll-forward residuals; an S cell the SEC model
  lacks fails unless its spec exempts it with a reason. At stage `"EC"` through `codes` and
  the spec's `twin_arg_map`.
- **T2**: every S new-business point restated at months that straddle the product's events
  (§6), and S's own in-force rows, reproduce S from the restated month, every result
  column and state cell, to 1e-9 relative at no absolute floor but on residuals; every
  assumption that ships at zero switched on; variants for every branch the shipped points
  leave unreached, each a change of S's columns, never of a formula.
- **T3**: future new business issued up to the horizon reproduces the S frame shifted, zero
  before issue, one row issued more than 12 months on.
- **T4**: the count algebra; the count multiplied by 2.5 with every zero-shipped assumption
  on, every counted cell scaled to 1e-12 relative and every per-policy cell unmoved.
- **T5**: each malformed table refused by name, table-driven, through a projection too;
  each window rule refused just inside both ends and read just outside; each tolerance
  pinned from both sides; the every-state test, which restates every state S reaches and
  requires it read, at the windows' edges by default and every month under
  `UKLIB_SEC_FULL=1`.
- **T6**: the committed table and companions equal what `gen_sec_points.py` generates.
- The product's own facts, the rules test (R1, R1a, R2, D3 on the splice grid), the cold
  depth bound on a fresh read at the longest cover, the cap and NaN tests, the runner's
  block, and the committed derived and future rows compared with S frame by frame.
- **C2**: the fingerprint, frozen at U2's step 2 and reproduced to 1e-12 relative.
- At the C step: **C1** unchanged in substance; **C3–C5** through the compiled
  conventions; C4 on the splice grid in chunks of 20 rows and at the contract's extremes;
  the compiled refusals on a relabelled table; the 1 MiB stack and the main thread at the
  longest cover; a Reference set late changes nothing cached; the compiled runner and its
  refusal leg; **C6** by `bench_sec_cy.py`, recorded in `model-sec.md`.

---

## 6. Per-product notes

Each note follows USLIB-SEC-PLAN.md §7's form: what S does today, what E needs (the
opening state, the rebase of every policy month read as `t`, the inputs' clocks, counts and
caps, the splice months), and what C needs. **S**, **M** and **L** are small, medium and
large, as there; "never reached" lists cells no report or check evaluates, which
`sample_sec.py` must call.

| Model | S clock today | In force in S | E | C | The crux |
|---|---|---|---|---|---|
| Term | policy, late frame | anniversaries; four states lost | M | M | the waiver's deferral pipeline as a companion; about 20 frame-index tests |
| CI | policy | — | M | M | review and RPI history as opening state; the pivot interpolation as arrays; a three-kind total |
| IP | policy; in-claim rows restart it | in claim only | L | L | a vector of claim cohorts, as opening state and as a `[t, z]` cache 626 wide |
| WOL | policy | — | M | S | a second count strand, paid-up policies, opened mid-life |
| WP | policy, late frame | anniversaries; two cumulants lost | M | M | four coupled chains, one of seven cells a month; the exhaustion scan inside `proj_len()` |
| ULB | policy | the fund alone | S | S | an exhaustion test a rounding residual defeats; a fund chain of four cells a month |
| PA | policy | — | M | M | RPI-linked income and its ratchet as opening state; SPIA's chassis otherwise |

### 6.1 Term assurance — `Term_UK_SEC` (E: M, C: M)

*Today:* policy clock, `duration_mth(t) = t`, frame `0 .. term_mths() - 1`. In-force
support opens late, on an anniversary only: `proj_start() = 12 * duration_inforce()`, so
point 8, in force at year 5, projects months 60..299 (`test_term_assurance_uk.py`).
Points 1–7 are new business.

S's in-force opening is complete only for point 8's shape. Each new-business point,
restated in force through S's own `duration_inforce` at years 1, 3, 5 and 10 and compared
per policy with its own run from month 12y, gives: points 1, 2, 4 and 6 reproduce
`result_cf()` exactly, but `result_pols()`'s `fib_cum` restarts at 0; the uncommuted
family income benefit (point 3) pays `claims_fib` 92 to 99 % low; the indexed point 5
collects premiums 4.3 to 36 % low and pays deaths 2.9 to 26 % low; the waiver point 7's
premiums are off by 0.27 to 0.75 %; and with the selective-lapse loading on
(`sel_lapse_lambda = 0.25`) deaths on every point are off by 2.9 to 10 %. S's own test
pins one of the zeros, `lapse_cum(60) == 0`. Commission clawback and rebroking reopen
exactly.

*E — the opening state* (D6), beyond `policy_count` and `duration_mth`, which replace
`pols_if_init` and `duration_inforce`:
- `lapse_cum_init`: the cumulative lapse ratio that loads mortality under selective
  lapsation. S divides each month's lapses by the count at the frame's start, so the column
  is held as a ratio to the issued cohort, count-free, and T4's scaling still holds.
- `fib_cum_init`: the family income benefit's ledger per policy in force, which
  `result_pols()` publishes and `check_fib_ledger_resid` rebuilds; the rebuild starts from
  it.
- **The waiver pipeline.** `wop_waived_frac(t)` reads itself at `t - 1` and new waivers at
  `t - 1 - wop_defer_mths`, seven months back as shipped. Its opening state is the waived
  fraction and the incidence of the deferral months not yet waived: a vector whose length
  is a Reference. It goes in a companion, `wop_pipeline_sec.csv`, keyed `(point_id, lag)`,
  in IUL's ladder shape (D8, R7), each lag checked present where it is read. This is
  Term's crux.
- `idx_factor_init` and `idx_prem_factor_init`: RPI increases already given are history;
  the issue sum assured and premium stay on the point, and the factors count anniversaries
  from the valuation date. `comm_init_pp()` reads the issue premium, as S's new business
  does.

*E — rebase* (R1a): the frame, base and expiry tests on `proj_start()` and `proj_len()`
(`pols_if`, `pols_if_at`'s `AFT_DECR`, `pols_maturity`); the four recursion bases at
`proj_start()` (`lapse_cum`, `wop_waived_frac` twice, `fib_cum`); `duration(proj_start())`
in the index factors; `idx_prem_factor(0)` in `comm_init_pp`; annual premiums on
`t % 12 == 0`; `annuity_certain_factor(term_mths() - t)`; acquisition and initial
commission on `t == 0`, renewal commission on `t >= 12`, the clawback's `t + 1` months;
and the checks' `range(proj_start(), ...)`. About twenty sites; no `t - 12` look-back.
Before issue S raises (`select_factor`, `lapse_rate_base`, `mort_rate_base`) or is
silently wrong (`benefit_sched(k < 0)`, the inflation exponent): each is guarded by
`is_active(t)`.

*E — inputs, counts and caps.* Expense inflation, `(1 + i)^duration(t)` in S, moves onto
`t` as `(1 + i)^(t // 12)`; S inflates point 8 from issue, so its twin differs by design
and is a splice case at offset 60 with inflation at 0. `rpi_rate`, `premium_market_ratio`
and `fib_commute_disc_rate` are flat References. Counts keep S's `BEF_DECR`, `BEF_LAPSE`
and `AFT_DECR` and add `BEF_NB`; joint first death stays one policy decremented by
`1 - (1 - q1)(1 - q2)`; the waiver's paying count is `pols_if * (1 - u)`. S already
charges acquisition and initial commission per policy, so on `pols_new_biz(t)` T1 holds at
any count; renewal commission from `duration_mth >= 12`; the clawback applies to lapses in
the 48 months from issue. Mortality, base × select × scale × selective-lapse load, is
capped `min(1.0, q)` in S and `min(q, 1.0)` in SEC; no cap binds on the shipped inputs (the
largest `q` is 0.0085), so the cap test uses a variant table. The lapse bound keeps S's
order.

*Splice months:* 1, 6 and 7 (the first waiver entrants); 11, 12, 13 (anniversary, renewal
commission, annual premium, index step); 30 (the selective-lapse ratio crosses its
reference at λ = 0.25); 47 and 48 (the clawback window's end); 59 and 60 (select period
and the ultimate lapse rate); 66; 120; 239 (point 7's last); 299. Point 8 is an in-force
twin at offset 60. Variants: annual premiums; the family income benefit commuted at 50 %;
an indexed waiver point.

*C:*
- To arrays: `mort_table` (sex, smoker, ages 18..100) to `[sex × smoker, age]`, padded from
  age 0, a code per life; `select_factor_table` to `[duration]`, checked against
  `select_period`; `lapse_table` to `[policy_year]` with its last year as an int cell (S
  reads `tbl.index.max()` per call).
- Decoded: `shape`, `sex`, `smoker` and the joint columns, `premium_mode` to a cycle,
  `mort_basis`; the three flag columns to int64; a blank `joint_age` to a value and a flag.
- Codes: `BEF_NB = 0`, `BEF_DECR = 1`, `BEF_LAPSE = 2`, `AFT_DECR = 3`; `claims(t, kind)`
  to `DEATH`, `FIB` and `LAPSE` with an explicit total, left to right, which equals S's
  `sum` in all 2,280 committed months (at most two kinds non-zero together).
- Per-`t` pandas in three readers; one generator in `claims`, and one in
  `check_fib_ledger_resid`, a residual that compiles, which becomes a loop from `t_entry()`
  over the opening ledger; no `round`, no `math`, no float parameter, no uncached cell.
- Caches: `t` to 12 × 50 + 120 + 2 (the longest term, the horizon, the roll-forward's
  `t + 1`); `benefit_sched(k)` to 600; `annuity_certain_factor(m)` to 480 under the family
  income benefit's 40 years. S enforces none of the product's bounds (term at most 50 years,
  40 for the family income benefit; entry age 18 or more; expiry by the 90th birthday, 70th
  for the family income benefit): `proj_len()` refuses each through a lower-case Reference.
  The bound is not named `expiry_age`, which S's tests assert absent.
- Every cell is reached by a report or a check.

#### Record — M1, done 2026-11-22

Built in three commits, as U1 and §7 ask: `Term_UK_S` copied with only `_name` changed
(`50bdfb4`), the enhancement (`3f7a01d`), and the Phase 1 fingerprint frozen alone
(`f041c4c`).
- One agent built it, injecting 22 faults. Two directions followed its brief, from M0's
  record: refuse the waiver incidence out of range, and drop the `life=1` defaults.
- A second agent reviewed it against this note, the plan and USLIB-SEC-PLAN.md, injecting
  29 faults of its own. It found:
  - two defects in the numbers that no test could see: history recomputed from today's
    assumptions, and a waived share past 1 at rates the model accepted;
  - a pipeline measured at the wrong instant;
  - five lesser gaps.
- The builder reworked the enhancement, fixing all eight, and 11 faults more were caught.
- The reviewer verified the rework with 12 faults of its own. It found two more gaps, which
  `2a2c5a3` closes.

**What exists now.**
- *`Term_UK_SEC` at stage E.*
  - `Projection` keeps 68 of `Term_UK_S`'s 70 cells: 14 unchanged, 16 with a new docstring
    only, and 38 rewritten.
  - It drops `proj_start` and `duration_inforce`, which the valuation clock replaces.
  - It adds 15 cells:
    - `policy_count`, `duration_mth_init`, `t_entry`, `is_active` and `pols_new_biz`;
    - `cohort_frac`, the issued cohort's share in force, rebuilt from the opening ratios;
    - `fib_streams`, the family income benefit's streams in payment;
    - the opening state's eight cells.
  - Five lower-case References hold the contract's bounds, which `proj_len()` checks:
    `issue_age_min`, `policy_term_max`, `policy_term_max_fib`, `expiry_age_max` and
    `expiry_age_max_fib`.
- *The opening state* (D6). Each column is documented in `model-sec.md` with the instant
  it is measured at. Seven columns sit on the table:
  - `lapse_cum_init`, held as a ratio to the issued cohort, count-free, so that T4's
    scaling holds;
  - `fib_cum_init`, the deaths since issue per policy in force, which `cohort_frac` and
    the ledger read;
  - `fib_streams_init`, the streams in payment;
  - `idx_factor_init` and `idx_prem_factor_init`, the RPI increases already given;
  - `wop_waived_frac_init`;
  - `comm_init_pp_init`, the commission paid at issue.

  The companion `wop_pipeline_sec.csv` is keyed `(point_id, lag)`, in IUL's ladder shape.
  - For a waiver point in force `d` months, it holds lags 1 to `min(wop_defer_mths, d)`.
  - Each lag is the share of the policies still in its deferred period at the start of
    month 0, `inc·(1 − u)·(1 − rec)^(k − 1)`. Its entrants at `t = D + 1 − k` take
    `(1 − rec)^t`, `D` months of deferral in all.
  - `proj_len()` refuses a pipeline whose count or last lag is wrong, and `Data` checks
    the file against seven rules, naming the lines at fault.
- *`model_point_table_sec.csv`*, 14 rows generated from Term's `SecSpec`.
  - S's eight points are twins, point 8 in force at 60 months.
  - Five rows are derived: the indexed point on its fifth anniversary; the family income
    benefit mid-year, its streams in payment; the waiver point after its select period,
    with six lags in the pipeline; the waiver point inside its deferred period, with four
    and none waived; and S point 1 in its last covered month.
  - One row is future, S point 7 issued at `t = 13`.
  - The pipeline holds ten rows.
  - A case-insensitive search for every publisher, product and form code that
    `term_assurance/sources.md` cites finds none in either file.
- *`tests/test_term_assurance_uk_sec.py`*, in uslib's settled forms: T2 on a core and a
  full splice grid, T3, T4 at 2.5, T5, T6, the rules test, the cold-depth bound, the caps,
  the runner and the committed rows. The product's own facts include a K14 test for each
  history column. 237 tests pass and 119 skip by default; 356 pass on the full grid.
- *The rest:*
  - `run_sec.py`, for one point or `--block`;
  - `model-sec.md`;
  - the registry entry, directly after `Term_UK_S`, with its `INPUT_FILES`;
  - the generated pages;
  - uklib's `index.md`, with the SEC paragraph and Term's row;
  - the `sec_uk` job over `[term_assurance]`. M0's job test now holds it to the registry
    instead of skipping.

**Departures and precisions.**
- *History beyond the plan's list* (§9 item 5, K14). The review found two more facts of
  the contract that S rebuilds from today's References.
  - **The streams in payment.** S pays `(1 − c) I (D + FIBcum)`, every death since issue
    at today's take-up. A take-up of 0.5 set at the valuation date on point 10 paid 49.6%
    low at `t = 0` and 21.9% low over the frame, and `check_fib_ledger` passed.
  - **The commission paid at issue,** which the clawback recovers.

  Both are now columns, each with a K14 test whose column departs from what the References
  give. `Data` also refuses streams off the family income benefit's shape, or beyond the
  deaths since issue, two states S cannot reach.
- *The pipeline is measured at the valuation instant* (D6), a precision of this note's
  "the incidence".
  - Measured at incidence, it re-ran the elapsed part of each deferred period at today's
    recovery rate: a rate changed at the valuation date moved point 11's waived share by
    up to 1.12%.
  - Measured at the instant, it matches the truth. It equals S to 2.5e-16 on 15 restated
    rows, at deferred periods of 6, 3, 1 and 0.
  - IP's claim cohorts take this form (§6.3).
- *The waived share stays in [0, 1].* S's recursion, kept, passes 1 from an incidence of
  about 0.8552 a year with the shipped recovery and deferral. At 0.86 the share is 1.012
  and the monthly premium −0.47, and both checks pass.
  - `wop_waived_frac(t)` raises in the month the share leaves [0, 1], naming the point,
    the month, the share and the three References. That is FIA's form for a computed value
    out of range.
  - `proj_len()` cannot see the share without running the recursion, which reads the
    pipeline, which asks `proj_len()` first.
  - 0.855 projects, its twin equal to S, and 0.856 is refused at month 19.
- *S's over-count, kept in both models.* S's incidence base, `1 − u(t − 6)`, includes the
  lives already in their deferred period, whom its technical notes' own account of an
  entrant counts once.
  - On point 7 and its rows, entrants run up to 0.184% high and the waived share up to
    0.182% (1.38e-5). Premiums are £0.07 (0.0011%) low over the frame.
  - It is a defect of the specification rather than of S, which reproduces its notes'
    formula bit for bit.
  - As with `SPIA_US_S`'s refund trim, it is fixed in neither model, so that T1 and T2
    hold on the waiver cells without exemptions (*Carried*).
- *The waiver's References.* The incidence and the recovery rate are each refused outside
  [0, 1] by name, NaN included. Past 1, S's monthly rate is complex. A recovery rate of
  exactly 1, under which nobody survives the deferral, is accepted.
  - The recovery rate goes beyond M0's carried item: it has the same form and the same
    defect, and below 0 the waived share grows without bound.
  - A non-zero opening waived share on a point in force no longer than its deferred period
    is refused in `proj_len()`, since `wop_defer_mths` is a `Projection` Reference that
    `Data` cannot read.
- *The `life=1` defaults are dropped* (M0's carried item, discharged). Every caller passes
  `life` positionally (R12). modelx keys S's calls by their bound arguments, `(t, 1)`, so
  T1 pairs them: zero mismatches over 1,140 keys on three points.
- *The contract's bounds are refused at stage E,* though this note lists them under C,
  since T5 asks for them.
- *The runner is uslib Term's as it stands*, `--cython` and `--build` included, with its
  `create()`-copy test, as M14's carried list asks. At E, `--cython` stops with
  `build_sec_cy.py`'s message that the model has no `sample_sec.py`.
- *T1 compares `check_fib_ledger_resid` at a floor of 1e-9* (`TWIN_FLOORS`). SEC sums the
  streams month by month, where S scales the deaths' sum.
  - At the shipped take-ups, 0 and 1, and at 0.5, they are the same floats.
  - At 0.3, which no committed point holds, T1 found 50 mismatches without the floor, each
    a rounding about zero (S's 0.0 against SEC's −2.8e-17), and none with it.
- *The cold-depth test also runs the family income benefit's point* at its own longest
  cover, 40 years from issue at 30. Written two cells a month, its streams chain had passed
  every test while running 965 deep. Now 495 are allowed there, and the test fails it.

**Measured for K6.** On the shared 4-CPU Linux machine:
- the default module takes 90 s and the full grid 145 s, against U6's five minutes, each
  near 900 MiB at its peak;
- uklib's suite, 1,056 passed and 135 skipped, takes 4 min 0 s. At M0's close it was 782
  and 28 in 165 s.

Cold, at the contract's longest cover:
- `net_cf` runs 11 cells beyond the waiver point's 599-month chain.
- On the family income benefit's 479-month chain, `fib_streams` runs 8 beyond,
  `claims(·, "FIB")` 10 and `net_cf` 11.
- All are inside Term's 16, and shallower than the level point's 610.

In CI, Tests run 45 on `2a2c5a3` ran the `sec_uk` job's first three legs, each in four
minutes or less:
- the full grid on Ubuntu, 356 passed in 3 min 1 s;
- the core on Windows, 236 passed and 120 skipped in 1 min 58 s;
- the core on macOS.

The core legs skip one more test than here: the module's docstring parse test, which needs
docutils, and only the full-grid leg installs it.

Run 45 passed all 79 jobs, 1 h 15 min from dispatch to the last. It is also the first CI
run of M0's six review commits.

**Faults.** Each fault was injected into a copy of its own, and each run was held to the
test meant to catch it.
- The builder: 22, then 11 on the rework, all caught.
- The review: 29, of which 26 were caught. The three misses were the pipeline check
  skipped with no rows, `last != lags` dropped, and `life` dropped from the runner's
  joint-life line. The rework added a test for each.
- The verification: 12. Ten were caught, and one only by T1, in the ledger residual's last
  bit. The one missed, the two-cell streams chain, is caught since `2a2c5a3`.

**Carried into M2 and after.**
- *M2, this note's C list.*
  - The model's data:
    - arrays for the three tables, and `[idx, lag]` for the pipeline;
    - decodes for the shape, sex, smoker, the joint columns, `premium_mode`, `mort_basis`,
      the flags, and a blank `joint_age`.
  - Codes, loops and keys:
    - codes `BEF_NB` to `AFT_DECR`, and `DEATH`, `FIB` and `LAPSE` with an explicit
      claims total;
    - loops in place of the generators in `claims` and `check_fib_ledger_resid`;
    - `param: "idx"`, with `point_id()` in the refusals;
    - a T1 `arg_map` for S's `claims(t, None)` keys.
  - The compile:
    - `reporting` and `reporting_columns`, where `sex` and `smoker` take `life`;
    - the spec's sizes: `t` 722, `benefit_sched` 600, `annuity_certain_factor` 480, and
      `life`;
    - `sample_sec.py`, `spec_sec.py`, the compile tests, the `cython_uk` shard and C6.
  - Two rules of uslib's *Carried into Phase 1* are met only at C, as this note's C list
    has them: branching on numbers, while S's text comparisons stay at E; and R7's "no
    string-keyed join in a per-`t` cell", where `mort_rate_base` and the other two table
    readers stand.
- *The template, for every later product.*
  - History as opening state reaches beyond RPI and reviews. A stream already in payment
    and a commission paid at issue are facts of the contract too. Each such column gets a
    K14 test whose column departs from what the References give.
  - A pipeline or cohort companion is measured at the valuation instant.
  - A computed value S lets leave its range is refused in its cell, naming the References.
  - The cold-depth test runs every chain at its own shape's longest cover.
- *The owner's decision.* Whether to fix `Term_UK_S`'s incidence base.
  - The fix would take it to `1 − u − P`, with `P` the share in its deferred period, which
    `wop_deferred_init` already serves.
  - It changes `technical-notes.md`'s formula and the worked example's goldens, and
    `Term_UK_SEC` with them.
  - It is outside this plan, and left as S has it.

#### Record — M2, done 2026-11-23

Built in two commits after the Phase 1 fingerprint, which M1 froze (`f041c4c`): the C step
(`8fef0a2`) and its docs with C6 (`6b48830`). Three more followed from the review. The
gate was met on Linux here at landing, and on Windows by the Tests workflow's run 46.
- One agent built it, injecting 10 faults, one for each kind the C step guards against.
- A second agent reviewed it against this note, the plan and USLIB-SEC-PLAN.md, injecting
  24 faults of its own, of which 20 were caught. It confirmed that no number had moved,
  163,873 values on the committed points and 1,997,675 on the full splice grid, and it
  found six gaps in what the tests hold:
  - the ledger residual's compensated sum, held by nothing;
  - the commutation discount, read with no domain, outside which the two engines differ;
  - a decode test that could not tell truncation from rounding;
  - `age_at_entry(2)` on a single life, untested;
  - the zero discount's branch, run nowhere;
  - `joint_age`'s `2**53` bound, tested far from the bound.

  It also found four lesser gaps: directives held present but not alone, the documented
  `idx` edges untested, a docs wording with some unwrapped lines, and C6's noise.
- The builder fixed all ten in `d262ca9` and `c9a2e7c`. Sweeping every power and
  division, it found five cells more whose powers overflow, and 9 faults more were
  caught.
- The reviewer verified the rework with 10 faults of its own. It found two more gaps,
  which `06a6a46` closes:
  - the zero discount's departure pinned only where `1 + r` is exactly 1;
  - a refusal printing a Reference as each engine holds it: an int `wop_inc_rate` of 2
    read "not 2" in modelx and "not 2.0" compiled.

  The builder found one more case there: modelx refused a `select_period` of 3.0, which
  numpy cannot take as an index, and now reads it as 3.

**What exists now.**
- *`Term_UK_SEC` at stage EC*, compiled under modelx-cython and checked against modelx.
  - `Projection` has 90 cells, keyed by `idx`: stage E's 83, and `point_id`, the decoded
    `is_level`, `is_decreasing`, `is_fib`, `is_select_basis`, `prem_cycle` and
    `mort_group`.
  - 82 compile to `bint`, `long long` or `double`. The eight that stay Python are
    `model_point`, the five label accessors and the two reports.
  - Codes: timings `BEF_NB` 0, `BEF_DECR` 1, `BEF_LAPSE` 2 and `AFT_DECR` 3; kinds
    `DEATH` 0, `FIB` 1 and `LAPSE` 2, and `ALL` 3, the total, which S spelt `claims(t)`.
  - `Data` has 45 cells: the six readers, and 39 int64 or float64 vectors, arrays,
    extents and counts, which its docstring tables.
    - The mortality table is `[group, age]`, padded with NaN from age 0.
    - The select factors and lapse rates are by duration and by policy year.
    - The pipeline is `[idx, lag]`.
  - A compiled `Projection` ItemSpace is 512,248 bytes.
- *Beside the model:*
  - `sample_sec.py`, which runs the reports and checks on every committed point, the
    labels on a blank second life, and sets a recursion limit of 5,000;
  - `spec_sec.py`: `t` 722, the 2-D caches 722 × 4, `life` 4, `k` 600 and `m` 481, each
    derived in its comment from the contract's References, and held there by a test;
  - `run_sec.py --cython` and `--build`;
  - in `model-sec.md`, *The compiled model*, in seven subsections.
- *Tests.* Term's module gains a representation section and a compiled section.
  - The representation section holds the total and the ledger residual to S by
    `float.hex`, every decode on every value, the NaN padding, the vectors' dtypes, and
    the spec's and sample's comments.
  - The compiled section holds C4 on the splice grid, at the contract's longest covers,
    where the cap binds, on float keys and at a commutation discount of 0 and of 1e−17.
    It also holds the labels, the refusals and overflows message for message, the `idx`
    edges, the 1 MiB stack, a Reference set late and the runner.
  - 291 pass and 119 skip by default, 410 pass on the full grid, and the `term_assurance`
    shard runs 13 compile tests.
- *Shared files, added to in place:*
  - `uk_sec_support.py`'s product specs, which gain Term's `twin_arg_map`, S's
    `claims(t, None)` to `ALL`;
  - `uk_registry.py`, with Term at `EC` with `idx`, its `"reporting"` labels and their
    `"reporting_columns"`;
  - `test_compiled_conventions_uk.py`, whose C3, C4 and release tests are now marked
    `cython` outright, M0's `_compile_test` having waited for this model, and which pins
    the build's directives;
  - the `cython_uk` job's `term_assurance` shard;
  - uklib's `index.md`.

**Departures and precisions.**
- *The claims total is written left to right,* `0.0 + DEATH + FIB + LAPSE`, not as a
  compensated sum.
  - The lapse kind is 0.0 in every month, by its formula, so at most two terms are ever
    non-zero, and the plain sum is `sum`'s float.
  - A test holds it to S by `float.hex`. CI's total, with three kinds, is a compensated sum
    (§6.2).
- *The ledger residual is a compensated loop,* Neumaier's, as Python's `sum` is since
  3.12. A test holds it to S by `float.hex` in every month, at the shipped take-ups and at
  0.5. T1's 1e−9 floor stays for take-ups such as 0.3, where M1 found the two models' sums
  round apart.
- *The shape is three flags, not one code.* A shape code named `FIB` would collide with
  the claims kind.
- *`sex(life)` and `smoker(life)` return each life's column as read,* NaN for a single
  life's second, where S refuses an invalid life. They compile to Python objects, as
  `SPIA_US_SEC`'s and `DIA_US_SEC`'s do, since `label_faults` needs every point to return
  its column.
- *`m` is 481, not this note's 480.* `m` reaches 480 in the family income benefit's issue
  month.
- *The 1-D `life` caches are widened to 4,* the shared inner width, so that a life of 0
  or 3 is refused by the formula in both engines.
- *`joint_first_death` serves as `joint_age`'s flag;* a blank second age decodes to 0.
- *New refusals, in both engines, message for message.*
  - `Data` refuses an issue age, a term or a joint age of `2**53` or more, which int64
    would hold inexactly without a word. Each is tested at exactly `2**53`.
  - `select_factor` checks its duration on both sides, since a negative `select_period`
    would wrap the index.
  - On a family income benefit point, `proj_len()` refuses a `fib_commute_disc_rate`
    that is not a finite number above −1.
    - At −1, S raises `ZeroDivisionError` and the compiled model gave an infinity, with
      `net_cf` NaN in every month.
    - Below −1, S's power is complex and the compiled model's NaN.
- *The zero discount is tested on the monthly rate,* as `benefit_sched` tests
  `sched_rate_mth()`. A rate whose monthly equivalent rounds to 0 gives `m` in both
  engines, where S divides by zero. It is a departure from S, in the departures table.
  T5 and C4 hold it at 1e−17, where `1 + r` is 1, and at 1.1102230246251568e−16, the
  least rate where it is not.
- *A refusal prints a Reference as the compiled model types it:* a rate through
  `float(...)`, and a term, an age or a count of months through `int(...)`. So the
  messages are the same in both engines whether the Reference is set as an int or a
  float, and T5 and the compiled refusal test hold a case of each.
  - The one difference left cannot be fixed in the model. The compiled model truncates a
    float set on an int Reference, 48.5 to 48, where modelx computes with 48.5.
    `model-sec.md` says to set int References as whole numbers.
- *Five cells' powers take uslib's M22 form.* Past the largest float, Python's power
  raises `OverflowError` where C's `pow` gives an infinity. So `inflation_factor`,
  `idx_factor`, `idx_prem_factor`, `benefit_sched` and `annuity_certain_factor` call
  Python's own power where theirs is infinite from a finite base, as `VA_US_SEC` does.
  - Only inputs far outside the product reach it: inflation above about 140,000 a year,
    an index increase above about 2 million, a schedule rate above about 1.5 million, or
    a discount within about 2e−8 of −1.
  - A case in the compiled refusal test reaches each one.
- *The build's directives are pinned.*
  - C3 requires `infer_types` and `cpow` and reads no other directive. Under
    `cdivision=True`, only C4's full sweep, through point 14's `duration(t)` before
    issue, saw floor division truncate.
  - A static test in `test_compiled_conventions_uk.py` now holds `tools/build_sec_cy.py`'s
    line to the two and no other. The tool is shared, so the test guards uslib's builds
    too.
- *The `idx` edges.* An `idx` past the last row raises `IndexError` in both engines, and
  `Projection[-1]` is the last point under its own `point_id()`. The compiled refusal
  test holds both, so `boundscheck=False` or `wraparound=False` would fail.
- *Tests in the template's form, with uklib's precisions:*
  - The label test runs its own compiled comparison, since the shared `label_mismatches`
    takes only labels without parameters.
  - The refusal test runs every case in one child, rewriting file paths in messages to
    file names.
  - The release test runs the committed points alone, as uslib's IUL does for a table
    with a point-keyed companion.
  - The stack test runs every shape at its longest cover, the decreasing and joint shapes
    added to M1's two.
  - The sample's recursion limit is four times the measured need, as uslib's later
    products set it.

**Measured for K6.** On the shared 4-CPU Linux machine, at a load of about 1:
- A build takes 62 s with gcc 13.3.
- C6, the median of three runs of `bench_sec_cy.py`:

  | Engine | `net_cf`, a point | `result_cf`, a point |
  |---|---|---|
  | compiled | 0.168 ms | 0.541 ms |
  | export | 2.10 ms | 2.55 ms |
  | modelx | 68.7 ms | 71.2 ms |

  - On `net_cf` the compiled model runs 12.4 times its export and 402 times modelx; on
    `result_cf`, 4.7 and 132 times. uslib's `Term_US_SEC` ran 9.5 and 4.7 times its
    export.
  - The noise is about ±3% on modelx, and from −10% to +5% on the compiled report.
  - The compiled peak is 86 to 88 MB, and grows by less than 0.1 MB over 6,006 points.
- *Stack.* The deepest call the contract allows, a cold `net_cf` at the waiver point's
  longest cover, needs a recursion limit of 26 compiled, against 1,246 in the export.
  - With every switch on that ships off, it ran on a 256 KiB thread and not on 192 KiB.
  - At the shipped References, per shape:
    - the waiver point: 192 to 224 KiB;
    - the level and decreasing shapes and the joint point: 128 to 160 KiB;
    - the family income benefit: 96 to 128 KiB.
  - All are inside the 1 MiB the test asserts.
- *Times.*
  - Term's module takes 265 s by default, its compile tests and their build included.
    M1's took 90 s.
  - The `term_assurance` shard takes 190 s and the toolchain shard 34 s.
  - At landing, `06a6a46` ran its gate in four jobs at once:
    - uklib's suite, 1,117 passed and 129 skipped, in 431 s (at M1's close, 1,056 and 135
      in 4 min 0 s);
    - the full grid, 410 passed, in 366 s;
    - both shards;
    - the generators' and the harness's checks, doccheck at 0 warnings, and the scaffolding
      at 0 files.
- *CI.* The Tests workflow's run 46 on `06a6a46` passed all 81 jobs, 1 h 18 min from
  dispatch to the last.
  - Its `cython_uk` legs were the first to compile a uklib model. The `term_assurance`
    shard passed its 13 tests in 161 s on Ubuntu and in 153 s on Windows, and the
    `toolchain` shard passed on both.
  - `sec_uk`'s three Term legs passed: the full grid on Ubuntu in 3.9 min, and the core
    on Windows in 3.1 and on macOS in 1.8.
  - The `test` job on Python 3.14 and Ubuntu passed 6,967 tests and skipped 102, in
    36 min 33 s.
  - *The stack, as the test records it.* The cold call ran on a thread of 384 KiB and
    not of 256 KiB on Windows, under MSVC. On Ubuntu it ran on 1 MiB and not on 512 KiB:
    two to four times what it needs here. Both are inside the 1 MiB the test asserts,
    but on Ubuntu with less than a factor of 2 to spare.

**Faults.** Each fault was injected into a copy of its own, and each run was held to the
test meant to catch it.
- The builder: 10, then 9 on the rework, all caught.
- The review: 24, of which 20 were caught.
  - The four misses were the Neumaier correction dropped, the term decoded by rounding,
    `age_at_entry(2)` unguarded, and `joint_age`'s bound at `2**62`.
  - Each is caught since `d262ca9`.
- The verification: 10, of which 9 were caught. The one missed, the zero test written on
  `1 + r`, is caught since `06a6a46`, which two faults more, both caught, also checked.

**Carried into M3 and after.**
- *The compile template, for every later product.* With uslib's Phase 2 template:
  - Every 2-D cache shares one inner width, and the per-life 1-D caches are widened to
    match.
  - A label that takes a parameter needs `"reporting_columns"`, a trace on a blank second
    life in the sample, and a compiled comparison of the module's own.
  - Every int64 column gets a `2**53` bound, tested at exactly `2**53`. Every array read
    gets a check on both sides.
  - A text code is decoded to flags when its name would clash with another family's code.
  - A total is written left to right only where at most two kinds can be non-zero.
    Otherwise it is a compensated sum, and every compensated sum is held to S by
    `float.hex`.
  - A rate Reference read by a closed form gets a domain in `proj_len()` and a zero test
    on its monthly rate. Every power an accepted input can overflow takes M22's form.
  - A decode test's fractional values sit above .5.
  - The compiled refusal test compares `idx` −1 and an `idx` past the table across the
    engines.
  - Measured limits and derived sizes are written in comments, and held by tests.
  - A batched refusal child rewrites file paths in messages to file names.
- *The stack on the Ubuntu runner* (K12). Term's cold call needs two to four times as
  much stack on CI's Ubuntu legs as on this machine, so a chain measured here can fail
  the 1 MiB thread there.
  - Why is not known. The runner's gcc, numpy 2.5.5 and pandas 3.1.1 all differ from
    this machine's.
  - IP, PA and WP run deeper chains than Term's. Each C step reads its stack record
    from CI's Ubuntu and Windows legs, as well as from here, before settling its chain.
  - K12's margin for `SPIA_US_SEC`, 1.33 to 1.6 times, was measured under gcc, not on
    that runner.
- *What the harness cannot see.* C3 reads the builtins a compiled formula calls by name.
  Cython reaches `float.__pow__` through `&PyFloat_Type`, not by such a name, so C3 sees
  M22's call only if its result lands in a Python-object local. It is C5 that confines
  the call to `raise` statements. Both copies of the harness are the same here.
- *For uslib, outside this plan* (U7):
  - uslib's suite holds the build's two directives present, not alone. uklib's static
    test now holds the shared tool's line for both libraries.
  - Its Term's compiled refusal test does not hold the `idx` edges.

### 6.2 Critical illness — `CI_UK_SEC` (E: M, C: M)

*Today:* policy clock from issue, new business only, no in-force column; frame
`0 .. 12n - 1`. On Term's chassis: the same three-cell count chain, the same timings and
maturity rule.

*E — the opening state.* The count alone reproduces S, since S recomputes everything else
from flat References on the policy clock from issue: the premium at reviews,
`P × idx_p × (1 + ρ)^reviews_passed`; the select-factor latch `ci_sel_factor`; the shock
window after a review; and the index factors. But an in-force point's history is not an
assumption: the reviews and RPI increases it has already had are facts of the contract, as
WholeLife's past dividends are. So the columns are `idx_factor_init` and
`idx_prem_factor_init`, `review_prem_factor_init` (the premium factor from reviews to
date, which S has no cell for), `ci_sel_factor_init` for the latch, and, read only while a
review before the valuation date is still inside its 12-month shock window,
`review_prem_shock_init` (D7's `<reference>_init`). Future reviews apply `ρ` from the
valuation date. T2 cannot see a missing column here, since S recomputes them, so each
gets a test of its own on a point whose history differs from the Reference.

*E — rebase:* the frame, base and expiry tests; `reviews_passed = t // review_period_mths`
and the shock window's `t % 60 < 12`, both onto `duration_mth(t)`; acquisition on
`t == 0`; the checks' ranges. Before issue, `pivot_interp` extrapolates and the review,
trend and inflation exponents go negative: each is guarded.

*E — inputs, counts and caps.* Expense inflation `(1 + i)^(y - 1)` moves onto `t`. The
morbidity trend `ci_trend`, `(1 + τ)^(y - 1)` from issue, is a calendar trend: D7 puts it
on the valuation clock, as uslib put ULSG's improvement, and the splice sets it to 0 (§9,
item 4). Additional-payment and children's claims are weighted by `pols_if` and do not
decrement it. No commission. `claim_rate` caps with the bound first in S; the product
`ci_rate × trend × sel` is not capped, and the standalone variant's `claim_rate_paid` is
not capped at all, so past 1 its monthly rate is complex in modelx: SEC caps each, the
bound second, a departure from S recorded in `model-sec.md`. `Data` refuses a pivot rate
of 0 or less, since `pivot_interp` raises a ratio of two rates to a power.

*Splice months:* 1; 11, 12, 13; 59, 60, 61 (the first review, pivot age 45, lapse year 6);
71 and 72 (the shock window's end); 119, 120, 121; 239; 299; with `ρ` and `τ` on.

*C:* `pivot_interp(x, sex, smoker, column)`, a `.loc`, a sorted generator and string keys
per call, becomes two `Data` arrays, `[sex × smoker, age]` for the incidence and the
death rate, built with S's formula element by element over ages 18 to 74 (the table is
extrapolated below 40); decoded `contract_type`, `life_basis`, `cover_basis`,
`premium_guarantee`, `premium_mode`, sex, smoker, the joint columns and the two flags;
timings as Term's; `benefit_pp`'s `MAIN`, `AP` and `CHILD`; and `claims` with `MAIN`, `AP`,
`CHILD` and `LAPSE`. Three kinds can be non-zero in one month, and a left-to-right total
differs from S's `sum` in 415 of 2,040 months, so the total is R12's Neumaier loop. Caches:
`t` to 600 + 120 + 2; inner width 5. `proj_len()` refuses outside the product's bounds,
entry age 18 to 64, cover ending by the 75th birthday, term 5 to 50 years, none of which
S enforces. `cover_basis`, `duration_mth` and `premium_mode` are reached by no report.

*Reuse:* Term's clock and count cells, its `BEF_NB` chain and codes, maturity rule,
acquisition, inflation, joint combination, index columns, lapse reader and `Data` checks.
CI has no selective lapsation, family income benefit, waiver or commission; it adds the
review history, the pivot arrays, the paid-and-exit split of the standalone variant with
`check_claim_split`'s tolerance, and the Neumaier total.

#### Record — M3, done 2026-11-23

Built in three commits, as U1 and §7 ask, on M2's record: `CI_UK_S` copied with only
`_name` changed (`256c079`), the enhancement (`d8c7b75`), and the Phase 1 fingerprint
frozen alone (`c770956`). The review's fixes followed in seven commits more (`7858f7f` to
`325596e`), among them a change to the shared harness (`7858f7f`) and a refreeze of the
fingerprint, alone (`d0d32ad`). It ran beside ULB's in-force step, M9, one in each stream
(§7).
- One agent built it, injecting 30 faults, all caught.
- A second agent reviewed it against this note, the plan and USLIB-SEC-PLAN.md, injecting
  23 faults of its own, of which 16 were caught. It found no wrong number on the committed
  points, and ten gaps in what the model refuses and the tests hold:
  - two NaN References lost silently, a threshold and a slope: on twin 3, claims 5.3%
    high, every check passing;
  - out-of-range References projecting negative premiums, rates and claims;
  - the select latch carried as its factor, so that a latch S closed at a loading of 0
    read as open and closed again at today's: claims 4.9% high on a copy of point 11;
  - the trend's reach held on one cell of one row;
  - no committed row with any review history, so that C2 froze none;
  - five lesser gaps: the splice's ρ equal to the shipped η, the threshold's equality,
    the second life's cap, refusals on a relabelled table, and a docs line.

  It also named a loop in `proj_len()` that the C step would have had to restructure.
- The builder fixed all ten and two plausible items, and 40 faults more were caught.
- The reviewer verified the rework with 27 faults of its own, of which 24 were caught. It
  found five gaps more, which `325596e` closes:
  - References still losing a NaN or leaving their range: the indexation caps and
    multiplier, the two benefit caps, the shares, the expenses, `rpi_rate`;
  - the one-review rule's edges unpinned;
  - a state S reaches refused by `Data`: a latch closed at 0 under η = −1;
  - no test of a check failing a NaN residual, which the domains now keep any input from
    reaching;
  - a review period of 60.0 projecting a float count of reviews.

  28 faults more were caught there.

**What exists now.**
- *`CI_UK_SEC` at stage E.* `Projection` keeps all 63 of `CI_UK_S`'s cells and adds 14:
  - `policy_count`, `duration_mth_init`, `t_entry`, `is_active` and `pols_new_biz`;
  - `expiry_mth`, the month cover ends, named after the event as uslib's rule names it;
  - `review_prem_factor` and `review_prem_change`, the reviews from the valuation date on;
  - the opening state's six cells.
- *The opening state* (D6), six columns, each documented in `model-sec.md` with its
  instant. A review or an anniversary that falls in the valuation month counts as made.
  - `idx_factor_init` and `idx_prem_factor_init`, the RPI increases already given;
  - `review_prem_factor_init`, the premium factor the reviews made so far have given;
  - `ci_sel_latched_init`, 0 or 1, and `ci_sel_factor_init`, read only when the latch is
    closed;
  - `review_prem_shock_init`, the change made by the review that opened the period, read
    only inside that review's 12-month window.

  Each has a K14 test on a reachable state that departs from today's References. No
  companion is needed: CI has no benefit in payment.
- *`model_point_table_sec.csv`*, 14 rows.
  - S's seven points are twins.
  - Five rows are derived: point 4 on its third anniversary, indexed; point 3 at its first
    review, inside the shock window it opens, and past it; point 1 in its last covered
    month.
  - One row is future, point 4 issued at `t = 13`.
  - Point 14 is derived from S under a review change of 10% at month 124 (*Departures*):
    latched at 1.1, a review factor of 1.21, a change of 0.1, its shock window open.
  - A case-insensitive search for every publisher, product and form code that
    `critical_illness/sources.md` cites finds none.
- *`tests/test_critical_illness_uk_sec.py`*, in the template's forms:
  - T2 on a core and a full splice grid, at ρ = 12% and τ = 0;
  - T3, T4 at 2.5, T5, T6;
  - the rules test, the cold-depth bound, the caps and the NaN tests, the runner and the
    committed rows;
  - K14 tests for the six history columns;
  - every twin compared with S with τ = 2% and ρ = 12% on in both models;
  - the domains, 177 cases.

  465 tests pass and 101 skip by default; 566 pass on the full grid.
- *The rest:* `run_sec.py`; `model-sec.md`, with a table of the domains; the registry
  entry directly after `CI_UK_S`, with its `INPUT_FILES`; the generated pages; uklib's
  `index.md` row; the `sec_uk` job over `critical_illness` too.

**Departures and precisions.**
- *τ is 0 in the splice.* §6.2's splice line says "with ρ and τ on", against its inputs
  paragraph, D7 and §9 item 4, which put τ at 0, as uslib's splice does since M11 (§5.2
  there).
  - S trends from issue and this model from the valuation date, so no splice can match
    with τ on.
  - The trend's clock is held by a test of its own. Its reach is held by comparing every
    twin with S, cell by cell, with τ and ρ on in both models: on new business the two
    clocks coincide.
- *ρ is 12% in the splice,* not the 10% the review found equal to the shipped η, under
  which a latch closing at `1 + ρ` passed every case. A case at 20% reaches the cap side of
  `min(review_lapse_cap, shock)`.
- *The latch is a flag beside its factor.* `Data` refuses an open latch whose factor is
  not 1, a factor not finite or below 0, and a closed latch on a guaranteed or unissued
  point. A latch closed at 1.0 or at 0.95 stays closed through a later shock review.
- *Domains.* `proj_len()` refuses 29 References off their domains, by name, NaN and ±inf
  included, among them every rate, cap, multiplier, share and expense, the five contract
  bounds as whole numbers, and `claim_split_tol`. `Data` holds `future_horizon_mth` to
  whole months.
  - `ap_freq_factor` and `child_freq` are bounded by 0 to 12, so that no month's count per
    policy in force can pass 1. The bound is derived in each one's docstring.
  - `review_period_mths` must be whole, and is read as an int.
  - The review found these by NaNs lost in S's bound-first and bound-second `min`s, and
    by values that project negative premiums and claims, every check passing.
- *History S cannot reach is refused,* where the relation is contractual:
  - review history before the first review;
  - between the first review and the second, a factor other than 1 + the change;
  - an index factor other than 1 in the first policy year.

  A latch left open after a change past today's threshold is accepted, since the
  threshold may have been higher then.
- *`q_exit` past 1,* where S's residual turns complex, is refused in
  `check_claim_split_resid`.
- *The contract's bounds,* none of which S enforces, are refused in `proj_len()`: a term
  of 5 to 50 years, entry at 18 to 64, and cover ending by the 75th birthday.
- *The pivot table is checked in its reader,* before S's sort, so that a refusal can name
  the file's lines.
- *The `life` defaults are dropped* from eight cells. S's caps stay as M0 left them, the
  bound second.
- *A row derived under References of its own.* `SecSpec` gains `derived_refs`, `{(p,
  d): {reference: value}}`, in both copies of the harness (`7858f7f`; U3).
  - Such rows are derived last, from S run under those References, which a `finally`
    restores.
  - A repeated `(p, d)`, an unknown Reference and a spec with companions are refused.
  - No uslib spec uses it, and every uslib and uklib `--check` is unchanged.
  - Point 14 is compared with S under its 10% up to its next review, 56 months, every
    cell. After that, today's References take over.

**Measured for K6.** On the shared 4-CPU Linux machine:
- the default module takes 145 s and the full grid 188 s, each near 925 MiB;
- a cold `net_cf` runs 11 cells beyond its one-a-month chain on every shape, inside 16.

At landing, `325596e` ran its gate here in four jobs at once, beside ULB's builder:
- uklib's suite: 1,624 passed and 231 skipped, in 637 s;
- the full grid: 566 passed;
- Term's `term_assurance` compile shard: 13 passed;
- uslib's `test_sec_support.py`: 78 passed;
- `gen_sec_points.py --check` and `gen_sec_fingerprint.py --check`: current and
  reproduced, for CI_UK_SEC, Term_UK_SEC and all twelve uslib models;
- `check_sec_harness.py`: agreed;
- doccheck: 0 warnings;
- the scaffolding: 0 files, for both libraries.

In CI, the Tests workflow's run 47 on `325596e` passed all 84 jobs, 1 h 28 min from
dispatch to the last:
- `sec_uk`'s three new legs: the full grid on Ubuntu in 4.5 min, and the core on Windows
  in 3.2 and on macOS in 3.3;
- Term's legs, both `cython_uk` shards and every uslib leg, unchanged;
- the `test` job on Python 3.14 and Ubuntu: 7,009 passed and 103 skipped, in 40 min
  26 s, its harness step agreeing.

**Faults.** Each was injected into a copy of its own, and each run was held to the test
meant to catch it.
- The builder: 30, then 40 on the rework and 28 on the last gaps, all caught.
- The review: 23, of which 16 were caught. Each miss is caught since the rework:
  - the second life uncapped;
  - refusals naming positions;
  - the trend dropped from the standalone paid rate;
  - the threshold's `<=` turned to `<`, at either site;
  - a latch factor below 1 read as open;
  - `Data`'s floor on the change raised to 0.
- The verification: 27, of which 24 were caught. Each miss is caught since `325596e`:
  - the one-review rule's tolerance loosened;
  - its window ended a month early;
  - a check passing a NaN residual.

**Carried into M4 and after.**
- *M4, §6.2's C list,* and M2's compile form:
  - the pivot arrays, the decodes and codes, and the claims total as R12's compensated
    loop, with `ALL` and a `twin_arg_map`;
  - `idx`, the reporting labels, and caches of `t` 722 and an inner width of 5;
  - M22's guards on the five powers: inflation, the trend, the two index factors and the
    review factor;
  - References printed as compiled, the `2**53` bounds and the `idx` edges;
  - `sample_sec.py`, `spec_sec.py`, the `cython_uk` shard and C6.

  `static_faults` lists, in `proj_len()`, only the `"reviewable"` code, and elsewhere
  only what that list rewrites.
- *The template, for every later product:*
  - A domain for every Reference a bound-first or bound-second `min` or `max` reads, or a
    closed form raises, NaN and ±inf included: a NaN is otherwise lost, or a value leaves
    its range with every check passing. A bound the C step's caches rest on is a whole
    number.
  - A latch, or any state S holds as a value standing for an event, is carried with a
    flag beside it.
  - History columns are held to each other only where the relation is contractual.
  - Where the shipped References leave a path's history trivial, one committed row is
    derived under References of its own (`derived_refs`), so that C2 freezes the path.
  - A splice Reference differs from every shipped one it could be mistaken for.
  - Each threshold is tested at equality and one float past it.
  - A Reference read on the valuation clock has its reach held by the twins compared with
    S with it on: on new business the two clocks coincide.
  - Some `MALFORMED` cases run on a relabelled table.
  - A test replaces each residual's formula with NaN, and the check must fail.

### 6.3 Income protection — `IP_UK_SEC` (E: L, C: L)

*Today:* the policy clock, `duration(t) = t // 12`, `proj_len() =
12 × (expiry_age − age_at_entry())`; the claim clock `z` is a separate 1-based cohort
index, which only the termination cells read. In force means in claim: `status =
in_claim` puts the count into cohort `claim_duration_months + 1` and leaves the healthy
state empty, and on such a row `entry_age` is the attained age at the valuation date, the
policy clock restarting there (a [std] simplification). Points 2, 5 and 7 are in claim, at
claim durations 0, 30 and 0. **A healthy policy months after issue cannot be represented:**
`active` always means at issue, with the first year's benefit, premium, lapse rate and
inflation. S point 1 restated the only way S allows at month 60 drops the 0.28 % then in
claim and values its net cash flow at 3 % at 1,037.47 against 449.79; adding one in-claim
row per live cohort makes month 0 exact, but every row's clock restarts, so `pols_if` is
6.2 % low after 12 months and 15.6 % after 60.

*E — the opening state,* at the start of month 0, recoveries already returned to health:
- `pols_active_init`, the healthy share of the count, S's `pols_active(d)` per policy;
- **the claim cohorts**: S's `sick_cohorts(d)`, the share of the count in each claim
  duration `z`, cohort 1 being month `d − 1`'s inceptions, not yet paid. A point's vector
  is as long as its months in force: 359 non-zero cohorts on point 1 at month 359, up to
  624 under the product's bounds (entry 18 to 59, expiry 50 to 70), one on a claim
  extract. It goes in a sparse companion, `inforce_cohorts_sec.csv`, keyed
  `(point_id, z)` with the share `pols_sick_dur_init`, in IUL's ladder shape (D8, R7).
  `Data` refuses a `z` that is not whole or outside `1 .. duration_mth`, a share outside 0
  to 1, shares that with the healthy share do not sum to 1 within a stated tolerance, and
  any cohort row on a point not yet in force, which is issued healthy. Rejected: 624
  columns; and one model point per state, exact since the model is linear (25 rows summed
  matched S to 5e-15), but a projection per cohort;
- `benefit_pp_init` and `premium_pp_init`, the amounts entering month 0, S's
  `benefit_pp(d − 1)`: escalation is closed-form by policy year in S, but an amount in
  force carries the RPI actually given and any increase refused. The benefit escalates on
  policy anniversaries for everyone in health and in claim alike, so no cohort carries an
  amount of its own.

A scratch copy with the clock rebased and both recursions started from these reproduced S
from `d` on in 28 splices, all 7 points from `d = 1` to the last month: every count, cash
flow, rate, residual and cohort element to 7.7e-13 relative, inflation at 0 in both. No
DIA-style restructure (K9) is needed: nothing is priced at issue on survival. The three
cumulative counts, which only `check_states_resid` reads, restart at `t_entry()`, the
identity restated on the count on the books, and T2 compares their increments.

**The in-claim twins** have no policy clock in S (D8). Each twin takes
`duration_mth = 12n` with `n ≥ ⌈(z0 + 1) / 12⌉` and issue age `entry_age − n`. Points 2
and 5 then match S in every count, cash flow and check, since their healthy state is empty
and only the clock cells differ; on point 7 recovered lives lapse at the real policy year
(`pols_if(60)` 0.8002 against S's 0.7791), so it is compared under a flat lapse table, and
its difference is S's restarted clock, recorded as an S defect.

*E — rebase:* the bases at `t == 0` and `t <= 0`; `annuity_dis()`'s division by
`amount_payable_pp(0)`, which becomes `t_entry()`; `max_dur()`, which on a future row would
size `z` by the horizon and is bounded by cover from issue; `pols_if_at(t, AFT_DECR)` and
the roll-forward's `pols_if(t + 1)`, which would count next month's new business and read
`pols_if_at(t + 1, BEF_NB)`; and `result_states()`'s unguarded rates before issue. No other
policy month is passed as `t`. Every chain is one cell a month, the only read ahead `t + 1`;
a cold `net_cf` is one cell a month plus 4 to 6, at most about 750 at the contract's
longest cover.

*E — inputs, counts, caps.* Expense inflation moves onto `t // 12`, which equals S on its
in-claim rows; discounting is already on `t`; `rpi_rate` is flat, its dates contractual;
`cycle_factor` is a scenario overlay. `pols_if` = healthy + sick stays the row weight, D5
with no exception; new business enters healthy; `BEF_NB` is exact, since new business
arrives only on an empty book. No acquisition or commission. Caps: active mortality is
uncapped in S (at a factor of 100, point 6 reaches `q = 1.345` at `t = 72`, its counts go
complex, and both checks still pass), as is sick mortality; inception is floored and
recovery and lapse capped with the bound first. SEC caps mortality, sick mortality and
inception `min(q, 1.0)`, departures from S recorded in `model-sec.md`, keeps S's order for
recovery and lapse, and `Data` refuses blank, text, infinite and out-of-range values in all
five rate columns, and a `cycle_factor` of 0 or less (below 0.4 S's in-claim survival is
silently 0).

*Splice months:* anniversaries 11 to 13; 59 to 61 (ultimate lapse); the inception table's
pivot ages (60, 120, …, 300, 348 on point 1); claim-duration bands on point 2 (11 to 13,
23 to 25, 47 to 49) and point 5 (5, 6, 17, 18); point 7 at 1 and 12 (recoveries back to
health); 1 and the last two months; RPI above 3.33 % to switch on the escalation lapse
shock, and at 10 % for the escalation cap; the month before a mortality cap binds.

*C — the restructure.* `sick_cohorts(t)` and `claim_rate_vectors()` return tuples, summed
by `sum()`. They become a two-parameter recursion `pols_sick_dur(t, z)`, `z = 1` from
`pols_inception(t − 1)` and otherwise `(t − 1, z − 1)` times the step's survival, based at
`t_entry()` from a `[idx, z]` array, with Neumaier sums in `z` order. Prototyped: bit for
bit with S on all seven points in every cell and cohort element, so C2 holds exactly; in
modelx it costs 130,321 cache entries and 5.3 s against 0.57 s on point 1, so it belongs to
the C step, as IUL's re-keying did. The live band is not narrow, so R15's re-keying gains
nothing: the `[746][626]` cache is about 3.7 MB, and uslib M15's one inner width per model would
widen `pols_if_at` and `claims` to 626 as well, about 11 MB a point against VUL's 7.8. The
C step chooses between making the timings and kinds 1-D cells, which keeps the rule and the
width to the cohorts, and pooling every cohort past the termination table's last duration
(49 months) into one ultimate bucket, exact in exact arithmetic but not bit for bit with S;
**recommended: the first.** S's tuple cells stay for S's tests as `"engine"` cells, which
needs the key to admit a cell of one parameter, or T1 exempts `sick_cohorts` and maps it
onto `pols_sick_dur`.

*C — the rest:* inception to `[schedule, age]`, 40 schedules (sex × occupation class ×
deferred period), `Data` reproducing S's interpolation, extrapolation and zero floor
element by element; termination by duration year, clamped at its last row; mortality
`[sex, age]` padded from 0; lapse by policy year, clamped at 6; the companion `[idx, z]`.
`status` a label, `escalation` a flag, `recovery_basis` a code, `premium_basis` a `Data`
refusal; kinds `BENEFIT`, `DEATH`, `LAPSE` with a total, left to right (only the benefit is
ever non-zero); timings `BEF_NB`, `BEF_DECR`, `AFT_DECR`. No float parameter, no `round`
or `math`. Caches: `t` 0..745, `z` 0..625, years 53, ages 70; `proj_len()` refuses outside
`issue_age_min` (18), `expiry_age_max` (70) and the horizon. Never reached by a report:
`annuity_dis`, `pv_benefits`, `disc_factor`, `claim_surv_step`, `pols_if_at`,
`pols_sick_dur`, `premium_basis`.

*S defects:* `premium_basis()` has no caller, so its check never runs (a point set to
"reviewable" projects); mortality is uncapped; the docstrings say restoring the age
dimension to the termination basis touches only the lookups, but the cohort shift assumes
rates depend on `z` alone; `claim_rate_vectors` recomputes in-claim survival beside
`claim_surv_step`, which only the tests read; and point 7's recovered lives lapse at
first-year rates.

IP is the plan's largest product and the least certain (K11), so it goes last in its
stream.

### 6.4 Whole of life — `WOL_UK_SEC` (E: M, C: S)

*Today:* the policy clock from issue, new business only; `proj_len() =
12 × (omega_age − age_at_entry())`, a limiting age of 120 rather than a contract end, so the
frames end in rows of zeros (119, 227 and 71 on the three cells' points). Seven points,
two cells: over-50s guaranteed acceptance (O50) and underwritten (UW).

*E — the opening state.* Four cells read month `t - 1`: `pols_if`, the paid-up count
`pols_pu`, the paid-up cover `pu_benefit`, and the premiums paid `prem_cum_pp`, which the
moratorium returns. So the columns are `pols_pu_init`, `pu_benefit_pp_init` and
`prem_cum_pp_init`, and, on the RPI-escalating variant only, `cover_pp_init` and
`premium_pp_init`: S rebuilds the escalated cover and premium from issue at today's
`rpi_rate`, which on an in-force point is history, not an assumption, and which the splice
cannot see on one flat rate, so it gets a test of its own; `cover_pp(t)` escalates from
the valuation date's step. `payments_made` (no payment holidays are modelled), the
moratorium and suicide windows, paid-up eligibility and the escalation steps all follow
from `duration_mth`; no `_prev_anniv_init` or `_ytd_init`. An in-memory prototype with the
closed-form clock, bases at `t_entry()` and the count columns restated S's points at 29
months each and four future months, 237 rows: every column of both reports matched S to
1.4e-13 relative, 2.3e-13 with the stress and 1 % improvement on, but for the
roll-forward check on the future rows (below).

**The paid-up strand** is the first two-strand count in either library. `pols_pu` counts
paid-up policies beside `pols_if`'s premium-paying ones, and S's `pu_benefit` is their
summed cover. The opening state holds the paid-up count beside `policy_count` and the
cover per paid-up policy, `pu_benefit_pp_init`, so that the counts alone carry the scale
and T4 multiplies `policy_count` and `pols_pu_init` together. A point may be paid-up
entirely, `policy_count = 0`. `Data` refuses either paid-up column on a point without the
paid-up variant, or before the earliest month a conversion can have happened.

*E — rebase:* about fifteen sites: the clock cells; the four bases at `t == 0`; cessation
in `premium_pp` and `lapse_rate`; the moratorium's `t < moratorium_mths()`; the
underwritten suicide window; `payments_made`'s `t + 1`; acquisition at `t == 0`, already
per policy in S, so `pols_new_biz(t)` keeps T1 at any count; the five tests against
`proj_len()`, which take a policy-clock end, `limit_mth()`; and `crossover_mth`, which
passes policy months as `t` over the premium term and returns a policy month (166 on the
anchor). In SEC the crossover can fall before the valuation date, where look-back stops,
and no projection cell reads it: it becomes a loop over the contractual premium and cover
schedule on the policy clock, the RPI variant's history taken from its columns, and keeps
S's policy month. Commission, 25 % of policy-year-1 premiums as paid, continues on a point
valued in its first year. `AFT_DECR` becomes `pols_if_at(t + 1, BEF_NB)`.

*E — counts and checks.* `pols_all = pols_if + pols_pu` weights maintenance and the
roll-forward. The roll-forward residual has no new-business term, and S's checks scale
their tolerance by `pols_if_init()`, which D5 makes 0 on new business: SEC adds
`pols_new_biz` to the residual and scales by the count on the books, `policy_count() +
pols_pu_init()`. Truncation at the limiting age is kept, keyed on the policy clock, and
`proj_len()` refuses a point at or past it.

*E — inputs and caps.* Expense inflation and mortality improvement, both
`(1 ± r)^duration(t)` from issue, which is S's projection start, move onto `t // 12`, as
ULSG's improvement did; `rpi_rate` is a flat Reference read from the valuation date.
Mortality is `min(1.0, q × loading × improvement)` in S, `min(q, 1.0)` in SEC; it binds on
the O50 cells at `t = 480` and 432, so the cap test uses the shipped points. The lapse bound
keeps S's order, and `Data` refuses a negative lapse stress. With 1 % improvement,
`check_truncation()` fails on the UW points (7.1e-6 still in force at 120) and at 2 % on
all: the splice switches improvement on at a rate the check holds at, and a test of its
own records where it gives way.

*Splice months:* points 1–4: 1, 6, 11 to 13, 60, 118 to 121, 165 to 167 (185, 186 on
point 4), 239 to 241, 479 to 481, 599; point 7: 222, 223, 299 to 301, 431 to 433, 659; UW:
11 to 13, 642, 643, 887 to 889, 959; future rows at −1, −12, −120; the lapse stress on;
variants with RPI and paid-up together, the double accidental benefit with paid-up, and
entry at 80.

*C:* the mortality table's four-key `.loc` per `t` to `[schedule, age]`, eight schedules
(basis × sex × smoker) padded from age 0; the lapse table to `[cell, policy_year]` with a
last-year extent; `cell`, `escalation`, `sex`, `smoker` and `mort_basis` decoded, the two
variant flags int64. Codes: timings `BEF_NB`, `BEF_DECR`, `BEF_LAPSE`, `AFT_DECR`;
`benefit_pp`'s `NON_ACC`, `ACC`, `DEATH`, `PAID_UP` and `claims`' `DEATH`, `DEATH_PU`,
`LAPSE`, one code for `DEATH` in both families, as ULSG's `GRACE`; a left-to-right total
equals S's, the lapse kind being 0. All 61 cells cached, no float parameter, no `round` or
`math`. `t` to 1,346 (12 × (120 − 18) + 120 + 2), inner width 4, about 1 MB a point;
`proj_len()` refuses an issue age below `issue_age_min` (18) and an `omega_age` past the
table. Never reached by a report: `crossover_mth`, two timings, and on UW the moratorium
and accidental cells, so the sample calls them. At the contract's maximum a cold chain is
about 1,350 levels.

*S defects:* the bound-first caps; `Data` validates nothing (blank or out-of-range rates,
unknown `cell` or `escalation` text, the paid-up variant without a cessation date); and
`test_whole_of_life_uk.py` writes `mort_table_light.csv` into the product directory while
its CSV-set test may run.

### 6.5 With-profits — `WP_UK_SEC` (E: M, C: M)

*Today:* the policy clock, opened late on an anniversary: `proj_start() =
12 * duration_inforce()`, `duration(t) = t // 12`; `proj_len()` counts policy months from
issue, `12 * policy_term()` on the conventional endowment (CWP) and
`min(12 * (omega_age - x), fund_exhaust_mth())` on the unitised bond, where
`fund_exhaust_mth()` loops the units chain from `proj_start()` to the limiting age and
returns the first month the units run out, 0 meaning never. Five of the six shipped points
are in force: bonds 1 to 4 at year 5 (frames 60..779, and 60..402 on point 4, which
exhausts by forced encashment), CWP 6 at year 20 (240..299). Point 5, a CWP, is the only
new business; no bond is.

S's in-force opening loses two cumulants, which restart at 0 at `proj_start()`: the
guarantee-charge cumulant `guar_charge_cum_pp`, which caps the charge at 2 % of the asset
share, and the count-weighted `smoothing_account`. Bonds reopened at their own anniversary
state therefore part from S: a −15 % variant reopened at 60 keeps charging from `t = 100`
where S from issue stops, its asset share up to 49 % off; a +5 % variant reopened at 120,
480 or 600 misses the cap that binds from 425. S's own point 3 stops charging at 487 where
from issue it would at 425. With both cumulants carried in, 62 rows reopened at any month,
mid-year, declaration and guarantee months, both caps' edges, the corridor, the asset-share
floor, exhaustion's last month and maturity among them, reproduce S from issue to 3e-12
relative, 6.5e-13 with the bonus rule on (on a scratch copy whose `proj_start` and two
bases read columns).

*E — the opening state,* at month 0's `BEF_NB` instant, S's close of month `d - 1`:
`asset_share_init`, `units_init` (S's `units` column), `unit_price_init` (on new business
the seed price, an issue value, which `Data`'s no-opening-state check exempts),
`attaching_bonus_init` (CWP), `smoothed_payout_init` (0 legitimately once the asset share
floors), `bonus_rate_init` (the rate for the policy year under way, S's `bonus_rate`
column; the splice writes S's own `bonus_rate(d)`), and the two S lacks,
`guar_charge_cum_pp_init` and `smoothing_account_init`. No `_prev_anniv_init` (the
declaration costs the month's own opening values) and no `_ytd_init`. The twins of S's
in-force rows carry 0 in both new columns, which reproduces S, as WholeLife's twins carry
S's own "before the frame" values. `Data` accepts an asset share and a payout of 0 in
force, and refuses an in-force bond with no units, a `fund_return` of −1 or less (its
monthly rate is complex), and guarantee dates on a CWP, which `guarantee_exercise` and
`guarantee_imminent` would read.

*E — rebase:* `premium_pp` adds the single premium at `t == 0`, which on the valuation
clock every in-force bond would pay again; `is_declaration_month`'s `(t + 1) % 12`;
`declaration_month()`, the policy month `12 * duration(t) + 11`, which `bonus_rate` passes
as `t`, at `d` and at `d - 12`, the model's one `t - 12` read: it takes WholeLife's
`anniv_mth` form; `guarantee_imminent`'s `12 * g - 1 - t`; `duration`, `age` and
`policy_year` on `t`; about twenty bases on `proj_start()`, which move to `t_entry()`; and
`fund_exhaust_mth`'s policy-month range and its sentinel 0, which on the valuation clock is
a real month. `is_active(t)` must not read `proj_len()`, since `proj_len()` reads the units
chain: it reads the policy-clock end of cover alone. WP has no acquisition or commission.

*E — chains.* Every recursion steps back one month, and none is evaluated below the frame,
but four chains are coupled and long: the count three cells a month, the asset share seven
(`asset_share(779)` runs 5,042 deep cold on point 1), the smoothed payout three,
interleaved with it through `wd_as_pp` and `policy_value_open`, and the CWP guarantee two.
D5's one-cell-a-month form applies to each. Two far reads stay, each admitted by R2:
`proj_len()` itself, which scans the units chain to exhaustion before any row (172 cells
deep cold on point 4), becomes one explicit loop over the units' own months from
`t_entry()`, the form DIA's survival took; and with the bonus rule on, `bonus_rate(t)`
reads the declaration month 1 to 11 months ahead, R2's anniversary read, except that on a
frame ending mid-year by forced encashment it reads past the frame (S evaluates the asset
share to 635 on point 4, whose last month is 628). SEC bounds that read by the frame, a
recorded departure that changes only the report column `bonus_rate` after the last month.

*E — inputs, counts, caps.* `fund_return` and `bonus_rate` are constant levels per point,
no path, so nothing is re-based. Expense inflation moves onto `t // 12`, so the in-force
twins differ from S by 1.03^5 and 1.03^20 in `expenses` and are splice cases at 60 and 240
with inflation at 0; T1 is exact on point 5 alone. Counts keep S's timings and add `BEF_NB`;
maturity takes the last month's survivors, the CWP paying G + TB and the bond FV + FB on
forced encashment only. Mortality is `min(1.0, q × mort_be_factor)` in S, `min(q, 1.0)` in
SEC; the table reaches 1.0 at M113 and F118, so at the shipped factor of 0.6 the cap never
binds, and its test takes a factor above 1. The surrender bounds keep S's order.

*E — future new business:* the CWP is closed to new business (`product-spec.md`), and it is
S's only new-business row. Future rows, and T1 on a bond, need a bond variant issued at the
valuation date, which the spec adds to its S source table (U6's variants are S rows, never
formulas). Until then T1 covers the bond through the splice alone.

*Splice months:* declarations at 71 and 119 (CWP 11 and 287), the month after (72, 120,
288) and mid-year (65, 125); the guarantee window on point 2 (106, 107, 118, 119, 120); the
smoothing cap (61, 64, 65, 289, 290); the corridor (92; 118 to 120, 131, 144, 154, 155);
the MVR turning on (67, 68); the charge cap (point 3 at 486 to 488, where it flickers
monthly; 158, 159; 279, 280; variants at 100, 425 and 194); the asset-share floor (240 to
242, 600); exhaustion (396, 402); one-row frames (maturity 299, limiting age 779); the
bond's issue month on a variant (0, 1); S's in-force rows at 60 and 240. Variants: bond new
business, a female life, the bonus rule on, `misc_surplus_rate` above 0, a binding
mortality cap, a −40 % crash for the corridor's ceiling, and the pension tax basis.

*C:* `mort_table` to `[sex, age]` padded from 0; `lapse_table` to `[chassis, policy_year]`
with each chassis's last key kept for S's clamp; `guarantee_dates`, text of one year or a
`;` list, to a `[idx, policy_year]` flag array; `chassis()` and `sex()` decoded,
`guarantee_years()`'s tuple gone, `tax_basis()` a label. Codes: the count's four timings
then the asset share's six, one inner width of 10; claims kinds `DEATH`, `SURRENDER`,
`GUARANTEE`, `MATURITY`, three non-zero together in the last month, so the total is
Neumaier's. No float parameter, no uncached cell (all 99 cached), no `round` or `math`, 12
powers under `cpow=True`. Caches: the bond's longest cover is 1,224 months from age 18, the
table's first, though the product admits issue from 3 months, and S bounds no CWP term;
`proj_len()` refuses outside `issue_age_min` (18), a CWP maturity-age bound and the
horizon, beside `omega_age`; ages 121, policy years 103. Never reached by a report:
`bonus_supportable` and `declaration_month` with the rule off, `policy_value_pp`,
`smoothing_cost_pp` at `GUARANTEE`, and `unit_price` on a CWP; the sample runs with the
rule on.

*A name.* The out-of-scope chassis key `SF_prufund` names a product: `WP_UK_S`'s refusal
message and the notes' `chassis` enum carry it, and `test_with_profits_uk.py` writes it into
a temporary model point table in the product directory. §9 item 9 asks whether a commit
of its own renames it in M0, as uslib renamed RILA's and VA's keys at their landings.

### 6.6 Unit-linked bond — `ULB_UK_SEC` (E: S, C: S)

*Today:* the policy clock from issue, new business only. `horizon_mths() =
12 × (omega_age − age_at_entry())`; `fund_exhaust_mth()` scans `av_pp(t)` from 0 over the
horizon and returns the first month the fund is `<= 0.0`, else `horizon + 1`; `proj_len()`
is the smaller. Frames run 353 months on points 1, 4 and 5 (exhaustion), 324 on 3, and 660
and 780 on 2 and 6 (the horizon). `uf_init`, which seeds `av_pp(0)`, is called the in-force
hook in the notes, but it moves the fund and nothing else: point 1 restated through it at
month 240 surrenders at 2 % where S does at 15 %, charges £305 of expenses where S charges
£8.19, and holds `wd_cum_pp` at 416.67 where S holds 100,416.67; point 4's GMDB restarts at
100,000 where S's is 0, and runs out 53 months on where S's does at 113.

*E — the opening state* is four columns: `policy_count`, `duration_mth`, `av_pp_init` (S's
`uf_init` renamed, holding `av_pp(d)`, above 0 for a point in force) and `wd_cum_pp_init`,
the withdrawals and adviser charges since issue, which never restart and which also open
the GMDB, `max(0, P − wd_cum_pp_init)`. The cumulative 5 % allowance, the excess gain and
the allowance factor are closed forms on the policy year; the premium, the charges, the
withdrawal pattern and the GMDB flag are issue columns already. `return_12m` reads no
window: it is `fund_return + return_shock`, two flat References, and the "rolling" cap is a
twelfth of the annual cap each month, so neither needs history. An in-memory variant of S
with these four columns, the closed-form clock, the bases on them and acquisition on
`duration_mth(t) == 0` matched S's reports and state cells to 6.4e-12 relative on 533
restated rows, all six points and two adviser-charge variants, under the shipped
References and three return stresses, `excess_gain_pp` alone needing the residuals' 1e-9
floor (S's value there is a rounding of 1.5e-11 to 2.9e-11).

*E — the exhaustion test.* S ends the frame at the first month the fund is exactly 0 or
less. With an adviser or GMDB charge the floor can leave a positive rounding instead: in
142 of 264 adviser-charge variants at 5 % growth (residues of 9e-16 to 4e-14) the frame ran
up to 8 months on, and at −2 % one ran 20 months on, charging £45.85 of maintenance against
6e-18 of AMC. So the frame depends on the last bit of the fund: point 3 restated at month 1
from a read one ulp off runs 324 rows against S's 323, and even with the harness's exact
writer one of the 533 rows missed. SEC takes `VA_US_SEC`'s form: a depletion threshold, a
lower-case Reference, below which the fund counts as exhausted, and `proj_len()` refuses a
point in force whose fund is at or below it; a recorded departure, whose effect on each S
point the module states. `fund_exhaust_mth()` scans from `t_entry()`, so that a future
point's empty pre-issue fund does not end its frame at 0, and is R2's admitted loop.

*E — rebase and chains:* the issue tests on `t` in `av_pp`, `gmdb_guarantee_pp`,
`wd_cum_pp`, `pols_if` and acquisition; the horizon and frame counted from issue;
inflation on `duration(t)`, which moves onto `t // 12`. No `t − 12` read and no anniversary
test on `t`; the surrender bands, the year-21 step and the 20-year allowance read
`policy_year(t)` and need only `is_active(t)` before issue, where the allowance goes
negative and the surrender table's `.loc` raises, or as an array silently wraps (F4). The
fund chain runs four cells a month (`av_pp` through `av_pp_at` at `AFT_WD`, `AFT_CHARGE`,
`AFT_GROWTH`): `av_pp(352)` runs 1,413 deep cold, and point 6's `net_cf(779)` 3,122, which
at the contract's longest cover is about 5,400, past F7's stack budget. So `av_pp` writes
the month's steps inline, one cell a month, as `MYGA_US_SEC.av_pp` does, `av_pp_at`
reading it; the count takes D5's `BEF_NB` form.

*E — inputs, counts, caps.* `fund_return` and `return_shock` are flat References, no path,
so nothing is re-based in T2 or T3. Counts keep S's `BEF_SURR` and `AFT_DECR` and add
`BEF_NB`; maturity is the survivors at exhaustion or ω, paid nothing. Acquisition, £300 at
`t == 0`, moves onto `pols_new_biz(t)`; an in-force point has no other initial cost, the
premium being net of the set-up adviser charge. `check_pols_roll_fwd`'s tolerance reads
`policy_count`. Mortality is `min(1.0, table × mort_be_factor)` in S, `min(q, 1.0)` in SEC;
it binds only with the factor at 1.25 or more. The surrender bound `min(surr_rate_cap, …)`
keeps S's order and cannot bind as shipped (0.10 × 2 × 1.5 = 0.30 < 0.35); its variant
raises `perf_factor_cap`.

*Splice months:* the surrender bands (11, 12, 23, 24, 59, 60, 119, 120); year 21 at 239 to
241, where the step goes to 1.5, the allowance caps, the first excess gain appears and
point 4's guarantee reaches 0; 37 and 125; each frame's last month (352, 323, 659, 779) and
the months after a residue. Variants: the GMDB in the money, a custom withdrawal above
7.5 % so that the cap binds, a return shock, a binding mortality cap, and a raised
`perf_factor_cap` that binds the surrender cap from year 21.

*C:* mortality `[sex, age]` padded from 0; surrender `[policy_year]` 1 to 11 with its last
year an int cell; `gmdb_flag` int64; `sex` a schedule; `lives` refused unless `single`
(S's guard is never called, so a joint row projects as single); `wd_pattern` an int code,
`wd_allowance_rate` being a `Projection` Reference `Data` cannot read. Codes: `BEF_NB`,
`BEF_DECR`, `BEF_SURR`, `AFT_DECR`, then the fund's `BEF_GROWTH`, `AFT_GROWTH`,
`AFT_CHARGE`, `AFT_WD`, one inner width of 8; claims `DEATH` and `SURRENDER` with a total,
left to right. No float parameter, no uncached cell, no `round` or `math`. `t` to 1,346
(issue age 18 to ω 120, the horizon, 2); `proj_len()` refuses below `issue_age_min` (18),
though the product admits issue from 3 months, which the table cannot rate. Never reached
by a report: `av_per_segment_pp`, `n_segments`, `lives`, and the `BEF_GROWTH` and
`BEF_DECR` keys.

#### Record — M9, done 2026-11-23

Built in three commits, as U1 and §7 ask, beside CI's in-force step, M3, one in each stream
(§7):
- `ULB_UK_S` copied with only `_name` changed (`7dcdb98`);
- the enhancement (`999a8b9`);
- the Phase 1 fingerprint, frozen alone (`82e35c3`).

The review's fixes followed in five commits more, among them a committed row derived under
a return of its own and a refreeze of the fingerprint, alone (`54dc92e`, `f851e5c`). They
were rebased onto M3's landing to use its `derived_refs`, keeping both sides of each shared
line.
- One agent built it, injecting 12 faults, all caught.
- A second agent reviewed it against this note, the plan and USLIB-SEC-PLAN.md, injecting
  22 faults of its own. Two were missed, and two more were caught only by tests other than
  the one meant for them, T1 and T4.
  - It found no wrong cash flow. It confirmed every claim of the threshold's.
  - It confirmed the inline chain bit for bit, on every twin and on 137 grid rows, under
    both sets of References.
  - It found seven gaps:
    - the allowance accrued before the valuation date, rebuilt from today's rate (K14);
    - six References with no domain, a NaN in each lost in S's bound-first `min` or `max`;
    - the 7.5% cap net of the adviser charge, reached by no row;
    - T1's frame cut keyed by model, not by point;
    - T4 never testing the rider charge;
    - mortality refusals naming keys, not lines;
    - a loop in `proj_len()` that the C step would have had to restructure.
- The builder fixed all seven and the minors, and 16 faults more were caught.
- The reviewer verified the rework with 14 faults of its own, of which 13 were caught, and
  found four gaps more:
  - the allowance column, on an anniversary, measured after month 0's own accrual;
  - `omega_age` with no domain;
  - a fund overflowing to NaN in silence;
  - the shock's domain stated on the shock, not the trailing return.

  The builder closed them, with 10 faults more caught.
- On M3's `derived_refs`, the builder committed a row with the GMDB in the money (4 faults,
  all caught).
- The reviewer verified that round and the rebase with 18 faults of its own, all caught.
  It found:
  - `omega_age`'s new bound one year too strict;
  - the overflow refusal blaming only the return;
  - the derived row recording its return nowhere in the table.

  The first two are fixed in `a15d894`; the third is carried.

**What exists now.**
- *`ULB_UK_SEC` at stage E.* `Projection` keeps 73 of `ULB_UK_S`'s 74 cells and adds 9.
  - It drops `av_init_pp`, which `av_pp_init` replaces.
  - It adds:
    - `policy_count`, `duration_mth_init`, `t_entry`, `is_active` and `pols_new_biz`;
    - `result_pols`;
    - the opening state's three cells.
- *The opening state* (D6), three columns per policy. Each is documented in `model-sec.md`
  with its instant, and each has a K14 test.
  - `av_pp_init` is the fund at the start of month 0, before that month's growth, charges
    and cancellations, which is S's `av_pp(d)`. It replaces S's `uf_init`, which moved the
    fund and nothing else.
  - `wd_cum_pp_init` holds the withdrawals and adviser charges to the end of month −1.
    These never restart, and they open the GMDB at `max(0, P − wd_cum_pp_init)`.
  - `allowance_cum_pp_init` is the 5% allowance accrued before month 0's own accrual, so
    that a policy year opening at the valuation date accrues at today's rate, as new
    business does (D6, as precised at M7).
- *The depletion threshold* (§9 item 10), `depletion_threshold = 0.005`, VA's value and
  form. Below it the fund counts as exhausted.
  - `proj_len()` refuses a point whose opening fund is at or below it.
  - `fund_exhaust_mth()` scans `av_pp` from `t_entry()`: R2's admitted loop, and the only
    look-ahead.
- *The fund chain,* written inline, one cell a month, in `av_pp_at`'s order (MYGA's form),
  with `av_pp_at` reading it. S's four cells a month ran 3,122 deep on point 6.
- *`model_point_table_sec.csv`*, 12 rows.
  - S's six points are twins.
  - Four rows are derived from S:
    - point 1 in its third policy year;
    - point 3 at month 66;
    - point 4 at year 21, where the step goes to 1.5 and the allowance caps;
    - point 1 in its last month before exhaustion.
  - One row is future, point 4 issued at `t = 13`.
  - Point 12 is derived from S under a fund return of 0 at month 66 (*Departures*). Its
    guarantee of 72,500 is above its fund of 67,232.39.
  - A case-insensitive search for every publisher, product and form code that
    `unit_linked_bond/sources.md` cites finds none.
- *`tests/test_unit_linked_bond_uk_sec.py`*, in the template's forms:
  - T2 on a core and a full splice grid, with ten variants, the tenth binding the 7.5% cap
    net of an adviser charge;
  - T3, T4 at 2.5 and T5, the last with the domains, over 102 cases;
  - T6;
  - the rules test, the cold-depth bound at each shape's longest cover, the caps and the
    NaN tests, the runner and the committed rows;
  - K14 tests for the three history columns, the threshold's tests, the inline-chain test,
    and a month-on restatement test.

  277 tests pass and 97 skip by default; 374 pass on the full grid.
- *Shared files, added to in place:* `test_model_conventions_uk.py`'s `TWIN_FRAME_ENDS`,
  beside `TWIN_FLOORS`, keyed by point. The rest is as M3's: the registry entry and its
  `INPUT_FILES`, the product spec, the `sec_uk` module and uklib's `index.md` row.

**Departures and precisions.**
- *The threshold's effect on S's points.*
  - Points 1, 4 and 5 close on exactly 0 and keep S's 353 months. Points 2 and 6 never
    run out, keeping 660 and 780.
  - Point 3 closes on 3.386e−15 at month 322 and runs 323 months, where S runs 324. Its
    0.019446 survivors mature in month 322, and `net_cf` differs only by S's month 323,
    −£0.18.
  - T1 cuts that one twin at SEC's frame (`TWIN_FRAME_ENDS = {3: (323, 324)}`). It asserts
    both frames, and that S's month 323 opens above 0 and at or below the threshold.
- *The allowance's two roles.* S's `wd_allowance_rate` is both the statutory allowance and
  the anchor pattern's election. It is kept as one Reference, and `model-sec.md` says what
  follows from that: from the valuation date on, both accrue at it.
- *Domains.* `proj_len()` refuses 14 References off their domains, by name, NaN and ±inf
  included:
  - `surr_rate_cap` and `wd_cap_rate` in [0, 1];
  - `fund_return` and `inflation_rate` at −1 or more;
  - `return_shock` above −1, and `fund_return + return_shock` above −1;
  - `issue_age_min`, `allowance_years` and `omega_age`, whole numbers below `2**53`;
    `omega_age` is above `issue_age_min` and at most one past the table's last age;
  - the rest finite and 0 or more.
- *Computed values past their range are refused in their cells,* naming the References:
  - a surrender rate outside [0, 1], where S's monthly rate would be complex;
  - a fund that stops being finite, at `av_pp_at(t, "AFT_GROWTH")`, naming the return and
    the opening fund;
  - an allowance past the largest float.
- *Mortality refusals name the table's lines,* read once and unsorted, with S's sort
  applied after.
- *A row derived under a return of its own.* At S's References no state S reaches has the
  rider charging. Variant 7's 4% AMC is a table column, which `derived_refs` cannot set.
  - So point 12 is S's state at month 66 under a fund return of 0: a fund that has
    earned nothing since issue.
  - At today's 5% the rider charges for 36 months, 86.71 in all, and the death benefit
    pays the guarantee for 39.
  - With the zero return set on the model, the row continues S in every cell over the
    whole frame, 143 months. At today's return the paths part at month 0's growth, so only
    the opening state and the counts are compared.
- *The frame's last month* on an exhausted point, `result_uf` and `excess_gain_pp` are
  compared at a floor of 1e−9. The first closes on a subtraction that is 0 in exact
  arithmetic, as VA's does. S's excess gain is a year-end rounding.
- *The rules test follows calls that take no month* (DIA's `_months_read`), since every
  count reads `proj_len()` and through it the scan.
- *Smaller precisions.*
  - The roll-forward tolerance scales with `policy_count`.
  - `Data` holds `future_horizon_mth`.
  - The runner's block leaves out `av_pp`.
  - The every-state test sets aside the exhausted states S reaches and asserts that they
    are refused.

**Measured for K6.** On the shared 4-CPU Linux machine:
- the default module takes about 220 s, and the full grid about 630 s, of which the
  every-state test is about 330 s;
- a cold `net_cf` runs at most 10 cells beyond its one-a-month chain at 1,224 months.
  At the rider's longest cover, `check_unit_funding_resid` runs 12 and `death_strain` 11,
  inside 16.

At landing, `a15d894` ran its gate here in four jobs at once:
- uklib's suite: 1,936 passed and 330 skipped, in 794 s;
- the full grid: 374 passed, in 593 s;
- Term's `term_assurance` compile shard: 13 passed;
- `gen_sec_points.py --check` and `gen_sec_fingerprint.py --check`, for ULB_UK_SEC,
  CI_UK_SEC and Term_UK_SEC: current and reproduced;
- `check_sec_harness.py`: agreed;
- doccheck: 0 warnings;
- the scaffolding: 0 files.

In CI, the Tests workflow's run 48 on `a15d894` passed all 87 jobs, 1 h 22 min from
dispatch to the last:
- `sec_uk`'s three new legs: the full grid on Ubuntu in 10.7 min, and the core on Windows
  in 5.6 and on macOS in 2.8;
- CI's and Term's legs, both `cython_uk` shards and every uslib leg;
- the `test` job on Python 3.14 and Ubuntu: 7,044 passed and 105 skipped, in 37 min
  44 s, its harness step agreeing.

**Faults.** Each was injected into a copy of its own, and each run was held to the test
meant to catch it.
- The builder: 12, then 16, 10, 4 and 2 on the reworks, all caught.
- The review: 22. Its misses are all caught since `1320d00`:
  - a surrender rate refused at exactly 1, and the cap not net of the adviser charge,
    missed by every test;
  - every exhausted twin a month short, missed by T1;
  - the rider charge weighted by the issued count, missed by T4.
- The first verification: 14, of which 13 were caught. The miss, the allowance measured
  after month 0's accrual in both the generator and the model, is caught since `ab5b962`.
- The second verification: 18, all caught.

**Carried into M10 and after.**
- *M10, §6.6's C list,* and M2's compile form:
  - mortality as `[sex, age]` padded from 0, surrender by policy year, `gmdb_flag` int64;
  - `wd_pattern` as a code, the fund's four timings beside the counts' four, an inner
    width of 8, and `claims`' total left to right;
  - M22's guard on inflation's power, References printed as compiled, and the `idx` edges.

  `static_faults` lists 83 lines, none in `proj_len()`, all of them that list's work.
- *The stack* (K12, M2's record). ULB's longest cold chain runs about 1,236 cells: 1,224
  months and 12 beyond, twice Term's 611. On CI's Ubuntu runner, where Term's needed
  512 KiB to 1 MiB, it may need more than the 1 MiB thread the test asserts. M10
  measures it there first.
- *`omega_age` bounds the frame by the table's length, not the contract.* The C step's `t`
  cache needs a contract Reference for the largest `omega_age`, as Term's caches have.
- *The template, for every later product:*
  - K14 reaches every cumulative quantity S rebuilds with today's References, an accrued
    allowance as much as an increase or a review.
  - A column's instant on an anniversary is before month 0's own event.
  - A domain is stated on each combination a formula reads, not only on each Reference.
  - A computed value that can leave the floats is refused where it first does.
  - An int Reference is whole and below `2**53` from stage E.
  - T4 holds every flow non-zero on some point. A month-on restatement test catches a
    flow weighted by the count issued.
  - A twin's frame-end exemption is keyed by point and asserts both frames.
- *For the harness, at the close:* a row derived under References of its own records them
  nowhere in its table. `ULB-000004-M66` and CI's point 14 read like restatements at the
  shipped References, and only the specs and `model-sec.md` say otherwise. A `row_kind` or
  a column for them is a shared change, left for M15.

### 6.7 Pension annuity — `PA_UK_SEC` (E: M, C: M)

*Today:* the policy clock from the annuity start, new business only: no in-force column
and no in-force point. `proj_len() = max(horizon_mths(), guarantee_mths())`, 636 months on
the 65/62 joint points and 600 on the single lives. Survival and payments to date are keyed
by time point `k` from the start, RPI by anniversary count `a`, income by policy year `y`.
45 of its 67 cells share a name with `SPIA_US_SEC`'s, which is its chassis.

*E — the clock and the count:* SPIA's, with `stop_mth()` the policy-clock end of the
obligation and `proj_len() = stop_mth() - duration_mth_init()`, refusing a point at or past
the stop and a contract owing nothing. S weights every flow by a constant count, so
SPIA's count chassis carries over: `BEF_NB` a closed form, the count never decremented,
mortality per life. `pols_if` is a closing measure, `max(C, l_last(t + 1))` where a
dependant's pension is payable (0.99999965 at `t = 0` on points 2, 6 and 7), so the
registry marks `PA_UK_SEC` `closing_pols_if`, the key `SPIA_US_SEC` carries in uslib's, and
uklib's registry test confines it to `PA_UK_SEC`; PA's measure drops the dependant leg
where there is none.

*E — the opening state,* read off S's dependency graph at splice months on every point:
- each life's survival, `lives_if_init_1` and `lives_if_init_2` (SPIA's; 1 or 0 on a
  record, S's `lives_if(d, i)` on a splice); S's base is hard-coded;
- `cum_annuity_all_init`, the survival-weighted payments to date, which last-survivor
  value protection reads and `result_pols()` publishes on every point: path-dependent, an
  expectation in S and on a splice, what was paid on a record;
- on RPI-linked escalation (`lpi5`, `rpi_catchup`) only: the income of the policy year
  under way, taken before any month-0 anniversary escalation, and the ratchet's state,
  `rpi_peak_init` relative to the latest index; and the as-if-alive annuitant payments to
  date, `cum_annuity_pp_init`, where value protection is on the first death. On level and
  fixed escalation all three are deterministic, re-derived by SPIA's loop at the
  valuation date's key, bit for bit;
- S's scenario death months, kept policy months, each life's status checked against them
  in `Data`, as SPIA's are.

S's `annual_income_init()`, which returns the first year's income, is renamed
`annual_income_first()`, as SPIA's was, so that D6's name is free. `vp_balance`, the months
since a payment, the guarantee months left and the next payment month follow from these.

*E — the RPI clock.* D7 puts an index path on the valuation clock, the history before the
valuation date being opening state, as SPIA's CMT change is. S's `rpi_rate` is one flat
rate, read as `(1 + r)^a` from the start by `rpi_catchup` and as the rate itself by
`lpi5`; a flat rate is the same on either clock, so SEC keeps it a flat Reference, the
assumed RPI from the valuation date on, and carries the history in the columns above.
No path is introduced (§9, item 4). The ratchet's catch-up branch, unreachable in S on a
flat rate, gets goldens of its own on a column that puts the peak above the index. The
six-month reference lag of the source contract is not modelled, as in S.

*E — rebase:* `is_payment_mth`'s `(t + 1) % step` and `t % step`; the months since a
payment; the guarantee's end in `certain_floor` and `overlap_gate`; the survival and
payments-to-date bases at `k <= 0`; the scenario step `k > d` and its twin in
`check_lives_roll_fwd_resid`, whose product from 0 becomes a rebuild from `t_entry()`;
`annuity_pp`, `payment_factor` and `dependant_factor` read at `k - 1` with a time point as
`t`; `vp_balance(k)` fed valuation times; `annual_income`'s base at `y <= 1` and
`rpi_index(0)`; and the frame counted from the start. `cum_annuity_pp(k, kind)` parts by
clock: the annuitant's schedule keeps `k`, the policy clock, and the survival-weighted
total becomes a `t`-keyed cell, as does `vp_balance`. The one far read,
`claims(t, PROP)`'s scan to the next payment month, becomes SPIA's closed form on the
policy month, its instalment `A(policy_year(t)) / m`. Expense inflation,
`(1 + π)^(policy_year - 1)`, moves onto `t`; improvement is dated by the calendar through
`start_year + duration` and stays on the policy clock (D7, as SPIA's).

*E — caps and new business.* `q = table rate × α × (1 − f)^(c − c0)`, then
`min(1.0, θ × q)` in S, the bound first; SEC writes `min(θ × q, 1.0)`. It binds on point 8
(θ = 1.35) at `t = 576..599`. New business is an annuity commencing in the month, with no
premium and no acquisition, as in S; future new business within 120 months has no blocker,
`start_year` being the commencement year.

*Splice months:* 1, 2, 3 (quarterly arrears); 11 to 13 and 23 to 25, the anniversaries,
also under `rpi_rate` of 0.08 and −0.02, where the LPI cap and floor bind and the ratchet
freezes; 15, 16, 17 around the scenario death (value protection and the proportionate
payment at 16, the dependant's first payment at 17); 119 to 122, the guarantee's end;
101 and 102, 170 and 171 (value protection running out on first and last death); 575 and
576 (point 8's cap); 599 and 600 (the older life past ω); 635; and 24 and 120 on the table
basis. Variants: advance timing with value protection, semi-annual, annual and quarterly in
advance, the dependant dying first, both lives dead with and without a guarantee, a
guarantee past the age stop, a rated joint life.

*C:* SPIA's, as uslib's M23 settled it. `mort_table` to `[schedule, age]`, padded from 0, each sex's own
extents (50 to 115), through one age reader guarded by `is_active`; `timing`,
`mort_basis`, `vp_basis` and `escalation_type` decoded in Phase 1, as SPIA's were; the
three bool columns to int64; `claims(t, kind)` to int kinds and a total, left to right (at
most two kinds non-zero together); `horizon_mths`'s list to one comparison; the blank
dependant and death columns to a value, a flag and a −1 sentinel (R8); the label
accessors reporting cells, `payment_timing` returning `timing` and `sex(life)`
`annuitant_sex` or `dependant_sex` through `"reporting_columns"`. Caches by uslib M23's rule:
S projects any age on the scenario basis, so `issue_age_min` 0, ω 115 and the 120-month
horizon give `t` 1,502, `k` 1,382, `y` and `a` 117, `x` 116, each 2-D cache 3 wide;
`proj_len()` refuses a negative age and a guarantee past 1,380 months, which S accepts.

*Risk:* the longest cold chain is about 1,510 levels, against SPIA's 1,453, whose margin
under gcc in a 1 MiB stack was 1.33 to 1.6 times. The C step measures it first, and blocks
the survival recursion by year if the margin is gone.

*S defects found*, which `Data` refuses in SEC (D6, R6): a blank bool column read as
True through `bool(nan)`; `death_mth` truncating a fraction and reading a negative month
as a life that never dies; `int()` truncating ages, frequency, guarantee and `start_year`;
no bounds on ages, the guarantee, `vp_pct`, the rating or the dependant's share.

---

## 7. Order and milestones

**The template first.** Term goes through both of its steps before any other product
starts (M1, M2). It has the late frame and an in-force twin at offset 60, the count chain,
acquisition and commission, joint lives, and a small companion, the waiver pipeline, which
puts D8's companion machinery through uklib's harness before IP needs it at scale. What it
finds that binds later products goes into its record, under *Carried into M3 and after*,
as uslib's M1 and M14 records did.

**Then two streams,** one product at a time in each, each product E then C (U2):

- **Protection:** CI → WOL → IP (M3–M8). CI is on Term's chassis; WOL brings the second
  count strand; IP, the largest and least certain (K11), goes last.
- **Savings and annuity:** ULB → PA → WP (M9–M14). ULB is the smallest. Its inline fund
  chain and its exhaustion threshold are the forms WP's units chain and its
  `fund_exhaust_mth` take. PA stands on uslib's SPIA chassis. WP, the widest, goes last.

**Landing** is uslib's (§5.3 there). A product adds what it needs to the shared files
(`uk_sec_support.py`, `uk_registry.py`, `conftest.py`, the two conventions suites, uklib's
`index.md`, the workflow) where it belongs, and reformats nothing already there. Each step
is rebased onto the branch as it stands, and the gate is run on the rebased tree before
the step is pushed.

**How each step is built.** One agent builds a step; a second reviews it against this plan,
USLIB-SEC-PLAN.md's rules and the tests, and injects faults to check that the tests catch
them, as uslib's later milestones did ("one merged reviewer", from its M16). Each step's
record is appended to its product's note: what exists now, the departures and precisions,
what was measured (K6) and the faults injected.

| # | Milestone | Content | Gate |
|---|---|---|---|
| M0 | Phase 0 | §3: tools, registry, harness and its check, conventions, configuration, CI; the S-side items of §9 items 6 and 9 | every S model of both libraries green unchanged; uslib's SEC modules and its `--check` tools unchanged; doccheck zero; a dispatched run green, `cython_uk`'s `toolchain` legs among it |
| M1 | Term E | §4, §5; `Term_UK_SEC` at stage `"E"`, the waiver pipeline's companion; the fingerprint frozen after | T1–T6 and the conventions green; the uklib suite; doccheck zero; `gen_sec_points.py --check`; `sec_uk`'s Term legs green |
| M2 | Term C | stage `"EC"`, `sample_sec.py`, `spec_sec.py`, the compile tests, Term's `cython_uk` shard | C1–C5 green on Linux and Windows; C6 in `model-sec.md`; `gen_sec_fingerprint.py --check` |
| M3, M4 | CI E, C | as M1, M2 | as M1, M2 |
| M5, M6 | WOL E, C | as M1, M2 | as M1, M2 |
| M7, M8 | IP E, C | as M1, M2; the cohort companion, and at C the 2-D cohort recursion | as M1, M2 |
| M9, M10 | ULB E, C | as M1, M2; the depletion threshold | as M1, M2 |
| M11, M12 | PA E, C | as M1, M2; the stack measured first at C | as M1, M2 |
| M13, M14 | WP E, C | as M1, M2; at E, the bond variant that future rows and T1 need | as M1, M2 |
| M15 | Close | uklib's `index.md` speed table, README and MERGE lines; the matrix measured (K6); the carried items settled | a dispatched run green over every job |

M1 and M2 run alone. M3–M8 and M9–M14 run as the two streams. A milestone whose gate is met
on Linux alone is done on Linux, and stays open until `cython_uk` has run on Windows
(uslib's §6.3).

---

## 8. Risks

uslib's K1–K9 hold here as written. K1 (modelx-cython 0.1.0, pinned), K2 (memory), K3
(knife edges), K7 (tests that need modelx) and K8 (packaging: `MANIFEST.in` prunes
`*_nomx*`, a `setup.py` beside a model and `build/`) need nothing new. The tests that need
modelx are many here too: every uklib S module reassigns References after a call and
clears, swaps `Data`'s file References, and expects `FormulaError`. They stay in C1, and
every SEC test sets its References on a model just read (K7). What uklib changes or adds:

- **K4 — Future new business on market products.** Lighter than uslib's: ULB's fund return
  and WP's fund return and bonus rate are flat levels, with no path to re-base. WP's one
  new-business S row is a conventional endowment, which is closed to new business, so its
  future rows and T1 on a bond need a bond variant (§6.5). D4's fallback, a horizon of 0
  with its own message, is there for a product where future new business proves
  disproportionate.
- **K5 — Wide interfaces.** WP opens on eight columns. IP's claim cohorts and Term's waiver
  pipeline are companions. PA carries up to seven columns on RPI-linked escalation. Each is
  documented in `model-sec.md` with the instant it is measured at, and an extract carrying
  every amount to the cent is read (D6).
- **K6 — CI time and concurrency.** uslib's Tests run 33 was 74 jobs. U7 adds 21 legs to
  `sec_uk` (7 modules × 3 systems) and 16 to `cython_uk` (8 shards × 2 systems): 111 jobs
  at the close, against a concurrency limit that queues the rest. The `test` job grows by
  uklib's SEC conventions and harness tests alone (G8). Each step records its module's
  default and full-grid times against U6's five minutes, and its legs' times in CI.
- **K10 — Two harnesses drift.** U3's check fails CI on any shared function that differs.
  What it cannot stop is a fix one library needs and the other does not; such a
  divergence is listed in the tool with its reason, and reviewed like code.
- **K11 — IP's cohorts in C.** No uslib model has a state of a length the point decides.
  IUL's ladder is twelve slots, fixed by the contract; IP's cohorts reach 624. At one inner
  width per model, the `[t, z]` cache would make IP's struct about 11 MB a point (§6.3).
  The representation is chosen at M8, recommended by §9 item 11, and IP goes last in its
  stream.
- **K12 — PA's chain on the stack.** PA's longest cold chain is about 1,510 cells, against
  `SPIA_US_SEC`'s 1,453, whose margin under gcc in a 1 MiB stack was 1.33 to 1.6 times.
  M12 measures it before anything else, and blocks the survival recursion by year if the
  margin is gone.
- **K13 — S's bound-first caps** (G5). The SEC models cap with the bound second whatever S
  does (§4). §9 item 6 asks whether S is fixed first, as uslib's were.
- **K14 — History the splice cannot see** (G3). S recomputes RPI increases and premium
  reviews from flat References. A model that dropped the history columns would pass T2,
  since S and the splice recompute them alike. So each history column gets a test of its
  own: a point whose column departs from what the References would give is projected
  through it.

## 9. Decisions to confirm

Each had a recommendation; uslib's §8.2 settled the same questions for uslib. All eleven
were confirmed on 2026-11-22, as recommended.

1. **Sequence (U2).** Each product E then C, back to back, after Term's two steps as the
   template, rather than all E before any C. *Recommended.*
2. **The harness (U3).** A copy under a library-unique name, `uk_sec_support.py`, held to
   uslib's by `tools/check_sec_harness.py` in CI. *Recommended.*
3. **Future new business (D4).** On all seven, with a horizon of 120 months and D4's
   per-product fallback; WP's future rows from a bond variant issued at the valuation
   date. *Recommended.*
4. **The clocks of inputs (D7).** Expense inflation moves to the valuation clock on all
   seven. So do CI's morbidity trend and WOL's mortality improvement, which S runs from
   issue, its projection start, as uslib moved ULSG's improvement. RPI stays one flat
   Reference, the assumed rate from the valuation date, with the increases already given
   carried as opening state (item 5). PA's improvement, dated by the calendar from the
   annuity's start, stays on the policy clock, as SPIA's did. *Recommended.*
5. **History as opening state** (G3, K14). The RPI increases and premium reviews a policy
   has already had are carried as `_init` columns, so that a real extract's amounts in
   force are what is projected, rather than recomputed from issue at today's References as
   S does. *Recommended.*
6. **S-side fixes, in M0, in commits of their own** (G5, G6):
   - every uklib S model's caps on mortality and morbidity (death, critical illness,
     inception) put their bound second, `min(q, 1.0)`;
   - S's uncapped rates of those kinds are capped wherever that changes no shipped number,
     each change shown by a test of every cached value, bit for bit;
   - `tests/test_mortality_caps_uk.py`, uslib's test, on uklib's models;
   - lapse and recovery bounds keep S's order;
   - each uklib product module's CSV-set test becomes uslib's subset form, so that an SEC
     table can sit beside the model.

   The other S defects (G9) are fixed in the SEC models only, as uslib's were.
   *Recommended.*
7. **Test depth (U6).** uslib's settled forms from each product's first commit, with a core
   by default and the full grid under `UKLIB_SEC_FULL=1`. *Recommended.*
8. **CI (U7).** Two new jobs, `sec_uk` and `cython_uk`, rather than a library axis on
   uslib's. *Recommended.*
9. **WP's chassis key** (G7). In M0, a commit of its own renames the out-of-scope chassis
   value `SF_prufund` to `SF_smoothed`: in `WP_UK_S`'s refusal message, the technical
   notes' enum and `test_with_profits_uk.py`. The prose, which describes the source,
   keeps the name. *Recommended*, as uslib renamed RILA's and VA's keys at their landings.
10. **ULB's exhaustion** (§6.6). `VA_US_SEC`'s depletion threshold, a recorded departure
    from S's exact test of 0. *Recommended.*
11. **IP** (§6.3). The in-claim twins take a policy clock of `12n` months,
    `n ≥ ⌈(z0 + 1) / 12⌉`. At M8, the timings and kinds become 1-D cells, so that only the
    cohorts carry the 626-wide cache, rather than pooling the cohorts past the termination
    table's last duration. *Recommended.*
