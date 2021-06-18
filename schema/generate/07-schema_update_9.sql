-- #SPDX-License-Identifier: MIT
ALTER TABLE "augur_data"."issues" ADD CONSTRAINT "fk_issues_repo" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE CASCADE ON UPDATE CASCADE;
update "augur_operations"."augur_settings" set value = 9 where setting = 'augur_data_version'; 


	-- Index Update for Performance 
CREATE INDEX "reponameindex" ON "augur_data"."repo" USING hash (
  "repo_name"
);

CREATE INDEX "reponameindexbtree" ON "augur_data"."repo" USING btree (
  "repo_name"
);

CREATE INDEX "rgnameindex" ON "augur_data"."repo_groups" USING btree (
  "rg_name" ASC
);

CREATE INDEX "rggrouponrepoindex" ON "augur_data"."repo" USING btree (
  "repo_group_id"
);

CREATE INDEX "repogitindexrep" ON "augur_data"."repo" USING btree (
  "repo_git"
);


COMMENT ON COLUMN "augur_data"."pull_request_meta"."pr_src_meta_label" IS 'This is a representation of the repo:branch information in the pull request. Head is issueing the pull request and base is taking the pull request. For example:  (We do not store all of this)

 "head": {
      "label": "chaoss:pull-request-worker",
      "ref": "pull-request-worker",
      "sha": "6b380c3d6d625616f79d702612ebab6d204614f2",
      "user": {
        "login": "chaoss",
        "id": 29740296,
        "node_id": "MDEyOk9yZ2FuaXphdGlvbjI5NzQwMjk2",
        "avatar_url": "https://avatars2.githubusercontent.com/u/29740296?v=4",
        "gravatar_id": "",
        "url": "https://api.github.com/users/chaoss",
        "html_url": "https://github.com/chaoss",
        "followers_url": "https://api.github.com/users/chaoss/followers",
        "following_url": "https://api.github.com/users/chaoss/following{/other_user}",
        "gists_url": "https://api.github.com/users/chaoss/gists{/gist_id}",
        "starred_url": "https://api.github.com/users/chaoss/starred{/owner}{/repo}",
        "subscriptions_url": "https://api.github.com/users/chaoss/subscriptions",
        "organizations_url": "https://api.github.com/users/chaoss/orgs",
        "repos_url": "https://api.github.com/users/chaoss/repos",
        "events_url": "https://api.github.com/users/chaoss/events{/privacy}",
        "received_events_url": "https://api.github.com/users/chaoss/received_events",
        "type": "Organization",
        "site_admin": false
      },
      "repo": {
        "id": 78134122,
        "node_id": "MDEwOlJlcG9zaXRvcnk3ODEzNDEyMg==",
        "name": "augur",
        "full_name": "chaoss/augur",
        "private": false,
        "owner": {
          "login": "chaoss",
          "id": 29740296,
          "node_id": "MDEyOk9yZ2FuaXphdGlvbjI5NzQwMjk2",
          "avatar_url": "https://avatars2.githubusercontent.com/u/29740296?v=4",
          "gravatar_id": "",
          "url": "https://api.github.com/users/chaoss",
          "html_url": "https://github.com/chaoss",
          "followers_url": "https://api.github.com/users/chaoss/followers",
          "following_url": "https://api.github.com/users/chaoss/following{/other_user}",
          "gists_url": "https://api.github.com/users/chaoss/gists{/gist_id}",
          "starred_url": "https://api.github.com/users/chaoss/starred{/owner}{/repo}",
          "subscriptions_url": "https://api.github.com/users/chaoss/subscriptions",
          "organizations_url": "https://api.github.com/users/chaoss/orgs",
          "repos_url": "https://api.github.com/users/chaoss/repos",
          "events_url": "https://api.github.com/users/chaoss/events{/privacy}",
          "received_events_url": "https://api.github.com/users/chaoss/received_events",
          "type": "Organization",
          "site_admin": false
        },
        "html_url": "https://github.com/chaoss/augur",
        "description": "Python library and web service for Open Source Software Health and Sustainability metrics & data collection.",
        "fork": false,
        "url": "https://api.github.com/repos/chaoss/augur",
        "forks_url": "https://api.github.com/repos/chaoss/augur/forks",
        "keys_url": "https://api.github.com/repos/chaoss/augur/keys{/key_id}",
        "collaborators_url": "https://api.github.com/repos/chaoss/augur/collaborators{/collaborator}",
        "teams_url": "https://api.github.com/repos/chaoss/augur/teams",
        "hooks_url": "https://api.github.com/repos/chaoss/augur/hooks",
        "issue_events_url": "https://api.github.com/repos/chaoss/augur/issues/events{/number}",
        "events_url": "https://api.github.com/repos/chaoss/augur/events",
        "assignees_url": "https://api.github.com/repos/chaoss/augur/assignees{/user}",
        "branches_url": "https://api.github.com/repos/chaoss/augur/branches{/branch}",
        "tags_url": "https://api.github.com/repos/chaoss/augur/tags",
        "blobs_url": "https://api.github.com/repos/chaoss/augur/git/blobs{/sha}",
        "git_tags_url": "https://api.github.com/repos/chaoss/augur/git/tags{/sha}",
        "git_refs_url": "https://api.github.com/repos/chaoss/augur/git/refs{/sha}",
        "trees_url": "https://api.github.com/repos/chaoss/augur/git/trees{/sha}",
        "statuses_url": "https://api.github.com/repos/chaoss/augur/statuses/{sha}",
        "languages_url": "https://api.github.com/repos/chaoss/augur/languages",
        "stargazers_url": "https://api.github.com/repos/chaoss/augur/stargazers",
        "contributors_url": "https://api.github.com/repos/chaoss/augur/contributors",
        "subscribers_url": "https://api.github.com/repos/chaoss/augur/subscribers",
        "subscription_url": "https://api.github.com/repos/chaoss/augur/subscription",
        "commits_url": "https://api.github.com/repos/chaoss/augur/commits{/sha}",
        "git_commits_url": "https://api.github.com/repos/chaoss/augur/git/commits{/sha}",
        "comments_url": "https://api.github.com/repos/chaoss/augur/comments{/number}",
        "issue_comment_url": "https://api.github.com/repos/chaoss/augur/issues/comments{/number}",
        "contents_url": "https://api.github.com/repos/chaoss/augur/contents/{+path}",
        "compare_url": "https://api.github.com/repos/chaoss/augur/compare/{base}...{head}",
        "merges_url": "https://api.github.com/repos/chaoss/augur/merges",
        "archive_url": "https://api.github.com/repos/chaoss/augur/{archive_format}{/ref}",
        "downloads_url": "https://api.github.com/repos/chaoss/augur/downloads",
        "issues_url": "https://api.github.com/repos/chaoss/augur/issues{/number}",
        "pulls_url": "https://api.github.com/repos/chaoss/augur/pulls{/number}",
        "milestones_url": "https://api.github.com/repos/chaoss/augur/milestones{/number}",
        "notifications_url": "https://api.github.com/repos/chaoss/augur/notifications{?since,all,participating}",
        "labels_url": "https://api.github.com/repos/chaoss/augur/labels{/name}",
        "releases_url": "https://api.github.com/repos/chaoss/augur/releases{/id}",
        "deployments_url": "https://api.github.com/repos/chaoss/augur/deployments",
        "created_at": "2017-01-05T17:34:54Z",
        "updated_at": "2019-11-15T00:56:12Z",
        "pushed_at": "2019-12-02T06:27:26Z",
        "git_url": "git://github.com/chaoss/augur.git",
        "ssh_url": "git@github.com:chaoss/augur.git",
        "clone_url": "https://github.com/chaoss/augur.git",
        "svn_url": "https://github.com/chaoss/augur",
        "homepage": "http://augur.osshealth.io/",
        "size": 82004,
        "stargazers_count": 153,
        "watchers_count": 153,
        "language": "Python",
        "has_issues": true,
        "has_projects": false,
        "has_downloads": true,
        "has_wiki": false,
        "has_pages": true,
        "forks_count": 205,
        "mirror_url": null,
        "archived": false,
        "disabled": false,
        "open_issues_count": 14,
        "license": {
          "key": "mit",
          "name": "MIT License",
          "spdx_id": "MIT",
          "url": "https://api.github.com/licenses/mit",
          "node_id": "MDc6TGljZW5zZTEz"
        },
        "forks": 205,
        "open_issues": 14,
        "watchers": 153,
        "default_branch": "master"
      }
    },
    "base": {
      "label": "chaoss:dev",
      "ref": "dev",
      "sha": "bfd2d34b51659613dd842cf83c3873f7699c2a0e",
      "user": {
        "login": "chaoss",
        "id": 29740296,
        "node_id": "MDEyOk9yZ2FuaXphdGlvbjI5NzQwMjk2",
        "avatar_url": "https://avatars2.githubusercontent.com/u/29740296?v=4",
        "gravatar_id": "",
        "url": "https://api.github.com/users/chaoss",
        "html_url": "https://github.com/chaoss",
        "followers_url": "https://api.github.com/users/chaoss/followers",
        "following_url": "https://api.github.com/users/chaoss/following{/other_user}",
        "gists_url": "https://api.github.com/users/chaoss/gists{/gist_id}",
        "starred_url": "https://api.github.com/users/chaoss/starred{/owner}{/repo}",
        "subscriptions_url": "https://api.github.com/users/chaoss/subscriptions",
        "organizations_url": "https://api.github.com/users/chaoss/orgs",
        "repos_url": "https://api.github.com/users/chaoss/repos",
        "events_url": "https://api.github.com/users/chaoss/events{/privacy}",
        "received_events_url": "https://api.github.com/users/chaoss/received_events",
        "type": "Organization",
        "site_admin": false
      },
      "repo": {
        "id": 78134122,
        "node_id": "MDEwOlJlcG9zaXRvcnk3ODEzNDEyMg==",
        "name": "augur",
        "full_name": "chaoss/augur",
        "private": false,
        "owner": {
          "login": "chaoss",
          "id": 29740296,
          "node_id": "MDEyOk9yZ2FuaXphdGlvbjI5NzQwMjk2",
          "avatar_url": "https://avatars2.githubusercontent.com/u/29740296?v=4",
          "gravatar_id": "",
          "url": "https://api.github.com/users/chaoss",
          "html_url": "https://github.com/chaoss",
          "followers_url": "https://api.github.com/users/chaoss/followers",
          "following_url": "https://api.github.com/users/chaoss/following{/other_user}",
          "gists_url": "https://api.github.com/users/chaoss/gists{/gist_id}",
          "starred_url": "https://api.github.com/users/chaoss/starred{/owner}{/repo}",
          "subscriptions_url": "https://api.github.com/users/chaoss/subscriptions",
          "organizations_url": "https://api.github.com/users/chaoss/orgs",
          "repos_url": "https://api.github.com/users/chaoss/repos",
          "events_url": "https://api.github.com/users/chaoss/events{/privacy}",
          "received_events_url": "https://api.github.com/users/chaoss/received_events",
          "type": "Organization",
          "site_admin": false
        },
';

ALTER TABLE "augur_data"."pull_request_repo" ALTER COLUMN "pr_src_node_id" TYPE varchar COLLATE "pg_catalog"."default" USING "pr_src_node_id"::varchar;


