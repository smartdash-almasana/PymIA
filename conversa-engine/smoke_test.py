from __future__ import annotations

from main import run_message
from tests.fixtures.owner_claims import RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY


if __name__ == "__main__":
    text = RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY
    reply = run_message(text)
    print("SMOKE_INPUT:", text)
    print("SMOKE_REPLY:", reply)
    print("SMOKE_OK:", bool(reply.strip()))
