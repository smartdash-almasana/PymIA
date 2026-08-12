# PymIA / SmartPyme — Administradores de Consorcios Argentina

**Fecha:** 2026-08-12 13:47 ART  
**Estado:** DISCOVERY / HIPÓTESIS DE DOMINIO  
**Vertical:** Administradores de Consorcios — Argentina  
**Uso:** insumo para entrevista empírica, selección de evidencia y eventual piloto.  
**No es:** especificación de producto, backlog, requisito funcional ni descripción definitiva de cómo opera el sector.

---

## 1. Regla epistemológica

Este documento conserva hallazgos derivados de investigación de repositorios y análisis de dominio, pero **la fuente primaria de verdad posterior será el trabajo de campo con una administradora real argentina y sus archivos reales anonimizados**.

Por lo tanto:

- una feature encontrada en software no demuestra práctica habitual;
- un modelo de datos no demuestra modelo real del negocio;
- repetición entre forks no cuenta como evidencia independiente;
- prácticas de EE. UU., Brasil o España no se trasladan automáticamente a Argentina;
- inferencias se conservan como hipótesis;
- cualquier contradicción con operación real debe conservarse y promover la evidencia empírica por encima del modelo provisional.

Regla:

```text
EVIDENCIA REAL
> HIPÓTESIS DE REPOSITORIO
> INFERENCIA
> IDEA DE PRODUCTO
```

---

## 2. Mapa provisional del dominio

La estructura más consistente observada es:

```text
CONSORCIO
→ UNIDAD FUNCIONAL
→ PROPIETARIO / RESIDENTE
→ CUENTA CORRIENTE
→ GASTO
→ REGLA DE DISTRIBUCIÓN
→ EXPENSA / CUOTA
→ PAGO
→ SALDO / MORA
```

Esto debe tratarse como **modelo a validar**, no como verdad cerrada.

Tres circuitos deben investigarse por separado porque pueden vivir en herramientas diferentes.

### 2.1 Circuito de gastos

```text
Proveedor
→ factura / gasto
→ clasificación
→ imputación a consorcio
→ aprobación si aplica
→ pago
→ banco / caja
```

### 2.2 Circuito de liquidación

```text
Gastos del período
→ reglas de distribución
→ coeficientes / criterios
→ liquidación
→ cargos por UF
→ saldo exigible
```

### 2.3 Circuito de cobranza

```text
Expensa / deuda
→ pago
→ identificación de pagador / UF
→ imputación
→ saldo restante / crédito
→ mora / interés si aplica
```

---

## 3. Entidad pivote: Unidad Funcional

La Unidad Funcional aparece recurrentemente con variantes como:

```text
UF
Unidad
Departamento
Unit
Fraction
Unidade
```

No debe asumirse que representa sólo departamentos. Puede abarcar, según el consorcio y la fuente:

- departamentos;
- locales;
- cocheras;
- bauleras;
- otras unidades accesorias.

### Preguntas críticas para campo

- ¿Qué consideran una UF dentro de cada consorcio?
- ¿Cocheras y bauleras tienen cuenta corriente propia o están ligadas a otra unidad?
- ¿Puede una misma persona ser responsable de varias UF?
- ¿Cómo identifican una UF entre sistema, Excel, liquidación, banco y comunicaciones?

### Potencial relevancia para Servicio 1

La homologación semántica podría necesitar reconocer nombres diferentes para una misma entidad operacional sin asumir equivalencia automática.

Ejemplo:

```text
UF 4A
Depto 4A
Unidad 12
Local 3
Cochera 18
```

---

## 4. GOLD-0 — La regla de distribución del gasto

El hallazgo de mayor densidad es que **no alcanza con preguntar si existen coeficientes**.

Un mismo consorcio puede tener:

- coeficiente general;
- varios coeficientes;
- gastos particulares;
- sectores afectados;
- unidades exentas de determinados conceptos;
- extraordinarias con criterio distinto;
- reglas definidas por reglamento o decisión de asamblea.

