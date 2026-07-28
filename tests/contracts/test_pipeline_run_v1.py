from pymia.contracts.pipeline_run_v1 import build_pipeline_run_record


def test_pipeline_run_record_uses_application_trace_identity() -> None:
    record = build_pipeline_run_record(
        tenant_id="tenant_1",
        intake_id="intake_1",
        message="Necesito entender mi caja",
        evidence_ids=["evidence_1"],
        status="COMPLETED",
        output_payload={"status": "ok"},
        steps_executed=["step_1"],
    )

    assert record.pipeline_name == "vertical_cli_evidence_spine"
    assert record.pipeline_module == "pymia.cli.vertical_slice"
    assert record.entrypoint == "build_report"
    assert record.service_name == "vertical_slice_cli"
    assert record.metadata["case_id_alias"] == "intake_1"
