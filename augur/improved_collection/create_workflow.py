import json
import logging
from typing import Dict, List, Optional, Any
from sqlalchemy import text
from augur.application.db.session import DatabaseSession
from augur.application.db.engine import DatabaseEngine

logger = logging.getLogger(__name__)


def _has_cycle(tasks: List[Dict[str, Any]]) -> bool:
    """
    Check if the task dependency graph has cycles using DFS.
    
    Args:
        tasks: List of task dictionaries with 'task_name' and 'depends_on' fields
    
    Returns:
        True if a cycle is detected, False otherwise
    """
    graph = {task["task_name"]: task.get("depends_on", []) for task in tasks}
    
    visited = set()
    rec_stack = set()
    
    def dfs(node: str) -> bool:
        visited.add(node)
        rec_stack.add(node)
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor):
                    return True
            elif neighbor in rec_stack:
                return True
        
        rec_stack.remove(node)
        return False
    
    for task_name in graph:
        if task_name not in visited:
            if dfs(task_name):
                return True
    
    return False


def insert_workflow_dag(dag_json: Dict[str, Any], session: Optional[DatabaseSession] = None) -> Optional[int]:
    """
    Insert a workflow DAG into the database.
    
    Args:
        dag_json: A dictionary representing the workflow DAG with the following structure:
            {
                "tasks": [
                    {
                        "task_name": "task1",
                        "task_type": "core",  # one of: 'core', 'secondary', 'facade'
                        "depends_on": ["task2", "task3"]  # optional list of task names this task depends on
                    },
                    ...
                ]
            }
        session: Optional DatabaseSession. If not provided, a new session will be created.
    
    Returns:
        The workflow_id of the created workflow, or None if insertion failed.
    
    Example:
        dag = {
            "tasks": [
                {"task_name": "repo_info", "task_type": "core", "depends_on": []},
                {"task_name": "issues", "task_type": "secondary", "depends_on": ["repo_info"]},
                {"task_name": "pull_requests", "task_type": "secondary", "depends_on": ["repo_info"]},
                {"task_name": "commits", "task_type": "facade", "depends_on": ["repo_info", "pull_requests"]}
            ]
        }
        workflow_id = insert_workflow_dag(dag)
    """
    
    if not dag_json or "tasks" not in dag_json:
        logger.error("Invalid DAG JSON: must contain 'tasks' key")
        return None
    
    tasks = dag_json.get("tasks", [])
    if not tasks:
        logger.error("DAG must contain at least one task")
        return None
    
    # Validate task types
    valid_task_types = {'core', 'secondary', 'facade'}
    for task in tasks:
        if "task_name" not in task or "task_type" not in task:
            logger.error(f"Each task must have 'task_name' and 'task_type': {task}")
            return None
        if task["task_type"] not in valid_task_types:
            logger.error(f"Invalid task_type '{task['task_type']}'. Must be one of: {valid_task_types}")
            return None
    
    # Validate dependencies reference existing tasks
    task_names = {task["task_name"] for task in tasks}
    for task in tasks:
        depends_on = task.get("depends_on", [])
        for dep in depends_on:
            if dep not in task_names:
                logger.error(f"Task '{task['task_name']}' depends on non-existent task '{dep}'")
                return None
    
    # Check for self-dependencies
    for task in tasks:
        depends_on = task.get("depends_on", [])
        if task["task_name"] in depends_on:
            logger.error(f"Task '{task['task_name']}' cannot depend on itself")
            return None
    
    # Check for cycles in the dependency graph
    if _has_cycle(tasks):
        logger.error("Cycle detected in task dependencies. The workflow must be a DAG (Directed Acyclic Graph)")
        return None
    
    # Create session if not provided
    session_created = False
    if session is None:
        session = DatabaseSession(logger)
        session_created = True
    
    try:
        # 1. Insert workflow
        workflow_result = session.execute(
            text("INSERT INTO workflows DEFAULT VALUES RETURNING id")
        )
        workflow_id = workflow_result.fetchone()[0]
        logger.info(f"Created workflow with id: {workflow_id}")
        
        # 2. Insert workflow tasks
        workflow_task_id_map = {}  # Maps task_name -> workflow_task_id
        
        for task in tasks:
            task_name = task["task_name"]
            task_type = task["task_type"]
            
            task_result = session.execute(
                text("""
                    INSERT INTO workflow_tasks (workflow_id, task_name, task_type)
                    VALUES (:workflow_id, :task_name, :task_type)
                    RETURNING id
                """),
                {
                    "workflow_id": workflow_id,
                    "task_name": task_name,
                    "task_type": task_type
                }
            )
            task_id = task_result.fetchone()[0]
            workflow_task_id_map[task_name] = task_id
            logger.debug(f"Created workflow_task '{task_name}' with id: {task_id}")
        
        # 3. Insert workflow dependencies
        dependency_count = 0
        for task in tasks:
            task_name = task["task_name"]
            depends_on = task.get("depends_on", [])
            
            for dependency_name in depends_on:
                session.execute(
                    text("""
                        INSERT INTO workflow_dependencies (workflow_task_id, depends_on_workflow_task_id)
                        VALUES (:workflow_task_id, :depends_on_workflow_task_id)
                    """),
                    {
                        "workflow_task_id": workflow_task_id_map[task_name],
                        "depends_on_workflow_task_id": workflow_task_id_map[dependency_name]
                    }
                )
                dependency_count += 1
                logger.debug(f"Created dependency: '{task_name}' depends on '{dependency_name}'")
        
        session.commit()
        logger.info(f"Successfully created workflow {workflow_id} with {len(tasks)} tasks and {dependency_count} dependencies")
        
        return workflow_id
        
    except Exception as e:
        logger.error(f"Error inserting workflow DAG: {e}")
        session.rollback()
        return None
        
    finally:
        if session_created:
            session.close()


