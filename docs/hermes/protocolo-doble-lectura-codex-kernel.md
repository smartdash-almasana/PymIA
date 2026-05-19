# Protocolo de doble lectura — Codex + ChatGPT para armado de kernel PymIA

## Estado

Documento operativo.

A partir de este punto, ninguna decisión de migración de kernel debe ejecutarse solo por criterio conversacional.

Regla:

```text
ChatGPT propone.
Codex valida o refuta contra código local.
Solo después se migra.
```

---

## Motivo

El plano lógico del kernel sirve como arquitectura de señales, pero el armado real del kernel exige doble lectura:

```text
1. lectura arquitectónica;
2. lectura de código ejecutable;
3. validación por tests;
4. decisión de migración mínima.
```

La autoridad final no es la conversación.

La autoridad final es:

```text
código local + tests + trazabilidad.
```

---

## Roles

## ChatGPT

Función:

```text
- ordenar arquitectura;
- identificar chips lógicos;
- definir pines, estados y condiciones de acople;
- proponer migración mínima;
- documentar decisión y evidencia.
```

Límite:

```text
No declarar funcional algo que no esté probado.
No migrar por archivo suelto.
No reemplazar tests por inferencia.
```

## Codex

Función:

```text
- leer código local real;
- verificar imports y dependencias;
- detectar acoples ocultos;
- ejecutar o proponer tests;
- refutar migraciones que arrastren factory/jobs/orchestration;
- adaptar código de SmartPyme a PymIA si corresponde.
```

Límite:

```text
No cambiar arquitectura sin registrar motivo.
No introducir app.* en PymIA.
No traer jobs, workflows, factory ni orchestration al kernel.
```

---

## Decisión actual sometida a doble lectura

Decisión propuesta:

```text
Pasar de documentación estratégica a armado de kernel.
```

Modo:

```text
Rescatar chips probados de SmartPyme, no archivos sueltos.
```

Primer chip candidato:

```text
FormulaEngineService
→ PathologyEngineService
→ DiagnosticReportService
```

Evidencia en origen SmartPyme:

```text
FormulaEngineService: 4 passed.
PathologyEngineService: 4 passed.
DiagnosticReportService: 3 passed.
```

Frontera:

```text
Probado en SmartPyme: SÍ.
Migrado a PymIA: NO.
Integrado al pipeline PymIA: NO.
```

---

## Regla de doble lectura antes de migrar

Para cada chip:

```text
1. ChatGPT define chip lógico y pines.
2. Codex lee archivos fuente y tests de SmartPyme.
3. Codex confirma dependencias reales.
4. Codex identifica qué se puede portar sin app.*, jobs, factory u orchestration.
5. ChatGPT documenta veredicto.
6. Se migra solo el mínimo.
7. Se ejecutan tests en PymIA.
8. Si los tests pasan, el chip queda aceptado.
```

---

## Criterios de aceptación

Un chip puede entrar a PymIA solo si:

```text
- tiene tests de origen verdes;
- no depende de runtime de SmartPyme;
- no introduce jobs/workflows/orchestration;
- no depende de Hermes para decidir;
- tiene estados fail-closed;
- puede emitir BLOCKED, PARTIAL o PASS;
- preserva trazabilidad mínima.
```

---

## Criterios de rechazo

Un chip se rechaza o posterga si:

```text
- requiere app.* sin adaptación limpia;
- arrastra repositorios, colas o factory;
- necesita interpretación LLM para completar datos;
- no tiene tests;
- no puede bloquear con causa explícita;
- genera outputs no trazables;
- mezcla UI/Hermes con kernel.
```

---

## Prompt operativo para Codex

```text
Estás en E:\BuenosPasos\smartbridge.

Objetivo: segunda lectura técnica antes de migrar Chip 1 desde SmartPyme a PymIA.

Lee estos archivos de origen:
- SmartPyme/app/contracts/formula_contract.py
- SmartPyme/app/services/formula_engine_service.py
- SmartPyme/app/contracts/pathology_contract.py
- SmartPyme/app/services/pathology_engine_service.py
- SmartPyme/app/services/diagnostic_report_service.py

Lee estos tests de origen:
- SmartPyme/tests/test_formula_engine_service_ts_009b.py
- SmartPyme/tests/test_pathology_engine_service_ts_010b.py
- SmartPyme/tests/services/test_diagnostic_report_service.py

Verifica:
1. dependencias reales;
2. imports app.* a adaptar;
3. riesgo de arrastrar jobs/factory/orchestration;
4. contratos mínimos requeridos en PymIA;
5. tests mínimos a portar;
6. si Chip 1 puede migrarse sin tocar Hermes.

No modifiques código todavía.
Devuelve un veredicto:
- APTO PARA MIGRACIÓN MÍNIMA;
- APTO CON PODA;
- NO APTO;
con razones concretas por archivo.
```

