# SERVICE_1_ACCOUNTING_WORKPAPER_SECOND_CONTROLLED_PILOT_PLAN_V1

VEREDICT:

```text
SECOND_CONTROLLED_PILOT_PLAN_V1: CREATED
```

PURPOSE:

```text
Preparar el segundo piloto controlado de la unidad Servicio 1 / Papel de trabajo contable asistido,
usando el operator runbook como guía principal.

El objetivo no es validar nueva funcionalidad.
El objetivo es validar repetibilidad operativa.
```

REFERENCE_CHAIN:

```text
accounting_workpaper_contract
  -> accounting_workpaper_manifest_model
  -> accounting_human_review_gate
  -> accounting_workpaper_draft_packet
  -> service_1_xlsx_delivery
```

REFERENCE_DOCS:

```text
SERVICE_1_ACCOUNTING_WORKPAPER_CONTROLLED_REAL_PILOT_V1
SERVICE_1_ACCOUNTING_WORKPAPER_FIRST_CONTROLLED_PILOT_RESULT_REVIEW_V1
SERVICE_1_ACCOUNTING_WORKPAPER_OPERATOR_RUNBOOK_V1
```

PILOT_OBJECTIVE:

```text
Validar que un operador pueda repetir el proceso con menos improvisación,
manteniendo límites, evidencia declarada, revisión humana y XLSX operativo.
```

PILOT_MODE:

```text
Controlled real pilot.
Manual/asistido.
Sin parser.
Sin OCR.
Sin APIs.
Sin runtime productivo.
Sin nueva herramienta.
```

CASE_SELECTION_RULE:

```text
Elegir un caso distinto al primer piloto, pero igualmente simple.
Debe tener un período único, evidencia mínima disponible y responsable humano identificado.
```

PREFERRED_CASE_TYPES:

```text
1. compras declaradas vs pagos declarados
2. caja simple diaria/semanal
3. ventas declaradas vs cobros declarados de otro período
4. legajo mensual de evidencias para contador
```

REJECTED_CASE_TYPES:

```text
- Mercado Pago complejo
- conciliación bancaria definitiva
- cierre fiscal
- múltiples períodos
- múltiples monedas
- caso sin responsable humano
- caso que requiera API/OCR/parser
- caso con reclamo legal o inspección fiscal
```

INPUTS_REQUIRED:

```text
periodo
cliente_o_empresa_anonimizada
area_revision
responsable_humano
evidencia_base_declarada
nota_contexto
estructura_o_plantilla_declarada
aceptacion_de_limites
```

OPERATOR_PRECHECK:

```text
1. Confirmar que el caso no repite exactamente el piloto 001.
2. Confirmar que el caso es simple y acotado.
3. Confirmar período único.
4. Confirmar área de revisión.
5. Confirmar responsable humano.
6. Confirmar evidencia mínima.
7. Confirmar que el cliente entiende que el XLSX es borrador operativo.
8. Confirmar que no se requiere parser, OCR ni API.
9. Confirmar que no se prometió auditoría, certificación ni conciliación final.
10. Confirmar carpeta local fuera del repo para artefactos.
```

LOCAL_ARTIFACT_RULE:

```text
Todo artefacto operativo del segundo piloto debe vivir fuera del repo.

Ubicación recomendada:
E:\BuenosPasos\smartbridge\PymIA-local-artifacts\_pilot_cases\PILOTO_002\

No commitear:
- _pilot_cases/
- XLSX de input
- XLSX de output
- evidencia del cliente
- notas locales con datos sensibles
```

EXECUTION_STEPS:

```text
1. Crear carpeta local externa para PILOTO_002.
2. Registrar contexto mínimo del caso.
3. Guardar evidencia recibida fuera del repo.
4. Aplicar operator runbook.
5. Registrar evidencia como declarada, no auditada.
6. Registrar plantilla o estructura declarada.
7. Confirmar revisión humana requerida.
8. Preparar paquete de revisión.
9. Generar XLSX operativo si corresponde.
10. Revisar con responsable humano.
11. Registrar fricciones y bloqueos.
12. Crear sólo review sanitizado si el piloto se ejecuta.
```

SUCCESS_CRITERIA:

```text
El segundo piloto será exitoso si:
- el operador puede ejecutar usando el runbook
- hay menos improvisación que en el primer piloto
- el cliente entiende límites del servicio
- la evidencia mínima alcanza para preparar paquete
- el responsable humano puede revisar
- el XLSX sirve como apoyo operativo
- faltantes y bloqueos quedan claros
- no se rompen límites de auditoría/certificación/fiscalidad/conciliación final
```

FAILURE_CRITERIA:

```text
El segundo piloto falla si:
- el caso se vuelve demasiado amplio
- el operador necesita improvisar fuera del runbook
- el cliente exige resultado final
- falta responsable humano
- falta evidencia mínima
- se requiere API/OCR/parser
- el XLSX se interpreta como dictamen
- el paquete no aporta valor operativo
```

MEASURE_REPEATABILITY:

```text
Registrar:
- pasos que el operador pudo seguir sin ayuda
- pasos que generaron duda
- campos que faltaron
- bloqueos detectados
- tiempo percibido de preparación
- utilidad percibida por responsable humano
- claridad del XLSX
- riesgos de wording
```

DO_NOT_EXPAND:

```text
No abrir nuevas capacidades.
No abrir Mercado Pago API.
No abrir Mercado Libre API.
No abrir banco API.
No abrir parser.
No abrir OCR.
No abrir Servicio 2.
No abrir chatbot.
No convertir diferencias visibles en conclusión final.
```

EXPECTED_AFTER_RUN_DOCUMENT:

```text
Si el segundo piloto se ejecuta, crear después un resumen sanitizado:
SERVICE_1_ACCOUNTING_WORKPAPER_SECOND_CONTROLLED_PILOT_RESULT_REVIEW_V1

Sólo doc sanitizado.
Sin artefactos operativos.
Sin XLSX.
Sin datos sensibles.
```

NEXT_SAFE_ACTION:

```text
EXECUTE_SECOND_CONTROLLED_PILOT_WITH_REAL_OR_CONTROLLED_SIMPLE_CASE
```

COMMIT_READY:

```text
YES
```
