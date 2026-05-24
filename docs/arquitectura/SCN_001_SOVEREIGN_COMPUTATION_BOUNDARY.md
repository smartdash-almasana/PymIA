# SCN-001 — Sovereign Computation Boundary

Estado: DRAFT  
Ámbito: Hermes ↔ PymIA  
Tipo: Documento rector de arquitectura  
Fecha: 2026-05-24

---

## 1. Propósito

Este documento fija la frontera de soberanía computacional entre Hermes y PymIA.

No implementa runtime.  
No habilita producción.  
No habilita MCP-3.  
No habilita Telegram real.  
No crea nuevas tools.  
No autoriza cambios de configuración sensible.

Su función es establecer el contrato conceptual mínimo para que Hermes y PymIA puedan convivir sin contaminación epistemológica.

---

## 2. Tesis central

La arquitectura separa agencia de autoridad computacional.

```text
Hermes = agencia / recolección / conversación / orquestación.
PymIA = autoridad computacional / evidencia / cálculo / validación / findings.
```

Hermes puede explorar el mundo.

PymIA decide qué significa.

---

## 3. Problema que resuelve

Un agente conversacional flexible puede recolectar información, operar canales, llamar herramientas y sostener contexto.

Ese mismo poder lo vuelve peligroso si empieza a:

- generar hallazgos propios;
- reinterpretar resultados del kernel;
- diagnosticar sin evidencia;
- persistir memoria clínica;
- crear computabilidad paralela;
- convertir outputs de PymIA en skills o reglas propias;
- saltarse la frontera MCP/contratos.

La soberanía no puede depender de prompts o instrucciones blandas.

Debe depender de frontera técnica, contratos, validación, auditoría y comportamiento fail-closed.

---

## 4. Principio arquitectónico

```text
Hermes transporta intención, contexto y evidencia candidata.
PymIA produce verdad computacional auditada.
```

La conversación no es fuente de verdad soberana.

La evidencia validada, los cálculos, las patologías, los findings y el `OperationalAuditResult` pertenecen a PymIA.

---

## 5. Regla fundamental de entrada

Todo input externo debe entrar como `EvidenceCandidate`.

Incluye:

- mensajes del usuario;
- archivos;
- Excel;
- PDFs;
- scraping;
- deep search;
- APIs externas;
- Telegram;
- datos recolectados por Hermes;
- datos cargados por el dueño.

Regla:

```text
EvidenceCandidate no es Finding.
```

Hermes puede recolectar y estructurar candidatos.

Hermes no puede validar soberanamente ni convertir evidencia candidata en hallazgo.

---

## 6. Regla fundamental de salida

La salida soberana de PymIA es `OperationalAuditResult`.

Un resultado puede contener:

- estado;
- findings;
- evidencia usada;
- evidencia faltante;
- severidad;
- próximos pasos permitidos;
- restricciones de renderizado;
- firma o marca soberana.

Regla:

```text
Nada sale como finding si no fue producido por PymIA.
```

Hermes puede renderizar la salida permitida.

Hermes no puede modificar, completar, reinterpretar ni expandir findings.

---

## 7. Hermes

Hermes cumple funciones de agencia externa:

- conversación;
- recepción;
- recolección de datos;
- scraping;
- deep search;
- coordinación de tools permitidas;
- contacto con canales;
- transporte de evidencia candidata;
- renderizado de respuestas autorizadas.

Hermes no tiene autoridad para:

- diagnosticar;
- crear findings;
- emitir verdad operacional;
- calcular resultados soberanos;
- persistir memoria clínica;
- modificar resultados de PymIA;
- llamar al kernel por fuera de contratos;
- operar como agente generalista paralelo a PymIA.

---

## 8. PymIA

PymIA conserva autoridad computacional.

Responsabilidades:

- validar evidencia;
- calcular;
- ejecutar fórmulas;
- evaluar patologías;
- producir findings;
- construir `OperationalAuditResult`;
- preservar trazabilidad;
- operar fail-closed si falta evidencia;
- mantener memoria computacional/auditada.

PymIA no delega soberanía en Hermes.

---

## 9. Boundary Layer

La frontera Hermes ↔ PymIA debe operar mediante una capa contractual.

Funciones mínimas esperadas:

- validar input;
- exigir schemas;
- convertir entradas externas en `EvidenceCandidate`;
- impedir findings generados por Hermes;
- exigir salida tipo `OperationalAuditResult`;
- restringir renderizado;
- registrar trazabilidad;
- aplicar policy;
- bloquear ejecución no autorizada;
- fallar cerrado.

