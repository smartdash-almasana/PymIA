# OWNER_SIMPLE_PRESENTATION_V1

## Estado

```text
FROZEN_LOCAL_PRESENTATION_CONTRACT
```

## Propósito

`owner_simple` es el protocolo local de presentación humana mínima para el dueño PyME dentro del flujo vertical actual de `PymIA-Live`.

Su función es traducir una parte de la salida técnica trazable a un bloque breve, prudente y conversacionalmente usable.

No es:

```text
- diagnóstico automático
- causa raíz confirmada
- reporte técnico completo
- sustituto de owner_facing_report
- sustituto de EvidenceRecord
- sustituto de PipelineRunRecord
- interfaz SaaS autónoma
```

Regla principal:

```text
owner_simple puede ayudar a conversar con el dueño, pero no puede afirmar más de lo que la evidencia permite.
```

---

## Forma actual

La forma actual de `owner_simple` es un objeto con cinco claves semánticas:

```text
que_entendimos
que_pudimos_leer
que_todavia_no_podemos_afirmar
proxima_pregunta
limites
```

### `que_entendimos`

Expresa una lectura breve de la preocupación declarada por el dueño.

Debe mantenerse como interpretación prudente, no como afirmación diagnóstica.

### `que_pudimos_leer`

Resume en lenguaje humano qué señales o áreas fueron legibles en la evidencia recibida.

No debe inferir causalidad desde nombres de columnas, hojas o encabezados.

### `que_todavia_no_podemos_afirmar`

Declara explícitamente el límite de conocimiento actual.

Debe impedir que el sistema convierta evidencia incompleta en diagnóstico.

### `proxima_pregunta`

Contiene la siguiente pregunta o reconducción que permite continuar la entrevista asistida.

Debe respetar la alineación semántica vigente cuando intervenga `QuestionAlignmentGate`.

### `limites`

Enumera límites explícitos de la salida.

Debe conservar como mínimo la regla de no diagnóstico sin evidencia suficiente ni confirmación del dueño.

---

## Consumidor autorizado actual

El único consumidor autorizado de `owner_simple` en este estado es:

```text
PymIA-Live/pymia/cli/vertical_slice.py
```

Esto significa que `owner_simple` está permitido como parte del modo CLI local actual, pero no queda promovido automáticamente como contrato multicanal del producto.

---

## Productor actual

El productor actual es:

```text
build_owner_simple_view()
```

ubicado en:

```text
PymIA-Live/pymia/smartpyme/owner_output.py
```

Esta ubicación separa la construcción de la salida humana mínima del canal CLI local.

`vertical_slice.py` queda como consumidor/orquestador local y no como dueño directo de la lógica `owner_simple`.

---

## Contrato declarativo actual

El copy y los mapas mínimos usados por `owner_simple` están gobernados temporalmente por:

```text
PymIA-Live/pymia/contracts/vertical_slice_copy_v1.json
PymIA-Live/pymia/contracts/vertical_slice_copy_v1.py
```

Esta decisión es temporal y limitada.

`vertical_slice_copy_v1` puede conservar la responsabilidad actual mientras exista un solo consumidor autorizado y no haya salida multicanal.

No queda autorizado seguir agregando complejidad owner-facing indefinidamente dentro de `vertical_slice_copy_v1`.

---

## Invariantes

`owner_simple` debe cumplir estas reglas:

```text
1. No diagnosticar causa raíz.
2. No declarar hallazgos confirmados sin evidencia suficiente.
3. Incluir límites explícitos.
4. Mantener lenguaje humano breve.
5. Preservar o reutilizar la próxima pregunta alineada cuando aplique QuestionAlignmentGate.
6. No reemplazar el reporte técnico ni la trazabilidad.
7. No exponer identificadores técnicos como salida humana principal.
8. No convertir nombres de columnas, hojas o encabezados en causalidad operativa.
9. No introducir conocimiento de dominio fuera de contratos declarativos vigentes.
10. Fallar de forma prudente cuando la evidencia no alcance.
```

---

## Prohibiciones

Mientras `owner_simple` permanezca en estado `FROZEN_LOCAL_PRESENTATION_CONTRACT`, queda prohibido:

```text
- agregar un segundo consumidor sin revisión arquitectónica
- usarlo como contrato de API, UI, PDF, WhatsApp, Telegram u otro canal
- convertirlo en diagnóstico
- seguir agregando copy owner_simple sin decisión explícita
- crear un nuevo contrato sólo por estética
- moverlo de contrato sólo por limpieza cosmética
- ampliar vertical_slice.py como capa de producto
- usar owner_simple como sustituto de owner_facing_report
- usar owner_simple como sustituto de evidencia o auditoría técnica
```

---

## Criterios de promoción futura

`owner_simple` sólo puede promoverse a contrato formal, por ejemplo `owner_output_v1` u `owner_brief_v1`, si aparece al menos una señal material:

```text
1. owner_simple se consume fuera de vertical_slice.py.
2. Aparece un segundo canal de salida: API, UI, PDF, WhatsApp, Telegram u otro.
3. Se requiere schema tipado formal.
4. Se detecta drift real entre tests, salida y contrato implícito.
5. Se vuelve la salida base del MVP.
6. Se necesita separar renderer técnico y renderer humano.
7. vertical_slice.py empieza a bloquear cambios materiales.
8. El contrato actual genera falla real de mantenimiento.
```

La promoción futura debe hacerse mediante una tarea explícita y no como saneamiento menor.

Nombre sugerido:

```text
OWNER_OUTPUT_CONTRACT_V1
```

---

## Criterios de refactor futuro

Sólo corresponde abrir `VERTICAL_SLICE_BOUNDARY_REDUCTION_V1` si se verifica una deuda técnica material, por ejemplo:

```text
- vertical_slice.py bloquea cambios funcionales relevantes
- owner output necesita reutilización fuera del CLI
- render_markdown_from_report impide un segundo canal
- los tests E2E se vuelven inmanejables por concentración de responsabilidades
- se decide formalmente promover owner_simple a owner_output_v1
```

No corresponde abrir ese refactor por estética, tamaño de archivo aislado o preferencia de nombres.

---

## Relación con `vertical_slice.py`

`vertical_slice.py` sigue siendo el modo CLI local operativo.

Su responsabilidad deseada de largo plazo es:

```text
- parsear argumentos
- invocar el flujo vertical
- recibir resultado
- escribir salida local
```

La lógica de construcción de `owner_simple` ya no debe vivir dentro de `vertical_slice.py`.

`vertical_slice.py` puede invocar `build_owner_simple_view()` como consumidor local, pero no debe volver a absorber helpers de presentación humana sin una decisión arquitectónica previa.

---

## Relación con `render_markdown_from_report()`

`render_markdown_from_report()` es el renderer markdown intencional del canal CLI local actual.

Puede contener la composición necesaria para la salida local mientras no exista un segundo canal.

Si aparece un segundo canal o una salida humana independiente, debe evaluarse la separación entre:

```text
- owner output semántico
- renderer markdown
- renderer técnico/auditable
- renderer humano
```

---

## Relación con `owner_facing_report`

`owner_simple` no reemplaza a `owner_facing_report`.

La relación vigente es:

```text
owner_facing_report = salida técnica owner-facing trazable
owner_simple = presentación humana mínima local
```

`owner_simple` puede resumir, limitar y presentar, pero no debe convertirse en fuente primaria de verdad.

---

## Relación con memoria vigente

Este documento respeta las decisiones vigentes:

```text
NO SPLIT NOW
NO MÁS MICRO-COPY CLEANUP
NO abrir nuevos contratos de copy salvo necesidad funcional clara
PymIA-Live debe quedar pequeño, trazable y gobernado por contratos declarativos
```

También respeta la regla de avance:

```text
Sólo intervenir si el próximo slice agrega capacidad operativa real o cierra deuda técnica material.
```

---

## Veredicto

```text
owner_simple queda congelado como protocolo local de presentación humana mínima.
Funciona como parte del CLI actual.
No queda promovido todavía a contrato formal multicanal.
No debe crecer sin decisión arquitectónica.
No debe refactorizarse por estética.
```
