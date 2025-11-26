import logging
import os
import re
import uuid
import datetime
import json
import hashlib

import sqlalchemy as s
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import nltk
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from collections import OrderedDict
from textblob import TextBlob
from collections import Counter
from sklearn.decomposition import NMF

# Import for coherence score calculation
try:
    from gensim.models import CoherenceModel
    from gensim.corpora import Dictionary
    from gensim import utils
    GENSIM_AVAILABLE = True
except ImportError:
    GENSIM_AVAILABLE = False

from augur.tasks.init.celery_app import celery_app as celery
from augur.application.db.lib import get_value, get_session, get_repo_by_repo_git
from augur.application.db.models import RepoClusterMessage, TopicWord, TopicModelMeta, RepoTopic
from augur.tasks.init.celery_app import AugurMlRepoCollectionTask


MODEL_FILE_NAME = "kmeans_repo_messages"
stemmer = nltk.stem.snowball.SnowballStemmer("english")

# --- Configuration Loading ---
# This section loads configuration from config.json file if available,
# otherwise falls back to database configuration.
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

# --- RETRAIN DECISION LOGIC ---
# Complete should_retrain logic based on 4 dimensions: Age, Params, Quality, Data

def should_retrain_by_age(latest_model, retrain_days, logger):
    """
    Check if model needs retraining based on age.
    
    Args:
        latest_model: TopicModelMeta object from database
        retrain_days: Maximum days before model is considered too old
        logger: Logger instance
    
    Returns:
        bool: True if model is too old and needs retraining
    """
    try:
        if not latest_model or not latest_model.training_end_time:
            logger.info("No existing model or training time found - retrain needed")
            return True
            
        model_age_days = (datetime.datetime.now() - latest_model.training_end_time).days
        logger.info(f"Model age: {model_age_days} days, threshold: {retrain_days} days")
        
        if model_age_days > retrain_days:
            logger.info(f"Model is too old ({model_age_days} > {retrain_days} days) - retrain needed")
            return True
        
        logger.info(f"Model age is acceptable ({model_age_days} <= {retrain_days} days)")
        return False
            
    except Exception as e:
        logger.warning(f"Error checking model age: {e} - defaulting to retrain")
        return True

def should_retrain_by_params(latest_model, new_params, logger):
    """
    Check if model needs retraining based on parameter changes.
    
    Args:
        latest_model: TopicModelMeta object from database
        new_params: Dictionary of current training parameters
        logger: Logger instance
    
    Returns:
        bool: True if parameters have changed and retraining is needed
    """
    try:
        if not latest_model or not latest_model.parameters_hash:
            logger.info("No existing model or parameters hash found - retrain needed")
            return True
            
        # Calculate current parameters hash
        params_str = json.dumps(new_params, sort_keys=True)
        current_hash = hashlib.md5(params_str.encode()).hexdigest()
        
        logger.info(f"Current params hash: {current_hash}")
        logger.info(f"Stored params hash: {latest_model.parameters_hash}")
        
        if current_hash != latest_model.parameters_hash:
            logger.info("Parameters have changed - retrain needed")
            return True
        
        logger.info("Parameters unchanged")
        return False
            
    except Exception as e:
        logger.warning(f"Error checking parameter changes: {e} - defaulting to retrain")
        return True

def should_retrain_by_quality(latest_model, quality_threshold, logger):
    """
    Check if model needs retraining based on quality metrics.
    
    Args:
        latest_model: TopicModelMeta object from database
        quality_threshold: Minimum acceptable coherence score (default: 0.3)
        logger: Logger instance
    
    Returns:
        bool: True if model quality is below threshold and retraining is needed
    """
    try:
        if not latest_model:
            logger.info("No existing model found - retrain needed")
            return True
            
        coherence_score = latest_model.coherence_score or 0.0
        logger.info(f"Model coherence score: {coherence_score}, threshold: {quality_threshold}")
        
        if coherence_score < quality_threshold:
            logger.info(f"Model quality too low ({coherence_score} < {quality_threshold}) - retrain needed")
            return True
        
        logger.info(f"Model quality acceptable ({coherence_score} >= {quality_threshold})")
        return False
            
    except Exception as e:
        logger.warning(f"Error checking model quality: {e} - defaulting to retrain")
        return True

def should_retrain_by_data(latest_model, current_message_count, growth_threshold, logger):
    """
    Check if model needs retraining based on data growth.
    
    Args:
        latest_model: TopicModelMeta object from database
        current_message_count: Current number of messages in repository
        growth_threshold: Minimum growth percentage to trigger retrain (default: 0.2 = 20%)
        logger: Logger instance
    
    Returns:
        bool: True if data has grown significantly and retraining is needed
    """
    try:
        if not latest_model or not latest_model.training_message_count:
            logger.info("No existing model or training message count found - retrain needed")
            return True
            
        training_count = latest_model.training_message_count
        logger.info(f"Training message count: {training_count}, current count: {current_message_count}")
        
        if training_count == 0:
            logger.info("Previous training count is 0 - retrain needed")
            return True
            
        growth_rate = (current_message_count - training_count) / training_count
        logger.info(f"Data growth rate: {growth_rate:.2%}, threshold: {growth_threshold:.2%}")
        
        if growth_rate > growth_threshold:
            logger.info(f"Data growth significant ({growth_rate:.2%} > {growth_threshold:.2%}) - retrain needed")
            return True
        
        logger.info(f"Data growth acceptable ({growth_rate:.2%} <= {growth_threshold:.2%})")
        return False
            
    except Exception as e:
        logger.warning(f"Error checking data growth: {e} - defaulting to retrain")
        return True

