# PymIA Museum Catalog

## Estado

`MUSEUM_CATALOG_V1`

## Propósito

Catalogar el museo histórico de PymIA sin repararlo, moverlo ni volver a mezclarlo con `PymIA-Live`.

Este documento existe para impedir que documentación histórica, huérfana o rota vuelva a gobernar el desarrollo del núcleo limpio.

```text
El museo se cataloga.
No se repara ahora.
No se migra a PymIA-Live.
No gobierna el desarrollo nuevo.
```

---

## 1. Veredicto de origen

Reporte recibido:

```text
MUSEUM_REQUIRES_CATALOGING
```

Hallazgo central:

```text
DOCUMENTATION_INDEX.md existe, pero no gobierna completamente el museo.
```

Cobertura estimada:

```text
docs/ indexado por DOCUMENTATION_INDEX.md: 262/482 = ~54%
cobertura real del museo total: ~40%
```

---

## 2. Taxonomía de clasificación

| Estado | Significado |
|---|---|
| `LIVE_REFERENCE` | Documento o carpeta que puede orientar operación vigente, sin desplazar a `PymIA-Live`. |
| `APPROVED_HISTORY` | Evidencia histórica aprobada. Conserva verdad de contexto, pero no manda el próximo desarrollo. |
| `LEGACY_CONTEXT` | Material útil para entender evolución, decisiones o errores, sin autoridad operativa. |
| `ORPHAN` | Superficie no gobernada por índice canónico visible. |
| `BROKEN_REFERENCE` | Documento con links o referencias internas muertas. |
| `DO_NOT_USE` | Superficie congelada, riesgosa o explícitamente fuera del núcleo vivo. |

---

## 3. Regla de autoridad

Orden de autoridad vigente:

```text
1. PymIA-Live ejecutable y smoke real PASS
2. PymIA-Live/README.md
3. PymIA-Live/docs/pymia/MIGRATION_REPORT.md
4. docs/pymia/PYMIA_LIVE_CORE_MANIFEST.md
5. docs/pymia/PYMIA_LIVE_PIPELINE.md
6. docs/ops/RUNBOOK_PILOTO_ASISTIDO_POST_LC.md
7. Museo histórico catalogado
```

Regla:

```text
Si un documento histórico contradice a PymIA-Live, manda PymIA-Live.
```

---

## 4. Catálogo por áreas

| Área | Estado | Observación |
|---|---|---|
| `PymIA-Live/` | `LIVE_REFERENCE` | Baseline limpio funcional validado por smoke real. No debe contaminarse con museo. |
| `docs/pymia/PYMIA_LIVE_CORE_MANIFEST.md` | `LIVE_REFERENCE` | Manifiesto de separación vivo/museo. |
| `docs/pymia/PYMIA_LIVE_PIPELINE.md` | `LIVE_REFERENCE` | Mapa del pipeline vivo extraído. |
| `docs/ops/RUNBOOK_PILOTO_ASISTIDO_POST_LC.md` | `LIVE_REFERENCE` | Runbook vivo operativo, aunque `docs/ops/` figura como huérfano en el índice general. |
| `DOCUMENTATION_INDEX.md` | `LEGACY_CONTEXT` | Índice maestro parcial. No cubre todo el museo. |
| `docs/doctrina/` | `ORPHAN` | Bloque completo fuera del índice efectivo. No usar como autoridad directa para `PymIA-Live`. |
| `docs/smartpyme/` | `APPROVED_HISTORY` | Parcialmente indexado. Contiene checkpoints y material aprobado, pero con cobertura incompleta. |
| `docs/pymia/` | `APPROVED_HISTORY` | Parcialmente indexado. Contiene documentos vivos y muchos históricos; requiere discriminación por archivo. |
| `docs/ops/` | `ORPHAN` | Fuera del índice. Incluye runbook vivo, por excepción catalogado como `LIVE_REFERENCE`. |
| `docs/roadmap/` | `ORPHAN` | No debe gobernar desarrollo actual sin promoción explícita. |
| `docs/conversa-engine/` | `DO_NOT_USE` | Superficie histórica/congelada. No migrar a `PymIA-Live`. |
| `docs/microsaas/` | `LEGACY_CONTEXT` | Material contextual; no autoridad operativa vigente. |
| `docs/mermaid/` | `ORPHAN` | Diagramas fuera de gobierno canónico visible. |
| `Pymia-memoria/` | `LEGACY_CONTEXT` | Memoria operativa parcial. Referencial, no fuente soberana. |
| `pymia/domain/` | `LEGACY_CONTEXT` | Mapping conceptual parcial, sin cobertura path-level efectiva. |
| `landing/` | `ORPHAN` | Material comercial/presentacional fuera del núcleo vivo. |
| `scripts/` | `ORPHAN` | Scripts sin inventario maestro visible. No ejecutar por defecto. |
| `prueba_excels/` | `LIVE_REFERENCE` | Fixtures útiles para smoke y validación; copiar sólo los necesarios en `PymIA-Live`. |
| `tools/bem_schema_builder/` | `LIVE_REFERENCE` | Entró en `PymIA-Live` por dependencia descubierta. No eliminar sin validación adicional. |
| `.tmp/` | `DO_NOT_USE` | Artefactos temporales. No fuente de verdad. |
| `_local_quarantine/` | `DO_NOT_USE` | Cuarentena local. No fuente de autoridad. |

