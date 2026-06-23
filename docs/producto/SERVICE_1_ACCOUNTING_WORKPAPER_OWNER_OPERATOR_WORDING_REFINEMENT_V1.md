# SERVICE_1_ACCOUNTING_WORKPAPER_OWNER_OPERATOR_WORDING_REFINEMENT_V1

VEREDICT:

```text
ACCOUNTING_WORKPAPER_OWNER_OPERATOR_WORDING_REFINEMENT_V1: CREATED_AS_DOC_ONLY_SAFE_LANGUAGE_REFINEMENT
```

PURPOSE:

```text
Refinar el lenguaje owner/operator/comercial de la unidad cerrada de Servicio 1:
Papel de trabajo contable asistido.
El objetivo es reducir riesgo semántico/comercial y evitar claims de auditoría,
certificación, conciliación final o reemplazo del contador.
```

REFERENCE_CHAIN:

```text
accounting_workpaper_contract
  -> accounting_workpaper_manifest_model
  -> accounting_human_review_gate
  -> accounting_workpaper_draft_packet
  -> service_1_xlsx_delivery
```

OWNER_LANGUAGE:

```text
Hablar en lenguaje claro, prudente y orientado a apoyo.
El dueño debe entender:
- qué evidencia fue ordenada o declarada
- qué falta para seguir
- qué parte revisará una persona
- qué límites tiene el entregable
- que no recibe un dictamen ni una conclusión final

Usar tono de acompañamiento operativo, no de validación técnica final.
```

OPERATOR_LANGUAGE:

```text
Hablar en lenguaje de control, readiness y handoff.
El operador debe ver:
- estado del contrato
- estado del manifest
- estado del human review gate
- bloqueos
- próxima acción segura
- claims prohibidos

Usar lenguaje de revisión, trazabilidad y preparación.
No usar lenguaje de cierre contable o fiscal.
```

XLSX_LANGUAGE:

```text
El XLSX debe describirse como:
- entregable de trabajo
- borrador operativo
- paquete de revisión
- archivo de apoyo

Nunca como dictamen, conciliación final, auditoría, certificación,
o resultado contable definitivo.
```

PILOT_LANGUAGE:

```text
Durante piloto usar expresiones como:
- piloto asistido
- revisión preliminar
- evidencia ordenada para revisión humana
- paquete borrador para contador/operador

Debe quedar explícito que el piloto no prueba automatización contable final
ni reemplazo del criterio profesional.
```

ALLOWED_PHRASES:

```text
papel de trabajo asistido
borrador operativo
paquete de revisión
evidencia ordenada
pendiente de revisión humana
insumos para análisis contable
checklist para contador
archivo de apoyo
no reemplaza criterio profesional
no constituye auditoría ni certificación
conciliación preliminar (solo si se aclara que no es final)
revisión documental asistida
estructura de revisión declarada
faltantes identificados para revisión
```

FORBIDDEN_PHRASES:

```text
auditoría
certificación
validación fiscal
conciliación definitiva
asientos automáticos
reemplaza al contador
garantiza exactitud
cumple normativa fiscal
apto presentación
resultado contable final
dictamen
cierre fiscal
saldo validado definitivamente
trabajo final listo para presentar
```

RISKY_PHRASES_TO_REWRITE:

| Frase riesgosa | Reescritura segura |
|---|---|
| auditamos tu información | ordenamos tu evidencia para revisión humana |
| certificamos tus papeles | preparamos un paquete de revisión documental |
| conciliación definitiva | conciliación preliminar pendiente de revisión humana |
| validación fiscal | apoyo documental sin validación fiscal |
| resultado contable final | borrador operativo para análisis contable |
| reemplaza al contador | no reemplaza criterio profesional del contador |
| garantiza exactitud | ayuda a estructurar evidencia y faltantes |
| apto para presentar | útil para revisión interna o con tu contador |
| papel de trabajo final | borrador de papel de trabajo asistido |
| asientos automáticos | no genera asientos contables |
| auditoría preliminar | revisión documental asistida |
| cierre conciliado | estado preliminar sujeto a revisión humana |

OWNER_SUMMARY_CANDIDATES:

```text
Preparamos un borrador operativo con la evidencia declarada, faltantes y límites para que puedas revisarlo con tu contador.
Ordenamos tus insumos en un paquete de revisión; no es un papel final ni una certificación.
Este archivo te ayuda a conversar con tu contador con más claridad sobre qué hay, qué falta y qué sigue.
Generamos un paquete de apoyo para revisión humana obligatoria; no reemplaza criterio profesional.
```

OPERATOR_SUMMARY_CANDIDATES:

```text
Paquete de revisión owner/operator listo para handoff, con human review gate obligatorio y sin autorización de runtime.
Borrador operativo generado desde contrato, manifiesto y revisión humana; pendiente de criterio profesional.
Artefacto de control para revisar readiness, bloqueos, faltantes y claims prohibidos antes de compartir con owner.
Salida estructurada para revisión documental asistida; no constituye cierre contable ni fiscal.
```

XLSX_SECTION_LABELS:

```text
Resumen de revisión
Evidencia declarada
Faltantes identificados
Límites del paquete
Claims prohibidos
Notas para revisión humana
Próxima acción segura
Checklist para contador
Estado del borrador operativo
```

COMMERCIAL_COPY_SAFE:

```text
Ordenamos evidencia contable para que el contador reciba el caso más claro.
Preparamos un paquete de revisión con faltantes, límites y estructura declarada.
Entregamos un XLSX de apoyo para revisión humana, no un dictamen.
Ayudamos a transformar documentación dispersa en un borrador operativo revisable.
Servicio asistido para ordenar evidencia antes del análisis contable.
```

COMMERCIAL_COPY_FORBIDDEN:

```text
Auditamos tu contabilidad.
Certificamos tus papeles de trabajo.
Validamos tus impuestos.
Conciliamos automáticamente de forma final.
Reemplazamos a tu contador.
Garantizamos exactitud contable.
Dejamos tu legajo listo para presentar.
Generamos asientos automáticos.
```

NEXT_SAFE_ACTION:

```text
Usar este refinamiento de lenguaje para revisar:
- owner_summary
- operator_summary
- labels del XLSX
- copy piloto/comercial

Antes de cualquier difusión externa, confirmar que:
- el XLSX se describe como entregable de trabajo, no dictamen
- el contador/operador conserva control profesional
- PymIA ordena, estructura y prepara evidencia
- el human review gate es obligatorio
- no existen claims fiscales ni contables finales
```

COMMIT_READY:

```text
YES
```
