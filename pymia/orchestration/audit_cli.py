"""CLI mínimo de auditoría para estados persistidos de orquestación."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pymia.orchestration.state_storage import (
    export_conversation_jsonl,
    find_conversations_by_tenant,
    get_conversation_history,
    replay_conversation,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pymia.orchestration.audit_cli")
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path(".runtime/orchestration_storage"),
        help="Base directory del storage JSONL",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list")
    list_parser.add_argument("tenant_id")

    show_parser = subparsers.add_parser("show")
    show_parser.add_argument("tenant_id")
    show_parser.add_argument("chat_id")

    history_parser = subparsers.add_parser("history")
    history_parser.add_argument("tenant_id")
    history_parser.add_argument("chat_id")

    export_parser = subparsers.add_parser("export")
    export_parser.add_argument("tenant_id")
    export_parser.add_argument("chat_id")
    export_parser.add_argument("output_path", type=Path)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "list":
            conversations = find_conversations_by_tenant(args.tenant_id, args.base_dir)
            if not conversations:
                print("No conversations found.")
                return 0
            for row in conversations:
                print(
                    f"{row['conversation_id']}\t{row['chat_id']}\t{row['last_phase']}\t"
                    f"{row['last_updated']}\t{row['evidence_count']}"
                )
            return 0

        if args.command == "show":
            state = replay_conversation(args.tenant_id, args.chat_id, args.base_dir)
            if state is None:
                print("Conversation not found.")
                return 1
            print(f"tenant_id: {state.tenant_id}")
            print(f"chat_id: {state.chat_id}")
            print(f"conversation_id: {state.conversation_id}")
            print(f"phase: {state.phase}")
            print(f"intake_id: {state.intake_id}")
            print(f"evidence_count: {len(state.evidence_ids)}")
            print(f"sufficiency_status: {state.sufficiency_status}")
            print(f"readiness_status: {state.readiness_status}")
            print(f"runtime_candidate_status: {state.runtime_candidate_status}")
            print(f"execution_status: {state.execution_status}")
            print(f"gate_verdict: {state.gate_verdict}")
            print(f"delivery_status: {state.delivery_status}")
            print(f"findings_count: {state.findings_count}")
            print(f"output_refs: {state.output_refs}")
            print(f"updated_at: {state.updated_at.isoformat()}")
            return 0

        if args.command == "history":
            history = get_conversation_history(args.tenant_id, args.chat_id, args.base_dir)
            if not history:
                print("No history found.")
                return 0
            for row in history:
                print(
                    f"{row.get('updated_at')}\t{row.get('phase')}\t{row.get('intake_id')}\t"
                    f"{row.get('execution_status')}\t{row.get('delivery_status')}"
                )
            return 0

        if args.command == "export":
            exported = export_conversation_jsonl(
                args.tenant_id, args.chat_id, args.base_dir, args.output_path
            )
            print(f"exported_lines: {exported}")
            return 0
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    print("Unknown command.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
