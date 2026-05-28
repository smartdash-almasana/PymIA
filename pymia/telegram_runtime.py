from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

SENTINEL = "[PymIA:TELEGRAM_RUNTIME]"


@dataclass(frozen=True)
class RuntimeResult:
    text: str
    source: Literal["pymia"] = "pymia"
    mode: Literal["controlled", "blocked", "needs_evidence"] = "controlled"


def handle_telegram_message(message: str) -> RuntimeResult:
    """Fail-closed runtime sin Hermes."""
    normalized = (message or "").strip()
    if not normalized:
        return RuntimeResult(
            text=f"{SENTINEL} No recibí mensaje. ¿Podés enviar la consulta?",
            mode="blocked",
        )

    lowered = normalized.lower()
    profitability_keywords = (
        "gano",
        "gano plata",
        "rentabilidad",
        "ganancia",
        "beneficio",
        "ingresos",
        "gastos",
        "costos",
        "costes",
        "perdida",
        "pérdida",
    )

    if any(keyword in lowered for keyword in profitability_keywords):
        return RuntimeResult(
            text=(
                f"{SENTINEL} Para analizar si estas ganando plata necesito:\n"
                f"- ventas del periodo\n"
                f"- costos o compras\n"
                f"- gastos fijos\n\n"
                f"Podes subir un Excel con estos datos o indicarme los valores?"
            ),
            mode="needs_evidence",
        )

    return RuntimeResult(
        text=(
            f"{SENTINEL} Entiendo tu consulta. Para ayudarte necesito más contexto operativo. "
            f"¿Querés revisar ventas, costos, stock, caja o subir un Excel?"
        ),
        mode="controlled",
    )


def main() -> None:
    import sys

    if "--dry-run" in sys.argv:
        index = sys.argv.index("--dry-run")
        message = sys.argv[index + 1] if (index + 1) < len(sys.argv) else ""
        result = handle_telegram_message(message)
        print(f"Text: {result.text}")
        print(f"Source: {result.source}")
        print(f"Mode: {result.mode}")
        return

    print('Uso: python -m pymia.telegram_runtime --dry-run "mensaje"')


if __name__ == "__main__":
    main()
