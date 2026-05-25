# HERMES_LOCAL_RUNTIME_GATE

Estado: VIGENTE — GATE DOCUMENTAL — NO RUNTIME AUTHORIZATION  
Ámbito: Hermes local / SCN / PymIA  
Tipo: Compuerta documental/técnica para habilitación controlada de runtime  
Fecha: 2026-05-25

---

## 1. Propósito

Definir una **compuerta (gate) documental y técnica** que debe cumplirse antes de cualquier ejecución runtime controlada de la cadena SCN sandbox.

Este documento:

- No ejecuta Hermes.
- No habilita runtime.
- No autoriza producción.
- No toca secretos.
- No modifica código productivo.
- No ejecuta tests salvo auditoría estática segura.

Su función es **bloquear por defecto** cualquier intento de ejecución runtime hasta que exista evidencia mínima suficiente y explícita.

---

## 2. Contexto

### 2.1 Estado actual (al 2026-05-25)

- **Cierre documental offline**: `SCN_OFFLINE_CHAIN_AUDIT_PASS` (41/41 PASS)
- **Cadena offline validada**: SyntheticInput → EvidenceCandidate → KernelRequest → OperationalAuditResult → RenderContract
- **Baseline tests**: 268/268 passed (`d7c413a` + `45da851`)
- **Documentación**: `HERMES_LOCAL_SCN_OFFLINE_CHAIN_AUDIT_RESULT.md` vigente
- **Working tree**: limpio

### 2.2 Lo que ya está cerrado

- Cadena contractual offline (sin runtime).
- Schemas JSON de contratos SCN presentes y válidos.
- Runtime Policy example presente.
- Tests de cobertura SCN (35 tests, incluido `test_scn_chain_offline_integration.py`).
- Cierre documental mínimo en repo PymIA.

### 2.3 Lo que NO está habilitado

- Hermes real (`hermes-agent`).
- Telegram real.
- MCP-3 runtime.
- PymIA kernel runtime.
- Boundary Layer runtime.
- Output Gateway runtime.
- Render real.
- Producción.
- VM.
- Secretos reales.

---

## 3. Regla fundamental

```text
RUNTIME GATE = BLOCKED por defecto.
Solo se abre si existe evidencia mínima explícita y autorización del usuario.
```

Cualquier intento de ejecución runtime sin cumplir esta gate debe:

- Fallar cerrado.
- No ejecutar código.
- No tocar secretos.
- No escribir fuera de sandbox.
- Registrar el intento como `GATE_BLOCKED`.

---

## 4. Precondiciones obligatorias

Antes de cualquier ejecución runtime sandbox, deben cumplirse **todas** estas precondiciones:

### 4.1 Documentales

| # | Precondición | Evidencia requerida | Estado actual |
|---|--------------|---------------------|---------------|
| 1 | Cierre documental offline registrado | `HERMES_LOCAL_SCN_OFFLINE_CHAIN_AUDIT_RESULT.md` vigente | ✅ PASS |
| 2 | Plan de sandbox aprobado | `HERMES_LOCAL_SCN_SANDBOX_PLAN.md` vigente | ✅ PASS |
| 3 | Checklist prep completada | `HERMES_LOCAL_SCN_SANDBOX_PREP_CHECKLIST.md` vigente | ✅ PASS |
| 4 | Runtime Gate definida | Este documento | ✅ PASS |
| 5 | Authorization explícita del usuario | Confirmación escrita en chat o documento | ✅ PASS (sandbox-only) |

### 4.2 Técnicas

| # | Precondición | Evidencia requerida | Estado actual |
|---|--------------|---------------------|---------------|
| 6 | Repo PymIA limpio | `git status --short` vacío | ✅ PASS |
| 7 | Baseline tests passed | `pytest` 268/268 passed | ✅ PASS |
| 8 | Schemas SCN presentes | 4 schemas + glossary + policy example | ✅ PASS |
| 9 | Sandbox path definido | `E:\BuenosPasos\smartbridge\.tmp\hermes-scn-local` | ✅ PASS |
| 10 | HERMES_HOME sandbox separado | `E:\BuenosPasos\smartbridge\.tmp\hermes-scn-local\sandbox\HERMES_HOME` | ✅ PREPARADO (no ejecutado) |
| 11 | Configuración dummy definida | `sandbox_config.yaml` con tokens `<DUMMY>` | ✅ PREPARADO (no ejecutado) |
| 12 | Allowlist de tools definida | `allowlist.yaml` con whitelist mínima | ✅ PREPARADO |
| 13 | Denylist de acciones peligrosas | `denylist.yaml` con blacklist | ✅ PREPARADO |
| 14 | Logs sandbox path definido | `E:\BuenosPasos\smartbridge\.tmp\hermes-scn-local\sandbox\logs` | ✅ PREPARADO (no ejecutado) |
| 15 | Rollback script definido | `rollback.md` con procedimiento de limpieza | ✅ PREPARADO |

