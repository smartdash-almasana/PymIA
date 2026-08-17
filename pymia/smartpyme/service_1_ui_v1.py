from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any, Mapping, Sequence

_MODULE_DIR = Path(__file__).resolve().parent
_TEMPLATE_PATH = _MODULE_DIR / "templates" / "service_1_assisted_web_v1.html"


def _esc(value: object) -> str:
    return escape(str(value if value is not None else ""), quote=True)


def _error(error: str | None) -> str:
    return f'<p class="ui-alert" role="alert">{_esc(error)}</p>' if error else ""


def _format_amount(value: float) -> str:
    return f"{value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def render_document_v1(content: str) -> str:
    template = _TEMPLATE_PATH.read_text(encoding="utf-8")
    shell = (
        '<div class="pymia-app">'
        '<header class="app-header">'
        '<a class="app-brand" href="/" aria-label="PymIA inicio">'
        '<span class="brand-mark" aria-hidden="true"><i></i><i></i><i></i></span>'
        '<span>PYMIA</span></a>'
        '<nav class="app-nav" aria-label="Navegación principal"><a href="/cases">Mis análisis</a></nav>'
        '</header>'
        f'<div class="app-main">{content}</div>'
        '<div class="sr-live" aria-live="polite" aria-atomic="true"></div>'
        '</div>'
    )
    return template.replace("{{content}}", shell)


def render_login_v1(error: str | None = None) -> str:
    return f'''<main id="app" tabindex="-1" class="journey journey--narrow">
      <header class="journey-intro"><p class="kicker">Servicio 1</p><h1>Ingresá a PymIA</h1><p>Accedé a los análisis de tu empresa y a tus resultados anteriores.</p></header>
      {_error(error)}
      <section class="panel form-panel" aria-labelledby="login-title"><h2 id="login-title">Tu cuenta</h2>
        <form action="/login" method="post" class="stack-form">
          <label for="email">Correo electrónico</label><input id="email" name="email" type="email" autocomplete="username" required>
          <label for="password">Contraseña</label><input id="password" name="password" type="password" autocomplete="current-password" required>
          <button type="submit">Ingresar</button>
        </form>
      </section>
    </main>'''


def render_home_v1(
    reconciliation_options: Sequence[tuple[str, str, str]],
    error: str | None = None,
) -> str:
    recon = "".join(
        f'<label class="compact-option"><input type="radio" name="reconciliation_type" value="{_esc(ref)}" required><span><strong>{_esc(name)}</strong><small>{_esc(description)}</small></span></label>'
        for ref, name, description in reconciliation_options
    )
    return f'''<main id="app" tabindex="-1" class="journey">
      <header class="journey-intro"><p class="kicker">Servicio 1</p><h1>Subí tu Excel</h1><p>PymIA primero lee el archivo, después te pide confirmar sólo lo necesario y recién entonces te muestra qué análisis podés pedir sobre esa misma información.</p></header>
      {_error(error)}
      <form action="/upload" method="post" enctype="multipart/form-data" class="analysis-start">
        <section class="upload-panel upload-panel--first" aria-labelledby="upload-title"><div><h2 id="upload-title">Elegí el archivo</h2><p>.xlsx · PymIA no modifica el original.</p></div>
          <input id="file" name="file" type="file" accept=".xlsx" required><button type="submit">Leer mi Excel</button>
        </section>
        <section class="next-step"><h2>Qué pasa después</h2><p><strong>1.</strong> PymIA identifica hojas, columnas y relaciones. <strong>2.</strong> Confirmás las dudas materiales. <strong>3.</strong> Elegís uno, varios o todos los análisis que quieras recibir con esa evidencia.</p></section>
        <details class="optional-context"><summary>Datos opcionales para administradores de consorcios</summary><div class="optional-body">
          <label for="consorcio_id">Código del consorcio</label><input id="consorcio_id" name="consorcio_id" type="text" autocomplete="off">
          <label for="consorcio_name">Nombre del consorcio</label><input id="consorcio_name" name="consorcio_name" type="text" autocomplete="organization">
          <label for="period">Período</label><input id="period" name="period" type="month">
        </div></details>
      </form>
      <details class="secondary-action"><summary>Necesito conciliar dos archivos</summary><div class="secondary-body"><form action="/start-reconciliation" method="post" hx-post="/start-reconciliation" hx-target="#app" hx-swap="outerHTML"><div class="compact-options">{recon}</div><button type="submit">Continuar con conciliación</button></form></div></details>
    </main>'''


