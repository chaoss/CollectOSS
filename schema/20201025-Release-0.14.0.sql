-- #SPDX-License-Identifier: MIT
-- ----------------------------

CREATE SCHEMA IF NOT EXISTS augur_data;
CREATE SCHEMA IF NOT EXISTS augur_operations;
CREATE SCHEMA IF NOT EXISTS spdx;
-- create the schemas
-- -----------------------

-- ----------------------------
-- Sequence structure for annotation_types_annotation_type_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."annotation_types_annotation_type_id_seq";
CREATE SEQUENCE "spdx"."annotation_types_annotation_type_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."annotation_types_annotation_type_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for annotations_annotation_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."annotations_annotation_id_seq";
CREATE SEQUENCE "spdx"."annotations_annotation_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."annotations_annotation_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for augur_repo_map_map_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."augur_repo_map_map_id_seq";
CREATE SEQUENCE "spdx"."augur_repo_map_map_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."augur_repo_map_map_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for creator_types_creator_type_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."creator_types_creator_type_id_seq";
CREATE SEQUENCE "spdx"."creator_types_creator_type_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."creator_types_creator_type_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for creators_creator_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."creators_creator_id_seq";
CREATE SEQUENCE "spdx"."creators_creator_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."creators_creator_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for document_namespaces_document_namespace_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."document_namespaces_document_namespace_id_seq";
CREATE SEQUENCE "spdx"."document_namespaces_document_namespace_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."document_namespaces_document_namespace_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for documents_creators_document_creator_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."documents_creators_document_creator_id_seq";
CREATE SEQUENCE "spdx"."documents_creators_document_creator_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."documents_creators_document_creator_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for documents_document_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."documents_document_id_seq";
CREATE SEQUENCE "spdx"."documents_document_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."documents_document_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for external_refs_external_ref_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."external_refs_external_ref_id_seq";
CREATE SEQUENCE "spdx"."external_refs_external_ref_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."external_refs_external_ref_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for file_contributors_file_contributor_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."file_contributors_file_contributor_id_seq";
CREATE SEQUENCE "spdx"."file_contributors_file_contributor_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."file_contributors_file_contributor_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for files_file_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."files_file_id_seq";
CREATE SEQUENCE "spdx"."files_file_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."files_file_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for files_licenses_file_license_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."files_licenses_file_license_id_seq";
CREATE SEQUENCE "spdx"."files_licenses_file_license_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."files_licenses_file_license_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for files_scans_file_scan_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."files_scans_file_scan_id_seq";
CREATE SEQUENCE "spdx"."files_scans_file_scan_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."files_scans_file_scan_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for identifiers_identifier_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."identifiers_identifier_id_seq";
CREATE SEQUENCE "spdx"."identifiers_identifier_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."identifiers_identifier_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for licenses_license_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."licenses_license_id_seq";
CREATE SEQUENCE "spdx"."licenses_license_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."licenses_license_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for packages_files_package_file_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."packages_files_package_file_id_seq";
CREATE SEQUENCE "spdx"."packages_files_package_file_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."packages_files_package_file_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for packages_package_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."packages_package_id_seq";
CREATE SEQUENCE "spdx"."packages_package_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."packages_package_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for packages_scans_package_scan_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."packages_scans_package_scan_id_seq";
CREATE SEQUENCE "spdx"."packages_scans_package_scan_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."packages_scans_package_scan_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for projects_package_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."projects_package_id_seq";
CREATE SEQUENCE "spdx"."projects_package_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."projects_package_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for relationship_types_relationship_type_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."relationship_types_relationship_type_id_seq";
CREATE SEQUENCE "spdx"."relationship_types_relationship_type_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."relationship_types_relationship_type_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for relationships_relationship_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."relationships_relationship_id_seq";
CREATE SEQUENCE "spdx"."relationships_relationship_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."relationships_relationship_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for scanners_scanner_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "spdx"."scanners_scanner_id_seq";
CREATE SEQUENCE "spdx"."scanners_scanner_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "spdx"."scanners_scanner_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for augur_settings_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_operations"."augur_settings_id_seq";
CREATE SEQUENCE "augur_operations"."augur_settings_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "augur_operations"."augur_settings_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for gh_worker_history_history_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_operations"."gh_worker_history_history_id_seq";
CREATE SEQUENCE "augur_operations"."gh_worker_history_history_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "augur_operations"."gh_worker_history_history_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for worker_oauth_oauth_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_operations"."worker_oauth_oauth_id_seq";
CREATE SEQUENCE "augur_operations"."worker_oauth_oauth_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1000
CACHE 1;
ALTER SEQUENCE "augur_operations"."worker_oauth_oauth_id_seq" OWNER TO "augur";

-- ----------------------------

-- ----------------------------
-- Sequence structure for augur_data.repo_insights_ri_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."augur_data.repo_insights_ri_id_seq";
CREATE SEQUENCE "augur_data"."augur_data.repo_insights_ri_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25430
CACHE 1;
ALTER SEQUENCE "augur_data"."augur_data.repo_insights_ri_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for chaoss_metric_status_cms_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."chaoss_metric_status_cms_id_seq";
CREATE SEQUENCE "augur_data"."chaoss_metric_status_cms_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "augur_data"."chaoss_metric_status_cms_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for commit_comment_ref_cmt_comment_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."commit_comment_ref_cmt_comment_id_seq";
CREATE SEQUENCE "augur_data"."commit_comment_ref_cmt_comment_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25430
CACHE 1;
ALTER SEQUENCE "augur_data"."commit_comment_ref_cmt_comment_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for commit_parents_parent_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."commit_parents_parent_id_seq";
CREATE SEQUENCE "augur_data"."commit_parents_parent_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25430
CACHE 1;
ALTER SEQUENCE "augur_data"."commit_parents_parent_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for commits_cmt_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."commits_cmt_id_seq";
CREATE SEQUENCE "augur_data"."commits_cmt_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25430
CACHE 1;
ALTER SEQUENCE "augur_data"."commits_cmt_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for contributor_affiliations_ca_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."contributor_affiliations_ca_id_seq";
CREATE SEQUENCE "augur_data"."contributor_affiliations_ca_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25430
CACHE 1;
ALTER SEQUENCE "augur_data"."contributor_affiliations_ca_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for contributors_aliases_cntrb_a_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."contributors_aliases_cntrb_a_id_seq";
CREATE SEQUENCE "augur_data"."contributors_aliases_cntrb_a_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25430
CACHE 1;
ALTER SEQUENCE "augur_data"."contributors_aliases_cntrb_a_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for contributors_cntrb_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."contributors_cntrb_id_seq";
CREATE SEQUENCE "augur_data"."contributors_cntrb_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25430
CACHE 1;
ALTER SEQUENCE "augur_data"."contributors_cntrb_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for contributors_history_cntrb_history_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."contributors_history_cntrb_history_id_seq";
CREATE SEQUENCE "augur_data"."contributors_history_cntrb_history_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25430
CACHE 1;
ALTER SEQUENCE "augur_data"."contributors_history_cntrb_history_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for discourse_insights_msg_discourse_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."discourse_insights_msg_discourse_id_seq";
CREATE SEQUENCE "augur_data"."discourse_insights_msg_discourse_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "augur_data"."discourse_insights_msg_discourse_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for issue_assignees_issue_assignee_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."issue_assignees_issue_assignee_id_seq";
CREATE SEQUENCE "augur_data"."issue_assignees_issue_assignee_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "augur_data"."issue_assignees_issue_assignee_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for issue_events_event_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."issue_events_event_id_seq";
CREATE SEQUENCE "augur_data"."issue_events_event_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25430
CACHE 1;
ALTER SEQUENCE "augur_data"."issue_events_event_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for issue_labels_issue_label_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."issue_labels_issue_label_id_seq";
CREATE SEQUENCE "augur_data"."issue_labels_issue_label_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25430
CACHE 1;
ALTER SEQUENCE "augur_data"."issue_labels_issue_label_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for issue_message_ref_issue_msg_ref_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."issue_message_ref_issue_msg_ref_id_seq";
CREATE SEQUENCE "augur_data"."issue_message_ref_issue_msg_ref_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25430
CACHE 1;
ALTER SEQUENCE "augur_data"."issue_message_ref_issue_msg_ref_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for issue_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."issue_seq";
CREATE SEQUENCE "augur_data"."issue_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 31000
CACHE 1;
ALTER SEQUENCE "augur_data"."issue_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for libraries_library_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."libraries_library_id_seq";
CREATE SEQUENCE "augur_data"."libraries_library_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25430
CACHE 1;
ALTER SEQUENCE "augur_data"."libraries_library_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for library_dependencies_lib_dependency_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."library_dependencies_lib_dependency_id_seq";
CREATE SEQUENCE "augur_data"."library_dependencies_lib_dependency_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25430
CACHE 1;
ALTER SEQUENCE "augur_data"."library_dependencies_lib_dependency_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for library_version_library_version_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."library_version_library_version_id_seq";
CREATE SEQUENCE "augur_data"."library_version_library_version_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25430
CACHE 1;
ALTER SEQUENCE "augur_data"."library_version_library_version_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for lstm_anomaly_models_model_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."lstm_anomaly_models_model_id_seq";
CREATE SEQUENCE "augur_data"."lstm_anomaly_models_model_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "augur_data"."lstm_anomaly_models_model_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for lstm_anomaly_results_result_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."lstm_anomaly_results_result_id_seq";
CREATE SEQUENCE "augur_data"."lstm_anomaly_results_result_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "augur_data"."lstm_anomaly_results_result_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for message_analysis_msg_analysis_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."message_analysis_msg_analysis_id_seq";
CREATE SEQUENCE "augur_data"."message_analysis_msg_analysis_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "augur_data"."message_analysis_msg_analysis_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for message_analysis_summary_msg_summary_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."message_analysis_summary_msg_summary_id_seq";
CREATE SEQUENCE "augur_data"."message_analysis_summary_msg_summary_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "augur_data"."message_analysis_summary_msg_summary_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for message_msg_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."message_msg_id_seq";
CREATE SEQUENCE "augur_data"."message_msg_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25430
CACHE 1;
ALTER SEQUENCE "augur_data"."message_msg_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for message_sentiment_msg_analysis_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."message_sentiment_msg_analysis_id_seq";
CREATE SEQUENCE "augur_data"."message_sentiment_msg_analysis_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "augur_data"."message_sentiment_msg_analysis_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for message_sentiment_summary_msg_summary_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."message_sentiment_summary_msg_summary_id_seq";
CREATE SEQUENCE "augur_data"."message_sentiment_summary_msg_summary_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "augur_data"."message_sentiment_summary_msg_summary_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for platform_pltfrm_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."platform_pltfrm_id_seq";
CREATE SEQUENCE "augur_data"."platform_pltfrm_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25430
CACHE 1;
ALTER SEQUENCE "augur_data"."platform_pltfrm_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for pull_request_assignees_pr_assignee_map_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."pull_request_assignees_pr_assignee_map_id_seq";
CREATE SEQUENCE "augur_data"."pull_request_assignees_pr_assignee_map_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25430
CACHE 1;
ALTER SEQUENCE "augur_data"."pull_request_assignees_pr_assignee_map_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for pull_request_commits_pr_cmt_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."pull_request_commits_pr_cmt_id_seq";
CREATE SEQUENCE "augur_data"."pull_request_commits_pr_cmt_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "augur_data"."pull_request_commits_pr_cmt_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for pull_request_events_pr_event_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."pull_request_events_pr_event_id_seq";
CREATE SEQUENCE "augur_data"."pull_request_events_pr_event_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25430
CACHE 1;
ALTER SEQUENCE "augur_data"."pull_request_events_pr_event_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for pull_request_files_pr_file_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."pull_request_files_pr_file_id_seq";
CREATE SEQUENCE "augur_data"."pull_request_files_pr_file_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25150
CACHE 1;
ALTER SEQUENCE "augur_data"."pull_request_files_pr_file_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for pull_request_labels_pr_label_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."pull_request_labels_pr_label_id_seq";
CREATE SEQUENCE "augur_data"."pull_request_labels_pr_label_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25430
CACHE 1;
ALTER SEQUENCE "augur_data"."pull_request_labels_pr_label_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for pull_request_message_ref_pr_msg_ref_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."pull_request_message_ref_pr_msg_ref_id_seq";
CREATE SEQUENCE "augur_data"."pull_request_message_ref_pr_msg_ref_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25430
CACHE 1;
ALTER SEQUENCE "augur_data"."pull_request_message_ref_pr_msg_ref_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for pull_request_meta_pr_repo_meta_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."pull_request_meta_pr_repo_meta_id_seq";
CREATE SEQUENCE "augur_data"."pull_request_meta_pr_repo_meta_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25430
CACHE 1;
ALTER SEQUENCE "augur_data"."pull_request_meta_pr_repo_meta_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for pull_request_repo_pr_repo_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."pull_request_repo_pr_repo_id_seq";
CREATE SEQUENCE "augur_data"."pull_request_repo_pr_repo_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25430
CACHE 1;
ALTER SEQUENCE "augur_data"."pull_request_repo_pr_repo_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for pull_request_reviewers_pr_reviewer_map_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."pull_request_reviewers_pr_reviewer_map_id_seq";
CREATE SEQUENCE "augur_data"."pull_request_reviewers_pr_reviewer_map_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25430
CACHE 1;
ALTER SEQUENCE "augur_data"."pull_request_reviewers_pr_reviewer_map_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for pull_request_teams_pr_team_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."pull_request_teams_pr_team_id_seq";
CREATE SEQUENCE "augur_data"."pull_request_teams_pr_team_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25430
CACHE 1;
ALTER SEQUENCE "augur_data"."pull_request_teams_pr_team_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for pull_requests_pull_request_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."pull_requests_pull_request_id_seq";
CREATE SEQUENCE "augur_data"."pull_requests_pull_request_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25430
CACHE 1;
ALTER SEQUENCE "augur_data"."pull_requests_pull_request_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for releases_release_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."releases_release_id_seq";
CREATE SEQUENCE "augur_data"."releases_release_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "augur_data"."releases_release_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for repo_badging_badge_collection_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."repo_badging_badge_collection_id_seq";
CREATE SEQUENCE "augur_data"."repo_badging_badge_collection_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25012
CACHE 1;
ALTER SEQUENCE "augur_data"."repo_badging_badge_collection_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for repo_cluster_messages_msg_cluster_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."repo_cluster_messages_msg_cluster_id_seq";
CREATE SEQUENCE "augur_data"."repo_cluster_messages_msg_cluster_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "augur_data"."repo_cluster_messages_msg_cluster_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for repo_group_insights_rgi_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."repo_group_insights_rgi_id_seq";
CREATE SEQUENCE "augur_data"."repo_group_insights_rgi_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25430
CACHE 1;
ALTER SEQUENCE "augur_data"."repo_group_insights_rgi_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for repo_groups_list_serve_rgls_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."repo_groups_list_serve_rgls_id_seq";
CREATE SEQUENCE "augur_data"."repo_groups_list_serve_rgls_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25430
CACHE 1;
ALTER SEQUENCE "augur_data"."repo_groups_list_serve_rgls_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for repo_groups_repo_group_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."repo_groups_repo_group_id_seq";
CREATE SEQUENCE "augur_data"."repo_groups_repo_group_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25430
CACHE 1;
ALTER SEQUENCE "augur_data"."repo_groups_repo_group_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for repo_info_repo_info_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."repo_info_repo_info_id_seq";
CREATE SEQUENCE "augur_data"."repo_info_repo_info_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25430
CACHE 1;
ALTER SEQUENCE "augur_data"."repo_info_repo_info_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for repo_insights_records_ri_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."repo_insights_records_ri_id_seq";
CREATE SEQUENCE "augur_data"."repo_insights_records_ri_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "augur_data"."repo_insights_records_ri_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for repo_insights_ri_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."repo_insights_ri_id_seq";
CREATE SEQUENCE "augur_data"."repo_insights_ri_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "augur_data"."repo_insights_ri_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for repo_labor_repo_labor_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."repo_labor_repo_labor_id_seq";
CREATE SEQUENCE "augur_data"."repo_labor_repo_labor_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25430
CACHE 1;
ALTER SEQUENCE "augur_data"."repo_labor_repo_labor_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for repo_meta_rmeta_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."repo_meta_rmeta_id_seq";
CREATE SEQUENCE "augur_data"."repo_meta_rmeta_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25430
CACHE 1;
ALTER SEQUENCE "augur_data"."repo_meta_rmeta_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for repo_repo_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."repo_repo_id_seq";
CREATE SEQUENCE "augur_data"."repo_repo_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25430
CACHE 1;
ALTER SEQUENCE "augur_data"."repo_repo_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for repo_sbom_scans_rsb_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."repo_sbom_scans_rsb_id_seq";
CREATE SEQUENCE "augur_data"."repo_sbom_scans_rsb_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25430
CACHE 1;
ALTER SEQUENCE "augur_data"."repo_sbom_scans_rsb_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for repo_stats_rstat_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."repo_stats_rstat_id_seq";
CREATE SEQUENCE "augur_data"."repo_stats_rstat_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25430
CACHE 1;
ALTER SEQUENCE "augur_data"."repo_stats_rstat_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for repo_test_coverage_repo_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."repo_test_coverage_repo_id_seq";
CREATE SEQUENCE "augur_data"."repo_test_coverage_repo_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "augur_data"."repo_test_coverage_repo_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for repo_topic_repo_topic_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."repo_topic_repo_topic_id_seq";
CREATE SEQUENCE "augur_data"."repo_topic_repo_topic_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "augur_data"."repo_topic_repo_topic_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for topic_words_topic_words_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."topic_words_topic_words_id_seq";
CREATE SEQUENCE "augur_data"."topic_words_topic_words_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "augur_data"."topic_words_topic_words_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for utility_log_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."utility_log_id_seq";
CREATE SEQUENCE "augur_data"."utility_log_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "augur_data"."utility_log_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for utility_log_id_seq1
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_data"."utility_log_id_seq1";
CREATE SEQUENCE "augur_data"."utility_log_id_seq1" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "augur_data"."utility_log_id_seq1" OWNER TO "augur";

-- ----------------------------

ALTER TABLE IF EXISTS "augur_data"."commit_comment_ref" DROP CONSTRAINT "fk_commit_comment_ref_commits_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."commit_comment_ref" DROP CONSTRAINT "fk_commit_comment_ref_message_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."commit_parents" DROP CONSTRAINT "fk_commit_parents_commits_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."commit_parents" DROP CONSTRAINT "fk_commit_parents_commits_2" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."commits" DROP CONSTRAINT "fk_commits_contributors_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."commits" DROP CONSTRAINT "fk_commits_contributors_2" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."commits" DROP CONSTRAINT "fk_commits_repo_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."contributors_aliases" DROP CONSTRAINT "fk_contributors_aliases_contributors_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."contributors_history" DROP CONSTRAINT "fk_contributors_history_contributors_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."discourse_insights" DROP CONSTRAINT "fk_discourse_insights_message_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."issue_assignees" DROP CONSTRAINT "fk_issue_assignees_contributors_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."issue_assignees" DROP CONSTRAINT "fk_issue_assignees_issues_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."issue_events" DROP CONSTRAINT "fk_issue_events_contributors_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."issue_events" DROP CONSTRAINT "fk_issue_events_issues_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."issue_labels" DROP CONSTRAINT "fk_issue_labels_issues_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."issue_message_ref" DROP CONSTRAINT "fk_issue_message_ref_issues_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."issue_message_ref" DROP CONSTRAINT "fk_issue_message_ref_message_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."issues" DROP CONSTRAINT "fk_issues_contributors_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."issues" DROP CONSTRAINT "fk_issues_contributors_2" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."issues" DROP CONSTRAINT "fk_issues_repo" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."libraries" DROP CONSTRAINT "fk_libraries_repo_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."library_dependencies" DROP CONSTRAINT "fk_library_dependencies_libraries_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."library_version" DROP CONSTRAINT "fk_library_version_libraries_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."lstm_anomaly_results" DROP CONSTRAINT "fk_lstm_anomaly_results_lstm_anomaly_models_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."lstm_anomaly_results" DROP CONSTRAINT "fk_lstm_anomaly_results_repo_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."message" DROP CONSTRAINT "fk_message_contributors_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."message" DROP CONSTRAINT "fk_message_platform_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."message" DROP CONSTRAINT "fk_message_repo_groups_list_serve_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."message_analysis" DROP CONSTRAINT "fk_message_analysis_message_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."message_analysis_summary" DROP CONSTRAINT "fk_message_analysis_summary_repo_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."message_sentiment" DROP CONSTRAINT "fk_message_sentiment_message_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."message_sentiment_summary" DROP CONSTRAINT "fk_message_sentiment_summary_repo_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."pull_request_assignees" DROP CONSTRAINT "fk_pull_request_assignees_contributors_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."pull_request_assignees" DROP CONSTRAINT "fk_pull_request_assignees_pull_requests_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."pull_request_commits" DROP CONSTRAINT "fk_pull_request_commits_pull_requests_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."pull_request_events" DROP CONSTRAINT "fk_pull_request_events_contributors_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."pull_request_events" DROP CONSTRAINT "fk_pull_request_events_pull_requests_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."pull_request_files" DROP CONSTRAINT "fk_pull_request_commits_pull_requests_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."pull_request_labels" DROP CONSTRAINT "fk_pull_request_labels_pull_requests_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."pull_request_message_ref" DROP CONSTRAINT "fk_pull_request_message_ref_message_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."pull_request_message_ref" DROP CONSTRAINT "fk_pull_request_message_ref_pull_requests_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."pull_request_meta" DROP CONSTRAINT "fk_pull_request_meta_contributors_2" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."pull_request_meta" DROP CONSTRAINT "fk_pull_request_meta_pull_requests_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."pull_request_repo" DROP CONSTRAINT "fk_pull_request_repo_contributors_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."pull_request_repo" DROP CONSTRAINT "fk_pull_request_repo_pull_request_meta_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."pull_request_reviewers" DROP CONSTRAINT "fk_pull_request_reviewers_contributors_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."pull_request_reviewers" DROP CONSTRAINT "fk_pull_request_reviewers_pull_requests_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."pull_request_teams" DROP CONSTRAINT "fk_pull_request_teams_pull_requests_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."pull_requests" DROP CONSTRAINT "fk_pull_requests_pull_request_meta_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."pull_requests" DROP CONSTRAINT "fk_pull_requests_pull_request_meta_2" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."pull_requests" DROP CONSTRAINT "fk_pull_requests_repo_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."releases" DROP CONSTRAINT "fk_releases_repo_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."repo" DROP CONSTRAINT "fk_repo_repo_groups_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."repo_badging" DROP CONSTRAINT "fk_repo_badging_repo_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."repo_cluster_messages" DROP CONSTRAINT "fk_repo_cluster_messages_repo_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."repo_group_insights" DROP CONSTRAINT "fk_repo_group_insights_repo_groups_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."repo_groups_list_serve" DROP CONSTRAINT "fk_repo_groups_list_serve_repo_groups_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."repo_info" DROP CONSTRAINT "fk_repo_info_repo_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."repo_insights" DROP CONSTRAINT "fk_repo_insights_repo_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."repo_insights_records" DROP CONSTRAINT "repo_id_ref" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."repo_labor" DROP CONSTRAINT "fk_repo_labor_repo_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."repo_meta" DROP CONSTRAINT "fk_repo_meta_repo_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."repo_sbom_scans" DROP CONSTRAINT "repo_linker_sbom" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."repo_stats" DROP CONSTRAINT "fk_repo_stats_repo_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."repo_test_coverage" DROP CONSTRAINT "fk_repo_test_coverage_repo_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."repo_topic" DROP CONSTRAINT "fk_repo_topic_repo_1" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."topic_words" DROP CONSTRAINT "fk_topic_words_repo_topic_1" CASCADE;
ALTER TABLE IF EXISTS "spdx"."annotations" DROP CONSTRAINT "annotations_annotation_type_id_fkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."annotations" DROP CONSTRAINT "annotations_creator_id_fkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."annotations" DROP CONSTRAINT "annotations_document_id_fkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."annotations" DROP CONSTRAINT "annotations_identifier_id_fkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."creators" DROP CONSTRAINT "creators_creator_type_id_fkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."documents" DROP CONSTRAINT "documents_data_license_id_fkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."documents" DROP CONSTRAINT "documents_document_namespace_id_fkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."documents" DROP CONSTRAINT "documents_package_id_fkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."documents_creators" DROP CONSTRAINT "documents_creators_creator_id_fkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."documents_creators" DROP CONSTRAINT "documents_creators_document_id_fkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."external_refs" DROP CONSTRAINT "external_refs_document_id_fkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."external_refs" DROP CONSTRAINT "external_refs_document_namespace_id_fkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."file_contributors" DROP CONSTRAINT "file_contributors_file_id_fkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."files_licenses" DROP CONSTRAINT "files_licenses_file_id_fkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."files_licenses" DROP CONSTRAINT "files_licenses_license_id_fkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."files_scans" DROP CONSTRAINT "files_scans_file_id_fkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."files_scans" DROP CONSTRAINT "files_scans_scanner_id_fkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."identifiers" DROP CONSTRAINT "identifiers_document_id_fkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."identifiers" DROP CONSTRAINT "identifiers_document_namespace_id_fkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."identifiers" DROP CONSTRAINT "identifiers_package_file_id_fkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."identifiers" DROP CONSTRAINT "identifiers_package_id_fkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."packages" DROP CONSTRAINT "fk_package_packages_files" CASCADE;
ALTER TABLE IF EXISTS "spdx"."packages" DROP CONSTRAINT "packages_concluded_license_id_fkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."packages" DROP CONSTRAINT "packages_declared_license_id_fkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."packages" DROP CONSTRAINT "packages_originator_id_fkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."packages" DROP CONSTRAINT "packages_supplier_id_fkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."packages_files" DROP CONSTRAINT "fk_package_files_packages" CASCADE;
ALTER TABLE IF EXISTS "spdx"."packages_files" DROP CONSTRAINT "packages_files_concluded_license_id_fkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."packages_files" DROP CONSTRAINT "packages_files_file_id_fkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."packages_scans" DROP CONSTRAINT "packages_scans_package_id_fkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."packages_scans" DROP CONSTRAINT "packages_scans_scanner_id_fkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."relationships" DROP CONSTRAINT "relationships_left_identifier_id_fkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."relationships" DROP CONSTRAINT "relationships_relationship_type_id_fkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."relationships" DROP CONSTRAINT "relationships_right_identifier_id_fkey" CASCADE;

