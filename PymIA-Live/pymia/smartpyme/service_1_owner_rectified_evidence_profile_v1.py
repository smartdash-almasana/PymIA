from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from pymia.contracts.column_confirmation_v1 import (
    ColumnConfirmationEntry,
    ColumnConfirmationMatrix,
    ConfirmationStatus,
    SemanticRectificationStatus,
    infer_calculation_relevance,
)

SCHEMA_VERSION = "SERVICE_1_OWNER_RECTIFIED_EVIDENCE_PROFILE_CONTRACT_V1"
SERVICE_NAME = "SERVICE_1"

MARGIN_SIGNAL = "margen_basico"
STOCK_SIGNAL = "stock_basico"
SALES_COLLECTION_SIGNAL = "ventas_cobros_basico"

SALE_FUNCTIONS = frozenset({"venta_total", "precio_venta"})
COST_FUNCTIONS = frozenset({"costo_unitario", "costo_total"})
PRODUCT_FUNCTIONS = frozenset({"producto", "sku"})
QUANTITY_FUNCTIONS = frozenset({"cantidad"})
STOCK_FUNCTIONS = frozenset({"stock", "stock_final"})
PAYMENT_FUNCTIONS = frozenset({"cobro", "pago", "ingreso", "saldo"})
DATE_FUNCTIONS = frozenset({"fecha"})


@dataclass(frozen=True)
class OwnerRectifiedEvidenceColumnV1:
    raw_header: str
    sheet_name: str
    pymia_inferred_function: str
    owner_rectified_function: str
    calculation_relevance: str


@dataclass(frozen=True)
class OwnerRectifiedEvidenceSignalV1:
    signal_name: str
    evidence_ready: bool
    present_functions: tuple[str, ...]
    missing_requirements: tuple[str, ...]
    source_headers: tuple[str, ...]
    allowed_next_steps: tuple[str, ...]


@dataclass(frozen=True)
class Service1OwnerRectifiedEvidenceProfileResultV1:
    schema_version: str
    service_name: str
    case_ref: str
    source_file_name: str
    source_columns: tuple[OwnerRectifiedEvidenceColumnV1, ...]
    evidence_signals: tuple[OwnerRectifiedEvidenceSignalV1, ...]
    evidence_ready: bool
    missing_requirements: tuple[str, ...]
    blockers: tuple[str, ...]
    allowed_next_steps: tuple[str, ...]
    runtime_authorized: bool
    tool_execution_authorized: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _optional_text(value: str | None) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _is_owner_rectified(entry: ColumnConfirmationEntry) -> bool:
    return (
        entry.confirmation_status == ConfirmationStatus.CONFIRMED
        and isinstance(entry.owner_rectified_function, str)
        and bool(entry.owner_rectified_function.strip())
    )


def _column_from_entry(entry: ColumnConfirmationEntry) -> OwnerRectifiedEvidenceColumnV1:
    owner_function = str(entry.owner_rectified_function or "").strip()
    return OwnerRectifiedEvidenceColumnV1(
        raw_header=entry.original_column_name,
        sheet_name=entry.sheet_name,
        pymia_inferred_function=entry.suggested_semantic_role,
        owner_rectified_function=owner_function,
        calculation_relevance=infer_calculation_relevance(owner_function).value,
    )


def _headers_for(functions: set[str], columns: tuple[OwnerRectifiedEvidenceColumnV1, ...]) -> tuple[str, ...]:
    headers = [
        column.raw_header
        for column in columns
        if column.owner_rectified_function in functions
    ]
    return tuple(sorted(dict.fromkeys(headers)))


def _present(functions: set[str], owner_functions: set[str]) -> tuple[str, ...]:
    return tuple(sorted(functions & owner_functions))


def _build_signal(
    *,
    signal_name: str,
    required_groups: dict[str, frozenset[str]],
    owner_functions: set[str],
    columns: tuple[OwnerRectifiedEvidenceColumnV1, ...],
    allowed_next_step_when_ready: str,
) -> OwnerRectifiedEvidenceSignalV1:
    missing = []
    present_flat: set[str] = set()
    source_function_set: set[str] = set()

    for requirement_name, acceptable_functions in required_groups.items():
        group_present = set(acceptable_functions) & owner_functions
        if group_present:
            present_flat.update(group_present)
            source_function_set.update(group_present)
            continue
        missing.append(requirement_name)

    evidence_ready = not missing
    allowed_next_steps = (allowed_next_step_when_ready,) if evidence_ready else ()

    return OwnerRectifiedEvidenceSignalV1(
        signal_name=signal_name,
        evidence_ready=evidence_ready,
        present_functions=tuple(sorted(present_flat)),
        missing_requirements=tuple(missing),
        source_headers=_headers_for(source_function_set, columns),
        allowed_next_steps=allowed_next_steps,
    )


