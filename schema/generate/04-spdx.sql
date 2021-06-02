-- #SPDX-License-Identifier: MIT
-- ----------------------------
-- Sequence structure for annotation_types_annotation_type_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."annotation_types_annotation_type_id_seq";
CREATE SEQUENCE "spdx"."annotation_types_annotation_type_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."annotation_types_annotation_type_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for annotations_annotation_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."annotations_annotation_id_seq";
CREATE SEQUENCE "spdx"."annotations_annotation_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."annotations_annotation_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for augur_repo_map_map_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."augur_repo_map_map_id_seq";
CREATE SEQUENCE "spdx"."augur_repo_map_map_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."augur_repo_map_map_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for creator_types_creator_type_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."creator_types_creator_type_id_seq";
CREATE SEQUENCE "spdx"."creator_types_creator_type_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."creator_types_creator_type_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for creators_creator_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."creators_creator_id_seq";
CREATE SEQUENCE "spdx"."creators_creator_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."creators_creator_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for document_namespaces_document_namespace_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."document_namespaces_document_namespace_id_seq";
CREATE SEQUENCE "spdx"."document_namespaces_document_namespace_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."document_namespaces_document_namespace_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for documents_creators_document_creator_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."documents_creators_document_creator_id_seq";
CREATE SEQUENCE "spdx"."documents_creators_document_creator_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."documents_creators_document_creator_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for documents_document_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."documents_document_id_seq";
CREATE SEQUENCE "spdx"."documents_document_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."documents_document_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for external_refs_external_ref_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."external_refs_external_ref_id_seq";
CREATE SEQUENCE "spdx"."external_refs_external_ref_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."external_refs_external_ref_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for file_contributors_file_contributor_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."file_contributors_file_contributor_id_seq";
CREATE SEQUENCE "spdx"."file_contributors_file_contributor_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."file_contributors_file_contributor_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for file_types_file_type_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."file_types_file_type_id_seq";
CREATE SEQUENCE "spdx"."file_types_file_type_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."file_types_file_type_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for files_file_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."files_file_id_seq";
CREATE SEQUENCE "spdx"."files_file_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."files_file_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for files_licenses_file_license_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."files_licenses_file_license_id_seq";
CREATE SEQUENCE "spdx"."files_licenses_file_license_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."files_licenses_file_license_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for files_scans_file_scan_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."files_scans_file_scan_id_seq";
CREATE SEQUENCE "spdx"."files_scans_file_scan_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."files_scans_file_scan_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for identifiers_identifier_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."identifiers_identifier_id_seq";
CREATE SEQUENCE "spdx"."identifiers_identifier_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."identifiers_identifier_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for licenses_license_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."licenses_license_id_seq";
CREATE SEQUENCE "spdx"."licenses_license_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."licenses_license_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for packages_files_package_file_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."packages_files_package_file_id_seq";
CREATE SEQUENCE "spdx"."packages_files_package_file_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."packages_files_package_file_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for packages_package_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."packages_package_id_seq";
CREATE SEQUENCE "spdx"."packages_package_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."packages_package_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for packages_scans_package_scan_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."packages_scans_package_scan_id_seq";
CREATE SEQUENCE "spdx"."packages_scans_package_scan_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."packages_scans_package_scan_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for projects_package_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."projects_package_id_seq";
CREATE SEQUENCE "spdx"."projects_package_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."projects_package_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for relationship_types_relationship_type_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."relationship_types_relationship_type_id_seq";
CREATE SEQUENCE "spdx"."relationship_types_relationship_type_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."relationship_types_relationship_type_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for relationships_relationship_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."relationships_relationship_id_seq";
CREATE SEQUENCE "spdx"."relationships_relationship_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."relationships_relationship_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for scanners_scanner_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."scanners_scanner_id_seq";
CREATE SEQUENCE "spdx"."scanners_scanner_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."scanners_scanner_id_seq" OWNER TO "augur";

-- ----------------------------
-- Table structure for annotation_types
-- ----------------------------
DROP TABLE IF EXISTS "spdx"."annotation_types";
CREATE TABLE "spdx"."annotation_types" (
  "annotation_type_id" int4 NOT NULL DEFAULT nextval('"spdx".annotation_types_annotation_type_id_seq'::regclass),
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL
)
;
ALTER TABLE "spdx"."annotation_types" OWNER TO "augur";

-- ----------------------------
-- Table structure for annotations
-- ----------------------------
DROP TABLE IF EXISTS "spdx"."annotations";
CREATE TABLE "spdx"."annotations" (
  "annotation_id" int4 NOT NULL DEFAULT nextval('"spdx".annotations_annotation_id_seq'::regclass),
  "document_id" int4 NOT NULL,
  "annotation_type_id" int4 NOT NULL,
  "identifier_id" int4 NOT NULL,
  "creator_id" int4 NOT NULL,
  "created_ts" timestamptz(6),
  "comment" text COLLATE "pg_catalog"."default" NOT NULL
)
;
ALTER TABLE "spdx"."annotations" OWNER TO "augur";

