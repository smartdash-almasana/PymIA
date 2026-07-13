from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Literal, TypedDict

CAPABILITY_REF = "service_1_bank_reconciliation_sandbox_fixture_model_v1"

Status = Literal[
    "VALID",
    "MISSING_BANK_STATEMENT_FIXTURE",
    "MISSING_INTERNAL_LEDGER_FIXTURE",
    "INVALID_MOVEMENT",
    "DUPLICATE_MOVEMENT_REF",
    "BLOCKED_LIVE_SOURCE",
    "INVALID_INPUT",
]

MovementKind = Literal["bank", "ledger"]


class MovementFixtureV1(TypedDict):
    movement_ref: str
    date: str
    amount: str
    description: str


class BankStatementFixtureV1(TypedDict):
    fixture_id: str
    source_ref: str
    period_ref: str
    currency: str
    movements: list[MovementFixtureV1]
    live_source: bool


class InternalLedgerFixtureV1(TypedDict):
    fixture_id: str
    source_ref: str
    period_ref: str
    currency: str
    movements: list[MovementFixtureV1]
    live_source: bool


class FixtureBundleInputV1(TypedDict):
    bank_statement_fixture: BankStatementFixtureV1 | None
    internal_ledger_fixture: InternalLedgerFixtureV1 | None


class FixtureBundleResultV1(TypedDict):
    capability_ref: str
    status: Status
    runtime_authorized: Literal[False]
    production_allowed: Literal[False]
    valid_for_sandbox_contract: bool
    bank_statement_fixture_id: str | None
    internal_ledger_fixture_id: str | None
    period_ref: str | None
    currency: str | None
    bank_movement_count: int
    ledger_movement_count: int
    missing_inputs: list[str]
    reasons: list[str]
    handoff_refs: list[str]


def build_bank_reconciliation_sandbox_fixture_model_v1(*, bundle_input: FixtureBundleInputV1) -> FixtureBundleResultV1:
    if not isinstance(bundle_input, dict):
        return _result("INVALID_INPUT", None, None, None, None, 0, 0, ["bundle_input"], ["Invalid bundle input."], [])

    bank_fixture = bundle_input.get("bank_statement_fixture")
    ledger_fixture = bundle_input.get("internal_ledger_fixture")

    if not isinstance(bank_fixture, dict):
        return _result(
            "MISSING_BANK_STATEMENT_FIXTURE",
            None,
            _fixture_id(ledger_fixture),
            _period_ref(ledger_fixture),
            _currency(ledger_fixture),
            0,
            _movement_count(ledger_fixture),
            ["bank_statement_fixture"],
            ["Bank statement fixture is missing."],
            _handoff_refs(bank_fixture, ledger_fixture),
        )
    if not isinstance(ledger_fixture, dict):
        return _result(
            "MISSING_INTERNAL_LEDGER_FIXTURE",
            _fixture_id(bank_fixture),
            None,
            _period_ref(bank_fixture),
            _currency(bank_fixture),
            _movement_count(bank_fixture),
            0,
            ["internal_ledger_fixture"],
            ["Internal ledger fixture is missing."],
            _handoff_refs(bank_fixture, ledger_fixture),
        )

    if bank_fixture.get("live_source") is True or ledger_fixture.get("live_source") is True:
        return _result(
            "BLOCKED_LIVE_SOURCE",
            _fixture_id(bank_fixture),
            _fixture_id(ledger_fixture),
            _shared_or_first_period(bank_fixture, ledger_fixture),
            _shared_or_first_currency(bank_fixture, ledger_fixture),
            _movement_count(bank_fixture),
            _movement_count(ledger_fixture),
            [],
            ["Live sources are blocked for sandbox fixtures."],
            _handoff_refs(bank_fixture, ledger_fixture),
        )

    invalid_reason = _first_invalid_movement_reason(bank_fixture, "bank") or _first_invalid_movement_reason(ledger_fixture, "ledger")
    if invalid_reason:
        return _result(
            "INVALID_MOVEMENT",
            _fixture_id(bank_fixture),
            _fixture_id(ledger_fixture),
            _shared_or_first_period(bank_fixture, ledger_fixture),
            _shared_or_first_currency(bank_fixture, ledger_fixture),
            _movement_count(bank_fixture),
            _movement_count(ledger_fixture),
            [],
            [invalid_reason],
            _handoff_refs(bank_fixture, ledger_fixture),
        )

    duplicate_ref = _first_duplicate_movement_ref(bank_fixture, ledger_fixture)
    if duplicate_ref:
        return _result(
            "DUPLICATE_MOVEMENT_REF",
            _fixture_id(bank_fixture),
            _fixture_id(ledger_fixture),
            _shared_or_first_period(bank_fixture, ledger_fixture),
            _shared_or_first_currency(bank_fixture, ledger_fixture),
            _movement_count(bank_fixture),
            _movement_count(ledger_fixture),
            [],
            [f"Duplicate movement_ref: {duplicate_ref}."],
            _handoff_refs(bank_fixture, ledger_fixture),
        )

    return _result(
        "VALID",
        _fixture_id(bank_fixture),
        _fixture_id(ledger_fixture),
        _shared_or_first_period(bank_fixture, ledger_fixture),
        _shared_or_first_currency(bank_fixture, ledger_fixture),
        _movement_count(bank_fixture),
        _movement_count(ledger_fixture),
        [],
        ["Fixture bundle is valid for sandbox contract handoff only."],
        _handoff_refs(bank_fixture, ledger_fixture),
    )


