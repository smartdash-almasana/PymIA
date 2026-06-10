# OWNER_CONFIRMED_SEMANTIC_REQUEST_FLOW_TASKSPEC

Fecha: 2026-06-10
Estado: DRAFT_FOR_REVIEW
Frente: OWNER_CONFIRMED_SEMANTIC_REQUEST_FLOW

## 1. Propósito

Diseñar el próximo slice posterior al gate soberano de confirmación semántica del dueño.

El objetivo es conectar conceptualmente tres piezas ya existentes:

```text
OwnerSemanticConfirmationGate
OwnerSemanticEvidenceRequest
owner-facing reentry / blocked actionable flow
```

sin abrir todavía runtime productivo ni modificar `DiagnosticCore`.

## 2. Regla rectora

```text
Narrativa del dueño
→ interpretación tentativa
→ confirmación / corrección explícita del dueño
→ pedido semántico accionable de evidencia
→ BLOCKED_ACTIONABLE hasta recibir evidencia estructural
```

Prohibido:

```text
Narrativa del dueño
→ evidencia automática
→ diagnóstico
```

## 3. Problema que resuelve

El sistema ya puede:

- capturar respuestas del dueño;
- evaluar respuestas sin promoverlas a evidencia dura;
- construir pedidos semánticos de evidencia;
- representar un gate de confirmación soberana.

Pero todavía falta una capacidad que conecte esos contratos en una ruta ordenada:

```text
si el dueño confirma un eje semántico,
entonces el sistema puede pedir evidencia accionable alineada a ese eje,
pero no puede computar ni diagnosticar hasta recibir evidencia estructural válida.
```

## 4. Alcance permitido del slice futuro

El slice futuro podrá diseñar o implementar una función pura, sin side effects, que reciba:

```text
OwnerSemanticConfirmationGate confirmado o corregido
missing inputs estructurales vigentes
contexto mínimo del caso / source_ref
```

y devuelva:

```text
OwnerSemanticEvidenceRequest o lista de OwnerSemanticEvidenceRequest
estado lógico BLOCKED_ACTIONABLE
traza de por qué no se computa todavía
```

## 5. Invariantes obligatorias

- Sólo se generan pedidos semánticos de evidencia si el gate está `CONFIRMED_BY_OWNER` o `CORRECTED_BY_OWNER`.
- Si el gate está `PENDING_OWNER_CONFIRMATION`, no se genera pedido final de evidencia.
- Si el gate está `REJECTED_BY_OWNER`, se debe pedir nueva interpretación o nueva repregunta, no evidencia final.
- Ningún owner answer narrativo se convierte en evidencia dura.
- Ningún pedido semántico produce findings.
- Ningún pedido semántico cambia resultado diagnóstico.
- El estado correcto ante faltantes estructurales sigue siendo bloqueado, pero accionable.

## 6. Entradas conceptuales

```text
confirmation_gate:
  OwnerSemanticConfirmationGate

missing_inputs:
  lista de missing_key / missing_input_type

case_context:
  tenant_id / cliente_id si aplica
  source_ref
  pathology candidates opcionales
  formula candidates opcionales
```

## 7. Salidas conceptuales

```text
semantic_evidence_requests:
  list[OwnerSemanticEvidenceRequest]

flow_status:
  BLOCKED_ACTIONABLE | PENDING_OWNER_CONFIRMATION | NEEDS_REINTERPRETATION

reason:
  texto técnico trazable
```

## 8. Ejemplo esperado

### Entrada

```text
Gate:
status = CONFIRMED_BY_OWNER
proposed_interpretation = revisar margen/precios por suba de tela
related_missing_keys = [own_price, cost_unit]

Missing inputs:
own_price
cost_unit
```

### Salida

```text
flow_status = BLOCKED_ACTIONABLE

semantic_evidence_requests:
- pedir precios de venta por producto/SKU, período y vigencia;
- pedir costo unitario o costo aproximado por producto/SKU.
```

### Prohibición

```text
No hay diagnóstico.
No hay findings.
No hay evidencia validada.
```

## 9. No autorizado en este TaskSpec

Este documento no autoriza:

- tocar `DiagnosticCore`;
- tocar graph productivo;
- tocar Telegram;
- tocar Hermes runtime productivo;
- crear PDF;
- crear ERP;
- agregar fórmulas;
- emitir findings;
- resolver evidencia estructural por narrativa.

## 10. Criterio de cierre futuro

Un futuro cierre del slice debe demostrar:

```text
1. gate pendiente → no genera request final;
2. gate rechazado → pide reinterpretación;
3. gate confirmado → genera request semántico accionable;
4. gate corregido → genera request basado en corrección;
5. todos los casos conservan fail-closed;
6. ningún caso produce evidencia dura ni diagnóstico.
```
