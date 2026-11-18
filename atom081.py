import random,json
from pathlib import Path
from collections import Counter

def trial(seed,mode):
    rng=random.Random(seed); history=[]; known={}; counts=Counter(); phases=Counter()
    for n in range(300):
        context=rng.randrange(8); epoch=int(n>=150); safe=(context+epoch)%3
        blocked=known.get(context,set()) if mode!='stateless' else set()
        candidates=[a for a in range(3) if a not in blocked]
        if not candidates:
            if mode=='adaptive': known[context]=set(); candidates=list(range(3)); counts['reopen']+=1
            else: counts['stalled']+=1; continue
        a=rng.choice(candidates); yes=a==safe
        reason=None if yes else 'action incompatible with context'
        repeated=not yes and any(h[:3]==(epoch,context,a) and not h[3] for h in history)
        history.append((epoch,context,a,yes,reason))
        counts['yes' if yes else 'no']+=1; counts['repeat_no']+=repeated
        phases[f'{epoch}_'+('yes' if yes else 'no')]+=1
        if not yes and mode!='stateless': known.setdefault(context,set()).add(a)
    assert len(history)+counts['stalled']==300
    return counts,phases

def run():
    out={}
    for mode in ['stateless','frozen','adaptive']:
        c=Counter();p=Counter()
        for seed in range(1000):
            a,b=trial(seed,mode);c.update(a);p.update(b)
        out[mode]=dict(c,phases=dict(p))
    return out
if __name__=='__main__':
    out=run();Path(__file__).with_name('atom081_results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
