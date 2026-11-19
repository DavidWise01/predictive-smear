import numpy as np,json
from pathlib import Path
C=.02
N=4000; T=130

def evaluate(seed,regime):
 r=np.random.default_rng(seed)
 rates={'stable':[0,.001], 'mixed':[0,.001,.005,.01,.02], 'turbulent':[-.04,-.02,.02,.04]}[regime]
 v=np.repeat(r.choice(rates,(N,10)),13,axis=1)
 drift=np.cumsum(v+r.normal(0,.002,(N,T)),axis=1)
 truth=r.integers(0,2,(N,T)); obs=truth+drift+r.normal(0,.03,(N,T))
 probe=drift+r.normal(0,.015,(N,T,3)).mean(2)
 results={}
 for mode in ('fixed','adaptive','hybrid'):
  off=np.zeros(N); vel=np.zeros(N); sq=0.; corrections=errors=0
  for t in range(T):
   if t: vel=.85*vel+.15*(probe[:,t]-probe[:,t-1])
   adaptive=np.clip(np.cbrt(1.5*C*abs(vel)),.025,.20)
   bound=.06 if mode=='fixed' else adaptive if mode=='adaptive' else np.clip(adaptive,.045,.09)
   u=abs(probe[:,t]-off)>bound; off[u]=probe[u,t]; corrections+=int(u.sum())
   x=obs[:,t]-off; sq+=float(((x-truth[:,t])**2).sum());errors+=int(((x>=.5)!=truth[:,t]).sum())
  results[mode]=dict(calibrations=corrections,errors=errors,rmse=(sq/(N*T))**.5,cost=(sq+C*corrections)/(N*T))
 return results
out={reg:evaluate(920+i,reg) for i,reg in enumerate(('stable','mixed','turbulent'))}
# Promotion requires no regression relative to incumbent in any regime.
promotion={m:all(row[m]['cost']<=row['fixed']['cost'] for row in out.values()) for m in ('adaptive','hybrid')}
result=dict(trajectories_per_regime=N,ticks=T,policy_evaluations=N*T*9,regimes=out,promotion=promotion)
Path(__file__).with_name('atom092_results.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
