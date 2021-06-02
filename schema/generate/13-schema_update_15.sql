-- #SPDX-License-Identifier: MIT
INSERT INTO "augur_operations"."augur_settings"("id", "setting", "value", "last_modified") VALUES (2, 'augur_api_key', 'invalid_key', CURRENT_TIMESTAMP);

update "augur_operations"."augur_settings" set value = 15 where setting = 'augur_data_version'; 
