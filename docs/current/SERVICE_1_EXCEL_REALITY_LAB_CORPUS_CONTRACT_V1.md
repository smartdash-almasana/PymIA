# Servicio 1 — Excel Reality Lab Corpus Contract V1

**Fecha:** 2026-08-15  
**Estado:** ACTIVE / A0

## Propósito

Definir un único contrato versionado para el corpus físico de Excel de Servicio 1, reutilizando el corpus existente y evitando crear fixtures, parsers o caminos productivos paralelos sin gobierno.

Fuente semilla existente:

```text
tools/service_1_physical_xlsx_product_readiness_corpus_v1.py
```

Manifest canónico del Reality Lab:

```text
docs/service_1_excel_reality_lab_corpus.v1.json
```

## Semilla absorbida

Se incorporan como semilla los 7 casos físicos ya existentes:

```text
S1-PHY-001 ventas/margen
S1-PHY-002 textil/ventas
S1-PHY-003 textil/compras
S1-PHY-004 textil/stock
S1-PHY-005 cobranzas
S1-PHY-006 taller/stock
S1-PHY-007 caja-banco control
```

La evidencia previa sobre estos casos certifica únicamente readiness semántica del corpus aprobado. No se proyecta de forma retroactiva computabilidad P8, ejecución, delivery ni producción para cada caso.

Por eso todos ingresan al nuevo manifest como:

```text
coverage_lane = SEMANTIC_ONLY_SEED
structure_profile_status = PENDING_A1
calculation_profile_status = PENDING_A2
expected_outcome = NOT_YET_EXECUTED
```

## Campos obligatorios por caso

```text
case_id
rubro
fixture
sheet_name
coverage_lane
source_kind
sanitization_status
structure_profile_status
calculation_profile_status
capability_target
expected_outcome
provenance
```

## Estados de resultado permitidos

```text
PASS_COMPUTABLE
PASS_NEEDS_OWNER
PASS_NEEDS_EVIDENCE
PASS_BLOCKED_FAIL_CLOSED
FAIL_DEFECT
NOT_YET_EXECUTED
```

`FAIL_DEFECT` no autoriza una solución ad hoc. Exige reproducción, causa y cambio mínimo.

## Carriles de cobertura

```text
SEMANTIC_ONLY_SEED
STRUCTURAL
CALCULATION
RUBRO
ADVERSARIAL
REAL_CLIENT_SHADOW
```

## Política de fixtures

1. El root físico canónico es `prueba_excels/`.
2. Todo fixture debe existir físicamente y estar referenciado por manifest.
3. Datos de clientes reales requieren sanitización o autorización explícita antes de entrar al repo.
4. Ningún fixture concede autoridad productiva por sí mismo.
5. No se crea un segundo parser XLSX para ampliar cobertura.

## Meta de expansión

```text
minimum_cases = 20
target_cases = 30
```

Rubros mínimos:

```text
comercio_minorista
mayorista_distribuidora
textil
produccion_fabrica
servicios_profesionales_estudio_contable
gastronomia
administracion_consorcios
mercado_libre_mercado_pago
```

Los rubros son contexto de corpus, no nuevas capabilities.

## Gate A0

A0 sólo puede cerrar si:

```text
CORPUS_SCHEMA: PASS
TRACEABILITY: PASS
SEED_ABSORPTION: PASS
FIXTURE_EXISTENCE: PASS
NO_UNGOVERNED_FIXTURES: PASS para los casos declarados
NO_SECOND_XLSX_PARSER: PRESERVED
NO_NEW_PRODUCT_AUTHORITY: PRESERVED
```

## Auditoría requerida

No se requiere auditoría arquitectónica global.

Se requiere una auditoría puntual de A0 al cierre para verificar:

```text
- el manifest refleja exactamente la semilla adoptada;
- no inventa evidencia de computabilidad o ejecución;
- no introduce una nueva authority;
- no introduce un segundo parser;
- el crecimiento futuro del corpus queda gobernado por el mismo contrato.
```

## Regla rectora

```text
un Excel nuevo
→ un caso gobernado
→ una ejecución
→ una clasificación
→ una evidencia
→ una decisión
```

Nunca:

```text
un Excel raro
→ una excepción ad hoc
→ nueva deriva arquitectónica
```
