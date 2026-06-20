#!/usr/bin/env bash
# Validate production Nginx config outside Compose.
# Upstream hosts are stubbed — real resolution happens on the a2z-network.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
NGINX_DIR="$ROOT/infrastructure/nginx"

docker run --rm \
  --add-host backend:127.0.0.1 \
  --add-host frontend:127.0.0.1 \
  -v "$NGINX_DIR/nginx.prod.conf:/etc/nginx/nginx.conf:ro" \
  -v "$NGINX_DIR/conf.d:/etc/nginx/conf.d:ro" \
  -v "$NGINX_DIR/proxy_params.conf:/etc/nginx/proxy_params.conf:ro" \
  -v "$NGINX_DIR/ssl:/etc/nginx/ssl:ro" \
  nginx:1.27-alpine nginx -t

echo "nginx: configuration OK"
