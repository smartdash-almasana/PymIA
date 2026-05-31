# Contrato MCP v0.1 — `pymia.first_clinical_interview.v1`

**Versión**: 0.1 (DRAFT)
**Fecha**: 2026-05-23
**Estado**: PROPUESTA — pendiente de revisión y aprobación antes de implementación
**ADR de referencia**: [ADR-008: Hermes MCP client → PymIA MCP server](file:///e:/BuenosPasos/smartbridge/PymIA/docs/adr/ADR-008-hermes-mcp-client-pymia-mcp-server.md)
**Contrato clínico de referencia**: [CONTRATO_PRIMER_ENCUENTRO_TAXONOMICO.md](file:///e:/BuenosPasos/smartbridge/PymIA/docs/arquitectura/CONTRATO_PRIMER_ENCUENTRO_TAXONOMICO.md)

---

## 1. Propósito

`pymia.first_clinical_interview.v1` es la tool MCP primaria del server PymIA.

Ejecuta el **primer contacto clínico** entre PymIA y el dueño de una PyME, respetando el orden canónico establecido en `CONTRATO_PRIMER_ENCUENTRO_TAXONOMICO`:

```
1. Encuadre taxonómico obligatorio del organismo PyME.
2. Síntomas detectados semántica o computacionalmente.
3. Evidencia/datos necesarios.
4. Análisis posterior.
```

Esta tool es el **punto de entrada único** para la conversación clínica inicial. No debe ser invocada en paralelo con otras tools de hipótesis o auditoría. Su output define el estado conversacional desde el cual Hermes continúa.

### Qué hace esta tool

- Recibe el texto libre del dueño y el contexto progresivo acumulado en turnos anteriores.
- Determina si corresponde iniciar el encuadre taxonómico o avanzar al pipeline clínico.
- Devuelve un mensaje formateado, el estado de anamnesis, el contrato de laboratorio, y el contexto progresivo actualizado.

### Qué NO hace esta tool

- No diagnostica.
- No calcula margen, caja ni rentabilidad.
- No interpreta documentos estructurados.
- No gestiona canal, sesión ni historial de mensajes.
- No invoca APIs externas.

---

## 2. Identificador MCP

```
tool_name: pymia.first_clinical_interview.v1
```

El sufijo `.v1` es parte del nombre y permite versionado sin romper contratos previos.

---

## 3. Input Schema

```json
{
  "name": "pymia.first_clinical_interview.v1",
  "description": "Ejecuta el primer contacto clínico de PymIA con el dueño. Respeta el orden taxonómico antes del pipeline clínico. Devuelve mensaje, anamnesis, laboratorio y contexto progresivo actualizado.",
  "inputSchema": {
    "type": "object",
    "required": ["tenant_id", "channel", "text"],
    "properties": {
      "tenant_id": {
        "type": "string",
        "description": "Identificador único del tenant (negocio observado). Nunca mezclar entre tenants.",
        "minLength": 1
      },
      "channel": {
        "type": "string",
        "description": "Canal de entrada desde el cual Hermes invoca la tool. Ej: 'telegram', 'api', 'cli'.",
        "minLength": 1
      },
      "text": {
        "type": "string",
        "description": "Texto libre del dueño. Relato conversacional, no evidencia documental.",
        "minLength": 1
      },
      "previous_progressive_context": {
        "type": "object",
        "description": "Snapshot del contexto progresivo clínico acumulado en turnos anteriores. Null si es primer turno absoluto.",
        "nullable": true,
        "properties": {
          "tenant_id": { "type": "string" },
          "channel": { "type": "string" },
          "business_identity": {
            "type": "object",
            "properties": {
              "display_name": { "type": "string", "nullable": true },
              "country_code": { "type": "string", "nullable": true, "description": "ISO 3166-1 alpha-2. Ej: 'AR', 'MX', 'BR'." },
              "industry_hint": { "type": "string", "nullable": true, "description": "Tipo de organismo inferido o declarado. Ej: 'comercio', 'industria/fabrica', 'servicios'." },
              "taxonomy_phase": {
                "type": "string",
                "nullable": true,
                "enum": [null, "FASE_0_IDENTIDAD"],
                "description": "Fase taxonómica completada. Null = no iniciada. 'FASE_0_IDENTIDAD' = organismo encuadrado y confirmado."
              }
            }
          },
          "symptom_summary": {
            "type": "array",
            "items": { "type": "string" },
            "description": "Síntomas operacionales detectados en turnos previos."
          },
          "documents_requested": {
            "type": "array",
            "items": { "type": "string" },
            "description": "Documentos solicitados en turnos previos."
          }
        }
      }
    }
  }
}
```

### Notas de input

| Campo | Obligatorio | Comportamiento si ausente |
|---|---|---|
| `tenant_id` | ✅ | Error de validación |
| `channel` | ✅ | Error de validación |
| `text` | ✅ | Error de validación |
| `previous_progressive_context` | ❌ | Se asume primer turno; se inicia encuadre taxonómico |

---

## 4. Output Schema

```json
{
  "outputSchema": {
    "type": "object",
    "oneOf": [
      {
        "title": "TaxonomicFramingResponse",
        "description": "Respuesta de encuadre taxonómico. Primer contacto sin taxonomía confirmada. Sin hipótesis, sin pedido de documentos.",
        "properties": {
          "status": { "type": "string", "enum": ["ok"] },
          "estado_conversacional": { "type": "string", "enum": ["encuadre_taxonomico_inicial"] },
          "message": { "type": "string", "description": "Pregunta de encuadre taxonómico. Menciona tipos de organismos. No diagnostica." },
          "anamnesis": { "$ref": "#/definitions/AnamnesisOriginaria" },
          "laboratorio": { "$ref": "#/definitions/LaboratorioInicialContrato" },
          "progressive_context": { "$ref": "#/definitions/ProgressiveTenantClinicalContext" }
        }
      },
      {
        "title": "ClinicalAnamnesisResponse",
        "description": "Respuesta clínica. Taxonomía ya confirmada. Contiene hipótesis, síntomas y evidencia requerida.",
        "properties": {
          "status": { "type": "string", "enum": ["ok"] },
          "estado_conversacional": { "type": "string", "enum": ["esperando_documentacion"] },
          "message": { "type": "string", "description": "Mensaje clínico con síntoma registrado, hipótesis inicial y pedido de evidencia." },
          "anamnesis": { "$ref": "#/definitions/AnamnesisOriginaria" },
          "laboratorio": { "$ref": "#/definitions/LaboratorioInicialContrato" },
          "progressive_context": { "$ref": "#/definitions/ProgressiveTenantClinicalContext" }
        }
      },
      {
        "title": "NoSignalResponse",
        "description": "Sin señal clínica ni taxonómica detectable. Taxonomía ya confirmada pero input sin contenido operacional.",
        "properties": {
          "status": { "type": "string", "enum": ["no_signal"] },
          "estado_conversacional": { "type": "string", "enum": ["no_signal"] },
          "message": { "type": "null" },
          "anamnesis": { "type": "null" },
          "laboratorio": { "type": "null" },
          "progressive_context": { "type": "null" }
        }
      },
      {
        "title": "ErrorResponse",
        "description": "Error tipado. Incluye código y causa.",
        "properties": {
          "status": { "type": "string", "enum": ["error"] },
          "error_code": { "type": "string" },
          "error_message": { "type": "string" },
          "details": { "type": "object", "nullable": true }
        }
      }
    ]
  }
}
```

### Definiciones de modelos referenciados

```json
{
  "definitions": {
    "AnamnesisOriginaria": {
      "type": "object",
      "properties": {
        "tenant_id": { "type": "string" },
        "canal": { "type": "string" },
        "frases_textuales": { "type": "array", "items": { "type": "string" } },
        "dolores_detectados": { "type": "array", "items": { "type": "string" } },
        "hipotesis_iniciales": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Vacío en encuadre_taxonomico_inicial. Poblado solo post-FASE_0_IDENTIDAD."
        },
        "taxonomia_inicial": {
          "type": "object",
          "properties": {
            "rubro": { "type": "string", "nullable": true },
            "tipo_pyme": { "type": "string", "nullable": true },
            "produce_o_revende": { "type": "string", "nullable": true },
            "maneja_stock": { "type": "string", "nullable": true }
          }
        },
        "documentos_pedidos": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Vacío en encuadre_taxonomico_inicial. Poblado solo post-FASE_0_IDENTIDAD."
        },
        "estado_conversacional": {
          "type": "string",
          "enum": [
            "encuadre_taxonomico_inicial",
            "esperando_documentacion",
            "contexto_clinico_insuficiente",
            "error_procesamiento_evidencia",
            "procesamiento_pendiente"
          ]
        }
      }
    },
    "LaboratorioInicialContrato": {
      "type": "object",
      "properties": {
        "tenant_id": { "type": "string" },
        "estado_conversacional": { "type": "string" },
        "hipotesis_a_contrastar": { "type": "array", "items": { "type": "string" } },
        "evidencia_requerida": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Vacío en encuadre_taxonomico_inicial."
        },
        "capability": { "type": "string" },
        "tipo_documental_esperado": { "type": "array", "items": { "type": "string" } },
        "campos_esperados": { "type": "array", "items": { "type": "string" } },
        "nivel_confianza": { "type": "string" },
        "limite_actual": { "type": "string" }
      }
    },
    "ProgressiveTenantClinicalContext": {
      "type": "object",
      "properties": {
        "tenant_id": { "type": "string" },
        "channel": { "type": "string" },
        "business_identity": {
          "type": "object",
          "properties": {
            "display_name": { "type": "string", "nullable": true },
            "country_code": { "type": "string", "nullable": true },
            "industry_hint": { "type": "string", "nullable": true },
            "taxonomy_phase": { "type": "string", "nullable": true, "enum": [null, "FASE_0_IDENTIDAD"] }
          }
        },
        "symptom_summary": { "type": "array", "items": { "type": "string" } },
        "documents_requested": { "type": "array", "items": { "type": "string" } }
      }
    }
  }
}
```

---

## 5. Estados conversacionales

| Estado | Cuándo ocurre | Hermes debe hacer |
|---|---|---|
| `encuadre_taxonomico_inicial` | Primer turno sin taxonomía confirmada, o segundo turno sin respuesta taxonómica suficiente | Presentar el `message` al dueño. Guardar `progressive_context`. Esperar respuesta. |
| `esperando_documentacion` | Taxonomía ya confirmada, señal clínica detectada | Presentar el `message` con hipótesis y pedido de evidencia. Guardar `progressive_context`. |
| `no_signal` | Taxonomía ya confirmada pero input sin señal clínica (saludo, confirmación, etc.) | No presentar diagnóstico. Puede pedir más información o mantener contexto. |
| `contexto_clinico_insuficiente` | `TenantClinicalContext` formal presente pero incompleto | Error recuperable. Continuar con `previous_progressive_context` si existe. |
| `error_procesamiento_evidencia` | Adjunto recibido pero con error de parsing | Informar al dueño del error. No continuar análisis. |
| `procesamiento_pendiente` | Adjunto recibido pero aún no procesado | Informar al dueño que se espera procesamiento. Reintentar en siguiente turno. |

### Diagrama de transiciones

```
                    ┌─────────────────────────────────────────────┐
                    │              Nuevo turno                       │
                    └──────────────────┬──────────────────────────┘
                                       │
                     previous_progressive_context presente?
                          │                         │
                         No                        Sí
                          │                         │
                          ▼                         ▼
              ┌─────────────────────┐    has_taxonomic_identity?
              │  encuadre_          │         │            │
              │  taxonomico_inicial │        No            Sí
              └─────────────────────┘         │            │
                                              ▼            ▼
                                   ┌──────────────┐  señal clínica?
                                   │  encuadre_   │    │         │
                                   │  taxonomico_ │   Sí        No
                                   │  inicial     │    │         │
                                   └──────────────┘   ▼         ▼
                                              ┌──────────┐  ┌──────────┐
                                              │ esperando │  │ no_signal│
                                              │ docum.    │  │          │
                                              └──────────┘  └──────────┘
```

---

## 6. Errores tipados

| `error_code` | Causa | HTTP equivalente | Recuperable |
|---|---|---|---|
| `INVALID_INPUT` | `tenant_id`, `channel` o `text` vacío o inválido | 400 | No — corregir input |
| `TENANT_ISOLATION_VIOLATION` | `tenant_id` en `previous_progressive_context` no coincide con `tenant_id` del input | 422 | No — bug en cliente |
| `CONTEXT_SCHEMA_INVALID` | `previous_progressive_context` recibido no puede deserializarse al schema esperado | 422 | Parcial — descartar contexto y reiniciar |
| `CLINICAL_KERNEL_UNAVAILABLE` | Error interno del kernel clínico de PymIA | 500 | Sí — reintentar |
| `EVIDENCE_PARSE_FAILED` | Adjunto recibido con error de análisis estructural | 422 | No — informar al dueño |
| `UNKNOWN_ERROR` | Error no clasificado | 500 | Depende |

### Formato de error

```json
{
  "status": "error",
  "error_code": "TENANT_ISOLATION_VIOLATION",
  "error_message": "El tenant_id del contexto progresivo no coincide con el tenant_id del input.",
  "details": {
    "input_tenant_id": "tenant_A",
    "context_tenant_id": "tenant_B"
  }
}
```

---

## 7. Reglas de frontera Hermes / PymIA

### Hermes DEBE hacer antes de invocar esta tool

1. **Cargar** el `previous_progressive_context` de la sesión actual (por `tenant_id` + `user_id`).
2. **Pasar** el contexto como input al invocar la tool. Nunca pasar el contexto de otro tenant.
3. **No modificar** el `previous_progressive_context` antes de pasarlo. Solo PymIA lo actualiza.
4. **No construir** hipótesis, pedidos de evidencia ni diagnósticos propios antes de invocar la tool.

### Hermes DEBE hacer después de recibir el output

1. **Guardar** el `progressive_context` del output como nuevo estado de sesión, reemplazando el anterior.
2. **Presentar** el `message` del output al dueño sin modificarlo salvo por formateo de canal.
3. **No interpretar** `hipotesis_iniciales` ni `evidencia_requerida` para construir respuestas propias.
4. Si `status == "no_signal"`, **no inventar** una respuesta clínica. Puede pedir más contexto al dueño.
5. Si `status == "error"`, **no ocultar** el error al dueño. Informar de forma simple y sin tecnicismos.

### Lo que Hermes NUNCA debe hacer

- Invocar la tool sin `tenant_id` o con un `tenant_id` distinto al del dueño activo.
- Pasar el `progressive_context` de un dueño a la sesión de otro.
- Acumular hipótesis propias y luego invocar la tool con el texto modificado.
- Invocar la tool más de una vez por turno de usuario.
- Cachear el output de la tool para reutilizarlo en el siguiente turno sin reinvocar.

---

## 8. Ejemplos de request/response

### Ejemplo 1 — Primer contacto sin taxonomía

**Request:**
```json
{
  "tenant_id": "tenant_pyme_001",
  "channel": "telegram",
  "text": "RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY",
  "previous_progressive_context": null
}
```

**Response:**
```json
{
  "status": "ok",
  "estado_conversacional": "encuadre_taxonomico_inicial",
  "message": "Antes de analizar números o sacar conclusiones, necesito ubicar qué tipo de negocio estamos mirando.\n\nPara empezar, contame:\n¿Es un comercio, una fábrica / industria, una empresa de servicios, logística / distribución, gastronomía, construcción, agro, salud, educación u otro tipo de organización?\n\nY si podés agregar:\n¿Fabricás, revendés, distribuís o prestás servicios?\n¿Vendés al público, a empresas, por local, online, por WhatsApp, por Mercado Libre u otro canal?\n¿Tenés empleados? Aproximadamente, ¿cuántos?\n\nCon eso puedo armar el contexto base antes de pedirte datos o documentos.",
  "anamnesis": {
    "tenant_id": "tenant_pyme_001",
    "canal": "telegram",
    "frases_textuales": ["RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY"],
    "dolores_detectados": [],
    "hipotesis_iniciales": [],
    "taxonomia_inicial": {
      "rubro": null,
      "tipo_pyme": null,
      "produce_o_revende": null,
      "maneja_stock": null
    },
    "documentos_pedidos": [],
    "estado_conversacional": "encuadre_taxonomico_inicial"
  },
  "laboratorio": {
    "tenant_id": "tenant_pyme_001",
    "estado_conversacional": "encuadre_taxonomico_inicial",
    "hipotesis_a_contrastar": [],
    "evidencia_requerida": [],
    "capability": "encuadre_taxonomico",
    "tipo_documental_esperado": [],
    "campos_esperados": [],
    "nivel_confianza": "sin_contexto_taxonomico",
    "limite_actual": "No se puede iniciar análisis sin conocer el tipo de organismo."
  },
  "progressive_context": {
    "tenant_id": "tenant_pyme_001",
    "channel": "telegram",
    "business_identity": {
      "display_name": null,
      "country_code": null,
      "industry_hint": null,
      "taxonomy_phase": null
    },
    "symptom_summary": ["incertidumbre de rentabilidad"],
    "documents_requested": ["ventas", "costos", "precios", "caja"]
  }
}
```

---

### Ejemplo 2 — Segundo turno con respuesta taxonómica del dueño

**Request:**
```json
{
  "tenant_id": "tenant_pyme_001",
  "channel": "telegram",
  "text": "somos una distribuidora de alimentos, 12 empleados, vendemos a comercios",
  "previous_progressive_context": {
    "tenant_id": "tenant_pyme_001",
    "channel": "telegram",
    "business_identity": {
      "display_name": null,
      "country_code": null,
      "industry_hint": null,
      "taxonomy_phase": null
    },
    "symptom_summary": ["incertidumbre de rentabilidad"],
    "documents_requested": ["ventas", "costos", "precios", "caja"]
  }
}
```

**Response:**
```json
{
  "status": "ok",
  "estado_conversacional": "esperando_documentacion",
  "message": "Señal económico-operacional registrada: incertidumbre de rentabilidad.\n\nEstado: hipótesis abierta, sin diagnóstico confirmado.\n\nLaboratorio inicial de rentabilidad/margen — evidencia requerida:\n- ventas del período\n- costos o facturas de compra\n- lista de precios vigente\n- extracto/caja si querés revisar si el problema es liquidez\n\nObjetivo del contraste: separar margen erosionado, costos desactualizados, precios no alineados o tensión de caja.",
  "anamnesis": {
    "tenant_id": "tenant_pyme_001",
    "canal": "telegram",
    "frases_textuales": ["somos una distribuidora de alimentos, 12 empleados, vendemos a comercios"],
    "dolores_detectados": ["incertidumbre de rentabilidad"],
    "hipotesis_iniciales": ["margen erosionado", "costos desactualizados", "precios de venta no alineados a costo", "caja o liquidez mezclada con rentabilidad"],
    "taxonomia_inicial": {
      "rubro": null,
      "tipo_pyme": null,
      "produce_o_revende": null,
      "maneja_stock": null
    },
    "documentos_pedidos": ["ventas del período", "costos o facturas de compra", "lista de precios vigente", "extracto/caja si querés revisar si el problema es liquidez"],
    "estado_conversacional": "esperando_documentacion"
  },
  "laboratorio": {
    "tenant_id": "tenant_pyme_001",
    "estado_conversacional": "esperando_documentacion",
    "hipotesis_a_contrastar": ["margen erosionado", "costos desactualizados", "precios de venta no alineados a costo", "caja o liquidez mezclada con rentabilidad"],
    "evidencia_requerida": ["ventas del período", "costos o facturas de compra", "lista de precios vigente", "extracto/caja si querés revisar si el problema es liquidez"],
    "capability": "laboratorio_inicial_margen_rentabilidad",
    "tipo_documental_esperado": ["xlsx", "csv", "pdf", "captura"],
    "campos_esperados": ["producto", "fecha", "cantidad", "precio_venta", "costo", "proveedor", "medio_de_cobro"],
    "nivel_confianza": "hipotesis_abierta",
    "limite_actual": "No se puede afirmar rentabilidad real sin contrastar ventas contra costos, precios y caja."
  },
  "progressive_context": {
    "tenant_id": "tenant_pyme_001",
    "channel": "telegram",
    "business_identity": {
      "display_name": null,
      "country_code": "AR",
      "industry_hint": "logistica/distribucion",
      "taxonomy_phase": "FASE_0_IDENTIDAD"
    },
    "symptom_summary": ["incertidumbre de rentabilidad"],
    "documents_requested": ["ventas", "costos", "precios", "caja", "ventas del período", "costos o facturas de compra", "lista de precios vigente", "extracto/caja si querés revisar si el problema es liquidez"]
  }
}
```

---

### Ejemplo 3 — Sin señal (post-taxonomía)

**Request:**
```json
{
  "tenant_id": "tenant_pyme_001",
  "channel": "telegram",
  "text": "hola, como estas?",
  "previous_progressive_context": {
    "tenant_id": "tenant_pyme_001",
    "channel": "telegram",
    "business_identity": {
      "display_name": null,
      "country_code": "AR",
      "industry_hint": "logistica/distribucion",
      "taxonomy_phase": "FASE_0_IDENTIDAD"
    },
    "symptom_summary": [],
    "documents_requested": []
  }
}
```

**Response:**
```json
{
  "status": "no_signal",
  "estado_conversacional": "no_signal",
  "message": null,
  "anamnesis": null,
  "laboratorio": null,
  "progressive_context": null
}
```

---

### Ejemplo 4 — Error: violación de aislamiento de tenant

**Request (inválido):**
```json
{
  "tenant_id": "tenant_pyme_001",
  "channel": "telegram",
  "text": "RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY",
  "previous_progressive_context": {
    "tenant_id": "tenant_pyme_OTRO",
    "channel": "telegram",
    "business_identity": { "taxonomy_phase": "FASE_0_IDENTIDAD" },
    "symptom_summary": [],
    "documents_requested": []
  }
}
```

**Response:**
```json
{
  "status": "error",
  "error_code": "TENANT_ISOLATION_VIOLATION",
  "error_message": "El tenant_id del contexto progresivo no coincide con el tenant_id del input.",
  "details": {
    "input_tenant_id": "tenant_pyme_001",
    "context_tenant_id": "tenant_pyme_OTRO"
  }
}
```

---

## 9. Criterios de aceptación

Una implementación de `pymia.first_clinical_interview.v1` es aceptable si:

### CA-01: Primer contacto sin taxonomía → encuadre taxonómico
- Input con `previous_progressive_context = null`.
- Output: `status = "ok"`, `estado_conversacional = "encuadre_taxonomico_inicial"`.
- `anamnesis.hipotesis_iniciales = []`.
- `laboratorio.evidencia_requerida = []`.
- `message` menciona tipos de organismos (comercio, fábrica, servicios, etc.).
- `progressive_context` no es null.
- `progressive_context.business_identity.taxonomy_phase = null`.

### CA-02: Taxonomía confirmada con señal clínica → pipeline clínico
- Input con `previous_progressive_context.business_identity.taxonomy_phase = "FASE_0_IDENTIDAD"`.
- Input con `text` que contenga señal de margen, rentabilidad u operacional.
- Output: `status = "ok"`, `estado_conversacional = "esperando_documentacion"`.
- `anamnesis.hipotesis_iniciales` no vacío.
- `laboratorio.evidencia_requerida` no vacío.
- `progressive_context.business_identity.taxonomy_phase = "FASE_0_IDENTIDAD"` (preservado).

### CA-03: Taxonomía confirmada sin señal → no_signal
- Input con `previous_progressive_context.business_identity.taxonomy_phase = "FASE_0_IDENTIDAD"`.
- Input con `text` sin señal clínica (saludo, confirmación neutral, etc.).
- Output: `status = "no_signal"`.
- `anamnesis = null`, `laboratorio = null`, `progressive_context = null`.

### CA-04: Segundo turno taxonómico sin confirmación → continúa encuadre
- Input con `previous_progressive_context` presente pero `taxonomy_phase = null`.
- Input con `text` sin datos taxonómicos reconocibles.
- Output: `status = "ok"`, `estado_conversacional = "encuadre_taxonomico_inicial"`.
- No emite hipótesis.

### CA-05: Respuesta taxonómica del dueño → actualiza progressive_context
- Input con `previous_progressive_context.taxonomy_phase = null`.
- Input con `text` que declara tipo de organismo (ej: "somos una distribuidora").
- Output: `progressive_context.business_identity.industry_hint` no null.
- Output: `progressive_context.business_identity.taxonomy_phase = "FASE_0_IDENTIDAD"`.
- Output: `progressive_context.business_identity.country_code = "AR"`.

### CA-06: Aislamiento de tenant
- Input con `previous_progressive_context.tenant_id ≠ input.tenant_id`.
- Output: `status = "error"`, `error_code = "TENANT_ISOLATION_VIOLATION"`.

### CA-07: Input inválido
- Input con `text = ""` o `tenant_id = ""`.
- Output: `status = "error"`, `error_code = "INVALID_INPUT"`.

### CA-08: El encuadre taxonómico no menciona términos diagnósticos
- Output con `estado_conversacional = "encuadre_taxonomico_inicial"`.
- `message` NO contiene: "margen erosionado", "tensión de caja", "fuga operativa", "hipótesis", "laboratorio".

### CA-09: Idempotencia parcial
- Dos invocaciones con el mismo input producen el mismo `estado_conversacional`.
- El `message` puede variar en formato menor pero no en contenido clínico.

---

## 10. Test mínimo futuro

**Archivo**: `tests/mcp/test_first_clinical_interview_contract.py`

```python
"""
tests/mcp/test_first_clinical_interview_contract.py

Validación del contrato MCP v0.1 para pymia.first_clinical_interview.v1.

IMPORTANTE: Estos tests verifican el contrato desde la perspectiva del cliente MCP
(Hermes). No deben depender de la implementación interna de PymIA.
Deben ejecutarse contra el server MCP real o un doble de contrato.

Estado: FUTURO — no implementar hasta que el server MCP esté disponible.
"""
from __future__ import annotations

import pytest

# Importaciones futuras (aún no existen)
# from pymia.mcp.server import PymIAMCPServer
# from pymia.mcp.client import invoke_tool


# ---------------------------------------------------------------------------
# CA-01: Primer contacto sin taxonomía → encuadre taxonómico
# ---------------------------------------------------------------------------

def test_ca01_first_contact_returns_taxonomic_framing():
    """CA-01: Sin previous_progressive_context → estado encuadre_taxonomico_inicial."""
    # ARRANGE
    request = {
        "tenant_id": "tenant_ca01",
        "channel": "test",
        "text": "RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY",
        "previous_progressive_context": None,
    }
    # ACT
    # response = invoke_tool("pymia.first_clinical_interview.v1", request)
    # ASSERT
    # assert response["status"] == "ok"
    # assert response["estado_conversacional"] == "encuadre_taxonomico_inicial"
    # assert response["anamnesis"]["hipotesis_iniciales"] == []
    # assert response["laboratorio"]["evidencia_requerida"] == []
    # assert response["progressive_context"] is not None
    # assert response["progressive_context"]["business_identity"]["taxonomy_phase"] is None
    pytest.skip("MCP server no disponible — test de contrato futuro (CA-01)")


# ---------------------------------------------------------------------------
# CA-02: Taxonomía confirmada con señal clínica → pipeline clínico
# ---------------------------------------------------------------------------

def test_ca02_taxonomy_confirmed_with_signal_runs_clinical_pipeline():
    """CA-02: taxonomy_phase=FASE_0_IDENTIDAD + señal clínica → esperando_documentacion."""
    # ARRANGE
    prev_ctx = {
        "tenant_id": "tenant_ca02",
        "channel": "test",
        "business_identity": {
            "display_name": None,
            "country_code": "AR",
            "industry_hint": "comercio",
            "taxonomy_phase": "FASE_0_IDENTIDAD",
        },
        "symptom_summary": [],
        "documents_requested": [],
    }
    request = {
        "tenant_id": "tenant_ca02",
        "channel": "test",
        "text": "creo que no estoy ganando plata",
        "previous_progressive_context": prev_ctx,
    }
    # ACT
    # response = invoke_tool("pymia.first_clinical_interview.v1", request)
    # ASSERT
    # assert response["status"] == "ok"
    # assert response["estado_conversacional"] == "esperando_documentacion"
    # assert len(response["anamnesis"]["hipotesis_iniciales"]) > 0
    # assert len(response["laboratorio"]["evidencia_requerida"]) > 0
    pytest.skip("MCP server no disponible — test de contrato futuro (CA-02)")


# ---------------------------------------------------------------------------
# CA-03: Taxonomía confirmada sin señal → no_signal
# ---------------------------------------------------------------------------

def test_ca03_taxonomy_confirmed_no_signal_returns_no_signal():
    """CA-03: taxonomy_phase=FASE_0_IDENTIDAD + texto sin señal → no_signal."""
    # ARRANGE
    prev_ctx = {
        "tenant_id": "tenant_ca03",
        "channel": "test",
        "business_identity": {
            "display_name": None,
            "country_code": "AR",
            "industry_hint": "servicios",
            "taxonomy_phase": "FASE_0_IDENTIDAD",
        },
        "symptom_summary": [],
        "documents_requested": [],
    }
    request = {
        "tenant_id": "tenant_ca03",
        "channel": "test",
        "text": "hola, como estas?",
        "previous_progressive_context": prev_ctx,
    }
    # ACT
    # response = invoke_tool("pymia.first_clinical_interview.v1", request)
    # ASSERT
    # assert response["status"] == "no_signal"
    # assert response["anamnesis"] is None
    # assert response["laboratorio"] is None
    # assert response["progressive_context"] is None
    pytest.skip("MCP server no disponible — test de contrato futuro (CA-03)")


# ---------------------------------------------------------------------------
# CA-05: Respuesta taxonómica actualiza progressive_context
# ---------------------------------------------------------------------------

def test_ca05_taxonomic_response_updates_progressive_context():
    """CA-05: Declaración de organismo actualiza industry_hint y taxonomy_phase."""
    # ARRANGE
    prev_ctx = {
        "tenant_id": "tenant_ca05",
        "channel": "test",
        "business_identity": {
            "display_name": None,
            "country_code": None,
            "industry_hint": None,
            "taxonomy_phase": None,
        },
        "symptom_summary": ["incertidumbre de rentabilidad"],
        "documents_requested": [],
    }
    request = {
        "tenant_id": "tenant_ca05",
        "channel": "test",
        "text": "somos una distribuidora de alimentos, 12 empleados",
        "previous_progressive_context": prev_ctx,
    }
    # ACT
    # response = invoke_tool("pymia.first_clinical_interview.v1", request)
    # ASSERT
    # ctx = response["progressive_context"]["business_identity"]
    # assert ctx["industry_hint"] == "logistica/distribucion"
    # assert ctx["country_code"] == "AR"
    # assert ctx["taxonomy_phase"] == "FASE_0_IDENTIDAD"
    pytest.skip("MCP server no disponible — test de contrato futuro (CA-05)")


# ---------------------------------------------------------------------------
# CA-06: Aislamiento de tenant
# ---------------------------------------------------------------------------

def test_ca06_tenant_isolation_violation_returns_error():
    """CA-06: Contexto de otro tenant → TENANT_ISOLATION_VIOLATION."""
    # ARRANGE
    prev_ctx = {
        "tenant_id": "tenant_OTRO",
        "channel": "test",
        "business_identity": {"taxonomy_phase": "FASE_0_IDENTIDAD"},
        "symptom_summary": [],
        "documents_requested": [],
    }
    request = {
        "tenant_id": "tenant_ca06",
        "channel": "test",
        "text": RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY,
        "previous_progressive_context": prev_ctx,
    }
    # ACT
    # response = invoke_tool("pymia.first_clinical_interview.v1", request)
    # ASSERT
    # assert response["status"] == "error"
    # assert response["error_code"] == "TENANT_ISOLATION_VIOLATION"
    pytest.skip("MCP server no disponible — test de contrato futuro (CA-06)")


# ---------------------------------------------------------------------------
# CA-08: El encuadre no menciona términos diagnósticos
# ---------------------------------------------------------------------------

def test_ca08_taxonomic_framing_contains_no_diagnostic_terms():
    """CA-08: El mensaje de encuadre taxonómico no debe contener terminología diagnóstica."""
    # ARRANGE
    request = {
        "tenant_id": "tenant_ca08",
        "channel": "test",
        "text": "hola, quiero mejorar mi negocio",
        "previous_progressive_context": None,
    }
    # FORBIDDEN_TERMS = [
    #     "margen erosionado", "tensión de caja", "fuga operativa",
    #     "hipótesis", "laboratorio", "incertidumbre de rentabilidad"
    # ]
    # ACT
    # response = invoke_tool("pymia.first_clinical_interview.v1", request)
    # ASSERT
    # assert response["estado_conversacional"] == "encuadre_taxonomico_inicial"
    # msg = response["message"].lower()
    # for term in FORBIDDEN_TERMS:
    #     assert term not in msg, f"Término diagnóstico prematuro en encuadre: '{term}'"
    pytest.skip("MCP server no disponible — test de contrato futuro (CA-08)")
```

---

## 11. Notas de implementación (para cuando se desarrolle el server MCP)

- La tool debe invocar internamente `ClinicalConversationalPort.handle()` o equivalente.
- El server MCP de PymIA debe ser **stateless**: no persiste `progressive_context` por sí mismo. La persistencia es responsabilidad de Hermes (o de las tools auxiliares `progressive_context_load` / `progressive_context_save` si se implementan como tools MCP separadas).
- La validación de `TENANT_ISOLATION_VIOLATION` debe realizarse en la capa de la tool, antes de invocar el kernel clínico.
- El servidor debe loguear cada invocación con: `tenant_id`, `tool_name`, `estado_conversacional_output`, `duration_ms`.
- El server no debe exponer stack traces en producción. Los errores `UNKNOWN_ERROR` deben loguearse internamente y devolver solo el `error_code` al cliente.

---

## 12. Trazabilidad

### Documentos de referencia
- [ADR-008: Hermes MCP client → PymIA MCP server](file:///e:/BuenosPasos/smartbridge/PymIA/docs/adr/ADR-008-hermes-mcp-client-pymia-mcp-server.md)
- [ADR-006: TenantClinicalContext como input del boundary](file:///e:/BuenosPasos/smartbridge/PymIA/docs/adr/ADR-006-tenant-clinical-context-as-input.md)
- [CONTRATO_PRIMER_ENCUENTRO_TAXONOMICO.md](file:///e:/BuenosPasos/smartbridge/PymIA/docs/arquitectura/CONTRATO_PRIMER_ENCUENTRO_TAXONOMICO.md)

### Código fuente de referencia
- [`pymia/services/initial_laboratory_anamnesis_service.py`](file:///e:/BuenosPasos/smartbridge/PymIA/pymia/services/initial_laboratory_anamnesis_service.py)
- [`pymia/interfaces/conversational_port.py`](file:///e:/BuenosPasos/smartbridge/PymIA/pymia/interfaces/conversational_port.py)
- [`tests/document_intelligence/test_phase2f_taxonomic_first_contact.py`](file:///e:/BuenosPasos/smartbridge/PymIA/tests/document_intelligence/test_phase2f_taxonomic_first_contact.py)

### Commits relacionados
- `08ede6c` feat(clinical-context): close phase zero taxonomic identity
- `e4b0d2c` test(clinical-context): align legacy anamnesis tests with phase zero
- `41e3990` feat(conversa): preserve progressive context roundtrip
