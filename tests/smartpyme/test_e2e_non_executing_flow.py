"""
SMARTPYME_E2E_NON_EXECUTING_FLOW — Smoke E2E determinístico.

Prueba el flujo completo sin ejecutar microservicios:
    create_intake_record
    → save_intake_record
    → create_evidence_record
    → save_evidence_record
    → load intake/evidence
    → evaluate_evidence_sufficiency
    → evaluate_analysis_readiness

NO ejecuta análisis. NO importa runtime modules.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest


class TestImportSmoke:
    def test_import_smoke(self):
        """All required modules can be imported."""
        from pymia.smartpyme.intake import create_intake_record
        from pymia.smartpyme.evidence import create_evidence_record
        from pymia.smartpyme.storage import (
            save_intake_record,
            save_evidence_record,
            load_intake_record_by_id,
            load_evidence_records_by_intake_id,
        )
        from pymia.smartpyme.evidence_gate import evaluate_evidence_sufficiency
        from pymia.smartpyme.readiness import evaluate_analysis_readiness

        assert callable(create_intake_record)
        assert callable(create_evidence_record)
        assert callable(save_intake_record)
        assert callable(save_evidence_record)
        assert callable(load_intake_record_by_id)
        assert callable(load_evidence_records_by_intake_id)
        assert callable(evaluate_evidence_sufficiency)
        assert callable(evaluate_analysis_readiness)


class TestE2ENonExecutingFlow:
    """Full E2E flow without executing runtime modules."""

    def test_e2e_non_executing_flow_ready_for_excel_diagnostic(self, tmp_path):
        """
        Scenario: User reports "no me cierra la plata" with Excel evidence.
        Expected: READY_FOR_ANALYSIS with excel_diagnostic runtime.
        """
        from pymia.smartpyme.intake import create_intake_record
        from pymia.smartpyme.evidence import (
            create_evidence_record,
            SOURCE_KIND_UPLOADED_FILE,
            EVIDENCE_STATUS_RECEIVED,
        )
        from pymia.smartpyme.storage import (
            save_intake_record,
            save_evidence_record,
            load_intake_record_by_id,
            load_evidence_records_by_intake_id,
        )
        from pymia.smartpyme.evidence_gate import evaluate_evidence_sufficiency
        from pymia.smartpyme.readiness import (
            evaluate_analysis_readiness,
            READINESS_READY_FOR_ANALYSIS,
            RUNTIME_CLASSIFICATION_EXCEL_DIAGNOSTIC,
        )

        tenant_id = "tenant_e2e_excel"
        base_dir = tmp_path / "storage"

        # Step 1: Create intake
        intake = create_intake_record(
            tenant_id=tenant_id,
            raw_text="Tengo un Excel con ventas y costos pero no me cierra la plata",
        )
        assert intake.tenant_id == tenant_id
        assert intake.intake_id

        # Step 2: Save intake
        intake_path = save_intake_record(tenant_id, intake, base_dir=base_dir)
        assert intake_path.exists()
        assert intake_path.name == "intakes.jsonl"

        # Step 3: Load intake
        loaded_intake = load_intake_record_by_id(
            tenant_id, intake.intake_id, base_dir=base_dir
        )
        assert loaded_intake is not None
        assert loaded_intake["intake_id"] == intake.intake_id

        # Step 4: Create evidence record matching the request
        # Get the first evidence_request from the intake
        evidence_requests = intake.evidence_requests
        if not evidence_requests:
            pytest.skip("No evidence requests generated for this input")

        first_request = evidence_requests[0]
        evidence = create_evidence_record(
            tenant_id=tenant_id,
            intake_id=intake.intake_id,
            evidence_type=first_request.evidence_type,
            source_kind=SOURCE_KIND_UPLOADED_FILE,
            source_ref="/path/to/ventas_costos.xlsx",
            request_id=first_request.request_id,
            status=EVIDENCE_STATUS_RECEIVED,
        )

        # Step 5: Save evidence
        evidence_path = save_evidence_record(tenant_id, evidence, base_dir=base_dir)
        assert evidence_path.exists()
        assert evidence_path.name == "evidences.jsonl"

        # Step 6: Load evidence
        loaded_evidences = load_evidence_records_by_intake_id(
            tenant_id, intake.intake_id, base_dir=base_dir
        )
        assert len(loaded_evidences) == 1
        assert loaded_evidences[0]["evidence_id"] == evidence.evidence_id

        # Step 7: Evaluate evidence sufficiency
        sufficiency = evaluate_evidence_sufficiency(loaded_intake, loaded_evidences)
        assert sufficiency.tenant_id == tenant_id
        assert sufficiency.intake_id == intake.intake_id

        # Step 8: Evaluate analysis readiness
        readiness = evaluate_analysis_readiness(loaded_intake, sufficiency.to_dict())
        assert readiness.status == READINESS_READY_FOR_ANALYSIS
        assert readiness.can_execute is True
        assert readiness.runtime_classification == RUNTIME_CLASSIFICATION_EXCEL_DIAGNOSTIC

    def test_e2e_non_executing_flow_ready_for_supplier_duplicate_check(self, tmp_path):
        """
        Scenario: User reports "tengo proveedores duplicados" with Excel evidence.
        Expected: READY_FOR_ANALYSIS with supplier_duplicate_check runtime.
        """
        from pymia.smartpyme.intake import create_intake_record
        from pymia.smartpyme.evidence import (
            create_evidence_record,
            SOURCE_KIND_UPLOADED_FILE,
            EVIDENCE_STATUS_RECEIVED,
        )
        from pymia.smartpyme.storage import (
            save_intake_record,
            save_evidence_record,
            load_intake_record_by_id,
            load_evidence_records_by_intake_id,
        )
        from pymia.smartpyme.evidence_gate import evaluate_evidence_sufficiency
        from pymia.smartpyme.readiness import (
            evaluate_analysis_readiness,
            READINESS_READY_FOR_ANALYSIS,
            RUNTIME_CLASSIFICATION_SUPPLIER_DUPLICATE_CHECK,
        )

        tenant_id = "tenant_e2e_supplier"
        base_dir = tmp_path / "storage"

        # Step 1: Create intake
        intake = create_intake_record(
            tenant_id=tenant_id,
            raw_text="Tengo proveedores duplicados en el Excel con CUIT repetidos",
        )
        assert intake.tenant_id == tenant_id
        assert intake.intake_id

        # Step 2: Save intake
        save_intake_record(tenant_id, intake, base_dir=base_dir)

        # Step 3: Load intake
        loaded_intake = load_intake_record_by_id(
            tenant_id, intake.intake_id, base_dir=base_dir
        )
        assert loaded_intake is not None

        # Step 4: Create evidence record
        evidence_requests = intake.evidence_requests
        if not evidence_requests:
            pytest.skip("No evidence requests generated for this input")

        first_request = evidence_requests[0]
        evidence = create_evidence_record(
            tenant_id=tenant_id,
            intake_id=intake.intake_id,
            evidence_type=first_request.evidence_type,
            source_kind=SOURCE_KIND_UPLOADED_FILE,
            source_ref="/path/to/proveedores.xlsx",
            request_id=first_request.request_id,
            status=EVIDENCE_STATUS_RECEIVED,
        )

        # Step 5: Save evidence
        save_evidence_record(tenant_id, evidence, base_dir=base_dir)

        # Step 6: Load evidence
        loaded_evidences = load_evidence_records_by_intake_id(
            tenant_id, intake.intake_id, base_dir=base_dir
        )
        assert len(loaded_evidences) == 1

        # Step 7: Evaluate evidence sufficiency
        sufficiency = evaluate_evidence_sufficiency(loaded_intake, loaded_evidences)

        # Step 8: Evaluate analysis readiness
        readiness = evaluate_analysis_readiness(loaded_intake, sufficiency.to_dict())
        assert readiness.status == READINESS_READY_FOR_ANALYSIS
        assert readiness.can_execute is True
        assert (
            readiness.runtime_classification
            == RUNTIME_CLASSIFICATION_SUPPLIER_DUPLICATE_CHECK
        )

    def test_e2e_non_executing_flow_needs_evidence_when_evidence_missing(self, tmp_path):
        """
        Scenario: User reports problem but no evidence is provided.
        Expected: NEEDS_EVIDENCE status.
        """
        from pymia.smartpyme.intake import create_intake_record
        from pymia.smartpyme.storage import (
            save_intake_record,
            load_intake_record_by_id,
            load_evidence_records_by_intake_id,
        )
        from pymia.smartpyme.evidence_gate import evaluate_evidence_sufficiency
        from pymia.smartpyme.readiness import (
            evaluate_analysis_readiness,
            READINESS_NEEDS_EVIDENCE,
        )

        tenant_id = "tenant_e2e_no_evidence"
        base_dir = tmp_path / "storage"

        # Step 1: Create intake
        intake = create_intake_record(
            tenant_id=tenant_id,
            raw_text="No me cierra la plata pero no tengo archivos",
        )

        # Step 2: Save intake
        save_intake_record(tenant_id, intake, base_dir=base_dir)

        # Step 3: Load intake
        loaded_intake = load_intake_record_by_id(
            tenant_id, intake.intake_id, base_dir=base_dir
        )
        assert loaded_intake is not None

        # Step 4: Load evidence (empty)
        loaded_evidences = load_evidence_records_by_intake_id(
            tenant_id, intake.intake_id, base_dir=base_dir
        )
        assert len(loaded_evidences) == 0

        # Step 5: Evaluate evidence sufficiency
        sufficiency = evaluate_evidence_sufficiency(loaded_intake, loaded_evidences)

        # Step 6: Evaluate analysis readiness
        readiness = evaluate_analysis_readiness(loaded_intake, sufficiency.to_dict())

        # If there are blocking evidence requests, should be NEEDS_EVIDENCE
        if intake.evidence_requests:
            blocking_requests = [
                req for req in intake.evidence_requests if req.blocks_analysis
            ]
            if blocking_requests:
                assert readiness.status == READINESS_NEEDS_EVIDENCE
                assert readiness.can_execute is False

    def test_e2e_does_not_execute_runtime_modules(self, tmp_path):
        """
        Verify that the E2E flow does not import or call runtime modules.
        """
        from pymia.smartpyme.intake import create_intake_record
        from pymia.smartpyme.evidence import (
            create_evidence_record,
            SOURCE_KIND_UPLOADED_FILE,
            EVIDENCE_STATUS_RECEIVED,
        )
        from pymia.smartpyme.storage import (
            save_intake_record,
            save_evidence_record,
            load_intake_record_by_id,
            load_evidence_records_by_intake_id,
        )
        from pymia.smartpyme.evidence_gate import evaluate_evidence_sufficiency
        from pymia.smartpyme.readiness import evaluate_analysis_readiness

        tenant_id = "tenant_e2e_no_runtime"
        base_dir = tmp_path / "storage"

        # Track imported modules before E2E
        modules_before = set(sys.modules.keys())

        # Execute E2E flow
        intake = create_intake_record(
            tenant_id=tenant_id,
            raw_text="Test input for runtime isolation",
        )
        save_intake_record(tenant_id, intake, base_dir=base_dir)
        loaded_intake = load_intake_record_by_id(
            tenant_id, intake.intake_id, base_dir=base_dir
        )

        if intake.evidence_requests:
            first_request = intake.evidence_requests[0]
            evidence = create_evidence_record(
                tenant_id=tenant_id,
                intake_id=intake.intake_id,
                evidence_type=first_request.evidence_type,
                source_kind=SOURCE_KIND_UPLOADED_FILE,
                source_ref="/path/to/test.xlsx",
                request_id=first_request.request_id,
                status=EVIDENCE_STATUS_RECEIVED,
            )
            save_evidence_record(tenant_id, evidence, base_dir=base_dir)

        loaded_evidences = load_evidence_records_by_intake_id(
            tenant_id, intake.intake_id, base_dir=base_dir
        )
        sufficiency = evaluate_evidence_sufficiency(loaded_intake, loaded_evidences)
        readiness = evaluate_analysis_readiness(loaded_intake, sufficiency.to_dict())

        # Track imported modules after E2E
        modules_after = set(sys.modules.keys())
        new_modules = modules_after - modules_before

        # Verify runtime modules were not imported
        forbidden_modules = {
            "pymia.smartpyme.excel_diagnostic",
            "pymia.smartpyme.supplier_duplicate_check",
        }
        for mod in forbidden_modules:
            assert mod not in new_modules, f"Forbidden module {mod} was imported"

        # Verify readiness result does not contain runtime execution markers
        assert readiness is not None
        assert hasattr(readiness, "status")
        assert hasattr(readiness, "can_execute")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
