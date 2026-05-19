# Plano lógico del kernel integrado — pines, estados, compuertas y umbrales

## Estado

Documento de diseño lógico.

Este plano no afirma que el kernel integrado ya exista en PymIA.

Define cómo debería ensamblarse el circuito mínimo usando nodos existentes o candidatos detectados en PymIA/SmartPyme.

Regla rectora:

```text
No migrar por archivo.
Migrar por circuito probado.
```

---

## Analogía de circuito integrado

Un kernel funcional debe comportarse como un circuito lógico:

```text
inputs definidos
→ nodos con enable/disable
→ señales internas tipadas
→ compuertas de validación
→ estados cerrados
→ outputs trazables
```

Cada nodo debe declarar:

```text
- pines de entrada;
- pines de salida;
- señales internas;
- condición de activación;
- condición de bloqueo;
- tabla de verdad mínima;
- próximo nodo habilitado;
- estados terminales.
```

Si un input queda flotante:

```text
BLOCKED
```

Si una salida no puede trazarse:

```text
NO_VALID_SYSTEM_OUTPUT
```

---

## Señales lógicas globales

### Señales booleanas mínimas

```text
T = tenant_id válido
M = mensaje/claim no vacío
C = claim clasificado o interpretable
E = evidencia presente
V = variables mínimas presentes
G = gaps críticos presentes
S = fuente conocida para resolver gaps
H = hipótesis investigable válida
K = skill/fórmula soportada
I = inputs numéricos válidos
R = resultado reproducible
P = patología soportada
F = finding con evidencia vinculante
Q = impacto cuantificado
X = trazabilidad completa
```

### Estados globales

```text
NO_SIGNAL
BLOCKED
PARTIAL
READY_TO_INVESTIGATE
PENDING_OWNER_VALIDATION
INSUFFICIENT_EVIDENCE
REJECTED_OUT_OF_SCOPE
OK
ACTIVE
NOT_DETECTED
PENDING_DATA
CONFIRMED
NO_VALID_SYSTEM_OUTPUT
```

### Estados normalizados para PymIA

Para PymIA conviene normalizar todo a tres estados operativos mayores:

```text
BLOCKED = no puede avanzar sin evidencia/regla/contrato.
PARTIAL = puede informar indicio limitado o pedir aclaración específica.
PASS = produce salida trazable, reproducible y suficiente.
```

Mapeo sugerido:

```text
NO_SIGNAL                  → BLOCKED o silencio controlado
BLOCKED                   → BLOCKED
PENDING_DATA              → BLOCKED
INSUFFICIENT_EVIDENCE     → BLOCKED
REJECTED_OUT_OF_SCOPE     → BLOCKED
PENDING_OWNER_VALIDATION  → PARTIAL
READY_TO_INVESTIGATE      → PARTIAL
OK                        → PASS técnico del nodo
ACTIVE                    → PASS patológico positivo
NOT_DETECTED              → PASS patológico negativo
CONFIRMED                 → PASS diagnóstico
```

---

# Circuito integrado propuesto

## Vista general

```text
[IN0 OwnerMessage]
[IN1 TenantContext]
[IN2 StructuredEvidence]
[IN3 Catalog/Formula/Pathology Corpus]
        │
        ▼
N1 Admission / OperationalClaim
        │
        ▼
N2 InvestigationGraph / EvidenceGap
        │
        ▼
N3 OperationalCaseCandidate
        │
        ▼
N4 CaseOpeningService
        │
        ▼
N5 FormulaEngineService
        │
        ▼
N6 PathologyEngineService
        │
        ▼
N7 DiagnosticReportService
        │
        ▼
[OUT KernelOutput]
```

Ruta alternativa directa:

```text
StructuredEvidence / CuratedEvidenceRecord
        │
        ▼
N8 BasicOperationalDiagnosticService
        │
        ▼
Findings determinísticos
```

---

# N1 — Admission / OperationalClaim

## Función

Captura una señal operacional inicial y la convierte en claim controlado, sin diagnosticar.

## Pines de entrada

```text
IN1.tenant_id
IN1.session_id
IN1.source_turn_id
IN1.message_text
IN1.channel
IN1.metadata opcional
```

## Pines de salida

```text
OUT1.claim_id
OUT1.claim_type
OUT1.statement
OUT1.status
OUT1.evidence_ids
OUT1.confirmation_question
OUT1.evidence_question
```

## Señales internas

```text
T = tenant_id válido
M = message_text no vacío
C = claim_type clasificado
```

## Umbral de activación

```text
ENABLE_N1 = T AND M
```

## Tabla de verdad mínima

