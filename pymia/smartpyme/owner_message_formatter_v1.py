from __future__ import annotations

from pymia.smartpyme.owner_response_renderer_v1 import OwnerResponseV1


def format_owner_message_v1(owner_response: OwnerResponseV1) -> str:
    """Format an OwnerResponseV1 as plain text for manual delivery.

    This formatter is presentation-only. It does not inspect files, infer business
    meaning, authorize runtime, call LLMs, execute tools, or add new business logic.
    """
    sections = [
        "Respuesta inicial de Servicio 1",
        "",
        owner_response["owner_message"],
        "",
        "1. Qué recibimos",
        owner_response["what_we_received"],
        "",
        "2. Qué podemos hacer ahora",
        owner_response["what_can_be_done_now"],
        "",
        "3. Qué falta",
        _format_list_or_none(owner_response["what_is_missing"]),
        "",
        "4. Qué no podemos afirmar todavía",
        _format_list_or_none(owner_response["what_cannot_be_claimed"]),
        "",
        "5. Próximo paso",
        owner_response["next_owner_action"],
    ]
    return "\n".join(sections)


def _format_list_or_none(values: list[str]) -> str:
    if not values:
        return "No hay faltantes declarados en esta etapa."
    return "\n".join(f"- {value}" for value in values)