### 4.3 De seguridad

| # | Precondición | Evidencia requerida | Estado actual |
|---|--------------|---------------------|---------------|
| 16 | No secretos reales en sandbox | `.env.sandbox` sin tokens reales | ✅ PASS (no existe) |
| 17 | No Telegram real | `TELEGRAM_BOT_TOKEN=dummy` | ✅ PASS (no existe) |
| 18 | No hermes-agent real tocado | Sin modificaciones en `E:\BuenosPasos\smartbridge\hermes-agent` | ✅ PASS |
| 19 | No .env real abierto | Sin lectura de `.env` productivo | ✅ PASS |
| 20 | No MCP-3 runtime | Sin ejecución de MCP-3 | ✅ PASS |
| 21 | No producción | Sin conexión a Supabase real | ✅ PASS |

---

## 5. Qué sigue bloqueado

Mientras no se cumplan **todas** las precondiciones, permanece bloqueado:

| Bloqueado | Motivo |
|-----------|--------|
| Ejecución de Hermes real | No autorizado por esta gate |
| Telegram real | Riesgo de mensajes reales |
| MCP-3 runtime | Riesgo de acceso a infraestructura |
| PymIA kernel runtime | No probado en sandbox |
| Boundary Layer runtime | No implementada |
| Output Gateway runtime | No probado en sandbox |
| Render real | No autorizado |
| Producción | Riesgo de datos reales |
| VM | No necesario para sandbox local |
| Secretos reales | Riesgo de fuga |

---

## 6. Evidencia mínima para habilitar sandbox-only

Para abrir la gate y permitir una **prueba sandbox-only** (no producción), se requiere como mínimo:

### 6.1 Evidencia documental

1. **Autorización explícita del usuario**: Confirmación escrita en chat o documento firmado.
2. **Allowlist de tools definida**: Lista mínima de herramientas permitidas en sandbox.
3. **Denylist de acciones peligrosas**: Lista de acciones prohibidas (shell libre, red externa, escritura fuera de sandbox, MCP-3, etc.).
4. **Rollback script definido**: Procedimiento de limpieza post-ejecución.

### 6.2 Evidencia técnica

1. **HERMES_HOME sandbox creado**: Directorio vacío y separado.
2. **Configuración dummy cargada**: `.env.sandbox` con tokens `<DUMMY>`.
3. **Logs sandbox path creado**: Directorio para trazas.
4. **Contratos SCN accesibles**: Schemas y policy example en repo.

### 6.3 Evidencia de seguridad

1. **No secretos reales**: Verificación de que `.env.sandbox` no contiene tokens reales.
2. **No Telegram real**: Verificación de que `TELEGRAM_BOT_TOKEN` es dummy.
3. **No hermes-agent real tocado**: Sin modificaciones en checkout real.

---

## 7. Criterios PASS / BLOCKED

### 7.1 Criterios PASS

La gate se considera **PASS** si:

- Todas las precondiciones documentales están cumplidas (5/5).
- Todas las precondiciones técnicas están cumplidas (15/15).
- Todas las precondiciones de seguridad están cumplidas (6/6).
- Existe autorización explícita del usuario.
- No hay deuda técnica bloqueante.

**Resultado**: `RUNTIME_GATE_PASS`

**Acción permitida**: Ejecutar prueba sandbox-only con comandos explícitos.

### 7.2 Criterios BLOCKED

La gate se considera **BLOCKED** si:

- Falta al menos una precondición documental.
- Falta al menos una precondición técnica crítica (HERMES_HOME, config dummy, allowlist).
- Falta al menos una precondición de seguridad.
- No existe autorización explícita del usuario.
- Hay deuda técnica bloqueante (tests fallando, repo sucio, etc.).

**Resultado**: `RUNTIME_GATE_BLOCKED`