| T | M | C | Salida |
|---|---|---|---|
| 0 | * | * | BLOCKED: tenant inválido |
| * | 0 | * | BLOCKED: mensaje vacío |
| 1 | 1 | 0 | NO_SIGNAL o PENDING_CONFIRMATION genérico |
| 1 | 1 | 1 | OperationalClaim(status=PENDING_CONFIRMATION) |

## Compuertas

```text
AND(T, M) = habilita captura.
OR(C, fallback_controlado) = permite claim genérico solo si está documentado.
NAND(T, M) = bloqueo inmediato.
```

## Condición de cierre

```text
claim.status in {CONFIRMED, REJECTED, BLOCKED}
```

## Próximo nodo

```text
N2 si claim.status == CONFIRMED o EVIDENCE_RECEIVED
```

---

# N2 — InvestigationGraph / EvidenceGap

## Función

Transforma claim + corpus + evidencia en grafo investigativo: síntomas, patologías candidatas, fórmulas, variables, evidencias y gaps.

## Pines de entrada

```text
IN2.claim_id
IN2.claim_type
IN2.statement
IN2.catalog_symptoms
IN2.catalog_pathologies
IN2.formula_catalog
IN2.structured_evidence
```

## Pines de salida

```text
OUT2.graph_id
OUT2.nodes[]
OUT2.edges[]
OUT2.required_variables[]
OUT2.available_variables[]
OUT2.evidence_gaps[]
OUT2.primary_pathology
OUT2.hypothesis
```

## Señales internas

```text
C = claim válido
H = hipótesis investigable construida
V = al menos una variable requerida identificada
E = evidencia disponible mapeada
G = gaps críticos presentes
S = fuente conocida para gap crítico
```

## Umbral de activación

```text
ENABLE_N2 = C AND H AND V
```

## Tabla de verdad mínima

| C | H | V | E | G | S | Salida |
|---|---|---|---|---|---|---|
| 0 | * | * | * | * | * | BLOCKED: claim inválido |
| 1 | 0 | * | * | * | * | BLOCKED: sin hipótesis investigable |
| 1 | 1 | 0 | * | * | * | BLOCKED: sin variables requeridas |
| 1 | 1 | 1 | 0 | 1 | 0 | BLOCKED_MISSING_VARIABLES |
| 1 | 1 | 1 | 0 | 1 | 1 | PENDING_OWNER_VALIDATION |
| 1 | 1 | 1 | 1 | 1 | 1 | PARTIAL_EVIDENCE |
| 1 | 1 | 1 | 1 | 0 | * | READY_TO_INVESTIGATE |

## Compuertas

```text
AND(C, H, V) = construye grafo.
NAND(C, H, V) = bloquea por contrato insuficiente.
AND(G, NOT S) = gap crítico irresoluble.
AND(G, S) = pregunta/validación al dueño.
OR(E, S) = puede formular siguiente paso.
XOR(E, G) = distingue evidencia suficiente de brecha pura.
```

## Condición de cierre

```text
InvestigationGraph emitido + OperationalCaseCandidate construible
```

## Próximo nodo

```text
N3
```

---

# N3 — OperationalCaseCandidate

## Función

Condensa el grafo en un candidato de caso: investigable, parcial, bloqueado o pendiente de validación.

## Pines de entrada

```text
IN3.graph_id
IN3.primary_pathology
IN3.hypothesis
IN3.available_variables[]
IN3.evidence_gaps[]
IN3.recommended_route
IN3.next_step
```

## Pines de salida

```text
OUT3.candidate_id
OUT3.status
OUT3.primary_pathology
OUT3.hypothesis
OUT3.available_variables[]
OUT3.evidence_gaps[]
OUT3.next_step
```

## Señales internas

```text
H = hipótesis válida
P = patología principal identificada
A = available_variables no vacío
G = evidence_gaps críticos
S = fuente conocida para gaps
```

## Umbral de activación

```text
ENABLE_N3 = H AND P
```

## Tabla de verdad mínima

| H | P | A | G | S | CandidateStatus |
|---|---|---|---|---|---|
| 0 | * | * | * | * | BLOCKED_MISSING_VARIABLES |
| * | 0 | * | * | * | BLOCKED_MISSING_VARIABLES |
| 1 | 1 | 0 | 1 | 0 | BLOCKED_MISSING_VARIABLES |
| 1 | 1 | 0 | 1 | 1 | PENDING_OWNER_VALIDATION |
| 1 | 1 | 1 | 1 | 1 | PARTIAL_EVIDENCE |
| 1 | 1 | 1 | 0 | * | READY_TO_INVESTIGATE |

## Compuertas

```text
AND(H, P) = candidato estructuralmente válido.
NAND(H, P) = candidato no válido.
AND(A, NOT G) = listo para investigar.
AND(G, NOT S) = bloqueado.
AND(G, S) = validación requerida.
```