def render_analysis_menu_v1(
    launch_options: Sequence[tuple[str, str, str]],
    *,
    filename: str = "",
    error: str | None = None,
) -> str:
    choices = "".join(
        f'''<label class="analysis-option">
          <input type="checkbox" name="review_{_esc(ref)}" value="1">
          <span class="analysis-copy"><strong>{_esc(name)}</strong><span class="analysis-question">{_esc(question)}</span></span>
        </label>'''
        for ref, name, question in launch_options
    )
    file_note = f'<p class="file-read">Archivo leído: <strong>{_esc(filename)}</strong></p>' if filename else ""
    return f'''<main id="app" tabindex="-1" class="journey">{_progress("comprension")}
      <header class="journey-intro"><p class="kicker">Excel entendido</p><h1>¿Qué querés que PymIA te devuelva?</h1><p>Podés elegir uno, varios o todos. Cada análisis usa la misma evidencia confirmada; si para alguno falta un dato material, PymIA lo deja pendiente sin completar nada por suposición.</p>{file_note}</header>
      {_error(error)}
      <form action="/run-review" method="post" class="analysis-start">
        <section class="analysis-list" aria-labelledby="analysis-menu-title"><h2 id="analysis-menu-title">Elegí tus análisis</h2>{choices}</section>
        <div class="sticky-action"><span>La selección define qué capacidades puede ejecutar PymIA sobre este archivo.</span><button type="submit">Preparar análisis seleccionados</button></div>
      </form>
    </main>'''


def render_analysis_bundle_v1(results: Sequence[Mapping[str, Any]]) -> str:
    cards: list[str] = []
    for item in results:
        ready = str(item.get("status") or "") == "READY"
        state_class = "is-ready" if ready else "is-missing"
        state_label = "Resultado listo" if ready else "Análisis pendiente"
        metrics = item.get("metrics") if isinstance(item.get("metrics"), Sequence) and not isinstance(item.get("metrics"), (str, bytes)) else []
        metric_html = "".join(
            f'<div><small>{_esc(metric.get("label"))}</small><strong>{_esc(metric.get("value"))}</strong></div>'
            for metric in metrics if isinstance(metric, Mapping)
        )
        actions = item.get("actions") if isinstance(item.get("actions"), Sequence) and not isinstance(item.get("actions"), (str, bytes)) else []
        action_html = "".join(
            f'<a href="{_esc(action.get("href"))}">{_esc(action.get("label"))}</a>'
            for action in actions if isinstance(action, Mapping)
        )
        details = item.get("details") if isinstance(item.get("details"), Sequence) and not isinstance(item.get("details"), (str, bytes)) else []
        details_html = "".join(f'<li>{_esc(detail)}</li>' for detail in details)
        cards.append(f'''<section class="analysis-result-card"><header><div><p class="kicker">{_esc(item.get("title"))}</p><h2>{_esc(item.get("headline"))}</h2></div><span class="result-state {state_class}">{state_label}</span></header>{f'<div class="metric-row">{metric_html}</div>' if metric_html else ''}<p>{_esc(item.get("summary"))}</p>{f'<details><summary>Datos utilizados</summary><div class="details-body"><ul>{details_html}</ul></div></details>' if details_html else ''}{f'<div class="result-actions">{action_html}</div>' if action_html else ''}</section>''')
    return f'''<main id="app" tabindex="-1" class="journey">{_progress("resultado")}<header class="journey-intro"><p class="kicker">Devolución del Excel</p><h1>Tus análisis</h1><p>Resultados obtenidos únicamente con la evidencia confirmada del archivo.</p></header>{''.join(cards)}<div class="result-actions"><a class="secondary" href="/">Analizar otro Excel</a><a class="secondary" href="/cases">Mis análisis</a></div></main>'''


def _progress(current: str) -> str:
    steps = (("archivo", "Archivo"), ("comprension", "Comprensión y elección"), ("resultado", "Resultado"))
    current_index = [key for key, _ in steps].index(current)
    items = []
    for index, (key, label) in enumerate(steps):
        cls = "is-current" if index == current_index else ("is-done" if index < current_index else "")
        items.append(f'<li class="{cls}"><span>{index + 1}</span>{label}</li>')
    return f'<ol class="journey-progress" aria-label="Progreso">{"".join(items)}</ol>'


def _sample_values(ingestion_output: Mapping[str, Any] | None, sheet_ref: str, column_ref: str, limit: int = 8) -> list[str]:
    if not isinstance(ingestion_output, Mapping):
        return []
    evidence = ingestion_output.get("column_evidence")
    if isinstance(evidence, Mapping):
        for item in evidence.values():
            if not isinstance(item, Mapping):
                continue
            if str(item.get("sheet_name") or "").strip() == sheet_ref and str(item.get("column_name") or "").strip() == column_ref:
                values = item.get("sample_values")
                if isinstance(values, list):
                    seen: list[str] = []
                    for value in values:
                        if value is None or (isinstance(value, str) and not value.strip()):
                            continue
                        text = str(value)
                        if text not in seen:
                            seen.append(text)
                        if len(seen) >= limit:
                            break
                    return seen
    tables = ingestion_output.get("normalized_tables")
    if not isinstance(tables, list):
        return []
    seen: list[str] = []
    for table in tables:
        if not isinstance(table, Mapping) or str(table.get("sheet_name") or "").strip() != sheet_ref:
            continue
        headers = [str(v or "").strip() for v in (table.get("headers") or [])]
        normalized = [str(v or "").strip() for v in (table.get("normalized_headers") or [])]
        candidates = [column_ref]
        if column_ref in headers:
            idx = headers.index(column_ref)
            if idx < len(normalized) and normalized[idx]:
                candidates.insert(0, normalized[idx])
        for row in table.get("rows") or []:
            if not isinstance(row, Mapping):
                continue
            key = next((candidate for candidate in candidates if candidate in row), None)
            if key is None:
                continue
            value = row.get(key)
            if value is None or (isinstance(value, str) and not value.strip()):
                continue
            text = str(value)
            if text not in seen:
                seen.append(text)
            if len(seen) >= limit:
                return seen
    return seen


