# CHECKPOINT — M34/M35 Diagnostic Core + Evidence Binding

Fecha: 2026-06-08
Estado: checkpoint operativo para continuidad entre chats
Repo: `E:/BuenosPasos/smartbridge/PymIA`

---

## Estado confirmado

```text
M34 = núcleo calculador determinístico construido y extendido
M35 = evidence-to-core iniciado y probado hasta fixture Excel
repo = sincronizado según último reporte del usuario
último HEAD informado = ccb5a31
```

Últimos commits relevantes informados:

```text
ccb5a31 feat(diagnostic-core): support REN002 replacement coefficient formula
de36c31 feat(diagnostic-core): support PYME033 sku concentration formula
4bfa179 feat(diagnostic-core): support PYME044 client margin formula
5504647 docs(pymia): checkpoint M35 evidence to core binding
5b3b7b9 feat(diagnostic-core): support PYME027 interest EBITDA ratio formula
e08888e feat(diagnostic-core): support PYME026 operating cash flow formula
39d493b test(diagnostic-core): execute Excel fixture through core
911ce5d fix(diagnostic-core): scope source refs per formula
505bc2d test(diagnostic-core): execute structured evidence through core
17d6432 feat(diagnostic-core): bind structured evidence to core input
f8aeeb4 docs(pymia): close M34 diagnostic core v1
```

---

## Núcleo calculador actual

Se implementaron 15 fórmulas/ejes en el núcleo:

```text
REN_001_margen_neto_real
LIQ_001_vendido_cobrado
INV_002_rotacion_stock
PYME_011_dso
PYME_013_dso_dpo_gap
LIQ_002_saldo_final_proyectado
PYME_024_liquidez_corriente
PYME_017_pricing_drift
INV_001_punto_reposicion
punto_equilibrio_ventas
PYME_026_flujo_operativo
PYME_027_intereses_ebitda
PYME_044_margen_cliente
PYME_033_concentracion_sku
REN_002_coeficiente_reposicion
```

Archivos centrales:

```text
pymia/contracts/formula_contract.py
pymia/services/formula_engine_service.py
pymia/diagnostic_core/core.py
pymia/diagnostic_core/models.py
pymia/diagnostic_core/evidence_binding.py
tests/services/test_formula_engine_service.py
tests/diagnosticcore/test_diagnostic_core_v1.py
tests/diagnosticcore/test_evidence_binding.py
tests/diagnosticcore/test_evidence_binding_core_execution.py
tests/diagnosticcore/test_excel_fixture_core_execution.py
```

---

## M35 cerrado hasta ahora

```text
M35-S1 — StructuredEvidence → DiagnosticCoreInput
M35-S2 — StructuredEvidence → binder → DiagnosticCoreV1
M35-S3 — source_refs por fórmula
M35-S4 — Excel fixture → StructuredEvidence → binder → core
```

Contratos preservados:

```text
no inventar variables
bloquear inputs faltantes
bloquear divisiones por cero cuando aplica
preservar source_refs
source_refs acotados por fórmula
DiagnosticCoreV1 devuelve CANDIDATE, nunca CONFIRMED
no tocar capas fuera del slice activo
```

---

## Decisión operativa vigente

No seguir explicando de más en chat. Trabajar por prompts cortos, slices chicos y evidencia:

```text
TaskSpec corto
Codex implementa
tests focales
DeepSeek/Coder audita rápido
push sólo con aprobación
checkpoint cuando haya cierre
```

Separación de roles:

```text
Codex = ejecución puntual, no lectura amplia
Coder = lectura/auditoría amplia si hace falta
DeepSeek = auditoría focal barata
GPT = orquestación y control de deriva
repo/tests = verdad
```

---

## Próximo paso recomendado

El usuario pidió seguir un poco más con poco tiempo restante. Próximo slice corto:

```text
M35-S5 — ampliar evidence_binding aliases para:
PYME_044_margen_cliente
PYME_033_concentracion_sku
REN_002_coeficiente_reposicion
```

Prompt reducido ya definido:

```text
Archivos permitidos:
- pymia/diagnostic_core/evidence_binding.py
- tests/diagnosticcore/test_evidence_binding.py

No tocar:
- FormulaEngineService
- formula_contract
- parser
- smartpyme
- tools
- conversa-engine
```

Aliases propuestos:

```text
PYME_044_margen_cliente:
client_revenue | ingresos_cliente
client_direct_costs | costos_directos_cliente
client_service_costs | costos_servicio_cliente

PYME_033_concentracion_sku:
main_sku_sales | ventas_sku_principal
total_sales | ventas_total

REN_002_coeficiente_reposicion:
closing_index | indice_cierre
origin_index | indice_origen
```

Test mínimo:

```text
test_binding_maps_new_formula_aliases
```

---

## Pendientes del catálogo JSON

Después de las 15 fórmulas implementadas, quedan pendientes:

```text
PYME_004_recpam_basico
PYME_047_tiempo_manual_automatizado
M05_roi_automatizacion
OPE_001_decisiones_centralizadas
```

No priorizar salvo decisión explícita. Mejor continuar M35/M36.

---

## Próxima etapa mayor

```text
M36 — Port Hardening / Contract Enforcement
```

Pero sólo después de cerrar más M35. Objetivo de M36:

```text
convertir puertos/gates documentales en contratos de código y tests
```
