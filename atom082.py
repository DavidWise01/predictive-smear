import random,json
from collections import Counter
from pathlib import Path
# Each arm experiences a common context; one acts per tick. Epoch is observable.
# Evidence is synthetic and truthful at its origin; a stale replay relabels epoch.
def run(seed,mode):
 r=random.Random(seed); ledgers=[[] for _ in range(3)]; counts=Counter(); frozen=[]
 for tick in range(300):
  epoch=tick//150; ctx=r.randrange(8); arm=tick%3; safe=(ctx+epoch)%3
  records=ledgers[arm] if mode=='isolated' else frozen
  evidence=[e for e in records if e[1]==ctx and (e[0]==epoch if mode=='verified' else True)]
  if mode=='verified':
   # Individually observed failures count once; replay cannot change source epoch.
   evidence=list({e[4]:e for e in evidence if e[0]==e[5]}.values())
  blocked={e[2] for e in evidence if not e[3]}
  choices=[a for a in range(3) if a not in blocked]
  if not choices:
   counts['stalled']+=1; continue
  a=r.choice(choices); yes=a==safe
  e=(epoch,ctx,a,yes,(seed,tick,arm),epoch)
  ledgers[arm].append(e); frozen.append(e)
  counts['yes' if yes else 'no']+=1
  counts[f'epoch{epoch}_yes']+=yes
  if not yes and any(q[0]==epoch and q[1]==ctx and q[2]==a and not q[3] for q in frozen[:-1]): counts['repeat_no']+=1
  if tick==149:
   # Replay historical failures with a changed claimed epoch, retaining origin.
   frozen.extend((1,q[1],q[2],q[3],q[4],q[5]) for q in frozen.copy() if not q[3])
 assert sum(counts[k] for k in ('yes','no','stalled'))==300
 return counts
out={}
for mode in ('isolated','shared_unscoped','verified'):
 c=Counter()
 for seed in range(1000): c.update(run(seed,mode))
 out[mode]=dict(c)
result={'runs_per_policy':1000,'opportunities_per_policy':300000,'policies':out}
Path(__file__).with_name('atom082_results.json').write_text(json.dumps(result,indent=2)); print(json.dumps(result,indent=2))
