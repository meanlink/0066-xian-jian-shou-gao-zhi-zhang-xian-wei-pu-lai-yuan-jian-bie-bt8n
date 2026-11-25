from fastapi import APIRouter,Depends
from core import db,require
from impression_store import Slide,capture,specimens
router=APIRouter(prefix="/samples")

@router.get("")
def samples(_=Depends(require())):
    with db() as cx:
        return specimens(cx)

@router.post("/{key}/image")
def recollect(key:str,data:Slide,_=Depends(require("operator","reviewer"))):
    with db() as cx:
        return capture(cx,key,data)
