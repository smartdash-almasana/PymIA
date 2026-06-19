# OCR Evidence Recovery Intent

## Estado

INTENT / NO IMPLEMENTATION

Este documento registra una intención arquitectónica. No autoriza código OCR productivo, no crea contrato ejecutable y no modifica el flujo vivo de PymIA-Live.

## Motivo

PymIA necesita contemplar evidencia documental no tabular o visual: PDFs, imágenes, escaneos, tickets, facturas, remitos, extractos, capturas y documentos fotografiados.

Sin embargo, incorporar OCR directamente como código productivo es riesgoso si no se respeta la doctrina existente del sistema:

```text
lo que no queda claro en la evidencia no se inventa;
se convierte en faltante, advertencia o pregunta trazable al dueño.
```

Por lo tanto, OCR debe pensarse como canal de recuperación de evidencia, no como motor diagnóstico.

## Principio rector

```text
OCR no interpreta lo dudoso: lo convierte en gap trazable.
```

OCR puede ayudar a leer documentos. No puede decidir por sí mismo qué significa organizacionalmente una ambigüedad.

## Frontera conceptual

La frontera deseada es:

```text
PDF / imagen / escaneo / captura
→ OCR raw extraction
→ campos detectados con confianza
→ warnings / unclear fields
→ evidence gaps
→ owner questions cuando corresponda
→ owner answer
→ recuperación de evidencia
```

## Lo que OCR puede hacer

- Extraer texto bruto.
- Extraer bloques, páginas, líneas o tablas si el motor lo permite.
- Detectar campos candidatos como fecha, importe, proveedor, cliente, CUIT, total, período, concepto.
- Asociar confianza por campo.
- Marcar campos ilegibles o ambiguos.
- Producir advertencias de baja confianza.
- Generar insumos para preguntas al dueño cuando la evidencia no alcanza.

## Lo que OCR no puede hacer

- No diagnosticar una PyME.
- No ejecutar fórmulas organizacionales.
- No decidir estado de caso.
- No decidir service depth.
- No crear records operativos directamente.
- No escribir storage.
- No modificar `vertical_pipeline.py`.
- No modificar `document_ingestion.py` sin TaskSpec explícito.
- No suponer datos faltantes.
- No convertir baja confianza en certeza.

## Relación con preguntas al dueño

Cuando un campo OCR sea incierto, incompleto o contradictorio, el sistema debe preferir una pregunta trazable al dueño antes que una inferencia.

Ejemplo conceptual:

```json
{
  "field": "total_amount",
  "status": "unclear",
  "confidence": 0.52,
  "recovery_action": "ask_owner",
  "owner_question": "No pude leer con claridad el total del comprobante. ¿Cuál es el importe final?"
}
```

Esa pregunta no debe vivir como texto suelto. Debe integrarse con la cadena ya existente de recuperación de evidencia y preguntas owner-facing.

## Relación con capas existentes

OCR debe respetar las fronteras ya gobernadas:

```text
document_ingestion.py          → ingesta y curado XLSX existente
structured_evidence_builder.py → construcción de contexto de evidencia
vertical_pipeline.py           → orquestación viva congelada
owner/question flow            → preguntas al dueño y recuperación
evidence_request / owner_answer → trazabilidad de faltantes y respuestas
case_replay.py / ocf_snapshot.py → continuidad del caso
```

OCR no debe saltarse esas capas.

## Posible nombre de frente futuro

```text
OCR_EVIDENCE_RECOVERY_BOUNDARY_V1
```

Pregunta central del futuro frente:

```text
¿Cómo convierte PymIA documentos visuales parcialmente claros en evidencia trazable o preguntas al dueño, sin inventar?
```

## Condición para escribir código

Antes de escribir código OCR debe existir un TaskSpec que defina al menos:

1. Entrada mínima aceptada.
2. Salida mínima esperada.
3. Representación de confianza por campo.
4. Representación de campos ambiguos.
5. Cómo se transforma un campo incierto en evidence gap.
6. Cómo se integra ese gap con owner questions.
7. Qué tests prueban que no hay diagnóstico ni inferencia libre.
8. Qué archivos están permitidos.
9. Qué archivos están prohibidos.

## Regla de no deriva

```text
OCR es recuperación de evidencia.
No es diagnóstico.
No es inteligencia organizacional autónoma.
No es sustituto de preguntas al dueño.
```

## Estado de implementación

No implementado.

Este documento sólo deja registrada la intención para evitar escribir código prematuro y para preservar la doctrina de evidencia insuficiente → pregunta trazable al dueño.
