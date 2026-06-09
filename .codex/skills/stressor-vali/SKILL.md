---
name: stressor-vali
description: Write a testlib validator for ICPC/CCPC problems, document its validation scope and complexity, and test it against existing small handwritten tests from stressor-gen-small. Use when the user wants a validator that enforces statement constraints and clearly states what ranges or special properties it can check efficiently.
---

# Stressor Vali

## Purpose

This skill writes a `testlib.h` validator for an ICPC/CCPC style programming contest problem.

It also documents the validator's validation scope.

The validator should be used by later data-generation skills such as `stressor-gen-large`.

The validator must be based on the problem statement, not overfitted to current tests.

Existing small tests from `stressor-gen-small` are used as the first regression suite.

## Required Outputs

When this skill is invoked, create:

```text
validators/
├── val.cpp
└── VALIDATION_SCOPE.md

scripts/
└── validate_small.sh
```

`validators/val.cpp` is the actual testlib validator.

`validators/VALIDATION_SCOPE.md` explains what the validator checks, what it does not check, and the maximum data range it can check efficiently.

`scripts/validate_small.sh` compiles the validator and runs it on existing small tests.

## Forbidden Outputs

Do not create unless the user explicitly asks:

* generators/
* checkers/
* solutions/
* stress/
* answers/
* large tests
* standard solution
* brute force solution
* wrong solutions
* checker
* answer files

This skill must not generate new tests.

This skill must not create large data.

This skill must not create checker, brute force, standard solution, wrong solution, stress testing, or answer files.

## Invocation

Preferred invocation:

```text
$stressor-vali path_to_problem_statement
```

Optional second argument:

```text
$stressor-vali path_to_problem_statement tests_dir
```

If `tests_dir` is omitted, use:

```text
tests/small/
```

This default matches the output directory of `stressor-gen-small`. Handwritten small tests live under `tests/small/`; larger test sets produced by later skills live under sibling directories such as `tests/large/`.

Treat the first argument as `path_to_problem_statement`.

Read the problem statement from that path first.

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

## Validator Must Check Official Samples

When writing or repairing `validators/val.cpp`, the validator must be tested against official sample input files from the statement directory when possible.

Sample sources include:

* samples embedded in `statement.md`, if they can be reliably extracted as complete input files
* sample input files under `statement/`, such as:

  * `ex_prefix1.in`
  * `sample1.in`
  * `example1.in`
  * `*.in`
  * `*.input`

The validator should run on official sample inputs if they are complete input files.

If official sample input files are found and their data ranges are within the statement constraints and within validator supported range, they must pass validator.

If a sample fails validator, do not blindly weaken the validator.

Triage the failure into one of:

* `VALIDATOR_TOO_STRICT`
* `SAMPLE_IS_NOT_COMPLETE_INPUT`
* `SAMPLE_OUT_OF_SCOPE_FOR_VALIDATOR`
* `SAMPLE_VIOLATES_STATEMENT`
* `STATEMENT_AMBIGUOUS`
* `TOOLING_OR_PATH_ERROR`

Resolution rules:

* If the sample is a complete official input and is within constraints, prefer fixing the validator.
* If the sample is not a complete input file (e.g. only a fragment of `statement.md`), report it and do not force validator acceptance.
* If the sample is outside `VALIDATION_SCOPE.md`, report the scope mismatch and explain whether validator scope should be expanded.
* If the sample appears to violate the statement, report the contradiction clearly.

Optional sample-validation invocation pattern (do not create scripts now; this is just documented behavior for future versions of `scripts/validate_small.sh`):

```bash
bash scripts/validate_small.sh tests/small
bash scripts/validate_small.sh statement
```

A future revision of `scripts/validate_small.sh` may accept a statement-directory argument to validate official sample input files; until then, the agent should run the compiled validator directly on each official sample input file and record the results.

## Core Principle

The validator must follow the statement.

The validator must be general for all legal inputs under the statement whenever this can be checked efficiently.

Do not overfit the validator to existing small tests.

Do not weaken the validator just to accept current tests.

Do not silently ignore expensive or ambiguous constraints.

If some statement constraint cannot be checked efficiently, clearly document it in `validators/VALIDATION_SCOPE.md`.

If the validator only supports a subset of the theoretical statement range, clearly document the supported range and the reason.

## Testlib Location Requirement

The validator must `#include "testlib.h"`. Before writing or compiling `validators/val.cpp`, locate the project-local `testlib.h`.

Search these patterns in order (take the first match):

