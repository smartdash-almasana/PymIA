# SMARTPYME_MEMORY_RUNTIME_SMOKE

## Estado

PASS local reportado.

## Frente

SMARTPYME_MEMORY_RUNTIME_SMOKE

## Propósito

Validar que `conversa-engine/main.py` consume la integración recall-before-reply con un cliente Supermemory inyectado, sin red real y preservando fail-open.

## Archivo de test

```text
tests/test_conversa_supermemory_recall_runtime.py
```

## Validación local

Comando ejecutado:

```powershell
cd E:\BuenosPasos\smartbridge\PymIA
python -m pytest tests/smartpyme/test_supermemory_tenant_recall.py tests/smartpyme/test_supermemory_recall_integration.py tests/test_conversa_supermemory_recall_runtime.py -q
```

Resultado reportado:

```text
tests\smartpyme\test_supermemory_tenant_recall.py ..........             [ 55%]
tests\smartpyme\test_supermemory_recall_integration.py ......            [ 88%]
tests\test_conversa_supermemory_recall_runtime.py ..                     [100%]

18 passed in 1.34s
```

## Qué valida

```text
- conversa-engine/main.py usa cliente Supermemory inyectado.
- recall se ejecuta antes de responder.
- el resumen se guarda tenant-scoped.
- si Supermemory falla, la conversación sigue.
- no hay llamadas reales de red.
```

## Límite

Este smoke no valida persistencia real en VM ni API Supermemory real. Valida integración runtime local con cliente fake.
