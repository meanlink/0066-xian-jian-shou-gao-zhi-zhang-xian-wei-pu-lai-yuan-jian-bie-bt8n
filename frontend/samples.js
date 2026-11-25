import {h,badge} from './base.js'
import {heading,choices,feedback} from './view.js'
import {canEdit,wire} from './forms.js'
import {samples,capture} from './sample_store.js'
import {names,phase} from './fiber_labels.js'
import {strip} from './fiber_strip.js'
export async function render(root,session) {
 const rows=await samples()
 root.innerHTML=heading('观察托盘','纸样按库架编号流转。重复取像保存新修订，原底片继续留档；新修订会使旧比对只能回看、不能签单。')+`
 <div class="sample-bench"><section>${rows.map(r=>`<article class="sample-slip"><small>${h(r.code)} / ${h(r.shelf)}</small><h2>${h(r.title)}</h2>
 ${badge(phase[r.phase],r.phase==='filed'?'approved':'')}${r.current?`<p>${h(r.current.slide)} · v${r.current.revision}</p>${strip(r.current)}`:'<p>待填写切片文件与纤维观察。</p>'}</article>`).join('')}</section>
 ${canEdit(session)?`<form class="panel compact-form"><h2>追加切片观察</h2><label>托盘<select name="case">${choices(rows.filter(x=>x.phase!=='filed'),r=>r.title)}</select></label><label>切片文件<input name="slide" placeholder="MS42-a.tif" required></label>
 ${Object.entries(names).map(([k,n])=>`<label>${h(n)}<input name="${k}" type="number" min="0" max="100" required></label>`).join('')}
 <button>保存观察</button>${feedback}</form>`:''}</div>`
 wire(root.querySelector('form'),capture,()=>render(root,session))
}
