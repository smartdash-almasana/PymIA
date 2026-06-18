# Owner / Operator View Split TaskSpec

## Estado

```text
Estado: TASKSPEC_READY
Tipo: DOCUMENTARY_TASKSPEC
Runtime impact: NONE
Productive code impact: NONE
Fecha: 2026-06-17
```

## Propósito

Separar explícitamente dos superficies de salida del flujo vertical de PymIA-Live:

```text
OWNER_VIEW
OPERATOR_VIEW
```

El objetivo es que el dueño PyME reciba una lectura simple, accionable y no técnica, mientras que el operador/auditor conserve trazabilidad completa para reconstrucción, soporte y auditoría.

Este frente no altera el core diagnóstico, no cambia contratos de evidencia y no modifica el significado de los registros existentes.

## Problema observado

El renderer actual `pymia/rendering/owner_markdown_renderer.py` genera un reporte titulado owner-facing, pero incluye en el encabezado identificadores técnicos:

```text
Tenant
Intake
Anamnesis ID
Investigation ID
Evidence ID
Evidence SHA-256
Run ID
Owner Answer ID, si existe
Evidence Request ID, si existe
```

Estos campos son correctos para trazabilidad interna, pero no necesariamente pertenecen a la primera vista del dueño.

La traza no debe eliminarse. Debe moverse o exponerse bajo una superficie explícita de operador.

## Evidencia de código leída

Archivos observados:

```text
pymia/rendering/owner_markdown_renderer.py
pymia/smartpyme/owner_facing_report.py
tests/e2e/test_vertical_slice_cli.py
```

Hallazgos:

```text
owner_markdown_renderer.py
- Renderiza el markdown visible.
- Inserta IDs técnicos en la parte superior del reporte.
- También renderiza secciones owner-readable: Qué entendimos, Qué pudimos leer, Qué falta, Próxima pregunta, Límites.

owner_facing_report.py
- Define OwnerFacingReport como reporte legible del dueño.
- No computa diagnóstico.
- No altera evidencia.
- Traduce artefactos existentes a reporte mínimo.

test_vertical_slice_cli.py
- Actualmente espera IDs técnicos dentro del markdown.
- Ya valida que diagnostic_operator_summary no aparezca en markdown.
- Ya valida que la referencia técnica de próxima pregunta se conserve para operador.
```

## Definiciones

### OWNER_VIEW

Vista destinada al dueño PyME.

Debe contener:

```text
- estado general del caso;
- archivo leído;
- mensaje recibido;
- qué entendimos;
- qué pudimos leer;
- qué todavía no podemos afirmar;
- evidencia usada en lenguaje comprensible;
- evidencia faltante en lenguaje comprensible;
- solicitud de evidencia, si aplica;
- próxima pregunta;
- límites y advertencias owner-safe.
```

No debe exponer como contenido principal:

```text
- anamnesis_id;
- investigation_id;
- evidence_id;
- evidence_request_id;
- owner_answer_id;
- run_id;
- output_hash / content_hash;
- nombres internos de contratos;
- IDs de fórmulas como texto primario;
- códigos de patologías como texto primario;
- diagnostic_operator_summary;
- estados internos del kernel.
```

### OPERATOR_VIEW

Vista destinada a operador, auditor o soporte técnico.

Debe conservar:

```text
- tenant_id;
- intake_id;
- anamnesis_id;
- investigation_id;
- evidence_id;
- evidence_request_id, si existe;
- owner_answer_id, si existe;
- run_id;
- evidence content_hash;
- output_hash, si aplica;
- metadata de PipelineRunRecord;
- storage paths o referencias internas, si existen;
- referencias técnicas de preguntas;
- diagnostic_operator_summary, si existe;
- límites técnicos y razones de bloqueo.
```

## Invariantes

```text
- No perder trazabilidad.
- No borrar IDs técnicos del modelo de datos.
- No romper PipelineRunRecord.
- No alterar EvidenceRecord.
- No promover OwnerAnswerRecord a EvidenceRecord automáticamente.
- No mostrar diagnostic_operator_summary en OWNER_VIEW.
- No diagnosticar en OWNER_VIEW.
- No prescribir acciones en OWNER_VIEW.
- No cambiar core diagnóstico.
- No cambiar contratos de evidencia.
```

## Alcance permitido para implementación futura

Una implementación futura podrá tocar, si se autoriza:

```text
pymia/rendering/owner_markdown_renderer.py
tests/e2e/test_vertical_slice_cli.py
```