def should_retrain_model(repo_id, new_params, current_message_count, retrain_days, growth_threshold, quality_threshold, logger):
    """
    Comprehensive retrain decision logic combining all 4 dimensions.
    
    Args:
        repo_id: Repository ID to check
        new_params: Current training parameters
        current_message_count: Current number of messages
        retrain_days: Maximum model age in days
        growth_threshold: Data growth threshold (e.g., 0.2 for 20%)
        quality_threshold: Minimum quality threshold (e.g., 0.3)
        logger: Logger instance
    
    Returns:
        tuple: (should_retrain: bool, reasons: list)
    """
    try:
        with get_session() as session:
            # Get the latest model for this repository
            latest_model = session.query(TopicModelMeta).filter_by(
                repo_id=repo_id
            ).order_by(TopicModelMeta.training_end_time.desc()).first()
            
            logger.info(f"Checking retrain conditions for repo {repo_id}")
            
            reasons = []
            
            # Check all 4 dimensions
            if should_retrain_by_age(latest_model, retrain_days, logger):
                reasons.append("Age: Model is too old")
                
            if should_retrain_by_params(latest_model, new_params, logger):
                reasons.append("Params: Training parameters have changed")
                
            if should_retrain_by_quality(latest_model, quality_threshold, logger):
                reasons.append("Quality: Model quality below threshold")
                
            if should_retrain_by_data(latest_model, current_message_count, growth_threshold, logger):
                reasons.append("Data: Significant data growth detected")
            
            should_retrain = len(reasons) > 0
            
            if should_retrain:
                logger.info(f"RETRAIN NEEDED - Reasons: {'; '.join(reasons)}")
            else:
                logger.info("NO RETRAIN NEEDED - All conditions satisfied")
                
            return should_retrain, reasons
            
    except Exception as e:
        logger.error(f"Error in retrain decision logic: {e}")
        return True, ["Error: Unable to check retrain conditions"]


def replace_env_vars(value):
    """Replace environment variables in string values"""
    if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
        # Extract variable name and default value
        var_content = value[2:-1]  # Remove ${ and }
        if ':-' in var_content:
            var_name, default_value = var_content.split(':-', 1)
        else:
            var_name = var_content
            default_value = ''
        
        # Get environment variable or use default
        env_value = os.getenv(var_name, default_value)
        
        # Try to convert to appropriate type
        try:
            if default_value.isdigit():
                return int(env_value)
            if default_value.replace('.', '').isdigit():
                return float(env_value)
            return env_value
        except (ValueError, AttributeError):
            return env_value
    
    return value

def load_config_with_env_vars(config_dict):
    """Recursively replace environment variables in config dictionary"""
    if isinstance(config_dict, dict):
        for key, value in config_dict.items():
            config_dict[key] = load_config_with_env_vars(value)
    elif isinstance(config_dict, list):
        for i, item in enumerate(config_dict):
            config_dict[i] = load_config_with_env_vars(item)
    elif isinstance(config_dict, str):
        return replace_env_vars(config_dict)
    
    return config_dict


@celery.task(base=AugurMlRepoCollectionTask, bind=True, queue='ml')
def clustering_task(self, repo_git):

    logger = logging.getLogger(clustering_model.__name__)
    engine = self.app.engine

    clustering_model(repo_git, logger, engine)

