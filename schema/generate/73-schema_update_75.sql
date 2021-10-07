BEGIN; 

ALTER TABLE "augur_data"."contributors" ADD CONSTRAINT "GL-cntrb-LOGIN-UNIQUE" UNIQUE ("cntrb_login");

update "augur_operations"."augur_settings" set value = 75 where setting = 'augur_data_version'; 


COMMIT; 