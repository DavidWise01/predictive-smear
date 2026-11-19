import itertools,json
from pathlib import Path
I=(1,2,3)
# Signed axes: image of each positive basis vector.
R={'xy':(2,-1,3),'xz':(3,2,-1),'yz':(1,3,-2)}
def apply(r,x):return (1 if x>0 else -1)*r[abs(x)-1]
def compose(a,b):return tuple(apply(a,x) for x in b)
def inv(a):return tuple(next(x for x in (1,-1,2,-2,3,-3) if apply(a,x)==i) for i in I)
group={I}; frontier=[I]
while frontier:
 a=frontier.pop()
 for r in R.values():
  b=compose(r,a)
  if b not in group:group.add(b);frontier.append(b)
assert len(group)==24
checks=sum(compose(inv(r),compose(r,a))==a for a in group for r in R.values())
assert checks==72
orders={}
for name,r in R.items():
 a=I
 for k in range(1,5):
  a=compose(r,a)
  if a==I:orders[name]=k;break
pairs={a+','+b:compose(R[a],R[b])==compose(R[b],R[a]) for a,b in itertools.combinations(R,2)}
# Rotations act on six axis addresses, leaving the 360 ring labels unchanged.
axes=(1,-1,2,-2,3,-3)
for r in group:assert set(apply(r,x) for x in axes)==set(axes)
out=dict(total=(124-4)*3+6,orientation_states=len(group),inverse_checks=checks,orders=orders,commute=pairs,axis_permutations=len(group),origin_fixed=True,example_xy_then_yz=compose(R['yz'],R['xy']),example_yz_then_xy=compose(R['xy'],R['yz']))
Path(__file__).with_name('atom109_results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
