# ADR: Shared Postgres table ownership (Go vs Django)

## Status

Accepted — Strangler Fig cutover

## Context

`Rahil-gallery-backend-go` (Go) and `Rahil-gallery-backend-django` share the `rahil_gallery` PostgreSQL database.
Go uses **golang-migrate** (`schema_migrations`). Django uses **`django_migrations`**.
Both ledgers must never mutate the same table.

Commerce tables (`carts`, `orders`, `payments`, `coupons`, …) were created in Go migration `000001` but have no Go HTTP handlers. Django adopts them for new bounded contexts.

## Decision

| Tables | Owner | Django `Meta.managed` | Migrator |
|--------|-------|----------------------|----------|
| `users`, `roles`, `refresh_tokens`, `user_addresses` | Go | `False` | golang-migrate only |
| `customers`, catalog, inventory, observability | Go | `False` | golang-migrate only |
| `carts`, `cart_items`, `orders`, `order_items`, `order_status_history`, `payments`, `coupons`, `coupon_redemptions` | Django | `True` (after claim) | Django migrations only |
| `django_*`, `auth_group*`, `auth_permission`, etc. | Django | `True` | Django only |

### Rules

1. Go **must not** add migrations that `CREATE` / `ALTER` / `DROP` Django-owned commerce tables.
2. Django **must not** emit migrations that alter Go-owned tables (`users`, `roles`, `customers`, `products`, …).
3. First commerce claim on an existing DB: `python manage.py migrate --fake-initial` so Django records state without `CREATE TABLE`.
4. Access JWTs are issued only by Go (`JWT_ACCESS_SECRET`, HS256, `sub` = user UUID). Django verifies only.
5. Refresh tokens remain Go-owned (`refresh_tokens` + `/api/v1/auth/*`).

## Consequences

- Cross-stack column needs on Go tables use expand-contract: Go adds nullable column first; Django reads via unmanaged models.
- CI ownership greps enforce the freeze (see `scripts/check_migration_ownership.sh`).
