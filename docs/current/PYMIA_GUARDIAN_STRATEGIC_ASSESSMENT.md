# PymIA Guardián — evaluación estratégica de los hallazgos

## Estado

**EVALUACIÓN ESTRATÉGICA CANDIDATA.**

Este documento interpreta y prioriza los hallazgos preservados en `PYMIA_GUARDIAN_CLINICAL_KERNEL_CONCEPT.md`.

No autoriza implementación, extracción de código, conexión con Mercado Libre, creación de runtime, modificación de Servicio 1 ni publicación comercial de nuevas capacidades.

Su función es fijar:

- qué hallazgos tienen mayor valor;
- qué diferenciación técnica y comercial aparece;
- qué riesgos deben evitarse;
- qué secuencia de validación resulta metodológicamente defendible.

En caso de conflicto, gobiernan el código, los tests, `AGENTS.md`, `ARCHITECTURE_GUARDRAILS.md` y el documento conceptual citado.

## Fuentes

Esta evaluación se apoya en:

1. `PYMIA_GUARDIAN_CLINICAL_KERNEL_CONCEPT.md`;
2. evidencia técnica revisada en `smartdash-almasana/smartsellerv2`;
3. transcripción aportada por el usuario el 22 de julio de 2026 sobre automatización de Mercado Libre;
4. invariantes vigentes de PymIA sobre evidencia, computabilidad, autoridad determinística y rol no soberano del LLM.

La transcripción aporta patrones, dolores, oportunidades y riesgos. No certifica resultados económicos, causalidad comercial, exactitud técnica vigente ni robustez de las implementaciones mostradas.

## Dictamen general

La valoración estratégica es **positiva y de alta relevancia**.

Los hallazgos ya no describen solamente:

```text
un conector de Mercado Libre
+
un score
+
un bot de preguntas
```

Describen una arquitectura potencialmente más profunda:

```text
kernel clínico determinístico
+
Guardián
+
Operador gobernado
+
gestión de casos
+
aprendizaje controlado por excepciones
```

La oportunidad principal no es automatizar Mercado Libre de forma aislada. Es construir una capacidad transversal que pueda:

- observar evidencia;
- determinar computabilidad;
- detectar desvíos;
- decidir si una acción está permitida;
- ejecutar, preparar o escalar;
- registrar outcomes;
- transformar resoluciones aprobadas en conocimiento candidato;
- ampliar autonomía únicamente después de pruebas.

## Hallazgo estratégico principal: autonomía progresiva

El hallazgo más valioso es este ciclo:

```text
automatizar lo conocido
→ abstenerse ante lo incierto
→ pedir intervención
→ registrar la resolución
→ proponer conocimiento candidato
→ aprobar y versionar
→ probar
→ ampliar cobertura
```

Este patrón es superior a un chatbot convencional porque el sistema puede distinguir:

- qué sabe;
- de dónde lo sabe;
- qué puede ejecutar;
- qué requiere revisión;
- qué debe bloquear;
- qué evidencia falta;
- qué aprendió bajo aprobación.

El patrón es extensible fuera de Mercado Libre a:

- documentos faltantes;
- conciliaciones dudosas;
- clasificación de movimientos;
- consultas contables;
- vencimientos ambiguos;
- inventario;
- cobranzas;
- procesos administrativos.

## Separación estratégica: Guardián y Operador

La separación entre ambas funciones es correcta y debe preservarse.

### Guardián

```text
observa
→ calcula
→ detecta
→ explica
→ alerta
```

### Operador

```text
recibe caso
→ consulta evidencia
→ evalúa política
→ ejecuta, propone, deriva o bloquea
→ registra outcome
```

Regla estratégica:

```text
detectar un problema
≠
autorizar una acción
≠
ejecutarla
```

Esta separación reduce riesgo, protege el kernel clínico y permite evolucionar la autonomía por capas.

## El kernel clínico como activo de plataforma

El diseño observado en SmartSeller contiene principios reutilizables:

- event log;
- snapshots;
- métricas;
- señales;
- score reproducible;
- identidad;
- idempotencia;
- writers gobernados;
- replay;
- auditoría.

La evaluación sostiene que estos principios pueden convertirse en infraestructura común para:

