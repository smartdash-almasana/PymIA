# Diseño Transitorio de Inteligencia Documental y Contexto Clínico del Tenant
**Especificación del Contrato TenantClinicalContext y su Integración con el Motor de Inferencia**

> [!NOTE]
> * **Estado**: DISEÑO_TRANSITORIO_VIGENTE
> * **Fecha**: 2026-05-22
> * **Dueño Conceptual**: PymIA Document Intelligence Subsystem
> * **Diseño de Referencia**: [ADR-004](file:///opt/PymIA/docs/adr/ADR-004-bem-como-fallback-pasivo.md), [ADR-005](file:///opt/PymIA/docs/adr/ADR-005-document-intelligence-engine.md), [ADR-006](file:///opt/PymIA/docs/adr/ADR-006-tenant-clinical-context-as-input.md), [ADR-007](file:///opt/PymIA/docs/adr/ADR-007-documentation-governance.md).

---

## 1. El Concepto de TenantClinicalContext

El principal hallazgo de la primera y segunda auditoría de PymIA es que **los archivos Excel no se pueden interpretar de forma confiable en el vacío**. Un mismo encabezado (como `"costo"`) o un mismo conjunto de números adquieren significados operativos diametralmente opuestos según el tipo de empresa (distribuidora mayorista vs. empresa de servicios) y las hipótesis clínicas activas en su ficha médica contable.

Por tanto, se prohíbe la interpretación ciega de adjuntos. El motor de inferencia semántica local de PymIA debe alimentarse de forma obligatoria de un **`TenantClinicalContext`** provisto por el canal conversacional antes de abrir cualquier planilla física.

```mermaid
flowchart TD
    subgraph Entrada ["Canal de Comunicación"]
        TC["TenantClinicalContext (Contexto Clínico)"]
        EX["Archivo Físico (Excel / CSV)"]
    end

    subgraph Motor ["Document Intelligence Subsystem"]
        ONT["PymeColumnOntology (Vocabulario + Pesos por Industria)"]
        HIST["HistoricalColumnMapping (Historial del Tenant)"]
        POL["Polars Mathematical Validator (Constraint SAT)"]
        BSE["BusinessSchemaInferenceEngine"]
    end

    subgraph Salida ["Admisión en Kernel PymIA"]
        EB["EvidenceBundle (Normalizado + Validado)"]
        FIO["Ficha Informativa Opacidad (FIO)"]
    end

    TC --> BSE
    EX --> BSE
    ONT --> BSE
    HIST --> BSE
    BSE --> POL
    POL -->|Éxito (Matemática Cierra)| EB
    POL -->|Fallo o Confianza < 0.75| FIO
```

---

## 2. Contratos Estructurados de Datos (Python 3.10)

A continuación, se definen los contratos formales para el contexto del tenant, la ontología y el motor de inferencia:

### 2.1. `TenantClinicalContext` (Contrato del Contexto Clínico)
* **Responsabilidad**: Suministrar al motor de inferencia la información pre-admitida sobre el sector de actividad, las hipótesis contables bajo investigación y el historial clínico inicial de la PyME.
* **Estructura de Datos**:
  ```python
  from enum import Enum
  from typing import Optional
  from dataclasses import dataclass, field

  class IndustrySector(str, Enum):
      WHOLESALE_DISTRIBUTION = "WHOLESALE_DISTRIBUTION"  # Mayoristas / Distribuidoras
      RETAIL = "RETAIL"                                  # Comercio minorista
      SERVICES = "SERVICES"                              # Empresas de servicios
      MANUFACTURING = "MANUFACTURING"                    # Producción / Manufactura

  class ClinicalHypothesis(str, Enum):
      REN_001_LOW_MARGINS = "REN_001_LOW_MARGINS"        # Sospecha de quiebre de margen bruto
      PYME_033_SKU_CONCENTRATION = "PYME_033_SKU_CONCENTRATION" # Concentración crítica de SKU
      LIQ_001_CASH_TENSION = "LIQ_001_CASH_TENSION"      # Tensión de liquidez operativa
      LOG_002_LOGISTIC_EFFICIENCY = "LOG_002_LOGISTIC_EFFICIENCY" # Ineficiencia de rutas comerciales

  @dataclass(frozen=True)
  class TenantClinicalContext:
      tenant_id: str
      business_name: str
      sector: IndustrySector
      active_hypotheses: list[ClinicalHypothesis] = field(default_factory=list)
      initial_clinical_notes: str = ""                   # Historia clínica en lenguaje natural
      known_dimensions: dict[str, list[str]] = field(default_factory=dict) # E.g., {"rutas": ["Norte", "Sur"]}
  ```
* **Invariantes**:
  * Un `TenantClinicalContext` válido debe poseer obligatoriamente un `tenant_id` no vacío y un `sector` tipificado dentro del enum.
  * La historia clínica inicial (`initial_clinical_notes`) no puede ser vacía si no hay hipótesis activas cargadas previamente.

### 2.2. `HistoricalColumnMapping` (Historial de Mapeos del Tenant)
* **Responsabilidad**: Registrar decisiones y confirmaciones anteriores realizadas por este tenant para reutilizar mappings semánticos ya aprobados, acelerando la confianza del autodescubrimiento de esquemas.
* **Estructura de Datos**:
  ```python
  @dataclass(frozen=True)
  class HistoricalColumnMapping:
      tenant_id: str
      raw_header_name: str         # Nombre de columna física de Excel
      approved_canonical_field: str # BusinessVariable asignada en el pasado
      confidence_weight: float = 1.0 # Peso de reutilización (se degrada si cambia el contexto)
  ```

### 2.3. `PymeColumnOntology` (Ontología Contextual)
* **Responsabilidad**: Enriquecer los sinónimos y pesos lingüísticos en función del sector industrial del tenant para elevar la precisión de la inferencia semántica.
* **Estructura de Datos**:
  ```python
  @dataclass(frozen=True)
  class OntologyTerm:
      canonical_variable: str
      synonyms: list[str]
      base_probability: float
      sector_modifiers: dict[IndustrySector, float] # Ajustes de peso según la industria

  class PymeColumnOntology:
      def __init__(self, sector: IndustrySector):
          self.sector = sector
          self._vocabulary: list[OntologyTerm] = []

      def get_score_modifier(self, variable: str) -> float:
          # Modifica la probabilidad sintáctica basándose en el sector del tenant.
          # E.g., para WHOLESALE_DISTRIBUTION, "ruta" y "cliente" reciben un modificador de +0.35.
          pass
  ```

---

## 3. Dinámica del BusinessSchemaInferenceEngine

El motor de inferencia semántica unificado combina tres factores lógicos ponderados para mapear una columna física:

$$S_{total} = w_1 \cdot S_{sintactico} + w_2 \cdot S_{contexto} + w_3 \cdot S_{historial}$$

1. **Score Sintáctico ($S_{sintactico}$)**: Similitud lingüística difusa (ej. Jaro-Winkler) entre el encabezado físico del Excel y el término de la ontología oficial.
2. **Score de Contexto ($S_{contexto}$)**: Inyección de pesos contextuales derivados del `TenantClinicalContext`. Si el tenant pertenece al sector `WHOLESALE_DISTRIBUTION`, las variables canónicas `RUTA` y `CLIENTE` incrementan significativamente su expectativa matemática e inmunidad semántica.
3. **Score de Historial ($S_{historial}$)**: Reutilización de mapeos confirmados previamente en `HistoricalColumnMapping` para el mismo `tenant_id`.

Una vez calculado el mapping tentativo para todas las columnas de la planilla física, el **Polars Mathematical Validator (Constraint SAT)** ejecuta las ecuaciones financieras cruzadas:

```python
# Pseudo-código de validación cruzada en Polars Engine
def validate_mathematical_consistency(df: pl.DataFrame, schema: SemanticSchema) -> list[MathematicalConsistencyCheck]:
    checks = []
    
    # Evaluar Venta - Costo = Margen
    if has_monetary_columns(schema, ["venta_total", "costo_total", "margen_bruto"]):
        # df: Polars DataFrame
        delta = df.select(
            (pl.col("venta_total") - pl.col("costo_total") - pl.col("margen_bruto")).abs().mean()
        ).item()
        
        satisfied = delta < 0.01  # Menor al 1% de error de redondeo
        checks.append(MathematicalConsistencyCheck(
            equation="venta_total - costo_total = margen_bruto",
            satisfied=satisfied,
            evaluated_rows=len(df),
            matched_rows=compute_matched_rows(df, "venta_total - costo_total = margen_bruto"),
            residual_error=delta
        ))
        
    return checks
```

---

## 4. Análisis del Caso Real: `distribuidora_mayorista_compleja.xlsx`

Bajo el nuevo esquema arquitectónico enriquecido con el contexto clínico del tenant, el caso problemático de la distribuidora mayorista se resuelve de manera determinista sin molestar al usuario final:

### Entrada de Contexto Conversacional:
El canal conversacional (Hermes) recibe el archivo junto con el siguiente contexto inicial:
```python
context = TenantClinicalContext(
    tenant_id="tenant_distribuidora_01",
    business_name="Distribuidora de Bebidas del Sur",
    sector=IndustrySector.WHOLESALE_DISTRIBUTION,
    active_hypotheses=[
        ClinicalHypothesis.REN_001_LOW_MARGINS,
        ClinicalHypothesis.LOG_002_LOGISTIC_EFFICIENCY
    ],
    initial_clinical_notes="El dueño sospecha que algunas rutas de despacho reportan márgenes negativos."
)
```

### Inferencia del Motor sobre las Columnas del Excel:

1. **Resolución de `"cantidad"`**:
   * *Ontología + Contexto*: Como el sector es `WHOLESALE_DISTRIBUTION` y la variable canónica `CANTIDAD` es de tipo `METRIC_QUANTITY`, el sistema identifica coincidencia lingüística de alta confianza y anula de forma absoluta cualquier asunción de ambigüedad.
   * *Resultado*: Mapeado a `BusinessVariable.CANTIDAD` con confianza integral `1.0`. **No hay preguntas al dueño.**

2. **Resolución de `"margen"`**:
   * *Ontología*: `"margen"` es reconocido nativamente por el vocabulario unificado de `PymeColumnOntology` como la métrica contable `BusinessVariable.MARGEN_BRUTO`.
   * *Resultado*: Mapeado a `BusinessVariable.MARGEN_BRUTO`. **No hay marcas unknown.**

3. **Resolución de `"ruta"`**:
   * *Contexto*: El `TenantClinicalContext` tiene la hipótesis activa de ineficiencia logística (`LOG_002`). La ontología aumenta el peso de la variable canónica `RUTA` en el ruteo de distribución mayorista.
   * *Resultado*: Mapeado a `BusinessVariable.RUTA` con confianza sintáctica-contextual alta como `ColumnRole.DIMENSION`. **No hay marcas unknown.**

4. **Resolución de `"costo"` total vs. unitario**:
   * *Validator en Polars*:
     El motor detecta que las columnas candidatas son `venta`, `costo`, y `margen`.
     * Ejecuta **Ecuación 1 (Costo Total)**: `df["venta"] - df["costo"] == df["margen"]`.
     * El validador de Polars comprueba que la ecuación se satisface para el 100% de las filas de la planilla física.
   * *Resultado*: El motor infiere automáticamente que `"costo"` representa `BusinessVariable.COSTO_TOTAL`. Eleva la confianza relacional a `1.0` y **cancela de forma absoluta cualquier pregunta al dueño**. El archivo se procesa en modo 100% automático.

---

## 5. Invariantes del Sistema

Para certificar la integridad del pipeline de Inteligencia Documental, la implementación de Opus 4.6 debe validar de forma restrictiva el cumplimiento de las siguientes condiciones lógicas:

1. **Invariante de Contexto Obligatorio**: No se permite la ejecución de la inferencia de esquemas sobre planillas físicas si la instancia de `TenantClinicalContext` no ha sido inyectada y validada en el pipeline de entrada.
2. **Invariante de Consistencia Matemática**: Si la validación relacional contable cruzada ($V - C = M$) es SATISFECHA, el score de confianza relacional de las variables involucradas debe forzarse invariablemente a `1.0` y omitir cualquier clarificación manual del usuario.
3. **Invariante de Bloqueo de Benchmarks**: El motor de admisión clínico de PymIA tiene estrictamente prohibido ejecutar benchmarks de diagnóstico o reportar hallazgos si el `overall_confidence` del esquema inferido es menor a `0.75` o si existe un contrato de FIO activo sin responder.
4. **Invariante de Inmunidad Canónica**: Las columnas físicas cuyo nombre coincida de forma textual con términos oficiales de la ontología no pueden clasificarse como "ambiguas" o "unknown" bajo ninguna circunstancia.

---

## 6. Relación con ADRs de Gobernanza

El presente diseño transitorio de contexto clínico e inteligencia documental se alinea de forma directa con los ADRs aprobados en el repositorio:

* **Sincronía con [ADR-004](file:///opt/PymIA/docs/adr/ADR-004-bem-como-fallback-pasivo.md)**: El desvío cognitivo de BEM queda desactivado gracias a la inyección de `TenantClinicalContext`, ya que dota al motor local de la inteligencia interpretativa necesaria para resolver la estructura de la planilla de forma nativa.
* **Sincronía con [ADR-005](file:///opt/PymIA/docs/adr/ADR-005-document-intelligence-engine.md)**: El validador matemático implementado sobre Polars materializa la regla contable cruzada descrita en este diseño para resolver el tipo de costo (unitario vs total) de manera matemática.
* **Sincronía con [ADR-006](file:///opt/PymIA/docs/adr/ADR-006-tenant-clinical-context-as-input.md)**: Establece el `EvidenceBundle` enriquecido como el payload final de salida del motor local hacia el Kernel de PymIA, protegiendo las hipótesis diagnósticas de datos corruptos.
* **Sincronía con [ADR-007](file:///opt/PymIA/docs/adr/ADR-007-documentation-governance.md)**: Se inscribe este diseño transitorio bajo las normas de gobierno documental como un archivo `CANDIDATO` aprobado para guiar directamente la implementación del código de Opus 4.6.
