# HERMES_LOCAL_INSTANCE_INVENTORY

Estado: READ_ONLY_AUDIT

## Alcance

Inventario pasivo de la instalación local existente de Hermes Agent en la PC local.

Este documento registra presencia, rutas y riesgos operativos sin exponer secretos ni ejecutar Hermes.

## Reglas aplicadas

- No se ejecutó Hermes.
- No se inició ningún loop autónomo.
- No se usó `--yolo`.
- No se tocó Telegram real.
- No se modificaron archivos de configuración activos.
- No se imprimieron tokens, API keys, credenciales ni contenido de `.env`.
- No se validó producción.
- No se ejecutó MCP-3.

## Rutas relevantes

Raíz de trabajo:

```text
E:\BuenosPasos\smartbridge
```

Repo PymIA:

```text
E:\BuenosPasos\smartbridge\PymIA
```

Instalación / checkout Hermes detectado:

```text
E:\BuenosPasos\smartbridge\hermes-agent
```

## Archivos de configuración detectados

Se detectó presencia de archivos de configuración y entorno asociados a Hermes.

Se detectó presencia de archivo `.env`, contenido omitido.

Los valores sensibles fueron omitidos deliberadamente.

Tipos de archivo detectados o esperables:

```text
config.yaml
soul.md
memory.md
.env
skills/
logs/
```

## Telegram

Se detectó configuración relacionada con Telegram en la instalación local de Hermes.

Token de bot: `<REDACTED_BOT_TOKEN>`

No se documentan tokens reales, chat IDs, allowed users ni credenciales.

Conclusión:

```text
La instancia local de Hermes debe tratarse como activo sensible porque tiene integración Telegram configurada.
```

## API keys

Se detectó presencia de credenciales/API keys en configuración local.

API key: `<REDACTED_API_KEY>`

No se documentan valores reales ni fragmentos parciales.

## HERMES_HOME sandbox requerido

La instancia local existente de Hermes no debe usarse como sandbox SCN.

Antes de cualquier prueba se debe crear un `HERMES_HOME` separado, aislado y descartable, sin tokens reales, sin memoria real, sin skills reales y sin integración Telegram real.

Recomendación de sandbox futuro:

```text
E:\BuenosPasos\smartbridge\.tmp\hermes-scn-local
```

Ese sandbox no debe reutilizar memoria, skills, logs ni tokens reales de la instancia existente.

## Memoria / skills / logs

La instancia Hermes puede contener memoria operativa, skills y logs persistentes.

Riesgos:

- contaminación de pruebas SCN con estado histórico;
- exposición accidental de secretos en logs;
- persistencia de inferencias no auditadas;
- reutilización indebida de skills en un entorno de soberanía computacional.

## Procesos activos

No se registra en este documento ningún comando de ejecución de Hermes.

Cualquier revisión futura de procesos debe hacerse sin iniciar Hermes ni loops autónomos.

## Prohibiciones

- No ejecutar Hermes.
- No usar `--yolo`.
- No iniciar loops `forward`/`goal`.
- No tocar Telegram real.
- No usar tokens reales en sandbox.
- No versionar secretos.
- No usar esta instancia como entorno de prueba SCN.
- No ejecutar MCP-3.
- No tocar producción.
- No modificar configuración sensible.

## Riesgos identificados

- Telegram real configurado.
- Posible presencia de secretos en `.env` o configuración local.
- Posible `HERMES_HOME` con estado persistente.
- Posibles skills o memoria generados por uso previo.
- No debe usarse esta instancia como sandbox SCN sin aislamiento previo.

## Recomendación

No trabajar directamente sobre la instancia local existente de Hermes para pruebas SCN.

Crear un sandbox derivado separado con:

- `HERMES_HOME` nuevo y descartable;
- sin token Telegram real;
- sin memoria real;
- sin skills reales;
- sin `--yolo`;
- sin loops autónomos;
- audit logs activos;
- tools mínimas;
- policy restrictiva;
- fail-closed obligatorio.

## Estado final

READ_ONLY_AUDIT_REDACTED
