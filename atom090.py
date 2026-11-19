import numpy as np,json
from pathlib import Path
rng=np.random.default_rng(90)
n=10000; ticks=130; rows=[]
for rate in [0,.001,.005,.01,.02]:
 drift=np.cumsum(rng.normal(rate,.002,(n,ticks)),axis=1)
 truth=rng.integers(0,2,(n,ticks)); obs=truth+drift+rng.normal(0,.03,(n,ticks))
 probe=drift+rng.normal(0,.015,(n,ticks,3)).mean(2)
 for mode in ['none','periodic','adaptive']:
  offset=np.zeros(n); errors=0; corrections=0; sq=0
  for t in range(ticks):
   update=np.zeros(n,dtype=bool)
   if mode=='periodic': update[:]=t%13==0
   if mode=='adaptive': update=abs(probe[:,t]-offset)>.08
   offset[update]=probe[update,t]; corrections+=int(update.sum())
   corrected=obs[:,t]-offset; errors+=int(((corrected>=.5)!=truth[:,t]).sum());sq+=float(np.sum((corrected-truth[:,t])**2))
  rows.append(dict(rate=rate,policy=mode,errors=errors,observations=n*ticks,calibrations=corrections,rmse=float(np.sqrt(sq/(n*ticks)))))
out=dict(seed=90,runs=n,ticks=ticks,rows=rows,threshold=.08)
Path(__file__).with_name('atom090_results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
