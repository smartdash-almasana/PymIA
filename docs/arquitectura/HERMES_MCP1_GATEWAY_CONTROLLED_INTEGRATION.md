# MCP-1: Integración controlada Hermes Gateway -> PymIA MCP Server

## Objetivo MCP-1
Definir y ejecutar una integración controlada en sandbox donde Hermes Gateway invoque el server MCP real de PymIA para la tool aprobada `pymia.first_clinical_interview.v1`, sin modificar runtime productivo ni fronteras arquitectónicas.

## Alcance aprobado
- Hermes como MCP client y PymIA como MCP server (`python -m pymia.mcp_server.server`).
- Única tool habilitada: `pymia.first_clinical_interview.v1`.
- Flujo de entrada/salida contractual con `tenant_id`, `channel`, `text`, `previous_progressive_context`.
- Persistencia del `progressive_context` por sesión/tenant en almacenamiento de sandbox del gateway.
- Control de fallback no clínico ante error MCP.

## Fuera de alcance
- Telegram productivo.
- systemd productivo.
- `.env` productivo.
- Gateway vivo fuera de sandbox.
- Nuevas tools MCP.
- `operational_audit`.
- Diagnóstico clínico completo.
- Persistencia clínica definitiva en Hermes.
- Interpretación documental/Excel vía Hermes.

## Contrato de invocación desde Hermes Gateway
Hermes debe invocar `pymia.first_clinical_interview.v1` con payload mínimo:

```json
{
  "tenant_id": "<tenant_id>",
  "channel": "<channel>",
  "text": "<texto_usuario>",
  "previous_progressive_context": { "..." : "..." } | null
}
```

Reglas:
- `tenant_id`: obligatorio, no vacío, estable por sesión.
- `channel`: obligatorio, no vacío (por ejemplo `gateway_sandbox`).
- `text`: obligatorio, no vacío, texto literal del dueño.
- `previous_progressive_context`: null en primer turno; luego el último contexto persistido para el mismo tenant.

## Gestión de progressive_context
1. Leer contexto previo en sandbox por clave compuesta (`tenant_id` + `channel` + `session_id`).
2. Enviar ese contexto en `previous_progressive_context`.
3. Si la respuesta MCP contiene `status="ok"` y `progressive_context` no nulo, guardar snapshot completo.
4. Nunca mezclar contexto entre tenants; si hay mismatch de `tenant_id`, descartar y registrar incidente.

## Regla de seguridad clínica ante fallo MCP
Si la tool falla (`status="error"`, timeout, conexión caída, respuesta inválida, excepción client):
- Hermes no debe emitir diagnóstico ni hipótesis propias.
- Hermes debe devolver respuesta operacional neutra (sin contenido clínico), indicando indisponibilidad temporal de análisis.
- Hermes debe registrar evento técnico con causa y correlación de sesión.
- Hermes debe conservar el último `progressive_context` válido sin sobrescribir con datos parciales.

## Criterio PASS / BLOCKED / FAIL
- PASS:
  - Gateway sandbox invoca tool real y recibe `status="ok"` en casos válidos.
  - Se persiste y reutiliza `progressive_context` por tenant sin contaminación cruzada.
  - Ante fallo MCP, Hermes responde neutro sin salida clínica.
- BLOCKED:
  - Dependencia externa no disponible (entorno sandbox, credenciales sandbox, conectividad interna).
  - Imposibilidad operativa de ejecutar flujo sin tocar entorno productivo.
- FAIL:
  - Hermes emite salida clínica sin respuesta MCP válida.
  - Se detecta mezcla de contexto entre tenants.
  - Se requiere tocar componentes fuera de alcance para completar la prueba.

## Comandos VM (solo sandbox)
Ejecutar únicamente en sandbox aislado, nunca sobre gateway productivo:

```bash
# En sandbox VM
cd /tmp/pymia-mcp1-sandbox/PymIA
python -m pymia.mcp_server.server
```

```bash
# En sandbox Hermes Gateway
# (comando concreto según runner de sandbox; prohibido systemd productivo)
<sandbox_gateway_runner> --mcp-server stdio --tool pymia.first_clinical_interview.v1
```

## Rollback
1. Detener procesos de sandbox de Hermes y PymIA MCP.
2. Revertir configuración de sandbox al modo previo (sin cliente MCP activo).
3. Eliminar snapshots de `progressive_context` generados en la corrida de prueba.
4. Confirmar que no se modificó gateway vivo, systemd, Telegram ni `.env` productivo.
