const $=s=>document.querySelector(s),messages=$('#messages'),form=$('#ask-form'),input=$('#question'),submit=$('#submit-button'),measure=$('#measure-select'),statusChip=$('#package-status'),sideRail=$('#side-rail'),grid=$('.product-grid'),sourceList=$('#source-list'),sourceCount=$('#source-count'),traceButton=$('#trace-button'),traceDialog=$('#trace-dialog'),traceContent=$('#trace-content');
let sessionId='',awaitingResponse=false,lastTrace=null;
const esc=s=>String(s??'').replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]));

function message(role,text,actions=[]){
  const node=document.createElement('article');node.className=`message ${role}`;
  const buttons=actions.length?`<div class="response-actions">${actions.map(action=>`<button type="button" data-action="${esc(action.id)}">${esc(action.label)}</button>`).join('')}</div>`:'';
  node.innerHTML=`<span class="avatar">${role==='user'?'YOU':'MN'}</span><div><small>${role==='user'?'You':'Navigator'}</small><p>${esc(text)}</p>${buttons}</div>`;
  messages.append(node);messages.scrollTop=messages.scrollHeight;
}
function sources(rows){const visible=(rows||[]).length>0;sideRail.hidden=!visible;grid.classList.toggle('has-faq',visible);if(!visible)return;sourceCount.textContent=rows.length;sourceList.innerHTML=rows.map(row=>`<article class="faq-card"><span class="source-type">${esc(row.source_type.replace('_',' '))}</span><strong>${esc(row.title)}</strong><p>${esc(row.text.slice(0,340))}${row.text.length>340?'…':''}</p><small>${esc(row.citation)}</small></article>`).join('')}
function trace(data){lastTrace=data.trace;traceButton.disabled=!lastTrace;if(!lastTrace)return;const facts=Object.entries(lastTrace.facts_used||{}).map(([key,value])=>`<div class="trace-step"><b>${esc(key.replaceAll('_',' '))}</b>${esc(Array.isArray(value)?value.join(', '):value)}</div>`).join('');const cites=(lastTrace.citations||[]).map(value=>`<div class="trace-step"><b>Source</b>${esc(value)}</div>`).join('');traceContent.innerHTML=`<div class="trace-step"><b>Intent</b>${esc(lastTrace.intent)}</div>${facts}${lastTrace.open_condition?`<div class="trace-step open"><b>Open condition</b>${esc(lastTrace.open_condition.replaceAll('_',' '))}</div>`:''}${cites}<div class="trace-step"><b>Source authority</b>${esc(lastTrace.source_priority)}</div>${lastTrace.conflict?`<div class="trace-step alert"><b>Potential conflict</b>${esc(lastTrace.conflict)}</div>`:''}<div class="trace-step"><b>Runtime</b>${esc(lastTrace.retrieval_backend)} · ${esc(lastTrace.llm_mode)}</div>`}
function render(data){
  sessionId=data.session_id||sessionId;
  if(data.phi_masked)message('warning',`${data.privacy_notice} Masked text: ${data.masked_question}`);
  const actions=[...(data.actions||[])];if(['ANSWERED','RESOLVED','INSUFFICIENT_EVIDENCE'].includes(data.status))actions.push({id:'start_new',label:'Start a new question'});
  message('assistant',data.message,actions);sources([...(data.sources||[]),...(data.faqs||[])].filter((row,index,all)=>all.findIndex(x=>x.id===row.id)===index));trace(data);
  awaitingResponse=data.status==='FOLLOW_UP';
  input.placeholder=awaitingResponse?'Answer the follow-up, or choose “I don’t know”…':sessionId?'Continue this investigation, or start a new question…':'Ask a MY2026 measure question…';
  submit.textContent=awaitingResponse?'Respond':sessionId?'Continue':'Ask';
}
async function post(url,body){const response=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}),data=await response.json();if(!response.ok)throw Error(data.error||'Request failed');return data}
async function sendResponse(text){message('user',text==='UNKNOWN'?"I don’t know":text);submit.disabled=true;try{render(await post(`/api/sessions/${sessionId}/respond`,{response:text}))}catch(error){message('warning',error.message)}finally{submit.disabled=false;input.focus()}}
function resetConversation(){sessionId='';awaitingResponse=false;lastTrace=null;traceButton.disabled=true;sources([]);messages.innerHTML='<article class="message assistant"><span class="avatar">MN</span><div><small>Navigator</small><p>What would you like to clarify next?</p></div></article>';input.placeholder='Ask a MY2026 measure question…';submit.textContent='Ask';input.focus()}
form.addEventListener('submit',async event=>{event.preventDefault();const text=input.value.trim();if(!text)return;input.value='';if(sessionId){await sendResponse(text);return}message('user',text);submit.disabled=true;try{render(await post('/api/chat',{question:text,measure_id:measure.value,measurement_year:2026}))}catch(error){message('warning',error.message)}finally{submit.disabled=false;input.focus()}});
document.addEventListener('click',async event=>{
  if(event.target.dataset.prompt){input.value=event.target.dataset.prompt;input.focus();return}
  const action=event.target.dataset.action;if(!action)return;
  if(action==='start_new'){resetConversation();return}
  if(action==='unknown'){await sendResponse('UNKNOWN');return}
  event.target.disabled=true;try{render(await post(`/api/sessions/${sessionId}/action`,{action}))}catch(error){message('warning',error.message)}finally{event.target.disabled=false}
});
traceButton.addEventListener('click',()=>traceDialog.showModal());$('#trace-close').addEventListener('click',()=>traceDialog.close());$('#trace-done').addEventListener('click',()=>traceDialog.close());
measure.addEventListener('change',()=>{$('#scope-measure').textContent=measure.value;resetConversation()});
async function init(){try{const [packageResponse,indexResponse]=await Promise.all([fetch('/api/packages'),fetch('/api/index/status')]);const packageData=await packageResponse.json(),indexData=await indexResponse.json();measure.innerHTML=(packageData.packages||[]).map(item=>`<option value="${esc(item.measure_id)}">${esc(item.display_name)}</option>`).join('');statusChip.textContent=indexData.chunks_indexed?`${indexData.chunks_indexed} sources ready`:'Index required';statusChip.classList.toggle('warn',!indexData.chunks_indexed)}catch{statusChip.textContent='Status unavailable';statusChip.classList.add('warn')}}init();

