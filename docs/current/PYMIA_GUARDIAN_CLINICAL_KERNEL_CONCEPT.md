# PymIA Guardián — concepto de kernel clínico transversal

## Estado

**CONCEPTO ARQUITECTÓNICO CANDIDATO.**

Este documento preserva un hallazgo arquitectónico y de producto con evidencia técnica externa al repositorio PymIA y material conceptual aportado por el usuario. No autoriza implementación productiva, migración de código, nuevo runtime, nuevo conector ni modificación de la raíz canónica de Servicio 1.

Para avanzar desde concepto a arquitectura aceptada se requiere:

```text
ADR específico
→ contratos explícitos
→ acceptance tests
→ implementación focal
→ evidencia observada
→ promoción gobernada
```

## Propósito

Registrar que el motor clínico determinístico desarrollado en SmartSeller puede constituir una base reutilizable para un futuro **PymIA Guardián**, orientado a vigilancia temprana y continua de una PyME a partir de evidencia proveniente de múltiples dominios.

El segundo hallazgo amplía esta hipótesis: el mismo kernel podría alimentar una capa operativa gobernada capaz de responder, ejecutar o escalar situaciones autorizadas sin convertir al LLM en autoridad soberana.

La oportunidad no consiste en incorporar SmartSeller completo dentro de PymIA ni en duplicar su repositorio. Consiste en:

1. extraer el patrón clínico general;
2. separar adaptadores y reglas particulares de Mercado Libre;
3. conservar Mercado Libre como primer paquete vertical;
4. distinguir vigilancia de ejecución;
5. convertir excepciones resueltas en conocimiento candidato bajo aprobación;
6. ampliar autonomía únicamente después de pruebas y evidencia.

## Fuentes y nivel de confianza

### Evidencia técnica revisada

Repositorio externo:

```text
smartdash-almasana/smartsellerv2
commit de referencia observado: 76e02436cde7986d120cdfa7b1fa2a30a7cd218c
```

Archivos principales revisados:

- `docs/adr/ADR-0009-v3-canonical-rebuild-strategy.md`;
- `docs/adr/ADR-0011-v3-pipeline-ownership-and-writer-governance.md`;
- `src/v3/engine/domain-to-snapshot-worker.ts`;
- `src/v3/engine/metrics-writer.ts`;
- `src/v3/engine/signals-writer.ts`;
- `src/v3/engine/health-score-writer.ts`;
- `src/v3/ingest/domain-normalizer.ts`;
- `src/v3/adapters/ml/webhook-adapter.ts`;
- `src/v2/ingest/webhook-handler.ts`;
- `auditoria_repo_db_smartseller_v3.md`.

Esta evidencia permite certificar existencia y forma del diseño en SmartSeller. No certifica trasplante directo, compatibilidad física con PymIA ni estado runtime completo.

### Material conceptual adicional

Se revisó una transcripción extensa aportada por el usuario el 22 de julio de 2026 sobre automatización de Mercado Libre, preventa, postventa, publicación de productos, CRM, bases de conocimiento, simulaciones y operación asistida.

La transcripción sirve como fuente de:

- patrones de uso;
- dolores operativos;
- hipótesis de producto;
- ejemplos de workflows;
- riesgos y prácticas a revisar.

No constituye por sí sola evidencia independiente de:

- resultados económicos declarados;
- mejora de posicionamiento;
- reducción causal de devoluciones;
- exactitud de endpoints;
- comportamiento vigente de permisos, tokens o límites de API;
- seguridad o robustez de las implementaciones mostradas.

## Hallazgo técnico original

SmartSeller implementa un pipeline clínico con la forma:

```text
webhook_events
→ domain_events
→ snapshots
→ metrics
→ clinical_signals
→ health_score
```

El diseño documentado exige:

- un writer gobernado por etapa;
- identidad completa;
- idempotencia por claves determinísticas;
- reconstrucción desde evidencia persistida;
- separación entre adaptadores y núcleo clínico;
- score reproducible sin autoridad soberana de un LLM.

Estos principios son compatibles con los invariantes de PymIA:

```text
El dueño aporta evidencia y significado operativo.
La capa conversacional pregunta y explica.
PymIA gobierna estado, evidencia y computabilidad.
Las tools determinísticas calculan y ejecutan.
```

La compatibilidad es metodológica y arquitectónica. No demuestra todavía compatibilidad física de esquemas, contratos, dependencias o runtime.

