# SERVICE_1_PATHOLOGY_CATALOG_AND_ANAMNESIS_ADR_V1

Status: Proposed
Type: Minimal conceptual ADR
Scope: Service 1 assisted XLSX lane only
Runtime impact: None
Code impact: None
Tests impact: None

## 1. Decisión

Servicio 1 incorporará como próximo bloque conceptual un **Pathology Catalog + Anamnesis Engine** acotado al carril **microservicio asistido sobre XLSX**.

La conversación con el dueño no gobernará el diagnóstico final por sí sola.
El catálogo de patologías propondrá **patologías candidatas**.
La anamnesis estructurará dolor, contexto, señales y evidencia faltante.
El diagnóstico seguirá dependiendo de evidencia computable y de ejecución determinística existente o futura autorizada.

## 2. Problema

Hoy Servicio 1 puede leer, normalizar, confirmar columnas, reingresar respuestas del dueño y preparar delivery controlado, pero todavía no tiene un bloque funcional explícito que una:

- dolor declarado por el dueño;
- señales operativas PyME;
- patologías candidatas;
- evidencia mínima requerida;
- preguntas de aclaración;
- decisión de qué cómputo vale la pena ejecutar.

Sin esa capa, el sistema corre riesgo de derivar hacia:

- intake sin orientación diagnóstica;
- preguntas aisladas sin hipótesis operacional;
- tools gobernando el producto;
- promesas diagnósticas antes de tener evidencia suficiente.

## 3. Alcance

Esta ADR define solamente:

- el lugar conceptual del catálogo de patologías dentro de Servicio 1;
- el rol de la anamnesis como captura estructurada del problema del dueño;
- un set inicial de patologías operativas PyME de bajo riesgo conceptual;
- el tipo de evidencia mínima requerida por patología;
- el tipo de preguntas que el sistema debe hacer al dueño;
- un contrato futuro mínimo para un módulo documental/runtime posterior.

## 4. No-alcance

Esta ADR **no** autoriza:

- diagnóstico integral automático;
- conciliación contable definitiva;
- nuevas capacidades contables soberanas;
- PDF/OCR como dependencia de entrada;
- apertura de Servicio 2;
- chatbot autónomo;
- SaaS autónomo;
- unificación de entrypoints;
- implementación de runtime, tests o código.

## 5. Modelo conceptual

```text
Dueño PyME
  ↓
Narrativa de dolor + contexto operativo
  ↓
Anamnesis estructurada
  ↓
Señales observables / términos del dueño
  ↓
Catálogo de patologías candidatas
  ↓
Evidencia mínima requerida por patología
  ↓
Preguntas de aclaración / owner confirmation
  ↓
Skills o microservicios determinísticos existentes
  ↓
Hallazgos técnicos acotados
  ↓
Diagnóstico asistido acotado
  ↓
Tratamiento / delivery controlado
```

Regla central:

**PymIA decide qué falta.**
**El dueño aporta significado y datos.**
**Las tools computan evidencia.**
**El delivery no convierte una sospecha en diagnóstico definitivo sin sustento.**

## 6. Estados

Estados conceptuales mínimos del bloque:

| Estado | Significado |
|---|---|
| `OWNER_NARRATIVE_CAPTURED` | Existe relato inicial del dueño. |
| `ANAMNESIS_PARTIAL` | Hay señales útiles pero faltan aclaraciones. |
| `PATHOLOGY_CANDIDATES_IDENTIFIED` | El catálogo pudo proponer una o más patologías candidatas. |
| `EVIDENCE_REQUIRED` | Falta evidencia mínima para contrastar la patología. |
| `OWNER_CONFIRMATION_REQUIRED` | Falta confirmación del dueño sobre significado, período, columnas o contexto. |
| `READY_FOR_DETERMINISTIC_COMPUTATION` | Ya existe base mínima para ejecutar cómputo permitido. |
| `EVIDENCE_INSUFFICIENT` | No alcanza para afirmar hallazgo útil. |
| `ASSISTED_FINDING_AVAILABLE` | Existe hallazgo acotado y trazable para delivery controlado. |

## 7. Primeras patologías operativas PyME

Se propone iniciar con patologías de lenguaje PyME, evidencia relativamente simple y afinidad con XLSX:

| Código | Patología | Lectura corta |
|---|---|---|
| `LIQ_001` | Descalce ventas-cobranzas | Vende pero no ve la plata entrar a tiempo. |
| `REN_001` | Margen invisible | Vende pero no sabe si gana o cuánto gana por línea. |
| `STK_001` | Stock incierto | Compra/vende sin confianza en existencias reales o rotación. |
| `CST_001` | Costeo incompleto | El precio existe, pero el costo total operativo no está armado. |
| `SAL_001` | Mezcla de ventas sin segmentación | Hay ventas, pero no se distingue producto, canal o período útil. |
| `CSH_001` | Caja desordenada por período | Hay movimientos, pero no una lectura clara de entradas/salidas por fecha. |

