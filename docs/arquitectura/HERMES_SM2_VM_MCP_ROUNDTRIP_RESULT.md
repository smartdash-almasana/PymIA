# Hermes SM2-VM MCP Roundtrip Result

## Estado

**VIGENTE — RESULTADO OPERATIVO**

Resultado de ejecución SM2-VM sobre la VM `smartpyme-factory` para validar Hermes MCP client contra un PymIA MCP server mínimo/stub.

## Veredicto

```text
SM2-VM MCP ROUNDTRIP: FAIL
```

## VM

```text
project: smartseller-490511
zone: us-central1-a
instance: smartpyme-factory
```

## Hermes

```text
Hermes Agent v0.13.0 (2026.5.7)
```

## Configuración aislada

```text
CONFIG_AISLADA: sí
```

Se confirmó que Hermes puede ejecutarse usando:

```text
HERMES_HOME=/tmp/pymia-sm2-vm/hermes-config
```

Esto permitió aislar configuración y evitar interacción con rutas productivas como `~/.hermes/`.

## MCP discovery

```text
MCP_DISCOVERY: fail
```

El comando:

```text
hermes mcp test pymia-mcp-stub
```

falló por timeout de 40 segundos.

Causa técnica:

```text
El stub del runbook no implementa un servidor MCP real JSON-RPC 2.0 por stdio.
El stub lee stdin hasta EOF.
El cliente MCP de Hermes mantiene el pipe abierto y espera handshake JSON-RPC.
Resultado: deadlock / timeout.
```

## Tool CA01

```text
TOOL_CA01: fail
```

Hermes no pudo invocar la tool `pymia.first_clinical_interview.v1` por falla de conexión MCP.

Observación crítica:

```text
Al fallar la conexión, Hermes respondió directamente usando su LLM base.
Eso viola la regla soberana: Hermes orquesta, PymIA computa.
```

## Tool CA05

```text
TOOL_CA05: fail
```

Hermes no pudo conectarse a la tool y respondió sin usar herramienta clínica ni transportar `progressive_context`.

## Control negativo

```text
CONTROL_NEGATIVO: fail
```

Ante una consulta clínica/financiera sin tool disponible, Hermes respondió con diagnóstico/instrucciones de negocio en lugar de negarse o derivar explícitamente a PymIA.

Esto confirma riesgo de suplantación:

```text
Hermes puede diagnosticar sin tool si la frontera no se fuerza técnicamente.
```

## Evidencias reportadas

```text
/tmp/pymia-sm2-vm/evidencias/SM2/hermes_version.txt
/tmp/pymia-sm2-vm/evidencias/SM2/hermes_help.txt
/tmp/pymia-sm2-vm/evidencias/SM2/hermes_mcp_help.txt
/tmp/pymia-sm2-vm/evidencias/SM2/hermes_mcp_list_before.txt
/tmp/pymia-sm2-vm/evidencias/SM2/hermes_mcp_list_after.txt
/tmp/pymia-sm2-vm/evidencias/SM2/stub_direct_CA01.txt
/tmp/pymia-sm2-vm/evidencias/SM2/stub_direct_CA05.txt
/tmp/pymia-sm2-vm/evidencias/SM2/tool_discovery.txt
/tmp/pymia-sm2-vm/evidencias/SM2/control_negativo.txt
```

## Riesgos confirmados

### R1 — Ruptura de regla soberana

Cuando el MCP falla, Hermes tiende a responder directamente con su LLM base.

Impacto:

```text
Hermes diagnostica sin PymIA.
```

Estado:

```text
CONFIRMADO_EN_SM2_VM
```

### R2 — No hay raw tool call simple confirmado

No se confirmó un comando Hermes CLI nativo que permita llamar una tool MCP con payload JSON crudo de forma directa y determinística.

Estado:

```text
PENDIENTE_DE_VALIDACION
```

### R3 — Stub no-MCP provoca deadlock

Un stub CLI por stdin/stdout no basta. MCP requiere protocolo JSON-RPC 2.0 persistente.

Estado:

```text
CONFIRMADO_EN_SM2_VM
```

## Bloqueo técnico raíz

```text
El stub usado no es un MCP server real.
```

Debe reemplazarse por un servidor MCP compatible con JSON-RPC 2.0 / stdio usando el SDK oficial `mcp`, `mcp.server`, `mcp.server.fastmcp` o equivalente compatible con Hermes.

## Decisión operativa

ADR-008 **no puede promoverse a APROBADO** con este resultado.

Estado de ADR-008:

```text
PROPUESTA
```

Motivo:

```text
Hermes MCP client existe y puede aislarse por HERMES_HOME, pero el roundtrip MCP con PymIA no está validado.
Además, se confirmó que Hermes puede suplantar computabilidad si la tool falla y no hay bloqueo técnico.
```

## Próximo paso obligatorio

Rediseñar SM2-VM con un MCP server real mínimo.

Nuevo frente técnico recomendado:

```text
pymia/mcp/server.py mínimo real
transport: stdio
protocol: MCP JSON-RPC 2.0
tool: pymia.first_clinical_interview.v1
```

Criterio para reintento:

```text
No volver a probar Hermes contra un stub stdin/stdout simple.
Solo reintentar con servidor MCP real compatible.
```

## Regla de no-regresión

Queda prohibido diseñar integración Hermes↔PymIA suponiendo que el stub simple valida MCP.

Antes de cualquier integración productiva debe existir:

```text
1. MCP server real mínimo de PymIA.
2. Test local del server MCP.
3. SM2-VM reejecutado contra ese server real.
4. Control negativo donde Hermes no diagnostique sin tool.
```

## Documentos relacionados

```text
docs/arquitectura/HERMES_SM2_VM_MCP_ROUNDTRIP_RUNBOOK.md
docs/arquitectura/HERMES_SM1_VM_GATEWAY_AUDIT_RESULT.md
docs/arquitectura/HERMES_OPERATIONAL_VERIFICATION.md
docs/adr/ADR-008-hermes-mcp-client-pymia-mcp-server.md
docs/contracts/pymia_first_clinical_interview_mcp_contract.md
```
