# PymIA — Astro Landing Blueprint

Diseño unificado para implementar una landing profesional de PymIA, basado en la auditoría de tres landings previas de SmartPyme/PymIA.

## Objetivo

Construir una landing de conversión para PymIA como laboratorio operacional PyME:

- evidencia antes que diagnóstico;
- archivos reales como entrada;
- hallazgos accionables como salida;
- WhatsApp y Telegram como canales conversacionales;
- chatbot promocionado como continuidad operativa, no como magia.

## Narrativa rectora

> Tu PyME ya está hablando. PymIA convierte archivos, mensajes y síntomas operativos en evidencia, hallazgos y próximos pasos.

## Secciones finales

1. Hero con promesa central.
2. Componente de ingesta de archivos.
3. Pain points del dueño PyME.
4. Cómo funciona el laboratorio.
5. Módulos de diagnóstico.
6. WhatsApp + Telegram como canales del chatbot.
7. Preview de informe / hallazgos.
8. Planes o niveles.
9. FAQ.
10. CTA final.

## Paleta recomendada

- Fondo: `#070B0F`
- Panel: `#0E151D`
- Panel elevado: `#121B24`
- Verde evidencia: `#00E676`
- Azul inteligencia: `#64B5F6`
- Amarillo advertencia: `#FFD600`
- Rojo riesgo: `#FF3D57`
- Texto principal: `#EEF3F7`
- Texto secundario: `#91A0AD`

## Tipografía

- Display: `DM Serif Display`
- UI: `Outfit`
- Técnica: `IBM Plex Mono`

## Implementación Astro

Estructura sugerida:

```text
src/
  pages/
    index.astro
  components/
    Hero.astro
    FileIngestionPanel.astro
    LabModules.astro
    ChatbotChannels.astro
    ReportPreview.astro
    Plans.astro
    FAQ.astro
  styles/
    global.css
```
