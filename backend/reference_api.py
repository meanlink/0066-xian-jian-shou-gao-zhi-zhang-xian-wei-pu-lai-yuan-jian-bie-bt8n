from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel
from core import db,require
from reference_bank import advance_epoch,inventory

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
        row=cx.execute(
            "SELECT code,accepted FROM paper_references WHERE code=%s FOR UPDATE",
            (code,)).fetchone()
        if not row:
            raise HTTPException(404,"参考藏批不存在")
        if row["accepted"] != body.accepted:
            cx.execute(
                "UPDATE paper_references SET accepted=%s WHERE code=%s",
                (body.accepted,code))
            # Any reference change permanently invalidates queued/earlier
            # comparisons; advancing the epoch keeps them stale even if the
            # reference is later restored to its previous value.
            advance_epoch(cx)
        return {"code":code,"accepted":body.accepted}
