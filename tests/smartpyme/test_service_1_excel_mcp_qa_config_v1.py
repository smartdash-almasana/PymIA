from __future__ import annotations

import json
from pathlib import Path


def test_excel_mcp_qa_is_registered_but_disabled_by_default() -> None:
    repo = Path(__file__).resolve().parents[2]
    config = json.loads((repo / ".opencode" / "opencode.json").read_text(encoding="utf-8"))

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
