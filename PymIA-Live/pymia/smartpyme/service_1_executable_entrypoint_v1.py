from __future__ import annotations

from typing import TypedDict

from pymia.smartpyme.file_intake_taskspec_boundary_v1 import TaskSpecPatch
from pymia.smartpyme.file_intake_v1 import FileAsset, FileIntakeResult, SourceChannel, classify_file_intake
from pymia.smartpyme.owner_message_formatter_v1 import format_owner_message_v1
from pymia.smartpyme.owner_response_renderer_v1 import OwnerResponseV1, render_owner_response_v1

SCHEMA_VERSION = "1.0"
SERVICE_NAME = "SERVICE_1"


class Service1ExecutablePacket(TypedDict):
    schema_version: str
    service_name: str
    source_channel: SourceChannel
    asset: dict
    file_intake: FileIntakeResult
    taskspec_patch: TaskSpecPatch
    owner_response: OwnerResponseV1
    owner_message: str
    runtime_authorized: bool


def run_service_1_executable_entrypoint_v1(
    *,
    source_channel: SourceChannel,
    asset: FileAsset,
    file_intake_id: str | None = None,
) -> Service1ExecutablePacket:
    """Execute the minimal Service 1 entrypoint chain.

    Chain:
        FileAsset
        → classify_file_intake(...)
        → derive_taskspec_patch_from_file_intake(...)
        → render_owner_response_v1(...)
        → format_owner_message_v1(...)

    Returns a packet with runtime_authorized = False (always).
    Does not execute pipeline, FSM, reentry, persistence, or LLM calls.
    """
    # Import boundary modules only (no pipeline, FSM, reentry, LLM)
    from pymia.smartpyme.file_intake_taskspec_boundary_v1 import derive_taskspec_patch_from_file_intake

    # Generate file_intake_id if not provided
    intake_id = file_intake_id or f"intake_{asset.get('asset_id', 'unknown')}"

    # Step 1: classify_file_intake
    file_intake = classify_file_intake(
        file_intake_id=intake_id,
        asset=asset,
        source_channel=source_channel,
    )

    # Step 2: derive_taskspec_patch_from_file_intake
    taskspec_patch = derive_taskspec_patch_from_file_intake(file_intake)

    # Step 3: render_owner_response_v1
    owner_response = render_owner_response_v1(file_intake, taskspec_patch)

    # Step 4: format_owner_message_v1
    owner_message = format_owner_message_v1(owner_response)

    # Return packet with runtime_authorized = False (invariant)
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "source_channel": source_channel,
        "asset": dict(asset),
        "file_intake": file_intake,
        "taskspec_patch": taskspec_patch,
        "owner_response": owner_response,
        "owner_message": owner_message,
        "runtime_authorized": False,
    }
