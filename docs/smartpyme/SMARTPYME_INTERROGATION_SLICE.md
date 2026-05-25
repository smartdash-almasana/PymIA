# SMARTPYME_INTERROGATION_SLICE

Estado: **IMPLEMENTADO (slice mínimo determinístico)**

## Qué implementa

Un slice mínimo determinístico de **interrogatorio inicial** previo a cualquier análisis SmartPyme.

Recibe:
- `raw_text`: relato libre del usuario (texto o transcripción de audio);
- `structured_selectors` (opcional): contexto estructural breve del negocio.

Devuelve un `InterrogationResult` con:
- `raw_input` preservado literal;
- `normalized_terms` (señales léxicas detectadas);
- `business_context` (selectores normalizados);
- `reformulation` no diagnóstica;
- `confirmation_question` para validar con el usuario;
- `semantic_signals`, `candidate_symptoms`, `candidate_domains`;
- `clarification_questions` (desambiguación);
- `evidence_needs` (qué evidencia pedir y por qué);
- `status` del interrogatorio;
- `suggested_classification` opcional (`excel_diagnostic` o `supplier_duplicate_check`).

## Qué NO implementa

- **No diagnostica.** Solo sugiere síntomas candidatos y dominios.
- **No ejecuta análisis.** No corre `excel_diagnostic` ni `supplier_duplicate_check`.
- **No procesa documentos.** Solo indica qué evidencia pedir.
- **No reemplaza clasificaciones existentes.** Las menciona como posibilidad.
- **No usa IA ni modelos.** Es 100% determinístico.
- **No hace fuzzy matching avanzado.** Usa detección léxica simple.
- **No asume Hermes real, Output Gateway, Telegram ni producción.**

## Relación con documentos previos

| Documento | Rol |
|---|---|
| `SMARTPYME_INTERROGATION_TAXONOMY.md` | Capa taxonómica: qué capturar, estados, preguntas, clasificación sugerida. |
| `SMARTPYME_SEMANTIC_DIALECTIC_PHASE.md` | Capa conversacional: cómo escuchar, reformular, confirmar, desambiguar. |
| **Este documento** | Implementación mínima del slice: entrada → resultado estructurado. |

Los tres documentos son complementarios:
- **Taxonomía** define el "qué".
- **Fase semántico-dialéctica** define el "cómo".
- **Slice** es la unidad ejecutable mínima que materializa ambos.

## Modelo de datos

### `StructuredSelectors`
- `sales_channel`: Local / Mayorista / Mercado Libre / Ecommerce / Instagram / Mixto
- `operation_type`: Revendo / Produzco / Servicios / Distribuyo / Mixto
- `stock_mode`: Sí / No / Informal
- `tools_used`: Excel / Sistema / Cuaderno / Varios
- `evidence_available`: Excel / PDF / Capturas / AudioTexto / NoSe
- `employee_range`
- `marketplace_presence`

### `InterrogationResult`
Ver `pymia/smartpyme/interrogation.py`.

### Estados (`status`)
- `RAW_CAPTURED`
- `NEEDS_ORGANISM_CONTEXT`
- `OWNER_CLAIM_REFORMULATED`
- `WAITING_OWNER_CONFIRMATION`
- `NEEDS_DISAMBIGUATION`
- `HYPOTHESIS_OPEN`
- `NEEDS_EVIDENCE`
- `READY_FOR_TAXONOMIC_ROUTING`
- `BLOCKED_INSUFFICIENT_CONTEXT`

### Síntomas operacionales mínimos
- `DESCUADRE_DINERO`
- `MARGEN_DUDOSO`
- `DATOS_DUPLICADOS`
- `STOCK_INCONSISTENTE`
- `SOBRECARGA_MANUAL`
- `COSTO_INCIERTO`
- `DOCUMENTACION_DESORDENADA`
- `MAESTRO_DESORDENADO`
- `DESCONOCIDO`

### Dominios candidatos
- `finanzas`, `comercial`, `proveedores`, `stock`, `produccion`,
  `administracion`, `automatizacion`, `datos_maestros`, `desconocido`

## Reglas determinísticas implementadas

