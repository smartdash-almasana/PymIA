# PymIA Memoria — Decisiones vigentes

Fecha: 2026-06-16

## Decisión rectora

```text
El conocimiento de dominio es enchufable.
El kernel permanece estable.
```

Consecuencia:

```text
JSON/contratos = fuente declarativa de conocimiento.
Python runtime = carga, valida, calcula, orquesta, renderiza, falla cerrado.
```

---

## Autoridad operativa vigente

```text
Repo git real: E:\BuenosPasos\smartbridge\PymIA
Subcarpeta viva: PymIA-Live
No tratar PymIA-Live como repo git independiente.
```

Orden de autoridad:

```text
1. PymIA-Live ejecutable y tests validados.
2. PymIA-Live/README.md.
3. PymIA-Live/docs/pymia/PYMIA_LIVE_TARGET_ARCHITECTURE_V1.md.
4. Contratos JSON vivos bajo PymIA-Live/pymia/contracts/.
5. Código runtime vivo bajo PymIA-Live/pymia/.
6. Documentos vivos explícitamente promovidos.
7. Museo histórico catalogado, sólo como contexto.
```

HEAD técnico vigente:

```text
faf9008 refactor(pymia-live): realign pipeline trace identity
```

Tests reportados:

```text
243/243 PASS
```

---

## Decisiones arquitectónicas vigentes

```text
vertical_slice.py no debe crecer.
vertical_slice.py debe permanecer como adaptador CLI.
Los futuros canales no deben copiar lógica desde vertical_slice.py.
Los futuros canales deben invocar una frontera de aplicación común.
```

Frontera de aplicación vigente:

```text
PymIA-Live/pymia/application/vertical_pipeline.py
```

CLI vigente:

```text
PymIA-Live/pymia/cli/vertical_slice.py
```

Distribución vigente de responsabilidades:

```text
owner_simple                -> pymia/smartpyme/owner_output.py
registration                -> pymia/smartpyme/pipeline_registration.py
question resolution         -> pymia/smartpyme/question_resolution.py
diagnostic operator adapter -> pymia/smartpyme/diagnostic_operator_adapter.py
owner markdown renderer     -> pymia/rendering/owner_markdown_renderer.py
vertical pipeline           -> pymia/application/vertical_pipeline.py
```

Compatibilidad temporal aceptada:

```text
vertical_slice.py puede re-exponer imports desde pymia.application.vertical_pipeline para preservar consumidores/tests históricos.
No debe conservar cuerpos de las funciones movidas.
```

---

## Identidad de trazabilidad vigente

La traza distingue caso de uso y canal.

Caso de uso:

```text
pipeline_name   -> vertical_pipeline_evidence_spine
pipeline_module -> pymia.application.vertical_pipeline
entrypoint      -> build_pipeline
service_name    -> vertical_pipeline
registered_by   -> vertical_pipeline
```

Canal:

```text
channel -> cli
```

Regla:

```text
El CLI no debe figurar como dueño del caso de uso.
El canal CLI sí puede figurar como canal de entrada en metadata.
```

---

## Decisiones técnicas vigentes

```text
formula_rules_v1.json gobierna reglas declarativas de fórmulas.
formula_engine_service.py usa registry formula_id -> calculator.
SUPPORTED_FORMULAS no debe volver.
FormulaDefinition no debe volver.
calculate_formula no debe volver.
presentation_labels_v1.json gobierna labels owner-facing.
question_alignment_v1.json gobierna QAG.
pathology_rules_v1.json gobierna reglas de patologías.
evidence_requirement_aliases_v1.json gobierna aliases de evidence requirements.
formula_aliases_v1.json gobierna aliases de evidencia hacia fórmulas.
evidence_requirement_copy_v1.json gobierna el template owner-facing mínimo del matcher.
owner_facing_report_copy_v1.json gobierna warnings owner-facing por status operativo.
vertical_slice_copy_v1.json gobierna copy mínimo y fallback owner-facing local.
language_corpus_seed.json gobierna labels declarativos del corpus dueño-variable.
pipeline_run_v1.py gobierna la identidad de ejecución del pipeline vertical.
```

---

## Decisiones de higiene vigentes

