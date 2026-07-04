"""Servicio 1 pathology shadow artifact builder.

Pure observational candidate builder.

This module does not execute tools, route cases, persist state, modify delivery,
or authorize diagnosis.
"""

from __future__ import annotations

import unicodedata
from typing import Any

SCHEMA_VERSION = "service_1_pathology_shadow_artifact.v1"
SERVICE_NAME = "SERVICE_1"
FEATURE_FLAG = "SERVICE_1_PATHOLOGY_SHADOW_MODE"
MODE = "SHADOW_MODE"
RUNTIME_DECISION = "NO_EFFECT"
SUPPORTED_CATALOG_STATUS = "DRAFT_CANONICAL_CANDIDATE"

STATUS_GENERATED = "GENERATED"
STATUS_NO_CANDIDATES = "NO_CANDIDATES"
STATUS_BLOCKED = "BLOCKED"
STATUS_SKIPPED = "SKIPPED"

BLOCKED_FEATURE_FLAG_OFF = "FEATURE_FLAG_OFF"
BLOCKED_FEATURE_FLAG_STATE_UNCONTRACTED = "FEATURE_FLAG_STATE_UNCONTRACTED"
BLOCKED_CATALOG_MISSING = "CATALOG_MISSING"
BLOCKED_CATALOG_STATUS_UNSUPPORTED = "CATALOG_STATUS_UNSUPPORTED"
BLOCKED_CASE_ID_MISSING = "CASE_ID_MISSING"
BLOCKED_NO_SIGNALS_AVAILABLE = "NO_SIGNALS_AVAILABLE"

EXECUTABLE_FLAG_STATE = "SHADOW_ONLY"
SKIPPED_FLAG_STATE = "OFF"
UNCONTRACTED_PROMOTION_STATES = {"ADVISORY", "ROUTING_CANDIDATE", "ACTIVE"}


