import {api,waitJob} from './base.js'
export const matches=()=>api('/api/spectra')
export async function compare(code,features){
 const {job_id}=await api('/api/spectra/'+encodeURIComponent(code),'POST',{features})
 return waitJob(job_id)
}
