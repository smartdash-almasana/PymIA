import subprocess, sys
from pathlib import Path
WT=Path(r'E:\BuenosPasos\smartbridge\PymIA-service1-cafeteria')
GCLOUD=r'E:\Program Files (x86)\google-cloud-sdk\bin\gcloud.CMD'
cmd=[GCLOUD,'run','services','describe','pymia-service1','--project','pymia-503920','--region','southamerica-east1','--format=value(status.url,status.latestCreatedRevisionName,status.latestReadyRevisionName,spec.template.spec.containers[0].image)']
p=subprocess.run(cmd,cwd=WT,text=True,capture_output=True,shell=False)
print(p.stdout.strip())
if p.stderr.strip(): print(p.stderr.strip(),file=sys.stderr)
raise SystemExit(p.returncode)
