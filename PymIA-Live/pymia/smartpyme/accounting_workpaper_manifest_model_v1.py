from __future__ import annotations

from typing import Final, Literal, TypedDict

CAPABILITY_REF: Final[str] = "service_1_accounting_workpaper_manifest_model_v1"
SERVICE_NAME: Final[str] = "SERVICE_1"

Status = Literal[
    "VALID",
    "MISSING_EVIDENCE_MANIFEST",
    "MISSING_TEMPLATE_MANIFEST",
    "INVALID_EVIDENCE_ITEM",
    "INVALID_TEMPLATE_SECTION",
    "DUPLICATE_EVIDENCE_REF",
    "DUPLICATE_TEMPLATE_SECTION",
    "BLOCKED_LIVE_SOURCE",
    "INVALID_INPUT",
]


class EvidenceItemV1(TypedDict):
    evidence_ref: str
    source_name: str
    source_kind: str
    period_ref: str
    owner_supplied: bool
    operator_notes: str
    sensitive_data_present: bool


class EvidenceManifestV1(TypedDict):
    manifest_id: str
    period_ref: str
    evidence_items: list[EvidenceItemV1]
    live_source: bool


class TemplateManifestV1(TypedDict):
    template_ref: str
    template_name: str
    area_revision: str
    required_sections: list[str]
    optional_sections: list[str]
    review_owner: str
    template_runtime_requested: bool


class WorkpaperManifestBundleInputV1(TypedDict):
    evidence_manifest: EvidenceManifestV1 | None
    template_manifest: TemplateManifestV1 | None


class WorkpaperManifestBundleResultV1(TypedDict):
    capability_ref: str
    status: Status
    runtime_authorized: Literal[False]
    production_allowed: Literal[False]
    valid_for_draft_packet: bool
    evidence_manifest_id: str | None
    template_ref: str | None
    period_ref: str | None
    area_revision: str | None
    evidence_count: int
    required_section_count: int
    optional_section_count: int
    missing_inputs: list[str]
    reasons: list[str]
    handoff_refs: list[str]
    forbidden_claims: list[str]
    delivery_input: dict[str, object]


_FORBIDDEN_CLAIMS: Final[tuple[str, ...]] = (
    "No evidence was fully audited.",
    "No workpaper is final.",
    "No accounting conclusion is certified.",
    "No fiscal conclusion is certified.",
    "No accounting entries were generated.",
    "No source file was parsed.",
    "No template was executed as runtime.",
)


def build_accounting_workpaper_manifest_model_v1(*, bundle_input: WorkpaperManifestBundleInputV1) -> WorkpaperManifestBundleResultV1:
    if not isinstance(bundle_input, dict):
        return _result("INVALID_INPUT", None, None, None, None, 0, 0, 0, ["bundle_input"], ["Invalid bundle input."], [])

    evidence_manifest = bundle_input.get("evidence_manifest")
    template_manifest = bundle_input.get("template_manifest")

    if not isinstance(evidence_manifest, dict):
        return _result(
            "MISSING_EVIDENCE_MANIFEST",
            None,
            _template_ref(template_manifest),
            None,
            _area_revision(template_manifest),
            0,
            _required_section_count(template_manifest),
            _optional_section_count(template_manifest),
            ["evidence_manifest"],
            ["Evidence manifest is missing."],
            _handoff_refs(evidence_manifest, template_manifest),
        )
    if not isinstance(template_manifest, dict):
        return _result(
            "MISSING_TEMPLATE_MANIFEST",
            _manifest_id(evidence_manifest),
            None,
            _period_ref(evidence_manifest),
            None,
            _evidence_count(evidence_manifest),
            0,
            0,
            ["template_manifest"],
            ["Template manifest is missing."],
            _handoff_refs(evidence_manifest, template_manifest),
        )

    common_payload = (
        _manifest_id(evidence_manifest),
        _template_ref(template_manifest),
        _period_ref(evidence_manifest),
        _area_revision(template_manifest),
        _evidence_count(evidence_manifest),
        _required_section_count(template_manifest),
        _optional_section_count(template_manifest),
    )

    if evidence_manifest.get("live_source") is True or template_manifest.get("template_runtime_requested") is True:
        return _result("BLOCKED_LIVE_SOURCE", *common_payload, [], ["Live source or template runtime is blocked."], _handoff_refs(evidence_manifest, template_manifest))

    invalid_evidence_reason = _first_invalid_evidence_reason(evidence_manifest)
    if invalid_evidence_reason:
        return _result("INVALID_EVIDENCE_ITEM", *common_payload, [], [invalid_evidence_reason], _handoff_refs(evidence_manifest, template_manifest))

    invalid_template_reason = _first_invalid_template_reason(template_manifest)
    if invalid_template_reason:
        return _result("INVALID_TEMPLATE_SECTION", *common_payload, [], [invalid_template_reason], _handoff_refs(evidence_manifest, template_manifest))

    duplicate_evidence_ref = _first_duplicate_evidence_ref(evidence_manifest)
    if duplicate_evidence_ref:
        return _result("DUPLICATE_EVIDENCE_REF", *common_payload, [], [f"Duplicate evidence_ref: {duplicate_evidence_ref}."], _handoff_refs(evidence_manifest, template_manifest))

    duplicate_section = _first_duplicate_template_section(template_manifest)
    if duplicate_section:
        return _result("DUPLICATE_TEMPLATE_SECTION", *common_payload, [], [f"Duplicate template section: {duplicate_section}."], _handoff_refs(evidence_manifest, template_manifest))

    return _result("VALID", *common_payload, [], ["Manifest bundle is valid for draft packet handoff only."], _handoff_refs(evidence_manifest, template_manifest))


