import os, shutil
from pathlib import Path
candidates=[]
for name in ('gcloud','gcloud.cmd','gcloud.exe'):
    p=shutil.which(name)
    if p: candidates.append(Path(p))
local=os.environ.get('LOCALAPPDATA')
pf=os.environ.get('ProgramFiles')
pfx86=os.environ.get('ProgramFiles(x86)')
for base in [local,pf,pfx86,'C:\\']:
    if not base: continue
    candidates += [
        Path(base)/'Google'/'Cloud SDK'/'google-cloud-sdk'/'bin'/'gcloud.cmd',
        Path(base)/'google-cloud-sdk'/'bin'/'gcloud.cmd',
    ]
seen=set()
for p in candidates:
    s=str(p)
    if s in seen: continue
    seen.add(s)
    if p.exists(): print(s)
