from fractions import Fraction as F
from pathlib import Path
import json
N=26; TURN=1296000; p=F(1,104)
A=(1-N*p)**4

def arm(phase,ratio):
    q=p*ratio; B=(1-q)**4
    c=(1-B)/(1-A*B)
    shell=[(1-c)/N]*N
    for _ in range(4):
        moved=p*c; c-=N*moved; shell=[x+moved for x in shell]
    alpha=F(N,TURN)*abs(phase)
    assert 0<=alpha<=1
    sign=(phase>0)-(phase<0)
    flux=sum(shell)*alpha*sign
    shell=[(1-alpha)*shell[i]+alpha*shell[(i-sign)%N] for i in range(N)]
    for _ in range(4):
        moved=[q*x for x in shell]; c+=sum(moved); shell=[x-y for x,y in zip(shell,moved)]
    assert c==(1-B)/(1-A*B) and c+sum(shell)==1 and min(shell)>=0
    return flux/3,c

def run():
    equal=F(41,40); cases=[]
    for name,phases,ratios in [('balanced',(1,1,-2),(equal,)*3),('reverse',(-1,-1,2),(equal,)*3),('zero',(0,0,0),(equal,)*3),('mismatched',(1,1,-2),(equal,equal,F(1)))]:
        vals=[arm(F(s),r) for s,r in zip(phases,ratios)]; flux=[x[0] for x in vals]
        cases.append(dict(name=name,phases=phases,net=float(sum(flux)),net_exact=str(sum(flux)),absolute_flux=float(sum(map(abs,flux))),arm_flux=list(map(float,flux)),center=[float(x[1]) for x in vals]))
    assert cases[0]['net_exact']==cases[1]['net_exact']==cases[2]['net_exact']=='0'
    assert cases[0]['absolute_flux']>0 and cases[3]['net']!=0
    # compensate unequal shell occupancy with exact phase adjustment
    j=arm(F(1),equal)[0]; k=arm(F(1),F(1))[0]; correction=-2*j/k
    corrected=2*j+arm(correction,F(1))[0]; assert corrected==0
    return dict(addresses=(124-4)*3+6,cases=cases,compensated_phase=float(correction),compensated_phase_exact=str(correction),compensated_net=str(corrected),model='three equal-mass independent ring arms; signed flux not physical angular momentum')
if __name__=='__main__':
    out=run();Path(__file__).with_name('atom120_results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
