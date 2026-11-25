from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel
from core import db,require
from reference_bank import inventory

router=APIRouter(prefix="/reference")

class Release(BaseModel):
    accepted:bool

@router.get("")
def catalogue(_=Depends(require())):
    with db() as cx:
        return inventory(cx)

@router.post("/{code}/filter")
def release(code:str,body:Release,_=Depends(require("reviewer"))):
    with db() as cx:
        cx.execute("SELECT pg_advisory_xact_lock(66017)")
        row=cx.execute("UPDATE paper_references SET accepted=%s WHERE code=%s RETURNING code", (body.accepted,code)).fetchone()
        if not row:
            raise HTTPException(404,"参考藏批不存在")
        cx.execute("DELETE FROM spectrum_matches m USING paper_cases c WHERE c.code=m.case_code AND c.phase<>'filed'")
        return {"code":code,"accepted":body.accepted}
