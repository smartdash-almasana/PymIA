# Servicio 1 — Estado de ingeniería de conciliación V1

**Estado:** CHECKPOINT TÉCNICO — MATCHER, CASO FÍSICO Y MERCADO PAGO CERRADOS  
**Propósito:** consolidar la evidencia técnica y las decisiones arquitectónicas obtenidas durante la auditoría de conciliación, evitando que queden como memoria conversacional.  
**Alcance:** conciliación existente en PymIA; no autoriza por sí mismo promoción a runtime productivo.

## 1. Conclusión ejecutiva

PymIA ya contiene patrimonio técnico de conciliación. No corresponde crear un `reconciliation_core_v1` paralelo ni tratar conciliación como greenfield.

La raíz productiva de Servicio 1 sigue siendo:

```text
pymia/smartpyme/service_1_product_pipeline_v1.py
```

La conciliación existente está distribuida entre contratos contables, contratos de dominio, matcher determinístico, revisión asistida, delivery y sandbox. Actualmente no está integrada como capacidad productiva dentro de la raíz canónica de Servicio 1.

La dirección aprobada es **madurar el matcher existente antes de integrar nuevas fuentes, APIs o IA**.

---

## 2. Patrimonio de conciliación existente

Piezas relevantes identificadas:

```text
pymia/smartpyme/service_1_accounting_contracts_v1.py
pymia/smartpyme/bank_reconciliation_contract_v1.py
pymia/smartpyme/mercado_pago_reconciliation_contract_v1.py
pymia/smartpyme/invoice_collection_matching_contract_v1.py
pymia/smartpyme/supplier_purchase_review_contract_v1.py

pymia/smartpyme/service_2_reconciliation_match_candidates_v1.py
pymia/smartpyme/service_2_mercado_pago_bank_reconciliation_v1.py
pymia/smartpyme/service_2_reconciliation_assisted_review_block_v1.py
pymia/smartpyme/service_2_reconciliation_assisted_review_delivery_packet_v1.py

pymia/smartpyme/bank_reconciliation_sandbox_*
pymia/smartpyme/invoice_collection_matching_sandbox_completion_slice_v1.py

pymia/smartpyme/accounting_workpaper_*
```

### Clasificación conceptual

- `service_1_accounting_contracts_v1.py`: base contractual y validación contable.
- contratos `bank`, `mercado_pago`, `invoice_collection`, `supplier_purchase`: contratos de dominio; no equivalen a matching ejecutado.
- `service_2_reconciliation_match_candidates_v1.py`: autoridad algorítmica general del matching existente.
- `service_2_mercado_pago_bank_reconciliation_v1.py`: especialización determinística que verifica neto Mercado Pago, agrupa por lote y reutiliza el matcher general; no constituye un segundo núcleo.
- `service_2_reconciliation_assisted_review_block_v1.py`: consumidor inmediato del matcher y capa de revisión humana.
- `service_2_reconciliation_assisted_review_delivery_packet_v1.py`: legado/deprecado.
- sandboxes: evidencia y soporte de prueba; no autoridad runtime productiva.
- workpapers: soporte contable; fuera del primer cambio.

La existencia de un módulo y sus tests no implica que sea autoridad productiva.

---

## 3. Frontera actual Servicio 1 / Servicio 2

Existe una frontera histórica no resuelta:

```text
Servicio 1
-----------
ingesta XLSX
comprensión semántica
confirmación del dueño
cálculo determinístico
hallazgo trazable

Conciliación existente
----------------------
contratos contables
matcher de candidatos S2
revisión asistida
sandbox
```

Hechos relevantes:

- `service_1_product_pipeline_v1.py` no invoca actualmente el matcher de conciliación.
- `service_1_capability_registry_v1.py` no registra todavía conciliación como capacidad productiva.
- los contratos contables de dominio usan componentes `service_1_*`.
- el matcher y la revisión asistida usan prefijo y referencia de `service_2_*`.

Por lo tanto, **no se autoriza aún una migración S2→S1 ni una integración a la raíz productiva**. Primero debe madurarse la semántica del matching.

---

## 4. Hallazgos del matcher actual

Archivo:

```text
pymia/smartpyme/service_2_reconciliation_match_candidates_v1.py
```

### 4.1 Fecha + importe no demuestran identidad

El comportamiento actual considera fuerte la coincidencia:

```text
misma fecha
+
mismo importe
```

Eso no basta para afirmar que dos registros representan el mismo hecho económico.

Nueva distinción conceptual:

```text
IDENTIDAD
COINCIDENCIA DE ATRIBUTOS
CANDIDATO
AMBIGÜEDAD
SIN CONTRAPARTE
EVIDENCIA INSUFICIENTE
```

### 4.2 La referencia se normaliza pero no gobierna el matching

`referencia` existe en el movimiento normalizado, pero el matcher actual no la utiliza para comparar.

La referencia debe incorporarse como **evidencia de identidad**, no como autoridad absoluta.

Una referencia coincidente no puede forzar un match si contradice evidencia material, por ejemplo un importe incompatible.

### 4.3 Colisiones 1:N / N:1 / N:M

El matcher compara movimientos mediante bucles par-a-par y puede generar múltiples supuestos matches para el mismo movimiento.

Ejemplo:

```text
Banco B1    $10.000
Interno I1  $10.000
Interno I2  $10.000
```

No corresponde:

```text
B1 ↔ I1 exacto
B1 ↔ I2 exacto
```

Ni tampoco resolver por orden de recorrido.

Debe producirse ambigüedad explícita y revisión humana.

### 4.4 No usar matching codicioso

Un movimiento no debe ser “consumido” simplemente porque aparece primero como candidato.

La resolución futura debe respetar cardinalidades:

```text
1:1
1:N
N:1
N:M
```

sin esconder candidatos competidores.

### 4.5 Diferencia de importe no equivale a contraparte encontrada

Hoy una coincidencia de fecha con diferencia de importe puede marcar ambos índices como candidatos y quitar movimientos de las listas de no imputados.

Debe mantenerse la distinción:

```text
POSSIBLE_RELATION
!=
COUNTERPART_CONFIRMED
```

Un movimiento puede figurar simultáneamente como parte de una diferencia analizable y continuar sin imputación confirmada.

### 4.6 Confidence scores arbitrarios

El matcher actual contiene valores como:

```text
confianza_exacta = 1.0
confianza_probable_minima = 0.6
```

Estos valores no deben actuar como autoridad ni como probabilidad contable.

Dirección:

```text
evidencia explícita
+
tipo discreto
+
revisión humana cuando corresponda
```

Ejemplo de evidencia:

```text
reference_match: true
amount_match: true
amount_delta: 0
date_match: false
date_delta_days: 1
candidate_count: 1
```

Los scores probabilísticos, si existieran en el futuro, sólo podrán servir para ruteo o priorización y nunca para autoaceptación financiera/fiscal.

---

## 5. Estados de matching: dirección aprobada

No se autoriza todavía un contrato V2 global definitivo.

El primer incremento debe evolucionar el matcher hacia estados/categorías discretas equivalentes a:

```text
MATCH_REFERENCE_EXACT
MATCH_ATTRIBUTES_EXACT
MATCH_PROBABLE_DATE
AMBIGUOUS
NO_MATCH
INSUFFICIENT_EVIDENCE
```

Los nombres finales se fijarán en código y tests durante el incremento.

Una ambigüedad no debe resolverse con LLM ni con orden de iteración.

---

## 6. Revisión humana

La revisión humana sigue siendo obligatoria en la capacidad existente.

Regla:

```text
caso determinístico suficientemente evidenciado
→ candidato fuerte / resultado auditable

ambigüedad
→ revisión humana

evidencia insuficiente
→ abstención / solicitud de evidencia
```

La revisión humana es mecanismo formal de resolución, no permiso para inventar hechos.

---

## 7. Rol del LLM

Para este ciclo:

```text
NO LLM
```

No se autoriza:

- matching mediante LLM;
- cálculo contable por LLM;
- decisión de conciliación por LLM;
- mutación de estado financiero;
- fijación de tolerancias;
- resolución autónoma de ambigüedad.

La doctrina general de inteligencia híbrida se mantiene separada de este incremento.

