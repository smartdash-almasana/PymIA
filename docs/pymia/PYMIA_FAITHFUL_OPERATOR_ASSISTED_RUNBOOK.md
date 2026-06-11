# PYMIA FAITHFUL OPERATOR — Assisted Runbook

Estado: `OPERATIVO_LOCAL`

Este runbook define cómo usar el `Faithful Operator` en modo asistido local con una PyME real, sin abrir producto, canal, runtime ni automatización externa.

## Propósito

Permitir que un operador humano use PymIA para convertir:

```text
relato inicial del dueño + Excel real → salida trazable para conversación operativa
```

El objetivo no es diagnosticar automáticamente, sino producir una lectura candidata con trazabilidad y límites explícitos.

## Precondiciones

Antes de ejecutar la demo asistida, el operador debe contar con:

1. Una frase inicial del dueño PyME.
2. Un Excel real aportado por el dueño.
3. Confirmación verbal o escrita de que el Excel corresponde al caso tratado.
4. Contexto mínimo del período de análisis.

## Comando base

Desde la raíz del repositorio:

```bash
python scripts/demo_faithful_operator_local.py \
  --message "Vendo más pero no me queda plata." \
  --excel "prueba_excels/Cafetería ABC.xlsx" \
  --confirmation "Sí, correcto, esas columnas representan mis ventas, costos, productos y período." \
  --write-report
```

Salida esperada:

```text
PYMIA FAITHFUL OPERATOR — DEMO LOCAL ASISTIDA
...
REPORTE_LOCAL_ESCRITO
.tmp/faithful_operator_demo_report.md
```

## Qué debe mirar el operador

### 1. Recorrido

Debe observarse un recorrido como:

```text
1. EVIDENCE_REQUESTED
2. OWNER_CONFIRMATION_PENDING
3. CLOSED
```

Si el recorrido termina en `BLOCKED`, el operador no debe forzar una conclusión.

### 2. Trazabilidad

La salida debe incluir:

```text
tenant_id
intake_id
evidence_id
run_id
output_hash
```

Sin estos identificadores, la lectura no debe tratarse como resultado trazable.

### 3. Límite

La salida debe mantener explícitamente el límite:

```text
no declara verdad final sin confirmación del dueño
```

Si una salida afirma causa definitiva, automatización o certeza final, debe considerarse inválida.

## Conversación sugerida con el dueño

Después de generar la salida, el operador debe validar:

1. “¿Este Excel cubre el período que querés revisar?”
2. “¿Estas columnas representan ventas reales, costos directos y productos reales?”
3. “¿Hay gastos, retiros, deudas o pagos que no estén en este archivo?”
4. “¿Querés revisar primero margen por producto, caja por período o costos directos?”

## Decisiones permitidas

El operador puede:

- registrar confirmación del dueño;
- pedir nueva evidencia;
- pedir corrección semántica;
- separar líneas de producto;
- pedir un Excel corregido;
- preparar una conversación operativa posterior.

## Decisiones prohibidas

El operador no debe:

- declarar diagnóstico final automático;
- afirmar causa definitiva;
- prometer mejora garantizada;
- venderlo como producto terminado;
- abrir Telegram, DB, runtime o canal externo;
- usar LLM libre para reescribir el resultado como certeza;
- ocultar límites de evidencia.

## Manejo de casos

### Caso A — Dueño confirma

Estado esperado:

```text
CLOSED + candidate_confirmed
```

Acción:

- entregar próximos pasos operativos;
- registrar trazabilidad;
- preguntar qué variable revisar primero.

### Caso B — Dueño corrige

Estado esperado:

```text
EVIDENCE_REQUESTED + correction_requested
```

Acción:

- no cerrar;
- pedir corrección concreta;
- reprocesar con evidencia corregida.

### Caso C — Dueño no sabe

Estado esperado:

```text
BLOCKED + blocked_by_owner_uncertainty
```

Acción:

- no cerrar;
- pedir ayuda para identificar columnas, período o fuente de datos.

### Caso D — Dueño aporta nuevo Excel

Estado esperado:

```text
EVIDENCE_REQUESTED + new_evidence_provided
```

Acción:

- registrar nueva evidencia;
- reprocesar;
- conservar trazabilidad anterior.

## Artefactos relacionados

- `pymia/faithful_operator.py`
- `scripts/demo_faithful_operator_local.py`
- `docs/pymia/PYMIA_FAITHFUL_OPERATOR_LOCAL_DEMO_CHECKPOINT.md`
- `docs/pymia/PYMIA_FAITHFUL_OPERATOR_ASSISTED_PACKET_EXAMPLE.md`

## Estado operativo

Este runbook habilita operación asistida local controlada. No habilita despliegue, producto ni canal externo.