## Hechos certificados desde SmartSeller

1. SmartSeller V3 fue diseñado con un núcleo explícitamente desacoplado de proveedores.
2. Los adaptadores de Mercado Libre están destinados a escribir eventos de entrada, no tablas clínicas downstream.
3. El pipeline conserva eventos, snapshots, métricas, señales y scores vinculados por identidad y ejecución.
4. Las señales actuales incluyen al menos:
   - ausencia de ventas;
   - aumento de cancelaciones;
   - preguntas sin responder;
   - reclamos activos;
   - riesgo de demora logística.
5. El score actual es determinístico y usa penalizaciones explícitas por señal y severidad.
6. El webhook productivo de SmartSeller realiza un dual-write temporal hacia V2 y V3.
7. El diseño conserva acoplamientos semánticos y físicos al concepto de `store` y a eventos de marketplace.
8. La implementación observada no constituye todavía un kernel PyME general.

## Hallazgo ampliado: Guardián y Operador

El material adicional permite distinguir dos funciones que no deben colapsarse.

### PymIA Guardián

```text
observa
→ verifica evidencia
→ calcula
→ detecta desvíos
→ produce señal
→ alerta
```

Responsabilidades candidatas:

- vigilancia continua o periódica;
- freshness y suficiencia de datos;
- métricas y reglas versionadas;
- señales clínicas;
- health state;
- alertas con evidencia;
- seguimiento y resolución.

### PymIA Operador

```text
recibe situación
→ consulta evidencia autorizada
→ evalúa política
→ responde, ejecuta, deriva o bloquea
→ registra resultado
```

Responsabilidades candidatas:

- responder interacciones repetitivas y autorizadas;
- preparar borradores;
- ejecutar acciones permitidas;
- clasificar casos;
- derivar excepciones;
- registrar decisiones y outcomes;
- abrir gaps de conocimiento.

### Relación propuesta

```text
PymIA Clinical Kernel
        │
        ├── Guardián
        │   observa, calcula, detecta y alerta
        │
        └── Operador
            actúa solo bajo políticas explícitas
```

El motor clínico gobierna evidencia, computabilidad, señales y estado. El Operador no puede inventar capacidad ni transformar confianza lingüística en autorización.

## Hallazgo ampliado: autonomía progresiva

La transcripción describe, de manera informal, un patrón con valor general:

```text
conocimiento inicial incompleto
→ situación real
→ respuesta posible o abstención
→ intervención humana cuando falta evidencia
→ resolución confirmada
→ conocimiento candidato
→ prueba
→ ampliación gradual de cobertura
```

Este patrón se alinea con PymIA si se preserva la siguiente cadena:

```text
excepción
→ NEEDS_EVIDENCE
→ resolución humana o fuente autorizada
→ candidato de conocimiento
→ aprobación
→ versión
→ acceptance tests
→ shadow mode
→ promoción
```

No está autorizado el aprendizaje automático directo desde cualquier respuesta humana o interacción histórica.

## Motor de abstención y decisión

Un sistema confiable no debe intentar responder siempre. El contrato conceptual mínimo debe admitir:

```text
AUTO_EXECUTE
DRAFT_FOR_REVIEW
ESCALATE
BLOCKED
NEEDS_EVIDENCE
```

### AUTO_EXECUTE

Solo cuando:

- la evidencia es suficiente y vigente;
- la política permite la acción;
- el sujeto y alcance están identificados;
- la respuesta o acción pasa validaciones;
- existe trazabilidad completa.

### DRAFT_FOR_REVIEW

Cuando la evidencia permite formular una propuesta, pero:

- el tema es sensible;
- la política exige aprobación;
- la confianza estructural no alcanza el umbral de ejecución;
- la acción tiene impacto relevante.

### ESCALATE

Cuando:

- existe una excepción legítima;
- se requiere criterio humano;
- hay conflicto entre fuentes;
- el caso no pertenece a una política automatizable.

### BLOCKED

Cuando:

- la acción está prohibida;
- faltan permisos;
- existe riesgo de incumplimiento;
- el sujeto o identidad no puede verificarse.

### NEEDS_EVIDENCE

Cuando:

- falta información del negocio;
- la fuente está vencida;
- no puede computarse una respuesta reproducible;
- el dueño debe confirmar significado operativo.

## Knowledge Loop gobernado

La oportunidad no es construir una FAQ creciente sin control. Es construir un ciclo de conocimiento con provenance.

### Fuentes candidatas

