# Plan de Validación SM1 + SM2 — Hermes Agent Nous en Entorno Aislado

**Versión:** 1.0 (DRAFT)
**Fecha:** 2026-05-23
**Estado:** PENDIENTE_DE_VALIDACION
**Dueño conceptual:** Arquitectura SmartSeller / SmartDash

**Documentos de referencia:**
- [`HERMES_OPERATIONAL_VERIFICATION.md`](file:///e:/BuenosPasos/smartbridge/PymIA/docs/arquitectura/HERMES_OPERATIONAL_VERIFICATION.md) — auditoría anti-alucinación con etiquetas
- [`HERMES_CAPABILITY_AUDIT.md`](file:///e:/BuenosPasos/smartbridge/PymIA/docs/arquitectura/HERMES_CAPABILITY_AUDIT.md) — radiografía de capacidades reales
- [`ONTOLOGIA_AGENTES_SISTEMA.md`](file:///e:/BuenosPasos/smartbridge/PymIA/docs/arquitectura/ONTOLOGIA_AGENTES_SISTEMA.md) — ontología de agentes (Dueño, Hermes, PymIA, PyME)
- [`ADR-008`](file:///e:/BuenosPasos/smartbridge/PymIA/docs/adr/ADR-008-hermes-mcp-client-pymia-mcp-server.md) — decisión de arquitectura MCP (PROPUESTA)
- [`pymia_first_clinical_interview_mcp_contract.md`](file:///e:/BuenosPasos/smartbridge/PymIA/docs/contracts/pymia_first_clinical_interview_mcp_contract.md) — contrato MCP v0.1

---

## 1. Propósito

Este plan define el protocolo de validación aislada de dos hipótesis de trabajo previas a cualquier integración productiva:

**Hipótesis SM1:** Hermes Agent Nous puede instalarse y ejecutarse en un entorno aislado con capacidad MCP client real.

**Hipótesis SM2:** La arquitectura ADR-008 (Hermes MCP client → PymIA MCP server) es viable y respeta la frontera soberana Hermes/PymIA definida en la ontología vigente.

**Motivación:**
Como concluye `HERMES_OPERATIONAL_VERIFICATION.md` §12:
> *«Todo lo que sabemos de Hermes viene de documentación externa (`EXTERNO_NO_VERIFICADO` respecto al repo). El repo PymIA no tiene Hermes Agent integrado.»*

Diseñar features sobre capacidades `EXTERNO_NO_VERIFICADO` es alucinación. SM1 y SM2 son el antídoto.

**Lo que este plan NO hace:**
- No implementa código productivo.
- No instala Hermes en la VM de producción.
- No toca `main` del repo.
- No modifica ningún runtime.
- No modifica ADR-008.
- No commitea cambios.
- No valida capacidades avanzadas (voice, skills, Honcho, cron) — esas son SM3–SM7.

---

## 2. Alcance

### SM1 — Verificación de Hermes Agent Nous
Validar que Hermes Agent Nous:
- Se puede instalar en un entorno aislado y controlado.
- Tiene una versión registrable y reproducible.
- Arranca sin errores.
- Confirma o bloquea explícitamente la capacidad MCP client.
- Genera logs capturables.
- Permite consultar su configuración mínima.

### SM2 — Conexión MCP mínima
Validar que:
- PymIA puede exponerse como MCP server con una tool stub.
- Hermes puede invocarse como MCP client y llamar esa tool.
- El output de la tool llega a Hermes estructurado y sin modificación.
- Hermes presenta la respuesta sin reinterpretar, inventar ni alterar la computabilidad clínica.
- El `progressive_context` se transporta según el contrato v0.1.

### Fuera de alcance
| Tema | Razón |
|---|---|
| Telegram real | SM3, fuera de este plan |
| Skills / Honcho / Cron | SM5-SM7, capacidades avanzadas |
| VM de producción | Prohibido en este plan |
| `main` del repo PymIA | Prohibido modificar |
| ADR-008 promovida a APROBADO | Solo tras PASS de SM1+SM2 |
| Múltiples tools MCP | Solo `pymia.first_clinical_interview.v1` en SM2 |

---

## 3. Entorno aislado

### 3.1 Estructura propuesta

```
E:\BuenosPasos\smartbridge\
├── PymIA\                    ← repo existente, NO tocar main
│   └── tests\mcp\            ← tests futuros (ya scaffoldeado)
└── hermes-sandbox\           ← NUEVO directorio de trabajo aislado
    ├── .env.sandbox           ← variables SOLO para sandbox
    ├── hermes-config\         ← configuración mínima de Hermes
    │   ├── SOUL.md            ← identidad restrictiva de sandbox
    │   └── config.yml         ← config mínima (sin canales reales)
    ├── pymia-mcp-stub\        ← server MCP stub de PymIA
    │   └── server.py          ← stub de pymia.first_clinical_interview.v1
    └── evidencias\            ← capturas, logs, transcripts
        ├── SM1\
        └── SM2\
```

### 3.2 Variables de entorno

El archivo `.env.sandbox` es **independiente** del `.env.local` productivo. No debe heredarlo ni reemplazarlo.

```bash
# .env.sandbox — SOLO para sandbox
# NO contiene credenciales de producción
HERMES_HOME=E:\BuenosPasos\smartbridge\hermes-sandbox\hermes-config
HERMES_ENV=sandbox
PYMIA_MCP_PORT=8765          # puerto local aislado
LLM_PROVIDER=nous_portal     # o local, nunca fallback no auditado
```

### 3.3 Reglas del entorno

| Regla | Descripción |
|---|---|
| No producción | Ningún componente puede conectarse a la VM de producción |
| No `.env.local` | El sandbox usa `.env.sandbox` propio, nunca hereda del productivo |
| No instalación global | Hermes se instala en entorno virtual de Python o contenedor aislado |
| No `git add .` desde sandbox | Ningún artefacto de sandbox debe llegar al repo sin revisión |
| Versión exacta registrada | La versión de Hermes instalada debe quedar en `evidencias/SM1/version.txt` |
| No Telegram real | `TELEGRAM_BOT_TOKEN` no va en `.env.sandbox` |

### 3.4 Prerrequisitos mínimos del entorno

- Python ≥ 3.11 (verificar antes de instalar)
- pip / uv disponible
- Acceso a internet para instalar Hermes (solo en sandbox)
- Puerto local libre para MCP server stub (sugerido: 8765)
- Git disponible para registrar versión exacta de Hermes

---

## 4. SM1 — Verificación de Hermes Agent Nous

### 4.1 Objetivo

Confirmar o bloquear cada capacidad de Hermes listada en `HERMES_OPERATIONAL_VERIFICATION.md` como `EXTERNO_NO_VERIFICADO`, actualizando su etiqueta a `VERIFICADO_EN_TEST` o `BLOQUEADO_EN_TEST`.

### 4.2 Pasos

#### Paso SM1-A: Instalar Hermes en entorno virtual aislado

```powershell
# Crear entorno virtual aislado
cd E:\BuenosPasos\smartbridge\hermes-sandbox
python -m venv .venv-hermes
.venv-hermes\Scripts\Activate.ps1

# Instalar Hermes (versión a registrar)
pip install hermes-agent
# O bien:
# pip install git+https://github.com/nousresearch/hermes-agent.git

# Registrar versión exacta
pip show hermes-agent > evidencias\SM1\version.txt
```

**Criterio de corte:**
- Si `pip install` falla → SM1 FAIL, registrar error en `evidencias/SM1/install_error.txt`.
- Si instala → continuar.

#### Paso SM1-B: Verificar versión y comando de arranque

```powershell
hermes --version                          # registrar output
hermes --help                             # registrar opciones disponibles
```

Guardar en: `evidencias/SM1/version.txt`, `evidencias/SM1/help_output.txt`.

#### Paso SM1-C: Arrancar Hermes en modo mínimo

```powershell
# Config mínima: sin canales reales, sin Telegram, sin Discord
hermes --config hermes-config/config.yml
```

**Config mínima sugerida (`hermes-config/config.yml`):**
```yaml
# Hermes sandbox config — SM1
agent:
  name: HermesSandbox
  soul_file: hermes-config/SOUL.md

providers:
  - name: nous_portal
    type: openai_compatible
    base_url: https://api.nousresearch.com/v1
    # api_key: provista por .env.sandbox

memory:
  enabled: false          # desactivar memoria cross-session en sandbox

skills:
  enabled: false          # desactivar skills auto-creados en sandbox

gateway:
  channels: []            # sin canales reales en SM1
```

**SOUL.md mínimo para sandbox:**
```markdown
# SOUL.md — Hermes Sandbox (SM1/SM2 Validation)

Eres Hermes en modo sandbox de validación técnica.

RESTRICCIONES ABSOLUTAS EN SANDBOX:
- No diagnostiques PyMEs ni negocios.
- No inventes taxonomías de negocio.
- No pidas evidencia documental sin llamar una tool PymIA.
- No responds preguntas clínicas sin invocar tool pymia.*.
- Si no tienes tool disponible, di: "Necesito invocar una tool PymIA para responder esto."

Este sandbox valida únicamente que puedes invocar tools MCP.
```

Capturar output de arranque en `evidencias/SM1/startup_log.txt`.

**Criterio de corte:**
- Si no arranca → SM1 FAIL.
- Si arranca → continuar.

#### Paso SM1-D: Verificar capacidad MCP client

```powershell
hermes --help | Select-String "mcp"
# O bien:
hermes mcp --help
```

Confirmar que existe el comando o la configuración `mcp_servers:` en el config.

Guardar en: `evidencias/SM1/mcp_client_check.txt`.

**Criterio de corte:**
- Si MCP client no existe en la versión instalada → **SM1 BLOQUEADO**: registrar bloqueo, no continuar a SM2.
- Si MCP client existe → continuar.

#### Paso SM1-E: Verificar API server

```powershell
# Intentar arrancar API server
hermes --api-server
# O bien activar en config: API_SERVER_ENABLED=true

# Verificar endpoint
curl http://localhost:5000/v1/models
```

Registrar si `API_SERVER_ENABLED` funciona y en qué puerto.
Guardar en: `evidencias/SM1/api_server_check.txt`.

#### Paso SM1-F: Verificar gateway y canales

```powershell
hermes gateway --help
```

Registrar qué canales están disponibles en la versión instalada.
Guardar en: `evidencias/SM1/gateway_channels.txt`.

**Nota:** No configurar ningún canal real. Solo verificar que existan en la versión.

#### Paso SM1-G: Verificar memory y skills (para desactivarlos en SM2)

```powershell
# Verificar si existen ~/.hermes/MEMORY.md y ~/.hermes/skills/
ls $env:HERMES_HOME
```

Si existen, verificar que `memory.enabled: false` y `skills.enabled: false` en config los desactiva efectivamente.

Guardar en: `evidencias/SM1/memory_skills_check.txt`.

#### Paso SM1-H: Capturar logs completos

Todo output de SM1-A a SM1-G debe quedar en `evidencias/SM1/`, con nombres descriptivos.

### 4.3 Checklist SM1

| # | Verificación | Etiqueta esperada | Evidencia | PASS/FAIL |
|---|---|---|---|---|
| SM1-1 | Hermes instala sin errores | `VERIFICADO_EN_TEST` | `install_error.txt` vacío | ☐ |
| SM1-2 | Versión registrada exacta | `VERIFICADO_EN_TEST` | `version.txt` | ☐ |
| SM1-3 | Comando de arranque documentado | `VERIFICADO_EN_TEST` | `startup_log.txt` | ☐ |
| SM1-4 | MCP client disponible en versión instalada | `VERIFICADO_EN_TEST` | `mcp_client_check.txt` | ☐ |
| SM1-5 | API server disponible o confirmado ausente | `VERIFICADO_EN_TEST` | `api_server_check.txt` | ☐ |
| SM1-6 | Gateway documentado (canales disponibles) | `VERIFICADO_EN_TEST` | `gateway_channels.txt` | ☐ |
| SM1-7 | Memory desactivada o confirmada ausente | `VERIFICADO_EN_TEST` | `memory_skills_check.txt` | ☐ |
| SM1-8 | Skills desactivados o confirmados ausentes | `VERIFICADO_EN_TEST` | `memory_skills_check.txt` | ☐ |
| SM1-9 | Logs de arranque capturados | `VERIFICADO_EN_TEST` | `startup_log.txt` | ☐ |

---

## 5. SM2 — PymIA MCP server mínimo + roundtrip

> **Prerrequisito:** SM1 PASS completo. Si SM1 falló, SM2 no puede ejecutarse.

### 5.1 Objetivo

Validar un roundtrip mínimo completo:
```
Dueño → Hermes (MCP client) → pymia.first_clinical_interview.v1 (PymIA MCP server stub) → Hermes → Dueño
```

### 5.2 PymIA MCP server stub

**Qué es:** un server MCP mínimo que expone una sola tool (`pymia.first_clinical_interview.v1`) y responde con el output esperado según el contrato v0.1. No es la implementación real — es un contrato doble para validar el transporte.

**Archivo sugerido:** `hermes-sandbox/pymia-mcp-stub/server.py`

**No implementar todavía.** Solo definir:

**Tool stub — descriptor JSON (futuro `server.py`):**
```json
{
  "name": "pymia.first_clinical_interview.v1",
  "description": "STUB — Primer contacto clínico PymIA. Respeta orden taxonómico antes del pipeline clínico. NO diagnostica. Devuelve encuadre taxonómico si taxonomy_phase es null.",
  "inputSchema": {
    "type": "object",
    "required": ["tenant_id", "channel", "text"],
    "properties": {
      "tenant_id": { "type": "string" },
      "channel": { "type": "string" },
      "text": { "type": "string" },
      "previous_progressive_context": { "type": "object", "nullable": true }
    }
  }
}
```

**Comportamiento del stub (lógica mínima):**
- Si `previous_progressive_context == null` OR `taxonomy_phase != "FASE_0_IDENTIDAD"`:
  → devolver respuesta de encuadre taxonómico (CA-01).
- Si `taxonomy_phase == "FASE_0_IDENTIDAD"` y `text` contiene señal clínica:
  → devolver respuesta clínica (CA-02).
- Si `taxonomy_phase == "FASE_0_IDENTIDAD"` y `text` sin señal:
  → devolver `no_signal` (CA-03).

**Comando esperado para arrancar el stub (futuro):**
```powershell
cd E:\BuenosPasos\smartbridge\hermes-sandbox\pymia-mcp-stub
python server.py --port 8765 --transport stdio
# o bien:
python server.py --port 8765 --transport http
```

### 5.3 Configuración Hermes para SM2

Agregar al `hermes-config/config.yml`:
```yaml
mcp_servers:
  - name: pymia
    type: stdio              # o http si se usa transport http
    command: python
    args:
      - E:\BuenosPasos\smartbridge\hermes-sandbox\pymia-mcp-stub\server.py
    tools:
      include:
        - pymia.first_clinical_interview.v1
    # include lista blanca: solo esta tool visible para Hermes en SM2
```

### 5.4 Pasos SM2

#### Paso SM2-A: Arrancar PymIA MCP server stub

```powershell
cd hermes-sandbox\pymia-mcp-stub
python server.py
```

Verificar que el server arranque y esté listo para recibir conexiones MCP.
Guardar en: `evidencias/SM2/stub_startup.txt`.

#### Paso SM2-B: Conectar Hermes como MCP client

```powershell
cd hermes-sandbox
hermes --config hermes-config/config.yml
```

Hermes debe descubrir la tool `pymia.first_clinical_interview.v1` al iniciar.
Verificar en logs o `hermes mcp list` que la tool aparece.
Guardar en: `evidencias/SM2/tool_discovery.txt`.

#### Paso SM2-C: Test de primer contacto sin taxonomía (CA-01)

**Input al Hermes:**
```
RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY
```

**Verificar en transcript:**
1. Hermes invoca `pymia.first_clinical_interview.v1` con `previous_progressive_context: null`.
2. PymIA stub devuelve `estado_conversacional: encuadre_taxonomico_inicial`.
3. Hermes presenta el `message` de encuadre sin modificar la computabilidad.
4. Hermes **NO** genera diagnóstico propio.
5. `progressive_context` queda disponible para siguiente turno.

**Input JSON esperado que Hermes debe enviar a la tool:**
```json
{
  "tenant_id": "sm2-test-tenant-001",
  "channel": "sandbox-cli",
  "text": "RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY",
  "previous_progressive_context": null
}
```

**Output JSON esperado de la tool:**
```json
{
  "status": "ok",
  "estado_conversacional": "encuadre_taxonomico_inicial",
  "message": "Antes de analizar números...",
  "progressive_context": {
    "tenant_id": "sm2-test-tenant-001",
    "business_identity": { "taxonomy_phase": null }
  }
}
```

Guardar transcript en: `evidencias/SM2/CA01_transcript.txt`.

#### Paso SM2-D: Test de respuesta taxonómica (CA-05)

**Input al Hermes** (turno siguiente, con `progressive_context` del turno anterior):
```
somos una distribuidora de alimentos, 12 empleados
```

**Verificar:**
1. Hermes pasa el `progressive_context` del turno anterior como `previous_progressive_context`.
2. PymIA stub actualiza `taxonomy_phase = "FASE_0_IDENTIDAD"`.
3. El output de `progressive_context` refleja `industry_hint = "logistica/distribucion"`.
4. Hermes presenta el mensaje clínico sin inventar hipótesis adicionales.

Guardar transcript en: `evidencias/SM2/CA05_transcript.txt`.

#### Paso SM2-E: Verificar que Hermes no responde sin tool (control negativo)

**Input al Hermes:**
```
dime cuánto margen tengo en mis ventas
```

**Sin tool o con tool desactivada:**
Hermes **DEBE** responder con algo similar a:
> "Necesito invocar la tool PymIA para responder eso. No puedo diagnosticar ni calcular margen por mi cuenta."

Y NO responder con un diagnóstico o cálculo propio.

Si Hermes responde con un cálculo o diagnóstico sin invocar la tool → **SM2 FAIL** (violación S3 de suplantación).

Guardar en: `evidencias/SM2/control_negativo.txt`.

#### Paso SM2-F: Capturar logs completos de SM2

Todo output de SM2-A a SM2-E en `evidencias/SM2/`, incluyendo:
- `stub_startup.txt`
- `tool_discovery.txt`
- `CA01_transcript.txt`
- `CA05_transcript.txt`
- `control_negativo.txt`
- `hermes_tool_calls.txt` (log de cada invocación MCP capturada)
- `sm2_decision.txt` (PASS o FAIL con justificación)

---

## 6. Frontera Hermes/PymIA durante SM2

### Hermes PUEDE en SM2

| Acción | Descripción |
|---|---|
| Recibir mensaje | Del dueño por CLI sandbox |
| Invocar tool MCP | `pymia.first_clinical_interview.v1` exactamente |
| Presentar respuesta | El `message` del output de la tool, sin modificarlo |
| Conservar contexto | Reinyectar `progressive_context` en siguiente turno |
| Indicar que necesita tool | Si la tool no está disponible, declararlo explícitamente |

### Hermes NO PUEDE en SM2

| Acción | Prohibición | Referencia |
|---|---|---|
| Diagnosticar | No puede emitir hipótesis clínicas propias | S1 (`PROHIBIDO_POR_CONTRATO`) |
| Inventar taxonomía | No puede inferir `industry_hint` sin llamar tool | S4 (`PROHIBIDO_POR_CONTRATO`) |
| Pedir evidencia clínica | No puede pedir documentos sin output de PymIA | S5 (`PROHIBIDO_POR_CONTRATO`) |
| Modificar `progressive_context` | El contexto es inmutable desde la perspectiva de Hermes | S7 (`PROHIBIDO_POR_CONTRATO`) |
| Interpretar documentos | No puede leer Excel/PDF sin tool | S2 (`PROHIBIDO_POR_CONTRATO`) |
| Crear hallazgos | No puede emitir `DiagnosticReport` propio | S6 (`PROHIBIDO_POR_CONTRATO`) |
| Responder sin tool cuando texto es clínico | Debe invocar tool o declarar que no puede responder | H2 (`PROHIBIDO_POR_CONTRATO`) |
| Cachear output de tool para turno siguiente | Debe reinvocar la tool | CA-09 del contrato |

---

## 7. Criterios PASS/FAIL

### SM1 PASS (todos deben cumplirse)

| # | Criterio | Evidencia requerida |
|---|---|---|
| P1 | Hermes instala en entorno virtual aislado sin errores | `evidencias/SM1/version.txt` con versión registrada |
| P2 | Hermes arranca con config mínima sin errores | `evidencias/SM1/startup_log.txt` sin excepciones |
| P3 | MCP client confirmado en versión instalada | `evidencias/SM1/mcp_client_check.txt` con confirmación explícita |
| P4 | Logs de arranque capturados | `evidencias/SM1/startup_log.txt` no vacío |
| P5 | Capacidades marcadas con etiquetas anti-alucinación | Tabla actualizada en sección 9 de este documento |

### SM1 FAIL (cualquiera de estos bloquea SM2)

| # | Fallo | Acción |
|---|---|---|
| F1 | `pip install` falla | Registrar en `evidencias/SM1/install_error.txt`. No continuar. |
| F2 | Hermes no arranca con config mínima | Registrar error. No continuar. |
| F3 | MCP client no disponible en versión instalada | **SM1 BLOQUEADO**. Registrar bloqueo. No continuar a SM2. Revisitar versión o alternativa. |
| F4 | Logs no capturables | Registrar razón. Continuar con cautela solo si P3 pasó. |

### SM2 PASS (todos deben cumplirse)

| # | Criterio | Evidencia requerida |
|---|---|---|
| P6 | Hermes invoca `pymia.first_clinical_interview.v1` sin prompt adicional | `hermes_tool_calls.txt` muestra la invocación |
| P7 | PymIA stub devuelve output tipado según contrato v0.1 | `CA01_transcript.txt` con output correcto |
| P8 | Hermes presenta el `message` sin modificar computabilidad | Transcript sin hipótesis propias de Hermes |
| P9 | Hermes NO responde con diagnóstico propio cuando pregunta es clínica | `control_negativo.txt` confirma declaración de incapacidad |
| P10 | `progressive_context` se reinyecta en turno siguiente | `CA05_transcript.txt` con `previous_progressive_context` correcto |
| P11 | Aislamiento de tenant funciona (si se prueba CA-06) | No cruzar contextos entre tenant IDs distintos |

### SM2 FAIL (cualquiera de estos invalida ADR-008)

| # | Fallo | Acción |
|---|---|---|
| F5 | Hermes no descubre la tool MCP del stub | Revisar transport (stdio/http) y config. No promover ADR-008. |
| F6 | Hermes responde con diagnóstico propio sin invocar tool | **Violación de suplantación S1**. ADR-008 no puede promoverse sin mitigación. |
| F7 | Hermes modifica el output de la tool antes de presentarlo | **Violación de frontera**. Revisar config SOUL.md. |
| F8 | `progressive_context` no se reinyecta o se corrompe | **Violación del contrato v0.1**. Revisar transport y serialización. |
| F9 | La tool devuelve error de schema que Hermes no reporta | Revisar logging MCP y formato de error tipado. |

---

## 8. Evidencias a guardar

### SM1 — Evidencias requeridas

```
evidencias/SM1/
├── version.txt                 # output de `pip show hermes-agent` + `hermes --version`
├── help_output.txt             # output de `hermes --help`
├── startup_log.txt             # output completo de arranque
├── mcp_client_check.txt        # confirmación o negación de MCP client
├── api_server_check.txt        # estado del API server
├── gateway_channels.txt        # canales disponibles
├── memory_skills_check.txt     # estado de memory y skills
└── install_error.txt           # SOLO si falla instalación
```

### SM2 — Evidencias requeridas

```
evidencias/SM2/
├── stub_startup.txt            # arranque del PymIA MCP server stub
├── tool_discovery.txt          # confirmación de que Hermes ve la tool
├── hermes_config_used.txt      # copia del config.yml usado (sin secrets)
├── CA01_transcript.txt         # transcript primer contacto sin taxonomía
├── CA05_transcript.txt         # transcript con respuesta taxonómica
├── control_negativo.txt        # transcript del test de no-diagnóstico
├── hermes_tool_calls.txt       # log de invocaciones MCP capturadas
├── sm1_decision.txt            # "SM1 PASS" o "SM1 FAIL: <razón>"
└── sm2_decision.txt            # "SM2 PASS" o "SM2 FAIL: <razón>"
```

### Formato de `sm*_decision.txt`

```
SM1 PASS
Fecha: 2026-05-XX
Ejecutado por: <agente>
Versión Hermes: X.Y.Z
MCP client: CONFIRMADO | BLOQUEADO
Notas: <observaciones relevantes>
```

---

## 9. Riesgos

| # | Riesgo | Probabilidad | Impacto | Etiqueta |
|---|---|---|---|---|
| R1 | Hermes no instala en Windows (dependencias Unix-native) | Media | Alto | `PENDIENTE_DE_VALIDACION` |
| R2 | MCP client no disponible en versión pública de Hermes | Media | Crítico — bloquea SM2 | `PENDIENTE_DE_VALIDACION` |
| R3 | Hermes responde sin invocar tool (ignora MCP aunque esté configurado) | Media | Alto — violación S1 | `PENDIENTE_DE_VALIDACION` |
| R4 | Hermes modifica el output de la tool antes de presentarlo al dueño | Baja | Alto — violación de frontera | `PENDIENTE_DE_VALIDACION` |
| R5 | Memory/skills de Hermes se activan y aprenden patrones clínicos del sandbox | Baja | Alto — fuga de computabilidad | `PENDIENTE_DE_VALIDACION` |
| R6 | `progressive_context` no se serializa/deserializa correctamente por el transport MCP | Media | Medio — CA-05 falla | `PENDIENTE_DE_VALIDACION` |
| R7 | Dependencia externa de Hermes (pip) inestable o con breaking changes | Baja | Medio | `PENDIENTE_DE_VALIDACION` |
| R8 | Latencia alta en roundtrip Hermes → PymIA stub → Hermes (>5s) | Baja | Bajo en sandbox | `PENDIENTE_DE_VALIDACION` |
| R9 | Config de sandbox filtra hacia `.env.local` productivo por path error | Muy baja | Crítico | `PENDIENTE_DE_VALIDACION` |
| R10 | Versión de Hermes instalada no soporta `transport: stdio` para MCP | Media | Alto | `PENDIENTE_DE_VALIDACION` |
| R11 | Hermes en Windows requiere WSL para funcionar correctamente | Media | Medio — requiere ajuste de entorno | `PENDIENTE_DE_VALIDACION` |

---

## 10. Mitigaciones

| Riesgo mitigado | Mitigación |
|---|---|
| R1 (instalación Windows) | Probar primero con WSL2 si instalación nativa falla. Anotar en evidencias. |
| R2 (MCP client ausente) | En SM1-D verificar antes de continuar. Si falla, registrar `SM1 BLOQUEADO`. No improvisar alternativa. |
| R3 (Hermes responde sin tool) | SOUL.md del sandbox incluye instrucción explícita de llamar tool. Test de control negativo (SM2-E) lo valida. |
| R4 (Hermes modifica output) | Comparar `message` del transcript con `message` del stub. Cualquier diferencia es FAIL. |
| R5 (memory/skills activos) | `memory.enabled: false` y `skills.enabled: false` en config. SM1-G lo verifica. |
| R6 (serialización `progressive_context`) | Usar transport `stdio` en primera prueba (más simple). Si falla, probar `http`. |
| R7 (inestabilidad pip) | Registrar versión exacta. Usar `pip freeze > evidencias/SM1/pip_freeze.txt`. |
| R8 (latencia) | No es bloqueante en SM2. Medir y registrar para SM6 posterior. |
| R9 (filtración de config) | Verificar que `.env.sandbox` no importa ni reexporta variables del `.env.local`. |
| R10 (transport stdio) | Verificar transport disponible en SM1-D. Si solo soporta http, usar http en SM2. |
| R11 (WSL) | Si requiere WSL, documentarlo como restricción de plataforma. No bloquea SM2. |

**Reglas generales de mitigación:**
- No usar provider fallback no auditado para computabilidad clínica.
- No promover ADR-008 a APROBADO sin SM1+SM2 PASS documentados.
- No diseñar features sobre `EXTERNO_NO_VERIFICADO` sin pasar el smoke correspondiente.
- Desactivar memory y skills en todo el entorno de sandbox.

---

## 11. Próximo paso tras el plan

```
Plan aprobado
    ↓
Ejecutar SM1 (instalar y verificar Hermes)
    ↓
SM1 PASS?
    ├── NO → Registrar SM1 FAIL, no continuar. Notificar a arquitectura.
    └── SÍ → Continuar
         ↓
     Implementar PymIA MCP stub mínimo (server.py)
         ↓
     Ejecutar SM2 (conectar Hermes ↔ PymIA stub)
         ↓
     SM2 PASS?
         ├── NO → Registrar SM2 FAIL. No implementar integración. Notificar a arquitectura.
         └── SÍ → Proponer promover ADR-008 de PROPUESTA → APROBADO
                  Actualizar DOCUMENTATION_INDEX.md
                  Notificar a equipo para siguiente fase (SM3: Telegram real)
```

**Qué agente debe ejecutar SM1:**

SM1 puede ejecutarse con un agente con capacidad de:
- Ejecutar comandos en PowerShell (Windows) o bash (WSL).
- Instalar paquetes Python en entorno virtual aislado.
- Capturar y guardar logs a disco.
- Reportar PASS/FAIL con evidencias.

Sugerido: **agente Coder con herramientas de terminal**, instrucción explícita de no tocar `main` ni `.env.local`.

**Qué agente debe ejecutar SM2:**

SM2 requiere además:
- Implementar el stub mínimo `server.py` (≤100 líneas).
- Configurar Hermes con `mcp_servers:` apuntando al stub.
- Ejecutar transcripts interactivos y capturar logs.
- Comparar output del transcript con expected según contrato v0.1.

Sugerido: **agente Coder/Self con herramientas de terminal + capacidad de crear archivos**.

---

## 12. Sección anti-alucinación

### Tabla de etiquetas vigentes sobre Hermes (post-SM1/SM2)

Toda afirmación futura sobre Hermes en este repo debe usar una de estas etiquetas:

| Etiqueta | Significado |
|---|---|
| `VERIFICADO_EN_REPO` | Existe en código fuente del repo PymIA |
| `VERIFICADO_EN_TEST` | Validado en test ejecutado y con evidencia |
| `VERIFICADO_EN_CONFIG` | Presente en archivo de configuración activo |
| `VERIFICADO_EN_DOC_LOCAL` | Documentado en un archivo del repo (no externo) |
| `INFERIDO_NO_PROBADO` | Razonado a partir de documentación, sin test |
| `EXTERNO_NO_VERIFICADO` | Solo documentado en web/docs externa, sin test en repo |
| `PROHIBIDO_POR_CONTRATO` | Explícitamente prohibido por ontología, ADR o contrato |
| `PENDIENTE_DE_VALIDACION` | Requiere SM1 o SM2 para actualizar etiqueta |
| `BLOQUEADO_EN_TEST` | Intentado en SM y fallido — documentar razón |

### Estado de capacidades al abrir este plan

| Capacidad | Etiqueta actual | Actualiza tras |
|---|---|---|
| Hermes instala en Windows/WSL | `PENDIENTE_DE_VALIDACION` | SM1-A |
| Hermes arranca con config mínima | `PENDIENTE_DE_VALIDACION` | SM1-C |
| MCP client disponible | `EXTERNO_NO_VERIFICADO` | SM1-D → `VERIFICADO_EN_TEST` o `BLOQUEADO_EN_TEST` |
| API server disponible | `EXTERNO_NO_VERIFICADO` | SM1-E |
| 20+ canales disponibles | `EXTERNO_NO_VERIFICADO` | SM1-F (solo listar, no probar) |
| Memory desactivable | `EXTERNO_NO_VERIFICADO` | SM1-G |
| Skills desactivables | `EXTERNO_NO_VERIFICADO` | SM1-G |
| Hermes invoca tool MCP sin prompt extra | `PENDIENTE_DE_VALIDACION` | SM2-C |
| Transport stdio funcional | `PENDIENTE_DE_VALIDACION` | SM2-A |
| `progressive_context` se serializa por MCP | `PENDIENTE_DE_VALIDACION` | SM2-D |
| Hermes no diagnostica sin tool | `PENDIENTE_DE_VALIDACION` | SM2-E |
| Hermes no modifica output de tool | `PENDIENTE_DE_VALIDACION` | SM2-C+D |

### Prohibiciones activas hasta SM1 PASS

Queda prohibido:
1. Diseñar features basados en capacidades Hermes marcadas `EXTERNO_NO_VERIFICADO`.
2. Promover ADR-008 de PROPUESTA a APROBADO.
3. Implementar `pymia/mcp/server.py` productivo.
4. Modificar `conversa-engine/main.py` para integrar Hermes.
5. Exponer un PymIA MCP server en producción.

---

## Historial de versiones

| Versión | Fecha | Cambio |
|---|---|---|
| v1.0 | 2026-05-23 | Creación inicial del plan SM1+SM2 |
