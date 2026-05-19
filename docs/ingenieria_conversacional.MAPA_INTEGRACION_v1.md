# Mapa de integración — Ingeniería conversacional v1

## Estado

Documento de consolidación documental. Ordena solapamientos entre el corpus migrado desde SmartPyme y la biblioteca actual de PymIA.

Este documento cumple cuatro funciones:

1. eliminar duplicaciones operativas;
2. definir jerarquía canónica inicial;
3. separar memoria histórica de normativa viva;
4. declarar qué documentos gobiernan runtime conversacional.

## Clasificación documental

### A. Normativa viva

Documentos que gobiernan comportamiento futuro y deben usarse antes de tocar runtime:

1. `docs/ingenieria_conversacional.NORMATIVA_v1.md`
2. `docs/ingenieria_conversacional.PROTOCOLO_PRIMER_CONTACTO_v1.md`
3. `docs/producto/capa-01-admision-epistemologica.md`
4. `docs/catalogo/anamnesis-y-catalogos.md`
5. `docs/catalogo/diseno-catalogo-clinico.md`
6. `docs/contratos/contratos-clinicos-operacionales.md`
7. `docs/contratos/evidence-chain-v1.md`
8. `docs/contratos/owner-decision-v1.md`
9. `docs/epistemologia/contrato-epistemologico-smartgraph.md`
10. `docs/epistemologia/modelo-verdad-soberania.md`

### B. Memoria histórica / corpus bruto

Documentos que conservan ADN, decisiones previas, roleplay conceptual o material de trabajo, pero no gobiernan runtime directamente:

1. `docs/ingenieria_conversacional.corpus_migrado.md`
2. `docs/ingenieria_conversacional.README.md`
3. documentos originales en `SmartPyme/docs/*` citados como fuente de provenance
4. código histórico conversacional en `SmartPyme/app/laboratorio_pyme/conversation/*`

La memoria histórica no debe borrarse. Sirve para depuración, reconstrucción y auditoría de origen.

### C. Catálogo operativo conversacional

Documento puente entre normativa viva y futura implementación:

1. `docs/ingenieria_conversacional.CATALOGO_HIPOTESIS_Y_EVIDENCIA_v1.md`
2. `docs/catalogo/atlas-sintomas-patologias.md`

Estos documentos no diagnostican. Definen síntomas, hipótesis, evidencia y preguntas.

## Jerarquía canónica final inicial

Para resolver contradicciones, aplicar este orden:

1. `ARCHITECTURE_GUARDRAILS.md`
2. `docs/README.md`
3. `docs/ingenieria_conversacional.NORMATIVA_v1.md`
4. `docs/ingenieria_conversacional.PROTOCOLO_PRIMER_CONTACTO_v1.md`
5. `docs/producto/capa-01-admision-epistemologica.md`
6. `docs/catalogo/anamnesis-y-catalogos.md`
7. `docs/catalogo/diseno-catalogo-clinico.md`
8. `docs/contratos/*`
9. `docs/epistemologia/*`
10. `docs/ingenieria_conversacional.corpus_migrado.md`

La normativa viva prevalece sobre el corpus bruto. El corpus bruto conserva contexto pero no puede contradecir la normativa vigente.

## Documentos que gobiernan runtime conversacional

Antes de modificar cualquiera de estos componentes:

- `pymia/pipeline/admission/v1/response_formatter.py`
- `pymia/services/initial_laboratory_anamnesis_service.py`
- `pymia/interfaces/conversational_port.py`
- `conversa-engine/HERMES_TELEGRAM_SYSTEM_PROMPT.md`
- `conversa-engine/TELEGRAM_PYMIA_ROUTING.md`

se deben verificar obligatoriamente:

```text
docs/ingenieria_conversacional.NORMATIVA_v1.md
docs/ingenieria_conversacional.PROTOCOLO_PRIMER_CONTACTO_v1.md
docs/producto/capa-01-admision-epistemologica.md
docs/catalogo/anamnesis-y-catalogos.md
docs/catalogo/diseno-catalogo-clinico.md
docs/contratos/contratos-clinicos-operacionales.md
```

## Eliminación de duplicaciones

No se eliminarán documentos todavía. Se eliminan duplicaciones operativas por jerarquía:

- Si dos documentos explican anamnesis, gobierna `PROTOCOLO_PRIMER_CONTACTO_v1.md` para runtime y `anamnesis-y-catalogos.md` para fundamento amplio.
- Si dos documentos explican hipótesis, gobierna `CATALOGO_HIPOTESIS_Y_EVIDENCIA_v1.md` para primer contacto y `diseno-catalogo-clinico.md` para diseño profundo.
- Si dos documentos explican evidencia, gobiernan `contratos/evidence-chain-v1.md` y `contratos-clinicos-operacionales.md`.
- Si dos documentos explican verdad/incertidumbre, gobiernan `epistemologia/*`.
- Si dos documentos explican UX Telegram, gobiernan `PROTOCOLO_PRIMER_CONTACTO_v1.md` y `producto/capa-01-admision-epistemologica.md`.

## Gating documental

Toda modificación de runtime conversacional debe declarar:

```text
DOCS_CHECKED:
- ruta 1
- ruta 2
- ruta 3

RUNTIME_TARGET:
- archivo tocado

CANONICAL_DRIFT_RISK:
- NONE | LOW | MEDIUM | HIGH
```

Si no se puede demostrar lectura documental previa, el cambio queda bloqueado por:

```text
CANONICAL_DRIFT_GATE P0
```

## Regla de cierre

La implementación futura debe moverse desde:

```text
claim → formatter → respuesta
```

hacia:

```text
sesión → anamnesis → foco síntomas → evidencia → hipótesis → pregunta siguiente → informe
```

Ese cambio requiere diseño técnico separado. Este documento solo fija jerarquía y fuente soberana.
