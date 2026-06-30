from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from pymia.smartpyme.service_1_xlsx_runtime_bridge_contract_v1 import (
    build_service_1_xlsx_runtime_bridge_contract_v1,
)


def run_service_1_xlsx_runtime_bridge_entrypoint_v1(
    *,
    xlsx_path: str | Path,
    case_ref: str | None,
    operator_ref: str | None,
    controlled_operational_case_ref: str | None = None,
    sheet_name: str | None = None,
) -> dict[str, Any]:
    return build_service_1_xlsx_runtime_bridge_contract_v1(
        xlsx_path=xlsx_path,
        case_ref=case_ref,
        operator_ref=operator_ref,
        controlled_operational_case_ref=controlled_operational_case_ref,
        sheet_name=sheet_name,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--xlsx", required=True)
    parser.add_argument("--case-ref", required=True)
    parser.add_argument("--operator-ref", required=True)
    parser.add_argument("--controlled-operational-case-ref", default=None)
    parser.add_argument("--sheet-name", default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args(argv)

    result = run_service_1_xlsx_runtime_bridge_entrypoint_v1(
        xlsx_path=args.xlsx,
        case_ref=args.case_ref,
        operator_ref=args.operator_ref,
        controlled_operational_case_ref=args.controlled_operational_case_ref,
        sheet_name=args.sheet_name,
    )
    payload = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)

    return 0 if result["ready"] is True else 2


if __name__ == "__main__":
    raise SystemExit(main())
