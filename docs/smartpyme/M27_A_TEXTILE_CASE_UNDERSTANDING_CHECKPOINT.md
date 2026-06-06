# M27-A — Textile Case Understanding Checkpoint

## Estado

CERRADO / PUSHED

## Commit certificado

```text
0b7f934 test(smartpyme): add M27-A textile case understanding flow
```

Commit previo de soporte semántico natural:

```text
9efb8f2 test(smartpyme): add natural textile evidence gate E2E
```

## Objetivo M27-A

Certificar el slice mínimo de M27 — entender caso:

```text
mensaje dueño + Excel real
→ caso operativo estructurado
→ clasificación inicial
→ evidencia suficiente/faltante
→ estado honesto
```

M27-A no diagnostica rentabilidad. No calcula margen. No entrega reporte final. Sólo certifica que PymIA entiende el caso operativo inicial, pide evidencia, procesa el Excel real sin metadata manual y conserva un estado honesto cuando la evidencia no alcanza.

## Evidencia

Archivo de test:

```text
tests/smartpyme/test_m27_a_textile_case_understanding.py
```

Validación focal reportada:

```text
python -m pytest tests/smartpyme/test_m27_a_textile_case_understanding.py -q
1 passed in 8.31s
```

## Resultado certificado

El flujo M27-A valida:

1. Turno 1 del dueño produce encuadre taxonómico inicial.
2. Turno 2 confirma organismo PyME textil.
3. Se genera pedido de evidencia.
4. El Excel textil real entra sin metadata manual.
5. El parser real opera sobre el fixture.
6. `semantic_field_resolution` opera naturalmente sobre metadata documental.
7. El estado final queda en `NEEDS_EVIDENCE`.
8. Se generan `owner_questions`.
9. No aparece falso `READY_FOR_ANALYSIS`.

## Restricciones preservadas

No se tocó:

```text
pymia/smartpyme/evidence_gate.py
pymia/smartpyme/post_ficha_evidence_gate.py
pymia/smartpyme/semantic_field_resolution.py
dispatcher
runtime
Telegram
UI
PDF
ERP
producto
```

No se usó:

```text
_evidence_metadata_for()
evidence_metadata manual
READY_FOR_ANALYSIS forzado
NEEDS_OWNER_CLARIFICATION
Guided Evidence Recovery
```

## Lectura metodológica

M27-A certifica que PymIA puede pasar de relato inicial del dueño a caso operativo estructurado con evidencia real y bloqueo honesto.

Este checkpoint consolida el paso desde DEPTH-04C hacia M27:

```text
DEPTH-04C:
Excel real → parser → semantic_field_resolution → NEEDS_EVIDENCE honesto

M27-A:
mensaje dueño + taxonomía + Excel real → caso operativo entendido → NEEDS_EVIDENCE honesto
```

El avance no convierte el flujo en producto. Sigue siendo una capacidad bajo test dentro del servicio asistido.

## Próximo paso

Preparar M28 — explicar hallazgo.

Condición: definir scope antes de tocar código.

M28 no debe abrirse como reporte final amplio. Debe empezar como slice mínimo de explicación grounded, probablemente sobre un resultado técnico ya existente, sin PDF, UI, producto ni diagnóstico integral.