def _result(
    status: Status,
    bank_statement_fixture_id: str | None,
    internal_ledger_fixture_id: str | None,
    period_ref: str | None,
    currency: str | None,
    bank_movement_count: int,
    ledger_movement_count: int,
    missing_inputs: list[str],
    reasons: list[str],
    handoff_refs: list[str],
) -> FixtureBundleResultV1:
    return {
        "capability_ref": CAPABILITY_REF,
        "status": status,
        "runtime_authorized": False,
        "production_allowed": False,
        "valid_for_sandbox_contract": status == "VALID",
        "bank_statement_fixture_id": bank_statement_fixture_id,
        "internal_ledger_fixture_id": internal_ledger_fixture_id,
        "period_ref": period_ref,
        "currency": currency,
        "bank_movement_count": bank_movement_count,
        "ledger_movement_count": ledger_movement_count,
        "missing_inputs": missing_inputs,
        "reasons": reasons,
        "handoff_refs": handoff_refs,
    }


def _fixture_id(fixture: object) -> str | None:
    if not isinstance(fixture, dict):
        return None
    return _clean_text(fixture.get("fixture_id"))


def _period_ref(fixture: object) -> str | None:
    if not isinstance(fixture, dict):
        return None
    return _clean_text(fixture.get("period_ref"))


def _currency(fixture: object) -> str | None:
    if not isinstance(fixture, dict):
        return None
    return _clean_text(fixture.get("currency"))


def _movement_count(fixture: object) -> int:
    if not isinstance(fixture, dict):
        return 0
    movements = fixture.get("movements")
    return len(movements) if isinstance(movements, list) else 0


def _shared_or_first_period(bank_fixture: dict[str, object], ledger_fixture: dict[str, object]) -> str | None:
    bank_period = _period_ref(bank_fixture)
    ledger_period = _period_ref(ledger_fixture)
    if bank_period and ledger_period and bank_period == ledger_period:
        return bank_period
    return bank_period or ledger_period


def _shared_or_first_currency(bank_fixture: dict[str, object], ledger_fixture: dict[str, object]) -> str | None:
    bank_currency = _currency(bank_fixture)
    ledger_currency = _currency(ledger_fixture)
    if bank_currency and ledger_currency and bank_currency == ledger_currency:
        return bank_currency
    return bank_currency or ledger_currency


def _first_invalid_movement_reason(fixture: dict[str, object], kind: MovementKind) -> str | None:
    fixture_id = _fixture_id(fixture) or f"{kind}_fixture"
    movements = fixture.get("movements")
    if not isinstance(movements, list):
        return f"{fixture_id} movements must be a list."
    for index, movement in enumerate(movements):
        if not isinstance(movement, dict):
            return f"{fixture_id} movement {index} must be an object."
        if not _clean_text(movement.get("movement_ref")):
            return f"{fixture_id} movement {index} missing movement_ref."
        if not _clean_text(movement.get("date")):
            return f"{fixture_id} movement {index} missing date."
        amount = _clean_text(movement.get("amount"))
        if not amount:
            return f"{fixture_id} movement {index} missing amount."
        if not _is_decimal_text(amount):
            return f"{fixture_id} movement {index} has invalid amount."
        if not _clean_text(movement.get("description")):
            return f"{fixture_id} movement {index} missing description."
    return None


def _first_duplicate_movement_ref(bank_fixture: dict[str, object], ledger_fixture: dict[str, object]) -> str | None:
    seen: set[str] = set()
    for fixture in (bank_fixture, ledger_fixture):
        movements = fixture.get("movements")
        if not isinstance(movements, list):
            continue
        for movement in movements:
            if not isinstance(movement, dict):
                continue
            movement_ref = _clean_text(movement.get("movement_ref"))
            if not movement_ref:
                continue
            if movement_ref in seen:
                return movement_ref
            seen.add(movement_ref)
    return None


def _handoff_refs(bank_fixture: object, ledger_fixture: object) -> list[str]:
    refs: list[str] = []
    bank_id = _fixture_id(bank_fixture)
    ledger_id = _fixture_id(ledger_fixture)
    if bank_id:
        refs.append("bank_statement_fixture")
    if ledger_id:
        refs.append("internal_ledger_fixture")
    return refs


def _clean_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _is_decimal_text(value: str) -> bool:
    try:
        Decimal(value)
    except InvalidOperation:
        return False
    return True
