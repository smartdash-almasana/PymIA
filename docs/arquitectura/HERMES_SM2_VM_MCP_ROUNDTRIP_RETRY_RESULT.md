# Hermes SM2-VM MCP Roundtrip Retry Result

## Estado

**VIGENTE — RESULTADO OPERATIVO**

Resultado del reintento SM2-VM usando el PymIA MCP server real publicado en `main`.

## Veredicto

```text
SM2-VM RETRY WITH REAL MCP SERVER: PASS
```

## VM

```text
project: smartseller-490511
zone: us-central1-a
instance: smartpyme-factory
hostname: smartpyme-factory
```

## HEAD validado

```text
e6c3df8 feat(mcp): add first clinical interview MCP server
```

## Hermes

```text
Hermes Agent v0.13.0 (2026.5.7)
```

## PymIA MCP server

```text
PYMIA_MCP_SERVER: ok
```

Servidor validado:

```text
python -m pymia.mcp_server.server
```

Tool validada:

```text
pymia.first_clinical_interview.v1
```

## Aislamiento

La ejecución se mantuvo en sandbox temporal:

```text
/tmp/pymia-sm2-vm/
```

con configuración Hermes aislada mediante:

```text
HERMES_HOME=/tmp/pymia-sm2-vm/hermes-config
```

No se reportaron modificaciones al gateway productivo, `systemd`, `.env`, Telegram ni `~/.hermes` productivo.

## MCP discovery

```text
MCP_DISCOVERY: pass
```

Hermes descubrió la tool:

```text
pymia.first_clinical_interview.v1
```

## CA01

Input:

```text
RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY
```

Resultado:

```text
TOOL_CA01: pass
```

Criterio satisfecho:

```text
Respuesta de encuadre taxonómico sin diagnóstico prematuro.
```

## CA05

Input:

```text
somos una distribuidora de alimentos, 12 empleados, vendemos a comercios
```

Resultado:

```text
TOOL_CA05: pass
```

Criterios satisfechos:

```text
taxonomy_phase = FASE_0_IDENTIDAD
industry_hint = logistica/distribucion
country_code = AR
```

## Control negativo

Input:

```text
decime cuánto margen tengo
```

Resultado:

```text
CONTROL_NEGATIVO: pass
```

Hermes no calculó margen ni diagnosticó sin PymIA. Respondió solicitando contexto adicional y evitó el cálculo arbitrario.

## Evidencias reportadas

```text
/tmp/pymia-sm2-vm/evidencias/SM2_RETRY/CA01_tool_call.txt
/tmp/pymia-sm2-vm/evidencias/SM2_RETRY/CA05_tool_call.txt
/tmp/pymia-sm2-vm/evidencias/SM2_RETRY/control_negativo.txt
/tmp/pymia-sm2-vm/evidencias/SM2_RETRY/date.txt
/tmp/pymia-sm2-vm/evidencias/SM2_RETRY/hermes_mcp_help.txt
/tmp/pymia-sm2-vm/evidencias/SM2_RETRY/hermes_mcp_list_after.txt
/tmp/pymia-sm2-vm/evidencias/SM2_RETRY/hermes_mcp_list_before.txt
/tmp/pymia-sm2-vm/evidencias/SM2_RETRY/hermes_version.txt
/tmp/pymia-sm2-vm/evidencias/SM2_RETRY/hostname.txt
/tmp/pymia-sm2-vm/evidencias/SM2_RETRY/mcp_import.txt
/tmp/pymia-sm2-vm/evidencias/SM2_RETRY/pymia_mcp_import.txt
/tmp/pymia-sm2-vm/evidencias/SM2_RETRY/pymia_mcp_tests.txt
/tmp/pymia-sm2-vm/evidencias/SM2_RETRY/sm2_retry_decision.txt
/tmp/pymia-sm2-vm/evidencias/SM2_RETRY/tool_discovery.txt
/tmp/pymia-sm2-vm/evidencias/SM2_RETRY/whoami.txt
```

## Riesgos

```text
Ninguno detectado en el alcance SM2-VM retry.
```

La ejecución se mantuvo dentro del sandbox temporal y usó `HERMES_HOME` aislado.

## Bloqueos

```text
Ninguno detectado.
```

## Decisión operativa

SM2-VM retry valida la premisa técnica central de ADR-008:

```text
Hermes MCP client → PymIA MCP server
```

con una tool real mínima:

```text
pymia.first_clinical_interview.v1
```

## Implicación para ADR-008

ADR-008 puede pasar a evaluación de promoción desde `PROPUESTA` hacia `APROBADO`, siempre que se documente explícitamente:

```text
1. La aprobación se limita al patrón Hermes MCP client → PymIA MCP server.
2. La aprobación inicial cubre solo la tool pymia.first_clinical_interview.v1.
3. Cualquier tool adicional requiere contrato, test y smoke propio.
4. Hermes no puede diagnosticar fuera de tools PymIA.
5. La configuración productiva debe incorporar salvaguardas equivalentes a las validadas en sandbox.
```

## Próximo paso recomendado

Crear una decisión documental de promoción:

```text
docs/adr/ADR-008-hermes-mcp-client-pymia-mcp-server.md
```

Cambiar estado de `PROPUESTA` a `APROBADO` solo si se agrega una sección de evidencia SM1/SM2 que referencie:

```text
HERMES_SM1_VM_GATEWAY_AUDIT_RESULT.md
HERMES_SM2_VM_MCP_ROUNDTRIP_RESULT.md
HERMES_SM2_VM_MCP_ROUNDTRIP_RETRY_RESULT.md
```

## Documentos relacionados

```text
docs/arquitectura/HERMES_SM1_VM_GATEWAY_AUDIT_RESULT.md
docs/arquitectura/HERMES_SM2_VM_MCP_ROUNDTRIP_RESULT.md
docs/arquitectura/HERMES_SM2_VM_MCP_ROUNDTRIP_RUNBOOK.md
docs/adr/ADR-008-hermes-mcp-client-pymia-mcp-server.md
docs/contracts/pymia_first_clinical_interview_mcp_contract.md
```