- descripción oficial;
- atributos de publicación;
- ficha técnica;
- manual;
- política comercial;
- stock confirmado;
- logística disponible;
- respuestas humanas aprobadas;
- preguntas históricas validadas;
- instrucciones confirmadas por el dueño;
- restricciones de plataforma.

### Jerarquía conceptual

```text
fuente oficial vigente
> política aprobada
> ficha técnica validada
> descripción publicada
> resolución humana confirmada
> interacción histórica validada
> texto generado sin aprobación
```

### Contrato candidato de conocimiento

```text
knowledge_id
source_type
source_reference
subject_scope
valid_from
valid_until
approved_by
approved_at
version
supersedes
provenance
```

Toda respuesta debe poder indicar qué fuentes utilizó. Una respuesta antigua no se vuelve verdad permanente por haber sido enviada alguna vez.

## Laboratorio de simulación

El material propone generar preguntas simuladas para probar respuestas antes de liberar automatización. El patrón es valioso si se formaliza:

```text
conocimiento versionado
→ casos simulados
→ decisión esperada
→ respuesta o acción esperada
→ evaluación
→ fallos
→ corrección
→ nueva ejecución
```

### Casos mínimos candidatos

- pregunta frecuente;
- pregunta ambigua;
- pregunta sobre otro producto;
- dato no disponible;
- fuente contradictoria;
- solicitud prohibida;
- solicitud de enlace o dato personal;
- consulta médica o sensible;
- pregunta sobre stock;
- pregunta sobre garantía;
- agradecimiento;
- spam;
- interacción ya respondida;
- pregunta que exige escalamiento.

### Evidencia requerida por simulación

- input completo;
- fuentes disponibles;
- versión de política;
- decisión esperada;
- decisión observada;
- respuesta esperada o invariantes;
- errores;
- resultado PASS/FAIL;
- provenance de la ejecución.

La generación de muchos ejemplos por un LLM no reemplaza casos de aceptación gobernados.

## CRM y lifecycle de casos

El contenido adicional sugiere que el valor comercial supera al chatbot y requiere una entidad operacional.

### Entidad conceptual

```text
interaction_case
```

Campos candidatos:

```text
case_id
tenant_id
subject_id
source_connection_id
external_case_id
case_type
priority
status
automation_decision
assigned_to
opened_at
last_activity_at
resolved_at
resolution_code
evidence_refs
```

### Tipos de caso candidatos

- preventa;
- postventa;
- garantía;
- devolución;
- envío;
- facturación;
- instalación;
- consulta técnica;
- reclamo;
- knowledge gap;
- caso no clasificado.

### Estados candidatos

```text
new
classified
auto_handled
needs_review
assigned
waiting_customer
waiting_business
resolved
discarded
```

Este lifecycle es compatible con los estados de PymIA Guardián:

```text
nueva
vista
asignada
en revisión
resuelta
descartada con motivo
```

## Interacciones como evidencia clínica

Las conversaciones y casos no solo deben resolverse. También pueden revelar patologías operativas.

Ejemplos conceptuales:

```text
preguntas recurrentes sobre medidas
→ información de producto insuficiente

consultas repetidas sobre compatibilidad
→ catálogo o atributos incompletos

consultas crecientes sobre entrega
→ comunicación logística deficiente

solicitudes reiteradas de factura
→ proceso de facturación poco claro

dudas frecuentes de instalación
→ onboarding postventa insuficiente
```

Señales candidatas:

```text
repeated_question_pattern
knowledge_gap_recurrence
product_description_insufficient
installation_confusion_spike
billing_request_backlog
post_sale_escalation_spike
refund_intent_spike
cross_product_question_rate
```

Estas señales no autorizan por sí mismas una explicación causal. Deben expresar el patrón observado, su ventana y evidencia.

## Modelo objetivo conceptual

```text
PymIA Clinical Kernel
├── identity and tenancy
├── evidence ledger
├── canonical events
├── snapshots
├── metrics
├── versioned rule engine
├── clinical signals
├── health states
├── alert candidates
├── action policies
├── automation decisions
├── interaction cases
├── knowledge candidates
├── simulation runs
├── replay
└── audit trail
```

Paquetes de dominio posibles:

```text
domain-packs/
├── mercadolibre
├── mercadopago
├── banking
├── sales
├── collections
├── inventory
├── accounting
├── taxes-arca
├── documents
└── operations
```

Cada paquete sería responsable de:

- recibir o conectar evidencia;
- conservar provenance;
- hidratar recursos cuando corresponda;
- normalizar hechos;
- aportar métricas y reglas específicas;
- declarar evidencia mínima;
- aportar políticas de acción;
- proveer fixtures y acceptance tests.

El kernel sería responsable de:

- identidad y aislamiento;
- ejecución gobernada;
- idempotencia;
- snapshots;
- evaluación determinística;
- señales y health state;
- candidatos de alerta;
- decisiones de automatización;
- replay y auditoría.

## Relación con SmartSeller

SmartSeller debe interpretarse como la primera implementación vertical conocida del patrón, no como el kernel general terminado.

```text
PymIA Clinical Kernel
        │
        ├── SmartSeller / Mercado Libre pack
        ├── PymIA Guardián PyME
        ├── PymIA Operador
        └── futuros paquetes operativos
```

SmartSeller podría mantenerse como vertical especializado:

```text
SmartSeller by PymIA
```

No se propone mantener motores clínicos divergentes. La hipótesis favorece un kernel compartido y paquetes especializados.

## Superficies comerciales candidatas

La transcripción permite distinguir cuatro superficies, todavía no productos autorizados:

### SmartSeller Guardián

- vigilancia;
- métricas;
- señales;
- alertas;
- estado de conexión y freshness.

### SmartSeller Operador

- respuesta autorizada;
- borradores;
- escalamiento;
- ejecución permitida;
- registro de outcomes.

### SmartSeller Control

- CRM preventa y postventa;
- casos;
- responsables;
- prioridad;
- resolución.

### SmartSeller Intelligence

- patrones recurrentes;
- knowledge gaps;
- calidad de fuentes;
- recomendaciones;
- simulaciones.

La promesa defendible no es “automatización total”. Es:

> Automatizar situaciones conocidas y autorizadas, derivar excepciones y mostrar dónde el negocio todavía necesita evidencia, conocimiento o intervención.

## Métricas de autonomía candidatas

La autonomía debe medirse, no declararse.

```text
interaction_count
auto_execute_count
draft_review_count
escalation_count
blocked_count
needs_evidence_count
human_override_count
resolution_time
automation_coverage_rate
verified_accuracy_rate
knowledge_gap_rate
```

La cobertura puede variar por:

- sujeto;
- tipo de caso;
- producto;
- canal;
- horario;
- versión de política;
- sensibilidad.

## Operación híbrida y horarios

El material sugiere un modelo híbrido donde humanos e IA operan según horario y tipo de caso.

Contrato conceptual:

```text
horario comercial
→ humano prioritario o copiloto

fuera de horario
→ automatización autorizada

caso sensible
→ humano obligatorio

caso repetitivo y validado
→ automatización permitida
```

La política debe ser explícita, versionada y auditable. El horario no convierte una acción prohibida en permitida.

## Reutilización candidata

### Alta reutilización conceptual

- writer único gobernado por etapa;
- idempotencia;
- event log append-only;
- snapshots reconstruibles;
- métricas;
- señales con evidencia;
- score determinístico;
- historial de runs;
- read models;
- separación entre adaptadores y núcleo.

### Requiere refactorización

- `store_id` como sujeto clínico universal;
- reglas y pesos hardcodeados;
- dependencia de webhooks como única evidencia;
- semántica centrada en marketplace;
- identidad ligada a una cuenta;
- ausencia de action policies;
- ausencia de abstención formal;
- falta de lifecycle de casos y alertas;
- falta de conocimiento versionado;
- falta de simulation gates.

### No copiar sin auditoría

- puentes V2/V3;
- dependencias Supabase específicas;
- migraciones no verificadas contra DB real;
- OAuth y tokens particulares de Mercado Libre;
- normalización sin hidratación confirmada;
- nombres físicos de tablas y rutas;
- workflows n8n mostrados en la transcripción;
- prompts, credenciales o prácticas de ensayo y error en producción.

## Generalización del sujeto clínico

`store_id` es válido para SmartSeller pero insuficiente para una PyME completa.

El kernel debería poder evaluar:

- empresa;
- sucursal;
- unidad de negocio;
- cuenta de Mercado Libre;
- cuenta bancaria;
- centro de costos;
- cliente;
- proveedor;
- período fiscal;
- proceso operativo.

Contrato conceptual candidato:

```text
tenant_id
subject_type
subject_id
source_key
observation_window
```

