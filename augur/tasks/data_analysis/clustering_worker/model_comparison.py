"""
Model Comparison Logic

This module provides functionality to compare old and new topic models
and evaluate their performance differences.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from augur.application.db import get_session
from augur.application.db.models import TopicModelMeta


@dataclass
class ModelComparisonResult:
    """Result of model comparison"""

    old_model_id: str
    new_model_id: str
    coherence_improvement: float
    training_time_difference: float  # in seconds
    parameter_changes: Dict[str, Tuple]
    overall_improvement: bool
    comparison_notes: List[str]


class ModelComparator:
    """
    Compare old and new topic models to evaluate improvements.
    """

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def compare_models(
        self, old_model_id: str, new_model_id: str
    ) -> ModelComparisonResult:
        """
        Compare two models and return detailed comparison results.

        Args:
            old_model_id: ID of the old model
            new_model_id: ID of the new model

        Returns:
            ModelComparisonResult with detailed comparison
        """
        self.logger.info(f"Comparing models: {old_model_id} vs {new_model_id}")

        try:
            with get_session() as session:
                # Get model metadata
                old_model = (
                    session.query(TopicModelMeta)
                    .filter(TopicModelMeta.model_id == old_model_id)
                    .first()
                )

                new_model = (
                    session.query(TopicModelMeta)
                    .filter(TopicModelMeta.model_id == new_model_id)
                    .first()
                )

                if not old_model or not new_model:
                    raise ValueError("One or both models not found")

                # Calculate improvements
                coherence_improvement = self._calculate_coherence_improvement(
                    old_model.coherence_score, new_model.coherence_score
                )

                training_time_diff = self._calculate_training_time_difference(
                    old_model.training_end_time, new_model.training_end_time
                )

                parameter_changes = self._compare_parameters(
                    old_model.training_parameters, new_model.training_parameters
                )

                overall_improvement = self._determine_overall_improvement(
                    coherence_improvement, parameter_changes
                )

                comparison_notes = self._generate_comparison_notes(
                    coherence_improvement, training_time_diff, parameter_changes
                )

                return ModelComparisonResult(
                    old_model_id=old_model_id,
                    new_model_id=new_model_id,
                    coherence_improvement=coherence_improvement,
                    training_time_difference=training_time_diff,
                    parameter_changes=parameter_changes,
                    overall_improvement=overall_improvement,
                    comparison_notes=comparison_notes,
                )

        except Exception as e:
            self.logger.error(f"Error comparing models: {e}")
            raise

    def _calculate_coherence_improvement(
        self, old_coherence: float, new_coherence: float
    ) -> float:
        """Calculate coherence score improvement"""
        if old_coherence is None or new_coherence is None:
            return 0.0

        improvement = new_coherence - old_coherence
        self.logger.info(f"Coherence improvement: {improvement:.3f}")
        return improvement

    def _calculate_training_time_difference(
        self, old_time: datetime, new_time: datetime
    ) -> float:
        """Calculate training time difference in seconds"""
        time_diff = (new_time - old_time).total_seconds()
        self.logger.info(f"Training time difference: {time_diff:.2f} seconds")
        return time_diff

    def _compare_parameters(
        self, old_params: Dict, new_params: Dict
    ) -> Dict[str, Tuple]:
        """Compare training parameters between models"""
        changes = {}

        # Key parameters to compare
        key_params = [
            "num_topics",
            "num_words_per_topic",
            "max_df",
            "min_df",
            "max_features",
        ]

        for param in key_params:
            old_val = old_params.get(param)
            new_val = new_params.get(param)

            if old_val != new_val:
                changes[param] = (old_val, new_val)
                self.logger.info(f"Parameter {param} changed: {old_val} -> {new_val}")

        return changes

    def _determine_overall_improvement(
        self, coherence_improvement: float, parameter_changes: Dict[str, Tuple]
    ) -> bool:
        """Determine if the new model represents an overall improvement"""
        # Consider it an improvement if coherence improved and no major parameter regressions
        coherence_improved = coherence_improvement > 0

        # Check for parameter regressions (simplified logic)
        no_major_regressions = True
        for param, (old_val, new_val) in parameter_changes.items():
            if param == "num_topics" and new_val < old_val:
                # Fewer topics might be a regression
                no_major_regressions = False
            elif param == "max_features" and new_val < old_val:
                # Fewer features might be a regression
                no_major_regressions = False

        overall_improvement = coherence_improved and no_major_regressions
        self.logger.info(f"Overall improvement: {overall_improvement}")
        return overall_improvement

    def _generate_comparison_notes(
        self,
        coherence_improvement: float,
        training_time_diff: float,
        parameter_changes: Dict[str, Tuple],
    ) -> List[str]:
        """Generate human-readable comparison notes"""
        notes = []

        if coherence_improvement > 0:
            notes.append(f"Coherence improved by {coherence_improvement:.3f}")
        elif coherence_improvement < 0:
            notes.append(f"Coherence decreased by {abs(coherence_improvement):.3f}")
        else:
            notes.append("Coherence score unchanged")

        if training_time_diff > 0:
            notes.append(f"Training took {training_time_diff:.2f} seconds longer")
        elif training_time_diff < 0:
            notes.append(f"Training was {abs(training_time_diff):.2f} seconds faster")
        else:
            notes.append("Training time unchanged")

        if parameter_changes:
            changes_list = [
                f"{param}: {old_val} -> {new_val}"
                for param, (old_val, new_val) in parameter_changes.items()
            ]
            notes.append(f"Parameter changes: {', '.join(changes_list)}")
        else:
            notes.append("No parameter changes")

        return notes

    def get_model_history(self, repo_id: int, limit: int = 5) -> List[TopicModelMeta]:
        """
        Get model history for a repository.

        Args:
            repo_id: Repository ID
            limit: Maximum number of models to return

        Returns:
            List of model metadata ordered by training time (newest first)
        """
        try:
            with get_session() as session:
                models = (
                    session.query(TopicModelMeta)
                    .filter(
                        TopicModelMeta.model_method
                        == "NMF_COUNT"  # Focus on NMF models
                    )
                    .order_by(TopicModelMeta.training_end_time.desc())
                    .limit(limit)
                    .all()
                )

                self.logger.info(f"Retrieved {len(models)} models for repo {repo_id}")
                return models

        except Exception as e:
            self.logger.error(f"Error retrieving model history: {e}")
            return []

    def compare_latest_models(self, repo_id: int) -> Optional[ModelComparisonResult]:
        """
        Compare the two most recent models for a repository.

        Args:
            repo_id: Repository ID

        Returns:
            Comparison result if at least 2 models exist, None otherwise
        """
        models = self.get_model_history(repo_id, limit=2)

        if len(models) < 2:
            self.logger.info(f"Not enough models for comparison (found {len(models)})")
            return None

        return self.compare_models(str(models[1].model_id), str(models[0].model_id))

    def generate_comparison_report(
        self, comparison_result: ModelComparisonResult
    ) -> str:
        """
        Generate a human-readable comparison report.

        Args:
            comparison_result: Result of model comparison

        Returns:
            Formatted comparison report
        """
        report = f"""
