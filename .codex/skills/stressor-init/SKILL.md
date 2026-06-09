---
name: stressor-init
description: Initialize and preflight-check the full stressor workflow before stressor-try by orchestrating small tests, validator, brute oracle, checker, and testlib-based large generators. It verifies component contracts, reports blockers, and prepares the project for stressor-try and stressor-stress.
---

# Stressor Init

## Purpose

This skill initializes a programming contest problem for the stressor workflow.

It prepares and checks everything needed before running `stressor-try`.

It orchestrates these existing skills:

- `stressor-gen-small`
- `stressor-vali`
- `stressor-brute`
- `stressor-checker`
- `stressor-gen-large`

It also checks whether the project is ready for:

- `stressor-try`
- `stressor-stress`
- large generator based testing

This skill is a preflight checker, bootstrapper, and gatekeeper.

It must not write an optimized attempt.

It must not run `stressor-try`.

It must not silently overwrite existing components.

## Target State

A fully initialized project should have:

```text
tests/
├── small/
│   ├── 01
│   ├── 02
│   └── ...
├── strong/
│   └── ...
└── large/
    └── ...

validators/
├── val.cpp
└── VALIDATION_SCOPE.md

solutions/
├── brute.cpp
├── BRUTE_SCOPE.md
└── BRUTE_LIMITS.json

checkers/
└── checker.cpp

generators/
├── gen_large.cpp
├── gen_max.cpp
├── gen_all_large.sh
└── README.md

scripts/
├── validate_small.sh
└── run_brute_on_tests.sh

reports/
└── init_report_XXXX.md

lightcp/problems/<pid>/
├── config.yaml
├── statement.txt
├── checker.cpp
└── testdata/
    ├── small_0001.in
    ├── small_0001.ans
    └── ...
```

`tests/large/` is temporary. It may be empty after initialization.

The `lightcp/problems/<pid>/` directory is the LightCPVerifier-compatible export mirror. The `<pid>` segment is the problem id chosen by `--pid`, or otherwise inferred from the problem statement filename / containing directory / current working directory name. The export mirror is built and refreshed by Stage 6.5 below.

## Scope

Allowed output when this skill is invoked:

```text
tests/small/
tests/strong/
tests/large/

validators/
solutions/
checkers/
generators/
scripts/

reports/init_report_XXXX.md
```

Only through the component skills or necessary orchestration.

Forbidden output unless explicitly requested:

```text
solutions/optimize_XXXX.cpp
solutions/notes_XXXX.md
outputs/optimized/
answers/
official final data package
```

This skill must not write optimized solutions.

This skill must not create official answers.

This skill must not silently overwrite user files.

## Invocation

Preferred invocation:

```text
$stressor-init path_to_problem_statement
```

Optional arguments:

```text
$stressor-init path_to_problem_statement --num-small 15 --num-large 10
$stressor-init path_to_problem_statement --check-only
$stressor-init path_to_problem_statement --force-regenerate small
$stressor-init path_to_problem_statement --force-regenerate validator
$stressor-init path_to_problem_statement --force-regenerate brute
$stressor-init path_to_problem_statement --force-regenerate checker
$stressor-init path_to_problem_statement --force-regenerate large-generators
```

Defaults:

* `--num-small`: if omitted, init picks a default of 12 to 20 (chosen by problem complexity) and forwards it to `stressor-gen-small` as `--num-tests N`.
* `--num-large`: 6 to 12 generator verification tests
* `--check-only`: false
* `--force-regenerate`: none

`--num-small N` is **not** an implicit hint — init forwards the exact value to `stressor-gen-small` via its `--num-tests N` parameter (see Stage 1).

Treat the first positional argument as `path_to_problem_statement`.

Read the statement from that path first.

If the argument is a directory, search for likely statement files:

* statement.md
* statement.pdf
* README.md
* problem.md
* problem.tex
* statements/
* statement/

Prefer an explicitly provided statement file over directory search.

## Official Sample Discovery

After resolving the statement directory, search for official sample files under the statement directory.

The preferred statement directory is:

```text
{problemname}/statement/
```

Official sample file pairs may include:

```text
*.in  + matching *.out
*.input + matching *.output
sample*.in + sample*.out
example*.in + example*.out
ex*.in + ex*.out
```

Examples:

```text
QOJ464/statement/ex_prefix1.in
QOJ464/statement/ex_prefix1.out
```

Pairing rule:

* A sample input file `X.in` pairs with `X.out`.
* A sample input file `X.input` pairs with `X.output`.
* Preserve lexical order when listing sample pairs.
* Do not guess outputs if no matching output file exists.
* If an input sample has no output sample, it may still be used for validator checks, but not for brute-vs-official-output checks.
* If an output sample has no matching input sample, report it as orphaned and do not use it.

Sample files are official statement content.

They may be read by skills that are allowed to read the statement bundle.

They are not generated tests.

They should not be modified.

Forbidden:

* Do not copy statement sample files into tests/strong automatically.
* Do not overwrite statement sample files.
* Do not treat generated tests as official samples.
* Do not infer hidden rules only from sample outputs.

## Operating Modes

### Default mode

In default mode:

* inspect existing components
* reuse components that pass contract checks
* create missing components by invoking or following the appropriate component skill
* repair incomplete components through the appropriate component skill when possible
* never overwrite existing files silently
* stop on blockers

### Check-only mode

If `--check-only` is provided:

