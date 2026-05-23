# Ontología de Agentes del Sistema PymIA / SmartPyme
**Estado:** VIGENTE
**Tipo:** Especificación ontológica-arquitectónica fundacional
**Dueño conceptual:** Arquitectura Maestra / Kernel PymIA / Hermes Orchestrator
**Relación con código:** transversal — rige responsabilidades de `pymia/`, `conversa-engine/`, `hermes/` y boundary conversacional
**Reemplaza a:** ninguna ontología previa formal (consolida principios dispersos en `arquitectura-maestra.md`, `GLOSARIO_SEMANTICO_PYMIA.md` y `HERMES_CONTRATO_SEMANTICO.md`)

> [!IMPORTANT]
> Este documento define **quiénes son los agentes del sistema**, qué rol cumple cada uno y cuál es el flujo dinámico correcto entre ellos. Es el contrato ontológico rector: cualquier implementación, diseño conversacional, decisión de runtime o decisión de producto debe respetar esta estructura. Ningún agente puede asumir responsabilidades que ontológicamente pertenecen a otro.

---

## 1. Estructura completa del sistema

```text
Dueño          = agente creacional
Hermes         = organismo operativo / conversacional
PymIA          = inteligencia computacional de Hermes
PyME / negocio = universo observado conocido/desconocido
```

---

## 2. Definición de cada agente

### 2.1 Dueño — agente creacional

El dueño no es solo “usuario”. Es quien:

- Da origen al sistema de sentido.
- Define la intención.
- Autoriza el camino.
- Corrige el rumbo.
- Valida si el resultado sirve.
- Decide qué se interviene y qué no.

**Sin dueño no hay dirección.**

El dueño es el único agente con legitimidad para:

- Declarar un síntoma.
- Aceptar o rechazar un pedido de evidencia.
- Aprobar un hallazgo.
- Autorizar una intervención.

### 2.2 PyME / negocio — universo observado

La PyME es el **mundo**. No es un objeto simple. Es un universo parcialmente conocido y parcialmente desconocido. Tiene:

- Zonas visibles y zonas opacas.
- Rutinas, síntomas, documentos, personas, flujos, errores.
- Costos, decisiones informales, memoria tácita, procesos no explicitados.

La PyME **no entra completa al sistema. Se revela progresivamente** a través de:

```text
negocio real
→ señales
→ contexto
→ evidencia
→ estructura
→ hallazgos
```

### 2.3 Hermes — organismo operativo / conversacional

Hermes es quien se mueve dentro del universo PyME. Hermes:

- Dialoga con el dueño.
- Recibe señales del negocio.
- Ordena la interacción.
- Elige qué capacidad activar.
- Mantiene continuidad.
- Coordina pasos.
- Presenta resultados.
- Pide autorización.

Hermes opera **entre** `dueño ↔ negocio ↔ PymIA`.

**Hermes no calcula por cuenta propia**, pero sí sabe **cuándo y cómo pedir computabilidad** a PymIA.

### 2.4 PymIA — inteligencia computacional de Hermes

PymIA es la inteligencia interna que le da a Hermes:

- Clasificación.
- Validación.
- Cálculo.
- Lectura estructurada.
- Evidencia contrastada.
- Hallazgos tipados.
- Límites y confianza.
- Outputs contractuales.

**PymIA no reemplaza al dueño.**
**PymIA no reemplaza a Hermes.**
**PymIA computa lo que Hermes necesita para operar correctamente.**

---

## 3. Flujo dinámico completo

```text
Dueño
  ↓ intención / pregunta / autorización

Hermes
  ↓ conversación / orquestación / solicitud de capacidad

PymIA
  ↓ computabilidad / validación / hallazgo / límite

Hermes
  ↓ traducción operativa / próximo paso / continuidad

PyME / negocio
  ↓ nueva evidencia / nuevos síntomas / nuevos datos

Dueño
  ↓ decisión / corrección / nueva creación
```

### Ciclo dinámico (no es una línea vertical)

```text
Dueño → Hermes → PymIA → Hermes → Dueño
              ↘
               PyME / evidencia / realidad operacional
```

---

## 4. Fórmula rectora

```text
El dueño es el agente creacional.
La PyME es el universo observado.
Hermes es el organismo operativo que explora y conversa.
PymIA es la inteligencia computacional que estabiliza, valida y calcula.
```

Versión breve:

```text
El dueño crea.
La PyME revela.
Hermes opera.
PymIA computa.
```

---

## 5. Regla soberana

```text
Hermes puede explorar el universo PyME.
Hermes puede conversar con el dueño.
Hermes puede sincronizar capacidades.
Hermes puede presentar resultados.

Pero Hermes NO puede inventar la computabilidad de PymIA.
```

Corolarios estrictos:

1. **Hermes no diagnostica.** Solo PymIA produce hallazgos con evidencia.
2. **Hermes no calcula.** Solo PymIA produce fórmulas, márgenes, ratios, contrastes.
3. **Hermes no decide por el dueño.** Solo traduce resultados y pide autorización.
4. **PymIA no conversa directamente con el dueño.** Siempre a través de Hermes.
5. **La PyME no se interpreta sin evidencia.** PymIA exige evidencia antes de hallazgo.
6. **El dueño nunca es forzado.** Puede rechazar, corregir, pausar o cancelar en cualquier momento.

---

## 6. Imagen ontológica del sistema

```text
            Dueño
   agente creacional / sentido
              ↓
           Hermes
 organismo operativo-conversacional
              ↓
            PymIA
 inteligencia computacional interna
              ↓
        PyME / negocio
 universo observado conocido/desconocido
```

---

## 7. Clave interpretativa

- **La PyME es el territorio.**
- **El dueño es quien le da sentido al recorrido.**
- **Hermes camina el territorio conversacionalmente.**
- **PymIA mide, valida y computa lo que aparece.**

---

## 8. Relación con otros documentos vigentes

| Documento | Relación |
|-----------|----------|
| `docs/arquitectura/arquitectura-maestra.md` | Este documento especializa los roles que la arquitectura maestra describe genéricamente. |
| `docs/arquitectura/GLOSARIO_SEMANTICO_PYMIA.md` | Los términos usados aquí (síntoma, evidencia, hallazgo, contexto, encuadre) se definen formalmente en el glosario. |
| `docs/arquitectura/CONTRATO_PRIMER_ENCUENTRO_TAXONOMICO.md` | El primer encuentro es la materialización conversacional de esta ontología: el dueño expresa, Hermes encuadra, PymIA estabiliza. |
| `docs/arquitectura/KERNEL_ANALITICA_TABULAR_SOBERANA.md` | El kernel es la materialización computacional de PymIA. |
| `docs/hermes/principio-obligatorio-hermes-runtime-orchestrator.md` | Refuerza la regla de que Hermes orquesta pero no calcula. |
| `docs/arquitectura/SEMANTICA_CONVERSACIONAL_PYMIA_HERMES_BEM.md` (SUPERADO) | Este documento reemplaza conceptualmente la antigua visión tripartita al redefinir los roles ontológicos. |

---

## 9. Antipatrones prohibidos por esta ontología

| Antipatrón | Por qué viola la ontología |
|------------|----------------------------|
| Hermes diagnosticando directamente | Viola §5 corolario 1 |
| PymIA respondiendo en lenguaje humano al dueño sin pasar por Hermes | Viola §5 corolario 4 |
| PymIA interpretando Excel sin contexto del dueño | Viola §5 corolario 5 |
| Asumir que el dueño sabe qué necesita antes del encuadre | Viola §2.1 (el dueño es creacional, no predictivo) |
| Pedir evidencia antes que identidad operacional | Viola §2.2 (la PyME se revela progresivamente) |
| Mezclar lógica de canal dentro de `pymia/` | Viola §2.4 (PymIA es computacional, no conversacional) |
| Agregar memoria caótica sin contrato | Viola §2.2 (el universo observado se revela, no se inventa) |

---

## 10. Criterio de uso

Cualquier ingeniero, agente de desarrollo o decisión de producto debe preguntarse antes de implementar:

1. ¿Este agente está haciendo lo que ontológicamente le corresponde?
2. ¿Estoy respetando el flujo Dueño → Hermes → PymIA → PyME?
3. ¿Estoy violando algún corolario de la regla soberana?

Si la respuesta a (1) o (3) indica violación, el diseño es incorrecto aunque técnicamente funcione.

---

## 11. Historial de versiones

| Versión | Fecha | Cambio |
|---------|-------|--------|
| v1.0 | 2026-05-24 | Creación inicial. Consolida principios dispersos en arquitectura maestra, glosario y contratos semánticos. |
