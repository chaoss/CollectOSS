BEGIN; 

CREATE OR REPLACE FUNCTION pc_chartoint(chartoconvert character varying)
  RETURNS integer AS
$BODY$
SELECT CASE WHEN trim($1) SIMILAR TO '[0-9]+' 
        THEN CAST(trim($1) AS integer) 
    ELSE NULL END;

$BODY$
  LANGUAGE 'sql' IMMUTABLE STRICT;

ALTER TABLE "augur_data"."pull_request_review_message_ref" 
  ALTER COLUMN "pr_review_msg_position" TYPE int8 USING pc_chartoint(pr_review_msg_position),
  ALTER COLUMN "pr_review_msg_original_position" TYPE int8 USING pc_chartoint(pr_review_msg_original_position),
  ALTER COLUMN "pr_review_msg_start_line" TYPE int8  using pc_chartoint(pr_review_msg_start_line),
  ALTER COLUMN "pr_review_msg_original_start_line" TYPE int8 using pc_chartoint(pr_review_msg_original_start_line),
  ALTER COLUMN "pr_review_msg_line" TYPE int8  using pc_chartoint(pr_review_msg_line),
  ALTER COLUMN "pr_review_msg_original_line" TYPE int8 using pc_chartoint(pr_review_msg_original_line);
  
update "augur_operations"."augur_settings" set value = 89 where setting = 'augur_data_version'; 


COMMIT; 