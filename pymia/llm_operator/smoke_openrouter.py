from __future__ import annotations

import argparse
import os
from pathlib import Path

import pymia.orchestration.os_tool_registry as registry_module
from pymia.llm_operator.operator import LLMOperator
from pymia.llm_operator.providers_openrouter import OpenRouterProvider


def _load_env_local(path: Path) -> dict[str, str]:
    loaded: dict[str, str] = {}
    if not path.exists():
        return loaded
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            loaded[key] = value
    return loaded


def _resolve_openrouter_key(env_file: Path) -> str | None:
    env_values = _load_env_local(env_file)
    key = os.environ.get("OPENROUTER_API_KEY") or env_values.get("OPENROUTER_API_KEY")
    if key and "OPENROUTER_API_KEY" not in os.environ:
        os.environ["OPENROUTER_API_KEY"] = key
    return key


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pymia.llm_operator.smoke_openrouter")
    parser.add_argument("--message", required=True)
    parser.add_argument("--tenant", default="smoke_openrouter")
    parser.add_argument("--chat", default="smoke_chat")
    parser.add_argument("--conversation", default="smoke_conversation")
    parser.add_argument("--base-dir", default=".runtime/os_storage")
    parser.add_argument("--env-file", default=".env.local")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    key = _resolve_openrouter_key(Path(args.env_file))
    if not key:
        print("selected_tool: None")
        print("reply_text: ")
        print("error: OPENROUTER_API_KEY missing (.env.local or env)")
        print(f"model: {os.environ.get('PYMIA_OPERATOR_MODEL') or 'openrouter/owl-alpha'}")
        return 2

    provider = OpenRouterProvider(api_key=key)
    operator = LLMOperator(provider=provider, registry=registry_module)
    result = operator.handle_turn(
        tenant_id=args.tenant,
        chat_id=args.chat,
        conversation_id=args.conversation,
        message=args.message,
        base_dir=args.base_dir,
    )

    print(f"selected_tool: {result.selected_tool}")
    print(f"reply_text: {result.reply_text}")
    print(f"error: {result.error}")
    print(f"model: {provider.model}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
