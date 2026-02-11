# LORD Chain Architecture (6.0+)

## Stack
- FastAPI
- SQLAlchemy 2.x
- PostgreSQL
- Alembic migrations
- JWT auth + OTP
- Admin token auth
- Decimal money model (Numeric(20,8))

## Key Rules
- 1 tx = 1 block
- block fields: block_index, prev_hash, block_hash
- tx is atomic (balances + block + audit)
- single active user session (sid)
- admin lockout: 3 fails -> 1 hour, token timeout 30 min, single admin session

## Modules
- src/models: User, Transaction, AuditLog
- src/services: security, blockchain, audit, auth_deps, admin_deps
- src/routers: auth, users, tx, explorer, admin, ui
