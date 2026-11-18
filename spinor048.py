import numpy as np,json
from pathlib import Path
I=np.array([2.,1.]*3); target=np.array([1.,-2.]*3)
D=np.eye(6)-np.roll(np.eye(6),1,axis=1); L=D.T@D
rng=np.random.default_rng(47); dt=.01; steps=3000; n=120
initial=rng.normal(0,.4,(n,6)); initial-=((initial@I)/I.sum())[:,None]
def spin(theta): return np.stack((np.exp(-.5j*theta),np.exp(.5j*theta)),axis=-1)/np.sqrt(2)
rows={}
for k in [0.,.5,2.]:
 v=target+initial.copy(); phi=np.zeros_like(v); p0=v@I; maxerr=0.; trace=[]
 for j in range(steps):
  phi+=dt*(v-target)
  v-=dt*k*((v-target)@L)/I
  maxerr=max(maxerr,float(np.max(np.abs(v@I-p0))))
  if (j+1)%500==0: trace.append(float(np.median(np.sqrt(np.mean(phi**2,axis=1)))))
 psi=spin(phi); overlap=np.real(np.sum(np.conj(spin(np.zeros_like(phi)))*psi,axis=-1)); fidelity=overlap**2
 rows[str(k)]={'median_speed_rms':float(np.median(np.sqrt(np.mean((v-target)**2,axis=1)))),'median_phase_rms_rad':float(np.median(np.sqrt(np.mean(phi**2,axis=1)))),'median_spinor_fidelity':float(np.median(fidelity)), 'phase_rms_trace':trace,'momentum_error':maxerr,'norm_error':float(np.max(abs(np.sum(abs(psi)**2,axis=-1)-1))),'weighted_phase_error':float(np.max(abs(phi@I)))}
 correction=-phi; assert np.max(abs(correction@I))<1e-10
 rows[str(k)]['corrected_fidelity']=float(np.min(abs(np.sum(np.conj(spin(np.zeros_like(phi)))*spin(phi+correction),axis=-1))**2))
rec=[]
for deg in (0,180,360,540,720):
 p=spin(np.deg2rad(deg)); overlap=np.vdot(spin(0),p); rec.append({'degrees':deg,'signed_overlap':float(overlap.real),'fidelity':float(abs(overlap)**2)})
out={'trials':360,'seconds':steps*dt,'rows':rows,'recurrence':rec}
Path(__file__).with_name('spinor048_results.json').write_text(json.dumps(out,indent=2)); print(json.dumps(out,indent=2))
