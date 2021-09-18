-- #SPDX-License-Identifier: MIT
BEGIN; 
ALTER TABLE "augur_data"."repo" 
  ALTER COLUMN "forked_from" TYPE varchar USING "forked_from"::varchar;

ALTER TABLE "augur_data"."repo" 
  ADD COLUMN IF NOT EXISTS "repo_archived" int4,
  ADD COLUMN IF NOT EXISTS "repo_archived_date_collected" timestamptz(0),
  ALTER COLUMN "forked_from" TYPE varchar USING "forked_from"::varchar;


INSERT INTO "augur_data"."repo" ("repo_id", "repo_group_id", "repo_git", "repo_path", "repo_name", "repo_added", "repo_status", "repo_type", "url", "owner_id", "description", "primary_language", "created_at", "forked_from", "updated_at", "tool_source", "tool_version", "data_source", "data_collection_date", "repo_archived", "repo_archived_date_collected") VALUES (1, 1, 'https://github.com/chaoss/augur', NULL, NULL, '2021-08-10 14:28:44', 'New', '', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'data load', 'one', 'git', '2021-06-05 18:41:14', NULL, NULL);



INSERT INTO "augur_data"."repo_groups" ("repo_group_id", "rg_name", "rg_description", "rg_website", "rg_recache", "rg_last_modified", "rg_type", "tool_source", "tool_version", "data_source", "data_collection_date") VALUES (25155, 'chaoss', 'CHAOSS PROJECT Repos', 'https://chaoss.community', 0, '2021-09-13 11:40:32', 'CHAOSS Base', 'Loaded by user', '1.0', 'Git', '2020-04-17 21:40:32');
INSERT INTO "augur_data"."repo_groups" ("repo_group_id", "rg_name", "rg_description", "rg_website", "rg_recache", "rg_last_modified", "rg_type", "tool_source", "tool_version", "data_source", "data_collection_date") VALUES (20000, 'chaoss', 'CHAOSS PROJECT Repos', 'https://chaoss.community', 0, '2021-09-13 11:40:32', 'CHAOSS Base', 'Loaded by user', '1.0', 'Git', '2020-04-17 21:40:32');


INSERT INTO "augur_data"."repo" ("repo_id", "repo_group_id", "repo_git", "repo_path", "repo_name", "repo_added", "repo_status", "repo_type", "url", "owner_id", "description", "primary_language", "created_at", "forked_from", "updated_at", "tool_source", "tool_version", "data_source", "data_collection_date", "repo_archived", "repo_archived_date_collected") VALUES (25445, 25155, 'https://github.com/chaoss/grimoirelab-perceval-opnfv', 'github.com/chaoss/', 'grimoirelab-perceval-opnfv', '2020-04-17 21:40:39', 'Complete', '', NULL, NULL, NULL, NULL, NULL, 'Parent not available', NULL, 'CLI', '1.0', 'Git', '2020-04-17 21:40:39', 0, NULL);
INSERT INTO "augur_data"."repo" ("repo_id", "repo_group_id", "repo_git", "repo_path", "repo_name", "repo_added", "repo_status", "repo_type", "url", "owner_id", "description", "primary_language", "created_at", "forked_from", "updated_at", "tool_source", "tool_version", "data_source", "data_collection_date", "repo_archived", "repo_archived_date_collected") VALUES (25450, 25155, 'https://github.com/chaoss/grimoirelab-hatstall', 'github.com/chaoss/', 'grimoirelab-hatstall', '2020-04-17 21:40:42', 'Complete', '', NULL, NULL, NULL, NULL, NULL, 'Parent not available', NULL, 'CLI', '1.0', 'Git', '2020-04-17 21:40:42', 0, NULL);
INSERT INTO "augur_data"."repo" ("repo_id", "repo_group_id", "repo_git", "repo_path", "repo_name", "repo_added", "repo_status", "repo_type", "url", "owner_id", "description", "primary_language", "created_at", "forked_from", "updated_at", "tool_source", "tool_version", "data_source", "data_collection_date", "repo_archived", "repo_archived_date_collected") VALUES (25452, 25155, 'https://github.com/chaoss/whitepaper', 'github.com/chaoss/', 'whitepaper', '2020-04-17 21:40:42', 'Complete', '', NULL, NULL, NULL, NULL, NULL, 'Parent not available', NULL, 'CLI', '1.0', 'Git', '2020-04-17 21:40:42', 0, NULL);

INSERT INTO "augur_data"."repo" ("repo_id", "repo_group_id", "repo_git", "repo_path", "repo_name", "repo_added", "repo_status", "repo_type", "url", "owner_id", "description", "primary_language", "created_at", "forked_from", "updated_at", "tool_source", "tool_version", "data_source", "data_collection_date", "repo_archived", "repo_archived_date_collected") VALUES (24441, 20000, 'https://github.com/operate-first/operate-first-twitter', 'github.com/operate-first/', 'operate-first-twitter', '2021-08-25 16:47:47', 'Complete', '', NULL, NULL, NULL, NULL, NULL, 'Parent not available', NULL, 'CLI', '1.0', 'Git', '2021-08-25 16:47:47', 0, NULL);
INSERT INTO "augur_data"."repo" ("repo_id", "repo_group_id", "repo_git", "repo_path", "repo_name", "repo_added", "repo_status", "repo_type", "url", "owner_id", "description", "primary_language", "created_at", "forked_from", "updated_at", "tool_source", "tool_version", "data_source", "data_collection_date", "repo_archived", "repo_archived_date_collected") VALUES (24442, 20000, 'https://github.com/operate-first/blueprint', 'github.com/operate-first/', 'blueprint', '2021-08-25 16:47:47', 'Complete', '', NULL, NULL, NULL, NULL, NULL, 'Parent not available', NULL, 'CLI', '1.0', 'Git', '2021-08-25 16:47:47', 0, NULL);


COMMIT; 

BEGIN; 

update "augur_operations"."augur_settings" set value = 17 where setting = 'augur_data_version'; 

COMMIT; 