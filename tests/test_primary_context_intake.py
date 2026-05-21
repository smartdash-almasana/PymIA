from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_primary_context_module():
    conversa_dir = Path(__file__).resolve().parents[1] / "conversa-engine"
    if str(conversa_dir) not in sys.path:
        sys.path.insert(0, str(conversa_dir))
    module_path = conversa_dir / "primary_context_intake.py"
    spec = importlib.util.spec_from_file_location("primary_context_intake", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_primary_context_intake_classifies_margin_uncertainty() -> None:
    mod = _load_primary_context_module()
    record = mod.build_primary_context_record(
        tenant_id="tenant-test",
        message_text="vendo mucho pero no se si gano plata",
    )

    pain_codes = {p.code for p in record.expressed_pain}
    maturity_codes = {m.code for m in record.maturity_hints}

    assert "margin_uncertainty" in pain_codes
    assert "reactiva" in maturity_codes
    assert record.state == "pending_data"
    assert record.evidence_gap.missing_evidence == ["ventas", "costos", "lista_precios"]


def test_primary_context_record_persists_json(tmp_path: Path) -> None:
    mod = _load_primary_context_module()
    record = mod.build_primary_context_record(
        tenant_id="tenant-test",
        message_text="quiero ordenar un excel",
    )
    out = mod.persist_primary_context_record(
        record=record,
        tenant_id="tenant-test",
        user_id="user-1",
        base_path=tmp_path,
    )
    assert out.exists()
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["tenant_id"] == "tenant-test"
    assert payload["state"] == "pending_data"

