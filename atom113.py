import json, math
from pathlib import Path
from decimal import Decimal, localcontext

def run():
    with localcontext() as c:
        c.prec=80
        pi=Decimal('3.141592653589793238462643383279502884197169399375105820974944592307816406286')
        lp=Decimal('1.61658e-35'); pf=Decimal(5).sqrt()*lp/(5*pi)
        rows=[]
        for radius in map(Decimal,['1','6371000','149597870700']):
            n=0
            while radius*pi/(648000*Decimal(60)**n)>pf:n+=1
            length=radius*pi/(648000*Decimal(60)**n)
            assert length<=pf<length*60
            rows.append(dict(radius_m=str(radius),depth=n,arc_length_m=str(length),previous_m=str(length*60)))
        return dict(addresses=(124-4)*3+6,foam_scale_m=str(pf),planck_length_input_m=str(lp),rows=rows,model='arc length R theta; foam scale is proposed, not measured')
if __name__=='__main__':
    out=run();Path(__file__).with_name('atom113_results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
