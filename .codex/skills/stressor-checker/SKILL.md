---
name: stressor-checker
description: Build a problem-specific testlib C++ checker for stress testing by comparing brute-force oracle output and optimized solution output, including basic formatting checks, semantic validation, oracle consistency, and precise diagnostics.
---

# Stressor Checker

A skill for producing a *problem-specific* testlib C++ checker that compares a
brute-force oracle output against an optimized solution output during stress
testing / 对拍. The checker must follow the problem statement, not a fixed
template per problem genre.

## When to use

Invoke this skill when you have:

* an optimized solution to be tested,
* a trusted brute-force oracle (typically produced by `stressor-brute`),
* one or more test inputs (typically from `stressor-gen-small` and/or
  `stressor-gen-large`),

and you want a deterministic, programmatic verdict for each pair
`(input.txt, optimized.out, brute.out)`.

Do **not** invoke this skill for:

* writing a validator — use `stressor-vali`.
* writing a brute — use `stressor-brute`.
* generating tests — use `stressor-gen-small` / `stressor-gen-large`.
* interactive problems — they require an interactor, not a checker. Report
  this explicitly and stop.

## Hard requirements

1. The checker **must** be implemented in C++ and **must** `#include "testlib.h"`. No Python checker. No `diff`-based bash script masquerading as a checker.
2. The generated source filename **must** be `checker.cpp`. The default location is `checkers/checker.cpp` (preferred by `stressor-init` and `stressor-stress`); write the file at the project root only when the project clearly has no `checkers/` directory and the user accepts that.
3. The first call inside `main` **must** be `registerTestlibCmd(argc, argv);`.
4. Compile with:
   ```bash
   g++ -std=c++17 -O2 -pipe -I"$TESTLIB_INCLUDE" checkers/checker.cpp -o build/checker
   ```
   `TESTLIB_INCLUDE` is the directory containing `testlib.h` discovered by the search step below.
5. Run with the testlib convention `input output answer`:
   ```bash
   ./checker input.txt optimized.out brute.out
   ```
   In this skill:
   * `input.txt` is read via `inf`.
   * `optimized.out` (the **candidate**) is read via `ouf`.
   * `brute.out` (the **oracle / answer**) is read via `ans`.
   Never swap `ouf` and `ans`.
6. If `testlib.h` cannot be located in the project, stop with the exact message:
   ```
   Cannot find testlib.h in current project. stressor-checker requires a testlib C++ checker and cannot continue.
   ```
   Do not download testlib. Do not fabricate it. Do not silently switch to Python or `diff`.
7. The checker must be derived from a careful reading of the statement. Mechanical templating per problem genre is forbidden.
8. Do not pre-classify problems as "ordinary / SPJ / optimization / construction". Organize logic as **basic comparison items** plus **advanced comparison items** that are enabled by what the statement actually requires.
9. Exit via testlib's `quit*` helpers only:
   * `quitf(_ok, ...)` — candidate is correct and consistent with the oracle.
   * `quitf(_wa, ...)` — candidate is malformed, illegal under the statement, or disagrees with a trusted oracle.
   * `quitf(_fail, ...)` — checker bug, malformed/illegal oracle, ambiguity that prevents reliable judgement, or candidate is valid and *strictly better than* the oracle (ORACLE_CONTRADICTION).
10. The optimized output is not required to be byte-equal to the brute output. It must be (a) legal under the statement and (b) consistent with the oracle information present in the brute output.
11. Whenever a checker is produced, this skill **must also write `checkers/CHECKER_SCOPE.md`** describing checker capability for `stressor-init`. See "Checker Scope Document" below.

## Checker Scope Document

Whenever `checkers/checker.cpp` is produced, also write:

```text
checkers/CHECKER_SCOPE.md
```

This document describes checker capability so that `stressor-init` can fill `x-stressor.sources.checker` and intersect into `x-stressor.compatible_range`.

Required content:

````markdown
# Checker Scope

## Checker File

- checkers/checker.cpp

## Invocation

```bash
checker input participant_output jury_answer
```

## Output Comparison Capability

- unique exact output: yes/no
- non-unique construction: yes/no
- floating point tolerance:
- uses jury answer:
- validates participant output against input:
- requires semantic validation:

## Input / Output Range Limitations

- input size limitations:
- output size limitations:
- parsing limitations:
- unsupported cases:

