from __future__ import annotations

import pytest

from .performance_support import write_report


@pytest.fixture(scope="session", autouse=True)
def write_performance_baseline_report() -> None:
    yield
    write_report()