-- ----------------------------
-- Table structure for augur_repo_map
-- ----------------------------
DROP TABLE IF EXISTS "spdx"."augur_repo_map";
CREATE TABLE "spdx"."augur_repo_map" (
  "map_id" int4 NOT NULL DEFAULT nextval('"spdx".augur_repo_map_map_id_seq'::regclass),
  "dosocs_pkg_id" int4,
  "dosocs_pkg_name" text COLLATE "pg_catalog"."default",
  "repo_id" int4,
  "repo_path" text COLLATE "pg_catalog"."default"
)
;
ALTER TABLE "spdx"."augur_repo_map" OWNER TO "augur";

-- ----------------------------
-- Table structure for creator_types
-- ----------------------------
DROP TABLE IF EXISTS "spdx"."creator_types";
CREATE TABLE "spdx"."creator_types" (
  "creator_type_id" int4 NOT NULL DEFAULT nextval('"spdx".creator_types_creator_type_id_seq'::regclass),
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL
)
;
ALTER TABLE "spdx"."creator_types" OWNER TO "augur";

-- ----------------------------
-- Table structure for creators
-- ----------------------------
DROP TABLE IF EXISTS "spdx"."creators";
CREATE TABLE "spdx"."creators" (
  "creator_id" int4 NOT NULL DEFAULT nextval('"spdx".creators_creator_id_seq'::regclass),
  "creator_type_id" int4 NOT NULL,
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "email" varchar(255) COLLATE "pg_catalog"."default" NOT NULL
)
;
ALTER TABLE "spdx"."creators" OWNER TO "augur";

-- ----------------------------
-- Table structure for document_namespaces
-- ----------------------------
DROP TABLE IF EXISTS "spdx"."document_namespaces";
CREATE TABLE "spdx"."document_namespaces" (
  "document_namespace_id" int4 NOT NULL DEFAULT nextval('"spdx".document_namespaces_document_namespace_id_seq'::regclass),
  "uri" varchar(500) COLLATE "pg_catalog"."default" NOT NULL
)
;
ALTER TABLE "spdx"."document_namespaces" OWNER TO "augur";

-- ----------------------------
-- Table structure for documents
-- ----------------------------
DROP TABLE IF EXISTS "spdx"."documents";
CREATE TABLE "spdx"."documents" (
  "document_id" int4 NOT NULL DEFAULT nextval('"spdx".documents_document_id_seq'::regclass),
  "document_namespace_id" int4 NOT NULL,
  "data_license_id" int4 NOT NULL,
  "spdx_version" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "license_list_version" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "created_ts" timestamptz(6) NOT NULL,
  "creator_comment" text COLLATE "pg_catalog"."default" NOT NULL,
  "document_comment" text COLLATE "pg_catalog"."default" NOT NULL,
  "package_id" int4 NOT NULL
)
;
ALTER TABLE "spdx"."documents" OWNER TO "augur";

-- ----------------------------
-- Table structure for documents_creators
-- ----------------------------
DROP TABLE IF EXISTS "spdx"."documents_creators";
CREATE TABLE "spdx"."documents_creators" (
  "document_creator_id" int4 NOT NULL DEFAULT nextval('"spdx".documents_creators_document_creator_id_seq'::regclass),
  "document_id" int4 NOT NULL,
  "creator_id" int4 NOT NULL
)
;
ALTER TABLE "spdx"."documents_creators" OWNER TO "augur";

-- ----------------------------
-- Table structure for external_refs
-- ----------------------------
DROP TABLE IF EXISTS "spdx"."external_refs";
CREATE TABLE "spdx"."external_refs" (
  "external_ref_id" int4 NOT NULL DEFAULT nextval('"spdx".external_refs_external_ref_id_seq'::regclass),
  "document_id" int4 NOT NULL,
  "document_namespace_id" int4 NOT NULL,
  "id_string" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "sha256" varchar(64) COLLATE "pg_catalog"."default" NOT NULL
)
;
ALTER TABLE "spdx"."external_refs" OWNER TO "augur";

-- ----------------------------
-- Table structure for file_contributors
-- ----------------------------
DROP TABLE IF EXISTS "spdx"."file_contributors";
CREATE TABLE "spdx"."file_contributors" (
  "file_contributor_id" int4 NOT NULL DEFAULT nextval('"spdx".file_contributors_file_contributor_id_seq'::regclass),
  "file_id" int4 NOT NULL,
  "contributor" text COLLATE "pg_catalog"."default" NOT NULL
)
;
ALTER TABLE "spdx"."file_contributors" OWNER TO "augur";

-- ----------------------------
-- Table structure for file_types
-- ----------------------------
DROP TABLE IF EXISTS "spdx"."file_types";
CREATE TABLE "spdx"."file_types" (
  "file_type_id" int4 NOT NULL DEFAULT nextval('"spdx".file_types_file_type_id_seq'::regclass),
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL
)
;
ALTER TABLE "spdx"."file_types" OWNER TO "augur";

