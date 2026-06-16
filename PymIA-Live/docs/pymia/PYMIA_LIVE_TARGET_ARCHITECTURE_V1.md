# PYMIA LIVE TARGET ARCHITECTURE V1

## Estado

```text
TARGET_ARCHITECTURE_V1
```

## Propósito

Declarar la arquitectura objetivo multicanal de `PymIA-Live` para que el crecimiento futuro no vuelva a concentrarse en `vertical_slice.py`.

Este documento no crea una capacidad nueva.

Este documento fija una frontera arquitectónica para las próximas extracciones y para la evolución futura hacia canales adicionales.

---

## 1. Problema que resuelve

`vertical_slice.py` nació como vertical slice ejecutable: una entrada local capaz de transformar un Excel y un mensaje del dueño en una salida owner-facing trazable.

Ese origen fue correcto para validar el flujo vivo.

Pero el archivo acumuló responsabilidades que no deben seguir creciendo dentro de un adaptador de canal:

```text
- CLI
- registro
- evidencia
- structured summary
- QAG / owner question
- owner output
- diagnostic adapter
- markdown renderer
- pipeline assembly
```

El refactor de `owner_simple` corrigió una parte de esta concentración.

La extracción de `pipeline_registration` corrigió otra parte.

Pero la arquitectura completa todavía debe quedar declarada para evitar que `vertical_slice.py` vuelva a convertirse en el producto completo.

---

## 2. Principio rector

```text
vertical_slice.py no debe crecer.
vertical_slice.py debe achicarse hasta quedar como adaptador CLI.
```

Su destino no es ser el sistema.

Su destino es ser un canal local que:

```text
- parsea argumentos;
- construye input local;
- invoca el caso de uso;
- escribe salida local;
- devuelve exit code.
```

---

## 3. Arquitectura objetivo

```text
pymia/
  cli/
    vertical_slice.py

  application/
    vertical_pipeline.py

  smartpyme/
    pipeline_registration.py
    owner_output.py
    question_resolution.py
    structured_summary_service.py
    diagnostic_operator_adapter.py

  rendering/
    owner_markdown_renderer.py

  contracts/
    *.json
    *.py
```

Lectura arquitectónica:

```text
canales -> application use case -> domain services / contracts / rendering / storage
```

Los canales actuales y futuros no deben copiar lógica desde `vertical_slice.py`.

Deben invocar una frontera de aplicación común.

---

## 4. Definiciones

### Canal

Un canal es una forma de entrada o salida hacia el sistema.

Ejemplos actuales o futuros:

```text
- CLI local
- API futura
- UI futura
- WhatsApp futuro
- Telegram futuro
- operador humano asistido
- PDF / markdown / salida descargable
```

Un canal puede adaptar formato, credenciales, archivos, argumentos, mensajes y transporte.

Un canal no debe contener lógica de negocio central.

### Application use case

Un application use case coordina un flujo operativo completo.

Para este caso:

```text
Excel + mensaje + tenant/intake
↓
registro
↓
evidencia estructurada
↓
suficiencia / reconciliación
↓
pregunta owner-facing
↓
owner-facing report
↓
owner output
↓
resultado estructurado independiente del canal
```

El destino objetivo es:

```text
pymia/application/vertical_pipeline.py
```

### Domain service

Un domain service encapsula una responsabilidad del dominio SmartPyme sin depender del canal.

Ejemplos:

```text
- registrar trazas del pipeline;
- resolver próxima pregunta owner-facing;
- construir summary estructurado;
- adaptar resultado diagnóstico para operador;
- construir owner output mínimo.
```

### Renderer

Un renderer transforma datos ya resueltos en un formato de presentación.

Ejemplos:

```text
- markdown local;
- PDF futuro;
- HTML futuro;
- bloque WhatsApp futuro;
- respuesta API futura.
```

Un renderer no debe decidir QAG, no debe registrar evidencia y no debe calcular diagnóstico.

Debe recibir datos ya resueltos.

### Contrato declarativo

Un contrato declarativo es una fuente de verdad no procedural para reglas, labels, copy, mappings o conocimiento.

Ejemplos vivos:

```text
- formula_rules_v1.json
- presentation_labels_v1.json
- question_alignment_v1.json
- pathology_rules_v1.json
- evidence_requirement_aliases_v1.json
- formula_aliases_v1.json
- evidence_requirement_copy_v1.json
- owner_facing_report_copy_v1.json
- vertical_slice_copy_v1.json
- language_corpus_seed.json
```

