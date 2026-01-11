[33m39546e8ca[m[33m ([m[1;36mHEAD[m[33m -> [m[1;32mdocs/readme-cleanup[m[33m, [m[1;31morigin/docs/readme-cleanup[m[33m)[m docs: address review feedback in README
[33mb3b0db73e[m docs: minor README cleanup and clarification
[33m76b520db6[m[33m ([m[1;31morigin/main[m[33m, [m[1;31morigin/HEAD[m[33m, [m[1;32mmain[m[33m)[m Merge pull request #3481 from PredictiveManish/Redis-update
[33mf876f98ed[m Merge pull request #3484 from chaoss/readme-typo
[33m49af484d2[m update Code of Conduct link
[33md410b3b9c[m Fix broken 8knot link in README Signed-off-by: Kushagra <Kushagrabhargava93@gmail.com> Signed-off-by: Adrian Edwards <adredwar@redhat.com>
[33mffd250598[m fix: Updated links for Redis Installation
[33m629da3a8a[m Fix: Updated link of redis windows installation
[33mb67cb6f85[m Merge pull request #3344 from chaoss/toml-swap
[33m1963924f2[m Merge pull request #3412 from shlokgilda/fix/issue-3401-database-connection-leaks
[33m28bc9d469[m Merge pull request #3439 from shlokgilda/fix/pr-reviews-batched-processing
[33mabec3f17f[m Merge pull request #3353 from chaoss/commit-message-toggle
[33m6f9ebefd0[m Merge branch 'main' into fix/pr-reviews-batched-processing
[33m2e6308efa[m Merge pull request #3466 from shlokgilda/fix/issue-3455-releases-null-target
[33mc0fc44036[m Merge pull request #3424 from shlokgilda/fix/issue-3404-large-in-memory-lists
[33m59bd91826[m Fix null target check in get_release_inf function
[33m1cab8cea7[m remove import from within function
[33m0f27edea9[m tomli only needed on older python versions since its part of the standard lib since 3.11
[33m9553151e1[m use built in tomllib instead
[33m539536940[m swap toml package in dependencies
[33m29edd21a1[m swap code to using tomli
[33mfad9eadc4[m Merge branch 'fix/issue-3404-large-in-memory-lists' of github.com:shlokgilda/augur into fix/issue-3404-large-in-memory-lists
[33mf9052cbfe[m Pylint and other style fixes
[33mb5eac7a48[m fix: Optimize database cursor usage by fetching results immediately in insert_facade_contributors
[33m0d068dc8c[m Update augur/tasks/github/issues.py
[33mab2fd7b72[m Update augur/tasks/github/issues.py
[33m44e6967d7[m fix: Add batch processing to PR commits and files collection
[33m7f502bd94[m fix: Convert issues collection to generator pattern with batching
[33m836544d9d[m fix: Process facade contributor results in batches
[33m79fa27981[m fix: Use list.clear() in facade tasks to reduce memory overhead
[33m7dcc2822b[m Merge pull request #3420 from shlokgilda/fix/git-deadlock-issue
[33m289038954[m Merge branch 'main' into fix/pr-reviews-batched-processing
[33m9214819bf[m Merge branch 'main' into fix/issue-3404-large-in-memory-lists
[33m52e88f5b2[m Merge branch 'main' into fix/git-deadlock-issue
[33m34f5644e2[m Merge pull request #3450 from chaoss/ntdn/consistent-sa-model-setup
[33mc7c860a60[m Merge branch 'main' into fix/pr-reviews-batched-processing
[33mdf51d587a[m Merge pull request #3438 from chaoss/null_string_fix
[33m134facd36[m Merge pull request #3436 from chaoss/ntdn/old_schemas
[33mf2929f764[m table_args formatting
[33m1acb41bbd[m formatting: move table name and schema attributes up top for consistency
[33m4d10fc13b[m Implement batched processing for pull request reviews and contributors
[33m1a52bf505[m Update augur/tasks/git/util/facade_worker/facade_worker/config.py
[33mc39b9f290[m[33m ([m[1;31morigin/null_string_fix[m[33m)[m specify `pr_review_body` as a User generated content string field for cleaning
[33maac134ea9[m remove three files that are entirely comments
[33m1ccc8dd1e[m Pylint and other style fixes
[33m7bf42a373[m refactor subprocess.run calls in FacadeHelper to use common options
[33mf8f06a259[m refactor git command execution to use unified timeout handling across facade operation
[33m6365814fd[m fix: Optimize database cursor usage by fetching results immediately in insert_facade_contributors
[33m11019b796[m Update augur/tasks/github/issues.py
[33ma2c1b78a4[m Update augur/tasks/github/issues.py
[33m40f9fab2e[m fix: Add batch processing to PR commits and files collection
[33m05165f108[m fix: Convert issues collection to generator pattern with batching
[33m19d0a9b37[m fix: Process facade contributor results in batches
[33m0d487afd9[m fix: Use list.clear() in facade tasks to reduce memory overhead
[33m7aefd1bef[m Fix deadlock issues by implementing timeout handling for git operations
[33mf33054b13[m refactor DEI and user CLI functions to use context managers for database sessions and improve error handling
[33m3a97f18b2[m Merge pull request #3375 from shlokgilda/feature/issue-3310-dynamic-csv-columns
[33mf759e7060[m Merge pull request #3386 from AdeebaNizam404/docs/move-contributors-to-CONTRIBUTORS-md
[33mcc55864b0[m Merge pull request #3416 from chaoss/augur-auto-migrations
[33m134dc9078[m Merge pull request #3339 from chaoss/unused
[33m21a02b222[m Update John's name
[33m361dbf854[m python-dotenv is not just a dev dependency
[33mf41ed4e18[m Merge pull request #3409 from PredictiveManish/docs-collection
[33m31bd7f447[m remove unused imports per reviewdog
[33m0f7da8e33[m use the public schema by default for the version table schema.
[33m7b18880c5[m include schemas/be schema-aware in offline version of migrations too
[33mec7793da5[m update alembic
[33me286f8f53[m remove search paths "It can make reflection “lose” schema names. Remove the connect listener that sets search_path while generating migrations." - gpt5
[33m28fb8397d[m replace file contents-based revision check with one that just looks at the filenames
[33m0e54842c2[m set up alembic to automatically determine the next version number
[33m972303a4a[m remove date from migration filename format
[33m8f7368f62[m load from .env
[33md78f5dceb[m install python-dotenv
[33m95b2b7835[m connect up the url in another place to prevent errors about a missing config file
[33md704670fc[m Merge pull request #3408 from chaoss/migrate-topic-models-2
[33ma96942364[m docs: move contributor lists to CONTRIBUTORS.md and update README for clarity
[33m016ad79c2[m Merge branch 'chaoss:main' into docs-collection
[33m17963e42c[m Fix: collection_intervals into seconds
[33m6a406fd92[m[33m ([m[1;31morigin/migrate-topic-models-2[m[33m)[m Create a migration to synchronize the topic model tables
[33m6475b634c[m Merge pull request #3389 from chaoss/gunicorn-errors
[33m74da53843[m Merge pull request #3400 from shlokgilda/feature/issue-3392-too-many-clients
[33m1c0247db7[m Merge pull request #3405 from xiaoha-cloud/topic-modeling-schema-only
[33m2f83a2e05[m Add explicit Integer type to repo_id column
[33m382e7b7f5[m Add TopicModelEvent ORM model to augur_data.py
[33m15b2dcc6e[m move RepoLoadController within the database session context
[33m9fff7d8ad[m add unit tests for CSV processing utilities including validation and error handling
[33mb42333f62[m enhance type annotations and docstrings for CSV processing functions in cli
[33m515adc1bf[m improve CSV processing error handling and logging in db commands
[33mb2d061437[m remove header rows from test CSV files for repo groups and repos
[33m46e5b69fa[m add flexible column order support for CSV imports
[33m6b48ab604[m Merge pull request #3397 from xiaoha-cloud/topic-modeling-schema-only
[33m5248b075e[m Merge pull request #3399 from shlokgilda/feature/issue-3398-fix-test-typos
[33maa67f9b42[m chore: rely on SQLAlchemy TIMESTAMP type with timezone
[33mc952f662a[m fix: Use timezone-aware timestamps for topic modeling schema
[33mc64246264[m[33m ([m[1;31morigin/gunicorn-errors[m[33m)[m Detect docker environments and ensure gunicorn error logs end up in dockers log stream
[33ma96e62ff7[m fix incorrect path for worker persistence in pytest configuration
[33m6702c35cf[m refactor: Remove payload index to match Augur conventions
[33md40e9acb9[m fix typos in the tests folder.
[33md20c672e5[m feat: Add Topic Modeling database schema tables
[33m4732c8090[m[33m ([m[1;33mtag: [m[1;33mv0.91.0[m[33m)[m updated the version in README.md
[33m