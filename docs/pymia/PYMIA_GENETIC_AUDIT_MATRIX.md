# PymIA Genetic Audit Matrix

Fecha: 2026-06-11
Estado: ANALYTIC_MATRIX
Origen: destilado de `AUDITORIA_GENETICA_PYMIA_2026_06_11.md`
Uso: emular auditorias globales de fidelidad metodologica, tecnica y operacional.

---

## 1. Proposito

Esta matriz conserva la logica de auditoria genetica como herramienta de analisis global.

No reemplaza:

- `AGENTS.md`;
- `ARCHITECTURE_GUARDRAILS.md`;
- `PYMIA_DEVELOPMENT_METHOD.md`;
- ADRs;
- CapabilitySpecs;
- ModuleContracts;
- TaskSpecs;
- checkpoints.

No autoriza runtime, canal externo, marketplace, DB, Telegram, Hermes productivo, ERP, PDF, graph productivo ni LLM dentro de PymIA.

Su funcion es evaluar si un cambio, hito o ciclo conserva la identidad de PymIA / SmartPyme y reduce ambiguedad operacional.

---

## 2. Modo de Uso

Usar esta matriz cuando el usuario pida:

- auditoria global;
- auditoria genetica;
- conciencia de producto;
- integralidad tecnica;
- evaluacion de deriva;
- evaluacion de avance real vs documentacion;
- decision de proximo paso metodologico.

La auditoria debe separar:

- hechos certificados;
- hipotesis;
- gaps;
- riesgos;
- proximo paso metodologico.

No declarar `PASS` sin evidencia observada o explicitamente reportada.

---

## 3. Preguntas Nucleares

### A. Soberania del dueno

1. El dueno conserva autoridad sobre el significado operacional?
2. El sistema pide confirmacion cuando interpreta una narrativa?
3. Se evita convertir texto libre en verdad operacional?
4. El flujo permite correccion, rechazo o bloqueo?
5. El resultado owner-facing respeta lo que el dueno realmente confirmo?

### B. Honestidad epistemologica

1. Esta separado lo narrado, lo interpretado, lo evidenciado y lo diagnosticado?
2. El sistema dice `BLOCKED`, `NEEDS_EVIDENCE` o `GAP` cuando corresponde?
3. Hay findings sin evidencia suficiente?
4. Se evita promover evidencia, learning o arquitectura entre capas automaticamente?
5. Existe alguna pieza que use LLM o inferencia como core computacional?

### C. Computabilidad gobernada

1. La decision se basa en contratos, datos estructurados o funciones deterministicas?
2. Las entradas y salidas estan validadas?
3. Hay hashes, IDs o trazas que permitan replay o auditoria?
4. Las formulas o reglas usadas estan gobernadas?
5. Aparece logica monolitica o lateral no cubierta por contrato?

### D. Evidencia antes de diagnostico

1. El cambio impide diagnosticar sin evidencia?
2. La evidencia faltante queda visible y accionable?
3. La suficiencia de evidencia se calcula o se infiere informalmente?
4. El owner-facing report comunica limites?
5. Los tests cubren escenarios insuficientes o bloqueados?

### E. Trazabilidad contractual

1. El cambio deriva de la cadena metodologica correcta?
2. Existe contrato o documento habilitante para el nivel tocado?
3. La evidencia de validacion esta registrada o reportada?
4. El commit es focal?
5. Hay documentacion que promete capacidades no implementadas?

### F. Integracion sistemica

1. La pieza nueva conecta un circuito real o queda flotante?
2. Reduce pasos manuales o ambiguedad entre piezas?
3. Conecta intake, evidencia, computo, salida y trazabilidad?
4. Evita abrir frentes externos innecesarios?
5. Puede ejecutarse o verificarse end-to-end?

### G. Fidelidad al servicio asistido realista

1. El avance acerca al servicio asistido real sin llamarlo producto prematuramente?
2. Mejora la capacidad de recibir caos real de una PyME?
3. Mejora la capacidad de pedir datos o significado operacional faltante?
4. Mejora la salida accionable para el dueno?
5. Evita confundir sandbox, protocolo, piloto y servicio real?

### H. Antideriva y simplicidad operacional

1. El cambio evita documentacion especulativa?
2. Hay menos ambiguedad despues del cambio?
3. Se evita abrir mas de un frente?
4. La solucion es mas simple que la complejidad que introduce?
5. Se preservan limites de alcance y lenguaje?

### I. Separacion de capas

1. Execution, Evidence, Learning y Architecture siguen separados?
2. Un test o comando se presenta solo como evidencia, no como arquitectura?
3. Un checkpoint no se convierte automaticamente en LearningMemory?
4. Un documento no se trata como capacidad real sin test y evidencia?
5. El canal conversacional queda separado del core computacional?

### J. Direccion estrategica

1. El cambio acerca un slice observable?
2. Reduce distancia entre aparato metodologico y utilidad operacional?
3. Evita expansion horizontal sin integracion?
4. El proximo paso unico es claro?
5. El trabajo preserva el rumbo: servicio asistido, evidencia, soberania del dueno?

---

## 4. Coeficientes

Cada dimension se puntua de 0 a 10.

| Dimension | Peso |
|---|---:|
| A. Soberania del dueno | 12% |
| B. Honestidad epistemologica | 12% |
| C. Computabilidad gobernada | 10% |
| D. Evidencia antes de diagnostico | 12% |
| E. Trazabilidad contractual | 10% |
| F. Integracion sistemica | 10% |
| G. Fidelidad al servicio asistido realista | 12% |
| H. Antideriva y simplicidad operacional | 8% |
| I. Separacion de capas | 7% |
| J. Direccion estrategica | 7% |

