"""Backward-compatibility wrapper for document ingestion.

This module delegates all execution to the productized implementation in
pymia.smartpyme.excel_lab_ingestion_v1.
"""

from __future__ import annotations

from tools.bem_schema_builder.owner_questions_builder import OwnerQuestionsBuilder  # re-export just in case
from pymia.smartpyme.excel_lab_ingestion_v1 import (
    NUMERIC_FIELDS,
    RawTable,
    FieldMapping,
    NormalizedTable,
    CellValidationIssue,
    DocumentCurationReport,
    CuratedDocument,
    ProductoRow,
    VentaRow,
    StockRow,
    CajaBancoRow,
    SignalRow,
    ContextClassifier,
    XlsxDocumentIngestor,
    SemanticFieldMapper,
    DocumentCurator,
    ColumnConfirmationBuilder,
    StructuredEvidenceExporter,
    XlsxCurationPipeline,
    curate_xlsx_document,
    build_structured_evidence_from_xlsx,
    persist_curation_artifacts,
)
