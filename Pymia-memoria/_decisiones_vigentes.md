# PymIA Memoria — Decisiones vigentes

Fecha: 2026-06-22

## Decisión metodológica vigente — bloques funcionales, no microciclo

Regla actual:

```text
1 bloque funcional
→ Codex ejecuta varias piezas relacionadas
→ tests amplios del bloque
→ reporte único
→ auditoría única
→ commit/push único
```

Se abandona el patrón:

```text
archivo mínimo
→ permiso
→ Codex
→ vuelta al chat
→ otro permiso
→ otro archivo
→ commit/push microscópico
```

Tamaño sano de bloque:

```text
1 capacidad operable
3–8 archivos aproximadamente
30–100+ tests focales o suite relevante
1 commit
1 push
```

La seguridad se mantiene por:

```text
allowlist explícita
tests amplios
auditoría única
forbidden layers scan conceptual
no git add .
no mezclar frentes heterogéneos
```

---

## Decisión vigente — Servicio 1 First Aid operable

Estado:

```text
SERVICE_1_OPERATOR_DELIVERY_PACKAGE_BLOCK_V1 = CLOSED / PUSHED
```

Commit reportado:

```text
fe582c1
```

Capacidad actual:

```text
operator harness
→ pipeline explícito
→ tools allowlist
→ FirstAidToolResultV1[]
→ aggregate
→ XLSX por tool
→ summary.txt
→ operator_report.txt
→ README_ENTREGA.md
→ manifest.json
→ hashes + bytes
→ carpeta final entregable
```

Interpretación:

```text
Servicio 1 First Aid ya es capacidad operable asistida.
No equivale a Servicio 1 completo.
No equivale a contabilidad automatizada.
No equivale a diagnóstico integral.
```

Próxima decisión recomendada:

```text
SERVICE_1_FIRST_AID_PILOT_OFFER_V1
```

---

## Decisión rectora de producto

```text
PymIA no es un oráculo.
PymIA es un sistema operativo para reducir tinieblas e incertidumbre mediante preguntas, evidencia y opciones proporcionales.
```

Consecuencia:

```text
La profundidad de servicio no debe adivinarse como primer movimiento.
La entrada debe preguntar primero qué necesita resolver el dueño hoy.
```

Pregunta madre:

```text
¿Qué necesitás resolver hoy?
```

Opciones iniciales:

```text
1. Primeros Auxilios
   Tengo algo puntual para ordenar o revisar ahora.

2. Problema específico / diagnóstico sectorial
   Tengo un problema más complejo que quiero entender.

3. Estructura completa de la empresa
   Quiero analizar y ordenar la empresa como sistema.
```

Secuencia rectora:

```text
pregunta inicial
→ opción elegida por el dueño
→ evidencia mínima
→ profundidad de servicio
→ respuesta proporcional
```

Regla de service depth:

```text
Service depth no debe ser adivinación.
Debe combinar:
1. elección explícita del dueño;
2. evidencia disponible;
3. señales del lenguaje;
4. límites de suficiencia.
```

La elección explícita del dueño manda primero.

---

