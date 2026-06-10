# ASSISTED_SIMULATED_PILOT_002_BIS_BLOCKED_ACTIONABLE_CHECKPOINT

Fecha: 2026-06-10
Estado: READY_FOR_VALIDATION
Tipo: simulación asistida documental/computable
Caso base: La Textil Cosida SRL
Deriva de: `ASSISTED_SIMULATED_PILOT_002_VALUE_CHECKPOINT.md`

## 1. Propósito

Repetir conceptualmente la simulación asistida 002 incorporando las nuevas piezas semánticas cerradas:

```text
OwnerSemanticConfirmationGate
build_owner_confirmed_semantic_request_flow(...)
project_confirmed_semantic_requests_to_owner_facing(...)
```

El objetivo no es producir findings ni diagnóstico. El objetivo es demostrar que el caso puede pasar de:

```text
BLOCKED genérico / PARTIAL de valor
```

a:

```text
BLOCKED_ACTIONABLE visible para el dueño
```

sin romper la frontera fail-closed.

## 2. Línea base 002 original

Resultado anterior:

```text
Estado: PARTIAL
findings_count = 0
phase = BLOCKED
delivery_status = BLOCKED
operational_status = pending_data
```

Fricción detectada:

```text
- preguntas demasiado genéricas;
- no prioriza evidencia concreta;
- missing_evidence conserva claves técnicas;
- respuesta narrativa del dueño fue considerada pero no redujo faltantes;
- no alcanza como informe cobrable autónomo.
```

Faltantes estructurales observados:

```text
average_sales
average_stock
client_direct_costs
client_revenue
client_service_costs
closing_index
lead_time
market_price
origin_index
own_price
safety_stock
taxes
```

## 3. Nuevas piezas aplicadas

### 3.1 Gate semántico

Se representa el acto de confirmación del dueño:

```text
OwnerSemanticConfirmationGate
status = CONFIRMED_BY_OWNER
proposed_interpretation = revisar margen/precios por suba de tela y cambios de precio durante el período
owner_response_text = Sí, primero margen y precios.
related_missing_keys = [own_price, average_stock, dso]
```

### 3.2 Flujo confirmado

Se aplica:

```text
build_owner_confirmed_semantic_request_flow(...)
```

con missing keys soportadas:

```text
own_price
average_stock
dso
```

Resultado esperado:

```text
flow_status = BLOCKED_ACTIONABLE
semantic_evidence_requests_count >= 1
unsupported_missing_keys preservadas si aparecen
findings_count = 0
```

### 3.3 Proyección owner-facing

Se aplica:

```text
project_confirmed_semantic_requests_to_owner_facing(...)
```

El reporte visible debe conservar:

```text
status = BLOCKED
delivery_status = BLOCKED
operational_status = pending_data
missing_evidence sin resolver
evidence_used sin alteración
findings sin alteración
```

pero debe mejorar:

```text
next_questions
next_steps
limit_warnings
semantic_request_projection
```

## 4. Resultado esperado 002 bis

### 4.1 Estado

```text
BLOCKED_ACTIONABLE
```

Interpretación:

```text
El sistema sigue bloqueado porque falta evidencia estructural, pero ahora puede pedir datos concretos alineados con el eje confirmado por el dueño.
```

### 4.2 Preguntas accionables esperadas

Para `own_price`:

```text
Para calcular margen necesito precios de venta por producto/SKU de la última semana y, si cambiaron durante el período, desde qué fecha rigió cada precio.
```

Para `average_stock`:

```text
Para revisar stock necesito stock inicial y stock final por producto del período analizado. Si no lo tenés exacto, pasame una estimación y marcala como estimada.
```

Para `dso`:

```text
Para revisar cobranzas necesito una lista con cliente, importe, fecha de factura o venta y fecha real de cobro. Si no tenés fecha exacta, indicá si cobró a 30, 45, 60 días o sigue pendiente.
```

## 5. Valor operativo que sí debería certificar

```text
- El dueño confirma/corrige el eje semántico.
- PymIA no diagnostica todavía.
- El sistema deja de responder con fallback genérico.
- El reporte owner-facing muestra qué evidencia concreta pedir.
- La narrativa no se promueve a evidencia dura.
- El caso queda bloqueado, pero accionable.
```

## 6. Valor que NO debe certificar

```text
- No findings accionables.
- No diagnóstico de margen.
- No recomendación operativa final.
- No piloto real.
- No cierre TD-004.
- No autonomía comercial plena.
```

## 7. Criterio PASS de Codex

Codex debe crear un test documental/computable que demuestre:

```text
1. partiendo de un owner-facing report bloqueado;
2. con un OwnerSemanticConfirmationGate confirmado;
3. con missing keys own_price, average_stock y dso;
4. el flow devuelve BLOCKED_ACTIONABLE;
5. la proyección agrega pedidos concretos en next_questions;
6. la proyección agrega warning fail-closed;
7. el reporte conserva status, evidence_used y missing_evidence;
8. findings_count sigue en 0 o no aparece;
9. no se toca runtime, graph ni DiagnosticCore.
```

## 8. Comando sugerido

```text
python -m pytest tests/smartpyme/test_assisted_simulated_pilot_002_bis_blocked_actionable.py tests/smartpyme/test_owner_confirmed_semantic_request_flow.py tests/smartpyme/test_owner_confirmed_semantic_request_projection.py tests/architecture -q --basetemp .tmp_pytest_assisted_simulated_pilot_002_bis
```

## 9. Veredicto esperado

Si los criterios pasan:

```text
PASS_BLOCKED_ACTIONABLE
```

Lectura:

```text
La simulación 002 bis no convierte el caso en diagnóstico, pero sí mejora el valor operativo de recuperación de evidencia: el dueño recibe pedidos concretos, trazables y alineados con el eje confirmado.
```

## 10. No autorizado

Este checkpoint no autoriza:

```text
DiagnosticCore
graph productivo
Telegram
Hermes runtime productivo
PDF
ERP
nuevas fórmulas
findings
promoción de narrativa a evidencia dura
piloto real
cierre TD-004
```
