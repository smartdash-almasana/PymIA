# Corpus migrado — Ingeniería conversacional SmartPyme → PymIA

## Estado

Migración amplia, sin depuración fina.  
Uso previsto: corpus de trabajo para revisión posterior.

## 1. Principio general

Fuente: `SmartPyme/docs/architecture/CONVERSATIONAL_METHODS.md`

SmartPyme trabaja con dos métodos complementarios:

```text
Mayéutica → hacia afuera, en la interacción con el dueño.
Método hipotético-deductivo → hacia adentro, en el procesamiento del sistema.
```

La conversación no es solo interfaz de chat. Es capa operativa central que permite:

- recibir la demanda del dueño;
- transformar dolor confuso en formulación clara;
- pedir evidencia sin invadir;
- registrar autorizaciones;
- sostener trazabilidad;
- producir decisiones documentadas;
- cerrar ciclos de diagnóstico, propuesta y acción.

Regla:

```text
La mayéutica ordena la demanda.
El método hipotético-deductivo ordena la investigación.
```

## 2. Primer tiempo lógico

Fuente: `SmartPyme/docs/adr/ADR-CAT-001A-primer-tiempo-logico-historia-clinica-pyme.md`

El primer contacto entre SmartPyme y una PyME no es onboarding ni chat aislado. Es:

```text
primer tiempo lógico clínico-operacional.
```

Constituye:

- apertura del caso;
- habilitación clínica del tenant;
- inicio de memoria operacional;
- comienzo del laboratorio PyME.

Objetivo:

```text
transformar caos operativo difuso
→ en estructura operacional contrastable.
```

Orden diagnóstico correcto:

```text
1. Recepción
2. Taxonomía inicial
3. Anamnesis conversacional
4. Hipótesis iniciales
5. Pedido documental
6. Contraste documental
7. Laboratorio inicial
8. Primer informe
9. Apertura de historia clínica PyME
```

No diagnosticar antes de:

- entender tipo de PyME;
- comprender dolor;
- recibir evidencia suficiente.

## 3. Chat y producto

Fuente: `SmartPyme/docs/adr/ADR-CAT-001A-primer-tiempo-logico-historia-clinica-pyme.md`

El chat es:

```text
la interfaz de recepción.
```

El producto real es:

```text
la recepción clínica-operacional de la PyME.
```

La conversación no precede al laboratorio. La conversación es el comienzo del laboratorio.

## 4. Conversación no invasiva

Fuente: `SmartPyme/docs/adr/ADR-CAT-001A-primer-tiempo-logico-historia-clinica-pyme.md`

La anamnesis debe ser:

- progresiva;
- pausable;
- retomable;
- explicativa;
- no intrusiva.

La PyME no debe sentir:

```text
me están haciendo llenar un ERP.
```

Debe sentir:

```text
me están ayudando a entender qué me pasa.
```

## 5. Mayéutica operativa

Fuente: `SmartPyme/docs/architecture/CONVERSATIONAL_METHODS.md`

Mayéutica significa:

```text
preguntar poco,
preguntar claro,
preguntar lo necesario,
preguntar con propósito.
```

El sistema debe ser:

```text
no invasivo en el tono,
duro en las condiciones.
```

Si falta información, SmartPyme no inventa. Debe pedir información mínima y esperar.

## 6. Dueño como fuente

Fuente: `SmartPyme/docs/architecture/CONVERSATIONAL_METHODS.md`

El dueño es fuente de:

- demanda;
- contexto;
- documentación;
- evidencia;
- convalidación;
- autorización;
- decisión.

No debe ser tratado como obstáculo. Debe ser tratado como fuente primaria del caso, pero ordenada, curada y validada.

## 7. Estados conversacionales históricos

Fuente: `SmartPyme/app/laboratorio_pyme/conversation/state.py`

Fases del protocolo clínico de investigación:

```text
ANAMNESIS_GENERAL
FOCO_SINTOMAS
RECOLECCION_EVIDENCIA
ANALISIS_HIPOTESIS
BLOQUEO_POR_EVIDENCIA
```

El estado conversacional representa:

```text
memoria viva de una sesión con un dueño de PyME.
No es un formulario: es un expediente clínico-operacional en construcción.
```

