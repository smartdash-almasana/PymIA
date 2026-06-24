# SERVICE_1_XLSX_OWNER_CHAT_BROWSER_V1

## Estado

```text
IMPLEMENTED_CANDIDATE
```

## Propósito

Crear una página de prueba para Servicio 1 siguiendo la pauta operacional:

```text
Excel entra
PymIA lee estructura real
PymIA pregunta
el dueño responde
se exporta el intercambio
```

No es marketing.
No es landing comercial.
No es simulación de análisis.
No emite diagnóstico.
No cierra conciliación ni resultado contable.

## Archivo implementado

```text
landing/build_service1_xlsx_owner_chat_html.py
```

El generador produce:

```text
landing/servicio1-xlsx-owner-chat.html
```

Comando:

```powershell
python landing/build_service1_xlsx_owner_chat_html.py
```

## Por qué generador y no HTML directo

La herramienta MCP bloquea escritura directa de `.html`.

Por eso se versiona un generador Python determinístico que escribe el HTML localmente.

## Flujo real de la página

```text
1. Dueño/operador confirma condiciones.
2. Carga XLSX/XLS/CSV.
3. SheetJS lee el archivo localmente en navegador.
4. PymIA arma un perfil estructural real:
   - nombre de archivo
   - tamaño
   - hojas
   - filas con contenido
   - cantidad de columnas
   - fila probable de encabezado
   - encabezados visibles
   - señales por nombres de hoja/columna
5. PymIA genera preguntas desde esa estructura.
6. El dueño responde en el chat derecho.
7. El sistema avanza pregunta por pregunta.
8. Se exporta TXT con perfil + respuestas + límites.
```

## Diferencia contra la demo anterior

La versión anterior tenía preguntas fijas y servía como sandbox visual.

Esta versión cambia el eje:

```text
No genera números falsos.
No dice registros procesados.
No dice total facturado.
No simula lectura.
No llama a /api/curate.
```

Las preguntas salen de:

```text
workbook.SheetNames
rows reales leídas por SheetJS
headers detectados
nombres de hoja
nombres de columnas
señales por palabras como ventas, cobranzas, banco, stock, costo, precio
```

## Preguntas generadas

Preguntas base:

```text
Qué representa este archivo.
Qué período cubre.
Cuál es la hoja principal.
Qué contiene cada hoja.
Qué columnas son las más importantes.
Si el foco detectado por nombres es correcto.
Qué se quiere revisar primero.
Qué columnas o valores generan duda.
Qué otro archivo debería mirarse junto con éste.
```

## Export TXT

El export comienza con:

```text
PYMIA_SERVICE_1_XLSX_OWNER_CHAT_V1
```

Incluye:

```text
created_at
runtime_authorized: false
production_allowed: false
final_diagnosis: false
final_accounting_result: false
human_review_required: true
FILE_PROFILE
ANSWERS
LIMITS
```

## Límites explícitos

```text
No backend.
No API.
No OCR.
No Mercado Pago.
No Servicio 2.
No diagnóstico final.
No conciliación final.
No resultado contable final.
```

## Qué madura realmente

Este slice empieza a corregir el problema de fondo detectado:

```text
Mucho perímetro, poco flujo.
```

Ahora aparece el circuito mínimo vivo:

```text
archivo -> lectura estructural -> preguntas -> respuestas -> transcript
```

Esto debe volverse el centro de Servicio 1 antes de seguir agregando registries o matrices.

## Tests

```text
tests/test_service1_xlsx_owner_chat_landing_generator.py
```

Verifica:

```text
- flujo basado en estructura real del XLSX
- chat derecho pregunta/respuesta
- SheetJS en navegador
- preview + tabs
- export TXT
- ausencia de métricas falsas
- ausencia de backend/API
- ausencia de claims finales
```

## Próximo ajuste recomendado

```text
SERVICE_1_XLSX_OWNER_CHAT_CASE_BINDING_V1
```

Propósito:

```text
Convertir el TXT exportado en un contrato de caso consumible por PymIA-Live.
```

Eso permitiría continuar el flujo:

```text
owner_chat_export.txt -> case intake -> service_1 route/run spec -> review checklist
```
