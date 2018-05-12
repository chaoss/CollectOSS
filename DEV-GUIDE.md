# Augur Development Guide: Making Contributions

## Getting Started
See our [Contributing to Augur](./Contributing.md) guide for specifics on how we review pull requests. tl;dr: Fork our repo. Make a change. Use the mailing list for [CHAOSS](https://lists.linuxfoundation.org/mailman/listinfo/oss-health-metrics), Submit a pull request. 

## Building Changes
After making your changes, run 
```bash
make build
```  
to update the docs and frontend before adding them to your staging area.
```
```

## Augur Development Overview

### Augur's Design Value System
Augur's architecture is designed with an eye toward fulfilling its primary missions of rapid open source software metric prototyping and using data visualization to facilitate discussions among folks who manage open source communities. 

Core aims: 

1. Rapid metrics prototyping
1. Using data visualization to support discussion

Our visualization design follows two principles:

1. Allow comparisons across projects
2. Where logical, show trends over time on a metric

Project comparison helps people understand what a metric tells them.  If I show you total commits in a month or a year, what does that tell you about the health of an open source project?  If  you are able to compare a project you are managing with a project or two in the same space that you are familiar with, is that helpful? In most cases the answers are yes. We aim to produce not only metrics, but enough information for consumers of Augur to construct meaning. Which then helps the CHAOSS community build better, more useful metrics. 

Time is, in effect, a project focused type of comparison. If you can see the changes in different metrics on your project over time, its easier to maintain awareness of how metrics compare with results. 

For futher instructions on how to add to Augur, here are guides to adding an endpoint to the full stack. 

### Augur's Architecture
In our aspiration to implement our value system for metrics in software, we seperate concerns pragmatically.  Any metrics dashboard system has to do 4 things: 1) Ingest data, 2) store data, 3) reshape data for analysis and 4) present data. Of course, these "dashboard requirements" can be interpreted and circumvented.  For example, if robust API's are available, like the [GitHub Version 4 API](https://developer.github.com/v4/), persistence can be considered optional. 

Right now, Augur satisfies the enumerated dashboard system requirements in concrete ways we describe in the following four sections. 

#### Augur Data Ingestion
We use the GHTorrent database, or its MSR14 little brother to help you get up and running quickly. You may find this dataset insufficient for a particular metric you want to build. API's available from a number of places can be accessed from Augur. 

Inside your Augur system root directory there is another directory named Augur.  This is where the python files that you can modify live.  

1. **downloads.py** : gathers download statistics for github repositories. Currently configured for npm and ruby gems download data. 
2. **ghtorrent.py** : reads the ghtorrent database you installed.  There are two functions at the top of this file that allow you to do counts on the GHTorrent Schema tables quickly using Python. 
    -     def __single_table_count_by_date(self, table, repo_col='project_id', user_col='author_id', group_by="week"): Generates query string to count occurances of rows per date for a given table.
    -     def __sub_table_count_by_date(self, parent_table, sub_table, parent_id, sub_id, project_id): Generates query string to count occurances of rows per date for a given query sub-table. A query sub-table is a table that describes in more detail a specfic asset of another query table-for example, the table "pull_request_comments" is a sub table of "pull_request", where the query is pull requests.
3. **ghtorrentplus.py** : Accesses the aggregate tables Augur creates for GHTorrent. 
4. **githubapi.py** : Pulls data from the GitHub API
5. **librariesio.py** : Pulls data from the libraries.io API (Package manager download data)
6. **localcsv.py** : Pulls data from a .csv file you persist. 
7. **publicwww.py** : Pulls download data from the https://publicwww.com website.

If you want to ingest substantial amounts of new data, you may want to contribute to the [Augur-OSSifragae](https://github.com/OSSHealth/augur-ossifragae) project, which focuses on systematic, structured ingestion of open source respository data from heterogeneous sources. (Note: an [Ossifragae](https://en.wikipedia.org/wiki/Bearded_Vulture) is a bearded vulture that is one of a handful of birds said to yield valid signs for ancient Roman Augurs (visionaries) to follow. We think the existance of "OSS" at the beginning of the birds name is a sign. We took it.)

#### Augur Data Storage
The database system that you built with GHTorrent or MSR14 is our principle data storage environment right now. We have added a few small details to the GHTorrent database in a seperate schema called GHTorrent_Plus.  This schema is built on deployment, and supports aggregations of the GHTorrent Schema information so that metrics can be generated more quickly in a few cases. 

#### Augur Data Reshaping for Analysis
Now that you understand the basic structure of Augur, our [Back End Development Guide](docs/dev-guide-pt1.md) will be the place to start for reshaping data and building out analysis endpoints. The end result of new back end code is a **REST API Endpoint.**

#### Augur Data Presentation 
Once you have a **REST API Endpoint**, you can stop and say, "I have built an endpoint. Here is my pull request".  OR, you can build front end visualizations for those endpoints, following our [Front End Development Guide](docs/dev-guide-pt2.md).

