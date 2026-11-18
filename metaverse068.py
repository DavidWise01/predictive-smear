import hashlib, itertools, json
from collections import Counter
from pathlib import Path
H=lambda x: hashlib.sha256(x).digest()

def gate(votes, roots, parent, external):
    if len(set(roots)) != 3: return 'shared_ancestry', parent
    if len(set(votes)) != 1: return 'disagreement', parent
    if external is None: return 'missing_external', parent
    if votes[0] != external: return 'external_mismatch', parent
    return 'advance', H(b'K068'+parent+votes[0])

def run():
    counts=Counter(); false_accept=Counter(); violations=0
    parent=H(b'genesis'); cases=0
    for n in range(4096):
        good=n.to_bytes(2,'big'); bad=(n^1).to_bytes(2,'big')
        for mask in range(8):
            votes=[bad if mask>>i&1 else good for i in range(3)]
            for roots in [('j','t','p'),('j','j','p')]:
                for label,external in [('correct',good),('missing',None),('corrupt',bad)]:
                    status,head=gate(votes,roots,parent,external); counts[label,status]+=1; cases+=1
                    if status=='advance' and votes[0]!=good: false_accept[label]+=1
                    if status!='advance' and head!=parent: violations+=1
    return dict(cases=cases, outcomes={label:{s:c for (l,s),c in counts.items() if l==label} for label in ['correct','missing','corrupt']},false_accept=dict(false_accept),held_head_violations=violations,head_bytes=32)
if __name__=='__main__':
    result=run(); Path(__file__).with_name('metaverse068_results.json').write_text(json.dumps(result,indent=2)); print(json.dumps(result,indent=2))
