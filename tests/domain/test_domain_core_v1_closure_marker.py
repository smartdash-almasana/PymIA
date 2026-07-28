from pathlib import Path


def test_domain_core_v1_closure_marker_exists_and_has_required_content() -> None:
    marker = Path('docs/domain/DOMAIN_CORE_V1_CLOSURE.md')
    assert marker.exists()

    content = marker.read_text(encoding='utf-8')

    assert 'DOMAIN_CORE_V1_CLOSED' in content
    assert 'f143b97' in content
    assert 'V1_READY_FOR_M17' in content
    assert 'M1-M16 + M16.5' in content
    assert 'Domain Core V1 no debe reabrirse sin ADR o frente explícito aprobado' in content
