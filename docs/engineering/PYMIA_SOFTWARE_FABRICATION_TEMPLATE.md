# PYMIA_SOFTWARE_FABRICATION_TEMPLATE

## Estado

PLANTILLA OPERATIVA

---

# Propósito

Esta plantilla fija el método de fabricación de software para PymIA.

Su objetivo es convertir intuición, criterio técnico y dirección doctrinal en unidades fabricables, testeables y auditables.

La regla central es:

```text
La vibra puede descubrir.
No puede decidir sola.
```

Toda idea debe atravesar una cadena de fabricación verificable antes de ingresar al sistema.

---

# Principio de fabricación

PymIA no debe crecer por acumulación de partes.

Debe crecer por incorporación de comportamientos verificables que fortalezcan su comportamiento como un uno.

Cada avance debe responder:

```text
¿Esto fortalece acoplamiento significativo, retroalimentación, continuidad o coherencia?
```

Si no fortalece ninguno de esos fundamentos, no debe entrar.

---

# Cadena de fabricación

Todo avance debe atravesar esta secuencia:

```text
Intuición
→ Principio
→ Pregunta de auditoría
→ Comportamiento observable
→ Test
→ Código mínimo
→ Integración
→ CI / pytest
→ Checkpoint
→ Nueva memoria del sistema
```

---

# Unidad mínima de fabricación

Cada hito debe tener:

```text
1 hito
1 hueco real
1 comportamiento observable
1 test principal
1 PR chico
1 checkpoint
```

Si falta alguno de estos elementos, el trabajo se considera incompleto.

---

# Antipatrón Frankenstein

Frankenstein aparece cuando se fabrica así:

```text
idea
→ código
→ más código
→ parche
→ explicación posterior
```

Ese flujo está prohibido para PymIA.

Producto sano aparece así:

```text
idea
→ principio
→ test de comportamiento
→ código mínimo
→ integración
→ evidencia
→ checkpoint
```

---

# Plantilla de hito

Todo hito debe poder expresarse con este formato.

## HITO

```text
MXX_NOMBRE_DEL_HITO
```

## HUECO

Describir qué falta y dónde fue detectado.

Debe referenciar uno o más de:

- auditoría previa;
- test ausente;
- checkpoint;
- fallo reproducible;
- inconsistencia documental;
- gap de comportamiento de unidad.

## PRINCIPIO QUE FORTALECE

Elegir uno o más:

```text
Acoplamiento significativo
Retroalimentación
Continuidad
Coherencia
```

## COMPORTAMIENTO OBSERVABLE

Describir qué debe ocurrir de punta a punta.

Debe ser verificable por test, smoke, fixture, CI o reporte.

Ejemplo:

```text
tenant_a habla
→ se persiste estado
→ tenant_a vuelve
→ el contexto evoluciona
→ tenant_b no hereda contexto de tenant_a
```

## ARCHIVOS A LEER

Lista cerrada de archivos que el agente debe leer antes de modificar.

## ARCHIVOS QUE PUEDE TOCAR

Lista cerrada de archivos permitidos.

Si no hay lista explícita, no se debe modificar nada.

## PROHIBIDO

Lista explícita de fronteras.

Ejemplo:

```text
No tocar CI.
No tocar registry.
No tocar dispatcher.
No tocar plugins.
No tocar Telegram/PDF/HTML/UI.
No agregar LLM.
No agregar red.
No crear capability nueva.
```

## TEST PRINCIPAL

Nombre o ubicación esperada del test principal.

Ejemplo:

```text
tests/orchestration/test_tenant_continuity_acceptance.py
```

## VALIDACIÓN

Comandos exactos a ejecutar.

Ejemplo:

```text
python -m pytest tests/orchestration/test_tenant_continuity_acceptance.py -q
python -m pytest tests/orchestration -q
python -m pytest tests/smartpyme -q
```

## SALIDA ESPERADA DEL AGENTE

El agente debe responder con:

```text
1. VEREDICTO
   PASS / PARTIAL / BLOCKED

2. ARCHIVOS MODIFICADOS

3. TESTS EJECUTADOS

4. RESULTADOS EXACTOS

5. JUSTIFICACIÓN DE SCOPE

6. RIESGO RESIDUAL

7. PRÓXIMO PASO RECOMENDADO
```

---

# Definición de veredictos

## PASS

El hito cerró el hueco declarado con evidencia reproducible.

## PARTIAL

El hito avanzó parcialmente pero dejó un hueco explícito.

Debe declarar riesgo residual.

## BLOCKED

El hito no puede ejecutarse sin violar scope o requiere decisión previa.

Debe declarar causa exacta.

---

# Regla de PR

Cada PR debe ser chico y auditable.

Debe contener una de estas categorías:

```text
test-only
docs-only
code-minimal
checkpoint
```

No mezclar categorías salvo justificación explícita.

---

# Regla de checkpoint

Todo avance significativo debe cerrar con checkpoint.

El checkpoint debe documentar:

- qué cambió;
- qué prueba;
- qué no prueba;
- qué límites preserva;
- qué riesgo residual queda;
- qué próximo frente recomienda.

Sin checkpoint, el sistema pierde memoria evolutiva.

---

# Relación con PymIA Unity Principles

Esta plantilla operacionaliza los fundamentos de comportamiento de unidad:

```text
Acoplamiento significativo
Retroalimentación
Continuidad
Coherencia
```

No reemplaza auditorías genéticas.

Las complementa.

Las capacidades individuales siguen siendo necesarias, pero cada una debe demostrar que participa del comportamiento de unidad.

---

# Criterio final

La pregunta para aceptar software en PymIA no es solamente:

```text
¿Anda?
```

La pregunta correcta es:

```text
¿Anda como parte del uno?
```
