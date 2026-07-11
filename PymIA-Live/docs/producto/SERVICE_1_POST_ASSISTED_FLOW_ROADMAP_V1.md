# SERVICE_1_POST_ASSISTED_FLOW_ROADMAP_V1

## VERDICT

ROADMAP_ACTIVO.

Servicio 1 ya tiene un flujo asistido cerrado y probado:

```text
XLSX -> preguntas -> ingestion_output -> semantica -> gate -> autorizacion -> validacion -> ejecucion controlada -> delivery
```

Tambien fue probado por navegador local via HTTP dev-only:

```text
frontend local -> POST /service-1/experiment/run -> backend boundary -> orquestador -> delivery
```

Este roadmap define como madurar Servicio 1 sin romper el flujo cerrado.

## BASELINE ACTUAL

Estado certificado:

```text
flujo asistido cerrado
orquestador end-to-end
endpoint HTTP dev-only
browser smoke PASS
delivery minimo real bajo autorizacion
```

Entrega actual:

```text
README.md
manifest.json
execution_result.json
hashes.json
```

Principio operativo:

```text
La IA conversa.
La FSM/gates gobiernan.
Las tools ejecutan.
Los archivos son el producto.
El duenio confirma.
```

## REGLA MADRE POST-CIERRE

No agregar arquitectura si no mejora una de estas cuatro cosas:

```text
1. experiencia del duenio
2. evidencia disponible
3. calidad del delivery
4. seguridad fail-closed
```

Si no mejora una de esas, no entra.

## FASE 1 - ESTABILIZACION DEL FLUJO CERRADO

Objetivo: que lo ya logrado no se rompa.

Acciones:

```text
1. Mantener congelados los 13 eslabones + orquestador + HTTP boundary.
2. Conservar smoke browser como evidencia.
3. Crear comando/smoke repetible para CASE_001.
4. No tocar orquestador salvo bug real.
```

Resultado esperado:

```text
CASE_001 siempre genera delivery autorizado.
```

## FASE 2 - UX HUMANA MINIMA

Objetivo: dejar de usar payload JSON manual.

Acciones:

```text
1. Frontend pregunta columnas una por una.
2. Frontend pregunta ambiguedades semanticas una por una.
3. Botones: aceptar plan / rechazar / pedir cambios.
4. Mostrar trace simple.
5. Mostrar links o paths del delivery.
```

Regla:

```text
La web no decide.
La web solo conversa y manda respuestas al backend.
```

Slice recomendado:

```text
SERVICE_1_WEB_OWNER_DIALOGUE_FRONTEND_V1
```

## FASE 3 - DELIVERY ENTENDIBLE PARA DUENIO PYME

Objetivo: que la carpeta final sea comprensible sin leer codigo.

Acciones:

```text
1. Mejorar README.md.
2. Agregar resumen ejecutivo PyME.
3. Separar: confirmado / ejecutado / faltante / recomendado.
4. Mantener manifest y hashes como control tecnico.
```

Resultado esperado:

```text
El duenio abre la carpeta y entiende que paso.
```

## FASE 4 - ANALISIS REAL MAS RICO

Objetivo: aumentar valor operacional sin inventar diagnosticos.

Prioridad:

```text
1. margen
2. precio/costo
3. ventas/cobranzas
4. stock basico
5. compras/proveedores
```

Regla:

```text
Si falta evidencia, pregunta o bloquea.
No inventa.
```

## FASE 5 - CASOS SINTETICOS REALES

Objetivo: madurar con variedad.

Casos sugeridos:

```text
CASE_001 ventas/margen
CASE_002 cobranzas
CASE_003 stock
CASE_004 compras/proveedores
CASE_005 caja/banco simple
```

Cada caso debe tener:

```text
input XLSX
respuestas del duenio
delivery esperado
smoke e2e
gaps detectados
```

## FASE 6 - LIMPIEZA DE DEUDA

Objetivo: que la suite no confunda.

Acciones:

```text
1. Resolver exceland_factory/specs env.
2. Confirmar suite S1 sin los 11 fallos env.
3. Separar legacy de activo.
4. Marcar obsoletos sin tocar el flujo cerrado.
```

## FASE 7 - EMPAQUE OPERATIVO

Objetivo: que se pueda correr sin asistencia tecnica constante.

Acciones:

```text
1. Comando unico local.
2. Instrucciones cortas.
3. Carpeta clara de input/output.
4. Web local simple.
5. Logs entendibles.
```

## FASE 8 - WEB REAL / SAAS

Objetivo: producto web real, recien despues del uso local estable.

Acciones:

```text
1. auth real
2. persistencia de casos
3. subida segura
4. historial de deliveries
5. multiusuario
6. UI madura
```

No hacer antes:

```text
no SaaS prematuro
no auth improvisado
no DB antes de estabilizar experiencia humana
```

## ORDEN RECOMENDADO

```text
1. UX humana minima
2. delivery entendible
3. tres casos sinteticos reales
4. formulas/patologias utiles
5. limpieza suite env
6. empaque operativo
7. SaaS
```

## PROXIMO SLICE

```text
SERVICE_1_WEB_OWNER_DIALOGUE_FRONTEND_V1
```

Objetivo:

```text
Reemplazar payload JSON manual por preguntas guiadas en la web,
sin cambiar backend, orquestador ni autoridad del flujo.
```

## NO TOCAR

```text
13 piezas cerradas del flujo asistido
orquestador salvo bug real
backend boundary salvo transporte
reader canonico XLSX
contratos fail-closed
```

## CIERRE

Servicio 1 ya no necesita mas micro-slices de arquitectura para demostrar que existe.
Ahora debe madurar por experiencia humana, casos reales sinteticos, delivery util y evidencia.
