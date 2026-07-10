"""
SERVICE_1_DUAL_PACKAGE_BOUNDARY_REPAIR_V1

Pure boundary check for the two local pymia packages. Servicio 1 active runtime
code must resolve from PymIA-Live/pymia, while the repository-root pymia package
is treated as legacy/non-runtime for Servicio 1.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

import pymia

SCHEMA_VERSION: Final[str] = "SERVICE_1_DUAL_PACKAGE_BOUNDARY_REPAIR_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"

EXPECTED_ACTIVE_PACKAGE_FLAVOR: Final[str] = "PYMIA_LIVE"
ROOT_LEGACY_PACKAGE_FLAVOR: Final[str] = "PYMIA_ROOT_LEGACY"

STATUS_BOUNDARY_READY: Final[str] = "DUAL_PACKAGE_BOUNDARY_READY"
STATUS_BLOCKED_BY_ROOT_PACKAGE: Final[str] = "DUAL_PACKAGE_BOUNDARY_BLOCKED_BY_ROOT_PACKAGE"
STATUS_BLOCKED_BY_UNKNOWN_PACKAGE: Final[str] = "DUAL_PACKAGE_BOUNDARY_BLOCKED_BY_UNKNOWN_PACKAGE"
STATUS_BLOCKED_BY_MISSING_MARKER: Final[str] = "DUAL_PACKAGE_BOUNDARY_BLOCKED_BY_MISSING_MARKER"


@dataclass(frozen=True)
class Service1DualPackageBoundaryRepairResultV1:
    schema_version: str = SCHEMA_VERSION
    service_name: str = SERVICE_NAME
    boundary_status: str = STATUS_BLOCKED_BY_UNKNOWN_PACKAGE
    active_package_name: str = "pymia"
    active_package_file: str = ""
    active_package_root: str = ""
    active_package_flavor: str = ""
    expected_active_package_flavor: str = EXPECTED_ACTIVE_PACKAGE_FLAVOR
    active_package_is_live: bool = False
    root_package_is_legacy: bool = False
    service_1_runtime_imports_allowed: bool = False
    root_package_runtime_allowed: bool = False
    runtime_authorized: bool = False
    delivery_authorized: bool = False
    product_ready: bool = False
    blocking_layer: str | None = None
    blocking_reasons: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


def build_service_1_dual_package_boundary_repair_v1(
    *,
    metadata: dict[str, Any] | None = None,
) -> Service1DualPackageBoundaryRepairResultV1:
    active_file = Path(getattr(pymia, "__file__", "") or "").resolve()
    active_root = active_file.parent if active_file.name == "__init__.py" else active_file
    active_flavor = str(getattr(pymia, "PACKAGE_FLAVOR", ""))

    base = Service1DualPackageBoundaryRepairResultV1(
        active_package_file=str(active_file),
        active_package_root=str(active_root),
        active_package_flavor=active_flavor,
        active_package_is_live=active_flavor == EXPECTED_ACTIVE_PACKAGE_FLAVOR,
        root_package_is_legacy=active_flavor == ROOT_LEGACY_PACKAGE_FLAVOR,
        service_1_runtime_imports_allowed=False,
        root_package_runtime_allowed=False,
        runtime_authorized=False,
        delivery_authorized=False,
        product_ready=False,
        metadata=dict(metadata or {}),
    )

    if not active_flavor:
        return _blocked(
            base,
            STATUS_BLOCKED_BY_MISSING_MARKER,
            "package_marker",
            ("pymia_package_flavor_marker_missing",),
        )

    if active_flavor == ROOT_LEGACY_PACKAGE_FLAVOR:
        return _blocked(
            base,
            STATUS_BLOCKED_BY_ROOT_PACKAGE,
            "root_package",
            ("root_pymia_package_cannot_host_service_1_runtime",),
        )

    if active_flavor != EXPECTED_ACTIVE_PACKAGE_FLAVOR:
        return _blocked(
            base,
            STATUS_BLOCKED_BY_UNKNOWN_PACKAGE,
            "package_marker",
            ("unexpected_pymia_package_flavor",),
        )

    if "PymIA-Live" not in {part for part in active_file.parts}:
        return _blocked(
            base,
            STATUS_BLOCKED_BY_UNKNOWN_PACKAGE,
            "package_path",
            ("active_pymia_package_must_resolve_under_pymia_live",),
        )

    return Service1DualPackageBoundaryRepairResultV1(
        **{
            **base.__dict__,
            "boundary_status": STATUS_BOUNDARY_READY,
            "active_package_is_live": True,
            "root_package_is_legacy": False,
            "service_1_runtime_imports_allowed": True,
            "root_package_runtime_allowed": False,
            "runtime_authorized": False,
            "delivery_authorized": False,
            "product_ready": False,
            "blocking_layer": None,
            "blocking_reasons": (),
            "metadata": {"rule": "active_package_is_pymia_live", **dict(metadata or {})},
        }
    )


def _blocked(
    base: Service1DualPackageBoundaryRepairResultV1,
    status: str,
    layer: str,
    reasons: tuple[str, ...],
) -> Service1DualPackageBoundaryRepairResultV1:
    return Service1DualPackageBoundaryRepairResultV1(
        **{
            **base.__dict__,
            "boundary_status": status,
            "service_1_runtime_imports_allowed": False,
            "root_package_runtime_allowed": False,
            "runtime_authorized": False,
            "delivery_authorized": False,
            "product_ready": False,
            "blocking_layer": layer,
            "blocking_reasons": reasons,
            "metadata": {"rule": reasons[0] if reasons else "blocked", **base.metadata},
        }
    )


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "EXPECTED_ACTIVE_PACKAGE_FLAVOR",
    "ROOT_LEGACY_PACKAGE_FLAVOR",
    "STATUS_BOUNDARY_READY",
    "STATUS_BLOCKED_BY_ROOT_PACKAGE",
    "STATUS_BLOCKED_BY_UNKNOWN_PACKAGE",
    "STATUS_BLOCKED_BY_MISSING_MARKER",
    "Service1DualPackageBoundaryRepairResultV1",
    "build_service_1_dual_package_boundary_repair_v1",
]
