from __future__ import annotations

import inspect
import subprocess
import sys
from pathlib import Path

from pymia.telegram_runtime import SENTINEL, RuntimeResult, handle_telegram_message


ROOT = Path(__file__).resolve().parents[2]


def test_dry_run_contains_sentinel() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "pymia.telegram_runtime", "--dry-run", "no se si gano plata"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=True,
    )
    assert SENTINEL in proc.stdout


def test_profitability_query_requests_evidence() -> None:
    result = handle_telegram_message("no se si gano plata")
    lowered = result.text.lower()
    assert SENTINEL in result.text
    assert "ventas del período" in lowered or "ventas del periodo" in lowered
    assert "costos o compras" in lowered
    assert "gastos fijos" in lowered
    assert result.mode == "needs_evidence"


def test_empty_message_returns_blocked() -> None:
    result = handle_telegram_message("   ")
    assert SENTINEL in result.text
    assert result.mode == "blocked"


def test_runtime_result_has_no_gateway_fields() -> None:
    fields = RuntimeResult.__dataclass_fields__
    assert "handled" not in fields
    assert "skip_gateway" not in fields


def test_module_does_not_import_hermes() -> None:
    module_source = inspect.getsource(sys.modules["pymia.telegram_runtime"])
    forbidden = ("import hermes", "from hermes", "import pymia.hermes", "from pymia.hermes")
    for token in forbidden:
        assert token not in module_source
