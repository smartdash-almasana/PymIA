# PYMIA CASE — Cafetería ABC assisted operation

Estado: `OPERATIVO_ASISTIDO_LOCAL`

Caso basado en la demo local validada del `Faithful Operator` con Excel real de cafetería.

## Entrada del dueño

```text
Vendo más pero no me queda plata.
```

## Evidencia usada

```text
prueba_excels/Cafetería ABC.xlsx
```

## Recorrido del operador

```text
1. EVIDENCE_REQUESTED
2. OWNER_CONFIRMATION_PENDING
3. CLOSED
```

Interpretación operativa:

- El operador no diagnostica al recibir el relato inicial.
- Pide evidencia mínima.
- Registra y procesa el Excel.
- Devuelve un candidato trazable.
- Cierra sólo luego de confirmación del dueño.

## Trazabilidad validada

```text
tenant_id: demo_cafeteria_abc
intake_id: intake_93546f538f5da1a7
evidence_id: evidence_fb309447997d4ef684c23bd417f645bf
run_id: run_c1c805258c8f4262bc309376f81cd662
output_hash: bea6fc31cb1fbf33cb2be7ea3771ba9c39dbedf8f346c73011786e7762f012ba
```

## Salida para operador asistido

```text
Resultado de trabajo posterior a confirmación
Caso: Vendo más pero no me queda plata.
Evidencia usada: evidence_fb309447997d4ef684c23bd417f645bf
Run ID: run_c1c805258c8f4262bc309376f81cd662
Output hash: bea6fc31cb1fbf33cb2be7ea3771ba9c39dbedf8f346c73011786e7762f012ba
Límite: Resultado candidato: no declara verdad final sin confirmación del dueño.
Próximos pasos operativos:
1. Revisar con el dueño si las ventas y costos cargados cubren el período completo.
2. Separar productos o líneas con margen dudoso para lectura focalizada.
3. Pedir al dueño una decisión operativa concreta sobre qué variable quiere ajustar primero.
Pregunta de seguimiento: ¿Querés que revisemos primero margen por producto, caja por período o costos directos?
```

## Conversación operativa recomendada

### Pregunta 1 — período

```text
¿El Excel de Cafetería ABC cubre el período completo que querés revisar?
```

Objetivo: evitar lectura parcial de ventas, costos o caja.

### Pregunta 2 — columnas

```text
¿Las columnas del archivo representan ventas reales, costos directos, productos y período correcto?
```

Objetivo: confirmar semántica de negocio antes de sostener conclusiones operativas.

### Pregunta 3 — foco

```text
¿Querés revisar primero margen por producto, caja por período o costos directos?
```

Objetivo: convertir la lectura candidata en una decisión de trabajo concreta.

## Decisiones posibles

### Si el dueño confirma

Acción:

- conservar trazabilidad;
- avanzar sobre el foco elegido;
- preparar revisión operativa focalizada.

### Si el dueño corrige

Acción:

- no cerrar;
- pedir corrección semántica concreta;
- reprocesar con evidencia corregida.

### Si el dueño no sabe

Acción:

- bloquear honestamente;
- pedir ayuda para identificar columnas, período o fuente de datos;
- no afirmar causa.

### Si aporta otro Excel

Acción:

- registrar nueva evidencia;
- reprocesar;
- conservar el vínculo con el `intake_id` original.

## Límites

Este caso no declara diagnóstico final automático.

No afirma causa definitiva.

No promete mejora garantizada.

No transforma la demo en producto, canal, runtime ni automatización externa.

## Resultado operativo

Cafetería ABC queda como primer caso asistido local versionable:

```text
relato del dueño + Excel real → salida trazable → conversación operativa controlada
```
