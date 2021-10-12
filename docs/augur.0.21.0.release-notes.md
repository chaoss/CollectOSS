# Issues Closed:

1424,
1423,
1369,
1368,
1367,
1357,
1348,
1338

# Release Contents:
1. Fully implemented natural keys at the database level
2. Significant advances on the resolution of contributors, and elimination of duplicate entries for the same user. 
    - You will now have users resolved to the contributors table, with email aliases pulled from git logs in the contributor_aliases table. 
    - For users whose git commit emails are not resolved by platform APIs, there is now an unresolved_commit_emails. These can typically be mapped as additions to the contributor_affiliations table to be resolved during commit counting. In most cases an organization can identify its own people if they are not automatically resolved (during testing we automatically identified and mapped 88.5% of contributors.)
3. Full release of dependency workers. This includes: 
    - Full implementation of OSSF_Scorecard
    - Dependency Tree Counts for each project for 10 languages
    - Implementation of the LibYear metric for javascript and python
4. Automatic updating of the default branch when it changes on a platform; for example, when making a change from the previous default of master, to main, Augur handles this for you. 
5. Optional automatic addition of new repos added to a GitHub organization
6. A new user interface option. Introducing "Augur View"!
7. Improvements to documentation, especially the API Documentation 
8. Error handled added throughout data collection process 
9. Refactored worker codebase to be easier to maintain 