import math

def bound(x):
    if math.isnan(x): return None
    if x == 0: return 0
    if math.isinf(x): return 5 if x>0 else -5
    return (1 if x>0 else -1)*min(5,math.ceil(abs(x)))

if __name__=='__main__':
    for x in [-float('inf'),-1e308,-.1,0,.1,1e308,float('inf'),float('nan')]:
        print(x,bound(x))
