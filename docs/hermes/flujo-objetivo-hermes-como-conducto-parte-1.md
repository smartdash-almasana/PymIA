# Flujo objetivo — Hermes como conducto

## Fuente

Salida provista por Hermes / PymIA.bot. Parte 1/2.

---

# PASO 0: RECEPCIÓN

**Componente:** HermesAgent

Recibe del usuario:

```text
- message: texto libre con el problema/síntoma
- file_path: path al archivo adjunto (XLSX, CSV, PDF, imagen)
```

Validación mínima:

```text
- Si file_path existe y es legible → continuar
- Si file_path es nulo o vacío → ir a Paso 1b (solo texto)
```

Acción:

```text
No abrir el archivo.
No parsear.
No leer contenido.
Solo verificar existencia y extensión.
```

---

# PASO 1a: REGISTRO DE EVIDENCIA (cuando hay archivo)

**Componente:** EvidenceRouter en PymIA

Llamada:

```bash
cd /opt/PymIA/conversa-engine && ./.venv/bin/python main.py \
  --register-evidence \
  --file "<file_path>" \
  --mime "<mime_type>"
```

Output esperado de PymIA:

```json
{
  "evidence_id": "uuid",
  "evidence_type": "structured_tabular",
  "rows_extracted": 5000,
  "columns": ["fecha", "cliente", "sku", "cantidad", "venta", "costo", "margen"],
  "status": "REGISTERED"
}
```

Acción de Hermes:

```text
Capturar evidence_id.
No inspeccionar los datos.
No validar contenido.
Solo verificar status == "REGISTERED".
```

Si `status != "REGISTERED"`:

```text
Ir a PASO 4 (detención).
```

---

# PASO 1b: SOLO TEXTO (sin archivo)

**Componente:** main.py de PymIA en modo texto

Llamada:

```bash
cd /opt/PymIA/conversa-engine && ./.venv/bin/python main.py \
  "<message>"
```

Output:

```text
texto crudo de PymIA
```

Acción de Hermes:

```text
Ir directo a PASO 3 (devolución).
Saltear PASO 2.
```

---

# PASO 2: CREACIÓN DE STRUCTURED EVIDENCE + CASO

**Componente:** StructuredEvidenceFactory + OperationalCaseOrchestrator en PymIA

Llamada:

```bash
cd /opt/PymIA/conversa-engine && ./.venv/bin/python main.py \
  --create-case \
  --message "<message>" \
  --evidence-id "<evidence_id>" \
  --mode FULL_DIAGNOSTIC
```

Output esperado de PymIA:

```json
{
  "case_id": "uuid",
  "run_id": "uuid",
  "trace_id": "uuid",
  "pipeline_name": "operational_diagnostics_v2",
  "pipeline_version": "2.1.0",
  "input_hash": "sha256:...",
  "status": "PROCESSING"
}
```

Acción de Hermes:

```text
Capturar case_id, run_id, trace_id, input_hash.
No interpretar.
Solo almacenar para trazabilidad.
```

---

# PASO 3: EJECUCIÓN DEL DIAGNÓSTICO

**Componente:** DiagnosticEngine en PymIA

Llamada:

```bash
cd /opt/PymIA/conversa-engine && ./.venv/bin/python main.py \
  --execute \
  --case-id "<case_id>" \
  --run-id "<run_id>"
```

Output esperado de PymIA (texto crudo, formato clínico):

```text
VEREDICTO: [conclusión directa]

ESTADO DE NÚMEROS:
[tabla de cifras clave]

CADENA CAUSAL:
[secuencia A → B → C con números]

HIPÓTESIS ABIERTAS:
[tabla hipótesis / confianza / evidencia]

EVIDENCIA FALTANTE:
[lista de datos necesarios para confirmar]

REPREGUNTA:
[pregunta mayéutica del kernel]
```

Acción de Hermes:

```text
Ir a PASO 3 (devolución).
```

---

# PASO 4: DETENCIÓN (PymIA no puede procesar)

## Archivo no soportado

```text
Condición: Archivo no soportado
Señal de PymIA: status: UNSUPPORTED_FORMAT
Acción de Hermes: Devolver mensaje crudo de PymIA. No intentar parsear.
```

## Archivo vacío / sin datos

```text
Condición: Archivo vacío / sin datos
Señal de PymIA: status: EMPTY_EVIDENCE
Acción de Hermes: Devolver mensaje crudo de PymIA. No generar datos ficticios.
```

## Kernel no tiene señal

```text
Condición: Kernel no tiene señal
Señal de PymIA: status: NO_SIGNAL / reply_text: None
Acción de Hermes: Devolver None verbatim. No analizar por cuenta propia.
```

## Error interno

```text
Condición: Error interno
Señal de PymIA: status: ERROR
Acción de Hermes: Devolver mensaje de error crudo. No diagnosticar el error.
```

## PymIA solicita más evidencia

```text
Condición: PymIA solicita más evidencia
Señal de PymIA: status: EVIDENCE_REQUIRED
Acción de Hermes: Devolver la pregunta de PymIA sin modificar. Esperar respuesta del usuario.
```

## En todos los casos de detención

```text
- No escribir scripts
- No abrir el archivo
- No calcular nada
- No emitir hipótesis propias
- Devolver exactamente lo que PymIA devolvió
```
