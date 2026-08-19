"""Native PymIA reconciliation knowledge derived from governed accounting primitives.

OCA/spreadsheet exposes portable accounting primitives such as debit, credit,
balance, fiscal periods and account groups. It does not provide a reconciliation
module in this repository. The controls below are therefore PymIA-native
compositions built from those verified primitives, not copied Odoo behavior.

All specs are candidate knowledge only and do not authorize Service 1 runtime.
"""
from __future__ import annotations

from pymia.business_knowledge.contracts_v1 import (
    EvidenceFieldV1,
    KnowledgePackV1,
    OperationalKnowledgeSpecV1,
)

_OCA_SOURCE = "OCA/spreadsheet@18.0:spreadsheet_oca/readme/USAGE.md"
_NATIVE_SOURCE = "PYMIA_NATIVE_DERIVATION_FROM_GOVERNED_ACCOUNTING_PRIMITIVES_V1"
_PROVENANCE = (_OCA_SOURCE, _NATIVE_SOURCE)

TRIAL_BALANCE_RECONCILIATION = OperationalKnowledgeSpecV1(
    knowledge_ref="trial_balance_reconciliation",
    domain="accounting",
    family="reconciliation",
    kind="CONTROL",
    status="CANDIDATE",
    inputs=(
        EvidenceFieldV1("debit_total", "accounting_debit_total", "currency"),
        EvidenceFieldV1("credit_total", "accounting_credit_total", "currency"),
        EvidenceFieldV1("period", "accounting_period"),
    ),
    expression="reconciliation_gap = debit_total - credit_total",
    output_key="trial_balance_gap",
    output_unit="currency",
    validations=(
        "debit and credit totals must share entity, ledger, currency and period",
        "source postings must be inside the governed accounting scope",
    ),
    interpretation_limits=(
        "a zero gap confirms arithmetic balance only, not accounting correctness",
        "a non-zero gap identifies inconsistency but does not identify its cause",
    ),
    provenance=_PROVENANCE,
)

ACCOUNTING_EQUATION_RECONCILIATION = OperationalKnowledgeSpecV1(
    knowledge_ref="accounting_equation_reconciliation",
    domain="accounting",
    family="reconciliation",
    kind="CONTROL",
    status="CANDIDATE",
    inputs=(
        EvidenceFieldV1("assets", "total_assets", "currency"),
        EvidenceFieldV1("liabilities", "total_liabilities", "currency"),
        EvidenceFieldV1("equity", "total_equity", "currency"),
        EvidenceFieldV1("as_of", "statement_date", "date"),
    ),
    expression="reconciliation_gap = assets - liabilities - equity",
    output_key="accounting_equation_gap",
    output_unit="currency",
    validations=(
        "all three totals must belong to the same entity and statement date",
        "classification policy and currency must be consistent across totals",
    ),
    interpretation_limits=(
        "a zero gap confirms the accounting identity only",
        "this control does not validate valuation, classification or completeness",
    ),
    provenance=_PROVENANCE,
)

BANK_LEDGER_RECONCILIATION = OperationalKnowledgeSpecV1(
    knowledge_ref="bank_ledger_reconciliation",
    domain="treasury",
    family="reconciliation",
    kind="CONTROL",
    status="CANDIDATE",
    inputs=(
        EvidenceFieldV1("bank_statement_balance", "bank_statement_closing_balance", "currency"),
        EvidenceFieldV1("ledger_bank_balance", "accounting_bank_account_balance", "currency"),
        EvidenceFieldV1("as_of", "reconciliation_date", "date"),
    ),
    expression="reconciliation_gap = bank_statement_balance - ledger_bank_balance",
    output_key="bank_ledger_gap",
    output_unit="currency",
    validations=(
        "bank statement and ledger balance must refer to the same bank account and date",
        "currency and sign convention must be normalized before comparison",
    ),
    interpretation_limits=(
        "a gap does not identify missing deposits, bank fees, timing differences or errors",
        "a zero gap does not prove that every underlying transaction is correct",
    ),
    provenance=_PROVENANCE,
)

