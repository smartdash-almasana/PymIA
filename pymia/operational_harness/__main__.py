from __future__ import annotations

import argparse
import json
from pathlib import Path

from .harness import build_operational_status


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m pymia.operational_harness",
        description="Build deterministic operational harness status from radiography artifacts.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Pipeline Radiography output directory containing summary.json and trace.json artifacts.",
    )
    args = parser.parse_args(argv)

    output_dir = Path(args.output_dir)
    status = build_operational_status(output_dir)
    (output_dir / "harness_status.json").write_text(
        json.dumps(status, indent=2, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