def render_semantic_questions_v1(questions: list[dict[str, Any]], error: str | None = None, *, selected_answers: dict[str, Any] | None = None) -> str:
    selected_answers = selected_answers or {}
    cards = []
    for question in questions:
        raw_id = str(question.get("question_id") or "")
        qid = _esc(raw_id)
        previous = selected_answers.get(raw_id)
        previous_option = str(previous.get("option_id") if isinstance(previous, dict) else previous or "").strip()
        previous_other = str(previous.get("free_text") if isinstance(previous, dict) else "").strip()
        options = [item for item in (question.get("options") or []) if isinstance(item, dict)]
        proposed = next((item for item in options if str(item.get("option_id") or "").strip() not in {"OTHER", "IGNORE"}), None)
        option_html = "".join(f'<option name="answer_{qid}" value="{_esc(item.get("option_id"))}"{" selected" if str(item.get("option_id") or "").strip() == previous_option else ""}>{_esc(item.get("label"))}</option>' for item in options)
        proposal = f'<p class="proposal">PymIA entiende que es <strong>{_esc(proposed.get("label"))}</strong>.</p>' if proposed else ""
        memory_hint = str(question.get("tenant_memory_hint") or "").strip()
        memory_note = (
            f'<p class="memory-note">La vez anterior confirmaste: <strong>{_esc(memory_hint)}</strong>. Lo muestro como antecedente; no completo la respuesta por vos.</p>'
            if memory_hint else ""
        )
        cards.append(f'''<section class="understanding-card">
          <div class="found-data"><small>Encontré</small><strong>{_esc(question.get("column_name") or "Columna")}</strong><span>Hoja {_esc(question.get("sheet_name") or "Hoja")}</span><p>{_esc(question.get("context") or "")}</p></div>
          <div class="confirm-data"><small>Necesito confirmar</small>{proposal}{memory_note}<label for="answer_{qid}">¿Qué significa este dato?</label>
            <select id="answer_{qid}" name="answer_{qid}" required><option value="" disabled{" selected" if not previous_option else ""}>Elegir significado</option>{option_html}<option value="not_sure"{" selected" if previous_option == "not_sure" else ""}>No lo puedo confirmar ahora</option></select>
            <input id="other_{qid}" name="other_{qid}" type="text" value="{_esc(previous_other)}" placeholder="Otra interpretación, si corresponde">
          </div></section>''')
    return f'''<main id="app" tabindex="-1" class="journey">{_progress("comprension")}
      <header class="journey-intro"><p class="kicker">Esto entendí de tu Excel</p><h1>Antes de calcular, confirmemos {len(cards)} {"dato" if len(cards) == 1 else "datos"}</h1><p>Te muestro únicamente lo que puede cambiar el resultado. Si algo no es claro, podés dejarlo pendiente.</p></header>
      {_error(error)}<form class="understanding-form" action="/confirm-meanings" method="post">{''.join(cards)}<div class="sticky-action"><span>Con tus confirmaciones PymIA vuelve al cálculo determinístico.</span><button type="submit">Continuar al resultado</button></div></form>
    </main>'''


def _friendly_ref(value: object) -> str:
    raw = str(value or "").strip()
    if not raw:
        return "Dato del Excel"
    if "->" in raw:
        left, right = raw.split("->", 1)
        return f"{_friendly_ref(left)} ↔ {_friendly_ref(right)}"
    if "." in raw:
        sheet, column = raw.split(".", 1)
        return f"{column} · hoja {sheet}"
    return raw.replace("_", " ")


