import itertools,json
from collections import Counter
from pathlib import Path
def encode(a,b,c): return (a,b,c,a^b,a^c,b^c)
def checks(s):
 a,b,c,ab,ac,bc=s
 return (ab==a^b,ac==a^c,bc==b^c)
counts=Counter(); by_distance=Counter(); examples=[]
for a in itertools.product(range(2),repeat=3):
 for b in itertools.product(range(2),repeat=3):
  truth=encode(*a)+encode(*b)
  for mask in range(4096):
   candidate=tuple(x^((mask>>i)&1) for i,x in enumerate(truth))
   valid=all(checks(candidate[:6])+checks(candidate[6:]))
   counts['tested']+=1
   counts['accepted' if valid else 'held']+=1
   if valid and mask: counts['false_accept']+=1;by_distance[mask.bit_count()]+=1
   if valid and not mask: counts['correct_accept']+=1
   if not valid and mask.bit_count()<=2: counts['single_double_detected']+=1
   if valid and mask and len(examples)<3: examples.append({'truth':truth,'candidate':candidate,'flips':mask.bit_count()})
out=dict(counts=counts,undetected_by_distance=by_distance,examples=examples)
assert counts['tested']==262144 and counts['false_accept']==4032
assert counts['single_double_detected']==64*(12+66)
Path(__file__).with_name('metaverse069_results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
