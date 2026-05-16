from __future__ import annotations

from main import run_message


if __name__ == "__main__":
    text = "vendo mucho pero no se si gano plata"
    reply = run_message(text)
    print("SMOKE_INPUT:", text)
    print("SMOKE_REPLY:", reply)
    print("SMOKE_OK:", bool(reply.strip()))
