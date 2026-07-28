from __future__ import annotations

import math
import json
from typing import Any

def canonical_normalize(obj: Any) -> Any:
    """
    Recursively normalizes Python objects/Pydantic model dict dumps to ensure 
    bit-to-bit equivalence for deterministic replay testing.
    """
    if isinstance(obj, dict):
        cleaned = {}
        for k, v in obj.items():
            # Exclude dynamic fields
            if k in {"generated_at", "audit_id"}:
                continue
            cleaned[k] = canonical_normalize(v)
        # Sort dict keys recursively
        return {k: cleaned[k] for k in sorted(cleaned.keys())}

    elif isinstance(obj, list):
        if not obj:
            return []
        
        normalized_list = [canonical_normalize(x) for x in obj]
        
        # Decide if we should sort this list
        # Check if the list contains elements with identifiable keys that indicate they are associative
        # Ordered elements (like priority_problems, allowed_messages) MUST NOT be sorted.
        # Associative lists that MUST be sorted:
        # - computed_metrics (by metric_id)
        # - pathology_findings (by finding_id)
        # - operational_signals (by signal_id)
        # - evidence_ids (lexicographically)
        
        try:
            first = normalized_list[0]
            if isinstance(first, dict):
                # Search for specific associative ID keys to sort by
                id_keys = {"metric_id", "finding_id", "signal_id", "question_id", "thread_id", "symptom_text", "opportunity_id"}
                matching_key = next((k for k in first.keys() if k in id_keys), None)
                if matching_key:
                    return sorted(normalized_list, key=lambda x: str(x.get(matching_key, "")))
                
                # Check if it contains sequential ordering (like "priority" or "timeframe" or "message_id" in AllowedMessage)
                # If so, do NOT sort! Let's preserve semantic priority order
                non_sort_keys = {"priority", "timeframe", "time_horizon", "message_id"}
                if any(k in first.keys() for k in non_sort_keys):
                    return normalized_list

                # Fallback: if it's an arbitrary dict list without sequential keys, sort by json representation
                return sorted(normalized_list, key=lambda x: json.dumps(x, sort_keys=True))
        except Exception:
            pass

        # If it is a list of simple types (like strings/numbers, e.g. evidence_ids, missing_evidence)
        # We sort them lexicographically
        try:
            if all(isinstance(x, (str, int, float)) or x is None for x in normalized_list):
                return sorted(normalized_list, key=lambda x: "" if x is None else str(x))
        except Exception:
            pass

        return normalized_list

    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        # Format as stable fixed string with 4 decimals of precision
        return f"{obj:.4f}"

    return obj


def assert_json_equivalence(actual: Any, expected: Any) -> None:
    """
    Applies canonical normalization to both actual and expected payloads,
    compares them, and produces a readable diff on failure.
    """
    actual_norm = canonical_normalize(actual)
    expected_norm = canonical_normalize(expected)
    
    actual_str = json.dumps(actual_norm, indent=2, ensure_ascii=False)
    expected_str = json.dumps(expected_norm, indent=2, ensure_ascii=False)
    
    assert actual_norm == expected_norm, f"JSON payloads are not canonically equivalent!\n\nACTUAL:\n{actual_str}\n\nEXPECTED:\n{expected_str}"
