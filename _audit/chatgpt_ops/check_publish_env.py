import subprocess, sys
from pathlib import Path
WORKTREE = Path(r'E:\BuenosPasos\smartbridge\PymIA-service1-cafeteria')

def run(cmd):
    p = subprocess.run(cmd, cwd=WORKTREE, text=True, capture_output=True, shell=False)
    print('$', ' '.join(cmd))
    print(p.stdout.strip())
    if p.stderr.strip(): print(p.stderr.strip(), file=sys.stderr)
    print('RC=', p.returncode)
    return p

run(['git','rev-parse','--abbrev-ref','HEAD'])
run(['git','rev-parse','HEAD'])
run(['gcloud','config','get-value','project'])
run(['gcloud','auth','list','--filter=status:ACTIVE','--format=value(account)'])
run(['gcloud','run','services','describe','pymia-service1','--project','pymia-503920','--region','southamerica-east1','--format=json(metadata.name,status.url,status.latestReadyRevisionName,spec.template.spec.containers[0].image)'])
