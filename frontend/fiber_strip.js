import {h} from './base.js'
import {columns,names} from './fiber_labels.js'
export function strip(record) {
 return `<dl class="fiber-strip">${columns.map(k=>`<div><dt>${h(names[k])}</dt><dd><meter min="0" max="100" value="${record[k]}"></meter><output>${record[k]}</output></dd></div>`).join('')}</dl>`
}
