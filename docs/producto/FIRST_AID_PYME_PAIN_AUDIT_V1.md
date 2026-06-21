# FIRST_AID_PYME_PAIN_AUDIT_V1

## Estado

```text
Tipo: PRODUCT_AUDIT
Estado: DRAFT_APPLIED
Runtime impact: NONE
Code impact: NONE
```

## Propósito

Auditar la sección `Primeros Auxilios PyME` contra dolores reales de PyMEs y comercios.

La pregunta de esta auditoría es:

```text
¿Primeros Auxilios cubre problemas frecuentes, simples y vendibles sin caer en diagnóstico completo, macro genérica, BI o consultoría abstracta?
```

---

# 1. Tesis

Primeros Auxilios debe atender el primer nivel de dolor operativo:

```text
Tengo algo desordenado, incompleto o confuso y necesito que alguien lo mire, lo ordene o me diga qué se puede saber con eso.
```

No debe prometer:

```text
diagnóstico integral
rentabilidad real completa
auditoría contable
ERP
BI permanente
automatización total
reestructuración de la empresa
```

Debe prometer:

```text
revisión puntual
orden inicial
detección de señales visibles
faltantes explícitos
siguiente pregunta útil
```

---

# 2. Dolor PyME principal: Excel desordenado

## Lenguaje del dueño

```text
Tengo este Excel hecho un desastre.
No entiendo esta planilla.
Nadie sabe cómo está armado esto.
Hay fórmulas rotas.
Hay columnas mezcladas.
Esto lo hizo un empleado que ya no está.
```

## Cuello de botella real

La PyME opera con Excel como sistema informal.

Problemas típicos:

```text
encabezados ambiguos
hojas duplicadas
celdas combinadas
fechas mal cargadas
números como texto
totales intermedios
fórmulas rotas
archivos copiados muchas veces
columnas sin significado claro
```

## Qué puede hacer Primeros Auxilios

```text
detectar estructura probable
identificar hojas útiles
marcar columnas ambiguas
señalar fórmulas rotas o faltantes
limpiar parcialmente datos legibles
devolver resumen de problemas visibles
pedir aclaración donde no alcanza la evidencia
```

## Qué no debe hacer

```text
ejecutar macros del usuario
sobrescribir el archivo original
asumir significado de columnas ambiguas
diagnosticar negocio completo por una planilla
inventar costos, precios o márgenes
```

## Veredicto

```text
APTO_FIRST_AID
```

---

# 3. Dolor PyME: análisis de datos básico

## Lenguaje del dueño

```text
Quiero saber qué vendo más.
Quiero ver qué productos se mueven.
Quiero sacar algo claro de esta tabla.
Quiero entender estos números.
```

## Cuello de botella real

El dueño tiene datos, pero no lectura.

Problemas típicos:

```text
ventas sin resumen
productos sin agrupación
clientes mezclados
canales no separados
fechas no normalizadas
datos sin indicador de calidad
```

## Qué puede hacer Primeros Auxilios

```text
top productos
top clientes si existe dato
ventas por período si existe fecha válida
conteo de registros
señales de duplicados
campos vacíos
estructura de tabla
mini-resumen operativo
```

## Qué no debe hacer

```text
concluir rentabilidad si no hay costos
recomendar estrategia comercial completa
hacer forecast sin serie suficiente
confundir ventas con ganancia
```

## Veredicto

```text
APTO_FIRST_AID_CON_LIMITES
```

---

# 4. Dolor PyME: fórmulas y macros

## Lenguaje del dueño

```text
Esta fórmula no anda.
La macro dejó de funcionar.
Este Excel calcula cualquier cosa.
No sé de dónde sale este total.
```

## Cuello de botella real

La PyME depende de automatizaciones artesanales no gobernadas.

Problemas típicos:

```text
fórmulas rotas
rangos mal referenciados
hojas renombradas
macros heredadas
celdas protegidas
copias manuales
archivos con lógica invisible
```

## Qué puede hacer Primeros Auxilios

```text
detectar presencia de fórmulas
identificar errores visibles
señalar dependencias internas
marcar zonas de riesgo
explicar que una macro no debe ejecutarse sin revisión
pedir versión segura o copia del archivo
```

## Qué no debe hacer

```text
ejecutar macros automáticamente
reparar lógica crítica sin entender proceso
certificar que el cálculo es correcto sin evidencia externa
reconstruir un sistema administrativo entero
```

