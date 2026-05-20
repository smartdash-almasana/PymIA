# Inventario SmartPyme → PymIA: nodos colgados candidatos

## Estado

Inventario preliminar basado en recorrido físico de `SmartPyme/` dentro de `E:\BuenosPasos\smartbridge` y cruce parcial contra `PymIA/`.

No es una orden de migración automática.
No todo lo encontrado debe copiarse.
Este documento separa material de kernel/corpus útil de material factory/orquestación que no debe contaminar PymIA.

---

## Criterio usado

Solo se consideran candidatos los nodos que:

```text
- existen físicamente en SmartPyme;
- están relacionados con contratos, corpus, evidencia, diagnóstico, fórmulas, patologías, claims o casos;
- cubren huecos ya detectados en PymIA;
- pueden fortalecer el kernel determinístico sin depender de Hermes.
```

Se excluye por defecto:

```text
- factory;
- orchestration;
- jobs;
- workers;
- PR automation;
- provider runtime;
- MCP bridge operativo;
- memoria compleja;
- autonomía de agentes.
```

---

## Hallazgo general

SmartPyme contiene una cadena más completa que PymIA para pasar de admisión a diagnóstico operacional.

PymIA actual tiene principalmente:

```text
texto → admisión → hipótesis → evidencia requerida
```

SmartPyme conserva piezas para:

```text
claim → evidencia → activación investigativa → candidato de caso → apertura de caso → fórmula → patología → hallazgo/reporte
```

Ese tramo está incompleto o ausente en PymIA.

---

## Candidatos fuertes a revisar para PymIA

| Prioridad | Nodo SmartPyme | Archivo origen | Estado observado en PymIA | Motivo |
|---|---|---|---|---|
| Alta | `OperationalClaim` | `SmartPyme/app/contracts/operational_claims.py` | No encontrado como código en PymIA | Aporta estados y transiciones fail-closed para claims operativos antes de evidencia. |
| Alta | `InvestigationGraph`, `EvidenceGap`, `OperationalCaseCandidate` | `SmartPyme/app/contracts/investigation_contract.py` | Aparece en docs PymIA, no como código | Es la capa faltante entre admisión y caso operativo; transforma hipótesis + evidencia en candidato investigable. |
| Alta | `CaseOpeningService` | `SmartPyme/app/services/case_opening_service.py` | No encontrado como código en PymIA | Evalúa suficiencia de un candidato y produce estados determinísticos de apertura de caso. |
| Alta | `OperationalCase` / `DiagnosticReport` / `FindingRecord` / `QuantifiedImpact` | `SmartPyme/app/contracts/operational_case_contract.py` | Parcialmente documentado, no como núcleo ejecutable PymIA | Define salida diagnóstica con evidencia, hallazgos e impacto cuantificado. |
| Alta | `DiagnosticReportService` | `SmartPyme/app/services/diagnostic_report_service.py` | No encontrado como código en PymIA | Aplica regla clave: sin evidencia/hallazgos medidos, el diagnóstico queda `INSUFFICIENT_EVIDENCE`. |
| Alta | `FormulaInput`, `FormulaResult`, `SUPPORTED_FORMULAS` | `SmartPyme/app/contracts/formula_contract.py` | No encontrado como código en PymIA | Define contrato mínimo para cálculo determinístico `OK/BLOCKED`. |
| Alta | `FormulaEngineService` | `SmartPyme/app/services/formula_engine_service.py` | No encontrado como código en PymIA | Ejecuta fórmulas mínimas `margen_bruto` y `ganancia_bruta` con fail-closed por inputs faltantes. |
| Alta | `PathologyFinding`, `PathologyDefinition`, `PathologyStatus` | `SmartPyme/app/contracts/pathology_contract.py` | No encontrado como código en PymIA | Da forma a la evaluación de patologías con `ACTIVE/NOT_DETECTED/PENDING_DATA`. |
| Alta | `PathologyEngineService` | `SmartPyme/app/services/pathology_engine_service.py` | No encontrado como código en PymIA | Evalúa patología desde resultado de fórmula, bloquea si falta fórmula/evaluador. |
| Alta | `BasicOperationalDiagnosticService` | `SmartPyme/app/services/basic_operational_diagnostic_service.py` | No encontrado en PymIA | Motor determinístico núcleo robusto inicial con reglas explícitas de hallazgos operacionales; posible base de kernel diagnóstico. |
| Media | `CuratedEvidenceRecord` / BEM payloads | `SmartPyme/app/contracts/bem_payloads.py` | PymIA tiene `StructuredEvidence`, pero no este contrato curado | Aporta contrato externo de evidencia curada fail-closed; debe mapearse, no copiarse sin criterio. |
| Media | `RawDocument`, `DocumentRecord`, `EvidenceChunk`, `ExtractedFactCandidate`, `CanonicalRowCandidate` | `SmartPyme/app/contracts/evidence_contract.py` | PymIA tiene contrato de evidencia más simple | Útil si PymIA necesita pipeline documental más granular; no imprescindible para primer kernel mínimo. |
| Media | `SYMPTOM_CATALOG` ampliado | `SmartPyme/app/catalogs/symptom_pathology_catalog.py` | PymIA conserva solo una entrada ejecutable local | SmartPyme tiene más síntomas: stock, ventas, stock inmovilizado, cobranzas. Migrar solo si se valida corpus. |
| Media | `SkillRegistry` | `SmartPyme/app/catalogs/skill_registry.py` | Skills aparecen como nombres en PymIA, no como registry ejecutable | Puede formalizar skills candidatas, pero no debe implicar ejecución inexistente. |
| Media | `SkillOperationalConditionsRegistry` | `SmartPyme/app/catalogs/skill_operational_conditions.py` | No encontrado como código en PymIA | Formaliza variables/evidencia/bloqueos por skill; útil para suficiencia de evidencia. |
| Media | `OPERATIONAL_CONDITIONS_CATALOG` | `SmartPyme/app/catalogs/operational_conditions_catalog.py` | No encontrado como código en PymIA | Versión compacta de condiciones por skill; posible punto de partida más simple que el registry completo. |

