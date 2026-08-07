# SmartPyme — MVP Realista y Filosofía Operacional

## Estado

Documento conceptual de producto.

Este documento consolida el criterio actual para un MVP realista, vendible y técnicamente serio de SmartPyme.

No describe la arquitectura total futura.

No describe el “reino completo”.

No describe una AGI empresarial.

Describe el primer producto que puede salir a la calle, recibir caos PyME real, estructurarlo, entregar valor y construir memoria operativa desde el uso real.

---

# 1. Tesis central

El MVP de SmartPyme no debe intentar administrar toda la empresa.

Debe resolver una función más básica y más valiosa:

```text
recibir caos operativo,
estructurarlo,
pedir evidencia,
ejecutar un análisis concreto,
devolver un hallazgo útil,
y registrar lo aprendido por tenant.
```

Ese es el núcleo.

La PyME argentina no suele llegar con procesos perfectos, datos ordenados y dashboards limpios.

Llega con:

```text
- Excel desordenados;
- PDFs;
- capturas;
- facturas;
- WhatsApp;
- intuiciones;
- urgencias;
- frases imprecisas;
- dolores económicos;
- decisiones tomadas a ojo;
- información dispersa;
- dependencia del dueño.
```

Por eso el primer valor de SmartPyme no está en “automatizar una empresa ideal”.

Está en construir una recepción inteligente para una empresa real.

---

# 2. Realismo PyME Argentina

El MVP debe partir de una verdad incómoda:

```text
la mayoría de las PyMEs no tienen el dato listo para ser automatizado.
```

Tienen fragmentos.

Tienen documentos.

Tienen personas que saben cosas.

Tienen memoria informal.

Tienen Excel vivos, no sistemas perfectos.

Tienen problemas que muchas veces no saben nombrar técnicamente.

Ejemplos:

```text
“No me cierra la caja.”
“Vendo pero no me queda plata.”
“No sé si me conviene producir esto.”
“Me parece que me falta stock.”
“Este Excel está imposible.”
“Los proveedores aumentan y no sé si trasladé bien los precios.”
```

Eso no es ruido descartable.

Eso es materia prima.

El MVP debe capturar esa materia prima, no exigir que el cliente piense como un sistema corporativo.

---

# 3. Filosofía operacional del MVP

El MVP no debe empezar desde una promesa abstracta.

Debe empezar desde una interacción concreta:

```text
cliente habla
→ sistema registra
→ sistema clasifica
→ sistema pide evidencia
→ sistema procesa
→ sistema devuelve algo útil
→ sistema conserva trazabilidad
```

La filosofía es:

```text
menos discurso,
más recepción;
menos formulario,
más conversación estructurada;
menos dashboard vacío,
más hallazgo accionable;
menos automatización total,
más utilidad inmediata.
```

SmartPyme no debe vender “IA”.

Debe producir una experiencia simple:

```text
“Mandé un archivo o expliqué un problema, y el sistema me devolvió claridad.”
```

---

# 4. Nueva etapa de la informática

SmartPyme pertenece a una etapa distinta de la informática.

Durante años el software exigió que el usuario se adaptara al sistema:

```text
formularios,
módulos rígidos,
campos obligatorios,
flujos cerrados,
ERP pesados,
pantallas administrativas.
```

La nueva etapa permite otra dirección:

```text
el sistema se adapta primero al lenguaje y al caos del usuario.
```

Pero esa adaptación no debe ser mágica ni caótica.

Debe estar gobernada por:

```text
- contratos;
- estados;
- evidencia;
- tenant_id;
- trazabilidad;
- clasificación;
- outputs verificables;
- límites explícitos.
```

La tecnología agente no debe significar autonomía sin control.

Debe significar:

```text
software que conversa,
interpreta,
pide evidencia,
usa herramientas,
y produce salidas útiles bajo restricciones.
```

---

# 5. Qué es el MVP

El MVP de SmartPyme es:

```text
recepción persistente del caos PyME
+
clasificación básica
+
evidencia mínima
+
microservicio útil
+
hallazgo accionable
+
registro por tenant_id
```

