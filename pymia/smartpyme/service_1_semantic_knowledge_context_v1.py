"""Servicio 1 — governed semantic knowledge context for C2 F2.

This module loads only explicitly approved semantic reference sources and
retrieves a bounded subset relevant to an already-canonical workbook semantic
context. Knowledge is CONTEXT_ONLY: it never grants semantic, mathematical,
runtime, owner, tool or delivery authority.
"""
from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
import re
import unicodedata
from typing import Any, Final

SCHEMA_VERSION: Final[str] = "SERVICE_1_SEMANTIC_KNOWLEDGE_CONTEXT_V1"
STATUS_READY: Final[str] = "SEMANTIC_KNOWLEDGE_CONTEXT_READY"
STATUS_BLOCKED: Final[str] = "BLOCKED"
AUTHORITY_CONTEXT_ONLY: Final[str] = "CONTEXT_ONLY"

BUSINESS_CATALOG_SOURCE: Final[str] = "docs/catalogo/SERVICE_1_BUSINESS_COLUMN_CATALOG_V1.md"
MAX_RETRIEVED_ITEMS: Final[int] = 32

BLOCK_WORKBOOK_CONTEXT_INVALID: Final[str] = "BLOCK_SEMANTIC_KNOWLEDGE_WORKBOOK_CONTEXT_INVALID"
BLOCK_SOURCE_MISSING: Final[str] = "BLOCK_SEMANTIC_KNOWLEDGE_SOURCE_MISSING"
BLOCK_SOURCE_INVALID: Final[str] = "BLOCK_SEMANTIC_KNOWLEDGE_SOURCE_INVALID"
BLOCK_NO_KNOWLEDGE: Final[str] = "BLOCK_SEMANTIC_KNOWLEDGE_EMPTY"

_ENTRY_RE = re.compile(r"^- \*\*(.+?)\*\*\s*$")
_ALIASES_RE = re.compile(r"^\s+- \*\*Sinónimos habituales:\*\*\s*(.*)$")
_MEANING_RE = re.compile(r"^\s+- \*\*Significado empresarial:\*\*\s*(.*)$")
_TYPE_RE = re.compile(r"^\s+- \*\*Tipo de dato:\*\*\s*(.*)$")
_CONFUSIONS_RE = re.compile(r"^\s+- \*\*Confusiones frecuentes:\*\*\s*(.*)$")


def load_service_1_business_semantic_knowledge_v1() -> dict[str, Any]:
    """Load the explicit business-column catalog as context-only knowledge."""
    source_path = Path(__file__).resolve().parents[2] / BUSINESS_CATALOG_SOURCE
    if not source_path.is_file():
        return _blocked(BLOCK_SOURCE_MISSING)
    try:
        text = source_path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError):
        return _blocked(BLOCK_SOURCE_INVALID)

    items: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for raw_line in text.splitlines():
        entry_match = _ENTRY_RE.match(raw_line)
        if entry_match:
            if current is not None:
                item = _finalize_item(current)
                if item is not None:
                    items.append(item)
            current = {
                "label": entry_match.group(1).strip(),
                "aliases": [],
                "description": "",
                "data_type_hint": "",
                "ambiguity_note": "",
            }
            continue
        if current is None:
            continue
        aliases_match = _ALIASES_RE.match(raw_line)
        if aliases_match:
            current["aliases"] = [
                value.strip() for value in aliases_match.group(1).split(",") if value.strip()
            ]
            continue
        meaning_match = _MEANING_RE.match(raw_line)
        if meaning_match:
            current["description"] = meaning_match.group(1).strip()
            continue
        type_match = _TYPE_RE.match(raw_line)
        if type_match:
            current["data_type_hint"] = type_match.group(1).strip()
            continue
        confusion_match = _CONFUSIONS_RE.match(raw_line)
        if confusion_match:
            current["ambiguity_note"] = confusion_match.group(1).strip()

    if current is not None:
        item = _finalize_item(current)
        if item is not None:
            items.append(item)

    unique_ids = {item["knowledge_id"] for item in items}
    if not items or len(unique_ids) != len(items):
        return _blocked(BLOCK_NO_KNOWLEDGE)

    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_READY,
        "blocked_reason": None,
        "source_registry": [
            {
                "source_ref": BUSINESS_CATALOG_SOURCE,
                "classification": "LEXICAL_REFERENCE_ONLY",
                "authority": AUTHORITY_CONTEXT_ONLY,
            }
        ],
        "knowledge_items": items,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def retrieve_service_1_semantic_knowledge_v1(
    *, workbook_semantic_context: Any,
    knowledge_catalog: Any | None = None,
    max_items: int = MAX_RETRIEVED_ITEMS,
) -> dict[str, Any]:
    """Retrieve bounded context from headers/sheet names without deciding meaning."""
    if not isinstance(workbook_semantic_context, Mapping):
        return _blocked(BLOCK_WORKBOOK_CONTEXT_INVALID)
    workbook = dict(workbook_semantic_context)
    if workbook.get("status") != "WORKBOOK_SEMANTIC_CONTEXT_READY":
        return _blocked(BLOCK_WORKBOOK_CONTEXT_INVALID)
    tables = workbook.get("tables")
    if not isinstance(tables, list) or not tables:
        return _blocked(BLOCK_WORKBOOK_CONTEXT_INVALID)

    catalog = (
        load_service_1_business_semantic_knowledge_v1()
        if knowledge_catalog is None
        else knowledge_catalog
    )
    if not isinstance(catalog, Mapping) or catalog.get("status") != STATUS_READY:
        return _blocked(BLOCK_SOURCE_INVALID)

    signals = _workbook_signals(tables)
    scored: list[tuple[int, str, dict[str, Any], tuple[str, ...]]] = []
    for raw_item in catalog.get("knowledge_items") or []:
        if not isinstance(raw_item, Mapping):
            continue
        item = dict(raw_item)
        score, matched = _retrieval_score(item=item, signals=signals)
        if score > 0:
            scored.append((score, str(item.get("knowledge_id") or ""), item, matched))

    scored.sort(key=lambda row: (-row[0], row[1]))
    bounded = scored[: max(1, int(max_items))]
    retrieved = [row[2] for row in bounded]
    evidence = [
        {
            "knowledge_id": row[1],
            "score": row[0],
            "matched_workbook_signals": list(row[3]),
            "retrieval_kind": "DETERMINISTIC_LEXICAL_RETRIEVAL_ONLY",
        }
        for row in bounded
    ]
    matched_signals = {signal for row in bounded for signal in row[3]}

    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_READY,
        "blocked_reason": None,
        "case_id": workbook.get("case_id"),
        "source_registry": list(catalog.get("source_registry") or []),
        "retrieved_knowledge": retrieved,
        "retrieval_evidence": evidence,
        "unmatched_context": [signal for signal in signals if signal not in matched_signals],
        "catalog_item_count": len(catalog.get("knowledge_items") or []),
        "retrieved_item_count": len(retrieved),
        "retrieval_scoped": len(retrieved) < len(catalog.get("knowledge_items") or []),
        "authority": AUTHORITY_CONTEXT_ONLY,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _finalize_item(raw: Mapping[str, Any]) -> dict[str, Any] | None:
    label = str(raw.get("label") or "").strip()
    description = str(raw.get("description") or "").strip()
    if not label or not description:
        return None
    return {
        "knowledge_id": f"business_term:{_normalize(label)}",
        "kind": "TERM",
        "label": label,
        "description": description,
        "aliases": [str(value).strip() for value in raw.get("aliases") or [] if str(value).strip()],
        "data_type_hint": str(raw.get("data_type_hint") or "").strip() or None,
        "ambiguity_note": str(raw.get("ambiguity_note") or "").strip() or None,
        "related_v2_axes": {},
        "source_ref": BUSINESS_CATALOG_SOURCE,
        "authority": AUTHORITY_CONTEXT_ONLY,
    }


