List of Regularly Used Data Tables In Augur
===========================================

** This is a list of data tables in augur that are regularly used and the various workers attached to them. **

* Commits - This is where a record for every file in every commit in every repository in an Augur instance is kept. 
    
    * Worker: Facade worker collects, and also stores platform user information in the commits table. 

* Contributor_affiliations: A list of emails and domains, with start and end dates for individuals to have an organizational affiliation. 
    
    * Populated by default when augur is installed
    * Can be edited so that an Augur instance can resolve a larger list of affiliations. 
    * These mappings are summarized in the dm_ tables. 

* Contributor_repo - Storage of a snowball sample of all the repositories anyone in your schema has accessed on GitHub. So, for example, if you wanted to know all the repositories that people on your project contributed to, this would be the table. 
    
    * Contributor_breadth_worker populates this table
    * Population of this table happens last, and can take a long time. 

* Contributors - These are all the contributors to a project/repo. In Augur, all types of contributions create a contributor record. This includes issue comments, pull request comments, label addition, etc. This is different than how GitHub counts contributors; they only include committers. 
    
    * Workers Adding Contributors: 

        * Github Issue Worker
        * Pull Request Worker
        * GitLab Issue Worker
        * GitLab Merge Request Worker
        * Facade Worker 