* inspect existing components only
* do not create new files
* do not repair files
* do not regenerate anything
* produce readiness report only

### Force-regenerate mode

If `--force-regenerate COMPONENT` is provided:

Allowed components:

* `small`
* `validator`
* `brute`
* `checker`
* `large-generators`

Rules:

* regenerate only the specified component
* do not blindly regenerate everything
* preserve unrelated files
* report what will be replaced or left untouched
* do not delete user data unless explicitly allowed

## Component Skills

Before doing setup, check that these component skills exist:

```text
.codex/skills/stressor-gen-small/SKILL.md
.codex/skills/stressor-vali/SKILL.md
.codex/skills/stressor-brute/SKILL.md
.codex/skills/stressor-checker/SKILL.md
.codex/skills/stressor-gen-large/SKILL.md
```

If a required component skill is missing:

* stop
* report the missing skill
* do not attempt to recreate it inside this skill

## testlib Requirement

These stages require `testlib.h`:

* `stressor-vali`
* `stressor-checker`
* `stressor-gen-large`

Before those stages, search for project-local `testlib.h`.

Acceptable locations include:

```text
./testlib.h
./third_party/testlib/testlib.h
./third_party/testlib.h
./lib/testlib.h
./generators/testlib.h
./checkers/testlib.h
../testlib.h
../third_party/testlib.h
../third_party/testlib/testlib.h
../../third_party/testlib.h
../../third_party/testlib/testlib.h
```

The last entries cover multi-problem layouts where `testlib.h` is shared one or two directories above the current problem.

If `testlib.h` is missing:

* report clearly
* show expected locations
* do not download it automatically
* do not continue to validator/checker/large generator stages unless the user explicitly provides it

You may show this command to the user, but do not execute it unless explicitly asked:

```bash
mkdir -p third_party
git clone --depth=1 https://github.com/MikeMirzayanov/testlib.git third_party/testlib
```

## Directory Conventions

This workflow uses:

```text
tests/small/   small handwritten legal corner cases from stressor-gen-small
tests/strong/  saved failing cases and important manually curated cases
tests/large/   temporary generated large tests
```

`stressor-gen-small` should write directly into `tests/small/`.

`stressor-gen-large` should write temporary generated data into `tests/large/`.

`stressor-stress` promotes failing generated large tests into `tests/strong/`.

Do not overwrite existing `tests/strong`.

Do not delete user-created tests.

## LightCPVerifier Compatibility

This workflow supports exporting judge-ready assets to a LightCPVerifier-compatible problem directory.

The target directory is:

```text
lightcp/problems/<pid>/
```

Expected structure:

```text
lightcp/problems/<pid>/
├── config.yaml
├── statement.txt
├── checker.cpp
└── testdata/
    ├── small_0001.in
    ├── small_0001.ans
    ├── small_0002.in
    ├── small_0002.ans
    ├── strong_0001.in
    ├── strong_0001.ans
    └── ...
```

Rules:

* `statement.txt` is the plain-text problem statement used by LightCPVerifier.
* `checker.cpp` is copied from `checkers/checker.cpp`.
* `testdata/*.in` are input files.
* `testdata/*.ans` are jury answer files generated by `solutions/brute.cpp`.
* Never generate `.ans` files from optimized attempts.
* Never use `solutions/optimize_XXXX.cpp` as jury answer generator.
* The exported `config.yaml` must explicitly list cases when possible, instead of relying only on `n_cases`.
* The exported package should be suitable for LightCPVerifier `/problem/setup` and `/submit` workflows.

Preferred `config.yaml` shape:

```yaml
type: default
time_limit: 1s
memory_limit: 256m
checker: checker.cpp
filename: main.cpp
subtasks:
  - score: 100
    cases:
      - input: small_0001.in
        output: small_0001.ans
      - input: small_0002.in
        output: small_0002.ans
```

If the problem has known time or memory limits in the statement, use them.

If not known, use conservative defaults and report assumptions:

```yaml
time_limit: 2s
memory_limit: 256m
```

The LightCPVerifier export is a mirror for judge evaluation.

The source-of-truth development directories remain:

```text
tests/small/
tests/strong/
tests/large/
solutions/
checkers/
validators/
generators/
```

`stressor-init` is the gatekeeper of LightCPVerifier package readiness: Stage 6.5 builds and refreshes `lightcp/problems/<pid>/`, and Stage 7 decides whether `Ready for LightCPVerifier` is YES or NO.

### Official Sample Files in LightCPVerifier Export

Official sample files under `statement/` are export candidates, but `.ans` files for LightCPVerifier should normally be generated by `solutions/brute.cpp`.

Do not blindly use `statement/*.out` as exported `.ans`.

Allowed uses of official sample `.out`:

* validating brute output through checker
* sanity checking checker behavior
* documenting sample consistency

When exporting official samples into `lightcp/problems/<pid>/testdata`, prefer:

```text
statement/ex_prefix1.in -> testdata/sample_0001.in
brute output             -> testdata/sample_0001.ans
```

Then optionally verify:

```bash
checker sample_0001.in sample_0001.ans original_ex_prefix1.out
```

if the checker supports it.

Stage 6.5 must not auto-promote `statement/*.out` into `testdata/*.ans` without an explicit user request. The default behavior is: when samples are exported, the export stage copies `statement/*.in` to `testdata/sample_00NN.in` and runs `solutions/brute.cpp` on each input to produce the matching `testdata/sample_00NN.ans`. The original `statement/*.out` may then be used by the optional cross-check above.

