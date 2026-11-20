import json, hashlib
from pathlib import Path
from copy import deepcopy

def digest(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()

class Kernel:
    def __init__(self, limit=3):
        self.stack=[dict(id=0,domain='main',state='OPEN',cursor=19,findings=[])]
        self.log=[]; self.limit=limit; self.serial=0
    def emit(self,kind,**data):
        e=dict(event=len(self.log),kind=kind,previous=self.log[-1]['hash'] if self.log else '0'*64,**data)
        e['hash']=digest(e); self.log.append(e)
    def open(self,domain,question):
        if len(self.stack)-1>=self.limit: raise ValueError('depth limit')
        parent=self.stack[-1]; frozen=digest(parent); self.serial+=1
        self.stack.append(dict(id=self.serial,domain=domain,state='OPEN',question=question,parent_hash=frozen,findings=[]))
        self.emit('OPEN',child=self.serial,parent_hash=frozen)
    def extrapolate(self,plan):
        f=self.stack[-1]; assert len(self.stack)>1 and f['state']=='OPEN'
        f.update(state='PLANNED',plan=plan); self.emit('EXTRAPOLATE',id=f['id'],plan=plan)
    def verify(self,approved):
        f=self.stack[-1]
        if f['state']!='PLANNED' or approved is not True: raise ValueError('explicit verification required')
        f['state']='VERIFIED'; self.emit('VERIFY',id=f['id'])
    def execute(self,observations):
        f=self.stack[-1]
        if f['state']!='VERIFIED': raise ValueError('not verified')
        f.update(state='EXECUTED',result=deepcopy(observations)); self.emit('EXECUTE',id=f['id'],result=deepcopy(observations))
    def close(self):
        f=self.stack[-1]
        if f['state']!='EXECUTED': raise ValueError('not executed')
        if digest(self.stack[-2])!=f['parent_hash']: raise ValueError('parent drift')
        self.stack.pop(); self.stack[-1]['findings'].append(dict(child=f['id'],result=deepcopy(f['result']),nested=deepcopy(f['findings'])))
        self.emit('RETURN',id=f['id'],parent=self.stack[-1]['id'])

def run():
    k=Kernel(); blocked=[]
    def reject(name,fn):
        try: fn()
        except ValueError: blocked.append(name)
        else: raise AssertionError(name)
    for domain in ('Jane','Toph','Patricia'):
        k.open(domain,'Inspect supplied audit fixture'); k.extrapolate('Inspect original record')
        reject('premature execution',lambda:k.execute({}))
        reject('casual approval',lambda:k.verify('I like it'))
        reject('premature closure',k.close)
        k.verify(True)
        k.open('Lattice','Check provenance'); k.extrapolate('Compare source identifiers'); k.verify(True)
        k.open('Evidence','Inspect duplicate source'); k.extrapolate('Count unique roots'); k.verify(True)
        reject('depth overflow',lambda:k.open('overflow','test'))
        k.execute({'roots':['A','A'],'unique':1}); k.close()
        k.execute({'independent_corroboration':False}); k.close()
        k.execute({'disposition':'request independent evidence'}); k.close()
        assert k.stack[0]['cursor']==19 and len(k.stack)==1
    k.open('drift-test','Check parent mutation'); k.extrapolate('probe'); k.verify(True); k.execute({'test':True})
    k.stack[0]['cursor']=20; reject('parent drift',k.close); k.stack[0]['cursor']=19; k.close()
    for i,e in enumerate(k.log):
        assert e['hash']==digest({a:b for a,b in e.items() if a!='hash'})
        assert e['previous']==(k.log[i-1]['hash'] if i else '0'*64)
    return dict(addresses=366,allocation=[3333,3333,3333,1],max_depth=k.limit,events=len(k.log),returns=sum(e['kind']=='RETURN' for e in k.log),blocked=blocked,parent_cursor=k.stack[0]['cursor'],parent=k.stack[0],log=k.log)
if __name__=='__main__':
    out=run(); Path(__file__).with_name('atom132_results.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({k:v for k,v in out.items() if k not in ('log','parent')},indent=2))
