import {h,empty} from './base.js'
import {heading,choices,feedback,table} from './view.js'
import {canEdit,wire} from './forms.js'
import {samples} from './sample_store.js'
import {matches,compare} from './match_store.js'
import {names} from './fiber_labels.js'
export async function render(root,session){
 const [cases,rows]=await Promise.all([samples(),matches()])
 root.innerHTML=heading('特征与比对','按藏批留组比较，区分纤维计数与孔隙读数。保留余量和独立验证率。')+`
 <div class="match-book">${canEdit(session)?`<form class="panel compact-form"><h2>选取特征</h2><label>纸样<select name="code" required>${choices(cases.filter(r=>r.phase==='imaged'),r=>r.title)}</select></label>
 <fieldset><legend>至少选两个</legend>${Object.entries(names).map(([k,v])=>`<label><input type="checkbox" name="feature" value="${k}" ${k==='pore'?'':'checked'}>${h(v)}</label>`).join('')}</fieldset><button>后台比对</button>${feedback}</form>`:''}
 <section>${rows.map(r=>`<article class="match-line"><h2>${h(r.case_code)} · ${h(r.winner)}</h2><p>${r.features.map(f=>h(names[f])).join('、')} · v${r.revision}</p>
 <p>候选余量 ${r.margin.toFixed(3)} / 藏批验证 ${Math.round(r.validation*100)}%</p>
 ${table(['来源','余弦相似度'],Object.entries(r.similarities))}</article>`).join('')||empty('暂无比对，选择一件已有切片的纸样后运行。')}</section></div>`
 const form=root.querySelector('form')
 wire(form,data=>compare(data.code,new FormData(form).getAll('feature')),()=>render(root,session))
}