## Component Status Values

Every component must be classified as one of:

```text
READY
MISSING
INCOMPLETE
BROKEN
FAILED_CHECK
SKIPPED
BLOCKED
```

Definitions:

* `READY`: required files exist and contract checks passed
* `MISSING`: required files do not exist
* `INCOMPLETE`: some required files exist but others are missing
* `BROKEN`: files exist but compile/run/basic checks fail
* `FAILED_CHECK`: semantic or workflow checks failed
* `SKIPPED`: intentionally not run due to mode or missing prerequisite
* `BLOCKED`: cannot continue because earlier dependency failed

## Required Workflow

### Stage 0: Inspect project

Read the problem statement.

Inspect:

```text
tests/
validators/
solutions/
checkers/
generators/
scripts/
reports/
.codex/skills/
```

Determine existing components:

* small tests
* validator
* validation scope
* brute
* brute scope
* brute limits
* checker
* large generators
* generator README
* large generator script

Produce an initialization plan before making changes.

Use this table:

```text
Component | Existing? | Status | Action | Required skill
small tests | yes/no | ... | reuse/generate/check | stressor-gen-small
validator | yes/no | ... | reuse/create/check | stressor-vali
brute | yes/no | ... | reuse/create/check | stressor-brute
checker | yes/no | ... | reuse/create/check | stressor-checker
large generators | yes/no | ... | reuse/create/check | stressor-gen-large
```

### Stage 1: Small tests contract check

Goal:

```text
tests/small/
```

Required contract:

* `tests/small/*` exists
* tests are small and readable
* tests were generated or verified according to `stressor-gen-small`
* every test passed three independent legality-review subagents
* if validator already exists, every small test passes validator

If existing `tests/small/` has files:

* inspect them
* reuse if they appear complete and were previously reviewed
* do not overwrite unless explicitly requested

If no small tests exist and not in check-only mode, invoke or follow:

```text
$stressor-gen-small path_to_problem_statement --num-tests N --out-dir tests/small

Generate N small legal corner-case tests into tests/small. Do not use testlib. Every test must pass three independent legality-review subagents (LEGAL × 3) before being accepted. Do not create generator/validator/brute/checker.
```

`N` is the value of init's `--num-small`. If the user did not provide `--num-small`, pick a default between 12 and 20 based on problem complexity and use that as `N`.

Fail-fast gate:

If small tests are not READY, stop initialization.

### Stage 2: Validator contract check

Goal:

```text
validators/
├── val.cpp
└── VALIDATION_SCOPE.md

scripts/
└── validate_small.sh
```

Required contract:

* `validators/val.cpp` exists
* `validators/VALIDATION_SCOPE.md` exists
* `scripts/validate_small.sh` exists
* `val.cpp` compiles
* `VALIDATION_SCOPE.md` explains:

  * supported input range
  * exact checks
  * partial checks
  * unchecked constraints
  * complexity
  * notes for `stressor-gen-large`
* validator accepts all `tests/small/*`

If validator exists:

* inspect it
* compile it
* run it on `tests/small`
* if `VALIDATION_SCOPE.md` is missing, mark INCOMPLETE and repair via `stressor-vali`

If validator is missing and not in check-only mode, invoke or follow:

```text
$stressor-vali path_to_problem_statement tests/small
```

If any small test fails validator:

* triage according to `stressor-vali`
* determine whether validator is too strict, small test is invalid, or statement is ambiguous
* do not blindly weaken validator
* do not continue until resolved

Fail-fast gate:

If validator is not READY, stop initialization.

### Stage 3: Brute oracle contract check

Goal:

```text
solutions/
├── brute.cpp
├── BRUTE_SCOPE.md
└── BRUTE_LIMITS.json

scripts/
└── run_brute_on_tests.sh
```

Required contract:

* `solutions/brute.cpp` exists
* `solutions/BRUTE_SCOPE.md` exists
* `solutions/BRUTE_LIMITS.json` exists
* `scripts/run_brute_on_tests.sh` exists
* brute compiles
* brute runs on `tests/small`
* `BRUTE_SCOPE.md` documents algorithm, correctness, complexity, limitations
* `BRUTE_LIMITS.json` is valid JSON and gives machine-readable runnable limits
* brute does not silently produce unreliable output on unsupported ranges

If brute exists:

* inspect it
* compile it
* run it on `tests/small`
* inspect `BRUTE_LIMITS.json`

If brute is missing or incomplete and not in check-only mode, invoke or follow:

```text
$stressor-brute path_to_problem_statement tests/small
```

If brute fails on small tests:

* classify as brute bug, unsupported input, invalid test, or ambiguity
* do not continue until resolved

Fail-fast gate:

If brute is not READY, stop initialization.

### Stage 4: Checker contract check

Goal:

```text
checkers/
└── checker.cpp
```

Required contract:

* `checkers/checker.cpp` exists
* `testlib.h` can be found
* checker compiles
* checker invocation must be:

```bash
./build/checker input_file participant_output jury_answer
```

For future stress:

* participant output = optimized output
* jury answer = brute output

Sanity check:

If brute outputs on small tests exist, run checker with brute output as both participant and jury:

```bash
./build/checker tests/small/01 outputs/brute/small/01.out outputs/brute/small/01.out
```

If checker fails on brute-vs-brute:

* checker is wrong or brute output is invalid
* do not continue until resolved

