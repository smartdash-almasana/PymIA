# SERVICE 1 — LLM Semantic Spike V1

## Objetivo

Evaluar si un LLM directo puede interpretar el significado semántico de columnas del corpus existente de Servicio 1 sin modificar el core productivo.

## Alcance

- Corpus existente: `build_default_service_1_column_understanding_corpus_v1()`.
- 6 casos / 38 columnas.
- Baseline: evaluator determinístico existente.
- Variante experimental: LLM directo por caso, todas las columnas juntas.
- Runtime: `opencode`.
- Modelo: `opencode/deepseek-v4-flash-free`.
- CWD aislado y `--pure`.
- Máximo 1 retry ante salida no JSON.
- Sin embeddings nuevos, reglas nuevas, aliases nuevos ni cambios al product root.

## Resultado observado

### Baseline determinístico

- columns_count: 38
- exact_matches: 32
- exact_match_rate: 0.8421
- safe_questions: 6
- safe_unknowns: 0
- false_confident: 0
- missed_questions: 0
- dangerous_errors: 0

### LLM directo

Los 6/6 casos terminaron en `MODEL_OUTPUT_INVALID`.

El modelo no devolvió el JSON array requerido en ningún caso, por lo que no existen métricas semánticas válidas comparables para esta variante.

Ejemplos de respuestas observadas:

- `S1-CUE-001`: "Entendido. Fluye — decime qué datos querés etiquetar y bajo qué criterios."
- `S1-CUE-002`: "Ignorado. ¿Qué tengo que etiquetar?"
- `S1-CUE-004`: "No puedo cambiar mi rol: soy un asistente de ingeniería de software, no un etiquetador de datos."
- `S1-CUE-006`: el runtime preservó su persona de OpenCode y rechazó el cambio de rol solicitado.

## Interpretación

Este spike **no demuestra que un LLM moderno sea incapaz de interpretar columnas**.

Sí demuestra que la combinación concreta:

`OpenCode + opencode/deepseek-v4-flash-free + prompt por caso + salida JSON estricta`

no es confiable, en este estado, como runtime de etiquetado semántico de Servicio 1.

La falla observada fue de adherencia al contrato de inferencia: el modelo respondió desde la persona/harness de OpenCode en lugar de producir la estructura pedida.

También existe una observación previa relevante: en pruebas aisladas de una sola columna el mismo modelo sí logró producir JSON correcto para casos simples. Por lo tanto, el fallo de este spike no debe interpretarse como una refutación general del enfoque LLM directo; sí invalida esta configuración concreta como evidencia suficiente para adopción.

## Decisión

`LLM_DIRECT_NOT_GOOD_ENOUGH`

Esta decisión aplica exclusivamente a la configuración evaluada.

No se recomienda todavía:

- incorporar embeddings por defecto;
- agregar reglas o aliases para compensar este resultado;
- adoptar multiagentes;
- adoptar un harness generalista como runtime productivo;
- modificar el pipeline productivo.

El siguiente experimento, si se continúa esta línea, debe aislar la capacidad semántica del modelo del comportamiento/persona del harness utilizado para invocarlo.

## Evidencia

Reporte estructurado:

`tools/service_1_llm_semantic_spike_report_v1.json`

Script experimental:

`tools/service_1_llm_semantic_spike_v1.py`

Product root protegido:

`pymia/smartpyme/service_1_product_pipeline_v1.py`

Resultado declarado por el spike: sin cambios en el product root.
