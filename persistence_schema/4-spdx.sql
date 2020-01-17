-- ----------------------------
-- Sequence structure for annotation_types_annotation_type_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."annotation_types_annotation_type_id_seq";
CREATE SEQUENCE "spdx"."annotation_types_annotation_type_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 10000
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
START 10000
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
START 10000
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
START 10000
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
START 10000
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
START 10000
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
START 10000
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
START 10000
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
START 10000
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
START 10000
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
START 10000
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
START 10000
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
START 10000
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
START 10000
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
START 10000
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
START 10000
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
START 10000
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
START 10000
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
START 10000
CACHE 1;
ALTER SEQUENCE "spdx"."packages_scans_package_scan_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for projects_project_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."projects_project_id_seq";
CREATE SEQUENCE "spdx"."projects_project_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 10000
CACHE 1;
ALTER SEQUENCE "spdx"."projects_project_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for relationship_types_relationship_type_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."relationship_types_relationship_type_id_seq";
CREATE SEQUENCE "spdx"."relationship_types_relationship_type_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 10000
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
START 10000
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
START 10000
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
-- Records of annotation_types
-- ----------------------------
BEGIN;
INSERT INTO "spdx"."annotation_types" VALUES (1, 'REVIEW');
INSERT INTO "spdx"."annotation_types" VALUES (2, 'OTHER');
COMMIT;

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
-- Records of creator_types
-- ----------------------------
BEGIN;
INSERT INTO "spdx"."creator_types" VALUES (1, 'Person');
INSERT INTO "spdx"."creator_types" VALUES (2, 'Organization');
INSERT INTO "spdx"."creator_types" VALUES (3, 'Tool');
COMMIT;

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
-- Records of creators
-- ----------------------------
BEGIN;
INSERT INTO "spdx"."creators" VALUES (1, 3, 'dosocs2-0.16.1', '');
COMMIT;

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
-- Records of file_types
-- ----------------------------
BEGIN;
INSERT INTO "spdx"."file_types" VALUES (1, 'SOURCE');
INSERT INTO "spdx"."file_types" VALUES (2, 'BINARY');
INSERT INTO "spdx"."file_types" VALUES (3, 'ARCHIVE');
INSERT INTO "spdx"."file_types" VALUES (4, 'APPLICATION');
INSERT INTO "spdx"."file_types" VALUES (5, 'AUDIO');
INSERT INTO "spdx"."file_types" VALUES (6, 'IMAGE');
INSERT INTO "spdx"."file_types" VALUES (7, 'TEXT');
INSERT INTO "spdx"."file_types" VALUES (8, 'VIDEO');
INSERT INTO "spdx"."file_types" VALUES (9, 'DOCUMENTATION');
INSERT INTO "spdx"."file_types" VALUES (10, 'SPDX');
INSERT INTO "spdx"."file_types" VALUES (11, 'OTHER');
COMMIT;

