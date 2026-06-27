from __future__ import annotations

from pathlib import Path
from typing import Final, Literal, TypedDict

from pymia.smartpyme.exceland_bridge_v1 import (
    ExcelandBridgeInputV1,
    build_exceland_bridge_v1,
)
from pymia.smartpyme.exceland_runtime_v1 import (
    run_exceland_runtime_v1,
)

_BRIDGE_TEMPLATE_TO_PRODUCT: Final[dict[str, str]] = {
    "precio_margen_basico_template": "precio_margen",
    "caja_diaria_template": "caja_diaria",
    "stock_alertas_basicas_template": "stock_control",
}

ExcelandExecutionFlowStatus = Literal[
    "OK",
    "BRIDGE_NOT_OK",
    "TEMPLATE_NOT_MAPPED",
    "RUNTIME_ERROR",
    "INVALID_INPUT",
]


class ExcelandExecutionFlowV1(TypedDict):
    status: ExcelandExecutionFlowStatus
    bridge_status: str
    runtime_status: str | None
    requested_template_ref: str | None
    product_ref: str | None
    output_path: str | None
    artifact_exists: bool
    error_message: str | None
    runtime_authorized: Literal[False]
    notes: list[str]


def run_exceland_execution_flow_v1(
    *,
    bridge_input: ExcelandBridgeInputV1,
    output_dir: str | Path,
    output_filename: str | None = None,
) -> ExcelandExecutionFlowV1:
    """Wire the exceland bridge (contract validation) to the runtime adapter (physical generation).

    Flow:
      1. Validate inputs via bridge (contract layer)
      2. If bridge is not OK → fail closed
      3. Map bridge template_ref → exceland product_ref
      4. If no mapping → fail closed
      5. Execute runtime adapter (physical generation)
      6. Return combined typed result

    This flow does NOT:
      - route from the pipeline
      - deliver to the owner
      - use the generic XLSX delivery layer
    """
    output_path = Path(output_dir)
    if not isinstance(bridge_input, dict):
        return {
            "status": "INVALID_INPUT",
            "bridge_status": "INVALID_INPUT",
            "runtime_status": None,
            "requested_template_ref": None,
            "product_ref": None,
            "output_path": None,
            "artifact_exists": False,
            "error_message": "bridge_input must be a dict (ExcelandBridgeInputV1)",
            "runtime_authorized": False,
            "notes": [],
        }

    bridge_result = build_exceland_bridge_v1(bridge_input=bridge_input)

    if bridge_result["status"] != "OK":
        return {
            "status": "BRIDGE_NOT_OK",
            "bridge_status": bridge_result["status"],
            "runtime_status": None,
            "requested_template_ref": bridge_result["requested_template_ref"],
            "product_ref": None,
            "output_path": None,
            "artifact_exists": False,
            "error_message": (
                f"Bridge validation failed with status '{bridge_result['status']}'. "
                f"{bridge_result.get('owner_summary', '')}"
            ),
            "runtime_authorized": False,
            "notes": [
                "exceland_execution_flow_v1: bridge rejected the request.",
            ],
        }

    requested_template_ref = bridge_result["requested_template_ref"]
    if not requested_template_ref:
        return {
            "status": "TEMPLATE_NOT_MAPPED",
            "bridge_status": bridge_result["status"],
            "runtime_status": None,
            "requested_template_ref": None,
            "product_ref": None,
            "output_path": None,
            "artifact_exists": False,
            "error_message": "Bridge returned OK but requested_template_ref is None.",
            "runtime_authorized": False,
            "notes": [
                "Bridge validated the request but no template_ref was present.",
            ],
        }

    product_ref = _BRIDGE_TEMPLATE_TO_PRODUCT.get(requested_template_ref)
    if product_ref is None:
        return {
            "status": "TEMPLATE_NOT_MAPPED",
            "bridge_status": bridge_result["status"],
            "runtime_status": None,
            "requested_template_ref": requested_template_ref,
            "product_ref": None,
            "output_path": None,
            "artifact_exists": False,
            "error_message": (
                f"Bridge template '{requested_template_ref}' has no mapped exceland product_ref. "
                f"Mapped templates: {', '.join(_BRIDGE_TEMPLATE_TO_PRODUCT)}."
            ),
            "runtime_authorized": False,
            "notes": [
                "exceland_execution_flow_v1: template_ref exists but no product mapping.",
            ],
        }

    runtime_result = run_exceland_runtime_v1(
        product_ref=product_ref,
        output_dir=output_dir,
        output_filename=output_filename,
    )

    if runtime_result["status"] != "OK":
        return {
            "status": "RUNTIME_ERROR",
            "bridge_status": bridge_result["status"],
            "runtime_status": runtime_result["status"],
            "requested_template_ref": requested_template_ref,
            "product_ref": product_ref,
            "output_path": runtime_result.get("output_path"),
            "artifact_exists": runtime_result["artifact_exists"],
            "error_message": (
                f"Runtime execution failed for product '{product_ref}': "
                f"{runtime_result.get('error_message', 'unknown error')}"
            ),
            "runtime_authorized": False,
            "notes": [
                f"exceland_execution_flow_v1: bridge passed but runtime failed for {product_ref}.",
            ],
        }

    return {
        "status": "OK",
        "bridge_status": bridge_result["status"],
        "runtime_status": runtime_result["status"],
        "requested_template_ref": requested_template_ref,
        "product_ref": product_ref,
        "output_path": runtime_result["output_path"],
        "artifact_exists": runtime_result["artifact_exists"],
        "error_message": None,
        "runtime_authorized": False,
        "notes": [
            f"exceland_execution_flow_v1: bridge → mapping → runtime completed for '{requested_template_ref}' → '{product_ref}'.",
            "No formulas executed inside PymIA-Live; generation delegated to exceland_factory.",
        ],
    }
