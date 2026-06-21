from __future__ import annotations

from typing import Final, Literal

TaskSpecBlockingState = Literal[
    "BLOCKED_MISSING_EVIDENCE",
    "BLOCKED_UNSUPPORTED_FILE_TYPE",
    "BLOCKED_UNKNOWN_FILE_TYPE",
    "BLOCKED_UNSAFE_FILE",
    "BLOCKED_COLUMN_CONFIRMATION",
    "BLOCKED_RUNTIME_NOT_AUTHORIZED",
]

TaskSpecNextAllowedAction = Literal[
    "send_to_xlsx_document_ingestion",
    "ask_owner_to_upload_xlsx",
    "ask_owner_for_clearer_file",
    "ask_owner_to_confirm_columns_after_curation",
    "block_runtime_until_supported",
]

EvidenceAssetStatus = Literal[
    "RECEIVED_SUPPORTED",
    "REJECTED_UNSUPPORTED",
    "REJECTED_UNKNOWN",
    "REJECTED_UNSAFE",
]

SERVICE_1_TASKSPEC_ALLOWED_BLOCKING_STATES: Final[tuple[TaskSpecBlockingState, ...]] = (
    "BLOCKED_MISSING_EVIDENCE",
    "BLOCKED_UNSUPPORTED_FILE_TYPE",
    "BLOCKED_UNKNOWN_FILE_TYPE",
    "BLOCKED_UNSAFE_FILE",
    "BLOCKED_COLUMN_CONFIRMATION",
    "BLOCKED_RUNTIME_NOT_AUTHORIZED",
)

SERVICE_1_TASKSPEC_ALLOWED_NEXT_ACTIONS: Final[tuple[TaskSpecNextAllowedAction, ...]] = (
    "send_to_xlsx_document_ingestion",
    "ask_owner_to_upload_xlsx",
    "ask_owner_for_clearer_file",
    "ask_owner_to_confirm_columns_after_curation",
    "block_runtime_until_supported",
)

SERVICE_1_EVIDENCE_ASSET_STATUSES: Final[tuple[EvidenceAssetStatus, ...]] = (
    "RECEIVED_SUPPORTED",
    "REJECTED_UNSUPPORTED",
    "REJECTED_UNKNOWN",
    "REJECTED_UNSAFE",
)

