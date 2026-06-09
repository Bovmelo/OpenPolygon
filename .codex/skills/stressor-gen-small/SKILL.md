---
name: stressor-gen-small
description: Handwrite small readable ICPC/CCPC test inputs with many legal corner cases, then verify each test through three independent legality-review subagents that each reread the problem statement from scratch. Use when the user wants small hand-checkable corner-case tests without generators, validator, checker, brute force, stress testing, or large data.
---

# Stressor Gen Small

## Purpose

This skill creates small hand-written test inputs for ICPC/CCPC style programming contest problems.

It focuses on:

- small legal tests
- readable corner cases
- direct handwritten test files
- careful legality inspection
- three independent legality-review subagents

This is the first stage of data preparation.

It must not create a full official Polygon package.

It must not use testlib.

It must not write generators.

Large data, testlib generators, validators, checkers, brute force solutions, stress testing, and answer generation belong to later stages.

## Scope

Allowed output when this skill is invoked:

- tests/small/01
- tests/small/02
- tests/small/03
- ...
- a final report explaining every test

All handwritten small tests in this skill must live under the `tests/small/` directory of the target problem. Do not write any test file directly under `tests/` itself, and do not invent other subdirectories (`tests/handwritten/`, `tests/manual/`, etc.) — `tests/small/` is the only allowed location.

If the user passes `--out-dir <path>`, write the small tests into that path instead of the default `tests/small/`. The default applies whenever `--out-dir` is omitted. Other skills (`stressor-vali`, `stressor-brute`, `stressor-init`) expect the small tests at `tests/small/`, so deviate from the default only when the user explicitly asks.

Forbidden output unless the user explicitly asks:

- generators/
- validators/
- checkers/
- solutions/
- stress/
- answers/
- testlib.h
- gen_all.sh
- large tests
- standard solution
- brute force solution
- wrong solutions
- checker
- validator

This skill must not create generator files.

This skill must not use testlib.

This skill must not create answer files.

This skill must not run stress testing.

## Invocation

Preferred invocation:

```text
$stressor-gen-small path_to_problem_statement
```

Optional arguments:

```text
$stressor-gen-small path_to_problem_statement --num-tests N
$stressor-gen-small path_to_problem_statement --num-tests N --out-dir tests/small
$stressor-gen-small path_to_problem_statement --out-dir custom/path
```

Parameter rules:

* `--num-tests N` — requested number of small handwritten tests. If omitted, choose a sensible default for the problem (typically 8 to 20).
* `--out-dir DIR` — output directory. Default `tests/small`.

When `--num-tests N` is provided:

* aim to produce exactly `N` legal corner-case tests;
* if the problem is too simple or the constraints make `N` distinct meaningful legal corner cases impossible, produce fewer than `N` and explain why in the final report — do **not** pad the count with duplicates or no-purpose tests;
* every test must still be reviewed by three independent legality-review subagents (A, B, C) and may only be kept when all three return LEGAL.

`stressor-init` uses `--num-small N` on its own command line and forwards it as `--num-tests N` when invoking this skill.

## Core Philosophy

Small tests should be hand-written.

The purpose is not random generation.

The purpose is to expose corner cases while keeping every input file small enough to inspect line by line.

Prefer many small legal corner cases over a few random-looking cases.

Every test must have a clear purpose.

Every test must be legal under the statement.

If legality cannot be confirmed, do not keep the test.

## Size Policy

Unless the statement forces larger values, keep all tests small.

Default suggested limits:

- array size: n <= 10
- string length: <= 20
- graph nodes: n <= 8
- graph edges: m <= 15
- tree nodes: n <= 10
- number of test cases per file: T <= 5
- coordinate values: usually between -10 and 10
- numeric values: use small values unless a small boundary-like value is important

Do not generate maximum-size data.

Do not create stress tests.

Do not create random huge data.

If a true boundary value is huge, usually avoid it in this skill. Instead, create a small analogue if it still helps reveal the corner case.

## Required Workflow

### 1. Read the problem from scratch

When invoked, read the target problem from `$ARGUMENTS`.

Inspect relevant files if they exist:

- statement
- samples
- notes
- constraints
- input format
- output format
- examples
- any README or problem description files

Extract:

- input format
- whether there is T
- bounds on T
- bounds on n, m, q, k, etc.
- value ranges
- whether zero is allowed
- whether negative values are allowed
- whether duplicate values are allowed
- string length constraints
- string alphabet constraints
- array length constraints
- graph restrictions
- tree restrictions
- whether self-loops are allowed
- whether multi-edges are allowed
- whether graph connectivity is required
- whether graph direction matters
- whether total sum constraints exist
- whether order matters
- any special validity constraints

