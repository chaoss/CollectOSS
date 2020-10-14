-- #SPDX-License-Identifier: MIT
CREATE SEQUENCE "augur_data"."releases_release_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

CREATE TABLE "augur_data"."releases" (
  "release_id" int8 NOT NULL DEFAULT nextval('"augur_data".releases_release_id_seq'::regclass),
  "repo_id" int8 NOT NULL,
  "release_name" varchar(255) COLLATE "pg_catalog"."default",
  "release_description" varchar(255) COLLATE "pg_catalog"."default",
  "release_author" varchar(255) COLLATE "pg_catalog"."default",
  "release_created_at" timestamp(6),
  "release_published_at" timestamp(6),
  "release_updated_at" timestamp(6),
  "release_is_draft" bool,
  "release_is_prerelease" bool,
  "release_tag_name" varchar(255) COLLATE "pg_catalog"."default",
  "release_url" varchar(255) COLLATE "pg_catalog"."default",
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "releases_pkey" PRIMARY KEY ("release_id")
)
;

ALTER TABLE "augur_data"."releases" OWNER TO "augur";

ALTER TABLE "augur_data"."repo" ALTER COLUMN "forked_from" TYPE varchar COLLATE "pg_catalog"."default" USING "forked_from"::varchar;

SELECT setval('"augur_data"."releases_release_id_seq"', 1, false);

ALTER SEQUENCE "augur_data"."releases_release_id_seq"
OWNED BY "augur_data"."releases"."release_id";

ALTER SEQUENCE "augur_data"."releases_release_id_seq" OWNER TO "augur";

ALTER TABLE "augur_data"."releases" ADD CONSTRAINT "fk_releases_repo_1" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

update "augur_operations"."augur_settings" set value = 18 where setting = 'augur_data_version'; 
