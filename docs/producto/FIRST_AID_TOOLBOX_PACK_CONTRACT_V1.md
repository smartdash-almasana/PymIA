# FIRST_AID_TOOLBOX_PACK_CONTRACT_V1

## Estado

```text
Tipo: PRODUCT_CONTRACT
Estado: DRAFT_APPLIED
Runtime impact: NONE
Code impact: NONE
```

## Propósito

Definir el contrato conceptual mínimo para un almacén enchufable de herramientas de `Primeros Auxilios PyME`.

Este contrato nace de la arqueología de `exeland2`, pero no importa `exeland2` como runtime.

Fuente arqueológica primaria:

```text
E:\BuenosPasos\exeland2\catalog\formulas.yaml
E:\BuenosPasos\exeland2\catalog\validations.yaml
E:\BuenosPasos\exeland2\catalog\product_registry.yaml
```

Documento previo:

```text
docs/producto/FIRST_AID_TOOLBOX_ARCHAEOLOGY_EXCELAND_V1.md
```

---

# 1. Tesis

Primeros Auxilios necesita una caja de herramientas enchufable.

No necesita que el kernel sepa de memoria todas las fórmulas, plantillas, validaciones o herramientas.

Regla:

```text
El conocimiento operativo entra como pack.
El kernel carga, valida, ejecuta si corresponde y falla cerrado.
```

---

# 2. Qué es un FirstAidToolboxPack

Un `FirstAidToolboxPack` es un conjunto declarativo de herramientas de baja fricción para resolver problemas puntuales de PyMEs.

Puede contener:

```text
FormulaRefs
ValidationRefs
ToolRefs
TemplateRefs
EvidenceRequirements
OwnerFacingLimitations
EscalationRules
ForbiddenClaims
```

No contiene:

```text
runtime Python obligatorio
lógica de diagnóstico global
conocimiento sectorial hardcodeado
autorización para modificar OCF
UI
CLI
rendering
storage
```

---

# 3. Alcance permitido

Un pack FIRST_AID puede servir para:

```text
ordenar una fuente
validar campos simples
aplicar cálculos básicos
marcar datos faltantes
producir una señal inicial
pedir evidencia concreta
sugerir escalamiento proporcional
```

No puede servir para:

```text
diagnosticar toda la empresa
confirmar rentabilidad real sin suficiencia
certificar caja, banco o stock
reemplazar contador, ERP o auditoría
activar automatización productiva
modificar archivos originales sin autorización explícita
```

---

# 4. Estructura conceptual del pack

Representación esperada:

```yaml
pack_id: first_aid_toolbox_pack_v1
name: Primeros Auxilios PyME Toolbox
source: exceland2_archaeology
scope: FIRST_AID
status: CANDIDATE
version: 1.0.0
allowed_service_depth:
  - FIRST_AID
requires_minimal_case_file_layer: true
owner_facing_name: Caja de herramientas de primeros auxilios
summary: Herramientas simples para revisar planillas, precios, costos, caja, stock y tareas manuales.
```

Campos obligatorios:

```yaml
pack_id:
name:
source:
scope:
status:
version:
allowed_service_depth:
requires_minimal_case_file_layer:
formula_refs:
validation_refs:
tool_refs:
evidence_requirements:
forbidden_claims:
escalation_rules:
```

---

# 5. Regla obligatoria de ficha mínima

Ningún pack FIRST_AID puede operar antes de capturar la primera capa formal de ficha organizacional.

Capa mínima:

```text
nombre visible del negocio
tipo de empresa
rubro o actividad
modelo operativo básico
canales de venta
presencia de stock
problema puntual elegido
frase textual del dueño
evidencia disponible o pendiente
```

Regla:

```text
Primero se ubica el organismo PyME.
Después se usa la herramienta.
```

---

# 6. FormulaRefs iniciales

Fórmulas candidatas FIRST_AID derivadas de Exceland:

```yaml
formula_refs:
  - id: margen_bruto
    source_ref: exceland2/catalog/formulas.yaml#margen_bruto
    service_depth: FIRST_AID
    owner_label: Margen bruto estimado
    required_inputs:
      - precio_venta
      - costo_unitario
    output_type: percentage
    limitation: No confirma rentabilidad real si faltan comisiones, impuestos, envíos, descuentos o costos indirectos.

  - id: margen_bruto_pesos
    source_ref: exceland2/catalog/formulas.yaml#margen_bruto_pesos
    service_depth: FIRST_AID
    owner_label: Diferencia entre precio y costo
    required_inputs:
      - precio_venta
      - costo_unitario
    output_type: currency
    limitation: Es margen bruto unitario, no resultado final del negocio.

  - id: precio_venta_con_margen
    source_ref: exceland2/catalog/formulas.yaml#precio_venta_con_margen
    service_depth: FIRST_AID
    owner_label: Precio sugerido para margen objetivo
    required_inputs:
      - costo_unitario
      - margen_objetivo
    output_type: currency
    limitation: Es simulación de precio, no recomendación comercial definitiva.

  - id: markup
    source_ref: exceland2/catalog/formulas.yaml#markup
    service_depth: FIRST_AID
    owner_label: Markup sobre costo
    required_inputs:
      - precio_venta
      - costo_unitario
    output_type: percentage
    limitation: Markup no es lo mismo que margen sobre precio.

  - id: ingresos_totales
    source_ref: exceland2/catalog/formulas.yaml#ingresos_totales
    service_depth: FIRST_AID
    owner_label: Ingresos totales simples
    required_inputs:
      - precio_venta
      - unidades_vendidas
    output_type: currency
    limitation: Ingresos no son ganancia.

  - id: egresos_totales
    source_ref: exceland2/catalog/formulas.yaml#egresos_totales
    service_depth: FIRST_AID
    owner_label: Egresos totales simples
    required_inputs:
      - costos_fijos
      - costo_variable_unitario
      - unidades_vendidas
    output_type: currency
    limitation: Depende de que los costos estén completos y bien clasificados.

  - id: flujo_caja_neto
    source_ref: exceland2/catalog/formulas.yaml#flujo_caja_neto
    service_depth: FIRST_AID
    owner_label: Flujo de caja neto
    required_inputs:
      - ingresos
      - egresos
    output_type: currency
    limitation: No equivale a conciliación bancaria ni resultado contable.

  - id: saldo_acumulado
    source_ref: exceland2/catalog/formulas.yaml#saldo_acumulado
    service_depth: FIRST_AID
    owner_label: Saldo acumulado
    required_inputs:
      - saldo_anterior
      - flujo_neto
    output_type: currency
    limitation: Depende de saldo inicial confiable.

  - id: alerta_stock_minimo
    source_ref: exceland2/catalog/formulas.yaml#alerta_stock_minimo
    service_depth: FIRST_AID
    owner_label: Alerta de stock mínimo
    required_inputs:
      - stock_actual
      - stock_minimo
    output_type: boolean
    limitation: No confirma stock físico real.

  - id: dias_stock_restante
    source_ref: exceland2/catalog/formulas.yaml#dias_stock_restante
    service_depth: FIRST_AID
    owner_label: Días estimados de stock restante
    required_inputs:
      - stock_actual
      - ventas_diarias_promedio
    output_type: number
    limitation: Sólo es válido si ventas_diarias_promedio representa la realidad reciente.
```

---

# 7. Fórmulas excluidas de activación FIRST_AID directa

Estas fórmulas pueden existir en el almacén, pero no deben activarse como hallazgo FIRST_AID sin mayor suficiencia:

```yaml
restricted_formula_refs:
  - id: resultado_neto
    reason: Puede inducir diagnóstico financiero si ingresos y egresos están incompletos.
    suggested_depth: DETERMINISTIC_DIAGNOSIS

  - id: punto_equilibrio_unidades
    reason: Requiere costos fijos, precio y costo variable confiables.
    suggested_depth: DETERMINISTIC_DIAGNOSIS

  - id: punto_equilibrio_pesos
    reason: Requiere margen de contribución confiable.
    suggested_depth: DETERMINISTIC_DIAGNOSIS

  - id: rotacion_inventario
    reason: Requiere CMV e inventario promedio confiables.
    suggested_depth: DETERMINISTIC_DIAGNOSIS

  - id: costo_reposicion_promedio
    reason: Puede orientar decisión de compras y reposición; requiere contexto de stock y costos.
    suggested_depth: DETERMINISTIC_DIAGNOSIS
```

---

# 8. ValidationRefs iniciales

Validadores candidatos:

```yaml
validation_refs:
  - positive_number
  - non_negative_number
  - percentage_0_1
  - percentage_0_100
  - integer_positive
  - integer_non_negative
```

Uso permitido:

```text
marcar entradas inválidas
explicar formato esperado
pedir corrección de dato
bloquear cálculo si el dato rompe suficiencia mínima
```

Uso prohibido:

```text
convertir validación en diagnóstico
asumir que dato válido formalmente es verdadero operacionalmente
```

---

# 9. ToolRefs iniciales

Herramientas candidatas:

```yaml
tool_refs:
  - id: caja_diaria_triage
    source_ref: exceland2/specs/caja_diaria.yaml
    category: cashflow
    service_depth: FIRST_AID
    owner_label: Revisión inicial de caja diaria
    solves:
      - ordenar ingresos y egresos
      - calcular flujo neto simple
      - calcular saldo acumulado simple
    forbidden_claims:
      - conciliación bancaria cerrada
      - saldo real certificado
      - auditoría contable

  - id: precio_margen_basico
    source_ref: exceland2/specs/precio_margen.yaml
    category: pricing
    service_depth: FIRST_AID
    owner_label: Revisión básica de precio y margen
    solves:
      - calcular margen bruto
      - calcular markup
      - simular precio con margen objetivo
    forbidden_claims:
      - rentabilidad real confirmada
      - precio comercial definitivo
      - estrategia de pricing completa

  - id: stock_alertas_basicas
    source_ref: exceland2/specs/stock_control.yaml
    category: stock
    service_depth: FIRST_AID
    owner_label: Alertas básicas de stock
    solves:
      - detectar stock bajo
      - estimar días de stock restante
      - señalar datos faltantes para rotación
    forbidden_claims:
      - stock físico confirmado
      - recomendación final de compra
      - rotación confiable sin ventas y CMV

  - id: gastos_triage
    source_ref: exceland2/catalog/product_registry.yaml#control_de_gastos
    category: cashflow
    service_depth: FIRST_AID
    owner_label: Orden inicial de gastos
    solves:
      - agrupar egresos
      - detectar gastos sin categoría
      - pedir clasificación faltante
    forbidden_claims:
      - clasificación contable/fiscal definitiva
      - auditoría de gastos

  - id: proveedores_precio_variacion_triage
    source_ref: exceland2/catalog/product_registry.yaml#compras_y_proveedores
    category: stock
    service_depth: FIRST_AID
    owner_label: Revisión inicial de compras y proveedores
    solves:
      - detectar aumentos visibles
      - comparar proveedores si hay datos
      - marcar costos faltantes
    forbidden_claims:
      - estrategia de compras definitiva
      - rentabilidad por proveedor confirmada
```

