# M31 — Servicio asistido repetible Checkpoint

## Estado

PASS

## Contexto

M31 cierra el tramo del roadmap de servicio asistido Excel + semántica PyME.

Base previa:

- M27: mensaje del dueño + Excel controlado -> IntakeRecord -> evidence gate -> READY_FOR_ANALYSIS.
- M28: ActionableFinding[] -> EvidenceItem[] -> NarrativeReport grounded -> markdown legible/auditable.
- M29: owner_message + tenant_id + case_id + evidence_refs + ActionableFinding[] -> Markdown mínimo entregable.
- M30: caso asistido persistido por tenant -> recuperación y evolución del contexto -> aislamiento entre tenants.

M31 no declara producto final, autonomía end-to-end ni servicio comercial validado.

M31 define y valida documentalmente un protocolo operativo para probar repetibilidad asistida en 3 a 5 casos piloto.

## Archivos M31

- docs/roadmap/M31_SERVICIO_ASISTIDO_REPETIBLE_PLAN.md
- docs/smartpyme/M31_SERVICIO_ASISTIDO_REPETIBLE_PROTOCOL.md
- tests/smartpyme/test_m31_service_protocol_docs.py

## Objetivo del slice

Probar repetibilidad operativa asistida, no producto.

El protocolo cubre:

- criterio de entrada;
- criterio de bloqueo;
- checklist de ejecución;
- plantilla de registro de piloto;
- medición de tiempo/costo;
- registro de bloqueos;
- registro de aprendizajes;
- criterio de repetibilidad;
- criterio de no repetibilidad.

## Validación reportada por auditor externo/local

El asistente de chat no ejecutó pytest directamente.
La siguiente evidencia fue reportada por el usuario desde auditor externo/local.

Comando ejecutado:

python -m pytest tests/smartpyme/test_m31_service_protocol_docs.py -q

Resultado reportado:

4 passed in 0.21s

## Veredicto de auditoría externa

PASS.

Causa reportada:

1. Los archivos creados para M31 son estrictamente documentales y de prueba de conformidad.
2. Respetan las restricciones operativas.
3. No modifican código productivo, dispatcher, registry, UI ni integraciones.
4. El protocolo define servicio asistido y no declara producto autónomo o comercial.
5. El test documental funciona como gate estático de conformidad del roadmap.

## Riesgo detectado

El test documental usa aserciones de subcadenas literales. Esto blinda el alcance, pero vuelve frágil la prueba ante cambios de redacción que preserven significado.

Decisión: aceptar esa rigidez por ahora para evitar deriva de alcance durante la fase M31.

## Certificado por M31

M31 certifica documentalmente que existe un protocolo repetible para ejecutar pilotos asistidos sin improvisar.

## No certificado por M31

M31 no certifica:

- producto final;
- pricing validado;
- servicio comercial validado;
- casos reales ya ejecutados;
- autonomía end-to-end;
- UI;
- PDF profesional;
- integración con dispatcher;
- integración con ERP;
- automatización comercial.

## Próximo paso sugerido

Cerrar M31 con commit/push.

Luego decidir, fuera de este hito, si se abre una fase de pilotos reales con registro de 3 a 5 casos usando el protocolo M31.
