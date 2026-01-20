-- ============================
-- Task Management Schema
-- ============================

-- 1. Workflows
CREATE TABLE workflows (
    id SERIAL PRIMARY KEY,
    created_on TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 2. Workflow Tasks
CREATE TABLE workflow_tasks (
    id SERIAL PRIMARY KEY,
    workflow_id INT NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    task_name TEXT NOT NULL,
    UNIQUE(workflow_id, task_name)
);

-- 3. Workflow Dependencies (Dependency Graph)
-- Each row means: workflow_task_id depends on depends_on_workflow_task_id
CREATE TABLE workflow_dependencies (
    workflow_task_id INT NOT NULL REFERENCES workflow_tasks(id) ON DELETE CASCADE,
    depends_on_workflow_task_id INT NOT NULL REFERENCES workflow_tasks(id) ON DELETE CASCADE,
    PRIMARY KEY (workflow_task_id, depends_on_workflow_task_id),
    CHECK (workflow_task_id <> depends_on_workflow_task_id)
);

-- 4. Collection Type Enum
CREATE TYPE collection_type AS ENUM (
    'full',        -- Full collection for new repos or forced full recollection
    'incremental'  -- Incremental collection that only collects new data
);

-- 5. Collection State Enum
CREATE TYPE collection_state AS ENUM (
    'Collecting',  -- Collection in progress, some tasks running
    'Failed',      -- Collection has failed tasks and no runnable tasks remain
    'Complete'     -- All tasks in collection completed successfully
);

-- 6. Repo Collections
CREATE TABLE repo_collections (
    id SERIAL PRIMARY KEY,
    repo_id TEXT NOT NULL,
    workflow_id INT NOT NULL REFERENCES workflows(id),
    origin TEXT NOT NULL CHECK (origin IN ('automation', 'manual')),
    collection_type collection_type NOT NULL DEFAULT 'full',
    is_new_repo BOOLEAN NOT NULL DEFAULT FALSE,
    started_on TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_on TIMESTAMP,
    state collection_state NOT NULL DEFAULT 'Collecting'
);

-- 7. Task Run State Enum
CREATE TYPE task_run_state AS ENUM (
    'Pending',
    'Queued',
    'Collecting',
    'Failed',
    'Complete'
);

-- 8. Task Runs
CREATE TABLE task_runs (
    id SERIAL PRIMARY KEY,
    collection_record_id INT NOT NULL REFERENCES repo_collections(id) ON DELETE CASCADE,
    workflow_task_id INT NOT NULL REFERENCES workflow_tasks(id),
    restarted BOOLEAN NOT NULL DEFAULT FALSE,
    start_date TIMESTAMP,
    state task_run_state NOT NULL DEFAULT 'Pending',
    stacktrace TEXT,

    UNIQUE(collection_record_id, workflow_task_id)
);

-- 9. Repo Collection Settings
CREATE TABLE repo_collection_settings (
    repo_id TEXT PRIMARY KEY,
    force_full_collection BOOLEAN NOT NULL DEFAULT FALSE,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 10. Optional: Task Status Activity (for detailed metrics later)
CREATE TABLE task_status_activity (
    id SERIAL PRIMARY KEY,
    task_run_id INT NOT NULL REFERENCES task_runs(id) ON DELETE CASCADE,
    old_state task_run_state,
    new_state task_run_state NOT NULL,
    changed_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ============================
-- Indexes
-- ============================

CREATE INDEX idx_workflow_tasks_workflow ON workflow_tasks(workflow_id);
CREATE INDEX idx_dependencies_task ON workflow_dependencies(workflow_task_id);
CREATE INDEX idx_dependencies_depends_on ON workflow_dependencies(depends_on_workflow_task_id);

CREATE INDEX idx_repo_collections_repo ON repo_collections(repo_id);
CREATE INDEX idx_repo_collection_settings_force_full ON repo_collection_settings(force_full_collection) WHERE force_full_collection = TRUE;
CREATE INDEX idx_task_runs_collection ON task_runs(collection_record_id);
CREATE INDEX idx_task_runs_state ON task_runs(state);



---- New Repo SQL



-- Recollections: last completed collection older than X days
SELECT rc.repo_id
FROM repo_collections rc
JOIN (
    SELECT repo_id, MAX(completed_on) AS last_completed
    FROM repo_collections
    WHERE completed_on IS NOT NULL
    GROUP BY repo_id
) lc ON rc.repo_id = lc.repo_id AND rc.completed_on = lc.last_completed
WHERE rc.completed_on < NOW() - INTERVAL ':recollection_days DAYS';


-- Failed Collections: any task failed and no runnable tasks remain
-- Parameter: :retry_hours → how long to wait before retrying a failed collection
SELECT rc.id AS collection_id,
       rc.repo_id,
       rc.workflow_id,
       rc.completed_on,
       rc.state
FROM repo_collections rc
JOIN (
    -- Get the last collection for each repo
    SELECT repo_id, MAX(id) AS last_collection_id
    FROM repo_collections
    GROUP BY repo_id
) lc ON rc.id = lc.last_collection_id
WHERE rc.state = 'Failed'
  AND rc.completed_on < NOW() - INTERVAL ':retry_hours HOURS';

