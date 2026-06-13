from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


LanguageCorpusStatus = Literal["DRAFT", "ACTIVE", "DEPRECATED"]
AmbiguityPolicy = Literal["ASK_CLARIFICATION", "REQUEST_EVIDENCE", "KEEP_CANDIDATE"]
DiagnosticAuthority = Literal["NONE"]


class LanguageCorpusEntry(BaseModel):
    """Entrada conceptual del Language Corpus V1.

    Boundary: este contrato transporta lenguaje controlado y referencias.
    No diagnostica, no calcula, no crea evidencia y no confirma findings.
    """

    concept_id: str = Field(..., description="ID estable y machine-readable del concepto.")
    canonical_label: str = Field(..., description="Etiqueta humana segura. No otorga autoridad diagnostica.")
    owner_synonyms: list[str] = Field(default_factory=list)
    owner_expression_patterns: list[str] = Field(default_factory=list)
    technical_synonyms: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    related_evidence_ids: list[str] = Field(default_factory=list)
    related_variable_ids: list[str] = Field(default_factory=list)
    related_formula_ids: list[str] = Field(default_factory=list)
    related_pathology_ids: list[str] = Field(default_factory=list)
    allowed_owner_questions: list[str] = Field(default_factory=list)
    allowed_report_phrases: list[str] = Field(default_factory=list)
    allowed_operator_language: list[str] = Field(default_factory=list)
    forbidden_language: list[str] = Field(default_factory=list)
    ambiguity_policy: AmbiguityPolicy
    diagnostic_authority: DiagnosticAuthority = "NONE"
    version: str
    status: LanguageCorpusStatus
    source_refs: list[str] = Field(..., description="Referencias documentales obligatorias.")

    @field_validator("concept_id", "canonical_label", "version")
    @classmethod
    def _required_strings_must_not_be_blank(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("required string fields must not be blank")
        return value.strip()

    @field_validator(
        "owner_synonyms",
        "owner_expression_patterns",
        "technical_synonyms",
        "tags",
        "related_evidence_ids",
        "related_variable_ids",
        "related_formula_ids",
        "related_pathology_ids",
        "allowed_owner_questions",
        "allowed_report_phrases",
        "allowed_operator_language",
        "forbidden_language",
        "source_refs",
    )
    @classmethod
    def _list_items_must_not_be_blank(cls, values: list[str]) -> list[str]:
        cleaned: list[str] = []
        for value in values:
            if not value or not value.strip():
                raise ValueError("list items must not be blank")
            cleaned.append(value.strip())
        return cleaned

    @field_validator("source_refs")
    @classmethod
    def _source_refs_are_mandatory(cls, values: list[str]) -> list[str]:
        if not values:
            raise ValueError("source_refs are mandatory")
        return values

    @model_validator(mode="after")
    def _forbidden_language_must_not_appear_in_allowed_text(self) -> "LanguageCorpusEntry":
        forbidden = [item.casefold() for item in self.forbidden_language]
        if not forbidden:
            return self

        allowed_texts = [
            *self.allowed_owner_questions,
            *self.allowed_report_phrases,
            *self.allowed_operator_language,
        ]
        for text in allowed_texts:
            normalized = text.casefold()
            for token in forbidden:
                if token in normalized:
                    raise ValueError("forbidden language cannot appear in allowed language fields")
        return self


class LanguageCorpus(BaseModel):
    """Coleccion versionada de entradas Language Corpus V1.

    Es read-only por contrato durante la ejecucion de un caso.
    """

    version: str
    status: LanguageCorpusStatus = "DRAFT"
    entries: list[LanguageCorpusEntry] = Field(default_factory=list)

    @field_validator("version")
    @classmethod
    def _version_must_not_be_blank(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("version must not be blank")
        return value.strip()

    @model_validator(mode="after")
    def _concept_ids_must_be_unique(self) -> "LanguageCorpus":
        ids = [entry.concept_id for entry in self.entries]
        if len(ids) != len(set(ids)):
            raise ValueError("concept_id values must be unique within a LanguageCorpus")
        return self

    def get_entry(self, concept_id: str) -> LanguageCorpusEntry | None:
        for entry in self.entries:
            if entry.concept_id == concept_id:
                return entry
        return None


def owner_label_for(concept_id: str, corpus: LanguageCorpus) -> str:
    """Return a safe owner-facing label or fail closed to the raw concept_id.

    This function does not infer, diagnose or create evidence.
    """

    entry = corpus.get_entry(concept_id)
    if entry is None:
        return concept_id
    return entry.canonical_label


def owner_label_for_variable_id(variable_id: str, corpus: LanguageCorpus) -> str:
    """Return the owner-facing label for a related variable or fail closed.

    The lookup is read-only and does not convert variables into findings.
    """

    for entry in corpus.entries:
        if variable_id in entry.related_variable_ids:
            return entry.canonical_label
    return variable_id


def load_language_corpus_seed(path: Path | None = None) -> LanguageCorpus:
    """Load the DRAFT seed corpus from JSON.

    This is a static contract loader, not a Pack Runtime loader.
    """

    seed_path = path or Path(__file__).with_name("language_corpus_seed.json")
    payload = json.loads(seed_path.read_text(encoding="utf-8"))
    return LanguageCorpus(**payload)


__all__ = [
    "AmbiguityPolicy",
    "DiagnosticAuthority",
    "LanguageCorpus",
    "LanguageCorpusEntry",
    "LanguageCorpusStatus",
    "load_language_corpus_seed",
    "owner_label_for",
    "owner_label_for_variable_id",
]
