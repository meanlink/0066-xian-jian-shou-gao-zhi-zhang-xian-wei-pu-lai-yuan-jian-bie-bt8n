from fastapi import HTTPException
from pydantic import BaseModel,Field

class Slide(BaseModel):
    rag:int=Field(ge=0,le=100)
    reed:int=Field(ge=0,le=100)
    bast:int=Field(ge=0,le=100)
    pore:int=Field(ge=0,le=100)
    slide:str=Field(pattern=r"^[A-Za-z0-9-]+[.]tif$")

def newest(cx,case):
    return cx.execute("SELECT * FROM paper_impressions WHERE case_code=%s ORDER BY revision DESC LIMIT 1",(case,)).fetchone()

def specimens(cx):
    cases=cx.execute("SELECT * FROM paper_cases ORDER BY code").fetchall()
    return [row|{"current":newest(cx,row["code"])} for row in cases]

def capture(cx,case,data):
    row=cx.execute("SELECT phase FROM paper_cases WHERE code=%s FOR UPDATE",(case,)).fetchone()
    if not row or row["phase"]=="filed":
        raise HTTPException(409,"托盘已回库或不存在，不能追加切片")
    if not any((data.rag,data.reed,data.bast)):
        raise HTTPException(409,"三个纤维计数均为零，无法用于比对")
    existing=newest(cx,case)
    rev=1 if not existing else existing["revision"]+1
    cx.execute('''
       INSERT INTO paper_impressions
       VALUES(%(case)s,%(revision)s,%(rag)s,%(reed)s,%(bast)s,%(pore)s,%(slide)s)
    ''',data.model_dump()|{"revision":rev,"case":case})
    cx.execute("UPDATE paper_cases SET phase='imaged' WHERE code=%s",(case,))
    return {"revision":rev}
