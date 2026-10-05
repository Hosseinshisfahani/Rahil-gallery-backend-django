# Rahil Gallery Backend (Django)

Strangler Fig commerce API: Django + DRF.

Sibling of [Rahil-gallery-backend-go](../Rahil-gallery-backend-go). Both share Postgres and Go-issued JWTs. Auth, CRM customers, and catalog stay on Go. Cart, orders, payments, and promotions live here.

The Next.js app in [Rahil-gallery-frontend](../Rahil-gallery-frontend) proxies commerce prefixes (`/api/v1/carts`, `/orders`, `/payments`, `/promotions`, `/coupons`) to this process (default `:8000`).

Live server orchestration and deploys are managed via `~/source/rahil-stack`.

## Ownership

See [docs/adr-table-ownership.md](docs/adr-table-ownership.md). `make check-ownership` blocks Django migrations that alter Go-owned tables.

| Owner | Tables |
|-------|--------|
| Go | `users`, `roles`, `refresh_tokens`, `customers`, catalog, inventory |
| Django | `carts`, `cart_items`, `orders`, `order_items`, `payments`, `coupons`, … |

Go uses **golang-migrate**. Django uses **`django_migrations`**. Never mutate the same table from both ledgers.

## Local development

Start Go's Postgres first (`make docker-dev` in [Rahil-gallery-backend-go](../Rahil-gallery-backend-go)). Copy `DATABASE_URL` and `JWT_ACCESS_SECRET` from that `.env`.

```bash
cp .env.example .env   # match Go DATABASE_URL + JWT_ACCESS_SECRET
make install
make migrate-fake      # first claim of existing Go commerce tables
make run               # http://127.0.0.1:8000
```

Equivalent without Make:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate --fake-initial
python manage.py runserver 0.0.0.0:8000
```

`--fake-initial` records Django's initial commerce migrations without `CREATE TABLE` — those tables already exist from Go `000001`. On a brand-new empty database, run Go migrations first, then the same command.

| Command | Description |
|---------|-------------|
| `make install` | Create `.venv` and install `requirements.txt` |
| `make run` | `runserver` on `:8000` |
| `make migrate` | Apply Django migrations |
| `make migrate-fake` | `migrate --fake-initial` |
| `make check-ownership` | Fail if a migration touches Go-owned tables |

## Docker

Requires Go's Postgres already published on the host (default `:5433`):

```bash
cp .env.example .env
docker compose up --build
```

The container listens on `${DJANGO_PORT:-8000}` and reaches Postgres via `host.docker.internal`.

## Configuration

See `.env.example`. `DJANGO_SECRET_KEY` is **not** the JWT secret.

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | Same Postgres as Go (host `:5433` for `make docker-dev`) |
| `JWT_ACCESS_SECRET` | Same HS256 secret Go uses to **issue** access tokens |
| `DJANGO_SECRET_KEY` | Django signing key only |
| `DJANGO_DEBUG` | Default `true` locally |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hosts |
| `DJANGO_PORT` | Compose publish port (default `8000`) |

## Auth

- Go issues HS256 access JWTs (`sub` = user UUID, plus `email`, `role`, `exp`, `iat`, `jti`).
- `GoJWTAuthentication` verifies the Bearer token and maps `sub` to unmanaged `identity.User`.
- Refresh stays on Go: `POST /api/v1/auth/refresh`.

## API surface

Prefix: `/api/v1`. Same success/error envelope as Go.

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | — | Liveness |
| GET | `/api/v1/carts/me` | Bearer | Get or create the current user's cart |
| POST | `/api/v1/carts/me/items` | Bearer | Add a line (`variant_id`, `quantity`, `unit_price_snapshot`) |
| PATCH | `/api/v1/carts/me/items/:id` | Bearer | Update quantity |
| DELETE | `/api/v1/carts/me/items/:id` | Bearer | Remove a line |

Orders, payments, and promotions are proxied by the frontend to this service; handlers land here as those contexts move off Go.

```bash
curl -s http://localhost:8000/health
curl -s http://localhost:8000/api/v1/carts/me -H "Authorization: Bearer TOKEN"
```

## CI

`.github/workflows/ci.yml` runs the ownership gate, `manage.py check`, and identity unit tests.
