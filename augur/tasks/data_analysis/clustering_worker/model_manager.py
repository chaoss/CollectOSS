"""
Model Manager for Topic Modeling

This module provides intelligent model versioning, caching, and reuse functionality
for the topic modeling system in Augur.
"""

import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional, Tuple

from augur.application.db import get_session
from augur.application.db.models import TopicModelMeta, Message


@dataclass
class ModelCache:
    """Model cache configuration"""

    cache_dir: str
    max_cache_size: int = 100  # Maximum number of cached models
    cache_expiry_days: int = 30  # Days before cache expires


@dataclass
class RetrainConfig:
    """Retraining configuration"""

    retrain_days: int = 90  # Retrain if model is older than this
    retrain_msg_growth: float = 0.2  # Retrain if message count grows by this fraction
    retrain_coherence_threshold: float = 0.3  # Retrain if coherence drops below this
    retrain_perplexity_threshold: float = (
        2.0  # Retrain if perplexity increases above this
    )


class ModelManager:
    """
    Intelligent model manager for topic modeling with versioning, caching, and reuse.
    """

    def __init__(
        self,
        logger: logging.Logger,
        cache_config: ModelCache,
        retrain_config: RetrainConfig,
    ):
        self.logger = logger
        self.cache_config = cache_config
        self.retrain_config = retrain_config

        # Ensure cache directory exists (cache is different from artifacts)
        os.makedirs(self.cache_config.cache_dir, exist_ok=True)

    def should_retrain(
        self,
        repo_id: int,
        model_id: Optional[str] = None,
        current_params: Optional[Dict] = None,
    ) -> Tuple[bool, str]:
        """
        Determine if a model should be retrained based on multiple criteria.

        Args:
            repo_id: Repository ID
            model_id: Current model ID (if exists)
            current_params: Current training parameters

        Returns:
            Tuple of (should_retrain, reason)
        """
        self.logger.info(f"Checking if model should be retrained for repo {repo_id}")

        # Check if model exists
        if not model_id:
            self.logger.info("No existing model found - retraining needed")
            return True, "No existing model"

        try:
            with get_session() as session:
                # Get model metadata
                model_meta = (
                    session.query(TopicModelMeta)
                    .filter(TopicModelMeta.model_id == model_id)
                    .first()
                )

                if not model_meta:
                    self.logger.info("Model metadata not found - retraining needed")
                    return True, "Model metadata not found"

                # Check model age
                model_age_days = (datetime.now() - model_meta.training_end_time).days
                if model_age_days > self.retrain_config.retrain_days:
                    self.logger.info(
                        f"Model is {model_age_days} days old - retraining needed"
                    )
                    return (
                        True,
                        f"Model age ({model_age_days} days) exceeds threshold ({self.retrain_config.retrain_days} days)",
                    )

                # Check data growth
                current_msg_count = self._get_message_count(repo_id, session)
                training_msg_count = self._get_training_message_count(model_id, session)

                if training_msg_count > 0:
                    growth_rate = (
                        current_msg_count - training_msg_count
                    ) / training_msg_count
                    if growth_rate > self.retrain_config.retrain_msg_growth:
                        self.logger.info(
                            f"Message growth rate {growth_rate:.2%} exceeds threshold {self.retrain_config.retrain_msg_growth:.2%}"
                        )
                        return (
                            True,
                            f"Data growth rate ({growth_rate:.2%}) exceeds threshold ({self.retrain_config.retrain_msg_growth:.2%})",
                        )

                # Check model performance
                if (
                    model_meta.coherence_score
                    and model_meta.coherence_score
                    < self.retrain_config.retrain_coherence_threshold
                ):
                    self.logger.info(
                        f"Coherence score {model_meta.coherence_score:.3f} below threshold {self.retrain_config.retrain_coherence_threshold}"
                    )
                    return (
                        True,
                        f"Coherence score ({model_meta.coherence_score:.3f}) below threshold ({self.retrain_config.retrain_coherence_threshold})",
                    )

                # Check parameter changes
                if current_params and self._parameters_changed(
                    model_meta.training_parameters, current_params
                ):
                    self.logger.info("Training parameters changed - retraining needed")
                    return True, "Training parameters changed"

                self.logger.info("Model is still valid - no retraining needed")
                return False, "Model is still valid"

        except Exception as e:
            self.logger.error(f"Error checking retrain conditions: {e}")
            return True, f"Error checking retrain conditions: {e}"

    def find_reusable_model(self, repo_id: int, params: Dict) -> Optional[str]:
        """
        Find a reusable model that matches the given parameters.

        Args:
            repo_id: Repository ID
            params: Training parameters

        Returns:
            Model ID if reusable model found, None otherwise
        """
        self.logger.info(f"Looking for reusable model for repo {repo_id}")

        try:
            with get_session() as session:
                # Find models with similar parameters
                similar_models = (
                    session.query(TopicModelMeta)
                    .filter(
                        TopicModelMeta.model_method
                        == params.get("model_method", "NMF_COUNT"),
                        TopicModelMeta.num_topics == params.get("num_topics", 8),
                        TopicModelMeta.num_words_per_topic
                        == params.get("num_words_per_topic", 12),
                    )
                    .order_by(TopicModelMeta.training_end_time.desc())
                    .limit(5)
                    .all()
                )

                for model in similar_models:
                    # Check if parameters are close enough
                    if self._parameters_similar(model.training_parameters, params):
                        # Check if model files exist
                        if self._model_files_exist(model.model_file_paths):
                            self.logger.info(f"Found reusable model: {model.model_id}")
                            return str(model.model_id)

                self.logger.info("No reusable model found")
                return None

        except Exception as e:
            self.logger.error(f"Error finding reusable model: {e}")
            return None

    def cache_model(self, model_id: str, model_data: Dict) -> bool:
        """
        Cache a model for future reuse.

        Args:
            model_id: Model ID
            model_data: Model data to cache

        Returns:
            True if caching successful, False otherwise
        """
        try:
            # Validate input data
            if model_data is None:
                self.logger.error(f"Cannot cache model {model_id}: model_data is None")
                return False

            cache_file = os.path.join(self.cache_config.cache_dir, f"{model_id}.json")
            
            # Add cache metadata
            cache_data = {
                "model_id": model_id,
                "cached_at": datetime.now().isoformat(),
                "model_data": model_data,
            }

            with open(cache_file, "w") as f:
                json.dump(cache_data, f, indent=2)

            # Clean up old cache entries
            self._cleanup_cache()

            self.logger.info(f"Model {model_id} cached successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error caching model {model_id}: {e}")
            return False

    def get_cached_model(self, model_id: str) -> Optional[Dict]:
        """
        Retrieve a cached model.

        Args:
            model_id: Model ID

        Returns:
            Cached model data if found, None otherwise
        """
        try:
            cache_file = os.path.join(self.cache_config.cache_dir, f"{model_id}.json")

            if not os.path.exists(cache_file):
                return None

            # Check cache expiry
            file_age = time.time() - os.path.getmtime(cache_file)
            if file_age > (self.cache_config.cache_expiry_days * 24 * 3600):
                self.logger.info(f"Cache for model {model_id} has expired")
                os.remove(cache_file)
                return None

            with open(cache_file, "r") as f:
                cache_data = json.load(f)

            self.logger.info(f"Retrieved cached model {model_id}")
            return cache_data.get("model_data")

        except Exception as e:
            self.logger.error(f"Error retrieving cached model {model_id}: {e}")
            return None

    def _get_message_count(self, repo_id: int, session) -> int:
        """Get current message count for repository"""
        try:
            count = session.query(Message).filter(Message.repo_id == repo_id).count()
            return count
        except Exception as e:
            self.logger.error(f"Error getting message count: {e}")
            return 0

    def _get_training_message_count(self, model_id: str, session) -> int:
        """Get message count at time of training"""
        try:
            meta = (
                session.query(TopicModelMeta)
                .filter(TopicModelMeta.model_id == model_id)
                .first()
            )
            if not meta:
                return 0
            params = meta.training_parameters or {}
            value = params.get("training_message_count")
            return int(value) if value is not None else 0
        except Exception as e:
            self.logger.error(f"Error getting training message count: {e}")
            return 0

    def _parameters_changed(self, old_params: Dict, new_params: Dict) -> bool:
        """Check if training parameters have changed significantly"""
        try:
            # Compare key parameters
            key_params = [
                "num_topics",
                "num_words_per_topic",
                "max_df",
                "min_df",
                "max_features",
            ]

            for param in key_params:
                if old_params.get(param) != new_params.get(param):
                    return True

            return False

        except Exception as e:
            self.logger.error(f"Error comparing parameters: {e}")
            return True

    def _parameters_similar(self, old_params: Dict, new_params: Dict) -> bool:
        """Check if parameters are similar enough for reuse"""
        try:
            # Allow some tolerance for parameter differences
            tolerance = 0.15  # Increased tolerance to allow 8->9 (0.125 difference)

            for param in ["num_topics", "num_words_per_topic", "max_features"]:
                old_val = old_params.get(param, 0)
                new_val = new_params.get(param, 0)

                if old_val > 0 and new_val > 0:
                    diff = abs(old_val - new_val) / old_val
                    if diff > tolerance:
                        return False
                elif old_val != new_val:
                    # If one is 0 or missing, they must be exactly the same
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Error checking parameter similarity: {e}")
            return False

    def _model_files_exist(self, file_paths: Dict) -> bool:
        """Check if model files exist"""
        try:
            for file_type, file_path in file_paths.items():
                if not os.path.exists(file_path):
                    return False
            return True
        except Exception as e:
            self.logger.error(f"Error checking model files: {e}")
            return False

    def _cleanup_cache(self):
        """Clean up old cache entries"""
        try:
            cache_files = []
            for filename in os.listdir(self.cache_config.cache_dir):
                if filename.endswith(".json"):
                    filepath = os.path.join(self.cache_config.cache_dir, filename)
                    file_age = time.time() - os.path.getmtime(filepath)
                    cache_files.append((filepath, file_age))

            # Sort by age (oldest first)
            cache_files.sort(key=lambda x: x[1])

            # Remove old files if cache is too large
            while len(cache_files) > self.cache_config.max_cache_size:
                oldest_file, _ = cache_files.pop(0)
                try:
                    os.remove(oldest_file)
                    self.logger.info(f"Removed old cache file: {oldest_file}")
                except Exception as e:
                    self.logger.error(f"Error removing cache file {oldest_file}: {e}")

        except Exception as e:
            self.logger.error(f"Error cleaning up cache: {e}")


