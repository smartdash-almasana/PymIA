# SCN-002 — Contract Validation Layer Design

Estado: DRAFT DESIGN — NO IMPLEMENTATION  
Ambito: Hermes <-> PymIA  
Tipo: Diseno conceptual de frontera contractual  
Fecha: 2026-05-24

---

## 1. Proposito

Disenar la Boundary Layer entre Hermes y PymIA sin implementar runtime.

Este documento define contratos conceptuales, reglas de fail-closed y criterios de validacion para evitar degradacion estructural entre entrada externa y salida soberana.

---

## 2. No autorizado

Este documento no autoriza:

- produccion;
- Telegram real;
- ejecucion MCP-3;
- nuevas tools;
- plugins reales;
- modificacion de runtime;
- configuracion sensible.

---

## 3. Evidencia de diseno

Resumen de auditoria de frontera `OperationalAuditResult -> operational_audit_router`:

- `OperationalAuditResult` existe y es estructuralmente valido.
- El router degrada estructura a texto demasiado temprano.
- `forbidden_inferences` se pierde en el render final.
- El fail-closed es parcial (modelo), pero insuficiente en router.
- `EvidenceCandidate` aun no esta materializado como contrato de entrada.
- Los tests de frontera son insuficientes para no degradacion.

Campos observados como degradados/ignorados en el flujo actual:

- `audit_trail`;
- `operational_signals`;
- `priority_problems`;
- `improvement_opportunities`;
- `taxonomy`.

---

## 4. Principio

```text
Hermes no llama al kernel directo.
Hermes envia EvidenceCandidate.
PymIA devuelve OperationalAuditResult.
Hermes renderiza solo un RenderContract autorizado.
```

---

## 5. Componentes propuestos

Definicion conceptual de componentes de la capa contractual:

- `PymIAInputGateway`: recibe input externo, valida envelope y enruta solo evidencia candidata.
- `EvidenceCandidateValidator`: valida estructura minima y clasifica estado `valid`/`pending_data`/`blocked`.
- `KernelRequestBuilder`: transforma evidencia validada en `KernelRequest` trazable.
- `PymIAOutputGateway`: recibe `OperationalAuditResult` y evita render directo de payload crudo.
- `OperationalAuditResultVerifier`: valida integridad estructural, estado, campos minimos y consistencia.
- `RenderContractBuilder`: reduce salida al contrato de render permitido por policy.
- `ForbiddenInferenceGuard`: propaga y hace cumplir `forbidden_inferences` sin silenciamiento.
- `FailClosedHandler`: aplica bloqueo obligatorio ante invalidaciones o faltantes criticos.
- `AuditTrailPropagator`: preserva trazas minimas de decision sin exponer computabilidad interna.
- `MemorySplitGuard`: impide que Hermes persista memoria clinica/finding como verdad propia.
- `PolicyEngine`: concentra reglas de autorizacion, minimizacion y restricciones de salida.
- `Signature/SovereignMarkVerifier`: exige marca soberana verificable antes de habilitar render.

---

## 6. Flujo propuesto

```text
External input
-> EvidenceCandidate
-> PymIAInputGateway
-> KernelRequest
-> PymIA Kernel
-> OperationalAuditResult
-> PymIAOutputGateway
-> RenderContract
-> Hermes render
```

---

## 7. Contratos conceptuales

Se definen contratos conceptuales sin crear schemas en este documento:

- `EvidenceCandidate`: entrada externa no soberana; puede ser texto, archivo o metadata de recoleccion.
- `KernelRequest`: solicitud normalizada y trazable hacia kernel PymIA, derivada de evidencia valida.
- `OperationalAuditResult`: salida soberana del kernel con estado, findings, restricciones y trazabilidad.
- `RenderContract`: subconjunto autorizado de salida para Hermes (sin razonamiento interno ni ampliaciones).
- `RuntimePolicy`: reglas de frontera que gobiernan validacion, minimizacion, propagacion y bloqueo.

---

## 8. Reglas de fail-closed

La capa debe bloquear cuando ocurra cualquiera de estas condiciones:

- falta evidencia;
- falta `status`;
- falta `result`;
- `result` invalido;
- `forbidden_inferences` no puede propagarse;
- output sin marca soberana verificable;
- Hermes intenta generar `finding`;
- kernel falla.

Salida esperada en bloqueo: `blocked` o `pending_data` segun corresponda, sin diagnostico ni recomendaciones fuertes.

---

## 9. Output minimization

Hermes solo puede recibir:

- `summary` permitido;
- `next_questions`;
- `next_steps`;
- `blocked_message`;
- `forbidden_inferences`;
- `references` permitidas.

Todo campo fuera de este conjunto debe ser descartado o bloqueado por policy.

---

## 10. Prohibiciones explicitas

Hermes no puede:

- generar findings;
- completar findings;
- transformar candidates en truth;
- persistir memoria clinica;
- crear skills con logica PymIA;
- ignorar `forbidden_inferences`;
- renderizar fuera del contrato.

---

## 11. Relacion con router actual

- `operational_audit_router` actual no se elimina en SCN-002.
- SCN-002 propone gateways futuros delante y detras del router.
- Este documento no ejecuta refactor ni modifica runtime.
- La implementacion futura debe demostrar no degradacion estructural extremo a extremo.

---

## 12. Tests futuros minimos

Tests requeridos para implementacion posterior (no creados en este documento):

- `invalid OperationalAuditResult -> blocked`
- `missing_evidence -> blocked/pending_data`
- `forbidden_inferences propagate to RenderContract`
- `no findings -> no diagnosis`
- `Hermes cannot add findings`
- `audit_trail preserved`
- `output without SovereignMark blocked`
- `blocked/pending_data do not become recommendations`
- `RenderContract contains only allowed fields`

---

## 13. Criterios de aceptacion futuros

SCN-002 no se considera implementable hasta contar con:

- schemas draft;
- tests de frontera;
- policy example;
- sandbox Hermes separado;
- no Telegram real;
- no produccion.

---

## 14. Relacion documental

Este diseno debe leerse junto con:

- `docs/arquitectura/SCN_001_SOVEREIGN_COMPUTATION_BOUNDARY.md`;
- `docs/contracts/scn/GLOSSARY.md`;
- `docs/hermes/HERMES_LOCAL_INSTANCE_INVENTORY.md`;
- auditoria de frontera `OperationalAuditResult -> operational_audit_router` con veredicto `FRONTIER_AUDIT_PASS_WITH_WARNINGS`.

---

## 15. Decision

SCN-002 queda como diseno conceptual.

No habilita implementacion hasta auditoria documental posterior, cierre de contratos de schema y validacion de frontera en sandbox.
