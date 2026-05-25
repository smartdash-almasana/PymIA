# HERMES_BASIC_COMMANDS

Estado: VIGENTE

## Objetivo

Guía corta para arrancar el dashboard local de Hermes desde terminal en Windows.

## Comando estándar

```powershell
hermes dashboard
```

URL esperada:

```text
http://127.0.0.1:9119
```

## Si no abre en Windows (ERR_CONNECTION_REFUSED)

En algunos entornos Windows, `hermes dashboard` falla por encoding CP1252 al imprimir caracteres Unicode o por build web no compatible con scripts Unix.

### Paso 1 — Build web manual (una vez)

```powershell
Set-Location "E:\BuenosPasos\smartbridge\hermes-agent\web"
npm install
```

Si `npm run build` falla por `rm`/`cp`, sincronizar assets y compilar manualmente:

```powershell
$web = "E:\BuenosPasos\smartbridge\hermes-agent\web"
Remove-Item -Recurse -Force "$web\public\fonts" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$web\public\ds-assets" -ErrorAction SilentlyContinue
Copy-Item -Recurse -Force "$web\node_modules\@nous-research\ui\dist\fonts" "$web\public\fonts"
Copy-Item -Recurse -Force "$web\node_modules\@nous-research\ui\dist\assets" "$web\public\ds-assets"
Set-Location $web
npx vite build
```

### Paso 2 — Levantar servidor web directo con UTF-8

```powershell
Set-Location "E:\BuenosPasos\smartbridge\hermes-agent"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
python -c "from hermes_cli.web_server import start_server; start_server(host='127.0.0.1', port=9119, open_browser=False)"
```

### Paso 3 — Abrir navegador

```powershell
Start-Process "http://127.0.0.1:9119"
```

## Verificación rápida

```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:9119" -UseBasicParsing
```

Si responde `StatusCode 200`, dashboard operativo.
