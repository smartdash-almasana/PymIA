import pytest

from pymia.smartpyme.anamnesis_fsm import _build_preliminary_taxonomy_signal
from pymia.smartpyme.anamnesis_fsm_integration import (
    AnamnesisTurnInput,
    run_anamnesis_turn,
)
from pymia.smartpyme.preliminary_taxonomy import (
    PreliminaryTaxonomySignal,
    PreliminaryTaxonomyStatus,
)


def test_contract_requires_core_fields_and_fail_closed_preliminary_confidence() -> None:
    with pytest.raises(ValueError, match="tenant_id"):
        PreliminaryTaxonomySignal(
            tenant_id="",
            source="raw_first_message",
            status=PreliminaryTaxonomyStatus.PRELIMINARY,
            organism_type="textil",
            sales_channels=("wholesale",),
            confidence=0.65,
            created_from="fabrico ropa y vendo por mayor",
        )

    with pytest.raises(ValueError, match="PRELIMINARY exige confidence < 1.0"):
        PreliminaryTaxonomySignal(
            tenant_id="T-LC-001",
            source="raw_first_message",
            status=PreliminaryTaxonomyStatus.PRELIMINARY,
            organism_type="textil",
            sales_channels=("wholesale",),
            confidence=1.0,
            created_from="fabrico ropa y vendo por mayor",
        )


def test_strong_message_builds_preliminary_signal_dict() -> None:
    signal = _build_preliminary_taxonomy_signal(
        "fabrico ropa, corto, coso y vendo por mayor",
        "T-LC-002",
    )

    assert signal is not None
    assert signal["tenant_id"] == "T-LC-002"
    assert signal["status"] == "PRELIMINARY"
    assert signal["source"] == "raw_first_message"
    assert signal["created_from"] == "fabrico ropa, corto, coso y vendo por mayor"
    assert signal["organism_type"] in {"textil", "produccion_fabrica"}
    assert "wholesale" in signal["sales_channels"]
    assert float(signal["confidence"]) < 1.0


def test_ambiguous_message_does_not_build_preliminary_signal() -> None:
    signal = _build_preliminary_taxonomy_signal("hola", "T-LC-003")

    assert signal is None


def test_preliminary_signal_does_not_activate_taxonomy_hypotheses_or_evidence() -> None:
    output = run_anamnesis_turn(
        AnamnesisTurnInput(
            tenant_id="T-LC-004",
            session_id="S-LC-004",
            message_text="fabrico ropa y vendo por mayor",
            previous_progressive_context=None,
        )
    )

    assert output.updated_progressive_context["has_preliminary_taxonomy"] is True
    assert output.updated_progressive_context["has_taxonomy"] is False
    assert output.updated_progressive_context["has_confirmed_taxonomy"] is False
    assert output.updated_progressive_context["has_hypotheses"] is False
    assert output.updated_progressive_context["has_evidence_requests"] is False

    fsm_state = output.updated_progressive_context["fsm_state"]
    assert fsm_state["preliminary_taxonomy"] is not None
    assert fsm_state["taxonomy"] is None
    assert fsm_state["hypotheses"] == []
    assert fsm_state["evidence_requests"] == []