def _result(
    status: Status,
    evidence_manifest_id: str | None,
    template_ref: str | None,
    period_ref: str | None,
    area_revision: str | None,
    evidence_count: int,
    required_section_count: int,
    optional_section_count: int,
    missing_inputs: list[str],
    reasons: list[str],
    handoff_refs: list[str],
) -> WorkpaperManifestBundleResultV1:
    valid = status == "VALID"
    delivery_input = {
        "service_name": SERVICE_NAME,
        "capability_ref": CAPABILITY_REF,
        "status": status,
        "owner_summary": _owner_summary(status),
        "inputs_used": {
            "evidence_manifest_id": evidence_manifest_id,
            "template_ref": template_ref,
            "period_ref": period_ref,
            "area_revision": area_revision,
        },
        "computed_results": {
            "valid_for_draft_packet": valid,
            "evidence_count": evidence_count,
            "required_section_count": required_section_count,
            "optional_section_count": optional_section_count,
            "handoff_refs": handoff_refs,
        },
        "missing_inputs": missing_inputs,
        "limitations": [
            "Manifest model only; no source files were read.",
            "Template structure was declared, not executed.",
            "Human accounting review remains mandatory.",
        ],
        "forbidden_claims": list(_FORBIDDEN_CLAIMS),
        "technical_notes": reasons,
        "runtime_authorized": False,
    }
    return {
        "capability_ref": CAPABILITY_REF,
        "status": status,
        "runtime_authorized": False,
        "production_allowed": False,
        "valid_for_draft_packet": valid,
        "evidence_manifest_id": evidence_manifest_id,
        "template_ref": template_ref,
        "period_ref": period_ref,
        "area_revision": area_revision,
        "evidence_count": evidence_count,
        "required_section_count": required_section_count,
        "optional_section_count": optional_section_count,
        "missing_inputs": missing_inputs,
        "reasons": reasons,
        "handoff_refs": handoff_refs,
        "forbidden_claims": list(_FORBIDDEN_CLAIMS),
        "delivery_input": delivery_input,
    }


def _owner_summary(status: Status) -> str:
    if status == "VALID":
        return "Los manifiestos están listos para un paquete borrador; no generan papel final."
    if status == "MISSING_EVIDENCE_MANIFEST":
        return "Falta el manifiesto de evidencia soporte."
    if status == "MISSING_TEMPLATE_MANIFEST":
        return "Falta el manifiesto de plantilla."
    if status == "BLOCKED_LIVE_SOURCE":
        return "El sandbox bloqueó fuente viva o ejecución de plantilla."
    return "El bundle de manifiestos requiere corrección antes de continuar."


