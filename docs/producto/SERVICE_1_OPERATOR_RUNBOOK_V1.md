# SERVICE_1_OPERATOR_RUNBOOK_V1

## Estado

```text
Tipo: OPERATOR_RUNBOOK
Estado: ACTIVE
Versión: V1
Runtime impact: NONE (manual protocol)
Code impact: NONE
Tests impact: NONE
```

---

## 1. Propósito

Este runbook es el protocolo operativo manual asistido para ejecutar Servicio 1 como microservicio vendible bajo supervisión humana.

No es chatbot.
No es autonomía completa.
No es pipeline automático.
No reemplaza revisión humana.
No autoriza nuevas capas prohibidas.

Su función es que un operador humano pueda ejecutar casos reales de Servicio 1 de forma repetible, segura y auditable, usando las piezas ya estabilizadas.

---

## 2. Qué es Servicio 1 hoy

```text
Servicio 1 = Microservicio Asistido de Primeros Auxilios PyME V1

Un microservicio que recibe archivos CSV/XLSX de un dueño PyME o contador,
aplica herramientas determinísticas acotadas, y devuelve un XLSX operativo
de revisión como borrador, no como dictamen.
```

Servicio 1 produce:

- archivos útiles a partir de evidencia imperfecta
- triages acotados sobre una sola fuente
- entregables operativos bajo revisión humana
- declaración explícita de faltantes y límites

Servicio 1 NO produce:

- auditoría fiscal
- conciliación definitiva
- validación contable final
- certificación
- asientos automáticos
- reemplazo del contador

---

## 3. Qué NO es Servicio 1

```text
NO es chatbot libre.
NO es LLM runtime.
NO es FSM productiva.
NO es conciliación definitiva.
NO es auditoría.
NO es certificación fiscal.
NO es cierre contable.
NO es IVA / IIBB.
NO es asientos automáticos.
NO es APIs bancarias vivas.
NO es Mercado Pago API.
NO es OCR.
NO es parser PDF automático.
NO es autonomía completa.
```

Regla madre vigente:

```text
La IA conversa.
La FSM gobierna.
Las tools ejecutan.
Los archivos son el producto.
```

En el estado actual, la FSM productiva y el LLM adapter todavía no están abiertos.

---

## 4. Precondiciones antes de aceptar un caso

```text
[ ] Cliente identificado (alias o referencia, sin datos sensibles en repo).
[ ] Responsable humano identificado (operador).
[ ] Revisor humano identificado (human_reviewer, obligatorio).
[ ] Problema expresado registrado.
[ ] Caso pertenece a una familia soportada:
    - ventas_declaradas_vs_cobros_declarados
    - compras_declaradas_vs_pagos_declarados
    - First Aid: precio_margen, caja_diaria, stock_alertas, gastos_triage, proveedores_triage
[ ] Alcance acotado a un período o recorte explícito.
[ ] Archivos tabulares válidos (CSV o XLSX) o archivo base suficiente.
[ ] Evidencia marcada como declarada, no auditada.
[ ] No se recibieron credenciales, claves fiscales, tokens ni accesos vivos.
[ ] No se pidieron APIs bancarias, Mercado Pago API ni Mercado Libre API.
[ ] El caso no exige auditoría, certificación, validación fiscal ni conciliación definitiva.
[ ] El caso no requiere OCR ni parser automático nuevo.
```

Si alguna precondición falla: recortar alcance, pedir evidencia mínima o bloquear.

---

## 5. Flujo operativo manual asistido

### 5.1 Intake

```text
1. Recibir archivos del cliente (CSV/XLSX).
2. Registrar archivos en carpeta de caso local (fuera del repo).
3. Confirmar extensión (.csv / .xlsx).
4. Registrar cliente_alias, período, problema expresado.
5. No commitear archivos reales al repo.
```

Ruta recomendada:

```text
E:\BuenosPasos\smartbridge\PymIA-local-artifacts\service_1_cases\<CASE_ID>\
```

### 5.2 Scope

```text
1. Aplicar SERVICE_1_REAL_CLIENT_OPERATOR_PACKET_V1.
2. Confirmar familia soportada.
3. Confirmar período definido.
4. Confirmar alcance acotado.
5. Si el caso es demasiado amplio, recortar o bloquear.
```

### 5.3 Evidencia

```text
1. Registrar evidencia como declarada, no auditada.
2. Listar archivos recibidos.
3. Listar archivos faltantes conocidos.
4. No inventar evidencia.
5. No completar cobros, pagos, proveedores, CUIT, fechas o referencias sin fuente.
6. Separar evidencia declarada de inferencia.
```

### 5.4 Ejecución operator harness

