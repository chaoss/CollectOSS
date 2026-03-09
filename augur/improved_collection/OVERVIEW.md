# Augur Improved Collection Scheduler — High-Level Overview

## Why This Project Exists

Augur currently uses Celery (with RabbitMQ broker + Redis backend) to schedule and execute repository data collection. Celery has proven unreliable in practice: tasks can silently stall, error states are opaque, debugging requires cross-referencing Redis, RabbitMQ, and Celery Beat state, and horizontal scaling is difficult to reason about. The goal of this project is to replace Celery's orchestration layer with a purpose-built scheduler that is:

- **Transparent**: all state lives in Postgres, queryable at any time
- **Debuggable**: every state transition is recorded with timestamps and optional stacktraces
- **Scalable**: consumers are stateless and horizontally scalable
- **Recoverable**: stuck or failed work is automatically detected and retried

---

## Architecture Overview

The new system has four major components that work together:

```
┌─────────────────────────────────────────────────────┐
│                   Postgres Database                  │
│  workflows / workflow_tasks / workflow_dependencies  │
│  repo_collections / task_runs / repo_collection_settings │
└───────────────┬──────────────────────────────────────┘
                │ read/write
       ┌────────▼────────┐
       │   Cron Job /    │  Runs periodically
       │   Scheduler     │  (replaces celery beat)
       └────────┬────────┘
                │ publish CloudEvents
       ┌────────▼────────────────────────────────┐
       │            RabbitMQ Exchanges            │
       │  core.exchange / secondary.exchange /    │
       │  facade.exchange                         │
       └────────┬────────────────────────────────┘
                │ consume
       ┌────────▼────────────────────────────────┐
       │   Worker Consumers (N replicas each)     │
       │   core workers / secondary workers /     │
       │   facade workers                         │
       └─────────────────────────────────────────┘
```

---

## Component 1: DAG-Based Workflow (in Postgres)

**Purpose:** Define what tasks make up a collection run and in what order they must execute.

**Key tables** (`augur_operations` schema, migration `39`):
- `workflows` — a named workflow template
- `workflow_tasks` — tasks belonging to a workflow, each with a `task_type` (core / secondary / facade) and `task_name`
- `workflow_dependencies` — edges in the DAG: which tasks must complete before another can start

**Default workflow** (migration `40`): A starter DAG is seeded at migration time via `insert_workflow_dag()` in `create_workflow.py`.

**Design rule:** The DAG must be acyclic (validated on insert). Tasks have no implicit ordering outside declared dependencies.

**Planned real workflow tasks** (to replace current Celery task chains):
- `repo_info` (core) — no dependencies; collects basic repo metadata
- `issues` (secondary) — depends on `repo_info`
- `pull_requests` (secondary) — depends on `repo_info`
- `commits` (facade) — depends on `repo_info` and `pull_requests`
- (others TBD as implementation proceeds)

**Key file:** `create_workflow.py`

---

## Component 2: Collection Run Tracking (in Postgres)

**Purpose:** Track the lifecycle of a single collection run for a single repo.

**Key tables:**
- `repo_collections` — one row per (repo, workflow) collection attempt; tracks `collection_type` (full/incremental), `origin` (automation/manual), and `state` (Collecting / Complete / Failed)
- `task_runs` — one row per workflow task per collection; state machine: `Pending → Queued → Collecting → Complete / Failed`
- `repo_collection_settings` — per-repo overrides, e.g. `force_full_collection`

**State machine for task_runs:**
```
Pending → Queued → Collecting → Complete
                              → Failed
```

**Key domain class:** `AugurCollection` in `collection.py`

Notable methods:
- `create_new_collection_from_most_recent_workflow()` — bootstraps a collection run with all tasks set to Pending
- `get_running_collections()` — returns active collections with their task states
- `find_repos_needing_initial_collection()` — repos never successfully collected
- `find_failed_collections()` — failed collections ready for retry
- `find_repos_needing_recollection()` — repos whose data is stale
- `retry_failed_collection()` — resets failed tasks to Pending so the scheduler re-queues them

---

## Component 3: Cron Job / Scheduler

**Purpose:** Periodically drive the collection lifecycle. This is the replacement for Celery Beat + `augur_collection_monitor`.

**Runs on a timer** (configurable interval). On each tick it executes `schedule_collection()` from `scheduler.py`, which calls:

1. **`trueup_collection_states()`** — defensive cleanup: marks any collection/task that has been `Collecting` for too long back to `Failed` so they can be retried. Guards against workers that crash without updating state.

2. **`start_collection_on_new_repos()`** — finds repos that have never been collected (`find_repos_needing_initial_collection()`), creates a new `repo_collection` record for each, sets all tasks to `Pending`.

3. **`retry_collection_on_failed_repos()`** — finds failed collections past the retry interval, resets their tasks to `Pending`.

4. **`start_recollection_on_collected_repos()`** — finds repos whose last successful collection is older than the configured recollection interval; creates a new collection run for each.

5. **`queue_tasks_for_running_collections()`** — the core dispatch loop: for each active collection, finds tasks whose dependencies are all `Complete` and whose own state is `Pending`, transitions them to `Queued`, and publishes a CloudEvent to the appropriate RabbitMQ exchange.