## Condición de cierre

```text
candidate.status emitido en set permitido
```

## Próximo nodo

```text
N4
```

---

# N4 — CaseOpeningService

## Función

Evalúa si el candidato abre un caso operativo o se bloquea/aclara/rechaza por suficiencia.

## Pines de entrada

```text
IN4.OperationalCaseCandidate
IN4.case_id opcional
```

## Pines de salida

```text
OUT4.OperationalCase
OUT4.status
OUT4.next_step
OUT4.clarification_question opcional
OUT4.insufficiency_reason opcional
OUT4.rejection_reason opcional
```

## Señales internas

```text
P = primary_pathology no vacía
A = available_variables no vacío
Gcrit = gap crítico
Ghigh = gap alto
S = required_source conocida
V = owner validation pendiente
```

## Umbral de activación

```text
ENABLE_N4 = candidate_id AND hypothesis
```

## Tabla de verdad mínima

| P | A | Gcrit | Ghigh | S | V | OperationalCase.status |
|---|---|---|---|---|---|---|
| 0 | * | * | * | * | * | REJECTED_OUT_OF_SCOPE |
| 1 | 0 | 1 | * | 0 | * | REJECTED_OUT_OF_SCOPE si candidate=BLOCKED_MISSING_VARIABLES |
| 1 | 0 | * | * | 0 | 0 | INSUFFICIENT_EVIDENCE |
| 1 | * | * | 1 | 1 | * | CLARIFICATION_REQUIRED |
| 1 | * | * | * | * | 1 | CLARIFICATION_REQUIRED |
| 1 | 1 | 0 | 0 | * | 0 | READY_FOR_INVESTIGATION |

## Compuertas

```text
NAND(P) = rechazo fuera de alcance.
AND(Gcrit, NOT S) = rechazo o insuficiencia.
OR(V, AND(Ghigh, S)) = aclaración requerida.
AND(P, A, NOT Gcrit, NOT V) = listo para investigar.
```

## Condición de cierre

```text
OperationalCase.status in {
  READY_FOR_INVESTIGATION,
  CLARIFICATION_REQUIRED,
  INSUFFICIENT_EVIDENCE,
  REJECTED_OUT_OF_SCOPE
}
```

## Próximo nodo

```text
N5 si status == READY_FOR_INVESTIGATION
owner loop si status == CLARIFICATION_REQUIRED
terminal BLOCKED si status in {INSUFFICIENT_EVIDENCE, REJECTED_OUT_OF_SCOPE}
```

---

# N5 — FormulaEngineService

## Función

Ejecuta una fórmula determinística sobre inputs numéricos trazados.

## Pines de entrada

```text
IN5.formula_id
IN5.FormulaInput[]
IN5.source_refs[]
```

## Pines de salida

```text
OUT5.FormulaResult
OUT5.status = OK | BLOCKED
OUT5.value
OUT5.inputs
OUT5.source_refs
OUT5.blocking_reason opcional
```

## Señales internas

```text
K = formula_id soportada
I = inputs requeridos presentes
Z = división por cero o dominio inválido
X = source_refs presentes
```

## Umbral de activación

```text
ENABLE_N5 = K AND I AND NOT Z
```

## Tabla de verdad mínima

| K | I | Z | Resultado |
|---|---|---|---|
| 0 | * | * | BLOCKED: FORMULA_NOT_SUPPORTED |
| 1 | 0 | * | BLOCKED: MISSING_INPUTS |
| 1 | 1 | 1 | BLOCKED: DIVISION_BY_ZERO / dominio inválido |
| 1 | 1 | 0 | OK(value calculado) |

## Compuertas

```text
AND(K, I, NOT Z) = cálculo habilitado.
NAND(K, I) = bloqueo por contrato.
OR(NOT K, NOT I, Z) = bloqueo técnico.
```

## Condición de cierre

```text
FormulaResult.status emitido + source_refs preservados
```

## Próximo nodo

```text
N6 si status == OK
terminal BLOCKED si status == BLOCKED
```

---

# N6 — PathologyEngineService

## Función

Evalúa si una patología operacional está activa, no detectada o pendiente de datos usando el resultado de fórmula.

## Pines de entrada

```text
IN6.pathology_id
IN6.formula_result_id
IN6.FormulaResult
IN6.pathology_catalog
IN6.evaluator_registry
```

## Pines de salida

```text
OUT6.PathologyFinding
OUT6.status = ACTIVE | NOT_DETECTED | PENDING_DATA
OUT6.severity opcional
OUT6.suggested_action opcional
OUT6.source_refs
OUT6.explanation
OUT6.metadata
```

## Señales internas

