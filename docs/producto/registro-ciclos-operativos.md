# Registro de ciclos operativos — PymIA

Contexto heredado. Este registro no autoriza jobs, workflows, orquestación, authorization flow, factory, app.*, MCP legacy ni runtime Hermes duplicado dentro de PymIA. Rige `../../ARCHITECTURE_GUARDRAILS.md`.

## CICLO 1 — PASS

Fecha: 2026-05-16

### Scope

Documentación canónica.

### Archivo tocado

- `docs/README.md`

### Objetivo

Corregir referencias documentales rotas sin incorporar documentos nuevos, sin reconstruir desde memoria y sin tocar runtime.

### Cambios

- Rutas documentales presentes expresadas como rutas reales.
- Pendientes explícitos separados como no-fuentes.
- Eliminadas referencias que el auditor interpretaba como archivos faltantes.

### Validación

```text
audit_docs_index: OK
pytest: 61 passed
forbidden terms: clean
demo canónica: PASS funcional
```

### Guardrails

```text
Sin jobs.
Sin workflows.
Sin orquestación nueva.
Sin authorization flow.
Sin factory/app/MCP legacy.
Sin runtime Hermes duplicado.
Hermes conversa, PymIA computa: preservado.
```

### Pendiente siguiente

Ciclo 2: reparar legibilidad UTF-8 / mojibake de demo CLI.

## CICLO 2 — PASS

Fecha: 2026-05-16

### Scope

Demo CLI canónica.

### Archivo tocado

- `pymia/cli/demo.py`

### Objetivo

Eliminar mojibake de salida en consola para que la demo canónica sea evidencia legible.

### Cambios

- Agregada configuración best-effort de `sys.stdout` a UTF-8 con `errors="replace"`.
- La configuración se aplica al inicio de `main()`.
- No se modificó el pipeline, los contratos ni el formatter clínico.

### Validación

```text
run_pymia_demo: PASS legible
pytest: 61 passed
forbidden terms: clean
audit_docs_index: OK
```

### Guardrails

```text
Sin jobs.
Sin workflows.
Sin orquestación nueva.
Sin authorization flow.
Sin factory/app/MCP legacy.
Sin runtime Hermes duplicado.
Hermes conversa, PymIA computa: preservado.
```

### Pendiente siguiente

Ciclo 3: fijar criterio de desempate clínico para hipótesis primarias con score empatado.

## CICLO 3 — PASS

Fecha: 2026-05-16

### Scope

Priorización determinística de hipótesis en admisión v1.

### Archivos tocados

- `pymia/pipeline/admission/v1/heuristics.py`
- `tests/pipeline/test_admission_pipeline_v1.py`

### Objetivo

Hacer explícito y testeable el desempate clínico cuando las hipótesis de rentabilidad tienen el mismo score.

### Cambios

- Documentado el orden clínico determinístico de `PROFIT_HYPOTHESES`.
- Reforzado test de variaciones de rentabilidad para exigir `Tensión de caja` como hipótesis primaria.
- No se agregaron capas externas ni cambios de frontera.

### Validación

```text
pytest: 61 passed
forbidden terms: clean
audit_docs_index: OK
run_pymia_demo: PASS legible
```

### Guardrails

```text
Sin jobs.
Sin workflows.
Sin orquestación nueva.
Sin authorization flow.
Sin factory/app/MCP legacy.
Sin runtime Hermes duplicado.
Hermes conversa, PymIA computa: preservado.
```

### Pendiente siguiente

Ciclo 4: evaluar frontera Hermes/Telegram/provider conversacional solo desde archivos presentes y tests existentes, sin implementar integración externa todavía.

## CICLO 4 — PASS

Fecha: 2026-05-16

### Scope

Frontera conversacional Hermes / Telegram / provider IA / BEM-OCR.

### Archivos leídos

- `pymia/hermes/adapter.py`
- `pymia/interfaces/conversational_port.py`
- `docs/arquitectura/orchestration-boundary.md`
- `docs/producto/capa-00-canal-entrada.md`

### Archivo creado

- `docs/hermes/boundary-integracion-conversacional.md`

### Objetivo

Definir el límite operativo para avanzar hacia demo conversacional sin contaminar el core PymIA.

### Hallazgos

- Ya existe `HermesAdapter` como frontera limpia entre Hermes externo y `ClinicalConversationalPort`.
- Ya existe `ClinicalConversationalPort` como única superficie pública para interfaces externas.
- No existen referencias físicas a DeepSeek en el repo.
- Telegram aparece como canal externo, no como runtime dentro de PymIA.
- BEM/OCR aparece como capacidad documental externa o posterior, no como decisor clínico del kernel.

