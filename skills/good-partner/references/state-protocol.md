# Durable State Protocol

Use durable state only when the cost of reconstructing context exceeds the cost of maintaining the ledger. A one-off task does not need it. Multi-project, multi-session, delegated, monitored, or approval-heavy work usually does.

## Storage Selection

Choose the first available option:

1. The user's existing canonical project/task system.
2. A persistent memory store whose scope the user has already authorized.
3. A workspace-local `.good-partner/state.json` proposed to the user.
4. A cross-project file or system only after explicit authorization of location, readers, and scope.

Do not put runtime state in the skill installation folder. Do not create a second source of truth when the project already has one. If an external system is canonical, keep only IDs and resume pointers locally.

## State Model

`scripts/partner_state.py` maintains one human-inspectable JSON document:

```json
{
  "schema_version": 1,
  "preferences": [],
  "projects": [],
  "decisions": [],
  "updated_at": "ISO-8601 timestamp"
}
```

### Preferences

Each preference contains:

- `key`: stable category such as `communication.detail` or `approval.external_send`;
- `value`: concise value;
- `scope`: `global` or a project/workspace identifier;
- `status`: `provisional`, `active`, or `conflicted`;
- `confidence`: evidence strength, not a psychological probability;
- `evidence`: explicit statements, corrections, or independent observations with timestamps and sources;
- `conflicts`: observations that disagree with the active value.

Activate explicit statements and corrections immediately. Activate inferred preferences only after two independent sources support the same value. Never treat silence as a source.

### Projects

Use one record per outcome, not one per chat. Required operational fields are:

- `id`, `title`, `status`, and `priority`;
- `goal` and `definition_of_done` for nontrivial work;
- `next_action` containing exactly one executable next step;
- `last_verified_at` and `resume_note` for reliable re-entry;
- `blocked_by`, `waiting_for`, `deadline`, `owner`, and `workspace` when relevant.

Use statuses from the SKILL.md. `blocked` requires a nonempty `blocked_by`. A done project should have verification evidence in its resume note, project artifacts, or canonical tracker.

### Decisions

A pending decision contains:

- one exact `question`;
- one `recommendation`;
- `priority`: `p0`, `p1`, or `p2`;
- optional project ID, options, deadline, impact, and safe continuation;
- `status`: `pending`, `resolved`, or `withdrawn`;
- a resolution when resolved.

Do not create a decision record for routine information. Bundle decisions that share the same approval boundary.

## Update Rules

- Read before writing and preserve unknown fields for forward compatibility.
- Update the ledger after meaningful state transitions, not after every tool call.
- Keep raw execution logs elsewhere; the ledger stores only resumption and decision state.
- Use stable IDs. Renaming a title must not create a duplicate project.
- Never record secrets, tokens, private message content, medical inferences, or protected traits.
- If the user corrects state, treat that correction as canonical and preserve only enough prior evidence to explain the change.
- Validate after manual edits and before portfolio reporting.

## Re-entry and Digest

On re-entry:

1. Validate the ledger.
2. Read active, waiting, blocked, and review projects.
3. Read pending P0/P1 decisions.
4. Compare ledger claims with the canonical project evidence.
5. Repair stale state or label it unverified.
6. Present only the current foreground item and decisions requiring attention.

For a digest, group by:

- `Now`: one foreground project and next checkpoint.
- `Waiting on you`: bundled pending P0/P1 decisions.
- `At risk`: deadline, dependency, or verification risks that changed.
- `Recently closed`: newly verified outcomes.

Do not list unchanged parked or completed work unless asked.

## Script Safety

The script writes atomically to the exact `--file` path and refuses to overwrite an existing file during `init`. It has no network access and uses only the Python standard library.

Before the first write, show or state the selected path and confirm that its scope matches the user's intent. A workspace-local ledger is not automatically a global user profile.
