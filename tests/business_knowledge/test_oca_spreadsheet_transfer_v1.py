from __future__ import annotations

from pymia.business_knowledge.purchase_operations_pack_v1 import PURCHASE_OPERATIONS_PACK_V1
from pymia.business_knowledge.quotation_operations_pack_v1 import QUOTATION_OPERATIONS_PACK_V1


def test_oca_derived_knowledge_is_non_authorizing() -> None:
    packs = (PURCHASE_OPERATIONS_PACK_V1, QUOTATION_OPERATIONS_PACK_V1)
    assert all(pack.runtime_authorized is False for pack in packs)
    assert all(cap.runtime_authorized is False for pack in packs for cap in pack.capabilities)


def test_knowledge_refs_are_unique() -> None:
    capabilities = (
        *PURCHASE_OPERATIONS_PACK_V1.capabilities,
        *QUOTATION_OPERATIONS_PACK_V1.capabilities,
    )
    refs = [cap.knowledge_ref for cap in capabilities]
    assert len(refs) == len(set(refs))


def test_every_capability_has_governance_metadata() -> None:
    capabilities = (
        *PURCHASE_OPERATIONS_PACK_V1.capabilities,
        *QUOTATION_OPERATIONS_PACK_V1.capabilities,
    )
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


def test_transferred_pack_has_ten_candidate_capabilities() -> None:
    capabilities = (
        *PURCHASE_OPERATIONS_PACK_V1.capabilities,
        *QUOTATION_OPERATIONS_PACK_V1.capabilities,
    )
    assert len(capabilities) == 10
