from __future__ import annotations

from pathlib import Path

OUTPUT_FILE = Path(__file__).with_name("servicio1-sandbox.html")

SERVICE1_SANDBOX_HTML = r'''<!DOCTYPE html>
<html lang="es-AR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>PymIA Servicio 1 — Sandbox XLSX</title>
  <meta name="description" content="Sandbox local para ensayar Servicio 1: carga XLSX en navegador, preview de hojas, preguntas al dueño y exportación de respuestas. No procesa datos en servidor." />
  <script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
  <style>
    :root {
      --bg: #07111f; --panel: #0e1b2f; --card: #ffffff; --ink: #0c1726;
      --muted: #697586; --line: #d9e2ef; --brand: #1e66ff; --ok: #10b981;
      --warn: #f59e0b; --danger: #ef4444; --soft: #f6f8fb; --radius: 18px;
      --shadow: 0 18px 60px rgba(7, 17, 31, .16);
    }
    * { box-sizing: border-box; }
    body { margin: 0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: var(--ink); background: var(--soft); line-height: 1.5; }
    .shell { min-height: 100vh; display: grid; grid-template-rows: auto 1fr; }
    header { background: rgba(7, 17, 31, .96); color: white; border-bottom: 1px solid rgba(255,255,255,.10); position: sticky; top: 0; z-index: 20; }
    .nav { width: min(1220px, calc(100% - 32px)); margin: 0 auto; min-height: 68px; display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 10px 0; }
    .brand { display: flex; gap: 10px; align-items: center; font-weight: 900; letter-spacing: -.03em; }
    .logo { width: 36px; height: 36px; border-radius: 12px; display: grid; place-items: center; background: linear-gradient(135deg, var(--brand), #00c2a8); }
    .env-badge { display: inline-flex; align-items: center; gap: 8px; padding: 8px 12px; border-radius: 999px; background: rgba(245, 158, 11, .14); border: 1px solid rgba(245, 158, 11, .36); color: #fde68a; font-weight: 800; font-size: 13px; white-space: nowrap; }
    main { width: min(1220px, calc(100% - 32px)); margin: 0 auto; padding: 28px 0 60px; }
    .hero { display: grid; grid-template-columns: 1.1fr .9fr; gap: 22px; align-items: stretch; margin-bottom: 22px; }
    .hero-card, .guard-card, .panel, .chat-panel { background: white; border: 1px solid var(--line); border-radius: var(--radius); box-shadow: var(--shadow); }
    .hero-card { padding: 28px; }
    .hero-card h1 { margin: 0 0 12px; font-size: clamp(34px, 4.8vw, 58px); line-height: .96; letter-spacing: -.06em; }
    .hero-card p { color: var(--muted); font-size: 18px; max-width: 820px; }
    .flags { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 18px; }
    .flag { padding: 8px 10px; border-radius: 999px; background: #eef5ff; color: #144fbb; font-weight: 800; font-size: 13px; }
    .guard-card { padding: 22px; border-left: 5px solid var(--warn); }
    .guard-card h2 { margin: 0 0 10px; font-size: 22px; }
    .guard-card ul { margin: 12px 0 0; padding-left: 20px; color: var(--muted); }
    .checks { display: grid; gap: 10px; margin-top: 16px; }
    label.check { display: flex; align-items: flex-start; gap: 10px; color: var(--ink); font-weight: 750; }
    label.check input { margin-top: 4px; width: 18px; height: 18px; }
    .grid { display: grid; grid-template-columns: minmax(0, 1fr) 380px; gap: 22px; align-items: start; }
    .panel { overflow: hidden; }
    .panel-head { padding: 18px 20px; background: var(--panel); color: white; display: flex; justify-content: space-between; align-items: center; gap: 12px; }
    .panel-head h2 { margin: 0; font-size: 18px; }
    .panel-body { padding: 20px; }
    .upload { border: 2px dashed #bfd0e8; border-radius: 18px; padding: 26px; background: #f8fbff; text-align: center; transition: .15s ease; }
    .upload.dragover { border-color: var(--brand); background: #eef5ff; }
    .upload strong { display: block; font-size: 20px; margin-bottom: 8px; }
    .upload p { margin: 0 0 16px; color: var(--muted); }
    .btn { appearance: none; border: 0; border-radius: 12px; padding: 12px 16px; background: var(--brand); color: white; font-weight: 900; cursor: pointer; display: inline-flex; justify-content: center; align-items: center; gap: 8px; text-decoration: none; }
    .btn.secondary { background: #e9eef8; color: var(--ink); }
    .btn.warning { background: var(--warn); color: #221400; }
    .btn:disabled { opacity: .45; cursor: not-allowed; }
    .hidden { display: none !important; }
    .meta { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 16px; }
    .meta-card { border: 1px solid var(--line); border-radius: 14px; padding: 12px; background: white; }
    .meta-card b { display: block; font-size: 13px; color: var(--muted); }
    .meta-card span { font-weight: 900; }
    .tabs { display: flex; flex-wrap: wrap; gap: 8px; margin: 18px 0; }
    .tab { border: 1px solid var(--line); background: white; color: var(--ink); border-radius: 999px; padding: 9px 12px; font-weight: 850; cursor: pointer; }
    .tab.active { background: var(--panel); color: white; border-color: var(--panel); }
    .table-wrap { overflow: auto; max-height: 420px; border: 1px solid var(--line); border-radius: 14px; }
    table { border-collapse: collapse; width: 100%; min-width: 720px; font-size: 13px; }
    th, td { border-bottom: 1px solid var(--line); border-right: 1px solid var(--line); padding: 9px 10px; text-align: left; vertical-align: top; }
    th { background: #eef5ff; position: sticky; top: 0; z-index: 1; }
    td.empty { color: #9aa4b2; font-style: italic; }
    .sheet-summary { color: var(--muted); margin-bottom: 12px; }
    .chat-panel { overflow: hidden; position: sticky; top: 92px; }
    .chat-head { background: var(--panel); color: white; padding: 16px; }
    .chat-head h2 { margin: 0 0 6px; font-size: 18px; }
    .chat-head p { margin: 0; color: #c8d7ee; font-size: 13px; }
    .chat-body { padding: 16px; display: grid; gap: 14px; }
    .question-card { border: 1px solid var(--line); border-radius: 14px; padding: 14px; background: #fff; }
    .question-card b { display: block; margin-bottom: 8px; }
    .question-card small { color: var(--muted); display: block; margin-bottom: 10px; }
    textarea, input[type="text"], select { width: 100%; border: 1px solid #cbd5e1; border-radius: 12px; padding: 11px 12px; font: inherit; background: white; }
    textarea { min-height: 82px; resize: vertical; }
    .status-line { padding: 10px 12px; border-radius: 12px; background: #fff7ed; color: #9a3412; border: 1px solid #fed7aa; font-size: 13px; font-weight: 800; }
    .ok-line { background: #ecfdf5; color: #047857; border-color: #bbf7d0; }
    .danger-line { background: #fef2f2; color: #b91c1c; border-color: #fecaca; }
    .footer-note { margin-top: 20px; color: var(--muted); font-size: 13px; }
    @media (max-width: 980px) { .hero, .grid { grid-template-columns: 1fr; } .chat-panel { position: static; } .meta { grid-template-columns: repeat(2, 1fr); } }
    @media (max-width: 620px) { .nav { height: auto; flex-direction: column; align-items: flex-start; } .meta { grid-template-columns: 1fr; } .hero-card { padding: 20px; } }
  </style>
</head>
<body>
  <div class="shell">
    <header>
      <div class="nav">
        <div class="brand"><span class="logo">S1</span><span>PymIA Servicio 1 · Sandbox XLSX</span></div>
        <div class="env-badge">SANDBOX · NO PRODUCCIÓN · REVISIÓN HUMANA</div>
      </div>
    </header>

    <main>
      <section class="hero">
        <div class="hero-card">
          <h1>Ensayo online controlado para archivos XLSX.</h1>
          <p>Esta interfaz carga un XLSX en el navegador, muestra hojas y columnas, guía preguntas al dueño y exporta respuestas a TXT. No envía archivos a un servidor, no diagnostica, no concilia y no produce resultados contables finales.</p>
          <div class="flags"><span class="flag">SheetJS en navegador</span><span class="flag">Preview de hojas</span><span class="flag">Preguntas al dueño</span><span class="flag">Export TXT</span><span class="flag">Servicio 1 compatible</span></div>
        </div>
        <aside class="guard-card">
          <h2>Condiciones de uso</h2>
          <p>Usar sólo con archivos sintéticos, de prueba o anonimizados.</p>
          <ul><li>No subir datos reales sensibles.</li><li>No usar como diagnóstico final.</li><li>No usar como conciliación contable/fiscal.</li><li>Las respuestas exportadas son insumo para revisión humana.</li></ul>
          <div class="checks"><label class="check"><input id="confirmNoSensitive" type="checkbox" /> Confirmo que no usaré datos reales sensibles.</label><label class="check"><input id="confirmSandbox" type="checkbox" /> Entiendo que esto es sandbox y no producción.</label></div>
        </aside>
      </section>

      <section class="grid">
        <div class="panel">
          <div class="panel-head"><h2>1. Cargar XLSX y revisar hojas</h2><span id="fileStatus">Sin archivo</span></div>
          <div class="panel-body">
            <div id="dropzone" class="upload"><strong>Arrastrá un XLSX o seleccioná archivo</strong><p>El archivo se lee localmente en tu navegador. Máximo recomendado: 15 MB.</p><input id="fileInput" class="hidden" type="file" accept=".xlsx,.xls,.csv" /><button id="selectFileBtn" class="btn" type="button" disabled>Seleccionar archivo</button></div>
            <div id="fileMeta" class="meta hidden" aria-live="polite"><div class="meta-card"><b>Archivo</b><span id="metaName">—</span></div><div class="meta-card"><b>Tamaño</b><span id="metaSize">—</span></div><div class="meta-card"><b>Hojas</b><span id="metaSheets">—</span></div><div class="meta-card"><b>Modo</b><span>SANDBOX</span></div></div>
            <div id="tabs" class="tabs hidden"></div><p id="sheetSummary" class="sheet-summary hidden"></p><div id="preview" class="table-wrap hidden"></div>
            <p class="footer-note">Servicio 1 apto: este flujo sólo produce contexto y respuestas del dueño. No ejecuta fórmulas de negocio ni afirma hallazgos.</p>
          </div>
        </div>

        <aside class="chat-panel">
          <div class="chat-head"><h2>2. Preguntas al dueño</h2><p>Ronda breve para convertir el archivo en evidencia revisable.</p></div>
          <div class="chat-body">
            <div id="guardStatus" class="status-line danger-line">Confirmá condiciones para habilitar carga.</div>
            <div class="question-card"><b>¿Qué representa este archivo?</b><small>Ejemplo: ventas, stock, compras, banco, cobranzas, precios.</small><input id="answerPurpose" type="text" placeholder="Este archivo representa..." /></div>
            <div class="question-card"><b>¿Qué período cubre?</b><small>Ejemplo: marzo 2026, semana 22, enero-junio.</small><input id="answerPeriod" type="text" placeholder="Período revisado..." /></div>
            <div class="question-card"><b>¿Qué querés revisar primero?</b><small>No diagnóstico; sólo foco de ensayo Servicio 1.</small><select id="answerFocus"><option value="">Seleccionar foco</option><option>Ordenar / entender columnas</option><option>Preparar Excel Treatment Lab</option><option>Preparar conciliación banco sandbox</option><option>Preparar matching factura/cobranza sandbox</option><option>Preparar papel de trabajo contable borrador</option><option>Otro / requiere revisión humana</option></select></div>
            <div class="question-card"><b>¿Qué columnas te generan duda?</b><small>Usar nombres visibles en el preview si aplica.</small><textarea id="answerColumns" placeholder="Columnas dudosas, equivalencias, campos importantes..."></textarea></div>
            <div class="question-card"><b>Notas del operador</b><small>Límites, cautelas, evidencia faltante.</small><textarea id="answerNotes" placeholder="Notas de revisión humana..."></textarea></div>
            <button id="exportBtn" class="btn warning" type="button" disabled>Exportar respuestas TXT</button><button id="resetBtn" class="btn secondary" type="button">Reiniciar sandbox</button>
          </div>
        </aside>
      </section>
    </main>
  </div>

  <script>
    const state = { workbook: null, file: null, activeSheetName: null, sheets: {} };
    const els = {
      confirmNoSensitive: document.getElementById('confirmNoSensitive'), confirmSandbox: document.getElementById('confirmSandbox'), guardStatus: document.getElementById('guardStatus'), selectFileBtn: document.getElementById('selectFileBtn'), fileInput: document.getElementById('fileInput'), dropzone: document.getElementById('dropzone'), fileStatus: document.getElementById('fileStatus'), fileMeta: document.getElementById('fileMeta'), metaName: document.getElementById('metaName'), metaSize: document.getElementById('metaSize'), metaSheets: document.getElementById('metaSheets'), tabs: document.getElementById('tabs'), sheetSummary: document.getElementById('sheetSummary'), preview: document.getElementById('preview'), exportBtn: document.getElementById('exportBtn'), resetBtn: document.getElementById('resetBtn'), answerPurpose: document.getElementById('answerPurpose'), answerPeriod: document.getElementById('answerPeriod'), answerFocus: document.getElementById('answerFocus'), answerColumns: document.getElementById('answerColumns'), answerNotes: document.getElementById('answerNotes')
    };
    function guardAccepted() { return els.confirmNoSensitive.checked && els.confirmSandbox.checked; }
    function updateGuard() { const ok = guardAccepted(); els.selectFileBtn.disabled = !ok; els.guardStatus.className = ok ? 'status-line ok-line' : 'status-line danger-line'; els.guardStatus.textContent = ok ? 'Sandbox habilitado. Usar sólo archivo sintético o anonimizado.' : 'Confirmá condiciones para habilitar carga.'; }
    els.confirmNoSensitive.addEventListener('change', updateGuard); els.confirmSandbox.addEventListener('change', updateGuard); els.selectFileBtn.addEventListener('click', () => els.fileInput.click()); els.fileInput.addEventListener('change', event => { const file = event.target.files && event.target.files[0]; if (file) handleFile(file); });
    ['dragenter', 'dragover'].forEach(type => { els.dropzone.addEventListener(type, event => { event.preventDefault(); if (guardAccepted()) els.dropzone.classList.add('dragover'); }); });
    ['dragleave', 'drop'].forEach(type => { els.dropzone.addEventListener(type, event => { event.preventDefault(); els.dropzone.classList.remove('dragover'); }); });
    els.dropzone.addEventListener('drop', event => { if (!guardAccepted()) return; const file = event.dataTransfer.files && event.dataTransfer.files[0]; if (file) handleFile(file); });
    async function handleFile(file) { if (!guardAccepted()) return; if (!/\.(xlsx|xls|csv)$/i.test(file.name)) { alert('Formato no permitido. Usar XLSX, XLS o CSV.'); return; } if (file.size > 15 * 1024 * 1024) { alert('Archivo demasiado grande para este sandbox. Usar máximo 15 MB.'); return; } const buffer = await file.arrayBuffer(); const workbook = XLSX.read(buffer, { type: 'array' }); state.workbook = workbook; state.file = file; state.activeSheetName = workbook.SheetNames[0] || null; state.sheets = {}; workbook.SheetNames.forEach(sheetName => { const sheet = workbook.Sheets[sheetName]; state.sheets[sheetName] = XLSX.utils.sheet_to_json(sheet, { header: 1, defval: '' }); }); renderMeta(); renderTabs(); renderActiveSheet(); els.exportBtn.disabled = false; }
    function renderMeta() { els.fileStatus.textContent = 'Archivo cargado localmente'; els.metaName.textContent = state.file.name; els.metaSize.textContent = formatBytes(state.file.size); els.metaSheets.textContent = String(state.workbook.SheetNames.length); els.fileMeta.classList.remove('hidden'); }
    function renderTabs() { els.tabs.innerHTML = ''; state.workbook.SheetNames.forEach(sheetName => { const button = document.createElement('button'); button.type = 'button'; button.className = 'tab' + (sheetName === state.activeSheetName ? ' active' : ''); button.textContent = sheetName; button.addEventListener('click', () => { state.activeSheetName = sheetName; renderTabs(); renderActiveSheet(); }); els.tabs.appendChild(button); }); els.tabs.classList.remove('hidden'); }
    function renderActiveSheet() { const sheetName = state.activeSheetName; const rows = state.sheets[sheetName] || []; const nonEmptyRows = rows.filter(row => row.some(cell => String(cell).trim() !== '')); const maxCols = Math.max(0, ...rows.map(row => row.length)); const previewRows = rows.slice(0, 30); els.sheetSummary.textContent = `Hoja "${sheetName}" · ${nonEmptyRows.length} filas con contenido · ${maxCols} columnas detectadas · preview limitado a 30 filas.`; els.sheetSummary.classList.remove('hidden'); const table = document.createElement('table'); const thead = document.createElement('thead'); const headRow = document.createElement('tr'); for (let i = 0; i < maxCols; i++) { const th = document.createElement('th'); th.textContent = columnName(i); headRow.appendChild(th); } thead.appendChild(headRow); table.appendChild(thead); const tbody = document.createElement('tbody'); previewRows.forEach(row => { const tr = document.createElement('tr'); for (let i = 0; i < maxCols; i++) { const td = document.createElement('td'); const value = row[i]; td.textContent = value === '' || value === undefined || value === null ? '—' : String(value); if (value === '' || value === undefined || value === null) td.className = 'empty'; tr.appendChild(td); } tbody.appendChild(tr); }); table.appendChild(tbody); els.preview.innerHTML = ''; els.preview.appendChild(table); els.preview.classList.remove('hidden'); }
    function exportAnswers() { const now = new Date().toISOString(); const sheetNames = state.workbook ? state.workbook.SheetNames.join(', ') : ''; const activeRows = state.activeSheetName ? (state.sheets[state.activeSheetName] || []) : []; const activeNonEmptyRows = activeRows.filter(row => row.some(cell => String(cell).trim() !== '')).length; const lines = ['PYMIA_SERVICIO_1_XLSX_SANDBOX_OWNER_ANSWERS_V1', '', `created_at: ${now}`, 'environment: SANDBOX_REHEARSAL_ONLY', 'runtime_authorized: false', 'production_allowed: false', 'human_review_required: true', 'real_client_claim: false', '', '[FILE_CONTEXT]', `file_name: ${state.file ? state.file.name : ''}`, `file_size: ${state.file ? formatBytes(state.file.size) : ''}`, `sheet_names: ${sheetNames}`, `active_sheet: ${state.activeSheetName || ''}`, `active_sheet_non_empty_rows: ${activeNonEmptyRows}`, '', '[OWNER_ANSWERS]', `file_purpose: ${els.answerPurpose.value.trim()}`, `period: ${els.answerPeriod.value.trim()}`, `review_focus: ${els.answerFocus.value.trim()}`, 'doubtful_columns:', indentBlock(els.answerColumns.value.trim()), 'operator_notes:', indentBlock(els.answerNotes.value.trim()), '', '[LIMITATIONS]', '- This export is not a diagnosis.', '- This export is not an accounting, tax, fiscal or reconciliation conclusion.', '- File was read locally in the browser for preview only.', '- Human review is required before any Servicio 1 delivery decision.']; const blob = new Blob([lines.join('\n')], { type: 'text/plain;charset=utf-8' }); const url = URL.createObjectURL(blob); const anchor = document.createElement('a'); anchor.href = url; anchor.download = buildDownloadName(); document.body.appendChild(anchor); anchor.click(); anchor.remove(); URL.revokeObjectURL(url); }
    function buildDownloadName() { const base = state.file ? state.file.name.replace(/\.[^.]+$/, '') : 'sandbox'; return `servicio1_owner_answers_${safeName(base)}.txt`; }
    function safeName(text) { return String(text).toLowerCase().replace(/[^a-z0-9_-]+/gi, '_').replace(/^_+|_+$/g, '').slice(0, 80) || 'sandbox'; }
    function indentBlock(text) { if (!text) return '  -'; return text.split('\n').map(line => `  ${line}`).join('\n'); }
    function formatBytes(bytes) { if (!bytes) return '0 B'; const units = ['B', 'KB', 'MB', 'GB']; const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1); return `${(bytes / Math.pow(1024, index)).toFixed(index === 0 ? 0 : 1)} ${units[index]}`; }
    function columnName(index) { let dividend = index + 1; let name = ''; while (dividend > 0) { const modulo = (dividend - 1) % 26; name = String.fromCharCode(65 + modulo) + name; dividend = Math.floor((dividend - modulo) / 26); } return name; }
    function resetSandbox() { state.workbook = null; state.file = null; state.activeSheetName = null; state.sheets = {}; els.fileInput.value = ''; els.fileStatus.textContent = 'Sin archivo'; els.fileMeta.classList.add('hidden'); els.tabs.classList.add('hidden'); els.tabs.innerHTML = ''; els.sheetSummary.classList.add('hidden'); els.sheetSummary.textContent = ''; els.preview.classList.add('hidden'); els.preview.innerHTML = ''; els.exportBtn.disabled = true; els.answerPurpose.value = ''; els.answerPeriod.value = ''; els.answerFocus.value = ''; els.answerColumns.value = ''; els.answerNotes.value = ''; }
    els.exportBtn.addEventListener('click', exportAnswers); els.resetBtn.addEventListener('click', resetSandbox); updateGuard();
  </script>
</body>
</html>
'''


def build_service1_sandbox_html(output_file: Path = OUTPUT_FILE) -> Path:
    output_file.write_text(SERVICE1_SANDBOX_HTML, encoding="utf-8", newline="\n")
    return output_file


if __name__ == "__main__":
    path = build_service1_sandbox_html()
    print(f"Wrote {path}")
