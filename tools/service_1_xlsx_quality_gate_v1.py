from __future__ import annotations

import argparse
import json
from pathlib import Path

from pymia.smartpyme.service_1_xlsx_quality_gate_v1 import (
    STATUS_PASS,
    evaluate_service_1_xlsx_quality_v1,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic P10 XLSX structural quality gate.")
    parser.add_argument("xlsx_path", type=Path)
    parser.add_argument(
        "--expected-sheet",
        action="append",
        default=[],
        dest="expected_sheets",
        help="Expected worksheet name. May be supplied multiple times.",
    )
    args = parser.parse_args()

    result = evaluate_service_1_xlsx_quality_v1(
        xlsx_path=args.xlsx_path,
        expected_sheet_names=tuple(args.expected_sheets),
    )
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    return 0 if result.verdict == STATUS_PASS else 2


if __name__ == "__main__":
    raise SystemExit(main())
