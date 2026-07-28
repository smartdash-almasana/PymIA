from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path
from typing import Any


JsonValue = dict[str, Any] | list[Any] | str | int | float | bool | None


def canonical_normalize(payload: JsonValue) -> JsonValue:
    """Normalize JSON payload for deterministic replay comparison.

    Rules:
    - Remove non-deterministic fields: generated_at, audit_id.
    - Keep tenant_id and all evidence/lineage/finding content.
    - Canonical dict key order.
    - Stable numeric normalization to avoid platform float artifacts.
    """

    def _norm(value: JsonValue) -> JsonValue:
        if isinstance(value, dict):
            cleaned: dict[str, JsonValue] = {}
            for key, val in value.items():
                if key in {"generated_at", "audit_id"}:
                    continue
                cleaned[key] = _norm(val)
            return {k: cleaned[k] for k in sorted(cleaned)}
        if isinstance(value, list):
            return [_norm(v) for v in value]
        if isinstance(value, float):
            if math.isnan(value) or math.isinf(value):
                return None
            return f"{value:.4f}"
        return value

    return _norm(payload)


def _list_fingerprint(values: list[Any]) -> list[str]:
    fprints: list[str] = []
    for item in values:
        if isinstance(item, dict):
            for candidate in (
                "finding_id",
                "pathology_code",
                "signal_id",
                "metric_id",
                "thread_id",
                "question_id",
                "action_id",
                "message_id",
            ):
                if candidate in item:
                    fprints.append(f"{candidate}:{item[candidate]}")
                    break
            else:
                fprints.append(json.dumps(item, ensure_ascii=False, sort_keys=True))
        else:
            fprints.append(json.dumps(item, ensure_ascii=False, sort_keys=True))
    return fprints


def assert_json_equivalence(actual: JsonValue, expected: JsonValue, *, float_tol: float = 1e-9) -> None:
    """Assert semantic JSON equivalence with replay-focused diagnostics."""

    diffs: list[str] = []

    def _cmp(a: JsonValue, e: JsonValue, path: str) -> None:
        if type(a) is not type(e):
            diffs.append(f"type drift at {path}: actual={type(a).__name__} expected={type(e).__name__}")
            return

        if isinstance(a, dict):
            a_keys = set(a.keys())
            e_keys = set(e.keys())
            missing = sorted(e_keys - a_keys)
            unexpected = sorted(a_keys - e_keys)
            if missing:
                diffs.append(f"missing fields at {path}: {missing}")
            if unexpected:
                diffs.append(f"unexpected fields at {path}: {unexpected}")
            for key in sorted(a_keys & e_keys):
                _cmp(a[key], e[key], f"{path}.{key}")
            return

        if isinstance(a, list):
            if len(a) != len(e):
                diffs.append(f"length drift at {path}: actual={len(a)} expected={len(e)}")
                return
            if a != e:
                af = _list_fingerprint(a)
                ef = _list_fingerprint(e)
                if af != ef and Counter(af) == Counter(ef):
                    diffs.append(f"ordering drift at {path}")
            for idx, (av, ev) in enumerate(zip(a, e)):
                _cmp(av, ev, f"{path}[{idx}]")
            return

        if isinstance(a, float):
            if abs(a - e) > float_tol:
                diffs.append(f"float drift at {path}: actual={a} expected={e}")
            return

        if isinstance(a, str) and isinstance(e, str):
            try:
                af = float(a)
                ef = float(e)
                if math.isfinite(af) and math.isfinite(ef):
                    if abs(af - ef) > float_tol:
                        diffs.append(f"float drift at {path}: actual={a} expected={e}")
                    return
            except ValueError:
                pass

        if a != e:
            diffs.append(f"value drift at {path}: actual={a!r} expected={e!r}")

    _cmp(actual, expected, "$")

    findings_related = [d for d in diffs if "pathology_findings" in d]
    lineage_related = [d for d in diffs if "evidence_ids" in d or "audit_trail" in d or "sheet_reports" in d]
    metric_related = [d for d in diffs if "computed_metrics" in d]

    if diffs:
        message_lines = ["JSON equivalence assertion failed."]
        if findings_related:
            message_lines.append("findings drift:")
            message_lines.extend(f"  - {d}" for d in findings_related[:20])
        if lineage_related:
            message_lines.append("lineage drift:")
            message_lines.extend(f"  - {d}" for d in lineage_related[:20])
        if metric_related:
            message_lines.append("metric drift:")
            message_lines.extend(f"  - {d}" for d in metric_related[:20])
        other = [d for d in diffs if d not in findings_related + lineage_related + metric_related]
        if other:
            message_lines.append("other drift:")
            message_lines.extend(f"  - {d}" for d in other[:40])
        raise AssertionError("\n".join(message_lines))


def load_json(path: Path) -> JsonValue:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)
