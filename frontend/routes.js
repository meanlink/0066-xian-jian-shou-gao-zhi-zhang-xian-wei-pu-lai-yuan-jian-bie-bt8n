import {mount} from './base.js'
import {render as samples} from './samples.js'
import {render as reference} from './reference.js'
import {render as spectra} from './spectra.js'
import {render as custody} from './custody.js'

const pages = {
  samples: '观察托盘',
  reference: '参考藏批',
  spectra: '特征与比对',
  custody: '回库意见'
}
const renderers = {samples, reference, spectra, custody}
mount({title: '纤笺 · 手稿纸张纤维谱来源鉴别', kicker: '西廊纸样研究室 · 纤维档案', pages, render: (key, root, session) => renderers[key](root, session)})
