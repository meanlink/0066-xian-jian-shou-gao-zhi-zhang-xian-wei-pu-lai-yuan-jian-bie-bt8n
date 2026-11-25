import {api} from './base.js'
export const receipts=()=>api('/api/custody')
export const file=({code,match_id,shelf,caveat})=>api('/api/custody/'+encodeURIComponent(code),'POST',{match_id:Number(match_id),shelf,caveat})