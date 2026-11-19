import numpy as np,json
from pathlib import Path
N=2000; T=130
REG={'stable':(0,.001),'mixed':(-.02,.02),'reversal':(-.04,.04),'shock':(-.08,.08)}
def mix(s,p):
 q=1/(s+1e-5);return (q*p).sum(1)/q.sum(1)
def run():
 out={}
 for i,(name,(lo,hi)) in enumerate(REG.items()):
  r=np.random.default_rng(2106+i);rates=r.uniform(lo,hi,(N,10));d=np.cumsum(np.repeat(rates,13,axis=1)+r.normal(0,.002,(N,T)),axis=1);p=d+r.normal(0,.015/np.sqrt(3),(N,T));delta=np.diff(p,axis=1)
  vel=np.zeros(N);prev=np.zeros(N);w=np.full((N,3,2),.5);g=np.full((N,4),.0003);old=np.full(N,5);idx=np.arange(N);loss=np.zeros(4)
  tables=[np.full((N,k,4),.0003) for k in (11,121,33)]; counts=[np.zeros((N,k),int) for k in (11,121,33)]; visits=np.zeros(33,int)
  for actual in delta.T:
   f=np.stack([vel,prev],axis=1);pred=np.column_stack([vel,(w*f[:,None,:]).sum(2)]);band=np.clip(np.rint(vel/.01).astype(int),-5,5)+5;direction=np.sign(band-old)+1;keys=[band,old*11+band,3*band+direction];scores=[tab[idx,key] for tab,key in zip(tables,keys)];a=[c[idx,key,None]/(c[idx,key,None]+13) for c,key in zip(counts,keys)];parent=a[0]*scores[0]+(1-a[0])*g
   forecasts=np.column_stack([vel,mix(parent,pred),mix(a[1]*scores[1]+(1-a[1])*parent,pred),mix(a[2]*scores[2]+(1-a[2])*parent,pred)])
   err=actual[:,None]-pred;loss+=((actual[:,None]-forecasts)**2).sum(0);visits+=np.bincount(keys[2],minlength=33);g=.95*g+.05*err**2
   for tab,c,key,s in zip(tables,counts,keys,scores):tab[idx,key]=.95*s+.05*err**2;c[idx,key]+=1
   w=np.clip(w+np.array([.05,.15,.45])[None,:,None]*err[:,1:,None]*f[:,None,:]/(.0001+(f*f).sum(1))[:,None,None],-2,2);vel=.85*vel+.15*actual;prev=actual;old=band
  assert visits.sum()==N*(T-1)
  out[name]=dict(mse=dict(zip(['baseline','context','full','compressed'],(loss/(N*(T-1))).tolist())),occupied=int((visits>0).sum()),visits=visits.reshape(11,3).tolist())
 return dict(regimes=out,evaluations=N*(T-1)*4*4,registers=[484,132],promotion=all(v['mse']['compressed']<=v['mse']['baseline'] for v in out.values()),compression_nonregression=all(v['mse']['compressed']<=v['mse']['full'] for v in out.values()))
if __name__=='__main__':
 out=run();Path(__file__).with_name('atom106_results.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:{a:b for a,b in v.items() if a!='visits'} for k,v in out['regimes'].items()},indent=2));print(out['promotion'],out['compression_nonregression'])
