# AAAS Operational Boundary

## Estado

**CANDIDATO_OPERATIVO**

**Fecha:** 2026-06-13

## Definición

En PymIA, **AAAS** significa:

```text
AI Agent as a Service
```

Traducción operacional:

```text
Agente IA corriendo sobre una plataforma SaaS PyME.
```

AAAS no define una plataforma genérica de software. Define la frontera operativa donde PymIA actúa como agente conversacional, evidencial y asistido sobre un SaaS, sin abandonar el kernel determinístico, la trazabilidad de evidencia ni los bloqueos fail-closed.

## Decisión rectora

```text
PymIA no es un dashboard con IA pegada.
PymIA es un agente operativo sobre SaaS gobernado por contratos, evidencia y estado del caso.
```

## Propósito

Este documento fija qué puede y qué no puede hacer PymIA cuando se lo piensa como AAAS.

El objetivo no es abrir producto, runtime ni canal externo. El objetivo es dejar definida la frontera mínima para avanzar hacia operación real sin confundir:

- agente IA,
- SaaS,
- conversación con el dueño,
- evidencia,
- diagnóstico inicial,
- pronóstico,
- reporte owner-facing,
- acción asistida,
- decisión soberana del dueño.

## Qué es AAAS en PymIA

AAAS es la capacidad de PymIA de operar como agente IA situado sobre una plataforma SaaS PyME, capaz de:

1. Recibir el relato inicial del dueño.
2. Interpretar el problema como hipótesis candidata, no como verdad.
3. Pedir evidencia o sentido operativo faltante.
4. Procesar evidencia estructurada cuando exista.
5. Bloquear cuando la evidencia es insuficiente.
6. Emitir diagnóstico inicial candidato si la frontera P1 lo permite.
7. Traducir resultados a lenguaje owner-facing sin alterar el core.
8. Proyectar pronóstico sólo cuando haya base suficiente.
9. Proponer próximos pasos asistidos sin ejecutarlos por cuenta propia.
10. Mantener continuidad del caso.

## Qué NO es AAAS en PymIA

AAAS no es:

- chatbot genérico,
- dashboard con respuestas decorativas,
- ERP,
- BI,
- consultor mágico,
- sistema que diagnostica sin evidencia,
- motor libre de predicción,
- reemplazo del dueño,
- reemplazo del contador, consultor o responsable operativo,
- canal productivo autorizado por este documento,
- autorización de Telegram, FastAPI, Hermes runtime, PDF productivo o delivery externo,
- autorización para modificar DiagnosticCoreV1,
- autorización para implementar FormulaPack, PathologyPack, CatalogPack o PackRegistry.

## Frontera con el SaaS

El SaaS puede aportar:

- identidad técnica del tenant,
- identidad de negocio del cliente,
- sesión conversacional,
- archivos o evidencia cargada,
- historial del caso,
- estado visible para el usuario,
- canal de interacción,
- permisos,
- trazabilidad de acciones.

El SaaS no debe reemplazar al kernel.

El SaaS no decide diagnóstico. El SaaS no confirma hallazgos. El SaaS no transforma respuestas del dueño en evidencia dura por sí mismo.

## Frontera con el agente IA

El agente IA puede:

- interpretar lenguaje natural,
- ordenar el caso,
- formular preguntas,
- explicar límites,
- humanizar preguntas owner-facing,
- resumir estado del caso,
- proponer próximos pasos bajo contrato.

El agente IA no puede:

- inventar evidencia,
- confirmar findings,
- saltar evidence sufficiency,
- mutar estados universales,
- modificar contratos,
- ejecutar decisiones sin autorización,
- transformar inferencias en datos materiales,
- asumir que una respuesta ambigua del dueño equivale a DecisionRecord.

## Frontera con el kernel

El kernel conserva autoridad sobre:

- contratos,
- validación,
- evidence sufficiency,
- diagnostic core,
- gates,
- estados universales,
- outputs soberanos,
- fail-closed,
- trazabilidad.

El AAAS consume capacidades del kernel. No lo reemplaza.

## Flujo operativo mínimo

```text
Dueño expresa problema
  → Agente interpreta hipótesis candidata
  → PymIA registra contexto inicial
  → PymIA pide evidencia o sentido faltante
  → Evidence gate evalúa suficiencia
  → DiagnosticCore opera sólo si hay inputs suficientes
  → P1/owner-facing traduce estado sin inflar conclusiones
  → Pronóstico se habilita sólo si hay base suficiente
  → Próxima acción se propone, no se ejecuta automáticamente
  → Dueño confirma, corrige o autoriza según contrato
```

## Estados mínimos del AAAS

