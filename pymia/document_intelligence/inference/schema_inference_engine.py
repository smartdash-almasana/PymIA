"""Phase 1 skeleton for schema inference execution."""

from __future__ import annotations

from pymia.document_intelligence.contracts import (
    SchemaInferenceResult,
    SemanticSchema,
    TenantClinicalContext,
)


class TenantClinicalContextRequiredError(ValueError):
    """Raised when schema inference is requested without valid tenant context."""


class SchemaInferenceEngine:
    """Minimal schema inference engine with strict context guard."""

    def infer(
        self,
        semantic_schema: SemanticSchema,
        tenant_context: TenantClinicalContext | None,
    ) -> SchemaInferenceResult:
        """Return a result or reject execution when context is missing/invalid."""
        if tenant_context is None or not tenant_context.has_minimum_context():
            raise TenantClinicalContextRequiredError(
                "TenantClinicalContext is required for schema inference."
            )

        return SchemaInferenceResult(
            semantic_schema=semantic_schema,
            context_present=True,
        )
