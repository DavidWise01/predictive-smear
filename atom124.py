import json
from pathlib import Path
from itertools import product

def step(s):
    a,b,c,parity=s
    return b,c,a,1-parity

states=[]; s=('a','b','c',0); origin=s
for k in range(6):
    states.append(dict(phase=k,precedence=list(s[:3]),route=['[d]','(e)'] if s[3]==0 else ['(e)','[d]']))
    s=step(s)
    assert (s==origin)==(k==5)
assert len({(tuple(x['precedence']),tuple(x['route'])) for x in states})==6
# Forward-only event log: phase returns, event identity never returns.
log=[]; s=origin
for k in range(366):
    log.append((k,s));s=step(s)
assert len(set(log))==366 and s==origin
out=dict(period=6,precedence_period=3,route_period=2,phases=states,events=len(log),complete_cycles=len(log)//6,addresses=(124-4)*3+6,assumption='alternate route continues across triplet closure; logical forward-only log, not hardware diode')
Path(__file__).with_name('atom124_results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
