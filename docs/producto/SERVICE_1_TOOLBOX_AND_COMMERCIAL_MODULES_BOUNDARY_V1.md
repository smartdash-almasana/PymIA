# SERVICE_1_TOOLBOX_AND_COMMERCIAL_MODULES_BOUNDARY_V1

## Estado

```text
Tipo: PRODUCT_BOUNDARY
Estado: DRAFT_APPLIED
Runtime impact: NONE
Code impact: NONE
Tests impact: NONE
```

## Propósito

Definir la frontera entre `First Aid Toolbox` y `Commercial Modules` dentro de PymIA Servicio 1.

Este documento evita duplicación conceptual antes de abrir loaders, pipeline, XLSX delivery o wiring productivo.

---

# 1. Tesis

```text
First Aid Toolbox = caja de herramientas inicial, limitada y segura.
Commercial Modules = módulos comerciales vendibles, declarativos y más estructurados.
```

Ambas capas pueden convivir, pero no deben mezclarse como si fueran lo mismo.

---

# 2. First Aid Toolbox

## Rol

Resolver o destrabar dolores puntuales de baja fricción.

## Alcance

```text
ordenar datos simples
validar evidencia mínima
calcular señales básicas
marcar faltantes
bloquear si falta evidencia
pedir confirmación de columnas
explicar límites owner-facing
```

## No debe hacer

```text
emitir findings comerciales completos
ejecutar acciones sugeridas
generar estrategia comercial
diagnosticar la empresa
producir automatización contable
```

## Artefactos actuales

```text
PymIA-Live/pymia/contracts/first_aid_toolbox_pack_seed_v1.json
PymIA-Live/pymia/contracts/first_aid_tool_activation_v1.json
PymIA-Live/pymia/smartpyme/first_aid_tool_activation_evaluator_v1.py
```

## Herramientas actuales

```text
caja_diaria_triage
precio_margen_basico
stock_alertas_basicas
gastos_triage
proveedores_precio_variacion_triage
```

---

# 3. Commercial Modules

## Rol

Representar paquetes comerciales declarativos más completos y vendibles.

## Alcance

Según `docs/product/modules/module_schema_v1.md`, un Commercial Module declara:

```text
input
normalization
entity_mapping
evaluation
findings
actions
output
```

## No debe hacer

```text
modificar el core para cada módulo nuevo
ejecutar acciones automáticamente sin confirmación
mezclarse con First Aid sin contrato de frontera
saltar validación de schema o registry
```

## Artefactos actuales fuera del repo PymIA

```text
docs/product/modules/README.md
docs/product/modules/module_schema_v1.md
docs/product/modules/modules_registry_v1.json
docs/product/modules/module_loader_validation_v1.md
docs/product/modules/cobranzas_vencidas_v1.md
docs/product/modules/stock_roto_v1.md
docs/product/modules/conciliacion_ventas_ml_v1.md
```

## Módulos activos detectados

```text
cobranzas_vencidas
stock_roto
conciliacion_ventas_ml
```

---

# 4. Diferencia operacional

| Criterio | First Aid Toolbox | Commercial Modules |
|---|---|---|
| Profundidad | Baja / inicial | Media / producto vendible |
| Forma | Tool refs + evidence requirements + guardrails | Module schema + registry + findings + actions |
| Output | señal, faltante, pregunta, limitación | normalized_rows, findings, suggested_actions, summary, validation_errors |
| Riesgo | bajo si se bloquea bien | mayor, porque emite findings y acciones |
| Runtime actual | no autorizado | no integrado a PymIA-Live |
| Relación con IA | ninguna ejecución IA | ninguna ejecución IA requerida |
| Relación con Servicio 2 | escala si pide diagnóstico | puede alimentar diagnóstico posterior |

---

# 5. Regla de convivencia

```text
First Aid Toolbox no reemplaza Commercial Modules.
Commercial Modules no reemplazan First Aid Toolbox.
```

Regla práctica:

```text
First Aid desbloquea y ordena.
Commercial Module empaqueta y entrega una solución comercial más completa.
```

---

# 6. Relación entre herramientas y módulos

| First Aid Tool | Commercial Module cercano | Relación |
|---|---|---|
| stock_alertas_basicas | stock_roto | First Aid detecta alerta simple; módulo analiza stock roto con findings/actions |
| gastos_triage | ninguno directo | First Aid ordena egresos; aún no hay módulo comercial equivalente |
| proveedores_precio_variacion_triage | ninguno directo | First Aid detecta variación inicial; aún no hay módulo comercial equivalente |
| caja_diaria_triage | ninguno directo | First Aid ordena caja; podría derivar a módulo futuro |
| precio_margen_basico | conciliacion_ventas_ml parcialmente | First Aid calcula margen básico; módulo ML analiza conciliación y margen neto operativo |

---

# 7. Regla de promoción

Una herramienta First Aid puede convertirse o alimentar un Commercial Module si cumple:

```text
tiene input estable
tiene normalización declarada
tiene entity_mapping
tiene reglas de evaluación
tiene findings definidos
tiene suggested_actions definidos
tiene output canónico
tiene validación de schema y registry
```

Hasta entonces, debe seguir como First Aid Tool.

---

# 8. Regla de integración futura

No crear loader compartido todavía.

Orden seguro:

```text
1. mantener First Aid Toolbox y Commercial Modules separados
2. validar Commercial Modules documentalmente
3. decidir si sus contratos se migran o referencian desde PymIA
4. crear adapter de frontera si hace falta
5. recién después evaluar loader compartido o registry común
```

---

# 9. Riesgos si se mezclan

```text
duplicación de registries
dos loaders compitiendo
tools First Aid emitiendo findings demasiado fuertes
Commercial Modules usados sin suficiente evidencia
pipeline contaminado con dos modelos de activación
confusión entre señal inicial y producto vendible
```

---

# 10. Decisiones actuales

```text
First Aid Toolbox permanece como capa inicial de triage.
Commercial Modules permanecen como capa comercial declarativa separada.
No se comparte loader todavía.
No se comparte registry todavía.
No se conecta a pipeline todavía.
No se abre XLSX delivery todavía.
```

---

# 11. Impacto sobre próximos pasos

El evaluator First Aid puede seguir existiendo como función pura.

Antes de abrir pipeline o delivery, conviene decidir si el siguiente frente será:

```text
A. First Aid Activation Scenarios V1
B. Commercial Modules Catalog Intake V1
C. Commercial Modules Boundary Audit V1
```

Recomendación:

```text
A. First Aid Activation Scenarios V1
```

Motivo:

```text
Permite probar flujos conceptuales de las 5 herramientas sin mezclar todavía Commercial Modules.
```

---

# 12. Veredicto

```text
BOUNDARY_DEFINED
```

Condición:

```text
No crear loader ni pipeline compartido hasta cerrar al menos un escenario First Aid completo y documentado.
```
