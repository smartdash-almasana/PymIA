import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from pymia.contracts.language_corpus_v1 import (
    LanguageCorpus,
    LanguageCorpusEntry,
    load_language_corpus_seed,
    owner_label_for,
    owner_label_for_variable_id,
)


def _entry(**overrides) -> LanguageCorpusEntry:
    payload = {
        "concept_id": "op_sales_gross",
        "canonical_label": "ventas brutas",
        "owner_synonyms": ["ventas", "facturacion"],
        "owner_expression_patterns": ["referencia libre a cuanto se vendio"],
        "technical_synonyms": ["ventas_total"],
        "tags": ["ventas", "evidencia_operativa"],
        "related_evidence_ids": ["ventas_periodo"],
        "related_variable_ids": ["ventas_total"],
        "related_formula_ids": [],
        "related_pathology_ids": [],
        "allowed_owner_questions": ["Las ventas informadas corresponden al periodo que queres analizar?"],
        "allowed_report_phrases": ["Se identifico evidencia relacionada con ventas del periodo."],
        "allowed_operator_language": ["variable de ventas brutas detectada"],
        "forbidden_language": ["el problema esta en las ventas"],
        "ambiguity_policy": "REQUEST_EVIDENCE",
        "diagnostic_authority": "NONE",
        "version": "0.1.0",
        "status": "DRAFT",
        "source_refs": ["docs/contratos/language-corpus-v1.md"],
    }
    payload.update(overrides)
    return LanguageCorpusEntry(**payload)


def test_language_corpus_entry_validates_seed_like_entry():
    entry = _entry()

    assert entry.concept_id == "op_sales_gross"
    assert entry.diagnostic_authority == "NONE"
    assert entry.status == "DRAFT"
    assert entry.source_refs == ["docs/contratos/language-corpus-v1.md"]


def test_language_corpus_rejects_non_none_diagnostic_authority():
    with pytest.raises(ValidationError):
        _entry(diagnostic_authority="DIAGNOSE")


def test_language_corpus_rejects_forbidden_language_inside_allowed_text():
    with pytest.raises(ValidationError):
        _entry(
            allowed_report_phrases=["El problema esta en las ventas."],
            forbidden_language=["el problema esta en las ventas"],
        )


def test_language_corpus_requires_source_refs():
    with pytest.raises(ValidationError):
        _entry(source_refs=[])


def test_language_corpus_rejects_duplicate_concept_ids():
    entry = _entry()
    with pytest.raises(ValidationError):
        LanguageCorpus(version="0.1.0", entries=[entry, entry])


def test_owner_label_for_returns_safe_label_without_inference():
    corpus = LanguageCorpus(version="0.1.0", entries=[_entry()])

    assert owner_label_for("op_sales_gross", corpus) == "ventas brutas"


def test_owner_label_for_unknown_concept_fails_closed_to_raw_id():
    corpus = LanguageCorpus(version="0.1.0", entries=[_entry()])

    assert owner_label_for("unknown_concept", corpus) == "unknown_concept"


def test_language_corpus_tags_are_plain_metadata_not_findings():
    entry = _entry(tags=["ventas", "margen", "evidencia_operativa"])

    assert entry.tags == ["ventas", "margen", "evidencia_operativa"]
    forbidden_attrs = [
        "finding",
        "findings",
        "finding_status",
        "pathology_status",
        "confirmed",
        "confirmed_finding",
    ]
    for attr in forbidden_attrs:
        assert not hasattr(entry, attr)


def test_language_corpus_owner_synonyms_are_plain_metadata_not_evidence():
    entry = _entry(owner_synonyms=["ventas", "facturacion", "ingresos"])

    assert entry.owner_synonyms == ["ventas", "facturacion", "ingresos"]
    forbidden_attrs = [
        "evidence",
        "evidence_id",
        "created_evidence",
        "structured_evidence",
        "evidence_table",
    ]
    for attr in forbidden_attrs:
        assert not hasattr(entry, attr)


def test_language_corpus_seed_json_validates_exactly_three_draft_concepts():
    seed_path = Path("pymia/contracts/language_corpus_seed.json")
    payload = json.loads(seed_path.read_text(encoding="utf-8"))

    corpus = LanguageCorpus(**payload)

    assert corpus.version == "0.1.0"
    assert corpus.status == "DRAFT"
    assert [entry.concept_id for entry in corpus.entries] == [
        "op_sales_gross",
        "op_cost_cogs",
        "op_cash_collection",
    ]
    assert all(entry.diagnostic_authority == "NONE" for entry in corpus.entries)
    assert all(entry.status == "DRAFT" for entry in corpus.entries)
    assert all(entry.source_refs == ["docs/contratos/language-corpus-v1.md"] for entry in corpus.entries)


def test_language_corpus_seed_json_does_not_activate_runtime_or_pack_behavior():
    payload = json.loads(Path("pymia/contracts/language_corpus_seed.json").read_text(encoding="utf-8"))
    corpus = LanguageCorpus(**payload)

    assert not hasattr(corpus, "run")
    assert not hasattr(corpus, "execute")
    assert not hasattr(corpus, "load_pack")
    assert not hasattr(corpus, "diagnose")
    assert not hasattr(corpus, "create_evidence")


def test_load_language_corpus_seed_loads_static_draft_seed():
    corpus = load_language_corpus_seed()

    assert corpus.version == "0.1.0"
    assert corpus.status == "DRAFT"
    assert len(corpus.entries) == 3


def test_owner_label_for_variable_id_uses_related_variable_ids_fail_closed():
    corpus = load_language_corpus_seed()

    assert owner_label_for_variable_id("ventas_total", corpus) == "ventas brutas"
    assert owner_label_for_variable_id("unknown_variable", corpus) == "unknown_variable"


def test_language_corpus_module_does_not_import_core_or_runtime_layers():
    import inspect
    import pymia.contracts.language_corpus_v1 as module

    source = inspect.getsource(module).lower()
    forbidden = [
        "diagnostic_core",
        "formula_engine",
        "orchestration",
        "telegram",
        "hermes",
        "llm_operator",
        "fastapi",
        "packloader",
    ]
    for token in forbidden:
        assert token not in source
