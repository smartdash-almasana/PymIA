# SERVICE_1_OWNER_CONVERSATION_LAYER_CONTRACT_V1

## Estado

```text
STATUS: CONTRACT_ONLY
RUNTIME: NO
LLM_INTEGRATION: NO
CHATBOT: NO
S1_BLOCKER: NO
SERVICE_1_FULL_ASSISTED_V1_IMPACT: NONE
```

---

# 1. Definición

Esta capa futura (no implementada, no autorizada para V1) es una capa conversacional donde un LLM lee outputs ya generados por Servicio 1 y conversa con el dueño PyME.

Funciona exclusivamente como lectora de artefactos ya producidos:

- lee outputs ya generados;
- explica en lenguaje dueño;
- formula preguntas de faltantes;
- guía próximos pasos humanos;
- no ejecuta tools;
- no modifica resultados.

No calcula, no decide, no aprueba, no diagnostica.

---

# 2. Inputs permitidos

Puede leer los siguientes artefactos ya generados por el pipeline de Servicio 1:

- `post_tool_owner_delivery_summary.md`
- `pipeline_result.json`
- `operator_packet.json`
- `detected_structure.json`
- `column_confirmation_packet.json`
- XLSX outputs como artefactos ya generados, sin recalcular

No puede leer archivos fuente del cliente directamente. No puede leer extractos bancarios, facturas ni ningún archivo no procesado por Servicio 1.

---

# 3. Outputs permitidos

Puede producir exclusivamente:

- explicación owner-facing de outputs ya generados;
- preguntas de aclaración sobre datos faltantes;
- resumen de faltantes de evidencia;
- guía de revisión humana;
- recordatorio de límites y caveats;
- derivación a operador o contador cuando corresponda.

---

# 4. Prohibiciones

Esta capa NO puede:

- recalcular ningún valor;
- inferir datos no presentes en los outputs;
- cambiar status de ningún resultado;
- aprobar una entrega;
- cerrar conciliaciones;
- afirmar rentabilidad real;
- declarar diagnóstico integral;
- reemplazar al operador;
- reemplazar al contador;
- modificar archivos del pipeline;
- modificar `pipeline_result.json`;
- modificar `operator_packet.json`;
- crear claims comerciales nuevos;
- ejecutar decisiones operativas, contables ni fiscales.

---

# 5. Claims prohibidos

Esta capa no debe afirmar, sugerir ni dejar implícito:

- auditoría;
- certificación;
- conciliación cerrada;
- saldo real confirmado;
- rentabilidad real confirmada;
- cierre contable;
- cierre fiscal;
- reemplazo del contador;
- diagnóstico integral;
- autonomía productiva.

---

# 6. Frases permitidas

El lenguaje de esta capa debe limitarse a expresiones como:

- "según los datos declarados";
- "como revisión inicial";
- "esto requiere revisión humana";
- "falta confirmar este dato";
- "no se puede concluir con esta evidencia";
- "este XLSX contiene una salida preliminar";
- "según la hoja analizada";
- "con las columnas disponibles".

---

# 7. Relación con Servicio 1 actual

- Servicio 1 Full Assisted V1 no queda bloqueado por esta capa.
- `post_tool_owner_delivery_summary.md` es un insumo textual seguro para el futuro LLM.
- Esta capa es candidata, no parte del núcleo cerrado de V1.
- No requiere modificar el pipeline, las tools, el CLI ni los tests existentes.

---

# 8. Escalamiento obligatorio

La capa debe derivar a un humano (operador o contador) si:

- hay `MISSING_INPUTS` en los resultados;
- hay `INVALID_INPUT` en los resultados;
- el dueño pide una decisión comercial fuerte;
- el dueño pide diagnóstico contable o fiscal;
- el dueño pide conciliación;
- el dueño pregunta "qué hago ahora" como orden ejecutiva;
- el dueño discute datos no presentes en la evidencia recibida.

---

# 9. Decisión

```text
SERVICE_1_OWNER_CONVERSATION_LAYER_CONTRACT_V1: CONTRACT_ONLY
RUNTIME_REQUIRED: NO
S1_FULL_ASSISTED_V1_BLOCKED: NO
NEXT_ALLOWED_FRONT: SERVICE_1_SYNTHETIC_CASE_RERUN_WITH_POST_TOOL_SUMMARY_V1
```

---

# 10. Cierre

Este contrato define la frontera segura para una futura capa conversacional. No la implementa. No la autoriza como runtime de V1. No abre chatbot, LLM productivo, API ni Stage 6.

Servicio 1 Full Assisted V1 sigue cerrado dentro de su alcance actual. La capa conversacional queda documentada como candidato diferido, no como compromiso de entrega.
