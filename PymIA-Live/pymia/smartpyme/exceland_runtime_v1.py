from __future__ import annotations

from pathlib import Path
from typing import Final, Literal, TypedDict

from exceland_factory.factory import build_product

_EXCELAND_PRODUCT_REFS: Final[tuple[str, ...]] = (
    "caja_diaria",
    "precio_margen",
    "stock_control",
    "costos_por_producto",
    "flujo_de_fondos",
    "rentabilidad_por_producto",
)

ExcelandRuntimeStatus = Literal[
    "OK",
    "MISSING_PRODUCT_REF",
    "UNKNOWN_PRODUCT",
    "FACTORY_ERROR",
    "INVALID_OUTPUT_DIR",
]


class ExcelandRuntimeV1(TypedDict):
    status: ExcelandRuntimeStatus
    product_ref: str | None
    output_path: str | None
    artifact_exists: bool
    error_message: str | None
    runtime_authorized: Literal[False]
    notes: list[str]


def run_exceland_runtime_v1(
    *,
    product_ref: str | None,
    output_dir: str | Path,
    output_filename: str | None = None,
) -> ExcelandRuntimeV1:
    """Run a controlled exceland factory product generation.

    This is the thin runtime adapter between PymIA-Live and exceland_factory.
    It validates the product reference, ensures the output directory exists,
    invokes build_product, and returns a typed, fail-closed result.

    This adapter does NOT:
      - validate formulas or template contracts (that's the bridge's job)
      - deliver to the owner (that's the delivery flow's job)
      - route from the pipeline (future concern)
    """
    if not product_ref:
        return {
            "status": "MISSING_PRODUCT_REF",
            "product_ref": None,
            "output_path": None,
            "artifact_exists": False,
            "error_message": "product_ref is required and must be a non-empty string",
            "runtime_authorized": False,
            "notes": ["exceland_runtime_v1 requires an explicit product_ref."],
        }

    if product_ref not in _EXCELAND_PRODUCT_REFS:
        return {
            "status": "UNKNOWN_PRODUCT",
            "product_ref": product_ref,
            "output_path": None,
            "artifact_exists": False,
            "error_message": (
                f"Product ref '{product_ref}' is not in the exceland runtime allowlist. "
                f"Allowed: {', '.join(_EXCELAND_PRODUCT_REFS)}."
            ),
            "runtime_authorized": False,
            "notes": [
                "exceland_runtime_v1 only executes explicitly allowlisted products.",
            ],
        }

    output_path = Path(output_dir)
    if not output_path.exists():
        return {
            "status": "INVALID_OUTPUT_DIR",
            "product_ref": product_ref,
            "output_path": None,
            "artifact_exists": False,
            "error_message": f"Output directory does not exist: {output_path}",
            "runtime_authorized": False,
            "notes": [
                "Output directory must exist before calling the runtime adapter.",
            ],
        }

    safe_filename = output_filename or f"{product_ref}.xlsx"
    if not safe_filename.endswith(".xlsx"):
        safe_filename = f"{safe_filename}.xlsx"
    artifact_path = output_path / safe_filename

    try:
        build_product(product_ref, output_path=artifact_path)
    except Exception as exc:
        return {
            "status": "FACTORY_ERROR",
            "product_ref": product_ref,
            "output_path": None,
            "artifact_exists": False,
            "error_message": str(exc),
            "runtime_authorized": False,
            "notes": [
                "exceland_factory.build_product raised an exception.",
                f"Product ref: {product_ref}",
            ],
        }

    artifact_exists = artifact_path.exists()

    if not artifact_exists:
        return {
            "status": "FACTORY_ERROR",
            "product_ref": product_ref,
            "output_path": str(artifact_path.resolve()),
            "artifact_exists": False,
            "error_message": (
                "exceland_factory.build_product returned without error "
                "but no artifact was created at the expected path."
            ),
            "runtime_authorized": False,
            "notes": [
                f"Expected artifact: {artifact_path}",
            ],
        }

    return {
        "status": "OK",
        "product_ref": product_ref,
        "output_path": str(artifact_path.resolve()),
        "artifact_exists": True,
        "error_message": None,
        "runtime_authorized": False,
        "notes": [
            f"exceland_runtime_v1 generated XLSX for product '{product_ref}'.",
            "No formulas were executed inside PymIA-Live; generation was delegated to exceland_factory.",
        ],
    }
