# Hipótesis de ensamble funcional — nodos SmartPyme para kernel PymIA

## Estado

Documento de trabajo.

Este documento no afirma que el flujo conjunto esté implementado en PymIA.

Su función es ordenar la hipótesis de cómo podrían conectarse los nodos identificados en SmartPyme para cubrir el tramo faltante del kernel de PymIA.

Regla:

```text
Cada nodo separado cumple una función, pero la utilidad real depende de la lógica de ensamble entre nodos.
```

---

## Problema

El inventario individual no alcanza.

Saber que existen contratos y servicios no prueba que formen un pipeline útil.

Lo que hay que validar es:

```text
entrada operacional
→ claim
→ investigación
→ suficiencia
→ caso
→ fórmula
→ patología
→ hallazgo
→ reporte
```

Si esa cadena no puede ejecutarse o testearse, los archivos son piezas sueltas.

---

## Hipótesis de flujo conjunto

```text
OperationalClaim
→ InvestigationContract / OperationalCaseCandidate
→ CaseOpeningService
→ OperationalCase
→ FormulaEngineService
→ PathologyEngineService
→ DiagnosticReportService
```

Opcionalmente, para un motor más directo:

```text
CuratedEvidenceRecord
→ BasicOperationalDiagnosticService
→ findings determinísticos
```

---

## Rol esperado de cada nodo dentro del conjunto

| Orden | Nodo | Rol dentro del flujo conjunto |
|---|---|---|
| 1 | `OperationalClaim` | Captura una afirmación operacional del dueño y controla su estado hasta que exista evidencia. |
| 2 | `InvestigationGraph` / `EvidenceGap` | Expande el claim en variables requeridas, evidencia disponible y brechas de investigación. |
| 3 | `OperationalCaseCandidate` | Resume si el caso puede investigarse, si falta evidencia o si requiere validación del dueño. |
| 4 | `CaseOpeningService` | Decide si el candidato abre un caso, pide aclaración, queda insuficiente o se rechaza. |
| 5 | `OperationalCase` | Representa el caso formal investigable, sin ser todavía diagnóstico. |
| 6 | `FormulaEngineService` | Ejecuta cálculo determinístico cuando existen inputs suficientes. |
| 7 | `PathologyEngineService` | Evalúa una patología operacional usando el resultado de fórmula. |
| 8 | `DiagnosticReportService` | Construye reporte diagnóstico y degrada a insuficiente si no hay evidencia/hallazgos medidos. |
| 9 | `BasicOperationalDiagnosticService` | Ruta alternativa directa: aplica reglas determinísticas sobre evidencia curada para generar findings. |

---

## Preguntas de validación

Antes de migrar a PymIA hay que responder con tests:

```text
1. ¿OperationalClaim puede alimentar InvestigationContract sin IA?
2. ¿InvestigationContract puede producir un OperationalCaseCandidate completo con evidencia mínima?
3. ¿CaseOpeningService decide estados sin depender de job/workflow/orquestación?
4. ¿OperationalCase puede existir sin job_id o debe podarse para PymIA?
5. ¿FormulaEngineService puede operar con StructuredEvidence o necesita adaptador?
6. ¿PathologyEngineService depende de catálogos `app.*` no migrados?
7. ¿DiagnosticReportService puede producir reporte sin acciones correctivas ni autorización?
8. ¿BasicOperationalDiagnosticService requiere repositorio externo o puede recibir evidencia en memoria?
9. ¿La cadena completa produce BLOCKED/PARTIAL/PASS o hay que mapear estados?
10. ¿Los tests existentes de SmartPyme pueden portarse sin traer factory/orchestration?
```

---

## Riesgo principal

El mayor riesgo no es técnico, sino arquitectónico:

```text
copiar piezas sueltas de SmartPyme sin entender su ensamble.
```

Eso produciría otra vez un kernel aparente, no un kernel funcional.

---

## Criterio de utilidad real

Un nodo se considera útil para PymIA solo si:

```text
- participa en una cadena ejecutable;
- tiene test asociado;
- no depende de jobs/workflows/orchestration;
- puede operar fail-closed;
- mejora el tramo evidencia → resultado;
- no requiere que Hermes interprete nada.
```

---

## Próxima prueba recomendada

No probar todos los nodos a la vez.

Primero probar la ruta más corta:

```text
FormulaInput
→ FormulaEngineService
→ FormulaResult
→ PathologyEngineService
→ PathologyFinding
→ DiagnosticReportService
```

Esta ruta valida cálculo, patología y reporte sin meter todavía claims, grafo ni caso operativo.

Segundo probar:

```text
OperationalCaseCandidate
→ CaseOpeningService
→ OperationalCase
```

Esta ruta valida suficiencia y apertura de caso.

Tercero probar:

```text
OperationalClaim
→ InvestigationContract
→ OperationalCaseCandidate
```

Esta ruta valida si la admisión puede convertirse en investigación sin IA.

---

## Decisión provisional

```text
No migrar por archivo.
Migrar por cadena testeada.
```

El valor no está en que cada archivo exista.

El valor está en demostrar que juntos cierran el tramo que falta en PymIA:

```text
evidencia → validación → cálculo → patología → hallazgo → reporte trazable
```
