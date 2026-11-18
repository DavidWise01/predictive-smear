import hashlib,json,struct
from pathlib import Path
H=lambda b: hashlib.sha256(b).digest()
ZERO=bytes(32)
def leaf(k,v): return H(b'\x00'+k.encode()+bytes(v))
def root(pairs):
 a=[leaf(k,v) for k,v in pairs]; a += [H(b'\x02')]*2
 while len(a)>1: a=[H(b'\x01'+a[i]+a[i+1]) for i in range(0,len(a),2)]
 return a[0]
keys=('x','y','z','xy','xz','yz')
def record(i,prev,values):
 r=root(zip(keys,values)); return H(b'\x03'+struct.pack('>Q',i)+prev+r)
def verify(rows,head):
 p=ZERO
 for i,v in enumerate(rows): p=record(i,p,v)
 return p==head
if __name__=='__main__':
 rows=[]; p=ZERO; checkpoints=[]
 for i in range(100000):
  v=[((i>>j)&1,((i+1)>>j)&1) for j in range(6)]; rows.append(v);p=record(i,p,v)
  if i+1 in (1,100,1000,10000,100000): checkpoints.append({'snapshots':i+1,'head_bytes':len(p),'encoded_history_bytes':len(rows)*12})
 assert verify(rows,p)
 detected=0
 for i in (0,1,99,999,9999,50000,99999):
  old=rows[i]; rows[i]=[(1-old[0][0],old[0][1])]+old[1:]; detected+=not verify(rows,p);rows[i]=old
 out={'snapshots':len(rows),'head_bytes':len(p),'history_verified':verify(rows,p),'tamper_detected':detected,'tamper_trials':7,'truncation_detected':not verify(rows[:-1],p),'head':p.hex(),'checkpoints':checkpoints}
 Path(__file__).with_name('metaverse066_results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