Calculo:

```text
coeficiente_genetico = sum(puntaje_dimension * peso_dimension)
```

Ejemplo:

```text
8.5 * 0.12 + 9.0 * 0.12 + ... = 7.51 / 10
```

---

## 5. Escala de Veredicto

| Coeficiente | Veredicto |
|---:|---|
| 9.00 - 10.00 | EXCELENTE_FIDELIDAD |
| 8.50 - 8.99 | ALTA_FIDELIDAD |
| 7.50 - 8.49 | BUENA_FIDELIDAD_CON_GAPS |
| 6.50 - 7.49 | FIDELIDAD_PARCIAL |
| 5.00 - 6.49 | DERIVA_RELEVANTE |
| 0.00 - 4.99 | DERIVA_CRITICA |

Para auditorias de commit o slice tecnico, se puede usar:

```text
VEREDICTO: PASS | PASS_WITH_NOTES | BLOCKED
COEFICIENTE_DE_INTEGRALIDAD: 0-10
```

Mapeo sugerido:

| Resultado | Criterio |
|---|---|
| PASS | Coeficiente >= 8.0 y sin bloqueo metodologico o tecnico |
| PASS_WITH_NOTES | Coeficiente >= 6.5 con gaps no bloqueantes |
| BLOCKED | Bloqueo de evidencia, contrato, frontera, dependencia lateral o ambiguedad critica |

---

## 6. Penalizadores

Restar criterio cualitativo o bajar dimensiones relacionadas cuando aparezca:

- findings sin evidencia;
- LLM dentro del core PymIA;
- runtime externo abierto sin autorizacion;
- Telegram, Hermes, marketplace, DB, ERP, PDF o graph activados fuera de alcance;
- documentos que prometen capacidades no implementadas;
- tests que solo instancian objetos sin probar conexion real;
- piezas persistidas sin relacion con intake, evidencia o salida;
- owner-facing report que sobrediagnostica;
- lenguaje de producto para protocolo, sandbox o piloto;
- duplicacion de registros sin valor de trazabilidad.

---

## 7. Bonificadores

Subir dimensiones relacionadas cuando el cambio:

- conecta un spine end-to-end verificable;
- persiste IDs y hashes utiles;
- hace visible evidencia faltante;
- produce `BLOCKED_ACTIONABLE` honestamente;
- reduce una frontera ambigua;
- mantiene congelados eventos externos y runtime;
- incluye test end-to-end real;
- mantiene salida owner-facing sobria;
- declara limites explicitos;
- deja un proximo paso unico.

---

## 8. Plantilla de Auditoria Global

```text
VEREDICTO_GENERAL:
COEFICIENTE_GENETICO: X/10

REPO_STATE:
- Branch:
- HEAD:
- Status:

FUENTES_LEIDAS:
- ...

HECHOS_CERTIFICADOS:
- ...

HIPOTESIS:
- ...

GAPS:
- ...

PUNTAJES:
- A. Soberania del dueno: X/10
- B. Honestidad epistemologica: X/10
- C. Computabilidad gobernada: X/10
- D. Evidencia antes de diagnostico: X/10
- E. Trazabilidad contractual: X/10
- F. Integracion sistemica: X/10
- G. Fidelidad al servicio asistido realista: X/10
- H. Antideriva y simplicidad operacional: X/10
- I. Separacion de capas: X/10
- J. Direccion estrategica: X/10

RAZON:
- Maximo 5 lineas.

HALLAZGOS:
- Maximo 10 bullets.

NO_CERTIFICADO:
- ...

PROXIMO_PASO_UNICO:
- ...
```

---

## 9. Plantilla de Auditoria de Commit o Slice

```text
VEREDICTO: PASS | PASS_WITH_NOTES | BLOCKED
COEFICIENTE_DE_INTEGRALIDAD: X/10

RAZON:
Maximo 5 lineas.

HALLAZGOS:
- Maximo 5 bullets.

SI BLOCKED:
- Causa concreta:
- Archivo exacto:
- Fix minimo:
- Test focal a repetir:

SI PASS O PASS_WITH_NOTES:
- Proximo paso unico recomendado:
```

Preguntas focales para commit o slice:

1. La pieza agrega integralidad o queda flotante?
2. Los IDs relevantes quedan ligados correctamente?
3. Los hashes son deterministas y utiles?
4. Los estados son honestos respecto de evidencia y alcance?
5. La salida owner-facing informa sin sobrediagnosticar?
6. El test prueba conexion real o solo objetos?
7. Se introdujo dependencia lateral innecesaria?
8. Se mantienen congelados eventos externos, marketplace y runtime?
9. Hay duplicacion innecesaria con registros existentes?
10. El slice aumenta o reduce ambiguedad operacional?

---

## 10. Stop Conditions

Bloquear la auditoria o el avance si:

- falta la fuente arquitectonica aplicable;
- se intenta declarar capacidad real sin test y evidencia;
- el cambio requiere ADR y no existe;
- el cambio mezcla capas;
- el repo esta sucio en archivos relacionados;
- se abre runtime externo sin autorizacion;
- se necesita LLM para una decision del core;
- se llama producto a un protocolo, sandbox, piloto o capability interna;
- el flujo no puede explicar intake, evidencia, computo, salida y trazabilidad.

---

## 11. Regla de Conciencia de Producto

La pregunta final de toda auditoria genetica debe ser:

```text
Despues de este cambio, una PyME real esta mas cerca de recibir ayuda honesta,
trazable y accionable, sin que PymIA invente evidencia ni sobreactue madurez?
```

Si la respuesta no es demostrable, el resultado maximo es `PASS_WITH_NOTES`.
