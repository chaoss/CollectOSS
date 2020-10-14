-- #SPDX-License-Identifier: MIT
CREATE TABLE augur_data.repo_cluster_messages
(
	msg_cluster_id serial8, 
    repo_id bigint,
    cluster_content integer,
    cluster_mechanism integer,
    "tool_source" varchar,
	"tool_version" varchar,	
	"data_source" varchar,
	"data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY ("msg_cluster_id") 
);

update "augur_operations"."augur_settings" set value = 22 where setting = 'augur_data_version'; 
