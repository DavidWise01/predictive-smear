import numpy as np, json, hashlib
from pathlib import Path
N=2000; T=130
REG={'stable':(0,.001),'mixed':(-.02,.02),'reversal':(-.04,.04),'shock':(-.08,.08)}
def run():
 out={}
 for i,(name,(lo,hi)) in enumerate(REG.items()):
  r=np.random.default_rng(2101+i); rates=r.uniform(lo,hi,(N,10)); v=np.repeat(rates,13,axis=1); d=np.cumsum(v+r.normal(0,.002,(N,T)),axis=1); p=d+r.normal(0,.015/np.sqrt(3),(N,T)); delta=np.diff(p,axis=1)
  vel=np.zeros(N); w=np.tile([.5,.5],(N,1)); prev=np.zeros(N); losses=np.zeros((N,2)); h=bytes(32); checkpoint=None
  for t in range(T-1):
   features=np.stack([vel,prev],axis=1); pred=(features*w).sum(1); actual=delta[:,t]; losses[:,0]+=(actual-vel)**2; losses[:,1]+=(actual-pred)**2
   w=np.clip(w+.15*(actual-pred)[:,None]*features/(.0001+(features**2).sum(1))[:,None],-2,2); vel=.85*vel+.15*actual; prev=actual
   h=hashlib.sha256(h+np.asarray([pred[0],actual[0],*w[0]],dtype='<f8').tobytes()).digest()
   if t==64: checkpoint=(w.copy(),vel.copy(),prev.copy(),h)
  ww,vv,pp,hh=checkpoint
  for t in range(65,T-1):
   f=np.stack([vv,pp],axis=1); pred=(f*ww).sum(1); a=delta[:,t]; ww=np.clip(ww+.15*(a-pred)[:,None]*f/(.0001+(f**2).sum(1))[:,None],-2,2); vv=.85*vv+.15*a; pp=a; hh=hashlib.sha256(hh+np.asarray([pred[0],a[0],*ww[0]],dtype='<f8').tobytes()).digest()
  assert np.array_equal(w,ww) and np.array_equal(vel,vv) and hh==h
  out[name]={'baseline_mse':float(losses[:,0].mean()/(T-1)),'learned_mse':float(losses[:,1].mean()/(T-1)),'replay_exact':True,'head':h.hex()}
 return {'predictions_per_policy':N*(T-1)*4,'regimes':out}
if __name__=='__main__':
 out=run();Path(__file__).with_name('atom101_results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
