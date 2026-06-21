# SmartD Candidates Checkpoint V1

## Estado

CLOSED_CANDIDATE

## Fuente auditada

```text
E:\BuenosPasos\smartd-dashb-clean\docs
```

## Alcance

Selección documental de información valiosa para PymIA / SmartPyme en sus tres servicios:

1. Primeros Auxilios PyME
2. Problema específico / diagnóstico sectorial
3. Estructura completa de la empresa

No se migra runtime.
No se migra código.
No se activan herramientas.
No se modifican contratos vivos.
No se ejecutan tests.

## Archivos creados

```text
PymIA-Live/docs/pymia/smartd_candidates/phase_1_first_aid.yaml
PymIA-Live/docs/pymia/smartd_candidates/phase_2_diagnostic.yaml
PymIA-Live/docs/pymia/smartd_candidates/phase_3_full_structure.yaml
PymIA-Live/docs/pymia/smartd_candidates/cross_cutting.yaml
PymIA-Live/docs/pymia/smartd_candidates/do_not_migrate.yaml
```

## Resultado de selección

```text
FIRST_AID_VALUE: 8
SPECIFIC_DIAGNOSIS_VALUE: 12
FULL_STRUCTURE_VALUE: 9
CROSS_CUTTING_VALUE: 13
DO_NOT_MIGRATE: 18
```

## Decisiones de gobierno

Todo lo seleccionado queda como candidato documental.

Ningún ítem entra directo al kernel.
Ningún ítem queda habilitado para runtime.
Ningún ítem queda aprobado como pack ejecutable.

Cualquier migración futura requiere decisión HITL explícita.

## Valor principal detectado

```text
MEASURED / ZERO_REAL / NOT_AVAILABLE
Health Score con decay
Top 7 preguntas clínicas
Evidence > Opinión
Clinical Scenarios Taxonomy
Memoria caliente / expediente archivado
KB / Core / Runtime layers
Owner-facing copy
Coverage caps
Weekly Brief structure
```

## Cuarentena

Los elementos acoplados a MercadoLibre, Shopify, Supabase, Vercel, MCP, SQL específico, endpoints específicos o agentes concretos quedaron en:

```text
do_not_migrate.yaml
```

Sólo se permite rescatar patrones conceptuales si se documentan aparte y se reevalúan con HITL.

## Próximo frente lógico

Unificar candidatos de Primeros Auxilios provenientes de:

```text
Exceland
SmartCounter
SmartD
```

en un inventario maestro documental de Primeros Auxilios PyME.

Archivo sugerido:

```text
PymIA-Live/docs/pymia/first_aid_toolbox_candidates/FIRST_AID_MASTER_CANDIDATE_INVENTORY_V1.md
```

## Cierre

El frente SmartD queda cerrado como fuente candidata documental.

Estado:

```text
CLOSED_CANDIDATE
```