def _manifest_id(manifest: object) -> str | None:
    return _clean_text(manifest.get("manifest_id")) if isinstance(manifest, dict) else None


def _period_ref(manifest: object) -> str | None:
    return _clean_text(manifest.get("period_ref")) if isinstance(manifest, dict) else None


def _template_ref(manifest: object) -> str | None:
    return _clean_text(manifest.get("template_ref")) if isinstance(manifest, dict) else None


def _area_revision(manifest: object) -> str | None:
    return _clean_text(manifest.get("area_revision")) if isinstance(manifest, dict) else None


def _evidence_count(manifest: object) -> int:
    items = manifest.get("evidence_items") if isinstance(manifest, dict) else None
    return len(items) if isinstance(items, list) else 0


def _required_section_count(manifest: object) -> int:
    sections = manifest.get("required_sections") if isinstance(manifest, dict) else None
    return len(sections) if isinstance(sections, list) else 0


def _optional_section_count(manifest: object) -> int:
    sections = manifest.get("optional_sections") if isinstance(manifest, dict) else None
    return len(sections) if isinstance(sections, list) else 0


def _first_invalid_evidence_reason(manifest: dict[str, object]) -> str | None:
    if not _manifest_id(manifest):
        return "Evidence manifest missing manifest_id."
    if not _period_ref(manifest):
        return "Evidence manifest missing period_ref."
    items = manifest.get("evidence_items")
    if not isinstance(items, list) or not items:
        return "Evidence manifest evidence_items must be a non-empty list."
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            return f"Evidence item {index} must be an object."
        for field in ("evidence_ref", "source_name", "source_kind", "period_ref"):
            if not _clean_text(item.get(field)):
                return f"Evidence item {index} missing {field}."
        if not isinstance(item.get("owner_supplied"), bool):
            return f"Evidence item {index} owner_supplied must be boolean."
        if not isinstance(item.get("sensitive_data_present"), bool):
            return f"Evidence item {index} sensitive_data_present must be boolean."
        if not isinstance(item.get("operator_notes"), str):
            return f"Evidence item {index} operator_notes must be string."
    return None


def _first_invalid_template_reason(manifest: dict[str, object]) -> str | None:
    for field in ("template_ref", "template_name", "area_revision", "review_owner"):
        if not _clean_text(manifest.get(field)):
            return f"Template manifest missing {field}."
    if not _is_non_empty_string_list(manifest.get("required_sections")):
        return "Template manifest required_sections must be a non-empty list of strings."
    if not _is_string_list(manifest.get("optional_sections")):
        return "Template manifest optional_sections must be a list of strings."
    if not isinstance(manifest.get("template_runtime_requested"), bool):
        return "Template manifest template_runtime_requested must be boolean."
    return None


def _first_duplicate_evidence_ref(manifest: dict[str, object]) -> str | None:
    seen: set[str] = set()
    items = manifest.get("evidence_items")
    if not isinstance(items, list):
        return None
    for item in items:
        if not isinstance(item, dict):
            continue
        evidence_ref = _clean_text(item.get("evidence_ref"))
        if evidence_ref in seen:
            return evidence_ref
        if evidence_ref:
            seen.add(evidence_ref)
    return None


def _first_duplicate_template_section(manifest: dict[str, object]) -> str | None:
    seen: set[str] = set()
    for key in ("required_sections", "optional_sections"):
        sections = manifest.get(key)
        if not isinstance(sections, list):
            continue
        for section in sections:
            text = _clean_text(section)
            if text in seen:
                return text
            if text:
                seen.add(text)
    return None


def _handoff_refs(evidence_manifest: object, template_manifest: object) -> list[str]:
    refs: list[str] = []
    if _manifest_id(evidence_manifest):
        refs.append("evidence_manifest")
    if _template_ref(template_manifest):
        refs.append("template_manifest")
    return refs


def _clean_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _is_string_list(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) and bool(item.strip()) for item in value)


def _is_non_empty_string_list(value: object) -> bool:
    return _is_string_list(value) and len(value) > 0