If checker is missing and not in check-only mode, invoke or follow:

```text
$stressor-checker path_to_problem_statement
```

Fail-fast gate:

If checker is not READY, stop initialization.

### Stage 5: Large generator contract check

Goal:

```text
generators/
├── gen_large.cpp
├── gen_max.cpp
├── gen_all_large.sh
└── README.md
```

Required contract:

* main generator files exist
* `generators/gen_all_large.sh` exists
* `generators/README.md` exists
* generators use testlib
* generators call `registerGen(argc, argv, 1)`
* generators use explicit seed and parameters
* README documents usage, modes, parameters, examples
* generators respect statement constraints
* generators respect `validators/VALIDATION_SCOPE.md`
* generator pilot tests pass three-way legality review
* if validator exists, pilot tests pass validator

If large generators exist:

* inspect README
* inspect script
* run only safe pilot/verification if appropriate
* do not overwrite existing generator files unless explicitly requested

If large generators are missing and not in check-only mode, invoke or follow:

```text
$stressor-gen-large path_to_problem_statement --num-tests N --out-dir tests/large

Prepare large data generators. Generate only safe initialization-level pilot or verification data. Respect validators/VALIDATION_SCOPE.md and solutions/BRUTE_LIMITS.json when choosing pilot or verification sizes. Use explicit seeds and parameters. Document all generator usage in generators/README.md.
```

Important:

Initialization should not generate huge data by default.

It should generate only enough pilot/verification data to prove that generators compile, produce valid data, and pass validator.

If verification data is created under `tests/large`, clean it at the end of this stage unless the user asks to keep it.

Large generator readiness affects large stress availability.

If large generator fails but small tests, validator, brute, and checker are READY:

* `Ready for stressor-try` may still be YES
* `Ready for stressor-stress` may be YES for small/strong only
* `Large generation ready` must be NO

### Stage 6: Integration sanity check

If all core components exist:

* compile validator
* compile brute
* compile checker
* run validator on `tests/small`
* run brute on `tests/small`
* run checker brute-vs-brute on at least one small test, preferably all small tests if cheap

If an optimized solution already exists, do not automatically run `stressor-stress` unless the user explicitly asks.

Since this skill is meant before `stressor-try`, optimized solution is not required.

### Stage 6.5: Build LightCPVerifier package mirror

This stage runs after the validator, brute, checker, and large-generator contract checks (Stages 2–5) and after the Stage 6 integration sanity check. It builds (or refreshes) the LightCPVerifier-compatible export mirror at:

```text
lightcp/problems/<pid>/
```

#### Resolving `<pid>`

* If the user passed `--pid PID`, use `PID` verbatim.
* Otherwise infer `<pid>` from, in order:
  1. the problem-statement file's basename (e.g. `QOJ464.md` → `QOJ464`);
  2. the problem-statement file's containing directory name;
  3. the current working directory name.
* Report the resolved `<pid>` in the final response.

#### Resolving the base directory

* If `--lightcp-dir DIR` is given, use `DIR/<pid>/`.
* Otherwise use `lightcp/problems/<pid>/`.

#### What this stage does

1. Create or refresh `lightcp/problems/<pid>/`.
2. Write `lightcp/problems/<pid>/statement.txt` as a plain-text rendering of the problem statement.
3. Write `lightcp/problems/<pid>/config.yaml` with the shape described in the "LightCPVerifier Compatibility" section. The case list must be enumerated explicitly.
4. Copy `checkers/checker.cpp` to `lightcp/problems/<pid>/checker.cpp` verbatim.
5. Collect inputs from `tests/small/` and `tests/strong/` for export.
6. Optionally, collect a user-selected subset of `tests/large/` (only when the user explicitly requested to keep specific generated large tests as judge cases; otherwise skip large tests).
7. For every collected input, generate the matching `.ans` by running `solutions/brute.cpp` (the only authorized jury-answer source).
8. For every exported case, run `checkers/checker.cpp` in brute-vs-brute mode:

```bash
checker testdata/<name>.in brute.out brute.out
```

   to confirm the checker is consistent with itself on the brute's own output.

9. If `validators/val.cpp` exists, run it on every exported `*.in`. Every exported input must pass the validator.

#### Naming rules

```text
tests/small/01   -> lightcp/problems/<pid>/testdata/small_0001.in
tests/small/02   -> lightcp/problems/<pid>/testdata/small_0002.in

tests/strong/01  -> lightcp/problems/<pid>/testdata/strong_0001.in
tests/strong/foo -> lightcp/problems/<pid>/testdata/strong_0002.in
```

Answer file names mirror the input file basename:

```text
small_0001.in  -> small_0001.ans
strong_0001.in -> strong_0001.ans
```

If kept large tests are exported (only on explicit user request):

```text
tests/large/<kept>  -> lightcp/problems/<pid>/testdata/large_00NN.in
                       (matching large_00NN.ans produced by brute)
```

#### `config.yaml` must enumerate cases

The exported `config.yaml` must explicitly list every exported case. Example:

```yaml
type: default
time_limit: 1s
memory_limit: 256m
checker: checker.cpp
filename: main.cpp
subtasks:
  - score: 100
    cases:
      - input: small_0001.in
        output: small_0001.ans
      - input: strong_0001.in
        output: strong_0001.ans
```

Do not rely solely on `n_cases` or a directory-glob convention; the explicit enumeration is what the rest of the pipeline reads.

#### Required `config.yaml` fields and fallbacks