```text
Mercado Libre
bancos
ventas
cobranzas
inventario
documentos
contabilidad
impuestos
operaciones
```

El valor no reside en que todos los dominios compartan las mismas reglas. Reside en que compartan el mismo marco de:

```text
evidencia
→ computabilidad
→ evaluación
→ señal
→ decisión
→ acción autorizada
→ outcome
```

## Activo comercial más inmediato: bandeja operacional de casos

La superficie comercial más tangible no es un score aislado ni un agente conversacional.

Es una bandeja donde el negocio pueda ver:

- qué requiere atención;
- qué resolvió el sistema;
- qué necesita aprobación;
- qué fue escalado;
- quién es responsable;
- qué está esperando al cliente;
- qué quedó resuelto;
- qué patrón se repite.

Entidad conceptual central:

```text
interaction_case
```

Esta superficie puede agrupar:

- preventa;
- postventa;
- envíos;
- facturación;
- garantía;
- instalación;
- consultas técnicas;
- reclamos;
- knowledge gaps.

La evaluación considera que este CRM de casos tiene más valor comercial inmediato que un dashboard general de salud sin workflow de resolución.

## Ventaja competitiva candidata: laboratorio de simulación

La simulación previa a la automatización puede convertirse en un diferenciador si se formaliza como prueba y no como demostración informal.

```text
caso
→ evidencia disponible
→ política aplicable
→ decisión esperada
→ respuesta o acción esperada
→ resultado observado
→ PASS / FAIL
```

Ventaja potencial:

> SmartSeller no solo genera respuestas: prueba cuándo debe responder, abstenerse, escalar o bloquear antes de operar externamente.

La cantidad de ejemplos generados por un LLM no equivale a cobertura probada. Se requieren casos de aceptación con invariantes y evidencia.

## Interacciones como evidencia clínica

Las conversaciones no son solamente trabajo pendiente. Pueden revelar fallas estructurales.

Ejemplos:

```text
preguntas repetidas sobre medidas
→ información de producto insuficiente

consultas sobre compatibilidad
→ catálogo incompleto o confuso

consultas sobre entrega
→ comunicación logística deficiente

dudas de instalación
→ onboarding postventa insuficiente

solicitudes reiteradas de factura
→ proceso administrativo poco claro
```

Esta relación conecta SmartSeller con PymIA:

```text
interacción
→ patrón
→ métrica
→ señal clínica
→ revisión o recomendación
```

Las señales deben describir patrones observados y no afirmar causalidad sin evidencia.

## Posicionamiento comercial defendible

No se recomienda posicionar SmartSeller como:

- bot que responde todo;
- canal cien por ciento automático;
- reemplazo total del equipo;
- sistema perfecto;
- garantía de ventas o posicionamiento.

Posicionamiento candidato:

> Sistema de vigilancia, operación y mejora progresiva para vendedores de Mercado Libre.

Diferencia conceptual:

```text
bot genérico
→ intenta responder

SmartSeller
→ verifica evidencia
→ evalúa política
→ responde, propone, escala o bloquea
→ registra outcome
→ detecta patrones
→ mejora bajo control
```

## Relación comercial entre SmartSeller y PymIA

La estructura estratégica recomendada es:

```text
PymIA Clinical Kernel
        │
        ├── SmartSeller by PymIA
        │   vertical Mercado Libre
        │
        ├── PymIA Guardián
        │   vigilancia PyME transversal
        │
        └── PymIA Operador
            ejecución gobernada
```

SmartSeller puede seguir siendo una oferta vertical, comprensible y vendible, sin mantener un motor clínico divergente.

PymIA Guardián puede combinar evidencia de múltiples dominios y obtener una visión operacional más amplia.

## Frontera del LLM

La evaluación reafirma:

```text
PymIA determina:
- estado;
- evidencia suficiente;
- política;
- permiso;
- bloqueo;
- escalamiento.

El LLM puede:
- interpretar lenguaje;
- recuperar contenido autorizado;
- redactar;
- clasificar dentro de contrato;
- explicar.
```

La fluidez de una respuesta no constituye evidencia, autorización ni computabilidad.

## Riesgo principal: expansión descontrolada

Los hallazgos abren numerosos frentes:

- kernel;
- conectores;
- Mercado Libre;
- Mercado Pago;
- CRM;
- conocimiento;
- simulaciones;
- catálogo;
- postventa;
- alertas;
- recomendaciones;
- inventario;
- PymIA Guardián;
- PymIA Operador.

Intentar construirlos simultáneamente degradaría la arquitectura, la verificabilidad y la capacidad de cierre.

Regla estratégica:

> Arquitectura amplia, implementación inicial estrecha.

## Secuencia recomendada

La prioridad no es comenzar por el agente de IA ni por el dashboard completo.

Secuencia candidata:

```text
1. recibir preguntas reales;
2. hidratar el recurso oficial;
3. persistir evidencia e identidad;
4. reunir fuentes autorizadas;
5. producir AUTO / DRAFT / ESCALATE / BLOCKED / NEEDS_EVIDENCE;
6. operar únicamente en shadow mode;
7. comparar con resolución humana;
8. registrar knowledge gaps;
9. aprobar y versionar conocimiento;
10. ejecutar simulaciones;
11. habilitar una única acción de bajo riesgo;
12. ampliar cobertura con evidencia.
```

## Slice inicial recomendado

Primer slice conceptual:

```text
pregunta preventa real
→ evento persistido
→ hidratación oficial
→ conocimiento autorizado
→ decisión en shadow mode
→ comparación humana
→ métrica de cobertura y error
```

No responde externamente.

Debe demostrar:

- identidad correcta;
- trazabilidad;
- hidratación;
- abstención;
- política;
- suficiencia de evidencia;
- reproducibilidad;
- capacidad de detectar gaps;
- comparación contra resolución real.

## Métricas prioritarias

Antes de medir impacto comercial, se debe medir calidad operacional:

```text
automation_coverage_rate
verified_accuracy_rate
abstention_correctness
escalation_precision
human_override_rate
knowledge_gap_rate
policy_violation_count
resolution_time
replay_consistency
```

Las ventas, conversiones, ranking o devoluciones pueden estudiarse después, con diseños que distingan correlación de causalidad.

## Hallazgos que no deben convertirse en hechos

No se consideran demostrados:

- que responder rápido mejore necesariamente el ranking;
- que la IA responda mejor que una persona;
- que el sistema incremente ventas por sí mismo;
- que un canal quede completamente autónomo;
- que los workflows mostrados sean robustos;
- que todos los endpoints o políticas descritos sigan vigentes;
- que las cifras comerciales declaradas prueben causalidad.

## Prioridades estratégicas

Orden recomendado:

1. **kernel y contratos**;
2. **abstención y políticas**;
3. **ledger de casos e interacciones**;
4. **shadow mode y comparación humana**;
5. **knowledge loop gobernado**;
6. **simulation gate**;
7. **una acción externa de bajo riesgo**;
8. **CRM operacional**;
9. **señales clínicas sobre interacciones**;
10. **expansión a otros dominios PyME**.

## Condiciones de stop

Detener si:

- se intenta construir varias superficies simultáneamente;
- se prioriza interfaz sobre contratos;
- el LLM decide autorización;
- una interacción se vuelve conocimiento sin aprobación;
- se ejecuta antes de shadow mode;
- no puede reconstruirse la decisión;
- no se distingue señal, alerta, decisión y acción;
- se afirma causalidad comercial sin evidencia;
- SmartSeller y PymIA crean motores divergentes;
- se altera Servicio 1 para acomodar este concepto;
- la arquitectura incorpora Hermes.

## Conclusión estratégica

Los tres activos de mayor valor son:

1. **kernel clínico transversal**;
2. **separación Guardián–Operador**;
3. **aprendizaje gobernado por excepciones**.

El activo comercial más inmediato es:

> Una bandeja operacional de Mercado Libre donde SmartSeller resuelve lo seguro, prepara lo dudoso, deriva lo sensible y muestra qué debe mejorar el negocio.

La cautela central es:

> No convertir el descubrimiento en veinte frentes de implementación. Primero debe demostrarse el ciclo completo sobre una única interacción de bajo riesgo, en shadow mode y con evidencia.

Dictamen final:

```text
hallazgo valioso
→ dirección estratégica favorable
→ implementación todavía no autorizada
→ validación focal obligatoria
```
