# Registro de Decisión de Arquitectura (ADR)
## ADR-004: Relegación de BEM a Fallback Pasivo de Contingencia

* **Estado**: ACEPTADO
* **Fecha**: 2026-05-22
* **Dueño Conceptual**: Arquitectura Maestra / Hermes Layer

---

## 1. Contexto
En la versión inicial de PymIA, el módulo externo **BEM** (Business Evaluation Module / AI Remote) actuaba como el intérprete semántico primario para descifrar la estructura y el significado de los adjuntos tabulares de entrada. Este diseño introducía latencias elevadas, dependencias externas no deterministic y, críticamente, delegaba la inteligencia empresarial en un servicio cognitivo externo que carecía de validación contable local. Esto causaba un alto volumen de preguntas manuales redundantes al dueño ante columnas estándar como `"cantidad"` y derivaba en graves errores de doble multiplicación en los costos.

## 2. Decisión
Se decide **relegar formalmente a BEM de la ruta principal de ingesta de datos**.
* BEM deja de ser el agente primario y pasa a actuar exclusivamente como un **fallback pasivo de contingencia**.
* La ruta por defecto de procesamiento e inferencia semántica de planillas será **100% local e interactiva**, ejecutada directamente por el runtime de SmartPyme/PymIA (`conversa-engine` + `PymIA kernel`).
* BEM solo se invocará si el pipeline físico local de Polars falla de forma absoluta al intentar parsear la estructura del archivo (por ejemplo, ante archivos PDF escaneados o planillas totalmente desestructuradas que la lógica local degrade con gracia).

## 3. Consecuencias
* **Positivas**:
  * Autonomía y soberanía de procesamiento local total.
  * Eliminación de costos de llamadas API y latencia de red para planillas estándar.
  * Control absoluto de los tipos de datos y la consistencia matemática local de los registros.
* **Negativas / Desafíos**:
  * El sistema local debe ser capaz de perfilar y clasificar columnas con extrema precisión.
  * Se requiere un motor de alineamiento lingüístico y validación de restricciones en memoria.

## 4. Qué Queda Prohibido
* **PROHIBIDO** desviar planillas Excel o CSV estándar hacia BEM de forma predeterminada.
* **PROHIBIDO** invocar a BEM si la pre-auditoría física confirma que el archivo es legible y localmente procesable.
* **PROHIBIDO** almacenar el estado de ruteo cognitivo en variables o metadata opaca no auditable.

## 5. Trazabilidad

### Documentos Relacionados
* [AUDITORIA_SCHEMA_INFERENCE_RUNTIME_V1.md](file:///opt/PymIA/docs/AUDITORIA_SCHEMA_INFERENCE_RUNTIME_V1.md) — Blueprint de la capa de inteligencia documental.
* [DOCUMENTATION_INDEX.md](file:///opt/PymIA/docs/DOCUMENTATION_INDEX.md) — Índice canónico de documentación de PymIA.

### Código Relacionado
* `conversa-engine/document_intake.py` (Maneja el triage semántico de desvío).
* `tools/document_ingestion.py` (Orquesta la curación local).
