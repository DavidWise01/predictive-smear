import numpy as np,json
from pathlib import Path
P=np.array([[[0,1],[1,0]],[[0,-1j],[1j,0]],[[1,0],[0,-1]]],complex); I=np.eye(2)
signs=np.array([-1,1]*5)
def run(axes,angles):
 r=I.astype(complex)
 for a,t,s in zip(axes,angles,signs):
  r=(np.cos(t/2)*I-1j*np.sin(t/2)*s*P[a])@r
 return np.linalg.norm(r-I)
rng=np.random.default_rng(54); rows={k:[] for k in ['cyclic','mirrored','adjacent_pairs']}
for j in range(10000):
 a=rng.integers(0,3,5); t=rng.uniform(0,4*np.pi,5)
 rows['cyclic'].append(run(np.arange(10)%3,np.r_[t,t[::-1]]))
 rows['mirrored'].append(run(np.r_[a,a[::-1]],np.r_[t,t[::-1]]))
 rows['adjacent_pairs'].append(run(np.repeat(a,2),np.repeat(t,2)))
out={k:{'trials':len(v),'closed':int(np.sum(np.array(v)<1e-10)),'median':float(np.median(v)),'max':float(max(v))} for k,v in rows.items()}
Path(__file__).with_name('neon054_results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