def render_semantic_dialogue_v1(decisions: list[dict[str, Any]], error: str | None = None, *, selected_actions: dict[str, str] | None = None) -> str:
    selected_actions = selected_actions or {}
    cards = []
    progress_html = ""
    for decision in decisions:
        if not isinstance(decision, Mapping):
            continue
        did = str(decision.get("decision_id") or "").strip()
        if not did:
            continue
        refs = [_friendly_ref(ref) for ref in list(decision.get("column_refs") or []) + list(decision.get("relationship_refs") or []) if str(ref).strip()]
        selected = selected_actions.get(did, "")
        reason = str(decision.get("assistant_rationale") or decision.get("materiality_reason") or "").strip()
        current = int(decision.get("progress_current") or 1)
        total = max(int(decision.get("progress_total") or 1), 1)
        completed = max(int(decision.get("progress_completed") or 0), 0)
        pct = min(100, max(0, round((completed / total) * 100)))
        progress_html = f'''<section aria-label="Progreso de comprensión" style="margin:0 0 1.25rem"><div style="display:flex;justify-content:space-between;gap:1rem;margin-bottom:.45rem"><strong>Columna {current} de {total}</strong><span>{pct}% confirmado</span></div><div style="height:8px;border-radius:999px;background:#e7edf4;overflow:hidden"><div style="height:100%;width:{pct}%;background:currentColor;opacity:.65"></div></div></section>'''
        samples = list(decision.get("sample_values") or [])[:5]
        sample_html = "".join(f'<code>{_esc(value)}</code>' for value in samples) or '<span class="empty-sample">Sin ejemplos visibles</span>'
        sheet = str(decision.get("sheet_name") or "").strip()
        column = str(decision.get("column_name") or "").strip()
        role = str(decision.get("proposed_semantic_role") or "").strip().replace("_", " ")
        variable = str(decision.get("proposed_variable_name") or "").strip()
        proposal_meta = ""
        if role or variable:
            proposal_meta = f'<p><small>Interpretación técnica</small><br><strong>{_esc(role or "sin rol")}</strong>{f" · {_esc(variable)}" if variable else ""}</p>'
        chat_rows = []
        for message in decision.get("chat_messages") or []:
            if not isinstance(message, Mapping):
                continue
            who = "Vos" if str(message.get("role") or "") == "owner" else "PymIA"
            chat_rows.append(f'<div class="chat-row"><strong>{_esc(who)}:</strong> {_esc(message.get("text") or "")}</div>')
        chat_history = "".join(chat_rows)
        suggestion = decision.get("chat_suggestion") if isinstance(decision.get("chat_suggestion"), Mapping) else {}
        suggested_role = str(suggestion.get("semantic_role") or "").strip()
        suggested_variable = str(suggestion.get("variable_name") or "").strip()
        suggestion_html = ""
        if suggested_role and suggested_variable:
            suggestion_html = f'''<div class="semantic-suggestion"><small>Propuesta revisada</small><p>PymIA entendió tu explicación como <strong>{_esc(suggested_role.replace("_", " "))}</strong> · <code>{_esc(suggested_variable)}</code>.</p><p>Esto todavía no está confirmado.</p><button type="submit" formaction="/semantic-revise" formmethod="post" formnovalidate>Usar esta propuesta y revisarla</button></div>'''
        raw_column_refs = [str(ref).strip() for ref in (decision.get("column_refs") or []) if str(ref).strip()]
        raw_relationship_refs = [str(ref).strip() for ref in (decision.get("relationship_refs") or []) if str(ref).strip()]
        skip_option_html = ""
        if len(raw_column_refs) == 1 and not raw_relationship_refs:
            skip_option_html = f'<label><input type="radio" name="action_{_esc(did)}" value="SKIP"{" checked" if selected == "SKIP" else ""}>No tomes en cuenta esta columna para el análisis que necesito</label>'
        cards.append(f'''<section class="understanding-card semantic-transaction"><div class="found-data"><small>Columna actual</small><strong>{_esc(column or " · ".join(refs) or did)}</strong>{f'<span>Hoja {_esc(sheet)}</span>' if sheet else ''}<p class="sample-label">Ejemplos del archivo</p><div class="sample-values">{sample_html}</div><p>La resolvemos ahora y después seguimos con la siguiente.</p></div>
          <div class="confirm-data"><small>Propuesta de PymIA</small><p class="question-text">{_esc(decision.get("presentation_text") or "")}</p>{proposal_meta}
          <div class="radio-stack"><label><input type="radio" name="action_{_esc(did)}" value="ACCEPT" required{" checked" if selected == "ACCEPT" else ""}>Sí, es correcto: eso significa</label><label><input type="radio" name="action_{_esc(did)}" value="REJECT"{" checked" if selected == "REJECT" else ""}>No, no significa eso</label><label><input type="radio" name="action_{_esc(did)}" value="CORRECT"{" checked" if selected == "CORRECT" else ""}>Quiero explicarlo con mis palabras</label>{skip_option_html}</div>
          <label for="correction_{_esc(did)}">Corrección, si hace falta</label><input id="correction_{_esc(did)}" type="text" name="correction_{_esc(did)}" placeholder="Ej.: es el precio de lista antes del descuento">
          <details class="semantic-assistant"{" open" if chat_history or suggestion_html else ""}><summary>💬 Preguntarle a PymIA sobre esta columna</summary><div class="details-body"><p>{_esc(reason or "PymIA usa nombre, tipo, ejemplos y contexto de la hoja. Puede explicarte la propuesta, pero no confirmarla por vos.")}</p>{chat_history}{suggestion_html}<input type="hidden" name="decision_id" value="{_esc(did)}"><label for="assistant_message_{_esc(did)}">Escribí una duda o explicá qué representa</label><textarea id="assistant_message_{_esc(did)}" name="assistant_message" rows="3" placeholder="Ej.: esto no es precio final, es la lista antes del descuento"></textarea><button type="submit" formaction="/semantic-assist" formmethod="post" formnovalidate>Enviar al asistente</button></div></details></div></section>''')
    return f'''<main id="app" tabindex="-1" class="journey">{_progress("comprension")}<header class="journey-intro"><p class="kicker">Esto entendí de tu Excel</p><h1>Una columna por vez</h1><p>PymIA propone. Vos confirmás, corregís o preguntás. El significado recién se vuelve evidencia cuando vos lo confirmás.</p></header>{progress_html}{_error(error)}<form action="/confirm-meanings" method="post" class="understanding-form">{''.join(cards)}<div class="sticky-action"><span>Tu respuesta queda guardada en esta sesión y avanzamos a la siguiente columna.</span><button type="submit">Guardar y seguir</button></div></form></main>'''


