# Registro de Decisión de Arquitectura (ADR)
## ADR-005: Implementación de Motor Local de Inferencia Semántica y Validación Matemática Basado en Polars

* **Estado**: ACEPTADO
* **Fecha**: 2026-05-22
* **Dueño Conceptual**: Document Intelligence Subsystem / Polars Engine

---

## 1. Contexto
La inferencia de esquemas semánticos en PymIA adolecía de un acoplamiento "split-brain" severo: el clasificador de perfiles (`excel_profile_builder.py`) y el mapeador final (`document_ingestion.py`) poseían diccionarios redundantes y descoordinados. Esto, sumado al sesgo por primer-match en cadenas estáticas, hacía que columnas válidas como `"cantidad"` se penalizaran como ambiguas y que la columna `"costo"` se catalogara como unitaria sin verificar las relaciones contables del negocio, multiplicando de forma astronómica e incorrecta las variables de costo en el kernel.

## 2. Decisión
Se establece la creación de un subsistema unificado local de inteligencia documental que operará sobre **Polars**:
* **Polars Engine**: Reemplaza las operaciones de tipificación del DataFrame crudo por un motor nativo y paralelizado en memoria, eliminando fallos por tipos inconsistentes.
* **BusinessSchemaInferenceEngine**: Unifica todas las reglas de mapeo, vocabularios, sinónimos contables y fallbacks lingüísticos en un único componente soberano de PymIA.
* **Validación de Restricciones Matemáticas (Constraint SAT)**: Todo mapeo contable tentativo debe ser validado evaluando relaciones matemáticas universales a nivel de fila (`venta_total - costo_total = margen_bruto` o `venta_total - (costo_unitario * cantidad) = margen_bruto`). Si la matemática cierra con un error de redondeo menor al 1% en más del 99% de los registros, el mapeo se confirma con un Score Relacional de 1.0 (100% de confianza) y se autoejecuta la ingesta sin formular ninguna pregunta manual.

## 3. Consecuencias
* **Positivas**:
  * Prevención absoluta del bug de la doble multiplicación de costos.
  * Mayor fluidez conversacional: el sistema no pregunta al dueño ante planillas lógicamente consistentes.
  * Desacoplamiento total entre la validación física estructural de la planilla y su interpretación contable semántica.
* **Negativas / Desafíos**:
  * Requiere de una biblioteca de alineamiento lingüístico y de evaluación estadística de percentiles robusta implementada de forma nativa.

## 4. Qué Queda Prohibido
* **PROHIBIDO** duplicar diccionarios de palabras clave o fallbacks contables en múltiples archivos (ej. entre profiler e ingestor).
* **PROHIBIDO** presuponer que la columna `"costo"` representa costos unitarios por defecto.
* **PROHIBIDO** arrojar excepciones crudas o técnicas de Pandas/Polars al usuario final en el canal conversacional.
* **PROHIBIDO** calcular métricas de rentabilidad clínica sobre evidencias con baja confianza de mapeo semántico.

## 5. Trazabilidad

### Documentos Relacionados
* [AUDITORIA_SCHEMA_INFERENCE_RUNTIME_V1.md](file:///opt/PymIA/docs/AUDITORIA_SCHEMA_INFERENCE_RUNTIME_V1.md) — Contrato de diseño e inferencia de esquema objetivo.
* [DOCUMENTATION_INDEX.md](file:///opt/PymIA/docs/DOCUMENTATION_INDEX.md) — Índice canónico de documentación de PymIA.

### Código Relacionado
* `tools/document_ingestion.py` (A reemplazar por el nuevo motor).
* `tools/bem_schema_builder/excel_profile_builder.py` (Extrae su clasificador antiguo).
* `tools/excel_evidence.py` (Se adaptará para invocar el motor de Polars).
