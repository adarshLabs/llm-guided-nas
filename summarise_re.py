import json,glob,statistics as s
b=[]
for p in sorted(glob.glob('results/runs/re_seed*.jsonl')):
    r=[json.loads(l) for l in open(p)][1:]
    t=max(r,key=lambda x:x['valid'])['test']; b.append(t); print(p,t)
print(f'n={len(b)} mean={s.mean(b):.3f}', f'std={s.stdev(b):.3f}' if len(b)>1 else 'std=n/a (one seed)')
