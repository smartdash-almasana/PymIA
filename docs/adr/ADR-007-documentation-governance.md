# Registro de Decisión de Arquitectura (ADR)
## ADR-007: Implementación del Sistema de Gobierno Documental y Estandarización de la Biblioteca Canónica

* **Estado**: ACEPTADO
* **Fecha**: 2026-05-22
* **Dueño Conceptual**: Gobierno Técnico / Biblioteca Canónica de PymIA

---

## 1. Contexto
A medida que el proyecto PymIA crecía e integraba componentes heredados de la plataforma original SmartPyme, la biblioteca de documentación física (`docs/`) acumulaba ruido histórico, directrices contradictorias, y duplicidad de guías normativas de desarrollo. Esto generaba una "deuda técnica cognitiva" severa, donde desarrolladores y agentes inteligentes consultaban documentos obsoletos (como el diseño de BEM como intérprete semántico primario), derivando en arquitecturas e implementaciones divergentes de las directrices maestras actuales de PymIA.

## 2. Decisión
Se establece un **Sistema de Gobierno Documental Obligatorio** para regular y certificar la biblioteca técnica de PymIA:
* **Índice Canónico SOBERANO**: Se crea [DOCUMENTATION_INDEX.md](file:///opt/PymIA/docs/DOCUMENTATION_INDEX.md) como el catálogo maestro centralizado. Todo documento de la biblioteca debe estar clasificado y listado de forma unívoca en este índice.
* **Separación de Ciclo de Vida**: Se clasifican los documentos en 5 categorías con roles claros:
  * **VIGENTE**: Rige y guía de forma obligatoria e incondicional el desarrollo de código en runtime.
  * **CANDIDATO**: Propuesta útil, pero requiere validación técnica o contable antes de guiar código.
  * **SUPERADO**: Decisiones reemplazadas o contradichas por diseños vigentes más recientes.
  * **ARCHIVO**: Información histórico-teórica valiosa (provenance, arqueología legacy), pero sin injerencia directa en la codificación actual.
  * **BORRAR_PROPUESTO**: Duplicados o archivos basura candidatos a remoción física del repositorio.
* **Registro de Deprecación**: Se crea [DEPRECATED_DOCS.md](file:///opt/PymIA/docs/DEPRECATED_DOCS.md) para encapsular todos los archivos clasificados como `SUPERADO`, `ARCHIVO` o `BORRAR_PROPUESTO`, con explicaciones explícitas de su deprecación y advertencias de no uso en runtime.

## 3. Consecuencias
* **Positivas**:
  * Eliminación del ruido cognitivo para desarrolladores humanos y agentes de inteligencia.
  * Unificación lógica del estado de diseño del sistema.
  * Mayor control en auditorías, certificando que sólo la documentación `VIGENTE` guíe el código.
* **Negativas / Desafíos**:
  * Requiere de mantenimiento riguroso: todo cambio de diseño que supere o reemplace un archivo debe actualizar de forma simultánea el Índice Canónico y el Registro de Deprecación.

## 4. Qué Queda Prohibido
* **PROHIBIDO** guiar implementaciones, refactorizaciones o lógica de pruebas basándose en documentos clasificados como `SUPERADO`, `ARCHIVO` o `BORRAR_PROPUESTO`.
* **PROHIBIDO** crear nuevos archivos documentales sin registrarlos de forma inmediata en el Índice General de Gobernanza.
* **PROHIBIDO** mantener reglas o criterios normativos de desarrollo duplicados o fragmentados entre documentos activos.

## 5. Trazabilidad

### Documentos Relacionados
* [DOCUMENTATION_INDEX.md](file:///opt/PymIA/docs/DOCUMENTATION_INDEX.md) — Índice de Gobernanza Documental de PymIA.
* [DEPRECATED_DOCS.md](file:///opt/PymIA/docs/DEPRECATED_DOCS.md) — Registro de documentos no vigentes.
* [README.md](file:///opt/PymIA/docs/README.md) — Raíz documental.
