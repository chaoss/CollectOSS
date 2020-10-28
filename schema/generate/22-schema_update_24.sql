-- #SPDX-License-Identifier: MIT
-- 22-schema_update_24.sql
--

CREATE SEQUENCE if not exists "augur_data"."repo_topic_repo_topic_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

CREATE SEQUENCE if not exists "augur_data"."topic_words_topic_words_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

CREATE TABLE if not exists "augur_data"."repo_topic" (
  "repo_topic_id" int8 NOT NULL DEFAULT nextval('"augur_data".repo_topic_repo_topic_id_seq'::regclass),
  "repo_id" int4,
  "topic_id" int4,
  "topic_prob" float8,
  "tool_source" varchar COLLATE "pg_catalog"."default",
  "tool_version" varchar COLLATE "pg_catalog"."default",
  "data_source" varchar COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "repo_topic_pkey" PRIMARY KEY ("repo_topic_id")
)
;

CREATE TABLE if not exists "augur_data"."topic_words" (
  "topic_words_id" int8 NOT NULL DEFAULT nextval('"augur_data".topic_words_topic_words_id_seq'::regclass),
  "topic_id" int4,
  "word" varchar COLLATE "pg_catalog"."default",
  "word_prob" float8,
  "tool_source" varchar COLLATE "pg_catalog"."default",
  "tool_version" varchar COLLATE "pg_catalog"."default",
  "data_source" varchar COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "topic_words_pkey" PRIMARY KEY ("topic_words_id")
)
;

SELECT setval('"augur_data"."repo_topic_repo_topic_id_seq"', 14655, true);

ALTER SEQUENCE "augur_data"."repo_topic_repo_topic_id_seq"
OWNED BY "augur_data"."repo_topic"."repo_topic_id";

SELECT setval('"augur_data"."topic_words_topic_words_id_seq"', 25, true);

ALTER SEQUENCE "augur_data"."topic_words_topic_words_id_seq"
OWNED BY "augur_data"."topic_words"."topic_words_id";



--
--- LSTM Models
--

CREATE SEQUENCE if not exists "augur_data"."lstm_anomaly_models_model_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

CREATE SEQUENCE if not exists "augur_data"."lstm_anomaly_results_result_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

CREATE TABLE if not exists "augur_data"."lstm_anomaly_models" (
  "model_id" int8 NOT NULL DEFAULT nextval('"augur_data".lstm_anomaly_models_model_id_seq'::regclass),
  "model_name" varchar COLLATE "pg_catalog"."default",
  "model_description" varchar COLLATE "pg_catalog"."default",
  "look_back_days" int8,
  "training_days" int8,
  "batch_size" int8,
  "metric" varchar COLLATE "pg_catalog"."default",
  "tool_source" varchar COLLATE "pg_catalog"."default",
  "tool_version" varchar COLLATE "pg_catalog"."default",
  "data_source" varchar COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "lstm_anomaly_models_pkey" PRIMARY KEY ("model_id")
)
;

ALTER TABLE "augur_data"."lstm_anomaly_models" OWNER TO "augur";

CREATE TABLE if not exists "augur_data"."lstm_anomaly_results" (
  "result_id" int8 NOT NULL DEFAULT nextval('"augur_data".lstm_anomaly_results_result_id_seq'::regclass),
  "repo_id" int8,
  "repo_category" varchar COLLATE "pg_catalog"."default",
  "model_id" int8,
  "metric" varchar COLLATE "pg_catalog"."default",
  "contamination_factor" float8,
  "mean_absolute_error" float8,
  "remarks" varchar COLLATE "pg_catalog"."default",
	"metric_field" varchar COLLATE "pg_catalog"."default",
  "mean_absolute_actual_value" float8,
  "mean_absolute_prediction_value" float8,
  "tool_source" varchar COLLATE "pg_catalog"."default",
  "tool_version" varchar COLLATE "pg_catalog"."default",
  "data_source" varchar COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "lstm_anomaly_results_pkey" PRIMARY KEY ("result_id")
)
;

ALTER TABLE "augur_data"."lstm_anomaly_results" OWNER TO "augur";

COMMENT ON COLUMN "augur_data"."lstm_anomaly_results"."metric_field" IS 'This is a listing of all of the endpoint fields included in the generation of the metric. Sometimes there is one, sometimes there is more than one. This will list them all. ';

ALTER TABLE "augur_data"."lstm_anomaly_results" ADD CONSTRAINT "fk_lstm_anomaly_results_lstm_anomaly_models_1" FOREIGN KEY ("model_id") REFERENCES "augur_data"."lstm_anomaly_models" ("model_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE "augur_data"."lstm_anomaly_results" ADD CONSTRAINT "fk_lstm_anomaly_results_repo_1" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

SELECT setval('"augur_data"."lstm_anomaly_models_model_id_seq"', 11, true);

ALTER SEQUENCE "augur_data"."lstm_anomaly_models_model_id_seq"
OWNED BY "augur_data"."lstm_anomaly_models"."model_id";

ALTER SEQUENCE "augur_data"."lstm_anomaly_models_model_id_seq" OWNER TO "augur";

SELECT setval('"augur_data"."lstm_anomaly_results_result_id_seq"', 37, true);

ALTER SEQUENCE "augur_data"."lstm_anomaly_results_result_id_seq"
OWNED BY "augur_data"."lstm_anomaly_results"."result_id";

ALTER SEQUENCE "augur_data"."lstm_anomaly_results_result_id_seq" OWNER TO "augur";

--
---
--


update "augur_operations"."augur_settings" set value = 24 where setting = 'augur_data_version'; 