-- ----------------------------
-- Table structure for files
-- ----------------------------
DROP TABLE IF EXISTS "spdx"."files";
CREATE TABLE "spdx"."files" (
  "file_id" int4 NOT NULL DEFAULT nextval('"spdx".files_file_id_seq'::regclass),
  "file_type_id" int4 NOT NULL,
  "sha256" varchar(64) COLLATE "pg_catalog"."default" NOT NULL,
  "copyright_text" text COLLATE "pg_catalog"."default",
  "package_id" int4,
  "comment" text COLLATE "pg_catalog"."default" NOT NULL,
  "notice" text COLLATE "pg_catalog"."default" NOT NULL
)
;
ALTER TABLE "spdx"."files" OWNER TO "augur";

-- ----------------------------
-- Table structure for files_licenses
-- ----------------------------
DROP TABLE IF EXISTS "spdx"."files_licenses";
CREATE TABLE "spdx"."files_licenses" (
  "file_license_id" int4 NOT NULL DEFAULT nextval('"spdx".files_licenses_file_license_id_seq'::regclass),
  "file_id" int4 NOT NULL,
  "license_id" int4 NOT NULL,
  "extracted_text" text COLLATE "pg_catalog"."default" NOT NULL
)
;
ALTER TABLE "spdx"."files_licenses" OWNER TO "augur";

-- ----------------------------
-- Table structure for files_scans
-- ----------------------------
DROP TABLE IF EXISTS "spdx"."files_scans";
CREATE TABLE "spdx"."files_scans" (
  "file_scan_id" int4 NOT NULL DEFAULT nextval('"spdx".files_scans_file_scan_id_seq'::regclass),
  "file_id" int4 NOT NULL,
  "scanner_id" int4 NOT NULL
)
;
ALTER TABLE "spdx"."files_scans" OWNER TO "augur";

-- ----------------------------
-- Table structure for identifiers
-- ----------------------------
DROP TABLE IF EXISTS "spdx"."identifiers";
CREATE TABLE "spdx"."identifiers" (
  "identifier_id" int4 NOT NULL DEFAULT nextval('"spdx".identifiers_identifier_id_seq'::regclass),
  "document_namespace_id" int4 NOT NULL,
  "id_string" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "document_id" int4,
  "package_id" int4,
  "package_file_id" int4
)
;
ALTER TABLE "spdx"."identifiers" OWNER TO "augur";

-- ----------------------------
-- Table structure for licenses
-- ----------------------------
DROP TABLE IF EXISTS "spdx"."licenses";
CREATE TABLE "spdx"."licenses" (
  "license_id" int4 NOT NULL DEFAULT nextval('"spdx".licenses_license_id_seq'::regclass),
  "name" varchar(255) COLLATE "pg_catalog"."default",
  "short_name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "cross_reference" text COLLATE "pg_catalog"."default" NOT NULL,
  "comment" text COLLATE "pg_catalog"."default" NOT NULL,
  "is_spdx_official" bool NOT NULL
)
;
ALTER TABLE "spdx"."licenses" OWNER TO "augur";

-- ----------------------------
-- Table structure for packages
-- ----------------------------
DROP TABLE IF EXISTS "spdx"."packages";
CREATE TABLE "spdx"."packages" (
  "package_id" int4 NOT NULL DEFAULT nextval('"spdx".packages_package_id_seq'::regclass),
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "version" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "file_name" text COLLATE "pg_catalog"."default" NOT NULL,
  "supplier_id" int4,
  "originator_id" int4,
  "download_location" text COLLATE "pg_catalog"."default",
  "verification_code" varchar(64) COLLATE "pg_catalog"."default" NOT NULL,
  "ver_code_excluded_file_id" int4,
  "sha256" varchar(64) COLLATE "pg_catalog"."default",
  "home_page" text COLLATE "pg_catalog"."default",
  "source_info" text COLLATE "pg_catalog"."default" NOT NULL,
  "concluded_license_id" int4,
  "declared_license_id" int4,
  "license_comment" text COLLATE "pg_catalog"."default" NOT NULL,
  "copyright_text" text COLLATE "pg_catalog"."default",
  "summary" text COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default" NOT NULL,
  "comment" text COLLATE "pg_catalog"."default" NOT NULL,
  "dosocs2_dir_code" varchar(64) COLLATE "pg_catalog"."default"
)
;
ALTER TABLE "spdx"."packages" OWNER TO "augur";

-- ----------------------------
-- Table structure for packages_files
-- ----------------------------
DROP TABLE IF EXISTS "spdx"."packages_files";
CREATE TABLE "spdx"."packages_files" (
  "package_file_id" int4 NOT NULL DEFAULT nextval('"spdx".packages_files_package_file_id_seq'::regclass),
  "package_id" int4 NOT NULL,
  "file_id" int4 NOT NULL,
  "concluded_license_id" int4,
  "license_comment" text COLLATE "pg_catalog"."default" NOT NULL,
  "file_name" text COLLATE "pg_catalog"."default" NOT NULL
)
;
ALTER TABLE "spdx"."packages_files" OWNER TO "augur";

-- ----------------------------
-- Table structure for packages_scans
-- ----------------------------
DROP TABLE IF EXISTS "spdx"."packages_scans";
CREATE TABLE "spdx"."packages_scans" (
  "package_scan_id" int4 NOT NULL DEFAULT nextval('"spdx".packages_scans_package_scan_id_seq'::regclass),
  "package_id" int4 NOT NULL,
  "scanner_id" int4 NOT NULL
)
;
ALTER TABLE "spdx"."packages_scans" OWNER TO "augur";

