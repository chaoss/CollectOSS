
## Idea: Enhance Conversational Topic Modelling Capabilities in CHAOSS Software

**Hours: 350**

[Micro-tasks and place for questions](https://github.com/chaoss/augur/issues/1640)

## Microtasks

For becoming familiar with Augur, you can start by reading some documentation. You can find useful information at in the links, below. Grimoirelab also has a set of installation instructions and documentation here: https://chaoss.github.io/grimoirelab-tutorial/

#### GSoC Students :
Once you're familiar with Augur, you can have a look at the following microtasks.

Microtask 0:
    Download and configure Augur, creating a dev environment using the general cautions noted here:
Augur
            https://oss-augur.readthedocs.io/en/dev/getting-started/installation.html and the full documentation here:
            https://oss-augur.readthedocs.io/en/dev/development-guide/toc.html
Grimoirelab
            https://chaoss.github.io/grimoirelab-tutorial/

Microstask 1:
    Work on any Augur or Grimoirelab Issue that's Open

Microtask 2:
    Identify new issues you encounter during installation.

Microstask 3:
    Explore data presently captured, develop an experimental visualization using tools of your choice. If Jupyter Notebooks against an Augur database/API endpoint collection, use https://github.com/chaoss/augur-community-reports for development.

Microtask 4:
    Anything you want to show us. Even if you find bugs in our documentation and want to issue a PR for those!


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



## IDEA: Implement Conversion Rate Metric in CHAOSS Software

**Hours: 350**

[Micro-tasks and place for questions](https://github.com/chaoss/augur/issues/2992)
 
### Conversion Rate 

Question: What are the rates at which new contributors become more sustained contributors? 

### Description 

The conversion rate metric is primarily aimed at identifying how new community members become more sustained contributors over time. However, the conversion rate metric can also help understand the changing roles of contributors, how a community is growing or declining, and paths to maintainership within an open source community.  
 
### Objectives (why)  
  - Observe if new members are becoming more involved with an open source project  
  - Observe if new members are taking on leadership roles within an open source project  
  - Observe if outreach efforts are generating new contributors to an open source project  
  - Observe if outreach efforts are impacting roles of existing community members  
  - Observe if community conflict results in changing roles within an open source community  
  - Identify casual, regular, and core contributors  

### Implementation 

This project could be implemented using either the CHAOSS/Augur, or CHAOSS/Grimoirelab (including stack components noted in references) technology stacks. 

The aims of the project are as follows:
  - Implement the Conversion Rate Metric in CHAOSS Software
    - After discussion, consider which CHAOSS Software Stack you wish to work with
    - In collaboration with mentors, define the technology framework, and initial path to a "hello world" version of the metric
    - Iterative development of the metric
  - Assist in the deployment of this metric for a pre-determined collection of repositories in a publicly viewable website linked to the CHAOSS project. 
  - Advance the work of the [chaoss metrics models working group](https://github.com/chaoss/wg-metrics-models). 

* _Difficulty:_ Medium
* _Requirements:_ Knowledge of Python is desired. Some knowledge of Javascript or twitter/bootstrap is also desired. Key requirement is a keenness to dig into this challenge!
* _Recommended:_ Python experience. 
* _Mentors:_ Sean Goggins 

#### Filters (optional) 
  - Commits  
  - Issue creation  
  - Issue comments  
  - Change request creation  
  - Change request comments  
  - Merged change requests  
  - Code Reviews  
  - Code Review Comments  
  - Reactions (emoji)  
  - Chat platform messages  
  - Maillist messages  
  - Meetup attendance 

#### Visualizations 
 
![](./images/gsoc-1.png)

Source: https://chaoss.github.io/grimoirelab-sigils/assets/images/screenshots/sigils/overall-community-structure.png  

![](./images/gsoc-2.png) 

Source: https://opensource.com/sites/default/files/uploads/2021-09-15-developer-level-02.png  

#### Tools Providing the Metric  
  - Augur  
  - openEuler Infra 

#### Data Collection Strategies 

The following is an example from the [openEuler](https://www.openeuler.org/en/) community:   
  - A group of people who attended an offline event A held by the community, can be identified as Group A. Demographic information of Group A could be fetched from an on-line survey when people register for the event. To identify the conversation rate of these participants:  
  - Some people from Group A started watching and forking the repos, indicating they have shown some interest in this community. We marked them as subgroup D0 (Developer Level 0) as a subset of Group A.  
  - Conversion rate from the total number of people in Group A to the number of people in subgroup D0 is: D0/Group A  
  - Some people from subgroup D0 make more contributions beyond just watching or forking, including creating issues, making comments on an issue, or performed a code review. We marked them as subgroup D1 (Developer Level 1) as a subset of D0.  
  - Conversion rate from the total number of people in Subgroup D0 to the number of people in subgroup D1 is: D1/D0.  
  - Some people from subgroup D1 continue to make more contributions, like code contributions, to the project. This could include creating merge requests and merging new project code. We marked them as subgroup D2 (Developer Level 2) as a subset of D1.  
  - Conversion rate from the total number of people in subgroup D1 to the number of people in subgroup D2 is: D2/D1. 

![](./images/gsoc-3.png)

   Definition:  
  - Developer Level 0 (D0) example: Contributors who have given the project a star, or are watching or have forked the repository  
  - Developer Level 1 (D1): Contributors who have created issues, made comments on an issue, or performed a code review  
  - Developer Level 2 (D2): Contributors who have created a merge request and successfully merged code  
  - Conversion Rate (Group A -> D0): CR (Group A -> D2) = D0/Group A  
  - Conversion Rate (D0 -> D1): CR (D0 -> D1) = D1/D0  
  - Conversion Rate (D1 -> D2): CR (D1 -> D2) = D2/D1 

### References  
  - https://opensource.com/article/21/11/data-open-source-contributors  
  - https://github.com/chaoss/augur
  - https://gitee.com/openeuler/website-v2/blob/master/web-ui/docs/en/blog/zhongjun/2021-09-15-developer-level.md  
  - https://chaoss.github.io/grimoirelab-sigils/common/onion_analysis/  
  - https://mikemcquaid.com/2018/08/14/the-open-source-contributor-funnel-why-people-dont-contribute-to-your-open-source-project/  
### Contributors  
  - Sean Goggins
  - Andrew Brain
  - John McGinness

## IDEA: Open Source Software Health Metrics Visualization Exploration

**Hours: 350**

[Micro-tasks and place for questions](https://github.com/chaoss/augur/issues/2993)

The CHAOSS Community currently delivers pre-packaged visualizations of open source software health data through Augur APIs (https://github.com/chaoss/augur/blob/main/augur/routes/pull_request_reports.py and https://github.com/chaoss/augur/blob/main/augur/routes/contributor_reports.py), and the https://github.com/chaoss/augur-community-reports repository. This project seeks to expand, refine, and standardize the visualization of different classes of community health metrics data. Specifically, some analyses are temporal, others are anomaly driven, and in some cases contrasts across repositories and communities are required. In each case, the visualization of data is an essential component for metrics, and what we are now referring to as metrics models (https://github.com/chaoss/wg-metrics-models). 

Additional resources include: http://new.augurlabs.io/ && https://github.com/augurlabs/augur_view which demonsrate the updated twitter/bootstrap Augur frontend. 

The aims of the project are as follows:
  - Experiment with standard metrics visualizations using direct Augur database connections, or through the Augur API. 
  - Refine metrics, and metrics model visualizations using Jupyter Notebooks are similar technology.
  - Transform visualizations, as they are completed, into Augur API endpoints, following the pull request, and contributor reports examples. 

* _Difficulty:_ Medium
* _Requirements:_ Strong interest in data visualization. 
* _Recommended:_ Experience with Python is desirable, and experience designing, or developing visualizations is desirable. 
* _Mentors:_ Isaac Milarsky, Andrew Brain 
