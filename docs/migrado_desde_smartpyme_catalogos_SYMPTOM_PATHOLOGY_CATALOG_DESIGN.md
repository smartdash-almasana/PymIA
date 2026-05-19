# Documentación Migrada: SYMPTOM_PATHOLOGY_CATALOG_DESIGN.md

**Origen**: SmartPyme/docs/architecture/SYMPTOM_PATHOLOGY_CATALOG_DESIGN.md
**Destino**: PymIA/docs/migrado_desde_smartpyme/catalogos/SYMPTOM_PATHOLOGY_CATALOG_DESIGN.md
**Categoría**: catalogos
**Fecha migración**: 2026-05-18
**Prioridad**: alta
**Riesgo drift**: medio

---

## Resumen 1 línea

Diseño conceptual del catálogo clínico-operativo PyME: traducción de dolor del dueño a síntoma, patologías posibles, hipótesis investigable, skills candidatas y evidencia requerida.

---

## Contenido preservado (extracto)

### Función del catálogo

Traducir:
```
dolor del dueño
→ síntoma operativo
→ patologías posibles
→ hipótesis investigable
→ skill candidata
→ variables necesarias
→ evidencia requerida
→ preguntas mayéuticas
```

### Regla central

> El sistema no pide datos porque sí. Pide datos porque una hipótesis necesita variables y evidencia para ser verificada.

### Relación con métodos

- **Mayéutica (externa)**: ayuda al dueño a formular
- **Hipotético-deductivo (interno)**: ayuda al sistema a verificar

### Estructura conceptual de entrada

```
symptom_id
nombre
dolores_asociados
sintoma_operativo
patologias_posibles
hipotesis_template
skills_candidatas
variables_necesarias
evidencia_requerida
preguntas_mayeuticas
criterios_para_avanzar
criterios_de_bloqueo
notas_semanticas
```

### Definiciones clave

**Dolor del dueño**: Formulación humana inicial, imprecisa. Ej: "Estoy perdiendo plata."

**Síntoma operativo**: Traducción del dolor a señal investigable. Ej: `sospecha_perdida_margen`

**Patología PyME**: Patrón recurrente de daño/fricción. Ej: `desalineacion_costo_precio`

**Hipótesis investigable**: Formulación verificable, no afirmativa. Ej: "Investigar si existe pérdida de margen por desalineación entre costos reales y precios de venta durante {periodo}."

**Skill candidata**: Capacidad técnica que puede investigar esa hipótesis. Ej: `skill_margin_leak_audit`

**Variables necesarias**: Datos escalares mínimos para verificar la hipótesis.

**Evidencia requerida**: Fuentes o documentos necesarios para contrastar.

### Ejemplo: sospecha de pérdida de margen

```yaml
symptom_id: sospecha_perdida_margen
dolores_asociados:
  - "pierdo plata"
  - "vendo pero no gano"
  - "no me deja margen"
patologias_posibles:
  - desalineacion_costo_precio
  - costo_reposicion_desactualizado
  - descuentos_no_controlados
hipotesis_template: "Investigar si existe pérdida de margen por desalineación entre costos reales y precios de venta durante {periodo}."
skills_candidatas:
  - skill_margin_leak_audit
variables_necesarias:
  - periodo
  - productos_o_familias
  - margen_esperado
  - precio_venta_real
  - costo_reposicion
evidencia_requerida:
  - ventas_pos
  - excel_ventas
  - facturas_proveedor
  - lista_costos
```

---

## Notas de migración

- Documento preservado sin reinterpretación
- Contenido original disponible en SmartPyme/docs/architecture/
- Clasificado como catálogo por su función de mapeo semántico entre síntomas y patologías
- No se migró código ni configuración asociada
- Posible drift: terminología `findings` vs `hallazgos` requiere resolución posterior

---

## Referencias cruzadas

- Relacionado con: `PYME_SYMPTOM_PATHOLOGY_ATLAS.md`
- Relacionado con: `PYME_OPERATIONAL_MODELS_SYMPTOMS_AND_CASES.md`
- Relacionado con: `HYPOTHETICO_DEDUCTIVE_METHOD.md`
- Ver también: `atlas-sintomas-patologias.md` en PymIA/docs/catalogo/