CASH_FLOW_CONTINUITY_RECONCILIATION = OperationalKnowledgeSpecV1(
    knowledge_ref="cash_flow_continuity_reconciliation",
    domain="treasury",
    family="reconciliation",
    kind="CONTROL",
    status="CANDIDATE",
    inputs=(
        EvidenceFieldV1("opening_cash", "opening_cash_balance", "currency"),
        EvidenceFieldV1("cash_inflows", "period_cash_inflows", "currency"),
        EvidenceFieldV1("cash_outflows", "period_cash_outflows", "currency"),
        EvidenceFieldV1("closing_cash", "closing_cash_balance", "currency"),
    ),
    expression="reconciliation_gap = opening_cash + cash_inflows - cash_outflows - closing_cash",
    output_key="cash_continuity_gap",
    output_unit="currency",
    validations=(
        "opening, movements and closing balance must belong to one continuous period",
        "inflows and outflows must follow the declared sign convention",
    ),
    interpretation_limits=(
        "a gap identifies broken cash continuity but does not identify the responsible transaction",
        "cash continuity is not equivalent to profitability",
    ),
    provenance=_PROVENANCE,
)

RECEIVABLES_ROLL_FORWARD_RECONCILIATION = OperationalKnowledgeSpecV1(
    knowledge_ref="receivables_roll_forward_reconciliation",
    domain="collections",
    family="reconciliation",
    kind="CONTROL",
    status="CANDIDATE",
    inputs=(
        EvidenceFieldV1("opening_receivables", "opening_accounts_receivable", "currency"),
        EvidenceFieldV1("credit_sales", "period_credit_sales", "currency"),
        EvidenceFieldV1("collections", "period_customer_collections", "currency"),
        EvidenceFieldV1("closing_receivables", "closing_accounts_receivable", "currency"),
    ),
    expression="reconciliation_gap = opening_receivables + credit_sales - collections - closing_receivables",
    output_key="receivables_roll_forward_gap",
    output_unit="currency",
    validations=(
        "balances, sales and collections must share entity, currency and period",
        "credit sales must exclude cash sales unless explicitly included by policy",
    ),
    interpretation_limits=(
        "a gap does not establish unrecorded sales, missing collections or fraud",
        "zero gap confirms roll-forward arithmetic only",
    ),
    provenance=_PROVENANCE,
)

PAYABLES_ROLL_FORWARD_RECONCILIATION = OperationalKnowledgeSpecV1(
    knowledge_ref="payables_roll_forward_reconciliation",
    domain="payments",
    family="reconciliation",
    kind="CONTROL",
    status="CANDIDATE",
    inputs=(
        EvidenceFieldV1("opening_payables", "opening_accounts_payable", "currency"),
        EvidenceFieldV1("credit_purchases", "period_credit_purchases", "currency"),
        EvidenceFieldV1("supplier_payments", "period_supplier_payments", "currency"),
        EvidenceFieldV1("closing_payables", "closing_accounts_payable", "currency"),
    ),
    expression="reconciliation_gap = opening_payables + credit_purchases - supplier_payments - closing_payables",
    output_key="payables_roll_forward_gap",
    output_unit="currency",
    validations=(
        "balances, purchases and payments must share entity, currency and period",
        "credit purchases must be distinguished from immediate cash purchases",
    ),
    interpretation_limits=(
        "a gap does not establish unpaid invoices, duplicate payments or supplier error",
        "zero gap confirms roll-forward arithmetic only",
    ),
    provenance=_PROVENANCE,
)

RECONCILIATION_OPERATIONS_PACK_V1 = KnowledgePackV1(
    pack_ref="reconciliation_operations_pack",
    version="1",
    source_family="PYMIA_NATIVE_DERIVATION_FROM_OCA_ACCOUNTING_PRIMITIVES",
    capabilities=(
        TRIAL_BALANCE_RECONCILIATION,
        ACCOUNTING_EQUATION_RECONCILIATION,
        BANK_LEDGER_RECONCILIATION,
        CASH_FLOW_CONTINUITY_RECONCILIATION,
        RECEIVABLES_ROLL_FORWARD_RECONCILIATION,
        PAYABLES_ROLL_FORWARD_RECONCILIATION,
    ),
)

__all__ = [
    "TRIAL_BALANCE_RECONCILIATION",
    "ACCOUNTING_EQUATION_RECONCILIATION",
    "BANK_LEDGER_RECONCILIATION",
    "CASH_FLOW_CONTINUITY_RECONCILIATION",
    "RECEIVABLES_ROLL_FORWARD_RECONCILIATION",
    "PAYABLES_ROLL_FORWARD_RECONCILIATION",
    "RECONCILIATION_OPERATIONS_PACK_V1",
]
