
BEGIN;

ALTER TABLE "augur_data"."topic_words" 
  DROP CONSTRAINT IF EXISTS "fk_topic_words_repo_topic_1";

update "augur_operations"."augur_settings" set value = 48 where setting = 'augur_data_version';


COMMIT; 

