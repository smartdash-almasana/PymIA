# SERVICE_2_RECONCILIATION_BOUNDARY_CONTRACT_V1

## Estado

```text
DOCUMENT_TYPE: BOUNDARY_CONTRACT
SERVICE: S2_ADMIN_OPERATIONS_V1
FRONT: conciliacion_asistida_banco_caja
STATUS: CONTRACT_OPENED
RUNTIME_MODIFIED: NO
TESTS_RUN: NO
CODE_CREATED: NO
S1_MODIFIED: NO
AUTOMATION_V2: OUT_OF_SCOPE
```

---

# 1. Objetivo

Definir la frontera mínima para el primer frente técnico de Servicio 2: conciliación asistida entre movimientos bancarios y movimientos internos declarados por la PyME.

Este contrato no implementa conciliación definitiva.
No crea runtime.
No conecta APIs.
No usa agente LLM.
No modifica Servicio 1.

---

# 2. Nombre operativo

```text
Conciliación asistida banco/caja/planilla interna
```

Traducción:

```text
Cruzar movimientos bancarios contra registros internos para producir candidatos de match, pendientes, diferencias y faltantes de evidencia, siempre bajo revisión humana.
```

---

# 3. Problema que resuelve

Este frente atiende casos donde la PyME o el contador dicen:

```text
- el banco no coincide con la caja;
- hay cobros sin identificar;
- hay pagos sin imputar;
- hay movimientos duplicados;
- faltan comprobantes;
- hay diferencias de fecha;
- hay diferencias de importe;
- la planilla interna no cierra con el extracto;
- no sabemos qué movimientos revisar primero.
```

---

# 4. Inputs permitidos

## 4.1 Banco

```text
movimientos_banco:
- fecha
- descripcion
- importe
- tipo opcional: credito/debito/ingreso/egreso
- referencia opcional
- saldo opcional
- fuente_archivo opcional
- fila_fuente opcional
```

## 4.2 Interno

```text
movimientos_internos:
- fecha
- descripcion
- importe
- tipo opcional: cobro/pago/ingreso/egreso
- contraparte opcional
- comprobante opcional
- referencia opcional
- fuente_archivo opcional
- fila_fuente opcional
```

---

# 5. Inputs no requeridos en V1

No se requieren para el primer slice:

```text
- API bancaria;
- API Mercado Pago;
- OCR/PDF;
- plan de cuentas;
- asientos contables;
- liquidación fiscal;
- credenciales bancarias;
- scraping;
- acceso a homebanking.
```

---

# 6. Outputs esperados

El contrato debe producir, como mínimo:

```text
matches_exactos:
- banco_id
- interno_id
- criterio
- confianza

matches_probables:
- banco_id
- interno_id
- criterio
- diferencias
- confianza

banco_sin_imputar:
- movimiento bancario sin candidato interno suficiente

interno_sin_banco:
- movimiento interno sin candidato bancario suficiente

diferencias_importe:
- pares con fecha/descripción compatible pero importe diferente

diferencias_fecha:
- pares con importe compatible pero fecha desplazada

faltantes_evidencia:
- comprobante faltante
- referencia faltante
- fecha ambigua
- importe inválido

requires_human_review:
- true
```

---

# 7. Estados permitidos

```text
READY_FOR_HUMAN_REVIEW
NEEDS_MORE_EVIDENCE
BLOCKED_BY_INVALID_INPUTS
NO_CANDIDATES_FOUND
PARTIAL_MATCHES_FOUND
```

No usar:

```text
CONCILIATED
CERTIFIED
AUDITED
ACCOUNTING_CLOSED
TAX_READY
```

---

# 8. Criterios de match permitidos

## 8.1 Match exacto

```text
- mismo importe;
- misma fecha o fecha normalizada equivalente;
- descripción/referencia compatible si existe.
```

## 8.2 Match probable

```text
- mismo importe con fecha cercana;
- fecha igual con descripción compatible e importe levemente diferente;
- referencia parcial compatible;
- contraparte compatible;
- comprobante compatible.
```

## 8.3 Pendiente

