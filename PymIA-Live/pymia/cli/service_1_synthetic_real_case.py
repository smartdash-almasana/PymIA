from __future__ import annotations

import argparse
import json
from pathlib import Path

from pymia.smartpyme.service_1_synthetic_real_owner_evidence_case_v1 import (
    run_service_1_synthetic_real_owner_evidence_case_v1,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run Servicio 1 synthetic-real owner evidence case",
    )
    parser.add_argument(
        "--output-root",
        default=".tmp/service_1_synthetic_real_case_v1",
        help="Output root for generated inputs, reentry store and case folder",
    )
    parser.add_argument(
        "--summary-json",
        default=None,
        help="Optional path to write the run summary JSON",
    )
    args = parser.parse_args(argv)

    result = run_service_1_synthetic_real_owner_evidence_case_v1(args.output_root)
    print(json.dumps(result, indent=2, ensure_ascii=False), flush=True)

    if args.summary_json:
        summary_path = Path(args.summary_json)
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    return 0 if result["exit_code"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
