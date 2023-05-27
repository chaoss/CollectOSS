Clustering Task
==========================

The task analyzes the comments in issues and pull requests, and clusters the repositories based on contents of those messages.
The task also performs topic modeling using Latent Dirichlet allocation


Clustering of text documents
----------------------------------------------------

Clustering is a type of unsupervised machine learning technique that involves grouping together similar data points. In case of textual data, it involves grouping together semantically similar documents.
The document is a collection of sentences. In our case, document represents the collection of comments across issues and pull requests across a particular repository. Since, clustering algorithm works with numerical features, we need to first convert documents into vector representation.

Implementation
--------------
The task performs two tasks — clustering of the repositories represented as documents (collection of all messages from issues and pull requests within the repository) and topic modeling. If the pre-trained model doesn’t exist in the clustering task's folder, the data from all the repository in the connected database are used to train the model. After the training, the following model files are dumped in the clustering task's folder

- vocabulary : the set of features obtained from TF-IDF vectorization on text data (required in prediction phase)
- kmeans_repo_messages : trained kmeans clustering model on tfidf features
- vocabulary_count: a set of features obtained from count vectorization on text data (required in prediction phase)
- lda_model : trained latent Dirichlet analysis model for topic modeling

The hyperparameters for the training are obtained from the configuration file.
In addition, the training phase populates the ‘topic words’ database table with the top words belonging to a topic.


**Prediction**
If the trained model exists in the task directory, the prediction is made on the documents corresponding to the repositories in the repo groups specified in the configuration. The task populates the following tables
repo_topic : stores probability distribution over the topics for a particular repository
repo_cluster_messages : stores clustering label assigned to a repository


Task Configuration
--------------------
For this task's configuration, in workers configuration block, we need to define port, switch and number of workers.

.. code-block:: json

    "clustering_worker":{
    	    "port" : 51500,
    	    "switch": 1,
    	    "workers": 1,
            "max_df" : 0.9,
            "max_features" : 1000,
            "min_df" : 0.1,
            "num_clusters" : 4
    }

Additional Worker Parameters: 
------------------------------------------------------

In addition to standard worker parameters, clustering worker requires some worker-specific parameters which are described below:

 - **max_df** :sets the threshold which filters out terms that have higher document frequency (corpus specific stop words)
 - **min_df** : filters out uncommon words
 - **max_features** - defines maximum number of features to be used in calculating tfidf matrix
 - **num_clusters** - defines number of clusters to segment the repositories into
