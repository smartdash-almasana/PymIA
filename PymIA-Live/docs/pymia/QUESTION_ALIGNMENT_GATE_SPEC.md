# QUESTION ALIGNMENT GATE SPEC — PYMIA-LIVE

## Estado
- **Clasificación:** `SPEC_ONLY`
- **Cambio en Runtime:** `NO_RUNTIME_CHANGE`
- **Ámbito:** Documento conceptual de diseño previo a implementación

---

## 1. Propósito
Definir las especificaciones y contratos conceptuales mínimos para una compuerta inteligente denominada `QuestionAlignmentGate`. Esta compuerta tiene como fin alinear la próxima pregunta sugerida por el sistema con:
1. El síntoma prioritario expresado por el dueño de la PyME (`owner_message`).
2. La evidencia detectada y variables computadas en el Excel (`structured_evidence_summary`).
3. La pregunta de auditoría candidata generada de forma secuencial por la reconciliación del catálogo (`catalog_reconciliation`).

---

## 2. Problema Actual
En el baseline clínico actual (`f4494a3`), la reconciliación del catálogo se ejecuta secuencialmente y propone como próxima pregunta el primer faltante de información técnica que encuentra. Esto genera un desfase conversacional cuando el dueño declara un problema específico y el sistema reacciona con una pregunta de otro ámbito.

**Ejemplo de Drift Conversacional:**
- **Owner message:** *"Tengo una textil y no me cierra la caja, no sé a dónde se va la plata."* (Eje prioritario: caja/liquidez).
- **Catalog reconciliation:** Encuentra que en el catálogo falta la variable `lead_time_proveedor` para calcular el punto de reposición (`INV_001`).
- **Resultado actual:** La próxima pregunta automática interroga sobre los tiempos de entrega de proveedores, lo cual es técnicamente coherente pero conversacionalmente desalineado y confuso para el dueño en su primer contacto.

---

