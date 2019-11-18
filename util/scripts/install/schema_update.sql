ALTER TABLE "augur_data"."contributors_aliases" ALTER COLUMN "data_collection_date" SET DEFAULT CURRENT_TIMESTAMP;

CREATE SEQUENCE "spdx"."projects_package_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

ALTER TABLE "spdx"."files" DROP CONSTRAINT "files_project_id_fkey";

ALTER TABLE "spdx"."files" ADD COLUMN "package_id" int4;

ALTER TABLE "spdx"."files" DROP COLUMN "project_id";

ALTER TABLE "spdx"."projects" DROP CONSTRAINT "projects_pkey";

ALTER TABLE "spdx"."projects" ADD COLUMN "package_id" int4 NOT NULL DEFAULT nextval('"spdx".projects_package_id_seq'::regclass);

ALTER TABLE "spdx"."projects" DROP COLUMN "project_id";

ALTER TABLE "spdx"."projects" ADD CONSTRAINT "projects_pkey" PRIMARY KEY ("package_id");

SELECT setval('"spdx"."projects_package_id_seq"', 1, false);

ALTER SEQUENCE "spdx"."projects_package_id_seq"
OWNED BY "spdx"."projects"."package_id";

ALTER SEQUENCE "spdx"."projects_package_id_seq" OWNER TO "augur";

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

-- Repo Badging Table Update. 

drop table repo_badging; 

CREATE TABLE augur_data.repo_badging
(
    badge_collection_id bigint NOT NULL DEFAULT nextval('augur_data.repo_badging_badge_collection_id_seq'::regclass),
    repo_id bigint,
    data jsonb,
	created_at timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP,
    tool_source character varying(255) COLLATE pg_catalog."default",
    tool_version character varying(255) COLLATE pg_catalog."default",
    data_source character varying(255) COLLATE pg_catalog."default",
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE "augur_data"."repo_badging" OWNER TO "augur";

-- ----------------------------
-- Primary Key structure for table repo_badging
-- ----------------------------
ALTER TABLE "augur_data"."repo_badging" ADD CONSTRAINT "repo_badging_pkey" PRIMARY KEY ("badge_collection_id");

-- ----------------------------
-- Foreign Keys structure for table repo_badging
-- ----------------------------
ALTER TABLE "augur_data"."repo_badging" ADD CONSTRAINT "fk_repo_badging_repo_1" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

GRANT ALL ON TABLE augur_data.repo_badging TO augur;

COMMENT ON TABLE augur_data.repo_badging
    IS 'This will be collected from the LF’s Badging API
https://bestpractices.coreinfrastructure.org/projects.json?pq=https%3A%2F%2Fgithub.com%2Fchaoss%2Faugur
';




