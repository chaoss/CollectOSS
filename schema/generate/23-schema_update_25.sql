-- #SPDX-License-Identifier: MIT
-- DROP TABLE "augur_data"."message_analysis";
-- DROP TABLE "augur_data"."message_analysis_summary";

CREATE TABLE if not exists "augur_data"."message_analysis" (
"msg_analysis_id" serial8 NOT NULL,
"msg_id" int8,
"worker_run_id" int8,
"sentiment_score" float8,
"reconstruction_error" float8,
"novelty_flag" bool,
"feedback_flag" bool,
"tool_source" varchar,
"tool_version" varchar,
"data_source" varchar,
"data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
PRIMARY KEY ("msg_analysis_id") 
)
WITHOUT OIDS;
COMMENT ON COLUMN "augur_data"."message_analysis"."worker_run_id" IS 'This column is used to indicate analyses run by a worker during the same execution period, and is useful for grouping, and time series analysis.  ';
COMMENT ON COLUMN "augur_data"."message_analysis"."sentiment_score" IS 'A sentiment analysis score. Zero is neutral, negative numbers are negative sentiment, and positive numbers are positive sentiment. ';
COMMENT ON COLUMN "augur_data"."message_analysis"."reconstruction_error" IS 'Each message is converted to a 250 dimensin doc2vec vector, so the reconstruction error is the difference between what the predicted vector and the actual vector.';
COMMENT ON COLUMN "augur_data"."message_analysis"."novelty_flag" IS 'This is an analysis of the degree to which the message is novel when compared to other messages in a repository.  For example when bots are producing numerous identical messages, the novelty score is low. It would also be a low novelty score when several people are making the same coment. ';
COMMENT ON COLUMN "augur_data"."message_analysis"."feedback_flag" IS 'This exists to provide the user with an opportunity provide feedback on the resulting the sentiment scores. ';
ALTER TABLE "augur_data"."message_analysis" OWNER TO "augur";

CREATE TABLE if not exists "augur_data"."message_analysis_summary" (
"msg_summary_id" serial8 NOT NULL,
"repo_id" int8,
"worker_run_id" int8,
"positive_ratio" float8,
"negative_ratio" float8,
"novel_count" int8,
"period" timestamp(0),
"tool_source" varchar,
"tool_version" varchar,
"data_source" varchar,
"data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
PRIMARY KEY ("msg_summary_id") 
)
WITHOUT OIDS;
COMMENT ON TABLE "augur_data"."message_analysis_summary" IS 'In a relationally perfect world, we would have a table called “message_analysis_run” the incremented the “worker_run_id” for both message_analysis and message_analysis_summary. For now, we decided this was overkill. ';
COMMENT ON COLUMN "augur_data"."message_analysis_summary"."worker_run_id" IS 'This value should reflect the worker_run_id for the messages summarized in the table. There is not a relation between these two tables for that purpose because its not *really*, relationaly a concept unless we create a third table for "worker_run_id", which we determined was unnecessarily complex. ';
COMMENT ON COLUMN "augur_data"."message_analysis_summary"."novel_count" IS 'The number of messages identified as novel during the analyzed period';
COMMENT ON COLUMN "augur_data"."message_analysis_summary"."period" IS 'The whole timeline is divided into periods based on the definition of time period for analysis, which is user specified. Timestamp of the first period to look at, until the end of messages at the data of execution. ';
ALTER TABLE "augur_data"."message_analysis_summary" OWNER TO "augur";


update "augur_operations"."augur_settings" set value = 25 where setting = 'augur_data_version'; 
