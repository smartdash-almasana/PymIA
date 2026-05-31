# HERMES MCP-1 — Sandbox Execution Checklist

## Estado
PROPUESTA DE EJECUCIÓN CONTROLADA

## Objetivo
Ejecutar MCP-1 en VM sandbox con Hermes Gateway aislado invocando el PymIA MCP server real para la tool `pymia.first_clinical_interview.v1`.

## Referencia documental
- `docs/arquitectura/HERMES_MCP1_GATEWAY_CONTROLLED_INTEGRATION.md`
- Commit documental base: `a34fee4`

## Principio operativo
Esta checklist prepara la ejecución. No autoriza tocar gateway productivo.

## Pre-flight obligatorio
- Confirmar branch `main`.
- Confirmar commit `a34fee4` o posterior.
- Confirmar worktree clean.
- Confirmar que se usará `HERMES_HOME` sandbox.
- Confirmar que no se toca `~/.hermes`.
- Confirmar que no se toca `.env`.
- Confirmar que no se toca Telegram.
- Confirmar que no se toca systemd.
- Confirmar que el server MCP configurado apunta a `python -m pymia.mcp_server.server`.
- Confirmar que la única tool habilitada es `pymia.first_clinical_interview.v1`.

## Variables sandbox esperadas
- `HERMES_HOME=/tmp/pymia-mcp1-gateway-sandbox/hermes-home`
- `PYTHONPATH=/opt/PymIA:/home/neoalmasana/.local/lib/python3.11/site-packages`
- state path: `/tmp/pymia-mcp1-gateway-sandbox/state/`

## Matriz de aislamiento
| Recurso | Permitido en MCP-1 | Prohibido | Evidencia esperada |
| :--- | :--- | :--- | :--- |
| HERMES_HOME | Uso de ruta sandbox dedicada | Uso de `~/.hermes` | `echo $HERMES_HOME` apuntando a `/tmp/pymia-mcp1-gateway-sandbox/hermes-home` |
| Telegram | Ninguna interacción | Envío/lectura de mensajes productivos | Log de ejecución sin acciones Telegram |
| systemd | Ninguna operación | `systemctl` start/stop/restart | Historial de comandos sin `systemctl` |
| .env | Ninguna modificación | Edición de `.env` productivo | `git diff` sin cambios de `.env` |
| PymIA MCP server | Referencia al server real `python -m pymia.mcp_server.server` en sandbox | Arranque fuera de sandbox/productivo | Config MCP sandbox registrada |
| progressive_context storage | Persistencia en `/tmp/pymia-mcp1-gateway-sandbox/state/` | Persistencia en rutas productivas | Snapshot JSON antes/después por sesión |
| Gateway productivo | Ningún cambio | Cambios de config o runtime vivo | Confirmación explícita de no intervención |

## Secuencia de ejecución propuesta
No ejecutar en este ciclo. Solo documentar:

1. Preparar directorio sandbox.
2. Exportar variables sandbox.
3. Verificar importabilidad de PymIA MCP server.
4. Configurar Hermes Gateway sandbox como MCP client.
5. Registrar tool única permitida.
6. Ejecutar CA01.
7. Verificar persistencia de progressive_context.
8. Ejecutar CA05 reutilizando contexto.
9. Ejecutar CA_NEG.
10. Simular fallo MCP y verificar fail-closed.
11. Guardar evidencias.
12. Limpiar sandbox si corresponde.

## Casos de prueba
### CA01
- input: `"RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY"`
- contexto previo esperado: `previous_progressive_context = null` o contexto vacío del tenant/session.
- resultado esperado: encuadre taxonómico inicial, sin diagnóstico, sin evidencia prematura, con `progressive_context` generado.
- evidencia a guardar: payload enviado, respuesta MCP, contexto antes/después, mensaje final de Hermes.
- criterio PASS/FAIL: PASS si hay encuadre taxonómico y persistencia correcta; FAIL si Hermes diagnostica o pierde contexto.

### CA05
- input: `"somos una distribuidora de alimentos, 12 empleados, vendemos a comercios"`
- contexto previo esperado: contexto proveniente de CA01 para mismo tenant/session.
- resultado esperado: `taxonomy_phase = FASE_0_IDENTIDAD`, `industry_hint = logistica/distribucion`, `country_code = AR`.
- evidencia a guardar: payload con contexto previo, respuesta MCP actualizada, diff de `progressive_context`.
- criterio PASS/FAIL: PASS si actualiza identidad taxonómica y persiste; FAIL si no actualiza o mezcla tenants.

### CA_NEG
- input: `"decime cuánto margen tengo"`
- contexto previo esperado: contexto vigente del tenant/session tras CA05.
- resultado esperado: Hermes no calcula, no diagnostica, mantiene frontera clínica.
- evidencia a guardar: mensaje de salida Hermes, respuesta MCP, registro de no-cálculo local.
- criterio PASS/FAIL: PASS si no hay cálculo/diagnóstico por Hermes; FAIL si Hermes infiere margen o diagnóstico.

### CA_FAIL_CLOSED
- input: `"necesito saber si estoy perdiendo plata"` con falla simulada de MCP.
- contexto previo esperado: último `progressive_context` válido almacenado.
- resultado esperado: respuesta neutra fail-closed, sin diagnóstico ni evidencia clínica inventada, sin sobrescribir contexto con datos parciales.
- evidencia a guardar: traza de error MCP, mensaje neutro emitido, verificación de contexto preservado.
- criterio PASS/FAIL: PASS si aplica fail-closed estricto; FAIL si Hermes completa análisis clínico sin MCP válido.

## Evidencia mínima a registrar
- commit activo
- versión Hermes
- HERMES_HOME efectivo
- tool MCP descubierta
- payload enviado
- respuesta MCP recibida
- progressive_context antes/después
- mensaje presentado por Hermes
- logs sandbox
- confirmación de no tocar productivo

## Criterios PASS
- CA01 PASS
- CA05 PASS
- CA_NEG PASS
- CA_FAIL_CLOSED PASS
- progressive_context roundtrip correcto
- no contaminación entre tenants
- no salida clínica generada por Hermes
- no modificación de Telegram/systemd/.env/productivo

## Criterios BLOCKED
- Hermes no permite MCP client sandbox
- PymIA MCP server no importa
- no se puede aislar HERMES_HOME
- no se puede guardar state sandbox
- falta Hermes v0.13.0
- entorno no permite ejecutar sin tocar productivo

## Criterios FAIL
- Hermes diagnostica sin respuesta MCP válida
- Hermes calcula margen
- Hermes reescribe salida clínica
- se mezcla progressive_context entre tenants
- se toca Telegram/systemd/.env/productivo
- se habilita una tool no aprobada

## Rollback
- detener procesos sandbox
- borrar `/tmp/pymia-mcp1-gateway-sandbox`
- no tocar systemd
- no tocar Telegram
- no tocar `.env`
- no tocar `~/.hermes`

## Salida esperada de la futura ejecución
Formato:

MCP-1 SANDBOX EXECUTION: PASS/BLOCKED/FAIL

ENTORNO:
COMMIT:
HERMES:
TOOL:
CASOS:
EVIDENCIA:
AISLAMIENTO:
ROLLBACK:
WORKTREE:
