"""Accounting knowledge patterns extracted from OCA/spreadsheet documentation.

These definitions translate portable business semantics into native PymIA
knowledge specs. They do not depend on Odoo and are not runtime-authorizing.
"""
from __future__ import annotations

from pymia.business_knowledge.contracts_v1 import (
    EvidenceFieldV1,
    KnowledgePackV1,
    OperationalKnowledgeSpecV1,
)

_SOURCE = "OCA/spreadsheet@18.0:spreadsheet_oca/readme/USAGE.md"

ACCOUNT_CREDIT_TOTAL = OperationalKnowledgeSpecV1(
    knowledge_ref="account_credit_total",
    domain="accounting",
    family="ledger",
    kind="METRIC",
    status="CANDIDATE",
    inputs=(
        EvidenceFieldV1("account_code", "accounting_account_code"),
        EvidenceFieldV1("posting_date", "accounting_posting_date", "date"),
        EvidenceFieldV1("credit_amount", "accounting_credit_amount", "currency"),
    ),
    expression="SUM(credit_amount) FILTER account_code IN selected_accounts AND posting_date IN selected_period",
    output_key="credit_total",
    output_unit="currency",
    validations=(
        "selected account codes must be explicit",
        "selected period must be explicit",
        "currency must be normalized before aggregation",
    ),
    interpretation_limits=(
        "credit total alone does not establish revenue, cash inflow or financial health",
        "account semantics must be known before interpreting the aggregate",
    ),
    provenance=(_SOURCE,),
)

ACCOUNT_DEBIT_TOTAL = OperationalKnowledgeSpecV1(
    knowledge_ref="account_debit_total",
    domain="accounting",
    family="ledger",
    kind="METRIC",
    status="CANDIDATE",
    inputs=(
        EvidenceFieldV1("account_code", "accounting_account_code"),
        EvidenceFieldV1("posting_date", "accounting_posting_date", "date"),
        EvidenceFieldV1("debit_amount", "accounting_debit_amount", "currency"),
    ),
    expression="SUM(debit_amount) FILTER account_code IN selected_accounts AND posting_date IN selected_period",
    output_key="debit_total",
    output_unit="currency",
    validations=(
        "selected account codes must be explicit",
        "selected period must be explicit",
        "currency must be normalized before aggregation",
    ),
    interpretation_limits=(
        "debit total alone does not establish expense, cash outflow or loss",
        "account semantics must be known before interpreting the aggregate",
    ),
    provenance=(_SOURCE,),
)

ACCOUNT_BALANCE_TOTAL = OperationalKnowledgeSpecV1(
    knowledge_ref="account_balance_total",
    domain="accounting",
    family="ledger",
    kind="METRIC",
    status="CANDIDATE",
    inputs=(
        EvidenceFieldV1("account_code", "accounting_account_code"),
        EvidenceFieldV1("posting_date", "accounting_posting_date", "date"),
        EvidenceFieldV1("debit_amount", "accounting_debit_amount", "currency"),
        EvidenceFieldV1("credit_amount", "accounting_credit_amount", "currency"),
    ),
    expression="SUM(debit_amount - credit_amount) FILTER account_code IN selected_accounts AND posting_date IN selected_period",
    output_key="account_balance",
    output_unit="currency",
    validations=(
        "debit and credit values must come from the same accounting scope",
        "selected account codes and period must be explicit",
        "sign convention must be declared before downstream interpretation",
    ),
    interpretation_limits=(
        "balance sign cannot be interpreted without account type and sign convention",
        "this metric does not replace a governed financial statement",
    ),
    provenance=(_SOURCE,),
)

FISCAL_YEAR_START = OperationalKnowledgeSpecV1(
    knowledge_ref="fiscal_year_start",
    domain="accounting",
    family="period_control",
    kind="CONTROL",
    status="CANDIDATE",
    inputs=(
        EvidenceFieldV1("day", "reference_date", "date"),
        EvidenceFieldV1("fiscal_calendar", "fiscal_year_definition"),
    ),
    expression="RESOLVE fiscal-year start containing day USING fiscal_calendar",
    output_key="fiscal_year_start_date",
    output_unit="date",
    validations=("fiscal calendar must be explicit and applicable to the entity",),
    interpretation_limits=("calendar resolution does not establish tax treatment or filing obligations",),
    provenance=(_SOURCE,),
)

FISCAL_YEAR_END = OperationalKnowledgeSpecV1(
    knowledge_ref="fiscal_year_end",
    domain="accounting",
    family="period_control",
    kind="CONTROL",
    status="CANDIDATE",
    inputs=(
        EvidenceFieldV1("day", "reference_date", "date"),
        EvidenceFieldV1("fiscal_calendar", "fiscal_year_definition"),
    ),
    expression="RESOLVE fiscal-year end containing day USING fiscal_calendar",
    output_key="fiscal_year_end_date",
    output_unit="date",
    validations=("fiscal calendar must be explicit and applicable to the entity",),
    interpretation_limits=("calendar resolution does not establish tax treatment or filing obligations",),
    provenance=(_SOURCE,),
)

ACCOUNT_GROUP_SELECTOR = OperationalKnowledgeSpecV1(
    knowledge_ref="account_group_selector",
    domain="accounting",
    family="account_scope",
    kind="CONTROL",
    status="CANDIDATE",
    inputs=(
        EvidenceFieldV1("account_code", "accounting_account_code"),
        EvidenceFieldV1("account_type", "accounting_account_type"),
        EvidenceFieldV1("requested_account_type", "requested_account_group"),
    ),
    expression="SELECT account_code WHERE account_type == requested_account_type",
    output_key="selected_account_codes",
    output_unit="account_set",
    validations=(
        "account type taxonomy must be explicit",
        "only accounts with confirmed type membership may be selected",
    ),
    interpretation_limits=(
        "group membership does not establish account correctness",
        "no financial conclusion follows from selection alone",
    ),
    provenance=(_SOURCE,),
)

ACCOUNTING_OPERATIONS_PACK_V1 = KnowledgePackV1(
    pack_ref="accounting_operations_pack",
    version="1",
    source_family="OCA_SPREADSHEET_CONCEPTUAL_EXTRACTION",
    capabilities=(
        ACCOUNT_CREDIT_TOTAL,
        ACCOUNT_DEBIT_TOTAL,
        ACCOUNT_BALANCE_TOTAL,
        FISCAL_YEAR_START,
        FISCAL_YEAR_END,
        ACCOUNT_GROUP_SELECTOR,
    ),
)

__all__ = [
    "ACCOUNT_CREDIT_TOTAL",
    "ACCOUNT_DEBIT_TOTAL",
    "ACCOUNT_BALANCE_TOTAL",
    "FISCAL_YEAR_START",
    "FISCAL_YEAR_END",
    "ACCOUNT_GROUP_SELECTOR",
    "ACCOUNTING_OPERATIONS_PACK_V1",
]
