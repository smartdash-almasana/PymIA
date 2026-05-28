from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from pymia.llm_operator.providers import AbstractProvider, ToolDecision


@dataclass(frozen=True)
class OpenRouterProvider(AbstractProvider):
    api_key: str
    model: str | None = None
    base_url: str = "https://openrouter.ai/api/v1"
    timeout: float = 30.0

    def __post_init__(self) -> None:
        resolved_model = self.model or os.environ.get("PYMIA_OPERATOR_MODEL") or "openrouter/owl-alpha"
        object.__setattr__(self, "model", resolved_model)

    def _fallback_decision(self, message: str, reason: str) -> ToolDecision:
        return ToolDecision(
            tool_name="submit_text_message",
            extra_args={"text": message},
            reasoning=reason,
        )

    def _safe_json_loads(self, raw: bytes) -> dict[str, Any]:
        loaded = json.loads(raw.decode("utf-8"))
        if not isinstance(loaded, dict):
            return {}
        return loaded

    def _extract_tool_decision(self, payload: dict[str, Any], message: str) -> ToolDecision:
        choices = payload.get("choices")
        if not isinstance(choices, list) or not choices:
            return self._fallback_decision(message, "no choices in provider response")

        first = choices[0] if isinstance(choices[0], dict) else {}
        msg = first.get("message") if isinstance(first, dict) else {}
        if not isinstance(msg, dict):
            return self._fallback_decision(message, "invalid message object in provider response")

        tool_calls = msg.get("tool_calls")
        if not isinstance(tool_calls, list) or not tool_calls:
            return self._fallback_decision(message, "no tool_calls in provider response")

        call = tool_calls[0] if isinstance(tool_calls[0], dict) else {}
        fn = call.get("function") if isinstance(call, dict) else {}
        if not isinstance(fn, dict):
            return self._fallback_decision(message, "invalid tool function object")

        tool_name = fn.get("name")
        raw_args = fn.get("arguments", "{}")
        if not isinstance(tool_name, str) or not tool_name.strip():
            return self._fallback_decision(message, "missing tool name in tool_call")

        try:
            parsed_args = json.loads(raw_args) if isinstance(raw_args, str) else {}
        except json.JSONDecodeError:
            parsed_args = {}
        if not isinstance(parsed_args, dict):
            parsed_args = {}

        return ToolDecision(
            tool_name=tool_name.strip(),
            extra_args=parsed_args,
            reasoning="tool_call selected by openrouter response",
        )

    def choose_tool(
        self,
        message: str,
        state: dict[str, Any],
        tools_schema: list[dict[str, Any]],
    ) -> ToolDecision:
        del state
        try:
            endpoint = f"{self.base_url.rstrip('/')}/chat/completions"
            body = {
                "model": self.model,
                "messages": [{"role": "user", "content": message}],
                "tools": tools_schema,
                "tool_choice": "auto",
            }
            request = urllib.request.Request(
                endpoint,
                data=json.dumps(body).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            with urllib.request.urlopen(request, timeout=self.timeout) as resp:
                payload = self._safe_json_loads(resp.read())
            decision = self._extract_tool_decision(payload, message)
            return decision
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError):
            return self._fallback_decision(message, "provider error; fallback to submit_text_message")
        except Exception:
            return self._fallback_decision(message, "unexpected provider error; fallback to submit_text_message")

    def render_reply(
        self,
        message: str,
        tool_result: dict[str, Any],
    ) -> str:
        del message
        if not isinstance(tool_result, dict):
            return "[OpenRouterProvider] Resultado no válido."
        if tool_result.get("error"):
            return f"[OpenRouterProvider] Error operativo: {tool_result['error']}"
        reply_text = tool_result.get("reply_text")
        if isinstance(reply_text, str) and reply_text.strip():
            return reply_text
        delivery_summary = tool_result.get("delivery_summary")
        if isinstance(delivery_summary, str) and delivery_summary.strip():
            return delivery_summary
        phase = tool_result.get("phase") or "desconocida"
        return f"[OpenRouterProvider] Operación completada. Fase actual: {phase}."