Regla vigente:

```text
JSON/contratos = fuente declarativa de conocimiento.
Python runtime = carga, valida, calcula, orquesta, renderiza y falla cerrado.
```

### Storage / registration

Storage persiste registros concretos.

Registration construye y registra trazas del flujo.

La responsabilidad actual extraída vive en:

```text
pymia/smartpyme/pipeline_registration.py
```

---

## 5. Mapa actual → destino

| Responsabilidad | Funciones actuales / superficie | Destino objetivo | Prioridad | Riesgo |
|---|---|---|---|---|
| CLI local | `main()`, argparse, construcción de argumentos locales | `pymia/cli/vertical_slice.py` | Alta | Bajo si no vuelve a crecer |
| Pipeline assembly actual | `build_pipeline()`, `build_report()`, `build_markdown()` | `pymia/application/vertical_pipeline.py` | Alta | Alto si futuros canales copian CLI |
| Registration / persistence | `register_*`, `_write_jsonl_line()`, `calculate_sha256()` | `pymia/smartpyme/pipeline_registration.py` | Cerrado inicial | Medio si conserva semántica de canal |
| Owner output | `build_owner_simple_view()` | `pymia/smartpyme/owner_output.py` | Cerrado inicial | Medio si se promueve sin contrato |
| Question resolution | `_build_owner_question()`, `_requested_evidence_from_report()`, `_resolve_owner_question_and_reference()` | `pymia/smartpyme/question_resolution.py` | Alta | Alto si renderer o CLI deciden QAG |
| Structured summary | `build_structured_summary()` | `pymia/smartpyme/structured_summary_service.py` | Media | Medio por acoplamiento a Excel |
| Diagnostic adapter | `_serializable_diagnostic_pipeline_result()`, `_diagnostic_pipeline_result_for_report()`, `_diagnostic_operator_summary_from_report()` | `pymia/smartpyme/diagnostic_operator_adapter.py` | Media | Medio por mezcla diagnóstico/reporte |
| Markdown renderer | `render_markdown_from_report()` | `pymia/rendering/owner_markdown_renderer.py` | Media | Alto si decide negocio o QAG |
| Declarative contracts | `contracts/*.json`, loaders `contracts/*.py` | `pymia/contracts/` | Permanente | Alto si se hardcodea conocimiento en runtime |

---

## 6. Orden de migración

Orden recomendado desde el estado actual:

```text
1. QUESTION_RESOLUTION_SERVICE_EXTRACTION_V1
2. DIAGNOSTIC_OPERATOR_ADAPTER_EXTRACTION_V1
3. OWNER_MARKDOWN_RENDERER_EXTRACTION_V1
4. VERTICAL_PIPELINE_APPLICATION_BOUNDARY_V1
```

Nota histórica:

```text
PIPELINE_REGISTRATION_SERVICE_EXTRACTION_V1 ya fue cerrado antes de este documento.
OWNER_SIMPLE_BUILDER_EXTRACTION_V1 ya fue cerrado antes de este documento.
```

El orden evita crear `application/vertical_pipeline.py` demasiado pronto con dependencias inversas hacia CLI.

Primero se extraen servicios de bajo riesgo.

Después se crea la frontera de aplicación.

---

## 7. Regla crítica de dependencia

```text
pymia/application/vertical_pipeline.py no debe importar desde pymia.cli.
```

También rige:

```text
pymia/smartpyme/* no debe importar desde pymia.cli.
pymia/rendering/* no debe importar desde pymia.cli.
```

La dependencia permitida es:

```text
cli -> application -> smartpyme / contracts / rendering
```

No al revés.

---

## 8. Prohibiciones

Mientras este documento gobierne la migración, queda prohibido:

```text
- crear canales nuevos todavía;
- crear API;
- crear UI;
- crear owner_output_v1 todavía;
- crear dataclasses nuevos por estética;
- mover todo de golpe;
- cambiar output observable;
- cambiar contratos declarativos sin necesidad material;
- crear arquitectura paralela;
- duplicar lógica entre canales;
- hacer que renderers resuelvan QAG;
- hacer que CLI registre directamente a largo plazo;
- hardcodear conocimiento de dominio en el kernel;
- abrir micro-copy cleanup sin deuda material;
- llamar producto a una capacidad interna, protocolo local o piloto asistido.
```