**What replaces what:**
| Old (Celery) | New |
|---|---|
| `celery beat` + `augur_collection_monitor` periodic task | Cron job running `schedule_collection()` |
| `CollectionRequest` + `AugurTaskRoutine` | `AugurCollection` domain class |
| `core_status` / `secondary_status` columns on `CollectionStatus` | `task_runs` table with state machine |
| Celery task chains for dependency ordering | DAG dependency resolution in scheduler |

**Key file:** `scheduler.py`

---

## Component 4: RabbitMQ Consumers (Workers)

**Purpose:** Consume task events from RabbitMQ queues and execute the actual data collection logic. Replaces Celery workers.

**Exchanges/queues** (set up by `AugurCollection.setup_collection_topology()`):
- `core.exchange` → `core.queue` — for tasks of type `core`
- `secondary.exchange` → `secondary.queue` — for tasks of type `secondary`
- `facade.exchange` → `facade.queue` — for tasks of type `facade`

**Message format:** CloudEvents (structured JSON) published via `rabbit_client.py`. Each event carries the `task_run_id` and `repo_collection_id` so consumers can look up context.

**Consumer lifecycle:**
1. Receive event from queue
2. Call `update_task_to_collecting()` on the `AugurCollection` domain object
3. Execute collection logic (GitHub API calls, git operations, etc.)
4. On success: call `update_task_to_complete()`
5. On failure: call `update_task_to_failed()` with stacktrace

**Scaling:** Multiple consumer processes can run against the same queue. RabbitMQ distributes messages across them. This replaces `core_worker_count` / `secondary_worker_count` / `facade_worker_count` Celery config.

**Key files:**
- `rabbit_client.py` — RabbitMQ abstraction (publish + consume)
- `collection.py` — state update methods workers call

---

## Current State of the Codebase

### Done (in `augur/improved_collection/`)
- [x] Database schema designed and in Alembic migrations (migration `39`)
- [x] Default DAG seeded at migration time (migration `40`)
- [x] `models.py` — shared enums
- [x] `create_workflow.py` — DAG validation + insertion
- [x] `collection.py` — `AugurCollection` domain class (state machine, query methods, RabbitMQ publishing)
- [x] `rabbit_client.py` — RabbitMQ abstraction with CloudEvents
- [x] `scheduler.py` — orchestration functions

### Not Yet Done / Integration Work Remaining
- [ ] Define real workflow task names that map to actual collection functions (the default DAG has placeholder `task_1`, `task_2`)
- [ ] Write RabbitMQ consumer entry points that execute actual collection logic (issues, PRs, commits, etc.) and call the state update methods
- [ ] Implement the cron job runner (a simple loop or OS cron that calls `schedule_collection()`)
- [ ] Replace / deprecate the old `CollectionStatus` table and Celery-based `augur_collection_monitor` usage
- [ ] Integrate consumer processes into the Augur CLI startup (`augur/application/cli/collection.py`)
- [ ] Migrate existing collection task logic from `augur/tasks/` into the new consumer handlers
- [ ] Handle `refresh_materialized_views`, contributor processing, and other non-repo-collection periodic tasks
- [ ] Testing: unit tests for state transitions, integration tests for scheduler + consumer interaction

---

## Key Existing Files to Understand / Migrate From

| File | Role | Status |
|---|---|---|
| `augur/tasks/init/celery_app.py` | Celery app config, queue definitions, periodic task setup | Replace |
| `augur/tasks/start_tasks.py` | `augur_collection_monitor` — main scheduler loop | Replace with `scheduler.py` |
| `augur/tasks/util/collection_util.py` | `CollectionRequest`, `AugurTaskRoutine`, task success/fail handlers | Replace with `AugurCollection` |
| `augur/application/cli/collection.py` | CLI for starting/stopping workers | Modify to start new consumers instead |
| `augur/application/db/models/augur_operations.py` | `CollectionStatus` model | Deprecate once new schema covers all cases |
| `augur/tasks/git/facade_tasks.py` | Git clone + analysis tasks | Migrate to new facade consumer |
| `augur/tasks/db/refresh_materialized_views.py` | DB view refresh periodic task | Keep as separate cron or integrate |

---

## Planned Implementation Sub-Tasks

Each of these is a focused, independently executable plan. Tackle them in roughly this order:

1. **Define real workflow DAG** — Replace placeholder task names with real ones (`repo_info`, `issues`, `pull_requests`, `commits`, etc.) and update migration `40`.

2. **Implement cron job runner** — A simple Python process (or integration with APScheduler) that calls `schedule_collection()` on a timer. Wire into `augur/application/cli/collection.py`.

3. **Implement core consumer** — Worker process that consumes from `core.queue`, executes `repo_info` collection logic, updates state.

4. **Implement secondary consumer** — Worker process for `issues` and `pull_requests` tasks.

5. **Implement facade consumer** — Worker process for git clone + commit analysis.

6. **CLI integration** — Update `augur collection start` command to launch the new cron + consumer processes instead of Celery workers.

7. **Remove old Celery infrastructure** — Deprecate `CollectionStatus`, remove Celery beat, remove `celery_app.py` worker configuration once all tasks are migrated.

8. **Materialized view refresh + other periodic tasks** — Decide whether these become separate cron jobs or are incorporated into the scheduler.
