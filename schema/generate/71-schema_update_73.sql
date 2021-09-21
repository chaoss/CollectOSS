BEGIN;

ALTER TABLE "augur_data"."pull_request_reviews" 
  ADD COLUMN "platform_id" int8 DEFAULT 25150,
  ADD CONSTRAINT "fk-review-platform" FOREIGN KEY ("platform_id") REFERENCES "augur_data"."platform" ("pltfrm_id") ON DELETE RESTRICT ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED;


update "augur_operations"."augur_settings" set value = 72 where setting = 'augur_data_version'; 


COMMIT; 