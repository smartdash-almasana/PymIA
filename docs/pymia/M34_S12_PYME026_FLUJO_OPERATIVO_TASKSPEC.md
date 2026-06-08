# M34-S12 — PYME_026 Flujo Operativo TaskSpec

Fecha: 2026-06-07
Frente activo: `DIAGNOSTIC_CORE_V1`
Slice: `M34-S12_PYME_026_FLUJO_OPERATIVO`

---

## Objetivo

Implementar soporte determinístico para la fórmula:

```text
PYME_026_flujo_operativo
```

---

## Fuente obligatoria

Codex debe tomar la expresión exacta, inputs, output_unit y bloqueo esperado desde:

```text
docs/formula_catalog.v1.json
```

Entrada del catálogo:

```text
formula_id: PYME_026_flujo_operativo
```

No inventar variables si el catálogo ya las define.

---

## Archivos permitidos

```text
pymia/contracts/formula_contract.py
pymia/services/formula_engine_service.py
pymia/diagnostic_core/core.py
tests/services/test_formula_engine_service.py
tests/diagnosticcore/test_diagnostic_core_v1.py
docs/pymia/M34_S12_PYME026_FLUJO_OPERATIVO_TASKSPEC.md
```

---

## Archivos prohibidos

```text
pymia/smartpyme/
conversa-engine/
tools/
SmartPyme/
docs/formula_catalog.v1.json
docs/pathology_catalog.v1.json
```

---

## Reglas

1. Agregar `PYME_026_flujo_operativo` a `SUPPORTED_FORMULAS`.
2. Implementar cálculo según expresión exacta del catálogo.
3. Requerir exactamente las variables del catálogo.
4. Bloquear si falta cualquier input.
5. Bloquear división por cero sólo si la fórmula tiene divisor.
6. Permitir cero o negativo si la fórmula aritmética lo permite.
7. Preservar `source_refs`.
8. `DiagnosticCoreV1` debe mantener `CANDIDATE`, no `CONFIRMED`.
9. No cambiar comportamiento de fórmulas previas.

---

## Tests obligatorios

1. Test cálculo OK con valores simples y resultado verificable.
2. Test input faltante para el último input requerido del catálogo.
3. Test cero o negativo si aplica.
4. Test división por cero si aplica.
5. Test integración `DiagnosticCoreV1` con `CANDIDATE`, no `CONFIRMED`.
6. Test `source_refs` preservados.

---

## Validación focal

```powershell
python -m pytest tests/services/test_formula_engine_service.py -v
python -m pytest tests/diagnosticcore/test_diagnostic_core_v1.py -v
```

---

## PASS

PASS si:

```text
- PYME_026_flujo_operativo implementa exactamente el catálogo;
- inputs faltantes bloquean;
- casos límite aplicables cubiertos;
- source_refs se preservan;
- DiagnosticCoreV1 mantiene CANDIDATE, no CONFIRMED;
- no se alteran fórmulas previas;
- tests focales pasan;
- commit local sin push.
```

---

## Salida obligatoria Codex

```text
VEREDICTO
FORMULA_FROM_CATALOG
FILES CHANGED
DIFF SUMMARY
TEST RESULTS
COMMIT HASH
GIT STATUS FINAL
CONFIRMACIÓN NO PUSH
```
