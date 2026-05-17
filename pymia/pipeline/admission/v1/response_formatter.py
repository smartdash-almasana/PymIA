"""Formatter determinístico para respuestas del Laboratorio Inicial PyME."""

from pymia.contracts.admission_v1 import DDIArtifact, HypothesisNode


class AdmissionResponseFormatterV1:
    """Convierte un DDIArtifact en mensaje clínico-operacional sobrio."""

    def format_response(self, artifact: DDIArtifact) -> str | None:
        if not artifact.symptoms or not artifact.hypotheses:
            return None

        primary_hypothesis = self._get_primary_hypothesis(artifact)
        if primary_hypothesis is None:
            return None

        other_hypotheses = [
            hypothesis.description
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
            "Síntoma operacional registrado:\n"
            + artifact.symptoms[0].claim
            + ".",
            "Hipótesis inicial prioritaria:\n"
            + primary_hypothesis.description.lower()
            + ".",
        ]

        if other_hypotheses:
            parts.append(
                "Hipótesis adicionales abiertas:\n"
                + ", ".join(h.lower() for h in other_hypotheses)
                + "."
            )

        if all_evidence:
            parts.append(
                "Evidencia requerida para confirmar o refutar:\n"
                + ", ".join(all_evidence)
                + "."
            )

        parts.append(
            "Estado: laboratorio inicial pendiente de línea de base documental."
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
