BEGIN; 

ALTER TABLE "augur_data"."pull_request_review_message_ref" 
  DROP CONSTRAINT "fk_pull_request_review_message_ref_message_1",
  DROP CONSTRAINT "fk_pull_request_review_message_ref_pull_request_reviews_1",
  ADD COLUMN "pull_request_id" int8,
  ADD CONSTRAINT "fk_pull_request_review_message_ref_message_1" FOREIGN KEY ("msg_id") REFERENCES "augur_data"."message" ("msg_id") ON DELETE RESTRICT ON UPDATE CASCADE,
  ADD CONSTRAINT "fk_pull_request_review_message_ref_pull_request_reviews_1" FOREIGN KEY ("pr_review_id") REFERENCES "augur_data"."pull_request_reviews" ("pr_review_id") ON DELETE RESTRICT ON UPDATE CASCADE,
  ADD CONSTRAINT "fk_pull_request_for_reviews_1" FOREIGN KEY ("pull_request_id") REFERENCES "augur_data"."pull_requests" ("pull_request_id") ON DELETE RESTRICT ON UPDATE CASCADE;

  update "augur_operations"."augur_settings" set value = 68 where setting = 'augur_data_version'; 

COMMIT; 