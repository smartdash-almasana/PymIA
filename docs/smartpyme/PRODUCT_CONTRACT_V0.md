# SmartPyme — Product Contract V0

## Estado

DRAFT_FOR_REVIEW

## Propósito

Este documento define una unidad mínima de producto controlado basada únicamente en evidencia técnica actualmente certificada en el repo PymIA.

No es una visión completa de SmartPyme.
No es una plataforma final.
No es una promesa comercial amplia.
No declara nuevas capacidades.

Su objetivo es cortar la deriva entre:

```text
capacidad técnica certificada
servicio manual asistido
producto mínimo controlado
```

---

# 1. Evidencia base

Al momento de este contrato, el núcleo técnico tiene certificadas dos capacidades:

```text
excel_diagnostic
supplier_duplicate_check
```

Ambas figuran en `pymia/smartpyme/capabilities.yaml` como:

```text
status: PIPELINE_CERTIFIED
pipeline_certified: true
dispatcher_available: true
cli_available: true
```

El pipeline también certifica bloqueos sanos para:

```text
falta de evidencia
evidencia incorrecta
clasificación no soportada
```

El sistema de certificación asociado incluye:

```text
Pipeline Radiography
capability registry
Operational Harness
Registry Hardening
CI con harness_status.json
```

---

# 2. Qué NO es este producto

Este contrato no habilita decir que SmartPyme es:

```text
un ERP
un dashboard
una IA empresarial completa
un laboratorio operacional completo
un parser documental general
un generador certificado de reportes HTML/PDF
un sistema que entiende cualquier Excel
un sistema que diagnostica integralmente una empresa
un asesor financiero general
un reemplazo del contador o del consultor
```

Tampoco habilita prometer capacidades registradas como `NOT_FOUND`, incluyendo:

```text
report_html
document_parser_front
```

---

# 3. Nombre de la oferta mínima

Nombre operativo:

```text
SmartPyme Control Operativo Inicial V0
```

Nombre interno:

```text
PRODUCT_CONTRACT_V0
```

---

# 4. Definición estricta

SmartPyme Control Operativo Inicial V0 es una unidad mínima de entrega que acepta evidencia Excel dentro de alcances soportados, ejecuta sólo capacidades certificadas y devuelve una salida operativa controlada con hallazgos, bloqueos y próximos pasos.

La unidad no promete resolver cualquier caso.

Debe poder terminar en uno de estos estados:

```text
DELIVERED
BLOCKED_NEEDS_EVIDENCE
BLOCKED_UNSUPPORTED
BLOCKED_EVIDENCE_MISMATCH
```

---

# 5. Cliente objetivo inicial

PyME o dueño/operador que tiene evidencia operativa en Excel y necesita una primera lectura controlada sobre:

```text
ventas / costos / margen
proveedores duplicados o inconsistentes
```

No se orienta todavía a empresas que requieren:

```text
integración automática con sistemas
onboarding multiusuario
historial mensual garantizado
conectores bancarios
análisis documental PDF general
reporting visual avanzado
dashboard operativo
```

---

# 6. Capacidades incluidas

## 6.1 Diagnóstico Excel ventas/costos/margen

Capability:

```text
excel_diagnostic
```

Alcance certificado:

```text
Excel con evidencia compatible de ventas/costos/margen.
```

Puede producir hallazgos operativos sobre evidencia estructurada de ventas/costos.

No equivale a auditoría financiera integral.
No garantiza interpretación correcta de cualquier estructura arbitraria de Excel.

## 6.2 Revisión de proveedores duplicados

Capability:

```text
supplier_duplicate_check
```

Alcance certificado:

```text
Excel de proveedores con columnas compatibles, incluyendo señales como proveedor, CUIT o razón social.
```

Puede producir hallazgos sobre duplicación o inconsistencia de proveedores según la capacidad certificada.

No equivale a saneamiento maestro completo de proveedores.
No garantiza deduplicación universal sobre cualquier base arbitraria.

---

# 7. Evidencia aceptada

La evidencia mínima aceptada en V0 es:

```text
archivo Excel de ventas/costos/margen
archivo Excel de proveedores
```

La evidencia debe ser localizable, procesable y suficientemente estructurada para las capacidades certificadas.

Ejemplos de señales esperadas:

```text
producto
ventas
costo
proveedor
cuit
razon_social
```

La ausencia de estas señales puede producir bloqueo o pedido de evidencia adicional.

---

# 8. Evidencia no aceptada en V0

V0 no acepta como alcance certificado:

```text
PDF arbitrarios
imágenes
capturas de WhatsApp
extractos bancarios no estructurados
bases de datos conectadas
ERP externo
Google Sheets conectado
emails
texto libre sin archivo operativo
archivos Excel sin relación clara con ventas, costos o proveedores
```

Estos insumos pueden ser útiles para una visión futura, pero no forman parte del contrato V0.

---

# 9. Flujo de entrada

Flujo mínimo:

```text
1. Se recibe una demanda operacional.
2. Se recibe uno o más archivos Excel.
3. Se clasifica si la evidencia corresponde a una capacidad certificada.
4. Si la evidencia es suficiente, se ejecuta la capacidad certificada.
5. Si la evidencia no es suficiente o no corresponde, se bloquea explícitamente.
6. Se genera una salida operativa controlada.
```

