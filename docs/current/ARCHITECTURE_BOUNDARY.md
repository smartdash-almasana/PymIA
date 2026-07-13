# Límite arquitectónico vigente

## Flujo rector

```text
Dueño PyME
↕
Capa conversacional
↕
PymIA computacional
↕
Tools determinísticas
↕
Archivos de entrega
```

## Responsabilidades

- El dueño PyME aporta evidencia y confirma el significado operativo de sus datos.
- La capa conversacional formula preguntas y explica resultados; no decide verdad operacional.
- PymIA gobierna estados, evidencia, bloqueos, bindings semánticos, computabilidad y selección autorizada de capacidades.
- Las tools ejecutan cálculos y producen archivos.

## Servicio 1

La única raíz productiva autorizada es la cadena canónica que parte de un archivo real, conserva su evidencia estructural, comprende columnas, pregunta solo cuando corresponde, reingresa respuestas canónicas y ejecuta tools explícitamente solicitadas.

## Prohibiciones

- No segundo parser XLSX.
- No cadenas semánticas paralelas.
- No texto libre que convierta `unknown` en confirmado.
- No LLM como autoridad de cálculo, diagnóstico o estado.
- No operador humano obligatorio ni revisión posterior como definición del producto.
- No landing, demo o documentación histórica gobernando runtime.

## Sistemas externos

Hermes, Telegram, gateways, MCP históricos, SaaS adapters y experimentos de infraestructura no forman parte de la autoridad productiva de Servicio 1 salvo contrato vigente y referencia explícita desde `docs/current/README.md`.
