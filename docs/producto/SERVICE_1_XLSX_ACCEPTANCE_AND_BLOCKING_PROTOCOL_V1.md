# SERVICE_1_XLSX_ACCEPTANCE_AND_BLOCKING_PROTOCOL_V1

## Estado

```text
PRODUCT_OPERATION_PROTOCOL
READY_FOR_ASSISTED_SERVICE_1_INTAKE
RUNTIME_IMPACT: NONE
CODE_IMPACT: NONE
TEST_IMPACT: NONE
```

## Veredicto

```text
SERVICE_1_XLSX_ACCEPTANCE_AND_BLOCKING_PROTOCOL_V1: READY
PRIMARY_ACCEPTED_FORMAT: XLSX
AUTONOMOUS_RUNTIME_ALLOWED: NO
OWNER_OUTPUT_ALLOWED: YES
HUMAN_REVIEW_REQUIRED: YES
```

## Propósito

Definir cuándo un archivo puede entrar a Servicio 1 como evidencia operativa inicial, cuándo debe bloquearse y cuál es la próxima acción segura para el dueño u operador.

Este protocolo existe para cerrar una brecha marcada por las auditorías:

```text
Servicio 1 tiene owner-facing output y varias piezas reales,
pero todavía necesita un protocolo explícito de aceptación/bloqueo por tipo de archivo y familia de problema.
```

## Quick path

1. Recibir un archivo y clasificarlo con criterio XLSX-first.
2. Aceptar sólo si entra como evidencia tabular segura y alcance acotado.
3. Bloquear o pedir corrección si el archivo, el alcance o la expectativa exceden Servicio 1.

## Qué resuelve

Este protocolo responde:

```text
qué archivo entra
qué archivo se bloquea
qué expectativas del dueño son compatibles con Servicio 1
qué riesgos obligan a frenar
qué mensaje seguro se devuelve en cada caso
```

No resuelve:

```text
diagnóstico
recalculation
delivery XLSX final
conciliación definitiva
automatización
chatbot libre
LLM runtime
OCR
parsers nuevos
```

## Relación con piezas existentes

| Pieza existente | Rol en este protocolo |
|---|---|
| `pymia/smartpyme/file_intake_v1.py` | Clasificación técnica inicial del archivo |
| `pymia/smartpyme/file_intake_taskspec_boundary_v1.py` | Traducción a patch técnico |
| `docs/producto/SERVICE_1_QA_DELIVERY_CHECKLIST_V1.md` | Gate posterior a la salida, no gate de intake |
| `docs/producto/SERVICE_1_DEVELOPMENT_AUDIT_AND_COMPLETION_ROADMAP_V1.md` | Justifica que falta tool ejecutable y cierre operativo |
| `docs/producto/SERVICE_1_CAPABILITY_MATURITY_AUDIT_V1.md` | Justifica que falta protocolo explícito de aceptación/bloqueo |

## Regla central

```text
Servicio 1 acepta primero evidencia tabular operable.
No acepta promesas de diagnóstico, cierre contable final, auditoría ni autonomía.
```

## Formato primario aceptado

### Aceptado en V1

```text
XLSX
```

Motivo:

```text
File Intake V1 ya es XLSX-first y puede enrutar de forma segura hacia document_ingestion_xlsx.
```

### No aceptados en V1 como fuente primaria

```text
CSV
PDF
ZIP
image
text
unknown
```

Estos formatos pueden existir como contexto futuro o auxiliar, pero no habilitan la entrada operativa principal en este protocolo.

## Familias de caso compatibles

El archivo puede aceptarse sólo si el caso entra en una familia operativa compatible con Servicio 1 asistido.

### Compatibles

```text
primeros_auxilios_xlsx
excel_triage
column_confirmation
invoice_collection_review
bank_reconciliation_preparation
accounting_workpaper_preparation
```

### Incompatibles o fuera de alcance

```text
diagnostico_integral
auditoria
certificacion
validacion_fiscal
conciliacion_definitiva
asientos_automaticos
ocr_required
api_required
marketplace_live_integration
chatbot_autonomo
```

## Criterios de aceptación

Aceptar el archivo sólo si todas estas condiciones se cumplen:

### A. Archivo

```text
- el archivo es XLSX
- el archivo no está vacío
- el nombre es seguro
- no hay mismatch crítico entre extensión y MIME
- el archivo puede tratarse como evidencia tabular
```

### B. Alcance

```text
- el dueño expresa una pregunta o problema operativo concreto
- el caso está acotado a una familia compatible
- el período o recorte es explícito o pedible de forma razonable
- el dueño no espera diagnóstico final ni dictamen
```

### C. Riesgo

```text
- no se recibieron credenciales, tokens ni accesos vivos
- no se pidió API bancaria, Mercado Pago API o integración viva
- no se requiere OCR
- no se exige parser nuevo antes de revisar
- el operador puede mantener human_review_required = true
```

## Criterios de bloqueo

Bloquear el intake si aparece cualquiera de estos casos:

### Bloqueo por archivo