-- ----------------------------
-- Table structure for projects
-- ----------------------------
DROP TABLE IF EXISTS "spdx"."projects";
CREATE TABLE "spdx"."projects" (
  "package_id" int4 NOT NULL DEFAULT nextval('"spdx".projects_package_id_seq'::regclass),
  "name" text COLLATE "pg_catalog"."default" NOT NULL,
  "homepage" text COLLATE "pg_catalog"."default" NOT NULL,
  "uri" text COLLATE "pg_catalog"."default" NOT NULL
)
;
ALTER TABLE "spdx"."projects" OWNER TO "augur";

-- ----------------------------
-- Table structure for relationship_types
-- ----------------------------
DROP TABLE IF EXISTS "spdx"."relationship_types";
CREATE TABLE "spdx"."relationship_types" (
  "relationship_type_id" int4 NOT NULL DEFAULT nextval('"spdx".relationship_types_relationship_type_id_seq'::regclass),
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL
)
;
ALTER TABLE "spdx"."relationship_types" OWNER TO "augur";

-- ----------------------------
-- Table structure for relationships
-- ----------------------------
DROP TABLE IF EXISTS "spdx"."relationships";
CREATE TABLE "spdx"."relationships" (
  "relationship_id" int4 NOT NULL DEFAULT nextval('"spdx".relationships_relationship_id_seq'::regclass),
  "left_identifier_id" int4 NOT NULL,
  "right_identifier_id" int4 NOT NULL,
  "relationship_type_id" int4 NOT NULL,
  "relationship_comment" text COLLATE "pg_catalog"."default" NOT NULL
)
;
ALTER TABLE "spdx"."relationships" OWNER TO "augur";

-- ----------------------------
-- Table structure for sbom_scans
-- ----------------------------
DROP TABLE IF EXISTS "spdx"."sbom_scans";
CREATE TABLE "spdx"."sbom_scans" (
  "repo_id" int4,
  "sbom_scan" json
)
;
ALTER TABLE "spdx"."sbom_scans" OWNER TO "augur";

-- ----------------------------
-- Table structure for scanners
-- ----------------------------
DROP TABLE IF EXISTS "spdx"."scanners";
CREATE TABLE "spdx"."scanners" (
  "scanner_id" int4 NOT NULL DEFAULT nextval('"spdx".scanners_scanner_id_seq'::regclass),
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL
)
;
ALTER TABLE "spdx"."scanners" OWNER TO "augur";

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "spdx"."annotation_types_annotation_type_id_seq"
OWNED BY "spdx"."annotation_types"."annotation_type_id";
SELECT setval('"spdx"."annotation_types_annotation_type_id_seq"', 3, true);
ALTER SEQUENCE "spdx"."annotations_annotation_id_seq"
OWNED BY "spdx"."annotations"."annotation_id";
SELECT setval('"spdx"."annotations_annotation_id_seq"', 2, false);
ALTER SEQUENCE "spdx"."augur_repo_map_map_id_seq"
OWNED BY "spdx"."augur_repo_map"."map_id";
SELECT setval('"spdx"."augur_repo_map_map_id_seq"', 105, true);
ALTER SEQUENCE "spdx"."creator_types_creator_type_id_seq"
OWNED BY "spdx"."creator_types"."creator_type_id";
SELECT setval('"spdx"."creator_types_creator_type_id_seq"', 4, true);
ALTER SEQUENCE "spdx"."creators_creator_id_seq"
OWNED BY "spdx"."creators"."creator_id";
SELECT setval('"spdx"."creators_creator_id_seq"', 2, true);
ALTER SEQUENCE "spdx"."document_namespaces_document_namespace_id_seq"
OWNED BY "spdx"."document_namespaces"."document_namespace_id";
SELECT setval('"spdx"."document_namespaces_document_namespace_id_seq"', 51, true);
ALTER SEQUENCE "spdx"."documents_creators_document_creator_id_seq"
OWNED BY "spdx"."documents_creators"."document_creator_id";
SELECT setval('"spdx"."documents_creators_document_creator_id_seq"', 51, true);
ALTER SEQUENCE "spdx"."documents_document_id_seq"
OWNED BY "spdx"."documents"."document_id";
SELECT setval('"spdx"."documents_document_id_seq"', 51, true);
ALTER SEQUENCE "spdx"."external_refs_external_ref_id_seq"
OWNED BY "spdx"."external_refs"."external_ref_id";
SELECT setval('"spdx"."external_refs_external_ref_id_seq"', 2, false);
ALTER SEQUENCE "spdx"."file_contributors_file_contributor_id_seq"
OWNED BY "spdx"."file_contributors"."file_contributor_id";
SELECT setval('"spdx"."file_contributors_file_contributor_id_seq"', 2, false);
ALTER SEQUENCE "spdx"."file_types_file_type_id_seq"
OWNED BY "spdx"."file_types"."file_type_id";
SELECT setval('"spdx"."file_types_file_type_id_seq"', 12, true);
ALTER SEQUENCE "spdx"."files_file_id_seq"
OWNED BY "spdx"."files"."file_id";
SELECT setval('"spdx"."files_file_id_seq"', 113749, true);
ALTER SEQUENCE "spdx"."files_licenses_file_license_id_seq"
OWNED BY "spdx"."files_licenses"."file_license_id";
SELECT setval('"spdx"."files_licenses_file_license_id_seq"', 75355, true);
ALTER SEQUENCE "spdx"."files_scans_file_scan_id_seq"
OWNED BY "spdx"."files_scans"."file_scan_id";
SELECT setval('"spdx"."files_scans_file_scan_id_seq"', 95824, true);
ALTER SEQUENCE "spdx"."identifiers_identifier_id_seq"
OWNED BY "spdx"."identifiers"."identifier_id";
SELECT setval('"spdx"."identifiers_identifier_id_seq"', 114434, true);
ALTER SEQUENCE "spdx"."licenses_license_id_seq"
OWNED BY "spdx"."licenses"."license_id";
SELECT setval('"spdx"."licenses_license_id_seq"', 386, true);
ALTER SEQUENCE "spdx"."packages_files_package_file_id_seq"
OWNED BY "spdx"."packages_files"."package_file_id";
SELECT setval('"spdx"."packages_files_package_file_id_seq"', 114334, true);
ALTER SEQUENCE "spdx"."packages_package_id_seq"
OWNED BY "spdx"."packages"."package_id";
SELECT setval('"spdx"."packages_package_id_seq"', 67, true);
ALTER SEQUENCE "spdx"."packages_scans_package_scan_id_seq"
OWNED BY "spdx"."packages_scans"."package_scan_id";
SELECT setval('"spdx"."packages_scans_package_scan_id_seq"', 51, true);
ALTER SEQUENCE "spdx"."projects_package_id_seq"
OWNED BY "spdx"."projects"."package_id";
SELECT setval('"spdx"."projects_package_id_seq"', 2, false);
ALTER SEQUENCE "spdx"."relationship_types_relationship_type_id_seq"
OWNED BY "spdx"."relationship_types"."relationship_type_id";
SELECT setval('"spdx"."relationship_types_relationship_type_id_seq"', 31, true);
ALTER SEQUENCE "spdx"."relationships_relationship_id_seq"
OWNED BY "spdx"."relationships"."relationship_id";
SELECT setval('"spdx"."relationships_relationship_id_seq"', 457433, true);
ALTER SEQUENCE "spdx"."scanners_scanner_id_seq"
OWNED BY "spdx"."scanners"."scanner_id";
SELECT setval('"spdx"."scanners_scanner_id_seq"', 2, true);

