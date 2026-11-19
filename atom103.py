import numpy as np,json
from pathlib import Path
N=2000; T=130
REG={'stable':(0,.001),'mixed':(-.02,.02),'reversal':(-.04,.04),'shock':(-.08,.08)}
RATES=np.array([.05,.15,.45])
def run():
 out={}
 for i,(name,(lo,hi)) in enumerate(REG.items()):
  r=np.random.default_rng(2103+i); rates=r.uniform(lo,hi,(N,10)); d=np.cumsum(np.repeat(rates,13,axis=1)+r.normal(0,.002,(N,T)),axis=1); p=d+r.normal(0,.015/np.sqrt(3),(N,T)); delta=np.diff(p,axis=1)
  vel=np.zeros(N); prev=np.zeros(N); w=np.full((N,3,2),.5); scores=np.full((N,4),.0003); losses=np.zeros(7); weights=np.zeros(4)
  for t in range(T-1):
   f=np.stack([vel,prev],axis=1); pred=(w*f[:,None,:]).sum(2); allpred=np.column_stack([vel,pred]); a=delta[:,t]; err=a[:,None]-allpred
   q=1/(scores+1e-5); q/=q.sum(1,keepdims=True); q3=q[:,1:]/q[:,1:].sum(1,keepdims=True)
   mix=np.column_stack([pred.mean(1),(q3*pred).sum(1),(q*allpred).sum(1)])
   losses[:4]+=(err**2).sum(0);losses[4:]+=((a[:,None]-mix)**2).sum(0);weights+=q.sum(0)
   scores=.95*scores+.05*err**2
   w=np.clip(w+RATES[None,:,None]*err[:,1:,None]*f[:,None,:]/(.0001+(f*f).sum(1))[:,None,None],-2,2);vel=.85*vel+.15*a;prev=a
  count=N*(T-1);out[name]={'mse':dict(zip(['baseline','slow','moderate','fast','equal','weighted','anchored'],(losses/count).tolist())),'mean_anchored_weights':(weights/count).tolist()}
 return dict(regimes=out,evaluations=N*(T-1)*4*7,promotion={k:all(v['mse'][k]<=v['mse']['baseline'] for v in out.values()) for k in ['equal','weighted','anchored']})
if __name__=='__main__':
 out=run();Path(__file__).with_name('atom103_results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