1. **"no me cierra / plata / caja / banco / cobros"**
   → `DESCUADRE_DINERO`, dominio `finanzas`, `NEEDS_DISAMBIGUATION`, sin clasificación.

2. **"vendo / no me queda / margen / precio / costo"**
   → `MARGEN_DUDOSO` o `COSTO_INCIERTO`, dominio `comercial`.
   → Solo sugiere `excel_diagnostic` si hay evidencia tabular.

3. **"proveedores / duplicados / cuit / razón social"**
   → `DATOS_DUPLICADOS` + `MAESTRO_DESORDENADO`, dominios `proveedores` + `datos_maestros`.
   → Sugiere `supplier_duplicate_check`.

4. **"stock / depósito / faltante / sistema dice"**
   → `STOCK_INCONSISTENTE`, dominio `stock`.

5. **"copio / a mano / manual / doble carga / Excel imposible"**
   → `SOBRECARGA_MANUAL` o `DOCUMENTACION_DESORDENADA`.

6. **Texto corto o ambiguo**
   → `DESCONOCIDO`, `NEEDS_DISAMBIGUATION` o `NEEDS_ORGANISM_CONTEXT`.

## Selectores estructurales

Se integran al `business_context` pero **no inducen diagnóstico**.
Solo refinan dominio y clasificación cuando el `raw_text` ya aporta señal compatible.

Ejemplo: relato "quiero revisar mi negocio" + selectores Mercado Libre + Excel
→ `business_context` poblado, `status` `NEEDS_DISAMBIGUATION`, sin clasificación cerrada.

## API

```python
from pymia.smartpyme.interrogation import (
    StructuredSelectors,
    run_interrogation,
)

r = run_interrogation(
    "Tengo proveedores duplicados y CUIT mezclados",
    structured_selectors=StructuredSelectors(evidence_available="Excel"),
)
print(r.to_dict())
```

## CLI de demo

```powershell
# 5 casos demo
python -m pymia.smartpyme.interrogation_cli --demo-out .tmp\smartpyme-interrogation-slice\output\interrogation_demo.json --pretty

# Caso único
python -m pymia.smartpyme.interrogation_cli --text "No me cierra la plata"
```

## Ejemplos de entrada/salida

### 1. "No me cierra la plata"
```json
{
  "raw_input": "No me cierra la plata",
  "candidate_symptoms": ["DESCUADRE_DINERO"],
  "candidate_domains": ["finanzas"],
  "status": "NEEDS_DISAMBIGUATION",
  "suggested_classification": null,
  "reformulation": "Entiendo que la señal principal es que la plata no cierra, pero todavía no sabemos si viene de caja, margen, cobros o gastos."
}
```

### 2. "Tengo proveedores duplicados y CUIT mezclados"
```json
{
  "raw_input": "Tengo proveedores duplicados y CUIT mezclados",
  "candidate_symptoms": ["DATOS_DUPLICADOS", "MAESTRO_DESORDENADO"],
  "candidate_domains": ["proveedores", "datos_maestros"],
  "status": "NEEDS_EVIDENCE",
  "suggested_classification": "supplier_duplicate_check",
  "evidence_needs": [
    {
      "evidence_type": "excel_proveedores",
      "required_fields": ["proveedor", "cuit", "razon_social"]
    }
  ]
}
```

## Límites

- No reemplaza conversación real.
- No garantiza cobertura de todos los síntomas PyME.
- No valida evidencia.
- No persiste estado entre turnos.
- No soporta múltiples idiomas.

## Próximos frentes sugeridos

- `SMARTPYME_INTAKE_RECORD_AND_EVIDENCE_REQUEST`: persistir el resultado del interrogatorio y emitir pedidos de evidencia concretos.
- `SMARTPYME_INTERROGATION_MULTITURN`: soportar conversación de varias vueltas hasta llegar a `READY_FOR_TAXONOMIC_ROUTING`.
- `SMARTPYME_DEMO_WITH_INTAKE_BEFORE_REPORT`: demo que muestre interrogatorio → evidencia → análisis → reporte.

## Archivos

- `pymia/smartpyme/interrogation.py` — implementación
- `pymia/smartpyme/interrogation_cli.py` — CLI de demo
- `tests/smartpyme/test_interrogation.py` — tests
