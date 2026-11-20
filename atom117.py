import itertools,json
from pathlib import Path
D=list(itertools.product((-1,0,1),repeat=3))
O=(0,0,0); shell=[v for v in D if v!=O]
def rank(v):return sum(x!=0 for x in v)
def opposite(v):return tuple(-x for x in v)
classes={str(k):sum(rank(v)==k for v in shell) for k in (1,2,3)}
assert classes=={'1':6,'2':12,'3':8}
assert all(opposite(v) in shell and opposite(opposite(v))==v for v in shell)
pairs={tuple(sorted((v,opposite(v)))) for v in shell};assert len(pairs)==13
# Face-only transport: Manhattan distance one; diagonal observation is separate.
links=[(a,b) for a in D for b in D if sum(abs(x-y) for x,y in zip(a,b))==1]
assert len(links)==108 and all((b,a) in links for a,b in links)
# Simultaneous conservative diffusion with integer mass and exact rational arithmetic.
from fractions import Fraction as F
mass={v:F(int(v==O)) for v in D}; history=[]
for step in range(13):
    nxt=mass.copy()
    for a,b in links:
        flow=mass[a]/12;nxt[a]-=flow;nxt[b]+=flow
    mass=nxt;assert sum(mass.values())==1 and min(mass.values())>=0
    assert all(mass[v]==mass[opposite(v)] for v in D)
    history.append(dict(step=step+1,center=float(mass[O]),face=float(sum(mass[v] for v in shell if rank(v)==1)),edge=float(sum(mass[v] for v in shell if rank(v)==2)),corner=float(sum(mass[v] for v in shell if rank(v)==3))))
out=dict(addresses=(124-4)*3+6,neighbors=len(shell),classes=classes,opposite_pairs=len(pairs),directed_face_links=len(links),undirected_face_links=len(links)//2,conservation_steps=13,history=history)
Path(__file__).with_name('atom117_results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
