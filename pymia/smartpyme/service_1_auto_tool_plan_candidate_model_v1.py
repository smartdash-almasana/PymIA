from __future__ import annotations

from typing import Final, Literal, TypedDict

SCHEMA_VERSION: Final[str] = "S1_AUTO_TOOL_PLAN_CANDIDATE_MODEL_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"
READY_FOR_TOOL_PLANNING: Final[str] = "READY_FOR_TOOL_PLANNING"
SUPPORTED_FAMILY_FIRST_AID: Final[str] = "FIRST_AID"

ToolPlanCandidateStatusV1 = Literal[
    "TOOL_PLAN_CANDIDATE_READY",
    "NEEDS_OWNER_INPUT",
    "NEEDS_EVIDENCE",
    "BLOCKED",
    "UNKNOWN",
]

CandidateToolRefV1 = Literal[
    "precio_margen_basico",
    "caja_diaria_triage",
    "stock_alertas_basicas",
    "gastos_triage",
    "proveedores_precio_variacion_triage",
]

_ALLOWED_CANDIDATE_TOOL_REFS: Final[tuple[str, ...]] = (
    "precio_margen_basico",
    "caja_diaria_triage",
    "stock_alertas_basicas",
    "gastos_triage",
    "proveedores_precio_variacion_triage",
)

_REQUIRED_EVIDENCE_BY_TOOL: Final[dict[str, tuple[str, ...]]] = {
    "precio_margen_basico": ("precio_venta", "costo_unitario"),
    "caja_diaria_triage": ("saldo_inicial", "ingresos", "egresos"),
    "stock_alertas_basicas": ("producto", "stock_actual", "stock_minimo", "ventas_diarias_promedio"),
    "gastos_triage": ("concepto", "importe"),
    "proveedores_precio_variacion_triage": ("proveedor", "producto_o_insumo", "precio_o_costo"),
}

_OWNER_AXIS_TOOL_MAP: Final[tuple[tuple[tuple[str, ...], str], ...]] = (
    (("precio_margen", "margen", "costos", "precios"), "precio_margen_basico"),
    (("caja", "cash", "caja_diaria"), "caja_diaria_triage"),
    (("stock", "inventario"), "stock_alertas_basicas"),
    (("gastos", "egresos"), "gastos_triage"),
    (("proveedores", "precios_proveedores"), "proveedores_precio_variacion_triage"),
)

_LIMITATIONS_BY_TOOL: Final[dict[str, tuple[str, ...]]] = {
    "precio_margen_basico": ("Planifica cálculo básico por referencia; no confirma rentabilidad real ni precio definitivo.",),
    "caja_diaria_triage": ("Planifica triage de caja diaria; no certifica saldo ni conciliación bancaria.",),
    "stock_alertas_basicas": ("Planifica alertas básicas de stock; no confirma stock físico ni causa del desvío.",),
    "gastos_triage": ("Planifica agrupación básica de gastos; no clasifica contable ni fiscalmente.",),
    "proveedores_precio_variacion_triage": ("Planifica revisión básica de variaciones; no decide estrategia de compras.",),
}

_OWNER_QUESTIONS_BY_TOOL: Final[dict[str, tuple[str, ...]]] = {
    "precio_margen_basico": ("Confirmá las referencias de precio de venta y costo unitario antes de planificar el cálculo.",),
    "caja_diaria_triage": ("Confirmá las referencias de saldo inicial, ingresos y egresos antes de planificar el triage.",),
    "stock_alertas_basicas": ("Confirmá las referencias de producto, stock actual, stock mínimo y ventas diarias promedio.",),
    "gastos_triage": ("Confirmá las referencias de concepto e importe antes de planificar el triage de gastos.",),
    "proveedores_precio_variacion_triage": ("Confirmá las referencias de proveedor, producto o insumo y precio o costo.",),
}


class Service1AutoToolPlanCandidateInputV1(TypedDict):
    case_truth_status: str
    supported_family: str | None
    owner_axis: str | None
    owner_problem: str | None
    evidence_refs: dict[str, str]
    confirmed_column_refs: list[str]
    ambiguous_column_refs: list[str]
    allowed_tool_refs: list[str]


