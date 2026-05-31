# CONVERSA_REAL_RECALL_SMOKE

## Estado

Pendiente de validación local.

## Frente

SMARTPYME_TENANT_RECALL_CONVERSATION_SMOKE

## Propósito

Validar localmente que `conversa-engine/main.py` puede usar Supermemory real para recuperar contexto conversacional tenant-scoped antes de responder.

Este smoke prueba el síntoma original: que el sistema no vuelva a preguntar desde cero cuando ya existe contexto conversacional del mismo tenant.

## Script

```text
scripts/smoke_conversa_real_recall_local.py
```

## Flujo

1. Carga `SUPERMEMORY_API_KEY` desde entorno o `.env.local`.
2. Siembra en Supermemory una memoria segura:
   - fabrica ropa;
   - vende por Mercado Libre;
   - quiere entender si gana plata;
   - registro no computacional.
3. Espera 5 segundos.
4. Carga `conversa-engine/main.py` en el mismo proceso.
5. Ejecuta:

```text
run_message("RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY", tenant_id="smoke_tenant_conversa_real_recall", user_id="user_conversa_real_recall")
```

6. Evalúa si la respuesta contiene marcadores de amnesia:

```text
vendés productos, fabricás algo o prestás servicios
necesito entender tu negocio
```

## Salida esperada

```text
STATUS: OK
AMNESIA: NO
REPLY_CHARS: <n>
```

## Interpretación

```text
AMNESIA: NO  → recall conversacional útil confirmado.
AMNESIA: YES → Supermemory recupera o no, pero la respuesta todavía degrada a plantilla inicial.
```

## Límites

```text
- No toca VM.
- No toca Telegram productivo.
- No toca Supabase.
- No toca Obsidian.
- No toca kernel PymIA.
- No imprime API key ni payload completo.
```
