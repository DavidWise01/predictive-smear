import numpy as np, json
from pathlib import Path
P=np.array([[[0,1],[1,0]],[[0,-1j],[1j,0]],[[1,0],[0,-1]]],complex)
I=np.eye(2,dtype=complex); word='abc'+'bca'+'cab'
signs=[1]*6+[-1]*3
def U(k,t): return np.cos(t/2)*I-1j*np.sin(t/2)*P['abc'.index(k)]
def prod(seq):
 r=I.copy()
 for m in seq:r=m@r
 return r
def err(m):return float(np.linalg.norm(m-I))
rng=np.random.default_rng(72); trials=10000; d=[]; inv=[]; axis=[]; norm=[]
for _ in range(trials):
 t=rng.uniform(0,4*np.pi,3); seq=[U(k,s*t['abc'.index(k)]) for k,s in zip(word,signs)]; f=prod(seq); back=prod([m.conj().T for m in seq[::-1]]); d.append(err(f));inv.append(err(back@f));norm.append(err(f.conj().T@f)); fixed=I.copy();axis.append(err(fixed))
angles={str(a):err(prod([U(k,s*np.deg2rad(a)) for k,s in zip(word,signs)])) for a in [0,30,60,90,120,180,360,720]}
out={'word':word,'trials':trials,'forward_closed':int(np.sum(np.array(d)<1e-10)),'inverse_closed':int(np.sum(np.array(inv)<1e-10)),'max_inverse_error':max(inv),'max_unitarity_error':max(norm),'fixed_reference_error':max(axis),'median_forward_error':float(np.median(d)),'equal_angle_forward_errors':angles}
assert out['inverse_closed']==trials
Path(__file__).with_name('atom072_results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
