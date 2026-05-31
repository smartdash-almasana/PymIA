"""
ParsedDocumentMetadata — Common Contract for Document Parser Fronts.

Define la forma común que todo parser documental (Excel, CSV, PDF, DOCX, texto
plano, etc.) debe producir para alimentar ``EvidenceRecord.metadata`` sin
mezclar parsing con narrativa, ejecución de fórmulas o diagnóstico.

Este módulo es puro:
    - NO lee archivos.
    - NO ejecuta fórmulas.
    - NO calcula variables derivadas.
    - NO diagnostica.
    - NO persiste.
    - NO despacha microservicios.
    - NO invoca Telegram / Hermes / landing / conversa-engine.

Solo define dataclasses ``frozen``, JSON-safe, con validaciones fail-closed
para que cualquier frente documental produzca metadata compatible con
``EvidenceSufficiencyGate`` y ``post_ficha_evidence_gate``.

Ver: docs/smartpyme/PYMIA_OPERATING_METHOD_POST_FICHA.md
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Parse statuses
# ---------------------------------------------------------------------------
PARSE_STATUS_OK = "OK"
PARSE_STATUS_PARTIAL = "PARTIAL"
PARSE_STATUS_FAILED = "FAILED"

ALLOWED_PARSE_STATUSES: tuple[str, ...] = (
    PARSE_STATUS_OK,
    PARSE_STATUS_PARTIAL,
    PARSE_STATUS_FAILED,
)

# ---------------------------------------------------------------------------
# Default ingestion routes / contexts (vocabulario abierto, no enumeración)
# ---------------------------------------------------------------------------
DEFAULT_INGESTION_ROUTE = "BEM_AI"
DEFAULT_DOCUMENT_CONTEXT = "desconocido"


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------
def _normalize_str_list(value: Any, *, label: str) -> List[str]:
    """Return a defensive, stripped, deduplicated list of non-empty strings."""
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list")
    out: List[str] = []
    seen: set[str] = set()
    for item in value:
        if item is None:
            continue
        s = str(item).strip()
        if s and s not in seen:
            seen.add(s)
            out.append(s)
    return out


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Summary dataclasses (frozen, JSON-safe)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class SheetSummary:
    """Resumen estructural de una hoja tabular (Excel/CSV)."""

    name: str
    kind: str  # "tabular" | "summary" | "auxiliary" | "section" | ...
    header_row: Optional[int] = None
    column_count: int = 0
    row_count: int = 0
    fields_detected: List[str] = field(default_factory=list)
    fields_ambiguous: List[str] = field(default_factory=list)
    fields_unknown: List[str] = field(default_factory=list)
    status: str = "OK"  # "OK" | "PARTIAL" | "BLOCKED"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TableSummary:
    """Resumen de una tabla extraída (puede provenir de PDF/DOCX/HTML)."""

    table_id: str
    origin: str  # "sheet:<name>" | "page:<N>" | "section:<Y>" | ...
    column_count: int = 0
    row_count: int = 0
    header_sample: List[str] = field(default_factory=list)
    semantic_hint: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SectionSummary:
    """Resumen de una sección narrativa (PDF/DOCX/txt)."""

    heading: str
    level: int = 0
    char_count: int = 0
    keyword_hits: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# ParsedDocumentMetadata
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ParsedDocumentMetadata:
    """
    Contrato común de metadata para cualquier parser documental.

    Invariante:
        - Es ``frozen`` (inmutable tras construcción).
        - Es JSON-safe vía ``to_dict()`` / ``asdict()``.
        - Expone ``fields`` de forma compatible con ``EvidenceSufficiencyGate``
          (que inspecciona ``metadata["fields"]`` y keys hermanas).
        - Es fail-closed: inputs inválidos producen ``ValueError``.
    """

    # Identidad del parser
    file_type: str  # "xlsx" | "csv" | "pdf" | "docx" | "txt" | "unknown" | ...
    parser_name: str  # "excel_profile_v1" | "docling_v1" | "plaintext_v1" | ...
    parser_version: str
    parse_status: str  # "OK" | "PARTIAL" | "FAILED"

    # Estructura: una o más pobladas según file_type
    sheets: List[SheetSummary] = field(default_factory=list)
    tables: List[TableSummary] = field(default_factory=list)
    sections: List[SectionSummary] = field(default_factory=list)

    # Contrato con EvidenceSufficiencyGate
    fields: List[str] = field(default_factory=list)  # mapped (sin ambiguous)
    ambiguous_fields: List[str] = field(default_factory=list)
    unknown_fields: List[str] = field(default_factory=list)
    declared_fields: List[str] = field(default_factory=list)  # de FIELDS=

    # Calidad y ruteo
    warnings: List[str] = field(default_factory=list)
    confidence: float = 0.0
    ingestion_route: str = DEFAULT_INGESTION_ROUTE
    document_context: str = DEFAULT_DOCUMENT_CONTEXT

    # Trazabilidad
    parsed_at: str = field(default_factory=_now_iso)
    raw_artifact_refs: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # --- validaciones fail-closed ------------------------------------
        if not isinstance(self.file_type, str) or not self.file_type.strip():
            raise ValueError("file_type is required and must be a non-empty string")
        if not isinstance(self.parser_name, str) or not self.parser_name.strip():
            raise ValueError("parser_name is required and must be a non-empty string")
        if self.parse_status not in ALLOWED_PARSE_STATUSES:
            raise ValueError(
                f"parse_status must be one of {ALLOWED_PARSE_STATUSES}, "
                f"got {self.parse_status!r}"
            )
        if isinstance(self.confidence, bool) or not isinstance(
            self.confidence, (int, float)
        ):
            raise ValueError("confidence must be a number")
        conf = float(self.confidence)
        if not (0.0 <= conf <= 1.0):
            raise ValueError("confidence must be between 0.0 and 1.0")

        # --- normalización de listas -------------------------------------
        norm_fields = _normalize_str_list(self.fields, label="fields")
        norm_ambiguous = _normalize_str_list(
            self.ambiguous_fields, label="ambiguous_fields"
        )
        norm_unknown = _normalize_str_list(self.unknown_fields, label="unknown_fields")
        norm_declared = _normalize_str_list(
            self.declared_fields, label="declared_fields"
        )
        norm_warnings = _normalize_str_list(self.warnings, label="warnings")

        # --- normalización de raw_artifact_refs --------------------------
        refs = self.raw_artifact_refs
        if refs is None:
            norm_refs: Dict[str, str] = {}
        elif isinstance(refs, dict):
            norm_refs = {str(k).strip(): str(v).strip() for k, v in refs.items()}
        else:
            raise ValueError("raw_artifact_refs must be a dict or None")

        # --- normalización de listas de resúmenes ------------------------
        sheets = self.sheets
        if sheets is None:
            sheets_norm: List[SheetSummary] = []
        elif isinstance(sheets, list):
            for i, s in enumerate(sheets):
                if not isinstance(s, SheetSummary):
                    raise ValueError(f"sheets[{i}] must be a SheetSummary")
            sheets_norm = list(sheets)
        else:
            raise ValueError("sheets must be a list")

        tables = self.tables
        if tables is None:
            tables_norm: List[TableSummary] = []
        elif isinstance(tables, list):
            for i, t in enumerate(tables):
                if not isinstance(t, TableSummary):
                    raise ValueError(f"tables[{i}] must be a TableSummary")
            tables_norm = list(tables)
        else:
            raise ValueError("tables must be a list")

        sections = self.sections
        if sections is None:
            sections_norm: List[SectionSummary] = []
        elif isinstance(sections, list):
            for i, sec in enumerate(sections):
                if not isinstance(sec, SectionSummary):
                    raise ValueError(f"sections[{i}] must be a SectionSummary")
            sections_norm = list(sections)
        else:
            raise ValueError("sections must be a list")

        # --- parsed_at: garantizar ISO no vacío --------------------------
        parsed_at = self.parsed_at
        if not isinstance(parsed_at, str) or not parsed_at.strip():
            parsed_at = _now_iso()

        # --- aplicar valores normalizados (frozen dataclass) -------------
        object.__setattr__(self, "fields", norm_fields)
        object.__setattr__(self, "ambiguous_fields", norm_ambiguous)
        object.__setattr__(self, "unknown_fields", norm_unknown)
        object.__setattr__(self, "declared_fields", norm_declared)
        object.__setattr__(self, "warnings", norm_warnings)
        object.__setattr__(self, "raw_artifact_refs", norm_refs)
        object.__setattr__(self, "sheets", sheets_norm)
        object.__setattr__(self, "tables", tables_norm)
        object.__setattr__(self, "sections", sections_norm)
        object.__setattr__(self, "confidence", conf)
        object.__setattr__(self, "parsed_at", parsed_at)

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialización JSON-safe sin encoder custom.

        Produce un ``dict`` plano listo para ``json.dumps(..., ensure_ascii=False)``.
        Las listas anidadas (``sheets``, ``tables``, ``sections``) se serializan
        recursivamente gracias a ``asdict``.
        """
        return asdict(self)


__all__ = [
    "SheetSummary",
    "TableSummary",
    "SectionSummary",
    "ParsedDocumentMetadata",
    "PARSE_STATUS_OK",
    "PARSE_STATUS_PARTIAL",
    "PARSE_STATUS_FAILED",
    "ALLOWED_PARSE_STATUSES",
    "DEFAULT_INGESTION_ROUTE",
    "DEFAULT_DOCUMENT_CONTEXT",
]
