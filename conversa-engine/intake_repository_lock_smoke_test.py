from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from intake_repository import DocumentIntakeRepository, IntakeRepositoryLockTimeoutError
from intake_state import DocumentIntakeState


def main() -> None:
    with TemporaryDirectory() as tmp_dir:
        repo = DocumentIntakeRepository(
            base_path=Path(tmp_dir),
            lock_timeout_seconds=0.1,
            lock_poll_interval_seconds=0.01,
        )
        session_id = "tenant:42/user?lock"

        with repo._acquire_lock(session_id):
            failed = False
            try:
                repo.save(session_id=session_id, state=DocumentIntakeState(received_events=["evt-lock"]))
            except IntakeRepositoryLockTimeoutError:
                failed = True
            assert failed, "Expected lock timeout while lock is already held"

        repo.save(session_id=session_id, state=DocumentIntakeState(received_events=["evt-ok"]))
        loaded = repo.load(session_id=session_id)
        assert loaded.received_events == ["evt-ok"]

    print("INTAKE_REPOSITORY_LOCK_SMOKE_OK:", True)


if __name__ == "__main__":
    main()

