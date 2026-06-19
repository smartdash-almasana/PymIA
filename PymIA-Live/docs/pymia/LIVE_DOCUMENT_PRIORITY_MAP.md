# LIVE_DOCUMENT_PRIORITY_MAP

## Estado

```text
LIVE_DOCS_RECONCILIATION_V1
```

## Propósito

Declarar qué documentos gobiernan el estado vivo de PymIA-Live cuando existen documentos verdaderos pero escritos en tiempos distintos.

Este documento no crea runtime, contratos, tests ni capacidades nuevas. Ordena prioridad documental para evitar que un documento histórico o parcialmente superado vuelva a abrir frentes ya cerrados.

---

## 1. Jerarquía de prioridad documental

| Documento | Autoridad vigente | Regla de uso |
|---|---|---|
| `LIVE_CODE_FREEZE_LEDGER.md` | Estado técnico certificado de módulos vivos | Manda sobre qué está `FROZEN`, `FIXED`, `PASS` o pendiente de reapertura. |
| `PYMIA_LIVE_CORE_MANIFEST.md` | Núcleo vivo actual | Manda sobre qué ejecuta, valida, decide, traduce, pregunta, registra evidencia u opera hoy. |
| `PYMIA_LIVE_TARGET_ARCHITECTURE_V1.md` | Arquitectura objetivo | Manda sobre reducción de `vertical_slice.py`, frontera `application`, canales y dependencias permitidas. |
| `docs/producto/PYMIA_PRODUCT_UNIVERSE_AND_SERVICE_DEPTH_MODEL_FINAL.md` | Dirección de producto | Manda sobre universo de producto, profundidad variable de servicio y rol de microservicios/OCF. No autoriza runtime por sí solo. |
| `ORGANIZATIONAL_CASE_FILE_V1_CONCEPT.md` | Concepto rector de OCF | Manda sobre la definición conceptual de ficha como grafo/álbum epistémico, no sobre estado implementado. |
| `ANAMNESIS_TAXONOMICA_MINIMA.md` | Primer contacto y taxonomía inicial | Manda sobre organismo/taxonomía/dolor/evidencia como orden canónico de ingreso. |
| `PYMIA_LIVE_PIPELINE.md` | Contexto histórico/parcial de pipeline Live V1 | No manda si contradice `PYMIA_LIVE_CORE_MANIFEST.md`, `LIVE_CODE_FREEZE_LEDGER.md` o `PYMIA_LIVE_TARGET_ARCHITECTURE_V1.md`. |
| `OCF_SNAPSHOT_FROM_REPLAY_SPIKE.md` | SpikeSpec histórico | Conserva valor como especificación de origen. Su estado operativo queda subordinado al ledger. |

---

## 2. Reglas de lectura

```text
Si un documento contradice el ledger, manda el ledger.
Si un documento contradice el core manifest, manda el core manifest.
Si un spike dice NOT_STARTED pero el ledger lo marca PASS/FIXED, el spike queda histórico.
Si un documento de producto propone dirección, no implica runtime autorizado.
Si un documento de arquitectura objetivo propone destino, no implica migración abierta.
Si un documento histórico contiene gaps ya cerrados, no debe reabrirlos sin hallazgo verificable nuevo.
```

---

## 3. Contradicciones resueltas

| Tema | Documento desfasado dice | Estado vigente | Autoridad vigente |
|---|---|---|---|
| QuestionAlignmentGate | `PYMIA_LIVE_PIPELINE.md` lo ubica como punto futuro de inserción | Cerrado e implementado mediante contrato declarativo y gate vivo | `PYMIA_LIVE_CORE_MANIFEST.md` + `LIVE_CODE_FREEZE_LEDGER.md` |
| OCF Snapshot | `OCF_SNAPSHOT_FROM_REPLAY_SPIKE.md` dice `Implementación: NOT_STARTED` / spike | Implementado, auditado como `FIXED` / `PASS` | `LIVE_CODE_FREEZE_LEDGER.md` |
| `service_depth.py` | Sin fila propia en ledger | Existe, está trackeado y cubierto por tests de módulos frozen; requiere fila explícita de cierre | Código + tests + `LIVE_CODE_FREEZE_LEDGER.md` actualizado |
| `vertical_slice.py` | Pipeline local como origen ejecutable | Debe reducirse progresivamente a adaptador CLI; no debe crecer | `PYMIA_LIVE_TARGET_ARCHITECTURE_V1.md` |
| Producto de profundidad variable | Define `FIRST_AID` / `DETERMINISTIC_DIAGNOSIS` / `ORGANIZATIONAL_LAB` | Dirección de producto válida; no autoriza runtime nuevo sin TaskSpec | `PYMIA_PRODUCT_UNIVERSE_AND_SERVICE_DEPTH_MODEL_FINAL.md` + método Live |
| OCF conceptual | Define ficha completa como mapa epistémico | Concepto rector válido; snapshot actual es vista mínima desde replay, no OCF V1 final | `ORGANIZATIONAL_CASE_FILE_V1_CONCEPT.md` + `LIVE_CODE_FREEZE_LEDGER.md` |

---

## 4. Regla de cierre documental

Una capacidad o auditoría sólo cuenta como cierre certificado si queda registrada en al menos uno de estos lugares:

```text
- commit versionado;
- checkpoint versionado;
- LIVE_CODE_FREEZE_LEDGER.md;
- documento rector actualizado por TaskSpec explícito.
```

Si una afirmación vive sólo en chat, no gobierna el repo.

---

## 5. Regla de producto vs runtime

`PYMIA_PRODUCT_UNIVERSE_AND_SERVICE_DEPTH_MODEL_FINAL.md` gobierna la coherencia del producto:

```text
primeros auxilios
→ diagnóstico determinístico
→ laboratorio organizacional
```

Pero una dirección de producto no autoriza por sí misma:

```text
- crear runtime;
- mover módulos;
- abrir canales;
- crear plugins;
- crear packs;
- crear storage;
- ejecutar diagnóstico nuevo;
- externalizar vocabularios.
```

Toda capacidad nueva requiere:

```text
archivo rector
→ contrato mínimo
→ test de aceptación
→ implementación focal
→ evidencia
→ checkpoint o ledger
```

---

## 6. Regla de spikes implementados

Los SpikeSpecs conservan valor para entender intención, límites y stop conditions.

Pero si el código ya existe y el ledger lo marcó como `PASS` o `FIXED`, el estado operativo vigente lo define el ledger.

```text
SpikeSpec = historia de diseño.
Ledger = estado certificado vivo.
```

---

## 7. Próximo uso esperado

Antes de abrir un nuevo frente, leer este mapa junto con:

```text
LIVE_CODE_FREEZE_LEDGER.md
PYMIA_LIVE_CORE_MANIFEST.md
PYMIA_LIVE_TARGET_ARCHITECTURE_V1.md
```

Después, recién cruzar con producto, OCF, anamnesis o spike según el frente.