def build_service_1_pathology_shadow_artifact_v1(
    *,
    case_id: str,
    catalog_snapshot: dict[str, Any] | None,
    feature_flag_state: str,
    case_ref: str | None = None,
    owner_pain_text: str | None = None,
    anamnesis_signals: list[str] | None = None,
    case_metadata: dict[str, Any] | None = None,
    available_evidence_refs: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a non-binding pathology shadow artifact payload.

    The returned payload is JSON-serializable and preserves the no-effect
    safety line for every status.
    """

    state = _normalize_flag_state(feature_flag_state)
    base = _base_payload(
        case_id=case_id,
        case_ref=case_ref,
        feature_flag_state=state,
        metadata=metadata,
    )

    if not case_id:
        return _blocked_payload(base, BLOCKED_CASE_ID_MISSING)

    if state == SKIPPED_FLAG_STATE:
        return _skipped_payload(base, BLOCKED_FEATURE_FLAG_OFF)

    if state in UNCONTRACTED_PROMOTION_STATES:
        return _blocked_payload(base, BLOCKED_FEATURE_FLAG_STATE_UNCONTRACTED)

    if state != EXECUTABLE_FLAG_STATE:
        return _blocked_payload(base, BLOCKED_FEATURE_FLAG_STATE_UNCONTRACTED)

    catalog_root = _get_catalog_root(catalog_snapshot)
    if catalog_root is None:
        return _blocked_payload(base, BLOCKED_CATALOG_MISSING)

    catalog_status = str(catalog_root.get("estado") or "")
    if catalog_status != SUPPORTED_CATALOG_STATUS:
        return _blocked_payload(base, BLOCKED_CATALOG_STATUS_UNSUPPORTED)

    signal_texts = _collect_signal_texts(
        owner_pain_text=owner_pain_text,
        anamnesis_signals=anamnesis_signals,
        case_metadata=case_metadata,
        available_evidence_refs=available_evidence_refs,
    )
    if not signal_texts:
        return _blocked_payload(base, BLOCKED_NO_SIGNALS_AVAILABLE)

    candidates = _match_catalog_candidates(
        catalog_root=catalog_root,
        signal_texts=signal_texts,
        catalog_status=catalog_status,
    )
    if not candidates:
        return _complete_payload(
            base,
            status=STATUS_NO_CANDIDATES,
            blocked_reason=None,
            candidates=[],
        )

    return _complete_payload(
        base,
        status=STATUS_GENERATED,
        blocked_reason=None,
        candidates=candidates,
    )


def _normalize_flag_state(feature_flag_state: str) -> str:
    return str(feature_flag_state or "").strip().upper()


def _base_payload(
    *,
    case_id: str,
    case_ref: str | None,
    feature_flag_state: str,
    metadata: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "case_id": case_id,
        "case_ref": case_ref,
        "mode": MODE,
        "feature_flag": FEATURE_FLAG,
        "feature_flag_state": feature_flag_state,
        "status": STATUS_BLOCKED,
        "blocked_reason": None,
        "runtime_decision": RUNTIME_DECISION,
        "diagnosis_authorized": False,
        "routing_authorized": False,
        "tool_selection_authorized": False,
        "delivery_modification_authorized": False,
        "candidate_count": 0,
        "detected_candidates": [],
        "missing_evidence_global": [],
        "metadata": dict(metadata or {}),
    }


def _blocked_payload(base: dict[str, Any], reason: str) -> dict[str, Any]:
    return _complete_payload(
        base,
        status=STATUS_BLOCKED,
        blocked_reason=reason,
        candidates=[],
    )


def _skipped_payload(base: dict[str, Any], reason: str) -> dict[str, Any]:
    return _complete_payload(
        base,
        status=STATUS_SKIPPED,
        blocked_reason=reason,
        candidates=[],
    )


def _complete_payload(
    base: dict[str, Any],
    *,
    status: str,
    blocked_reason: str | None,
    candidates: list[dict[str, Any]],
) -> dict[str, Any]:
    payload = dict(base)
    payload["status"] = status
    payload["blocked_reason"] = blocked_reason
    payload["detected_candidates"] = list(candidates)
    payload["candidate_count"] = len(candidates)
    payload["missing_evidence_global"] = _unique_preserve_order(
        item
        for candidate in candidates
        for item in candidate.get("missing_evidence", [])
    )
    return payload


def _get_catalog_root(
    catalog_snapshot: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if not catalog_snapshot:
        return None
    root = catalog_snapshot.get("catalogo_patologias_smartpyme_v0")
    if not isinstance(root, dict):
        return None
    return root


def _collect_signal_texts(
    *,
    owner_pain_text: str | None,
    anamnesis_signals: list[str] | None,
    case_metadata: dict[str, Any] | None,
    available_evidence_refs: list[str] | None,
) -> list[str]:
    values: list[str] = []
    if owner_pain_text:
        values.append(owner_pain_text)
    for signal in anamnesis_signals or []:
        if signal:
            values.append(str(signal))
    for value in (case_metadata or {}).values():
        if value:
            values.append(str(value))
    for evidence_ref in available_evidence_refs or []:
        if evidence_ref:
            values.append(str(evidence_ref))
    return [value for value in values if _normalize_text(value)]


def _match_catalog_candidates(
    *,
    catalog_root: dict[str, Any],
    signal_texts: list[str],
    catalog_status: str,
) -> list[dict[str, Any]]:
    normalized_case_text = " ".join(_normalize_text(value) for value in signal_texts)
    candidates: list[dict[str, Any]] = []
    domains = catalog_root.get("dominios") or {}
    if not isinstance(domains, dict):
        return candidates

    for domain, entries in domains.items():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            matched_signals = _matched_catalog_signals(entry, normalized_case_text)
            if not matched_signals:
                continue
            candidates.append(
                {
                    "pathology_id": str(entry.get("id") or ""),
                    "name": str(entry.get("nombre") or ""),
                    "domain": str(domain),
                    "confidence": "candidate",
                    "matched_signals": matched_signals,
                    "missing_evidence": _list_of_strings(entry.get("datos_minimos")),
                    "suggested_formulas": _list_of_strings(
                        entry.get("formulas_asociadas")
                    ),
                    "suggested_skills": [],
                    "source_catalog_status": catalog_status,
                }
            )
    return candidates


def _matched_catalog_signals(
    entry: dict[str, Any], normalized_case_text: str
) -> list[str]:
    raw_signals = []
    raw_signals.extend(_list_of_strings(entry.get("senales_anamnesis")))
    raw_signals.extend(_list_of_strings(entry.get("sintomas")))
    matched: list[str] = []
    for raw_signal in raw_signals:
        normalized_signal = _normalize_text(raw_signal)
        if normalized_signal and normalized_signal in normalized_case_text:
            matched.append(raw_signal)
    return _unique_preserve_order(matched)


def _normalize_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", str(value).lower().strip())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def _list_of_strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if item is not None]


def _unique_preserve_order(values: Any) -> list[str]:
    seen = set()
    output = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        output.append(value)
    return output
