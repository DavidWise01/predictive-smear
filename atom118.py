from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json
O=(0,0,0)
D=[v for v in product((-1,0,1),repeat=3) if v!=O]
pairs=[(v,tuple(-x for x in v)) for v in D if v>O]
assert len(pairs)==13
# Four push and four pull substeps, simultaneous conservative transfers.
a=F(1,104); b=a*F(41,40)
def cycle(m,pull):
 for rate,rev in [(a,False)]*4+[(pull,True)]*4:
  nxt=m.copy()
  for v in D:
   s,t=(v,O) if rev else (O,v)
   q=rate*m[s]; nxt[s]-=q; nxt[t]+=q
  m=nxt
  assert sum(m.values())==1 and min(m.values())>=0
  assert all(m[v]==m[w] for v,w in pairs)
 return m
rows={}
for name,pull in [('symmetric',a),('biased',b)]:
 m={v:F(int(v==O)) for v in [O]+D}; hist=[]
 for k in range(1,65):
  m=cycle(m,pull)
  if k in (1,2,4,8,13,32,64):hist.append(dict(cycle=k,center=float(m[O]),shell=float(1-m[O])))
 A=(1-26*a)**4; B=(1-pull)**4
 equilibrium=(1-B)/(1-A*B)
 rows[name]=dict(history=hist,equilibrium_center=float(equilibrium),equilibrium_exact=str(equilibrium),net_cycle_flux=float(m[O]-1))
out=dict(addresses=366,channels=13,push=str(a),pull=str(b),rows=rows,conservation_checks=2*64*8,model='star transport; all reciprocal pairs symmetric; four push then four pull')
Path(__file__).with_name('atom118_results.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
