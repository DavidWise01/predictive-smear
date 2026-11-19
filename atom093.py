import numpy as np,json,itertools
from pathlib import Path
C=.02; T=130
REG={'stable':[0,.001],'mixed':[0,.001,.005,.01,.02],'turbulent':[-.04,-.02,.02,.04]}
def data(seed,n,reg):
 r=np.random.default_rng(seed); v=np.repeat(r.choice(REG[reg],(n,10)),13,axis=1); d=np.cumsum(v+r.normal(0,.002,(n,T)),axis=1); y=r.integers(0,2,(n,T)); x=y+d+r.normal(0,.03,(n,T)); p=d+r.normal(0,.015,(n,T,3)).mean(2); vel=np.zeros_like(p)
 for t in range(1,T):vel[:,t]=.85*vel[:,t-1]+.15*(p[:,t]-p[:,t-1])
 return y,x,p,np.cbrt(1.5*C*abs(vel))
def evaluate(d,b):
 y,x,p,a=d; n=len(y); off=np.zeros(n); sq=0.; k=err=0
 for t in range(T):
  u=abs(p[:,t]-off)>np.clip(a[:,t],*b);off[u]=p[u,t];k+=int(u.sum());z=x[:,t]-off-y[:,t];sq+=float((z*z).sum());err+=int((abs(z)>=.5).sum())
 return dict(cost=(sq+C*k)/(n*T),calibrations=k,rmse=(sq/(n*T))**.5,large_errors=err)
def run():
 base=(.045,.09); train={r:data(930+i,1800,r) for i,r in enumerate(REG)}; incumbent={r:evaluate(d,base)['cost'] for r,d in train.items()}; history=[]; best=base
 for step in (.015,.0075,.00375):
  candidates=sorted({(round(best[0]+i*step,6),round(best[1]+j*step,6)) for i,j in itertools.product((-1,0,1),repeat=2) if .015<=best[0]+i*step<=best[1]+j*step<=.2})
  scores=[]
  for b in candidates:
   ratios=[evaluate(d,b)['cost']/incumbent[r] for r,d in train.items()];scores.append((max(ratios),sum(ratios)/3,b))
  worst,mean,best=min(scores);history.append(dict(step=step,bounds=best,worst_ratio=worst,mean_ratio=mean,candidates=len(scores)))
 test={}
 for i,r in enumerate(REG):
  d=data(1930+i,6000,r);test[r]={'incumbent':evaluate(d,base),'candidate':evaluate(d,best)}
 return dict(baseline=base,selected=best,history=history,test=test,promotion=all(x['candidate']['cost']<=x['incumbent']['cost'] for x in test.values()),test_evaluations=6000*T*3*2)
if __name__=='__main__':
 out=run();Path(__file__).with_name('atom093_results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
