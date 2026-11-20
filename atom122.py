import json, math, random
from pathlib import Path
N=26; TURN=1296000; p=1/104; A=(1-N*p)**4

def run():
    rng=random.Random(122); frames=[]; c=[1/27]*3
    for t in range(120):
        c=[x*A for x in c]; w=[(1-x)*N/(3*TURN) for x in c]
        noise=[rng.uniform(-1e-4,1e-4) for _ in w]
        frames.append((w,[x*(1+e) for x,e in zip(w,noise)]))
        ratios=[1.025+((t//10)%3-1)/100,1.025+((t//7)%3-1)/100,1.025+((t//13)%5-2)/50]
        c=[1-(1-x)*(1-p*r)**4 for x,r in zip(c,ratios)]
        assert all(0<=x<=1 for x in c)
    rows=[]
    for mode in ('ideal','noisy'):
        for n in range(7):
            scale=60**n; residual=[]; bounds=[]
            for w,observed in frames:
                v=w if mode=='ideal' else observed
                target=-(v[0]+v[1])/v[2]
                theta=round(target*scale)/scale
                e=w[0]+w[1]+w[2]*theta
                bound=w[2]/(2*scale)+sum(abs(a-b)*abs(s) for a,b,s in zip(w,v,(1,1,target)))
                assert abs(e)<=bound+1e-18
                residual.append(e); bounds.append(bound)
            rows.append(dict(mode=mode,depth=n,peak=max(map(abs,residual)),rms=math.sqrt(sum(x*x for x in residual)/len(residual)),drift=sum(residual),bound=max(bounds)))
    return dict(addresses=366,cycles=120,seed=122,relative_noise_limit=1e-4,tolerance=1e-9,checks=1680,rows=rows)
if __name__=='__main__':
    out=run();Path(__file__).with_name('atom122_results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
