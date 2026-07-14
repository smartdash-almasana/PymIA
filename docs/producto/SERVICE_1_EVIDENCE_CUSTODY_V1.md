# SERVICE_1_EVIDENCE_CUSTODY_V1

## Estado

```text
EVIDENCE_DISCIPLINE_PROTOCOL
READY_FOR_CONTROLLED_SERVICE_1_CASES
RUNTIME_IMPACT: NONE
CODE_IMPACT: NONE
TEST_IMPACT: NONE
```

## Veredicto

```text
SERVICE_1_EVIDENCE_CUSTODY_V1: READY
REAL_FILE_TRACKING_REQUIRED: YES
NEW_STORAGE_BACKEND_ALLOWED: NO
CLIENT_XLSX_IN_REPO_ALLOWED: NO
MINIMAL_HASH_OR_STABLE_REF_REQUIRED: YES
```

## Propósito

Definir la disciplina mínima de custodia de evidencia para Servicio 1 cuando se trabaje con casos controlados, reales anonimizados o sintéticos.

Este documento no crea storage nuevo.

Este documento no autoriza mover archivos reales al repo.

Su función es fijar:

- qué archivo o evidencia se usó en cada caso;
- en qué estado quedó;
- qué nivel de anonimización tiene;
- qué uso está permitido;
- qué evidencia quedó fuera o bloqueada;
- qué humano es responsable de la revisión.

## Por qué existe

La auditoría de madurez marcó este faltante explícitamente:

```text
Evidence custody = INSUFFICIENT
Falta hash / custodia / estado por archivo real como disciplina central.
```

Y el corpus recién creado necesita una capa mínima de control para que los rehearsals no dependan de memoria informal.

## Quick path

1. Registrar cada archivo o pieza de evidencia usada por un caso.
2. Marcar si es real anonimizada o sintética controlada.
3. Indicar estado, restricciones y responsable humano.

## Regla central

```text
Servicio 1 puede revisar evidencia controlada,
pero debe poder explicar exactamente qué archivo usó,
qué archivo no usó,
qué nivel de anonimización tiene,
y por qué ese archivo no se convirtió en evidencia validada final.
```

## Qué cuenta como evidencia bajo custodia

Puede entrar bajo custodia:

```text
XLSX principal del caso
XLSX auxiliar permitido
CSV auxiliar convertido fuera del repo y resumido como referencia
extracto bancario anonimizado
liquidación anonimizada
workpaper base anonimizado
nota operatoria de diferencias visibles
nota operatoria de faltantes de evidencia
```

No debe entrar:

```text
credenciales
tokens
APIs vivas
OCR raws sensibles
archivos reales no anonimizados dentro del repo
dump completo sin recorte
```

## Unidad mínima de custodia

Cada pieza bajo custodia debe poder registrarse como:

```yaml
case_id: string
asset_id: string
asset_role: primary | auxiliary | excluded
source_type: real_anonymized | synthetic_controlled
file_type: xlsx | csv | pdf | image | text | unknown
file_name_alias: string
period_scope: string | null
anonymization_status: REQUIRED | PARTIAL | VERIFIED
allowed_usage: intake_only | review_only | rehearsal_only
custody_status: RECEIVED | ACCEPTED | EXCLUDED | BLOCKED | SUPERSEDED
stable_ref_or_hash: string
excluded_data: list
known_risks: list
review_owner: string
notes: list
```

## Campos obligatorios

| Campo | Obligatorio | Motivo |
|---|---:|---|
| `case_id` | sí | ligar la evidencia al caso |
| `asset_id` | sí | identificar la pieza concreta |
| `asset_role` | sí | distinguir principal, auxiliar o excluida |
| `source_type` | sí | distinguir real anonimizada de sintética |
| `file_type` | sí | saber qué familia de archivo se está usando |
| `file_name_alias` | sí | evitar nombre real sensible |
| `anonymization_status` | sí | no trabajar “asumiendo” anonimización |
| `allowed_usage` | sí | limitar uso permitido |
| `custody_status` | sí | saber si entra, se bloquea o se excluye |
| `stable_ref_or_hash` | sí | referencia estable mínima |
| `review_owner` | sí | responsable humano |

## Regla de referencia estable

Servicio 1 V1 todavía no necesita un backend sofisticado ni hashing productivo complejo.

Pero sí necesita una referencia estable mínima:

```text
hash corto
o file fingerprint local
o asset_ref estable manual
```

Lo importante no es el algoritmo perfecto.

Lo importante es evitar:

```text
“creo que usamos este archivo”
“no sé si era esta versión”
“no recuerdo si estaba anonimizado”
```

## Estados de custodia permitidos