| Estado | Significado | Salida permitida |
|---|---|---|
| `INTAKE_OPEN` | El dueño inició conversación o caso | Preguntas de encuadre |
| `NEEDS_CONTEXT` | Falta sentido operativo básico | Repregunta semántica |
| `NEEDS_EVIDENCE` | Falta evidencia material | Pedido de evidencia |
| `BLOCKED_ACTIONABLE` | No se puede avanzar, pero hay pedido claro | Bloqueo explicado + próximos datos requeridos |
| `INITIAL_DIAGNOSIS_CANDIDATE` | Hay comprensión inicial candidata | Primer diagnóstico no final |
| `CORE_READY` | Hay evidencia suficiente para core | Ejecución determinística habilitable |
| `OWNER_REVIEW` | El dueño debe confirmar/corregir/autorizar | Preguntas owner-facing |
| `PROGNOSIS_ELIGIBLE` | Hay base para pronóstico prudente | Pronóstico condicional |
| `ACTION_ASSISTANCE_ELIGIBLE` | Hay base para asistencia operativa | Propuesta de próximo paso |

## Outputs permitidos

AAAS puede producir:

- resumen del problema declarado,
- hipótesis candidata,
- pedido de evidencia,
- pedido de aclaración,
- bloqueo accionable,
- diagnóstico inicial candidato,
- resumen owner-facing,
- pronóstico condicional,
- próximos pasos sugeridos,
- registro de continuidad del caso.

## Outputs prohibidos

AAAS no puede producir:

- diagnóstico final sin evidencia suficiente,
- finding confirmado sin contrato correspondiente,
- pronóstico como certeza,
- acción ejecutada sin autorización explícita,
- modificación de datos del caso sin traza,
- DecisionRecord implícito,
- evidencia fabricada,
- recomendación financiera/legal/contable concluyente sin frontera profesional y evidencia.

## Relación con P1

P1 cubre la frontera de:

```text
diagnóstico inicial pre-core + primer informe pre-core
```

AAAS usa P1 como primer momento operativo de comprensión situada, pero no lo convierte en diagnóstico final.

El primer informe P1 no reemplaza al `OwnerFacingReport` post-core regulado por ADR-018.

## Relación con pronóstico

Pronóstico no significa predicción libre.

En AAAS, pronóstico significa:

```text
proyección prudente y condicional del riesgo operativo si la situación observada continúa y la evidencia disponible no cambia.
```

Estados de pronóstico sugeridos:

| Estado | Significado |
|---|---|
| `NO_PROGNOSIS` | No hay base suficiente |
| `LOW_CONFIDENCE` | Hay señales, pero faltan evidencias críticas |
| `CONDITIONAL_PROGNOSIS` | Puede formularse proyección condicionada |
| `EVIDENCE_BACKED_PROGNOSIS` | Hay evidencia suficiente y trazable |

Este documento no autoriza implementación de pronóstico. Sólo fija frontera.

## Relación con packs

AAAS no reemplaza el Pack System.

Los packs aportarán conocimiento enchufable futuro:

- `FormulaPack`,
- `PathologyPack`,
- `CatalogPack`,
- `DomainPack`,
- `SectorPack`,
- `KnowledgePack`.

AAAS consume conocimiento validado por el kernel. No carga conocimiento arbitrario ni permite que el agente modifique el kernel.

## Relación con decisión del dueño

El dueño puede:

- confirmar comprensión semántica,
- corregir interpretación,
- aportar evidencia,
- responder preguntas,
- autorizar una acción,
- rechazar una recomendación,
- pedir continuidad.

Pero estas respuestas no son equivalentes entre sí.

AAAS debe respetar ADR-025 y `owner-decision-v1`:

```text
confirmar entendimiento ≠ autorizar acción
responder pregunta ≠ aportar evidencia estructurada suficiente
aceptar resumen ≠ aprobar delivery o intervención
```

## Criterios fail-closed

AAAS debe bloquear cuando:

- falta evidencia material,
- falta identidad mínima del caso,
- el dueño no confirmó una interpretación crítica,
- hay contradicción entre relato y evidencia,
- el pronóstico sería especulativo,
- la acción sugerida requiere autorización explícita,
- el output podría sonar a diagnóstico final sin base suficiente.

## Prohibiciones de este documento

Este documento no autoriza:

- código,
- tests,
- runtime,
- Telegram,
- Hermes productivo,
- FastAPI,
- PDF productivo,
- delivery externo,
- nuevos endpoints,
- nuevos packs,
- migración de fórmulas,
- modificación de DiagnosticCoreV1,
- modificación de anamnesis FSM,
- modificación de owner-facing report,
- acciones automáticas sobre datos reales.

## Próximo frente autorizado por este documento

El próximo frente razonable no es implementación directa de AAAS.

El próximo frente documental-operativo debería ser:

```text
OWNER_CONVERSATION_TO_INITIAL_DIAGNOSIS_TASKSPEC.md
```

Alcance sugerido:

- mensaje inicial del dueño,
- captura mínima de caso,
- preguntas permitidas,
- evidencia requerida,
- bloqueo accionable,
- diagnóstico inicial candidato,
- relación con P1,
- relación con owner questions,
- prohibición de diagnóstico final.

## Veredicto

```text
AAAS_BOUNDARY_DEFINED_AS_CANDIDATE_OPERATIONAL_FRONT
```

AAAS queda definido como agente IA operativo sobre SaaS, subordinado al kernel, evidencia, contratos, P1, ADR-018, ADR-024, ADR-025 y owner-decision-v1.