## Machine-Readable Summary for stressor-init

```yaml
comparison:
  method: testlib
  invocation: checker input participant_output jury_answer
  exact_diff_used: false
  supports_non_unique_output:
  supports_floating_point:
  floating_point_tolerance:
range_limitations:
  input_size:
    max:
  output_size:
    max:
unsupported:
  - ...
```
````

If the checker has no meaningful input-size limitation beyond memory/time, state that explicitly under `range_limitations` (e.g. `input_size: { max: null }`) and explain in prose that the checker scales with whatever brute and validator allow.

`stressor-init` uses this document to:

* fill `x-stressor.sources.checker`
* compute the checker contribution to `x-stressor.compatible_range`
* decide whether stress against this checker is safe for non-unique outputs

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

## Checker Must Support Official Sample Validation

The checker must support validating brute output against official sample output files.

Required invocation:

```bash
./build/checker sample.in brute.out sample.out
```

Meaning:

* `sample.in`: input from `statement/`
* `brute.out`: participant output produced by `solutions/brute.cpp` on `sample.in`
* `sample.out`: jury answer from `statement/`

If output is non-unique or construction-based, the checker must validate participant output according to the statement rather than requiring exact text equality.

If the official sample output is one valid answer among many, the checker must accept any valid brute output that satisfies the statement.

If the checker cannot use the official sample output as a jury answer because the problem requires special semantic comparison (e.g. the official output is just one valid construction and no canonical form is enforced), document the limitation clearly in the final report and explain what the checker can and cannot infer from `statement/*.out`.

## Problem understanding first

Before any code is written, answer the following in plain English. Record the
answers in the final report. If any answer is "I don't know", stop and report
the gap — do not paper over it.

1. What mathematical object does the statement require the program to output?
2. Which parts of the output are pure formatting?
3. Which parts of the output carry semantic meaning?
4. What output differences does the statement explicitly permit (tie-breaking, multiple valid constructions, any-order, etc.)?
5. What output differences does the statement forbid (e.g. extra tokens, wrong case, missing newline)?
6. What oracle information does `brute.out` carry? Possibilities include but are not limited to:
   * a unique answer,
   * a decision (yes/no, possible/impossible),
   * an optimum value,
   * a single legal construction,
   * a reference construction not guaranteed to be the unique answer,
   * a feasibility certificate.
7. Is `brute.out` sufficient as an oracle, or does it lack information needed by the checker?
8. Does the candidate only need to agree with `brute.out`, or must it also be verified against `input.txt` independently?
9. When the candidate differs from the oracle, is that automatically wrong, or is it allowed?
10. If the candidate looks *strictly better* than the oracle, is the correct verdict `WA` or `ORACLE_CONTRADICTION`?
11. Does the input contain multiple test cases?
12. Should diagnostics be emitted per case?
13. Are there subtle format rules (case sensitivity, NaN, trailing whitespace, exact line counts, floating-point precision)?
14. What absolute / relative tolerance does the statement give for floating-point comparisons, if any?

Only after these are answered do you decide what to actually check.

Forbidden defaults (apply *only* when the statement says so):

* blind token diff,
* treating `brute.out`'s construction as the unique legal answer,
* ignoring extra tokens,
* enforcing no-trailing-whitespace,
* case-insensitive `YES`/`NO`,
* assuming the first integer is `T`,
* using `1e-6` as the floating-point tolerance.

## Required testlib C++ implementation

The checker must be a single self-contained `checker.cpp`:

```cpp
#include "testlib.h"
#include <bits/stdc++.h>
using namespace std;

int main(int argc, char* argv[]) {
    registerTestlibCmd(argc, argv);

    // 1. Read input.txt via inf — reconstruct enough problem structure to
    //    verify candidate constructions.
    //
    // 2. Read brute.out via ans — parse the oracle. Any parse error here is
    //    quitf(_fail, "oracle malformed: ...").
    //
    // 3. Read optimized.out via ouf — parse the candidate. Any parse error
    //    here is quitf(_wa, "candidate malformed: ...").
    //
    // 4. Basic checks (see "Basic comparison items").
    //
    // 5. Advanced checks chosen for *this* problem (see "Advanced
    //    comparison items").
    //
    // 6. Verdict via quitf(_ok | _wa | _fail, ...).
}
```

