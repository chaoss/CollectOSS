import logging
import sqlalchemy as s
import pandas as pd
import pickle
import re
import nltk
from collections import Counter

from augur.tasks.init.celery_app import celery_app as celery
from augur.application.db.session import DatabaseSession
from augur.application.db.models import Repo, DiscourseInsight
from augur.application.db.engine import create_database_engine
from augur.application.db.util import execute_session_query

#import os, sys, time, requests, json
# from sklearn.model_selection import train_test_split
# from sklearn.feature_extraction.text import CountVectorizer
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.model_selection import cross_val_score
# import scipy
# import sklearn_crfsuite
# from sklearn_crfsuite import scorers
# from sklearn_crfsuite import metrics
# from sklearn.metrics import make_scorer
# from sklearn.model_selection import cross_val_score
# from sklearn.model_selection import RandomizedSearchCV
# from textblob import TextBlob
# from os import path

stemmer = nltk.stem.snowball.SnowballStemmer("english")

DISCOURSE_ANALYSIS_DIR = "augur/tasks/data_analysis/discourse_analysis/"

@celery.task
def discourse_analysis_model(repo_git: str) -> None:

    logger = logging.getLogger(discourse_analysis_model.__name__)

    tool_source = 'Discourse Worker'
    tool_version = '0.1.0'
    data_source = 'Analysis of Issue/PR Messages'

    with DatabaseSession(logger) as session:

        query = session.query(Repo).filter(Repo.repo_git == repo_git)
        repo_id = execute_session_query(query, 'one').repo_id

    get_messages_for_repo_sql = s.sql.text("""
                (SELECT r.repo_group_id, r.repo_id, r.repo_git, r.repo_name, i.issue_id thread_id,m.msg_text,i.issue_title thread_title,m.msg_id
                FROM augur_data.repo r, augur_data.issues i,
                augur_data.message m, augur_data.issue_message_ref imr
                WHERE r.repo_id=i.repo_id
                AND imr.issue_id=i.issue_id
                AND imr.msg_id=m.msg_id
                AND r.repo_id = :repo_id)
                UNION
                (SELECT r.repo_group_id, r.repo_id, r.repo_git, r.repo_name, pr.pull_request_id thread_id,m.msg_text,pr.pr_src_title thread_title,m.msg_id
                FROM augur_data.repo r, augur_data.pull_requests pr,
                augur_data.message m, augur_data.pull_request_message_ref prmr
                WHERE r.repo_id=pr.repo_id
                AND prmr.pull_request_id=pr.pull_request_id
                AND prmr.msg_id=m.msg_id
                AND r.repo_id = :repo_id)
            """)

    # result = db.execute(delete_points_SQL, repo_id=repo_id, min_date=min_date)
    msg_df_cur_repo = pd.read_sql(get_messages_for_repo_sql, create_database_engine(), params={"repo_id": repo_id})
    msg_df_cur_repo = msg_df_cur_repo.sort_values(by=['thread_id']).reset_index(drop=True)
    logger.info(msg_df_cur_repo.head())

    with open(DISCOURSE_ANALYSIS_DIR + "trained_crf_model", 'rb') as model_file:
        crf_model = pickle.load(model_file)

    with open(DISCOURSE_ANALYSIS_DIR + "word_to_emotion_map", 'rb') as emotion_map_file:
        word_to_emotion_map = pickle.load(emotion_map_file)

    with open(DISCOURSE_ANALYSIS_DIR + "tfidf_transformer", 'rb') as tfidf_transformer_file:
        tfidf_transformer = pickle.load(tfidf_transformer_file)

    logger.debug(f"msg_df_cur_repo before len: {len(msg_df_cur_repo)}")
    X_git, msg_df_cur_repo = create_features_for_structured_prediction(msg_df_cur_repo, 'msg_text', 'thread_id', logger, False, tfidf_transformer)
    logger.debug(f"msg_df_cur_repo after len: {len(msg_df_cur_repo)}")
    logger.debug(f"X_git len: {len(X_git)}")
    y_pred_git = crf_model.predict(X_git)
    logger.debug(f"y_pred_git len: {len(y_pred_git)}")
    y_pred_git_flat = [label for group in y_pred_git for label in group]
    logger.debug(f"y_pred_git_flat len: {len(y_pred_git_flat)}")
    msg_df_cur_repo['discourse_act'] = y_pred_git_flat

    with DatabaseSession(logger) as session:
        for index, row in msg_df_cur_repo.iterrows():
            record = {
                'msg_id': row['msg_id'],
                'discourse_act': row['discourse_act']
            }
            discourse_insight_object = DiscourseInsight(**record)
            session.add(discourse_insight_object)
            session.commit()
            # result = db.execute(discourse_insights_table.insert().values(record))
            logging.info(
                "Primary key inserted into the discourse_insights table: {}".format(discourse_insight_object.msg_discourse_id))

    logger.info("prediction: " + str(y_pred_git_flat))


