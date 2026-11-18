import numpy as np, json
from pathlib import Path
X=np.array([[0,1],[1,0]],complex); Y=np.array([[0,-1j],[1j,0]]); Z=np.diag([1,-1]); eye=np.eye(2)
def U(axis,deg):
 t=np.deg2rad(deg)/2; return np.cos(t)*eye-1j*np.sin(t)*axis
def dist(a,b): return float(np.linalg.norm(a-b,'fro'))
def seq(word,deg):
 m=eye.copy()
 for i in word:m=U([X,Y,Z][int(i)-1],deg)@m
 return m
rows=[]
for deg in [0,15,30,60,90,120,180,360,720]:
 a,b=U(X,deg),U(Y,deg); c=a@b@a.conj().T@b.conj().T
 cycle=eye.copy()
 for word in ['123','231','312','111']:cycle=seq(word,deg)@cycle
 rows.append(dict(deg=deg,order_error=dist(a@b,b@a),commutator_trace=float(np.trace(c).real/2),cycle_to_identity=dist(cycle,eye),cycle_to_negative_identity=dist(cycle,-eye)))
rng=np.random.default_rng(50); max_unitarity=0.;max_inverse=0.;max_det=0.
for _ in range(10000):
 axis=rng.normal(size=3);axis/=np.linalg.norm(axis);s=sum(v*m for v,m in zip(axis,[X,Y,Z]));d=rng.uniform(-720,720);a=U(s,d);b=U(s,-d);max_unitarity=max(max_unitarity,dist(a.conj().T@a,eye));max_inverse=max(max_inverse,dist(a@b,eye));max_det=max(max_det,float(abs(np.linalg.det(a)-1)))
out=dict(rows=rows,random_trials=10000,max_unitarity_error=max_unitarity,max_counterrotation_error=max_inverse,max_determinant_error=max_det)
Path(__file__).with_name('spinor050_results.json').write_text(json.dumps(out,indent=2)); print(json.dumps(out,indent=2))
