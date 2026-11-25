import {h,badge} from './base.js'
import {heading,feedback} from './view.js'
import {wire} from './forms.js'
import {filter,references} from './reference_store.js'
import {strip} from './fiber_strip.js'
export async function render(root,session){
 const data=await references()
 root.innerHTML=heading('参考藏批','对参考材料去重核准。改变纳入范围会废止待回库的匹配。')+`<div class="library-drawer">${Array.from(Map.groupBy(data,r=>r.source),([source,rows])=>`
 <section class="panel"><h2>${h(source)}</h2>${rows.map(r=>`<article><div><strong>${h(r.batch)}</strong> ${badge(r.accepted?'已纳入':'隔离',r.accepted?'ready':'held')}</div>${strip(r)}
 ${session.role==='reviewer'?`<form><input name="code" type="hidden" value="${h(r.code)}"><input name="accepted" type="hidden" value="${!r.accepted}"><button class="quiet">${r.accepted?'隔离':'纳入'}</button>${feedback}</form>`:''}</article>`).join('')}</section>`).join('')}</div>`
 for (const form of root.querySelectorAll('form'))wire(form,filter,()=>render(root,session))
}