```text
P = pathology_id soportada
F = FormulaResult.status == OK
C = formula_id coincide con pathology.formula_id
E = evaluador implementado
A = regla patológica activa
```

## Umbral de activación

```text
ENABLE_N6 = P AND F AND C AND E
```

## Tabla de verdad mínima

| P | F | C | E | A | PathologyStatus |
|---|---|---|---|---|---|
| 0 | * | * | * | * | PENDING_DATA: PATHOLOGY_NOT_SUPPORTED |
| 1 | 0 | * | * | * | PENDING_DATA: fórmula bloqueada |
| 1 | 1 | 0 | * | * | PENDING_DATA: fórmula no coincide |
| 1 | 1 | 1 | 0 | * | PENDING_DATA: evaluador no implementado |
| 1 | 1 | 1 | 1 | 1 | ACTIVE |
| 1 | 1 | 1 | 1 | 0 | NOT_DETECTED |

## Compuertas

```text
AND(P, F, C, E) = evaluación habilitada.
NAND(P, F, C, E) = PENDING_DATA.
XOR(A, NOT A) = salida binaria de patología evaluada.
```

## Condición de cierre

```text
PathologyFinding.status emitido + source_refs preservados
```

## Próximo nodo

```text
N7 si status in {ACTIVE, NOT_DETECTED}
terminal BLOCKED/PARTIAL si status == PENDING_DATA
```

---

# N7 — DiagnosticReportService

## Función

Construye reporte diagnóstico final y degrada a insuficiencia si no hay evidencia, hallazgos o diferencias medidas.

## Pines de entrada

```text
IN7.case_id
IN7.cliente_id / tenant_id
IN7.hypothesis
IN7.findings[]
IN7.evidence_used[]
IN7.formulas_used[]
IN7.quantified_impact
IN7.reasoning_summary
IN7.references_used[]
```

## Pines de salida

```text
OUT7.DiagnosticReport
OUT7.diagnosis_status = CONFIRMED | INSUFFICIENT_EVIDENCE | DISPROVED/PENDING según contrato
OUT7.findings[]
OUT7.evidence_used[]
OUT7.quantified_impact
OUT7.owner_question opcional
```

## Señales internas

```text
F = findings no vacío
E = evidence_used no vacío
D = measured_difference presente en cada finding
Q = quantified_impact no vacío
R = reasoning_summary no vacío
X = trazabilidad completa
```

## Umbral de activación

```text
ENABLE_N7 = E AND F AND D AND Q AND R
```

## Tabla de verdad mínima

| E | F | D | Q | R | X | DiagnosisStatus |
|---|---|---|---|---|---|---|
| 0 | * | * | * | * | * | INSUFFICIENT_EVIDENCE |
| 1 | 0 | * | * | * | * | INSUFFICIENT_EVIDENCE |
| 1 | 1 | 0 | * | * | * | INSUFFICIENT_EVIDENCE |
| 1 | 1 | 1 | 0 | * | * | INSUFFICIENT_EVIDENCE o PARTIAL |
| 1 | 1 | 1 | 1 | 0 | * | INSUFFICIENT_EVIDENCE |
| 1 | 1 | 1 | 1 | 1 | 0 | NO_VALID_SYSTEM_OUTPUT |
| 1 | 1 | 1 | 1 | 1 | 1 | CONFIRMED |

## Compuertas

```text
AND(E, F, D, Q, R, X) = diagnóstico confirmado.
NAND(E, F, D) = insuficiencia de evidencia.
NAND(X) = salida inválida del sistema.
OR(NOT E, NOT F, NOT D, NOT R) = degradación a insuficiente.
```

## Condición de cierre

```text
DiagnosticReport emitido con estado terminal
```

## Próximo nodo

```text
OUT KernelOutput
```

---

# N8 — BasicOperationalDiagnosticService

## Función

Ruta alternativa directa: aplica reglas determinísticas sobre evidencia curada y produce findings operacionales sin pasar por grafo/caso/fórmula.

## Pines de entrada

```text
IN8.tenant_id
IN8.CuratedEvidenceRecord[]
IN8.payload por evidencia
```

## Pines de salida

```text
OUT8.report.tenant_id
OUT8.report.findings[]
OUT8.report.evidence_count
```

## Señales internas

```text
T = tenant_id válido
E = evidencia existente
N = campos numéricos requeridos por regla
A = regla activa
Iso = aislamiento tenant correcto
```

## Umbral de activación

```text
ENABLE_N8 = T
```

## Tabla de verdad mínima

| T | E | N | A | Iso | Salida |
|---|---|---|---|---|---|
| 0 | * | * | * | * | excepción fail-closed |
| 1 | 0 | * | * | 1 | findings=[]; evidence_count=0 |
| 1 | 1 | 0 | * | 1 | findings=[]; no falso positivo |
| 1 | 1 | 1 | 0 | 1 | findings=[] |
| 1 | 1 | 1 | 1 | 1 | findings determinísticos |
| 1 | 1 | 1 | 1 | 0 | NO_VALID_SYSTEM_OUTPUT |

