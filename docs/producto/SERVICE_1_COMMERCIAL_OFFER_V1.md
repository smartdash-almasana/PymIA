# SERVICE_1_COMMERCIAL_OFFER_V1

## Estado

```text
STATUS: COMMERCIAL_OFFER_V1
SERVICE: Servicio 1 / Laboratorio Operacional Asistido
OFFER_TYPE: First Aid Excel para PyMEs
AUTONOMY: no
HUMAN_REVIEW_REQUIRED: yes
STAGE_6: deferred
PDF_OCR: deferred
CHATBOT_PRODUCTIVO: no
```

---

# 1. Nombre comercial recomendado

```text
Servicio 1 — Primeros Auxilios Excel para PyMEs
```

Subtítulo recomendado:

```text
Revisión operativa asistida de archivos Excel para detectar señales, faltantes y datos que necesitan decisión humana.
```

Nombre corto para conversación comercial:

```text
Laboratorio Operacional Excel
```

---

# 2. Descripción corta

Servicio 1 es un laboratorio operacional asistido para PyMEs que reciben, usan o acumulan archivos Excel sin una lectura clara.

El servicio toma archivos declarados por el cliente, revisa su estructura, detecta columnas y faltantes, ejecuta tools acotadas de primer auxilio y entrega archivos revisables con mensajes claros para dueño u operador.

Regla madre:

```text
La IA conversa.
La FSM gobierna.
Las tools ejecutan.
Los archivos son el producto.
```

---

# 3. Cliente ideal

Servicio 1 es adecuado para:

- comercios y PyMEs que trabajan con planillas de ventas, precios, costos, stock o caja;
- dueños que necesitan una primera lectura ordenada antes de decidir;
- estudios contables que reciben archivos desordenados de clientes;
- operadores que necesitan separar datos válidos, faltantes y señales iniciales;
- equipos que todavía no tienen ERP completo o que exportan datos a Excel/CSV.

No es ideal para:

- empresas que piden auditoría formal;
- automatización fiscal;
- conciliación bancaria definitiva;
- integración API bancaria/productiva;
- reemplazo de contador o analista.

---

# 4. Problema que resuelve

Muchas PyMEs tienen archivos, pero no tienen una rutina clara para responder:

- qué contiene cada hoja;
- qué columnas sirven;
- qué datos faltan;
- qué cálculos se pueden hacer con seguridad;
- qué señales operativas aparecen;
- qué no debe concluirse todavía.

Servicio 1 convierte ese caos en una entrega supervisada y revisable.

---

# 5. Qué promete

Servicio 1 promete:

- revisión inicial de archivos XLSX/CSV;
- detección de estructura, hojas y columnas;
- paquete de confirmación de columnas;
- ejecución de tools permitidas cuando hay datos suficientes;
- detección de faltantes o datos inválidos;
- outputs descargables;
- mensaje owner-facing con límites claros;
- revisión humana antes de vender conclusiones fuertes;
- trazabilidad de qué se usó y qué no se pudo usar.

El núcleo más fuerte hoy es:

```text
precios, costos y márgenes sobre Excel.
```

---

# 6. Qué NO promete

Servicio 1 no promete:

- auditoría;
- diagnóstico integral;
- exactitud garantizada;
- conciliación definitiva;
- contabilidad fiscal;
- liquidación de impuestos;
- reemplazo del contador;
- autonomía total;
- chatbot productivo;
- PDF/OCR productivo;
- APIs bancarias o de marketplaces;
- Stage 6 o auto-routing avanzado.

---

# 7. Inputs que debe enviar el cliente

El cliente puede enviar:

- archivos Excel `.xlsx`;
- archivos CSV;
- planillas de ventas;
- listas de productos, precios y costos;
- stock básico;
- caja o movimientos simples;
- gastos con concepto e importe;
- compras/proveedores cuando existan columnas compatibles.

El cliente también debe poder responder:

- qué significa cada columna relevante;
- qué período importa;
- qué datos son declarados y cuáles faltan;
- si una hoja representa ventas, stock, caja, gastos o proveedores.

---

# 8. Outputs que recibe el cliente

La entrega puede incluir:

- `owner_message.md` con resumen claro;
- `operator_packet.json` para revisión interna;
- `detected_structure.json` con hojas y columnas detectadas;
- `column_confirmation_packet.json`;
- outputs XLSX de tools ejecutadas;
- resumen de faltantes;
- limitaciones y claims prohibidos;
- QA/delivery gate cuando aplica.

Los archivos son parte central del servicio. No se vende una opinión suelta de IA.

---

# 9. Familias incluidas

## 9.1 Precios / costos / márgenes

Estado: fuerte / cerrado para operación asistida.

Sirve para:

- calcular margen básico según precio y costo declarados;
- detectar faltantes de costo o precio;
- preparar una lectura inicial de rentabilidad bruta.

Límite:

- no confirma rentabilidad real;
- no incluye impuestos, comisiones, costos fijos ni costos indirectos salvo que se provean y estén soportados.

## 9.2 Stock básico

Estado: operativo con caveats.

Sirve para:

- alertas simples;
- señales de stock bajo o desvíos básicos cuando los datos calzan.

Límite:

- no confirma stock físico;
- depende de calidad del archivo y mapping.

## 9.3 Caja triage

Estado: parcial / limitado.

Sirve para:

- lectura agregada o por fecha cuando el operador declara el modo;
- señales iniciales sobre diferencias o faltantes.

Límite:

- no confirma saldo bancario;
- no reemplaza arqueo ni conciliación.

## 9.4 Gastos triage

Estado: parcial.

Sirve para:

- ordenar gastos declarados;
- detectar campos faltantes;
- separar datos usables de datos incompletos.

Límite:

- no clasifica fiscalmente;
- no audita gastos.

## 9.5 Proveedores / precios

Estado: limitado / según evidencia.

Sirve para:

- observar variaciones visibles cuando hay proveedor, producto/insumo y precio/costo.

Límite:

- no decide estrategia de compras;
- no confirma rentabilidad ni negociación óptima.

---

# 10. Paquetes sugeridos

## Starter — Primeros Auxilios

Para una primera revisión acotada de uno o pocos archivos.

Incluye:

- intake;
- detección de estructura;
- confirmación de columnas;
- precios/costos/márgenes cuando aplica;
- entrega owner-facing simple.

## Operativo — Laboratorio Excel

Para ordenar archivos operativos recurrentes.

Incluye:

- revisión XLSX/CSV;
- normalización operativa inicial;
- múltiples hojas;
- outputs descargables;
- registro de faltantes;
- señales operativas básicas.

## Contador aliado — Revisión asistida

Para estudios o profesionales que necesitan recibir archivos de clientes y ordenar evidencia antes de trabajar.

Incluye:

- paquete operador;
- limitaciones explícitas;
- faltantes;
- datos inválidos;
- archivos listos para revisión humana.

No incluye dictamen contable ni fiscal.

---

# 11. Criterios de bloqueo o rechazo

Bloquear o rechazar cuando:

- el archivo no es soportado;
- faltan headers;
- hay columnas ambiguas sin confirmación;
- el cliente pide diagnóstico integral;
- el cliente pide auditoría o exactitud garantizada;
- el cliente pide PDF/OCR productivo;
- el cliente pide conciliación definitiva;
- el cliente pide integración bancaria/API;
- los datos no alcanzan para ejecutar la tool solicitada.

Respuesta correcta ante bloqueo:

```text
No se puede concluir todavía. Falta evidencia o confirmación humana.
```

---

# 12. Lenguaje comercial permitido

Usar:

- revisión inicial;
- primer auxilio operativo;
- laboratorio operacional;
- según datos declarados;
- archivos entregables;
- revisión humana;
- triage;
- señales operativas;
- faltantes detectados;
- datos inválidos detectados;
- entrega supervisada;
- lectura preliminar.

---

# 13. Lenguaje prohibido

No usar:

- auditoría;
- diagnóstico integral;
- exactitud garantizada;
- conciliación definitiva;
- fiscal;
- autónomo;
- la IA resuelve sola;
- reemplaza contador;
- optimización garantizada;
- verdad contable;
- rentabilidad real confirmada;
- saldo bancario confirmado.

---

# 14. Ejemplo de oferta en una página

## Servicio 1 — Primeros Auxilios Excel para PyMEs

Ordenamos tus archivos Excel y CSV para saber qué se puede leer, qué falta y qué señales operativas aparecen.

Trabajamos sobre datos declarados por la empresa. El servicio detecta estructura, pide confirmación de columnas, ejecuta cálculos permitidos y entrega archivos revisables.

### Ideal para

- revisar precios, costos y márgenes;
- ordenar ventas o listas de productos;
- detectar faltantes;
- preparar información para dueño, operador o contador aliado.

### Entregás

- Excel o CSV;
- explicación de columnas si hace falta;
- contexto mínimo del período y objetivo.

### Recibís

- resumen owner-facing;
- estructura detectada;
- columnas a confirmar;
- outputs XLSX cuando aplica;
- faltantes y límites;
- paquete de revisión humana.

### Importante

No es auditoría, no es diagnóstico integral y no reemplaza al contador. Es una revisión operativa inicial con archivos y límites claros.

---

# 15. Relación con documentos de gobierno

Esta oferta depende de:

- `docs/producto/SERVICE_1_FULL_OPERATOR_PLAYBOOK_V1.md`;
- `docs/producto/SERVICE_1_CAPABILITY_COMPLETION_MATRIX_V1.md`;
- `docs/producto/SERVICE_1_OWNER_FACING_DELIVERY_TEMPLATE_V1.md`.

La oferta comercial no habilita runtime nuevo. Sólo traduce capacidades ya gobernadas a lenguaje vendible con límites.

---

# 16. Estado final

```text
SERVICE_1_COMMERCIAL_OFFER_V1: READY_FOR_REVIEW
SELLABLE_CORE: YES
SERVICE_1_FULL: NOT_DECLARED
HUMAN_SUPERVISION_REQUIRED: YES
PDF_OCR: DEFERRED
STAGE_6: DEFERRED
CHATBOT_PRODUCTIVO: NO
```