La identidad definitiva no queda autorizada por este documento.

## Separación entre señal, score, alerta, decisión y acción

```text
clinical_signal
├── contribución al health state
├── alert_candidate
│   → alerta operacional
└── automation_candidate
    → policy evaluation
    → automation_decision
    → action attempt
    → outcome
```

Definiciones:

- **señal:** desviación determinada por regla;
- **score o health state:** agregación resumida;
- **alerta:** objeto operacional con lifecycle;
- **decisión de automatización:** evaluación de permiso y suficiencia;
- **acción:** ejecución concreta;
- **outcome:** resultado observado.

No deben colapsarse en una sola entidad.

## Ejemplo transversal de valor

Una cuenta de Mercado Libre puede mostrar crecimiento de ventas mientras la PyME presenta:

```text
ventas creciendo
+
cobranzas demoradas
+
stock disminuyendo
+
caja insuficiente
+
pagos próximos
```

Formulación permitida:

> La actividad comercial aumentó, mientras que la disponibilidad financiera y el inventario no acompañaron el mismo ritmo durante la ventana observada.

Formulación no permitida sin evidencia causal:

> El crecimiento de Mercado Libre está causando la crisis de caja.

## Riesgos y prácticas descartadas

El contenido fuente incluye recomendaciones o afirmaciones que no deben transformarse en arquitectura sin validación.

### Permisos amplios por comodidad

No se autoriza “marcar todos los permisos”. Debe aplicarse mínimo privilegio.

### Refresh de token distribuido

No se autoriza renovar credenciales desde cada workflow. La gestión debe ser centralizada, segura, auditable y resistente a concurrencia.

### Responder siempre

La prioridad es:

```text
respuesta correcta y autorizada
> respuesta rápida
> respuesta automática
```

### Posicionamiento como causalidad

No debe afirmarse que responder más rápido mejora necesariamente el ranking sin evidencia oficial y medición controlada.

### Marketing externo para evitar comisiones

No forma parte del alcance autorizado.

### Automatización de reembolsos, reclamos o casos sensibles

Requiere contratos específicos, políticas, pruebas y autorización explícita. El default conceptual es revisión humana.

### Consultas médicas

En productos sanitarios u ortopédicos, el sistema solo puede utilizar información autorizada del producto. No emite diagnóstico ni orientación clínica.

### Promesas de perfección

No son contratos válidos:

- “responde mejor que un humano”;
- “no se rompe”;
- “canal cien por ciento automático”;
- “sistema perfecto”.

### Ensayo y error contra producción

La publicación o modificación debe seguir:

```text
schema
→ validación local
→ fixtures
→ dry run
→ revisión
→ ejecución controlada
```

## Relación con Servicio 1

Este concepto no sustituye, modifica ni expande automáticamente Servicio 1.

Servicio 1 conserva su raíz productiva única:

```text
archivo real
→ lectura estructural
→ confirmación semántica
→ análisis determinístico
→ entrega
```

PymIA Guardián y PymIA Operador serían capacidades futuras diferentes. Toda reutilización debe ocurrir mediante contratos explícitos y sin abrir:

- segundo parser XLSX;
- cadena semántica paralela;
- autoridad alternativa de diagnóstico;
- LLM soberano;
- ruta productiva no indexada.

## Invariantes propuestos

1. El LLM comunica y propone; no determina señales, score, alertas ni permisos.
2. Toda señal referencia evidencia persistida.
3. Toda regla y política está versionada.
4. Toda ejecución es reproducible dentro de su contrato y ventana.
5. Toda fuente declara freshness, alcance y calidad mínima.
6. Falta de evidencia produce `GAP`, `BLOCKED` o `NEEDS_EVIDENCE`.
7. Los adaptadores no escriben señales, scores, alertas ni acciones downstream.
8. Una alerta no afirma causalidad cuando solo se observó correlación o desvío.
9. Mercado Libre es un paquete de dominio, no la definición del kernel.
10. Toda acción conserva decisión, política, evidencia, intento y outcome.
11. Ninguna interacción se convierte automáticamente en conocimiento aprobado.
12. La autonomía se promueve por cobertura probada, no por confianza declarada.
13. Los casos sensibles escalan por default.
14. El mínimo privilegio es obligatorio.
15. Hermes no forma parte de esta arquitectura.

## No objetivos

Este documento no autoriza:

- copiar código desde SmartSeller;
- agregar SmartSeller como dependencia;
- crear tablas;
- crear workers, endpoints, cron o webhooks;
- conectar Mercado Libre a PymIA;
- cambiar la FSM de Servicio 1;
- modificar catálogos de patologías;
- publicar Guardián u Operador como productos disponibles;
- declarar equivalencia técnica entre repositorios;
- iniciar migración de datos;
- activar respuesta automática;
- crear un sistema de aprendizaje automático autónomo;
- sustituir la arquitectura actual de PymIA.

## Gaps abiertos

1. No existe contrato aprobado de `EvidenceRecord`.
2. No existe `CanonicalEvent` común a múltiples dominios.
3. No existe modelo aprobado de `ClinicalSubject`.
4. No existe catálogo versionado de reglas transversales.
5. No existe entidad de alerta con lifecycle.
6. No existe contrato de `ActionPolicy`.
7. No existe contrato de `AutomationDecision`.
8. No existe `InteractionCase` canónico.
9. No existe knowledge store versionado y gobernado.
10. No existe simulation gate.
11. No se auditó compatibilidad entre SmartSeller y PymIA.
12. No se definió ubicación física del kernel.
13. No existe estrategia de extracción incremental.
14. No existen acceptance tests cross-domain.
15. No se verificó el runtime completo de SmartSeller.
16. No se definió el modelo comercial final.

## Próximo paso metodológico

Antes de implementar código:

1. realizar auditoría de extracción cross-repo;
2. clasificar componentes SmartSeller como `reusable`, `adaptable`, `provider-specific` o `legacy`;
3. proponer contratos mínimos para:
   - `EvidenceRecord`;
   - `CanonicalEvent`;
   - `ClinicalSubject`;
   - `MetricSet`;
   - `RuleDefinition`;
   - `ClinicalSignal`;
   - `HealthState`;
   - `AlertCandidate`;
   - `ActionPolicy`;
   - `AutomationDecision`;
   - `ActionAttempt`;
   - `InteractionCase`;
   - `KnowledgeCandidate`;
   - `HumanResolution`;
   - `SimulationCase`;
   - `SimulationRun`;
4. redactar ADR `GO / NO-GO`;
5. definir acceptance tests antes de extraer código;
6. validar primero en shadow mode;
7. promover una sola acción de bajo riesgo como slice inicial;
8. mantener Servicio 1 sin cambios durante la validación.

## Slice de validación candidato

Sin autorizar implementación, el slice inicial más seguro sería:

```text
observar preguntas preventa
→ hidratar recurso oficial
→ reunir evidencia autorizada
→ producir decisión en shadow mode
→ no responder externamente
→ comparar con resolución humana
→ medir cobertura, abstención y errores
```

Este slice permite validar:

- identidad;
- ingestión;
- evidencia;
- conocimiento;
- abstención;
- políticas;
- simulaciones;
- métricas de cobertura;
- trazabilidad;

sin ejecutar acciones en Mercado Libre.

## Condiciones de stop

Detener si:

- se intenta copiar SmartSeller sin contrato;
- el kernel conserva semántica exclusiva de Mercado Libre;
- se abre una segunda raíz productiva de Servicio 1;
- una regla no puede reproducirse;
- el LLM se vuelve evaluador soberano;
- no existe aislamiento multi-tenant;
- faltan pruebas de idempotencia o replay;
- el score no puede reconstruirse;
- la alerta no conserva evidencia y versión;
- la acción no conserva política y outcome;
- una respuesta histórica se promueve sin aprobación;
- se ejecutan acciones antes de shadow mode;
- se solicitan permisos innecesarios;
- la arquitectura requiere Hermes.

## Dictamen conceptual

La evidencia técnica sostiene:

> SmartSeller contiene un patrón de motor clínico determinístico candidato a extracción y generalización como kernel transversal de PymIA Guardián.

El material conceptual adicional sostiene como hipótesis:

> El mismo kernel puede gobernar una capa Operador que automatice situaciones conocidas, derive excepciones y transforme resoluciones aprobadas en conocimiento candidato.

La evidencia no sostiene todavía:

> El motor puede copiarse directamente, aprender sin gobierno y operar Mercado Libre o una PyME en producción de forma autónoma.

La dirección recomendada es:

```text
extraer contratos y patrones
→ generalizar identidad, reglas y políticas
→ conservar Mercado Libre como paquete vertical
→ separar Guardián de Operador
→ validar abstención y conocimiento en shadow mode
→ promover autonomía solo con evidencia
```