### Decisión

PymIA no implementa bot de Telegram, provider LLM, ingesta documental pesada, OCR ni runtime Hermes.

La demo futura debe vivir fuera del core y llamar a:

```text
HermesAdapter.handle(HermesInput(...))
```

### Validación

```text
pytest: 61 passed
audit_docs_index: OK
forbidden terms: clean
run_pymia_demo: PASS legible
```

### Guardrails

```text
Sin jobs.
Sin workflows.
Sin orquestación nueva.
Sin authorization flow.
Sin factory/app/MCP legacy.
Sin runtime Hermes duplicado.
Hermes conversa, PymIA computa: preservado.
```

### Pendiente siguiente

Ciclo 5: endurecer tests de frontera para impedir imports de Telegram/provider/BEM dentro de `pymia/`.

## CICLO 5 — PASS

Fecha: 2026-05-16

### Scope

Endurecimiento de frontera MVP conversacional/documental.

### Archivo tocado

- `tests/architecture/test_forbidden_imports.py`

### Objetivo

Impedir contaminación del core `pymia/` con SDKs conversacionales, providers IA y runtimes documentales externos.

### Cambios

Se agregaron imports prohibidos para:

```text
telegram
telebot
aiogram
openai
anthropic
google.generativeai
groq
langchain
bem
ocr
```

HermesAdapter sigue siendo la frontera permitida.

### Validación

```text
pytest: 61 passed
forbidden terms: clean
audit_docs_index(PymIA): OK
run_pymia_demo(PymIA): PASS legible
```

### Guardrails

```text
Sin jobs.
Sin workflows.
Sin orquestación nueva.
Sin authorization flow.
Sin factory/app/MCP legacy.
Sin runtime Hermes duplicado.
Hermes conversa, PymIA computa: preservado.
```

### Resultado arquitectónico

PymIA queda listo para ser consumido por una demo externa Hermes/Telegram sin incorporar SDKs conversacionales ni providers IA dentro del kernel clínico.

### Pendiente siguiente

Ciclo 6: preparar contrato mínimo de integración externa Hermes ↔ Telegram ↔ PymIA sin incorporar runtime conversacional al repo.

## CICLO 6 — PASS

Fecha: 2026-05-16

### Scope

Contrato mínimo de integración externa Hermes ↔ Telegram ↔ PymIA.

### Archivos leídos

- `pymia/hermes/adapter.py`
- `pymia/interfaces/conversational_port.py`

### Archivo creado

- `docs/hermes/contrato-minimo-integracion-externa.md`

### Objetivo

Formalizar el boundary operativo mínimo para una demo externa Hermes/Telegram sin incorporar runtime conversacional al core PymIA.

### Resultado

Quedó documentado:

```text
Telegram externo
→ Hermes externo
→ provider IA externo (opcional)
→ HermesAdapter
→ ClinicalConversationalPort
→ kernel clínico PymIA
```

### Decisiones explícitas

- Telegram es solo canal.
- Providers IA externos pueden conversar pero no decidir verdad operacional.
- BEM/OCR viven fuera del kernel.
- El único boundary soportado es:

```text
HermesInput
→ HermesAdapter.handle()
→ HermesOutput
```

- PymIA no debe importar runtime Telegram/provider/BEM.

### Validación

```text
pytest: 61 passed
forbidden terms: clean
audit_docs_index(PymIA): OK
run_pymia_demo(PymIA): PASS legible
```

### Guardrails

```text
Sin jobs.
Sin workflows.
Sin orquestación nueva.
Sin authorization flow.
Sin factory/app/MCP legacy.
Sin runtime Hermes duplicado.
Hermes conversa, PymIA computa: preservado.
```

### Resultado arquitectónico

PymIA queda preparado para ser consumido por:

```text
Hermes runtime externo
Telegram externo
provider IA externo
```

sin contaminar el kernel clínico.

### Pendiente siguiente

Ciclo 7: preparar demo externa mínima Hermes/Telegram sobre SmartPyme sin mover runtime conversacional a PymIA.

## Norte operativo posterior — no implementado en este ciclo

Meta deseada por producto: demo conversacional con bot de Telegram, Hermes como capa conversacional, provider IA configurado explícitamente y capacidades de ingesta documental grande/OCR por frontera externa.

Restricción: esa meta no autoriza contaminar el core PymIA. Toda integración futura debe respetar la frontera: Hermes conversa; PymIA computa. PymIA no incorpora jobs, workflows, orquestación, authorization flow, runtime Hermes duplicado ni providers obligatorios en core.
