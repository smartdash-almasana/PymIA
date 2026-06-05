# M31P-001 — Solicitud mínima de datos para piloto

## Estado

DATA_REQUEST_PENDING

## Propósito

Definir exactamente qué información hace falta para convertir `M31P-001_INTAKE.md` en un registro de piloto completo.

Este archivo no es evidencia de piloto ejecutado.

No cuenta para PASS_OPERATIVO.

## Regla principal

No se completa `M31P-001.md` hasta contar con datos reales o realistas suficientes.

## Bloque mínimo A — Identificación del caso

Completar:

```yaml
pilot_id: M31P-001
tenant_ref:
case_date:
business_type:
case_origin:
```

Preguntas:

1. ¿Qué referencia anónima usamos para el caso o tenant?
2. ¿Qué fecha corresponde al caso?
3. ¿Qué tipo de PyME es?
4. ¿El caso viene de cliente real, demo realista, caso interno o prospecto?

## Bloque mínimo B — Problema declarado

Completar:

```yaml
owner_problem_statement:
```

Pregunta:

¿Qué dijo el dueño PyME que quiere resolver o entender?

Ejemplos válidos:

- No sé si gano plata.
- Vendo mucho pero no queda plata.
- No me cierra caja/banco.
- No entiendo este Excel.
- Creo que los costos están desactualizados.

## Bloque mínimo C — Sentido operativo

Completar:

```yaml
owner_operational_meaning:
```

Preguntas:

1. ¿Qué período quiere mirar el dueño?
2. ¿Qué significa cada archivo o columna relevante?
3. ¿Qué proceso real generó esos datos?
4. ¿Qué decisión necesita tomar?
5. ¿Qué dato falta pero existe en otro lado?

Si no hay sentido operativo suficiente, registrar la ausencia como bloqueo o evidencia faltante.

## Bloque mínimo D — Evidencia recibida

Completar:

```yaml
received_evidence:
  -
```

Preguntas:

1. ¿Qué archivos o datos están disponibles?
2. ¿Hay Excel de ventas, costos, stock, compras, banco o precios?
3. ¿Hay PDFs, extractos, facturas o reportes?
4. ¿La evidencia está en archivos reales o sólo declarada verbalmente?

## Bloque mínimo E — Evidencia faltante

Completar:

```yaml
missing_evidence:
  -
```

Preguntas:

1. ¿Qué evidencia falta para aplicar el protocolo M31?
2. ¿Faltan ventas, costos, período, columnas explicadas, facturas o extractos?
3. ¿La falta de evidencia bloquea el piloto o permite salida parcial?

## Bloque mínimo F — Ejecución y medición

Completar:

```yaml
execution_time_minutes:
operational_cost:
human_intervention:
operator_notes:
```

Preguntas:

1. ¿Quién ejecuta o asiste el piloto?
2. ¿Cómo se medirá el tiempo real?
3. ¿Corresponde costo operativo o `not_applicable`?
4. ¿Qué intervención humana se espera?
5. ¿Qué notas debe preservar el operador?

## Bloque mínimo G — Salida o bloqueo

Completar:

```yaml
output_delivered:
final_status:
blockers:
  -
repeatability_assessment:
limitations:
  -
```

Preguntas:

1. ¿Se espera entregar un informe mínimo, un hallazgo, una solicitud de evidencia o un bloqueo?
2. ¿El estado esperado es DELIVERED, BLOCKED, PARTIAL o UNSUPPORTED?
3. ¿Qué bloqueos existen?
4. ¿El caso parece repetible, parcialmente repetible, no repetible o todavía no hay evidencia suficiente?
5. ¿Cuáles son las limitaciones?

## Bloque mínimo H — Aprendizajes candidatos

Completar:

```yaml
candidate_learnings:
  -
```

Regla:

Puede ser lista vacía.

No convertir estos aprendizajes en LearningMemory automática.

## Salida esperada de esta solicitud

Cuando estos bloques estén completos, crear:

```text
docs/smartpyme/pilots/M31P-001.md
```

con el contrato canónico completo.

## Estado hasta completar datos

```yaml
pilot_id: M31P-001
intake_status: DATA_REQUEST_PENDING
counts_for_pass_operativo: false
reason: datos mínimos todavía no completos
```
