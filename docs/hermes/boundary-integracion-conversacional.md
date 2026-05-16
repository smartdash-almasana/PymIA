# Boundary de integración conversacional — Hermes, canales y providers

Contexto heredado. Este documento no autoriza jobs, workflows, orquestación, authorization flow, factory, app.*, MCP legacy ni runtime Hermes duplicado dentro de PymIA. Rige `../../ARCHITECTURE_GUARDRAILS.md`.

## Estado

Documento operativo de frontera — v0.1.

## Decisión

PymIA no implementa bot de Telegram, provider LLM, ingesta documental pesada, OCR ni runtime Hermes.

PymIA expone únicamente el boundary clínico-conversacional ya presente:

```text
Hermes / canal externo
→ HermesAdapter
→ ClinicalConversationalPort
→ InitialLaboratoryAnamnesisService
→ AdmissionPipelineV1
→ AdmissionResponseFormatterV1
```

## Regla rectora

```text
Hermes conversa.
PymIA computa.
```

## Lo que vive fuera de PymIA

### Telegram

Telegram es canal externo. Debe resolver recepción, metadata del canal, archivos, sesiones y envío de mensajes fuera del kernel PymIA.

PymIA solo puede recibir texto ya seleccionado mediante:

```text
HermesInput(tenant_id, channel, message_text, metadata)
```

### Provider IA

El provider IA conversacional vive en Hermes o en una capa externa explícita.

Puede ayudar a conversar, reformular o pedir aclaraciones, pero no decide verdad operacional ni diagnostica fuera del kernel.

No debe convertirse en dependencia obligatoria de `pymia.pipeline`, `pymia.services`, `pymia.contracts` ni `pymia.interfaces`.

### BEM / ingesta documental grande / OCR

BEM, OCR e ingesta documental pesada son frontera documental externa.

PymIA puede pedir evidencia y recibir referencias o outputs estructurados validados, pero no debe incorporar runtime documental pesado en el core de admisión conversacional.

## Contrato permitido hoy

El contrato físico disponible hoy es:

```text
pymia.hermes.adapter.HermesInput
pymia.hermes.adapter.HermesOutput
pymia.hermes.adapter.HermesAdapter
pymia.interfaces.conversational_port.ConversationalInput
pymia.interfaces.conversational_port.ConversationalOutput
pymia.interfaces.conversational_port.ClinicalConversationalPort
```

## Flujo mínimo de demo futura

```text
Telegram recibe mensaje
→ Hermes externo construye HermesInput
→ HermesAdapter.handle(input)
→ PymIA devuelve HermesOutput
→ Hermes externo envía output.reply_text
```

Si `status == no_signal`, Hermes externo puede pedir más contexto conversacional. PymIA no prescribe acción externa.

## Flujo documental futuro

```text
Telegram recibe archivo
→ Hermes externo registra evento crudo
→ BEM/OCR externo procesa documento si corresponde
→ salida documental estructurada se valida contra contrato
→ PymIA usa evidencia estructurada solo cuando exista boundary explícito
```

## Prohibiciones

PymIA no debe:

- importar SDKs de Telegram;
- importar clientes de providers IA;
- guardar API keys;
- crear runtime Hermes alternativo;
- crear jobs;
- crear workflows;
- implementar authorization flow;
- convertir BEM/OCR en decisor clínico;
- interpretar metadata del canal como instrucción clínica;
- aceptar outputs LLM como verdad sin contrato y validación.

## Criterio para comenzar integración real

Antes de implementar demo Telegram real, debe existir fuera de PymIA:

```text
1. runtime Hermes externo;
2. provider IA configurado explícitamente en Hermes;
3. adapter de canal Telegram externo;
4. forma de construir HermesInput;
5. regla de envío de HermesOutput.reply_text;
6. frontera documental para archivos/OCR/BEM;
7. tests que demuestren que PymIA sigue sin importar Telegram/provider/BEM.
```

## Validación requerida por ciclo

Cada cambio que toque esta frontera debe cerrar con:

```text
pytest -q
check_forbidden_terms
audit_docs_index
run_pymia_demo("vendo mucho pero no sé si gano plata")
```