---

## 9. Criterios de activación por migración

### QUESTION_RESOLUTION_SERVICE_EXTRACTION_V1

Activar cuando se quiera reducir responsabilidad de `vertical_slice.py` sin cambiar comportamiento owner-facing.

Debe mover sólo resolución de pregunta y evidencia solicitada.

No debe cambiar copy, QAG, contratos JSON ni output.

### DIAGNOSTIC_OPERATOR_ADAPTER_EXTRACTION_V1

Activar cuando se quiera separar adaptación de diagnóstico del canal CLI.

Debe conservar los mismos campos y la misma semántica visible.

No debe cambiar reglas de diagnóstico ni fórmulas.

### OWNER_MARKDOWN_RENDERER_EXTRACTION_V1

Activar cuando la composición markdown bloquee la reducción del CLI o cuando se prepare una frontera clara entre datos resueltos y presentación.

No debe decidir QAG.

No debe registrar evidencia.

No debe calcular diagnóstico.

### VERTICAL_PIPELINE_APPLICATION_BOUNDARY_V1

Activar sólo después de extraer las responsabilidades suficientes para que `application/vertical_pipeline.py` no dependa de `pymia.cli`.

Debe contener el caso de uso principal y devolver resultado estructurado independiente del canal.

---

## 10. Criterio de finalización

La arquitectura objetivo se considera alcanzada cuando:

```text
- vertical_slice.py sólo adapta canal CLI;
- application/vertical_pipeline.py contiene el caso de uso principal;
- ningún canal futuro necesita copiar lógica de vertical_slice.py;
- renderers reciben datos ya resueltos;
- registration vive fuera del CLI;
- owner output vive fuera del CLI;
- question resolution vive fuera del CLI;
- diagnostic adapter vive fuera del CLI;
- tests E2E siguen pasando sin cambio observable.
```

---

## 11. Relación con owner_simple

`owner_simple` ya vive en:

```text
pymia/smartpyme/owner_output.py
```

Su estado sigue siendo:

```text
FROZEN_LOCAL_PRESENTATION_CONTRACT
```

No queda promovido a contrato multicanal.

No crear `owner_output_v1` hasta señal material.

Señales materiales posibles:

```text
- segundo canal consumidor;
- necesidad de schema tipado formal;
- drift real entre tests, salida y contrato implícito;
- owner_simple se vuelve salida base del MVP;
- separación necesaria entre renderer técnico y renderer humano.
```

---

## 12. Relación con PYMIA_LIVE_CORE_MANIFEST

Este documento no contradice `PYMIA_LIVE_CORE_MANIFEST.md`.

Lo proyecta hacia una arquitectura multicanal sin crear capacidad nueva.

El manifiesto declara el núcleo vivo actual.

Este documento declara el destino estructural para que ese núcleo no quede encerrado en un canal local.

Regla de compatibilidad:

```text
el core vivo actual se preserva;
el output observable no cambia;
la trazabilidad no se reduce;
la evidencia sigue gobernando;
los contratos declarativos siguen siendo fuente de conocimiento.
```

---

## 13. Relación con conocimiento enchufable

La arquitectura objetivo debe proteger la regla vigente:

```text
El conocimiento de dominio es enchufable.
El kernel permanece estable.
```

Por lo tanto:

```text
nuevas fórmulas,
nuevas patologías,
nuevas variables organizacionales,
nuevos sectores,
nuevos packs de conocimiento
```

no deben modificar el canal CLI ni incrustarse como lógica hardcodeada en el kernel.

Deben entrar por contratos, catálogos o packs declarativos gobernados.

---

## 14. Decisión

```text
vertical_slice.py no debe crecer.
vertical_slice.py debe achicarse hacia adaptador CLI.
Los futuros canales deben invocar una frontera de aplicación común.
Las responsabilidades extraídas no deben volver al CLI.
La migración debe avanzar por extracciones focales, sin cambiar comportamiento observable.
```

---

## 15. Veredicto

```text
TARGET_ARCHITECTURE_V1 aprobado como plano rector documental.
No implementa runtime.
No crea contratos nuevos.
No habilita canales nuevos.
Gobierna el orden de reducción de vertical_slice.py y la futura frontera application/vertical_pipeline.py.
```
