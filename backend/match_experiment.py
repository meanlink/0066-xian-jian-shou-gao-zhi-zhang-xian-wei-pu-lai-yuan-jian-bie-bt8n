from fastapi import HTTPException
from psycopg.types.json import Jsonb
from cosine_match import rank,holdout_score
from impression_store import newest
from reference_bank import secure_panel

def run_job(cx,kind,payload):
    if kind!="spectrum-distance":
        raise ValueError(kind)
    cx.execute("SELECT pg_advisory_xact_lock(66017)")
    key=payload["case"]
    paper=cx.execute("SELECT phase FROM paper_cases WHERE code=%s FOR UPDATE",(key,)).fetchone()
    if not paper or paper["phase"]!="imaged":
        raise HTTPException(409,"纸样需处于已取像状态")
    fields=payload["features"]
    impression=newest(cx,key)
    if not any(impression[x] for x in fields):
        raise HTTPException(409,"选中特征向量为零，请重新选维度")
    references=secure_panel(cx,fields)
    scores=rank(references,impression,fields)
    result={"case_code":key,"revision":impression["revision"],"features":fields,
        "winner":scores[0][0],"similarities":{k:round(v,5) for k,v in scores},
        "margin":round(scores[0][1]-scores[1][1],5),"validation":holdout_score(references,fields)}
    cx.execute('''
       INSERT INTO spectrum_matches VALUES(%(case_code)s,%(revision)s,%(features)s,%(similarities)s,%(winner)s,%(margin)s,%(validation)s)
       ON CONFLICT(case_code) DO UPDATE SET revision=excluded.revision,features=excluded.features,
       similarities=excluded.similarities,winner=excluded.winner,margin=excluded.margin,validation=excluded.validation
    ''',result|{"similarities":Jsonb(result["similarities"])})
    return result