The candidate read from `ouf` and the oracle read from `ans` must always be
distinguished in error attribution:

* candidate parse error / illegal candidate / disagreement with trusted oracle → `quitf(_wa, ...)`.
* oracle parse error / illegal oracle / oracle internally inconsistent → `quitf(_fail, ...)`.

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

### Role of `stressor-checker` in the export

* `stressor-checker` keeps writing the canonical checker to `checkers/checker.cpp`. That path is unchanged.
* During the LightCPVerifier export stage (owned by `stressor-init`), `checkers/checker.cpp` is **copied verbatim** to `lightcp/problems/<pid>/checker.cpp`. This is a copy, not a relocation — both files must exist and be identical after the export.
* For LightCPVerifier compatibility, the checker **must** keep the standard testlib argument order:

```bash
checker input participant_output jury_answer
```

  In this workflow the export stage relies on that exact order. Skills outside this one must not rewrite checker calls into any other order. Inside this skill, the `registerTestlibCmd(argc, argv)` first-call rule, the `inf` / `ouf` / `ans` binding rule, and the "never swap `ouf` and `ans`" rule from "Hard requirements" together guarantee this order.

### LightCPVerifier brute-vs-brute sanity check

During `stressor-init`'s export stage (and during any export refresh), the checker is exercised with the brute output as both the participant output and the jury answer, for every exported case:

```bash
checker input brute.out brute.out
```

This must return `_ok` for every exported case before the export stage marks the package ready. If `checker input brute.out brute.out` returns `_wa` or `_fail` on any case:

* the case must not be exported;
* the export stage must report which case failed brute-vs-brute and why;
* this is treated as a checker bug or as an unreliable brute output, not as an optimized-solution failure.

If the checker is not compatible with the LightCPVerifier / testlib `input participant_output jury_answer` argument order — for example, the checker reads arguments in a non-standard order, or it was built against a non-testlib convention — the package must **not** be marked ready. The export stage must report:

```text
Ready for LightCPVerifier: NO
Reason: checker.cpp does not follow the testlib argument order.
```

Strict rules for this skill in the LightCPVerifier context:

* `stressor-checker` must keep writing `checkers/checker.cpp` as the canonical output (the long-standing default).
* `stressor-checker` must **not** write `config.yaml`.
* `stressor-checker` must **not** generate `.ans` files.
* `stressor-checker` does not create `lightcp/problems/<pid>/` directly. The export stage (owned by `stressor-init`) performs the copy `checkers/checker.cpp` → `lightcp/problems/<pid>/checker.cpp`.
* `stressor-checker` must **not** swap `ouf` (participant) and `ans` (jury), which would break the LightCPVerifier invocation contract.

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

`stressor-checker`'s role in this context is to be invocable with the standard `input participant_output jury_answer` order so that the export stage can both (a) brute-vs-brute sanity-check exported cases and (b) cross-check brute output against `statement/*.out` when desired.

## testlib.h requirement

Before producing or compiling `checker.cpp`, locate `testlib.h` in the
current project. Try the following paths in order:

```
./testlib.h
./checkers/testlib.h
./validators/testlib.h
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

If none of those match, fall back to:

```bash
find . -maxdepth 4 -name testlib.h
find .. -maxdepth 3 -name testlib.h
find ../.. -maxdepth 3 -name testlib.h
```

When `testlib.h` is found:

* record its directory in a `TESTLIB_INCLUDE` shell variable (default it to that path inside any helper script you emit),
* compile with `-I"$TESTLIB_INCLUDE"`,
* never hard-code `-I.` unless `testlib.h` truly lives at the project root.

When `testlib.h` is missing:

* stop,
* emit the exact error message in Hard requirement #6,
* do not create `checker.cpp`,
* do not create helper scripts,
* do not switch to Python, do not download anything.

If the user supplies `testlib.h` after the error, restart from this section
and continue normally.

## Official checker handling

If the project already ships an official checker, prefer to read and reuse it
before writing anything new. Candidate filenames include:

```
checker.cpp
check.cpp
checker_*.cpp
spj.cpp
special_judge.cpp
polygon/checker.cpp
checkers/*.cpp
```

Rules:

1. If the official checker is testlib-based and matches the
   `input output answer` convention, prefer to reuse it (wrap it if needed)
   rather than write a parallel one.
2. If the official checker requires a different `answer-file` format than
   `brute.out`, document the incompatibility and either:
   * adapt your `brute.out` format (only with user permission), or
   * write a new testlib checker that accepts `brute.out` directly.
3. If the official checker is not testlib-based (e.g. a Python script, a
   Polygon-specific harness), study its logic but the final artifact in this
   skill must still be a testlib C++ checker.
4. If the official checker only enforces format and does not validate the
   semantic contract between candidate and oracle, extend it with explicit
   oracle-consistency checks.
5. If the official checker contradicts the statement, flag the contradiction
   and do not silently inherit its behaviour. Choose the statement.

## Basic comparison items

Every checker considers these items. Each is enabled or disabled by what the
statement actually says — they are *not* a fixed sequence.

### 1. File and stream readiness

* `inf` opens `input.txt`.
* `ouf` opens `optimized.out`.
* `ans` opens `brute.out`.
* `registerTestlibCmd(argc, argv)` is the first call in `main`.

### 2. EOF and output completeness

* If the candidate ends before the expected token count, `quitf(_wa, "candidate ended early at ...")`.
* If the oracle ends early, `quitf(_fail, "oracle ended early at ...")`.
* If the statement requires "exactly K integers and nothing else", enforce
  `ouf.seekEof()` (or the equivalent stream API) at the end.

### 3. Extra tokens

* Decide from the statement whether trailing tokens are allowed.
* If forbidden, an extra candidate token → `_wa`. Treat an extra *oracle*
  token as a failure of the brute, i.e. `_fail`, only if it affects oracle
  reliability; otherwise tolerate it.

### 4. Whitespace handling

* Defaults: token-level comparison ignores horizontal whitespace, newlines,
  and tabs between tokens.
* Do not enforce "no trailing whitespace" unless the statement explicitly
  requires it.
* If the statement specifies a strict line/column structure (exact line
  count, exact `k` numbers per line, no trailing space, etc.), use
  `readSpace`, `readEoln`, `readEof` and record in the final report that
  strict formatting is enforced.

### 5. Case sensitivity

* Default case-sensitive.
* `YES`/`Yes`/`yes` are equivalent only if the statement explicitly says so;
  otherwise pick the variant the statement uses and reject the others.

### 6. Integers

* Choose `readInt` / `readLong` / `readToken` + manual `int128` parsing based on the declared range, not on a hopeful guess.
* Reject out-of-range candidate integers with `_wa`. Out-of-range oracle integers → `_fail`.

### 7. Floating point

* Use the tolerance the statement gives. Implement both the absolute and the
  relative form when the statement requires "absolute or relative error of `1e-X`".
* Do not pick a loose tolerance "to be safe". A wrong tolerance turns the
  checker into an accomplice.
* If the statement is silent on tolerance but floating-point comparison is
  required, halt and report the ambiguity rather than guess. If forced to
  pick (e.g. the user grants permission), document the chosen `eps`.
* `NaN` and `inf` are illegal candidate output unless the statement explicitly
  allows them.

### 8. Strings

* Default: token-level comparison.
* If the statement asks for a full line including spaces (e.g. "a sentence",
  "a path printed verbatim"), use line-level reads, not `readToken`.
* When the alphabet is restricted by the statement, validate it explicitly.

### 9. Error attribution

* Always attribute the failure to the correct side:
  * candidate's fault → `_wa`;
  * oracle's fault → `_fail`;
  * checker cannot decide → `_fail` with an explicit reason.

## Advanced comparison items

Enable any of these when the statement makes them load-bearing. None of these
is unconditional.

### 1. Feasibility of the candidate construction

Verify that the candidate object satisfies the input constraints:

* node indices in range,
* edges exist in the input graph,
* array length matches the prescribed size,
* set size matches the prescribed cardinality,
* capacity / weight / count limits respected,
* each element used the prescribed number of times,
* the prescribed operation sequence is actually executable,
* the final state satisfies the goal.

### 2. Certificate checks for structured outputs

When the candidate outputs a structured object, parse and verify it:

* **path**: start, end, contiguity, every edge exists, no forbidden repeats, length matches the declared length.
* **cycle**: closure, edge existence, vertex/edge uniqueness if required.
* **tree**: `n-1` edges, connectivity, acyclicity, vertex range.
* **matching**: each edge exists, each vertex matched at most once.
* **permutation**: in range, no repeats, no omissions.
* **topological order**: every directed edge `u→v` has `pos[u] < pos[v]`.
* **coloring**: colors in range, adjacency constraints respected.
* **partition**: each element in exactly one group, group sizes / inter-group constraints respected.
* **operation sequence**: simulate and verify intermediate and final states.
* **expression**: parse and evaluate, then compare semantic value to the statement's requirement.

### 3. Recompute declared values from the certificate

When the candidate prints both a claimed value and a witness, recompute the
value from the witness:

* compare `claimed_value` with `recomputed_value`; if they disagree, `_wa`.
* compare `recomputed_value` with the brute oracle value:
  * equal → consistent.
  * candidate value strictly *worse* than oracle (in the optimization
    direction stated by the problem) → `_wa`.
  * candidate value strictly *better* than oracle → `_fail`
    `ORACLE_CONTRADICTION` (the brute is no longer a trustworthy oracle).
* If the candidate's construction is illegal, do not compare values at all;
  report `_wa` for the illegal construction.

### 4. Decision-result consistency

When outputs include a feasibility verdict (`YES`/`NO`, `POSSIBLE`/`IMPOSSIBLE`,
`-1`, `No solution`, ...):

* brute says NO, candidate provides a construction:
  * if construction is illegal → `_wa`.
  * if construction is legal → `_fail` `ORACLE_CONTRADICTION`.
* brute says YES, candidate says NO:
  * `_wa`.
* both say YES:
  * verify the candidate construction.
* both say NO:
  * accept, provided the brute oracle is trustworthy. If the oracle is itself
    suspect, escalate to `_fail`.

### 5. Multi-answer legality

If the statement permits multiple valid outputs, never compare the two
constructions byte by byte. Instead:

* parse the oracle to extract just the oracle-relevant information (value,
  yes/no, optimum, etc.).
* validate the candidate construction independently against `input.txt`.
* compare candidate's oracle-relevant information with the oracle's.

Forbidden shortcuts:

* `diff` of the two constructions,
* treating the oracle's construction as canonical,
* only checking the first line and ignoring the certificate,
* checking format but not semantics.

### 6. Oracle contradiction

`_fail` (not `_wa`) is the correct verdict when any of the following holds:

* `brute.out` is itself malformed,
* `brute.out` carries an illegal construction,
* candidate is legal and strictly better than the oracle,
* candidate is a legal construction but oracle says the answer is impossible.

Use a recognisable diagnostic prefix such as `ORACLE_CONTRADICTION:` or
`INVALID_ORACLE:` so the surrounding pipeline can route these cases to the
brute author rather than the optimized-solution author.

## Input parsing and multiple cases

The checker must parse `input.txt` and reconstruct enough of the problem
structure to verify candidate constructions. When multiple test cases are
present:

1. Check each case independently.
2. Report 1-based case indices in every diagnostic.
3. When possible, also report local positions:
   * token index,
   * vertex id,
   * edge id,
   * path position,
   * permutation position,
   * operation index,
   * constraint index that fails.
4. If the input format does not let you slice it into cases (e.g. one big
   global structure that is implicitly indexed), state explicitly in the
   diagnostic that
   `"Per-case extraction is unavailable; the whole input is the failing case."`

Do not blindly assume the first integer is `T`. Decide from the statement,
the validator, and the brute's input parser combined.

## Brute oracle requirements

Before writing the checker, evaluate whether `brute.out` carries enough
information.

* If the brute prints only a construction but the problem permits multiple
  legal constructions, the brute construction must not be treated as canonical.
* Prefer `brute.out` formats that expose oracle information explicitly. Examples:
  ```
  YES
  value 123
  <certificate ...>
  ```
  ```
  NO
  ```
  ```
  OPT 123
  ```
  ```
  POSSIBLE
  minimum_cost 456
  <construction ...>
  ```
* If the current `brute.out` is insufficient for a reliable checker, do not
  silently work around it. Report what extra information the brute needs to
  emit. Unless the user explicitly authorises it, do not modify the brute.

## testlib checker structure

Suggested file layout. Adapt names to the problem.

```cpp
#include "testlib.h"
#include <bits/stdc++.h>
using namespace std;

// 1. Problem-specific data structures.
struct InputData      { /* fields reconstructed from input.txt */ };
struct OracleAnswer   { /* fields extracted from brute.out   */ };
struct CandidateAnswer{ /* fields extracted from optimized.out */ };

