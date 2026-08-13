# SERVICE_1_SELLABLE_PRODUCT_CONTRACT_V1

## STATUS

```text
FREEZE_SELLABLE_PRODUCT: CLOSED_PASS
SELLABLE_SCOPE: ONE
PROMISES_MATCH_RUNTIME: PASS
NO_UNAUTHORIZED_CAPABILITY: PASS
NEW_PRODUCTIVE_CAPABILITY_AUTHORIZED: NO
```

## PURPOSE

Congelar qué se vende como Servicio 1 sobre la evidencia ya cerrada en el repo. Este contrato no crea capacidades, fórmulas, arquitectura, parser, autoridad de ejecución ni autoridad de delivery nuevas.

## CLIENTE OBJETIVO INICIAL

PyME que ya opera con información en Excel y necesita controles operativos concretos sobre cobros, margen y conciliación bancaria sin reemplazar la revisión humana ni profesional.

Este freeze no declara una vertical sectorial exclusiva. Consorcios permanece fuera del portfolio general de lanzamiento hasta su propio cierre comercial.

## PROBLEMA QUE COMPRA EL CLIENTE

Servicio 1 vende controles operativos acotados y basados en evidencia sobre archivos XLSX para responder preguntas concretas de negocio, exponer datos faltantes o inconsistencias y producir un resultado revisable y descargable.

No vende un diagnóstico integral de empresa.

## PORTFOLIO DISPONIBLE V1

### S1-01 — Control de Cobros y Conciliación

Recorrido probado:

```text
selección de servicio
→ XLSX
→ confirmación semántica cuando corresponde
→ ejecución determinística
→ resultado de vendido / cobrado / diferencia
→ límites de interpretación
→ descarga XLSX
```

Estado comercial del freeze: `DISPONIBLE`.

### S1-02 — Conciliación Bancaria

Recorrido probado:

```text
inicio de conciliación
→ carga de dos fuentes
→ confirmación de columnas
→ matching gobernado
→ revisión humana obligatoria
→ resumen de coincidencias/diferencias
→ workpaper XLSX
```

PymIA no marca movimientos como conciliados automáticamente.

Estado comercial del freeze: `DISPONIBLE`.

### S1-03 — Margen Real

Recorrido probado:

```text
selección de servicio
→ XLSX
→ confirmación semántica del dueño
→ P6
→ P7
→ P8
→ ejecución determinística net_margin_real
→ P10
→ resultado acotado
→ descarga XLSX
```

Estado comercial del freeze: `DISPONIBLE`.

## NO DISPONIBLE EN ESTE FREEZE

### S1-04 — Caja y Capital de Trabajo

Estado actual: `TECHNICAL_E2E_READY / PASS_WITH_PRODUCT_GAPS`.

Existe composición sobre `projected_closing_cash_balance`, `dso` y `current_ratio`, pero no se declara comercialmente cerrada hasta resolver su propio gate de producto. No forma parte del portfolio `DISPONIBLE` de este contrato.

### S1-05 — Stock y Reposición

Estado actual: `GATED`.

Capacidades internas existentes no equivalen a un servicio comercial terminado.

### Otras capacidades internas

Las demás capacidades conectadas a la raíz productiva permanecen capacidades del motor y no se presentan como productos comerciales visibles por el hecho de existir.

## RADAR

RADAR es una capa transversal sobre resultados ya gobernados. No es una segunda raíz productiva ni una autoridad de diagnóstico, computabilidad o ejecución.

## INPUTS REQUERIDOS

Según el servicio:

```text
identidad tenant cuando corresponda
archivo XLSX o fuentes XLSX requeridas
contexto/período de negocio cuando corresponda
confirmaciones explícitas del dueño cuando P6 las requiera
evidencia mínima requerida por la capacidad
```

Ante evidencia insuficiente, Servicio 1 debe bloquear o pedir input adicional.

## JOURNEY VENDIDO

Para controles de una fuente:

```text
HOME
→ elegir servicio
→ cargar Excel
→ confirmar significado si hace falta
→ ejecutar el servicio elegido
→ resultado
→ descargar
```

Para conciliación bancaria:

```text
HOME
→ Conciliación Bancaria
→ cargar dos fuentes
→ confirmar columnas
→ matching gobernado
→ revisión humana
→ resultado
→ descargar workpaper
```

La autoridad interna sigue siendo P0→P10 y `pymia/smartpyme/service_1_product_pipeline_v1.py` donde corresponda.