### Pregunta de campo correcta

> Cuando aparece un gasto, ¿cómo deciden qué unidades lo pagan y cómo se reparte?

Luego:

> ¿Todos los gastos usan el mismo porcentaje o existen distintas formas de repartirlos?

### Hipótesis a NO asumir

```text
coeficiente = superficie
```

No hay base suficiente para asumirlo universalmente.

---

## 5. La liquidación no es un importe simple

Una liquidación puede componerse de una combinación de:

```text
saldo anterior
+ cargos del período
+ ordinarias
+ extraordinarias
+ gastos particulares
+ servicios
+ intereses
- pagos
± ajustes
= total exigible
```

También aparecen como posibilidades:

- múltiples vencimientos;
- saldo a favor;
- pagos parciales;
- deuda previa;
- cargos accesorios;
- reliquidaciones o ajustes posteriores.

### Consecuencia para discovery

No preguntar sólo “¿cómo liquidan expensas?”.

Reconstruir:

> ¿Cómo se forma exactamente el saldo que termina viendo cada UF?

---

## 6. GOLD — Pagos parciales, diferencias y saldos a favor

Las excepciones de cobranza parecen estructuralmente importantes.

Casos a validar:

```text
pago parcial
pago por importe mayor
pago duplicado
pago sin referencia
pago de titular distinto del propietario
saldo a favor
pago imputado al período equivocado
reclamo “yo ya pagué”
```

### Preguntas concretas

- Si una UF debe $300.000 y paga $200.000, ¿qué sucede?
- Si paga $320.000, ¿qué sucede con la diferencia?
- ¿Quién decide a qué período o deuda se aplica un pago?
- ¿Existe una regla automática o se corrige manualmente?
- ¿Cómo se registra un pago todavía no identificado?

### Hipótesis que requiere validación

No asumir FIFO, “primero intereses”, “primero capital” ni otra política particular de imputación.

---

## 7. GOLD — Transferencia huérfana

Hipótesis operacional relevante:

```text
entra dinero al banco
pero
no está claro a qué UF corresponde
```

Debe investigarse empíricamente su frecuencia e impacto.

### Preguntas

- ¿Les entra dinero al banco que no pueden identificar inmediatamente?
- ¿Cómo averiguan de quién es?
- ¿Dónde queda registrado mientras está sin identificar?
- ¿Qué ocurre si pasan días sin poder asociarlo?
- ¿Qué sucede si el titular bancario no coincide con el propietario?

### No promover todavía a requisito

No existe evidencia suficiente para afirmar que ésta sea universalmente “la principal” fricción de los administradores argentinos.

---

## 8. Conciliación bancaria — mantener como hipótesis

Hay evidencia de cuentas, movimientos, importaciones y mecanismos de matching en software, pero **no debe asumirse todavía un workflow argentino estándar de conciliación**.

Preguntas de campo:

- Cuando entra plata al banco, ¿cómo saben qué UF pagó?
- ¿Descargan algún archivo del banco?
- ¿En qué formato?
- ¿Contra qué lo comparan?
- ¿Quién revisa diferencias?
- ¿Con qué frecuencia?
- ¿Qué ocurre con montos que no coinciden?
- ¿Cuánto de ese trabajo es manual?

Regla:

```text
NO HAY EVIDENCIA SUFICIENTE
```

para declarar una forma canónica de conciliación bancaria en administraciones argentinas.

---

## 9. Cierre mensual — caja negra a abrir

Los repositorios muestran conceptos de cierre, generación de cuotas y restricciones posteriores, pero **no hay base suficiente para definir cómo funciona el cierre mensual real de una administración argentina**.

Pregunta principal:

> ¿Hay un momento en que ustedes dicen “este consorcio ya está cerrado este mes”?

Después:

