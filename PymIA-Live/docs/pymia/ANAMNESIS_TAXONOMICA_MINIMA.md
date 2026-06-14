# Anamnesis Taxonómica Mínima — PymIA-Live

## Estado

Documento operativo extraído del acervo histórico de PymIA y depurado para PymIA-Live.

No arrastra dependencia con Hermes, MCP, Telegram, bot, UI ni canal productivo.

Este documento fija la regla de primer contacto, ficha mínima, taxonomía inicial y relación con evidencia.

---

## 1. Principio

PymIA-Live no debe comenzar por el archivo.

PymIA-Live debe comenzar por ubicar el organismo PyME observado.

El archivo, Excel, PDF, captura o planilla es evidencia. No es el ingreso conceptual al caso.

---

## 2. Orden correcto del primer contacto

```text
organismo / taxonomía
→ naturaleza operacional
→ preocupación declarada
→ anamnesis mínima
→ evidencia concreta
→ contraste
→ informe inicial
→ nuevas preguntas
```

---

## 3. Regla canónica

Antes de cualquier interpretación operacional, PymIA-Live debe intentar establecer:

```text
- tipo de empresa;
- rubro;
- naturaleza económica;
- dominio operacional;
- canales de venta;
- presencia de stock;
- presencia de producción o prestación de servicio;
- áreas críticas declaradas;
- documentación disponible.
```

Sin esta taxonomía mínima, las métricas pueden cambiar de significado y las preguntas pueden quedar mal orientadas.

---

## 4. Ficha mínima de ingreso

La ficha mínima debe capturar, cuando esté disponible:

```text
- tenant_id;
- nombre visible de la empresa;
- país / jurisdicción;
- tipo de empresa;
- rubro / industria;
- modelo comercial;
- canales de venta;
- cantidad aproximada de empleados;
- si produce, revende, distribuye o presta servicios;
- si maneja stock;
- áreas operativas presentes;
- preocupación principal declarada;
- frases textuales del dueño;
- dolores declarados;
- hipótesis propias del dueño;
- documentos disponibles;
- documentos solicitados;
- estado operativo;
- fecha de creación;
- fecha de actualización.
```

---

## 5. Taxonomía inicial

Representación conceptual mínima:

```json
{
  "empresa_tipo": "fabrica | comercio | servicios | distribucion | mixta | otra | desconocido",
  "industria": "textil | gastronomia | metalurgica | logistica | retail | servicios | otra | desconocido",
  "modelo_comercial": "b2b | b2c | marketplace | mayorista | minorista | mixto | desconocido",
  "canales_venta": [],
  "areas_criticas": [],
  "dolores_declarados": [],
  "hipotesis_duenio": [],
  "frases_textuales": [],
  "documentos_disponibles": [],
  "documentos_solicitados": [],
  "capabilities_iniciales": [],
  "catalogos_activados": []
}
```

Esta taxonomía no confirma hechos operativos. Es contexto inicial para orientar preguntas, evidencia y contraste.

---

## 6. Anamnesis operacional mínima

La anamnesis transforma el relato inicial del dueño en un mapa de incertidumbre.

Debe preservar:

```text
- relato literal;
- dolores declarados;
- dudas;
- certezas percibidas;
- hipótesis del dueño;
- áreas mencionadas;
- documentos disponibles;
- documentos faltantes;
- prioridad percibida;
- evidencia requerida.
```

Las frases del dueño no son evidencia dura. Son material semántico a contrastar.

---

## 7. Relación con evidencia

PymIA-Live debe unir dos fuentes:

```text
dolor declarado
→ documentación solicitada
→ evidencia estructurada
→ contraste
→ hallazgo o bloqueo por evidencia insuficiente
```

Si falta evidencia, PymIA-Live no inventa diagnóstico. Debe devolver un bloqueo accionable o una pregunta concreta.

---

## 8. Pedido de evidencia según dolor declarado

Ejemplos orientativos:

```text
Dolor de margen:
- ventas del período;
- costos unitarios o facturas de compra;
- lista de precios vigente.

Dolor de caja:
- cierre de caja;
- extractos bancarios;
- cuentas por cobrar / pagar;
- liquidaciones de medios de pago.

Dolor de stock:
- hoja de stock;
- movimientos;
- ventas por producto;
- inventario físico si existe.

Dolor de tiempo o tareas manuales:
- descripción del proceso;
- planillas usadas;
- capturas del flujo;
- frecuencia y responsables.
```

---

## 9. Resultado esperado de la anamnesis

La salida de la anamnesis no es una charla suelta.

Debe producir:

```text
- ficha inicial;
- taxonomía mínima;
- dolores declarados;
- hipótesis abiertas;
- evidencia requerida;
- preguntas pendientes;
- límite actual del análisis;
- próximo paso permitido.
```

---

## 10. Informe inicial

El primer informe debe incluir, cuando corresponda:

```text
- resumen de la anamnesis;
- dolores declarados por el dueño;
- documentación recibida;
- evidencia estructurada;
- hallazgos trazables;
- hipótesis no confirmadas;
- datos faltantes;
- riesgos visibles;
- próximos documentos sugeridos;
- próxima pregunta operativa recomendada.
```

No debe prometer certeza donde sólo hay indicios.

---

## 11. Prohibiciones

PymIA-Live no debe:

```text
- diagnosticar antes de encuadrar el organismo;
- tratar el Excel como ingreso conceptual único;
- confundir relato del dueño con evidencia validada;
- pedir documentación genérica sin relación con el dolor declarado;
- inferir dominio de forma prematura;
- abrir hipótesis sin taxonomía mínima;
- afirmar hallazgos sin evidencia suficiente;
- arrastrar dependencias externas del museo conversacional anterior.
```

---

## 12. Relación con el role playing

El role playing realizado no reemplaza esta arquitectura. La valida operacionalmente.

La secuencia observada fue:

```text
persona
→ empresa
→ actividad
→ contexto
→ preocupación principal
→ evidencia disponible
→ análisis
→ informe
→ nuevas preguntas
```

Esa secuencia confirma que la ficha/anamnesis/taxonomía debe preceder al análisis documental.

---

## 13. Fórmula operacional

```text
Primero se encuadra el organismo.
Después se escucha el dolor.
Luego se pide evidencia.
Después se mide.
Finalmente se devuelve claridad trazable.
```
