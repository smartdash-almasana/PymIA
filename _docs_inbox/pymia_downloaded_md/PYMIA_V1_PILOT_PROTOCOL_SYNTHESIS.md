# PymIA V1 — Protocolo de piloto real con 5 PyMEs

## Veredicto

Esta pieza baja PymIA a validación real.

El objetivo del piloto no es demostrar que PymIA “anda”.

El objetivo es evitar autoengaño:

```text
no vanity metrics
no score encubierto
no dashboard prematuro
no promesas de automatización
no casos fáciles para quedar bien
```

El piloto debe probar si la arquitectura epistémica sirve frente a PyMEs reales, operadores reales, evidencia imperfecta y dueños con relatos reales.

## Principio rector

```text
El piloto valida si PymIA produce criterio trazable útil.
No valida velocidad, satisfacción superficial ni cantidad de hallazgos.
```

## Tipo de PyMEs a elegir

Criterio:

```text
estrés al kernel, no casos fáciles
```

Selección recomendada:

```text
5 casos reales
mínimo 3 sectores distintos
ideal 4 sectores
mezcla de micro y pequeñas
mezcla de evidencia rica, pobre y mixta
mezcla de dueños disponibles y difíciles
mezcla de regímenes fiscales
problemas de liquidez, rentabilidad y casos mixtos
PyMEs tradicionales argentinas
```

Ejemplos útiles:

```text
panadería micro
metalúrgica pequeña
distribuidora pequeña
textil micro
servicios profesionales pequeño
```

## Casos que NO deben entrar todavía

```text
evidencia dramáticamente insuficiente
dueño que no participa
crisis terminal / concurso / cierre inminente
sectores sin pack VALIDATED
conflictos societarios/familiares abiertos
PyMEs demasiado simples
PyMEs demasiado grandes para V1
problemas legales abiertos
operación fuertemente dolarizada
casos ya diagnosticados por otro framework
```

## Pre-flight checklist antes de aceptar un caso

Todo debe pasar:

```text
SectorPack VALIDATED disponible
PathologyPack cubre patologías core
FormulaPack listo para la evidencia esperada
operador entrenado
consentimientos preparados
template de informe aprobado
compromiso de dos sesiones del dueño y operador
pre-clasificación documentada
caso piloto registrado con pilot_case_id
```

Regla:

```text
si falla el checklist, no entra al piloto
```

## Qué medir en cada caso

### Métricas cuantitativas útiles

```text
cantidad de AssertionCandidates evaluadas
distribución READY / BLOCKED / CONTRADICTED / STALE
cantidad de OperatorConfirmations
cantidad de TensionReports
cantidad de evidencia cargada
cantidad de missing_evidence
largo del MinimumEvidencePath
tiempo del operador por fase
tiempo del dueño
case_status final
cantidad de confirm_partial_with_caveat
```

### Métricas cualitativas útiles

```text
si el EpistemicState ayudó al operador
si el dueño sintió que el reporte decía algo verdadero
si las TensionReports mostraron desalineamientos no vistos
si el DominantUnknown priorizó evidencia útil
si el kernel agregó valor o generó fricción
si la audit trail reconstruye la conclusión
```

## Qué NO medir todavía

```text
NPS
CSAT
tiempo a resolución
número de problemas encontrados
revenue per case
daily active operators
retención del cliente
benchmark sectorial
operator throughput
cantidad de confirmaciones como éxito
```

Regla:

```text
si la métrica suena a SaaS, probablemente no sirve para validar este piloto
```

## Señales de que PymIA aporta valor

```text
el operador usa el EpistemicState en conversación
las tensiones dueño-datos aparecen y son útiles
DominantUnknown identifica la evidencia siguiente correcta
el dueño entiende qué se sabe y qué no
el dueño no se siente juzgado
OperatorConfirmation ayuda a registrar criterio humano
la audit trail permite reconstruir conclusiones
el operador dice que esto cambió cómo encara el próximo caso
```

## Señales de que PymIA no está listo

```text
EpistemicState correcto pero no usado
TensionReports difíciles de comunicar sin confrontar
DominantUnknown no es confiable para el operador
el dueño exige score como salida
el kernel estorba más de lo que ayuda
el operador saltea OperatorConfirmation
audit trail ilegible
pack change rompe confirmaciones
LLM sale al cliente sin revisión
```

## Qué sigue manual durante el piloto

```text
sesiones con el dueño
captura de FichaPrimaria
carga/interpretación de evidencia
captura de OwnerSemanticClaims
OperatorConfirmation
redacción/revisión del informe
entrega del informe
consentimientos
```

Regla:

```text
El piloto es operator-mediated by design.
Si se automatiza la conversación o la confirmación, se traiciona el producto.
```

## Qué ejecuta el kernel

```text
linter de evidencia
linter de packs
formula_evaluated
generación de AssertionCandidates
cómputo de TensionReports
cómputo de DominantUnknown
cómputo de MinimumEvidencePath
generación de EpistemicState
audit trail append-only
tracking de versiones de pack
rendering asistido por LLM bajo revisión humana
recomputación ante cambios de evidencia o pack
```

Regla:

```text
El operador carga y decide.
El kernel calcula y traza.
```

## Feedback del operador

Tres mecanismos:

```text
debrief post-caso
diario del operador
revisión side-by-side
```

Preguntas críticas:

```text
qué dijo el kernel que no hubieras visto sin él
dónde se interpuso
si OwnerSemanticClaim ayudó
si TensionReports ayudaron
si DominantUnknown priorizó bien
si OperatorConfirmation fue útil o burocrática
si el informe reflejó el caso real
```

Stop signal:

```text
si en 3 de 5 casos el operador dice que el kernel estorbó más de lo que ayudó, el diseño está mal
```

## Feedback del dueño PyME

Dos mecanismos:

```text
conversación post-entrega
feedback escrito opcional
```

Preguntas:

```text
el reporte te dijo algo verdadero
te dijo algo que no sabías
hubo algo que sintieras como juicio
entendiste qué no se puede saber todavía
entendiste qué dato falta
te quedó claro el próximo paso
te sentiste tratado como par o como alguien analizado
```

Regla:

```text
si el dueño se siente analizado en vez de tratado como par, la retórica falló aunque el kernel calcule bien
```

## Criterios para pasar a producto repetible

Siete condiciones:

```text
C1. 4 de 5 casos llegan a CONFIRMED o SUFFICIENT.
C2. En 3 de 5, DominantUnknown predice la evidencia útil siguiente.
C3. En 3 de 5, TensionReports revelan una desalineación no vista.
C4. En 4 de 5, el dueño reporta verdad, incertidumbre honesta y trato como par.
C5. En 5 de 5, audit trail reconstruye el EpistemicState final.
C6. En 5 de 5, el operador no siente fricción sin payoff en más del 30% de momentos clave.
C7. En 5 de 5, el dueño no reporta sentirse analizado.
```

Veredicto:

```text
5+ de 7 condiciones = producto repetible
4 de 7 = iterar con nuevo piloto de 3-5 casos
3 o menos = rediseño
```

## Decisión candidata para repo

```text
PymIA V1 debe validarse con un piloto operator-assisted de 5 PyMEs reales, heterogéneas y seleccionadas por capacidad de tensionar el kernel.

El piloto no debe medir velocidad, satisfacción superficial ni cantidad de hallazgos.

Debe medir trazabilidad, utilidad operatoria, comprensión del dueño, tratamiento como par, calidad del DominantUnknown y reconstruibilidad del EpistemicState.
```

## Frase de cierre

```text
El piloto es la prueba de que la arquitectura sirve al mundo real, no al revés.
```