DROP INDEX IF EXISTS "augur_data"."repos_id" CASCADE;
DROP INDEX IF EXISTS "augur_data"."comment_id" CASCADE;
DROP INDEX IF EXISTS "augur_data"."commit_parents_ibfk_1" CASCADE;
DROP INDEX IF EXISTS "augur_data"."commit_parents_ibfk_2" CASCADE;
DROP INDEX IF EXISTS "augur_data"."author_affiliation" CASCADE;
DROP INDEX IF EXISTS "augur_data"."author_cntrb_id" CASCADE;
DROP INDEX IF EXISTS "augur_data"."author_email,author_affiliation,author_date" CASCADE;
DROP INDEX IF EXISTS "augur_data"."author_raw_email" CASCADE;
DROP INDEX IF EXISTS "augur_data"."cmt-author-date-idx2" CASCADE;
DROP INDEX IF EXISTS "augur_data"."cmt-committer-date-idx3" CASCADE;
DROP INDEX IF EXISTS "augur_data"."cmt_author-name-idx5" CASCADE;
DROP INDEX IF EXISTS "augur_data"."cmt_author_contrib_worker" CASCADE;
DROP INDEX IF EXISTS "augur_data"."cmt_cmmter-name-idx4" CASCADE;
DROP INDEX IF EXISTS "augur_data"."cmt_commiter_contrib_worker" CASCADE;
DROP INDEX IF EXISTS "augur_data"."commited" CASCADE;
DROP INDEX IF EXISTS "augur_data"."commits_idx_cmt_email_cmt_date_cmt_name" CASCADE;
DROP INDEX IF EXISTS "augur_data"."commits_idx_cmt_email_cmt_date_cmt_name2" CASCADE;
DROP INDEX IF EXISTS "augur_data"."commits_idx_cmt_name_cmt_date2" CASCADE;
DROP INDEX IF EXISTS "augur_data"."commits_idx_cmt_name_cmt_date_cmt_date3" CASCADE;
DROP INDEX IF EXISTS "augur_data"."commits_idx_repo_id_cmt_ema_cmt_dat_cmt_nam" CASCADE;
DROP INDEX IF EXISTS "augur_data"."commits_idx_repo_id_cmt_ema_cmt_dat_cmt_nam2" CASCADE;
DROP INDEX IF EXISTS "augur_data"."commits_idx_repo_id_cmt_ema_cmt_nam_cmt_dat2" CASCADE;
DROP INDEX IF EXISTS "augur_data"."commits_idx_repo_id_cmt_ema_cmt_nam_cmt_dat3" CASCADE;
DROP INDEX IF EXISTS "augur_data"."committer_affiliation" CASCADE;
DROP INDEX IF EXISTS "augur_data"."committer_cntrb_id" CASCADE;
DROP INDEX IF EXISTS "augur_data"."committer_email,committer_affiliation,committer_date" CASCADE;
DROP INDEX IF EXISTS "augur_data"."committer_raw_email" CASCADE;
DROP INDEX IF EXISTS "augur_data"."repo_id,commit" CASCADE;
DROP INDEX IF EXISTS "augur_data"."cnt-fullname" CASCADE;
DROP INDEX IF EXISTS "augur_data"."cntrb-theemail" CASCADE;
DROP INDEX IF EXISTS "augur_data"."cntrb_login_platform_index" CASCADE;
DROP INDEX IF EXISTS "augur_data"."contributor_delete_finder" CASCADE;
DROP INDEX IF EXISTS "augur_data"."contributor_worker_email_finder" CASCADE;
DROP INDEX IF EXISTS "augur_data"."contributor_worker_finder" CASCADE;
DROP INDEX IF EXISTS "augur_data"."contributor_worker_fullname_finder" CASCADE;
DROP INDEX IF EXISTS "augur_data"."contributors_idx_cntrb_email3" CASCADE;
DROP INDEX IF EXISTS "augur_data"."login" CASCADE;
DROP INDEX IF EXISTS "augur_data"."login-contributor-idx" CASCADE;
DROP INDEX IF EXISTS "augur_data"."alias,active" CASCADE;
DROP INDEX IF EXISTS "augur_data"."canonical,alias" CASCADE;
DROP INDEX IF EXISTS "augur_data"."issue-alias-cntrb-idx1" CASCADE;
DROP INDEX IF EXISTS "augur_data"."issue-alias-cntrb-idx2" CASCADE;
DROP INDEX IF EXISTS "augur_data"."contrb-history-dix1" CASCADE;
DROP INDEX IF EXISTS "augur_data"."login_index_2" CASCADE;
DROP INDEX IF EXISTS "augur_data"."repo_id,affiliation_copy_1" CASCADE;
DROP INDEX IF EXISTS "augur_data"."repo_id,email_copy_1" CASCADE;
DROP INDEX IF EXISTS "augur_data"."projects_id,affiliation_copy_1" CASCADE;
DROP INDEX IF EXISTS "augur_data"."projects_id,email_copy_1" CASCADE;
DROP INDEX IF EXISTS "augur_data"."projects_id,affiliation_copy_2" CASCADE;
DROP INDEX IF EXISTS "augur_data"."projects_id,email_copy_2" CASCADE;
DROP INDEX IF EXISTS "augur_data"."projects_id,year,affiliation_copy_1" CASCADE;
DROP INDEX IF EXISTS "augur_data"."projects_id,year,email_copy_1" CASCADE;
DROP INDEX IF EXISTS "augur_data"."projects_id,affiliation" CASCADE;
DROP INDEX IF EXISTS "augur_data"."projects_id,email" CASCADE;
DROP INDEX IF EXISTS "augur_data"."projects_id,year,affiliation" CASCADE;
DROP INDEX IF EXISTS "augur_data"."projects_id,year,email" CASCADE;
DROP INDEX IF EXISTS "augur_data"."repo_id,affiliation_copy_2" CASCADE;
DROP INDEX IF EXISTS "augur_data"."repo_id,email_copy_2" CASCADE;
DROP INDEX IF EXISTS "augur_data"."repo_id,year,affiliation_copy_1" CASCADE;
DROP INDEX IF EXISTS "augur_data"."repo_id,year,email_copy_1" CASCADE;
DROP INDEX IF EXISTS "augur_data"."repo_id,affiliation" CASCADE;
DROP INDEX IF EXISTS "augur_data"."repo_id,email" CASCADE;
DROP INDEX IF EXISTS "augur_data"."repo_id,year,affiliation" CASCADE;
DROP INDEX IF EXISTS "augur_data"."repo_id,year,email" CASCADE;
DROP INDEX IF EXISTS "augur_data"."issue-cntrb-assign-idx-1" CASCADE;
DROP INDEX IF EXISTS "augur_data"."issue-cntrb-idx2" CASCADE;
DROP INDEX IF EXISTS "augur_data"."issue_events_ibfk_1" CASCADE;
DROP INDEX IF EXISTS "augur_data"."issue_events_ibfk_2" CASCADE;
DROP INDEX IF EXISTS "augur_data"."issue-cntrb-dix2" CASCADE;
DROP INDEX IF EXISTS "augur_data"."issues_ibfk_1" CASCADE;
DROP INDEX IF EXISTS "augur_data"."issues_ibfk_2" CASCADE;
DROP INDEX IF EXISTS "augur_data"."issues_ibfk_4" CASCADE;
DROP INDEX IF EXISTS "augur_data"."REPO_DEP" CASCADE;
DROP INDEX IF EXISTS "augur_data"."messagegrouper" CASCADE;
DROP INDEX IF EXISTS "augur_data"."msg-cntrb-id-idx" CASCADE;
DROP INDEX IF EXISTS "augur_data"."platformgrouper" CASCADE;
DROP INDEX IF EXISTS "augur_data"."plat" CASCADE;
DROP INDEX IF EXISTS "augur_data"."pr_meta_cntrb-idx" CASCADE;
DROP INDEX IF EXISTS "augur_data"."pr_events_ibfk_1" CASCADE;
DROP INDEX IF EXISTS "augur_data"."pr_events_ibfk_2" CASCADE;
DROP INDEX IF EXISTS "augur_data"."pr_meta-cntrbid-idx" CASCADE;
DROP INDEX IF EXISTS "augur_data"."pr-cntrb-idx-repo" CASCADE;
DROP INDEX IF EXISTS "augur_data"."pr-reviewers-cntrb-idx1" CASCADE;
DROP INDEX IF EXISTS "augur_data"."id_node" CASCADE;
DROP INDEX IF EXISTS "augur_data"."forked" CASCADE;
DROP INDEX IF EXISTS "augur_data"."repogitindexrep" CASCADE;
DROP INDEX IF EXISTS "augur_data"."reponameindex" CASCADE;
DROP INDEX IF EXISTS "augur_data"."reponameindexbtree" CASCADE;
DROP INDEX IF EXISTS "augur_data"."rggrouponrepoindex" CASCADE;
DROP INDEX IF EXISTS "augur_data"."therepo" CASCADE;
DROP INDEX IF EXISTS "augur_data"."rgidm" CASCADE;
DROP INDEX IF EXISTS "augur_data"."rgnameindex" CASCADE;
DROP INDEX IF EXISTS "augur_data"."lister" CASCADE;
DROP INDEX IF EXISTS "augur_data"."dater" CASCADE;
DROP INDEX IF EXISTS "augur_data"."repos_id,status" CASCADE;
DROP INDEX IF EXISTS "augur_data"."repos_id,statusops" CASCADE;
DROP INDEX IF EXISTS "augur_data"."type,projects_id" CASCADE;
DROP INDEX IF EXISTS "augur_operations"."repos_id,statusops" CASCADE;

ALTER TABLE IF EXISTS "augur_data"."commit_comment_ref" DROP CONSTRAINT "commitcomment" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."contributor_affiliations" DROP CONSTRAINT "unique_domain" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."message" DROP CONSTRAINT "REPOGROUPLISTER" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."message" DROP CONSTRAINT "platformer" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."repo_groups_list_serve" DROP CONSTRAINT "rglistserve" CASCADE;
ALTER TABLE IF EXISTS "spdx"."annotation_types" DROP CONSTRAINT "uc_annotation_type_name" CASCADE;
ALTER TABLE IF EXISTS "spdx"."document_namespaces" DROP CONSTRAINT "uc_document_namespace_uri" CASCADE;
ALTER TABLE IF EXISTS "spdx"."documents" DROP CONSTRAINT "uc_document_document_namespace_id" CASCADE;
ALTER TABLE IF EXISTS "spdx"."external_refs" DROP CONSTRAINT "uc_external_ref_document_id_string" CASCADE;
ALTER TABLE IF EXISTS "spdx"."files" DROP CONSTRAINT "uc_file_sha256" CASCADE;
ALTER TABLE IF EXISTS "spdx"."files_licenses" DROP CONSTRAINT "uc_file_license" CASCADE;
ALTER TABLE IF EXISTS "spdx"."files_scans" DROP CONSTRAINT "uc_file_scanner_id" CASCADE;
ALTER TABLE IF EXISTS "spdx"."identifiers" DROP CONSTRAINT "uc_identifier_document_namespace_id" CASCADE;
ALTER TABLE IF EXISTS "spdx"."identifiers" DROP CONSTRAINT "uc_identifier_namespace_document_id" CASCADE;
ALTER TABLE IF EXISTS "spdx"."identifiers" DROP CONSTRAINT "uc_identifier_namespace_package_id" CASCADE;
ALTER TABLE IF EXISTS "spdx"."identifiers" DROP CONSTRAINT "uc_identifier_namespace_package_file_id" CASCADE;
ALTER TABLE IF EXISTS "spdx"."licenses" DROP CONSTRAINT "uc_license_short_name" CASCADE;
ALTER TABLE IF EXISTS "spdx"."packages" DROP CONSTRAINT "uc_package_sha256" CASCADE;
ALTER TABLE IF EXISTS "spdx"."packages" DROP CONSTRAINT "uc_dir_code_ver_code" CASCADE;
ALTER TABLE IF EXISTS "spdx"."packages_files" DROP CONSTRAINT "uc_package_id_file_name" CASCADE;
ALTER TABLE IF EXISTS "spdx"."packages_scans" DROP CONSTRAINT "uc_package_scanner_id" CASCADE;
ALTER TABLE IF EXISTS "spdx"."relationship_types" DROP CONSTRAINT "uc_relationship_type_name" CASCADE;
ALTER TABLE IF EXISTS "spdx"."relationships" DROP CONSTRAINT "uc_left_right_relationship_type" CASCADE;
ALTER TABLE IF EXISTS "spdx"."scanners" DROP CONSTRAINT "uc_scanner_name" CASCADE;

ALTER TABLE IF EXISTS "spdx"."identifiers" DROP CONSTRAINT "ck_identifier_exactly_one" CASCADE;
ALTER TABLE IF EXISTS "spdx"."packages" DROP CONSTRAINT "uc_sha256_ds2_dir_code_exactly_one" CASCADE;

ALTER TABLE IF EXISTS "augur_data"."chaoss_metric_status" DROP CONSTRAINT "chaoss_metric_status_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."commit_comment_ref" DROP CONSTRAINT "commit_comment_ref_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."commit_parents" DROP CONSTRAINT "commit_parents_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."commits" DROP CONSTRAINT "commits_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."contributor_affiliations" DROP CONSTRAINT "contributor_affiliations_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."contributors" DROP CONSTRAINT "contributors_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."contributors_aliases" DROP CONSTRAINT "contributors_aliases_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."contributors_history" DROP CONSTRAINT "contributors_history_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."exclude" DROP CONSTRAINT "exclude_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."issue_assignees" DROP CONSTRAINT "issue_assignees_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."issue_events" DROP CONSTRAINT "issue_events_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."issue_labels" DROP CONSTRAINT "issue_labels_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."issue_message_ref" DROP CONSTRAINT "issue_message_ref_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."issues" DROP CONSTRAINT "issues_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."libraries" DROP CONSTRAINT "libraries_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."library_dependencies" DROP CONSTRAINT "library_dependencies_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."library_version" DROP CONSTRAINT "library_version_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."lstm_anomaly_models" DROP CONSTRAINT "lstm_anomaly_models_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."lstm_anomaly_results" DROP CONSTRAINT "lstm_anomaly_results_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."message" DROP CONSTRAINT "message_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."message_analysis" DROP CONSTRAINT "message_analysis_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."message_analysis_summary" DROP CONSTRAINT "message_analysis_summary_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."message_sentiment" DROP CONSTRAINT "message_sentiment_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."message_sentiment_summary" DROP CONSTRAINT "message_sentiment_summary_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."platform" DROP CONSTRAINT "theplat" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."pull_request_assignees" DROP CONSTRAINT "pull_request_assignees_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."pull_request_commits" DROP CONSTRAINT "pull_request_commits_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."pull_request_events" DROP CONSTRAINT "pr_events_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."pull_request_files" DROP CONSTRAINT "pull_request_files_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."pull_request_labels" DROP CONSTRAINT "pull_request_labels_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."pull_request_message_ref" DROP CONSTRAINT "pull_request_message_ref_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."pull_request_meta" DROP CONSTRAINT "pull_request_meta_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."pull_request_repo" DROP CONSTRAINT "pull_request_repo_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."pull_request_reviewers" DROP CONSTRAINT "pull_request_reviewers_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."pull_request_teams" DROP CONSTRAINT "pull_request_teams_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."pull_requests" DROP CONSTRAINT "pull_requests_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."releases" DROP CONSTRAINT "releases_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."repo" DROP CONSTRAINT "repounique" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."repo_badging" DROP CONSTRAINT "repo_badging_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."repo_cluster_messages" DROP CONSTRAINT "repo_cluster_messages_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."repo_group_insights" DROP CONSTRAINT "repo_group_insights_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."repo_groups" DROP CONSTRAINT "rgid" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."repo_groups_list_serve" DROP CONSTRAINT "repo_groups_list_serve_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."repo_info" DROP CONSTRAINT "repo_info_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."repo_insights" DROP CONSTRAINT "repo_insights_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."repo_insights_records" DROP CONSTRAINT "repo_insights_records_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."repo_labor" DROP CONSTRAINT "repo_labor_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."repo_meta" DROP CONSTRAINT "repo_meta_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."repo_sbom_scans" DROP CONSTRAINT "repo_sbom_scans_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."repo_stats" DROP CONSTRAINT "repo_stats_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."repo_test_coverage" DROP CONSTRAINT "repo_test_coverage_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."repo_topic" DROP CONSTRAINT "repo_topic_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."settings" DROP CONSTRAINT "settings_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."topic_words" DROP CONSTRAINT "topic_words_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_data"."utility_log" DROP CONSTRAINT "utility_log_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_operations"."augur_settings" DROP CONSTRAINT "augur_settings_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_operations"."worker_history" DROP CONSTRAINT "history_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_operations"."worker_job" DROP CONSTRAINT "job_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_operations"."worker_oauth" DROP CONSTRAINT "worker_oauth_pkey" CASCADE;
ALTER TABLE IF EXISTS "augur_operations"."worker_settings_facade" DROP CONSTRAINT "settings_pkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."annotation_types" DROP CONSTRAINT "annotation_types_pkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."annotations" DROP CONSTRAINT "annotations_pkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."augur_repo_map" DROP CONSTRAINT "augur_repo_map_pkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."creator_types" DROP CONSTRAINT "creator_types_pkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."creators" DROP CONSTRAINT "creators_pkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."document_namespaces" DROP CONSTRAINT "document_namespaces_pkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."documents" DROP CONSTRAINT "documents_pkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."documents_creators" DROP CONSTRAINT "documents_creators_pkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."external_refs" DROP CONSTRAINT "external_refs_pkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."file_contributors" DROP CONSTRAINT "file_contributors_pkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."file_types" DROP CONSTRAINT "uc_file_type_name" CASCADE;
ALTER TABLE IF EXISTS "spdx"."files" DROP CONSTRAINT "files_pkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."files_licenses" DROP CONSTRAINT "files_licenses_pkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."files_scans" DROP CONSTRAINT "files_scans_pkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."identifiers" DROP CONSTRAINT "identifiers_pkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."licenses" DROP CONSTRAINT "licenses_pkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."packages" DROP CONSTRAINT "packages_pkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."packages_files" DROP CONSTRAINT "packages_files_pkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."packages_scans" DROP CONSTRAINT "packages_scans_pkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."projects" DROP CONSTRAINT "projects_pkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."relationship_types" DROP CONSTRAINT "relationship_types_pkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."relationships" DROP CONSTRAINT "relationships_pkey" CASCADE;
ALTER TABLE IF EXISTS "spdx"."scanners" DROP CONSTRAINT "scanners_pkey" CASCADE;

