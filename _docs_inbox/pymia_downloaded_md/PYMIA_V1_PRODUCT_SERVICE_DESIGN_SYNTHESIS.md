# PymIA V1 — Diseño de producto/servicio operator-assisted

## Veredicto

La respuesta de Minimax es muy útil porque traduce la arquitectura epistémica a producto vendible sin traicionar el kernel.

La conclusión principal:

```text
PymIA V1 no se vende como SaaS self-service para dueños PyME.
PymIA V1 se vende como servicio diagnóstico operator-assisted para estudios contables, asesores financieros y consultores PyME.
```

## Decisión central

```text
No vendés tecnología.
Vendés criterio trazable.
```

El software es el motor.

El servicio es el vehículo.

El operador es quien convierte el motor en valor percibido por la PyME.

## Comprador real

El comprador V1 recomendado no es la PyME directamente.

Es:

```text
estudio contable
asesor financiero independiente
consultor PyME
equipo profesional con cartera PyME
```

Motivos:

```text
ya tiene confianza del dueño
ya accede a información sensible
ya entiende vocabulario económico/contable
ya sufre el costo de armar diagnósticos manuales
puede convertir el output en conversación consultiva
```

## Anti-buyer V1

```text
dueño PyME directo en self-service
```

Aunque pueda pagar, no es el comprador ideal para V1.

Motivo:

```text
sin operador no hay caso gobernable ni confirmación humana robusta.
```

## Usuario operador

El usuario real del sistema es:

```text
contador
asesor
consultor
auditor interno
equipo SmartPyme
```

No es:

```text
data scientist
programador
prompt engineer
usuario final sin criterio técnico
```

## Trabajo del operador en V1

```text
captura FichaPrimaria
carga evidencia
captura OwnerSemanticClaim
revisa AssertionCandidates
revisa TensionReports
observa DominantUnknown
confirma, ajusta o rechaza candidates
produce informe owner-facing
acompaña conversación de cierre
```

## Qué recibe la PyME

La PyME recibe:

```text
informe diagnóstico firmable
conversación de cierre
próximo paso mínimo
```

Formato inicial recomendado:

```text
markdown
```

PDF puede venir después si se justifica.

## Qué contiene el informe

```text
identidad del caso
período analizado
operador
packs usados
qué se pudo afirmar
con qué evidencia
con qué fórmula
qué confirmó el operador
qué no se pudo afirmar
qué evidencia falta
tensiones dueño-datos
preguntas de recuperación
próximo paso mínimo
```

## Qué NO contiene el informe V1

```text
score
semáforo
riesgo alto/medio/bajo
forecast
viabilidad del negocio
benchmark sectorial
recomendaciones estratégicas automáticas
```

## Flujo de servicio V1

```text
1. Primer contacto comercial.
2. Engagement y consentimiento.
3. Sesión de intake.
4. FichaPrimaria sellada.
5. OwnerSemanticClaim inicial desde problem_statement.
6. Recepción de evidencia.
7. Primera evaluación del kernel.
8. Segunda sesión con el dueño.
9. Segunda evaluación y arbitraje operatorio.
10. EpistemicState final.
11. Informe owner-facing.
12. Entrega y conversación de cierre.
```

Tiempo realista:

```text
5 a 15 días corridos por caso
```

No prometer instantaneidad.

## Qué debe ser manual en V1

```text
sesión de intake
captura de FichaPrimaria
captura de OwnerSemanticClaim
carga/interpretación de evidencia desordenada
OperatorConfirmation
segunda sesión con dueño
redacción/revisión del informe
entrega conversada
```

Motivo:

```text
el valor está en la conversación y el juicio humano.
```

## Qué conviene automatizar en V1

```text
linter de evidencia
linter de packs
formula_evaluated
generación de AssertionCandidates
cómputo de TensionReports
cómputo de DominantUnknown
cómputo de MinimumEvidencePath
generación/actualización de EpistemicState
audit trail append-only
eventos de Pack Governance
rendering asistido por LLM bajo revisión humana
```

