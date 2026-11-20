from decimal import Decimal as D, localcontext
from pathlib import Path
import json

def run():
    with localcontext() as c:
        c.prec=80
        pi=D('3.141592653589793238462643383279502884197169399375105820974944592307816406286')
        pf=D(5).sqrt()*D('1.61658e-35')/(5*pi)
        base=648000*pf/pi
        rows=[{'n':n,'radius_m':str(base*60**n)} for n in range(33)]
        targets={'one_meter':'1','earth_radius':'6371000','one_AU':'149597870700','one_light_year':'9460730472580800','one_parsec_approx':'3.0856775814913673e16'}
        crossings={}
        for name,x in targets.items():
            r=D(x); n=next(n for n in range(33) if base*60**n>=r)
            assert n==0 or base*60**(n-1)<r<=base*60**n
            crossings[name]={'depth':n,'radius_m':str(r),'capacity_m':str(base*60**n),'arc_length_m':str(r*pi/(648000*60**n))}
        return {'addresses':(124-4)*3+6,'pf_m':str(pf),'base_radius_m':str(base),'ladder':rows,'crossings':crossings}
if __name__=='__main__':
    out=run();Path(__file__).with_name('atom114_results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
