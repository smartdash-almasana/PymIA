# M50 — Guided Evidence Recovery Replay Checkpoint

Fecha: 2026-06-09
Estado: CLOSED

## Alcance M50

M50 no abrió funcionalidad nueva.

Su propósito fue cerrar un replay end-to-end de la cadena ya construida entre M45 y M49:

```text
missing_evidence
→ OwnerQuestionsBundle
→ owner_questions_bundle.json
→ render_contract.next_questions
→ render_contract.blocked_message
→ response visible
```

El frente fue estrictamente de checkpoint/replay.

## Commits previos relevantes

- `d92939c` `docs(pymia): authorize M45 guided evidence recovery`
- `8006d05` `feat(pymia): add owner questions contract`
- `206ae07` `feat(pymia): build owner questions from evidence gaps`
- `802e8df` `feat(pymia): integrate owner questions into delivery bundle`
- `de769ec` `feat(pymia): expose owner questions in delivery response`

## Evidencia pytest

Suite ejecutada y atribuida:

```text
python -m pytest tests/orchestration/test_graph.py tests/diagnosticcore/test_core_audit_delivery_bridge.py -q --basetemp .tmp_pytest_m50
→ 36 passed in 15.65s
```

## Qué queda certificado

- el replay real existente genera físicamente `owner_questions_bundle.json`
- `owner_questions_bundle.json` contiene preguntas legibles
- las preguntas provienen de gaps reales o de bloqueo trazado
- `render_contract.next_questions` contiene textos amigables proyectados desde `OwnerQuestionsBundle`
- `render_contract.blocked_message` contiene la primera pregunta visible
- la respuesta visible del replay contiene la pregunta cuando el caso queda bloqueado
- el circuito no requirió modificar `graph.py`
- la cadena documental/técnica M45→M49 queda observable en un replay end-to-end real

## Qué NO queda certificado

- no queda certificado ningún canal productivo hacia el dueño
- no queda certificada lógica conversacional
- no queda certificada recuperación efectiva de evidencia por respuesta del dueño
- no queda certificado Telegram, Hermes, FastAPI ni runtime externo
- no queda certificada interpretación semántica avanzada más allá del mapping estático autorizado

## Riesgos residuales

- el replay depende del fixture actual y de los gaps que ese flujo produzca
- la visibilidad contractual de preguntas no equivale todavía a una interacción guiada completa
- el circuito sigue sin cerrar el loop de respuesta del dueño hacia intake/evidence

## Próximo paso metodológico

Abrir el siguiente frente sólo si se autoriza una frontera explícita para consumir respuestas del dueño sin mezclar:

```text
pregunta visible
≠ respuesta capturada
≠ evidencia registrada
≠ diagnóstico recalculado
```

Ese frente deberá nacer con ADR / CapabilitySpec / ModuleContract / TaskSpec / tests / evidence propios.