def count_emotions(tokens, logger):

    with open(DISCOURSE_ANALYSIS_DIR + "word_to_emotion_map", 'rb') as emotion_map_file:
        word_to_emotion_map = pickle.load(emotion_map_file)
    count_dict = {}
    emotion_labels = ['anger', 'anticipation', 'disgust', 'fear', 'joy', 'negative', 'positive', 'sadness',
                      'surprise', 'trust']
    for label in emotion_labels:
        count_dict[label] = 0

    tokens = [token for token in tokens if len(token) > 1]
    stems = [stemmer.stem(t) for t in tokens]
    for stem in stems:
        if stem in word_to_emotion_map:
            emotions = word_to_emotion_map[stem]
            for emotion in emotions:
                count_dict[emotion] += 1
    return count_dict


def preprocess_text(text):
    text = re.sub('<[^<]+?>', '',
                  text.strip().lower().replace("\n", "").replace("\t", "").replace('/', ""))  # removing tags
    text = ''.join(c for c in text if not c.isdigit())  # removing digits
    return text

def create_features_for_structured_prediction(df, text_data_column_name, group_by_column_name, logger,
                                              label_available=True, tfidf_transformer=None):

    list_feature_dict = []
    invalid_text_indexes = []
    for text in df[text_data_column_name]:
        feature_dict = tfidf_transformer.transform([text]).todok()
        feature_dict_n = {}
        for key, value in feature_dict.items():
            feature_dict_n[str(key)] = value

        try:
            tokens = nltk.word_tokenize(text)
        except IndexError as e:
            logger.debug(f"Failed to tokenize: {text}. skipping...")

            df = df.drop(df[df[text_data_column_name] == text].index)
            invalid_text_indexes.extend(df.index[df[text_data_column_name] == text].tolist())
            continue

        text = preprocess_text(text)
        # new features
        emotion_count_dict = count_emotions(tokens, logger)
        # end emotion features
        feature_dict_n.update(emotion_count_dict)

        tags = nltk.pos_tag(tokens)
        counts = Counter(tag for word, tag in tags)
        pos_count_dict = dict(counts)
        normalized_count = {key: value / sum(pos_count_dict.values()) for key, value in pos_count_dict.items()}
        feature_dict_n.update(dict(normalized_count))

        # need to normalize the following
        feature_dict_n['num_sentences'] = len([word for word in text.split(".") if len(word) > 0])
        feature_dict_n['num_words'] = len(text.split(" "))
        feature_dict_n['num_characters'] = len(text)

        # end new features

        list_feature_dict.append(feature_dict_n)
    df['tfidf_features'] = list_feature_dict

    df_group_by_thread = df.groupby(group_by_column_name)
    X_all = []  # Each element is a list of features corresponding to messages in a thread
    if label_available: y_all = []  # Each element is a list of labels assigned to messages in a thread

    for name, group in df_group_by_thread:
        sentence_count = 0
        word_count = 0
        character_count = 0
        for ind, row in group.iterrows():
            sentence_count += row['tfidf_features']['num_sentences']
            word_count += row['tfidf_features']['num_words']
            character_count += row['tfidf_features']['num_characters']

        X_cur = []
        if label_available: y_cur = []
        for ind, row in group.iterrows():

            row['tfidf_features']['normalized_num_sentences'] = row['tfidf_features']['num_sentences'] / sentence_count if sentence_count != 0 else 0
            row['tfidf_features']['normalized_num_words'] = row['tfidf_features']['num_words'] / word_count  if word_count != 0 else 0
            row['tfidf_features']['normalized_num_characters'] = row['tfidf_features']['num_characters'] / character_count  if character_count != 0 else 0
            # print(row)
            X_cur.append(row['tfidf_features'])
            if label_available: y_cur.append(row['majority_type'])
        X_all.append(X_cur)
        if label_available: y_all.append(y_cur)
    if label_available: return X_all, y_all
    return X_all, df

