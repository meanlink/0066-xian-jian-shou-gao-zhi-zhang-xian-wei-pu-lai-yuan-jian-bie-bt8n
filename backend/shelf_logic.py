from fastapi import HTTPException
from pydantic import BaseModel,Field
from impression_store import newest
from match_experiment import present

class Custody(BaseModel):
    match_id:int
    shelf:str
    caveat:str=Field(min_length=6,max_length=180)

def file_opinion(cx,key,data,reviewer):
    cx.execute("SELECT pg_advisory_xact_lock(66017)")
    case=cx.execute("SELECT * FROM paper_cases WHERE code=%s FOR UPDATE",(key,)).fetchone()
    if not case:
        raise HTTPException(404,"纸样不存在")
    match=cx.execute("SELECT * FROM spectrum_matches WHERE id=%s AND case_code=%s",(data.match_id,key)).fetchone()
    if not match:
        raise HTTPException(409,"签单指定的比对记录不存在")
    current=newest(cx,key)
    # Re-evaluate at signing time: the match must still be the current queued
    # comparison, tied to the latest slide revision, against the live reference
    # epoch, and meet the separation thresholds. A match superseded by a newer
    # comparison or invalidated by a re-shot/reference change is not signable.
    live=cx.execute(
        """SELECT (SELECT max(id) FROM spectrum_matches WHERE case_code=%s) AS latest_id""",
        (key,)).fetchone()["latest_id"]
    epoch=cx.execute("SELECT epoch FROM reference_clock").fetchone()["epoch"]
    view=present(match,case,current["revision"] if current else None,live,epoch)
    if not view["signable"]:
        raise HTTPException(409,_reason(view))
    if data.shelf != case["shelf"]:
        raise HTTPException(409,"回库架位与借出原架不一致")
    cx.execute("INSERT INTO shelf_returns(case_code,revision,match_id,finding,shelf,reviewer,caveat) VALUES (%s,%s,%s,%s,%s,%s,%s)",
               (key,match["revision"],match["id"],match["winner"],data.shelf,reviewer,data.caveat))
    cx.execute("UPDATE paper_cases SET phase='filed' WHERE code=%s",(key,))
    return {"case_code":key,"finding":match["winner"],"shelf":data.shelf,"match_id":match["id"]}

_REASONS={
 "phase":"纸样已回库或尚未取像",
 "revision":"该比对对应的切片已被更晚的取像替换",
 "references":"参考藏批已变更，旧比对失效，需重新比对",
 "margin":"候选来源分离不足，需复拍或换参考",
 "validation":"参考藏批验证率不足，需复拍或换参考",
 "superseded":"已有更新的比对结果，旧比对不能签单",
 "pending":"比对尚未完成",
 "failed":"比对任务失败，需重新运行",
}

def _reason(view):
    state=view["state"]
    if state in _REASONS:
        return _REASONS[state]
    kinds=[k for k in view["reasons"] if k in _REASONS]
    if not kinds:
        return "当前比对不可签核"
    return _REASONS[kinds[0]]
