"""CLI mínimo para demo del slice de interrogatorio SmartPyme.

Uso:
    python -m pymia.smartpyme.interrogation_cli
    python -m pymia.smartpyme.interrogation_cli --demo-out output/interrogation_demo.json
    python -m pymia.smartpyme.interrogation_cli --text "No me cierra la plata"

No requiere --tenant-id ni --input. No toca Hermes, Output Gateway ni producción.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List

from pymia.smartpyme.interrogation import (
    StructuredSelectors,
    run_interrogation,
)


DEMO_CASES: List[Dict] = [
    {
        "case_id": "case_01_descuadre",
        "raw_text": "No me cierra la plata",
        "selectors": None,
    },
    {
        "case_id": "case_02_margen",
        "raw_text": "Vendo mucho pero no me queda nada",
        "selectors": None,
    },
    {
        "case_id": "case_03_proveedores",
        "raw_text": "Tengo proveedores duplicados y CUIT mezclados",
        "selectors": {"evidence_available": "Excel"},
    },
    {
        "case_id": "case_04_stock",
        "raw_text": "El sistema dice un stock y el depósito otro",
        "selectors": None,
    },
    {
        "case_id": "case_05_sobrecarga",
        "raw_text": "Copio todos los días de un Excel a otro",
        "selectors": None,
    },
]


def _selectors_from_dict(d: Dict | None) -> StructuredSelectors | None:
    if not d:
        return None
    return StructuredSelectors(**{k: v for k, v in d.items()
                                   if k in StructuredSelectors.__dataclass_fields__})


def _run_demo_cases() -> List[Dict]:
    results = []
    for case in DEMO_CASES:
        selectors = _selectors_from_dict(case.get("selectors"))
        r = run_interrogation(case["raw_text"], structured_selectors=selectors)
        payload = r.to_dict()
        payload["case_id"] = case["case_id"]
        results.append(payload)
    return results


def _run_single(text: str) -> Dict:
    r = run_interrogation(text)
    return r.to_dict()


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="interrogation_cli",
        description="SmartPyme — slice mínimo de interrogatorio taxonómico",
    )
    parser.add_argument("--demo-out", type=str, default=None,
                        help="Ruta donde escribir el JSON de la demo (5 casos).")
    parser.add_argument("--text", type=str, default=None,
                        help="Relato crudo único para procesar.")
    parser.add_argument("--pretty", action="store_true",
                        help="Indentar JSON de salida.")
    args = parser.parse_args(argv)

    indent = 2 if args.pretty else None

    if args.demo_out:
        results = _run_demo_cases()
        os.makedirs(os.path.dirname(os.path.abspath(args.demo_out)), exist_ok=True)
        with open(args.demo_out, "w", encoding="utf-8") as f:
            json.dump({"cases": results}, f, ensure_ascii=False, indent=indent)
        print(f"[OK] Demo escrita en: {args.demo_out}")
        print(f"[OK] Casos procesados: {len(results)}")
        for r in results:
            print(f"  - {r['case_id']}: status={r['status']}, "
                  f"symptoms={r['candidate_symptoms']}, "
                  f"classification={r['suggested_classification']}")
        return 0

    if args.text:
        result = _run_single(args.text)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    # Si no hay argumentos, imprimir ayuda y correr demo en stdout
    parser.print_help()
    print("\n-- Ejemplo rápido (stdout): --")
    results = _run_demo_cases()
    print(json.dumps({"cases": results}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
