# Servicio 1 — estado actual

**Fecha de corte:** 2026-07-13

**Commit certificado:** `cfea59f`

**Regresión certificada:** `2857 passed, 1 skipped`

## Estado

```text
RAÍZ PRODUCTIVA CANÓNICA: ACTIVA
CLI CANÓNICO: ACTIVO
XLSX REAL → COMPRENSIÓN → CONFIRMACIÓN → TOOL → XLSX: PROBADO
FAIL-CLOSED SEMÁNTICO: PROBADO
SERVICIO 1 COMPLETO EN TODA SU AMPLITUD: NO
CONSOLIDACIÓN FÍSICA DEL REPOSITORIO: CERRADA
```

## Qué hace hoy

Servicio 1 puede:

- leer un XLSX real por la ruta canónica;
- conservar encabezados, muestras y contexto de hoja;
- proponer significados semánticos mediante el motor de comprensión de columnas;
- avanzar sin preguntar cuando la evidencia es suficiente;
- bloquear y preguntar al dueño cuando existe ambigüedad;
- aceptar únicamente una opción semántica canónica o `IGNORED_NOT_RELEVANT`;
- impedir que texto libre convierta `unknown` en una confirmación ficticia;
- ejecutar una tool explícitamente solicitada y permitida;
- generar un XLSX físico de salida.

## Recorrido actual

```text
Excel
→ lectura estructural
→ comprensión de columnas
→ pregunta al dueño, solo cuando hace falta
→ vínculo semántico confirmado
→ gate de seguridad
→ ejecución determinística explícita
→ archivo de entrega
```

## Raíz técnica

```text
pymia/smartpyme/service_1_product_pipeline_v1.py
pymia/cli/service_1_product.py
```

El motor de comprensión está integrado en la raíz mediante:

```text
service_1_canonical_ingestion_output_to_semantic_bridge_v1.py
service_1_column_understanding_engine_v1.py
```

## Límites honestos

- Las tools todavía se solicitan explícitamente; el caso probado no demuestra selección automática de tool desde el contenido del Excel.
- El universo completo de patologías, fórmulas y microservicios todavía no está conectado a la raíz productiva.
- No hay LLM con autoridad de decisión dentro del pipeline.
- No hay autorización para una cadena paralela, un segundo parser XLSX ni una arquitectura SaaS alternativa.
- La raíz física ya está consolidada; permanecen deuda de integración funcional y documentación no rectora por depurar.

## Próximo frente

```text
ENDURECIMIENTO_P0_POST_CONSOLIDACION
→ CI reproducible y build limpio
→ dependencias externas fail-closed
→ eliminar módulos obsoletos con prueba de callers
→ conectar capacidades solo a la raíz productiva
```
