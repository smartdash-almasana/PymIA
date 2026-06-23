# SERVICE_1_ACCOUNTING_WORKPAPER_PILOT_SCRIPT_V1

VEREDICT:

```text
ACCOUNTING_WORKPAPER_PILOT_SCRIPT_V1: CREATED
```

PURPOSE:

```text
Definir el guion operativo para correr un piloto real de la unidad de producto:
Papel de trabajo contable asistido para Servicio 1.
```

REFERENCE_CHAIN:

```text
accounting_workpaper_contract
  -> accounting_workpaper_manifest_model
  -> accounting_human_review_gate
  -> accounting_workpaper_draft_packet
  -> service_1_xlsx_delivery
```

REFERENCE_CLOSEOUT:

```text
SERVICE_1_ACCOUNTING_WORKPAPER_PRODUCT_CLOSEOUT_V1
```

PILOT_MODE:

```text
Manual/asistido.
Sin parser.
Sin runtime.
Sin automatización contable.
Sin claims fiscales.
```

TARGET_USER:

```text
Contador, operador administrativo o dueño PyME que necesita ordenar evidencia antes de revisión contable.
```

PILOT_OBJECTIVE:

```text
Validar si PymIA puede convertir evidencia documental desordenada en un paquete de revisión claro, útil y descargable, sin prometer auditoría ni certificación.
```

MINIMUM_CASE_PROFILE:

```text
Una PyME o contador con un caso simple de revisión mensual.
Área recomendada para piloto inicial:
- ventas
- compras
- caja
- conciliación documental preliminar
- legajo mensual de evidencias
```

DO_NOT_SELECT_FOR_FIRST_PILOT:

```text
Casos con inspección fiscal activa.
Casos con reclamos legales.
Casos con deuda tributaria compleja.
Casos con múltiples monedas.
Casos con Mercado Pago complejo.
Casos que requieran conciliación final.
Casos que requieran asientos automáticos.
```

PRE_PILOT_QUESTIONNAIRE:

```text
1. ¿Qué período se quiere revisar?
2. ¿Qué cliente/empresa corresponde?
3. ¿Qué área se quiere ordenar?
4. ¿Quién será responsable de revisar el paquete?
5. ¿Qué evidencia existe?
6. ¿Qué evidencia falta?
7. ¿Existe una plantilla o estructura esperada de papel de trabajo?
8. ¿El objetivo es ordenar, revisar o cerrar contablemente?
9. ¿Hay datos sensibles que deban anonimizarse?
10. ¿Qué resultado esperaría recibir el contador?
```

INPUTS_TO_REQUEST:

```text
periodo
cliente
area_revision
responsable
evidencia_soporte declarada
plantilla_papel_trabajo declarada
notas del operador
restricciones conocidas
```

EVIDENCE_REQUEST_RULE:

```text
Para el primer piloto no pedir carga masiva ni automatización.
Pedir inventario declarado de evidencia, no procesamiento de archivos.
```

ANONYMIZATION_RULES:

```text
Eliminar o reemplazar:
- CUIT
- DNI
- domicilios
- teléfonos
- emails
- nombres de clientes finales
- números completos de cuenta bancaria
- credenciales
- tokens
- claves fiscales
- datos de acceso

Conservar o reemplazar de forma trazable:
- período
- tipo de documento
- referencia interna anonimizada
- importe si el contador lo autoriza
- fecha si el contador lo autoriza
- área de revisión
- responsable interno anonimizado
```

PILOT_FLOW:

```text
1. Registrar alcance declarado.
2. Registrar fuentes/evidencia declarada.
3. Registrar plantilla o estructura esperada.
4. Confirmar que no se ejecutará parser ni runtime.
5. Confirmar revisión humana para sandbox.
6. Construir manifest de evidencia.
7. Construir manifest de plantilla.
8. Construir draft packet owner/operator.
9. Generar XLSX de revisión si corresponde.
10. Revisar con contador/operador si el paquete es entendible y útil.
```

OWNER_EXPECTED_OUTPUT:

```text
Un resumen simple de:
- qué se intentó ordenar
- qué evidencia fue declarada
- qué estructura se usó
- qué falta
- qué límites tiene el paquete
- cuál es la próxima acción segura
```

OPERATOR_EXPECTED_OUTPUT:

```text
Un paquete de control con:
- estado del contrato
- estado del manifest de evidencia
- estado del manifest de plantilla
- readiness flags
- blocked reasons
- forbidden claims
- next allowed action
```

XLSX_EXPECTED_OUTPUT:

```text
Archivo XLSX de revisión Servicio 1.
Debe ser tratado como borrador de trabajo, no como papel final.
```

SUCCESS_CRITERIA:

```text
El contador entiende el paquete sin explicación técnica extensa.
El dueño entiende qué falta y qué no se está prometiendo.
El operador puede detectar bloqueos y próxima acción.
El XLSX resulta útil como material de revisión.
No se generan claims contables o fiscales indebidos.
No se necesita parser para que el piloto tenga valor.
```

FAILURE_CRITERIA:

```text
El contador no entiende el entregable.
El dueño interpreta el paquete como certificación.
El operador no puede distinguir evidencia declarada de evidencia auditada.
El XLSX no aporta claridad.
El caso exige cálculos, conciliación final o fiscalidad no autorizada.
```

FORBIDDEN_CLAIMS_DURING_PILOT:

```text
No decir: auditamos.
No decir: certificamos.
No decir: conciliamos definitivamente.
No decir: validamos impuestos.
No decir: generamos papel final.
No decir: reemplazamos al contador.
No decir: leímos archivos si no hubo parser autorizado.
No decir: ejecutamos plantilla si no hubo runtime autorizado.
```

ALLOWED_COMMERCIAL_LANGUAGE:

```text
Ordenamos la evidencia para revisión contable.
Preparamos un paquete de trabajo asistido.
Marcamos faltantes y límites.
Entregamos un XLSX de revisión.
Ayudamos al contador a recibir el caso más claro.
```

PILOT_REVIEW_QUESTIONS_FOR_ACCOUNTANT:

```text
1. ¿El paquete ayuda a entender el caso más rápido?
2. ¿Qué sección falta?
3. ¿Qué campo sobra?
4. ¿Qué wording puede generar confusión?
5. ¿El XLSX sirve como material de revisión?
6. ¿Qué evidencia pedirías antes de avanzar?
7. ¿Qué parte no debería ver el dueño?
8. ¿Qué parte sí debería ver el dueño?
9. ¿Pagarías por recibir casos así ordenados?
10. ¿Qué tendría que mejorar para usarlo con clientes reales?
```

PILOT_REVIEW_QUESTIONS_FOR_OWNER:

```text
1. ¿Entendés qué se revisó?
2. ¿Entendés qué falta?
3. ¿Entendés que no es una certificación?
4. ¿El archivo te ayuda a hablar con tu contador?
5. ¿Qué frase te genera dudas?
6. ¿Qué esperabas recibir que no apareció?
```

DECISION_AFTER_PILOT:

```text
PASS:
  El paquete es entendible, útil y no induce claims falsos.

PASS_WITH_WORDING_FIXES:
  La estructura sirve, pero hay que mejorar lenguaje owner/operator.

PARTIAL:
  Sirve para el operador, pero no para dueño o contador.

FAIL:
  No aporta claridad suficiente o genera riesgo de interpretación falsa.
```

DATA_TO_CAPTURE_AFTER_PILOT:

```text
case_type
period_ref
area_revision
evidence_count
template_section_count
blocked_reasons
questions_from_accountant
questions_from_owner
wording_confusions
missing_sections
sellability_signal
```

SELLABILITY_SIGNAL:

```text
HIGH:
  El contador pediría usarlo de nuevo o pagaría por recibir casos así ordenados.

MEDIUM:
  El contador ve utilidad, pero exige cambios de formato/lenguaje.

LOW:
  El paquete no modifica su trabajo o agrega fricción.
```

NEXT_SAFE_ACTION_AFTER_SUCCESSFUL_PILOT:

```text
SERVICE_1_ACCOUNTING_WORKPAPER_OWNER_OPERATOR_WORDING_REFINEMENT_V1
```

NEXT_SAFE_ACTION_AFTER_FAILED_PILOT:

```text
SERVICE_1_ACCOUNTING_WORKPAPER_PILOT_RETROSPECTIVE_V1
```

LIMITS_PRESERVED:

```text
No código.
No tests.
No parser.
No runtime.
No API.
No final workpaper.
No certificación contable.
No certificación fiscal.
No asientos automáticos.
```

COMMIT_READY:

```text
YES
```
