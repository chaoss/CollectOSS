import logging, os, sys, time, requests, json
from datetime import datetime
from multiprocessing import Process, Queue
import pandas as pd
import sqlalchemy as s
from sqlalchemy.schema import Sequence
from workers.worker_base import Worker
import seaborn as sns
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
import nltk
import re
from nltk.stem.snowball import SnowballStemmer
stemmer = SnowballStemmer("english")
from sklearn.cluster import KMeans
import string
import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA
from collections import OrderedDict
from sklearn.decomposition import LatentDirichletAllocation  as LDA
import pickle

from textblob import TextBlob
from collections import Counter

from os import path

class ClusteringWorker(Worker):
	def __init__(self, config={}):
	
		worker_type = "clustering_worker"
		
		given = [['git_url']]
		models = ['clustering']

		data_tables = ['repo_cluster_messages','repo_topic','topic_words']
		operations_tables = ['worker_history', 'worker_job']

		# Run the general worker initialization
		super().__init__(worker_type, config, given, models, data_tables, operations_tables)

		self.config.update({
			'api_host': self.augur_config.get_value('Server', 'host'),
			'api_port': self.augur_config.get_value('Server', 'port')
		})

		# Define data collection info
		self.tool_source = 'Clustering Worker'
		self.tool_version = '0.0.0'
		self.data_source = 'Non-existent API'
		
		#define clustering specific parameters
		# self.max_df = 0.9 #get from configuration file
		# self.max_features = 1000 
		# self.min_df = 0.1 
		# self.ngram_range = (1,3)
		# self.num_clusters = 4
		self.max_df = self.config['max_df'] #get from configuration file
		self.max_features = self.config['max_features']
		self.min_df = self.config['min_df']
		self.ngram_range = (1,3)
		self.num_clusters = self.config['num_clusters']
		self.clustering_by_content = True
		self.clustering_by_mechanism = False
		
		#define topic modeling specific parameters
		self.num_topics = 50
		self.num_words_per_topic = 12

		nltk.download('punkt')
		

	def clustering_model(self, task, repo_id):
		#self.logger.info("Clustering Worker init")
		# self.logger.info(self.max_df)
		# self.logger.info(self.max_features)
		# self.logger.info(self.min_df)
		# self.logger.info(self.num_clusters)
		
		
		MODEL_FILE_NAME = "kmeans_repo_messages"
		
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
		#result = self.db.execute(delete_points_SQL, repo_id=repo_id, min_date=min_date)
		msg_df_cur_repo = pd.read_sql(get_messages_for_repo_sql, self.db, params={"repo_id" : repo_id})
		self.logger.info(msg_df_cur_repo.head())
		
		
		#check if dumped pickle file exists, if exists no need to train the model
		if not path.exists(MODEL_FILE_NAME):
			self.logger.info("clustering model not trained. Training the model.........")
			self.train_model()
		else:
			self.logger.info("using pre-trained clustering model....")	
		
		with open("kmeans_repo_messages", 'rb') as model_file:
			kmeans_model = pickle.load(model_file)
		
		msg_df = msg_df_cur_repo.groupby('repo_id')['msg_text'].apply(','.join).reset_index()
		
		if msg_df.empty:
			self.logger.info("not enough data for prediction")
			self.register_task_completion(task, repo_id, 'clustering')
			return
		
		vocabulary = pickle.load(open("vocabulary", "rb"))
		
		tfidf_vectorizer = TfidfVectorizer(max_df = self.max_df, max_features =self.max_features,
                                      min_df = self.min_df, stop_words='english',
                                      use_idf=True, tokenizer=self.preprocess_and_tokenize, ngram_range=self.ngram_range, vocabulary =vocabulary)
		tfidf_transformer = tfidf_vectorizer.fit(msg_df['msg_text']) #might be fitting twice, might have been used in training
		
		#save new vocabulary ??
		feature_matrix_cur_repo = tfidf_transformer.transform(msg_df['msg_text'])
		
		
		prediction = kmeans_model.predict(feature_matrix_cur_repo)
		self.logger.info("prediction: "+ str(prediction[0]))
		
		#inserting data
		record = {
				  'repo_id': int(repo_id),
				  'cluster_content': int(prediction[0]),
				  'cluster_mechanism' : -1
				  }
		result = self.db.execute(self.repo_cluster_messages_table.insert().values(record))
		logging.info("Primary key inserted into the repo_cluster_messages table: {}".format(result.inserted_primary_key))
		
		lda_model = pickle.load(open("lda_model", "rb"))
		
		vocabulary = pickle.load(open("vocabulary_count", "rb"))
		count_vectorizer = CountVectorizer(max_df=self.max_df, max_features=self.max_features, min_df=self.min_df,stop_words="english", tokenizer=self.preprocess_and_tokenize, vocabulary=vocabulary)
		count_transformer = count_vectorizer.fit(msg_df['msg_text']) #might be fitting twice, might have been used in training
		
		#save new vocabulary ??
		count_matrix_cur_repo = count_transformer.transform(msg_df['msg_text'])
		prediction = lda_model.transform(count_matrix_cur_repo)
		
		for i, prob_vector in enumerate(prediction):
			#repo_id = msg_df.loc[i]['repo_id']
			for i, prob in enumerate(prob_vector):
				record = {
				  'repo_id': int(repo_id),
				  'topic_id': i+1,
				  'topic_prob' : prob
				  }
				result = self.db.execute(self.repo_topic_table.insert().values(record))
				
		self.register_task_completion(task, repo_id, 'clustering')
	
	
	
	def train_model(self):
		get_messages_sql = s.sql.text(
                            """
				SELECT r.repo_group_id, r.repo_id, r.repo_git, r.repo_name, i.issue_id thread_id,m.msg_text,i.issue_title thread_title,m.msg_id
					FROM augur_data.repo r, augur_data.issues i,
					augur_data.message m, augur_data.issue_message_ref imr
					WHERE r.repo_id=i.repo_id
					AND imr.issue_id=i.issue_id
					AND imr.msg_id=m.msg_id
					UNION
				SELECT r.repo_group_id, r.repo_id, r.repo_git, r.repo_name, pr.pull_request_id thread_id,m.msg_text,pr.pr_src_title thread_title,m.msg_id
					FROM augur_data.repo r, augur_data.pull_requests pr,
					augur_data.message m, augur_data.pull_request_message_ref prmr
					WHERE r.repo_id=pr.repo_id
					AND prmr.pull_request_id=pr.pull_request_id
					AND prmr.msg_id=m.msg_id
				"""
                                )
		msg_df_all = pd.read_sql(get_messages_sql, self.db, params={})
		
		
		#select only highly active repos
		msg_df_all = msg_df_all.groupby("repo_id").filter(lambda x: len(x)>500)
		
		#combining all the messages in a repository to form a single doc
		msg_df = msg_df_all.groupby('repo_id')['msg_text'].apply(','.join)
		msg_df = msg_df.reset_index()
		
		#dataframe summarizing total message count in a repository
		message_desc_df = msg_df_all[["repo_id","repo_git","repo_name","msg_id"]].groupby(["repo_id","repo_git","repo_name"]).agg('count').reset_index()
		message_desc_df.columns = ["repo_id","repo_git", "repo_name", "message_count"]
		self.logger.info(msg_df.head())
		
		tfidf_matrix, features = self.get_tf_idf_matrix(msg_df['msg_text'], self.max_df, self.max_features, self.min_df, self.ngram_range)
		msg_df['cluster'] = self.cluster_and_label(tfidf_matrix, self.num_clusters)
		
		
		
		#visualize_labels_PCA(tfidf_matrix.todense(), msg_df['cluster'], msg_df['repo_id'], 2, "MIN_DF={} and MAX_DF={} and NGRAM_RANGE={}".format(MIN_DF, MAX_DF, NGRAM_RANGE))
		
		
		#LDA - Topic Modeling
		count_vectorizer = CountVectorizer(max_df=self.max_df, max_features=self.max_features, min_df=self.min_df,stop_words="english", tokenizer=self.preprocess_and_tokenize)
		
		#count_matrix = count_vectorizer.fit_transform(msg_df['msg_text'])
		count_transformer = count_vectorizer.fit(msg_df['msg_text'])
		count_matrix = count_transformer.transform(msg_df['msg_text'])
		pickle.dump(count_transformer.vocabulary_, open("vocabulary_count",'wb'))
		feature_names = count_vectorizer.get_feature_names()
		
		
		lda_model = LDA(n_components=self.num_topics)
		lda_model.fit(count_matrix)
		# each component in lda_model.components_ represents probability distribution over words in that topic
		topic_list = lda_model.components_
		logging.info("Topic List Created: {}".format(topic_list))
		pickle.dump(lda_model, open("lda_model",'wb'))
		logging.info("pickle dump")

		#insert topic list into database
		topic_id = 1
		for topic in topic_list:
			for i in topic.argsort()[:-self.num_words_per_topic-1:-1]:
				twidseq = Sequence(name=f'augur_data.topic_words_topic_words_id_seq')
				#twid = self.db.execute(twidseq)

				record = {
				  'topic_words_id': int(twidseq),
				  'topic_id': int(topic_id),
				  'word': feature_names[i]
				  }
				result = self.db.execute(self.topic_words_table.insert().values(record))
				logging.info("Primary key inserted into the topic_words table: {}".format(result.inserted_primary_key))
			topic_id+=1
		
		#insert topic list into database
		
		#save the model and predict on each repo separately
			
		
		prediction = lda_model.transform(count_matrix)

		topic_model_dict_list = []
		for i, prob_vector in enumerate(prediction):
			topic_model_dict = {}
			topic_model_dict['repo_id'] = msg_df.loc[i]['repo_id']
			for i, prob in enumerate(prob_vector):
				topic_model_dict["topic"+str(i+1)] = prob
			topic_model_dict_list.append(topic_model_dict)
		topic_model_df = pd.DataFrame(topic_model_dict_list)

		result_content_df = topic_model_df.set_index('repo_id').join(message_desc_df.set_index('repo_id')).join(msg_df.set_index('repo_id'))
		result_content_df = result_content_df.reset_index()
		self.logger.info(result_content_df)
		
		POS_count_dict = msg_df.apply(lambda row : self.count_func(row['msg_text']), axis = 1)
		msg_df_aug = pd.concat([msg_df,pd.DataFrame.from_records(POS_count_dict)], axis=1)
		self.logger.info(msg_df_aug)
		
	def get_tf_idf_matrix(self,text_list, max_df, max_features, min_df, ngram_range):
	
		
		
		tfidf_vectorizer = TfidfVectorizer(max_df = max_df, max_features=max_features,
                                      min_df=min_df, stop_words='english',
                                      use_idf=True, tokenizer=self.preprocess_and_tokenize, ngram_range=ngram_range)
		tfidf_transformer = tfidf_vectorizer.fit(text_list)
		tfidf_matrix = tfidf_transformer.transform(text_list)
		pickle.dump(tfidf_transformer.vocabulary_, open("vocabulary",'wb'))
		return tfidf_matrix, tfidf_vectorizer.get_feature_names()
		
	def cluster_and_label(self,feature_matrix, num_clusters):
		kmeans_model = KMeans(n_clusters=num_clusters)
		kmeans_model.fit(feature_matrix)
		pickle.dump(kmeans_model, open("kmeans_repo_messages",'wb'))
		return kmeans_model.labels_.tolist()
		
	def visualize_labels_PCA(self,features, labels, annotations, num_components, title):
    
		labels_color_map = {-1 : "red"}
		for label in labels:
			labels_color_map[label] = [list([x/255.0 for x in list(np.random.choice(range(256), size=3))])]
		low_dim_data = PCA(n_components=num_components).fit_transform(features)
	
		fig, ax = plt.subplots(figsize=(20,10))
	
		for i, data in enumerate(low_dim_data):
			pca_comp_1, pca_comp_2 = data
			color = labels_color_map[labels[i]]
			ax.scatter(pca_comp_1, pca_comp_2, c=color,label=labels[i])
			#ax.annotate(annotations[i],(pca_comp_1, pca_comp_2))
			
		
		handles,labels = ax.get_legend_handles_labels()
		handles_label_dict = OrderedDict(zip(labels, handles))
		ax.legend(handles_label_dict.values(), handles_label_dict.keys() )
		
		plt.title(title)
		plt.xlabel("PCA Component 1")
		plt.ylabel("PCA Component 2")
		plt.show()
		
	def count_func(self,msg):
		blobed = TextBlob(msg)
		counts = Counter(tag for word,tag in blobed.tags if tag not in ['NNPS','RBS','SYM','WP$','LS','POS','RP','RBR','JJS','UH','FW','PDT'])
		total = sum(counts.values())
		normalized_count = {key: value/total for key,value in counts.items()}
		return normalized_count
		
	def preprocess_and_tokenize(self,text):
			text= text.lower()
			text =  re.sub(r'[@]\w+','',text)
			text =  re.sub(r'[^A-Za-z]+', ' ', text)
    
			tokens = nltk.word_tokenize(text)
			tokens = [token for token in tokens if len(token)>1]
			stems = [stemmer.stem(t) for t in tokens]
			return stems