def create_model_manager(
    logger: logging.Logger, config: Optional[Dict] = None
) -> ModelManager:
    """
    Create a model manager with configuration from config file or defaults.

    Args:
        logger: Logger instance
        config: Configuration dictionary (optional, will load from config file if not provided)

    Returns:
        Configured ModelManager instance
    """
    if config is None:
        # Load configuration from config file
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                config = json.load(f)
        else:
            # Use default configuration
            config = {
                "model_management": {
                    "cache": {
                        "cache_dir": "artifacts/model_cache",  # Cache directory (separate from model artifacts)
                        "max_cache_size": 50,
                        "cache_expiry_days": 30,
                    },
                    "retrain": {
                        "retrain_days": 90,
                        "retrain_msg_growth": 0.2,
                        "retrain_coherence_threshold": 0.3,
                        "retrain_perplexity_threshold": 2.0,
                    },
                    "reuse": {
                        "parameter_tolerance": 0.1,
                        "max_similar_models": 5,
                        "enable_model_reuse": True,
                    },
                }
            }

    # Extract model management configuration
    model_mgmt_config = config.get("model_management", {})
    cache_config = model_mgmt_config.get("cache", {})
    retrain_config = model_mgmt_config.get("retrain", {})

    # Create cache configuration
    cache = ModelCache(
        cache_dir=cache_config.get("cache_dir", "artifacts/model_cache"),  # Cache directory
        max_cache_size=cache_config.get("max_cache_size", 50),
        cache_expiry_days=cache_config.get("cache_expiry_days", 30),
    )

    # Create retrain configuration
    retrain = RetrainConfig(
        retrain_days=retrain_config.get("retrain_days", 90),
        retrain_msg_growth=retrain_config.get("retrain_msg_growth", 0.2),
        retrain_coherence_threshold=retrain_config.get(
            "retrain_coherence_threshold", 0.3
        ),
        retrain_perplexity_threshold=retrain_config.get(
            "retrain_perplexity_threshold", 2.0
        ),
    )

    return ModelManager(logger, cache, retrain)