def render_unit_questions_v1(questions: list[dict[str, Any]], error: str | None = None, *, selected_units: dict[str, str] | None = None, ingestion_output: Mapping[str, Any] | None = None) -> str:
    selected_units = selected_units or {}
    unit_copy = {
        "DISCOUNT_FRACTION_0_1": ("Porcentaje escrito como decimal", "0,10 significa 10%"),
        "DISCOUNT_PERCENT_0_100": ("Porcentaje escrito como número", "10 significa 10%"),
        "DISCOUNT_LINE_AMOUNT": ("Importe de dinero", "10 significa $10 descontados"),
    }
    cards = []
    for question in questions:
        if not isinstance(question, Mapping) or question.get("question_kind") != "UNIT_MEANING":
            continue
        qid = str(question.get("question_id") or "").strip(); sheet = str(question.get("sheet_ref") or "").strip(); column = str(question.get("column_ref") or "").strip(); selected = selected_units.get(qid, "")
        samples = _sample_values(ingestion_output, sheet, column)
        sample_html = ''.join(f'<code>{_esc(value)}</code>' for value in samples) or '<span class="empty-sample">Sin valores visibles</span>'
        options = []
        for option in question.get("options") or []:
            if not isinstance(option, Mapping):
                continue
            kind = str(option.get("unit_kind") or "").strip(); label, example = unit_copy.get(kind, (str(option.get("label") or ""), str(option.get("example") or "")))
            options.append(f'<label><input type="radio" name="unit_{_esc(qid)}" value="{_esc(kind)}" required{" checked" if selected == kind else ""}><span><strong>{_esc(label)}</strong><small>{_esc(example)}</small></span></label>')
        options.append(f'<label><input type="radio" name="unit_{_esc(qid)}" value="not_sure" required{" checked" if selected == "not_sure" else ""}><span><strong>No lo puedo confirmar ahora</strong><small>El análisis queda pendiente; PymIA no inventa una unidad.</small></span></label>')
        cards.append(f'''<section class="understanding-card"><div class="found-data"><small>Encontré</small><strong>{_esc(column)}</strong><span>Hoja {_esc(sheet)}</span><p class="sample-label">Valores que encontré en esta columna</p><div class="sample-values">{sample_html}</div></div><div class="confirm-data"><small>Necesito confirmar</small><p class="question-text">¿Cómo están guardados estos descuentos?</p><div class="radio-stack">{''.join(options)}</div></div></section>''')
    return f'''<main id="app" tabindex="-1" class="journey">{_progress("comprension")}<header class="journey-intro"><p class="kicker">Esto entendí de tu Excel</p><h1>Confirmemos el descuento</h1><p>Te muestro valores reales del archivo para que puedas reconocer cómo está expresado.</p></header>{_error(error)}<form action="/confirm-meanings" method="post" class="understanding-form">{''.join(cards)}<div class="sticky-action"><span>Sólo usamos una unidad que hayas confirmado.</span><button type="submit">Continuar al resultado</button></div></form></main>'''


def render_unit_deferred_v1(questions: list[dict[str, Any]]) -> str:
    refs = [f"{str(q.get('column_ref') or '').strip()} · hoja {str(q.get('sheet_ref') or '').strip()}" for q in questions if isinstance(q, Mapping) and q.get("question_kind") == "UNIT_MEANING"]
    return f'''<main id="app" tabindex="-1" class="journey">{_progress("comprension")}<header class="journey-intro"><p class="kicker">Análisis pendiente</p><h1>Necesito una confirmación para continuar</h1><p>No voy a suponer cómo está expresado el descuento.</p></header><section class="needs-data"><h2>Dato pendiente</h2><p><strong>{_esc(" · ".join(refs) or "Unidad del descuento")}</strong></p><p>Cuando puedas verificarlo, volvé a analizar el archivo.</p><p>No generé ningún cálculo con este dato pendiente.</p></section><div class="result-actions"><a href="/">Revisar otro Excel</a><a class="secondary" href="/cases">Mis análisis</a></div></main>'''