- ¿Qué debe estar listo antes?
- ¿Qué tarea bloquea la liquidación si falta?
- ¿Qué se puede corregir después de emitir?
- ¿Quién autoriza correcciones?
- ¿Cuántas veces se repite este circuito por mes?
- ¿Hay días o franjas horarias particularmente críticas?

Posibles dependencias a validar:

```text
facturas
pagos a proveedores
cobranzas
banco
sueldos
intereses
coeficientes
extraordinarias
comprobantes
controles
```

---

## 10. Caja chica y fuentes paralelas

Aparece en software latinoamericano como fuente financiera separada de la cuenta bancaria.

Debe validarse:

- si existe caja chica por consorcio;
- si existe efectivo central de administración;
- cómo se registra;
- cómo se rinde;
- contra qué se controla;
- si esos movimientos terminan en Excel, sistema o ambos.

Pregunta:

> Además de las cuentas bancarias, ¿manejan efectivo o caja chica? ¿Cómo se registra y controla?

---

## 11. GOLD — estudiar el viaje del dato

No limitar discovery a “qué sistema usan”.

Para cada dato importante reconstruir:

```text
DATO
→ dónde nace
→ quién lo carga
→ herramienta / archivo
→ quién lo copia
→ qué transformación recibe
→ contra qué se controla
→ dónde termina
→ qué ocurre si no coincide
```

Este patrón debe aplicarse al menos a:

- UF;
- coeficientes;
- gastos;
- proveedores;
- liquidaciones;
- cobranzas;
- extractos bancarios;
- deuda;
- recibos;
- reportes.

---

## 12. GOLD — “el Excel que más costaría abandonar”

Pregunta de alto valor para entrevista:

> ¿Qué sistema o planilla de Excel es la que más te costaría abandonar hoy mismo?

Luego:

> ¿Qué hace esa planilla que el sistema no hace?

Esto puede revelar:

- verdadero sistema operativo informal;
- controles no cubiertos por software;
- fórmulas críticas;
- know-how embebido;
- dependencia de una persona;
- fuente de verdad efectiva;
- exportaciones que se transforman manualmente.

---

## 13. Excepciones que deben buscarse deliberadamente

El happy path puede esconder la complejidad real.

Investigar específicamente:

```text
pago parcial
saldo a favor
pago no identificado
pago duplicado
unidad accesoria
gasto particular
gasto que afecta sólo algunas UF
varios coeficientes
varios vencimientos
deuda anterior
cambio de propietario
error después de emitir
extraordinaria
reliquidación
fondo de reserva
factura faltante
gasto urgente sin documentación completa
```

Pregunta transversal:

> ¿Qué casos hacen que tengas que salirte del procedimiento normal?

---

## 14. Tres familias de controles potencialmente relevantes

No son requisitos de producto. Son familias de diagnóstico para validar con archivos reales.

### 14.1 Integridad estructural

```text
UF duplicada
referencia inexistente
importe inválido
fecha incoherente
período incorrecto
registro incompleto
```

### 14.2 Integridad financiera

```text
total ≠ componentes
saldo ≠ saldo anterior + cargos - pagos
pago sin deuda identificable
deuda sin origen claro
movimiento sin contraparte
importe duplicado sospechoso
```

### 14.3 Integridad temporal

```text
operación modificada después de cierre
recibo asociado a dato alterado
corrección destructiva de período emitido
movimiento cargado fuera del período esperado
```

Estas familias encajan conceptualmente con análisis determinístico basado en evidencia, pero deben validarse antes de convertirse en capacidades de Servicio 1.

---

## 15. Paquete de evidencia ideal para piloto

No pedir archivos aislados si puede obtenerse un conjunto coherente.

Prioridad:

```text
UN CONSORCIO
+
UN MISMO PERÍODO
```

Solicitar idealmente:

1. padrón / maestro de UF;
2. matriz de coeficientes o reglas de distribución;
3. detalle de gastos del período;
4. liquidación emitida;
5. archivo fuente de la liquidación, si existe;
6. cobranzas por UF;
7. extracto bancario del mismo período;
8. estado de deuda / morosidad;
9. facturas principales de proveedores;
10. rendición, cierre o reporte final, si existe.