def clustering_model(repo_git: str,logger,engine) -> None: 
    """
    Main entry for clustering and topic modeling on repository messages.
    
    AUTOMATIC INTELLIGENT RETRAIN SYSTEM:
    This function automatically decides whether to retrain or use existing models based on 4 dimensions:
    - Age: Model age vs retrain_days threshold (default: 90 days)
    - Params: Training parameter changes vs parameters_hash
    - Quality: Model coherence_score vs quality_threshold (default: 0.3)
    - Data: Message count growth vs retrain_msg_growth threshold (default: 20%)
    
    WORKFLOW:
    1. If no model exists -> Train new model
    2. If model exists -> Check 4 retrain conditions
    3. If any condition fails -> Retrain model
    4. If all conditions pass -> Use existing model
    
    This eliminates the need for manual retrain decisions and ensures models stay current automatically.
    
    Loads parameters from config.json if available, otherwise from database config table.
    Config parameters:
      - db: Database connection info (used for standalone runs)
      - topic_modeling.num_topics: Number of topics for NMF model (int)
      - topic_modeling.min_df: Min document frequency for vectorizer (int)
      - topic_modeling.max_df: Max document frequency for vectorizer (float)
      - topic_modeling.random_state: Random seed (int)
      - topic_modeling.coherence_metric: Coherence metric (str)
      - topic_modeling.retrain_days: Retrain if last model older than this (int, days)
      - topic_modeling.retrain_msg_growth: Retrain if message count grows by this fraction (float)
      - topic_modeling.quality_threshold: Retrain if coherence score below this (float, default: 0.3)
      - topic_modeling.output_dir: Where to save models/visualizations (str)
    """
    logger.info(f"Starting clustering analysis for {repo_git}")

    # Load topic modeling parameters from config.json or database
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
            # Replace environment variables in config
            config = load_config_with_env_vars(config)
            topic_cfg = config.get('Clustering_Task', {})
            num_topics = int(topic_cfg.get('num_topics', 8))
            min_df = int(topic_cfg.get('min_df', 2))
            max_df = float(topic_cfg.get('max_df', 0.8))
            max_features = int(topic_cfg.get('max_features', 1000))
            num_words_per_topic = int(topic_cfg.get('num_words_per_topic', 12))
            num_clusters = int(topic_cfg.get('num_clusters', 5))
            random_state = int(topic_cfg.get('random_state', 42))
            coherence_metric = topic_cfg.get('coherence_metric', 'c_v')
            retrain_days = int(topic_cfg.get('retrain_days', 90))
            retrain_msg_growth = float(topic_cfg.get('retrain_msg_growth', 0.2))
            quality_threshold = float(topic_cfg.get('quality_threshold', 0.3))
            output_dir = topic_cfg.get('output_dir', 'database')  # Store in database, not artifacts
            ngram_range = (1, 4)  # Default ngram range
            clustering_by_content = True
            clustering_by_mechanism = False
            logger.info("Configuration loaded from config.json file")
    else:
        # Fallback to database configuration
        num_topics = get_value("Clustering_Task", 'num_topics') or 8
        min_df = get_value("Clustering_Task", 'min_df') or 2
        max_df = get_value("Clustering_Task", 'max_df') or 0.8
        max_features = get_value("Clustering_Task", 'max_features') or 1000
        num_words_per_topic = get_value("Clustering_Task", 'num_words_per_topic') or 12
        num_clusters = get_value("Clustering_Task", 'num_clusters') or 5
        random_state = get_value("Clustering_Task", 'random_state') or 42
        coherence_metric = get_value("Clustering_Task", 'coherence_metric') or 'c_v'
        retrain_days = get_value("Clustering_Task", 'retrain_days') or 90
        retrain_msg_growth = get_value("Clustering_Task", 'retrain_msg_growth') or 0.2
        quality_threshold = get_value("Clustering_Task", 'quality_threshold') or 0.3
        output_dir = get_value("Clustering_Task", 'output_dir') or 'database'  # Store in database, not artifacts
        ngram_range = (1, 4)
        clustering_by_content = True
        clustering_by_mechanism = False
        logger.info("Configuration loaded from database")

    tool_source = 'Clustering Worker'
    tool_version = '0.3.0'
    data_source = 'Augur Collected Messages'

    repo_id = get_repo_by_repo_git(repo_git).repo_id

    logger.info(f"Min df: {min_df}. Max df: {max_df}")

    logger.info("If you did not install NLTK libraries when you installed Augur, this will fail. ")
    #nltk.download('all')

    logger.info(f"Getting repo messages for repo_id: {repo_id}")
    get_messages_for_repo_sql = s.sql.text(
        """
            SELECT
                r.repo_group_id,
                r.repo_id,
                r.repo_git,
                r.repo_name,
                i.issue_id thread_id,
                M.msg_text,
                i.issue_title thread_title,
                M.msg_id 
            FROM
                augur_data.repo r,
                augur_data.issues i,
                augur_data.message M,
                augur_data.issue_message_ref imr 
            WHERE
                r.repo_id = i.repo_id 
                AND imr.issue_id = i.issue_id 
                AND imr.msg_id = M.msg_id 
                AND r.repo_id = :repo_id 
            UNION
            SELECT
                r.repo_group_id,
                r.repo_id,
                        r.repo_git,
                r.repo_name,
                pr.pull_request_id thread_id,
                M.msg_text,
                pr.pr_src_title thread_title,
                M.msg_id 
            FROM
                augur_data.repo r,
                augur_data.pull_requests pr,
                augur_data.message M,
                augur_data.pull_request_message_ref prmr 
            WHERE
                r.repo_id = pr.repo_id 
                AND prmr.pull_request_id = pr.pull_request_id 
                AND prmr.msg_id = M.msg_id 
                AND r.repo_id = :repo_id
            """
    )
    # result = db.execute(delete_points_SQL, repo_id=repo_id, min_date=min_date)

    with engine.connect() as conn:
        msg_df_cur_repo = pd.read_sql(get_messages_for_repo_sql, conn, params={"repo_id": repo_id})
    logger.info(msg_df_cur_repo.head())
    logger.debug(f"Repo message df size: {len(msg_df_cur_repo.index)}")

    # Prepare current training parameters for retrain decision
    current_params = {
        "max_df": max_df,
        "min_df": min_df,
        "max_features": max_features,
        "ngram_range": ngram_range,
        "num_clusters": num_clusters,
        "num_topics": num_topics,
        "num_words_per_topic": num_words_per_topic
    }
    
    current_message_count = len(msg_df_cur_repo.index)
    
    logger.info("=" * 50)
    logger.info("INTELLIGENT RETRAIN DECISION SYSTEM")
    logger.info("=" * 50)
    
    # Use intelligent retrain decision logic
    should_retrain, retrain_reasons = should_retrain_model(
        repo_id=repo_id,
        new_params=current_params,
        current_message_count=current_message_count,
        retrain_days=retrain_days,
        growth_threshold=retrain_msg_growth,
        quality_threshold=quality_threshold,
        logger=logger
    )
    
    if should_retrain:
        logger.info(" RETRAINING MODEL")
        logger.info(f"Retrain reasons: {', '.join(retrain_reasons)}")
        train_model(logger, engine, max_df, min_df, max_features, ngram_range, num_clusters, num_topics, num_words_per_topic, tool_source, tool_version, data_source, repo_id)
        # train_model handles all model training, storage, and data persistence
        # No need for legacy clustering code below
        return
    
    # Using existing model - no retraining needed
        logger.info(" USING EXISTING MODEL")
        logger.info("All conditions satisfied - no retraining needed")
        
        # Load existing model information
        with get_session() as session:
            latest_model = session.query(TopicModelMeta).filter_by(
                repo_id=repo_id
            ).order_by(TopicModelMeta.training_end_time.desc()).first()
            
            if latest_model:
                logger.info(f" EXISTING MODEL INFO:")
                logger.info(f"   • Model ID: {latest_model.model_id}")
                logger.info(f"   • Method: {latest_model.model_method}")
                logger.info(f"   • Topics: {latest_model.num_topics}")
                logger.info(f"   • Coherence Score: {latest_model.coherence_score}")
                logger.info(f"   • Training Date: {latest_model.training_end_time}")
                logger.info(f"   • Training Messages: {latest_model.training_message_count}")
                logger.info(f"   • Age: {(datetime.datetime.now() - latest_model.training_end_time).days} days")
                
                # Model is already in database and working
                # No additional training or clustering needed
                logger.info("   • Model is ready for use via API endpoints")
                
                # Since model is good, we can skip the legacy clustering operations below
                logger.info("Skipping legacy clustering operations - using database model")
                return
            
            # This code path should be unreachable but kept for safety
            logger.warning("No existing model found despite retrain check - this shouldn't happen")
            logger.info("Falling back to training new model")
            train_model(logger, engine, max_df, min_df, max_features, ngram_range, num_clusters, num_topics, num_words_per_topic, tool_source, tool_version, data_source, repo_id)
            return

    # Legacy clustering code removed - train_model() handles all model training and data persistence
    # All topic modeling data (topics, vocabulary, repo_topic, repo_cluster_messages) 
    # is now stored in the database via train_model() function
    logger.debug("Clustering model workflow completed")