If anything is unclear, list it under Assumptions.

Never silently invent constraints.

Never generate a corner case if the statement does not allow it.

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

## Official Samples vs Generated Small Tests

When generating small tests, inspect official samples under the statement directory.

Official samples should not be duplicated blindly.

If official samples already cover a corner case, mention that in the final report under "corner cases already covered by official samples" rather than re-handwriting an equivalent test.

Strict rules:

* Do not copy `statement/*.in` files into `tests/small/`.
* Do not overwrite any `statement/*.in` or `statement/*.out`.
* Do not auto-generate small tests whose only purpose is to mirror an official sample.
* Continue to generate complementary small tests for corner cases the official samples miss.
* Report which official samples were inspected and which corner cases they covered.

### 2. Create a corner-case-focused sample plan

Before writing tests, create a sample plan.

Usually generate 8 to 20 small tests, depending on problem complexity.

Use this format:

Test | Purpose | Size | Important legality points
01 | minimum legal case | tiny | lower bounds
02 | simplest normal case | small | normal input format
03 | all equal values | small | only if duplicates are allowed
04 | strictly increasing values | small | ordering corner
05 | strictly decreasing values | small | reverse ordering corner
06 | includes zero | small | only if zero is allowed
07 | includes negative values | small | only if negative values are allowed
08 | repeated pattern | small | low-entropy or periodic case
09 | small random-looking case | small | readable diversity
10 | special structure | small | chain, star, cycle, palindrome, etc. if applicable

Only include applicable legal cases.

If a tempting corner case is illegal according to the statement, do not generate it. Mention it under “corner cases intentionally not generated”.

### 3. Handwrite test files directly

Create files directly under:

tests/small/01
tests/small/02
tests/small/03
...

If the `tests/small/` directory does not exist, create it. Do not place any handwritten file directly under `tests/` — every file produced by this skill must live inside `tests/small/`.

Every file must be a complete valid input file.

If the problem has T, ensure T exactly matches the number of test cases inside that file.

If the problem does not have T, do not add T.

Do not add comments inside test files.

Do not add explanations inside test files.

Do not create generators.

Do not create gen_all.sh.

Do not use testlib.

Do not create answer files.

### 4. Corner case guidance

For array problems, consider legal versions of:

- minimum n
- n = 1 if allowed
- all equal
- all distinct
- sorted increasing
- sorted decreasing
- almost sorted
- alternating high/low
- repeated blocks
- includes minimum value
- includes zero if allowed
- includes negative values if allowed
- duplicate-heavy case if allowed
- small boundary-like values

For string problems, consider legal versions of:

- minimum length
- all same character
- all distinct characters if possible
- palindrome
- almost palindrome
- periodic string
- repeated substrings
- long common prefix
- long common suffix
- alphabet size 1 if allowed
- full allowed alphabet if small
- lexicographically ordered strings

For graph problems, consider legal versions of:

- minimum n and m
- no edges if allowed
- single edge
- chain
- star
- cycle if allowed
- disconnected graph if allowed
- connected sparse graph
- dense small graph if allowed
- isolated vertex if allowed
- repeated edge weights if weighted and allowed
- equal edge weights if weighted
- small extreme edge weights
- no self-loops unless allowed
- no duplicate edges unless allowed

For tree problems, consider legal versions of:

- n = 1 if allowed
- chain
- star
- broom
- balanced-like tree
- repeated node weights if allowed
- repeated edge weights if allowed
- small edge-weight extremes if weighted

For number theory problems, consider legal versions of:

- 0 if allowed
- 1 if allowed
- small primes
- small composites
- powers of two
- powers of a small prime
- coprime values
- values with large gcd
- repeated values
- small boundary-like values

For geometry problems, consider legal versions of:

- minimum number of points
- collinear points if allowed
- duplicate points only if allowed
- vertical lines
- horizontal lines
- small negative coordinates if allowed
- symmetric points
- degenerate cases only if allowed

For interval or range problems, consider legal versions of:

- single-point intervals
- non-overlapping intervals
- nested intervals
- identical intervals if allowed
- touching endpoints
- sorted intervals
- unsorted intervals if input order is arbitrary

For query problems, consider legal versions of:

- minimum number of queries
- repeated queries
- queries on first position
- queries on last position
- full-range queries
- single-element queries
- update-before-query patterns if applicable

### 5. Three independent legality-review subagents

Every generated test must be checked by three independent legality-review subagents:

- legality-reviewer-A
- legality-reviewer-B
- legality-reviewer-C

