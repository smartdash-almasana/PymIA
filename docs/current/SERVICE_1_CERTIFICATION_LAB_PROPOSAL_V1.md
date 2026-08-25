# Servicio 1 — Certification Lab Proposal V1

**Fecha:** 2026-08-24 20:17 ART (UTC-03:00)  
**Estado:** `PROPOSAL_NOT_IMPLEMENTED`  
**Objetivo:** definir un sistema profesional de testing y certificación de Servicio 1 cuyo veredicto no dependa de ChatGPT, Codex ni de otra IA.

---

## Principio rector

> Ni ChatGPT ni Codex pueden declarar Servicio 1 aprobado. Sólo pueden producir código, tests, análisis y evidencia. El PASS final debe ser emitido por un harness reproducible, automático y auditable.

El objetivo es separar claramente responsabilidades:

- **Codex:** implementa y repara.
- **ChatGPT:** arquitectura, auditoría y análisis de defectos.
- **Test harness:** decide PASS/FAIL.
- **Corpus/oracles:** establecen la verdad esperada.
- **CI limpio:** ejecuta la certificación.
- **Humano:** autoriza release.

---

# 1. Capas de certificación propuestas

## G0 — Reproducibilidad

Demostrar que la certificación corre sobre un estado físico identificable y repetible:

- SHA/candidate exacto.
- versión de Python.
- sistema operativo.
- dependencias bloqueadas.
- configuración efectiva.
- corpus versionado.
- hashes de artefactos.

## G1 — Arquitectura

Bloqueo automático ante desviaciones estructurales:

- un Product Root.
- cuatro execution commands explícitos.
- un XLSX reader canónico.
- un semantic FSM.
- cero legacy callers productivos.
- cero Sheet1 fallback productivo.
- Web sin bypass de F7/F8/F9.
- D4→P8 provenance íntegro.
- F7 como única autoridad de materialización de joins.
- un math engine.
- clasificación declarativa.
- cero autoridad matemática/runtime del LLM.
- cero mutaciones post-build del canonical envelope.
- ResultRead sin recalculación.
- D7 evidence-only.
- registry drift = 0.

El `python -m pymia.architecture_guard` existente debe convertirse en gate obligatorio de release.

## G2 — Unit / Contract testing

Probar cada frontera aisladamente:

- D1–D7.
- SEM.
- owner confirmation.
- P7.
- P8.
- F7.
- F8.
- F9.
- F13.
- specialized workflows.
- tenant memory.
- result integrity.

## G3 — Property-based testing

Agregar pruebas generativas para invariantes de Servicio 1. Ejemplos:

- el orden de filas no cambia agregados.
- cambiar filename no cambia workbook identity.
- reordenar hojas no cambia identidad lógica cuando el contenido es equivalente.
- dos tenants nunca comparten memoria.
- una ambigüedad semántica nunca se autoconfirma.
- un join 1:N no autorizado nunca se materializa silenciosamente.
- output LLM inválido siempre termina fail-closed.
- sumar una fila modifica únicamente métricas dependientes de esa fila.

Tecnología sugerida: Hypothesis.

## G4 — Mutation testing

Romper deliberadamente el código para comprobar que los tests detectan defectos reales.

Prioridad:

- FormulaEngineService.
- P7.
- P8.
- F7.
- F8.
- classification.
- tenant scoping.
- owner confirmation.
- D4 relationship safety.
- F13 result integrity.

Ejemplos de mutaciones:

- `>` → `>=`.
- `+` → `-`.
- `True` → `False`.
- desactivar tenant check.
- permitir fanout.
- aceptar owner confirmation ausente.

Tecnología sugerida: mutmut u otra herramienta equivalente.

## G5 — Integration testing

Ejecutar juntas las fronteras arquitectónicas principales antes del full suite:

`CanonicalIngestionOutput → D1→D7 → SEM/owner → P7 → P8 → F7 → F8 → F9 → F13`

Debe incluir Product Root, commands, specialized paths, result read boundary y architecture guard.

## G6 — Corpus XLSX real

Convertir los XLSX reales en examen formal de certificación.

Corpus mínimo actual:

- cafetería.
- textil.
- distribuidora mayorista.
- fábrica industrial.
- consorcio.
- conciliación.
- multisheet.
- casos adversariales.

Cada XLSX debe tener oracle independiente y manifiesto versionado.

Estructura propuesta:

```text
certification/
  corpus/
    real/
    synthetic/
    adversarial/
  expected/
  manifests/
  reports/
```

Cada manifiesto debe contener como mínimo:

```text
artifact_sha256
scenario_id
expected_sheets
expected_tables
expected_semantic_ambiguities
expected_owner_questions
expected_computable_analyses
expected_blocked_analyses
expected_numeric_results
expected_failure_mode
```

El resultado esperado no puede ser inventado en runtime por una IA. Debe estar versionado previamente.

### Caso cafetería

La discrepancia histórica `602.106,15` vs `612.649,00` debe resolverse mediante un oracle independiente basado en filas y fórmulas, nunca por hardcode ni por aceptar como verdad la salida actual de PymIA.

