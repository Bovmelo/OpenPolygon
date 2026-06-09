---
name: stressor-gen-large
description: Generate medium and large ICPC/CCPC test inputs into tests/large using Codeforces Polygon style testlib.h generators. Supports user-specified number of tests, prompt-specified ranges and special properties, pilot legality review through three independent subagents, and validator checking if available.
---

# Stressor Gen Large

## Purpose

This skill creates medium and large test inputs for ICPC/CCPC style programming contest problems.

Unlike `stressor-gen-small`, this skill does not handwrite final test files.

This skill uses Codeforces Polygon style `testlib.h` generators.

It focuses on:

- legal data first
- reproducible testlib generators
- generator parameters explicitly chosen by the agent
- seed-controlled generation
- medium and large tests
- max or near-max boundary tests
- structured corner cases at scale
- user-specified number of generated tests
- user-specified generation ranges and special properties
- pilot small-data legality review before large generation
- optional validation through existing `validators/val.cpp`
- documentation of every generator's usage

This skill does not create a full official Polygon package.

This skill does not write validator, checker, brute force, standard solution, wrong solutions, answer files, or solution stress testing scripts.

## Default Output Directory

Generated large tests must be placed under:

```text
tests/large/
```

The default output directory is:

```text
tests/large
```

Do not use `tests_large/` unless the user explicitly asks.

Test files should be named:

```text
tests/large/01
tests/large/02
tests/large/03
...
```

If more than 99 tests are generated, use enough zero padding, such as:

```text
tests/large/001
tests/large/002
...
```

Avoid overwriting unrelated files.

If `tests/large/` already exists, identify which files this skill owns before overwriting. Prefer overwriting only generated numbered test files after reporting the action.

## Scope

Allowed output when this skill is invoked:

```text
generators/
├── gen_large.cpp
├── gen_max.cpp
├── gen_structured.cpp        optional, if useful
├── gen_graph.cpp             optional, if graph-specific
├── gen_array.cpp             optional, if array-specific
├── gen_string.cpp            optional, if string-specific
├── gen_all_large.sh
└── README.md

tests/
└── large/
    ├── 01
    ├── 02
    ├── 03
    └── ...

build/                         created by scripts if needed
```

Forbidden output unless the user explicitly asks:

```text
validators/
checkers/
solutions/
stress/
answers/
standard solution
brute force solution
wrong solutions
checker
validator
answer files
```

This skill must not write `validators/val.cpp`.

This skill must not write checker or solution files.

This skill must not create answer files.

This skill must not run solution stress testing.

## Invocation

Preferred invocation:

```text
$stressor-gen-large path_to_problem_statement --num-tests N
```

Examples:

```text
$stressor-gen-large ./statement.md --num-tests 20
```

```text
$stressor-gen-large ./statement.md --num-tests 15 --out-dir tests/large
```

```text
$stressor-gen-large ./statement.md --num-tests 25 --out-dir tests/large

Generate mostly near-maximum random tests. Include many duplicate values, monotone arrays, and boundary values.
```

Supported arguments:

* first positional argument: `path_to_problem_statement`
* `--num-tests N`: number of large test files to generate
* `--out-dir DIR`: output directory, default is `tests/large`
* remaining natural language text: generation requirements

If `--num-tests` is omitted, choose a reasonable default, usually 10 to 15 tests.

If `--out-dir` is omitted, use:

```text
tests/large
```

Treat the first positional argument as `path_to_problem_statement`.

Read the problem statement file from that path first.

If the first argument is a directory, search that directory for likely statement files such as:

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

`stressor-gen-large` reads official samples only to understand the input format; it must not duplicate them into `tests/large/` and must not derive generator parameters from sample outputs.

## Legality Priority

The highest priority is legal data generation.

The priority order is:

1. Problem statement constraints.
2. `validators/VALIDATION_SCOPE.md`, if it exists.
3. `validators/val.cpp`, if it exists.
4. User prompt requirements.
5. Generator convenience.

If the user's requested range or special property conflicts with the statement, reject or adjust it.

