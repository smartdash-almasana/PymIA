import json, shutil, subprocess, sys, tempfile, urllib.request, zipfile
from pathlib import Path

WT = Path(r'E:\BuenosPasos\smartbridge\PymIA-service1-cafeteria')
GCLOUD = r'E:\Program Files (x86)\google-cloud-sdk\bin\gcloud.CMD'
PROJECT = 'pymia-503920'
REGION = 'southamerica-east1'
SERVICE = 'pymia-service1'
EXPECTED_SHA = 'ea61875366fd5e3b564260700da7189225738573'
ENTRYPOINT = 'python -m pymia.smartpyme.service_1_semantic_reception_server_v1'

def run(cmd, cwd=None):
    p = subprocess.run(cmd, cwd=cwd or WT, text=True, capture_output=True, shell=False)
    print('$', ' '.join(str(x) for x in cmd))
    if p.stdout.strip(): print(p.stdout.strip())
    if p.stderr.strip(): print(p.stderr.strip(), file=sys.stderr)
    print('RC=', p.returncode)
    if p.returncode != 0:
        raise SystemExit(p.returncode)
    return p

sha = run(['git','rev-parse','HEAD']).stdout.strip()
if sha != EXPECTED_SHA:
    print(f'ABORT unexpected HEAD {sha}', file=sys.stderr)
    raise SystemExit(3)

root = Path(tempfile.mkdtemp(prefix='pymia-service1-release-'))
try:
    archive = root / 'release.zip'
    source = root / 'source'
    source.mkdir()
    run(['git','archive','--format=zip','-o',str(archive),sha])
    with zipfile.ZipFile(archive) as zf:
        zf.extractall(source)
    run([
        GCLOUD,'run','deploy',SERVICE,
        '--source',str(source),
        '--project',PROJECT,
        '--region',REGION,
        '--allow-unauthenticated',
        '--set-build-env-vars',f'GOOGLE_ENTRYPOINT={ENTRYPOINT}',
        '--quiet'
    ], cwd=source)
    desc = run([
        GCLOUD,'run','services','describe',SERVICE,
        '--project',PROJECT,'--region',REGION,
        '--format=json(status.url,status.latestReadyRevisionName,status.traffic,spec.template.spec.containers[0].image)'
    ], cwd=source)
    data = json.loads(desc.stdout)
    url = data['status']['url']
    revision = data['status']['latestReadyRevisionName']
    image = data['spec']['template']['spec']['containers'][0]['image']
    traffic = data['status'].get('traffic', [])
    print('DEPLOYED_SHA=', sha)
    print('REVISION=', revision)
    print('URL=', url)
    print('IMAGE=', image)
    print('TRAFFIC=', json.dumps(traffic, separators=(',',':')))
    req = urllib.request.Request(url, method='GET', headers={'User-Agent':'PymIA-Deploy-Smoke/1.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read(256)
        print('HTTP_STATUS=', resp.status)
        print('CONTENT_TYPE=', resp.headers.get('content-type',''))
        print('BODY_PREFIX_BYTES=', len(body))
        if resp.status != 200:
            raise SystemExit(4)
finally:
    shutil.rmtree(root, ignore_errors=True)