def insert_workflow_dag_from_json_string(dag_json_string: str, session: Optional[DatabaseSession] = None) -> Optional[int]:
    """
    Insert a workflow DAG from a JSON string.
    
    Args:
        dag_json_string: A JSON string representing the workflow DAG
        session: Optional DatabaseSession. If not provided, a new session will be created.
    
    Returns:
        The workflow_id of the created workflow, or None if insertion failed.
    """
    try:
        dag_json = json.loads(dag_json_string)
        return insert_workflow_dag(dag_json, session)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON string: {e}")
        return None


def get_workflow_dag(workflow_id: int, session: Optional[DatabaseSession]) -> Optional[Dict[str, Any]]:
    """
    Retrieve a workflow DAG from the database.
    
    Args:
        workflow_id: The ID of the workflow to retrieve
        session: Optional DatabaseSession. If not provided, a new session will be created.
    
    Returns:
        A dictionary representing the workflow DAG, or None if not found.
    """
    
    try:
        # Get all tasks for this workflow
        tasks_result = session.execute(
            text("""
                SELECT id, task_name, task_type
                FROM workflow_tasks
                WHERE workflow_id = :workflow_id
            """),
            {"workflow_id": workflow_id}
        )
        
        tasks_rows = tasks_result.fetchall()
        if not tasks_rows:
            logger.warning(f"No tasks found for workflow_id: {workflow_id}")
            return None
        
        # Build task_id -> task_name mapping
        task_id_to_name = {row[0]: row[1] for row in tasks_rows}
        
        # Get all dependencies
        deps_result = session.execute(
            text("""
                SELECT workflow_task_id, depends_on_workflow_task_id
                FROM workflow_dependencies
                WHERE workflow_task_id IN :task_ids
            """),
            {"task_ids": tuple(task_id_to_name.keys())}
        )
        
        # Build dependency map: task_id -> [depends_on_task_ids]
        dependency_map = {}
        for row in deps_result.fetchall():
            task_id = row[0]
            depends_on_id = row[1]
            if task_id not in dependency_map:
                dependency_map[task_id] = []
            dependency_map[task_id].append(depends_on_id)
        
        # Build the DAG structure
        tasks = []
        for task_id, task_name, task_type in tasks_rows:
            depends_on_ids = dependency_map.get(task_id, [])
            depends_on_names = [task_id_to_name[dep_id] for dep_id in depends_on_ids]
            
            tasks.append({
                "task_name": task_name,
                "task_type": task_type,
                "depends_on": depends_on_names
            })
        
        return {
            "workflow_id": workflow_id,
            "tasks": tasks
        }
        
    except Exception as e:
        logger.error(f"Error retrieving workflow DAG: {e}")
        return None


def main():
    """
    Main method for testing workflow creation and retrieval.
    
    Prompts user for database connection string or uses default connection.
    """
    import sys
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Prompt for connection string
    print("\n" + "="*60)
    print("Workflow Creation Test")
    print("="*60)
    print("\nEnter database connection string")
    print("Format: postgresql://user:password@host:port/database")
    print("Or press Enter to use default Augur connection")
    print("-"*60)
    
    connection_string = input("Connection string: ").strip()
    
    if connection_string:
        try:
            engine = DatabaseEngine(connection_string=connection_string)
            print(f"✓ Using provided connection string")
        except Exception as e:
            print(f"✗ Error with connection string: {e}")
            print("Falling back to default connection")
            engine = DatabaseEngine()
    else:
        print("✓ Using default database connection")
        engine = DatabaseEngine()
    
    session = DatabaseSession(logger, engine)
    
    try:
        # Create a sample workflow DAG
        sample_dag = {
            "tasks": [
                {
                    "task_name": "repo_info",
                    "task_type": "core",
                    "depends_on": []
                },
                {
                    "task_name": "issues",
                    "task_type": "secondary",
                    "depends_on": ["repo_info"]
                }
            ]
        }
        
        print("\n" + "="*60)
        print("Testing Workflow Creation")
        print("="*60)
        print("\nSample DAG:")
        print(json.dumps(sample_dag, indent=2))
        
        # Insert the workflow
        workflow_id = insert_workflow_dag(sample_dag, session)
        
        if workflow_id:
            print(f"\n✓ Successfully created workflow with ID: {workflow_id}")
            
            # Retrieve the workflow
            print("\n" + "="*60)
            print("Testing Workflow Retrieval")
            print("="*60)
            
            retrieved_dag = get_workflow_dag(workflow_id, session)
            
            if retrieved_dag:
                print(f"\n✓ Successfully retrieved workflow {workflow_id}:")
                print(json.dumps(retrieved_dag, indent=2))
            else:
                print(f"\n✗ Failed to retrieve workflow {workflow_id}")
        else:
            print("\n✗ Failed to create workflow")
            
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        print(f"\n✗ Error: {e}")
    finally:
        session.close()
        print("\n" + "="*60)


if __name__ == "__main__":
    main()
