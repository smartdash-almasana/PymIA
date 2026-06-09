# M44 — Visible Owner Report Output ModuleContract

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M44_VISIBLE_OWNER_REPORT_OUTPUT`

---

## 1. Frontera

Este contrato regula la frontera entre:

```text
CoreAuditDeliveryBundle
↔ PymIAState.delivery_summary
↔ respuesta visible existente
```

La frontera M44 no crea un canal nuevo.

Sólo proyecta al state/respuesta existente una pieza textual ya autorizada por M42/M43.

---

## 2. Responsabilidad permitida

La frontera M44 puede:

- leer `bundle.owner_facing_report`;
- leer `bundle.delivery_package`;
- seleccionar el summary visible según prioridad contractual;
- escribir `PymIAState.delivery_summary`;
- preservar `PymIAState.output_refs`;
- conservar `phase`, `gate_verdict`, `delivery_status`, `execution_status` y `findings_count` según el bundle.

---

## 3. Regla de prioridad del summary

La selección del summary visible debe ser:

```text
1. owner_facing_report["summary"] si existe y no está vacío
2. delivery_package.summary como fallback
```

El fallback existe para evitar salida vacía, no para reinterpretar el resultado.

---

## 4. Responsabilidades prohibidas

La frontera M44 no puede:

- construir un nuevo `OwnerFacingReport`;
- modificar `owner_facing_report.py`;
- recalcular diagnóstico;
- recalcular fórmulas;
- cambiar findings;
- alterar gates;
- cambiar `DeliveryPackage`;
- tocar `pymia/orchestration/graph.py` salvo que un TaskSpec específico lo autorice;
- abrir Telegram, Hermes, FastAPI o canal externo;
- generar narrativa no trazable.

---

## 5. Inputs

- `state: PymIAState`
- `bundle: CoreAuditDeliveryBundle`

Campos relevantes del bundle:

- `owner_facing_report`
- `delivery_package.summary`
- `delivery_package.output_refs`
- `delivery_package.status`
- `execution_result.status`
- `execution_result.findings_count`
- `gate_verdict.verdict`

---

## 6. Outputs

- Nuevo `PymIAState` copiado desde el estado anterior.
- `delivery_summary` seleccionado por prioridad contractual.
- `output_refs` preservados desde `delivery_package.output_refs`.
- `phase` derivada sólo del `delivery_package.status`, sin nueva semántica.

---

## 7. Side effects

La función de proyección a state no debe escribir archivos, ejecutar runtime, llamar red, invocar canales ni modificar artefactos fuente.

---

## 8. Determinismo

Para el mismo `state` y el mismo `bundle`, la proyección debe producir el mismo `PymIAState`.

---

## 9. Invariantes

- Un caso `BLOCKED` debe seguir `BLOCKED`.
- Un resultado candidato no puede aparecer como confirmado.
- El summary visible no puede agregar información no presente en artefactos fuente.
- Si el owner summary está vacío, el fallback debe ser explícitamente `delivery_package.summary`.
- `output_refs` debe conservar el artefacto `owner_facing_report.json` cuando el bundle lo contiene.

---

## 10. Estado

```text
M44 ModuleContract = AUTHORIZED_DOCUMENTARY
```

Este contrato autoriza la proyección visible mínima.

No certifica implementación ni validación.
