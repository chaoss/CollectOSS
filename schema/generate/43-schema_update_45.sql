
CREATE SEQUENCE IF NOT EXISTS "augur_operations"."worker_oauth_oauth_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 620000
CACHE 1;

COMMENT ON TABLE "augur_operations"."augur_settings" IS 'Augur settings include the schema version, and the Augur API Key as of 10/25/2020. Future augur settings may be stored in this table, which has the basic structure of a name-value pair. ';

COMMENT ON TABLE "augur_operations"."repos_fetch_log" IS 'For future use when we move all working tables to the augur_operations schema. ';

COMMENT ON TABLE "augur_operations"."worker_history" IS 'This table stores the complete history of job execution, including success and failure. It is useful for troubleshooting. ';

COMMENT ON TABLE "augur_operations"."worker_job" IS 'This table stores the jobs workers collect data for. A job is found in the code, and in the augur.config.json under the construct of a “model”. ';

ALTER TABLE "augur_operations"."worker_job" ALTER COLUMN "description" SET DEFAULT 'None'::character varying;

COMMENT ON TABLE "augur_operations"."worker_oauth" IS 'This table stores credentials for retrieving data from platform API’s. Entries in this table must comply with the terms of service for each platform. ';

ALTER TABLE "augur_operations"."worker_oauth" ALTER COLUMN "oauth_id" TYPE int8 USING "oauth_id"::int8;

ALTER TABLE "augur_operations"."worker_oauth" ALTER COLUMN "oauth_id" SET DEFAULT nextval('"augur_operations".worker_oauth_oauth_id_seq'::regclass);

ALTER TABLE "augur_operations"."worker_oauth" ADD CONSTRAINT "worker_oauth_pkey" PRIMARY KEY ("oauth_id");

COMMENT ON TABLE "augur_operations"."worker_settings_facade" IS 'For future use when we move all working tables to the augur_operations schema. ';

COMMENT ON TABLE "augur_operations"."working_commits" IS 'For future use when we move all working tables to the augur_operations schema. ';

SELECT setval('"augur_operations"."affiliations_corp_id_seq"', 1, false);


ALTER SEQUENCE "augur_operations"."affiliations_corp_id_seq" OWNER TO "augur";

SELECT setval('"augur_operations"."gh_worker_history_history_id_seq"', 6300000, true);

SELECT setval('"augur_operations"."worker_oauth_oauth_id_seq"', 6300000, true);

ALTER SEQUENCE "augur_operations"."worker_oauth_oauth_id_seq" OWNER TO "augur";

CREATE INDEX "repos_id,statusops" ON "augur_operations"."repos_fetch_log" USING btree (
  "repos_id" "pg_catalog"."int4_ops" ASC NULLS LAST,
  "status" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);



update "augur_operations"."augur_settings" set value = 45 where setting = 'augur_data_version'; 