Objetivo:

```text
INPUT
→ TRANSFORMACIÓN
→ OUTPUT
→ COBRANZA
→ BANCO
→ SALDO
```

---

## 16. Pareja documental de máximo valor

Si sólo pudieran obtenerse dos elementos del proceso de liquidación:

```text
A. Liquidación final recibida por el propietario
+
B. Excel / archivo / exportación desde el cual fue construida
```

Esta pareja permite observar:

- nomenclatura real;
- transformaciones;
- campos descartados;
- agregaciones;
- cálculos;
- inconsistencias entre fuente y salida;
- complejidad del negocio vs. complejidad del formato.

---

## 17. Diseño recomendado del piloto

No elegir simplemente “el consorcio más grande”.

### Piloto A — representativo

Un consorcio que la administradora considere normal y cuya documentación esté disponible.

Objetivo:

```text
happy path real
```

### Piloto B — complicado

Un consorcio con varias excepciones, por ejemplo:

- mora;
- pagos parciales;
- extraordinarias;
- múltiples criterios de distribución;
- unidades accesorias;
- muchos proveedores;
- obra importante;
- pagos difíciles de identificar.

Objetivo:

```text
exception path real
```

---

## 18. Encaje provisional con PymIA Servicio 1

Sin convertir nada en backlog, aparecen seis zonas compatibles con el tipo de problema que Servicio 1 busca resolver.

### 18.1 Normalización

```text
Excel
CSV
exportaciones
PDF transformado a estructura
```

### 18.2 Homologación semántica

```text
UF / unidad / depto
importe / monto / total
saldo / deuda
proveedor / acreedor
```

### 18.3 Relación entre fuentes

```text
UF ↔ liquidación
UF ↔ pago
pago ↔ banco
liquidación ↔ deuda
proveedor ↔ gasto
```

### 18.4 Controles determinísticos

```text
integridad
cuadratura
duplicados
referencias
fechas
totales
```

### 18.5 Excepciones

```text
sin match
ambiguo
pago parcial
saldo a favor
diferencia
```

### 18.6 Diagnóstico

```text
entidad
problema
evidencia
importe / magnitud
explicación
próximo control
```

Tesis provisional:

> La oportunidad no parece estar en enseñar a PymIA a “administrar consorcios”, sino en permitirle reconstruir y controlar circuitos operativos de un consorcio a partir de los archivos imperfectos que la administración ya produce.

---

## 19. Modelo de discovery recomendado para entrevista

Organizar el corazón de la entrevista en seis mapas:

| Mapa | Qué reconstruir |
|---|---|
| Estructura | consorcios, UF, propietarios, cuentas |
| Información | dónde nace y dónde vive cada dato |
| Gasto | factura → clasificación → pago |
| Liquidación | gastos → distribución → expensa |
| Cobranza | deuda → pago → imputación → saldo |
| Control | qué verifican, cuándo y qué pasa si falla |

Sólo después cuantificar:

```text
tiempo
errores
duplicación
fricción
dependencia manual
automatización deseada
```

---

## 20. Hipótesis prioritarias a validar y NO asumir

1. La conciliación bancaria consume tiempo material.
2. Las transferencias no identificadas son frecuentes.
3. Existe una regla estable para imputar pagos parciales.
4. El cierre mensual funciona como gate operativo.
5. Excel contiene controles que el software especializado no cubre.
6. Existen múltiples coeficientes o reglas de reparto por consorcio.
7. Las excepciones consumen más tiempo que el cálculo matemático base.
8. El volumen de trabajo escala de forma casi lineal con el número de consorcios.
9. La deuda/morosidad requiere reconstrucción manual frecuente.
10. Un paquete de archivos del mismo período permite controles cruzados de alto valor.

---

