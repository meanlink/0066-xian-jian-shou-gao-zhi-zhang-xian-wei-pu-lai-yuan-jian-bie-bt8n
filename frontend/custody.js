import {h,empty,badge} from './base.js'
import {heading,feedback,table} from './view.js'
import {wire} from './forms.js'
import {receipts,file} from './custody_store.js'
import {samples} from './sample_store.js'
import {matches} from './match_store.js'
export async function render(root,session){
 const [cases,results,records]=await Promise.all([samples(),matches(),receipts()])
 root.innerHTML=heading('回库意见','选中的纤维谱提供材料比对意见。库管交回原架前要复核版本、可信度和架位。')+`
 <div class="return-board"><section><h2>可回库审签</h2>${cases.filter(r=>r.phase==='imaged').map(r=>{
 const m=results.find(x=>x.case_code===r.code)
 return `<article class="panel"><h3>${h(r.title)}</h3><p>原架 ${h(r.shelf)} · ${m?badge(m.winner):'待比对'}</p>${session.role==='reviewer'&&m?`
 <form class="compact-form"><input type="hidden" name="code" value="${h(r.code)}"><label>回库架位<input name="shelf" required value="${h(r.shelf)}"></label><label>归档限制<input name="caveat" required minlength="6"></label><button>归档并回库</button>${feedback}</form>`:''}</article>`}).join('')||empty('没有待回库纸样。')}</section>
 <aside class="panel"><h2>库房登记联</h2>${table(['架位','意见','限制'],records.map(r=>[r.shelf,r.finding,r.caveat]))}</aside></div>`
 for(const form of root.querySelectorAll('form'))wire(form,file,()=>render(root,session))
}
