-- ============================
-- Task Management Schema
-- ============================

-- 1. Workflows
CREATE TABLE augur_operations.workflows (
    id SERIAL PRIMARY KEY,
    created_on TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 2. Task Type Enum
CREATE TYPE augur_operations.task_type AS ENUM (
    'core',
    'secondary',
    'facade'
);

-- 3. Workflow Tasks
CREATE TABLE augur_operations.workflow_tasks (
    id SERIAL PRIMARY KEY,
    workflow_id INT NOT NULL REFERENCES augur_operations.workflows(id) ON DELETE CASCADE,
    task_name TEXT NOT NULL,
    task_type augur_operations.task_type NOT NULL,
    UNIQUE(workflow_id, task_name)
);

-- 4. Workflow Dependencies (Dependency Graph)
-- Each row means: workflow_task_id depends on depends_on_workflow_task_id
CREATE TABLE augur_operations.workflow_dependencies (
    workflow_task_id INT NOT NULL REFERENCES augur_operations.workflow_tasks(id) ON DELETE CASCADE,
    depends_on_workflow_task_id INT NOT NULL REFERENCES augur_operations.workflow_tasks(id) ON DELETE CASCADE,
    PRIMARY KEY (workflow_task_id, depends_on_workflow_task_id),
    CHECK (workflow_task_id <> depends_on_workflow_task_id)
);

-- 5. Origin Type Enum
CREATE TYPE augur_operations.origin_type AS ENUM (
    'automation',
    'manual'
);

-- 6. Collection Type Enum
CREATE TYPE augur_operations.collection_type AS ENUM (
    'full',        -- Full collection for new repos or forced full recollection
    'incremental'  -- Incremental collection that only collects new data
);

-- 7. Collection State Enum
CREATE TYPE augur_operations.collection_state AS ENUM (
    'Collecting',  -- Collection in progress, some tasks running
    'Failed',      -- Collection has failed tasks and no runnable tasks remain
    'Complete'     -- All tasks in collection completed successfully
);

-- 8. Repo Collections
CREATE TABLE augur_operations.repo_collections (
    id SERIAL PRIMARY KEY,
    repo_id TEXT NOT NULL,
    workflow_id INT NOT NULL REFERENCES augur_operations.workflows(id),
    origin augur_operations.origin_type NOT NULL,
    collection_type augur_operations.collection_type NOT NULL DEFAULT 'full',
    is_new_repo BOOLEAN NOT NULL DEFAULT FALSE,
    started_on TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_on TIMESTAMP,
    state augur_operations.collection_state NOT NULL DEFAULT 'Collecting'
);

-- 9. Task Run State Enum
CREATE TYPE augur_operations.task_run_state AS ENUM (
    'Pending',
    'Queued',
    'Collecting',
    'Failed',
    'Complete'
);

-- 10. Task Runs
CREATE TABLE augur_operations.task_runs (
    id SERIAL PRIMARY KEY,
    collection_record_id INT NOT NULL REFERENCES augur_operations.repo_collections(id) ON DELETE CASCADE,
    workflow_task_id INT NOT NULL REFERENCES augur_operations.workflow_tasks(id),
    restarted BOOLEAN NOT NULL DEFAULT FALSE,
    start_date TIMESTAMP,
    completed_date TIMESTAMP,
    state augur_operations.task_run_state NOT NULL DEFAULT 'Pending',
    stacktrace TEXT,

    UNIQUE(collection_record_id, workflow_task_id)
);

-- 11. Repo Collection Settings
CREATE TABLE augur_operations.repo_collection_settings (
    repo_id TEXT PRIMARY KEY,
    force_full_collection BOOLEAN NOT NULL DEFAULT FALSE,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 12. Optional: Task Status Activity (for detailed metrics later)
CREATE TABLE augur_operations.task_status_activity (
    id SERIAL PRIMARY KEY,
    task_run_id INT NOT NULL REFERENCES augur_operations.task_runs(id) ON DELETE CASCADE,
    old_state augur_operations.task_run_state,
    new_state augur_operations.task_run_state NOT NULL,
    changed_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ============================
-- Indexes
-- ============================

CREATE INDEX idx_workflow_tasks_workflow ON augur_operations.workflow_tasks(workflow_id);
CREATE INDEX idx_dependencies_task ON augur_operations.workflow_dependencies(workflow_task_id);
CREATE INDEX idx_dependencies_depends_on ON augur_operations.workflow_dependencies(depends_on_workflow_task_id);

CREATE INDEX idx_repo_collections_repo ON augur_operations.repo_collections(repo_id);
CREATE INDEX idx_repo_collection_settings_force_full ON augur_operations.repo_collection_settings(force_full_collection) WHERE force_full_collection = TRUE;
CREATE INDEX idx_task_runs_collection ON augur_operations.task_runs(collection_record_id);
CREATE INDEX idx_task_runs_state ON augur_operations.task_runs(state);