El flujo no requiere UI ni canal productivo específico en V0.

---

# 10. Salida entregable

La salida mínima debe ser legible y auditable.

Formato recomendado para V0:

```text
Markdown + JSON estructurado
```

No se promete PDF, HTML ni dashboard en este contrato.

## 10.1 Secciones mínimas del entregable Markdown

```text
1. Resumen ejecutivo
2. Evidencia recibida
3. Capacidad ejecutada
4. Hallazgos
5. Bloqueos o datos faltantes
6. Riesgos operativos detectados
7. Próximo paso recomendado
8. Límites del análisis
```

## 10.2 Campos mínimos del JSON

```text
tenant_or_case_id
input_files
capabilities_requested
capabilities_executed
status
findings
blocked_reasons
missing_evidence
next_recommended_action
scope_limits
```

---

# 11. Criterios de bloqueo

El producto V0 debe bloquear, no improvisar, cuando:

```text
falta evidencia necesaria
la evidencia recibida no corresponde a una capacidad certificada
la clasificación no está soportada
el archivo no puede procesarse
el usuario pide una capacidad fuera de alcance
```

Estados de bloqueo:

```text
BLOCKED_NEEDS_EVIDENCE
BLOCKED_EVIDENCE_MISMATCH
BLOCKED_UNSUPPORTED
BLOCKED_INVALID_FILE
```

Un bloqueo correcto es una salida válida del producto.

---

# 12. Qué significa terminado

Un caso V0 está terminado si llega a uno de estos resultados:

```text
DELIVERED
BLOCKED_NEEDS_EVIDENCE
BLOCKED_EVIDENCE_MISMATCH
BLOCKED_UNSUPPORTED
BLOCKED_INVALID_FILE
```

Para `DELIVERED`, deben existir:

```text
entregable Markdown
entregable JSON
capacidad ejecutada registrada
hallazgos o resultado explícito
evidencia usada
límites del análisis
```

Para estados bloqueados, deben existir:

```text
motivo de bloqueo
evidencia faltante o incompatible
próximo dato requerido
límite explícito del sistema
```

---

# 13. Diferencia entre capacidad, servicio y producto

## 13.1 Capacidad técnica certificada

Una capacidad técnica certificada demuestra que el sistema puede ejecutar un camino controlado bajo tests, radiografía, registry y CI.

Ejemplos actuales:

```text
excel_diagnostic
supplier_duplicate_check
```

## 13.2 Servicio manual asistido

Un servicio manual asistido ocurre cuando una persona usa una IA o herramienta para analizar un archivo y redactar una respuesta.

Eso no es producto por sí mismo.

## 13.3 Producto mínimo controlado

Un producto mínimo controlado existe cuando hay:

```text
entrada definida
alcance definido
salida definida
criterios de bloqueo
capacidades certificadas usadas
repetibilidad
trazabilidad
límites explícitos
```

SmartPyme Control Operativo Inicial V0 apunta a esta categoría.

---

# 14. Valor diferencial frente a IA manual + humano

V0 sólo se diferencia de IA manual + humano si mantiene estas propiedades:

```text
no promete capacidades inexistentes
usa sólo capacidades certificadas
dejan trazas y estados verificables
bloquea casos fuera de alcance
produce salida con estructura estable
puede repetirse sobre casos equivalentes
se valida contra registry/radiography/harness/CI
```

Si una entrega no usa estas propiedades, debe considerarse servicio asistido, no producto SmartPyme.

---

# 15. Qué no se promete

V0 no promete:

```text
análisis integral de rentabilidad
conciliación bancaria
análisis fiscal o contable
análisis de PDFs
limpieza universal de Excel
normalización completa de proveedores
visualización web
PDF automático
HTML certificado
dashboard
integración Telegram
persistencia histórica garantizada
multiusuario
automatización continua
recomendaciones estratégicas amplias
```

---

# 16. Criterios de aceptación de V0

El contrato V0 queda aceptado si permite diseñar una implementación que:

```text
1. use sólo excel_diagnostic y supplier_duplicate_check;
2. genere salida Markdown + JSON;
3. bloquee explícitamente evidencia insuficiente o no soportada;
4. no agregue capacidades nuevas;
5. no dependa de UI/PDF/HTML/Telegram;
6. sea testeable con fixtures existentes o evidencia local controlada;
7. pueda ser ejecutada localmente;
8. no rompa registry/radiography/harness/CI.
```

---

# 17. Próximo hito sugerido

No implementar producto todavía sin review de este contrato.

Siguiente hito lógico:

```text
P1_DELIVERY_SPEC_V0
```

Objetivo de P1:

```text
Definir la estructura exacta del entregable Markdown + JSON para SmartPyme Control Operativo Inicial V0.
```

P1 no debe agregar capacidades nuevas.
P1 no debe introducir UI, PDF, HTML ni dashboard.

---

# 18. Regla de continuidad

Toda implementación posterior debe responder a este contrato.

Si una tarea no contribuye directamente a:

```text
entrada definida
salida definida
bloqueo explícito
uso de capacidades certificadas
entrega repetible
```

entonces no pertenece al camino corto hacia producto V0.
