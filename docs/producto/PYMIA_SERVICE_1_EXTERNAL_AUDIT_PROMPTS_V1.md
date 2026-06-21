# PYMIA_SERVICE_1_EXTERNAL_AUDIT_PROMPTS_V1

## Estado

```text
Tipo: EXTERNAL_AUDIT_PROMPTS
Estado: DRAFT_APPLIED
Runtime impact: NONE
Code impact: NONE
Tests impact: NONE
```

## Propósito

Conservar prompts listos para auditar con otras IA el plan de implementación e integración de PymIA Servicio 1.

Documento base a auditar:

```text
docs/producto/PYMIA_SERVICE_1_IMPLEMENTATION_INTEGRATION_PLAN_V1.md
```

Documentos relacionados:

```text
docs/producto/FIRST_AID_TOOLBOX_ARCHAEOLOGY_EXCELAND_V1.md
docs/producto/FIRST_AID_TOOLBOX_PACK_CONTRACT_V1.md
PymIA-Live/docs/pymia/first_aid_toolbox_candidates/
```

---

# PROMPT 1 — Auditoría arquitectónica dura

```text
Actúa como auditor arquitectónico senior de software/producto.

Contexto:
Estamos construyendo PymIA Servicio 1.
Servicio 1 no es un MVP mutilado. Es una línea completa de producto que debe implementarse incrementalmente.

Definición de Servicio 1:
Laboratorio Operacional de Datos, Excel y Contabilidad
+ Primeros Auxilios
+ Laboratorio Excel
+ Factoría Excel
+ Excel descargables con fórmulas
+ Servicios para contadores
+ Conciliaciones
+ PDF/CSV/Excel a Excel normalizado
+ Chatbot operativo con IA bajo arnés

Documentos a revisar:
- docs/producto/PYMIA_SERVICE_1_IMPLEMENTATION_INTEGRATION_PLAN_V1.md
- docs/producto/FIRST_AID_TOOLBOX_ARCHAEOLOGY_EXCELAND_V1.md
- docs/producto/FIRST_AID_TOOLBOX_PACK_CONTRACT_V1.md
- PymIA-Live/docs/pymia/first_aid_toolbox_candidates/

Reglas:
AUDIT ONLY.
No código.
No tests.
No commits.
No proponer arquitectura nueva si la existente alcanza.
No achicar el producto.
No mezclar Servicio 1 con Servicio 2/3.
No recomendar multiagentes, WhatsApp, Telegram ni canales todavía.
No autorizar runtime si falta contrato.

Auditar:
1. Si el plan respeta la regla: Exceland = cantera; PymIA-Live = sistema operativo.
2. Si evita contaminación del kernel.
3. Si el orden pack seed -> loader -> activación -> tools -> XLSX delivery es correcto.
4. Si service_1_pipeline.py conviene más que seguir cargando vertical_pipeline.py.
5. Si hay pasos faltantes antes de implementar runtime.
6. Si hay riesgos de deriva tipo Hermes.
7. Si el uso de IA queda correctamente limitado.
8. Si las fronteras entre documentación, contrato, loader, activación, ejecución y delivery están limpias.

Responder con este formato:

VEREDICTO:
APPROVE / APPROVE_WITH_CHANGES / REJECT

CRITICAL_FINDINGS:
- ...

ARCHITECTURAL_RISKS:
- ...

MISSING_GUARDS:
- ...

ORDER_CORRECTION:
si el orden propuesto debe cambiar, indicar orden corregido.

FILES_THAT_SHOULD_EXIST:
- path: propósito

FILES_THAT_SHOULD_NOT_BE_TOUCHED_YET:
- path: motivo

NEXT_SAFE_STEP:
una sola acción concreta.

FINAL_NOTE:
breve, sin entusiasmo artificial.
```

---

# PROMPT 2 — Auditoría de producto y mercado