## Reglas internas observadas

```text
VENTA_BAJO_COSTO
RENTABILIDAD_NULA
MARGEN_CRITICO
COSTO_CERO_SOSPECHOSO
VENTA_SIN_STOCK
STOCK_NEGATIVO
MOVIMIENTO_INCONSISTENTE
INVENTARIO_FANTASMA
PRECIO_DESACTUALIZADO
STOCK_INMOVILIZADO
DESCUENTO_EXCESIVO
VENTA_ESTANCADA
COMPRA_SIN_VENTA
DUPLICADO_OPERACIONAL
```

## Compuertas

```text
AND(T, E, N, A, Iso) = finding válido.
NAND(T) = excepción.
NAND(N) = no finding, fail-closed.
AND(A, NOT X) = output inválido si no hay trazabilidad.
```

## Condición de cierre

```text
report emitido con evidence_count y findings trazados por evidence_id
```

## Próximo nodo

```text
Puede alimentar N7 si findings se adaptan a DiagnosticReport.
```

---

# Tabla de acoplamiento entre nodos

| De | A | Señal que pasa | Condición de acople |
|---|---|---|---|
| N1 | N2 | `OperationalClaim` | claim confirmado o con evidencia recibida |
| N2 | N3 | `InvestigationGraph` + gaps | hipótesis y variables requeridas identificadas |
| N3 | N4 | `OperationalCaseCandidate` | candidate válido con status permitido |
| N4 | N5 | `OperationalCase` | status `READY_FOR_INVESTIGATION` |
| N5 | N6 | `FormulaResult` | status `OK` y source_refs preservados |
| N6 | N7 | `PathologyFinding` | status `ACTIVE` o `NOT_DETECTED` |
| N8 | N7 | `findings[]` | adapter convierte finding dict a FindingRecord |

---

# Compuertas globales del kernel

## AND — avance normal

```text
ADVANCE = tenant_ok AND input_ok AND contract_ok AND evidence_ok AND trace_ok
```

Uso:

```text
habilita paso al siguiente nodo.
```

## NAND — bloqueo seguro

```text
BLOCK = NOT(tenant_ok AND contract_ok AND trace_ok)
```

Uso:

```text
si falta un mínimo estructural, no se interpreta; se bloquea.
```

## OR — rutas alternativas válidas

```text
EVIDENCE_AVAILABLE = structured_evidence OR curated_evidence OR available_variables
```

Uso:

```text
permite distintas fuentes de evidencia si todas tienen contrato.
```

## XOR — exclusividad de rutas

```text
USE_GRAPH_ROUTE XOR USE_DIRECT_DIAGNOSTIC_ROUTE
```

Uso:

```text
evita que dos rutas produzcan diagnósticos simultáneos contradictorios.
```

Regla:

```text
Si ambas rutas están activas, se requiere reconciliación explícita o BLOCKED.
```

## NOR — no señal válida

```text
NO_SIGNAL = NOT(claim_signal OR evidence_signal OR catalog_match)
```

Uso:

```text
evita crear casos cuando no hay señal operacional.
```

---

# Tabla global de verdad del kernel

| T | M/C | E | V | K | I | P | F | X | Estado kernel |
|---|-----|---|---|---|---|---|---|---|---|
| 0 | * | * | * | * | * | * | * | * | BLOCKED |
| 1 | 0 | * | * | * | * | * | * | * | NO_SIGNAL/BLOCKED |
| 1 | 1 | 0 | 0 | * | * | * | * | 1 | BLOCKED: falta evidencia |
| 1 | 1 | 1 | 0 | * | * | * | * | 1 | PARTIAL: evidencia no mapea variables |
| 1 | 1 | 1 | 1 | 0 | * | * | * | 1 | BLOCKED: fórmula/skill no soportada |
| 1 | 1 | 1 | 1 | 1 | 0 | * | * | 1 | BLOCKED: inputs inválidos |
| 1 | 1 | 1 | 1 | 1 | 1 | 0 | * | 1 | BLOCKED/PARTIAL: patología no soportada |
| 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 1 | PASS negativo o INSUFFICIENT según caso |
| 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | NO_VALID_SYSTEM_OUTPUT |
| 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | PASS |

---

# Umbrales de activación y cierre

## Activación mínima del kernel

```text
tenant_id válido
AND mensaje/claim no vacío
AND contrato de entrada válido
```

## Activación de investigación

```text
claim confirmado
AND hipótesis investigable
AND variables requeridas identificadas
```

