import numpy as np,json
from pathlib import Path
from atom095 import data,REG,MODES,T
N=4000; H=13; C=.02; S=.002

def evaluate(d,predict):
 y,x,p=d;n=len(y);off=np.zeros(n);vel=np.zeros(n);mode=np.ones(n,int);sq=0.;k=sw=wrong=0;peak=0.;counts=np.zeros(3,int)
 for t in range(T):
  if t:vel=.85*vel+.15*(p[:,t]-p[:,t-1])
  if predict:
   # Causal constant-velocity forecast, no future samples or truth.
   horizon=min(H,T-t); scores=np.zeros((n,3))
   for j in range(3):
    a=off.copy();b=np.clip(np.cbrt(.03*abs(vel)),*MODES[j]);loss=S*(mode!=j).astype(float)
    for h in range(horizon):
     f=p[:,t]+h*vel;u=abs(f-a)>b;a[u]=f[u];loss+=(f-a)**2+C*u
    scores[:,j]=loss
   new=np.argmin(scores,axis=1);sw+=int((new!=mode).sum());mode=new
  counts+=np.bincount(mode,minlength=3)
  b=np.clip(np.cbrt(.03*abs(vel)),MODES[mode,0],MODES[mode,1]);u=abs(p[:,t]-off)>b;off[u]=p[u,t];k+=int(u.sum());z=x[:,t]-off-y[:,t];sq+=float((z*z).sum());wrong+=int(((z+y[:,t]>=.5)!=y[:,t]).sum());peak=max(peak,float(abs(z).max()))
 return dict(cost=(sq+C*k+S*sw)/(n*T),rmse=(sq/(n*T))**.5,calibrations=k,switches=sw,wrong=wrong,peak=peak,mode_counts=counts.tolist())

def run():
 out={}
 for i,r in enumerate(REG):
  d=data(1970+i,N,r);out[['stable','mixed','turbulent','shock'][i]]={ 'balanced':evaluate(d,False),'predictive':evaluate(d,True)}
 return dict(horizon=H,trajectories_per_regime=N,evaluations=4*N*T*2,regimes=out,promotion=all(r['predictive']['cost']<=r['balanced']['cost'] and r['predictive']['peak']<=.30 for r in out.values()))
if __name__=='__main__':
 out=run();Path(__file__).with_name('atom097_results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
