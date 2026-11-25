import {api} from './base.js'
export const receipts=()=>api('/api/custody')
export const file=({code,shelf,caveat})=>api('/api/custody/'+encodeURIComponent(code),'POST',{shelf,caveat})
