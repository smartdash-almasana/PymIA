# DESIGN.md — PymIA Landing Pública + Web Servicio 1

> Fuente única de verdad del sistema de diseño de PymIA (landing pública Astro + web del Servicio 1). Generado por la skill `tres-web-design-system`. Todo cambio se registra en la sección 10 (Governanza y changelog) antes de tocar código.

**Proyecto:** PymIA — landing comercial + aplicación Servicio 1 (controles operativos)
**Fecha:** 2026-08-13
**Estado:** en vigor
**Versión del sistema:** v1.0

---

## 1. Brand overview & personality

- **Qué es**: PymIA es un laboratorio operacional para PyMEs que convierte archivos (Excel, PDF, extractos) en hallazgos operativos con evidencia trazable. No inventa datos: si falta evidencia, declara exactamente qué falta.
- **Para quién**: dueños de PyME y responsables operativos (audiencia primaria); contadores y asistentes que ordenan la información (secundaria).
- **Adjetivos de marca**: confiable, riguroso, luminoso, cálido, institucional.
- **Anti-adjetivos**: startup tech genérica, dark neón, "sci-fi", cliché SaaS (gradientes azul-navy), lúdico, juvenil.
- **Tono de copy**: vos directo, operativo, sin promesas vacías. Frases cortas que nombran el problema concreto ("vendo mucho pero no sé si gano"). Evitar jerga técnica de IA y superlativos de marketing.

## 2. Typography

| Rol | Familia | Peso | Fallback | Uso |
|---|---|---|---|---|
| Display | Georgia / DM Serif Display | 400/700 | Georgia, "Times New Roman", serif | H1–H3, títulos de sección |
| Text | Aptos | 400/600/700 | "Segoe UI", system-ui, sans-serif | Cuerpo, UI, botones |
| Mono (funcional) | IBM Plex Mono | 400/500/700 | "Cascadia Mono", Consolas, monospace | Datos, eyebrows, chips, números |

- Escala fluida con `clamp()`: H1 `clamp(1.75rem, 3vw, 2.55rem)` · H2 `clamp(1.5rem, 2.6vw, 2.15rem)` · H3 `1.15–1.5rem` · body `0.92–1rem` · small/labels `0.62–0.72rem`.
- `font-display: swap`; tamaños en rem; interlineado 1.5–1.75 para lectura.
- **Banned fonts nunca en uso**: Inter, Roboto, Arial, Helvetica, Space Grotesk, Lato, Open Sans, Source Sans Pro. Nota: el CSS del Servicio 1 contenía `Inter` como fallback de sans; se elimina en la migración v1.0 (ver changelog).
- Los eyebrows y labels usan siempre mono, mayúsculas con `letter-spacing`.

## 3. Color system

Fondo base de la marca: papel cálido. Verde profundo institucional como primario. Azul solo para información técnica (Telegram). Todos los pares verificados computacionalmente (WCAG AA, texto 4.5:1 / UI 3:1).

