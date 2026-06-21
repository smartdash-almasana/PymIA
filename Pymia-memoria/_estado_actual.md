# PymIA Memoria — Estado actual

Fecha: 2026-06-20

## Estado operativo actual

Repo principal:

```text
E:\BuenosPasos\smartbridge\PymIA
```

Subcarpeta viva:

```text
PymIA-Live
```

GitHub:

```text
smartdash-almasana/PymIA
```

## Estado consolidado reciente

Últimos commits reportados y aceptados en esta sesión:

```text
716c6d7 docs(producto): define excel treatment lab concept
f924c27 feat(pymia-live): add first aid entrypoint helper
dd0e659 feat(pymia-live): add first aid owner output helper
67db189 chore(graphify): include pymia live in architecture graph
```

## Cambios actuales no commiteados desde esta sesión

```text
docs/producto/PYMIA_PRODUCT_UNIVERSE_AND_SERVICE_DEPTH_MODEL_FINAL.md
PymIA-Live/docs/pymia/FIRST_AID_LATENT_HELPERS_CHECKPOINT.md
Pymia-memoria/_estado_actual.md
Pymia-memoria/_task_actual.md
Pymia-memoria/_decisiones_vigentes.md
Pymia-memoria/_no_volver_a_hacer.md
```

## Documento de producto final

Documento rector:

```text
docs/producto/PYMIA_PRODUCT_UNIVERSE_AND_SERVICE_DEPTH_MODEL_FINAL.md
```

Cambio agregado:

```text
## 6.4 Pregunta madre de entrada / No-oráculo
```

Estado:

```text
Actualizado sin reemplazar el documento.
Runtime impact: NONE.
Code impact: NONE.
```

## Decisión rectora incorporada

```text
PymIA no es un oráculo.
PymIA es un sistema operativo para reducir tinieblas e incertidumbre mediante preguntas, evidencia y opciones proporcionales.
```

La entrada correcta no debe ser adivinación de profundidad de servicio.

La entrada correcta es preguntar primero:

```text
¿Qué necesitás resolver hoy?
```

Con tres caminos explícitos:

```text
1. Primeros Auxilios
   Tengo algo puntual para ordenar o revisar ahora.

2. Problema específico / diagnóstico sectorial
   Tengo un problema más complejo que quiero entender.

3. Estructura completa de la empresa
   Quiero analizar y ordenar la empresa como sistema.
```

Secuencia rectora:

```text
pregunta inicial
→ opción elegida por el dueño
→ evidencia mínima
→ profundidad de servicio
→ respuesta proporcional
```

Regla:

```text
Service depth no debe ser adivinación.
Debe combinar elección explícita del dueño, evidencia disponible, señales de lenguaje y límites de suficiencia.
La elección explícita del dueño manda primero.
```

## Estado FIRST_AID

```text
FIRST_AID_ENTRYPOINT_V1 = CLOSED
FIRST_AID_OWNER_OUTPUT_V1 = CLOSED
FIRST_AID_APPLICATION_WIRING_V1 = DEFERRED
```

Cadena cerrada:

```text
service_depth.py
→ first_aid_entrypoint.py
→ first_aid_owner_output.py
```

Estado conceptual:

```text
FIRST_AID existe como capacidad latente cerrada.
No está cableado a application, CLI, rendering, storage, OCF ni diagnóstico.
No debe cablearse hasta que exista canal real, caso real o test de integración fallando por falta de wiring.
```

Evidencia reportada:

```text
FIRST_AID_ENTRYPOINT_V1: 8/8 PASS; batería focal 38/38 PASS; forbidden import scan CLEAN.
FIRST_AID_OWNER_OUTPUT_V1: 7/7 PASS; batería focal 19/19 PASS; forbidden import/text scan CLEAN.
FIRST_AID_GRAPHIFY_AUDIT_V1: CLEAN; 15/15 PASS.
```

Checkpoint creado:

```text
PymIA-Live/docs/pymia/FIRST_AID_LATENT_HELPERS_CHECKPOINT.md
```

Estado del checkpoint:

```text
CREATED_NOT_COMMITTED
```

## Estado Graphify

```text
GRAPHIFY_SCOPE_FIX_V1 = CLOSED
GRAPHIFY_POST_COMMIT_REGEN_CHECK_V1 = CLOSED
```

Resultado:

```text
.graphifyignore versionado en 67db189.
PymIA-Live/ queda incluido para auditorías Graphify futuras.
graphify-out/ queda regenerable y untracked intencional.
No seguir invirtiendo ciclos en Graphify salvo decisión arquitectónica concreta.
```

## Excel Treatment Lab

```text
EXCEL_TREATMENT_LAB_PRODUCT_CONCEPT.md = versionado
```

Estado conceptual:

```text
Excel Treatment Lab es puerta FIRST_AID y cámara de descompresión entre caos administrativo y estructura computable.
No es Excel Reader genérico.
No autoriza runtime por sí mismo.
```

## Reglas operativas reforzadas

```text
No deriva GPT.
No alucinaciones arquitectónicas.
No proponer wiring sin necesidad real.
No usar Graphify como ciclo ritual.
No hacer tests desde entorno del asistente si ya se sabe inestable.
No asumir contenido documental sin lectura real.
No abrir runtime por ansiedad de avance.
No convertir helpers cerrados en producto cableado sin canal real.
No usar service_depth como oráculo cuando puede preguntarse explícitamente al dueño.
```

## Próximo foco recomendado

Cerrar documentalmente este frente si el usuario autoriza commit.

Categoría:

```text
D. DOCUMENTACIÓN / MEMORIA
```

## Guardrail actual

```text
La elección explícita del dueño manda primero.
Las señales del lenguaje ayudan, pero no reemplazan la pregunta inicial.
Service depth no debe ser adivinación.
```