If it conflicts with `VALIDATION_SCOPE.md`, reject or adjust it.

If validator exists, generated data must pass validator.

Never generate data that is known to violate the statement.

Never generate data that is outside the validator supported range if `VALIDATION_SCOPE.md` says the validator cannot check it efficiently.

Do not silently ignore conflicts.

Report every adjustment.

## Testlib Location Requirement

This skill must use `testlib.h`.

Before writing or compiling generators, search the current project for `testlib.h`.

Acceptable locations include (in roughly descending priority — search each pattern, take the first match):

```text
./testlib.h
./generators/testlib.h
./lib/testlib.h
./third_party/testlib.h
./third_party/testlib/testlib.h
../testlib.h
../third_party/testlib.h
../third_party/testlib/testlib.h
../../third_party/testlib.h
../../third_party/testlib/testlib.h
```

The last few entries cover multi-problem layouts where `testlib.h` is shared one or two directories above the current problem directory.

If none of the patterns match, fall back to:

```bash
find . -maxdepth 4 -name testlib.h
find .. -maxdepth 3 -name testlib.h
find ../.. -maxdepth 3 -name testlib.h
```

If `testlib.h` is found, record its **directory** (the value to pass to `-I`) and reuse it everywhere:

```bash
TESTLIB_INCLUDE=../third_party/testlib   # example
g++ -std=c++17 -O2 -pipe -I"$TESTLIB_INCLUDE" generators/gen_large.cpp -o build/gen_large
```

The generation script (`generators/gen_all_large.sh`) must accept this path via the `TESTLIB_INCLUDE` environment variable with a sensible default; never hard-code `-I.` unless `testlib.h` is actually at the project root.

If `testlib.h` is missing:

* stop
* report that `testlib.h` is required
* do not write incomplete generators
* do not generate tests
* do not download `testlib.h`
* do not vendor external files unless explicitly asked

## Relationship with Validator

If `validators/VALIDATION_SCOPE.md` exists:

* read it before designing generators
* extract supported input range
* extract special generator requirements
* extract unchecked or partially checked constraints
* ensure generated data stays within validator-supported range
* if user asks for data outside that range, clamp or reject the request and report it

If `solutions/BRUTE_LIMITS.json` exists:

* read it as well; it documents the brute oracle's runnable input range
* when this skill is being driven by `stressor-init` or `stressor-stress` (i.e. the generated data is meant to be cross-checked against the brute), keep generated sizes within `BRUTE_LIMITS.json` so the brute can actually run on the data
* for unconstrained large generation (default standalone use), `BRUTE_LIMITS.json` is advisory only — the statement constraints and `VALIDATION_SCOPE.md` remain authoritative

## Using x-stressor.compatible_range

If `lightcp/problems/<pid>/config.yaml` exists and contains an `x-stressor.compatible_range` block, that block is the canonical safe range for differential testing data.

```yaml
x-stressor:
  compatible_range:
    status: READY
    limits:
      n: { min: ..., max: ... }
      m: { min: ..., max: ... }
      ...
```

Generator schedules for differential testing must stay within that range:

* For any test that will be cross-checked against `solutions/brute.cpp` or against `checkers/checker.cpp`, every generated parameter must fall inside `x-stressor.compatible_range.limits`.
* If the user requests data outside `compatible_range`, either clamp to the range or report that the requested data is outside the brute/checker/validator/generator intersection. Do not silently produce out-of-range stress tests.
* If `compatible_range.status` is `INCOMPLETE` or `CONFLICT`, treat it as "not authoritative" and fall back to `VALIDATION_SCOPE.md` + `BRUTE_LIMITS.json`, reporting which source was actually used.

Standalone validator-only generation (not for differential testing) may exceed `compatible_range` only if the user explicitly requests full-range data **and** the resulting tests are not handed to `stressor-stress` for brute comparison. Such tests must be reported as "validator-only, not safe for brute comparison".

If `config.yaml` does not exist, behave as before using `VALIDATION_SCOPE.md` and `BRUTE_LIMITS.json` directly.

## Init mode (called by stressor-init)

