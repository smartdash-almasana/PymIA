# SaaS Autonomy Target

## Definición de Autonomía en PymIA

La transición hacia `S1_AUTONOMOUS_GUARDED_SAAS_V1` significa convertir gradualmente el sistema para que sea guiado por el dueño (owner-driven) y por evidencia (evidencia-driven), implementando gates y reingresos automáticos.

Para lograr esta autonomía, se deben cumplir las siguientes reglas:

1. **Avanzar solo con evidencia**: El sistema procesa y avanza de estado única y exclusivamente si cuenta con evidencia suficiente.
2. **Bloquear sin evidencia**: Si falta información o evidencia que sustente una decisión, el flujo debe bloquearse automáticamente.
3. **Preguntar al Dueño PyME**: Ante bloqueos o falta de contexto, el sistema (a través de la IA conversacional) debe preguntar directamente al Dueño PyME para solicitar la evidencia o el sentido operativo que falta.
4. **Liberar entrega automáticamente**: La entrega de valor se libera *solo* si se pasan exitosamente todos los gates definidos por la PymIA computacional.
5. **Operador como fallback**: El operador humano interviene únicamente como una vía de excepción (fallback), y no como un paso necesario en el proceso normal del SaaS.
