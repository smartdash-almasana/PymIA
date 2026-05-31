from pymia.smartpyme.anamnesis_fsm_integration import (
    build_structured_selectors_from_profile_data,
)
from pymia.smartpyme.interrogation import StructuredSelectors


def test_profile_to_selectors_commerce_spreadsheet_team_wholesale_social_excel() -> None:
    profile_data = {
        "business_taxonomy": {"activity_type": "commerce_products"},
        "current_tools": {"primary_information_system": "spreadsheet"},
        "company_profile": {"team_size_range": "team_2_5"},
        "business_model": {"sales_channels": ["wholesale", "social_media"]},
        "evidence": {"available": ["sales_records", "price_list"]},
    }

    selectors = build_structured_selectors_from_profile_data(profile_data)
    assert isinstance(selectors, StructuredSelectors)
    assert selectors.operation_type == "Revendo"
    assert selectors.tools_used == "Excel"
    assert selectors.employee_range == "2 a 5"
    assert selectors.sales_channel == "Mixto"
    assert selectors.evidence_available == "Excel"


def test_profile_to_selectors_manufacturing_erp_marketplace() -> None:
    profile_data = {
        "business_taxonomy": {"activity_type": "manufacturing"},
        "current_tools": {"primary_information_system": "erp"},
        "business_model": {"sales_channels": ["marketplace"]},
        "digital_presence": {"presence_channels": ["instagram"]},
    }

    selectors = build_structured_selectors_from_profile_data(profile_data)
    assert selectors.operation_type == "Produzco"
    assert selectors.tools_used == "Sistema"
    assert selectors.marketplace_presence == "Sí"
    assert selectors.sales_channel == "Marketplace"
    assert selectors.stock_mode == "Informal"


def test_profile_to_selectors_empty_data_returns_safe_fallbacks() -> None:
    selectors = build_structured_selectors_from_profile_data({})
    assert isinstance(selectors, StructuredSelectors)
    assert selectors.operation_type == "Mixto"
    assert selectors.tools_used is None
    assert selectors.employee_range is None
    assert selectors.sales_channel is None
    assert selectors.marketplace_presence is None
    assert selectors.evidence_available is None
    assert selectors.stock_mode is None
