from __future__ import annotations

import json
from pathlib import Path

from pymia.cli import service_1_product as cli


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _packet() -> dict:
    return json.loads((_repo_root() / "docs" / "service_1_operability_packet.v1.json").read_text(encoding="utf-8"))


def test_operability_packet_is_indexed_and_points_to_official_surface() -> None:
    root = _repo_root()
    readme = (root / "docs" / "current" / "README.md").read_text(encoding="utf-8")
    doc = (root / "docs" / "current" / "SERVICE_1_OPERABILITY_PACKET.md").read_text(encoding="utf-8")
    packet = _packet()

    assert "SERVICE_1_OPERABILITY_PACKET.md" in readme
    assert packet["schema_version"] == "SERVICE_1_OPERABILITY_PACKET_V1"
    assert packet["status"] == "ACTIVE"
    assert packet["official_command_module"] == "pymia.cli.service_1_product"
    assert packet["official_entrypoint_path"] == "pymia/cli/service_1_product.py"
    assert packet["canonical_product_root"] == "pymia/smartpyme/service_1_product_pipeline_v1.py"
    assert (root / packet["official_entrypoint_path"]).exists()
    assert (root / packet["canonical_product_root"]).exists()
    assert "python -m pymia.cli.service_1_product" in doc
    assert "--tool-requests" in doc
    assert "--requested-capability" in doc
    assert "allowed_option_ids" in doc


def test_operability_packet_commands_use_supported_cli_modes_only() -> None:
    packet = _packet()
    first = packet["commands"]["first_pass_explicit_tool"]
    final = packet["commands"]["final_pass_explicit_tool"]
    plan = packet["commands"]["plan_only_liq_001"]

    for command in (first, final, plan):
        assert command[:3] == ["python", "-m", "pymia.cli.service_1_product"]
        assert "--xlsx" in command
        assert "--owner-column-answers" in command
        assert "--output-dir" in command
        assert "--result-json" in command
    assert "--tool-requests" in first
    assert "--tool-requests" in final
    assert "--semantic-owner-answers" in final
    assert "--requested-capability" in plan
    assert "--tool-requests" not in plan


def test_operability_packet_real_cafeteria_example_runs_to_xlsx_output(tmp_path: Path) -> None:
    root = _repo_root()
    packet = _packet()
    fixture = root / packet["fixture"]["path"]
    assert fixture.exists()
    output_dir = tmp_path / "output"
    output_dir.mkdir(parents=True)

    first = cli.run_service_1_product_entrypoint_v1(
        xlsx_path=fixture,
        owner_column_answers=packet["operator_inputs"]["owner_column_answers_json"],
        semantic_owner_answers=None,
        output_dir=output_dir,
        sheet_name=packet["fixture"]["sheet"],
        requested_capability="sales_total",
        semantic_owner_actor_id="owner-cli",
        semantic_owner_actor_role="owner",
    )
    assert first["status"] == packet["expected_statuses"]["first_pass_without_semantic_answers"]
    assert first["product_pipeline"]["tools_executed"] is False
    assert not list(output_dir.glob("*.xlsx"))

    semantic_answers = {
        question["decision_id"]: {"action": "ACCEPT"}
        for question in first["product_pipeline"]["owner_questions"]
    }
    assert semantic_answers

    final = cli.run_service_1_product_entrypoint_v1(
        xlsx_path=fixture,
        owner_column_answers=packet["operator_inputs"]["owner_column_answers_json"],
        semantic_owner_answers=semantic_answers,
        output_dir=output_dir,
        sheet_name=packet["fixture"]["sheet"],
        requested_capability="sales_total",
        semantic_owner_actor_id="owner-cli",
        semantic_owner_actor_role="owner",
    )
    # sales_total is not yet P8-governed; the current root must fail closed.
    assert final["status"] == "BLOCKED"
    assert final["blocked_reason"] == "CAPABILITY_NOT_GOVERNED"
    assert final["product_pipeline"]["semantic_bindings_confirmed"] is True
    assert final["product_pipeline"]["computation_executed"] is False
    assert final["product_pipeline"]["tools_executed"] is False
    assert final["product_pipeline"]["physical_run"] is None
    assert not list(output_dir.glob("*.xlsx"))


def test_operability_packet_blocks_free_text_semantic_answers(tmp_path: Path) -> None:
    root = _repo_root()
    packet = _packet()
    fixture = root / packet["fixture"]["path"]
    output_dir = tmp_path / "output"
    output_dir.mkdir(parents=True)

    first = cli.run_service_1_product_entrypoint_v1(
        xlsx_path=fixture,
        owner_column_answers=packet["operator_inputs"]["owner_column_answers_json"],
        semantic_owner_answers=None,
        output_dir=output_dir,
        sheet_name=packet["fixture"]["sheet"],
        requested_capability="sales_total",
        semantic_owner_actor_id="owner-cli",
        semantic_owner_actor_role="owner",
    )
    invalid = {
        question["decision_id"]: {
            "action": "UNSUPPORTED_ACTION",
            "correction_text": "texto libre no canónico",
        }
        for question in first["product_pipeline"]["owner_questions"]
    }
    blocked = cli.run_service_1_product_entrypoint_v1(
        xlsx_path=fixture,
        owner_column_answers=packet["operator_inputs"]["owner_column_answers_json"],
        semantic_owner_answers=invalid,
        output_dir=output_dir,
        sheet_name=packet["fixture"]["sheet"],
        requested_capability="sales_total",
        semantic_owner_actor_id="owner-cli",
        semantic_owner_actor_role="owner",
    )
    assert blocked["status"] == packet["expected_statuses"]["invalid_free_text_semantic_reentry"]
    assert blocked["blocked_reason"] == "BLOCK_SEM8_OWNER_RESPONSES_INVALID"
