# FIRST_AID_GPT_V1_REAL_PILOT_INTAKE_PROTOCOL

## Estado

```text
Tipo: PRODUCT_OPERATION_PROTOCOL
Estado: READY_FOR_REAL_ASSISTED_PILOTS
Runtime impact: NONE
Code impact: NONE
```

Este protocolo define cómo recibir los primeros 3 casos reales de dueños PyME para `Primeros Auxilios GPT V1` en modo asistido, manual y prudente.

No autoriza runtime, pipeline, `diagnostic_core`, OCF productivo, replay, storage, canales externos, automatización, chatbot ni diagnóstico real.

---

# 1. Veredicto

```text
FIRST_AID_GPT_V1_REAL_PILOT_INTAKE_PROTOCOL: READY
REAL_ASSISTED_PILOTS_ALLOWED: YES
MAX_INITIAL_REAL_CASES: 3
AUTOMATED_PRODUCT_ALLOWED: NO
RUNTIME_EXPANSION_ALLOWED: NO
DIAGNOSTIC_PROMISE_ALLOWED: NO
```

El frente puede recibir 3 casos reales en modalidad asistida si cada caso cumple admisión, consentimiento operativo simple, anonimización y registro de aprendizaje.

---

# 2. Propósito

Definir un modo seguro de entrada para casos reales de dueños PyME sin convertir el piloto en producto automático.

El protocolo responde:

```text
qué se le pide al dueño
qué archivos puede enviar
qué archivos NO debe enviar
qué contexto mínimo necesitamos
qué entra como Primeros Auxilios
qué queda fuera de alcance
qué advertencias se dan antes de revisar
qué salida prometemos
qué salida NO prometemos
cómo se anonimiza el caso
cómo se documenta el aprendizaje
cuándo se bloquea el caso
cuándo se deriva a Nivel 2
```

---

# 3. Alcance

Este protocolo cubre únicamente:

```text
recepción manual de hasta 3 casos reales
revisión asistida de evidencia puntual
respuesta owner-safe de Primeros Auxilios
registro manual de aprendizaje de producto
anonimización mínima del caso
criterios de bloqueo y derivación
```

Queda fuera:

```text
runtime
pipeline
diagnostic_core
OCF productivo
replay
storage
canales externos
automatización
chatbot
diagnóstico real
auditoría
asesoramiento profesional
```

---

# 4. Principio operativo

```text
Primeros Auxilios PyME no diagnostica la empresa.
Ordena una evidencia puntual, marca señales visibles, explicita límites y propone la próxima pregunta razonable.
```

El operador debe priorizar:

```text
claridad antes que profundidad
límite antes que conclusión
pregunta siguiente antes que recomendación definitiva
evidencia faltante antes que diagnóstico
lenguaje owner-safe antes que jerga técnica
```

---

# 5. Qué se acepta como caso real

Un caso real aceptable debe tener:

```text
un dueño o responsable operativo identificable
una preocupación concreta
una evidencia puntual revisable
expectativa de ordenar o entender señales visibles
permiso para aprendizaje anonimizado
posibilidad de ocultar datos sensibles
```

Ejemplos aceptables:

```text
ventas sin costos completos
lista de precios/costos con dudas de margen
stock/inventario declarado
caja/banco desordenado
conciliación simple no cerrada
```

---

# 6. Qué NO se acepta

No se acepta un caso si el dueño solicita:

```text
diagnóstico integral
auditoría
investigación de fraude
confirmación de rentabilidad real
confirmación de stock físico real
conciliación bancaria cerrada
asesoramiento legal
asesoramiento fiscal
asesoramiento contable profesional
automatización
integración con canales externos
```

Tampoco se acepta si requiere ejecutar macros, manipular credenciales, procesar datos sensibles no anonimizables o trabajar sin pregunta operativa.

---

# 7. Información mínima del dueño

Antes de revisar cualquier archivo se debe pedir:

```text
nombre del negocio o alias anonimizado
rubro
rol de quien consulta
problema en una frase
archivo disponible
qué espera entender
urgencia
autorización de uso anonimizado para aprendizaje
datos sensibles que deben ocultarse
```

Si falta la pregunta concreta o la autorización de aprendizaje anonimizado, el caso no entra al piloto.

---

# 8. Evidencia aceptada

Se acepta evidencia puntual como:

```text
Excel de ventas
lista de precios
lista de costos
stock/inventario
movimientos de caja
extracto o export bancario
liquidaciones POS/Mercado Pago
capturas o PDFs sólo si son auxiliares, no como fuente productiva principal
```

Preferencia:

```text
archivos tabulares simples
una fuente principal por caso
datos anonimizados antes de compartir
archivos sin macros ejecutables
período temporal claro
```

---

# 9. Evidencia prohibida o sensible

No se debe recibir ni conservar:

```text
contraseñas
tokens
datos bancarios completos innecesarios
DNI/CUIT de terceros no anonimizados
nóminas completas
datos médicos
datos de menores
información legal sensible
archivos con macros no revisadas
```

Si el dueño tiene esa información dentro del archivo, debe ocultarla antes de enviar o el caso se bloquea.

---

# 10. Advertencia previa al dueño

Texto sugerido:

```text
Esto es una revisión asistida de Primeros Auxilios PyME.
No es auditoría, diagnóstico integral ni asesoramiento contable, fiscal o legal.
Vamos a mirar una evidencia puntual para ordenar qué se puede ver, qué no se puede afirmar todavía y cuál es la próxima pregunta razonable.
Si el archivo trae datos sensibles, contraseñas, datos de terceros o información que no querés compartir, por favor ocultalos antes de enviarlo.
```

---

# 11. Promesa permitida

La única promesa permitida es:

```text
Primeros Auxilios PyME no diagnostica la empresa.
Ordena una evidencia puntual, marca señales visibles, explicita límites y propone la próxima pregunta razonable.
```

En lenguaje comercial prudente:

```text
Te ayudamos a entender qué muestra tu archivo, qué límites tiene y qué dato conviene pedir o revisar después.
```

---

# 12. Promesas prohibidas

```text
No prometemos diagnóstico integral.
No prometemos auditoría.
No prometemos detectar fraude.
No prometemos confirmar rentabilidad real.
No prometemos confirmar stock físico real.
No prometemos conciliación bancaria cerrada.
No prometemos recomendación contable, legal ni fiscal.
No prometemos automatización.
```

También queda prohibido prometer:

```text
resultados económicos
corrección automática del archivo
integración con sistemas del dueño
canales externos
chatbot operativo
OCF productivo
```

---

# 13. Flujo operativo del piloto real

1. Recibir interés del dueño.
2. Enviar advertencia previa y alcance.
3. Completar formulario de intake.
4. Confirmar consentimiento operativo simple.
5. Revisar si el caso cumple admisión.
6. Solicitar anonimización o limpieza si hay datos sensibles.
7. Recibir una evidencia puntual.
8. Revisar manualmente en modo asistido.
9. Preparar devolución owner-safe.
10. Registrar cierre del caso.
11. Registrar aprendizaje de producto anonimizado.
12. Decidir si quedó en First Aid, se bloqueó o debe derivarse a Nivel 2.

---

# 14. Criterio de admisión

Un caso entra si cumple:

```text
hay dueño o responsable operativo
hay pregunta concreta
hay evidencia puntual
el archivo puede revisarse sin ejecutar macros
la expectativa es ordenar/señalar, no diagnosticar
el caso puede anonimizarse
```

Admisión posible:

```text
ACCEPT_FIRST_AID_REAL_PILOT
REQUEST_ANONYMIZATION_BEFORE_ACCEPTANCE
REQUEST_CLEARER_OWNER_QUESTION
BLOCK_CASE
```

---

# 15. Criterio de bloqueo

Bloquear si:

```text
el dueño pide diagnóstico integral
el dueño pide auditoría/fraude
el dueño pide asesoramiento legal/fiscal/contable profesional
el archivo requiere ejecutar macros
la evidencia es demasiado sensible
no hay pregunta operativa
no hay permiso para usar el caso como aprendizaje anonimizado
```

Mensaje de bloqueo sugerido:

```text
Con ese alcance no lo podemos tomar como Primeros Auxilios PyME.
Para cuidarte y cuidar el proceso, no hacemos diagnóstico integral, auditoría ni revisión legal/fiscal/contable profesional.
Si querés, podemos reformularlo como una revisión puntual de una evidencia concreta y anonimizada.
```

---

# 16. Criterio de derivación a Nivel 2

Derivar si:

```text
requiere cruzar múltiples fuentes
requiere fórmula determinística con evidencia suficiente
requiere diagnóstico económico-financiero
requiere análisis de rotación real
requiere conciliación real
requiere evaluación de rentabilidad real
```

La derivación no debe venderse como diagnóstico automático. Debe presentarse como otro nivel de profundidad que requiere más evidencia y otro acuerdo de trabajo.

---

# 17. Plantilla de intake

```yaml
real_pilot_intake:
  case_id: REAL_PILOT_CASE_00X
  intake_date: YYYY-MM-DD
  operator: assisted_manual

  business_context:
    business_alias: ""
    rubro: ""
    role_of_requester: ""

  owner_question:
    problem_in_one_sentence: ""
    what_owner_expects_to_understand: ""
    urgency: low | medium | high

  evidence:
    available_file_type: ""
    file_description: ""
    has_macros: yes | no | unknown
    contains_sensitive_data: yes | no | unknown
    sensitive_data_to_hide: []

  consent:
    understands_not_diagnosis: yes | no
    authorizes_anonymized_learning: yes | no
    accepts_no_runtime_no_automation: yes | no

  admission:
    verdict: ACCEPT_FIRST_AID_REAL_PILOT | REQUEST_MORE_CONTEXT | REQUEST_ANONYMIZATION | BLOCK_CASE | REFER_LEVEL_2
    reason: ""
```

---

# 18. Plantilla de consentimiento operativo simple

```text
Acepto que esta revisión es un piloto asistido de Primeros Auxilios PyME.
Entiendo que no es auditoría, diagnóstico integral ni asesoramiento contable, fiscal o legal.
Entiendo que la revisión puede ordenar una evidencia puntual, marcar señales visibles, indicar límites y proponer una próxima pregunta.
Confirmo que oculté datos sensibles que no deben compartirse.
Autorizo que el caso se use como aprendizaje de producto de forma anonimizada, sin nombre real del negocio ni datos identificables.
```

Campos:

```text
Nombre o alias del negocio:
Rol de quien autoriza:
Fecha:
Autoriza aprendizaje anonimizado: SÍ / NO
Datos sensibles ocultados: SÍ / NO / NO APLICA
```

---

# 19. Plantilla de devolución inicial

```text
Recibimos [tipo de archivo].
Podemos revisar [X].
No podemos afirmar [Y].
Para avanzar necesitamos [Z].
```

Versión extendida:

```text
Recibimos [tipo de archivo] sobre [tema del caso].
Con esta evidencia podemos revisar [señales visibles o estructura revisable].
No podemos afirmar [diagnóstico, rentabilidad real, stock físico real, conciliación cerrada u otro límite].
El dato o contexto que falta para avanzar es [evidencia faltante].
La próxima pregunta razonable es: [pregunta siguiente].
```

---

# 20. Plantilla de cierre del caso