// 2. Parsing functions. Attribute errors to the correct side.
InputData     readInput(int tc);
OracleAnswer  readOracle(int tc);     // parse errors → quitf(_fail, ...)
CandidateAnswer readCandidate(int tc);// parse errors → quitf(_wa,  ...)

// 3. Verification helpers.
void validateCandidateConstruction(const InputData& in, const CandidateAnswer& c, int tc);
long long recomputeValue(const InputData& in, const CandidateAnswer& c);
void ensureNoExtraOutput();           // optional; only if the statement forbids extras.

// 4. main.
int main(int argc, char* argv[]) {
    registerTestlibCmd(argc, argv);

    int T = readTifAny();             // 1 if no multitest.
    for (int tc = 1; tc <= T; tc++) {
        auto in   = readInput(tc);
        auto orc  = readOracle(tc);
        auto cand = readCandidate(tc);

        validateCandidateConstruction(in, cand, tc);
        compareWithOracle(in, cand, orc, tc);    // _wa or _fail on mismatch.
    }
    ensureNoExtraOutput();
    quitf(_ok, "ok");
}
```

Diagnostics in every `quitf` should pinpoint where the failure occurred:

```cpp
quitf(_wa,
    "Case %d: candidate path uses nonexistent edge (%d, %d) at position %d",
    tc, u, v, pos);

