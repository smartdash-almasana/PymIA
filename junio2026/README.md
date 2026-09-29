# Auditoría PymIA — junio2026

Carpeta de conclusiones auditadas para subir al repositorio GitHub.

## Estado de esta carpeta

Estos documentos no implementan código. Son una capa de saneamiento documental y decisión arquitectónica para orientar el próximo trabajo del repo.

## Decisión rectora incorporada

**Hermes debe desaparecer de PymIA.**

Hermes no será agente LLM, runtime, orchestrator, gateway activo, marca interna de conversación ni entidad arquitectónica. Toda referencia a Hermes debe ser tratada como legacy/deuda documental o técnica a eliminar, renombrar, aislar o mover a museo histórico.

## Documentos incluidos

1. [`00_RESUMEN_EJECUTIVO.md`](00_RESUMEN_EJECUTIVO.md)  
   Síntesis auditada del estado del proyecto.

2. [`01_DECISION_RETIRO_HERMES.md`](01_DECISION_RETIRO_HERMES.md)  
   Decisión explícita de retiro total de Hermes y criterios de limpieza.

3. [`02_MAPA_OPERATIVO_PYMIA.md`](02_MAPA_OPERATIVO_PYMIA.md)  
   Modelo operativo vigente para leer PymIA sin arrastrar legacy.

4. [`03_MVP_SERVICIO_1_ASISTIDO.md`](03_MVP_SERVICIO_1_ASISTIDO.md)  
   Recorte recomendado para validar el primer servicio real.

5. [`04_DEUDA_TECNICA_Y_RIESGOS.md`](04_DEUDA_TECNICA_Y_RIESGOS.md)  
   Riesgos técnicos/documentales/producto detectados.

6. [`05_PLAN_LIMPIEZA_REPO.md`](05_PLAN_LIMPIEZA_REPO.md)  
   Plan de saneamiento documental/técnico para futuras tareas.

7. [`MANIFEST.md`](MANIFEST.md)  
   Alcance, limitaciones y evidencia usada.

## Uso recomendado

- Subir esta carpeta como `junio2026/` en la raíz del repo.
- No mezclar estos documentos con código productivo.
- Usar estos documentos como base para issues/PRs de saneamiento.
- No tratar esta carpeta como cierre definitivo del producto: es un checkpoint de auditoría.
