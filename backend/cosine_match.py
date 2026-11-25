from math import hypot
from statistics import mean

def rank(rows,target,selected):
    centroid={}
    for label in {r["source"] for r in rows}:
        peers=[r for r in rows if r["source"]==label]
        centroid[label]=[mean(r[f] for r in peers) for f in selected]
    vector=[target[f] for f in selected]
    return sorted([(label,sum(a*b for a,b in zip(center,vector))/(hypot(*center)*hypot(*vector)))
        for label,center in centroid.items()],key=lambda pair:(-pair[1],pair[0]))

def holdout_score(rows,selected):
    return sum(rank([r for r in rows if r["batch"]!=row["batch"]],row,selected)[0][0]==row["source"] for row in rows)/len(rows)
