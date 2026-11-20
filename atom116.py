import json
from pathlib import Path

def partition(m):
    if m == 1:
        return dict(interior=0,face=0,edge=0,corner=0,singlet=1)
    k=m-2
    return dict(interior=k**3,face=6*k*k,edge=12*k,corner=8,singlet=0)

def run():
    rows=[]
    for n in range(33):
        m=60**n;p=partition(m)
        assert sum(p.values())==m**3
        shell=m**3-p['interior']
        if m>1: assert shell==6*m*m-12*m+8
        rows.append(dict(n=n,edge_length_cells=m,**p,shell=shell,total=m**3))
    brute=0
    for m in (1,2,3,4,5,6,7,8,9,10,60):
        actual=dict.fromkeys(partition(m),0)
        for x in range(m):
            for y in range(m):
                for z in range(m):
                    b=sum(v in (0,m-1) for v in (x,y,z))
                    actual['singlet' if m==1 else ('interior','face','edge','corner')[b]]+=1
                    brute+=1
        assert actual==partition(m)
    return dict(addresses=(124-4)*3+6,generations=rows,brute_cells=brute,brute_sizes=11)
if __name__=='__main__':
    out=run();Path(__file__).with_name('atom116_results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({**out,'generations':out['generations'][:4]},indent=2))