No es todavía:

```text
- sistema operativo organizacional completo;
- multiagente profundo;
- gobierno completo del reino;
- memoria avanzada;
- cientos de skills;
- tanques de conocimiento completos;
- ERP universal;
- automatización total.
```

---

# 6. Componentes obligatorios del MVP

## 6.1 Tenant

Toda interacción debe asociarse a un `tenant_id`.

Esto es obligatorio desde el inicio.

Sin tenant_id no hay historia operativa.

Sin historia operativa no hay aprendizaje de mercado.

El tenant permite construir:

```text
- dolores recurrentes;
- evidencia disponible;
- bloqueos frecuentes;
- demandas no resueltas;
- historial de archivos;
- outputs entregados;
- oportunidades futuras;
- taxonomía viva del cliente.
```

---

## 6.2 ReceptionRecord

Toda demanda debe registrarse.

Aunque no se pueda resolver.

Aunque esté incompleta.

Aunque sea confusa.

Aunque termine bloqueada.

Un `ReceptionRecord` debería conservar:

```text
- tenant_id;
- user_id si existe;
- canal;
- mensaje original;
- dolor expresado;
- clasificación inicial;
- estado;
- evidencia solicitada;
- evidencia recibida;
- resultado;
- bloqueo;
- oportunidad detectada;
- timestamp.
```

El pedido imposible también tiene valor.

Ejemplo:

```text
“Quiero saber si pierdo plata, pero no tengo costos.”
```

Eso revela:

```text
- dolor real;
- evidencia faltante;
- posible microservicio;
- patrón PyME;
- oportunidad educativa;
- futura skill;
- posible tanque de conocimiento.
```

---

## 6.3 Clasificación básica

El MVP debe poder clasificar demandas en categorías simples.

Ejemplos:

```text
- limpieza de Excel;
- conciliación;
- margen;
- stock;
- proveedores;
- costos;
- producción;
- caja/banco;
- documentación;
- automatización manual;
- consulta no resoluble todavía.
```

La clasificación no tiene que ser perfecta.

Debe ser suficiente para:

```text
- orientar la conversación;
- pedir evidencia;
- elegir microservicio;
- registrar demanda;
- construir taxonomía.
```

---

## 6.4 Evidencia mínima

El sistema debe pedir evidencia concreta.

No debe decir simplemente:

```text
“Faltan datos.”
```

Debe decir:

```text
“Para investigar margen necesito ventas del período y costos o facturas de proveedor.”
```

La evidencia mínima para el MVP puede ser:

```text
- Excel;
- PDF;
- factura;
- extracto;
- lista de precios;
- reporte de ventas;
- descripción del proceso;
- captura o archivo simple.
```

La regla es:

```text
sin evidencia suficiente, no se inventa diagnóstico.
```

---

## 6.5 Microservicio inicial

El MVP debe tener un microservicio fuerte.

No diez débiles.

El microservicio inicial debe cumplir:

```text
- fácil de entender;
- fácil de vender;
- frecuente en PyMEs;
- basado en archivos reales;
- con output visible;
- con bajo riesgo;
- con valor inmediato.
```

Candidatos:

```text
- limpieza y diagnóstico de Excel;
- conciliación simple;
- comparación básica de ventas/costos;
- detección de inconsistencias;
- revisión de lista de precios;
- comparación de proveedores;
- cálculo simple de margen.
```

La recomendación práctica:

```text
empezar con Excel.
```

Porque Excel es el sistema nervioso informal de muchas PyMEs.

---

## 6.6 Hallazgo accionable

El output no debe ser una respuesta decorativa.

Debe ser un hallazgo o reporte simple.

Ejemplos:

```text
- columnas problemáticas detectadas;
- filas duplicadas;
- diferencias entre totales;
- productos sin costo;
- precios vacíos;
- valores inconsistentes;
- posibles errores;
- próximo paso recomendado.
```

Un hallazgo útil debe tener:

```text
- entidad;
- problema;
- evidencia;
- diferencia o señal;
- recomendación.
```

