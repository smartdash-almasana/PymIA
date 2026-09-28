import subprocess, sys
from pathlib import Path
WT = Path(r'E:\BuenosPasos\smartbridge\PymIA-service1-cafeteria')
EXCLUDED = ('_audit/', 'tmp-r13d2-flow/', 'tmp-r13d2-radar/')

def run(args, check=True):
    p = subprocess.run(args, cwd=WT, text=True, capture_output=True, shell=False)
    print('$', ' '.join(args))
    if p.stdout: print(p.stdout)
    if p.stderr: print(p.stderr, file=sys.stderr)
    if check and p.returncode != 0:
        raise SystemExit(p.returncode)
    return p

run(['git','add','-A','--','.',':(exclude)_audit/**',':(exclude)tmp-r13d2-flow/**',':(exclude)tmp-r13d2-radar/**'])
name = run(['git','diff','--cached','--name-only']).stdout.splitlines()
for path in name:
    if path.startswith(EXCLUDED):
        print('ABORT excluded path staged:', path, file=sys.stderr)
        raise SystemExit(3)
print('STAGED_FILES=', len(name))
run(['git','diff','--cached','--stat'])
if not name:
    print('NOTHING_TO_COMMIT')
    raise SystemExit(0)
run(['git','commit','-m','refactor(service1): complete reconstruction and R13 sanitation'])
run(['git','rev-parse','HEAD'])
