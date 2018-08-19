# Augur Development Guide: Making Contributions

## Getting Started
See our [Contributing to Augur](/CONTRIBUTING.md) guide for specifics on how we review pull requests. tl;dr: Fork our repo. Make a change. Use the mailing list for [CHAOSS](https://lists.linuxfoundation.org/mailman/listinfo/oss-health-metrics), Submit a pull request. 

## Building Changes
After making your changes, run 
```bash
make build
```  
to update the docs and frontend before adding them to your staging area.
```
```

## Augur Development Overview

### tl;dr
  1. [Back End Development Guide](/docs/dev-guide-pt1.md) 
  2. [Front End Development Guide](/docs/dev-guide-pt2.md)
---------------------

### Augur's Design Value System
Augur's architecture is designed with an eye toward fulfilling its primary missions of rapid open source software metric prototyping and using data visualization to facilitate discussions among folks who manage open source communities. 

**Core aims: **
  1. Rapid metrics prototyping
  2. Using data visualization to support discussion

**Our visualization design follows two principles:**
  1. Allow comparisons across projects
  2. Where logical, show trends over time on a metric

Project comparison helps people understand what a metric tells them.  If I show you total commits in a month or a year, what does that tell you about the health of an open source project?  If you are able to compare a project you are managing with a project or two in the same space that you are familiar with, is that helpful? In most cases the answers are yes. We aim to produce not only metrics, but enough information for consumers of Augur to construct meaning. Which then helps the CHAOSS community build better, more useful metrics. 

Time is, in effect, a project focused type of comparison. If you can see the changes in different metrics on your project over time, its easier to maintain awareness of how metrics compare with results. 

--------------------------------

## Augur's Architecture
In our aspiration to implement our value system for metrics in software, we seperate concerns pragmatically.  Any metrics dashboard system has to do 4 things: 1) Ingest data, 2) store data, 3) reshape data for analysis and 4) present data. Of course, these "dashboard requirements" can be interpreted and circumvented.  For example, if robust API's are available, like the [GitHub Version 4 API](https://developer.github.com/v4/), persistence can be considered optional. 

Right now, Augur satisfies the enumerated dashboard system requirements in concrete ways we describe in the following four sections. 

### Augur Data Ingestion
We use the GHTorrent database, or its MSR14 little brother to help you get up and running quickly. You may find this dataset insufficient for a particular metric you want to build. API's available from a number of places can be accessed from Augur. 

Inside your Augur system root directory there is another directory named Augur.  This is where the Python files that you can modify live. Each one of these files should correspond to a different data source.

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

### Augur Data Storage
The database system that you built with GHTorrent or MSR14 is our principle data storage environment right now. We have added a few small details to the GHTorrent database in a seperate schema called GHTorrent_Plus.  This schema is built on deployment, and supports aggregations of the GHTorrent Schema information so that metrics can be generated more quickly in a few cases. 

### Augur Data Reshaping for Analysis
Now that you understand the basic structure of Augur, our [Back End Development Guide](/docs/dev-guide-pt1.md) will be the place to start for reshaping data and building out analysis endpoints. The end result of new back end code is a **REST API Endpoint.**

### Augur Data Presentation 
Once you have a **REST API Endpoint**, you can stop and say, "I have built an endpoint. Here is my pull request".  OR, you can build front end visualizations for those endpoints, following our [Front End Development Guide](/docs/dev-guide-pt2.md).
---------------------
## Important notes about contributing metrics

Before we start, there are a few things we would like to go over. Please take the time to read this section carefully; not only will it will make your life much easier, but also the lives of all the other conributors!

When contributing a new metric, please reference [this list](https://github.com/OSSHealth/augur/blob/dev/docs/scratchpad/master-metrics-order.md) in order to make sure you are putting the metric in the correct spot in the code. With the amount of metrics we have already implemented and the ones we plan to implement, **it is imperative that you stick to this order**, as this helps contributors both new and old maintain clarity and order when working with metrics. 

Some of the metrics we develop are defined more formally by metrics committees and working groups; some are not. Should you choose to work on implementing any of these metrics that are formally defined, they should be placed under their respective category.

If you are adding a new metric that does **not** fall under one of these categories, it should be placed in the Experimental group in the correct sub-category. If you would like to add a new Experimental sub-category, please open a pull request with your proposed addition. In addition, please update the file mentioned above to include your new metric: it can be found at `augur/docs/scratchpad/master-metrics-order.md`.

This order is followed across the project. Data source files, test files, `server.py`, `AugurAPI.js`, frontend cards, and other places that metrics appear in should adhere to this order for maximum uniformity (In `AugurAPI.js`, Git metrics have their own section).

Files where metrics appear should include a header for every group, even if there are no relevant metrics in that group. The exception to the rule are the frontend tab cards; these are already grouped.