## 8. Anamnesis contextual

Fuente: `SmartPyme/app/laboratorio_pyme/conversation/state.py`

Campos de contexto inicial:

```text
rubro
tamano_aprox
urgencia
impacto_economico_estimado
impacto_tiempo
proceso_afectado
periodo_problema
evidencia_disponible
```

Estos campos son insumos de recepción y foco, no decoración.

## 9. Preguntas de apertura

Fuente: `SmartPyme/app/laboratorio_pyme/conversation/questions.py`

Preguntas de apertura migradas:

```text
Contame, qué es lo que más te preocupa del negocio ahora mismo?
Dónde sentís que el negocio te está fallando hoy?
Si tuvieras que señalar un problema urgente, cuál sería?
```

Regla asociada:

```text
Una sola pregunta por turno.
La más informativa posible.
Nunca diagnostica: investiga.
```

## 10. Preguntas de contexto crítico

Fuente: `SmartPyme/app/laboratorio_pyme/conversation/questions.py`

- Rubro: `Para entender mejor el caso: en qué rubro está tu negocio?`
- Proceso afectado: `Qué proceso puntual está más afectado hoy (ventas, caja, stock, compras u otro)?`
- Período: `Desde cuándo notaste este problema?`
- Impacto: `Qué impacto te está generando hoy en plata o en tiempo?`

## 11. Preguntas de evidencia

Fuente: `SmartPyme/app/laboratorio_pyme/conversation/questions.py`

- ventas_periodo → ventas del último trimestre en Excel o PDF;
- compras_periodo → facturas o registros de compras del mismo período;
- lista_precios_actual / vigente → lista de precios actual aunque esté desactualizada;
- resumen_caja_diaria → cierre diario de caja aunque sea manual;
- inventario_actual → inventario actualizado del stock actual;
- ultimas_ventas_por_producto → productos con movimiento reciente;
- fecha_ultima_compra_por_item → última compra por artículo;
- descripcion_procesos_repetitivos → tarea repetitiva que consume tiempo;
- tiempo_estimado_por_tarea → horas semanales;
- herramientas_actuales_usadas → Excel, sistema, papel u otras herramientas.

## 12. Hipótesis investigativas históricas

Fuente: `SmartPyme/app/laboratorio_pyme/conversation/hypotheses.py`

Cada hipótesis es una posibilidad investigativa, nunca un diagnóstico.

Estructura:

```text
síntomas → hipótesis → evidencia → preguntas
```

Hipótesis migradas:

### margen_erosionado

Descripción: ventas sostenidas pero rentabilidad caída por costos, inflación o precios atrasados.

Evidencia requerida:

- ventas_periodo;
- compras_periodo;
- lista_precios_vigente;
- costo_mercaderia_vendida.

### caja_inconsistente

Descripción: dinero disponible no coincide con ventas o movimientos esperados.

Evidencia requerida:

- resumen_caja_diaria;
- ventas_registradas;
- egresos_registrados.

### stock_inmovilizado

Descripción: capital atrapado en mercadería con baja rotación o sin salida.

Evidencia requerida:

- inventario_actual;
- ultimas_ventas_por_producto;
- fecha_ultima_compra_por_item.

### precios_atrasados

Descripción: precios de venta detrás de costos de reposición.

Evidencia requerida:

- lista_precios_actual;
- fecha_ultima_actualizacion_precios;
- facturas_proveedores_recientes.

### tiempo_perdido

Descripción: dueño o equipo pierde horas en procesos manuales repetitivos.

Evidencia requerida:

- descripcion_procesos_repetitivos;
- tiempo_estimado_por_tarea;
- herramientas_actuales_usadas.

## 13. Método interno hipotético-deductivo

Fuente: `SmartPyme/docs/architecture/CONVERSATIONAL_METHODS.md`

Secuencia interna:

```text
Dolor expresado
→ síntoma operativo
→ patología posible
→ hipótesis investigable
→ variables necesarias
→ evidencia requerida
→ curación de datos
→ validación de condiciones
→ comparación/fórmula
→ diagnóstico
→ reporte
→ propuesta
→ nueva decisión del dueño
```

Regla:

```text
Mal: Hay pérdida de margen.
Bien: Investigar si existe pérdida de margen por desalineación entre costos reales y precios de venta durante un período determinado.
```

