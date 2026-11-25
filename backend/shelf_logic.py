from fastapi import HTTPException
from pydantic import BaseModel,Field
from impression_store import newest

class Custody(BaseModel):
    shelf:str
    caveat:str=Field(min_length=6,max_length=180)

def file_opinion(cx,key,data,reviewer):
    cx.execute("SELECT pg_advisory_xact_lock(66017)")
    case=cx.execute("SELECT * FROM paper_cases WHERE code=%s FOR UPDATE",(key,)).fetchone()
    row=cx.execute("SELECT * FROM spectrum_matches WHERE case_code=%s",(key,)).fetchone()
    current=newest(cx,key)
    if not case or case["phase"]!="imaged" or not row or not current or current["revision"]!=row["revision"]:
        raise HTTPException(409,"最新取像没有有效比对结果")
    if row["margin"] < .12 or row["validation"] < .8:
        raise HTTPException(409,"候选来源分离不足，需复拍或换参考")
    if data.shelf != case["shelf"]:
        raise HTTPException(409,"回库架位与借出原架不一致")
    cx.execute("INSERT INTO shelf_returns(case_code,revision,finding,shelf,reviewer,caveat) VALUES (%s,%s,%s,%s,%s,%s)",
               (key,row["revision"],row["winner"],data.shelf,reviewer,data.caveat))
    cx.execute("UPDATE paper_cases SET phase='filed' WHERE code=%s",(key,))
    return {"case_code":key,"finding":row["winner"],"shelf":data.shelf}
