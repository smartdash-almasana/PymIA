# SERVICE_1_VALIDATION_CASE_CORPUS_V1

## Estado

```text
VALIDATION_CORPUS_CATALOG
READY_FOR_CONTROLLED_SERVICE_1_REHEARSALS
RUNTIME_IMPACT: NONE
CODE_IMPACT: NONE
TEST_IMPACT: NONE
```

## Veredicto

```text
SERVICE_1_VALIDATION_CASE_CORPUS_V1: READY
REAL_CLIENT_FILES_IN_REPO_ALLOWED: NO
ANONYMIZED_CONTROLLED_CASES_REQUIRED: YES
MINIMUM_INITIAL_CORPUS: 4
```

## Propósito

Definir el corpus mínimo de casos controlados con el que Servicio 1 debe validarse antes de llamarse funcional de forma repetible.

Este documento no agrega archivos reales al repo.

Su función es fijar:

- qué tipos de caso deben existir;
- qué estructura mínima debe tener cada caso;
- qué niveles de anonimización son obligatorios;
- qué criterio de PASS/BLOCK aplica al rehearsal del caso.

## Por qué existe

La auditoría de madurez ya marcó esto como un faltante crítico:

```text
Real anonymized corpus = INSUFFICIENT
```

Y además dejó claro que Servicio 1:

```text
no debe medirse por marketing ni por demos,
sino por capacidad de repetir flujos sobre casos controlados.
```

## Quick path

1. Definir un conjunto pequeño de casos tipo.
2. Prepararlos en forma anonimizada y controlada.
3. Repetir sobre ellos el flujo de Servicio 1 con intake, review humana y decisión segura.

## Qué cuenta como “caso” en este corpus

Un caso del corpus es:

```text
una unidad de validación operativa
con problema concreto
archivo o conjunto de archivos delimitado
familia operativa explícita
resultado esperado de alto nivel
riesgos conocidos
criterio de bloqueo si falta algo
```

No es:

```text
un cliente real sin anonimizar
un benchmark comercial
una demo libre
un caso sin alcance acotado
```

## Regla central

```text
El corpus valida repetibilidad operativa, no exactitud contable final.
```

## Familias mínimas del corpus inicial

El corpus V1 debe tener al menos 4 casos:

| Caso | Familia | Motivo |
|---|---|---|
| `CASE_01_XLSX_TRIAGE` | `excel_triage` | núcleo más alineado con Servicio 1 |
| `CASE_02_COLUMN_CONFIRMATION` | `column_confirmation` | valida intake + owner-facing + reentry controlado |
| `CASE_03_INVOICE_COLLECTION_REVIEW` | `invoice_collection_review` | cubre una familia fuerte de evidencia operativa |
| `CASE_04_BANK_RECON_PREPARATION` | `bank_reconciliation_preparation` | cubre una familia distinta con riesgo de sobreclaim |

### Caso opcional recomendado

```text
CASE_05_ACCOUNTING_WORKPAPER_PREPARATION
```

para validar el frente contadores sin convertirlo en cierre profesional final.

## Estructura mínima por caso

Cada caso del corpus debe registrar como mínimo:

```yaml
case_id: string
case_family: enum
case_status: READY_FOR_REHEARSAL | BLOCKED
source_type: real_anonymized | synthetic_controlled
primary_file_type: xlsx
period_scope: string
owner_problem: string
expected_service_1_role: string
minimum_files_expected: list
known_missing_evidence: list
known_risks: list
expected_safe_outcome: string
forbidden_claims: list
review_notes: list
```

## Niveles de fuente permitidos

### Permitido

```text
real_anonymized
synthetic_controlled
```

### No permitido

```text
real_identifiable_client_file_in_repo
live_credentials
raw banking secrets
fiscal secrets without redaction
unbounded folder dumps
```

## Regla de anonimización

Antes de que un caso entre al corpus debe cumplir:

```text
- nombres comerciales reemplazables por alias
- personas reemplazables por alias
- CUIT/DNI/CBU/token/credencial removidos o irreversiblemente ocultos
- cuentas bancarias completas removidas
- datos sensibles no necesarios removidos
- macros no confiables removidas o bloqueadas
```

## Resultado esperado por familia

### `CASE_01_XLSX_TRIAGE`

Debe permitir validar:

```text
intake aceptado
lectura owner-facing inicial
faltantes visibles
próxima acción segura
```

### `CASE_02_COLUMN_CONFIRMATION`

Debe permitir validar:

```text
columnas ambiguas o discutibles
pregunta visible al dueño
reentry gobernado
candidate bridge sin evidence promotion
```

### `CASE_03_INVOICE_COLLECTION_REVIEW`

Debe permitir validar:

```text
descalce operativo visible
faltantes de evidencia explícitos
sin cierre definitivo de saldos
```

### `CASE_04_BANK_RECON_PREPARATION`

Debe permitir validar:

```text
preparación de revisión bancaria
advertencias visibles
sin conciliación definitiva
```

### `CASE_05_ACCOUNTING_WORKPAPER_PREPARATION` (opcional)

Debe permitir validar:

```text
paquete base para trabajo contable
límites explícitos
sin claims profesionales finales
```

## Criterio de PASS por caso

Un caso pasa el rehearsal de Servicio 1 si:

```text
entra por el protocolo XLSX-first
pasa review checklist humana
produce output owner-facing prudente
si requiere reentry, lo hace sin promover evidencia
deja faltantes y límites visibles
no dispara claims prohibidos
```

## Criterio de FAIL por caso

Un caso falla si:

```text
no puede anonimizarse de forma segura
requiere OCR o parser nuevo para existir
requiere API viva
requiere diagnóstico final
mezcla múltiples frentes sin recorte
la próxima acción segura no puede formularse
```

## Artefactos esperados por cada caso

Cada caso del corpus debería poder producir o registrar:

```text
intake decision
case family
owner-facing message
known missing evidence
known visible differences
review decision
next safe action
```

No requiere todavía:

```text
XLSX final productivo
chatbot
runtime autónomo
evidencia validada final
```

## Checklist para admitir un caso al corpus

```text
[ ] La familia del caso es compatible con Servicio 1.
[ ] El archivo principal es XLSX o puede reducirse a XLSX.
[ ] El caso tiene problema concreto.
[ ] El período o recorte es explícito.
[ ] El caso puede anonimizarse.
[ ] No requiere credenciales ni APIs.
[ ] No requiere OCR.
[ ] No promete cierre final.
[ ] Tiene expected_safe_outcome definido.
[ ] Tiene known_risks definidos.
```

## Decisiones permitidas sobre el corpus

Cada caso puede quedar en uno de estos estados:

| Estado | Significado |
|---|---|
| `READY_FOR_REHEARSAL` | Caso apto para correr bajo flujo asistido |
| `BLOCKED_NEEDS_ANONYMIZATION` | No puede entrar hasta anonimizarse bien |
| `BLOCKED_BY_SCOPE` | Caso demasiado amplio o fuera de familia |
| `BLOCKED_BY_RISK` | Requiere APIs, OCR, credenciales o claims fuera de alcance |

## Non-goals

Este documento no autoriza:

```text
subir archivos reales al repo
guardar XLSX de clientes
armar benchmark comercial
ejecutar casos automáticamente
prometer cobertura total de patologías
```

## Próximo paso correcto

```text
SERVICE_1_EVIDENCE_CUSTODY_V1
```

Porque una vez definido el corpus, el siguiente faltante fuerte es disciplinar qué archivo real/controlado se usó, en qué estado, y bajo qué custodia mínima.