Ejemplo:

```text
Producto “Leche 1L” aparece con precio de venta pero sin costo asociado.
No puede calcularse margen hasta completar costo.
```

---

## 6.7 Output descargable o legible

El cliente debe recibir algo concreto:

```text
- reporte Markdown;
- PDF simple;
- Excel corregido;
- CSV limpio;
- resumen de hallazgos;
- lista de próximos pasos.
```

La entrega debe sentirse como trabajo realizado.

No como conversación infinita.

---

# 7. Qué puede hacer un cliente con el MVP

Un cliente puede:

## 7.1 Conversar un problema real

Ejemplos:

```text
“No me cierra el banco.”
“Creo que pierdo plata.”
“No entiendo este Excel.”
“No sé qué producto me deja margen.”
“Quiero ordenar esta lista.”
```

---

## 7.2 Subir evidencia

Puede enviar:

```text
- Excel;
- PDFs;
- facturas;
- reportes;
- extractos;
- listas de precios;
- archivos desordenados.
```

---

## 7.3 Recibir preguntas inteligentes

El sistema pregunta poco, pero con precisión.

Ejemplo:

```text
“¿Qué período querés revisar?”
“¿Este archivo representa ventas, costos o stock?”
“¿Tenés facturas o costos para comparar contra ventas?”
```

---

## 7.4 Obtener una primera respuesta útil

Puede recibir:

```text
- inconsistencias;
- diferencias;
- archivos corregidos;
- alertas;
- datos faltantes;
- reporte simple;
- próximos pasos sugeridos.
```

---

## 7.5 Construir historial

Cada interacción deja rastro.

Con el tiempo, el sistema empieza a saber:

```text
- qué problemas trae ese cliente;
- qué evidencia suele tener;
- qué evidencia suele faltar;
- qué microservicios usa;
- qué bloqueos se repiten;
- qué oportunidades aparecen.
```

Esto no requiere LearningMemory avanzada.

Requiere recepción persistente bien diseñada.

---

# 8. Qué NO hace el MVP

El MVP no debe prometer:

```text
- administrar toda la empresa;
- reemplazar al contador;
- reemplazar un ERP;
- decidir por el dueño;
- automatizar todo;
- diagnosticar sin evidencia;
- operar sin autorización;
- entender cualquier documento arbitrario;
- resolver cualquier problema de negocio.
```

Debe poder decir:

```text
“Con lo que me diste todavía no puedo resolverlo.”
```

Ese bloqueo sano es parte del producto.

---

# 9. Por qué es vendible

Es vendible porque no exige que el cliente compre una visión completa.

Le ofrece una utilidad inmediata:

```text
“Mandame el archivo y te devuelvo algo mejor que lo que tenías.”
```

Eso es comprensible.

Eso es demostrable.

Eso es repetible.

La venta inicial no debería ser:

```text
“te vendo un sistema operativo organizacional multiagente.”
```

Debería ser:

```text
“te ayudo a ordenar, revisar o entender este problema concreto.”
```

El sistema operativo aparece después.

Primero aparece la utilidad.

---

# 10. Qué se vende realmente

En el fondo se vende:

```text
recepción inteligente del caos PyME.
```

Eso incluye:

```text
- escuchar el problema;
- traducirlo;
- pedir evidencia;
- procesar documentos;
- detectar señales;
- entregar claridad;
- registrar historia;
- proponer próximo paso.
```

La mayoría de las herramientas actuales presuponen orden.

SmartPyme puede diferenciarse porque parte del desorden.

---

# 11. Relación con DiscoveryMemory

El MVP debe incluir una forma inicial de `DiscoveryMemory`.

No técnica compleja.

No autónoma.

Simplemente:

```text
registro estructurado de demandas reales.
```

Debe guardar:

```text
- qué pide la gente;
- cómo lo dice;
- qué evidencia trae;
- qué evidencia falta;
- qué se pudo resolver;
- qué quedó bloqueado;
- qué microservicio se repite;
- qué demanda aparece con frecuencia.
```

