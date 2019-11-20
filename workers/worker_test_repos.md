# Data to test worker collection

```sql
-- ----------------------------
-- Records of repo_groups
-- ----------------------------
BEGIN;
INSERT INTO "augur_data"."repo_groups" VALUES (20, ' "Sample Database Repo Group Two"', '', '', 0, '2019-10-19 16:02:23', 'Unknown', 'Loaded by user', '1.0', 'Git', '2019-10-19 16:02:23');
INSERT INTO "augur_data"."repo_groups" VALUES (10, ' "Sample Database Repo Group One"', '', '', 0, '2019-10-19 16:02:23', 'Unknown', 'Loaded by user', '1.0', 'Git', '2019-10-19 16:02:23');
COMMIT;


-- ----------------------------
-- Records of repo
-- ----------------------------
BEGIN;
INSERT INTO "augur_data"."repo" VALUES (25433, 20, 'https://github.com/chaoss/wg-risk.git', 'github.com/chaoss/', 'wg-risk', '2019-10-19 16:03:01', 'Complete', '', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'CLI', '1.0', 'Git', '2019-10-19 16:03:01');
INSERT INTO "augur_data"."repo" VALUES (25434, 20, 'https://github.com/chaoss/wg-common.git', 'github.com/chaoss/', 'wg-common', '2019-10-19 16:03:01', 'Complete', '', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'CLI', '1.0', 'Git', '2019-10-19 16:03:01');
INSERT INTO "augur_data"."repo" VALUES (25430, 10, 'https://github.com/chaoss/augur.git', 'github.com/chaoss/', 'augur', '2019-10-19 16:03:01', 'Complete', '', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'CLI', '1.0', 'Git', '2019-10-19 16:03:01');
INSERT INTO "augur_data"."repo" VALUES (25431, 20, 'https://github.com/chaoss/grimoirelab.git', 'github.com/chaoss/', 'grimoirelab', '2019-10-19 16:03:01', 'Complete', '', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'CLI', '1.0', 'Git', '2019-10-19 16:03:01');
INSERT INTO "augur_data"."repo" VALUES (25432, 20, 'https://github.com/chaoss/wg-evolution.git', 'github.com/chaoss/', 'wg-evolution', '2019-10-19 16:03:01', 'Complete', '', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'CLI', '1.0', 'Git', '2019-10-19 16:03:01');
COMMIT;

```