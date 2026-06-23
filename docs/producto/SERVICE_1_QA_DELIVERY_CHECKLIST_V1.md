# SERVICE_1_QA_DELIVERY_CHECKLIST_V1

VEREDICT:

```text
SERVICE_1_QA_DELIVERY_CHECKLIST_V1: CREATED
```

PURPOSE:

```text
Definir el checklist QA de entrega para Servicio 1 V1.

El objetivo es que un operador pueda revisar, antes de entregar al cliente, si un caso de Servicio 1 está seguro para salida bajo el modelo aprobado:
microservicio asistido bajo revisión humana.
```

WHEN_TO_USE:

```text
Usar este checklist antes de entregar cualquier output de Servicio 1 al cliente, especialmente cuando exista:
- XLSX operativo de revisión
- mensaje owner-facing
- paquete operador
- diferencias visibles
- faltantes de evidencia
- human review gate

Este checklist aplica a entregas asistidas, no autónomas.
```

QA_SCOPE:

```text
El checklist valida seguridad de entrega, no exactitud contable final.

Incluye:
- intake recibido
- alcance acotado
- archivos tabulares válidos
- columnas mínimas identificadas o confirmadas
- evidencia declarada separada de inferencia
- diferencias visibles registradas
- faltantes de evidencia registrados
- XLSX operativo revisado
- mensaje owner-facing revisado
- paquete operador revisado
- human review gate aplicado
- claims prohibidos ausentes
- stop conditions no activadas
- próxima acción segura indicada

No incluye:
- auditoría
- certificación
- validación fiscal
- conciliación definitiva
- asientos automáticos
- reemplazo del contador
- garantía de exactitud
- autonomía plena
- APIs vivas
- OCR
- parser automático
- chatbot libre
```

PRE_DELIVERY_CHECKLIST:

```text
[ ] Intake recibido.
[ ] Alcance acotado.
[ ] Familia operativa soportada.
[ ] Período definido.
[ ] Archivos tabulares válidos o archivo base suficiente.
[ ] Columnas mínimas identificadas o confirmadas.
[ ] Evidencia declarada separada de inferencia.
[ ] Diferencias visibles registradas.
[ ] Faltantes de evidencia registrados.
[ ] XLSX operativo revisado.
[ ] Mensaje owner-facing revisado.
[ ] Paquete operador revisado.
[ ] Human review gate aplicado.
[ ] Claims prohibidos ausentes.
[ ] Stop conditions no activadas.
[ ] Próxima acción segura indicada.
```

INPUT_CHECKS:

```text
[ ] Cliente/caso identificado.
[ ] Responsable humano identificado.
[ ] Período definido.
[ ] Problema expresado registrado.
[ ] Archivos recibidos registrados.
[ ] Archivos faltantes conocidos registrados.
[ ] Evidencia marcada como declarada, no auditada.
[ ] No se recibieron credenciales, claves fiscales, tokens ni accesos vivos.
[ ] No se pidieron APIs bancarias, Mercado Pago API ni Mercado Libre API.
```

SCOPE_CHECKS:

```text
[ ] El caso pertenece a una familia soportada.
[ ] El caso está limitado a un período o recorte explícito.
[ ] El caso no mezcla múltiples frentes sin recorte.
[ ] El caso no exige cierre contable final.
[ ] El caso no exige auditoría, certificación ni validación fiscal.
[ ] El caso no requiere OCR ni parser automático nuevo.

Si el caso excede alcance:
- recortar a una familia operativa
- recortar a un período
- pedir evidencia mínima
- bloquear si no puede recortarse
```

EVIDENCE_CHECKS:

```text
[ ] La evidencia declarada está listada.
[ ] Las inferencias están separadas de los datos declarados.
[ ] No se inventó evidencia faltante.
[ ] No se completaron cobros, pagos, proveedores, CUIT, fechas o referencias sin fuente.
[ ] Las diferencias visibles están marcadas como señales de revisión, no como conclusión final.
[ ] Los faltantes de evidencia están registrados.
[ ] Los duplicados posibles están marcados como advertencias operativas.
[ ] Los importes negativos, notas de crédito o ajustes requieren revisión humana.
[ ] Si faltan llaves transaccionales, se marcó limitación estructural o reducción de alcance.
```

XLSX_CHECKS:

```text
[ ] El XLSX se presenta como operativo/de revisión.
[ ] El XLSX no se presenta como dictamen.
[ ] El XLSX diferencia evidencia declarada, diferencias visibles y faltantes.
[ ] El XLSX incluye o acompaña límites del entregable.
[ ] El XLSX no contiene claims de exactitud final.
[ ] El XLSX no contiene datos innecesarios para el caso.
[ ] El XLSX no fue commiteado al repo.
[ ] El XLSX real del cliente queda fuera del repo.
```

OWNER_MESSAGE_CHECKS:

```text
[ ] El mensaje usa lenguaje seguro.
[ ] El mensaje dice borrador operativo.
[ ] El mensaje dice evidencia declarada.
[ ] El mensaje dice diferencias visibles.
[ ] El mensaje dice faltantes de evidencia.
[ ] El mensaje dice requiere revisión humana.
[ ] El mensaje indica próxima acción segura.
[ ] El mensaje no promete exactitud.
[ ] El mensaje no reemplaza al contador.
```

OPERATOR_PACKAGE_CHECKS:

```text
[ ] El paquete operador incluye resumen del caso.
[ ] El paquete operador incluye alcance.
[ ] El paquete operador incluye evidencia recibida.
[ ] El paquete operador incluye diferencias visibles.
[ ] El paquete operador incluye faltantes de evidencia.
[ ] El paquete operador incluye checklist de revisión humana.
[ ] El paquete operador incluye límites del entregable.
[ ] El paquete operador indica stop conditions si existen.
[ ] El paquete operador indica próxima acción segura.
```

HUMAN_REVIEW_GATE_CHECKS:

```text
[ ] Responsable humano identificado.
[ ] Revisión humana requerida explícitamente.
[ ] El entregable no se marca como final sin revisión humana.
[ ] El operador verificó que no haya claims prohibidos.
[ ] El operador verificó que las advertencias operativas estén visibles.
[ ] El operador verificó que los faltantes no hayan sido inferidos ni rellenados.
[ ] El operador verificó que el caso pueda salir como borrador operativo.
```

CLAIMS_CHECKS:

```text
Deben estar ausentes:
[ ] auditado
[ ] certificado
[ ] conciliado definitivamente
[ ] validado fiscalmente
[ ] exacto
[ ] cerrado contablemente
[ ] aprobado fiscalmente
[ ] reemplaza al contador
[ ] garantiza exactitud
[ ] listo para presentación fiscal
[ ] resultado contable final

Deben estar presentes cuando corresponda:
[ ] borrador operativo
[ ] evidencia declarada
[ ] diferencias visibles
[ ] faltantes de evidencia
[ ] advertencias operativas
[ ] requiere revisión humana
```

STOP_CONDITIONS:

```text
Bloquear entrega si:
- falta responsable humano
- falta evidencia mínima
- el caso excede alcance y no puede recortarse
- el cliente pide auditoría
- el cliente pide certificación
- el cliente pide validación fiscal
- el cliente pide conciliación definitiva
- el cliente pide asientos automáticos
- el cliente pide resultado contable final
- el cliente espera reemplazo del contador
- aparecen APIs vivas como requisito
- aparece OCR como requisito
- aparece parser automático nuevo como requisito
- el XLSX puede interpretarse como dictamen
- no hubo revisión humana cuando era obligatoria
- se inventó evidencia o se completaron faltantes sin fuente
```

PASS_CRITERIA:

```text
La entrega puede salir si:
- intake está completo para el alcance aceptado
- alcance está acotado
- archivos tabulares son suficientes para borrador operativo
- columnas mínimas fueron identificadas o confirmadas
- evidencia declarada e inferencia están separadas
- diferencias visibles están registradas
- faltantes de evidencia están registrados
- XLSX operativo fue revisado
- mensaje owner-facing fue revisado
- paquete operador fue revisado
- human review gate fue aplicado
- claims prohibidos están ausentes
- stop conditions no están activadas
- próxima acción segura está indicada
```

FAIL_CRITERIA:

```text
La entrega no puede salir si:
- falta evidencia mínima
- se inventó evidencia
- no hay responsable humano
- el alcance es demasiado amplio
- el caso exige auditoría/certificación/fiscalidad/conciliación definitiva
- el output parece final o exacto
- el XLSX parece dictamen
- faltan diferencias visibles o faltantes cuando el caso los requiere
- no se indicó próxima acción segura
```

REWORK_ACTIONS:

```text
Si falla QA:
1. No entregar.
2. Registrar motivo de bloqueo.
3. Pedir evidencia faltante si corresponde.
4. Recortar alcance si corresponde.
5. Reescribir mensaje owner-facing con lenguaje seguro.
6. Revisar XLSX operativo.
7. Reaplicar human review gate.
8. Repetir QA antes de entregar.
```

DELIVERY_APPROVAL:

```text
APPROVE_DELIVERY sólo si:
- todos los checks críticos están completos
- no hay stop conditions activadas
- el output dice borrador operativo
- el output dice evidencia declarada
- el output dice requiere revisión humana
- el responsable humano está identificado
- la próxima acción segura está indicada

Si alguno de estos puntos falla:
DELIVERY_BLOCKED_OR_REWORK_REQUIRED
```

NEXT_SAFE_ACTION:

```text
RUN_FIRST_REAL_CLIENT_CASE_UNDER_OPERATOR_SUPERVISION
```

COMMIT_READY:

```text
YES
```
