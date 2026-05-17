from __future__ import annotations

import base64
import json
import os
import time
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Iterator

from intake_state import DocumentIntakeState


class IntakeRepositoryLockTimeoutError(TimeoutError):
    pass


class DocumentIntakeRepository:
    SCHEMA_VERSION = 1

    def __init__(
        self,
        base_path: str | Path,
        *,
        lock_timeout_seconds: float = 2.0,
        lock_poll_interval_seconds: float = 0.05,
        stale_lock_seconds: float | None = None,
    ) -> None:
        self._base_path = Path(base_path)
        self._base_path.mkdir(parents=True, exist_ok=True)
        self._lock_timeout_seconds = lock_timeout_seconds
        self._lock_poll_interval_seconds = lock_poll_interval_seconds
        self._stale_lock_seconds = stale_lock_seconds

    def _session_file(self, session_id: str) -> Path:
        session_bytes = session_id.encode("utf-8")
        encoded_id = base64.urlsafe_b64encode(session_bytes).decode("ascii").rstrip("=")
        return self._base_path / f"{encoded_id}.json"

    def _session_lock_file(self, session_id: str) -> Path:
        return self._session_file(session_id).with_suffix(".lock")

    def _lock_payload(self, session_id: str) -> dict[str, object]:
        return {
            "pid": os.getpid(),
            "session_id": session_id,
            "created_at_utc": datetime.now(UTC).isoformat(),
        }

    def _is_stale_lock(self, lock_file: Path) -> bool:
        if self._stale_lock_seconds is None:
            return False
        try:
            raw = json.loads(lock_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return False
        created_at = raw.get("created_at_utc")
        if not isinstance(created_at, str):
            return False
        try:
            created_dt = datetime.fromisoformat(created_at)
        except ValueError:
            return False
        age_seconds = (datetime.now(UTC) - created_dt.astimezone(UTC)).total_seconds()
        return age_seconds > self._stale_lock_seconds

    def _remove_stale_lock_if_needed(self, lock_file: Path) -> None:
        if not lock_file.exists():
            return
        if not self._is_stale_lock(lock_file):
            return
        try:
            lock_file.unlink()
        except FileNotFoundError:
            pass

    @contextmanager
    def _acquire_lock(self, session_id: str, timeout_seconds: float | None = None) -> Iterator[None]:
        lock_file = self._session_lock_file(session_id)
        timeout = self._lock_timeout_seconds if timeout_seconds is None else timeout_seconds
        deadline = time.monotonic() + timeout
        lock_fd: int | None = None

        while time.monotonic() <= deadline:
            self._remove_stale_lock_if_needed(lock_file)
            try:
                lock_fd = os.open(str(lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                payload = json.dumps(self._lock_payload(session_id), ensure_ascii=False).encode("utf-8")
                os.write(lock_fd, payload)
                break
            except FileExistsError:
                time.sleep(self._lock_poll_interval_seconds)

        if lock_fd is None:
            raise IntakeRepositoryLockTimeoutError(
                f"Could not acquire intake repository lock for session_id='{session_id}' "
                f"within {timeout:.3f}s"
            )

        try:
            yield
        finally:
            try:
                os.close(lock_fd)
            except OSError:
                pass
            try:
                lock_file.unlink(missing_ok=True)
            except OSError:
                pass

    def save(self, *, session_id: str, state: DocumentIntakeState) -> None:
        with self._acquire_lock(session_id):
            target = self._session_file(session_id)
            payload = {
                "schema_version": self.SCHEMA_VERSION,
                "session_id": session_id,
                "saved_at_utc": datetime.now(UTC).isoformat(),
                "state": state.to_dict(),
            }
            with NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self._base_path,
                prefix=".tmp_intake_",
                suffix=".json",
                delete=False,
            ) as tmp:
                json.dump(payload, tmp, ensure_ascii=False, indent=2)
                temp_path = Path(tmp.name)
            temp_path.replace(target)

    def load(self, *, session_id: str) -> DocumentIntakeState:
        source = self._session_file(session_id)
        if not source.exists():
            return DocumentIntakeState()
        raw = json.loads(source.read_text(encoding="utf-8"))
        if isinstance(raw, dict) and "state" in raw:
            return DocumentIntakeState.from_dict(raw.get("state"))
        return DocumentIntakeState.from_dict(raw)

    def is_expired(self, *, session_id: str, ttl_seconds: int) -> bool:
        source = self._session_file(session_id)
        if not source.exists():
            return False
        raw = json.loads(source.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            return False
        saved_at = raw.get("saved_at_utc")
        if not isinstance(saved_at, str):
            return False
        try:
            saved_dt = datetime.fromisoformat(saved_at)
        except ValueError:
            return False
        age_seconds = (datetime.now(UTC) - saved_dt.astimezone(UTC)).total_seconds()
        return age_seconds > ttl_seconds
