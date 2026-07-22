# PymIA Guardián — concepto de kernel clínico transversal

## Estado

**CONCEPTO ARQUITECTÓNICO CANDIDATO.**

Este documento registra un hallazgo con evidencia técnica externa al repositorio PymIA y fija sus límites de interpretación. No autoriza implementación productiva, migración de código, nuevo runtime, nuevo conector ni modificación de la raíz canónica de Servicio 1.

Para avanzar desde concepto a arquitectura aceptada se requiere un ADR específico, contratos explícitos, pruebas de aceptación y evidencia observada.

## Propósito

Registrar que el motor clínico determinístico desarrollado en SmartSeller puede constituir una base reutilizable para un futuro **PymIA Guardián**, orientado a vigilancia temprana y continua de una PyME a partir de evidencia proveniente de múltiples dominios.

La oportunidad no consiste en incorporar SmartSeller completo dentro de PymIA ni en duplicar su repositorio. Consiste en extraer el patrón clínico general, separar los adaptadores particulares de Mercado Libre y convertir Mercado Libre en el primer paquete vertical conectado a un kernel común.

## Hallazgo central

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
- reconstrucción del estado desde evidencia persistida;
- separación entre adaptadores de proveedor y núcleo clínico;
- score reproducible sin autoridad soberana de un LLM.

Estos principios son compatibles con los invariantes de PymIA:

```text
El dueño aporta evidencia y significado operativo.
La capa conversacional pregunta y explica.
PymIA gobierna estado, evidencia y computabilidad.
Las tools determinísticas calculan.
```

La compatibilidad es metodológica y arquitectónica. No demuestra todavía compatibilidad física de esquemas, contratos, dependencias o runtime.

## Fuentes de evidencia

Repositorio externo revisado:

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

La evidencia permite certificar existencia y forma del diseño en SmartSeller. No certifica que ese pipeline esté listo para trasplante directo ni que todas sus etapas estén operativas en la infraestructura de PymIA.

## Hechos certificados

1. SmartSeller V3 fue diseñado con un núcleo explícitamente desacoplado de proveedores.
2. Los adaptadores de Mercado Libre están destinados a escribir solamente eventos de entrada y no tablas clínicas downstream.
3. El pipeline conserva eventos, snapshots, métricas, señales y scores vinculados por identidad y ejecución.
4. Las señales actuales incluyen al menos:
   - ausencia de ventas;
   - aumento de cancelaciones;
   - preguntas sin responder;
   - reclamos activos;
   - riesgo de demora logística.
5. El score actual es determinístico y se calcula mediante penalizaciones explícitas por señal y severidad.
6. El webhook productivo de SmartSeller realiza un dual-write temporal hacia V2 y V3.
7. El diseño de SmartSeller contiene una base reusable, pero todavía conserva acoplamientos semánticos y físicos al concepto de `store` y a eventos de marketplace.

## Hipótesis arquitectónica

PymIA puede evolucionar hacia un kernel clínico transversal con esta forma:

```text
evidencia confirmada
→ evento canónico
→ snapshot operativo
→ métricas gobernadas
→ reglas versionadas
→ señales clínicas
→ estado de salud
→ candidatos de alerta
```

Nombre conceptual:

```text
PymIA Clinical Kernel
```

Superficie de producto futura que podría utilizarlo:

```text
PymIA Guardián
```

El kernel no sería un producto comercial por sí solo. Sería infraestructura determinística común para productos, módulos y paquetes de dominio.

## Modelo objetivo conceptual

