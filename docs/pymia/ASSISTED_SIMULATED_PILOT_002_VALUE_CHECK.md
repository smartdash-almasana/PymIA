# ASSISTED_SIMULATED_PILOT_002_VALUE_CHECK

Fecha: 2026-06-10
Estado: READY_TO_RUN
Tipo: simulación asistida orientada a valor

## 1. Objetivo

Ejecutar una segunda simulación controlada para medir si SmartPyme produce claridad operativa útil, no sólo bloqueo correcto.

La pregunta central es:

```text
¿Con evidencia suficiente, el flujo genera un informe que una PyME pueda entender y usar?
```

## 2. Alcance

Flujo a ensayar:

```text
F1 primer contacto
→ ficha inicial
→ evidencia suficiente o casi suficiente
→ OwnerFacingReport
→ owner_questions_bundle si falta algo
→ respuesta del dueño si aplica
→ reporte actualizado
```

## 3. Restricciones

Esta simulación NO autoriza:

- Telegram;
- Hermes;
- ERP;
- PDF productivo;
- runtime externo;
- nuevas fórmulas;
- nuevos reportes;
- cambios en DiagnosticCore;
- refactor amplio;
- cierre de TD-004.

TD-004 sólo se cierra con caso real.

## 4. Caso sugerido

Usar el caso textil ya conocido, pero esta vez orientado a valor:

```text
La Textil Cosida SRL
```

Evidencia sugerida:

```text
prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx
```

## 5. Qué medir

Registrar:

```text
findings_count
calidad de findings
claridad del OwnerFacingReport
preguntas generadas
faltantes estructurales
respuestas del dueño necesarias
tiempo operativo humano estimado
si el informe sería entregable a una PyME
```

## 6. Criterios PASS

La simulación pasa si:

- aparecen hallazgos útiles o, si no aparecen, el sistema explica claramente por qué;
- el reporte es entendible para dueño PyME;
- las preguntas no exponen claves técnicas;
- los faltantes estructurales están clasificados;
- no se inventa causalidad;
- no se promueve narrativa a evidencia dura;
- el resultado permite estimar si el servicio es vendible asistidamente.

## 7. Criterios FAIL

La simulación falla si:

- el reporte no aporta claridad;
- el dueño recibiría texto técnico crudo;
- se inventa evidencia o causalidad;
- el sistema queda bloqueado sin explicar qué falta;
- no se puede estimar valor operativo.

## 8. Resultado esperado

Crear checkpoint al finalizar:

```text
docs/pymia/ASSISTED_SIMULATED_PILOT_002_VALUE_CHECKPOINT.md
```

Salida esperada:

```text
VEREDICTO: PASS / PARTIAL / BLOCKED
EVIDENCIA USADA
RESULTADO OPERATIVO
FINDINGS
PREGUNTAS AL DUEÑO
FRICCIONES
ESTIMACIÓN DE ENTREGABILIDAD
NO PUSH
```
