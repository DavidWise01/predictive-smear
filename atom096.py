import numpy as np,json
from pathlib import Path
from atom095 import data,evaluate,REG,MODES,T

def persistent(d,cut,margin,dwell):
 y,x,p=d;n=len(y);off=np.zeros(n);vel=np.zeros(n);m=np.ones(n,int);pending=m.copy();streak=np.zeros(n,int);sq=0.;k=sw=wrong=0;peak=0.
 for t in range(T):
  if t:vel=.85*vel+.15*(p[:,t]-p[:,t-1])
  v=abs(vel);lo,hi=cut
  wanted=np.where(v<lo*(1-margin),0,np.where(v>hi*(1+margin),2,1))
  wanted=np.where((m==0)&(v<lo*(1+margin)),0,wanted)
  wanted=np.where((m==2)&(v>hi*(1-margin)),2,wanted)
  streak=np.where(wanted==pending,streak+1,1);pending=wanted
  change=(wanted!=m)&(streak>=dwell);sw+=int(change.sum());m=np.where(change,wanted,m)
  b=np.clip(np.cbrt(.03*v),MODES[m,0],MODES[m,1]);u=abs(p[:,t]-off)>b;off[u]=p[u,t];k+=int(u.sum());z=x[:,t]-off-y[:,t];sq+=float((z*z).sum());wrong+=int(((z+y[:,t]>=.5)!=y[:,t]).sum());peak=max(peak,float(abs(z).max()))
 return dict(cost=(sq+.02*k+.002*sw)/(n*T),switches=sw,wrong=wrong,peak=peak,calibrations=k)

def run():
 cut=tuple(json.loads(Path(__file__).with_name('atom095_results.json').read_text())['cut']);train=[data(960+i,1000,r) for i,r in enumerate(REG[:3])];base=[evaluate(d,1)['cost'] for d in train]
 candidates=[]
 for margin in (0,.15,.30):
  for dwell in (2,5,8,13):
   ratios=[persistent(d,cut,margin,dwell)['cost']/b for d,b in zip(train,base)];candidates.append((max(ratios),sum(ratios)/3,margin,dwell))
 _,_,margin,dwell=min(candidates);out={}
 for i,r in enumerate(REG):
  d=data(1960+i,4000,r);out[['stable','mixed','turbulent','shock'][i]]={'balanced':evaluate(d,1),'instant':evaluate(d,-1,cut),'persistent':persistent(d,cut,margin,dwell)}
 return dict(cut=cut,margin=margin,dwell=dwell,training_candidates=len(candidates),test_evaluations=4*4000*T*3,regimes=out,promotion=all(r['persistent']['cost']<=r['balanced']['cost'] and r['persistent']['peak']<=.30 for r in out.values()))
if __name__=='__main__':
 out=run();Path(__file__).with_name('atom096_results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
