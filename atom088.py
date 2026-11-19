import itertools,json
from pathlib import Path
def observe(t,c,e): return tuple(t^c^v for v in e)
rows=[]
for t,c in itertools.product(range(2),repeat=2):
 for e in itertools.product(range(2),repeat=7):
  rows.append((t,c,e,observe(t,c,e)))
by={}
for t,c,e,o in rows: by.setdefault(o,set()).add(t)
assert all(v=={0,1} for v in by.values())
assert all(observe(t,c,e)==observe(t^1,c^1,e) for t,c,e,o in rows)
worlds=[]
for t,c in itertools.product(range(2),repeat=2):
 o=observe(t,c,(0,)*7)
 worlds.append(dict(truth=t,common_flip=c,observation=''.join(map(str,o)),anchor=t))
u=[r for r in rows if len(set(r[3]))==1]
out=dict(worlds=len(rows),distinct_observations=len(by),ambiguous_observations=sum(len(v)>1 for v in by.values()),symmetry_pairs=len(rows)//2,unanimous_worlds=len(u),unanimous_wrong=sum(o[0]!=t for t,c,e,o in u),unanimous_correct=sum(o[0]==t for t,c,e,o in u),ambiguity_held=len(rows),ideal_anchor_correct=sum(t==w['anchor'] for t,w in zip([0,0,1,1],worlds)),ideal_anchor_worlds=worlds)
Path(__file__).with_name('atom088_results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
