#!/bin/bash
# Generate self-signed TLS certs for local production Compose (--profile proxy).
# Not for production — use Cloudflare Origin or Let's Encrypt on real hosts.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SSL_DIR="${SCRIPT_DIR}/../nginx/ssl/a2ztools.com"
mkdir -p "${SSL_DIR}"

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout "${SSL_DIR}/privkey.pem" \
  -out "${SSL_DIR}/fullchain.pem" \
  -subj "/CN=*.a2ztools.com/O=A2Z Tools Dev"

chmod 600 "${SSL_DIR}/privkey.pem"
echo "Wrote ${SSL_DIR}/fullchain.pem and privkey.pem"
