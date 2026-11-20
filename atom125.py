import json, hashlib
from pathlib import Path

NAMES=('Jane','Toph','Patricia')
def run(n=366):
    log=[]; prev='0'*64
    for k in range(n):
        r=k%3; order=NAMES[r:]+NAMES[:r]
        route=['[d]','(e)'] if k%2==0 else ['(e)','[d]']
        event=dict(event=k,phase=k%6,order=order,route=route,previous=prev)
        prev=hashlib.sha256(json.dumps(event,sort_keys=True).encode()).hexdigest()
        event['hash']=prev; log.append(event)
    for k,e in enumerate(log):
        body={a:b for a,b in e.items() if a!='hash'}
        assert e['hash']==hashlib.sha256(json.dumps(body,sort_keys=True).encode()).hexdigest()
        assert e['previous']==(log[k-1]['hash'] if k else '0'*64)
    assert len({e['hash'] for e in log})==n
    counts={name:sum(e['order'][0]==name for e in log) for name in NAMES}
    assert set(counts.values())=={122}
    assert len({(tuple(e['order']),tuple(e['route'])) for e in log})==6
    return dict(addresses=366,events=n,cycles=n//6,lead_counts=counts,route_counts={r:sum(e['route'][0]==r for e in log) for r in ('[d]','(e)')},log=log)
if __name__=='__main__':
    out=run(); Path(__file__).with_name('atom125_results.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({k:v for k,v in out.items() if k!='log'},indent=2)); print(json.dumps(out['log'][:6],indent=2))