-- ----------------------------
-- Table structure for files
-- ----------------------------
DROP TABLE IF EXISTS "spdx"."files";
CREATE TABLE "spdx"."files" (
  "file_id" int4 NOT NULL DEFAULT nextval('"spdx".files_file_id_seq'::regclass),
  "file_type_id" int4 NOT NULL,
  "sha256" varchar(64) COLLATE "pg_catalog"."default" NOT NULL,
  "copyright_text" text COLLATE "pg_catalog"."default",
  "project_id" int4,
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
-- Records of licenses
-- ----------------------------
BEGIN;
INSERT INTO "spdx"."licenses" VALUES (1, '3dfx Glide License', 'Glide', 'http://spdx.org/licenses/Glide.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (2, 'Abstyles License', 'Abstyles', 'http://spdx.org/licenses/Abstyles.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (3, 'Academic Free License v1.1', 'AFL-1.1', 'http://spdx.org/licenses/AFL-1.1.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (4, 'Academic Free License v1.2', 'AFL-1.2', 'http://spdx.org/licenses/AFL-1.2.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (5, 'Academic Free License v2.0', 'AFL-2.0', 'http://spdx.org/licenses/AFL-2.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (6, 'Academic Free License v2.1', 'AFL-2.1', 'http://spdx.org/licenses/AFL-2.1.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (7, 'Academic Free License v3.0', 'AFL-3.0', 'http://spdx.org/licenses/AFL-3.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (8, 'Academy of Motion Picture Arts and Sciences BSD', 'AMPAS', 'http://spdx.org/licenses/AMPAS.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (9, 'Adaptive Public License 1.0', 'APL-1.0', 'http://spdx.org/licenses/APL-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (10, 'Adobe Glyph List License', 'Adobe-Glyph', 'http://spdx.org/licenses/Adobe-Glyph.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (11, 'Adobe Postscript AFM License', 'APAFML', 'http://spdx.org/licenses/APAFML.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (12, 'Adobe Systems Incorporated Source Code License Agreement', 'Adobe-2006', 'http://spdx.org/licenses/Adobe-2006.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (13, 'Affero General Public License v1.0', 'AGPL-1.0', 'http://spdx.org/licenses/AGPL-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (14, 'Afmparse License', 'Afmparse', 'http://spdx.org/licenses/Afmparse.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (15, 'Aladdin Free Public License', 'Aladdin', 'http://spdx.org/licenses/Aladdin.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (16, 'Amazon Digital Services License', 'ADSL', 'http://spdx.org/licenses/ADSL.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (17, 'AMD''s plpa_map.c License', 'AMDPLPA', 'http://spdx.org/licenses/AMDPLPA.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (18, 'ANTLR Software Rights Notice', 'ANTLR-PD', 'http://spdx.org/licenses/ANTLR-PD.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (19, 'Apache License 1.0', 'Apache-1.0', 'http://spdx.org/licenses/Apache-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (20, 'Apache License 1.1', 'Apache-1.1', 'http://spdx.org/licenses/Apache-1.1.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (21, 'Apache License 2.0', 'Apache-2.0', 'http://spdx.org/licenses/Apache-2.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (22, 'Apple MIT License', 'AML', 'http://spdx.org/licenses/AML.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (23, 'Apple Public Source License 1.0', 'APSL-1.0', 'http://spdx.org/licenses/APSL-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (24, 'Apple Public Source License 1.1', 'APSL-1.1', 'http://spdx.org/licenses/APSL-1.1.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (25, 'Apple Public Source License 1.2', 'APSL-1.2', 'http://spdx.org/licenses/APSL-1.2.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (26, 'Apple Public Source License 2.0', 'APSL-2.0', 'http://spdx.org/licenses/APSL-2.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (27, 'Artistic License 1.0', 'Artistic-1.0', 'http://spdx.org/licenses/Artistic-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (28, 'Artistic License 1.0 (Perl)', 'Artistic-1.0-Perl', 'http://spdx.org/licenses/Artistic-1.0-Perl.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (29, 'Artistic License 1.0 w/clause 8', 'Artistic-1.0-cl8', 'http://spdx.org/licenses/Artistic-1.0-cl8.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (30, 'Artistic License 2.0', 'Artistic-2.0', 'http://spdx.org/licenses/Artistic-2.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (31, 'Attribution Assurance License', 'AAL', 'http://spdx.org/licenses/AAL.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (32, 'Bahyph License', 'Bahyph', 'http://spdx.org/licenses/Bahyph.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (33, 'Barr License', 'Barr', 'http://spdx.org/licenses/Barr.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (34, 'Beerware License', 'Beerware', 'http://spdx.org/licenses/Beerware.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (35, 'BitTorrent Open Source License v1.0', 'BitTorrent-1.0', 'http://spdx.org/licenses/BitTorrent-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (36, 'BitTorrent Open Source License v1.1', 'BitTorrent-1.1', 'http://spdx.org/licenses/BitTorrent-1.1.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (37, 'Boost Software License 1.0', 'BSL-1.0', 'http://spdx.org/licenses/BSL-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (38, 'Borceux license', 'Borceux', 'http://spdx.org/licenses/Borceux.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (39, 'BSD 2-clause "Simplified" License', 'BSD-2-Clause', 'http://spdx.org/licenses/BSD-2-Clause.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (40, 'BSD 2-clause FreeBSD License', 'BSD-2-Clause-FreeBSD', 'http://spdx.org/licenses/BSD-2-Clause-FreeBSD.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (41, 'BSD 2-clause NetBSD License', 'BSD-2-Clause-NetBSD', 'http://spdx.org/licenses/BSD-2-Clause-NetBSD.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (42, 'BSD 3-clause "New" or "Revised" License', 'BSD-3-Clause', 'http://spdx.org/licenses/BSD-3-Clause.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (43, 'BSD 3-clause Clear License', 'BSD-3-Clause-Clear', 'http://spdx.org/licenses/BSD-3-Clause-Clear.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (44, 'BSD 4-clause "Original" or "Old" License', 'BSD-4-Clause', 'http://spdx.org/licenses/BSD-4-Clause.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (45, 'BSD Protection License', 'BSD-Protection', 'http://spdx.org/licenses/BSD-Protection.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (46, 'BSD with attribution', 'BSD-3-Clause-Attribution', 'http://spdx.org/licenses/BSD-3-Clause-Attribution.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (47, 'BSD Zero Clause License', '0BSD', 'http://spdx.org/licenses/0BSD.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (48, 'BSD-4-Clause (University of California-Specific)', 'BSD-4-Clause-UC', 'http://spdx.org/licenses/BSD-4-Clause-UC.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (49, 'bzip2 and libbzip2 License v1.0.5', 'bzip2-1.0.5', 'http://spdx.org/licenses/bzip2-1.0.5.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (50, 'bzip2 and libbzip2 License v1.0.6', 'bzip2-1.0.6', 'http://spdx.org/licenses/bzip2-1.0.6.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (51, 'Caldera License', 'Caldera', 'http://spdx.org/licenses/Caldera.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (52, 'CeCILL Free Software License Agreement v1.0', 'CECILL-1.0', 'http://spdx.org/licenses/CECILL-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (53, 'CeCILL Free Software License Agreement v1.1', 'CECILL-1.1', 'http://spdx.org/licenses/CECILL-1.1.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (54, 'CeCILL Free Software License Agreement v2.0', 'CECILL-2.0', 'http://spdx.org/licenses/CECILL-2.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (55, 'CeCILL Free Software License Agreement v2.1', 'CECILL-2.1', 'http://spdx.org/licenses/CECILL-2.1.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (56, 'CeCILL-B Free Software License Agreement', 'CECILL-B', 'http://spdx.org/licenses/CECILL-B.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (57, 'CeCILL-C Free Software License Agreement', 'CECILL-C', 'http://spdx.org/licenses/CECILL-C.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (58, 'Clarified Artistic License', 'ClArtistic', 'http://spdx.org/licenses/ClArtistic.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (59, 'CMU License', 'MIT-CMU', 'http://spdx.org/licenses/MIT-CMU.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (60, 'CNRI Jython License', 'CNRI-Jython', 'http://spdx.org/licenses/CNRI-Jython.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (61, 'CNRI Python License', 'CNRI-Python', 'http://spdx.org/licenses/CNRI-Python.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (62, 'CNRI Python Open Source GPL Compatible License Agreement', 'CNRI-Python-GPL-Compatible', 'http://spdx.org/licenses/CNRI-Python-GPL-Compatible.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (63, 'Code Project Open License 1.02', 'CPOL-1.02', 'http://spdx.org/licenses/CPOL-1.02.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (64, 'Common Development and Distribution License 1.0', 'CDDL-1.0', 'http://spdx.org/licenses/CDDL-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (65, 'Common Development and Distribution License 1.1', 'CDDL-1.1', 'http://spdx.org/licenses/CDDL-1.1.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (66, 'Common Public Attribution License 1.0', 'CPAL-1.0', 'http://spdx.org/licenses/CPAL-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (67, 'Common Public License 1.0', 'CPL-1.0', 'http://spdx.org/licenses/CPL-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (68, 'Computer Associates Trusted Open Source License 1.1', 'CATOSL-1.1', 'http://spdx.org/licenses/CATOSL-1.1.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (69, 'Condor Public License v1.1', 'Condor-1.1', 'http://spdx.org/licenses/Condor-1.1.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (70, 'Creative Commons Attribution 1.0', 'CC-BY-1.0', 'http://spdx.org/licenses/CC-BY-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (71, 'Creative Commons Attribution 2.0', 'CC-BY-2.0', 'http://spdx.org/licenses/CC-BY-2.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (72, 'Creative Commons Attribution 2.5', 'CC-BY-2.5', 'http://spdx.org/licenses/CC-BY-2.5.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (73, 'Creative Commons Attribution 3.0', 'CC-BY-3.0', 'http://spdx.org/licenses/CC-BY-3.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (74, 'Creative Commons Attribution 4.0', 'CC-BY-4.0', 'http://spdx.org/licenses/CC-BY-4.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (75, 'Creative Commons Attribution No Derivatives 1.0', 'CC-BY-ND-1.0', 'http://spdx.org/licenses/CC-BY-ND-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (76, 'Creative Commons Attribution No Derivatives 2.0', 'CC-BY-ND-2.0', 'http://spdx.org/licenses/CC-BY-ND-2.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (77, 'Creative Commons Attribution No Derivatives 2.5', 'CC-BY-ND-2.5', 'http://spdx.org/licenses/CC-BY-ND-2.5.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (78, 'Creative Commons Attribution No Derivatives 3.0', 'CC-BY-ND-3.0', 'http://spdx.org/licenses/CC-BY-ND-3.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (79, 'Creative Commons Attribution No Derivatives 4.0', 'CC-BY-ND-4.0', 'http://spdx.org/licenses/CC-BY-ND-4.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (80, 'Creative Commons Attribution Non Commercial 1.0', 'CC-BY-NC-1.0', 'http://spdx.org/licenses/CC-BY-NC-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (81, 'Creative Commons Attribution Non Commercial 2.0', 'CC-BY-NC-2.0', 'http://spdx.org/licenses/CC-BY-NC-2.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (82, 'Creative Commons Attribution Non Commercial 2.5', 'CC-BY-NC-2.5', 'http://spdx.org/licenses/CC-BY-NC-2.5.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (83, 'Creative Commons Attribution Non Commercial 3.0', 'CC-BY-NC-3.0', 'http://spdx.org/licenses/CC-BY-NC-3.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (84, 'Creative Commons Attribution Non Commercial 4.0', 'CC-BY-NC-4.0', 'http://spdx.org/licenses/CC-BY-NC-4.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (85, 'Creative Commons Attribution Non Commercial No Derivatives 1.0', 'CC-BY-NC-ND-1.0', 'http://spdx.org/licenses/CC-BY-NC-ND-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (86, 'Creative Commons Attribution Non Commercial No Derivatives 2.0', 'CC-BY-NC-ND-2.0', 'http://spdx.org/licenses/CC-BY-NC-ND-2.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (87, 'Creative Commons Attribution Non Commercial No Derivatives 2.5', 'CC-BY-NC-ND-2.5', 'http://spdx.org/licenses/CC-BY-NC-ND-2.5.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (88, 'Creative Commons Attribution Non Commercial No Derivatives 3.0', 'CC-BY-NC-ND-3.0', 'http://spdx.org/licenses/CC-BY-NC-ND-3.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (89, 'Creative Commons Attribution Non Commercial No Derivatives 4.0', 'CC-BY-NC-ND-4.0', 'http://spdx.org/licenses/CC-BY-NC-ND-4.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (90, 'Creative Commons Attribution Non Commercial Share Alike 1.0', 'CC-BY-NC-SA-1.0', 'http://spdx.org/licenses/CC-BY-NC-SA-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (91, 'Creative Commons Attribution Non Commercial Share Alike 2.0', 'CC-BY-NC-SA-2.0', 'http://spdx.org/licenses/CC-BY-NC-SA-2.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (92, 'Creative Commons Attribution Non Commercial Share Alike 2.5', 'CC-BY-NC-SA-2.5', 'http://spdx.org/licenses/CC-BY-NC-SA-2.5.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (93, 'Creative Commons Attribution Non Commercial Share Alike 3.0', 'CC-BY-NC-SA-3.0', 'http://spdx.org/licenses/CC-BY-NC-SA-3.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (94, 'Creative Commons Attribution Non Commercial Share Alike 4.0', 'CC-BY-NC-SA-4.0', 'http://spdx.org/licenses/CC-BY-NC-SA-4.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (95, 'Creative Commons Attribution Share Alike 1.0', 'CC-BY-SA-1.0', 'http://spdx.org/licenses/CC-BY-SA-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (96, 'Creative Commons Attribution Share Alike 2.0', 'CC-BY-SA-2.0', 'http://spdx.org/licenses/CC-BY-SA-2.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (97, 'Creative Commons Attribution Share Alike 2.5', 'CC-BY-SA-2.5', 'http://spdx.org/licenses/CC-BY-SA-2.5.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (98, 'Creative Commons Attribution Share Alike 3.0', 'CC-BY-SA-3.0', 'http://spdx.org/licenses/CC-BY-SA-3.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (99, 'Creative Commons Attribution Share Alike 4.0', 'CC-BY-SA-4.0', 'http://spdx.org/licenses/CC-BY-SA-4.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (100, 'Creative Commons Zero v1.0 Universal', 'CC0-1.0', 'http://spdx.org/licenses/CC0-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (101, 'Crossword License', 'Crossword', 'http://spdx.org/licenses/Crossword.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (102, 'CrystalStacker License', 'CrystalStacker', 'http://spdx.org/licenses/CrystalStacker.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (103, 'CUA Office Public License v1.0', 'CUA-OPL-1.0', 'http://spdx.org/licenses/CUA-OPL-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (104, 'Cube License', 'Cube', 'http://spdx.org/licenses/Cube.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (105, 'Deutsche Freie Software Lizenz', 'D-FSL-1.0', 'http://spdx.org/licenses/D-FSL-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (106, 'diffmark license', 'diffmark', 'http://spdx.org/licenses/diffmark.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (107, 'Do What The F*ck You Want To Public License', 'WTFPL', 'http://spdx.org/licenses/WTFPL.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (108, 'DOC License', 'DOC', 'http://spdx.org/licenses/DOC.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (109, 'Dotseqn License', 'Dotseqn', 'http://spdx.org/licenses/Dotseqn.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (110, 'DSDP License', 'DSDP', 'http://spdx.org/licenses/DSDP.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (111, 'dvipdfm License', 'dvipdfm', 'http://spdx.org/licenses/dvipdfm.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (112, 'Eclipse Public License 1.0', 'EPL-1.0', 'http://spdx.org/licenses/EPL-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (113, 'Educational Community License v1.0', 'ECL-1.0', 'http://spdx.org/licenses/ECL-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (114, 'Educational Community License v2.0', 'ECL-2.0', 'http://spdx.org/licenses/ECL-2.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (115, 'eGenix.com Public License 1.1.0', 'eGenix', 'http://spdx.org/licenses/eGenix.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (116, 'Eiffel Forum License v1.0', 'EFL-1.0', 'http://spdx.org/licenses/EFL-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (117, 'Eiffel Forum License v2.0', 'EFL-2.0', 'http://spdx.org/licenses/EFL-2.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (118, 'Enlightenment License (e16)', 'MIT-advertising', 'http://spdx.org/licenses/MIT-advertising.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (119, 'enna License', 'MIT-enna', 'http://spdx.org/licenses/MIT-enna.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (120, 'Entessa Public License v1.0', 'Entessa', 'http://spdx.org/licenses/Entessa.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (121, 'Erlang Public License v1.1', 'ErlPL-1.1', 'http://spdx.org/licenses/ErlPL-1.1.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (122, 'EU DataGrid Software License', 'EUDatagrid', 'http://spdx.org/licenses/EUDatagrid.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (123, 'European Union Public License 1.0', 'EUPL-1.0', 'http://spdx.org/licenses/EUPL-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (124, 'European Union Public License 1.1', 'EUPL-1.1', 'http://spdx.org/licenses/EUPL-1.1.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (125, 'Eurosym License', 'Eurosym', 'http://spdx.org/licenses/Eurosym.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (126, 'Fair License', 'Fair', 'http://spdx.org/licenses/Fair.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (127, 'feh License', 'MIT-feh', 'http://spdx.org/licenses/MIT-feh.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (128, 'Frameworx Open License 1.0', 'Frameworx-1.0', 'http://spdx.org/licenses/Frameworx-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (129, 'FreeImage Public License v1.0', 'FreeImage', 'http://spdx.org/licenses/FreeImage.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (130, 'Freetype Project License', 'FTL', 'http://spdx.org/licenses/FTL.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (131, 'FSF Unlimited License', 'FSFUL', 'http://spdx.org/licenses/FSFUL.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (132, 'FSF Unlimited License (with License Retention)', 'FSFULLR', 'http://spdx.org/licenses/FSFULLR.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (133, 'Giftware License', 'Giftware', 'http://spdx.org/licenses/Giftware.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (134, 'GL2PS License', 'GL2PS', 'http://spdx.org/licenses/GL2PS.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (135, 'Glulxe License', 'Glulxe', 'http://spdx.org/licenses/Glulxe.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (136, 'GNU Affero General Public License v3.0', 'AGPL-3.0', 'http://spdx.org/licenses/AGPL-3.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (137, 'GNU Free Documentation License v1.1', 'GFDL-1.1', 'http://spdx.org/licenses/GFDL-1.1.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (138, 'GNU Free Documentation License v1.2', 'GFDL-1.2', 'http://spdx.org/licenses/GFDL-1.2.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (139, 'GNU Free Documentation License v1.3', 'GFDL-1.3', 'http://spdx.org/licenses/GFDL-1.3.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (140, 'GNU General Public License v1.0 only', 'GPL-1.0', 'http://spdx.org/licenses/GPL-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (141, 'GNU General Public License v2.0 only', 'GPL-2.0', 'http://spdx.org/licenses/GPL-2.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (142, 'GNU General Public License v3.0 only', 'GPL-3.0', 'http://spdx.org/licenses/GPL-3.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (143, 'GNU Lesser General Public License v2.1 only', 'LGPL-2.1', 'http://spdx.org/licenses/LGPL-2.1.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (144, 'GNU Lesser General Public License v3.0 only', 'LGPL-3.0', 'http://spdx.org/licenses/LGPL-3.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (145, 'GNU Library General Public License v2 only', 'LGPL-2.0', 'http://spdx.org/licenses/LGPL-2.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (146, 'gnuplot License', 'gnuplot', 'http://spdx.org/licenses/gnuplot.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (147, 'gSOAP Public License v1.3b', 'gSOAP-1.3b', 'http://spdx.org/licenses/gSOAP-1.3b.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (148, 'Haskell Language Report License', 'HaskellReport', 'http://spdx.org/licenses/HaskellReport.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (149, 'Historic Permission Notice and Disclaimer', 'HPND', 'http://spdx.org/licenses/HPND.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (150, 'IBM PowerPC Initialization and Boot Software', 'IBM-pibs', 'http://spdx.org/licenses/IBM-pibs.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (151, 'IBM Public License v1.0', 'IPL-1.0', 'http://spdx.org/licenses/IPL-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (152, 'ICU License', 'ICU', 'http://spdx.org/licenses/ICU.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (153, 'ImageMagick License', 'ImageMagick', 'http://spdx.org/licenses/ImageMagick.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (154, 'iMatix Standard Function Library Agreement', 'iMatix', 'http://spdx.org/licenses/iMatix.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (155, 'Imlib2 License', 'Imlib2', 'http://spdx.org/licenses/Imlib2.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (156, 'Independent JPEG Group License', 'IJG', 'http://spdx.org/licenses/IJG.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (157, 'Intel ACPI Software License Agreement', 'Intel-ACPI', 'http://spdx.org/licenses/Intel-ACPI.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (158, 'Intel Open Source License', 'Intel', 'http://spdx.org/licenses/Intel.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (159, 'Interbase Public License v1.0', 'Interbase-1.0', 'http://spdx.org/licenses/Interbase-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (160, 'IPA Font License', 'IPA', 'http://spdx.org/licenses/IPA.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (161, 'ISC License', 'ISC', 'http://spdx.org/licenses/ISC.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (162, 'JasPer License', 'JasPer-2.0', 'http://spdx.org/licenses/JasPer-2.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (163, 'JSON License', 'JSON', 'http://spdx.org/licenses/JSON.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (164, 'LaTeX Project Public License 1.3a', 'LPPL-1.3a', 'http://spdx.org/licenses/LPPL-1.3a.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (165, 'LaTeX Project Public License v1.0', 'LPPL-1.0', 'http://spdx.org/licenses/LPPL-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (166, 'LaTeX Project Public License v1.1', 'LPPL-1.1', 'http://spdx.org/licenses/LPPL-1.1.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (167, 'LaTeX Project Public License v1.2', 'LPPL-1.2', 'http://spdx.org/licenses/LPPL-1.2.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (168, 'LaTeX Project Public License v1.3c', 'LPPL-1.3c', 'http://spdx.org/licenses/LPPL-1.3c.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (169, 'Latex2e License', 'Latex2e', 'http://spdx.org/licenses/Latex2e.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (170, 'Lawrence Berkeley National Labs BSD variant license', 'BSD-3-Clause-LBNL', 'http://spdx.org/licenses/BSD-3-Clause-LBNL.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (171, 'Leptonica License', 'Leptonica', 'http://spdx.org/licenses/Leptonica.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (172, 'Lesser General Public License For Linguistic Resources', 'LGPLLR', 'http://spdx.org/licenses/LGPLLR.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (173, 'libpng License', 'Libpng', 'http://spdx.org/licenses/Libpng.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (174, 'libtiff License', 'libtiff', 'http://spdx.org/licenses/libtiff.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (175, 'Lucent Public License v1.02', 'LPL-1.02', 'http://spdx.org/licenses/LPL-1.02.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (176, 'Lucent Public License Version 1.0', 'LPL-1.0', 'http://spdx.org/licenses/LPL-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (177, 'MakeIndex License', 'MakeIndex', 'http://spdx.org/licenses/MakeIndex.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (178, 'Matrix Template Library License', 'MTLL', 'http://spdx.org/licenses/MTLL.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (179, 'Microsoft Public License', 'MS-PL', 'http://spdx.org/licenses/MS-PL.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (180, 'Microsoft Reciprocal License', 'MS-RL', 'http://spdx.org/licenses/MS-RL.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (181, 'MirOS Licence', 'MirOS', 'http://spdx.org/licenses/MirOS.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (182, 'MIT +no-false-attribs license', 'MITNFA', 'http://spdx.org/licenses/MITNFA.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (183, 'MIT License', 'MIT', 'http://spdx.org/licenses/MIT.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (184, 'Motosoto License', 'Motosoto', 'http://spdx.org/licenses/Motosoto.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (185, 'Mozilla Public License 1.0', 'MPL-1.0', 'http://spdx.org/licenses/MPL-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (186, 'Mozilla Public License 1.1', 'MPL-1.1', 'http://spdx.org/licenses/MPL-1.1.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (187, 'Mozilla Public License 2.0', 'MPL-2.0', 'http://spdx.org/licenses/MPL-2.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (188, 'Mozilla Public License 2.0 (no copyleft exception)', 'MPL-2.0-no-copyleft-exception', 'http://spdx.org/licenses/MPL-2.0-no-copyleft-exception.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (189, 'mpich2 License', 'mpich2', 'http://spdx.org/licenses/mpich2.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (190, 'Multics License', 'Multics', 'http://spdx.org/licenses/Multics.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (191, 'Mup License', 'Mup', 'http://spdx.org/licenses/Mup.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (192, 'NASA Open Source Agreement 1.3', 'NASA-1.3', 'http://spdx.org/licenses/NASA-1.3.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (193, 'Naumen Public License', 'Naumen', 'http://spdx.org/licenses/Naumen.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (194, 'Net Boolean Public License v1', 'NBPL-1.0', 'http://spdx.org/licenses/NBPL-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (195, 'NetCDF license', 'NetCDF', 'http://spdx.org/licenses/NetCDF.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (196, 'Nethack General Public License', 'NGPL', 'http://spdx.org/licenses/NGPL.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (197, 'Netizen Open Source License', 'NOSL', 'http://spdx.org/licenses/NOSL.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (198, 'Netscape Public License v1.0', 'NPL-1.0', 'http://spdx.org/licenses/NPL-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (199, 'Netscape Public License v1.1', 'NPL-1.1', 'http://spdx.org/licenses/NPL-1.1.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (200, 'Newsletr License', 'Newsletr', 'http://spdx.org/licenses/Newsletr.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (201, 'No Limit Public License', 'NLPL', 'http://spdx.org/licenses/NLPL.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (202, 'Nokia Open Source License', 'Nokia', 'http://spdx.org/licenses/Nokia.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (203, 'Non-Profit Open Software License 3.0', 'NPOSL-3.0', 'http://spdx.org/licenses/NPOSL-3.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (204, 'Noweb License', 'Noweb', 'http://spdx.org/licenses/Noweb.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (205, 'NRL License', 'NRL', 'http://spdx.org/licenses/NRL.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (206, 'NTP License', 'NTP', 'http://spdx.org/licenses/NTP.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (207, 'Nunit License', 'Nunit', 'http://spdx.org/licenses/Nunit.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (208, 'OCLC Research Public License 2.0', 'OCLC-2.0', 'http://spdx.org/licenses/OCLC-2.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (209, 'ODC Open Database License v1.0', 'ODbL-1.0', 'http://spdx.org/licenses/ODbL-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (210, 'ODC Public Domain Dedication &amp; License 1.0', 'PDDL-1.0', 'http://spdx.org/licenses/PDDL-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (211, 'Open Group Test Suite License', 'OGTSL', 'http://spdx.org/licenses/OGTSL.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (212, 'Open LDAP Public License  2.2.2', 'OLDAP-2.2.2', 'http://spdx.org/licenses/OLDAP-2.2.2.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (213, 'Open LDAP Public License v1.1', 'OLDAP-1.1', 'http://spdx.org/licenses/OLDAP-1.1.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (214, 'Open LDAP Public License v1.2', 'OLDAP-1.2', 'http://spdx.org/licenses/OLDAP-1.2.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (215, 'Open LDAP Public License v1.3', 'OLDAP-1.3', 'http://spdx.org/licenses/OLDAP-1.3.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (216, 'Open LDAP Public License v1.4', 'OLDAP-1.4', 'http://spdx.org/licenses/OLDAP-1.4.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (217, 'Open LDAP Public License v2.0 (or possibly 2.0A and 2.0B)', 'OLDAP-2.0', 'http://spdx.org/licenses/OLDAP-2.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (218, 'Open LDAP Public License v2.0.1', 'OLDAP-2.0.1', 'http://spdx.org/licenses/OLDAP-2.0.1.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (219, 'Open LDAP Public License v2.1', 'OLDAP-2.1', 'http://spdx.org/licenses/OLDAP-2.1.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (220, 'Open LDAP Public License v2.2', 'OLDAP-2.2', 'http://spdx.org/licenses/OLDAP-2.2.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (221, 'Open LDAP Public License v2.2.1', 'OLDAP-2.2.1', 'http://spdx.org/licenses/OLDAP-2.2.1.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (222, 'Open LDAP Public License v2.3', 'OLDAP-2.3', 'http://spdx.org/licenses/OLDAP-2.3.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (223, 'Open LDAP Public License v2.4', 'OLDAP-2.4', 'http://spdx.org/licenses/OLDAP-2.4.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (224, 'Open LDAP Public License v2.5', 'OLDAP-2.5', 'http://spdx.org/licenses/OLDAP-2.5.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (225, 'Open LDAP Public License v2.6', 'OLDAP-2.6', 'http://spdx.org/licenses/OLDAP-2.6.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (226, 'Open LDAP Public License v2.7', 'OLDAP-2.7', 'http://spdx.org/licenses/OLDAP-2.7.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (227, 'Open LDAP Public License v2.8', 'OLDAP-2.8', 'http://spdx.org/licenses/OLDAP-2.8.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (228, 'Open Market License', 'OML', 'http://spdx.org/licenses/OML.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (229, 'Open Public License v1.0', 'OPL-1.0', 'http://spdx.org/licenses/OPL-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (230, 'Open Software License 1.0', 'OSL-1.0', 'http://spdx.org/licenses/OSL-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (231, 'Open Software License 1.1', 'OSL-1.1', 'http://spdx.org/licenses/OSL-1.1.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (232, 'Open Software License 2.0', 'OSL-2.0', 'http://spdx.org/licenses/OSL-2.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (233, 'Open Software License 2.1', 'OSL-2.1', 'http://spdx.org/licenses/OSL-2.1.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (234, 'Open Software License 3.0', 'OSL-3.0', 'http://spdx.org/licenses/OSL-3.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (235, 'OpenSSL License', 'OpenSSL', 'http://spdx.org/licenses/OpenSSL.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (236, 'PHP License v3.0', 'PHP-3.0', 'http://spdx.org/licenses/PHP-3.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (237, 'PHP License v3.01', 'PHP-3.01', 'http://spdx.org/licenses/PHP-3.01.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (238, 'Plexus Classworlds License', 'Plexus', 'http://spdx.org/licenses/Plexus.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (239, 'PostgreSQL License', 'PostgreSQL', 'http://spdx.org/licenses/PostgreSQL.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (240, 'psfrag License', 'psfrag', 'http://spdx.org/licenses/psfrag.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (241, 'psutils License', 'psutils', 'http://spdx.org/licenses/psutils.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (242, 'Python License 2.0', 'Python-2.0', 'http://spdx.org/licenses/Python-2.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (243, 'Q Public License 1.0', 'QPL-1.0', 'http://spdx.org/licenses/QPL-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (244, 'Qhull License', 'Qhull', 'http://spdx.org/licenses/Qhull.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (245, 'Rdisc License', 'Rdisc', 'http://spdx.org/licenses/Rdisc.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (246, 'RealNetworks Public Source License v1.0', 'RPSL-1.0', 'http://spdx.org/licenses/RPSL-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (247, 'Reciprocal Public License 1.1', 'RPL-1.1', 'http://spdx.org/licenses/RPL-1.1.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (248, 'Reciprocal Public License 1.5', 'RPL-1.5', 'http://spdx.org/licenses/RPL-1.5.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (249, 'Red Hat eCos Public License v1.1', 'RHeCos-1.1', 'http://spdx.org/licenses/RHeCos-1.1.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (250, 'Ricoh Source Code Public License', 'RSCPL', 'http://spdx.org/licenses/RSCPL.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (251, 'RSA Message-Digest License ', 'RSA-MD', 'http://spdx.org/licenses/RSA-MD.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (252, 'Ruby License', 'Ruby', 'http://spdx.org/licenses/Ruby.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (253, 'Sax Public Domain Notice', 'SAX-PD', 'http://spdx.org/licenses/SAX-PD.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (254, 'Saxpath License', 'Saxpath', 'http://spdx.org/licenses/Saxpath.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (255, 'SCEA Shared Source License', 'SCEA', 'http://spdx.org/licenses/SCEA.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (256, 'Scheme Widget Library (SWL) Software License Agreement', 'SWL', 'http://spdx.org/licenses/SWL.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (257, 'Sendmail License', 'Sendmail', 'http://spdx.org/licenses/Sendmail.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (258, 'SGI Free Software License B v1.0', 'SGI-B-1.0', 'http://spdx.org/licenses/SGI-B-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (259, 'SGI Free Software License B v1.1', 'SGI-B-1.1', 'http://spdx.org/licenses/SGI-B-1.1.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (260, 'SGI Free Software License B v2.0', 'SGI-B-2.0', 'http://spdx.org/licenses/SGI-B-2.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (261, 'SIL Open Font License 1.0', 'OFL-1.0', 'http://spdx.org/licenses/OFL-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (262, 'SIL Open Font License 1.1', 'OFL-1.1', 'http://spdx.org/licenses/OFL-1.1.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (263, 'Simple Public License 2.0', 'SimPL-2.0', 'http://spdx.org/licenses/SimPL-2.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (264, 'Sleepycat License', 'Sleepycat', 'http://spdx.org/licenses/Sleepycat.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (265, 'SNIA Public License 1.1', 'SNIA', 'http://spdx.org/licenses/SNIA.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (266, 'Spencer License 86', 'Spencer-86', 'http://spdx.org/licenses/Spencer-86.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (267, 'Spencer License 94', 'Spencer-94', 'http://spdx.org/licenses/Spencer-94.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (268, 'Spencer License 99', 'Spencer-99', 'http://spdx.org/licenses/Spencer-99.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (269, 'Standard ML of New Jersey License', 'SMLNJ', 'http://spdx.org/licenses/SMLNJ.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (270, 'SugarCRM Public License v1.1.3', 'SugarCRM-1.1.3', 'http://spdx.org/licenses/SugarCRM-1.1.3.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (271, 'Sun Industry Standards Source License v1.1', 'SISSL', 'http://spdx.org/licenses/SISSL.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (272, 'Sun Industry Standards Source License v1.2', 'SISSL-1.2', 'http://spdx.org/licenses/SISSL-1.2.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (273, 'Sun Public License v1.0', 'SPL-1.0', 'http://spdx.org/licenses/SPL-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (274, 'Sybase Open Watcom Public License 1.0', 'Watcom-1.0', 'http://spdx.org/licenses/Watcom-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (275, 'TCL/TK License', 'TCL', 'http://spdx.org/licenses/TCL.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (276, 'The Unlicense', 'Unlicense', 'http://spdx.org/licenses/Unlicense.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (277, 'TMate Open Source License', 'TMate', 'http://spdx.org/licenses/TMate.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (278, 'TORQUE v2.5+ Software License v1.1', 'TORQUE-1.1', 'http://spdx.org/licenses/TORQUE-1.1.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (279, 'Trusster Open Source License', 'TOSL', 'http://spdx.org/licenses/TOSL.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (280, 'Unicode Terms of Use', 'Unicode-TOU', 'http://spdx.org/licenses/Unicode-TOU.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (281, 'Universal Permissive License v1.0', 'UPL-1.0', 'http://spdx.org/licenses/UPL-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (282, 'University of Illinois/NCSA Open Source License', 'NCSA', 'http://spdx.org/licenses/NCSA.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (283, 'Vim License', 'Vim', 'http://spdx.org/licenses/Vim.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (284, 'VOSTROM Public License for Open Source', 'VOSTROM', 'http://spdx.org/licenses/VOSTROM.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (285, 'Vovida Software License v1.0', 'VSL-1.0', 'http://spdx.org/licenses/VSL-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (286, 'W3C Software Notice and License (1998-07-20)', 'W3C-19980720', 'http://spdx.org/licenses/W3C-19980720.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (287, 'W3C Software Notice and License (2002-12-31)', 'W3C', 'http://spdx.org/licenses/W3C.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (288, 'Wsuipa License', 'Wsuipa', 'http://spdx.org/licenses/Wsuipa.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (289, 'X.Net License', 'Xnet', 'http://spdx.org/licenses/Xnet.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (290, 'X11 License', 'X11', 'http://spdx.org/licenses/X11.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (291, 'Xerox License', 'Xerox', 'http://spdx.org/licenses/Xerox.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (292, 'XFree86 License 1.1', 'XFree86-1.1', 'http://spdx.org/licenses/XFree86-1.1.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (293, 'xinetd License', 'xinetd', 'http://spdx.org/licenses/xinetd.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (294, 'XPP License', 'xpp', 'http://spdx.org/licenses/xpp.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (295, 'XSkat License', 'XSkat', 'http://spdx.org/licenses/XSkat.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (296, 'Yahoo! Public License v1.0', 'YPL-1.0', 'http://spdx.org/licenses/YPL-1.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (297, 'Yahoo! Public License v1.1', 'YPL-1.1', 'http://spdx.org/licenses/YPL-1.1.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (298, 'Zed License', 'Zed', 'http://spdx.org/licenses/Zed.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (299, 'Zend License v2.0', 'Zend-2.0', 'http://spdx.org/licenses/Zend-2.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (300, 'Zimbra Public License v1.3', 'Zimbra-1.3', 'http://spdx.org/licenses/Zimbra-1.3.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (301, 'Zimbra Public License v1.4', 'Zimbra-1.4', 'http://spdx.org/licenses/Zimbra-1.4.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (302, 'zlib License', 'Zlib', 'http://spdx.org/licenses/Zlib.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (303, 'zlib/libpng License with Acknowledgement', 'zlib-acknowledgement', 'http://spdx.org/licenses/zlib-acknowledgement.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (304, 'Zope Public License 1.1', 'ZPL-1.1', 'http://spdx.org/licenses/ZPL-1.1.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (305, 'Zope Public License 2.0', 'ZPL-2.0', 'http://spdx.org/licenses/ZPL-2.0.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (306, 'Zope Public License 2.1', 'ZPL-2.1', 'http://spdx.org/licenses/ZPL-2.1.html', '', 't');
INSERT INTO "spdx"."licenses" VALUES (307, 'eCos license version 2.0', 'eCos-2.0', 'http://spdx.org/licenses/eCos-2.0', '', 't');
INSERT INTO "spdx"."licenses" VALUES (308, 'GNU General Public License v1.0 or later', 'GPL-1.0+', 'http://spdx.org/licenses/GPL-1.0+', '', 't');
INSERT INTO "spdx"."licenses" VALUES (309, 'GNU General Public License v2.0 or later', 'GPL-2.0+', 'http://spdx.org/licenses/GPL-2.0+', '', 't');
INSERT INTO "spdx"."licenses" VALUES (310, 'GNU General Public License v2.0 w/Autoconf exception', 'GPL-2.0-with-autoconf-exception', 'http://spdx.org/licenses/GPL-2.0-with-autoconf-exception', '', 't');
INSERT INTO "spdx"."licenses" VALUES (311, 'GNU General Public License v2.0 w/Bison exception', 'GPL-2.0-with-bison-exception', 'http://spdx.org/licenses/GPL-2.0-with-bison-exception', '', 't');
INSERT INTO "spdx"."licenses" VALUES (312, 'GNU General Public License v2.0 w/Classpath exception', 'GPL-2.0-with-classpath-exception', 'http://spdx.org/licenses/GPL-2.0-with-classpath-exception', '', 't');
INSERT INTO "spdx"."licenses" VALUES (313, 'GNU General Public License v2.0 w/Font exception', 'GPL-2.0-with-font-exception', 'http://spdx.org/licenses/GPL-2.0-with-font-exception', '', 't');
INSERT INTO "spdx"."licenses" VALUES (314, 'GNU General Public License v2.0 w/GCC Runtime Library exception', 'GPL-2.0-with-GCC-exception', 'http://spdx.org/licenses/GPL-2.0-with-GCC-exception', '', 't');
INSERT INTO "spdx"."licenses" VALUES (315, 'GNU General Public License v3.0 or later', 'GPL-3.0+', 'http://spdx.org/licenses/GPL-3.0+', '', 't');
INSERT INTO "spdx"."licenses" VALUES (316, 'GNU General Public License v3.0 w/Autoconf exception', 'GPL-3.0-with-autoconf-exception', 'http://spdx.org/licenses/GPL-3.0-with-autoconf-exception', '', 't');
INSERT INTO "spdx"."licenses" VALUES (317, 'GNU General Public License v3.0 w/GCC Runtime Library exception', 'GPL-3.0-with-GCC-exception', 'http://spdx.org/licenses/GPL-3.0-with-GCC-exception', '', 't');
INSERT INTO "spdx"."licenses" VALUES (318, 'GNU Lesser General Public License v2.1 or later', 'LGPL-2.1+', 'http://spdx.org/licenses/LGPL-2.1+', '', 't');
INSERT INTO "spdx"."licenses" VALUES (319, 'GNU Lesser General Public License v3.0 or later', 'LGPL-3.0+', 'http://spdx.org/licenses/LGPL-3.0+', '', 't');
INSERT INTO "spdx"."licenses" VALUES (320, 'GNU Library General Public License v2 or later', 'LGPL-2.0+', 'http://spdx.org/licenses/LGPL-2.0+', '', 't');
INSERT INTO "spdx"."licenses" VALUES (321, 'Standard ML of New Jersey License', 'StandardML-NJ', 'http://spdx.org/licenses/StandardML-NJ', '', 't');
INSERT INTO "spdx"."licenses" VALUES (322, 'wxWindows Library License', 'WXwindows', 'http://spdx.org/licenses/WXwindows', '', 't');
COMMIT;

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
  "project_id" int4 NOT NULL DEFAULT nextval('"spdx".projects_project_id_seq'::regclass),
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
-- Records of relationship_types
-- ----------------------------
BEGIN;
INSERT INTO "spdx"."relationship_types" VALUES (1, 'DESCRIBES');
INSERT INTO "spdx"."relationship_types" VALUES (2, 'DESCRIBED_BY');
INSERT INTO "spdx"."relationship_types" VALUES (3, 'CONTAINS');
INSERT INTO "spdx"."relationship_types" VALUES (4, 'CONTAINED_BY');
INSERT INTO "spdx"."relationship_types" VALUES (5, 'GENERATES');
INSERT INTO "spdx"."relationship_types" VALUES (6, 'GENERATED_FROM');
INSERT INTO "spdx"."relationship_types" VALUES (7, 'ANCESTOR_OF');
INSERT INTO "spdx"."relationship_types" VALUES (8, 'DESCENDANT_OF');
INSERT INTO "spdx"."relationship_types" VALUES (9, 'VARIANT_OF');
INSERT INTO "spdx"."relationship_types" VALUES (10, 'DISTRIBUTION_ARTIFACT');
INSERT INTO "spdx"."relationship_types" VALUES (11, 'PATCH_FOR');
INSERT INTO "spdx"."relationship_types" VALUES (12, 'PATCH_APPLIED');
INSERT INTO "spdx"."relationship_types" VALUES (13, 'COPY_OF');
INSERT INTO "spdx"."relationship_types" VALUES (14, 'FILE_ADDED');
INSERT INTO "spdx"."relationship_types" VALUES (15, 'FILE_DELETED');
INSERT INTO "spdx"."relationship_types" VALUES (16, 'FILE_MODIFIED');
INSERT INTO "spdx"."relationship_types" VALUES (17, 'EXPANDED_FROM_ARCHIVE');
INSERT INTO "spdx"."relationship_types" VALUES (18, 'DYNAMIC_LINK');
INSERT INTO "spdx"."relationship_types" VALUES (19, 'STATIC_LINK');
INSERT INTO "spdx"."relationship_types" VALUES (20, 'DATA_FILE_OF');
INSERT INTO "spdx"."relationship_types" VALUES (21, 'TEST_CASE_OF');
INSERT INTO "spdx"."relationship_types" VALUES (22, 'BUILD_TOOL_OF');
INSERT INTO "spdx"."relationship_types" VALUES (23, 'DOCUMENTATION_OF');
INSERT INTO "spdx"."relationship_types" VALUES (24, 'OPTIONAL_COMPONENT_OF');
INSERT INTO "spdx"."relationship_types" VALUES (25, 'METAFILE_OF');
INSERT INTO "spdx"."relationship_types" VALUES (26, 'PACKAGE_OF');
INSERT INTO "spdx"."relationship_types" VALUES (27, 'AMENDS');
INSERT INTO "spdx"."relationship_types" VALUES (28, 'PREREQUISITE_FOR');
INSERT INTO "spdx"."relationship_types" VALUES (29, 'HAS_PREREQUISITE');
INSERT INTO "spdx"."relationship_types" VALUES (30, 'OTHER');
COMMIT;

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
SELECT setval('"spdx"."augur_repo_map_map_id_seq"', 2, false);
ALTER SEQUENCE "spdx"."creator_types_creator_type_id_seq"
OWNED BY "spdx"."creator_types"."creator_type_id";
SELECT setval('"spdx"."creator_types_creator_type_id_seq"', 4, true);
ALTER SEQUENCE "spdx"."creators_creator_id_seq"
OWNED BY "spdx"."creators"."creator_id";
SELECT setval('"spdx"."creators_creator_id_seq"', 2, true);
ALTER SEQUENCE "spdx"."document_namespaces_document_namespace_id_seq"
OWNED BY "spdx"."document_namespaces"."document_namespace_id";
SELECT setval('"spdx"."document_namespaces_document_namespace_id_seq"', 2, false);
ALTER SEQUENCE "spdx"."documents_creators_document_creator_id_seq"
OWNED BY "spdx"."documents_creators"."document_creator_id";
SELECT setval('"spdx"."documents_creators_document_creator_id_seq"', 2, false);
ALTER SEQUENCE "spdx"."documents_document_id_seq"
OWNED BY "spdx"."documents"."document_id";
SELECT setval('"spdx"."documents_document_id_seq"', 2, false);
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
SELECT setval('"spdx"."files_file_id_seq"', 2, false);
ALTER SEQUENCE "spdx"."files_licenses_file_license_id_seq"
OWNED BY "spdx"."files_licenses"."file_license_id";
SELECT setval('"spdx"."files_licenses_file_license_id_seq"', 2, false);
ALTER SEQUENCE "spdx"."files_scans_file_scan_id_seq"
OWNED BY "spdx"."files_scans"."file_scan_id";
SELECT setval('"spdx"."files_scans_file_scan_id_seq"', 2, false);
ALTER SEQUENCE "spdx"."identifiers_identifier_id_seq"
OWNED BY "spdx"."identifiers"."identifier_id";
SELECT setval('"spdx"."identifiers_identifier_id_seq"', 2, false);
ALTER SEQUENCE "spdx"."licenses_license_id_seq"
OWNED BY "spdx"."licenses"."license_id";
SELECT setval('"spdx"."licenses_license_id_seq"', 323, true);
ALTER SEQUENCE "spdx"."packages_files_package_file_id_seq"
OWNED BY "spdx"."packages_files"."package_file_id";
SELECT setval('"spdx"."packages_files_package_file_id_seq"', 2, false);
ALTER SEQUENCE "spdx"."packages_package_id_seq"
OWNED BY "spdx"."packages"."package_id";
SELECT setval('"spdx"."packages_package_id_seq"', 2, false);
ALTER SEQUENCE "spdx"."packages_scans_package_scan_id_seq"
OWNED BY "spdx"."packages_scans"."package_scan_id";
SELECT setval('"spdx"."packages_scans_package_scan_id_seq"', 2, false);
ALTER SEQUENCE "spdx"."projects_project_id_seq"
OWNED BY "spdx"."projects"."project_id";
SELECT setval('"spdx"."projects_project_id_seq"', 2, false);
ALTER SEQUENCE "spdx"."relationship_types_relationship_type_id_seq"
OWNED BY "spdx"."relationship_types"."relationship_type_id";
SELECT setval('"spdx"."relationship_types_relationship_type_id_seq"', 31, true);
ALTER SEQUENCE "spdx"."relationships_relationship_id_seq"
OWNED BY "spdx"."relationships"."relationship_id";
SELECT setval('"spdx"."relationships_relationship_id_seq"', 2, false);
ALTER SEQUENCE "spdx"."scanners_scanner_id_seq"
OWNED BY "spdx"."scanners"."scanner_id";
SELECT setval('"spdx"."scanners_scanner_id_seq"', 2, false);

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
ALTER TABLE "spdx"."projects" ADD CONSTRAINT "projects_pkey" PRIMARY KEY ("project_id");

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
ALTER TABLE "spdx"."files" ADD CONSTRAINT "files_project_id_fkey" FOREIGN KEY ("project_id") REFERENCES "spdx"."projects" ("project_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

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
