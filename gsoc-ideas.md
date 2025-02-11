
## Idea: Enhance Conversational Topic Modelling Capabilities in CHAOSS Software

**Hours: 350**

[Micro-tasks and place for questions](https://github.com/chaoss/augur/issues/1640)

This project will add GenSIM logic, and other capabilities to the Clustering Worker inside of Augur Software, and be extended into a generalized Open Source Software Conversational Topic Modeling Instrument. 

CHOASS/augur has several workers that store machine learning information derived from computational linguistic analysis of data in the `message` table. The message table includes messages from issue, pull request, pull request review, and email messages. They are related to their origin with bridge tables like `pull_request_message_ref`. The ML/CL workers are all run against all the messages, regardless of origin. 

1. Clustering Worker (clusters created and topics modeled)
2. message analysis worker  (sentiment and novelty analysis)
3. discourse analysis worker (speech act classification (question, answer, approval, etc.)

Clustering Worker Notes: 

Clustering Worker: 2 Models.
 - Models: 
  - Topic modeling, but it needs a better way of estimating number of topics.
   - Tables
    - repo_topic
    - topic_words
  - Computational linguistic clustering
   - Tables
    - repo_cluster_messages
 - Key Needs
    - Add GenSim algorithms to topic modeling section https://github.com/chaoss/augur/issues/1199
  - The topics, and associated topic words need to be persisted after each run. At the moment, the topic words get overwritten for each topic modeling run. 
  - Description/optimization of the parameters used to create the computational linguistic clusters.
  - Periodic deletion of models (heuristic: If 3 months pass, OR there’s a 10% increase in the messages, issues, or PRs in a repo, rebuild the models)
  - Establish some kind of model archiving with appropriate metadata (lower priority)

Discourse Analysis Worker Notes: 

discourse_insights table (select max(data_collection_date) for each msg_id)
 - sequence is reassembled from the timestamp in the message table (look at msg_timestamp)
 - issues_msg_ref, pull_request_message_ref, pull_request_review_msg_ref

Message Analysis Worker
 - message_analysis 
 - message_analysis_summary

<img width="1159" alt="augur-tech" src="https://user-images.githubusercontent.com/379847/124799236-f440dc80-df19-11eb-84ce-302cf274884f.png">

The aims of the project are as follows:
  - Advance topic modeling of open source software conversations captured in GitHub.
  - Integrate this information into clearer, more parsimonious CHAOSS metrics.
  - Automate the management machine learning insights, and topic models over time. 
  - (Stretch Goal) Improve the operation of the overall machine learning insights pipeline in CHAOSS/augur, and generalize these capabilities. 


* _Difficulty:_ Medium
* _Requirements:_ Interest in software analytics. Python programming. Conceptual understanding of machine learning, and an eagerness to learn maching learning, and SQL knowledge.
* _Recommended:_ Experience with Python
* _Mentors:_ Sean Goggins, Andrew Brain, Isaac Milarsky
