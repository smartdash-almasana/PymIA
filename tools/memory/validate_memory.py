from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

REQUIRED_MEMORY_FILES = (
    "_contexto_global.md",
    "_estado_actual.md",
    "_decisiones_vigentes.md",
    "_no_volver_a_hacer.md",
    "_task_actual.md",
)

_MAX_FILE_SIZE = 16_000
_WARN_GROWTH_SIZE = 12_000
_MIN_FILE_SIZE = 120
_GROWTH_WARNING_FILES = {
    "_contexto_global.md",
    "_decisiones_vigentes.md",
    "_no_volver_a_hacer.md",
}


@dataclass(slots=True)
class MemoryValidationResult:
    ok: bool
    memory_root: str
    checked_files: list[str]
    errors: list[str]
    warnings: list[str]


def default_memory_root(repo_root: str | Path | None = None) -> Path:
    base = Path(repo_root) if repo_root is not None else Path.cwd()
    base = base.resolve()

    candidates = (
        base.parent / "Pymia-memoria",
        base / "Pymia-memoria",
        base / "memoria-obsidian",
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def validate_memory(memory_root: str | Path) -> MemoryValidationResult:
    root = Path(memory_root)
    errors: list[str] = []
    warnings: list[str] = []
    checked_files: list[str] = []

    if not root.exists():
        errors.append(f"Memory root does not exist: {root}")
        return MemoryValidationResult(False, str(root), checked_files, errors, warnings)

    if not root.is_dir():
        errors.append(f"Memory root is not a directory: {root}")
        return MemoryValidationResult(False, str(root), checked_files, errors, warnings)

    for filename in REQUIRED_MEMORY_FILES:
        file_path = root / filename
        checked_files.append(str(file_path))

        if not file_path.exists():
            errors.append(f"Missing memory file: {filename}")
            continue

        if not file_path.is_file():
            errors.append(f"Memory path is not a file: {filename}")
            continue

        size = file_path.stat().st_size
        if size <= _MIN_FILE_SIZE:
            errors.append(
                f"Memory file too small ({size} bytes <= {_MIN_FILE_SIZE}): {filename}"
            )

        if size > _MAX_FILE_SIZE:
            warnings.append(
                f"Memory file exceeds {_MAX_FILE_SIZE} bytes ({size}): {filename}"
            )

        if filename in _GROWTH_WARNING_FILES and size > _WARN_GROWTH_SIZE:
            warnings.append(
                f"Memory file above growth threshold {_WARN_GROWTH_SIZE} bytes ({size}): {filename}"
            )

    estado_path = root / "_estado_actual.md"
    if estado_path.is_file():
        estado_content = estado_path.read_text(encoding="utf-8")
        if "Estado" not in estado_content:
            errors.append("_estado_actual.md must contain 'Estado'")

    task_path = root / "_task_actual.md"
    if task_path.is_file():
        task_content = task_path.read_text(encoding="utf-8")
        if "Tarea" not in task_content and "tarea" not in task_content:
            errors.append("_task_actual.md must contain 'Tarea' or 'tarea'")

    return MemoryValidationResult(
        ok=not errors,
        memory_root=str(root),
        checked_files=checked_files,
        errors=errors,
        warnings=warnings,
    )


def main() -> int:
    memory_root = default_memory_root()
    result = validate_memory(memory_root)

    print(f"memory_root={result.memory_root}")
    print(f"ok={result.ok}")

    for message in result.errors:
        print(f"ERROR: {message}")

    for message in result.warnings:
        print(f"WARNING: {message}")

    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