---

# 10. EvidenceRequirements por herramienta

```yaml
evidence_requirements:
  caja_diaria_triage:
    minimum:
      - saldo_inicial
      - ingresos
      - egresos
    optional:
      - banco
      - mercado_pago
      - ventas
    missing_response: Para revisar caja necesito al menos saldo inicial, ingresos y egresos del período.

  precio_margen_basico:
    minimum:
      - precio_venta
      - costo_unitario
    optional:
      - margen_objetivo
      - descuento
      - comision
      - impuesto
      - envio
    missing_response: Para estimar margen necesito precio de venta y costo unitario.

  stock_alertas_basicas:
    minimum:
      - producto
      - stock_actual
      - stock_minimo
    optional:
      - ventas_diarias_promedio
      - costo_unitario
      - inventario_fisico
    missing_response: Para revisar stock necesito producto, stock actual y umbral mínimo.

  gastos_triage:
    minimum:
      - concepto
      - importe
    optional:
      - fecha
      - categoria
      - proveedor
      - medio_pago
    missing_response: Para ordenar gastos necesito al menos concepto e importe.

  proveedores_precio_variacion_triage:
    minimum:
      - proveedor
      - producto_o_insumo
      - precio_o_costo
    optional:
      - fecha
      - cantidad
      - factura
      - lista_anterior
    missing_response: Para revisar proveedores necesito proveedor, producto o insumo y precio/costo.
```

---

# 11. Salidas permitidas

Un tool FIRST_AID puede devolver:

```text
resultado simple
alerta puntual
campo faltante
validación fallida
señal inicial
pregunta siguiente
recomendación de escalamiento
```

Debe declarar:

```text
datos usados
datos faltantes
límite de interpretación
próximo paso sugerido
```

---

# 12. ForbiddenClaims globales

Prohibido afirmar en FIRST_AID:

```text
rentabilidad real confirmada
margen neto real sin costos completos
saldo bancario conciliado con una sola fuente
stock físico confirmado sin conteo
fraude o irregularidad intencional
auditoría contable cerrada
precio óptimo definitivo
estrategia comercial completa
punto de equilibrio empresarial total sin evidencia suficiente
diagnóstico integral de la empresa
```

---

# 13. EscalationRules

Escalar a `DETERMINISTIC_DIAGNOSIS` si:

```text
el dueño pregunta por causa
hay dos o más fuentes para cruzar
aparece diferencia material
se requiere explicar caja, margen, stock, canal o costos
se activan fórmulas restringidas
```

Escalar a `ORGANIZATIONAL_LAB` si:

```text
el dueño quiere ordenar la empresa completa
hay múltiples áreas críticas
hay necesidad longitudinal
hay intención explícita de laboratorio recurrente
```

---

# 14. No-oráculo

El pack no decide solo la profundidad de servicio.

Debe obedecer la regla:

```text
pregunta inicial
→ opción elegida por el dueño
→ ficha mínima
→ evidencia
→ herramienta proporcional
```

Service depth puede asistir, pero no reemplaza la elección explícita del dueño.

---

# 15. Criterio de aceptación del pack

Un `FirstAidToolboxPack` es aceptable si:

```text
no toca kernel
no hardcodea dominio en runtime
no diagnostica sin evidencia
requiere ficha mínima
expone limitaciones owner-facing
separa fórmulas aptas de fórmulas restringidas
incluye validaciones
incluye evidence requirements
incluye forbidden claims
incluye reglas de escalamiento
```

---

# 16. Veredicto

```text
FIRST_AID_TOOLBOX_PACK_CONTRACT_V1 = PRODUCT_CONTRACT_READY
```

Pero:

```text
NO_RUNTIME_AUTHORIZED
NO_LOADER_AUTHORIZED
NO_SCHEMA_AUTHORIZED
NO_TESTS_AUTHORIZED
NO_APPLICATION_WIRING_AUTHORIZED
```

Siguiente paso posible:

```text
Crear FIRST_AID_TOOLBOX_PACK_SEED_V1.yaml como artefacto candidato, todavía fuera del runtime.
```
