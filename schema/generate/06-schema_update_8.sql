-- #SPDX-License-Identifier: MIT
/***
Database update script. For release 8. 

***/ 


-------------------------------------------------
-- Database history table.  If the tables does not exist, then create it and populate it and run all this stuff. 
-- This works for everything we already have deployed. After that, we will need the script to check the version in the table. 
-- This release is version 8 of the schema. 
-------------------------------------------------
CREATE TABLE "augur_operations"."augur_settings" (
"id" serial8 NOT NULL,
"setting" varchar,
"value" varchar,
"last_modified" timestamp(0) DEFAULT CURRENT_DATE,
PRIMARY KEY ("id") 
)
WITHOUT OIDS;
ALTER TABLE "augur_operations"."augur_settings" OWNER TO "augur";


INSERT INTO "augur_operations"."augur_settings"("id", "setting", "value", "last_modified") VALUES (1, 'augur_data_version', '8', '2019-11-18 08:41:51');

-------------------------------------------------

-------------------------------------------------


-- Updates to commit timestamps
ALTER TABLE "augur_data"."commits" ALTER COLUMN "cmt_author_timestamp" TYPE timestamptz(0) USING "cmt_author_timestamp"::timestamptz(0);

ALTER TABLE "augur_data"."commits" ALTER COLUMN "cmt_committer_timestamp" TYPE timestamptz(0) USING "cmt_committer_timestamp"::timestamptz(0);



-- New operations tables

CREATE TABLE "augur_operations"."worker_settings_facade" (
"id" int4 NOT NULL,
"setting" varchar(32) COLLATE "default" NOT NULL,
"value" varchar COLLATE "default" NOT NULL,
"last_modified" timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT "settings_pkey" PRIMARY KEY ("id") 
)
WITHOUT OIDS;
ALTER TABLE "augur_operations"."worker_settings_facade" OWNER TO "augur";

CREATE TABLE "augur_operations"."repos_fetch_log" (
"repos_id" int4 NOT NULL,
"status" varchar(128) COLLATE "default" NOT NULL,
"date" timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP
)
WITHOUT OIDS;
CREATE INDEX "repos_id,statusops" ON "augur_operations"."repos_fetch_log" USING btree ("repos_id" "pg_catalog"."int4_ops" ASC NULLS LAST, "status" "pg_catalog"."text_ops" ASC NULLS LAST);
ALTER TABLE "augur_operations"."repos_fetch_log" OWNER TO "augur";

CREATE TABLE "augur_operations"."working_commits" (
"repos_id" int4 NOT NULL,
"working_commit" varchar(40) COLLATE "default" DEFAULT 'NULL'::character varying
)
WITHOUT OIDS;
ALTER TABLE "augur_operations"."working_commits" OWNER TO "augur";

insert into "augur_operations"."worker_settings_facade"  select * from "augur_data"."settings"; 




-- Contributor Alias Updates
ALTER TABLE "augur_data"."contributors_aliases" ALTER COLUMN "data_collection_date" SET DEFAULT CURRENT_TIMESTAMP;