```text
- movimiento bancario sin candidato interno;
- movimiento interno sin candidato bancario;
- registro con datos insuficientes;
- importe inválido;
- fecha inválida;
- descripción demasiado ambigua.
```

---

# 9. Umbrales iniciales sugeridos

Estos umbrales son sugeridos para el futuro micro-slice, no implementación actual.

```text
fecha_cercana_dias: 3
importe_tolerancia_absoluta: 0.01
importe_tolerancia_relativa: 0.0
confianza_exacta: 1.0
confianza_probable_minima: 0.6
```

Regla:

```text
Los umbrales deben ser parámetros explícitos, no constantes ocultas.
```

---

# 10. Claims prohibidos

No afirmar:

```text
- conciliación definitiva;
- banco conciliado;
- saldo real confirmado;
- cierre contable;
- auditoría;
- certificación;
- cumplimiento fiscal;
- asientos correctos;
- fraude detectado;
- reemplazo del contador;
- automatización completa;
- resultado final sin revisión humana.
```

---

# 11. Lenguaje permitido

Se permite decir:

```text
- conciliación asistida;
- candidatos de conciliación;
- matches exactos/probables;
- movimientos pendientes;
- diferencias visibles;
- faltantes de evidencia;
- revisión humana requerida;
- paquete operativo para contador o responsable administrativo;
- control preliminar de banco/caja.
```

---

# 12. Reglas de seguridad

```text
- requires_human_review siempre debe ser true.
- Ningún output puede declarar cierre definitivo.
- Todo match probable debe conservar diferencias y criterio.
- Todo input inválido debe bloquear o quedar como faltante, no corregirse silenciosamente.
- No se deben inventar comprobantes ni contrapartes.
- No se deben fusionar movimientos sin evidencia explícita.
- No se deben ocultar duplicados.
```

---

# 13. Primer micro-slice técnico habilitado

Después de este contrato, queda habilitado abrir:

```text
S2_MICROSLICE_001_RECONCILIATION_MATCH_CANDIDATES
```

Archivos probables:

```text
PymIA-Live/pymia/smartpyme/service_2_reconciliation_match_candidates_v1.py
PymIA-Live/tests/smartpyme/test_service_2_reconciliation_match_candidates_v1.py
```

Función esperada:

```text
build_reconciliation_match_candidates_v1(
    bank_movements,
    internal_movements,
    options=None,
) -> ReconciliationMatchCandidatesV1
```

---

# 14. Tests mínimos esperados para el micro-slice

```text
1. match exacto por fecha e importe.
2. match probable por fecha cercana e importe igual.
3. diferencia de importe con fecha compatible.
4. diferencia de fecha con importe compatible.
5. banco sin imputar.
6. interno sin banco.
7. input inválido bloquea.
8. duplicados no se ocultan.
9. requires_human_review siempre true.
10. output determinístico.
11. no claims de conciliación definitiva.
12. umbrales explícitos.
```

---

# 15. Fuera de alcance del primer micro-slice

```text
- APIs bancarias;
- Mercado Pago;
- tarjetas;
- OCR/PDF;
- asientos contables;
- plan de cuentas;
- liquidación fiscal;
- UI;
- agente LLM;
- Stage 6;
- automatización total;
- conciliación definitiva.
```

---

# 16. Relación con S1

Servicio 1 queda protegido.

```text
S1 no se modifica.
S1 no absorbe conciliación profunda.
S1 no cambia claims.
S1 no cambia runtime por este contrato.
```

---

# 17. Decisión

```text
SERVICE_2_RECONCILIATION_BOUNDARY_CONTRACT_V1: OPENED
NEXT_ALLOWED_FRONT: S2_MICROSLICE_001_RECONCILIATION_MATCH_CANDIDATES
CODE_ALLOWED_AFTER_THIS_CONTRACT: YES_WITH_TESTS
RUNTIME_AUTHORIZATION: ONLY_FOR_NEW_S2_MODULE
S1_RUNTIME_AUTHORIZATION: NO
```

---

# 18. Cierre

La conciliación asistida de Servicio 2 queda definida como generación de candidatos, pendientes, diferencias y faltantes para revisión humana.

No queda definida como conciliación definitiva, auditoría ni cierre contable.
