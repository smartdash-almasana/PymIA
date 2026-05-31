# PymIA

Repositorio limpio de producto para SmartPyme Laboratorio.

## Propósito

PymIA es la extracción limpia del núcleo clínico-operacional que funciona hoy:

```text
relato del dueño
→ anamnesis inicial
→ síntomas
→ hipótesis
→ evidencia requerida
→ respuesta sobria
```

No contiene factoría, jobs, MCP de desarrollo, runners legacy ni configuración histórica de Hermes.

## Regla arquitectónica

Hermes puede ser la interfaz conversacional elegida para hablar por Telegram con el dueño, con el modelo que se configure explícitamente. PymIA conserva la soberanía clínica del producto: Hermes no crea jobs por defecto ni decide diagnósticos fuera del kernel.

## Primer caso canónico

Entrada:

```text
RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY
```

Salida esperada:

```text
anamnesis inicial
hipótesis prioritaria
evidencia requerida
```

## Estructura

```text
PymIA/
  pymia/
    contracts/
    pipeline/
    services/
    cli/
  tests/
  docs/
```

## Demo local

```bash
cd PymIA
python -m pymia.cli.demo "RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY"
```

## Tests

```bash
cd PymIA
pytest -q
```