---

## 8. Knowledge packs

Existe trabajo separado de banco de conocimiento operativo.

Reglas:

- no duplicar conocimiento ya modelado;
- no convertir knowledge packs en un segundo ERP;
- no almacenar transacciones empresariales dentro del banco de conocimiento;
- no convertir conocimiento declarativo en autoridad runtime por mera existencia;
- mantener procedencia, versión, evidencia y límites de interpretación.

La integración de knowledge packs con conciliación queda fuera del primer incremento del matcher.

---

## 9. Evidencia de tests

### Matcher focal

```text
tests/smartpyme/test_service_2_reconciliation_match_candidates_v1.py
17 passed
0 failed
```

### Matcher + casos físicos

```text
tests/smartpyme/test_service_2_reconciliation_match_candidates_v1.py
tests/smartpyme/test_service_2_reconciliation_physical_cases_v1.py
21 passed
0 failed
```

### Mercado Pago ↔ banco

```text
tests/smartpyme/test_service_2_mercado_pago_bank_reconciliation_v1.py
6 passed
0 failed
```

El fixture físico:

```text
prueba_excels/conciliacion_mercado_pago_banco_corregida.xlsx
```

es procesado por PymIA mediante:

```text
importe_bruto - comision - retencion = importe_neto
→ agrupación por lote
→ movimientos sintéticos auditables
→ matcher general
→ expansión a operaciones y acreditaciones originales
```

Resultado observado del fixture:

```text
10 conciliaciones
1 diferencia de importe
2 ambigüedades
1 operación MP sin acreditación
1 movimiento bancario sin operación MP
```

Dos rótulos del `CASO_ESPERADO` no son distinguibles por la evidencia disponible: `CASO-06` y `CASO-10` presentan la misma estructura económica y documental. PymIA no inventa una diferencia semántica y clasifica ambos como `COINCIDENCIA_LOTE`.

### Regresión amplia de conciliación

```text
15 archivos focales
148 tests
148 passed
0 failed
0 skipped
```

### Fixture físico gobernado

```text
prueba_excels/conciliacion_pyme_argentina_corregida.xlsx
```

Hojas verificadas:

```text
VENTAS
COBROS
BANCO
CASO_ESPERADO
```

`CASO_ESPERADO` funciona como ground truth ejecutable para:

```text
MATCH_REFERENCE_EXACT
MATCH_ATTRIBUTES_EXACT
AMBIGUOUS 1:N
AMBIGUOUS N:1
AMBIGUOUS N:M
NO_MATCH
no imputados
diferencia de importe
```

El caso físico detectó y cerró además dos problemas que la prueba unitaria aislada no exponía:

- ruido combinatorio de diferencias de importe entre operaciones de igual fecha pero sin relación suficiente;
- fecha almacenada como serial Excel dentro de una fila del fixture, normalizada en la frontera de lectura del test.

Esto prueba regresión verde en las suites ejecutadas; **no debe describirse como 100% de cobertura de código** sin una medición específica de coverage.

---

## 10. Decisiones arquitectónicas cerradas

```text
NO nuevo reconciliation_core_v1 paralelo
NO uncertainty_resolution_v1 global
NO event bus
NO colas
NO microservicios nuevos
NO LLM en este ciclo
NO matching codicioso
NO confidence float como autoridad
NO integración productiva S1/S2 todavía
NO APIs todavía
NO modificación del sandbox en el primer incremento
```

Sí:

```text
madurar matcher existente
hacer explícita la evidencia
hacer explícita la ambigüedad
preservar no imputados hasta identidad suficiente
mantener determinismo
mantener revisión humana
mantener trazabilidad
```

---

## 11. Primer incremento ejecutado

### Archivos

```text
pymia/smartpyme/service_2_reconciliation_match_candidates_v1.py
tests/smartpyme/test_service_2_reconciliation_match_candidates_v1.py
```

### Objetivo

Pasar de:

```text
fecha + importe
→ exacto/probable
→ confidence
```

a:

```text
evidencias de identidad
→ candidatos
→ análisis de cardinalidad
→ tipo discreto
→ ambigüedad explícita cuando corresponda
```

