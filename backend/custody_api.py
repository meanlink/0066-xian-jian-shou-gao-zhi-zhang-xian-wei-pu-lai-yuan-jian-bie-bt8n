from fastapi import APIRouter,Depends
from core import db,require
from shelf_logic import Custody,file_opinion
router=APIRouter(prefix="/custody")

@router.get("")
def receipts(_=Depends(require())):
    with db() as cx:
        return cx.execute("SELECT * FROM shelf_returns ORDER BY filed_at DESC").fetchall()

@router.post("/{case}")
def return_sample(case:str,data:Custody,user=Depends(require("reviewer"))):
    with db() as cx:
        return file_opinion(cx,case,data,user["email"])
