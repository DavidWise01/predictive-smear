import numpy as np,json
from pathlib import Path
N=2000; T=130
REG={'stable':(0,.001),'mixed':(-.02,.02),'reversal':(-.04,.04),'shock':(-.08,.08)}
RATES=np.array([.05,.15,.45])
def mix(s,p):
 q=1/(s+1e-5); return (q*p).sum(1)/q.sum(1)
def run():
 out={}
 for i,(name,(lo,hi)) in enumerate(REG.items()):
  r=np.random.default_rng(2105+i); rates=r.uniform(lo,hi,(N,10)); d=np.cumsum(np.repeat(rates,13,axis=1)+r.normal(0,.002,(N,T)),axis=1); p=d+r.normal(0,.015/np.sqrt(3),(N,T)); delta=np.diff(p,axis=1)
  vel=np.zeros(N); prev=np.zeros(N); w=np.full((N,3,2),.5); g=np.full((N,4),.0003); local=np.full((N,11,4),.0003); trans=np.full((N,121,4),.0003); lc=np.zeros((N,11),int); tc=np.zeros((N,121),int); old=np.full(N,5); idx=np.arange(N); loss=np.zeros(5); visits=np.zeros(121,int)
  for t in range(T-1):
   f=np.stack([vel,prev],axis=1); pred=np.column_stack([vel,(w*f[:,None,:]).sum(2)]); band=np.clip(np.rint(vel/.01).astype(int),-5,5)+5; key=old*11+band
   s=local[idx,band]; z=trans[idx,key]; a=lc[idx,band,None]/(lc[idx,band,None]+13); b=tc[idx,key,None]/(tc[idx,key,None]+13); parent=a*s+(1-a)*g
   forecasts=np.column_stack([vel,mix(g,pred),mix(parent,pred),mix(z,pred),mix(b*z+(1-b)*parent,pred)])
   actual=delta[:,t]; err=actual[:,None]-pred; loss+=((actual[:,None]-forecasts)**2).sum(0); visits+=np.bincount(key,minlength=121)
   g=.95*g+.05*err**2; local[idx,band]=.95*s+.05*err**2; trans[idx,key]=.95*z+.05*err**2; lc[idx,band]+=1; tc[idx,key]+=1
   w=np.clip(w+RATES[None,:,None]*err[:,1:,None]*f[:,None,:]/(.0001+(f*f).sum(1))[:,None,None],-2,2); vel=.85*vel+.15*actual; prev=actual; old=band
  assert visits.sum()==N*(T-1)
  out[name]=dict(mse=dict(zip(['baseline','global','contextual','transition','hierarchical'],(loss/(N*(T-1))).tolist())),visited_transitions=int((visits>0).sum()),diagonal_visits=int(np.trace(visits.reshape(11,11))),visits=visits.reshape(11,11).tolist())
 return dict(regimes=out,evaluations=N*(T-1)*4*5,promotion={k:all(v['mse'][k]<=v['mse']['baseline'] for v in out.values()) for k in ['transition','hierarchical']})
if __name__=='__main__':
 out=run();Path(__file__).with_name('atom105_results.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:{a:b for a,b in v.items() if a!='visits'} for k,v in out['regimes'].items()},indent=2));print(out['promotion'])
