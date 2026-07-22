#!/usr/bin/env python3
"""Maintain a small, auditable Good Partner state ledger."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
PROJECT_STATUSES = {
    "inbox",
    "shaping",
    "ready",
    "active",
    "waiting-agent",
    "waiting-user",
    "blocked",
    "review",
    "done",
    "parked",
    "canceled",
}
DECISION_PRIORITIES = {"p0", "p1", "p2"}
DECISION_STATUSES = {"pending", "resolved", "withdrawn"}
EVIDENCE_KINDS = {"explicit", "correction", "observation"}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def initial_state() -> dict[str, Any]:
    timestamp = now_iso()
    return {
        "schema_version": SCHEMA_VERSION,
        "preferences": [],
        "projects": [],
        "decisions": [],
        "created_at": timestamp,
        "updated_at": timestamp,
    }


def load_state(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"state file does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc
    if not isinstance(data, dict):
        raise ValueError("state root must be a JSON object")
    return data


def atomic_write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = now_iso()
    payload = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def validate_state(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")

    for collection in ("preferences", "projects", "decisions"):
        if not isinstance(data.get(collection), list):
            errors.append(f"{collection} must be a list")

    projects = data.get("projects", [])
    if isinstance(projects, list):
        seen: set[str] = set()
        for index, project in enumerate(projects):
            prefix = f"projects[{index}]"
            if not isinstance(project, dict):
                errors.append(f"{prefix} must be an object")
                continue
            project_id = project.get("id")
            if not isinstance(project_id, str) or not project_id.strip():
                errors.append(f"{prefix}.id must be a nonempty string")
            elif project_id in seen:
                errors.append(f"duplicate project id: {project_id}")
            else:
                seen.add(project_id)
            if not isinstance(project.get("title"), str) or not project.get("title", "").strip():
                errors.append(f"{prefix}.title must be a nonempty string")
            status = project.get("status")
            if status not in PROJECT_STATUSES:
                errors.append(f"{prefix}.status must be one of {sorted(PROJECT_STATUSES)}")
            if status == "blocked" and not str(project.get("blocked_by", "")).strip():
                errors.append(f"{prefix}.blocked_by is required when status is blocked")

    preferences = data.get("preferences", [])
    if isinstance(preferences, list):
        seen_preferences: set[tuple[str, str]] = set()
        for index, preference in enumerate(preferences):
            prefix = f"preferences[{index}]"
            if not isinstance(preference, dict):
                errors.append(f"{prefix} must be an object")
                continue
            key = preference.get("key")
            scope = preference.get("scope")
            if not isinstance(key, str) or not key.strip():
                errors.append(f"{prefix}.key must be a nonempty string")
            if not isinstance(scope, str) or not scope.strip():
                errors.append(f"{prefix}.scope must be a nonempty string")
            if isinstance(key, str) and isinstance(scope, str):
                identity = (key, scope)
                if identity in seen_preferences:
                    errors.append(f"duplicate preference key/scope: {key}/{scope}")
                seen_preferences.add(identity)
            if preference.get("status") not in {"provisional", "active", "conflicted"}:
                errors.append(f"{prefix}.status is invalid")
            if not isinstance(preference.get("evidence"), list):
                errors.append(f"{prefix}.evidence must be a list")

    decisions = data.get("decisions", [])
    if isinstance(decisions, list):
        seen_decisions: set[str] = set()
        for index, decision in enumerate(decisions):
            prefix = f"decisions[{index}]"
            if not isinstance(decision, dict):
                errors.append(f"{prefix} must be an object")
                continue
            decision_id = decision.get("id")
            if not isinstance(decision_id, str) or not decision_id.strip():
                errors.append(f"{prefix}.id must be a nonempty string")
            elif decision_id in seen_decisions:
                errors.append(f"duplicate decision id: {decision_id}")
            else:
                seen_decisions.add(decision_id)
            if decision.get("priority") not in DECISION_PRIORITIES:
                errors.append(f"{prefix}.priority must be one of {sorted(DECISION_PRIORITIES)}")
            status = decision.get("status")
            if status not in DECISION_STATUSES:
                errors.append(f"{prefix}.status must be one of {sorted(DECISION_STATUSES)}")
            if status == "pending":
                if not str(decision.get("question", "")).strip():
                    errors.append(f"{prefix}.question is required while pending")
                if not str(decision.get("recommendation", "")).strip():
                    errors.append(f"{prefix}.recommendation is required while pending")
            if status == "resolved" and not str(decision.get("resolution", "")).strip():
                errors.append(f"{prefix}.resolution is required when resolved")
    return errors


def require_valid(data: dict[str, Any]) -> None:
    errors = validate_state(data)
    if errors:
        raise ValueError("state validation failed:\n- " + "\n- ".join(errors))


def find_by_id(items: list[dict[str, Any]], item_id: str) -> dict[str, Any] | None:
    return next((item for item in items if item.get("id") == item_id), None)


def set_if_present(target: dict[str, Any], args: argparse.Namespace, names: list[str]) -> None:
    for name in names:
        value = getattr(args, name)
        if value is not None:
            target[name] = value


def command_init(args: argparse.Namespace) -> None:
    path = Path(args.file)
    if path.exists():
        raise ValueError(f"refusing to overwrite existing state file: {path}")
    state = initial_state()
    require_valid(state)
    atomic_write(path, state)
    print(f"initialized {path}")


def command_validate(args: argparse.Namespace) -> None:
    path = Path(args.file)
    state = load_state(path)
    errors = validate_state(state)
    if errors:
        print("INVALID", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)
    print(f"valid: {path}")


def command_project(args: argparse.Namespace) -> None:
    path = Path(args.file)
    state = load_state(path)
    projects: list[dict[str, Any]] = state.setdefault("projects", [])
    project = find_by_id(projects, args.id)
    timestamp = now_iso()
    if project is None:
        if not args.title:
            raise ValueError("--title is required for a new project")
        project = {
            "id": args.id,
            "title": args.title,
            "status": args.status or "inbox",
            "priority": args.priority or "normal",
            "created_at": timestamp,
        }
        projects.append(project)
    set_if_present(
        project,
        args,
        [
            "title",
            "status",
            "priority",
            "goal",
            "definition_of_done",
            "next_action",
            "resume_note",
            "blocked_by",
            "waiting_for",
            "deadline",
            "owner",
            "workspace",
            "last_verified_at",
        ],
    )
    project["updated_at"] = timestamp
    require_valid(state)
    atomic_write(path, state)
    print(f"updated project {args.id}")


def command_preference(args: argparse.Namespace) -> None:
    path = Path(args.file)
    state = load_state(path)
    preferences: list[dict[str, Any]] = state.setdefault("preferences", [])
    preference = next(
        (
            item
            for item in preferences
            if item.get("key") == args.key and item.get("scope") == args.scope
        ),
        None,
    )
    timestamp = now_iso()
    evidence = {
        "kind": args.evidence,
        "source": args.source,
        "value": args.value,
        "observed_at": timestamp,
    }
    if preference is None:
        preference = {
            "key": args.key,
            "scope": args.scope,
            "value": args.value,
            "status": "active" if args.evidence in {"explicit", "correction"} else "provisional",
            "confidence": 1.0 if args.evidence in {"explicit", "correction"} else 0.4,
            "evidence": [evidence],
            "conflicts": [],
            "created_at": timestamp,
        }
        preferences.append(preference)
    elif args.evidence in {"explicit", "correction"}:
        if preference.get("value") != args.value:
            preference.setdefault("conflicts", []).append(
                {
                    "value": preference.get("value"),
                    "reason": "superseded by explicit user evidence",
                    "recorded_at": timestamp,
                }
            )
        preference["value"] = args.value
        preference["status"] = "active"
        preference["confidence"] = 1.0
        preference.setdefault("evidence", []).append(evidence)
    elif preference.get("value") == args.value:
        preference.setdefault("evidence", []).append(evidence)
        independent_sources = {
            item.get("source")
            for item in preference["evidence"]
            if item.get("kind") == "observation" and item.get("value") == args.value
        }
        if len(independent_sources) >= 2:
            preference["status"] = "active"
            preference["confidence"] = max(float(preference.get("confidence", 0)), 0.7)
    else:
        preference.setdefault("conflicts", []).append(evidence)
        explicit_support = any(
            item.get("kind") in {"explicit", "correction"}
            and item.get("value") == preference.get("value")
            for item in preference.get("evidence", [])
        )
        if explicit_support:
            preference["status"] = "active"
            preference["confidence"] = 1.0
        else:
            preference["status"] = "conflicted"
            preference["confidence"] = min(float(preference.get("confidence", 0.4)), 0.4)
    preference["updated_at"] = timestamp
    require_valid(state)
    atomic_write(path, state)
    print(f"updated preference {args.key}/{args.scope}: {preference['status']}")


def command_decision(args: argparse.Namespace) -> None:
    path = Path(args.file)
    state = load_state(path)
    decisions: list[dict[str, Any]] = state.setdefault("decisions", [])
    decision = find_by_id(decisions, args.id)
    timestamp = now_iso()
    if decision is None:
        if not args.question or not args.recommendation:
            raise ValueError("--question and --recommendation are required for a new decision")
        decision = {
            "id": args.id,
            "status": args.status or "pending",
            "priority": args.priority or "p1",
            "question": args.question,
            "recommendation": args.recommendation,
            "created_at": timestamp,
        }
        decisions.append(decision)
    set_if_present(
        decision,
        args,
        [
            "project_id",
            "status",
            "priority",
            "question",
            "recommendation",
            "options",
            "impact",
            "safe_continuation",
            "deadline",
            "resolution",
        ],
    )
    decision["updated_at"] = timestamp
    require_valid(state)
    atomic_write(path, state)
    print(f"updated decision {args.id}: {decision['status']}")


def command_summary(args: argparse.Namespace) -> None:
    state = load_state(Path(args.file))
    require_valid(state)
    projects = state["projects"]
    decisions = state["decisions"]
    preferences = state["preferences"]

    foreground = [item for item in projects if item.get("status") == "active"]
    waiting = [
        item
        for item in projects
        if item.get("status") in {"waiting-agent", "waiting-user", "blocked", "review"}
    ]
    pending = [item for item in decisions if item.get("status") == "pending"]
    active_preferences = [item for item in preferences if item.get("status") == "active"]

    print("NOW")
    if not foreground:
        print("- none")
    for project in foreground:
        print(f"- [{project['id']}] {project['title']}: {project.get('next_action', 'next action unset')}")

    print("WAITING / AT RISK")
    if not waiting:
        print("- none")
    for project in waiting:
        reason = project.get("blocked_by") or project.get("waiting_for") or project.get("next_action") or "reason unset"
        print(f"- [{project['status']}] {project['title']}: {reason}")

    print("PENDING DECISIONS")
    if not pending:
        print("- none")
    for decision in sorted(pending, key=lambda item: item.get("priority", "p2")):
        print(f"- [{decision['priority'].upper()}] {decision['question']} -> {decision['recommendation']}")

    print(f"ACTIVE PREFERENCES: {len(active_preferences)}")
    print(f"UPDATED: {state.get('updated_at', 'unknown')}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="create a new state file")
    init_parser.add_argument("--file", required=True)
    init_parser.set_defaults(handler=command_init)

    validate_parser = subparsers.add_parser("validate", help="validate a state file")
    validate_parser.add_argument("--file", required=True)
    validate_parser.set_defaults(handler=command_validate)

    summary_parser = subparsers.add_parser("summary", help="print an attention-oriented summary")
    summary_parser.add_argument("--file", required=True)
    summary_parser.set_defaults(handler=command_summary)

    project_parser = subparsers.add_parser("project", help="create or update a project")
    project_parser.add_argument("--file", required=True)
    project_parser.add_argument("--id", required=True)
    project_parser.add_argument("--title")
    project_parser.add_argument("--status", choices=sorted(PROJECT_STATUSES))
    project_parser.add_argument("--priority")
    project_parser.add_argument("--goal")
    project_parser.add_argument("--definition-of-done", dest="definition_of_done")
    project_parser.add_argument("--next-action", dest="next_action")
    project_parser.add_argument("--resume-note", dest="resume_note")
    project_parser.add_argument("--blocked-by", dest="blocked_by")
    project_parser.add_argument("--waiting-for", dest="waiting_for")
    project_parser.add_argument("--deadline")
    project_parser.add_argument("--owner")
    project_parser.add_argument("--workspace")
    project_parser.add_argument("--last-verified-at", dest="last_verified_at")
    project_parser.set_defaults(handler=command_project)

    preference_parser = subparsers.add_parser("preference", help="record preference evidence")
    preference_parser.add_argument("--file", required=True)
    preference_parser.add_argument("--key", required=True)
    preference_parser.add_argument("--value", required=True)
    preference_parser.add_argument("--scope", required=True)
    preference_parser.add_argument("--evidence", choices=sorted(EVIDENCE_KINDS), required=True)
    preference_parser.add_argument("--source", required=True)
    preference_parser.set_defaults(handler=command_preference)

    decision_parser = subparsers.add_parser("decision", help="create or update an approval decision")
    decision_parser.add_argument("--file", required=True)
    decision_parser.add_argument("--id", required=True)
    decision_parser.add_argument("--project-id", dest="project_id")
    decision_parser.add_argument("--status", choices=sorted(DECISION_STATUSES))
    decision_parser.add_argument("--priority", choices=sorted(DECISION_PRIORITIES))
    decision_parser.add_argument("--question")
    decision_parser.add_argument("--recommendation")
    decision_parser.add_argument("--options")
    decision_parser.add_argument("--impact")
    decision_parser.add_argument("--safe-continuation", dest="safe_continuation")
    decision_parser.add_argument("--deadline")
    decision_parser.add_argument("--resolution")
    decision_parser.set_defaults(handler=command_decision)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.handler(args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
