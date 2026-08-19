# 00 — Resumen ejecutivo auditado

## Conclusión central

PymIA tiene coherencia conceptual fuerte, pero el repositorio mezcla capas vivas, legacy, documentación histórica, prototipos, contratos aspiracionales y artefactos parcialmente rotos.

El valor real del proyecto está en este núcleo:

```text
Dueño PyME + datos reales + evidencia estructurada
↓
contratos y validación
↓
kernel / gates determinísticos
↓
salida trazable y comprensible
↓
revisión humana cuando la evidencia no alcanza
```

La dirección correcta inmediata no es sumar más autonomía, más agentes ni más documentación. La dirección correcta es validar un Servicio 1 asistido con caso real, limpiar autoridad documental y eliminar Hermes por completo.

## Estado observado

Auditoría realizada sobre el repo extraído desde `PymIA-main.rar`.

Métricas observadas localmente:

| Métrica | Valor observado |
|---|---:|
| Archivos totales legibles en repo extraído | 1845 |
| Directorios | 154 |
| Archivos `.py` | 922 |
| Archivos `.md` | 792 |
| Archivos `.json` | 32 |
| Archivos `.yaml` / `.yml` | 28 |
| Archivos vacíos detectados | 166 |
| Archivos con referencias a Hermes | 309 |
| Referencias textuales a Hermes/hermes/HERMES | 2495 |
| Archivos `*service_1*.py` | 195 |

Estas cifras no son un juicio de calidad por sí solas, pero muestran una desproporción clara: hay una enorme superficie documental y contractual en relación con el núcleo ejecutable validado.

## Hallazgos principales

### 1. PymIA no debe ser entendido como chatbot ni agente

PymIA debe conservar la soberanía computacional. La conversación puede existir como interfaz, pero no puede decidir diagnóstico, verdad operacional ni avance de gates.

### 2. Hermes debe desaparecer

La decisión vigente elimina Hermes como agente, runtime, orchestrator, gateway o marca técnica. Esto transforma todas las referencias activas a Hermes en deuda.

No hay que “resolver la contradicción Hermes”. Hay que retirar Hermes.

### 3. El MVP real debe ser asistido

El primer producto validable no debería ser un SaaS autónomo. El recorte sano es:

```text
Servicio 1 — Primeros Auxilios Asistidos
CLI / operador humano / caso real supervisado / salida trazable
```

### 4. La documentación excede al sistema ejecutable

El repo documenta más de lo que parece poder ejecutar de manera estable hoy. Esto no invalida la arquitectura, pero obliga a congelar expansión documental hasta que haya evidencia de caso real.

### 5. `vertical_pipeline.py` es un concentrador de riesgo

Aunque `vertical_slice.py` fue reducido a CLI/adaptador, `PymIA-Live/pymia/application/vertical_pipeline.py` concentra 566 líneas y combina lectura de Excel, evidencia, reporte, adapter diagnóstico, question alignment y registro.

### 6. Hay fallas técnicas reproducibles

Un smoke test selectivo de `PymIA-Live` falla durante collection por import roto:

```text
ImportError: cannot import name 'load_formula_rules' from 'pymia.contracts.formula_rules_v1'
```

Además, en la primera prueba desde raíz aparecieron conflictos de paquetes y archivos vacíos por extracción parcial.

## Decisión de orientación

A partir de este checkpoint, la auditoría debe favorecer:

1. Menos documentos nuevos.
2. Menos abstracción aspiracional.
3. Más caso real.
4. Más contratos mínimos ejecutables.
5. Más evidencia reproducible.
6. Limpieza total de Hermes.
7. Separación entre catálogo aspiracional y catálogo activable.
8. No declarar producto/SaaS donde todavía hay servicio asistido.

## Recomendación ejecutiva

No avanzar con SaaS autónomo, runtime conversacional ni agente LLM. Avanzar con saneamiento y validación:

```text
Fase inmediata:
- retirar Hermes como autoridad técnica/documental;
- corregir imports rotos;
- definir MVP Servicio 1 asistido;
- ejecutar un caso real supervisado;
- producir evidencia de salida;
- recién después discutir automatización.
```
