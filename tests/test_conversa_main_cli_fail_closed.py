from __future__ import annotations

import importlib.util
from pathlib import Path
from tests.fixtures.owner_claims import RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY


def _load_conversa_main():
    module_path = Path(__file__).resolve().parents[1] / "conversa-engine" / "main.py"
    spec = importlib.util.spec_from_file_location("conversa_main", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_unknown_flag_is_rejected_fail_closed():
    main = _load_conversa_main()

    exit_code, stdout, stderr = main._cli_message_from_args(["--foo"])

    assert exit_code == 1
    assert stdout == ""
    assert stderr == "COMANDO_NO_PERMITIDO: --foo"


def test_reserved_flag_is_not_implemented_without_text_fallback():
    main = _load_conversa_main()

    exit_code, stdout, stderr = main._cli_message_from_args(["--execute"])

    assert exit_code == 1
    assert stdout == ""
    assert stderr == "COMANDO_NO_IMPLEMENTADO: --execute"


def test_text_message_still_passes_through():
    main = _load_conversa_main()

    exit_code, stdout, stderr = main._cli_message_from_args(
        ["vendo", "mucho", "pero", "no", "se", "si", "gano", "plata"]
    )

    assert exit_code == 0
    assert stdout == "vendo mucho pero no se si gano plata"
    assert stderr is None


def test_empty_args_keep_default_demo_message():
    main = _load_conversa_main()

    exit_code, stdout, stderr = main._cli_message_from_args([])

    assert exit_code == 0
    assert stdout == RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY
    assert stderr is None