Opcionalmente, si el diseño lo justifica:

```text
pymia/smartpyme/owner_facing_report.py
pymia/contracts/vertical_slice_copy_v1.py
```

No debe tocar en este frente:

```text
pymia/diagnostic_core/
pymia/contracts/evidence_v1.py
pymia/contracts/pipeline_run_v1.py
pymia/smartpyme/evidence.py
pymia/smartpyme/pipeline_registration.py
```

salvo hallazgo técnico posterior y TaskSpec nuevo.

## Opciones de diseño aceptables

### Opción A — Secciones separadas en un único markdown

Un mismo archivo markdown contiene:

```text
# Reporte para el dueño
...

---

# Anexo técnico para operador
...
```

Ventaja:

```text
mínimo cambio en CLI y delivery actual
```

Riesgo:

```text
el dueño puede seguir viendo el anexo si se le entrega el archivo completo
```

### Opción B — Dos renderers / dos salidas

Generar dos superficies:

```text
owner_markdown
operator_markdown
```

Ventaja:

```text
separación semántica fuerte
```

Riesgo:

```text
más cambio de pipeline y tests
```

### Opción C — Modo de render explícito

El renderer acepta un modo:

```text
audience="owner" | "operator" | "combined"
```

Ventaja:

```text
mantiene un punto de entrada y permite transición controlada
```

Riesgo:

```text
si no se testea bien, puede filtrar trazas técnicas en modo owner
```

## Recomendación inicial

Para un primer slice, la opción preferida es:

```text
Opción C: modo de render explícito
```

con default conservador:

```text
audience="owner"
```

y tests que garanticen:

```text
OWNER_VIEW no expone IDs técnicos.
OPERATOR_VIEW conserva IDs técnicos.
```

## Acceptance tests requeridos para implementación futura

Antes de tocar código, crear tests que expresen:

```text
1. owner markdown no contiene Anamnesis ID, Investigation ID, Evidence ID, Evidence SHA-256, Run ID.
2. owner markdown no contiene Owner Answer ID ni Evidence Request ID como encabezado técnico.
3. owner markdown conserva Qué entendimos, Qué pudimos leer, Qué falta, Próxima pregunta y Límites.
4. operator markdown contiene Anamnesis ID, Investigation ID, Evidence ID, Evidence SHA-256, Run ID.
5. operator markdown contiene Owner Answer ID y Evidence Request ID cuando existen.
6. operator markdown puede contener referencia técnica de pregunta.
7. owner markdown no contiene diagnostic_operator_summary.
8. operator view no cambia PipelineRunRecord ni EvidenceRecord.
9. build_report sigue devolviendo los records técnicos completos en dict interno.
10. No se introducen imports de runtime prohibido: Telegram, Hermes, LLM operator, MCP server, FastAPI.
```

## Criterio de cierre futuro

El frente podrá cerrarse cuando exista evidencia de:

```text
- tests owner/operator PASS;
- markdown owner limpio de IDs técnicos principales;
- operator view preserva trazabilidad;
- build_report conserva registros internos;
- no cambios en core diagnóstico;
- no cambios en contratos de evidencia;
- auditoría externa focal PASS.
```

## Riesgos

```text
- Romper tests actuales que esperan IDs técnicos en markdown.
- Ocultar trazabilidad si se eliminan IDs en lugar de moverlos.
- Crear duplicación de renderers sin contrato claro.
- Mezclar nuevamente owner view con operator view bajo nombres ambiguos.
- Reabrir core diagnóstico sin necesidad.
```

## Stop conditions

Detener implementación si ocurre cualquiera de estas condiciones:

```text
- se requiere modificar contratos de evidencia;
- se requiere cambiar PipelineRunRecord;
- se pierde algún ID técnico del dict interno;
- no queda claro qué salida recibe el dueño;
- no existen tests para owner view y operator view;
- aparecen cambios en core diagnóstico;
- se intenta commitear graphify-out/ o tooling local.
```

## Estado git esperado antes de implementación

Dirty local conocido y ajeno al frente:

```text
?? .agents/
?? .graphifyignore
?? .opencode/
?? graphify-out/
```

Estos archivos no pertenecen al frente y no deben incluirse en commits.

## Veredicto

```text
OWNER_OPERATOR_VIEW_SPLIT = TASKSPEC_READY
IMPLEMENTATION = NOT_STARTED
REQUIRES_EXTERNAL_AUDIT_BEFORE_CODE = YES
```
