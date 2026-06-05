# M31 — Servicio asistido repetible Protocol

## Estado

PROTOCOL_DRAFT

## Tesis de M31

M27–M30 prueban capacidades internas.

M31 debe probar repetibilidad operativa asistida.

Este protocolo no declara producto final. No declara autonomía end-to-end. No declara servicio comercial validado.

Define cómo ejecutar 3 a 5 casos piloto sin improvisar, midiendo tiempo, bloqueos, calidad de entrada, calidad de salida y aprendizaje para PymIA.

---

## Capacidades internas certificadas que habilitan este protocolo

### M27 — Caso inicial estructurado

Certificado por evidencia reportada:

```text
mensaje del dueño + Excel controlado
→ IntakeRecord
→ evidence gate
→ READY_FOR_ANALYSIS
```

Límite: no prueba cualquier Excel arbitrario ni diagnóstico integral.

### M28 — Hallazgo explicable

Certificado por evidencia reportada:

```text
ActionableFinding[]
→ EvidenceItem[]
→ NarrativeReport grounded
→ markdown legible / auditable
```

Límite: no prueba narrativa comercial óptima ni flujo end-to-end real.

### M29 — Reporte mínimo entregable

Certificado por evidencia reportada:

```text
owner_message + tenant_id + case_id + evidence_refs + ActionableFinding[]
→ Markdown mínimo entregable
```

Límite: no prueba PDF profesional, UI ni cliente real.

### M30 — Continuidad del caso

Certificado por evidencia reportada:

```text
caso asistido tenant_a
→ persistencia de contexto útil
→ tenant_b independiente
→ tenant_a vuelve
→ recuperación y evolución del caso
→ aislamiento entre tenants
```

Límite: no prueba automatización end-to-end ni flujo con dispatcher.

---

## Objetivo operativo

Ejecutar primeros casos piloto con un protocolo repetible:

```text
cliente trae problema + archivo
→ se decide si entra o se bloquea
→ se analiza evidencia controlada
→ se generan hallazgos
→ se produce reporte mínimo
→ se registra continuidad
→ se mide tiempo/costo/bloqueos/aprendizaje
```

---

## Regla de lenguaje

Usar:

```text
servicio asistido
piloto operativo
reporte mínimo
análisis sobre evidencia recibida
hallazgos preliminares
límites del análisis
```

No usar:

```text
producto final
plataforma autónoma
diagnóstico integral de empresa
ERP inteligente
IA que administra tu empresa
resultado garantizado
```

---

## Criterio de entrada del caso piloto

Un caso puede entrar sólo si cumple todos estos puntos:

1. Existe un dueño/responsable que declara un problema operativo concreto.
2. El problema se puede asociar a una categoría tratable inicial:
   - margen/costos/ventas;
   - proveedores duplicados;
   - datos faltantes en Excel;
   - evidencia insuficiente pero pedible.
3. Hay al menos un archivo o evidencia estructurable.
4. El cliente acepta que el resultado es un reporte mínimo asistido, no diagnóstico integral.
5. El equipo puede registrar tiempo real de trabajo y bloqueos.

---

## Criterio de bloqueo

Bloquear el caso si ocurre cualquiera de estos puntos:

1. No hay archivo ni evidencia mínima.
2. El problema declarado no puede traducirse a una categoría operativa inicial.
3. El archivo no tiene campos suficientes para análisis básico.
4. El cliente espera auditoría contable, fiscal, legal o financiera integral.
5. El cliente pide implementación de sistema/ERP como condición inicial.
6. El caso requiere PDF profesional, UI, automatización o integración externa para ser entregado.
7. El equipo no puede medir tiempo/costo de entrega.

Salida de bloqueo esperada:

```text
No hay evidencia suficiente para generar un reporte operativo mínimo.
Para avanzar hace falta: <evidencia solicitada>.
```

---

## Checklist de ejecución

### 1. Intake

Registrar:

- `pilot_id`
- `tenant_id`
- `case_id`
- fecha
- rubro declarado
- problema declarado textual
- archivo(s) recibido(s)
- categoría inicial estimada
- responsable humano del caso

### 2. Evidencia

Registrar:

- nombre de archivo
- tipo de archivo
- columnas/campos detectados
- campos requeridos presentes
- campos requeridos faltantes
- decisión: `READY_FOR_ANALYSIS` o `NEEDS_EVIDENCE`

### 3. Análisis

Registrar:

- capacidad usada si aplica;
- hallazgos detectados;
- severidad;
- evidencia asociada;
- recomendaciones básicas;
- errores o ambigüedades.

### 4. Reporte

Debe incluir como mínimo:

- problema declarado;
- evidencia usada;
- hallazgos principales;
- acciones sugeridas;
- límites del análisis;
- si corresponde, evidencia faltante.

### 5. Continuidad

Registrar:

- reporte entregado o referencia;
- próximo paso sugerido;
- estado del caso;
- si el cliente vuelve, qué contexto se reutilizó;
- qué no se repreguntó porque ya estaba registrado.

### 6. Medición

Registrar tiempos:

- minutos de intake;
- minutos de preparación de evidencia;
- minutos de análisis;
- minutos de redacción/revisión de reporte;
- minutos de entrega;
- tiempo total.

Registrar costos:

- costo herramientas;
- costo humano estimado;
- costo externo si existiera;
- observaciones.

### 7. Aprendizaje PymIA

Registrar:

- nuevo patrón observado;
- bloqueo repetido;
- columna o formato frecuente;
- pregunta de intake que debería mejorar;
- hallazgo frecuente;
- recomendación que debería volverse plantilla;
- riesgo de promesa excesiva.

---

## Plantilla de registro de piloto

```text
pilot_id:
tenant_id:
case_id:
fecha:
rubro:
problema_declarado:
archivos_recibidos:
categoria_inicial:
estado_evidencia:
evidencia_faltante:
hallazgos:
reporte_ref:
proximo_paso:
estado_final:
min_intake:
min_preparacion_evidencia:
min_analisis:
min_reporte:
min_entrega:
min_total:
bloqueos:
aprendizajes:
observaciones:
```

---

## Criterio de repetibilidad

El servicio asistido se considera repetible sólo si, tras 3 a 5 casos piloto:

1. El protocolo pudo ejecutarse sin reinventar el proceso.
2. Los casos pudieron clasificarse o bloquearse de forma honesta.
3. El reporte mínimo fue entregable sin prometer diagnóstico integral.
4. El tiempo total por caso fue medido.
5. Los bloqueos fueron registrados.
6. Los aprendizajes fueron convertibles en mejoras de PymIA.
7. No fue necesario abrir UI, PDF profesional, ERP, dispatcher, registry ni LLM externo para completar el piloto.

---

## Criterio de no repetibilidad

El servicio asistido no es repetible todavía si:

1. Cada caso exige una solución completamente distinta.
2. Los archivos son imposibles de normalizar sin intervención excesiva.
3. El reporte depende de redacción artesanal no sistematizable.
4. No se puede medir tiempo real.
5. El cliente exige algo fuera del alcance mínimo.
6. El análisis no produce hallazgos útiles o bloqueos claros.
7. Se requiere infraestructura nueva para cada caso.

---

## Métrica mínima de decisión

Después de 3 a 5 pilotos, completar:

```text
casos_totales:
casos_entregados:
casos_bloqueados:
tiempo_promedio_total:
tiempo_promedio_analisis:
tiempo_promedio_reporte:
bloqueo_mas_frecuente:
hallazgo_mas_frecuente:
aprendizaje_mas_importante:
se_puede_repetir_sin_improvisar: SI/NO
```

---

## Veredicto esperado al cerrar M31

M31 puede cerrarse como PASS sólo si existe evidencia documental de ejecución o simulación controlada del protocolo.

M31 no puede cerrarse sólo por tener este documento.

Para cerrar M31 hacen falta:

- protocolo versionado;
- plantilla de registro;
- al menos una validación documental o test documental del protocolo;
- decisión explícita de pasar a pilotos reales o bloquear.

---

## Próximo paso

Crear una validación mínima del protocolo:

```text
test documental o checklist verificado
→ confirma que el protocolo contiene entrada, bloqueo, entrega, continuidad, medición y aprendizaje
```

No abrir producto.
No abrir UI.
No abrir ERP.