### Casos mínimos nuevos

1. referencia priorizada frente a dos candidatos con misma fecha/monto;
2. colisión 1:N genera ambigüedad explícita;
3. diferencia de importe no oculta movimiento sin imputar;
4. salida sin float confidence como autoridad;
5. N:M expone cantidad/candidatos ambiguos.

### Compatibilidad del primer incremento

Para mantener acotado el cambio, la existencia de ambigüedad puede seguir produciendo:

```text
status = PARTIAL_MATCHES_FOUND
```

mientras se agrega una colección explícita de candidatos ambiguos.

El matcher se cerró primero de forma focal. En el incremento inmediatamente posterior, `service_2_reconciliation_assisted_review_block_v1.py` fue adaptado para exponer `matches_ambiguos`, su cardinalidad y la necesidad de revisión humana.

### Resultado observado

```text
17 passed — matcher focal
21 passed — matcher + primer caso físico
6 passed — especialización Mercado Pago ↔ banco
148 passed — regresión amplia de conciliación
0 failed
0 skipped
```

---

## 12. Fuera de alcance del primer incremento

No tocar:

```text
pymia/smartpyme/service_1_product_pipeline_v1.py
pymia/smartpyme/service_1_accounting_contracts_v1.py
pymia/smartpyme/service_1_capability_registry_v1.py
bank_reconciliation_contract_v1.py
mercado_pago_reconciliation_contract_v1.py
invoice_collection_matching_contract_v1.py
supplier_purchase_review_contract_v1.py
bank_reconciliation_sandbox_*
accounting_workpaper_*
```

Tampoco:

```text
Mercado Libre API
Mercado Pago API
ARCA
PDF/OCR
WhatsApp
LLM
optimización
clasificadores ML
```

---

## 13. Dirección posterior

Estado de la secuencia:

```text
1. suite amplia de conciliación: COMPLETADA
2. ambigüedad expuesta en revisión humana: COMPLETADA
3. caso físico venta ↔ cobro ↔ banco: COMPLETADO
4. segundo caso Mercado Pago ↔ banco: COMPLETADO
5. puente gobernado con Servicio 1: LISTO PARA EVALUACIÓN, NO IMPLEMENTADO
6. abstracción transversal: BLOQUEADA HASTA DEFINIR EL PUENTE MÍNIMO
```

El próximo incremento no debe crear una segunda raíz. Debe definir el contrato mínimo de entrada/salida para que Servicio 1 pueda solicitar esta conciliación sin absorber autoridad contable ni romper la revisión humana.

---

# CURRENT_AUTHORITY

```text
pymia/smartpyme/service_1_product_pipeline_v1.py
pymia/cli/service_1_product.py
docs/current/README.md
docs/current/SERVICE_1_STATUS.md
docs/current/SERVICE_1_CANONICAL_AXIS.md
docs/current/SERVICE_1_DETERMINISTIC_SEMANTIC_PIPELINE_ENGINEERING_METHOD_V1.md
```

La conciliación existente no reemplaza esta autoridad.

# TARGET_DIRECTION

```text
Servicio 1
→ comprender hechos empresariales
→ evidenciarlos
→ relacionarlos
→ conciliarlos cuando corresponda
→ calcular/controlar
→ producir hallazgos trazables
```

Excel permanece como fuente importante, pero no define por sí solo la identidad futura del producto.

# NEXT_IMPLEMENTATION_SLICE

```text
GOAL:
definir el contrato mínimo de entrada/salida para un puente gobernado con Servicio 1

ENTRADA:
operaciones MP normalizadas + movimientos bancarios normalizados + confirmaciones del dueño cuando falte identidad

SALIDA:
conciliaciones candidatas + diferencias + ambigüedades + no imputados + evidencia explícita

RESTRICCIONES:
NO autoaceptación contable
NO LLM
NO segunda raíz productiva
NO promoción productiva sin compuerta explícita
```

# DO_NOT_TOUCH

```text
service_1_product_pipeline_v1.py
service_1_accounting_contracts_v1.py
service_1_capability_registry_v1.py
contratos de dominio
sandbox
workpapers
APIs
LLM
```
