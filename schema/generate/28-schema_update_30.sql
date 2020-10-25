ALTER TABLE "augur_data"."message_analysis" ADD CONSTRAINT "fk_message_analysis_message_1" FOREIGN KEY ("msg_id") REFERENCES "augur_data"."message" ("msg_id");

ALTER TABLE "augur_data"."message_analysis_summary" ADD CONSTRAINT "fk_message_analysis_summary_repo_1" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id");

ALTER TABLE "augur_data"."message_sentiment" ADD CONSTRAINT "fk_message_sentiment_message_1" FOREIGN KEY ("msg_id") REFERENCES "augur_data"."message" ("msg_id");

ALTER TABLE "augur_data"."message_sentiment_summary" ADD CONSTRAINT "fk_message_sentiment_summary_repo_1" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id");

ALTER TABLE "augur_data"."repo_cluster_messages" ADD CONSTRAINT "fk_repo_cluster_messages_repo_1" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id");

ALTER TABLE "augur_data"."topic_words" ALTER COLUMN "topic_id" TYPE int8 USING "topic_id"::int8;

ALTER TABLE "augur_data"."topic_words" ADD CONSTRAINT "fk_topic_words_repo_topic_1" FOREIGN KEY ("topic_id") REFERENCES "augur_data"."repo_topic" ("repo_topic_id");

DROP TABLE IF EXISTS "augur_data"."_git_census";

DROP TABLE IF EXISTS "augur_data"."repo_ghtorrent_map";

DROP TABLE IF EXISTS "augur_operations"."cncf_users";

DROP TABLE IF EXISTS "augur_operations"."science";


update "augur_operations"."augur_settings" set value = 30 where setting = 'augur_data_version'; 
