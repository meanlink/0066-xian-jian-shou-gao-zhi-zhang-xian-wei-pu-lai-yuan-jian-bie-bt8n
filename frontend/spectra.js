import {h,empty,badge,notice} from './base.js'
import {heading,choices,feedback,table} from './view.js'
import {canEdit} from './forms.js'
import {samples} from './sample_store.js'
import {matches,compare} from './match_store.js'
import {names} from './fiber_labels.js'

const verdict = m => m.signable
  ? badge('可签核', 'ready')
  : m.state === 'pending' ? badge('计算中', 'held')
  : m.state === 'failed' ? badge('失败', 'held')
  : m.state === 'superseded' ? badge('旧比对 · 仅回看', 'held')
  : badge('已失效 · 仅回看', 'held')

export async function render(root,session){
 const [cases,rows]=await Promise.all([samples(),matches()])
 root.innerHTML=heading('特征与比对','排队时即冻结切片修订与参考藏批，旧任务照常算完留档；重拍或改参考后旧比对只供回看，不再可签。')+`
 <div class="match-book">${canEdit(session)?`<form class="panel compact-form"><h2>选取特征</h2><label>纸样<select name="code" required>${choices(cases.filter(r=>r.phase==='imaged'),r=>r.title)}</select></label>
 <fieldset><legend>至少选两个</legend>${Object.entries(names).map(([k,v])=>`<label><input type="checkbox" name="feature" value="${k}" ${k==='pore'?'':'checked'}>${h(v)}</label>`).join('')}</fieldset><button>后台比对</button>${feedback}</form>`:''}
 <section>${rows.map(r=>`<article class="match-line"><h2>${h(r.case_code)} · ${h(r.winner||'—')} ${verdict(r)}</h2>
 <p>冻结切片 v${r.revision} · 参考第 ${r.reference_epoch} 版 · ${r.features.map(f=>h(names[f])).join('、')}</p>
 <p>候选余量 ${r.margin==null?'—':r.margin.toFixed(3)} / 藏批验证 ${r.validation==null?'—':Math.round(r.validation*100)+'%'}</p>
 ${r.similarities?table(['来源','余弦相似度'],Object.entries(r.similarities)):empty(r.error||'比对尚未完成。')}</article>`).join('')||empty('暂无比对，选择一件已有切片的纸样后运行。')}</section></div>`
 const form=root.querySelector('form')
 if(!form) return
 form.onsubmit=async event=>{
  event.preventDefault()
  const button=form.querySelector('button')
  button.disabled=true
  try{
   const reply=await compare(form.elements.code.value,new FormData(form).getAll('feature'))
   await render(root,session)
   const status=root.querySelector('[role=status]')
   if(status) notice(status,reply?.message||'比对完成',Boolean(reply?.error))
  }catch(error){
   const status=form.querySelector('[role=status]')
   if(status) notice(status,error.message,true)
   button.disabled=false
  }
 }
}
