# Hermes SM2-VM MCP Roundtrip Runbook

## Estado

**VIGENTE — RUNBOOK OPERATIVO**

Este documento convierte en acción operativa el protocolo SM2-VM. No debe quedar como información dispersa en chat.

## Propósito

Validar, en la VM real de Google Cloud, si Hermes puede actuar como MCP client contra un PymIA MCP server mínimo/stub sin tocar el gateway productivo.

La prueba busca confirmar o bloquear la arquitectura definida por ADR-008:

```text
Hermes MCP client → PymIA MCP server
```

## Contexto verificado previo

SM1-VM confirmó:

```text
project: smartseller-490511
zone: us-central1-a
instance: smartpyme-factory
hostname: smartpyme-factory
Hermes Agent: v0.13.0 (2026.5.7)
Hermes Gateway activo: /opt/PymIA/conversa-engine/.venv/bin/hermes gateway run --replace
Hermes Dashboard activo: /opt/PymIA/conversa-engine/.venv/bin/hermes dashboard --no-open --tui
MCP CLI: disponible
MCP servers configurados: ninguno
```

## Regla soberana

```text
Hermes orquesta.
PymIA computa.
Hermes no suplanta la computabilidad de PymIA.
```

## Prohibiciones

Durante SM2-VM:

```text
No tocar gateway productivo.
No reiniciar servicios.
No modificar systemd.
No tocar .env ni tokens.
No mandar mensajes reales por Telegram.
No modificar configs productivas de Hermes.
No usar hermes mcp add si escribe configuración global/productiva.
No hacer deploy.
No commitear desde la VM.
No exponer secretos.
Si no se puede aislar config MCP, detener y reportar BLOCKED.
```

## Objetivo SM2-VM

Validar en sandbox aislado dentro de la VM:

```text
Hermes MCP client
→ PymIA MCP server mínimo/stub
→ tool pymia.first_clinical_interview.v1
→ respuesta tipada
→ Hermes no diagnostica ni modifica computabilidad
```

---

# Fase 0 — Acceso a VM

Desde máquina local con gcloud autenticado:

```bash
gcloud compute ssh smartpyme-factory \
  --project=smartseller-490511 \
  --zone=us-central1-a \
  --tunnel-through-iap
```

---

# Fase 1 — Preparar sandbox aislado en VM

```bash
mkdir -p /tmp/pymia-sm2-vm
cd /tmp/pymia-sm2-vm
mkdir -p pymia-mcp-stub evidencias/SM2 hermes-config
```

Reglas:

```text
No usar /opt/PymIA salvo lectura.
No usar configs productivas.
Todo output de prueba debe quedar bajo /tmp/pymia-sm2-vm/evidencias/SM2.
```

---

# Fase 2 — Localizar Hermes CLI real

```bash
HERMES_BIN="/opt/PymIA/conversa-engine/.venv/bin/hermes"

$HERMES_BIN --version > /tmp/pymia-sm2-vm/evidencias/SM2/hermes_version.txt 2>&1
$HERMES_BIN --help | head -120 > /tmp/pymia-sm2-vm/evidencias/SM2/hermes_help.txt 2>&1
$HERMES_BIN mcp --help > /tmp/pymia-sm2-vm/evidencias/SM2/hermes_mcp_help.txt 2>&1
$HERMES_BIN mcp list > /tmp/pymia-sm2-vm/evidencias/SM2/hermes_mcp_list_before.txt 2>&1
```

Criterio:

```text
Debe quedar registrada la versión Hermes y el estado inicial de MCP.
Si HERMES_BIN no existe o no ejecuta, SM2-VM BLOCKED.
```

---

# Fase 3 — Verificar si Hermes permite config aislada

Investigar solo por help/man/config:

```bash
$HERMES_BIN --help | grep -Ei "config|home|profile|mcp|server" > /tmp/pymia-sm2-vm/evidencias/SM2/hermes_config_surface.txt 2>&1
$HERMES_BIN mcp --help | grep -Ei "config|home|profile|add|list|remove|server" > /tmp/pymia-sm2-vm/evidencias/SM2/hermes_mcp_config_surface.txt 2>&1
```

Criterio:

```text
Si Hermes permite --config, HERMES_HOME, --profile, o equivalente aislado: continuar.
Si solo permite modificar configuración global/productiva: SM2-VM BLOCKED.
```

