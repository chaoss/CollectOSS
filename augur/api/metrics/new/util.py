from sqlalchemy import text
from functools import wraps
from flask import request, jsonify

from ...server import app


class UserGroupRequest:
    user_id: int
    name: int


def get_repo_ids(conn, repo_id, user_group_request):

    repo_ids = []
    if repo_id:
        repo_ids.append(repo_id)
    else:
        repo_ids.append(get_repo_ids_by_user_group(conn, user_group_request.name, user_group_request.user_id))

    return repo_ids


def get_repo_ids_by_user_group(conn, name: str, user_id: int) -> list:
    """
    Returns the repo_ids based on the provided user group name and user_id.
    This function is reusable and uses parameterized queries to prevent SQL injection.

    :param name: The name of the user group.
    :param user_id: The user ID to filter by.
    :param conn: The database connection.
    :return: List of repo_ids.
    """
    query = """
    SELECT user_repos.repo_id
    FROM user_repos
    JOIN user_groups ON user_repos.group_id = user_groups.group_id
    WHERE user_groups.name = :name
    AND user_groups.user_id = :user_id
    """
    # Execute the query with parameters
    result = conn.execute(text(query), {'name': name, 'user_id': user_id})
    
    # Fetch all the rows and return the repo_ids as a list
    repo_ids = [row['repo_id'] for row in result.fetchall()]
    return repo_ids



def repo_metrics_route(route_path):
    def decorator(func):
        @wraps(func)
        def wrapper(repo_id, *args, **kwargs):
            # Extract query parameters from the request
            period = request.args.get('period', default='day')
            begin_date = request.args.get('begin_date')
            end_date = request.args.get('end_date')

            try:
                # Call the original function with the parameters
                data = func(repo_id=repo_id, period=period, begin_date=begin_date, end_date=end_date, *args, **kwargs)
                # NOTE: Probably remove data transformation to allow for more use cases
                return data.to_json(orient='records')
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        # Register the route inside the decorator itself
        wrapper.route_path = route_path
        wrapper.methods = ['GET']

        # Use Flask's routing system to register the route automatically
        app.route(wrapper.route_path, methods=wrapper.methods)(wrapper)
        return wrapper
    return decorator


def group_metrics_route(route_path):
    def decorator(func):
        @wraps(func)
        def wrapper(group_name, *args, **kwargs):
            # Extract query parameters from the request
            user_id = request.args.get('user_id')
            period = request.args.get('period', default='day')
            begin_date = request.args.get('begin_date')
            end_date = request.args.get('end_date')

            # Create a UserGroupRequest object and populate it with parameters
            user_group_request = UserGroupRequest()
            user_group_request.name = group_name
            user_group_request.user_id = user_id

            try:
                # Call the original function with the populated parameters
                data = func(user_group_request=user_group_request, period=period, begin_date=begin_date, end_date=end_date, *args, **kwargs)
                # NOTE: Probably remove data transformation to allow for more use cases
                return data.to_json(orient='records')
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        # Register the route inside the decorator itself
        wrapper.route_path = route_path
        wrapper.methods = ['GET']

        # Use Flask's routing system to register the route automatically
        app.route(wrapper.route_path, methods=wrapper.methods)(wrapper)
        return wrapper
    return decorator