## 21. Preguntas de máximo rendimiento para la administradora real

1. ¿Qué planilla o sistema te costaría más abandonar hoy?
2. ¿Qué hace esa planilla que el sistema principal no hace?
3. Cuando aparece un gasto, ¿cómo deciden quiénes lo pagan y cómo se reparte?
4. ¿Todos los gastos se reparten igual?
5. ¿Cómo se forma el saldo final que ve cada UF?
6. ¿Qué pasa si una UF paga menos de lo que debe?
7. ¿Qué pasa si paga de más?
8. Cuando entra plata al banco, ¿cómo saben a qué UF corresponde?
9. ¿Qué hacen con un movimiento que no pueden identificar?
10. ¿Qué archivo descargan del banco, si descargan alguno?
11. ¿Contra qué lo comparan?
12. ¿Qué tiene que estar terminado para poder liquidar el mes?
13. ¿Qué cosa puede bloquear una liquidación?
14. ¿Qué error sería grave que se les escape antes de enviar expensas?
15. ¿Qué casos obligan a salir del procedimiento normal?
16. ¿Qué información se copia de un sistema a otro?
17. ¿Qué exportan a Excel para trabajar y luego vuelven a cargar?
18. ¿Qué tarea se repite para cada consorcio?
19. ¿Cuál de esas tareas consume más tiempo?
20. ¿Qué dos consorcios elegirías: uno normal y uno particularmente complicado?

---

## 22. Siguiente investigación focal

### Objetivo

Terminar de dilucidar dolores y cuellos de botella de **administradores de consorcios argentinos**, sin volver a hacer una cartografía genérica del software.

### Prompt canónico