```text
./testlib.h
./validators/testlib.h
./lib/testlib.h
./third_party/testlib.h
./third_party/testlib/testlib.h
../testlib.h
../third_party/testlib.h
../third_party/testlib/testlib.h
../../third_party/testlib.h
../../third_party/testlib/testlib.h
```

The last entries cover multi-problem layouts where `testlib.h` is shared one or two directories above the current problem.

If none match, fall back to:

```bash
find . -maxdepth 4 -name testlib.h
find .. -maxdepth 3 -name testlib.h
find ../.. -maxdepth 3 -name testlib.h
```

If `testlib.h` is still not found:

* stop
* report that `testlib.h` is required
* do not write `validators/val.cpp` (the file is useless without testlib)
* do not download `testlib.h` or vendor external files unless explicitly asked

Record the **directory** containing `testlib.h` (the value passed to `-I`). The validation script (`scripts/validate_small.sh`) must read this through a `TESTLIB_INCLUDE` environment variable with a sensible default so the same script works from any problem directory in the repo. Never hard-code `-I.` unless `testlib.h` is actually at the project root.

## Testlib Requirements

Create:

```text
validators/val.cpp
```

The validator must:

* include `#include "testlib.h"`
* call `registerValidation(argc, argv);`
* use `inf.readInt`, `inf.readLong`, `inf.readToken`, `inf.readSpace`, `inf.readEoln`, and `inf.readEof`
* strictly check input format
* strictly check all cheap and practical constraints from the statement
* use `ensuref` or equivalent testlib checks for semantic constraints
* call `setTestCase(tc)` for multi-testcase inputs
* check total sum constraints if present
* check graph restrictions if present
* check tree restrictions if present
* check string length and alphabet restrictions if present
* check uniqueness constraints if present
* check no extra tokens at EOF

Prefer C++17.

Use readable helper functions.

Examples:

* `readArray`
* `readPermutation`
* `readTree`
* `readGraph`
* `checkConnected`
* `checkNoDuplicateEdges`
* `checkAlphabet`
* `readTestCase`

Prefer named constants for constraints.

Example:

```cpp
const int MIN_N = 1;
const int MAX_N = 200000;
```

If constraints are unknown or ambiguous, use a clearly marked assumption and report it.

Do not silently invent constraints.

## Validator Complexity Requirement

Before finalizing `val.cpp`, analyze its complexity.

The validator should usually be:

* O(input size)
* O(input size log input size)
* or another clearly justified efficient complexity

For large official data, avoid validators that are:

* exponential
* quadratic on large n or m unless constraints are tiny
* dependent on solving the original problem
* dependent on expensive optimization or NP-hard checks
* overly memory-heavy

If a required property is expensive to check, do not pretend it is fully checked.

Instead:

1. Check the cheap necessary conditions.
2. Document the unchecked or partially checked property in `VALIDATION_SCOPE.md`.
3. Explain whether the generator must guarantee that property.
4. Explain whether an additional offline checker or custom verification step is needed.

Examples:

* If checking graph connectivity is required, this is cheap: check it with DFS/DSU.
* If checking “the graph is planar” is required and constraints are large, do not implement a fragile or expensive check unless clearly feasible.
* If checking “there exists a valid schedule” is equivalent to solving the problem, do not put that into the validator unless the statement explicitly makes it a simple input constraint and it is efficiently checkable.
* If checking “all points form a strictly convex polygon in order” is required, implement a robust O(n) or O(n log n) check if feasible, and document numeric assumptions.

## Required Workflow

### 1. Read the problem statement from scratch

Read the statement from `path_to_problem_statement`.

Extract:

* input format
* whether there is T
* bounds on T
* bounds on n, m, q, k, etc.
* numeric value ranges
* whether zero is allowed
* whether negative values are allowed
* whether duplicate values are allowed
* array length constraints
* string length constraints
* string alphabet constraints
* graph restrictions
* tree restrictions
* whether graph is directed or undirected
* whether self-loops are allowed
* whether multi-edges are allowed
* whether graph connectivity is required
* whether total sum constraints exist
* any special validity constraints

List all assumptions explicitly.

### 2. Classify constraints by checkability

Before writing code, classify every extracted constraint into one of:

* CHECKED_EXACTLY
* CHECKED_NECESSARY_CONDITIONS_ONLY
* NOT_CHECKED_TOO_EXPENSIVE
* NOT_CHECKED_AMBIGUOUS
* NOT_APPLICABLE

Use this table:

```text
Constraint | Status | Planned check | Complexity | Notes
n range | CHECKED_EXACTLY | readInt(MIN_N, MAX_N) | O(1) | -
array value range | CHECKED_EXACTLY | readLong(L, R) | O(n) | -
no duplicate edges | CHECKED_EXACTLY | set of normalized edges | O(m log m) | -
connected graph | CHECKED_EXACTLY | DSU/DFS | O(n + m) | -
special feasibility property | NOT_CHECKED_TOO_EXPENSIVE | generator must guarantee | - | equivalent to solving problem
```

Do not skip this classification.

### 3. Inspect existing small tests

Read all files under `tests_dir`.

Usually this is:

```text
tests/small/01
tests/small/02
tests/small/03
...
```

Do not assume they are valid just because they exist.

Use them as regression inputs after writing the validator.

Do not create tests in this skill.

### 4. Write validators/val.cpp

Implement the validator according to the statement and the checkability plan.

Do not overfit to the current small tests.

Do not hardcode the number of current tests.

Do not hardcode values that only appear in current tests unless they are actual constraints from the statement.

Make the validator general for legal inputs under the statement, subject to the documented validation scope.

### 5. Write validators/VALIDATION_SCOPE.md

Create:

```text
validators/VALIDATION_SCOPE.md
```

It must contain:

```markdown
# Validation Scope

## Statement Source

- Problem statement: ...
- Validator file: validators/val.cpp

## Supported Input Range

Describe the data range this validator is intended to check efficiently.

Example:

- T up to ...
- n up to ...
- m up to ...
- q up to ...
- sum n up to ...
- sum m up to ...
- value ranges ...
- string lengths ...
- graph size ...

## Complexity

State validator complexity.

Example:

- Time: O(total_n + total_m log total_m)
- Memory: O(total_n + total_m)

## Checked Exactly

List all constraints that are fully checked.

Examples:

- input format
- integer ranges
- array lengths
- string alphabet
- no self-loops
- no duplicate edges
- tree has n - 1 edges
- graph connectivity
- sum constraints
- EOF / no extra tokens

## Partially Checked

List constraints where only necessary conditions are checked.

For each one, explain:

- what is checked
- what is not checked
- why full checking is not done
- what the generator must guarantee

## Not Checked

List constraints not checked by the validator.

For each one, explain:

- reason
- risk
- whether generator must guarantee it
- whether an extra offline checker is recommended

## Assumptions

List all assumptions made because the statement was incomplete or ambiguous.

## Notes for stressor-gen-large

Explain what `stressor-gen-large` must respect when generating large tests.

If validator can check all statement constraints efficiently, say so clearly.

If not, clearly say which properties are trusted to the generator.

## Official Sample Validation

- Sample directory: ...
- Sample inputs found:
  - ...
- Samples validated:
  - ...
- Samples skipped:
  - ...
- Failures / reasons:
  - ...

## Machine-Readable Summary for stressor-init

```yaml
supported_range:
  T:
    min:
    max:
  n:
    min:
    max:
  m:
    min:
    max:
  q:
    min:
    max:
  sum_n:
    max:
  sum_m:
    max:
  value_abs_max:
    max:
  string_length:
    max:
special_requirements:
  - ...
unsupported:
  - ...
complexity:
  time: ...
  memory: ...
```

If exact values are unknown, write `null` and explain in the prose sections above. `stressor-init` reads this block to fill `x-stressor.sources.validator` and intersect into `x-stressor.compatible_range`.
```

This file is mandatory.

Do not omit it.

### 6. Write scripts/validate_small.sh

Create:

```text
scripts/validate_small.sh
```

The script must:

* compile validators/val.cpp
* find all files in the selected tests directory
* run validator on each test file
* stop on the first validator failure
* print which file failed
* print success only if all tests passed

Use this interface:

```bash
bash scripts/validate_small.sh
bash scripts/validate_small.sh tests/small
bash scripts/validate_small.sh tests/large
```

Suggested script:

```bash
#!/usr/bin/env bash
set -euo pipefail

TESTS_DIR="${1:-tests/small}"
TESTLIB_INCLUDE="${TESTLIB_INCLUDE:-../third_party/testlib}"

mkdir -p build

g++ -std=c++17 -O2 -pipe -I"$TESTLIB_INCLUDE" validators/val.cpp -o build/val

found=0
for f in "$TESTS_DIR"/*; do
    [ -f "$f" ] || continue
    found=1
    echo "Validating $f"
    ./build/val < "$f"
done

if [ "$found" -eq 0 ]; then
    echo "No test files found in $TESTS_DIR"
    exit 1
fi

echo "All tests in $TESTS_DIR passed validator."
```

