
def get_collection_info_for_running_collections():
    
    get_tasks_for_collection_sql = """
        WITH collecting_collections AS (
            SELECT *
            FROM repo_collections
            WHERE state = 'Collecting'
        )
        SELECT
            rc.id AS collection_id,
            rc.repo_id,
            rc.workflow_id,
            tr.id AS task_run_id,
            tr.workflow_task_id,
            wt.task_name,
            tr.state AS task_run_state,
            tr.start_date,
            -- Array of dependency task ids
            array_agg(wd.depends_on_workflow_task_id) FILTER (WHERE wd.depends_on_workflow_task_id IS NOT NULL) AS depends_on_task_ids,
            -- Array of dependency task run states (join to get states)
            array_agg(dep_tr.state) FILTER (WHERE dep_tr.state IS NOT NULL) AS depends_on_task_states
        FROM collecting_collections rc
        JOIN task_runs tr
            ON tr.collection_record_id = rc.id
        JOIN workflow_tasks wt
            ON wt.id = tr.workflow_task_id
        LEFT JOIN workflow_dependencies wd
            ON wd.workflow_task_id = wt.id
        LEFT JOIN task_runs dep_tr
            ON dep_tr.collection_record_id = rc.id
        AND dep_tr.workflow_task_id = wd.depends_on_workflow_task_id
        GROUP BY rc.id, rc.repo_id, rc.workflow_id, tr.id, tr.workflow_task_id, wt.task_name, tr.state, tr.start_date
        ORDER BY rc.id, tr.workflow_task_id;
    """


def queue_tasks_for_running_collections():
    
    collection_info = get_collection_info_for_running_collections()
    
    


def start_collection_on_new_repos():

    new_repo_sql = """    
    SELECT DISTINCT rc.repo_id
    FROM repo_collections rc
    LEFT JOIN task_runs tr 
        ON tr.collection_record_id = rc.id
    GROUP BY rc.repo_id
    HAVING COUNT(*) = 0
    OR NOT EXISTS (
        SELECT 1
        FROM repo_collections rc2
        JOIN task_runs tr2 ON tr2.collection_record_id = rc2.id
        WHERE rc2.repo_id = rc.repo_id
            AND tr2.state = 'Complete'
   );"""

def retry_collection_on_failed_repos():
    
    failed_sql = """    
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
  """

def start_recollection_on_collected_repos():
    
    recollection_sql = """    
    SELECT rc.repo_id
    FROM repo_collections rc
    JOIN (
        SELECT repo_id, MAX(completed_on) AS last_completed
        FROM repo_collections
        WHERE completed_on IS NOT NULL
        GROUP BY repo_id
    ) lc ON rc.repo_id = lc.repo_id AND rc.completed_on = lc.last_completed
    WHERE rc.completed_on < NOW() - INTERVAL ':recollection_days DAYS';
   );"""
   


def create_new_collection_from_most_recent_workflow(repo_id):
    
    create_new_collection_sql = """
    WITH latest_workflow AS (
        SELECT id AS workflow_id
        FROM workflows
        ORDER BY id DESC
        LIMIT 1
    ),
    new_collection AS (
        INSERT INTO repo_collections (repo_id, workflow_id, origin, state)
        SELECT %s, lw.workflow_id, 'automation', 'Pending'
        FROM latest_workflow lw
        RETURNING id AS collection_id
    )
    INSERT INTO task_runs (collection_record_id, workflow_task_id, state)
    SELECT nc.collection_id, wt.id, 'Pending'
    FROM new_collection nc
    JOIN workflow_tasks wt
    ON wt.workflow_id = (SELECT workflow_id FROM latest_workflow)
    RETURNING collection_record_id, workflow_task_id, state;
    """

def trueup_collection_states():
    """
    Defensive method to ensure no collections are stuck in a collecting state. 
    Generally these states should be updates by the task copleted and failed events
    but in case they are not, this method will update them.
    It marks collection as failed if they have a failed task run and no runnable tasks remain.
    It marks collection as complete if they have a complete task run and no runnable tasks remain.
    """
    
    collection_info = get_collection_info_for_running_collections()

def schedule_collection():
    
    start_collection_on_new_repos()
    
    retry_collection_on_failed_repos()
    
    start_recollection_on_collected_repos()

    trueup_collection_states()

    # run this last so tasks for new collections are queued
    queue_tasks_for_running_collections()