Prohibición explícita:

```text
No ejecutar hermes mcp add todavía.
```

---

# Fase 4 — Crear PymIA MCP server stub mínimo

Crear:

```bash
cat > /tmp/pymia-sm2-vm/pymia-mcp-stub/server.py <<'PY'
#!/usr/bin/env python3
from __future__ import annotations

import json
import sys

TOOL_NAME = "pymia.first_clinical_interview.v1"


def _response(payload: dict) -> dict:
    text = (payload.get("text") or "").lower()
    tenant_id = payload.get("tenant_id") or "sm2-vm-test"
    previous = payload.get("previous_progressive_context")
    previous_phase = None
    if isinstance(previous, dict):
        previous_phase = (
            previous.get("business_identity", {})
            .get("taxonomy_phase")
        )

    if "distribuidora de alimentos" in text:
        return {
            "status": "ok",
            "tool": TOOL_NAME,
            "estado_conversacional": "identidad_taxonomica_confirmada",
            "message": "Identidad base registrada: distribuidora de alimentos. A partir de ahora puedo continuar la primera entrevista clínica sin repetir el encuadre.",
            "anamnesis": None,
            "laboratorio": None,
            "progressive_context": {
                "tenant_id": tenant_id,
                "business_identity": {
                    "industry_hint": "logistica/distribucion",
                    "country_code": "AR",
                    "taxonomy_phase": "FASE_0_IDENTIDAD"
                },
                "symptom_summary": [],
                "documents_requested": []
            }
        }

    if previous_phase != "FASE_0_IDENTIDAD":
        return {
            "status": "ok",
            "tool": TOOL_NAME,
            "estado_conversacional": "encuadre_taxonomico_inicial",
            "message": "Antes de analizar síntomas o pedir evidencia, necesito ubicar qué tipo de organismo PyME estamos mirando: comercio, fábrica, servicios, distribución, gastronomía u otro.",
            "anamnesis": None,
            "laboratorio": None,
            "progressive_context": {
                "tenant_id": tenant_id,
                "business_identity": {
                    "industry_hint": None,
                    "country_code": None,
                    "taxonomy_phase": None
                },
                "symptom_summary": [],
                "documents_requested": []
            }
        }

    return {
        "status": "ok",
        "tool": TOOL_NAME,
        "estado_conversacional": "anamnesis_inicial",
        "message": "Con la identidad base resuelta, puedo continuar la primera entrevista clínica. Necesito entender qué área preocupa y qué señales ve el dueño, sin emitir diagnóstico todavía.",
        "anamnesis": None,
        "laboratorio": None,
        "progressive_context": previous
    }


def main() -> None:
    raw = sys.stdin.read().strip()
    if not raw:
        print(json.dumps({"status": "ready", "tool": TOOL_NAME}))
        return
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(json.dumps({"status": "error", "error_code": "invalid_json", "message": str(exc)}))
        return
    print(json.dumps(_response(payload), ensure_ascii=False))


if __name__ == "__main__":
    main()
PY
chmod +x /tmp/pymia-sm2-vm/pymia-mcp-stub/server.py
```

Importante:

```text
El stub valida transporte MCP, no computabilidad real.
No debe interpretarse como implementación productiva de PymIA.
```

Prueba directa opcional del stub, sin Hermes:

```bash
echo '{"tenant_id":"sm2-vm-test","channel":"sandbox-cli","text":"RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY","previous_progressive_context":null}' \
  | python3 /tmp/pymia-sm2-vm/pymia-mcp-stub/server.py \
  > /tmp/pymia-sm2-vm/evidencias/SM2/stub_direct_CA01.txt 2>&1
```

---

# Fase 5 — Config Hermes aislada

Crear config aislada solo si Hermes lo soporta.

Ubicación sugerida:

```bash
/tmp/pymia-sm2-vm/hermes-config/
```

Debe:

```text
desactivar memory si se puede;
desactivar skills si se puede;
registrar solo el MCP server stub;
exponer solo tool pymia.first_clinical_interview.v1.
```

Si no se puede aislar config:

```text
No continuar.
SM2-VM BLOCKED.
```

---

# Fase 6 — Test MCP discovery

Ejecutar Hermes con config aislada y verificar:

```bash
hermes mcp list
```

usando la config aislada.

Guardar:

```bash
/tmp/pymia-sm2-vm/evidencias/SM2/hermes_mcp_list_after.txt
/tmp/pymia-sm2-vm/evidencias/SM2/tool_discovery.txt
```

PASS parcial si aparece:

```text
pymia.first_clinical_interview.v1
```

---

# Fase 7 — Test tool call directo

Si Hermes tiene comando tipo:

```bash
hermes mcp call ...
```

o equivalente, invocar payload CA01:

```json
{
  "tenant_id": "sm2-vm-test",
  "channel": "sandbox-cli",
  "text": "RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY",
  "previous_progressive_context": null
}
```

Guardar request/response en:

```bash
/tmp/pymia-sm2-vm/evidencias/SM2/CA01_tool_call.txt
```

Validar:

```text
Hermes llama tool.
Stub responde tipado.
No hay diagnóstico.
No hay evidencia prematura.
```

---

# Fase 8 — Test segundo turno

Payload CA05:

```json
{
  "tenant_id": "sm2-vm-test",
  "channel": "sandbox-cli",
  "text": "somos una distribuidora de alimentos, 12 empleados, vendemos a comercios",
  "previous_progressive_context": {
    "tenant_id": "sm2-vm-test",
    "business_identity": {
      "taxonomy_phase": null
    }
  }
}
```

Guardar:

```bash
/tmp/pymia-sm2-vm/evidencias/SM2/CA05_tool_call.txt
```

Validar:

```text
taxonomy_phase = FASE_0_IDENTIDAD
industry_hint = logistica/distribucion
country_code = AR
```

---

# Fase 9 — Control negativo

Probar si Hermes responde clínicamente sin tool.

Input:

```text
decime cuánto margen tengo
```

Resultado esperado:

```text
Hermes debe negarse o indicar que necesita PymIA.
Hermes NO debe calcular ni diagnosticar.
```

Guardar:

```bash
/tmp/pymia-sm2-vm/evidencias/SM2/control_negativo.txt
```

---

# Fase 10 — Decisión final

Crear:

```bash
/tmp/pymia-sm2-vm/evidencias/SM2/sm2_decision.txt
```

Formato:

```text
SM2-VM PASS / BLOCKED / FAIL

Hermes version:
...

MCP config aislada:
sí/no

Tool discovery:
sí/no

Tool call CA01:
pass/fail

Tool call CA05:
pass/fail

Control negativo:
pass/fail

Conclusión:
...
```

---

# Criterios de decisión

## SM2-VM PASS

```text
config MCP aislada fue posible;
Hermes descubre el server MCP stub;
Hermes puede invocar pymia.first_clinical_interview.v1;
CA01 y CA05 pasan;
Hermes no diagnostica sin tool.
```

## SM2-VM BLOCKED

```text
no hay forma segura de aislar config;
Hermes MCP no permite call/test directo;
MCP server no puede registrarse sin tocar config productiva.
```

## SM2-VM FAIL

```text
Hermes diagnostica sin tool;
Hermes modifica output;
progressive_context no se transporta;
tool discovery falla pese a config aislada correcta.
```

---

# Salida obligatoria del agente ejecutor

```text
SM2-VM MCP ROUNDTRIP: PASS/BLOCKED/FAIL

VM:
<project/zone/instance>

HERMES:
<version>

CONFIG_AISLADA:
<sí/no + evidencia>

MCP_DISCOVERY:
<resultado>

TOOL_CA01:
<resultado>

TOOL_CA05:
<resultado>

CONTROL_NEGATIVO:
<resultado>

EVIDENCIAS:
<lista de archivos en /tmp/pymia-sm2-vm/evidencias/SM2>

RIESGOS:
<lista>

BLOQUEOS:
<lista>

SIGUIENTE_PASO:
- Si PASS: documentar SM2-VM y evaluar promover ADR-008.
- Si BLOCKED/FAIL: documentar bloqueo y no implementar integración.
```

---

# Documentos relacionados

```text
docs/arquitectura/HERMES_SM1_VM_GATEWAY_AUDIT_RESULT.md
docs/arquitectura/HERMES_SM1_SM2_ISOLATED_VALIDATION_PLAN.md
docs/arquitectura/HERMES_OPERATIONAL_VERIFICATION.md
docs/adr/ADR-008-hermes-mcp-client-pymia-mcp-server.md
docs/contracts/pymia_first_clinical_interview_mcp_contract.md
```
