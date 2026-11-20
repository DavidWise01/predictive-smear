import json, math
from pathlib import Path
from fractions import Fraction as F
# 26 shell sites arranged as 13 opposing pairs on a ring.
# Interpolated one-arcsecond displacement is a modeled transport rule.
p=F(1,104); q=p*F(41,40); N=26
A=(1-N*p)**4; B=(1-q)**4
center=(1-B)/(1-A*B)
# Four outward transfers, angular shift, four inward transfers.
# Uniform shell is stationary in occupancy, but directed transport has nonzero flux.
def run(sign,bias):
    pull=p*bias; b=(1-pull)**4; c=(1-b)/(1-A*b)
    shell=[(1-c)/N]*N
    for _ in range(4):
        moved=p*c; c-=N*moved; shell=[x+moved for x in shell]
    alpha=F(N,1296000) if sign else F(0)
    flux=sum(shell)*alpha*sign
    shifted=[(1-alpha)*shell[i]+alpha*shell[(i-sign)%N] for i in range(N)]
    assert sum(shifted)+c==1 and min(shifted)>=0
    for _ in range(4):
        moved=[pull*x for x in shifted]; c+=sum(moved); shifted=[x-y for x,y in zip(shifted,moved)]
    assert c== (1-b)/(1-A*b)
    assert shifted==[(1-c)/N]*N
    return dict(phase_arcseconds=sign,pull_ratio=float(bias),center=float(c),signed_flux=float(flux),angular_transport_arcseconds=float(flux*F(1296000,N)),mass=float(c+sum(shifted)))
rows=[run(s,b) for b in (F(1),F(41,40)) for s in (-1,0,1)]
assert rows[0]['signed_flux']==-rows[2]['signed_flux'] and rows[3]['signed_flux']==-rows[5]['signed_flux']
assert rows[1]['signed_flux']==rows[4]['signed_flux']==0
out=dict(addresses=(124-4)*3+6,channels=13,rows=rows,model='ring interpolation, one signed arcsecond, equilibrium cycle; not spontaneous rotation')
Path(__file__).with_name('atom119_results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
