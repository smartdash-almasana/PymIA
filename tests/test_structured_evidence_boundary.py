from __future__ import annotations

from pymia.contracts.evidence_v1 import EvidenceTable, StructuredEvidence
from pymia.interfaces.conversational_port import ClinicalConversationalPort, ConversationalInput


def test_conversational_input_accepts_structured_evidence() -> None:
    evidence = StructuredEvidence(
        tenant_id="tenant-test",
        document_type="xlsx_operational_evidence",
        source="xlsx_upload",
        file_name="textil_cosida_demo_pymia.xlsx",
        tables=[
            EvidenceTable(
                sheet_name="ventas",
                columns=["producto", "ventas", "costo"],
                rows=[["remera", 120000.0, 80000.0]],
            )
        ],
        computed_variables={
            "ventas_total": 120000.0,
            "costos_total": 80000.0,
            "margen_bruto": 40000.0,
            "margen_bruto_pct": 0.3333,
            "margen_objetivo_pct": 0.35,
        },
    )

    input_ = ConversationalInput(
        tenant_id="tenant-test",
        channel="telegram",
        text="subo el excel textil para revisar rentabilidad",
        evidence=evidence,
    )

    assert input_.evidence is evidence


def test_kernel_does_not_request_sales_or_costs_when_structured_evidence_has_them() -> None:
    evidence = StructuredEvidence(
        tenant_id="tenant-test",
        document_type="xlsx_operational_evidence",
        source="xlsx_upload",
        file_name="textil_cosida_demo_pymia.xlsx",
        computed_variables={
            "ventas_total": 2600000.0,
            "costos_total": 2100000.0,
            "margen_bruto": 500000.0,
            "margen_bruto_pct": 0.1923,
            "margen_objetivo_pct": 0.35,
        },
    )

    port = ClinicalConversationalPort()
    output = port.handle(
        ConversationalInput(
            tenant_id="tenant-test",
            channel="telegram",
            text="revisar rentabilidad con el excel recibido",
            evidence=evidence,
        )
    )

    assert output.status == "ok"
    assert output.message is not None
    assert "ventas del período" not in output.message
    assert "costos o facturas de compra" not in output.message
    assert "evidencia estructurada" in output.message.lower()
    assert "margen" in output.message.lower()
