# M37 — Core to Audit and Delivery Integration ModuleContract

Fecha: 2026-06-08
Estado: VIGENTE
Frente: `M37_CORE_TO_AUDIT_AND_DELIVERY_INTEGRATION`

---

## 1. Módulo / frontera

Frontera mínima entre:

- núcleo diagnóstico (`DiagnosticCoreV1` + gates M36)
- salida soberana SCN
- gate de entrega
- paquete de entrega
- estado operativo

```text
DiagnosticCoreResult
→ SCN OperationalAuditResult mapping
→ RenderContract
→ ExecutionResultGate-compatible result
→ DeliveryPackage
→ PymIAState
```

---

## 2. Responsabilidades

La frontera M37 debe:

- adaptar `DiagnosticCoreResult` a un `OperationalAuditResult` soberano mínimo;
- preservar `tenant_id`, referencias de evidencia y `missing_evidence`;
- derivar `RenderContract` sólo desde un resultado soberano verificado;
- materializar archivos mínimos para `output_refs`;
- proyectar el resultado final al estado operativo.

---

## 3. Side effects permitidos

Permitidos sólo dentro de un `output_dir` explícito:

- escribir `operational_audit_result.json`
- escribir `render_contract.json`
- escribir `delivery_summary.md`

Fuera de eso, ningún side effect.

---

## 4. Side effects prohibidos

Prohibido:

- ejecutar Telegram;
- ejecutar parser Excel;
- ejecutar runtime bridge o microservicios;
- persistir estado fuera del helper explícito;
- generar narrativa libre;
- inventar findings nuevos.

---

## 5. Dependency boundaries

Dependencias permitidas:

- `pymia/contracts/evidence_v1.py`
- `pymia/diagnostic_core/*`
- `pymia/contracts/scn_operational_audit_verifier.py`
- `pymia/contracts/scn_output_gateway.py`
- `pymia/smartpyme/execution_result_gate.py`
- `pymia/smartpyme/delivery_package.py`
- `pymia/orchestration/state.py`

Dependencias prohibidas:

- `pymia/telegram_*`
- parser Excel
- runtime productivo
- nuevos contratos soberanos paralelos

---

## 6. Determinismo

- mismo input → mismo `status`, mismas referencias y mismo contenido semántico;
- orden determinístico de `findings`, `missing_evidence` y referencias;
- no reinterpretar findings fuera de lo que ya trae `DiagnosticCoreResult`;
- no agregar causalidad ni narrativa diagnóstica.
