# Validate production Nginx config outside Compose.
# Upstream hosts are stubbed — real resolution happens on the a2z-network.
$ErrorActionPreference = "Stop"
$Root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$Nginx = Join-Path $Root "infrastructure\nginx"

docker run --rm `
  --add-host backend:127.0.0.1 `
  --add-host frontend:127.0.0.1 `
  -v "${Nginx}/nginx.prod.conf:/etc/nginx/nginx.conf:ro" `
  -v "${Nginx}/conf.d:/etc/nginx/conf.d:ro" `
  -v "${Nginx}/proxy_params.conf:/etc/nginx/proxy_params.conf:ro" `
  -v "${Nginx}/ssl:/etc/nginx/ssl:ro" `
  nginx:1.27-alpine nginx -t

Write-Host "nginx: configuration OK"
