# -*- coding: utf-8 -*-
"""
Unit tests for pymia.hermes.plugins.pymia_telegram_bridge.document_resolver.

These tests validate document caching and Excel resolution logic
without touching AppData, Hermes, or Telegram.
"""

import tempfile
from pathlib import Path
from datetime import datetime
import time

import pytest

from pymia.hermes.plugins.pymia_telegram_bridge.document_resolver import (
    TelegramSession,
    DocumentRecord,
    ExcelRef,
    remember_latest_document,
    resolve_latest_excel,
)


@pytest.fixture
def temp_repo(tmp_path: Path) -> Path:
    """Create a temporary repo root with .runtime/telegram_documents/."""
    runtime_dir = tmp_path / ".runtime" / "telegram_documents"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    return tmp_path


@pytest.fixture
def session(temp_repo: Path) -> TelegramSession:
    """Create a test TelegramSession."""
    return TelegramSession(
        tenant_id="telegram:test",
        user_id="user123",
        chat_id="chat456",
        repo_root=temp_repo,
    )


def test_session_key(session: TelegramSession):
    """TelegramSession.session_key returns tenant_id/user_id."""
    assert session.session_key == "telegram:test/user123"


def test_telegram_documents_dir(session: TelegramSession):
    """TelegramSession.telegram_documents_dir points to .runtime/telegram_documents/."""
    expected = session.repo_root / ".runtime" / "telegram_documents"
    assert session.telegram_documents_dir == expected


def test_remember_latest_document_copies_file(session: TelegramSession, tmp_path: Path):
    """remember_latest_document copies source to .runtime/telegram_documents/."""
    # Create a temporary source file
    source_file = tmp_path / "source_test.xlsx"
    source_file.write_bytes(b"fake excel content")

    # Call remember_latest_document
    record = remember_latest_document(
        session=session,
        source_path=source_file,
        file_name="test.xlsx",
    )

    # Verify record
    assert isinstance(record, DocumentRecord)
    assert record.file_name == "test.xlsx"
    assert record.chat_id == "chat456"
    assert record.runtime_path.exists()
    assert record.runtime_path.name == "chat456_test.xlsx"
    assert record.runtime_path.read_bytes() == b"fake excel content"


def test_remember_latest_document_creates_directory(session: TelegramSession, tmp_path: Path):
    """remember_latest_document creates .runtime/telegram_documents/ if missing."""
    # Remove the directory
    runtime_dir = session.telegram_documents_dir
    if runtime_dir.exists():
        import shutil
        shutil.rmtree(runtime_dir)

    # Create source file
    source_file = tmp_path / "source_test2.xlsx"
    source_file.write_bytes(b"fake excel 2")

    # Call remember_latest_document
    record = remember_latest_document(
        session=session,
        source_path=source_file,
        file_name="test2.xlsx",
    )

    # Verify directory was created and file exists
    assert runtime_dir.exists()
    assert record.runtime_path.exists()


def test_remember_latest_document_raises_on_missing_source(session: TelegramSession):
    """remember_latest_document raises FileNotFoundError if source doesn't exist."""
    with pytest.raises(FileNotFoundError, match="Source document not found"):
        remember_latest_document(
            session=session,
            source_path=Path("/nonexistent/file.xlsx"),
            file_name="missing.xlsx",
        )


def test_resolve_latest_excel_finds_single_file(session: TelegramSession, tmp_path: Path):
    """resolve_latest_excel finds a single Excel file for the chat_id."""
    # Create an Excel file in .runtime/telegram_documents/
    source_file = tmp_path / "source.xlsx"
    source_file.write_bytes(b"fake excel")
    remember_latest_document(session, source_file, "report.xlsx")

    # Resolve
    ref = resolve_latest_excel(session)

    # Verify
    assert ref is not None
    assert isinstance(ref, ExcelRef)
    assert ref.exists is True
    assert ref.path.name == "chat456_report.xlsx"
    assert ref.mtime is not None


def test_resolve_latest_excel_returns_most_recent(session: TelegramSession, tmp_path: Path):
    """resolve_latest_excel returns the most recently modified Excel."""
    # Create two Excel files with different mtimes
    source1 = tmp_path / "source1.xlsx"
    source1.write_bytes(b"excel 1")
    record1 = remember_latest_document(session, source1, "old.xlsx")

    # Wait a bit to ensure different mtime
    time.sleep(0.1)

    source2 = tmp_path / "source2.xlsx"
    source2.write_bytes(b"excel 2")
    record2 = remember_latest_document(session, source2, "new.xlsx")

    # Resolve
    ref = resolve_latest_excel(session)

    # Verify it returns the newer one
    assert ref is not None
    assert ref.path.name == "chat456_new.xlsx"
    assert ref.mtime > record1.runtime_path.stat().st_mtime


def test_resolve_latest_excel_supports_multiple_extensions(session: TelegramSession, tmp_path: Path):
    """resolve_latest_excel finds .xlsx, .xls, and .csv files."""
    # Create files with different extensions
    for ext in [".xlsx", ".xls", ".csv"]:
        source = tmp_path / f"source{ext}"
        source.write_bytes(b"fake data")
        remember_latest_document(session, source, f"file{ext}")

    # Resolve (should find the most recent)
    ref = resolve_latest_excel(session)

    # Verify
    assert ref is not None
    assert ref.exists is True
    assert ref.path.suffix in [".xlsx", ".xls", ".csv"]


def test_resolve_latest_excel_returns_none_if_no_files(session: TelegramSession):
    """resolve_latest_excel returns None if no Excel files exist."""
    ref = resolve_latest_excel(session)
    assert ref is None


def test_resolve_latest_excel_returns_none_if_directory_missing(temp_repo: Path):
    """resolve_latest_excel returns None if .runtime/telegram_documents/ doesn't exist."""
    # Create session with non-existent directory
    session = TelegramSession(
        tenant_id="telegram:test",
        user_id="user123",
        chat_id="chat999",
        repo_root=temp_repo,
    )

    # Remove the directory
    import shutil
    if session.telegram_documents_dir.exists():
        shutil.rmtree(session.telegram_documents_dir)

    # Resolve
    ref = resolve_latest_excel(session)

    # Verify
    assert ref is None


def test_resolve_latest_excel_filters_by_chat_id(session: TelegramSession, tmp_path: Path):
    """resolve_latest_excel only returns files for the current chat_id."""
    # Create file for a different chat_id
    other_session = TelegramSession(
        tenant_id="telegram:test",
        user_id="user123",
        chat_id="other_chat",
        repo_root=session.repo_root,
    )
    source = tmp_path / "other.xlsx"
    source.write_bytes(b"other excel")
    remember_latest_document(other_session, source, "other.xlsx")

    # Resolve for original session
    ref = resolve_latest_excel(session)

    # Verify no file found (different chat_id)
    assert ref is None
