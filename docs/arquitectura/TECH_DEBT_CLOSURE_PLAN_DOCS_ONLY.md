# PymIA Docs-Only Debt Closure Plan

## Estado
VIGENTE

## Fecha
2026-05-24

## Objetivo
Cerrar documentalmente la deuda técnica registrada en `TECH_DEBT_REGISTER.md` sin modificar código, sin ejecutar runtime, sin tocar producción y sin habilitar MCP-3.

**No tocar código.**  
**No tocar producción.**  
**No ejecutar runtime.**

## Documento fuente
- `docs/arquitectura/TECH_DEBT_REGISTER.md`

## Fases

### Fase A — Inventario documental
**Objetivo:** confirmar que toda la deuda registrada tiene fuente documental trazable.

**Acciones:**
1. Verificar que cada item TD-001 a TD-014 tenga al menos una fuente obligatoria como evidencia.
2. Confirmar que no existen items huérfanos sin referencia documental.
3. Verificar que no hay evidencia inventada ni secreta.

**Criterios de salida:**
- Todos los items tienen al menos 1 fuente obligatoria.
- Ningún item tiene evidencia inexistente o inventada.
- No hay secretos ni contenido `.env` en ningún documento.

---

### Fase B — Normalización documental
**Objetivo:** producir documentos de cierre para items P0 y P1 que lo requieran.

**Acciones:**
1. Para cada item P0: producir documento de política/baseline/matriz aprobado.
2. Para cada item P1: producir documento de política/taxonomía/matriz aprobado.
3. Items P2: documentar si son cerrables en este ciclo o quedan como deuda residual.

**Criterios de salida:**
- Todos los items P0 tienen documento de cierre con estado VIGENTE.
- Todos los items P1 tienen documento de cierre con estado VIGENTE o quedan marcados como BLOCKED con justificación.
- Los documentos de cierre no contienen secretos, código, ni instrucciones de ejecución.

---

### Fase C — Trazabilidad
**Objetivo:** asegurar que el índice documental (`DOCUMENTATION_INDEX.md`) refleja todos los documentos nuevos.

**Acciones:**
1. Registrar cada documento nuevo en `DOCUMENTATION_INDEX.md`.
2. Verificar que no hay filas duplicadas.
3. Verificar que estado, tema y relación con código sean coherentes.

**Criterios de salida:**
- `DOCUMENTATION_INDEX.md` contiene todas las filas nuevas sin duplicados.
- Cada documento nuevo es reachable desde el índice.
- El formato respeta la tabla existente.

---

### Fase D — Aprobación
**Objetivo:** consolidar resultado de cierre y declarar estado final del paquete documental.

**Acciones:**
1. Verificar que todos los criterios de salida de fases A, B y C se cumplieron.
2. Producir `TECH_DEBT_CLOSURE_RESULT_DOCS_ONLY.md` con estado final.
3. Declarar si el paquete documental está listo para diseño MCP-3 o queda bloqueado.

**Criterios de salida:**
- Resultado documentado con PASS o BLOCKED.
- Si PASS: todos los P0 cerrados y P1 cerrados o justificados.
- Si BLOCKED: lista explícita de items no cerrados y motivo.

---

## Riesgos de ejecución documental

| Riesgo | Impacto | Mitigación |
| :--- | :--- | :--- |
| Item P0 sin cierre documental completo | Bloquea diseño MCP-3 | Priorizar P0 antes que P1/P2 |
| Incluir accidentalmente secretos en docs | Exposición de credenciales | Revisión manual de contenido antes de commit |
| Duplicar filas en DOCUMENTATION_INDEX | Degradación del gobierno documental | Validación de unicidad por ruta |
| Crear docs que autoricen ejecución productiva | Riesgo operacional | Prohibición explícita en cada documento |
| Inventar evidencia no respaldada por fuentes | Pérdida de trazabilidad | Solo citar fuentes obligatorias listadas |

## Definición de Done documental

El paquete documental está DONE cuando:
1. `TECH_DEBT_REGISTER.md` existe y está indexado.
2. `TECH_DEBT_CLOSURE_PLAN_DOCS_ONLY.md` existe y está indexado.
3. `TECH_DEBT_CLOSURE_RESULT_DOCS_ONLY.md` existe y está indexado.
4. `DOCUMENTATION_INDEX.md` tiene las 3 filas nuevas sin duplicados.
5. Todos los documentos incluyen prohibición explícita de cambios productivos.
6. Todos los documentos incluyen declaración explícita de MCP-3 no habilitado.
7. No hay secretos ni contenido `.env` en ningún documento.
8. No se modificó código, runtime, VM, Telegram, systemd ni `.env`.
9. Commit realizado solo con los 4 archivos documentales esperados.
10. Push exitoso a `origin main`.

## Restricciones duras
- No tocar código.
- No tocar producción.
- No ejecutar runtime.
- No tocar VM.
- No tocar Telegram/systemd/.env/~/.hermes.
- No crear nuevas tools MCP.
- No usar `git add .`.
- No inventar evidencia.
- No incluir secretos.
- Todo cambio solo en `docs/`.
