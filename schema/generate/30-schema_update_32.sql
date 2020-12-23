CREATE TABLE "augur_data"."pull_request_analysis" (
  "pull_request_analysis_id" serial8,
  "pull_request_id" int8,
  "merge_probability" float8,
  "mechanism" varchar,
  "tool_source" varchar,
  "tool_version" varchar,
  "data_source" varchar,
  "data_collection_date" timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("pull_request_analysis_id")
)
;

ALTER TABLE "augur_data"."pull_request_analysis" OWNER TO "augur";

COMMENT ON COLUMN "augur_data"."pull_request_analysis"."pull_request_id" IS 'It would be better if the pull request worker is run first to fetch the latest PRs before analyzing';

COMMENT ON COLUMN "augur_data"."pull_request_analysis"."merge_probability" IS 'Indicates the probability of the PR being merged';

COMMENT ON COLUMN "augur_data"."pull_request_analysis"."mechanism" IS 'the ML model used for prediction (It is XGBoost Classifier at present)';

ALTER TABLE "augur_data"."pull_request_analysis" ADD CONSTRAINT "fk_pull_request_analysis_pull_requests_1" FOREIGN KEY ("pull_request_id") REFERENCES "augur_data"."pull_requests" ("pull_request_id") ON DELETE CASCADE ON UPDATE CASCADE;

CREATE  INDEX CONCURRENTLY "probability_idx"  ON "augur_data"."pull_request_analysis" USING btree (
  "merge_probability" DESC NULLS LAST 
);

CREATE INDEX CONCURRENTLY  "pr_anal_idx"  ON "augur_data"."pull_request_analysis" USING btree (
  "pull_request_id"
);

update "augur_operations"."augur_settings" set value = 32 where setting = 'augur_data_version'; 