Replace the default `TESTLIB_INCLUDE` value with whatever directory the testlib-search step actually located.

### 7. Run validator on small tests

After writing the validator and script, run:

```bash
bash scripts/validate_small.sh tests_dir
```

If all tests pass, report success.

If a test fails, do not immediately weaken the validator.

Perform failure triage.

### 8. Failure triage

For every failing test:

1 repeat until it passes or another issue appears

If VALIDATOR_TOO_LOOSE_OR_BUGGY:

* fix validators/val.cpp
* update VALIDATION_SCOPE.md if needed
* rerun the tests

If TEST_IS_INVALID:

* do not weaken the validator
* report the test file and the exact reason it violates the statement
* recommend fixing it through `stressor-gen-small`

If STATEMENT_AMBIGUOUS:

* report the ambiguity
* choose the safer interpretation only if justified
* mark the assumption in VALIDATION_SCOPE.md and final report

If TOOLING_OR_PATH_ERROR:

* fix the script or include path
* do not change validator semantics unnecessarily

### 9. Validator self-review

Before finalizing, review the validator against the extracted constraints.

Check:

* Does it read exactly the required input format?
* Does it reject extra tokens?
* Does it enforce all numeric ranges?
* Does it enforce all length constraints?
* Does it enforce all sum constraints?
* Does it enforce graph/tree constraints?
* Does it handle T correctly?
* Does it use `setTestCase(tc)` when T exists?
* Does it avoid accepting invalid duplicates/self-loops if forbidden?
* Does it avoid rejecting legal small corner cases?
* Does VALIDATION_SCOPE.md accurately describe what is checked and not checked?
* Is the validator fast enough for the stated supported range?

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

This skill (`stressor-vali`) is consulted during the export stage so that every exported `testdata/*.in` can be validated. The validator itself is **not** copied into the LightCPVerifier package — only `checker.cpp` is. This skill does not write `config.yaml` or `statement.txt` and does not generate `.ans` files.

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

`stressor-vali`'s role in this context is to validate `statement/*.in` candidates before they are exported. The validator never reads `statement/*.out` and never produces `.ans` files.

### 10. Final report format

After using this skill, the final response must contain:

```text
Problem understanding:
...

Extracted constraints:
...

Constraint checkability:
Constraint | Status | Check | Complexity | Notes
...

Existing small tests inspected:
...

Files created:
- validators/val.cpp
- validators/VALIDATION_SCOPE.md
- scripts/validate_small.sh

Validation command:
bash scripts/validate_small.sh tests/small

Small-test validation result:
tests/small/01 - PASS
tests/small/02 - PASS
tests/small/03 - PASS
...

Validator supported range:
- T: ...
- n: ...
- m: ...
- q: ...
- sum constraints: ...
- value ranges: ...

Validator complexity:
- Time: ...
- Memory: ...

Checked exactly:
- ...

Partially checked:
- ...

Not checked:
- ...

Failures fixed:
- ...

Tests rejected as invalid:
- ...

Ambiguities / assumptions:
- ...

Notes for stressor-gen-large:
- ...

Official sample validation:
- sample input files found: ...
- passed validator: ...
- skipped: ...
- failed: ...
- reasons: ...

Not created:
- generators
- checker
- brute force
- standard solution
- wrong solutions
- stress testing
- answer files
- large data
```

## Strict Rules

* Must write validators/val.cpp when invoked.
* Must write validators/VALIDATION_SCOPE.md when invoked.
* Must write scripts/validate_small.sh when invoked.
* Do not generate new tests.
* Do not generate large data.
* Do not write generator files.
* Do not write checker.
* Do not write brute force.
* Do not write standard solution.
* Do not write wrong solutions.
* Do not write answer files.
* Do not silently invent constraints.
* Do not skip constraint checkability classification.
* Do not skip VALIDATION_SCOPE.md.
* Do not claim all constraints are checked unless they really are.
* Do not claim the validator supports the full statement range unless it is efficient for that range.
* Do not weaken the validator just to accept existing tests.
* Do not assume existing tests are valid without checking the statement.
* Do not skip validation against existing small tests if tests exist.
* If small tests fail, triage the failure before changing code.
* If a test is invalid, report it instead of making the validator accept it.
* Keep validator general for all legal inputs, subject to documented validation scope.
