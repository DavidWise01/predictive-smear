import json, math, random
from pathlib import Path
N=26; TURN=1296000; p=1/104; A=(1-N*p)**4

def run():
    rng=random.Random(123); frames=[]; c=[1/27]*3
    for t in range(1200):
        c=[x*A for x in c]; w=[(1-x)*N/(3*TURN) for x in c]
        v=[x*(1+rng.uniform(-1e-4,1e-4)) for x in w]
        frames.append((w,-(v[0]+v[1])/v[2],-(w[0]+w[1])/w[2]))
        ratios=[1.025+((t//10)%3-1)/100,1.025+((t//7)%3-1)/100,1.025+((t//13)%5-2)/50]
        c=[1-(1-x)*(1-p*r)**4 for x,r in zip(c,ratios)]
        assert all(0<=x<=1 for x in c)
    rows=[]
    for mode in ('raw','mean3','ema','adaptive'):
        hist=[]; prev=None; errors=[]; change_errors=[]; quiet_errors=[]; trace=[]
        for t,(w,obs,truth) in enumerate(frames):
            hist.append(obs)
            if prev is None or mode=='raw': est=obs
            elif mode=='mean3': est=sum(hist[-3:])/len(hist[-3:])
            else:
                alpha=.35 if mode=='ema' else (.85 if abs(obs-prev)>0.00035 else .2)
                est=prev+alpha*(obs-prev)
            prev=est; theta=round(est*60**3)/60**3
            e=w[0]+w[1]+w[2]*theta; errors.append(e)
            (change_errors if t and abs(truth-frames[t-1][2])>0.0002 else quiet_errors).append(e)
            assert abs(theta-est)<=.5/60**3+1e-15
            if t<120: trace.append(e)
        rms=lambda a:math.sqrt(sum(x*x for x in a)/len(a))
        rows.append(dict(mode=mode,rms=rms(errors),peak=max(map(abs,errors)),change_rms=rms(change_errors),quiet_rms=rms(quiet_errors),change_count=len(change_errors),drift=sum(errors),trace=trace))
    return dict(addresses=366,cycles=1200,seed=123,noise_limit=1e-4,depth=3,checks=4800,rows=rows)
if __name__=='__main__':
    out=run(); Path(__file__).with_name('atom123_results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps([{k:v for k,v in r.items() if k!='trace'} for r in out['rows']],indent=2))
