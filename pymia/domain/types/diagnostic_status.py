"""DiagnosticStatus — Estado epistémico de un reporte diagnóstico."""

from enum import Enum


class DiagnosticStatus(Enum):
    """Estados posibles de un DiagnosticReport."""

    PRELIMINAR = "preliminar"
    CONFIRMADO = "confirmado"
    REFUTADO = "refutado"
    OBSOLETO = "obsoleto"
