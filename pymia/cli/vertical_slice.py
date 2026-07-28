from __future__ import annotations

import argparse
from pathlib import Path

from pymia.application.vertical_pipeline import (
    build_markdown,
    build_pipeline,
    build_report,
    build_structured_summary,
    has_operational_columns,
    inspect_excel,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--excel", required=True)
    parser.add_argument("--message", required=True)
    parser.add_argument("--output")
    parser.add_argument("--tenant-id", default="tenant_cli_local")
    parser.add_argument("--intake-id", default="intake_cli_local")
    parser.add_argument("--formula-id", action="append", default=[])
    parser.add_argument("--storage-dir", default=".tmp/vertical_slice_storage")
    args = parser.parse_args(argv)

    path = Path(args.excel)
    if not path.exists():
        raise FileNotFoundError(path)

    pipeline = build_pipeline(
        path,
        args.message,
        tenant_id=args.tenant_id,
        intake_id=args.intake_id,
        formula_ids=args.formula_id,
        storage_dir=Path(args.storage_dir),
    )
    markdown = pipeline["markdown"]
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
    else:
        print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