`config.yaml` must include LightCPVerifier + go-judge sandbox parameters, with conservative fallbacks recorded under `x-stressor.config_fallbacks` whenever the statement is silent.

| field | source | fallback | notes |
|---|---|---|---|
| `type` | statement (interactive / SPJ / default) | `default` | If statement requires interactive judging and this workflow does not support it, do not silently set `default` — instead report a blocker. |
| `time_limit` | statement | `2s` | Record the fallback in `x-stressor.assumptions` and `x-stressor.config_fallbacks`. |
| `memory_limit` | statement | `256m` | Same recording rule. |
| `checker` | `checkers/checker.cpp` (copied into package as `checker.cpp`) | n/a — must exist | If checker is missing, write config as incomplete and set `Ready for LightCPVerifier: NO`. |
| `filename` | statement (rare) | `main.cpp` | Submitted source filename inside the judge environment. |
| `subtasks` | computed | one subtask `score: 100` | Use explicit `cases:` enumeration. |
| `cases` | from `testdata/` | n/a | Each entry must list `input` and `output`, both relative to `testdata/`. Do not rely on `n_cases`. |

If the statement is incomplete, do not invent precise official constraints. Use the fallback values above and record every assumption:

```yaml
x-stressor:
  assumptions:
    - "time_limit not specified in statement; using fallback 2s"
    - "memory_limit not specified in statement; using fallback 256m"
  config_fallbacks:
    time_limit: 2s
    memory_limit: 256m
    type: default
    filename: main.cpp
```

If the statement specifies time or memory limits, use them. Otherwise default to:

```yaml
time_limit: 2s
memory_limit: 256m
```

and record the assumption in the init report.

#### Handling brute failures during export

For every collected input, brute may fail because the input is outside `solutions/BRUTE_LIMITS.json`, brute crashes, or brute times out.

Handling rules:

* Do **not** export that case.
* Record the case in the init report's `skipped cases` list together with the reason.
* If the case originated from `tests/strong/`, additionally mark it as "strong case not exportable by current brute" — this is a stronger signal because strong cases were promoted as regression inputs and the brute should ideally cover them.
* Never substitute an optimized attempt as the answer source. Never edit the `.in` file to make brute happy.

#### Handling a missing checker

If `checkers/checker.cpp` does not exist:

* Do **not** declare the LightCPVerifier package ready.
* Stage 6.5 still creates `lightcp/problems/<pid>/` and writes `statement.txt` if possible (to make later refreshes easier), but the package readiness flag must be `Ready for LightCPVerifier: NO`.
* The init report must list the missing checker as the blocker.

#### Idempotence

Stage 6.5 should be safe to rerun. On a refresh:

* `statement.txt`, `config.yaml`, and `checker.cpp` may be regenerated verbatim from their canonical sources.
* `testdata/*.in` may be re-derived from `tests/small/` and `tests/strong/`; report any cases that disappeared since the previous export.
* `testdata/*.ans` must always be regenerated by brute on each refresh — do not trust cached `.ans` files when the brute or the inputs may have changed.

#### `x-stressor` metadata block

`config.yaml` must contain a custom `x-stressor` block that captures stressor-workflow metadata so that downstream skills (`stressor-gen-large`, `stressor-stress`, future export refreshes) can act on it without re-deriving the intersection.

Required shape:

```yaml
x-stressor:
  schema_version: 1
  pid: QOJ464
  problem_root: .
  statement:
    primary: statement/statement.md
    directory: statement
  package:
    directory: lightcp/problems/QOJ464
    statement_txt: statement.txt
    checker: checker.cpp
    testdata: testdata
  sources:
    validator:
      path: validators/val.cpp
      scope: validators/VALIDATION_SCOPE.md
      status: READY
    brute:
      path: solutions/brute.cpp
      scope: solutions/BRUTE_SCOPE.md
      limits: solutions/BRUTE_LIMITS.json
      status: READY
    checker:
      path: checkers/checker.cpp
      scope: checkers/CHECKER_SCOPE.md
      status: READY
    generators:
      directory: generators
      readme: generators/README.md
      status: READY
  compatible_range:
    source: intersection of statement constraints, validator scope, brute limits, checker scope, and generator capabilities
    status: READY
    notes:
      - This range is for stressor differential testing, not necessarily the full official constraint range.
    limits:
      T: { min: null, max: null }
      n: { min: null, max: null }
      m: { min: null, max: null }
      q: { min: null, max: null }
      sum_n: { max: null }
      sum_m: { max: null }
      value_abs_max: { max: null }
      string_length: { max: null }
      estimated_operations: { max: null }
    special_requirements:
      - ...
    unsupported:
      - ...
  output_comparison:
    method: testlib checker
    invocation: checker input participant_output jury_answer
    exact_diff_used: false
  generation_policy:
    stress_tests_must_respect_compatible_range: true
    large_tests_outside_compatible_range_must_not_be_used_for_brute_comparison: true
  exported_cases:
    - input: small_0001.in
      output: small_0001.ans
      source: tests/small/01
      within_compatible_range: true
      validator: PASS
      brute: PASS
      checker_brute_vs_brute: PASS
  assumptions:
    - ...
  config_fallbacks:
    time_limit: 2s
    memory_limit: 256m
    type: default
    filename: main.cpp
```

Rules:

* Do not leave meaningless placeholders if information is known. Fill real values.
* If a number is genuinely unknown, write `null` rather than guessing. Prefer `UNKNOWN` plus a prose note over a fabricated number.
* Only include problem variables that actually exist (e.g. omit `string_length` for a graph-only problem).
* `exported_cases` is stressor-side metadata; the LightCPVerifier judge still reads `subtasks.cases`.

#### Computing `x-stressor.compatible_range`

`stressor-init` computes a conservative intersection of:

1. Statement constraints (read from the problem statement).
2. Validator scope: `validators/VALIDATION_SCOPE.md` — in particular its "Machine-Readable Summary for stressor-init" YAML block.
3. Brute limits: `solutions/BRUTE_LIMITS.json` — `recommended_limits`, `global_work_budget`, `unsupported_if`.
4. Checker capability: `checkers/CHECKER_SCOPE.md` — its "Machine-Readable Summary for stressor-init" YAML block. If absent, only infer that the checker exists and supports the testlib invocation order.
5. Generator capability: `generators/README.md` — declared generator modes and parameter ranges.

The resulting `compatible_range` describes data that should be:

* legal under the statement;
* accepted by validator;
* runnable by brute;
* comparable by checker;
* generatable by the available generators.

This is the safe range for `stressor-stress` and generator-based differential testing. It is **not** necessarily the full official problem range.

Computation rules:

* For numeric upper bounds, take the minimum of all known upper bounds.
* For numeric lower bounds, take the maximum of all known lower bounds.
* For total work budgets, use the most restrictive budget.
* For special graph/string/geometry requirements, intersect the allowed properties.
* If a component lacks a range, do **not** assume it supports full statement constraints — record `status: INCOMPLETE`.
* If component ranges conflict (e.g. validator demands connected graphs but generator only emits forests), record `status: CONFLICT` and list blockers.
* If brute only supports small data, `compatible_range` must reflect brute limits.
* If the generator can only produce a subset of legal inputs, `compatible_range` must reflect generator capability.
* If the checker cannot safely compare non-unique outputs, mark `compatible_range.output_comparison` accordingly and downgrade stress readiness.

Example: if the statement allows `n <= 200000` but `BRUTE_LIMITS.json` says `recommended_limits.n = 12`, then

```yaml
x-stressor:
  compatible_range:
    limits:
      n: { max: 12 }
```

because that is the range in which brute differential testing is meaningful.

#### Cases vs `compatible_range`

Cases exported to the LightCPVerifier package should satisfy `compatible_range` unless explicitly marked otherwise:

* Do not silently export a case whose input falls outside `compatible_range`.
* If a strong / official case must be exported despite being outside `compatible_range`, the user must explicitly request it; record it in `x-stressor.exported_cases` with `within_compatible_range: false` and a note explaining the override.
* `exported_cases` metadata is for stressor; the judge still drives evaluation from `subtasks.cases`.

### Stage 6.7: Official Sample Preflight

After statement resolution and after the validator / brute / checker / LightCPVerifier-export stages, and before the final readiness decision in Stage 7, discover official samples under the statement directory and run a sample preflight.

Record:

* sample inputs found
* sample input/output pairs found
* orphan inputs (inputs with no matching output)
* orphan outputs (outputs with no matching input)

Then enforce, in order, the following sample checks. Each check produces a status that feeds into Stage 7.

#### 1. Validator sample check

If `validators/val.cpp` exists:

* run the compiled validator on every complete official sample input file under `statement/`;
* if the sample's data range is allowed by `validators/VALIDATION_SCOPE.md` and the sample is a complete input file, validator must pass;
* if validator fails, triage according to `stressor-vali`'s sample-failure triage rules (`VALIDATOR_TOO_STRICT`, `SAMPLE_IS_NOT_COMPLETE_INPUT`, `SAMPLE_OUT_OF_SCOPE_FOR_VALIDATOR`, `SAMPLE_VIOLATES_STATEMENT`, `STATEMENT_AMBIGUOUS`, `TOOLING_OR_PATH_ERROR`);
* if unresolved, mark validator or sample preflight as `FAILED_CHECK` and record the reason.

#### 2. Brute sample check

If `solutions/brute.cpp` exists and a matching official sample output file exists for a discovered sample input:

* check whether the sample input is within `solutions/BRUTE_LIMITS.json`;
* if runnable and checker exists, run:

  ```bash
  ./build/checker sample.in brute.out sample.out
  ```
* if checker is missing, mark sample checker validation as `BLOCKED`;
* if brute fails a runnable official sample, mark brute as `FAILED_CHECK`;
* if the sample is outside `BRUTE_LIMITS.json`, record `SAMPLE_OUT_OF_BRUTE_SCOPE` and do not force the brute to run it.

#### 3. Checker sample check

If `checkers/checker.cpp` exists:

* it must be able to check brute output against an official sample output when a matching sample output exists;
* if checker fails on a brute-vs-official-sample comparison that looks correct, triage one of:

  * checker bug
  * brute bug
  * sample output not compatible due to non-unique output
  * statement ambiguity

* record the chosen triage outcome with a one-line explanation.

#### 4. Readiness impact

Sample preflight feeds the four readiness flags computed in Stage 7 like this:

* `Ready for stressor-try`: sample failures do **not** necessarily block writing an optimized try if the only issue is a missing checker, but every sample failure must be reported in the init report.
* `Ready for stressor-stress`: if the checker cannot validate sample-style outputs and the output is non-unique, mark stress readiness as `NO` and explain why under Blockers.
* `Ready for LightCPVerifier`: official sample inputs exported to a LightCP package must have `.ans` generated by `solutions/brute.cpp`, not copied blindly from `statement/*.out` unless the user explicitly opts in. Sample output files from `statement/` may be used for validation or as a cross-check; they must not be the canonical answer-generation source.

