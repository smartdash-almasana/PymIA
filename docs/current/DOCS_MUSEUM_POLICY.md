# Docs Museum Policy

Las siguientes documentaciones y recursos se consideran "Museo" (histórico):
- `docs/hermes`
- Registros de Telegram
- `conversa-engine`
- Pilotos viejos
- Prompts acumulados
- Matrices antiguas

## Reglas de Manejo del Museo

1. **No borrar**: La documentación histórica debe preservarse como antecedente de diseño y decisiones pasadas.
2. **No es fuente rectora**: Ninguno de estos recursos debe ser usado como fuente rectora de la arquitectura actual o la toma de decisiones, *salvo* que exista una cita explícita desde `docs/current` apuntando a ellos.
3. **Lectura de docs históricos sin deriva**: Al consultar cualquier archivo del museo, las IAs y los agentes no deben re-derivar el sistema ni cambiar la arquitectura, sino que deben usar la información estrictamente como contexto pasivo, validando cualquier suposición con las reglas actuales en `docs/current`.
