import {h,empty,badge} from './base.js'
import {heading,feedback,table} from './view.js'
import {wire} from './forms.js'
import {receipts,file} from './custody_store.js'
import {samples} from './sample_store.js'
import {matches} from './match_store.js'
const verdict = m => m.signable ? badge('可签核','ready')
  : m.state==='pending' ? badge('计算中','held')
  : m.state==='failed' ? badge('失败','held')
  : badge('仅回看','held')
export async function render(root,session){
 const [cases,results,records]=await Promise.all([samples(),matches(),receipts()])
 root.innerHTML=heading('回库意见','签单只认当下仍有效、且由复核员此刻核过的那份比对。旧比对、失效比对仅供回看，不能签回库单。')+`
 <div class="return-board"><section><h2>可回库审签</h2>${cases.filter(r=>r.phase==='imaged').map(r=>{
 const signable=results.filter(x=>x.case_code===r.code&&x.signable).sort((a,b)=>b.id-a.id)[0]
 const viewable=results.filter(x=>x.case_code===r.code&&!x.signable).sort((a,b)=>b.id-a.id)
 return `<article class="panel"><h3>${h(r.title)}</h3><p>原架 ${h(r.shelf)} · ${signable?badge(signable.winner,'approved'):badge('暂无可签比对','held')}</p>
 ${session.role==='reviewer'&&signable?`
 <form class="compact-form"><input type="hidden" name="match_id" value="${h(signable.id)}"><input type="hidden" name="code" value="${h(r.code)}">
 <p>签核比对 #${h(signable.id)} · 冻结 v${h(signable.revision)} · 参考第 ${h(signable.reference_epoch)} 版</p>
 <label>回库架位<input name="shelf" required value="${h(r.shelf)}"></label><label>归档限制<input name="caveat" required minlength="6"></label><button>归档并回库</button>${feedback}</form>`:''}
 ${viewable.length?`<details><summary>仅回看比对 ${viewable.length} 份</summary>${viewable.map(m=>`<p><small>#${h(m.id)} · v${h(m.revision)} · 参考第 ${h(m.reference_epoch)} 版 ${verdict(m)}</small></p>`).join('')}</details>`:''}
 </article>`}).join('')||empty('没有待回库纸样。')}</section>
 <aside class="panel"><h2>库房登记联</h2>${table(['架位','意见','限制'],records.map(r=>[r.shelf,r.finding,r.caveat]))}</aside></div>`
 for(const form of root.querySelectorAll('form'))wire(form,file,()=>render(root,session))
}