-- Repo Badging Table Update. 

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "id";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "user_id";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "name";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "description";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "homepage_url";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "repo_url";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "license";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "homepage_url_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "homepage_url_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "sites_https_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "sites_https_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "description_good_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "description_good_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "interact_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "interact_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "contribution_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "contribution_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "contribution_requirements_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "contribution_requirements_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "license_location_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "license_location_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "floss_license_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "floss_license_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "floss_license_osi_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "floss_license_osi_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "documentation_basics_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "documentation_basics_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "documentation_interface_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "documentation_interface_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "repo_public_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "repo_public_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "repo_track_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "repo_track_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "repo_interim_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "repo_interim_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "repo_distributed_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "repo_distributed_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "version_unique_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "version_unique_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "version_semver_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "version_semver_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "version_tags_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "version_tags_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "release_notes_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "release_notes_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "release_notes_vulns_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "release_notes_vulns_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "report_url_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "report_url_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "report_tracker_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "report_tracker_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "report_process_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "report_process_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "report_responses_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "report_responses_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "enhancement_responses_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "enhancement_responses_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "report_archive_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "report_archive_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "vulnerability_report_process_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "vulnerability_report_process_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "vulnerability_report_private_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "vulnerability_report_private_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "vulnerability_report_response_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "vulnerability_report_response_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "build_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "build_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "build_common_tools_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "build_common_tools_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "build_floss_tools_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "build_floss_tools_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "test_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "test_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "test_invocation_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "test_invocation_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "test_most_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "test_most_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "test_policy_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "test_policy_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "tests_are_added_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "tests_are_added_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "tests_documented_added_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "tests_documented_added_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "warnings_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "warnings_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "warnings_fixed_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "warnings_fixed_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "warnings_strict_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "warnings_strict_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "know_secure_design_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "know_secure_design_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "know_common_errors_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "know_common_errors_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "crypto_published_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "crypto_published_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "crypto_call_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "crypto_call_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "crypto_floss_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "crypto_floss_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "crypto_keylength_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "crypto_keylength_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "crypto_working_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "crypto_working_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "crypto_pfs_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "crypto_pfs_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "crypto_password_storage_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "crypto_password_storage_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "crypto_random_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "crypto_random_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "delivery_mitm_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "delivery_mitm_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "delivery_unsigned_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "delivery_unsigned_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "vulnerabilities_fixed_60_days_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "vulnerabilities_fixed_60_days_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "vulnerabilities_critical_fixed_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "vulnerabilities_critical_fixed_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "static_analysis_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "static_analysis_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "static_analysis_common_vulnerabilities_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "static_analysis_common_vulnerabilities_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "static_analysis_fixed_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "static_analysis_fixed_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "static_analysis_often_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "static_analysis_often_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "dynamic_analysis_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "dynamic_analysis_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "dynamic_analysis_unsafe_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "dynamic_analysis_unsafe_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "dynamic_analysis_enable_assertions_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "dynamic_analysis_enable_assertions_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "dynamic_analysis_fixed_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "dynamic_analysis_fixed_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "general_comments";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "updated_at";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "crypto_weaknesses_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "crypto_weaknesses_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "test_continuous_integration_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "test_continuous_integration_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "cpe";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "discussion_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "discussion_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "no_leaked_credentials_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "no_leaked_credentials_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "english_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "english_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "hardening_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "hardening_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "crypto_used_network_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "crypto_used_network_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "crypto_tls12_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "crypto_tls12_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "crypto_certificate_verification_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "crypto_certificate_verification_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "crypto_verification_private_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "crypto_verification_private_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "hardened_site_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "hardened_site_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "installation_common_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "installation_common_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "build_reproducible_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "build_reproducible_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "badge_percentage_0";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "achieved_passing_at";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "lost_passing_at";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "last_reminder_at";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "disabled_reminders";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "implementation_languages";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "lock_version";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "badge_percentage_1";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "dco_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "dco_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "governance_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "governance_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "code_of_conduct_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "code_of_conduct_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "roles_responsibilities_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "roles_responsibilities_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "access_continuity_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "access_continuity_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "bus_factor_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "bus_factor_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "documentation_roadmap_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "documentation_roadmap_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "documentation_architecture_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "documentation_architecture_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "documentation_security_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "documentation_security_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "documentation_quick_start_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "documentation_quick_start_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "documentation_current_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "documentation_current_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "documentation_achievements_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "documentation_achievements_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "accessibility_best_practices_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "accessibility_best_practices_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "internationalization_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "internationalization_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "sites_password_security_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "sites_password_security_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "maintenance_or_update_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "maintenance_or_update_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "vulnerability_report_credit_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "vulnerability_report_credit_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "vulnerability_response_process_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "vulnerability_response_process_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "coding_standards_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "coding_standards_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "coding_standards_enforced_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "coding_standards_enforced_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "build_standard_variables_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "build_standard_variables_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "build_preserve_debug_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "build_preserve_debug_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "build_non_recursive_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "build_non_recursive_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "build_repeatable_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "build_repeatable_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "installation_standard_variables_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "installation_standard_variables_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "installation_development_quick_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "installation_development_quick_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "external_dependencies_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "external_dependencies_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "dependency_monitoring_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "dependency_monitoring_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "updateable_reused_components_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "updateable_reused_components_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "interfaces_current_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "interfaces_current_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "automated_integration_testing_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "automated_integration_testing_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "regression_tests_added50_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "regression_tests_added50_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "test_statement_coverage80_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "test_statement_coverage80_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "test_policy_mandated_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "test_policy_mandated_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "implement_secure_design_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "implement_secure_design_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "input_validation_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "input_validation_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "crypto_algorithm_agility_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "crypto_algorithm_agility_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "crypto_credential_agility_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "crypto_credential_agility_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "signed_releases_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "signed_releases_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "version_tags_signed_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "version_tags_signed_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "badge_percentage_2";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "contributors_unassociated_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "contributors_unassociated_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "copyright_per_file_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "copyright_per_file_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "license_per_file_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "license_per_file_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "small_tasks_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "small_tasks_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "require_2FA_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "require_2FA_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "secure_2FA_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "secure_2FA_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "code_review_standards_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "code_review_standards_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "two_person_review_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "two_person_review_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "test_statement_coverage90_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "test_statement_coverage90_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "test_branch_coverage80_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "test_branch_coverage80_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "security_review_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "security_review_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "assurance_case_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "assurance_case_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "achieve_passing_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "achieve_passing_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "achieve_silver_status";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "achieve_silver_justification";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "tiered_percentage";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "badge_level";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "additional_rights";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "project_entry_license";

ALTER TABLE "augur_data"."repo_badging" DROP COLUMN "project_entry_attribution";

ALTER TABLE "augur_data"."repo_badging" ADD COLUMN "data" jsonb;

ALTER TABLE "augur_data"."repo_badging" ALTER COLUMN "created_at" TYPE timestamp(0) USING "created_at"::timestamp(0);

ALTER TABLE "augur_data"."repo_badging" ALTER COLUMN "created_at" SET DEFAULT CURRENT_TIMESTAMP;




