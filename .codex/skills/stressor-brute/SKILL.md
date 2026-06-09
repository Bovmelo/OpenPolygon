---
name: stressor-brute
description: Write a correctness-first brute force or reference solution for ICPC/CCPC problems, with documented complexity and machine-readable runnable limits for testcase generation. Use when the user wants a reliable oracle for small or controlled tests, not an optimized contest solution.
---

# Stressor Brute

## Purpose

This skill writes a correctness-first brute force or reference solution for an ICPC/CCPC style programming contest problem.

The goal is correctness and clarity, not optimal performance.

The brute solution may only support small or medium inputs.

It should be suitable as an oracle for:

- small hand-written tests from `stressor-gen-small`
- future stress testing
- comparing with optimized solutions
- generating trusted outputs for small inputs
- validating understanding of the statement
- helping testcase generators choose cases that the brute can actually run

This skill must not try to be clever unless cleverness is necessary for correctness.

Prefer simple exhaustive search, direct simulation, simple dynamic programming, BFS/DFS over state space, Floyd-Warshall, bitmask enumeration, permutation enumeration, or other obviously correct methods.

## Scope

Allowed output when this skill is invoked:

```text
solutions/
├── brute.cpp
├── BRUTE_SCOPE.md
└── BRUTE_LIMITS.json

scripts/
└── run_brute_on_tests.sh
```

Optional if useful:

```text
scripts/compare_brute_with_samples.sh
```

Forbidden output unless explicitly asked:

```text
generators/
validators/
checkers/
stress/
answers/
large tests
optimized solution
wrong solutions
standard solution
```

This skill must not generate tests.

This skill must not write generators.

This skill must not write validator.

This skill must not write checker.

This skill must not write optimized solution unless the user explicitly asks, or unless the optimized algorithm is also the simplest exact reference method.

## Invocation

Preferred invocation:

```text
$stressor-brute path_to_problem_statement
```

Optional second argument:

```text
$stressor-brute path_to_problem_statement tests_dir
```

If `tests_dir` is omitted, use:

```text
tests/small/
```

This default matches the output directory of `stressor-gen-small` and the convention used by `stressor-init`, `stressor-vali`, and `stressor-stress`. Pass a different directory only when the user explicitly asks.

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

## Brute Must Pass Official Samples When Runnable

When writing or repairing `solutions/brute.cpp`, the brute must be tested against official samples when possible.

Official sample sources include:

* embedded samples in the statement, if reliably extractable
* paired sample files under `statement/`, such as:

  * `ex_prefix1.in` + `ex_prefix1.out`
  * `sample1.in` + `sample1.out`
  * `example1.in` + `example1.out`

If an official sample input is within `solutions/BRUTE_LIMITS.json` and the sample has a matching official output file, brute output must be checked using `checkers/checker.cpp` when checker is available.

Checker invocation:

```bash
./build/checker sample.in brute.out sample.out
```

Here:

