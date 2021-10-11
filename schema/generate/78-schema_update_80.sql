BEGIN; 

update "augur_operations"."augur_settings" set value = 80 where setting = 'augur_data_version'; 


COMMIT; 