==============
Insight_worker
==============

It uses Augur's metrics API to discover insights for every time_series metrics like ``issues``, ``reviews``, ``code-changes``, ``code-changes-lines`` etc.. of every repos present in the database.

We used BiLSTM(Bi-directional Long Short Term Memory)model as it is capable of capturing trend, long-short seasonality in the data. A bidirectional LSTM (BiLSTM) layer learns bidirectional long-term dependencies between time steps of time series or sequence data. These dependencies can be useful when you want the network to learn from the complete time series at each time step.

*Worker Configuration*
======================
Worker has three main configurations that are standard across all workers.And it also have few more configurations that are mainly for Machine Learning model inside the worker.

The standard options are:

- ``switch``, a boolean flag indicating if the worker should automatically be started with Augur. Defaults to ``0`` (false).
- ``workers``, the number of instances of this worker that Augur should spawn if ``switch`` is set to ``1``. Defaults to ``1``.
- ``port``, which is the base TCP port the worker will use t0 communicate with Augur’s broker. The default is different for each worker, for the ``insight_worker`` it is ``21311``.

Keeping workers at 1 should be fine for small collection sets, but if you have a lot of repositories to collect data for, you can raise it. We also suggest double checking that the default worker ports are free on your machine.

Configuration for ML models are:

We recommend leaving the defaults in place for the insight worker unless you interested in other metrics, or anomalies for a different time period. 

- ``training_days``, which specifies the date range that the ``insight_worker`` should use as its baseline for the statistical comparison. Defaults to ``365``, meaning that the worker will identify metrics that have had anomalies compared to their values over the course of the past year, starting at the current date.

- ``anomaly_days``, which specifies the date range in which the ``insight_worker`` should look for anomalies. Defaults to ``14``, meaning that the worker will detect anomalies that have only occured within the past fourteen days, starting at the current date.

- ``contamination``, which is the "sensitivity" parameter for detecting anomalies. Acts as an estimated percentage of the training_days that are expected to be anomalous. The default is ``0.1`` for the default training days of 365: 10% of 365 days means that about 36 data points of the 365 days are expected to be anomalous.

- ``metrics``, which specifies which metrics the ``insight_worker`` should run the anomaly detection algorithm on. This is structured like so::

    [
        'endpoint_name_1',
        'endpoint_name_1',
        'endpoint_name_2',
        ...
    ] 

    # defaults to the following

    [
        "issues-new", 
        "code-changes", 
        "code-changes-lines", 
        "reviews", 
        "contributors-new"
    ]

Methods inside the Insight_model
--------------------------------

- ``time_series_metrics``\:It takes parameters ``entry_info`` , ``repo_id`` .Collects data of different metrics using API endpoints.Preprocesses data and creates a dataframe with date and each and every fields of the given endpoints as columns.Then this method calls another method that is ``lstm_selection``.Structure of the dataframe is as follows\:

 .. code-block:: bash

  
  df>>
  index   date          endpoints1 _ field     endpoints2 _ field
  0.      2020-03-20    5                      8


- ``lstm_selection``\:This method takes ``entry_info``, ``repo_id``, ``df`` as parameters.It Selects window_size or time_steps by checking sparsity and coefficient of variation in data which is passed into the ``lstm_keras`` method.

- ``preprocess_data``\:This method is called by the ``lstm_keras`` method with ``data``, ``tr_days``, ``lback_days``, ``n_features``, ``n_predays`` as parameters.It arranges training_data according to different parameters passed by ``lstm_keras`` method for the ``BiLSTM`` model.It returns two variables ``features_set`` and ``labels`` with the following structure\:

 .. code-block:: bash

  
  features_set = [ 
      [[1],
       [2]],
      [[2],
       [3]],
      [[3],
       [4]]
  ]
  labels = [ [3],[4],[5] ]

  #tr_days : number of training days(it is not equal to the training days passed into the configuration)
  #lback_days : number of days to lookback for next-day prediction
  #n_features : number of features of columns in dataframe for training
  #n_predays : next number of days to predict for each entry in features_set

  
  #tr_days = training_days - anomaly_days   (in configuration)
  
  #here 
  tr_days = 4,
  black_days = 2,
  n_features = 1,
  n_predays = 1   

- ``lstm_model``\:It is the configuration of the multiple ``BiLSTM`` layers along with single ``dense`` layer and optimisers.This method called inside the ``lstm_keras`` method with ``features_set``, ``n_predays``, ``n_features`` as parameters.Configuation of the model is as follows\:

 .. code-block:: bash

  
  model = Sequential()
  model.add(Bidirectional(LSTM(90, activation='linear',return_sequences=True,input_shape=(features_set.shape[1], n_features))))
  model.add(Dropout(0.2))
  model.add(Bidirectional(LSTM(90, activation='linear',return_sequences=True)))
  model.add(Dropout(0.2))
  model.add(Bidirectional(LSTM(90, activation='linear')))
  model.add(Dense(1))
  model.add(Activation('linear'))
  model.compile(optimizer='adam', loss='mae')

 This configuration is designed to acheive the best possible results for all kind of metrics.

- ``lstm_keras``\:This is the most important method in the ``insights_model`` called by the ``lstm_selection`` method with ``entry_info`` , ``repo_id``, and ``dataframe`` as parameters.Here dataframe consists of two columns, one is ``date`` and another one is ``endpoint1 _ field`` .In this method model is trained on ``tr_days`` data and values were predicted for ``anomaly_days`` data.Baesd on the difference on actual and predicted values outliers were discovered.
  
 If any outliers discovered between the ``anomaly_days`` then those points will be inserted into to the ``repo_insights`` and ``repo_insights_records`` table by calling ``insert_data`` method. 

 Before calling the ``insert_data`` method, performance of model on the training as well as test data will be evaluated and its summary will be inserted into the ``lstm_anomaly_results`` table along with the unique model configuration into the ``lstm_anomaly_models`` table.

- ``insert_data``\:It is called by the ``lstm_keras`` method with ``entry_info``, ``repo_id``, ``anomaly_df``, ``model`` as parameters.Here ``anomaly_df`` is the dataframe which consists of points which are classified as outliers between the ``anomaly_days``.

Insights\_model consists of multiple independent methods like ``time_series_metrics``, ``insert_data`` etc..These methods can be used independently with other Machine Learning models.Also ``preprocess_data``, ``model_lstm`` methods can be easily modified according to the different LSTM networks configuration.