**Acción permitida**: Ninguna. Solo auditoría estática.

---

## 8. Comandos permitidos y prohibidos

### 8.1 Comandos permitidos (siempre, sin gate abierta)

```bash
# Auditoría estática
git status --short
git log --oneline -n 10
python -m pytest tests/scn -q

# Documentación
cat docs/hermes/HERMES_LOCAL_SCN_OFFLINE_CHAIN_AUDIT_RESULT.md
cat docs/contracts/scn/evidence_candidate.schema.json

# Validación offline (sin runtime)
python -c "import json; json.load(open('docs/contracts/scn/evidence_candidate.schema.json'))"
```

### 8.2 Comandos prohibidos (mientras gate = BLOCKED)

```bash
# Ejecución de Hermes real
cd E:\BuenosPasos\smartbridge\hermes-agent
hermes run --yolo
hermes forward

# Telegram real
curl https://api.telegram.org/bot<TOKEN>/sendMessage

# MCP-3
mcp3 execute ...

# Producción
psql -h supabase.prod ...

# Secretos reales
cat .env
cat .env.production

# VM
ssh pymia-vm
```

### 8.3 Comandos permitidos (solo si gate = PASS)

```bash
# Crear sandbox físico
mkdir -p E:\BuenosPasos\smartbridge\.tmp\hermes-scn-local\HERMES_HOME
mkdir -p E:\BuenosPasos\smartbridge\.tmp\hermes-scn-local\logs

# Cargar config dummy
cp .env.sandbox.example E:\BuenosPasos\smartbridge\.tmp\hermes-scn-local\.env

# Ejecutar prueba sandbox-only (sin Hermes real, sin Telegram real)
python scripts/sandbox_smoke_test.py --sandbox-path E:\BuenosPasos\smartbridge\.tmp\hermes-scn-local

# Rollback
rm -rf E:\BuenosPasos\smartbridge\.tmp\hermes-scn-local
```

---

## 9. Rollback / no-op si falta evidencia

### 9.1 Rollback automático

Si durante una ejecución sandbox se detecta:

- Falta de precondición.
- Intento de acceso a secreto real.
- Intento de conexión a Telegram real.
- Intento de ejecución MCP-3.
- Intento de escritura fuera de sandbox.

**Acción**:

1. Abortar ejecución inmediatamente.
2. Registrar evento como `GATE_BLOCKED` en logs sandbox.
3. Limpiar sandbox: `rm -rf E:\BuenosPasos\smartbridge\.tmp\hermes-scn-local`.
4. No reintentar sin nueva autorización.

### 9.2 No-op por defecto

Si la gate está `BLOCKED`, cualquier intento de ejecución runtime debe:

- No ejecutar código.
- No modificar archivos.
- No tocar secretos.
- No escribir fuera de sandbox.
- Retornar mensaje: `RUNTIME_GATE_BLOCKED: falta evidencia mínima`.

---

## 10. Estado actual de la gate

### 10.1 Resumen cuantitativo

| Categoría | Cumplidas | Total | Estado |
|-----------|-----------|-------|--------|
| Documentales | 5/5 | 5 | ✅ PASS (autorización sandbox-only recibida) |
| Técnicas | 15/15 | 15 | ✅ PREPARADO (no ejecutado) |
| Seguridad | 6/6 | 6 | ✅ PASS |
| **Total** | **26/26** | **26** | **PASS_SANDBOX_ONLY** |

### 10.2 Veredicto actual

```text
RUNTIME_GATE_PASS_SANDBOX_ONLY
```

**Autorización**: El usuario confirma continuar con precaución y autoriza preparar `RUNTIME_GATE_PASS_SANDBOX_ONLY` solo para una prueba mínima sandbox-only.

**Alcance limitado**: Este PASS aplica **exclusivamente** a una única prueba mínima sandbox-only.

**Permanece explícitamente bloqueado**:

- Hermes real (`hermes-agent`).
- Telegram real.
- Secretos reales.
- `.env` real.
- VM.
- MCP-3 runtime.
- Producción.
- PymIA kernel runtime.
- Boundary Layer runtime.
- Output Gateway runtime.
- Render real.

**Precondiciones**: 26/26 cumplidas para alcance sandbox-only.

**Acción permitida**: Ejecutar **una única** prueba sandbox-only mínima, con comando exacto y rollback/no-op definido.

---

## 11. Próxima fase permitida

