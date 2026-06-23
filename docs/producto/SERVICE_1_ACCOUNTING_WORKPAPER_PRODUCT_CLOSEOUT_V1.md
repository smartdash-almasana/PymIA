# SERVICE_1_ACCOUNTING_WORKPAPER_PRODUCT_CLOSEOUT_V1

VEREDICT:

```text
ACCOUNTING_WORKPAPER_PRODUCT_UNIT: CLOSED_AS_SERVICE_1_PRODUCT_UNIT
```

PRODUCT_UNIT:

```text
Papel de trabajo contable asistido para Servicio 1.
```

POSITIONING:

```text
Herramienta basada en archivos para ordenar evidencia, declarar estructura de revisión y entregar un paquete de trabajo owner/operator-facing.
No es auditoría.
No es certificación fiscal.
No es conciliación final.
No es automatización contable productiva.
```

IMPLEMENTED_CHAIN:

```text
accounting_workpaper_contract
  -> accounting_workpaper_manifest_model
  -> accounting_human_review_gate
  -> accounting_workpaper_draft_packet
  -> service_1_xlsx_delivery
```

LAST_IMPLEMENTED_BLOCK:

```text
194da35 feat(pymia-live): add accounting workpaper draft packet
```

OWNER_RECEIVES:

```text
Un paquete claro de revisión que informa:
- qué alcance fue declarado
- qué evidencia fue declarada como recibida
- qué plantilla o estructura de papel de trabajo fue declarada
- si el paquete está listo o bloqueado
- qué falta resolver
- qué no debe interpretarse como conclusión contable o fiscal
```

OPERATOR_RECEIVES:

```text
Un artefacto de control para revisar:
- estado del contrato de papel de trabajo
- estado del manifiesto de evidencia y plantilla
- estado de la revisión humana
- readiness flags
- blocked reasons
- next allowed action
- claims prohibidos
```

DELIVERABLE:

```text
XLSX Service 1 generado desde Service1XlsxDeliveryInputV1.
El XLSX es un paquete de revisión/borrador, no un papel de trabajo final.
```

SELLABLE_SCOPE:

```text
Servicio asistido para ordenar papeles de trabajo contables iniciales.
Se puede vender como:
- revisión de alcance documental
- organización de evidencia recibida
- preparación de paquete borrador para contador/operador
- checklist de faltantes y restricciones
- salida XLSX de revisión
```

CUSTOMER_PROBLEM_SOLVED:

```text
Reduce desorden documental antes de que el contador trabaje.
Evita que evidencia, plantilla, período, responsable y área de revisión queden implícitos.
Convierte archivos y declaraciones sueltas en un paquete revisable.
```

FORBIDDEN_CLAIMS:

```text
No genera papel de trabajo final.
No certifica evidencia suficiente.
No certifica conclusión contable.
No certifica conclusión fiscal.
No ejecuta plantilla.
No lee archivos soporte.
No genera asientos contables.
No valida impuestos.
No reemplaza criterio del contador.
No autoriza uso productivo.
```

OUT_OF_SCOPE:

```text
Parser de archivos reales.
OCR.
PDF parser.
Ejecución de plantillas Excel.
Cálculos fiscales.
Asientos automáticos.
Conciliación final.
Auditoría certificada.
Integraciones externas.
Mercado Pago API.
Banco API.
LLM runtime.
FSM changes.
vertical_slice.py.
```

CURRENT_PRODUCT_MATURITY:

```text
PRE_SELLABLE_INTERNAL_TOOLKIT
```

REASON:

```text
La cadena técnica existe y es testeable, pero todavía falta probarla con un caso documental real y ajustar la forma comercial del entregable.
```

PILOT_REQUIREMENTS:

```text
1. Conseguir un caso real simple de cliente o contador.
2. Recibir evidencia soporte no sensible o anonimizada.
3. Definir una plantilla de papel de trabajo mínima.
4. Ejecutar flujo manual/asistido sin parser.
5. Generar XLSX de revisión.
6. Validar si el contador entiende el paquete sin explicación técnica.
7. Registrar faltantes, confusiones y mejoras de wording.
```

PILOT_INPUTS_MINIMUM:

```text
periodo
cliente
area_revision
responsable
evidencia_soporte declarada
plantilla_papel_trabajo declarada
revisión humana aprobada para sandbox
```

COMMERCIAL_LANGUAGE_ALLOWED:

```text
Ordenamos tu evidencia contable para que el contador trabaje con menos fricción.
Preparamos un paquete de revisión con alcance, evidencia declarada, faltantes y límites.
Entregamos un XLSX de trabajo asistido para revisión humana.
```

COMMERCIAL_LANGUAGE_FORBIDDEN:

```text
Auditamos tus papeles.
Certificamos tus datos.
Calculamos impuestos definitivos.
Generamos asientos automáticos.
Conciliamos todo automáticamente.
Reemplazamos al contador.
```

RECOMMENDED_PRICE_LOGIC:

```text
Cobrar como servicio asistido de ordenamiento y preparación documental, no como software autónomo ni como auditoría.
```

NEXT_SAFE_ACTION:

```text
SERVICE_1_ACCOUNTING_WORKPAPER_PILOT_SCRIPT_V1
```

NEXT_SAFE_ACTION_MODE:

```text
DOC ONLY
Definir guion operativo para correr un piloto real con contador/cliente.
No código.
No parser.
No runtime.
```

COMMIT_READY:

```text
YES
```
