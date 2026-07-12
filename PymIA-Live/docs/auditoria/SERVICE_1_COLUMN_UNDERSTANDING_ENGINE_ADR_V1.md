# SERVICE_1_COLUMN_UNDERSTANDING_ENGINE_ADR_V1

**Decision arquitectonica para el motor de comprension de columnas de Servicio 1.**

- Repo: `PymIA` / subproyecto `PymIA-Live`
- Base: `561c295` — `feat(pymia-live): add service 1 column understanding engine contract`
- Alcance: documentar la decision; no tocar codigo; no integrar aun al flujo web/orquestador

---

## VERDICT

**ACCEPTED — el motor de comprension de columnas pasa a ser la fuente futura de preguntas humanas.**

Servicio 1 ya tiene un flujo asistido cerrado y un endpoint experimental funcional, pero la interfaz humana habia quedado en una capa demasiado pobre: preguntas genericas, copy tecnico y dependencia excesiva de nombres de columnas. El nuevo motor introduce una frontera necesaria: antes de preguntarle al dueno, PymIA debe construir una hipotesis auditable por columna.

---

## PROBLEMA

La interfaz anterior podia ser dinamica tecnicamente, pero no suficientemente inteligente desde el punto de vista humano/sistema operativo.

Ejemplos de problema:

- Preguntar por columnas sin explicar que entendio PymIA.
- Exponer lenguaje interno como `rol semantico`.
- Tratar columnas ambiguas como si bastara con confirmar un label.
- No usar de forma fuerte muestras, tipo inferido, co-columnas, contexto de hoja y riesgos.

Esto rompe la experiencia esperada: PymIA no debe pedirle al dueno que entienda la arquitectura interna. Debe consultar con precision operacional: "veo esto, por estas razones, puede significar A/B/C; cual es?".

---

## DECISION

A partir de este ADR, toda pregunta owner-facing futura sobre columnas debe derivar de un `Service1ColumnUnderstandingV1` o de un paquete equivalente producido por el motor de comprension de columnas.

No se deben crear nuevas preguntas humanas desde strings sueltos, copy hardcodeado de frontend, ni desde el mapper semantico viejo sin pasar por una capa de entendimiento.

Modulo base:

- `pymia/smartpyme/service_1_column_understanding_engine_contract_v1.py`
- `pymia/smartpyme/service_1_column_understanding_engine_v1.py`
- `tests/smartpyme/test_service_1_column_understanding_engine_contract_v1.py`

---

## QUE HACE EL ENGINE

Para cada columna genera un objeto auditable con:

- `column_name`
- `sheet_name`
- `sample_values`
- `inferred_data_type`
- `normalized_header`
- `candidate_meanings[]`
- `primary_hypothesis`
- `confidence`
- `evidence[]`
- `alternatives[]`
- `risk_if_wrong`
- `owner_question_needed`
- `owner_question_text`
- `allowed_owner_answers[]`
- `metadata{}`

La puntuacion actual combina:

- Header: `0.5`
- Tipo inferido: `0.35`
- Contexto/co-columnas: `0.15`
- Penalizaciones por contradicciones de tipo o contexto

La pregunta humana queda estructurada como consulta operacional, por ejemplo:

```text
En la hoja "Ventas" veo la columna "precio_unitario" con valores como 1200, 1450 y 980.
Por el nombre y los datos, podria ser:
(A) Precio de venta unitario
(B) Costo unitario
(C) Venta total
(D) Otra cosa
Cual es?
```

---

## QUE NO HACE

Este engine **no** forma parte todavia del flujo productivo cerrado.

No hace:

- No LLM.
- No runtime.
- No delivery.
- No escritura de archivos.
- No llamadas externas.
- No ejecucion de tools.
- No reemplazo automatico del orquestador.
- No modifica los 13 eslabones cerrados.
- No decide producto final.
- No diagnostica patologias por si mismo.

Es un modulo puro, invocable, auditable y aislado.

---

## INVARIANTES

El motor debe conservar estas reglas:

- Fail-closed por defecto.
- Inputs no mutados.
- Sin I/O.
- Sin permisos de runtime.
- Sin delivery.
- Sin autorizacion implicita.
- Sin imports desde los 13 eslabones cerrados hacia el nuevo engine.
- Preguntas humanas sin jerga interna como "rol semantico".
- Toda pregunta debe incluir evidencia, alternativas y riesgo operacional.

---

## RELACION CON EL FLUJO CERRADO

El flujo asistido de Servicio 1 sigue cerrado y no se reabre por este ADR.

Estado actual:

- 13 piezas cerradas: boundary -> delivery + orquestador.
- Endpoint web experimental funcional.
- Dynamic owner question loop existente.
- Nuevo engine standalone en `561c295`.

Relacion correcta:

```text
XLSX -> estructura/columnas -> Column Understanding Engine -> preguntas humanas mejores
```

Integracion futura, todavia pendiente:

```text
web dynamic loop -> understanding packet -> owner-facing question view -> owner answer -> flujo cerrado
```

---

## RIESGO QUE CONTROLA

Este ADR evita tres derivas:

1. **Deriva de interfaz**: mejorar solo textos sin mejorar la comprension real.
2. **Deriva semantica**: usar nombres de columna como unica verdad.
3. **Deriva de pipeline**: conectar el engine al flujo cerrado antes de probarlo con suficientes Excels.

---

## SIGUIENTES PASOS

No integrar todavia al frontend ni al orquestador.

Orden recomendado:

1. **Corpus de Excels variados**
   - Ventas simples.
   - Ventas con descuentos/impuestos.
   - Stock.
   - Caja/cobros.
   - Compras/costos.
   - Columnas raras o ambiguas.

2. **Evaluacion de precision**
   - Comparar hipotesis contra respuesta esperada.
   - Medir falsos positivos peligrosos.
   - Medir preguntas innecesarias.
   - Medir preguntas utiles para desconocidos.

3. **Owner-facing question adapter**
   - Convertir `Service1ColumnUnderstandingV1` en vista humana estable.
   - No inventar copy en frontend.

4. **Wiring al dynamic web loop**
   - Reemplazar preguntas actuales por preguntas derivadas del understanding packet.
   - Mantener bloqueo si el dueno no responde.

5. **Re-auditoria end-to-end**
   - CASE_001 + corpus dificil.
   - Verificar que el flujo cerrado no se rompio.

---

## DECISION FINAL

El `SERVICE_1_COLUMN_UNDERSTANDING_ENGINE_CONTRACT_V1` queda aceptado como frontera arquitectonica para madurar la interfaz humana de Servicio 1.

La maduracion de la interfaz no debe avanzar por copy ni por hardcode. Debe avanzar por comprension de columnas, evidencia, alternativas y preguntas operacionales al dueno.