```text
PymIA Clinical Kernel
├── evidence ledger
├── canonical events
├── snapshots
├── metrics
├── versioned rule engine
├── clinical signals
├── health states
├── alert candidates
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

- conectar o recibir evidencia;
- conservar provenance;
- hidratar recursos cuando corresponda;
- normalizar hechos en eventos canónicos;
- aportar métricas específicas;
- aportar reglas versionadas;
- declarar evidencia mínima y guardas de suficiencia;
- proveer fixtures y pruebas de aceptación.

El kernel sería responsable de:

- identidad y aislamiento;
- ejecución gobernada;
- idempotencia;
- snapshots;
- evaluación determinística;
- señales;
- score o estado de salud;
- candidatos de alerta;
- reconstrucción y auditoría.

## Relación con SmartSeller

SmartSeller debe interpretarse como la primera implementación vertical conocida de este patrón, no como el kernel general terminado.

Relación propuesta:

```text
PymIA Clinical Kernel
        │
        ├── SmartSeller / Mercado Libre pack
        ├── PymIA Guardián PyME
        └── futuros paquetes operativos
```

SmartSeller podría mantenerse comercialmente como vertical especializado:

```text
SmartSeller by PymIA
```

Mientras que PymIA Guardián combinaría evidencia de varios dominios de una misma PyME.

No se propone que ambos mantengan motores clínicos divergentes. La hipótesis favorece un kernel compartido y paquetes especializados.

## Reutilización candidata

### Componentes con alta reutilización conceptual

- writer único gobernado por etapa;
- idempotencia;
- event log append-only;
- snapshots reconstruibles;
- materialización de métricas;
- señales con evidencia;
- agregación determinística de salud;
- historial de runs;
- read models derivados;
- separación entre adaptadores y núcleo.

### Componentes que requieren refactorización

- `store_id` como sujeto clínico universal;
- reglas hardcodeadas en TypeScript;
- pesos de score embebidos en código;
- dependencia de webhooks como única forma de evidencia;
- semántica centrada en órdenes, preguntas, reclamos y envíos;
- identidad ligada a una cuenta marketplace;
- falta de separación formal entre señal y alerta operativa;
- falta de lifecycle de asignación, seguimiento y resolución.

### Componentes que no deben copiarse sin auditoría

- puentes temporales V2/V3;
- dependencias internas de Supabase específicas de SmartSeller;
- migraciones no verificadas contra la DB real;
- contratos de OAuth y token particulares de Mercado Libre;
- normalización basada solo en payload de webhook sin hidratación confirmada;
- nombres de tablas y rutas físicas del repositorio externo.

## Generalización del sujeto clínico

El concepto `store_id` es válido para SmartSeller pero insuficiente para una PyME completa.

El kernel general debería poder evaluar sujetos como:

- empresa completa;
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

## Separación entre señal, score y alerta

SmartSeller materializa principalmente:

```text
signal
→ health_score
```

PymIA Guardián necesita una separación adicional:

```text
clinical_signal
├── contribución al estado de salud
└── alert_candidate
    → alerta emitida
    → destinatario
    → canal
    → acuse
    → asignación
    → revisión
    → resolución