If the environment supports explicit subagents or Task tool calls, use three separate subagent calls.

Each reviewer must be given the problem statement and the concrete test file content.

Each reviewer must work independently.

Each reviewer must reread the problem statement from scratch.

Each reviewer must not rely on:

- the sample plan
- the creator’s explanation
- other reviewers’ conclusions
- the assumption that handwritten tests are correct

For every test file, each reviewer must inspect the concrete content line by line and verify:

- input format
- whether T exists and matches the number of test cases
- all array lengths
- all string lengths
- all string alphabets
- all numeric ranges
- graph node labels
- graph edge counts
- self-loop rules
- multi-edge rules
- graph connectivity if required
- tree edge count and connectedness if required
- directionality if graph is directed
- sum constraints if any
- extra tokens
- missing tokens
- special statement-specific validity constraints

Each reviewer must mark ambiguous cases as SUSPICIOUS instead of LEGAL.

Each reviewer must output this format:

Reviewer A for tests/small/01:
Status: LEGAL / SUSPICIOUS / INVALID
Reason:
Checked items:
- ...
Assumptions:
- ...

Reviewer B for tests/small/01:
Status: LEGAL / SUSPICIOUS / INVALID
Reason:
Checked items:
- ...
Assumptions:
- ...

Reviewer C for tests/small/01:
Status: LEGAL / SUSPICIOUS / INVALID
Reason:
Checked items:
- ...
Assumptions:
- ...

A test can be accepted only if all three reviewers explicitly return LEGAL.

If any reviewer returns SUSPICIOUS or INVALID:

- do not accept the test
- fix or replace the test
- rerun all three reviews from scratch
- accept the fixed test only after A, B, and C all return LEGAL

Never claim a test is legal unless all three reviewers say LEGAL.

### 6. Handling reviewer disagreement

If reviewers disagree:

- treat the test as not accepted
- identify the reason for disagreement
- reread the statement
- fix the test or remove it
- rerun all three reviews

If the issue is caused by ambiguous statement wording, do not force acceptance.

Either choose a safer test or report the ambiguity.

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

### Role of `stressor-gen-small` in the export

* `stressor-gen-small` keeps writing its handwritten files under `tests/small/`. That remains the canonical location.
* Small tests are **development inputs only**. They are not directly judge-ready until `stressor-init` (or a dedicated LightCP export stage) runs `solutions/brute.cpp` to create matching `.ans` files.
* When `stressor-init` performs the LightCPVerifier export, files in `tests/small/` map to `lightcp/problems/<pid>/testdata/` with names like:

```text
tests/small/01    -> lightcp/problems/<pid>/testdata/small_0001.in
tests/small/02    -> lightcp/problems/<pid>/testdata/small_0002.in
tests/small/foo   -> lightcp/problems/<pid>/testdata/small_0003.in
```

Strict rules for this skill in the LightCPVerifier context:

* `stressor-gen-small` must **not** generate `.ans` files.
* `stressor-gen-small` must **not** write `config.yaml`.
* `stressor-gen-small` must **not** write anything under `lightcp/problems/<pid>/`.
* `stressor-gen-small` must **not** copy `checker.cpp` or `statement.txt` into a LightCPVerifier package.

The export step is owned by `stressor-init` (or a dedicated export stage), not by `stressor-gen-small`.

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

`stressor-gen-small` itself does not perform this export. It only refrains from copying or mirroring official samples into `tests/small/` so that the export stage can treat `statement/` as the canonical sample source.

### 7. Final report format

After using this skill, the final response must contain:

Problem understanding:
...

Extracted constraints:
...

Generated files:
...

Sample plan:
...

Test overview:
01 - ...
02 - ...
03 - ...

Three-way legality review:
tests/small/01:
- Reviewer A: LEGAL, ...
- Reviewer B: LEGAL, ...
- Reviewer C: LEGAL, ...
- Final status: ACCEPTED

tests/small/02:
- Reviewer A: LEGAL, ...
- Reviewer B: LEGAL, ...
- Reviewer C: LEGAL, ...
- Final status: ACCEPTED

Corner cases covered:
- ...

Corner cases intentionally not generated:
- ... because illegal under the statement
- ... because it belongs to large-data generation
- ... because legality is ambiguous

Assumptions:
...

Not created:
- generators
- validator
- checker
- brute force
- stress pt a test unless all three reviewers say LEGAL.
- Do not silently invent constraints.
- Do not include comments inside test files.
- Keep tests small and readable.
- Prefer many small legal corner cases over random-looking cases.
- If legality cannot be guaranteed, report the uncertainty instead of pretending the test is valid.
