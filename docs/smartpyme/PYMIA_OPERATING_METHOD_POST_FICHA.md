# PymIA Operating Method — Post Ficha

Estado: VIGENTE
Fecha: 2026-05-31

## Propósito

Este documento fija el método de trabajo para continuar PymIA sin improvisación, sin fricción innecesaria y sin reabrir debates ya cerrados.

Aplica al frente posterior a:

```text
CONVERSATIONAL_RUNTIME_OFFLINE_READY
FICHA_PYME_ORDER_REDESIGN
FIXTURE_DECONTAMINATION_OWNER_CLAIMS
```

## Problema que resuelve

El trabajo venía derivando por:

- propuestas de arquitectura antes de leer contratos existentes;
- prompts demasiado largos o demasiado generales;
- mezcla de frentes;
- tests verdes confundidos con producto cerrado;
- ejemplos humanos contaminantes usados como fixtures;
- falta de especificación antes de implementación;
- falta de gates claros de aceptación.

Este método busca que cada avance tenga:

```text
lectura previa
spec breve
prompt operativo
implementación focalizada
gates objetivos
cierre documental mínimo
```

## Principios obligatorios

### 1. Leer antes de diseñar

Antes de proponer arquitectura, leer:

- memoria vigente;
- documentación específica;
- código real;
- tests del frente.

No se puede proponer una frontera nueva si ya existe una reutilizable.

### 2. Un frente por vez

No mezclar:

- Ficha PyME;
- post-ficha intake routing;
- evidencias;
- ejecución de fórmulas;
- Telegram;
- Hermes;
- landing;
- microservicios;
- documentación histórica.

### 3. No diagnosticar antes de evidencia

El flujo post-ficha puede producir:

- síntoma candidato;
- patología candidata;
- hipótesis investigable;
- evidencia requerida;
- bloqueo por faltantes.

No puede producir:

- diagnóstico confirmado;
- resultado numérico;
- fórmula ejecutada;
- informe final;
- recomendación causal fuerte.

### 4. Fixtures estructurales

No usar frases humanas como caso canónico.

Permitido:

```text
RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY
OWNER_CLAIM_MARGIN_UNCERTAINTY_FIXTURE
__OWNER_CLAIM_MARGIN_UNCERTAINTY__
```

Permitido en runtime productivo:

- patrones léxicos reales necesarios para clasificación.

No permitido:

- frases humanas repetidas como fixtures;
- ejemplos narrativos usados como contrato;
- tokens de test dentro de heurísticas productivas.

### 5. Separación de capas

Contrato vigente:

```text
conversa-engine guía
SmartPyme estructura y enruta
PymIA computa
Hermes/Telegram/WhatsApp son canales
```

El canal no decide diagnóstico.
El LLM no gobierna el flujo.
La ficha no ejecuta análisis.

## Fase actual

```text
POST_FICHA_INTAKE_ROUTING
```

Objetivo:

```text
Ficha PyME completa
→ profile_data
→ StructuredSelectors
→ create_intake_record(...)
→ IntakeRecord
→ evidence_requests
→ respuesta conversacional de pedido documental
```

## Punto de soldadura esperado

La soldadura correcta debe pasar por el pipeline formal existente:

```text
pymia/smartpyme/interrogation.py
pymia/smartpyme/tank_selection.py
pymia/smartpyme/intake.py
```

No debe saltar a:

```text
conversa-engine/symptom_pathology_catalog.py
```

salvo como referencia documental o compatibilidad posterior.

## Spec mínima antes de implementar

Antes de tocar código en este frente, debe existir una respuesta de auditoría con:

1. mapa `profile_data` → `StructuredSelectors`;
2. campos sin correspondencia directa;
3. función puente propuesta;
4. ubicación del puente;
5. tests exactos;
6. riesgos;
7. criterio PASS.

## Contrato de función candidato

```python
build_structured_selectors_from_profile_data(profile_data: dict[str, Any]) -> StructuredSelectors
```

Y luego:

```python
create_intake_record(
    tenant_id=tenant_id,
    raw_text=profile_data["raw_first_message"],
    structured_selectors=selectors,
)
```

## Respuesta conversacional post-ficha esperada

Debe explicar el próximo paso sin diagnosticar:

```text
Ya tengo la ficha inicial.
Con los datos cargados, el primer frente a ordenar es [familia_operativa].
Para avanzar sin adivinar necesito esta evidencia mínima:
1. [evidence_request_1]
2. [evidence_request_2]
3. [evidence_request_3]
```

No debe decir:

```text
El problema es...
El diagnóstico es...
Tu margen está...
La causa es...
```

## Gates por hito

### Gate 1 — Auditoría

Debe entregar:

```text
VEREDICTO
MAPA_DATOS
PUNTO_SOLDADURA
TESTS_PROPUESTOS
RIESGOS
PROXIMA_ACCION
```

### Gate 2 — Implementación

Debe entregar:

```text
archivos modificados
contrato nuevo o reutilizado
tests ejecutados
rg si aplica
git status
```

### Gate 3 — Producto

Debe probar:

```text
CLI persistente
ficha completa
post-ficha genera evidence_requests
no diagnóstico prematuro
estado persistido contiene intake/evidence_requests si corresponde
```

## Prompts estándar

### Prompt de auditoría

```text
AGENTE: Gemini
MODO: AUDITORÍA
NO IMPLEMENTAR

Leer memoria, docs, código y tests del frente.
Responder con VEREDICTO, mapa de datos, punto de soldadura, riesgos y próxima acción única.
```

### Prompt de implementación

```text
AGENTE: Gemini/Codex
MODO: IMPLEMENTACIÓN CONTROLADA

Implementar solo lo aprobado en la auditoría.
No abrir frentes nuevos.
No crear arquitectura paralela.
Validar con tests pactados.
```

### Prompt de reparación

```text
AGENTE: Gemini/Codex
MODO: REPAIR

No rediseñar.
No ampliar alcance.
Reparar exclusivamente los fallos observados.
Entregar tests y git status.
```

## Tests base recurrentes

Para SmartPyme/post-ficha:

```powershell
python -m pytest tests/smartpyme -q
python -m pytest tests/test_conversa_engine_boundary_consumption_smoke.py tests/test_conversa_progressive_context_roundtrip.py -q
python -m pytest tests/orchestration/test_state.py tests/orchestration/test_state_storage.py -q
```

Tests específicos esperados para post-ficha:

```powershell
python -m pytest tests/smartpyme/test_interrogation.py tests/smartpyme/test_tank_selection.py tests/smartpyme/test_intake.py -q
```

## Criterio de avance

No avanzar a ejecución de fórmulas hasta que exista:

- `IntakeRecord` post-ficha;
- `evidence_requests` contextual;
- persistencia o exposición en `progressive_context`;
- test que pruebe que no hay diagnóstico prematuro.

## Próximo paso vigente

Ejecutar auditoría profunda del ensamble:

```text
POST_FICHA_INTAKE_ROUTING_AUDIT
```

No implementar hasta tener el mapa de soldadura aceptado.
