Contexto heredado. No autoriza runtime, MCP, jobs, workflows ni orquestación dentro de PymIA. Rige ARCHITECTURE_GUARDRAILS.md.

# INVENTARIO CANÓNICO — PymIA/docs

Última actualización: en progreso (secuencial)

---

## Estado operativo consolidado

Definición canónica para este inventario:

- `presente`: archivo existe físicamente en `PymIA/docs/`.
- `pendiente`: archivo objetivo definido pero no existe en `PymIA/docs/`.
- `placeholder`: archivo existe, pero es marcador de espera y no contiene fuente canónica final.

Resumen actual:

- `presente`: 22
- `pendiente`: 6
- `placeholder`: 2

---
## Formato de cada entrada

```
destino:               ruta relativa dentro de PymIA/docs/
fuente_original:       ruta en SmartPyme repo
estado:                presente | pendiente | placeholder
provenance:            verificado_fisicamente | fuente_externa_validada | sin_fuente
contaminacion:         ninguna | paths_vm_removidos | referencias_factory_removidas | secretos_removidos
decision:              incluido | placeholder | pendiente
```

---

## vision/

| destino | fuente_original | estado | provenance | contaminacion | decision |
|---|---|---|---|---|---|
| `vision/SMARTPYME_LABORATORIO_PYME_Y_ESTABILIZACION_OPERACIONAL.md` | no encontrada en repo local | placeholder | fuente_externa_validada | ninguna | placeholder — incorporar fuente real |
| `vision/SMARTPYME_MVP_REALISTA_Y_FILOSOFIA_OPERACIONAL.md` | no encontrada en repo local | placeholder | fuente_externa_validada | ninguna | placeholder — incorporar fuente real |

**Nota:** Versiones fabricadas desde memoria fueron detectadas y eliminadas. Reemplazadas por placeholders con provenance explícito.

---

## fundamentos/

| destino | fuente_original | estado | provenance | contaminacion | decision |
|---|---|---|---|---|---|
|  |  | presente | verificado_fisicamente | ninguna | incluido |
|  |  | presente | verificado_fisicamente | ninguna | incluido |
|  |  | presente | verificado_fisicamente | ninguna | incluido |
|  |  | presente | verificado_fisicamente | ninguna | incluido — extracto de sección "Primer tiempo lógico" |

---

## epistemologia/

| destino | fuente_original | estado | provenance | contaminacion | decision |
|---|---|---|---|---|---|
|  |  | presente | verificado_fisicamente | ninguna | incluido |
|  |  | presente | verificado_fisicamente | ninguna | incluido |
|  |  | presente | verificado_fisicamente | ninguna | incluido |

---

## arquitectura/

| destino | fuente_original | estado | provenance | contaminacion | decision |
|---|---|---|---|---|---|
|  |  | presente | verificado_fisicamente | ninguna | incluido |
|  |  | presente | verificado_fisicamente | ninguna | incluido |
|  |  | presente | verificado_fisicamente | ninguna | incluido |
|  |  | presente | verificado_fisicamente | ninguna | incluido |
|  |  | presente | verificado_fisicamente | ninguna | incluido |
|  |  | presente | verificado_fisicamente | ninguna | incluido |
|  |  | presente | verificado_fisicamente | ninguna | incluido — agregada sección boundary MCP derivada de fix quirúrgico documentado |

---

## producto/

| destino | fuente_original | estado | provenance | contaminacion | decision |
|---|---|---|---|---|---|
|  |  | presente | verificado_fisicamente | ninguna | incluido |
|  |  | pendiente | verificado_fisicamente | ninguna | pendiente |
|  |  | presente | verificado_fisicamente | ninguna | incluido |
|  |  | presente | verificado_fisicamente | ninguna | incluido |

---

## contratos/

| destino | fuente_original | estado | provenance | contaminacion | decision |
|---|---|---|---|---|---|
|  |  | presente | verificado_fisicamente | ninguna | incluido |
|  |  | presente | verificado_fisicamente | referencias_factory_removidas | incluido — sección 10 "Conformidad con Fact Factory" removida (contiene path factory/evidence/ y placeholder [COMMIT_HASH]) |
|  |  | presente | verificado_fisicamente | referencias_factory_removidas | incluido — referencia a "flujo soberano de factoría" y "AUDIT_GATE" removidas de sección 7; contrato de soberanía del dueño preservado íntegro |

---

## catalogo/

| destino | fuente_original | estado | provenance | contaminacion | decision |
|---|---|---|---|---|---|
|  |  | presente | verificado_fisicamente | ninguna | incluido |
|  |  | presente | verificado_fisicamente | referencias_factory_removidas | incluido — sección "Próximo frente técnico sugerido" removida (contiene TS_026C task spec de factoría y rutas app/catalogs/) |
|  |  | presente | verificado_fisicamente | ninguna | incluido |

---

## hermes/

| destino | fuente_original | estado | provenance | contaminacion | decision |
|---|---|---|---|---|---|
|  |  | presente | verificado_fisicamente | ninguna | incluido |
|  |  | pendiente | verificado_fisicamente | paths_vm_removidos | pendiente |
|  |  | pendiente | verificado_fisicamente | ninguna | pendiente — ya existe en arquitectura/, evaluar si duplicar o referenciar |

---

## gobernanza/

| destino | fuente_original | estado | provenance | contaminacion | decision |
|---|---|---|---|---|---|
|  |  | pendiente | verificado_fisicamente | referencias_factory_removidas | pendiente |
|  |  | pendiente | verificado_fisicamente | ninguna | pendiente |
|  |  | pendiente | verificado_fisicamente | ninguna | pendiente |

---

## Dependencias conceptuales detectadas

| documento | depende de |
|---|---|
| `contratos/contratos-clinicos-operacionales.md` | `epistemologia/contrato-epistemologico-smartgraph.md` |
| `contratos/evidence-chain-v1.md` | `contratos/contratos-clinicos-operacionales.md` |
| `contratos/owner-decision-v1.md` | `contratos/evidence-chain-v1.md` |
| `catalogo/atlas-sintomas-patologias.md` | `fundamentos/metodo-hipotetico-deductivo.md` |
| `catalogo/diseno-catalogo-clinico.md` | `catalogo/atlas-sintomas-patologias.md` |
| `producto/capa-01-admision-epistemologica.md` | `producto/capa-00-canal-entrada.md` |
| `hermes/soul.md` | `arquitectura/orchestration-boundary.md` |
| `gobernanza/determinismo.md` | `contratos/contratos-clinicos-operacionales.md` |


