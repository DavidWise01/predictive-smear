import numpy as np,json
from pathlib import Path
rng=np.random.default_rng(85)
N=1000000
rows=[]
for q in (0,.01,.05,.10,.20):
    shared=rng.random(N)<q
    independent=rng.random((N,3))<.1
    errors=np.where(shared[:,None],True,independent)
    unanimous=errors.all(axis=1)
    # Shared incidents carry one authenticated origin in this synthetic model.
    eligible=~shared
    rows.append(dict(shared_probability=q,trials=N,shared_incidents=int(shared.sum()),unanimous_false=int(unanimous.sum()),ancestry_gated_false=int((unanimous&eligible).sum()),held_shared=int(shared.sum()),expected_raw=q+(1-q)*.001,expected_gated=(1-q)*.001))
out=dict(seed=85,independent_error=.1,rows=rows)
Path(__file__).with_name('atom085_results.json').write_text(json.dumps(out,indent=2)); print(json.dumps(out,indent=2))
