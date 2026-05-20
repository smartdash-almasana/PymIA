Contexto heredado. No autoriza runtime, MCP, jobs, workflows ni orquestación dentro de PymIA. Rige `../ARCHITECTURE_GUARDRAILS.md`.

# PymIA — Biblioteca Documental Canónica

## Estado

Documento rector — Índice canónico v1.4
Fecha: Mayo 2026

---

## Principio rector

```text
La IA interpreta.
Pydantic valida.
El kernel determinístico decide.
El dueño confirma.
```

---

## Estructura vigente — archivos presentes

Las referencias de esta sección usan rutas relativas reales desde `PymIA/docs/`.

### Raíz documental

- `README.md`
- `DOCTRINA_ROBUSTEZ_INCREMENTAL_Y_MIGRACION_MVP.md` — doctrina vigente sobre robustez incremental y plan de transición de lenguaje/campos legado
- `INVENTARIO_CANONICO.md`
- `ingenieria_conversacional.README.md` — índice lógico de corpus conversacional migrado
- `ingenieria_conversacional.corpus_migrado.md` — corpus bruto SmartPyme → PymIA, sin depuración fina
- `ingenieria_conversacional.NORMATIVA_v1.md` — reglas canónicas iniciales para conversación
- `ingenieria_conversacional.PROTOCOLO_PRIMER_CONTACTO_v1.md` — protocolo de recepción/anamnesis inicial
- `ingenieria_conversacional.CATALOGO_HIPOTESIS_Y_EVIDENCIA_v1.md` — hipótesis investigativas, evidencia y preguntas
- `ingenieria_conversacional.CATALOGO_FORMULAS_MATEMATICAS_PYME_v1.md` — catálogo inicial de fórmulas para capa matematizadora
- `ingenieria_conversacional.ENSAMBLE_DOCUMENTAL_FASE1_v1.md` — ensamble del staging migrado con normativa viva
- `formula_catalog.v1.json` — catálogo inicial de fórmulas correlacionado con patologías
- `pathology_catalog.v1.json` — catálogo JSON inicial de patologías PyME
- `ingenieria_conversacional.MAPA_INTEGRACION_v1.md` — jerarquía provisional y mapa de solapamientos

### `vision/`

- `vision/SMARTPYME_LABORATORIO_PYME_Y_ESTABILIZACION_OPERACIONAL.md` — placeholder con provenance explícito
- `vision/SMARTPYME_MVP_REALISTA_Y_FILOSOFIA_OPERACIONAL.md` — placeholder con provenance explícito

### `fundamentos/`

- `fundamentos/cosmovision-clinico-operacional.md`
- `fundamentos/organismo-pyme.md`
- `fundamentos/metodo-hipotetico-deductivo.md`
- `fundamentos/primer-tiempo-logico.md`

### `epistemologia/`

- `epistemologia/contrato-epistemologico-smartgraph.md`
- `epistemologia/protocolo-conversacional-hermes.md`
- `epistemologia/modelo-verdad-soberania.md`

### `arquitectura/`

- `arquitectura/arquitectura-maestra.md`
- `arquitectura/domain-classification.md`
- `arquitectura/entropy-routing.md`
- `arquitectura/capability-runtime.md`
- `arquitectura/harness-engineering.md`
- `arquitectura/palantir-principles.md`
- `arquitectura/orchestration-boundary.md`
- `arquitectura/kernel-clinico-matematico-y-loop-humano.md`
- `arquitectura/roadmap-kernel-pericial-y-riesgos.md`

### `producto/`

- `producto/capa-00-canal-entrada.md`
- `producto/capa-01-admision-epistemologica.md`
- `producto/protocolo-anamnesis-mvp.md`
- `producto/asertividades-operativas.md`
- `producto/caso-operativo-diagnostico-y-decision.md`
- `producto/capas-00-a-03-admision-evidencia-caso-operativo.md`
- `producto/regla-estimacion-vs-diagnostico-confirmado.md`
- `producto/regla-identidad-conversacional-pymia.md`
- `producto/regla-no-loop-evidencia-ya-recibida.md`
- `producto/registro-ciclos-operativos.md`

### `contratos/`

- `contratos/contratos-clinicos-operacionales.md`
- `contratos/evidence-chain-v1.md`
- `contratos/owner-decision-v1.md`

### `catalogo/`

- `catalogo/atlas-sintomas-patologias.md`
- `catalogo/diseno-catalogo-clinico.md`
- `catalogo/anamnesis-y-catalogos.md`

### `hermes/`

- `hermes/soul.md`

---

## Pendientes explícitos — no presentes

Estos archivos están definidos como pendientes. No son fuente disponible y no autorizan reconstrucción desde memoria.

```text
hermes / arquitectura-conversacional
hermes / boundary-orquestacion
gobernanza / agents
gobernanza / agent-harness-governance
gobernanza / determinismo
```

---

## Qué NO está en esta biblioteca

Esta biblioteca no contiene:

- documentación de factoría;
- runtime legacy;
- workflows de jobs;
- prompts operativos de factoría;
- YAMLs híbridos de Hermes;
- evidencia de ciclos de construcción;
- reportes de ejecución de factoría;
- configuración de infraestructura VM;
- scripts de deploy.

Esos documentos pertenecen al repo SmartPyme y no deben migrar a PymIA, salvo corpus conversacional explícitamente migrado con provenance.
