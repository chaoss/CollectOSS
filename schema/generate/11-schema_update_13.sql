-- #SPDX-License-Identifier: MIT
DROP INDEX "augur_data"."domain,active";

DROP INDEX "augur_data"."domain,affiliation,start_date";

ALTER TABLE "augur_data"."contributor_affiliations" ADD COLUMN "ca_last_used" timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE "augur_data"."contributor_affiliations" DROP COLUMN "ca_affiliation";

ALTER TABLE "augur_data"."contributor_affiliations" DROP COLUMN "ca_active";

ALTER TABLE "augur_data"."contributor_affiliations" DROP COLUMN "ca_last_modified";

update "augur_operations"."augur_settings" set value = 13 where setting = 'augur_data_version'; 
