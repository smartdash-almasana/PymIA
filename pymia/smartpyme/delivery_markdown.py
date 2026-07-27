"""Minimal markdown renderer for DeliveryPackage.

Pure function: no IO, no filesystem checks, no runtime execution.
"""

from __future__ import annotations

from typing import Any


def _as_dict(package: Any) -> dict:
    if isinstance(package, dict):
        return dict(package)
    if hasattr(package, "to_dict") and callable(package.to_dict):
        data = package.to_dict()
        if not isinstance(data, dict):
            raise ValueError("package.to_dict() must return dict")
        return dict(data)
    raise ValueError("package must be dict or expose to_dict()")


def _as_lines(items: list[Any], *, empty_label: str) -> str:
    if not items:
        return empty_label
    return "\n".join(f"- {item}" for item in items)


def render_delivery_markdown(package: Any) -> str:
    """Render a DeliveryPackage-like object as markdown string."""
    data = _as_dict(package)

    status = str(data.get("status", ""))
    tenant_id = str(data.get("tenant_id", ""))
    intake_id = str(data.get("intake_id", ""))
    runtime_classification = str(data.get("runtime_classification", ""))
    created_at = str(data.get("created_at", ""))
    summary = str(data.get("summary", ""))

    output_refs = list(data.get("output_refs") or [])
    warnings = list(data.get("warnings") or [])
    reasons = list(data.get("reasons") or [])

    output_refs_block = _as_lines(output_refs, empty_label="No output references.")
    warnings_block = _as_lines(warnings, empty_label="No warnings.")
    reasons_block = _as_lines(reasons, empty_label="No reasons.")

    return (
        "# Delivery Package\n\n"
        f"**Status:** {status}  \n"
        f"**Tenant:** {tenant_id}  \n"
        f"**Intake:** {intake_id}  \n"
        f"**Classification:** {runtime_classification}  \n"
        f"**Created:** {created_at}\n\n"
        "## Summary\n"
        f"{summary}\n\n"
        "## Output References\n"
        f"{output_refs_block}\n\n"
        "## Warnings\n"
        f"{warnings_block}\n\n"
        "## Reasons\n"
        f"{reasons_block}\n"
    )


__all__ = ["render_delivery_markdown"]
