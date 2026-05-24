# HERMES_LOCAL_SCN_SANDBOX_PLAN

Estado: DRAFT PLAN — NO EXECUTION  
Ámbito: Hermes local / SCN / PymIA  
Tipo: Plan documental de sandbox  
Fecha: 2026-05-24

---

## 1. Propósito

Diseñar un sandbox local separado para validar la convivencia Hermes/PymIA bajo SCN sin tocar la instancia Hermes real ni su integración Telegram.

Este documento no ejecuta Hermes.  
No modifica configuración.  
No crea runtime.  
No habilita Telegram real.  
No habilita MCP-3.  
No habilita producción.

---

## 2. Contexto

Existe una instalación local de Hermes inventariada como activo sensible.

Referencia:

```text
docs/hermes/HERMES_LOCAL_INSTANCE_INVENTORY.md
```

La instancia local existente puede contener:

- configuración Telegram real;
- tokens o secretos en entorno local;
- memoria persistente;
- skills previas;
- logs;
- estado operativo no controlado por SCN.

Por lo tanto, no debe usarse directamente como entorno de prueba SCN.

---

## 3. Regla base

```text
Hermes real existente = activo sensible.
Hermes SCN sandbox = entorno separado, descartable y sin secretos reales.
```

El sandbox puede reutilizar conocimiento de instalación, estructura y versión.

No puede reutilizar:

- tokens reales;
- Telegram real;
- memoria real;
- skills reales;
- logs reales;
- `.env` real;
- estado persistente de la instancia existente.

---

## 4. Objetivo del sandbox

El sandbox debe permitir probar, en fase futura, que Hermes puede:

- recolectar evidencia candidata;
- enviar `EvidenceCandidate`;
- respetar `RuntimePolicy`;
- recibir `RenderContract`;
- renderizar sin reinterpretar;
- fallar cerrado;
- no producir findings.

No debe permitir:

- autonomía libre;
- `--yolo`;
- loops `forward`/`goal`;
- Telegram real;
- MCP-3;
- acceso a producción;
- persistencia de memoria clínica;
- ejecución de tools no autorizadas.

---

## 5. Ubicaciones propuestas

Raíz de trabajo:

```text
E:\BuenosPasos\smartbridge
```

Checkout Hermes real inventariado:

```text
E:\BuenosPasos\smartbridge\hermes-agent
```

Sandbox SCN propuesto:

```text
E:\BuenosPasos\smartbridge\.tmp\hermes-scn-local
```

HERMES_HOME sandbox propuesto:

```text
E:\BuenosPasos\smartbridge\.tmp\hermes-scn-local\HERMES_HOME
```

Estas rutas son propuestas documentales. No crean carpetas ni ejecutan procesos.

---

## 6. Reglas de aislamiento

El sandbox debe cumplir:

- `HERMES_HOME` separado;
- sin `.env` real;
- sin token Telegram real;
- sin chat IDs reales;
- sin allowed users reales;
- sin memory real;
- sin skills reales;
- sin logs reales;
- sin acceso a producción;
- sin escritura fuera del sandbox;
- sin ejecución autónoma no autorizada.

---

## 7. Configuración permitida futura

Solo se permitirá configuración sintética o redacted:

```text
TELEGRAM_BOT_TOKEN=<REDACTED_OR_DUMMY>
OPENROUTER_API_KEY=<REDACTED_OR_DUMMY>
HERMES_HOME=<SANDBOX_PATH>
```

Ningún secreto real debe copiarse al sandbox.

---

## 8. Tools permitidas futuras

En una fase posterior, la allowlist inicial debería limitarse a acciones SCN seguras:

- leer input sintético;
- producir `EvidenceCandidate`;
- validar schema local;
- escribir logs de auditoría sandbox;
- solicitar evaluación PymIA por contrato simulado;
- renderizar `RenderContract`.

No se permiten en el sandbox inicial:

- Telegram real;
- shell libre;
- filesystem amplio;
- red externa sin policy;
- escritura en repo principal;
- modificación de `.env`;
- generación de skills persistentes;
- llamadas MCP-3 productivas.

---

## 9. Relación con contratos SCN

El sandbox debe operar contra los contratos draft:

```text
docs/contracts/scn/evidence_candidate.schema.json
docs/contracts/scn/kernel_request.schema.json
docs/contracts/scn/operational_audit_result.scn.schema.json
docs/contracts/scn/render_contract.schema.json
docs/contracts/scn/runtime_policy.example.yaml
```

Reglas:

- Hermes produce `EvidenceCandidate`.
- Boundary Layer futura produce `KernelRequest`.
- PymIA produce `OperationalAuditResult`.
- Output Gateway produce `RenderContract`.
- Hermes renderiza, no reinterpreta.

---

## 10. Casos de prueba futuros

Cuando se autorice ejecución sandbox, los casos mínimos serán:

1. Input externo sintético → `EvidenceCandidate` válido.
2. Input inválido → bloqueo fail-closed.
3. `OperationalAuditResult` válido → `RenderContract` válido.
4. `forbidden_inferences` se propagan.
5. Output sin sovereign mark → bloqueado.
6. Hermes intenta crear finding → bloqueado.
7. PymIA devuelve `pending_data` → Hermes no diagnostica.
8. PymIA devuelve `blocked` → Hermes comunica bloqueo.
9. Audit trail sandbox preservado.
10. No escritura fuera de sandbox.

---

## 11. Prohibiciones explícitas

Este plan no autoriza:

- ejecutar Hermes;
- usar `--yolo`;
- iniciar loops `forward`/`goal`;
- tocar Telegram real;
- usar tokens reales;
- copiar `.env` real;
- reutilizar memoria real;
- reutilizar skills reales;
- ejecutar MCP-3;
- tocar producción;
- modificar servicios;
- crear systemd;
- abrir túneles;
- crear nuevas tools productivas;
- implementar Boundary Layer runtime.

---

## 12. Criterios de aceptación antes de ejecución

Antes de cualquier ejecución sandbox debe existir:

- revisión documental aprobada del plan;
- repo limpio;
- `HERMES_HOME` sandbox definido;
- configuración dummy o redacted;
- allowlist de tools;
- denylist de acciones peligrosas;
- política fail-closed;
- logs sandbox;
- contratos SCN disponibles;
- autorización explícita del usuario para ejecutar.

---

## 13. Relación documental

Este plan depende de:

```text
docs/hermes/HERMES_LOCAL_INSTANCE_INVENTORY.md
docs/arquitectura/SCN_001_SOVEREIGN_COMPUTATION_BOUNDARY.md
docs/arquitectura/SCN_002_CONTRACT_VALIDATION_LAYER_DESIGN.md
docs/contracts/scn/GLOSSARY.md
docs/contracts/scn/runtime_policy.example.yaml
```

Si cualquier documento superior cambia, este plan debe re-auditarse.

---

## 14. Decisión

Se define que Hermes local existente no será usado directamente para pruebas SCN.

Toda prueba futura deberá ocurrir en un sandbox separado, descartable, sin secretos reales y con policy fail-closed.

---

## 15. Próximo paso autorizado

Después de aprobar este plan, el siguiente bloque recomendado es:

```text
SCN_TEST_FRONTIER_PLAN.md
```

Ese documento deberá definir tests futuros sin ejecutarlos todavía.
