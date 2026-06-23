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
También puede aceptarse parcialmente con advertencias operativas si:
- el caso preserva límites
- existe evidencia mínima suficiente
- el período y la familia operativa son claros
- los faltantes quedan explícitos
- se mantiene revisión humana requerida
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
- el caso mezcla demasiadas familias operativas sin posibilidad real de recorte
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
- duplicados visibles o probables
- datos maestros incompletos
- importes negativos o notas de crédito
- importes expresados de forma comparable
- notas de contexto presentes
- evidencia marcada como declarada, no auditada
- no hay necesidad de API/OCR/parser
```

EDGE_CASE_RULES:

```text
1. INCOMPLETE_SALES_COLLECTIONS
Condición:
- ventas declaradas existentes pero cobros faltantes para varios tickets.
Acción:
- aceptar parcialmente si el período y archivos base son claros.
- marcar faltantes.
- no inventar cobros.
- requerir revisión humana.
Resultado esperado:
PARTIAL_CONTROLLED_PILOT_RUN

2. DUPLICATED_COLLECTIONS
Condición:
- múltiples cobros asociados al mismo ticket o referencia.
Acción:
- marcar posible duplicado.
- no netear automáticamente.
- no decidir si es error o pago parcial sin revisión humana.
Resultado esperado:
PASS_WITH_WARNINGS

3. MISSING_MASTER_DATA
Condición:
- faltan CUIT, proveedor, fecha, medio, referencia o datos maestros relevantes.
Acción:
- aceptar con advertencias si hay evidencia suficiente para borrador operativo.
- registrar datos maestros incompletos.
- pedir saneamiento antes de cierre o registración contable.
Resultado esperado:
PASS_WITH_WARNINGS

4. NEGATIVE_AMOUNTS_AND_CREDIT_NOTES
Condición:
- importes negativos, notas de crédito, devoluciones o ajustes.
Acción:
- separar ajustes de operaciones normales.
- no tratarlos automáticamente como pagos o cobros ordinarios.
- requerir revisión humana.
Resultado esperado:
NEEDS_HUMAN_REVIEW

5. TOO_BROAD_MIXED_CASE
Condición:
- el cliente mezcla ventas, cobros, compras, pagos, banco, Mercado Pago, Mercado Libre, stock o impuestos en un único pedido.
Acción:
- bloquear o recortar.
- proponer una sola familia operativa y un solo período.
- no ejecutar análisis amplio.
Resultado esperado:
BLOCKED_OR_SCOPE_REDUCTION_REQUIRED

6. NO_TRANSACTION_KEYS
Condición:
- existen archivos tabulares pero no hay llaves transaccionales claras.
Acción:
- pedir columnas mínimas o recortar a análisis agregado.
- no hacer matching fino.
- marcar limitación estructural.
Resultado esperado:
NEEDS_SCOPE_REDUCTION
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
- cobros faltantes
- cobros duplicados
- proveedores sin CUIT
- pagos sin comprobante
- importes negativos
- notas de crédito
- casos sin llaves transaccionales
- límites del entregable
- si el XLSX puede ser usado como apoyo operativo
- si corresponde pedir evidencia adicional
- si el caso debe detenerse por riesgo
```

CASE_SCOPE_REDUCTION:

```text
Si el caso no debe bloquearse de inmediato, reducirlo por:
- familia operativa
- período
- tipo de evidencia

Recortes válidos:
- de múltiples frentes a una sola familia operativa soportada
- de varios períodos a un solo período
- de análisis transaccional fino a análisis agregado si faltan llaves mínimas
- de evidencia amplia a un subconjunto mínimo con borrador operativo posible
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
- hay pedido de auditoría
- hay pedido de certificación
- hay pedido de validación fiscal
- hay pedido de conciliación definitiva
- el caso se amplía fuera de la familia aceptada
- el caso es multi-fuente imposible de recortar
- falta evidencia mínima
- hay ausencia total de evidencia mínima
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
- no se inventó evidencia
- no se netearon duplicados automáticamente
- no se trató una nota de crédito como pago normal sin advertencia
- no se prometió exactitud
- se preservó revisión humana
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
