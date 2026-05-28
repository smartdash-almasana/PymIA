"""LLMOperator — orquestador offline de tools del OS vía provider abstracto.

Contrato:
- LLMOperator recibe un provider y un registry module.
- handle_turn ejecuta: get_conversation_state → choose_tool → invoke tool → render_reply.
- No toca graph, state_storage ni smartpyme directamente.
- No tiene adaptadores de I/O ni lógica de transporte de mensajes.
- Toda interacción con el OS pasa exclusivamente por os_tool_registry.
- OperatorResult es JSON-serializable.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any

from pymia.llm_operator.providers import AbstractProvider


def _sanitize_for_json(obj: Any) -> Any:
    """Recursivamente convierte tipos no-JSON-serializables a primitivos."""
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_sanitize_for_json(i) for i in obj]
    return obj


@dataclass
class OperatorResult:
    """Resultado de un turno del operador. Siempre JSON-serializable."""

    reply_text: str
    selected_tool: str | None
    tool_args: dict[str, Any]
    tool_result: dict[str, Any]
    operator_trace: list[str]
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "reply_text": self.reply_text,
            "selected_tool": self.selected_tool,
            "tool_args": self.tool_args,
            "tool_result": self.tool_result,
            "operator_trace": self.operator_trace,
            "error": self.error,
        }

    def is_json_serializable(self) -> bool:
        try:
            json.dumps(self.to_dict())
            return True
        except (TypeError, ValueError):
            return False


def _get_tool_fn(registry: ModuleType, tool_name: str) -> Any:
    """Resuelve la función del tool por nombre desde el registry module."""
    fn = getattr(registry, tool_name, None)
    if fn is None or not callable(fn):
        raise AttributeError(f"Tool '{tool_name}' not found or not callable in registry")
    return fn


def _build_tool_kwargs(
    *,
    tool_name: str,
    tenant_id: str,
    chat_id: str,
    conversation_id: str,
    extra_args: dict[str, Any],
    base_dir: Path | None,
) -> dict[str, Any]:
    """Construye kwargs para el tool combinando IDs de sesión con extra_args del provider."""
    kwargs: dict[str, Any] = {
        "tenant_id": tenant_id,
        "chat_id": chat_id,
    }

    # get_conversation_state no requiere conversation_id
    if tool_name != "get_conversation_state":
        kwargs["conversation_id"] = conversation_id

    # submit_text_message requiere text; si no está en extra_args, el tool lo rechazará
    # (fail-closed del registry — no inventamos texto aquí)

    kwargs.update(extra_args)

    if base_dir is not None:
        kwargs["base_dir"] = base_dir

    return kwargs


class LLMOperator:
    """Operador que media entre un provider LLM y el OS Tool Registry.

    No contiene lógica de negocio. Su única responsabilidad es:
    1. Consultar el estado actual.
    2. Dejar que el provider elija el tool.
    3. Invocar el tool del registry.
    4. Dejar que el provider renderice la respuesta.
    5. Retornar OperatorResult.
    """

    def __init__(self, provider: AbstractProvider, registry: ModuleType) -> None:
        """
        Args:
            provider: Implementación de AbstractProvider (Mock o real).
            registry: Módulo Python con las funciones de tool y OS_TOOLS schema.
        """
        if not isinstance(provider, AbstractProvider):
            raise TypeError("provider must be an instance of AbstractProvider")
        if not isinstance(registry, ModuleType):
            raise TypeError("registry must be a Python module")

        self._provider = provider
        self._registry = registry

    def _get_tools_schema(self) -> list[dict[str, Any]]:
        os_tools = getattr(self._registry, "OS_TOOLS", None)
        if os_tools is None or not isinstance(os_tools, list):
            return []
        return list(os_tools)

    def handle_turn(
        self,
        *,
        tenant_id: str,
        chat_id: str,
        conversation_id: str,
        message: str,
        base_dir: Path | str | None = None,
    ) -> OperatorResult:
        """Ejecuta un turno completo del operador.

        Flujo:
        1. get_conversation_state → snapshot del OS.
        2. provider.choose_tool(message, state, schema) → ToolDecision.
        3. Construir kwargs y llamar tool del registry.
        4. provider.render_reply(message, tool_result) → reply_text.
        5. Retornar OperatorResult.

        Falla cerrado: cualquier excepción interna queda en OperatorResult.error.
        """
        target_base = Path(base_dir) if base_dir is not None else None
        trace: list[str] = []

        # --- Paso 1: obtener estado actual ---
        try:
            state_fn = _get_tool_fn(self._registry, "get_conversation_state")
            state_kwargs: dict[str, Any] = {"tenant_id": tenant_id, "chat_id": chat_id}
            if target_base is not None:
                state_kwargs["base_dir"] = target_base
            current_state = state_fn(**state_kwargs)
            trace.append(f"get_conversation_state: phase={current_state.get('phase')}")
        except Exception as exc:
            current_state = {}
            trace.append(f"get_conversation_state failed (non-fatal): {exc}")

        # --- Paso 2: provider elige tool ---
        tools_schema = self._get_tools_schema()
        try:
            decision = self._provider.choose_tool(message, current_state, tools_schema)
            trace.append(
                f"choose_tool: selected={decision.tool_name!r} reasoning={decision.reasoning!r}"
            )
        except Exception as exc:
            return OperatorResult(
                reply_text="[Operator] No se pudo determinar la acción a ejecutar.",
                selected_tool=None,
                tool_args={},
                tool_result={},
                operator_trace=trace,
                error=f"choose_tool failed: {exc}",
            )

        # --- Paso 3: invocar tool ---
        try:
            tool_fn = _get_tool_fn(self._registry, decision.tool_name)
        except AttributeError as exc:
            return OperatorResult(
                reply_text="[Operator] Tool no disponible.",
                selected_tool=decision.tool_name,
                tool_args={},
                tool_result={},
                operator_trace=trace,
                error=str(exc),
            )

        # Construir args: IDs de sesión + extra_args del provider
        # Para submit_text_message: si el provider no incluyó text, lo usamos del message
        extra_args = dict(decision.extra_args)
        if decision.tool_name == "submit_text_message" and "text" not in extra_args:
            extra_args["text"] = message

        tool_kwargs = _build_tool_kwargs(
            tool_name=decision.tool_name,
            tenant_id=tenant_id,
            chat_id=chat_id,
            conversation_id=conversation_id,
            extra_args=extra_args,
            base_dir=target_base,
        )
        # Copia sanitizada para almacenar en OperatorResult (JSON-safe)
        safe_tool_args = _sanitize_for_json(dict(tool_kwargs))
        trace.append(f"invoking tool: {decision.tool_name} with keys={sorted(tool_kwargs.keys())}")

        try:
            tool_result = tool_fn(**tool_kwargs)
            if not isinstance(tool_result, dict):
                tool_result = {"raw": str(tool_result)}
            tool_result = _sanitize_for_json(tool_result)
            trace.append(
                f"tool_result: phase={tool_result.get('phase')} error={tool_result.get('error')}"
            )
        except Exception as exc:
            return OperatorResult(
                reply_text="[Operator] Error al ejecutar el tool del OS.",
                selected_tool=decision.tool_name,
                tool_args=safe_tool_args,
                tool_result={},
                operator_trace=trace,
                error=f"tool execution failed: {exc}",
            )

        # --- Paso 4: provider renderiza respuesta ---
        try:
            reply_text = self._provider.render_reply(message, tool_result)
            trace.append(f"render_reply: reply_length={len(reply_text)}")
        except Exception as exc:
            reply_text = "[Operator] Resultado procesado sin respuesta formateada."
            trace.append(f"render_reply failed (non-fatal): {exc}")

        return OperatorResult(
            reply_text=reply_text,
            selected_tool=decision.tool_name,
            tool_args=safe_tool_args,
            tool_result=tool_result,
            operator_trace=trace,
            error=None,
        )


__all__ = ["LLMOperator", "OperatorResult"]
