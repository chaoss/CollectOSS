BEGIN; 

ALTER TABLE "augur_data"."contributors" ADD COLUMN "gl_id" int8;

ALTER TABLE "augur_data"."contributors" ADD COLUMN "gl_full_name" varchar COLLATE "pg_catalog"."default";

ALTER TABLE "augur_data"."contributors" ADD COLUMN "gl_username" varchar COLLATE "pg_catalog"."default";

ALTER TABLE "augur_data"."contributors" ADD COLUMN "gl_state" varchar COLLATE "pg_catalog"."default";

ALTER TABLE "augur_data"."contributors" ADD COLUMN "gl_avatar_url" varchar COLLATE "pg_catalog"."default";

ALTER TABLE "augur_data"."contributors" ADD COLUMN "gl_web_url" varchar COLLATE "pg_catalog"."default";

COMMENT ON COLUMN "augur_data"."contributors"."gl_id" IS '"id" value from these API calls to GitLab, all for the same user

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

COMMENT ON COLUMN "augur_data"."contributors"."gl_full_name" IS '“name” value from these API calls to GitLab, all for the same user

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

COMMENT ON COLUMN "augur_data"."contributors"."gl_username" IS '“username” value from these API calls to GitLab, all for the same user

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

COMMENT ON COLUMN "augur_data"."contributors"."gl_state" IS '“state” value from these API calls to GitLab, all for the same user

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

COMMENT ON COLUMN "augur_data"."contributors"."gl_avatar_url" IS '“avatar_url” value from these API calls to GitLab, all for the same user

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

COMMENT ON COLUMN "augur_data"."contributors"."gl_web_url" IS '“web_url” value from these API calls to GitLab, all for the same user

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

update "augur_operations"."augur_settings" set value = 57 where setting = 'augur_data_version';

COMMIT; 