```text
EMPTY_FILE
UNSAFE_FILENAME
MIME_EXTENSION_MISMATCH
UNKNOWN_FILE_TYPE
UNSUPPORTED_CSV_V1
UNSUPPORTED_PDF_V1
UNSUPPORTED_ZIP_V1
UNSUPPORTED_IMAGE_V1
UNSUPPORTED_TEXT_V1
```

### Bloqueo por alcance

```text
SCOPE_NOT_SUPPORTED
NO_OWNER_PROBLEM_DEFINED
NO_PERIOD_OR_REVIEW_WINDOW
MULTIPLE_FRONTS_WITHOUT_CUT
EXPECTS_FINAL_ACCOUNTING_RESULT
EXPECTS_AUDIT_OR_CERTIFICATION
EXPECTS_AUTOMATION_OR_RUNTIME
```

### Bloqueo por riesgo

```text
LIVE_CREDENTIALS_PRESENT
API_REQUIRED
OCR_REQUIRED
PARSER_REQUIRED
REAL_DATA_POLICY_RISK
HUMAN_REVIEW_NOT_AVAILABLE
```

## Resultado operativo permitido

El intake sólo puede terminar en uno de estos estados:

| Estado | Significado | Próxima acción segura |
|---|---|---|
| `ACCEPTED_FOR_XLSX_INTAKE` | El archivo puede entrar al flujo asistido de Servicio 1 | enviar a revisión/curación XLSX |
| `BLOCKED_NEEDS_SAFE_XLSX` | El formato o archivo no entra en V1 | pedir XLSX claro y verificable |
| `BLOCKED_SCOPE_REDUCTION_REQUIRED` | El caso excede alcance | recortar familia o período |
| `BLOCKED_BY_RISK` | Hay riesgo operativo o de datos | bloquear hasta corregir |

## Owner-safe messages requeridos

### Si se acepta

El mensaje debe comunicar algo como:

```text
Recibí el archivo Excel.
Puedo revisarlo como evidencia operativa inicial.
Primero voy a identificar hojas, columnas, faltantes y posibles campos a confirmar.
Esto no habilita cálculo final ni conclusión definitiva.
```

### Si se bloquea por formato

```text
En esta versión Servicio 1 trabaja con un XLSX claro y verificable.
Para avanzar, necesito que reenvíes el archivo como XLSX.
```

### Si se bloquea por alcance

```text
El pedido excede el alcance actual de Servicio 1.
Podemos recortarlo a una revisión operativa concreta del archivo o detenernos acá.
```

### Si se bloquea por riesgo

```text
No puedo avanzar con este archivo o pedido en el estado actual porque requiere credenciales, integración viva, OCR o un nivel de validación fuera del alcance seguro.
```

## Procedimiento operativo

### Paso 1 — Clasificar archivo

Usar la frontera ya existente:

```text
classify_file_intake(...)
```

Leer:

```text
support.status
support.reason_code
routing.next_allowed_action
risk_flags
blocks_runtime
```

### Paso 2 — Validar alcance del caso

Confirmar:

- familia operativa;
- problema concreto;
- período o recorte;
- expectativa del dueño.

### Paso 3 — Validar riesgo

Confirmar ausencia de:

- credenciales;
- tokens;
- API viva requerida;
- OCR requerido;
- parser nuevo requerido;
- expectativa de dictamen final.

### Paso 4 — Emitir decisión

Emitir sólo una:

```text
ACCEPTED_FOR_XLSX_INTAKE
BLOCKED_NEEDS_SAFE_XLSX
BLOCKED_SCOPE_REDUCTION_REQUIRED
BLOCKED_BY_RISK
```

### Paso 5 — Indicar próxima acción segura

La próxima acción debe ser una sola y explícita:

```text
send_to_xlsx_document_ingestion
ask_owner_to_upload_xlsx
ask_owner_to_reduce_scope
block_until_human_review_or_safe_input
```

## Checklist de intake

```text
[ ] El archivo es XLSX.
[ ] El archivo no está vacío.
[ ] El nombre es seguro.
[ ] No hay mismatch crítico MIME/extensión.
[ ] El dueño expresó un problema concreto.
[ ] El alcance entra en una familia compatible.
[ ] El período o recorte es explícito o recuperable.
[ ] No se pidió auditoría ni certificación.
[ ] No se pidió resultado contable final.
[ ] No se requieren credenciales ni APIs vivas.
[ ] No se requiere OCR.
[ ] Human review sigue siendo obligatoria.
[ ] La próxima acción segura quedó indicada.
```

## PASS / FAIL

### PASS

El intake pasa si:

```text
archivo = XLSX seguro
alcance = compatible y acotado
riesgo = controlado
próxima acción = explícita
runtime_authorized = false
human_review_required = true
```

### FAIL

El intake falla si:

```text
el archivo no es XLSX seguro
el alcance no puede recortarse
hay riesgo operativo o de datos
se espera diagnóstico, certificación o autonomía
```

## Non-goals

Este protocolo no autoriza:

```text
tool execution final
XLSX final delivery
pipeline runtime
vertical_pipeline wiring
chatbot
LLM orchestration
OCR
PDF parsing
CSV production path
```

## Próximo paso correcto

```text
SERVICE_1_REVIEW_CHECKLIST_V1
```

Porque después de aceptar un XLSX, el siguiente cuello de botella real es el gate humano por corrida.