## RESULTADO VISIBLE

Toda salida comercial debe permitir entender:

1. qué encontró PymIA;
2. qué datos se usaron;
3. qué requiere revisión humana;
4. qué no puede concluir PymIA;
5. qué archivo puede descargarse;
6. cuál es el próximo paso cuando falte evidencia.

La UI puede usar lenguaje comercial como:

```text
LISTO
REQUIERE REVISIÓN
FALTA INFORMACIÓN
EN PROCESO
```

Los estados técnicos internos no deben ser requisito de comprensión para el cliente.

## ESTADOS CONTRACTUALES

### READY / LISTO

Existe evidencia suficiente para producir el resultado acotado y el entregable correspondiente bajo los gates vigentes.

### NEEDS_OWNER_INPUT / FALTA INFORMACIÓN

Falta evidencia o confirmación del dueño. No se inventa significado ni se ejecuta por inferencia no gobernada.

### REQUIRES_REVIEW / REQUIERE REVISIÓN

Existe un resultado que requiere revisión humana antes de cualquier conclusión o cierre operativo, especialmente en conciliación.

### BLOCKED

Un requisito obligatorio, evidencia, identidad, guard o condición de seguridad impide continuar. El bloqueo sano es comportamiento correcto.

## ENTREGABLES

```text
S1-01 → resultado web + XLSX
S1-02 → resultado web + workpaper XLSX
S1-03 → resultado web + XLSX
```

La existencia de un archivo descargable no autoriza claims fuera del alcance del resultado gobernado.

## REENTRADA Y PERSISTENCIA

Identidad tenant y persistencia semántica durable están activas en el recorrido vigente.

La vista de casos recientes/reentrada disponible en la web permite reabrir snapshots dentro del alcance implementado, pero la persistencia de esos snapshots es in-memory por instancia y no sobrevive un restart. Por lo tanto, este contrato no promete persistencia durable enterprise de casos recientes.

## INTERVENCIÓN HUMANA

La revisión humana permanece obligatoria cuando el resultado, el flujo o el guard correspondiente la requieran.

Owner confirmation es evidencia semántica. No concede autoridad general de ejecución ni delivery.

## CLAIMS PERMITIDOS

Formulaciones compatibles con este contrato:

```text
control operativo
hallazgo basado en la evidencia disponible
resultado preliminar/acotado
requiere revisión
faltan datos para concluir
PymIA encontró una diferencia / relación / coincidencia candidata
```

## CLAIMS PROHIBIDOS

Servicio 1 no debe prometer ni afirmar:

```text
diagnóstico definitivo
auditoría
certificación
conciliación definitiva
rentabilidad real confirmada
reemplazo del contador o profesional
cierre contable automático
causalidad no demostrada
entrega autónoma soberana
```

## FUERA DEL PRODUCTO V1

```text
Consorcios como suite general
Marketplace / Mercado Libre / Mercado Pago como vertical completa
Secretario Digital
ARCA / impuestos como suite
CRM
ERP
WhatsApp
gestión general de tareas
billing propio
agentes autónomos
OCR/PDF parser
nueva arquitectura
nueva capability productiva
```

## CRITERIO DE ENTREGABLE

Un resultado es entregable dentro de este contrato sólo cuando:

```text
el servicio está marcado DISPONIBLE en este contrato
la evidencia requerida está presente
las confirmaciones obligatorias están resueltas
P6/P7/P8 pasan cuando aplican
la ejecución determinística termina sin bypass
P10/delivery correspondiente pasa
el output visible conserva límites y provenance
la revisión humana requerida no se omite
```

## INVARIANTES

```text
ONE_CANONICAL_PRODUCT_ROOT
NO_LLM_RUNTIME_AUTHORITY
NO_SECOND_XLSX_PARSER
NO_PARALLEL_PRODUCTIVE_PIPELINE
FAIL_CLOSED
OWNER_CONFIRMATION_IS_EVIDENCE_NOT_PERMISSION
P7_REQUIREMENT_MATCH_PRECEDES_P8
P9_EXECUTION_ONLY_FROM_GOVERNED_INPUT
P10_CONTROLS_DELIVERY_QUALITY
```

## NEXT_GATE

```text
PROVE_REAL_SELLABLE_JOURNEY
```

No se autoriza ampliar el portfolio antes de probar ese gate sobre el producto congelado.


Contract marker for excluded launch items: `NOT_SELLABLE_YET`.
