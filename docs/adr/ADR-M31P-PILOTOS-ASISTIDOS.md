# ADR-M31P — Pilotos asistidos reales antes de M32

## Estado

ACCEPTED

## Fecha

2026-06-05

## Contexto

M31 fue aclarado en dos niveles:

```text
M31_DOCUMENTAL = PASS_DOCUMENTAL
M31_OPERATIVO_PILOTOS = PENDING_PILOTS
```

La discrepancia detectada fue que el roadmap exigía 3 a 5 casos piloto documentados para certificar cierre operativo, mientras que el checkpoint M31 declaró PASS con evidencia documental.

Para evitar deriva metodológica, no corresponde abrir M32 como si M31 operativo estuviera certificado.

PymIA / SmartPyme debe validar primero si el protocolo M31 puede repetirse en condiciones asistidas con casos reales o realistas.

## Decisión

Antes de abrir M32, se abre una fase intermedia:

```text
M31-P — Pilotos asistidos reales
```

M31-P es una fase de validación operativa asistida, no una feature técnica.

Su objetivo es ejecutar o documentar 3 a 5 pilotos usando el protocolo M31 y registrar:

- intake del dueño PyME;
- evidencia aportada;
- evidencia faltante;
- salida entregada o bloqueo;
- tiempo real de ejecución;
- intervención humana requerida;
- bloqueos encontrados;
- aprendizajes candidatos;
- evaluación de repetibilidad.

## Alcance autorizado por este ADR

Este ADR autoriza documentación y preparación operativa de M31-P:

- CapabilitySpec de M31-P;
- TaskSpec de M31-P;
- plantilla de registro de piloto;
- checkpoint futuro M31-P;
- validación documental de la fase.

## Alcance no autorizado

Este ADR no autoriza:

- código productivo;
- M32;
- Guided Evidence Recovery;
- integración ERP;
- UI;
- PDF profesional;
- dispatcher;
- registry;
- runtime;
- automatización comercial;
- declarar producto;
- declarar autonomía end-to-end;
- LearningMemory automática.

## Alternativas consideradas

### Alternativa A — Abrir M32 directamente

Rechazada.

Motivo: abrir M32 sin pilotos reales convertiría un PASS documental en certificación operativa no demostrada.

### Alternativa B — Reescribir el roadmap para bajar el criterio M31

Rechazada.

Motivo: eliminar el requisito de pilotos reales ocultaría una diferencia válida entre protocolo escrito y repetibilidad operacional comprobada.

### Alternativa C — Marcar M31 como fallido

Rechazada.

Motivo: M31 sí cerró documentalmente el protocolo. Lo incorrecto sería confundir ese cierre con validación operativa.

### Alternativa D — Dividir M31 en cierre documental y cierre operativo

Aceptada.

Motivo: preserva la evidencia real, evita sobrediagnóstico metodológico y habilita una fase clara de pilotos.

## Consecuencias

- M31_DOCUMENTAL permanece como PASS_DOCUMENTAL.
- M31_OPERATIVO_PILOTOS permanece como PENDING_PILOTS.
- M31-P debe completarse antes de considerar M32.
- El roadmap no se invalida: se precisa su criterio de cierre operativo.
- Los nuevos documentos deben hablar de servicio asistido, protocolo o pilotos, no producto.
- Todo aprendizaje derivado de pilotos debe registrarse como candidato, no LearningMemory automática.

## Criterio de cierre de M31-P

M31-P podrá cerrar como PASS_OPERATIVO sólo si existen:

- 3 a 5 registros de pilotos;
- tiempos reales registrados;
- evidencia recibida y faltante;
- salidas o bloqueos documentados;
- evaluación de repetibilidad;
- checkpoint M31-P.

Si hay menos de 3 pilotos o evidencia incompleta, M31-P deberá cerrar como PARTIAL o BLOCKED según corresponda.

## Relación con AGENTS.md

Este ADR aplica la regla:

```text
No declarar PASS sin evidencia suficiente para el tipo de cierre afirmado.
```

La evidencia documental alcanza para PASS_DOCUMENTAL.

No alcanza para PASS_OPERATIVO.

## Próximo paso

Crear:

```text
docs/smartpyme/M31P_CAPABILITY_SPEC.md
docs/smartpyme/M31P_TASK_SPEC.md
```

Ambos deben mantener el ciclo dentro de documentación y validación operativa, sin código productivo.
