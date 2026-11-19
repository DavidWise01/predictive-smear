import numpy as np, json
from pathlib import Path

def simulate(seed,n,mode,threshold=.08,cost=.02):
    rng=np.random.default_rng(seed); T=130
    rates=rng.choice([0,.001,.005,.01,.02],(n,10))
    drift=np.cumsum(np.repeat(rates,13,axis=1)+rng.normal(0,.002,(n,T)),axis=1)
    truth=rng.integers(0,2,(n,T)); obs=truth+drift+rng.normal(0,.03,(n,T))
    probe=drift+rng.normal(0,.015,(n,T,3)).mean(2)
    offset=np.zeros(n); velocity=np.zeros(n); sq=0.; corrections=0; errors=0
    for t in range(T):
        if t: velocity=.85*velocity+.15*(probe[:,t]-probe[:,t-1])
        bound=np.clip(np.cbrt(1.5*cost*np.abs(velocity)),.025,.20) if mode=='adaptive' else threshold
        update=abs(probe[:,t]-offset)>bound if mode!='periodic' else np.full(n,t%13==0)
        offset[update]=probe[update,t]; corrections+=int(update.sum())
        corrected=obs[:,t]-offset; sq+=float(np.sum((corrected-truth[:,t])**2));errors+=int(np.sum((corrected>=.5)!=truth[:,t]))
    count=n*T; return dict(mode=mode,threshold=threshold if mode=='fixed' else None,observations=count,errors=errors,calibrations=corrections,rmse=(sq/count)**.5,objective=(sq+cost*corrections)/count)

def run():
    candidates=[simulate(910,2000,'fixed',x) for x in [.025,.04,.06,.08,.10,.12,.16,.20]]
    best=min(candidates,key=lambda r:r['objective'])['threshold']
    tests=[simulate(911,10000,'fixed',.08),simulate(911,10000,'fixed',best),simulate(911,10000,'periodic'),simulate(911,10000,'adaptive')]
    return dict(training=candidates,chosen_threshold=best,test=tests,cost=.02,train_seed=910,test_seed=911)
if __name__=='__main__':
    out=run();Path(__file__).with_name('atom091_results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
