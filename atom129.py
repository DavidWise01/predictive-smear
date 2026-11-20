import json, hashlib, itertools
from pathlib import Path
NAMES=('Jane','Toph','Patricia')
# Three observations of a binary state; at most one corrupted observation.
# Four quadrants: perception, comparison, decision, persistence.
def digest(x): return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def kernel(values, event, previous):
    r=event%3; order=NAMES[r:]+NAMES[:r]
    route=['[d]','(e)'] if event%2==0 else ['(e)','[d]']
    data=dict(zip(NAMES,values)); a,b,c=[data[n] for n in order]
    # Two bilateral comparisons suffice for binary majority assuming at most one fault.
    comparisons=[a==b,b==c]
    decision=b if any(comparisons) else a
    dissent=[n for n in NAMES if data[n]!=decision]
    cells={q:{n:None for n in NAMES} for q in ('perception','comparison','decision','persistence')}
    for n in NAMES:
        cells['perception'][n]=data[n]
        cells['comparison'][n]=data[n]==decision
        cells['decision'][n]=decision
        cells['persistence'][n]=n in dissent
    pop={'decision':decision,'disagreement':dissent,'question':'Which input disagreed with the consensus, and what evidence would resolve it?' if dissent else 'Would this consensus survive an independent perturbation?'}
    body=dict(event=event,phase=event%6,order=order,route=route,allocation=[3333,3333,3333,1],cells=cells,stage3=data,stage2=comparisons,stage1=decision,stage0={'action_pending':True},pop=pop,previous=previous)
    # Observer reads completed body; has no path into selection.
    body['hash']=digest(body); return body

def run():
    log=[]; prev='0'*64; tests=0
    for event,(truth,fault,phase) in enumerate(itertools.product((0,1),(None,0,1,2),range(6))):
        v=[truth]*3
        if fault is not None:v[fault]^=1
        e=kernel(v,event,prev); prev=e['hash'];log.append(e)
        assert e['pop']['decision']==truth
        assert e['pop']['disagreement']==([] if fault is None else [NAMES[fault]])
        assert sum(e['allocation'])==10000 and sum(map(len,e['cells'].values()))==12
        tests+=1
    for i,e in enumerate(log):
        assert e['previous']==(log[i-1]['hash'] if i else '0'*64)
        assert digest({k:v for k,v in e.items() if k!='hash'})==e['hash']
    counter=kernel([1,1,0],0,'0'*64) # truth=0, two corrupted inputs
    assert counter['pop']['decision']!=0
    return dict(addresses=366,tests=tests,phases=6,observer_units=1,first_dissent=log[6],counterexample=counter['pop'],log=log,limitation='POP is rule-generated diagnostic, not proof of agency; route is scheduling metadata, not distinct physical transforms')
if __name__=='__main__':
    out=run();Path(__file__).with_name('atom129_results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='log'},indent=2))
