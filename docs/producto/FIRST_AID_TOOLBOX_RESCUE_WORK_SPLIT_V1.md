# FIRST_AID_TOOLBOX_RESCUE_WORK_SPLIT_V1

## Estado

```text
Tipo: OPERATING_PLAN
Estado: DRAFT_APPLIED
Runtime impact: NONE
Code impact: NONE
```

## Propósito

Separar con precisión qué puede hacer ChatGPT en este entorno sin trabas ni bloqueos, y qué debe hacer Codex u otro agente con acceso real al repo/código para rescatar piezas valiosas de `exeland2` hacia el almacén enchufable de Primeros Auxilios PymIA.

Fuente de arqueología:

```text
E:\BuenosPasos\exeland2
```

Destino conceptual:

```text
PymIA / Primeros Auxilios / Toolbox Packs enchufables
```

---

# 1. Principio rector

```text
ChatGPT diseña, audita, clasifica, documenta y redacta contratos.
Codex extrae, normaliza, migra, testea y propone código bajo TaskSpec.
```

Regla:

```text
No usar Codex para decidir arquitectura.
No usar ChatGPT para fingir ejecución técnica que no puede validar.
```

---

# 2. Lo que puede hacer ChatGPT sin trabas

## 2.1 Arqueología documental

ChatGPT puede:

```text
leer árboles de archivos
leer YAML/MD/TXT/HTML accesibles
inventariar catálogos
comparar specs
identificar duplicados
marcar riesgos semánticos
clasificar piezas por nivel de servicio
```

Ya realizado parcialmente:

```text
exeland2/catalog/formulas.yaml
exeland2/catalog/validations.yaml
exeland2/catalog/product_registry.yaml
exeland2/specs/*.yaml
exeland2/warehouse/templates
```

## 2.2 Clasificación de valor

ChatGPT puede separar piezas en:

```text
FIRST_AID_READY
FIRST_AID_WITH_LIMITS
RESTRICTED_LEVEL_2
RESTRICTED_LEVEL_3
REVIEW_REQUIRED
REJECT_OR_QUARANTINE
```

Ejemplos detectados:

```text
caja_diaria.yaml -> FIRST_AID_READY
precio_margen.yaml -> FIRST_AID_READY
stock_control.yaml -> FIRST_AID_WITH_LIMITS
punto_equilibrio.yaml -> RESTRICTED_LEVEL_2
proyeccion_ventas.yaml -> RESTRICTED_LEVEL_2/3
auto_ganancia.yaml -> REVIEW_REQUIRED por slug inconsistente
compras_y_proveedores.yaml -> REVIEW_REQUIRED por binding semántico dudoso
```

## 2.3 Diseño de contratos

ChatGPT puede redactar:

```text
FIRST_AID_TOOLBOX_PACK_CONTRACT_V1.md
FIRST_AID_TOOLBOX_PACK_SEED_V1.yaml
FIRST_AID_TEMPLATE_REF_CATALOG_V1.md
FIRST_AID_FORMULA_REF_CATALOG_V1.md
FIRST_AID_VALIDATION_REF_CATALOG_V1.md
FIRST_AID_EVIDENCE_REQUIREMENTS_V1.md
FIRST_AID_FORBIDDEN_CLAIMS_V1.md
```

Debe mantenerse en documentación/contrato hasta autorización explícita de runtime.

## 2.4 Detección de antipatrones

ChatGPT puede identificar:

```text
fórmulas usadas con semántica incorrecta
plantillas duplicadas
slugs inconsistentes
nombres comerciales que prometen demasiado
riesgo de diagnóstico sin evidencia
riesgo de convertir PymIA en tienda de Excels
riesgo de contaminar kernel con conocimiento de dominio
```

## 2.5 Redacción de prompts para Codex

ChatGPT puede producir prompts precisos para:

```text
auditoría técnica de exeland2
extracción de catálogos
normalización YAML
creación de seed fuera de runtime
tests de contrato
comparación de specs vs registry
reporte de inconsistencias
```

## 2.6 Documentación de memoria

ChatGPT puede actualizar:

```text
Pymia-memoria/_estado_actual.md
Pymia-memoria/_task_actual.md
Pymia-memoria/_decisiones_vigentes.md
Pymia-memoria/_no_volver_a_hacer.md
```

Sólo si el frente lo justifica.

---

# 3. Lo que NO debe hacer ChatGPT en este frente

ChatGPT no debe:

```text
crear runtime PymIA para cargar packs
modificar kernel
simular tests como si hubieran corrido
migrar YAML directamente a contracts vivos
copiar XLSX al repo PymIA
editar specs Exceland originales
convertir exeland2 en dependencia del core
abrir application wiring
crear loader Pydantic sin autorización
```

También debe evitar:

```text
seguir leyendo infinitamente si ya hay suficiente muestra
confundir arqueología con implementación
proponer features por entusiasmo
```

---

# 4. Lo que debe hacer Codex

Codex debe trabajar sólo bajo TaskSpec cerrado.

## 4.1 Auditoría técnica de exeland2

Codex puede:

```text
recorrer todos los YAML de exeland2/catalog y exeland2/specs
parsearlos con YAML real
validar que todos los formula_ref existan en formulas.yaml
validar que todos los validation existan en validations.yaml
validar que product_registry apunte a specs existentes
validar que templates XLSX existan para cada spec registrado
identificar specs huérfanas
identificar templates huérfanos
identificar slugs duplicados o inconsistentes
```

Output esperado:

```text
EXELAND2_RESCUE_AUDIT_REPORT.md
exeland2_rescue_audit.json
```

## 4.2 Extracción de catálogo normalizado

Codex puede generar artefactos derivados, sin tocar runtime:

```text
first_aid_formula_refs_candidate.yaml
first_aid_validation_refs_candidate.yaml
first_aid_template_refs_candidate.yaml
first_aid_tool_refs_candidate.yaml
```

Condición:

```text
Ubicación temporal o docs/producto, no runtime.
```

## 4.3 Tests de contrato no-runtime

Codex puede crear tests documentales o schema tests sólo si se autoriza.

Ejemplos:

```text
tests/contracts/test_first_aid_toolbox_pack_candidate.py
```

Validaciones posibles:

```text
pack_id presente
scope FIRST_AID
requires_minimal_case_file_layer true
formula_refs existen
restricted_formula_refs separadas
forbidden_claims no vacíos
evidence_requirements por tool
```

## 4.4 Normalización semántica

Codex puede preparar propuestas de corrección, no aplicarlas sin revisión:

```text
auto_ganancia.yaml -> slug/title inconsistente
compras_y_proveedores.yaml -> tiempo_promedio_entrega usa costo_reposicion_promedio
stock_control.yaml vs auto_stock.yaml -> duplicación
rentabilidad_por_producto.yaml -> renombrar owner-facing como margen_bruto_por_producto_triage
```

Output esperado:

```text
EXELAND2_SEMANTIC_RISK_REGISTER.md
```

## 4.5 No debe decidir qué entra al kernel

Codex no debe:

```text
crear loader en PymIA-Live sin TaskSpec
mover archivos a pymia/contracts sin autorización
copiar templates XLSX al repo principal
crear dependencia runtime a exeland2
renombrar specs fuente sin aprobación
```

---

# 5. División por fases

## Fase A — ChatGPT

```text
A1. Completar arqueología conceptual.
A2. Crear Work Split.
A3. Crear TemplateRefs conceptuales.
A4. Crear prompt Codex de auditoría técnica.
A5. Actualizar memoria si se cierra la fase.
```

## Fase B — Codex auditor

```text
B1. Parsear exeland2 completo.
B2. Verificar registry/specs/templates/formulas/validations.
B3. Emitir reporte de inconsistencias.
B4. No tocar PymIA runtime.
```

## Fase C — ChatGPT + Owner

```text
C1. Revisar reporte Codex.
C2. Aprobar qué piezas pasan a pack candidato.
C3. Rechazar o poner en cuarentena piezas dudosas.
```

## Fase D — Codex implementador documental

```text
D1. Crear seed YAML candidato.
D2. Crear tests de contrato si se autoriza.
D3. No crear loader todavía.
```

## Fase E — Runtime futuro, no ahora

```text
E1. Diseñar loader de packs.
E2. Tests.
E3. Integración controlada.
```

---

# 6. Prompts que debe recibir Codex

## Prompt 1 — auditoría técnica sin cambios

Objetivo:

```text
Auditar exeland2 como cantera de herramientas, sin modificar PymIA ni exeland2.
```

Debe producir:

```text
EXELAND2_RESCUE_AUDIT_REPORT.md
exeland2_rescue_audit.json
```

## Prompt 2 — extracción de candidatos

Objetivo:

```text
Generar archivos candidate derivados de la auditoría, sin runtime.
```

Debe producir:

```text
first_aid_formula_refs_candidate.yaml
first_aid_validation_refs_candidate.yaml
first_aid_template_refs_candidate.yaml
first_aid_tool_refs_candidate.yaml
```

## Prompt 3 — contrato/tests

Objetivo:

```text
Validar que los candidate packs cumplen contrato, sin loader runtime.
```

Debe producir:

```text
test_first_aid_toolbox_pack_candidate.py
```

Sólo si el Owner autoriza tests.

---

# 7. Reglas de seguridad

```text
No copiar XLSX al repo PymIA sin decisión explícita.
No ejecutar macros.
No usar templates como diagnóstico.
No confundir plantilla con capacidad certificada.
No migrar fórmulas restringidas a FIRST_AID.
No hardcodear conocimiento Exceland en kernel.
No tocar PymIA-Live runtime.
```

---

# 8. Veredicto

```text
RESCUE_SPLIT = APPROVED_AS_OPERATING_PLAN
```

ChatGPT sigue como:

```text
arquitecto documental
auditor conceptual
redactor de contratos
redactor de prompts
clasificador de piezas
```

Codex entra como:

```text
auditor técnico
normalizador de YAML
extractor de candidates
ejecutor de tests autorizados
```

---

# 9. Siguiente paso recomendado

Crear el prompt Codex:

```text
PROMPT_CODEX_EXELAND2_RESCUE_AUDIT_V1
```

Alcance:

```text
read-only
sin modificar archivos
sin runtime PymIA
sin tests salvo lectura/parsing local
reporte MD + JSON
```
