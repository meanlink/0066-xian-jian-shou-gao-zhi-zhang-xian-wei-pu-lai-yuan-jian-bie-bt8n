from fastapi import HTTPException

def inventory(cx):
    return cx.execute("SELECT * FROM paper_references ORDER BY source,batch").fetchall()

def current_epoch(cx):
    return cx.execute("SELECT epoch FROM reference_clock").fetchone()["epoch"]

def advance_epoch(cx):
    """Advance the monotonic clock; called on any membership or identity change."""
    return cx.execute(
        "UPDATE reference_clock SET epoch=epoch+1,changed_at=now() RETURNING epoch"
    ).fetchone()["epoch"]

def secure_panel(cx,selected):
    valid=[r for r in inventory(cx) if r["accepted"] and any(r[x] for x in selected)]
    sources={row["source"] for row in valid}
    if len(sources)<2 or any(len({x["batch"] for x in valid if x["source"]==source})<2 for source in sources):
        raise HTTPException(409,"每种来源至少需两个有效参考藏批")
    return valid
