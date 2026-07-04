# SERVICE_1_RUNTIME_GOVERNANCE_V1

## Propósito

Este documento define la gobernanza funcional completa de Servicio 1 desde que el dueño inicia un caso hasta que recibe valor.

## Flujo canónico

```text
Dueño
↓
Expresa un dolor
↓
LLM conversa (anamnesis)
↓
Catálogo de patologías propone hipótesis
↓
PymIA solicita evidencia mínima
↓
Dueño responde y sube archivos
↓
Servicio 1 ejecuta skills y microservicios
↓
Motor determinístico computa resultados
↓
Contraste evidencia ↔ patologías
↓
Diagnóstico
↓
Tratamiento recomendado
↓
Entregables
↓
Próximos pasos
```

## Responsabilidades

### Conversación
- Comprender el lenguaje del dueño.
- Pedir aclaraciones.
- Solicitar evidencia faltante.
- No emitir diagnóstico definitivo.

### Catálogo de patologías
- Transformar señales en hipótesis.
- Definir evidencia mínima.
- Priorizar posibles tratamientos.
- No ejecutar cálculos.

### Motor determinístico
- Ejecutar fórmulas, validaciones y microservicios.
- Generar evidencia objetiva.
- No interpretar por sí solo el negocio.

### Diagnóstico
- Integrar evidencia y patologías.
- Explicar el problema en lenguaje PyME.
- Priorizar acciones.

## Reglas rectoras

1. La IA conversa; no inventa evidencia.
2. PymIA computa; no improvisa resultados.
3. El catálogo gobierna el diagnóstico; no realiza cálculos.
4. Los microservicios producen evidencia; no determinan por sí solos la patología.
5. Todo diagnóstico debe poder justificarse con evidencia obtenida del caso.

## Metodología de evolución

Las nuevas capacidades se integrarán preferentemente mediante Feature Flag + Shadow Mode. Sólo después de validar resultados podrán participar del routing activo.
