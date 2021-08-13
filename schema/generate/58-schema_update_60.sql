BEGIN; 

ALTER TABLE "augur_data"."contributors" 
  ADD CONSTRAINT "GL-UNIQUE-B" UNIQUE ("gl_id"),
  ADD CONSTRAINT "GL-UNIQUE-C" UNIQUE ("gl_username");

update "augur_operations"."augur_settings" set value = 60 where setting = 'augur_data_version';


COMMIT; 

