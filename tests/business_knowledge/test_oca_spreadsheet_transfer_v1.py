from __future__ import annotations

from pymia.business_knowledge.accounting_operations_pack_v1 import ACCOUNTING_OPERATIONS_PACK_V1
from pymia.business_knowledge.purchase_operations_pack_v1 import PURCHASE_OPERATIONS_PACK_V1
from pymia.business_knowledge.quotation_operations_pack_v1 import QUOTATION_OPERATIONS_PACK_V1
from pymia.business_knowledge.reconciliation_operations_pack_v1 import RECONCILIATION_OPERATIONS_PACK_V1


def _packs():
    return (
        PURCHASE_OPERATIONS_PACK_V1,
        QUOTATION_OPERATIONS_PACK_V1,
        ACCOUNTING_OPERATIONS_PACK_V1,
        RECONCILIATION_OPERATIONS_PACK_V1,
    )


def test_oca_derived_knowledge_is_non_authorizing() -> None:
    packs = _packs()
    assert all(pack.runtime_authorized is False for pack in packs)
    assert all(cap.runtime_authorized is False for pack in packs for cap in pack.capabilities)


def test_knowledge_refs_are_unique() -> None:
    capabilities = tuple(cap for pack in _packs() for cap in pack.capabilities)
    refs = [cap.knowledge_ref for cap in capabilities]
    assert len(refs) == len(set(refs))


def test_every_capability_has_governance_metadata() -> None:
    capabilities = tuple(cap for pack in _packs() for cap in pack.capabilities)
    for cap in capabilities:
        assert cap.status == "CANDIDATE"
        assert cap.inputs
        assert cap.expression
        assert cap.validations
        assert cap.interpretation_limits
        assert cap.provenance


def test_purchase_pack_contains_portable_procurement_controls() -> None:
    refs = {cap.knowledge_ref for cap in PURCHASE_OPERATIONS_PACK_V1.capabilities}
    assert refs == {
        "purchase_amount_by_period",
        "supplier_spend_by_vendor",
        "open_rfq_control",
        "confirmed_purchase_order_register",
        "confirmed_purchase_volume_by_buyer",
        "late_incoming_receipt_control",
    }


def test_quotation_pack_preserves_scoping_mapping_and_writeback_controls() -> None:
    refs = {cap.knowledge_ref for cap in QUOTATION_OPERATIONS_PACK_V1.capabilities}
    assert refs == {
        "quotation_line_extended_amount",
        "quotation_scope_filter_control",
        "quotation_column_sync_control",
        "quotation_calculated_writeback_control",
    }


def test_accounting_pack_translates_business_functions_without_odoo_dependency() -> None:
    refs = {cap.knowledge_ref for cap in ACCOUNTING_OPERATIONS_PACK_V1.capabilities}
    assert refs == {
        "account_credit_total",
        "account_debit_total",
        "account_balance_total",
        "fiscal_year_start",
        "fiscal_year_end",
        "account_group_selector",
    }


def test_reconciliation_pack_is_native_composition_not_claimed_as_oca_module() -> None:
    refs = {cap.knowledge_ref for cap in RECONCILIATION_OPERATIONS_PACK_V1.capabilities}
    assert refs == {
        "trial_balance_reconciliation",
        "accounting_equation_reconciliation",
        "bank_ledger_reconciliation",
        "cash_flow_continuity_reconciliation",
        "receivables_roll_forward_reconciliation",
        "payables_roll_forward_reconciliation",
    }
    assert RECONCILIATION_OPERATIONS_PACK_V1.source_family == (
        "PYMIA_NATIVE_DERIVATION_FROM_OCA_ACCOUNTING_PRIMITIVES"
    )


def test_transferred_and_derived_packs_have_twenty_two_candidate_capabilities() -> None:
    capabilities = tuple(cap for pack in _packs() for cap in pack.capabilities)
    assert len(capabilities) == 22
