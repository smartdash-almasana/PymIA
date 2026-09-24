import subprocess, sys
from pathlib import Path
WT=Path(r'E:\BuenosPasos\smartbridge\PymIA-service1-cafeteria')
GCLOUD=r'E:\Program Files (x86)\google-cloud-sdk\bin\gcloud.CMD'

def run(args):
    p=subprocess.run([GCLOUD,*args],cwd=WT,text=True,capture_output=True,shell=False)
    print('$ gcloud',' '.join(args))
    print(p.stdout.strip())
    if p.stderr.strip(): print(p.stderr.strip(),file=sys.stderr)
    print('RC=',p.returncode)
    if p.returncode: raise SystemExit(p.returncode)

run(['config','get-value','project'])
run(['auth','list','--filter=status:ACTIVE','--format=value(account)'])
run(['run','services','describe','pymia-service1','--project','pymia-503920','--region','southamerica-east1','--format=json(metadata.name,status.url,status.latestReadyRevisionName,spec.template.spec.containers[0].image,spec.template.spec.containers[0].env)'])
