import numpy as np, json
from pathlib import Path
N=2000; T=130
REG={'stable':(0,.001),'mixed':(-.02,.02),'reversal':(-.04,.04),'shock':(-.08,.08)}
RATES=np.array([.05,.15,.45])
def run():
 out={}
 for i,(name,(lo,hi)) in enumerate(REG.items()):
  r=np.random.default_rng(2102+i); rates=r.uniform(lo,hi,(N,10)); v=np.repeat(rates,13,axis=1); d=np.cumsum(v+r.normal(0,.002,(N,T)),axis=1); p=d+r.normal(0,.015/np.sqrt(3),(N,T)); delta=np.diff(p,axis=1)
  vel=np.zeros(N); prev=np.zeros(N); w=np.full((N,3,2),.5); scores=np.zeros((N,3)); losses=np.zeros(5); counts=np.zeros(3,int); switches=0; old=np.ones(N,int)
  for t in range(T-1):
   f=np.stack([vel,prev],axis=1); pred=(w*f[:,None,:]).sum(2); choice=np.argmin(scores,axis=1); choice=np.where(t==0,1,choice); a=delta[:,t]; err=a[:,None]-pred
   losses[0]+=np.sum((a-vel)**2); losses[1:4]+=np.sum(err**2,axis=0); losses[4]+=np.sum(err[np.arange(N),choice]**2); counts+=np.bincount(choice,minlength=3); switches+=int((choice!=old).sum()); old=choice
   scores=.95*scores+.05*err**2
   w=np.clip(w+RATES[None,:,None]*err[:,:,None]*f[:,None,:]/(.0001+(f*f).sum(1))[:,None,None],-2,2); vel=.85*vel+.15*a; prev=a
  assert counts.sum()==N*(T-1)
  out[name]=dict(mse=dict(zip(['baseline','slow','moderate','fast','selector'],(losses/(N*(T-1))).tolist())),selection_counts=counts.tolist(),switches=switches)
 return dict(seed_start=2102,rates=RATES.tolist(),evaluations=N*(T-1)*4*5,regimes=out,promotion=all(x['mse']['selector']<=x['mse']['baseline'] for x in out.values()))
if __name__=='__main__':
 out=run();Path(__file__).with_name('atom102_results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