## 14. Diferencias semánticas obligatorias

Fuente: `SmartPyme/docs/architecture/CONVERSATIONAL_METHODS.md`

| Concepto | Significado |
|---|---|
| Dolor | Lo que el dueño expresa |
| Síntoma | Señal operativa interpretada |
| Patología posible | Patrón de daño que podría estar ocurriendo |
| Hipótesis | Formulación verificable |
| Diagnóstico | Resultado de contrastar evidencia |
| Hallazgo | Diferencia cuantificada, trazable y accionable |

## 15. Relación con informe

Fuente: `SmartPyme/docs/adr/ADR-CAT-001A-primer-tiempo-logico-historia-clinica-pyme.md`

El primer informe debe contener:

- síntomas detectados;
- hipótesis principales;
- evidencia recibida;
- evidencia faltante;
- hallazgos iniciales;
- riesgos visibles;
- próximos pasos.

Incluso un informe parcial puede ser válido si es:

- consistente;
- honesto;
- útil;
- trazable.

## 16. Persistencia obligatoria

Fuente: `SmartPyme/docs/adr/ADR-CAT-001A-primer-tiempo-logico-historia-clinica-pyme.md`

El sistema debe persistir:

- tenant_id;
- frases textuales;
- anamnesis originaria;
- taxonomía inicial;
- hipótesis iniciales;
- patologías sospechadas;
- documentos pedidos;
- documentos recibidos;
- evidencia curada;
- hallazgos;
- informes emitidos.

Persistir solamente mensajes de chat es insuficiente.

## 17. Protocolo epistemológico conversacional

Fuente: `SmartPyme/docs/adr/ADR-EP-002-hermes-conversational-protocol.md`

La salida conversacional debe comunicar estado operativo y evidencia, no respuestas mágicas.

Estados epistemológicos obligatorios:

```text
CONFIRMADO
INFERIDO
PENDIENTE
BLOQUEADO
DECISION_REQUERIDA
```

Modos de copilotaje:

- DIOS: máxima soberanía del dueño y mínimo margen interpretativo del sistema;
- HIBRIDO: ejecución compartida entre automatización y validación humana frecuente;
- INVESTIGADOR: recolección de evidencia y reducción de incertidumbre antes de actuar.

Toda entrega conversacional operativa debe incluir, cuando corresponda, el 6-Step Report:

1. qué tenemos;
2. qué alcanzamos;
3. qué todavía no sabemos;
4. qué falta;
5. qué decisión del dueño desbloquea;
6. qué dato duro certifica.

## 18. Reglas semánticas rectoras

Fuente: `SmartPyme/docs/architecture/CONVERSATIONAL_METHODS.md`

1. El dolor del dueño no es diagnóstico.
2. El síntoma no es patología confirmada.
3. La patología posible no es hallazgo.
4. El hallazgo requiere evidencia, comparación y diferencia cuantificada.
5. El sistema no pide datos porque sí.
6. Pide datos porque una hipótesis necesita variables y evidencia para ser verificada.
7. Si falta evidencia mínima, se pide aclaración.
8. No se crea caso operativo sin material suficiente.
9. No se genera reporte diagnóstico sin evidencia trazable.
10. No se ejecuta acción sin decisión registrada.
11. La mayéutica ayuda al dueño a formular.
12. El método hipotético-deductivo ayuda al sistema a verificar.

## 19. Conversación saludable

Fuente: `SmartPyme/docs/architecture/CONVERSATIONAL_METHODS.md`

Una conversación saludable debe:

- reducir ambigüedad;
- no abrumar;
- no inventar;
- pedir evidencia concreta;
- explicar para qué se pide;
- dejar al dueño en control;
- registrar decisiones;
- abrir el siguiente paso si corresponde.

## 20. Implicancia para implementación futura en PymIA

Este corpus sugiere que PymIA no debe operar solo como:

```text
claim → formatter → respuesta
```

Debe recuperar el patrón:

```text
sesión → anamnesis → foco síntomas → evidencia → hipótesis → pregunta siguiente → informe
```

La migración de runtime queda fuera de este documento. Este archivo es fuente de corpus para depuración posterior.