def render_margin_result_v1(*, title: str, value: object, unit: object, finding: object, data_html: str, limitations: Sequence[object], download_html: str) -> str:
    limits = ''.join(f'<li>{_esc(item)}</li>' for item in limitations)
    return f'''<main id="app" tabindex="-1" class="journey">{_progress("resultado")}<header class="result-header"><div><p class="kicker">Resultado</p><h1>{_esc(title)}</h1><p>Calculado con los datos que PymIA encontró y vos confirmaste.</p></div><span class="result-state is-ready">Resultado listo</span></header><section class="primary-result"><h2>Tu resultado</h2><p class="primary-value">{_esc(value)} {_esc(unit)}</p><p>{_esc(finding)}</p></section><details><summary>Datos utilizados</summary><div class="details-body">{data_html}</div></details><details><summary>Qué conviene tener en cuenta</summary><div class="details-body"><p>Este resultado surge de los datos confirmados y no atribuye automáticamente causas.</p><ul>{limits}</ul></div></details><div class="result-actions">{download_html}<a class="secondary" href="/">Analizar otro Excel</a><a class="secondary" href="/cases">Mis análisis</a></div></main>'''


def render_sales_collections_result_v1(*, sold: float, collected: float, gap: float, ratio_text: str, finding: str, classification_label: str, source_rows: str, filename: str, period_text: str, limitations: Sequence[object], download_html: str) -> str:
    state = "Hay una diferencia" if gap != 0 else "Sin diferencias"
    cls = "is-review" if gap != 0 else "is-ready"
    limits = ''.join(f'<li>{_esc(item)}</li>' for item in limitations)
    return f'''<main id="app" tabindex="-1" class="journey">{_progress("resultado")}<header class="result-header"><div><p class="kicker">Resultado</p><h1>Ventas y cobranzas</h1><p>Comparación entre lo vendido y lo cobrado en los registros analizados.</p></div><span class="result-state {cls}">{state}</span></header><section class="metric-row"><div><small>Total vendido</small><strong>{_esc(_format_amount(sold))}</strong></div><div><small>Total cobrado</small><strong>{_esc(_format_amount(collected))}</strong></div><div class="metric-focus"><small>Diferencia</small><strong>{_esc(_format_amount(gap))}</strong></div></section><section class="primary-result"><h2>Qué significa</h2><p><strong>{_esc(finding)}</strong></p><p>Porcentaje cobrado: <strong>{_esc(ratio_text)}</strong>. {_esc(classification_label)}.</p></section><details><summary>Datos utilizados</summary><div class="details-body"><p>Archivo: <strong>{_esc(filename or 'archivo recibido')}</strong></p><ul>{source_rows or '<li>Columnas confirmadas del archivo recibido.</li>'}</ul><p>Período: {_esc(period_text)}</p></div></details><details><summary>Qué conviene tener en cuenta</summary><div class="details-body"><ul>{limits}</ul><p>La diferencia surge de los registros recibidos y no determina por sí sola la causa.</p></div></details><div class="result-actions">{download_html}<a class="secondary" href="/">Analizar otro Excel</a><a class="secondary" href="/cases">Mis análisis</a></div></main>'''


def render_cash_flow_result_v1(packet: dict[str, Any]) -> str:
    components = packet.get("computed_components") if isinstance(packet.get("computed_components"), dict) else {}
    cash = components.get("projected_closing_cash_balance") if isinstance(components.get("projected_closing_cash_balance"), dict) else {}
    dso = components.get("dso") if isinstance(components.get("dso"), dict) else {}
    ratio = components.get("current_ratio") if isinstance(components.get("current_ratio"), dict) else {}
    cash_value = (cash.get("computed") or {}).get("projected_closing_balance") if isinstance(cash.get("computed"), dict) else None
    dso_value = (dso.get("computed") or {}).get("dso_days") if isinstance(dso.get("computed"), dict) else None
    ratio_value = (ratio.get("computed") or {}).get("current_ratio_value") if isinstance(ratio.get("computed"), dict) else None
    if cash_value is None:
        return f'''<main id="app" tabindex="-1" class="journey">{_progress("resultado")}<header class="result-header"><div><p class="kicker">Flujo de caja</p><h1>Necesito un dato más</h1><p>No pude proyectar el saldo de caja sin saldo inicial, cobros previstos y pagos previstos.</p></div><span class="result-state is-missing">Análisis pendiente</span></header><section class="needs-data"><h2>Para continuar</h2><p>Tu Excel debería incluir saldo inicial, cobros o ingresos previstos y pagos o egresos previstos.</p></section><div class="result-actions"><a href="/">Revisar otro Excel</a><a class="secondary" href="/cases">Mis análisis</a></div></main>'''
    optional = []
    if dso_value is not None:
        optional.append(f'<div><small>Tiempo promedio de cobro</small><strong>{_esc(dso_value)} días</strong></div>')
    if ratio_value is not None:
        optional.append(f'<div><small>Cobertura de corto plazo</small><strong>{_esc(ratio_value)}</strong></div>')
    expansion = []
    if dso_value is None:
        expansion.append('<li><strong>Tiempo promedio de cobro:</strong> cuentas por cobrar, ventas del período y cantidad de días.</li>')
    if ratio_value is None:
        expansion.append('<li><strong>Cobertura de corto plazo:</strong> activo corriente y pasivo corriente.</li>')
    optional_html = f'<section class="metric-row metric-row--optional">{"".join(optional)}</section>' if optional else ''
    expansion_html = f'<details open><summary>Podés ampliar este análisis</summary><div class="details-body"><p>Estos datos no son necesarios para proyectar tu saldo de caja.</p><ul>{"".join(expansion)}</ul></div></details>' if expansion else ''
    return f'''<main id="app" tabindex="-1" class="journey">{_progress("resultado")}<header class="result-header"><div><p class="kicker">Resultado</p><h1>Flujo de caja</h1><p>Proyección realizada con el saldo inicial, los cobros previstos y los pagos previstos de tu Excel.</p></div><span class="result-state is-ready">Resultado listo</span></header><section class="primary-result"><h2>Saldo de caja proyectado</h2><p class="primary-value">{_esc(_format_amount(float(cash_value)))}</p><p>Este sería el saldo al cierre del período analizado según los importes informados.</p></section>{optional_html}{expansion_html}<details><summary>Qué conviene tener en cuenta</summary><div class="details-body"><p>El saldo proyectado no explica por sí solo la causa de un faltante o excedente de caja ni reemplaza una decisión profesional.</p></div></details><div class="result-actions"><a class="secondary" href="/">Analizar otro Excel</a><a class="secondary" href="/cases">Mis análisis</a></div></main>'''


