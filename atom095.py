import numpy as np,json
from pathlib import Path
T=130
MODES=np.array([[.065,.120],[.045,.105],[.025,.075]])
REG=[[0,.001],[0,.001,.005,.01,.02],[-.04,-.02,.02,.04],[-.08,0,.08]]
def data(seed,n,rates):
 r=np.random.default_rng(seed);v=np.repeat(r.choice(rates,(n,10)),13,axis=1);d=np.cumsum(v+r.normal(0,.002,(n,T)),axis=1);y=r.integers(0,2,(n,T));x=y+d+r.normal(0,.03,(n,T));p=d+r.normal(0,.015,(n,T,3)).mean(2);return y,x,p

def evaluate(d,mode,cut=(.004,.018)):
 y,x,p=d;n=len(y);off=np.zeros(n);vel=np.zeros(n);prev=np.full(n,1);sq=0.;k=tail=large=wrong=switch=0;peak=0.;counts=np.zeros(3,int)
 for t in range(T):
  if t:vel=.85*vel+.15*(p[:,t]-p[:,t-1])
  m=np.full(n,mode) if mode>=0 else np.where(abs(vel)<cut[0],0,np.where(abs(vel)>cut[1],2,1))
  if t:switch+=int((m!=prev).sum())
  prev=m;counts+=np.bincount(m,minlength=3)
  b=np.clip(np.cbrt(.03*abs(vel)),MODES[m,0],MODES[m,1]);u=abs(p[:,t]-off)>b;off[u]=p[u,t];k+=int(u.sum());z=x[:,t]-off-y[:,t];sq+=float((z*z).sum());tail+=int((abs(z)>.15).sum());large+=int((abs(z)>=.5).sum());wrong+=int(((z+y[:,t]>=.5)!=y[:,t]).sum());peak=max(peak,float(abs(z).max()))
 N=n*T;return dict(mse=sq/N,rate=k/N,tail=tail/N,large=large,wrong=wrong,peak=peak,switches=switch,mode_counts=counts.tolist(),cost=(sq+.02*k+.002*switch)/N)
def run():
 train=[data(950+i,1000,r) for i,r in enumerate(REG[:3])];cuts=[(a,b) for a in (.002,.004,.008) for b in (.012,.018,.03)];best=min(cuts,key=lambda c:np.mean([evaluate(d,-1,c)['cost'] for d in train]));out={}
 for i,r in enumerate(REG):
  d=data(1950+i,4000,r);out[['stable','mixed','turbulent','shock'][i]]={name:evaluate(d,m,best) for name,m in [('efficiency',0),('balanced',1),('accuracy',2),('dynamic',-1)]}
 return dict(cut=best,regimes=out,test_evaluations=4*4*4000*T,training_evaluations=9*3*1000*T,switch_cost=.002,calibration_cost=.02,promotion=all(r['dynamic']['cost']<=r['balanced']['cost'] and r['dynamic']['peak']<=.30 for r in out.values()))
if __name__=='__main__':
 out=run();Path(__file__).with_name('atom095_results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
