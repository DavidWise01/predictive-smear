import json, math, itertools
from pathlib import Path
# Exact group arithmetic in Q(sqrt(2)), coefficients represented as rational pairs.
from fractions import Fraction as F
Z=(F(0),F(0)); O=(F(1),F(0)); H=(F(0),F(1,2))
def add(a,b):return (a[0]+b[0],a[1]+b[1])
def neg(a):return (-a[0],-a[1])
def mul(a,b):return (a[0]*b[0]+2*a[1]*b[1],a[0]*b[1]+a[1]*b[0])
def qm(a,b):
 w,x,y,z=a; W,X,Y,Zb=b
 terms=[[(w,W,1),(x,X,-1),(y,Y,-1),(z,Zb,-1)],[(w,X,1),(x,W,1),(y,Zb,1),(z,Y,-1)],[(w,Y,1),(x,Zb,-1),(y,W,1),(z,X,1)],[(w,Zb,1),(x,Y,1),(y,X,-1),(z,W,1)]]
 out=[]
 for row in terms:
  v=Z
  for p,q,s in row:v=add(v,mul(p,q) if s==1 else neg(mul(p,q)))
  out.append(v)
 return tuple(out)
def inv(q):return (q[0],*(neg(x) for x in q[1:]))
I=(O,Z,Z,Z); minus=tuple(map(neg,I)); G=[(H,H,Z,Z),(H,Z,H,Z),(H,Z,Z,H)]
group={I}; todo=[I]
while todo:
 q=todo.pop()
 for g in G:
  r=qm(g,q)
  if r not in group:group.add(r);todo.append(r)
assert len(group)==48
basis=[(Z,O,Z,Z),(Z,Z,O,Z),(Z,Z,Z,O)]
def projection(q):return tuple(qm(qm(q,b),inv(q)) for b in basis)
fibers={}
for q in group:fibers.setdefault(projection(q),[]).append(q)
assert len(fibers)==24 and all(len(v)==2 and v[0]==tuple(map(neg,v[1])) for v in fibers.values())
closure=sum(qm(a,b) in group for a in group for b in group)
assert closure==48**2
checks=sum(qm(inv(g),qm(g,q))==q for q in group for g in G)
assert checks==144
for g in G:
 q=I
 for k in range(8):
  q=qm(g,q)
  if k==3:assert q==minus
 assert q==I
out=dict(addresses=(124-4)*3+6,spinor_states=len(group),spatial_orientations=len(fibers),fiber_sizes=sorted(set(map(len,fibers.values()))),closure_checks=closure,inverse_checks=checks,full_turn_sign_checks=3,double_turn_return_checks=3,arithmetic='exact rational coefficients in Q(sqrt(2))')
Path(__file__).with_name('atom110_results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
