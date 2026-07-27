import ast
from pathlib import Path

import pytest

from pymia.microsaas.contracts import MicroSaaSCapability, MicroSaaSDescriptor
from pymia.microsaas.registry import (
    clear_registry,
    get_microsaas,
    list_microsaas,
    register_microsaas,
)


@pytest.fixture(autouse=True)
def _reset_registry():
    clear_registry()
    yield
    clear_registry()


def _descriptor(microsaas_id: str = "sample") -> MicroSaaSDescriptor:
    return MicroSaaSDescriptor(
        microsaas_id=microsaas_id,
        name="Sample",
        version="0.1.0",
        description="Sample descriptor",
        category="template-generation",
        enabled=True,
    )


def test_imports_contracts_and_registry():
    assert MicroSaaSDescriptor
    assert MicroSaaSCapability
    assert register_microsaas


def test_registers_and_gets_descriptor_by_id():
    descriptor = _descriptor()

    register_microsaas(descriptor)

    assert get_microsaas("sample") == descriptor


def test_lists_registered_descriptors_deterministically():
    descriptor_b = _descriptor("beta")
    descriptor_a = _descriptor("alpha")

    register_microsaas(descriptor_b)
    register_microsaas(descriptor_a)

    assert list_microsaas() == [descriptor_a, descriptor_b]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("microsaas_id", ""),
        ("version", " "),
        ("category", ""),
    ],
)
def test_descriptor_rejects_empty_required_fields(field: str, value: str):
    values = {
        "microsaas_id": "sample",
        "name": "Sample",
        "version": "0.1.0",
        "description": "Sample descriptor",
        "category": "template-generation",
        "enabled": True,
    }
    values[field] = value

    with pytest.raises(ValueError, match=field):
        MicroSaaSDescriptor(**values)


def test_capability_rejects_empty_ids():
    with pytest.raises(ValueError, match="capability_id"):
        MicroSaaSCapability("", "sample", "xlsx", "template")

    with pytest.raises(ValueError, match="microsaas_id"):
        MicroSaaSCapability("generate", "", "xlsx", "template")


def test_duplicate_registration_is_rejected():
    register_microsaas(_descriptor())

    with pytest.raises(ValueError, match="already registered"):
        register_microsaas(_descriptor())


def test_clear_registry_removes_registered_descriptors():
    register_microsaas(_descriptor())

    clear_registry()

    assert list_microsaas() == []
    assert get_microsaas("sample") is None


def test_microsaas_package_has_no_forbidden_imports():
    package_root = Path(__file__).parents[2] / "pymia" / "microsaas"
    forbidden = {"pymia.domain", "langgraph", "telegram", "hermes", "fastapi"}
    imported: set[str] = set()

    for module_path in package_root.glob("*.py"):
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)

    violations = sorted(
        name
        for name in imported
        if any(name == prefix or name.startswith(f"{prefix}.") for prefix in forbidden)
    )
    assert violations == []
