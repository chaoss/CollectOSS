## Readme File for Value Worker Creation
Most of the installation for the value worker is handled by the general augur installation script. As noted there, the only thing you *have* to do is make sure that the `Go` programming language is installed. 


### Installing the value worker: 
1. Install the go language following operating system specific instructions at : https://golang.org/doc/install 
2. Install scc with `go get -u github.com/boyter/scc/`
3. set the `scc_bin` value in the value_worker block of `augur.config.json` to the location of the scc excecutable installed above. For example, `/home/sean/go/bin/scc`

#### Housekeeper Block for `augur.config.json`

```json
      {
    "delay": 100000,
    "given": ["git_url"],
    "model": "value",
    "repo_group_id": 0
      }
```

#### Worker Block for `augur.config.json`
```json
        "value_worker": {
            "port": 58611,
            "scc_bin": "/home/sean/go/bin/scc",
            "switch": 0,
            "workers": 1
        }
```

1. This is how I ran SCC against facade repositories on a server: 
`/root/go/bin/scc /home/sean/facade/git-repos/15/github.com/microprofile/wpsite/ . >> https:--github.com-microprofile-wpsite.git.csv`
2. We want to wrap this in Python: https://github.com/boyter/scc as an Augur worker/plugin. 
3. Key Steps:   
    - Make the "worker" so it inserts into the database. 
    - Identify what installation might look like.  I think it will need to be installed as kind of a "worker that calls an installed piece of software" and writes it to our database. 
4. Augur now installs with `make install` ... 
5. The process requires a .git repository ... and so the way I handled that was I identified the facade_worker repository directory and scanned it. 
    - We have an API endpoint to get that information ... remind me where that is ... 
    - Default to running it on all the repositories
6. repo_labor is the intended table ... and the intended design is to count the lines of code and complexity for each file in a repository and store it. 
7. Then an API endpoint would return summarization type data, like 
    - language
    - etc. 
    - loc
    - complexity
    - ... 
8. Not sure if this is easy, but I would like the worker to allow for a parameterized calculation of labor cost .. $/hr etc ... into labor/complexity 
9. The repo_labor table might not cover everything ... 
```sql
CREATE TABLE "augur_data"."repo_labor" (
  "repo_labor_id" int8 NOT NULL DEFAULT nextval('"augur_data".repo_labor_repo_labor_id_seq'::regclass),
  "repo_id" int8,
  "repo_clone_date" timestamp(0),
  "rl_analysis_date" timestamp(0),
  "programming_language" varchar(255) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "file_path" varchar(500) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "file_name" varchar(255) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "total_lines" int4,
  "code_lines" int4,
  "comment_lines" int4,
  "blank_lines" int4,
  "code_complexity" int4,
  "repo_url" varchar(500) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0)
)
;
ALTER TABLE "augur_data"."repo_labor" OWNER TO "augur";
COMMENT ON COLUMN "augur_data"."repo_labor"."repo_url" IS 'This is a convenience column to simplify analysis against external datasets';
COMMENT ON TABLE "augur_data"."repo_labor" IS 'repo_labor is a derivative of tables used to store scc code and complexity counting statistics that are inputs to labor analysis, which are components of CHAOSS value metric calculations. ';

-- ----------------------------
-- Primary Key structure for table repo_labor
-- ----------------------------
ALTER TABLE "augur_data"."repo_labor" ADD CONSTRAINT "repo_labor_pkey" PRIMARY KEY ("repo_labor_id");

-- ----------------------------
-- Foreign Keys structure for table repo_labor
-- ----------------------------
ALTER TABLE "augur_data"."repo_labor" ADD CONSTRAINT "fk_repo_labor_repo_1" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

```
10. There are many different parameters that can be used to run this scc program ... the one in the example is what I did to populate repo_labor .... but there may be other functions that are useful for summarizing labor cost. 


