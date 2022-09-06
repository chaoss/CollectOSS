List of Working Data Tables In Augur
===================================

**This Is A List of Working Tables In Augur and The Workers Attached to Them.**

    They are in lowercase to represent exactly how they look like on the actual table.

    * analysis_log - this table is a record of the analysis steps the facade worker has taken on an augur instance. A listing of all the analysis steps taken for every repository is recorded as they are completed.
        
        * Worker Associated With It? 

            * Facade Worker

                .. image:: analysis_log.png
                    :width: 200

    * commit_parents - this table keeps a record of parent commits that are squashed during Facade Worker execution.

                .. image:: commit_parents.png
                    :width: 200

    Other working tables are: 

    * exclude                
                .. image:: exclude.png
                    :width: 200

    * repos_fetch_log
                
                .. image:: repos_fetch_log.png
                    :width: 200

    * settings

                .. image:: settings.png
                    :width: 200

    * unknown_cache

                .. image:: unknown_cache.png
                    :width: 200

    * utility_log

                .. image:: utility_log.png
                    :width: 200

    * working_commits

                .. image:: working_commits.png
                    :width: 200
