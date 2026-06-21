"""Compatibility shim for the canonical PymIA-Live document ingestion module.

Canonical implementation:
    PymIA-Live/tools/document_ingestion.py

This root-level module exists because older tests and modules import
`tools.document_ingestion` from the repository root. To avoid divergent copies,
it loads and re-exports the canonical PymIA-Live implementation.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any


_REPO_ROOT = Path(__file__).resolve().parents[1]
_PYMIA_LIVE_ROOT = _REPO_ROOT / "PymIA-Live"
_CANONICAL_PATH = _PYMIA_LIVE_ROOT / "tools" / "document_ingestion.py"
_CANONICAL_MODULE_NAME = "_pymia_live_tools_document_ingestion"


def _load_canonical_module() -> ModuleType:
    # Make PymIA-Live contract modules visible without shadowing the root `pymia` package.
    import pymia
    live_pymia_path = str(_PYMIA_LIVE_ROOT / "pymia")
    if live_pymia_path not in pymia.__path__:
        pymia.__path__.append(live_pymia_path)

    import pymia.contracts
    live_contracts_path = str(_PYMIA_LIVE_ROOT / "pymia" / "contracts")
    if live_contracts_path not in pymia.contracts.__path__:
        pymia.contracts.__path__.append(live_contracts_path)

    import pymia.smartpyme
    root_smartpyme_path = str(_REPO_ROOT / "pymia" / "smartpyme")
    live_smartpyme_path = str(_PYMIA_LIVE_ROOT / "pymia" / "smartpyme")
    if root_smartpyme_path not in pymia.smartpyme.__path__:
        pymia.smartpyme.__path__.insert(0, root_smartpyme_path)
    if live_smartpyme_path not in pymia.smartpyme.__path__:
        pymia.smartpyme.__path__.append(live_smartpyme_path)

    # Make canonical PymIA-Live tool subpackages preferred for imports made by the live module.
    import tools
    live_tools_path = str(_PYMIA_LIVE_ROOT / "tools")
    if live_tools_path not in tools.__path__:
        tools.__path__.insert(0, live_tools_path)

    if not _CANONICAL_PATH.exists():
        raise ImportError(f"Canonical document_ingestion module not found: {_CANONICAL_PATH}")

    existing = sys.modules.get(_CANONICAL_MODULE_NAME)
    if existing is not None:
        return existing

    spec = importlib.util.spec_from_file_location(_CANONICAL_MODULE_NAME, _CANONICAL_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load canonical document_ingestion module: {_CANONICAL_PATH}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[_CANONICAL_MODULE_NAME] = module
    spec.loader.exec_module(module)
    return module


_canonical = _load_canonical_module()

for _name, _value in vars(_canonical).items():
    if _name in {"__name__", "__file__", "__package__", "__loader__", "__spec__", "__cached__"}:
        continue
    globals()[_name] = _value


__all__ = [
    name
    for name in globals()
    if not name.startswith("__")
    and name not in {
        "Any",
        "ModuleType",
        "Path",
        "importlib",
        "sys",
        "_CANONICAL_PATH",
        "_CANONICAL_MODULE_NAME",
        "_canonical",
        "_load_canonical_module",
    }
]
