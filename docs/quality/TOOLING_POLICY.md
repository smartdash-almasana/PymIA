# PymIA Tooling Policy — Fast Quality Gate

## Estado

FASE 1-A: REPORT-ONLY.

## Reglas

1. Las herramientas observan; NOP gobierna.
2. Ningún scanner puede redefinir arquitectura, semántica, matemática o CURRENT STATE.
3. No hay autofix en el Fast Quality Gate.
4. Findings históricos y findings causados por el diff deben mantenerse distinguibles.
5. Una herramienta ausente se informa como `NOT_AVAILABLE`; no se maquilla como PASS.
6. Un finding no se remedia automáticamente.
7. Los oráculos/tests no se modifican para hacer pasar una implementación.
8. Product code queda fuera de FASE 1-A.
9. CI, dependencias y configuración de herramientas se incorporan sólo mediante cambio posterior autorizado.
10. CodeRabbit permanece al final del pipeline, después de gates determinísticos.

## Contrato de salida

El runner emite JSON con:

- `schema_version`
- `mode=REPORT_ONLY`
- `autofix=false`
- `blocking=false`
- resultados por herramienta

Estados permitidos por herramienta:

- PASS
- FINDINGS
- NOT_AVAILABLE
- ERROR

## Criterio de cierre de FASE 1-A

- runner creado;
- tests propios verdes;
- ningún archivo productivo tocado por esta fase;
- baseline físico previo preservado;
- STOP.
