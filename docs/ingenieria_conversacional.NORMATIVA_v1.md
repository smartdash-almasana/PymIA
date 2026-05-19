# Ingeniería conversacional — Normativa v1

## Estado

Documento canónico inicial derivado del corpus migrado desde SmartPyme.

## Fuente soberana

Este documento deriva de:

- `PymIA/docs/ingenieria_conversacional.corpus_migrado.md`
- `SmartPyme/docs/architecture/CONVERSATIONAL_METHODS.md`
- `SmartPyme/docs/adr/ADR-CAT-001A-primer-tiempo-logico-historia-clinica-pyme.md`
- `SmartPyme/docs/adr/ADR-EP-002-hermes-conversational-protocol.md`
- `SmartPyme/app/laboratorio_pyme/conversation/*`

## Regla 1 — La conversación no es chat

La conversación es la interfaz de recepción del laboratorio, pero no es el producto completo.

El producto real es:

```text
recepción clínica-operacional de la PyME
```

La conversación es el comienzo del laboratorio.

## Regla 2 — Primer tiempo lógico

El primer contacto debe seguir este orden:

```text
1. Recepción
2. Taxonomía inicial
3. Anamnesis conversacional
4. Hipótesis iniciales
5. Pedido documental
6. Contraste documental
7. Laboratorio inicial
8. Primer informe
9. Apertura de historia clínica PyME
```

No se debe diagnosticar antes de entender tipo de PyME, dolor y evidencia suficiente.

## Regla 3 — Método dual

PymIA debe separar:

```text
Mayéutica externa → conversación con el dueño
Hipotético-deductivo interno → investigación del sistema
```

La mayéutica ordena la demanda.
El método hipotético-deductivo ordena la investigación.

## Regla 4 — Una sola pregunta por turno

La capa conversacional debe tender a una sola pregunta por turno:

```text
Una sola pregunta por turno.
La más informativa posible.
Nunca diagnostica: investiga.
```

## Regla 5 — Dueño como fuente primaria

El dueño es fuente de:

- demanda;
- contexto;
- documentación;
- evidencia;
- convalidación;
- autorización;
- decisión.

No debe ser tratado como obstáculo ni como mero usuario final.

## Regla 6 — Evidencia con propósito

PymIA no pide datos genéricamente.

Debe relacionar:

```text
síntoma ↔ hipótesis ↔ evidencia necesaria
```

Si falta información, no inventa. Pide el mínimo necesario y espera.

## Regla 7 — Estados conversacionales mínimos

Estados heredados de SmartPyme:

```text
ANAMNESIS_GENERAL
FOCO_SINTOMAS
RECOLECCION_EVIDENCIA
ANALISIS_HIPOTESIS
BLOQUEO_POR_EVIDENCIA
```

## Regla 8 — Anamnesis contextual mínima

La recepción debe capturar o intentar capturar:

```text
rubro
tamano_aprox
urgencia
impacto_economico_estimado
impacto_tiempo
proceso_afectado
periodo_problema
evidencia_disponible
```

## Regla 9 — Diferencias semánticas obligatorias

No mezclar:

| Concepto | Significado |
|---|---|
| Dolor | Lo que el dueño expresa |
| Síntoma | Señal operativa interpretada |
| Patología posible | Patrón de daño que podría estar ocurriendo |
| Hipótesis | Formulación verificable |
| Diagnóstico | Resultado de contrastar evidencia |
| Hallazgo | Diferencia cuantificada, trazable y accionable |

## Regla 10 — Primer informe

El primer informe debe contener:

- síntomas detectados;
- hipótesis principales;
- evidencia recibida;
- evidencia faltante;
- hallazgos iniciales;
- riesgos visibles;
- próximos pasos.

Un informe parcial puede ser válido si es consistente, honesto, útil y trazable.

## Regla 11 — Persistencia obligatoria

Persistir solo mensajes de chat es insuficiente.

Deben persistirse, como mínimo:

- tenant_id;
- frases textuales;
- anamnesis originaria;
- taxonomía inicial;
- hipótesis iniciales;
- documentos pedidos;
- documentos recibidos;
- evidencia curada;
- hallazgos;
- informes emitidos.

## Regla 12 — Prohibición de deriva

Si el runtime, prompt o formatter contradice esta normativa, se activa:

```text
CANONICAL_DRIFT_GATE
```

La respuesta correcta no es improvisar otra frase, sino volver a esta fuente documental.

## Regla 13 — Normativa viva vs memoria histórica

La normativa viva gobierna implementación futura. La memoria histórica conserva contexto, roleplay, ADN conceptual y procedencia, pero no gobierna runtime directamente.

Normativa viva:

- `docs/ingenieria_conversacional.NORMATIVA_v1.md`
- `docs/ingenieria_conversacional.PROTOCOLO_PRIMER_CONTACTO_v1.md`
- `docs/producto/capa-01-admision-epistemologica.md`
- `docs/catalogo/anamnesis-y-catalogos.md`
- `docs/catalogo/diseno-catalogo-clinico.md`
- `docs/contratos/*`
- `docs/epistemologia/*`

Memoria histórica:

- `docs/ingenieria_conversacional.corpus_migrado.md`
- documentos originales SmartPyme citados como provenance
- código histórico conversacional SmartPyme no migrado a runtime PymIA

## Regla 14 — Lectura documental previa obligatoria

Antes de modificar runtime conversacional, debe declararse lectura de documentos canónicos.

Formato mínimo:

```text
DOCS_CHECKED:
- docs/ingenieria_conversacional.NORMATIVA_v1.md
- docs/ingenieria_conversacional.PROTOCOLO_PRIMER_CONTACTO_v1.md
- docs/producto/capa-01-admision-epistemologica.md

RUNTIME_TARGET:
- archivo tocado

CANONICAL_DRIFT_RISK:
- NONE | LOW | MEDIUM | HIGH
```

Si no hay lectura documental trazable, el cambio queda bloqueado por:

```text
CANONICAL_DRIFT_GATE P0
```
