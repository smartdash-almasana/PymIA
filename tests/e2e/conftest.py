from __future__ import annotations

import os
from pathlib import Path

import pytest

playwright = pytest.importorskip(
    "playwright.sync_api",
    reason="Playwright is an optional e2e dependency; install with `pip install playwright` and `python -m playwright install chromium`.",
)
Browser = playwright.Browser
Page = playwright.Page
sync_playwright = playwright.sync_playwright


@pytest.fixture(scope="session")
def browser() -> Browser:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def context(browser: Browser):
    ctx = browser.new_context()
    yield ctx
    ctx.close()


@pytest.fixture
def page(context) -> Page:
    return context.new_page()


@pytest.fixture
def llm_client():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        from tests.e2e.llm_dummy import DummyLLM
        return DummyLLM()
    from anthropic import Anthropic
    return Anthropic(api_key=api_key)


@pytest.fixture
def real_xlsx_dir() -> Path:
    return Path("PymIA-Live/prueba_excels")


@pytest.fixture
def real_xlsx_files(real_xlsx_dir: Path) -> list[Path]:
    if not real_xlsx_dir.exists():
        pytest.skip(f"Real XLSX directory not available: {real_xlsx_dir}")
    files = sorted(real_xlsx_dir.glob("*.xlsx"))
    if not files:
        pytest.skip(f"No real XLSX files available in: {real_xlsx_dir}")
    return files