---

## Decisión vigente

```text
Seguimos con armado de kernel, pero bajo doble lectura.
```

No se avanza a migración hasta que Codex confirme o refute Chip 1.

---

## Recepción de segunda lectura y corrección contra código físico

Codex emitió veredicto:

```text
APTO PARA MIGRACIÓN MÍNIMA
```

Ese veredicto es útil, pero no debe aceptarse sin corrección porque al contrastar contra archivos físicos aparecen diferencias relevantes:

```text
1. FormulaEngineService no importa BusinessRuleException en el archivo leído.
2. PathologyEngineService no depende solo de contratos: depende de app.catalog.pathologies y app.services.pathology_evaluators.
3. DiagnosticReportService depende de operational_case_contract, exige job_id y emite proposed_next_actions / owner_question de autorización.
4. Los tests leídos anteriormente usan pytest simple; no se verificó que usen unittest/mock como dijo la segunda lectura.
```

Veredicto corregido:

```text
APTO CON PODA, no APTO directo.
```

Poda mínima requerida:

```text
- adaptar imports app.* a pymia.*;
- decidir si se migran o reescriben pathologies catalog y pathology_evaluators;
- eliminar o aislar job_id del contrato de reporte para PymIA si no pertenece al kernel;
- eliminar proposed_next_actions / owner_question si implican autorización o capa owner/Hermes;
- portar solo tests que validen cálculo, patología y reporte fail-closed;
- no introducir jobs, autorización, factory ni orchestration.
```

Decisión actualizada:

```text
Chip 1 sigue siendo candidato fuerte, pero como migración podada o reescritura mínima en PymIA.
No copiar archivos tal cual.
```

---

## Corrección de sesgo del prompt

El prompt anterior queda marcado como sesgado porque presupone que el objetivo es migrar Chip 1.

La doble lectura debe formularse como auditoría neutral, no como pedido de confirmación.

Regla corregida:

```text
Codex no debe validar una decisión ya tomada.
Codex debe auditar si la decisión corresponde.
```

Prompt neutral resumido:

```text
Analizá si los archivos de fórmula, patología y reporte forman realmente un chip lógico útil para PymIA.
No asumas que deben migrarse.
Buscá dependencias ocultas, acoples faltantes, imports problemáticos y razones para rechazar, podar o reescribir.
No modifiques código.
Devolvé uno de estos veredictos: APTO, APTO CON PODA, REESCRIBIR EN PYMIA, NO APTO.
```

---

## Lectura Kiro

Kiro emitió veredicto:

```text
MIGRAR CON PODA
```

Puntos confirmados:

```text
FormulaInput → FormulaEngineService → FormulaResult: compatible.
FormulaResult → PathologyEngineService → PathologyFinding: compatible.
PathologyFinding → DiagnosticReportService: no compatible directo; requiere adaptador.
```

Bloqueantes confirmados:

```text
- job_id;
- owner_question;
- proposed_next_actions;
- diferencia de tipo entre PathologyFinding y FindingRecord;
- necesidad de adaptador explícito.
```

Decisión convergente:

```text
Codex identificó utilidad general.
ChatGPT corrigió a APTO CON PODA.
Kiro confirmó MIGRAR CON PODA.
```

Decisión final operativa:

```text
Migrar/recrear Chip 1 en PymIA con poda y adaptador.
No copiar DiagnosticReportService tal cual.
```

---

## Lectura Qwen

Qwen converge con la decisión Kiro/ChatGPT:

```text
MIGRAR CON PODA
```

Aporte adicional detectado:

```text
Propone evaluar una consolidación de contratos mínimos del chip en un contrato kernel_v1.py.
```

Contraste:

```text
La idea puede servir para evitar dispersión contractual, pero no debe aceptarse automáticamente.
PymIA ya tiene estructura existente en pymia/contracts/ y servicios separados.
La decisión de unificar en kernel_v1.py requiere contraste contra imports, tests y legibilidad del dominio.
```

Decisión mantenida:

```text
Migrar/recrear Chip 1 con poda y adaptador.
No copiar directo.
No consolidar contratos en kernel_v1.py sin prueba previa.
```
