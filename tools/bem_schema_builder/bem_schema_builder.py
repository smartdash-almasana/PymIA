from __future__ import annotations

from collections import Counter
from typing import Any

from .models import ExcelProfile


class BemSchemaBuilder:
    def build_candidate_schema(self, profile: ExcelProfile, owner_questions: dict[str, Any]) -> dict[str, Any]:
        semantics = Counter()
        for sheet in profile.sheets:
            for col in sheet.columns:
                semantics[col.semantic_label] += 1

        mode = self._select_mode(semantics)
        owner_required = bool(owner_questions.get("owner_questions"))

        schema: dict[str, Any] = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": f"https://pymia.local/schemas/bem/{profile.file_name}.candidate.json",
            "title": f"PymIA Candidate BEM Schema for {profile.file_name}",
            "type": "object",
            "additionalProperties": False,
            "required": [
                "document_identity",
                "curation_status",
                "economic_summary",
                "items",
                "anomalies",
                "extraction_quality",
                "owner_clarifications_required",
            ],
            "properties": {
                "document_identity": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["original_file_name", "sheet_names_detected", "profile_mode"],
                    "properties": {
                        "original_file_name": {"type": ["string", "null"]},
                        "sheet_names_detected": {"type": "array", "items": {"type": "string"}},
                        "profile_mode": {"type": "string", "enum": ["margin", "stock", "finance", "conservative"]},
                    },
                },
                "curation_status": {
                    "type": "string",
                    "enum": ["CURATED", "PARTIAL", "BLOCKED", "UNSUPPORTED"],
                },
                "economic_summary": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "ventas_total": {"type": ["number", "null"]},
                        "costos_total": {"type": ["number", "null"]},
                        "stock_total_unidades": {"type": ["number", "null"]},
                        "pagos_total": {"type": ["number", "null"]},
                        "saldo_final": {"type": ["number", "null"]},
                    },
                },
                "items": {
                    "type": "array",
                    "items": self._item_schema_by_mode(mode),
                },
                "anomalies": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["code", "detail"],
                        "properties": {
                            "code": {"type": "string"},
                            "detail": {"type": "string"},
                        },
                    },
                },
                "extraction_quality": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["semantic_mode", "owner_questions_count", "has_ambiguities"],
                    "properties": {
                        "semantic_mode": {"type": "string", "enum": ["margin", "stock", "finance", "conservative"]},
                        "owner_questions_count": {"type": "integer", "minimum": 0},
                        "has_ambiguities": {"type": "boolean"},
                    },
                },
                "owner_clarifications_required": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["required", "questions"],
                    "properties": {
                        "required": {"type": "boolean"},
                        "questions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "additionalProperties": True,
                            },
                        },
                    },
                },
            },
        }

        schema["x_profile_context"] = {
            "mode": mode,
            "tabular_sheets": profile.likely_tabular_sheets,
            "summary_sheets": profile.likely_summary_sheets,
            "auxiliary_sheets": profile.likely_auxiliary_sheets,
        }
        schema["x_defaults"] = {
            "document_identity": {
                "original_file_name": profile.file_name,
                "sheet_names_detected": [s.sheet_name for s in profile.sheets],
                "profile_mode": mode,
            },
            "extraction_quality": {
                "semantic_mode": mode,
                "owner_questions_count": owner_questions.get("question_count", 0),
                "has_ambiguities": owner_required,
            },
            "owner_clarifications_required": {
                "required": owner_required,
                "questions": owner_questions.get("owner_questions", []),
            },
        }
        return schema

    def _select_mode(self, semantics: Counter) -> str:
        margin_score = semantics["producto"] + semantics["cantidad"] + semantics["precio_venta"] + semantics["costo_unitario"] + semantics["venta_total"] + semantics["costo_total"]
        stock_score = semantics["stock"] + semantics["sku"] + semantics["producto"]
        finance_score = semantics["pago"] + semantics["saldo"] + semantics["gasto"]

        top = max(margin_score, stock_score, finance_score)
        if top <= 1:
            return "conservative"
        if margin_score == top:
            return "margin"
        if stock_score == top:
            return "stock"
        return "finance"

    def _item_schema_by_mode(self, mode: str) -> dict[str, Any]:
        common = {
            "type": "object",
            "additionalProperties": True,
            "properties": {
                "producto": {"type": ["string", "null"]},
                "sku": {"type": ["string", "null"]},
                "fecha": {"type": ["string", "null"]},
                "cantidad": {"type": ["number", "null"]},
                "precio_venta": {"type": ["number", "null"]},
                "costo_unitario": {"type": ["number", "null"]},
                "stock": {"type": ["number", "null"]},
                "pago": {"type": ["number", "null"]},
                "saldo": {"type": ["number", "null"]},
                "moneda": {"type": ["string", "null"]},
            },
        }
        if mode == "margin":
            common["required"] = ["cantidad", "precio_venta"]
        elif mode == "stock":
            common["required"] = ["producto", "stock"]
        elif mode == "finance":
            common["required"] = ["pago", "saldo"]
        else:
            common["required"] = []
        return common
