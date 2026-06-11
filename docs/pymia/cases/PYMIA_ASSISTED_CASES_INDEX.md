# PYMIA ASSISTED CASES INDEX

Estado: `OPERATIVO_LOCAL`

Índice de casos asistidos locales del `Faithful Operator`.

## Propósito

Mantener trazabilidad de casos reales o simulados usados para operación asistida local, sin abrir producto, canal, runtime ni diagnóstico final automático.

## Casos disponibles

### Cafetería ABC

Estado: `SESSION_RECORD_READY`

Archivos:

- `docs/pymia/cases/PYMIA_CASE_CAFETERIA_ABC_ASSISTED.md`
- `docs/pymia/cases/PYMIA_CASE_CAFETERIA_ABC_OWNER_SESSION.md`
- `docs/pymia/cases/PYMIA_CASE_CAFETERIA_ABC_SESSION_RECORD.md`

Evidencia base:

```text
prueba_excels/Cafetería ABC.xlsx
```

Trazabilidad validada:

```text
tenant_id: demo_cafeteria_abc
intake_id: intake_93546f538f5da1a7
evidence_id: evidence_fb309447997d4ef684c23bd417f645bf
run_id: run_c1c805258c8f4262bc309376f81cd662
output_hash: bea6fc31cb1fbf33cb2be7ea3771ba9c39dbedf8f346c73011786e7762f012ba
```

Estado operativo:

```text
relato del dueño + Excel real → salida trazable → sesión asistida → registro ejecutable
```

## Plantilla reutilizable

- `docs/pymia/cases/PYMIA_ASSISTED_CASE_TEMPLATE.md`

Uso:

```text
copiar plantilla → completar identificación → ejecutar demo local → registrar sesión → definir foco operativo
```

## Regla de inclusión

Un caso sólo entra en este índice si tiene:

1. relato inicial del dueño;
2. evidencia base identificada;
3. trazabilidad mínima (`tenant_id`, `intake_id`, `evidence_id`, `run_id`, `output_hash` o estado honesto de ausencia);
4. límite explícito de no diagnóstico final automático;
5. próxima acción operativa.

## Prohibiciones

No incluir casos que dependan de:

- canal externo;
- LLM libre;
- runtime productivo;
- DB productiva;
- Telegram/Hermes;
- PDF final;
- promesa de producto terminado.