DROP TABLE IF EXISTS "augur_data"."analysis_log" CASCADE;
DROP TABLE IF EXISTS "augur_data"."chaoss_metric_status" CASCADE;
DROP TABLE IF EXISTS "augur_data"."commit_comment_ref" CASCADE;
DROP TABLE IF EXISTS "augur_data"."commit_parents" CASCADE;
DROP TABLE IF EXISTS "augur_data"."commits" CASCADE;
DROP TABLE IF EXISTS "augur_data"."contributor_affiliations" CASCADE;
DROP TABLE IF EXISTS "augur_data"."contributors" CASCADE;
DROP TABLE IF EXISTS "augur_data"."contributors_aliases" CASCADE;
DROP TABLE IF EXISTS "augur_data"."contributors_history" CASCADE;
DROP TABLE IF EXISTS "augur_data"."discourse_insights" CASCADE;
DROP TABLE IF EXISTS "augur_data"."dm_repo_annual" CASCADE;
DROP TABLE IF EXISTS "augur_data"."dm_repo_group_annual" CASCADE;
DROP TABLE IF EXISTS "augur_data"."dm_repo_group_monthly" CASCADE;
DROP TABLE IF EXISTS "augur_data"."dm_repo_group_weekly" CASCADE;
DROP TABLE IF EXISTS "augur_data"."dm_repo_monthly" CASCADE;
DROP TABLE IF EXISTS "augur_data"."dm_repo_weekly" CASCADE;
DROP TABLE IF EXISTS "augur_data"."exclude" CASCADE;
DROP TABLE IF EXISTS "augur_data"."issue_assignees" CASCADE;
DROP TABLE IF EXISTS "augur_data"."issue_events" CASCADE;
DROP TABLE IF EXISTS "augur_data"."issue_labels" CASCADE;
DROP TABLE IF EXISTS "augur_data"."issue_message_ref" CASCADE;
DROP TABLE IF EXISTS "augur_data"."issues" CASCADE;
DROP TABLE IF EXISTS "augur_data"."libraries" CASCADE;
DROP TABLE IF EXISTS "augur_data"."library_dependencies" CASCADE;
DROP TABLE IF EXISTS "augur_data"."library_version" CASCADE;
DROP TABLE IF EXISTS "augur_data"."lstm_anomaly_models" CASCADE;
DROP TABLE IF EXISTS "augur_data"."lstm_anomaly_results" CASCADE;
DROP TABLE IF EXISTS "augur_data"."message" CASCADE;
DROP TABLE IF EXISTS "augur_data"."message_analysis" CASCADE;
DROP TABLE IF EXISTS "augur_data"."message_analysis_summary" CASCADE;
DROP TABLE IF EXISTS "augur_data"."message_sentiment" CASCADE;
DROP TABLE IF EXISTS "augur_data"."message_sentiment_summary" CASCADE;
DROP TABLE IF EXISTS "augur_data"."platform" CASCADE;
DROP TABLE IF EXISTS "augur_data"."pull_request_assignees" CASCADE;
DROP TABLE IF EXISTS "augur_data"."pull_request_commits" CASCADE;
DROP TABLE IF EXISTS "augur_data"."pull_request_events" CASCADE;
DROP TABLE IF EXISTS "augur_data"."pull_request_files" CASCADE;
DROP TABLE IF EXISTS "augur_data"."pull_request_labels" CASCADE;
DROP TABLE IF EXISTS "augur_data"."pull_request_message_ref" CASCADE;
DROP TABLE IF EXISTS "augur_data"."pull_request_meta" CASCADE;
DROP TABLE IF EXISTS "augur_data"."pull_request_repo" CASCADE;
DROP TABLE IF EXISTS "augur_data"."pull_request_reviewers" CASCADE;
DROP TABLE IF EXISTS "augur_data"."pull_request_teams" CASCADE;
DROP TABLE IF EXISTS "augur_data"."pull_requests" CASCADE;
DROP TABLE IF EXISTS "augur_data"."releases" CASCADE;
DROP TABLE IF EXISTS "augur_data"."repo" CASCADE;
DROP TABLE IF EXISTS "augur_data"."repo_badging" CASCADE;
DROP TABLE IF EXISTS "augur_data"."repo_cluster_messages" CASCADE;
DROP TABLE IF EXISTS "augur_data"."repo_group_insights" CASCADE;
DROP TABLE IF EXISTS "augur_data"."repo_groups" CASCADE;
DROP TABLE IF EXISTS "augur_data"."repo_groups_list_serve" CASCADE;
DROP TABLE IF EXISTS "augur_data"."repo_info" CASCADE;
DROP TABLE IF EXISTS "augur_data"."repo_insights" CASCADE;
DROP TABLE IF EXISTS "augur_data"."repo_insights_records" CASCADE;
DROP TABLE IF EXISTS "augur_data"."repo_labor" CASCADE;
DROP TABLE IF EXISTS "augur_data"."repo_meta" CASCADE;
DROP TABLE IF EXISTS "augur_data"."repo_sbom_scans" CASCADE;
DROP TABLE IF EXISTS "augur_data"."repo_stats" CASCADE;
DROP TABLE IF EXISTS "augur_data"."repo_test_coverage" CASCADE;
DROP TABLE IF EXISTS "augur_data"."repo_topic" CASCADE;
DROP TABLE IF EXISTS "augur_data"."repos_fetch_log" CASCADE;
DROP TABLE IF EXISTS "augur_data"."settings" CASCADE;
DROP TABLE IF EXISTS "augur_data"."topic_words" CASCADE;
DROP TABLE IF EXISTS "augur_data"."unknown_cache" CASCADE;
DROP TABLE IF EXISTS "augur_data"."utility_log" CASCADE;
DROP TABLE IF EXISTS "augur_data"."working_commits" CASCADE;
DROP TABLE IF EXISTS "augur_operations"."all" CASCADE;
DROP TABLE IF EXISTS "augur_operations"."augur_settings" CASCADE;
DROP TABLE IF EXISTS "augur_operations"."repos_fetch_log" CASCADE;
DROP TABLE IF EXISTS "augur_operations"."worker_history" CASCADE;
DROP TABLE IF EXISTS "augur_operations"."worker_job" CASCADE;
DROP TABLE IF EXISTS "augur_operations"."worker_oauth" CASCADE;
DROP TABLE IF EXISTS "augur_operations"."worker_settings_facade" CASCADE;
DROP TABLE IF EXISTS "augur_operations"."working_commits" CASCADE;
DROP TABLE IF EXISTS "spdx"."annotation_types" CASCADE;
DROP TABLE IF EXISTS "spdx"."annotations" CASCADE;
DROP TABLE IF EXISTS "spdx"."augur_repo_map" CASCADE;
DROP TABLE IF EXISTS "spdx"."creator_types" CASCADE;
DROP TABLE IF EXISTS "spdx"."creators" CASCADE;
DROP TABLE IF EXISTS "spdx"."document_namespaces" CASCADE;
DROP TABLE IF EXISTS "spdx"."documents" CASCADE;
DROP TABLE IF EXISTS "spdx"."documents_creators" CASCADE;
DROP TABLE IF EXISTS "spdx"."external_refs" CASCADE;
DROP TABLE IF EXISTS "spdx"."file_contributors" CASCADE;
DROP TABLE IF EXISTS "spdx"."file_types" CASCADE;
DROP TABLE IF EXISTS "spdx"."files" CASCADE;
DROP TABLE IF EXISTS "spdx"."files_licenses" CASCADE;
DROP TABLE IF EXISTS "spdx"."files_scans" CASCADE;
DROP TABLE IF EXISTS "spdx"."identifiers" CASCADE;
DROP TABLE IF EXISTS "spdx"."licenses" CASCADE;
DROP TABLE IF EXISTS "spdx"."packages" CASCADE;
DROP TABLE IF EXISTS "spdx"."packages_files" CASCADE;
DROP TABLE IF EXISTS "spdx"."packages_scans" CASCADE;
DROP TABLE IF EXISTS "spdx"."projects" CASCADE;
DROP TABLE IF EXISTS "spdx"."relationship_types" CASCADE;
DROP TABLE IF EXISTS "spdx"."relationships" CASCADE;
DROP TABLE IF EXISTS "spdx"."sbom_scans" CASCADE;
DROP TABLE IF EXISTS "spdx"."scanners" CASCADE;