-- ----------------------------
-- Uniques structure for table annotation_types
-- ----------------------------
ALTER TABLE "spdx"."annotation_types" ADD CONSTRAINT "uc_annotation_type_name" UNIQUE ("name");

-- ----------------------------
-- Primary Key structure for table annotation_types
-- ----------------------------
ALTER TABLE "spdx"."annotation_types" ADD CONSTRAINT "annotation_types_pkey" PRIMARY KEY ("annotation_type_id");

-- ----------------------------
-- Primary Key structure for table annotations
-- ----------------------------
ALTER TABLE "spdx"."annotations" ADD CONSTRAINT "annotations_pkey" PRIMARY KEY ("annotation_id");

-- ----------------------------
-- Primary Key structure for table augur_repo_map
-- ----------------------------
ALTER TABLE "spdx"."augur_repo_map" ADD CONSTRAINT "augur_repo_map_pkey" PRIMARY KEY ("map_id");

-- ----------------------------
-- Primary Key structure for table creator_types
-- ----------------------------
ALTER TABLE "spdx"."creator_types" ADD CONSTRAINT "creator_types_pkey" PRIMARY KEY ("creator_type_id");

-- ----------------------------
-- Primary Key structure for table creators
-- ----------------------------
ALTER TABLE "spdx"."creators" ADD CONSTRAINT "creators_pkey" PRIMARY KEY ("creator_id");

-- ----------------------------
-- Uniques structure for table document_namespaces
-- ----------------------------
ALTER TABLE "spdx"."document_namespaces" ADD CONSTRAINT "uc_document_namespace_uri" UNIQUE ("uri");

-- ----------------------------
-- Primary Key structure for table document_namespaces
-- ----------------------------
ALTER TABLE "spdx"."document_namespaces" ADD CONSTRAINT "document_namespaces_pkey" PRIMARY KEY ("document_namespace_id");

-- ----------------------------
-- Uniques structure for table documents
-- ----------------------------
ALTER TABLE "spdx"."documents" ADD CONSTRAINT "uc_document_document_namespace_id" UNIQUE ("document_namespace_id");

-- ----------------------------
-- Primary Key structure for table documents
-- ----------------------------
ALTER TABLE "spdx"."documents" ADD CONSTRAINT "documents_pkey" PRIMARY KEY ("document_id");

