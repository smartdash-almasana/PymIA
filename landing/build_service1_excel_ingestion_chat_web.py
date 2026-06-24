from __future__ import annotations

from pathlib import Path

OUTPUT_FILE = Path(__file__).with_name("servicio1-excel-ingestion-chat.html")

SERVICE1_EXCEL_INGESTION_CHAT_HTML = r'''<!doctype html>
<html lang="es-AR">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>PymIA · Ingesta Excel + Chat</title>
  <script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
  <style>
    :root { --bg:#07111f; --panel:#0d1b2f; --ink:#0f172a; --muted:#64748b; --line:#dbe4f0; --soft:#f6f8fb; --white:#fff; --brand:#1e66ff; --warn:#f59e0b; --ok:#10b981; --bad:#ef4444; }
    * { box-sizing:border-box; }
    body { margin:0; font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; background:var(--soft); color:var(--ink); }
    header { height:64px; background:var(--bg); color:white; display:flex; align-items:center; justify-content:space-between; padding:0 24px; border-bottom:1px solid rgba(255,255,255,.12); }
    header b { letter-spacing:-.03em; }
    .badge { color:#fde68a; border:1px solid rgba(245,158,11,.45); background:rgba(245,158,11,.14); border-radius:999px; padding:8px 12px; font-size:12px; font-weight:800; }
    main { height:calc(100vh - 64px); display:grid; grid-template-columns:minmax(0,1fr) 430px; gap:16px; padding:16px; }
    .left,.right { min-height:0; background:white; border:1px solid var(--line); border-radius:18px; overflow:hidden; box-shadow:0 18px 44px rgba(7,17,31,.08); }
    .section-head { height:56px; background:var(--panel); color:white; display:flex; align-items:center; justify-content:space-between; padding:0 16px; }
    .section-head h1,.section-head h2 { margin:0; font-size:17px; }
    .left-body { height:calc(100% - 56px); display:grid; grid-template-rows:auto auto auto minmax(0,1fr); gap:14px; padding:16px; overflow:hidden; }
    .dropzone { border:2px dashed #bdd0ea; border-radius:16px; background:#f8fbff; padding:22px; text-align:center; }
    .dropzone.dragover { border-color:var(--brand); background:#eef5ff; }
    .dropzone strong { display:block; font-size:20px; margin-bottom:6px; }
    .dropzone p { margin:0 0 14px; color:var(--muted); }
    button { border:0; border-radius:12px; padding:11px 14px; font-weight:900; cursor:pointer; background:var(--brand); color:white; }
    button.secondary { background:#e9eef8; color:var(--ink); }
    button.warn { background:var(--warn); color:#231600; }
    button:disabled { opacity:.45; cursor:not-allowed; }
    input[type=file] { display:none; }
    .meta { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; }
    .meta-card { border:1px solid var(--line); border-radius:14px; padding:10px; background:white; }
    .meta-card small { display:block; color:var(--muted); font-size:12px; }
    .meta-card span { font-weight:900; }
    .tabs { display:flex; gap:8px; flex-wrap:wrap; }
    .tab { background:white; color:var(--ink); border:1px solid var(--line); border-radius:999px; padding:8px 12px; }
    .tab.active { background:var(--panel); color:white; border-color:var(--panel); }
    .summary { color:var(--muted); margin:0; font-size:14px; }
    .table-wrap { min-height:0; overflow:auto; border:1px solid var(--line); border-radius:14px; }
    table { border-collapse:collapse; width:100%; min-width:760px; font-size:13px; }
    th,td { border-bottom:1px solid var(--line); border-right:1px solid var(--line); padding:8px 10px; text-align:left; vertical-align:top; }
    th { background:#eef5ff; position:sticky; top:0; z-index:1; }
    td.empty { color:#94a3b8; font-style:italic; }
    .right { display:grid; grid-template-rows:56px minmax(0,1fr) auto; }
    .chat-log { min-height:0; overflow:auto; background:#f8fbff; padding:14px; display:flex; flex-direction:column; gap:10px; }
    .msg { max-width:92%; border-radius:15px; padding:10px 12px; white-space:pre-wrap; line-height:1.35; font-size:14px; }
    .msg.pymia { align-self:flex-start; background:white; border:1px solid var(--line); }
    .msg.owner { align-self:flex-end; background:#dbeafe; }
    .composer { padding:14px; display:grid; gap:10px; border-top:1px solid var(--line); }
    textarea { width:100%; min-height:86px; resize:vertical; border:1px solid #cbd5e1; border-radius:12px; padding:11px; font:inherit; }
    .row { display:flex; gap:8px; flex-wrap:wrap; }
    .hidden { display:none!important; }
    .status { font-size:13px; font-weight:800; }
    @media(max-width:980px){ main{height:auto; min-height:calc(100vh - 64px); grid-template-columns:1fr;} .right{min-height:620px;} .meta{grid-template-columns:repeat(2,1fr);} }
  </style>
</head>
<body>
<header>
  <b>PymIA · Servicio 1 · Ingesta Excel + Chat</b>
  <span class="badge">PRUEBA REAL · SIN SIMULACIÓN · SIN BACKEND</span>
</header>
<main>
  <section class="left">
    <div class="section-head"><h1>Excel cargado</h1><span id="fileStatus" class="status">Sin archivo</span></div>
    <div class="left-body">
      <div id="dropzone" class="dropzone">
        <strong>Cargar Excel</strong>
        <p>El archivo se lee en el navegador con SheetJS. PymIA hará preguntas según hojas, filas, columnas y encabezados reales.</p>
        <input id="fileInput" type="file" accept=".xlsx,.xls,.csv" />
        <button id="selectFileBtn">Seleccionar XLSX / CSV</button>
      </div>
      <div id="meta" class="meta hidden">
        <div class="meta-card"><small>Archivo</small><span id="metaName">—</span></div>
        <div class="meta-card"><small>Tamaño</small><span id="metaSize">—</span></div>
        <div class="meta-card"><small>Hojas</small><span id="metaSheets">—</span></div>
        <div class="meta-card"><small>Preguntas</small><span id="metaQuestions">—</span></div>
      </div>
      <div><div id="tabs" class="tabs hidden"></div><p id="summary" class="summary hidden"></p></div>
      <div id="preview" class="table-wrap hidden"></div>
    </div>
  </section>

  <aside class="right">
    <div class="section-head"><h2>Chat con el dueño</h2><span id="chatState" class="status">Esperando Excel</span></div>
    <div id="chatLog" class="chat-log"></div>
    <div class="composer">
      <textarea id="ownerInput" placeholder="Respuesta del dueño..." disabled></textarea>
      <div class="row">
        <button id="sendBtn" disabled>Enviar respuesta</button>
        <button id="unknownBtn" class="secondary" disabled>No sé</button>
        <button id="exportBtn" class="warn" disabled>Exportar conversación</button>
        <button id="resetBtn" class="secondary">Reiniciar</button>
      </div>
    </div>
  </aside>
</main>
<script>
const state = { file:null, workbook:null, sheets:{}, activeSheet:null, profile:null, questions:[], questionIndex:-1, answers:[] };
const els = {
  dropzone:id('dropzone'), fileInput:id('fileInput'), selectFileBtn:id('selectFileBtn'), fileStatus:id('fileStatus'), meta:id('meta'), metaName:id('metaName'), metaSize:id('metaSize'), metaSheets:id('metaSheets'), metaQuestions:id('metaQuestions'), tabs:id('tabs'), summary:id('summary'), preview:id('preview'), chatLog:id('chatLog'), chatState:id('chatState'), ownerInput:id('ownerInput'), sendBtn:id('sendBtn'), unknownBtn:id('unknownBtn'), exportBtn:id('exportBtn'), resetBtn:id('resetBtn')
};
function id(x){ return document.getElementById(x); }
els.selectFileBtn.addEventListener('click',()=>els.fileInput.click());
els.fileInput.addEventListener('change',e=>{ const file=e.target.files&&e.target.files[0]; if(file) ingestExcel(file); });
['dragenter','dragover'].forEach(t=>els.dropzone.addEventListener(t,e=>{ e.preventDefault(); els.dropzone.classList.add('dragover'); }));
['dragleave','drop'].forEach(t=>els.dropzone.addEventListener(t,e=>{ e.preventDefault(); els.dropzone.classList.remove('dragover'); }));
els.dropzone.addEventListener('drop',e=>{ const file=e.dataTransfer.files&&e.dataTransfer.files[0]; if(file) ingestExcel(file); });
els.sendBtn.addEventListener('click',()=>answerCurrent(false));
els.unknownBtn.addEventListener('click',()=>answerCurrent(true));
els.exportBtn.addEventListener('click',exportConversation);
els.resetBtn.addEventListener('click',()=>location.reload());

async function ingestExcel(file){
  if(!/\.(xlsx|xls|csv)$/i.test(file.name)){ alert('Formato no permitido. Usar XLSX, XLS o CSV.'); return; }
  const buffer = await file.arrayBuffer();
  const workbook = XLSX.read(buffer,{type:'array'});
  state.file=file; state.workbook=workbook; state.activeSheet=workbook.SheetNames[0]||null; state.sheets={};
  workbook.SheetNames.forEach(name=>{ state.sheets[name]=XLSX.utils.sheet_to_json(workbook.Sheets[name],{header:1,defval:''}); });
  state.profile=profileWorkbook();
  state.questions=questionsFromProfile(state.profile);
  renderWorkbook();
  startChat();
}

function profileWorkbook(){
  return { fileName:state.file.name, fileSize:state.file.size, sheets:state.workbook.SheetNames.map(name=>profileSheet(name,state.sheets[name]||[])) };
}
function profileSheet(name,rows){
  const nonEmptyRows=rows.filter(row=>row.some(cell=>String(cell).trim()!==''));
  const columnCount=Math.max(0,...rows.map(row=>row.length));
  const headerRowIndex=findHeaderRow(rows);
  const headers=headerRowIndex>=0 ? rows[headerRowIndex].map(v=>String(v).trim()).filter(Boolean) : [];
  return { name, nonEmptyRowCount:nonEmptyRows.length, columnCount, headerRowIndex, headers };
}
function findHeaderRow(rows){
  for(let i=0;i<Math.min(rows.length,10);i++){ if(rows[i].filter(cell=>String(cell).trim()!=='').length>=2) return i; }
  return -1;
}
function questionsFromProfile(profile){
  const questions=[];
  questions.push({id:'file_meaning', text:`Cargaste "${profile.fileName}". ¿Qué representa este archivo?`});
  questions.push({id:'file_period', text:'¿Qué período o fecha cubre este archivo?'});
  questions.push({id:'main_sheet', text:`Veo estas hojas: ${profile.sheets.map(s=>s.name).join(', ')}. ¿Cuál querés revisar primero?`});
  profile.sheets.forEach(sheet=>{
    questions.push({id:`sheet_meaning_${safe(sheet.name)}`, text:`En la hoja "${sheet.name}" veo ${sheet.nonEmptyRowCount} filas con contenido y ${sheet.columnCount} columnas. ¿Qué contiene esta hoja?`});
    if(sheet.headers.length){ questions.push({id:`headers_${safe(sheet.name)}`, text:`En "${sheet.name}" leo estos encabezados: ${sheet.headers.slice(0,12).join(', ')}. ¿Qué significan los principales?`}); }
    else { questions.push({id:`headers_missing_${safe(sheet.name)}`, text:`En "${sheet.name}" no veo encabezados claros. ¿Dónde empiezan los datos y cómo se leen las columnas?`}); }
  });
  questions.push({id:'owner_goal', text:'¿Qué querés que PymIA te ayude a entender o revisar en este Excel?'});
  questions.push({id:'unclear_fields', text:'¿Qué columnas, hojas o valores te generan duda?'});
  questions.push({id:'related_files', text:'¿Hay otro archivo que debería mirarse junto con este?'});
  return questions;
}
function renderWorkbook(){
  els.fileStatus.textContent='Archivo leído';
  els.metaName.textContent=state.file.name;
  els.metaSize.textContent=formatBytes(state.file.size);
  els.metaSheets.textContent=String(state.workbook.SheetNames.length);
  els.metaQuestions.textContent=String(state.questions.length);
  els.meta.classList.remove('hidden');
  renderTabs(); renderSheet();
}
function renderTabs(){
  els.tabs.innerHTML='';
  state.workbook.SheetNames.forEach(name=>{ const b=document.createElement('button'); b.className='tab'+(name===state.activeSheet?' active':''); b.textContent=name; b.onclick=()=>{state.activeSheet=name; renderTabs(); renderSheet();}; els.tabs.appendChild(b); });
  els.tabs.classList.remove('hidden');
}
function renderSheet(){
  const rows=state.sheets[state.activeSheet]||[];
  const nonEmpty=rows.filter(row=>row.some(cell=>String(cell).trim()!==''));
  const cols=Math.max(0,...rows.map(row=>row.length));
  els.summary.textContent=`Hoja "${state.activeSheet}" · ${nonEmpty.length} filas con contenido · ${cols} columnas · vista previa 30 filas.`;
  els.summary.classList.remove('hidden');
  const table=document.createElement('table'); const thead=document.createElement('thead'); const hr=document.createElement('tr');
  for(let i=0;i<cols;i++){ const th=document.createElement('th'); th.textContent=columnName(i); hr.appendChild(th); }
  thead.appendChild(hr); table.appendChild(thead);
  const tbody=document.createElement('tbody');
  rows.slice(0,30).forEach(row=>{ const tr=document.createElement('tr'); for(let i=0;i<cols;i++){ const td=document.createElement('td'); const v=row[i]; td.textContent=(v===undefined||v===null||v==='')?'—':String(v); if(td.textContent==='—') td.className='empty'; tr.appendChild(td); } tbody.appendChild(tr); });
  table.appendChild(tbody); els.preview.innerHTML=''; els.preview.appendChild(table); els.preview.classList.remove('hidden');
}
function startChat(){
  els.chatLog.innerHTML=''; state.questionIndex=-1; state.answers=[];
  addMessage('pymia',`Recibí el Excel "${state.file.name}".\nLo leí en el navegador. No voy a diagnosticar; voy a preguntarte para entender el archivo.`);
  els.ownerInput.disabled=false; els.sendBtn.disabled=false; els.unknownBtn.disabled=false; els.exportBtn.disabled=false;
  nextQuestion();
}
function nextQuestion(){
  state.questionIndex += 1;
  if(state.questionIndex >= state.questions.length){ els.chatState.textContent='Completo'; addMessage('pymia','Terminé las preguntas iniciales. Podés exportar la conversación.'); els.ownerInput.disabled=true; els.sendBtn.disabled=true; els.unknownBtn.disabled=true; return; }
  const q=state.questions[state.questionIndex]; els.chatState.textContent=`Pregunta ${state.questionIndex+1}/${state.questions.length}`; addMessage('pymia',q.text);
}
function answerCurrent(unknown){
  const q=state.questions[state.questionIndex]; const answer=unknown?'NO SÉ / requiere revisión humana':els.ownerInput.value.trim();
  if(!answer){ alert('Escribí una respuesta o usá No sé.'); return; }
  state.answers.push({question_id:q.id, question:q.text, answer}); addMessage('owner',answer); els.ownerInput.value=''; nextQuestion();
}
function addMessage(role,text){ const div=document.createElement('div'); div.className='msg '+role; div.textContent=(role==='pymia'?'PymIA: ':'Dueño: ')+text; els.chatLog.appendChild(div); els.chatLog.scrollTop=els.chatLog.scrollHeight; }
function exportConversation(){
  const payload={marker:'PYMIA_SERVICE_1_EXCEL_INGESTION_CHAT_V1', created_at:new Date().toISOString(), runtime_authorized:false, production_allowed:false, final_diagnosis:false, final_accounting_result:false, file_profile:state.profile, answers:state.answers};
  const blob=new Blob([JSON.stringify(payload,null,2)],{type:'application/json;charset=utf-8'}); const url=URL.createObjectURL(blob); const a=document.createElement('a'); a.href=url; a.download='pymia_excel_ingestion_chat_'+safe(state.file?state.file.name:'case')+'.json'; document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url);
}
function safe(text){ return String(text).toLowerCase().replace(/[^a-z0-9_-]+/gi,'_').replace(/^_+|_+$/g,'').slice(0,80)||'case'; }
function formatBytes(bytes){ if(!bytes)return'0 B'; const units=['B','KB','MB','GB']; const i=Math.min(Math.floor(Math.log(bytes)/Math.log(1024)),units.length-1); return `${(bytes/Math.pow(1024,i)).toFixed(i===0?0:1)} ${units[i]}`; }
function columnName(index){ let n=index+1,s=''; while(n>0){const m=(n-1)%26; s=String.fromCharCode(65+m)+s; n=Math.floor((n-m)/26);} return s; }
</script>
</body>
</html>
'''


def build_service1_excel_ingestion_chat_web(output_file: Path = OUTPUT_FILE) -> Path:
    output_file.write_text(SERVICE1_EXCEL_INGESTION_CHAT_HTML, encoding="utf-8", newline="\n")
    return output_file


if __name__ == "__main__":
    path = build_service1_excel_ingestion_chat_web()
    print(f"Wrote {path}")