When this skill is invoked from `stressor-init`, the goal is **pilot / verification only**:

* generate enough small pilot data to prove the generators compile, parse arguments correctly, produce legal output, and pass `validators/val.cpp` if it exists;
* do **not** generate the full requested number of large tests in init mode;
* if `tests/large/` is used as a scratch directory for verification, the temporary files should be cleaned by `stressor-init` after verification (this skill does not own that cleanup).

Standalone invocations (without `stressor-init`) keep the full behaviour described elsewhere in this document.

If `validators/val.cpp` exists:

* compile it
* run it on pilot tests if applicable
* run it on every generated large test
* every generated large test must pass validator
* if a generated test fails validator, fix the generator or parameters, not the output file
* rerun generation and validation
* final report must include validator result for each test

If `validators/val.cpp` does not exist:

* still write generators and generate tests if the user asked for generation
* do not claim the data is mechanically verified
* final report must clearly say that validator was not found
* final report must say that legality is based only on statement-derived generator logic and pilot reviewer checks, not validator verification

Never pretend that large data is definitely legal without validator checking.

## Testlib Generator Requirements

Every generator must:

* include `#include "testlib.h"`
* call `registerGen(argc, argv, 1);`
* use `rnd` from testlib for randomness
* avoid `rand()`
* avoid unnecessary `mt19937`
* print exactly one complete input file to stdout
* generate deterministic output for the same command line arguments
* keep generated data within statement constraints
* keep generated data within validator scope if `VALIDATION_SCOPE.md` exists
* support command line parameters
* support explicit seed
* support explicit generation modes
* generate medium or large tests, not tiny handwritten samples

Every generator must accept a seed parameter.

Important testlib gotcha: with `registerGen(argc, argv, 1)`, **every** `--key value` argument on the command line must be consumed by an `opt<>(...)` call. If a generator is invoked with `--seed N` but the source never calls `opt<>("seed")`, testlib will print `FAIL Opts: unused key 'seed'` and exit non-zero **after** main returns, even if the data was already written to stdout. The fix is to acknowledge the key explicitly:

```cpp
(void)opt<long long>("seed");   // testlib has already used argv to seed rnd
```

Read every parameter you intend to pass on the command line, even if the value is unused inside main.

Prefer this style:

```cpp
#include "testlib.h"
#include <bits/stdc++.h>
using namespace std;

int main(int argc, char* argv[]) {
    registerGen(argc, argv, 1);

    int seed = opt<int>("seed");
    int mode = opt<int>("mode", 0);

    // Other parameters should be explicit and problem-specific.
    // Examples:
    // int n = opt<int>("n");
    // int m = opt<int>("m");
    // int q = opt<int>("q");

    // Generate one valid complete input file.
}
```

Do not rely on hidden defaults for important parameters — always read them via `opt<>` so a reviewer can see the full configuration on the command line.

## Multiple Generators

```text
generators/gen_large.cpp
```

For medium and large data.

```text
generators/gen_max.cpp
```

For maximum or near-maximum boundary cases.

```text
generators/gen_structured.cpp
```

For structured cases such as chains, stars, monotone arrays, periodic strings, dense/sparse graphs, etc.

Problem-specific generators are encouraged when they make the design cleaner.

Examples:

```text
generators/gen_array.cpp
generators/gen_tree.cpp
generators/gen_graph.cpp
generators/gen_string.cpp
generators/gen_queries.cpp
```

Do not create too many tiny overlapping generators.

Each generator should have a clear role.

## Generator Documentation Requirement

Create:

```text
generators/README.md
```

This file must document:

* every generator file
* its purpose
* its command line interface
* every parameter
* every mode
* default assumptions if any
* example commands
* what kind of data each mode generates
* which modes are used in `gen_all_large.sh`
* notes about validator scope
* notes about user-requested special properties

Example structure:

````markdown
# Large Data Generators

## gen_large.cpp

Purpose:
- medium and large random/semi-random tests

Usage:
```bash
./build/gen_large --seed 100001 --mode 0 --n 200000
```

Parameters:

* `--seed`: deterministic seed
* `--mode`: generation mode
* `--n`: size parameter
* ...

Modes:

* `0`: high-entropy random
* `1`: low-entropy duplicate-heavy
* `2`: monotone/increasing
* ...

## gen_max.cpp

...

````

Do not omit this file.

## Pilot Test Requirement

Before generating the requested medium/large data, each generator must first generate small pilot tests.

The purpose of pilot tests is to catch generator logic mistakes before producing large data.

Pilot tests should be small enough for line-by-line AI inspection.

Suggested pilot sizes:

- array n <= 10
- string length <= 20
- graph n <= 8, m <= 15
- tree n <= 10
- T <= 3
- small numeric values when possible

For each generator and each important mode, generate at least one pilot test.

Pilot and verification tests must be written to:

```text
tests/large/
```

This is the same directory used for ordinary large-test output. `tests/large/` is **temporary workflow-generated data**: it is cleaned by `stressor-stress` at the end of the large stage, and any durable failing case must be promoted to `tests/strong/` rather than left in `tests/large/`.

When `stressor-gen-large` is invoked by `stressor-init` for pilot or verification, the temporary generated data must still be placed under `tests/large/`. `stressor-init` cleans this temporary data after verification unless the user explicitly asks to keep it.

Do not use `build/pilot/` or `tests/large_pilot/` as alternative pilot locations; those names are deprecated and would diverge from `stressor-init` and `stressor-stress` expectations.

Always report where pilot data was stored.

Pilot tests must not be confused with final large tests.

## Three Independent Pilot Legality Reviewers

Every pilot test must be checked by three independent legality-review subagents:

* legality-reviewer-A
* legality-reviewer-B
* legality-reviewer-C

If the environment supports explicit subagents or Task tool calls, use three separate subagent calls.

Each reviewer must be given:

* the problem statement
* the relevant validator scope if available
* the concrete pilot test content

Each reviewer must:

* reread the problem statement from scratch
* not rely on the generator code
* not rely on the generation plan
* not rely on other reviewers
* inspect the concrete pilot test line by line
* verify input format
* verify T if T exists
* verify array lengths
* verify string lengths and alphabets
* verify numeric ranges
* verify graph node labels
* verify graph edge counts
* verify self-loop rules
* verify multi-edge rules
* verify connectivity if required
* verify tree edge count and connectedness if required
* verify sum constraints if any
* verify statement-specific validity constraints
* mark ambiguous cases as SUSPICIOUS instead of LEGAL

Each reviewer must output:

```text
Reviewer A for pilot <name>:
Status: LEGAL / SUSPICIOUS / INVALID
Reason:
Checked items:
- ...
Assumptions:
- ...
```

Same for Reviewer B and Reviewer C.

A pilot test can be accepted only if all three reviewers explicitly return LEGAL.

If any reviewer returns SUSPICIOUS or INVALID:

* do not proceed to large generation for that generator/mode
* inspect the generator and parameters
* fix the generator or pilot parameters
* regenerate the pilot test
* rerun all three reviews from scratch
* accept only when A, B, and C all return LEGAL

If validator exists, pilot tests must also pass validator.

If a pilot test passes three reviewers but fails validator:

* inspect whether validator is too strict or generator is wrong
* this skill primarily owns generators, so prefer fixing generator or parameters
* do not modify validator unless the user explicitly asks
* report validator disagreement if it appears to be a validator issue

## Required Workflow

### 1. Read problem statement

Read the target statement from `path_to_problem_statement`.

Extract:

* input format
* whether there is T
* bounds on T
* bounds on n, m, q, k, etc.
* numeric value ranges
* string length constraints
* string alphabet constraints
* array length constraints
* graph restrictions
* tree restrictions
* whether graph is directed or undirected
* whether self-loops are allowed
* whether multi-edges are allowed
* whether graph connectivity is required
* whether total sum constraints exist
* whether duplicates are allowed
* whether zero is allowed
* whether negative values are allowed
* special validity constraints

If anything is unclear, list it under Assumptions.

Never silently invent constraints.