def render_blocked_result_v1(*, title: str, evidence_html: str, next_step: str) -> str:
    return f'''<main id="app" tabindex="-1" class="journey">{_progress("resultado")}<header class="result-header"><div><p class="kicker">Necesito un dato más</p><h1>Todavía no puedo completar {_esc(title)}</h1><p>No completo valores por suposición. Lo que ya confirmaste queda disponible para retomar el análisis.</p></div><span class="result-state is-missing">Análisis pendiente</span></header><section class="needs-data"><h2>Qué falta</h2>{evidence_html}</section><section class="next-step"><h2>Cómo seguir</h2><p><strong>{_esc(next_step)}</strong></p><div class="result-actions"><a href="/">Revisar o subir otro Excel</a><a class="secondary" href="/cases">Mis análisis</a></div></section></main>'''


def render_recent_analyses_v1(snapshots: list[dict[str, Any]]) -> str:
    if not snapshots:
        return '''<main id="app" tabindex="-1" class="journey"><header class="journey-intro"><p class="kicker">Historial</p><h1>Mis análisis</h1><p>Acá vas a encontrar los análisis que puedas volver a abrir.</p></header><section class="empty-state"><h2>Todavía no hay análisis para mostrar</h2><p>Empezá con un Excel y el resultado aparecerá acá cuando corresponda.</p><div class="result-actions"><a href="/">Nuevo análisis</a></div></section></main>'''
    rows = "".join(
        f'''<tr><td><strong>{_esc(item.get("service_name"))}</strong></td><td><span class="history-state">{_esc(item.get("status"))}</span></td><td>{_esc(item.get("updated_at"))}</td><td><a href="/case?case_ref={_esc(item.get("case_ref"))}">Abrir</a></td></tr>'''
        for item in snapshots
    )
    return f'''<main id="app" tabindex="-1" class="journey"><header class="result-header"><div><p class="kicker">Historial</p><h1>Mis análisis</h1><p>Volvé a consultar resultados y casos que siguen disponibles.</p></div><a class="header-action" href="/">Nuevo análisis</a></header><section class="history-panel"><div class="table-wrap"><table><thead><tr><th>Análisis</th><th>Estado</th><th>Actualizado</th><th></th></tr></thead><tbody>{rows}</tbody></table></div></section></main>'''


def render_persisted_analysis_v1(case: dict[str, Any]) -> str:
    evidence = case.get("evidence") if isinstance(case.get("evidence"), list) else []
    rows = "".join(
        f'''<tr><td>{_esc(item.get("sheet_ref"))}</td><td>{_esc(item.get("column_ref"))}</td><td>{_esc(item.get("owner_answer"))}</td><td>{_esc(item.get("confirmed_at"))}</td></tr>'''
        for item in evidence if isinstance(item, dict)
    )
    return f'''<main id="app" tabindex="-1" class="journey"><header class="result-header"><div><p class="kicker">Análisis guardado</p><h1>Datos que confirmaste</h1><p>PymIA conserva estas confirmaciones para este caso y no las reemplaza por una interpretación automática.</p></div><a class="header-action" href="/cases">Volver a Mis análisis</a></header><section class="primary-result"><h2>Archivo</h2><p><strong>{_esc(case.get("workbook_ref") or "Archivo recibido")}</strong></p></section><section class="history-panel"><h2>Confirmaciones guardadas</h2><div class="table-wrap"><table><thead><tr><th>Hoja</th><th>Columna</th><th>Qué confirmaste</th><th>Fecha</th></tr></thead><tbody>{rows}</tbody></table></div></section><details><summary>Información técnica del caso</summary><div class="details-body"><p>Identificador: <code>{_esc(case.get("case_id"))}</code></p><p>Tenant: <code>{_esc(case.get("tenant_id"))}</code></p></div></details><section class="needs-data"><h2>Sobre este historial</h2><p>Las confirmaciones son durables. Un resultado completo o su archivo descargable sólo puede reabrirse cuando el snapshot de ejecución correspondiente sigue disponible.</p></section></main>'''