```text
1. Crear case folder manifest.
2. Aplicar operator runbook y edge-case rules.
3. Si aplica First Aid: ejecutar via CLI:
   python -m pymia.cli.service_1_operator \
     --file <path> \
     --confirmed-columns <json> \
     --run-tools <json>
4. Si aplica Factoría Excel: ejecutar via CLI:
   python -m pymia.cli.service_1_operator \
     --run-factory \
     --template-ref <ref> \
     --formula-ref <ref> \
     --factory-input key=value \
     --factory-output <path>
5. Si aplica NormalizedTableV1: usar CSV adapter o XLSX adapter.
6. Registrar operator_notes.md con observaciones.
```

### 5.5 Generación delivery package

```text
1. Generar XLSX operativo de revisión (fuera del repo).
2. Generar README_ENTREGA.md.
3. Generar manifest.json con inventario.
4. Generar summary.txt.
5. Generar operator_report.txt.
6. Generar hashes sha256 de cada archivo.
7. No commitear la carpeta de entrega al repo.
```

### 5.6 QA checklist

```text
Aplicar SERVICE_1_QA_DELIVERY_CHECKLIST_V1:
- intake completo
- alcance acotado
- archivos tabulares válidos
- columnas mínimas identificadas o confirmadas
- evidencia declarada separada de inferencia
- diferencias visibles registradas
- faltantes de evidencia registrados
- XLSX operativo revisado
- mensaje owner-facing revisado
- paquete operador revisado
- human review gate aplicado
- claims prohibidos ausentes
- stop conditions no activadas
- próxima acción segura indicada
```

### 5.7 Delivery manifest audit

```text
Aplicar SERVICE_1_DELIVERY_MANIFEST_AUDIT_V1:
- manifest presente
- case_id existe
- período definido
- familia soportada o alcance reducido
- operador identificado
- human reviewer identificado
- QA checklist pasada
- owner message presente
- evidence gap log presente
- visible differences log presente
- forbidden claims check pasada
- stop_conditions = NONE
- delivery status correcto
- next safe action existe
```

### 5.8 Human review gate

```text
1. Confirmar responsable humano identificado.
2. Confirmar revisión humana requerida explícitamente.
3. Verificar que el entregable no se marca como final sin revisión.
4. Verificar ausencia de claims prohibidos.
5. Verificar que las advertencias operativas estén visibles.
6. Verificar que los faltantes no hayan sido inferidos.
7. Verificar que el caso pueda salir como borrador operativo.
```

### 5.9 Entrega como borrador operativo

```text
Entregar al cliente solo si:
- todos los checks críticos están completos
- no hay stop conditions activadas
- el output dice "borrador operativo"
- el output dice "evidencia declarada"
- el output dice "requiere revisión humana"
- el responsable humano está identificado
- la próxima acción segura está indicada
```

Lenguaje obligatorio en mensaje owner-facing:

```text
borrador operativo
evidencia declarada
diferencias visibles
faltantes de evidencia
advertencias operativas
requiere revisión humana
XLSX operativo de revisión
```

---

## 6. Comandos disponibles ya existentes

```text
First Aid (5 tools):
python -m pymia.cli.service_1_operator \
  --file <path> \
  --confirmed-columns <json> \
  --run-tools <json>

Factoría Excel:
python -m pymia.cli.service_1_operator \
  --run-factory \
  --template-ref <ref> \
  --formula-ref <ref> \
  --factory-input key=value \
  --factory-output <path>

Templates mapeados:
- precio_margen_basico_template -> precio_margen
- caja_diaria_template -> caja_diaria
- stock_alertas_basicas_template -> stock_control

Tools First Aid:
- precio_margen_basico
- caja_diaria_triage
- stock_alertas_basicas
- gastos_triage
- proveedores_precio_variacion_triage

Adapters NormalizedTableV1:
- service_1_csv_to_normalized_table_v1.read_csv_to_normalized_table_v1()
- service_1_xlsx_to_normalized_table_v1.read_xlsx_to_normalized_table_v1()
```

---

## 7. Artefactos generados

```text
Carpeta de caso (fuera del repo):
- input files (CSV/XLSX originales)
- output XLSX operativo de revisión
- case_manifest.md
- operator_notes.md
- evidence_gap_log.md
- visible_differences_log.md
- owner_message.md
- qa_checklist_result.md
- delivery_manifest_audit_result.md
- README_ENTREGA.md
- manifest.json
- summary.txt
- operator_report.txt
- hashes sha256
- post_delivery_review.md (si aplica)
```

Nunca commitear al repo:

```text
- service_1_cases/
- real client folders
- XLSX inputs
- XLSX outputs
- sensitive evidence
- scratch scripts
- delivery artifacts con datos reales
```

---

## 8. Checklist de bloqueo

Bloquear entrega si:

```text
[ ] Falta responsable humano.
[ ] Falta evidencia mínima.
[ ] El caso excede alcance y no puede recortarse.
[ ] El cliente pide auditoría.
[ ] El cliente pide certificación.
[ ] El cliente pide validación fiscal.
[ ] El cliente pide conciliación definitiva.
[ ] El cliente pide asientos automáticos.
[ ] El cliente pide resultado contable final.
[ ] El cliente espera reemplazo del contador.
[ ] Aparecen APIs vivas como requisito.
[ ] Aparece OCR como requisito.
[ ] Aparece parser automático nuevo como requisito.
[ ] El XLSX puede interpretarse como dictamen.
[ ] No hubo revisión humana cuando era obligatoria.
[ ] Se inventó evidencia o se completaron faltantes sin fuente.
[ ] Forbidden claims detectados en el output.
[ ] QA checklist no pasó.
[ ] Delivery manifest audit no pasó.
[ ] stop_conditions != NONE.
```

---

## 9. Checklist de entrega

Puede salir si:

```text
[ ] Intake completo para alcance aceptado.
[ ] Alcance acotado.
[ ] Archivos tabulares suficientes para borrador operativo.
[ ] Columnas mínimas identificadas o confirmadas.
[ ] Evidencia declarada e inferencia separadas.
[ ] Diferencias visibles registradas.
[ ] Faltantes de evidencia registrados.
[ ] XLSX operativo revisado.
[ ] Mensaje owner-facing revisado.
[ ] Paquete operador revisado.
[ ] Human review gate aplicado.
[ ] Claims prohibidos ausentes.
[ ] Stop conditions no activadas.
[ ] Próxima acción segura indicada.
[ ] QA checklist pasada.
[ ] Delivery manifest audit pasada.
[ ] Human reviewer identificado.
[ ] Output dice "borrador operativo".
[ ] Output dice "evidencia declarada".
[ ] Output dice "requiere revisión humana".
```

---

## 10. Fronteras prohibidas

```text
NO abrir chatbot.
NO abrir LLM adapter.
NO reactivar FSM congelada.
NO abrir pipeline full.
NO abrir Servicio 2.
NO agregar APIs externas.
NO agregar OCR.
NO agregar parser PDF.
NO mezclar First Aid con diagnóstico contable.
NO afirmar conciliación real productiva.
NO afirmar Mercado Pago runtime.
NO afirmar PDF intake productivo.
NO usar Factoría Excel como owner-facing delivery final automático.
NO mover fórmulas activas al delivery genérico.
NO declarar Servicio 1 full.
```

---

## 11. Criterio PASS / BLOCKED / NEEDS_EVIDENCE

```text
PASS:
- todas las precondiciones cumplidas
- QA checklist pasada
- delivery manifest audit pasada
- human review gate aplicado
- forbidden claims ausentes
- stop_conditions = NONE
- output marcado como borrador operativo
- próxima acción segura indicada

BLOCKED:
- alguna stop condition activa
- forbidden claims detectados
- evidencia mínima faltante
- human reviewer faltante
- QA checklist no pasada
- delivery manifest audit no pasada
- alcance no soportado y no reducible
- cliente pide auditoría/certificación/fiscalidad/conciliación definitiva

NEEDS_EVIDENCE:
- evidencia declarada incompleta pero documentada
- faltantes de evidencia registrados
- caso puede proceder como borrador parcial con advertencias
- requiere confirmación humana de alcance reducido
```

---

## 12. Post-delivery review mínima

Después de cada entrega:

```text
[ ] Registrar post_delivery_review.md con:
    - case_id
    - familia
    - período
    - resultado (PASS / PASS_WITH_WARNINGS / NEEDS_SCOPE_REDUCTION / BLOCKED)
    - advertencias observadas
    - faltantes de evidencia documentados
    - comportamiento de edge cases
    - decisión humana final
    - próxima acción segura indicada al cliente
[ ] No commitear el post_delivery_review con datos reales.
[ ] Mantener como archivo operativo fuera del repo.
[ ] Si surge aprendizaje transversal, actualizar docs/producto correspondiente.
```

---

## Firma

- Documento creado en modo `DOC ONLY`.
- Sin modificación de runtime, tests, CLI, pipeline ni memoria.
- Referencia documentos existentes sin duplicarlos.
- Próxima acción segura: `RUN_FIRST_REAL_CLIENT_CASE_UNDER_OPERATOR_SUPERVISION`.