Este documento no implementa esa capa.

La definición de diseño queda reservada para `SCN-002_CONTRACT_VALIDATION_LAYER_DESIGN.md`.

---

## 10. Memory Sovereignty

La memoria debe separarse.

### Hermes puede recordar

- contexto conversacional;
- estado de canal;
- preferencias operativas no clínicas;
- workflow de recolección;
- referencias a resultados PymIA.

### Hermes no puede recordar como verdad

- findings;
- reglas clínicas;
- fórmulas soberanas;
- lógica interna del kernel;
- razonamiento computacional;
- taxonomías validadas como memoria propia;
- outputs PymIA transformados en skills.

### PymIA conserva

- evidencia validada;
- findings;
- resultados auditados;
- trazas;
- taxonomías;
- fórmulas;
- estado computacional del caso.

Regla:

```text
Hermes nunca persiste findings.
```

---

## 11. Output Minimization

PymIA debe entregar a Hermes solo lo necesario para continuar la conversación o renderizar respuesta.

No debe exponer innecesariamente:

- razonamiento interno;
- árboles de decisión internos;
- pesos;
- heurísticas sensibles;
- reglas completas si no son necesarias;
- trazas computacionales que permitan reconstruir el kernel.

Hermes recibe resultado autorizado, no computabilidad interna.

---

## 12. Fail-Closed

Si falta evidencia, falla el kernel, falta firma, falta contrato o hay conflicto de policy, Hermes no improvisa.

Respuesta permitida:

```text
No puedo validar esa información con evidencia suficiente en este momento.
El estado debe permanecer pendiente o bloqueado hasta que PymIA pueda procesarlo.
```

Respuestas prohibidas:

- diagnósticos probables sin evidencia;
- inferencias de margen/caja/stock no producidas por PymIA;
- recomendaciones fuertes sin `OperationalAuditResult`;
- sustitución del kernel por razonamiento conversacional.

---

## 13. Violaciones de soberanía

Se considera violación si Hermes:

- genera findings;
- diagnostica;
- recalcula resultados PymIA;
- altera `OperationalAuditResult`;
- persiste memoria clínica;
- convierte evidencia candidata en verdad;
- crea skills con lógica soberana;
- salta la Boundary Layer;
- usa Telegram real para pruebas no autorizadas;
- opera MCP-3 sin aprobación explícita;
- toca producción o configuración sensible.

---

## 14. Relación con documentos existentes

Este documento no reemplaza ADRs vigentes.

Debe leerse junto con:

- `docs/adr/ADR-008-hermes-mcp-client-pymia-mcp-server.md`;
- `docs/hermes/HERMES_LOCAL_INSTANCE_INVENTORY.md`;
- `docs/hermes/HERMES_CONFIG_HARDENING_PLAN.md`;
- `docs/hermes/HERMES_CONFIG_HARDENING_PLAN_REVIEW.md`;
- `docs/epistemologia/modelo-verdad-soberania.md`;
- `docs/contracts/scn/GLOSSARY.md`.

Si hay conflicto entre documentos históricos y esta frontera SCN, debe abrirse auditoría documental antes de implementar.

---

## 15. Estado de autorización

Permitido por este documento:

- discutir arquitectura;
- auditar documentación;
- diseñar contratos;
- crear schemas conceptuales;
- preparar sandbox futuro.

No permitido por este documento:

- ejecutar MCP-3;
- activar Telegram real;
- tocar producción;
- modificar configuración sensible;
- crear plugins reales;
- crear nuevas tools productivas;
- convertir Hermes en autoridad computacional.

---

## 16. Decisión

Se adopta la frontera SCN:

```text
Hermes tiene agencia.
PymIA tiene autoridad computacional.
EvidenceCandidate es el input externo válido.
OperationalAuditResult es la salida soberana.
Hermes no produce findings.
Hermes no persiste memoria clínica.
Fail-closed es obligatorio.
```

---

## 17. Próximo documento

El siguiente documento habilitado es:

```text
docs/contracts/scn/GLOSSARY.md
```

Después de cerrar glosario, podrá diseñarse:

```text
docs/arquitectura/SCN_002_CONTRACT_VALIDATION_LAYER_DESIGN.md
```

SCN-002 no debe escribirse antes de cerrar SCN-001 y el glosario.
