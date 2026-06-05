# Roadmap — Servicio asistido Excel + semántica PyME

## Estado

DRAFT_OPERATIVO

## Propósito

Este roadmap define un camino corto para convertir capacidades técnicas existentes de PymIA / SmartPyme en un servicio asistido repetible, sin llamarlo producto y sin prometer autonomía completa.

El objetivo no es construir un ERP, ni una plataforma final, ni una nueva arquitectura general.

El objetivo es avanzar desde:

```text
Excel controlado + semántica del dueño + hallazgos técnicos
```

hacia:

```text
servicio asistido capaz de recibir un caso PyME, analizar evidencia concreta,
entregar hallazgos entendibles y repetir el proceso con trazabilidad.
```

---

## Regla de lenguaje

No llamar producto a este roadmap.

Usar:

```text
servicio asistido
capacidad técnica aplicada
protocolo de entrega
laboratorio operativo asistido
```

No usar todavía:

```text
producto final
plataforma autónoma
ERP inteligente
sistema completo
IA que administra la empresa
```

---

## Punto de partida certificado

PymIA / SmartPyme tiene capacidades técnicas certificadas para:

- analizar Excel controlados de ventas / costos / margen;
- detectar proveedores duplicados en Excel controlado;
- generar hallazgos técnicos con entidad, métrica, diferencia, severidad, evidencia y recomendación;
- bloquear cuando falta evidencia suficiente;
- conservar trazabilidad técnica de la evidencia usada.

Límite actual:

- no diagnostica toda la empresa;
- no garantiza cualquier Excel arbitrario;
- no es producto cerrado;
- no tiene todavía reporte narrativo final consolidado para cliente PyME;
- no tiene aún servicio repetible validado con casos reales.

---

## Principio rector

```text
Primero servicio asistido repetible.
Después producto.
```

PymIA debe avanzar con casos reales, pero sin vender autonomía que todavía no existe.

---

# Hitos

## M27 — Excel + semántica del dueño

### Objetivo

Unir en un mismo caso operativo:

```text
mensaje del dueño
+
archivo Excel
+
clasificación inicial
+
evidencia requerida
```

### Pasa de

```text
Tengo un Excel por un lado y un dolor PyME por otro.
```

### A

```text
PymIA registra un caso con:
- qué dijo el dueño;
- qué archivo aportó;
- qué categoría operativa parece corresponder;
- qué evidencia alcanza;
- qué evidencia falta.
```

### Alcance permitido

- recepción del mensaje;
- identificación de dolor declarado;
- asociación con Excel controlado;
- clasificación inicial;
- evidence gate;
- salida estructurada del caso.

### Fuera de alcance

- nuevo microservicio;
- cambios en registry;
- cambios en dispatcher;
- integración ERP;
- Telegram / PDF / HTML / UI;
- LLM externo;
- autonomía comercial.

### Evidencia de cierre

Test o fixture donde:

```text
mensaje del dueño + Excel controlado
→ ReceptionRecord / IntakeRecord
→ clasificación
→ evidencia suficiente o faltante
→ estado del caso
```

---

## M28 — Hallazgo explicable

### Objetivo

Convertir hallazgos técnicos en explicaciones entendibles para dueño PyME.

### Pasa de

```text
LOW_MARGIN
PRODUCT_WITHOUT_COST
DUPLICATE_ROWS
SUPPLIER_DUPLICATE
```

### A

```text
Estos productos no permiten saber si ganás plata porque falta costo.
Estos registros duplicados pueden inflar ventas o compras.
Estos proveedores parecen repetidos y pueden generar errores administrativos.
```

### Alcance permitido

- adaptador puro `ActionableFinding → NarrativeClaim`;
- grounding obligatorio;
- markdown con y sin trace;
- lenguaje claro, no comercial exagerado;
- fail-closed si no hay hallazgos.

### Fuera de alcance

- narrativa generada por LLM;
- PDF;
- HTML;
- dashboard;
- cambios en capacidades certificadas;
- nuevas patologías de dominio sin evidencia.

### Evidencia de cierre

Tests que demuestren:

```text
ActionableFinding[]
→ reporte narrativo grounded
→ markdown legible
→ trace auditable opcional
```

---

## M29 — Reporte mínimo entregable

### Objetivo

Generar una salida única, corta, legible y auditable para un caso asistido.

### Pasa de

```text
outputs técnicos fragmentados
```

### A

