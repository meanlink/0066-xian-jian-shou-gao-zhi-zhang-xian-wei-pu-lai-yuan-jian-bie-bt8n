"""Queue and run spectrum comparisons against a frozen snapshot.

A comparison freezes what it is allowed to look at when it is queued: the slide
revision and the set of accepted reference batches. Later re-imaging or
reference-bank changes therefore never rewrite an already queued result; they
only make it ineligible for signing. Comparisons are immutable rows ordered by
queue position, so a slow older task can finish without displacing a newer one.
"""
import json

from fastapi import HTTPException
from psycopg.types.json import Jsonb
from cosine_match import rank, holdout_score
from core import enqueue
from impression_store import newest
from reference_bank import current_epoch, secure_panel

KIND = "spectrum-distance"


def queue_comparison(cx, key, features):
    """Freeze the slice and reference panel, then commit the job atomically."""
    cx.execute("SELECT pg_advisory_xact_lock(66017)")
    paper = cx.execute(
        "SELECT phase FROM paper_cases WHERE code=%s FOR UPDATE", (key,)
    ).fetchone()
    if not paper:
        raise HTTPException(404, "纸样不存在")
    if paper["phase"] != "imaged":
        raise HTTPException(409, "纸样需处于已取像状态")
    impression = newest(cx, key)
    if not impression:
        raise HTTPException(409, "纸样尚无可比对的切片")
    if not any(impression[f] for f in features):
        raise HTTPException(409, "选中特征向量为零，请重新选维度")
    # Validate the panel at queue time so we never enqueue a task that cannot run.
    references = secure_panel(cx, features)
    epoch = current_epoch(cx)
    match_id = cx.execute(
        """INSERT INTO spectrum_matches
           (case_code,revision,reference_epoch,features,reference_snapshot,status)
           VALUES (%s,%s,%s,%s,%s,'pending') RETURNING id""",
        (key, impression["revision"], epoch, features, Jsonb(references)),
    ).fetchone()["id"]
    job_id = enqueue(cx, KIND, {"match_id": match_id})
    cx.execute("UPDATE spectrum_matches SET job_id=%s WHERE id=%s", (job_id, match_id))
    return {"job_id": job_id, "match_id": match_id}


def run_job(cx, kind, payload):
    if kind != KIND:
        raise ValueError(kind)
    cx.execute("SELECT pg_advisory_xact_lock(66017)")
    match = cx.execute(
        "SELECT * FROM spectrum_matches WHERE id=%s FOR UPDATE",
        (payload["match_id"],),
    ).fetchone()
    if not match:
        raise HTTPException(409, "比对任务不存在")
    if match["status"] != "pending":
        # Already settled; do not recompute or let a late run rewrite history.
        return results_payload(match)
    impression = cx.execute(
        "SELECT * FROM paper_impressions WHERE case_code=%s AND revision=%s",
        (match["case_code"], match["revision"]),
    ).fetchone()
    if not impression:
        raise HTTPException(409, "冻结的切片修订已不存在")
    fields = match["features"]
    if not any(impression[f] for f in fields):
        raise HTTPException(409, "选中特征向量为零，请重新选维度")
    # Compute against the frozen snapshot, never the live reference bank.
    references = match["reference_snapshot"]
    if isinstance(references, str):
        references = json.loads(references)
    scores = rank(references, impression, fields)
    result = {
        "match_id": match["id"], "case_code": match["case_code"],
        "revision": match["revision"], "reference_epoch": match["reference_epoch"],
        "features": fields, "winner": scores[0][0],
        "similarities": {k: round(v, 5) for k, v in scores},
        "margin": round(scores[0][1] - scores[1][1], 5),
        "validation": holdout_score(references, fields),
    }
    cx.execute(
        """UPDATE spectrum_matches SET status='ready',similarities=%s,winner=%s,
           margin=%s,validation=%s,computed_at=now() WHERE id=%s""",
        (Jsonb(result["similarities"]), result["winner"], result["margin"],
         result["validation"], match["id"]),
    )
    return result


def mark_failed(cx, match_id, error):
    cx.execute(
        """UPDATE spectrum_matches SET status='failed',error=%s,computed_at=now()
           WHERE id=%s AND status='pending'""",
        (error, match_id),
    )


def list_matches(cx):
    """Return every comparison with a view-only / signable verdict computed now."""
    rows = cx.execute(
        "SELECT * FROM spectrum_matches ORDER BY case_code,id"
    ).fetchall()
    cases = {
        r["code"]: r for r in cx.execute(
            "SELECT * FROM paper_cases"
        ).fetchall()
    }
    revisions = {
        r["case_code"]: r["revision"] for r in cx.execute(
            "SELECT case_code,max(revision) AS revision FROM paper_impressions GROUP BY case_code"
        ).fetchall()
    }
    latest = {
        r["case_code"]: r["id"] for r in cx.execute(
            "SELECT case_code,max(id) AS id FROM spectrum_matches GROUP BY case_code"
        ).fetchall()
    }
    epoch = current_epoch(cx)
    return [present(row, cases.get(row["case_code"]),
                     revisions.get(row["case_code"]), latest.get(row["case_code"]),
                     epoch) for row in rows]


def present(row, case, revision, latest_id, epoch):
    snapshot = row["reference_snapshot"] or []
    out = {
        "id": row["id"], "case_code": row["case_code"], "revision": row["revision"],
        "reference_epoch": row["reference_epoch"], "features": row["features"],
        "status": row["status"], "similarities": row["similarities"],
        "winner": row["winner"], "margin": row["margin"], "validation": row["validation"],
        "error": row["error"], "queued_at": row["queued_at"], "computed_at": row["computed_at"],
        "reference_codes": [r["code"] for r in snapshot],
        "current": latest_id == row["id"],
    }
    reasons = []
    if latest_id != row["id"]:
        # A newer comparison was queued (or ran); this one only remains for review,
        # even if this older task happens to finish later.
        state, reasons = "superseded", ["superseded"]
    elif row["status"] == "pending":
        state = "pending"
    elif row["status"] == "failed":
        state = "failed"
    else:
        if not case or case["phase"] != "imaged":
            reasons.append("phase")
        if revision is None or revision != row["revision"]:
            reasons.append("revision")
        if row["reference_epoch"] != epoch:
            reasons.append("references")
        if row["margin"] is None or row["margin"] < .12:
            reasons.append("margin")
        if row["validation"] is None or row["validation"] < .8:
            reasons.append("validation")
        state = "stale" if reasons else "signable"
    out["state"] = state
    out["reasons"] = reasons
    out["signable"] = state == "signable"
    return out


def results_payload(match):
    similarities = match["similarities"]
    if isinstance(similarities, str):
        similarities = json.loads(similarities)
    return {
        "match_id": match["id"], "case_code": match["case_code"],
        "revision": match["revision"], "reference_epoch": match["reference_epoch"],
        "features": match["features"], "winner": match["winner"],
        "similarities": similarities, "margin": match["margin"],
        "validation": match["validation"], "status": match["status"],
    }
