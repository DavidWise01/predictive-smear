import random,json
from collections import Counter
from pathlib import Path

def run(seed,mode):
    env=random.Random(seed); rng=random.Random(seed+100000); contexts=[env.randrange(8) for _ in range(300)]; change=env.randrange(100,201)
    blocked=[set() for _ in range(8)]; preferred=[None]*8; ledger=[]; c=Counter(); detected=set()
    for t,x in enumerate(contexts):
        epoch=int(t>=change); correct=(x+epoch)%3
        if mode=='periodic' and t%30==0:
            blocked=[set() for _ in range(8)]; preferred=[None]*8
        choices=[a for a in range(3) if a not in blocked[x]]
        if not choices:
            if mode=='resistance':
                blocked[x].clear(); preferred[x]=None; choices=list(range(3)); c['reopen']+=1
            else:
                c['stalled']+=1; continue
        a=preferred[x] if preferred[x] in choices else rng.choice(choices)
        yes=a==correct
        ledger.append((t,x,a,yes))
        c['yes' if yes else 'no']+=1
        c['post_yes' if epoch else 'pre_yes']+=yes
        if yes: preferred[x]=a
        else:
            if mode=='resistance' and preferred[x]==a:
                c['contradiction']+=1; blocked[x].clear(); detected.add(x)
            blocked[x].add(a); preferred[x]=None
    c['post_opportunities']=300-change; c['changed_contexts_detected']=len(detected)
    assert c['yes']+c['no']+c['stalled']==300
    return c
out={}
for mode in ('permanent','periodic','resistance'):
    c=Counter()
    for seed in range(1000): c.update(run(seed,mode))
    out[mode]=dict(c)
Path(__file__).with_name('atom083_results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
