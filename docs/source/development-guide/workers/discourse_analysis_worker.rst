Discourse Analysis Worker
==============================

The worker analyzes the sequential conversation data in GitHub issues and pull requests. The worker classifies the messages into one of the following discourse acts.

- Question
- Answer
- Elaboration
- Announcement
- Agreement
- Disagreement

Structured Prediction Using Conditional Random Field
-------------------------------------------------------

Structured prediction is a type of supervised machine learning technique that involves predicting a structured group of multiple correlated outputs at the same time. In the problem of discourse act classification, it means predicting discourse labels for each utterance in a discourse sequence simultaneously. Structured prediction methods take advantage of the inherent dependency among the sentences in a discussion thread. One of the popular methods in structured prediction problem is "Conditional Random Fields" (CRF). They belong to a class of undirected graphical models where each node represents a random variable and edge denotes dependency among the connected random variables. In CRF, the nodes are divided into two distinct sets - input features "X" (also called an observed variable)and output labels "Y". We can then model the conditional distribution p(Y | X) using maximum likelihood learning of parameters. The optimization problem is often convex and can be solved using a gradient descent algorithm like lbfgs. In case of discourse anlaysis, each message is dependent on the preceding and succeeding messages giving rise to the linear chain-like structure.

Worker Implementation
------------------------

The feature vector consists of semantic and structural features. The messages are preprocessed and are converted into a vector using TF-IDF vectorizer. The lexical and structural features are added before grouping them based on conversation thread. sklearn-crfsuite library for building CRF model. The library provides scikitlearn compatible interface. The worker uses the conditional random field model pretrained with labeled Reddit data to make predictions on GitHub data.

In addition to the python files defining the worker, the worker directory consists of following model files

- **trained_crf_model** - the trained crf model which can be used to predict sequential discourse acts
- **tfidf_transformer** - the trained tfidf transformer can be used to convert text into feature vector
- **word_to_emotion_map** - the dictionary provides mapping from word to label signifying particular emotion

Worker Configuration
-----------------------
Like standard worker configuration, we need to define delay, given, model and repo_group_id in housekeeper configuration block.

.. code-block:: json 

	{
	    "delay": 10000,
	    "given":["git_url"],
	    "model" : "discourse_analysis",
	    "repo_group_id" : 60003
	}

Further, in workers configuration block, we need to define port, switch and number of workers.

.. code-block:: json 

	"discourse_analysis_worker":{
		    "port" : 51400,
		    "switch": 1,
		    "workers": 1
		}
