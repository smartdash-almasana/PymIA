from __future__ import annotations

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from document_intake import intake_document


def main() -> None:
    result = intake_document(
        tenant_id="telegram:42",
        user_id="42",
        file_path="/tmp/stock_control.xlsx",
        file_name="stock_control.xlsx",
        mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        expected_schema="unknown",
        entropy_level=0.5,
    )
    assert "Ruta asignada: BEM_AI" in result
    assert "no confirma ninguna patología" in result
    print("DOCUMENT_INTAKE_SMOKE_OK:", True)


if __name__ == "__main__":
    main()
