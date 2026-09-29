"""Architecture guard for the diagnostic core runtime boundary."""

from .policy import extract_imports, get_project_root, iter_python_files


def test_diagnostic_core_does_not_import_services() -> None:
    root = get_project_root()
    diagnostic_core_dir = root / "pymia" / "diagnostic_core"

    violations: list[str] = []
    for path in iter_python_files(diagnostic_core_dir):
        for lineno, imported in extract_imports(path):
            if imported == "pymia.services" or imported.startswith("pymia.services."):
                violations.append(
                    f"{path.relative_to(root).as_posix()}:{lineno} -> {imported}"
                )

    assert not violations, "diagnostic_core must not import services:\n" + "\n".join(violations)