def _workbook_signals(tables: list[Any]) -> tuple[str, ...]:
    signals: list[str] = []
    seen: set[str] = set()
    for raw_table in tables:
        if not isinstance(raw_table, Mapping):
            continue
        values = [raw_table.get("sheet_name")]
        for raw_column in raw_table.get("columns") or []:
            if isinstance(raw_column, Mapping):
                values.extend(
                    [
                        raw_column.get("column_name"),
                        raw_column.get("normalized_header"),
                    ]
                )
        for value in values:
            normalized = _normalize(str(value or ""))
            if normalized and normalized not in seen:
                seen.add(normalized)
                signals.append(normalized)
    return tuple(signals)


def _retrieval_score(*, item: Mapping[str, Any], signals: tuple[str, ...]) -> tuple[int, tuple[str, ...]]:
    terms = {
        _normalize(str(item.get("label") or "")),
        *(_normalize(str(value)) for value in item.get("aliases") or []),
    }
    terms.discard("")
    score = 0
    matched: list[str] = []
    for signal in signals:
        signal_tokens = set(signal.split("_"))
        best = 0
        for term in terms:
            term_tokens = set(term.split("_"))
            if signal == term:
                best = max(best, 100)
            elif term and (term in signal or signal in term):
                best = max(best, 70)
            elif len(term_tokens) >= 2 and term_tokens.issubset(signal_tokens):
                best = max(best, 60)
            elif len(signal_tokens.intersection(term_tokens)) >= 2:
                best = max(best, 30)
        if best:
            score += best
            matched.append(signal)
    return score, tuple(matched)


def _normalize(value: str) -> str:
    folded = unicodedata.normalize("NFKD", value)
    asciiish = "".join(ch for ch in folded if not unicodedata.combining(ch)).lower()
    return "_".join(part for part in re.split(r"[^a-z0-9]+", asciiish) if part)


def _blocked(reason: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_BLOCKED,
        "blocked_reason": reason,
        "retrieved_knowledge": [],
        "retrieval_evidence": [],
        "unmatched_context": [],
        "authority": AUTHORITY_CONTEXT_ONLY,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_READY",
    "STATUS_BLOCKED",
    "AUTHORITY_CONTEXT_ONLY",
    "BUSINESS_CATALOG_SOURCE",
    "load_service_1_business_semantic_knowledge_v1",
    "retrieve_service_1_semantic_knowledge_v1",
]