quitf(_fail,
    "Case %d: ORACLE_CONTRADICTION: candidate value %lld is strictly better than oracle value %lld",
    tc, candValue, oracleValue);
```

## testlib parsing rules

* Use the testlib stream APIs. Do not invent custom parsers when `readInt`,
  `readLong`, `readToken`, `readDouble`, `readSpace`, `readEoln`, `readEof`,
  `readWord`, `readLine` already cover the format.
* Range-check at parse time using the two-argument overloads (`readInt(lo, hi, "name")`).
  This both parses and validates in one call.
* Do **not** execute or `eval` candidate output. Treat it as data.
* Do not trust the candidate's claimed value when a certificate is also
  present — recompute.
* Do not swallow oracle parse errors. Surface them as `_fail`.
* Do not let invalid candidate output cause the checker to crash. Every parse
  step on `ouf` must funnel into `quitf(_wa, ...)`, never abort/UB.
* Do not modify any input or output file.
* No network access. No randomness. The checker must be deterministic.

## Diagnostics requirement

Every `quitf(_wa, ...)` and every `quitf(_fail, ...)` must answer:

* **What** failed (the specific assertion).
* **Where** it failed (case index, token index, vertex / edge / position).
* **Why** it failed (the candidate value vs the expected predicate or oracle).

Generic messages like `"WA"`, `"wrong answer"`, `"failed"` are not acceptable.
Bad: `quitf(_wa, "wrong");`. Good: `quitf(_wa, "Case 3: edge (4, 5) reported at position 7 does not exist in the input graph");`.

When a structured certificate is involved, the diagnostic must identify the
exact element of the certificate that violated a rule, not just say "invalid
construction".

## Failure artifact protocol

When the checker is used inside a stress-testing loop and a verdict is
non-`_ok`, the surrounding harness should preserve the artifacts that
produced the verdict. The skill encourages, but does not author, this
behaviour in the checker itself. Document in the final report:

* the exact paths the harness should preserve (`input.txt`, `optimized.out`,
  `brute.out`),
* the suggested directory naming (e.g. `failures/<verdict>/<id>/`),
* the verdict string the checker emits, so the harness can route.

The checker itself must not write files. It only emits a verdict and
diagnostic.

## Self-tests

Before declaring the checker done, run at least these self-tests. The skill
must perform them and report results:

1. **Compile**:
   ```bash
   g++ -std=c++17 -O2 -pipe -I"$TESTLIB_INCLUDE" checker.cpp -o checker
   ```
   Must succeed with no warnings related to the checker logic.

2. **Round-trip OK**: use a known-good `(input.txt, optimized.out, brute.out)`
   triple (e.g. the official sample with both files equal to the sample
   output). The checker must return `_ok`.

3. **Candidate corruption rejection**: mutate `optimized.out` (truncate,
   inject an extra token, wrong case if applicable, out-of-range value).
   The checker must return `_wa` with a diagnostic that names the mutation
   site.

4. **Oracle corruption attribution**: mutate `brute.out` (truncate, replace a
   value, break the format). The checker must return `_fail`, not `_wa`.

5. **Tie-breaking**: if the problem permits multiple valid outputs, produce
   a candidate that is a *different* valid answer from the brute. The checker
   must return `_ok`, not `_wa`.

6. **Oracle contradiction**: if applicable, construct a candidate that is
   legal and strictly better than the brute oracle. The checker must return
   `_fail` with `ORACLE_CONTRADICTION` in the message.

Document in the final report which self-tests applied to this problem and
which ones were inapplicable, with reasons.

## Multi-review checklist

Apply this checklist after writing `checker.cpp`. Treat each line as a "must
have considered" item; record the decision in the final report.

* [ ] Statement re-read end-to-end before writing the checker.
* [ ] Output object identified (what is being checked).
* [ ] Oracle information from `brute.out` documented.
* [ ] Candidate parse errors map to `_wa`, oracle parse errors to `_fail`.
* [ ] Extra-token policy decided from the statement.
* [ ] Whitespace policy decided from the statement.
* [ ] Case-sensitivity decided from the statement.
* [ ] Integer ranges enforced at parse time.
* [ ] Floating-point tolerance taken from the statement (or ambiguity reported).
* [ ] Multi-case loop with 1-based indices.
* [ ] Per-case position information in diagnostics.
* [ ] Construction certificates independently re-verified against `input.txt`.
* [ ] Declared values recomputed from certificates and compared with the oracle.
* [ ] Multi-answer legality handled — no byte-diff of constructions when not required.
* [ ] Oracle-contradiction path emits `_fail` with a recognisable prefix.
* [ ] `quitf` messages include what / where / why.
* [ ] No randomness, no I/O side effects, no network calls.
* [ ] `testlib.h` actually located in the project (no fabrication).
* [ ] Self-tests run and recorded.

## Integration with stressor pipeline

The checker is the verdict step inside the stress-testing loop. Its sibling
skills are responsible for:

* `stressor-vali` — `validators/val.cpp` and `validators/VALIDATION_SCOPE.md`
  describe which inputs are well-formed. Reuse range information from
  `VALIDATION_SCOPE.md` when reading `input.txt` in the checker.
* `stressor-brute` — `solutions/brute.cpp`, `solutions/BRUTE_SCOPE.md`, and
  `solutions/BRUTE_LIMITS.json` describe the oracle's reliability range. The
  checker should refuse to run on inputs outside `BRUTE_LIMITS.json`, or at
  least surface that the verdict is unreliable in that regime.
* `stressor-gen-small` / `stressor-gen-large` — provide the `input.txt`
  stream. Generated tests outside `BRUTE_LIMITS.json` cannot be checked
  by this pipeline.

Recommended on-disk layout when the checker is added to a problem directory:

```
<problem>/
├── input.txt              # or tests/small/* / tests/large/*
├── solutions/
│   ├── brute.cpp
│   ├── BRUTE_SCOPE.md
│   └── BRUTE_LIMITS.json
├── validators/
│   ├── val.cpp
│   └── VALIDATION_SCOPE.md
├── checker.cpp            # produced by this skill
└── scripts/
    └── run_checker.sh     # optional helper (this skill may emit it)
