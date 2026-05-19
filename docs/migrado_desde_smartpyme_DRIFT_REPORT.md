# DRIFT_REPORT.md

Reporte de duplicaciones y contradicciones detectadas durante la migración.

## Regla

NO resolver duplicaciones ni contradicciones en esta fase.
Solo registrar para resolución posterior.

---

## Fase 1 — Entradas con drift potencial

### Terminología findings/hallazgos

**Documento**: SYMPTOM_PATHOLOGY_CATALOG_DESIGN.md
**Conflicto**: Uso de término inglés "findings" vs término castellano "hallazgos"
**Contexto**: ARCHIVO_LEGACY.md indica que "findings" es término técnico legado, "hallazgos" es término rector de negocio
**Acción pendiente**: Resolver normalización terminológica en fase posterior
**Riesgo**: medio

### Terminología inglés/castellano en fórmulas

**Documento**: CLINICAL_MATHEMATICAL_KERNEL_AND_HUMAN_COGNITIVE_LOOP.md
**Conflicto**: Mezcla de términos técnicos en inglés (FormulaCatalog, MathEngine, INSUFFICIENT_DATA) con documentación en castellano
**Contexto**: Documentación conceptual usa ambos idiomas; runtime podría requerir consistencia
**Acción pendiente**: Definir política de localización de términos técnicos
**Riesgo**: medio

### Estructura de catálogos

**Documento**: SYMPTOM_PATHOLOGY_CATALOG_DESIGN.md
**Conflicto**: Estructura YAML conceptual vs posible implementación JSON/Pydantic en runtime
**Contexto**: Documento es diseño conceptual, no especificación de implementación
**Acción pendiente**: Validar formato de serialización en fase de ensamblado
**Riesgo**: bajo

---

## Fase 3 — Nuevos Drifts Detectados

### Duplicaciones Conceptuales

#### 1. Catálogo de Patologías (3 variantes)

**Documentos involucrados**:
- `PYME_SYMPTOM_PATHOLOGY_ATLAS.md` (conceptual/atlas)
- `SYMPTOM_PATHOLOGY_CATALOG_DESIGN.md` (técnico/diseño)
- `app/catalog/pathologies.py` (implementación/código)

**Conflicto**: Mismo dominio (patologías PyME) documentado en tres niveles: conceptual, de diseño e implementación.
**Contexto**: El atlas define el marco semántico; el diseño especifica estructura; el código implementa lógica.
**Acción pendiente**: Migrar docs conceptuales y de diseño; código permanece en runtime. Documentar relación jerárquica en índice.
**Riesgo**: bajo (si se mantiene separación conceptual/implementación)

#### 2. Taxonomía Operativa (3 variantes)

**Documentos involucrados**:
- `DOMAIN_PACK_ARCHITECTURE.md` (arquitectura conceptual)
- `DOMAIN_CLASSIFICATION_2026-05-12.md` (clasificación por fecha)
- `app/catalogs/taxonomia_operativa_pyme_argentina_v0.json` (JSON ejecutable)

**Conflicto**: Taxonomía documentada como arquitectura, como snapshot temporal y como catálogo ejecutable.
**Contexto**: La arquitectura define estructura; la clasificación por fecha permite trazabilidad; el JSON es implementación operativa.
**Acción pendiente**: Migrar docs conceptuales; JSON como referencia operativa. Clarificar relación en MIGRATION_INDEX.md.
**Riesgo**: medio (posible desincronización entre conceptual y ejecutable)

#### 3. Fórmulas Financieras (3 variantes)

**Documentos involucrados**:
- `CLINICAL_MATHEMATICAL_KERNEL...md` (conceptual)
- `formulas_smartpyme_v0.json` (catálogo ejecutable)
- `app/services/formula_engine_service.py` (implementación)

**Conflicto**: Fórmulas documentadas conceptualmente, en catálogo JSON y en código de servicio.
**Contexto**: El kernel define principios matemáticos; el JSON lista fórmulas aplicables; el servicio ejecuta cálculos.
**Acción pendiente**: Migrar docs conceptuales y catálogo; código en runtime. Validar consistencia fórmula→JSON→implementación en Fase 5.
**Riesgo**: medio (inconsistencia entre definición y ejecución)

### Contradicciones Terminológicas

#### 4. Knowledge Tank vs Tanque de Conocimiento

