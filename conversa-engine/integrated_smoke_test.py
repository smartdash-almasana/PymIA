from __future__ import annotations

from main import run_message


def main() -> None:
    message = "vendo mucho pero no sé si gano plata"
    result = run_message(message)

    assert "tensión de caja" in result.lower() or "tension de caja" in result.lower()
    assert "CONTRASTE CON CATÁLOGO PYME" in result
    assert "Patologías candidatas" in result
    assert "Evidencia requerida" in result
    assert "No son hallazgos confirmados" in result

    print("INTEGRATED_INPUT:", message)
    print(result)
    print("INTEGRATED_SMOKE_OK:", True)


if __name__ == "__main__":
    main()
