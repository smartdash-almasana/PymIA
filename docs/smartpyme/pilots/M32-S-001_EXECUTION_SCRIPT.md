# M32-S-001 — Manual Execution Script

## Estado

READY_FOR_MANUAL_EXECUTION

## Caso

Distribuidora Mayorista Don Roque

## Fixture

`prueba_excels/distribuidora_mayorista_compleja.xlsx`

## Rol del Operador

El usuario interpreta dueño PyME simulado.

## Comando para Iniciar Bot

```text
TELEGRAM_BOT_TOKEN=<token> python -m pymia.telegram_bot_runtime
```

## Guion Exacto de Turnos

### Turno 1

```text
Hola, tengo una distribuidora y no me cierra la caja.
```

### Turno 2

```text
Me llamo Roque Pérez. La empresa es Distribuidora Don Roque. Compramos productos de consumo masivo y revendemos a kioscos y almacenes. Somos 8 personas. Vendemos por vendedores propios y distribuidores.
```

### Turno 3

```text
No sé si gano plata. Entra y sale plata todo el tiempo y no sé cuánto gano por producto.
```

### Turno 4

Subir archivo:

```text
distribuidora_mayorista_compleja.xlsx
```

### Turno 5

```text
Analizá el Excel y decime qué se puede saber y qué falta.
```

### Turno 6

```text
Dame un resumen claro y próximos pasos.
```

## Registro Requerido por Turno

Para cada turno registrar:

- hora
- texto enviado
- respuesta literal del bot
- captura o log
- si pidió evidencia
- si diagnosticó o no
- si hubo bloqueo honesto

## Métricas

- `time_intake_minutes`
- `time_taxonomy_minutes`
- `time_evidence_minutes`
- `time_analysis_minutes`
- `time_report_minutes`
- `time_total_minutes`
- `bot_questions_asked`
- `bot_blockers_emitted`
- `files_received`
- `file_cached_path` si aparece en log

## Stop Conditions

- bot no inicia
- bot no responde
- bot no recibe archivo
- bot diagnostica sin evidencia
- bot inventa hallazgos
- se necesita tocar código
- se intenta declarar PASS M32

## Resultado Esperado

- `SIMULATED_CONTROLLED_INTERACTIVE`
- `counts_for_pass_m32 = false`

## Siguiente Archivo Después de Ejecutar

`docs/smartpyme/pilots/M32-S-001.md`
