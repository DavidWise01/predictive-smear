import random,json,statistics
from pathlib import Path
def run():
 out={}
 for noise in (.01,.05,.10,.20):
  rows={k:dict(errors=0,false_switches=0,delays=[],misses=0) for k in (1,2,3)}
  for seed in range(1000):
   rng=random.Random(seed); change=rng.randrange(100,201); estimates={k:0 for k in rows}; first={k:None for k in rows}
   for t in range(300):
    truth=int(t>=change); obs=[truth ^ int(rng.random()<noise) for _ in range(3)]
    for k,r in rows.items():
     prev=estimates[k]
     if sum(v!=prev for v in obs)>=k: estimates[k]=1-prev
     r['errors']+=estimates[k]!=truth
     r['false_switches']+=prev==truth and estimates[k]!=truth
     if t>=change and estimates[k]==truth and first[k] is None:first[k]=t-change
   for k,r in rows.items():
    if first[k] is None:r['misses']+=1
    else:r['delays'].append(first[k])
  out[str(noise)]={str(k):dict(errors=r['errors'],false_switches=r['false_switches'],median_delay=statistics.median(r['delays']),mean_delay=statistics.mean(r['delays']),misses=r['misses'],accuracy=1-r['errors']/300000) for k,r in rows.items()}
 return out
if __name__=='__main__':
 out=run(); Path(__file__).with_name('atom084_results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
