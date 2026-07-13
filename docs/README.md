# PymIA — documentación

La autoridad documental vigente está en [`docs/current/README.md`](current/README.md).

Reglas:

1. Solo gobiernan los documentos listados en `docs/current/README.md`.
2. Código físico y tests verdes prevalecen sobre prosa desactualizada.
3. Documentos obsoletos, duplicados o sustituidos se eliminan; Git conserva la historia.
4. No se crean nuevos closeouts, checkpoints, TaskSpecs o auditorías como archivos separados cuando la información puede incorporarse a un documento rector existente.
5. El resto de `docs/` se sanea por lotes y carece de autoridad salvo cita expresa desde `docs/current/README.md`.