class Service1ToolPlanCandidateV1(TypedDict):
    tool_ref: str
    reason: str
    input_mapping_refs: dict[str, str]
    missing_inputs: list[str]
    limitations: list[str]


class Service1AutoToolPlanCandidateResultV1(TypedDict):
    schema_version: str
    service_name: str
    status: ToolPlanCandidateStatusV1
    candidate_tool_refs: list[str]
    tool_plan_candidate: list[Service1ToolPlanCandidateV1]
    missing_evidence_refs: list[str]
    owner_questions: list[str]
    blocked_reason: str | None
    runtime_authorized: Literal[False]
    execution_authorized: Literal[False]
    tool_requests_authorized: Literal[False]
    autonomous_delivery_authorized: Literal[False]
    notes: list[str]


def build_service_1_auto_tool_plan_candidate_v1(
    plan_input: Service1AutoToolPlanCandidateInputV1,
) -> Service1AutoToolPlanCandidateResultV1:
    """Build a governed First Aid tool plan candidate from confirmed evidence refs only.

    This model is pure. It does not read files, execute tools, build executable
    tool requests, call pipelines, call model runtimes, persist state, or authorize delivery.
    """
    case_truth_status = str(plan_input.get("case_truth_status") or "")
    if case_truth_status != READY_FOR_TOOL_PLANNING:
        return _result(
            status="BLOCKED",
            blocked_reason="case_truth_status_not_ready_for_tool_planning",
            notes=["Tool plan candidates require TruthIntegration READY_FOR_TOOL_PLANNING."],
        )

    supported_family = plan_input.get("supported_family")
    if supported_family != SUPPORTED_FAMILY_FIRST_AID:
        return _result(
            status="BLOCKED",
            blocked_reason="supported_family_not_first_aid",
            notes=["S1_AUTO_TOOL_PLAN_CANDIDATE_MODEL_V1 supports FIRST_AID only."],
        )

    candidate_tool_ref = _match_candidate_tool_ref(
        owner_axis=plan_input.get("owner_axis"),
        owner_problem=plan_input.get("owner_problem"),
    )
    if candidate_tool_ref is None:
        return _result(
            status="UNKNOWN",
            blocked_reason=None,
            notes=["No clear V1 owner_axis match. Refusing to infer a tool candidate aggressively."],
        )

    allowed_tool_refs = set(str(ref) for ref in plan_input.get("allowed_tool_refs", []))
    if candidate_tool_ref not in _ALLOWED_CANDIDATE_TOOL_REFS or candidate_tool_ref not in allowed_tool_refs:
        return _result(
            status="BLOCKED",
            candidate_tool_refs=[candidate_tool_ref],
            blocked_reason="candidate_tool_ref_not_allowlisted",
            notes=["Candidate tool ref must be present in the explicit allowed_tool_refs input."],
        )

    evidence_refs = dict(plan_input.get("evidence_refs", {}))
    required_inputs = list(_REQUIRED_EVIDENCE_BY_TOOL[candidate_tool_ref])
    missing_inputs = [required for required in required_inputs if not _has_ref(evidence_refs.get(required))]
    if missing_inputs:
        return _result(
            status="NEEDS_EVIDENCE",
            candidate_tool_refs=[candidate_tool_ref],
            tool_plan_candidate=[
                _candidate(
                    tool_ref=candidate_tool_ref,
                    input_mapping_refs={key: evidence_refs[key] for key in required_inputs if _has_ref(evidence_refs.get(key))},
                    missing_inputs=missing_inputs,
                )
            ],
            missing_evidence_refs=missing_inputs,
            owner_questions=list(_OWNER_QUESTIONS_BY_TOOL[candidate_tool_ref]),
            notes=["Required evidence refs are missing. No raw values were used."],
        )

    ambiguous_refs = set(str(ref) for ref in plan_input.get("ambiguous_column_refs", []))
    required_mapping_refs = {key: evidence_refs[key] for key in required_inputs}
    ambiguous_required = [
        semantic_key
        for semantic_key, evidence_ref in required_mapping_refs.items()
        if semantic_key in ambiguous_refs or evidence_ref in ambiguous_refs
    ]
    if ambiguous_required:
        return _result(
            status="NEEDS_OWNER_INPUT",
            candidate_tool_refs=[candidate_tool_ref],
            tool_plan_candidate=[
                _candidate(
                    tool_ref=candidate_tool_ref,
                    input_mapping_refs=required_mapping_refs,
                    missing_inputs=[],
                )
            ],
            owner_questions=list(_OWNER_QUESTIONS_BY_TOOL[candidate_tool_ref]),
            notes=["At least one required evidence ref points to an ambiguous/unconfirmed column."],
        )

    confirmed_refs = set(str(ref) for ref in plan_input.get("confirmed_column_refs", []))
    unconfirmed_required = [
        semantic_key
        for semantic_key, evidence_ref in required_mapping_refs.items()
        if semantic_key not in confirmed_refs and evidence_ref not in confirmed_refs
    ]
    if unconfirmed_required:
        return _result(
            status="NEEDS_OWNER_INPUT",
            candidate_tool_refs=[candidate_tool_ref],
            tool_plan_candidate=[
                _candidate(
                    tool_ref=candidate_tool_ref,
                    input_mapping_refs=required_mapping_refs,
                    missing_inputs=[],
                )
            ],
            owner_questions=list(_OWNER_QUESTIONS_BY_TOOL[candidate_tool_ref]),
            notes=["Required evidence refs exist but are not confirmed."],
        )

    return _result(
        status="TOOL_PLAN_CANDIDATE_READY",
        candidate_tool_refs=[candidate_tool_ref],
        tool_plan_candidate=[
            _candidate(
                tool_ref=candidate_tool_ref,
                input_mapping_refs=required_mapping_refs,
                missing_inputs=[],
            )
        ],
        notes=["Candidate built from confirmed evidence refs only. No executable request was produced."],
    )


