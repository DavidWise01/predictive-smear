import hashlib, random, json
from pathlib import Path
MASK=(1<<40)-1
FULL=(1<<42)-1
H=lambda b: hashlib.sha256(b).digest()
def pack(rgb,p,o,ing,out):
    values=(rgb,p,o,ing,out)
    if any(not isinstance(v,int) or not 0<=v<1<<w for v,w in zip(values,(24,10,6,1,1))): raise ValueError('field range')
    return rgb|(p<<24)|(o<<34)|(ing<<40)|(out<<41)
def unpack(v):
    if not 0<=v<=FULL: raise ValueError('register range')
    return (v&0xffffff,(v>>24)&1023,(v>>34)&63,(v>>40)&1,(v>>41)&1)
def seal(parent,node,word): return H(b'ATOM076\0'+parent+bytes([node])+word.to_bytes(6,'big'))
def chain(words):
    head=bytes(32)
    for n,w in enumerate(words): head=seal(head,n,w)
    return head
rng=random.Random(76)
results=dict(trials=10000,roundtrip_failures=0,payload_failures=0,transitions=0,tamper_detected=0,tamper_trials=0)
for _ in range(results['trials']):
    fields=[rng.randrange(1<<w) for w in (24,10,6,1,1)]
    v=pack(*fields); results['roundtrip_failures']+=tuple(fields)!=unpack(v)
    words=[]
    for n in range(13):
        w=(v&MASK)|(rng.randrange(4)<<40); words.append(w)
        results['payload_failures']+=(w&MASK)!=(v&MASK)
    results['transitions']+=12
    head=chain(words)
    for n,w in enumerate(words):
        for bit in (0,23,24,33,34,39,40,41):
            altered=words.copy(); altered[n]=w^(1<<bit)
            results['tamper_trials']+=1;results['tamper_detected']+=chain(altered)!=head
results.update(nodes=13,packed_bytes=6,unused_bits=6,commitment_bytes=32,logical_bits=42)
assert results['roundtrip_failures']==results['payload_failures']==0
assert results['tamper_detected']==results['tamper_trials']
Path(__file__).with_name('atom076_results.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
