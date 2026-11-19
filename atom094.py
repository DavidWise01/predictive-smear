import numpy as np,json,itertools
from pathlib import Path
T=130
REG=[[0,.001],[0,.001,.005,.01,.02],[-.04,-.02,.02,.04]]
def data(seed,n,rates):
 r=np.random.default_rng(seed);v=np.repeat(r.choice(rates,(n,10)),13,axis=1);d=np.cumsum(v+r.normal(0,.002,(n,T)),axis=1);y=r.integers(0,2,(n,T));x=y+d+r.normal(0,.03,(n,T));p=d+r.normal(0,.015,(n,T,3)).mean(2);vel=np.zeros_like(p)
 for t in range(1,T):vel[:,t]=.85*vel[:,t-1]+.15*(p[:,t]-p[:,t-1])
 return y,x,p,np.cbrt(.03*abs(vel))
def evaluate(d,b):
 y,x,p,a=d;n=len(y);off=np.zeros(n);sq=0.;k=err=0;peak=0.;tail=0
 for t in range(T):
  u=abs(p[:,t]-off)>np.clip(a[:,t],*b);off[u]=p[u,t];k+=int(u.sum());z=x[:,t]-off-y[:,t];sq+=float((z*z).sum());err+=int((abs(z)>=.5).sum());tail+=int((abs(z)>.15).sum());peak=max(peak,float(abs(z).max()))
 return dict(mse=sq/(n*T),rate=k/(n*T),tail=tail/(n*T),large_errors=err,peak=peak)
def run():
 bounds=list(itertools.product([.025,.035,.045,.055,.065],[.075,.09,.105,.12,.15]));base=(.045,.105)
 train=[data(940+i,1200,r) for i,r in enumerate(REG)]
 def metrics(ds,b):return [evaluate(d,b) for d in ds]
 def vec(rows):return tuple(np.mean([r[k] for r in rows]) for k in ['mse','rate','tail'])
 rows=[]
 for b in bounds:
  m=metrics(train,b);rows.append(dict(bounds=b,vector=vec(m),safe=all(r['large_errors']==0 and r['peak']<=.30 for r in m)))
 eligible=[r for r in rows if r['safe']];front=[r for r in eligible if not any(all(a<=b for a,b in zip(s['vector'],r['vector'])) and any(a<b for a,b in zip(s['vector'],r['vector'])) for s in eligible)]
 # Select cost preferences on training only; safety gate independent of weights.
 chosen={str(w):min(front,key=lambda r:r['vector'][0]+w*r['vector'][1])['bounds'] for w in [.005,.02,.08]}
 test=[data(1940+i,4000,r) for i,r in enumerate(REG)]
 results={name:metrics(test,b) for name,b in {'incumbent':base,**chosen}.items()}
 out=dict(training_candidates=len(rows),eligible=len(eligible),front=front,chosen=chosen,test=results,test_vectors={k:vec(v) for k,v in results.items()},test_evaluations=4000*T*3*len(results),safety='zero absolute residual >=0.5; maximum residual <=0.30 per regime')
 return out
if __name__=='__main__':
 out=run();Path(__file__).with_name('atom094_results.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='front'},indent=2));print('front size',len(out['front']))
