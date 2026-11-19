import numpy as np,json
from pathlib import Path

def run():
    rng=np.random.default_rng(87); n=200000; rows=[]
    for q in (0,.01,.05,.10,.20):
        truth=rng.integers(0,2,n); common=rng.random(n)<q
        ref=truth ^ (common | (rng.random(n)<.02))
        witnesses=truth[:,None] ^ (common[:,None] | (rng.random((n,3))<.1))
        probes=truth[:,None] ^ (rng.random((n,3))<.02)
        unanimous=(witnesses==witnesses[:,:1]).all(1); candidate=witnesses[:,0]
        verified=(probes==probes[:,:1]).all(1); recovered=probes[:,0]
        policies={'blind':unanimous & (candidate==ref),'audit_hold':unanimous & (candidate==ref) & verified & (ref==recovered),'audit_recover':unanimous & verified & (candidate==recovered)}
        row={'common_fault_probability':q,'trials':n,'reference_faults':int((ref!=truth).sum()),'reference_recovery_correct':int((verified & (ref!=truth) & (recovered==truth)).sum()),'reference_recovery_wrong':int((verified & (ref==truth) & (recovered!=truth)).sum()),'policies':{}}
        for name,a in policies.items():
            correct=int((a & (candidate==truth)).sum()); wrong=int((a & (candidate!=truth)).sum()); hold=int((~a).sum()); assert correct+wrong+hold==n
            row['policies'][name]=dict(correct=correct,wrong=wrong,hold=hold)
        rows.append(row)
    return dict(seed=87,rows=rows,assumptions={'witness_error':.1,'reference_error':.02,'probe_error':.02,'probes_independent_of_common_fault':True})
if __name__=='__main__':
    out=run();Path(__file__).with_name('atom087_results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
