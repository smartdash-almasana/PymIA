# PymIA Memoria — Task actual

Fecha: 2026-06-20

## Task actual

```text
PRODUCT_FINAL_NO_ORACLE_AND_MEMORY_UPDATE
```

## Categoría

```text
D. DOCUMENTACIÓN / MEMORIA
```

## Estado

```text
APPLIED_NOT_COMMITTED
```

## Objetivo

Registrar la corrección conceptual incorporada al documento maestro de producto:

```text
PymIA no es un oráculo.
PymIA reduce tinieblas e incertidumbre preguntando primero.
```

## Archivo modificado

```text
docs/producto/PYMIA_PRODUCT_UNIVERSE_AND_SERVICE_DEPTH_MODEL_FINAL.md
```

Se agregó sección nueva:

```text
## 6.4 Pregunta madre de entrada / No-oráculo
```

## Archivos de memoria actualizados

```text
Pymia-memoria/_estado_actual.md
Pymia-memoria/_task_actual.md
Pymia-memoria/_decisiones_vigentes.md
Pymia-memoria/_no_volver_a_hacer.md
```

## Documento checkpoint creado

```text
PymIA-Live/docs/pymia/FIRST_AID_LATENT_HELPERS_CHECKPOINT.md
```

Estado:

```text
CREATED_NOT_COMMITTED
```

## Decisión rectora incorporada

```text
Service depth no debe ser adivinación.
Debe combinar:
1. elección explícita del dueño;
2. evidencia disponible;
3. señales del lenguaje;
4. límites de suficiencia.
```

La elección explícita del dueño manda primero.

## Pregunta madre

```text
¿Qué necesitás resolver hoy?
```

Opciones:

```text
1. Primeros Auxilios
   Tengo algo puntual para ordenar o revisar ahora.

2. Problema específico / diagnóstico sectorial
   Tengo un problema más complejo que quiero entender.

3. Estructura completa de la empresa
   Quiero analizar y ordenar la empresa como sistema.
```

## FIRST_AID — Estado vigente

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

No cablear application/CLI/rendering mientras no exista canal consumidor real, caso piloto real o test de integración fallando por falta de wiring.

## Próximo paso recomendado

Commit documental focal con los archivos modificados de este frente, si el usuario lo autoriza.

Archivos candidatos:

```text
docs/producto/PYMIA_PRODUCT_UNIVERSE_AND_SERVICE_DEPTH_MODEL_FINAL.md
PymIA-Live/docs/pymia/FIRST_AID_LATENT_HELPERS_CHECKPOINT.md
Pymia-memoria/_estado_actual.md
Pymia-memoria/_task_actual.md
Pymia-memoria/_decisiones_vigentes.md
Pymia-memoria/_no_volver_a_hacer.md
```

Commit sugerido:

```text
docs(pymia): record no-oracle service entry decision
```

## Prohibiciones vigentes

```text
No runtime.
No tests.
No Graphify.
No wiring application.
No CLI.
No rendering.
No OCF write-model.
No diagnóstico por inferencia.
No abrir más frentes antes de cerrar este documental.
```