Regla:

```text
Automatizar cálculo.
No automatizar juicio.
```

## Qué NO debe aparecer en V1

```text
dashboard
real-time monitoring
scorecard
semáforo
forecast
self-service owner interface
mobile app
multi-tenant SaaS completo
marketplace de packs
alertas push
benchmarking sectorial
ERP/home banking integration automática
API pública
chatbot con el dueño
modelos predictivos
aprendizaje automático del sistema
promesas de cero error
```

## Modelo de cobro

Minimax propone modelo de dos ejes:

### Eje 1 — Por caso diagnóstico

Cobrado a la PyME por el estudio/asesor.

Incluye:

```text
intake
hasta dos sesiones
evaluación kernel
informe
conversación de cierre
```

### Eje 2 — Licencia de plataforma

Cobrada al estudio/asesor.

Incluye:

```text
acceso a PymIA
N casos por mes
training
soporte
actualización de packs
hosting/operación
```

Unidad de valor:

```text
casos diagnosticados por mes por estudio
```

## Modelos a evitar

```text
per-seat SaaS clásico
freemium
per API call
commission on outcomes
revenue share con dueño PyME
```

## Promesas comerciales defendibles

```text
Te entregamos un diagnóstico trazable de la situación actual de tu PyME.
Vas a saber qué se puede afirmar con la evidencia disponible y qué no.
Vas a saber qué dato falta para destrabar lo que hoy no se puede afirmar.
El diagnóstico es revisado por un profesional.
Cada aserción tiene evidencia, fórmula y confirmación documentada.
No usamos score ni semáforo: usamos trazabilidad.
El próximo paso queda claro.
```

## Promesas peligrosas o falsas

```text
diagnóstico en 24 horas
te decimos si tu negocio es viable
IA que predice tu futuro financiero
reemplazamos a tu contador
100% seguro
funciona para cualquier PyME
score de riesgo 0-100
comparación sectorial V1
aprende automáticamente con cada caso
self-service sin operador
cero error
garantizamos encontrar el problema
diagnóstico en 5 minutos
```

## Posicionamiento correcto

```text
PymIA no es un dashboard.
PymIA no es un scorer.
PymIA no es una IA que reemplaza al contador.

PymIA es un servicio diagnóstico asistido por operador,
aumentado por un kernel epistémico trazable.
```

## Producto V1 en una frase

```text
PymIA V1 ayuda a estudios contables y asesores PyME a entregar diagnósticos trazables, honestos y accionables, sin convertir evidencia incompleta en falsa certeza.
```

## Arquitectura convertida en producto

```text
FichaPrimaria
→ OwnerSemanticClaim
→ StructuredEvidence
→ TensionReport
→ AssertionCandidate
→ DominantUnknown
→ OperatorConfirmation
→ EpistemicState
→ Informe markdown firmable
→ Conversación de cierre
```

## Decisiones candidatas para repo

```text
1. Buyer V1 = estudio contable / asesor / consultor PyME.
2. Beneficiario = PyME.
3. Usuario operativo = operador humano.
4. Entrega V1 = informe markdown firmable + conversación.
5. No dashboard en V1.
6. No self-service dueño en V1.
7. No score ni semáforo.
8. No forecast en V1.
9. Automatizar cálculo, no juicio.
10. Cobrar por caso + licencia al operador/estudio.
11. Prometer trazabilidad, no predicción.
12. Producto = servicio diagnóstico operator-assisted.
```

## Riesgo estratégico principal

El riesgo no es que el producto sea poco tecnológico.

El riesgo es venderlo como SaaS genérico y romper la arquitectura.

```text
Si vendés el motor como vehículo, terminás compitiendo contra dashboards.
Si vendés criterio trazable, el motor se vuelve indispensable.
```

## Frase de cierre

```text
PymIA V1 no vende respuestas automáticas.
Vende una forma auditada de saber qué se puede afirmar, qué no, y qué dato falta para avanzar.
```