## 8. Evidencia requerida por patología

| Patología | Evidencia mínima requerida |
|---|---|
| `LIQ_001` | ventas por período, cobranzas por período, cuentas a cobrar o saldo pendiente, fechas de vencimiento si existen |
| `REN_001` | precio de venta, costo unitario o costo aproximado, volumen vendido, gastos variables relevantes |
| `STK_001` | listado de productos, stock inicial o actual, entradas, salidas o ventas, unidad de medida |
| `CST_001` | precio de compra o costo base, gastos asociados relevantes, criterio de imputación declarado por el dueño |
| `SAL_001` | fecha, producto/servicio, cantidad o importe, canal o categoría si existe |
| `CSH_001` | fecha, concepto, entrada/salida, monto, saldo si existe |

Regla:

Si la evidencia mínima no está, el sistema no debe cerrar diagnóstico; debe pedir aclaración, archivo o confirmación del dueño.

## 9. Preguntas al dueño

Preguntas iniciales permitidas y de bajo riesgo:

- ¿Cuál es el problema que más te preocupa hoy: caja, margen, stock, ventas o costos?
- ¿De qué período querés hablar?
- ¿Qué archivo usás para seguir ese problema?
- ¿Qué significa cada columna clave para vos?
- ¿Qué dato existe pero todavía no está en el archivo?
- ¿Querés entender un número puntual o una tendencia del negocio?
- Cuando decís “no me cierra”, ¿hablás de plata en caja, ganancia, stock o diferencia con otro registro?

Regla:

Las preguntas deben buscar **significado operativo** y **evidencia mínima**, no conversación abierta infinita.

## 10. Contrato futuro del módulo

Contrato documental futuro mínimo sugerido:

### `Service1AnamnesisRecordV1`

- `case_id`
- `owner_ref`
- `tenant_ref`
- `raw_owner_narrative`
- `declared_primary_pain`
- `business_period_reference`
- `declared_data_sources`
- `column_meaning_confirmations`
- `owner_constraints`
- `signals_detected`
- `candidate_pathology_codes`
- `owner_confirmation_required`
- `missing_evidence_items`
- `status`

### `Service1PathologyCandidateV1`

- `pathology_code`
- `pathology_label`
- `confidence_mode` (`RULE_BASED_CANDIDATE_ONLY`)
- `trigger_signals`
- `required_evidence`
- `missing_evidence`
- `allowed_microservices`
- `diagnostic_scope_limit`
- `status`

### `Service1AnamnesisTriageDecisionV1`

- `case_id`
- `selected_primary_pathology`
- `alternative_pathologies`
- `why_selected`
- `why_not_ready`
- `next_owner_questions`
- `next_allowed_computation`
- `delivery_policy_constraints`

## 11. Riesgos de deriva

Riesgos principales:

1. **Deriva conversacional**: convertir anamnesis en chatbot genérico sin cierre operativo.
2. **Deriva diagnóstica**: afirmar diagnóstico antes de reunir evidencia mínima.
3. **Deriva contable**: prometer conciliación o verdad contable definitiva sin contrato específico.
4. **Deriva de tooling**: dejar que una fórmula o microservicio defina el problema en vez del dolor del dueño.
5. **Deriva de alcance**: intentar cubrir todas las patologías PyME antes de cerrar un frente mínimo y vendible.
6. **Deriva documental**: usar lenguaje de “Servicio 1 full” o “autónomo” cuando este bloque sigue siendo asistido y XLSX-first.

## 12. Próximo paso implementable

Próximo paso implementable recomendado:

**CapabilitySpec + ModuleContract del frente `SERVICE_1_PATHOLOGY_ANAMNESIS_TRIAGE_V1`**.

Ese siguiente paso debería definir, sin abrir diagnóstico completo:

- inputs permitidos desde intake/reentry/question bundle;
- shape de `Service1AnamnesisRecordV1`;
- shape de `Service1PathologyCandidateV1`;
- reglas determinísticas mínimas para mapear narrativa/señales a 3-6 patologías candidatas;
- criterios de `OWNER_CONFIRMATION_REQUIRED` vs `EVIDENCE_REQUIRED`;
- aceptación limitada al carril XLSX asistido.

## Relación con el estado actual

Esta ADR no declara cierre de Servicio 1 ni cambia por sí sola el objetivo macro documentado en `docs/current/`.
Esta ADR no reemplaza el objetivo macro vigente definido en `docs/current/SERVICE_1_STATUS.md`; ordena únicamente el próximo sub-frente implementable del carril asistido XLSX dentro de Servicio 1.

Su función es más chica y concreta:
ordenar el **próximo bloque funcional implementable** dentro del carril asistido de Servicio 1 para evitar deriva entre intake, evidencia y diagnóstico.
