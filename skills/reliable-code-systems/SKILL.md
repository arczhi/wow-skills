---
name: reliable-code-systems
description: Use when developing, fixing, reviewing, or refactoring any codebase where AI must produce reliable, observable, verifiable software with clear architecture, traceable execution paths, CI gates, and root-cause-oriented fixes rather than black-box changes.
---

# Reliable Code Systems

Use this skill to guide AI-assisted software development in any project. The goal is to build reliable code systems: architecture is understandable, execution paths are traceable, failures can be located quickly, and every change has a verification loop.

AI is allowed to move fast, but it must not develop as a black box.

## Work Contract

Before changing code:

- Read the project shape first: `README`, design docs, dependency files, scripts/Makefile/package commands, Docker/CI config, tests, logging, runtime entrypoints, and known troubleshooting docs.
- Identify the main runtime path from user/API/CLI input to storage, external calls, background work, and final output.
- Identify the canonical local gates: lint, typecheck, unit tests, integration tests, smoke tests, build, and any project-specific eval or validation commands.
- State the behavior being changed, the likely root cause, and the verification that will prove the change.
- Follow existing module boundaries and naming patterns unless they are the root cause.

During changes:

- Keep edits close to the responsible layer.
- Prefer explicit contracts over hidden conventions.
- Preserve unrelated user changes.
- Avoid speculative refactors that are not needed for the requested behavior.
- Leave short comments only where they clarify a non-obvious invariant or boundary.

Before handoff:

- Run the smallest meaningful verification first, then broader gates when the blast radius warrants it.
- Report exactly what was verified, what failed, and what remains unverified.
- Mention if old persisted data, cached state, generated artifacts, or running jobs must be regenerated before the user sees the new behavior.

## Root-Cause Fixes

When the user points to a wrong result, treat their example as evidence, not as the full problem statement.

- Find whether the error comes from data shape, responsibility boundary, prompt/contract wording, state flow, cache, scoring, ranking, sorting, fallback, concurrency, persistence, or UI display.
- Do not patch only the named keyword, sample, file, tag, timestamp, ID, or visible symptom.
- If an exception is truly required, explain why it is a business rule rather than a temporary bypass.
- Lift "what went wrong here" into a general invariant that protects the whole class of failures.
- Fix near the cause. Data-source confusion belongs in data/context modeling; sorting bugs belong in ordering semantics; stale display bugs belong in persistence/cache/refresh semantics.
- Clarify ambiguous interface fields. Prefer names like `current`, `reference`, `candidate`, `accepted`, `rejected`, `fallback`, `source`, `parent_refs`, and `is_derived` when those meanings matter.
- Check whether old state can reappear through cache, task resume, pagination, fallback ranking, local storage, or UI refresh paths.
- Verify the user's exact case plus at least one adjacent or opposite case.

## Architecture Discipline

Keep the system readable from the outside in:

- Entrypoints should be thin: parse/validate input, call services, translate errors, and return responses.
- Services orchestrate workflows and business rules.
- Repositories or data adapters own persistence queries and schema details.
- Runtime adapters own external systems: HTTP clients, model providers, queues, storage, shell tools, browsers, and platform APIs.
- Long-running work should use durable jobs, queues, or workflow runs instead of blocking request paths.
- Configuration comes from typed config and environment; secrets never enter committed files.
- Make ownership of state explicit: one source of truth for each entity or result.

For long or multi-step work, use durable state:

- Persist status such as `queued`, `running`, `succeeded`, `failed`, `canceled`, and `paused` when human review exists.
- Store `started_at`, `finished_at`, `progress`, `current_step`, `attempts`, `locked_by`, and structured error details where useful.
- Make resume/retry idempotent. Already-produced outputs should be reused or explicitly invalidated, not accidentally recomputed.
- Keep intermediate outputs small, structured, and inspectable.
- Generate diagrams from code when workflows are complex, and check diagram drift in CI if diagrams are committed.

