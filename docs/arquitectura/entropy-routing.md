Contexto alineado. No autoriza runtime, MCP, jobs, workflows ni orquestación dentro de PymIA. Rige ARCHITECTURE_GUARDRAILS.md y la doctrina de SEMANTICA_CONVERSACIONAL_PYMIA_HERMES_BEM.md.

# Entropy Routing and Sovereign Ingestion

**Status:** Accepted  
**Ámbito:** Gestión de entropía documental e ingesta

---

## 1. Axioma Arquitectónico y Doctrina

* **PymIA no cree: contrasta.**
* **Hermes no supone: pregunta.**
* **BEM no diagnostica: extrae.**
* **La hipótesis no es diagnóstico.**

---

## 2. Contexto de Entrada Documental

SmartPyme/PymIA procesa múltiples formatos de evidencia aportados por el dueño:

* **PDFs e imágenes de alta entropía:** Facturas impresas, capturas de pantalla, remitos escaneados.
* **Hojas de cálculo (.xlsx, .csv) limpias y estructuradas:** Planillas de ventas o stock ordenadas y predecibles.
* **Relatos humanos de texto (NARRATIVE):** Declaraciones de síntomas e intenciones en el chat.

Para evitar saturación computacional en el core y asegurar la soberanía del cálculo matemático, se implementa una clasificación y enrutamiento disciplinado según el nivel de entropía.

---

## 3. Las Tres Rutas de Entrada Oficiales

La asimilación de cualquier input se canaliza estrictamente a través de estas tres vías del `AuditBoundaryGraph`:

### A. BEM_AI (Frontera de Apoyo Externa)
Destinada a todos los **PDFs, imágenes de facturas y hojas de cálculo con entropía elevada ($> 0.3$)**.
* El procesamiento pesado (OCR, layouts, extracción multimodal) se terceriza en la frontera auxiliar externa.
* **Regla estricta:** Todo resultado de extracción devuelto por `BEM_AI` tiene rango exclusivo de **evidencia candidata**. Jamás se asume como diagnóstico consolidado ni verdad probada hasta que el kernel de PymIA convalide su consistencia matemática.

### B. INTERNAL_FACT (Ingesta Local Controlada)
Destinada de forma exclusiva a **planillas estructuradas (.xlsx, .csv) limpias, con un esquema de columnas esperado y baja entropía ($\le 0.3$)**.
* El parser local de `conversa-engine` procesa el archivo síncronamente y lanza la auditoría local del kernel de forma síncrona y fail-closed, eludiendo llamadas a IAs externas.
* **Principio de Madurez:** A medida que PymIA desarrolle parsers síncronos e internos más estables y seguros, el ecosistema debe **depender cada vez menos de BEM**, consolidando una ingesta directa limpia.

### C. NARRATIVE (Admisión Conversacional)
Destinada exclusivamente al procesamiento de **chats en texto plano, quejas y respuestas mayéuticas**. Alimenta de forma secuencial la fase de anamnesis de primer contacto liderada por Hermes.

---

## 4. Separación Estricta de Dominios

```text
               Entrada Física (Documento / Chat)
                              │
                              ▼
                    [Triage de Entropía]
                              │
       ┌──────────────────────┼──────────────────────┐
       ▼                      ▼                      ▼
  [BEM_AI]             [INTERNAL_FACT]          [NARRATIVE]
 (PDF/Imagen)         (Excel limpio)           (Texto plano)
       │                      │                      │
       ▼                      ▼                      ▼
 Evidencia Candidata ──> [PymIA (Kernel)] <─── Anamnesis Inicial
```

### Dominio BEM (Extractor y Coprocesador Documental)
* **Responsabilidades:** Route, Split, OCR visual complejo, reducción de caos de columnas.
* **Prohibición absoluta:** BEM no calcula métricas del negocio, no evalúa patologías del catálogo de fórmulas, no gestiona la memoria de la conversación y no formula hallazgos (findings) operativos.

### Dominio PymIA (Soberano de la Verdad Científica)
* **Responsabilidades:** Evaluación del catálogo de fórmulas, contraste de consistencia interna de la evidencia, cálculo matemático, señales operativas, hilos de auditoría y emisión del diagnóstico en el `OperationalAuditResult`.
* PymIA es el único runtime epistemológico-operativo soberano.

---

## 5. Clarification Gate

Si el nivel de confianza del enrutamiento es bajo, la extracción resulta ambigua, o se detectan discrepancias o contradicciones graves entre el relato subjetivo del dueño y los números reales de la planilla:
* El estado del flujo se marca inmediatamente como bloqueado (`BLOCKED_BY_AMBIGUITY`).
* Hermes entra en acción formulando una **pregunta de rigor o de inteligencia mayéutica** para resolver la ambigüedad de forma guiada antes de habilitar el cálculo clínico.
