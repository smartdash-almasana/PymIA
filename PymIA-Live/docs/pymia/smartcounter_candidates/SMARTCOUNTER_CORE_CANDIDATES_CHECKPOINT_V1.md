# SmartCounter Core Candidates Checkpoint V1

## Estado

DOCUMENTARY_EXTRACTION_CREATED

## Fuente auditada

```text
E:\BuenosPasos\smartbridge\smartcounter_core
```

## Veredicto de fuente

```text
B) PARTIAL_VALUE_SOURCE
```

## Resumen

La fuente contiene un prototipo pequeño de conciliación de dos archivos/fuentes.

No es valiosa por su runtime.
No es valiosa por su ingesta.
No es valiosa por su normalización.

El valor está en sus invariantes:

```text
bloqueo por uncertainties
umbrales fuzzy matching 0.90 / 0.75
pipeline de conciliación en 5 etapas
modelo explícito Entity / Uncertainty / Finding
anti-duplicación 1:1 con matched_b_indices
priorización de findings por diferencia absoluta
```

## Archivos documentales creados

```text
PymIA-Live/docs/pymia/smartcounter_candidates/core_phase_1_first_aid.yaml
PymIA-Live/docs/pymia/smartcounter_candidates/core_cross_cutting.yaml
PymIA-Live/docs/pymia/smartcounter_candidates/core_do_not_migrate.yaml
PymIA-Live/docs/pymia/smartcounter_candidates/SMARTCOUNTER_CORE_CANDIDATES_CHECKPOINT_V1.md
```

## Conteo rescatado

```text
FIRST_AID_VALUE: 6
CROSS_CUTTING_VALUE: 8
DO_NOT_MIGRATE: 4
SPECIFIC_DIAGNOSIS_VALUE: 0
FULL_STRUCTURE_VALUE: 0
```

## Oro real extraído

### 1. Anti-oráculo por incertidumbre

```text
Si hay uncertainties, el flujo se bloquea.
No se fuerzan findings.
No se adivina matching.
```

Valor PymIA:

```text
Esto refuerza la regla: PymIA no diagnostica ni calcula como si supiera cuando la evidencia no alcanza.
```

### 2. Umbrales de matching

```text
AUTO_MATCH_THRESHOLD = 0.90
UNCERTAINTY_THRESHOLD = 0.75
```

Lectura PymIA:

```text
>= 0.90 puede ser match automático candidato.
>= 0.75 y < 0.90 debe ir a incertidumbre / validación humana.
< 0.75 no debe asumirse match.
```

### 3. Conciliación de dos fuentes

Patrón:

```text
ingest -> normalize -> resolve -> compare -> findings
```

Candidato First Aid:

```text
two_source_reconciliation_basic
```

Owner-facing:

```text
Conciliar dos fuentes parecidas.
```

### 4. Modelos de datos transversales

```text
Entity
Uncertainty
Finding
```

Lectura PymIA:

```text
No migrar dataclasses directamente.
Rescatar como contratos futuros de matching y conciliación.
```

### 5. Anti-duplicación 1:1

```text
matched_b_indices = set()
```

Valor:

```text
Evita usar la misma fila candidata para múltiples matches.
```

## No migrar

```text
ingestion.py
normalization.py
hardcoded product_name / quantity
__init__.py vacío
```

Motivo:

```text
Son stubs, schema estrecho o infraestructura sin valor de dominio.
```

## Impacto runtime

```text
runtime_touched: NO
kernel_touched: NO
pipeline_touched: NO
storage_touched: NO
diagnostic_core_touched: NO
```

## Decisión

```text
No copiar código.
Rescatar patrones.
Reimplementar en PymIA sólo con contratos, tests y adapters puros.
```

## Relación con slices actuales

Este rescate se apoya naturalmente en:

```text
Evidence Availability V1
Evidence Warning V1
```

Pero no los modifica.

## Próximo paso técnico recomendado

Primero terminar el slice pendiente:

```text
Evidence Warning Contract V1 -> correr tests -> checkpoint -> commit
```

Luego, si se decide activar este oro:

```text
Two Source Reconciliation Contract V1
```

posible ubicación:

```text
PymIA-Live/pymia/contracts/two_source_reconciliation_v1.json
PymIA-Live/pymia/contracts/two_source_reconciliation_v1.py
PymIA-Live/tests/contracts/test_two_source_reconciliation_v1.py
```

## Estado final

```text
SMARTCOUNTER_CORE_CANDIDATES_CHECKPOINT_V1 = CREATED
status: DOCUMENTARY_EXTRACTION_CREATED
runtime_touched: NO
verdict: PARTIAL_VALUE_SOURCE_WITH_HIGH_VALUE_FIRST_AID_PATTERNS
```
