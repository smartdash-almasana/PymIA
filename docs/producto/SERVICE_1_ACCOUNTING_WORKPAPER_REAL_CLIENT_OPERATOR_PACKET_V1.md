# SERVICE_1_ACCOUNTING_WORKPAPER_REAL_CLIENT_OPERATOR_PACKET_V1

VEREDICT:

```text
REAL_CLIENT_OPERATOR_PACKET_V1: CREATED
```

PURPOSE:

```text
Preparar el paquete operativo mínimo para que un operador pueda iniciar un caso real con cliente para el microservicio asistido de Servicio 1:
Papel de trabajo contable asistido.

El paquete reduce improvisación, evita pedir datos innecesarios y preserva límites comerciales, contables y fiscales.
```

WHEN_TO_USE:

```text
Usar sólo para casos:
- simples
- acotados
- con período definido
- con archivos tabulares simples
- con familia operativa soportada
- con responsable humano de revisión
- con aceptación explícita de límites del servicio

Familias soportadas actualmente:
- ventas declaradas vs cobros declarados
- compras declaradas vs pagos declarados
```

WHEN_NOT_TO_USE:

```text
No usar para:
- auditoría
- certificación
- validación fiscal
- conciliación definitiva
- asientos automáticos
- resultado contable final
- garantía de exactitud
- reemplazo del contador
- API bancaria
- Mercado Pago API
- Mercado Libre API
- OCR
- parser automático nuevo
- casos con inspección fiscal activa
- casos con reclamo legal activo
- casos sin responsable humano de revisión
- casos multi-período o multi-moneda sin recorte
```

CLIENT_FIRST_MESSAGE:

```text
Hola. Podemos ayudarte a ordenar la evidencia de un caso simple en un borrador operativo para revisión humana.

Para empezar necesitamos un período concreto, una planilla simple de ventas/cobros o compras/pagos, una nota breve del problema y el nombre de la persona que revisará el resultado.

La entrega es un XLSX de revisión con evidencia declarada, diferencias visibles, faltantes y límites. No es auditoría, certificación, validación fiscal ni conciliación definitiva, y no reemplaza al contador.
```

CLIENT_FILE_REQUEST:

```text
Para iniciar el caso, pedir sólo evidencia mínima:

1. Período a revisar.
2. Planilla de ventas/cobros o compras/pagos.
3. Nota breve del problema o duda principal.
4. Responsable humano de revisión.
5. Archivos complementarios si ya existen.

No pedir:
- credenciales
- claves fiscales
- accesos bancarios
- acceso a Mercado Pago
- acceso a Mercado Libre
- exportaciones masivas sin recorte
- documentación de períodos no involucrados
```

CLIENT_CONTEXT_FORM:

```text
nombre_empresa:
responsable:
periodo:
familia_operativa: ventas_cobros / compras_pagos
problema_expresado:
archivos_disponibles:
archivos_faltantes_conocidos:
expectativa_del_cliente:
responsable_humano:
aceptacion_limites: SI/NO
```

CLIENT_BOUNDARY_ACCEPTANCE:

```text
Antes de aceptar el caso, confirmar explícitamente que el cliente entiende y acepta:

- el entregable es un borrador operativo
- el XLSX es de revisión
- la evidencia es declarada, no auditada
- requiere revisión humana
- no es auditoría
- no es certificación
- no es conciliación definitiva
- no es validación fiscal
- no reemplaza al contador
- no garantiza exactitud
```

OPERATOR_PRECHECK:

```text
1. Confirmar período único.
2. Confirmar empresa/cliente.
3. Confirmar familia operativa soportada.
4. Confirmar archivos tabulares simples o archivo base suficiente.
5. Confirmar responsable humano.
6. Confirmar aceptación de límites.
7. Verificar que no se pidan APIs, OCR ni parser automático nuevo.
8. Verificar que el cliente no espere resultado final.
9. Verificar que el caso no tenga riesgo fiscal/legal activo.
10. Verificar que los artefactos se guardarán fuera del repo.
```

CASE_ACCEPTANCE_DECISION:

```text
ACCEPT si:
- el caso es simple y acotado
- hay período definido
- hay familia operativa soportada
- hay evidencia mínima disponible
- hay responsable humano
- el cliente acepta límites
- no se requieren API/OCR/parser
- no se promete resultado contable o fiscal final
```

CASE_REJECTION_DECISION:

```text
REJECT o REDUCE_SCOPE si:
- el caso pide auditoría
- el caso pide certificación
- el caso pide validación fiscal
- el caso pide conciliación definitiva
- el caso pide asientos automáticos
- el caso requiere API/OCR/parser
- no hay responsable humano
- no hay período definido
- faltan archivos mínimos
- el cliente no acepta límites
```

CASE_SCOPE_REDUCTION:

```text
Si el caso es amplio, reducirlo a:
- un período
- una familia operativa
- un conjunto mínimo de archivos
- una pregunta operativa principal
- un responsable humano

Ejemplo:
De “revisar toda la contabilidad” a “ordenar ventas declaradas vs cobros declarados de abril 2026 para revisión humana”.
```

REAL_CLIENT_FOLDER_STRUCTURE:

```text
Crear carpeta local fuera del repo:

E:\BuenosPasos\smartbridge\PymIA-local-artifacts\real_client_cases\<CASE_ID>\

Subcarpetas:
01_contexto\
02_evidencia_base\
03_outputs_operativos\
04_notas_revision\
05_entrega_cliente\

No commitear carpetas de clientes reales.
No subir XLSX reales.
No subir datos reales al repo.
No subir outputs operativos reales.
```

INPUT_FILE_NAMING:

```text
Usar nombres trazables, mínimos y sin datos sensibles.

Ejemplos:
ventas_declaradas_<periodo>.xlsx
cobros_declarados_<periodo>.xlsx
compras_declaradas_<periodo>.xlsx
pagos_declarados_<periodo>.xlsx
nota_contexto_<case_id>.txt
faltantes_declarados_<case_id>.txt

Evitar:
- CUIT reales en nombre de archivo
- nombres de clientes finales
- números completos de cuenta
- credenciales
- tokens
- claves fiscales
```

EVIDENCE_LOG_TEMPLATE:

```text
case_id:
cliente_anonimizado:
periodo:
familia_operativa:
responsable_humano:
archivo_recibido:
tipo_evidencia:
fecha_recepcion:
contiene_datos_sensibles: SI/NO
evidencia_declarada_no_auditada: SI
faltantes_detectados:
notas_operador:
```

OPERATOR_EXECUTION_CHECKLIST:

```text
1. Crear carpeta local fuera del repo.
2. Registrar contexto del cliente.
3. Guardar evidencia recibida localmente.
4. Completar evidence log.
5. Confirmar límites aceptados.
6. Seleccionar flujo: ventas/cobros o compras/pagos.
7. Registrar totales declarados si los archivos lo permiten.
8. Registrar diferencias visibles.
9. Registrar faltantes de evidencia.
10. Preparar XLSX operativo de revisión.
11. Verificar wording seguro.
12. Confirmar revisión humana requerida.
13. Preparar mensaje de entrega.
14. Registrar post-delivery review.
```

HUMAN_REVIEW_CHECKLIST:

```text
El responsable humano debe revisar:
- alcance del caso
- evidencia declarada
- diferencias visibles
- faltantes de evidencia
- límites del entregable
- si el XLSX sirve como apoyo operativo
- si corresponde pedir evidencia adicional
- si el caso debe detenerse o reducirse
- si hay riesgo contable/fiscal que excede el servicio
```

DELIVERY_PACKAGE_TEMPLATE:

```text
El paquete de entrega debe incluir:
- XLSX operativo de revisión
- resumen del caso
- diferencias visibles
- faltantes de evidencia
- checklist de revisión humana
- límites del entregable
- próxima acción sugerida

El paquete no debe incluir:
- dictamen
- certificación
- validación fiscal
- conciliación definitiva
- asientos automáticos
- garantía de exactitud
```

CLIENT_DELIVERY_MESSAGE:

```text
Te compartimos un borrador operativo de revisión.

El archivo organiza evidencia declarada, muestra diferencias visibles, registra faltantes de evidencia y deja una próxima acción sugerida para revisión humana.

Este entregable es un apoyo de trabajo. No es auditoría, no es certificación, no es conciliación definitiva, no es validación fiscal y no reemplaza al contador. Las conclusiones finales deben quedar a cargo del responsable humano de revisión.
```

POST_DELIVERY_REVIEW:

```text
Registrar después de entregar:
- si el cliente entendió los límites
- si el XLSX fue útil
- si el responsable humano pudo revisar
- qué faltantes fueron relevantes
- qué diferencias visibles generaron acción
- qué wording generó dudas
- si el caso debe continuar, cerrarse o reducirse
```

STOP_CONDITIONS:

```text
Detener si:
- el cliente usa lenguaje de auditoría/certificación/cierre final
- el cliente exige exactitud garantizada
- falta responsable humano
- faltan archivos mínimos
- aparece necesidad de API/OCR/parser
- aparece riesgo fiscal/legal activo
- el caso excede ventas/cobros o compras/pagos
- el operador no puede explicar límites
- el XLSX puede interpretarse como dictamen
```

NEXT_SAFE_ACTION:

```text
RUN_FIRST_REAL_CLIENT_CASE_UNDER_OPERATOR_SUPERVISION
```

COMMIT_READY:

```text
YES
```
