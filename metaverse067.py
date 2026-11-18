import hashlib,json,itertools
from pathlib import Path
H=lambda b: hashlib.sha256(b).digest()
def decide(votes, roots, parent, previous):
    if len(set(roots))!=3: return previous,'shared_ancestry'
    if any(p!=parent for p,h in votes): return previous,'wrong_parent'
    if len({h for p,h in votes})!=1: return previous,'disagreement'
    return votes[0][1],'advance'
def run():
    counts={}; failures=0; cases=0
    for n in range(4096):
        parent=H(b'parent'+n.to_bytes(2,'big')); good=H(parent+n.to_bytes(2,'big')); bad=H(b'bad'+good)
        for mask in range(8):
            votes=[(parent,bad if mask>>i&1 else good) for i in range(3)]
            for roots in [('j','t','p'),('j','j','p')]:
                head,status=decide(votes,roots,parent,parent); counts[status]=counts.get(status,0)+1;cases+=1
                expected=(len(set(roots))==3 and mask in (0,7))
                failures+= (status=='advance')!=expected or (not expected and head!=parent)
    p=H(b'parent'); g=H(b'good'); assert decide([(p,g),(p,g),(H(p),g)],('j','t','p'),p,p)==(p,'wrong_parent')
    return dict(cases=cases,counts=counts,policy_failures=failures,unanimous_wrong_cases=4096,wrong_parent_test='pass',head_bytes=32)
if __name__=='__main__':
    out=run();Path(__file__).with_name('metaverse067_results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
