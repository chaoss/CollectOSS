ALTER TABLE "augur_data"."issues" ADD CONSTRAINT "fk_issues_repo" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE CASCADE ON UPDATE CASCADE;
update "augur_operations"."augur_settings" set value = 9 where setting = 'augur_data_version'; 


	-- Index Update for Performance 
CREATE INDEX "reponameindex" ON "augur_data"."repo" USING hash (
  "repo_name"
);

CREATE INDEX "reponameindexbtree" ON "augur_data"."repo" USING btree (
  "repo_name"
);

CREATE INDEX "rgnameindex" ON "augur_data"."repo_groups" USING btree (
  "rg_name" ASC
);

CREATE INDEX "rggrouponrepoindex" ON "augur_data"."repo" USING btree (
  "repo_group_id"
);

CREATE INDEX "repogitindexrep" ON "augur_data"."repo" USING btree (
  "repo_git"
);