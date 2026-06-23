# SERVICE_1_ACCOUNTING_WORKPAPER_PILOT_INTAKE_PACKET_V1

VEREDICT:

```text
ACCOUNTING_WORKPAPER_PILOT_INTAKE_PACKET_V1: CREATED_AS_DOC_ONLY_PILOT_INTAKE_PACKET
```

PURPOSE:

```text
Definir el paquete documental de intake para correr un piloto real de la unidad
“Papel de trabajo contable asistido” con entrada clara, evidencia mínima,
condiciones de bloqueo y expectativas seguras de entrega.
```

SOURCE_CHAIN:

```text
accounting_workpaper_contract
  -> accounting_workpaper_manifest_model
  -> accounting_human_review_gate
  -> accounting_workpaper_draft_packet
  -> service_1_xlsx_delivery
```

CLIENT_INTAKE_MESSAGE:

```text
Hola. Para preparar tu papel de trabajo asistido, necesitamos recibir un conjunto acotado de archivos y notas de contexto.

La idea no es pedir todo ni abrir un proceso complejo: buscamos armar un borrador operativo con evidencia ordenada, faltantes visibles y una base clara para revisión humana.

Podés enviarnos los archivos que ya tengas disponibles y una nota breve con período, área a revisar y responsable interno o contador que lo revisará.
```

FILES_TO_REQUEST:

```text
- Excel de ventas
- Excel de cobros
- extracto bancario
- liquidaciones de medios de pago
- comprobantes relevantes
- notas del contador u operador
```

MINIMUM_EVIDENCE:

```text
Para aceptar el piloto como caso válido, pedir al menos:
- período definido
- cliente o empresa identificada
- área de revisión definida
- responsable de revisión humana identificado
- al menos un archivo base de operación (ventas, cobros o extracto bancario)
- al menos una nota operativa que explique qué se quiere ordenar o revisar
- estructura mínima declarada de trabajo o expectativa de revisión
```

OPTIONAL_EVIDENCE:

```text
Útil pero no obligatoria para el primer piloto:
- planilla histórica del mismo período anterior
- referencias internas del contador
- listado de dudas del cliente
- observaciones sobre diferencias ya detectadas
- resumen manual de comprobantes faltantes
- archivo complementario de caja o compras si ayuda a entender el caso
```

DO_NOT_REQUEST_YET:

```text
- acceso bancario
- acceso API de Mercado Pago
- acceso API de Mercado Libre
- credenciales
- claves fiscales
- parser automático de PDFs
- OCR de comprobantes
- exportaciones masivas de sistemas externos
- evidencia de múltiples períodos sin recorte claro
- documentación legal o fiscal compleja fuera del caso puntual
```

OPERATOR_INTAKE_CHECKLIST:

```text
1. Confirmar período.
2. Confirmar cliente o empresa.
3. Confirmar área de revisión.
4. Confirmar responsable de revisión humana.
5. Verificar que exista al menos un archivo base de operación.
6. Verificar que exista una nota de contexto del cliente, contador u operador.
7. Confirmar que el caso se entiende como paquete de revisión y no como cierre final.
8. Confirmar que no se prometieron claims prohibidos.
9. Confirmar que no se pidió acceso a APIs, OCR ni parser automático.
10. Confirmar que el entregable esperado será un XLSX operativo y no un dictamen.
```

BLOCKING_CONDITIONS:

```text
- no hay período definido
- no hay cliente o empresa identificada
- no hay área de revisión definida
- no hay responsable de revisión humana
- no existe evidencia mínima base
- el cliente espera conciliación definitiva
- el cliente espera validación fiscal
- el cliente espera resultado contable final
- el caso requiere APIs, OCR, parser o automatización fuera de alcance
- el caso mezcla demasiados frentes sin recorte claro
```

SAFE_ACCEPTANCE_CRITERIA:

```text
Aceptar el piloto sólo si:
- el caso está recortado a un período y un frente concreto
- la evidencia mínima existe
- el objetivo es ordenar, estructurar o preparar revisión
- el cliente acepta que el XLSX es un entregable operativo
- el contador u operador conserva control profesional
- queda explícita la revisión humana requerida
- no se prometen claims contables ni fiscales finales
```

PILOT_FOLDER_STRUCTURE:

```text
piloto_cliente_periodo/
  01_contexto/
    - nota_cliente.txt
    - nota_operador.txt
  02_evidencia_base/
    - ventas/
    - cobros/
    - extracto_bancario/
    - medios_de_pago/
  03_comprobantes_relevantes/
  04_faltantes_detectados/
  05_borrador_revision/
    - xlsx_entregable/
    - notas_revision_humana/
```

DELIVERY_EXPECTATION:

```text
La entrega esperada del piloto es:
- un XLSX operativo de revisión
- un borrador operativo con evidencia ordenada
- faltantes y límites explícitos
- checklist para contador
- próxima acción segura

No se entrega dictamen, validación fiscal, conciliación final ni resultado contable definitivo.
```

HUMAN_REVIEW_REQUIRED:

```text
La revisión humana es obligatoria.
El contador u operador debe revisar el borrador operativo antes de usarlo como insumo de trabajo.
PymIA no reemplaza criterio profesional ni habilita uso productivo automático.
```

CLIENT_BOUNDARY_NOTICE:

```text
Este servicio prepara un papel de trabajo asistido y un archivo de apoyo para revisión.
No emitimos dictamen.
No realizamos auditoría.
No certificamos evidencia.
No validamos impuestos.
No hacemos conciliación definitiva.
No generamos asientos automáticos.
El control profesional sigue en manos del contador u operador responsable.
```

NEXT_SAFE_ACTION:

```text
Usar este intake packet como base para pedir evidencia real de un primer piloto acotado,
sin ampliar alcance técnico ni comercial antes de validar claridad, utilidad y límites del entregable.
```

COMMIT_READY:

```text
YES
```
