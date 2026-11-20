from fractions import Fraction
from decimal import Decimal as D, localcontext
from pathlib import Path
import json

def run():
    # Cubic lattice in units of a proposed local cell edge Pf.
    rows=[]
    for n in range(33):
        side=60**n; area=side**2; volume=side**3
        assert area==3600**n and volume==216000**n
        assert Fraction(volume,side**3)==1
        if n:
            assert side==60*rows[-1]['edge_cells']
            assert area==3600*rows[-1]['face_cells']
            assert volume==216000*rows[-1]['volume_cells']
        rows.append(dict(n=n,edge_cells=side,face_cells=area,volume_cells=volume))
    with localcontext() as c:
        c.prec=80
        pi=D('3.141592653589793238462643383279502884197169399375105820974944592307816406286')
        pf=D(5).sqrt()*D('1.61658e-35')/(5*pi)
        for r in rows:
            r['edge_m']=str(pf*r['edge_cells'])
            r['face_m2']=str(pf**2*r['face_cells'])
            r['volume_m3']=str(pf**3*r['volume_cells'])
        return dict(addresses=(124-4)*3+6,cell_edge_m=str(pf),cell_volume_m3=str(pf**3),generations=rows,scaling_checks=96,identity_checks=99,geometry='cube; edge starts at Pf, not K114 radial base')
if __name__=='__main__':
    out=run();Path(__file__).with_name('atom115_results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({**out,'generations':[out['generations'][n] for n in (0,1,2,3,6,12,18,24,32)]},indent=2))
