# Cloudflare — Production Configuration Reference

Apply these settings in the Cloudflare dashboard for `a2ztools.com` (replace with your domain).

## DNS

| Name | Type | Content | Proxy |
|------|------|---------|-------|
| `@` | CNAME | `www` | Proxied |
| `www` | A/AAAA | `<ORIGIN_IP>` | **Proxied** |
| `dashboard` | A/AAAA | `<ORIGIN_IP>` | **Proxied** |
| `api` | A/AAAA | `<ORIGIN_IP>` | **DNS only** (grey cloud) |

## SSL/TLS

- Mode: **Full (strict)**
- Always Use HTTPS: **On**
- Minimum TLS: **1.2**
- TLS 1.3: **On**
- HSTS: enable after 48h stable HTTPS (`max-age=31536000; includeSubDomains; preload`)

## Origin certificate

1. SSL/TLS → Origin Server → Create Certificate (`*.a2ztools.com`, `a2ztools.com`)
2. Save to `infrastructure/nginx/ssl/a2ztools.com/fullchain.pem` and `privkey.pem` on origin
3. See `infrastructure/nginx/ssl/README.md`

## Cache rules

Import or recreate from `cache-rules.json`:

- **Cache** `www` → `/_next/static/*` — Edge TTL 1 year
- **Bypass** `www` → `/api/*`, `/admin-dashboard/*`, `/cart`, `/checkout`
- **Bypass** `dashboard` → all paths
- **Bypass** `api` → all paths (belt-and-suspenders even when grey-cloud)

## WAF

- OWASP Core Ruleset: **On**
- Rate limit: `POST */api/v1/auth/login*` — 20 req/min/IP
- Rate limit: `POST */api/v1/auth/register*` — 10 req/min/IP
- Optional: challenge on `dashboard.a2ztools.com` for non-AU traffic

## Bot management

- Super Bot Fight Mode on `www` checkout paths

## Logpush (optional)

- Destination: S3 or R2 bucket `a2z-cloudflare-logs`
- Fields: ClientIP, ClientRequestHost, EdgeResponseStatus, WAFAction
