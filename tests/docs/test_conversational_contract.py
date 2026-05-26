from __future__ import annotations

from pathlib import Path


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_soul_md_matches_clinical_boundary():
    text = _read("docs/hermes/soul.md")
    assert "asistente técnico enfocado en desarrollo" not in text
    assert "Hermes conversa y orquesta; PymIA computa" in text


def test_anamnesis_term_usage_consistency():
    adr = _read("docs/adr/ADR-010-conversational-anamnesis-contract.md")
    assert "Status: Accepted" in adr

    boundary = _read("docs/hermes/CONVERSATIONAL_BOUNDARY_POLICY.md")
    assert "PymIA computa" in boundary


def test_hermes_audit_policy_blocks_premature_diagnosis():
    policy = _read("docs/conversa-engine/HERMES_AGENT_AUDIT_POLICY.md")
    must_have = [
        "ALLOW",
        "WARN",
        "BLOCK",
        "Inventar hallazgos",
        "Convertir warnings en diagnósticos",
    ]
    for token in must_have:
        assert token in policy


def test_no_hypothesis_without_taxonomy():
    adr = _read("docs/adr/ADR-010-conversational-anamnesis-contract.md")
    assert "OperationalHypothesis" in adr
    assert "BusinessTaxonomySnapshot" in adr


def test_interrogation_taxonomy_slice_mentions_organism():
    target = Path("docs/smartpyme/SMARTPYME_INTERROGATION_TAXONOMY.md")
    if not target.exists():
        # If doc is absent in current checkout, keep test deterministic and explicit.
        assert target.exists(), "Missing SMARTPYME_INTERROGATION_TAXONOMY.md"

    text = target.read_text(encoding="utf-8")
    has_business_taxonomy = "BusinessTaxonomySnapshot" in text
    has_org_taxonomy = "taxonomía de organismo" in text.lower()
    assert has_business_taxonomy or has_org_taxonomy
