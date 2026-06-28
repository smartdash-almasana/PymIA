# SERVICE_1_PRODUCTIZATION_PACK_V1

## Estado

```text
Tipo: PRODUCTIZATION_PACK
Estado: ACTIVE
Versión: V1
Nombre comercial operativo: Microservicio Asistido de Primeros Auxilios PyME V1
Runtime impact: NONE
Code impact: NONE
Tests impact: NONE
```

---

## 1. Nombre comercial operativo

```text
Microservicio Asistido de Primeros Auxilios PyME V1
```

Posicionamiento:

```text
Servicio asistido bajo supervisión humana que recibe archivos
CSV/XLSX de una PyME y devuelve un XLSX operativo de revisión
como borrador, con evidencia declarada, diferencias visibles,
faltantes de evidencia y límites explícitos.
```

No es producto autónomo.
No es SaaS.
No es API pública.
No es chatbot.
No reemplaza al contador.

---

## 2. Oferta vendible

```text
Revisión asistida de archivos CSV/XLSX y outputs operativos controlados
para dueños PyME y contadores, bajo supervisión humana y con límites
explícitos.
```

Qué incluye:

- recepción y análisis de archivos tabulares (CSV/XLSX)
- aplicación de herramientas determinísticas acotadas (First Aid)
- generación de XLSX operativo de revisión
- declaración de evidencia, faltantes y límites
- revisión humana obligatoria antes de entregar
- mensaje owner-facing con lenguaje seguro

Qué NO incluye:

- auditoría fiscal
- certificación
- conciliación definitiva
- validación contable final
- asientos automáticos
- IVA / IIBB
- APIs bancarias vivas
- OCR
- parser PDF automático
- autonomía completa

---

## 3. Capacidades vendibles hoy

```text
- First Aid toolbox (5 herramientas validadas)
    - precio_margen_basico
    - caja_diaria_triage
    - stock_alertas_basicas
    - gastos_triage
    - proveedores_precio_variacion_triage
- Excel Lab (ingestión estructural + profiling)
- Excel Factory controlada (3 templates mapeados a runtime)
- CSV/XLSX NormalizedTableV1 (frontera común, 47 tests)
- Delivery package (carpeta entregable con README, manifest, hashes)
- QA Delivery Checklist V1 (gate de calidad pre-entrega)
- Delivery Manifest Audit V1 (auditoría contractual de entrega)
- Human Review Gate (revisión humana obligatoria)
```

Estado de madurez:

```text
First Aid:                  IMPLEMENTED_VALIDATED
Excel Lab:                  IMPLEMENTED_MINIMAL_CONTRACT
Excel Factory:              CLOSED_IN_SCOPE_RUNTIME
Stage 5 NormalizedTableV1:  COMPLETE_VERSIONED_CLEAN (47 tests)
Operator Harness:           MANUAL_PROTOCOL_ACTIVE
QA/Delivery/Audit:          DOCUMENTED_AND_APPLIED
```

---

## 4. Entregables

Por cada caso, el cliente recibe:

```text
- XLSX operativo de revisión (fuera del repo)
- carpeta de entrega local con:
    - README_ENTREGA.md
    - manifest.json (inventario con hashes sha256)
    - summary.txt
    - operator_report.txt
    - XLSX operativo
- limitaciones explícitas (en README y XLSX)
- recomendaciones operativas (próxima acción segura)
- declaración de evidencia declarada vs inferencia
- faltantes de evidencia documentados
- diferencias visibles registradas
```

El XLSX incluye cuando aplica:

```text
- Resumen
- Evidencia declarada
- Diferencias visibles
- Faltantes de evidencia
- Advertencias operativas
- Revisión humana
- Límites del entregable
```

Nunca se entrega como:

```text
- dictamen
- auditoría
- certificación
- conciliación definitiva
- resultado contable final
```

---

## 5. Límites comerciales

```text
NO es auditoría fiscal.
NO reemplaza al contador.
NO garantiza exactitud.
NO hace OCR/PDF.
NO es chatbot autónomo.
NO es autonomía completa.
NO es conciliación definitiva.
NO hace IVA / IIBB.
NO genera asientos automáticos.
NO se conecta a APIs bancarias vivas.
NO se conecta a Mercado Pago API.
NO se conecta a Mercado Libre API.
NO valida fiscalmente.
NO aprueba balances.
NO cierra contablemente.
```

Lenguaje obligatorio en toda comunicación:

```text
borrador operativo
evidencia declarada
diferencias visibles
faltantes de evidencia
advertencias operativas
requiere revisión humana
XLSX operativo de revisión
```

Lenguaje prohibido:

```text
auditado
certificado
conciliado definitivamente
validado fiscalmente
exacto
cerrado contablemente
aprobado fiscalmente
reemplaza al contador
garantiza exactitud
listo para presentación fiscal
resultado contable final
```

---

## 6. Cliente ideal inicial

```text
Dueño PyME chico o mediano que:
- tiene archivos CSV/XLSX desordenados
- necesita "sacar algo en limpio" rápido
- no espera reemplazo del contador
- acepta recibir un borrador operativo bajo revisión humana
- entiende que la evidencia es declarada, no auditada
- valora que los faltantes y límites queden explícitos
```

Caso típico:

```text
Dueño con Excel de ventas/cobros o compras/pagos
que necesita una primera lectura ordenada para
tomar decisiones operativas o llevarle algo más
prolijo al contador.
```

---

## 7. Casos aceptables

```text
- revisión de margen y precio sobre una sola fuente
- triage de caja diaria con ingresos/egresos declarados
- alertas básicas de stock mínimo sobre inventario declarado
- orden inicial de gastos por concepto/importe
- variación de precios de proveedores sobre compras declaradas
- ventas declaradas vs cobros declarados (borrador)
- compras declaradas vs pagos declarados (borrador)
- análisis agregado cuando faltan llaves transaccionales
- casos con duplicados marcados para revisión humana
- casos con datos maestros incompletos documentados
```

Condiciones:

```text
- familia soportada
- período definido
- alcance acotado
- evidencia mínima presente o faltantes documentados
- human reviewer identificado
- sin pretensión de auditoría/certificación/conciliación definitiva
```

---

## 8. Casos no aceptables

```text
- auditoría fiscal
- certificación contable
- validación fiscal
- conciliación definitiva
- asientos automáticos
- IVA / IIBB
- APIs bancarias vivas
- Mercado Pago API
- Mercado Libre API
- OCR sobre PDFs
- parser automático de documentos
- casos que exigen resultado contable final
- casos demasiado amplios sin posibilidad de recorte
- casos que piden reemplazo del contador
- casos que exigen garantía de exactitud
```

Si el caso cae aquí:

```text
- bloquear entrega
- explicar alcance
- ofrecer recorte si es posible
- derivar a contador profesional si corresponde
```

---

## 9. Engagement template

```text
ALCANCE:
- Microservicio Asistido de Primeros Auxilios PyME V1.
- Revisión asistida de archivos CSV/XLSX bajo supervisión humana.
- Aplicación de herramientas determinísticas acotadas.
- Generación de XLSX operativo de revisión como borrador.

EVIDENCIA REQUERIDA:
- Archivos tabulares (CSV/XLSX) del período acordado.
- Declaración del problema operativo a revisar.
- Confirmación de columnas mínimas si aplica.
- Identificación del revisor humano obligatorio.

RESULTADO ESPERADO:
- XLSX operativo de revisión con:
    - evidencia declarada
    - diferencias visibles
    - faltantes de evidencia
    - advertencias operativas
    - límites del entregable
- README de entrega con inventario y hashes.
- Mensaje owner-facing con lenguaje seguro.

LÍMITES:
- No es auditoría, certificación, validación fiscal ni conciliación definitiva.
- No reemplaza al contador.
- No garantiza exactitud.
- No usa OCR, parser automático ni APIs vivas.
- La evidencia se considera declarada, no auditada.
- Los faltantes no se infieren ni se completan sin fuente.

REVISIÓN HUMANA:
- Revisión humana obligatoria antes de entregar.
- El entregable se marca como borrador operativo.
- El cliente acepta que requiere revisión humana.

BLOQUEO POR EVIDENCIA INSUFICIENTE:
- Si falta evidencia mínima y no puede documentarse, se bloquea.
- Si el caso excede alcance y no puede recortarse, se bloquea.
- Si el cliente pide auditoría/certificación/conciliación definitiva, se bloquea.
```

---

## 10. Sales one-pager

```text
QUÉ PROBLEMA RESUELVE:

Dueños PyME con archivos CSV/XLSX desordenados necesitan
"sacar algo en limpio" rápido sin esperar un proceso contable
completo. El microservicio aplica herramientas acotadas y
devuelve un XLSX operativo de revisión con evidencia, faltantes
y límites explícitos.

QUÉ RECIBE EL CLIENTE:

- XLSX operativo de revisión con:
    - evidencia declarada
    - diferencias visibles
    - faltantes de evidencia
    - advertencias operativas
    - límites del entregable
- Carpeta de entrega con README, manifest, hashes y resumen.
- Mensaje owner-facing con lenguaje seguro.
- Todo bajo revisión humana obligatoria.

QUÉ DEBE ENVIAR EL CLIENTE:

- Archivos CSV/XLSX del período acordado.
- Descripción breve del problema operativo.
- Confirmación de columnas mínimas si aplica.
- Identificación del revisor humano responsable.

QUÉ NO PROMETE:

- No es auditoría ni certificación.
- No reemplaza al contador.
- No garantiza exactitud final.
- No hace OCR, parser PDF ni APIs bancarias.
- No es autonomía completa ni chatbot libre.
- No genera asientos ni liquida IVA/IIBB.
- No concilia definitivamente.

CÓMO SE ENTREGA:

- El microservicio se ejecuta bajo supervisión humana.
- Se aplican QA checklist + delivery manifest audit + human review gate.
- Se entrega solo como borrador operativo.
- El cliente recibe el XLSX y la carpeta de entrega.
- El revisor humano valida antes de dar por cerrado el caso.
```

---

## Firma

- Documento creado en modo `DOC ONLY`.
- Sin modificación de runtime, tests, CLI, pipeline ni memoria.
- No crea capacidad nueva, empaqueta la existente.
- Próxima acción segura: `RUN_FIRST_REAL_CLIENT_CASE_UNDER_OPERATOR_SUPERVISION`.
