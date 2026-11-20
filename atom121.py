from fractions import Fraction as F
from pathlib import Path
import json
N=26; TURN=1296000; p=F(1,104)
A=(1-N*p)**4

def run(mode):
    c=[F(1,27)]*3; previous=None; cumulative=F(0); activity=F(0); peak=F(0); rows=[]
    for t in range(120):
        ratios=[F(41,40)+F((t//10)%3-1,100), F(41,40)+F((t//7)%3-1,100), F(41,40)+F((t//13)%5-2,50)]
        c=[x*A for x in c]
        w=[(1-x)*F(N,3*TURN) for x in c]
        target=-(w[0]+w[1])/w[2]
        theta= -2 if mode=='fixed' else (previous if mode=='delayed' and previous is not None else target)
        previous=target
        flux=[w[0],w[1],w[2]*theta]; net=sum(flux)
        cumulative+=net; activity+=sum(map(abs,flux)); peak=max(peak,abs(net))
        if mode=='feedback': assert net==0
        c=[1-(1-x)*(1-p*r)**4 for x,r in zip(c,ratios)]
        assert all(0<=x<=1 for x in c)
        assert sum(x+(1-x) for x in c)/3==1
        rows.append(dict(cycle=t+1,phase=float(theta),net=float(net),cumulative=float(cumulative),center=[float(x) for x in c]))
    return dict(mode=mode,peak_residual=float(peak),cumulative=float(cumulative),activity=float(activity),rows=rows)
if __name__=='__main__':
    out=dict(addresses=(124-4)*3+6,cycles=120,policies=[run(m) for m in ('fixed','delayed','feedback')]); Path(__file__).with_name('atom121_results.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps([ {k:v for k,v in r.items() if k!='rows'} for r in out['policies']],indent=2));print('phase range',min(r['phase'] for r in out['policies'][2]['rows']),max(r['phase'] for r in out['policies'][2]['rows']))