### Stage 7: Readiness decision

Compute five readiness flags:

```text
Ready for stressor-try: YES / NO
Ready for stressor-stress: YES / NO
Large generation ready: YES / NO
Ready for LightCPVerifier: YES / NO
Compatible range ready: YES / NO
```

Rules:

`Ready for stressor-try = YES` if:

* small tests READY
* validator READY
* brute READY
* checker READY

Large generator may be missing and still allow `stressor-try`, but report that large stress is unavailable.

`Ready for stressor-stress = YES` if:

* brute READY
* checker READY
* small tests READY
* strong directory exists or can be created
* optimized solution will be supplied later

`Large generation ready = YES` if:

* large generators READY
* validator READY
* generator pilot/verification passed

`Ready for LightCPVerifier = YES` if and only if **all** of the following hold:

* `lightcp/problems/<pid>/config.yaml` exists and explicitly enumerates the exported cases.
* `lightcp/problems/<pid>/config.yaml` contains a non-empty `x-stressor` metadata block.
* `lightcp/problems/<pid>/statement.txt` exists.
* `lightcp/problems/<pid>/checker.cpp` exists (copied from `checkers/checker.cpp`).
* For every exported case, both `testdata/<name>.in` and a matching `testdata/<name>.ans` exist.
* Every exported `*.in` passed `validators/val.cpp` if a validator exists.
* Every exported `*.ans` was generated by `solutions/brute.cpp` (never by an optimized attempt).
* The checker brute-vs-brute sanity check (`checker input brute.out brute.out`) returned `_ok` on every exported case.

If any of these fails, `Ready for LightCPVerifier` must be `NO`, and the reason must be listed under Blockers.

`Compatible range ready = YES` if and only if **all** of the following hold:

* `x-stressor.compatible_range.status` is `READY`.
* `validators/VALIDATION_SCOPE.md` exists with a Machine-Readable Summary that fed the computation.
* `solutions/BRUTE_LIMITS.json` exists with machine-readable limits that fed the computation.
* Checker capability is known — either via `checkers/CHECKER_SCOPE.md` or via an explicit note that the checker imposes no input-size limit beyond memory/time.
* Generator capability is known via `generators/README.md`, **or** large generation is explicitly marked unavailable in this run.

If any contributing scope is missing, `compatible_range.status` must be `INCOMPLETE`, and `Compatible range ready` must be `NO`. Do not silently set it to `READY`.

### Stage 8: Init report

Create:

```text
reports/init_report_XXXX.md
```

Use a fresh four-digit number or timestamp.

The report must include:

````markdown
# Stressor Init Report

## Problem

- Statement: ...

## Mode

- default / check-only / force-regenerate COMPONENT

## Component Status

| Component | Status | Path | Checks Performed | Notes |
|---|---|---|---|---|
| small tests | READY / MISSING / ... | tests/small | ... | ... |
| validator | READY / MISSING / ... | validators/val.cpp | ... | ... |
| validation scope | READY / MISSING / ... | validators/VALIDATION_SCOPE.md | ... | ... |
| brute | READY / MISSING / ... | solutions/brute.cpp | ... | ... |
| brute scope | READY / MISSING / ... | solutions/BRUTE_SCOPE.md | ... | ... |
| brute limits | READY / MISSING / ... | solutions/BRUTE_LIMITS.json | ... | ... |
| checker | READY / MISSING / ... | checkers/checker.cpp | ... | ... |
| large generators | READY / MISSING / ... | generators/ | ... | ... |

## Small Tests

- count:
- legality review status:
- validator status:
- brute status:

## Validator

- status:
- supported range:
- checked exactly:
- partially checked:
- not checked:
- complexity:

## Brute

- status:
- complexity:
- runnable limits:
- output comparison notes:

## Checker

- status:
- checker path:
- testlib include path:
- checker invocation:
- brute-vs-brute sanity check:

## Large Generators

- status:
- generator files:
- README:
- pilot review:
- validator result:
- verification data cleaned: yes/no

## LightCPVerifier Package

- pid:
- directory:
- config: lightcp/problems/<pid>/config.yaml
- statement: lightcp/problems/<pid>/statement.txt
- checker: lightcp/problems/<pid>/checker.cpp
- testdata count:
- exported small cases:
- exported strong cases:
- skipped cases:
- ready for LightCPVerifier: YES / NO

## LightCPVerifier config.yaml

- path:
- generated: yes/no
- pid:
- type:
- time_limit:
- memory_limit:
- checker:
- filename:
- cases exported:
- config fallbacks used:
- ready: YES / NO

## x-stressor Compatible Range

- status: READY / INCOMPLETE / CONFLICT
- sources used: statement / validator / brute / checker / generators
- limits:
- special_requirements:
- unsupported:
- notes:

## Official Samples

- statement directory:
- sample input files found:
- sample input/output pairs:
- orphan sample inputs:
- orphan sample outputs:

## Official Sample Validator Check

- checked:
- passed:
- failed:
- skipped:
- reasons:

## Official Sample Brute Check

- runnable samples:
- skipped due to BRUTE_LIMITS:
- checker used:
- passed:
- failed:
- pending:

## Official Sample Impact

- validator ready impact:
- brute ready impact:
- checker ready impact:
- stress readiness impact:

## Readiness

- Ready for stressor-try: YES / NO
- Ready for stressor-stress: YES / NO
- Large generation ready: YES / NO
- Ready for LightCPVerifier: YES / NO
- Compatible range ready: YES / NO

## Blockers

List blockers.

## Next Command

If ready for try:

```text
$stressor-try path_to_problem_statement
```

If not ready, list required fixes.
````

## Failure Policy

This skill is fail-fast.

Stop if:

- small tests cannot be legally generated or verified
- validator rejects legal small tests and cannot be repaired
- brute cannot be produced or fails on small tests
- checker cannot be produced or fails brute-vs-brute sanity check
- testlib is missing for validator/checker/generator stages
- required component skill is missing

Do not continue to later stages when earlier prerequisites are unreliable.

## Idempotence Rules

This skill should be safe to rerun.

If a component already exists:

- inspect it
- reuse it if it passes contract checks
- do not overwrite it unless user explicitly requests regeneration
- report reuse

If a component is incomplete:

- repair or regenerate only that component through the appropriate component skill
- avoid unnecessary changes to other components

Do not delete existing tests or code.

Do not overwrite `tests/strong`.

Do not overwrite existing generator files unless requested.

Do not overwrite existing validator/brute/checker unless requested or clearly broken and repair is part of the requested init.

## Relationship to Other Skills

Expected order:

```text
stressor-gen-small
-> stressor-vali
-> stressor-brute
-> stressor-checker
-> stressor-gen-large
-> ready for stressor-try
```

Do not call `stressor-try` from this skill.

Do not call `stressor-stress` unless an optimized solution already exists and the user explicitly asks for a post-init smoke stress.

## Final Response Format

After using this skill, final response must contain:

```text
Stressor init summary:
- statement: ...
- mode: ...
- ready for stressor-try: yes/no
- ready for stressor-stress: yes/no
- large generation ready: yes/no
- compatible range ready: yes/no

Component statuses:
- small tests: READY / ...
- validator: READY / ...
- brute: READY / ...
- checker: READY / ...
- large generators: READY / ...

Important paths:
- tests/small: ...
- validators/val.cpp: ...
- validators/VALIDATION_SCOPE.md: ...
- solutions/brute.cpp: ...
- solutions/BRUTE_LIMITS.json: ...
- checkers/checker.cpp: ...
- generators/README.md: ...
- reports/init_report_XXXX.md: ...

LightCPVerifier:
- ready: yes/no
- pid: ...
- package: lightcp/problems/<pid>
- config: lightcp/problems/<pid>/config.yaml
- config fallbacks used: ...
- x-stressor block present: yes/no
- compatible range status: READY / INCOMPLETE / CONFLICT

Blockers:
- ...

Next command:
- ...
```

## Strict Rules

* Must not write optimized attempt files.
* Must not run `stressor-try`.
* Must not overwrite existing components silently.
* Must inspect existing components before regenerating them.
* Must use existing component skills instead of duplicating their full logic.
* Must create or verify `tests/small` before validator/brute/checker/large generator stages.
* Must ensure small tests pass validator before continuing.
* Must ensure brute runs on small tests before continuing.
* Must ensure checker compiles before continuing.
* Must sanity-check checker with brute output when possible.
* Must ensure large generators use testlib.
* Must ensure large generator pilot tests pass three-way legality review.
* Must ensure large generator pilot or verification tests pass validator if validator exists.
* Must respect `validators/VALIDATION_SCOPE.md`.
* Must respect `solutions/BRUTE_LIMITS.json` for any brute-based verification.
* Must not generate huge large data during init by default.
* Must clean temporary `tests/large` verification data unless user asks to keep it.
* Must generate an init report.
* Must stop and report blockers instead of pretending initialization succeeded.
* Must create or refresh `lightcp/problems/<pid>/config.yaml` whenever the package directory is built.
* `config.yaml` must enumerate cases explicitly under `subtasks.cases`; relying on `n_cases` alone is not allowed.
* `config.yaml` must include an `x-stressor` metadata block.
* Must compute `x-stressor.compatible_range` as the conservative intersection of statement, `validators/VALIDATION_SCOPE.md`, `solutions/BRUTE_LIMITS.json`, `checkers/CHECKER_SCOPE.md` (if present), and `generators/README.md`.
* Must not claim `compatible_range.status: READY` if any required component scope is missing — use `INCOMPLETE` or `CONFLICT` instead.
* Must record fallback values (e.g. `time_limit: 2s`, `memory_limit: 256m`, `filename: main.cpp`) under `x-stressor.config_fallbacks` and explain them under `x-stressor.assumptions`.
* Must not use the optimized solution to generate `.ans`. `.ans` is always generated by `solutions/brute.cpp`.
* Must not blindly use `statement/*.out` as `.ans`. Sample outputs are for cross-checking only.
* Must not silently export cases outside `compatible_range`; if a case must be exported anyway, record it in `x-stressor.exported_cases` with `within_compatible_range: false` and an explanation.
* Must not claim `Ready for LightCPVerifier: YES` unless config (with `x-stressor`), checker, statement, testdata, and brute-vs-brute sanity checks are all complete.
* Must not place optimized attempts (`solutions/optimize_XXXX.cpp`) inside `lightcp/problems/<pid>/`. The optimized source stays in `solutions/`.