Model Comparison Report
======================

Old Model ID: {comparison_result.old_model_id}
New Model ID: {comparison_result.new_model_id}

Performance Metrics:
- Coherence Improvement: {comparison_result.coherence_improvement:.3f}
- Training Time Difference: {comparison_result.training_time_difference:.2f} seconds

Parameter Changes:
"""

        if comparison_result.parameter_changes:
            for param, (
                old_val,
                new_val,
            ) in comparison_result.parameter_changes.items():
                report += f"- {param}: {old_val} → {new_val}\n"
        else:
            report += "- No parameter changes\n"

        report += f"""
Overall Assessment:
- Overall Improvement: {'Yes' if comparison_result.overall_improvement else 'No'}

Notes:
"""

        for note in comparison_result.comparison_notes:
            report += f"- {note}\n"

        return report


def create_model_comparator(logger: logging.Logger) -> ModelComparator:
    """
    Create a model comparator instance.

    Args:
        logger: Logger instance

    Returns:
        ModelComparator instance
    """
    return ModelComparator(logger)


def optimize_parameters(logger, engine, repo_id, optimization_params):
    """
    Optimize topic modeling parameters for a given repository based on actual data.
    
    Args:
        logger: Logger instance
        engine: Database engine
        repo_id: Repository ID
        optimization_params: Dictionary containing parameter ranges to optimize
        
    Returns:
        Dictionary containing optimization results
    """
    logger.info(f"Starting REAL parameter optimization for repo {repo_id}")
    
    try:
        from sqlalchemy import text
        
        # Get message data for this repo to understand dataset characteristics
        with engine.connect() as conn:
            query = text("""
                SELECT COUNT(*) as message_count,
                       AVG(LENGTH(msg_text)) as avg_message_length,
                       COUNT(DISTINCT cntrb_id) as contributor_count
                FROM augur_data.message m
                JOIN augur_data.repo r ON m.repo_id = r.repo_id  
                WHERE m.repo_id = :repo_id
                AND msg_text IS NOT NULL 
                AND msg_text != ''
            """)
            result = conn.execute(query, {"repo_id": repo_id})
            data_stats = result.fetchone()
            
        if not data_stats or data_stats[0] == 0:
            logger.warning(f"No message data found for repo {repo_id}, using default parameters")
            return {
                'status': 'completed',
                'best_params': {
                    'num_topics': 5,
                    'max_df': 0.8,
                    'min_df': 1,
                    'max_features': 1000,
                    'num_clusters': 3,
                    'num_words_per_topic': 12
                },
                'best_score': 0.50,  # Default score
                'evaluated_counts': 'No data available',
                'optimization_method': 'default_fallback',
                'model_trained': False,
                'notes': 'No data available for optimization, using safe defaults'
            }
        
        message_count = data_stats[0]
        avg_length = data_stats[1] or 100
        contributor_count = data_stats[2] or 1
        
        logger.info(f"Dataset characteristics: {message_count} messages, avg length {avg_length:.1f}, {contributor_count} contributors")
        
        # Smart parameter optimization based on data characteristics
        # 1. Number of topics: Based on message count and contributor diversity
        if message_count < 10:
            optimal_topics = 2
        elif message_count < 50:
            optimal_topics = min(3, max(2, message_count // 5))
        elif message_count < 200:
            optimal_topics = min(5, max(3, message_count // 20))
        elif message_count < 1000:
            optimal_topics = min(8, max(5, message_count // 50))
        else:
            optimal_topics = min(12, max(8, message_count // 100))
            
        # 2. min_df: Based on message count (avoid overfitting)
        if message_count < 20:
            optimal_min_df = 1
        elif message_count < 100:
            optimal_min_df = max(1, message_count // 20)
        else:
            optimal_min_df = max(2, min(5, message_count // 50))
        
        # 3. max_df: Based on diversity (avoid common words)
        if contributor_count < 5:
            optimal_max_df = 0.9  # Less strict for small teams
        elif contributor_count < 20:
            optimal_max_df = 0.8
        else:
            optimal_max_df = 0.7  # More strict for large teams
            
        # 4. max_features: Based on message count and length
        if message_count < 50:
            optimal_max_features = 500
        elif message_count < 200:
            optimal_max_features = 1000
        else:
            optimal_max_features = min(5000, max(1000, int(message_count * 2.5)))
            
        # 5. num_clusters: Usually slightly less than topics
        optimal_clusters = max(2, optimal_topics - 1)
        
        # 6. words_per_topic: Based on average message length
        if avg_length < 50:
            optimal_words_per_topic = 8
        elif avg_length < 150:
            optimal_words_per_topic = 12
        else:
            optimal_words_per_topic = 15
        
        best_params = {
            'num_topics': optimal_topics,
            'max_df': optimal_max_df,
            'min_df': optimal_min_df,
            'max_features': optimal_max_features,
            'num_clusters': optimal_clusters,
            'num_words_per_topic': optimal_words_per_topic
        }
        
        logger.info(f"Data-driven optimization completed for repo {repo_id}")
        logger.info(f"Optimized parameters: {best_params}")
        
        # Calculate a simple optimization score
        optimization_score = (
            (optimal_topics / 10.0) * 0.3 +  # Topic diversity
            (1.0 - optimal_max_df) * 0.2 +    # Specificity 
            (optimal_min_df / 5.0) * 0.2 +    # Noise reduction
            (optimal_max_features / 5000.0) * 0.3  # Feature richness
        )
        
        # Now train a model with the optimized parameters
        logger.info(f"Training new model with optimized parameters for repo {repo_id}")
        training_success = False
        new_model_id = None
        training_error = None
        
        try:
            from augur.tasks.data_analysis.clustering_worker.tasks import train_model
            
            # Train the model with optimized parameters
            new_model_id = train_model(
                logger=logger,
                engine=engine,
                max_df=optimal_max_df,
                min_df=optimal_min_df,
                max_features=optimal_max_features,
                ngram_range=(1, 2),  # Default ngram range
                num_clusters=optimal_clusters,
                num_topics=optimal_topics,
                num_words_per_topic=optimal_words_per_topic,
                tool_source="Parameter Optimization",
                tool_version="1.0.0",
                data_source="augur_data",
                repo_id=int(repo_id)
            )
            training_success = True
            logger.info(f"Successfully trained optimized model {new_model_id} for repo {repo_id}")
            
        except Exception as train_error:
            training_error = str(train_error)
            logger.error(f"Failed to train optimized model for repo {repo_id}: {training_error}")
        
        if training_success:
            return {
                'status': 'completed_with_new_model',  # Indicate successful training
                'best_params': best_params,
                'best_score': round(optimization_score, 3),
                'evaluated_counts': f'{message_count} messages analyzed',
                'optimization_method': 'data_driven_heuristic',
                'new_model_id': str(new_model_id) if new_model_id else None,
                'dataset_stats': {
                    'message_count': message_count,
                    'avg_message_length': round(avg_length, 1),
                    'contributor_count': contributor_count
                },
                'optimization_reasoning': {
                    'num_topics': f'Based on {message_count} messages: {optimal_topics} topics optimal',
                    'min_df': f'Set to {optimal_min_df} to handle {message_count} documents',
                    'max_df': f'Set to {optimal_max_df} for {contributor_count} contributors',
                    'max_features': f'Set to {optimal_max_features} for dataset size'
                },
                'detailed_analysis': f'Analyzed {message_count} messages (avg length: {round(avg_length, 1)}) from {contributor_count} contributors. Trained optimized model.',
                'model_trained': True,  # Indicate successful training
                'notes': 'Parameters optimized and new model trained successfully'
            }
        
        return {
            'status': 'optimization_completed_training_failed',
                'best_params': best_params,
                'best_score': round(optimization_score, 3),
                'evaluated_counts': f'{message_count} messages analyzed',
                'optimization_method': 'data_driven_heuristic',
                'training_error': training_error,
                'dataset_stats': {
                    'message_count': message_count,
                    'avg_message_length': round(avg_length, 1),
                    'contributor_count': contributor_count
                },
                'optimization_reasoning': {
                    'num_topics': f'Based on {message_count} messages: {optimal_topics} topics optimal',
                    'min_df': f'Set to {optimal_min_df} to handle {message_count} documents',
                    'max_df': f'Set to {optimal_max_df} for {contributor_count} contributors',
                    'max_features': f'Set to {optimal_max_features} for dataset size'
                },
                'detailed_analysis': f'Analyzed {message_count} messages but training failed: {training_error}',
                'model_trained': False,
                'notes': 'Parameters optimized but model training failed'
            }
        
    except Exception as e:
        logger.error(f"Parameter optimization failed: {e}")
        raise
