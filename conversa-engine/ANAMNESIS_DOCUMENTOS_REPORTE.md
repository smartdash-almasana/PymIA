# Anamnesis, documentos y reporte

## Objetivo

Convertir `conversa-engine` en el interlocutor que guía al dueño PyME desde un síntoma inicial hasta un reporte simple y contundente.

## Regla arquitectónica

```text
Hermes conversa.
conversa-engine guía.
PymIA computa.
```

## Flujo operativo deseado

```text
1. Usuario expresa síntoma operacional.
2. conversa-engine ejecuta PymIA para detectar hipótesis iniciales.
3. conversa-engine contrasta síntomas e hipótesis contra catálogo de patologías PyME.
4. conversa-engine solicita evidencia mínima según patologías candidatas.
5. Usuario envía documentos: Excel, CSV, PDF o texto.
6. conversa-engine registra qué evidencia llegó y qué falta.
7. conversa-engine recontrasta contra catálogo: evidencia disponible vs evidencia requerida.
8. PymIA computa línea de base operacional.
9. conversa-engine devuelve reporte simple, breve y accionable.
```

## Anamnesis mínima

El sistema debe empujar la conversación para obtener:

- tipo de negocio
- cómo vende
- qué cobra
- frecuencia de ventas
- costos fijos
- costos variables
- movimientos de caja
- deudas o compromisos críticos
- stock, si aplica
- planillas disponibles
- extractos disponibles

## Documentos aceptados

Primera versión:

- `.xlsx`
- `.csv`
- `.pdf`
- `.txt`

## Regla para documentos

Cuando el usuario envía documentación, `conversa-engine` no debe diagnosticar solo por intuición.
Debe:

1. identificar tipo de archivo
2. extraer datos relevantes
3. declarar evidencia detectada
4. declarar evidencia faltante
5. pedir confirmación si hay ambigüedad
6. enviar datos estructurados a PymIA

## Reporte final esperado

Formato objetivo:

```text
REPORTE OPERACIONAL INICIAL

1. Diagnóstico principal
2. Evidencia observada
3. Riesgo más urgente
4. Acción recomendada esta semana
5. Datos faltantes para precisión
```

## Tono del reporte

- simple
- contundente
- sin jerga excesiva
- orientado a dueño PyME
- no académico
- no consultoría genérica

## Criterio de éxito

El usuario debe terminar con una respuesta útil aunque los datos sean incompletos:

```text
Con lo que hay, esto es lo más probable.
Para confirmarlo, falta esto.
La acción inmediata es esta.
```
