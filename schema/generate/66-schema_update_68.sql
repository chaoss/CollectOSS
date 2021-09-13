BEGIN; 
-- ----------------------------
-- Table structure for contributors_aliases
-- ----------------------------
DROP TABLE IF EXISTS "augur_data"."contributors_aliases";
CREATE TABLE "augur_data"."contributors_aliases" (
  "cntrb_alias_id" serial8,
  "cntrb_id" int8 NOT NULL,
  "canonical_email" varchar COLLATE "pg_catalog"."default" NOT NULL,
  "alias_email" varchar COLLATE "pg_catalog"."default" NOT NULL,
  "cntrb_active" int2 NOT NULL DEFAULT 1,
  "cntrb_last_modified" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP
)
;
ALTER TABLE "augur_data"."contributors_aliases" OWNER TO "augur";
COMMENT ON TABLE "augur_data"."contributors_aliases" IS 'An alias will need to be created for every contributor in this model, otherwise we will have to look in 2 places. ';

-- ----------------------------
-- Primary Key structure for table contributors_aliases
-- ----------------------------
ALTER TABLE "augur_data"."contributors_aliases" ADD CONSTRAINT "contributors_aliases_pkey" PRIMARY KEY ("cntrb_alias_id");

-- ----------------------------
-- Foreign Keys structure for table contributors_aliases
-- ----------------------------
ALTER TABLE "augur_data"."contributors_aliases" ADD CONSTRAINT "fk_contributors_aliases_contributors_1" FOREIGN KEY ("cntrb_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON DELETE CASCADE ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED;


update "augur_operations"."augur_settings" set value = 68 where setting = 'augur_data_version'; 

COMMIT; 
