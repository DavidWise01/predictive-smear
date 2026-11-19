import itertools,json,hashlib
from pathlib import Path
from collections import defaultdict
N=8
words=list(itertools.product((0,1),repeat=N))
def switches(w):return sum(a!=b for a,b in zip(w,w[1:]))
def run(anchor=False,limited=False):
 groups=defaultdict(set); worlds=0
 for s in words:
  if anchor and s[0]!=0:continue
  for c in words:
   if limited and switches(c)>1:continue
   o=tuple(a^b for a,b in zip(s,c));groups[o].add(s[-1]);worlds+=1
 return dict(worlds=worlds,histories=len(groups),determinate=sum(len(v)==1 for v in groups.values()),ambiguous=sum(len(v)>1 for v in groups.values()))
def stable_anchor():
 groups=defaultdict(set)
 for s in words:
  if s[0]!=0:continue
  for c in (0,1):groups[tuple(a^c for a in s)].add(s[-1])
 return dict(worlds=256,histories=len(groups),determinate=sum(len(v)==1 for v in groups.values()),ambiguous=sum(len(v)>1 for v in groups.values()))
def seal(o):
 h=bytes(32)
 for n,b in enumerate(o):h=hashlib.sha256(h+bytes((n,b))).digest()
 return h.hex()
a=(0,)*N;b=(0,)*7+(1,)
assert tuple(x^y for x,y in zip(a,a))==tuple(x^y for x,y in zip(b,b))
out={'ticks':N,'unrestricted':run(),'initial_anchor':run(True),'anchor_one_flip':run(True,True),'anchor_constant_shadow':stable_anchor(),'counterexample':{'state_a':a,'shadow_a':a,'state_b':b,'shadow_b':b,'identical_head':seal(a)}}
assert out['anchor_constant_shadow']['determinate']==256
Path(__file__).with_name('atom089_results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
