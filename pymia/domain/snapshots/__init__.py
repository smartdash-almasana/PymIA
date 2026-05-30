# Domain snapshots (evaluaciones compuestas inmutables, Capa 4)
from .health_assessment import HealthAssessment
from .diagnostic_report import DiagnosticReport
from .prognosis_assessment import PrognosisAssessment
from .decision_capability_assessment import DecisionCapabilityAssessment

__all__ = [
    "HealthAssessment",
    "DiagnosticReport",
    "PrognosisAssessment",
    "DecisionCapabilityAssessment",
]
