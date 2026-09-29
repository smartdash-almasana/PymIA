# 03 — MVP recomendado: Servicio 1 asistido

## Nombre recomendado

```text
Servicio 1 — Primeros Auxilios Asistidos para PyME
```

## Qué es

Un servicio asistido, operado por humano, que toma datos administrativos/operativos de una PyME y produce una primera lectura trazable de señales críticas.

No es todavía SaaS autónomo. No es chatbot. No es diagnóstico automático completo.

## Flujo mínimo

```text
1. Dueño PyME declara preocupación principal.
2. Operador recibe archivo(s) y contexto mínimo.
3. PymIA inspecciona Excel/datos.
4. PymIA construye evidencia estructurada.
5. PymIA calcula solo variables soportadas.
6. PymIA activa solo reglas con evidencia suficiente.
7. Operador revisa salida.
8. Se entrega resumen owner-facing.
9. Dueño confirma/corrige.
10. Se registra evidencia y resultado.
```

## Qué incluye

- CLI o ejecución local controlada.
- Carpeta de caso.
- Registro de archivos recibidos.
- Evidencia estructurada.
- Variables calculadas soportadas.
- Preguntas faltantes al dueño.
- Resumen owner-facing breve.
- Manifest de ejecución.
- Revisión humana obligatoria.

## Qué no incluye

- Hermes.
- SaaS autónomo.
- Agente LLM decidiendo.
- Diagnóstico soberano sin evidencia.
- Conciliación bancaria plena si no está implementada.
- Catálogo completo activado si no hay reglas.
- Promesa comercial de “50 patologías detectadas”.
- Conversación automatizada como fuente de verdad.

## Catálogo activo vs catálogo aspiracional

El catálogo debe dividirse explícitamente:

| Tipo | Descripción |
|---|---|
| Catálogo activo | Tiene regla, evidencia requerida, test y salida trazable |
| Catálogo aspiracional | Existe como vocabulario/roadmap, pero no se promete como capacidad |
| Catálogo presentation-only | Sirve para lenguaje owner-facing, no para detección |

Regla:

```text
No se vende ni se reporta como detectado lo que no tenga regla y evidencia suficiente.
```

## Criterio de éxito MVP

El MVP se considera validado cuando exista al menos:

1. Un caso real de PyME.
2. Archivo(s) reales procesados.
3. Evidencia estructurada generada.
4. Output owner-facing revisado por operador.
5. Feedback del dueño.
6. Lista de correcciones aprendidas.
7. Registro reproducible de ejecución.
8. Decisión explícita: repetir, ajustar o descartar.

## Decisión sobre owner_message

Para MVP asistido:

```text
owner_message no necesita gobernar automáticamente todo el pipeline.
```

Pero sí debe quedar registrado y usado por el operador para priorizar la lectura.

Para una fase posterior:

```text
owner_message → síntoma declarado → evidencia requerida → pregunta priorizada
```

Debe implementarse como contrato propio, no como comportamiento implícito.

## Recomendación de alcance

Trabajar con pocos problemas PyME de alto valor:

- caja;
- margen;
- ventas vs cobros;
- costos;
- stock si hay evidencia suficiente;
- señales de rentabilidad negativa.

Evitar abrir 50 patologías antes de validar que el dueño entiende y usa la salida.