Never generate data that violates known constraints.

### 2. Search for testlib.h

Search the current project for `testlib.h`.

If found:

* record the path
* choose the correct include path
* continue

If missing:

* stop
* report the error
* do not generate files requiring testlib
* do not download anything

### 3. Read validator scope if available

If `validators/VALIDATION_SCOPE.md` exists:

* read it
* extract validator supported range
* extract complexity notes
* extract partially checked constraints
* extract not-checked constraints
* extract requirements for `stressor-gen-large`

If `validators/val.cpp` exists:

* plan to compile and run it

If validator is missing:

* continue only with clear warning
* do not claim mechanical legality

### 4. Parse invocation arguments and user prompt

Parse:

* `path_to_problem_statement`
* `--num-tests N`
* `--out-dir DIR`
* natural language generation requirements

If `--num-tests` is missing, choose a reasonable default, usually 10 to 15.

If `--out-dir` is missing, use:

```text
tests/large
```

If the user asks for a certain number of groups, generate exactly that many final large test files unless impossible.

If impossible, report why and generate the closest reasonable number.

Parse natural language requirements into concrete constraints such as:

* n range
* m range
* q range
* T preference
* value range
* alphabet size
* coordinate range
* graph density
* tree shape
* random/structured ratio
* boundary-heavy preference
* special structures

Then reconcile these requirements with:

1. statement constraints
2. validator scope
3. generator feasibility

### 5. Create generation plan

Before writing generators, create a generation plan.

The number of final planned tests must match `--num-tests N`.

Use this format:

```text
Test | Generator | Seed | Parameters | Purpose | User requirement covered | Validator required
01 | gen_large | 100001 | mode=0 n=100000 | medium high-entropy random | random baseline | yes if validator exists
02 | gen_large | 100002 | mode=1 n=200000 | duplicate-heavy large case | many duplicates | yes if validator exists
03 | gen_max | 100003 | mode=0 n=MAX_N | near-maximum boundary | max-size request | yes if validator exists
04 | gen_structured | 100004 | mode=chain n=MAX_N | chain structure | tree/graph chain | yes if validator exists
```

Every final test must have:

* generator
* seed
* explicit parameters
* purpose
* relation to user prompt or coverage plan

Do not generate large random data blindly.

### 6. Write generators

Create problem-appropriate generators.

At minimum, usually create:

```text
generators/gen_large.cpp
generators/gen_max.cpp
```

Optionally create:

```text
generators/gen_structured.cpp
```

or more problem-specific generators.

Generators must satisfy all testlib requirements and parameter discipline rules above.

### 7. Write generators/README.md

Document every generator and mode.

This documentation is mandatory.

### 8. Write generation script

Create:

```text
generators/gen_all_large.sh
```

The script must:

* use `set -euo pipefail`
* accept first argument as number of tests
* accept second argument as output directory
* default number of tests to the plan's chosen number
* default output directory to `tests/large`
* create `build/`
* create the output tests directory
* compile generators using the discovered testlib include path
* optionally compile validator if `validators/val.cpp` exists
* generate pilot tests first
* run validator on pilot tests if validator exists
* generate final tests only after pilot tests have been reviewed and accepted
* generate exactly the requested number of final test files
* immediately run validator on every final generated test if validator exists
* stop on the first generator or validator failure
* print which test is being generated
* print which test is being validated
* avoid silently overwriting unrelated files

Important:

The script can generate pilot tests and run validator on them.

The three-way AI legality review of pilot tests may require the agent to inspect pilot outputs after the script creates them. If fully automating this is not possible inside shell, the skill must instruct the agent to run the pilot generation phase first, perform three-way review, fix generators if needed, then run final generation.

Suggested script interface:

```bash
bash generators/gen_all_large.sh
bash generators/gen_all_large.sh 20
bash generators/gen_all_large.sh 20 tests/large
```

The actual script must be customized to the problem's generators and parameter schedule.

Do not leave a generic placeholder schedule.

### 9. Pilot-first execution protocol

When this skill is invoked for actual generation, follow this protocol:

1. Write generators and script.
2. Generate small pilot tests for each generator and important mode.
3. Inspect pilot test contents.
4. Run three independent legality-review subagents on every pilot.
5. If validator exists, run validator on every pilot.
6. If any pilot fails, fix generator or parameters and repeat.
7. Only after all pilots pass, generate the requested final large tests.
8. If validator exists, run validator on every final large test.
9. Report final results.

Do not skip pilot review.

Do not proceed to final large generation if pilot legality is unresolved.

### 10. Validation rule

If validator exists, every generated final large test must pass it.

If a final test fails validator:

* do not manually edit the generated test file
* inspect the validator failure
* inspect the generator
* inspect the statement
* inspect `VALIDATION_SCOPE.md` if available
* fix the generator or parameters if generated data is invalid or out of scope
* if validator appears too strict, report this but do not modify validator unless the user explicitly asks
* rerun generation and validation

This skill primarily owns generators, not validator.

Do not weaken or rewrite `validators/val.cpp` unless explicitly asked.

## Data Type Guidance

For array problems, include applicable large modes:

* large random high-entropy
* large low-entropy
* all equal if allowed
* many duplicates if allowed
* increasing
* decreasing
* almost sorted
* alternating high/low
* values near minimum
* values near maximum
* zero-heavy if zero allowed
* negative-heavy if negative allowed

For string problems, include applicable large modes:

* long random string
* all same character
* periodic string
* repeated blocks
* palindrome-like string
* alphabet size 1 if allowed
* full alphabet if allowed
* long common prefix/suffix structures

For graph problems, include applicable large modes:

* sparse random graph
* dense graph if allowed by constraints and validator scope
* chain-like graph
* star-like graph
* connected random graph if connectedness required
* disconnected graph if allowed
* many equal weights if weighted
* extreme small/large weights
* no self-loops unless allowed
* no duplicate edges unless allowed

For tree problems, include applicable large modes:

* chain
* star
* broom
* random tree
* balanced-like tree
* weighted repeated values if allowed
* extreme edge weights if weighted

For number theory problems, include applicable large modes:

* many primes
* many composites
* powers of two
* powers of a small prime
* pairwise coprime patterns
* large gcd patterns
* repeated values
* values near maximum

For geometry problems, include applicable large modes:

* random points
* collinear points if allowed
* grid-like points
* symmetric points
* vertical/horizontal structures
* small and large coordinate mixtures
* degenerate cases only if allowed

For query problems, include applicable large modes:

* many queries
* repeated queries
* full-range queries
* single-position queries
* first/last position queries
* update-heavy sequence if updates exist
* query-heavy sequence if queries exist
* alternating update/query sequence if applicable

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

### Role of `stressor-gen-large` in the export

* `stressor-gen-large` keeps writing generated data under `tests/large/`. That directory remains workflow-temporary.
* By default, **large tests are not exported** into `lightcp/problems/<pid>/testdata/`. They are scratch data used by `stressor-init`, `stressor-stress`, and brute-vs-optimized comparison.
* Only when the user explicitly asks to keep specific generated large tests as judge cases may a subset of `tests/large/*` be promoted to the LightCPVerifier package, and that promotion is performed by the export stage (owned by `stressor-init`), not by this skill.
* When the user does request it, the export stage maps each kept large test as:

```text
tests/large/01     -> lightcp/problems/<pid>/testdata/large_0001.in
tests/large/02     -> lightcp/problems/<pid>/testdata/large_0002.in
```

  and the corresponding `.ans` files are produced by `solutions/brute.cpp`, never by an optimized attempt. Tests that fall outside `solutions/BRUTE_LIMITS.json` cannot be exported by this pipeline because no jury answer can be reliably produced.

Strict rules for this skill in the LightCPVerifier context:

* `stressor-gen-large` must **not** generate `.ans` files.
* `stressor-gen-large` must **not** write `config.yaml`.
* `stressor-gen-large` must **not** write anything under `lightcp/problems/<pid>/`.
* `stressor-gen-large` must **not** copy `checker.cpp` or `statement.txt` into a LightCPVerifier package.
* `stressor-gen-large` must **not** auto-promote large tests into the LightCPVerifier package without explicit user request.

