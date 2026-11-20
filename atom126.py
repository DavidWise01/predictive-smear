import json
from pathlib import Path
agents=('Jane','Toph','Patricia')
weights={a:3333 for a in agents}
observer=1
rows=[]
for k in range(366):
    r=k%3; order=agents[r:]+agents[:r]
    allocation=[weights[a] for a in order]
    assert sum(allocation)+observer==10000
    assert observer==1
    rows.append(dict(event=k,order=order,allocation=allocation,observer=observer,route='[d]->(e)' if k%2==0 else '(e)->[d]'))
out=dict(addresses=366,total_units=10000,observer_units=observer,checks=366,events=rows)
Path(__file__).with_name('atom126_results.json').write_text(json.dumps(out,indent=2)+'\n')
print('366 allocation checks passed; 9999 active + 1 observer = 10000')