## Decisión rectora de conocimiento

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
7. Código runtime vivo bajo PymIA-Live/pymia/.
8. Contratos JSON vivos bajo PymIA-Live/pymia/contracts/.
9. Documentos vivos explícitamente promovidos.
10. Museo histórico catalogado, sólo como contexto.
```

Commits recientes aceptados:

```text
716c6d7 docs(producto): define excel treatment lab concept
f924c27 feat(pymia-live): add first aid entrypoint helper
dd0e659 feat(pymia-live): add first aid owner output helper
67db189 chore(graphify): include pymia live in architecture graph
```

---

## Decisión vigente sobre FIRST_AID

```text
FIRST_AID_ENTRYPOINT_V1 = CLOSED
FIRST_AID_OWNER_OUTPUT_V1 = CLOSED
FIRST_AID_APPLICATION_WIRING_V1 = DEFERRED
```

Cadena cerrada:

```text
service_depth.py
→ first_aid_entrypoint.py
→ first_aid_owner_output.py
```

Interpretación:

```text
FIRST_AID existe como capacidad latente cerrada.
No está cableado a application, CLI, rendering, storage, OCF ni diagnóstico.
```

Regla:

```text
No cablear FIRST_AID por simetría arquitectónica.
No cablear FIRST_AID porque los helpers existen.
Sólo reabrir application wiring si existe canal consumidor real, caso piloto real o test de integración fallando por falta de wiring.
```

Checkpoint:

```text
```

Estado:

```text
CREATED_NOT_COMMITTED
```

---

## Decisiones arquitectónicas vigentes

```text
vertical_slice.py no debe crecer.
vertical_slice.py debe permanecer como adaptador CLI.
Los futuros canales no deben copiar lógica desde vertical_slice.py.
Los futuros canales deben invocar una frontera de aplicación común sólo cuando exista consumidor real.
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
FIRST_AID latent entry      -> pymia/smartpyme/first_aid_entrypoint.py
FIRST_AID latent owner view -> pymia/smartpyme/first_aid_owner_output.py
```

Compatibilidad temporal aceptada:

```text
vertical_slice.py puede re-exponer imports desde pymia.application.vertical_pipeline para preservar consumidores/tests históricos.
No debe conservar cuerpos de las funciones movidas.
```

---

## Frontera application/rendering vigente

Regla:

```text
El renderer markdown no decide dominio.
El renderer markdown no resuelve QAG.
El renderer markdown no reconstruye owner_simple.
El renderer markdown sólo presenta datos ya resueltos por el caso de uso.
```

Prohibición vigente para `pymia/rendering/owner_markdown_renderer.py`:

```text
No importar pymia.smartpyme.owner_output.
No importar pymia.smartpyme.question_alignment_gate.
No importar pymia.smartpyme.question_resolution.
No llamar build_owner_simple_view.
No llamar align_next_question.
No llamar _resolve_owner_question_and_reference.
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
service_depth.py clasifica profundidad proporcional, pero no debe actuar como oráculo si puede preguntarse explícitamente al dueño.
```

---

## Decisiones de higiene vigentes

```text
.tmp/ no se versiona.
_local_quarantine/ no se versiona.
PymIA-Live/.tmp_smoke_owner_alignment/ no se versiona salvo decisión explícita de evidencia sanitizada.
graphify-out/ queda regenerable y untracked intencional.
MUSEUM_CATALOG.md no gobierna runtime; sólo puede catalogar frontera museo/vivo.
ROLE_PLAYING_ONBOARDING_FINDINGS.md es hallazgo experimental hasta promoción explícita.
```

---

## Estado Graphify

```text
GRAPHIFY_SCOPE_FIX_V1 = CLOSED
GRAPHIFY_POST_COMMIT_REGEN_CHECK_V1 = CLOSED
```

Regla:

```text
Graphify se usa sólo si resuelve una decisión arquitectónica concreta.
No usarlo como ritual de validación redundante.
No regenerar graphify-out/ por costumbre.
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
vertical_slice.py conserva imports de compatibilidad temporal.
build_structured_summary vive dentro de application/vertical_pipeline.py.
operator next step copy hardcodeado sigue siendo baja prioridad.
Language corpus sigue limitado y puede exponer snake_case owner-facing si faltan labels.
Runbook/checklist operativo debe actualizar flags y protocolo de piloto.
```

Deuda cerrada:

```text
La identidad de trazabilidad ya no apunta a pymia.cli.vertical_slice como dueño del caso de uso.
vertical_slice_cli ya no gobierna la identidad del pipeline.
owner_markdown_renderer.py ya no decide QAG.
owner_markdown_renderer.py ya no reconstruye owner_simple.
owner_markdown_renderer.py ya no importa servicios smartpyme de dominio.
FIRST_AID helpers quedaron cerrados como capacidad latente, sin wiring prematuro.
```

Estas deudas no autorizan refactor automático. Requieren auditoría focal y clasificación previa.

---

## Reglas de trabajo

```text
Si trae evidencia -> validar evidencia.
Si pide prompt -> dar prompt con encabezado: PROMPT — objetivo / PARA: agente.
Si pide decisión -> dar decisión.
Si pide siguiente paso -> dar un solo siguiente paso.
Si pide ejecutar -> pedir AUTH si modifica repo, tests, commit o push, salvo que el usuario haya autorizado explícitamente el frente.
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
No mezclar memoria documental con runtime en el mismo commit salvo autorización explícita del frente documental.
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
PymIA-Live debe quedar pequeño, trazable, multicanal-ready, gobernado por contratos declarativos y guiado por preguntas explícitas antes que por adivinación.
```