```text
Actúa como auditor de producto B2B para servicios operativos con archivos, Excel y contabilidad para PyMEs/contadores.

Contexto:
PymIA Servicio 1 busca ser una línea de producto vendible basada en archivos útiles: Excel normalizados, conciliaciones, papeles de trabajo, plantillas operativas, reportes y entregables descargables.

No debe venderse como “IA genérica”.
Debe vender resultados operativos concretos.

Documento a revisar:
- docs/producto/PYMIA_SERVICE_1_IMPLEMENTATION_INTEGRATION_PLAN_V1.md

Documentos relacionados:
- docs/producto/FIRST_AID_TOOLBOX_ARCHAEOLOGY_EXCELAND_V1.md
- docs/producto/FIRST_AID_TOOLBOX_PACK_CONTRACT_V1.md

Reglas:
AUDIT ONLY.
No código.
No tests.
No commits.
No rediseñar todo.
No achicar visión.
No convertirlo en SaaS genérico.
No vender IA como producto principal.

Auditar:
1. Si Servicio 1 queda vendible como línea de producto.
2. Si el catálogo inicial cubre dolores reales de PyMEs/contadores.
3. Si First Aid + Factoría Excel + servicios contables tienen coherencia comercial.
4. Si faltan paquetes vendibles concretos.
5. Si la secuencia técnica permite llegar a entregables vendibles.
6. Si XLSX delivery aparece suficientemente temprano.
7. Si se está subestimando PDF/CSV/Excel normalizado.
8. Si el roadmap preserva diferenciación contra IA genérica tipo “creame un Excel”.

Responder:

VEREDICTO_PRODUCTO:
STRONG / PARTIAL / WEAK

SELLABLE_PACKAGES_RECOMMENDED:
- nombre:
  cliente:
  input:
  output:
  precio/valor sugerido si aplica:

PRODUCT_GAPS:
- ...

OVERENGINEERING_RISKS:
- ...

UNDERENGINEERING_RISKS:
- ...

FIRST_3_PACKAGES_TO_SELL:
1.
2.
3.

NEXT_PRODUCT_ACTION:
una sola acción concreta.
```

---

# PROMPT 3 — Auditoría técnica de implementación incremental

```text
Actúa como tech lead Python responsable de convertir documentación en implementación incremental segura.

Contexto:
Existe PymIA-Live. Ya hay vertical pipeline, structured evidence, column confirmation, owner report, service depth, case replay y documentos First Aid.

Queremos implementar Servicio 1 sin contaminar kernel y sin abrir demasiado scope.

Documento principal:
- docs/producto/PYMIA_SERVICE_1_IMPLEMENTATION_INTEGRATION_PLAN_V1.md

Documentos de referencia:
- docs/producto/FIRST_AID_TOOLBOX_ARCHAEOLOGY_EXCELAND_V1.md
- docs/producto/FIRST_AID_TOOLBOX_PACK_CONTRACT_V1.md
- PymIA-Live/docs/pymia/first_aid_toolbox_candidates/

Reglas:
AUDIT ONLY.
No modificar código.
No correr tests.
No commits.
No inventar módulos si ya existen equivalentes.
No recomendar refactor masivo.
No tocar vertical_pipeline.py salvo que sea estrictamente necesario.

Auditar:
1. Qué archivos existentes deberían revisarse antes de implementar.
2. Si los paths propuestos son correctos.
3. Si first_aid_toolbox_pack_v1.py debe vivir en contracts o smartpyme.
4. Si el seed debe ser JSON, YAML o ambos.
5. Si el loader debe devolver dataclasses/Pydantic/plain dict.
6. Si la activación debe vivir en smartpyme o application.
7. Qué tests mínimos aceptarían cada ciclo.
8. Qué fixtures usar para precio/margen, caja y stock.
9. Qué no tocar todavía.

Responder:

VEREDICTO_TECNICO:
APPROVE / APPROVE_WITH_CHANGES / REJECT

PRE_IMPLEMENTATION_READ_LIST:
- path: por qué leerlo

PROPOSED_FILE_LAYOUT:
- path: responsabilidad

TEST_PLAN_BY_CYCLE:
CYCLE | TEST FILE | ASSERTIONS

RISKY_FILES:
- path: riesgo

DO_NOT_TOUCH:
- path: motivo

FIRST_IMPLEMENTATION_SLICE:
objetivo:
files_new:
files_modified:
tests:
acceptance_criteria:

FINAL_RECOMMENDATION:
una sola recomendación.
```

---

# PROMPT 4 — Auditoría de límites de IA / arnés

