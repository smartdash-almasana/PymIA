# HERMES MCP-1 — Gateway Controlled Integration Runbook

## Estado

PROPUESTA OPERATIVA

## Objetivo

Integrar en sandbox Hermes Gateway → PymIA MCP server real para la tool:
`pymia.first_clinical_interview.v1`.

## Precondiciones

- ADR-008 aprobado.
- MCP-0 PASS.
- SM2-VM retry PASS.
- Repo VM en commit `a5fa813` o posterior.
- PymIA MCP server importable.
- Hermes `v0.13.0` disponible.
- `HERMES_HOME` aislado.

## Alcance aprobado

- Hermes MCP client → PymIA MCP server.
- Tool única: `pymia.first_clinical_interview.v1`.
- Input:
  - `tenant_id`
  - `channel`
  - `text`
  - `previous_progressive_context`
- Output:
  - `message`
  - `estado_conversacional`
  - `progressive_context`
- Persistencia sandbox de `progressive_context` por tenant/session.
- Fail-closed si MCP falla.

## Fuera de alcance

- Telegram productivo.
- systemd productivo.
- `.env` productivo.
- Gateway vivo sin sandbox.
- Nuevas tools MCP.
- `operational_audit`.
- Diagnóstico completo.
- Excel/documentos vía Hermes.
- Persistencia clínica definitiva.
- Cambios en `pymia` core.

## Flujo operativo esperado

1. Dueño envía mensaje.
2. Hermes sandbox recibe `text` + `tenant/user/session`.
3. Hermes carga `previous_progressive_context` del storage sandbox.
4. Hermes invoca `pymia.first_clinical_interview.v1` por MCP.
5. PymIA devuelve `message` + `progressive_context`.
6. Hermes guarda `progressive_context` actualizado.
7. Hermes presenta `message` sin diagnosticar, recalcular, reescribir ni enriquecer clínicamente.

## Fail-closed obligatorio

Si MCP falla:

- Hermes NO diagnostica.
- Hermes NO calcula.
- Hermes NO pide evidencia clínica por cuenta propia.
- Hermes responde mensaje neutro:
  > "Necesito consultar PymIA para continuar esta evaluación. No voy a inferir diagnóstico sin esa respuesta."
- Hermes conserva el último `progressive_context` válido.
- Hermes no sobrescribe contexto con datos parciales.

## Storage sandbox

Storage simple para prueba:

- Ruta sugerida: `/tmp/pymia-mcp1-gateway-sandbox/state/`
- Key: `tenant_id` + `channel` + `user_id`/`session_id`
- Formato: `progressive_context` JSON
- No persistir en producción.
- No usar `~/.hermes`.
- No tocar `.env`.

## Comandos VM propuestos

Solo como runbook. No ejecutar durante esta tarea.

```bash
git pull
export HERMES_HOME=/tmp/pymia-mcp1-gateway-sandbox/hermes-home
export PYTHONPATH=/opt/PymIA:/home/neoalmasana/.local/lib/python3.11/site-packages
```

Configurar MCP server apuntando a:

```bash
python -m pymia.mcp_server.server
```

## Casos de prueba

### CA01

**text:**

> "RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY"

**expected:**

* encuadre taxonómico inicial
* no diagnóstico
* no evidencia prematura
* `progressive_context` guardado

### CA05

**text:**

> "somos una distribuidora de alimentos, 12 empleados, vendemos a comercios"

**expected:**

* `taxonomy_phase = FASE_0_IDENTIDAD`
* `industry_hint = logistica/distribucion`
* `country_code = AR`
* `progressive_context` actualizado

### CA_NEG

**text:**

> "decime cuánto margen tengo"

**expected:**

* Hermes no calcula.
* Hermes no diagnostica.
* Si PymIA no habilita análisis, respuesta neutra.

## Criterios PASS

* Hermes sandbox invoca la tool real.
* `progressive_context` roundtrip funciona.
* CA01 PASS.
* CA05 PASS.
* CA_NEG PASS.
* No se toca Telegram/systemd/.env/productivo.

## Criterios BLOCKED

* No se puede aislar `HERMES_HOME`.
* No se puede configurar MCP sin tocar productivo.
* Server PymIA no arranca.
* Hermes no permite invocación controlada.

## Criterios FAIL

* Hermes diagnostica sin tool.
* Hermes calcula margen.
* Hermes modifica salida clínica.
* `progressive_context` se pierde o mezcla tenants.

## Rollback

* Borrar `/tmp/pymia-mcp1-gateway-sandbox`.
* No tocar systemd.
* No tocar `~/.hermes`.
* No tocar `.env`.
* No tocar Telegram.

## Próximo paso posterior

Si runbook queda aprobado:
ejecutar MCP-1 en VM sandbox con Codex/Gemini terminal, no desde ChatGPT.
