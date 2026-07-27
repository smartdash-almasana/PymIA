from __future__ import annotations

from pathlib import Path

from tools.memory.validate_memory import (
    REQUIRED_MEMORY_FILES,
    default_memory_root,
    main,
    validate_memory,
)


def _write_file(path: Path, size: int, content: str = "X") -> None:
    path.write_text(content * size, encoding="utf-8")


def _create_valid_memory_dir(base: Path) -> Path:
    base.mkdir(parents=True, exist_ok=True)
    for filename in REQUIRED_MEMORY_FILES:
        target = base / filename
        if filename == "_estado_actual.md":
            target.write_text("Estado actual\n" + ("A" * 200), encoding="utf-8")
        elif filename == "_task_actual.md":
            target.write_text("Tarea en curso\n" + ("B" * 200), encoding="utf-8")
        else:
            target.write_text("C" * 300, encoding="utf-8")
    return base


def test_closed_memory_contract_validates_explicit_fixture(tmp_path: Path):
    memory_root = _create_valid_memory_dir(tmp_path / "Pymia-memoria")

    result = validate_memory(memory_root)

    assert result.ok is True
    assert result.errors == []


def test_default_memory_root_does_not_create_external_memory(tmp_path: Path):
    repo_root = tmp_path / "PymIA"
    repo_root.mkdir()

    memory_root = default_memory_root(repo_root)

    assert memory_root.is_absolute()
    assert memory_root.name == "Pymia-memoria"
    assert memory_root == tmp_path / "Pymia-memoria"
    assert not memory_root.exists()


def test_validate_memory_detects_missing_file(tmp_path: Path):
    for filename in REQUIRED_MEMORY_FILES[:-1]:
        target = tmp_path / filename
        if filename == "_estado_actual.md":
            target.write_text("Estado\n" + ("A" * 200), encoding="utf-8")
        else:
            target.write_text("X" * 300, encoding="utf-8")

    result = validate_memory(tmp_path)

    assert result.ok is False
    assert any("Missing memory file" in err for err in result.errors)


def test_validate_memory_warns_large_file(tmp_path: Path):
    _create_valid_memory_dir(tmp_path)
    _write_file(tmp_path / "_contexto_global.md", 16_100)

    result = validate_memory(tmp_path)

    assert result.ok is True
    assert result.warnings


def test_cli_validate_memory_passes(tmp_path: Path, monkeypatch):
    memory_dir = _create_valid_memory_dir(tmp_path / "Pymia-memoria")
    monkeypatch.chdir(tmp_path)

    exit_code = main()

    assert memory_dir.exists()
    assert exit_code == 0
