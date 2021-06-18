-- Contributor repo and machine learning index changes

CREATE SEQUENCE "augur_data"."contributor_repo_cntrb_repo_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

CREATE TABLE "augur_data"."contributor_repo" (
  "cntrb_repo_id" int4 NOT NULL DEFAULT nextval('"augur_data".contributor_repo_cntrb_repo_id_seq'::regclass),
  "cntrb_id" int8 NOT NULL,
  "repo_git" varchar COLLATE "pg_catalog"."default" NOT NULL,
  "cntrb_category" varchar COLLATE "pg_catalog"."default",
  "tool_source" varchar COLLATE "pg_catalog"."default",
  "tool_version" varchar COLLATE "pg_catalog"."default",
  "data_source" varchar COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "cntrb_repo_id_key" PRIMARY KEY ("cntrb_repo_id")
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

ALTER TABLE "augur_data"."contributor_repo" ADD CONSTRAINT "fk_contributor_repo_contributors_1" FOREIGN KEY ("cntrb_repo_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE "augur_data"."repo_topic" ADD CONSTRAINT "fk_repo_topic_repo_1" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

SELECT setval('"augur_data"."contributor_repo_cntrb_repo_id_seq"', 1, false);

ALTER SEQUENCE "augur_data"."contributor_repo_cntrb_repo_id_seq"
OWNED BY "augur_data"."contributor_repo"."cntrb_repo_id";

ALTER SEQUENCE "augur_data"."contributor_repo_cntrb_repo_id_seq" OWNER TO "augur";


update "augur_operations"."augur_settings" set value = 37 where setting = 'augur_data_version'; 
