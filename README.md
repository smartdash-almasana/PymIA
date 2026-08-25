# PymIA

Repositorio canónico del núcleo operativo de PymIA.

```text
pymia/   paquete productivo único
tests/   suite canónica
tools/   ingesta y utilidades gobernadas
docs/    autoridad documental única
```

Validación principal:

```powershell
python -m pytest -q
```

La integración `exceland_factory` es externa y opcional. No es dependencia de la raíz canónica. Su smoke se ejecuta únicamente cuando existe una versión gobernada instalada:

```powershell
python -m pytest tests_optional/exceland -q
```


## Servicio 1 — handoff de implementación

La arquitectura objetivo de Servicio 1 está cerrada. Un agente que retome la implementación debe comenzar por:

```text
docs/current/SERVICE_1_IMPLEMENTATION_HANDOFF_V1.md
```

Ese documento define orden de lectura, arquitectura inmutable, delta código→target, plan de reconstrucción y contrato de finalización. No reabrir decisiones arquitectónicas ni usar documentación histórica como autoridad de runtime.
