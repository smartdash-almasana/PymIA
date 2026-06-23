# SERVICE_1_ACCOUNTING_WORKPAPER_OPERATOR_RUNBOOK_V1

VEREDICT:

```text
ACCOUNTING_WORKPAPER_OPERATOR_RUNBOOK_V1: STANDARDIZED_AFTER_TWO_CONTROLLED_PILOTS
```

PURPOSE:

```text
Convertir los pilotos controlados exitosos de la unidad Servicio 1 / Papel de trabajo contable asistido
en una rutina operativa repetible para operador humano.

Este runbook define cómo aceptar, preparar, ejecutar y entregar casos simples bajo revisión humana,
sin abrir parser, OCR, APIs, runtime ni claims contables/fiscales finales.
```

SERVICE_SCOPE:

```text
El servicio produce:
- borrador operativo
- XLSX de revisión
- diferencias visibles
- faltantes de evidencia
- checklist para revisión humana

El servicio ordena evidencia declarada y prepara un paquete de revisión.
No produce dictamen, certificación, conciliación definitiva ni resultado contable final.
```

SUPPORTED_CASE_FAMILIES:

```text
1. ventas declaradas vs cobros declarados
2. compras declaradas vs pagos declarados
```

UNSUPPORTED_CASES:

```text
- auditoría
- certificación
- conciliación definitiva
- validación fiscal
- asientos automáticos
- resultado contable final
- garantía de exactitud
- API bancaria
- Mercado Pago API
- Mercado Libre API
- OCR
- parser automático nuevo
- casos multi-período sin recorte
- casos multi-moneda
- casos con inspección fiscal o reclamo legal activo
- casos sin responsable humano de revisión
```

CASE_ACCEPTANCE_RULES:

```text
Aceptar sólo si existe:
- período definido
- cliente identificado
- familia operativa acotada
- al menos dos archivos tabulares simples o un archivo base suficiente
- llaves transaccionales mínimas cuando existan
- responsable humano de revisión
- aceptación explícita de límites del servicio

La aceptación debe confirmar que la evidencia será tratada como declarada, no auditada.
```

CASE_REJECTION_RULES:

```text
Rechazar o detener si:
- el cliente exige auditoría
- el cliente exige certificación
- el cliente exige conciliación definitiva
- el cliente exige validación fiscal
- el cliente exige resultado contable final
- el cliente exige asientos automáticos
- el caso requiere API bancaria, Mercado Pago API o Mercado Libre API
- el caso requiere OCR o parser automático nuevo
- no hay responsable humano
- no hay período definido
- la familia operativa no está acotada
- los archivos mínimos no existen
```

CLIENT_INTAKE_STEPS:

```text
1. Identificar cliente o empresa.
2. Definir período.
3. Elegir familia operativa soportada.
4. Registrar objetivo del cliente.
5. Pedir archivos tabulares simples o archivo base suficiente.
6. Pedir nota breve de contexto.
7. Confirmar responsable humano de revisión.
8. Confirmar aceptación de límites.
9. Confirmar que no se espera dictamen, auditoría, certificación ni cierre final.
10. Registrar el caso como piloto/servicio asistido bajo revisión humana.
```

PILOT_FOLDER_SETUP:

```text
Crear carpeta local fuera del repo para cada caso.

Ubicación recomendada:
E:\BuenosPasos\smartbridge\PymIA-local-artifacts\_pilot_cases\<CASE_REF>\

Estructura sugerida:
01_contexto\
02_inputs_declarados\
03_outputs_operativos\
04_notas_revision\
05_review_sanitizado\

No commitear artefactos operativos.
No commitear XLSX.
No commitear datos del caso.
```

INPUT_FILE_NAMING:

```text
Usar nombres simples, trazables y sin datos sensibles.

Ejemplos:
ventas_declaradas_<periodo>.xlsx
cobros_declarados_<periodo>.xlsx
compras_declaradas_<periodo>.xlsx
pagos_declarados_<periodo>.xlsx
nota_contexto_<case_ref>.txt
faltantes_declarados_<case_ref>.txt

Evitar:
- CUIT reales
- nombres de clientes finales
- datos bancarios completos
- credenciales
- claves fiscales
- tokens
```

EVIDENCE_PRECHECK:

```text
Antes de ejecutar confirmar:
- archivos presentes
- período consistente
- familia operativa correcta
- columnas mínimas visibles o declaradas
- llaves transaccionales mínimas cuando existan
- importes expresados de forma comparable
- notas de contexto presentes
- evidencia marcada como declarada, no auditada
- no hay necesidad de API/OCR/parser
```

OPERATOR_EXECUTION_FLOW:

