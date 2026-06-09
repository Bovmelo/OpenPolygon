---
name: stressor-try
description: Generate a versioned attempted optimized ICPC/CCPC solution through an OpenAI-compatible API in statement-only hard-isolation mode. The skill only resolves the statement, chooses a version number, and invokes scripts/api_try.py; the API receives only statement content and writes solutions/optimize_XXXX.cpp plus solutions/notes_XXXX.md.
---

# Stressor Try

## Purpose

This skill creates a versioned attempted optimized solution.

This version uses API hard isolation.

The local Codex agent must not solve the problem directly.

The local skill only:

1. Resolves the official statement.
2. Chooses the next version number.
3. Computes output paths under `solutions/`.
4. Invokes `.codex/skills/stressor-try/scripts/api_try.py`.

The API model receives only statement content.

The API model must not receive tests, brute code, checker code, validator code, generators, reports, previous attempts, or counterexamples.

## Output Files

Every successful run creates a fresh versioned pair:

```text
solutions/optimize_0001.cpp
solutions/notes_0001.md
solutions/optimize_0002.cpp
solutions/notes_0002.md
...
```

Rules:

* Use four-digit zero-padded version numbers.
* Scan existing filenames before choosing a version.
* If either `optimize_XXXX.cpp` or `notes_XXXX.md` exists, version `XXXX` is occupied.
* Do not overwrite existing versions.
* Only inspect filenames for version selection.
* Do not open previous `optimize_XXXX.cpp` contents.
* Do not open previous `notes_XXXX.md` contents.

These files are compatible with the stressor workflow and LightCPVerifier/go-judge submission flow:

* `solutions/optimize_XXXX.cpp` is the attempted solution/submission code.
* `solutions/notes_XXXX.md` is the public solution explanation and metadata.
* Do not place optimized attempts inside `lightcp/problems/<pid>/`.
* The LightCPVerifier problem package is separate.
* Optimized attempts are submitted from `solutions/optimize_XXXX.cpp`.

## Statement Resolution

The first positional argument is `path_to_problem_statement_or_problem_dir`.

It may be:

1. A direct statement file:

```text
QOJ464/statement/statement.md
```

2. A problem root directory:

```text
QOJ464
```

3. A statement directory:

```text
QOJ464/statement
```

If the argument is a file, use it as the primary statement file.

If the argument is a directory, resolve the statement file using this priority:

```text
<dir>/statement/statement.md
<dir>/statement/problem.md
<dir>/statement/README.md
<dir>/statement/statement.txt
<dir>/statement.md
<dir>/problem.md
<dir>/README.md
<dir>/statement.pdf
<dir>/statement/statement.pdf
```

If the argument itself is a `statement/` directory, resolve using:

```text
<dir>/statement.md
<dir>/problem.md
<dir>/README.md
<dir>/statement.txt
<dir>/statement.pdf
```

Preferred layout:

```text
{problemname}/statement/statement.md
```

If no statement file is found, stop and report searched paths.

Do not guess the statement from tests, solutions, generators, validators, checkers, outputs, or reports.

## Statement Bundle

The allowed input context for `stressor-try` is the statement bundle only.

Usually:

```text
{problemname}/statement/
```

Allowed statement bundle files:

```text
statement.md
problem.md
README.md
statement.txt
samples.md
examples.md
notes.md
*.in
*.out
*.input
*.output
```

The skill may pass the statement directory or primary statement file to `api_try.py`.

`api_try.py` must only read files inside the statement bundle.

Forbidden reads:

```text
tests/
tests/small/
tests/strong/
tests/large/
solutions/brute.cpp
solutions/BRUTE_SCOPE.md
solutions/BRUTE_LIMITS.json
previous optimize_XXXX.cpp contents
previous notes_XXXX.md contents
checkers/
validators/
generators/
outputs/
reports/
lightcp/problems/
counterexamples
```

Official sample files under the statement directory, such as:

```text
QOJ464/statement/ex_prefix1.in
QOJ464/statement/ex_prefix1.out
```

are considered statement content and may be included in the API prompt.

Do not include generated tests or strong counterexamples.

## API Hard Isolation

This skill must use:

```text
.codex/skills/stressor-try/scripts/api_try.py
```

The helper script performs the actual API call.

Required environment variables:

```text
API_BASE_URL
API_AUTH_TOKEN
STRESSOR_TRY_MODEL
```

Meaning:

* `API_BASE_URL`: OpenAI-compatible API base URL
* `API_AUTH_TOKEN`: authentication token
* `STRESSOR_TRY_MODEL`: model name to use

The helper script must check that `STRESSOR_TRY_MODEL` appears in `client.models.list()`.

If model is missing, stop and report available model ids.

If API call fails, do not locally solve as fallback.

If helper fails:

* report failure
* do not create fake solution files
* do not use local Codex reasoning to fill code

