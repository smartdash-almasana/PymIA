from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class PathologyCatalogEntryV1(BaseModel):
    pathology_code: str
    name: str
    category: str
    formula_expression: str | None = None
    version: str = "1.0"


class PathologyCatalogV1(BaseModel):
    catalog_version: str
    architecture_mode: str | None = None
    hot_swappable: bool = True
    mutable: bool = True
    supports_taxonomy_modules: bool = True
    supports_formula_overrides: bool = True
    supports_industry_extensions: bool = True
    description: str | None = None
    knowledge_tank: str | None = None
    source_document: str | None = None
    pathologies: list[PathologyCatalogEntryV1] = Field(default_factory=list)


class FormulaCatalogEntryV1(BaseModel):
    formula_id: str
    pathology_code: str
    name: str
    expression: str
    display_expression: str
    category: str
    required_variables: list[str] = Field(default_factory=list)
    required_evidence: list[str] = Field(default_factory=list)
    output_unit: str
    calculation_state: Literal[
        "CALCULABLE",
        "CALCULABLE_CON_SUPUESTOS",
        "NO_CALCULABLE_POR_EVIDENCIA_INSUFICIENTE",
    ]


class FormulaCatalogV1(BaseModel):
    catalog_version: str
    description: str | None = None
    source_document: str | None = None
    status: str | None = None
    formulas: list[FormulaCatalogEntryV1] = Field(default_factory=list)
    pending_expansion: str | None = None