## Practical Development Habits

Reliable code work should optimize for traceability, reversibility, and fast diagnosis.

- Before changing behavior, identify the owner of the behavior. Trace from entrypoint to data transform to persistence to display/output. Fix the layer that owns the rule, not the layer where the symptom is easiest to patch.
- Prefer one semantic formatter, parser, validator, scheduler, or scoring function per business concept. Duplicated logic is acceptable only when the concepts are truly different; otherwise consolidate or clearly name the divergence.
- Keep raw data and presentation data separate. Raw values should remain suitable for sorting, filtering, aggregation, and audits; display values should be derived at the boundary closest to presentation.
- When a user gives one example, generalize it into a rule and test the boundary cases. Examples include zero, empty, null, one item, many items, threshold values, long text, duplicate keys, concurrent runs, and stale data.
- Make state transitions explicit. Long-running tasks should have observable status, timestamps, input/output counts, failure reason, and a way to detect stale `running` records after process death.
- Treat scheduler timing as product behavior. Decide whether a job should run relative to process startup or wall-clock time. Persist or log the next scheduled run so operations can verify it without reading code.
- Do not treat process health as workflow health. A container can be healthy while the inner job is idle, stuck, retrying, or failing. Verify process args, pid files, logs, next run time, and durable task records.
- Avoid silent recovery that hides bad state. If code skips, retries, falls back, deduplicates, or soft-deletes, persist or log enough context to explain what happened later.
- Prefer idempotent writes for refresh flows. If exact database constraints cannot be changed, make replacement behavior explicit in code and verify duplicate active rows cannot survive.
- Optimize expensive work by defaulting to bounded concurrency, explicit limits, and manual backfill controls. Backfill and OCR-like workflows should not silently compete with online services.
- Treat environment files as operational contracts. Scripts should read explicit env keys, provide safe defaults, and avoid committing secrets. When env files are ignored, document the required changes separately.
- After deployment-script changes, test the actual command path, not just the application binary. Build/recreate containers, inspect service lists, pid files, command args, health status, and logs.
- When changing a rule table and code logic together, verify both sources of truth match. A seeded rule that disagrees with hardcoded calculation is a future incident.
- For data pipelines, validate at each layer boundary: ODS/raw ingest count, DWD normalized count, DWS business count, and API visible count. Differences should be explainable by named filters or rules.
- If a cleanup operation deletes or replaces data, describe when it runs, what key bounds it uses, and whether history is intentionally preserved elsewhere.

## Clear Execution Paths

Every important feature should be explainable as a chain:

```text
input
  -> validation
  -> decision/routing
  -> state change
  -> external work if any
  -> result persistence
  -> response/display
  -> observability record
```

When implementing or debugging, trace this chain before guessing. If the chain is unclear, improve names, boundaries, state records, or debug endpoints until it is clear.

For non-deterministic or AI-assisted behavior:

- Separate objective facts from semantic decisions.
- Persist the facts, inputs, selected decision, output, and enough metadata to reproduce or audit the behavior.
- Use deterministic guardrails only for contracts, safety, cost, quotas, and invalid input. Avoid brittle semantic keyword rules unless they are explicitly a business rule.
- Maintain data visibility: if the system needs previous artifacts or decisions, expose them through structured context instead of relying on hidden memory or logs.

## Verification Strategy

Choose verification by risk:

- Pure logic: unit tests.
- Data access and state transitions: repository/service integration tests.
- API/CLI contracts: route/command tests.
- UI behavior: browser or component tests that inspect the actual rendered state.
- Background work: tests for dispatch payloads, retries, idempotency, failure states, and resume behavior.
- External providers: contract tests with mocks plus smoke tests or scheduled tests when real credentials are available.
- Non-deterministic decisions: data-driven eval cases with observable expected behavior.
- Schedulers: verify wall-clock behavior, startup behavior, next-run logs, process args, and that skipped overlapping runs are observable.
- Data refreshes: verify row counts, duplicate-key invariants, stale active records, and representative API output after refresh.
- Config and script changes: verify with the same container or process command used in production, including env-file loading and service selection.
- Formatter and parser changes: test threshold and malformed inputs, not only the user-provided example.