-- ----------------------------
-- Primary Key structure for table documents_creators
-- ----------------------------
ALTER TABLE "spdx"."documents_creators" ADD CONSTRAINT "documents_creators_pkey" PRIMARY KEY ("document_creator_id");

-- ----------------------------
-- Uniques structure for table external_refs
-- ----------------------------
ALTER TABLE "spdx"."external_refs" ADD CONSTRAINT "uc_external_ref_document_id_string" UNIQUE ("document_id", "id_string");

-- ----------------------------
-- Primary Key structure for table external_refs
-- ----------------------------
ALTER TABLE "spdx"."external_refs" ADD CONSTRAINT "external_refs_pkey" PRIMARY KEY ("external_ref_id");

-- ----------------------------
-- Primary Key structure for table file_contributors
-- ----------------------------
ALTER TABLE "spdx"."file_contributors" ADD CONSTRAINT "file_contributors_pkey" PRIMARY KEY ("file_contributor_id");

-- ----------------------------
-- Uniques structure for table file_types
-- ----------------------------
ALTER TABLE "spdx"."file_types" ADD CONSTRAINT "uc_file_type_name" UNIQUE ("name");

-- ----------------------------
-- Primary Key structure for table file_types
-- ----------------------------
ALTER TABLE "spdx"."file_types" ADD CONSTRAINT "file_types_pkey" PRIMARY KEY ("file_type_id");

-- ----------------------------
-- Uniques structure for table files
-- ----------------------------
ALTER TABLE "spdx"."files" ADD CONSTRAINT "uc_file_sha256" UNIQUE ("sha256");

-- ----------------------------
-- Primary Key structure for table files
-- ----------------------------
ALTER TABLE "spdx"."files" ADD CONSTRAINT "files_pkey" PRIMARY KEY ("file_id");

-- ----------------------------
-- Uniques structure for table files_licenses
-- ----------------------------
ALTER TABLE "spdx"."files_licenses" ADD CONSTRAINT "uc_file_license" UNIQUE ("file_id", "license_id");

-- ----------------------------
-- Primary Key structure for table files_licenses
-- ----------------------------
ALTER TABLE "spdx"."files_licenses" ADD CONSTRAINT "files_licenses_pkey" PRIMARY KEY ("file_license_id");

-- ----------------------------
-- Uniques structure for table files_scans
-- ----------------------------
ALTER TABLE "spdx"."files_scans" ADD CONSTRAINT "uc_file_scanner_id" UNIQUE ("file_id", "scanner_id");

-- ----------------------------
-- Primary Key structure for table files_scans
-- ----------------------------
ALTER TABLE "spdx"."files_scans" ADD CONSTRAINT "files_scans_pkey" PRIMARY KEY ("file_scan_id");

-- ----------------------------
-- Uniques structure for table identifiers
-- ----------------------------
ALTER TABLE "spdx"."identifiers" ADD CONSTRAINT "uc_identifier_document_namespace_id" UNIQUE ("document_namespace_id", "id_string");
ALTER TABLE "spdx"."identifiers" ADD CONSTRAINT "uc_identifier_namespace_document_id" UNIQUE ("document_namespace_id", "document_id");
ALTER TABLE "spdx"."identifiers" ADD CONSTRAINT "uc_identifier_namespace_package_id" UNIQUE ("document_namespace_id", "package_id");
ALTER TABLE "spdx"."identifiers" ADD CONSTRAINT "uc_identifier_namespace_package_file_id" UNIQUE ("document_namespace_id", "package_file_id");

-- ----------------------------
-- Checks structure for table identifiers
-- ----------------------------
ALTER TABLE "spdx"."identifiers" ADD CONSTRAINT "ck_identifier_exactly_one" CHECK ((((((document_id IS NOT NULL))::integer + ((package_id IS NOT NULL))::integer) + ((package_file_id IS NOT NULL))::integer) = 1));

-- ----------------------------
-- Primary Key structure for table identifiers
-- ----------------------------
ALTER TABLE "spdx"."identifiers" ADD CONSTRAINT "identifiers_pkey" PRIMARY KEY ("identifier_id");

-- ----------------------------
-- Uniques structure for table licenses
-- ----------------------------
ALTER TABLE "spdx"."licenses" ADD CONSTRAINT "uc_license_short_name" UNIQUE ("short_name");

-- ----------------------------
-- Primary Key structure for table licenses
-- ----------------------------
ALTER TABLE "spdx"."licenses" ADD CONSTRAINT "licenses_pkey" PRIMARY KEY ("license_id");

-- ----------------------------
-- Uniques structure for table packages
-- ----------------------------
ALTER TABLE "spdx"."packages" ADD CONSTRAINT "uc_package_sha256" UNIQUE ("sha256");
ALTER TABLE "spdx"."packages" ADD CONSTRAINT "uc_dir_code_ver_code" UNIQUE ("verification_code", "dosocs2_dir_code");

-- ----------------------------
-- Checks structure for table packages
-- ----------------------------
ALTER TABLE "spdx"."packages" ADD CONSTRAINT "uc_sha256_ds2_dir_code_exactly_one" CHECK (((((sha256 IS NOT NULL))::integer + ((dosocs2_dir_code IS NOT NULL))::integer) = 1));

