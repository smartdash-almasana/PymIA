# SERVICE_1_ACCOUNTING_WORKPAPER_OPERATOR_RUNBOOK_V1

VEREDICT:

```text
ACCOUNTING_WORKPAPER_OPERATOR_RUNBOOK_V1: CREATED
```

PURPOSE:

```text
Definir el runbook operativo mínimo para que un operador pueda repetir pilotos controlados de la unidad:
Papel de trabajo contable asistido.

El runbook estandariza ejecución manual/asistida sin abrir parser, OCR, APIs, runtime ni claims contables/fiscales finales.
```

WHEN_TO_USE:

```text
Usar este runbook para:
- segundo piloto controlado
- repetición de piloto simple
- onboarding de operador interno
- preparación de paquete de revisión para contador
- control de límites antes de entregar XLSX operativo
```

WHEN_NOT_TO_USE:

```text
No usar este runbook para:
- auditoría
- certificación
- validación fiscal
- conciliación definitiva
- generación de asientos
- casos con API/OCR/parser requerido
- casos Mercado Pago complejos
- cierres contables o fiscales
- casos sin responsable humano
```

OPERATOR_ROLE:

```text
El operador ordena, registra, controla límites y prepara el paquete.
El operador no audita, no certifica, no valida impuestos, no concilia definitivamente y no reemplaza al contador.
```

PRE_RUN_CHECKLIST:

```text
1. Confirmar que el caso es simple.
2. Confirmar período único.
3. Confirmar cliente/empresa.
4. Confirmar área de revisión.
5. Confirmar responsable humano.
6. Confirmar evidencia mínima.
7. Confirmar nota de contexto.
8. Confirmar plantilla o estructura esperada.
9. Confirmar aceptación de límites.
10. Confirmar que no se requiere API, OCR ni parser.
```

REQUIRED_CLIENT_INPUTS:

```text
periodo
cliente_o_empresa
area_revision
responsable_humano
evidencia_base_declarada
nota_contexto
estructura_o_plantilla_declarada
aceptacion_limites
```

CASE_ACCEPTANCE_RULE:

```text
Aceptar sólo si el caso puede ejecutarse como revisión documental asistida.
Rechazar si el cliente espera resultado final, dictamen, certificación, validación fiscal, conciliación definitiva o asientos.
```

FOLDER_RULE:

```text
Los artefactos operativos del piloto deben mantenerse fuera del repo.

Usar carpeta local externa, por ejemplo:
E:\BuenosPasos\smartbridge\PymIA-local-artifacts\_pilot_cases\

No commitear:
- _pilot_cases/
- XLSX de input
- XLSX de output
- archivos del cliente
- notas operativas locales con datos sensibles
```

EVIDENCE_REGISTRATION_RULE:

```text
Registrar evidencia como declarada, no auditada.
No afirmar que un archivo fue leído, parseado o validado si sólo fue declarado.
No afirmar que una diferencia visible es conclusión contable final.
```

EXECUTION_STEPS:

```text
1. Crear carpeta local fuera del repo para el caso.
2. Guardar archivos recibidos en carpeta local externa.
3. Registrar período, cliente, área y responsable humano.
4. Registrar evidencia declarada.
5. Registrar plantilla o estructura declarada.
6. Confirmar límites con cliente/responsable.
7. Preparar manifest de evidencia.
8. Preparar manifest de plantilla.
9. Confirmar human review gate.
10. Preparar draft packet.
11. Generar XLSX operativo si corresponde.
12. Revisar paquete antes de entregar.
13. Entregar como borrador operativo de revisión.
14. Registrar feedback post-piloto.
15. Crear sólo resumen sanitizado en docs/producto si corresponde.
```

DELIVERY_CHECKLIST:

```text
Antes de entregar verificar:
- XLSX identificado como borrador operativo
- evidencia marcada como declarada
- faltantes visibles
- límites explícitos
- claims prohibidos visibles
- próxima acción segura incluida
- revisión humana requerida indicada
- sin lenguaje de auditoría/certificación/resultado final
```

CLIENT_MESSAGE_TEMPLATE:

```text
Te entregamos un borrador operativo de revisión con evidencia declarada, faltantes visibles y límites explícitos.
Este archivo sirve como apoyo para revisión humana con el contador u operador responsable.
No es auditoría, certificación, validación fiscal, conciliación definitiva ni resultado contable final.
```

OPERATOR_STOP_CONDITIONS:

```text
Detener ejecución si:
- falta responsable humano
- falta evidencia mínima
- el caso se amplía sin recorte
- el cliente exige resultado final
- aparece necesidad de API/OCR/parser
- aparece riesgo fiscal/legal no previsto
- el operador no puede explicar límites
- el XLSX podría interpretarse como dictamen
```

HUMAN_REVIEW_GATE:

```text
La revisión humana es obligatoria antes de usar el paquete como insumo de trabajo.
El contador, operador o responsable designado conserva control profesional.
PymIA sólo ordena, estructura y prepara revisión.
```

POST_RUN_LOG:

```text
Registrar después de cada piloto:
- case_ref
- fecha
- período
- área de revisión
- evidencia declarada
- faltantes detectados
- diferencias visibles
- bloqueos
- feedback cliente
- feedback responsable humano
- utilidad del XLSX
- riesgos de wording
- decisión: repetir, ajustar, detener
```

SANITIZED_REVIEW_RULE:

```text
Si se documenta resultado en repo, crear sólo resumen sanitizado.
No incluir archivos operativos, datos sensibles, XLSX ni carpeta del caso.
```

SUCCESS_CRITERIA:

```text
El run es exitoso si:
- el operador pudo seguir pasos sin improvisar
- el cliente entendió límites
- la evidencia mínima fue suficiente para preparar paquete
- el responsable humano pudo revisar
- el XLSX fue útil como apoyo operativo
- los faltantes o bloqueos quedaron claros
```

FAILURE_CRITERIA:

```text
El run falla si:
- el caso requiere cierre contable/fiscal
- el cliente interpreta el entregable como dictamen
- falta responsable humano
- falta evidencia mínima
- se necesita API/OCR/parser
- el paquete no ayuda al responsable humano
- el operador no puede mantener límites
```

BOUNDARIES_PRESERVED:

```text
No código.
No tests.
No runtime.
No parser.
No OCR.
No APIs.
No auditoría.
No certificación.
No validación fiscal.
No conciliación definitiva.
No asientos automáticos.
No resultado contable final.
```

NEXT_SAFE_ACTION:

```text
RUN_SECOND_CONTROLLED_PILOT_WITH_OPERATOR_RUNBOOK
```

COMMIT_READY:

```text
YES
```