```text
informe mínimo con:
- problema declarado;
- evidencia usada;
- hallazgos principales;
- severidad;
- recomendación básica;
- evidencia faltante;
- límites del análisis.
```

### Alcance permitido

- reporte Markdown;
- estructura estable;
- disclaimer operativo;
- trace opcional para auditoría;
- fixture reproducible.

### Fuera de alcance

- PDF profesional;
- landing;
- UI;
- automatización de envío;
- promesa de diagnóstico integral;
- diseño visual comercial.

### Evidencia de cierre

Fixture reproducible:

```text
mensaje dueño + Excel controlado
→ hallazgos
→ reporte Markdown mínimo
```

El reporte debe poder leerse por una persona no técnica.

---

## M30 — Continuidad del caso

### Objetivo

Recordar el caso del cliente sin reiniciar desde cero.

### Pasa de

```text
cada análisis es aislado
```

### A

```text
tenant/caso con historial mínimo:
- dolor inicial;
- archivos recibidos;
- hallazgos generados;
- evidencia faltante;
- próximo paso sugerido;
- estado del caso.
```

### Alcance permitido

- persistencia mínima por tenant;
- recuperación de contexto útil;
- aislamiento entre tenants;
- continuidad de evidencia y hallazgos.

### Fuera de alcance

- CRM completo;
- seguimiento comercial automatizado;
- Supermemory real obligatorio;
- multiagente;
- dashboard.

### Evidencia de cierre

Test:

```text
cliente A inicia caso
→ sube evidencia
→ recibe hallazgos
→ vuelve
→ PymIA recupera contexto útil
→ no mezcla con cliente B
```

---

## M31 — Servicio asistido repetible

### Objetivo

Convertir el flujo en un protocolo operativo repetible para primeros casos reales, todavía sin llamarlo producto.

### Pasa de

```text
podemos analizar un Excel controlado
```

### A

```text
podemos entregar varios casos similares con:
- mismo protocolo;
- mismo criterio de entrada;
- mismo criterio de bloqueo;
- mismo tipo de salida;
- medición de tiempo y costo por caso.
```

### Alcance permitido

- checklist de entrega;
- plantilla de intake;
- plantilla de reporte;
- medición de tiempo por caso;
- registro de bloqueos y aprendizajes;
- documentación de 3 a 5 casos piloto.

### Fuera de alcance

- producto autónomo;
- onboarding automático;
- facturación integrada;
- ERP;
- Odoo / Dolibarr como dependencia obligatoria;
- promesas comerciales no validadas.

### Evidencia de cierre

Cierre con:

```text
3 a 5 casos piloto documentados
+ tiempo real de entrega
+ bloqueos encontrados
+ aprendizajes
+ checklist estable
```

Sólo después de este hito puede evaluarse si existe base suficiente para hablar de producto mínimo.

---

# Secuencia resumida

```text
M27 — entender caso
M28 — explicar hallazgo
M29 — entregar reporte
M30 — recordar continuidad
M31 — repetir como servicio asistido
```

---

# Decisiones explícitas

## No ERP

Este roadmap no requiere Odoo, Dolibarr, ERPNext ni ningún ERP externo.

Los ERP pueden volver como hipótesis futura de sustrato operativo, pero no forman parte de este camino mínimo.

## No producto todavía

El cierre de M31 no declara producto automáticamente.

Sólo habilita una evaluación honesta:

```text
¿este servicio asistido es repetible, cobrable y suficientemente estable
como para convertirse en producto mínimo?
```

## No autonomía falsa

Todo el roadmap asume supervisión humana.

PymIA asiste, estructura, detecta y explica.

No se declara operación autónoma end-to-end.

---

# Criterio de aprobación del roadmap

Este roadmap sirve si:

- reduce deriva;
- acerca PymIA a casos reales;
- conserva evidencia;
- no sobrepromete;
- permite aprender de clientes;
- mide tiempo/costo por entrega;
- fortalece el núcleo PymIA.

Este roadmap falla si:

- genera documentación sin entregas;
- intenta vender producto antes de tiempo;
- introduce ERP prematuramente;
- mezcla UI, Telegram, PDF, CI, dispatcher y nuevas capacidades;
- convierte hipótesis comercial en verdad certificada.

---

# Próximo paso recomendado

Abrir M27 con scope estricto:

```text
mensaje del dueño + Excel controlado
→ caso operativo estructurado
→ clasificación
→ evidence gate
```

Sin tocar producto, ERP, UI, registry ni dispatcher.