def _unrectified_blockers(matrix: ColumnConfirmationMatrix) -> tuple[str, ...]:
    blockers: list[str] = []
    for entry in matrix.entries:
        if _is_owner_rectified(entry):
            continue
        if entry.confirmation_status in {
            ConfirmationStatus.PENDING_OWNER_CONFIRMATION,
            ConfirmationStatus.BLOCKED_AMBIGUOUS,
        } and entry.suggested_semantic_role != "unknown":
            blockers.append(
                f"UNRECTIFIED_SEMANTIC_FUNCTION:{entry.sheet_name}.{entry.original_column_name}"
            )
        if (
            entry.semantic_rectification_status
            == SemanticRectificationStatus.BLOCKED_UNNORMALIZABLE_OWNER_RESPONSE
        ):
            blockers.append(
                f"BLOCKED_UNNORMALIZABLE_OWNER_RESPONSE:{entry.sheet_name}.{entry.original_column_name}"
            )
        if entry.semantic_rectification_status == SemanticRectificationStatus.OWNER_REJECTED:
            blockers.append(f"OWNER_REJECTED:{entry.sheet_name}.{entry.original_column_name}")
    return tuple(sorted(dict.fromkeys(blockers)))


def build_service_1_owner_rectified_evidence_profile_v1(
    *,
    matrix: ColumnConfirmationMatrix,
    case_ref: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> Service1OwnerRectifiedEvidenceProfileResultV1:
    if not isinstance(matrix, ColumnConfirmationMatrix):
        raise ValueError("matrix must be a ColumnConfirmationMatrix")
    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("metadata must be a dict or None")

    source_columns = tuple(
        sorted(
            (_column_from_entry(entry) for entry in matrix.entries if _is_owner_rectified(entry)),
            key=lambda column: (column.sheet_name, column.raw_header, column.owner_rectified_function),
        )
    )
    owner_functions = {column.owner_rectified_function for column in source_columns}

    # Build explicitly to keep every signal deterministic and readable.
    margin_signal = _build_signal(
        signal_name=MARGIN_SIGNAL,
        required_groups={
            "product_function": PRODUCT_FUNCTIONS,
            "sale_function": SALE_FUNCTIONS,
            "cost_function": COST_FUNCTIONS,
        },
        owner_functions=owner_functions,
        columns=source_columns,
        allowed_next_step_when_ready="MARGIN_EVIDENCE_REVIEW",
    )
    stock_signal = _build_signal(
        signal_name=STOCK_SIGNAL,
        required_groups={
            "product_function": PRODUCT_FUNCTIONS,
            "stock_function": STOCK_FUNCTIONS,
        },
        owner_functions=owner_functions,
        columns=source_columns,
        allowed_next_step_when_ready="STOCK_EVIDENCE_REVIEW",
    )
    sales_collection_signal = _build_signal(
        signal_name=SALES_COLLECTION_SIGNAL,
        required_groups={
            "date_function": DATE_FUNCTIONS,
            "sale_function": SALE_FUNCTIONS,
            "payment_function": PAYMENT_FUNCTIONS,
        },
        owner_functions=owner_functions,
        columns=source_columns,
        allowed_next_step_when_ready="SALES_COLLECTION_EVIDENCE_REVIEW",
    )
    signals = (margin_signal, stock_signal, sales_collection_signal)

    signal_missing_requirements = tuple(
        sorted(
            dict.fromkeys(
                f"{signal.signal_name}:{requirement}"
                for signal in signals
                for requirement in signal.missing_requirements
            )
        )
    )

    blockers = list(_unrectified_blockers(matrix))
    if not source_columns:
        blockers.append("NO_OWNER_RECTIFIED_FUNCTIONS")

    ready_signals = tuple(signal for signal in signals if signal.evidence_ready)
    allowed_next_steps = tuple(
        sorted(
            dict.fromkeys(
                step
                for signal in ready_signals
                for step in signal.allowed_next_steps
            )
        )
    )

    return Service1OwnerRectifiedEvidenceProfileResultV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        case_ref=_optional_text(case_ref),
        source_file_name=matrix.file_name,
        source_columns=source_columns,
        evidence_signals=signals,
        evidence_ready=bool(ready_signals) and not blockers,
        missing_requirements=signal_missing_requirements,
        blockers=tuple(sorted(dict.fromkeys(blockers))),
        allowed_next_steps=allowed_next_steps,
        runtime_authorized=False,
        tool_execution_authorized=False,
        metadata=dict(metadata or {}),
    )


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "MARGIN_SIGNAL",
    "STOCK_SIGNAL",
    "SALES_COLLECTION_SIGNAL",
    "OwnerRectifiedEvidenceColumnV1",
    "OwnerRectifiedEvidenceSignalV1",
    "Service1OwnerRectifiedEvidenceProfileResultV1",
    "build_service_1_owner_rectified_evidence_profile_v1",
]
