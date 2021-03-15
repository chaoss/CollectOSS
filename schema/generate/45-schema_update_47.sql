
-- ----------------------------
-- Table structure for contributor_repo
-- ----------------------------

BEGIN;

DROP TABLE IF EXISTS "augur_data"."contributor_repo";


CREATE TABLE IF NOT EXISTS "augur_data"."contributor_repo" (
  "cntrb_repo_id" SERIAL8,
  "cntrb_id" int8 NOT NULL,
  "repo_git" varchar COLLATE "pg_catalog"."default" NOT NULL,
  "tool_source" varchar COLLATE "pg_catalog"."default",
  "tool_version" varchar COLLATE "pg_catalog"."default",
  "data_source" varchar COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  "repo_name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "gh_repo_id" int8 NOT NULL,
  "cntrb_category" varchar(255) COLLATE "pg_catalog"."default",
  "event_id" int8
)
;
ALTER TABLE "augur_data"."contributor_repo" OWNER TO "augur";
COMMENT ON COLUMN "augur_data"."contributor_repo"."cntrb_id" IS 'This is not null because what is the point without the contributor in this table? ';
COMMENT ON COLUMN "augur_data"."contributor_repo"."repo_git" IS 'Similar to cntrb_id, we need this data for the table to have meaningful data. ';
COMMENT ON TABLE "augur_data"."contributor_repo" IS 'Developed in Partnership with Andrew Brain. 
 From:   [
  {
    "login": "octocat",
    "id": 1,
    "node_id": "MDQ6VXNlcjE=",
    "avatar_url": "https://github.com/images/error/octocat_happy.gif",
    "gravatar_id": "",
    "url": "https://api.github.com/users/octocat",
    "html_url": "https://github.com/octocat",
    "followers_url": "https://api.github.com/users/octocat/followers",
    "following_url": "https://api.github.com/users/octocat/following{/other_user}",
    "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
    "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
    "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
    "organizations_url": "https://api.github.com/users/octocat/orgs",
    "repos_url": "https://api.github.com/users/octocat/repos",
    "events_url": "https://api.github.com/users/octocat/events{/privacy}",
    "received_events_url": "https://api.github.com/users/octocat/received_events",
    "type": "User",
    "site_admin": false
  }
]
     ';

-- ----------------------------
-- Primary Key structure for table contributor_repo
-- ----------------------------
ALTER TABLE "augur_data"."contributor_repo" DROP CONSTRAINT "cntrb_repo_id_key";

ALTER TABLE "augur_data"."contributor_repo" ADD CONSTRAINT "cntrb_repo_id_key" PRIMARY KEY ("cntrb_repo_id");

-- ----------------------------
-- Foreign Keys structure for table contributor_repo
-- ----------------------------
ALTER TABLE "augur_data"."contributor_repo" DROP CONSTRAINT "fk_contributor_repo_contributors_1";

ALTER TABLE "augur_data"."contributor_repo" ADD CONSTRAINT "fk_contributor_repo_contributors_1" FOREIGN KEY ("cntrb_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON DELETE RESTRICT ON UPDATE CASCADE;

update "augur_operations"."augur_settings" set value = 46 where setting = 'augur_data_version';


COMMIT; 