Bug fixes need a pin test:

- The test should fail on the old bug.
- It should protect the failure mode, not only the user's sample.
- Include a neighboring or opposite case when feasible.

Coverage rules:

- Use coverage thresholds for owned deterministic code.
- Exclude provider wrappers or subprocess-heavy modules only with a written reason.
- Compensate excluded areas with smoke, integration, contract, or eval coverage.
- Do not raise coverage with hollow assertions.

## CI/CD Gates

Prefer a single local command that mirrors CI:

```bash
make ci
```

A reliable pipeline usually has:

- `validate`: lint, format check, typecheck if configured, unit/integration tests, coverage threshold, and cheap schema/eval smoke checks.
- `build`: produce deployable artifacts or images from a clean environment.
- `smoke`: start dependencies, wait for readiness, hit real endpoints/commands, print logs on failure, and always clean up.
- `behavior-eval`: run expensive or non-deterministic evals when credentials and time budget allow.
- `review`: AI or human review as a supplement, not a replacement for executable gates.

CI rules:

- Run checks in an environment close to production when practical.
- Keep test env files separate and safe.
- Isolate CI ports, worktrees, volumes, and caches to avoid cross-run contamination.
- On shell runners, create per-pipeline workspaces and clean them up `always`.
- Make failures diagnosable: preserve logs for failing services, migrations, queues, workers, and smoke commands.
- Avoid drift between comments, Makefile targets, CI config, and the commands reported to the user.

## Observability Requirements

Add observability where it helps locate failures, not as decorative logging.

Minimum for request or command flows:

- Generate or accept a correlation ID such as `trace_id` or `request_id`.
- Propagate it through service calls, jobs, workflow runs, external requests, logs, and persisted records.
- Return it in API response headers or CLI output when useful.
- Log method/command, path/action, status, latency, user/session/entity IDs, external provider/model, retry count, and structured error codes.
- Persist machine-readable error details separately from user-facing messages.
- Provide health and readiness checks separately: process alive is not the same as dependencies ready.
- Provide a way to query by trace/job/run/entity ID for debugging.

Metrics to consider:

- Rate, error, duration for APIs and commands.
- Queue depth, job duration, job status totals, worker liveness.
- External provider latency, retry count, error code totals, and cost/token counters when relevant.
- Workflow step durations and failure counts.

Prefer structured JSON logs when logs are consumed by machines. Plain logs are acceptable locally only if correlation IDs and key fields are still present.

## AI-As-Developer Rules

When AI writes code in the project:

- It must expose its assumptions through code, tests, logs, or final notes.
- It must not rely on "looks plausible" as validation.
- It must not add hidden fallback behavior that makes failures harder to see.
- It must not silently swallow errors unless the caller receives a structured degraded state.
- It must not solve architecture confusion by piling `if/else` into a caller.
- It must prefer deterministic parsers, schemas, and contracts over ad hoc string handling when the ecosystem provides them.

Good AI output leaves humans with:

- A smaller search space for future bugs.
- A clear path from symptom to cause.
- Reproducible commands.
- Tests or evals that explain the intended behavior.
- Logs and state records that make production failures diagnosable.

## Review Checklist

Before final response or PR handoff, verify:

- The change is located at the right layer.
- The execution path is still clear from input to output.
- Data semantics and ownership are explicit.
- Root cause was fixed, not just the sample symptom.
- Related fallback/cache/resume/display paths were considered.
- Verification covers the exact case and at least one broader scenario when feasible.
- Logs/state/errors include enough context to debug the next failure.
- CI/local commands are reported accurately.

