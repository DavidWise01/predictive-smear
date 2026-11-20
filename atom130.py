import json, hashlib
from pathlib import Path
NAMES=('Jane','Toph','Patricia')
CASES=[
 dict(id='bounce',response='hard_bounce',legitimate=True,genuine=True,rule_verified=False,raw=True,roots=['smtp-1']),
 dict(id='redirect',response='phone_redirect',legitimate=True,genuine=True,rule_verified=True,raw=True,roots=['email-1','smtp-2']),
 dict(id='resolved',response='email_resolved',legitimate=True,genuine=True,rule_verified=True,raw=True,roots=['email-2']),
 dict(id='duplicate',response='soft_block',legitimate=True,genuine=True,rule_verified=True,raw=True,roots=['email-3','email-3']),
 dict(id='unsupported',response='hard_bounce',legitimate=True,genuine=True,rule_verified=True,raw=False,roots=[]),
 dict(id='bad_faith',response='hard_bounce',legitimate=False,genuine=False,rule_verified=True,raw=True,roots=['smtp-4'])]
def digest(x): return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def audit(c,k,prev):
    r=k%3; order=NAMES[r:]+NAMES[:r]
    j={'observed':c['response'] if c['raw'] else 'unverified_report','barrier_candidate':c['raw'] and c['response']!='email_resolved'}
    t={'ethical_gate':c['legitimate'] and c['genuine'],'rule_verified_fixture':c['rule_verified'],'legal_conclusion':'not_adjudicated'}
    p={'raw_available':c['raw'],'distinct_roots':len(set(c['roots'])),'corroborated_fixture':c['raw'] and len(set(c['roots']))>=2}
    if not t['ethical_gate']: result='STOP_ETHICAL_GATE'
    elif not p['raw_available']: result='REQUEST_ORIGINAL_EVIDENCE'
    elif not j['barrier_candidate']: result='CLOSE_RESOLVED'
    elif not t['rule_verified_fixture']: result='VERIFY_APPLICABLE_RULE'
    elif not p['corroborated_fixture']: result='REQUEST_INDEPENDENT_EVIDENCE'
    else: result='REFER_FOR_HUMAN_REVIEW'
    e=dict(event=k,case=c['id'],order=order,route='[d]->(e)' if k%2==0 else '(e)->[d]',allocation=[3333,3333,3333,1],auditors=dict(zip(NAMES,(j,t,p))),pop=result,previous=prev)
    e['hash']=digest(e);return e
if __name__=='__main__':
    log=[];prev='0'*64
    for c in CASES:
        for phase in range(6):
            e=audit(c,len(log),prev);prev=e['hash'];log.append(e)
        assert len({e['pop'] for e in log[-6:]})==1
    expected=['VERIFY_APPLICABLE_RULE','REFER_FOR_HUMAN_REVIEW','CLOSE_RESOLVED','REQUEST_INDEPENDENT_EVIDENCE','REQUEST_ORIGINAL_EVIDENCE','STOP_ETHICAL_GATE']
    assert [log[i*6]['pop'] for i in range(6)]==expected
    for i,e in enumerate(log):
        assert e['previous']==(log[i-1]['hash'] if i else '0'*64)
        assert digest({k:v for k,v in e.items() if k!='hash'})==e['hash']
        assert sum(e['allocation'])==10000
    out=dict(synthetic=True,events=len(log),cases=len(CASES),results=dict(zip([c['id'] for c in CASES],expected)),log=log)
    Path(__file__).with_name('atom130_results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='log'},indent=2))