def render_reconciliation_upload_v1(title: str, description: str, source_specs: Sequence[tuple[str, str, object]], error: str | None = None) -> str:
    fields = "".join(
        f'''<label class="recon-source" for="source_{_esc(kind)}"><span><strong>{_esc(label)}</strong><small>Excel .xlsx</small></span><input id="source_{_esc(kind)}" name="source_{_esc(kind)}" type="file" accept=".xlsx" required></label>'''
        for kind, label, _ in source_specs
    )
    return f'''<main id="app" tabindex="-1" class="journey">{_progress("archivo")}<header class="journey-intro"><p class="kicker">Conciliación</p><h1>{_esc(title)}</h1><p>{_esc(description)}</p></header>{_error(error)}<section class="reconciliation-step"><h2>Subí las dos fuentes</h2><p>PymIA necesita ambos archivos para buscar coincidencias y diferencias. No modifica los originales.</p><form action="/upload-reconciliation" method="post" enctype="multipart/form-data" hx-post="/upload-reconciliation" hx-target="#app" hx-swap="outerHTML" class="recon-upload-grid">{fields}<div class="recon-action"><button type="submit">Leer los archivos</button></div></form></section></main>'''


def render_reconciliation_confirmation_v1(title: str, source_specs: Sequence[tuple[str, str, Sequence[tuple[str, str]]]], intakes: Mapping[str, Mapping[str, Any]], error: str | None = None) -> str:
    blocks = []
    for source_kind, source_label, field_specs in source_specs:
        intake = intakes[source_kind]
        columns = [str(item) for item in (intake.get("columns") or [])]
        selectors = []
        for canonical_field, field_label in field_specs:
            options = '<option value="">Elegí una columna</option>' + ''.join(f'<option value="{_esc(column)}">{_esc(column)}</option>' for column in columns)
            selectors.append(f'<label>{_esc(field_label)}<select name="bind_{_esc(source_kind)}_{_esc(canonical_field)}" required>{options}</select></label>')
        blocks.append(f'''<section class="recon-source-map"><header><small>{_esc(source_label)}</small><strong>{_esc(intake.get("filename"))}</strong></header><p>Decinos qué columna representa cada dato necesario para el cruce.</p><div class="mapping-grid">{''.join(selectors)}</div></section>''')
    return f'''<main id="app" tabindex="-1" class="journey">{_progress("comprension")}<header class="journey-intro"><p class="kicker">Esto entendí de tus archivos</p><h1>Confirmemos cómo cruzar { _esc(title.lower()) }</h1><p>Mostramos sólo las columnas necesarias para comparar los movimientos. PymIA no las elige en silencio.</p></header>{_error(error)}<form action="/confirm-reconciliation-columns" method="post" hx-post="/confirm-reconciliation-columns" hx-target="#app" hx-swap="outerHTML" class="understanding-form">{''.join(blocks)}<div class="sticky-action"><span>Después de confirmar las columnas, PymIA prepara los casos para revisión humana.</span><button type="submit">Cruzar movimientos</button></div></form></main>'''


def render_reconciliation_result_v1(*, title: str, status_note: str, decision_count: int, summary_rows: str, details_html: str, radar_html: str = "", notice: str | None = None, error: str | None = None) -> str:
    return f'''<main id="app" tabindex="-1" class="journey">{_progress("resultado")}<header class="result-header"><div><p class="kicker">Resultado de conciliación</p><h1>{_esc(title)}</h1><p>{_esc(status_note)}</p></div><span class="result-state is-review">Revisión humana</span></header>{_error(error)}{f'<p class="ui-note">{_esc(notice)}</p>' if notice else ''}<section class="reconciliation-summary"><h2>Resumen del cruce</h2><p>Decisiones registradas en esta revisión: <strong>{decision_count}</strong>.</p><div class="table-wrap"><table><tbody>{summary_rows}</tbody></table></div></section>{radar_html}<section class="reconciliation-review"><h2>Casos para revisar</h2><p>PymIA propone coincidencias y diferencias; una persona decide qué confirmar, rechazar o dejar pendiente.</p>{details_html}</section><details open><summary>Límites de este resultado</summary><div class="details-body"><p>PymIA no marca movimientos como conciliados automáticamente, no modifica los archivos y no realiza un cierre contable.</p></div></details><div class="result-actions"><a href="/download-reconciliation-workpaper">Descargar papel de trabajo (.xlsx)</a><a class="secondary" href="/">Nuevo análisis</a><a class="secondary" href="/cases">Mis análisis</a></div></main>'''