**Documentos involucrados**:
- `KNOWLEDGE_TANKS_ARCHITECTURE.md`
- `SMARTPYME_TANQUES_CONOCIMIENTO_FISIOLOGIA_PATOLOGIAS.md`
- `SPECIFIC_KNOWLEDGE_TANKS_AND_SOURCE_ENGINE.md`

**Conflicto**: Uso indistinto de término inglés "Knowledge Tank" y castellano "Tanque de Conocimiento".
**Contexto**: Ambos términos refieren al mismo concepto: repositorio sectorial de conocimiento PyME.
**Acción pendiente**: Definir término rector en Fase 4 (normalización). Sugerencia: "Tanque de Conocimiento" para documentación en castellano.
**Riesgo**: medio (confusión en búsqueda y referencia cruzada)

#### 5. Domain Pack vs Paquete de Dominio

**Documentos involucrados**:
- `DOMAIN_PACK_ARCHITECTURE.md`
- `DOMAIN_CLASSIFICATION_2026-05-12.md`

**Conflicto**: Mismo fenómeno de mezcla lingüística: "Domain Pack" (inglés técnico) vs "Paquete de Dominio" (castellano negocio).
**Contexto**: Concepto de módulo de conocimiento por rubro/función.
**Acción pendiente**: Resolver en Fase 4. Sugerencia: mantener "Domain Pack" como término técnico, documentar equivalencia.
**Riesgo**: bajo (término principalmente interno de arquitectura)

#### 6. OperationalCase vs Caso Operativo

**Documentos involucrados**:
- Múltiples documentos de arquitectura y conversacional
- Código: `operational_case_service.py`

**Conflicto**: Naming de componente central del sistema: inglés técnico vs castellano descriptivo.
**Contexto**: `OperationalCase` es entidad de runtime; "caso operativo" es descripción conceptual.
**Acción pendiente**: Mantener `OperationalCase` como nombre técnico en código; usar "caso operativo" en documentación conceptual. Documentar esta convención.
**Riesgo**: bajo (si se mantiene convención clara)

#### 7. findings vs hallazgos (ampliación)

**Documentos involucrados**:
- `PYME_SYMPTOM_PATHOLOGY_ATLAS.md`
- `HYPOTHETICO_DEDUCTIVE_METHOD.md`
- `CONVERSATIONAL_METHODS.md`

**Conflicto**: Uso mixto de "findings" (inglés técnico) y "hallazgos" (castellano negocio) para referirse al resultado cuantificado de una investigación.
**Contexto**: Término clave en flujo diagnóstico: hipótesis → evidencia → contraste → hallazgo.
**Acción pendiente**: Resolver en Fase 4. Sugerencia: "hallazgo" como término rector en documentación; mantener "finding" solo en referencias técnicas heredadas.
**Riesgo**: medio (término central en flujo semántico)

### Drifts de Formato

#### 8. JSON vs Markdown para catálogos

**Documentos involucrados**:
- `formulas_smartpyme_v0.json`
- `taxonomia_operativa_pyme_argentina_v0.json`
- Documentos conceptuales en Markdown

**Conflicto**: Catálogos operativos en JSON ejecutable vs documentación conceptual en Markdown.
**Contexto**: JSON para ejecución/runtime; Markdown para lectura humana y trazabilidad conceptual.
**Acción pendiente**: Mantener dualidad; documentar relación JSON↔Markdown en índice. Validar sincronización en Fase 5.
**Riesgo**: medio (desincronización entre catálogo ejecutable y documentación)

---

## Resumen de Riesgos por Categoría

| Categoría | Drifts detectados | Riesgo predominante |
|-----------|------------------|---------------------|
| Terminología | 4 (findings/hallazgos, Knowledge Tank/Tanque, Domain Pack/Paquete, OperationalCase/Caso) | medio |
| Duplicación conceptual | 3 grupos (patologías, taxonomías, fórmulas) | bajo-medio |
| Formato/serialización | 1 (JSON vs Markdown) | medio |
| Idioma técnico | 2 (inglés/castellano en fórmulas, términos híbridos) | medio |

---

> **Nota**: Todos los drifts registrados quedan pendientes de resolución en Fase 4 (Normalización Terminológica y Deduplicación). Ninguna decisión de resolución se toma en Fase 3.

**Última actualización**: 2026-05-18 — Fase 3 completada