```

A minimal helper script (optional, only emit if useful):

```bash
#!/usr/bin/env bash
set -euo pipefail
TESTLIB_INCLUDE="${TESTLIB_INCLUDE:-../third_party/testlib}"
mkdir -p build
g++ -std=c++17 -O2 -pipe -I"$TESTLIB_INCLUDE" checker.cpp -o build/checker
./build/checker "$1" "$2" "$3"   # input.txt optimized.out brute.out
```

## Safety and robustness

* The checker must be deterministic: same inputs → same verdict, every time.
* No file system writes from the checker. No network calls. No `std::system`.
* No execution of candidate output as code (no `eval`-style processing).
* No `unordered_set` / `unordered_map` keyed on candidate-controlled values
  unless a guarded hasher is used; prefer ordered containers when feasible.
* Use `long long` (or `__int128`) when the input or recomputed value can
  exceed `int` range.
* Avoid floating-point inside the certificate verification when the input is
  integer; use exact integer arithmetic.
* The checker must not modify `input.txt`, `optimized.out`, or `brute.out`.
* The checker must not depend on environment variables, the wall clock, or
  the locale.

## When reliable checking is impossible

If after careful reading you cannot write a reliable checker, do not bluff.
Report:

1. what information is missing,
2. why the brute output is insufficient as an oracle,
3. which statement rules are unclear,
4. what you need from the user (statement clarification, richer brute output,
   the official checker, a sample of accepted outputs),
5. whether the problem is in fact interactive and therefore needs an
   interactor, not a checker.

Hard rule: do not substitute a Python script or a `diff` invocation for a
real checker. If the checker cannot be written in testlib C++, the verdict
of this skill is "cannot continue", with a clear explanation.

Stop conditions that must trigger an explicit failure report (not a silent
fallback):

* `testlib.h` not found in the project.
* Problem is interactive.
* Statement is ambiguous on a load-bearing detail (e.g. tolerance, tie-breaking, exact format).
* `brute.out` format lacks information the checker needs.

## Final response format

Every invocation of this skill must produce a final report with these
sections, in order. Be explicit; "see above" is not acceptable.

1. **Inspected files** — the statement, validator (if any), brute scope (if
   any), brute output sample (if any), optimized output sample (if any),
   any pre-existing official checker.

2. **testlib.h status** — found / not found, path used, include flag used.
   If not found, the report ends here with the literal error message.

3. **Official checker status** — found / not found; if found, reused or
   replaced, and why.

4. **Output semantics** — what the statement requires the program to print,
   what the candidate must validate against `input.txt`, what oracle
   information `brute.out` carries.

5. **Basic comparison items used** — each item with a one-line decision
   (e.g. "case sensitive: yes; extra tokens forbidden; integer range [1, 10^9]
   enforced at parse; NaN/inf rejected").

6. **Advanced comparison items used** — each item with a one-line decision
   (e.g. "candidate certificate validated against input graph; declared value
   recomputed from certificate; oracle-contradiction path enabled").

7. **Generated files** — `checker.cpp`; helper script if any; any notes.

8. **Compile command** —
   ```bash
   g++ -std=c++17 -O2 -pipe -I"$TESTLIB_INCLUDE" checker.cpp -o checker
   ```

9. **Run command** —
   ```bash
   ./checker input.txt optimized.out brute.out
   ```
   or via the helper script if emitted.

10. **Complexity** — checker time and memory complexity, expressed in the
    input variables of the problem.

11. **Diagnostics** — the granularity the checker reports at (case index,
    token, vertex, edge, position).

12. **Self-test results** — which of the self-tests in the "Self-tests"
    section were run, and the verdict for each. Mark inapplicable ones with
    reasons.

13. **Limitations** — assumptions, ambiguity flagged to the user, gaps in
    `brute.out`, checks that are intentionally not implemented, ranges
    outside which the checker should not be trusted.

14. **Official sample checker support** — one block of the form:

    ```text
    Official sample checker support:
    - can check brute output against sample output: yes/no
    - reason:
    ```

    State explicitly whether `./build/checker sample.in brute.out sample.out` can be used as a meaningful check against `statement/*.out`. If the answer is "no", explain why (non-unique output, missing oracle info, etc.).

If the skill ended in a failure / "cannot continue" state, the report has
the same sections up to the point of failure, and a final block:

```
Status: cannot continue
Reason: <one paragraph>
Required from user: <bullet list>
```

## Strict rules (recap)

* testlib C++ checker only. No Python. No bash diff. No fabricated testlib.
* `checker.cpp` is the filename.
* `registerTestlibCmd(argc, argv)` is the first call in `main`.
* Arguments are `input output answer`. `optimized.out` is `ouf`,
  `brute.out` is `ans`. Never swap.
* `testlib.h` must be located inside the project. If not found, stop with
  the exact error message in Hard requirement #6.
* Do not classify problems into fixed genres. Use basic + advanced items.
* Candidate parse errors → `_wa`. Oracle parse errors → `_fail`. Candidate
  legal and strictly better than oracle → `_fail` with
  `ORACLE_CONTRADICTION`.
* Diagnostics must report what / where / why.
* Recompute claimed values from certificates; never trust them blindly.
* When multiple valid answers exist, do not byte-diff constructions.
* Run the self-tests and record results.
* If reliable checking is impossible, report and stop. Do not bluff.