## Activación de cálculo

```text
fórmula soportada
AND inputs requeridos presentes
AND dominio matemático válido
```

## Activación de patología

```text
patología soportada
AND fórmula OK
AND fórmula coincide con patología
AND evaluador implementado
```

## Activación de diagnóstico confirmado

```text
evidencia usada
AND hallazgos presentes
AND diferencia medida
AND impacto cuantificado
AND razonamiento no vacío
AND trazabilidad completa
```

## Cierre por bloqueo

```text
falta tenant
OR falta contrato
OR falta evidencia crítica
OR falta fórmula soportada
OR falta evaluador
OR falta trazabilidad
```

## Cierre por parcialidad

```text
hay señal válida
AND hay algo de evidencia
AND faltan variables o validación del dueño
AND existe pregunta concreta de desbloqueo
```

## Cierre por PASS

```text
todo input crítico presente
AND cálculo reproducible
AND evaluación completada
AND reporte trazable
```

---

# Señales que nunca puede fabricar Hermes

```text
evidence_used
source_refs
formula_result.value
pathology_status
finding.measured_difference
quantified_impact
blocking_reason
case.status
diagnosis_status
input_hash
output_hash
```

Hermes solo puede transportar estas señales si vienen emitidas por el kernel.

---

# Pruebas mínimas del circuito integrado

## Prueba 1 — bloqueo por falta de evidencia

```text
OwnerMessage válido
sin StructuredEvidence
sin CuratedEvidenceRecord
```

Esperado:

```text
BLOCKED o PARTIAL con pregunta de evidencia;
no diagnóstico;
no finding;
no fórmula ejecutada.
```

## Prueba 2 — fórmula OK

```text
formula_id=margen_bruto
ventas=1000
costos=750
```

Esperado:

```text
FormulaResult.status=OK
value=0.25
source_refs preservados
```

## Prueba 3 — fórmula bloqueada

```text
formula_id=margen_bruto
ventas=0
costos=750
```

Esperado:

```text
FormulaResult.status=BLOCKED
blocking_reason=DIVISION_BY_ZERO: ventas
```

## Prueba 4 — patología activa

```text
margen_bruto con ventas=1000, costos=1200
pathology_id=margen_bruto_negativo
```

Esperado:

```text
PathologyFinding.status=ACTIVE
source_refs preservados
```

## Prueba 5 — patología no detectada

```text
margen_bruto con ventas=1000, costos=600
pathology_id=margen_bruto_negativo
```

Esperado:

```text
PathologyFinding.status=NOT_DETECTED
```

## Prueba 6 — reporte insuficiente

```text
findings=[]
evidence_used=[]
```

Esperado:

```text
DiagnosticReport.diagnosis_status=INSUFFICIENT_EVIDENCE
```

## Prueba 7 — ruta directa por evidencia curada

```text
CuratedEvidenceRecord payload={precio_venta: 50, costo_unitario: 80}
```

Esperado:

```text
finding_type=VENTA_BAJO_COSTO
severity=HIGH
evidence_id preservado
```

## Prueba 8 — anti-XOR de rutas

```text
GraphRoute produce patología A
DirectDiagnosticRoute produce finding contradictorio B
```

Esperado:

```text
BLOCKED: ROUTE_CONFLICT_REQUIRES_RECONCILIATION
```

---

# Decisión de diseño

El kernel integrado mínimo no debe empezar por UI ni Hermes.

Tampoco debe quedar soldado a una única galaxia de conocimiento.

Principio rector:

```text
El kernel hard puro es la capa lógica y universal de investigación y hallazgo.
Los tanques de conocimiento deben ser enchufables y desenchufables.
```

El kernel no debe depender de un dominio específico para existir.
Debe poder conectarse a distintos corpus, catálogos, fórmulas, patologías, taxonomías o reglas, y operar con la misma lógica:

```text
lógica incompleta
→ contextualización por tanque de conocimiento
→ hipótesis investigable
→ evidencia requerida
→ cálculo/evaluación
→ hallazgo trazable
```

El motor vive para completar el rompecabezas, pero no puede inventar piezas.
Si el tanque de conocimiento no provee una pieza o la evidencia no alcanza, el kernel debe bloquear o declarar parcialidad.

Máxima de adquisición:

```text
El kernel no inventa piezas: pide.
```

Puede pedir a:

```text
- humanos;
- dueños/operadores;
- documentos;
- datos en base de datos;
- memoria semántica RAW/RAG;
- internet;
- deepsearch;
- APIs;
- MCP;
- cualquier tanque de conocimiento conectable.
```

Pero solo puede ingerir lo que aporte coherencia verificable al rompecabezas:

```text
input externo
→ validación de procedencia
→ encaje con hipótesis/evidencia requerida
→ trazabilidad
→ aceptación, parcialidad o rechazo
```

Regla de máxima prioridad:

```text
1. Documentos y datos persistidos.
2. Respuestas explícitas de dueños/humanos.
3. Memoria semántica RAW/RAG.
4. APIs/MCP/fuentes estructuradas.
5. Internet/deepsearch con trazabilidad.
```

Ninguna fuente externa autoriza al kernel a completar un hueco sin evidencia.
Si una pieza no puede validarse, queda como candidata, no como verdad del sistema.

Definición abstracta del kernel:

```text
Kernel experto en ecuaciones e incógnitas.
```

Todo problema debe poder representarse como una ecuación incompleta:

```text
estado observado + contexto + restricciones + evidencia disponible + incógnitas = hallazgo verificable
```

El kernel opera sobre incógnitas:

```text
- detecta variables conocidas;
- detecta variables faltantes;
- identifica restricciones;
- identifica fuentes posibles para resolver cada incógnita;
- pide la pieza faltante;
- valida si la pieza encaja;
- recalcula el estado del sistema;
- cierra en BLOCKED, PARTIAL o PASS.
```

La función universal del kernel no es responder: es resolver ecuaciones de conocimiento incompleto sin inventar términos.

Arquetipo operacional:

```text
Kernel = Sherlock Holmes.
```

No es un generador de respuestas.
Es un investigador lógico:

```text
observa señales;
separa hechos de suposiciones;
formula hipótesis;
busca contradicciones;
pide evidencia faltante;
descarta hipótesis incompatibles;
conserva trazabilidad;
cierra solo cuando el caso encaja.
```

Regla Holmes:

```text
No adivinar.
Inferir solo desde piezas observables.
Cuando falta una pieza, pedirla.
Cuando una hipótesis contradice la evidencia, descartarla.
Cuando varias hipótesis siguen vivas, declarar PARTIAL.
Cuando no hay evidencia mínima, declarar BLOCKED.
```

Patrón metodológico equivalente:

```text
Kernel = auditor científico deductivo-inductivo.
```

El kernel debe operar como un auditor empírico de grandes compañías, pero generalizado a cualquier galaxia de conocimiento:

```text
observación
→ planteamiento del problema
→ hipótesis
→ prueba / experimentación
→ evidencia
→ contraste
→ conclusión verificable
```

Traducción al kernel:

```text
observación = señales, documentos, datos, respuestas, memoria RAW/RAG, APIs o MCP;
hipótesis = explicación candidata del problema;
experimentación = pruebas, recálculo, comparación, confirmación externa, inspección o consulta;
evidencia = pieza trazable que confirma, debilita o refuta la hipótesis;
validación = cierre PASS/PARTIAL/BLOCKED según suficiencia y coherencia.
```

Método deductivo-inductivo:

```text
inducción = subir desde operaciones particulares hacia patrones o anomalías;
deducción = bajar desde reglas, contratos, políticas o modelos hacia pruebas concretas;
contraste = verificar si las piezas empíricas encajan con la hipótesis.
```

Técnicas universales del kernel:

```text
confirmación externa;
procedimientos analíticos;
comparación contra ratios/modelos/corpus;
recálculo;
inspección documental;
rastreo de origen;
detección de desviaciones;
ajuste o descarte de hipótesis.
```

La salida no es una opinión libre.
La salida es un dictamen lógico sobre la razonabilidad de una hipótesis frente a evidencia trazable.

Fundamento metodológico externo incorporado:

```text
Marchese/Ingrassia — Métodos de investigación en Contabilidad y Administración.
```

Aportes relevantes al kernel:

```text
- toda actividad humana debe estar basada en una metodología;
- sistematizar una actividad no equivale a pensar sistémicamente;
- la investigación contable positiva busca identificar y contrastar empíricamente hipótesis;
- los sistemas suaves operan como procesos de aprendizaje, no como soluciones cerradas;
- el conocimiento puede representarse como hechos, reglas, constantes y variables;
- los indicadores surgen de combinaciones de hechos según procedimientos aceptados;
- la producción de conocimiento integra información en forma de variables, reglas y declaraciones.
```

Traducción al kernel:

```text
hechos observados = datos/documentos/señales;
reglas = corpus, contrato, fórmula, criterio o restricción;
variables = piezas conocidas o incógnitas;
indicador = combinación válida de hechos según regla;
hallazgo = indicador contrastado contra hipótesis;
aprendizaje sistémico = iteración BLOCKED/PARTIAL/PASS con nuevas piezas.
```

Consecuencia:

```text
El kernel no debe ser una máquina cerrada de respuestas.
Debe ser un sistema lógico de investigación que aprende por contraste, sin abandonar el control metodológico.
```

