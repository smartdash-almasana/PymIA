# SMARTPYME_INTERROGATION_TAXONOMY

Estado: CANÓNICO  
Fecha: 2026-05-26  
HEAD base: 788f6d8

---

## 1. Estado y propósito

Este documento consolida el sistema taxonómico de interrogatorio previo al reporte para SmartPyme Laboratorio.

Resuelve la tensión entre:

- capturar lenguaje crudo del usuario sin inducir;
- encuadrar el tipo de organismo PyME antes de diagnosticar;
- mapear síntomas sin cerrar diagnóstico;
- pedir evidencia solo cuando corresponde;
- sugerir clasificación ejecutable solo al final.

El interrogatorio no es un formulario. Es una secuencia clínica-operacional que transforma caos narrativo en estructura contrastable.

---

## 2. Principios rectores

### No diagnóstico inicial

El sistema no diagnostica en primer contacto. Primero encuadra, luego escucha, después pide evidencia, recién al final sugiere clasificación.

### No cuestionario inductivo cerrado

El sistema no ofrece menús prematuros del tipo:

```text
¿Tu problema es de costos, ventas, stock o caja?
```

Eso induce respuesta y cierra prematuramente el problema.

### Conservar lenguaje crudo

Las frases textuales del dueño se preservan sin reescribir. Son material clínico-operacional, no ruido.

Ejemplos válidos:

```text
"RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY"
"Paulita tiene un Excel con el stock"
"RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY por producto"
```

### Encuadrar organismo con mínima fricción

Antes de interpretar síntomas, el sistema debe ubicar el tipo de organización:

- rubro
- naturaleza económica
- dominio operacional
- tipo de organismo (comercio, industria, servicios, logística, salud, construcción, agro, financiero, educación, otro)

Sin taxonomía de organismo, las métricas cambian de significado y las patologías pierden contexto.

### Evidencia antes de diagnóstico

El sistema no afirma datos operacionales sin evidencia real o cálculo del núcleo determinístico. Diferencia explícitamente entre:

- señal
- hipótesis
- estimación orientativa
- diagnóstico confirmado

---

## 3. Secuencia previa al reporte

```text
RawInboundEvent
→ encuadre mínimo de organismo
→ anamnesis narrativa
→ señales lingüísticas
→ síntomas candidatos
→ dominios candidatos
→ preguntas de desambiguación
→ evidencia requerida
→ clasificación ejecutable sugerida
→ laboratorio
→ reporte
```

Cada paso es una capa conceptual. No se saltean. No se fusionan prematuramente.

---

## 4. Capas separadas

### Capa 0: Entrada cruda

Recibe cualquier entrada desde cualquier canal. Registra sin interpretar. Produce `RawInboundEvent`.

Campos mínimos:

- `event_id`
- `channel`
- `received_at`
- `raw_text` o `raw_file_ref`
- `conversation_id` (si existe)
- `cliente_id` (si está disponible)

No interpreta. No clasifica. No diagnostica.

### Capa 1: Organismo / empresa

Establece el tipo de organización antes de cualquier interpretación operacional.

Pregunta canónica:

```text
Antes de analizar la evidencia, necesito ubicar el tipo de organización:
¿esto corresponde a comercio, industria, servicios, logística, salud, construcción u otro rubro?
```

### Capa 2: Dolor declarado

Captura el síntoma expresado por el dueño en su propio lenguaje.

Metadata mínima por dolor:

- claim literal
- intensidad percibida
- temporalidad
- causalidad percibida
- impacto operacional
- área afectada

### Capa 3: Señal lingüística

Detecta indicadores semánticos en la narrativa cruda.

Taxonomía de señales lingüísticas:

- `lenguaje_no_tecnico`
- `intuicion_sin_evidencia`
- `urgencia_emocional`
- `incertidumbre_financiera`
- `dependencia_del_dueno`
- `delegacion_fragil`
- `caos_normalizado`

### Capa 4: Síntoma operacional

Transforma el dolor declarado en objeto operacional contrastable.

Ejemplo:

```text
Entrada: "Vendemos mucho pero no queda plata."
Síntoma operacional: incertidumbre de rentabilidad
```

### Capa 5: Dominio candidato

Identifica áreas operacionales potencialmente afectadas.

Dominios mínimos:

- margen
- stock
- caja
- costos
- ventas
- proveedores
- producción
- tiempo operativo

### Capa 6: Hipótesis

Genera hipótesis iniciales sin cerrarlas.

Ejemplo:

```text
Síntoma: incertidumbre de rentabilidad
Hipótesis v0: margen erosionado, fuga operativa o tensión de caja
```

### Capa 7: Evidencia requerida

Define qué documentación se necesita para contrastar cada hipótesis.

No se pide evidencia genérica. Se pide evidencia consecuencia del contrato de laboratorio.

Ejemplo:

```text
Si el dolor es margen:
→ lista de precios
→ costos unitarios
→ ventas recientes
```

### Capa 8: Clasificación ejecutable sugerida

