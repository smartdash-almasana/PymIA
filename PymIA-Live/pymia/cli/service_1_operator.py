from __future__ import annotations

import argparse
import json
import uuid
from pathlib import Path
from typing import Any

from pymia.smartpyme.service_1_executable_entrypoint_v1 import (
    run_service_1_executable_entrypoint_v1,
)


def _infer_mime_type(filename: str) -> str | None:
    """Infer MIME type from file extension. Only XLSX is recognized."""
    ext = Path(filename).suffix.lower()
    if ext in (".xlsx", ".xlsm"):
        return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return None


def _build_file_asset(file_path: Path) -> dict[str, Any]:
    """Build FileAsset from a real file on disk."""
    asset_id = f"asset_{uuid.uuid4().hex[:12]}"
    filename = file_path.name
    declared_mime_type = _infer_mime_type(filename)
    size_bytes = file_path.stat().st_size

    return {
        "asset_id": asset_id,
        "filename": filename,
        "declared_mime_type": declared_mime_type,
        "size_bytes": size_bytes,
        "source": "path",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Service 1 operator CLI - minimal intake entrypoint",
    )
    parser.add_argument(
        "--file",
        required=True,
        help="Path to the file to process",
    )
    parser.add_argument(
        "--source-channel",
        default="cli",
        choices=["cli", "chat", "upload", "api", "unknown"],
        help="Source channel (default: cli)",
    )
    args = parser.parse_args(argv)

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: file not found: {file_path}", flush=True)
        return 2

    # Build FileAsset from real file
    asset = _build_file_asset(file_path)
    asset_id = asset["asset_id"]

    # Run the entrypoint
    packet = run_service_1_executable_entrypoint_v1(
        source_channel=args.source_channel,
        asset=asset,
    )

    # Print owner_message to stdout
    print(packet["owner_message"], flush=True)

    # Save packet JSON to .tmp/service_1_operator/<asset_id>.json
    output_dir = Path(".tmp/service_1_operator")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{asset_id}.json"
    
    # Convert packet to JSON-serializable dict
    packet_serializable = {
        "schema_version": packet["schema_version"],
        "service_name": packet["service_name"],
        "source_channel": packet["source_channel"],
        "asset": packet["asset"],
        "file_intake": packet["file_intake"],
        "taskspec_patch": packet["taskspec_patch"],
        "owner_response": packet["owner_response"],
        "owner_message": packet["owner_message"],
        "runtime_authorized": packet["runtime_authorized"],
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(packet_serializable, f, indent=2, ensure_ascii=False)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