## G7 — Corpus XLSX adversarial

Casos que deben fallar de forma controlada:

- columnas duplicadas.
- hojas ambiguas.
- tipos inconsistentes.
- referencias rotas.
- relaciones ambiguas.
- joins fanout.
- cardinalidad contradictoria.
- owner evidence incompatible.
- fórmulas incompletas.
- multi-region conflictivo.
- workbook con estructura engañosa.

El objetivo es comprobar fail-closed, no sólo éxito nominal.

## G8 — Testing LLM semántico

Separar dos suites.

### Suite determinística

Provider controlado para comprobar de forma reproducible:

`Excel → semantic proposal → validation → owner → canonical evidence`

### Suite con LLM real

Evaluar un corpus conocido de columnas/workbooks y verificar invariantes, no frases exactas:

- no inventa columnas.
- no calcula.
- no genera datos inexistentes.
- no autoriza runtime.
- no resuelve ambigüedad material sin owner.
- todas las refs existen.
- output cumple schema.

Esto permite cambiar de modelo sin cambiar la arquitectura.

## G9 — E2E de producto

Probar el flujo visible completo:

- upload XLSX.
- columnas detectadas.
- confirmación semántica.
- corrección semántica.
- resolución de relaciones.
- menú de análisis disponibles/bloqueados.
- ejecución.
- resultado.
- descarga.
- persistencia.
- “Mis análisis”.
- reentrada.
- aislamiento entre tenants.
- nuevo Excel.
- caso bloqueado.

Tecnología sugerida: Playwright.

Ante fallo conservar automáticamente:

- trace.
- screenshot.
- HTML.
- logs.
- request/response relevante.

## G10 — No funcional

Agregar gates para:

- tenant isolation.
- seguridad básica.
- concurrencia.
- recuperación de errores.
- tiempos de ejecución.
- memoria.
- integridad de persistencia.
- idempotencia.

---

# 2. CI independiente

La certificación debe correr en un entorno limpio, separado del worktree donde Codex modifica código.

Cadena propuesta:

```text
git checkout <candidate SHA>
↓
instalación limpia
↓
architecture guard
↓
unit/contracts
↓
property tests
↓
integration
↓
real XLSX corpus
↓
adversarial XLSX corpus
↓
LLM contract suite
↓
Playwright
↓
coverage
↓
mutation gate
↓
certification manifest
```

El proveedor puede ser GitHub Actions, GitLab CI o runner propio; lo importante es la reproducibilidad y separación del entorno de desarrollo.

---

# 3. Certificado de build

Cada ejecución completa debe producir un artefacto similar a:

```text
SERVICE_1_CERTIFICATION.json

candidate_sha: ...
timestamp: ...
python: ...
os: ...
corpus_version: ...
corpus_hash: ...

architecture: 16/16 PASS
unit: .../... PASS
integration: .../... PASS
property: ... examples PASS
mutation_score: ...%
real_xlsx: .../... PASS
adversarial_xlsx: .../... PASS
llm_contract: .../... PASS
playwright: .../... PASS
tenant_isolation: PASS
result_integrity: PASS

FAILED: 0
ERRORS: 0

VERDICT: PASS_READY_FOR_RELEASE_DECISION
```

Artefactos complementarios:

- JUnit XML.
- coverage XML/HTML.
- mutation report.
- architecture_guard.json.
- XLSX comparison report.
- Playwright traces/screenshots.
- dependency/environment manifest.

---

# 4. Calibración del propio laboratorio

Antes de confiar en la certificación, romper PymIA deliberadamente en ramas temporales y comprobar que los gates detectan cada sabotaje.

Sabotajes mínimos:

- habilitar Sheet1 fallback.
- romper tenant check.
- alterar SUM.
- permitir 1:N no autorizado.
- permitir al LLM autorizar cálculo.
- usar filename como workbook identity.
- eliminar owner confirmation.
- hacer que F13 recalcule.

Cada sabotaje debe activar un gate concreto.

Esto demuestra que el sistema de certificación no sólo puede quedar verde: también sabe detectar un Servicio 1 incorrecto.

---

# 5. Comandos objetivo

Propuesta de interfaz permanente:

```text
python -m pymia.architecture_guard
python -m pymia.service1_test_lab --fast
python -m pymia.service1_test_lab --complete
python -m pymia.service1_certify
```

`service1_certify` debe ser el único componente autorizado para emitir:

```text
PASS_READY_FOR_RELEASE_DECISION
```

---

# 6. Decisión arquitectónica propuesta

Crear un subsistema permanente llamado:

**PymIA Service 1 Certification Lab**

Su función es transformar el testing actual —hoy distribuido entre focales, full suite, corpus y auditorías— en una certificación reproducible, falsable, automatizada y auditable.

El laboratorio no reemplaza R13/R14 actuales. Los formaliza y los convierte en una infraestructura permanente para futuras modificaciones de Servicio 1.