---

## Material probablemente ya migrado o parcialmente migrado

| Nodo | SmartPyme | PymIA | Observación |
|---|---|---|---|
| Pipeline de admisión v1 | `SmartPyme/app/pipeline/admission/v1/*` | `PymIA/pymia/pipeline/admission/v1/*` | Parece migrado de forma sustancial. No priorizar salvo diff puntual. |
| Contrato `admission_v1` | `SmartPyme/app/contracts/admission_v1.py` | `PymIA/pymia/contracts/admission_v1.py` | Ya existe en PymIA. Revisar divergencias solo si tests lo exigen. |
| Servicio de anamnesis inicial | `SmartPyme/app/services/initial_laboratory_anamnesis_service.py` | `PymIA/pymia/services/initial_laboratory_anamnesis_service.py` | Ya existe versión PymIA. Revisar diferencias, no copiar entero. |
| Diseño de catálogo síntoma/patología | `SmartPyme/app/catalogs/symptom_pathology_catalog.py` | `PymIA/conversa-engine/symptom_pathology_catalog.py` + docs | Migración parcial: PymIA tiene una entrada ejecutable y más contenido documental. |

---

## Material a evitar dentro de PymIA core

Aunque exista en SmartPyme, no debe migrarse al core de PymIA sin boundary explícito:

```text
- jobs;
- job_executor;
- job_authorization;
- orchestration;
- factory;
- continuous_factory;
- queue runners;
- MCP execution bridges;
- provider fallback runtime;
- PR automation;
- multiagent runner;
- Hermes control tooling.
```

Motivo:

```text
PymIA debe fortalecer kernel determinístico, no absorber la factoría SmartPyme.
```

---

## Lectura arquitectónica

La pieza faltante más importante no es Telegram ni Hermes.

Es esta cadena:

```text
OperationalClaim
→ InvestigationGraph / EvidenceGap
→ OperationalCaseCandidate
→ CaseOpeningService
→ OperationalCase
→ FormulaEngineService
→ PathologyEngineService
→ DiagnosticReportService
```

Esa cadena representa el tramo que PymIA necesita para pasar de admisión a diagnóstico operacional trazable.

---

## Primer recorte recomendado

No migrar todo.

Primer paquete lógico a evaluar:

```text
1. formula_contract.py
2. formula_engine_service.py
3. pathology_contract.py
4. pathology_engine_service.py
5. diagnostic_report_service.py
6. tests asociados de fórmula/patología/reporte
```

Motivo:

```text
Es el tramo más pequeño que puede demostrar cálculo determinístico y bloqueo por falta de inputs.
```

Segundo paquete:

```text
1. operational_claims.py
2. investigation_contract.py
3. case_opening_service.py
4. operational_case_v2_contract.py / operational_case_contract.py
5. tests asociados
```

Motivo:

```text
Es el tramo de suficiencia y apertura de caso que conecta admisión con investigación.
```

Tercer paquete:

```text
1. skill_registry.py
2. skill_operational_conditions.py
3. operational_conditions_catalog.py
4. symptom_pathology_catalog.py ampliado
```

Motivo:

```text
Debe entrar solo después de decidir qué corpus real va a sostener el kernel.
```

---

## Regla de migración

```text
No copiar archivos de SmartPyme a PymIA por nombre.
Migrar comportamiento probado, contrato mínimo y tests.
```

Cada migración debe cumplir:

```text
- test de origen identificado;
- contrato PymIA equivalente o nuevo;
- imports adaptados de `app.*` a `pymia.*`;
- sin jobs/workflows/orchestration;
- sin dependencia de Hermes;
- fail-closed verificable.
```

---

## Próximo paso recomendado

Ejecutar una auditoría más fina de tests SmartPyme asociados a:

```text
- test_formula_contract_ts_009a.py
- test_formula_engine_service_ts_009b.py
- test_pathology_contract_ts_010a.py
- test_pathology_engine_service_ts_010b.py
- test_diagnostic_report_contract.py
- test_case_opening_service.py
- test_investigation_contract.py
```

Objetivo:

```text
extraer el mínimo comportamiento testeado que PymIA necesita para cerrar su kernel.
```