## Veredicto

```text
APTO_FIRST_AID_SOLO_REVISION_SEGURA
```

---

# 5. Dolor PyME: conciliación bancaria simple

## Lenguaje del dueño

```text
No me cierra el banco.
No sé qué cobros faltan.
Mercado Pago no coincide con ventas.
Tengo movimientos sin identificar.
```

## Cuello de botella real

La plata entra y sale por múltiples medios, pero la explicación está dispersa.

Fuentes típicas:

```text
extracto bancario
reporte de ventas
Mercado Pago
POS
efectivo
transferencias
Excel manual
```

## Qué puede hacer Primeros Auxilios

Con una fuente:

```text
clasificar el archivo recibido
marcar movimientos sin descripción clara
identificar columnas necesarias
pedir la segunda fuente necesaria
```

Con dos fuentes simples:

```text
comparación inicial de importes
posibles coincidencias
posibles diferencias
movimientos no conciliados
faltantes explícitos
```

## Qué no debe hacer

```text
auditoría contable
confirmar fraude
certificar saldos
hacer conciliación legal/fiscal
interpretar retiros sin contexto
```

## Veredicto

```text
APTO_FIRST_AID_PARA_TRIAGE
ESCALA_A_NIVEL_2_SI_HAY_CRUCE_REAL
```

---

# 6. Dolor PyME: lista de precios y costos

## Lenguaje del dueño

```text
No sé si trasladé los aumentos.
Tengo precios viejos.
No sé qué producto deja plata.
Me aumentaron proveedores y no sé qué tocar.
```

## Cuello de botella real

Precios, costos y márgenes suelen estar desalineados.

Problemas típicos:

```text
productos sin costo
costos viejos
listas duplicadas
precios sin fecha
proveedores mezclados
familias no normalizadas
margen confundido con markup
```

## Qué puede hacer Primeros Auxilios

```text
detectar productos sin costo
marcar precios vacíos o duplicados
comparar columnas precio/costo si existen
identificar familias o categorías si están presentes
señalar que no puede calcular margen real si faltan costos, comisiones o impuestos
```

## Qué no debe hacer

```text
calcular rentabilidad real sin costos suficientes
recomendar aumentos definitivos sin contexto
asumir IVA, descuentos, comisiones o envíos
```

## Veredicto

```text
APTO_FIRST_AID_CON_PREGUNTA_PROVOCADORA
```

Pregunta provocadora típica:

```text
Veo productos con precio pero sin costo actualizado. ¿Querés que miremos margen real con facturas o lista de costos?
```

---

# 7. Dolor PyME: stock

## Lenguaje del dueño

```text
No sé qué stock tengo.
El sistema no coincide.
Tengo productos parados.
No sé qué comprar.
```

## Cuello de botella real

El stock suele mezclar existencia física, sistema, ventas y compras sin trazabilidad plena.

Problemas típicos:

```text
SKU duplicados
productos sin movimiento
stock negativo
stock sin costo
fechas ausentes
unidades mezcladas
nombres inconsistentes
```

## Qué puede hacer Primeros Auxilios

```text
detectar columnas de producto/SKU/cantidad
marcar stock negativo o vacío
listar productos sin movimiento si hay fecha
identificar duplicados probables
pedir ventas o compras si se quiere calcular rotación
```

## Qué no debe hacer

```text
confirmar stock físico sin conteo
calcular rotación si no hay ventas o fechas
recomendar compras sin demanda histórica
```

## Veredicto

```text
APTO_FIRST_AID_PARA_ORDEN_Y_ALERTAS
ESCALA_A_NIVEL_2_PARA_ROTACION_CAJA_O_COMPRAS
```

---

# 8. Dolor PyME: tareas manuales repetitivas

## Lenguaje del dueño

```text
Copiamos todo a mano.
Perdemos horas cargando datos.
Cada semana hacemos lo mismo.
Esto habría que automatizarlo.
```

## Cuello de botella real

La PyME no necesita automatizar todo; necesita detectar qué repetición duele y si vale la pena tratarla.

Problemas típicos:

```text
doble carga
copiar y pegar entre archivos
control manual de cobranzas
armado manual de reportes
renombrar archivos
conciliación artesanal
```

## Qué puede hacer Primeros Auxilios

```text
registrar proceso declarado
estimar esfuerzo si el dueño informa frecuencia y tiempo
identificar evidencia necesaria
señalar si es candidato a automatización
pedir muestra del archivo o flujo
```

