# ADR-008: Integración Hermes ↔ PymIA vía MCP

## Estado
Propuesta

## Contexto
El sistema necesita una frontera estable entre el organismo conversacional y la computabilidad clínica-operacional.

Marco conceptual:
- El dueño es agente creacional.
- La PyME/negocio es universo observado conocido/desconocido.
- Hermes es organismo operativo/conversacional.
- PymIA es la inteligencia computacional de Hermes.

Necesidad arquitectónica:
- Hermes debe poder orquestar, conversar, mantener estado y presentar resultados.
- Hermes no debe suplantar ni duplicar la computabilidad clínica/matemática de PymIA.
- PymIA debe exponer capacidades clínicas/computacionales como herramientas invocables por contrato.

## Decisión
Adoptar una integración MCP donde:
- Hermes actúa como **MCP client**.
- PymIA actúa como **MCP server**.

## Opciones evaluadas
1. Hermes como MCP client de PymIA MCP server.
2. PymIA como MCP client de Hermes MCP server.
3. PymIA consume API server de Hermes.

## Opción elegida
**Hermes MCP client → PymIA MCP server**.

## Consecuencias positivas
- Se separan claramente conversación/orquestación y computabilidad clínica.
- Se evita duplicar lógica diagnóstica en Hermes.
- Se formaliza un contrato de tools explícito, testeable y auditable.
- Se habilita evolución independiente de Hermes y PymIA por frontera estable.
- Se preserva el principio: PymIA decide clínicamente; Hermes canaliza operacionalmente.

## Riesgos
- Acoplamiento temprano a contratos MCP incompletos.
- Sobrecarga de latencia en llamadas tool-by-tool si el diseño es demasiado granular.
- Riesgo de bypass: que Hermes intente inferir/diagnosticar fuera de tools.
- Deriva semántica entre nombres de tools y contratos reales de salida.
- Riesgo de estados inconsistentes si no se define bien la carga/guardado del contexto progresivo.

## Mitigaciones
- Versionar contratos MCP desde v1 con schemas estrictos.
- Definir tools con responsabilidades atómicas pero de valor clínico (no micro-tools triviales).
- Validar en tests de frontera que Hermes no produce diagnóstico sin output formal de PymIA.
- Mantener reglas de frontera explícitas y tests de no-bypass.
- Incluir contratos de contexto progresivo (`load/save`) con claves de sesión claras.

## Tools candidatas de PymIA
- `taxonomic_classify`
- `first_clinical_interview`
- `anamnesis_step`
- `symptom_intake`
- `evidence_requirements`
- `progressive_context_load`
- `progressive_context_save`
- `operational_audit`

## Reglas de frontera
- Hermes no diagnostica.
- Hermes no interpreta Excel.
- Hermes no calcula margen.
- Hermes no crea hallazgos.
- Hermes no pide evidencia clínica sin output de PymIA.
- Hermes no inventa taxonomía.
- PymIA no gestiona canal ni conversación libre.

## Próximo paso
Diseñar contrato MCP mínimo para `pymia.first_clinical_interview`:
- input mínimo,
- output estructurado,
- errores contractuales,
- criterios de bloqueo/continuación de fase.
