# Registro de Documentos No-Vigentes y Referencias Históricas
**Repositorio de Documentos SUPERADOS, ARCHIVO y BORRAR_PROPUESTO**

> [!WARNING]
> ### ADVERTENCIA CRÍTICA DE GOBIERNO TÉCNICO
> Los documentos listados en este registro están clasificados de forma oficial como **NO VIGENTES** (Estados: `SUPERADO`, `ARCHIVO` o `BORRAR_PROPUESTO`). 
> **NO USAR ESTOS DOCUMENTOS PARA GUIAR LA IMPLEMENTACIÓN O REFACTORIZACIÓN EN RUNTIME.** Su uso para justificar cambios en el código de producción o en el diseño de contratos activos constituirá un fallo metodológico severo y directo.

---

## 1. Documentos SUPERADOS
*Contienen decisiones de diseño o contratos de negocio que han sido contradichos o reemplazados explícitamente por arquitecturas más recientes.*

| Documento | Razón Concreta de Deprecación | Reemplazado por (Vigente) |
| :--- | :--- | :--- |
| `docs/arquitectura/SEMANTICA_CONVERSACIONAL_PYMIA_HERMES_BEM.md` | Define al motor remoto BEM como el intérprete semántico primario para las planillas del negocio, lo cual degrada la autonomía local de PymIA y produce inconsistencias críticas. | [AUDITORIA_SCHEMA_INFERENCE_RUNTIME_V1.md](file:///opt/PymIA/docs/AUDITORIA_SCHEMA_INFERENCE_RUNTIME_V1.md) y [ADR-004-bem-como-fallback-pasivo.md](file:///opt/PymIA/docs/adr/ADR-004-bem-como-fallback-pasivo.md) |
| `docs/arquitectura/signal-admission-refactor.md` | Propuesta antigua de admisión de señales físicas que ha sido superada por la especificación de contratos clínicos unificados de admisión y el `EvidenceBundle`. | [contratos/contratos-clinicos-operacionales.md](file:///opt/PymIA/docs/contratos/contratos-clinicos-operacionales.md) |

---

## 2. Documentos ARCHIVO (Referencias Históricas)
*Documentos con valor referencial, teórico o metodológico, pero que no dictan de manera directa la lógica, el comportamiento o los límites del código en runtime.*

| Documento | Razón de Clasificación |
| :--- | :--- |
| `docs/arquitectura/palantir-principles.md` | Ensayo filosófico de desarrollo que establece principios éticos y conceptuales (ej. soberanía del dato, robustez, etc.), no técnico-operativos. |
| `docs/arquitectura/PDF_IMAGE_EXTRACTION_BENCHMARK.md` | Pruebas estructurales de extracción OCR sobre planillas PDF escaneadas. Útil de forma referencial para PDF, pero sin injerencia en el pipeline local actual de Polars para Excel/CSV. |
| `docs/arquitectura/domain-classification.md` | Guía de clasificación teórica de dominios. |
| `docs/arquitectura/entropy-routing.md` | Modelo de ruteo estocástico de conversaciones basado en entropía. No implementado en producción. |
| `docs/arquitectura/capability-runtime.md` | Nota histórica sobre capacidades operativas. |
| `docs/arquitectura/harness-engineering.md` | Borrador conceptual de ingeniería de pruebas y simuladores. |
| `docs/vision/SMARTPYME_LABORATORIO_PYME_Y_ESTABILIZACION_OPERACIONAL.md` | Documento de visión y provenance inicial del laboratorio PyME heredado de la fase SmartPyme. |
| `docs/vision/SMARTPYME_MVP_REALISTA_Y_FILOSOFIA_OPERACIONAL.md` | Filosofía inicial del MVP. Conservado solo por trazabilidad del proyecto. |
| `docs/fundamentos/metodo-hipotetico-deductivo.md` | Justificación epistemológica del diagnóstico clínico contable de PymIA basado en el método deductivo. |
| `docs/fundamentos/organismo-pyme.md` | Analogía biológica que describe a la PyME como un organismo vivo susceptible a "patologías contables". |
| `docs/fundamentos/primer-tiempo-logico.md` | Teoría analítica del tiempo lógico de aceptación del usuario. |
| `docs/fundamentos/cosmovision-clinico-operacional.md` | Filosofía global que une la medicina clínica con las finanzas operativas de la PyME. |
| `docs/epistemologia/protocolo-conversacional-hermes.md` | Filosofía teórica de la comunicación verbal. |
| `docs/epistemologia/modelo-verdad-soberania.md` | Ensayo sobre la soberanía epistémica de los registros contables frente a las alucinaciones del modelo. |
| `docs/epistemologia/contrato-epistemologico-smartgraph.md` | Diseño teórico del SmartGraph contable preliminar. |
| `docs/hermes/protocolo-doble-lectura-codex-kernel.md` | Diseño de sincronización conversacional teórica. |
| `docs/hermes/plano-logico-kernel-integrado-pines-estados-compuertas.md` | Metáfora de hardware para el ruteo conversacional de Hermes. No representa código en producción. |
| `docs/hermes/inventario-smartpyme-nodos-colgados-para-pymia.md` | Lista arqueológica de archivos y módulos heredados del sistema anterior. |
| `docs/hermes/kernel-minimo-viable-y-corpus-minimo.md` | Notas históricas sobre límites del corpus conversacional inicial. |
| `docs/hermes/incidente-integracion-hermes-pymia-a-mitad-de-construccion.md` | Resumen de incidentes post-mortem ocurridos durante la fase de integración física Hermes-PymIA. |

### 2.1. Arqueología e Ingeniería Conversacional Migrada (SmartPyme Legacy)
*Todos los archivos con prefijo `docs/migrado_desde_smartpyme_` y `docs/ingenieria_conversacional.` (excepto el índice conversacional redundante) corresponden al acervo de arqueología digital del sistema original SmartPyme. Se preservan estrictamente para fines de trazabilidad de provenance y consulta histórica de reglas del negocio:*

* `docs/migrado_desde_smartpyme_MIGRATION_INDEX.md`
* `docs/migrado_desde_smartpyme_DRIFT_REPORT.md`
* `docs/migrado_desde_smartpyme_MIGRACION_FISICA_FASE3.md`
* `docs/migrado_desde_smartpyme_REPORTE_CIERRE_FASE1.md`
* `docs/migrado_desde_smartpyme_ARQUEOLOGIA_FASE3.md`
* `docs/migrado_desde_smartpyme_formulas_CLINICAL_MATHEMATICAL_KERNEL_AND_HUMAN_COGNITIVE_LOOP.md`
* `docs/migrado_desde_smartpyme_conversacional_CONVERSATIONAL_COMMERCE_MULTIUSER_STRATEGY.md`
* `docs/migrado_desde_smartpyme_catalogos_SYMPTOM_PATHOLOGY_CATALOG_DESIGN.md`
* `docs/migrado_desde_smartpyme_epistemologia_NOCION_001_ORGANISMO_PYME.md`
* `docs/ingenieria_conversacional.corpus_migrado.md`
* `docs/ingenieria_conversacional.MIGRACION_SMARTPYME_CONVERSACIONAL_v1.md`
* `docs/ingenieria_conversacional.NORMATIVA_v1.md`
* `docs/ingenieria_conversacional.PROTOCOLO_PRIMER_CONTACTO_v1.md`
* `docs/ingenieria_conversacional.CATALOGO_HIPOTESIS_Y_EVIDENCIA_v1.md`
* `docs/ingenieria_conversacional.CATALOGO_FORMULAS_MATEMATICAS_PYME_v1.md`
* `docs/ingenieria_conversacional.ENSAMBLE_DOCUMENTAL_FASE1_v1.md`
* `docs/ingenieria_conversacional.MAPA_INTEGRACION_v1.md`
* `docs/ingenieria_conversacional.PATOLOGIAS_PYME_Y_TANQUES_DE_CONOCIMIENTO_v1.md`

---

## 3. Documentos con Propuesta de Borrado (BORRAR_PROPUESTO)
*Archivos duplicados, redundantes o que causan confusión epistemológica y que se sugiere remover del repositorio físico en la próxima fase de limpieza:*

| Documento | Razón Concreta de Borrado Propuesto | Reemplazado por (Vigente) |
| :--- | :--- | :--- |
| `docs/ingenieria_conversacional.README.md` | Es un índice anidado redundante para los archivos conversacionales migrados, el cual genera confusión y duplicidad estructural con respecto a la raíz documental. | [DOCUMENTATION_INDEX.md](file:///opt/PymIA/docs/DOCUMENTATION_INDEX.md) |
