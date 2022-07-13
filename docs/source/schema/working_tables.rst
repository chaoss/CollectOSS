List of Working Data Tables In Augur
===================================

**This Is A List of Working Tables In Augur and The Workers Attached to Them.**

    They are in lowercase to represent exactly how they look like on the actual table.

    * analysis_log - this table is a record of the analysis steps the facade worker has taken on an augur instance. A listing of all the analysis steps taken for every repository is recorded as they are completed.
        
        * Worker Associated With It? 

            * Facade Worker

    * commit_parents - this table keeps a record of parent commits that are squashed during Facade Worker execution.
        
        * Worker Associated With It? 

            * Facade Worker
    
    Other working tables are: 

    * exclude
    * repos_fetch_log
    * settings
    * unknown_cache
    * utility_log
    * working_commits
