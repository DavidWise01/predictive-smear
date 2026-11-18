import numpy as np,json
from pathlib import Path
P=np.array([[[0,1],[1,0]],[[0,-1j],[1j,0]],[[1,0],[0,-1]]],complex); I=np.eye(2)
def u(axis,a):return np.cos(a/2)*I-1j*np.sin(a/2)*P[axis]
def product(seq):
 r=I.astype(complex)
 for m in seq:r=m@r
 return r
def error(m):return float(np.linalg.norm(m-I))
rng=np.random.default_rng(51); rows={k:[] for k in ['inverse_reverse','inverse_same','reverse_only']}
for _ in range(10000):
 axes=rng.integers(0,3,12); angles=rng.uniform(0,4*np.pi,12); f=[u(a,t) for a,t in zip(axes,angles)]; inv=[m.conj().T for m in f]
 for k,r in zip(rows,[inv[::-1],inv,f[::-1]]):rows[k].append(error(product(r)@product(f)))
out={k:{'trials':len(v),'closed':int(np.sum(np.array(v)<1e-10)),'median_error':float(np.median(v)),'max_error':max(v)} for k,v in rows.items()}
Path(__file__).with_name('spinor051_results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