Formulación final:

```text
Todo esto debe llevarse a un circuito integrado determinístico.
```

El método científico, la auditoría empírica, el razonamiento Holmes, las ecuaciones con incógnitas y los tanques de conocimiento enchufables deben compilarse en una arquitectura ejecutable:

```text
pines de entrada
→ normalización
→ detección de incógnitas
→ selección de tanque de conocimiento
→ generación de hipótesis
→ pedido de piezas faltantes
→ validación de evidencia
→ recálculo/contraste
→ compuertas de cierre
→ output trazable
```

El circuito integrado determinístico debe cumplir:

```text
- mismos inputs producen mismos outputs;
- cada transición tiene regla explícita;
- cada bloqueo tiene causa explícita;
- cada hipótesis conserva trazabilidad;
- cada tanque de conocimiento es enchufable/desenchufable;
- ninguna pieza se inventa;
- toda pieza externa entra como candidata hasta validarse;
- todo cierre termina en BLOCKED, PARTIAL o PASS.
```

Representación lógica mínima:

```text
ObservedFacts
+ KnowledgeTank
+ Constraints
+ Unknowns
+ Evidence
+ Rules
= FindingState(BLOCKED | PARTIAL | PASS)
```

Compuerta maestra:

```text
PASS = facts_valid AND rules_valid AND evidence_sufficient AND trace_complete AND no_contradiction
PARTIAL = signal_valid AND missing_piece_known AND next_request_defined AND no_fatal_contradiction
BLOCKED = no_signal OR missing_critical_piece OR invalid_source OR contradiction OR unsupported_rule
```

La aspiración del kernel no es parecer inteligente.
La aspiración del kernel es ser un circuito lógico que investiga, pide, contrasta y cierra sin delirio.

Debe empezar por probar el circuito:

```text
inputs tipados
→ compuertas de suficiencia
→ cálculo determinístico
→ evaluación de patología
→ reporte trazable
```

La migración desde SmartPyme a PymIA debe hacerse por chip lógico:

```text
Chip 1: Formula + Pathology + DiagnosticReport
Chip 2: OperationalCaseCandidate + CaseOpeningService
Chip 3: OperationalClaim + InvestigationGraph
Chip 4: BasicOperationalDiagnosticService como ruta directa controlada
```

Cada chip debe tener sus pines, estados y tests antes de conectarse al siguiente.

---

# Veredicto sobre lógica de entrada/salida

El plano sirve como diseño lógico porque define pines, estados, compuertas y condiciones de acople.

Pero todavía no debe declararse como circuito funcional ejecutable.

```text
Sirve como arquitectura de señales.
No está probado como circuito integrado operativo.
```

Para afirmar que funciona hay que demostrar continuidad pin-a-pin:

```text
OUT_N1 compatible con IN_N2
OUT_N2 compatible con IN_N3
OUT_N3 compatible con IN_N4
OUT_N4 compatible con IN_N5
OUT_N5 compatible con IN_N6
OUT_N6 compatible con IN_N7
```

La lógica de entrada/salida queda validada solo si cada nodo cumple tres condiciones:

```text
1. acepta exactamente los pines que declara;
2. emite exactamente los pines que consume el siguiente nodo;
3. bloquea cuando falta un pin crítico en vez de improvisar.
```

## Estado actual del veredicto

```text
Coherencia conceptual: SÍ.
Circuito ejecutable probado end-to-end: NO confirmado.
Utilidad para diseñar tests de integración: SÍ.
Autorización para migrar todo: NO.
```

## Evidencia parcial de Chip 1

Ejecuciones locales reportadas:

```text
FormulaEngineService: 4 passed.
PathologyEngineService: 4 passed.
DiagnosticReportService: 3 passed.
```

Estado del chip:

```text
FormulaInput → FormulaEngineService → FormulaResult: PASS.
FormulaResult → PathologyEngineService → PathologyFinding: PASS.
PathologyFinding → DiagnosticReportService → DiagnosticReport: PASS.
```

Veredicto parcial:

```text
Chip 1 está probado en origen SmartPyme como bloque candidato: cálculo determinístico → evaluación patológica → reporte diagnóstico.
```

## Prueba mínima requerida

La prueba que define si la lógica funciona es:

```text
Fixture de entrada
→ ejecutar Chip 1
→ verificar FormulaResult
→ verificar PathologyFinding
→ verificar DiagnosticReport
→ verificar estado final PASS/BLOCKED/PARTIAL
→ verificar trazabilidad
```

Si cualquier pin no acopla:

```text
PIN_MISMATCH
```

Si cualquier nodo requiere interpretación externa de Hermes/ChatGPT:

```text
NO_VALID_SYSTEM_OUTPUT
```