## API Environment Initialization

Before invoking `api_try.py`, this skill must load:

```text
.codex/skills/stressor-try/scripts/api_init.sh
```

This file is expected to export:

```text
API_BASE_URL
API_AUTH_TOKEN
STRESSOR_TRY_MODEL
```

The script must be sourced in the same shell that launches `api_try.py`.

Correct:

```bash
source .codex/skills/stressor-try/scripts/api_init.sh
python3 .codex/skills/stressor-try/scripts/api_try.py ...
```

Incorrect:

```bash
.codex/skills/stressor-try/scripts/api_init.sh
python3 .codex/skills/stressor-try/scripts/api_try.py ...
```

Reason:

Running `api_init.sh` directly starts a child shell. Environment variables exported there may not be visible to the later Python process. Sourcing it applies exports to the current shell.

If `api_init.sh` is missing, stop and report:

```text
Missing .codex/skills/stressor-try/scripts/api_init.sh
```

Do not fallback to local solving.

Do not ask API credentials interactively.

Do not print `API_AUTH_TOKEN`.

## Invocation Protocol

When invoked, this skill should run a command of the following shape. `api_init.sh` must be sourced in the same shell that runs `api_try.py`; the two cannot be split across separate shell invocations.

```bash
bash -lc '
set -euo pipefail
source .codex/skills/stressor-try/scripts/api_init.sh
python3 .codex/skills/stressor-try/scripts/api_try.py \
  --statement "<resolved_statement_or_statement_dir>" \
  --output-cpp "solutions/optimize_XXXX.cpp" \
  --output-notes "solutions/notes_XXXX.md" \
  --version "XXXX"
'
```

Concrete example with literal paths:

```bash
bash -lc '
set -euo pipefail
source .codex/skills/stressor-try/scripts/api_init.sh
python3 .codex/skills/stressor-try/scripts/api_try.py \
  --statement QOJ464/statement/statement.md \
  --output-cpp solutions/optimize_0001.cpp \
  --output-notes solutions/notes_0001.md \
  --version 0001
'
```

Rules:

* `api_init.sh` must be loaded before `api_try.py`, in the same shell.
* The skill must compute `XXXX` first.
* `api_try.py` still validates the required environment variables.
* `api_try.py` still calls `client.models.list()`.
* `api_try.py` still checks that `STRESSOR_TRY_MODEL` exists in the returned model list.
* If model validation fails, report the error.
* If API call fails, do not locally generate code.
* The helper script must not overwrite existing output files.

## No Local Solve

The local Codex agent must not produce the solution code itself.

It may only orchestrate the API call.

No local fallback is allowed.

## No Testing

This skill must not run:

* tests
* validator
* brute
* checker
* generators
* stressor-stress
* sample comparison through local files

Testing belongs to `stressor-stress`.

## Final Report

After successful execution, final response should contain:

```text
stressor-try API isolation:
- enabled: yes
- statement argument: ...
- resolved statement: ...
- statement directory: ...
- model: $STRESSOR_TRY_MODEL
- version: XXXX
- cpp: solutions/optimize_XXXX.cpp
- notes: solutions/notes_XXXX.md
- forbidden project files read: none
- local solve fallback used: no
- next command: $stressor-stress path_to_problem_statement_or_problem_dir --optimized latest --brute solutions/brute.cpp --rounds 20
```

If failure occurs:

```text
stressor-try failed:
- reason: ...
- files created: none
- local fallback used: no
```

## Strict Rules

* Must use API hard isolation.
* Must invoke `.codex/skills/stressor-try/scripts/api_try.py`.
* Must source `.codex/skills/stressor-try/scripts/api_init.sh` before invoking `api_try.py`.
* Must not run `api_init.sh` as a standalone child process when expecting its exports to affect `api_try.py`.
* Must stop if `api_init.sh` is missing.
* Must not solve locally if API fails.
* Must not fallback to local solving if environment initialization fails.
* Must not read tests.
* Must not read brute code.
* Must not read checker code.
* Must not read validator code.
* Must not read generators.
* Must not read reports.
* Must not read previous optimized solution contents.
* May inspect previous optimized filenames only for version-number selection.
* Must not run stress testing.
* Must not run brute/checker comparison.
* Must not overwrite existing solution versions.
* Must write attempted solution to `solutions/optimize_XXXX.cpp`.
* Must write public notes to `solutions/notes_XXXX.md`.
* Must not put optimized attempts into `lightcp/problems/<pid>/`.
* Must not expose `API_AUTH_TOKEN` in logs.
* Must not print `API_AUTH_TOKEN`.
* Must not print full API request if it contains token.
* Must report model-not-found errors clearly.
* `api_try.py` remains responsible for validating `API_BASE_URL`, `API_AUTH_TOKEN`, and `STRESSOR_TRY_MODEL`.