```text
1. Abrir caso local fuera del repo.
2. Aplicar intake.
3. Validar reglas de aceptación.
4. Registrar evidencia declarada.
5. Registrar responsable humano.
6. Seleccionar flujo operativo: ventas/cobros o compras/pagos.
7. Preparar revisión tabular manual/asistida.
8. Calcular totales declarados si los datos lo permiten.
9. Identificar diferencias visibles.
10. Identificar faltantes de evidencia.
11. Preparar XLSX operativo de revisión si corresponde.
12. Revisar límites y wording antes de entrega.
13. Entregar como borrador operativo sujeto a revisión humana.
14. Registrar feedback y fricciones.
```

SALES_COLLECTIONS_FLOW:

```text
Usar para ventas declaradas vs cobros declarados.

Pasos mínimos:
1. Registrar total de ventas declaradas.
2. Registrar cantidad de tickets/operaciones de venta.
3. Registrar total de cobros declarados.
4. Registrar cantidad de cobros.
5. Comparar por llave transaccional si existe.
6. Registrar diferencias visibles.
7. Registrar cobros huérfanos si existen.
8. Registrar ventas sin cobro asociado si existen.
9. Registrar faltantes documentales.
10. Preparar checklist para revisión humana.
```

PURCHASES_PAYMENTS_FLOW:

```text
Usar para compras declaradas vs pagos declarados.

Pasos mínimos:
1. Registrar total de compras declaradas.
2. Registrar cantidad de comprobantes de compra.
3. Registrar total de pagos declarados.
4. Registrar cantidad de pagos.
5. Comparar por proveedor, comprobante o referencia si existe.
6. Registrar pagos parciales visibles.
7. Registrar pagos huérfanos si existen.
8. Registrar compras sin pago asociado si existen.
9. Registrar faltantes documentales.
10. Preparar checklist para revisión humana.
```

DIFFERENCE_LOGGING:

```text
Registrar diferencias como señales visibles, no como conclusiones finales.

Formato mínimo:
- difference_ref
- familia
- referencia_origen
- monto_declarado_A
- monto_declarado_B
- diferencia_visible
- tipo: parcial / faltante / huérfano / exceso / no_clasificado
- requiere_revision_humana: sí

No llamar a esto saldo conciliado.
No llamar a esto diferencia final.
```

EVIDENCE_GAP_LOGGING:

```text
Registrar faltantes como brechas documentales.

Formato mínimo:
- gap_ref
- familia
- evidencia_faltante
- referencia_relacionada
- monto_asociado si existe
- impacto_operativo
- próxima acción sugerida

No resolver fiscalmente la brecha.
No inferir validez documental.
```

HUMAN_REVIEW_CHECKLIST:

```text
El responsable humano debe revisar:
- alcance del caso
- evidencia declarada
- totales declarados
- diferencias visibles
- brechas documentales
- límites del entregable
- si el XLSX puede ser usado como apoyo operativo
- si corresponde pedir evidencia adicional
- si el caso debe detenerse por riesgo
```

DELIVERY_PACKAGE:

```text
El paquete de entrega debe incluir:
- XLSX operativo de revisión
- resumen del caso
- totales declarados
- diferencias visibles
- faltantes de evidencia
- checklist de revisión humana
- límites del entregable
- próxima acción segura

El paquete no debe incluir datos sensibles innecesarios ni artefactos operativos dentro del repo.
```

CLIENT_DELIVERY_WORDING:

```text
Usar lenguaje seguro:
- borrador operativo
- evidencia declarada
- diferencias visibles
- faltantes de evidencia
- requiere revisión humana
- archivo de apoyo
- paquete de revisión

Mensaje base:
Te entregamos un borrador operativo con evidencia declarada, diferencias visibles y faltantes de evidencia para revisión humana. Este archivo es un apoyo de trabajo: no es auditoría, certificación, validación fiscal, conciliación definitiva ni resultado contable final.

Evitar:
- auditado
- certificado
- conciliado definitivamente
- validado fiscalmente
- exacto
- cerrado contablemente
```

STOP_CONDITIONS:

```text
Detener si:
- el caso se amplía fuera de la familia aceptada
- falta evidencia mínima
- falta responsable humano
- el cliente exige resultado final
- el operador detecta riesgo fiscal/legal
- se requiere API/OCR/parser
- el XLSX puede interpretarse como dictamen
- no se pueden preservar límites del servicio
```

QUALITY_CHECK:

```text
Antes de cerrar el caso confirmar:
- artefactos operativos fuera del repo
- evidencia declarada, no auditada
- diferencias visibles, no conclusiones finales
- faltantes documentales explícitos
- revisión humana requerida
- wording seguro
- límites preservados
- no claims prohibidos
- git status limpio salvo documento sanitizado si corresponde
```

NEXT_SAFE_ACTION:

```text
PREPARE_REAL_CLIENT_OPERATOR_PACKET_OR_RUN_THIRD_CONTROLLED_PILOT
```

COMMIT_READY:

```text
YES
```
