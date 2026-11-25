import {api,waitJob} from './base.js'
export const matches=()=>api('/api/spectra')

// Queue a comparison and wait for its own job to settle. A failed or still
// queued job is reported but does not hide the record; the page re-renders the
// real, possibly stale-but-viewable state afterwards.
export async function compare(code,features){
 const {job_id}=await api('/api/spectra/'+encodeURIComponent(code),'POST',{features})
 if(!job_id) return {message:'比对已排队'}
 try { await waitJob(job_id); return {message:'比对完成'} }
 catch(error){ return {message:error.message,error:true} }
}
