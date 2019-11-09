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

-- Index Update for Performance. 
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





