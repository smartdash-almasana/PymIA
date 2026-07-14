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
