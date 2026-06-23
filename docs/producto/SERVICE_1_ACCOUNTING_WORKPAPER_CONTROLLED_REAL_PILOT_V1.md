# SERVICE_1_ACCOUNTING_WORKPAPER_CONTROLLED_REAL_PILOT_V1

VEREDICT:

```text
CONTROLLED_REAL_PILOT_PROTOCOL_V1: CREATED
```

PURPOSE:

```text
Definir el protocolo operativo mínimo para ejecutar el primer piloto real controlado de la unidad de Servicio 1:
Papel de trabajo contable asistido.

El protocolo permite validar utilidad real con cliente/contador sin abrir deriva técnica ni comercial.
```

PILOT_SCOPE:

```text
Piloto real controlado, manual/asistido, con caso simple y acotado.

Debe tener:
- período definido
- cliente/empresa identificada
- área de revisión definida
- evidencia mínima declarada
- responsable humano identificado
- aceptación explícita de límites del servicio
- XLSX operativo como entregable de trabajo
```

PILOT_NON_GOALS:

```text
No dictamen.
No auditoría.
No certificación.
No validación fiscal.
No conciliación definitiva.
No resultado contable final.
No asientos automáticos.
No reemplazo del contador.
No parser automático.
No OCR.
No APIs externas.
No Mercado Pago API.
No Mercado Libre API.
No banco API.
No runtime productivo.
```

CLIENT_SELECTION_CRITERIA:

```text
Seleccionar sólo cliente/contador que acepte:
- caso simple
- período único
- frente documental acotado
- evidencia disponible mínima
- revisión humana obligatoria
- entrega como borrador operativo
- límites explícitos del servicio
```

ACCEPTED_CASE_TYPES:

```text
- revisión mensual simple de ventas
- revisión documental preliminar de compras
- ordenamiento de caja simple
- legajo mensual de evidencias
- preparación de documentación para contador
- caso con pocos archivos y objetivo claro
```

REJECTED_CASE_TYPES:

```text
- inspección fiscal activa
- reclamo legal o fiscal
- deuda tributaria compleja
- múltiples períodos sin recorte
- múltiples monedas
- Mercado Pago complejo
- conciliación bancaria definitiva
- cierre contable o fiscal
- generación de asientos
- casos que requieran API, OCR o parser
- casos sin responsable humano
```

CLIENT_INPUTS_REQUIRED:

```text
- período
- cliente o empresa
- área de revisión
- responsable de revisión humana
- al menos un archivo base de operación
- nota breve de contexto
- objetivo declarado: ordenar, revisar o preparar evidencia
- estructura mínima esperada o plantilla declarada
- aceptación de que la evidencia será declarada, no auditada
- aceptación de que el XLSX es operativo, no dictamen
```

OPERATOR_PRECHECK:

```text
1. Confirmar período único.
2. Confirmar cliente/empresa.
3. Confirmar área de revisión.
4. Confirmar responsable humano.
5. Confirmar evidencia mínima disponible.
6. Confirmar nota de contexto.
7. Confirmar que el cliente no espera resultado final.
8. Confirmar que no se requiere API, OCR ni parser.
9. Confirmar que no se prometieron claims prohibidos.
10. Confirmar que el entregable será XLSX operativo de revisión.
```

HUMAN_REVIEW_REQUIREMENT:

```text
La revisión humana es obligatoria.

El contador, operador o responsable designado conserva control profesional.
PymIA ordena, estructura y prepara evidencia declarada.
PymIA no audita, no certifica, no valida impuestos y no reemplaza criterio profesional.
```

PILOT_EXECUTION_STEPS:

```text
1. Recibir caso acotado.
2. Aplicar operator precheck.
3. Registrar límites aceptados por el cliente.
4. Registrar evidencia como declarada, no auditada.
5. Registrar plantilla o estructura esperada.
6. Confirmar human review requirement.
7. Preparar manifest de evidencia.
8. Preparar manifest de plantilla.
9. Preparar draft packet owner/operator.
10. Generar XLSX operativo si corresponde.
11. Revisar paquete con responsable humano.
12. Entregar sólo como borrador operativo de revisión.
13. Registrar feedback post-piloto.
```

DELIVERY_PACKAGE:

```text
El paquete de entrega del piloto puede incluir:
- XLSX operativo de revisión
- resumen de alcance
- evidencia declarada
- faltantes visibles
- límites explícitos
- blocked reasons si existen
- próxima acción segura
- nota de revisión humana requerida
```

CLIENT_BOUNDARY_NOTICE:

```text
Este piloto prepara un papel de trabajo asistido y un archivo de apoyo para revisión humana.

La evidencia se registra como declarada, no auditada.
El XLSX es un borrador operativo, no un dictamen.
No realizamos auditoría.
No certificamos evidencia.
No validamos impuestos.
No hacemos conciliación definitiva.
No generamos asientos automáticos.
El control profesional permanece en manos del contador, operador o responsable humano.
```

STOP_CONDITIONS:

```text
Detener el piloto si:
- no hay período definido
- no hay cliente/empresa identificada
- no hay área de revisión
- no hay responsable humano
- faltan archivos mínimos
- el caso es demasiado amplio
- el cliente exige resultado final
- el cliente exige auditoría o certificación
- el cliente exige validación fiscal
- el cliente exige conciliación definitiva
- el caso requiere API, OCR o parser
- aparece riesgo legal/fiscal no previsto
- el operador no puede explicar límites del entregable
```

EVIDENCE_LOG:

```text
Registrar durante el piloto:
- case_ref
- cliente/empresa anonimizada
- período
- área de revisión
- responsable humano
- archivos recibidos declarados
- archivos faltantes
- nota de contexto recibida
- plantilla/estructura esperada
- blocked reasons
- límites aceptados
- fecha de entrega
- feedback del cliente
- feedback del contador/operador
```

SUCCESS_CRITERIA:

```text
El piloto se considera exitoso si:
- el cliente entendió el límite del servicio
- el cliente pudo entregar evidencia mínima
- el operador pudo preparar el paquete sin parser/OCR/API
- el responsable humano pudo revisar el paquete
- el XLSX fue útil como apoyo operativo
- aparecieron faltantes o bloqueos relevantes y comprensibles
- no se generaron claims contables o fiscales indebidos
- el caso permaneció simple y acotado
```

FAILURE_CRITERIA:

```text
El piloto se considera fallido o no aceptable si:
- el caso fue demasiado amplio
- el cliente exigió resultado final
- faltaron archivos mínimos
- el caso requirió API, OCR o parser
- el caso requirió criterio fiscal/contable final
- no hubo responsable humano
- el cliente interpretó el XLSX como dictamen
- el operador no pudo explicar límites
- el paquete no ayudó al responsable humano
```

POST_PILOT_REVIEW:

```text
Después del piloto registrar:
- qué entendió el cliente
- qué no entendió el cliente
- qué pudo hacer el operador
- qué bloqueos aparecieron
- qué faltantes fueron relevantes
- si el XLSX ayudó al responsable humano
- qué wording generó riesgo
- si el piloto puede repetirse con otro caso simple
- si debe ajustarse intake, oferta o paquete de entrega
```

NEXT_SAFE_ACTION:

```text
RUN_CONTROLLED_REAL_PILOT_WITH_ONE_SIMPLE_CASE
```

COMMIT_READY:

```text
YES
```
