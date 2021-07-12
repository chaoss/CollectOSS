BEGIN; 

alter index if exists cmt_author_contrib_worker set (pages_per_range = 64,autosummarize = on);
alter index if exists cmt_commiter_contrib_worker set (pages_per_range = 64,autosummarize = on);
alter index if exists contributor_delete_finder set (pages_per_range = 64,autosummarize = on);
alter index if exists contributor_worker_finder set (pages_per_range = 64,autosummarize = on);
alter index if exists contributor_worker_fullname_finder set (pages_per_range = 64,autosummarize = on);
alter index if exists contributor_worker_email_finder set (pages_per_range = 64,autosummarize = on);

update "augur_operations"."augur_settings" set value = 56 where setting = 'augur_data_version';

COMMIT; 