```text
Quiero realizar una investigación profunda, focalizada exclusivamente en ADMINISTRADORES DE CONSORCIOS EN ARGENTINA.

OBJETIVO

No quiero otra cartografía general del dominio ni otro inventario de funcionalidades de software.

Quiero dilucidar, con la mayor evidencia posible:

1. cuáles son los dolores operativos reales;
2. cuáles son los cuellos de botella recurrentes;
3. qué tareas consumen más tiempo;
4. qué tareas generan más errores;
5. qué controles obligan a revisión manual;
6. qué información se copia o reconstruye entre sistemas;
7. qué procesos se vuelven críticos en cierre/liquidación;
8. qué problemas aparecen en cobranza, morosidad e imputación de pagos;
9. qué fricciones existen entre banco, sistema de administración, Excel y documentación;
10. qué excepciones rompen el flujo normal;
11. qué problemas escalan cuando una administración maneja muchos consorcios;
12. qué dolores tienen impacto económico, reputacional o legal suficiente como para justificar pago por una solución.

CONTEXTO

Estamos preparando empíricamente la vertical ADMINISTRADORES DE CONSORCIOS para PymIA / SmartPyme.

Ya tenemos una hipótesis provisional del circuito:

CONSORCIO
→ UNIDAD FUNCIONAL
→ REGLAS DE DISTRIBUCIÓN
→ GASTOS
→ LIQUIDACIÓN
→ CUENTA CORRIENTE
→ COBRANZAS
→ BANCO
→ SALDO / MORA

Este modelo es HIPÓTESIS, no verdad.
La investigación debe intentar confirmarlo, corregirlo o romperlo.

ALCANCE GEOGRÁFICO

ARGENTINA como prioridad absoluta.
Dar especial peso a CABA, Provincia de Buenos Aires y administraciones que gestionan múltiples consorcios.
No extrapolar automáticamente prácticas de España, Brasil, EE. UU. u otros países.

FUENTES

No limitarse a GitHub.
Buscar evidencia en repositorios argentinos, documentación de software argentino, manuales, centros de ayuda, tutoriales, videos demostrativos, foros, comunidades de administradores, preguntas frecuentes, reclamos/reseñas, publicaciones profesionales, cámaras/asociaciones/colegios, material de capacitación, normativa sólo cuando explique una carga operativa concreta, avisos laborales y discusiones sobre Excel, sistemas, bancos, cobranzas y liquidaciones.

Los materiales comerciales de proveedores sirven como evidencia de qué problemas intentan resolver, pero NO prueban por sí mismos que esos problemas sean frecuentes.

SEPARACIÓN OBLIGATORIA DE EVIDENCIA

E1 — evidencia directa de administrador/empleado del sector
E2 — documentación funcional de software usado en Argentina
E3 — evidencia repetida en múltiples fuentes independientes
E4 — inferencia razonable
E5 — afirmación comercial de proveedor

Priorizar E1 + E2 + E3.
No presentar E4/E5 como hecho.

INVESTIGAR EN PROFUNDIDAD

A. Liquidación de expensas
B. Cobranzas e imputación
C. Banco y conciliación, sin asumir que existe conciliación formal
D. Gastos, proveedores y pagos
E. Cierre del mes
F. Excel y sistemas paralelos
G. Operación multi-consorcio
H. Consultas y reclamos
I. Controles críticos
J. Tiempo y costo operativo
K. Dolores por impacto

Para cada dolor registrar:

FRECUENCIA: diario / semanal / mensual / eventual
IMPACTO: bajo / medio / alto / crítico
TIPO: tiempo / dinero / error / retrabajo / riesgo legal / reclamo / reputación / dependencia de persona / falta de trazabilidad
AUTOMATIZABILIDAD APARENTE: baja / media / alta
EVIDENCIA DISPONIBLE: archivo / sistema / banco / documento / no evidente

Construir matriz:

DOLOR | PROCESO | FRECUENCIA | IMPACTO | TAREA MANUAL | EVIDENCIA | FUENTE | CONFIANZA | POSIBLE CONTROL/ANÁLISIS | REQUIERE VALIDACIÓN HUMANA

Producir TOP 15 de dolores argentinos utilizando comparativamente:
frecuencia × impacto × repetición entre consorcios × trabajo manual × disponibilidad de evidencia analizable.
No inventar puntajes.

BUSCAR CONTRADICCIONES

Conservar diferencias entre administraciones: conciliación automática vs manual, uso intensivo de Excel vs ausencia de Excel, políticas distintas de imputación, modelos de liquidación diferentes, diferentes grados de centralización.
Las contradicciones son hallazgos.

RESULTADO FINAL

1. TOP 15 dolores/cuellos de botella mejor sustentados.
2. Workflow argentino real más probable.
3. Momentos de máxima carga mensual.
4. Top tareas manuales repetitivas.
5. Top errores y excepciones.
6. Top controles críticos.
7. Mapa origen → archivo/sistema → transformación → destino.
8. Qué sigue viviendo en Excel y por qué.
9. Qué dolores escalan con cantidad de consorcios.
10. Qué dolores tienen evidencia directamente analizable por PymIA Servicio 1.
11. Qué dolores parecen valiosos pero están fuera de Servicio 1.
12. Top 20 preguntas de validación para entrevista real.
13. Top 10 archivos/evidencias a solicitar.
14. Top 10 hipótesis todavía no probadas.
15. Contradicciones encontradas.
16. Vacíos donde debe escribirse: NO HAY EVIDENCIA SUFICIENTE.

REGLA FINAL

No diseñar producto todavía.
Reducir incertidumbre de dominio.
Distinguir:

DOLOR REAL
vs
FEATURE INTERESANTE

CUELLO DE BOTELLA ECONÓMICAMENTE RELEVANTE
vs
MOLESTIA MENOR.
```

---

## 23. Criterio de promoción futura

Nada de este documento se promueve a requisito hasta contar con una combinación suficiente de:

```text
entrevista real
+
evidencia documental real
+
recurrencia entre casos
+
problema económicamente relevante
+
compatibilidad con el alcance de Servicio 1
```

Hasta entonces, este documento pertenece a **Discovery de Dominio**.
