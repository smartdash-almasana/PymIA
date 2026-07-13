# PymIA — guardrails arquitectónicos

## Jerarquía de verdad

1. Código físico y tests verdes.
2. `AGENTS.md`.
3. `docs/current/README.md` y los documentos que enumera.
4. Evidencia técnica citada explícitamente.
5. Memoria conversacional solo como pista.

## Invariantes

- La capa conversacional comunica; PymIA decide y computa.
- El dueño PyME aporta datos y significado operacional.
- No LLM obligatorio ni autoridad LLM en el núcleo determinístico.
- No segundo parser XLSX ni cadenas soberanas paralelas.
- No runtime Hermes, jobs, workflows, APIs externas, OCR o PDF parser por inferencia documental.
- Sin evidencia suficiente: bloquear y preguntar.
- Las tools se ejecutan solo por recorridos explícitos y gobernados.

## Política documental

- No reconstruir arquitectura desde memoria.
- No crear un archivo documental por cada slice, test o cierre.
- Actualizar documentos rectores existentes.
- Eliminar documentos sustituidos; Git conserva su historia.
- Ningún archivo no listado en `docs/current/README.md` autoriza código.

## Validación

- tests focales y regresión relevante verdes;
- ausencia de imports o capacidades prohibidas;
- claims limitados a la evidencia observada.
