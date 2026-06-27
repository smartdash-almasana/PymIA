# SERVICE_1_AGENT_BOOTSTRAP

## Propósito

Este archivo es la puerta de entrada mínima para cualquier IA/agente que continúe el desarrollo de PymIA Servicio 1.

No es roadmap.
No es closeout.
No es TaskSpec.
No abre código.
No reemplaza al repo.

Su única función es evitar que una IA lea documentos históricos al azar y derive.

---

## 1. Leer primero

```text
OBLIGATORIO:
docs/producto/SERVICE_1_CURRENT_STATE_V1.md
```

Ese documento es la fuente canónica viva del estado actual de Servicio 1.

Si hay contradicción entre documentos:

```text
SERVICE_1_CURRENT_STATE_V1.md manda.
```

---

## 2. Orden de lectura recomendado

```text
1. SERVICE_1_CURRENT_STATE_V1.md
2. SERVICE_1_FULL_CLOSURE_RECTOR_V1.md
3. SERVICE_1_DEVELOPMENT_AUDIT_AND_COMPLETION_ROADMAP_V1.md
4. SERVICE_1_FIRST_AID_FAMILY_CLOSEOUT_V1.md
5. SERVICE_1_EXCEL_LAB_CLOSEOUT_V1.md
6. SERVICE_1_STAGE_4_EXCEL_FACTORY_CLOSEOUT_V1.md
```

No empezar por catálogos, traces, arqueologías o documentos antiguos.

---

## 3. Estado operativo resumido

```text
First Aid:
CLOSED_IN_SCOPE_RUNTIME

Excel Lab:
CLOSED_IN_SCOPE_RUNTIME

Factoría Excel:
CLOSED_IN_SCOPE_RUNTIME vía --run-factory

Servicio 1 full:
NOT_CLOSED

Pipeline full:
MISSING

CSV/PDF normalizado:
MISSING para CSV y PDF

Contabilidad/conciliaciones:
PARTIAL_SYNTHETIC_RUNTIME / CONTRACT / SANDBOX

FSM/LLM/Chatbot:
FROZEN_OR_MISSING
```

---

## 4. No tocar sin autorización explícita

```text
NO abrir chatbot.
NO abrir LLM adapter.
NO reactivar FSM congelada.
NO abrir pipeline full.
NO abrir Servicio 2.
NO agregar APIs externas.
NO agregar OCR.
NO agregar parser PDF.
NO tocar código sin TaskSpec.
NO mezclar docs + runtime + refactor en un mismo ciclo.
```

---

## 5. Regla de trabajo

```text
Una frontera por vez.
Un ciclo por vez.
Una pieza por commit.
Auditoría antes de implementación.
Human stop antes de avanzar.
```

Regla madre:

```text
La IA conversa.
La FSM gobierna.
Las tools ejecutan.
Los archivos son el producto.
```

En el estado actual, la FSM productiva todavía no está abierta.

---

## 6. Próximo frente seguro

```text
SERVICE_1_STAGE_5_NORMALIZATION_SCOPE_DESIGN_V1
```

Objetivo:

```text
Diseñar la Etapa 5 — CSV + PDF + normalizador común.
```

Orden recomendado:

```text
1. CSV intake
2. normalizador común
3. PDF intake
```

Motivo:

```text
CSV es una frontera más controlable que PDF.
PDF queda diferido para evitar OCR/parser prematuro.
```

---

## 7. Qué debe hacer una IA antes de proponer código

```text
1. Leer SERVICE_1_CURRENT_STATE_V1.md.
2. Verificar git status.
3. Identificar el frente activo.
4. Proponer TaskSpec mínimo.
5. Esperar autorización humana.
```

Si no hay TaskSpec activo:

```text
No implementar.
Proponer TaskSpec.
```

---

## 8. Veredicto

```text
Este bootstrap existe para reducir documentos, no para multiplicarlos.
Desde este punto, actualizar SERVICE_1_CURRENT_STATE_V1.md cuando cambie el estado operativo.
No crear micro-closeouts salvo excepción justificada.
```
