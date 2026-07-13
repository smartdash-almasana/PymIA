from __future__ import annotations

from pymia.contracts.column_confirmation_v1 import (
    CalculationRelevance,
    ColumnConfirmationEntry,
    ColumnConfirmationMatrix,
    ConfirmationStatus,
)
from pymia.smartpyme.service_1_evidence_profile_to_candidate_tools_contract_v1 import (
    BLOCKED,
    CANDIDATE_TOOLS_READY,
    NEEDS_EVIDENCE,
    NO_CANDIDATE_TOOLS,
    build_service_1_evidence_profile_to_candidate_tools_v1,
)
from pymia.smartpyme.service_1_owner_rectified_evidence_profile_v1 import (
    build_service_1_owner_rectified_evidence_profile_v1,
)


def _entry(header: str, function: str, *, sheet: str = "Ventas") -> ColumnConfirmationEntry:
    return ColumnConfirmationEntry(
        original_column_name=header,
        sheet_name=sheet,
        suggested_semantic_role="unknown",
        calculation_relevance=CalculationRelevance.INFORMATIONAL,
        owner_confirmed_role=function,
        owner_rectified_function=function,
        confirmation_status=ConfirmationStatus.CONFIRMED,
    )


def _evidence_profile(entries: list[ColumnConfirmationEntry]):
    return build_service_1_owner_rectified_evidence_profile_v1(
        matrix=ColumnConfirmationMatrix(file_name="pyme.xlsx", entries=entries),
        case_ref="CASE-TOOLS-001",
    )


def test_margin_signal_maps_to_precio_margen_candidate_without_execution() -> None:
    profile = _evidence_profile([
        _entry("Producto", "producto"),
        _entry("Precio", "precio_venta"),
        _entry("Costo", "costo_unitario"),
    ])

    result = build_service_1_evidence_profile_to_candidate_tools_v1(evidence_profile=profile)

    assert result.status == CANDIDATE_TOOLS_READY
    assert result.candidate_tool_refs == ("precio_margen_basico",)
    assert result.candidate_tools[0].source_signal_name == "margen_basico"
    assert result.candidate_tools[0].runtime_authorized is False
    assert result.candidate_tools[0].tool_execution_authorized is False
    assert result.candidate_tools[0].executable_tool_request_authorized is False
    assert result.runtime_authorized is False
    assert result.tool_execution_authorized is False
    assert result.executable_tool_requests_authorized is False


def test_stock_signal_maps_to_stock_candidate() -> None:
    profile = _evidence_profile([
        _entry("SKU", "sku"),
        _entry("Stock", "stock"),
    ])

    result = build_service_1_evidence_profile_to_candidate_tools_v1(evidence_profile=profile)

    assert result.status == CANDIDATE_TOOLS_READY
    assert result.candidate_tool_refs == ("stock_alertas_basicas",)
    assert result.candidate_tools[0].source_headers == ("SKU", "Stock")


def test_sales_collection_signal_maps_to_caja_candidate() -> None:
    profile = _evidence_profile([
        _entry("Fecha", "fecha"),
        _entry("Venta", "venta_total"),
        _entry("Cobro", "cobro"),
    ])

    result = build_service_1_evidence_profile_to_candidate_tools_v1(evidence_profile=profile)

    assert result.status == CANDIDATE_TOOLS_READY
    assert result.candidate_tool_refs == ("caja_diaria_triage",)
    assert result.candidate_tools[0].source_signal_name == "ventas_cobros_basico"


def test_multiple_ready_signals_build_sorted_candidates() -> None:
    profile = _evidence_profile([
        _entry("Producto", "producto"),
        _entry("Precio", "precio_venta"),
        _entry("Costo", "costo_unitario"),
        _entry("Stock", "stock"),
        _entry("Fecha", "fecha"),
        _entry("Cobro", "cobro"),
    ])

    result = build_service_1_evidence_profile_to_candidate_tools_v1(evidence_profile=profile)

    assert result.status == CANDIDATE_TOOLS_READY
    assert result.candidate_tool_refs == (
        "caja_diaria_triage",
        "precio_margen_basico",
        "stock_alertas_basicas",
    )


def test_incomplete_evidence_profile_returns_needs_evidence() -> None:
    profile = _evidence_profile([
        _entry("Producto", "producto"),
        _entry("Precio", "precio_venta"),
    ])

    result = build_service_1_evidence_profile_to_candidate_tools_v1(evidence_profile=profile)

    assert result.status == NEEDS_EVIDENCE
    assert result.candidate_tools == ()
    assert "margen_basico:cost_function" in result.missing_requirements
    assert result.tool_execution_authorized is False


def test_upstream_blockers_block_candidate_tools() -> None:
    matrix = ColumnConfirmationMatrix(
        file_name="pyme.xlsx",
        entries=[
            ColumnConfirmationEntry(
                original_column_name="Precio",
                sheet_name="Ventas",
                suggested_semantic_role="precio_venta",
                calculation_relevance=CalculationRelevance.VENTAS,
                confirmation_status=ConfirmationStatus.PENDING_OWNER_CONFIRMATION,
            )
        ],
    )
    profile = build_service_1_owner_rectified_evidence_profile_v1(matrix=matrix, case_ref="CASE-BLOCKED")

    result = build_service_1_evidence_profile_to_candidate_tools_v1(evidence_profile=profile)

    assert result.status == BLOCKED
    assert "NO_OWNER_RECTIFIED_FUNCTIONS" in result.blockers
    assert "UNRECTIFIED_SEMANTIC_FUNCTION:Ventas.Precio" in result.blockers
    assert result.candidate_tools == ()


def test_explicit_allowlist_blocks_non_allowed_candidate() -> None:
    profile = _evidence_profile([
        _entry("Producto", "producto"),
        _entry("Precio", "precio_venta"),
        _entry("Costo", "costo_unitario"),
    ])

    result = build_service_1_evidence_profile_to_candidate_tools_v1(
        evidence_profile=profile,
        allowed_tool_refs=("stock_alertas_basicas",),
    )

    assert result.status == BLOCKED
    assert result.candidate_tools == ()
    assert result.blockers == ("TOOL_REF_NOT_IN_EXPLICIT_ALLOWLIST:precio_margen_basico",)


def test_confirmed_but_unmapped_evidence_returns_no_candidate_tools() -> None:
    profile = _evidence_profile([
        _entry("Producto", "producto"),
    ])

    # Force the profile into a ready-but-unmapped shape without changing production code.
    object.__setattr__(profile, "evidence_ready", True)
    object.__setattr__(profile, "missing_requirements", ())
    object.__setattr__(profile, "blockers", ())
    object.__setattr__(profile, "evidence_signals", ())

    result = build_service_1_evidence_profile_to_candidate_tools_v1(evidence_profile=profile)

    assert result.status == NO_CANDIDATE_TOOLS
    assert result.candidate_tools == ()
    assert result.candidate_tool_refs == ()


def test_candidate_tools_output_is_deterministic() -> None:
    entries = [
        _entry("Costo", "costo_unitario"),
        _entry("Producto", "producto"),
        _entry("Precio", "precio_venta"),
    ]

    first_profile = _evidence_profile(entries)
    second_profile = _evidence_profile(list(reversed(entries)))

    first = build_service_1_evidence_profile_to_candidate_tools_v1(
        evidence_profile=first_profile,
        allowed_tool_refs=["precio_margen_basico", "precio_margen_basico"],
    ).to_dict()
    second = build_service_1_evidence_profile_to_candidate_tools_v1(
        evidence_profile=second_profile,
        allowed_tool_refs=["precio_margen_basico"],
    ).to_dict()

    assert first == second