```text
.tmp/ no se versiona.
_local_quarantine/ no se versiona.
PymIA-Live/.tmp_smoke_owner_alignment/ no se versiona salvo decisión explícita de evidencia sanitizada.
Pymia-memoria/ está trackeado: .gitignore no impide cambios porque los archivos ya existen en índice.
MUSEUM_CATALOG.md no gobierna runtime; sólo puede catalogar frontera museo/vivo.
ROLE_PLAYING_ONBOARDING_FINDINGS.md es hallazgo experimental hasta promoción explícita.
```

---

## Decisión vigente sobre owner_simple

```text
No crear owner_output_v1 todavía.
owner_simple vive como protocolo local congelado en pymia/smartpyme/owner_output.py.
Su estado sigue siendo FROZEN_LOCAL_PRESENTATION_CONTRACT.
```

Criterios para habilitar un split futuro:

```text
- segundo canal consumidor;
- necesidad de schema tipado formal;
- drift real entre tests, salida y contrato implícito;
- owner_simple se vuelve salida base del MVP;
- separación necesaria entre renderer técnico y renderer humano.
```

---

## Deuda viva reconocida

```text
Renderer markdown todavía decide QAG y recompone owner_simple.
vertical_slice.py conserva imports de compatibilidad temporal.
build_structured_summary vive dentro de application/vertical_pipeline.py.
operator next step copy hardcodeado sigue siendo baja prioridad.
```

Deuda cerrada:

```text
La identidad de trazabilidad ya no apunta a pymia.cli.vertical_slice como dueño del caso de uso.
vertical_slice_cli ya no gobierna la identidad del pipeline.
```

Estas deudas no autorizan refactor automático. Requieren auditoría focal y clasificación previa.

---

## Reglas de trabajo

```text
Si trae evidencia -> validar evidencia.
Si pide prompt -> dar prompt con encabezado: PROMPT — objetivo / PARA: agente.
Si pide decisión -> dar decisión.
Si pide siguiente paso -> dar un solo siguiente paso.
Si pide ejecutar -> pedir AUTH si modifica repo, tests, commit o push.
Lectura/auditoría puede hacerse sólo cuando el usuario la autoriza o el frente lo requiere explícitamente.
```

---

## Reglas de limpieza

```text
No agregar .tmp/
No agregar PymIA-Live/.tmp_smoke_owner_alignment/
No agregar _local_quarantine/
No commitear museo ni documentación no intencional.
No mezclar memoria, museo, smoke y runtime en un mismo commit.
No mezclar memoria documental con runtime en el mismo commit.
```

---

## ARCHITECTURE MEMORY GATE

Reglas y controles de frontera para evitar derivas metodológicas en la IA:

- **Lectura obligatoria:** Antes de proponer cualquier slice, el asistente de IA debe leer la memoria vigente (`_estado_actual.md`, `_task_actual.md`, `_decisiones_vigentes.md`).
- **Respeto a los frenos:** Si la memoria documental explícitamente dice parar un frente, este no puede reabrirse o proponerse bajo nuevas hipótesis de refactorización o saneamiento estético salvo que se demuestre una deuda técnica material bloqueante para la ejecución.
- **Clasificación obligatoria de frentes de trabajo:** Todo frente de trabajo propuesto debe clasificarse explícitamente en una de las siguientes categorías:
  - **A. CAPACIDAD OPERATIVA**: agrega funcionalidad, valor real de negocio o interfaces ejecutables para la pyme.
  - **B. DEUDA TÉCNICA MATERIAL**: resuelve bug demostrado, bloqueo de tests en runtime o falla real del pipeline.
  - **C. SANEAMIENTO MENOR**: refactorización cosmética, renombrado, micro-split o embellecimiento sin deuda material.
  - **D. DOCUMENTACIÓN / MEMORIA**: actualización de checkpoints, memoria documental o reglas de gobernanza.
  - **E. EXPERIMENTO**: pruebas aisladas sin tocar runtime productivo.
  - **F. MUSEO / HISTÓRICO**: movimiento de archivos en desuso al archivo histórico.
- **Control de avance:** Sólo A, B o D pueden avanzar de forma ordinaria. C requiere autorización explícita del usuario y no puede iniciarse automáticamente.
- **Dirección arquitectónica:** No usar la IA ni Codex como sustituto de la dirección arquitectónica explícita del Owner.
- **Calidad profesional:** No priorizar un funciona rápido sobre coherencia arquitectónica cuando los contratos exijan adherencia estricta a patrones data-driven.

---

## Frase rectora actual

```text
PymIA-Live debe quedar pequeño, trazable, multicanal-ready y gobernado por contratos declarativos.
```
