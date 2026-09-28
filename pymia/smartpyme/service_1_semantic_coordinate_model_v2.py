"""C2 Semantic Coordinate Model V2.

Contract-only semantic representation for reconstructing workbook meaning from
orthogonal governed axes.  It grants no runtime, mathematical, delivery or
automatic-reuse authority.

The model deliberately does not encode vertical-specific roles.  Business
families and operating archetypes are optional structural context assembled
from the same reusable taxonomy.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from functools import lru_cache
from pathlib import Path
import re
import unicodedata
from typing import Any, Final, Mapping, Sequence


SCHEMA_VERSION: Final[str] = "SERVICE_1_C2_SEMANTIC_COORDINATE_MODEL_V2"
TAXONOMY_SCHEMA_VERSION: Final[str] = "SERVICE_1_C2_SEMANTIC_COORDINATE_TAXONOMY_V2"
TAXONOMY_STATUS_READY: Final[str] = "SERVICE_1_C2_SEMANTIC_COORDINATE_TAXONOMY_READY"

AXES: Final[tuple[str, ...]] = (
    "entity",
    "object",
    "process",
    "measure",
    "state",
    "grain",
    "scope",
    "time",
    "identity",
    "relation",
    "unit",
    "aggregation",
)

_NON_ALNUM_RE: Final[re.Pattern[str]] = re.compile(r"[^a-z0-9_]+")
_UNDERSCORE_RE: Final[re.Pattern[str]] = re.compile(r"_+")
_CONTEXTUAL_AXES: Final[frozenset[str]] = frozenset({"entity", "process", "grain"})


def normalize_service_1_semantic_coordinate_text_v2(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or "")).encode("ascii", "ignore").decode("ascii")
    text = text.casefold().strip().replace("-", "_").replace("/", "_")
    text = _NON_ALNUM_RE.sub("_", text)
    return _UNDERSCORE_RE.sub("_", text).strip("_")


def _contains_token(normalized: str, token: str) -> bool:
    return (
        normalized == token
        or normalized.startswith(f"{token}_")
        or normalized.endswith(f"_{token}")
        or f"_{token}_" in normalized
    )


def _text(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value.strip()


def _optional_text(value: Any, *, field_name: str) -> str | None:
    if value is None:
        return None
    return _text(value, field_name=field_name)


def _unique_text_tuple(value: Any, *, field_name: str) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        raise ValueError(f"{field_name} must be a list or tuple")
    result: list[str] = []
    for item in value:
        text = _text(item, field_name=f"{field_name} item")
        if text in result:
            raise ValueError(f"{field_name} contains duplicate value {text!r}")
        result.append(text)
    return tuple(result)


@dataclass(frozen=True)
class Service1SemanticCoordinateTaxonomyV2:
    """Externally governed reusable semantic axes and structural taxonomy."""

    schema_version: str
    status: str
    axes: Mapping[str, tuple[str, ...]]
    labels: Mapping[str, Mapping[str, str]]
    aliases: Mapping[str, Mapping[str, tuple[str, ...]]]
    business_families: tuple[str, ...]
    operating_archetypes: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != TAXONOMY_SCHEMA_VERSION:
            raise ValueError("invalid semantic coordinate taxonomy schema_version")
        if self.status != TAXONOMY_STATUS_READY:
            raise ValueError("invalid semantic coordinate taxonomy status")
        if set(self.axes) != set(AXES):
            raise ValueError("semantic coordinate taxonomy must define exactly the governed axes")
        normalized: dict[str, tuple[str, ...]] = {}
        for axis in AXES:
            values = _unique_text_tuple(self.axes[axis], field_name=f"axis {axis}")
            if not values:
                raise ValueError(f"axis {axis} must not be empty")
            normalized[axis] = values
        object.__setattr__(self, "axes", normalized)
        if not isinstance(self.labels, Mapping) or set(self.labels) != set(AXES):
            raise ValueError("semantic coordinate taxonomy labels must define exactly the governed axes")
        normalized_labels: dict[str, dict[str, str]] = {}
        for axis in AXES:
            raw_labels = self.labels[axis]
            if not isinstance(raw_labels, Mapping):
                raise ValueError(f"labels for axis {axis} must be a mapping")
            if set(raw_labels) != set(normalized[axis]):
                raise ValueError(f"labels for axis {axis} must cover exactly its governed values")
            normalized_labels[axis] = {
                value: _text(raw_labels[value], field_name=f"label {axis}.{value}")
                for value in normalized[axis]
            }
        object.__setattr__(self, "labels", normalized_labels)
        if not isinstance(self.aliases, Mapping) or set(self.aliases) != set(AXES):
            raise ValueError("semantic coordinate taxonomy aliases must define exactly the governed axes")
        normalized_aliases: dict[str, dict[str, tuple[str, ...]]] = {}
        for axis in AXES:
            raw_axis_aliases = self.aliases[axis]
            if not isinstance(raw_axis_aliases, Mapping):
                raise ValueError(f"aliases for axis {axis} must be a mapping")
            unknown_values = set(raw_axis_aliases) - set(normalized[axis])
            if unknown_values:
                raise ValueError(f"aliases for axis {axis} reference unknown governed values")
            seen_aliases: set[str] = set()
            normalized_aliases[axis] = {}
            for value in normalized[axis]:
                raw_aliases = raw_axis_aliases.get(value, ())
                aliases = _unique_text_tuple(raw_aliases, field_name=f"aliases {axis}.{value}")
                normalized_tokens = tuple(dict.fromkeys(
                    token
                    for token in (
                        normalize_service_1_semantic_coordinate_text_v2(alias)
                        for alias in aliases
                    )
                    if token
                ))
                if set(normalized_tokens).intersection(seen_aliases):
                    raise ValueError(f"aliases for axis {axis} must be unique across governed values")
                seen_aliases.update(normalized_tokens)
                normalized_aliases[axis][value] = normalized_tokens
        object.__setattr__(self, "aliases", normalized_aliases)
        object.__setattr__(
            self,
            "business_families",
            _unique_text_tuple(self.business_families, field_name="business_families"),
        )
        object.__setattr__(
            self,
            "operating_archetypes",
            _unique_text_tuple(self.operating_archetypes, field_name="operating_archetypes"),
        )

    def allowed(self, axis: str) -> tuple[str, ...]:
        if axis not in self.axes:
            raise ValueError(f"unknown semantic axis {axis!r}")
        return self.axes[axis]

    def label(self, axis: str, value: str) -> str:
        if axis not in self.labels or value not in self.labels[axis]:
            raise ValueError(f"unknown semantic label {axis}.{value}")
        return self.labels[axis][value]

    def aliases_for(self, axis: str, value: str) -> tuple[str, ...]:
        if axis not in self.aliases or value not in self.aliases[axis]:
            raise ValueError(f"unknown semantic aliases {axis}.{value}")
        return self.aliases[axis][value]


@dataclass(frozen=True)
class Service1SemanticCoordinateV2:
    """One semantic field meaning reconstructed from reusable coordinates."""

    field_ref: str
    entity: str | None = None
    object: str | None = None
    process: str | None = None
    measure: str | None = None
    state: str | None = None
    grain: str | None = None
    scope: str | None = None
    time: str | None = None
    identity: str | None = None
    relation: str | None = None
    unit: str | None = None
    aggregation: str | None = None
    confidence: float = 0.0
    evidence: tuple[str, ...] = field(default_factory=tuple)
    source: str = "C2_PROPOSAL"
    runtime_authorized: bool = False
    tool_execution_authorized: bool = False
    product_ready: bool = False
    delivery_authorized: bool = False
    automatic_reuse_authorized: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "field_ref", _text(self.field_ref, field_name="field_ref"))
        for axis in AXES:
            object.__setattr__(self, axis, _optional_text(getattr(self, axis), field_name=axis))
        try:
            confidence = float(self.confidence)
        except (TypeError, ValueError) as exc:
            raise ValueError("confidence must be between 0 and 1") from exc
        if not 0 <= confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")
        object.__setattr__(self, "confidence", confidence)
        object.__setattr__(self, "evidence", _unique_text_tuple(self.evidence, field_name="evidence"))
        object.__setattr__(self, "source", _text(self.source, field_name="source"))
        if not any(getattr(self, axis) is not None for axis in AXES):
            raise ValueError("semantic coordinate requires at least one governed axis")
        for authority_field in (
            "runtime_authorized",
            "tool_execution_authorized",
            "product_ready",
            "delivery_authorized",
            "automatic_reuse_authorized",
        ):
            if getattr(self, authority_field) is not False:
                raise ValueError(f"{authority_field} must remain False in C2")

    def validate_against(self, taxonomy: Service1SemanticCoordinateTaxonomyV2) -> "Service1SemanticCoordinateV2":
        for axis in AXES:
            value = getattr(self, axis)
            if value is not None and value not in taxonomy.allowed(axis):
                raise ValueError(f"{axis} value {value!r} is outside the governed taxonomy")
        if self.identity is not None:
            if self.entity is None:
                raise ValueError("identity semantics require an entity")
            if self.measure is not None:
                raise ValueError("identity semantics cannot simultaneously be a measure")
            if self.aggregation is not None:
                raise ValueError("identity semantics cannot carry aggregation")
        if self.aggregation is not None and self.measure is None:
            raise ValueError("aggregation semantics require a measure")
        return self

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1BusinessStructureProfileV2:
    """Structural workbook/business context; never a vertical execution switch."""

    family: str | None = None
    archetypes: tuple[str, ...] = field(default_factory=tuple)
    processes: tuple[str, ...] = field(default_factory=tuple)
    objects: tuple[str, ...] = field(default_factory=tuple)

    def validate_against(self, taxonomy: Service1SemanticCoordinateTaxonomyV2) -> "Service1BusinessStructureProfileV2":
        family = _optional_text(self.family, field_name="family")
        if family is not None and family not in taxonomy.business_families:
            raise ValueError("family is outside the governed structural taxonomy")
        archetypes = _unique_text_tuple(self.archetypes, field_name="archetypes")
        if set(archetypes) - set(taxonomy.operating_archetypes):
            raise ValueError("archetypes contain values outside the governed structural taxonomy")
        processes = _unique_text_tuple(self.processes, field_name="processes")
        if set(processes) - set(taxonomy.allowed("process")):
            raise ValueError("processes contain values outside the governed semantic taxonomy")
        objects = _unique_text_tuple(self.objects, field_name="objects")
        if set(objects) - set(taxonomy.allowed("object")):
            raise ValueError("objects contain values outside the governed semantic taxonomy")
        object.__setattr__(self, "family", family)
        object.__setattr__(self, "archetypes", archetypes)
        object.__setattr__(self, "processes", processes)
        object.__setattr__(self, "objects", objects)
        return self

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def default_service_1_semantic_coordinate_taxonomy_path_v2() -> Path:
    return (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "current"
        / "SERVICE_1_C2_SEMANTIC_COORDINATE_TAXONOMY_V2.json"
    )


def _load_service_1_semantic_coordinate_taxonomy_from_path_v2(
    taxonomy_path: Path,
) -> Service1SemanticCoordinateTaxonomyV2:
    try:
        raw = json.loads(taxonomy_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("semantic coordinate taxonomy could not be read") from exc
    if not isinstance(raw, Mapping):
        raise ValueError("semantic coordinate taxonomy root must be a mapping")
    allowed_top = {"schema_version", "status", "axes", "labels", "aliases", "business_families", "operating_archetypes"}
    if set(raw) != allowed_top:
        raise ValueError("semantic coordinate taxonomy contains missing or unknown top-level fields")
    axes_raw = raw.get("axes")
    labels_raw = raw.get("labels")
    aliases_raw = raw.get("aliases")
    if not isinstance(axes_raw, Mapping):
        raise ValueError("semantic coordinate taxonomy axes must be a mapping")
    if not isinstance(labels_raw, Mapping):
        raise ValueError("semantic coordinate taxonomy labels must be a mapping")
    if not isinstance(aliases_raw, Mapping):
        raise ValueError("semantic coordinate taxonomy aliases must be a mapping")
    return Service1SemanticCoordinateTaxonomyV2(
        schema_version=raw.get("schema_version"),
        status=raw.get("status"),
        axes={
            str(axis): tuple(values) if isinstance(values, list) else values
            for axis, values in axes_raw.items()
        },
        labels={
            str(axis): dict(values) if isinstance(values, Mapping) else values
            for axis, values in labels_raw.items()
        },
        aliases={
            str(axis): {
                str(value): tuple(items) if isinstance(items, list) else items
                for value, items in values.items()
            } if isinstance(values, Mapping) else values
            for axis, values in aliases_raw.items()
        },
        business_families=tuple(raw.get("business_families") or ()),
        operating_archetypes=tuple(raw.get("operating_archetypes") or ()),
    )


@lru_cache(maxsize=1)
def _load_default_service_1_semantic_coordinate_taxonomy_v2() -> Service1SemanticCoordinateTaxonomyV2:
    return _load_service_1_semantic_coordinate_taxonomy_from_path_v2(
        default_service_1_semantic_coordinate_taxonomy_path_v2()
    )


def load_service_1_semantic_coordinate_taxonomy_v2(
    path: str | Path | None = None,
) -> Service1SemanticCoordinateTaxonomyV2:
    if path is None:
        return _load_default_service_1_semantic_coordinate_taxonomy_v2()
    return _load_service_1_semantic_coordinate_taxonomy_from_path_v2(Path(path))


def _unique_axis_match(
    *,
    taxonomy: Service1SemanticCoordinateTaxonomyV2,
    axis: str,
    normalized: str,
) -> tuple[str | None, str | None]:
    matches: list[tuple[str, str]] = []
    for value in taxonomy.allowed(axis):
        for alias in sorted(taxonomy.aliases_for(axis, value), key=len, reverse=True):
            if _contains_token(normalized, alias):
                matches.append((value, alias))
                break
    if not matches:
        return None, None

    # Prefer the most specific governed alias. A compound business term such as
    # ``valor_hora`` must outrank the generic token ``hora`` contained inside it.
    # If two different semantic values remain tied at the same specificity, the
    # inference stays fail-closed instead of guessing.
    max_specificity = max((alias.count("_") + 1, len(alias)) for _, alias in matches)
    most_specific = [
        (value, alias)
        for value, alias in matches
        if (alias.count("_") + 1, len(alias)) == max_specificity
    ]
    unique_values = tuple(dict.fromkeys(value for value, _ in most_specific))
    if len(unique_values) != 1:
        return None, None
    value = unique_values[0]
    alias = next(alias for candidate, alias in most_specific if candidate == value)
    return value, alias


def infer_service_1_semantic_coordinate_v2(
    column_name: str,
    *,
    normalized_header: str | None = None,
    sheet_name: str | None = None,
    taxonomy: Service1SemanticCoordinateTaxonomyV2 | None = None,
) -> Service1SemanticCoordinateV2 | None:
    """Infer only uniquely evidenced V2 coordinates from governed aliases."""
    taxonomy = taxonomy or load_service_1_semantic_coordinate_taxonomy_v2()
    normalized = normalize_service_1_semantic_coordinate_text_v2(normalized_header or column_name)
    if not normalized:
        return None
    sheet_normalized = normalize_service_1_semantic_coordinate_text_v2(sheet_name or "")
    coordinates: dict[str, str | None] = {axis: None for axis in AXES}
    evidence: list[str] = [f"normalized_header: '{normalized}'"]
    direct_match_count = 0
    contextual_match_count = 0
    for axis in AXES:
        value, alias = _unique_axis_match(taxonomy=taxonomy, axis=axis, normalized=normalized)
        if value is not None:
            coordinates[axis] = value
            direct_match_count += 1
            evidence.append(f"{axis}_token: '{alias}'")
            continue
        if axis in _CONTEXTUAL_AXES and sheet_normalized:
            value, alias = _unique_axis_match(
                taxonomy=taxonomy,
                axis=axis,
                normalized=sheet_normalized,
            )
            if value is not None:
                coordinates[axis] = value
                contextual_match_count += 1
                evidence.append(f"{axis}_sheet_token: '{alias}'")
    # Deterministic inference is conservative: dependent coordinates are
    # withheld when their prerequisite meaning is not established. The strict
    # contract remains unchanged for explicit LLM/owner proposals.
    if coordinates["aggregation"] is not None and coordinates["measure"] is None:
        coordinates["aggregation"] = None
        evidence.append("aggregation_deferred_without_measure")
    if coordinates["identity"] is not None and coordinates["entity"] is None:
        coordinates["identity"] = None
        evidence.append("identity_deferred_without_entity")
    if coordinates["identity"] is not None and coordinates["measure"] is not None:
        coordinates["identity"] = None
        evidence.append("identity_deferred_due_measure_conflict")
    if not any(value is not None for value in coordinates.values()):
        return None
    confidence = min(0.98, 0.72 + direct_match_count * 0.06 + contextual_match_count * 0.03)
    field_ref = (
        f"{str(sheet_name).strip()}.{str(column_name).strip()}"
        if str(sheet_name or "").strip()
        else str(column_name).strip()
    )
    return Service1SemanticCoordinateV2(
        field_ref=field_ref,
        **coordinates,
        confidence=confidence,
        evidence=tuple(evidence),
        source="DETERMINISTIC_C2_V2",
    ).validate_against(taxonomy)


def render_service_1_semantic_coordinate_owner_proposal_v2(
    field_label: str,
    coordinate: Service1SemanticCoordinateV2,
    *,
    taxonomy: Service1SemanticCoordinateTaxonomyV2 | None = None,
) -> str:
    taxonomy = taxonomy or load_service_1_semantic_coordinate_taxonomy_v2()
    coordinate.validate_against(taxonomy)
    label = _text(field_label, field_name="field_label")
    if coordinate.identity and coordinate.entity:
        meaning = f"{taxonomy.label('identity', coordinate.identity)} de {taxonomy.label('entity', coordinate.entity)}"
    elif coordinate.time and coordinate.process:
        meaning = f"{taxonomy.label('time', coordinate.time)} de {taxonomy.label('process', coordinate.process)}"
    else:
        parts: list[str] = []
        if coordinate.measure:
            parts.append(taxonomy.label("measure", coordinate.measure))
        if coordinate.object:
            object_label = taxonomy.label("object", coordinate.object)
            parts.append(f"de {object_label}" if parts else object_label)
        if coordinate.process:
            process_label = taxonomy.label("process", coordinate.process)
            parts.append(f"en {process_label}")
        if coordinate.state:
            parts.append(f"{taxonomy.label('state', coordinate.state)}")
        if coordinate.scope:
            parts.append(taxonomy.label("scope", coordinate.scope))
        elif coordinate.grain:
            parts.append(f"por {taxonomy.label('grain', coordinate.grain)}")
        if coordinate.unit and not parts:
            parts.append(taxonomy.label("unit", coordinate.unit))
        if coordinate.entity and not parts:
            parts.append(taxonomy.label("entity", coordinate.entity))
        meaning = " ".join(parts).strip() or "un significado de negocio estructurado"
    return f"Entendí {label} como {meaning}. ¿Está bien?"


__all__ = [
    "SCHEMA_VERSION",
    "TAXONOMY_SCHEMA_VERSION",
    "TAXONOMY_STATUS_READY",
    "AXES",
    "Service1SemanticCoordinateTaxonomyV2",
    "Service1SemanticCoordinateV2",
    "Service1BusinessStructureProfileV2",
    "default_service_1_semantic_coordinate_taxonomy_path_v2",
    "load_service_1_semantic_coordinate_taxonomy_v2",
    "normalize_service_1_semantic_coordinate_text_v2",
    "infer_service_1_semantic_coordinate_v2",
    "render_service_1_semantic_coordinate_owner_proposal_v2",
]
