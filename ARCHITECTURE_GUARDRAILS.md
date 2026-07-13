# PymIA Architecture Guardrails

Este documento fija los invariantes para evitar deriva arquitectónica y documental.

## 1. Jerarquía de verdad

```text
1. código físico vigente;
2. tests verdes y evidencia observada;
3. docs/current/README.md y sus referencias explícitas;
4. contratos y ADR vigentes citados desde la autoridad actual;
5. documentación externa con provenance;
6. memoria conversacional solo como pista.
```

Un documento histórico no puede contradecir código y tests actuales ni autorizar nuevas capacidades.

## 2. Servicio 1

```text
La IA conversa.
La FSM gobierna.
Las tools ejecutan.
Los archivos son el producto.
El dueño confirma significado durante la lectura.
```

La raíz canónica debe reutilizar la ingesta XLSX existente, conservar evidencia real, bloquear ambigüedades y admitir únicamente respuestas semánticas canónicas o exclusión explícita de una columna no relevante.

## 3. Prohibiciones

- segundo parser XLSX;
- cadenas productivas paralelas;
- `unknown` desbloqueado por texto libre;
- LLM obligatorio o soberano en el core;
- operador humano obligatorio como actor del producto;
- APIs, workers, canales o runtimes externos autorizados por documentación histórica;
- landing o demo usada como evidencia productiva;
- promesas de diagnóstico o entrega sin evidencia del caso.

## 4. Política documental

- `docs/current/` debe contener únicamente autoridad vigente y evidencia necesaria.
- No se conserva documentación obsoleta como “museo”, “archive” o “legacy” dentro del árbol activo cuando pueda contaminar decisiones.
- Lo eliminado permanece recuperable mediante Git; no necesita seguir físicamente presente.
- No crear un documento nuevo cuando uno vigente puede actualizarse.
- Todo documento rector debe indicar alcance, estado y fuente de evidencia.
- Índices históricos no tienen autoridad sobre `docs/current/README.md`.

## 5. Política de pruebas

- Todo cambio productivo requiere tests focales y regresión vecina.
- Una declaración global de estabilidad requiere regresión completa.
- PASS solo con evidencia observada y alcance explícito.

## 6. Criterios mínimos

```text
working tree controlado;
root productiva única;
flags de seguridad preservados;
pruebas verdes;
documentación vigente alineada con código real;
sin referencias rectoras a documentos eliminados.
```