def get_tf_idf_matrix(text_list, max_df, max_features, min_df, ngram_range, logger):
    # Validate input parameters
    if hasattr(text_list, 'empty'):
        # For pandas Series/DataFrame
        if text_list.empty:
            raise ValueError("Text list cannot be empty")
    elif not text_list:
        # For regular lists/arrays
        raise ValueError("Text list cannot be empty")
    
    if max_df <= 0 or max_df > 1.0:
        raise ValueError("max_df must be between 0 and 1")
    
    if min_df < 0:
        raise ValueError("min_df must be non-negative")
    
    # For small datasets, allow min_df to be larger than max_df if min_df is an integer
    if isinstance(min_df, float) and max_df < min_df:
        raise ValueError("max_df must be >= min_df")
    
    logger.debug("Getting the tf idf matrix from function")
    
    # Smart parameter adjustment for small datasets
    num_docs = len(text_list)
    logger.debug(f"Dataset size: {num_docs} documents")
    
    # Adjust min_df for small datasets
    adjusted_min_df = min_df
    if isinstance(min_df, int) and min_df >= num_docs:
        adjusted_min_df = max(1, num_docs // 4)  # Use 25% of documents as threshold
        logger.warning(f"Adjusted min_df from {min_df} to {adjusted_min_df} for small dataset")
    
    # Adjust max_df if needed
    adjusted_max_df = max_df
    if isinstance(min_df, int) and max_df < 1.0:
        min_docs_for_max_df = int(num_docs * max_df)
        if min_docs_for_max_df < adjusted_min_df:
            # For single document case, use 1.0 to include all terms
            adjusted_max_df = 1.0 if num_docs == 1 else 0.95
            logger.warning(f"Adjusted max_df from {max_df} to {adjusted_max_df} to avoid conflict with min_df")
    
    try:
        tfidf_vectorizer = TfidfVectorizer(max_df=adjusted_max_df, max_features=max_features,
                                           min_df=adjusted_min_df, stop_words='english',
                                           use_idf=True, tokenizer=preprocess_and_tokenize,
                                           ngram_range=ngram_range)
        tfidf_transformer = tfidf_vectorizer.fit(text_list)
        tfidf_matrix = tfidf_transformer.transform(text_list)
        logger.info(f"TF-IDF successful with adjusted parameters: min_df={adjusted_min_df}, max_df={adjusted_max_df}")
    except ValueError as e:
        # Fallback to very conservative parameters
        logger.warning(f"TF-IDF failed with adjusted parameters: {e}")
        logger.warning("Using fallback parameters: min_df=1, max_df=0.95")
        tfidf_vectorizer = TfidfVectorizer(max_df=0.95, max_features=max_features,
                                           min_df=1, stop_words='english',
                                           use_idf=True, tokenizer=preprocess_and_tokenize,
                                           ngram_range=ngram_range)
        tfidf_transformer = tfidf_vectorizer.fit(text_list)
        tfidf_matrix = tfidf_transformer.transform(text_list)
    # vocabulary will be stored in database, not as local file
    return tfidf_matrix, tfidf_vectorizer.get_feature_names_out()

def cluster_and_label(feature_matrix, num_clusters, logger=None):
    # Validate input parameters
    if feature_matrix is None:
        raise ValueError("Feature matrix cannot be None")
    
    if num_clusters <= 0:
        raise ValueError("Number of clusters must be positive")
    
    num_samples = feature_matrix.shape[0]
    
    # Smart cluster adjustment for small datasets
    adjusted_clusters = num_clusters
    if num_samples < num_clusters:
        adjusted_clusters = max(1, num_samples)  # Use all samples as separate clusters
        if logger:
            logger.warning(f"Adjusted number of clusters from {num_clusters} to {adjusted_clusters} for small dataset with {num_samples} samples")
    elif num_samples < 10 and num_clusters > num_samples // 2:
        # For very small datasets, use conservative clustering
        adjusted_clusters = max(1, num_samples // 2)
        if logger:
            logger.warning(f"Adjusted number of clusters from {num_clusters} to {adjusted_clusters} for very small dataset")
    
    if adjusted_clusters == 1:
        # Special case: only one cluster, all samples belong to cluster 0
        if logger:
            logger.info("Using single cluster for all samples")
        return [0] * num_samples
    
    try:
        kmeans_model = KMeans(n_clusters=adjusted_clusters, random_state=42, n_init=10)
        kmeans_model.fit(feature_matrix)
        labels = kmeans_model.labels_.tolist()
        if logger:
            logger.info(f"K-means clustering successful with {adjusted_clusters} clusters for {num_samples} samples")
        return labels
    except Exception as e:
        # Fallback: assign each sample to its own cluster (up to available samples)
        if logger:
            logger.warning(f"K-means clustering failed: {e}. Using fallback: each sample as separate cluster")
        return list(range(min(num_samples, adjusted_clusters)))

def count_func(msg):
    # Handle None or empty input
    if msg is None or not isinstance(msg, str):
        raise TypeError("Input must be a non-empty string")
    
    if not msg.strip():
        return {}
    
    blobed = TextBlob(msg)
    counts = Counter(tag for word, tag in blobed.tags if
                     tag not in ['NNPS', 'RBS', 'SYM', 'WP$', 'LS', 'POS', 'RP', 'RBR', 'JJS', 'UH', 'FW', 'PDT'])
    total = sum(counts.values())
    if total == 0:
        return {}
    normalized_count = {key: value / total for key, value in counts.items()}
    return normalized_count

def preprocess_and_tokenize(text):
    text = text.lower()
    text = re.sub(r'[@]\w+', '', text)
    text = re.sub(r'[^A-Za-z]+', ' ', text)

    tokens = nltk.word_tokenize(text)
    tokens = [token for token in tokens if len(token) > 1]
    stems = [stemmer.stem(t) for t in tokens]
    return stems



def calculate_nmf_interpretability(nmf_model, document_term_matrix, logger):
    """
    Calculate NMF interpretability using reconstruction error.
    Lower reconstruction error = higher interpretability
    
    Args:
        nmf_model: Trained NMF model
        document_term_matrix: Original document-term matrix
        logger: Logger instance
    
    Returns:
        float: Interpretability score (0-1, higher is better)
    """
    try:
        # Calculate reconstruction error
        W = nmf_model.transform(document_term_matrix)  # Document-topic matrix
        H = nmf_model.components_  # Topic-word matrix
        reconstructed = W @ H  # Reconstruct original matrix
        
        # Calculate normalized reconstruction error
        original_norm = np.linalg.norm(document_term_matrix.toarray())
        error_norm = np.linalg.norm(document_term_matrix.toarray() - reconstructed)
        
        # Convert to interpretability score (1 - normalized_error)
        if original_norm > 0:
            normalized_error = error_norm / original_norm
            interpretability = max(0.0, 1.0 - normalized_error)
        else:
            interpretability = 0.0
            
        logger.info(f"NMF Interpretability (reconstruction-based): {interpretability:.4f}")
        return round(interpretability, 4)
        
    except Exception as e:
        logger.warning(f"Failed to calculate NMF interpretability: {e}")
        return 0.0


def calculate_topic_sparsity(topic_list, logger):
    """
    Calculate topic sparsity - a key advantage of NMF.
    Higher sparsity = better interpretability
    
    Args:
        topic_list: List of topic arrays from NMF
        logger: Logger instance
    
    Returns:
        float: Average sparsity score (0-1, higher is better)
    """
    try:
        sparsity_scores = []
        
        for topic in topic_list:
            # Calculate sparsity as percentage of near-zero elements
            total_elements = len(topic)
            near_zero_elements = np.sum(topic < 0.01)  # Elements close to zero
            sparsity = near_zero_elements / total_elements if total_elements > 0 else 0.0
            sparsity_scores.append(sparsity)
        
        average_sparsity = np.mean(sparsity_scores) if sparsity_scores else 0.0
        logger.info(f"NMF Topic Sparsity (higher = more interpretable): {average_sparsity:.4f}")
        return round(average_sparsity, 4)
        
    except Exception as e:
        logger.warning(f"Failed to calculate topic sparsity: {e}")
        return 0.0


def calculate_real_coherence_score(texts, nmf_model, vectorizer, logger):
    """
    Calculate real coherence score using Gensim's CoherenceModel.
    This is the standard metric for evaluating topic model quality.
    
    Args:
        texts: List of text documents (strings)
        nmf_model: Trained NMF model
        vectorizer: Fitted CountVectorizer used for training
        logger: Logger instance
    
    Returns:
        float: Coherence score (higher is better, typically 0.3-0.7 is good)
    """
    try:
        if not GENSIM_AVAILABLE:
            logger.warning("Gensim not available for coherence calculation, using fallback")
            return calculate_nmf_interpretability(nmf_model, vectorizer.transform(texts), logger)
            
        if not texts or not nmf_model or not vectorizer:
            logger.warning("Insufficient data for coherence calculation")
            return 0.0
        
        # Preprocess texts for gensim
        processed_texts = []
        for text in texts:
            if text and isinstance(text, str):
                # Simple tokenization and cleaning
                words = utils.simple_preprocess(text, min_len=2, max_len=15)
                if words:  # Only add non-empty word lists
                    processed_texts.append(words)
        
        if len(processed_texts) == 0:
            logger.warning("No valid texts after preprocessing")
            return 0.0
        
        # Create dictionary from processed texts
        dictionary = Dictionary(processed_texts)
        
        # Get feature names from vectorizer
        feature_names = vectorizer.get_feature_names_out()
        
        # Extract topic words from NMF model
        topics = []
        for topic_idx in range(nmf_model.n_components):
            topic = nmf_model.components_[topic_idx]
            # Get top 10 words for this topic
            top_word_indices = topic.argsort()[-10:][::-1]
            topic_words = [feature_names[i] for i in top_word_indices]
            topics.append(topic_words)
        
        if len(topics) == 0:
            logger.warning("No valid topics extracted for coherence calculation")
            return 0.0
        
        # Calculate coherence using C_V measure (most commonly used)
        coherence_model = CoherenceModel(
            topics=topics,
            texts=processed_texts,
            dictionary=dictionary,
            coherence='c_v'
        )
        
        coherence_score = coherence_model.get_coherence()
        logger.info(f"Real Coherence Score (C_V): {coherence_score:.4f}")
        
        # Normalize to 0-1 range and ensure valid output
        normalized_score = max(0.0, min(1.0, coherence_score)) if coherence_score is not None else 0.0
        return round(normalized_score, 4)
        
    except Exception as e:
        logger.warning(f"Real coherence calculation failed: {e}")
        # Fallback to reconstruction-based score
        return calculate_nmf_interpretability(nmf_model, vectorizer.transform(texts), logger)


def train_model(logger, engine, max_df, min_df, max_features, ngram_range, num_clusters, num_topics, num_words_per_topic, tool_source, tool_version, data_source, repo_id=None):
    def visualize_labels_PCA(features, labels, annotations, num_components, title):
        labels_color_map = {-1: "red"}
        for label in labels:
            labels_color_map[label] = [list([x / 255.0 for x in list(np.random.choice(range(256), size=3))])]
        low_dim_data = PCA(n_components=num_components).fit_transform(features)

        fig, ax = plt.subplots(figsize=(20, 10))

        for i, data in enumerate(low_dim_data):
            pca_comp_1, pca_comp_2 = data
            color = labels_color_map[labels[i]]
            ax.scatter(pca_comp_1, pca_comp_2, c=color, label=labels[i])
        # ax.annotate(annotations[i],(pca_comp_1, pca_comp_2))

        handles, labels = ax.get_legend_handles_labels()
        handles_label_dict = OrderedDict(zip(labels, handles))
        ax.legend(handles_label_dict.values(), handles_label_dict.keys())

        plt.title(title)
        plt.xlabel("PCA Component 1")
        plt.ylabel("PCA Component 2")
        # plt.show()
        filename = labels + "_PCA.png"
        plt.savefig(filename)

    get_messages_sql = s.sql.text(
        """
        SELECT r.repo_group_id, r.repo_id, r.repo_git, r.repo_name, i.issue_id thread_id,m.msg_text,i.issue_title thread_title,m.msg_id
        FROM augur_data.repo r, augur_data.issues i,
        augur_data.message m, augur_data.issue_message_ref imr
        WHERE r.repo_id=i.repo_id
        AND imr.issue_id=i.issue_id
        AND imr.msg_id=m.msg_id
        AND r.repo_id = :repo_id
        UNION
        SELECT r.repo_group_id, r.repo_id, r.repo_git, r.repo_name, pr.pull_request_id thread_id,m.msg_text,pr.pr_src_title thread_title,m.msg_id
        FROM augur_data.repo r, augur_data.pull_requests pr,
        augur_data.message m, augur_data.pull_request_message_ref prmr
        WHERE r.repo_id=pr.repo_id
        AND prmr.pull_request_id=pr.pull_request_id
        AND prmr.msg_id=m.msg_id
        AND r.repo_id = :repo_id
        """
    )

    with engine.connect() as conn:
        msg_df_all = pd.read_sql(get_messages_sql, conn, params={"repo_id": repo_id})

        # select only highly active repos
        logger.debug("Selecting highly active repos")
        msg_df_filtered = msg_df_all.groupby("repo_id").filter(lambda x: len(x) > 200)
        
        # Check if we have any data after filtering
        if msg_df_filtered.empty:
            logger.warning("No repositories with enough messages (>200) found, using less restrictive filter")
            # Fallback to repos with at least 50 messages
            msg_df_filtered = msg_df_all.groupby("repo_id").filter(lambda x: len(x) > 50)
            
            if msg_df_filtered.empty:
                logger.warning("No repositories with enough messages (>50) found, using all available data")
                # Use all available data as last resort
                msg_df_filtered = msg_df_all
        
        msg_df_all = msg_df_filtered

    # Topic modeling should be done at message level, not repo level
    # Each message is a document, not the entire repo
    logger.debug("Using messages as individual documents for topic modeling")
    
    # Ensure we have data to work with
    if msg_df_all.empty:
        raise ValueError("No message data available for training")

    # dataframe summarizing total message count in a repository
    logger.debug("Summarizing total message count in a repo")
    message_desc_df = msg_df_all[["repo_id", "repo_git", "repo_name", "msg_id"]].groupby(
        ["repo_id", "repo_git", "repo_name"]).agg('count').reset_index()
    message_desc_df.columns = ["repo_id", "repo_git", "repo_name", "message_count"]
    logger.info(f"Total messages: {len(msg_df_all)}, Repos: {len(message_desc_df)}")

    # For clustering, we can still group by repo (optional, for repo-level clustering)
    # But for topic modeling, we use individual messages
    msg_df_for_clustering = msg_df_all.groupby('repo_id')['msg_text'].apply(','.join).reset_index()
    tfidf_matrix, features = get_tf_idf_matrix(msg_df_for_clustering['msg_text'], max_df, max_features, min_df,
                                                    ngram_range, logger)
    msg_df_for_clustering['cluster'] = cluster_and_label(tfidf_matrix, num_clusters, logger)

    # Count Vectorizer for NMF topic modeling
    logger.debug("Calling CountVectorizer for NMF topic modeling")
    
    # Apply same smart parameter adjustment for CountVectorizer
    # Use individual messages, not merged repos
    num_docs_count = len(msg_df_all)
    logger.debug(f"CountVectorizer dataset size: {num_docs_count} messages (documents)")
    
    # Adjust parameters for CountVectorizer
    count_min_df = min_df
    if isinstance(min_df, int) and min_df >= num_docs_count:
        count_min_df = max(1, num_docs_count // 4)
        logger.warning(f"CountVectorizer: Adjusted min_df from {min_df} to {count_min_df}")
    
    count_max_df = max_df
    if isinstance(min_df, int) and max_df < 1.0:
        min_docs_for_count_max_df = int(num_docs_count * max_df)
        if min_docs_for_count_max_df < count_min_df:
            # For single document case, use 1.0 to include all terms
            count_max_df = 1.0 if num_docs_count == 1 else 0.95
            logger.warning(f"CountVectorizer: Adjusted max_df from {max_df} to {count_max_df}")
    
    try:
        count_vectorizer = CountVectorizer(max_df=count_max_df, max_features=min(max_features, 500), min_df=count_min_df,
                                           stop_words="english", tokenizer=preprocess_and_tokenize,
                                           ngram_range=(1, 2))
        # Fit and transform on individual messages, not merged repos
        count_transformer = count_vectorizer.fit(msg_df_all['msg_text'])
        count_matrix = count_transformer.transform(msg_df_all['msg_text'])
        logger.info(f"CountVectorizer successful with adjusted parameters: min_df={count_min_df}, max_df={count_max_df}")
    except ValueError as e:
        # Fallback to very conservative parameters
        logger.warning(f"CountVectorizer failed with adjusted parameters: {e}")
        logger.warning("CountVectorizer using fallback parameters: min_df=1, max_df=0.95")
        count_vectorizer = CountVectorizer(max_df=0.95, max_features=min(max_features, 500), min_df=1,
                                           stop_words="english", tokenizer=preprocess_and_tokenize,
                                           ngram_range=(1, 2))
        count_transformer = count_vectorizer.fit(msg_df_all['msg_text'])
        count_matrix = count_transformer.transform(msg_df_all['msg_text'])
    # vocabulary_count will be stored in database, not as local file
    feature_names = count_vectorizer.get_feature_names_out()

    logger.debug("Training NMF model for topic modeling")
    
    # Smart topic number adjustment for small datasets
    num_features = len(feature_names)
    num_docs_nmf = count_matrix.shape[0]
    
    adjusted_topics = num_topics
    max_possible_topics = min(num_features, num_docs_nmf)
    
    if num_topics > max_possible_topics:
        adjusted_topics = max(1, max_possible_topics)
        logger.warning(f"Adjusted number of topics from {num_topics} to {adjusted_topics} (max possible with {num_docs_nmf} docs and {num_features} features)")
    elif num_docs_nmf < 10 and num_topics > num_docs_nmf // 2:
        # For very small datasets, use conservative topic modeling
        adjusted_topics = max(1, num_docs_nmf // 2)
        logger.warning(f"Adjusted number of topics from {num_topics} to {adjusted_topics} for very small dataset")
    
    try:
        nmf_model = NMF(n_components=adjusted_topics, random_state=42, max_iter=100, tol=0.01)
        nmf_model.fit(count_matrix)
        logger.info(f"NMF model successful with {adjusted_topics} topics for {num_docs_nmf} documents and {num_features} features")
    except Exception as e:
        # Fallback to single topic
        logger.warning(f"NMF model failed with {adjusted_topics} topics: {e}. Using fallback: single topic")
        adjusted_topics = 1
        nmf_model = NMF(n_components=1, random_state=42, max_iter=100, tol=0.01)
        nmf_model.fit(count_matrix)
    topic_list = nmf_model.components_

    logging.info(f"NMF Topic List Created: {topic_list}")
    # NMF model will be stored in database, not as local file
    logging.info("NMF model will be stored in database")

    # Save topics to DB
    with get_session() as session:
        topic_id = 1
        for topic in topic_list:
            for i in topic.argsort()[:-num_words_per_topic - 1:-1]:
                record = {
                    'topic_id': int(topic_id),
                    'word': feature_names[i],
                    'tool_source': tool_source,
                    'tool_version': tool_version,
                    'data_source': data_source
                }
                topic_word_obj = TopicWord(**record)
                session.add(topic_word_obj)
                session.commit()
                logger.info(
                    "Primary key inserted into the topic_words table: {}".format(topic_word_obj.topic_words_id))
            topic_id += 1
    
    # Predict topic distribution for each message (not repo)
    logger.debug(f'entering prediction in model training, count_matrix is {count_matrix.shape}')
    prediction = nmf_model.transform(count_matrix)  # Shape: (num_messages, num_topics)
    logger.info(f"Prediction shape: {prediction.shape} (messages x topics)")
    
    # Aggregate message-level topic distributions to repo level
    # Group by repo_id and average the topic probabilities
    logger.debug('Aggregating message-level topic distributions to repo level')
    
    # Create a DataFrame with message-level predictions
    message_topic_df = pd.DataFrame(
        prediction,
        index=msg_df_all.index
    )
    message_topic_df['repo_id'] = msg_df_all['repo_id'].values
    
    # Aggregate by repo_id: average topic probabilities
    repo_topic_df = message_topic_df.groupby('repo_id').mean().reset_index()
    
    # Create topic_model_dict_list for compatibility
    topic_model_dict_list = []
    for _, row in repo_topic_df.iterrows():
        topic_model_dict = {'repo_id': int(row['repo_id'])}
        for j in range(int(adjusted_topics)):
            topic_model_dict[f"topic{j + 1}"] = float(row[j])
        topic_model_dict_list.append(topic_model_dict)
    
    topic_model_df = pd.DataFrame(topic_model_dict_list)
    
    # Join with message description
    result_content_df = topic_model_df.set_index('repo_id').join(message_desc_df.set_index('repo_id'))
    result_content_df = result_content_df.reset_index()
    logger.info(f"Aggregated topic distributions for {len(result_content_df)} repos")
    logger.debug(result_content_df.head())

    # Generate model ID and prepare metadata for database-only storage
    model_id = str(uuid.uuid4())
    start_time = datetime.datetime.now()
    
    # Prepare metadata for database storage (no file artifacts)
    meta_json = {
        "model_id": model_id,
        "model_type": "NMF_COUNT",
        "num_topics": int(adjusted_topics),
        "model_parameters": {
            "max_df": max_df,
            "min_df": min_df,
            "max_features": max_features,
            "ngram_range": ngram_range,
            "num_clusters": num_clusters,
            "num_words_per_topic": int(num_words_per_topic),
            "adjusted_topics": int(adjusted_topics)
        },
        "model_file_paths": {
            "nmf_model": None,  # No file storage - data in database
            "vocab": None        # No file storage - data in database
        },
        "training_start_time": str(start_time),
        "training_end_time": str(datetime.datetime.now()),
        "tool_source": tool_source,
        "tool_version": tool_version,
        "data_source": data_source
    }
    
    logger.info(f"Model {model_id} - all data will be stored directly in database")
    # Prepare visualization data for direct database storage
    topic_viz_data = {
            "topics": {},
        "topic_words": {},
        "vocabulary": feature_names.tolist(),  # Save complete vocabulary for reconstruction
        "model_info": {
            "model_id": model_id,
            "model_type": "NMF_COUNT",
            "num_topics": int(adjusted_topics),
            "training_params": meta_json["model_parameters"]
        }
    }
    
    # Add topic information to visualization data
    for i, topic_vector in enumerate(topic_list):
        topic_id = i + 1
        topic_words = []
        
        # Get top words for this topic
        top_word_indices = topic_vector.argsort()[-num_words_per_topic:][::-1]
        for word_idx in top_word_indices:
            if word_idx < len(feature_names):
                word = feature_names[word_idx]
                weight = topic_vector[word_idx]
                topic_words.append({"word": word, "weight": float(weight)})
        
        topic_viz_data["topics"][f"topic_{topic_id}"] = {
            "id": topic_id,
            "words": topic_words
        }
    
    # Write topic_model_meta ORM record with visualization_data
    try:
        with get_session() as session:
            # Use passed repo_id parameter or find from message data
            if repo_id is not None:
                repo_id = int(repo_id)
            elif not msg_df_all.empty:
                repo_id = int(msg_df_all.iloc[0]['repo_id'])
            else:
                repo_id = None
                
            # Calculate parameters hash
            params_str = json.dumps(meta_json["model_parameters"], sort_keys=True)
            parameters_hash = hashlib.md5(params_str.encode()).hexdigest()
            
            # Calculate data fingerprint
            data_fingerprint = {
                "repo_id": repo_id,
                "message_count": len(msg_df_all),
                "data_hash": hashlib.md5(str(msg_df_all['msg_text'].tolist()).encode()).hexdigest()
            }
            
            training_end_time = datetime.datetime.now()
            
            topic_model_meta = TopicModelMeta(
                model_id=model_id,
                repo_id=repo_id,
                model_method="NMF_COUNT",
                num_topics=int(adjusted_topics),
                num_words_per_topic=int(num_words_per_topic),
                training_parameters=meta_json["model_parameters"],
                model_file_paths=meta_json["model_file_paths"],
                parameters_hash=parameters_hash,
                coherence_score=calculate_real_coherence_score(msg_df_all['msg_text'].tolist(), nmf_model, count_vectorizer, logger),  # Real coherence score
                perplexity_score=0.0,  # For detail page calculation
                topic_diversity=calculate_topic_sparsity(topic_list, logger),  # NMF sparsity
                quality={},  # Will be populated later
                training_message_count=len(msg_df_all),
                data_fingerprint=data_fingerprint,
                visualization_data=topic_viz_data,  # Add visualization data
                training_start_time=start_time,
                training_end_time=training_end_time,
                tool_source=tool_source,
                tool_version=tool_version,
                data_source=data_source
            )
            session.add(topic_model_meta)
            session.commit()
            logger.info(f"Topic model {model_id} with visualization data saved to database")
            
            # Write repo_topic data - repository-topic associations
            logger.info("Writing repo_topic data...")
            
            # Optional: Implement REPLACE strategy - delete old data for this repo
            if repo_id is not None:
                deleted_count = session.query(RepoTopic).filter(
                    RepoTopic.repo_id == repo_id,
                    RepoTopic.tool_source == tool_source,
                    RepoTopic.tool_version == tool_version
                ).delete(synchronize_session=False)
                if deleted_count > 0:
                    logger.info(f"Deleted {deleted_count} old repo_topic records for repo {repo_id}")
            
            # Bulk create RepoTopic objects using ORM
            # Use aggregated repo-level topic distributions
            repo_topic_objects = []
            for _, row in repo_topic_df.iterrows():
                repo_id_for_topic = int(row['repo_id'])
                for j in range(int(adjusted_topics)):
                    prob = float(row[j])
                    if prob > 0.01:  # Only store topics with probability > 1%
                        repo_topic_obj = RepoTopic(
                            repo_id=repo_id_for_topic,
                            topic_id=j + 1,
                            topic_prob=prob,
                            tool_source=tool_source,
                            tool_version=tool_version,
                            data_source=data_source
                        )
                        repo_topic_objects.append(repo_topic_obj)
            
            # Bulk insert using ORM
            if repo_topic_objects:
                session.bulk_save_objects(repo_topic_objects)
                logger.info(f"Bulk inserted {len(repo_topic_objects)} repo_topic records using ORM")
            else:
                logger.warning("No repo_topic records to insert (all probabilities <= 0.01)")
            
            # Write repo_cluster_messages data - clustered messages
            logger.info("Writing repo_cluster_messages data...")
            if 'cluster' in msg_df_for_clustering.columns and len(msg_df_for_clustering) > 0:
                # Optional: Delete old data for this repo
                if repo_id is not None:
                    deleted_count = session.query(RepoClusterMessage).filter(
                        RepoClusterMessage.repo_id == repo_id,
                        RepoClusterMessage.tool_source == tool_source,
                        RepoClusterMessage.tool_version == tool_version
                    ).delete(synchronize_session=False)
                    if deleted_count > 0:
                        logger.info(f"Deleted {deleted_count} old repo_cluster_messages records for repo {repo_id}")
                
                # Bulk create RepoClusterMessage objects using ORM
                cluster_objects = []
                for i, cluster_label in enumerate(msg_df_for_clustering['cluster']):
                    repo_id_for_cluster = int(msg_df_for_clustering.iloc[i]['repo_id'])
                    cluster_obj = RepoClusterMessage(
                        repo_id=repo_id_for_cluster,
                        cluster_content=int(cluster_label),
                        cluster_mechanism=1,  # K-means clustering
                        tool_source=tool_source,
                        tool_version=tool_version,
                        data_source=data_source
                    )
                    cluster_objects.append(cluster_obj)
                
                # Bulk insert using ORM
                if cluster_objects:
                    session.bulk_save_objects(cluster_objects)
                    logger.info(f"Bulk inserted {len(cluster_objects)} repo_cluster_messages records using ORM")
                else:
                    logger.warning("No cluster records to insert")
            else:
                logger.warning("Cluster column not found or msg_df is empty, skipping cluster data write")
            
            session.commit()
            logger.info(f"Completed writing all Topic Modeling data for model {model_id}")
            return model_id  # Return the model ID for optimization workflow
    except Exception as e:
        logger.warning(f"topic_model_meta DB write failed: {e}")
        raise  # Re-raise the exception so optimization knows training failed



