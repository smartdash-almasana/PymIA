from __future__ import annotations

from typing import Any

from .models import ExcelProfile


class OwnerQuestionsBuilder:
    _PROMPTS = {
        "importe": "La columna \"{name}\" representa venta, costo, pago, deuda, saldo u otro concepto?",
        "monto": "La columna \"{name}\" representa ingreso, egreso, deuda, pago u otro concepto economico?",
        "total": "La columna \"{name}\" es total de venta, costo, stock valorizado o saldo acumulado?",
        "precio": "La columna \"{name}\" es precio de venta, costo unitario o precio promedio?",
        "valor": "La columna \"{name}\" corresponde a valorizacion de stock, venta, costo o saldo?",
        "estado": "La columna \"{name}\" describe estado de pago, entrega, produccion u otro flujo?",
        "cantidad": "La columna \"{name}\" representa unidades vendidas, compradas, producidas o stock actual?",
        "saldo": "La columna \"{name}\" es saldo de caja, banco, cliente, proveedor o cuenta corriente?",
        "diferencia": "La columna \"{name}\" indica diferencia contra que referencia (precio, stock, conciliacion, costo)?",
        "cuenta": "La columna \"{name}\" es cuenta contable, cuenta bancaria o cuenta corriente comercial?",
        "concepto": "La columna \"{name}\" detalla concepto de venta, gasto, pago, impuesto u otro?",
    }

    def build(self, profile: ExcelProfile) -> dict[str, Any]:
        questions: list[dict[str, str]] = []

        for sheet in profile.sheets:
            if sheet.sheet_kind == "summary":
                questions.append(
                    {
                        "sheet": sheet.sheet_name,
                        "question": f'La hoja "{sheet.sheet_name}" debe usarse como fuente de verdad o solo como resumen manual?',
                        "reason": "summary_sheet_needs_confirmation",
                    }
                )

            for col in sheet.columns:
                if col.is_ambiguous:
                    questions.append(
                        {
                            "sheet": sheet.sheet_name,
                            "column": col.name,
                            "question": self._question_for_column(col.name),
                            "reason": col.ambiguity_reason or "ambiguous_column",
                        }
                    )
                if col.semantic_label == "unknown":
                    questions.append(
                        {
                            "sheet": sheet.sheet_name,
                            "column": col.name,
                            "question": f'Que significado economico/operativo tiene la columna "{col.name}" en la hoja "{sheet.sheet_name}"?',
                            "reason": "unknown_semantic",
                        }
                    )

        return {
            "file_name": profile.file_name,
            "owner_questions": questions,
            "question_count": len(questions),
            "status": "requires_owner_input" if questions else "no_questions",
        }

    def _question_for_column(self, column_name: str) -> str:
        lower = column_name.lower()
        for key, prompt in self._PROMPTS.items():
            if key in lower:
                return prompt.format(name=column_name)
        return f'La columna "{column_name}" es ambigua. Que concepto exacto representa en su operacion?'
