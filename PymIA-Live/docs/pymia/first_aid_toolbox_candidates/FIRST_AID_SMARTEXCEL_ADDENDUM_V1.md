# First Aid SmartExcel Addendum V1

## Estado

CANDIDATE_ADDENDUM

## Propósito

Registrar SmartExcel como fuente auxiliar documental para Primeros Auxilios PyME / Fase 1, sin integrarlo todavía al inventario maestro ni al contrato principal.

Fuente base:

```text
PymIA-Live/docs/pymia/smartexcel_candidates/
```

Checkpoint fuente:

```text
PymIA-Live/docs/pymia/smartexcel_candidates/SMARTEXCEL_CANDIDATES_CHECKPOINT_V1.md
```

## Regla de alcance

Este addendum:

```text
no modifica FIRST_AID_MASTER_CANDIDATE_INVENTORY_V1.md
no modifica FIRST_AID_TOOLBOX_PACK_CONTRACT_V1.md
no activa runtime
no crea loader
no toca código
no toca kernel
```

SmartExcel queda como fuente auxiliar candidata, separada y trazable.

---

# 1. Veredicto de fuente

```text
B) PARTIAL_VALUE_SOURCE
```

SmartExcel contiene valor útil, pero también arrastra acoplamientos técnicos que no deben migrarse.

---

# 2. Resultado documental cerrado

```text
FIRST_AID_VALUE: 7
CROSS_CUTTING_VALUE: 13
DO_NOT_MIGRATE: 9
```

Archivos fuente creados:

```text
PymIA-Live/docs/pymia/smartexcel_candidates/phase_1_first_aid.yaml
PymIA-Live/docs/pymia/smartexcel_candidates/cross_cutting.yaml
PymIA-Live/docs/pymia/smartexcel_candidates/do_not_migrate.yaml
PymIA-Live/docs/pymia/smartexcel_candidates/SMARTEXCEL_CANDIDATES_CHECKPOINT_V1.md
```

---

# 3. Candidatos First Aid auxiliares

Los siguientes candidatos pueden ser considerados en una futura revisión del botiquín, pero no quedan integrados automáticamente.

```text
top_deudores_payload
structured_warnings_payload
mixed_amount_parsing_warning
exclude_ambiguous_amounts_rule
color_limit_disclaimer
excel_to_finding_to_summary_flow
recipient_routing_with_fallback
```

## Valor aportado

```text
ranking o resumen de deuda visible
warnings estructuradas
exclusión de montos ambiguos
declaración de limitaciones por color/formato
flujo archivo → hallazgo → resumen
ruteo conceptual con fallback
```

## Límite owner-facing

```text
SmartExcel sólo puede ayudar a observar y ordenar datos de archivos.
No confirma deuda legal.
No confirma cobrabilidad.
No confirma realidad organizacional fuera del archivo.
No diagnostica causa raíz.
```

---

# 4. Patrones transversales auxiliares

SmartExcel aporta patrones conceptuales potencialmente reutilizables:

```text
structured_warning_contract
parsing_confidence_flag
ambiguous_value_quarantine
technical_warning_to_owner_copy
finding_summary_boundary
channel_agnostic_delivery
delivery_fallback_reason
input_file_observation_boundary
local_path_redaction_rule
evidence_payload_minimal_shape
warning_severity_levels
calculation_exclusion_trace
human_review_trigger_for_ambiguity
```

Estos patrones son transversales y no pertenecen exclusivamente a Primeros Auxilios.

---

# 5. Cuarentena

SmartExcel incluye elementos no migrables por estar acoplados a infraestructura, canales concretos, librerías concretas, rutas locales o scripts operativos.

La cuarentena queda resumida en:

```text
PymIA-Live/docs/pymia/smartexcel_candidates/do_not_migrate.yaml
```

Regla:

```text
Sólo pueden rescatarse patrones conceptuales.
Nunca migrar piezas operativas o dependencias concretas desde SmartExcel.
```

---

# 6. Relación con el master inventory

Estado actual:

```text
SmartExcel NO está integrado al master inventory.
SmartExcel NO altera conteos del master inventory.
SmartExcel NO altera el pack contract.
```

Master inventory vigente:

```text
PymIA-Live/docs/pymia/first_aid_toolbox_candidates/FIRST_AID_MASTER_CANDIDATE_INVENTORY_V1.md
```

Pack contract vigente:

```text
PymIA-Live/docs/pymia/first_aid_toolbox_candidates/FIRST_AID_TOOLBOX_PACK_CONTRACT_V1.md
```

---

# 7. Decisión futura posible

Si se decide incorporar SmartExcel al inventario maestro, debe hacerse como addendum o versión nueva, nunca como edición silenciosa.

Opciones futuras:

```text
A) mantener SmartExcel separado
B) crear FIRST_AID_MASTER_CANDIDATE_INVENTORY_V1_SMARTEXCEL_ADDENDUM
C) crear FIRST_AID_MASTER_CANDIDATE_INVENTORY_V2 con SmartExcel incluido
```

Requiere decisión HITL explícita.

---

# 8. Estado de cierre

```text
FIRST_AID_SMARTEXCEL_ADDENDUM_V1 = CREATED
status: CANDIDATE_ADDENDUM
runtime_impact: NONE
code_impact: NONE
tests_run: NO
```
