# PYMIA_FAITHFUL_OPERATOR_V1_PLAN

Estado: CANDIDATO_OPERATIVO
Fecha: 2026-06-11

## 1. Decisión

`PYMIA_FAITHFUL_OPERATOR_V1` será un arnés conversacional determinístico para operar PymIA sin traicionar su spine.

No será un chatbot libre.
No usará LangGraph dentro de `pymia/`.
No usará LLM real en V1.
No abrirá canales externos.

Forma técnica V1:

```text
FSM nativa + Pydantic + respuestas determinísticas + spine batch importable
```

## 2. Misión

Convertir conversación caótica del dueño PyME en un flujo trazable:

```text
relato del dueño
→ intake_id
→ pedido de evidencia
→ evidencia recibida
→ ejecución del spine batch
→ evidence_id
→ run_id
→ output_hash
→ resultado candidato
→ confirmación pendiente del dueño
```

## 3. Frontera arquitectónica

Prohibido para V1:

```text
LangGraph bajo pymia/
LLM real
agente autónomo
subprocess como integración principal
Telegram
HTTP
DB
runtime productivo
Hermes
marketplace
ERP
PDF productivo
multiagente
fine-tuning
```

Permitido para V1:

```text
FSM Python nativa
Pydantic
funciones importables existentes o extraídas del CLI vertical
respuestas determinísticas
tests focales
storage local ya usado por el spine batch
```

## 4. Spine que debe gobernar

El operador no reemplaza PymIA. Sólo gobierna el acceso conversacional al spine ya validado:

```text
intake_id
→ EvidenceRecord
→ StructuredEvidence
→ sufficiency
→ PipelineRunRecord
→ output_hash
```

## 5. Estados V1

Estados conversacionales permitidos:

```text
LISTENING
EVIDENCE_REQUESTED
PROCESSING
CANDIDATE_DELIVERED
OWNER_CONFIRMATION_PENDING
BLOCKED
CLOSED
```

Estados internos como `INTAKE_FORMED`, `SPINE_READY` o `SPINE_EXECUTED` no son estados conversacionales V1; deben representarse como campos/invariantes del estado, no como fases visibles.

## 6. Invariantes de fidelidad

El operador debe cumplir siempre:

```text
Sin evidencia, no diagnostica.
Sin intake_id, no procesa.
Sin evidence_id, no afirma evidencia registrada.
Sin run_id, no entrega resultado candidato.
Sin output_hash, no declara salida trazable.
Sin confirmación del dueño, no declara diagnóstico final.
```

Invariantes negativas:

```text
Nunca inventa datos.
Nunca convierte nombres de columnas en verdad de negocio.
Nunca confunde evidence_hash con output_hash.
Nunca ejecuta en background sin cierre verificable.
Nunca abre herramientas prohibidas.
Nunca crea arquitectura por iniciativa propia.
```

## 7. Entradas permitidas

```text
mensaje del dueño
rubro declarado
problema declarado
tenant_id
intake_id
ruta de Excel
confirmación o corrección del dueño
```

## 8. Salidas permitidas

```text
resumen breve del problema
pedido concreto de evidencia
bloqueo honesto
resultado candidato con límites
próxima pregunta al dueño
evidence_id
run_id
output_hash
estado actual
```

## 9. Conducta inicial esperada

Input:

```text
Vendo más pero no me queda plata.
```

Respuesta correcta:

```text
Entiendo. Puede ser caja, margen, costos o plazos, pero todavía no puedo afirmar la causa. Para avanzar necesito evidencia mínima: ventas, costos, productos y período. Si tenés un Excel, lo registro como evidencia inicial y te devuelvo una lectura candidata con límites.
```

Estado esperado:

```text
EVIDENCE_REQUESTED
```

## 10. Bloqueos obligatorios

Debe bloquear cuando:

```text
no hay evidencia suficiente
no hay intake_id válido
no hay archivo legible
el spine no devuelve run_id
el spine no devuelve output_hash
el dueño pide diagnóstico sin evidencia
una herramienta prohibida es solicitada
```

Bloqueo correcto:

```text
No puedo avanzar honestamente con diagnóstico todavía. Falta: [dato concreto]. Próxima acción: [pedido concreto].
```

## 11. Primer slice implementable

Nombre:

```text
FAITHFUL_OPERATOR_NO_DIAGNOSIS_AND_EVIDENCE_REQUEST
```

Alcance:

```text
crear estado Pydantic mínimo
crear FSM nativa mínima
procesar relato inicial
no diagnosticar
crear/conservar intake_id
pedir evidencia concreta
quedar en EVIDENCE_REQUESTED
```

Archivos máximos:

```text
pymia/operator/faithful_operator.py
tests/operator/test_faithful_operator.py
```

## 12. Segundo slice implementable

Nombre:

```text
FAITHFUL_OPERATOR_VERTICAL_SPINE_BINDING
```

Precondición:

Debe existir función importable del spine batch, sin subprocess como integración principal.

Función objetivo:

```text
build_pipeline(excel_path, tenant_id, intake_id, message, storage_dir)
```

Salida mínima:

```text
status
evidence_id
evidence_hash
run_id
output_hash
markdown_text o markdown_ref
missing_evidence
```

## 13. Tests de aceptación V1

Tests mínimos:

```text
1. no diagnostica sin evidencia
2. pide evidencia concreta
3. conserva o crea intake_id
4. bloquea sin archivo legible
5. no procesa sin intake_id
6. ejecuta spine sólo con evidencia recibida
7. entrega candidato sólo con run_id y output_hash
8. distingue evidence_hash de output_hash por origen semántico
9. queda en OWNER_CONFIRMATION_PENDING tras entregar candidato
10. rechaza herramientas prohibidas
```

## 14. Criterio de éxito

V1 pasa si demuestra:

```text
relato caótico
→ no diagnóstico
→ intake_id
→ pedido de evidencia
→ bloqueo honesto o procesamiento
→ resultado candidato trazable
→ confirmación pendiente
```

## 15. Principio rector

```text
Primero obediencia determinística.
Después conversación fluida.
Último, framework si hace falta.
```