def _match_candidate_tool_ref(*, owner_axis: str | None, owner_problem: str | None) -> str | None:
    text = _normalize_text(" ".join(part for part in [owner_axis or "", owner_problem or ""] if part))
    if not text:
        return None
    for tokens, tool_ref in _OWNER_AXIS_TOOL_MAP:
        if any(_normalize_text(token) in text for token in tokens):
            return tool_ref
    return None


def _candidate(
    *,
    tool_ref: str,
    input_mapping_refs: dict[str, str],
    missing_inputs: list[str],
) -> Service1ToolPlanCandidateV1:
    return {
        "tool_ref": tool_ref,
        "reason": f"Owner axis matched conservative V1 candidate {tool_ref}.",
        "input_mapping_refs": dict(input_mapping_refs),
        "missing_inputs": list(missing_inputs),
        "limitations": list(_LIMITATIONS_BY_TOOL[tool_ref]),
    }


def _result(
    *,
    status: ToolPlanCandidateStatusV1,
    candidate_tool_refs: list[str] | None = None,
    tool_plan_candidate: list[Service1ToolPlanCandidateV1] | None = None,
    missing_evidence_refs: list[str] | None = None,
    owner_questions: list[str] | None = None,
    blocked_reason: str | None = None,
    notes: list[str] | None = None,
) -> Service1AutoToolPlanCandidateResultV1:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "status": status,
        "candidate_tool_refs": list(candidate_tool_refs or []),
        "tool_plan_candidate": list(tool_plan_candidate or []),
        "missing_evidence_refs": list(missing_evidence_refs or []),
        "owner_questions": list(owner_questions or []),
        "blocked_reason": blocked_reason,
        "runtime_authorized": False,
        "execution_authorized": False,
        "tool_requests_authorized": False,
        "autonomous_delivery_authorized": False,
        "notes": list(notes or []),
    }


def _normalize_text(value: str) -> str:
    return value.strip().lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")


def _has_ref(value: str | None) -> bool:
    return isinstance(value, str) and bool(value.strip())


__all__ = [
    "SCHEMA_VERSION",
    "Service1AutoToolPlanCandidateInputV1",
    "Service1ToolPlanCandidateV1",
    "Service1AutoToolPlanCandidateResultV1",
    "build_service_1_auto_tool_plan_candidate_v1",
]
