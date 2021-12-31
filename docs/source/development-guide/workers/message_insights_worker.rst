=======================
Message Insights Worker
=======================

.. note:: 
    - If you have an NVidia GPU available, you can install the `cuda` drivers to make this worker run faster. 
    - On Ubuntu 20.04, use the following commands: 
      - On the Ubuntu machine, open a Terminal. Type in the following commands to add the Nvidia ppa repository:
      - `wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin`
      - `sudo mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600 && sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/7fa2af80.pub`
      - `sudo add-apt-repository "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/ /"`
      - `sudo apt-get update && sudo apt-get install -y nvidia-kernel-source-460`
      - `sudo apt-get -y install cuda`

This worker analyzes the comments and text messages corresponding to all the issues and pull requests in a repository and performs two tasks:

- **Identifies novel messages** - Detects if a new message is semantically different from past messages in a repo
- **Performs sentiment analysis** - Assigns a score to every message indicating positive/negative/neutral sentiments

Worker Configuration
---------------------

To kickstart the worker, it needs to receive a task from the Housekeeper, similar to other workers, and have a corresponding worker specific configuration.

The standard options are:

- ``switch`` - a boolean flag indicating if the worker should automatically be started with Augur. Defaults to ``0`` (false).
- ``workers`` - the number of instances of this worker that Augur should spawn if ``switch`` is set to ``1``. Defaults to ``1``.
- ``port`` - the TCP port the worker will use to communicate with Augur’s broker, the default being ``51300``.
- ``insight_days`` - the most recent period (in days) for which insights would be calculated.
- ``models_dir`` - the directory within the worker directory, where all trained machine learning models would be stored.

.. note::

    - ``insight_days`` can be kept at roughly 20-30 as the sentiment, or novelty do not fluctuate very fast!
    - The ``models_dir`` would collect the trained ML models. A different model would be saved per repo for performing novelty detection and a common sentiment analysis model across all repos. Do not accidentally delete this, as subsequent runs leverage these!

Worker Pipeline
---------------

When a repo is being analyzed for the first time, the ML models are trained and saved on disk in the ``models_dir`` specified in the config block. During subsequent runs, these models are used to predict directly. The worker contains the files — ``preprocess_text.py``, ``message_novelty.py``, and ``message_sentiment.py`` to get insights. The ``train_data`` directory contains training files that are utilized by the worker when running for the first time.

.. code-block:: bash

    message_insights_worker/
    ├── __init__.py
    ├── runtime.py
    ├── setup.py
    ├── message_insights_worker.py
    ├── message_novelty.py
    ├── message_sentiment.py
    ├── preprocess_text.py
    ├── message_models/
    │   ├── 27940_uniq.h5
    │   ├── tfidf_vectorizer.pkl
    │   └── XGB_senti.pkl
    └── train_data/
        ├── custom_dataset.xlsx
        ├── doc2vec.model
        └── EmoticonLookupTable.txt

The ``custom_dataset.xlsx`` is a dataset containing technical code review and commit messages from Oracle & Jira database, and general sentiment, emoji-filled messages from StackOverflow. ``EmoticonLookupTable`` is used in sentiment analysis to parse emojis/emoticons and capture their sentiment. ``doc2vecmodel`` is the trained Doc2Vec model on the custom_dataset, utilized for forming word embeddings in novelty detection.

Novelty Detection 
^^^^^^^^^^^^^^^^^^
Novelty detection is an unsupervised classification problem to identify abnormal/outlier messages. Since a message that is novel in the context of 1 repo may be normal to another, it is essential to maintain the semantics of the past messages of every repo, to flag an incoming message as novel/normal accurately. Every message is transformed to a 250-dimensional Doc2Vec embedding. Deep Autoencoders are used to compress input data and calculate error thresholds. The architecture of the autoencoder model consists of two symmetrical deep neural networks — an encoder and a decoder that applies backpropagation, setting the target values to be equal to the inputs. It attempts to copy its input to its output and anomalies are harder to reconstruct compared with normal samples. 2 AEs are used, the first one identifies normal data based on the threshold calculated and then the second is trained using only the normal data. The Otsu thresholding technique is used in these steps to get the error threshold. Messages which are at least 10 characters long and have reconstruction error > threshold, get flagged as novel.

Sentiment Analysis
^^^^^^^^^^^^^^^^^^
The sentiment analysis was modeled as a supervised problem. This uses the SentiCR tool with modifications to improved preprocessing, emoji parsing, and predicting. Messages are first cleaned using an 8 step preprocessing method. The messages are converted into embeddings using TF-IDF vectorization and then sent to an XGBoost classifier, which assigns sentiment labels.

Insights
---------

After these tasks are done, the ``message_analysis`` table is populated with all details are about a message: the id and the sentiment and novelty scores. In order to get a view of these metrics at a repo level, the ``message_analysis_summary`` table is updated with the total ratio of positive/negative sentiment messages and count of novel messages every ``insight_days`` frequency. 

The 3 types of insights provided are:

- Counts of positive/negative sentiment and novel messages
- Mean deviation of these in the most recent analyzed with the past to understand trends
- A list of timestamps  which indicate possible anomaly durations with respect to sentiment trends

These are also sent to Auggie.
