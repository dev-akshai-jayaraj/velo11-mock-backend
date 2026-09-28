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
  football_intelligence_expanded.dbml   current ERD (source of truth for app/store/registry.py)
  schema.sql       Postgres DDL for the original 18 tables, kept for the future migration
scripts/
  generate_mock_data.py   (re)generates data/*.csv with a consistent, FK-valid mock dataset
main.py            dev entrypoint (uvicorn runner)
```

The source-of-truth ERD is [db/football_intelligence_expanded.dbml](db/football_intelligence_expanded.dbml).
Every table in it gets a full REST resource at `/api/v1/<resource>` with `GET /`, `POST /`,
`GET /{id}`, `PATCH /{id}`, `DELETE /{id}` (audit logs and analytics snapshots are
read/create only, because they are immutable records). 47 resources in total:

| Area | Resources |
|---|---|
| Foundation | home-clubs, venues, own-teams, users, roles, permissions, user-roles, role-permissions, seasons, competitions, player-positions, system-modules, approval-*, audit-logs |
| Squad & opposition | players, team-players, player-availability, opponent-clubs, opponent-teams, competition-seasons, team-competitions |
| Fixtures & matches | fixtures, matches, match-contexts, match-lineups, match-lineup-players, match-events |
| Statistics | player-match-stats, team-match-stats, player-season-stats, team-season-stats |
| Match preparation | scouting-notes, opposition-analyses, tactical-plans, set-piece-plans |
| Team dynamics | team-dynamics-assessments, player-relationships, unit-cohesion |
| Insights | analytics-snapshots, recommendations, reports |
| Data ingestion | data-sources, data-imports |

A **fixture** is the scheduled game. A **match** is its 1:1 result and analysis workspace
(`matches.fixture_id` is unique), so pre-match planning can exist before kickoff.
All lineups, events, stats and plans hang off the match.

### Domain validation (on create)

On top of FK, unique and delete-restrict checks, the schemas enforce these rules
(422 `VALIDATION_ERROR` on violation):

- Enums the ERD spells out: `venue_side` (HOME/AWAY/NEUTRAL), `team_scope` (OWN/OPPONENT),
  `result` (WIN/DRAW/LOSS), set-piece `phase` (ATTACKING/DEFENDING), data source
  `source_type` (MANUAL/CSV/EXCEL/API/SCRAPER).
- `matches.result` is derived from `own_score`/`opponent_score` when both are given (also on
  PATCH), and a contradicting result is rejected.
- A lineup player needs exactly one of `player_id` (own squad) or `opponent_player_name`.
  Opposition players aren't player records, so an `OPPONENT` match event can't carry a `player_id`.
- `player_relationships` needs two different players. A scouting note must reference a
  player, an opponent team or a match.
- Date ordering (`joined_at ≤ left_at`, `start_date ≤ return dates`, `kickoff ≤ finished`).
  Non-negative counts. `shots_on_target ≤ shots`, `passes_completed ≤ passes_attempted`,
  `wins+draws+losses ≤ matches_played`, `processed+failed ≤ received`. Percentages are
  0–100 and recommendation `confidence` is 0–1.

Cross-field rules are checked on create only (and for the match result on PATCH when both
scores are sent), because a partial PATCH doesn't carry the rest of the row.

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
   sample requests, and audit log entries. It also seeds the football domain: 4 opponent clubs and
   teams, an 11-player squad per first team, and for the Manchester Reds first team 3 played matches
   plus 1 upcoming one. The played matches have lineups, events and player/team stats, and the season
   stats are aggregated from those match stats. The upcoming match has scouting, opposition analysis
   and tactical and set-piece plans. There's also sample availability, team-dynamics, analytics,
   recommendation, report and data-import rows. Re-run any time to reset to a clean dataset.

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
  collection covering all 47 resources: 254 requests, 466 saved example responses (Success,
  Validation Error, Conflict, Not Found and rule-specific errors), and a status-code test on
  every request. Examples were captured live against the CSV backend with the mock dataset loaded.
  - **Run order:** a top-to-bottom run (Collection Runner / newman) satisfies every foreign key.
    Each Create saves its id to a collection variable, and nothing is deleted until the final
    **Cleanup** folder, which removes everything the run created, children first. A run leaves
    the dataset exactly as it found it.
  - **Validation Rules** folder: negative tests for the domain rules above. It changes no data.
  - A collection-level pre-request script sets a random `run_suffix` once per run, embedded in
    unique fields (role code, user email, season name, player display name, …), so the
    collection can be re-run against the same persistent dataset without `409` conflicts.
