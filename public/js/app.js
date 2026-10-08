const $=s=>document.querySelector(s);
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const NAMES={zero_shot:'Zero-shot',few_shot:'Few-shot',role_based:'Role-based'};
async function api(url,opt){const r=await fetch((window.API_BASE||'')+url,opt);const j=await r.json().catch(()=>({}));if(!r.ok)throw new Error(j.detail||r.statusText);return j}
const err=m=>`<div class="err">${esc(m)}</div>`;
const chunkHTML=(c,i)=>`<div class="chunk"><div class="meta"><b>Chunk ${i+1}</b><span>${esc(c.source)}</span><span class="bar"><i style="width:${Math.max(c.similarity,0)*100}%"></i></span><span>similarity ${c.similarity.toFixed(2)} · distance ${c.distance.toFixed(2)}</span></div><p>${esc(c.text)}</p></div>`;
let mode='role_based';

async function loadDocs(){try{const d=await api('/api/docs-list');$('#dcount').textContent=`Library · ${d.length} documents`;$('#docs').innerHTML=d.map(x=>`<div class="doc"><span>${esc(x.name)}</span><small>${x.chunks} chunks</small></div>`).join('')}catch(e){$('#docs').innerHTML=err(e.message)}}
$('#up').onclick=()=>$('#file').click();
$('#file').onchange=async e=>{const fd=new FormData();[...e.target.files].forEach(f=>fd.append('files',f));$('#upmsg').textContent='Indexing…';try{const r=await api('/api/upload',{method:'POST',body:fd});$('#upmsg').textContent=`Added ${r.length} file(s).`;loadDocs()}catch(x){$('#upmsg').innerHTML=err(x.message)}e.target.value=''};

$('#mode').onclick=e=>{const b=e.target.closest('button');if(!b)return;mode=b.dataset.m;document.querySelectorAll('#mode button').forEach(x=>x.setAttribute('aria-pressed',x===b))};
async function ask(){const q=$('#q').value.trim();if(!q)return;$('#ans').textContent='Thinking…';$('#chunks').textContent='Searching…';
 try{const r=await api('/api/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q,mode})});
 $('#ans').innerHTML=`<p class="lbl">${NAMES[mode]}</p>`+esc(r.answer).replace(/\n/g,'<br>');
 $('#chunks').innerHTML=r.chunks.map(chunkHTML).join('')||'No chunks found.'}catch(e){$('#ans').innerHTML=err(e.message);$('#chunks').textContent=''}}
$('#go').onclick=ask;$('#q').onkeydown=e=>{if(e.key==='Enter')ask()};

$('#bq').value=["What is a vector database and why is it used in RAG?","How are text chunks converted into embeddings?","What is the difference between a list and a tuple in Python?","Why is chunk overlap useful?","What is overfitting in machine learning?"].join('\n');
$('#run').onclick=async()=>{const qs=$('#bq').value.split('\n').map(s=>s.trim()).filter(Boolean);if(!qs.length)return;
 $('#run').classList.add('busy');$('#bmsg').textContent='Running 3 templates × '+qs.length+' questions… this takes a minute.';$('#bout').innerHTML='';
 try{const r=await api('/api/benchmark',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({questions:qs})});
 const rows=r.results.map(x=>{const best=Math.max(...Object.values(x.runs).map(v=>v.scores.avg));
  return `<tr><td>${esc(x.question)}</td>${Object.keys(NAMES).map(m=>`<td class="n ${x.runs[m].scores.avg===best?'win':''}">${x.runs[m].scores.avg}</td>`).join('')}</tr>`}).join('');
 const avg=`<tr><td><b>Average</b></td>${Object.keys(NAMES).map(m=>`<td class="n"><b>${r.averages[m]}</b></td>`).join('')}</tr>`;
 const det=r.results.map(x=>`<details><summary>${esc(x.question)}</summary><div class="cols">${Object.keys(NAMES).map(m=>{const s=x.runs[m].scores;return `<div class="card"><h3>${NAMES[m]}</h3><div class="meta" style="margin-bottom:6px">accuracy ${s.accuracy} · clarity ${s.clarity} · relevance ${s.relevance}</div>${esc(x.runs[m].answer).replace(/\n/g,'<br>')}</div>`}).join('')}</div></details>`).join('');
 $('#bout').innerHTML=`<div class="card tb"><p class="lbl">Average of accuracy, clarity and relevance (out of 10)</p><table><thead><tr><th>Question</th>${Object.values(NAMES).map(n=>`<th class="n">${n}</th>`).join('')}</tr></thead><tbody>${rows}${avg}</tbody></table></div><div class="card"><p class="lbl">Verdict</p>${NAMES[r.best]} scored highest in this run. Explain why in your report using the answers below.</div><div class="card"><p class="lbl">Full answers</p>${det}</div>`;
 $('#bmsg').textContent=''}catch(e){$('#bmsg').innerHTML=err(e.message)}$('#run').classList.remove('busy')};

async function search(){const q=$('#sq').value.trim();if(!q)return;
 try{const r=await api('/api/search?q='+encodeURIComponent(q));
 $('#kw').innerHTML=r.keyword.map(c=>`<div class="chunk"><div class="meta"><b>${esc(c.source)}</b><span>matched: ${c.matches.map(esc).join(', ')}</span></div><p>${esc(c.text)}</p></div>`).join('')||'No chunk shares a word with this query.';
 $('#sm').innerHTML=r.semantic.map(chunkHTML).join('')}catch(e){$('#sm').innerHTML=err(e.message)}}
$('#sgo').onclick=search;$('#sq').onkeydown=e=>{if(e.key==='Enter')search()};

document.querySelectorAll('.tab').forEach(t=>t.onclick=()=>{document.querySelectorAll('.tab').forEach(x=>x.setAttribute('aria-selected',x===t));['ask','cmp','sem'].forEach(id=>$('#'+id).hidden=id!==t.dataset.t)});
loadDocs();
