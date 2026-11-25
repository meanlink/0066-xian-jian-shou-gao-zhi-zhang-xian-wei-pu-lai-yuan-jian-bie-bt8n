import {api} from './base.js'
export const references=()=>api('/api/reference')
export const filter=({code,accepted})=>api('/api/reference/'+encodeURIComponent(code)+'/filter','POST',{accepted:accepted==='true'})