## 3. Límites Explícitos
Para evitar la deriva funcional del proyecto, se establecen los siguientes límites estrictos:
- **No Diagnóstico:** El gate no infiere patologías ni genera conclusiones clínicas.
- **No Interpreta Negocio:** No realiza análisis financieros ni contables complejos sobre las variables.
- **No LLM / No AI Generativa:** La alineación se basa en reglas determinísticas y mapeos de palabras clave de baja complejidad; no se integra ningún modelo de lenguaje grande (LLM).
- **No Reemplaza al Operador:** Es una ayuda de priorización conversacional local; el operador técnico sigue gobernando la reconducción humana en el piloto asistido.
- **No Modifica Records:** No altera el contrato ni los datos de `EvidenceRecord` ni de `PipelineRunRecord`.
- **No Altera Código:** Este documento es meramente descriptivo. Queda estrictamente prohibido modificar [vertical_slice.py](file:///e:/BuenosPasos/smartbridge/PymIA/PymIA-Live/pymia/cli/vertical_slice.py) hasta que esta especificación sea aprobada.

---

## 4. Inputs Conceptuales Mínimos
La compuerta requiere de cuatro entradas estructuradas para resolver la alineación:
- `owner_message` (str): Texto crudo provisto por el dueño de la PyME.
- `catalog_reconciliation` (list[dict]): Lista de desajustes y variables faltantes arrojados por el comparador del catálogo.
- `structured_evidence_summary` (dict): Conjunto de variables y tablas detectadas en la planilla.
- `candidate_question` (str): Pregunta candidata inicial generada por el pipeline sin el filtro de alineación.

---

## 5. Outputs Conceptuales Mínimos
El resultado de evaluar el Gate debe ser clasificado en uno de los tres estados siguientes:
- `ALIGNED`: La pregunta candidata se alinea con el síntoma del dueño. Se emite la pregunta automáticamente.
- `MISALIGNED`: La pregunta candidata pertenece a un eje diferente al síntoma prioritario. Se bloquea la emisión automática y se solicita la reconducción del operador humano.
- `UNKNOWN`: No hay suficiente información o el mensaje del dueño es ambiguo. Se emite una pregunta neutra de aclaración o validación general.

---

## 6. Modelo Conceptual Mínimo
Se definen los siguientes tipos de datos y objetos conceptuales (contratos de diseño, no código de ejecución):

```typescript
interface OwnerDeclaredAxis {
    axis_code: EjeInicial;
    confidence: "high" | "low";
    matched_keywords: string[];
}

interface EvidenceDetectedAxis {
    axis_code: EjeInicial;
    has_variables: boolean;
    has_tables: boolean;
}

interface CandidateQuestionAxis {
    axis_code: EjeInicial;
    formula_id: string;
    pathology_code: string;
}

interface QuestionAlignmentGateResult {
    status: "ALIGNED" | "MISALIGNED" | "UNKNOWN";
    declared_axis: EjeInicial;
    question_axis: EjeInicial;
    final_question_text: string;
    technical_reference: string;
}
```

---

## 7. Ejes Iniciales Permitidos
El gate clasificará los síntomas y preguntas bajo una taxonomía cerrada de ejes operacionales de la PyME:
- `caja_liquidez` (conceptos de cobros, pagos, saldos bancarios, disponibilidad, caja diaria).
- `ventas_margen` (volumen de ventas, facturación, rentabilidad, márgenes brutos/netos).
- `stock_reposicion` (rotación de inventario, stock de seguridad, faltantes, reposición, mermas).
- `costos_proveedores` (costos de insumos, facturas de compras, cuentas por pagar a proveedores).
- `produccion` (tiempos de elaboración, materias primas, mermas en planta).
- `rrhh` (sueldos, carga laboral, horas extra, dotación).
- `automatizacion_manual` (carga de horas manuales, automatización de planillas, procesos).
- `desconocido` (fallback para textos ambiguos, saludos o campos vacíos).

---

## 8. Reglas de Alineación Mínimas
1. **Regla de Caja/Stock (Bloqueo de Desviación):** Si el síntoma prioritario de `owner_message` se clasifica en el eje `caja_liquidez` y la pregunta candidata (`candidate_question`) se asocia a `stock_reposicion`, el resultado es obligatoriamente `MISALIGNED`.
2. **Regla de Caja/Banco (Alineación Exitosa):** Si el síntoma de `owner_message` es `caja_liquidez` y la pregunta candidata requiere extractos, saldo de caja, banco, cobranzas o deudas de corto plazo, el resultado es `ALIGNED`.
3. **Regla de Ambigüedad (Fallback Neutro):** Si el mensaje del dueño es genérico (ej: *"quiero analizar mi negocio"*), el resultado es `UNKNOWN` y se opta por una pregunta aclaratoria general.
4. **Regla de Vacío de Mensaje:** Si no se ingresa `--message` o es una cadena vacía, el resultado es `UNKNOWN`.
5. **Regla de Vacío de Pregunta:** Si no hay pregunta técnica candidata generada por la reconciliación, el resultado es `UNKNOWN`.

---

## 9. Punto de Inserción Futuro
De acuerdo con [PYMIA_LIVE_PIPELINE.md](file:///e:/BuenosPasos/smartbridge/PymIA/PymIA-Live/docs/pymia/PYMIA_LIVE_PIPELINE.md), la evaluación del gate se insertará en el siguiente punto lógico del pipeline:

```text
catalog_reconciliation
        ↓
[QuestionAlignmentGate]  <-- PUNTO DE INTEGRACIÓN
        ↓
_build_owner_question(entry)
```

---

## 10. Casos de Aceptación Documentales

- **Caso 1 (Caja a Banco):**
  - *Mensaje:* *"No tengo efectivo para pagar los sueldos mañana."* (`caja_liquidez`)
  - *Pregunta Candidata:* *"¿Podés enviarnos el saldo inicial de caja y banco?"* (`caja_liquidez`)
  - *Resultado esperado:* `ALIGNED`
- **Caso 2 (Caja a Stock):**
  - *Mensaje:* *"No sé por qué nunca tengo plata en el banco."* (`caja_liquidez`)
  - *Pregunta Candidata:* *"¿Podés compartir los tiempos de reposición de proveedores?"* (`stock_reposicion`)
  - *Resultado esperado:* `MISALIGNED`
- **Caso 3 (Margen a Costos):**
  - *Mensaje:* *"Vendo un montón pero no me queda margen neto de ganancia."* (`ventas_margen`)
  - *Pregunta Candidata:* *"¿Podés detallar los costos directos de tus productos?"* (`costos_proveedores` / `ventas_margen`)
  - *Resultado esperado:* `ALIGNED`
- **Caso 4 (Mensaje Ambiguo):**
  - *Mensaje:* *"Hola, quiero que revisen mi planilla por favor."* (`desconocido`)
  - *Pregunta Candidata:* *"Falta información sobre reposición de stock. ¿Podés compartir el stock de seguridad?"* (`stock_reposicion`)
  - *Resultado esperado:* `UNKNOWN` (se emite una pregunta neutra de validación de columnas o proceso real).
- **Caso 5 (Sin mensaje):**
  - *Mensaje:* *""* (`desconocido`)
  - *Pregunta Candidata:* *"¿Podés detallar el CMVs de este periodo?"* (`costos_proveedores`)
  - *Resultado esperado:* `UNKNOWN`

---

## 11. Anti-Deriva
Queda terminantemente prohibido incorporar las siguientes lógicas o deudas:
- No estructurar flujos conversacionales dinámicos que guarden estados complejos.
- No utilizar agentes reactivos de LangGraph, LangChain o arquitecturas de grafos.
- No reabrir los frentes de mensajería externos de Telegram, Discord o Hermes.
- No modificar ni acoplar `PipelineRunRecord` ni `EvidenceRecord` con los ejes de alineación; la alineación es puramente una compuerta de filtro de interfaz.
- No escribir código en `vertical_slice.py` hasta que esta especificación conceptual esté aprobada por auditoría.

---

## 12. Recomendación Final
> [!IMPORTANT]
> Auditar rigurosamente esta especificación conceptual para verificar su coherencia doctrinal y técnica antes de proceder con el diseño de los tests unitarios o la implementación del código en el subpaquete `pymia/diagnostic_core`.
