from __future__ import annotations

import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from pymia.smartpyme import service_1_assisted_web_v1 as web
from pymia.smartpyme.service_1_assisted_web_v1 import AssistedWebApplicationV1


def test_same_session_lock_serializes_overlapping_work(tmp_path: Path) -> None:
    app = AssistedWebApplicationV1(output_dir=tmp_path / "outputs")
    active = 0
    max_active = 0
    counter_guard = threading.Lock()
    start = threading.Barrier(2)

    def work() -> None:
        nonlocal active, max_active
        start.wait(timeout=2)
        with app.session_lock("same-session"):
            with counter_guard:
                active += 1
                max_active = max(max_active, active)
            time.sleep(0.05)
            with counter_guard:
                active -= 1

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(work) for _ in range(2)]
        for future in futures:
            future.result(timeout=2)

    assert max_active == 1


def test_different_sessions_do_not_share_the_same_lock(tmp_path: Path) -> None:
    app = AssistedWebApplicationV1(output_dir=tmp_path / "outputs")
    lock_a = app.session_lock("session-a")
    lock_b = app.session_lock("session-b")
    assert lock_a is not lock_b
    assert app.session_lock("session-a") is lock_a


def test_oversized_upload_is_rejected_before_body_read() -> None:
    class Body:
        def read(self, _length: int) -> bytes:
            raise AssertionError("oversized body must not be read")

    class Handler:
        headers = {
            "Content-Type": "multipart/form-data; boundary=x",
            "Content-Length": str(40 * 1024 * 1024 + 1),
        }
        rfile = Body()

    with pytest.raises(ValueError, match="invalid upload size"):
        web._multipart_form(Handler())
