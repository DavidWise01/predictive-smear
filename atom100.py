import numpy as np,json,hashlib
from pathlib import Path
from atom095 import data,REG,MODES,T
from atom098 import evaluate as baseline
from atom099 import H,C,S,P

def pack(x,p,v,off,mode,depth,cal,active,sw,bit):
    # RGB channels encode observed signal, probe and velocity; 10-bit offset.
    q=lambda a,l,h,n: int(np.clip(round((a-l)/(h-l)*((1<<n)-1)),0,(1<<n)-1))
    rgb=[q(x,-12,12,8),q(p,-12,12,8),q(v,-.12,.12,8)]
    flags=int(mode)|(int(cal)<<2)|(int(sw)<<3)|(int(bit)<<4)|(int(active)<<5)
    word=rgb[0]|rgb[1]<<8|rgb[2]<<16|q(off,-12,12,10)<<24|flags<<34|1<<40|1<<41
    return word.to_bytes(6,'little')
def seal(records):
    h=bytes(32)
    for i,row in enumerate(records):h=hashlib.sha256(h+i.to_bytes(4,'little')+row).digest()
    return h.hex()
def evaluate(d,gate=.12,margin=.0005):
    y,x,p=d;n=len(y);off=np.zeros(n);vel=np.zeros(n);mode=np.ones(n,int);sq=0.;k=sw=wrong=calls=nodes=0;peak=0.;records=[];depths={}
    for t in range(T):
        innovation=p[:,t]-p[:,t-1]-vel if t else np.zeros(n)
        if t:vel=.85*vel+.15*(p[:,t]-p[:,t-1])
        old=mode.copy();idx=np.flatnonzero((abs(innovation)>gate)|(abs(p[:,t]-off)>2*gate));calls+=len(idx);depth=np.zeros(n,int)
        if len(idx):
            v=vel[idx];q=p[idx,t];a=np.repeat(off[idx,None],3,axis=1);b=np.clip(np.cbrt(.03*abs(v))[:,None],MODES[:,0],MODES[:,1]);loss=S*(old[idx,None]!=np.arange(3));active=np.arange(len(idx));last=0;previous=np.full(len(idx),-1);limit=min(13,T-t)
            for h in sorted({min(h,limit) for h in H}):
                if not len(active):break
                for step in range(last,h):
                    f=q[active,None]+step*v[active,None];u=abs(f-a[active])>b[active];a[active]=np.where(u,f,a[active]);loss[active]+=(f-a[active])**2+C*u;nodes+=3*len(active)
                rank=np.argsort(loss[active],axis=1);best=rank[:,0];gap=loss[active,rank[:,1]]-loss[active,best];done=((best==previous[active])&(gap>=margin*h))|(h==limit);chosen=active[done];new=best[done];mode[idx[chosen]]=new;depth[idx[chosen]]=h;depths[str(h)]=depths.get(str(h),0)+len(chosen);previous[active]=best;active=active[~done];last=h
        sw+=int((mode!=old).sum());bound=np.clip(np.cbrt(.03*abs(vel)),MODES[mode,0],MODES[mode,1]);u=abs(p[:,t]-off)>bound;off[u]=p[u,t];k+=int(u.sum());z=x[:,t]-off-y[:,t];bits=x[:,t]-off>=.5;wrong+=int((bits!=y[:,t]).sum());sq+=float((z*z).sum());peak=max(peak,float(abs(z).max()))
        # Audit one representative trajectory per regime; rest are performance trials.
        records.append(pack(x[0,t],p[0,t],vel[0],off[0],mode[0],depth[0],u[0],depth[0]>0,mode[0]!=old[0],bits[0]))
    head=seal(records);tamper=0
    for i in range(T):
        for b in range(42):
            copy=records.copy();copy[i]=(int.from_bytes(copy[i],'little')^(1<<b)).to_bytes(6,'little');tamper+=seal(copy)!=head
    assert tamper==T*42 and sum(depths.values())==calls
    return dict(cost=(sq+C*k+S*sw+P*nodes)/(n*T),wrong=wrong,peak=peak,calls=calls,nodes=nodes,switches=sw,depths=depths,head=head,records=[r.hex() for r in records],tamper_detected=tamper)
def run():
    out={}
    for i,r in enumerate(REG):
        d=data(2000+i,2000,r);out[['stable','mixed','turbulent','shock'][i]]={'balanced':baseline(d,np.inf),'integrated':evaluate(d)}
    return dict(regimes=out,evaluations=4*2000*T*2,promotion=all(r['integrated']['cost']<=r['balanced']['cost'] and r['integrated']['peak']<=.30 and r['integrated']['wrong']==0 for r in out.values()))
if __name__=='__main__':
    out=run();Path(__file__).with_name('atom100_results.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:{m:{a:b for a,b in v.items() if a!='records'} for m,v in r.items()} for k,r in out['regimes'].items()},indent=2));print('promotion',out['promotion'])