```

Una señal es una desviación determinada por una regla.

Un score es una agregación resumida.

Una alerta es un objeto operacional con lifecycle.

Estos tres conceptos no deben colapsarse en una sola entidad.

## Ejemplo transversal de valor

Una cuenta de Mercado Libre aislada puede mostrar crecimiento de ventas. Una PyME completa puede, al mismo tiempo, presentar:

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

El valor diferencial de PymIA Guardián aparece cuando el kernel combina evidencia gobernada de varios dominios y produce señales compuestas sin inventar causalidad.

Ejemplo de formulación permitida:

> La actividad comercial aumentó, mientras que la disponibilidad financiera y el inventario no acompañaron el mismo ritmo durante la ventana observada.

Ejemplo no permitido sin evidencia causal:

> El crecimiento de Mercado Libre está causando la crisis de caja.

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

PymIA Guardián sería una capacidad futura diferente, orientada a vigilancia continua o periódica.

Toda reutilización de componentes de Servicio 1 deberá ocurrir mediante contratos explícitos y sin abrir:

- un segundo parser XLSX;
- una cadena semántica paralela;
- una autoridad alternativa de diagnóstico;
- un LLM soberano;
- una ruta productiva no indexada.

## Invariantes propuestos

1. El LLM comunica; no determina señales, score ni alertas.
2. Toda señal debe referenciar evidencia persistida.
3. Toda regla debe estar versionada.
4. Toda ejecución debe ser reproducible dentro de su contrato y ventana.
5. Toda fuente debe declarar freshness y calidad mínima.
6. Falta de evidencia debe producir `GAP`, `BLOCKED` o `NEEDS_EVIDENCE`, no una inferencia silenciosa.
7. Los adaptadores no escriben directamente señales, scores ni alertas.
8. Una alerta no afirma causalidad cuando solo se comprobó correlación o desvío.
9. Mercado Libre es un paquete de dominio, no la definición del kernel.
10. Hermes no forma parte de esta arquitectura.

## No objetivos de este documento

Este documento no autoriza:

- copiar código desde SmartSeller;
- agregar SmartSeller como dependencia;
- crear tablas nuevas;
- crear workers, endpoints, cron o webhooks;
- conectar Mercado Libre a PymIA;
- cambiar la FSM de Servicio 1;
- modificar catálogos de patologías;
- publicar PymIA Guardián como producto disponible;
- declarar equivalencia técnica entre ambos repositorios;
- iniciar una migración de datos;
- sustituir la arquitectura actual de PymIA.

## Gaps abiertos

1. No existe todavía un contrato canónico de `CanonicalEvent` común a múltiples dominios.
2. No existe un modelo aprobado de sujeto clínico general.
3. No existe un catálogo versionado de reglas transversales.
4. No existe una entidad de alerta con lifecycle.
5. No se auditó compatibilidad entre persistencia SmartSeller y PymIA.
6. No se definió si el kernel debe residir físicamente dentro de PymIA o como paquete independiente.
7. No existe estrategia de extracción incremental ni compatibilidad de versiones.
8. No existen acceptance tests cross-domain.
9. No se verificó el estado runtime completo de SmartSeller contra infraestructura productiva.
10. No se definió el modelo comercial final de SmartSeller respecto de PymIA.

## Próximo paso metodológico

Antes de implementar código:

1. realizar una auditoría de extracción cross-repo;
2. inventariar componentes SmartSeller en categorías `reusable`, `adaptable`, `provider-specific` y `legacy`;
3. proponer contratos mínimos para:
   - `EvidenceRecord`;
   - `CanonicalEvent`;
   - `ClinicalSubject`;
   - `MetricSet`;
   - `RuleDefinition`;
   - `ClinicalSignal`;
   - `HealthState`;
   - `AlertCandidate`;
4. redactar un ADR de decisión `GO / NO-GO`;
5. definir acceptance tests antes de extraer código;
6. comenzar, si se autoriza, mediante feature flag y shadow mode;
7. mantener Servicio 1 sin cambios durante la validación del kernel.

## Condiciones de stop

Detener la implementación si:

- se intenta copiar SmartSeller sin contrato de extracción;
- el kernel conserva semántica exclusiva de Mercado Libre;
- se abre una segunda raíz productiva de Servicio 1;
- una regla no puede reproducirse desde evidencia persistida;
- se pretende usar un LLM como evaluador soberano;
- no existe aislamiento multi-tenant verificable;
- no existen pruebas de idempotencia y replay;
- el score no puede reconstruirse;
- la alerta no conserva evidencia y versión de regla;
- la arquitectura requiere Hermes.

## Dictamen conceptual

El hallazgo es técnicamente relevante y merece preservarse.

La evidencia observada sostiene esta conclusión acotada:

> SmartSeller contiene un patrón de motor clínico determinístico que puede ser candidato a extracción y generalización como kernel transversal de PymIA Guardián.

La evidencia no sostiene todavía esta afirmación más fuerte:

> El motor puede copiarse directamente y utilizarse en producción dentro de PymIA.

La dirección recomendada es:

```text
extraer contratos y patrones
→ generalizar identidad y reglas
→ conservar Mercado Libre como paquete vertical
→ validar en shadow mode
→ promover solo con evidencia
```
