"""Formatter determinístico para respuestas del Laboratorio Inicial PyME."""

from pymia.contracts.admission_v1 import DDIArtifact, HypothesisNode


class AdmissionResponseFormatterV1:
    """Convierte un DDIArtifact en mensaje natural para primer contacto."""

    def format_response(self, artifact: DDIArtifact) -> str | None:
        if not artifact.symptoms or not artifact.hypotheses:
            return None

        primary_hypothesis = self._get_primary_hypothesis(artifact)
        if primary_hypothesis is None:
            return None

        other_hypotheses = [
            hypothesis.description.lower()
            for hypothesis in artifact.hypotheses
            if hypothesis.node_id != primary_hypothesis.node_id
        ]

        all_evidence = sorted(
            {
                evidence
                for hypothesis in artifact.hypotheses
                for evidence in hypothesis.evidence_required
            }
        )

        parts = [
            "Registré este síntoma operacional: " + artifact.symptoms[0].claim + ".",
            "Entiendo la señal: " + artifact.symptoms[0].claim + ".",
            (
                "Todavía no lo tomo como una conclusión cerrada. "
                "Con lo que contás, primero haría una lectura preliminar."
            ),
            (
                "Hipótesis inicial prioritaria:\n"
                + primary_hypothesis.description.lower()
                + "."
            ),
            (
                "Lo primero que revisaría es "
                + primary_hypothesis.description.lower()
                + "."
            ),
        ]

        if other_hypotheses:
            parts.append(
                "También puede estar mezclado con "
                + ", ".join(other_hypotheses)
                + "."
            )

        if all_evidence:
            evidence_lines = "\n".join(f"- {evidence}" for evidence in all_evidence)
            parts.append(
                "Para confirmar o refutar estas hipótesis necesito:\n"
                + evidence_lines
            )
            parts.append(
                "Evidencia requerida: " + ", ".join(all_evidence)
            )
            parts.append(
                "Para mirarlo con números necesito:\n"
                + evidence_lines
            )

        parts.append(
            "Con eso puedo separar si el problema viene por margen, caja, "
            "costos o movimiento operativo."
        )

        return "\n\n".join(parts)

    def _get_primary_hypothesis(
        self,
        artifact: DDIArtifact,
    ) -> HypothesisNode | None:
        if artifact.primary_hypothesis_id is not None:
            for hypothesis in artifact.hypotheses:
                if hypothesis.node_id == artifact.primary_hypothesis_id:
                    return hypothesis

        return max(
            artifact.hypotheses,
            key=lambda hypothesis: hypothesis.confidence_score,
            default=None,
        )