The export step is owned by `stressor-init` (or a dedicated export stage), not by `stressor-gen-large`.

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

`stressor-gen-large` never participates in this export and never writes `.ans` files for official samples. It also must not mix `statement/*.in` files into `tests/large/` so that the export stage can still treat `statement/` as the canonical sample source.

## Final Report Format

After using this skill, the final response must contain:

```text
Problem understanding:
...

Extracted constraints:
...

testlib.h:
- found: yes/no
- path: ...
- include path used: ...

Validator scope:
- VALIDATION_SCOPE.md found / not found
- supported range used: ...
- special generator requirements: ...

Existing validator:
- found / not found
- path: validators/val.cpp if found

User generation requirements:
- num-tests: ...
- output directory: tests/large
- requested ranges: ...
- requested special properties: ...
- conflicts or adjustments: ...

Files created:
- generators/gen_large.cpp
- generators/gen_max.cpp
- generators/gen_structured.cpp
- generators/gen_all_large.sh
- generators/README.md
- tests/large/...

Generator documentation:
- generators/README.md

Pilot tests:
- generator/mode: ...
- pilot file: ...
- Reviewer A: LEGAL / ...
- Reviewer B: LEGAL / ...
- Reviewer C: LEGAL / ...
- validator: PASS / NOT RUN
- final pilot status: ACCEPTED

Generation command:
bash generators/gen_all_large.sh N tests/large

Generation plan:
Test | Generator | Seed | Parameters | Purpose | User requirement covered | Validator result
...

Generated tests:
01 - seed=..., parameters=..., purpose=...
02 - seed=..., parameters=..., purpose=...
03 - seed=..., parameters=..., purpose=...

Validator results:
tests/large/01 - PASS / NOT RUN
tests/large/02 - PASS / NOT RUN
tests/large/03 - PASS / NOT RUN

If validator was not found:
- clearly state that final large tests were not mechanically validated

Requirement conflicts or adjustments:
- ...

Assumptions:
- ...

Not created:
- validator
- checker
- brute force
- standard solution
- wrong solutions
- stress testing
- answer files
```

## Strict Rules

* Use testlib for generators.
* Search for project-local `testlib.h` before writing generators.
* Stop with an error if `testlib.h` is missing.
* Default output directory is `tests/large`.
* Support `--num-tests N`.
* Generate exactly the requested number of final tests unless impossible.
* Support natural language generation requirements from the user's prompt.
* Follow statement constraints first.
* Follow `VALIDATION_SCOPE.md` if it exists.
* Every generator must call `registerGen(argc, argv, 1);`.
* Every generator must accept an explicit seed.
* Use testlib `rnd` for randomness.
* Do not use `rand()`.
* Do not rely on hidden randomness.
* Every final test must be generated from explicit seed and parameters.
* Provide `generators/README.md`.
* Generate pilot tests before final large tests.
* Every pilot test must pass three independent legality-review subagents.
* If validator exists, every pilot and every final test must pass validator.
* Do not proceed to final large generation if pilot legality is unresolved.
* Do not create validator.
* Do not create checker.
* Do not create brute force.
* Do not create standard solution.
* Do not create wrong solutions.
* Do not create answer files.
* Do not run solution stress testing.
* Do not manually patch generated output files.
* Fix generators or parameters instead of editing generated tests.
* Do not claim large data is mechanically legal unless validator passed.
* If validator does not exist, clearly report that validation was not run.
* Do not silently invent constraints.
* Do not generate data violating known constraints.
* Do not satisfy user-specified special properties if they violate the statement or validator scope.
* Every large test must have a clear purpose.
* When `lightcp/problems/<pid>/config.yaml` exists, generators for differential testing must respect `x-stressor.compatible_range`. Out-of-range data must not be used for brute comparison.
* `generators/README.md` must document each generator's supported parameter ranges and modes so `stressor-init` can fill the generator contribution to `x-stressor.compatible_range`.
