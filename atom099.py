import numpy as np,json
from pathlib import Path
from atom095 import data,REG,MODES,T
from atom098 import evaluate as fixed
H=(1,2,3,5,8,13); C=.02; S=.002; P=.00001

def progressive(d,gate=.12,margin=.0005):
 y,x,p=d;n=len(y);off=np.zeros(n);vel=np.zeros(n);mode=np.ones(n,int);sq=0.;k=sw=wrong=calls=nodes=0;peak=0.;depths={str(h):0 for h in H}
 for t in range(T):
  innovation=p[:,t]-p[:,t-1]-vel if t else np.zeros(n)
  if t:vel=.85*vel+.15*(p[:,t]-p[:,t-1])
  idx=np.flatnonzero((abs(innovation)>gate)|(abs(p[:,t]-off)>2*gate));calls+=len(idx)
  if len(idx):
   v=vel[idx];q=p[idx,t];old=mode[idx].copy();a=np.repeat(off[idx,None],3,axis=1);b=np.clip(np.cbrt(.03*abs(v))[:,None],MODES[:,0],MODES[:,1]);loss=S*(old[:,None]!=np.arange(3));active=np.arange(len(idx));last=0;previous=np.full(len(idx),-1);limit=min(13,T-t)
   for h in sorted({min(h,limit) for h in H}):
    if not len(active):break
    for step in range(last,h):
     f=q[active,None]+step*v[active,None];u=abs(f-a[active])>b[active];a[active]=np.where(u,f,a[active]);loss[active]+=(f-a[active])**2+C*u;nodes+=3*len(active)
    rank=np.argsort(loss[active],axis=1);best=rank[:,0];gap=loss[active,rank[:,1]]-loss[active,best];early=(best==previous[active])&(gap>=margin*h);done=early|(h==limit)
    chosen=active[done];new=best[done];sw+=int((new!=old[chosen]).sum());mode[idx[chosen]]=new;depths[str(h)]=depths.get(str(h),0)+len(chosen);previous[active]=best;active=active[~done];last=h
  bound=np.clip(np.cbrt(.03*abs(vel)),MODES[mode,0],MODES[mode,1]);u=abs(p[:,t]-off)>bound;off[u]=p[u,t];k+=int(u.sum());z=x[:,t]-off-y[:,t];sq+=float((z*z).sum());wrong+=int(((z+y[:,t]>=.5)!=y[:,t]).sum());peak=max(peak,float(abs(z).max()))
 assert sum(depths.values())==calls
 return dict(cost=(sq+C*k+S*sw+P*nodes)/(n*T),calls=calls,nodes=nodes,switches=sw,wrong=wrong,peak=peak,depths=depths)

def run():
 out={}
 for i,r in enumerate(REG):
  d=data(1990+i,2000,r);out[['stable','mixed','turbulent','shock'][i]]={'balanced':fixed(d,np.inf),'full':fixed(d,.12),'progressive':progressive(d)}
 return dict(horizons=H,gate=.12,margin=.0005,regimes=out,evaluations=4*2000*T*3,promotion=all(r['progressive']['cost']<=r['balanced']['cost'] and r['progressive']['wrong']==0 and r['progressive']['peak']<=.3 for r in out.values()))
if __name__=='__main__':
 out=run();Path(__file__).with_name('atom099_results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
