import numpy as np,json
from pathlib import Path
from atom095 import data,REG,MODES,T
H=13; C=.02; S=.002; P=.00001

def evaluate(d,gate):
 y,x,p=d;n=len(y);off=np.zeros(n);vel=np.zeros(n);mode=np.ones(n,int);sq=0.;k=sw=wrong=calls=nodes=0;peak=0.
 for t in range(T):
  innovation=p[:,t]-p[:,t-1]-vel if t else np.zeros(n)
  if t:vel=.85*vel+.15*(p[:,t]-p[:,t-1])
  idx=np.flatnonzero((abs(innovation)>gate)|(abs(p[:,t]-off)>2*gate))
  if len(idx):
   h=min(H,T-t);scores=np.zeros((len(idx),3));v=vel[idx];q=p[idx,t];calls+=len(idx);nodes+=len(idx)*3*h
   for j in range(3):
    a=off[idx].copy();b=np.clip(np.cbrt(.03*abs(v)),*MODES[j]);loss=S*(mode[idx]!=j).astype(float)
    for step in range(h):
     f=q+step*v;u=abs(f-a)>b;a[u]=f[u];loss+=(f-a)**2+C*u
    scores[:,j]=loss
   new=np.argmin(scores,axis=1);sw+=int((new!=mode[idx]).sum());mode[idx]=new
  b=np.clip(np.cbrt(.03*abs(vel)),MODES[mode,0],MODES[mode,1]);u=abs(p[:,t]-off)>b;off[u]=p[u,t];k+=int(u.sum());z=x[:,t]-off-y[:,t];sq+=float((z*z).sum());wrong+=int(((z+y[:,t]>=.5)!=y[:,t]).sum());peak=max(peak,float(abs(z).max()))
 N=n*T;return dict(cost=(sq+C*k+S*sw+P*nodes)/N,operating_cost=(sq+C*k+S*sw)/N,calls=calls,nodes=nodes,switches=sw,calibrations=k,wrong=wrong,peak=peak)

def run():
 train=[data(980+i,500,r) for i,r in enumerate(REG[:3])];gates=[.015,.03,.06,.12,.24];base=[evaluate(d,np.inf)['cost'] for d in train];scores=[max(evaluate(d,g)['cost']/b for d,b in zip(train,base)) for g in gates];g=gates[int(np.argmin(scores))];out={}
 for i,r in enumerate(REG):
  d=data(1980+i,2000,r);out[['stable','mixed','turbulent','shock'][i]]={name:evaluate(d,gate) for name,gate in [('balanced',np.inf),('always',-1),('attenuated',g)]}
 return dict(gate=g,training=list(zip(gates,scores)),node_cost=P,regimes=out,promotion=all(r['attenuated']['cost']<=r['balanced']['cost'] and r['attenuated']['peak']<=.30 and r['attenuated']['wrong']==0 for r in out.values()))
if __name__=='__main__':
 out=run();Path(__file__).with_name('atom098_results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
