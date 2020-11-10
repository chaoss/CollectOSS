CREATE SEQUENCE "augur_data"."discourse_insights_msg_discourse_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

CREATE SEQUENCE "augur_data"."discourse_insights_msg_discourse_id_seq1" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

COMMENT ON TABLE "augur_data"."chaoss_metric_status" IS 'This table used to track CHAOSS Metric implementations in Augur, but due to the constantly changing location of that information, it is for the moment not actively populated. ';

COMMENT ON TABLE "augur_data"."contributors_history" IS 'For GitHub, this should be repeated from gh_login. for other systems, it should be that systems login. 

At this time the table is not populated. ';

CREATE TABLE "augur_data"."discourse_insights" (
  "msg_discourse_id" int8 NOT NULL DEFAULT nextval('"augur_data".discourse_insights_msg_discourse_id_seq1'::regclass),
  "msg_id" int8,
  "discourse_act" varchar COLLATE "pg_catalog"."default",
  "tool_source" varchar COLLATE "pg_catalog"."default",
  "tool_version" varchar COLLATE "pg_catalog"."default",
  "data_source" varchar COLLATE "pg_catalog"."default",
  "data_collection_date" timestamptz(6) DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "discourse_insights_pkey" PRIMARY KEY ("msg_discourse_id")
)
;

ALTER TABLE "augur_data"."discourse_insights" OWNER TO "augur";

ALTER TABLE "augur_data"."discourse_insights" ADD CONSTRAINT "fk_discourse_insights_message_1" FOREIGN KEY ("msg_id") REFERENCES "augur_data"."message" ("msg_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

SELECT setval('"augur_data"."discourse_insights_msg_discourse_id_seq"', 1, false);

ALTER SEQUENCE "augur_data"."discourse_insights_msg_discourse_id_seq" OWNER TO "augur";

SELECT setval('"augur_data"."discourse_insights_msg_discourse_id_seq1"', 1, false);

ALTER SEQUENCE "augur_data"."discourse_insights_msg_discourse_id_seq1"
OWNED BY "augur_data"."discourse_insights"."msg_discourse_id";

ALTER SEQUENCE "augur_data"."discourse_insights_msg_discourse_id_seq1" OWNER TO "augur";

update "augur_operations"."augur_settings" set value = 31 where setting = 'augur_data_version'; 
