from __future__ import annotations

import json
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

from intake_repository import DocumentIntakeRepository
from intake_state import DocumentIntakeState


def main() -> None:
    with TemporaryDirectory() as tmp_dir:
        repo = DocumentIntakeRepository(
            base_path=Path(tmp_dir),
            stale_lock_seconds=0.1,
            lock_timeout_seconds=0.2,
            lock_poll_interval_seconds=0.01,
        )

        session_id = "tenant:42/user:stale"
        lock_file = repo._session_lock_file(session_id)

        stale_payload = {
            "pid": 999999,
            "session_id": session_id,
            "created_at_utc": (datetime.now(UTC) - timedelta(seconds=5)).isoformat(),
        }

        lock_file.write_text(json.dumps(stale_payload), encoding="utf-8")

        repo.save(
            session_id=session_id,
            state=DocumentIntakeState(received_events=["evt-stale-ok"]),
        )

        loaded = repo.load(session_id=session_id)
        assert loaded.received_events == ["evt-stale-ok"]

        assert not lock_file.exists(), "Expected stale lock cleanup after save"

    print("INTAKE_REPOSITORY_STALE_LOCK_SMOKE_OK:", True)


if __name__ == "__main__":
    main()
