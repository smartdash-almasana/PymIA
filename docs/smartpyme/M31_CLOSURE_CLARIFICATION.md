# M31 — Closure Clarification

## Estado

CLARIFICATION

## Motivo

Se detectó una discrepancia metodológica entre:

- `docs/roadmap/ROADMAP_SERVICIO_ASISTIDO_EXCEL_SEMANTICA_PYME.md`
- `docs/smartpyme/M31_SERVICIO_ASISTIDO_REPETIBLE_CHECKPOINT.md`

El roadmap define como evidencia de cierre operativo de M31:

```text
3 a 5 casos piloto documentados
+ tiempo real de entrega
+ bloqueos encontrados
+ aprendizajes
+ checklist estable
```

El checkpoint M31, en cambio, declaró PASS con evidencia documental:

```text
python -m pytest tests/smartpyme/test_m31_service_protocol_docs.py -q
4 passed in 0.21s
```

Esta aclaración evita convertir un cierre documental en cierre operativo real.

## Decisión

M31 queda dividido en dos niveles de cierre.

## 1. M31_DOCUMENTAL

### Estado

PASS_DOCUMENTAL

### Certifica

- Existe un protocolo escrito de servicio asistido repetible.
- Existe un test documental de conformidad.
- El protocolo no declara producto final.
- El protocolo no declara autonomía end-to-end.
- El protocolo no modifica código productivo.
- El protocolo define criterios de entrada, bloqueo, ejecución, registro y aprendizaje.

### No certifica

- pilotos reales ejecutados;
- tiempos reales medidos;
- bloqueos reales observados;
- aprendizajes reales derivados de casos;
- repetibilidad operacional comprobada con clientes o casos reales;
- producto mínimo;
- servicio comercial validado.

## 2. M31_OPERATIVO_PILOTOS

### Estado

PENDING_PILOTS

### Para certificarlo hace falta

- ejecutar o documentar 3 a 5 casos piloto;
- registrar tiempo real de entrega por caso;
- registrar costo operativo si corresponde;
- registrar evidencia recibida;
- registrar bloqueos reales;
- registrar aprendizajes candidatos, sin convertirlos automáticamente en LearningMemory;
- evaluar repetibilidad o no repetibilidad del protocolo.

## Regla de avance

No abrir M32 como feature hasta resolver explícitamente si el próximo ciclo será:

```text
M31-P — Pilotos asistidos reales
```

u otra fase metodológica equivalente.

## Restricciones

Este documento no autoriza:

- código productivo;
- Guided Evidence Recovery;
- integración ERP;
- UI;
- PDF profesional;
- autonomía end-to-end;
- naming de producto final;
- LearningMemory automática;
- apertura de M32 por inercia.

## Próximo paso metodológico

Crear una fase de pilotos asistidos reales, con cadena mínima:

```text
ADR
→ CapabilitySpec
→ ModuleContract, si corresponde
→ TaskSpec
→ validación documental / operativa
→ ejecución de pilotos
→ evidencia
→ checkpoint M31-P
```

## Relación con AGENTS.md

Esta aclaración refuerza la regla central del contrato de arranque:

```text
No declarar PASS sin evidencia suficiente para el tipo de cierre que se afirma.
```

Por lo tanto:

- M31 documental: PASS_DOCUMENTAL.
- M31 operativo con pilotos: PENDING_PILOTS.
- Producto: NO_CERTIFICADO.
