"""
Defines the api routes for the augur views
"""
import logging
import math
from flask import render_template, request, redirect, url_for, session, flash, jsonify
from .utils import getSetting, render_module, renderRepos, render_message
from flask_login import login_user, logout_user, current_user, login_required

from augur.application.db.models import User, Repo, ClientApplication
from .server import LoginException
from augur.application.util import *
from augur.application.db.lib import get_value
from ..server import app, db_session
from .init import reports
from datetime import datetime

logger = logging.getLogger(__name__)


# ROUTES -----------------------------------------------------------------------

""" ----------------------------------------------------------------
root:
    This route returns a redirect to the application root, appended
    by the provided path, if any.
"""
@app.route('/root/')
@app.route('/root/<path:path>')
def root(path=""):
    return redirect(getSetting("approot") + path)

""" ----------------------------------------------------------------
logo:
    this route returns a redirect to the application logo associated
    with the provided brand, otherwise the inverted Augur logo if no
    brand is provided.
"""
@app.route('/logo/')
@app.route('/logo/<string:brand>')
def logo(brand=None):
    if brand is None:
        return redirect(url_for('static', filename='img/augur_logo.png'))
    if "augur" in brand:
        return logo(None)
    if "chaoss" in brand:
        return redirect(url_for('static', filename='img/Chaoss_Logo_white.png'))
    return ""

""" ----------------------------------------------------------------
default:
table:
    This route returns the default view of the application, which
    is currently defined as the repository table view
"""
@app.route('/')
@app.route('/repos/views/table')
def repo_table_view():
    query = request.args.get('q')
    try:
        page = int(request.args.get('p') or 0)
    except (ValueError, TypeError):
        page = 1

    sorting = request.args.get('s')
    rev = request.args.get('r')

    if rev is not None:
        if rev == "False":
            rev = False
        elif rev == "True":
            rev = True
    
    direction = "DESC" if rev else "ASC"

    pagination_offset = get_value("frontend", "pagination_offset")
    
    if current_user.is_authenticated:
        data = current_user.get_repos(page = page, sort = sorting, direction = direction, search=query)[0]
        repos_count = (current_user.get_repo_count(search = query)[0] or 0)
    else:
        data = get_all_repos(page = page, sort = sorting, direction = direction, search=query)[0]
        repos_count = (get_all_repos_count(search = query)[0] or 0)

    page_count = math.ceil(repos_count / pagination_offset) - 1
    
    if not data:
        data = None


    return render_module("repos-table", title="Repos", repos=data, query_key=query, activePage=page, pages=page_count, offset=pagination_offset, PS="repo_table_view", reverse = rev, sorting = sorting)

""" ----------------------------------------------------------------
card:
    This route returns the repository card view
"""
@app.route('/repos/views/card')
def repo_card_view():
    query = request.args.get('q')
    if current_user.is_authenticated:
        count = current_user.get_repo_count()[0]
        data = current_user.get_repos(page_size = count)[0]
    else:
        count = get_all_repos_count()[0]
        data = get_all_repos(page_size=count)[0]

    return renderRepos("card", query, data, filter = True)

""" ----------------------------------------------------------------
status:
    This route returns the status view, which displays information
    about the current status of collection in the backend
"""
@app.route('/collection/status')
def status_view():
    return render_module("status", title="Status")