CREATE TABLE IF NOT EXISTS "augur_data"."analysis_log" (
  "repos_id" int4 NOT NULL,
  "status" varchar COLLATE "pg_catalog"."default" NOT NULL,
  "date_attempted" timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP
);
ALTER TABLE IF EXISTS "augur_data"."analysis_log" OWNER TO "augur";
CREATE INDEX "repos_id" ON "augur_data"."analysis_log" USING btree (
  "repos_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);

CREATE TABLE IF NOT EXISTS "augur_data"."chaoss_metric_status" (
  "cms_id" int8 NOT NULL DEFAULT nextval('"augur_data".chaoss_metric_status_cms_id_seq'::regclass),
  "cm_group" varchar COLLATE "pg_catalog"."default",
  "cm_source" varchar COLLATE "pg_catalog"."default",
  "cm_type" varchar COLLATE "pg_catalog"."default",
  "cm_backend_status" varchar COLLATE "pg_catalog"."default",
  "cm_frontend_status" varchar COLLATE "pg_catalog"."default",
  "cm_defined" bool,
  "cm_api_endpoint_repo" varchar COLLATE "pg_catalog"."default",
  "cm_api_endpoint_rg" varchar COLLATE "pg_catalog"."default",
  "cm_name" varchar COLLATE "pg_catalog"."default",
  "cm_working_group" varchar COLLATE "pg_catalog"."default",
  "cm_info" json,
  "tool_source" varchar COLLATE "pg_catalog"."default",
  "tool_version" varchar COLLATE "pg_catalog"."default",
  "data_source" varchar COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  "cm_working_group_focus_area" varchar COLLATE "pg_catalog"."default",
  CONSTRAINT "chaoss_metric_status_pkey" PRIMARY KEY ("cms_id")
);
ALTER TABLE IF EXISTS "augur_data"."chaoss_metric_status" OWNER TO "augur";
COMMENT ON TABLE "augur_data"."chaoss_metric_status" IS 'This table used to track CHAOSS Metric implementations in Augur, but due to the constantly changing location of that information, it is for the moment not actively populated. ';

CREATE TABLE IF NOT EXISTS "augur_data"."commit_comment_ref" (
  "cmt_comment_id" int8 NOT NULL DEFAULT nextval('"augur_data".commit_comment_ref_cmt_comment_id_seq'::regclass),
  "cmt_id" int8 NOT NULL,
  "msg_id" int8 NOT NULL,
  "user_id" int8 NOT NULL,
  "body" text COLLATE "pg_catalog"."default",
  "line" int8,
  "position" int8,
  "created_at" timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  "cmt_comment_src_id" int8 NOT NULL,
  "commit_comment_src_node_id" varchar COLLATE "pg_catalog"."default",
  CONSTRAINT "commit_comment_ref_pkey" PRIMARY KEY ("cmt_comment_id"),
  CONSTRAINT "commitcomment" UNIQUE ("cmt_id", "msg_id", "cmt_comment_id")
);
ALTER TABLE IF EXISTS "augur_data"."commit_comment_ref" OWNER TO "augur";
CREATE INDEX "comment_id" ON "augur_data"."commit_comment_ref" USING btree (
  "cmt_comment_src_id" "pg_catalog"."int8_ops" ASC NULLS LAST,
  "cmt_comment_id" "pg_catalog"."int8_ops" ASC NULLS LAST,
  "msg_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
COMMENT ON COLUMN "augur_data"."commit_comment_ref"."cmt_comment_src_id" IS 'For data provenance, we store the source ID if it exists. ';
COMMENT ON COLUMN "augur_data"."commit_comment_ref"."commit_comment_src_node_id" IS 'For data provenance, we store the source node ID if it exists. ';

CREATE TABLE IF NOT EXISTS "augur_data"."commit_parents" (
  "cmt_id" int8 NOT NULL,
  "parent_id" int8 NOT NULL DEFAULT nextval('"augur_data".commit_parents_parent_id_seq'::regclass),
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "commit_parents_pkey" PRIMARY KEY ("cmt_id", "parent_id")
);
ALTER TABLE IF EXISTS "augur_data"."commit_parents" OWNER TO "augur";
CREATE INDEX "commit_parents_ibfk_1" ON "augur_data"."commit_parents" USING btree (
  "cmt_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "commit_parents_ibfk_2" ON "augur_data"."commit_parents" USING btree (
  "parent_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);

CREATE TABLE IF NOT EXISTS "augur_data"."commits" (
  "cmt_id" int8 NOT NULL DEFAULT nextval('"augur_data".commits_cmt_id_seq'::regclass),
  "repo_id" int8 NOT NULL,
  "cmt_commit_hash" varchar(80) COLLATE "pg_catalog"."default" NOT NULL,
  "cmt_author_name" varchar(128) COLLATE "pg_catalog"."default" NOT NULL,
  "cmt_author_raw_email" varchar(128) COLLATE "pg_catalog"."default" NOT NULL,
  "cmt_author_email" varchar COLLATE "pg_catalog"."default" NOT NULL,
  "cmt_author_date" varchar(10) COLLATE "pg_catalog"."default" NOT NULL,
  "cmt_author_affiliation" varchar(128) COLLATE "pg_catalog"."default" DEFAULT 'NULL'::character varying,
  "cmt_committer_name" varchar(128) COLLATE "pg_catalog"."default" NOT NULL,
  "cmt_committer_raw_email" varchar(128) COLLATE "pg_catalog"."default" NOT NULL,
  "cmt_committer_email" varchar COLLATE "pg_catalog"."default" NOT NULL,
  "cmt_committer_date" varchar(10) COLLATE "pg_catalog"."default" NOT NULL,
  "cmt_committer_affiliation" varchar(128) COLLATE "pg_catalog"."default" DEFAULT 'NULL'::character varying,
  "cmt_added" int4 NOT NULL,
  "cmt_removed" int4 NOT NULL,
  "cmt_whitespace" int4 NOT NULL,
  "cmt_filename" varchar(4096) COLLATE "pg_catalog"."default" NOT NULL,
  "cmt_date_attempted" timestamp(0) NOT NULL,
  "cmt_ght_author_id" int4,
  "cmt_ght_committer_id" int4,
  "cmt_ght_committed_at" timestamp(0),
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  "cmt_author_timestamp" timestamptz(0),
  "cmt_committer_timestamp" timestamptz(0),
  CONSTRAINT "commits_pkey" PRIMARY KEY ("cmt_id")
);
ALTER TABLE IF EXISTS "augur_data"."commits" OWNER TO "augur";
CREATE INDEX CONCURRENTLY "author_affiliation" ON "augur_data"."commits" USING hash (
  "cmt_author_affiliation" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops"
);
CREATE INDEX CONCURRENTLY "author_cntrb_id" ON "augur_data"."commits" USING btree (
  "cmt_ght_author_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX CONCURRENTLY "author_email,author_affiliation,author_date" ON "augur_data"."commits" USING btree (
  "cmt_author_email" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "cmt_author_affiliation" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "cmt_author_date" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX CONCURRENTLY "author_raw_email" ON "augur_data"."commits" USING btree (
  "cmt_author_raw_email" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX CONCURRENTLY "cmt-author-date-idx2" ON "augur_data"."commits" USING btree (
  "cmt_author_date" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX CONCURRENTLY "cmt-committer-date-idx3" ON "augur_data"."commits" USING btree (
  "cmt_committer_date" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX CONCURRENTLY "cmt_author-name-idx5" ON "augur_data"."commits" USING btree (
  "cmt_committer_name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX CONCURRENTLY "cmt_author_contrib_worker" ON "augur_data"."commits" USING brin (
  "cmt_author_name" COLLATE "pg_catalog"."default" "pg_catalog"."text_minmax_ops",
  "cmt_author_email" COLLATE "pg_catalog"."default" "pg_catalog"."text_minmax_ops",
  "cmt_author_date" COLLATE "pg_catalog"."default" "pg_catalog"."text_minmax_ops"
);
CREATE INDEX CONCURRENTLY "cmt_cmmter-name-idx4" ON "augur_data"."commits" USING btree (
  "cmt_author_name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX CONCURRENTLY "cmt_commiter_contrib_worker" ON "augur_data"."commits" USING brin (
  "cmt_committer_name" COLLATE "pg_catalog"."default" "pg_catalog"."text_minmax_ops",
  "cmt_committer_email" COLLATE "pg_catalog"."default" "pg_catalog"."text_minmax_ops",
  "cmt_committer_date" COLLATE "pg_catalog"."default" "pg_catalog"."text_minmax_ops"
);
CREATE INDEX CONCURRENTLY "commited" ON "augur_data"."commits" USING btree (
  "cmt_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX CONCURRENTLY "commits_idx_cmt_email_cmt_date_cmt_name" ON "augur_data"."commits" USING btree (
  "cmt_author_email" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "cmt_author_date" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "cmt_author_name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX CONCURRENTLY "commits_idx_cmt_email_cmt_date_cmt_name2" ON "augur_data"."commits" USING btree (
  "cmt_committer_email" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "cmt_committer_date" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "cmt_committer_name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX CONCURRENTLY "commits_idx_cmt_name_cmt_date2" ON "augur_data"."commits" USING btree (
  "cmt_author_name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "cmt_author_date" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX CONCURRENTLY "commits_idx_cmt_name_cmt_date_cmt_date3" ON "augur_data"."commits" USING btree (
  "cmt_committer_name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "cmt_author_date" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "cmt_committer_date" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX CONCURRENTLY "commits_idx_repo_id_cmt_ema_cmt_dat_cmt_nam" ON "augur_data"."commits" USING btree (
  "repo_id" "pg_catalog"."int8_ops" ASC NULLS LAST,
  "cmt_author_email" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "cmt_author_date" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "cmt_author_name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX CONCURRENTLY "commits_idx_repo_id_cmt_ema_cmt_dat_cmt_nam2" ON "augur_data"."commits" USING btree (
  "repo_id" "pg_catalog"."int8_ops" ASC NULLS LAST,
  "cmt_committer_email" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "cmt_committer_date" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "cmt_committer_name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX CONCURRENTLY "commits_idx_repo_id_cmt_ema_cmt_nam_cmt_dat2" ON "augur_data"."commits" USING btree (
  "repo_id" "pg_catalog"."int8_ops" ASC NULLS LAST,
  "cmt_author_email" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "cmt_author_name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "cmt_author_date" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX CONCURRENTLY "commits_idx_repo_id_cmt_ema_cmt_nam_cmt_dat3" ON "augur_data"."commits" USING btree (
  "repo_id" "pg_catalog"."int8_ops" ASC NULLS LAST,
  "cmt_committer_email" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "cmt_committer_name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "cmt_author_date" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX CONCURRENTLY "committer_affiliation" ON "augur_data"."commits" USING btree (
  "cmt_committer_affiliation" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX CONCURRENTLY "committer_cntrb_id" ON "augur_data"."commits" USING btree (
  "cmt_ght_committer_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX CONCURRENTLY "committer_email,committer_affiliation,committer_date" ON "augur_data"."commits" USING btree (
  "cmt_committer_email" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "cmt_committer_affiliation" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "cmt_committer_date" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX CONCURRENTLY "committer_raw_email" ON "augur_data"."commits" USING btree (
  "cmt_committer_raw_email" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX CONCURRENTLY "repo_id,commit" ON "augur_data"."commits" USING btree (
  "repo_id" "pg_catalog"."int8_ops" ASC NULLS LAST,
  "cmt_commit_hash" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
COMMENT ON TABLE "augur_data"."commits" IS 'Starts with augur.analysis_data table and incorporates GHTorrent commit table attributes if different. 
Cmt_id is from get
The author and committer ID’s are at the bottom of the table and not required for now because we want to focus on the facade schema’s properties over the ghtorrent properties when they are in conflict. ';

CREATE TABLE IF NOT EXISTS "augur_data"."contributor_affiliations" (
  "ca_id" int8 NOT NULL DEFAULT nextval('"augur_data".contributor_affiliations_ca_id_seq'::regclass),
  "ca_domain" varchar(64) COLLATE "pg_catalog"."default" NOT NULL,
  "ca_start_date" date DEFAULT '1970-01-01'::date,
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  "ca_last_used" timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "ca_affiliation" varchar COLLATE "pg_catalog"."default",
  "ca_active" int2 DEFAULT 1,
  CONSTRAINT "contributor_affiliations_pkey" PRIMARY KEY ("ca_id"),
  CONSTRAINT "unique_domain" UNIQUE ("ca_domain")
);
ALTER TABLE IF EXISTS "augur_data"."contributor_affiliations" OWNER TO "augur";
COMMENT ON CONSTRAINT "unique_domain" ON "augur_data"."contributor_affiliations" IS 'Only one row should exist for any given top level domain or subdomain. ';

CREATE TABLE IF NOT EXISTS "augur_data"."contributors" (
  "cntrb_id" int8 NOT NULL DEFAULT nextval('"augur_data".contributors_cntrb_id_seq'::regclass),
  "cntrb_login" varchar(255) COLLATE "pg_catalog"."default",
  "cntrb_email" varchar COLLATE "pg_catalog"."default",
  "cntrb_company" varchar(255) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "cntrb_created_at" timestamp(0),
  "cntrb_type" varchar(255) COLLATE "pg_catalog"."default",
  "cntrb_fake" int2 DEFAULT 0,
  "cntrb_deleted" int2 DEFAULT 0,
  "cntrb_long" numeric(11,8) DEFAULT NULL::numeric,
  "cntrb_lat" numeric(10,8) DEFAULT NULL::numeric,
  "cntrb_country_code" char(3) COLLATE "pg_catalog"."default" DEFAULT NULL::bpchar,
  "cntrb_state" varchar(255) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "cntrb_city" varchar(255) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "cntrb_location" varchar(255) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "cntrb_canonical" varchar COLLATE "pg_catalog"."default",
  "gh_user_id" int8,
  "gh_login" varchar(255) COLLATE "pg_catalog"."default",
  "gh_url" varchar(255) COLLATE "pg_catalog"."default",
  "gh_html_url" varchar(255) COLLATE "pg_catalog"."default",
  "gh_node_id" varchar(255) COLLATE "pg_catalog"."default",
  "gh_avatar_url" varchar(4000) COLLATE "pg_catalog"."default",
  "gh_gravatar_id" varchar(255) COLLATE "pg_catalog"."default",
  "gh_followers_url" varchar(4000) COLLATE "pg_catalog"."default",
  "gh_following_url" varchar(4000) COLLATE "pg_catalog"."default",
  "gh_gists_url" varchar(4000) COLLATE "pg_catalog"."default",
  "gh_starred_url" varchar(4000) COLLATE "pg_catalog"."default",
  "gh_subscriptions_url" varchar(4000) COLLATE "pg_catalog"."default",
  "gh_organizations_url" varchar(4000) COLLATE "pg_catalog"."default",
  "gh_repos_url" varchar(4000) COLLATE "pg_catalog"."default",
  "gh_events_url" varchar(4000) COLLATE "pg_catalog"."default",
  "gh_received_events_url" varchar(4000) COLLATE "pg_catalog"."default",
  "gh_type" varchar(255) COLLATE "pg_catalog"."default",
  "gh_site_admin" varchar(255) COLLATE "pg_catalog"."default",
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  "cntrb_full_name" varchar COLLATE "pg_catalog"."default",
  "cntrb_last_used" timestamptz(0) DEFAULT NULL::timestamp with time zone,
  CONSTRAINT "contributors_pkey" PRIMARY KEY ("cntrb_id")
);
ALTER TABLE IF EXISTS "augur_data"."contributors" OWNER TO "augur";
CREATE INDEX "cnt-fullname" ON "augur_data"."contributors" USING hash (
  "cntrb_full_name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops"
);
CREATE INDEX "cntrb-theemail" ON "augur_data"."contributors" USING hash (
  "cntrb_email" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops"
);
CREATE INDEX "cntrb_login_platform_index" ON "augur_data"."contributors" USING btree (
  "cntrb_login" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "contributor_delete_finder" ON "augur_data"."contributors" USING brin (
  "cntrb_id" "pg_catalog"."int8_minmax_ops",
  "cntrb_email" COLLATE "pg_catalog"."default" "pg_catalog"."text_minmax_ops"
);
CREATE INDEX "contributor_worker_email_finder" ON "augur_data"."contributors" USING brin (
  "cntrb_email" COLLATE "pg_catalog"."default" "pg_catalog"."text_minmax_ops"
);
CREATE INDEX "contributor_worker_finder" ON "augur_data"."contributors" USING brin (
  "cntrb_login" COLLATE "pg_catalog"."default" "pg_catalog"."text_minmax_ops",
  "cntrb_email" COLLATE "pg_catalog"."default" "pg_catalog"."text_minmax_ops",
  "cntrb_id" "pg_catalog"."int8_minmax_ops"
);
CREATE INDEX "contributor_worker_fullname_finder" ON "augur_data"."contributors" USING brin (
  "cntrb_full_name" COLLATE "pg_catalog"."default" "pg_catalog"."text_minmax_ops"
);
CREATE INDEX "contributors_idx_cntrb_email3" ON "augur_data"."contributors" USING btree (
  "cntrb_email" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "login" ON "augur_data"."contributors" USING btree (
  "cntrb_login" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "login-contributor-idx" ON "augur_data"."contributors" USING btree (
  "cntrb_login" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
COMMENT ON COLUMN "augur_data"."contributors"."cntrb_login" IS 'Will be a double population with the same value as gh_login for github, but the local value for other systems. ';
COMMENT ON COLUMN "augur_data"."contributors"."cntrb_email" IS 'This needs to be here for matching contributor ids, which are augur, to the commit information. ';
COMMENT ON COLUMN "augur_data"."contributors"."cntrb_type" IS 'Present in another models. It is not currently used in Augur. ';
COMMENT ON COLUMN "augur_data"."contributors"."gh_login" IS 'populated with the github user name for github originated data. ';
COMMENT ON TABLE "augur_data"."contributors" IS 'For GitHub, this should be repeated from gh_login. for other systems, it should be that systems login. ';

CREATE TABLE IF NOT EXISTS "augur_data"."contributors_aliases" (
  "cntrb_id" int8 NOT NULL,
  "cntrb_a_id" int8 NOT NULL DEFAULT nextval('"augur_data".contributors_aliases_cntrb_a_id_seq'::regclass),
  "canonical_email" varchar COLLATE "pg_catalog"."default" NOT NULL,
  "alias_email" varchar(128) COLLATE "pg_catalog"."default" NOT NULL,
  "cntrb_active" int2 NOT NULL DEFAULT 1,
  "cntrb_last_modified" timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "contributors_aliases_pkey" PRIMARY KEY ("cntrb_id", "cntrb_a_id")
);
ALTER TABLE IF EXISTS "augur_data"."contributors_aliases" OWNER TO "augur";
CREATE INDEX "alias,active" ON "augur_data"."contributors_aliases" USING btree (
  "alias_email" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "cntrb_active" "pg_catalog"."int2_ops" ASC NULLS LAST
);
CREATE UNIQUE INDEX "canonical,alias" ON "augur_data"."contributors_aliases" USING btree (
  "canonical_email" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "alias_email" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "issue-alias-cntrb-idx1" ON "augur_data"."contributors_aliases" USING btree (
  "cntrb_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "issue-alias-cntrb-idx2" ON "augur_data"."contributors_aliases" USING btree (
  "cntrb_a_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
COMMENT ON TABLE "augur_data"."contributors_aliases" IS 'An alias will need to be created for every contributor in this model, otherwise we will have to look in 2 places. ';

CREATE TABLE IF NOT EXISTS "augur_data"."contributors_history" (
  "cntrb_history_id" int8 NOT NULL DEFAULT nextval('"augur_data".contributors_history_cntrb_history_id_seq'::regclass),
  "cntrb_id" int8 NOT NULL,
  "cntrb_history_timestamp" timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "cntrb_history_current_bool" bool,
  "cntrb_organizations_list" json,
  "cntrb_gists_count" int8,
  "cntrb_starred_count" int8,
  "cntrb_following_count" int8,
  "cntrb_follower_count" int8,
  "cntrb_login" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "cntrb_email" varchar(255) COLLATE "pg_catalog"."default",
  "cntrb_company" varchar(255) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "cntrb_created_at" timestamp(0) NOT NULL,
  "cntrb_type" varchar(255) COLLATE "pg_catalog"."default",
  "cntrb_fake" int2 NOT NULL DEFAULT 0,
  "cntrb_deleted" int2 NOT NULL DEFAULT 0,
  "cntrb_long" numeric(11,8) DEFAULT NULL::numeric,
  "cntrb_lat" numeric(10,8) DEFAULT NULL::numeric,
  "cntrb_country_code" char(3) COLLATE "pg_catalog"."default" DEFAULT NULL::bpchar,
  "cntrb_state" varchar(255) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "cntrb_city" varchar(255) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "cntrb_location" varchar(255) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "cntrb_canonical" varchar(128) COLLATE "pg_catalog"."default",
  "gh_user_id" int8,
  "gh_login" varchar(255) COLLATE "pg_catalog"."default",
  "gh_url" varchar(255) COLLATE "pg_catalog"."default",
  "gh_html_url" varchar(255) COLLATE "pg_catalog"."default",
  "gh_node_id" varchar(255) COLLATE "pg_catalog"."default",
  "gh_avatar_url" varchar(4000) COLLATE "pg_catalog"."default",
  "gh_gravatar_id" varchar(255) COLLATE "pg_catalog"."default",
  "gh_followers_url" varchar(4000) COLLATE "pg_catalog"."default",
  "gh_following_url" varchar(4000) COLLATE "pg_catalog"."default",
  "gh_gists_url" varchar(4000) COLLATE "pg_catalog"."default",
  "gh_starred_url" varchar(4000) COLLATE "pg_catalog"."default",
  "gh_subscriptions_url" varchar(4000) COLLATE "pg_catalog"."default",
  "gh_organizations_url" varchar(4000) COLLATE "pg_catalog"."default",
  "gh_repos_url" varchar(4000) COLLATE "pg_catalog"."default",
  "gh_events_url" varchar(4000) COLLATE "pg_catalog"."default",
  "gh_received_events_url" varchar(4000) COLLATE "pg_catalog"."default",
  "gh_type" varchar(255) COLLATE "pg_catalog"."default",
  "gh_site_admin" varchar(255) COLLATE "pg_catalog"."default",
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "contributors_history_pkey" PRIMARY KEY ("cntrb_history_id")
);
ALTER TABLE IF EXISTS "augur_data"."contributors_history" OWNER TO "augur";
CREATE INDEX "contrb-history-dix1" ON "augur_data"."contributors_history" USING btree (
  "cntrb_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "login_index_2" ON "augur_data"."contributors_history" USING btree (
  "cntrb_login" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
COMMENT ON COLUMN "augur_data"."contributors_history"."cntrb_history_current_bool" IS 'At some point it would be great to have a boolean updated by a contributor worker that set the most recent contributor data to true. ';
COMMENT ON COLUMN "augur_data"."contributors_history"."cntrb_login" IS 'Will be a double population with the same value as gh_login for github, but the local value for other systems. ';
COMMENT ON COLUMN "augur_data"."contributors_history"."cntrb_email" IS 'This needs to be here for matching contributor ids, which are augur, to the commit information. ';
COMMENT ON COLUMN "augur_data"."contributors_history"."cntrb_type" IS 'Present in another models. It is not currently used in Augur. ';
COMMENT ON COLUMN "augur_data"."contributors_history"."gh_login" IS 'populated with the github user name for github originated data. ';
COMMENT ON TABLE "augur_data"."contributors_history" IS 'For GitHub, this should be repeated from gh_login. for other systems, it should be that systems login. 

At this time the table is not populated. ';

CREATE TABLE IF NOT EXISTS "augur_data"."discourse_insights" (
  "msg_discourse_id" serial8,
  "msg_id" int8,
  "discourse_act" varchar,
  "tool_source" varchar,
  "tool_version" varchar,
  "data_source" varchar,
  "data_collection_date" timestamptz DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("msg_discourse_id")
);
ALTER TABLE IF EXISTS "augur_data"."discourse_insights" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "augur_data"."dm_repo_annual" (
  "repo_id" int8 NOT NULL,
  "email" varchar(128) COLLATE "pg_catalog"."default" NOT NULL,
  "affiliation" varchar(128) COLLATE "pg_catalog"."default" DEFAULT 'NULL'::character varying,
  "year" int2 NOT NULL,
  "added" int8 NOT NULL,
  "removed" int8 NOT NULL,
  "whitespace" int8 NOT NULL,
  "files" int8 NOT NULL,
  "patches" int8 NOT NULL,
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP
);
ALTER TABLE IF EXISTS "augur_data"."dm_repo_annual" OWNER TO "augur";
CREATE INDEX "repo_id,affiliation_copy_1" ON "augur_data"."dm_repo_annual" USING btree (
  "repo_id" "pg_catalog"."int8_ops" ASC NULLS LAST,
  "affiliation" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "repo_id,email_copy_1" ON "augur_data"."dm_repo_annual" USING btree (
  "repo_id" "pg_catalog"."int8_ops" ASC NULLS LAST,
  "email" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

CREATE TABLE IF NOT EXISTS "augur_data"."dm_repo_group_annual" (
  "repo_group_id" int8 NOT NULL,
  "email" varchar(128) COLLATE "pg_catalog"."default" NOT NULL,
  "affiliation" varchar(128) COLLATE "pg_catalog"."default" DEFAULT 'NULL'::character varying,
  "year" int2 NOT NULL,
  "added" int8 NOT NULL,
  "removed" int8 NOT NULL,
  "whitespace" int8 NOT NULL,
  "files" int8 NOT NULL,
  "patches" int8 NOT NULL,
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP
);
ALTER TABLE IF EXISTS "augur_data"."dm_repo_group_annual" OWNER TO "augur";
CREATE INDEX "projects_id,affiliation_copy_1" ON "augur_data"."dm_repo_group_annual" USING btree (
  "repo_group_id" "pg_catalog"."int8_ops" ASC NULLS LAST,
  "affiliation" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "projects_id,email_copy_1" ON "augur_data"."dm_repo_group_annual" USING btree (
  "repo_group_id" "pg_catalog"."int8_ops" ASC NULLS LAST,
  "email" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

CREATE TABLE IF NOT EXISTS "augur_data"."dm_repo_group_monthly" (
  "repo_group_id" int8 NOT NULL,
  "email" varchar(128) COLLATE "pg_catalog"."default" NOT NULL,
  "affiliation" varchar(128) COLLATE "pg_catalog"."default" DEFAULT 'NULL'::character varying,
  "month" int2 NOT NULL,
  "year" int2 NOT NULL,
  "added" int8 NOT NULL,
  "removed" int8 NOT NULL,
  "whitespace" int8 NOT NULL,
  "files" int8 NOT NULL,
  "patches" int8 NOT NULL,
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP
);
ALTER TABLE IF EXISTS "augur_data"."dm_repo_group_monthly" OWNER TO "augur";
CREATE INDEX "projects_id,affiliation_copy_2" ON "augur_data"."dm_repo_group_monthly" USING btree (
  "repo_group_id" "pg_catalog"."int8_ops" ASC NULLS LAST,
  "affiliation" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "projects_id,email_copy_2" ON "augur_data"."dm_repo_group_monthly" USING btree (
  "repo_group_id" "pg_catalog"."int8_ops" ASC NULLS LAST,
  "email" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "projects_id,year,affiliation_copy_1" ON "augur_data"."dm_repo_group_monthly" USING btree (
  "repo_group_id" "pg_catalog"."int8_ops" ASC NULLS LAST,
  "year" "pg_catalog"."int2_ops" ASC NULLS LAST,
  "affiliation" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "projects_id,year,email_copy_1" ON "augur_data"."dm_repo_group_monthly" USING btree (
  "repo_group_id" "pg_catalog"."int8_ops" ASC NULLS LAST,
  "year" "pg_catalog"."int2_ops" ASC NULLS LAST,
  "email" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

CREATE TABLE IF NOT EXISTS "augur_data"."dm_repo_group_weekly" (
  "repo_group_id" int8 NOT NULL,
  "email" varchar(128) COLLATE "pg_catalog"."default" NOT NULL,
  "affiliation" varchar(128) COLLATE "pg_catalog"."default" DEFAULT 'NULL'::character varying,
  "week" int2 NOT NULL,
  "year" int2 NOT NULL,
  "added" int8 NOT NULL,
  "removed" int8 NOT NULL,
  "whitespace" int8 NOT NULL,
  "files" int8 NOT NULL,
  "patches" int8 NOT NULL,
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP
);
ALTER TABLE IF EXISTS "augur_data"."dm_repo_group_weekly" OWNER TO "augur";
CREATE INDEX "projects_id,affiliation" ON "augur_data"."dm_repo_group_weekly" USING btree (
  "repo_group_id" "pg_catalog"."int8_ops" ASC NULLS LAST,
  "affiliation" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "projects_id,email" ON "augur_data"."dm_repo_group_weekly" USING btree (
  "repo_group_id" "pg_catalog"."int8_ops" ASC NULLS LAST,
  "email" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "projects_id,year,affiliation" ON "augur_data"."dm_repo_group_weekly" USING btree (
  "repo_group_id" "pg_catalog"."int8_ops" ASC NULLS LAST,
  "year" "pg_catalog"."int2_ops" ASC NULLS LAST,
  "affiliation" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "projects_id,year,email" ON "augur_data"."dm_repo_group_weekly" USING btree (
  "repo_group_id" "pg_catalog"."int8_ops" ASC NULLS LAST,
  "year" "pg_catalog"."int2_ops" ASC NULLS LAST,
  "email" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

CREATE TABLE IF NOT EXISTS "augur_data"."dm_repo_monthly" (
  "repo_id" int8 NOT NULL,
  "email" varchar(128) COLLATE "pg_catalog"."default" NOT NULL,
  "affiliation" varchar(128) COLLATE "pg_catalog"."default" DEFAULT 'NULL'::character varying,
  "month" int2 NOT NULL,
  "year" int2 NOT NULL,
  "added" int8 NOT NULL,
  "removed" int8 NOT NULL,
  "whitespace" int8 NOT NULL,
  "files" int8 NOT NULL,
  "patches" int8 NOT NULL,
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP
);
ALTER TABLE IF EXISTS "augur_data"."dm_repo_monthly" OWNER TO "augur";
CREATE INDEX "repo_id,affiliation_copy_2" ON "augur_data"."dm_repo_monthly" USING btree (
  "repo_id" "pg_catalog"."int8_ops" ASC NULLS LAST,
  "affiliation" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "repo_id,email_copy_2" ON "augur_data"."dm_repo_monthly" USING btree (
  "repo_id" "pg_catalog"."int8_ops" ASC NULLS LAST,
  "email" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "repo_id,year,affiliation_copy_1" ON "augur_data"."dm_repo_monthly" USING btree (
  "repo_id" "pg_catalog"."int8_ops" ASC NULLS LAST,
  "year" "pg_catalog"."int2_ops" ASC NULLS LAST,
  "affiliation" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "repo_id,year,email_copy_1" ON "augur_data"."dm_repo_monthly" USING btree (
  "repo_id" "pg_catalog"."int8_ops" ASC NULLS LAST,
  "year" "pg_catalog"."int2_ops" ASC NULLS LAST,
  "email" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

CREATE TABLE IF NOT EXISTS "augur_data"."dm_repo_weekly" (
  "repo_id" int8 NOT NULL,
  "email" varchar(128) COLLATE "pg_catalog"."default" NOT NULL,
  "affiliation" varchar(128) COLLATE "pg_catalog"."default" DEFAULT 'NULL'::character varying,
  "week" int2 NOT NULL,
  "year" int2 NOT NULL,
  "added" int8 NOT NULL,
  "removed" int8 NOT NULL,
  "whitespace" int8 NOT NULL,
  "files" int8 NOT NULL,
  "patches" int8 NOT NULL,
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP
);
ALTER TABLE IF EXISTS "augur_data"."dm_repo_weekly" OWNER TO "augur";
CREATE INDEX "repo_id,affiliation" ON "augur_data"."dm_repo_weekly" USING btree (
  "repo_id" "pg_catalog"."int8_ops" ASC NULLS LAST,
  "affiliation" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "repo_id,email" ON "augur_data"."dm_repo_weekly" USING btree (
  "repo_id" "pg_catalog"."int8_ops" ASC NULLS LAST,
  "email" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "repo_id,year,affiliation" ON "augur_data"."dm_repo_weekly" USING btree (
  "repo_id" "pg_catalog"."int8_ops" ASC NULLS LAST,
  "year" "pg_catalog"."int2_ops" ASC NULLS LAST,
  "affiliation" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "repo_id,year,email" ON "augur_data"."dm_repo_weekly" USING btree (
  "repo_id" "pg_catalog"."int8_ops" ASC NULLS LAST,
  "year" "pg_catalog"."int2_ops" ASC NULLS LAST,
  "email" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

CREATE TABLE IF NOT EXISTS "augur_data"."exclude" (
  "id" int4 NOT NULL,
  "projects_id" int4 NOT NULL,
  "email" varchar(128) COLLATE "pg_catalog"."default" DEFAULT 'NULL'::character varying,
  "domain" varchar(128) COLLATE "pg_catalog"."default" DEFAULT 'NULL'::character varying,
  CONSTRAINT "exclude_pkey" PRIMARY KEY ("id")
);
ALTER TABLE IF EXISTS "augur_data"."exclude" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "augur_data"."issue_assignees" (
  "issue_assignee_id" int8 NOT NULL DEFAULT nextval('"augur_data".issue_assignees_issue_assignee_id_seq'::regclass),
  "issue_id" int8,
  "cntrb_id" int8,
  "tool_source" varchar COLLATE "pg_catalog"."default",
  "tool_version" varchar COLLATE "pg_catalog"."default",
  "data_source" varchar COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  "issue_assignee_src_id" int8,
  "issue_assignee_src_node" varchar COLLATE "pg_catalog"."default",
  CONSTRAINT "issue_assignees_pkey" PRIMARY KEY ("issue_assignee_id")
);
ALTER TABLE IF EXISTS "augur_data"."issue_assignees" OWNER TO "augur";
CREATE INDEX "issue-cntrb-assign-idx-1" ON "augur_data"."issue_assignees" USING btree (
  "cntrb_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
COMMENT ON COLUMN "augur_data"."issue_assignees"."issue_assignee_src_id" IS 'This ID comes from the source. In the case of GitHub, it is the id that is the first field returned from the issue events API in the issue_assignees embedded JSON object. We may discover it is an ID for the person themselves; but my hypothesis is that its not.';
COMMENT ON COLUMN "augur_data"."issue_assignees"."issue_assignee_src_node" IS 'This character based identifier comes from the source. In the case of GitHub, it is the id that is the second field returned from the issue events API in the issue_assignees embedded JSON object. We may discover it is an ID for the person themselves; but my hypothesis is that its not.';

CREATE TABLE IF NOT EXISTS "augur_data"."issue_events" (
  "event_id" int8 NOT NULL DEFAULT nextval('"augur_data".issue_events_event_id_seq'::regclass),
  "issue_id" int8 NOT NULL,
  "cntrb_id" int8 NOT NULL,
  "action" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "action_commit_hash" varchar COLLATE "pg_catalog"."default",
  "created_at" timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "node_id" varchar COLLATE "pg_catalog"."default",
  "node_url" varchar COLLATE "pg_catalog"."default",
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  "issue_event_src_id" int8,
  CONSTRAINT "issue_events_pkey" PRIMARY KEY ("event_id")
);
ALTER TABLE IF EXISTS "augur_data"."issue_events" OWNER TO "augur";
CREATE INDEX "issue-cntrb-idx2" ON "augur_data"."issue_events" USING btree (
  "issue_event_src_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "issue_events_ibfk_1" ON "augur_data"."issue_events" USING btree (
  "issue_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "issue_events_ibfk_2" ON "augur_data"."issue_events" USING btree (
  "cntrb_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
COMMENT ON COLUMN "augur_data"."issue_events"."node_id" IS 'This should be renamed to issue_event_src_node_id, as its the varchar identifier in GitHub and likely common in other sources as well. However, since it was created before we came to this naming standard and workers are built around it, we have it simply named as node_id. Anywhere you see node_id in the schema, it comes from GitHubs terminology.';
COMMENT ON COLUMN "augur_data"."issue_events"."issue_event_src_id" IS 'This ID comes from the source. In the case of GitHub, it is the id that is the first field returned from the issue events API';

CREATE TABLE IF NOT EXISTS "augur_data"."issue_labels" (
  "issue_label_id" int8 NOT NULL DEFAULT nextval('"augur_data".issue_labels_issue_label_id_seq'::regclass),
  "issue_id" int8,
  "label_text" varchar COLLATE "pg_catalog"."default",
  "label_description" varchar COLLATE "pg_catalog"."default",
  "label_color" varchar COLLATE "pg_catalog"."default",
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  "label_src_id" int8,
  "label_src_node_id" varchar COLLATE "pg_catalog"."default",
  CONSTRAINT "issue_labels_pkey" PRIMARY KEY ("issue_label_id")
);
ALTER TABLE IF EXISTS "augur_data"."issue_labels" OWNER TO "augur";
COMMENT ON COLUMN "augur_data"."issue_labels"."label_src_id" IS 'This character based identifier (node) comes from the source. In the case of GitHub, it is the id that is the second field returned from the issue events API JSON subsection for issues.';

CREATE TABLE IF NOT EXISTS "augur_data"."issue_message_ref" (
  "issue_msg_ref_id" int8 NOT NULL DEFAULT nextval('"augur_data".issue_message_ref_issue_msg_ref_id_seq'::regclass),
  "issue_id" int8,
  "msg_id" int8,
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  "issue_msg_ref_src_comment_id" int8,
  "issue_msg_ref_src_node_id" varchar COLLATE "pg_catalog"."default",
  CONSTRAINT "issue_message_ref_pkey" PRIMARY KEY ("issue_msg_ref_id")
);
ALTER TABLE IF EXISTS "augur_data"."issue_message_ref" OWNER TO "augur";
COMMENT ON COLUMN "augur_data"."issue_message_ref"."issue_msg_ref_src_comment_id" IS 'This ID comes from the source. In the case of GitHub, it is the id that is the first field returned from the issue comments API';
COMMENT ON COLUMN "augur_data"."issue_message_ref"."issue_msg_ref_src_node_id" IS 'This character based identifier comes from the source. In the case of GitHub, it is the id that is the first field returned from the issue comments API';

CREATE TABLE IF NOT EXISTS "augur_data"."issues" (
  "issue_id" int8 NOT NULL DEFAULT nextval('"augur_data".issue_seq'::regclass),
  "repo_id" int8,
  "reporter_id" int8,
  "pull_request" int8,
  "pull_request_id" int8,
  "created_at" timestamp(0),
  "issue_title" varchar(500) COLLATE "pg_catalog"."default",
  "issue_body" text COLLATE "pg_catalog"."default",
  "cntrb_id" int8,
  "comment_count" int8,
  "updated_at" timestamp(0),
  "closed_at" timestamp(0),
  "due_on" timestamp(0),
  "repository_url" varchar(4000) COLLATE "pg_catalog"."default",
  "issue_url" varchar(4000) COLLATE "pg_catalog"."default",
  "labels_url" varchar(4000) COLLATE "pg_catalog"."default",
  "comments_url" varchar(4000) COLLATE "pg_catalog"."default",
  "events_url" varchar(4000) COLLATE "pg_catalog"."default",
  "html_url" varchar(4000) COLLATE "pg_catalog"."default",
  "issue_state" varchar(255) COLLATE "pg_catalog"."default",
  "issue_node_id" varchar COLLATE "pg_catalog"."default",
  "gh_issue_id" int8,
  "gh_user_id" int8,
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  "gh_issue_number" int8,
  CONSTRAINT "issues_pkey" PRIMARY KEY ("issue_id")
);
ALTER TABLE IF EXISTS "augur_data"."issues" OWNER TO "augur";
CREATE INDEX "issue-cntrb-dix2" ON "augur_data"."issues" USING btree (
  "cntrb_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "issues_ibfk_1" ON "augur_data"."issues" USING btree (
  "repo_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "issues_ibfk_2" ON "augur_data"."issues" USING btree (
  "reporter_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "issues_ibfk_4" ON "augur_data"."issues" USING btree (
  "pull_request_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
COMMENT ON COLUMN "augur_data"."issues"."reporter_id" IS 'The ID of the person who opened the issue. ';
COMMENT ON COLUMN "augur_data"."issues"."cntrb_id" IS 'The ID of the person who closed the issue. ';

CREATE TABLE IF NOT EXISTS "augur_data"."libraries" (
  "library_id" int8 NOT NULL DEFAULT nextval('"augur_data".libraries_library_id_seq'::regclass),
  "repo_id" int8,
  "platform" varchar(255) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "name" varchar(255) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "created_timestamp" timestamp(0) DEFAULT NULL::timestamp without time zone,
  "updated_timestamp" timestamp(0) DEFAULT NULL::timestamp without time zone,
  "library_description" varchar(2000) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "keywords" varchar(255) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "library_homepage" varchar(1000) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "license" varchar(255) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "version_count" int4,
  "latest_release_timestamp" varchar(255) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "latest_release_number" varchar(255) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "package_manager_id" varchar(255) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "dependency_count" int4,
  "dependent_library_count" int4,
  "primary_language" varchar(255) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0),
  CONSTRAINT "libraries_pkey" PRIMARY KEY ("library_id")
);
ALTER TABLE IF EXISTS "augur_data"."libraries" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "augur_data"."library_dependencies" (
  "lib_dependency_id" int8 NOT NULL DEFAULT nextval('"augur_data".library_dependencies_lib_dependency_id_seq'::regclass),
  "library_id" int8,
  "manifest_platform" varchar(255) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "manifest_filepath" varchar(1000) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "manifest_kind" varchar(255) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "repo_id_branch" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0),
  CONSTRAINT "library_dependencies_pkey" PRIMARY KEY ("lib_dependency_id")
);
ALTER TABLE IF EXISTS "augur_data"."library_dependencies" OWNER TO "augur";
CREATE INDEX "REPO_DEP" ON "augur_data"."library_dependencies" USING btree (
  "library_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);

CREATE TABLE IF NOT EXISTS "augur_data"."library_version" (
  "library_version_id" int8 NOT NULL DEFAULT nextval('"augur_data".library_version_library_version_id_seq'::regclass),
  "library_id" int8,
  "library_platform" varchar(255) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "version_number" varchar(255) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "version_release_date" timestamp(0) DEFAULT NULL::timestamp without time zone,
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0),
  CONSTRAINT "library_version_pkey" PRIMARY KEY ("library_version_id")
);
ALTER TABLE IF EXISTS "augur_data"."library_version" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "augur_data"."lstm_anomaly_models" (
  "model_id" int8 NOT NULL DEFAULT nextval('"augur_data".lstm_anomaly_models_model_id_seq'::regclass),
  "model_name" varchar COLLATE "pg_catalog"."default",
  "model_description" varchar COLLATE "pg_catalog"."default",
  "look_back_days" int8,
  "training_days" int8,
  "batch_size" int8,
  "metric" varchar COLLATE "pg_catalog"."default",
  "tool_source" varchar COLLATE "pg_catalog"."default",
  "tool_version" varchar COLLATE "pg_catalog"."default",
  "data_source" varchar COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "lstm_anomaly_models_pkey" PRIMARY KEY ("model_id")
);
ALTER TABLE IF EXISTS "augur_data"."lstm_anomaly_models" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "augur_data"."lstm_anomaly_results" (
  "result_id" int8 NOT NULL DEFAULT nextval('"augur_data".lstm_anomaly_results_result_id_seq'::regclass),
  "repo_id" int8,
  "repo_category" varchar COLLATE "pg_catalog"."default",
  "model_id" int8,
  "metric" varchar COLLATE "pg_catalog"."default",
  "contamination_factor" float8,
  "mean_absolute_error" float8,
  "remarks" varchar COLLATE "pg_catalog"."default",
  "metric_field" varchar COLLATE "pg_catalog"."default",
  "mean_absolute_actual_value" float8,
  "mean_absolute_prediction_value" float8,
  "tool_source" varchar COLLATE "pg_catalog"."default",
  "tool_version" varchar COLLATE "pg_catalog"."default",
  "data_source" varchar COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "lstm_anomaly_results_pkey" PRIMARY KEY ("result_id")
);
ALTER TABLE IF EXISTS "augur_data"."lstm_anomaly_results" OWNER TO "augur";
COMMENT ON COLUMN "augur_data"."lstm_anomaly_results"."metric_field" IS 'This is a listing of all of the endpoint fields included in the generation of the metric. Sometimes there is one, sometimes there is more than one. This will list them all. ';

CREATE TABLE IF NOT EXISTS "augur_data"."message" (
  "msg_id" int8 NOT NULL DEFAULT nextval('"augur_data".message_msg_id_seq'::regclass),
  "rgls_id" int8,
  "msg_text" text COLLATE "pg_catalog"."default",
  "msg_timestamp" timestamp(0),
  "msg_sender_email" varchar(255) COLLATE "pg_catalog"."default",
  "msg_header" varchar(4000) COLLATE "pg_catalog"."default",
  "pltfrm_id" int8 NOT NULL,
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0),
  "cntrb_id" int8,
  CONSTRAINT "message_pkey" PRIMARY KEY ("msg_id"),
  CONSTRAINT "REPOGROUPLISTER" UNIQUE ("msg_id", "rgls_id"),
  CONSTRAINT "platformer" UNIQUE ("msg_id", "pltfrm_id")
);
ALTER TABLE IF EXISTS "augur_data"."message" OWNER TO "augur";
CREATE UNIQUE INDEX "messagegrouper" ON "augur_data"."message" USING btree (
  "msg_id" "pg_catalog"."int8_ops" ASC NULLS LAST,
  "rgls_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "msg-cntrb-id-idx" ON "augur_data"."message" USING btree (
  "cntrb_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "platformgrouper" ON "augur_data"."message" USING btree (
  "msg_id" "pg_catalog"."int8_ops" ASC NULLS LAST,
  "pltfrm_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
COMMENT ON COLUMN "augur_data"."message"."cntrb_id" IS 'Not populated for mailing lists. Populated for GitHub issues. ';

CREATE TABLE IF NOT EXISTS "augur_data"."message_analysis" (
  "msg_analysis_id" int8 NOT NULL DEFAULT nextval('"augur_data".message_analysis_msg_analysis_id_seq'::regclass),
  "msg_id" int8,
  "worker_run_id" int8,
  "sentiment_score" float8,
  "reconstruction_error" float8,
  "novelty_flag" bool,
  "feedback_flag" bool,
  "tool_source" varchar COLLATE "pg_catalog"."default",
  "tool_version" varchar COLLATE "pg_catalog"."default",
  "data_source" varchar COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "message_analysis_pkey" PRIMARY KEY ("msg_analysis_id")
);
ALTER TABLE IF EXISTS "augur_data"."message_analysis" OWNER TO "augur";
COMMENT ON COLUMN "augur_data"."message_analysis"."worker_run_id" IS 'This column is used to indicate analyses run by a worker during the same execution period, and is useful for grouping, and time series analysis.  ';
COMMENT ON COLUMN "augur_data"."message_analysis"."sentiment_score" IS 'A sentiment analysis score. Zero is neutral, negative numbers are negative sentiment, and positive numbers are positive sentiment. ';
COMMENT ON COLUMN "augur_data"."message_analysis"."reconstruction_error" IS 'Each message is converted to a 250 dimensin doc2vec vector, so the reconstruction error is the difference between what the predicted vector and the actual vector.';
COMMENT ON COLUMN "augur_data"."message_analysis"."novelty_flag" IS 'This is an analysis of the degree to which the message is novel when compared to other messages in a repository.  For example when bots are producing numerous identical messages, the novelty score is low. It would also be a low novelty score when several people are making the same coment. ';
COMMENT ON COLUMN "augur_data"."message_analysis"."feedback_flag" IS 'This exists to provide the user with an opportunity provide feedback on the resulting the sentiment scores. ';

CREATE TABLE IF NOT EXISTS "augur_data"."message_analysis_summary" (
  "msg_summary_id" int8 NOT NULL DEFAULT nextval('"augur_data".message_analysis_summary_msg_summary_id_seq'::regclass),
  "repo_id" int8,
  "worker_run_id" int8,
  "positive_ratio" float8,
  "negative_ratio" float8,
  "novel_count" int8,
  "period" timestamp(0),
  "tool_source" varchar COLLATE "pg_catalog"."default",
  "tool_version" varchar COLLATE "pg_catalog"."default",
  "data_source" varchar COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "message_analysis_summary_pkey" PRIMARY KEY ("msg_summary_id")
);
ALTER TABLE IF EXISTS "augur_data"."message_analysis_summary" OWNER TO "augur";
COMMENT ON COLUMN "augur_data"."message_analysis_summary"."worker_run_id" IS 'This value should reflect the worker_run_id for the messages summarized in the table. There is not a relation between these two tables for that purpose because its not *really*, relationaly a concept unless we create a third table for "worker_run_id", which we determined was unnecessarily complex. ';
COMMENT ON COLUMN "augur_data"."message_analysis_summary"."novel_count" IS 'The number of messages identified as novel during the analyzed period';
COMMENT ON COLUMN "augur_data"."message_analysis_summary"."period" IS 'The whole timeline is divided into periods based on the definition of time period for analysis, which is user specified. Timestamp of the first period to look at, until the end of messages at the data of execution. ';
COMMENT ON TABLE "augur_data"."message_analysis_summary" IS 'In a relationally perfect world, we would have a table called “message_analysis_run” the incremented the “worker_run_id” for both message_analysis and message_analysis_summary. For now, we decided this was overkill. ';

CREATE TABLE IF NOT EXISTS "augur_data"."message_sentiment" (
  "msg_analysis_id" int8 NOT NULL DEFAULT nextval('"augur_data".message_sentiment_msg_analysis_id_seq'::regclass),
  "msg_id" int8,
  "worker_run_id" int8,
  "sentiment_score" float8,
  "reconstruction_error" float8,
  "novelty_flag" bool,
  "feedback_flag" bool,
  "tool_source" varchar COLLATE "pg_catalog"."default",
  "tool_version" varchar COLLATE "pg_catalog"."default",
  "data_source" varchar COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "message_sentiment_pkey" PRIMARY KEY ("msg_analysis_id")
);
ALTER TABLE IF EXISTS "augur_data"."message_sentiment" OWNER TO "augur";
COMMENT ON COLUMN "augur_data"."message_sentiment"."worker_run_id" IS 'This column is used to indicate analyses run by a worker during the same execution period, and is useful for grouping, and time series analysis.  ';
COMMENT ON COLUMN "augur_data"."message_sentiment"."sentiment_score" IS 'A sentiment analysis score. Zero is neutral, negative numbers are negative sentiment, and positive numbers are positive sentiment. ';
COMMENT ON COLUMN "augur_data"."message_sentiment"."reconstruction_error" IS 'Each message is converted to a 250 dimensin doc2vec vector, so the reconstruction error is the difference between what the predicted vector and the actual vector.';
COMMENT ON COLUMN "augur_data"."message_sentiment"."novelty_flag" IS 'This is an analysis of the degree to which the message is novel when compared to other messages in a repository.  For example when bots are producing numerous identical messages, the novelty score is low. It would also be a low novelty score when several people are making the same coment. ';
COMMENT ON COLUMN "augur_data"."message_sentiment"."feedback_flag" IS 'This exists to provide the user with an opportunity provide feedback on the resulting the sentiment scores. ';

CREATE TABLE IF NOT EXISTS "augur_data"."message_sentiment_summary" (
  "msg_summary_id" int8 NOT NULL DEFAULT nextval('"augur_data".message_sentiment_summary_msg_summary_id_seq'::regclass),
  "repo_id" int8,
  "worker_run_id" int8,
  "positive_ratio" float8,
  "negative_ratio" float8,
  "novel_count" int8,
  "period" timestamp(0),
  "tool_source" varchar COLLATE "pg_catalog"."default",
  "tool_version" varchar COLLATE "pg_catalog"."default",
  "data_source" varchar COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "message_sentiment_summary_pkey" PRIMARY KEY ("msg_summary_id")
);
ALTER TABLE IF EXISTS "augur_data"."message_sentiment_summary" OWNER TO "augur";
COMMENT ON COLUMN "augur_data"."message_sentiment_summary"."worker_run_id" IS 'This value should reflect the worker_run_id for the messages summarized in the table. There is not a relation between these two tables for that purpose because its not *really*, relationaly a concept unless we create a third table for "worker_run_id", which we determined was unnecessarily complex. ';
COMMENT ON COLUMN "augur_data"."message_sentiment_summary"."novel_count" IS 'The number of messages identified as novel during the analyzed period';
COMMENT ON COLUMN "augur_data"."message_sentiment_summary"."period" IS 'The whole timeline is divided into periods based on the definition of time period for analysis, which is user specified. Timestamp of the first period to look at, until the end of messages at the data of execution. ';
COMMENT ON TABLE "augur_data"."message_sentiment_summary" IS 'In a relationally perfect world, we would have a table called “message_sentiment_run” the incremented the “worker_run_id” for both message_sentiment and message_sentiment_summary. For now, we decided this was overkill. ';

CREATE TABLE IF NOT EXISTS "augur_data"."platform" (
  "pltfrm_id" int8 NOT NULL DEFAULT nextval('"augur_data".platform_pltfrm_id_seq'::regclass),
  "pltfrm_name" varchar(255) COLLATE "pg_catalog"."default",
  "pltfrm_version" varchar(255) COLLATE "pg_catalog"."default",
  "pltfrm_release_date" date,
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0),
  CONSTRAINT "theplat" PRIMARY KEY ("pltfrm_id")
);
ALTER TABLE IF EXISTS "augur_data"."platform" OWNER TO "augur";
CREATE UNIQUE INDEX "plat" ON "augur_data"."platform" USING btree (
  "pltfrm_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);

CREATE TABLE IF NOT EXISTS "augur_data"."pull_request_assignees" (
  "pr_assignee_map_id" int8 NOT NULL DEFAULT nextval('"augur_data".pull_request_assignees_pr_assignee_map_id_seq'::regclass),
  "pull_request_id" int8,
  "contrib_id" int8,
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "pull_request_assignees_pkey" PRIMARY KEY ("pr_assignee_map_id")
);
ALTER TABLE IF EXISTS "augur_data"."pull_request_assignees" OWNER TO "augur";
CREATE INDEX "pr_meta_cntrb-idx" ON "augur_data"."pull_request_assignees" USING btree (
  "contrib_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);

CREATE TABLE IF NOT EXISTS "augur_data"."pull_request_commits" (
  "pr_cmt_id" int8 NOT NULL DEFAULT nextval('"augur_data".pull_request_commits_pr_cmt_id_seq'::regclass),
  "pull_request_id" int8,
  "pr_cmt_sha" varchar COLLATE "pg_catalog"."default",
  "pr_cmt_node_id" varchar COLLATE "pg_catalog"."default",
  "pr_cmt_message" varchar COLLATE "pg_catalog"."default",
  "pr_cmt_comments_url" varbit,
  "tool_source" varchar COLLATE "pg_catalog"."default",
  "tool_version" varchar COLLATE "pg_catalog"."default",
  "data_source" varchar COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "pull_request_commits_pkey" PRIMARY KEY ("pr_cmt_id")
);
ALTER TABLE IF EXISTS "augur_data"."pull_request_commits" OWNER TO "augur";
COMMENT ON COLUMN "augur_data"."pull_request_commits"."pr_cmt_sha" IS 'This is the commit SHA for a pull request commit. If the PR is not to the master branch of the main repository (or, in rare cases, from it), then you will NOT find a corresponding commit SHA in the commit table. (see table comment for further explanation). ';
COMMENT ON TABLE "augur_data"."pull_request_commits" IS 'Pull request commits are an enumeration of each commit associated with a pull request. 
Not all pull requests are from a branch or fork into master. 
The commits table intends to count only commits that end up in the master branch (i.e., part of the deployed code base for a project).
Therefore, there will be commit “SHA”’s in this table that are no associated with a commit SHA in the commits table. 
In cases where the PR is to the master branch of a project, you will find a match. In cases where the PR does not involve the master branch, you will not find a corresponding commit SHA in the commits table. This is expected. ';

CREATE TABLE IF NOT EXISTS "augur_data"."pull_request_events" (
  "pr_event_id" int8 NOT NULL DEFAULT nextval('"augur_data".pull_request_events_pr_event_id_seq'::regclass),
  "pull_request_id" int8 NOT NULL,
  "cntrb_id" int8 NOT NULL,
  "action" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "action_commit_hash" varchar COLLATE "pg_catalog"."default",
  "created_at" timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "issue_event_src_id" int8,
  "node_id" varchar COLLATE "pg_catalog"."default",
  "node_url" varchar COLLATE "pg_catalog"."default",
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "pr_events_pkey" PRIMARY KEY ("pr_event_id")
);
ALTER TABLE IF EXISTS "augur_data"."pull_request_events" OWNER TO "augur";
CREATE INDEX "pr_events_ibfk_1" ON "augur_data"."pull_request_events" USING btree (
  "pull_request_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "pr_events_ibfk_2" ON "augur_data"."pull_request_events" USING btree (
  "cntrb_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
COMMENT ON COLUMN "augur_data"."pull_request_events"."issue_event_src_id" IS 'This ID comes from the source. In the case of GitHub, it is the id that is the first field returned from the issue events API';
COMMENT ON COLUMN "augur_data"."pull_request_events"."node_id" IS 'This should be renamed to issue_event_src_node_id, as its the varchar identifier in GitHub and likely common in other sources as well. However, since it was created before we came to this naming standard and workers are built around it, we have it simply named as node_id. Anywhere you see node_id in the schema, it comes from GitHubs terminology.';

CREATE TABLE IF NOT EXISTS "augur_data"."pull_request_files" (
  "pull_request_id" int8,
  "pr_file_id" int8 NOT NULL DEFAULT nextval('"augur_data".pull_request_files_pr_file_id_seq'::regclass),
  "pr_file_additions" int8,
  "pr_file_deletions" int8,
  "pr_file_path" varchar COLLATE "pg_catalog"."default",
  "tool_source" varchar COLLATE "pg_catalog"."default",
  "tool_version" varchar COLLATE "pg_catalog"."default",
  "data_source" varchar COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "pull_request_files_pkey" PRIMARY KEY ("pr_file_id")
);
ALTER TABLE IF EXISTS "augur_data"."pull_request_files" OWNER TO "augur";
COMMENT ON TABLE "augur_data"."pull_request_files" IS 'Pull request commits are an enumeration of each commit associated with a pull request. 
Not all pull requests are from a branch or fork into master. 
The commits table intends to count only commits that end up in the master branch (i.e., part of the deployed code base for a project).
Therefore, there will be commit “SHA”’s in this table that are no associated with a commit SHA in the commits table. 
In cases where the PR is to the master branch of a project, you will find a match. In cases where the PR does not involve the master branch, you will not find a corresponding commit SHA in the commits table. This is expected. ';

CREATE TABLE IF NOT EXISTS "augur_data"."pull_request_labels" (
  "pr_label_id" int8 NOT NULL DEFAULT nextval('"augur_data".pull_request_labels_pr_label_id_seq'::regclass),
  "pull_request_id" int8,
  "pr_src_id" int8,
  "pr_src_node_id" varchar COLLATE "pg_catalog"."default",
  "pr_src_url" varchar COLLATE "pg_catalog"."default",
  "pr_src_description" varchar COLLATE "pg_catalog"."default",
  "pr_src_color" varchar COLLATE "pg_catalog"."default",
  "pr_src_default_bool" bool,
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "pull_request_labels_pkey" PRIMARY KEY ("pr_label_id")
);
ALTER TABLE IF EXISTS "augur_data"."pull_request_labels" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "augur_data"."pull_request_message_ref" (
  "pr_msg_ref_id" int8 NOT NULL DEFAULT nextval('"augur_data".pull_request_message_ref_pr_msg_ref_id_seq'::regclass),
  "pull_request_id" int8,
  "msg_id" int8,
  "pr_message_ref_src_comment_id" int8,
  "pr_message_ref_src_node_id" varchar COLLATE "pg_catalog"."default",
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "pull_request_message_ref_pkey" PRIMARY KEY ("pr_msg_ref_id")
);
ALTER TABLE IF EXISTS "augur_data"."pull_request_message_ref" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "augur_data"."pull_request_meta" (
  "pr_repo_meta_id" int8 NOT NULL DEFAULT nextval('"augur_data".pull_request_meta_pr_repo_meta_id_seq'::regclass),
  "pull_request_id" int8,
  "pr_head_or_base" varchar COLLATE "pg_catalog"."default",
  "pr_src_meta_label" varchar COLLATE "pg_catalog"."default",
  "pr_src_meta_ref" varchar COLLATE "pg_catalog"."default",
  "pr_sha" varchar COLLATE "pg_catalog"."default",
  "cntrb_id" int8,
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "pull_request_meta_pkey" PRIMARY KEY ("pr_repo_meta_id")
);
ALTER TABLE IF EXISTS "augur_data"."pull_request_meta" OWNER TO "augur";
CREATE INDEX "pr_meta-cntrbid-idx" ON "augur_data"."pull_request_meta" USING btree (
  "cntrb_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
COMMENT ON COLUMN "augur_data"."pull_request_meta"."pr_head_or_base" IS 'Each pull request should have one and only one head record; and one and only one base record. ';
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
COMMENT ON TABLE "augur_data"."pull_request_meta" IS 'Pull requests contain referencing metadata.  There are a few columns that are discrete. There are also head and base designations for the repo on each side of the pull request. Similar functions exist in GitLab, though the language here is based on GitHub. The JSON Being adapted to as of the development of this schema is here:      "base": {       "label": "chaoss:dev",       "ref": "dev",       "sha": "dc6c6f3947f7dc84ecba3d8bda641ef786e7027d",       "user": {         "login": "chaoss",         "id": 29740296,         "node_id": "MDEyOk9yZ2FuaXphdGlvbjI5NzQwMjk2",         "avatar_url": "https://avatars2.githubusercontent.com/u/29740296?v=4",         "gravatar_id": "",         "url": "https://api.github.com/users/chaoss",         "html_url": "https://github.com/chaoss",         "followers_url": "https://api.github.com/users/chaoss/followers",         "following_url": "https://api.github.com/users/chaoss/following{/other_user}",         "gists_url": "https://api.github.com/users/chaoss/gists{/gist_id}",         "starred_url": "https://api.github.com/users/chaoss/starred{/owner}{/repo}",         "subscriptions_url": "https://api.github.com/users/chaoss/subscriptions",         "organizations_url": "https://api.github.com/users/chaoss/orgs",         "repos_url": "https://api.github.com/users/chaoss/repos",         "events_url": "https://api.github.com/users/chaoss/events{/privacy}",         "received_events_url": "https://api.github.com/users/chaoss/received_events",         "type": "Organization",         "site_admin": false       },       "repo": {         "id": 78134122,         "node_id": "MDEwOlJlcG9zaXRvcnk3ODEzNDEyMg==",         "name": "augur",         "full_name": "chaoss/augur",         "private": false,         "owner": {           "login": "chaoss",           "id": 29740296,           "node_id": "MDEyOk9yZ2FuaXphdGlvbjI5NzQwMjk2",           "avatar_url": "https://avatars2.githubusercontent.com/u/29740296?v=4",           "gravatar_id": "",           "url": "https://api.github.com/users/chaoss",           "html_url": "https://github.com/chaoss",           "followers_url": "https://api.github.com/users/chaoss/followers",           "following_url": "https://api.github.com/users/chaoss/following{/other_user}",           "gists_url": "https://api.github.com/users/chaoss/gists{/gist_id}",           "starred_url": "https://api.github.com/users/chaoss/starred{/owner}{/repo}",           "subscriptions_url": "https://api.github.com/users/chaoss/subscriptions",           "organizations_url": "https://api.github.com/users/chaoss/orgs",           "repos_url": "https://api.github.com/users/chaoss/repos",           "events_url": "https://api.github.com/users/chaoss/events{/privacy}",           "received_events_url": "https://api.github.com/users/chaoss/received_events",           "type": "Organization",           "site_admin": false         }, ';

CREATE TABLE IF NOT EXISTS "augur_data"."pull_request_repo" (
  "pr_repo_id" int8 NOT NULL DEFAULT nextval('"augur_data".pull_request_repo_pr_repo_id_seq'::regclass),
  "pr_repo_meta_id" int8,
  "pr_repo_head_or_base" varchar COLLATE "pg_catalog"."default",
  "pr_src_repo_id" int8,
  "pr_src_node_id" varchar COLLATE "pg_catalog"."default",
  "pr_repo_name" varchar COLLATE "pg_catalog"."default",
  "pr_repo_full_name" varchar COLLATE "pg_catalog"."default",
  "pr_repo_private_bool" bool,
  "pr_cntrb_id" int8,
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "pull_request_repo_pkey" PRIMARY KEY ("pr_repo_id")
);
ALTER TABLE IF EXISTS "augur_data"."pull_request_repo" OWNER TO "augur";
CREATE INDEX "pr-cntrb-idx-repo" ON "augur_data"."pull_request_repo" USING btree (
  "pr_cntrb_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
COMMENT ON COLUMN "augur_data"."pull_request_repo"."pr_repo_head_or_base" IS 'For ease of validation checking, we should determine if the repository referenced is the head or base of the pull request. Each pull request should have one and only one of these, which is not enforcable easily in the database.';
COMMENT ON TABLE "augur_data"."pull_request_repo" IS 'This table is for storing information about forks that exist as part of a pull request. Generally we do not want to track these like ordinary repositories. ';

CREATE TABLE IF NOT EXISTS "augur_data"."pull_request_reviewers" (
  "pr_reviewer_map_id" int8 NOT NULL DEFAULT nextval('"augur_data".pull_request_reviewers_pr_reviewer_map_id_seq'::regclass),
  "pull_request_id" int8,
  "cntrb_id" int8,
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "pull_request_reviewers_pkey" PRIMARY KEY ("pr_reviewer_map_id")
);
ALTER TABLE IF EXISTS "augur_data"."pull_request_reviewers" OWNER TO "augur";
CREATE INDEX "pr-reviewers-cntrb-idx1" ON "augur_data"."pull_request_reviewers" USING btree (
  "cntrb_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);

CREATE TABLE IF NOT EXISTS "augur_data"."pull_request_teams" (
  "pr_team_id" int8 NOT NULL DEFAULT nextval('"augur_data".pull_request_teams_pr_team_id_seq'::regclass),
  "pull_request_id" int8,
  "pr_src_team_id" int8,
  "pr_src_team_node" varchar COLLATE "pg_catalog"."default",
  "pr_src_team_url" varchar COLLATE "pg_catalog"."default",
  "pr_team_name" varchar COLLATE "pg_catalog"."default",
  "pr_team_slug" varchar COLLATE "pg_catalog"."default",
  "pr_team_description" varchar COLLATE "pg_catalog"."default",
  "pr_team_privacy" varchar COLLATE "pg_catalog"."default",
  "pr_team_permission" varchar COLLATE "pg_catalog"."default",
  "pr_team_src_members_url" varchar COLLATE "pg_catalog"."default",
  "pr_team_src_repositories_url" varchar COLLATE "pg_catalog"."default",
  "pr_team_parent_id" int8,
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "pull_request_teams_pkey" PRIMARY KEY ("pr_team_id")
);
ALTER TABLE IF EXISTS "augur_data"."pull_request_teams" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "augur_data"."pull_requests" (
  "pull_request_id" int8 NOT NULL DEFAULT nextval('"augur_data".pull_requests_pull_request_id_seq'::regclass),
  "pr_url" varchar COLLATE "pg_catalog"."default",
  "pr_src_id" int8,
  "pr_src_node_id" varchar COLLATE "pg_catalog"."default",
  "pr_html_url" varchar COLLATE "pg_catalog"."default",
  "pr_diff_url" varchar COLLATE "pg_catalog"."default",
  "pr_patch_url" varchar COLLATE "pg_catalog"."default",
  "pr_issue_url" varchar COLLATE "pg_catalog"."default",
  "pr_augur_issue_id" int8,
  "pr_src_number" int8,
  "pr_src_state" varchar COLLATE "pg_catalog"."default",
  "pr_src_locked" bool,
  "pr_src_title" varchar COLLATE "pg_catalog"."default",
  "pr_augur_contributor_id" int8,
  "pr_body" text COLLATE "pg_catalog"."default",
  "pr_created_at" timestamp(0),
  "pr_updated_at" timestamp(0),
  "pr_closed_at" timestamp(0),
  "pr_merged_at" timestamp(0),
  "pr_merge_commit_sha" varchar COLLATE "pg_catalog"."default",
  "pr_teams" int8,
  "pr_milestone" varchar COLLATE "pg_catalog"."default",
  "pr_commits_url" varchar COLLATE "pg_catalog"."default",
  "pr_review_comments_url" varchar COLLATE "pg_catalog"."default",
  "pr_review_comment_url" varchar COLLATE "pg_catalog"."default",
  "pr_comments_url" varchar COLLATE "pg_catalog"."default",
  "pr_statuses_url" varchar COLLATE "pg_catalog"."default",
  "pr_meta_head_id" int8,
  "pr_meta_base_id" int8,
  "pr_src_issue_url" varchar COLLATE "pg_catalog"."default",
  "pr_src_comments_url" varchar COLLATE "pg_catalog"."default",
  "pr_src_review_comments_url" varchar COLLATE "pg_catalog"."default",
  "pr_src_commits_url" varchar COLLATE "pg_catalog"."default",
  "pr_src_statuses_url" varchar COLLATE "pg_catalog"."default",
  "pr_src_author_association" varchar COLLATE "pg_catalog"."default",
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  "repo_id" int8,
  CONSTRAINT "pull_requests_pkey" PRIMARY KEY ("pull_request_id")
);
ALTER TABLE IF EXISTS "augur_data"."pull_requests" OWNER TO "augur";
CREATE INDEX "id_node" ON "augur_data"."pull_requests" USING btree (
  "pr_src_id" "pg_catalog"."int8_ops" DESC NULLS FIRST,
  "pr_src_node_id" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" DESC NULLS LAST
);
COMMENT ON COLUMN "augur_data"."pull_requests"."pr_src_id" IS 'The pr_src_id is unique across all of github.';
COMMENT ON COLUMN "augur_data"."pull_requests"."pr_augur_issue_id" IS 'This is to link to the augur stored related issue';
COMMENT ON COLUMN "augur_data"."pull_requests"."pr_src_number" IS 'The pr_src_number is unique within a repository.';
COMMENT ON COLUMN "augur_data"."pull_requests"."pr_augur_contributor_id" IS 'This is to link to the augur contributor record. ';
COMMENT ON COLUMN "augur_data"."pull_requests"."pr_teams" IS 'One to many with pull request teams. ';
COMMENT ON COLUMN "augur_data"."pull_requests"."pr_review_comment_url" IS 'This is a field with limited utility. It does expose how to access a specific comment if needed with parameters. If the source changes URL structure, it may be useful';
COMMENT ON COLUMN "augur_data"."pull_requests"."pr_meta_head_id" IS 'The metadata for the head repo that links to the pull_request_meta table. ';
COMMENT ON COLUMN "augur_data"."pull_requests"."pr_meta_base_id" IS 'The metadata for the base repo that links to the pull_request_meta table. ';

CREATE TABLE IF NOT EXISTS "augur_data"."releases" (
  "release_id" char(64) COLLATE "pg_catalog"."default" NOT NULL DEFAULT nextval('"augur_data".releases_release_id_seq'::regclass),
  "repo_id" int8 NOT NULL,
  "release_name" varchar(255) COLLATE "pg_catalog"."default",
  "release_description" varchar COLLATE "pg_catalog"."default",
  "release_author" varchar(255) COLLATE "pg_catalog"."default",
  "release_created_at" timestamp(6),
  "release_published_at" timestamp(6),
  "release_updated_at" timestamp(6),
  "release_is_draft" bool,
  "release_is_prerelease" bool,
  "release_tag_name" varchar(255) COLLATE "pg_catalog"."default",
  "release_url" varchar(255) COLLATE "pg_catalog"."default",
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "tag_only" bool,
  CONSTRAINT "releases_pkey" PRIMARY KEY ("release_id")
);
ALTER TABLE IF EXISTS "augur_data"."releases" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "augur_data"."repo" (
  "repo_id" int8 NOT NULL DEFAULT nextval('"augur_data".repo_repo_id_seq'::regclass),
  "repo_group_id" int8 NOT NULL,
  "repo_git" varchar COLLATE "pg_catalog"."default" NOT NULL,
  "repo_path" varchar(256) COLLATE "pg_catalog"."default" DEFAULT 'NULL'::character varying,
  "repo_name" varchar COLLATE "pg_catalog"."default" DEFAULT 'NULL'::character varying,
  "repo_added" timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "repo_status" varchar(32) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'New'::character varying,
  "repo_type" varchar COLLATE "pg_catalog"."default" DEFAULT ''::character varying,
  "url" varchar(255) COLLATE "pg_catalog"."default",
  "owner_id" int4,
  "description" varchar COLLATE "pg_catalog"."default",
  "primary_language" varchar(255) COLLATE "pg_catalog"."default",
  "created_at" varchar(255) COLLATE "pg_catalog"."default",
  "forked_from" varchar COLLATE "pg_catalog"."default",
  "updated_at" timestamp(0),
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0),
  "repo_archived" int4,
  "repo_archived_date_collected" timestamptz(0),
  CONSTRAINT "repounique" PRIMARY KEY ("repo_id")
);
ALTER TABLE IF EXISTS "augur_data"."repo" OWNER TO "augur";
CREATE INDEX "forked" ON "augur_data"."repo" USING btree (
  "forked_from" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "repogitindexrep" ON "augur_data"."repo" USING btree (
  "repo_git" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "reponameindex" ON "augur_data"."repo" USING hash (
  "repo_name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops"
);
CREATE INDEX "reponameindexbtree" ON "augur_data"."repo" USING btree (
  "repo_name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "rggrouponrepoindex" ON "augur_data"."repo" USING btree (
  "repo_group_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE UNIQUE INDEX "therepo" ON "augur_data"."repo" USING btree (
  "repo_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
COMMENT ON COLUMN "augur_data"."repo"."repo_type" IS 'This field is intended to indicate if the repository is the "main instance" of a repository in cases where implementations choose to add the same repository to more than one repository group. In cases where the repository group is of rg_type Github Organization then this repo_type should be "primary". In other cases the repo_type should probably be "user created". We made this a varchar in order to hold open the possibility that there are additional repo_types we have not thought about. ';
COMMENT ON TABLE "augur_data"."repo" IS 'This table is a combination of the columns in Facade’s repo table and GHTorrent’s projects table. ';

CREATE TABLE IF NOT EXISTS "augur_data"."repo_badging" (
  "badge_collection_id" int8 NOT NULL DEFAULT nextval('"augur_data".repo_badging_badge_collection_id_seq'::regclass),
  "repo_id" int8,
  "created_at" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  "data" jsonb,
  CONSTRAINT "repo_badging_pkey" PRIMARY KEY ("badge_collection_id")
);
ALTER TABLE IF EXISTS "augur_data"."repo_badging" OWNER TO "augur";
COMMENT ON TABLE "augur_data"."repo_badging" IS 'This will be collected from the LF’s Badging API
https://bestpractices.coreinfrastructure.org/projects.json?pq=https%3A%2F%2Fgithub.com%2Fchaoss%2Faugur
';

CREATE TABLE IF NOT EXISTS "augur_data"."repo_cluster_messages" (
  "msg_cluster_id" int8 NOT NULL DEFAULT nextval('"augur_data".repo_cluster_messages_msg_cluster_id_seq'::regclass),
  "repo_id" int8,
  "cluster_content" int4,
  "cluster_mechanism" int4,
  "tool_source" varchar COLLATE "pg_catalog"."default",
  "tool_version" varchar COLLATE "pg_catalog"."default",
  "data_source" varchar COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "repo_cluster_messages_pkey" PRIMARY KEY ("msg_cluster_id")
);
ALTER TABLE IF EXISTS "augur_data"."repo_cluster_messages" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "augur_data"."repo_group_insights" (
  "rgi_id" int8 NOT NULL DEFAULT nextval('"augur_data".repo_group_insights_rgi_id_seq'::regclass),
  "repo_group_id" int8,
  "rgi_metric" varchar COLLATE "pg_catalog"."default",
  "rgi_value" varchar COLLATE "pg_catalog"."default",
  "cms_id" int8,
  "rgi_fresh" bool,
  "tool_source" varchar COLLATE "pg_catalog"."default",
  "tool_version" varchar COLLATE "pg_catalog"."default",
  "data_source" varchar COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "repo_group_insights_pkey" PRIMARY KEY ("rgi_id")
);
ALTER TABLE IF EXISTS "augur_data"."repo_group_insights" OWNER TO "augur";
COMMENT ON COLUMN "augur_data"."repo_group_insights"."rgi_fresh" IS 'false if the date is before the statistic that triggered the insight, true if after. This allows us to automatically display only "fresh insights" and avoid displaying "stale insights". The insight worker will populate this table. ';
COMMENT ON TABLE "augur_data"."repo_group_insights" IS 'This table is output from an analytical worker inside of Augur. It runs through the different metrics on a REPOSITORY_GROUP and identifies the five to ten most “interesting” metrics as defined by some kind of delta or other factor. The algorithm is going to evolve. 

Worker Design Notes: The idea is that the "insight worker" will scan through a bunch of active metrics or "synthetic metrics" to list the most important insights. ';

CREATE TABLE IF NOT EXISTS "augur_data"."repo_groups" (
  "repo_group_id" int8 NOT NULL DEFAULT nextval('"augur_data".repo_groups_repo_group_id_seq'::regclass),
  "rg_name" varchar COLLATE "pg_catalog"."default" NOT NULL,
  "rg_description" varchar COLLATE "pg_catalog"."default" DEFAULT 'NULL'::character varying,
  "rg_website" varchar(128) COLLATE "pg_catalog"."default" DEFAULT 'NULL'::character varying,
  "rg_recache" int2 DEFAULT 1,
  "rg_last_modified" timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "rg_type" varchar COLLATE "pg_catalog"."default",
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0),
  CONSTRAINT "rgid" PRIMARY KEY ("repo_group_id")
);
ALTER TABLE IF EXISTS "augur_data"."repo_groups" OWNER TO "augur";
CREATE UNIQUE INDEX "rgidm" ON "augur_data"."repo_groups" USING btree (
  "repo_group_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "rgnameindex" ON "augur_data"."repo_groups" USING btree (
  "rg_name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
COMMENT ON TABLE "augur_data"."repo_groups" IS 'rg_type is intended to be either a GitHub Organization or a User Created Repo Group. ';

CREATE TABLE IF NOT EXISTS "augur_data"."repo_groups_list_serve" (
  "rgls_id" int8 NOT NULL DEFAULT nextval('"augur_data".repo_groups_list_serve_rgls_id_seq'::regclass),
  "repo_group_id" int8 NOT NULL,
  "rgls_name" varchar(255) COLLATE "pg_catalog"."default",
  "rgls_description" varchar(3000) COLLATE "pg_catalog"."default",
  "rgls_sponsor" varchar(255) COLLATE "pg_catalog"."default",
  "rgls_email" varchar(255) COLLATE "pg_catalog"."default",
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0),
  CONSTRAINT "repo_groups_list_serve_pkey" PRIMARY KEY ("rgls_id"),
  CONSTRAINT "rglistserve" UNIQUE ("rgls_id", "repo_group_id")
);
ALTER TABLE IF EXISTS "augur_data"."repo_groups_list_serve" OWNER TO "augur";
CREATE UNIQUE INDEX "lister" ON "augur_data"."repo_groups_list_serve" USING btree (
  "rgls_id" "pg_catalog"."int8_ops" ASC NULLS LAST,
  "repo_group_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);

CREATE TABLE IF NOT EXISTS "augur_data"."repo_info" (
  "repo_info_id" int8 NOT NULL DEFAULT nextval('"augur_data".repo_info_repo_info_id_seq'::regclass),
  "repo_id" int8 NOT NULL,
  "last_updated" timestamp(0) DEFAULT NULL::timestamp without time zone,
  "issues_enabled" varchar(255) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "open_issues" int4,
  "pull_requests_enabled" varchar(255) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "wiki_enabled" varchar(255) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "pages_enabled" varchar(255) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "fork_count" int4,
  "default_branch" varchar(255) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "watchers_count" int4,
  "UUID" int4,
  "license" varchar(255) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "stars_count" int4,
  "committers_count" int4,
  "issue_contributors_count" varchar(255) COLLATE "pg_catalog"."default",
  "changelog_file" varchar(255) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "contributing_file" varchar(255) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "license_file" varchar(255) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "code_of_conduct_file" varchar(255) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "security_issue_file" varchar(255) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "security_audit_file" varchar(255) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "status" varchar(255) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "keywords" varchar(255) COLLATE "pg_catalog"."default" DEFAULT NULL::character varying,
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  "commit_count" int8,
  "issues_count" int8,
  "issues_closed" int8,
  "pull_request_count" int8,
  "pull_requests_open" int8,
  "pull_requests_closed" int8,
  "pull_requests_merged" int8,
  CONSTRAINT "repo_info_pkey" PRIMARY KEY ("repo_info_id")
);
ALTER TABLE IF EXISTS "augur_data"."repo_info" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "augur_data"."repo_insights" (
  "ri_id" int8 NOT NULL DEFAULT nextval('"augur_data".repo_insights_ri_id_seq'::regclass),
  "repo_id" int8,
  "ri_metric" varchar COLLATE "pg_catalog"."default",
  "ri_value" varchar(255) COLLATE "pg_catalog"."default",
  "ri_date" timestamp(0),
  "ri_fresh" bool,
  "tool_source" varchar COLLATE "pg_catalog"."default",
  "tool_version" varchar COLLATE "pg_catalog"."default",
  "data_source" varchar COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  "ri_score" numeric,
  "ri_field" varchar(255) COLLATE "pg_catalog"."default",
  "ri_detection_method" varchar(255) COLLATE "pg_catalog"."default",
  CONSTRAINT "repo_insights_pkey" PRIMARY KEY ("ri_id")
);
ALTER TABLE IF EXISTS "augur_data"."repo_insights" OWNER TO "augur";
COMMENT ON COLUMN "augur_data"."repo_insights"."ri_fresh" IS 'false if the date is before the statistic that triggered the insight, true if after. This allows us to automatically display only "fresh insights" and avoid displaying "stale insights". The insight worker will populate this table. ';
COMMENT ON TABLE "augur_data"."repo_insights" IS 'This table is output from an analytical worker inside of Augur. It runs through the different metrics on a repository and identifies the five to ten most “interesting” metrics as defined by some kind of delta or other factor. The algorithm is going to evolve. 

Worker Design Notes: The idea is that the "insight worker" will scan through a bunch of active metrics or "synthetic metrics" to list the most important insights. ';

CREATE TABLE IF NOT EXISTS "augur_data"."repo_insights_records" (
  "ri_id" int8 NOT NULL DEFAULT nextval('"augur_data".repo_insights_records_ri_id_seq'::regclass),
  "repo_id" int8,
  "ri_metric" varchar COLLATE "pg_catalog"."default",
  "ri_field" varchar COLLATE "pg_catalog"."default",
  "ri_value" varchar COLLATE "pg_catalog"."default",
  "ri_date" timestamp(6),
  "ri_score" float8,
  "ri_detection_method" varchar COLLATE "pg_catalog"."default",
  "tool_source" varchar COLLATE "pg_catalog"."default",
  "tool_version" varchar COLLATE "pg_catalog"."default",
  "data_source" varchar COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "repo_insights_records_pkey" PRIMARY KEY ("ri_id")
);
ALTER TABLE IF EXISTS "augur_data"."repo_insights_records" OWNER TO "augur";
CREATE INDEX "dater" ON "augur_data"."repo_insights_records" USING btree (
  "ri_date" "pg_catalog"."timestamp_ops" ASC NULLS LAST
);
COMMENT ON COLUMN "augur_data"."repo_insights_records"."ri_id" IS 'Primary key. ';
COMMENT ON COLUMN "augur_data"."repo_insights_records"."repo_id" IS 'Refers to repo table primary key. Will have a foreign key';
COMMENT ON COLUMN "augur_data"."repo_insights_records"."ri_metric" IS 'The metric endpoint';
COMMENT ON COLUMN "augur_data"."repo_insights_records"."ri_field" IS 'The field in the metric endpoint';
COMMENT ON COLUMN "augur_data"."repo_insights_records"."ri_value" IS 'The value of the endpoint in ri_field';
COMMENT ON COLUMN "augur_data"."repo_insights_records"."ri_date" IS 'The date the insight is for; in other words, some anomaly occurred on this date. ';
COMMENT ON COLUMN "augur_data"."repo_insights_records"."ri_score" IS 'A Score, derived from the algorithm used. ';
COMMENT ON COLUMN "augur_data"."repo_insights_records"."ri_detection_method" IS 'A confidence interval or other expression of the type of threshold and the value of a threshold met in order for it to be "an insight". Example. "95% confidence interval". ';
COMMENT ON COLUMN "augur_data"."repo_insights_records"."tool_source" IS 'Standard Augur Metadata';
COMMENT ON COLUMN "augur_data"."repo_insights_records"."tool_version" IS 'Standard Augur Metadata';
COMMENT ON COLUMN "augur_data"."repo_insights_records"."data_source" IS 'Standard Augur Metadata';
COMMENT ON COLUMN "augur_data"."repo_insights_records"."data_collection_date" IS 'Standard Augur Metadata';

CREATE TABLE IF NOT EXISTS "augur_data"."repo_labor" (
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
  "data_collection_date" timestamp(0),
  CONSTRAINT "repo_labor_pkey" PRIMARY KEY ("repo_labor_id")
);
ALTER TABLE IF EXISTS "augur_data"."repo_labor" OWNER TO "augur";
COMMENT ON COLUMN "augur_data"."repo_labor"."repo_url" IS 'This is a convenience column to simplify analysis against external datasets';
COMMENT ON TABLE "augur_data"."repo_labor" IS 'repo_labor is a derivative of tables used to store scc code and complexity counting statistics that are inputs to labor analysis, which are components of CHAOSS value metric calculations. ';

CREATE TABLE IF NOT EXISTS "augur_data"."repo_meta" (
  "repo_id" int8 NOT NULL,
  "rmeta_id" int8 NOT NULL DEFAULT nextval('"augur_data".repo_meta_rmeta_id_seq'::regclass),
  "rmeta_name" varchar(255) COLLATE "pg_catalog"."default",
  "rmeta_value" varchar(255) COLLATE "pg_catalog"."default" DEFAULT 0,
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0),
  CONSTRAINT "repo_meta_pkey" PRIMARY KEY ("rmeta_id", "repo_id")
);
ALTER TABLE IF EXISTS "augur_data"."repo_meta" OWNER TO "augur";
COMMENT ON TABLE "augur_data"."repo_meta" IS 'Project Languages';

CREATE TABLE IF NOT EXISTS "augur_data"."repo_sbom_scans" (
  "rsb_id" int8 NOT NULL DEFAULT nextval('"augur_data".repo_sbom_scans_rsb_id_seq'::regclass),
  "repo_id" int4,
  "sbom_scan" json,
  CONSTRAINT "repo_sbom_scans_pkey" PRIMARY KEY ("rsb_id")
);
ALTER TABLE IF EXISTS "augur_data"."repo_sbom_scans" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "augur_data"."repo_stats" (
  "repo_id" int8 NOT NULL,
  "rstat_id" int8 NOT NULL DEFAULT nextval('"augur_data".repo_stats_rstat_id_seq'::regclass),
  "rstat_name" varchar(400) COLLATE "pg_catalog"."default",
  "rstat_value" int8,
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0),
  CONSTRAINT "repo_stats_pkey" PRIMARY KEY ("rstat_id", "repo_id")
);
ALTER TABLE IF EXISTS "augur_data"."repo_stats" OWNER TO "augur";
COMMENT ON TABLE "augur_data"."repo_stats" IS 'Project Watchers';

CREATE TABLE IF NOT EXISTS "augur_data"."repo_test_coverage" (
  "repo_id" int8 NOT NULL DEFAULT nextval('"augur_data".repo_test_coverage_repo_id_seq'::regclass),
  "repo_clone_date" timestamp(0),
  "rtc_analysis_date" timestamp(0),
  "programming_language" varchar COLLATE "pg_catalog"."default",
  "file_path" varchar COLLATE "pg_catalog"."default",
  "file_name" varchar COLLATE "pg_catalog"."default",
  "testing_tool" varchar COLLATE "pg_catalog"."default",
  "file_statement_count" int8,
  "file_subroutine_count" int8,
  "file_statements_tested" int8,
  "file_subroutines_tested" int8,
  "tool_source" varchar COLLATE "pg_catalog"."default",
  "tool_version" varchar COLLATE "pg_catalog"."default",
  "data_source" varchar COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "repo_test_coverage_pkey" PRIMARY KEY ("repo_id")
);
ALTER TABLE IF EXISTS "augur_data"."repo_test_coverage" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "augur_data"."repo_topic" (
  "repo_topic_id" int8 NOT NULL DEFAULT nextval('"augur_data".repo_topic_repo_topic_id_seq'::regclass),
  "repo_id" int4,
  "topic_id" int4,
  "topic_prob" float8,
  "tool_source" varchar COLLATE "pg_catalog"."default",
  "tool_version" varchar COLLATE "pg_catalog"."default",
  "data_source" varchar COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "repo_topic_pkey" PRIMARY KEY ("repo_topic_id")
);
ALTER TABLE IF EXISTS "augur_data"."repo_topic" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "augur_data"."repos_fetch_log" (
  "repos_id" int4 NOT NULL,
  "status" varchar(128) COLLATE "pg_catalog"."default" NOT NULL,
  "date" timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP
);
ALTER TABLE IF EXISTS "augur_data"."repos_fetch_log" OWNER TO "augur";
CREATE INDEX "repos_id,status" ON "augur_data"."repos_fetch_log" USING btree (
  "repos_id" "pg_catalog"."int4_ops" ASC NULLS LAST,
  "status" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "repos_id,statusops" ON "augur_data"."repos_fetch_log" USING btree (
  "repos_id" "pg_catalog"."int4_ops" ASC NULLS LAST,
  "status" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

CREATE TABLE IF NOT EXISTS "augur_data"."settings" (
  "id" int4 NOT NULL,
  "setting" varchar(32) COLLATE "pg_catalog"."default" NOT NULL,
  "value" varchar COLLATE "pg_catalog"."default" NOT NULL,
  "last_modified" timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "settings_pkey" PRIMARY KEY ("id")
);
ALTER TABLE IF EXISTS "augur_data"."settings" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "augur_data"."topic_words" (
  "topic_words_id" int8 NOT NULL DEFAULT nextval('"augur_data".topic_words_topic_words_id_seq'::regclass),
  "topic_id" int8,
  "word" varchar COLLATE "pg_catalog"."default",
  "word_prob" float8,
  "tool_source" varchar COLLATE "pg_catalog"."default",
  "tool_version" varchar COLLATE "pg_catalog"."default",
  "data_source" varchar COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "topic_words_pkey" PRIMARY KEY ("topic_words_id")
);
ALTER TABLE IF EXISTS "augur_data"."topic_words" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "augur_data"."unknown_cache" (
  "type" varchar(10) COLLATE "pg_catalog"."default" NOT NULL,
  "repo_group_id" int4 NOT NULL,
  "email" varchar(128) COLLATE "pg_catalog"."default" NOT NULL,
  "domain" varchar(128) COLLATE "pg_catalog"."default" DEFAULT 'NULL'::character varying,
  "added" int8 NOT NULL,
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP
);
ALTER TABLE IF EXISTS "augur_data"."unknown_cache" OWNER TO "augur";
CREATE INDEX "type,projects_id" ON "augur_data"."unknown_cache" USING btree (
  "type" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "repo_group_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);

CREATE TABLE IF NOT EXISTS "augur_data"."utility_log" (
  "id" int8 NOT NULL DEFAULT nextval('"augur_data".utility_log_id_seq1'::regclass),
  "level" varchar(8) COLLATE "pg_catalog"."default" NOT NULL,
  "status" varchar COLLATE "pg_catalog"."default" NOT NULL,
  "attempted" timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "utility_log_pkey" PRIMARY KEY ("id")
);
ALTER TABLE IF EXISTS "augur_data"."utility_log" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "augur_data"."working_commits" (
  "repos_id" int4 NOT NULL,
  "working_commit" varchar(40) COLLATE "pg_catalog"."default" DEFAULT 'NULL'::character varying
);
ALTER TABLE IF EXISTS "augur_data"."working_commits" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "augur_operations"."all" (
  "Name" varchar COLLATE "pg_catalog"."default",
  "Bytes" varchar COLLATE "pg_catalog"."default",
  "Lines" varchar COLLATE "pg_catalog"."default",
  "Code" varchar COLLATE "pg_catalog"."default",
  "Comment" varchar COLLATE "pg_catalog"."default",
  "Blank" varchar COLLATE "pg_catalog"."default",
  "Complexity" varchar COLLATE "pg_catalog"."default",
  "Count" varchar COLLATE "pg_catalog"."default",
  "WeightedComplexity" varchar COLLATE "pg_catalog"."default",
  "Files" varchar COLLATE "pg_catalog"."default"
);
ALTER TABLE IF EXISTS "augur_operations"."all" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "augur_operations"."augur_settings" (
  "id" int8 NOT NULL DEFAULT nextval('"augur_operations".augur_settings_id_seq'::regclass),
  "setting" varchar COLLATE "pg_catalog"."default",
  "value" varchar COLLATE "pg_catalog"."default",
  "last_modified" timestamp(0) DEFAULT CURRENT_DATE,
  CONSTRAINT "augur_settings_pkey" PRIMARY KEY ("id")
);
ALTER TABLE IF EXISTS "augur_operations"."augur_settings" OWNER TO "augur";
COMMENT ON TABLE "augur_operations"."augur_settings" IS 'Augur settings include the schema version, and the Augur API Key as of 10/25/2020. Future augur settings may be stored in this table, which has the basic structure of a name-value pair. ';

CREATE TABLE IF NOT EXISTS "augur_operations"."repos_fetch_log" (
  "repos_id" int4 NOT NULL,
  "status" varchar(128) COLLATE "pg_catalog"."default" NOT NULL,
  "date" timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP
);
ALTER TABLE IF EXISTS "augur_operations"."repos_fetch_log" OWNER TO "augur";
CREATE INDEX "repos_id,statusops" ON "augur_operations"."repos_fetch_log" USING btree (
  "repos_id" "pg_catalog"."int4_ops" ASC NULLS LAST,
  "status" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
COMMENT ON TABLE "augur_operations"."repos_fetch_log" IS 'For future use when we move all working tables to the augur_operations schema. ';

CREATE TABLE IF NOT EXISTS "augur_operations"."worker_history" (
  "history_id" int8 NOT NULL DEFAULT nextval('"augur_operations".gh_worker_history_history_id_seq'::regclass),
  "repo_id" int8,
  "worker" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "job_model" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "oauth_id" int4 NOT NULL,
  "timestamp" timestamp(0) NOT NULL,
  "status" varchar(7) COLLATE "pg_catalog"."default" NOT NULL,
  "total_results" int4,
  CONSTRAINT "history_pkey" PRIMARY KEY ("history_id")
);
ALTER TABLE IF EXISTS "augur_operations"."worker_history" OWNER TO "augur";
COMMENT ON TABLE "augur_operations"."worker_history" IS 'This table stores the complete history of job execution, including success and failure. It is useful for troubleshooting. ';

CREATE TABLE IF NOT EXISTS "augur_operations"."worker_job" (
  "job_model" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "state" int4 NOT NULL DEFAULT 0,
  "zombie_head" int4,
  "since_id_str" varchar(255) COLLATE "pg_catalog"."default" NOT NULL DEFAULT '0'::character varying,
  "description" varchar(255) COLLATE "pg_catalog"."default" DEFAULT 'None'::character varying,
  "last_count" int4,
  "last_run" timestamp(0) DEFAULT NULL::timestamp without time zone,
  "analysis_state" int4 DEFAULT 0,
  "oauth_id" int4 NOT NULL,
  CONSTRAINT "job_pkey" PRIMARY KEY ("job_model")
);
ALTER TABLE IF EXISTS "augur_operations"."worker_job" OWNER TO "augur";
COMMENT ON TABLE "augur_operations"."worker_job" IS 'This table stores the jobs workers collect data for. A job is found in the code, and in the augur.config.json under the construct of a “model”. ';

CREATE TABLE IF NOT EXISTS "augur_operations"."worker_oauth" (
  "oauth_id" int8 NOT NULL DEFAULT nextval('"augur_operations".worker_oauth_oauth_id_seq'::regclass),
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "consumer_key" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "consumer_secret" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "access_token" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "access_token_secret" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "repo_directory" varchar COLLATE "pg_catalog"."default",
  "platform" varchar COLLATE "pg_catalog"."default" DEFAULT 'github'::character varying,
  CONSTRAINT "worker_oauth_pkey" PRIMARY KEY ("oauth_id")
);
ALTER TABLE IF EXISTS "augur_operations"."worker_oauth" OWNER TO "augur";
COMMENT ON TABLE "augur_operations"."worker_oauth" IS 'This table stores credentials for retrieving data from platform API’s. Entries in this table must comply with the terms of service for each platform. ';

CREATE TABLE IF NOT EXISTS "augur_operations"."worker_settings_facade" (
  "id" int4 NOT NULL,
  "setting" varchar(32) COLLATE "pg_catalog"."default" NOT NULL,
  "value" varchar COLLATE "pg_catalog"."default" NOT NULL,
  "last_modified" timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "settings_pkey" PRIMARY KEY ("id")
);
ALTER TABLE IF EXISTS "augur_operations"."worker_settings_facade" OWNER TO "augur";
COMMENT ON TABLE "augur_operations"."worker_settings_facade" IS 'For future use when we move all working tables to the augur_operations schema. ';

CREATE TABLE IF NOT EXISTS "augur_operations"."working_commits" (
  "repos_id" int4 NOT NULL,
  "working_commit" varchar(40) COLLATE "pg_catalog"."default" DEFAULT 'NULL'::character varying
);
ALTER TABLE IF EXISTS "augur_operations"."working_commits" OWNER TO "augur";
COMMENT ON TABLE "augur_operations"."working_commits" IS 'For future use when we move all working tables to the augur_operations schema. ';

CREATE TABLE IF NOT EXISTS "spdx"."annotation_types" (
  "annotation_type_id" int4 NOT NULL DEFAULT nextval('"spdx".annotation_types_annotation_type_id_seq'::regclass),
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  CONSTRAINT "annotation_types_pkey" PRIMARY KEY ("annotation_type_id"),
  CONSTRAINT "uc_annotation_type_name" UNIQUE ("name")
);
ALTER TABLE IF EXISTS "spdx"."annotation_types" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "spdx"."annotations" (
  "annotation_id" int4 NOT NULL DEFAULT nextval('"spdx".annotations_annotation_id_seq'::regclass),
  "document_id" int4 NOT NULL,
  "annotation_type_id" int4 NOT NULL,
  "identifier_id" int4 NOT NULL,
  "creator_id" int4 NOT NULL,
  "created_ts" timestamptz(6),
  "comment" text COLLATE "pg_catalog"."default" NOT NULL,
  CONSTRAINT "annotations_pkey" PRIMARY KEY ("annotation_id")
);
ALTER TABLE IF EXISTS "spdx"."annotations" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "spdx"."augur_repo_map" (
  "map_id" int4 NOT NULL DEFAULT nextval('"spdx".augur_repo_map_map_id_seq'::regclass),
  "dosocs_pkg_id" int4,
  "dosocs_pkg_name" text COLLATE "pg_catalog"."default",
  "repo_id" int4,
  "repo_path" text COLLATE "pg_catalog"."default",
  CONSTRAINT "augur_repo_map_pkey" PRIMARY KEY ("map_id")
);
ALTER TABLE IF EXISTS "spdx"."augur_repo_map" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "spdx"."creator_types" (
  "creator_type_id" int4 NOT NULL DEFAULT nextval('"spdx".creator_types_creator_type_id_seq'::regclass),
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  CONSTRAINT "creator_types_pkey" PRIMARY KEY ("creator_type_id")
);
ALTER TABLE IF EXISTS "spdx"."creator_types" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "spdx"."creators" (
  "creator_id" int4 NOT NULL DEFAULT nextval('"spdx".creators_creator_id_seq'::regclass),
  "creator_type_id" int4 NOT NULL,
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "email" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  CONSTRAINT "creators_pkey" PRIMARY KEY ("creator_id")
);
ALTER TABLE IF EXISTS "spdx"."creators" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "spdx"."document_namespaces" (
  "document_namespace_id" int4 NOT NULL DEFAULT nextval('"spdx".document_namespaces_document_namespace_id_seq'::regclass),
  "uri" varchar(500) COLLATE "pg_catalog"."default" NOT NULL,
  CONSTRAINT "document_namespaces_pkey" PRIMARY KEY ("document_namespace_id"),
  CONSTRAINT "uc_document_namespace_uri" UNIQUE ("uri")
);
ALTER TABLE IF EXISTS "spdx"."document_namespaces" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "spdx"."documents" (
  "document_id" int4 NOT NULL DEFAULT nextval('"spdx".documents_document_id_seq'::regclass),
  "document_namespace_id" int4 NOT NULL,
  "data_license_id" int4 NOT NULL,
  "spdx_version" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "license_list_version" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "created_ts" timestamptz(6) NOT NULL,
  "creator_comment" text COLLATE "pg_catalog"."default" NOT NULL,
  "document_comment" text COLLATE "pg_catalog"."default" NOT NULL,
  "package_id" int4 NOT NULL,
  CONSTRAINT "documents_pkey" PRIMARY KEY ("document_id"),
  CONSTRAINT "uc_document_document_namespace_id" UNIQUE ("document_namespace_id")
);
ALTER TABLE IF EXISTS "spdx"."documents" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "spdx"."documents_creators" (
  "document_creator_id" int4 NOT NULL DEFAULT nextval('"spdx".documents_creators_document_creator_id_seq'::regclass),
  "document_id" int4 NOT NULL,
  "creator_id" int4 NOT NULL,
  CONSTRAINT "documents_creators_pkey" PRIMARY KEY ("document_creator_id")
);
ALTER TABLE IF EXISTS "spdx"."documents_creators" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "spdx"."external_refs" (
  "external_ref_id" int4 NOT NULL DEFAULT nextval('"spdx".external_refs_external_ref_id_seq'::regclass),
  "document_id" int4 NOT NULL,
  "document_namespace_id" int4 NOT NULL,
  "id_string" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "sha256" varchar(64) COLLATE "pg_catalog"."default" NOT NULL,
  CONSTRAINT "external_refs_pkey" PRIMARY KEY ("external_ref_id"),
  CONSTRAINT "uc_external_ref_document_id_string" UNIQUE ("document_id", "id_string")
);
ALTER TABLE IF EXISTS "spdx"."external_refs" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "spdx"."file_contributors" (
  "file_contributor_id" int4 NOT NULL DEFAULT nextval('"spdx".file_contributors_file_contributor_id_seq'::regclass),
  "file_id" int4 NOT NULL,
  "contributor" text COLLATE "pg_catalog"."default" NOT NULL,
  CONSTRAINT "file_contributors_pkey" PRIMARY KEY ("file_contributor_id")
);
ALTER TABLE IF EXISTS "spdx"."file_contributors" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "spdx"."file_types" (
  "file_type_id" int4,
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  CONSTRAINT "uc_file_type_name" PRIMARY KEY ("name")
);
ALTER TABLE IF EXISTS "spdx"."file_types" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "spdx"."files" (
  "file_id" int4 NOT NULL DEFAULT nextval('"spdx".files_file_id_seq'::regclass),
  "file_type_id" int4,
  "sha256" varchar(64) COLLATE "pg_catalog"."default" NOT NULL,
  "copyright_text" text COLLATE "pg_catalog"."default",
  "package_id" int4,
  "comment" text COLLATE "pg_catalog"."default" NOT NULL,
  "notice" text COLLATE "pg_catalog"."default" NOT NULL,
  CONSTRAINT "files_pkey" PRIMARY KEY ("file_id"),
  CONSTRAINT "uc_file_sha256" UNIQUE ("sha256")
);
ALTER TABLE IF EXISTS "spdx"."files" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "spdx"."files_licenses" (
  "file_license_id" int4 NOT NULL DEFAULT nextval('"spdx".files_licenses_file_license_id_seq'::regclass),
  "file_id" int4 NOT NULL,
  "license_id" int4 NOT NULL,
  "extracted_text" text COLLATE "pg_catalog"."default" NOT NULL,
  CONSTRAINT "files_licenses_pkey" PRIMARY KEY ("file_license_id"),
  CONSTRAINT "uc_file_license" UNIQUE ("file_id", "license_id")
);
ALTER TABLE IF EXISTS "spdx"."files_licenses" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "spdx"."files_scans" (
  "file_scan_id" int4 NOT NULL DEFAULT nextval('"spdx".files_scans_file_scan_id_seq'::regclass),
  "file_id" int4 NOT NULL,
  "scanner_id" int4 NOT NULL,
  CONSTRAINT "files_scans_pkey" PRIMARY KEY ("file_scan_id"),
  CONSTRAINT "uc_file_scanner_id" UNIQUE ("file_id", "scanner_id")
);
ALTER TABLE IF EXISTS "spdx"."files_scans" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "spdx"."identifiers" (
  "identifier_id" int4 NOT NULL DEFAULT nextval('"spdx".identifiers_identifier_id_seq'::regclass),
  "document_namespace_id" int4 NOT NULL,
  "id_string" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "document_id" int4,
  "package_id" int4,
  "package_file_id" int4,
  CONSTRAINT "identifiers_pkey" PRIMARY KEY ("identifier_id"),
  CONSTRAINT "uc_identifier_document_namespace_id" UNIQUE ("document_namespace_id", "id_string"),
  CONSTRAINT "uc_identifier_namespace_document_id" UNIQUE ("document_namespace_id", "document_id"),
  CONSTRAINT "uc_identifier_namespace_package_id" UNIQUE ("document_namespace_id", "package_id"),
  CONSTRAINT "uc_identifier_namespace_package_file_id" UNIQUE ("document_namespace_id", "package_file_id"),
  CONSTRAINT "ck_identifier_exactly_one" CHECK (((document_id IS NOT NULL)::integer + (package_id IS NOT NULL)::integer + (package_file_id IS NOT NULL)::integer) = 1)
);
ALTER TABLE IF EXISTS "spdx"."identifiers" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "spdx"."licenses" (
  "license_id" int4 NOT NULL DEFAULT nextval('"spdx".licenses_license_id_seq'::regclass),
  "name" varchar(255) COLLATE "pg_catalog"."default",
  "short_name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "cross_reference" text COLLATE "pg_catalog"."default" NOT NULL,
  "comment" text COLLATE "pg_catalog"."default" NOT NULL,
  "is_spdx_official" bool NOT NULL,
  CONSTRAINT "licenses_pkey" PRIMARY KEY ("license_id"),
  CONSTRAINT "uc_license_short_name" UNIQUE ("short_name")
);
ALTER TABLE IF EXISTS "spdx"."licenses" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "spdx"."packages" (
  "package_id" int4 NOT NULL DEFAULT nextval('"spdx".packages_package_id_seq'::regclass),
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "version" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "file_name" text COLLATE "pg_catalog"."default" NOT NULL,
  "supplier_id" int4,
  "originator_id" int4,
  "download_location" text COLLATE "pg_catalog"."default",
  "verification_code" varchar(64) COLLATE "pg_catalog"."default" NOT NULL,
  "ver_code_excluded_file_id" int4,
  "sha256" varchar(64) COLLATE "pg_catalog"."default",
  "home_page" text COLLATE "pg_catalog"."default",
  "source_info" text COLLATE "pg_catalog"."default" NOT NULL,
  "concluded_license_id" int4,
  "declared_license_id" int4,
  "license_comment" text COLLATE "pg_catalog"."default" NOT NULL,
  "copyright_text" text COLLATE "pg_catalog"."default",
  "summary" text COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default" NOT NULL,
  "comment" text COLLATE "pg_catalog"."default" NOT NULL,
  "dosocs2_dir_code" varchar(64) COLLATE "pg_catalog"."default",
  CONSTRAINT "packages_pkey" PRIMARY KEY ("package_id"),
  CONSTRAINT "uc_package_sha256" UNIQUE ("sha256"),
  CONSTRAINT "uc_dir_code_ver_code" UNIQUE ("verification_code", "dosocs2_dir_code"),
  CONSTRAINT "uc_sha256_ds2_dir_code_exactly_one" CHECK (((sha256 IS NOT NULL)::integer + (dosocs2_dir_code IS NOT NULL)::integer) = 1)
);
ALTER TABLE IF EXISTS "spdx"."packages" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "spdx"."packages_files" (
  "package_file_id" int4 NOT NULL DEFAULT nextval('"spdx".packages_files_package_file_id_seq'::regclass),
  "package_id" int4 NOT NULL,
  "file_id" int4 NOT NULL,
  "concluded_license_id" int4,
  "license_comment" text COLLATE "pg_catalog"."default" NOT NULL,
  "file_name" text COLLATE "pg_catalog"."default" NOT NULL,
  CONSTRAINT "packages_files_pkey" PRIMARY KEY ("package_file_id"),
  CONSTRAINT "uc_package_id_file_name" UNIQUE ("package_id", "file_name")
);
ALTER TABLE IF EXISTS "spdx"."packages_files" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "spdx"."packages_scans" (
  "package_scan_id" int4 NOT NULL DEFAULT nextval('"spdx".packages_scans_package_scan_id_seq'::regclass),
  "package_id" int4 NOT NULL,
  "scanner_id" int4 NOT NULL,
  CONSTRAINT "packages_scans_pkey" PRIMARY KEY ("package_scan_id"),
  CONSTRAINT "uc_package_scanner_id" UNIQUE ("package_id", "scanner_id")
);
ALTER TABLE IF EXISTS "spdx"."packages_scans" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "spdx"."projects" (
  "package_id" int4 NOT NULL DEFAULT nextval('"spdx".projects_package_id_seq'::regclass),
  "name" text COLLATE "pg_catalog"."default" NOT NULL,
  "homepage" text COLLATE "pg_catalog"."default" NOT NULL,
  "uri" text COLLATE "pg_catalog"."default" NOT NULL,
  CONSTRAINT "projects_pkey" PRIMARY KEY ("package_id")
);
ALTER TABLE IF EXISTS "spdx"."projects" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "spdx"."relationship_types" (
  "relationship_type_id" int4 NOT NULL DEFAULT nextval('"spdx".relationship_types_relationship_type_id_seq'::regclass),
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  CONSTRAINT "relationship_types_pkey" PRIMARY KEY ("relationship_type_id"),
  CONSTRAINT "uc_relationship_type_name" UNIQUE ("name")
);
ALTER TABLE IF EXISTS "spdx"."relationship_types" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "spdx"."relationships" (
  "relationship_id" int4 NOT NULL DEFAULT nextval('"spdx".relationships_relationship_id_seq'::regclass),
  "left_identifier_id" int4 NOT NULL,
  "right_identifier_id" int4 NOT NULL,
  "relationship_type_id" int4 NOT NULL,
  "relationship_comment" text COLLATE "pg_catalog"."default" NOT NULL,
  CONSTRAINT "relationships_pkey" PRIMARY KEY ("relationship_id"),
  CONSTRAINT "uc_left_right_relationship_type" UNIQUE ("left_identifier_id", "right_identifier_id", "relationship_type_id")
);
ALTER TABLE IF EXISTS "spdx"."relationships" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "spdx"."sbom_scans" (
  "repo_id" int4,
  "sbom_scan" json
);
ALTER TABLE IF EXISTS "spdx"."sbom_scans" OWNER TO "augur";

CREATE TABLE IF NOT EXISTS "spdx"."scanners" (
  "scanner_id" int4 NOT NULL DEFAULT nextval('"spdx".scanners_scanner_id_seq'::regclass),
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  CONSTRAINT "scanners_pkey" PRIMARY KEY ("scanner_id"),
  CONSTRAINT "uc_scanner_name" UNIQUE ("name")
);
ALTER TABLE IF EXISTS "spdx"."scanners" OWNER TO "augur";

ALTER TABLE IF EXISTS "augur_data"."commit_comment_ref" ADD CONSTRAINT "fk_commit_comment_ref_commits_1" FOREIGN KEY ("cmt_id") REFERENCES "augur_data"."commits" ("cmt_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."commit_comment_ref" ADD CONSTRAINT "fk_commit_comment_ref_message_1" FOREIGN KEY ("msg_id") REFERENCES "augur_data"."message" ("msg_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."commit_parents" ADD CONSTRAINT "fk_commit_parents_commits_1" FOREIGN KEY ("cmt_id") REFERENCES "augur_data"."commits" ("cmt_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."commit_parents" ADD CONSTRAINT "fk_commit_parents_commits_2" FOREIGN KEY ("parent_id") REFERENCES "augur_data"."commits" ("cmt_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."commits" ADD CONSTRAINT "fk_commits_contributors_1" FOREIGN KEY ("cmt_ght_author_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."commits" ADD CONSTRAINT "fk_commits_contributors_2" FOREIGN KEY ("cmt_ght_committer_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."commits" ADD CONSTRAINT "fk_commits_repo_1" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."contributors_aliases" ADD CONSTRAINT "fk_contributors_aliases_contributors_1" FOREIGN KEY ("cntrb_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."contributors_history" ADD CONSTRAINT "fk_contributors_history_contributors_1" FOREIGN KEY ("cntrb_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."discourse_insights" ADD CONSTRAINT "fk_discourse_insights_message_1" FOREIGN KEY ("msg_id") REFERENCES "augur_data"."message" ("msg_id");
ALTER TABLE IF EXISTS "augur_data"."issue_assignees" ADD CONSTRAINT "fk_issue_assignees_contributors_1" FOREIGN KEY ("cntrb_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."issue_assignees" ADD CONSTRAINT "fk_issue_assignees_issues_1" FOREIGN KEY ("issue_id") REFERENCES "augur_data"."issues" ("issue_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."issue_events" ADD CONSTRAINT "fk_issue_events_contributors_1" FOREIGN KEY ("cntrb_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."issue_events" ADD CONSTRAINT "fk_issue_events_issues_1" FOREIGN KEY ("issue_id") REFERENCES "augur_data"."issues" ("issue_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."issue_labels" ADD CONSTRAINT "fk_issue_labels_issues_1" FOREIGN KEY ("issue_id") REFERENCES "augur_data"."issues" ("issue_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."issue_message_ref" ADD CONSTRAINT "fk_issue_message_ref_issues_1" FOREIGN KEY ("issue_id") REFERENCES "augur_data"."issues" ("issue_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."issue_message_ref" ADD CONSTRAINT "fk_issue_message_ref_message_1" FOREIGN KEY ("msg_id") REFERENCES "augur_data"."message" ("msg_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."issues" ADD CONSTRAINT "fk_issues_contributors_1" FOREIGN KEY ("cntrb_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."issues" ADD CONSTRAINT "fk_issues_contributors_2" FOREIGN KEY ("reporter_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."issues" ADD CONSTRAINT "fk_issues_repo" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE IF EXISTS "augur_data"."libraries" ADD CONSTRAINT "fk_libraries_repo_1" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."library_dependencies" ADD CONSTRAINT "fk_library_dependencies_libraries_1" FOREIGN KEY ("library_id") REFERENCES "augur_data"."libraries" ("library_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."library_version" ADD CONSTRAINT "fk_library_version_libraries_1" FOREIGN KEY ("library_id") REFERENCES "augur_data"."libraries" ("library_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."lstm_anomaly_results" ADD CONSTRAINT "fk_lstm_anomaly_results_lstm_anomaly_models_1" FOREIGN KEY ("model_id") REFERENCES "augur_data"."lstm_anomaly_models" ("model_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."lstm_anomaly_results" ADD CONSTRAINT "fk_lstm_anomaly_results_repo_1" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."message" ADD CONSTRAINT "fk_message_contributors_1" FOREIGN KEY ("cntrb_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."message" ADD CONSTRAINT "fk_message_platform_1" FOREIGN KEY ("pltfrm_id") REFERENCES "augur_data"."platform" ("pltfrm_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."message" ADD CONSTRAINT "fk_message_repo_groups_list_serve_1" FOREIGN KEY ("rgls_id") REFERENCES "augur_data"."repo_groups_list_serve" ("rgls_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."message_analysis" ADD CONSTRAINT "fk_message_analysis_message_1" FOREIGN KEY ("msg_id") REFERENCES "augur_data"."message" ("msg_id");
ALTER TABLE IF EXISTS "augur_data"."message_analysis_summary" ADD CONSTRAINT "fk_message_analysis_summary_repo_1" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id");
ALTER TABLE IF EXISTS "augur_data"."message_sentiment" ADD CONSTRAINT "fk_message_sentiment_message_1" FOREIGN KEY ("msg_id") REFERENCES "augur_data"."message" ("msg_id");
ALTER TABLE IF EXISTS "augur_data"."message_sentiment_summary" ADD CONSTRAINT "fk_message_sentiment_summary_repo_1" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id");
ALTER TABLE IF EXISTS "augur_data"."pull_request_assignees" ADD CONSTRAINT "fk_pull_request_assignees_contributors_1" FOREIGN KEY ("contrib_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."pull_request_assignees" ADD CONSTRAINT "fk_pull_request_assignees_pull_requests_1" FOREIGN KEY ("pull_request_id") REFERENCES "augur_data"."pull_requests" ("pull_request_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."pull_request_commits" ADD CONSTRAINT "fk_pull_request_commits_pull_requests_1" FOREIGN KEY ("pull_request_id") REFERENCES "augur_data"."pull_requests" ("pull_request_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."pull_request_events" ADD CONSTRAINT "fk_pull_request_events_contributors_1" FOREIGN KEY ("cntrb_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."pull_request_events" ADD CONSTRAINT "fk_pull_request_events_pull_requests_1" FOREIGN KEY ("pull_request_id") REFERENCES "augur_data"."pull_requests" ("pull_request_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."pull_request_files" ADD CONSTRAINT "fk_pull_request_commits_pull_requests_1" FOREIGN KEY ("pull_request_id") REFERENCES "augur_data"."pull_requests" ("pull_request_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."pull_request_labels" ADD CONSTRAINT "fk_pull_request_labels_pull_requests_1" FOREIGN KEY ("pull_request_id") REFERENCES "augur_data"."pull_requests" ("pull_request_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."pull_request_message_ref" ADD CONSTRAINT "fk_pull_request_message_ref_message_1" FOREIGN KEY ("msg_id") REFERENCES "augur_data"."message" ("msg_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."pull_request_message_ref" ADD CONSTRAINT "fk_pull_request_message_ref_pull_requests_1" FOREIGN KEY ("pull_request_id") REFERENCES "augur_data"."pull_requests" ("pull_request_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."pull_request_meta" ADD CONSTRAINT "fk_pull_request_meta_contributors_2" FOREIGN KEY ("cntrb_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."pull_request_meta" ADD CONSTRAINT "fk_pull_request_meta_pull_requests_1" FOREIGN KEY ("pull_request_id") REFERENCES "augur_data"."pull_requests" ("pull_request_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."pull_request_repo" ADD CONSTRAINT "fk_pull_request_repo_contributors_1" FOREIGN KEY ("pr_cntrb_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."pull_request_repo" ADD CONSTRAINT "fk_pull_request_repo_pull_request_meta_1" FOREIGN KEY ("pr_repo_meta_id") REFERENCES "augur_data"."pull_request_meta" ("pr_repo_meta_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."pull_request_reviewers" ADD CONSTRAINT "fk_pull_request_reviewers_contributors_1" FOREIGN KEY ("cntrb_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."pull_request_reviewers" ADD CONSTRAINT "fk_pull_request_reviewers_pull_requests_1" FOREIGN KEY ("pull_request_id") REFERENCES "augur_data"."pull_requests" ("pull_request_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."pull_request_teams" ADD CONSTRAINT "fk_pull_request_teams_pull_requests_1" FOREIGN KEY ("pull_request_id") REFERENCES "augur_data"."pull_requests" ("pull_request_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."pull_requests" ADD CONSTRAINT "fk_pull_requests_pull_request_meta_1" FOREIGN KEY ("pr_meta_head_id") REFERENCES "augur_data"."pull_request_meta" ("pr_repo_meta_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."pull_requests" ADD CONSTRAINT "fk_pull_requests_pull_request_meta_2" FOREIGN KEY ("pr_meta_base_id") REFERENCES "augur_data"."pull_request_meta" ("pr_repo_meta_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."pull_requests" ADD CONSTRAINT "fk_pull_requests_repo_1" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."releases" ADD CONSTRAINT "fk_releases_repo_1" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."repo" ADD CONSTRAINT "fk_repo_repo_groups_1" FOREIGN KEY ("repo_group_id") REFERENCES "augur_data"."repo_groups" ("repo_group_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
COMMENT ON CONSTRAINT "fk_repo_repo_groups_1" ON "augur_data"."repo" IS 'Repo_groups cardinality set to one and only one because, although in theory there could be more than one repo group for a repo, this might create dependecies in hosted situation that we do not want to live with. ';
ALTER TABLE IF EXISTS "augur_data"."repo_badging" ADD CONSTRAINT "fk_repo_badging_repo_1" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."repo_cluster_messages" ADD CONSTRAINT "fk_repo_cluster_messages_repo_1" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id");
ALTER TABLE IF EXISTS "augur_data"."repo_group_insights" ADD CONSTRAINT "fk_repo_group_insights_repo_groups_1" FOREIGN KEY ("repo_group_id") REFERENCES "augur_data"."repo_groups" ("repo_group_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."repo_groups_list_serve" ADD CONSTRAINT "fk_repo_groups_list_serve_repo_groups_1" FOREIGN KEY ("repo_group_id") REFERENCES "augur_data"."repo_groups" ("repo_group_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."repo_info" ADD CONSTRAINT "fk_repo_info_repo_1" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."repo_insights" ADD CONSTRAINT "fk_repo_insights_repo_1" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."repo_insights_records" ADD CONSTRAINT "repo_id_ref" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE IF EXISTS "augur_data"."repo_labor" ADD CONSTRAINT "fk_repo_labor_repo_1" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."repo_meta" ADD CONSTRAINT "fk_repo_meta_repo_1" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."repo_sbom_scans" ADD CONSTRAINT "repo_linker_sbom" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE IF EXISTS "augur_data"."repo_stats" ADD CONSTRAINT "fk_repo_stats_repo_1" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."repo_test_coverage" ADD CONSTRAINT "fk_repo_test_coverage_repo_1" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "augur_data"."repo_topic" ADD CONSTRAINT "fk_repo_topic_repo_1" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id");
ALTER TABLE IF EXISTS "augur_data"."topic_words" ADD CONSTRAINT "fk_topic_words_repo_topic_1" FOREIGN KEY ("topic_id") REFERENCES "augur_data"."repo_topic" ("repo_topic_id");
ALTER TABLE IF EXISTS "spdx"."annotations" ADD CONSTRAINT "annotations_annotation_type_id_fkey" FOREIGN KEY ("annotation_type_id") REFERENCES "spdx"."annotation_types" ("annotation_type_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "spdx"."annotations" ADD CONSTRAINT "annotations_creator_id_fkey" FOREIGN KEY ("creator_id") REFERENCES "spdx"."creators" ("creator_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "spdx"."annotations" ADD CONSTRAINT "annotations_document_id_fkey" FOREIGN KEY ("document_id") REFERENCES "spdx"."documents" ("document_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "spdx"."annotations" ADD CONSTRAINT "annotations_identifier_id_fkey" FOREIGN KEY ("identifier_id") REFERENCES "spdx"."identifiers" ("identifier_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "spdx"."creators" ADD CONSTRAINT "creators_creator_type_id_fkey" FOREIGN KEY ("creator_type_id") REFERENCES "spdx"."creator_types" ("creator_type_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "spdx"."documents" ADD CONSTRAINT "documents_data_license_id_fkey" FOREIGN KEY ("data_license_id") REFERENCES "spdx"."licenses" ("license_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "spdx"."documents" ADD CONSTRAINT "documents_document_namespace_id_fkey" FOREIGN KEY ("document_namespace_id") REFERENCES "spdx"."document_namespaces" ("document_namespace_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "spdx"."documents" ADD CONSTRAINT "documents_package_id_fkey" FOREIGN KEY ("package_id") REFERENCES "spdx"."packages" ("package_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "spdx"."documents_creators" ADD CONSTRAINT "documents_creators_creator_id_fkey" FOREIGN KEY ("creator_id") REFERENCES "spdx"."creators" ("creator_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "spdx"."documents_creators" ADD CONSTRAINT "documents_creators_document_id_fkey" FOREIGN KEY ("document_id") REFERENCES "spdx"."documents" ("document_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "spdx"."external_refs" ADD CONSTRAINT "external_refs_document_id_fkey" FOREIGN KEY ("document_id") REFERENCES "spdx"."documents" ("document_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "spdx"."external_refs" ADD CONSTRAINT "external_refs_document_namespace_id_fkey" FOREIGN KEY ("document_namespace_id") REFERENCES "spdx"."document_namespaces" ("document_namespace_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "spdx"."file_contributors" ADD CONSTRAINT "file_contributors_file_id_fkey" FOREIGN KEY ("file_id") REFERENCES "spdx"."files" ("file_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "spdx"."files_licenses" ADD CONSTRAINT "files_licenses_file_id_fkey" FOREIGN KEY ("file_id") REFERENCES "spdx"."files" ("file_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "spdx"."files_licenses" ADD CONSTRAINT "files_licenses_license_id_fkey" FOREIGN KEY ("license_id") REFERENCES "spdx"."licenses" ("license_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "spdx"."files_scans" ADD CONSTRAINT "files_scans_file_id_fkey" FOREIGN KEY ("file_id") REFERENCES "spdx"."files" ("file_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "spdx"."files_scans" ADD CONSTRAINT "files_scans_scanner_id_fkey" FOREIGN KEY ("scanner_id") REFERENCES "spdx"."scanners" ("scanner_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "spdx"."identifiers" ADD CONSTRAINT "identifiers_document_id_fkey" FOREIGN KEY ("document_id") REFERENCES "spdx"."documents" ("document_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "spdx"."identifiers" ADD CONSTRAINT "identifiers_document_namespace_id_fkey" FOREIGN KEY ("document_namespace_id") REFERENCES "spdx"."document_namespaces" ("document_namespace_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "spdx"."identifiers" ADD CONSTRAINT "identifiers_package_file_id_fkey" FOREIGN KEY ("package_file_id") REFERENCES "spdx"."packages_files" ("package_file_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "spdx"."identifiers" ADD CONSTRAINT "identifiers_package_id_fkey" FOREIGN KEY ("package_id") REFERENCES "spdx"."packages" ("package_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "spdx"."packages" ADD CONSTRAINT "fk_package_packages_files" FOREIGN KEY ("ver_code_excluded_file_id") REFERENCES "spdx"."packages_files" ("package_file_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "spdx"."packages" ADD CONSTRAINT "packages_concluded_license_id_fkey" FOREIGN KEY ("concluded_license_id") REFERENCES "spdx"."licenses" ("license_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "spdx"."packages" ADD CONSTRAINT "packages_declared_license_id_fkey" FOREIGN KEY ("declared_license_id") REFERENCES "spdx"."licenses" ("license_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "spdx"."packages" ADD CONSTRAINT "packages_originator_id_fkey" FOREIGN KEY ("originator_id") REFERENCES "spdx"."creators" ("creator_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "spdx"."packages" ADD CONSTRAINT "packages_supplier_id_fkey" FOREIGN KEY ("supplier_id") REFERENCES "spdx"."creators" ("creator_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "spdx"."packages_files" ADD CONSTRAINT "fk_package_files_packages" FOREIGN KEY ("package_id") REFERENCES "spdx"."packages" ("package_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "spdx"."packages_files" ADD CONSTRAINT "packages_files_concluded_license_id_fkey" FOREIGN KEY ("concluded_license_id") REFERENCES "spdx"."licenses" ("license_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "spdx"."packages_files" ADD CONSTRAINT "packages_files_file_id_fkey" FOREIGN KEY ("file_id") REFERENCES "spdx"."files" ("file_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "spdx"."packages_scans" ADD CONSTRAINT "packages_scans_package_id_fkey" FOREIGN KEY ("package_id") REFERENCES "spdx"."packages" ("package_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "spdx"."packages_scans" ADD CONSTRAINT "packages_scans_scanner_id_fkey" FOREIGN KEY ("scanner_id") REFERENCES "spdx"."scanners" ("scanner_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "spdx"."relationships" ADD CONSTRAINT "relationships_left_identifier_id_fkey" FOREIGN KEY ("left_identifier_id") REFERENCES "spdx"."identifiers" ("identifier_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "spdx"."relationships" ADD CONSTRAINT "relationships_relationship_type_id_fkey" FOREIGN KEY ("relationship_type_id") REFERENCES "spdx"."relationship_types" ("relationship_type_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE IF EXISTS "spdx"."relationships" ADD CONSTRAINT "relationships_right_identifier_id_fkey" FOREIGN KEY ("right_identifier_id") REFERENCES "spdx"."identifiers" ("identifier_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

INSERT INTO "augur_operations"."augur_settings" set value = 31 where setting = 'augur_data_version'; 