## Qué no debe hacer

```text
implementar automatización inmediata
prometer ahorro sin medir frecuencia
reemplazar proceso completo sin mapa mínimo
```

## Veredicto

```text
APTO_FIRST_AID_COMO_TRIAGE_DE_AUTOMATIZACION
```

---

# 9. Matriz de aceptación FIRST_AID

| Dolor | Entra en Primeros Auxilios | Límite | Escala si |
|---|---:|---|---|
| Excel desordenado | SÍ | no macro/BI/diagnóstico total | aparecen señales de margen, caja o stock |
| Análisis simple de datos | SÍ | no rentabilidad sin costos | pide explicación causal |
| Fórmulas rotas | SÍ | revisión segura, no ejecución ciega | fórmula gobierna proceso crítico |
| Macros | PARCIAL | no ejecutar macros | requiere rediseño de proceso |
| Conciliación bancaria | PARCIAL | triage o cruce simple | hay varias fuentes y diferencias materiales |
| Lista de precios/costos | SÍ | no asumir impuestos/comisiones | busca margen real |
| Stock | SÍ | no confirmar físico | busca rotación/caja/compras |
| Automatización manual | SÍ | sólo triage | requiere implementación o ROI |

---

# 10. Subopciones recomendadas para Primeros Auxilios

Cuando el dueño elige `Primeros Auxilios`, PymIA debería preguntar:

```text
¿Qué querés revisar ahora?
```

Opciones recomendadas:

```text
A. Un Excel o planilla desordenada
B. Fórmulas, totales o cálculos que no cierran
C. Una lista de precios o costos
D. Stock o inventario
E. Caja, banco o conciliación simple
F. Ventas o datos comerciales
G. Una tarea manual repetitiva
H. Otro archivo o problema puntual
```

---

# 11. Promesa owner-facing recomendada

```text
Vamos a hacer una revisión inicial y prudente.
No es un diagnóstico completo de la empresa.
Te vamos a decir qué se puede leer, qué está desordenado, qué señales aparecen, qué dato falta y cuál sería el siguiente paso razonable.
```

---

# 12. Salida mínima esperada

Toda experiencia de Primeros Auxilios debe devolver:

```text
1. Qué recibimos.
2. Qué tipo de archivo/problema parece ser.
3. Qué se pudo revisar.
4. Qué señales o problemas visibles aparecen.
5. Qué no se puede afirmar todavía.
6. Qué evidencia falta.
7. Próximo paso sugerido.
```

---

# 13. Criterio de bloqueo sano

Primeros Auxilios debe bloquear o pedir aclaración si:

```text
no hay archivo ni descripción suficiente
la columna clave es ambigua
el archivo mezcla procesos incompatibles
la macro no puede evaluarse sin ejecución riesgosa
se pide rentabilidad sin costos
se pide conciliación sin segunda fuente
se pide stock real sin conteo o inventario observado
```

Bloqueo correcto:

```text
Con lo que tengo puedo ordenar la fuente, pero no confirmar el problema. Para avanzar necesito X.
```

---

# 14. Criterio de escalamiento a Nivel 2

Primeros Auxilios debe sugerir Nivel 2 cuando aparece una pregunta causal:

```text
¿Por qué no me queda plata?
¿Qué productos pierden margen?
¿Por qué no cierra la caja?
¿Qué stock me inmoviliza capital?
¿Qué canal me conviene?
```

Regla:

```text
Nivel 1 ordena y detecta señal.
Nivel 2 explica cuello de botella con evidencia suficiente.
```

---

# 15. Veredicto de auditoría

```text
PRIMEROS_AUXILIOS_PYME = PRODUCTIVAMENTE_VALIDO
```

Pero sólo si se mantiene esta frontera:

```text
revisión puntual
una fuente o problema acotado
baja fricción
sin diagnóstico total
sin ejecución riesgosa de macros
sin cálculo sin suficiencia
con pedido explícito de evidencia faltante
con pregunta siguiente proporcional
```

---

# 16. Decisión recomendada

Agregar esta auditoría como base de la futura experiencia owner-facing de Primeros Auxilios.

No autoriza todavía:

```text
runtime
CLI
UI
rendering
storage
OCF write-model
application wiring
```

Siguiente documento lógico:

```text
FIRST_AID_OWNER_EXPERIENCE_V1.md
```

Ese documento debe convertir esta auditoría en flujo visible para el dueño.
