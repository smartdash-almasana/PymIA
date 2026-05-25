from __future__ import annotations

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from main import run_message


def main() -> None:
    message = "vendo mucho pero no sé si gano plata"
    result = run_message(message)

    assert "CONTRASTE CON CATÁLOGO PYME" not in result
    assert "Patologías candidatas" not in result
    assert "No son hallazgos confirmados" not in result
    assert result.strip()

    print("INTEGRATED_INPUT:", message)
    print(result)
    print("INTEGRATED_SMOKE_OK:", True)


if __name__ == "__main__":
    main()
