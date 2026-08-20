from __future__ import annotations

import json
from pathlib import Path


def test_excel_mcp_qa_local_config_is_optional_and_safe_when_present() -> None:
    repo = Path(__file__).resolve().parents[2]
    gitignore = (repo / ".gitignore").read_text(encoding="utf-8")
    assert ".opencode/" in gitignore

    config_path = repo / ".opencode" / "opencode.json"
    if not config_path.exists():
        return

    config = json.loads(config_path.read_text(encoding="utf-8"))
    server = config["mcp"]["excel_qa"]
    assert server["type"] == "local"
    assert server["command"] == ["npx", "--yes", "@negokaz/excel-mcp-server"]
    assert server["enabled"] is False
    assert server["environment"]["EXCEL_MCP_PAGING_CELLS_LIMIT"] == "4000"
    assert config["permission"]["excel_qa_*"] == "ask"


def test_product_runtime_does_not_import_excel_mcp_dependency() -> None:
    repo = Path(__file__).resolve().parents[2]
    productive_files = (
        repo / "pymia" / "smartpyme" / "service_1_product_pipeline_v1.py",
        repo / "pymia" / "smartpyme" / "service_1_computability_v1.py",
        repo / "pymia" / "smartpyme" / "service_1_xlsx_delivery_v1.py",
    )
    combined = "\n".join(path.read_text(encoding="utf-8").lower() for path in productive_files)

    assert "excel-mcp-server" not in combined
    assert "negokaz" not in combined
    assert "npx" not in combined
