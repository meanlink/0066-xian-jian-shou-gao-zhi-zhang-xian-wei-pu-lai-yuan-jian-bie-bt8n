from typing import Literal
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from core import db,require
from match_experiment import list_matches,queue_comparison
router=APIRouter(prefix="/spectra")

class Features(BaseModel):
    features:list[Literal["rag","reed","bast","pore"]]=Field(min_length=2,max_length=4)

@router.get("")
def results(_=Depends(require())):
    with db() as cx:
        return list_matches(cx)

@router.post("/{case}")
def calculate(case:str,data:Features,_=Depends(require("operator","reviewer"))):
    if len(set(data.features))!=len(data.features):
        raise HTTPException(422,"特征不能重复")
    with db() as cx:
        return queue_comparison(cx,case,data.features)