-- ----------------------------
-- Primary Key structure for table packages
-- ----------------------------
ALTER TABLE "spdx"."packages" ADD CONSTRAINT "packages_pkey" PRIMARY KEY ("package_id");

-- ----------------------------
-- Uniques structure for table packages_files
-- ----------------------------
ALTER TABLE "spdx"."packages_files" ADD CONSTRAINT "uc_package_id_file_name" UNIQUE ("package_id", "file_name");

-- ----------------------------
-- Primary Key structure for table packages_files
-- ----------------------------
ALTER TABLE "spdx"."packages_files" ADD CONSTRAINT "packages_files_pkey" PRIMARY KEY ("package_file_id");

-- ----------------------------
-- Uniques structure for table packages_scans
-- ----------------------------
ALTER TABLE "spdx"."packages_scans" ADD CONSTRAINT "uc_package_scanner_id" UNIQUE ("package_id", "scanner_id");

-- ----------------------------
-- Primary Key structure for table packages_scans
-- ----------------------------
ALTER TABLE "spdx"."packages_scans" ADD CONSTRAINT "packages_scans_pkey" PRIMARY KEY ("package_scan_id");

-- ----------------------------
-- Primary Key structure for table projects
-- ----------------------------
ALTER TABLE "spdx"."projects" ADD CONSTRAINT "projects_pkey" PRIMARY KEY ("package_id");

-- ----------------------------
-- Uniques structure for table relationship_types
-- ----------------------------
ALTER TABLE "spdx"."relationship_types" ADD CONSTRAINT "uc_relationship_type_name" UNIQUE ("name");

-- ----------------------------
-- Primary Key structure for table relationship_types
-- ----------------------------
ALTER TABLE "spdx"."relationship_types" ADD CONSTRAINT "relationship_types_pkey" PRIMARY KEY ("relationship_type_id");

-- ----------------------------
-- Uniques structure for table relationships
-- ----------------------------
ALTER TABLE "spdx"."relationships" ADD CONSTRAINT "uc_left_right_relationship_type" UNIQUE ("left_identifier_id", "right_identifier_id", "relationship_type_id");

-- ----------------------------
-- Primary Key structure for table relationships
-- ----------------------------
ALTER TABLE "spdx"."relationships" ADD CONSTRAINT "relationships_pkey" PRIMARY KEY ("relationship_id");

-- ----------------------------
-- Uniques structure for table scanners
-- ----------------------------
ALTER TABLE "spdx"."scanners" ADD CONSTRAINT "uc_scanner_name" UNIQUE ("name");

-- ----------------------------
-- Primary Key structure for table scanners
-- ----------------------------
ALTER TABLE "spdx"."scanners" ADD CONSTRAINT "scanners_pkey" PRIMARY KEY ("scanner_id");

