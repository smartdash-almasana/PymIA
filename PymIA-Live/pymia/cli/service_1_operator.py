from __future__ import annotations

import argparse
import json
import uuid
from pathlib import Path
from typing import Any

from pymia.smartpyme.service_1_executable_entrypoint_v1 import (
    run_service_1_executable_entrypoint_v1,
)
from pymia.smartpyme.service_1_column_confirmation_packet_v1 import (
    build_service_1_column_confirmation_packet_v1,
)
from pymia.smartpyme.service_1_case_delivery_folder_v1 import (
    build_service_1_human_review_gate_v1,
    finalize_service_1_case_delivery_folder_v1,
    write_service_1_case_delivery_folder_v1,
)
from pymia.smartpyme.service_1_xlsx_structure_v1 import (
    read_service_1_xlsx_structure_v1,
)
from pymia.smartpyme.service_1_qa_delivery_gate_v1 import (
    evaluate_service_1_qa_delivery_gate_v1,
)
from pymia.smartpyme.service_1_first_aid_minimal_v1 import (
    load_confirmed_columns_v1,
    evaluate_first_aid_minimal_eligibility_v1,
    run_first_aid_minimal_v1,
    render_first_aid_owner_summary_v1,
)
from pymia.smartpyme.service_1_pipeline_v1 import (
    run_service_1_pipeline_v1,
)
from pymia.smartpyme.service_1_post_tool_owner_delivery_summary_v1 import (
    SUMMARY_FILENAME,
    render_service_1_post_tool_owner_delivery_summary_v1,
)
from pymia.smartpyme.exceland_execution_flow_v1 import (
    run_exceland_execution_flow_v1,
)
from pymia.smartpyme.service_1_owner_reentry_bridge_v1 import (
    run_service_1_owner_reentry_bridge_v1,
)
from pymia.smartpyme.service_1_next_owner_question_view_v1 import (
    build_service_1_next_owner_question_view_v1,
)


def _infer_mime_type(filename: str) -> str | None:
    """Infer MIME type from file extension. Only XLSX is recognized."""
    ext = Path(filename).suffix.lower()
    if ext in (".xlsx", ".xlsm"):
        return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return None


def _build_file_asset(file_path: Path) -> dict[str, Any]:
    """Build FileAsset from a real file on disk."""
    asset_id = f"asset_{uuid.uuid4().hex[:12]}"
    filename = file_path.name
    declared_mime_type = _infer_mime_type(filename)
    size_bytes = file_path.stat().st_size

    return {
        "asset_id": asset_id,
        "filename": filename,
        "declared_mime_type": declared_mime_type,
        "size_bytes": size_bytes,
        "source": "path",
    }


def _build_loop_status(packet: dict[str, Any]) -> dict[str, Any]:
    has_file = isinstance(packet.get("file_intake"), dict)
    has_questions = isinstance(packet.get("question_bundle"), dict)
    has_answer = isinstance(packet.get("owner_reentry_bridge"), dict)
    next_view = packet.get("next_owner_question")
    has_next = isinstance(next_view, dict) and next_view.get("status") == "READY"
    if not has_file:
        status = "NEEDS_FILE_EVIDENCE"
    elif has_questions and not has_answer:
        status = "NEEDS_OWNER_EVIDENCE"
    elif has_answer and has_next:
        status = "NEEDS_OWNER_EVIDENCE"
    elif has_answer:
        status = "EVIDENCE_LOOP_COMPLETE"
    else:
        status = "INTAKE_ONLY"
    return {
        "schema_version": "SERVICE_1_LOOP_STATUS_V1",
        "service_name": "SERVICE_1",
        "status": status,
        "has_file_intake": has_file,
        "has_question_bundle": has_questions,
        "has_owner_reentry_bridge": has_answer,
        "has_next_owner_question": has_next,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "delivery_authorized": False,
    }


def _build_case_record(packet: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "SERVICE_1_CASE_RECORD_V1",
        "service_name": "SERVICE_1",
        "asset": packet.get("asset"),
        "file_intake": packet.get("file_intake"),
        "question_bundle_present": isinstance(packet.get("question_bundle"), dict),
        "owner_reentry_bridge_present": isinstance(packet.get("owner_reentry_bridge"), dict),
        "next_owner_question_present": isinstance(packet.get("next_owner_question"), dict),
        "pipeline_result_present": isinstance(packet.get("pipeline_result"), dict),
        "first_aid_result_present": isinstance(packet.get("first_aid_result"), dict),
        "factory_result_present": isinstance(packet.get("factory_result"), dict),
        "runtime_authorized": False,
        "delivery_authorized": False,
    }


