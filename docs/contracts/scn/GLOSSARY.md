# Glosario SCN / Domain Packs — PymIA

Estado: DRAFT  
Ámbito: SCN / Hermes ↔ PymIA / Domain Packs  
Tipo: Glosario operativo

---

## Propósito

Este glosario fija el lenguaje mínimo para la arquitectura de Soberanía Computacional de Núcleo.

No implementa runtime.  
No habilita producción.  
No habilita MCP-3.  
No habilita Telegram real.  
No crea plugins reales.

---

## Domain Pack

Paquete versionado de conocimiento computable específico de un rubro o área operativa.

Un Domain Pack puede contener taxonomías, patologías, fórmulas, evidence requirements, benchmarks, plantillas de hallazgos y preguntas de anamnesis específica.

Un Domain Pack no es un agente autónomo.

---

## Taxonomía

Clasificación estructurada del dominio: rubro, subtipo, operación, entidades y relaciones.

Sirve para ordenar el lenguaje del dominio y seleccionar evidencia, reglas o fórmulas aplicables.

---

## Patología

Problema operativo recurrente detectable mediante evidencia.

Ejemplos:

- costos no actualizados;
- margen erosionado;
- stock desfasado;
- conciliación incompleta;
- carga manual crónica.

Una patología no debe declararse como confirmada sin evidencia suficiente.

---

## Fórmula

Cálculo explícito, versionado y auditable utilizado por el kernel para producir señales o hallazgos.

Una fórmula debe declarar inputs, outputs, unidades, supuestos y condiciones de bloqueo.

---

## Evidence Requirement

Conjunto mínimo de evidencia necesario para ejecutar una fórmula, validar una patología o emitir un hallazgo.

Si no se cumple el evidence requirement, el sistema debe operar como `pending_data`, `blocked` o equivalente fail-closed.

---

## Finding

Hallazgo soberano producido por PymIA.

No puede ser generado por Hermes.

Un finding debe estar asociado a evidencia, cálculo, validación o regla computacional auditable.

---

## EvidenceCandidate

Dato, archivo, texto, scraping o input externo recolectado por Hermes o por el usuario antes de ser validado por PymIA.

Ejemplos:

- mensaje del dueño;
- archivo Excel;
- PDF;
- dato de API;
- resultado de scraping;
- referencia externa;
- captura o documento cargado por canal.

Regla:

```text
EvidenceCandidate no es Finding.
```

---

## OperationalAuditResult

Salida soberana del kernel PymIA con findings, evidencia usada, evidencia faltante, estado y marca/firma soberana.

Debe ser la unidad principal de consumo para Hermes cuando se comunica un resultado computacional.

---

## Boundary Layer

Frontera contractual que valida inputs, outputs, políticas, firmas y permisos entre Hermes y PymIA.

Debe impedir que Hermes:

- llame al kernel fuera de contrato;
- produzca findings;
- reinterprete resultados;
- persista memoria clínica;
- convierta metadata en verdad computacional.

---

## Memory Sovereignty

Separación estricta entre memoria operativa de Hermes y memoria computacional/auditada de PymIA.

Hermes puede guardar contexto conversacional y referencias.

PymIA conserva evidencia validada, findings, cálculos y resultados auditados.

---

## Output Minimization

Principio por el cual PymIA entrega a Hermes solo lo necesario para renderizar o continuar la conversación, sin exponer razonamiento interno ni computabilidad soberana innecesaria.

---

## Computable Knowledge

Conocimiento expresado en forma de:

- taxonomías;
- fórmulas;
- reglas;
- umbrales;
- contratos ejecutables;
- estructuras auditables.

Debe poder ser versionado, revisado y probado.

---

## Plugin gobernado

Extensión controlada del kernel que aporta conocimiento específico sin autonomía propia ni autoridad soberana.

Un plugin gobernado no puede:

- abrir tools externas por sí mismo;
- decidir fuera del kernel;
- alterar findings;
- persistir memoria clínica;
- saltarse contratos.

---

## Versión de dominio

Identificador de versión de un Domain Pack.

Ejemplos:

```text
textil.v1
gastronomia.v1
stock.v1
conciliacion.v1
```

La versión permite auditar qué conocimiento estaba activo cuando se produjo un resultado.

---

## Firma soberana

Marca verificable de que un resultado fue generado por PymIA bajo contrato, evidencia y versión determinada.

Puede comenzar como firma estructural/documental y evolucionar a firma criptográfica si la arquitectura lo requiere.

---

## Kernel

Núcleo computacional soberano de PymIA.

Ejecuta reglas, fórmulas, validaciones y produce resultados firmados/auditados.

---

## Hermes

Agente/orquestador externo.

Recolecta, conversa, transporta evidencia candidata y renderiza respuestas autorizadas.

No produce verdad computacional.

---

## Fail-Closed

Comportamiento obligatorio ante falta de evidencia, error de contrato, ausencia de firma, conflicto de policy o falla del kernel.

El sistema debe bloquear, pedir evidencia o marcar pendiente.

No debe improvisar diagnóstico.

---

## Anamnesis específica

Preguntas propias del dominio para completar contexto operativo antes de diagnosticar.

Debe usarse para pedir evidencia concreta, no para reemplazar cálculo o validación soberana.

---

## Benchmark

Referencia externa o interna usada para comparar desempeño, costos, márgenes, tiempos o ratios.

Un benchmark puede orientar análisis, pero no reemplaza evidencia del tenant.

---

## Regla de mantenimiento del glosario

Todo término nuevo introducido por un Domain Pack, contrato SCN o documento de frontera debe agregarse a este glosario o declarar explícitamente su glosario local.

Si un término entra en conflicto con este glosario, debe abrirse auditoría documental antes de implementación.
