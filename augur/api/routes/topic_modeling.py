"""
Topic Modeling API Routes

This module provides API endpoints for topic modeling functionality.
"""

from flask import jsonify, request
from augur.application.db.models.augur_data import TopicModelMeta
from augur.api.util import ssl_required
from ..server import app, db_session
from augur.api.routes import AUGUR_API_VERSION


@app.route(f"/{AUGUR_API_VERSION}/topic-models", methods=['GET'])
@ssl_required
def get_topic_models():
    """Get all topic models"""
    try:
        models = db_session.query(TopicModelMeta).all()
        
        result = []
        for model in models:
            result.append({
                'model_id': str(model.model_id),
                'repo_id': model.repo_id,
                'model_type': model.model_type,
                'num_topics': model.num_topics,
                'created_at': model.created_at.isoformat() if model.created_at else None,
                'updated_at': model.updated_at.isoformat() if model.updated_at else None
            })
        
        return jsonify({'status': 'success', 'data': result})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route(f"/{AUGUR_API_VERSION}/topic-models/<model_id>", methods=['GET'])
@ssl_required
def get_topic_model(model_id):
    """Get a specific topic model by ID"""
    try:
        model = db_session.query(TopicModelMeta).filter(
            TopicModelMeta.model_id == model_id
        ).first()
        
        if not model:
            return jsonify({'status': 'error', 'message': 'Model not found'}), 404
        
        result = {
            'model_id': str(model.model_id),
            'repo_id': model.repo_id,
            'model_type': model.model_type,
            'num_topics': model.num_topics,
            'created_at': model.created_at.isoformat() if model.created_at else None,
            'updated_at': model.updated_at.isoformat() if model.updated_at else None
        }
        
        return jsonify({'status': 'success', 'data': result})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route(f"/{AUGUR_API_VERSION}/topic-models/<model_id>/visualization", methods=['GET'])
@ssl_required
def get_topic_model_visualization(model_id):
    """Get visualization data for a specific topic model"""
    try:
        model = db_session.query(TopicModelMeta).filter(
            TopicModelMeta.model_id == model_id
        ).first()
        
        if not model:
            return jsonify({'status': 'error', 'message': 'Model not found'}), 404
        
        # For now, return basic visualization data
        # This would be enhanced with actual topic modeling results
        visualization_data = {
            'model_id': str(model.model_id),
            'topics': [],  # Placeholder for topic data
            'word_clouds': [],  # Placeholder for word cloud data
            'metrics': {
                'coherence': None,
                'perplexity': None
            }
        }
        
        return jsonify({'status': 'success', 'data': visualization_data})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route(f"/{AUGUR_API_VERSION}/repos/<int:repo_id>/topic-models", methods=['GET'])
@ssl_required
def get_repo_topic_models(repo_id):
    """Get all topic models for a specific repository"""
    try:
        models = db_session.query(TopicModelMeta).filter(
            TopicModelMeta.repo_id == repo_id
        ).all()
        
        result = []
        for model in models:
            result.append({
                'model_id': str(model.model_id),
                'repo_id': model.repo_id,
                'model_type': model.model_type,
                'num_topics': model.num_topics,
                'created_at': model.created_at.isoformat() if model.created_at else None,
                'updated_at': model.updated_at.isoformat() if model.updated_at else None
            })
        
        return jsonify({'status': 'success', 'data': result})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route(f"/{AUGUR_API_VERSION}/topic-models/<int:repo_id>/train", methods=['POST'])
@ssl_required
def train_topic_model(repo_id):
    """Train a new topic model for a repository"""
    try:
        # This would integrate with the clustering worker
        # For now, return a placeholder response
        return jsonify({
            'status': 'success', 
            'message': 'Topic model training initiated',
            'repo_id': repo_id
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route(f"/{AUGUR_API_VERSION}/topic-models/<int:repo_id>/optimize", methods=['POST'])
@ssl_required
def optimize_topic_model(repo_id):
    """Optimize topic model parameters for a repository"""
    try:
        # This would integrate with the clustering worker
        # For now, return a placeholder response
        return jsonify({
            'status': 'success', 
            'message': 'Topic model optimization initiated',
            'repo_id': repo_id
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route(f"/{AUGUR_API_VERSION}/topic-models/<int:repo_id>/compare", methods=['GET'])
@ssl_required
def compare_topic_models(repo_id):
    """Compare topic models for a repository"""
    try:
        model_a_id = request.args.get('model_a')
        model_b_id = request.args.get('model_b')
        
        if not model_a_id or not model_b_id:
            return jsonify({'status': 'error', 'message': 'Both model_a and model_b are required'}), 400
        
        # This would integrate with the clustering worker
        # For now, return a placeholder response
        return jsonify({
            'status': 'success', 
            'message': 'Topic model comparison completed',
            'repo_id': repo_id,
            'model_a': model_a_id,
            'model_b': model_b_id
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route(f"/{AUGUR_API_VERSION}/topic-models/<int:repo_id>/status", methods=['GET'])
@ssl_required
def get_topic_model_status(repo_id):
    """Get the status of topic modeling for a repository"""
    try:
        models_count = db_session.query(TopicModelMeta).filter(
            TopicModelMeta.repo_id == repo_id
        ).count()
        
        return jsonify({
            'status': 'success', 
            'repo_id': repo_id,
            'models_count': models_count,
            'ready_for_training': True
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500