import numpy as np,json
from pathlib import Path
N=2000; T=130
REG={'stable':(0,.001),'mixed':(-.02,.02),'reversal':(-.04,.04),'shock':(-.08,.08)}
RATES=np.array([.05,.15,.45])
def weights(s):
 q=1/(s+1e-5);return q/q.sum(1,keepdims=True)
def run():
 out={}
 for i,(name,(lo,hi)) in enumerate(REG.items()):
  r=np.random.default_rng(2104+i); rates=r.uniform(lo,hi,(N,10));d=np.cumsum(np.repeat(rates,13,axis=1)+r.normal(0,.002,(N,T)),axis=1);p=d+r.normal(0,.015/np.sqrt(3),(N,T));delta=np.diff(p,axis=1)
  vel=np.zeros(N);prev=np.zeros(N);w=np.full((N,3,2),.5);g=np.full((N,4),.0003);local=np.full((N,11,4),.0003);counts=np.zeros((N,11),int);loss=np.zeros(4);visits=np.zeros(11,int);idx=np.arange(N)
  for t in range(T-1):
   f=np.stack([vel,prev],axis=1);pred=np.column_stack([vel,(w*f[:,None,:]).sum(2)])
   band=np.clip(np.rint(vel/.01).astype(int),-5,5)+5
   s=local[idx,band];n=counts[idx,band];a=n[:,None]/(n[:,None]+13)
   forecasts=np.column_stack([vel,(weights(g)*pred).sum(1),(weights(s)*pred).sum(1),(weights(a*s+(1-a)*g)*pred).sum(1)])
   actual=delta[:,t];err=actual[:,None]-pred;loss+=((actual[:,None]-forecasts)**2).sum(0)
   visits+=np.bincount(band,minlength=11);g=.95*g+.05*err**2;local[idx,band]=.95*s+.05*err**2;counts[idx,band]+=1
   w=np.clip(w+RATES[None,:,None]*err[:,1:,None]*f[:,None,:]/(.0001+(f*f).sum(1))[:,None,None],-2,2);vel=.85*vel+.15*actual;prev=actual
  assert visits.sum()==N*(T-1)
  out[name]={'mse':dict(zip(['baseline','global','local','shrunk'],(loss/(N*(T-1))).tolist())),'visits':visits.tolist()}
 return dict(regimes=out,evaluations=N*(T-1)*4*4,band_width=.01,prior_count=13,promotion={k:all(v['mse'][k]<=v['mse']['baseline'] for v in out.values()) for k in ['global','local','shrunk']})
if __name__=='__main__':
 out=run();Path(__file__).with_name('atom104_results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