-- ----------------------------
-- Foreign Keys structure for table annotations
-- ----------------------------
ALTER TABLE "spdx"."annotations" ADD CONSTRAINT "annotations_annotation_type_id_fkey" FOREIGN KEY ("annotation_type_id") REFERENCES "spdx"."annotation_types" ("annotation_type_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "spdx"."annotations" ADD CONSTRAINT "annotations_creator_id_fkey" FOREIGN KEY ("creator_id") REFERENCES "spdx"."creators" ("creator_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "spdx"."annotations" ADD CONSTRAINT "annotations_document_id_fkey" FOREIGN KEY ("document_id") REFERENCES "spdx"."documents" ("document_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "spdx"."annotations" ADD CONSTRAINT "annotations_identifier_id_fkey" FOREIGN KEY ("identifier_id") REFERENCES "spdx"."identifiers" ("identifier_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table creators
-- ----------------------------
ALTER TABLE "spdx"."creators" ADD CONSTRAINT "creators_creator_type_id_fkey" FOREIGN KEY ("creator_type_id") REFERENCES "spdx"."creator_types" ("creator_type_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table documents
-- ----------------------------
ALTER TABLE "spdx"."documents" ADD CONSTRAINT "documents_data_license_id_fkey" FOREIGN KEY ("data_license_id") REFERENCES "spdx"."licenses" ("license_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "spdx"."documents" ADD CONSTRAINT "documents_document_namespace_id_fkey" FOREIGN KEY ("document_namespace_id") REFERENCES "spdx"."document_namespaces" ("document_namespace_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "spdx"."documents" ADD CONSTRAINT "documents_package_id_fkey" FOREIGN KEY ("package_id") REFERENCES "spdx"."packages" ("package_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table documents_creators
-- ----------------------------
ALTER TABLE "spdx"."documents_creators" ADD CONSTRAINT "documents_creators_creator_id_fkey" FOREIGN KEY ("creator_id") REFERENCES "spdx"."creators" ("creator_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "spdx"."documents_creators" ADD CONSTRAINT "documents_creators_document_id_fkey" FOREIGN KEY ("document_id") REFERENCES "spdx"."documents" ("document_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table external_refs
-- ----------------------------
ALTER TABLE "spdx"."external_refs" ADD CONSTRAINT "external_refs_document_id_fkey" FOREIGN KEY ("document_id") REFERENCES "spdx"."documents" ("document_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "spdx"."external_refs" ADD CONSTRAINT "external_refs_document_namespace_id_fkey" FOREIGN KEY ("document_namespace_id") REFERENCES "spdx"."document_namespaces" ("document_namespace_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table file_contributors
-- ----------------------------
ALTER TABLE "spdx"."file_contributors" ADD CONSTRAINT "file_contributors_file_id_fkey" FOREIGN KEY ("file_id") REFERENCES "spdx"."files" ("file_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table files
-- ----------------------------
ALTER TABLE "spdx"."files" ADD CONSTRAINT "files_file_type_id_fkey" FOREIGN KEY ("file_type_id") REFERENCES "spdx"."file_types" ("file_type_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table files_licenses
-- ----------------------------
ALTER TABLE "spdx"."files_licenses" ADD CONSTRAINT "files_licenses_file_id_fkey" FOREIGN KEY ("file_id") REFERENCES "spdx"."files" ("file_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "spdx"."files_licenses" ADD CONSTRAINT "files_licenses_license_id_fkey" FOREIGN KEY ("license_id") REFERENCES "spdx"."licenses" ("license_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table files_scans
-- ----------------------------
ALTER TABLE "spdx"."files_scans" ADD CONSTRAINT "files_scans_file_id_fkey" FOREIGN KEY ("file_id") REFERENCES "spdx"."files" ("file_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "spdx"."files_scans" ADD CONSTRAINT "files_scans_scanner_id_fkey" FOREIGN KEY ("scanner_id") REFERENCES "spdx"."scanners" ("scanner_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table identifiers
-- ----------------------------
ALTER TABLE "spdx"."identifiers" ADD CONSTRAINT "identifiers_document_id_fkey" FOREIGN KEY ("document_id") REFERENCES "spdx"."documents" ("document_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "spdx"."identifiers" ADD CONSTRAINT "identifiers_document_namespace_id_fkey" FOREIGN KEY ("document_namespace_id") REFERENCES "spdx"."document_namespaces" ("document_namespace_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "spdx"."identifiers" ADD CONSTRAINT "identifiers_package_file_id_fkey" FOREIGN KEY ("package_file_id") REFERENCES "spdx"."packages_files" ("package_file_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "spdx"."identifiers" ADD CONSTRAINT "identifiers_package_id_fkey" FOREIGN KEY ("package_id") REFERENCES "spdx"."packages" ("package_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table packages
-- ----------------------------
ALTER TABLE "spdx"."packages" ADD CONSTRAINT "fk_package_packages_files" FOREIGN KEY ("ver_code_excluded_file_id") REFERENCES "spdx"."packages_files" ("package_file_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "spdx"."packages" ADD CONSTRAINT "packages_concluded_license_id_fkey" FOREIGN KEY ("concluded_license_id") REFERENCES "spdx"."licenses" ("license_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "spdx"."packages" ADD CONSTRAINT "packages_declared_license_id_fkey" FOREIGN KEY ("declared_license_id") REFERENCES "spdx"."licenses" ("license_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "spdx"."packages" ADD CONSTRAINT "packages_originator_id_fkey" FOREIGN KEY ("originator_id") REFERENCES "spdx"."creators" ("creator_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "spdx"."packages" ADD CONSTRAINT "packages_supplier_id_fkey" FOREIGN KEY ("supplier_id") REFERENCES "spdx"."creators" ("creator_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table packages_files
-- ----------------------------
ALTER TABLE "spdx"."packages_files" ADD CONSTRAINT "fk_package_files_packages" FOREIGN KEY ("package_id") REFERENCES "spdx"."packages" ("package_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "spdx"."packages_files" ADD CONSTRAINT "packages_files_concluded_license_id_fkey" FOREIGN KEY ("concluded_license_id") REFERENCES "spdx"."licenses" ("license_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "spdx"."packages_files" ADD CONSTRAINT "packages_files_file_id_fkey" FOREIGN KEY ("file_id") REFERENCES "spdx"."files" ("file_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table packages_scans
-- ----------------------------
ALTER TABLE "spdx"."packages_scans" ADD CONSTRAINT "packages_scans_package_id_fkey" FOREIGN KEY ("package_id") REFERENCES "spdx"."packages" ("package_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "spdx"."packages_scans" ADD CONSTRAINT "packages_scans_scanner_id_fkey" FOREIGN KEY ("scanner_id") REFERENCES "spdx"."scanners" ("scanner_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table relationships
-- ----------------------------
ALTER TABLE "spdx"."relationships" ADD CONSTRAINT "relationships_left_identifier_id_fkey" FOREIGN KEY ("left_identifier_id") REFERENCES "spdx"."identifiers" ("identifier_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "spdx"."relationships" ADD CONSTRAINT "relationships_relationship_type_id_fkey" FOREIGN KEY ("relationship_type_id") REFERENCES "spdx"."relationship_types" ("relationship_type_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "spdx"."relationships" ADD CONSTRAINT "relationships_right_identifier_id_fkey" FOREIGN KEY ("right_identifier_id") REFERENCES "spdx"."identifiers" ("identifier_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
