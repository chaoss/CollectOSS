-- #SPDX-License-Identifier: MIT
-- SPDX Updates

CREATE SEQUENCE "spdx"."projects_package_id_seq_tw0" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;


ALTER TABLE "spdx"."files" DROP CONSTRAINT  if exists  "files_project_id_fkey";

ALTER TABLE "spdx"."files" ADD COLUMN "package_id" int4;

ALTER TABLE "spdx"."files" DROP COLUMN "project_id";

ALTER TABLE "spdx"."projects" DROP CONSTRAINT if exists  "projects_pkey";

ALTER TABLE "spdx"."projects" ADD COLUMN "package_id" int4 NOT NULL DEFAULT nextval('"spdx".projects_package_id_seq'::regclass);

ALTER TABLE "spdx"."projects" DROP COLUMN "project_id";

ALTER TABLE "spdx"."projects" ADD CONSTRAINT "projects_pkey" PRIMARY KEY ("package_id");

SELECT setval('"spdx"."projects_package_id_seq"', 1000000, false);

ALTER SEQUENCE "spdx"."projects_package_id_seq"
OWNED BY "spdx"."projects"."package_id";

ALTER SEQUENCE "spdx"."projects_package_id_seq" OWNER TO "augur";



