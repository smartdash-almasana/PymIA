from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from intake_repository import DocumentIntakeRepository
from intake_state import DocumentIntakeState


def main() -> None:
    with TemporaryDirectory() as tmp_dir:
        repo = DocumentIntakeRepository(base_path=Path(tmp_dir))
        session_id = "tenant42_user42"

        state = DocumentIntakeState()
        state.received_events.extend(["evt-1", "evt-2"])
        state.received_files.append("facturas.pdf")
        state.require_evidence("ventas_pos")

        repo.save(session_id=session_id, state=state)
        loaded = repo.load(session_id=session_id)

        assert loaded.received_events == ["evt-1", "evt-2"]
        assert loaded.received_files == ["facturas.pdf"]
        assert loaded.missing_evidence == ["ventas_pos"]

        empty = repo.load(session_id="missing-session")
        assert empty.received_events == []
        assert empty.received_files == []
        assert empty.missing_evidence == []

    print("INTAKE_REPOSITORY_SMOKE_OK:", True)


if __name__ == "__main__":
    main()

