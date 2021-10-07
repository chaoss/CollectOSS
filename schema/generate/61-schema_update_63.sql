BEGIN; 
ALTER TABLE "augur_data"."contributors" DROP CONSTRAINT "GL-UNIQUE-B";

ALTER TABLE "augur_data"."contributors" DROP CONSTRAINT "GL-UNIQUE-C";

ALTER TABLE "augur_data"."contributors" ADD CONSTRAINT "GL-UNIQUE-B" UNIQUE ("gl_id") DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE "augur_data"."contributors" ADD CONSTRAINT "GL-UNIQUE-C" UNIQUE ("gl_username") DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE "augur_data"."message" ADD CONSTRAINT "gh-message" UNIQUE ("platform_msg_id", "tool_source");

COMMENT ON CONSTRAINT "gh-message" ON "augur_data"."message" IS 'The GitHub Issue and Pull Request APIs both return messages for Pull Requests. By including the tools source in the natural key, we are preserving the GitHub API’s provenance as a source. 

This has implications for data retrieval. For example, if you are processing messages, attending to the platform_msg_id you can select distinct and avoid duplicate messages. ';


ALTER TABLE "augur_data"."issue_message_ref" ADD CONSTRAINT "repo-issue" UNIQUE ("issue_msg_ref_src_comment_id", "tool_source");

COMMENT ON CONSTRAINT "repo-issue" ON "augur_data"."issue_message_ref" IS 'The comment ID, and tool source are the natural key for this table, same as messages. This preserves the integrity of data provenance from GitHub, which returns identical messages in the issue API and pull request API. Inclusion of the tool ensures both a natural key from the source, and the preservation of provenance. 

Use select distinct on `issue_msg_ref_src_comment_id` to ensure only one of the two messages is analyzed when performing text analysis. ';

update "augur_operations"."augur_settings" set value = 63 where setting = 'augur_data_version';


COMMIT; 

