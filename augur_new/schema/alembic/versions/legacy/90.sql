BEGIN; 

DROP INDEX "augur_data"."cmt-committer-date-idx3";

DROP INDEX "augur_data"."cmt_author-name-idx5";

DROP INDEX "augur_data"."cmt_cmmter-name-idx4";

DROP INDEX "augur_data"."commits_idx_cmt_email_cmt_date_cmt_name2";

DROP INDEX "augur_data"."commits_idx_cmt_name_cmt_date2";

DROP INDEX "augur_data"."commits_idx_cmt_name_cmt_date_cmt_date3";

DROP INDEX "augur_data"."commits_idx_repo_id_cmt_ema_cmt_nam_cmt_dat2";

DROP INDEX "augur_data"."commits_idx_repo_id_cmt_ema_cmt_nam_cmt_dat3";

DROP INDEX "augur_data"."committer_cntrb_id";


update "augur_operations"."augur_settings" set value = 90 where setting = 'augur_data_version'; 


COMMIT; 