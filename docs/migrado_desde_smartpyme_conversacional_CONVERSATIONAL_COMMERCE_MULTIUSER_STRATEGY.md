# Documentación Migrada: CONVERSATIONAL_COMMERCE_MULTIUSER_STRATEGY.md

**Origen**: SmartPyme/docs/architecture/CONVERSATIONAL_COMMERCE_MULTIUSER_STRATEGY.md
**Destino**: PymIA/docs/migrado_desde_smartpyme/conversacional/CONVERSATIONAL_COMMERCE_MULTIUSER_STRATEGY.md
**Categoría**: conversacional
**Fecha migración**: 2026-05-18
**Prioridad**: alta
**Riesgo drift**: bajo

---

## Resumen 1 línea

Estrategia de comercio conversacional multiusuario: microservicios puntuales, bot como canal comercial, y soporte para múltiples roles dentro de un mismo tenant con trazabilidad auditable.

---

## Contenido preservado (extracto)

### Idea central

SmartPyme como plataforma conversacional que puede:
- vender y recibir demanda
- pedir evidencia y cobrar
- entregar microservicios y abrir diagnósticos
- registrar decisiones y operar sobre múltiples usuarios
- generar trazabilidad para el dueño

### Dos líneas de producto

1. **Microservicios puntuales**: soluciones concretas y rápidas (conciliación bancaria, cálculo de margen, plantillas, etc.)
2. **Sistema operativo organizacional**: flujo completo desde dolor hasta acción controlada con trazabilidad

### Bot como canal comercial

El bot puede operar como vendedor, recepcionista, mayéutico, cobrador y orquestador inicial, respetando límites éticos:
- no diagnosticar sin evidencia
- no ejecutar sin autorización
- registrar decisiones importantes

### Cliente multiusuario

Soporte para que un mismo tenant tenga múltiples usuarios con roles diferenciados:
- OWNER, ADMIN, MANAGER, ACCOUNTANT, PURCHASING, SALES, ECOMMERCE, IT, HR, OPERATIONS, VIEWER

### Trazabilidad

Cada interacción importante se registra con: cliente_id, user_id, role, timestamp, canal, decisión, job_id, case_id, resultado.

---

## Notas de migración

- Documento preservado sin reinterpretación
- Contenido original disponible en SmartPyme/docs/architecture/
- Clasificado como documentación conversacional por su enfoque en flujo de diálogo comercial
- No se migró código ni configuración asociada

---

## Referencias cruzadas

- Relacionado con: `PROTOCOLO_ANAMNESIS_MVP.md`
- Relacionado con: `PYME_OPERATIONAL_MODELS_SYMPTOMS_AND_CASES.md`
- Ver también: `PALANTIR_PRINCIPLES_FOR_SMARTPYME.md`
