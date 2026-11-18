import numpy as np,json
from pathlib import Path
from scipy.linalg import expm
I=np.array([2.,1.]*3); target=np.array([1.,-2.]*3)
D=np.eye(6)-np.roll(np.eye(6),1,axis=1); L=D.T@D
rng=np.random.default_rng(47); n=120; dt=.01; steps=3000
v0=rng.normal(0,.4,(n,6)); v0-=((v0@I)/I.sum())[:,None]
rows={}
for h in [0.,.5,2.]:
 A=np.block([[np.zeros((6,6)),np.eye(6)],[-h*L/I[:,None],-2*L/I[:,None]]]); M=expm(A*dt)
 x=np.concatenate([np.zeros_like(v0),v0],axis=1); trace=[]; err=0.; reversal=np.zeros(n,dtype=bool); eprev=np.sum(I*v0*v0,axis=1)/2; rise=0.
 for j in range(steps+1):
  p,v=x[:,:6],x[:,6:]; err=max(err,float(np.max(abs(v@I-v0@I))))
  reversal|=np.any((v+target)*target<=0,axis=1)
  e=(np.sum(I*v*v,axis=1)+h*np.sum((p@D.T)**2,axis=1))/2
  rise=max(rise,float(np.max(e-eprev))); eprev=e
  if j%500==0: trace.append(float(np.median(np.sqrt(np.mean(p*p,axis=1)))))
  if j<steps:x=x@M.T
 rms=np.sqrt(np.mean(p*p,axis=1)); rows[str(h)]={'phase_rms_median':float(np.median(rms)),'speed_rms_median':float(np.median(np.sqrt(np.mean(v*v,axis=1)))),'recovered':int(np.sum(rms<.001)),'reversal_trials':int(reversal.sum()),'momentum_error':err,'max_energy_increase':rise,'trace':trace,'median_signed_overlap':float(np.median(np.cos(p/2)))}
out={'trials':n*3,'seconds':steps*dt,'rows':rows}; Path(__file__).with_name('spinor049_results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
