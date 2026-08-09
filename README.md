# Velo Dash — Football Intelligence App API

FastAPI REST backend generated from the ERD in [app_docs/Football_Intelligence_App.sql](app_docs/Football_Intelligence_App.sql).

## Stack

- FastAPI + Uvicorn
- **Active data layer: flat CSV files** (`app/store/`) — no database required to run this
- Pydantic v2 / pydantic-settings
- Postgres/SQLAlchemy implementation still in the repo but currently inactive (see
  [Data backend](#data-backend) below)

## Project structure

```
app/
  core/            settings, CSV data dir config, password hashing, error codes
  store/           active data layer
    registry.py      single source of truth: entity fields, types, FKs, unique constraints
    csv_engine.py     thread-safe CSV read/write + type coercion
    repository.py     CsvRepository: list/get/create/update/delete + integrity checks
  schemas/         Pydantic Create/Update/Read schemas per resource (unchanged by backend)
  crud/            per-resource CsvRepository instances (thin wiring, see app/store/)
  api/
    router_factory.py      builds list/get/create/update/delete routes incl. sort/filter
    v1/endpoints/          one file per resource, wired via the factory
    v1/api.py              aggregates all resource routers
  models/          SQLAlchemy ORM models — inactive, kept for a future Postgres migration
  crud/base.py     SQLAlchemy CRUDBase — inactive, same reason
  core/database.py Postgres async engine/session — inactive, same reason
  main.py          FastAPI app instance, global exception handlers
data/
  *.csv            the actual dataset the API reads and writes, one file per entity
db/
  schema.sql       Postgres DDL, kept for the future migration
scripts/
  generate_mock_data.py   (re)generates data/*.csv with a consistent, FK-valid mock dataset
main.py            dev entrypoint (uvicorn runner)
```

Every table in the ERD (home_clubs, venues, own_teams, users, roles, permissions,
user_roles, role_permissions, seasons, competitions, player_positions,
system_modules, approval_workflows, approval_stages, approval_stage_approvers,
approval_requests, approval_actions, audit_logs) gets a full REST resource at
`/api/v1/<resource>` with `GET /`, `POST /`, `GET /{id}`, `PATCH /{id}`, `DELETE /{id}`
(audit logs are read/create only — no update, since they're an immutable log).

## Data backend

The API currently reads and writes flat CSV files under `DATA_DIR` (default: `./data`)
instead of a database — one CSV per entity, e.g. `data/home_clubs.csv`. This was a deliberate
"for now" choice to make the app deployable without provisioning a database. The trade-offs:

- **CRUD, sort, and filter all work** the same way they would against a DB (see below).
- **Referential integrity is enforced in code**, mirroring what Postgres would otherwise do:
  - creating/updating a row with a foreign key pointing at a non-existent row →
    `400 INVALID_REFERENCE`
  - violating a unique constraint (e.g. duplicate `roles.code`) → `409 CONFLICT`
  - deleting a row still referenced by another table (e.g. a `home_clubs` row with
    `own_teams`/`users` pointing at it) → `409 CONFLICT` — same RESTRICT-style behavior
    the DB schema implies (no `ON DELETE CASCADE` was defined).
- **Concurrency is in-process only** (a `threading.Lock` per CSV file). Fine for a single
  Uvicorn process; not safe across multiple processes/instances writing the same files.
- **No transactions across entities** — each request touches exactly one CSV file, which
  matches how the router/CRUD layer already calls it (one entity per endpoint).

All of this lives behind `app/store/registry.py` (the field/type/FK/unique definitions —
edit this first if the schema changes) and `app/store/repository.py` (`CsvRepository`,
the thing that actually enforces the rules above). `app/crud/*.py` just instantiates one
`CsvRepository` per resource and wires it into `app/api/router_factory.py`.

### Switching back to Postgres later

The SQLAlchemy models, `CRUDBase`, `app/core/database.py`, and `db/schema.sql` are all still
here and untouched. To reactivate them: swap the `CsvRepository` instances in `app/crud/*.py`
back for the SQLAlchemy `CRUDBase` ones, restore the `db: AsyncSession = Depends(get_db)`
parameter in `app/api/router_factory.py`, and add `DATABASE_URL` back to your `.env`.

## Sorting and filtering

Every list endpoint (`GET /api/v1/<resource>/`) supports:

- `skip`, `limit` — pagination (unchanged)
- `sort_by=<column>&sort_order=asc|desc` — sort by any real column on that entity
- any other query param is treated as an exact-match filter, e.g.
  `GET /api/v1/own-teams/?team_type=YOUTH&sort_by=name&sort_order=desc`

An unknown sort or filter column returns `400` with `INVALID_SORT_FIELD` / `INVALID_FILTER_FIELD`
rather than silently ignoring it.

## Setup

1. Install dependencies:

   ```bash
   uv sync
   ```

2. Generate the mock dataset (or bring your own CSVs matching `app/store/registry.py`):

   ```bash
   uv run python scripts/generate_mock_data.py
   ```

   This (re)writes every file under `data/` with a consistent, FK-valid dataset: 3 clubs each
   with a venue and two own-teams, 6 users, 4 roles with permissions granted, 3 seasons, 4
   competitions, the 10 standard player positions, an approval workflow with stages/approvers/
   sample requests, and audit log entries. Re-run any time to reset to a clean dataset.

3. Run the API:

   ```bash
   uv run python main.py
   # or: uv run uvicorn app.main:app --reload
   ```

4. Open http://localhost:8000/docs for interactive Swagger docs.

## Deploying on Render

This app needs no external database to run — that's the point of the CSV backend for now.
Two things matter for Render specifically:

- **Persistent disk**: Render's default filesystem is ephemeral — every deploy/restart wipes
  it, which would silently reset `data/` back to whatever's checked into the repo. If you want
  writes (create/update/delete) to survive restarts, add a
  [Render persistent disk](https://render.com/docs/disks), mount it (e.g. at `/var/data`), and
  set the `DATA_DIR` environment variable to that mount path.
- **Start command**: `uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## Response envelope

Every endpoint — success or failure — responds with the same shape:

```json
{
  "status": true,
  "message": "Competition created successfully",
  "result": { "...": "resource fields, or an array for list endpoints, or null" },
  "error": null
}
```

On failure, `status` is `false`, `result` is `null`, and `error` carries a stable machine-readable
code plus a human-readable message:

```json
{
  "status": false,
  "message": "Competition not found",
  "result": null,
  "error": { "code": "NOT_FOUND", "message": "Competition not found" }
}
```

The HTTP status code still reflects the outcome (`201` create, `200` read/update/delete, `404`
not found, `400` invalid reference / invalid sort or filter field, `409` conflict/unique-constraint
violation, `422` validation error, `500` unexpected error) — the envelope is consistent, but
callers should still branch on the HTTP status first.

Defined in [app/schemas/common.py](app/schemas/common.py) (`APIResponse[T]`, `ErrorDetail`) and
[app/core/errors.py](app/core/errors.py) (error codes, `AppError`). Wired centrally in
[app/api/router_factory.py](app/api/router_factory.py) (every resource route) and
[app/main.py](app/main.py) (global exception handlers for `AppError`, HTTP errors, validation
errors, and any unhandled exception) — so no per-resource endpoint code has to build the
envelope itself.

## Notes

- `users.password_hash` is populated from a `password` field on `UserCreate`/`UserUpdate`,
  hashed with PBKDF2-SHA256 in `app/core/security.py`. There's no login endpoint yet, so
  nothing currently verifies against it.
- IDs are UUIDs generated in-app (`uuid.uuid4()`), stored as text in the CSV.
- `postman/Football_Intelligence_App.postman_collection.json` — a ready-to-import Postman
  collection covering all 18 resources (list/create/get/update/delete), ordered so foreign-key
  dependencies resolve when run top-to-bottom via Collection Runner, with 171 saved example
  responses (Success, Validation Error, Conflict, Not Found as applicable) and test scripts
  that assert the envelope shape. Captured live against the CSV backend with the mock dataset
  pre-loaded. A collection-level pre-request script generates a random `run_suffix` variable
  once per run, which several Create bodies embed into their unique fields (role code, user
  email, season name, player position code, system module code, permission action code) —
  so the collection can be run repeatedly against the same persistent dataset without ever
  hitting a `409` conflict from its own past runs or from the seed data.
