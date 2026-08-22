# Rahil Gallery Django API (Strangler Fig)

Sibling of [Rahil-gallery-backend-go](../Rahil-gallery-backend-go). Shares Postgres and Go-issued JWTs.
Auth, CRM customers, and catalog stay on Go. Cart / Orders / Payments / Promotions live here.

## Ownership

See [docs/adr-table-ownership.md](docs/adr-table-ownership.md).

| Owner | Tables |
|-------|--------|
| Go | `users`, `roles`, `refresh_tokens`, `customers`, catalog, inventory |
| Django | `carts`, `cart_items`, `orders`, `order_items`, `payments`, `coupons`, … |

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # set DATABASE_URL + JWT_ACCESS_SECRET to match Go
```

### First migrate against an existing Go DB

Commerce tables already exist from Go `000001`. Claim them without recreating:

```bash
python manage.py migrate --fake-initial
```

On a brand-new empty database (rare), run Go migrations first, then the same command.

### Run

```bash
python manage.py runserver 0.0.0.0:8000
```

Health: `GET /health`  
Cart (Bearer Go access JWT): `GET /api/v1/carts/me`

## Auth

- Go issues HS256 access JWTs with `JWT_ACCESS_SECRET`
- Django `GoJWTAuthentication` verifies `sub` → unmanaged `identity.User`
- Refresh stays on Go: `POST /api/v1/auth/refresh`

## Next.js proxy

Client routes commerce prefixes to this service (`DJANGO_API_PROXY_URL`, default `:8000`)
and everything else to Go (`GO_API_PROXY_URL`, default `:8081`).
