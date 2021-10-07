BEGIN; 
ALTER TABLE "augur_data"."pull_request_reviews" ADD CONSTRAINT "sourcepr-review-id" UNIQUE ("pr_review_src_id", "tool_source");

COMMENT ON CONSTRAINT "sourcepr-review-id" ON "augur_data"."pull_request_reviews" IS 'Natural Key from Source, plus tool source to account for different platforms like GitHub and gitlab. ';
update "augur_operations"."augur_settings" set value = 64 where setting = 'augur_data_version';


COMMIT; 

