#!/usr/bin/env python3
"""BIO-RF-008: sampled tesseract projection, standard library only."""
import math,json,itertools
V=list(itertools.product((-1,1),repeat=4))
def project(deg):
 t=math.radians(deg);c,s=math.cos(t),math.sin(t)
 return [(450+3/(4-z*s-w*c)*155*(x-.52*(z*c-w*s)),335+3/(4-z*s-w*c)*155*(y+.38*(z*c-w*s))) for x,y,z,w in V]
def grid(deg):
 a=[0]*9
 for x,y in project(deg):
  a[3*max(0,min(2,int(y/(670/3))))+max(0,min(2,int(x/300)))]+=1
 return a
def test():
 rows=[]
 for hz in (4,1.2,1,.8):
  step=90/hz;alias=(step+45)%90-45
  actual=[grid(17+n*step) for n in range(12)]
  assert actual==[grid(17+n*alias) for n in range(12)]
  rows.append(dict(hz=hz,step=step,alias=alias,unique_patterns=len(set(map(tuple,actual)))))
 return rows
if __name__=='__main__': print(json.dumps(test(),indent=2))