* `sample.in` is the official sample input
* `brute.out` is participant output (the brute's output on `sample.in`)
* `sample.out` is jury answer (the official statement's expected output)

Do not use plain `diff` unless the checker is unavailable and exact unique output is explicitly known. Prefer checker-based validation.

If checker is not yet available at brute-writing time:

* still run brute on the sample if possible
* record sample checking as pending checker validation
* `stressor-init` should later run checker-based sample validation after checker is created

If a sample is outside brute supported range:

* do not force brute to run it
* report it as `SAMPLE_OUT_OF_BRUTE_SCOPE`
* explain using `BRUTE_LIMITS.json`

If brute fails an official sample within supported range:

* do not accept the brute
* fix `solutions/brute.cpp`
* rerun sample check
* if unresolved, report failure

## Core Principle

Correctness comes first.

Do not write an optimized solution unless the user explicitly asks for it, or unless the optimized algorithm is also the simplest exact reference method.

The goal is not to AC the original problem.

The goal is to create a trustworthy oracle for small or controlled test cases.

Do not infer hidden rules from sample outputs.

Do not reverse-engineer the intended logic from samples.

Do not hardcode sample behavior.

Samples may only be used as sanity checks after the algorithm is derived from the statement.

If the statement is ambiguous, report the ambiguity instead of guessing silently.

Do not silently assume constraints.

Do not implement a heuristic unless the problem itself allows heuristic output.

If a completely general brute force is infeasible even for small meaningful cases, create the simplest exact algorithm with a clearly documented supported range.

If no exact brute force is feasible, stop and report why.

## Required Outputs

When invoked, create:

```text
solutions/brute.cpp
solutions/BRUTE_SCOPE.md
solutions/BRUTE_LIMITS.json
scripts/run_brute_on_tests.sh
```

`solutions/brute.cpp` is the brute force / reference solution.

`solutions/BRUTE_SCOPE.md` documents the algorithm, correctness argument, complexity, supported input range, limitations, and reviewer results.

`solutions/BRUTE_LIMITS.json` gives machine-readable recommended limits for generating testcases that this brute can run within reasonable time.

`scripts/run_brute_on_tests.sh` compiles and runs brute on existing tests.

If no reliable brute can be produced, do not create `solutions/brute.cpp`. Instead, report failure clearly.

## Language

Prefer C++17.

Use simple, portable code.

Avoid unnecessary macros.

Avoid undefined behavior.

Use `long long` or wider integer types when needed.

If the problem requires arbitrary precision and C++ built-ins are unsafe, either use a clearly correct approach such as `boost::multiprecision::cpp_int`, or document the limitation.

## Oracle Reliability Rules

The brute solution is an oracle, so reliability is more important than speed.

Rules:

* Do not infer hidden rules from samples only.
* Do not hardcode sample behavior.
* Do not use randomized algorithms.
* Do not use heuristics.
* Do not rely on hash collision assumptions.
* Do not rely on floating hash.
* Avoid `unordered_map` / `unordered_set` when deterministic containers are just as simple.
* Do not silently produce output on unsupported input sizes.
* For unsupported input, print a clear error to stderr and exit nonzero.
* For construction problems, verify the constructed output internally when feasible.
* For non-unique outputs, define a canonical output strategy or state that a checker is required.
* For floating-point outputs, document precision and comparison requirements.
* Prefer deterministic, simple, obviously correct methods.

Never present a partial, heuristic, or uncertain solution as a correct oracle.

## Required Workflow

### 1. Read the problem statement from scratch

Read the target statement from `path_to_problem_statement`.

Extract:

* input format
* output format
* whether there is T
* bounds on T
* bounds on n, m, q, k, etc.
* value ranges
* whether zero is allowed
* whether negative values are allowed
* whether duplicates are allowed
* whether output is unique
* whether multiple valid outputs are allowed
* whether special judge is needed
* whether answers are numeric, floating-point, construction, path, graph, sequence, etc.
* sample inputs and outputs if present
* any edge cases implied by the statement

List all assumptions explicitly.

Never silently invent constraints.

Never derive problem rules only from sample outputs.

### 2. Use multiple independent brute-design subagents

Before finalizing `solutions/brute.cpp`, try multiple independent approaches.

Use at least three independent brute-design subagents when possible:

* brute-designer-A
* brute-designer-B
* brute-designer-C

Each brute designer must:

* reread the problem statement from scratch
* propose a correctness-first brute or reference algorithm
* avoid optimized contest solutions unless necessary
* avoid using sample outputs to infer hidden rules
* state the algorithm
* state why it is correct
* state time complexity
* state memory complexity
* state supported input range
* state limitations
* state concerns

Each designer must output:

```text
Designer A:
Status: SOLVED / PARTIAL / FAILED
Algorithm:
Correctness argument:
Complexity:
Supported range:
Concerns:
```

Same for Designer B and Designer C.

After receiving all designs:

1. Compare the proposed algorithms.
2. Prefer the simplest exact algorithm with the clearest correctness argument.
3. If multiple algorithms agree, use the most reliable and readable one.
4. If one algorithm is suspicious, do not use it unless concerns are resolved.
5. If all designers fail, do not fabricate a brute solution.
6. If all designers only produce partial solutions, report the limitation clearly.

### 3. Failure handling

If no reliable brute force or exact reference solution can be produced:

* do not create `solutions/brute.cpp`
* do not pretend a heuristic is correct
* do not write an optimized solution just to have something
* do not infer rules from sample outputs
* report why a reliable brute could not be produced
* list the ambiguous or difficult parts of the statement
* list what additional information would be needed
* optionally suggest a smaller subproblem that could have a brute oracle

If a partial brute is possible only for a restricted subcase, create it only if clearly useful, and document the limitation in `BRUTE_SCOPE.md` and `BRUTE_LIMITS.json`.

Never present a partial or heuristic solution as a correct oracle.

### 4. Design a correctness-first algorithm

Before writing code, design a brute force or simple reference algorithm.

Prefer methods such as:

For array / sequence problems:

* enumerate all subsets
* enumerate all intervals
* enumerate all pairs/triples
* try all permutations if n is tiny
* direct simulation
* O(n^2), O(n^3), or O(2^n) if supported range is small

For graph problems:

* Floyd-Warshall for all-pairs shortest path
* BFS/DFS from every node
* enumerate subsets of vertices/edges
* brute force all paths only when n is tiny
* DSU/DFS for direct property checks
* min-cut/max-flow only if it is simpler and trustworthy for the brute

For tree problems:

* root each node if needed
* enumerate paths
* compute answers by DFS from every node
* brute force all pairs
* simple DP over tree only if clearly correct

For string problems:

* enumerate substrings
* direct matching
* simple DP
* try all split points
* compare strings directly
* avoid complicated hashing if exact comparison is simpler

For number theory problems:

* trial division
* enumerate divisors
* enumerate possible values
* direct gcd/lcm checks with overflow protection
* use arbitrary precision if exactness requires it

For geometry problems:

* direct O(n^2) or O(n^3) checks
* exact integer arithmetic if possible
* avoid fragile floating-point comparisons
* if floating-point is unavoidable, document tolerance

For query problems:

* process queries naively
* update arrays directly
* answer each query by scanning the relevant range
* avoid segment tree/Fenwick unless needed for clarity

For optimization problems:

* enumerate all candidates if possible
* use simple DP if enumeration is too large
* verify objective directly
* output the best by comparing all possibilities

For construction problems:

* find a valid object by exhaustive search/backtracking if possible
* verify the constructed object before printing
* if no object exists, print the required impossible output

For decision problems:

* directly test the condition by enumeration or simulation

### 5. Define supported brute range

Before finalizing code, define the input range for which this brute is intended.

The brute does not need to support the original maximum constraints.

It must honestly document what it can run.

Examples:

```text
Supported brute range:
- n <= 12 for subset enumeration
- n <= 8 for permutation enumeration
- n <= 300 for O(n^3) Floyd-Warshall
- total input size small enough for O(n^2)
```

If the statement maximum is larger than the brute range, this is acceptable.

Document it clearly.

The brute should still parse the official input format correctly.

If the input exceeds the supported brute range, choose one of:

1. Still run if it is safe.
2. Print an error to stderr and exit with nonzero status.
3. Use assertions in debug-like scripts.

Prefer not to produce silently wrong output on unsupported ranges.

## Brute Complexity and Runnable Test Range Requirement

The brute solution must explicitly provide:

1. Time complexity
2. Memory complexity
3. Supported input range
4. Recommended testcase generation limits
5. Unsafe or unsupported ranges

The goal is to let later skills, especially testcase generation skills, create tests that the brute can actually run.

Do not only say “exponential” or “slow”.

Give concrete estimates.

Examples:

* O(2^n * n): recommended n <= 20
* O(n! * n): recommended n <= 9
* O(n^3): recommended n <= 500 or n <= 1000 depending on constants
* O(n^2): recommended n <= 5000 or n <= 10000 depending on constants
* O(n * m): recommended n * m <= 5e7
* O(T * n^2): recommended sum of n^2 over all test cases <= 2e7
* O(3^n): recommended n <= 16
* O(V * (V + E)) BFS from every node: recommended V <= 3000 for sparse graphs, smaller for dense graphs

The supported range must be conservative.

Prefer underestimating safe limits over producing tests that hang.

If the brute has different behavior for different problem types or modes, document each one separately.

If the problem has multiple test cases, provide limits both per test case and over the whole input file.

Examples:

* per testcase: n <= 12
* total over input: sum 2^n <= 2e7
* total edges: sum m <= 5000
* total n^3 over all cases <= 1e8

If the brute intentionally exits on unsupported large inputs, describe the condition.

## Timeout and Runnable Range

The brute must provide conservative runnable limits.

The script should support a timeout to avoid hanging.

The default timeout is only a safety guard, not a proof of complexity.

The brute should document both per-testcase limits and whole-file limits.

For multiple test cases, estimate the total work across all test cases, not just the maximum single case.

## Non-Unique Output Rules

For non-unique output problems, the brute must define a canonical valid output strategy when possible.

Examples:

* choose lexicographically smallest solution
* choose the first solution found by DFS
* choose the minimum-index valid object
* output any valid construction after verifying it internally

If output validity cannot be checked by exact diff, state that a checker is required for comparison.

Do not claim exact diff is valid for non-unique output unless the brute's output is required to match a unique canonical answer.

## Construction Problem Rules

For construction problems, after constructing an answer, the brute should internally verify that the constructed object satisfies the statement whenever feasible.

If verification fails:

* print an internal error to stderr
* exit with nonzero status
* do not output an invalid construction

If no valid construction exists, print the required impossible output.

## Floating-Point Rules

For floating-point problems, document:

* whether the brute computes exact rational/integer values or floating-point values
* the tolerance used
* whether outputs are suitable for exact diff
* whether approximate checking is required

If exact rational arithmetic is feasible, prefer exact arithmetic.

If floating-point is unavoidable, use a conservative precision strategy and document it.

## Write solutions/brute.cpp

Create:

```text
solutions/brute.cpp
```

Requirements:

* parse input exactly as the statement specifies
* produce output exactly as the statement requiresunless it is also the simplest correct reference method.

## Correctness Self-Review

After writing the brute code, perform a self-review.

Check:

* Does it parse the input format exactly?
* Does it handle T correctly?
* Does it handle minimum cases?
* Does it handle repeated values?
* Does it handle zero or negative values if allowed?
* Does it handle disconnected graphs if allowed?
* Does it avoid overflow?
* Does it avoid relying on ordering assumptions?
* Does it produce valid output format?
* Does it work for non-unique outputs?
* Does it return impossible cases correctly?
* Does it reject or safely handle unsupported ranges?
* Does it have documented complexity and runnable limits?

## Three Independent Correctness Reviewers

The brute solution must be reviewed by three independent correctness-review subagents:

* brute-reviewer-A
* brute-reviewer-B
* brute-reviewer-C

Each reviewer must:

* reread the problem statement from scratch
* inspect `solutions/brute.cpp`
* not rely on the author's explanation
* not rely on other reviewers
* check whether the algorithm is exact
* check whether the input/output format is correct
* check whether edge cases are handled
* check whether unsupported ranges are documented
* check whether complexity and runnable limits are realistic
* check whether overflow risks exist
* check whether construction outputs are valid if applicable
* check whether non-unique outputs require a checker
* check whether floating-point outputs need approximate comparison
* mark the solution SUSPICIOUS if correctness is not clear

Each reviewer must output:

```text
Reviewer A:
Status: CORRECT / SUSPICIOUS / INCORRECT
Reason:
Checked items:
- ...
Concerns:
- ...
```

Same for Reviewer B and Reviewer C.

The brute can be accepted only if all three reviewers explicitly return CORRECT or if all concerns are resolved and the review is rerun.

If any reviewer returns SUSPICIOUS or INCORRECT:

* do not accept the brute
* fix the algorithm or code
* rerun the three reviews
* accept only after all three reviewers return CORRECT

## Write solutions/BRUTE_SCOPE.md

Create:

```text
solutions/BRUTE_SCOPE.md
```

It must contain:

```markdown
# Brute Force Scope

## Statement Source

- Problem statement: ...
- Brute file: solutions/brute.cpp

## Algorithm

Describe the brute force / reference algorithm.

## Correctness Argument

Explain why the algorithm returns the correct answer.

Use clear reasoning, not just “it is brute force”.

## Complexity

- Time: ...
- Memory: ...

Explain the complexity in terms of the actual input variables.

For multiple test cases, also state the total cost across all test cases.

## Recommended Runnable Test Range

These are conservative limits for generating tests that this brute can run.

- T <= ...
- n <= ...
- m <= ...
- q <= ...
- sum n <= ...
- sum m <= ...
- value range <= ...

## Global Work Budget

Examples:

- sum over test cases of n^3 <= 1e8
- sum over test cases of 2^n * n <= 2e7
- sum over test cases of n * m <= 5e7

## Output Type

State whether output is:

- unique exact answer
- non-unique construction
- floating-point answer
- yes/no decision
- sequence/path/graph construction

If output is non-unique, explain how the brute chooses one valid output.

If exact diff is not appropriate, say that a checker is required.

## Unsupported or Dangerous Ranges

List cases where brute may be too slow or intentionally refuses to run.

## Overflow / Precision Notes

Explain integer width or floating-point tolerance choices.

## Notes for Testcase Generators

- stressor-gen-small should ...
- stressor-gen-large should not use this brute unless ...
- generated tests for brute comparison should satisfy ...

## Reviewer Results

Summarize the three independent correctness reviews.

## Official Sample Checks

- Sample directory: ...
- Sample pairs found:
  - ...
- Samples run:
  - ...
- Checker used: yes/no
- Passed:
  - ...
- Skipped:
  - ...
- Failures:
  - ...
```

Do not omit this file.

## Write solutions/BRUTE_LIMITS.json

Create:

```text
solutions/BRUTE_LIMITS.json
```

This file is **mandatory** whenever a reliable brute is produced. It must be valid JSON and contain enough machine-readable information for `stressor-init` to compute `x-stressor.compatible_range` inside the LightCPVerifier `config.yaml`.

Use this structure when applicable:

```json
{
  "time_complexity": "...",
  "memory_complexity": "...",
  "recommended_limits": {
    "T": null,
    "n": null,
    "m": null,
    "q": null,
    "sum_n": null,
    "sum_m": null,
    "value_abs_max": null,
    "string_length": null
  },
  "global_work_budget": {
    "formula": "...",
    "max_estimated_operations": null
  },
  "unsupported_if": [
    "..."
  ],
  "notes_for_generators": [
    "..."
  ],
  "output_comparison": {
    "exact_diff_ok": true,
    "requires_checker": false,
    "reason": "unique exact output"
  },
  "lightcp_export": {
    "can_generate_jury_answers": true,
    "notes": "Only cases within recommended limits should be exported."
  }
}
```

Adapt the keys to the problem.

Do not include fake parameters that do not exist in the problem.

Only declare problem variables that actually exist; use `null` for fields that the problem does not have rather than inventing them.

The JSON must be useful for testcase generators to choose runnable small cases **and** for `stressor-init` to fill `x-stressor.sources.brute` and intersect into `x-stressor.compatible_range`.

If output is non-unique, set:

```json
"exact_diff_ok": false,
"requires_checker": true
```

If floating-point comparison is required, document tolerance in JSON.

Additionally, the JSON should note whether official samples (from `statement/`) are expected to be runnable by this brute. Suggested extension:

```json
"official_samples": {
  "expected_runnable": true,
  "notes": "All discovered statement/*.in pairs are within the recommended limits."
}
```

Set `"expected_runnable": false` when at least one official sample input is outside the recommended limits, and explain which sample(s) are out of scope.

## Write scripts/run_brute_on_tests.sh

Create:

```text
scripts/run_brute_on_tests.sh
```

The script must:

* compile `solutions/brute.cpp`
* run it on every file in a selected tests directory
* write outputs to a selected output directory
* stop on runtime error
* support timeout
* print which file is being processed
* report unsupported input failures clearly

Suggested interface:

```bash
bash scripts/run_brute_on_tests.sh
bash scripts/run_brute_on_tests.sh tests
bash scripts/run_brute_on_tests.sh tests outputs/brute
TIMEOUT=20s bash scripts/run_brute_on_tests.sh tests outputs/brute
```

Suggested script:

```bash
#!/usr/bin/env bash
set -euo pipefail

TESTS_DIR="${1:-tests/small}"
OUT_DIR="${2:-outputs/brute}"
TIMEOUT_LIMIT="${TIMEOUT:-10s}"

mkdir -p build "$OUT_DIR"

g++ -std=c++17 -O2 -pipe solutions/brute.cpp -o build/brute

found=0
for f in "$TESTS_DIR"/*; do
    [ -f "$f" ] || continue
    found=1
    name=$(basename "$f")
    echo "Running brute on $f"
    timeout "$TIMEOUT_LIMIT" ./build/brute < "$f" > "$OUT_DIR/$name.out"
done

if [ "$found" -eq 0 ]; then
    echo "No test files found in $TESTS_DIR"
    exit 1
fi

echo "Brute outputs written to $OUT_DIR"
```

If the brute intentionally refuses unsupported large inputs, the script should be used mainly on tests satisfying `solutions/BRUTE_LIMITS.json`.

## Run brute on small tests if available

If tests exist in `tests_dir`, run:

```bash
bash scripts/run_brute_on_tests.sh tests_dir
```

If it succeeds, report the output directory.

If it fails:

* inspect whether the test is outside brute scope
* inspect whether brute has a bug
* inspect whether test is invalid
* fix the brute if needed
* do not silently ignore failures

If the input is outside `BRUTE_LIMITS.json`, report that the brute is not intended to run on it.

## Sample comparison if sample outputs exist

If official sample input/output files exist and output is unique exact:

* run brute on sample input
* compare against sample output
* report PASS/FAIL

If output is non-unique, floating-point, construction-based, or special-judged:

* do not use exact diff as proof
* report that a checker or manual validity inspection is needed
* do not claim sample comparison proves correctness

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

### Role of `stressor-brute` in the export

`solutions/brute.cpp` is the **only** authorized source of `testdata/*.ans` in the LightCPVerifier package. No optimized attempt may be substituted for it.

Hard rules for `.ans` generation:

* `.ans` files must be generated only by `solutions/brute.cpp`.
* `.ans` file basename must match the corresponding `.in` basename (e.g. `small_0001.in` → `small_0001.ans`).
* If `solutions/brute.cpp` fails on an input — runtime error, timeout, or refuses the input as outside `BRUTE_LIMITS.json` — that case **cannot** be exported to the LightCPVerifier package, and the export stage must skip it and report the skip.

### Answer generation interface for the export stage

`scripts/run_brute_on_tests.sh` (the script this skill creates) keeps its primary role of writing brute outputs to a development directory (default `outputs/brute/`). When the LightCPVerifier export stage runs, it must be able to drive the same brute binary to produce `.ans` files directly under `lightcp/problems/<pid>/testdata/`.

Recommended dual interface (the existing script may already cover the first form; a sibling `scripts/build_lightcp_problem.sh` may be created later to cover the second):

```bash
# Development use: write *.out under outputs/brute/small/
bash scripts/run_brute_on_tests.sh tests/small outputs/brute/small

# LightCPVerifier export use: write *.ans under lightcp/problems/<pid>/testdata/
# with the small_/strong_ prefix already applied by the export stage.
bash scripts/run_brute_on_tests.sh tests/small lightcp/problems/<pid>/testdata --answer-ext .ans --input-prefix small
```

If implementing both behaviours in a single script is awkward, the export stage may rely on a dedicated future script (see "Optional export scripts" below) to drive `build/brute` directly. Either way, the rule is unchanged: only `solutions/brute.cpp` (compiled to `build/brute`) is allowed to produce `.ans`.

### Optional export scripts

Two helper scripts may be introduced in future runs of `stressor-init`:

* `scripts/build_lightcp_problem.sh` — runs the full export (compute pid, create `lightcp/problems/<pid>/`, copy `statement.txt` and `checker.cpp`, select inputs from `tests/small` and `tests/strong`, generate `.ans` via brute, validate inputs, run checker brute-vs-brute, write explicit `config.yaml`).
* `scripts/submit_lightcp_solution.sh` — reads `LIGHTCP_BASE_URL` (default `http://localhost:8081`), submits an optimized solution via `POST /submit`, polls `GET /result/:sid`, and saves the result next to the optimized solution.

This skill does **not** create those scripts. It only declares that, when they exist, the `.ans` generation step must call `solutions/brute.cpp` and nothing else.

### `BRUTE_LIMITS.json` and the export

Add (or extend) a `lightcp_export` field in `solutions/BRUTE_LIMITS.json` so the export stage can reason about whether jury answers can be produced reliably:

```json
"lightcp_export": {
  "can_generate_jury_answers": true,
  "notes": "Only cases within recommended limits should be exported."
}
```

Set `"can_generate_jury_answers": false` if the brute can only solve a strict subcase that does not cover what the LightCPVerifier package needs to test; in that case the export stage must report that LightCPVerifier readiness is NO and refuse to write `.ans` files.

Final-report addition for this skill:

```text
LightCPVerifier answer generation:
- supported: yes/no
- answer source: solutions/brute.cpp
```

Strict rules for this skill in the LightCPVerifier context:

* `stressor-brute` must **not** write `config.yaml`.
* `stressor-brute` must **not** write anything under `lightcp/problems/<pid>/` directly. The export stage (owned by `stressor-init`) is what copies brute outputs into the package as `.ans` files.
* `stressor-brute` must **not** modify or alias any `solutions/optimize_XXXX.cpp` as an answer source.

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

This skill's contribution to the sample export is to ensure that `solutions/brute.cpp` is correct on every runnable official sample, so the export stage can generate `.ans` from brute output and optionally cross-check against `statement/*.out`.

## Final Report Format

After using this skill, the final response must contain:

```text
Problem understanding:
...

Extracted input/output format:
...

Brute-design subagents:
- Designer A: SOLVED / PARTIAL / FAILED
- Designer B: SOLVED / PARTIAL / FAILED
- Designer C: SOLVED / PARTIAL / FAILED

Chosen brute algorithm:
...

Correctness argument:
...

Brute complexity:
- Time: ...
- Memory: ...

Runnable testcase limits:
- T <= ...
- n <= ...
- m <= ...
- q <= ...
- sum constraints for brute: ...
- global work budget: ...

Machine-readable limits:
- solutions/BRUTE_LIMITS.json

Output comparison:
- exact diff ok: yes/no
- checker required: yes/no
- reason: ...

Files created:
- solutions/brute.cpp
- solutions/BRUTE_SCOPE.md
- solutions/BRUTE_LIMITS.json
- scripts/run_brute_on_tests.sh

Correctness review:
- Reviewer A: CORRECT / ...
- Reviewer B: CORRECT / ...
- Reviewer C: CORRECT / ...

Small test execution:
tests/01 - OK / not run / failed / unsupported
tests/02 - OK / not run / failed / unsupported
...

Sample comparison:
- ...

Official sample checks:
- sample pairs found: ...
- runnable under BRUTE_LIMITS: ...
- passed checker: ...
- skipped: ...
- failed: ...

Notes for testcase generation:
- ...

Limitations:
- ...

Assumptions:
- ...

Not created:
- generator
- validator
- checker
- optimized solution
- standard solution
- wrong solutions
- stress testing
- large data
```

If no reliable brute could be produced, final response must contain:

```text
No reliable brute produced.

Reason:
...

Failed/partial subagent attempts:
- Designer A: ...
- Designer B: ...
- Designer C: ...

Ambiguities or blockers:
...

What information is needed:
...

Files created:
- none, or only explanatory notes if useful
```

## Strict Rules

* Prioritize correctness over performance.
* Do not write an optimized solution unless explicitly requested, or unless it is also the simplest exact reference method.
* Do not infer hidden rules from sample outputs.
* Do not hardcode sample behavior.
* Use samples only as sanity checks, not as the source of the algorithm.
* Use multiple independent brute-design subagents when possible.
* If all brute-design subagents fail, report failure instead of fabricating a solution.
* If only a partial brute is possible, clearly document its limitations.
* Never present a heuristic or uncertain solution as a correct oracle.
* Do not silently invent constraints.
* Do not use randomization.
* Do not use heuristics.
* Do not rely on hash collisions.
* Do not produce silently wrong output on unsupported input sizes.
* Must write `solutions/brute.cpp` when a reliable brute is produced.
* Must write `solutions/BRUTE_SCOPE.md` when a reliable brute is produced.
* Must write `solutions/BRUTE_LIMITS.json` when a reliable brute is produced.
* Must write `scripts/run_brute_on_tests.sh` when a reliable brute is produced.
* Must document time complexity.
* Must document memory complexity.
* Must document supported range and recommended testcase generation limits.
* Must document global work budget for multiple test cases.
* Must perform three independent correctness reviews.
* Must fix the brute if any reviewer marks it SUSPICIOUS or INCORRECT.
* Must not generate tests.
* Must not write generators.
* Must not write validator.
* Must not write checker.
* Must not write answer files unless the user explicitly asks.
* Must not create large data.
* Must not run solution stress testing unless the user explicitly asks.
