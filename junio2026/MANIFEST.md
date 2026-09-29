# Manifest — auditoría junio2026

## Propósito

Esta carpeta registra conclusiones de auditoría para orientar el saneamiento de PymIA antes de avanzar en nuevas capacidades.

## Alcance

Auditoría realizada sobre el repo PymIA comprimido y sobre la auditoría Markdown pegada en la conversación.

## Limitación importante

La extracción local del `.rar` presentó archivos vacíos/fallidos. Se detectaron 166 archivos vacíos en el árbol extraído.

Por eso, estos documentos deben tratarse como auditoría de orientación y no como dictamen final sobre cada archivo individual.

Antes de aplicar cambios masivos, verificar contra el repo Git original.

## Evidencia generada

Se incluyeron logs en `evidencia/`:

- `repo_metrics.txt`
- `hermes_top_refs.txt`
- `pytest_root_selective.log`
- `pytest_pymia_live_selective.log`
- `zero_files_sample.txt`

## Decisión incorporada por dueño del proyecto

```text
Todo lo referente a Hermes debe desaparecer.
Hermes no va a ser empleado como agente LLM.
```

Esta decisión domina sobre documentos anteriores que activen Hermes.

## Uso sugerido en GitHub

Subir como carpeta:

```text
junio2026/
```

Luego abrir issues separados:

1. Retiro documental de Hermes.
2. Retiro técnico de Hermes.
3. Smoke suite viva.
4. Corrección de imports `PymIA-Live`.
5. Scope único de Servicio 1 asistido.
6. Plan de primer caso real.
