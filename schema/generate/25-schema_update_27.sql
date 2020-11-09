ALTER TABLE "spdx"."file_types" DROP CONSTRAINT IF EXISTS "uc_file_type_name";

ALTER TABLE "spdx"."file_types" DROP CONSTRAINT IF EXISTS "file_types_pkey" CASCADE;

ALTER TABLE "spdx"."file_types" ALTER COLUMN "file_type_id" DROP NOT NULL;

ALTER TABLE "spdx"."file_types" ALTER COLUMN "file_type_id" DROP DEFAULT;

ALTER TABLE "spdx"."file_types" ADD CONSTRAINT "uc_file_type_name" PRIMARY KEY ("name");

ALTER TABLE "spdx"."files" ALTER COLUMN "file_type_id" DROP NOT NULL;

ALTER TABLE "spdx"."identifiers" DROP CONSTRAINT IF EXISTS "ck_identifier_exactly_one";

ALTER TABLE "spdx"."identifiers" ADD CONSTRAINT "ck_identifier_exactly_one" CHECK (((document_id IS NOT NULL)::integer + (package_id IS NOT NULL)::integer + (package_file_id IS NOT NULL)::integer) = 1);

ALTER TABLE "spdx"."packages" DROP CONSTRAINT IF EXISTS "uc_sha256_ds2_dir_code_exactly_one";

ALTER TABLE "spdx"."packages" ADD CONSTRAINT "uc_sha256_ds2_dir_code_exactly_one" CHECK (((sha256 IS NOT NULL)::integer + (dosocs2_dir_code IS NOT NULL)::integer) = 1);

ALTER TABLE "spdx"."identifiers" DROP CONSTRAINT IF EXISTS "ck_identifier_exactly_one";

ALTER TABLE "spdx"."identifiers" ADD CONSTRAINT "ck_identifier_exactly_one" CHECK ((((((document_id IS NOT NULL))::integer + ((package_id IS NOT NULL))::integer) + ((package_file_id IS NOT NULL))::integer) = 1));

ALTER TABLE "spdx"."packages" DROP CONSTRAINT IF EXISTS "uc_sha256_ds2_dir_code_exactly_one";

ALTER TABLE "spdx"."packages" ADD CONSTRAINT "uc_sha256_ds2_dir_code_exactly_one" CHECK (((((sha256 IS NOT NULL))::integer + ((dosocs2_dir_code IS NOT NULL))::integer) = 1));

update "augur_operations"."augur_settings" set value = 27 where setting = 'augur_data_version'; 