""" ----------------------------------------------------------------
login:
    Under development
"""
@app.route('/account/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            remember = request.form.get('remember') is not None
            password = request.form.get('password')
            register = request.form.get('register')

            if username is None:
                raise LoginException("A login issue occurred")

            user = User.get_user(db_session, username)

            if not user and register is None:
                raise LoginException("Invalid login credentials")
            
            # register a user
            if register is not None:
                if user:
                    raise LoginException("User already exists")
                
                email = request.form.get('email')
                first_name = request.form.get('first_name')
                last_name = request.form.get('last_name')
                admin = request.form.get('admin') or False

                result = User.create_user(username, password, email, first_name, last_name, admin)
                if not result[0]:
                    raise LoginException("An error occurred registering your account")
                
                user = User.get_user(db_session, username)
                flash(result[1]["status"])

            # Log the user in if the password is valid
            if user.validate(password) and login_user(user, remember = remember):
                flash(f"Welcome, {username}!")
                if "login_next" in session:
                    return redirect(session.pop("login_next"))
                return redirect(url_for('root'))
            print("Invalid login")
            raise LoginException("Invalid login credentials")
        except LoginException as e:
            flash(str(e))
    return render_module('login', title="Login")

""" ----------------------------------------------------------------
logout:
    Under development
"""
@app.route('/account/logout')
@login_required
def user_logout():
    logout_user()
    flash("You have been logged out")
    return redirect(url_for('root'))

""" ----------------------------------------------------------------
default:
table:
    This route performs external authorization for a user
"""
@app.route('/user/authorize')
@login_required
def authorize_user():
    client_id = request.args.get("client_id")
    state = request.args.get("state")
    response_type = request.args.get("response_type")

    if not client_id or response_type != "code":
        return render_message("Invalid Request", "Something went wrong. You may need to return to the previous application and make the request again.")
    
    # TODO get application from client id
    client = ClientApplication.get_by_id(db_session, client_id)            

    return render_module("authorization", app = client, state = state)

@app.route('/account/delete')
@login_required
def user_delete():
    if current_user.delete()[0]:
        flash(f"Account {current_user.login_name} successfully removed")
        logout_user()
    else:
        flash("An error occurred removing the account")

    return redirect(url_for("root"))

""" ----------------------------------------------------------------
settings:
    Under development
"""
@app.route('/account/settings')
@login_required
def user_settings():
    return render_template("settings.j2")

""" ----------------------------------------------------------------
report page:
    This route returns a report view of the requested repo (by ID).
"""
@app.route('/repos/views/repo/<id>')
def repo_repo_view(id):
    repo = Repo.get_by_id(db_session, id)

    return render_module("repo-info", title="Repo", repo=repo, repo_id=id)

""" ----------------------------------------------------------------
default:
table:
    This route returns the groups view for the logged in user.
"""
@app.route('/user/groups/')
@login_required
def user_groups_view():
    params = {}

    pagination_offset = get_value("frontend", "pagination_offset")

    params = {}
    
    if query := request.args.get('q'):
        params["search"] = query

    if sort := request.args.get('s'):
        params["sort"] = sort

    rev = request.args.get('r')
    if rev is not None:
        if rev == "False":
            rev = False
            params["direction"] = "ASC"
        elif rev == "True":
            rev = True
            params["direction"] = "DESC"

    try:
        activepage = int(request.args.get('p')) if 'p' in request.args else 0
    except (ValueError, TypeError):
        activepage = 0

    (groups, status) = current_user.get_groups_info(**params)

    # if not groups and not query:
    #     return render_message("No Groups Defined", "You do not have any groups defined, you can add groups on you profile page.")
    # elif not groups:
    #     return render_message("No Matching Groups", "Your search did not match any group names.")

    page_count = len(groups)
    page_count //= pagination_offset
    current_page_start = activepage * pagination_offset
    current_page_end = current_page_start + pagination_offset

    groups = groups[current_page_start : current_page_end]

    return render_module("groups-table", title="Groups", groups=groups, query_key=query, activePage=activepage, pages=page_count, offset=pagination_offset, PS="user_groups_view", reverse = rev, sorting = sort)


""" ----------------------------------------------------------------
default:
table:
    This route returns the groups view for the logged in user.
"""
@app.route('/user/group/<group>')
@login_required
def user_group_view(group = None):
    if not group:
        return render_message("No Group Specified", "You must specify a group to view this page.")

    params = {}

    try:
        params["page"] = int(request.args.get('p') or 0)
    except (ValueError, TypeError):
        params["page"] = 1
    
    if query := request.args.get('q'):
        params["search"] = query

    if sort := request.args.get('s'):
        params["sort"] = sort

    rev = request.args.get('r')
    if rev is not None:
        if rev == "False":
            rev = False
            params["direction"] = "ASC"
        elif rev == "True":
            rev = True
            params["direction"] = "DESC"

    pagination_offset = get_value("frontend", "pagination_offset")

    data = current_user.get_group_repos(group, **params)[0]
    page_count = current_user.get_group_repo_count(group, search = query)[0] or 0
    page_count //= pagination_offset

    return render_module("user-group-repos-table", title="Repos", repos=data, query_key=query, activePage=params["page"], pages=page_count, offset=pagination_offset, PS="user_group_view", reverse = rev, sorting = params.get("sort"), group=group)

@app.route('/error')
def throw_exception():
    raise Exception("This Exception intentionally raised")

""" ----------------------------------------------------------------
Admin dashboard:
    View the admin dashboard.
"""
@app.route('/dashboard')
def dashboard_view():
    empty = [
        { "title": "Placeholder", "settings": [
            { "id": "empty",
                "display_name": "Empty Entry",
                "value": "NULL",
                "description": "There's nothing here 👻"
            }
        ]}
    ]

    # TODO: Fix requestJson function - it's not defined anywhere
    # backend_config = requestJson("config/get", False)
    backend_config = {}

    return render_template('admin-dashboard.j2', sections = empty, config = backend_config)

""" ----------------------------------------------------------------
topic_models:
    These routes render topic modeling interfaces with full Augur styling.
"""
@app.route('/repos/<repo_id>/topic-models')
def topic_models_view(repo_id):
    """
    Topic models overview page for a specific repository with full Augur styling
    """
    repo = db_session.query(Repo).filter(Repo.repo_id == repo_id).first()
    if not repo:
        return "Repository not found", 404
    
    from augur.application.db.models.augur_data import TopicModelMeta
    models = db_session.query(TopicModelMeta).filter(
        TopicModelMeta.repo_id == repo_id
    ).all()
    
    print(f"DEBUG: Found {len(models)} models for repo {repo_id}")
    return render_module('topic-models', title="Topic Models", repo=repo, models=models)

@app.route('/repos/<repo_id>/topic-models/<model_id>')
def topic_model_detail_view(repo_id, model_id):
    """
    Topic model detail page for a specific model with full Augur styling
    """
    repo = db_session.query(Repo).filter(Repo.repo_id == repo_id).first()
    if not repo:
        return "Repository not found", 404
        
    from augur.application.db.models.augur_data import TopicModelMeta, TopicWord
    model = db_session.query(TopicModelMeta).filter(
        TopicModelMeta.model_id == model_id
    ).first()
    
    if not model:
        return "Topic model not found", 404
    
    # Query topic words for this model from database
    # Note: TopicWord table doesn't have model_id, so we get all words for topic range
    topic_words_query = db_session.query(TopicWord).filter(
        TopicWord.topic_id.between(1, model.num_topics)
    ).order_by(TopicWord.topic_id, TopicWord.word_prob.desc()).all()
    
    # Organize topic words by topic_id for template
    topic_words = {}
    for topic_word in topic_words_query:
        topic_id = topic_word.topic_id
        if topic_id not in topic_words:
            topic_words[topic_id] = []
        topic_words[topic_id].append(topic_word)
    
    # Get repo topics data from visualization_data
    repo_topics = []
    if model.visualization_data and 'topics' in model.visualization_data:
        # Create repo topics from visualization data
        topics_data = model.visualization_data['topics']
        topic_count = len(topics_data)
        if topic_count > 0:
            # Even distribution as placeholder 
            prob_per_topic = 100.0 / topic_count
            for i, (topic_key, topic_info) in enumerate(topics_data.items()):
                topic_id = topic_info.get('id', i + 1)
                repo_topics.append({
                    'topic_id': topic_id,
                    'topic_prob': prob_per_topic / 100.0  # Convert back to 0-1 range
                })
    
    return render_module('topic-model-detail', title="Topic Model Details", 
                       repo=repo, model=model, topic_words=topic_words, repo_topics=repo_topics)

# API routes for Topic Modeling frontend support
@app.route('/topic-models/<repo_id>/train', methods=['POST'])
def train_topic_model_api(repo_id):
    """
    API endpoint to train a new topic model
    """
    local_logger = logging.getLogger(__name__)
    
    try:
        from augur.tasks.data_analysis.clustering_worker.tasks import train_model
        from augur.application.db import get_engine
        
        # Get training parameters from request
        params = request.get_json() or {}
        
        # Default parameters
        max_df = params.get('max_df', 0.7)
        min_df = params.get('min_df', 1)
        max_features = params.get('max_features', 1000)
        ngram_range = params.get('ngram_range', [1, 2])
        num_clusters = params.get('num_clusters', 5)
        num_topics = params.get('num_topics', 5)
        num_words_per_topic = params.get('num_words_per_topic', 12)
        
        engine = get_engine()
        
        # Start training
        train_model(
            logger=logger,
            engine=engine,
            max_df=max_df,
            min_df=min_df,
            max_features=max_features,
            ngram_range=tuple(ngram_range),
            num_clusters=num_clusters,
            num_topics=num_topics,
            num_words_per_topic=num_words_per_topic,
            tool_source="Topic Modeling Interface",
            tool_version="1.0.0",
            data_source="augur_data",
            repo_id=int(repo_id)  # Pass the correct repo_id
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Topic model training started successfully'
        })
        
    except Exception as e:
        logger.error(f"Training failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/topic-models/<repo_id>/optimize', methods=['POST'])
def optimize_topic_model_api(repo_id):
    """
    API endpoint to optimize topic model parameters
    """
    local_logger = logging.getLogger(__name__)
    
    try:
        from augur.tasks.data_analysis.clustering_worker.model_comparison import optimize_parameters
        from augur.application.db import get_engine
        
        # Get optimization parameters from request
        params = request.get_json() or {}
        
        engine = get_engine()
        
        # Start optimization
        result = optimize_parameters(
            logger=logger,
            engine=engine,
            repo_id=int(repo_id),
            optimization_params=params
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Parameter optimization completed successfully',
            'result': result
        })
        
    except Exception as e:
        logger.error(f"Optimization failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/topic-models/<repo_id>/status', methods=['GET'])
def topic_model_status_api(repo_id):
    """
    API endpoint to get topic model training status
    """
    try:
        from augur.application.db.models.augur_data import TopicModelMeta
        models = db_session.query(TopicModelMeta).filter(
            TopicModelMeta.repo_id == repo_id
        ).all()
        
        return jsonify({
            'status': 'success',
            'models': [{
                'model_id': str(model.model_id),
                'repo_id': model.repo_id,
                'model_method': model.model_method,
                'num_topics': model.num_topics,
                'num_words_per_topic': model.num_words_per_topic,
                'training_parameters': model.training_parameters,
                'coherence_score': model.coherence_score,
                'perplexity_score': model.perplexity_score,
                'topic_diversity': model.topic_diversity,
                'training_message_count': model.training_message_count,
                'visualization_data': model.visualization_data,
                'training_start_time': model.training_start_time.isoformat() if model.training_start_time else None,
                'training_end_time': model.training_end_time.isoformat() if model.training_end_time else None,
                'data_collection_date': model.data_collection_date.isoformat() if model.data_collection_date else None
            } for model in models]
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/topic-models/<repo_id>/visualization/<model_id>', methods=['GET'])
def topic_model_visualization_api(repo_id, model_id):
    """
    API endpoint to get topic model visualization data
    """
    try:
        from augur.application.db.models.augur_data import TopicModelMeta
        model = db_session.query(TopicModelMeta).filter(
            TopicModelMeta.model_id == model_id
        ).first()
        
        if not model:
            return jsonify({
                'status': 'error',
                'message': 'Topic model not found'
            }), 404
            
        # Extract and format visualization data for frontend
        viz_data = model.visualization_data or {}
        
        # Format for frontend expectations
        formatted_data = {
            'status': 'success',
            'model_id': str(model.model_id),
            'num_topics': model.num_topics,
            'model_method': model.model_method,
            'coherence_score': model.coherence_score,
            'training_date': model.data_collection_date.isoformat() if model.data_collection_date else None,
            
            # Repository topic distribution (for bar chart)
            'repo_topics': [],
            
            # Topic positions (for PCA scatter plot) 
            'topic_positions': [],
            
            # Topics and words (for word clouds)
            'topics': viz_data.get('topics', {})
        }
        
        # Generate mock repository topic distribution if not available
        if model.num_topics and model.num_topics > 0:
            # Create even distribution as placeholder
            prob_per_topic = 1.0 / model.num_topics
            for i in range(model.num_topics):
                formatted_data['repo_topics'].append({
                    'topic_id': i + 1,
                    'topic_prob': prob_per_topic * 100  # Convert to percentage
                })
                
            # Generate mock PCA positions in a circle
            import math as math_module
            for i in range(model.num_topics):
                angle = (2 * math_module.pi * i) / model.num_topics
                formatted_data['topic_positions'].append({
                    'topic_id': i + 1,
                    'x': math_module.cos(angle),
                    'y': math_module.sin(angle)
                })
        
        return jsonify(formatted_data)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/topic-models/<repo_id>/compare', methods=['GET'])
def topic_model_compare_api(repo_id):
    """API endpoint for comparing two topic models"""
    local_logger = logging.getLogger(__name__)
    
    try:
        model_a_id = request.args.get('model_a')
        model_b_id = request.args.get('model_b')
        
        if not model_a_id or not model_b_id:
            logger.error("Missing model IDs for comparison")
            return jsonify({
                'status': 'error', 
                'message': 'Both model_a and model_b parameters are required'
            }), 400
        
        logger.info(f"Comparing models {model_a_id} vs {model_b_id} for repo {repo_id}")
        
        from augur.application.db.models.augur_data import TopicModelMeta
        model_a = db_session.query(TopicModelMeta).filter_by(model_id=model_a_id).first()
        model_b = db_session.query(TopicModelMeta).filter_by(model_id=model_b_id).first()
        
        if not model_a or not model_b:
            logger.error(f"Model not found: A={bool(model_a)}, B={bool(model_b)}")
            return jsonify({
                'status': 'error',
                'message': 'One or both models not found'
            }), 404
        
        # Calculate comparison metrics
        coherence_improvement = (model_b.coherence_score or 0.0) - (model_a.coherence_score or 0.0)
        
        # Determine overall improvement
        if coherence_improvement > 0.1:
            overall_improvement = "significant_improvement"
        elif coherence_improvement > 0.01:
            overall_improvement = "improvement" 
        elif coherence_improvement > -0.01:
            overall_improvement = "no_change"
        elif coherence_improvement > -0.1:
            overall_improvement = "decline"
        else:
            overall_improvement = "significant_decline"
        
        # Get model parameters
        params_a = model_a.training_parameters or {}
        params_b = model_b.training_parameters or {}
        
        # Format response
        response_data = {
            'status': 'success',
            'repo_id': int(repo_id),
            'model_a_id': model_a_id,
            'model_a_coherence': round(model_a.coherence_score or 0.0, 4),
            'model_a_topics': model_a.num_topics or 'N/A',
            'model_a_created': model_a.training_start_time.isoformat() if model_a.training_start_time else 'N/A',
            'model_b_id': model_b_id, 
            'model_b_coherence': round(model_b.coherence_score or 0.0, 4),
            'model_b_topics': model_b.num_topics or 'N/A',
            'model_b_created': model_b.training_start_time.isoformat() if model_b.training_start_time else 'N/A',
            'coherence_improvement': round(coherence_improvement, 4),
            'overall_improvement': overall_improvement,
            'comparison_notes': []
        }
        
        # Add comparison notes
        if coherence_improvement > 0:
            response_data['comparison_notes'].append(f"Coherence improved by {coherence_improvement:.4f}")
        elif coherence_improvement < 0:
            response_data['comparison_notes'].append(f"Coherence decreased by {abs(coherence_improvement):.4f}")
        else:
            response_data['comparison_notes'].append("No change in coherence score")
        
        # Compare parameters
        if params_a.get('num_topics') != params_b.get('num_topics'):
            response_data['comparison_notes'].append(
                f"Topics changed: {params_a.get('num_topics', 'N/A')} → {params_b.get('num_topics', 'N/A')}"
            )
        
        logger.info(f"Model comparison completed: {overall_improvement}")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Model comparison failed: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Comparison failed: {str(e)}'
        }), 500

@app.route('/topic-models/<repo_id>/timeline', methods=['GET'])
def topic_model_timeline_api(repo_id):
    """
    API endpoint to get model evolution timeline data for a repository.
    Returns models ordered by training_end_time with key metrics for charting.
    """
    try:
        from augur.application.db.models.augur_data import TopicModelMeta
        query = db_session.query(TopicModelMeta).filter(
            TopicModelMeta.repo_id == repo_id
        ).order_by(TopicModelMeta.training_end_time.asc())
        models = query.all()

        points = []
        for m in models:
            points.append({
                'model_id': str(m.model_id),
                'training_start_time': m.training_start_time.isoformat() if m.training_start_time else None,
                'training_end_time': m.training_end_time.isoformat() if m.training_end_time else None,
                'coherence_score': float(m.coherence_score) if m.coherence_score is not None else None,
                'num_topics': int(m.num_topics) if m.num_topics is not None else None,
                'model_method': m.model_method,
            })

        return jsonify({
            'status': 'success',
            'repo_id': int(repo_id),
            'points': points
        })
    except Exception as e:
        logger.error(f"Timeline generation failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/topic-models/<repo_id>/export/<model_id>.json', methods=['GET'])
def topic_model_export_api(repo_id, model_id):
    """
    Export a model as JSON with metadata, parameters, topic-word distributions, and repository topics.
    Structure mirrors the frontend exportModel() payload for interoperability.
    """
    try:
        from augur.application.db.models.augur_data import TopicModelMeta, TopicWord
        model = db_session.query(TopicModelMeta).filter(TopicModelMeta.model_id == model_id).first()
        if not model:
            return jsonify({'status': 'error', 'message': 'Model not found'}), 404

        # Build export payload
        export = {
            'model_metadata': {
                'model_id': str(model.model_id),
                'model_method': model.model_method,
                'num_topics': model.num_topics,
                'num_words_per_topic': model.num_words_per_topic,
                'coherence_score': float(model.coherence_score) if model.coherence_score is not None else None,
                'training_date': model.training_end_time.strftime('%Y-%m-%d %H:%M:%S') if model.training_end_time else 'Unknown',
                'tool_source': model.tool_source or 'Unknown',
                'tool_version': model.tool_version or 'Unknown',
            },
            'training_parameters': model.training_parameters or {},
            'topics': {},
            'repository_topics': [],
            'export_info': {
                'exported_at': datetime.utcnow().isoformat() + 'Z',
                'exported_by': 'Augur Topic Modeling API',
                'format_version': '1.0',
                'description': 'Complete topic model export including metadata, parameters, topics, and repository associations.'
            }
        }

        # Topic-word distributions
        topic_words = db_session.query(TopicWord).filter(
            TopicWord.topic_id.between(1, model.num_topics)
        ).order_by(TopicWord.topic_id, TopicWord.word_prob.desc()).all()

        by_topic = {}
        for tw in topic_words:
            by_topic.setdefault(tw.topic_id, []).append({
                'word': tw.word,
                'probability': float(tw.word_prob) if tw.word_prob is not None else None
            })
        for topic_id, words in by_topic.items():
            export['topics'][f'topic_{topic_id}'] = {
                'topic_id': topic_id,
                'words': [
                    { 'word': w['word'], 'probability': w['probability'], 'rank': idx + 1 }
                    for idx, w in enumerate(words)
                ]
            }

        # Repository topic probabilities if available via visualization_data
        viz = model.visualization_data or {}
        topics_data = viz.get('topics', {})
        if topics_data:
            # Even distribution fallback already handled in visualization API; here we pass-through if present
            for key, info in topics_data.items():
                topic_id = info.get('id')
                prob = info.get('probability') or info.get('topic_prob')
                export['repository_topics'].append({
                    'topic_id': topic_id,
                    'probability': prob,
                    'data_collection_date': model.data_collection_date.strftime('%Y-%m-%d') if model.data_collection_date else 'Unknown'
                })

        return jsonify(export)
    except Exception as e:
        logger.error(f"Export failed: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
