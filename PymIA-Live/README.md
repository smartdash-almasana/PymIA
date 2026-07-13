# PymIA-Live

Subárbol ejecutable transitorio de PymIA mientras se completa la consolidación física del repositorio.

## Autoridad

La autoridad documental única está en `../docs/current/README.md`. Este subárbol no contiene una biblioteca documental propia.

## Ejecución vigente

```powershell
cd PymIA-Live
python -m pytest tests/smartpyme tests/cli tests/e2e -q
python -m pymia.cli.service_1_product --help
```

La raíz productiva de Servicio 1 es `pymia/smartpyme/service_1_product_pipeline_v1.py`.
