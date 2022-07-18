BEGIN; 
DROP INDEX "augur_data"."committer_affiliation";

CREATE INDEX "committer_affiliation" ON "augur_data"."commits" USING hash (
  "cmt_committer_affiliation" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops"
);

update "augur_operations"."augur_settings" set value = 87 where setting = 'augur_data_version'; 


COMMIT; 