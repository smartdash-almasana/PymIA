from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from intake_repository import DocumentIntakeRepository
from intake_state import DocumentIntakeState


def main() -> None:
    with TemporaryDirectory() as tmp_dir:
        repo = DocumentIntakeRepository(base_path=Path(tmp_dir))

        session_a = "tenant:42/user?alpha"
        session_b = "tenant_42_user_alpha"

        state_a = DocumentIntakeState(received_events=["evt-a"])
        state_b = DocumentIntakeState(received_events=["evt-b"])

        repo.save(session_id=session_a, state=state_a)
        repo.save(session_id=session_b, state=state_b)

        assert repo.load(session_id=session_a).received_events == ["evt-a"]
        assert repo.load(session_id=session_b).received_events == ["evt-b"]

        file_a = repo._session_file(session_a)  # internal check for collision hardening
        file_b = repo._session_file(session_b)
        assert file_a != file_b
        assert file_a.exists()
        assert file_b.exists()

        payload = json.loads(file_a.read_text(encoding="utf-8"))
        assert payload["schema_version"] == DocumentIntakeRepository.SCHEMA_VERSION
        assert payload["session_id"] == session_a
        assert isinstance(payload["saved_at_utc"], str)
        assert payload["state"]["received_events"] == ["evt-a"]

        assert repo.is_expired(session_id=session_a, ttl_seconds=10_000) is False
        assert repo.is_expired(session_id=session_a, ttl_seconds=0) is True

    print("INTAKE_REPOSITORY_HARDENING_SMOKE_OK:", True)


if __name__ == "__main__":
    main()

