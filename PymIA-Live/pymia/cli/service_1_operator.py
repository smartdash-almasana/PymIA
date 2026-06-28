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

    # Write case delivery folder (before First Aid, to get manifest)
    manifest = write_service_1_case_delivery_folder_v1(packet_serializable)
    packet_serializable["case_delivery_manifest"] = manifest
    case_dir = Path(manifest["case_dir"])

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

    # Write operator_packet.json to case folder
    operator_packet_path = case_dir / "operator_packet.json"
    operator_packet_path.write_text(
        json.dumps(packet_serializable, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

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
    print(f"- Archivos generados: {len(manifest['files_written'])}", flush=True)
    print(f"- Ubicaci\u00f3n: {manifest['case_dir']}", flush=True)
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