```yaml
real_pilot_case_closure:
  case_id: REAL_PILOT_CASE_00X
  closure_date: YYYY-MM-DD

  received:
    evidence_type: ""
    owner_question: ""

  reviewed:
    what_could_be_reviewed: []
    visible_signals: []

  blocked:
    blocked_items: []
    reason: ""

  missing:
    missing_evidence: []
    missing_context: []

  next_question:
    owner_safe_next_question: ""

  depth_decision:
    remained_first_aid: yes | no
    referred_to_level_2: yes | no
    referral_reason: ""

  product_learning:
    repeated_pain: []
    language_adjustment: []
    missing_template_candidate: []
    risk_detected: []
```

---

# 21. Registro de aprendizaje

El aprendizaje del piloto debe registrarse sin datos identificables.

Permitido:

```text
rubro general
tipo de archivo
pregunta del dueño reescrita
patrón de dolor
qué evidencia faltó
qué límite hubo que explicar
qué plantilla faltó
si derivó o quedó en First Aid
```

Prohibido:

```text
nombre real del negocio
clientes, proveedores o empleados identificables
DNI/CUIT de terceros
números de cuenta completos
contraseñas o tokens
capturas con datos personales innecesarios
archivos originales sin anonimizar como memoria de producto
```

---

# 22. Casos objetivo para los primeros 3 pilotos reales

## REAL_PILOT_CASE_001

```text
comercio con Excel de ventas, sin costos completos
```

Objetivo:

```text
validar si el dueño entiende la diferencia entre ventas, productos más vendidos y rentabilidad no afirmable.
```

## REAL_PILOT_CASE_002

```text
pyme con lista de precios/costos o márgenes dudosos
```

Objetivo:

```text
validar margen bruto estimado, costo faltante, valor ambiguo y límite de rentabilidad real.
```

## REAL_PILOT_CASE_003

```text
pyme con caja/banco/stock desordenado
```

Objetivo:

```text
validar señales operativas sin afirmar conciliación, fraude, stock físico real ni rotación real.
```

---

# 23. Regla de anonimización

Antes de registrar aprendizaje o compartir internamente el caso:

```text
reemplazar nombre del negocio por alias
eliminar datos de clientes/proveedores/personas
ocultar DNI/CUIT de terceros
ocultar cuentas bancarias completas
eliminar contraseñas, tokens y accesos
reemplazar importes sensibles si no son necesarios para el aprendizaje
mantener sólo estructura y patrón operativo relevante
```

Regla mínima:

```text
Si no puede anonimizarse sin destruir el caso, el caso se bloquea.
```

---

# 24. Riesgos controlados

| Riesgo | Control |
|---|---|
| Convertir piloto en diagnóstico | Advertencia previa y promesa limitada. |
| Recibir datos sensibles innecesarios | Regla de evidencia prohibida y anonimización. |
| Abrir runtime por presión operativa | Regla explícita NO_RUNTIME y revisión manual. |
| Prometer automatización | Promesa prohibida y consentimiento operativo. |
| Sobrediagnosticar fraude, rentabilidad o stock | Límites owner-safe y criterios de Nivel 2. |
| Usar aprendizaje como OCF productivo | Registro anonimizado de producto, no expediente productivo. |
| Ejecutar macros o archivos riesgosos | Bloqueo si requiere macros no revisadas. |

---

# 25. Próximo frente recomendado

```text
FIRST_AID_GPT_V1_REAL_PILOT_CASE_LOGS
```

Objetivo:

```text
registrar los 3 casos reales asistidos con aprendizaje anonimizado, sin runtime, sin OCF productivo y sin prometer diagnóstico.
```

Este frente debe usar el presente protocolo, el guion operativo y la plantilla de log ya existentes.

---

# 26. Regla de cierre

```text
NO_RUNTIME
NO_PIPELINE
NO_DIAGNOSTIC_CORE
NO_OCF_PRODUCTIVE_WRITE
NO_REPLAY
NO_STORAGE
NO_EXTERNAL_CHANNELS
NO_AUTOMATION
NO_CHATBOT
NO_REAL_DIAGNOSTIC_CLAIM
NO_NEW_FEATURES
```

Este protocolo habilita sólo recepción asistida, manual y documentada de 3 casos reales. No abre producto automático.