| Estado | Significado |
|---|---|
| `RECEIVED` | llegó pero todavía no fue aceptada para uso |
| `ACCEPTED` | puede usarse dentro del caso controlado |
| `EXCLUDED` | existe pero queda fuera del uso permitido |
| `BLOCKED` | no puede usarse por riesgo, alcance o anonimización |
| `SUPERSEDED` | fue reemplazada por una versión más segura o correcta |

## Regla de anonimización

### `REQUIRED`

Todavía falta anonimizar o no hay confirmación suficiente.

No puede pasar a `ACCEPTED`.

### `PARTIAL`

Hay ocultamiento inicial, pero todavía quedan dudas.

Puede quedar:

```text
BLOCKED
o EXCLUDED
```

según riesgo.

### `VERIFIED`

El operador confirmó que:

```text
no quedan identificadores sensibles innecesarios
no quedan credenciales
el archivo es apto para rehearsal asistido
```

## Allowed usage

### `intake_only`

El archivo sólo sirve para clasificación inicial.

### `review_only`

El archivo puede entrar a revisión humana controlada.

### `rehearsal_only`

El archivo puede entrar a rehearsal completo del flujo asistido.

Ningún valor autoriza:

```text
runtime autónomo
entrega final al cliente
subida al repo
```

## Criterios de aceptación bajo custodia

Aceptar una pieza sólo si:

```text
está ligada a un case_id
tiene alias seguro
tiene anonymization_status verificable
tiene stable_ref_or_hash
tiene review_owner
su allowed_usage es explícito
no contiene credenciales ni riesgo vivo
```

## Criterios de bloqueo bajo custodia

Bloquear una pieza si aparece cualquiera de estos:

```text
NO_STABLE_REF
ANONYMIZATION_NOT_VERIFIED
LIVE_CREDENTIALS_PRESENT
UNSCOPED_FILE_DUMP
REAL_IDENTIFIER_NOT_REMOVED
UNSUPPORTED_USAGE_REQUESTED
NO_REVIEW_OWNER
```

## Decisiones permitidas

Cada pieza puede terminar en una de estas decisiones:

| Decisión | Resultado |
|---|---|
| `ACCEPT_FOR_REHEARSAL` | pasa a `ACCEPTED` |
| `BLOCK_UNTIL_ANONYMIZED` | pasa a `BLOCKED` |
| `EXCLUDE_FROM_CASE` | pasa a `EXCLUDED` |
| `REPLACE_WITH_SAFE_VERSION` | la previa queda `SUPERSEDED` |

## Ejemplos de uso correcto

### Caso 1 — XLSX principal anonimizado

```text
source_type = real_anonymized
file_type = xlsx
asset_role = primary
anonymization_status = VERIFIED
allowed_usage = rehearsal_only
custody_status = ACCEPTED
```

### Caso 2 — PDF auxiliar no apto como fuente primaria

```text
source_type = real_anonymized
file_type = pdf
asset_role = auxiliary
allowed_usage = intake_only
custody_status = EXCLUDED
```

### Caso 3 — Archivo con identificadores no removidos

```text
anonymization_status = REQUIRED
custody_status = BLOCKED
known_risks = [REAL_IDENTIFIER_NOT_REMOVED]
```

## Relación con artefactos existentes

| Artefacto | Rol |
|---|---|
| `SERVICE_1_VALIDATION_CASE_CORPUS_V1` | define qué casos deben existir |
| `SERVICE_1_EVIDENCE_CUSTODY_V1` | define cómo rastrear la evidencia de esos casos |
| `SERVICE_1_XLSX_ACCEPTANCE_AND_BLOCKING_PROTOCOL_V1` | define si el archivo/caso entra o no |
| `SERVICE_1_REVIEW_CHECKLIST_V1` | define si la corrida puede seguir o bloquearse |

## PASS / FAIL

### PASS

La disciplina de custodia pasa si:

```text
cada pieza usada en un rehearsal tiene referencia estable
source_type y anonymization_status son explícitos
allowed_usage y custody_status son explícitos
hay review_owner identificado
no hay archivos reales sensibles dentro del repo
```

### FAIL

La disciplina falla si:

```text
no se sabe qué archivo se usó
no se sabe si fue anonimizado
no se sabe si era principal o auxiliar
no hay responsable humano
aparecen archivos reales no protegidos en el repo
```

## Non-goals

Este documento no autoriza:

```text
storage backend nuevo
hashing fuerte obligatorio en esta fase
subir XLSX de clientes al repo
persistencia automática
delivery final
runtime autónomo
```

## Próximo paso correcto

```text
SERVICE_1_EXECUTABLE_ENTRYPOINT_V1
```

Porque después de intake, review, corpus y custodia, el siguiente cuello real es abrir una entrada ejecutable asistida y controlada para correr un caso de Servicio 1 end-to-end.
