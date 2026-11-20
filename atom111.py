import json
from pathlib import Path
import numpy as np
TURN=1296000; DOUBLE=2*TURN; STEP=10800
# Clock is exact integer arcseconds; continuous angles are not restricted to 48 spinors.
def state(t,arm=0):
    lap,phase=divmod(t,TURN)
    slot,within=divmod(phase,STEP)
    return (3*slot+arm+1,within,lap%2)
def run():
    t=np.arange(DOUBLE,dtype=np.int64)
    phase=t%TURN; slot=phase//STEP; within=phase%STEP; sign=t//TURN
    assert np.array_equal(slot*STEP+within+sign*TURN,t)
    assert np.array_equal(np.bincount(slot),np.full(120,2*STEP))
    for arm in range(3):
        for k in range(120):
            a=3*k+arm+1
            assert state(k*STEP,arm)==(a,0,0)
            assert state(k*STEP+TURN,arm)==(a,0,1)
            assert state(k*STEP+DOUBLE,arm)==(a,0,0)
    assert sorted(3*k+a+1 for k in range(120) for a in range(3)) + list(range(361,367))==list(range(1,367))
    for x in (-DOUBLE-1,-TURN,-1,0,1,TURN,DOUBLE):
        assert state(x)==state(x+DOUBLE)
    return dict(addresses=366,reserved_bonds=4,turn_arcseconds=TURN,double_turn_arcseconds=DOUBLE,slot_arcseconds=STEP,clock_states=len(t),address_clock_pairs_checked=3*len(t),boundary_checks=1080,signed_period=DOUBLE,spatial_period=TURN,axis_addresses=list(range(361,367)),note='Parity tracks complete turns, not the instantaneous quaternion sign in a chosen chart. Axis labels held fixed.')
if __name__=='__main__':
    out=run();Path(__file__).with_name('atom111_results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
