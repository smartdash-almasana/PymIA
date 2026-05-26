# HERMES_AGENT_AUDIT_POLICY

## Tesis

Hermes conversa y orquesta. PymIA computa.

Hermes no reemplaza el cálculo soberano de PymIA. PymIA es la fuente de verdad
para hallazgos y resultados operativos.

## Roles

### Hermes LLM Agent

- Gestiona conversación con usuario.
- Solicita contexto y evidencia faltante.
- Orquesta flujo hacia contratos válidos.
- Renderiza salida permitida por contrato.
- No calcula diagnóstico soberano.

### Hermes Audit Agent

- Audita decisiones del Hermes LLM Agent antes de entregar.
- Verifica cumplimiento de frontera Hermes ↔ PymIA.
- Evalúa riesgo de contaminación semántica u operativa.
- Emite decisión conceptual: `ALLOW`, `WARN`, `BLOCK`.

## Frontera Hermes ↔ PymIA

- Entrada a PymIA: evidencia/candidatos estructurados.
- Salida de PymIA: resultados soberanos y campos permitidos para render.
- Hermes no modifica significado del resultado soberano.
- Hermes no agrega hallazgos ni recalcula métricas.

## Datos permitidos y prohibidos

### Permitidos en Hermes

- Texto conversacional del usuario.
- Metadata operativa mínima de sesión y tenant.
- Referencias a evidencia autorizada.
- Resultado soberano de PymIA para render controlado.

### Prohibidos en Hermes

- Datos crudos sensibles no autorizados por contrato.
- Tokens/secretos/configuración sensible.
- Mezcla de contexto entre tenants.
- Resultado clínico/operativo inventado fuera del kernel.

## Contrato conceptual: AuditDecision

`AuditDecision`:

- `ALLOW`: salida segura y alineada al contrato.
- `WARN`: salida permitida con riesgo menor, requiere aviso explícito.
- `BLOCK`: salida no entregable, se detiene flujo.

## Reglas de bloqueo (BLOCK)

Bloquear de forma inmediata si Hermes intenta:

1. Inventar hallazgos no emitidos por PymIA.
2. Recalcular métricas soberanas por fuera del kernel.
3. Mezclar tenants o referencias cruzadas de sesión.
4. Saltar gates de evidencia/readiness/ejecución.
5. Convertir warnings en diagnósticos cerrados.
6. Usar datos crudos prohibidos por política/contrato.

## Ejemplos

### ALLOW

- PymIA devuelve resultado `EXECUTED` válido.
- Hermes resume hallazgos sin reinterpretar.
- Hermes entrega referencias de salida permitidas.

### WARN

- Salida técnicamente válida pero con warnings de contexto incompleto.
- Hermes entrega respuesta con aviso explícito de limitación.
- No se altera el veredicto soberano.

### BLOCK

- Hermes agrega “diagnóstico final” no presente en PymIA.
- Hermes mezcla evidencia de otro tenant.
- Hermes intenta bypass de gate para forzar entrega.

## Roadmap (máximo 2 ciclos)

1. Fixture smoke determinístico.
- Escenario mínimo reproducible con entradas/salidas controladas.
- Validación de `ALLOW/WARN/BLOCK` sin ejecutar canales reales.

2. Experimento con 4 Excels y kernel como fuente de verdad.
- Correr 4 casos controlados.
- Hermes solo conversa/orquesta.
- PymIA conserva autoridad de cómputo y veredicto.
