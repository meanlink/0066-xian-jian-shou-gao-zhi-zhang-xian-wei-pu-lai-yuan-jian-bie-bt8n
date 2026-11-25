import {api} from './base.js'
import {columns} from './fiber_labels.js'
export const samples=()=>api('/api/samples')
export function capture(row){
 const readings=Object.fromEntries(columns.map(key=>[key,Number(row[key])]))
 return api('/api/samples/'+encodeURIComponent(row.case)+'/image','POST',{slide:row.slide,...readings})
}