Esto reemplaza parcialmente focus groups, encuestas y suposiciones.

No porque elimine toda investigación.

Sino porque captura demanda real mientras el producto opera.

---

# 12. De focus group a recepción viva

Un focus group produce opiniones.

La recepción viva produce:

```text
- demandas contextualizadas;
- urgencias reales;
- archivos reales;
- evidencia real;
- fricciones reales;
- disposición real a pagar;
- lenguaje espontáneo;
- problemas mal nombrados.
```

Ejemplo:

```text
“No sé por qué vendo mucho y no me queda plata.”
```

El cliente no pide “auditoría de margen”.

Pero el sistema puede detectar:

```text
- síntoma de pérdida de margen;
- posible desalineación costo-precio;
- necesidad de ventas y costos;
- oportunidad de microservicio;
- futura skill.
```

Eso es aprendizaje de producto desde la calle.

---

# 13. Adsorción y absorción del caos PyME

Puede pensarse en dos momentos.

## Adsorción

Primero el sistema captura señales superficiales:

```text
- frases;
- dolores;
- archivos;
- preguntas;
- bloqueos;
- síntomas;
- demandas.
```

Todavía no comprende todo.

Pero lo retiene en una superficie estructurada.

## Absorción

Después el sistema transforma esas señales en estructura:

```text
- taxonomía;
- microservicios;
- evidence requirements;
- skills;
- casos operativos;
- domain packs;
- tanques de conocimiento.
```

La adsorción captura.

La absorción metaboliza.

El MVP debe cubrir al menos la primera y una parte mínima de la segunda.

---

# 14. Escalabilidad del MVP

El MVP escala si nace pequeño en funciones pero serio en estructura.

Debe tener desde el inicio:

```text
Tenant
ReceptionRecord
EvidenceRecord
Finding
Task/Job
OutputReport
```

No escala si nace como:

```text
scripts sueltos
sin tenant_id
sin estados
sin evidencia
sin contratos
sin registros
```

La escalabilidad no depende de tener muchas funciones al principio.

Depende de que cada función deje trazabilidad y encaje en el core.

---

# 15. Core mínimo operativo

El core del MVP debe incluir:

```text
- recepción;
- persistencia;
- tenant_id;
- clasificación;
- evidencia;
- estados;
- trazabilidad mínima;
- ejecución segura;
- outputs.
```

No debe incluir todavía:

```text
- autonomía compleja;
- memoria avanzada;
- gobierno multiagente completo;
- atlas gigantesco;
- cientos de skills;
- capas cognitivas sofisticadas.
```

La fórmula correcta:

```text
core estable
+
capacidades emergentes desde la calle.
```

---

# 16. Estados mínimos

Una demanda puede quedar en:

```text
RECEIVED
CLASSIFIED
NEEDS_EVIDENCE
READY_TO_PROCESS
PROCESSING
DELIVERED
BLOCKED
UNSUPPORTED
```

Estos estados permiten ordenar el caos.

El MVP no necesita más complejidad.

---

# 17. Primeros microservicios posibles

## Opción A — Excel diagnosticado

Entrada:

```text
archivo Excel desordenado
```

Salida:

```text
- estructura detectada;
- columnas vacías;
- duplicados;
- inconsistencias;
- totales sospechosos;
- propuesta de limpieza;
- archivo corregido si aplica.
```

---

## Opción B — Margen simple

Entrada:

```text
ventas + costos/lista de precios
```

Salida:

```text
- productos sin costo;
- productos con margen bajo;
- diferencias visibles;
- familias críticas.
```

---

## Opción C — Conciliación simple

Entrada:

```text
extracto + reporte de ventas/cobros
```

Salida:

```text
- coincidencias;
- diferencias;
- movimientos no conciliados;
- próximos datos necesarios.
```

---

## Opción D — Proveedores

Entrada:

```text
facturas o listas de proveedores
```

Salida:

```text
- aumentos detectados;
- diferencias entre proveedores;
- productos críticos;
- sugerencia de revisión.
```

---

