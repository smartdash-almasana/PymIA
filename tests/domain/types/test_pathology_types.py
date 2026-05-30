"""Tests para enums de OrganizationalPathology (M10)."""

import pytest

from pymia.domain.types.pathology_type import PathologyType
from pymia.domain.types.pathology_severity import PathologySeverity
from pymia.domain.types.pathology_stage import PathologyStage
from pymia.domain.types.pathology_status import PathologyStatus


class TestPathologyType:
    """Tests para PathologyType enum."""

    def test_has_8_values(self):
        """PathologyType debe tener exactamente 8 valores."""
        assert len(PathologyType) == 8

    def test_values(self):
        """Verifica los 8 valores específicos."""
        assert PathologyType.MARGEN_EROSIONADO_POR_CANAL.value == "margen_erosionado_por_canal"
        assert PathologyType.DEPENDENCIA_CLIENTE_CONCENTRADO.value == "dependencia_cliente_concentrado"
        assert PathologyType.DESCAPITALIZACION_SILENCIOSA.value == "descapitalizacion_silenciosa"
        assert PathologyType.CENTRALISMO_ASFIXIANTE.value == "centralismo_asfixiante"
        assert PathologyType.CRECIMIENTO_NO_DIGESTIDO.value == "crecimiento_no_digerido"
        assert PathologyType.ESTANCAMIENTO_ADAPTATIVO.value == "estancamiento_adaptativo"
        assert PathologyType.CONFLICTO_SOCIETARIO_LATENTE.value == "conflicto_societario_latente"
        assert PathologyType.FATIGA_DECISIONAL_CRONICA.value == "fatiga_decisional_cronica"

    def test_from_value(self):
        """Construcción desde string."""
        assert PathologyType("margen_erosionado_por_canal") == PathologyType.MARGEN_EROSIONADO_POR_CANAL
        assert PathologyType("fatiga_decisional_cronica") == PathologyType.FATIGA_DECISIONAL_CRONICA

    def test_invalid_value_raises(self):
        """Valor inválido eleva ValueError."""
        with pytest.raises(ValueError):
            PathologyType("invalido")


class TestPathologySeverity:
    """Tests para PathologySeverity enum."""

    def test_has_4_values(self):
        """PathologySeverity debe tener exactamente 4 valores."""
        assert len(PathologySeverity) == 4

    def test_values(self):
        """Verifica los 4 valores específicos."""
        assert PathologySeverity.LEVE.value == "leve"
        assert PathologySeverity.MODERADA.value == "moderada"
        assert PathologySeverity.GRAVE.value == "grave"
        assert PathologySeverity.CRITICA.value == "critica"

    def test_from_value(self):
        """Construcción desde string."""
        assert PathologySeverity("leve") == PathologySeverity.LEVE
        assert PathologySeverity("critica") == PathologySeverity.CRITICA

    def test_invalid_value_raises(self):
        """Valor inválido eleva ValueError."""
        with pytest.raises(ValueError):
            PathologySeverity("invalido")


class TestPathologyStage:
    """Tests para PathologyStage enum."""

    def test_has_2_values(self):
        """PathologyStage debe tener exactamente 2 valores."""
        assert len(PathologyStage) == 2

    def test_values(self):
        """Verifica los 2 valores específicos."""
        assert PathologyStage.AGUDA.value == "aguda"
        assert PathologyStage.CRONICA.value == "cronica"

    def test_from_value(self):
        """Construcción desde string."""
        assert PathologyStage("aguda") == PathologyStage.AGUDA
        assert PathologyStage("cronica") == PathologyStage.CRONICA

    def test_invalid_value_raises(self):
        """Valor inválido eleva ValueError."""
        with pytest.raises(ValueError):
            PathologyStage("invalido")


class TestPathologyStatus:
    """Tests para PathologyStatus enum."""

    def test_has_3_values(self):
        """PathologyStatus debe tener exactamente 3 valores."""
        assert len(PathologyStatus) == 3

    def test_values(self):
        """Verifica los 3 valores específicos."""
        assert PathologyStatus.ACTIVA.value == "activa"
        assert PathologyStatus.RESUELTA.value == "resuelta"
        assert PathologyStatus.CRONIFICADA.value == "cronificada"

    def test_from_value(self):
        """Construcción desde string."""
        assert PathologyStatus("activa") == PathologyStatus.ACTIVA
        assert PathologyStatus("resuelta") == PathologyStatus.RESUELTA
        assert PathologyStatus("cronificada") == PathologyStatus.CRONIFICADA

    def test_invalid_value_raises(self):
        """Valor inválido eleva ValueError."""
        with pytest.raises(ValueError):
            PathologyStatus("invalido")
