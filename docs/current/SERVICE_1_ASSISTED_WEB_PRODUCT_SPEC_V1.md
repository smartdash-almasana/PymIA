# Servicio 1 — Producto web asistido

**Ciclo:** `CYCLE_054_DEFINE_SERVICE_1_ASSISTED_WEB_PRODUCT`

**Estado:** `DECIDED`

## Objetivo

Convertir Servicio 1 en una experiencia web utilizable por una persona sin conocimientos técnicos ni contables avanzados, preservando la raíz productiva única, la confirmación explícita del responsable y la ejecución determinística.

## Tecnología

- HTML semántico.
- HTMX para actualizaciones parciales.
- CSS sencillo y accesible.
- JavaScript mínimo y no obligatorio para completar el flujo principal.

HTMX, rutas, contratos, motores y estados internos no deben aparecer en la interfaz visible.

## Lenguaje visible

La interfaz debe usar español claro, directo y cotidiano.

### Términos prohibidos en pantalla

- ingesta
- pipeline
- binding
- runtime
- capacidad atómica
- variable canónica
- outcome
- delivery
- patología
- kernel
- FSM

### Equivalencias visibles

| Término interno | Texto visible |
|---|---|
| ingesta | subir archivo |
| patología | revisión |
| capacidad | análisis disponible |
| binding | relación entre columnas |
| confirmación del dueño | confirmación del responsable |
| computation | cálculo |
| outcome | resultado |
| delivery | archivo para descargar |
| blocked | no se puede continuar |
| evidence | datos utilizados |

## Flujo principal

1. Subir un archivo de Excel.
2. Ver qué hojas y columnas fueron encontradas.
3. Responder preguntas simples sobre columnas ambiguas.
4. Confirmar o corregir el significado de los datos.
5. Elegir explícitamente qué se quiere revisar.
6. Ejecutar el cálculo gobernado correspondiente.
7. Mostrar resultado, datos utilizados, forma de cálculo y límites de interpretación.
8. Permitir descarga sólo cuando la entrega esté autorizada.

## Pantallas mínimas

### 1. Inicio

Título visible:

`REVISAR INFORMACIÓN DE MI NEGOCIO`

Texto:

`Subí un archivo de Excel y te ayudaremos a entenderlo paso a paso.`

Acción principal:

`Elegir archivo`

Aclaraciones:

- `Tu archivo no se modifica.`
- `Antes de hacer cálculos, te pediremos que confirmes qué significa cada dato.`

### 2. Archivo recibido

Debe mostrar:

- nombre del archivo;
- hojas encontradas;
- cantidad de filas y columnas;
- avisos comprensibles;
- acción `Continuar`.

No debe mostrar identificadores internos ni estructuras técnicas.

### 3. Confirmación de columnas

Cada pregunta debe ser concreta y presentar:

- nombre original de la columna;
- ejemplo breve de valores;
- opciones comprensibles;
- `Otra cosa`;
- `No estoy seguro`.

Nunca se debe forzar una confirmación falsa.

### 4. Elección de revisión

Título:

`¿Qué querés revisar?`

Cada opción debe explicar en una frase qué responde. No mostrar códigos como `PYME_026`, `LIQ_001` o `REN_002`.

La selección debe ser explícita. No existe selección automática de revisión.

### 5. Resultado

Debe mostrar, en este orden:

1. nombre comprensible de la revisión;
2. resultado principal;
3. explicación breve;
4. datos utilizados;
5. advertencia de alcance;
6. acción secundaria `Ver cómo se calculó`;
7. descarga sólo si está autorizada.

No debe presentar diagnósticos causales ni recomendaciones universales.

## Accesibilidad obligatoria

- estructura correcta de encabezados;
- navegación completa con teclado;
- foco visible;
- etiquetas asociadas a todos los controles;
- contraste suficiente;
- tamaño de texto legible;
- botones amplios;
- mensajes de error junto al problema;
- estados expresados con texto e icono, no sólo color;
- avisos dinámicos anunciables por lectores de pantalla;
- ausencia de ventanas emergentes innecesarias;
- ausencia de animaciones decorativas;
- ausencia de límites de tiempo;
- diseño adaptable a pantallas pequeñas.

Estados visibles permitidos:

- `Confirmado`
- `Necesita revisión`
- `No se puede usar`

## Reglas arquitectónicas

- La web llama a la raíz productiva única de Servicio 1.
- La web no replica fórmulas ni reglas de negocio.
- La web no selecciona análisis automáticamente.
- La web no habilita LLM en runtime.
- La web no genera diagnóstico causal.
- La web no autoriza entregas por sí misma.
- La web conserva la confirmación explícita del responsable.
- Los doce códigos internos permanecen ocultos al usuario final.

## Alcance inicial

Incluido:

- XLSX;
- preguntas y respuestas sobre columnas;
- selección explícita entre las doce revisiones productivas;
- ejecución determinística;
- resultado comprensible;
- trazabilidad del caso;
- descarga autorizada.

Excluido:

- PDF;
- OCR;
- correo electrónico;
- WhatsApp;
- agente autónomo;
- conectores bancarios o ERP;
- servidores MCP nuevos;
- selección automática;
- nuevas patologías.

## Criterios de aceptación

1. Una persona puede completar el flujo sin conocer términos técnicos.
2. Ningún texto visible contiene los términos prohibidos.
3. Todas las decisiones relevantes requieren una acción explícita.
4. El flujo principal funciona con teclado.
5. `No estoy seguro` está disponible en toda pregunta de significado.
6. Los errores explican qué ocurrió y cómo continuar.
7. La web no duplica lógica del núcleo determinístico.
8. La descarga permanece bloqueada cuando la capacidad no la autoriza.
9. Los resultados muestran límites de interpretación.
10. La regresión completa de Servicio 1 permanece en verde.

## Próximo ciclo autorizado

`CYCLE_055_IMPLEMENT_SERVICE_1_ASSISTED_WEB_VERTICAL_SLICE`

Debe implementar una primera sección vertical completa:

`subir XLSX → confirmar columnas → elegir revisión → ejecutar → mostrar resultado`

No debe implementar todavía historial persistente completo, agente secretario, PDF, OCR ni conectores externos.
