# PymIA Consorcios — Modelo conceptual de control operativo

**Fecha:** 12 de agosto de 2026  
**Estado:** Conceptual / descubrimiento de producto  
**Vertical:** Administradores de consorcios  

## 1. Tesis central

PymIA Consorcios no debe definirse como un ERP de administración de edificios ni como una suma de automatizaciones aisladas.

La hipótesis de producto más consistente es:

> **PymIA controla que la realidad financiera y operativa de cada consorcio cierre contra sus datos disponibles, identifica excepciones y permite que RADAR supervise los desvíos que el administrador considera relevantes.**

La unidad de análisis más útil no es sólo “el edificio”, sino el **estado operativo-financiero verificable de un consorcio durante un período**.

```text
CONSORCIO
  ↓
PERÍODO
  ↓
DATOS ESTRUCTURADOS
  ↓
NORMALIZACIÓN SEMÁNTICA
  ↓
CAPACIDAD DETERMINÍSTICA
  ↓
RESULTADO
  ↓
EXCEPCIONES
  ↓
WORKPAPER / EVIDENCIA
  ↓
RADAR
```

## 2. Evidencia institucional relevante

El Manual de Buenas Prácticas Consorciales del Gobierno de la Ciudad de Buenos Aires confirma que la operación mensual involucra, entre otros elementos:

- gastos del período;
- proveedores;
- remuneraciones y cargas sociales;
- seguros;
- depósitos no identificados;
- propietarios con saldo deudor;
- juicios;
- composición del estado financiero;
- banco, caja, valores y retenciones;
- fondos ordinarios y de reserva;
- ingresos por expensas;
- egresos por gastos;
- saldo al cierre;
- cobranzas pendientes de imputación;
- estado de cuenta y prorrateo.

Las categorías **“depósitos no identificados”** y **“cobranzas pendientes de imputación”** son particularmente relevantes porque muestran que las excepciones de identificación e imputación forman parte explícita del dominio consorcial, no son una construcción artificial de PymIA.

## 3. Qué debe modelar Servicio 1

Servicio 1 debe mantenerse acotado a capacidades concretas sobre datos operativos estructurados.

Ejemplos:

```text
extracto bancario + archivo de cobranzas
→ normalización
→ matching determinístico
→ conciliadas / pendientes / ambiguas
→ workpaper
```

Otros cruces admisibles dentro de una capacidad concreta:

```text
venta ↔ cobro
factura ↔ pago
deuda ↔ cobranza
saldo inicial ↔ saldo final anterior
```

Estos cruces son parte de la ejecución de una capacidad, no una red relacional general.

## 4. La excepción como objeto operativo

Servicio 1 debe poder producir excepciones explícitas y trazables, por ejemplo:

```text
EXCEPCIÓN
Tipo: COBRANZA_SIN_IMPUTAR
Consorcio: X
Período: 07/2026
Importe: $...
Evidencia: movimiento bancario ...
Esperado: asociación con unidad funcional
Encontrado: ninguna coincidencia suficiente
Estado: requiere revisión humana
```

Esto permite pasar de un informe difuso a una unidad de trabajo gobernable.

## 5. Separación con RADAR

Servicio 1 responde:

> **¿Qué pasó?**

Ejemplo:

```text
14 cobranzas sin imputar
$873.450
```

RADAR responde:

> **¿Ese estado cruzó una frontera definida por el dueño?**

Ejemplo:

```text
Política: cobranzas pendientes < 2% del total mensual
Real: 5,7%
Resultado: RADAR_EVENT
```

Regla conceptual:

> **Servicio 1 descubre y estructura el estado. RADAR supervisa el estado contra políticas del dueño.**

## 6. Invariantes operativos como futura herramienta conceptual

Sin convertirlos todavía en una nueva arquitectura, es útil pensar ciertas relaciones esperadas como invariantes de una capacidad:

```text
saldo inicial + ingresos - egresos = saldo final
cobros registrados ≈ movimientos bancarios atribuibles
gasto informado ↔ comprobante ↔ pago
saldo inicial período N = saldo final período N-1
```

Cuando una capacidad concreta detecta que una relación esperada no se cumple, produce una excepción.

## 7. Límite de alcance

Este documento NO autoriza:

- construir un ERP de consorcios;
- agregar CRM de reclamos;
- agregar gestión de mantenimiento;
- incorporar una red general de conocimiento;
- expandir Servicio 1 hacia razonamiento documental transversal;
- asumir que todos los controles listados deben implementarse ahora.

La prioridad sigue siendo cerrar capacidades vendibles y determinísticas de Servicio 1.

## 8. Formulación de producto

Una formulación de trabajo adecuada para la vertical es:

> **PymIA Consorcios controla datos operativos y financieros, cruza fuentes dentro de capacidades definidas, identifica excepciones, genera evidencia trazable y permite a RADAR supervisar los desvíos que el administrador decide vigilar.**