```text
Actúa como auditor de sistemas con IA bajo control determinístico.

Contexto:
PymIA Servicio 1 puede usar IA para conversación, clasificación, specs y explicación, pero no para ejecutar cálculos críticos ni generar archivos opacos.

Regla rectora:
La IA conversa.
La FSM gobierna.
Las tools ejecutan.
Los archivos son el producto.

Documento a revisar:
- docs/producto/PYMIA_SERVICE_1_IMPLEMENTATION_INTEGRATION_PLAN_V1.md

Reglas:
AUDIT ONLY.
No código.
No tests.
No commits.
No proponer agente autónomo.
No proponer multiagente.
No proponer canales externos.
No habilitar IA para claims finales.

Auditar:
1. Si la IA queda limitada a TaskSpec, EvidenceRequest, OwnerQuestion, ExcelSpec y ExplanationDraft.
2. Si falta contrato para ExcelSpec.
3. Si falta validación antes de XLSX delivery.
4. Si hay riesgo de que la IA calcule o concilie indirectamente.
5. Si la FSM propuesta tiene estados suficientes.
6. Si falta traza/historial para explicar decisiones.
7. Si los claims owner-facing están suficientemente controlados.

Responder:

VEREDICTO_IA:
SAFE / SAFE_WITH_GUARDS / UNSAFE

AI_ALLOWED_ACTIONS:
- ...

AI_FORBIDDEN_ACTIONS:
- ...

MISSING_CONTRACTS:
- ...

FSM_GAPS:
- ...

TRACEABILITY_REQUIREMENTS:
- ...

RECOMMENDED_GUARDS_BEFORE_LLM:
1.
2.
3.

NEXT_SAFE_STEP:
una sola acción concreta.
```

---

# PROMPT 5 — Auditoría de documentación y continuidad

```text
Actúa como auditor documental de repo.

Contexto:
PymIA tiene mucha documentación histórica. Debemos evitar dispersión, duplicación y pérdida de decisiones. El usuario prohibió dejar información valiosa tirada en chats.

Documentos a revisar:
- docs/producto/PYMIA_SERVICE_1_IMPLEMENTATION_INTEGRATION_PLAN_V1.md
- docs/producto/FIRST_AID_TOOLBOX_ARCHAEOLOGY_EXCELAND_V1.md
- docs/producto/FIRST_AID_TOOLBOX_PACK_CONTRACT_V1.md
- PYMIA_SERVICE_1_ROADMAP_CICLOS_MADUREZ_V1.md si está disponible
- DOCUMENTATION_INDEX.md si existe
- Pymia-memoria/_estado_actual.md
- Pymia-memoria/_task_actual.md
- Pymia-memoria/_decisiones_vigentes.md

Reglas:
AUDIT ONLY.
No código.
No tests.
No commits.
No escribir documentación nueva.
No reordenar archivos.

Auditar:
1. Si el nuevo plan debe indexarse en DOCUMENTATION_INDEX.md.
2. Si debe reflejarse en memoria PymIA.
3. Si duplica otro documento existente.
4. Si contradice alguna decisión vigente.
5. Si está en la carpeta correcta.
6. Qué documento debería ser fuente maestra de Servicio 1.
7. Qué documentos quedan subordinados.

Responder:

VEREDICTO_DOCS:
INDEX_READY / NEEDS_CHANGES / DUPLICATED / CONFLICT

MASTER_DOC_RECOMMENDED:
path:
reason:

DOCS_TO_INDEX:
- path: razón

MEMORY_UPDATES_REQUIRED:
- file:
  update_summary:

DUPLICATES_OR_OVERLAPS:
- doc_a:
  doc_b:
  action:

CONFLICTS:
- ...

NEXT_DOC_ACTION:
una sola acción concreta.
```

---

# Uso recomendado

```text
1. Enviar primero PROMPT 1 a Qwen.
2. Enviar PROMPT 3 a una IA fuerte en código.
3. Enviar PROMPT 5 para cierre documental.
4. Usar PROMPT 2 sólo si se quiere validar producto/mercado.
5. Usar PROMPT 4 antes de abrir cualquier LLM adapter.
```

No ejecutar implementación hasta tener al menos:

```text
- auditoría arquitectónica aprobada o aprobada con cambios
- auditoría técnica con primer slice claro
- auditoría documental indicando index/memoria
```
