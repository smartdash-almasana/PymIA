# Graphify Usage Guide for PymIA-Live

## Estado

Guía operativa mínima para usar Graphify como herramienta externa de navegación arquitectónica del repo.

```text
Estado: ACTIVE_GUIDE
Tipo: TOOLING_GUIDE
Runtime impact: NONE
Productive code impact: NONE
```

## Propósito

Graphify se usa para reducir lectura manual diaria del repo y localizar relaciones entre nodos, archivos, contratos y módulos antes de abrir auditorías largas.

Graphify no es una feature de PymIA.
Graphify no pertenece al runtime de PymIA-Live.
Graphify no reemplaza la lectura de archivos fuente.

La regla central es:

```text
Graphify orienta.
La ruta de archivo confirma.
Los edges INFERRED son hipótesis.
Los nodos del museo no gobiernan PymIA-Live.
```

## Estado operativo conocido

```text
GRAPHIFY_READY
```

Artefactos locales esperados:

```text
graphify-out/graph.json
graphify-out/graph.html
graphify-out/GRAPH_REPORT.md
graphify-out/manifest.json
```

Estos artefactos son de análisis local y no deben entrar en commits de PymIA-Live salvo decisión explícita posterior.

## Qué sí usar

Usar Graphify para:

```text
- ubicar nodos centrales;
- encontrar rutas entre conceptos;
- descubrir archivos relevantes antes de leer;
- distinguir hubs reales de ruido;
- reducir auditoría manual repetitiva;
- orientar preguntas arquitectónicas sobre PymIA-Live.
```

## Qué no hacer

No usar Graphify para:

```text
- declarar PASS sin leer fuentes;
- justificar cambios de código;
- convertir un edge INFERRED en verdad;
- mezclar museo histórico con núcleo vivo;
- reabrir arquitectura cerrada sin hallazgo verificable;
- commitear graphify-out/ por inercia;
- tratar Graphify como dependencia productiva.
```

## Regla de filtro PymIA-Live

Graphify puede mezclar:

```text
repo raíz PymIA
+ PymIA-Live
+ museo histórico
+ tooling local
```

Por lo tanto, para decisiones del núcleo vivo sólo cuenta como evidencia inicial aquello que después pueda confirmarse en rutas:

```text
PymIA-Live/...
```

Si una consulta devuelve un nodo útil pero la ruta no pertenece a `PymIA-Live/`, clasificarlo como:

```text
MUSEUM_OR_LEGACY_CANDIDATE
```

hasta verificación manual.

## Rutina diaria recomendada

Antes de leer documentos largos:

```powershell
graphify query "How is PymIA-Live structured?"
```

Después, usar una consulta más focal:

```powershell
graphify query "Where does vertical_slice.py connect to records, contracts, renderers and pipeline execution?"
```

Luego leer sólo los archivos señalados que estén bajo:

```text
PymIA-Live/
```

## Queries base

### Estructura viva

```powershell
graphify query "How is PymIA-Live structured?"
```

### Pipeline vertical

```powershell
graphify query "Where does vertical_slice.py connect to records, contracts, renderers and pipeline execution?"
```

### Narrativa, ficha mínima, evidencia y traza

```powershell
graphify query "How are owner narrative, BusinessTaxonomy, AnamnesisRecord, InvestigationRecord, EvidenceRecord, EvidenceRequestRecord, OwnerAnswerRecord and PipelineRunRecord connected?"
```

### Evidencia a salida owner-facing

```powershell
graphify query "How does StructuredEvidence connect to owner-facing output?"
```

### Contratos y renderers

```powershell
graphify query "What are the central contracts and owner-facing renderers in PymIA-Live?"
```

### Rutas específicas

```powershell
graphify path "StructuredEvidence" "vertical_slice.py"
graphify path "PipelineRunRecord" "vertical_slice.py"
graphify path "StructuredEvidence" "OwnerQuestionsBundle"
```

### Explicación de nodos

```powershell
graphify explain "StructuredEvidence"
graphify explain "PipelineRunRecord"
graphify explain "PrimaryCaseFile"
```

## Archivos prioritarios para confirmar flujo vivo

Leer primero estos archivos cuando una query apunte al flujo vertical:

```text
PymIA-Live/pymia/cli/vertical_slice.py
PymIA-Live/pymia/application/vertical_pipeline.py
PymIA-Live/pymia/smartpyme/pipeline_registration.py
PymIA-Live/pymia/smartpyme/storage.py
PymIA-Live/pymia/rendering/owner_markdown_renderer.py
PymIA-Live/pymia/smartpyme/owner_facing_report.py
PymIA-Live/tests/e2e/test_vertical_slice_cli.py
```

Leer según necesidad:

```text
PymIA-Live/pymia/smartpyme/anamnesis.py
PymIA-Live/pymia/smartpyme/investigation.py
PymIA-Live/pymia/smartpyme/evidence.py
PymIA-Live/pymia/smartpyme/evidence_request.py
PymIA-Live/pymia/smartpyme/owner_answer.py
PymIA-Live/pymia/contracts/pipeline_run_v1.py
PymIA-Live/pymia/contracts/presentation_labels_v1.py
PymIA-Live/pymia/contracts/vertical_slice_copy_v1.py
```

## Nodos centrales observados

Graphify detectó como nodos de alto grado o alta utilidad:

```text
StructuredEvidence
OperationalHypothesis
OwnerQuestionsBundle
StructuredSelectors
BusinessTaxonomySnapshot
EvidenceRequirement
PipelineRunRecord
PrimaryCaseFile
```

Interpretación operativa:

```text
StructuredEvidence = nodo de frontera crítico.
PipelineRunRecord = traza de ejecución.
OwnerQuestionsBundle = puente hacia preguntas al dueño.
BusinessTaxonomySnapshot / BusinessTaxonomy = ficha/taxonomía mínima.
EvidenceRequirement = necesidad de evidencia.
```

Cualquier cambio sobre `StructuredEvidence` o contratos cercanos requiere TaskSpec, tests y auditoría focal. Graphify no autoriza cambios por sí mismo.

## Nodos ruidosos a ignorar o filtrar

No tomar como dominio real sin verificación:

```text
Any
Path
str
Enum
UUID
datetime
BaseException
ValueError
docstrings largos
rationale nodes
self cycles de un solo archivo
```

Estos nodos suelen venir de AST, tipos Python o documentación incrustada y pueden inflar comunidades.

## Cómo interpretar edges

```text
EXTRACTED = relación observada por análisis estructural.
INFERRED = hipótesis del extractor/modelo.
AMBIGUOUS = requiere especial cuidado.
```

Regla:

```text
EXTRACTED puede orientar lectura.
INFERRED exige confirmación manual.
AMBIGUOUS no se usa para decidir sin evidencia adicional.
```

## Cuándo actualizar el grafo

Actualizar después de cambios grandes de código o reorganización importante:

```powershell
graphify update .
```

No hace falta actualizar por cada documento menor.

## Estado git esperado

Después de generar Graphify localmente pueden quedar untracked:

```text
?? graphify-out/
?? .agents/
?? .graphifyignore
?? .opencode/
```

No commitear esos artefactos salvo decisión separada y explícita.

## Criterio de uso correcto

Una respuesta basada en Graphify debe distinguir:

```text
Hecho confirmado por archivo fuente.
Hipótesis sugerida por Graphify.
Nodo legacy/museo.
Gap real.
Ruido del grafo.
```

## Veredicto

```text
Graphify debe usarse como primer filtro de navegación diaria.
Graphify no debe usarse como verdad única.
Graphify reduce fricción, no reemplaza método.
```
