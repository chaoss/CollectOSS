-- #SPDX-License-Identifier: MIT
BEGIN; 
ALTER TABLE "augur_data"."repo" 
  ALTER COLUMN "forked_from" TYPE varchar USING "forked_from"::varchar;

ALTER TABLE "augur_data"."repo" 
  ADD COLUMN IF NOT EXISTS "repo_archived" int4,
  ADD COLUMN IF NOT EXISTS "repo_archived_date_collected" timestamptz(0),
  ALTER COLUMN "forked_from" TYPE varchar USING "forked_from"::varchar;


INSERT INTO "augur_data"."repo" ("repo_id", "repo_group_id", "repo_git", "repo_path", "repo_name", "repo_added", "repo_status", "repo_type", "url", "owner_id", "description", "primary_language", "created_at", "forked_from", "updated_at", "tool_source", "tool_version", "data_source", "data_collection_date", "repo_archived", "repo_archived_date_collected") VALUES (1, 1, 'https://github.com/chaoss/augur', NULL, NULL, '2021-08-10 14:28:44', 'New', '', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'data load', 'one', 'git', '2021-06-05 18:41:14', NULL, NULL);
INSERT INTO "augur_data"."repo" ("repo_id", "repo_group_id", "repo_git", "repo_path", "repo_name", "repo_added", "repo_status", "repo_type", "url", "owner_id", "description", "primary_language", "created_at", "forked_from", "updated_at", "tool_source", "tool_version", "data_source", "data_collection_date", "repo_archived", "repo_archived_date_collected") VALUES (2, 1, 'https://github.com/saltstack/salt', NULL, NULL, '2021-08-10 17:58:43', 'New', '', NULL, NULL, NULL, NULL, NULL, 'Parent not available', NULL, NULL, NULL, NULL, NULL, 0, NULL);

COMMIT; 

BEGIN; 

update "augur_operations"."augur_settings" set value = 17 where setting = 'augur_data_version'; 

COMMIT; 