Solo después de tener evidencia suficiente, el sistema sugiere una clasificación ejecutable.

Clasificaciones vigentes en runtime real:

- `excel_diagnostic` (diagnóstico financiero tabular)
- `supplier_duplicate_check` (detección de proveedores duplicados)

No se sugiere clasificación sin evidencia mínima.

### Capa 9: Laboratorio

Ejecuta el análisis sobre la evidencia aportada. Produce hallazgos trazables.

### Capa 10: Reporte

Genera outputs legibles:

- `diagnostic_report.md`
- `diagnostic_report.html` (si se solicita)
- `diagnostic_result.json`
- `reception_record.json`
- `receptions.jsonl`

---

## 5. Estados del interrogatorio

### `RAW_CAPTURED`

Entrada cruda registrada. Todavía no se interpretó.

### `NEEDS_ORGANISM_CONTEXT`

Falta encuadrar el tipo de organización antes de continuar.

### `NEEDS_DISAMBIGUATION`

El síntoma es ambiguo. Se requieren preguntas de clarificación semiestructurada.

### `NEEDS_EVIDENCE`

Hipótesis abierta, pero falta documentación concreta para contrastar.

### `EVIDENCE_RECEIVED`

Documentación aportada. Pendiente curación y análisis.

### `READY_TO_ROUTE`

Evidencia suficiente para sugerir clasificación ejecutable.

### `READY_TO_ANALYZE`

Clasificación confirmada. Listo para ejecutar laboratorio.

### `BLOCKED`

Falta evidencia mínima crítica. El sistema bloquea con claridad:

```text
Con lo que me diste todavía no puedo armar un caso.
Necesito ventas, costos y período.
Cuando tengas esa información, seguimos.
```

### `UNSUPPORTED`

El caso no corresponde a capacidades vigentes del sistema.

---

## 6. Taxonomía mínima

### Señales crudas

Indicadores detectables en narrativa o datos:

- ventas cero
- stock crítico
- stock inmovilizado
- margen negativo
- precio desactualizado
- caja insuficiente
- compras creciendo más que ventas
- devoluciones altas

### Síntomas operacionales

Objetos clínicos estructurados:

- incertidumbre de rentabilidad
- tensión de caja
- fuga de margen
- sobrestock
- cuello de botella productivo
- desorden financiero
- precios atrasados
- improductividad operativa
- dependencia manual excesiva

### Dominios funcionales

Áreas operacionales PyME:

- ventas
- compras
- stock
- caja
- producción
- precios
- margen
- proveedores
- sueldos
- impuestos
- tiempo operativo

### Evidencias candidatas

Tipos documentales esperables:

- lista de precios
- hoja de stock
- ventas (Excel, PDF, CSV)
- compras / facturas
- cierre de caja
- extracto bancario
- reporte de marketplace
- planilla de producción
- maestro de proveedores

---

## 7. Microcuestionario estructural no inductivo

El sistema puede usar botones/selectores para capturar contexto estructural rápido del organismo PyME.

**Principio:** los selectores sirven para ubicar el organismo. El texto/audio sirve para entender el síntoma.

### Reglas del microcuestionario

- Los selectores **no diagnostican**.
- **No deben forzar** el dolor del usuario a categorías cerradas.
- Sirven para mejorar la taxonomía del organismo.
- Deben ser **breves** (3 a 5 selectores máximo).
- Deben ser **opcionales o progresivos**.
- Deben convivir con relato libre por texto/audio.
- Si el usuario llega con audio/texto espontáneo, no interrumpirlo con formulario; capturar primero y luego pedir contexto faltante.

### Selectores permitidos

#### Canal de venta
- Local
- Mayorista
- Mercado Libre
- Ecommerce
- Instagram/WhatsApp
- Mixto

#### Tipo de operación
- Revendo productos
- Produzco/fabrico
- Presto servicios
- Distribuyo
- Mixto
- No estoy seguro

#### Stock
- Manejo stock
- No manejo stock
- Lo manejo informalmente
- No sé si está actualizado

#### Herramientas actuales
- Excel
- Sistema de gestión
- Cuaderno/papel
- Contador/estudio
- Mercado Libre/tienda online
- Varios

#### Evidencia disponible
- Excel
- PDF/facturas
- Capturas
- Export de sistema
- Audio/texto
- Todavía no sé

### Selectores prohibidos o peligrosos

Estos selectores inducen diagnóstico prematuro y no deben usarse:

```text
¿Tu problema es margen, caja, proveedores o stock?
¿Querés auditoría financiera, comercial o de inventario?
¿Qué diagnóstico querés correr?
```

### Captura del dolor

El dolor siempre debe capturarse con pregunta abierta, no con selector:

```text
Contame con tus palabras qué querés entender o qué te preocupa.
Podés escribirlo o mandarlo por audio.
```

---

## 8. Preguntas no inductivas

Ejemplos concretos de preguntas correctas:

```text
¿Qué pasó?
¿Cómo te diste cuenta?
¿Desde cuándo?
¿Qué impacto te está generando hoy en plata o en tiempo?
¿Qué proceso puntual está más afectado?
¿Tenés ventas del último trimestre aunque sea en Excel?
¿Esto corresponde a comercio, industria, servicios u otro rubro?
```

Estas preguntas:

- no inducen respuesta;
- no ofrecen menú cerrado;
- permiten narrativa abierta;
- buscan evidencia concreta.

---

## 9. Preguntas prohibidas o débiles

Ejemplos de menús prematuros que no deben usarse:

```text
¿Tu problema es de costos, ventas, stock o caja?
¿Querés analizar margen, rotación o punto de equilibrio?
¿Necesitás un dashboard, un reporte o una auditoría?
```

Estas preguntas:

- inducen respuesta;
- cierran prematuramente el problema;
- asumen conocimiento técnico del usuario;
- convierten interrogatorio en formulario consultorial.

---

## 10. Relación con runtime real

### Clasificaciones vigentes

El runtime SmartPyme MVP local soporta actualmente:

- `excel_diagnostic`: diagnóstico financiero tabular genérico
- `supplier_duplicate_check`: detección de proveedores duplicados y normalización de maestro

### Sin routing automático asumido

Este documento no asume que existe routing automático por columnas. La clasificación puede ser explícita vía CLI (`--classification`).

### Sin HTML asumido

Este documento no asume que existe `--html-out`. El reporte HTML es capacidad opcional, no obligatoria.

### Mapeo evidencia → clasificación

Ejemplo de mapeo sano:

```text
Columnas: proveedor, cuit, razon_social
→ supplier_duplicate_check

Columnas: monto, fecha_factura, concepto
→ excel_diagnostic
```

Si el usuario pasa clasificación explícita distinta, el sistema respeta pero puede advertir inconsistencia.

---

## 11. Criterios de cierre del interrogatorio

El interrogatorio queda cerrado cuando:

1. El tipo de organismo está encuadrado.
2. Los síntomas declarados están estructurados.
3. Las hipótesis iniciales están formuladas.
4. La evidencia requerida está identificada.
5. La evidencia aportada es suficiente (o el sistema bloquea con claridad).
6. La clasificación ejecutable está sugerida y confirmada.

Cierre no significa diagnóstico. Significa que el sistema sabe qué analizar y con qué evidencia.

---

## 12. Gaps posteriores

Este documento no define todavía:

- schema Pydantic definitivo de `InterrogationRecord`;
- persistencia de estado de interrogatorio por tenant;
- integración con LearningMemory o memoria conversacional;
- fuzzy matching para señales lingüísticas;
- scoring de confianza por hipótesis;
- UI de interrogatorio para Telegram/web;
- política de reintento ante evidencia insuficiente;
- catálogo completo de patologías y su mapeo a evidencias.

Estos gaps se resuelven en frentes específicos posteriores.

---

## 13. Roadmap siguiente

### SMARTPYME_INTERROGATION_TAXONOMY_SLICE

Implementar slice mínimo que:

- capture `RawInboundEvent`;
- registre estado de interrogatorio;
- sugiera clasificación tras evidencia;
- sin routing automático complejo;
- sin fuzzy;
- sin LearningMemory.

### SMARTPYME_INTAKE_RECORD_AND_EVIDENCE_REQUEST

Implementar:

- `IntakeRecord` persistido por tenant;
- pedido de evidencia estructurado;
- bloqueo sano si falta evidencia crítica;
- trazabilidad de qué se pidió y qué se recibió.

### SMARTPYME_DEMO_WITH_INTAKE_BEFORE_REPORT

Demo integrada que muestre:

- entrada cruda;
- interrogatorio mínimo;
- pedido de evidencia;
- laboratorio;
- reporte final.

Sin cambios de arquitectura. Sin Hermes real. Sin producción.

---

## Documentos base consultados

- `docs/ingenieria_conversacional.PROTOCOLO_PRIMER_CONTACTO_v1.md`
- `docs/arquitectura/CONTRATO_PRIMER_ENCUENTRO_TAXONOMICO.md`
- `docs/producto/protocolo-anamnesis-mvp.md`
- `docs/producto/capa-00-canal-entrada.md`
- `docs/producto/capa-01-admision-epistemologica.md`
- `docs/catalogo/anamnesis-y-catalogos.md`
- `docs/catalogo/primary_context_taxonomy.v1.json`
- `docs/smartpyme/SMARTPYME_LOCAL_MVP_RUNTIME.md`
- `docs/smartpyme/SMARTPYME_SUPPLIER_DUPLICATE_CHECK_SPEC.md`

---

## Restricciones preservadas

Este documento:

- no autoriza runtime nuevo;
- no autoriza MCP;
- no autoriza jobs ni workflows;
- no autoriza orquestación;
- no modifica código;
- no toca Hermes real;
- no toca producción;
- no toca secretos ni `.env`.

Solo establece taxonomía canónica para futuros frentes de implementación controlada.
