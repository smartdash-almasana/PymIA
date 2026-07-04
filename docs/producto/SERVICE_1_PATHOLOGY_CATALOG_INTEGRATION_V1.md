# SERVICE_1_PATHOLOGY_CATALOG_INTEGRATION_V1

## Estado

```text
Tipo: PRODUCT_ARCHITECTURE_INTEGRATION
Servicio: SERVICE_1 / SmartPyme
Estado: DRAFT_CANONICAL_CANDIDATE
Runtime impact: NONE
Code impact: NONE
Tests impact: NONE
```

Este documento define cómo debe conectarse el catálogo de patologías PyME con Servicio 1.

No implementa runtime.
No crea nuevas tools.
No reemplaza el catálogo.
No modifica el flujo existente.

---

## 1. Regla central

Servicio 1 no debe organizarse solamente por fórmulas, tools o archivos.

Debe organizarse por patologías operacionales detectables en PyMEs.

```text
El dueño expresa un dolor.
PymIA identifica señales.
El catálogo propone patologías candidatas.
PymIA pide evidencia mínima.
Las tools computan.
PymIA devuelve diagnóstico, hallazgos y tratamiento.
```

---

## 2. Artefacto base

Catálogo base:

```text
docs/doctrina/organizacional/PYMIA_ORGANIZATIONAL_PATHOLOGY_CATALOG_V0.json
```

Estado esperado:

```text
DRAFT_CANONICAL_CANDIDATE
```

Ese catálogo define:

```text
- dominios;
- patologías;
- síntomas;
- señales de anamnesis;
- datos mínimos;
- fórmulas asociadas;
- impacto.
```

---

## 3. Posición dentro de Servicio 1

El catálogo queda ubicado entre la conversación y las tools.

```text
Dueño
  ↓
Conversación / anamnesis
  ↓
Catálogo de patologías
  ↓
Evidencia mínima requerida
  ↓
Skills / fórmulas / tools
  ↓
Hallazgos técnicos
  ↓
Diagnóstico PyME
  ↓
Tratamiento recomendado
  ↓
Entregables
```

---

## 4. Responsabilidad de cada capa

### 4.1 Conversación

La conversación captura lenguaje real del dueño.

Ejemplos:

```text
"vendo pero no veo la plata"
"no sé si gano"
"tengo todo desparramado"
"le mando planillas al contador y después no coincide"
```

La conversación no diagnostica sola.

Produce señales de anamnesis y pide aclaraciones.

### 4.2 Catálogo de patologías

El catálogo traduce señales del dueño en patologías candidatas.

Ejemplo:

```text
"vendo pero no veo la plata"
→ LIQ_001 descalce_ventas_cobranzas
```

### 4.3 Evidencia mínima

Cada patología define qué datos necesita.

Si faltan datos, PymIA debe preguntar o pedir archivos.

No debe inventar diagnóstico.

### 4.4 Skills / tools

Las fórmulas y tools computan evidencia.

No gobiernan el producto.

Son instrumentos diagnósticos.

### 4.5 Diagnóstico

El diagnóstico expresa el resultado en lenguaje PyME.

No debe limitarse a valores técnicos.

Debe decir:

```text
- qué patrón aparece;
- qué evidencia lo sostiene;
- qué riesgo implica;
- qué debería corregirse primero.
```

---

## 5. Ejemplos de integración

### 5.1 LIQ_001 — descalce_ventas_cobranzas

Entrada posible del dueño:

```text
"Vendo pero no veo la plata."
```

Patología candidata:

```text
LIQ_001 descalce_ventas_cobranzas
```

Evidencia mínima:

```text
- total_ventas_periodo;
- total_cobrado_periodo;
- cuentas_por_cobrar;
- fecha_vencimiento_cobros.
```

Tools / fórmulas asociadas:

```text
- diferencia vendido-cobrado;
- antigüedad de deuda;
- flujo de fondos proyectado.
```

Salida esperada:

```text
Hay ventas registradas que todavía no se transformaron en caja.
El problema principal no es facturación sino descalce entre venta y cobranza.
```

---

### 5.2 REN_001 — margen_invisible

Entrada posible del dueño:

```text
"Vendo mucho pero no sé si gano."
```

Patología candidata:

```text
REN_001 margen_invisible
```

Evidencia mínima:

```text
- precio_venta;
- costo_unitario;
- comisiones;
- impuestos;
- logística;
- descuentos.
```

Tools / fórmulas asociadas:

```text
- margen bruto por producto;
- margen neto;
- precio de venta con margen objetivo.
```

Salida esperada:

```text
La empresa factura, pero no puede distinguir qué productos, clientes o canales dejan ganancia real.
```

---

### 5.3 FIS_001 — data_decay_excel_contable

Entrada posible del dueño o contador:

```text
"Le mando planillas al contador y después no coincide."
```

Patología candidata:

```text
FIS_001 data_decay_excel_contable
```

Evidencia mínima:

```text
- archivos_excel;
- versiones;
- origen_dato;
- fecha_modificacion;
- responsable.
```

Tools / fórmulas asociadas:

```text
- validaciones de consistencia;
- BUSCARV/BUSCARX;
- SUMAR.SI.CONJUNTO;
- conciliación.
```

Salida esperada:

```text
La evidencia contable está degradada por versiones, manipulación manual o falta de trazabilidad.
```

---

## 6. Regla de producto

Servicio 1 vende diagnóstico operativo sobre evidencia real.

No vende fórmulas sueltas.
No vende archivos aislados.
No vende un operador.
No vende el catálogo como documento.

Vende:

```text
claridad operacional basada en patologías detectables.
```

---

## 7. Regla de arquitectura

```text
La IA conversa.
PymIA computa.
El catálogo orienta el diagnóstico.
Las tools ejecutan cálculos.
Los entregables muestran claridad y próximos pasos.
```

---

## 8. Implicancias para futuras implementaciones

Todo nuevo microservicio de Servicio 1 debe declarar:

```text
- qué patologías ayuda a detectar;
- qué datos mínimos requiere;
- qué señales de anamnesis lo activan;
- qué fórmulas/tools ejecuta;
- qué entregable produce;
- qué tratamiento recomienda.
```

Si un microservicio no puede vincularse con una patología, debe tratarse como infraestructura interna o herramienta auxiliar, no como producto principal.

---

## 9. Estado final de este documento

```text
SERVICE_1_PATHOLOGY_CATALOG_INTEGRATION_V1: CREATED_AS_DRAFT_CANONICAL_CANDIDATE
RUNTIME_TOUCHED: NO
CODE_TOUCHED: NO
TESTS_REQUIRED: NO
```
