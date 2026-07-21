# Servicio 1 — CYCLE_045A DPO prerequisite brief

**Estado:** DECIDED

## Decisión

`PYME_013` no puede conectarse todavía como primera capacidad `COMPOSITE` porque el repositorio sólo dispone de un resultado gobernado para `dso`. No existe aún una capacidad productiva `dpo` en el Generic Capability Kernel.

## Secuencia obligatoria

1. Implementar `dpo` como capacidad `ATOMIC` gobernada.
2. Fórmula canónica: `(accounts_payable / purchases) * days`.
3. Variables mínimas: `accounts_payable`, `purchases`, `days`.
4. Dominio: valores finitos y no negativos; `purchases > 0`; `days > 0` y consistente.
5. Resultado tipado: unidad `days`, período derivado de `days`.
6. Clasificación acotada respecto del período.
7. Sin entrega XLSX, sin diagnóstico causal, sin selección automática.
8. Integrar `dpo` en la raíz única mediante solicitud explícita.
9. Recién después habilitar `PYME_013` como `COMPOSITE`, consumiendo resultados gobernados `dso` y `dpo`.

## Prohibiciones

- No reconstruir DSO ni DPO implícitamente dentro de `PYME_013`.
- No consumir evidencia cruda directamente desde la capacidad compuesta.
- No crear una segunda raíz.
- No autorizar delivery.
- No agregar LLM ni selección automática.

## Criterio de cierre de CYCLE_045A

- `dpo` registrado explícitamente en el kernel.
- tests de dominio, clasificación, bloqueos y raíz productiva.
- regresión completa verde.
- root única preservada.
- `PYME_013` todavía no conectado.

## Próximo ciclo

`CYCLE_045B_CONNECT_PYME_013_COMPOSITE`
