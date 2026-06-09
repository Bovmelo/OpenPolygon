---
name: polygon-mcp
description: "Use when Codex needs to manage Codeforces Polygon problems or contests through the cf-polygon-mcp MCP server: creating problems, reading problem metadata/statements/tests/files/solutions, saving statements/resources/scripts/tests/solutions, configuring validator/checker/interactor, checking readiness, building packages, downloading package/descriptor/PDF artifacts, or preparing a release. Do not use for unrelated geometry polygon tasks."
---

# Polygon MCP

## Purpose

Use the configured `cf-polygon-mcp` MCP tools as the source of truth for Codeforces Polygon state. Prefer MCP read/write/workflow tools over shell scripts, browser automation, or hand-written Polygon API calls.

Treat Polygon as a remote production system: identify the target object first, make narrow changes, inspect structured results, and do not hide failed operations.

## Preconditions

Before calling Polygon tools:

- Confirm the target `problem_id`, `contest_id`, `problem_url`, or `contest_url` from the user request or a prior read tool result.
- Ensure the `cf-polygon-mcp` MCP server is available. If no Polygon tools are visible, stop and ask the user to enable the MCP server instead of simulating results.
- Assume most read/write/workflow tools require `POLYGON_API_KEY` and `POLYGON_API_SECRET`.
- For binary downloads and descriptor/PDF downloads, also expect `POLYGON_LOGIN` and `POLYGON_PASSWORD` unless explicit `login`/`password` arguments are provided.
- Never print API secrets, passwords, or PIN values in the final answer.

## Tool Selection

Use read tools to inspect current state:

- `get_problems`, `get_problem_info`, `get_problem_statements`
- `get_problem_statement_resources`, `get_problem_files`
- `get_problem_tests`, `view_problem_test_input`, `view_problem_test_answer`, `view_problem_test_groups`
- `get_problem_validator`, `get_problem_extra_validators`, `get_problem_checker`, `get_problem_interactor`
- `get_problem_solutions`, `view_problem_solution`
- `get_problem_tags`, `get_problem_packages`, `get_contest_problems`

Use write tools only for the specific requested change:

- Create/update metadata: `create_problem`, `update_problem_info`
- Statement/content: `save_problem_statement`, `save_problem_statement_resource`, `save_problem_file`, `save_problem_script`
- Tests/groups/points: `save_problem_test`, `enable_problem_groups`, `save_problem_test_group`, `set_problem_test_group`, `enable_problem_points`
- Judging components: `set_problem_validator`, `set_problem_checker`, `set_problem_interactor`, plus validator/checker test tools
- Solutions/tags/tutorials: `save_problem_solution`, `edit_problem_solution_extra_tags`, `save_problem_tags`, `save_problem_general_description`, `save_problem_general_tutorial`
- Working copy/package: `update_problem_working_copy`, `commit_problem_changes`, `discard_problem_working_copy`, `build_problem_package`

Use workflow tools for orchestration:

- `check_problem_readiness` before release-sensitive changes.
- `build_problem_package_and_wait` when a package build needs polling and recovery guidance.
- `prepare_problem_release` only when the user asks to prepare/release/commit a problem after checks.

Use download tools carefully:

- Prefer `_info` variants when the agent only needs metadata, filename, size, hash, or content kind.
- Use raw download tools only when actual bytes are required by the user or subsequent workflow.

## Standard Problem Workflow

For a normal non-interactive problem, follow this order unless the user asks for a narrower operation:

1. Inspect or create the problem.
   - Existing problem: call `get_problem_info`.
   - New problem: call `create_problem`, then use the returned problem id.
2. Set metadata with `update_problem_info`: input/output files, time limit, memory limit, and `interactive=false`.
3. Save statement content with `save_problem_statement`; upload referenced assets with `save_problem_statement_resource`.
4. Save scripts and tests with `save_problem_script` and `save_problem_test`.
5. Configure judging files after confirming the source files exist: `set_problem_validator`, `set_problem_checker`, and `set_problem_interactor` only for interactive problems.
6. Upload at least the main accepted solution with `save_problem_solution`; add wrong/TL/RE solutions when the release criteria require coverage.
7. Run `check_problem_readiness`.
8. If readiness has blocking issues, stop and report those issues with the next concrete repair step.
9. If readiness passes and the user wants a package, call `build_problem_package_and_wait`.
10. If the user wants release preparation, call `prepare_problem_release`.

## Special Cases

Interactive problems:

- Set `interactive=true` with `update_problem_info`.
- Configure both `set_problem_interactor` and the required checker/validator setup.
- Include the statement `interaction` section in `save_problem_statement`.
- Run `check_problem_readiness` before package or release operations.

Scored problems:

- Use `enable_problem_points`.
- Include `test_points` when saving tests.
- Include statement scoring text.
- Treat missing scoring explanation as a release blocker unless the user explicitly decides otherwise.

Grouped tests:

- Use `enable_problem_groups` before group edits.
- Use `save_problem_test_group` and `set_problem_test_group`.
- Check for dependency cycles through `check_problem_readiness`.

Existing working copy:

- Prefer reading current state before overwriting.
- Use `update_problem_working_copy` when a fresh working copy is required.
- Use `discard_problem_working_copy` only when the user explicitly asks to discard remote edits or the workflow result clearly requires it.

## Result Handling

For write and workflow tools, inspect these fields:

- `status`: success or error.
- `action`: operation attempted.
- `message`: human-readable result.
- `result`: tool-specific payload.
- `error` and `error_type`: failure details.
- `stage`, `decision`, `can_retry`, `recovery_actions`: workflow guidance.

Do not treat partial success as complete. If `status=error`, or workflow `decision` indicates blocking issues, report the failed stage and the recommended recovery action. Do not call later release/package steps after a failed readiness or build unless the user explicitly asks to force the workflow and the tool supports that option.

## Safety Rules

- Make the smallest remote change that satisfies the request.
- Do not invent Polygon state; read it through MCP tools.
- Do not fabricate package ids, file names, hashes, or readiness results.
- Do not swallow tool errors or replace them with generic success text.
- Do not call release-oriented tools when the user only asked to inspect or draft.
- For file uploads from local paths, verify the path exists and matches the intended source before calling the write tool.

## Final Response

When finished, summarize:

- What Polygon object was touched.
- Which MCP tools were called.
- Whether readiness/build/release was actually verified.
- Any blocking issues, warnings, or unverified assumptions.
