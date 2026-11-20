import json, random
from fractions import Fraction
from pathlib import Path
TURN=1296000

def encode(t,n,arm):
    scale=60**n
    lap,phase=divmod(t,TURN*scale)
    slot,rem=divmod(phase,10800*scale)
    sec,sub=divmod(rem,scale)
    digits=[]
    for _ in range(n):
        sub,d=divmod(sub,60);digits.append(d)
    return (3*slot+arm+1,sec,tuple(reversed(digits)),lap%2)

def decode(state):
    a,sec,digits,parity=state
    scale=60**len(digits);sub=0
    for d in digits:sub=60*sub+d
    return ((parity*TURN+((a-1)//3)*10800+sec)*scale+sub,(a-1)%3)

def run():
    rng=random.Random(112); rows=[]
    for n in range(13):
        scale=60**n; period=2*TURN*scale; checks=0
        for arm in range(3):
            for k in range(120):
                for t in (k*10800*scale-1,k*10800*scale,k*10800*scale+1):
                    for shift in (0,TURN*scale,period):
                        x=t+shift;s=encode(x,n,arm)
                        assert decode(s)==(x%period,arm)
                        assert encode(x+period,n,arm)==s
                        assert encode(x+TURN*scale,n,arm)==(*s[:3],1-s[3]); checks+=1
        for _ in range(10000):
            x=rng.randrange(-3*period,3*period); arm=rng.randrange(3)
            assert decode(encode(x,n,arm))==(x%period,arm);checks+=1
        rows.append(dict(depth=n,precision_arcseconds=str(Fraction(1,scale)),clock_states=period,checks=checks))
    return dict(addresses=(124-4)*3+6,rows=rows,total_checks=sum(r['checks'] for r in rows))
if __name__=='__main__':
    out=run();Path(__file__).with_name('atom112_results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