| Token | Hex | Uso | Par verificado | Ratio (AA) |
|---|---|---|---|---|
| `--paper` | `#f4f1e8` | Fondo base de página | `--ink` sobre `--paper` | 14.76:1 ✓ |
| `--paper-2` | `#fbfaf5` | Tarjetas, secciones, superficies elevadas | `--ink-strong` sobre `--paper-2` | 16.41:1 ✓ |
| `--paper-3` | `#ece7dc` | Fondo de página alterno, zonas marcadas | `--slate` sobre `--paper-2` | 7.65:1 ✓ |
| `--ink` | `#17201c` | Texto principal | `--ink` sobre `--paper` | 14.76:1 ✓ |
| `--ink-strong` | `#0d1512` | Títulos, topbar | `--ink-strong` sobre `--paper` | 16.41:1 ✓ |
| `--muted` | `#5d6760` | Texto secundario | `--muted` sobre `--paper` / `--paper-2` | 5.2 / 5.62:1 ✓ |
| `--slate` | `#49534d` | Texto de párrafos | `--slate` sobre `--paper-2` | 7.65:1 ✓ |
| `--green` | `#1d5b43` | Marca, primario, links, estados OK | `--green` sobre `--paper` | 7.07:1 ✓ |
| `--green-strong` | `#123c2d` | Botones primarios, acentos fuertes | `--white` sobre `--green-strong` | 12.28:1 ✓ |
| `--green-soft` | `#dfe9e2` | Fondos de acento verde (UI) | `--green` sobre `--green-soft` | 6.42:1 ✓ |
| `--amber` | `#8b5b16` | Estado "requiere revisión" | `--amber` sobre `--amber-soft` | 4.73:1 ✓ |
| `--amber-soft` | `#f2e7c8` | Fondo del estado amber | — | — |
| `--red` | `#873b34` | Errores, estado faltante | `--red` sobre `--red-soft` | 5.94:1 ✓ |
| `--red-soft` | `#f0ddda` | Fondo de error | — | — |
| `--blue` | `#255e6b` | Info técnica, Telegram (nunca decorativo) | `--blue` sobre `--paper` | 6.43:1 ✓ |
| `--rule` | `#c9c4b7` | Bordes suaves | — | — |
| `--rule-strong` | `#8e978f` | Bordes fuertes, separadores | — | — |
| `--white` | `#fffef9` | Texto sobre verde fuerte | `--white` sobre `--green-strong` | 12.28:1 ✓ |

- Estados (hover, active, focus, disabled) definidos como tokens, no variantes ad hoc.
- Verde neón `#00e676` y paleta dark de la landing anterior quedan **deprecados** (changelog v1.0). El emerald `#059669` queda restringido a UI/gráficos (3.34:1 sobre papel — nunca texto).

## 4. Spacing & layout

- Escala base 4px: `--space-1: .25rem` · `--space-2: .5rem` · `--space-3: .75rem` · `--space-4: 1rem` · `--space-5: 1.5rem` · `--space-6: 2rem` · `--space-7: 3rem` · `--space-8: 4rem`.
- Breakpoints: 640 / 768 / 1024 / 1280 / 1536 px. Mobile-first con `min-width`.
- Contenedor: `min(1120px, 100% - 48px)` (landing) / `min(1120px, 100% - 48px)` (app).
- Radios: 0 (esquinas rectas, lenguaje institucional de papel impreso). Excepción documentada: chips de estado de la landing pueden usar `999px` (badges de plan) — aprobado como detalle menor en v1.0.
- Patrón de composición (break the grid):
  - **Hero**: copy izquierda + panel de evidencia derecha (terminal estilizado como papel de trabajo).
  - **Problemas**: grilla 2 columnas con última card centrada.
  - **Módulos**: grilla 4 columnas con separadores 1px.
  - **Pasos**: timeline vertical mono con números.
  - **FAQ**: 2 columnas asimétricas (340px + 1fr) sticky.
  - **Landing CTA final**: banda verde-soft centrada.
  - **Web Servicio 1**: workspace con rail lateral numerado (01–06) + área de trabajo.

## 5. Components

| Componente | Variantes | Estados | Fuente de verdad |
|---|---|---|---|
| Botón | primary (verde fuerte) / secondary (outline) / ghost | hover / focus / disabled | tokens + CSS |
| Eyebrow | label mono verde con prefijo `PYMIA / ` (app) o punto (landing) | — | CSS |
| Card | panel / alt / featured | hover (border verde, translateY −2px) | CSS |
| Status chip | ready / review / missing | — | CSS |
| Metric | grid 3 col, mono tabular | — | CSS |
| Form field | text / month / file / select | focus-visible (outline ámbar 3px) | CSS |
| Choice card (radio) | checked → border verde + fondo verde-soft | hover / checked / focus | CSS |
| Tabla | th mono uppercase, hover de fila | — | CSS |
| Terminal (hero) | panel de trabajo simulado con filas key/value | — | CSS |
| Trust chips | mono uppercase con dot verde | — | CSS |
| FAQ | `<details>` con flecha mono, open → border verde | open / hover | CSS |

- Cada componente: markup semántico, estados de foco, variantes tokenizadas. Sin variantes improvisadas en el build.

## 6. Imagery & iconography