# 18. Recomendación de secuencia

Primero:

```text
Excel diagnosticado / limpieza operativa
```

Después:

```text
margen simple
```

Después:

```text
conciliación
```

Después:

```text
proveedores / costos
```

Motivo:

```text
Excel es el soporte común.
Antes de diagnosticar negocio, conviene aprender a leer y ordenar evidencia.
```

---

# 19. Tiempo estimado

Con una dedicación realista de 35 horas semanales:

```text
MVP técnico funcional: 80–120 horas
MVP vendible controlado: 120–180 horas
MVP robusto para primeros clientes: 180–250 horas
```

Traducción:

```text
funcional: 3 semanas
vendible controlado: 4–5 semanas
primeros clientes: 6–8 semanas
```

Condición:

```text
un microservicio fuerte primero,
no diez a medias.
```

---

# 20. Criterio de salida a la calle

El producto puede ofrecerse cuando pueda hacer consistentemente esto:

```text
recibir una demanda
→ registrar tenant
→ clasificar
→ pedir archivo/evidencia
→ procesar
→ entregar output útil
→ registrar resultado
```

No hace falta esperar:

```text
- LearningMemory;
- Domain Packs completos;
- tanques;
- multiusuario avanzado;
- dashboard grande;
- arquitectura perfecta.
```

La calle debe entrar temprano.

Porque la calle es parte de la construcción.

---

# 21. Qué prepara para el futuro

Este MVP prepara:

```text
- taxonomía viva;
- backlog validado;
- microservicios reales;
- evidencia de mercado;
- lenguaje PyME;
- patrones de bloqueo;
- primeros tenants;
- primeras asertividades;
- futuras skills;
- futuros tanques.
```

No es un MVP descartable.

Es el embrión real del sistema.

---

# 22. Riesgos

## 22.1 Sobrearquitectura

Riesgo:

```text
querer construir todo el sistema antes de vender.
```

Mitigación:

```text
un microservicio fuerte,
core mínimo,
recepción persistente.
```

---

## 22.2 Script suelto

Riesgo:

```text
resolver casos pero no registrar nada.
```

Mitigación:

```text
tenant_id + ReceptionRecord + EvidenceRecord desde el día uno.
```

---

## 22.3 Marketing antes que utilidad

Riesgo:

```text
prometer IA empresarial sin output concreto.
```

Mitigación:

```text
vender entrega concreta.
```

---

## 22.4 Diagnóstico sin evidencia

Riesgo:

```text
afirmar problemas sin base.
```

Mitigación:

```text
si falta evidencia, estado NEEDS_EVIDENCE o BLOCKED.
```

---

## 22.5 Construir para PyME ideal

Riesgo:

```text
diseñar para empresas ordenadas que no representan el mercado inicial.
```

Mitigación:

```text
diseñar para Excel real, PDF real, frase confusa real.
```

---

# 23. Principios finales

```text
El MVP no administra la empresa.
Recibe su caos.
```

```text
El MVP no promete inteligencia total.
Entrega claridad puntual.
```

```text
El MVP no reemplaza al dueño.
Le devuelve evidencia y próximos pasos.
```

```text
El MVP no necesita saber todo.
Necesita registrar bien lo que aparece.
```

```text
El MVP no nace para impresionar técnicamente.
Nace para ser usado.
```

---

# 24. Cierre

SmartPyme debe salir a la calle como una pieza simple, pero no trivial.

Simple en superficie:

```text
hablame,
mandame un archivo,
te devuelvo claridad.
```

Seria por debajo:

```text
tenant_id,
recepción,
evidencia,
clasificación,
hallazgo,
trazabilidad,
output.
```

Esa combinación es potente porque respeta dos realidades al mismo tiempo:

```text
la PyME real viene desordenada;
la nueva informática puede absorber ese desorden sin perder estructura.
```

El MVP correcto no es el sistema final reducido.

Es la primera máquina de absorción del caos PyME.

Y si esa máquina funciona, el resto de la arquitectura deja de ser teoría.

Pasa a ser consecuencia.
