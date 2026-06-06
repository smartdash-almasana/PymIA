# M32-S — Simulación Controlada Interactiva por Telegram

## Estado

PLAN_OPERATIVO_SIMULADO_INTERACTIVO

## Naturaleza

- `case_type = simulated_controlled_interactive`
- `counts_for_pass_m32 = false`
- no producto
- no cliente real
- no autonomía

## Caso Inicial

- `M32-S-001 — Distribuidora Mayorista Don Roque`

## Taxonomía

- distribuidora mayorista
- compra y reventa
- productos de consumo masivo
- maneja stock
- 8 personas
- vende a kioscos/almacenes por vendedores y distribuidores

## Problema Simulado

```text
No me cierra la caja. Entra y sale plata, pero no sé cuánto gano por producto.
```

## Fixture

- `prueba_excels/distribuidora_mayorista_compleja.xlsx`

## Flujo Telegram Esperado

1. Turno 1: problema inicial
2. Turno 2: taxonomía/contexto
3. Turno 3: problema de rentabilidad/caja
4. Turno 4: subir Excel
5. Turno 5: pedir análisis
6. Turno 6: pedir resumen o próximos pasos

## Requisitos Mínimos Telegram

- recibir mensaje
- responder con sentinel/runtime
- recibir archivo
- cachear archivo
- no diagnosticar sin evidencia
- registrar si persiste o no contexto
- registrar si FSM real está conectada o no

## GAP Conocido

- `GAP-M32S-001`
- `telegram_bot_runtime.py` usa `telegram_runtime.handle_telegram_message`
- runtime simple por keywords
- no está probado que use `anamnesis_fsm.process_message`
- la simulación debe registrar este gap, no resolverlo

## Evidencia Válida

- capturas de Telegram
- logs del bot
- nombre del archivo recibido
- respuestas literales del bot
- tiempos medidos
- bloqueos del bot
- hallazgos efectivamente emitidos por el bot

## Evidencia Inválida

- hallazgos inventados manualmente
- respuestas editadas
- tiempos estimados
- diagnóstico no emitido por el bot

## Stop Conditions

- bot no recibe mensajes
- bot no recibe archivo
- bot diagnostica sin evidencia
- bot inventa hallazgos
- se requiere tocar código productivo
- se intenta declarar PASS M32

## Registro Posterior

- `docs/smartpyme/pilots/M32-S-001.md`
- sólo después de ejecutar la simulación
