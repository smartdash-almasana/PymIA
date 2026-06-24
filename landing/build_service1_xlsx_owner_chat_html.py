from __future__ import annotations

from pathlib import Path

OUTPUT_FILE = Path(__file__).with_name("servicio1-xlsx-owner-chat.html")

SERVICE1_XLSX_OWNER_CHAT_HTML = r'''<!DOCTYPE html>
<html lang="es-AR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>PymIA Servicio 1 — XLSX Owner Chat</title>
  <script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
  <style>
    :root { --bg:#07111f; --panel:#0e1b2f; --ink:#0c1726; --muted:#64748b; --line:#d9e2ef; --brand:#1e66ff; --warn:#f59e0b; --ok:#10b981; --soft:#f6f8fb; --radius:18px; }
    * { box-sizing:border-box; }
    body { margin:0; font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; background:var(--soft); color:var(--ink); }
    header { background:var(--bg); color:white; position:sticky; top:0; z-index:20; border-bottom:1px solid rgba(255,255,255,.12); }
    .nav { width:min(1280px,calc(100% - 32px)); margin:auto; min-height:64px; display:flex; justify-content:space-between; align-items:center; gap:12px; }
    .brand { font-weight:900; letter-spacing:-.03em; display:flex; align-items:center; gap:10px; }
    .logo { width:36px; height:36px; border-radius:12px; background:linear-gradient(135deg,var(--brand),#00c2a8); display:grid; place-items:center; }
    .badge { border:1px solid rgba(245,158,11,.45); background:rgba(245,158,11,.16); color:#fde68a; border-radius:999px; padding:8px 12px; font-size:13px; font-weight:800; }
    main { width:min(1280px,calc(100% - 32px)); margin:auto; padding:24px 0 52px; }
    .top { display:grid; grid-template-columns:1fr 420px; gap:18px; margin-bottom:18px; }
    .card { background:white; border:1px solid var(--line); border-radius:var(--radius); box-shadow:0 16px 48px rgba(7,17,31,.12); overflow:hidden; }
    .intro { padding:24px; }
    .intro h1 { margin:0 0 10px; font-size:clamp(30px,4vw,52px); line-height:.98; letter-spacing:-.06em; }
    .intro p { margin:0; color:var(--muted); font-size:17px; max-width:820px; }
    .guard { padding:18px; border-left:5px solid var(--warn); }
    .guard h2 { margin:0 0 8px; font-size:18px; }
    .guard label { display:flex; gap:10px; margin-top:10px; font-weight:750; }
    .guard input { width:18px; height:18px; margin-top:2px; }
    .work { display:grid; grid-template-columns:minmax(0,1fr) 420px; gap:18px; align-items:start; }
    .head { padding:14px 16px; background:var(--panel); color:white; display:flex; justify-content:space-between; gap:12px; align-items:center; }
    .head h2 { margin:0; font-size:17px; }
    .body { padding:16px; }
    .upload { border:2px dashed #bfd0e8; border-radius:16px; background:#f8fbff; padding:24px; text-align:center; }
    .upload.dragover { border-color:var(--brand); background:#eef5ff; }
    .upload strong { display:block; font-size:19px; margin-bottom:6px; }
    .upload p { color:var(--muted); margin:0 0 14px; }
    .btn { border:0; border-radius:12px; padding:11px 15px; background:var(--brand); color:white; font-weight:900; cursor:pointer; }
    .btn.secondary { background:#e9eef8; color:var(--ink); }
    .btn.warning { background:var(--warn); color:#221400; }
    .btn:disabled { opacity:.45; cursor:not-allowed; }
    .hidden { display:none!important; }
    .meta { margin-top:14px; display:grid; grid-template-columns:repeat(4,1fr); gap:10px; }
    .meta div { border:1px solid var(--line); border-radius:14px; padding:11px; }
    .meta b { display:block; color:var(--muted); font-size:12px; }
    .meta span { font-weight:900; }
    .tabs { display:flex; flex-wrap:wrap; gap:8px; margin:16px 0; }
    .tab { border:1px solid var(--line); background:white; border-radius:999px; padding:8px 12px; font-weight:850; cursor:pointer; }
    .tab.active { background:var(--panel); color:white; border-color:var(--panel); }
    .sheet-summary { color:var(--muted); margin:8px 0 12px; }
    .table-wrap { overflow:auto; max-height:430px; border:1px solid var(--line); border-radius:14px; }
    table { border-collapse:collapse; width:100%; min-width:760px; font-size:13px; }
    th,td { border-bottom:1px solid var(--line); border-right:1px solid var(--line); padding:8px 10px; text-align:left; vertical-align:top; }
    th { background:#eef5ff; position:sticky; top:0; z-index:1; }
    td.empty { color:#94a3b8; font-style:italic; }
    .chat { position:sticky; top:88px; }
    .chat-log { height:440px; overflow:auto; display:flex; flex-direction:column; gap:10px; padding:14px; background:#f8fbff; border-bottom:1px solid var(--line); }
    .msg { max-width:92%; border-radius:14px; padding:10px 12px; font-size:14px; white-space:pre-wrap; }
    .msg.pymia { background:white; border:1px solid var(--line); align-self:flex-start; }
    .msg.owner { background:#dbeafe; align-self:flex-end; }
    .composer { display:grid; gap:10px; padding:14px; }
    textarea { width:100%; min-height:84px; resize:vertical; border:1px solid #cbd5e1; border-radius:12px; padding:11px; font:inherit; }
    .row { display:flex; gap:8px; flex-wrap:wrap; }
    .status { padding:9px 11px; border-radius:12px; font-weight:800; font-size:13px; background:#fef2f2; color:#991b1b; border:1px solid #fecaca; }
    .status.ok { background:#ecfdf5; color:#047857; border-color:#bbf7d0; }
    .note { color:var(--muted); font-size:13px; margin-top:12px; }
    @media (max-width:980px) { .top,.work { grid-template-columns:1fr; } .chat { position:static; } .meta { grid-template-columns:repeat(2,1fr); } }
  </style>
</head>
<body>
<header><div class="nav"><div class="brand"><span class="logo">S1</span><span>PymIA Servicio 1 · XLSX Owner Chat</span></div><div class="badge">LOCAL · SIN API · REVISIÓN HUMANA</div></div></header>
<main>
  <section class="top">
    <div class="card intro"><h1>El Excel entra. PymIA pregunta. El dueño responde.</h1><p>Esta página lee la estructura real del XLSX en el navegador: hojas, filas, columnas visibles y celdas vacías. Con eso genera preguntas de Servicio 1. No inventa métricas, no llama a backend y no emite diagnóstico.</p></div>
    <aside class="card guard"><h2>Condiciones</h2><div id="guardStatus" class="status">Confirmar condiciones para habilitar carga.</div><label><input id="confirmLocal" type="checkbox" /> Entiendo que el archivo se lee localmente en el navegador.</label><label><input id="confirmNoFinal" type="checkbox" /> Entiendo que esto no entrega diagnóstico ni resultado contable final.</label></aside>
  </section>

  <section class="work">
    <div class="card">
      <div class="head"><h2>Archivo y vista previa</h2><span id="fileStatus">Sin archivo</span></div>
      <div class="body">
        <div id="dropzone" class="upload"><strong>Arrastrá un XLSX/CSV o seleccioná archivo</strong><p>PymIA leerá hojas y columnas reales para iniciar preguntas.</p><input id="fileInput" class="hidden" type="file" accept=".xlsx,.xls,.csv" /><button id="selectFileBtn" class="btn" disabled>Seleccionar archivo</button></div>
        <div id="meta" class="meta hidden"><div><b>Archivo</b><span id="metaName">—</span></div><div><b>Tamaño</b><span id="metaSize">—</span></div><div><b>Hojas</b><span id="metaSheets">—</span></div><div><b>Preguntas</b><span id="metaQuestions">—</span></div></div>
        <div id="tabs" class="tabs hidden"></div><p id="sheetSummary" class="sheet-summary hidden"></p><div id="preview" class="table-wrap hidden"></div>
        <p class="note">La vista previa está limitada a 30 filas. El objetivo es confirmar sentido y contexto antes de cualquier tratamiento.</p>
      </div>
    </div>

    <aside class="card chat">
      <div class="head"><h2>Chat de confirmación</h2><span id="chatState">Esperando archivo</span></div>
      <div id="chatLog" class="chat-log"></div>
      <div class="composer"><textarea id="ownerInput" placeholder="Respuesta del dueño..." disabled></textarea><div class="row"><button id="sendBtn" class="btn" disabled>Responder</button><button id="skipBtn" class="btn secondary" disabled>Marcar como no sé</button><button id="exportBtn" class="btn warning" disabled>Exportar TXT</button><button id="resetBtn" class="btn secondary">Reiniciar</button></div></div>
    </aside>
  </section>
</main>
<script>
const state = { file:null, workbook:null, activeSheet:null, sheets:{}, profile:null, questions:[], index:-1, answers:[], transcript:[] };
const els = { confirmLocal:byId('confirmLocal'), confirmNoFinal:byId('confirmNoFinal'), guardStatus:byId('guardStatus'), selectFileBtn:byId('selectFileBtn'), fileInput:byId('fileInput'), dropzone:byId('dropzone'), fileStatus:byId('fileStatus'), meta:byId('meta'), metaName:byId('metaName'), metaSize:byId('metaSize'), metaSheets:byId('metaSheets'), metaQuestions:byId('metaQuestions'), tabs:byId('tabs'), sheetSummary:byId('sheetSummary'), preview:byId('preview'), chatLog:byId('chatLog'), chatState:byId('chatState'), ownerInput:byId('ownerInput'), sendBtn:byId('sendBtn'), skipBtn:byId('skipBtn'), exportBtn:byId('exportBtn'), resetBtn:byId('resetBtn') };
function byId(id){return document.getElementById(id)}
function canLoad(){return els.confirmLocal.checked && els.confirmNoFinal.checked}
function updateGuard(){ const ok=canLoad(); els.selectFileBtn.disabled=!ok; els.guardStatus.className=ok?'status ok':'status'; els.guardStatus.textContent=ok?'Carga habilitada.':'Confirmar condiciones para habilitar carga.' }
els.confirmLocal.addEventListener('change', updateGuard); els.confirmNoFinal.addEventListener('change', updateGuard); els.selectFileBtn.addEventListener('click',()=>els.fileInput.click()); els.fileInput.addEventListener('change',e=>{const f=e.target.files&&e.target.files[0]; if(f) handleFile(f)});
['dragenter','dragover'].forEach(t=>els.dropzone.addEventListener(t,e=>{e.preventDefault(); if(canLoad()) els.dropzone.classList.add('dragover')})); ['dragleave','drop'].forEach(t=>els.dropzone.addEventListener(t,e=>{e.preventDefault(); els.dropzone.classList.remove('dragover')})); els.dropzone.addEventListener('drop',e=>{if(!canLoad())return; const f=e.dataTransfer.files&&e.dataTransfer.files[0]; if(f) handleFile(f)});
els.sendBtn.addEventListener('click',()=>sendAnswer(false)); els.skipBtn.addEventListener('click',()=>sendAnswer(true)); els.exportBtn.addEventListener('click',exportTxt); els.resetBtn.addEventListener('click',()=>location.reload());
async function handleFile(file){ if(!/\.(xlsx|xls|csv)$/i.test(file.name)){alert('Formato no permitido.');return} const buffer=await file.arrayBuffer(); const workbook=XLSX.read(buffer,{type:'array'}); state.file=file; state.workbook=workbook; state.activeSheet=workbook.SheetNames[0]||null; state.sheets={}; workbook.SheetNames.forEach(name=>{state.sheets[name]=XLSX.utils.sheet_to_json(workbook.Sheets[name],{header:1,defval:''})}); state.profile=buildProfile(); state.questions=buildQuestions(state.profile); renderMeta(); renderTabs(); renderActiveSheet(); startChat(); }
function buildProfile(){ const sheets=state.workbook.SheetNames.map(name=>{ const rows=state.sheets[name]||[]; const nonEmpty=rows.filter(r=>r.some(c=>String(c).trim()!=='')); const maxCols=Math.max(0,...rows.map(r=>r.length)); const headerRow=findHeaderRow(rows); const headers=headerRow>=0 ? rows[headerRow].map(v=>String(v).trim()).filter(Boolean) : []; const emptyHeaders=maxCols-headers.length; return {name, rows:nonEmpty.length, cols:maxCols, headerRow, headers, emptyHeaders} }); return {fileName:state.file.name, fileSize:state.file.size, sheets}; }
function findHeaderRow(rows){ for(let i=0;i<Math.min(rows.length,10);i++){ const filled=rows[i].filter(c=>String(c).trim()!=='' ).length; if(filled>=2) return i } return -1 }
function buildQuestions(profile){ const qs=[]; qs.push(q('archivo_proposito',`Leí el archivo "${profile.fileName}". ¿Qué representa este archivo en tu operación?`, 'PymIA necesita ubicar el archivo antes de tratar columnas.')); qs.push(q('periodo', '¿Qué período cubre este archivo?', 'No se infiere desde el archivo; lo confirma el dueño.')); qs.push(q('hoja_principal', `Detecté estas hojas: ${profile.sheets.map(s=>s.name).join(', ')}. ¿Cuál debería revisar primero?`, 'No asumo que la primera hoja sea la correcta.')); profile.sheets.forEach(sheet=>{ qs.push(q(`sentido_hoja_${safeId(sheet.name)}`, `En la hoja "${sheet.name}" veo ${sheet.rows} filas con contenido y ${sheet.cols} columnas. ¿Qué contiene esta hoja?`, 'Confirmación de sentido de hoja.')); if(sheet.headers.length){ qs.push(q(`columnas_clave_${safeId(sheet.name)}`, `En "${sheet.name}" leo estos encabezados: ${sheet.headers.slice(0,10).join(', ')}. ¿Qué significa cada uno de los principales?`, 'Confirmación semántica de columnas, sin inferencia automática.')); } else { qs.push(q(`sin_encabezado_${safeId(sheet.name)}`, `No pude identificar encabezados claros en "${sheet.name}". ¿Dónde empiezan los datos y qué significa cada bloque?`, 'Bloqueo potencial por encabezados débiles.')); } }); qs.push(q('objetivo_revision', '¿Qué querés revisar primero con este archivo?', 'El objetivo lo define el dueño; PymIA no lo inventa.')); qs.push(q('dudas_columnas', '¿Qué columnas o valores te generan duda?', 'Ayuda a evitar interpretación automática equivocada.')); qs.push(q('evidencia_faltante', '¿Existe otro archivo que debería mirarse junto con este?', 'PymIA registra evidencia relacionada sin asumirla.')); return qs; }
function q(id,text,reason){return {id,text,reason}}
function renderMeta(){ els.fileStatus.textContent='Archivo leído localmente'; els.metaName.textContent=state.file.name; els.metaSize.textContent=formatBytes(state.file.size); els.metaSheets.textContent=String(state.workbook.SheetNames.length); els.metaQuestions.textContent=String(state.questions.length); els.meta.classList.remove('hidden') }
function renderTabs(){ els.tabs.innerHTML=''; state.workbook.SheetNames.forEach(name=>{ const b=document.createElement('button'); b.className='tab'+(name===state.activeSheet?' active':''); b.textContent=name; b.onclick=()=>{state.activeSheet=name; renderTabs(); renderActiveSheet()}; els.tabs.appendChild(b) }); els.tabs.classList.remove('hidden') }
function renderActiveSheet(){ const rows=state.sheets[state.activeSheet]||[]; const nonEmpty=rows.filter(r=>r.some(c=>String(c).trim()!=='')); const maxCols=Math.max(0,...rows.map(r=>r.length)); els.sheetSummary.textContent=`Hoja "${state.activeSheet}" · ${nonEmpty.length} filas con contenido · ${maxCols} columnas · preview 30 filas.`; els.sheetSummary.classList.remove('hidden'); const table=document.createElement('table'); const thead=document.createElement('thead'); const hr=document.createElement('tr'); for(let i=0;i<maxCols;i++){const th=document.createElement('th'); th.textContent=columnName(i); hr.appendChild(th)} thead.appendChild(hr); table.appendChild(thead); const tbody=document.createElement('tbody'); rows.slice(0,30).forEach(row=>{const tr=document.createElement('tr'); for(let i=0;i<maxCols;i++){const td=document.createElement('td'); const v=row[i]; td.textContent=(v===undefined||v===null||v==='')?'—':String(v); if(td.textContent==='—')td.className='empty'; tr.appendChild(td)} tbody.appendChild(tr)}); table.appendChild(tbody); els.preview.innerHTML=''; els.preview.appendChild(table); els.preview.classList.remove('hidden') }
function startChat(){ els.chatLog.innerHTML=''; addMsg('pymia',`Archivo recibido: ${state.profile.fileName}\nHojas detectadas: ${state.profile.sheets.length}\nVoy a hacer preguntas basadas en la estructura leída. No voy a diagnosticar.`); state.index=-1; nextQuestion(); els.ownerInput.disabled=false; els.sendBtn.disabled=false; els.skipBtn.disabled=false; els.exportBtn.disabled=false; }
function nextQuestion(){ state.index++; if(state.index>=state.questions.length){ els.chatState.textContent='Preguntas completas'; addMsg('pymia','No tengo más preguntas iniciales. Exportá el TXT para revisar el caso.'); els.ownerInput.disabled=true; els.sendBtn.disabled=true; els.skipBtn.disabled=true; return } const item=state.questions[state.index]; els.chatState.textContent=`Pregunta ${state.index+1}/${state.questions.length}`; addMsg('pymia',`${item.text}\n\nMotivo: ${item.reason}`); }
function sendAnswer(skip){ const item=state.questions[state.index]; const text=skip?'NO_SE / requiere revisión humana':els.ownerInput.value.trim(); if(!text){alert('Escribí una respuesta o marcá como no sé.'); return} state.answers.push({question_id:item.id, question:item.text, answer:text}); addMsg('owner',text); els.ownerInput.value=''; nextQuestion(); }
function addMsg(role,text){ state.transcript.push({role,text,at:new Date().toISOString()}); const div=document.createElement('div'); div.className='msg '+role; div.textContent=(role==='pymia'?'PymIA: ':'Dueño: ')+text; els.chatLog.appendChild(div); els.chatLog.scrollTop=els.chatLog.scrollHeight; }
function exportTxt(){ const lines=['PYMIA_SERVICE_1_XLSX_OWNER_CHAT_V1','',`created_at: ${new Date().toISOString()}`,'runtime_authorized: false','production_allowed: false','final_diagnosis: false','final_accounting_result: false','human_review_required: true','', '[FILE_PROFILE]', JSON.stringify(state.profile,null,2),'','[ANSWERS]']; state.answers.forEach((a,i)=>{lines.push(`Q${i+1}: ${a.question}`,`A${i+1}: ${a.answer}`,'')}); lines.push('[LIMITS]','- PymIA preguntó sobre estructura real del archivo leído.','- No se emitió diagnóstico.','- No se cerró conciliación ni resultado contable.','- El TXT requiere revisión humana.'); const blob=new Blob([lines.join('\n')],{type:'text/plain;charset=utf-8'}); const url=URL.createObjectURL(blob); const a=document.createElement('a'); a.href=url; a.download='pymia_service1_xlsx_owner_chat_'+safeId(state.file?state.file.name:'case')+'.txt'; document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url); }
function safeId(s){return String(s).toLowerCase().replace(/[^a-z0-9_-]+/gi,'_').replace(/^_+|_+$/g,'').slice(0,80)||'case'}
function formatBytes(bytes){ if(!bytes)return'0 B'; const units=['B','KB','MB','GB']; const i=Math.min(Math.floor(Math.log(bytes)/Math.log(1024)),units.length-1); return `${(bytes/Math.pow(1024,i)).toFixed(i===0?0:1)} ${units[i]}` }
function columnName(index){ let n=index+1,s=''; while(n>0){const m=(n-1)%26; s=String.fromCharCode(65+m)+s; n=Math.floor((n-m)/26)} return s }
updateGuard();
</script>
</body>
</html>
'''


def build_service1_xlsx_owner_chat_html(output_file: Path = OUTPUT_FILE) -> Path:
    output_file.write_text(SERVICE1_XLSX_OWNER_CHAT_HTML, encoding="utf-8", newline="\n")
    return output_file


if __name__ == "__main__":
    path = build_service1_xlsx_owner_chat_html()
    print(f"Wrote {path}")
