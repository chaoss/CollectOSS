-- Adding GitLab Platform
INSERT INTO "augur_data"."platform" ("pltfrm_id", "pltfrm_name", "pltfrm_version", "pltfrm_release_date", "tool_source", "tool_version", "data_source", "data_collection_date") VALUES (25151, 'GitLab', '3', '2020-12-27', 'Manual Entry', 'Sean Goggins', 'GitLab', '2020-12-27 16:07:20');
--  # Pull request commit updates
update "augur_operations"."augur_settings" set value = 35 where setting = 'augur_data_version'; 
