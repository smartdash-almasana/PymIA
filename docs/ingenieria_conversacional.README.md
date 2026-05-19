# Ingeniería conversacional — PymIA

## Estado

Migración documental inicial desde SmartPyme.  
Fecha: Mayo 2026.  
Estado operativo: corpus puente, pendiente de depuración final.

## Propósito

Concentrar en PymIA el ADN conversacional, semántico y epistemológico trabajado originalmente en SmartPyme para gobernar la primera fase del Laboratorio PyME.

Esta familia documental no implementa runtime. Define fuente documental soberana para:

- recepción clínica-operacional;
- anamnesis conversacional;
- conversación mayéutica;
- hipótesis investigativas;
- evidencia requerida y confirmada;
- estados de verdad;
- primer informe;
- límites de diagnóstico.

## Documentos

- `ingenieria_conversacional.corpus_migrado.md` — corpus bruto migrado desde SmartPyme, sin depuración fina.
- `ingenieria_conversacional.NORMATIVA_v1.md` — reglas rectoras iniciales.
- `ingenieria_conversacional.PROTOCOLO_PRIMER_CONTACTO_v1.md` — protocolo de recepción/anamnesis inicial.
- `ingenieria_conversacional.CATALOGO_HIPOTESIS_Y_EVIDENCIA_v1.md` — hipótesis investigativas, evidencia y preguntas.
- `ingenieria_conversacional.MAPA_INTEGRACION_v1.md` — solapamientos, jerarquía provisional y rutas de integración.

## Fuentes migradas o resumidas

- `SmartPyme/docs/architecture/CONVERSATIONAL_METHODS.md`
- `SmartPyme/docs/adr/ADR-CAT-001A-primer-tiempo-logico-historia-clinica-pyme.md`
- `SmartPyme/docs/adr/ADR-EP-002-hermes-conversational-protocol.md`
- `SmartPyme/app/laboratorio_pyme/conversation/state.py`
- `SmartPyme/app/laboratorio_pyme/conversation/questions.py`
- `SmartPyme/app/laboratorio_pyme/conversation/hypotheses.py`
- `SmartPyme/app/laboratorio_pyme/conversation/engine.py`

## Regla rectora

```text
La conversación no es un chat.
La conversación es el comienzo del laboratorio.
```

## Jerarquía provisional

1. `ingenieria_conversacional.NORMATIVA_v1.md`
2. `ingenieria_conversacional.PROTOCOLO_PRIMER_CONTACTO_v1.md`
3. `ingenieria_conversacional.CATALOGO_HIPOTESIS_Y_EVIDENCIA_v1.md`
4. `ingenieria_conversacional.MAPA_INTEGRACION_v1.md`
5. `ingenieria_conversacional.corpus_migrado.md`

El corpus bruto conserva memoria documental. La normativa y el protocolo gobiernan implementación futura.

## Implicancia para PymIA

Todo comportamiento conversacional de primer contacto debe obedecer este corpus antes de improvisar prompts o respuestas.

Si hay conflicto entre salida runtime y esta fuente documental, se activa `CANONICAL_DRIFT_GATE`.

## Próximo trabajo

- depurar duplicaciones contra `docs/catalogo/anamnesis-y-catalogos.md`;
- depurar duplicaciones contra `docs/catalogo/diseno-catalogo-clinico.md`;
- decidir si esta familia se mantiene como raíz lógica o se migra a subcarpeta real;
- derivar contratos implementables para estado conversacional persistente;
- recién después modificar runtime/Telegram.
