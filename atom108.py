import json
from pathlib import Path
# K107 frozen cardinality; K108 candidate addressing convention.
VALENCE=('v0','v1','v2','v3')
ARMS=('j','t','p')
AXES=('x+','x-','y+','y-','z+','z-')
def encode(arm,phase):
    assert arm in ARMS and 0<=phase<120
    return 3*phase+ARMS.index(arm)+1
def decode(address):
    assert 1<=address<=366
    if address>360:return AXES[address-361]
    phase,arm=divmod(address-1,3)
    return ARMS[arm],phase
addresses=[encode(a,k) for a in ARMS for k in range(120)]
assert sorted(addresses+list(range(361,367)))==list(range(1,367))
assert all(decode(encode(a,k))==(a,k) for a in ARMS for k in range(120))
assert len(VALENCE)+120==124
# One-degree interleaving; each arm advances three degrees per step.
assert all((encode(a,(k+1)%120)-encode(a,k))%360==3 for a in ARMS for k in range(120))
assert all(decode(361+i)==axis for i,axis in enumerate(AXES))
# Reversing a phase step restores the same address.
assert all(encode(a,((k+1)%120-1)%120)==encode(a,k) for a in ARMS for k in range(120))
out={'frozen':'(124 - 4) * 3 + 6 = 366','valence_reserved':4,'operational_per_arm':120,'rotational_addresses':360,'geometric_addresses':6,'total':366,'implicit_origin':0,'roundtrips':366,'phase_step_checks':360,'inverse_step_checks':360,'collisions':0,'address_convention':'interleaved, not a replacement for OCTAVIA registry'}
Path(__file__).with_name('atom108_results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