---

## 5. Huérfanos reales declarados

```text
docs/ops/
docs/roadmap/
docs/doctrina/
docs/conversa-engine/
docs/microsaas/
docs/mermaid/
Pymia-memoria/
landing/
scripts/
prueba_excels/
tools/bem_schema_builder/
```

Lectura:

```text
Huérfano no significa inútil.
Significa no gobernado por índice canónico suficiente.
```

---

## 6. Referencias muertas declaradas

| Documento | Referencia muerta |
|---|---|
| `docs/pymia/KERNEL_PIPELINE_INVENTORY.md` | Apunta a varios tests `../SmartPyme/tests/...` inexistentes en este repo. |
| `docs/catalogo/diseno-catalogo-clinico.md` | Referencia `docs/architecture/SYMPTOM_PATHOLOGY_CATALOG_DESIGN.md` inexistente. |
| `docs/catalogo/atlas-sintomas-patologias.md` | Referencia `docs/architecture/PYME_SYMPTOM_PATHOLOGY_ATLAS.md` inexistente. |
| `docs/contratos/owner-decision-v1.md` | Referencia `docs/product/OWNER_DECISION_CONTRACT_V1.md` inexistente. |
| `docs/contratos/evidence-chain-v1.md` | Referencia `docs/product/EVIDENCE_CHAIN_CONTRACT_V1.md` inexistente. |

Regla:

```text
No corregir referencias muertas durante ciclos de PymIA-Live.
Sólo catalogarlas salvo tarea explícita de mantenimiento del museo.
```

---

## 7. Riesgos del museo

| Riesgo | Descripción | Mitigación |
|---|---|---|
| Autoridad falsa | Documentos viejos parecen rectores por volumen o tono. | `PymIA-Live` manda sobre el museo. |
| Deriva documental | Roadmaps y prompts antiguos reabren frentes cerrados. | No abrir roadmap desde museo sin promoción explícita. |
| Contaminación de núcleo | Dependencias históricas vuelven a entrar al repo limpio. | Toda migración a `PymIA-Live` requiere smoke/import validation. |
| Reparación infinita | Intentar arreglar 482 docs antes de avanzar. | Catalogar, no reparar. |
| Memoria como política | `Pymia-memoria/` se usa como fuente soberana. | Memoria es contexto, no autoridad. |

---

## 8. Regla de uso para próximos chats/agentes

Antes de usar un documento histórico, clasificarlo:

```text
LIVE_REFERENCE
APPROVED_HISTORY
LEGACY_CONTEXT
ORPHAN
BROKEN_REFERENCE
DO_NOT_USE
```

Si no puede clasificarse:

```text
NO_USAR_COMO_AUTORIDAD
```

---

## 9. Qué no se hace en este ciclo

```text
No mover archivos.
No borrar archivos.
No corregir links.
No reindexar todo docs/.
No migrar museo a PymIA-Live.
No abrir features.
No crear ADR.
No convertir este catálogo en roadmap.
```

---

## 10. Decisión final

```text
PymIA histórico queda como museo catalogado.
PymIA-Live queda como baseline limpio funcional.
El museo puede informar, pero no gobernar.
```

Próximo paso recomendado:

```text
Auditoría externa post-migración de PymIA-Live.
```
