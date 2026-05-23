# HERMES SM1-VM Gateway Audit Result

## 1. Resumen ejecutivo
- SM1 local fue invalidado como fuente primaria porque Hermes Gateway no vive en la PC local.
- Se ejecutó auditoria read-only directa en VM Google Cloud via IAP SSH.
- Resultado: `SM1-VM PASS` con Hermes Gateway activo en VM, MCP disponible en CLI, pero sin servidores MCP configurados.

## 2. VM auditada
- Proyecto: `smartseller-490511`
- Zona: `us-central1-a`
- Instancia: `smartpyme-factory`
- Hostname: `smartpyme-factory`

## 3. Metodo de acceso
- Acceso confirmado por `gcloud compute ssh ... --tunnel-through-iap`.
- Sin cambios de firewall, IAM o configuracion de red.

## 4. Servicios detectados
- `smartpyme-telegram-control.service` existe en systemd.
- Estado actual: `inactive (dead)`.

## 5. Procesos detectados
- Hermes Gateway activo:
  - `/opt/PymIA/conversa-engine/.venv/bin/hermes gateway run --replace`
- Hermes Dashboard activo:
  - `/opt/PymIA/conversa-engine/.venv/bin/hermes dashboard --no-open --tui`
- Proxy uvicorn activo:
  - `... python -m uvicorn ... --host 127.0.0.1 --port 8777`

## 6. Puertos detectados
- `127.0.0.1:9119`
- `127.0.0.1:8777`
- `127.0.0.1:11434`

## 7. Rutas relevantes
- `/opt/PymIA`
- `/opt/PymIA/conversa-engine`
- `/opt/PymIA/pymia/hermes`
- `/opt/hermes-runtime/pymia`

## 8. Version Hermes
- `Hermes Agent v0.13.0 (2026.5.7)`
- Python VM: `Python 3.11.2`

## 9. Estado MCP
- `hermes mcp` disponible en CLI.
- `hermes mcp list`: no hay servidores MCP configurados.
- Estado operativo de cliente MCP hacia PymIA: `PENDIENTE_DE_VALIDACION`.

## 10. Estado systemd
- Unidad encontrada:
  - `/etc/systemd/system/smartpyme-telegram-control.service`
- Evidencia de falla en logs:
  - error de `EnvironmentFile` faltante
  - error de ruta/archivo faltante en `ExecStart`
- Impacto: la unidad systemd falla, aunque Hermes Gateway real corre por proceso separado.

## 11. Relacion real con PymIA
- Relacion `real` confirmada.
- Evidencia: procesos Hermes levantados desde `/opt/PymIA/conversa-engine`.

## 12. Riesgos
- Divergencia entre runtime real (proceso Hermes en `.venv`) y unidad systemd fallida.
- Falta de configuracion MCP puede bloquear validacion de roundtrip Hermes client -> PymIA MCP server.
- Posible confusion operativa si se diagnostica solo por systemd sin verificar procesos vivos.

## 13. Bloqueos
- No hubo bloqueo de acceso IAP SSH.
- Bloqueo operativo actual: cliente MCP sin servidores configurados.
- Bloqueo secundario: servicio `smartpyme-telegram-control.service` caido por archivo/ruta faltante.

## 14. Decision
- `SM1-VM PASS` con:
  - gateway Hermes activo en VM
  - cliente MCP disponible en CLI
  - servidores MCP no configurados aun
- Estado consolidado: validacion de infraestructura base confirmada; integracion MCP todavia no confirmada.

## 15. Proximo paso
- Ejecutar `SM2-VM` en modo controlado y read-only ampliado:
  - validar conexion de Hermes como MCP client contra endpoint de prueba de PymIA
  - no tocar gateway productivo
  - no hacer deploy ni cambios de runtime en esta etapa

## Etiquetas de evidencia
- `VERIFICADO_EN_VM`
- `VERIFICADO_EN_SERVICE`
- `VERIFICADO_EN_PROCESS`
- `VERIFICADO_EN_PORT`
- `VERIFICADO_EN_LOG`
- `VERIFICADO_EN_REPO`
- `PENDIENTE_DE_VALIDACION`
- `BLOQUEADO_OPERACIONAL`