def _build_owner_delivery_packet(packet: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "SERVICE_1_OWNER_DELIVERY_PACKET_V1",
        "service_name": "SERVICE_1",
        "owner_message": packet.get("owner_message"),
        "next_owner_question": packet.get("next_owner_question"),
        "post_tool_owner_delivery_summary": packet.get("post_tool_owner_delivery_summary"),
        "first_aid_owner_summary": packet.get("first_aid_owner_summary"),
        "limitations": [
            "No reemplaza contador.",
            "No concluye sin evidencia suficiente.",
            "No autoriza ejecucion autonoma.",
        ],
        "runtime_authorized": False,
        "delivery_authorized": False,
    }


def _build_product_gate(packet: dict[str, Any]) -> dict[str, Any]:
    loop_status = packet.get("evidence_loop_status", {})
    has_files = isinstance(packet.get("case_delivery_manifest"), dict)
    has_tools = isinstance(packet.get("pipeline_result"), dict) or isinstance(packet.get("first_aid_result"), dict) or isinstance(packet.get("factory_result"), dict)
    if loop_status.get("status") == "NEEDS_FILE_EVIDENCE":
        status = "NEEDS_FILE_EVIDENCE"
    elif loop_status.get("status") == "NEEDS_OWNER_EVIDENCE":
        status = "NEEDS_OWNER_EVIDENCE"
    elif has_files and has_tools:
        status = "READY_FOR_OWNER_DELIVERY"
    elif has_files:
        status = "NEEDS_SCOPE_REDUCTION"
    else:
        status = "BLOCKED"
    return {
        "schema_version": "SERVICE_1_PRODUCT_GATE_V1",
        "service_name": "SERVICE_1",
        "status": status,
        "runtime_authorized": False,
        "delivery_authorized": False,
        "has_case_folder": has_files,
        "has_tool_outputs": has_tools,
        "loop_status": loop_status.get("status"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Service 1 operator CLI - minimal intake entrypoint",
    )
    parser.add_argument(
        "--file",
        required=True,
        help="Path to the file to process",
    )
    parser.add_argument(
        "--source-channel",
        default="cli",
        choices=["cli", "chat", "upload", "api", "unknown"],
        help="Source channel (default: cli)",
    )
    parser.add_argument(
        "--confirmed-columns",
        default=None,
        help="Path to confirmed_columns JSON file",
    )
    parser.add_argument(
        "--run-first-aid",
        action="store_true",
        default=False,
        help="Run minimal First Aid after intake (requires --confirmed-columns)",
    )
    parser.add_argument(
        "--run-tools",
        default=None,
        help="Path to JSON file with tool requests for the First Aid pipeline",
    )
    parser.add_argument(
        "--run-factory",
        action="store_true",
        default=False,
        help="Run Exceland factory execution (requires --template-ref)",
    )
    parser.add_argument(
        "--template-ref",
        default=None,
        help="Template ref for factory execution (e.g. precio_margen_basico_template)",
    )
    parser.add_argument(
        "--formula-ref",
        action="append",
        default=None,
        help="Formula ref for factory (repeatable, e.g. --formula-ref margen_bruto)",
    )
    parser.add_argument(
        "--factory-input",
        action="append",
        default=None,
        help="Input field as key=value for factory (repeatable, e.g. --factory-input precio_venta=120)",
    )
    parser.add_argument(
        "--factory-output",
        default=None,
        help="Output filename for factory XLSX (optional)",
    )
    parser.add_argument(
        "--question-bundle",
        default=None,
        help="Path to Service 1 question bundle JSON for owner evidence reentry",
    )
    parser.add_argument(
        "--question-ref",
        default=None,
        help="Stable question_ref answered by the owner",
    )
    parser.add_argument(
        "--owner-answer",
        default=None,
        help="Raw owner answer for the selected question_ref",
    )
    parser.add_argument(
        "--owner-reentry-storage-dir",
        default=None,
        help="Storage dir for owner evidence reentry records",
    )
    args = parser.parse_args(argv)

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: file not found: {file_path}", flush=True)
        return 2

    # Build FileAsset from real file
    asset = _build_file_asset(file_path)
    asset_id = asset["asset_id"]

    # Run the entrypoint
    packet = run_service_1_executable_entrypoint_v1(
        source_channel=args.source_channel,
        asset=asset,
    )

    # Print owner_message to stdout
    print(packet["owner_message"], flush=True)

    # If the file is XLSX, read its structure and build column confirmation packet
    _detected_structure = None
    _column_confirmation_packet = None
    if file_path.suffix.lower() in (".xlsx",):
        try:
            structure = read_service_1_xlsx_structure_v1(str(file_path))
            _detected_structure = structure

            # Print structure block to stdout
            sheet_count = structure.get("workbook", {}).get("sheet_count", 0)
            sheets = structure.get("workbook", {}).get("sheets", [])
            first_sheet_name = sheets[0]["name"] if sheets else "N/A"

            all_columns: list[str] = []
            for sheet in sheets:
                for header in sheet.get("headers", []):
                    if header and header not in all_columns:
                        all_columns.append(header)

            print()
            print("Estructura detectada", flush=True)
            print(f"- Hojas detectadas: {sheet_count}", flush=True)
            print(f"- Primera hoja: {first_sheet_name}", flush=True)
            if all_columns:
                print(
                    f"- Columnas detectadas: {', '.join(all_columns)}",
                    flush=True,
                )
            print()

            # Build column confirmation packet from detected structure
            _column_confirmation_packet = (
                build_service_1_column_confirmation_packet_v1(structure)
            )
            questions = _column_confirmation_packet.get("questions", [])
            if questions:
                print("Confirmaci\u00f3n necesaria", flush=True)
                print(
                    "- Necesito confirmar el significado de algunas columnas "
                    "antes de calcular o concluir.",
                    flush=True,
                )
                print(f"- Preguntas generadas: {len(questions)}", flush=True)
                print(f"- Primera pregunta: {questions[0]['question']}", flush=True)
                print()
        except Exception:
            _detected_structure = {
                "error": True,
                "warning": "No se pudo leer la estructura XLSX autom\u00e1ticamente; requiere revisi\u00f3n manual.",
                "runtime_authorized": False,
            }
            print()
            print(
                "No se pudo leer la estructura XLSX autom\u00e1ticamente; requiere revisi\u00f3n manual.",
                flush=True,
            )
            print()

    # Save packet JSON to .tmp/service_1_operator/<asset_id>.json (legacy)
    output_dir = Path(".tmp/service_1_operator")
    output_dir.mkdir(parents=True, exist_ok=True)

    packet_serializable: dict[str, Any] = {
        "schema_version": packet["schema_version"],
        "service_name": packet["service_name"],
        "source_channel": packet["source_channel"],
        "asset": packet["asset"],
        "file_intake": packet["file_intake"],
        "taskspec_patch": packet["taskspec_patch"],
        "owner_response": packet["owner_response"],
        "owner_message": packet["owner_message"],
        "runtime_authorized": packet["runtime_authorized"],
    }
    if _detected_structure is not None:
        packet_serializable["detected_structure"] = _detected_structure
    if _column_confirmation_packet is not None:
        packet_serializable["column_confirmation_packet"] = _column_confirmation_packet

    reentry_args = [args.question_bundle, args.question_ref, args.owner_answer]
    if any(reentry_args) and not all(reentry_args):
        print("Error: reentry requires bundle, ref and answer", flush=True)
        return 2

    if all(reentry_args):
        question_bundle_path = Path(args.question_bundle)
        if not question_bundle_path.exists():
            print(f"Error: question bundle file not found: {question_bundle_path}", flush=True)
            return 2
        try:
            with open(question_bundle_path, encoding="utf-8") as f:
                question_bundle = json.load(f)
        except json.JSONDecodeError as exc:
            print(f"Error: invalid question bundle JSON: {exc}", flush=True)
            return 2
        reentry_storage_dir = (
            Path(args.owner_reentry_storage_dir)
            if args.owner_reentry_storage_dir
            else Path(".tmp/service_1_owner_reentry")
        )
        packet_serializable.update({"question_bundle": question_bundle})
        reentry_bridge = run_service_1_owner_reentry_bridge_v1(
            question_bundle=question_bundle,
            question_ref=args.question_ref,
            raw_owner_answer=args.owner_answer,
            anamnesis_id=packet_serializable["file_intake"].get("anamnesis_id", asset_id),
            investigation_id=packet_serializable["file_intake"].get("investigation_id", asset_id),
            storage_dir=reentry_storage_dir,
            metadata={"source_channel": args.source_channel, "cli_entrypoint": "service_1_operator"},
        )
        packet_serializable["owner_reentry_bridge"] = reentry_bridge.to_dict()
        packet_serializable["next_owner_question"] = build_service_1_next_owner_question_view_v1(packet_serializable)
        print()
        print("Owner evidence reentry", flush=True)
        print(f"- Estado: {reentry_bridge.status}", flush=True)
        print(f"- Question ref: {reentry_bridge.question_ref}", flush=True)
        if reentry_bridge.selected_next_pending_question_ref:
            print(f"- Next pending: {reentry_bridge.selected_next_pending_question_ref}", flush=True)
        if reentry_bridge.blocked_reason:
            print(f"- Bloqueo: {reentry_bridge.blocked_reason}", flush=True)
        print("- Runtime autorizado: false", flush=True)
        print()

    # Load confirmed_columns if provided
    _confirmed_columns_block = None
    if args.confirmed_columns:
        cc_path = Path(args.confirmed_columns)
        if cc_path.exists():
            try:
                _confirmed_columns_block = load_confirmed_columns_v1(cc_path)
                packet_serializable["confirmed_columns"] = _confirmed_columns_block
            except Exception as exc:
                print(
                    f"Warning: could not load confirmed_columns: {exc}",
                    flush=True,
                )

    packet_serializable["evidence_loop_status"] = _build_loop_status(packet_serializable)
    packet_serializable["case_record"] = _build_case_record(packet_serializable)
    packet_serializable["owner_delivery_packet"] = _build_owner_delivery_packet(packet_serializable)

    # Write case delivery folder (before First Aid, to get manifest)
    manifest = write_service_1_case_delivery_folder_v1(packet_serializable)
    packet_serializable["case_delivery_manifest"] = manifest
    case_dir = Path(manifest["case_dir"])

    packet_serializable["product_gate"] = _build_product_gate(packet_serializable)

    # Run QA delivery gate
    qa_gate = evaluate_service_1_qa_delivery_gate_v1(packet_serializable)
    packet_serializable["qa_delivery_gate"] = qa_gate

    # Track files added after initial case folder creation
    manifest_files_written: list[str] = manifest.get("files_written", [])

    # Run pipeline tools if requested
    if args.run_tools:
        tools_path = Path(args.run_tools)
        if not tools_path.exists():
            print(f"Error: tools file not found: {tools_path}", flush=True)
            return 2

        try:
            with open(tools_path, encoding="utf-8") as f:
                tool_requests = json.load(f)
        except json.JSONDecodeError as exc:
            print(f"Error: invalid tools JSON: {exc}", flush=True)
            return 2

        if not isinstance(tool_requests, list) or not tool_requests:
            print(
                "Error: tools JSON must be a non-empty list of tool requests",
                flush=True,
            )
            return 2

        for i, req in enumerate(tool_requests):
            if not isinstance(req, dict):
                print(
                    f"Error: tool request at index {i} must be a JSON object",
                    flush=True,
                )
                return 2
            if "tool_ref" not in req:
                print(
                    f"Error: tool request at index {i} missing 'tool_ref'",
                    flush=True,
                )
                return 2
            if "inputs" not in req or not isinstance(req["inputs"], dict):
                print(
                    f"Error: tool request at index {i} missing or invalid 'inputs'",
                    flush=True,
                )
                return 2

        # Run pipeline
        pipeline_result = run_service_1_pipeline_v1(
            tool_requests=tool_requests,
            output_dir=case_dir,
        )
        packet_serializable["pipeline_result"] = pipeline_result

        # Write pipeline result to case folder
        pipeline_result_filename = "pipeline_result.json"
        (case_dir / pipeline_result_filename).write_text(
            json.dumps(pipeline_result, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        if pipeline_result_filename not in manifest_files_written:
            manifest_files_written.append(pipeline_result_filename)

        post_tool_owner_summary = render_service_1_post_tool_owner_delivery_summary_v1(
            packet_serializable
        )
        packet_serializable["post_tool_owner_delivery_summary"] = post_tool_owner_summary
        (case_dir / SUMMARY_FILENAME).write_text(
            post_tool_owner_summary,
            encoding="utf-8",
        )
        if SUMMARY_FILENAME not in manifest_files_written:
            manifest_files_written.append(SUMMARY_FILENAME)

        # Track XLSX files from delivery flow
        for delivery in pipeline_result["delivery_flow"]["deliveries"]:
            delivery_path = Path(delivery["output_path"])
            if (
                delivery_path.name not in manifest_files_written
                and delivery_path.exists()
            ):
                manifest_files_written.append(delivery_path.name)

        # Print pipeline summary
        print()
        print("Pipeline de herramientas First Aid", flush=True)
        print(
            f"- Tools ejecutadas: {', '.join(pipeline_result['executed_tool_refs'])}",
            flush=True,
        )
        print(f"- Tool count: {pipeline_result['requested_tool_count']}", flush=True)
        print("- Revisi\u00f3n humana requerida: true", flush=True)
        print("- Runtime autorizado: false", flush=True)

        for result in pipeline_result["tool_results"]:
            tool_ref = result["tool_ref"]
            status = result["status"]
            print(f"  - {tool_ref}: {status}", flush=True)
            computed = result.get("computed_results", {})
            if isinstance(computed, dict):
                for label, value in computed.items():
                    if label and value is not None:
                        print(f"    * {label}: {value}", flush=True)

        print()

    # Run Exceland factory if requested
    if args.run_factory:
        if not args.template_ref:
            print()
            print("Factor\u00eda Excel", flush=True)
            print("- Estado: BLOCKED", flush=True)
            print("- Motivo: requiere --template-ref", flush=True)
            print("- Revisi\u00f3n humana requerida: true", flush=True)
            print("- Runtime autorizado: false", flush=True)
            print()
        else:
            factory_inputs: dict[str, object] = {}
            formula_refs: list[str] = args.formula_ref or []
            raw_inputs: list[str] = args.factory_input or []
            for entry in raw_inputs:
                if "=" in entry:
                    key, _, value = entry.partition("=")
                    key = key.strip()
                    value_str = value.strip()
                    try:
                        if "." in value_str:
                            factory_inputs[key] = float(value_str)
                        else:
                            factory_inputs[key] = int(value_str)
                    except ValueError:
                        factory_inputs[key] = value_str

            bridge_input: dict[str, object] = {
                "requested_template_ref": args.template_ref,
                "requested_formula_refs": formula_refs,
                "input_fields_required": list(factory_inputs.keys()),
                "input_fields_received": factory_inputs,
                "warnings": ["Factory execution requested from operator CLI."],
                "limitations": ["Generated via exceland_execution_flow_v1; requires human review."],
            }

            factory_result = run_exceland_execution_flow_v1(
                bridge_input=bridge_input,
                output_dir=case_dir,
                output_filename=args.factory_output,
            )
            packet_serializable["factory_result"] = factory_result

            factory_result_filename = "factory_result.json"
            (case_dir / factory_result_filename).write_text(
                json.dumps(factory_result, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            if factory_result_filename not in manifest_files_written:
                manifest_files_written.append(factory_result_filename)

            if factory_result.get("output_path"):
                output_path = Path(factory_result["output_path"])
                if output_path.name not in manifest_files_written and output_path.exists():
                    manifest_files_written.append(output_path.name)

            print()
            print("Factor\u00eda Excel", flush=True)
            print(f"- Estado: {factory_result['status']}", flush=True)
            if factory_result.get("product_ref"):
                print(f"- Producto: {factory_result['product_ref']}", flush=True)
            if factory_result.get("output_path"):
                print(f"- Archivo: {factory_result['output_path']}", flush=True)
            print(f"- Artifact existe: {factory_result['artifact_exists']}", flush=True)
            print("- Revisi\u00f3n humana requerida: true", flush=True)
            print("- Runtime autorizado: false", flush=True)
            if factory_result.get("error_message"):
                print(f"- Error: {factory_result['error_message']}", flush=True)
            print()

    # Run First Aid if requested
    if args.run_first_aid:
        if _confirmed_columns_block is None:
            print()
            print("First Aid mínimo", flush=True)
            print("- Estado: BLOCKED", flush=True)
            print("- Motivo: requiere --confirmed-columns", flush=True)
            print("- Revisión humana requerida: true", flush=True)
            print("- Runtime autorizado: false", flush=True)
            print()
        else:
            # Evaluate eligibility
            eligibility_gate = evaluate_first_aid_minimal_eligibility_v1(
                packet_serializable
            )
            packet_serializable["first_aid_eligibility_gate"] = eligibility_gate

            eligibility_gate_filename = "first_aid_eligibility_gate.json"
            (case_dir / eligibility_gate_filename).write_text(
                json.dumps(eligibility_gate, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            if eligibility_gate_filename not in manifest_files_written:
                manifest_files_written.append(eligibility_gate_filename)

            if eligibility_gate["status"] == "ELIGIBLE":
                # Run First Aid
                first_aid_result = run_first_aid_minimal_v1(
                    packet_serializable, str(file_path)
                )
                packet_serializable["first_aid_result"] = first_aid_result

                # Render owner summary
                owner_summary = render_first_aid_owner_summary_v1(first_aid_result)
                packet_serializable["first_aid_owner_summary"] = owner_summary

                # Write First Aid files to case folder
                first_aid_result_filename = "first_aid_result.json"
                (case_dir / first_aid_result_filename).write_text(
                    json.dumps(first_aid_result, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
                if first_aid_result_filename not in manifest_files_written:
                    manifest_files_written.append(first_aid_result_filename)

                first_aid_owner_summary_filename = "first_aid_owner_summary.md"
                (case_dir / first_aid_owner_summary_filename).write_text(
                    owner_summary,
                    encoding="utf-8",
                )
                if first_aid_owner_summary_filename not in manifest_files_written:
                    manifest_files_written.append(first_aid_owner_summary_filename)

                # Print First Aid summary to stdout
                print()
                print("First Aid mínimo", flush=True)
                print(f"- Estado: {first_aid_result['status']}", flush=True)
                print("- Revisión humana requerida: true", flush=True)
                print("- Runtime autorizado: false", flush=True)

                summary = first_aid_result.get("summary", {})
                print(
                    f"- Hojas perfiladas: {summary.get('sheets_profiled', 0)}",
                    flush=True,
                )
                print(
                    f"- Findings generados: {summary.get('total_findings', 0)}",
                    flush=True,
                )
                print()
            else:
                # BLOCKED
                print()
                print("First Aid mínimo", flush=True)
                print("- Estado: BLOCKED", flush=True)
                blockers_str = ", ".join(eligibility_gate.get("blockers", []))
                if blockers_str:
                    print(f"- Motivos: {blockers_str}", flush=True)
                print("- Revisión humana requerida: true", flush=True)
                print("- Runtime autorizado: false", flush=True)
                print()

    # Build explicit human review gate before the final operator packet is written.
    human_review_gate = build_service_1_human_review_gate_v1(packet_serializable)
    packet_serializable["human_review_gate"] = human_review_gate

    # Write operator_packet.json to case folder
    operator_packet_path = case_dir / "operator_packet.json"
    operator_packet_path.write_text(
        json.dumps(packet_serializable, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    if "operator_packet.json" not in manifest_files_written:
        manifest_files_written.append("operator_packet.json")

    final_delivery_manifest = finalize_service_1_case_delivery_folder_v1(
        packet=packet_serializable,
        case_dir=case_dir,
        files_written=manifest_files_written,
    )
    packet_serializable["final_delivery_manifest"] = final_delivery_manifest

    # Print QA delivery gate summary to stdout
    print()
    print("QA delivery gate", flush=True)
    print(f"- Estado: {qa_gate['status']}", flush=True)
    print(f"- Checks: {qa_gate['checks_passed']}/{qa_gate['checks_total']}", flush=True)
    print("- Runtime autorizado: false", flush=True)
    if qa_gate["status"] == "BLOCKED":
        print()
        print("El caso queda bloqueado para entrega hasta revisión humana.", flush=True)
    print()

    # Print case delivery summary to stdout
    print()
    print("Carpeta de caso", flush=True)
    print(f"- Caso: {manifest['case_id']}", flush=True)
    print(f"- Archivos generados: {len(manifest_files_written)}", flush=True)
    print(f"- Ubicaci\u00f3n: {manifest['case_dir']}", flush=True)
    print("- Ruta canónica de entrega: true", flush=True)
    print(
        f"- QA final: {final_delivery_manifest['final_qa_delivery_gate']['status']}",
        flush=True,
    )
    print(
        f"- Human review gate: {final_delivery_manifest['human_review_gate']['status']}",
        flush=True,
    )
    print()

    # Legacy JSON output for backward compatibility
    legacy_path = output_dir / f"{asset_id}.json"
    legacy_path.write_text(
        json.dumps(packet_serializable, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