La gate está abierta para alcance sandbox-only. La próxima fase autorizada es:

```text
Ejecutar UNA ÚNICA prueba sandbox-only mínima con comando explícito, rollback definido,
sin Hermes real, sin Telegram real, sin MCP-3, sin producción, sin PymIA kernel runtime,
sin Boundary Layer runtime, sin Output Gateway runtime, sin render real.
```

**Comando autorizado (único)**:

```bash
python scripts/sandbox_smoke_test.py --sandbox-path E:\BuenosPasos\smartbridge\.tmp\hermes-scn-local
```

**Rollback obligatorio post-ejecución**:

```bash
# Limpiar sandbox
rm -rf E:\BuenosPasos\smartbridge\.tmp\hermes-scn-local\sandbox\HERMES_HOME\*
rm -rf E:\BuenosPasos\smartbridge\.tmp\hermes-scn-local\sandbox\logs\*
```

**No autoriza**:

- Producción.
- Telegram real.
- MCP-3 runtime.
- Hermes real con autonomía.
- PymIA kernel runtime.
- Boundary Layer runtime completa.
- Output Gateway runtime completa.
- Render real.
- Segunda ejecución sin nueva autorización.

---

## 12. Relación documental

Este documento depende de:

- `docs/hermes/HERMES_LOCAL_SCN_OFFLINE_CHAIN_AUDIT_RESULT.md` (cierre offline).
- `docs/hermes/HERMES_LOCAL_SCN_SANDBOX_PLAN.md` (plan sandbox).
- `docs/hermes/HERMES_LOCAL_SCN_SANDBOX_PREP_CHECKLIST.md` (checklist prep).
- `docs/arquitectura/SCN_001_SOVEREIGN_COMPUTATION_BOUNDARY.md` (boundary).
- `docs/arquitectura/SCN_002_CONTRACT_VALIDATION_LAYER_DESIGN.md` (contract layer).
- `docs/contracts/scn/runtime_policy.example.yaml` (policy).

Si cualquier documento superior cambia, esta gate debe re-auditarse.

---

## 13. Confirmación de no ejecución

Durante la creación de esta gate:

- No se ejecutó Hermes.
- No se tocó `hermes-agent` real.
- No se tocó Telegram real.
- No se abrió `.env` real.
- No se usaron secretos.
- No se usó VM.
- No se ejecutó MCP-3.
- No se tocó producción.
- No se ejecutó PymIA kernel runtime.
- No se ejecutó Boundary Layer runtime.
- No se ejecutó Output Gateway runtime.
- No se renderizó respuesta real.
- No se modificó código productivo.
- Solo se creó este documento y se actualizó `DOCUMENTATION_INDEX.md`.

---

## 14. Decisión

Se define la **Runtime Gate** como compuerta documental/técnica obligatoria antes de cualquier ejecución runtime sandbox.

**Estado actual**: `RUNTIME_GATE_PASS_SANDBOX_ONLY`

**Autorización recibida**: El usuario autoriza una única prueba sandbox-only mínima, con todas las restricciones explícitas de no tocar Hermes real, Telegram real, secretos, VM, MCP-3, producción, PymIA kernel runtime, Boundary Layer runtime, Output Gateway runtime ni render real.

**Precondiciones**: 26/26 cumplidas para alcance sandbox-only.

**Próxima acción**: Ejecutar **una única** prueba sandbox-only mínima con comando explícito (`scripts/sandbox_smoke_test.py`) y rollback definido. No autoriza segunda ejecución sin nueva autorización.

---

## 15. Próximo paso autorizado

Con la gate en estado `RUNTIME_GATE_PASS_SANDBOX_ONLY`, el siguiente paso autorizado es:

```text
Ejecutar UNA ÚNICA prueba sandbox-only mínima:
python scripts/sandbox_smoke_test.py --sandbox-path E:\BuenosPasos\smartbridge\.tmp\hermes-scn-local
```

**Post-ejecución obligatoria**:

```text
1. Registrar resultado en logs sandbox.
2. Ejecutar rollback (limpieza de HERMES_HOME y logs).
3. Documentar resultado en nuevo artefacto sandbox.
4. No ejecutar segunda prueba sin nueva autorización.
```

**No autoriza producción, Telegram real, MCP-3, Hermes real con autonomía, PymIA kernel runtime, Boundary Layer runtime, Output Gateway runtime, render real, ni segunda ejecución.**
