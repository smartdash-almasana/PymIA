# SERVICE_2_ADMIN_OPERATIONS_FOUNDATION_V1

## Estado

```text
DOCUMENT_TYPE: SERVICE_FOUNDATION_BOUNDARY
SERVICE: S2_ADMIN_OPERATIONS_V1
STATUS: FOUNDATION_OPENED
RUNTIME_MODIFIED: NO
TESTS_RUN: NO
CODE_CREATED: NO
S1_MODIFIED: NO
AUTOMATION_V2: OUT_OF_SCOPE
```

---

# 1. Objetivo

Abrir Servicio 2 como servicio separado de Servicio 1.

Servicio 2 no es V2 de Servicio 1.
Servicio 2 no es automatización transversal.
Servicio 2 no es chatbot ni agente LLM.

Servicio 2 es una línea de trabajo para resolver problemas administrativos reales después del triage inicial.

---

# 2. Separación de capas

```text
S1_FULL_ASSISTED_V1 = primeros auxilios operativos sobre archivos.
S2_ADMIN_OPERATIONS_V1 = administración profunda asistida con evidencia.
AUTOMATION_V2 = automatización transversal futura para S1/S2.
```

Regla:

```text
No mezclar S1 con S2.
No llamar V2 a Servicio 2.
No meter automatización transversal como si fuera Servicio 2.
```

---

# 3. Qué problema resuelve Servicio 2

Servicio 2 atiende situaciones donde la PyME ya no necesita sólo ordenar archivos, sino resolver circuitos administrativos incompletos o inconsistentes.

Ejemplos:

```text
- esto no cierra;
- faltan comprobantes;
- hay descalce entre banco y caja;
- hay pagos sin imputar;
- hay cobros sin registrar;
- proveedores tienen saldos dudosos;
- clientes tienen cuentas corrientes desordenadas;
- hay diferencias entre planilla interna y extractos;
- el contador necesita papeles de trabajo operativos;
- la administración necesita control mensual recurrente.
```

---

# 4. Diferencia con Servicio 1

## Servicio 1

```text
- recibe archivos XLSX/CSV;
- ordena evidencia inicial;
- ejecuta First Aid;
- entrega resultados preliminares;
- trabaja con caveats fuertes;
- no resuelve administración profunda.
```

## Servicio 2

```text
- cruza fuentes administrativas;
- busca correspondencias;
- detecta pendientes;
- registra descalces;
- pide evidencia faltante;
- arma base de trabajo administrativo;
- integra revisión humana y contador;
- apunta a seguimiento operativo recurrente.
```

---

# 5. Inputs esperados de Servicio 2

Servicio 2 puede recibir, según el frente:

```text
- extractos bancarios;
- planillas internas de caja/banco;
- reportes de Mercado Pago o tarjetas;
- listados de ventas/cobros;
- listados de compras/pagos;
- cuentas corrientes de clientes;
- cuentas corrientes de proveedores;
- comprobantes o referencias administrativas;
- reportes mensuales;
- archivos XLSX/CSV exportados de sistemas contables o administrativos.
```

V1 no exige APIs. Los archivos pueden ser manuales/exportados.

---

# 6. Outputs esperados de Servicio 2

Servicio 2 debe producir paquetes de trabajo administrativos, no dictámenes.

Outputs posibles:

```text
- candidatos de conciliación;
- movimientos bancarios sin imputar;
- movimientos internos sin banco;
- diferencias por importe;
- diferencias por fecha;
- cobros pendientes;
- pagos pendientes;
- comprobantes faltantes;
- saldos a revisar;
- planilla de seguimiento;
- reporte de descalces;
- paquete para contador o responsable administrativo;
- tablero mensual operativo.
```

---

# 7. Claims prohibidos de Servicio 2

Servicio 2 no debe prometer:

```text
- conciliación definitiva;
- auditoría;
- certificación;
- cierre contable;
- saldo real confirmado;
- cumplimiento fiscal;
- liquidación impositiva;
- asientos definitivos;
- detección automática de fraude;
- reemplazo del contador;
- autonomía sin revisión humana.
```

Lenguaje permitido:

```text
- conciliación asistida;
- candidatos de match;
- diferencias visibles;
- pendientes de imputación;
- evidencia faltante;
- saldos a revisar;
- paquete operativo para revisión humana;
- control administrativo preliminar;
- requiere validación del responsable o contador.
```

---

# 8. Primer frente autorizado

Primer frente S2 recomendado:

```text
SERVICE_2_RECONCILIATION_BOUNDARY_CONTRACT_V1
```

Traducción:

```text
Contrato de frontera para conciliación asistida banco/caja/planilla interna.
```

Objetivo del primer frente:

```text
Tomar movimientos bancarios e internos, producir candidatos de match, detectar pendientes, diferencias y faltantes, sin declarar conciliación definitiva.
```

---

# 9. Primer micro-slice técnico posterior

Sólo después del contrato de frontera se podrá abrir código.

Nombre probable:

```text
S2_MICROSLICE_001_RECONCILIATION_MATCH_CANDIDATES
```

Función esperada futura:

```text
input:
- movimientos_banco
- movimientos_internos

output:
- matches_exactos
- matches_probables
- banco_sin_imputar
- interno_sin_banco
- diferencias_importe
- diferencias_fecha
- requires_human_review = true
```

---

# 10. Prohibiciones metodológicas

```text
NO abrir código S2 sin contrato mínimo.
NO reabrir Servicio 1 para meter S2.
NO usar Servicio 2 como excusa para agente LLM.
NO abrir APIs todavía.
NO declarar conciliación definitiva.
NO crear documentación extensa sin habilitar el siguiente slice.
NO crear roadmap gigante.
```

---

# 11. Criterio de avance

Servicio 2 puede avanzar si:

```text
[ ] S1 sigue cerrado y limpio.
[ ] S2 tiene frontera propia.
[ ] El primer frente tiene inputs/outputs claros.
[ ] El primer frente no promete conciliación definitiva.
[ ] El primer código futuro será testeable y reversible.
[ ] Automation V2 queda fuera.
```

---

# 12. Decisión

```text
S2_ADMIN_OPERATIONS_V1: OPENED_AS_SEPARATE_SERVICE
S1_FULL_ASSISTED_V1: PROTECTED_BASELINE
AUTOMATION_V2: DEFERRED_TRANSVERSAL_LAYER
NEXT_FRONT: S2_RECONCILIATION_ASSISTED_REVIEW_DELIVERY_PACKET_V1
```

---

# 13. Cierre

Servicio 2 queda abierto como servicio separado para administración profunda asistida.

El siguiente paso permitido no es código todavía. Es el contrato mínimo de frontera para conciliación asistida.
