# Conversational Runtime Offline E2E

Estado: CERRADO / PASS_E2E
Fecha: 2026-05-31

## Propósito

Este documento registra el cierre del hito de runtime conversacional offline persistente para PymIA.

El objetivo validado fue que `conversa-engine` pueda operar una Ficha PyME inicial completa desde CLI, entre procesos separados, sin reiniciar la conversación y sin depender únicamente de memoria RAM.

## Commits validados

- `110cec5 feat(smartpyme): add initial company profile FSM`
- `5105c60 feat(conversa): persist runtime state across CLI turns`

## Contrato de producto validado

Primer contacto obligatorio:

```text
FICHA_PYME_INICIAL
```

Reglas verificadas:

- el sistema no diagnostica en el primer contacto;
- el sistema no interpreta el dolor inicial como hipótesis;
- el sistema no ejecuta análisis antes de completar ficha;
- el sistema abre una Ficha PyME conversacional;
- la ficha avanza una pregunta por turno;
- el primer mensaje del usuario queda conservado como `raw_first_message`;
- `profile_step` y `profile_data` persisten entre comandos CLI separados.

## Secuencia funcional de ficha

La Ficha PyME inicial cubre:

1. contacto: nombre y apellido;
2. rol en la empresa;
3. teléfono o WhatsApp;
4. email;
5. nombre de empresa o marca;
6. actividad principal;
7. rubro concreto;
8. modelo operativo;
9. canales de venta;
10. presencia digital;
11. links de web/redes/marketplaces;
12. catálogo o lista de precios;
13. tamaño operativo;
14. herramientas actuales;
15. problema principal;
16. período a revisar;
17. evidencia disponible;
18. cierre de ficha inicial.

## Prueba E2E CLI multiproceso

Comandos ejecutados como procesos separados:

```powershell
python conversa-engine/main.py "RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY"
python conversa-engine/main.py "Alejandro Arab"
python conversa-engine/main.py "Dueño"
python conversa-engine/main.py "11 1234 5678"
python conversa-engine/main.py "alejandro@email.com"
python conversa-engine/main.py "SmartPyme Test SRL"
python conversa-engine/main.py "1"
python conversa-engine/main.py "textil"
python conversa-engine/main.py "compro ropa terminada y revendo"
python conversa-engine/main.py "2, 3, 6"
python conversa-engine/main.py "Instagram, WhatsApp Business y Google Maps"
python conversa-engine/main.py "https://instagram.com/smartpymetest"
python conversa-engine/main.py "lista de precios Excel"
python conversa-engine/main.py "2 a 5 personas"
python conversa-engine/main.py "Excel y WhatsApp"
python conversa-engine/main.py "RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY"
python conversa-engine/main.py "últimos 3 meses"
python conversa-engine/main.py "ventas, compras, lista de precios"
```

Resultado validado:

- la conversación no se reinicia entre comandos;
- la ficha avanza paso por paso;
- al finalizar, el estado llega a `INITIAL_PROFILE_COMPLETE`;
- `profile_data.profile_status` queda en `COMPLETE`;
- `raw_first_message` conserva `RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY`.

## Persistencia

El runtime reutiliza infraestructura formal existente:

- `pymia/orchestration/state.py`
- `pymia/orchestration/state_storage.py`

No se creó un almacenamiento paralelo.

El estado persistido usa:

```text
PymIAState.progressive_context
```

Ruta por defecto observada:

```text
conversa-engine/.conversation_state/<tenant_sanitizado>/conversation_states.jsonl
```

También existe override por entorno:

```text
PYMIA_CONVERSA_STATE_BASE_DIR
```

## Campos críticos verificados

En el último estado persistido se verificó la presencia de:

```text
tenant_id
chat_id
conversation_id
last_user_message
progressive_context
fsm_state
phase
profile_step
profile_data
```

Campos de ficha verificados:

```text
profile_data.contact.full_name
profile_data.contact.role
profile_data.contact.phone
profile_data.contact.email
profile_data.company.legal_or_trade_name
profile_data.business_taxonomy.activity_type
profile_data.business_taxonomy.industry_label
profile_data.business_model.operating_model
profile_data.business_model.sales_channels
profile_data.digital_presence.presence_channels
profile_data.digital_presence.website_url / social_links
profile_data.commercial_catalog.has_catalog
profile_data.commercial_catalog.catalog_type
profile_data.company_profile.team_size_range
profile_data.current_tools.primary_information_system
profile_data.initial_problem.primary_pain
profile_data.analysis_scope.period
profile_data.evidence.available
```

## Prohibiciones verificadas

Durante la Ficha PyME inicial, antes de `INITIAL_PROFILE_COMPLETE`, no debe aparecer ni ejecutarse:

- diagnóstico;
- hipótesis;
- microservicio;
- microSaaS;
- análisis de margen;
- inferencia de causa;
- ejecución operativa.

El runtime debe capturar estructura antes de interpretar.

## Tests validados

```text
python -m pytest tests/orchestration/test_state.py tests/orchestration/test_state_storage.py -q
→ 30 passed

python -m pytest tests/test_conversa_engine_boundary_consumption_smoke.py tests/test_conversa_progressive_context_roundtrip.py -q
→ 4 passed

python -m pytest tests/smartpyme -q
→ 416 passed
```

## Estado de cierre

Veredicto final:

```text
CONVERSATIONAL_RUNTIME_OFFLINE_READY
```

Este hito deja lista la base conversacional offline persistente para pruebas humanas locales y evolución posterior hacia canales reales.

## Próximo frente natural

No abrir análisis, canales reales ni nuevas capacidades antes de validar humanamente la calidad de la entrevista completa.

Próximo frente recomendado:

```text
HUMAN_ONBOARDING_QUALITY_REVIEW
```

Objetivo: revisar si la entrevista de Ficha PyME es clara, profesional, útil y suficientemente inteligente para un dueño de PyME real.
