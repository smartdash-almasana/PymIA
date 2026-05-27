# -*- coding: utf-8 -*-
"""
Document resolver for the PymIA Telegram Bridge.

Responsibilities:
- Copy Telegram documents from Hermes cache to .runtime/telegram_documents/
- Resolve the latest Excel file for a given chat_id
- Provide structured references (DocumentRecord, ExcelRef) for downstream logic
"""

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import logging

from pymia.hermes.plugins.pymia_telegram_bridge.config import (
    TELEGRAM_DOCUMENTS_DIR,
    EXCEL_EXTENSIONS,
)


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TelegramSession:
    """
    Represents a Telegram session context.
    
    Attributes:
        tenant_id: Tenant identifier (e.g., "telegram:42")
        user_id: User identifier within the tenant
        chat_id: Telegram chat ID (unique per conversation)
        repo_root: Absolute path to the PymIA repo root
    """
    tenant_id: str
    user_id: str
    chat_id: str
    repo_root: Path

    @property
    def session_key(self) -> str:
        """Composite key: tenant_id/user_id."""
        return f"{self.tenant_id}/{self.user_id}"

    @property
    def telegram_documents_dir(self) -> Path:
        """Absolute path to .runtime/telegram_documents/."""
        return self.repo_root / TELEGRAM_DOCUMENTS_DIR


@dataclass(frozen=True)
class DocumentRecord:
    """
    Record of a document cached in .runtime/telegram_documents/.
    
    Attributes:
        runtime_path: Absolute path to the cached document
        file_name: Original file name
        chat_id: Telegram chat ID
        cached_at: Timestamp of caching (ISO format)
    """
    runtime_path: Path
    file_name: str
    chat_id: str
    cached_at: str


@dataclass(frozen=True)
class ExcelRef:
    """
    Reference to an Excel file in .runtime/telegram_documents/.
    
    Attributes:
        path: Absolute path to the Excel file
        exists: Whether the file exists on disk
        mtime: Modification time (Unix timestamp) or None if not exists
    """
    path: Path
    exists: bool
    mtime: Optional[float]


def remember_latest_document(
    session: TelegramSession,
    source_path: Path,
    file_name: str,
) -> DocumentRecord:
    """
    Copy a document from source_path to .runtime/telegram_documents/.
    
    Args:
        session: Telegram session context
        source_path: Absolute path to the source document (e.g., Hermes cache)
        file_name: Original file name
    
    Returns:
        DocumentRecord with runtime_path and metadata
    
    Raises:
        FileNotFoundError: If source_path does not exist
        PermissionError: If cannot write to .runtime/telegram_documents/
    
    Logs:
        [pymia.telegram_document] source_path=... runtime_path=... status=cached
    """
    # Ensure source exists
    source = Path(source_path)
    if not source.exists():
        raise FileNotFoundError(f"Source document not found: {source}")

    # Ensure target directory exists
    target_dir = session.telegram_documents_dir
    target_dir.mkdir(parents=True, exist_ok=True)

    # Build target path: {chat_id}_{file_name}
    target_name = f"{session.chat_id}_{file_name}"
    target_path = target_dir / target_name

    # Copy file
    shutil.copy2(source, target_path)

    # Get modification time
    mtime = target_path.stat().st_mtime
    from datetime import datetime
    cached_at = datetime.fromtimestamp(mtime).isoformat()

    # Log
    logger.info(
        "[pymia.telegram_document] "
        "source_path=%s runtime_path=%s status=cached",
        source,
        target_path,
    )

    return DocumentRecord(
        runtime_path=target_path,
        file_name=file_name,
        chat_id=session.chat_id,
        cached_at=cached_at,
    )


def resolve_latest_excel(session: TelegramSession) -> Optional[ExcelRef]:
    """
    Find the most recent Excel file for this chat_id in .runtime/telegram_documents/.
    
    Args:
        session: Telegram session context
    
    Returns:
        ExcelRef if an Excel file is found, None otherwise
    
    Logs:
        [pymia.excel] file_path=... file_exists=... latest_excel_found=...
    """
    target_dir = session.telegram_documents_dir

    # If directory doesn't exist, no Excel found
    if not target_dir.exists():
        logger.info(
            "[pymia.excel] file_path=None file_exists=false latest_excel_found=false"
        )
        return None

    # Find all Excel files for this chat_id
    pattern = f"{session.chat_id}_*"
    candidates = []
    for ext in EXCEL_EXTENSIONS:
        candidates.extend(target_dir.glob(f"{pattern}{ext}"))

    # If no candidates, no Excel found
    if not candidates:
        logger.info(
            "[pymia.excel] file_path=None file_exists=false latest_excel_found=false"
        )
        return None

    # Sort by modification time (most recent first)
    candidates_with_mtime = []
    for path in candidates:
        if path.exists():
            mtime = path.stat().st_mtime
            candidates_with_mtime.append((path, mtime))

    if not candidates_with_mtime:
        logger.info(
            "[pymia.excel] file_path=None file_exists=false latest_excel_found=false"
        )
        return None

    # Pick the most recent
    candidates_with_mtime.sort(key=lambda x: x[1], reverse=True)
    latest_path, latest_mtime = candidates_with_mtime[0]

    logger.info(
        "[pymia.excel] file_path=%s file_exists=true latest_excel_found=true",
        latest_path,
    )

    return ExcelRef(
        path=latest_path,
        exists=True,
        mtime=latest_mtime,
    )
