"""Provider abstracto y MockProvider determinístico para LLM Operator.

Contrato:
- AbstractProvider define la interfaz que cualquier LLM real debe implementar.
- MockProvider es una implementación determinística para tests y desarrollo offline.
- Ningún provider toca orchestration, storage ni smartpyme directamente.
- Ningún provider tiene lógica de transporte de mensajes ni integraciones externas.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ToolDecision:
    """Decisión del provider: qué tool invocar y con qué args extra (sin IDs de sesión)."""

    tool_name: str
    extra_args: dict[str, Any]
    reasoning: str


class AbstractProvider(ABC):
    """Interfaz mínima que un proveedor LLM debe implementar.

    Contrato:
    - choose_tool debe ser puro: mismo input → misma salida (o al menos determinístico
      dentro del contexto de un turno).
    - render_reply puede aplicar formato libre al resultado del tool.
    - Ambos métodos deben fallar cerrado ante excepciones internas.
    """

    @abstractmethod
    def choose_tool(
        self,
        message: str,
        state: dict[str, Any],
        tools_schema: list[dict[str, Any]],
    ) -> ToolDecision:
        """Elegir qué tool invocar dado el mensaje y el estado actual.

        Args:
            message: Texto del usuario en este turno.
            state: Snapshot del estado conversacional (salida de get_conversation_state).
            tools_schema: Lista de tools disponibles (OS_TOOLS del registry).

        Returns:
            ToolDecision con tool_name, extra_args y reasoning.
        """

    @abstractmethod
    def render_reply(
        self,
        message: str,
        tool_result: dict[str, Any],
    ) -> str:
        """Construir la respuesta final para el usuario a partir del resultado del tool.

        Args:
            message: Mensaje original del usuario.
            tool_result: Dict retornado por el tool invocado.

        Returns:
            Texto de respuesta para el usuario.
        """


# ---------------------------------------------------------------------------
# Palabras clave usadas por MockProvider
# ---------------------------------------------------------------------------

_DOCUMENT_KEYWORDS = frozenset(
    ["documento", "archivo", "excel", "planilla", "subir", "adjunto", "file"]
)
_DIAGNOSTIC_KEYWORDS = frozenset(
    [
        "diagnosticar",
        "diagnostico",
        "diagnóstico",
        "analizar",
        "análisis",
        "gano plata",
        "no gano",
        "margen",
        "rentabilidad",
        "revisar mis numeros",
        "revisar números",
    ]
)


def _contains_any(text: str, keywords: frozenset[str]) -> bool:
    lowered = text.lower()
    return any(kw in lowered for kw in keywords)


class MockProvider(AbstractProvider):
    """Provider determinístico para tests offline.

    Reglas de selección de tool:
    1. Si organization_profile aún no existe/completa:
       - sin status o vacío → start_organization_profile
       - status IN_PROGRESS → answer_organization_profile(answer=message)
    2. Si el mensaje menciona documento/archivo/excel Y hay document_path en extra_input
       → submit_document.
    3. Si el mensaje menciona diagnóstico/margen/gano plata
       → request_diagnostic.
    4. En cualquier otro caso
       → submit_text_message.

    render_reply:
    - Si el tool_result tiene 'reply_text' no vacío, lo usa directamente.
    - Si tiene 'delivery_summary', lo usa.
    - Caso contrario, construye un mensaje genérico con la fase.
    """

    def __init__(self, extra_input: dict[str, Any] | None = None) -> None:
        """
        Args:
            extra_input: Datos adicionales disponibles para el provider en este turno.
                         Puede contener 'document_path', 'document_name', etc.
                         No muta el estado del OS; es contexto de turno.
        """
        self._extra_input: dict[str, Any] = dict(extra_input or {})

    def choose_tool(
        self,
        message: str,
        state: dict[str, Any],
        tools_schema: list[dict[str, Any]],
    ) -> ToolDecision:
        available = {t["name"] for t in tools_schema}
        progressive_context = state.get("progressive_context") if isinstance(state, dict) else {}
        if not isinstance(progressive_context, dict):
            progressive_context = {}
        profile_status = str(progressive_context.get("organization_profile_status") or "").upper()
        profile_data = progressive_context.get("organization_profile")
        profile_complete = profile_status == "COMPLETED" and isinstance(profile_data, dict) and bool(profile_data)

        if not profile_complete:
            if profile_status == "IN_PROGRESS" and "answer_organization_profile" in available:
                return ToolDecision(
                    tool_name="answer_organization_profile",
                    extra_args={"answer": message},
                    reasoning="organization profile intake in progress; routing answer",
                )
            if "start_organization_profile" in available:
                return ToolDecision(
                    tool_name="start_organization_profile",
                    extra_args={},
                    reasoning="organization profile not completed; start mandatory intake",
                )

        # Regla 1: documento presente explícitamente en extra_input
        if (
            _contains_any(message, _DOCUMENT_KEYWORDS)
            and "document_path" in self._extra_input
            and "submit_document" in available
        ):
            return ToolDecision(
                tool_name="submit_document",
                extra_args={
                    "document_path": self._extra_input["document_path"],
                    "document_name": self._extra_input.get("document_name", "documento.xlsx"),
                },
                reasoning="message mentions document/file and document_path is available in extra_input",
            )

        # Regla 2: solicitud de diagnóstico
        if _contains_any(message, _DIAGNOSTIC_KEYWORDS) and "request_diagnostic" in available:
            return ToolDecision(
                tool_name="request_diagnostic",
                extra_args={},
                reasoning="message contains diagnostic/margin/profitability keywords",
            )

        # Regla 3: fallback → texto conversacional
        return ToolDecision(
            tool_name="submit_text_message",
            extra_args={},
            reasoning="no specific tool trigger detected; routing to conversational text",
        )

    def render_reply(
        self,
        message: str,
        tool_result: dict[str, Any],
    ) -> str:
        if tool_result.get("error"):
            return f"[MockProvider] Error operativo: {tool_result['error']}"

        reply_text = tool_result.get("reply_text")
        if reply_text and isinstance(reply_text, str) and reply_text.strip():
            return reply_text

        delivery_summary = tool_result.get("delivery_summary")
        if delivery_summary and isinstance(delivery_summary, str) and delivery_summary.strip():
            return delivery_summary

        phase = tool_result.get("phase") or "desconocida"
        return f"[MockProvider] Operación completada. Fase actual: {phase}."


__all__ = [
    "AbstractProvider",
    "MockProvider",
    "ToolDecision",
]
