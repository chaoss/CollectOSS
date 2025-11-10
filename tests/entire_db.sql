--
-- PostgreSQL database dump
--

-- Dumped from database version 12.14 (Ubuntu 12.14-0ubuntu0.20.04.1)
-- Dumped by pg_dump version 12.14 (Ubuntu 12.14-0ubuntu0.20.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: augur_data; Type: SCHEMA; Schema: -; Owner: augur
--

CREATE SCHEMA augur_data;


ALTER SCHEMA augur_data OWNER TO augur;

--
-- Name: augur_operations; Type: SCHEMA; Schema: -; Owner: augur
--

CREATE SCHEMA augur_operations;


ALTER SCHEMA augur_operations OWNER TO augur;

--
-- Name: spdx; Type: SCHEMA; Schema: -; Owner: augur
--

CREATE SCHEMA spdx;


ALTER SCHEMA spdx OWNER TO augur;

--
-- Name: toss_specific; Type: SCHEMA; Schema: -; Owner: augur
--

CREATE SCHEMA toss_specific;


ALTER SCHEMA toss_specific OWNER TO augur;

--
-- Name: refresh_aggregates(); Type: PROCEDURE; Schema: augur_data; Owner: augur
--

CREATE PROCEDURE augur_data.refresh_aggregates()
    LANGUAGE plpgsql
    AS $$
    begin
        perform pg_advisory_lock(124);
        execute 'REFRESH MATERIALIZED VIEW "augur_data"."issue_reporter_created_at"';
        perform pg_advisory_unlock(124);
    end;
$$;


ALTER PROCEDURE augur_data.refresh_aggregates() OWNER TO augur;

--
-- Name: create_constraint_if_not_exists(text, text, text); Type: FUNCTION; Schema: public; Owner: augur
--

CREATE FUNCTION public.create_constraint_if_not_exists(t_name text, c_name text, constraint_sql text) RETURNS void
    LANGUAGE plpgsql
    AS $$
  BEGIN
    -- Look for our constraint
    IF NOT EXISTS (SELECT constraint_name
                   FROM information_schema.constraint_column_usage
                   WHERE constraint_name = c_name) THEN
        EXECUTE 'ALTER TABLE ' || t_name || ' ADD CONSTRAINT ' || c_name || ' ' || constraint_sql;
    END IF;
  END;
$$;


ALTER FUNCTION public.create_constraint_if_not_exists(t_name text, c_name text, constraint_sql text) OWNER TO augur;

--
-- Name: pc_chartoint(character varying); Type: FUNCTION; Schema: public; Owner: augur
--

CREATE FUNCTION public.pc_chartoint(chartoconvert character varying) RETURNS integer
    LANGUAGE sql IMMUTABLE STRICT
    AS $_$
SELECT CASE WHEN trim($1) SIMILAR TO '[0-9]+' 
        THEN CAST(trim($1) AS integer) 
    ELSE NULL END;

$_$;


ALTER FUNCTION public.pc_chartoint(chartoconvert character varying) OWNER TO augur;

--
-- Name: refresh_aggregates(); Type: PROCEDURE; Schema: public; Owner: augur
--

CREATE PROCEDURE public.refresh_aggregates()
    LANGUAGE plpgsql
    AS $$
    begin
        perform pg_advisory_lock(124);
        execute 'REFRESH MATERIALIZED VIEW "augur_data"."issue_reporter_created_at"';
        perform pg_advisory_unlock(124);
    end;
$$;


ALTER PROCEDURE public.refresh_aggregates() OWNER TO augur;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: analysis_log; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.analysis_log (
    repos_id integer NOT NULL,
    status character varying NOT NULL,
    date_attempted timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE augur_data.analysis_log OWNER TO augur;

--
-- Name: pull_requests_pull_request_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.pull_requests_pull_request_id_seq
    START WITH 25430
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.pull_requests_pull_request_id_seq OWNER TO augur;

--
-- Name: pull_requests; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.pull_requests (
    pull_request_id bigint DEFAULT nextval('augur_data.pull_requests_pull_request_id_seq'::regclass) NOT NULL,
    repo_id bigint DEFAULT 0,
    pr_url character varying,
    pr_src_id bigint,
    pr_src_node_id character varying,
    pr_html_url character varying,
    pr_diff_url character varying,
    pr_patch_url character varying,
    pr_issue_url character varying,
    pr_augur_issue_id bigint,
    pr_src_number bigint,
    pr_src_state character varying,
    pr_src_locked boolean,
    pr_src_title character varying,
    pr_body text,
    pr_created_at timestamp(0) without time zone,
    pr_updated_at timestamp(0) without time zone,
    pr_closed_at timestamp(0) without time zone,
    pr_merged_at timestamp(0) without time zone,
    pr_merge_commit_sha character varying,
    pr_teams bigint,
    pr_milestone character varying,
    pr_commits_url character varying,
    pr_review_comments_url character varying,
    pr_review_comment_url character varying,
    pr_comments_url character varying,
    pr_statuses_url character varying,
    pr_meta_head_id character varying,
    pr_meta_base_id character varying,
    pr_src_issue_url character varying,
    pr_src_comments_url character varying,
    pr_src_review_comments_url character varying,
    pr_src_commits_url character varying,
    pr_src_statuses_url character varying,
    pr_src_author_association character varying,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP,
    pr_augur_contributor_id uuid
);


ALTER TABLE augur_data.pull_requests OWNER TO augur;

--
-- Name: COLUMN pull_requests.pr_src_id; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.pull_requests.pr_src_id IS 'The pr_src_id is unique across all of github.';


--
-- Name: COLUMN pull_requests.pr_augur_issue_id; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.pull_requests.pr_augur_issue_id IS 'This is to link to the augur stored related issue';


--
-- Name: COLUMN pull_requests.pr_src_number; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.pull_requests.pr_src_number IS 'The pr_src_number is unique within a repository.';


--
-- Name: COLUMN pull_requests.pr_teams; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.pull_requests.pr_teams IS 'One to many with pull request teams. ';


--
-- Name: COLUMN pull_requests.pr_review_comment_url; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.pull_requests.pr_review_comment_url IS 'This is a field with limited utility. It does expose how to access a specific comment if needed with parameters. If the source changes URL structure, it may be useful';


--
-- Name: COLUMN pull_requests.pr_meta_head_id; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.pull_requests.pr_meta_head_id IS 'The metadata for the head repo that links to the pull_request_meta table. ';


--
-- Name: COLUMN pull_requests.pr_meta_base_id; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.pull_requests.pr_meta_base_id IS 'The metadata for the base repo that links to the pull_request_meta table. ';


--
-- Name: COLUMN pull_requests.pr_augur_contributor_id; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.pull_requests.pr_augur_contributor_id IS 'This is to link to the augur contributor record. ';


--
-- Name: api_get_all_repo_prs; Type: MATERIALIZED VIEW; Schema: augur_data; Owner: augur
--

CREATE MATERIALIZED VIEW augur_data.api_get_all_repo_prs AS
 SELECT pull_requests.repo_id,
    count(*) AS pull_requests_all_time
   FROM augur_data.pull_requests
  GROUP BY pull_requests.repo_id
  WITH NO DATA;


ALTER TABLE augur_data.api_get_all_repo_prs OWNER TO augur;

--
-- Name: commits_cmt_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.commits_cmt_id_seq
    START WITH 25430
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.commits_cmt_id_seq OWNER TO augur;

--
-- Name: commits; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.commits (
    cmt_id bigint DEFAULT nextval('augur_data.commits_cmt_id_seq'::regclass) NOT NULL,
    repo_id bigint NOT NULL,
    cmt_commit_hash character varying(80) NOT NULL,
    cmt_author_name character varying NOT NULL,
    cmt_author_raw_email character varying NOT NULL,
    cmt_author_email character varying NOT NULL,
    cmt_author_date character varying(10) NOT NULL,
    cmt_author_affiliation character varying,
    cmt_committer_name character varying NOT NULL,
    cmt_committer_raw_email character varying NOT NULL,
    cmt_committer_email character varying NOT NULL,
    cmt_committer_date character varying NOT NULL,
    cmt_committer_affiliation character varying,
    cmt_added integer NOT NULL,
    cmt_removed integer NOT NULL,
    cmt_whitespace integer NOT NULL,
    cmt_filename character varying NOT NULL,
    cmt_date_attempted timestamp(0) without time zone NOT NULL,
    cmt_ght_committer_id integer,
    cmt_ght_committed_at timestamp(0) without time zone,
    cmt_committer_timestamp timestamp(0) with time zone,
    cmt_author_timestamp timestamp(0) with time zone,
    cmt_author_platform_username character varying,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP,
    cmt_ght_author_id uuid
)
WITH (autovacuum_vacuum_scale_factor='0', autovacuum_vacuum_threshold='1000');


ALTER TABLE augur_data.commits OWNER TO augur;

--
-- Name: TABLE commits; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON TABLE augur_data.commits IS 'Commits.
Each row represents changes to one FILE within a single commit. So you will encounter multiple rows per commit hash in many cases. ';


--
-- Name: api_get_all_repos_commits; Type: MATERIALIZED VIEW; Schema: augur_data; Owner: augur
--

CREATE MATERIALIZED VIEW augur_data.api_get_all_repos_commits AS
 SELECT commits.repo_id,
    count(DISTINCT commits.cmt_commit_hash) AS commits_all_time
   FROM augur_data.commits
  GROUP BY commits.repo_id
  WITH NO DATA;


ALTER TABLE augur_data.api_get_all_repos_commits OWNER TO augur;

--
-- Name: issue_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.issue_seq
    START WITH 31000
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.issue_seq OWNER TO augur;

--
-- Name: issues; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.issues (
    issue_id bigint DEFAULT nextval('augur_data.issue_seq'::regclass) NOT NULL,
    repo_id bigint,
    pull_request bigint,
    pull_request_id bigint,
    created_at timestamp(0) without time zone,
    issue_title character varying,
    issue_body character varying,
    comment_count bigint,
    updated_at timestamp(0) without time zone,
    closed_at timestamp(0) without time zone,
    due_on timestamp(0) without time zone,
    repository_url character varying,
    issue_url character varying,
    labels_url character varying,
    comments_url character varying,
    events_url character varying,
    html_url character varying,
    issue_state character varying,
    issue_node_id character varying,
    gh_issue_number bigint,
    gh_issue_id bigint,
    gh_user_id bigint,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP,
    reporter_id uuid,
    cntrb_id uuid
);


ALTER TABLE augur_data.issues OWNER TO augur;

--
-- Name: COLUMN issues.reporter_id; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.issues.reporter_id IS 'The ID of the person who opened the issue. ';


--
-- Name: COLUMN issues.cntrb_id; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.issues.cntrb_id IS 'The ID of the person who closed the issue. ';


--
-- Name: api_get_all_repos_issues; Type: MATERIALIZED VIEW; Schema: augur_data; Owner: augur
--

CREATE MATERIALIZED VIEW augur_data.api_get_all_repos_issues AS
 SELECT issues.repo_id,
    count(*) AS issues_all_time
   FROM augur_data.issues
  WHERE (issues.pull_request IS NULL)
  GROUP BY issues.repo_id
  WITH NO DATA;


ALTER TABLE augur_data.api_get_all_repos_issues OWNER TO augur;

--
-- Name: augur_data.repo_insights_ri_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data."augur_data.repo_insights_ri_id_seq"
    START WITH 25430
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data."augur_data.repo_insights_ri_id_seq" OWNER TO augur;

--
-- Name: commit_comment_ref_cmt_comment_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.commit_comment_ref_cmt_comment_id_seq
    START WITH 25430
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.commit_comment_ref_cmt_comment_id_seq OWNER TO augur;

--
-- Name: commit_comment_ref; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.commit_comment_ref (
    cmt_comment_id bigint DEFAULT nextval('augur_data.commit_comment_ref_cmt_comment_id_seq'::regclass) NOT NULL,
    cmt_id bigint NOT NULL,
    repo_id bigint,
    msg_id bigint NOT NULL,
    user_id bigint NOT NULL,
    body text,
    line bigint,
    "position" bigint,
    commit_comment_src_node_id character varying,
    cmt_comment_src_id bigint NOT NULL,
    created_at timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE augur_data.commit_comment_ref OWNER TO augur;

--
-- Name: COLUMN commit_comment_ref.commit_comment_src_node_id; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.commit_comment_ref.commit_comment_src_node_id IS 'For data provenance, we store the source node ID if it exists. ';


--
-- Name: COLUMN commit_comment_ref.cmt_comment_src_id; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.commit_comment_ref.cmt_comment_src_id IS 'For data provenance, we store the source ID if it exists. ';


--
-- Name: contributors; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.contributors (
    cntrb_login character varying,
    cntrb_email character varying,
    cntrb_full_name character varying,
    cntrb_company character varying,
    cntrb_created_at timestamp(0) without time zone,
    cntrb_type character varying,
    cntrb_fake smallint DEFAULT 0,
    cntrb_deleted smallint DEFAULT 0,
    cntrb_long numeric(11,8) DEFAULT NULL::numeric,
    cntrb_lat numeric(10,8) DEFAULT NULL::numeric,
    cntrb_country_code character(3) DEFAULT NULL::bpchar,
    cntrb_state character varying,
    cntrb_city character varying,
    cntrb_location character varying,
    cntrb_canonical character varying,
    cntrb_last_used timestamp(0) with time zone DEFAULT NULL::timestamp with time zone,
    gh_user_id bigint,
    gh_login character varying,
    gh_url character varying,
    gh_html_url character varying,
    gh_node_id character varying,
    gh_avatar_url character varying,
    gh_gravatar_id character varying,
    gh_followers_url character varying,
    gh_following_url character varying,
    gh_gists_url character varying,
    gh_starred_url character varying,
    gh_subscriptions_url character varying,
    gh_organizations_url character varying,
    gh_repos_url character varying,
    gh_events_url character varying,
    gh_received_events_url character varying,
    gh_type character varying,
    gh_site_admin character varying,
    gl_web_url character varying,
    gl_avatar_url character varying,
    gl_state character varying,
    gl_username character varying,
    gl_full_name character varying,
    gl_id bigint,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP,
    cntrb_id uuid NOT NULL
);


ALTER TABLE augur_data.contributors OWNER TO augur;

--
-- Name: TABLE contributors; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON TABLE augur_data.contributors IS 'For GitHub, this should be repeated from gh_login. for other systems, it should be that systems login. 
Github now allows a user to change their login name, but their user id remains the same in this case. So, the natural key is the combination of id and login, but there should never be repeated logins. ';


--
-- Name: COLUMN contributors.cntrb_login; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.contributors.cntrb_login IS 'Will be a double population with the same value as gh_login for github, but the local value for other systems. ';


--
-- Name: COLUMN contributors.cntrb_email; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.contributors.cntrb_email IS 'This needs to be here for matching contributor ids, which are augur, to the commit information. ';


--
-- Name: COLUMN contributors.cntrb_type; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.contributors.cntrb_type IS 'Present in another models. It is not currently used in Augur. ';


--
-- Name: COLUMN contributors.gh_login; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.contributors.gh_login IS 'populated with the github user name for github originated data. ';


--
-- Name: COLUMN contributors.gl_web_url; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.contributors.gl_web_url IS '“web_url” value from these API calls to GitLab, all for the same user

https://gitlab.com/api/v4/users?username=computationalmystic
https://gitlab.com/api/v4/users?search=s@goggins.com
https://gitlab.com/api/v4/users?search=outdoors@acm.org

[
  {
    "id": 5481034,
    "name": "sean goggins",
    "username": "computationalmystic",
    "state": "active",
    "avatar_url": "https://secure.gravatar.com/avatar/fb1fb43953a6059df2fe8d94b21d575c?s=80&d=identicon",
    "web_url": "https://gitlab.com/computationalmystic"
  }
]';


--
-- Name: COLUMN contributors.gl_avatar_url; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.contributors.gl_avatar_url IS '“avatar_url” value from these API calls to GitLab, all for the same user

https://gitlab.com/api/v4/users?username=computationalmystic
https://gitlab.com/api/v4/users?search=s@goggins.com
https://gitlab.com/api/v4/users?search=outdoors@acm.org

[
  {
    "id": 5481034,
    "name": "sean goggins",
    "username": "computationalmystic",
    "state": "active",
    "avatar_url": "https://secure.gravatar.com/avatar/fb1fb43953a6059df2fe8d94b21d575c?s=80&d=identicon",
    "web_url": "https://gitlab.com/computationalmystic"
  }
]';


--
-- Name: COLUMN contributors.gl_state; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.contributors.gl_state IS '“state” value from these API calls to GitLab, all for the same user

https://gitlab.com/api/v4/users?username=computationalmystic
https://gitlab.com/api/v4/users?search=s@goggins.com
https://gitlab.com/api/v4/users?search=outdoors@acm.org

[
  {
    "id": 5481034,
    "name": "sean goggins",
    "username": "computationalmystic",
    "state": "active",
    "avatar_url": "https://secure.gravatar.com/avatar/fb1fb43953a6059df2fe8d94b21d575c?s=80&d=identicon",
    "web_url": "https://gitlab.com/computationalmystic"
  }
]';


--
-- Name: COLUMN contributors.gl_username; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.contributors.gl_username IS '“username” value from these API calls to GitLab, all for the same user

https://gitlab.com/api/v4/users?username=computationalmystic
https://gitlab.com/api/v4/users?search=s@goggins.com
https://gitlab.com/api/v4/users?search=outdoors@acm.org

[
  {
    "id": 5481034,
    "name": "sean goggins",
    "username": "computationalmystic",
    "state": "active",
    "avatar_url": "https://secure.gravatar.com/avatar/fb1fb43953a6059df2fe8d94b21d575c?s=80&d=identicon",
    "web_url": "https://gitlab.com/computationalmystic"
  }
]';


--
-- Name: COLUMN contributors.gl_full_name; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.contributors.gl_full_name IS '“name” value from these API calls to GitLab, all for the same user

https://gitlab.com/api/v4/users?username=computationalmystic
https://gitlab.com/api/v4/users?search=s@goggins.com
https://gitlab.com/api/v4/users?search=outdoors@acm.org

[
  {
    "id": 5481034,
    "name": "sean goggins",
    "username": "computationalmystic",
    "state": "active",
    "avatar_url": "https://secure.gravatar.com/avatar/fb1fb43953a6059df2fe8d94b21d575c?s=80&d=identicon",
    "web_url": "https://gitlab.com/computationalmystic"
  }
]';


--
-- Name: COLUMN contributors.gl_id; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.contributors.gl_id IS '"id" value from these API calls to GitLab, all for the same user

https://gitlab.com/api/v4/users?username=computationalmystic
https://gitlab.com/api/v4/users?search=s@goggins.com
https://gitlab.com/api/v4/users?search=outdoors@acm.org

[
  {
    "id": 5481034,
    "name": "sean goggins",
    "username": "computationalmystic",
    "state": "active",
    "avatar_url": "https://secure.gravatar.com/avatar/fb1fb43953a6059df2fe8d94b21d575c?s=80&d=identicon",
    "web_url": "https://gitlab.com/computationalmystic"
  }
]';


--
-- Name: issue_events_event_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.issue_events_event_id_seq
    START WITH 25430
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.issue_events_event_id_seq OWNER TO augur;

--
-- Name: issue_events; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.issue_events (
    event_id bigint DEFAULT nextval('augur_data.issue_events_event_id_seq'::regclass) NOT NULL,
    issue_id bigint NOT NULL,
    repo_id bigint,
    action character varying NOT NULL,
    action_commit_hash character varying,
    created_at timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    node_id character varying,
    node_url character varying,
    platform_id bigint NOT NULL,
    issue_event_src_id bigint,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP,
    cntrb_id uuid
);


ALTER TABLE augur_data.issue_events OWNER TO augur;

--
-- Name: COLUMN issue_events.node_id; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.issue_events.node_id IS 'This should be renamed to issue_event_src_node_id, as its the varchar identifier in GitHub and likely common in other sources as well. However, since it was created before we came to this naming standard and workers are built around it, we have it simply named as node_id. Anywhere you see node_id in the schema, it comes from GitHubs terminology.';


--
-- Name: COLUMN issue_events.issue_event_src_id; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.issue_events.issue_event_src_id IS 'This ID comes from the source. In the case of GitHub, it is the id that is the first field returned from the issue events API';


--
-- Name: issue_message_ref_issue_msg_ref_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.issue_message_ref_issue_msg_ref_id_seq
    START WITH 25430
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.issue_message_ref_issue_msg_ref_id_seq OWNER TO augur;

--
-- Name: issue_message_ref; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.issue_message_ref (
    issue_msg_ref_id bigint DEFAULT nextval('augur_data.issue_message_ref_issue_msg_ref_id_seq'::regclass) NOT NULL,
    issue_id bigint,
    repo_id bigint,
    msg_id bigint,
    issue_msg_ref_src_node_id character varying,
    issue_msg_ref_src_comment_id bigint,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE augur_data.issue_message_ref OWNER TO augur;

--
-- Name: COLUMN issue_message_ref.issue_msg_ref_src_node_id; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.issue_message_ref.issue_msg_ref_src_node_id IS 'This character based identifier comes from the source. In the case of GitHub, it is the id that is the first field returned from the issue comments API';


--
-- Name: COLUMN issue_message_ref.issue_msg_ref_src_comment_id; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.issue_message_ref.issue_msg_ref_src_comment_id IS 'This ID comes from the source. In the case of GitHub, it is the id that is the first field returned from the issue comments API';


--
-- Name: message_msg_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.message_msg_id_seq
    START WITH 25430
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.message_msg_id_seq OWNER TO augur;

--
-- Name: message; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.message (
    msg_id bigint DEFAULT nextval('augur_data.message_msg_id_seq'::regclass) NOT NULL,
    rgls_id bigint,
    platform_msg_id bigint,
    platform_node_id character varying,
    repo_id bigint,
    msg_text character varying,
    msg_timestamp timestamp(0) without time zone,
    msg_sender_email character varying,
    msg_header character varying,
    pltfrm_id bigint NOT NULL,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP,
    cntrb_id uuid
);


ALTER TABLE augur_data.message OWNER TO augur;

--
-- Name: COLUMN message.cntrb_id; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.message.cntrb_id IS 'Not populated for mailing lists. Populated for GitHub issues. ';


--
-- Name: pull_request_message_ref_pr_msg_ref_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.pull_request_message_ref_pr_msg_ref_id_seq
    START WITH 25430
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.pull_request_message_ref_pr_msg_ref_id_seq OWNER TO augur;

--
-- Name: pull_request_message_ref; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.pull_request_message_ref (
    pr_msg_ref_id bigint DEFAULT nextval('augur_data.pull_request_message_ref_pr_msg_ref_id_seq'::regclass) NOT NULL,
    pull_request_id bigint,
    repo_id bigint,
    msg_id bigint,
    pr_message_ref_src_comment_id bigint,
    pr_message_ref_src_node_id character varying,
    pr_issue_url character varying,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE augur_data.pull_request_message_ref OWNER TO augur;

--
-- Name: repo_repo_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.repo_repo_id_seq
    START WITH 25430
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.repo_repo_id_seq OWNER TO augur;

--
-- Name: repo; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.repo (
    repo_id bigint DEFAULT nextval('augur_data.repo_repo_id_seq'::regclass) NOT NULL,
    repo_group_id bigint NOT NULL,
    repo_git character varying NOT NULL,
    repo_path character varying DEFAULT 'NULL'::character varying,
    repo_name character varying DEFAULT 'NULL'::character varying,
    repo_added timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    repo_type character varying DEFAULT ''::character varying,
    url character varying,
    owner_id integer,
    description character varying,
    primary_language character varying,
    created_at character varying,
    forked_from character varying,
    updated_at timestamp(0) without time zone,
    repo_archived_date_collected timestamp(0) with time zone,
    repo_archived integer,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE augur_data.repo OWNER TO augur;

--
-- Name: TABLE repo; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON TABLE augur_data.repo IS 'This table is a combination of the columns in Facade’s repo table and GHTorrent’s projects table. ';


--
-- Name: COLUMN repo.repo_type; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.repo.repo_type IS 'This field is intended to indicate if the repository is the "main instance" of a repository in cases where implementations choose to add the same repository to more than one repository group. In cases where the repository group is of rg_type Github Organization then this repo_type should be "primary". In other cases the repo_type should probably be "user created". We made this a varchar in order to hold open the possibility that there are additional repo_types we have not thought about. ';


--
-- Name: augur_new_contributors; Type: MATERIALIZED VIEW; Schema: augur_data; Owner: augur
--

CREATE MATERIALIZED VIEW augur_data.augur_new_contributors AS
 SELECT x.cntrb_id,
    x.created_at,
    x.month,
    x.year,
    x.repo_id,
    x.repo_name,
    x.full_name,
    x.login,
    x.rank
   FROM ( SELECT b.cntrb_id,
            b.created_at,
            b.month,
            b.year,
            b.repo_id,
            b.repo_name,
            b.full_name,
            b.login,
            b.action,
            b.rank
           FROM ( SELECT a.id AS cntrb_id,
                    a.created_at,
                    date_part('month'::text, (a.created_at)::date) AS month,
                    date_part('year'::text, (a.created_at)::date) AS year,
                    a.repo_id,
                    repo.repo_name,
                    a.full_name,
                    a.login,
                    a.action,
                    rank() OVER (PARTITION BY a.id ORDER BY a.created_at) AS rank
                   FROM ( SELECT canonical_full_names.canonical_id AS id,
                            issues.created_at,
                            issues.repo_id,
                            'issue_opened'::text AS action,
                            contributors.cntrb_full_name AS full_name,
                            contributors.cntrb_login AS login
                           FROM ((augur_data.issues
                             LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = issues.reporter_id)))
                             LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                    contributors_1.cntrb_canonical AS canonical_email,
                                    contributors_1.data_collection_date,
                                    contributors_1.cntrb_id AS canonical_id
                                   FROM augur_data.contributors contributors_1
                                  WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                  ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                          WHERE (issues.pull_request IS NULL)
                          GROUP BY canonical_full_names.canonical_id, issues.repo_id, issues.created_at, contributors.cntrb_full_name, contributors.cntrb_login
                        UNION ALL
                         SELECT canonical_full_names.canonical_id AS id,
                            to_timestamp((commits.cmt_author_date)::text, 'YYYY-MM-DD'::text) AS created_at,
                            commits.repo_id,
                            'commit'::text AS action,
                            contributors.cntrb_full_name AS full_name,
                            contributors.cntrb_login AS login
                           FROM ((augur_data.commits
                             LEFT JOIN augur_data.contributors ON (((contributors.cntrb_email)::text = (commits.cmt_author_email)::text)))
                             LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                    contributors_1.cntrb_canonical AS canonical_email,
                                    contributors_1.data_collection_date,
                                    contributors_1.cntrb_id AS canonical_id
                                   FROM augur_data.contributors contributors_1
                                  WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                  ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                          GROUP BY commits.repo_id, canonical_full_names.canonical_email, canonical_full_names.canonical_id, commits.cmt_author_date, contributors.cntrb_full_name, contributors.cntrb_login
                        UNION ALL
                         SELECT message.cntrb_id AS id,
                            commit_comment_ref.created_at,
                            commits.repo_id,
                            'commit_comment'::text AS action,
                            contributors.cntrb_full_name AS full_name,
                            contributors.cntrb_login AS login
                           FROM augur_data.commit_comment_ref,
                            augur_data.commits,
                            ((augur_data.message
                             LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = message.cntrb_id)))
                             LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                    contributors_1.cntrb_canonical AS canonical_email,
                                    contributors_1.data_collection_date,
                                    contributors_1.cntrb_id AS canonical_id
                                   FROM augur_data.contributors contributors_1
                                  WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                  ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                          WHERE ((commits.cmt_id = commit_comment_ref.cmt_id) AND (commit_comment_ref.msg_id = message.msg_id))
                          GROUP BY message.cntrb_id, commits.repo_id, commit_comment_ref.created_at, contributors.cntrb_full_name, contributors.cntrb_login
                        UNION ALL
                         SELECT issue_events.cntrb_id AS id,
                            issue_events.created_at,
                            issues.repo_id,
                            'issue_closed'::text AS action,
                            contributors.cntrb_full_name AS full_name,
                            contributors.cntrb_login AS login
                           FROM augur_data.issues,
                            ((augur_data.issue_events
                             LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = issue_events.cntrb_id)))
                             LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                    contributors_1.cntrb_canonical AS canonical_email,
                                    contributors_1.data_collection_date,
                                    contributors_1.cntrb_id AS canonical_id
                                   FROM augur_data.contributors contributors_1
                                  WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                  ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                          WHERE ((issues.issue_id = issue_events.issue_id) AND (issues.pull_request IS NULL) AND (issue_events.cntrb_id IS NOT NULL) AND ((issue_events.action)::text = 'closed'::text))
                          GROUP BY issue_events.cntrb_id, issues.repo_id, issue_events.created_at, contributors.cntrb_full_name, contributors.cntrb_login
                        UNION ALL
                         SELECT pull_requests.pr_augur_contributor_id AS id,
                            pull_requests.pr_created_at AS created_at,
                            pull_requests.repo_id,
                            'open_pull_request'::text AS action,
                            contributors.cntrb_full_name AS full_name,
                            contributors.cntrb_login AS login
                           FROM ((augur_data.pull_requests
                             LEFT JOIN augur_data.contributors ON ((pull_requests.pr_augur_contributor_id = contributors.cntrb_id)))
                             LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                    contributors_1.cntrb_canonical AS canonical_email,
                                    contributors_1.data_collection_date,
                                    contributors_1.cntrb_id AS canonical_id
                                   FROM augur_data.contributors contributors_1
                                  WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                  ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                          GROUP BY pull_requests.pr_augur_contributor_id, pull_requests.repo_id, pull_requests.pr_created_at, contributors.cntrb_full_name, contributors.cntrb_login
                        UNION ALL
                         SELECT message.cntrb_id AS id,
                            message.msg_timestamp AS created_at,
                            pull_requests.repo_id,
                            'pull_request_comment'::text AS action,
                            contributors.cntrb_full_name AS full_name,
                            contributors.cntrb_login AS login
                           FROM augur_data.pull_requests,
                            augur_data.pull_request_message_ref,
                            ((augur_data.message
                             LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = message.cntrb_id)))
                             LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                    contributors_1.cntrb_canonical AS canonical_email,
                                    contributors_1.data_collection_date,
                                    contributors_1.cntrb_id AS canonical_id
                                   FROM augur_data.contributors contributors_1
                                  WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                  ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                          WHERE ((pull_request_message_ref.pull_request_id = pull_requests.pull_request_id) AND (pull_request_message_ref.msg_id = message.msg_id))
                          GROUP BY message.cntrb_id, pull_requests.repo_id, message.msg_timestamp, contributors.cntrb_full_name, contributors.cntrb_login
                        UNION ALL
                         SELECT issues.reporter_id AS id,
                            message.msg_timestamp AS created_at,
                            issues.repo_id,
                            'issue_comment'::text AS action,
                            contributors.cntrb_full_name AS full_name,
                            contributors.cntrb_login AS login
                           FROM augur_data.issues,
                            augur_data.issue_message_ref,
                            ((augur_data.message
                             LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = message.cntrb_id)))
                             LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                    contributors_1.cntrb_canonical AS canonical_email,
                                    contributors_1.data_collection_date,
                                    contributors_1.cntrb_id AS canonical_id
                                   FROM augur_data.contributors contributors_1
                                  WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                  ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                          WHERE ((issue_message_ref.msg_id = message.msg_id) AND (issues.issue_id = issue_message_ref.issue_id) AND (issues.pull_request_id = NULL::bigint))
                          GROUP BY issues.reporter_id, issues.repo_id, message.msg_timestamp, contributors.cntrb_full_name, contributors.cntrb_login) a,
                    augur_data.repo
                  WHERE ((a.id IS NOT NULL) AND (a.repo_id = repo.repo_id))
                  GROUP BY a.id, a.repo_id, a.action, a.created_at, repo.repo_name, a.full_name, a.login
                  ORDER BY a.id) b
          WHERE (b.rank = ANY (ARRAY[(1)::bigint, (2)::bigint, (3)::bigint, (4)::bigint, (5)::bigint, (6)::bigint, (7)::bigint]))) x
  WITH NO DATA;


ALTER TABLE augur_data.augur_new_contributors OWNER TO augur;

--
-- Name: chaoss_metric_status_cms_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.chaoss_metric_status_cms_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.chaoss_metric_status_cms_id_seq OWNER TO augur;

--
-- Name: chaoss_metric_status; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.chaoss_metric_status (
    cms_id bigint DEFAULT nextval('augur_data.chaoss_metric_status_cms_id_seq'::regclass) NOT NULL,
    cm_group character varying,
    cm_source character varying,
    cm_type character varying,
    cm_backend_status character varying,
    cm_frontend_status character varying,
    cm_defined boolean,
    cm_api_endpoint_repo character varying,
    cm_api_endpoint_rg character varying,
    cm_name character varying,
    cm_working_group character varying,
    cm_info json,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP,
    cm_working_group_focus_area character varying
);


ALTER TABLE augur_data.chaoss_metric_status OWNER TO augur;

--
-- Name: TABLE chaoss_metric_status; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON TABLE augur_data.chaoss_metric_status IS 'This table used to track CHAOSS Metric implementations in Augur, but due to the constantly changing location of that information, it is for the moment not actively populated. ';


--
-- Name: chaoss_user; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.chaoss_user (
    chaoss_id bigint NOT NULL,
    chaoss_login_name character varying,
    chaoss_login_hashword character varying,
    chaoss_email character varying,
    chaoss_text_phone character varying,
    chaoss_first_name character varying,
    chaoss_last_name character varying,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(6) with time zone DEFAULT now()
);


ALTER TABLE augur_data.chaoss_user OWNER TO augur;

--
-- Name: chaoss_user_chaoss_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.chaoss_user_chaoss_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.chaoss_user_chaoss_id_seq OWNER TO augur;

--
-- Name: chaoss_user_chaoss_id_seq; Type: SEQUENCE OWNED BY; Schema: augur_data; Owner: augur
--

ALTER SEQUENCE augur_data.chaoss_user_chaoss_id_seq OWNED BY augur_data.chaoss_user.chaoss_id;


--
-- Name: commit_parents_parent_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.commit_parents_parent_id_seq
    START WITH 25430
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.commit_parents_parent_id_seq OWNER TO augur;

--
-- Name: commit_parents; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.commit_parents (
    cmt_id bigint NOT NULL,
    parent_id bigint DEFAULT nextval('augur_data.commit_parents_parent_id_seq'::regclass) NOT NULL,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE augur_data.commit_parents OWNER TO augur;

--
-- Name: contributor_affiliations_ca_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.contributor_affiliations_ca_id_seq
    START WITH 25430
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.contributor_affiliations_ca_id_seq OWNER TO augur;

--
-- Name: contributor_affiliations; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.contributor_affiliations (
    ca_id bigint DEFAULT nextval('augur_data.contributor_affiliations_ca_id_seq'::regclass) NOT NULL,
    ca_domain character varying(64) NOT NULL,
    ca_start_date date DEFAULT '1970-01-01'::date,
    ca_last_used timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    ca_affiliation character varying,
    ca_active smallint DEFAULT 1,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE augur_data.contributor_affiliations OWNER TO augur;

--
-- Name: TABLE contributor_affiliations; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON TABLE augur_data.contributor_affiliations IS 'This table exists outside of relations with other tables. The purpose is to provide a dynamic, owner maintained (and augur augmented) list of affiliations. This table is processed in affiliation information in the DM_ tables generated when Augur is finished counting commits using the Facade Worker. ';


--
-- Name: contributor_repo_cntrb_repo_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.contributor_repo_cntrb_repo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.contributor_repo_cntrb_repo_id_seq OWNER TO augur;

--
-- Name: contributor_repo; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.contributor_repo (
    cntrb_repo_id bigint DEFAULT nextval('augur_data.contributor_repo_cntrb_repo_id_seq'::regclass) NOT NULL,
    repo_git character varying NOT NULL,
    repo_name character varying NOT NULL,
    gh_repo_id bigint NOT NULL,
    cntrb_category character varying,
    event_id bigint,
    created_at timestamp(0) without time zone,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP,
    cntrb_id uuid NOT NULL
);


ALTER TABLE augur_data.contributor_repo OWNER TO augur;

--
-- Name: TABLE contributor_repo; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON TABLE augur_data.contributor_repo IS 'Developed in Partnership with Andrew Brain. 
From: [
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


--
-- Name: COLUMN contributor_repo.repo_git; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.contributor_repo.repo_git IS 'Similar to cntrb_id, we need this data for the table to have meaningful data. ';


--
-- Name: COLUMN contributor_repo.cntrb_id; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.contributor_repo.cntrb_id IS 'This is not null because what is the point without the contributor in this table? ';


--
-- Name: contributors_aliases_cntrb_alias_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.contributors_aliases_cntrb_alias_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.contributors_aliases_cntrb_alias_id_seq OWNER TO augur;

--
-- Name: contributors_aliases; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.contributors_aliases (
    cntrb_alias_id bigint DEFAULT nextval('augur_data.contributors_aliases_cntrb_alias_id_seq'::regclass) NOT NULL,
    canonical_email character varying NOT NULL,
    alias_email character varying NOT NULL,
    cntrb_active smallint DEFAULT 1 NOT NULL,
    cntrb_last_modified timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP,
    cntrb_id uuid NOT NULL
);


ALTER TABLE augur_data.contributors_aliases OWNER TO augur;

--
-- Name: TABLE contributors_aliases; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON TABLE augur_data.contributors_aliases IS 'Every open source user may have more than one email used to make contributions over time. Augur selects the first email it encounters for a user as its “canonical_email”. 

The canonical_email is also added to the contributors_aliases table, with the canonical_email and alias_email being identical.  Using this strategy, an email search will only need to join the alias table for basic email information, and can then more easily map the canonical email from each alias row to the same, more detailed information in the contributors table for a user. ';


--
-- Name: contributors_aliases_cntrb_a_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.contributors_aliases_cntrb_a_id_seq
    START WITH 25430
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.contributors_aliases_cntrb_a_id_seq OWNER TO augur;

--
-- Name: contributors_cntrb_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.contributors_cntrb_id_seq
    START WITH 25430
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.contributors_cntrb_id_seq OWNER TO augur;

--
-- Name: contributors_history_cntrb_history_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.contributors_history_cntrb_history_id_seq
    START WITH 25430
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.contributors_history_cntrb_history_id_seq OWNER TO augur;

--
-- Name: discourse_insights_msg_discourse_id_seq1; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.discourse_insights_msg_discourse_id_seq1
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.discourse_insights_msg_discourse_id_seq1 OWNER TO augur;

--
-- Name: discourse_insights; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.discourse_insights (
    msg_discourse_id bigint DEFAULT nextval('augur_data.discourse_insights_msg_discourse_id_seq1'::regclass) NOT NULL,
    msg_id bigint,
    discourse_act character varying,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(6) with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE augur_data.discourse_insights OWNER TO augur;

--
-- Name: TABLE discourse_insights; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON TABLE augur_data.discourse_insights IS 'This table is populated by the “Discourse_Analysis_Worker”. It examines sequential discourse, using computational linguistic methods, to draw statistical inferences regarding the discourse in a particular comment thread. ';


--
-- Name: discourse_insights_msg_discourse_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.discourse_insights_msg_discourse_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.discourse_insights_msg_discourse_id_seq OWNER TO augur;

--
-- Name: dm_repo_annual; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.dm_repo_annual (
    repo_id bigint NOT NULL,
    email character varying NOT NULL,
    affiliation character varying DEFAULT 'NULL'::character varying,
    year smallint NOT NULL,
    added bigint NOT NULL,
    removed bigint NOT NULL,
    whitespace bigint NOT NULL,
    files bigint NOT NULL,
    patches bigint NOT NULL,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE augur_data.dm_repo_annual OWNER TO augur;

--
-- Name: dm_repo_group_annual; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.dm_repo_group_annual (
    repo_group_id bigint NOT NULL,
    email character varying NOT NULL,
    affiliation character varying DEFAULT 'NULL'::character varying,
    year smallint NOT NULL,
    added bigint NOT NULL,
    removed bigint NOT NULL,
    whitespace bigint NOT NULL,
    files bigint NOT NULL,
    patches bigint NOT NULL,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE augur_data.dm_repo_group_annual OWNER TO augur;

--
-- Name: dm_repo_group_monthly; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.dm_repo_group_monthly (
    repo_group_id bigint NOT NULL,
    email character varying NOT NULL,
    affiliation character varying DEFAULT 'NULL'::character varying,
    month smallint NOT NULL,
    year smallint NOT NULL,
    added bigint NOT NULL,
    removed bigint NOT NULL,
    whitespace bigint NOT NULL,
    files bigint NOT NULL,
    patches bigint NOT NULL,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE augur_data.dm_repo_group_monthly OWNER TO augur;

--
-- Name: dm_repo_group_weekly; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.dm_repo_group_weekly (
    repo_group_id bigint NOT NULL,
    email character varying NOT NULL,
    affiliation character varying DEFAULT 'NULL'::character varying,
    week smallint NOT NULL,
    year smallint NOT NULL,
    added bigint NOT NULL,
    removed bigint NOT NULL,
    whitespace bigint NOT NULL,
    files bigint NOT NULL,
    patches bigint NOT NULL,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE augur_data.dm_repo_group_weekly OWNER TO augur;

--
-- Name: dm_repo_monthly; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.dm_repo_monthly (
    repo_id bigint NOT NULL,
    email character varying NOT NULL,
    affiliation character varying DEFAULT 'NULL'::character varying,
    month smallint NOT NULL,
    year smallint NOT NULL,
    added bigint NOT NULL,
    removed bigint NOT NULL,
    whitespace bigint NOT NULL,
    files bigint NOT NULL,
    patches bigint NOT NULL,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE augur_data.dm_repo_monthly OWNER TO augur;

--
-- Name: dm_repo_weekly; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.dm_repo_weekly (
    repo_id bigint NOT NULL,
    email character varying NOT NULL,
    affiliation character varying DEFAULT 'NULL'::character varying,
    week smallint NOT NULL,
    year smallint NOT NULL,
    added bigint NOT NULL,
    removed bigint NOT NULL,
    whitespace bigint NOT NULL,
    files bigint NOT NULL,
    patches bigint NOT NULL,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE augur_data.dm_repo_weekly OWNER TO augur;

--
-- Name: exclude; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.exclude (
    id integer NOT NULL,
    projects_id integer NOT NULL,
    email character varying DEFAULT 'NULL'::character varying,
    domain character varying DEFAULT 'NULL'::character varying
);


ALTER TABLE augur_data.exclude OWNER TO augur;

--
-- Name: explorer_commits_and_committers_daily_count; Type: MATERIALIZED VIEW; Schema: augur_data; Owner: augur
--

CREATE MATERIALIZED VIEW augur_data.explorer_commits_and_committers_daily_count AS
 SELECT repo.repo_id,
    repo.repo_name,
    commits.cmt_committer_date,
    count(commits.cmt_id) AS num_of_commits,
    count(DISTINCT commits.cmt_committer_raw_email) AS num_of_unique_committers
   FROM (augur_data.commits
     LEFT JOIN augur_data.repo ON ((repo.repo_id = commits.repo_id)))
  GROUP BY repo.repo_id, repo.repo_name, commits.cmt_committer_date
  ORDER BY repo.repo_id, commits.cmt_committer_date
  WITH NO DATA;


ALTER TABLE augur_data.explorer_commits_and_committers_daily_count OWNER TO augur;

--
-- Name: explorer_contributor_actions; Type: MATERIALIZED VIEW; Schema: augur_data; Owner: augur
--

CREATE MATERIALIZED VIEW augur_data.explorer_contributor_actions AS
 SELECT x.cntrb_id,
    x.created_at,
    x.repo_id,
    x.login,
    x.action,
    x.rank
   FROM ( SELECT b.cntrb_id,
            b.created_at,
            b.month,
            b.year,
            b.repo_id,
            b.repo_name,
            b.full_name,
            b.login,
            b.action,
            b.rank
           FROM ( SELECT a.id AS cntrb_id,
                    a.created_at,
                    date_part('month'::text, (a.created_at)::date) AS month,
                    date_part('year'::text, (a.created_at)::date) AS year,
                    a.repo_id,
                    repo.repo_name,
                    a.full_name,
                    a.login,
                    a.action,
                    rank() OVER (PARTITION BY a.id, a.repo_id ORDER BY a.created_at) AS rank
                   FROM ( SELECT canonical_full_names.canonical_id AS id,
                            issues.created_at,
                            issues.repo_id,
                            'issue_opened'::text AS action,
                            contributors.cntrb_full_name AS full_name,
                            contributors.cntrb_login AS login
                           FROM ((augur_data.issues
                             LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = issues.reporter_id)))
                             LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                    contributors_1.cntrb_canonical AS canonical_email,
                                    contributors_1.data_collection_date,
                                    contributors_1.cntrb_id AS canonical_id
                                   FROM augur_data.contributors contributors_1
                                  WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                  ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                          WHERE (issues.pull_request IS NULL)
                          GROUP BY canonical_full_names.canonical_id, issues.repo_id, issues.created_at, contributors.cntrb_full_name, contributors.cntrb_login
                        UNION ALL
                         SELECT canonical_full_names.canonical_id AS id,
                            to_timestamp((commits.cmt_author_date)::text, 'YYYY-MM-DD'::text) AS created_at,
                            commits.repo_id,
                            'commit'::text AS action,
                            contributors.cntrb_full_name AS full_name,
                            contributors.cntrb_login AS login
                           FROM ((augur_data.commits
                             LEFT JOIN augur_data.contributors ON (((contributors.cntrb_canonical)::text = (commits.cmt_author_email)::text)))
                             LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                    contributors_1.cntrb_canonical AS canonical_email,
                                    contributors_1.data_collection_date,
                                    contributors_1.cntrb_id AS canonical_id
                                   FROM augur_data.contributors contributors_1
                                  WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_canonical)::text)
                                  ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                          GROUP BY commits.repo_id, canonical_full_names.canonical_email, canonical_full_names.canonical_id, commits.cmt_author_date, contributors.cntrb_full_name, contributors.cntrb_login
                        UNION ALL
                         SELECT message.cntrb_id AS id,
                            commit_comment_ref.created_at,
                            commits.repo_id,
                            'commit_comment'::text AS action,
                            contributors.cntrb_full_name AS full_name,
                            contributors.cntrb_login AS login
                           FROM augur_data.commit_comment_ref,
                            augur_data.commits,
                            ((augur_data.message
                             LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = message.cntrb_id)))
                             LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                    contributors_1.cntrb_canonical AS canonical_email,
                                    contributors_1.data_collection_date,
                                    contributors_1.cntrb_id AS canonical_id
                                   FROM augur_data.contributors contributors_1
                                  WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                  ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                          WHERE ((commits.cmt_id = commit_comment_ref.cmt_id) AND (commit_comment_ref.msg_id = message.msg_id))
                          GROUP BY message.cntrb_id, commits.repo_id, commit_comment_ref.created_at, contributors.cntrb_full_name, contributors.cntrb_login
                        UNION ALL
                         SELECT issue_events.cntrb_id AS id,
                            issue_events.created_at,
                            issues.repo_id,
                            'issue_closed'::text AS action,
                            contributors.cntrb_full_name AS full_name,
                            contributors.cntrb_login AS login
                           FROM augur_data.issues,
                            ((augur_data.issue_events
                             LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = issue_events.cntrb_id)))
                             LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                    contributors_1.cntrb_canonical AS canonical_email,
                                    contributors_1.data_collection_date,
                                    contributors_1.cntrb_id AS canonical_id
                                   FROM augur_data.contributors contributors_1
                                  WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                  ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                          WHERE ((issues.issue_id = issue_events.issue_id) AND (issues.pull_request IS NULL) AND (issue_events.cntrb_id IS NOT NULL) AND ((issue_events.action)::text = 'closed'::text))
                          GROUP BY issue_events.cntrb_id, issues.repo_id, issue_events.created_at, contributors.cntrb_full_name, contributors.cntrb_login
                        UNION ALL
                         SELECT pull_requests.pr_augur_contributor_id AS id,
                            pull_requests.pr_created_at AS created_at,
                            pull_requests.repo_id,
                            'open_pull_request'::text AS action,
                            contributors.cntrb_full_name AS full_name,
                            contributors.cntrb_login AS login
                           FROM ((augur_data.pull_requests
                             LEFT JOIN augur_data.contributors ON ((pull_requests.pr_augur_contributor_id = contributors.cntrb_id)))
                             LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                    contributors_1.cntrb_canonical AS canonical_email,
                                    contributors_1.data_collection_date,
                                    contributors_1.cntrb_id AS canonical_id
                                   FROM augur_data.contributors contributors_1
                                  WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                  ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                          GROUP BY pull_requests.pr_augur_contributor_id, pull_requests.repo_id, pull_requests.pr_created_at, contributors.cntrb_full_name, contributors.cntrb_login
                        UNION ALL
                         SELECT message.cntrb_id AS id,
                            message.msg_timestamp AS created_at,
                            pull_requests.repo_id,
                            'pull_request_comment'::text AS action,
                            contributors.cntrb_full_name AS full_name,
                            contributors.cntrb_login AS login
                           FROM augur_data.pull_requests,
                            augur_data.pull_request_message_ref,
                            ((augur_data.message
                             LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = message.cntrb_id)))
                             LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                    contributors_1.cntrb_canonical AS canonical_email,
                                    contributors_1.data_collection_date,
                                    contributors_1.cntrb_id AS canonical_id
                                   FROM augur_data.contributors contributors_1
                                  WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                  ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                          WHERE ((pull_request_message_ref.pull_request_id = pull_requests.pull_request_id) AND (pull_request_message_ref.msg_id = message.msg_id))
                          GROUP BY message.cntrb_id, pull_requests.repo_id, message.msg_timestamp, contributors.cntrb_full_name, contributors.cntrb_login
                        UNION ALL
                         SELECT issues.reporter_id AS id,
                            message.msg_timestamp AS created_at,
                            issues.repo_id,
                            'issue_comment'::text AS action,
                            contributors.cntrb_full_name AS full_name,
                            contributors.cntrb_login AS login
                           FROM augur_data.issues,
                            augur_data.issue_message_ref,
                            ((augur_data.message
                             LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = message.cntrb_id)))
                             LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                    contributors_1.cntrb_canonical AS canonical_email,
                                    contributors_1.data_collection_date,
                                    contributors_1.cntrb_id AS canonical_id
                                   FROM augur_data.contributors contributors_1
                                  WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                  ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                          WHERE ((issue_message_ref.msg_id = message.msg_id) AND (issues.issue_id = issue_message_ref.issue_id) AND (issues.pull_request_id = NULL::bigint))
                          GROUP BY issues.reporter_id, issues.repo_id, message.msg_timestamp, contributors.cntrb_full_name, contributors.cntrb_login) a,
                    augur_data.repo
                  WHERE ((a.id IS NOT NULL) AND (a.repo_id = repo.repo_id))
                  GROUP BY a.id, a.repo_id, a.action, a.created_at, repo.repo_name, a.full_name, a.login
                  ORDER BY a.created_at DESC) b) x
  ORDER BY x.created_at DESC
  WITH NO DATA;


ALTER TABLE augur_data.explorer_contributor_actions OWNER TO augur;

--
-- Name: repo_groups_repo_group_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.repo_groups_repo_group_id_seq
    START WITH 25430
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.repo_groups_repo_group_id_seq OWNER TO augur;

--
-- Name: repo_groups; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.repo_groups (
    repo_group_id bigint DEFAULT nextval('augur_data.repo_groups_repo_group_id_seq'::regclass) NOT NULL,
    rg_name character varying NOT NULL,
    rg_description character varying DEFAULT 'NULL'::character varying,
    rg_website character varying(128) DEFAULT 'NULL'::character varying,
    rg_recache smallint DEFAULT 1,
    rg_last_modified timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    rg_type character varying,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone
);


ALTER TABLE augur_data.repo_groups OWNER TO augur;

--
-- Name: TABLE repo_groups; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON TABLE augur_data.repo_groups IS 'rg_type is intended to be either a GitHub Organization or a User Created Repo Group. ';


--
-- Name: explorer_entry_list; Type: MATERIALIZED VIEW; Schema: augur_data; Owner: augur
--

CREATE MATERIALIZED VIEW augur_data.explorer_entry_list AS
 SELECT DISTINCT r.repo_git,
    r.repo_id,
    r.repo_name,
    rg.rg_name
   FROM (augur_data.repo r
     JOIN augur_data.repo_groups rg ON ((rg.repo_group_id = r.repo_group_id)))
  ORDER BY rg.rg_name
  WITH NO DATA;


ALTER TABLE augur_data.explorer_entry_list OWNER TO augur;

--
-- Name: repo_deps_libyear_repo_deps_libyear_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.repo_deps_libyear_repo_deps_libyear_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.repo_deps_libyear_repo_deps_libyear_id_seq OWNER TO augur;

--
-- Name: repo_deps_libyear; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.repo_deps_libyear (
    repo_deps_libyear_id bigint DEFAULT nextval('augur_data.repo_deps_libyear_repo_deps_libyear_id_seq'::regclass) NOT NULL,
    repo_id bigint,
    name character varying,
    requirement character varying,
    type character varying,
    package_manager character varying,
    current_verion character varying,
    latest_version character varying,
    current_release_date character varying,
    latest_release_date character varying,
    libyear double precision,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE augur_data.repo_deps_libyear OWNER TO augur;

--
-- Name: explorer_libyear_all; Type: MATERIALIZED VIEW; Schema: augur_data; Owner: augur
--

CREATE MATERIALIZED VIEW augur_data.explorer_libyear_all AS
 SELECT a.repo_id,
    a.repo_name,
    avg(b.libyear) AS avg_libyear,
    date_part('month'::text, (a.data_collection_date)::date) AS month,
    date_part('year'::text, (a.data_collection_date)::date) AS year
   FROM augur_data.repo a,
    augur_data.repo_deps_libyear b
  GROUP BY a.repo_id, a.repo_name, (date_part('month'::text, (a.data_collection_date)::date)), (date_part('year'::text, (a.data_collection_date)::date))
  ORDER BY (date_part('year'::text, (a.data_collection_date)::date)) DESC, (date_part('month'::text, (a.data_collection_date)::date)) DESC, (avg(b.libyear)) DESC
  WITH NO DATA;


ALTER TABLE augur_data.explorer_libyear_all OWNER TO augur;

--
-- Name: explorer_libyear_detail; Type: MATERIALIZED VIEW; Schema: augur_data; Owner: augur
--

CREATE MATERIALIZED VIEW augur_data.explorer_libyear_detail AS
 SELECT a.repo_id,
    a.repo_name,
    b.name,
    b.requirement,
    b.current_verion,
    b.latest_version,
    b.current_release_date,
    b.libyear,
    max(b.data_collection_date) AS max
   FROM augur_data.repo a,
    augur_data.repo_deps_libyear b
  GROUP BY a.repo_id, a.repo_name, b.name, b.requirement, b.current_verion, b.latest_version, b.current_release_date, b.libyear
  ORDER BY a.repo_id, b.requirement
  WITH NO DATA;


ALTER TABLE augur_data.explorer_libyear_detail OWNER TO augur;

--
-- Name: explorer_libyear_summary; Type: MATERIALIZED VIEW; Schema: augur_data; Owner: augur
--

CREATE MATERIALIZED VIEW augur_data.explorer_libyear_summary AS
 SELECT a.repo_id,
    a.repo_name,
    avg(b.libyear) AS avg_libyear,
    date_part('month'::text, (a.data_collection_date)::date) AS month,
    date_part('year'::text, (a.data_collection_date)::date) AS year
   FROM augur_data.repo a,
    augur_data.repo_deps_libyear b
  GROUP BY a.repo_id, a.repo_name, (date_part('month'::text, (a.data_collection_date)::date)), (date_part('year'::text, (a.data_collection_date)::date))
  ORDER BY (date_part('year'::text, (a.data_collection_date)::date)) DESC, (date_part('month'::text, (a.data_collection_date)::date)) DESC, (avg(b.libyear)) DESC
  WITH NO DATA;


ALTER TABLE augur_data.explorer_libyear_summary OWNER TO augur;

--
-- Name: explorer_new_contributors; Type: MATERIALIZED VIEW; Schema: augur_data; Owner: augur
--

CREATE MATERIALIZED VIEW augur_data.explorer_new_contributors AS
 SELECT x.cntrb_id,
    x.created_at,
    x.month,
    x.year,
    x.repo_id,
    x.repo_name,
    x.full_name,
    x.login,
    x.rank
   FROM ( SELECT b.cntrb_id,
            b.created_at,
            b.month,
            b.year,
            b.repo_id,
            b.repo_name,
            b.full_name,
            b.login,
            b.action,
            b.rank
           FROM ( SELECT a.id AS cntrb_id,
                    a.created_at,
                    date_part('month'::text, (a.created_at)::date) AS month,
                    date_part('year'::text, (a.created_at)::date) AS year,
                    a.repo_id,
                    repo.repo_name,
                    a.full_name,
                    a.login,
                    a.action,
                    rank() OVER (PARTITION BY a.id ORDER BY a.created_at) AS rank
                   FROM ( SELECT canonical_full_names.canonical_id AS id,
                            issues.created_at,
                            issues.repo_id,
                            'issue_opened'::text AS action,
                            contributors.cntrb_full_name AS full_name,
                            contributors.cntrb_login AS login
                           FROM ((augur_data.issues
                             LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = issues.reporter_id)))
                             LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                    contributors_1.cntrb_canonical AS canonical_email,
                                    contributors_1.data_collection_date,
                                    contributors_1.cntrb_id AS canonical_id
                                   FROM augur_data.contributors contributors_1
                                  WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                  ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                          WHERE (issues.pull_request IS NULL)
                          GROUP BY canonical_full_names.canonical_id, issues.repo_id, issues.created_at, contributors.cntrb_full_name, contributors.cntrb_login
                        UNION ALL
                         SELECT canonical_full_names.canonical_id AS id,
                            to_timestamp((commits.cmt_author_date)::text, 'YYYY-MM-DD'::text) AS created_at,
                            commits.repo_id,
                            'commit'::text AS action,
                            contributors.cntrb_full_name AS full_name,
                            contributors.cntrb_login AS login
                           FROM ((augur_data.commits
                             LEFT JOIN augur_data.contributors ON (((contributors.cntrb_canonical)::text = (commits.cmt_author_email)::text)))
                             LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                    contributors_1.cntrb_canonical AS canonical_email,
                                    contributors_1.data_collection_date,
                                    contributors_1.cntrb_id AS canonical_id
                                   FROM augur_data.contributors contributors_1
                                  WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                  ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                          GROUP BY commits.repo_id, canonical_full_names.canonical_email, canonical_full_names.canonical_id, commits.cmt_author_date, contributors.cntrb_full_name, contributors.cntrb_login
                        UNION ALL
                         SELECT message.cntrb_id AS id,
                            commit_comment_ref.created_at,
                            commits.repo_id,
                            'commit_comment'::text AS action,
                            contributors.cntrb_full_name AS full_name,
                            contributors.cntrb_login AS login
                           FROM augur_data.commit_comment_ref,
                            augur_data.commits,
                            ((augur_data.message
                             LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = message.cntrb_id)))
                             LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                    contributors_1.cntrb_canonical AS canonical_email,
                                    contributors_1.data_collection_date,
                                    contributors_1.cntrb_id AS canonical_id
                                   FROM augur_data.contributors contributors_1
                                  WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                  ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                          WHERE ((commits.cmt_id = commit_comment_ref.cmt_id) AND (commit_comment_ref.msg_id = message.msg_id))
                          GROUP BY message.cntrb_id, commits.repo_id, commit_comment_ref.created_at, contributors.cntrb_full_name, contributors.cntrb_login
                        UNION ALL
                         SELECT issue_events.cntrb_id AS id,
                            issue_events.created_at,
                            issues.repo_id,
                            'issue_closed'::text AS action,
                            contributors.cntrb_full_name AS full_name,
                            contributors.cntrb_login AS login
                           FROM augur_data.issues,
                            ((augur_data.issue_events
                             LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = issue_events.cntrb_id)))
                             LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                    contributors_1.cntrb_canonical AS canonical_email,
                                    contributors_1.data_collection_date,
                                    contributors_1.cntrb_id AS canonical_id
                                   FROM augur_data.contributors contributors_1
                                  WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                  ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                          WHERE ((issues.issue_id = issue_events.issue_id) AND (issues.pull_request IS NULL) AND (issue_events.cntrb_id IS NOT NULL) AND ((issue_events.action)::text = 'closed'::text))
                          GROUP BY issue_events.cntrb_id, issues.repo_id, issue_events.created_at, contributors.cntrb_full_name, contributors.cntrb_login
                        UNION ALL
                         SELECT pull_requests.pr_augur_contributor_id AS id,
                            pull_requests.pr_created_at AS created_at,
                            pull_requests.repo_id,
                            'open_pull_request'::text AS action,
                            contributors.cntrb_full_name AS full_name,
                            contributors.cntrb_login AS login
                           FROM ((augur_data.pull_requests
                             LEFT JOIN augur_data.contributors ON ((pull_requests.pr_augur_contributor_id = contributors.cntrb_id)))
                             LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                    contributors_1.cntrb_canonical AS canonical_email,
                                    contributors_1.data_collection_date,
                                    contributors_1.cntrb_id AS canonical_id
                                   FROM augur_data.contributors contributors_1
                                  WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                  ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                          GROUP BY pull_requests.pr_augur_contributor_id, pull_requests.repo_id, pull_requests.pr_created_at, contributors.cntrb_full_name, contributors.cntrb_login
                        UNION ALL
                         SELECT message.cntrb_id AS id,
                            message.msg_timestamp AS created_at,
                            pull_requests.repo_id,
                            'pull_request_comment'::text AS action,
                            contributors.cntrb_full_name AS full_name,
                            contributors.cntrb_login AS login
                           FROM augur_data.pull_requests,
                            augur_data.pull_request_message_ref,
                            ((augur_data.message
                             LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = message.cntrb_id)))
                             LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                    contributors_1.cntrb_canonical AS canonical_email,
                                    contributors_1.data_collection_date,
                                    contributors_1.cntrb_id AS canonical_id
                                   FROM augur_data.contributors contributors_1
                                  WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                  ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                          WHERE ((pull_request_message_ref.pull_request_id = pull_requests.pull_request_id) AND (pull_request_message_ref.msg_id = message.msg_id))
                          GROUP BY message.cntrb_id, pull_requests.repo_id, message.msg_timestamp, contributors.cntrb_full_name, contributors.cntrb_login
                        UNION ALL
                         SELECT issues.reporter_id AS id,
                            message.msg_timestamp AS created_at,
                            issues.repo_id,
                            'issue_comment'::text AS action,
                            contributors.cntrb_full_name AS full_name,
                            contributors.cntrb_login AS login
                           FROM augur_data.issues,
                            augur_data.issue_message_ref,
                            ((augur_data.message
                             LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = message.cntrb_id)))
                             LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                    contributors_1.cntrb_canonical AS canonical_email,
                                    contributors_1.data_collection_date,
                                    contributors_1.cntrb_id AS canonical_id
                                   FROM augur_data.contributors contributors_1
                                  WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                  ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                          WHERE ((issue_message_ref.msg_id = message.msg_id) AND (issues.issue_id = issue_message_ref.issue_id) AND (issues.pull_request_id = NULL::bigint))
                          GROUP BY issues.reporter_id, issues.repo_id, message.msg_timestamp, contributors.cntrb_full_name, contributors.cntrb_login) a,
                    augur_data.repo
                  WHERE ((a.id IS NOT NULL) AND (a.repo_id = repo.repo_id))
                  GROUP BY a.id, a.repo_id, a.action, a.created_at, repo.repo_name, a.full_name, a.login
                  ORDER BY a.id) b
          WHERE (b.rank = ANY (ARRAY[(1)::bigint, (2)::bigint, (3)::bigint, (4)::bigint, (5)::bigint, (6)::bigint, (7)::bigint]))) x
  WITH NO DATA;


ALTER TABLE augur_data.explorer_new_contributors OWNER TO augur;

--
-- Name: issue_assignees_issue_assignee_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.issue_assignees_issue_assignee_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.issue_assignees_issue_assignee_id_seq OWNER TO augur;

--
-- Name: issue_assignees; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.issue_assignees (
    issue_assignee_id bigint DEFAULT nextval('augur_data.issue_assignees_issue_assignee_id_seq'::regclass) NOT NULL,
    issue_id bigint,
    repo_id bigint,
    issue_assignee_src_id bigint,
    issue_assignee_src_node character varying,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP,
    cntrb_id uuid
);


ALTER TABLE augur_data.issue_assignees OWNER TO augur;

--
-- Name: COLUMN issue_assignees.issue_assignee_src_id; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.issue_assignees.issue_assignee_src_id IS 'This ID comes from the source. In the case of GitHub, it is the id that is the first field returned from the issue events API in the issue_assignees embedded JSON object. We may discover it is an ID for the person themselves; but my hypothesis is that its not.';


--
-- Name: COLUMN issue_assignees.issue_assignee_src_node; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.issue_assignees.issue_assignee_src_node IS 'This character based identifier comes from the source. In the case of GitHub, it is the id that is the second field returned from the issue events API in the issue_assignees embedded JSON object. We may discover it is an ID for the person themselves; but my hypothesis is that its not.';


--
-- Name: issue_labels_issue_label_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.issue_labels_issue_label_id_seq
    START WITH 25430
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.issue_labels_issue_label_id_seq OWNER TO augur;

--
-- Name: issue_labels; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.issue_labels (
    issue_label_id bigint DEFAULT nextval('augur_data.issue_labels_issue_label_id_seq'::regclass) NOT NULL,
    issue_id bigint,
    repo_id bigint,
    label_text character varying,
    label_description character varying,
    label_color character varying,
    label_src_id bigint,
    label_src_node_id character varying,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE augur_data.issue_labels OWNER TO augur;

--
-- Name: COLUMN issue_labels.label_src_id; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.issue_labels.label_src_id IS 'This character based identifier (node) comes from the source. In the case of GitHub, it is the id that is the second field returned from the issue events API JSON subsection for issues.';


--
-- Name: libraries_library_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.libraries_library_id_seq
    START WITH 25430
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.libraries_library_id_seq OWNER TO augur;

--
-- Name: libraries; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.libraries (
    library_id bigint DEFAULT nextval('augur_data.libraries_library_id_seq'::regclass) NOT NULL,
    repo_id bigint,
    platform character varying,
    name character varying,
    created_timestamp timestamp(0) without time zone DEFAULT NULL::timestamp without time zone,
    updated_timestamp timestamp(0) without time zone DEFAULT NULL::timestamp without time zone,
    library_description character varying(2000) DEFAULT NULL::character varying,
    keywords character varying,
    library_homepage character varying(1000) DEFAULT NULL::character varying,
    license character varying,
    version_count integer,
    latest_release_timestamp character varying,
    latest_release_number character varying,
    package_manager_id character varying,
    dependency_count integer,
    dependent_library_count integer,
    primary_language character varying,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone
);


ALTER TABLE augur_data.libraries OWNER TO augur;

--
-- Name: library_dependencies_lib_dependency_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.library_dependencies_lib_dependency_id_seq
    START WITH 25430
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.library_dependencies_lib_dependency_id_seq OWNER TO augur;

--
-- Name: library_dependencies; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.library_dependencies (
    lib_dependency_id bigint DEFAULT nextval('augur_data.library_dependencies_lib_dependency_id_seq'::regclass) NOT NULL,
    library_id bigint,
    manifest_platform character varying,
    manifest_filepath character varying(1000) DEFAULT NULL::character varying,
    manifest_kind character varying,
    repo_id_branch character varying NOT NULL,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone
);


ALTER TABLE augur_data.library_dependencies OWNER TO augur;

--
-- Name: library_version_library_version_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.library_version_library_version_id_seq
    START WITH 25430
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.library_version_library_version_id_seq OWNER TO augur;

--
-- Name: library_version; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.library_version (
    library_version_id bigint DEFAULT nextval('augur_data.library_version_library_version_id_seq'::regclass) NOT NULL,
    library_id bigint,
    library_platform character varying,
    version_number character varying,
    version_release_date timestamp(0) without time zone DEFAULT NULL::timestamp without time zone,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone
);


ALTER TABLE augur_data.library_version OWNER TO augur;

--
-- Name: lstm_anomaly_models_model_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.lstm_anomaly_models_model_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.lstm_anomaly_models_model_id_seq OWNER TO augur;

--
-- Name: lstm_anomaly_models; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.lstm_anomaly_models (
    model_id bigint DEFAULT nextval('augur_data.lstm_anomaly_models_model_id_seq'::regclass) NOT NULL,
    model_name character varying,
    model_description character varying,
    look_back_days bigint,
    training_days bigint,
    batch_size bigint,
    metric character varying,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(6) without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE augur_data.lstm_anomaly_models OWNER TO augur;

--
-- Name: lstm_anomaly_results_result_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.lstm_anomaly_results_result_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.lstm_anomaly_results_result_id_seq OWNER TO augur;

--
-- Name: lstm_anomaly_results; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.lstm_anomaly_results (
    result_id bigint DEFAULT nextval('augur_data.lstm_anomaly_results_result_id_seq'::regclass) NOT NULL,
    repo_id bigint,
    repo_category character varying,
    model_id bigint,
    metric character varying,
    contamination_factor double precision,
    mean_absolute_error double precision,
    remarks character varying,
    metric_field character varying,
    mean_absolute_actual_value double precision,
    mean_absolute_prediction_value double precision,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(6) without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE augur_data.lstm_anomaly_results OWNER TO augur;

--
-- Name: COLUMN lstm_anomaly_results.metric_field; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.lstm_anomaly_results.metric_field IS 'This is a listing of all of the endpoint fields included in the generation of the metric. Sometimes there is one, sometimes there is more than one. This will list them all. ';


--
-- Name: message_analysis_msg_analysis_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.message_analysis_msg_analysis_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.message_analysis_msg_analysis_id_seq OWNER TO augur;

--
-- Name: message_analysis; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.message_analysis (
    msg_analysis_id bigint DEFAULT nextval('augur_data.message_analysis_msg_analysis_id_seq'::regclass) NOT NULL,
    msg_id bigint,
    worker_run_id bigint,
    sentiment_score double precision,
    reconstruction_error double precision,
    novelty_flag boolean,
    feedback_flag boolean,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE augur_data.message_analysis OWNER TO augur;

--
-- Name: COLUMN message_analysis.worker_run_id; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.message_analysis.worker_run_id IS 'This column is used to indicate analyses run by a worker during the same execution period, and is useful for grouping, and time series analysis.  ';


--
-- Name: COLUMN message_analysis.sentiment_score; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.message_analysis.sentiment_score IS 'A sentiment analysis score. Zero is neutral, negative numbers are negative sentiment, and positive numbers are positive sentiment. ';


--
-- Name: COLUMN message_analysis.reconstruction_error; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.message_analysis.reconstruction_error IS 'Each message is converted to a 250 dimensin doc2vec vector, so the reconstruction error is the difference between what the predicted vector and the actual vector.';


--
-- Name: COLUMN message_analysis.novelty_flag; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.message_analysis.novelty_flag IS 'This is an analysis of the degree to which the message is novel when compared to other messages in a repository.  For example when bots are producing numerous identical messages, the novelty score is low. It would also be a low novelty score when several people are making the same coment. ';


--
-- Name: COLUMN message_analysis.feedback_flag; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.message_analysis.feedback_flag IS 'This exists to provide the user with an opportunity provide feedback on the resulting the sentiment scores. ';


--
-- Name: message_analysis_summary_msg_summary_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.message_analysis_summary_msg_summary_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.message_analysis_summary_msg_summary_id_seq OWNER TO augur;

--
-- Name: message_analysis_summary; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.message_analysis_summary (
    msg_summary_id bigint DEFAULT nextval('augur_data.message_analysis_summary_msg_summary_id_seq'::regclass) NOT NULL,
    repo_id bigint,
    worker_run_id bigint,
    positive_ratio double precision,
    negative_ratio double precision,
    novel_count bigint,
    period timestamp(0) without time zone,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE augur_data.message_analysis_summary OWNER TO augur;

--
-- Name: TABLE message_analysis_summary; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON TABLE augur_data.message_analysis_summary IS 'In a relationally perfect world, we would have a table called “message_analysis_run” the incremented the “worker_run_id” for both message_analysis and message_analysis_summary. For now, we decided this was overkill. ';


--
-- Name: COLUMN message_analysis_summary.worker_run_id; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.message_analysis_summary.worker_run_id IS 'This value should reflect the worker_run_id for the messages summarized in the table. There is not a relation between these two tables for that purpose because its not *really*, relationaly a concept unless we create a third table for "worker_run_id", which we determined was unnecessarily complex. ';


--
-- Name: COLUMN message_analysis_summary.novel_count; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.message_analysis_summary.novel_count IS 'The number of messages identified as novel during the analyzed period';


--
-- Name: COLUMN message_analysis_summary.period; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.message_analysis_summary.period IS 'The whole timeline is divided into periods based on the definition of time period for analysis, which is user specified. Timestamp of the first period to look at, until the end of messages at the data of execution. ';


--
-- Name: message_sentiment_msg_analysis_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.message_sentiment_msg_analysis_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.message_sentiment_msg_analysis_id_seq OWNER TO augur;

--
-- Name: message_sentiment; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.message_sentiment (
    msg_analysis_id bigint DEFAULT nextval('augur_data.message_sentiment_msg_analysis_id_seq'::regclass) NOT NULL,
    msg_id bigint,
    worker_run_id bigint,
    sentiment_score double precision,
    reconstruction_error double precision,
    novelty_flag boolean,
    feedback_flag boolean,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE augur_data.message_sentiment OWNER TO augur;

--
-- Name: COLUMN message_sentiment.worker_run_id; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.message_sentiment.worker_run_id IS 'This column is used to indicate analyses run by a worker during the same execution period, and is useful for grouping, and time series analysis.  ';


--
-- Name: COLUMN message_sentiment.sentiment_score; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.message_sentiment.sentiment_score IS 'A sentiment analysis score. Zero is neutral, negative numbers are negative sentiment, and positive numbers are positive sentiment. ';


--
-- Name: COLUMN message_sentiment.reconstruction_error; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.message_sentiment.reconstruction_error IS 'Each message is converted to a 250 dimensin doc2vec vector, so the reconstruction error is the difference between what the predicted vector and the actual vector.';


--
-- Name: COLUMN message_sentiment.novelty_flag; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.message_sentiment.novelty_flag IS 'This is an analysis of the degree to which the message is novel when compared to other messages in a repository.  For example when bots are producing numerous identical messages, the novelty score is low. It would also be a low novelty score when several people are making the same coment. ';


--
-- Name: COLUMN message_sentiment.feedback_flag; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.message_sentiment.feedback_flag IS 'This exists to provide the user with an opportunity provide feedback on the resulting the sentiment scores. ';


--
-- Name: message_sentiment_summary_msg_summary_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.message_sentiment_summary_msg_summary_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.message_sentiment_summary_msg_summary_id_seq OWNER TO augur;

--
-- Name: message_sentiment_summary; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.message_sentiment_summary (
    msg_summary_id bigint DEFAULT nextval('augur_data.message_sentiment_summary_msg_summary_id_seq'::regclass) NOT NULL,
    repo_id bigint,
    worker_run_id bigint,
    positive_ratio double precision,
    negative_ratio double precision,
    novel_count bigint,
    period timestamp(0) without time zone,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE augur_data.message_sentiment_summary OWNER TO augur;

--
-- Name: TABLE message_sentiment_summary; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON TABLE augur_data.message_sentiment_summary IS 'In a relationally perfect world, we would have a table called “message_sentiment_run” the incremented the “worker_run_id” for both message_sentiment and message_sentiment_summary. For now, we decided this was overkill. ';


--
-- Name: COLUMN message_sentiment_summary.worker_run_id; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.message_sentiment_summary.worker_run_id IS 'This value should reflect the worker_run_id for the messages summarized in the table. There is not a relation between these two tables for that purpose because its not *really*, relationaly a concept unless we create a third table for "worker_run_id", which we determined was unnecessarily complex. ';


--
-- Name: COLUMN message_sentiment_summary.novel_count; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.message_sentiment_summary.novel_count IS 'The number of messages identified as novel during the analyzed period';


--
-- Name: COLUMN message_sentiment_summary.period; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.message_sentiment_summary.period IS 'The whole timeline is divided into periods based on the definition of time period for analysis, which is user specified. Timestamp of the first period to look at, until the end of messages at the data of execution. ';


--
-- Name: platform_pltfrm_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.platform_pltfrm_id_seq
    START WITH 25430
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.platform_pltfrm_id_seq OWNER TO augur;

--
-- Name: platform; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.platform (
    pltfrm_id bigint DEFAULT nextval('augur_data.platform_pltfrm_id_seq'::regclass) NOT NULL,
    pltfrm_name character varying,
    pltfrm_version character varying,
    pltfrm_release_date date,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone
);


ALTER TABLE augur_data.platform OWNER TO augur;

--
-- Name: pull_request_analysis_pull_request_analysis_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.pull_request_analysis_pull_request_analysis_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.pull_request_analysis_pull_request_analysis_id_seq OWNER TO augur;

--
-- Name: pull_request_analysis; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.pull_request_analysis (
    pull_request_analysis_id bigint DEFAULT nextval('augur_data.pull_request_analysis_pull_request_analysis_id_seq'::regclass) NOT NULL,
    pull_request_id bigint,
    merge_probability numeric(256,250),
    mechanism character varying,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(6) with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE augur_data.pull_request_analysis OWNER TO augur;

--
-- Name: COLUMN pull_request_analysis.pull_request_id; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.pull_request_analysis.pull_request_id IS 'It would be better if the pull request worker is run first to fetch the latest PRs before analyzing';


--
-- Name: COLUMN pull_request_analysis.merge_probability; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.pull_request_analysis.merge_probability IS 'Indicates the probability of the PR being merged';


--
-- Name: COLUMN pull_request_analysis.mechanism; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.pull_request_analysis.mechanism IS 'the ML model used for prediction (It is XGBoost Classifier at present)';


--
-- Name: pull_request_assignees_pr_assignee_map_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.pull_request_assignees_pr_assignee_map_id_seq
    START WITH 25430
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.pull_request_assignees_pr_assignee_map_id_seq OWNER TO augur;

--
-- Name: pull_request_assignees; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.pull_request_assignees (
    pr_assignee_map_id bigint DEFAULT nextval('augur_data.pull_request_assignees_pr_assignee_map_id_seq'::regclass) NOT NULL,
    pull_request_id bigint,
    repo_id bigint,
    pr_assignee_src_id bigint,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP,
    contrib_id uuid
);


ALTER TABLE augur_data.pull_request_assignees OWNER TO augur;

--
-- Name: pull_request_commits_pr_cmt_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.pull_request_commits_pr_cmt_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.pull_request_commits_pr_cmt_id_seq OWNER TO augur;

--
-- Name: pull_request_commits; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.pull_request_commits (
    pr_cmt_id bigint DEFAULT nextval('augur_data.pull_request_commits_pr_cmt_id_seq'::regclass) NOT NULL,
    pull_request_id bigint,
    repo_id bigint,
    pr_cmt_sha character varying,
    pr_cmt_node_id character varying,
    pr_cmt_message character varying,
    pr_cmt_comments_url character varying,
    pr_cmt_timestamp timestamp(0) without time zone,
    pr_cmt_author_email character varying,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP,
    pr_cmt_author_cntrb_id uuid
);


ALTER TABLE augur_data.pull_request_commits OWNER TO augur;

--
-- Name: TABLE pull_request_commits; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON TABLE augur_data.pull_request_commits IS 'Pull request commits are an enumeration of each commit associated with a pull request. 
Not all pull requests are from a branch or fork into master. 
The commits table intends to count only commits that end up in the master branch (i.e., part of the deployed code base for a project).
Therefore, there will be commit “SHA”’s in this table that are no associated with a commit SHA in the commits table. 
In cases where the PR is to the master branch of a project, you will find a match. In cases where the PR does not involve the master branch, you will not find a corresponding commit SHA in the commits table. This is expected. ';


--
-- Name: COLUMN pull_request_commits.pr_cmt_sha; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.pull_request_commits.pr_cmt_sha IS 'This is the commit SHA for a pull request commit. If the PR is not to the master branch of the main repository (or, in rare cases, from it), then you will NOT find a corresponding commit SHA in the commit table. (see table comment for further explanation). ';


--
-- Name: pull_request_events_pr_event_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.pull_request_events_pr_event_id_seq
    START WITH 25430
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.pull_request_events_pr_event_id_seq OWNER TO augur;

--
-- Name: pull_request_events; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.pull_request_events (
    pr_event_id bigint DEFAULT nextval('augur_data.pull_request_events_pr_event_id_seq'::regclass) NOT NULL,
    pull_request_id bigint NOT NULL,
    repo_id bigint,
    action character varying NOT NULL,
    action_commit_hash character varying,
    created_at timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    issue_event_src_id bigint,
    node_id character varying,
    node_url character varying,
    platform_id bigint DEFAULT 25150 NOT NULL,
    pr_platform_event_id bigint,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP,
    cntrb_id uuid
);


ALTER TABLE augur_data.pull_request_events OWNER TO augur;

--
-- Name: COLUMN pull_request_events.issue_event_src_id; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.pull_request_events.issue_event_src_id IS 'This ID comes from the source. In the case of GitHub, it is the id that is the first field returned from the issue events API';


--
-- Name: COLUMN pull_request_events.node_id; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.pull_request_events.node_id IS 'This should be renamed to issue_event_src_node_id, as its the varchar identifier in GitHub and likely common in other sources as well. However, since it was created before we came to this naming standard and workers are built around it, we have it simply named as node_id. Anywhere you see node_id in the schema, it comes from GitHubs terminology.';


--
-- Name: pull_request_files_pr_file_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.pull_request_files_pr_file_id_seq
    START WITH 25150
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.pull_request_files_pr_file_id_seq OWNER TO augur;

--
-- Name: pull_request_files; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.pull_request_files (
    pr_file_id bigint DEFAULT nextval('augur_data.pull_request_files_pr_file_id_seq'::regclass) NOT NULL,
    pull_request_id bigint,
    repo_id bigint,
    pr_file_additions bigint,
    pr_file_deletions bigint,
    pr_file_path character varying,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE augur_data.pull_request_files OWNER TO augur;

--
-- Name: TABLE pull_request_files; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON TABLE augur_data.pull_request_files IS 'Pull request commits are an enumeration of each commit associated with a pull request. 
Not all pull requests are from a branch or fork into master. 
The commits table intends to count only commits that end up in the master branch (i.e., part of the deployed code base for a project).
Therefore, there will be commit “SHA”’s in this table that are no associated with a commit SHA in the commits table. 
In cases where the PR is to the master branch of a project, you will find a match. In cases where the PR does not involve the master branch, you will not find a corresponding commit SHA in the commits table. This is expected. ';


--
-- Name: pull_request_labels_pr_label_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.pull_request_labels_pr_label_id_seq
    START WITH 25430
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.pull_request_labels_pr_label_id_seq OWNER TO augur;

--
-- Name: pull_request_labels; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.pull_request_labels (
    pr_label_id bigint DEFAULT nextval('augur_data.pull_request_labels_pr_label_id_seq'::regclass) NOT NULL,
    pull_request_id bigint,
    repo_id bigint,
    pr_src_id bigint,
    pr_src_node_id character varying,
    pr_src_url character varying,
    pr_src_description character varying,
    pr_src_color character varying,
    pr_src_default_bool boolean,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE augur_data.pull_request_labels OWNER TO augur;

--
-- Name: pull_request_meta_pr_repo_meta_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.pull_request_meta_pr_repo_meta_id_seq
    START WITH 25430
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.pull_request_meta_pr_repo_meta_id_seq OWNER TO augur;

--
-- Name: pull_request_meta; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.pull_request_meta (
    pr_repo_meta_id bigint DEFAULT nextval('augur_data.pull_request_meta_pr_repo_meta_id_seq'::regclass) NOT NULL,
    pull_request_id bigint,
    repo_id bigint,
    pr_head_or_base character varying,
    pr_src_meta_label character varying,
    pr_src_meta_ref character varying,
    pr_sha character varying,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP,
    cntrb_id uuid
);


ALTER TABLE augur_data.pull_request_meta OWNER TO augur;

--
-- Name: TABLE pull_request_meta; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON TABLE augur_data.pull_request_meta IS 'Pull requests contain referencing metadata.  There are a few columns that are discrete. There are also head and base designations for the repo on each side of the pull request. Similar functions exist in GitLab, though the language here is based on GitHub. The JSON Being adapted to as of the development of this schema is here:      "base": {       "label": "chaoss:dev",       "ref": "dev",       "sha": "dc6c6f3947f7dc84ecba3d8bda641ef786e7027d",       "user": {         "login": "chaoss",         "id": 29740296,         "node_id": "MDEyOk9yZ2FuaXphdGlvbjI5NzQwMjk2",         "avatar_url": "https://avatars2.githubusercontent.com/u/29740296?v=4",         "gravatar_id": "",         "url": "https://api.github.com/users/chaoss",         "html_url": "https://github.com/chaoss",         "followers_url": "https://api.github.com/users/chaoss/followers",         "following_url": "https://api.github.com/users/chaoss/following{/other_user}",         "gists_url": "https://api.github.com/users/chaoss/gists{/gist_id}",         "starred_url": "https://api.github.com/users/chaoss/starred{/owner}{/repo}",         "subscriptions_url": "https://api.github.com/users/chaoss/subscriptions",         "organizations_url": "https://api.github.com/users/chaoss/orgs",         "repos_url": "https://api.github.com/users/chaoss/repos",         "events_url": "https://api.github.com/users/chaoss/events{/privacy}",         "received_events_url": "https://api.github.com/users/chaoss/received_events",         "type": "Organization",         "site_admin": false       },       "repo": {         "id": 78134122,         "node_id": "MDEwOlJlcG9zaXRvcnk3ODEzNDEyMg==",         "name": "augur",         "full_name": "chaoss/augur",         "private": false,         "owner": {           "login": "chaoss",           "id": 29740296,           "node_id": "MDEyOk9yZ2FuaXphdGlvbjI5NzQwMjk2",           "avatar_url": "https://avatars2.githubusercontent.com/u/29740296?v=4",           "gravatar_id": "",           "url": "https://api.github.com/users/chaoss",           "html_url": "https://github.com/chaoss",           "followers_url": "https://api.github.com/users/chaoss/followers",           "following_url": "https://api.github.com/users/chaoss/following{/other_user}",           "gists_url": "https://api.github.com/users/chaoss/gists{/gist_id}",           "starred_url": "https://api.github.com/users/chaoss/starred{/owner}{/repo}",           "subscriptions_url": "https://api.github.com/users/chaoss/subscriptions",           "organizations_url": "https://api.github.com/users/chaoss/orgs",           "repos_url": "https://api.github.com/users/chaoss/repos",           "events_url": "https://api.github.com/users/chaoss/events{/privacy}",           "received_events_url": "https://api.github.com/users/chaoss/received_events",           "type": "Organization",           "site_admin": false         }, ';


--
-- Name: COLUMN pull_request_meta.pr_head_or_base; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.pull_request_meta.pr_head_or_base IS 'Each pull request should have one and only one head record; and one and only one base record. ';


--
-- Name: COLUMN pull_request_meta.pr_src_meta_label; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.pull_request_meta.pr_src_meta_label IS 'This is a representation of the repo:branch information in the pull request. Head is issueing the pull request and base is taking the pull request. For example:  (We do not store all of this)

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


--
-- Name: pull_request_repo_pr_repo_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.pull_request_repo_pr_repo_id_seq
    START WITH 25430
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.pull_request_repo_pr_repo_id_seq OWNER TO augur;

--
-- Name: pull_request_repo; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.pull_request_repo (
    pr_repo_id bigint DEFAULT nextval('augur_data.pull_request_repo_pr_repo_id_seq'::regclass) NOT NULL,
    pr_repo_meta_id bigint,
    pr_repo_head_or_base character varying,
    pr_src_repo_id bigint,
    pr_src_node_id character varying,
    pr_repo_name character varying,
    pr_repo_full_name character varying,
    pr_repo_private_bool boolean,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP,
    pr_cntrb_id uuid
);


ALTER TABLE augur_data.pull_request_repo OWNER TO augur;

--
-- Name: TABLE pull_request_repo; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON TABLE augur_data.pull_request_repo IS 'This table is for storing information about forks that exist as part of a pull request. Generally we do not want to track these like ordinary repositories. ';


--
-- Name: COLUMN pull_request_repo.pr_repo_head_or_base; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.pull_request_repo.pr_repo_head_or_base IS 'For ease of validation checking, we should determine if the repository referenced is the head or base of the pull request. Each pull request should have one and only one of these, which is not enforcable easily in the database.';


--
-- Name: pull_request_review_message_ref_pr_review_msg_ref_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.pull_request_review_message_ref_pr_review_msg_ref_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.pull_request_review_message_ref_pr_review_msg_ref_id_seq OWNER TO augur;

--
-- Name: pull_request_review_message_ref; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.pull_request_review_message_ref (
    pr_review_msg_ref_id bigint DEFAULT nextval('augur_data.pull_request_review_message_ref_pr_review_msg_ref_id_seq'::regclass) NOT NULL,
    pr_review_id bigint NOT NULL,
    repo_id bigint,
    msg_id bigint NOT NULL,
    pr_review_msg_url character varying,
    pr_review_src_id bigint,
    pr_review_msg_src_id bigint,
    pr_review_msg_node_id character varying,
    pr_review_msg_diff_hunk character varying,
    pr_review_msg_path character varying,
    pr_review_msg_position bigint,
    pr_review_msg_original_position bigint,
    pr_review_msg_commit_id character varying,
    pr_review_msg_original_commit_id character varying,
    pr_review_msg_updated_at timestamp(6) without time zone,
    pr_review_msg_html_url character varying,
    pr_url character varying,
    pr_review_msg_author_association character varying,
    pr_review_msg_start_line bigint,
    pr_review_msg_original_start_line bigint,
    pr_review_msg_start_side character varying,
    pr_review_msg_line bigint,
    pr_review_msg_original_line bigint,
    pr_review_msg_side character varying,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE augur_data.pull_request_review_message_ref OWNER TO augur;

--
-- Name: pull_request_reviewers_pr_reviewer_map_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.pull_request_reviewers_pr_reviewer_map_id_seq
    START WITH 25430
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.pull_request_reviewers_pr_reviewer_map_id_seq OWNER TO augur;

--
-- Name: pull_request_reviewers; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.pull_request_reviewers (
    pr_reviewer_map_id bigint DEFAULT nextval('augur_data.pull_request_reviewers_pr_reviewer_map_id_seq'::regclass) NOT NULL,
    pull_request_id bigint,
    pr_source_id bigint,
    repo_id bigint,
    pr_reviewer_src_id bigint,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP,
    cntrb_id uuid
);


ALTER TABLE augur_data.pull_request_reviewers OWNER TO augur;

--
-- Name: COLUMN pull_request_reviewers.pr_source_id; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.pull_request_reviewers.pr_source_id IS 'The platform ID for the pull/merge request. Used as part of the natural key, along with pr_reviewer_src_id in this table. ';


--
-- Name: COLUMN pull_request_reviewers.pr_reviewer_src_id; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.pull_request_reviewers.pr_reviewer_src_id IS 'The platform ID for the pull/merge request reviewer. Used as part of the natural key, along with pr_source_id in this table. ';


--
-- Name: pull_request_reviews_pr_review_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.pull_request_reviews_pr_review_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.pull_request_reviews_pr_review_id_seq OWNER TO augur;

--
-- Name: pull_request_reviews; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.pull_request_reviews (
    pr_review_id bigint DEFAULT nextval('augur_data.pull_request_reviews_pr_review_id_seq'::regclass) NOT NULL,
    pull_request_id bigint NOT NULL,
    repo_id bigint,
    pr_review_author_association character varying,
    pr_review_state character varying,
    pr_review_body character varying,
    pr_review_submitted_at timestamp(6) without time zone,
    pr_review_src_id bigint,
    pr_review_node_id character varying,
    pr_review_html_url character varying,
    pr_review_pull_request_url character varying,
    pr_review_commit_id character varying,
    platform_id bigint DEFAULT 25150,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP,
    cntrb_id uuid NOT NULL
);


ALTER TABLE augur_data.pull_request_reviews OWNER TO augur;

--
-- Name: pull_request_teams_pr_team_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.pull_request_teams_pr_team_id_seq
    START WITH 25430
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.pull_request_teams_pr_team_id_seq OWNER TO augur;

--
-- Name: pull_request_teams; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.pull_request_teams (
    pr_team_id bigint DEFAULT nextval('augur_data.pull_request_teams_pr_team_id_seq'::regclass) NOT NULL,
    pull_request_id bigint,
    pr_src_team_id bigint,
    pr_src_team_node character varying,
    pr_src_team_url character varying,
    pr_team_name character varying,
    pr_team_slug character varying,
    pr_team_description character varying,
    pr_team_privacy character varying,
    pr_team_permission character varying,
    pr_team_src_members_url character varying,
    pr_team_src_repositories_url character varying,
    pr_team_parent_id bigint,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE augur_data.pull_request_teams OWNER TO augur;

--
-- Name: releases_release_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.releases_release_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.releases_release_id_seq OWNER TO augur;

--
-- Name: releases; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.releases (
    release_id character(256) DEFAULT nextval('augur_data.releases_release_id_seq'::regclass) NOT NULL,
    repo_id bigint NOT NULL,
    release_name character varying,
    release_description character varying,
    release_author character varying,
    release_created_at timestamp(6) without time zone,
    release_published_at timestamp(6) without time zone,
    release_updated_at timestamp(6) without time zone,
    release_is_draft boolean,
    release_is_prerelease boolean,
    release_tag_name character varying,
    release_url character varying,
    tag_only boolean,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(6) without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE augur_data.releases OWNER TO augur;

--
-- Name: repo_badging_badge_collection_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.repo_badging_badge_collection_id_seq
    START WITH 25012
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.repo_badging_badge_collection_id_seq OWNER TO augur;

--
-- Name: repo_badging; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.repo_badging (
    badge_collection_id bigint DEFAULT nextval('augur_data.repo_badging_badge_collection_id_seq'::regclass) NOT NULL,
    repo_id bigint,
    created_at timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP,
    data jsonb
);


ALTER TABLE augur_data.repo_badging OWNER TO augur;

--
-- Name: TABLE repo_badging; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON TABLE augur_data.repo_badging IS 'This will be collected from the LF’s Badging API
https://bestpractices.coreinfrastructure.org/projects.json?pq=https%3A%2F%2Fgithub.com%2Fchaoss%2Faugur
';


--
-- Name: repo_clones_data_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.repo_clones_data_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.repo_clones_data_id_seq OWNER TO augur;

--
-- Name: repo_clones_data; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.repo_clones_data (
    repo_clone_data_id bigint DEFAULT nextval('augur_data.repo_clones_data_id_seq'::regclass) NOT NULL,
    repo_id bigint NOT NULL,
    unique_clones bigint,
    count_clones bigint,
    clone_data_timestamp timestamp(6) without time zone
);


ALTER TABLE augur_data.repo_clones_data OWNER TO augur;

--
-- Name: repo_cluster_messages_msg_cluster_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.repo_cluster_messages_msg_cluster_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.repo_cluster_messages_msg_cluster_id_seq OWNER TO augur;

--
-- Name: repo_cluster_messages; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.repo_cluster_messages (
    msg_cluster_id bigint DEFAULT nextval('augur_data.repo_cluster_messages_msg_cluster_id_seq'::regclass) NOT NULL,
    repo_id bigint,
    cluster_content integer,
    cluster_mechanism integer,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE augur_data.repo_cluster_messages OWNER TO augur;

--
-- Name: repo_dependencies_repo_dependencies_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.repo_dependencies_repo_dependencies_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.repo_dependencies_repo_dependencies_id_seq OWNER TO augur;

--
-- Name: repo_dependencies; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.repo_dependencies (
    repo_dependencies_id bigint DEFAULT nextval('augur_data.repo_dependencies_repo_dependencies_id_seq'::regclass) NOT NULL,
    repo_id bigint,
    dep_name character varying,
    dep_count integer,
    dep_language character varying,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE augur_data.repo_dependencies OWNER TO augur;

--
-- Name: TABLE repo_dependencies; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON TABLE augur_data.repo_dependencies IS 'Contains the dependencies for a repo.';


--
-- Name: COLUMN repo_dependencies.repo_id; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.repo_dependencies.repo_id IS 'Forign key for repo id. ';


--
-- Name: COLUMN repo_dependencies.dep_name; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.repo_dependencies.dep_name IS 'Name of the dependancy found in project. ';


--
-- Name: COLUMN repo_dependencies.dep_count; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.repo_dependencies.dep_count IS 'Number of times the dependancy was found. ';


--
-- Name: COLUMN repo_dependencies.dep_language; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.repo_dependencies.dep_language IS 'Language of the dependancy. ';


--
-- Name: repo_deps_scorecard_repo_deps_scorecard_id_seq1; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.repo_deps_scorecard_repo_deps_scorecard_id_seq1
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.repo_deps_scorecard_repo_deps_scorecard_id_seq1 OWNER TO augur;

--
-- Name: repo_deps_scorecard; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.repo_deps_scorecard (
    repo_deps_scorecard_id bigint DEFAULT nextval('augur_data.repo_deps_scorecard_repo_deps_scorecard_id_seq1'::regclass) NOT NULL,
    repo_id bigint,
    name character varying,
    score character varying,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP,
    scorecard_check_details jsonb
);


ALTER TABLE augur_data.repo_deps_scorecard OWNER TO augur;

--
-- Name: repo_group_insights_rgi_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.repo_group_insights_rgi_id_seq
    START WITH 25430
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.repo_group_insights_rgi_id_seq OWNER TO augur;

--
-- Name: repo_group_insights; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.repo_group_insights (
    rgi_id bigint DEFAULT nextval('augur_data.repo_group_insights_rgi_id_seq'::regclass) NOT NULL,
    repo_group_id bigint,
    rgi_metric character varying,
    rgi_value character varying,
    cms_id bigint,
    rgi_fresh boolean,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE augur_data.repo_group_insights OWNER TO augur;

--
-- Name: TABLE repo_group_insights; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON TABLE augur_data.repo_group_insights IS 'This table is output from an analytical worker inside of Augur. It runs through the different metrics on a REPOSITORY_GROUP and identifies the five to ten most “interesting” metrics as defined by some kind of delta or other factor. The algorithm is going to evolve. 

Worker Design Notes: The idea is that the "insight worker" will scan through a bunch of active metrics or "synthetic metrics" to list the most important insights. ';


--
-- Name: COLUMN repo_group_insights.rgi_fresh; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.repo_group_insights.rgi_fresh IS 'false if the date is before the statistic that triggered the insight, true if after. This allows us to automatically display only "fresh insights" and avoid displaying "stale insights". The insight worker will populate this table. ';


--
-- Name: repo_groups_list_serve_rgls_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.repo_groups_list_serve_rgls_id_seq
    START WITH 25430
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.repo_groups_list_serve_rgls_id_seq OWNER TO augur;

--
-- Name: repo_groups_list_serve; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.repo_groups_list_serve (
    rgls_id bigint DEFAULT nextval('augur_data.repo_groups_list_serve_rgls_id_seq'::regclass) NOT NULL,
    repo_group_id bigint NOT NULL,
    rgls_name character varying,
    rgls_description character varying(3000),
    rgls_sponsor character varying,
    rgls_email character varying,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone
);


ALTER TABLE augur_data.repo_groups_list_serve OWNER TO augur;

--
-- Name: repo_info_repo_info_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.repo_info_repo_info_id_seq
    START WITH 25430
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.repo_info_repo_info_id_seq OWNER TO augur;

--
-- Name: repo_info; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.repo_info (
    repo_info_id bigint DEFAULT nextval('augur_data.repo_info_repo_info_id_seq'::regclass) NOT NULL,
    repo_id bigint NOT NULL,
    last_updated timestamp(0) without time zone DEFAULT NULL::timestamp without time zone,
    issues_enabled character varying,
    open_issues integer,
    pull_requests_enabled character varying,
    wiki_enabled character varying,
    pages_enabled character varying,
    fork_count integer,
    default_branch character varying,
    watchers_count integer,
    "UUID" integer,
    license character varying,
    stars_count integer,
    committers_count integer,
    issue_contributors_count character varying,
    changelog_file character varying,
    contributing_file character varying,
    license_file character varying,
    code_of_conduct_file character varying,
    security_issue_file character varying,
    security_audit_file character varying,
    status character varying,
    keywords character varying,
    commit_count bigint,
    issues_count bigint,
    issues_closed bigint,
    pull_request_count bigint,
    pull_requests_open bigint,
    pull_requests_closed bigint,
    pull_requests_merged bigint,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE augur_data.repo_info OWNER TO augur;

--
-- Name: repo_insights_ri_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.repo_insights_ri_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.repo_insights_ri_id_seq OWNER TO augur;

--
-- Name: repo_insights; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.repo_insights (
    ri_id bigint DEFAULT nextval('augur_data.repo_insights_ri_id_seq'::regclass) NOT NULL,
    repo_id bigint,
    ri_metric character varying,
    ri_value character varying,
    ri_date timestamp(0) without time zone,
    ri_fresh boolean,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP,
    ri_score numeric,
    ri_field character varying,
    ri_detection_method character varying
);


ALTER TABLE augur_data.repo_insights OWNER TO augur;

--
-- Name: TABLE repo_insights; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON TABLE augur_data.repo_insights IS 'This table is output from an analytical worker inside of Augur. It runs through the different metrics on a repository and identifies the five to ten most “interesting” metrics as defined by some kind of delta or other factor. The algorithm is going to evolve. 

Worker Design Notes: The idea is that the "insight worker" will scan through a bunch of active metrics or "synthetic metrics" to list the most important insights. ';


--
-- Name: COLUMN repo_insights.ri_fresh; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.repo_insights.ri_fresh IS 'false if the date is before the statistic that triggered the insight, true if after. This allows us to automatically display only "fresh insights" and avoid displaying "stale insights". The insight worker will populate this table. ';


--
-- Name: repo_insights_records_ri_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.repo_insights_records_ri_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.repo_insights_records_ri_id_seq OWNER TO augur;

--
-- Name: repo_insights_records; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.repo_insights_records (
    ri_id bigint DEFAULT nextval('augur_data.repo_insights_records_ri_id_seq'::regclass) NOT NULL,
    repo_id bigint,
    ri_metric character varying,
    ri_field character varying,
    ri_value character varying,
    ri_date timestamp(6) without time zone,
    ri_score double precision,
    ri_detection_method character varying,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(6) without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE augur_data.repo_insights_records OWNER TO augur;

--
-- Name: COLUMN repo_insights_records.ri_id; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.repo_insights_records.ri_id IS 'Primary key. ';


--
-- Name: COLUMN repo_insights_records.repo_id; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.repo_insights_records.repo_id IS 'Refers to repo table primary key. Will have a foreign key';


--
-- Name: COLUMN repo_insights_records.ri_metric; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.repo_insights_records.ri_metric IS 'The metric endpoint';


--
-- Name: COLUMN repo_insights_records.ri_field; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.repo_insights_records.ri_field IS 'The field in the metric endpoint';


--
-- Name: COLUMN repo_insights_records.ri_value; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.repo_insights_records.ri_value IS 'The value of the endpoint in ri_field';


--
-- Name: COLUMN repo_insights_records.ri_date; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.repo_insights_records.ri_date IS 'The date the insight is for; in other words, some anomaly occurred on this date. ';


--
-- Name: COLUMN repo_insights_records.ri_score; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.repo_insights_records.ri_score IS 'A Score, derived from the algorithm used. ';


--
-- Name: COLUMN repo_insights_records.ri_detection_method; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.repo_insights_records.ri_detection_method IS 'A confidence interval or other expression of the type of threshold and the value of a threshold met in order for it to be "an insight". Example. "95% confidence interval". ';


--
-- Name: COLUMN repo_insights_records.tool_source; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.repo_insights_records.tool_source IS 'Standard Augur Metadata';


--
-- Name: COLUMN repo_insights_records.tool_version; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.repo_insights_records.tool_version IS 'Standard Augur Metadata';


--
-- Name: COLUMN repo_insights_records.data_source; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.repo_insights_records.data_source IS 'Standard Augur Metadata';


--
-- Name: COLUMN repo_insights_records.data_collection_date; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.repo_insights_records.data_collection_date IS 'Standard Augur Metadata';


--
-- Name: repo_labor_repo_labor_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.repo_labor_repo_labor_id_seq
    START WITH 25430
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.repo_labor_repo_labor_id_seq OWNER TO augur;

--
-- Name: repo_labor; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.repo_labor (
    repo_labor_id bigint DEFAULT nextval('augur_data.repo_labor_repo_labor_id_seq'::regclass) NOT NULL,
    repo_id bigint,
    repo_clone_date timestamp(0) without time zone,
    rl_analysis_date timestamp(0) without time zone,
    programming_language character varying,
    file_path character varying,
    file_name character varying,
    total_lines integer,
    code_lines integer,
    comment_lines integer,
    blank_lines integer,
    code_complexity integer,
    repo_url character varying,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone
);


ALTER TABLE augur_data.repo_labor OWNER TO augur;

--
-- Name: TABLE repo_labor; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON TABLE augur_data.repo_labor IS 'repo_labor is a derivative of tables used to store scc code and complexity counting statistics that are inputs to labor analysis, which are components of CHAOSS value metric calculations. ';


--
-- Name: COLUMN repo_labor.repo_url; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON COLUMN augur_data.repo_labor.repo_url IS 'This is a convenience column to simplify analysis against external datasets';


--
-- Name: repo_meta_rmeta_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.repo_meta_rmeta_id_seq
    START WITH 25430
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.repo_meta_rmeta_id_seq OWNER TO augur;

--
-- Name: repo_meta; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.repo_meta (
    repo_id bigint NOT NULL,
    rmeta_id bigint DEFAULT nextval('augur_data.repo_meta_rmeta_id_seq'::regclass) NOT NULL,
    rmeta_name character varying,
    rmeta_value character varying DEFAULT 0,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone
);


ALTER TABLE augur_data.repo_meta OWNER TO augur;

--
-- Name: TABLE repo_meta; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON TABLE augur_data.repo_meta IS 'Project Languages';


--
-- Name: repo_sbom_scans_rsb_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.repo_sbom_scans_rsb_id_seq
    START WITH 25430
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.repo_sbom_scans_rsb_id_seq OWNER TO augur;

--
-- Name: repo_sbom_scans; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.repo_sbom_scans (
    rsb_id bigint DEFAULT nextval('augur_data.repo_sbom_scans_rsb_id_seq'::regclass) NOT NULL,
    repo_id bigint,
    sbom_scan json
);


ALTER TABLE augur_data.repo_sbom_scans OWNER TO augur;

--
-- Name: repo_stats_rstat_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.repo_stats_rstat_id_seq
    START WITH 25430
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.repo_stats_rstat_id_seq OWNER TO augur;

--
-- Name: repo_stats; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.repo_stats (
    repo_id bigint NOT NULL,
    rstat_id bigint DEFAULT nextval('augur_data.repo_stats_rstat_id_seq'::regclass) NOT NULL,
    rstat_name character varying(400),
    rstat_value bigint,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone
);


ALTER TABLE augur_data.repo_stats OWNER TO augur;

--
-- Name: TABLE repo_stats; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON TABLE augur_data.repo_stats IS 'Project Watchers';


--
-- Name: repo_test_coverage_repo_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.repo_test_coverage_repo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.repo_test_coverage_repo_id_seq OWNER TO augur;

--
-- Name: repo_test_coverage; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.repo_test_coverage (
    repo_id bigint DEFAULT nextval('augur_data.repo_test_coverage_repo_id_seq'::regclass) NOT NULL,
    repo_clone_date timestamp(0) without time zone,
    rtc_analysis_date timestamp(0) without time zone,
    programming_language character varying,
    file_path character varying,
    file_name character varying,
    testing_tool character varying,
    file_statement_count bigint,
    file_subroutine_count bigint,
    file_statements_tested bigint,
    file_subroutines_tested bigint,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE augur_data.repo_test_coverage OWNER TO augur;

--
-- Name: repo_topic_repo_topic_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.repo_topic_repo_topic_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.repo_topic_repo_topic_id_seq OWNER TO augur;

--
-- Name: repo_topic; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.repo_topic (
    repo_topic_id bigint DEFAULT nextval('augur_data.repo_topic_repo_topic_id_seq'::regclass) NOT NULL,
    repo_id bigint,
    topic_id integer,
    topic_prob double precision,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE augur_data.repo_topic OWNER TO augur;

--
-- Name: repos_fetch_log; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.repos_fetch_log (
    repos_id integer NOT NULL,
    status character varying(128) NOT NULL,
    date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE augur_data.repos_fetch_log OWNER TO augur;

--
-- Name: settings; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.settings (
    id integer NOT NULL,
    setting character varying(32) NOT NULL,
    value character varying NOT NULL,
    last_modified timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE augur_data.settings OWNER TO augur;

--
-- Name: topic_words_topic_words_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.topic_words_topic_words_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.topic_words_topic_words_id_seq OWNER TO augur;

--
-- Name: topic_words; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.topic_words (
    topic_words_id bigint DEFAULT nextval('augur_data.topic_words_topic_words_id_seq'::regclass) NOT NULL,
    topic_id bigint,
    word character varying,
    word_prob double precision,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE augur_data.topic_words OWNER TO augur;

--
-- Name: unknown_cache; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.unknown_cache (
    type character varying(10) NOT NULL,
    repo_group_id integer NOT NULL,
    email character varying(128) NOT NULL,
    domain character varying(128) DEFAULT 'NULL'::character varying,
    added bigint NOT NULL,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE augur_data.unknown_cache OWNER TO augur;

--
-- Name: unresolved_commit_emails_email_unresolved_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.unresolved_commit_emails_email_unresolved_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.unresolved_commit_emails_email_unresolved_id_seq OWNER TO augur;

--
-- Name: unresolved_commit_emails; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.unresolved_commit_emails (
    email_unresolved_id bigint DEFAULT nextval('augur_data.unresolved_commit_emails_email_unresolved_id_seq'::regclass) NOT NULL,
    email character varying NOT NULL,
    name character varying,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE augur_data.unresolved_commit_emails OWNER TO augur;

--
-- Name: utility_log_id_seq1; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.utility_log_id_seq1
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.utility_log_id_seq1 OWNER TO augur;

--
-- Name: utility_log; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.utility_log (
    id bigint DEFAULT nextval('augur_data.utility_log_id_seq1'::regclass) NOT NULL,
    level character varying(8) NOT NULL,
    status character varying NOT NULL,
    attempted timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE augur_data.utility_log OWNER TO augur;

--
-- Name: utility_log_id_seq; Type: SEQUENCE; Schema: augur_data; Owner: augur
--

CREATE SEQUENCE augur_data.utility_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_data.utility_log_id_seq OWNER TO augur;

--
-- Name: working_commits; Type: TABLE; Schema: augur_data; Owner: augur
--

CREATE TABLE augur_data.working_commits (
    repos_id integer NOT NULL,
    working_commit character varying(40) DEFAULT 'NULL'::character varying
);


ALTER TABLE augur_data.working_commits OWNER TO augur;

--
-- Name: affiliations_corp_id_seq; Type: SEQUENCE; Schema: augur_operations; Owner: augur
--

CREATE SEQUENCE augur_operations.affiliations_corp_id_seq
    START WITH 620000
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_operations.affiliations_corp_id_seq OWNER TO augur;

--
-- Name: all; Type: TABLE; Schema: augur_operations; Owner: augur
--

CREATE TABLE augur_operations."all" (
    "Name" character varying,
    "Bytes" character varying,
    "Lines" character varying,
    "Code" character varying,
    "Comment" character varying,
    "Blank" character varying,
    "Complexity" character varying,
    "Count" character varying,
    "WeightedComplexity" character varying,
    "Files" character varying
);


ALTER TABLE augur_operations."all" OWNER TO augur;

--
-- Name: augur_settings_id_seq; Type: SEQUENCE; Schema: augur_operations; Owner: augur
--

CREATE SEQUENCE augur_operations.augur_settings_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_operations.augur_settings_id_seq OWNER TO augur;

--
-- Name: augur_settings; Type: TABLE; Schema: augur_operations; Owner: augur
--

CREATE TABLE augur_operations.augur_settings (
    id bigint DEFAULT nextval('augur_operations.augur_settings_id_seq'::regclass) NOT NULL,
    setting character varying,
    value character varying,
    last_modified timestamp(0) without time zone DEFAULT CURRENT_DATE
);


ALTER TABLE augur_operations.augur_settings OWNER TO augur;

--
-- Name: TABLE augur_settings; Type: COMMENT; Schema: augur_operations; Owner: augur
--

COMMENT ON TABLE augur_operations.augur_settings IS 'Augur settings include the schema version, and the Augur API Key as of 10/25/2020. Future augur settings may be stored in this table, which has the basic structure of a name-value pair. ';


--
-- Name: client_applications; Type: TABLE; Schema: augur_operations; Owner: augur
--

CREATE TABLE augur_operations.client_applications (
    id character varying NOT NULL,
    api_key character varying NOT NULL,
    user_id integer NOT NULL,
    name character varying NOT NULL,
    redirect_url character varying NOT NULL
);


ALTER TABLE augur_operations.client_applications OWNER TO augur;

--
-- Name: collection_status; Type: TABLE; Schema: augur_operations; Owner: augur
--

CREATE TABLE augur_operations.collection_status (
    repo_id bigint NOT NULL,
    core_data_last_collected timestamp without time zone,
    core_status character varying DEFAULT 'Pending'::character varying NOT NULL,
    core_task_id character varying,
    secondary_data_last_collected timestamp without time zone,
    secondary_status character varying DEFAULT 'Pending'::character varying NOT NULL,
    secondary_task_id character varying,
    event_last_collected timestamp without time zone,
    facade_status character varying DEFAULT 'Pending'::character varying NOT NULL,
    facade_data_last_collected timestamp without time zone,
    facade_task_id character varying
);


ALTER TABLE augur_operations.collection_status OWNER TO augur;

--
-- Name: config; Type: TABLE; Schema: augur_operations; Owner: augur
--

CREATE TABLE augur_operations.config (
    id smallint NOT NULL,
    section_name character varying NOT NULL,
    setting_name character varying NOT NULL,
    value character varying,
    type character varying
);


ALTER TABLE augur_operations.config OWNER TO augur;

--
-- Name: config_id_seq; Type: SEQUENCE; Schema: augur_operations; Owner: augur
--

CREATE SEQUENCE augur_operations.config_id_seq
    AS smallint
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_operations.config_id_seq OWNER TO augur;

--
-- Name: config_id_seq; Type: SEQUENCE OWNED BY; Schema: augur_operations; Owner: augur
--

ALTER SEQUENCE augur_operations.config_id_seq OWNED BY augur_operations.config.id;


--
-- Name: gh_worker_history_history_id_seq; Type: SEQUENCE; Schema: augur_operations; Owner: augur
--

CREATE SEQUENCE augur_operations.gh_worker_history_history_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_operations.gh_worker_history_history_id_seq OWNER TO augur;

--
-- Name: refresh_tokens; Type: TABLE; Schema: augur_operations; Owner: augur
--

CREATE TABLE augur_operations.refresh_tokens (
    id character varying NOT NULL,
    user_session_token character varying NOT NULL
);


ALTER TABLE augur_operations.refresh_tokens OWNER TO augur;

--
-- Name: repos_fetch_log; Type: TABLE; Schema: augur_operations; Owner: augur
--

CREATE TABLE augur_operations.repos_fetch_log (
    repos_id integer NOT NULL,
    status character varying(128) NOT NULL,
    date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE augur_operations.repos_fetch_log OWNER TO augur;

--
-- Name: TABLE repos_fetch_log; Type: COMMENT; Schema: augur_operations; Owner: augur
--

COMMENT ON TABLE augur_operations.repos_fetch_log IS 'For future use when we move all working tables to the augur_operations schema. ';


--
-- Name: subscription_types; Type: TABLE; Schema: augur_operations; Owner: augur
--

CREATE TABLE augur_operations.subscription_types (
    id bigint NOT NULL,
    name character varying NOT NULL
);


ALTER TABLE augur_operations.subscription_types OWNER TO augur;

--
-- Name: subscription_types_id_seq; Type: SEQUENCE; Schema: augur_operations; Owner: augur
--

CREATE SEQUENCE augur_operations.subscription_types_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_operations.subscription_types_id_seq OWNER TO augur;

--
-- Name: subscription_types_id_seq; Type: SEQUENCE OWNED BY; Schema: augur_operations; Owner: augur
--

ALTER SEQUENCE augur_operations.subscription_types_id_seq OWNED BY augur_operations.subscription_types.id;


--
-- Name: subscriptions; Type: TABLE; Schema: augur_operations; Owner: augur
--

CREATE TABLE augur_operations.subscriptions (
    application_id character varying NOT NULL,
    type_id bigint NOT NULL
);


ALTER TABLE augur_operations.subscriptions OWNER TO augur;

--
-- Name: user_groups; Type: TABLE; Schema: augur_operations; Owner: augur
--

CREATE TABLE augur_operations.user_groups (
    group_id bigint NOT NULL,
    user_id integer NOT NULL,
    name character varying NOT NULL,
    favorited boolean DEFAULT false NOT NULL
);


ALTER TABLE augur_operations.user_groups OWNER TO augur;

--
-- Name: user_groups_group_id_seq; Type: SEQUENCE; Schema: augur_operations; Owner: augur
--

CREATE SEQUENCE augur_operations.user_groups_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_operations.user_groups_group_id_seq OWNER TO augur;

--
-- Name: user_groups_group_id_seq; Type: SEQUENCE OWNED BY; Schema: augur_operations; Owner: augur
--

ALTER SEQUENCE augur_operations.user_groups_group_id_seq OWNED BY augur_operations.user_groups.group_id;


--
-- Name: user_repos; Type: TABLE; Schema: augur_operations; Owner: augur
--

CREATE TABLE augur_operations.user_repos (
    repo_id bigint NOT NULL,
    group_id bigint NOT NULL
);


ALTER TABLE augur_operations.user_repos OWNER TO augur;

--
-- Name: user_session_tokens; Type: TABLE; Schema: augur_operations; Owner: augur
--

CREATE TABLE augur_operations.user_session_tokens (
    token character varying NOT NULL,
    user_id integer NOT NULL,
    created_at bigint,
    expiration bigint,
    application_id character varying
);


ALTER TABLE augur_operations.user_session_tokens OWNER TO augur;

--
-- Name: users; Type: TABLE; Schema: augur_operations; Owner: augur
--

CREATE TABLE augur_operations.users (
    user_id integer NOT NULL,
    login_name character varying NOT NULL,
    login_hashword character varying NOT NULL,
    email character varying NOT NULL,
    text_phone character varying,
    first_name character varying NOT NULL,
    last_name character varying NOT NULL,
    tool_source character varying,
    tool_version character varying,
    data_source character varying,
    data_collection_date timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP,
    admin boolean NOT NULL
);


ALTER TABLE augur_operations.users OWNER TO augur;

--
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: augur_operations; Owner: augur
--

CREATE SEQUENCE augur_operations.users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_operations.users_user_id_seq OWNER TO augur;

--
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: augur_operations; Owner: augur
--

ALTER SEQUENCE augur_operations.users_user_id_seq OWNED BY augur_operations.users.user_id;


--
-- Name: worker_history; Type: TABLE; Schema: augur_operations; Owner: augur
--

CREATE TABLE augur_operations.worker_history (
    history_id bigint DEFAULT nextval('augur_operations.gh_worker_history_history_id_seq'::regclass) NOT NULL,
    repo_id bigint,
    worker character varying(255) NOT NULL,
    job_model character varying(255) NOT NULL,
    oauth_id integer,
    "timestamp" timestamp(0) without time zone NOT NULL,
    status character varying(7) NOT NULL,
    total_results integer
);


ALTER TABLE augur_operations.worker_history OWNER TO augur;

--
-- Name: TABLE worker_history; Type: COMMENT; Schema: augur_operations; Owner: augur
--

COMMENT ON TABLE augur_operations.worker_history IS 'This table stores the complete history of job execution, including success and failure. It is useful for troubleshooting. ';


--
-- Name: worker_job; Type: TABLE; Schema: augur_operations; Owner: augur
--

CREATE TABLE augur_operations.worker_job (
    job_model character varying(255) NOT NULL,
    state integer DEFAULT 0 NOT NULL,
    zombie_head integer,
    since_id_str character varying(255) DEFAULT '0'::character varying NOT NULL,
    description character varying(255) DEFAULT 'None'::character varying,
    last_count integer,
    last_run timestamp(0) without time zone DEFAULT NULL::timestamp without time zone,
    analysis_state integer DEFAULT 0,
    oauth_id integer NOT NULL
);


ALTER TABLE augur_operations.worker_job OWNER TO augur;

--
-- Name: TABLE worker_job; Type: COMMENT; Schema: augur_operations; Owner: augur
--

COMMENT ON TABLE augur_operations.worker_job IS 'This table stores the jobs workers collect data for. A job is found in the code, and in the augur.config.json under the construct of a “model”. ';


--
-- Name: worker_oauth_oauth_id_seq; Type: SEQUENCE; Schema: augur_operations; Owner: augur
--

CREATE SEQUENCE augur_operations.worker_oauth_oauth_id_seq
    START WITH 1000
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE augur_operations.worker_oauth_oauth_id_seq OWNER TO augur;

--
-- Name: worker_oauth; Type: TABLE; Schema: augur_operations; Owner: augur
--

CREATE TABLE augur_operations.worker_oauth (
    oauth_id bigint DEFAULT nextval('augur_operations.worker_oauth_oauth_id_seq'::regclass) NOT NULL,
    name character varying(255) NOT NULL,
    consumer_key character varying(255) NOT NULL,
    consumer_secret character varying(255) NOT NULL,
    access_token character varying(255) NOT NULL,
    access_token_secret character varying(255) NOT NULL,
    repo_directory character varying,
    platform character varying DEFAULT 'github'::character varying
);


ALTER TABLE augur_operations.worker_oauth OWNER TO augur;

--
-- Name: TABLE worker_oauth; Type: COMMENT; Schema: augur_operations; Owner: augur
--

COMMENT ON TABLE augur_operations.worker_oauth IS 'This table stores credentials for retrieving data from platform API’s. Entries in this table must comply with the terms of service for each platform. ';


--
-- Name: worker_settings_facade; Type: TABLE; Schema: augur_operations; Owner: augur
--

CREATE TABLE augur_operations.worker_settings_facade (
    id integer NOT NULL,
    setting character varying(32) NOT NULL,
    value character varying NOT NULL,
    last_modified timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE augur_operations.worker_settings_facade OWNER TO augur;

--
-- Name: TABLE worker_settings_facade; Type: COMMENT; Schema: augur_operations; Owner: augur
--

COMMENT ON TABLE augur_operations.worker_settings_facade IS 'For future use when we move all working tables to the augur_operations schema. ';


--
-- Name: working_commits; Type: TABLE; Schema: augur_operations; Owner: augur
--

CREATE TABLE augur_operations.working_commits (
    repos_id integer NOT NULL,
    working_commit character varying(40) DEFAULT 'NULL'::character varying
);


ALTER TABLE augur_operations.working_commits OWNER TO augur;

--
-- Name: TABLE working_commits; Type: COMMENT; Schema: augur_operations; Owner: augur
--

COMMENT ON TABLE augur_operations.working_commits IS 'For future use when we move all working tables to the augur_operations schema. ';


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: augur
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO augur;

--
-- Name: annotation_types_annotation_type_id_seq; Type: SEQUENCE; Schema: spdx; Owner: augur
--

CREATE SEQUENCE spdx.annotation_types_annotation_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE spdx.annotation_types_annotation_type_id_seq OWNER TO augur;

--
-- Name: annotation_types; Type: TABLE; Schema: spdx; Owner: augur
--

CREATE TABLE spdx.annotation_types (
    annotation_type_id integer DEFAULT nextval('spdx.annotation_types_annotation_type_id_seq'::regclass) NOT NULL,
    name character varying(255) NOT NULL
);


ALTER TABLE spdx.annotation_types OWNER TO augur;

--
-- Name: annotations_annotation_id_seq; Type: SEQUENCE; Schema: spdx; Owner: augur
--

CREATE SEQUENCE spdx.annotations_annotation_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE spdx.annotations_annotation_id_seq OWNER TO augur;

--
-- Name: annotations; Type: TABLE; Schema: spdx; Owner: augur
--

CREATE TABLE spdx.annotations (
    annotation_id integer DEFAULT nextval('spdx.annotations_annotation_id_seq'::regclass) NOT NULL,
    document_id integer NOT NULL,
    annotation_type_id integer NOT NULL,
    identifier_id integer NOT NULL,
    creator_id integer NOT NULL,
    created_ts timestamp(6) with time zone,
    comment text NOT NULL
);


ALTER TABLE spdx.annotations OWNER TO augur;

--
-- Name: augur_repo_map_map_id_seq; Type: SEQUENCE; Schema: spdx; Owner: augur
--

CREATE SEQUENCE spdx.augur_repo_map_map_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE spdx.augur_repo_map_map_id_seq OWNER TO augur;

--
-- Name: augur_repo_map; Type: TABLE; Schema: spdx; Owner: augur
--

CREATE TABLE spdx.augur_repo_map (
    map_id integer DEFAULT nextval('spdx.augur_repo_map_map_id_seq'::regclass) NOT NULL,
    dosocs_pkg_id integer,
    dosocs_pkg_name text,
    repo_id integer,
    repo_path text
);


ALTER TABLE spdx.augur_repo_map OWNER TO augur;

--
-- Name: creator_types_creator_type_id_seq; Type: SEQUENCE; Schema: spdx; Owner: augur
--

CREATE SEQUENCE spdx.creator_types_creator_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE spdx.creator_types_creator_type_id_seq OWNER TO augur;

--
-- Name: creator_types; Type: TABLE; Schema: spdx; Owner: augur
--

CREATE TABLE spdx.creator_types (
    creator_type_id integer DEFAULT nextval('spdx.creator_types_creator_type_id_seq'::regclass) NOT NULL,
    name character varying(255) NOT NULL
);


ALTER TABLE spdx.creator_types OWNER TO augur;

--
-- Name: creators_creator_id_seq; Type: SEQUENCE; Schema: spdx; Owner: augur
--

CREATE SEQUENCE spdx.creators_creator_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE spdx.creators_creator_id_seq OWNER TO augur;

--
-- Name: creators; Type: TABLE; Schema: spdx; Owner: augur
--

CREATE TABLE spdx.creators (
    creator_id integer DEFAULT nextval('spdx.creators_creator_id_seq'::regclass) NOT NULL,
    creator_type_id integer NOT NULL,
    name character varying(255) NOT NULL,
    email character varying(255) NOT NULL
);


ALTER TABLE spdx.creators OWNER TO augur;

--
-- Name: document_namespaces_document_namespace_id_seq; Type: SEQUENCE; Schema: spdx; Owner: augur
--

CREATE SEQUENCE spdx.document_namespaces_document_namespace_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE spdx.document_namespaces_document_namespace_id_seq OWNER TO augur;

--
-- Name: document_namespaces; Type: TABLE; Schema: spdx; Owner: augur
--

CREATE TABLE spdx.document_namespaces (
    document_namespace_id integer DEFAULT nextval('spdx.document_namespaces_document_namespace_id_seq'::regclass) NOT NULL,
    uri character varying(500) NOT NULL
);


ALTER TABLE spdx.document_namespaces OWNER TO augur;

--
-- Name: documents_document_id_seq; Type: SEQUENCE; Schema: spdx; Owner: augur
--

CREATE SEQUENCE spdx.documents_document_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE spdx.documents_document_id_seq OWNER TO augur;

--
-- Name: documents; Type: TABLE; Schema: spdx; Owner: augur
--

CREATE TABLE spdx.documents (
    document_id integer DEFAULT nextval('spdx.documents_document_id_seq'::regclass) NOT NULL,
    document_namespace_id integer NOT NULL,
    data_license_id integer NOT NULL,
    spdx_version character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    license_list_version character varying(255) NOT NULL,
    created_ts timestamp(6) with time zone NOT NULL,
    creator_comment text NOT NULL,
    document_comment text NOT NULL,
    package_id integer NOT NULL
);


ALTER TABLE spdx.documents OWNER TO augur;

--
-- Name: documents_creators_document_creator_id_seq; Type: SEQUENCE; Schema: spdx; Owner: augur
--

CREATE SEQUENCE spdx.documents_creators_document_creator_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE spdx.documents_creators_document_creator_id_seq OWNER TO augur;

--
-- Name: documents_creators; Type: TABLE; Schema: spdx; Owner: augur
--

CREATE TABLE spdx.documents_creators (
    document_creator_id integer DEFAULT nextval('spdx.documents_creators_document_creator_id_seq'::regclass) NOT NULL,
    document_id integer NOT NULL,
    creator_id integer NOT NULL
);


ALTER TABLE spdx.documents_creators OWNER TO augur;

--
-- Name: external_refs_external_ref_id_seq; Type: SEQUENCE; Schema: spdx; Owner: augur
--

CREATE SEQUENCE spdx.external_refs_external_ref_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE spdx.external_refs_external_ref_id_seq OWNER TO augur;

--
-- Name: external_refs; Type: TABLE; Schema: spdx; Owner: augur
--

CREATE TABLE spdx.external_refs (
    external_ref_id integer DEFAULT nextval('spdx.external_refs_external_ref_id_seq'::regclass) NOT NULL,
    document_id integer NOT NULL,
    document_namespace_id integer NOT NULL,
    id_string character varying(255) NOT NULL,
    sha256 character varying(64) NOT NULL
);


ALTER TABLE spdx.external_refs OWNER TO augur;

--
-- Name: file_contributors_file_contributor_id_seq; Type: SEQUENCE; Schema: spdx; Owner: augur
--

CREATE SEQUENCE spdx.file_contributors_file_contributor_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE spdx.file_contributors_file_contributor_id_seq OWNER TO augur;

--
-- Name: file_contributors; Type: TABLE; Schema: spdx; Owner: augur
--

CREATE TABLE spdx.file_contributors (
    file_contributor_id integer DEFAULT nextval('spdx.file_contributors_file_contributor_id_seq'::regclass) NOT NULL,
    file_id integer NOT NULL,
    contributor text NOT NULL
);


ALTER TABLE spdx.file_contributors OWNER TO augur;

--
-- Name: file_types; Type: TABLE; Schema: spdx; Owner: augur
--

CREATE TABLE spdx.file_types (
    file_type_id integer,
    name character varying(255) NOT NULL
);


ALTER TABLE spdx.file_types OWNER TO augur;

--
-- Name: file_types_file_type_id_seq; Type: SEQUENCE; Schema: spdx; Owner: augur
--

CREATE SEQUENCE spdx.file_types_file_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE spdx.file_types_file_type_id_seq OWNER TO augur;

--
-- Name: files_file_id_seq; Type: SEQUENCE; Schema: spdx; Owner: augur
--

CREATE SEQUENCE spdx.files_file_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE spdx.files_file_id_seq OWNER TO augur;

--
-- Name: files; Type: TABLE; Schema: spdx; Owner: augur
--

CREATE TABLE spdx.files (
    file_id integer DEFAULT nextval('spdx.files_file_id_seq'::regclass) NOT NULL,
    file_type_id integer,
    sha256 character varying(64) NOT NULL,
    copyright_text text,
    package_id integer,
    comment text NOT NULL,
    notice text NOT NULL
);


ALTER TABLE spdx.files OWNER TO augur;

--
-- Name: files_licenses_file_license_id_seq; Type: SEQUENCE; Schema: spdx; Owner: augur
--

CREATE SEQUENCE spdx.files_licenses_file_license_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE spdx.files_licenses_file_license_id_seq OWNER TO augur;

--
-- Name: files_licenses; Type: TABLE; Schema: spdx; Owner: augur
--

CREATE TABLE spdx.files_licenses (
    file_license_id integer DEFAULT nextval('spdx.files_licenses_file_license_id_seq'::regclass) NOT NULL,
    file_id integer NOT NULL,
    license_id integer NOT NULL,
    extracted_text text NOT NULL
);


ALTER TABLE spdx.files_licenses OWNER TO augur;

--
-- Name: files_scans_file_scan_id_seq; Type: SEQUENCE; Schema: spdx; Owner: augur
--

CREATE SEQUENCE spdx.files_scans_file_scan_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE spdx.files_scans_file_scan_id_seq OWNER TO augur;

--
-- Name: files_scans; Type: TABLE; Schema: spdx; Owner: augur
--

CREATE TABLE spdx.files_scans (
    file_scan_id integer DEFAULT nextval('spdx.files_scans_file_scan_id_seq'::regclass) NOT NULL,
    file_id integer NOT NULL,
    scanner_id integer NOT NULL
);


ALTER TABLE spdx.files_scans OWNER TO augur;

--
-- Name: identifiers_identifier_id_seq; Type: SEQUENCE; Schema: spdx; Owner: augur
--

CREATE SEQUENCE spdx.identifiers_identifier_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE spdx.identifiers_identifier_id_seq OWNER TO augur;

--
-- Name: identifiers; Type: TABLE; Schema: spdx; Owner: augur
--

CREATE TABLE spdx.identifiers (
    identifier_id integer DEFAULT nextval('spdx.identifiers_identifier_id_seq'::regclass) NOT NULL,
    document_namespace_id integer NOT NULL,
    id_string character varying(255) NOT NULL,
    document_id integer,
    package_id integer,
    package_file_id integer,
    CONSTRAINT ck_identifier_exactly_one CHECK ((((((document_id IS NOT NULL))::integer + ((package_id IS NOT NULL))::integer) + ((package_file_id IS NOT NULL))::integer) = 1))
);


ALTER TABLE spdx.identifiers OWNER TO augur;

--
-- Name: licenses_license_id_seq; Type: SEQUENCE; Schema: spdx; Owner: augur
--

CREATE SEQUENCE spdx.licenses_license_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE spdx.licenses_license_id_seq OWNER TO augur;

--
-- Name: licenses; Type: TABLE; Schema: spdx; Owner: augur
--

CREATE TABLE spdx.licenses (
    license_id integer DEFAULT nextval('spdx.licenses_license_id_seq'::regclass) NOT NULL,
    name character varying(255),
    short_name character varying(255) NOT NULL,
    cross_reference text NOT NULL,
    comment text NOT NULL,
    is_spdx_official boolean NOT NULL
);


ALTER TABLE spdx.licenses OWNER TO augur;

--
-- Name: packages_package_id_seq; Type: SEQUENCE; Schema: spdx; Owner: augur
--

CREATE SEQUENCE spdx.packages_package_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE spdx.packages_package_id_seq OWNER TO augur;

--
-- Name: packages; Type: TABLE; Schema: spdx; Owner: augur
--

CREATE TABLE spdx.packages (
    package_id integer DEFAULT nextval('spdx.packages_package_id_seq'::regclass) NOT NULL,
    name character varying(255) NOT NULL,
    version character varying(255) NOT NULL,
    file_name text NOT NULL,
    supplier_id integer,
    originator_id integer,
    download_location text,
    verification_code character varying(64) NOT NULL,
    ver_code_excluded_file_id integer,
    sha256 character varying(64),
    home_page text,
    source_info text NOT NULL,
    concluded_license_id integer,
    declared_license_id integer,
    license_comment text NOT NULL,
    copyright_text text,
    summary text NOT NULL,
    description text NOT NULL,
    comment text NOT NULL,
    dosocs2_dir_code character varying(64),
    CONSTRAINT uc_sha256_ds2_dir_code_exactly_one CHECK (((((sha256 IS NOT NULL))::integer + ((dosocs2_dir_code IS NOT NULL))::integer) = 1))
);


ALTER TABLE spdx.packages OWNER TO augur;

--
-- Name: packages_files_package_file_id_seq; Type: SEQUENCE; Schema: spdx; Owner: augur
--

CREATE SEQUENCE spdx.packages_files_package_file_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE spdx.packages_files_package_file_id_seq OWNER TO augur;

--
-- Name: packages_files; Type: TABLE; Schema: spdx; Owner: augur
--

CREATE TABLE spdx.packages_files (
    package_file_id integer DEFAULT nextval('spdx.packages_files_package_file_id_seq'::regclass) NOT NULL,
    package_id integer NOT NULL,
    file_id integer NOT NULL,
    concluded_license_id integer,
    license_comment text NOT NULL,
    file_name text NOT NULL
);


ALTER TABLE spdx.packages_files OWNER TO augur;

--
-- Name: packages_scans_package_scan_id_seq; Type: SEQUENCE; Schema: spdx; Owner: augur
--

CREATE SEQUENCE spdx.packages_scans_package_scan_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE spdx.packages_scans_package_scan_id_seq OWNER TO augur;

--
-- Name: packages_scans; Type: TABLE; Schema: spdx; Owner: augur
--

CREATE TABLE spdx.packages_scans (
    package_scan_id integer DEFAULT nextval('spdx.packages_scans_package_scan_id_seq'::regclass) NOT NULL,
    package_id integer NOT NULL,
    scanner_id integer NOT NULL
);


ALTER TABLE spdx.packages_scans OWNER TO augur;

--
-- Name: projects_package_id_seq; Type: SEQUENCE; Schema: spdx; Owner: augur
--

CREATE SEQUENCE spdx.projects_package_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE spdx.projects_package_id_seq OWNER TO augur;

--
-- Name: projects; Type: TABLE; Schema: spdx; Owner: augur
--

CREATE TABLE spdx.projects (
    package_id integer DEFAULT nextval('spdx.projects_package_id_seq'::regclass) NOT NULL,
    name text NOT NULL,
    homepage text NOT NULL,
    uri text NOT NULL
);


ALTER TABLE spdx.projects OWNER TO augur;

--
-- Name: relationship_types_relationship_type_id_seq; Type: SEQUENCE; Schema: spdx; Owner: augur
--

CREATE SEQUENCE spdx.relationship_types_relationship_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE spdx.relationship_types_relationship_type_id_seq OWNER TO augur;

--
-- Name: relationship_types; Type: TABLE; Schema: spdx; Owner: augur
--

CREATE TABLE spdx.relationship_types (
    relationship_type_id integer DEFAULT nextval('spdx.relationship_types_relationship_type_id_seq'::regclass) NOT NULL,
    name character varying(255) NOT NULL
);


ALTER TABLE spdx.relationship_types OWNER TO augur;

--
-- Name: relationships_relationship_id_seq; Type: SEQUENCE; Schema: spdx; Owner: augur
--

CREATE SEQUENCE spdx.relationships_relationship_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE spdx.relationships_relationship_id_seq OWNER TO augur;

--
-- Name: relationships; Type: TABLE; Schema: spdx; Owner: augur
--

CREATE TABLE spdx.relationships (
    relationship_id integer DEFAULT nextval('spdx.relationships_relationship_id_seq'::regclass) NOT NULL,
    left_identifier_id integer NOT NULL,
    right_identifier_id integer NOT NULL,
    relationship_type_id integer NOT NULL,
    relationship_comment text NOT NULL
);


ALTER TABLE spdx.relationships OWNER TO augur;

--
-- Name: sbom_scans; Type: TABLE; Schema: spdx; Owner: augur
--

CREATE TABLE spdx.sbom_scans (
    repo_id integer,
    sbom_scan json
);


ALTER TABLE spdx.sbom_scans OWNER TO augur;

--
-- Name: scanners_scanner_id_seq; Type: SEQUENCE; Schema: spdx; Owner: augur
--

CREATE SEQUENCE spdx.scanners_scanner_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE spdx.scanners_scanner_id_seq OWNER TO augur;

--
-- Name: scanners; Type: TABLE; Schema: spdx; Owner: augur
--

CREATE TABLE spdx.scanners (
    scanner_id integer DEFAULT nextval('spdx.scanners_scanner_id_seq'::regclass) NOT NULL,
    name character varying(255) NOT NULL
);


ALTER TABLE spdx.scanners OWNER TO augur;

--
-- Name: chaoss_user chaoss_id; Type: DEFAULT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.chaoss_user ALTER COLUMN chaoss_id SET DEFAULT nextval('augur_data.chaoss_user_chaoss_id_seq'::regclass);


--
-- Name: config id; Type: DEFAULT; Schema: augur_operations; Owner: augur
--

ALTER TABLE ONLY augur_operations.config ALTER COLUMN id SET DEFAULT nextval('augur_operations.config_id_seq'::regclass);


--
-- Name: subscription_types id; Type: DEFAULT; Schema: augur_operations; Owner: augur
--

ALTER TABLE ONLY augur_operations.subscription_types ALTER COLUMN id SET DEFAULT nextval('augur_operations.subscription_types_id_seq'::regclass);


--
-- Name: user_groups group_id; Type: DEFAULT; Schema: augur_operations; Owner: augur
--

ALTER TABLE ONLY augur_operations.user_groups ALTER COLUMN group_id SET DEFAULT nextval('augur_operations.user_groups_group_id_seq'::regclass);


--
-- Name: users user_id; Type: DEFAULT; Schema: augur_operations; Owner: augur
--

ALTER TABLE ONLY augur_operations.users ALTER COLUMN user_id SET DEFAULT nextval('augur_operations.users_user_id_seq'::regclass);


--
-- Name: augur_data.repo_insights_ri_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data."augur_data.repo_insights_ri_id_seq"', 25430, false);


--
-- Name: chaoss_metric_status_cms_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.chaoss_metric_status_cms_id_seq', 1, false);


--
-- Name: chaoss_user_chaoss_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.chaoss_user_chaoss_id_seq', 1, false);


--
-- Name: commit_comment_ref_cmt_comment_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.commit_comment_ref_cmt_comment_id_seq', 25430, false);


--
-- Name: commit_parents_parent_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.commit_parents_parent_id_seq', 25430, false);


--
-- Name: commits_cmt_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.commits_cmt_id_seq', 25430, false);


--
-- Name: contributor_affiliations_ca_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.contributor_affiliations_ca_id_seq', 25430, false);


--
-- Name: contributor_repo_cntrb_repo_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.contributor_repo_cntrb_repo_id_seq', 1, false);


--
-- Name: contributors_aliases_cntrb_a_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.contributors_aliases_cntrb_a_id_seq', 25430, false);


--
-- Name: contributors_aliases_cntrb_alias_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.contributors_aliases_cntrb_alias_id_seq', 1, false);


--
-- Name: contributors_cntrb_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.contributors_cntrb_id_seq', 25430, false);


--
-- Name: contributors_history_cntrb_history_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.contributors_history_cntrb_history_id_seq', 25430, false);


--
-- Name: discourse_insights_msg_discourse_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.discourse_insights_msg_discourse_id_seq', 1, false);


--
-- Name: discourse_insights_msg_discourse_id_seq1; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.discourse_insights_msg_discourse_id_seq1', 1, false);


--
-- Name: issue_assignees_issue_assignee_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.issue_assignees_issue_assignee_id_seq', 1, false);


--
-- Name: issue_events_event_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.issue_events_event_id_seq', 25430, false);


--
-- Name: issue_labels_issue_label_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.issue_labels_issue_label_id_seq', 25430, false);


--
-- Name: issue_message_ref_issue_msg_ref_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.issue_message_ref_issue_msg_ref_id_seq', 25430, false);


--
-- Name: issue_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.issue_seq', 31000, false);


--
-- Name: libraries_library_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.libraries_library_id_seq', 25430, false);


--
-- Name: library_dependencies_lib_dependency_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.library_dependencies_lib_dependency_id_seq', 25430, false);


--
-- Name: library_version_library_version_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.library_version_library_version_id_seq', 25430, false);


--
-- Name: lstm_anomaly_models_model_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.lstm_anomaly_models_model_id_seq', 1, false);


--
-- Name: lstm_anomaly_results_result_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.lstm_anomaly_results_result_id_seq', 1, false);


--
-- Name: message_analysis_msg_analysis_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.message_analysis_msg_analysis_id_seq', 1, false);


--
-- Name: message_analysis_summary_msg_summary_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.message_analysis_summary_msg_summary_id_seq', 1, false);


--
-- Name: message_msg_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.message_msg_id_seq', 25430, false);


--
-- Name: message_sentiment_msg_analysis_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.message_sentiment_msg_analysis_id_seq', 1, false);


--
-- Name: message_sentiment_summary_msg_summary_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.message_sentiment_summary_msg_summary_id_seq', 1, false);


--
-- Name: platform_pltfrm_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.platform_pltfrm_id_seq', 25430, false);


--
-- Name: pull_request_analysis_pull_request_analysis_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.pull_request_analysis_pull_request_analysis_id_seq', 1, false);


--
-- Name: pull_request_assignees_pr_assignee_map_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.pull_request_assignees_pr_assignee_map_id_seq', 25430, false);


--
-- Name: pull_request_commits_pr_cmt_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.pull_request_commits_pr_cmt_id_seq', 1, false);


--
-- Name: pull_request_events_pr_event_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.pull_request_events_pr_event_id_seq', 25430, false);


--
-- Name: pull_request_files_pr_file_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.pull_request_files_pr_file_id_seq', 25150, false);


--
-- Name: pull_request_labels_pr_label_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.pull_request_labels_pr_label_id_seq', 25430, false);


--
-- Name: pull_request_message_ref_pr_msg_ref_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.pull_request_message_ref_pr_msg_ref_id_seq', 25430, false);


--
-- Name: pull_request_meta_pr_repo_meta_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.pull_request_meta_pr_repo_meta_id_seq', 25430, false);


--
-- Name: pull_request_repo_pr_repo_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.pull_request_repo_pr_repo_id_seq', 25430, false);


--
-- Name: pull_request_review_message_ref_pr_review_msg_ref_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.pull_request_review_message_ref_pr_review_msg_ref_id_seq', 1, false);


--
-- Name: pull_request_reviewers_pr_reviewer_map_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.pull_request_reviewers_pr_reviewer_map_id_seq', 25430, false);


--
-- Name: pull_request_reviews_pr_review_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.pull_request_reviews_pr_review_id_seq', 1, false);


--
-- Name: pull_request_teams_pr_team_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.pull_request_teams_pr_team_id_seq', 25430, false);


--
-- Name: pull_requests_pull_request_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.pull_requests_pull_request_id_seq', 25430, false);


--
-- Name: releases_release_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.releases_release_id_seq', 1, false);


--
-- Name: repo_badging_badge_collection_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.repo_badging_badge_collection_id_seq', 25012, false);


--
-- Name: repo_clones_data_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.repo_clones_data_id_seq', 1, false);


--
-- Name: repo_cluster_messages_msg_cluster_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.repo_cluster_messages_msg_cluster_id_seq', 1, false);


--
-- Name: repo_dependencies_repo_dependencies_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.repo_dependencies_repo_dependencies_id_seq', 1, false);


--
-- Name: repo_deps_libyear_repo_deps_libyear_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.repo_deps_libyear_repo_deps_libyear_id_seq', 1, false);


--
-- Name: repo_deps_scorecard_repo_deps_scorecard_id_seq1; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.repo_deps_scorecard_repo_deps_scorecard_id_seq1', 1, false);


--
-- Name: repo_group_insights_rgi_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.repo_group_insights_rgi_id_seq', 25430, false);


--
-- Name: repo_groups_list_serve_rgls_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.repo_groups_list_serve_rgls_id_seq', 25430, false);


--
-- Name: repo_groups_repo_group_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.repo_groups_repo_group_id_seq', 25430, true);


--
-- Name: repo_info_repo_info_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.repo_info_repo_info_id_seq', 25430, false);


--
-- Name: repo_insights_records_ri_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.repo_insights_records_ri_id_seq', 1, false);


--
-- Name: repo_insights_ri_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.repo_insights_ri_id_seq', 1, false);


--
-- Name: repo_labor_repo_labor_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.repo_labor_repo_labor_id_seq', 25430, false);


--
-- Name: repo_meta_rmeta_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.repo_meta_rmeta_id_seq', 25430, false);


--
-- Name: repo_repo_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.repo_repo_id_seq', 25480, false);


--
-- Name: repo_sbom_scans_rsb_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.repo_sbom_scans_rsb_id_seq', 25430, false);


--
-- Name: repo_stats_rstat_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.repo_stats_rstat_id_seq', 25430, false);


--
-- Name: repo_test_coverage_repo_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.repo_test_coverage_repo_id_seq', 1, false);


--
-- Name: repo_topic_repo_topic_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.repo_topic_repo_topic_id_seq', 1, false);


--
-- Name: topic_words_topic_words_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.topic_words_topic_words_id_seq', 1, false);


--
-- Name: unresolved_commit_emails_email_unresolved_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.unresolved_commit_emails_email_unresolved_id_seq', 1, false);


--
-- Name: utility_log_id_seq; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.utility_log_id_seq', 1, false);


--
-- Name: utility_log_id_seq1; Type: SEQUENCE SET; Schema: augur_data; Owner: augur
--

SELECT pg_catalog.setval('augur_data.utility_log_id_seq1', 1, false);


--
-- Name: affiliations_corp_id_seq; Type: SEQUENCE SET; Schema: augur_operations; Owner: augur
--

SELECT pg_catalog.setval('augur_operations.affiliations_corp_id_seq', 620000, false);


--
-- Name: augur_settings_id_seq; Type: SEQUENCE SET; Schema: augur_operations; Owner: augur
--

SELECT pg_catalog.setval('augur_operations.augur_settings_id_seq', 1, false);


--
-- Name: config_id_seq; Type: SEQUENCE SET; Schema: augur_operations; Owner: augur
--

SELECT pg_catalog.setval('augur_operations.config_id_seq', 49, true);


--
-- Name: gh_worker_history_history_id_seq; Type: SEQUENCE SET; Schema: augur_operations; Owner: augur
--

SELECT pg_catalog.setval('augur_operations.gh_worker_history_history_id_seq', 15000, false);


--
-- Name: subscription_types_id_seq; Type: SEQUENCE SET; Schema: augur_operations; Owner: augur
--

SELECT pg_catalog.setval('augur_operations.subscription_types_id_seq', 1, false);


--
-- Name: user_groups_group_id_seq; Type: SEQUENCE SET; Schema: augur_operations; Owner: augur
--

SELECT pg_catalog.setval('augur_operations.user_groups_group_id_seq', 2, false);


--
-- Name: users_user_id_seq; Type: SEQUENCE SET; Schema: augur_operations; Owner: augur
--

SELECT pg_catalog.setval('augur_operations.users_user_id_seq', 2, false);


--
-- Name: worker_oauth_oauth_id_seq; Type: SEQUENCE SET; Schema: augur_operations; Owner: augur
--

SELECT pg_catalog.setval('augur_operations.worker_oauth_oauth_id_seq', 1000, false);


--
-- Name: annotation_types_annotation_type_id_seq; Type: SEQUENCE SET; Schema: spdx; Owner: augur
--

SELECT pg_catalog.setval('spdx.annotation_types_annotation_type_id_seq', 1, false);


--
-- Name: annotations_annotation_id_seq; Type: SEQUENCE SET; Schema: spdx; Owner: augur
--

SELECT pg_catalog.setval('spdx.annotations_annotation_id_seq', 1, false);


--
-- Name: augur_repo_map_map_id_seq; Type: SEQUENCE SET; Schema: spdx; Owner: augur
--

SELECT pg_catalog.setval('spdx.augur_repo_map_map_id_seq', 1, false);


--
-- Name: creator_types_creator_type_id_seq; Type: SEQUENCE SET; Schema: spdx; Owner: augur
--

SELECT pg_catalog.setval('spdx.creator_types_creator_type_id_seq', 1, false);


--
-- Name: creators_creator_id_seq; Type: SEQUENCE SET; Schema: spdx; Owner: augur
--

SELECT pg_catalog.setval('spdx.creators_creator_id_seq', 1, false);


--
-- Name: document_namespaces_document_namespace_id_seq; Type: SEQUENCE SET; Schema: spdx; Owner: augur
--

SELECT pg_catalog.setval('spdx.document_namespaces_document_namespace_id_seq', 1, false);


--
-- Name: documents_creators_document_creator_id_seq; Type: SEQUENCE SET; Schema: spdx; Owner: augur
--

SELECT pg_catalog.setval('spdx.documents_creators_document_creator_id_seq', 1, false);


--
-- Name: documents_document_id_seq; Type: SEQUENCE SET; Schema: spdx; Owner: augur
--

SELECT pg_catalog.setval('spdx.documents_document_id_seq', 1, false);


--
-- Name: external_refs_external_ref_id_seq; Type: SEQUENCE SET; Schema: spdx; Owner: augur
--

SELECT pg_catalog.setval('spdx.external_refs_external_ref_id_seq', 1, false);


--
-- Name: file_contributors_file_contributor_id_seq; Type: SEQUENCE SET; Schema: spdx; Owner: augur
--

SELECT pg_catalog.setval('spdx.file_contributors_file_contributor_id_seq', 1, false);


--
-- Name: file_types_file_type_id_seq; Type: SEQUENCE SET; Schema: spdx; Owner: augur
--

SELECT pg_catalog.setval('spdx.file_types_file_type_id_seq', 1, false);


--
-- Name: files_file_id_seq; Type: SEQUENCE SET; Schema: spdx; Owner: augur
--

SELECT pg_catalog.setval('spdx.files_file_id_seq', 1, false);


--
-- Name: files_licenses_file_license_id_seq; Type: SEQUENCE SET; Schema: spdx; Owner: augur
--

SELECT pg_catalog.setval('spdx.files_licenses_file_license_id_seq', 1, false);


--
-- Name: files_scans_file_scan_id_seq; Type: SEQUENCE SET; Schema: spdx; Owner: augur
--

SELECT pg_catalog.setval('spdx.files_scans_file_scan_id_seq', 1, false);


--
-- Name: identifiers_identifier_id_seq; Type: SEQUENCE SET; Schema: spdx; Owner: augur
--

SELECT pg_catalog.setval('spdx.identifiers_identifier_id_seq', 1, false);


--
-- Name: licenses_license_id_seq; Type: SEQUENCE SET; Schema: spdx; Owner: augur
--

SELECT pg_catalog.setval('spdx.licenses_license_id_seq', 1, false);


--
-- Name: packages_files_package_file_id_seq; Type: SEQUENCE SET; Schema: spdx; Owner: augur
--

SELECT pg_catalog.setval('spdx.packages_files_package_file_id_seq', 1, false);


--
-- Name: packages_package_id_seq; Type: SEQUENCE SET; Schema: spdx; Owner: augur
--

SELECT pg_catalog.setval('spdx.packages_package_id_seq', 1, false);


--
-- Name: packages_scans_package_scan_id_seq; Type: SEQUENCE SET; Schema: spdx; Owner: augur
--

SELECT pg_catalog.setval('spdx.packages_scans_package_scan_id_seq', 1, false);


--
-- Name: projects_package_id_seq; Type: SEQUENCE SET; Schema: spdx; Owner: augur
--

SELECT pg_catalog.setval('spdx.projects_package_id_seq', 1, false);


--
-- Name: relationship_types_relationship_type_id_seq; Type: SEQUENCE SET; Schema: spdx; Owner: augur
--

SELECT pg_catalog.setval('spdx.relationship_types_relationship_type_id_seq', 1, false);


--
-- Name: relationships_relationship_id_seq; Type: SEQUENCE SET; Schema: spdx; Owner: augur
--

SELECT pg_catalog.setval('spdx.relationships_relationship_id_seq', 1, false);


--
-- Name: scanners_scanner_id_seq; Type: SEQUENCE SET; Schema: spdx; Owner: augur
--

SELECT pg_catalog.setval('spdx.scanners_scanner_id_seq', 1, false);


--
-- Name: contributors GH-UNIQUE-C; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.contributors
    ADD CONSTRAINT "GH-UNIQUE-C" UNIQUE (gh_login) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: contributors GL-UNIQUE-B; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.contributors
    ADD CONSTRAINT "GL-UNIQUE-B" UNIQUE (gl_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: contributors GL-UNIQUE-C; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.contributors
    ADD CONSTRAINT "GL-UNIQUE-C" UNIQUE (gl_username) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: contributors GL-cntrb-LOGIN-UNIQUE; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.contributors
    ADD CONSTRAINT "GL-cntrb-LOGIN-UNIQUE" UNIQUE (cntrb_login);


--
-- Name: pull_request_assignees assigniees-unique; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_assignees
    ADD CONSTRAINT "assigniees-unique" UNIQUE (pull_request_id, pr_assignee_src_id);


--
-- Name: chaoss_metric_status chaoss_metric_status_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.chaoss_metric_status
    ADD CONSTRAINT chaoss_metric_status_pkey PRIMARY KEY (cms_id);


--
-- Name: chaoss_user chaoss_unique_email_key; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.chaoss_user
    ADD CONSTRAINT chaoss_unique_email_key UNIQUE (chaoss_email);


--
-- Name: chaoss_user chaoss_user_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.chaoss_user
    ADD CONSTRAINT chaoss_user_pkey PRIMARY KEY (chaoss_id);


--
-- Name: contributor_repo cntrb_repo_id_key; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.contributor_repo
    ADD CONSTRAINT cntrb_repo_id_key PRIMARY KEY (cntrb_repo_id);


--
-- Name: commit_comment_ref commit_comment_ref_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.commit_comment_ref
    ADD CONSTRAINT commit_comment_ref_pkey PRIMARY KEY (cmt_comment_id);


--
-- Name: commit_parents commit_parents_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.commit_parents
    ADD CONSTRAINT commit_parents_pkey PRIMARY KEY (cmt_id, parent_id);


--
-- Name: commit_comment_ref commitcomment; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.commit_comment_ref
    ADD CONSTRAINT commitcomment UNIQUE (cmt_comment_src_id);


--
-- Name: commits commits_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.commits
    ADD CONSTRAINT commits_pkey PRIMARY KEY (cmt_id);


--
-- Name: contributors_aliases contributor-alias-unique; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.contributors_aliases
    ADD CONSTRAINT "contributor-alias-unique" UNIQUE (alias_email);


--
-- Name: contributor_affiliations contributor_affiliations_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.contributor_affiliations
    ADD CONSTRAINT contributor_affiliations_pkey PRIMARY KEY (ca_id);


--
-- Name: contributors contributors-pk; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.contributors
    ADD CONSTRAINT "contributors-pk" PRIMARY KEY (cntrb_id);


--
-- Name: contributors_aliases contributors_aliases_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.contributors_aliases
    ADD CONSTRAINT contributors_aliases_pkey PRIMARY KEY (cntrb_alias_id);


--
-- Name: repo_dependencies deps-insert-unique; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_dependencies
    ADD CONSTRAINT "deps-insert-unique" UNIQUE (repo_id, dep_name, data_collection_date);


--
-- Name: repo_deps_libyear deps-libyear-insert-unique; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_deps_libyear
    ADD CONSTRAINT "deps-libyear-insert-unique" UNIQUE (repo_id, name, data_collection_date);


--
-- Name: repo_deps_scorecard deps-scorecard-insert-unique; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_deps_scorecard
    ADD CONSTRAINT "deps-scorecard-insert-unique" UNIQUE (repo_id, name);


--
-- Name: discourse_insights discourse_insights_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.discourse_insights
    ADD CONSTRAINT discourse_insights_pkey PRIMARY KEY (msg_discourse_id);


--
-- Name: contributor_repo eventer; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.contributor_repo
    ADD CONSTRAINT eventer UNIQUE (event_id, tool_version);


--
-- Name: exclude exclude_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.exclude
    ADD CONSTRAINT exclude_pkey PRIMARY KEY (id);


--
-- Name: issue_assignees issue-assignee-insert-unique; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.issue_assignees
    ADD CONSTRAINT "issue-assignee-insert-unique" UNIQUE (issue_assignee_src_id, issue_id);


--
-- Name: issues issue-insert-unique; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.issues
    ADD CONSTRAINT "issue-insert-unique" UNIQUE (issue_url);


--
-- Name: issue_message_ref issue-message-ref-insert-unique; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.issue_message_ref
    ADD CONSTRAINT "issue-message-ref-insert-unique" UNIQUE (issue_msg_ref_src_comment_id, issue_id);


--
-- Name: issue_assignees issue_assignees_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.issue_assignees
    ADD CONSTRAINT issue_assignees_pkey PRIMARY KEY (issue_assignee_id);


--
-- Name: issue_events issue_events_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.issue_events
    ADD CONSTRAINT issue_events_pkey PRIMARY KEY (event_id);


--
-- Name: issue_labels issue_labels_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.issue_labels
    ADD CONSTRAINT issue_labels_pkey PRIMARY KEY (issue_label_id);


--
-- Name: issue_message_ref issue_message_ref_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.issue_message_ref
    ADD CONSTRAINT issue_message_ref_pkey PRIMARY KEY (issue_msg_ref_id);


--
-- Name: issues issues_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.issues
    ADD CONSTRAINT issues_pkey PRIMARY KEY (issue_id);


--
-- Name: libraries libraries_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.libraries
    ADD CONSTRAINT libraries_pkey PRIMARY KEY (library_id);


--
-- Name: library_dependencies library_dependencies_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.library_dependencies
    ADD CONSTRAINT library_dependencies_pkey PRIMARY KEY (lib_dependency_id);


--
-- Name: library_version library_version_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.library_version
    ADD CONSTRAINT library_version_pkey PRIMARY KEY (library_version_id);


--
-- Name: lstm_anomaly_models lstm_anomaly_models_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.lstm_anomaly_models
    ADD CONSTRAINT lstm_anomaly_models_pkey PRIMARY KEY (model_id);


--
-- Name: lstm_anomaly_results lstm_anomaly_results_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.lstm_anomaly_results
    ADD CONSTRAINT lstm_anomaly_results_pkey PRIMARY KEY (result_id);


--
-- Name: message message-insert-unique; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.message
    ADD CONSTRAINT "message-insert-unique" UNIQUE (platform_msg_id);


--
-- Name: message_analysis message_analysis_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.message_analysis
    ADD CONSTRAINT message_analysis_pkey PRIMARY KEY (msg_analysis_id);


--
-- Name: message_analysis_summary message_analysis_summary_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.message_analysis_summary
    ADD CONSTRAINT message_analysis_summary_pkey PRIMARY KEY (msg_summary_id);


--
-- Name: message message_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.message
    ADD CONSTRAINT message_pkey PRIMARY KEY (msg_id);


--
-- Name: message_sentiment message_sentiment_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.message_sentiment
    ADD CONSTRAINT message_sentiment_pkey PRIMARY KEY (msg_analysis_id);


--
-- Name: message_sentiment_summary message_sentiment_summary_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.message_sentiment_summary
    ADD CONSTRAINT message_sentiment_summary_pkey PRIMARY KEY (msg_summary_id);


--
-- Name: pull_request_events pr-unqiue-event; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_events
    ADD CONSTRAINT "pr-unqiue-event" UNIQUE (node_id);


--
-- Name: pull_request_commits pr_commit_nk; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_commits
    ADD CONSTRAINT pr_commit_nk UNIQUE (pull_request_id, repo_id, pr_cmt_sha);


--
-- Name: pull_request_events pr_events_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_events
    ADD CONSTRAINT pr_events_pkey PRIMARY KEY (pr_event_id);


--
-- Name: pull_request_review_message_ref pr_review_msg_ref_id; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_review_message_ref
    ADD CONSTRAINT pr_review_msg_ref_id PRIMARY KEY (pr_review_msg_ref_id);


--
-- Name: pull_request_reviews pr_review_unique; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_reviews
    ADD CONSTRAINT pr_review_unique UNIQUE (pr_review_src_id);


--
-- Name: pull_request_files prfiles_unique; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_files
    ADD CONSTRAINT prfiles_unique UNIQUE (pull_request_id, repo_id, pr_file_path);


--
-- Name: pull_requests pull-request-insert-unique; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_requests
    ADD CONSTRAINT "pull-request-insert-unique" UNIQUE (pr_url);


--
-- Name: pull_request_message_ref pull-request-message-ref-insert-unique; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_message_ref
    ADD CONSTRAINT "pull-request-message-ref-insert-unique" UNIQUE (pr_message_ref_src_comment_id, pull_request_id);


--
-- Name: pull_request_meta pull-request-meta-insert-unique; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_meta
    ADD CONSTRAINT "pull-request-meta-insert-unique" UNIQUE (pull_request_id, pr_head_or_base, pr_sha);


--
-- Name: pull_request_review_message_ref pull-request-review-message-ref-insert-unique; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_review_message_ref
    ADD CONSTRAINT "pull-request-review-message-ref-insert-unique" UNIQUE (pr_review_msg_src_id);


--
-- Name: pull_request_analysis pull_request_analysis_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_analysis
    ADD CONSTRAINT pull_request_analysis_pkey PRIMARY KEY (pull_request_analysis_id);


--
-- Name: pull_request_assignees pull_request_assignees_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_assignees
    ADD CONSTRAINT pull_request_assignees_pkey PRIMARY KEY (pr_assignee_map_id);


--
-- Name: pull_request_commits pull_request_commits_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_commits
    ADD CONSTRAINT pull_request_commits_pkey PRIMARY KEY (pr_cmt_id);


--
-- Name: pull_request_files pull_request_files_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_files
    ADD CONSTRAINT pull_request_files_pkey PRIMARY KEY (pr_file_id);


--
-- Name: pull_request_labels pull_request_labels_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_labels
    ADD CONSTRAINT pull_request_labels_pkey PRIMARY KEY (pr_label_id);


--
-- Name: pull_request_message_ref pull_request_message_ref_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_message_ref
    ADD CONSTRAINT pull_request_message_ref_pkey PRIMARY KEY (pr_msg_ref_id);


--
-- Name: pull_request_meta pull_request_meta_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_meta
    ADD CONSTRAINT pull_request_meta_pkey PRIMARY KEY (pr_repo_meta_id);


--
-- Name: pull_request_repo pull_request_repo_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_repo
    ADD CONSTRAINT pull_request_repo_pkey PRIMARY KEY (pr_repo_id);


--
-- Name: pull_request_reviews pull_request_review_id; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_reviews
    ADD CONSTRAINT pull_request_review_id PRIMARY KEY (pr_review_id);


--
-- Name: pull_request_reviewers pull_request_reviewers_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_reviewers
    ADD CONSTRAINT pull_request_reviewers_pkey PRIMARY KEY (pr_reviewer_map_id);


--
-- Name: pull_request_teams pull_request_teams_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_teams
    ADD CONSTRAINT pull_request_teams_pkey PRIMARY KEY (pr_team_id);


--
-- Name: pull_requests pull_requests_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_requests
    ADD CONSTRAINT pull_requests_pkey PRIMARY KEY (pull_request_id);


--
-- Name: releases releases_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.releases
    ADD CONSTRAINT releases_pkey PRIMARY KEY (release_id);


--
-- Name: repo_badging repo_badging_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_badging
    ADD CONSTRAINT repo_badging_pkey PRIMARY KEY (badge_collection_id);


--
-- Name: repo_clones_data repo_clones_data_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_clones_data
    ADD CONSTRAINT repo_clones_data_pkey PRIMARY KEY (repo_clone_data_id);


--
-- Name: repo_cluster_messages repo_cluster_messages_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_cluster_messages
    ADD CONSTRAINT repo_cluster_messages_pkey PRIMARY KEY (msg_cluster_id);


--
-- Name: repo_dependencies repo_dependencies_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_dependencies
    ADD CONSTRAINT repo_dependencies_pkey PRIMARY KEY (repo_dependencies_id);


--
-- Name: repo_deps_libyear repo_deps_libyear_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_deps_libyear
    ADD CONSTRAINT repo_deps_libyear_pkey PRIMARY KEY (repo_deps_libyear_id);


--
-- Name: repo_deps_scorecard repo_deps_scorecard_pkey1; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_deps_scorecard
    ADD CONSTRAINT repo_deps_scorecard_pkey1 PRIMARY KEY (repo_deps_scorecard_id);


--
-- Name: repo repo_git-unique; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo
    ADD CONSTRAINT "repo_git-unique" UNIQUE (repo_git);


--
-- Name: repo_group_insights repo_group_insights_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_group_insights
    ADD CONSTRAINT repo_group_insights_pkey PRIMARY KEY (rgi_id);


--
-- Name: repo_groups_list_serve repo_groups_list_serve_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_groups_list_serve
    ADD CONSTRAINT repo_groups_list_serve_pkey PRIMARY KEY (rgls_id);


--
-- Name: repo_info repo_info_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_info
    ADD CONSTRAINT repo_info_pkey PRIMARY KEY (repo_info_id);


--
-- Name: repo_insights repo_insights_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_insights
    ADD CONSTRAINT repo_insights_pkey PRIMARY KEY (ri_id);


--
-- Name: repo_insights_records repo_insights_records_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_insights_records
    ADD CONSTRAINT repo_insights_records_pkey PRIMARY KEY (ri_id);


--
-- Name: repo_labor repo_labor_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_labor
    ADD CONSTRAINT repo_labor_pkey PRIMARY KEY (repo_labor_id);


--
-- Name: repo_meta repo_meta_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_meta
    ADD CONSTRAINT repo_meta_pkey PRIMARY KEY (rmeta_id, repo_id);


--
-- Name: repo_sbom_scans repo_sbom_scans_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_sbom_scans
    ADD CONSTRAINT repo_sbom_scans_pkey PRIMARY KEY (rsb_id);


--
-- Name: repo_stats repo_stats_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_stats
    ADD CONSTRAINT repo_stats_pkey PRIMARY KEY (rstat_id, repo_id);


--
-- Name: repo_test_coverage repo_test_coverage_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_test_coverage
    ADD CONSTRAINT repo_test_coverage_pkey PRIMARY KEY (repo_id);


--
-- Name: repo_topic repo_topic_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_topic
    ADD CONSTRAINT repo_topic_pkey PRIMARY KEY (repo_topic_id);


--
-- Name: repo repounique; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo
    ADD CONSTRAINT repounique PRIMARY KEY (repo_id);


--
-- Name: repo_groups rgid; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_groups
    ADD CONSTRAINT rgid PRIMARY KEY (repo_group_id);


--
-- Name: repo_groups_list_serve rglistserve; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_groups_list_serve
    ADD CONSTRAINT rglistserve UNIQUE (rgls_id, repo_group_id);


--
-- Name: repo_labor rl-unique; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_labor
    ADD CONSTRAINT "rl-unique" UNIQUE (repo_id, rl_analysis_date, file_path, file_name) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: settings settings_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.settings
    ADD CONSTRAINT settings_pkey PRIMARY KEY (id);


--
-- Name: platform theplat; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.platform
    ADD CONSTRAINT theplat PRIMARY KEY (pltfrm_id);


--
-- Name: topic_words topic_words_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.topic_words
    ADD CONSTRAINT topic_words_pkey PRIMARY KEY (topic_words_id);


--
-- Name: issues unique-issue; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.issues
    ADD CONSTRAINT "unique-issue" UNIQUE (repo_id, gh_issue_id);


--
-- Name: pull_requests unique-pr; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_requests
    ADD CONSTRAINT "unique-pr" UNIQUE (repo_id, pr_src_id);


--
-- Name: pull_request_events unique-pr-event-id; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_events
    ADD CONSTRAINT "unique-pr-event-id" UNIQUE (platform_id, node_id);


--
-- Name: pull_request_labels unique-pr-src-label-id; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_labels
    ADD CONSTRAINT "unique-pr-src-label-id" UNIQUE (pr_src_id, pull_request_id);


--
-- Name: pull_requests unique-prx; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_requests
    ADD CONSTRAINT "unique-prx" UNIQUE (repo_id, pr_src_id);


--
-- Name: contributor_affiliations unique_domain; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.contributor_affiliations
    ADD CONSTRAINT unique_domain UNIQUE (ca_domain);


--
-- Name: CONSTRAINT unique_domain ON contributor_affiliations; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON CONSTRAINT unique_domain ON augur_data.contributor_affiliations IS 'Only one row should exist for any given top level domain or subdomain. ';


--
-- Name: issue_events unique_event_id_key; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.issue_events
    ADD CONSTRAINT unique_event_id_key UNIQUE (issue_id, issue_event_src_id);


--
-- Name: CONSTRAINT unique_event_id_key ON issue_events; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON CONSTRAINT unique_event_id_key ON augur_data.issue_events IS 'Natural key for issue events. ';


--
-- Name: issue_labels unique_issue_label; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.issue_labels
    ADD CONSTRAINT unique_issue_label UNIQUE (label_src_id, issue_id);


--
-- Name: pull_request_reviewers unique_pr_src_reviewer_key; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_reviewers
    ADD CONSTRAINT unique_pr_src_reviewer_key UNIQUE (pull_request_id, pr_reviewer_src_id);


--
-- Name: unresolved_commit_emails unresolved_commit_emails_email_key; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.unresolved_commit_emails
    ADD CONSTRAINT unresolved_commit_emails_email_key UNIQUE (email);


--
-- Name: unresolved_commit_emails unresolved_commit_emails_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.unresolved_commit_emails
    ADD CONSTRAINT unresolved_commit_emails_pkey PRIMARY KEY (email_unresolved_id);


--
-- Name: utility_log utility_log_pkey; Type: CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.utility_log
    ADD CONSTRAINT utility_log_pkey PRIMARY KEY (id);


--
-- Name: augur_settings augur_settings_pkey; Type: CONSTRAINT; Schema: augur_operations; Owner: augur
--

ALTER TABLE ONLY augur_operations.augur_settings
    ADD CONSTRAINT augur_settings_pkey PRIMARY KEY (id);


--
-- Name: client_applications client_applications_pkey; Type: CONSTRAINT; Schema: augur_operations; Owner: augur
--

ALTER TABLE ONLY augur_operations.client_applications
    ADD CONSTRAINT client_applications_pkey PRIMARY KEY (id);


--
-- Name: collection_status collection_status_pkey; Type: CONSTRAINT; Schema: augur_operations; Owner: augur
--

ALTER TABLE ONLY augur_operations.collection_status
    ADD CONSTRAINT collection_status_pkey PRIMARY KEY (repo_id);


--
-- Name: config config_pkey; Type: CONSTRAINT; Schema: augur_operations; Owner: augur
--

ALTER TABLE ONLY augur_operations.config
    ADD CONSTRAINT config_pkey PRIMARY KEY (id);


--
-- Name: worker_history history_pkey; Type: CONSTRAINT; Schema: augur_operations; Owner: augur
--

ALTER TABLE ONLY augur_operations.worker_history
    ADD CONSTRAINT history_pkey PRIMARY KEY (history_id);


--
-- Name: worker_job job_pkey; Type: CONSTRAINT; Schema: augur_operations; Owner: augur
--

ALTER TABLE ONLY augur_operations.worker_job
    ADD CONSTRAINT job_pkey PRIMARY KEY (job_model);


--
-- Name: refresh_tokens refresh_token_user_session_token_id_unique; Type: CONSTRAINT; Schema: augur_operations; Owner: augur
--

ALTER TABLE ONLY augur_operations.refresh_tokens
    ADD CONSTRAINT refresh_token_user_session_token_id_unique UNIQUE (user_session_token);


--
-- Name: refresh_tokens refresh_tokens_pkey; Type: CONSTRAINT; Schema: augur_operations; Owner: augur
--

ALTER TABLE ONLY augur_operations.refresh_tokens
    ADD CONSTRAINT refresh_tokens_pkey PRIMARY KEY (id);


--
-- Name: worker_settings_facade settings_pkey; Type: CONSTRAINT; Schema: augur_operations; Owner: augur
--

ALTER TABLE ONLY augur_operations.worker_settings_facade
    ADD CONSTRAINT settings_pkey PRIMARY KEY (id);


--
-- Name: subscription_types subscription_type_title_unique; Type: CONSTRAINT; Schema: augur_operations; Owner: augur
--

ALTER TABLE ONLY augur_operations.subscription_types
    ADD CONSTRAINT subscription_type_title_unique UNIQUE (name);


--
-- Name: subscription_types subscription_types_pkey; Type: CONSTRAINT; Schema: augur_operations; Owner: augur
--

ALTER TABLE ONLY augur_operations.subscription_types
    ADD CONSTRAINT subscription_types_pkey PRIMARY KEY (id);


--
-- Name: subscriptions subscriptions_pkey; Type: CONSTRAINT; Schema: augur_operations; Owner: augur
--

ALTER TABLE ONLY augur_operations.subscriptions
    ADD CONSTRAINT subscriptions_pkey PRIMARY KEY (application_id, type_id);


--
-- Name: config unique-config-setting; Type: CONSTRAINT; Schema: augur_operations; Owner: augur
--

ALTER TABLE ONLY augur_operations.config
    ADD CONSTRAINT "unique-config-setting" UNIQUE (section_name, setting_name);


--
-- Name: users user-unique-email; Type: CONSTRAINT; Schema: augur_operations; Owner: augur
--

ALTER TABLE ONLY augur_operations.users
    ADD CONSTRAINT "user-unique-email" UNIQUE (email);


--
-- Name: users user-unique-name; Type: CONSTRAINT; Schema: augur_operations; Owner: augur
--

ALTER TABLE ONLY augur_operations.users
    ADD CONSTRAINT "user-unique-name" UNIQUE (login_name);


--
-- Name: users user-unique-phone; Type: CONSTRAINT; Schema: augur_operations; Owner: augur
--

ALTER TABLE ONLY augur_operations.users
    ADD CONSTRAINT "user-unique-phone" UNIQUE (text_phone);


--
-- Name: user_groups user_groups_pkey; Type: CONSTRAINT; Schema: augur_operations; Owner: augur
--

ALTER TABLE ONLY augur_operations.user_groups
    ADD CONSTRAINT user_groups_pkey PRIMARY KEY (group_id);


--
-- Name: user_groups user_groups_user_id_name_key; Type: CONSTRAINT; Schema: augur_operations; Owner: augur
--

ALTER TABLE ONLY augur_operations.user_groups
    ADD CONSTRAINT user_groups_user_id_name_key UNIQUE (user_id, name);


--
-- Name: user_repos user_repos_pkey; Type: CONSTRAINT; Schema: augur_operations; Owner: augur
--

ALTER TABLE ONLY augur_operations.user_repos
    ADD CONSTRAINT user_repos_pkey PRIMARY KEY (group_id, repo_id);


--
-- Name: user_session_tokens user_session_tokens_pkey; Type: CONSTRAINT; Schema: augur_operations; Owner: augur
--

ALTER TABLE ONLY augur_operations.user_session_tokens
    ADD CONSTRAINT user_session_tokens_pkey PRIMARY KEY (token);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: augur_operations; Owner: augur
--

ALTER TABLE ONLY augur_operations.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: worker_oauth worker_oauth_pkey; Type: CONSTRAINT; Schema: augur_operations; Owner: augur
--

ALTER TABLE ONLY augur_operations.worker_oauth
    ADD CONSTRAINT worker_oauth_pkey PRIMARY KEY (oauth_id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: augur
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: annotation_types annotation_types_pkey; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.annotation_types
    ADD CONSTRAINT annotation_types_pkey PRIMARY KEY (annotation_type_id);


--
-- Name: annotations annotations_pkey; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.annotations
    ADD CONSTRAINT annotations_pkey PRIMARY KEY (annotation_id);


--
-- Name: augur_repo_map augur_repo_map_pkey; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.augur_repo_map
    ADD CONSTRAINT augur_repo_map_pkey PRIMARY KEY (map_id);


--
-- Name: creator_types creator_types_pkey; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.creator_types
    ADD CONSTRAINT creator_types_pkey PRIMARY KEY (creator_type_id);


--
-- Name: creators creators_pkey; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.creators
    ADD CONSTRAINT creators_pkey PRIMARY KEY (creator_id);


--
-- Name: document_namespaces document_namespaces_pkey; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.document_namespaces
    ADD CONSTRAINT document_namespaces_pkey PRIMARY KEY (document_namespace_id);


--
-- Name: documents_creators documents_creators_pkey; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.documents_creators
    ADD CONSTRAINT documents_creators_pkey PRIMARY KEY (document_creator_id);


--
-- Name: documents documents_pkey; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.documents
    ADD CONSTRAINT documents_pkey PRIMARY KEY (document_id);


--
-- Name: external_refs external_refs_pkey; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.external_refs
    ADD CONSTRAINT external_refs_pkey PRIMARY KEY (external_ref_id);


--
-- Name: file_contributors file_contributors_pkey; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.file_contributors
    ADD CONSTRAINT file_contributors_pkey PRIMARY KEY (file_contributor_id);


--
-- Name: files_licenses files_licenses_pkey; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.files_licenses
    ADD CONSTRAINT files_licenses_pkey PRIMARY KEY (file_license_id);


--
-- Name: files files_pkey; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.files
    ADD CONSTRAINT files_pkey PRIMARY KEY (file_id);


--
-- Name: files_scans files_scans_pkey; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.files_scans
    ADD CONSTRAINT files_scans_pkey PRIMARY KEY (file_scan_id);


--
-- Name: identifiers identifiers_pkey; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.identifiers
    ADD CONSTRAINT identifiers_pkey PRIMARY KEY (identifier_id);


--
-- Name: licenses licenses_pkey; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.licenses
    ADD CONSTRAINT licenses_pkey PRIMARY KEY (license_id);


--
-- Name: packages_files packages_files_pkey; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.packages_files
    ADD CONSTRAINT packages_files_pkey PRIMARY KEY (package_file_id);


--
-- Name: packages packages_pkey; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.packages
    ADD CONSTRAINT packages_pkey PRIMARY KEY (package_id);


--
-- Name: packages_scans packages_scans_pkey; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.packages_scans
    ADD CONSTRAINT packages_scans_pkey PRIMARY KEY (package_scan_id);


--
-- Name: projects projects_pkey; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (package_id);


--
-- Name: relationship_types relationship_types_pkey; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.relationship_types
    ADD CONSTRAINT relationship_types_pkey PRIMARY KEY (relationship_type_id);


--
-- Name: relationships relationships_pkey; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.relationships
    ADD CONSTRAINT relationships_pkey PRIMARY KEY (relationship_id);


--
-- Name: scanners scanners_pkey; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.scanners
    ADD CONSTRAINT scanners_pkey PRIMARY KEY (scanner_id);


--
-- Name: annotation_types uc_annotation_type_name; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.annotation_types
    ADD CONSTRAINT uc_annotation_type_name UNIQUE (name);


--
-- Name: packages uc_dir_code_ver_code; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.packages
    ADD CONSTRAINT uc_dir_code_ver_code UNIQUE (verification_code, dosocs2_dir_code);


--
-- Name: documents uc_document_document_namespace_id; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.documents
    ADD CONSTRAINT uc_document_document_namespace_id UNIQUE (document_namespace_id);


--
-- Name: document_namespaces uc_document_namespace_uri; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.document_namespaces
    ADD CONSTRAINT uc_document_namespace_uri UNIQUE (uri);


--
-- Name: external_refs uc_external_ref_document_id_string; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.external_refs
    ADD CONSTRAINT uc_external_ref_document_id_string UNIQUE (document_id, id_string);


--
-- Name: files_licenses uc_file_license; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.files_licenses
    ADD CONSTRAINT uc_file_license UNIQUE (file_id, license_id);


--
-- Name: files_scans uc_file_scanner_id; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.files_scans
    ADD CONSTRAINT uc_file_scanner_id UNIQUE (file_id, scanner_id);


--
-- Name: files uc_file_sha256; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.files
    ADD CONSTRAINT uc_file_sha256 UNIQUE (sha256);


--
-- Name: file_types uc_file_type_name; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.file_types
    ADD CONSTRAINT uc_file_type_name PRIMARY KEY (name);


--
-- Name: identifiers uc_identifier_document_namespace_id; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.identifiers
    ADD CONSTRAINT uc_identifier_document_namespace_id UNIQUE (document_namespace_id, id_string);


--
-- Name: identifiers uc_identifier_namespace_document_id; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.identifiers
    ADD CONSTRAINT uc_identifier_namespace_document_id UNIQUE (document_namespace_id, document_id);


--
-- Name: identifiers uc_identifier_namespace_package_file_id; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.identifiers
    ADD CONSTRAINT uc_identifier_namespace_package_file_id UNIQUE (document_namespace_id, package_file_id);


--
-- Name: identifiers uc_identifier_namespace_package_id; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.identifiers
    ADD CONSTRAINT uc_identifier_namespace_package_id UNIQUE (document_namespace_id, package_id);


--
-- Name: relationships uc_left_right_relationship_type; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.relationships
    ADD CONSTRAINT uc_left_right_relationship_type UNIQUE (left_identifier_id, right_identifier_id, relationship_type_id);


--
-- Name: licenses uc_license_short_name; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.licenses
    ADD CONSTRAINT uc_license_short_name UNIQUE (short_name);


--
-- Name: packages_files uc_package_id_file_name; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.packages_files
    ADD CONSTRAINT uc_package_id_file_name UNIQUE (package_id, file_name);


--
-- Name: packages_scans uc_package_scanner_id; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.packages_scans
    ADD CONSTRAINT uc_package_scanner_id UNIQUE (package_id, scanner_id);


--
-- Name: packages uc_package_sha256; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.packages
    ADD CONSTRAINT uc_package_sha256 UNIQUE (sha256);


--
-- Name: relationship_types uc_relationship_type_name; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.relationship_types
    ADD CONSTRAINT uc_relationship_type_name UNIQUE (name);


--
-- Name: scanners uc_scanner_name; Type: CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.scanners
    ADD CONSTRAINT uc_scanner_name UNIQUE (name);


--
-- Name: REPO_DEP; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX "REPO_DEP" ON augur_data.library_dependencies USING btree (library_id);


--
-- Name: author_affiliation; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX author_affiliation ON augur_data.commits USING btree (cmt_author_affiliation);


--
-- Name: author_cntrb_id; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX author_cntrb_id ON augur_data.commits USING btree (cmt_ght_author_id);


--
-- Name: author_email,author_affiliation,author_date; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX "author_email,author_affiliation,author_date" ON augur_data.commits USING btree (cmt_author_email, cmt_author_affiliation, cmt_author_date);


--
-- Name: author_raw_email; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX author_raw_email ON augur_data.commits USING btree (cmt_author_raw_email);


--
-- Name: cnt-fullname; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX "cnt-fullname" ON augur_data.contributors USING hash (cntrb_full_name);


--
-- Name: cntrb-theemail; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX "cntrb-theemail" ON augur_data.contributors USING hash (cntrb_email);


--
-- Name: cntrb_canonica-idx11; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX "cntrb_canonica-idx11" ON augur_data.contributors USING btree (cntrb_canonical);


--
-- Name: cntrb_login_platform_index; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX cntrb_login_platform_index ON augur_data.contributors USING btree (cntrb_login);


--
-- Name: comment_id; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX comment_id ON augur_data.commit_comment_ref USING btree (cmt_comment_src_id, cmt_comment_id, msg_id);


--
-- Name: commit_parents_ibfk_1; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX commit_parents_ibfk_1 ON augur_data.commit_parents USING btree (cmt_id);


--
-- Name: commit_parents_ibfk_2; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX commit_parents_ibfk_2 ON augur_data.commit_parents USING btree (parent_id);


--
-- Name: commited; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX commited ON augur_data.commits USING btree (cmt_id);


--
-- Name: commits_idx_cmt_email_cmt_date_cmt_name; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX commits_idx_cmt_email_cmt_date_cmt_name ON augur_data.commits USING btree (cmt_author_email, cmt_author_date, cmt_author_name);


--
-- Name: committer_affiliation; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX committer_affiliation ON augur_data.commits USING btree (cmt_committer_affiliation);


--
-- Name: committer_raw_email; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX committer_raw_email ON augur_data.commits USING btree (cmt_committer_raw_email);


--
-- Name: contributor_worker_email_finder; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX contributor_worker_email_finder ON augur_data.contributors USING brin (cntrb_email);


--
-- Name: contributor_worker_fullname_finder; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX contributor_worker_fullname_finder ON augur_data.contributors USING brin (cntrb_full_name);


--
-- Name: contributors_idx_cntrb_email3; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX contributors_idx_cntrb_email3 ON augur_data.contributors USING btree (cntrb_email);


--
-- Name: dater; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX dater ON augur_data.repo_insights_records USING btree (ri_date);


--
-- Name: forked; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX forked ON augur_data.repo USING btree (forked_from);


--
-- Name: id_node; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX id_node ON augur_data.pull_requests USING btree (pr_src_id DESC, pr_src_node_id DESC NULLS LAST);


--
-- Name: issue-cntrb-assign-idx-1; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX "issue-cntrb-assign-idx-1" ON augur_data.issue_assignees USING btree (cntrb_id);


--
-- Name: issue-cntrb-dix2; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX "issue-cntrb-dix2" ON augur_data.issues USING btree (cntrb_id);


--
-- Name: issue-cntrb-idx2; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX "issue-cntrb-idx2" ON augur_data.issue_events USING btree (issue_event_src_id);


--
-- Name: issue_events_ibfk_1; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX issue_events_ibfk_1 ON augur_data.issue_events USING btree (issue_id);


--
-- Name: issue_events_ibfk_2; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX issue_events_ibfk_2 ON augur_data.issue_events USING btree (cntrb_id);


--
-- Name: issues_ibfk_1; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX issues_ibfk_1 ON augur_data.issues USING btree (repo_id);


--
-- Name: issues_ibfk_2; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX issues_ibfk_2 ON augur_data.issues USING btree (reporter_id);


--
-- Name: issues_ibfk_4; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX issues_ibfk_4 ON augur_data.issues USING btree (pull_request_id);


--
-- Name: lister; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE UNIQUE INDEX lister ON augur_data.repo_groups_list_serve USING btree (rgls_id, repo_group_id);


--
-- Name: login; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX login ON augur_data.contributors USING btree (cntrb_login);


--
-- Name: login-contributor-idx; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX "login-contributor-idx" ON augur_data.contributors USING btree (cntrb_login);


--
-- Name: messagegrouper; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE UNIQUE INDEX messagegrouper ON augur_data.message USING btree (msg_id, rgls_id);


--
-- Name: msg-cntrb-id-idx; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX "msg-cntrb-id-idx" ON augur_data.message USING btree (cntrb_id);


--
-- Name: plat; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE UNIQUE INDEX plat ON augur_data.platform USING btree (pltfrm_id);


--
-- Name: platformgrouper; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX platformgrouper ON augur_data.message USING btree (msg_id, pltfrm_id);


--
-- Name: pr-cntrb-idx-repo; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX "pr-cntrb-idx-repo" ON augur_data.pull_request_repo USING btree (pr_cntrb_id);


--
-- Name: pr-reviewers-cntrb-idx1; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX "pr-reviewers-cntrb-idx1" ON augur_data.pull_request_reviewers USING btree (cntrb_id);


--
-- Name: pr_anal_idx; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX pr_anal_idx ON augur_data.pull_request_analysis USING btree (pull_request_id);


--
-- Name: pr_events_ibfk_1; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX pr_events_ibfk_1 ON augur_data.pull_request_events USING btree (pull_request_id);


--
-- Name: pr_events_ibfk_2; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX pr_events_ibfk_2 ON augur_data.pull_request_events USING btree (cntrb_id);


--
-- Name: pr_meta-cntrbid-idx; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX "pr_meta-cntrbid-idx" ON augur_data.pull_request_meta USING btree (cntrb_id);


--
-- Name: pr_meta_cntrb-idx; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX "pr_meta_cntrb-idx" ON augur_data.pull_request_assignees USING btree (contrib_id);


--
-- Name: probability_idx; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX probability_idx ON augur_data.pull_request_analysis USING btree (merge_probability DESC NULLS LAST);


--
-- Name: projects_id,affiliation; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX "projects_id,affiliation" ON augur_data.dm_repo_group_weekly USING btree (repo_group_id, affiliation);


--
-- Name: projects_id,affiliation_copy_1; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX "projects_id,affiliation_copy_1" ON augur_data.dm_repo_group_annual USING btree (repo_group_id, affiliation);


--
-- Name: projects_id,affiliation_copy_2; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX "projects_id,affiliation_copy_2" ON augur_data.dm_repo_group_monthly USING btree (repo_group_id, affiliation);


--
-- Name: projects_id,email; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX "projects_id,email" ON augur_data.dm_repo_group_weekly USING btree (repo_group_id, email);


--
-- Name: projects_id,email_copy_1; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX "projects_id,email_copy_1" ON augur_data.dm_repo_group_annual USING btree (repo_group_id, email);


--
-- Name: projects_id,email_copy_2; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX "projects_id,email_copy_2" ON augur_data.dm_repo_group_monthly USING btree (repo_group_id, email);


--
-- Name: projects_id,year,affiliation; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX "projects_id,year,affiliation" ON augur_data.dm_repo_group_weekly USING btree (repo_group_id, year, affiliation);


--
-- Name: projects_id,year,affiliation_copy_1; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX "projects_id,year,affiliation_copy_1" ON augur_data.dm_repo_group_monthly USING btree (repo_group_id, year, affiliation);


--
-- Name: projects_id,year,email; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX "projects_id,year,email" ON augur_data.dm_repo_group_weekly USING btree (repo_group_id, year, email);


--
-- Name: projects_id,year,email_copy_1; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX "projects_id,year,email_copy_1" ON augur_data.dm_repo_group_monthly USING btree (repo_group_id, year, email);


--
-- Name: pull_requests_idx_repo_id_data_datex; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX pull_requests_idx_repo_id_data_datex ON augur_data.pull_requests USING btree (repo_id, data_collection_date);


--
-- Name: repo_id,affiliation; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX "repo_id,affiliation" ON augur_data.dm_repo_weekly USING btree (repo_id, affiliation);


--
-- Name: repo_id,affiliation_copy_1; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX "repo_id,affiliation_copy_1" ON augur_data.dm_repo_annual USING btree (repo_id, affiliation);


--
-- Name: repo_id,affiliation_copy_2; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX "repo_id,affiliation_copy_2" ON augur_data.dm_repo_monthly USING btree (repo_id, affiliation);


--
-- Name: repo_id,commit; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX "repo_id,commit" ON augur_data.commits USING btree (repo_id, cmt_commit_hash);


--
-- Name: repo_id,email; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX "repo_id,email" ON augur_data.dm_repo_weekly USING btree (repo_id, email);


--
-- Name: repo_id,email_copy_1; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX "repo_id,email_copy_1" ON augur_data.dm_repo_annual USING btree (repo_id, email);


--
-- Name: repo_id,email_copy_2; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX "repo_id,email_copy_2" ON augur_data.dm_repo_monthly USING btree (repo_id, email);


--
-- Name: repo_id,year,affiliation; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX "repo_id,year,affiliation" ON augur_data.dm_repo_weekly USING btree (repo_id, year, affiliation);


--
-- Name: repo_id,year,affiliation_copy_1; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX "repo_id,year,affiliation_copy_1" ON augur_data.dm_repo_monthly USING btree (repo_id, year, affiliation);


--
-- Name: repo_id,year,email; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX "repo_id,year,email" ON augur_data.dm_repo_weekly USING btree (repo_id, year, email);


--
-- Name: repo_id,year,email_copy_1; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX "repo_id,year,email_copy_1" ON augur_data.dm_repo_monthly USING btree (repo_id, year, email);


--
-- Name: repo_idx_repo_id_repo_namex; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX repo_idx_repo_id_repo_namex ON augur_data.repo USING btree (repo_id, repo_name);


--
-- Name: repo_info_idx_repo_id_data_date_1x; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX repo_info_idx_repo_id_data_date_1x ON augur_data.repo_info USING btree (repo_id, data_collection_date);


--
-- Name: repo_info_idx_repo_id_data_datex; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX repo_info_idx_repo_id_data_datex ON augur_data.repo_info USING btree (repo_id, data_collection_date);


--
-- Name: repogitindexrep; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX repogitindexrep ON augur_data.repo USING btree (repo_git);


--
-- Name: reponameindex; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX reponameindex ON augur_data.repo USING hash (repo_name);


--
-- Name: reponameindexbtree; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX reponameindexbtree ON augur_data.repo USING btree (repo_name);


--
-- Name: repos_id; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX repos_id ON augur_data.analysis_log USING btree (repos_id);


--
-- Name: repos_id,status; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX "repos_id,status" ON augur_data.repos_fetch_log USING btree (repos_id, status);


--
-- Name: repos_id,statusops; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX "repos_id,statusops" ON augur_data.repos_fetch_log USING btree (repos_id, status);


--
-- Name: rggrouponrepoindex; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX rggrouponrepoindex ON augur_data.repo USING btree (repo_group_id);


--
-- Name: rgidm; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE UNIQUE INDEX rgidm ON augur_data.repo_groups USING btree (repo_group_id);


--
-- Name: rgnameindex; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX rgnameindex ON augur_data.repo_groups USING btree (rg_name);


--
-- Name: therepo; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE UNIQUE INDEX therepo ON augur_data.repo USING btree (repo_id);


--
-- Name: type,projects_id; Type: INDEX; Schema: augur_data; Owner: augur
--

CREATE INDEX "type,projects_id" ON augur_data.unknown_cache USING btree (type, repo_group_id);


--
-- Name: repos_id,statusops; Type: INDEX; Schema: augur_operations; Owner: augur
--

CREATE INDEX "repos_id,statusops" ON augur_operations.repos_fetch_log USING btree (repos_id, status);


--
-- Name: commits cmt_ght_author_cntrb_id_fk; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.commits
    ADD CONSTRAINT cmt_ght_author_cntrb_id_fk FOREIGN KEY (cmt_ght_author_id) REFERENCES augur_data.contributors(cntrb_id) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;


--
-- Name: contributor_repo contributor_repo_cntrb_id_fkey; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.contributor_repo
    ADD CONSTRAINT contributor_repo_cntrb_id_fkey FOREIGN KEY (cntrb_id) REFERENCES augur_data.contributors(cntrb_id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: contributors_aliases contributors_aliases_cntrb_id_fkey; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.contributors_aliases
    ADD CONSTRAINT contributors_aliases_cntrb_id_fkey FOREIGN KEY (cntrb_id) REFERENCES augur_data.contributors(cntrb_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: pull_request_reviews fk-review-platform; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_reviews
    ADD CONSTRAINT "fk-review-platform" FOREIGN KEY (platform_id) REFERENCES augur_data.platform(pltfrm_id) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;


--
-- Name: commit_comment_ref fk_commit_comment_ref_commits_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.commit_comment_ref
    ADD CONSTRAINT fk_commit_comment_ref_commits_1 FOREIGN KEY (cmt_id) REFERENCES augur_data.commits(cmt_id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: commit_comment_ref fk_commit_comment_ref_message_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.commit_comment_ref
    ADD CONSTRAINT fk_commit_comment_ref_message_1 FOREIGN KEY (msg_id) REFERENCES augur_data.message(msg_id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: commit_parents fk_commit_parents_commits_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.commit_parents
    ADD CONSTRAINT fk_commit_parents_commits_1 FOREIGN KEY (cmt_id) REFERENCES augur_data.commits(cmt_id);


--
-- Name: commit_parents fk_commit_parents_commits_2; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.commit_parents
    ADD CONSTRAINT fk_commit_parents_commits_2 FOREIGN KEY (parent_id) REFERENCES augur_data.commits(cmt_id);


--
-- Name: commits fk_commits_contributors_3; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.commits
    ADD CONSTRAINT fk_commits_contributors_3 FOREIGN KEY (cmt_author_platform_username) REFERENCES augur_data.contributors(cntrb_login) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: commits fk_commits_contributors_4; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.commits
    ADD CONSTRAINT fk_commits_contributors_4 FOREIGN KEY (cmt_author_platform_username) REFERENCES augur_data.contributors(cntrb_login) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: commits fk_commits_repo_2; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.commits
    ADD CONSTRAINT fk_commits_repo_2 FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: discourse_insights fk_discourse_insights_message_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.discourse_insights
    ADD CONSTRAINT fk_discourse_insights_message_1 FOREIGN KEY (msg_id) REFERENCES augur_data.message(msg_id);


--
-- Name: issue_assignees fk_issue_assignee_repo_id; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.issue_assignees
    ADD CONSTRAINT fk_issue_assignee_repo_id FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: issue_assignees fk_issue_assignees_issues_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.issue_assignees
    ADD CONSTRAINT fk_issue_assignees_issues_1 FOREIGN KEY (issue_id) REFERENCES augur_data.issues(issue_id);


--
-- Name: issue_events fk_issue_event_platform_ide; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.issue_events
    ADD CONSTRAINT fk_issue_event_platform_ide FOREIGN KEY (platform_id) REFERENCES augur_data.platform(pltfrm_id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: issue_events fk_issue_events_issues_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.issue_events
    ADD CONSTRAINT fk_issue_events_issues_1 FOREIGN KEY (issue_id) REFERENCES augur_data.issues(issue_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: issue_events fk_issue_events_repo; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.issue_events
    ADD CONSTRAINT fk_issue_events_repo FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: issue_labels fk_issue_labels_issues_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.issue_labels
    ADD CONSTRAINT fk_issue_labels_issues_1 FOREIGN KEY (issue_id) REFERENCES augur_data.issues(issue_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: issue_labels fk_issue_labels_repo_id; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.issue_labels
    ADD CONSTRAINT fk_issue_labels_repo_id FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: issue_message_ref fk_issue_message_ref_issues_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.issue_message_ref
    ADD CONSTRAINT fk_issue_message_ref_issues_1 FOREIGN KEY (issue_id) REFERENCES augur_data.issues(issue_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: issue_message_ref fk_issue_message_ref_message_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.issue_message_ref
    ADD CONSTRAINT fk_issue_message_ref_message_1 FOREIGN KEY (msg_id) REFERENCES augur_data.message(msg_id) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;


--
-- Name: issues fk_issues_repo; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.issues
    ADD CONSTRAINT fk_issues_repo FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: libraries fk_libraries_repo_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.libraries
    ADD CONSTRAINT fk_libraries_repo_1 FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id);


--
-- Name: library_dependencies fk_library_dependencies_libraries_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.library_dependencies
    ADD CONSTRAINT fk_library_dependencies_libraries_1 FOREIGN KEY (library_id) REFERENCES augur_data.libraries(library_id);


--
-- Name: library_version fk_library_version_libraries_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.library_version
    ADD CONSTRAINT fk_library_version_libraries_1 FOREIGN KEY (library_id) REFERENCES augur_data.libraries(library_id);


--
-- Name: lstm_anomaly_results fk_lstm_anomaly_results_lstm_anomaly_models_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.lstm_anomaly_results
    ADD CONSTRAINT fk_lstm_anomaly_results_lstm_anomaly_models_1 FOREIGN KEY (model_id) REFERENCES augur_data.lstm_anomaly_models(model_id);


--
-- Name: lstm_anomaly_results fk_lstm_anomaly_results_repo_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.lstm_anomaly_results
    ADD CONSTRAINT fk_lstm_anomaly_results_repo_1 FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id);


--
-- Name: message_analysis fk_message_analysis_message_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.message_analysis
    ADD CONSTRAINT fk_message_analysis_message_1 FOREIGN KEY (msg_id) REFERENCES augur_data.message(msg_id);


--
-- Name: message_analysis_summary fk_message_analysis_summary_repo_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.message_analysis_summary
    ADD CONSTRAINT fk_message_analysis_summary_repo_1 FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id);


--
-- Name: message fk_message_platform_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.message
    ADD CONSTRAINT fk_message_platform_1 FOREIGN KEY (pltfrm_id) REFERENCES augur_data.platform(pltfrm_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: message fk_message_repo_groups_list_serve_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.message
    ADD CONSTRAINT fk_message_repo_groups_list_serve_1 FOREIGN KEY (rgls_id) REFERENCES augur_data.repo_groups_list_serve(rgls_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: message fk_message_repoid; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.message
    ADD CONSTRAINT fk_message_repoid FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: message_sentiment fk_message_sentiment_message_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.message_sentiment
    ADD CONSTRAINT fk_message_sentiment_message_1 FOREIGN KEY (msg_id) REFERENCES augur_data.message(msg_id);


--
-- Name: message_sentiment_summary fk_message_sentiment_summary_repo_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.message_sentiment_summary
    ADD CONSTRAINT fk_message_sentiment_summary_repo_1 FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id);


--
-- Name: pull_request_message_ref fk_pr_repo; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_message_ref
    ADD CONSTRAINT fk_pr_repo FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: pull_request_analysis fk_pull_request_analysis_pull_requests_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_analysis
    ADD CONSTRAINT fk_pull_request_analysis_pull_requests_1 FOREIGN KEY (pull_request_id) REFERENCES augur_data.pull_requests(pull_request_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: pull_request_assignees fk_pull_request_assignees_pull_requests_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_assignees
    ADD CONSTRAINT fk_pull_request_assignees_pull_requests_1 FOREIGN KEY (pull_request_id) REFERENCES augur_data.pull_requests(pull_request_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: pull_request_assignees fk_pull_request_assignees_repo_id; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_assignees
    ADD CONSTRAINT fk_pull_request_assignees_repo_id FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;


--
-- Name: pull_request_commits fk_pull_request_commits_pull_requests_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_commits
    ADD CONSTRAINT fk_pull_request_commits_pull_requests_1 FOREIGN KEY (pull_request_id) REFERENCES augur_data.pull_requests(pull_request_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: pull_request_files fk_pull_request_commits_pull_requests_1_copy_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_files
    ADD CONSTRAINT fk_pull_request_commits_pull_requests_1_copy_1 FOREIGN KEY (pull_request_id) REFERENCES augur_data.pull_requests(pull_request_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: pull_request_commits fk_pull_request_commits_repo_id; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_commits
    ADD CONSTRAINT fk_pull_request_commits_repo_id FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: pull_request_events fk_pull_request_events_pull_requests_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_events
    ADD CONSTRAINT fk_pull_request_events_pull_requests_1 FOREIGN KEY (pull_request_id) REFERENCES augur_data.pull_requests(pull_request_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: pull_request_files fk_pull_request_files_repo_id; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_files
    ADD CONSTRAINT fk_pull_request_files_repo_id FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;


--
-- Name: pull_request_labels fk_pull_request_labels_pull_requests_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_labels
    ADD CONSTRAINT fk_pull_request_labels_pull_requests_1 FOREIGN KEY (pull_request_id) REFERENCES augur_data.pull_requests(pull_request_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: pull_request_labels fk_pull_request_labels_repo; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_labels
    ADD CONSTRAINT fk_pull_request_labels_repo FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: pull_request_message_ref fk_pull_request_message_ref_message_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_message_ref
    ADD CONSTRAINT fk_pull_request_message_ref_message_1 FOREIGN KEY (msg_id) REFERENCES augur_data.message(msg_id) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;


--
-- Name: pull_request_message_ref fk_pull_request_message_ref_pull_requests_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_message_ref
    ADD CONSTRAINT fk_pull_request_message_ref_pull_requests_1 FOREIGN KEY (pull_request_id) REFERENCES augur_data.pull_requests(pull_request_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: pull_request_meta fk_pull_request_meta_pull_requests_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_meta
    ADD CONSTRAINT fk_pull_request_meta_pull_requests_1 FOREIGN KEY (pull_request_id) REFERENCES augur_data.pull_requests(pull_request_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: pull_request_meta fk_pull_request_repo_meta_repo_id; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_meta
    ADD CONSTRAINT fk_pull_request_repo_meta_repo_id FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;


--
-- Name: pull_request_repo fk_pull_request_repo_pull_request_meta_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_repo
    ADD CONSTRAINT fk_pull_request_repo_pull_request_meta_1 FOREIGN KEY (pr_repo_meta_id) REFERENCES augur_data.pull_request_meta(pr_repo_meta_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: pull_request_review_message_ref fk_pull_request_review_message_ref_message_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_review_message_ref
    ADD CONSTRAINT fk_pull_request_review_message_ref_message_1 FOREIGN KEY (msg_id) REFERENCES augur_data.message(msg_id) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;


--
-- Name: pull_request_review_message_ref fk_pull_request_review_message_ref_pull_request_reviews_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_review_message_ref
    ADD CONSTRAINT fk_pull_request_review_message_ref_pull_request_reviews_1 FOREIGN KEY (pr_review_id) REFERENCES augur_data.pull_request_reviews(pr_review_id) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;


--
-- Name: pull_request_reviewers fk_pull_request_reviewers_pull_requests_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_reviewers
    ADD CONSTRAINT fk_pull_request_reviewers_pull_requests_1 FOREIGN KEY (pull_request_id) REFERENCES augur_data.pull_requests(pull_request_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: pull_request_reviews fk_pull_request_reviews_pull_requests_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_reviews
    ADD CONSTRAINT fk_pull_request_reviews_pull_requests_1 FOREIGN KEY (pull_request_id) REFERENCES augur_data.pull_requests(pull_request_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: pull_request_teams fk_pull_request_teams_pull_requests_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_teams
    ADD CONSTRAINT fk_pull_request_teams_pull_requests_1 FOREIGN KEY (pull_request_id) REFERENCES augur_data.pull_requests(pull_request_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: pull_requests fk_pull_requests_repo_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_requests
    ADD CONSTRAINT fk_pull_requests_repo_1 FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: releases fk_releases_repo_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.releases
    ADD CONSTRAINT fk_releases_repo_1 FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id);


--
-- Name: repo_badging fk_repo_badging_repo_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_badging
    ADD CONSTRAINT fk_repo_badging_repo_1 FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id);


--
-- Name: repo_cluster_messages fk_repo_cluster_messages_repo_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_cluster_messages
    ADD CONSTRAINT fk_repo_cluster_messages_repo_1 FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id);


--
-- Name: repo_group_insights fk_repo_group_insights_repo_groups_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_group_insights
    ADD CONSTRAINT fk_repo_group_insights_repo_groups_1 FOREIGN KEY (repo_group_id) REFERENCES augur_data.repo_groups(repo_group_id);


--
-- Name: repo_groups_list_serve fk_repo_groups_list_serve_repo_groups_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_groups_list_serve
    ADD CONSTRAINT fk_repo_groups_list_serve_repo_groups_1 FOREIGN KEY (repo_group_id) REFERENCES augur_data.repo_groups(repo_group_id);


--
-- Name: issue_message_ref fk_repo_id_fk1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.issue_message_ref
    ADD CONSTRAINT fk_repo_id_fk1 FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;


--
-- Name: repo_info fk_repo_info_repo_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_info
    ADD CONSTRAINT fk_repo_info_repo_1 FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id);


--
-- Name: repo_insights fk_repo_insights_repo_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_insights
    ADD CONSTRAINT fk_repo_insights_repo_1 FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id);


--
-- Name: repo_labor fk_repo_labor_repo_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_labor
    ADD CONSTRAINT fk_repo_labor_repo_1 FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id);


--
-- Name: repo_meta fk_repo_meta_repo_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_meta
    ADD CONSTRAINT fk_repo_meta_repo_1 FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id);


--
-- Name: repo fk_repo_repo_groups_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo
    ADD CONSTRAINT fk_repo_repo_groups_1 FOREIGN KEY (repo_group_id) REFERENCES augur_data.repo_groups(repo_group_id);


--
-- Name: CONSTRAINT fk_repo_repo_groups_1 ON repo; Type: COMMENT; Schema: augur_data; Owner: augur
--

COMMENT ON CONSTRAINT fk_repo_repo_groups_1 ON augur_data.repo IS 'Repo_groups cardinality set to one and only one because, although in theory there could be more than one repo group for a repo, this might create dependencies in hosted situation that we do not want to live with. ';


--
-- Name: pull_request_reviews fk_repo_review; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_reviews
    ADD CONSTRAINT fk_repo_review FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: repo_stats fk_repo_stats_repo_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_stats
    ADD CONSTRAINT fk_repo_stats_repo_1 FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id);


--
-- Name: repo_test_coverage fk_repo_test_coverage_repo_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_test_coverage
    ADD CONSTRAINT fk_repo_test_coverage_repo_1 FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id);


--
-- Name: repo_topic fk_repo_topic_repo_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_topic
    ADD CONSTRAINT fk_repo_topic_repo_1 FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id);


--
-- Name: pull_request_review_message_ref fk_review_repo; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_review_message_ref
    ADD CONSTRAINT fk_review_repo FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;


--
-- Name: pull_request_events fkpr_platform; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_events
    ADD CONSTRAINT fkpr_platform FOREIGN KEY (platform_id) REFERENCES augur_data.platform(pltfrm_id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;


--
-- Name: pull_request_events fkprevent_repo_id; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_events
    ADD CONSTRAINT fkprevent_repo_id FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id) ON UPDATE RESTRICT ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;


--
-- Name: issue_assignees issue_assignees_cntrb_id_fkey; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.issue_assignees
    ADD CONSTRAINT issue_assignees_cntrb_id_fkey FOREIGN KEY (cntrb_id) REFERENCES augur_data.contributors(cntrb_id);


--
-- Name: issue_events issue_events_cntrb_id_fkey; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.issue_events
    ADD CONSTRAINT issue_events_cntrb_id_fkey FOREIGN KEY (cntrb_id) REFERENCES augur_data.contributors(cntrb_id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: issues issues_cntrb_id_fkey; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.issues
    ADD CONSTRAINT issues_cntrb_id_fkey FOREIGN KEY (cntrb_id) REFERENCES augur_data.contributors(cntrb_id);


--
-- Name: issues issues_reporter_id_fkey; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.issues
    ADD CONSTRAINT issues_reporter_id_fkey FOREIGN KEY (reporter_id) REFERENCES augur_data.contributors(cntrb_id);


--
-- Name: message message_cntrb_id_fkey; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.message
    ADD CONSTRAINT message_cntrb_id_fkey FOREIGN KEY (cntrb_id) REFERENCES augur_data.contributors(cntrb_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: pull_request_assignees pull_request_assignees_contrib_id_fkey; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_assignees
    ADD CONSTRAINT pull_request_assignees_contrib_id_fkey FOREIGN KEY (contrib_id) REFERENCES augur_data.contributors(cntrb_id);


--
-- Name: pull_request_commits pull_request_commits_pr_cmt_author_cntrb_id_fkey; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_commits
    ADD CONSTRAINT pull_request_commits_pr_cmt_author_cntrb_id_fkey FOREIGN KEY (pr_cmt_author_cntrb_id) REFERENCES augur_data.contributors(cntrb_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: pull_request_events pull_request_events_cntrb_id_fkey; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_events
    ADD CONSTRAINT pull_request_events_cntrb_id_fkey FOREIGN KEY (cntrb_id) REFERENCES augur_data.contributors(cntrb_id);


--
-- Name: pull_request_meta pull_request_meta_cntrb_id_fkey; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_meta
    ADD CONSTRAINT pull_request_meta_cntrb_id_fkey FOREIGN KEY (cntrb_id) REFERENCES augur_data.contributors(cntrb_id);


--
-- Name: pull_request_repo pull_request_repo_pr_cntrb_id_fkey; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_repo
    ADD CONSTRAINT pull_request_repo_pr_cntrb_id_fkey FOREIGN KEY (pr_cntrb_id) REFERENCES augur_data.contributors(cntrb_id);


--
-- Name: pull_request_reviewers pull_request_reviewers_cntrb_id_fkey; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_reviewers
    ADD CONSTRAINT pull_request_reviewers_cntrb_id_fkey FOREIGN KEY (cntrb_id) REFERENCES augur_data.contributors(cntrb_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: pull_request_reviews pull_request_reviews_cntrb_id_fkey; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_request_reviews
    ADD CONSTRAINT pull_request_reviews_cntrb_id_fkey FOREIGN KEY (cntrb_id) REFERENCES augur_data.contributors(cntrb_id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: pull_requests pull_requests_pr_augur_contributor_id_fkey; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.pull_requests
    ADD CONSTRAINT pull_requests_pr_augur_contributor_id_fkey FOREIGN KEY (pr_augur_contributor_id) REFERENCES augur_data.contributors(cntrb_id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: repo_clones_data repo_clones_data_repo_id_fkey; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_clones_data
    ADD CONSTRAINT repo_clones_data_repo_id_fkey FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;


--
-- Name: repo_dependencies repo_id; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_dependencies
    ADD CONSTRAINT repo_id FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id);


--
-- Name: repo_deps_scorecard repo_id_copy_1; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_deps_scorecard
    ADD CONSTRAINT repo_id_copy_1 FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id);


--
-- Name: repo_deps_libyear repo_id_copy_2; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_deps_libyear
    ADD CONSTRAINT repo_id_copy_2 FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id);


--
-- Name: repo_insights_records repo_id_ref; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_insights_records
    ADD CONSTRAINT repo_id_ref FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: repo_sbom_scans repo_linker_sbom; Type: FK CONSTRAINT; Schema: augur_data; Owner: augur
--

ALTER TABLE ONLY augur_data.repo_sbom_scans
    ADD CONSTRAINT repo_linker_sbom FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: client_applications client_application_user_id_fkey; Type: FK CONSTRAINT; Schema: augur_operations; Owner: augur
--

ALTER TABLE ONLY augur_operations.client_applications
    ADD CONSTRAINT client_application_user_id_fkey FOREIGN KEY (user_id) REFERENCES augur_operations.users(user_id);


--
-- Name: collection_status collection_status_repo_id_fk; Type: FK CONSTRAINT; Schema: augur_operations; Owner: augur
--

ALTER TABLE ONLY augur_operations.collection_status
    ADD CONSTRAINT collection_status_repo_id_fk FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id);


--
-- Name: refresh_tokens refresh_token_session_token_id_fkey; Type: FK CONSTRAINT; Schema: augur_operations; Owner: augur
--

ALTER TABLE ONLY augur_operations.refresh_tokens
    ADD CONSTRAINT refresh_token_session_token_id_fkey FOREIGN KEY (user_session_token) REFERENCES augur_operations.user_session_tokens(token);


--
-- Name: subscriptions subscriptions_application_id_fkey; Type: FK CONSTRAINT; Schema: augur_operations; Owner: augur
--

ALTER TABLE ONLY augur_operations.subscriptions
    ADD CONSTRAINT subscriptions_application_id_fkey FOREIGN KEY (application_id) REFERENCES augur_operations.client_applications(id);


--
-- Name: subscriptions subscriptions_type_id_fkey; Type: FK CONSTRAINT; Schema: augur_operations; Owner: augur
--

ALTER TABLE ONLY augur_operations.subscriptions
    ADD CONSTRAINT subscriptions_type_id_fkey FOREIGN KEY (type_id) REFERENCES augur_operations.subscription_types(id);


--
-- Name: user_groups user_groups_user_id_fkey; Type: FK CONSTRAINT; Schema: augur_operations; Owner: augur
--

ALTER TABLE ONLY augur_operations.user_groups
    ADD CONSTRAINT user_groups_user_id_fkey FOREIGN KEY (user_id) REFERENCES augur_operations.users(user_id);


--
-- Name: user_repos user_repos_group_id_fkey; Type: FK CONSTRAINT; Schema: augur_operations; Owner: augur
--

ALTER TABLE ONLY augur_operations.user_repos
    ADD CONSTRAINT user_repos_group_id_fkey FOREIGN KEY (group_id) REFERENCES augur_operations.user_groups(group_id);


--
-- Name: user_repos user_repos_repo_id_fkey; Type: FK CONSTRAINT; Schema: augur_operations; Owner: augur
--

ALTER TABLE ONLY augur_operations.user_repos
    ADD CONSTRAINT user_repos_repo_id_fkey FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id);


--
-- Name: user_session_tokens user_session_token_application_id_fkey; Type: FK CONSTRAINT; Schema: augur_operations; Owner: augur
--

ALTER TABLE ONLY augur_operations.user_session_tokens
    ADD CONSTRAINT user_session_token_application_id_fkey FOREIGN KEY (application_id) REFERENCES augur_operations.client_applications(id);


--
-- Name: user_session_tokens user_session_token_user_fk; Type: FK CONSTRAINT; Schema: augur_operations; Owner: augur
--

ALTER TABLE ONLY augur_operations.user_session_tokens
    ADD CONSTRAINT user_session_token_user_fk FOREIGN KEY (user_id) REFERENCES augur_operations.users(user_id);


--
-- Name: annotations annotations_annotation_type_id_fkey; Type: FK CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.annotations
    ADD CONSTRAINT annotations_annotation_type_id_fkey FOREIGN KEY (annotation_type_id) REFERENCES spdx.annotation_types(annotation_type_id);


--
-- Name: annotations annotations_creator_id_fkey; Type: FK CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.annotations
    ADD CONSTRAINT annotations_creator_id_fkey FOREIGN KEY (creator_id) REFERENCES spdx.creators(creator_id);


--
-- Name: annotations annotations_document_id_fkey; Type: FK CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.annotations
    ADD CONSTRAINT annotations_document_id_fkey FOREIGN KEY (document_id) REFERENCES spdx.documents(document_id);


--
-- Name: annotations annotations_identifier_id_fkey; Type: FK CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.annotations
    ADD CONSTRAINT annotations_identifier_id_fkey FOREIGN KEY (identifier_id) REFERENCES spdx.identifiers(identifier_id);


--
-- Name: creators creators_creator_type_id_fkey; Type: FK CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.creators
    ADD CONSTRAINT creators_creator_type_id_fkey FOREIGN KEY (creator_type_id) REFERENCES spdx.creator_types(creator_type_id);


--
-- Name: documents_creators documents_creators_creator_id_fkey; Type: FK CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.documents_creators
    ADD CONSTRAINT documents_creators_creator_id_fkey FOREIGN KEY (creator_id) REFERENCES spdx.creators(creator_id);


--
-- Name: documents_creators documents_creators_document_id_fkey; Type: FK CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.documents_creators
    ADD CONSTRAINT documents_creators_document_id_fkey FOREIGN KEY (document_id) REFERENCES spdx.documents(document_id);


--
-- Name: documents documents_data_license_id_fkey; Type: FK CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.documents
    ADD CONSTRAINT documents_data_license_id_fkey FOREIGN KEY (data_license_id) REFERENCES spdx.licenses(license_id);


--
-- Name: documents documents_document_namespace_id_fkey; Type: FK CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.documents
    ADD CONSTRAINT documents_document_namespace_id_fkey FOREIGN KEY (document_namespace_id) REFERENCES spdx.document_namespaces(document_namespace_id);


--
-- Name: documents documents_package_id_fkey; Type: FK CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.documents
    ADD CONSTRAINT documents_package_id_fkey FOREIGN KEY (package_id) REFERENCES spdx.packages(package_id);


--
-- Name: external_refs external_refs_document_id_fkey; Type: FK CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.external_refs
    ADD CONSTRAINT external_refs_document_id_fkey FOREIGN KEY (document_id) REFERENCES spdx.documents(document_id);


--
-- Name: external_refs external_refs_document_namespace_id_fkey; Type: FK CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.external_refs
    ADD CONSTRAINT external_refs_document_namespace_id_fkey FOREIGN KEY (document_namespace_id) REFERENCES spdx.document_namespaces(document_namespace_id);


--
-- Name: file_contributors file_contributors_file_id_fkey; Type: FK CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.file_contributors
    ADD CONSTRAINT file_contributors_file_id_fkey FOREIGN KEY (file_id) REFERENCES spdx.files(file_id);


--
-- Name: files_licenses files_licenses_file_id_fkey; Type: FK CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.files_licenses
    ADD CONSTRAINT files_licenses_file_id_fkey FOREIGN KEY (file_id) REFERENCES spdx.files(file_id);


--
-- Name: files_licenses files_licenses_license_id_fkey; Type: FK CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.files_licenses
    ADD CONSTRAINT files_licenses_license_id_fkey FOREIGN KEY (license_id) REFERENCES spdx.licenses(license_id);


--
-- Name: files_scans files_scans_file_id_fkey; Type: FK CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.files_scans
    ADD CONSTRAINT files_scans_file_id_fkey FOREIGN KEY (file_id) REFERENCES spdx.files(file_id);


--
-- Name: files_scans files_scans_scanner_id_fkey; Type: FK CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.files_scans
    ADD CONSTRAINT files_scans_scanner_id_fkey FOREIGN KEY (scanner_id) REFERENCES spdx.scanners(scanner_id);


--
-- Name: packages_files fk_package_files_packages; Type: FK CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.packages_files
    ADD CONSTRAINT fk_package_files_packages FOREIGN KEY (package_id) REFERENCES spdx.packages(package_id);


--
-- Name: packages fk_package_packages_files; Type: FK CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.packages
    ADD CONSTRAINT fk_package_packages_files FOREIGN KEY (ver_code_excluded_file_id) REFERENCES spdx.packages_files(package_file_id);


--
-- Name: identifiers identifiers_document_id_fkey; Type: FK CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.identifiers
    ADD CONSTRAINT identifiers_document_id_fkey FOREIGN KEY (document_id) REFERENCES spdx.documents(document_id);


--
-- Name: identifiers identifiers_document_namespace_id_fkey; Type: FK CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.identifiers
    ADD CONSTRAINT identifiers_document_namespace_id_fkey FOREIGN KEY (document_namespace_id) REFERENCES spdx.document_namespaces(document_namespace_id);


--
-- Name: identifiers identifiers_package_file_id_fkey; Type: FK CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.identifiers
    ADD CONSTRAINT identifiers_package_file_id_fkey FOREIGN KEY (package_file_id) REFERENCES spdx.packages_files(package_file_id);


--
-- Name: identifiers identifiers_package_id_fkey; Type: FK CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.identifiers
    ADD CONSTRAINT identifiers_package_id_fkey FOREIGN KEY (package_id) REFERENCES spdx.packages(package_id);


--
-- Name: packages packages_concluded_license_id_fkey; Type: FK CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.packages
    ADD CONSTRAINT packages_concluded_license_id_fkey FOREIGN KEY (concluded_license_id) REFERENCES spdx.licenses(license_id);


--
-- Name: packages packages_declared_license_id_fkey; Type: FK CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.packages
    ADD CONSTRAINT packages_declared_license_id_fkey FOREIGN KEY (declared_license_id) REFERENCES spdx.licenses(license_id);


--
-- Name: packages_files packages_files_concluded_license_id_fkey; Type: FK CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.packages_files
    ADD CONSTRAINT packages_files_concluded_license_id_fkey FOREIGN KEY (concluded_license_id) REFERENCES spdx.licenses(license_id);


--
-- Name: packages_files packages_files_file_id_fkey; Type: FK CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.packages_files
    ADD CONSTRAINT packages_files_file_id_fkey FOREIGN KEY (file_id) REFERENCES spdx.files(file_id);


--
-- Name: packages packages_originator_id_fkey; Type: FK CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.packages
    ADD CONSTRAINT packages_originator_id_fkey FOREIGN KEY (originator_id) REFERENCES spdx.creators(creator_id);


--
-- Name: packages_scans packages_scans_package_id_fkey; Type: FK CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.packages_scans
    ADD CONSTRAINT packages_scans_package_id_fkey FOREIGN KEY (package_id) REFERENCES spdx.packages(package_id);


--
-- Name: packages_scans packages_scans_scanner_id_fkey; Type: FK CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.packages_scans
    ADD CONSTRAINT packages_scans_scanner_id_fkey FOREIGN KEY (scanner_id) REFERENCES spdx.scanners(scanner_id);


--
-- Name: packages packages_supplier_id_fkey; Type: FK CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.packages
    ADD CONSTRAINT packages_supplier_id_fkey FOREIGN KEY (supplier_id) REFERENCES spdx.creators(creator_id);


--
-- Name: relationships relationships_left_identifier_id_fkey; Type: FK CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.relationships
    ADD CONSTRAINT relationships_left_identifier_id_fkey FOREIGN KEY (left_identifier_id) REFERENCES spdx.identifiers(identifier_id);


--
-- Name: relationships relationships_relationship_type_id_fkey; Type: FK CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.relationships
    ADD CONSTRAINT relationships_relationship_type_id_fkey FOREIGN KEY (relationship_type_id) REFERENCES spdx.relationship_types(relationship_type_id);


--
-- Name: relationships relationships_right_identifier_id_fkey; Type: FK CONSTRAINT; Schema: spdx; Owner: augur
--

ALTER TABLE ONLY spdx.relationships
    ADD CONSTRAINT relationships_right_identifier_id_fkey FOREIGN KEY (right_identifier_id) REFERENCES spdx.identifiers(identifier_id);


--
-- Name: api_get_all_repo_prs; Type: MATERIALIZED VIEW DATA; Schema: augur_data; Owner: augur
--

REFRESH MATERIALIZED VIEW augur_data.api_get_all_repo_prs;


--
-- Name: api_get_all_repos_commits; Type: MATERIALIZED VIEW DATA; Schema: augur_data; Owner: augur
--

REFRESH MATERIALIZED VIEW augur_data.api_get_all_repos_commits;


--
-- Name: api_get_all_repos_issues; Type: MATERIALIZED VIEW DATA; Schema: augur_data; Owner: augur
--

REFRESH MATERIALIZED VIEW augur_data.api_get_all_repos_issues;


--
-- Name: augur_new_contributors; Type: MATERIALIZED VIEW DATA; Schema: augur_data; Owner: augur
--

REFRESH MATERIALIZED VIEW augur_data.augur_new_contributors;


--
-- Name: explorer_commits_and_committers_daily_count; Type: MATERIALIZED VIEW DATA; Schema: augur_data; Owner: augur
--

REFRESH MATERIALIZED VIEW augur_data.explorer_commits_and_committers_daily_count;


--
-- Name: explorer_contributor_actions; Type: MATERIALIZED VIEW DATA; Schema: augur_data; Owner: augur
--

REFRESH MATERIALIZED VIEW augur_data.explorer_contributor_actions;


--
-- Name: explorer_entry_list; Type: MATERIALIZED VIEW DATA; Schema: augur_data; Owner: augur
--

REFRESH MATERIALIZED VIEW augur_data.explorer_entry_list;


--
-- Name: explorer_libyear_all; Type: MATERIALIZED VIEW DATA; Schema: augur_data; Owner: augur
--

REFRESH MATERIALIZED VIEW augur_data.explorer_libyear_all;


--
-- Name: explorer_libyear_detail; Type: MATERIALIZED VIEW DATA; Schema: augur_data; Owner: augur
--

REFRESH MATERIALIZED VIEW augur_data.explorer_libyear_detail;


--
-- Name: explorer_libyear_summary; Type: MATERIALIZED VIEW DATA; Schema: augur_data; Owner: augur
--

REFRESH MATERIALIZED VIEW augur_data.explorer_libyear_summary;


--
-- Name: explorer_new_contributors; Type: MATERIALIZED VIEW DATA; Schema: augur_data; Owner: augur
--

REFRESH MATERIALIZED VIEW augur_data.explorer_new_contributors;


--
-- PostgreSQL database dump complete
--

