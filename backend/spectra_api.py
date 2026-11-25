from typing import Literal
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from core import db,enqueue,require
router=APIRouter(prefix="/spectra")

class Features(BaseModel):
    features:list[Literal["rag","reed","bast","pore"]]=Field(min_length=2,max_length=4)

@router.get("")
def results(_=Depends(require())):
    with db() as cx:
        return cx.execute("SELECT * FROM spectrum_matches ORDER BY case_code").fetchall()

@router.post("/{case}")
def calculate(case:str,data:Features,_=Depends(require("operator","reviewer"))):
    if len(set(data.features))!=len(data.features):
        raise HTTPException(422,"特征不能重复")
    with db() as cx:
        return {"job_id":enqueue(cx,"spectrum-distance",{"case":case,**data.model_dump()})}
