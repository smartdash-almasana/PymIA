# PymIA Architecture Guardrails

Este documento fija los invariantes arquitectónicos para evitar deriva documental y runtime.

## 1. SOURCE_OF_TRUTH_HIERARCHY

```text
1. código físico vigente;
2. tests verdes y evidencia observada;
3. docs/current/README.md y sus referencias explícitas;
4. contratos y ADR vigentes citados desde la autoridad actual;
5. documentación externa con provenance;
6. memoria conversacional solo como pista.
```

Un documento histórico no puede contradecir código y tests actuales ni autorizar nuevas capacidades.

## 2. PROHIBICIONES ABSOLUTAS

- segundo parser XLSX;
- cadenas productivas paralelas;
- `unknown` desbloqueado por texto libre;
- LLM obligatorio o soberano en el core;
- operador humano obligatorio como actor del producto;
- create_job, workflow orchestration o runners paralelos como autoridad productiva;
- landings, demos o documentación histórica gobernando runtime;
- promesas de diagnóstico o entrega sin evidencia del caso.

## 3. HERMES_BOUNDARY

```text
Hermes/Conversa/PymIA-Live = legacy histórico
No gobiernan runtime actual.
No autorizan imports, adapters, wrappers ni entrypoints productivos.
Si se los cita, debe ser sólo como antecedente superado o referencia explícitamente histórica.
```

La capa conversacional puede formular preguntas y explicar resultados, pero no decide verdad operacional ni computabilidad.

## 4. DOCUMENTATION_POLICY

- Existe una sola raíz documental física: `docs/` en la raíz del repositorio.
- `docs/current/` contiene la autoridad vigente.
- Todo documento rector debe indicar alcance, estado y fuente de evidencia.
- No crear un documento nuevo cuando corresponde corregir uno vigente.
- La documentación obsoleta, duplicada o contradictoria se elimina del árbol activo.
- Índices históricos no tienen autoridad sobre `docs/current/README.md`.

## 5. TEST_POLICY

- Todo cambio productivo requiere tests focales y regresión vecina.
- Una declaración global de estabilidad requiere regresión completa.
- Los guards arquitectónicos deben verificar ausencia de contaminación legacy y de imports prohibidos.
- PASS solo con evidencia observada y alcance explícito.

## 6. ACCEPTANCE_CRITERIA

```text
pytest -q verde;
root productiva única;
no LLM runtime authority;
no segunda raíz productiva;
documentación vigente alineada con código real;
sin referencias rectoras activas a Hermes, Conversa o PymIA-Live.
```