- Sin fotografía externa. El lenguaje visual es "papel de trabajo": emojis funcionales en tarjetas de problema/módulos (uso existente, no decorativo), barras y figuras CSS en la marca.
- Iconos: emoji funcionales + CSS inline (sin librerías externas). Iconografía de marca: `brand-mark` (3 barras verticales de altura decreciente en verde sobre verde-strong).
- Rutas de assets: `src/` (Astro), `dist/` (build). Formatos: SVG/CSS inline; sin imágenes raster de momento.

## 7. Motion & interaction

- Principio: quiet y con propósito. 150–250 ms, ease-out, solo transform/opacity.
- Permitidos (CSS-only): hover con `translateY(-2px)` en cards, fade-in de hero (`animation .7s both`), rotación de flecha FAQ (`.25s`).
- `prefers-reduced-motion: reduce` obligatorio: ninguna animación esencial para la comprensión; todo se anula.

## 8. Accessibility

- Contraste AA verificado computacionalmente (sección 3).
- Focus visible: `:focus-visible` con outline ámbar 3px (`#bb7a1c`) en app; en landing, outline visible en todos los interactivos.
- Skip link a `#app` / contenido principal; landmarks semánticos (`header`, `nav`, `main`, `section`, `footer`); `lang="es"`.
- Alt text: informativo / decorativo (`alt=""`) según caso. Emojis decorativos con `aria-hidden` donde aplique.
- Formularios con labels; errores descriptivos asociados a campos (`p[role=alert]`).
- Checklist axe sin violaciones críticas en QA.

## 9. Performance & technical

- **Landing**: Astro estático (SSG). Cero JS de runtime (solo `details`/`summary` nativos). Build: `npm run build` en `landing/`.
- **Web Servicio 1**: servidor HTTP nativo Python + htmx 2.0.4 (único JS externo, justificado: intercambio de fragmentos sin recarga). CSS embebido en `_document` (visual_system) — se alinea con los tokens de este documento.
- Budgets: Lighthouse 95+ · LCP < 2.5 s · INP < 200 ms · CLS < 0.1 · TBT < 200 ms.
- Fuentes con `font-display: swap` (sistema, sin webfonts externas salvo justificación).
- SEO: metas por página, `lang`, títulos únicos; sitemap/robots cuando la landing se publique.
- Seguridad: sin secretos en frontend; links externos con `rel="noopener noreferrer"`; el upload de archivos solo por la app (backend Python con sanitización).

## 10. Governanza & changelog

- Cambios al sistema: proponer → aprobar (humano) → registrar aquí → implementar.
- Sin aprobación no se toca el sistema en el código.
- La landing (Astro) y la web del Servicio 1 comparten estos tokens; cualquier cambio se refleja en ambas implementaciones.

| Fecha | Versión | Cambio | Decisión |
|---|---|---|---|
| 2026-08-13 | v1.0 | Sistema inicial aprobado: verde institucional `#1d5b43` sobre papel cálido; deprecados dark `#070b0f` + neón `#00e676` de la landing y navy de prototipos; `--muted` corregido de `#69736d` (4.35:1, fallaba AA) a `#5d6760` (5.2:1); `Inter` eliminado como fallback del Servicio 1 (banned font). | Humano (dirección aprobada en brief) |
| 2026-08-13 | v1.0 | Web Servicio 1: corregidos 5 pares que fallaban AA (`eyebrow::before`, `.rail-disabled`, `.rail-note`, `.choice::before` → `#5d6760`; `.brand-divider` → `#9aa39c`). Landing Astro: `global.css` + 8 componentes migrados de dark a papel/verde. | Implementación |
| 2026-08-13 | v1.0 | **Excepción registrada (regla 6 de design-rules)**: los `<style>` scoped de los componentes Astro conservan media queries `max-width` preexistentes (patrón desktop-first heredado). El `global.css` es mobile-first `min-width`. Refactor completo a `min-width` queda para la tanda v1.1 — requiere aprobación y testeo visual por viewport antes de tocar layout. | Pendiente humano |

---

**Reglas que siempre aplican**: `references/design-rules.md` de la skill `tres-web-design-system`. Ante conflicto entre este documento y las reglas, prevalecen las reglas — y la excepción se registra aquí.